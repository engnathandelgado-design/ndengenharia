"""iso_nd.py — isométricos vetoriais (montado e explodido com balões) e símbolos de fabricação para as pranchas ND.

Sólidos em mm (prismas convexos: faces planas com normal para fora). O desenho sai no DXF da prancha (hachura sólida
com cor real por sombreamento + arestas), na ordem do pintor, numa Vista do prancha_nd (mesma escala, título e
verificação de sobreposição). Também: símbolo de solda (AWS A2.4 / ISO 2553, seta + linha de referência), balão de
item, rosca em vista e em furo.
"""
from __future__ import annotations
import math
import numpy as np

AZUL_ACO = (168, 184, 200)
CINZA_PAR = (128, 128, 138)
DOURADO = (196, 170, 98)
CONCRETO = (214, 212, 202)
VERDE = (150, 186, 150)


class Solido:
    def __init__(self, faces, item=None, cor=AZUL_ACO, nome="", liso=False):
        self.faces = [np.array(f, float) for f in faces]
        self.item, self.cor, self.nome, self.liso = item, cor, nome, liso
        c = np.vstack(self.faces).mean(0)
        self.centro = c
        self.normais = []
        for f in self.faces:
            n = np.cross(f[1] - f[0], f[2] - f[0])
            if np.linalg.norm(n) < 1e-9 and len(f) > 3:
                n = np.cross(f[2] - f[0], f[3] - f[0])
            n = n / (np.linalg.norm(n) or 1)
            if np.dot(n, f.mean(0) - c) < 0:
                n = -n
            self.normais.append(n)

    def movido(self, d):
        return Solido([f + np.array(d, float) for f in self.faces], self.item, self.cor, self.nome, self.liso)


def caixa(x0, x1, y0, y1, z0, z1, **kw):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    F = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return Solido([[v[i] for i in f] for f in F], **kw)


def prisma(poli2d, plano, a0, a1, **kw):
    """polígono convexo no plano ('xy','yz','xz') extrudado de a0 a a1 no eixo normal."""
    def P(u, v, w):
        if plano == "xy":
            return (u, v, w)
        if plano == "yz":
            return (w, u, v)
        return (u, w, v)                                  # xz: (x, z) e extrusão em y
    base = [P(u, v, a0) for u, v in poli2d]
    topo = [P(u, v, a1) for u, v in poli2d]
    faces = [base, topo]
    n = len(poli2d)
    for i in range(n):
        j = (i + 1) % n
        faces.append([base[i], base[j], topo[j], topo[i]])
    return Solido(faces, **kw)


def cilindro(c, eixo, r, h, n=20, hexa=False, **kw):
    """cilindro (ou prisma hexagonal com r = metade da distância entre cantos) a partir do centro da base c, ao longo de eixo (x/y/z)."""
    kw.setdefault("liso", not hexa)
    m = 6 if hexa else n
    pts = [(r * math.cos(2 * math.pi * k / m + (math.pi / 6 if hexa else 0)), r * math.sin(2 * math.pi * k / m + (math.pi / 6 if hexa else 0))) for k in range(m)]
    cx, cy, cz = c
    if eixo == "z":
        return prisma([(cx + u, cy + v) for u, v in pts], "xy", cz, cz + h, **kw)
    if eixo == "y":
        return prisma([(cx + u, cz + v) for u, v in pts], "xz", cy, cy + h, **kw)
    return prisma([(cy + u, cz + v) for u, v in pts], "yz", cx, cx + h, **kw)


def barra_poli(pts, d, n=8, **kw):
    """barra redonda ao longo de uma polilinha (segmentos ortogonais), como prismas de n lados."""
    out = []
    for p, q in zip(pts[:-1], pts[1:]):
        p, q = np.array(p, float), np.array(q, float)
        L = np.linalg.norm(q - p)
        ax = int(np.argmax(np.abs(q - p)))
        a = "xyz"[ax]
        c0 = p if q[ax] > p[ax] else q
        out.append(cilindro(tuple(c0), a, d / 2, L, n=n, **kw))
    return out


class Camera:
    def __init__(self, direcao=(-1.0, -1.2, 0.9), luz=(-0.4, -0.8, 1.0)):
        d = np.array(direcao, float); d /= np.linalg.norm(d)
        f = -d
        up0 = np.array((0, 0, 1.0))
        r = np.cross(f, up0); r /= np.linalg.norm(r)
        u = np.cross(r, f)
        self.d, self.r, self.u = d, r, u
        L = np.array(luz, float); self.L = L / np.linalg.norm(L)

    def proj(self, p):
        p = np.asarray(p, float)
        return float(p @ self.r), float(p @ self.u)

    def prof(self, p):
        return float(np.asarray(p, float) @ self.d)


def _cor(c, n, cam):
    k = 0.42 + 0.58 * max(0.0, float(n @ cam.L))
    k += 0.10 * max(0.0, float(n @ cam.d))
    k = min(k, 1.08)
    return tuple(int(max(0, min(255, round(ch * k)))) for ch in c)


