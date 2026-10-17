"""Vento NBR 6123:1988 — conferências à mão (Tabela 1, item 4.2, Tabela 4, item 6.2.5)."""
from nd_estruturas import vento_nbr6123 as V
from nd_estruturas.prefabricados import pressao_vento


def test_s2_e_q():
    assert abs(V.S2(10, "III", "C") - 0.93 * 0.95) < 1e-9
    assert abs(V.q(10, 45, S3=0.95) - pressao_vento(45, z=10, S3=0.95)) < 1e-9


def test_paredes_letsara():
    c = V.cpe_paredes(10.0, 79.35, 39.5)      # h/b = 0,25; a/b = 2,0
    assert c["a0"]["C"] == 0.7 and c["a0"]["D"] == -0.3 and c["a90"]["B"] == -0.5


def test_cpi_abertura():
    assert V.cpi_abertura_dominante(6, "barlavento") == 0.8
    assert V.cpi_abertura_dominante(1.5, "barlavento") == 0.3
    assert V.cpi_uniforme() == (-0.3, 0.0)
