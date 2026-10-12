"""Letsara — modelo global 3D (OpenSeesPy) para deslocamentos e estabilidade global.

Pilares engastados no cálice (elasticBeamColumn, Ecs·Ic — estádio I sob vento frequente, ver
resumo); vigas pré-moldadas articuladas = treliças (só esforço axial: escora/tirante);
contraventamento em X da cobertura nos vãos extremos; laje do mezanino como diafragma (treliças).
Cargas: peso das vigas e das placas nos pilares (placas excêntricas → momento), vento NBR 6123
(V0 45, S3 0,95) frequente ψ1 = 0,3 para ELS e característico para γz.
Saída: deslocamentos do topo, razão 2ª/1ª ordem (≈ γz), forças nas escoras e figuras.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import openseespy.opensees as ops

from nd_estruturas.prefabricados import Concreto, pressao_vento

AQUI = Path(__file__).parent
C = Concreto(40)
E, G = C.Ecs, C.Ecs / 2.4
qv = pressao_vento(45.0, S3=0.95)

# --------------------------------------------------------------- geometria (R01 + decisões)
YL = [0.0, 10.05, 19.705, 29.36, 38.865, 48.445, 58.025, 67.605, 76.81]  # linhas de pórtico
XF = [0.0, 9.87, 20.05, 29.63, 40.10]                                    # eixos da fachada
X_CEN = 20.05
VAOS_CONTRAV = [(0, 1), (1, 2), (3, 4), (4, 5), (6, 7), (7, 8)]
N_PAINEL = 5            # painéis por meia água (≈ 4,0 m)
A_BARRA = 1.13e-4       # barra redonda A36 Ø12 (conferido abaixo)
Z_P1, Z_P2, Z_CEN, Z_TOP = 8.53, 9.73, 9.12, 10.0   # assento dos dentes da I90: P1 (baixo), P2 (alto), centro; topo da platibanda
Z_MEZ = [3.15, 6.55]
TRIB_Y = [(YL[min(i + 1, 8)] - YL[max(i - 1, 0)]) / 2 for i in range(9)]
TRIB_X = [(XF[min(i + 1, 4)] - XF[max(i - 1, 0)]) / 2 for i in range(5)]
I90_A = 0.2225
Rg_I = (I90_A * 25 + 0.25 * 9.655) * 19.15 / 2      # reação da I90 por apoio (kN)
W_placa_m = 2.5 * 10.0                               # kN por metro de fachada (placa 10 cm, 10 m)
E_PLACA = 0.40

nos, tag = {}, [0]


def no(x, y, z):
    k = (round(x, 3), round(y, 3), round(z, 3))
    if k not in nos:
        tag[0] += 1
        nos[k] = tag[0]
        ops.node(tag[0], x, y, z)
    return nos[k]


def montar(pdelta=True):
    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)
    nos.clear(); tag[0] = 0
    ops.geomTransf("PDelta" if pdelta else "Linear", 1, 1, 0, 0)  # pilares verticais: eixo local z global x
    ops.uniaxialMaterial("Elastic", 9, E)
    ops.uniaxialMaterial("Elastic", 10, 200e6)  # aço do contraventamento e das escoras metálicas
    pil = []   # (nome, x, y, b_x, b_y, z_lista)

    def pilar(nome, x, y, bx, by, ztop, zs_extra=()):
        zs = sorted(set([0.0, 2.5, 5.0, 7.5, ztop] + list(zs_extra)))
        zs = [z for z in zs if z <= ztop + 1e-9]
        ns = [no(x, y, z) for z in zs]
        ops.fix(ns[0], 1, 1, 1, 1, 1, 1)
        A, Iy, Iz = bx * by, by * bx ** 3 / 12, bx * by ** 3 / 12   # Iy: flexão no plano xz
        J = 0.2 * min(bx, by) ** 3 * max(bx, by)
        for a, b in zip(ns[:-1], ns[1:]):
            ops.element("elasticBeamColumn", len(pil) * 100 + ns.index(a) + 1, a, b, A, E, G, J, Iy, Iz, 1)  # ordem OpenSees 3D: Iy, Iz
        pil.append((nome, x, y, bx, by, zs, ns))
        return ns

    # pilares laterais (60 na direção x), fachadas e centrais
    for i, y in enumerate(YL):
        pilar(f"P1@L{i}", 0.0, y, 0.60, 0.40, Z_TOP, (Z_P1,) + (tuple(Z_MEZ) if i <= 1 else ()))
        pilar(f"P2@L{i}", 40.10, y, 0.60, 0.40, Z_TOP, (Z_P2,) + (tuple(Z_MEZ) if i <= 1 else ()))
    for i in (0, 8):
        for x in XF[1:4]:
            pilar(f"F{x:g}@L{i}", x, YL[i], 0.40, 0.60, Z_TOP, (Z_CEN,) + (tuple(Z_MEZ) if i == 0 else ()))
    for x in (9.87, 29.63):  # pilares do mezanino na L1 (P8, P8B)
        pilar(f"M{x:g}@L1", x, YL[1], 0.60, 0.40, Z_MEZ[1], tuple(Z_MEZ))
    pilar("P8A", X_CEN, YL[1], 0.60, 0.40, Z_CEN, tuple(Z_MEZ))
    pilar("P11", X_CEN, YL[3], 0.50, 0.50, Z_CEN)
    y13 = YL[5] + 4.6
    pilar("P13", X_CEN, YL[5] + 4.6, 0.50, 0.50, Z_CEN)

    # nós soltos (só treliça): travar z e rotações
    def no_trelica(x, y, z):
        n = no(x, y, z)
        if n not in [m for p in pil for m in p[6]]:
            try:
                ops.fix(n, 0, 0, 1, 1, 1, 1)
            except Exception:
                pass
        return n

    tr = [0]
    trelicas = []

    def barra(n1, n2, A, nome):
        tr[0] += 1
        mat = 10 if nome in ("contravento", "escora beiral", "terça escora") else 9
        ops.element("Truss", 50000 + tr[0], n1, n2, A, mat)
        trelicas.append((50000 + tr[0], nome))

    # ---------------- cobertura: vigas (cordas), terças-escora e contraventamento em painéis curtos
    def z_viga(x):
        return Z_P1 + (Z_CEN - Z_P1) * x / X_CEN if x <= X_CEN else Z_CEN + (Z_P2 - Z_CEN) * (x - X_CEN) / (40.1 - X_CEN)
    XP = sorted(set([round(X_CEN * k / N_PAINEL, 3) for k in range(N_PAINEL + 1)] +
                    [round(X_CEN + (40.1 - X_CEN) * k / N_PAINEL, 3) for k in range(1, N_PAINEL + 1)]))
    XFAC = [0.0, 9.87, 20.05, 29.63, 40.1]
    def xs_vao(ia, ib):
        return XFAC if 0 in (ia, ib) or 8 in (ia, ib) else XP
    xs_linha = {i: set([0.0, X_CEN, 40.1]) for i in range(9)}
    for ia, ib in VAOS_CONTRAV:
        for i in (ia, ib):
            xs_linha[i] |= set(xs_vao(ia, ib))
    def no_cob(x, i):
        if i in (0, 8) and x in XFAC:
            return nos[(round(x, 3), round(YL[i], 3), Z_P1 if x == 0 else (Z_P2 if x == 40.1 else Z_CEN))]
        if x == 0.0:
            return nos[(0.0, round(YL[i], 3), Z_P1)]
        if x == 40.1:
            return nos[(40.1, round(YL[i], 3), Z_P2)]
        k = (round(x, 3), round(YL[i], 3), round(z_viga(x), 3))
        if x == X_CEN and k in nos:
            return nos[k]
        return nos[k] if k in nos else no_trelica(x, YL[i], z_viga(x))
    for i in range(9):
        xs = sorted(xs_linha[i])
        ns = [no_cob(x, i) for x in xs]
        nome = "VB fachada" if i in (0, 8) else "I90"
        for x_a, x_b, a_, b_ in zip(xs[:-1], xs[1:], ns[:-1], ns[1:]):
            if i not in (0, 8) and x_a < X_CEN < x_b:
                continue
            barra(a_, b_, 0.15 * 0.70 if i in (0, 8) else I90_A, f"{nome} L{i}")
    for ia, ib in VAOS_CONTRAV:
        xs = xs_vao(ia, ib)
        A_ = [no_cob(x, ia) for x in xs]; B_ = [no_cob(x, ib) for x in xs]
        for j in range(len(xs)):
            barra(A_[j], B_[j], 15.2e-4, "terça escora")
        for j in range(len(xs) - 1):
            barra(A_[j], B_[j + 1], A_BARRA, "contravento")
            barra(B_[j], A_[j + 1], A_BARRA, "contravento")
    # viga central I110 (articulada) entre apoios centrais
    y13 = YL[5] + 4.6
    pts = sorted([(y, nos[(X_CEN, round(y, 3), Z_CEN)]) for y in YL[1:8] + [y13]])
    for (ya, a_), (yb, b_) in zip(pts[:-1], pts[1:]):
        barra(a_, b_, 0.3025, "I110 central")
    # escoras de beiral (terça de beiral) nas linhas laterais
    for xx, zz in ((0.0, Z_P1), (40.1, Z_P2)):
        ns = [nos[(xx, round(y, 3), zz)] for y in YL]
        for a_, b_ in zip(ns[:-1], ns[1:]):
            barra(a_, b_, 15.2e-4, "escora beiral")
    # mezanino: vigas I90 + laje como diafragma (treliças em X) entre L0 e L1
    for z in Z_MEZ:
        l0 = [nos[(round(x, 3), 0.0, z)] for x in XF]
        l1 = [nos[(round(x, 3), round(YL[1], 3), z)] for x in (0.0, 9.87, 20.05, 29.63, 40.1)]
        for row in (l0, l1):
            for a, b in zip(row[:-1], row[1:]):
                barra(a, b, I90_A, "I90 mezanino")
        escravos = l0 + l1
        mestre = no(20.05, YL[1] / 2, z)
        ops.fix(mestre, 0, 0, 1, 1, 1, 0)
        ops.rigidDiaphragm(3, mestre, *escravos)   # laje alveolar + capa = diafragma rígido
    return pil, trelicas


def cargas(pil, wx=0.0, wy=0.0, grav=1.0):
    """wx, wy: multiplicador do vento característico nas direções x e y."""
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    for nome, x, y, bx, by, zs, ns in pil:
        iy = min(range(9), key=lambda i: abs(YL[i] - y))
        lateral = nome.startswith("P1") or nome.startswith("P2")
        fachada = nome.startswith("F") or ((nome.startswith("P1") or nome.startswith("P2")) and iy in (0, 8))
        # gravidade: viga I90 no apoio + placas + peso próprio do pilar
        N = 0.0
        if lateral and 0 < iy < 8:
            N += Rg_I
        if nome in ("P8A", "P11", "P13"):
            N += 2 * Rg_I + 300.0
        pp = bx * by * 25 * zs[-1]
        ops.load(ns[-1], 0, 0, -grav * (N + pp), 0, 0, 0)
        # placas penduradas na face externa (peso + momento da excentricidade), distribuídas na altura
        if lateral or fachada:
            larg = TRIB_Y[iy] if lateral else TRIB_X[min(range(5), key=lambda k: abs(XF[k] - x))]
            Wn = W_placa_m * larg / (len(ns) - 1)
            for n in ns[1:]:
                sx = -1 if x < 1 else (1 if x > 39 else 0)
                sy = -1 if iy == 0 else (1 if iy == 8 else 0)
                ops.load(n, 0, 0, -grav * Wn, grav * Wn * E_PLACA * sy, -grav * Wn * E_PLACA * sx, 0)
        # vento (forças nodais pela área de influência na altura)
        for k, n in enumerate(ns[1:], 1):
            dz = (zs[k] - zs[k - 1]) / 2 + ((zs[k + 1] - zs[k]) / 2 if k + 1 < len(zs) else 0)
            if wx and lateral:
                cp = 0.7 if x < 1 else 0.5
                ops.load(n, wx * cp * qv * TRIB_Y[iy] * dz, 0, 0, 0, 0, 0)
            if wy and (fachada or (lateral and iy in (0, 8))):
                cp = 0.7 if iy == 0 else 0.5
                larg = TRIB_X[min(range(5), key=lambda k2: abs(XF[k2] - x))]
                ops.load(n, 0, wy * cp * qv * larg * dz, 0, 0, 0, 0)


def rodar(wx, wy, pdelta):
    pil, tre = montar(pdelta)
    cargas(pil, wx, wy)
    ops.system("UmfPack"); ops.numberer("RCM"); ops.constraints("Transformation")
    ops.test("NormDispIncr", 1e-8, 30); ops.algorithm("Newton")
    ops.integrator("LoadControl", 0.1); ops.analysis("Static")
    ok = ops.analyze(10)
    topo = {p[0]: (ops.nodeDisp(p[6][-1], 1) * 1000, ops.nodeDisp(p[6][-1], 2) * 1000) for p in pil}
    forcas = {}
    for t, nome in tre:
        f = ops.basicForce(t)[0]
        forcas[nome] = max(forcas.get(nome, 0.0), abs(f))
    return ok, pil, topo, forcas


res = {}
for caso, (wx, wy) in {"vento_x_freq": (0.3, 0), "vento_y_freq": (0, 0.3), "vento_x_k": (1, 0), "vento_y_k": (0, 1), "so_gravidade": (0, 0)}.items():
    ok2, pil, t2, f2 = rodar(wx, wy, True)
    ok1, _, t1, _ = rodar(wx, wy, False)
    dir_ = 0 if wx else 1
    dmax2 = max(abs(v[dir_]) for v in t2.values())
    dmax1 = max(abs(v[dir_]) for v in t1.values())
    crit = max(t2, key=lambda k: abs(t2[k][dir_]))
    res[caso] = dict(convergiu=ok2 == 0, desl_max_mm=round(dmax2, 1), pilar=crit,
                     razao_2a_1a=round(dmax2 / dmax1, 3) if dmax1 > 0.05 else None,
                     forca_max_kN={k: round(v, 1) for k, v in f2.items()})
    print(caso, res[caso]["desl_max_mm"], "mm em", crit, "| 2ª/1ª:", res[caso]["razao_2a_1a"])

# figura: modelo e deformada (vento x frequente, escala ampliada)
import opsvis as opsv
rodar(0.3, 0, True)
fig = plt.figure(figsize=(11, 7))
opsv.plot_defo(sfac=300, fmt_defo={"color": "#c0392b", "linewidth": 1.4}, fmt_undefo={"color": "#9a9a9a", "linewidth": .6},
               az_el=(-55, 25), node_supports=False)
ax = plt.gca()
ax.set_title("Letsara — modelo global 3D · deformada com vento transversal frequente (×300)", fontsize=10)
plt.figtext(0.99, 0.01, "projeto da ND Engenharia", ha="right", fontsize=7, color="gray")
plt.savefig(AQUI / "modelo_global_vento_x.png", dpi=140, bbox_inches="tight")
rodar(0, 0.3, True)
fig = plt.figure(figsize=(11, 7))
opsv.plot_defo(sfac=300, fmt_defo={"color": "#1f5fa8", "linewidth": 1.4}, fmt_undefo={"color": "#9a9a9a", "linewidth": .6},
               az_el=(-55, 25), node_supports=False)
plt.gca().set_title("Letsara — modelo global 3D · deformada com vento longitudinal frequente (×300)", fontsize=10)
plt.figtext(0.99, 0.01, "projeto da ND Engenharia", ha="right", fontsize=7, color="gray")
plt.savefig(AQUI / "modelo_global_vento_y.png", dpi=140, bbox_inches="tight")
(AQUI / "modelo_global.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
