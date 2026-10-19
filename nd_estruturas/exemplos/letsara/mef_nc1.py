"""Letsara rev06d — elementos finitos do nicho NC-1 (casca ShellMITC4) apoiado no concreto da placa. Gera mef_nc1.json.

Eixos do nicho (mm): x a partir da ponta da placa (0–120), y a partir da boca (face interna da placa, 0–60), z a partir da
face de baixo (0–200). Chapas no plano médio, nós comuns nas soldas:
  teto     z = H − t_teto/2, x 0–120, y 0 até o plano do fundo;     base   z = t_base/2 (idem);
  fundo    y = P − t_fundo/2, z entre base e teto;                  parede x = B − t_parede/2 (lado de dentro da placa);
  abas     y = t_aba/2, z da borda de baixo da aba ao teto, x 0–39 e 81–117.
Concreto: molas só de compressão (ENT) na face de cima do teto, de baixo da base e de fora da parede (k = Ec·A/h0, h0 = 50 mm).
Atrás do fundo há só 40 mm de concreto (não verifica à punção, 10,9 < 13,8 kN): o fundo não se apoia nele (a favor da segurança).
A ponta (x = 0) e a boca (y = 0) são abertas. Grampos U Ø6,3 (4, dentro dos estribos N5/N6): molas axiais (z) e de pino (x, y).
Cargas de cálculo de um console (fixacao_placas.json): Vd no anel da cabeça do M16 de nível sob o teto (+z); vento Fd na
ponta do prisioneiro no fundo (sobrepressão, +y) ou nas 2 abas no contato com os dentes (sucção, −y, face do dente de 13 mm nos 10 mm de baixo da aba).
Soldas: esforços da casca na borda de cada junta → 2 filetes (NBR 8800:2008 6.2.5.1), a por junta em A_SOLDA; força por mm = maior\nmédia em 10 mm de cordão (o pico do canto reentrante da casca elástica depende da malha).\nCritério: von Mises nas faces (EN 1993-1-1:2005 6.2.1(5)) ≤ fy/γa1 (γa1 = 1,10, NBR 8800:2008); percentil 99 por chapa.
Uso: python mef_nc1.py [t_teto t_base t_fundo t_parede t_aba]  (sem argumentos: espessuras do GEO).
"""
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import openseespy.opensees as ops

AQ = Path(__file__).parent
FX = json.loads(Path(os.environ.get("CS1_FX", AQ / "fixacao_placas.json")).read_text(encoding="utf-8"))
N = dict(FX["GEO"]["NC1"])
C = FX["GEO"]["CS1"]
TOL = FX["GEO"]["tol"]
CG = FX["cargas_por_console"]
ES, NU, GA1 = 200000.0, 0.3, 1.10
FY = {"teto": 345.0, "base": 345.0, "fundo": 345.0, "abas": 345.0, "parede": 250.0}
EC = 0.85 * 5600 * math.sqrt(40.0)            # MPa (C40)
H0 = 50.0
Vd, Fd = CG["Vd_kN"] * 1e3, CG["vento_d_kN"] * 1e3
K_PINO, K_AX = 5.0e3, 31.2 * ES / 100.0       # N/mm: grampo como pino no concreto e axial (perna de 100 mm)
FW, GW2 = 485.0, 1.35                          # metal de solda E70 / ER70S-6; NBR 8800:2008 6.2.5.1 (γw2)
# filetes de oficina (garganta 0,707 a), dos dois lados de cada junta; a ≤ espessura da chapa mais fina
A_SOLDA = {k: N.get("a_solda", {}).get(k, v) for k, v in dict(teto_fundo=5.0, base_fundo=3.0, parede=2.0).items()}   # 5 = mínimo AWS D1.1 p/ 9,5; 2 na chapa de 2 (AWS D1.3)


def solda_por_mm(a):
    """Resistência de cálculo de um filete por mm de cordão (NBR 8800:2008 6.2.5.1: 0,6·fw·Aw/γw2)."""
    return 0.6 * FW * 0.707 * a / GW2


