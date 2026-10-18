"""Letsara rev06c — análise por elementos finitos do console CS-1 (casca, OpenSeesPy ShellMITC4). Gera mef_cs1.json
(resultados e malha para o visualizador 3D) e confere com a análise de calc_fixacao_placas.py e com contas à mão.

Modelo (mm, N, MPa) — eixos do console: x transversal, y a partir da face da CE-1 rumo à placa, z a partir do topo da mesa.
  costas   16 mm, plano y = 8 (meia espessura), x ±60, z −170 a +30; engaste nas 2 bordas verticais x = ±60 (filetes de obra
           de 6 mm na CE-1 — a CE-1 e o pilar são bem mais rígidos que o console);
  almas    9,5 mm, planos x = ±35, de y = 8 a 64, altura 80 na raiz e 50 na ponta (borda inferior inclinada);
  mesa     16 mm, plano z = 0, x ±40, y 8 a 64 (furo Ø18 do M16 de nível desprezado: a porca soldada fecha o furo);
  ponta    9,5 mm, plano y = 64 entre as almas, z −50 a 0;
  dentes   2 chapas 19 mm, plano y = 54, x de ±27 a ±40, z 0 a 32 (sobre as almas).
Nós comuns em todas as arestas de ligação (soldas contínuas = ligação rígida).
Cargas de cálculo por console (calc_fixacao_placas, cargas_por_console): Vd = 26,8 kN (montagem, γf 1,3 × βa 1,3 — NBR 9062:2017
5.3.2) no anel da porca do M16 de nível (s = 24) e vento Fd = 13,8 kN: sobrepressão no anel da porca do prisioneiro frontal
(chapa de ponta, rumo à CE-1) ou sucção nos 2 dentes (contato da aba do NC-1 a 5 mm do topo, rumo à placa).
Critério: von Mises nas faces da casca ≤ fy/γa1 = 345/1,10 = 314 MPa (critério de von Mises do EN 1993-1-1:2005 6.2.1(5); γa1 da NBR 8800:2008), usando o percentil 99
para excluir os picos singulares nos cantos engastados e nos pontos de carga.
"""
import json
import math
import os
from pathlib import Path

import numpy as np
import openseespy.opensees as ops

AQ = Path(__file__).parent
FX = json.loads(Path(os.environ.get("CS1_FX", AQ / "fixacao_placas.json")).read_text(encoding="utf-8"))
C = FX["GEO"]["CS1"]
CG = FX["cargas_por_console"]
ES, NU, FY, GA1 = 200000.0, 0.3, 345.0, 1.10
Vd, Fd = CG["Vd_kN"] * 1e3, CG["vento_d_kN"] * 1e3
YC = C["costas"]["t"] / 2
XA, TA = C["alma"]["x"], C["alma"]["t"]
YP = C["alma"]["y1"]
HR, HP = C["alma"]["h_raiz"], C["alma"]["h_ponta"]
TM, BM = C["mesa"]["t"], C["mesa"]["b"] / 2
DE = C["dente"]
YD = DE["y0"] + DE["t"] / 2
TP = C["ponta"]["t"]
YN, ZF = C["y_nivel"], C["z_frontal"]
S_PORCA = FX["GEO"]["hex"]["s"]


