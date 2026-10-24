"""DEC-040 (22/10/2026) — menor armadura longitudinal de cada marca de pilar com a envoltória do modelo integrado r05.
Duas verificações, as duas têm de passar (NBR 6118:2023 15.8.3 + NBR 9062:2017 5.1.2 / Anexo A):
 (a) seção da base com os esforços de 2ª ordem global do r05 (P-Δ, 0,4 EciIc, desaprumo H/400), flexão oblíqua
     (Mx/MRx)^1,2 + (My/MRy)^1,2 ≤ 1 (17.2.5.2), com N de cada combinação (G1,3 e G1,0);
 (b) método geral (15.8.3.2) no pilar isolado em balanço, por direção: NLF por fibras, NLG corrotacional, fluência
     φef 0,5 e imperfeição θ1, com o carregamento de 1ª ordem do r05 (V e M da base → carga distribuída + força no topo)
     e as barras reais (camadas). Passa com λu ≥ 1,0.
Escolhe, por marca, o arranjo de MENOR área de aço que passa (regra do Nathan), simétrico, Ø ≤ 20, espaçamento ≤ 40 cm,
ρ ≥ max(0,15 Nd/fyd; 0,4 %) (17.3.5.3). Grava dimensionamento_pilares_r05.json."""
import json, math, os, sys, types
from pathlib import Path
AQ = Path(__file__).resolve().parent
sys.path.insert(0, str(AQ.parent.parent))
from nd_estruturas.prefabricados import Concreto, pilar_metodo_geral

C40 = Concreto(40)
FYD = 500 / 1.15
EST = json.loads((AQ / "estudo_pilares_r05.json").read_text(encoding="utf-8"))
_r4 = (AQ / "modelo_global_r04.py").read_text(encoding="utf-8")
_p = types.ModuleType("_p"); _p.__dict__["math"] = math
exec(_r4[_r4.index("def MRd("):_r4.index("def tipo_pilar(")], _p.__dict__)
MRd = _p.MRd

GRUPOS = {   # marca → pilares do modelo
    "PL-01": ["P1-L5", "P1-L6", "P1-L7", "P1-L8"], "PL-09": ["P1-L3"], "PL-10": ["P1-L4"], "PL-02": ["P1-L2"],
    "PL-03": ["P1C-L1"], "PL-04": ["P1C-L9"], "PL-05": ["P2-L5", "P2-L6", "P2-L7", "P2-L8"], "PL-11": ["P2-L3"],
    "PL-12": ["P2-L4"], "PL-06": ["P2-L2"], "PL-07": ["P2C-L1"], "PL-08": ["P2C-L9"],
    "PF-01": ["P3-L1"], "PF-02": ["P4-L1"], "PF-03": ["P5-L1"], "PF-05": ["P3-L9"], "PF-04": ["P14-L9"], "PF-06": ["P5-L9"],
    "PC-01": ["P8A"], "PC-02": ["P11"], "PC-03": ["P13", "P13B"], "PM-01": ["P8"], "PM-02": ["P8B"],   # rev09b (DEC-050): alturas diferentes
    "PG-01": ["P9"], "PG-02": ["P10a"], "PG-03": ["P12"], "PG-04": ["P10b"],
    "PE-01": ["P6E"], "PE-02": ["P7E"], "PE-03": ["P6-L2"],            # rev09 (DEC-045): pilares da escada
}
ATUAL = {"PL": (5, 4, 20.0), "PF": (5, 4, 20.0), "PC-01": (5, 7, 20.0), "PC-02": (4, 4, 20.0), "PC-03": (6, 4, 16.0),
         "PM-01": (3, 4, 20.0), "PM-02": (3, 4, 20.0), "PG-01": (3, 3, 16.0), "PG-03": (3, 3, 16.0), "PG-02": (2, 2, 16.0), "PG-04": (2, 2, 16.0),
         "PE-01": (2, 3, 16.0), "PE-02": (3, 3, 16.0), "PE-03": (2, 3, 16.0)}
