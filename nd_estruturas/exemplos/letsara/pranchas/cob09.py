"""ND-LET-COB09 — cobertura metálica: isométricos explodidos de montagem das ligações (rev11, Nathan 26/10/2026, checklist 8):
terças na TS-01 (ST-1P + transpasse), W da linha 2 na cabeça do pilar, montante W 150 sobre a VM do +7,30, emenda da W e terça
na W (ST-W + MF-1). Geometria única: exemplos/letsara/lig_cob.py — a mesma que o modelo 3D usa. Balões = itens da tabela;
parafusos com Ø, classe, comprimento, quantidade e torque. A1."""
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
import math
import numpy as np
import iso_nd as I
import lig_cob as LC
from prancha_nd import Prancha
from cob_comum import cabecalho

pr = Prancha("A0", cabecalho("ND-LET-COB09", "01/01", "COBERTURA METÁLICA — ISOMÉTRICOS EXPLODIDOS DE MONTAGEM DAS LIGAÇÕES (TERÇAS, W DA LINHA 2, MONTANTES, EMENDAS, ST-W, ST-1V E ST-1FL)"))
pr.revisao("11", "26/10/2026", "EMISSÃO: ISOMÉTRICOS EXPLODIDOS GERADOS DA GEOMETRIA DO 3D; TORQUES DE APERTO")
pr.revisao("R12", "27/10/2026", "FOLHA A0; ISO 6 (TERÇA NA VB, ST-1V) E ISO 7 (TERÇA NO PILAR DE CANTO, ST-1FL)")
Q = pr.quadro
cam = I.Camera((-1.0, -1.25, 0.95))
COR = {"concreto": I.CONCRETO, "par": I.CINZA_PAR, "aco": I.AZUL_ACO, "terca": (186, 196, 176)}


