"""MEF não linear 2D (estado plano de tensões) da extremidade de viga protendida com dente Gerber — OpenSeesPy.

Modelo: trecho de viga de comprimento Ls a partir da ponta, apoiado no dente (aparelho de apoio) e na outra ponta,
com carga concentrada no topo em xP (momento cresce linearmente a partir do apoio, como na viga real, a favor da
segurança). Concreto: ASDConcrete3D em estado plano (dano à tração e à compressão, fissuração distribuída, integração IMPL-EX).
Armaduras passivas e cordoalhas: barras de treliça com aderência perfeita; cordoalhas com deformação inicial
(InitStrainMaterial) crescendo linearmente no comprimento de transferência a partir da face onde são cortadas.
Resistências de cálculo (fcd, fctd, fyd, fpyd): a força última do modelo é comparada direto com Vd.
Unidades: N, mm, MPa.
"""
from __future__ import annotations
import math
import numpy as np


def _asd_concreto(ops, tag, Ec, fc, ft, lch, Gf=0.15):
    """ASDConcrete3D (dano, IMPL-EX). Tração: linear até ft e amolecimento linear curto (até 10 εt0, sem contar
    enrijecimento à tração além disso — com a energia de fratura distribuída em malha de 25 mm o modelo superestimava a
    resistência à flexão em ~20%); compressão: parábola até fc (2‰), queda até 0,2 fc em 3,5‰ e patamar."""
    et0 = ft / Ec
    etu = 10 * et0             # amolecimento curto (a favor da segurança no ELU; ver validação em tests/)
    Te = [0.0, et0, etu, 10 * etu]
    Ts = [0.0, ft, 0.02 * ft, 0.02 * ft]
    ec1 = 0.002
    Ce = [0.0]
    Cs = [0.0]
    for e in np.linspace(0.0002, ec1, 8):
        Ce.append(e)
        Cs.append(min(fc * (1 - (1 - e / ec1) ** 2), Ec * e))
    Ce += [0.0035, 0.01]
    Cs += [0.2 * fc, 0.2 * fc]
    dam = lambda e, s_: 0.0 if e == 0 else max(0.0, min(0.99, 1 - s_ / (Ec * e)))
    Td = [dam(e, s_) for e, s_ in zip(Te, Ts)]
    Cd = [dam(e, s_) for e, s_ in zip(Ce, Cs)]
    ops.nDMaterial("ASDConcrete3D", tag, Ec, 0.2, "-Te", *Te, "-Ts", *Ts, "-Td", *Td,
                   "-Ce", *Ce, "-Cs", *Cs, "-Cd", *Cd, "-implex")


def _espessura(x, y, g):
    """Largura da seção na posição (x, y)."""
    if x <= g["x_mac"]:
        return g["b"]
    ti, mi, ts, ms, H, b, bw = g["ti"], g["mi"], g["ts"], g["ms"], g["H"], g["b"], g["bw"]
    bi = g.get("bi", b)                      # mesa inferior (meio vaso / T: bi = bw)
    if y <= ti:
        return bi
    if y <= ti + mi:
        return bi - (bi - bw) * (y - ti) / mi
    if y <= H - ts - ms:
        return bw
    if y <= H - ts:
        return bw + (b - bw) * (y - (H - ts - ms)) / ms
    return b