COB, PHI_T = 0.030, 0.0063
# método geral do pilar isolado em balanço (N no topo) só onde a força normal entra no topo: nos pilares do mezanino a carga
# entra em +3,90/+7,30 e nos dos portões o topo está ligado à TS-01 — ali vale a 2ª ordem global do r05 + fluência e_cc
BITOLAS = tuple(float(x) for x in __import__("os").environ.get("BITOLAS", "16").split(","))
SEM_MG = set()          # rev: método geral com as cargas nos níveis reais em todas as marcas


def barras(bx, by, nx, ny, d):
    c = COB + PHI_T + d / 2000
    xs = [-bx / 2 + c + k * (bx - 2 * c) / (nx - 1) for k in range(nx)]
    ys = [-by / 2 + c + k * (by - 2 * c) / (ny - 1) for k in range(ny)]
    pts = {(round(x, 4), round(y, 4)) for x in xs for y in (ys[0], ys[-1])} | {(round(x, 4), round(y, 4)) for y in ys for x in (xs[0], xs[-1])}
    return [(x, y, math.pi * (d / 1000) ** 2 / 4) for x, y in pts], c


def candidatos(bx, by):
    if os.environ.get("PADRAO") and {round(bx, 2), round(by, 2)} == {0.40, 0.60}:
        # família 40×60 padronizada: k barras em cada face de 40 (as que trabalham na flexão principal) + 1 no meio de cada face de 60
        out = []
        for k in range(2, 8):
            for m in (3, 4, 5, 6, 7):                       # m barras em cada face de 60 (cantos + intermediárias)
                nx, ny = (m, k) if bx > by else (k, m)
                brs, c = barras(bx, by, nx, ny, 16.0)
                out.append(dict(nx=nx, ny=ny, d=16.0, n=len(brs), As=sum(a for *_, a in brs) * 1e4, brs=brs, c=c, tipo=f"T{len(brs)}" + ("" if m == 3 else f"-{m}")))
        return sorted(out, key=lambda k: (round(k["As"], 2), k["n"]))
    out = []
    for d in BITOLAS:
        for nx in range(2, 8):
            for ny in range(2, 8):
                brs, c = barras(bx, by, nx, ny, d)
                sx, sy = (bx - 2 * c) / (nx - 1), (by - 2 * c) / (ny - 1)
                if max(sx, sy) > 0.40 or min(sx, sy) < max(0.02, d / 1000, 1.2 * 0.019) + d / 1000:   # 18.4.2.2 e 18.3.2.2
                    continue
                out.append(dict(nx=nx, ny=ny, d=d, n=len(brs), As=sum(a for *_, a in brs) * 1e4, brs=brs, c=c))
    return sorted(out, key=lambda k: (round(k["As"], 2), k["n"]))


def camadas(brs, eixo):
    """camadas na direção de h para o método geral: eixo 'x' → h = bx (posição x); 'y' → h = by."""
    from collections import Counter
    k = 0 if eixo == "x" else 1
    cnt = Counter(round(b[k], 4) for b in brs)
    a1 = brs[0][2] * 1e4
    return [(y, n, a1) for y, n in sorted(cnt.items())]


from geometria import Z_PISOS as Z_MEZ_DIAF   # +3,90 / +7,30 (lajes alveolares com capa = diafragmas)
PHI = 2.0                                   # coeficiente de fluência φ(∞, t0) — peça pré-moldada carregada após 28 dias (NBR 6118 A.2.2.3)
ECI = 5600 * math.sqrt(40) * 1e3            # kN/m²
QP = "ELU sobrecarga"                       # quase permanente ≈ (G1,3 + Q1,4)/1,35 (a favor da segurança: inclui toda a sobrecarga)