def desenhar_iso(vista, solidos, cam: Camera, origem2d=(0.0, 0.0), arestas=True):
    """Desenha os sólidos numa Vista (coordenadas de modelo = projeção em mm). Retorna o mapeamento proj().
    Sólidos 'lisos' (cilindros): só as arestas de contorno (silhueta) e das tampas visíveis."""
    pr = vista.pr
    faces = []
    for s in solidos:
        vis = [float(n @ cam.d) > 1e-6 for n in s.normais]
        aresta_faces = {}
        if s.liso:
            for i, f in enumerate(s.faces):
                for k in range(len(f)):
                    key = tuple(sorted((tuple(np.round(f[k], 4)), tuple(np.round(f[(k + 1) % len(f)], 4)))))
                    aresta_faces.setdefault(key, []).append(i)
        for i, (f, n) in enumerate(zip(s.faces, s.normais)):
            if not vis[i]:
                continue
            ed = None
            if s.liso:
                ed = []
                for k in range(len(f)):
                    key = tuple(sorted((tuple(np.round(f[k], 4)), tuple(np.round(f[(k + 1) % len(f)], 4)))))
                    outras = [j for j in aresta_faces.get(key, []) if j != i]
                    if len(f) > 4 or not outras or not all(vis[j] for j in outras):
                        ed.append((f[k], f[(k + 1) % len(f)]))
            faces.append((max(cam.prof(p) for p in f) * 0.25 + cam.prof(f.mean(0)) * 0.75, f, n, s, ed))
    faces.sort(key=lambda t: t[0])
    ox, oy = origem2d
    pj = lambda p: (cam.proj(p)[0] + ox, cam.proj(p)[1] + oy)
    for _, f, n, s, ed in faces:
        pts = [pj(p) for p in f]
        h = pr.msp.add_hatch(dxfattribs={"layer": "HACHURA"})
        h.set_solid_fill(color=7, rgb=_cor(s.cor, n, cam))
        h.paths.add_polyline_path([vista.P(p) for p in pts], is_closed=True)
        vista._add(h)
        if not arestas:
            continue
        if ed is None:
            vista.poli(pts, "VISTA", fechada=True)
        else:
            for p_, q_ in ed:
                vista.linha(pj(p_), pj(q_), "VISTA")
    return pj


def balao(vista, p_modelo, desloc_papel, num, r=3.6):
    """balão de item (círculo com número) com linha de chamada até um ponto da peça."""
    x0, y0 = vista.P(p_modelo)
    bx, by = x0 + desloc_papel[0], y0 + desloc_papel[1]
    L = math.hypot(bx - x0, by - y0) or 1
    ux, uy = (bx - x0) / L, (by - y0) / L
    msp = vista.pr.msp
    vista._add(msp.add_line((x0, y0), (bx - ux * r, by - uy * r), dxfattribs={"layer": "COTA"}))
    vista._add(msp.add_circle((x0, y0), 0.6, dxfattribs={"layer": "COTA"}))
    vista._add(msp.add_circle((bx, by), r, dxfattribs={"layer": "COTA"}))
    vista._add(vista.pr.texto(bx, by, str(num), 3.0, "COTA", "MIDDLE_CENTER"))


