"""Testes de ligacoes_aco — fonte: Manual Gerdau "Ligações para Estruturas de Aço" (ed. NBR 8800:2024), tabelas 1 a 4
(págs. 10–11) e disposições construtivas (seção 2.4). Valores do manual em kN, tolerância 0,1 kN."""
import pytest
from nd_estruturas.ligacoes_aco import (DIAMETROS, ACOS, Ft_Rd, Fv_Rd, Fc_Rd, furo_padrao, LCPP,
                                        checar_disposicoes, interacao_tracao_corte, bloco_cisalhamento, emenda_tala)

T1 = {"5/8": 91.3, "3/4": 131.4, "7/8": 178.9, "1": 233.6}          # tração A325
T2 = {"5/8": 54.8, "3/4": 78.9, "7/8": 107.3, "1": 140.2}           # corte 1 plano, rosca no plano
T3 = {"A36": {"5/8": 105.3, "3/4": 128.5, "7/8": 151.7, "1": 174.9},  # contato entre furos s = 3d, t = 1 cm
      "A572-50": {"5/8": 118.5, "3/4": 144.6, "7/8": 170.7, "1": 196.8}}
T4 = {"A36": {"5/8": 52.6, "3/4": 64.3, "7/8": 75.9, "1": 87.5},      # contato furo-borda e = 1,5d, t = 1 cm
      "A572-50": {"5/8": 59.2, "3/4": 72.3, "7/8": 85.4, "1": 98.4}}


@pytest.mark.parametrize("dp", list(T1))
def test_tabela1_tracao(dp):
    assert Ft_Rd(DIAMETROS[dp]) == pytest.approx(T1[dp], abs=0.1)


@pytest.mark.parametrize("dp", list(T2))
def test_tabela2_corte(dp):
    assert Fv_Rd(DIAMETROS[dp]) == pytest.approx(T2[dp], abs=0.1)
    assert Fv_Rd(DIAMETROS[dp], planos=2) == pytest.approx(2 * T2[dp], abs=0.2)


@pytest.mark.parametrize("aco", ["A36", "A572-50"])
@pytest.mark.parametrize("dp", ["5/8", "3/4", "7/8", "1"])
def test_tabelas3e4_contato(aco, dp):
    d = DIAMETROS[dp]
    dh = furo_padrao(d)
    fu = ACOS[aco][1]
    assert Fc_Rd(d, 1.0, fu, lf=3 * d - dh) == pytest.approx(T3[aco][dp], abs=0.1)
    assert Fc_Rd(d, 1.0, fu, lf=1.5 * d - dh / 2) == pytest.approx(T4[aco][dp], abs=0.1)


def test_contato_teto_2_4_d_t_fu():
    d = DIAMETROS["3/4"]
    assert Fc_Rd(d, 1.0, 40.0, lf=100.0) == pytest.approx(2.4 * d * 40.0 / 1.35)


def test_disposicoes_preferenciais_manual():
    # manual 2.4: 3/4" com s = 75 mm e e = 40 mm em cantoneira de 6,4 mm → sem não conformidade (borda laminada)
    assert checar_disposicoes(DIAMETROS["3/4"], 7.5, 4.0, 0.635) == []
    assert checar_disposicoes(DIAMETROS["3/4"], 4.0, 2.0, 0.635)          # s < 2,7d e borda curta


def test_interacao():
    assert interacao_tracao_corte(60, 120, 30, 60) == pytest.approx(0.5)


def test_bloco_cisalhamento_limite_escoamento():
    # ramo de escoamento governa quando 0,6·fu·Anv > 0,6·fy·Agv
    assert bloco_cisalhamento(10, 9.9, 1, 25, 40) == pytest.approx((0.6 * 25 * 10 + 40 * 1) / 1.35)


def test_lcpp_ordem_de_grandeza_tabela_manual():
    """LCPP 3 parafusos 3/4" por aba, L76×76×6,4 (gabarito 45 mm), alma W360×51 (tw 7,2 mm), sem recorte:
    manual (pág. 15 / tabelas LCPP) dá Vd,max 328 kN sem recorte para W360×51 — o modelo simplificado (sem flambagem
    do recorte; alma sem borda livre) reproduz 329,2 kN (desvio 0,4%)."""
    lig = LCPP(diam="3/4", n=3, s=7.5, e=4.0, b_aba=7.62, t_c=0.635, g=4.5, tw=0.72, H=35.5)
    assert lig.Vd_Rd() == pytest.approx(328, rel=0.02), lig.detalhes