def e_cc(p):
    """excentricidade de fluência por direção (NBR 6118:2023 15.8.4) — pilar em balanço, le = 2H."""
    b = EST[QP]["1a"][p]
    H, Nsg = b["H"], max(b["N"], 1.0) / 1.35
    out = {}
    for eixo, Mk, h, bb in (("x", "My", b["bx"], b["by"]), ("y", "Mx", b["by"], b["bx"])):
        Msg = abs(b[Mk]) / 1.35
        le = 2 * H
        if all(any(abs(z - zl) < 1e-3 for z in b["zs"]) for zl in Z_MEZ_DIAF):
            # rev09b (DEC-050): pilar ligado às 2 lajes do mezanino (diafragmas +3,90 e +7,30): o deslocamento lateral do conjunto já está
            # na 2ª ordem global do r05; para a fluência vale o comprimento entre travamentos (trecho em balanço acima do +7,30 com le = 2 l)
            le = max(2 * (H - Z_MEZ_DIAF[-1]), Z_MEZ_DIAF[0], Z_MEZ_DIAF[1] - Z_MEZ_DIAF[0])
        Ne = 10 * ECI * (bb * h ** 3 / 12) / le ** 2
        th = max(1 / 300, min(1 / 200, 1 / (100 * math.sqrt(H))))
        ea = th * H
        out[eixo] = (Msg / Nsg + ea) * (math.exp(PHI * Nsg / max(Ne - Nsg, 1e-6)) - 1) if Nsg < Ne else 9.9
    return out


def secao_ok(cand, pils):
    pior = 0.0
    ecc = {p: e_cc(p) for p in pils}
    for nome_c, it in EST.items():
        for p in pils:
            b = it["2a"][p]
            Nd = max(b["N"], 0.0)
            MRx = MRd(b["bx"], b["by"], cand["brs"], Nd, "y")
            MRy = MRd(b["by"], b["bx"], cand["brs"], Nd, "x")
            Mx = abs(b["Mx"]) + Nd * ecc[p]["y"]
            My = abs(b["My"]) + Nd * ecc[p]["x"]
            u = (Mx / MRx) ** 1.2 + (My / MRy) ** 1.2
            if u > pior:
                pior, onde = u, (nome_c, p)
    return pior, onde


def cargas_nos(b, eixo):
    """cargas externas nos nós do pilar no plano de flexão, a partir dos esforços dos trechos (1ª ordem do r05):
    P_nó = Σ forças de extremidade dos trechos que chegam ao nó. Devolve [(z, Fh, Fv, M2d)] do 2º nó ao topo."""
    zs, sg = b["zs"], b["segs"]
    kh, km, sm = (0, 4, -1.0) if eixo == "x" else (1, 3, 1.0)
    out = []
    for k in range(1, len(zs)):
        fj = sg[k - 1][6:]
        fi = sg[k][:6] if k < len(sg) else [0.0] * 6
        F = [fj[t] + fi[t] for t in range(6)]
        out.append((zs[k], F[kh], F[2], sm * F[km]))
    return out