def solidos(partes, explodido=True):
    out = []
    for p in partes:
        e = np.array(p["exp"], float) if explodido else np.zeros(3)
        cor = COR["concreto"] if p.get("concreto") else (COR["par"] if p["g"] in ("cil", "hex") else (COR["terca"] if p["marca"] == "T" else COR["aco"]))
        kw = dict(item=p["item"], cor=cor)
        if p["g"] == "caixa":
            x0, x1, y0, y1, z0, z1 = p["b"]
            s = I.caixa(x0, x1, y0, y1, z0, z1, **kw)
        elif p["g"] == "cil":
            c, h = p["c"], p["h"]
            ax = "xyz".index(p["eixo"])
            c = list(c)
            if h < 0:
                c[ax] += h
                h = -h
            s = I.cilindro(tuple(c), p["eixo"], p["r"], h, n=12, **kw)
        elif p["g"] == "hex":
            c, h = list(p["c"]), p["h"]
            ax = "xyz".index(p["eixo"])
            if h < 0:
                c[ax] += h
                h = -h
            s = I.cilindro(tuple(c), p["eixo"], p["r"], h, hexa=True, **kw)
        elif p["g"] == "prisma_xz":
            s = I.prisma(p["pol"], "xz", p["y"][0], p["y"][1], **kw)
        elif p["g"] == "barra":
            a, b = np.array(p["a"], float), np.array(p["b"], float)
            u = (b - a) / np.linalg.norm(b - a)
            n1 = np.array((1.0, 0, 0))
            n2 = np.cross(u, n1)
            t1, t2 = p["s"]
            cs = [n1 * sx * t1 / 2 + n2 * sy * t2 / 2 for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            base = [a + c_ for c_ in cs]
            topo = [b + c_ for c_ in cs]
            F = [base, topo] + [[base[i], base[(i + 1) % 4], topo[(i + 1) % 4], topo[i]] for i in range(4)]
            s = I.Solido(F, **kw)
        else:
            continue
        out.append(s.movido(e) if explodido else s)
    return out


def bbox_proj(sol):
    pts = np.vstack([f for s in sol for f in s.faces])
    pp = np.array([cam.proj(p) for p in pts])
    return pp.min(0), pp.max(0)


def qt_item(partes, it):
    return sum(1 for p in partes if p["item"] == it and p["desc"])


def desc_item(partes, it):
    return next(p["desc"] for p in partes if p["item"] == it and p["desc"])


# comprimento comercial do parafuso (mm): pega + 2 fios além da porca, arredondado para a série 5/10
def L_paraf(partes, it):
    Ls = [abs(p["h"]) for p in partes if p["item"] == it and p["g"] == "cil" and p["desc"]]
    if not Ls:
        return None
    L = max(Ls)
    return int(math.ceil(L / 5.0) * 5)


import os, json as _json, re as _re
SKIP = _json.loads(os.environ.get("COB09_SKIP", "[]"))
_x2 = lambda a, b: a[0] * b[1] - a[1] * b[0]
CELAS = {"ISO 2": (Q[0] + 8, Q[3] - 14, 200, 250), "ISO 3": (Q[0] + 214, Q[3] - 14, 200, 250), "ISO 4": (Q[0] + 420, Q[3] - 14, 200, 250),
         "ISO 1": (Q[0] + 8, Q[3] - 300, 300, 200), "ISO 5": (Q[0] + 316, Q[3] - 300, 304, 200),
         "ISO 6": (Q[0] + 8, Q[3] - 520, 300, 200), "ISO 7": (Q[0] + 316, Q[3] - 520, 304, 200)}   # rev12: ST-1V na VB e ST-1FL no canto
TAB = []
for nome, (tit, fn) in LC.ITENS.items():
    partes = fn()
    sol = solidos(partes)
    (x0, y0), (x1, y1) = bbox_proj(sol)
    cx, cy, cw, ch = CELAS[nome]
    esc = next(e for e in (2.5, 3, 4, 5, 6, 7.5, 8, 10, 12.5, 15) if (x1 - x0) / e <= cw - 40 and (y1 - y0) / e <= ch - 46)
    org = (cx + 20 + (cw - 40 - (x1 - x0) / esc) / 2 - x0 / esc, cy - 8 - (ch - 46) + (ch - 46 - (y1 - y0) / esc) / 2 - y0 / esc)
    v = pr.vista(nome, org, esc, titulo=f"{nome} — {tit}", subtitulo="explodido ao longo dos parafusos; balões = itens da tabela", unidade="mm")
    pj = I.desenhar_iso(v, sol, cam)
    # rev12 (COB09): cotas em mm nas chapas (2 maiores arestas, alinhadas no isométrico) e hachura na face maior de cada chapa
    feitos = set()
    for p in partes:
        if p["g"] != "caixa" or p.get("concreto") or p["marca"] == "T" or p["item"] in feitos:
            continue
        feitos.add(p["item"])
        bx0, bx1, by0, by1, bz0, bz1 = p["b"]
        e_ = np.array(p["exp"], float)
        dims = sorted([(bx1 - bx0, 0), (by1 - by0, 1), (bz1 - bz0, 2)], reverse=True)
        lo = np.array((bx0, by0, bz0), float) + e_
        for comp, ax in dims[:2]:
            if comp < 15 or [nome, f"{comp:g}"] in SKIP:
                continue
            fim = lo.copy(); fim[ax] += comp
            pa, pb = cam.proj(lo), cam.proj(fim)
            dx, dy = pb[0] - pa[0], pb[1] - pa[1]
            nrm = math.hypot(dx, dy) or 1.0
            ox, oy = -dy / nrm * 6 * esc, dx / nrm * 6 * esc                 # 6 mm no papel, para fora do conjunto
            cxa, cya = np.mean([cam.proj(np.array(c_, float)) for s_ in sol for f_ in s_.faces for c_ in f_], axis=0)
            if ox * ((pa[0] + pb[0]) / 2 - cxa) + oy * ((pa[1] + pb[1]) / 2 - cya) < 0:
                ox, oy = -ox, -oy
            qa, qb = (pa[0] + ox, pa[1] + oy), (pb[0] + ox, pb[1] + oy)
            v.linha(pa, qa, "COTA"); v.linha(pb, qb, "COTA"); v.linha(qa, qb, "COTA")
            ang = math.degrees(math.atan2(dy, dx))
            ang = ang + 180 if ang > 90 else (ang - 180 if ang < -90 else ang)
            v.texto(((qa[0] + qb[0]) / 2 + ox * 0.15, (qa[1] + qb[1]) / 2 + oy * 0.15), f"{comp:g}".replace(".", ","), "nota", "BOTTOM_CENTER", rot=ang)
        # hachura da face de maior área (projetada)
        cantos = lambda fixo, val: [np.array(c_, float) + e_ for c_ in (
            [(val, by0, bz0), (val, by1, bz0), (val, by1, bz1), (val, by0, bz1)] if fixo == 0 else
            [(bx0, val, bz0), (bx1, val, bz0), (bx1, val, bz1), (bx0, val, bz1)] if fixo == 1 else
            [(bx0, by0, val), (bx1, by0, val), (bx1, by1, val), (bx0, by1, val)])]
        melhor = max(((fx, vv) for fx, vv in ((0, bx0), (0, bx1), (1, by0), (1, by1), (2, bz0), (2, bz1))),
                     key=lambda t: abs(_x2(np.subtract(cam.proj(cantos(*t)[2]), cam.proj(cantos(*t)[0])), np.subtract(cam.proj(cantos(*t)[3]), cam.proj(cantos(*t)[1])))))
        v.hachura([tuple(cam.proj(c_)) for c_ in cantos(*melhor)], "ANSI31", 0.4 * esc / 5, "METALICA")
    # balões fora do desenho, na direção do centro do item (ordenados para não cruzar)
    xc_, yc_ = (x0 + x1) / 2, (y0 + y1) / 2
    itens = sorted({p["item"] for p in partes})
    anc = {}
    for it in itens:
        ss = [s for s in sol if s.item == it]
        c = np.vstack([f for s in ss for f in s.faces]).mean(0)
        anc[it] = cam.proj(c)
    usados = []
    for it in itens:
        px, py = anc[it]
        ang = math.atan2(py - yc_, px - xc_)
        for tent in range(24):
            a_ = ang + (tent // 2 + 1) * 0.13 * (1 if tent % 2 else -1) * (tent > 0)
            # ponto na borda do retângulo do desenho + 9 mm no papel
            rx, ry = (x1 - x0) / 2 / esc + 9, (y1 - y0) / 2 / esc + 9
            k = min(rx / max(abs(math.cos(a_)), 1e-6), ry / max(abs(math.sin(a_)), 1e-6))
            bx, by = xc_ / esc + k * math.cos(a_), yc_ / esc + k * math.sin(a_)
            if all(math.hypot(bx - ux, by - uy) > 9 for ux, uy in usados):
                break
        usados.append((bx, by))
        I.balao(v, (px, py), (bx - px / esc, by - py / esc), it)
        p0 = next(p for p in partes if p["item"] == it and p["desc"])
        nome_ = p0["marca"]
        dsc = desc_item(partes, it)
        if p0["g"] == "cil" and "8.8" in nome_ and nome_.startswith("M"):
            L = L_paraf(partes, it)
            dd = 12 if "M12" in nome_ else 16
            nome_ = f"{nome_.split()[0]} × {L}" + (" 8.8" if "8.8" in p0["marca"] else "")
            dsc += f" — torque {LC.TORQUE['M12' if dd == 12 else 'M16']} N·m"
        TAB.append([nome.replace("ISO ", ""), str(it), nome_, dsc, str(qt_item(partes, it))])

# ------------------------------------------------------------------ tabela de itens e notas
x0t = Q[2] - 182
y = pr.tabela(x0t, Q[3] - 4, "ITENS DOS ISOMÉTRICOS (QT POR LIGAÇÃO)", ["ISO", "ITEM", "MARCA", "DESCRIÇÃO", "QT"], TAB, [10, 10, 26, 124, 10], h_lin=5.6)
notas = [
    "Ligações 100 % parafusadas, sem solda na fábrica e na obra. Parafusos ASTM A325 / ISO 8.8 zincados a fogo, porca classe 8 e arruela lisa endurecida; furos d + 2 mm (Ø14 para M12, Ø18 para M16) de fábrica.",
    f"Torque de aperto (porca encostada + giro com torquímetro, k = 0,20 em rosca galvanizada): M12 = {LC.TORQUE['M12']} N·m, M16 = {LC.TORQUE['M16']} N·m. Exceções: nos furos oblongos deslizantes da W da linha 2 (fora do apoio C) e das ES-1 a porca fica encostada (folga ≤ 1 mm) com contraporca; nas terças Z 2,30 confirmar o torque com a METSEC antes da montagem.",
    "Concreto (cinza claro) e perfis principais aparecem só como referência; marcas, comprimentos e quantidades totais nas listas da COB01, COB02 e COB05.",
    "Sequência de montagem de cada isométrico: peças na ordem dos itens (1, 2, 3...), parafusos postos com aperto manual; aperto final com toda a linha montada e alinhada."]
pr.notas(x0t, y - 4, notas, 180)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-COB09")
_cruz = [a for a in avisos if "cruza o texto" in a[1]]
if _cruz and not os.environ.get("COB09_SKIP"):                         # rev12: cota que cruza o desenho sai (fica a da tabela de itens)
    import subprocess as _sp
    _vals = {_re.search(r"texto '([^']+)'", a[1]).group(1) for a in _cruz}
    _sk = [[n_, v_] for n_ in CELAS for v_ in _vals]
    _sp.run([sys.executable, __file__], env=dict(os.environ, COB09_SKIP=_json.dumps(_sk)))
    sys.exit(0)
for a in avisos:
    print(a)