def test_emenda_tala_simples():
    FRd, det, uso = emenda_tala(200.0, "7/8", 6, 1, 1.25, 20.0, 1.25)
    assert uso < 1.0 and FRd == min(det.values())


# ============================================================================================================
# Capítulos 3 (recortes), 4 (LCHE), 5 (LCHS), 6 (LMPA) e 8 (LT/LMTS) do Manual Gerdau "Ligações para Estruturas de Aço"
# (ed. NBR 8800:2024). Tolerância: 2% ou 0,5 da unidade tabelada (as tabelas trazem inteiros; ex.: 21 kN·m ± 0,5).
# ============================================================================================================
from nd_estruturas.ligacoes_aco import (
    LCHE,
    LCHS,
    LMPA,
    LT,
    Fbc_alma_recortada,
    lche_rotacao_ok,
    lmts_verificar,
    verificar_pilar_suporte,
)


def _ok(calc, tab, rel=0.02):
    assert abs(calc - tab) <= max(rel * abs(tab), 0.5), f"calculado {calc:.2f} x tabela {tab}"


# ------------------------------------------------------------------ LCHE (cap. 4)
def test_lche_exemplo_pag56_W250x28_4():
    """pág. 56: W 250 x 28,4, CH 6,3 A36, 4 Ø 3/4" A325N. O exemplo usa a 2ª linha da tabela (pág. 61):
    Vd = 93 kN com Nd = 22 kN (50% de Vd,max); Vd,max = 187 kN com Nd = 0. Vd = 79 e Nd = 9,3 kN atendem."""
    lig = LCHE("3/4", 4, 0.63, perfil="W 250 x 28,4")
    _ok(lig.Vd_Rd(), 187)
    Nd, Vdm = lig.Nd_Rd()
    _ok(Nd, 22)
    _ok(Vdm, 93)
    assert lig.verificar(79.0, 9.3)[0]
    assert not lig.verificar(100.0, 9.3)[0]
    assert min(lig.detalhes, key=lig.detalhes.get) == "cisalhamento da alma da viga"


@pytest.mark.parametrize("pag,diam,nps,t,perfil,Vd,Nd", [
    (59, "5/8", 4, 0.63, "W 150 x 13,0", 97, 18),     # LCHE 20-A, governa a alma da viga
    (59, "5/8", 4, 0.63, "W 150 x 24,0", 115, 18),    # governa a flexão da chapa
    (61, "3/4", 4, 0.63, "W 250 x 17,9", 140, 23),    # LCHE 20-B
    (64, "3/4", 6, 0.63, "W 310 x 21,0", 221, 33),    # LCHE 30-B
    (66, "3/4", 6, 0.63, "W 360 x 79,0", 314, 32),    # governa o metal-base da solda
    (68, "3/4", 8, 0.63, "W 410 x 38,8", 367, 42),    # LCHE 40-B
    (74, "7/8", 10, 0.80, "W 530 x 66,0", 622, 86),   # LCHE 50-C, solda 6 mm
    (83, "7/8", 12, 0.80, "W 610 x 217,0", 745, 110),  # LCHE 60-C
])
def test_lche_tabelas(pag, diam, nps, t, perfil, Vd, Nd):
    lig = LCHE(diam, nps, t, perfil=perfil)
    _ok(lig.Vd_Rd(), Vd)
    _ok(lig.Nd_Rd()[0], Nd)


def test_lche_rotacao_pag56():
    assert lche_rotacao_ok(0.01, 20.0)          # 0,01 rad × 20 cm = 2 mm
    assert not lche_rotacao_ok(0.012, 20.0)


def test_lche_entrada_invalida():
    with pytest.raises(ValueError):
        LCHE("3/4", 5, 0.63, tw=0.6)
    with pytest.raises(ValueError):
        LCHE("3/4", 4, 0.63)


