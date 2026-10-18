"""Ombreira OM-1 da porta da vista I (Letsara rev06d, DEC-028): equilíbrio do MEF da placa e conferências à mão."""
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

AQ = Path(__file__).resolve().parents[1] / "exemplos" / "letsara"


@pytest.fixture(scope="module")
def R():
    subprocess.run([sys.executable, str(AQ / "calc_ombreira.py")], check=True, capture_output=True,
                   env={"PYTHONPATH": str(AQ.parents[1]), "PATH": "/usr/bin:/bin"})
    return json.loads((AQ / "ombreira.json").read_text(encoding="utf-8"))


def test_equilibrio_mef_placa(R):
    for caso in ("sem_U", "com_U"):
        c = R["placa_porta"][caso]
        assert abs(c["soma_kN"] - c["carga_kN"]) < 0.05


def test_inercia_U_a_mao(R):
    # U 125 × 80 × 6,3: alma t·h³/12 + 2 abas (b − t)·t·(h/2 − t/2)² (+ parcela própria desprezível) — conta à mão
    h, b, t = 125.0, 80.0, 6.3
    I = t * h ** 3 / 12 + 2 * (b - t) * t * (h / 2 - t / 2) ** 2
    assert R["U"]["I_mm4"] == pytest.approx(I, rel=0.002)


def test_reacoes_U_somam_cargas(R):
    U = R["U"]
    total = U["q_porta_kNm"] * U["L_mm"] / 1000 + U["R_placa_kN"] + R["p_k_kNm2"] * 0.30 * (U["L_mm"] / 1000 - (1.25 - 0.0125))
    assert U["R_base_k_kN"] + U["R_topo_k_kN"] == pytest.approx(total, abs=0.02)


def test_usos(R):
    assert R["U"]["uso_flexao"] <= 1 and R["U"]["flecha_k_mm"] <= R["U"]["lim_mm"]
    assert R["ligacoes"]["topo"]["uso"] <= 1 and R["ligacoes"]["base"]["uso"] <= 1
    assert R["placa_I15"]["uso_8cord"] > 1 >= R["placa_I15"]["uso_12cord"]
