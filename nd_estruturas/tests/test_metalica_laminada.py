"""Testes do módulo metalica_laminada (NBR 8800:2024, perfis W/HP Gerdau) — 13/10/2026.

Fontes (Drive, pasta "materiais gerdau"):
- [TVC] Gerdau, "Tabela de Vãos e Cargas" 6ª ed. (NBR 8800:2024): tabela de bitolas pp. 20–24
  (Lb = Lp, MRd FLT/FLM, VRd, Qs/Qa), TCPA pp. 25–78, TVPA-1 a 4 pp. 79–102.
- [MG] Gerdau, "Galpões em Pórticos com Perfis Estruturais W" (set/2025): Tabela 2 (htr = 150·r),
  esforços por família (p. 27), exemplos 1 e 3 (GMQ6/30/9/6, pp. 48–55).

Divergências conhecidas da [TVC] (não testadas, documentadas):
- TVPA gerada com σr = 70 MPa, tabela de bitolas com σr = 0,3·fy: nos perfis em que a FLM governa
  (ex. W 150×13, W 150×22,5) MRd/1,5 da TVPA é 0,4–0,9 % maior que o da bitola. Os testes TVPA
  passam sigma_r=70.
- Células da TVPA fora da fórmula (erro de digitação no PDF): TVPA-1 W200×71 L=2,5; W360×44,6
  L=2,0; W530×85 L=2,5; TVPA-2 W250×32,7 L=1,0; W310×28,3 L=1,0; W250×38,5 L=1,5; W360×39
  L=1,0/1,5; W250×167 L=1,5; TVPA-3 W410×46,1 L=1,5. Wx do W 610×113 = 2.091,2 na tabela (correto
  2.901,2) e Zy do W 530×92 = 345,7 (catálogo 354,7).
- TCPA, eixo X: em alguns perfis (W 310×179, HP 200×53) a tabela usa só a flexo-torção e ignora a
  flexão em x; no W 610×82 entre 8 e 11 m os valores caem abaixo da flexo-torção e voltam a subir
  em 11,5 m (resistência crescendo com o comprimento — erro da tabela). Não usados nos testes.
- TCPA não reduz as mesas esbeltas (HP 310×79, bf/2tf = 13,91 > 13,48): aqui a área efetiva das
  mesas é reduzida (até 0,9 % a menos, a favor da segurança).
- O [MG] não traz valores de resistência (é manual de pré-dimensionamento por tabelas); os testes
  do manual conferem que os perfis escolhidos por ele passam e que o imediatamente mais leve da
  mesma família não passa, com os esforços publicados.
"""
import math

import pytest

from nd_estruturas.metalica_laminada import (
    LIMITES_FLECHA,
    Perfil,
    area_efetiva,
    compressao_resistente,
    cortante_resistente,
    fator_cb,
    fator_chi,
    fator_q,
    flecha_biapoiada,
    interacao,
    listar_perfis,
    momento_resistente,
    momento_resistente_y,
    perfil,
    tracao_resistente,
    tvpa,
    tvpa_vao_limite_flecha,
    verificar_barra,
)


# ------------------------------------------------------------------ catálogo
def test_catalogo_completo_e_coerente():
    nomes = listar_perfis()
    assert len(nomes) == 110                       # 108 do [MG] 6.7 + W150×9,2 e W150×10,4 do catálogo
    assert len(listar_perfis("HP")) == 8
    for n in nomes:
        p = perfil(n)
        assert p.Wx == pytest.approx(2 * p.Ix / (p.d / 10), rel=0.01)
        assert p.Cw == pytest.approx(p.Iy * (p.d - p.tf) ** 2 / 4 / 100, rel=0.03)   # Cw = Iy(d−tf)²/4
        assert p.d_linha < p.h < p.d


def test_busca_por_nome_tolerante():
    a = perfil("W 310 x 32,7")
    assert perfil("W310x32.7") is a and perfil("w310X32,7") is a
    assert perfil("HP 250 x 62,0 (H)").familia == "HP"
    assert perfil("W 610 x 153").massa == pytest.approx(154.2)
    with pytest.raises(KeyError):
        perfil("W 310 x 33")
    with pytest.raises(ValueError):
        perfil("UDC 150")