# ------------------------------------------------------------------ LCHS (cap. 5)
def test_lchs_exemplo_pag86_W310():
    """pág. 86: W 310, Vd = 102 kN: 2 Ø 3/4" resiste 56 kN (não atende); 3 Ø 3/4" resiste 112 kN (atende)."""
    assert LCHS("3/4", 2, 0.63, perfil="W 310 x 21,0").Vd_Rd() == pytest.approx(56, abs=0.5)
    lig = LCHS("3/4", 3, 0.63, perfil="W 310 x 21,0")
    _ok(lig.Vd_Rd(), 112)
    assert lig.Vd_Rd() >= 102
    assert lig.disposicoes() == []


@pytest.mark.parametrize("pag,diam,np_,t,b,perfil,Vd,Nd", [
    (90, "5/8", 2, 0.63, 0.5, "W 150 x 13,0", 25, 6),
    (91, "3/4", 2, 0.63, 0.5, "W 250 x 17,9", 56, 14),
    (92, "3/4", 3, 0.63, 0.5, "W 460 x 52,0", 112, 28),
    (94, "3/4", 4, 0.80, 0.6, "W 410 x 38,8", 220, 55),
    (95, "7/8", 4, 0.95, 0.8, "W 610 x 82,0", 256, 64),
    (96, "3/4", 5, 0.80, 0.6, "W 530 x 66,0", 306, 76),
    (97, "7/8", 5, 0.95, 0.8, "W 460 x 52,0", 356, 89),
    (98, "7/8", 6, 1.25, 1.0, "W 530 x 66,0", 533, 133),
])
def test_lchs_tabelas(pag, diam, np_, t, b, perfil, Vd, Nd):
    lig = LCHS(diam, np_, t, b_solda=b, perfil=perfil)
    _ok(lig.Vd_Rd(), Vd)
    N, _, chk = lig.Nd_Rd()
    _ok(N, Nd)
    assert all(v >= N for v in chk.values())            # chapa e solda resistem ao par (Nd, 0,5 Vd,max)


def test_lchs_tabelas_que_nao_fecham_ficam_a_favor_da_seguranca():
    """pág. 93 (3 Ø 7/8", CH 8,0): manual 159 kN; o contato na chapa de 8 mm (mesma regra que fecha as págs. 90–92,
    94–98) dá 134 kN — 159 só sai com chapa de 9,5 mm ou com o contato na alma do W 310 x 21,0 (158,7).
    pág. 99 (6 Ø 1", CH 12,5): manual 625 kN (= ruptura da chapa por cisalhamento, 624); o contato na chapa dá 564.
    Nos dois casos o módulo fica abaixo da tabela (a favor da segurança)."""
    a = LCHS("7/8", 3, 0.80, b_solda=0.6, perfil="W 310 x 21,0").Vd_Rd()
    b = LCHS("1", 6, 1.25, b_solda=1.0, perfil="W 530 x 66,0")
    assert a == pytest.approx(134.4, abs=0.5) and a < 159
    assert b.Vd_Rd() < 625 and b.detalhes["cisalhamento da chapa"] == pytest.approx(624.4, abs=0.5)


def test_lchs_limitacoes_pag85():
    assert LCHS("3/4", 6, 0.63, perfil="W 530 x 66,0").disposicoes()      # 6 parafusos exige t ≥ 8 mm
    assert LCHS("5/8", 2, 1.25, perfil="W 150 x 13,0").disposicoes()      # t > d/2 + 2 mm


# ------------------------------------------------------------------ LMPA (cap. 6)
G1 = {"e1": 5.5, "e3": 11.0, "e4": 4.5, "e5": 4.5}      # 6 Ø 1", chapa 220 mm (pág. 120)
G5 = {"e1": 3.0, "e3": 7.0, "e4": 3.0, "e5": 3.0}       # 6 Ø 5/8", chapa 130 mm (pág. 105)
G34 = {"e1": 3.5, "e3": 7.0, "e4": 3.5, "e5": 3.5}       # 6 Ø 3/4", chapa 140 mm (pág. 109)


