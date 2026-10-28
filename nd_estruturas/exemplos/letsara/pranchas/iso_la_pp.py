"""rev07 (21/10/2026): isométricos sombreados das peças de produção — laje alveolar LA-01/LA-01R e placa protendida PP
(nichos NC-1, luvas TSA, insertos IZ-1, macho-fêmea). PNG em img/, sem marca (projeto da fábrica). Medidas em mm,
das mesmas constantes das pranchas (lajes_placas.py / fechamento.py / geo_fixacao.py)."""
import sys, math
sys.path.insert(0, "/home/claude/letsara/pranchas")
import numpy as np
import pyvista as pv
from shapely.geometry import Polygon, Point, box
from shapely.ops import triangulate

pv.OFF_SCREEN = True
D = "/home/claude/letsara/pranchas/img/"
CONC, ACO, PROT = "#c9c5bd", "#7d8a96", "#c2185b"


def _malha_plana(poly, z=0.0):
    """Polígono shapely (pode ter furos) → malha triangulada no plano z (Delaunay filtrado pelos centróides)."""
    pts = []
    for ring in [poly.exterior] + list(poly.interiors):
        pts += list(ring.coords)[:-1]
    from shapely.geometry import MultiPoint
    tris = [t for t in triangulate(MultiPoint(pts)) if poly.buffer(1e-6).contains(t.centroid)]
    V, F = [], []
    idx = {}
    for t in tris:
        f = []
        for c in list(t.exterior.coords)[:3]:
            k = (round(c[0], 4), round(c[1], 4))
            if k not in idx:
                idx[k] = len(V); V.append((c[0], c[1], z))
            f.append(idx[k])
        F += [3] + f
    return pv.PolyData(np.array(V, float), np.array(F))


def extrudar(poly, L, eixo="x", x0=0.0):
    """Seção poly no plano (u, v) extrudada no comprimento L. eixo='x': u→y, v→z, extrusão em x a partir de x0."""
    if poly.geom_type == "MultiPolygon":
        ms = [extrudar(g, L, eixo, x0) for g in poly.geoms]
        out = ms[0]
        for q in ms[1:]:
            out = out.merge(q)
        return out
    m = _malha_plana(poly).extrude((0, 0, L), capping=True)
    P = m.points.copy()
    m.points = np.c_[P[:, 2] + x0, P[:, 0], P[:, 1]]
    return m


def caixa(x0, x1, y0, y1, z0, z1):
    return pv.Box(bounds=(min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1)))


def cena(objs, arq, cam, titulo, w=1600, h=1000, zoom=1.0, paralela=False):
    p = pv.Plotter(window_size=(w, h)); p.set_background("white")
    for m, c in objs:
        p.add_mesh(m, color=c, smooth_shading=False, specular=0.05, show_edges=False)
        try:
            p.add_mesh(m.extract_feature_edges(25), color="#3a3f44", line_width=1)
        except Exception:
            pass
    p.camera_position = cam
    if paralela:
        p.enable_parallel_projection(); p.reset_camera()
    p.camera.zoom(zoom)
    # rev08: sem título embutido (a folha já tem título e subtítulo; texto pequeno na imagem fica ilegível)
    p.screenshot(arq); p.close()
    return arq


# ------------------------------------------------------------------ laje alveolar (LP20 de referência)
def laje(arq=D + "iso_la01.png", recorte=True):
    """Laje alveolar adotada (calc_laje_alveolar.py → laje_alveolar.json): alvéolos no passo real e uma cordoalha por nervura."""
    import json
    LJ = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/laje_alveolar.json", encoding="utf-8"))
    G = LJ["secao"]
    B, H, NAL, DAL, PAS = round(G["b"] * 1000), round(G["h"] * 1000), G["n_alveolos"], round(G["d_alveolo"] * 1000), G["passo"] * 1000
    sec = Polygon([(0, 0), (B, 0), (B, 40), (B + 25, 60), (B + 25, 150), (B, H), (0, H), (-25, 150), (-25, 60), (0, 40)])
    xa0 = B / 2 - (NAL - 1) * PAS / 2
    furos = sec
    for k in range(NAL):
        furos = furos.difference(Point(xa0 + k * PAS, H / 2).buffer(DAL / 2, 48))
    Lmostra, Lp = 3000, 200                                                      # trecho de 3,0 m; 20 cm de alvéolos fechados na ponta
    PRE = LJ["LA01R"][LJ["LA01R"]["adotado"]]["alveolos_preenchidos"] if recorte else []
    L_pre = 600                                                                   # rev08: alvéolos 2 e 5 cheios 60 cm junto ao recorte (cortante na ponta)
    if PRE:
        cheios = sec
        for k in range(NAL):
            if k + 1 not in PRE:
                cheios = cheios.difference(Point(xa0 + k * PAS, H / 2).buffer(DAL / 2, 48))
        objs = [(extrudar(cheios, L_pre - Lp, x0=Lp), CONC), (extrudar(furos, Lmostra - L_pre, x0=L_pre), CONC)]
    else:
        objs = [(extrudar(furos, Lmostra - Lp, x0=Lp), CONC)]
    if recorte:                                                                   # LA-01R: recorte 45 × 20 na ponta (pilar 40 × 60)
        xr0 = B / 2 - 225
        ponta = sec.difference(box(xr0, -1, xr0 + 450, H + 1))
        objs.append((extrudar(ponta, Lp, x0=0), CONC))
    else:
        objs.append((extrudar(sec, Lp, x0=0), CONC))
    for c in LJ["cordoalhas"]:                                                   # uma cordoalha por nervura (posição real)
        r = 4.75 if c["diam"] == "9.5" else 6.35
        x0c = 0.0 if not recorte or abs(c["x_mm"]) > 225 else Lp
        objs.append((pv.Cylinder(center=((Lmostra + x0c) / 2, B / 2 + c["x_mm"], c["y_mm"]), direction=(1, 0, 0), radius=r * 1.4, height=Lmostra - x0c + 20), PROT))
    n = len(LJ["cordoalhas"])
    from collections import Counter as _Cn                                      # rev12b (item 15): arranjo real (2 nas nervuras de borda)
    _por = _Cn(round(c["x_mm"]) for c in LJ["cordoalhas"])
    arr = "uma por nervura" if max(_por.values()) == 1 else f"uma por nervura interna e {max(_por.values())} em cada nervura de borda"
    tit = (f"LA-01R — laje alveolar h{H / 10:.0f} (trecho de 3,0 m): {NAL} alvéolos, ponta fechada 20 cm, recorte 45 × 20 junto ao pilar; {n} cordoalhas, {arr}" if recorte else
           f"LA-01 — laje alveolar h{H / 10:.0f} (trecho de 3,0 m): {n} cordoalhas, {arr}")
    return cena(objs, arq, [(-2600, -2300, 2100), (900, 620, 60), (0, 0, 1)], tit, zoom=1.45)


