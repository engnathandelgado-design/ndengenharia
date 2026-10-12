"""Isométricos 3D (PyVista) do pilar PL-01 40×60 com consolo, pino, insertos e alças — ISO-PIL-geral.png e ISO-PIL-consolo.png.
Eixos do modelo: x = direção do lado de 60 (face A = x+, consolo; face C = x−, placas), y = lado de 40 (faces B = y+, D = y−),
z = comprimento a partir da base do cálice. Unidades em metros."""
import json, math, sys, numpy as np, pyvista as pv
pv.OFF_SCREEN = True
AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
LG = json.load(open(AQ + "ligacoes.json"))
G = json.load(open("/home/claude/letsara/pranchas/pilar_geom.json"))
B, H, L = G["B"] / 1000, G["H"] / 1000, G["L_TOT"] / 1000
ZC = G["zc"] / 1000                        # topo do consolo a partir da base
CP, CH, CHP = G["cons"]["proj"] / 1000, G["cons"]["h"] / 1000, G["cons"]["hp"] / 1000
I = G["incl"]
PINO_X = G["pino_x"] / 1000
Z_PLACA = [z / 1000 for z in G["z_placa_abs"]]
AL = [z / 1000 for z in G["al"]]
SAIDA = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/letsara/pranchas/"


def box(x0, y0, z0, dx, dy, dz):
    return pv.Box(bounds=(x0, x0 + dx, y0, y0 + dy, z0, z0 + dz))


def prisma(pts_xz, y0, y1):
    """Prisma extrudado em y a partir de um polígono no plano xz."""
    n = len(pts_xz)
    pts = [(x, y0, z) for x, z in pts_xz] + [(x, y1, z) for x, z in pts_xz]
    faces = [n] + list(range(n)) + [n] + list(range(2 * n - 1, n - 1, -1))
    for i in range(n):
        j = (i + 1) % n
        faces += [4, i, j, n + j, n + i]
    return pv.PolyData(np.array(pts), faces)


def cena(p, z0=0.0, z1=L, com_chaves=True):
    conc = dict(color="#c9c9c4", smooth_shading=False, show_edges=True, edge_color="#7a7a7a", line_width=0.6)
    aco = dict(color="#d9822b", show_edges=True, edge_color="#6b3d10", line_width=0.4)
    p.add_mesh(box(-H / 2, -B / 2, z0, H, B, z1 - z0), **conc)
    # consolo CP-TS na face A (x+): topo a 3 % subindo para a ponta
    if z0 <= ZC <= z1:
        poly = [(H / 2, ZC - CH), (H / 2 + CP, ZC - CHP), (H / 2 + CP, ZC + CP * I), (H / 2, ZC)]
        p.add_mesh(prisma(poly, -B / 2, B / 2), **conc)
        # neoprene e pino
        p.add_mesh(box(H / 2 + 0.025, -0.075, ZC + 0.0, 0.25, 0.15, 0.010), color="#202020")
        p.add_mesh(pv.Cylinder(center=(H / 2 + PINO_X, 0, ZC - 0.30 + 0.35), direction=(0, 0, 1), radius=0.010, height=0.70), color="#444444")
    # chaves de cisalhamento no cálice (4 faces)
    if com_chaves:
        for k in range(3):
            zz = 0.15 + k * 0.30
            for face in ("x+", "x-", "y+", "y-"):
                if face[0] == "x":
                    sg = 1 if face[1] == "+" else -1
                    poly = [(sg * H / 2, zz), (sg * (H / 2 + 0.03), zz + 0.04), (sg * (H / 2 + 0.03), zz + 0.16), (sg * H / 2, zz + 0.20)]
                    p.add_mesh(prisma(poly, -B / 2 + 0.05, B / 2 - 0.05), color="#b5b5b0", show_edges=True, edge_color="#7a7a7a")
                else:
                    sg = 1 if face[1] == "+" else -1
                    pts = [(sg * B / 2, zz), (sg * (B / 2 + 0.03), zz + 0.04), (sg * (B / 2 + 0.03), zz + 0.16), (sg * B / 2, zz + 0.20)]
                    n = len(pts)
                    P = [(x, y, z) for y, z in pts for x in (-H / 2 + 0.05,)] + [(x, y, z) for y, z in pts for x in (H / 2 - 0.05,)]
                    faces = [n] + list(range(n)) + [n] + list(range(2 * n - 1, n - 1, -1))
                    for i in range(n):
                        j = (i + 1) % n
                        faces += [4, i, j, n + j, n + i]
                    p.add_mesh(pv.PolyData(np.array(P), faces), color="#b5b5b0", show_edges=True, edge_color="#7a7a7a")
    # insertos IP-01 na face C (x−) e alças AL-2 na face A (x+)
    for z in Z_PLACA:
        if z0 <= z <= z1:
            p.add_mesh(box(-H / 2 - 0.0095, -0.075, z - 0.075, 0.0095, 0.15, 0.15), **aco)
    for z in AL:
        if z0 <= z <= z1:
            t = np.linspace(0, math.pi, 30)
            pts = np.c_[H / 2 + 0.14 * np.sin(t), 0.05 * np.cos(t), z + 0 * t]
            p.add_mesh(pv.Spline(pts, 60).tube(radius=0.0065), color="#8a8a8a")