def test_lmpa_exemplo_pag101_W460x89():
    """págs. 101–102: W 460 x 89,0, tc = 31,5 mm, 6 Ø 1", soldas de penetração. Tabela (pág. 120): Md = 385 kN·m
    (Nd = 0) e 305 kN·m (Nd = 360 kN), Vd = 240 kN. Esforços do exemplo: Nd = 245, Vd = 102, Md = 290 → atende."""
    lig = LMPA("W 460 x 89,0", "1", 3.15, 2, **G1)
    _ok(lig.Md_Rd(0, 240), 385)
    _ok(lig.Md_Rd(360, 240), 305)
    assert lig.Md_Rd(245, 102) >= 290
    assert lig.disposicoes() == []


@pytest.mark.parametrize("pag,perfil,diam,tc,bsf,bsw,geo,Vd,linhas", [
    (105, "W 150 x 13,0", "5/8", 1.6, 0.5, 0.4, G5, 75, [(0, 21), (76, 16)]),
    (105, "W 150 x 18,0", "5/8", 1.9, 0.7, 0.6, G5, 114, [(0, 32), (109, 24)]),
    (105, "W 150 x 24,0", "5/8", 2.5, 0.0, 0.6, G5, 114, [(0, 49), (147, 38)]),
    (106, "W 200 x 19,3", "5/8", 1.6, 0.7, 0.6, G5, 155, [(0, 41), (109, 30)]),
    (109, "W 250 x 25,3", "3/4", 1.6, 0.8, 0.6, G34, 197, [(0, 55), (125, 39)]),
    (109, "W 250 x 28,4", "3/4", 2.5, 0.0, 0.6, G34, 196, [(0, 80), (182, 57)]),
    (120, "W 460 x 74,0", "1", 3.15, 0.0, 0.9, G1, 240, [(0, 382), (360, 303)]),
    (120, "W 460 x 106,0", "1", 3.15, 0.0, 0.0, G1, 240, [(0, 389), (360, 308)]),
])
def test_lmpa_tabelas_caso2(pag, perfil, diam, tc, bsf, bsw, geo, Vd, linhas):
    lig = LMPA(perfil, diam, tc, 2, bsf=bsf, bsw=bsw, **geo)
    for Nd, Md in linhas:
        _ok(lig.Md_Rd(Nd, Vd), Md, rel=0.025)   # W 150 x 13,0: 21,49 x 21 (arredondamento da tabela)


@pytest.mark.parametrize("perfil,linhas", [("W 610 x 155,0", [(0, 1024), (720, 811)]),
                                           ("W 610 x 195,0", [(0, 1034), (720, 819)])])
def test_lmpa_tabela_caso1_12_parafusos_1pol_pag126(perfil, linhas):
    lig = LMPA(perfil, "1", 3.75, 1, e1=4.5, e2=8.0, e3=10.0, e4=4.5, e5=4.5)
    for Nd, Md in linhas:
        _ok(lig.Md_Rd(Nd, 480), Md)


def test_lmpa_tabela_caso1_12_parafusos_3_4_pag125():
    """pág. 125 (12 Ø 3/4", tc 25): manual 544 kN·m; modelo puro dá 569 (+4,6%); com a redução de 5% (DEC-017) fica
    a favor da segurança e dentro de 2% da tabela."""
    lig = LMPA("W 610 x 101,0", "3/4", 2.5, 1, e1=3.5, e2=6.0, e3=7.5, e4=3.5, e5=3.5)
    Md = lig.Md_Rd(0, 277)
    assert Md <= 544 * 1.001 or Md == pytest.approx(544, rel=0.02)
    assert "aviso" in lig.detalhes


def test_lmpa_fator_corte_texto_e_limite_de_cortante():
    """com Fv,Rd sem o fator 0,75 (texto da pág. 103) o momento sobe; Vd acima de d'·tw·0,6fy/1,1 é recusado."""
    a = LMPA("W 460 x 89,0", "1", 3.15, 2, **G1).Md_Rd(0, 240)
    b = LMPA("W 460 x 89,0", "1", 3.15, 2, fator_corte=1.0, **G1).Md_Rd(0, 240)
    assert b > a
    with pytest.raises(ValueError):
        LMPA("W 150 x 13,0", "5/8", 1.6, 2, bsf=0.5, bsw=0.4, **G5).Md_Rd(0, 200)


