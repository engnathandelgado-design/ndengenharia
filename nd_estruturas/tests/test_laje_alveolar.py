"""Testes de nd_estruturas.laje_alveolar conferidos à mão.

Fontes: geometria (A e I de retângulo menos círculos — fórmulas de resistência dos materiais); EN 1992-1-1:2004
eq. (6.4) / EN 1168 4.3.3.2.2 (VRd,c = I·bw/S·√(fctd² + αl·σcp·fctd)); NBR 6118:2023 17.4.2.2 (VRd1);
frequência de viga biapoiada f = π/(2L²)·√(EI/m) (Clough & Penzien, viga de Euler-Bernoulli).
"""
import math

import pytest

from nd_estruturas.laje_alveolar import SecaoAlveolar, vrd_tracao_alma, vrd1_nbr, frequencia_biapoiada, composta


def test_area_inercia_com_alveolos():
    # 1,00 × 0,20 com 2 alvéolos Ø0,10 no meio da altura:
    # A = 0,20 − 2·π·0,05² = 0,184292 m²; I = 1·0,2³/12 − 2·π·0,1⁴/64 = 6,6667e-4 − 9,8175e-6 = 6,5685e-4 m⁴
    s = SecaoAlveolar(b=1.0, h=0.20, n=2, d=0.10, passo=0.40, dy=0.0002)
    assert s.A == pytest.approx(0.184292, rel=1e-3)
    assert s.yc == pytest.approx(0.10, abs=1e-6)
    assert s.I == pytest.approx(6.5685e-4, rel=2e-3)
    # nervuras: bordas (1,0 − 0,4 − 0,1)/2 = 0,25 e interna 0,40 − 0,10 = 0,30
    assert s.larg_nervuras() == pytest.approx([0.25, 0.30, 0.25])
    assert s.bw_min == pytest.approx(0.80)


def test_tracao_alma_secao_retangular():
    # retângulo 0,30 × 0,50 (sem alvéolos): I·b/S no centroide = 2bh/3 = 0,10 m²
    # sem protensão: VRd = 0,10 · 1500 kPa = 150 kN
    # P = 300 kN → σcp = 300/0,15 = 2000 kPa → √(1500² + 2000·1500) = 2291,3 kPa → 229,1 kN
    s = SecaoAlveolar(b=0.30, h=0.50, n=0, d=0.01, passo=0.01, dy=0.0002)
    v0, y0 = vrd_tracao_alma(s, 1.5, 0.0, n_pts=200)
    assert v0 == pytest.approx(150.0, rel=2e-3)
    assert y0 == pytest.approx(0.25, abs=0.01)
    v1, _ = vrd_tracao_alma(s, 1.5, 300.0, n_pts=200)
    assert v1 == pytest.approx(229.1, rel=2e-3)


def test_vrd1_nbr_a_mao():
    # fck 50: fctm = 0,3·50^(2/3) = 4,072; fctd = 0,7·4,072/1,4 = 2,036; τRd = 0,509 MPa
    # bw 0,333, d 0,21: k = 1,6 − 0,21 = 1,39; ρ1 = 0,01 → (1,2 + 0,4) = 1,6; σcp 5 → 0,15·5 = 0,75
    # VRd1 = (0,509·1,39·1,6 + 0,75)·0,333·0,21·1000 = 1,882·0,06993·1000 = 131,6 kN
    assert vrd1_nbr(0.333, 0.21, 50.0, 0.01, 5.0) == pytest.approx(131.6, rel=2e-3)


def test_frequencia_biapoiada():
    # EI = 1e5 kN·m², m = 1 t/m, L = 10 m: f = π/200·√1e5 = 4,967 Hz
    assert frequencia_biapoiada(1e5, 1.0, 10.0) == pytest.approx(4.967, rel=1e-3)


def test_composta_retangulo_mais_capa():
    # laje maciça 1,0 × 0,20 + capa 1,0 × 0,05 com n = 0,5 (área 0,025):
    # A = 0,225; yc = (0,2·0,1 + 0,025·0,225)/0,225 = 0,11389
    # I = 1·0,2³/12 + 0,2·(0,1 − 0,11389)² + 0,5·1·0,05³/12 + 0,025·(0,225 − 0,11389)²
    #   = 6,6667e-4 + 3,858e-5 + 5,208e-6 + 3,0864e-4 = 1,01910e-3
    s = SecaoAlveolar(b=1.0, h=0.20, n=0, d=0.01, passo=0.01, dy=0.0001)
    c = composta(s, 1.0, 0.05, 0.5)
    assert c["A"] == pytest.approx(0.225, rel=1e-3)
    assert c["yc"] == pytest.approx(0.11389, rel=1e-3)
    assert c["I"] == pytest.approx(1.01910e-3, rel=2e-3)