def test_htr_manual_galpoes():
    # [MG] Tabela 2: htr = 150·ry -> W 410×67 = 6.000 mm; W 610×155 = 11.070 mm; W 200×15 = 3.180 mm
    for n, htr in (("W 410 x 67", 6000), ("W 610 x 155", 11070), ("W 200 x 15", 3180)):
        assert 150 * perfil(n).ry * 10 == pytest.approx(htr, abs=1)


# ------------------------------------------------------------------ bitolas [TVC] pp. 20–24
# nome: (Lb = Lp [cm], MRd FLT [kN·m], MRd FLM [kN·m], VRd [kN])
BITOLAS = {
    "W 150 x 13,0": (94, 30.23, 29.42, 119.76),
    "W 150 x 22,5": (155, 56.33, 52.98, 165.90),
    "W 200 x 15,0": (90, 46.39, 45.82, 161.84),
    "HP 200 x 53,0": (210, 172.91, 172.86, 433.80),
    "W 250 x 17,9": (84, 66.18, 65.50, 226.72),
    "HP 250 x 62,0": (260, 247.93, 230.36, 486.07),
    "W 310 x 21,0": (81, 91.55, 91.55, 290.80),
    "HP 310 x 79,0": (307, 379.53, 334.34, 618.93),
    "W 310 x 97,0": (325, 500.00, 490.72, 573.80),
    "W 360 x 44,6": (160, 245.99, 245.99, 457.06),
    "W 410 x 67,0": (170, 427.39, 427.39, 678.96),
    "W 460 x 74,0": (177, 519.82, 519.82, 773.99),
    "W 530 x 72,0": (178, 550.71, 545.59, 887.47),
    "W 610 x 82,0": (144, 696.24, 696.24, 1127.21),
    "W 610 x 155,0": (313, 1489.49, 1489.49, 1460.23),
}


@pytest.mark.parametrize("nome", BITOLAS)
def test_bitolas_tabela_vaos_cargas(nome):
    Lp, flt, flm, vrd = BITOLAS[nome]
    p = perfil(nome)
    r = momento_resistente(p, Lb=0.0)                      # Lb ≤ Lp, Cb = 1, σr = 0,3·fy
    assert r.Lp * 100 == pytest.approx(Lp, abs=1.0)        # tabela arredonda Lp ao cm (desvio ≤ 0,6 %)
    assert r.MRd_FLT == pytest.approx(flt, rel=0.002)
    assert r.MRd_FLM == pytest.approx(flm, rel=0.002)
    assert r.MRd == pytest.approx(min(flt, flm), rel=0.002)
    assert cortante_resistente(p) == pytest.approx(vrd, rel=0.002)


def test_fator_q_2008_coluna_bitolas():
    # [TVC] colunas Qs/Qa (σ = fy): W 410×38,8 Qa 0,87; W 310×21 Qa 0,86; W 200×15 Qa 0,97; HP 310×79 Qs 0,99
    assert fator_q(perfil("W 410 x 38,8"))[2] == pytest.approx(0.87, abs=0.006)
    assert fator_q(perfil("W 310 x 21,0"))[2] == pytest.approx(0.86, abs=0.006)
    assert fator_q(perfil("W 200 x 15,0"))[2] == pytest.approx(0.97, abs=0.006)
    assert fator_q(perfil("HP 310 x 79,0"))[1] == pytest.approx(0.99, abs=0.006)
    assert fator_q(perfil("W 410 x 67,0"))[2] == pytest.approx(0.97, abs=0.006)
    assert fator_q(perfil("W 410 x 85,0")) == (1.0, 1.0, 1.0)