# ------------------------------------------------------------------ LT / LMTS (cap. 8)
@pytest.mark.parametrize("pag,perfil,Lt,diam,X,Y,e,s,G,Td,Cd", [
    (141, "W 460 x 68,0", 17, "1", 8, 10, 5.1, 10, 8.5, 282, 485),     # exemplo (TC) — Cd = escoamento da alma
    (141, "W 460 x 68,0", 20, "1", 9, 11, 5.1, 10, 8.5, 325, 531),     # exemplo — Cd = contato na alma do T
    (141, "W 530 x 85,0", 17, "1", 8, 10, 5.7, 12.5, 9, 309, 549),     # exemplo
    (144, "W 150 x 22,5", 14, "3/4", 7.5, 8, 3, 5.9, 8, 44, 172),      # TM
    (144, "W 150 x 37,1", 23, "3/4", 10, 13, 3, 5.9, 8, 191, 240),
    (145, "W 200 x 26,6", 14, "3/4", 7.5, 8, 4, 7.5, 8, 72, 255),
    (145, "W 200 x 41,7", 23, "7/8", 10, 13, 4, 7.5, 8.5, 200, 311),
    (146, "W 200 x 59,0", 23, "1", 10, 13, 4, 7.5, 9, 284, 371),
    (159, "W 460 x 52,0", 17, "3/4", 8, 10, 5.1, 10, 8.5, 139, 314),
    (160, "W 530 x 72,0", 20, "3/4", 9, 11, 5.7, 12.5, 10, 149, 314),
    (161, "W 530 x 101,0", 23, "1", 10, 13, 5.5, 12.5, 11, 384, 561),
])
def test_lt_tabelas(pag, perfil, Lt, diam, X, Y, e, s, G, Td, Cd):
    t = LT(perfil, Lt, diam, G=G, X=X, Y=Y, e=e, s=s)
    T, C = t.resistencias()
    _ok(T, Td)
    _ok(C, Cd)
    assert t.detalhes["ductilidade (Td < demais)"]


def test_lt_braco_do_texto_fica_contra_a_seguranca():
    """pág. 142: com b' = b1 − 0,5d e 4,4 (texto) o Td do TM-W150x22,5 Lt 140 daria 60,5 kN, 37% acima da tabela
    (44 kN, pág. 144); as tabelas só fecham com o braço b1 — por isso o padrão do módulo é a forma das tabelas."""
    T = LT("W 150 x 22,5", 14, "3/4", G=8, X=7.5, Y=8, e=3, s=5.9, braco_texto=True).resistencias()[0]
    assert T == pytest.approx(60.4, abs=0.5)


def test_lmts_exemplo_pag141_W310x44_5():
    """pág. 141: W 310 x 44,5, Md = 30 kN·m, Nd = 20 kN, Vd = 100 kN → T = 105,85 kN, C = 85,85 kN; TC-W460x68 Lt 170
    (Td 282, Cd 485) atende; cantoneiras 2 L102x102x8 com 2 Ø 3/4" na alma → Vd,Rd = 201 kN (tabela LMTS pág. 164)."""
    Vrd = LCPP(diam="3/4", n=2, b_aba=10.16, t_c=0.8, g=6.5, perfil="W 310 x 44,5").Vd_Rd()
    _ok(Vrd, 201)
    ok, T, C = lmts_verificar(30, 20, 100, 31.3, 282, 485, Vrd)
    assert ok and T == pytest.approx(105.85, abs=0.01) and C == pytest.approx(85.85, abs=0.01)


@pytest.mark.parametrize("pag,perfil,Vd", [(164, "W 310 x 38,7", 176), (165, "W 360 x 44,6", 210)])
def test_lmts_cortante_cantoneiras(pag, perfil, Vd):
    _ok(LCPP(diam="3/4", n=2, b_aba=10.16, t_c=0.8, g=6.5, perfil=perfil).Vd_Rd(), Vd)