def analisar(g, arm, cord, Vd, Hd, fck=50.0, malha=25.0, Ls=3000.0, xP=2000.0, passos=400, sig_pe=1150.0, du=0.05, rampa_fim=False, robusto=False,
             lt=760.0, saida_png=None, titulo=""):
    """g: geometria (H, b, bw, ti, mi, ts, ms, hd, ln, a_apoio, x_mac, l_apoio).
    arm: lista de barras dict(tipo='h'|'v', pos (y para 'h', x para 'v'), ini, fim, area_total mm²).
    cord: lista de dict(y, n) — n cordoalhas Ø12,7 na altura y."""
    import openseespy.opensees as ops
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 2)
    H, hd, ln = g["H"], g["hd"], g["ln"]
    y_dente = H - hd
    nx, ny = int(round(Ls / malha)), int(round(H / malha))
    xs, ys = np.linspace(0, Ls, nx + 1), np.linspace(0, H, ny + 1)
    tag = {}
    k = 0
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            if x < ln - 1e-6 and y < y_dente - 1e-6:
                continue                                      # recorte do dente (abaixo do dente, antes da face reentrante)
            k += 1
            ops.node(k, float(x), float(y))
            tag[(i, j)] = k
    fcd, fctd = 0.85 * fck / 1.4, 0.7 * 0.3 * fck ** (2 / 3) / 1.4
    Ec = 0.85 * 5600 * math.sqrt(fck)
    _asd_concreto(ops, 10, Ec, fcd, fctd, malha)
    ops.nDMaterial("PlaneStress", 1, 10)
    e = 0
    elem_c = []
    for i in range(nx):
        for j in range(ny):
            ns = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            if all(n in tag for n in ns):
                xc, yc = (xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2
                if xc < ln and yc < y_dente:
                    continue
                e += 1
                ops.element("quad", e, *[tag[n] for n in ns], _espessura(xc, yc, g), "PlaneStress", 1)
                elem_c.append((e, xc, yc))
    # aço passivo e cordoalhas
    ops.uniaxialMaterial("Steel02", 2, 500 / 1.15, 200000.0, 0.001, 18, 0.925, 0.15)
    ops.uniaxialMaterial("Steel02", 3, 0.9 * 1900 / 1.15, 195000.0, 0.001, 18, 0.925, 0.15)
    eps_pe = sig_pe / 195000.0
    mt = [100]

    def no_mais_proximo(x, y):
        i, j = int(round(x / malha)), int(round(y / malha))
        return tag.get((i, j))

    barras = []
    for b_ in arm:
        if b_["tipo"] == "h":
            j = int(round(b_["pos"] / malha))
            ii = range(int(round(b_["ini"] / malha)), int(round(b_["fim"] / malha)))
            pares = [((i, j), (i + 1, j)) for i in ii]
        else:
            i = int(round(b_["pos"] / malha))
            jj = range(int(round(b_["ini"] / malha)), int(round(b_["fim"] / malha)))
            pares = [((i, j), (i, j + 1)) for j in jj]
        for a, c in pares:
            if a in tag and c in tag:
                e += 1
                ops.element("Truss", e, tag[a], tag[c], b_["area_total"], 2)
                barras.append((e, b_.get("nome", ""), b_["tipo"]))
    for c in cord:
        j = int(round(c["y"] / malha))
        x0 = (ln if c["y"] < y_dente else 0.0) + c.get("isol", 0.0)   # cortada na face do dente; isolada (bainha) no trecho "isol"
        for i in range(int(round(x0 / malha)), nx):
            a, b2 = (i, j), (i + 1, j)
            if a in tag and b2 in tag:
                xm = (xs[i] + xs[i + 1]) / 2
                f = min(1.0, (xm - x0) / lt)
                if rampa_fim:                                  # corte artificial do modelo: transferência gradual também no fim
                    f = min(f, (Ls - xm) / lt)
                mt[0] += 1
                ops.uniaxialMaterial("InitStrainMaterial", mt[0], 3, f * eps_pe)
                e += 1
                ops.element("Truss", e, tag[a], tag[b2], c["n"] * 98.7, mt[0])
                barras.append((e, "cordoalha", "p"))
    # apoios: aparelho de apoio no dente (vertical em l_apoio) e apoio do outro lado (vertical + horizontal)
    # apoios: placa de aço (20 mm, quads elásticos) sob a área de apoio, com UM nó de apoio no centro da placa —
    # evita a restrição à rotação que surge ao fixar vários nós em linha
    ops.nDMaterial("ElasticIsotropic", 50, 200000.0, 0.3)

    def placa(cx, yb, larg):
        nonlocal k, e
        i0, i1 = int(round((cx - larg / 2) / malha)), int(round((cx + larg / 2) / malha))
        sup, inf = [], []
        for i in range(i0, i1 + 1):
            if (i, int(round(yb / malha))) not in tag:
                continue
            k += 1
            ops.node(k, float(xs[i]), float(yb - 20.0))
            inf.append((i, k))
            sup.append(tag[(i, int(round(yb / malha)))])
        for m in range(len(inf) - 1):
            e += 1
            ops.element("quad", e, inf[m][1], inf[m + 1][1], sup[m + 1], sup[m], g["b"], "PlaneStress", 50)
        meio = inf[len(inf) // 2][1]
        return meio, sup

    no_ap, ap = placa(g["a_apoio"], y_dente, g["l_apoio"])
    ops.fix(no_ap, 0, 1)
    no_ap2, _ = placa(Ls - 100, 0.0, 150)
    ops.fix(no_ap2, 1, 1)
    # etapa 1: protensão (forças internas das cordoalhas)
    ops.timeSeries("Constant", 1)
    ops.pattern("Plain", 1, 1)
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("UmfPack")
    ops.test("NormUnbalance", 1.0, 200)                     # equilíbrio de verdade (resíduo < 1 N)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 0.0)
    ops.analysis("Static")
    ok0 = ops.analyze(5)
    ops.reactions()
    R0 = ops.nodeReaction(no_ap, 2)                          # reação residual da protensão (deveria ser ~0)
    ops.loadConst("-time", 0.0)
    # etapa 2: carga P no topo (placa de 200 mm) + Hd proporcional no apoio do dente
    ops.timeSeries("Linear", 2)
    ops.pattern("Plain", 2, 2)
    topo = [tag[(i, ny)] for i in range(nx + 1) if abs(xs[i] - xP) <= 100 + 1e-6]
    for n in topo:
        ops.load(n, 0.0, -1.0 / len(topo))
    fator_V = (Ls - 100 - xP) / (Ls - 100 - g["a_apoio"])     # V no dente ≈ fator_V · P (só para a força horizontal)
    ops.load(no_ap, -Hd / Vd * fator_V, 0.0)                  # tração horizontal no apoio (para fora da peça)
    ctrl = topo[len(topo) // 2]
    ops.integrator("DisplacementControl", ctrl, 2, -du)
    ops.test("NormDispIncr", 1e-5, 60)
    ops.algorithm("KrylovNewton")
    hist = []
    snap_d = None
    lim = None
    # elementos monitorados para o critério de deformação (fora das placas de carga e de apoio)
    perto = lambda xc, yc: (abs(xc - xP) < 200 and yc > H - 200) or (abs(xc - g["a_apoio"]) < 200 and abs(yc - y_dente) < 200) \
        or ((xc > Ls - lt - 100 and yc < 300) if rampa_fim else (xc > Ls - 300 and yc < 200))
    mon_c = [e_ for e_, xc, yc in elem_c if not perto(xc, yc)]
    mon_s = [e_ for e_, nome, tipo in barras if tipo != "p"]
    eps_ini = {e_: ops.basicDeformation(e_)[0] / malha for e_, nome, tipo in barras if tipo == "p"}
    mon_p = list(eps_ini)
    for p in range(passos):
        r = ops.analyze(1)
        if r != 0:                                             # subpassos adaptativos
            for div in (2, 4, 8, 16, 32):
                ops.integrator("DisplacementControl", ctrl, 2, -du / div)
                ok_sub = all(ops.analyze(1) == 0 for _ in range(div))
                if ok_sub:
                    r = 0
                    break
            if r != 0 and robusto:                          # último recurso: Newton modificado / line search, tolerância 1e-4
                for alg in (("ModifiedNewton", "-initial"), ("NewtonLineSearch",)):
                    ops.algorithm(*alg); ops.test("NormDispIncr", 1e-4, 300)
                    ops.integrator("DisplacementControl", ctrl, 2, -du / 10)
                    if all(ops.analyze(1) == 0 for _ in range(10)):
                        r = 0
                    ops.algorithm("KrylovNewton"); ops.test("NormDispIncr", 1e-5, 60)
                    if r == 0:
                        break
            ops.integrator("DisplacementControl", ctrl, 2, -du)
            if r != 0:
                break
        ops.reactions()
        V = (ops.nodeReaction(no_ap, 2) - R0) / 1e3
        hist.append((-ops.nodeDisp(ctrl, 2), V))
        if lim is None:
            es = max(ops.basicDeformation(e_)[0] / malha for e_ in mon_s) if mon_s else 0.0
            ep = max((ops.basicDeformation(e_)[0] / malha - eps_ini[e_]) for e_ in mon_p) if mon_p else 0.0
            ec, e_min = 0.0, None
            for e_ in mon_c:
                st = ops.eleResponse(e_, "material", 1, "strain")
                a_, b_, c_ = st[0], st[1], st[2]
                ev = (a_ + b_) / 2 - math.sqrt(((a_ - b_) / 2) ** 2 + (c_ / 2) ** 2)
                if ev < ec:
                    ec, e_min = ev, e_
            if es >= 0.010 or ep >= 0.010 or ec <= -0.0035:
                lim = dict(V=V, aco=round(es * 1000, 2), cordoalha=round(ep * 1000, 2), concreto=round(ec * 1000, 2),
                           criterio="aço 10‰" if es >= 0.010 else ("cordoalha +10‰" if ep >= 0.010 else "concreto 3,5‰"),
                           xy_concreto_mm=next(((round(xc), round(yc)) for e_, xc, yc in elem_c if e_ == e_min), None))
        if snap_d is None and V >= Vd:
            snap_d = _estado(ops, elem_c, barras)
        if len(hist) > 30 and V < 0.80 * max(h[1] for h in hist):
            break
    Vpico = max(h[1] for h in hist) if hist else 0.0
    Vu = min(Vpico, lim["V"]) if lim else Vpico
    snap_u = _estado(ops, elem_c, barras)
    res = dict(Vu_kN=round(Vu, 1), V_pico_kN=round(Vpico, 1), limite=lim, Vd_kN=Vd, FS=round(Vu / Vd, 2), ok=Vu >= Vd,
               protensao_ok=ok0 == 0, reacao_residual_protensao_kN=round(R0 / 1e3, 2),
               n_elem=len(elem_c), curva=[(round(a, 3), round(b, 1)) for a, b in hist[::max(1, len(hist) // 60)]],
               aco_suspensao_em_Vd_MPa=None if snap_d is None else snap_d["max_tensao"].get("suspensao"),
               aco_tirante_em_Vd_MPa=None if snap_d is None else snap_d["max_tensao"].get("tirante"))
    if saida_png:
        _figura(saida_png, g, elem_c, snap_d, snap_u, hist, res, titulo, malha, Ls)
    ops.wipe()
    return res


def _estado(ops, elem_c, barras):
    eps1 = {}
    for e, xc, yc in elem_c:
        try:
            s = ops.eleResponse(e, "material", 1, "strain")
            ex, ey, gxy = s[0], s[1], s[2]
            eps1[e] = (ex + ey) / 2 + math.sqrt(((ex - ey) / 2) ** 2 + (gxy / 2) ** 2)
        except Exception:
            eps1[e] = 0.0
    tens = {}
    for e, nome, tipo in barras:
        try:
            f = ops.eleResponse(e, "axialForce")[0]
            A = ops.eleResponse(e, "material", "stress")
        except Exception:
            f = 0.0
        try:
            st = ops.eleResponse(e, "material", "stress")[0]
        except Exception:
            st = 0.0
        if nome:
            tens[nome] = max(tens.get(nome, 0.0), st)
    return dict(eps1=eps1, max_tensao={k: round(v, 0) for k, v in tens.items()})


def _figura(caminho, g, elem_c, snap_d, snap_u, hist, res, titulo, malha, Ls):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    from matplotlib.collections import PatchCollection
    fig = plt.figure(figsize=(14, 9.5), dpi=130)
    for k, (snap, nome) in enumerate(((snap_d, f"em Vd = {res['Vd_kN']:.0f} kN"), (snap_u, f"na ruptura, Vu = {res['Vu_kN']:.0f} kN"))):
        ax = fig.add_axes([0.04, 0.70 - 0.32 * k, 0.86, 0.27])
        if snap is None:
            ax.axis("off")
            continue
        pats, cores = [], []
        for e, xc, yc in elem_c:
            pats.append(Rectangle((xc - malha / 2, yc - malha / 2), malha, malha))
            cores.append(snap["eps1"].get(e, 0.0) * 1000)
        pc = PatchCollection(pats, cmap="inferno_r", edgecolor="none")
        pc.set_array(np.clip(np.array(cores), 0, 3.0))
        pc.set_clim(0, 3.0)
        ax.add_collection(pc)
        ax.set_xlim(-50, Ls + 50)
        ax.set_ylim(-50, g["H"] + 50)
        ax.set_aspect("equal")
        ax.set_anchor("W")
        ax.set_title(f"{titulo} — deformação principal de tração (‰) {nome}", fontsize=10)
        ax.set_xticks([])
        ax.set_yticks([])
        fig.colorbar(pc, ax=ax, fraction=0.015, pad=0.01, label="ε1 (‰) — fissuração acima de ≈ 0,1‰")
    ax = fig.add_axes([0.07, 0.06, 0.88, 0.26])
    d, v = zip(*hist) if hist else ([0], [0])
    ax.plot(d, v, color="#c0392b", lw=1.8, label="força no dente (MEF)")
    ax.axhline(res["Vd_kN"], color="#2c3e50", ls="--", label=f"Vd = {res['Vd_kN']:.0f} kN")
    ax.set_xlabel("deslocamento do ponto de carga (mm)")
    ax.set_ylabel("V no dente (kN)")
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(alpha=0.3)
    ax.set_title(f"Curva força × deslocamento — Vu/Vd = {res['FS']:.2f} (resistências de cálculo)", fontsize=10)
    fig.text(0.99, 0.005, "projeto da ND Engenharia", ha="right", fontsize=9, color="gray")
    fig.savefig(caminho)
    plt.close(fig)