def mg_nodal(bb, h, zs, cargas, camadas_, c, phi_ef=0.5, sub=3):
    """método geral (NBR 6118:2023 15.8.3.2) do pilar isolado engastado na base com as cargas nos níveis reais:
    forças verticais fixas (+ imperfeição θ1·N), forças horizontais e momentos crescendo até λu. Fibras (concreto
    0,85 fcd com o diagrama alongado por (1+φef), CA-50 de cálculo), corrotacional. λu ≥ 1,0 passa."""
    import openseespy.opensees as ops
    ops.wipe(); ops.logFile("/dev/null", "-noEcho")
    ops.model("basic", "-ndm", 2, "-ndf", 3)
    zn = [0.0]
    for z0, z1 in zip(zs[:-1], zs[1:]):
        zn += [z0 + (z1 - z0) * (i + 1) / sub for i in range(sub)]
    for i, z in enumerate(zn):
        ops.node(i + 1, 0.0, z)
    ops.fix(1, 1, 1, 1)
    fc = 0.85 * C40.fcd
    e0, eu = -0.002 * (1 + phi_ef), -0.0035 * (1 + phi_ef)
    ops.uniaxialMaterial("Concrete01", 1, -fc, e0, -fc, eu)
    ops.uniaxialMaterial("Steel01", 2, 500e3 / 1.15, 210e6, 0.001)
    ops.section("Fiber", 1)
    ops.patch("rect", 1, 24, 4, -h / 2, -bb / 2, h / 2, bb / 2)
    for y, n, a1 in camadas_:
        if n == 1:
            ops.fiber(y, 0.0, a1 * 1e-4, 2)
        else:
            ops.layer("straight", 2, n, a1 * 1e-4, y, -bb / 2 + c, y, bb / 2 - c)
    ops.geomTransf("Corotational", 1)
    ops.beamIntegration("Lobatto", 1, 1, 5)
    for i in range(len(zn) - 1):
        ops.element("forceBeamColumn", i + 1, i + 1, i + 2, 1, 1)
    no = {round(z, 4): i + 1 for i, z in enumerate(zn)}
    H = zs[-1]
    th = max(1 / 300, min(1 / 200, 1 / (100 * math.sqrt(H))))
    sgn = 1.0 if sum(Fh * z + M for z, Fh, Fv, M in cargas) >= 0 else -1.0     # imperfeição no sentido das ações horizontais
    ops.timeSeries("Constant", 1); ops.pattern("Plain", 1, 1)
    for z, Fh, Fv, M in cargas:
        N = -Fv if Fv < 0 else 0.0
        ops.load(no[round(z, 4)], sgn * th * N, Fv if Fv < 0 else 0.0, 0.0)
    ops.system("BandGeneral"); ops.numberer("RCM"); ops.constraints("Plain")
    ops.test("NormDispIncr", 1e-8, 60); ops.algorithm("Newton")
    ops.integrator("LoadControl", 0.1); ops.analysis("Static")
    if ops.analyze(10) != 0:
        ops.wipe(); return 0.0
    ops.loadConst("-time", 0.0)
    ops.timeSeries("Linear", 2); ops.pattern("Plain", 2, 2)
    for z, Fh, Fv, M in cargas:
        ops.load(no[round(z, 4)], Fh, Fv if Fv > 0 else 0.0, M)
    nel = len(zn) - 1

    def rompeu():
        for e in range(1, nel + 1):
            for ip in range(1, 6):
                d = ops.eleResponse(e, "section", ip, "deformation")
                if not d:
                    continue
                eps, kap = d[0], d[1]
                ec = min(eps - kap * h / 2, eps + kap * h / 2)
                es = max(eps - kap * (h / 2 - c), eps + kap * (h / 2 - c))
                if ec < eu or es > 0.010:
                    return True
        return False
    lam, st = 0.0, 0.02
    ops.integrator("LoadControl", st)
    while lam < 3.0:
        if ops.analyze(1) != 0:
            okk = False
            for s_ in (st / 4, st / 16):
                ops.integrator("LoadControl", s_)
                if ops.analyze(1) == 0:
                    okk, lam = True, lam + s_
                    break
            if not okk:
                break
            ops.integrator("LoadControl", st)
        else:
            lam += st
        if rompeu():
            lam -= st
            break
    ops.wipe()
    return round(lam, 2)


def criticos(pils, n=3):
    """combinações com maior momento de 1ª ordem na base, por direção (e a de maior N)."""
    out = []
    for eixo, Mk in (("x", "My"), ("y", "Mx")):
        lst = sorted(((abs(it["1a"][p][Mk]), nome_c, p) for nome_c, it in EST.items() for p in pils), reverse=True)[:n]
        out += [(eixo, nome_c, p) for _, nome_c, p in lst]
    return out


def mg_ok(cand, crit):
    pior, onde = 9.9, None
    for eixo, nome_c, p in crit:
        b = EST[nome_c]["1a"][p]
        h, bb = (b["bx"], b["by"]) if eixo == "x" else (b["by"], b["bx"])
        lam = mg_nodal(bb, h, b["zs"], cargas_nos(b, eixo), camadas(cand["brs"], eixo), cand["c"])
        if lam < pior:
            pior, onde = lam, (eixo, nome_c, p)
        if pior < 1.0:
            break
    return pior, onde


import manuseio_pilares_r05 as MAN_