# ------------------------------------------------------------------ FLT com Lb > Lp e Cb (conferido à mão)
def test_flt_inelastica_e_elastica_W310x32_7():
    # W 310×32,7: Iy 192, J 12,91, Cw 43.612, ry 2,13, Wx 419,8, Zx 485,3; fy 34,5; σr 10,35 kN/cm²
    # β1 = 24,15·419,8/(20000·12,91) = 0,039265; λr = 130,93 (Lr = 2,789 m); λp = 42,38 (Lp = 0,903 m)
    p = perfil("W 310 x 32,7")
    r2 = momento_resistente(p, Lb=2.0)
    assert r2.Lr == pytest.approx(2.789, abs=0.002)
    # Lb = 2 m: λ = 93,90; Mn = 16742,9 − (16742,9 − 10138,2)·(93,90−42,38)/(130,93−42,38) = 12900 kN·cm
    assert r2.MRd == pytest.approx(117.27, rel=0.001) and r2.governa == "FLT"
    # Cb = 1,136 (carga uniforme, Lb = vão): 1,136·117,27 = 133,22 ≤ Mpl/γa1 = 152,21
    assert momento_resistente(p, 2.0, Cb=fator_cb(1, 0.75, 1, 0.75)).MRd == pytest.approx(133.22, rel=0.002)
    # Lb = 3 m > Lr: Mcr = π²·20000·192/300² · √(43612/192·(1 + 0,039·12,91·300²/43612)) = 9062,5 kN·cm
    assert momento_resistente(p, Lb=3.0).MRd == pytest.approx(82.39, rel=0.001)
    # Cb alto não passa de Mpl
    assert momento_resistente(p, 2.0, Cb=3.0).MRd == pytest.approx(152.21, rel=0.001)


def test_fator_cb():
    assert fator_cb(1, 0.75, 1, 0.75) == pytest.approx(12.5 / 11)          # carga uniforme: 1,136
    assert fator_cb(1, 1, 1, 1) == pytest.approx(1.0)
    assert fator_cb(1, 0.25, 0, 0.25) == 3.0                                 # 12,5/4 = 3,125 -> limite 3,0


def test_momento_eixo_y():
    # W 150×22,5: bf/2tf = 11,52 (λp 9,15; λr 23,89): Mpl = 77,9·34,5 = 2687,6;
    # Mr = 24,15·50,9 = 1229,2; Mn = 2687,6 − 1458,4·(2,37/14,74) = 2453,1 kN·cm -> 22,30 kN·m
    assert momento_resistente_y(perfil("W 150 x 22,5")) == pytest.approx(22.30, rel=0.002)


# ------------------------------------------------------------------ cortante (5.4.3)
def test_cortante_com_e_sem_enrijecedor():
    # Perfis Gerdau: todos têm h/tw < λp (kv = 5) — enrijecedor não muda VRd
    p = perfil("W 610 x 82,0")
    assert cortante_resistente(p, a=0.6) == pytest.approx(cortante_resistente(p))
    # Alma esbelta fictícia (d 1000, tw 8, d' 960 mm; λ = 120), A572-50:
    # Vpl = 0,6·(100·0,8)·34,5 = 1656 kN
    # sem enrijecedor: kv 5, λp 59,22, λr 73,76 -> 1,24·(59,22/120)²·1656/1,10 = 454,7 kN
    # a = 1,0 m: a/h = 1,0417 -> kv = 9,608; λp 82,09, λr 102,24 -> 1,24·(82,09/120)²·1656/1,10 = 873,7 kN
    q = Perfil(nome="fict", familia="W", massa=100, d=1000, bf=300, tw=8, tf=20, h=960, d_linha=960, A=200,
               Ix=1, Wx=1, rx=1, Zx=1, Iy=1, Wy=1, ry=1, Zy=1, rt=1, It=1, Cw=1, u=1,
               formato_H=False, sob_encomenda=False)
    assert cortante_resistente(q) == pytest.approx(454.7, rel=0.002)
    assert cortante_resistente(q, a=1.0) == pytest.approx(873.7, rel=0.002)


# ------------------------------------------------------------------ compressão (5.3) x TCPA [TVC]
TCPA = [  # (perfil, eixo, KL [m], ELU [tf = kN/10])
    ("W 150 x 13,0", "y", 2.0, 28.79),      # p. 25
    ("W 150 x 13,0", "y", 1.0, 44.90),
    ("W 150 x 18,0", "y", 0.25, 72.77),
    ("W 150 x 13,0", "z", 2.0, 38.36),      # eixo X da TCPA governado pela flexo-torção (Lz = KL)
    ("W 610 x 82,0", "z", 5.5, 151.39),     # p. 73
    ("W 410 x 38,8", "y", 2.0, 100.94),     # alma esbelta (Q < 1), p. 60
    ("W 610 x 82,0", "y", 1.0, 269.76),     # alma esbelta
    ("W 610 x 82,0", "y", 3.0, 177.93),
    ("HP 250 x 62,0", "y", 2.0, 230.97),
    ("W 530 x 66,0", "y", 2.5, 157.43),
]


