"""Isométricos (PyVista) de pilar genérico com consolos em qualquer face, pinos, IP-01 e alças — lê pilar_gen_geom.json.
Faces: A = x+, B = y+, C = x−, D = y−. Unidades m. Saída: ISO-<marca>-geral.png e ISO-<marca>-consolo.png"""
import json, math, sys, numpy as np, pyvista as pv
pv.OFF_SCREEN = True
G = json.load(open(sys.argv[1]))
SAIDA = sys.argv[2]
B, H, L = G["B"] / 1000, G["H"] / 1000, G["L_TOT"] / 1000
FACE_N = {"A": (1, 0), "B": (0, 1), "C": (-1, 0), "D": (0, -1)}


def box(x0, y0, z0, dx, dy, dz):
    return pv.Box(bounds=(x0, x0 + dx, y0, y0 + dy, z0, z0 + dz))


def prisma(pts2, eixo_u, eixo_v, w0, w1, origem):
    """polígono no plano (u = saliência, v = altura) extrudado na largura w (perpendicular)."""
    n = len(pts2)
    P = []
    for w in (w0, w1):
        for u, v in pts2:
            P.append((origem[0] + eixo_u[0] * u + eixo_v[0] * w, origem[1] + eixo_u[1] * u + eixo_v[1] * w, v))
    faces = [n] + list(range(n)) + [n] + list(range(2 * n - 1, n - 1, -1))
    for i in range(n):
        j = (i + 1) % n
        faces += [4, i, j, n + j, n + i]
    return pv.PolyData(np.array(P), faces)


def cena(p, z0=0.0, z1=L, chaves=True):
    conc = dict(color="#c9c9c4", smooth_shading=False, show_edges=True, edge_color="#7a7a7a", line_width=0.6)
    aco = dict(color="#d9822b", show_edges=True, edge_color="#6b3d10", line_width=0.4)
    p.add_mesh(box(-H / 2, -B / 2, z0, H, B, z1 - z0), **conc)
    labs = []
    for c in G["consolos"]:
        nx, ny = FACE_N[c["face"]]
        zc = c["z"] / 1000
        proj, h, hp, larg = c["proj"] / 1000, c["h"] / 1000, c["hp"] / 1000, c["larg"] / 1000
        incl = c.get("incl", 0.03)
        face_d = (H / 2 if nx else B / 2)
        if not (z0 <= zc <= z1):
            continue
        poly = [(face_d, zc - h), (face_d + proj, zc - hp), (face_d + proj, zc + proj * incl), (face_d, zc)]
        eu, ev = (nx, ny), (-ny, nx)
        p.add_mesh(prisma(poly, eu, ev, -larg / 2, larg / 2, (0, 0)), **conc)
        px = c["pino_x"] / 1000
        cx, cy = nx * (face_d + px), ny * (face_d + px)
        p.add_mesh(pv.Cylinder(center=(cx, cy, zc + 0.05), direction=(0, 0, 1), radius=c["pino_d"] / 2000, height=c["pino_L"] / 1000), color="#444444")
        nw, nl = c["neo"][0] / 1000, c["neo"][1] / 1000
        p.add_mesh(box(nx * face_d + (0.025 if nx > 0 else -nl - 0.025 if nx < 0 else -nw / 2), ny * face_d + (0.025 if ny > 0 else -nl - 0.025 if ny < 0 else -nw / 2), zc,
                       nl if nx else nw, nw if nx else nl, 0.01), color="#202020")
        labs.append(((nx * (face_d + proj), ny * (face_d + proj), zc + 0.02), f"{c['tipo']} (face {c['face']})"))
    if chaves:
        for k in range(3):
            zz = 0.15 + k * 0.30
            for f_, (nx, ny) in FACE_N.items():
                fd = H / 2 if nx else B / 2
                poly = [(fd, zz), (fd + 0.03, zz + 0.04), (fd + 0.03, zz + 0.16), (fd, zz + 0.20)]
                wl = (B / 2 if nx else H / 2) - 0.05
                p.add_mesh(prisma(poly, (nx, ny), (-ny, nx), -wl, wl, (0, 0)), color="#b5b5b0", show_edges=True, edge_color="#7a7a7a")
    for ip in G.get("ip01", []):
        nx, ny = FACE_N[ip["face"]]
        fd = H / 2 if nx else B / 2
        for z in ip["z"]:
            z = z / 1000
            if z0 <= z <= z1:
                p.add_mesh(box(nx * fd + (0 if nx > 0 else -0.0095 if nx < 0 else -0.075), ny * fd + (0 if ny > 0 else -0.0095 if ny < 0 else -0.075), z - 0.075,
                               0.0095 if nx else 0.15, 0.0095 if ny else 0.15, 0.15), **aco)
    for z in G.get("al", []):
        z = z / 1000
        if z0 <= z <= z1:
            t = np.linspace(0, math.pi, 30)
            pts = np.c_[H / 2 + 0.14 * np.sin(t), 0.05 * np.cos(t), z + 0 * t]
            p.add_mesh(pv.Spline(pts, 60).tube(radius=0.0065), color="#8a8a8a")
    return labs


def rot(p, pts, labs, fs=13):
    if pts:
        p.add_point_labels(np.array(pts), labs, font_size=fs, point_size=8, point_color="#c0392b", text_color="#111111",
                           shape_color="white", shape_opacity=0.85, margin=3, always_visible=True)


p = pv.Plotter(off_screen=True, window_size=(760, 2600)); p.set_background("white")
labs = cena(p)
pts = [l[0] for l in labs] + [(0, B / 2, L), (0, B / 2, 1.0), (-H / 2, 0, L * 0.45), (0, B / 2, L * 0.3)]
txt = [l[1] for l in labs] + [f"topo +{G['z_topo']:.3f}", "piso ±0,000", "FACE C", "FACE B"]
rot(p, pts, txt)
p.enable_parallel_projection()
p.camera_position = [(-9.0, 7.5, L / 2 + 2.5), (0.0, 0, L / 2), (0, 0, 1)]
p.reset_camera(); p.camera.zoom(G.get("zoom", 3.2))
p.add_text(f"{G['marca']} em pé", font_size=13, position="upper_left", color="#111111")
p.add_text("projeto da ND Engenharia", font_size=9, position="lower_left", color="#888888")
p.screenshot(SAIDA + f"ISO-{G['marca']}-geral.png")

c0 = G["consolos"][0]
zc = c0["z"] / 1000
p = pv.Plotter(off_screen=True, window_size=(1400, 1130), lighting="three lights"); p.set_background("white")
labs = cena(p, zc - 1.0, zc + 0.9, chaves=False)
rot(p, [l[0] for l in labs], [l[1] for l in labs])
p.enable_parallel_projection()
p.camera_position = [(H / 2 + 4.0, -3.4, zc + 2.3), (0, 0, zc - 0.1), (0, 0, 1)]
p.reset_camera(); p.camera.zoom(1.3)
p.add_text(f"Detalhe — consolos do {G['marca']}", font_size=15, position="upper_left", color="#111111")
p.add_text("projeto da ND Engenharia", font_size=11, position="lower_right", color="#888888")
p.screenshot(SAIDA + f"ISO-{G['marca']}-consolo.png")
print("ok")
