"""Viga contínua por MEF — conferida com as fórmulas clássicas (Formulário de vigas, qualquer manual de resistência)."""
import numpy as np
from nd_estruturas.viga_continua import analisar


def test_biapoiada():
    r = analisar([6.0], 1000.0, 2.0)
    assert abs(r["M"].max() - 2.0 * 36 / 8) < 1e-6
    assert abs(r["v"].max() - 5 * 2.0 * 6 ** 4 / (384 * 1000.0)) < 1e-6


def test_dois_vaos_iguais():
    r = analisar([1.0, 1.0], 1.0, 1.0)
    assert abs(r["M"].min() + 0.125) < 1e-6           # apoio central −wL²/8
    assert abs(r["M"].max() - 9 / 128) < 1e-3         # vão +9wL²/128
    assert np.allclose(r["reacoes"], [0.375, 1.25, 0.375])


def test_trecho_rigido_atrai_momento():
    a = analisar([1.0, 1.0], 1.0, 1.0)
    b = analisar([1.0, 1.0], 1.0, 1.0, EI_trechos=[(0.9, 1.1, 2.0)])
    assert b["M"].min() < a["M"].min()