@pytest.mark.parametrize("nome,eixo,KL,elu", TCPA)
def test_compressao_tcpa(nome, eixo, KL, elu):
    p = perfil(nome)
    if eixo == "y":
        r = compressao_resistente(p, KLx=1e-3, KLy=KL, KLz=1e-3)
    else:
        r = compressao_resistente(p, KLx=KL, KLy=1e-3, KLz=KL)
    assert r.NcRd / 10 == pytest.approx(elu, rel=0.01)


def test_compressao_chi_e_metodo_2008():
    assert fator_chi(1.5) == pytest.approx(0.658 ** 2.25)
    assert fator_chi(2.0) == pytest.approx(0.877 / 4)
    p = perfil("W 410 x 38,8")
    r24 = compressao_resistente(p, 3.0, 3.0)
    r08 = compressao_resistente(p, 3.0, 3.0, metodo="2008")
    assert r08.Q == pytest.approx(fator_q(p)[0])
    assert r08.NcRd < r24.NcRd                 # método Q de 2008 (σ = fy) é mais conservador
    assert area_efetiva(perfil("W 410 x 85,0"), 34.5) == pytest.approx(perfil("W 410 x 85,0").A)   # d'/tw 32,7 < 35,9
    assert area_efetiva(perfil("W 410 x 67,0"), 34.5) / perfil("W 410 x 67,0").A == pytest.approx(0.97, abs=0.005)
    assert not compressao_resistente(perfil("W 150 x 13,0"), 5.0, 5.0).esbeltez_ok   # 500/2,22 > 200


# ------------------------------------------------------------------ tração e interação
def test_tracao():
    p = perfil("W 200 x 15,0")
    assert tracao_resistente(p) == pytest.approx(19.4 * 34.5 / 1.10)                  # 608,5 kN
    assert tracao_resistente(p, An=18.0, Ct=0.9) == pytest.approx(0.9 * 18 * 45 / 1.35)  # 540 kN
    assert tracao_resistente(p, aco_nome="A36") == pytest.approx(19.4 * 25 / 1.10)


def test_interacao_dois_ramos():
    assert interacao(-50, 40, 0, 100, 100, 50) == pytest.approx(0.5 + 8 / 9 * 0.4)
    assert interacao(-10, 40, 10, 100, 100, 50) == pytest.approx(0.05 + 0.4 + 0.2)
    assert interacao(30, 0, 0, 100, 100, 50) == pytest.approx(0.30)


# ------------------------------------------------------------------ flecha
def test_flecha_biapoiada():
    # W 310×32,7, q = 10 kN/m, L = 6 m: 5·0,10·600⁴/(384·20000·6570) = 1,284 cm
    p = perfil("W 310 x 32,7")
    assert flecha_biapoiada(p, 6.0, q=10.0) == pytest.approx(0.012843, rel=1e-3)
    assert flecha_biapoiada(p, 6.0, P=10.0) == pytest.approx(10 * 600 ** 3 / (48 * 20000 * 6570) / 100)
    assert LIMITES_FLECHA["viga_piso"] == 350


# ------------------------------------------------------------------ TVPA [TVC] pp. 79–102 (tf)
TVPA = [  # (caso, perfil, L [m], valor tabelado [tf]) — caso 1 = Q total; 2/3/4 = cada P
    (1, "W 150 x 13,0", 3.0, 5.2),
    (1, "W 150 x 22,5", 1.0, 22.1),       # limitado pela cortante (2·VRd/1,5)
    (1, "W 200 x 26,6", 4.0, 11.7),
    (1, "W 250 x 32,7", 5.0, 14.2),
    (1, "W 310 x 21,0", 6.0, 8.0),
    (1, "W 410 x 67,0", 3.0, 75.8),
    (1, "W 410 x 67,0", 8.0, 28.0),
    (1, "W 460 x 60,0", 10.0, 21.0),
    (1, "W 610 x 155,0", 12.0, 64.3),
    (1, "HP 250 x 62,0", 7.0, 17.3),
    (2, "W 360 x 32,9", 5.0, 9.1),
    (2, "W 530 x 72,0", 9.0, 15.9),
    (3, "W 250 x 44,8", 6.0, 6.2),
    (3, "W 610 x 101,0", 10.0, 18.0),
    (4, "W 200 x 46,1", 4.0, 5.1),
    (4, "W 460 x 82,0", 7.5, 10.1),
]