def rot(p, pts, labs, fs=15):
    p.add_point_labels(np.array(pts), labs, font_size=fs, point_size=8, point_color="#c0392b", text_color="#111111",
                       shape_color="white", shape_opacity=0.85, margin=3, always_visible=True)


# 1) geral — pilar deitado como na fôrma (z no eixo horizontal), face A para cima
p = pv.Plotter(off_screen=True, window_size=(2600, 760)); p.set_background("white")
cena(p)
rot(p, [(H / 2 + CP, 0, ZC + 0.02), (H / 2 + PINO_X, 0, ZC + 0.38), (-H / 2 - 0.01, 0.0, Z_PLACA[2]), (-H / 2 - 0.01, 0.0, Z_PLACA[6]),
        (H / 2 + 0.14, 0, AL[0]), (H / 2 + 0.14, 0, AL[1]), (H / 2 + 0.03, 0, 0.45), (H / 2, B / 2, L - 0.05),
        (H / 2, -B / 2, 1.0), (-H / 2, B / 2, 5.5), (0, B / 2, 3.0)],
    ["consolo CP-TS (face A)", "PN-1 pino Ø20 L=70", "IP-01 (face C, 8x)", "IP-01", "AL-2 alça (içamento)", "AL-2",
     "chaves de cisalhamento (cálice)", "topo +10,000 (platibanda)", "base do cálice", "FACE C (externa, placas)", "FACE B (lado de 40)"])
p.enable_parallel_projection()
p.camera_position = [(-4.0, 12.0, L / 2 - 3.0), (0.0, 0, L / 2), (1, 0, 0)]   # vê as faces C (placas) e B; consolo e alças aparecem acima da silhueta
p.reset_camera(); p.camera.zoom(3.1)
p.add_text(f"PL-01 — pilar 40×60 cm, L = {L*100:.0f} cm (cálice 100 + 1000) · 6,6 t · 6 peças (família PL/PF: 29)", font_size=16, position="upper_left", color="#111111")
p.add_text("projeto da ND Engenharia", font_size=11, position="lower_right", color="#888888")
p.screenshot(SAIDA + "ISO-PIL-geral.png")

# 2) consolo CP-TS em detalhe (pilar em pé)
p = pv.Plotter(off_screen=True, window_size=(1400, 1130), lighting="three lights"); p.set_background("white")
cena(p, ZC - 1.0, ZC + 0.9, com_chaves=False)
rot(p, [(H / 2 + CP, B / 2, ZC + 0.01), (H / 2 + PINO_X, 0.0, ZC + 0.36), (H / 2 + 0.15, 0.07, ZC + 0.01),
        (H / 2 + CP, 0, ZC - CHP), (H / 2 + 0.14, 0, AL[0]), (H / 2, -B / 2, ZC + 0.6), (-H / 2, -B / 2, ZC - 0.6)],
    ["consolo CP-TS 40 × 30 × 45/25 cm", "PN-1 Ø20, 30 cm embutido", "NEO-1 30×15×1 cm (furo Ø30)",
     "chanfro 20 cm na ponta", "AL-2", "FACE A (consolo)", "FACE C"])
p.enable_parallel_projection()
p.camera_position = [(H / 2 + 4.0, -3.4, ZC + 2.3), (H / 2 + 0.1, 0, ZC - 0.1), (0, 0, 1)]
p.reset_camera(); p.camera.zoom(1.5)
p.add_text("Detalhe — consolo CP-TS, pino e neoprene (PL-01, assento +7,914)", font_size=15, position="upper_left", color="#111111")
p.add_text("projeto da ND Engenharia", font_size=11, position="lower_right", color="#888888")
p.screenshot(SAIDA + "ISO-PIL-consolo.png")
print("ok")