def grade(pts, h):
    out = [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        n = max(1, math.ceil((b - a) / h - 1e-9))
        out += [a + (b - a) * k / n for k in range(1, n + 1)]
    return out


def zb(y):                                             # borda inferior da alma (raiz −80 em y ≤ 16, ponta −50 em y = 64)
    y0 = C["alma"]["y0"]
    return -HR if y <= y0 else -HR + (HR - HP) * (y - y0) / (YP - y0)


def montar(h=4.0):
    X = grade([-60, -BM, -XA, -DE["x0"] - DE["b"] + 0, -DE["x0"], -12, 0, 12, DE["x0"], DE["x0"] + DE["b"], XA, BM, 60], h)
    X = sorted(set(round(v, 6) for v in X))
    Y = grade([YC, 16, 36, YN, YD, 60, YP], h)
    ZC = grade([C["costas"]["z0"], -HR, -HP, ZF, -16, 0, C["costas"]["z1"]], h)
    S = [z / -HR for z in ZC if -HR <= z <= 0]           # parâmetros da altura da alma (1 na borda inferior, 0 na mesa)
    nos, E = {}, []

    def no(x, y, z):
        k = (round(x, 4), round(y, 4), round(z, 4))
        if k not in nos:
            nos[k] = len(nos) + 1
        return nos[k]

    def quad(a, b, c, d, t, parte):
        E.append(([no(*a), no(*b), no(*c), no(*d)], t, parte))

    for i in range(len(X) - 1):                          # costas
        for j in range(len(ZC) - 1):
            quad((X[i], YC, ZC[j]), (X[i + 1], YC, ZC[j]), (X[i + 1], YC, ZC[j + 1]), (X[i], YC, ZC[j + 1]), C["costas"]["t"], "costas")
    for xa in (-XA, XA):                                 # almas (malha mapeada com a borda inclinada)
        for i in range(len(Y) - 1):
            for j in range(len(S) - 1):
                p = lambda y, s: (xa, y, s * zb(y))
                quad(p(Y[i], S[j]), p(Y[i + 1], S[j]), p(Y[i + 1], S[j + 1]), p(Y[i], S[j + 1]), TA, "almas")
    XM = [x for x in X if -BM - 1e-9 <= x <= BM + 1e-9]
    for i in range(len(XM) - 1):                         # mesa
        for j in range(len(Y) - 1):
            quad((XM[i], Y[j], 0), (XM[i + 1], Y[j], 0), (XM[i + 1], Y[j + 1], 0), (XM[i], Y[j + 1], 0), TM, "mesa")
    XP = [x for x in X if -XA - 1e-9 <= x <= XA + 1e-9]
    for i in range(len(XP) - 1):                         # chapa de ponta (z = s·zb(64))
        for j in range(len(S) - 1):
            p = lambda x, s: (x, YP, s * zb(YP))
            quad(p(XP[i], S[j]), p(XP[i + 1], S[j]), p(XP[i + 1], S[j + 1]), p(XP[i], S[j + 1]), TP, "ponta")
    ZD = grade([0, DE["h"] - 10, DE["h"]], h)
    for sg in (-1, 1):                                   # dentes
        XD = sorted(x for x in X if DE["x0"] - 1e-9 <= sg * x <= DE["x0"] + DE["b"] + 1e-9)
        for i in range(len(XD) - 1):
            for j in range(len(ZD) - 1):
                quad((XD[i], YD, ZD[j]), (XD[i + 1], YD, ZD[j]), (XD[i + 1], YD, ZD[j + 1]), (XD[i], YD, ZD[j + 1]), DE["t"], "dentes")
    return nos, E


def analisar(caso, h=4.0):
    nos, E = montar(h)
    ops.wipe(); ops.model("basic", "-ndm", 3, "-ndf", 6)
    for (x, y, z), n in nos.items():
        ops.node(n, x, y, z)
    secs = {}
    for k, (ns, t, parte) in enumerate(E):
        if t not in secs:
            secs[t] = len(secs) + 1
            ops.section("ElasticMembranePlateSection", secs[t], ES, NU, t, 0.0)
        ops.element("ShellMITC4", k + 1, *ns, secs[t])
    solda = [n for (x, y, z), n in nos.items() if abs(abs(x) - 60) < 1e-6 and abs(y - YC) < 1e-6]
    for n in solda:
        ops.fix(n, 1, 1, 1, 1, 1, 1)
    ops.timeSeries("Linear", 1); ops.pattern("Plain", 1, 1)
    carga = []
    anel = [n for (x, y, z), n in nos.items() if abs(z) < 1e-6 and math.hypot(x, y - YN) <= S_PORCA / 2 + 0.5]
    if caso in ("montagem", "sobrepressao", "succao"):
        for n in anel:
            ops.load(n, 0, 0, -Vd / len(anel), 0, 0, 0)
        carga.append(dict(tipo="peso", p=[0, YN, 0], d=[0, 0, -1], F_kN=Vd / 1e3))
    if caso == "sobrepressao":
        anf = [n for (x, y, z), n in nos.items() if abs(y - YP) < 1e-6 and math.hypot(x, z - ZF) <= S_PORCA / 2 + 0.5]
        for n in anf:
            ops.load(n, 0, -Fd / len(anf), 0, 0, 0, 0)
        carga.append(dict(tipo="vento", p=[0, YP, ZF], d=[0, -1, 0], F_kN=Fd / 1e3))
    if caso == "succao":
        zc = DE["h"] - 5.0
        lin = [n for (x, y, z), n in nos.items() if abs(y - YD) < 1e-6 and abs(z - zc) < 2.6 and DE["x0"] - 1e-6 <= abs(x) <= DE["x0"] + DE["b"] + 1e-6]
        zs = sorted({round(z, 4) for (x, y, z), n in nos.items() if n in lin})
        lin = [n for (x, y, z), n in nos.items() if n in lin and abs(z - min(zs, key=lambda v: abs(v - zc))) < 1e-6]
        for n in lin:
            ops.load(n, 0, Fd / len(lin), 0, 0, 0, 0)
        for sg in (-1, 1):
            carga.append(dict(tipo="vento", p=[sg * (DE["x0"] + DE["b"] / 2), YD, zc], d=[0, 1, 0], F_kN=Fd / 2e3))
    ops.system("UmfPack"); ops.numberer("RCM"); ops.constraints("Plain")
    ops.integrator("LoadControl", 1.0); ops.test("NormDispIncr", 1e-12, 10); ops.algorithm("Newton"); ops.analysis("Static")
    assert ops.analyze(1) == 0
    ops.reactions()
    Rz = sum(ops.nodeReaction(n, 3) for n in solda)
    Ry = sum(ops.nodeReaction(n, 2) for n in solda)
    vm_e, parte_e = [], []
    for k, (ns, t, parte) in enumerate(E):
        s = np.array(ops.eleResponse(k + 1, "stresses")).reshape(4, 8).mean(0)
        v = 0.0
        for sg in (+1, -1):
            sx = s[0] / t + sg * 6 * s[3] / t ** 2
            sy = s[1] / t + sg * 6 * s[4] / t ** 2
            txy = s[2] / t + sg * 6 * s[5] / t ** 2
            v = max(v, math.sqrt(sx ** 2 - sx * sy + sy ** 2 + 3 * txy ** 2))
        vm_e.append(v); parte_e.append(parte)
    U = {n: ops.nodeDisp(n)[:3] for n in nos.values()}
    vm_e = np.array(vm_e)
    res = dict(caso=caso, n_elem=len(E), n_nos=len(nos), vm_max=float(vm_e.max()), vm_p99=float(np.percentile(vm_e, 99)),
               vm_parte={p: dict(max=float(vm_e[[i for i, q in enumerate(parte_e) if q == p]].max()),
                                 p99=float(np.percentile(vm_e[[i for i, q in enumerate(parte_e) if q == p]], 99))) for p in sorted(set(parte_e))},
               u_max_mm=float(max(np.linalg.norm(u) for u in U.values())), dz_nivel_mm=float(-np.mean([U[n][2] for n in anel])),
               soma_Rz_kN=Rz / 1e3, soma_Ry_kN=Ry / 1e3, carga=carga)
    # tensão média na raiz das almas (fibra extrema inferior, linha y = 16) para a conferência à mão
    raiz = [i for i, (ns, t, p) in enumerate(E) if p == "almas" and abs(np.mean([k[1] for k, n in nos.items() if n in ns]) - 16) < h]
    res["almas_raiz_vm_med"] = float(np.mean(vm_e[raiz])) if raiz else None
    ops.wipe()
    return res, nos, E, U, vm_e


CASOS = {"montagem": "peso (montagem)", "sobrepressao": "peso + vento de sobrepressão", "succao": "peso + vento de sucção"}
R = dict(cargas=dict(Vd_kN=Vd / 1e3, Fd_kN=Fd / 1e3), criterio_MPa=round(FY / GA1, 1), casos={})
VIS = None
for k in CASOS:
    r, nos, E, U, vm = analisar(k, 4.0)
    r2, *_ = analisar(k, 2.0)                        # malha refinada (convergência)
    assert abs(r["soma_Rz_kN"] - (Vd / 1e3)) < 0.01  # equilíbrio vertical
    R["casos"][k] = dict(nome=CASOS[k], **{q: (round(v, 3) if isinstance(v, float) else v) for q, v in r.items() if q != "carga"},
                         p99_malha_2mm=round(r2["vm_p99"], 1),
                         p99_parte_malha_2mm={p_: round(v_["p99"], 1) for p_, v_ in r2["vm_parte"].items()},
                         uso_parte={p_: round(max(v_["p99"], r2["vm_parte"][p_]["p99"]) / (FY / GA1), 3) for p_, v_ in r["vm_parte"].items()})
    R["casos"][k]["uso"] = max(R["casos"][k]["uso_parte"].values())
    if VIS is None:
        inv = {n: k_ for k_, n in nos.items()}
        VIS = dict(nos=[list(inv[n]) for n in range(1, len(nos) + 1)], elem=[[n - 1 for n in ns] for ns, _, _ in E], parte=[p for _, _, p in E],
                   esp=[t for _, t, _ in E], casos={})
    VIS["casos"][k] = dict(nome=CASOS[k], u=[[round(c, 5) for c in U[n]] for n in range(1, len(nos) + 1)], vm=[round(float(v), 1) for v in vm],
                           carga=r["carga"], vm_p99=round(r["vm_p99"], 1), vm_max=round(r["vm_max"], 1), u_max=round(r["u_max_mm"], 4))
# conferência à mão: almas na raiz como 2 balanços de 80 × 9,5 com o peso a y = 48 (braço até a face das costas 16)
M = Vd * (YN - 16)
W = 2 * TA * HR ** 2 / 6
# seção T na raiz (2 almas 80 × 9,5 + mesa 80 × 16, colaborante): σ na fibra inferior = M·c/I
A1_, A2_ = 2 * HR * TA, 2 * BM * TM
yb = (A1_ * (-HR / 2) + A2_ * (-TM / 2)) / (A1_ + A2_)
I_T = 2 * TA * HR ** 3 / 12 + A1_ * (-HR / 2 - yb) ** 2 + 2 * BM * TM ** 3 / 12 + A2_ * (-TM / 2 - yb) ** 2
R["mao"] = dict(sigma_secao_T_raiz_MPa=round(M * (HR + yb) / I_T, 1), sigma_almas_raiz_MPa=round(M / W, 1), tau_almas_MPa=round(Vd / (2 * TA * HR), 1),
                vm_mao_MPa=round(math.sqrt((M / W) ** 2 + 3 * (Vd / (2 * TA * HR)) ** 2), 1),
                mef_almas_raiz_vm_med_MPa=round(R["casos"]["montagem"]["almas_raiz_vm_med"], 1))
R["uso"] = max(c["uso"] for c in R["casos"].values())
R["anterior_calc_fixacao_placas"] = FX["console_mef"]
Path(os.environ.get("CS1_MEF_SAIDA", AQ / "mef_cs1.json")).write_text(json.dumps(R, indent=1, ensure_ascii=False), encoding="utf-8")
Path(os.environ.get("CS1_VIS_SAIDA", AQ / "saidas" / "mef_cs1_vis.json")).write_text(json.dumps(VIS, separators=(",", ":")), encoding="utf-8")
assert R["uso"] <= 1.0
if __name__ == "__main__":
    print(json.dumps(R, indent=1, ensure_ascii=False))
