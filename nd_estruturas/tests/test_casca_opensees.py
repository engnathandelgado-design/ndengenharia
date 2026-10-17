"""Conferência do uso de ShellMITC4 (OpenSeesPy) nos cálculos de placas (calc_fixacao_placas.py, DEC-026):
placa 10 × 1,25 m biapoiada nas pontas, carga fora do plano 1 kN/m² → Mxx = w·L²/8 = 12,5 kN·m/m e flecha 5wL⁴/(384EI).
Mostra também a armadilha: com o algoritmo Linear as tensões dos elementos saem zeradas (é preciso Newton)."""
import numpy as np
import pytest

ops = pytest.importorskip("openseespy.opensees")


def _placa(alg):
    L, H, t, E = 10.0, 1.25, 0.1, 30e6
    ops.wipe(); ops.model("basic", "-ndm", 3, "-ndf", 6)
    ops.section("ElasticMembranePlateSection", 1, E, 0.2, t, 0.0)
    nx, nz = 40, 4
    xs, zs = np.linspace(0, L, nx + 1), np.linspace(0, H, nz + 1)
    T, n = {}, 0
    for j, z in enumerate(zs):
        for i, x in enumerate(xs):
            n += 1; ops.node(n, x, 0, z); T[i, j] = n
    E_, e = [], 0
    for j in range(nz):
        for i in range(nx):
            e += 1; ops.element("ShellMITC4", e, T[i, j], T[i + 1, j], T[i + 1, j + 1], T[i, j + 1], 1); E_.append((e, i))
    ops.fix(T[0, 2], 1, 1, 1, 0, 0, 0); ops.fix(T[nx, 2], 0, 1, 1, 0, 0, 0)
    for j in (0, 1, 3, 4):
        ops.fix(T[0, j], 0, 1, 0, 0, 0, 0); ops.fix(T[nx, j], 0, 1, 0, 0, 0, 0)
    ops.timeSeries("Linear", 1); ops.pattern("Plain", 1, 1)
    for (e, i) in E_:
        for nn in ops.eleNodes(e):
            ops.load(nn, 0, -(L / nx) * (H / nz) / 4, 0, 0, 0, 0)
    ops.system("UmfPack"); ops.constraints("Plain"); ops.numberer("RCM"); ops.integrator("LoadControl", 1.0)
    if alg == "Newton":
        ops.test("NormDispIncr", 1e-12, 10)
    ops.algorithm(alg); ops.analysis("Static")
    assert ops.analyze(1) == 0
    M = sum(np.array(ops.eleResponse(e, "stresses")).reshape(4, 8)[:, 3].mean() * H / nz for (e, i) in E_ if i == nx // 2 - 1)
    w = abs(ops.nodeDisp(T[nx // 2, 2], 2))
    ops.wipe()
    return M, w


def test_momento_e_flecha_com_newton():
    M, w = _placa("Newton")
    assert M == pytest.approx(1.25 * 10 ** 2 / 8, rel=0.01)                   # w·L²/8 × altura
    assert w == pytest.approx(5 * 1.25 * 10 ** 4 / (384 * 30e6 * 1.25 * 0.1 ** 3 / 12), rel=0.01)


def test_linear_nao_atualiza_tensoes():
    M, _ = _placa("Linear")
    assert abs(M) < 1e-9
