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
