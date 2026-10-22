"""Checagem de colisão do MODELO INTEIRO (22/10/2026): todas as peças × todas, com caixas ORIENTADAS (OBB, teorema do eixo
separador), não caixas alinhadas aos eixos — peças inclinadas (X, TS-01 a 3 %, telhas) não geram falso positivo.
Exclui o que atravessa ou fica embutido por projeto (parafusos, pinos, esperas, buchas, grampos, alças, tubos, neoprenes,
juntas grauteadas, CE-1 rente/embutida, consoles no nicho da placa, terças no transpasse, camadas da cobertura entre si).
Saída: colisao_modelo.json (lista de colisões > 1 mm, agrupadas por par de grupos)."""
import json, math, sys, collections
from pathlib import Path
import numpy as np
import manifold3d as mf
AQ = Path(__file__).parent
sys.path.insert(0, str(AQ)); sys.path.insert(0, str(AQ.parent.parent))
import modelo_bim as MB
from nd_estruturas.bim import PerfilI, PerfilPoligono

TOL = 0.001
ATRAVESSA = ("pino", "espera", "es-", "bucha", "chumbador", "pn-", "n18", "grampo", "br-", "barra roscada", "porca", "tb-", "tubo",
             "neoprene", "neo-", "alça", "al-", "fi-1", "m12", "m16", "m20", "graute", "junta", "ce-1", "parafuso", "prisioneiro", "luva",
             "tsa", "par tapper", "rebite", "esticador", "or-x", "insertos")
PARES_OK = {frozenset(("Fixação das placas", "Placas de fechamento")), frozenset(("Telhas",)), frozenset(("Terças metálicas",)),
            frozenset(("Laje alveolar", "Concreto de 2º estágio (obra, com a capa)")), frozenset(("Vigas de mezanino (meio vaso)", "Concreto de 2º estágio (obra, com a capa)")),
            frozenset(("Vigas de mezanino (meio vaso)",)), frozenset(("Vigas centrais I130",)), frozenset(("Pilares",)),
            frozenset(("Fixação das placas",)), frozenset(("Ligações da cobertura",)), frozenset(("Calha e descidas",)),
            frozenset(("Pilares", "Consolos")), frozenset(("Piso e fundações", "Pilares")), frozenset(("Piso e fundações",)),
            frozenset(("Rufos e acabamentos",)), frozenset(("Alças N9 (2º estágio)", "Concreto de 2º estágio (obra, com a capa)")),
            frozenset(("Alças N9 (2º estágio)", "Vigas de mezanino (meio vaso)")), frozenset(("Contraventamento",)),
            frozenset(("Correntes, tirantes rígidos e diagonais",)),
            frozenset(("Esperas e insertos embutidos", "Placas de fechamento"))}      # NC-1: nicho embutido na placa
# tolerância de contato por par (mm): telhas modeladas como lâminas planas entre os apoios (seguem a reta do topo das terças) —
# ficam até 6 mm "dentro" do Z302 no meio; barras, correntes e suportes encostados na terça com folga de modelagem ≤ 3 mm
TOL_PAR = {frozenset(("Telhas", "Terças metálicas")): 7.0}
TOL_MM = 3.0


def obb(p):
    M = np.array(p.matriz(), float)
    pf = p.perfil
    if isinstance(pf, PerfilPoligono):
        xs, ys = zip(*pf.pontos); x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    else:
        x0, x1, y0, y1 = -pf.b / 2, pf.b / 2, -pf.h / 2, pf.h / 2
    L = p.comprimento
    c_loc = np.array([(x0 + x1) / 2, (y0 + y1) / 2, L / 2, 1.0])
    c = (M @ c_loc)[:3]
    ax = [M[:3, i] / np.linalg.norm(M[:3, i]) for i in range(3)]
    h = np.array([(x1 - x0) / 2, (y1 - y0) / 2, L / 2])
    return c, ax, h


def solido(p):
    """sólido exato da peça (perfil real extrudado, inclusive Z e polígonos côncavos) no referencial global."""
    pf = p.perfil
    if isinstance(pf, PerfilPoligono):
        pts = [tuple(q) for q in pf.pontos]
    elif isinstance(pf, PerfilI):
        b, h, tw, tf = pf.b / 2, pf.h / 2, pf.tw / 2, pf.tf
        pts = [(-b, -h), (b, -h), (b, -h + tf), (tw, -h + tf), (tw, h - tf), (b, h - tf), (b, h), (-b, h), (-b, h - tf), (-tw, h - tf), (-tw, -h + tf), (-b, -h + tf)]
    else:
        pts = [(-pf.b / 2, -pf.h / 2), (pf.b / 2, -pf.h / 2), (pf.b / 2, pf.h / 2), (-pf.b / 2, pf.h / 2)]
    A2 = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    if A2 < 0:
        pts = pts[::-1]
    so = mf.Manifold.extrude(mf.CrossSection([pts]), p.comprimento)
    M = np.array(p.matriz(), float)
    return so.transform(M[:3, :4].tolist())