def grade(pts, h):
    out = [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        n = max(1, math.ceil((b - a) / h - 1e-9))
        out += [a + (b - a) * k / n for k in range(1, n + 1)]
    return sorted(set(round(v, 4) for v in out))


def analisar(T, caso, h=4.0):
    B, Hh, P = N["B"], N["H"], N["P"]
    tt, tb, tf, tp, ta = T["teto"], T["base"], T["fundo"], T["parede"], T["abas"]
    zt, zb, yf, xp, ya = Hh - tt / 2, tb / 2, P - tf / 2, B - tp / 2, ta / 2
    za0 = Hh - tt - N["h_aba"]                                 # borda de baixo das abas
    AE, AD = N["aba_e"], N["aba_d"]
    # posições de carga (console na posição nominal: x_NC = 60, y_NC = y_CS − a, z_NC = z_CS + (H − t_teto) − G)
    xc = B / 2
    y_niv = C["y_nivel"] - TOL["a"]
    z_fr = C["z_frontal"] + (Hh - tt) - TOL["G"]
    de = C["dente"]
    XG = sorted(v for par in N["x_gr"] for v in par)                # pernas dos grampos
    X = grade(sorted(set([0, AE[0], *XG, xc - de["x0"] - de["b"], xc - de["x0"], AE[1], xc - 12, xc, xc + 12, AD[0], xc + de["x0"], xc + de["x0"] + de["b"], AD[1], xp])), h)
    Y = grade([0, ya, y_niv - 12, y_niv, y_niv + 12, N["y_gr"], yf], h)
    Z = grade([zb, za0, za0 + 5, za0 + 10, z_fr - 12, z_fr, z_fr + 12, zt], h)
    nos, E = {}, []

    def no(x, y, z):
        k = (round(x, 4), round(y, 4), round(z, 4))
        if k not in nos:
            nos[k] = len(nos) + 1
        return nos[k]

    def quad(a, b, c, d, t, parte):
        E.append(([no(*a), no(*b), no(*c), no(*d)], t, parte))
    for i in range(len(X) - 1):
        for j in range(len(Y) - 1):
            quad((X[i], Y[j], zt), (X[i + 1], Y[j], zt), (X[i + 1], Y[j + 1], zt), (X[i], Y[j + 1], zt), tt, "teto")
            quad((X[i], Y[j], zb), (X[i + 1], Y[j], zb), (X[i + 1], Y[j + 1], zb), (X[i], Y[j + 1], zb), tb, "base")
        for k in range(len(Z) - 1):
            quad((X[i], yf, Z[k]), (X[i + 1], yf, Z[k]), (X[i + 1], yf, Z[k + 1]), (X[i], yf, Z[k + 1]), tf, "fundo")
    for j in range(len(Y) - 1):
        for k in range(len(Z) - 1):
            quad((xp, Y[j], Z[k]), (xp, Y[j + 1], Z[k]), (xp, Y[j + 1], Z[k + 1]), (xp, Y[j], Z[k + 1]), tp, "parede")
    ZA = [z for z in Z if z >= za0 - 1e-9]
    for (x0, x1) in (AE, AD):
        XA = [x for x in X if x0 - 1e-9 <= x <= min(x1, xp) + 1e-9]
        for i in range(len(XA) - 1):
            for k in range(len(ZA) - 1):
                quad((XA[i], ya, ZA[k]), (XA[i + 1], ya, ZA[k]), (XA[i + 1], ya, ZA[k + 1]), (XA[i], ya, ZA[k + 1]), ta, "abas")
    # abas ligadas ao teto: a linha de topo da aba (z = zt) fica no plano do teto (nós comuns em y = ya)
    ops.wipe(); ops.model("basic", "-ndm", 3, "-ndf", 6)
    for (x, y, z), n in nos.items():
        ops.node(n, x, y, z)
    secs = {}
    for k, (ns, t, p) in enumerate(E):
        if t not in secs:
            secs[t] = len(secs) + 1
            ops.section("ElasticMembranePlateSection", secs[t], ES, NU, t, 0.0)
        ops.element("ShellMITC4", k + 1, *ns, secs[t])
    ops.uniaxialMaterial("ENT", 1, 1.0)                        # mola unitária só de compressão (escala pela área em cada mola)
    tag_g = [10 ** 7]

    def mola(n, dirn, k, so_compressao=True, sinal=1):
        tag_g[0] += 1
        g = tag_g[0]
        x, y, z = ops.nodeCoord(n)
        ops.node(g, x, y, z); ops.fix(g, 1, 1, 1, 1, 1, 1)
        mt = tag_g[0] + 10 ** 6
        if so_compressao:
            ops.uniaxialMaterial("ENT", mt, k)
        else:
            ops.uniaxialMaterial("Elastic", mt, k)
        # ENT resiste a compressão: alongamento negativo do elemento (nó → terra). sinal = +1 quando o concreto está do lado + do eixo
        i_, j_ = (n, g) if sinal < 0 else (g, n)              # deformação = u_j − u_i: com o concreto do lado +, inverte a ordem
        ops.element("zeroLength", 2 * 10 ** 7 + g, i_, j_, "-mat", mt, "-dir", dirn)
        return 2 * 10 ** 7 + g
    trib = {}
    for ns, t, p in E:
        pts = np.array([ops.nodeCoord(n) for n in ns])
        a = np.linalg.norm(np.cross(pts[1] - pts[0], pts[3] - pts[0]))
        for n in ns:
            trib.setdefault((p, n), 0.0)
            trib[(p, n)] += a / 4
    molas = []
    for (p, n), a in trib.items():
        k = EC * a / H0
        if p == "teto":
            molas.append(mola(n, 3, k, True, -1))              # concreto acima: o teto o comprime subindo (+z) — mola com eixo invertido
        elif p == "base":
            molas.append(mola(n, 3, k, True, +1))
        elif p == "parede":
            molas.append(mola(n, 1, k, True, -1))
    # grampos (pernas soldadas no teto e na base)
    gr = []
    for (x0, x1) in N["x_gr"]:
        for x in (x0, x1):
            for z, p in ((zt, "teto"), (zb, "base")):
                n = min(nos.items(), key=lambda kv: (kv[0][0] - x) ** 2 + (kv[0][1] - N["y_gr"]) ** 2 + (kv[0][2] - z) ** 2)[1]
                gr.append((p, n, [mola(n, 3, K_AX, False), mola(n, 1, K_PINO, False), mola(n, 2, K_PINO, False)]))
    ops.timeSeries("Linear", 1); ops.pattern("Plain", 1, 1)
    anel = [n for (x, y, z), n in nos.items() if abs(z - zt) < 1e-6 and math.hypot(x - xc, y - y_niv) <= 11.25 + 0.5]
    for n in anel:
        ops.load(n, 0, 0, Vd / len(anel), 0, 0, 0)
    if caso == "sobrepressao":
        anf = [n for (x, y, z), n in nos.items() if abs(y - yf) < 1e-6 and math.hypot(x - xc, z - z_fr) <= 8.0 + 0.5]
        for n in anf:
            ops.load(n, 0, Fd / len(anf), 0, 0, 0, 0)
    if caso == "succao":
        # contato aba × dente: face do dente (13 mm em x) nos 10 mm de baixo da aba (engate mínimo, G máximo)
        lin = [n for (x, y, z), n in nos.items() if abs(y - ya) < 1e-6 and za0 - 1e-6 <= z <= za0 + 10 + 1e-6 and de["x0"] - 1e-6 <= abs(x - xc) <= de["x0"] + de["b"] + 1e-6]
        for n in lin:
            ops.load(n, 0, -Fd / len(lin), 0, 0, 0, 0)
    ops.system("UmfPack"); ops.numberer("RCM"); ops.constraints("Plain")
    ops.integrator("LoadControl", 1.0); ops.test("NormDispIncr", 1e-8, 60); ops.algorithm("Newton"); ops.analysis("Static")
    ok = ops.analyze(1)
    assert ok == 0, "não convergiu"
    ops.reactions()
    vm = {}
    for k, (ns, t, p) in enumerate(E):
        s = np.array(ops.eleResponse(k + 1, "stresses")).reshape(4, 8).mean(0)
        v = 0.0
        for sg in (1, -1):
            sx = s[0] / t + sg * 6 * s[3] / t ** 2; sy = s[1] / t + sg * 6 * s[4] / t ** 2; txy = s[2] / t + sg * 6 * s[5] / t ** 2
            v = max(v, math.sqrt(sx ** 2 - sx * sy + sy ** 2 + 3 * txy ** 2))
        vm.setdefault(p, []).append(v)
    # soldas: esforços por mm na borda de cada chapa junto à junta (N, M, V da casca) → 2 filetes, braço z = t (a favor)
    coord = {n: k for k, n in nos.items()}
    # linhas de solda: (chapa, teste do nó na linha, eixo ao longo da linha)
    L_MED = 10.0                                           # mm: média móvel ao longo do cordão (pico de canto reentrante não é real)
    juntas = dict(teto_fundo=[("fundo", lambda c: abs(c[2] - zt) < 1e-6, 0), ("teto", lambda c: abs(c[1] - yf) < 1e-6, 0)],
                  base_fundo=[("fundo", lambda c: abs(c[2] - zb) < 1e-6, 0), ("base", lambda c: abs(c[1] - yf) < 1e-6, 0)],
                  parede=[("parede", lambda c: abs(c[2] - zt) < 1e-6, 1), ("parede", lambda c: abs(c[2] - zb) < 1e-6, 1),
                          ("parede", lambda c: abs(c[1] - yf) < 1e-6, 2)])
    solda = {}
    for j, regras in juntas.items():
        fmax, fpico, onde = 0.0, 0.0, None
        for pp, f_, eixo in regras:
            lista = []
            for k, (ns, t, p) in enumerate(E):
                if p == pp and any(f_(coord[n]) for n in ns):
                    s8 = np.array(ops.eleResponse(k + 1, "stresses")).reshape(4, 8).mean(0)
                    # eixo local x da casca ≈ direção do 1º lado (nó 1 → 2): cordão ao longo de x local → componentes ⊥ em y local
                    d12 = np.abs(np.array(coord[ns[1]]) - np.array(coord[ns[0]]))
                    i_ = 1 if int(np.argmax(d12)) == eixo else 0
                    nn, mm, vv = abs(s8[i_]), abs(s8[3 + i_]), math.hypot(s8[2], s8[6 + i_])   # N⊥, M⊥ (por mm); cisalhamento no plano e fora dele
                    cs = [coord[n][eixo] for n in ns]
                    lista.append((min(cs), max(cs), math.hypot(nn / 2 + mm / t, vv / 2)))
            for x0, x1, fe in lista:
                fpico = max(fpico, fe)
                ini = min(x0, max(v[1] for v in lista) - L_MED)
                trecho = [(min(v[1], ini + L_MED) - max(v[0], ini), v[2]) for v in lista if v[1] > ini and v[0] < ini + L_MED]
                fm = sum(l * f for l, f in trecho) / sum(l for l, f in trecho)
                if fm > fmax:
                    fmax, onde = fm, round(float(ini), 1)
        a = A_SOLDA[j]
        solda[j] = dict(a_mm=a, F_Nmm=round(fmax, 1), F_pico_Nmm=round(fpico, 1), inicio_trecho_mm=onde,
                        Rd_Nmm=round(solda_por_mm(a), 1), uso=round(fmax / solda_por_mm(a), 3))
    F_gr = {}
    for p, n, ms in gr:
        f = [ops.eleResponse(m, "basicForce")[0] for m in ms]
        F_gr.setdefault(p, []).append(math.sqrt(sum(v * v for v in f)))
    umax = max(np.linalg.norm(ops.nodeDisp(n)[:3]) for n in nos.values())
    ops.wipe()
    res = dict(uso={p: round(float(np.percentile(v, 99)) / (FY[p] / GA1), 3) for p, v in vm.items()},
               vm_p99={p: round(float(np.percentile(v, 99)), 1) for p, v in vm.items()}, vm_max={p: round(float(max(v)), 1) for p, v in vm.items()},
               F_grampo_max_kN={p: round(max(v) / 1e3, 2) for p, v in F_gr.items()}, u_max_mm=round(float(umax), 4), n_elem=len(E), solda=solda)
    return res


def rodar(T, h=4.0):
    R = {c: analisar(T, c, h) for c in ("peso", "sobrepressao", "succao")}
    uso = {p: max(R[c]["uso"][p] for c in R) for p in R["peso"]["uso"]}
    uso.update({"solda_" + j: max(R[c]["solda"][j]["uso"] for c in R) for j in A_SOLDA})
    return R, uso


if __name__ == "__main__":
    T = dict(teto=N["t_teto"], base=N["t_base"], fundo=N["t_fundo"], parede=N["t_parede"], abas=N["t_aba"])
    if len(sys.argv) == 6:
        T = dict(zip(("teto", "base", "fundo", "parede", "abas"), map(float, sys.argv[1:])))
    R, uso = rodar(T, float(os.environ.get("NC1_H", 4.0)))
    out = dict(T=T, uso=uso, casos=R)
    Path(os.environ.get("NC1_SAIDA", AQ / "mef_nc1.json")).write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(dict(T=T, uso=uso), ensure_ascii=False))
