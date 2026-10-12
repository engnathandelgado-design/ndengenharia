"""Testes do módulo prefabricados — valores conferidos à mão (12/10/2026)."""
import math

import pytest

from nd_estruturas.prefabricados import (
    Concreto, pilar_metodo_geral, pressao_vento, secao_I, secao_retangular, torcao_retangular,
)


def test_secao_retangular():
    s = secao_retangular(0.40, 1.00)
    assert s.A == pytest.approx(0.40)
    assert s.yc == pytest.approx(0.50)
    assert s.I == pytest.approx(0.40 / 12)


def test_secao_I90_area_por_partes():
    # mesa inf 0,40×0,15 + mísula inf (0,40+0,12)/2×0,08 + alma 0,12×0,52
    # + mísula sup (0,12+0,40)/2×0,05 + mesa sup 0,40×0,10 = 0,1962 m²
    s = secao_I(0.90)
    assert s.A == pytest.approx(0.1962, abs=1e-4)
    assert s.largura_em(0.45) == pytest.approx(0.12)


def test_concreto_c40():
    c = Concreto(40)
    assert c.fcd == pytest.approx(28571.4, rel=1e-4)
    assert c.fctm == pytest.approx(0.3 * 40 ** (2 / 3))
    with pytest.raises(ValueError):
        Concreto(15)


def test_vento_cat3_classeC():
    # S2 = 0,93·0,95 = 0,8835; Vk = 39,76 m/s; q = 0,613·Vk² = 969 N/m²
    assert pressao_vento(45) == pytest.approx(0.969, abs=0.002)


def test_torcao_bielas():
    # b=0,40 h=1,00: A/u = 0,143 → he = 0,143; Ae = 0,257·0,857 = 0,2203 m²
    # TRd2 = 0,5·(1−40/250)·28571·0,2203·0,143·sin90° = 378 kN·m
    r = torcao_retangular(0.40, 1.00, 0.0, 0.0, Concreto(40))
    assert r["TRd2_kNm"] == pytest.approx(378, rel=0.01)


def test_pilar_metodo_geral_flexao_simples():
    # 40×60, 5Ø20/face (15,71 cm²), N≈0: MRd ≈ As·fyd·0,9d = 15,71e-4·434783·0,9·0,555 ≈ 341 kN·m
    # balanço de 10 m com carga distribuída: w_u = 2·MRd/L² ≈ 6,8 kN/m → λu ≈ 6,8/5 = 1,36
    r = pilar_metodo_geral(0.40, 0.60, 10.0, 15.71, 10.0, 5.0, Concreto(40), phi_ef=0.0)
    assert 1.25 <= r["lambda_u"] <= 1.45
