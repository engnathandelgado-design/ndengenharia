"""Letsara rev06c: compatibilidade geométrica CS-1 × NC-1 (folgas no pior caso das tolerâncias) e usos das verificações
gravados por exemplos/letsara/calc_fixacao_placas.py. Conferência à mão do dente: M = 6,9 kN × 27 mm, W = 13 × 19²/6."""
import json
from pathlib import Path

import pytest

ARQ = Path(__file__).parents[1] / "exemplos" / "letsara" / "fixacao_placas.json"


@pytest.mark.skipif(not ARQ.exists(), reason="rode calc_fixacao_placas.py")
def test_folgas_e_usos():
    R = json.loads(ARQ.read_text(encoding="utf-8"))
    fo = R["montagem_CS1_NC1"]["folgas_mm"]
    assert all(v >= 0 for v in fo.values()), fo
    assert fo["engate aba–dente com G máximo (z)"] >= 10
    for k in ("console_mef", "dentes_CS1", "solda"):
        assert R[k]["uso"] <= 1.0
    assert R["nicho_NC1"]["fundo"]["uso"] <= 1 and R["nicho_NC1"]["aba"]["uso"] <= 1
    d = R["dentes_CS1"]
    assert d["sigma_MPa"] == pytest.approx(6.9e3 * 27 / (13 * 19 ** 2 / 6), rel=0.02)