# ------------------------------------------------------------------ placa protendida PP (face interna para cima na imagem: y = 0 externa, y = E interna)
def placa(L, arq, ponta=False):
    import geo_fixacao as GF
    E, H = 100, 1250
    NC_B, NC_H, NC_P, Z_NC = GF.N["B"], GF.N["H"], GF.N["P"], 940
    sec = Polygon([(0, 0), (30, 0), (30, 35), (70, 35), (70, 0), (100, 0), (100, 1250), (70, 1250), (70, 1280), (30, 1280), (30, 1250), (0, 1250)])
    nicho = box(E - NC_P, Z_NC - NC_H / 2, E + 1, Z_NC + NC_H / 2)
    sec_ponta = sec.difference(nicho)
    objs = [(extrudar(sec, L - 2 * NC_B, x0=NC_B), CONC), (extrudar(sec_ponta, NC_B, x0=0), CONC), (extrudar(sec_ponta, NC_B, x0=L - NC_B), CONC)]
    # NC-1 (chapas: teto, base, fundo) nas 2 pontas
    for xa in (0, L - NC_B):
        za, zb = Z_NC - NC_H / 2, Z_NC + NC_H / 2
        objs += [(caixa(xa, xa + NC_B, E - NC_P, E, zb - GF.N["t_teto"], zb), ACO), (caixa(xa, xa + NC_B, E - NC_P, E, za, za + GF.N["t_base"]), ACO),
                 (caixa(xa, xa + NC_B, E - NC_P, E - NC_P + GF.N["t_fundo"], za, zb), ACO)]
    # rev11: sem alças AL-P (içamento pelos 4 IZ-1 da face); luvas TSA (topo e base) a 0,21 L + 15 cm (pinos PT-1)
    for xt in (0.21 * L + 150, L - 0.21 * L - 150):
        for zt in (1281, -1):
            objs.append((pv.Cylinder(center=(xt, E / 2, zt), direction=(0, 0, 1), radius=14, height=6), ACO))
    for xa in (0.104 * L, 0.396 * L, L - 0.396 * L, L - 0.104 * L):           # rev08: IZ-1 (desforma por 4 pontos na face interna, meia altura)
        objs.append((pv.Cylinder(center=(xa, E + 2, 625), direction=(0, 1, 0), radius=22, height=6), ACO))
    if ponta:
        cam = [(-1500, 2600, 2300), (250, 50, 820), (0, 0, 1)]
        tit = "PP — ponta da placa (face interna): nicho NC-1 aberto na ponta e na face, macho no topo, fêmea na base"
        return cena(objs, arq, cam, tit, zoom=1.0)
    cam = [(-0.10 * L, 0.95 * L, 0.42 * L), (L / 2, 50, 640), (0, 0, 1)]
    tit = f"PP — placa protendida 125 × 10, L = {L / 10:.1f} cm (face interna): NC-1 nas pontas, 4 IZ-1 de içamento na face e luvas TSA no topo".replace(".", ",")
    return cena(objs, arq, cam, tit, w=1800, h=800, zoom=1.9, paralela=True)


if __name__ == "__main__":
    print(laje(), laje(D + "iso_la01_liso.png", recorte=False), placa(10160, D + "iso_pp_tipica.png"), placa(10160, D + "iso_pp_ponta.png", ponta=True))