def manuseio(mk, cand):
    g = json.loads(open(f"/home/claude/letsara/pranchas/{mk}_geom.json", encoding="utf-8").read())
    nb, nh = MAN_.arranjo(mk, cand)
    pts = MAN_.xy(g["B"], g["H"], nb, nh, c=cand["c"] * 1000)
    A1 = math.pi * cand["d"] ** 2 / 4
    bars = [(x, y, A1) for x, y in pts]
    L = g["L_TOT"] / 1000
    w = g["B"] * g["H"] / 1e6 * 25 * 1.10
    casos = [("deitado nas 2 AL-2", MAN_.momentos(L, w, [z / 1000 for z in g["al"]]), "H"),
             (f"verticalização FI-1 {g['fi']['eixo']}", MAN_.momentos(L, w, [0.0, g["fi"]["z"] / 1000]), "H" if g["fi"]["eixo"] == "BD" else "B")]
    pior, ok, det = 0.0, True, []
    for nome, Mk, dirc in casos:
        h, b, eixo = (g["H"], g["B"], "y") if dirc == "H" else (g["B"], g["H"], "x")
        MRd = MAN_.MRd0(b, h, bars, eixo)
        k = 1 if eixo == "y" else 0
        ymax = max(q[k] for q in pts)
        At = sum(A1 for q in pts if abs(q[k] - ymax) < 1)
        sig = Mk * 1.3 * 1e6 / (At * 0.9 * (h / 2 + ymax))
        ok &= 1.69 * Mk <= MRd and sig <= 250
        det.append(dict(caso=nome, Mk=round(Mk, 1), uso=round(1.69 * Mk / MRd, 2), sigma_s=round(sig)))
    return dict(ok=ok, casos=det)


def rho_min(cand, pils):
    b0 = EST[next(iter(EST))]["2a"][pils[0]]
    Ac = b0["bx"] * b0["by"]
    Nd = max(it["2a"][p]["N"] for it in EST.values() for p in pils)
    return max(0.15 * Nd / (FYD * 1e3), 0.004 * Ac) * 1e4


if __name__ == "__main__":
    so = sys.argv[1:]
    out = json.loads((AQ / "dimensionamento_pilares_r05.json").read_text(encoding="utf-8")) if so and (AQ / "dimensionamento_pilares_r05.json").exists() else {}
    for mk, pils in GRUPOS.items():
        if so and mk not in so:
            continue
        b0 = EST[next(iter(EST))]["2a"][pils[0]]
        bx, by = b0["bx"], b0["by"]
        At = rho_min(None, pils)
        crit = criticos(pils)
        a = ATUAL.get(mk, ATUAL.get(mk[:2]))
        nx_a, ny_a = (a[0], a[1]) if bx < by or abs(bx - by) < 1e-6 else (a[1], a[0])   # ATUAL: (barras na face menor, barras na face maior)
        brs_a, c_a = barras(bx, by, a[0] if bx <= by else a[1], a[1] if bx <= by else a[0], a[2])
        atual = dict(n=len(brs_a), d=a[2], As=round(sum(x[2] for x in brs_a) * 1e4, 1))
        u_at, _ = secao_ok(dict(brs=brs_a), pils)
        esc = None
        for cand in candidatos(bx, by):
            if cand["As"] < At:
                continue
            u, onde_u = secao_ok(cand, pils)
            if u > 1.0:
                continue
            man = manuseio(mk, cand)
            if not man["ok"]:
                continue
            if mk in SEM_MG:
                lam, onde_l = None, "não se aplica (N entra nos níveis do mezanino / topo ligado à TS-01): seção com 2ª ordem global + e_cc"
            else:
                lam, onde_l = mg_ok(cand, crit)
                if lam < 1.0:
                    continue
            esc = dict(manuseio=man, tipo=cand.get("tipo"), nx=cand["nx"], ny=cand["ny"], d=cand["d"], n=cand["n"], As_cm2=round(cand["As"], 2), uso_secao=round(u, 3),
                       comb_secao=onde_u, lambda_u=lam, mg_governa=onde_l, As_min_cm2=round(At, 2),
                       taxa_pct=round(cand["As"] / (bx * by * 1e4) * 100, 2))
            break
        out[mk] = dict(e_cc_cm={k: round(v * 100, 2) for k, v in e_cc(pils[0]).items()}, pilares=pils, secao=f"{bx*100:.0f}×{by*100:.0f}", H=b0["H"], atual=atual, uso_atual=round(u_at, 3), proposto=esc)
        print(mk, out[mk]["secao"], "atual", atual, "uso", round(u_at, 3), "→", esc and {k: esc[k] for k in ("n", "d", "nx", "ny", "As_cm2", "uso_secao", "lambda_u")}, flush=True)
        (AQ / "dimensionamento_pilares_r05.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