# ------------------------------------------------------------------ LCPP com recortes (cap. 3)
def test_lcpp_exemplo_E1_pag15_W360x51_um_recorte():
    """pág. 15: W 360 x 51,0 em W 530 x 92,0, Lh = 99 mm, Lv = 26 mm, Vd = 202 kN. Tabela (pág. 26), 1 recorte
    com Lv,max = 30 mm e Lh,max = 130 mm: Vd,max = 252 kN (governa o bloco de cisalhamento da alma)."""
    lig = LCPP(diam="3/4", n=3, perfil="W 360 x 51,0", recortes=1, Lv=3.0, Lh=13.0)
    _ok(lig.Vd_Rd(), 252)
    assert min(lig.detalhes, key=lig.detalhes.get) == "bloco de cisalhamento da alma"
    real = LCPP(diam="3/4", n=3, perfil="W 360 x 51,0", recortes=1, Lv=2.6, Lh=9.9)
    assert real.Vd_Rd() >= 202


@pytest.mark.parametrize("perfil,sem,um,dois", [
    ("W 360 x 32,9", 265, 203, 181),
    ("W 360 x 39,0", 296, 228, 208),
    ("W 360 x 64,0", 346, 270, 237),
    ("W 360 x 79,0", 346, 329, 303),
])
def test_lcpp_tabela_pag26_recortes(perfil, sem, um, dois):
    """pág. 26 (3 Ø 3/4" por aba, L76x76x6,4): sem recorte, 1 recorte (Lh 170) e 2 recortes (Lh 130), Lv = 30 mm.
    Com 2 recortes e Lh 130 governa o início de escoamento por flexão da seção recortada."""
    kw = {"diam": "3/4", "n": 3, "perfil": perfil}
    _ok(LCPP(**kw).Vd_Rd(), sem)
    _ok(LCPP(recortes=1, Lv=3.0, Lh=17.0, **kw).Vd_Rd(), um)
    d2 = LCPP(recortes=2, Lv=3.0, Lh=13.0, **kw)
    _ok(d2.Vd_Rd(), dois)
    assert min(d2.detalhes, key=d2.detalhes.get) == "flexão na seção recortada"


def test_flambagem_alma_recortada_limitada_a_fy():
    # alma espessa → Fbc acima de fy/1,1 é limitado; alma fina e recorte longo → governa a flambagem
    assert Fbc_alma_recortada(1.0, 30.0, 8.0, 35.0, 34.5) == pytest.approx(34.5 / 1.1)
    f = 16243 * (0.4 / 40) ** 2 * (2 * 17 / 45) * 2.2 * (40 / 17) ** 1.65
    assert Fbc_alma_recortada(0.4, 40.0, 17.0, 45.0, 34.5) == pytest.approx(f)


def test_lcpp_recorte_sem_dimensoes_e_invalido():
    with pytest.raises(ValueError):
        LCPP(perfil="W 360 x 51,0", recortes=1)


# ------------------------------------------------------------------ elemento suporte (pilar)
def test_pilar_suporte_conferido_a_mao():
    """W 310 x 97,0 (tf 15,4; tw 9,9; d 308; d' 277 mm): flexão local da mesa 6,25·1,54²·34,5/1,1 = 464,9 kN;
    painel de alma 0,6·34,5·30,8·0,99/1,1 = 573,8 kN (N ≤ 0,4 Ny). Fórmulas NBR 8800:2008 5.7 / AISC J10."""
    R, enrij, Ast = verificar_pilar_suporte("W 310 x 97,0", F_tracao=300, F_compressao=300, ln=2.0, V_painel=500)
    assert R["flexão local da mesa (tração)"] == pytest.approx(6.25 * 1.54 ** 2 * 34.5 / 1.1)
    assert R["painel de alma (cisalhamento)"] == pytest.approx(0.6 * 34.5 * 30.8 * 0.99 / 1.1)
    assert R["painel ok"] and not enrij and Ast == 0
    R, enrij, Ast = verificar_pilar_suporte("W 310 x 97,0", F_tracao=900, ln=2.0)
    assert enrij and Ast == pytest.approx((900 - min(R["flexão local da mesa (tração)"],
                                                     R["escoamento local da alma"])) * 1.1 / 34.5 / 2)