@pytest.mark.parametrize("caso,nome,L,tab", TVPA)
def test_tvpa(caso, nome, L, tab):
    # tabela em tf = kN/10, uma casa decimal: tolerância = meia unidade da última casa ou 1 %
    calc = tvpa(nome, L, caso, sigma_r=70.0) / 10
    assert abs(calc - tab) <= max(0.051, 0.01 * tab)


def test_tvpa_peso_proprio_descontado_e_flecha():
    p = perfil("W 410 x 67,0")
    M = momento_resistente(p).MRd / 1.5
    assert tvpa(p, 8.0) == pytest.approx(8 * (M - p.peso * 64 / 8) / 8.0)
    # coluna "Llim (1/350)" da TVPA: W 410×67 = 4.759 mm; W 150×13 = 1.772 mm; TVPA-2 W 360×32,9 = 4.966 mm
    assert tvpa_vao_limite_flecha(p) * 1000 == pytest.approx(4759, rel=0.002)
    assert tvpa_vao_limite_flecha("W 150 x 13,0", sigma_r=70) * 1000 == pytest.approx(1772, rel=0.002)
    assert tvpa_vao_limite_flecha("W 360 x 32,9", caso=2) * 1000 == pytest.approx(4966, rel=0.002)
    # mesa não travada reduz a carga (FLT com Lb = vão, Cb de carga uniforme)
    assert tvpa(p, 8.0, Lb=8.0, Cb=12.5 / 11) < tvpa(p, 8.0)


# ------------------------------------------------------------------ manual de galpões [MG]
def test_manual_galpoes_viga_cumeeira():
    # [MG] exemplo 3 (GMQ6/30/9/6): viga W 410×46,1, terças a cada 2,5 m (Lb = 2,5 m, item 3.3.3),
    # água com 15,06 m. Esforços ELU no nó 2 (cumeeira) da família W410, p. 27: N 56 kN, Q 14 kN, M 181 kN·m.
    r = verificar_barra(perfil("W 410 x 46,1"), N=-56, Mx=181, Vy=14, KLx=15.06, KLy=2.5, Lb=2.5)
    assert r["governa_Mx"] == "FLT"
    assert r["MxRd"] == pytest.approx(222.0, rel=0.002)
    assert r["ok"] and r["razao_interacao"] == pytest.approx(0.871, abs=0.005)
    # o W 410×38,8 (mais leve da família) não atende — coerente com a escolha do manual
    assert not verificar_barra(perfil("W 410 x 38,8"), N=-56, Mx=181, Vy=14, KLx=15.06, KLy=2.5, Lb=2.5)["ok"]


def test_manual_galpoes_coluna():
    # [MG] exemplos 1 e 3: L 30 m, H 9 m, B 6 m, Q6 -> coluna W 410×67,0, base engastada.
    # Reações ELU do exemplo 1: Rv1 = 78 kN, Mx2 = 177 kN·m, Rh2 = 51 kN. Comprimento destravado
    # fora do plano = htr máx. da Tabela 2 (150·ry = 6,0 m); KLx = H = 9 m (esforços de 1ª+2ª ordem).
    def ver(n):
        return verificar_barra(perfil(n), N=-78, Mx=177, Vy=51, KLx=9.0, KLy=6.0, Lb=6.0)
    r = ver("W 410 x 67,0")
    assert r["ok"] and r["razao_interacao"] == pytest.approx(0.933, abs=0.005)
    assert not ver("W 410 x 60,0")["ok"]       # o imediatamente mais leve não passa


# ------------------------------------------------------------------ validações de entrada
def test_entradas_invalidas():
    p = perfil("W 250 x 25,3")
    with pytest.raises(ValueError):
        momento_resistente(p, Lb=-1)
    with pytest.raises(ValueError):
        compressao_resistente(p, 0, 3)
    with pytest.raises(ValueError):
        tvpa(p, 5.0, caso=5)
    with pytest.raises(ValueError):
        tracao_resistente(p, Ct=1.2)
    with pytest.raises(ValueError):
        momento_resistente(p, aco_nome="S355")
    assert not math.isnan(momento_resistente(p, aco_nome="A36").MRd)
