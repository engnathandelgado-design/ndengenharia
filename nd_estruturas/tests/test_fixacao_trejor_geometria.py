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
    # rev06d (DEC-030): chapas e soldas do nicho pelo MEF de casca (mef_nc1); a viga à mão do fundo é só limite superior
    m = R["nicho_NC1"]["mef"]
    assert m["atual"] and max(m["uso"].values()) <= 1
    assert {"solda_teto_fundo", "solda_base_fundo", "solda_parede"} <= set(m["uso"])
    c = R["console_mef_casca"]
    assert c["uso"] <= 1 and max(c["soldas"].values()) <= 1
    d = R["dentes_CS1"]
    assert d["sigma_MPa"] == pytest.approx(6.9e3 * 30 / (13 * 19 ** 2 / 6), rel=0.02)
