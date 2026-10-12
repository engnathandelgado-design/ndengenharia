"""Testes do módulo formfinding (JAX FDM -> OpenSees). Rodar: pytest -q tests/test_formfinding.py"""
import numpy as np
import pytest
from nd_estruturas.formfinding import (forma_casca, forma_geometrica, modelo_casca, cargas,
                                       analisar_linear, esforcos)

N = 12   # malha leve para o teste


@pytest.fixture(scope="module")
def forma():
    return forma_casca(n=N)


def test_metas_de_altura(forma):
    xyz = forma["xyz"]; c = N // 2
    assert xyz[c, c, 2] == pytest.approx(4.0, abs=1e-4)
    assert xyz[c, 0, 2] == pytest.approx(2.5, abs=1e-4)


def test_so_compressao(forma):
    assert max(forma["forcas"].values()) < 0


def test_equilibrio_rede(forma):
    Rz = sum(-r[2] for r in forma["reacoes"])
    assert Rz == pytest.approx(3.5 * 20 * 20 * (1 - 4 * 0.25 / N**2), rel=1e-6)   # cantos sem carga


def test_casca_reproduz_empuxo_da_rede(forma):
    mod = modelo_casca(forma["xyz"]); P = cargas(mod, lambda x, y: 3.5); assert analisar_linear()
    out, R, w = esforcos(mod)
    assert sum(r[2] for r in R) == pytest.approx(P, rel=1e-6)
    H_rede = np.hypot(*forma["reacoes"][0][:2]); H_casca = np.hypot(*R[0][:2])
    assert H_casca == pytest.approx(H_rede, rel=0.05)
    assert max(o["N1"] for o in out) < 0.05 * abs(min(o["N2"] for o in out))   # quase sem tração de membrana


def test_funicular_flete_menos_que_geometrica(forma):
    Ms = []
    for X in (forma["xyz"], forma_geometrica(n=N)):
        mod = modelo_casca(X); cargas(mod, lambda x, y: 3.5); analisar_linear()
        Ms.append(max(o["M_abs"] for o in esforcos(mod)[0]))
    assert Ms[0] < 0.6 * Ms[1]


def test_arco_funicular_confere_M0_sobre_f():
    """Conferido à mão: 19 cargas de 10 kN a cada 1 m num vão de 20 m -> V = 95 kN,
    M0 = 95·10 − 10·(1+2+…+9) = 950 − 450 = 500 kN·m; f = 2,5 m -> H = 200 kN."""
    from nd_estruturas.formfinding import arco_funicular
    xs = np.linspace(-10, 10, 21); P = np.full(21, 10.0); P[0] = P[-1] = 0.0
    r = arco_funicular(xs, P, f_alvo=2.5)
    assert r["H"] == pytest.approx(200.0, rel=1e-4)
    assert max(r["forcas"]) < 0
    r2 = arco_funicular(xs, P, H_alvo=125.0)                 # inverso: f = M0/H = 4,0 m
    assert r2["z"].max() == pytest.approx(4.0, rel=1e-3)


def test_entrada_invalida():
    from nd_estruturas.formfinding import arco_funicular
    with pytest.raises(ValueError):
        arco_funicular([0, 1, 2], [0, 1, 0])