def solda(vista, p_modelo, desloc_papel, a=None, tipo="filete", lado="seta", contorno=False, campo=False, cauda=None, comp=None):
    """Símbolo de solda: seta até a junta, linha de referência horizontal, símbolo básico (filete = triângulo,
    chanfro = bisel 1/2 V, ponto = tampão) do lado da seta (abaixo) ou do outro lado (acima) ou nos dois,
    dimensão à esquerda, comprimento à direita, círculo de solda em todo o contorno, bandeira de solda de campo e cauda."""
    pr, msp = vista.pr, vista.pr.msp
    x0, y0 = vista.P(p_modelo)
    ex, ey = x0 + desloc_papel[0], y0 + desloc_papel[1]
    sg = 1 if desloc_papel[0] >= 0 else -1
    Lr = 22.0
    xr1 = ex + sg * Lr
    ad = lambda e: vista._add(e)
    ad(msp.add_line((ex, ey), (x0, y0), dxfattribs={"layer": "COTA"}))
    ang = math.atan2(y0 - ey, x0 - ex)
    for s_ in (1, -1):
        ad(msp.add_line((x0, y0), (x0 - 2.2 * math.cos(ang + s_ * 0.33), y0 - 2.2 * math.sin(ang + s_ * 0.33)), dxfattribs={"layer": "COTA"}))
    ad(msp.add_line((ex, ey), (xr1, ey), dxfattribs={"layer": "COTA"}))
    xs = ex + sg * 9.0                                   # posição do símbolo na linha de referência
    def simb(up):
        k = 1 if up else -1
        if tipo == "filete":
            pts = [(xs - 1.6, ey), (xs - 1.6, ey + k * 3.0), (xs + 1.6, ey)]
        elif tipo == "chanfro":
            pts = [(xs - 1.4, ey), (xs - 1.4, ey + k * 3.2), (xs - 1.4, ey), (xs + 1.8, ey + k * 3.2)]
        else:
            pts = [(xs - 1.8, ey), (xs - 1.8, ey + k * 2.2), (xs + 1.8, ey + k * 2.2), (xs + 1.8, ey)]
        ad(msp.add_lwpolyline(pts, dxfattribs={"layer": "COTA"}))
        if a is not None:
            t = pr.texto(xs - 2.6, ey + k * 1.6, str(a).replace(".", ","), 2.2, "COTA", "MIDDLE_RIGHT")
            ad(t)
        if comp:
            ad(pr.texto(xs + 2.6, ey + k * 1.6, str(comp), 2.2, "COTA", "MIDDLE_LEFT"))
    if lado in ("seta", "ambos"):
        simb(False)
    if lado in ("outro", "ambos"):
        simb(True)
    if contorno:
        ad(msp.add_circle((ex, ey), 1.4, dxfattribs={"layer": "COTA"}))
    if campo:
        ad(msp.add_line((ex, ey), (ex, ey + 5.0), dxfattribs={"layer": "COTA"}))
        ad(msp.add_lwpolyline([(ex, ey + 5.0), (ex + sg * 3.2, ey + 4.0), (ex, ey + 3.0)], close=True, dxfattribs={"layer": "COTA"}))
    if cauda:
        ad(msp.add_line((xr1, ey), (xr1 + sg * 2.2, ey + 2.2), dxfattribs={"layer": "COTA"}))
        ad(msp.add_line((xr1, ey), (xr1 + sg * 2.2, ey - 2.2), dxfattribs={"layer": "COTA"}))
        ad(pr.texto(xr1 + sg * 3.0, ey, cauda, 2.2, "COTA", "MIDDLE_LEFT" if sg > 0 else "MIDDLE_RIGHT"))


def furo_roscado(vista, c, d_nom, camada="VISTA"):
    """furo roscado em vista de topo: diâmetro menor contínuo e 3/4 de arco no diâmetro nominal (traço fino)."""
    r_min = (d_nom - 1.0825 * 2.0 * (d_nom / 16)) / 2 if d_nom >= 10 else 0.42 * d_nom
    vista.circulo(c, r_min, camada)
    x, y = vista.P(c)
    vista._add(vista.pr.msp.add_arc((x, y), d_nom / 2 / vista.esc, 0, 270, dxfattribs={"layer": "COTA"}))


def parafuso_lateral(vista, x0, y0, L, d, cabeca=None, sentido=1, comp_rosca=None, eixo="x"):
    """parafuso em vista lateral: corpo no diâmetro nominal, linhas finas da rosca no diâmetro menor, cabeça sextavada
    (k, s) opcional. eixo 'x': corpo de x0 a x0 + sentido·L na altura y0; eixo 'y': vertical."""
    p = 2.0 if d >= 16 else 1.75 if d >= 12 else 1.5
    dmin = d - 1.2269 * p
    cr = L if comp_rosca is None else comp_rosca
    def P(a, b):
        return (a, b) if eixo == "x" else (b, a)
    s = sentido
    pts = [P(x0, y0 - d / 2), P(x0 + s * L, y0 - d / 2), P(x0 + s * L, y0 + d / 2), P(x0, y0 + d / 2)]
    vista.poli(pts, "METALICA", fechada=True)
    for yy in (y0 - dmin / 2, y0 + dmin / 2):
        vista.linha(P(x0 + s * (L - cr), yy), P(x0 + s * L, yy), "COTA")
    if cabeca:
        k, sw = cabeca
        e = sw / math.cos(math.pi / 6)
        hp = [P(x0, y0 - e / 2), P(x0 - s * k, y0 - e / 2), P(x0 - s * k, y0 + e / 2), P(x0, y0 + e / 2)]
        vista.poli(hp, "METALICA", fechada=True)
        for yy in (y0 - e / 4, y0 + e / 4):
            vista.linha(P(x0, yy), P(x0 - s * k, yy), "VISTA")


def porca_lateral(vista, x0, y0, m, sw, eixo="x"):
    e = sw / math.cos(math.pi / 6)
    def P(a, b):
        return (a, b) if eixo == "x" else (b, a)
    vista.poli([P(x0, y0 - e / 2), P(x0 + m, y0 - e / 2), P(x0 + m, y0 + e / 2), P(x0, y0 + e / 2)], "METALICA", fechada=True)
    for yy in (y0 - e / 4, y0 + e / 4):
        vista.linha(P(x0, yy), P(x0 + m, yy), "VISTA")


def hexagono(vista, c, sw, camada="METALICA", rot=0.0):
    e = sw / math.cos(math.pi / 6) / 2
    pts = [(c[0] + e * math.cos(math.radians(60 * k + rot)), c[1] + e * math.sin(math.radians(60 * k + rot))) for k in range(6)]
    vista.poli(pts, camada, fechada=True)
