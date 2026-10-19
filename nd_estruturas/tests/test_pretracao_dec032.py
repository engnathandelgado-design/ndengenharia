"""Testes das funções de pré-tração da DEC-032 (prefabricados.py), conferidos à mão.

Fontes: NBR 6118:2023 Tab. 8.2 (φ e εcs), Tab. 8.4 (ψ1000), 8.4.8, 9.4.5 (lbpt), 9.6.3.4.2 (perdas progressivas,
processo simplificado) e 17.2.4.3.2 (ato); NBR 9062:2017 7.3.1.1 (γn). Contas à mão nos comentários.
"""
import math

import pytest

from nd_estruturas.prefabricados import (Concreto, secao_retangular, fluencia_retracao, psi1000_rb, relaxacao,
                                         lbpt_cordoalha, gama_n_consolo, perdas_pretracao, ato_pretracao, CORD)


def test_tab_8_2_pontos_da_tabela():
    # NBR 6118:2023 Tab. 8.2, U 75 %, 2Ac/u 20 cm, t0 5 dias: φ 2,8 e εcs −0,36 ‰; 60 cm, 60 dias: 1,8 e −0,31 ‰
    assert fluencia_retracao(75, 20, 5) == pytest.approx((2.8, -0.36e-3))
    assert fluencia_retracao(75, 60, 60) == pytest.approx((1.8, -0.31e-3))
    # interpolação linear em U entre 55 e 75 (h 20, t0 5): φ = (3,9 + 2,8)/2 = 3,35
    assert fluencia_retracao(65, 20, 5)[0] == pytest.approx(3.35)


def test_relaxacao_rb():
    # Tab. 8.4: σp/fptk 0,7 → ψ1000 2,5 %; ψ∞ = 2,5 ψ1000 = 6,25 % (8.4.8)
    assert psi1000_rb(0.7) == pytest.approx(2.5)
    assert psi1000_rb(0.5) == 0.0
    d, psi = relaxacao(0.7 * 1900, math.inf)
    assert psi == pytest.approx(0.0625)
    assert d == pytest.approx(0.0625 * 1330)


def test_lbpt_cordoalha_a_mao():
    # fckj 35: fctm = 0,3·35^(2/3) = 3,210; fctd = 0,7·3,210/1,4 = 1,605; fbpd = 1,2·1,605 = 1,926 MPa
    # lbp = 7·12,7/36 · (1710/1,15)/1,926 = 2,4694 · 1486,96/1,926 = 1906 mm
    # lbpt (gradual) = 0,5·lbp·σp/fpyd = 0,5·1906·1369,6/1486,96 = 878 mm (é o valor da TS-01)
    lbpt, lbp, fbpd = lbpt_cordoalha(35.0, 1369.6)
    assert fbpd == pytest.approx(1.926, abs=0.002)
    assert lbp == pytest.approx(1.906, abs=0.002)
    assert lbpt == pytest.approx(0.878, abs=0.002)
    assert lbpt_cordoalha(35.0, 1369.6, gradual=False)[0] == pytest.approx(0.878 * 1.25, abs=0.003)


def test_gama_n_consolo():
    # NBR 9062:2017 7.3.1.1 — pré-moldado: 1,1 permanente preponderante, 1,2 nos demais
    assert gama_n_consolo(80, 20) == 1.1
    assert gama_n_consolo(40, 60) == pytest.approx(1.2)
    assert gama_n_consolo(80, 20, pre_fabricado=True) == 1.0


def test_perdas_pretracao_centrada_confere_a_mao():
    # Placa 125 × 10 com 8 Ø12,7 centradas, C40, fckj 25, sem peso em t0, U 70 %, t0 5 d.
    b, h = 1.25, 0.10
    A, I = b * h, b * h ** 3 / 12
    Ap = 8 * 98.7e-6
    r = perdas_pretracao(1400.0, Ap, A, I, h / 2, h / 2, 0.0, Concreto(40), 25.0, 2 * (b + h), U=70.0, t0_dias=5.0)
    # cravação: 6 mm / 60 m · 195 GPa = 19,5 MPa
    assert r["d_cravacao"] == pytest.approx(19.5)
    # encurtamento elástico: Δσ = αp·σc, σc = P0/A (e = 0); conferir a consistência da iteração
    alfa = r["alfa_p_j"]
    sc = r["P0"] / A / 1000
    assert r["d_elastica"] == pytest.approx(alfa * sc, rel=1e-3)
    # progressivas 9.6.3.4.2 (sem fases): refazer a fórmula à mão
    phi, ecs = r["phi"], r["eps_cs"]
    ap = 195000 / (Concreto(40).Eci / 1000)
    s0 = r["sig_p0"]
    psi = 2.5 * psi1000_rb(s0 / 1900) / 100
    chi = -math.log(1 - psi)
    d_a = -(ecs * 195000 - ap * sc * phi - s0 * chi) / ((1 + chi) + (1 + 0.5 * phi) * ap * 1.0 * (Ap / A))
    d_b = (7.4 + ap / 18.7 * phi ** 1.07 * (3 + sc)) / 100 * s0
    assert r["d_prog"] == pytest.approx(max(d_a, d_b), rel=1e-6)
    assert 20 < r["perda_total_pct"] < 30


def test_ato_pretracao_forca_centrada_uniforme():
    # Seção 40 × 90 com 8 cordoalhas no centroide, sem peso: depois de lbpt a tensão é −γp·P/A em toda a seção
    sec = secao_retangular(0.40, 0.90)
    sig_p0 = 1300.0
    P = 8 * CORD["12.7"] * sig_p0 * 1000
    r = ato_pretracao(sec, sec, 0.0, 10.0, [dict(n=8, y=0.45, x0=0.0)], sig_p0, 0.0, 35.0, 0.8, dx=0.05)
    pt = next(p for p in r["pontos"] if p["x"] >= 1.0)
    assert pt["base"] == pytest.approx(-1.1 * P / sec.A / 1000, rel=1e-6)
    assert pt["topo"] == pytest.approx(pt["base"], rel=1e-6)
    assert r["lim_c"] == pytest.approx(-0.7 * 35)
    assert r["lim_t"] == pytest.approx(1.2 * 0.3 * 35 ** (2 / 3))
    # antes de lbpt a força é proporcional a x/lbpt
    p04 = next(p for p in r["pontos"] if abs(p["x"] - 0.4) < 1e-6)
    assert p04["P"] == pytest.approx(1.1 * P * 0.4 / 0.8, rel=1e-6)