def sat(A, B):
    """menor sobreposição (m) entre duas OBB nos 15 eixos; <= 0 = separadas."""
    ca, aa, ha = A; cb, ab, hb = B
    t = cb - ca
    best = 1e9
    eixos = list(aa) + list(ab) + [np.cross(u, v) for u in aa for v in ab]
    for e in eixos:
        n = np.linalg.norm(e)
        if n < 1e-9:
            continue
        e = e / n
        ra = sum(ha[i] * abs(aa[i] @ e) for i in range(3))
        rb = sum(hb[i] * abs(ab[i] @ e) for i in range(3))
        ov = ra + rb - abs(t @ e)
        if ov < best:
            best = ov
            if best <= TOL:
                return best
    return best


def main():
    m = MB.montar()
    P = [p for p in m.pecas if not any(k in p.marca.lower() for k in ATRAVESSA)]
    O = [obb(p) for p in P]
    # pré-filtro: grade de 2 m pelas caixas alinhadas das OBB
    cel = collections.defaultdict(list)
    bb = []
    for i, (c, ax, h) in enumerate(O):
        r = sum(np.abs(ax[k]) * h[k] for k in range(3))
        lo, hi = c - r, c + r
        bb.append((lo, hi))
        for gx in range(int(lo[0] // 2), int(hi[0] // 2) + 1):
            for gy in range(int(lo[1] // 2), int(hi[1] // 2) + 1):
                cel[(gx, gy)].append(i)
    vistos, col, cand = set(), [], []
    for lista in cel.values():
        for a_ in range(len(lista)):
            i = lista[a_]
            for j in lista[a_ + 1:]:
                if (i, j) in vistos:
                    continue
                vistos.add((i, j))
                gi, gj = P[i].grupo, P[j].grupo
                if frozenset((gi, gj)) in PARES_OK:
                    continue
                (l1, h1), (l2, h2) = bb[i], bb[j]
                if np.any(l1 > h2 + TOL) or np.any(l2 > h1 + TOL):
                    continue
                d = sat(O[i], O[j])
                if d > TOL:
                    cand.append((i, j))
    # 2ª etapa: interseção EXATA dos sólidos reais (manifold3d) nos pares que as OBB não separaram
    cache = {}
    def S(k):
        if k not in cache:
            cache[k] = solido(P[k])
        return cache[k]
    for i, j in cand:
        inter = S(i) ^ S(j)
        v = inter.volume()
        if v <= 1e-7:                                            # < 0,1 cm³: contato de face / tolerância numérica
            continue
        lo, hi = inter.bounding_box()[:3], inter.bounding_box()[3:]
        esp = min(h_ - l_ for h_, l_ in zip(hi, lo))
        gi, gj = P[i].grupo, P[j].grupo
        if esp * 1000 <= TOL_PAR.get(frozenset((gi, gj)), TOL_MM):
            continue
        col.append(dict(a=P[i].marca, ga=gi, b=P[j].marca, gb=gj, mm=round(esp * 1000, 1), cm3=round(v * 1e6, 1),
                        xyz=[round(float((l_ + h_) / 2), 2) for l_, h_ in zip(lo, hi)]))
    grupos = collections.defaultdict(list)
    for c in col:
        grupos[" × ".join(sorted((c["ga"], c["gb"])))].append(c)
    res = dict(pecas=len(P), colisoes=len(col), por_grupo={k: dict(n=len(v), max_mm=max(x["mm"] for x in v), exemplos=sorted(v, key=lambda x: -x["mm"])[:6])
                                                         for k, v in sorted(grupos.items(), key=lambda kv: -len(kv[1]))})
    (AQ / "colisao_modelo.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(P)} peças testadas, {len(col)} colisões > {TOL_MM:g} mm (telhas × terças > 7 mm)")
    for k, v in res["por_grupo"].items():
        print(f"  {v['n']:5d}  máx {v['max_mm']:7.1f} mm  {k}  ex.: {v['exemplos'][0]['a']} × {v['exemplos'][0]['b']} @ {v['exemplos'][0]['xyz']}")


if __name__ == "__main__":
    main()
