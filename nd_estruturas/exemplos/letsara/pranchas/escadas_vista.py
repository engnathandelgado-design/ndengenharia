"""Projeção das peças de escadas.json (fonte única: escadas_detalhe.py) nas vistas das folhas ES01/ES02/ES03.
Cada peça vira o contorno projetado (envoltória convexa dos vértices) no plano pedido; as longarinas (contorno poligonal) são
desenhadas pelo próprio contorno quando a vista é perpendicular ao eixo de extrusão. Unidades: entrada em m, saída em mm."""
import json
import math

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
EJ = json.load(open(AQ + "escadas.json"))
P = EJ["pecas"]


def _sub(a, b): return [a[i] - b[i] for i in range(3)]
def _norm(a):
    n = math.sqrt(sum(v * v for v in a)) or 1.0
    return [v / n for v in a]
def _cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def vertices(pc):
    """vértices 3D (m) da peça."""
    if pc["g"] == "caixa":
        return [(x, y, z) for x in (pc["x0"], pc["x1"]) for y in (pc["y0"], pc["y1"]) for z in (pc["z0"], pc["z1"])]
    if pc["g"] == "poligono":
        out = []
        for c, z in pc["contorno"]:
            for a in (pc["a0"], pc["a1"]):
                out.append((a, c, z) if pc["eixo"] == "y" else (c, a, z))
        return out
    pf = pc["perfil"]
    h, b = (pf[1], pf[2]) if pf[0] == "I" else (pf[2], pf[1])
    ax = _norm(_sub(pc["p1"], pc["p0"]))
    up = _norm(pc["cima"])
    lat = _norm(_cross(up, ax))
    out = []
    for p in (pc["p0"], pc["p1"]):
        for su in (-0.5, 0.5):
            for sl in (-0.5, 0.5):
                out.append(tuple(p[i] + su * h * up[i] + sl * b * lat[i] for i in range(3)))
    return out


def _hull(pts):
    pts = sorted(set((round(x, 2), round(y, 2)) for x, y in pts))
    if len(pts) < 3:
        return pts
    def cr(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def projetar(v, plano, filtro, cam="METALICA", tf=None, minimo=1.0):
    """plano: função (x, y, z) m → (u, w) mm; filtro: função peça → bool; tf: função peça → camada (opcional).
    Devolve o número de peças desenhadas."""
    n = 0
    for pc in P:
        if not filtro(pc):
            continue
        c = tf(pc) if tf else cam
        if c is None:
            continue
        if pc["g"] == "poligono":
            q0 = plano(*((pc["a0"], 0, 0) if pc["eixo"] == "y" else (0, pc["a0"], 0)))
            q1 = plano(*((pc["a1"], 0, 0) if pc["eixo"] == "y" else (0, pc["a1"], 0)))
            if abs(q0[0] - q1[0]) < 1e-6 and abs(q0[1] - q1[1]) < 1e-6:      # vista perpendicular à extrusão: contorno real
                pts = [plano(*((pc["a0"], cc, z) if pc["eixo"] == "y" else (cc, pc["a0"], z))) for cc, z in pc["contorno"]]
                pts = [p for i, p in enumerate(pts) if i == 0 or abs(p[0] - pts[i - 1][0]) + abs(p[1] - pts[i - 1][1]) > 0.5]
                v.poli(pts, c, fechada=True); n += 1
                continue
        h = _hull([plano(*p) for p in vertices(pc)])
        if len(h) >= 3:
            xs = [p[0] for p in h]; ys = [p[1] for p in h]
            if max(xs) - min(xs) < minimo and max(ys) - min(ys) < minimo:
                continue
            v.poli(h, c, fechada=True); n += 1
        elif len(h) == 2:
            v.linha(h[0], h[1], c); n += 1
    return n


def zmin(pc): return min(p[2] for p in vertices(pc))
def zmax(pc): return max(p[2] for p in vertices(pc))
def bbox(pc):
    vs = vertices(pc)
    return [min(p[i] for p in vs) for i in range(3)], [max(p[i] for p in vs) for i in range(3)]


def externa(pc): return "externa" in pc["grupo"]
def interna(pc): return pc["grupo"].startswith("Escada metálica") and not externa(pc)
def guarda(pc): return pc["marca"][:3] in ("GI-", "GE-")


def cod(pc): return pc["marca"].split()[0]


def centro(prefixo, plano, cond=lambda pc: True):
    """centro projetado (mm) da 1ª peça cujo código começa com o prefixo."""
    for pc in P:
        if pc["marca"].startswith(prefixo) and cond(pc):
            vs = [plano(*p) for p in vertices(pc)]
            return (sum(p[0] for p in vs) / len(vs), sum(p[1] for p in vs) / len(vs))
    raise KeyError(prefixo)


def linhas_lista(escada, f):
    """linhas da lista de material: estrutura item a item e cada guarda-corpo/corrimão consolidado numa linha."""
    out, gc = [], {}
    for r in EJ["lista"]:
        if r["escada"] != escada:
            continue
        if r["item"][:3] in ("GI-", "GE-"):
            g = gc.setdefault(r["item"], dict(kg=0.0, partes=[]))
            g["kg"] += r["kg"]
            p_ = r["desc"].split(" do fechamento")[0].replace("barra redonda ", "barras ")
            g["partes"].append(p_.replace("montante ", "mont. ").replace("cantoneira ", "").replace(" das barras", " (barras)"))
        else:
            out.append([r["item"], r["desc"], str(r["qt"]), f(r["kg"], 1)])
    nomes = {g["cod"]: g["nome"] for g in EJ["guardas"]}
    for k in sorted(gc, key=lambda s: (s[:3], int(s[3:]) if s[3:].isdigit() else 99)):
        out.append([k, ("corrimão" if k in ("GI-2", "GE-2", "GI-R") else "guarda-corpo + corrimão") + " — " + nomes.get(k, "retorno no patamar") + " (ND-LET-ES03)", "1", f(gc[k]["kg"], 1)])
    return out
