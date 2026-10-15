"""Isométrico 3D (PyVista) — TS-01 com chaparia nomeada. Gera ISO-TS01-geral.png e ISO-TS01-ponta.png."""
import json, math, numpy as np, pyvista as pv
pv.OFF_SCREEN = True
LG = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/ligacoes.json"))
L, H, MAC = LG["L_TS"], 0.90, 1.20
TERCAS = LG["s_tercas"]
NOS = [TERCAS[k] for k in range(0, len(TERCAS), 2)]
ALCAS = LG["alcas"]
SEC = [(-0.20, 0), (0.20, 0), (0.20, 0.15), (0.075, 0.23), (0.075, 0.70), (0.20, 0.78), (0.20, 0.90),
       (-0.20, 0.90), (-0.20, 0.78), (-0.075, 0.70), (-0.075, 0.23), (-0.20, 0.15)]
DX = H * 0.03          # ponta a prumo: topo deslocado 27 mm


def extrude(sec, x0, x1, skew=True):
    pts = []
    for x in (x0, x1):
        for y, z in sec:
            pts.append((x + (z * 0.03 if skew and x in (0.0, L) else 0), y, z))
    n = len(sec)
    faces = [n] + list(range(n)) + [n] + list(range(2 * n - 1, n - 1, -1))
    for i in range(n):
        j = (i + 1) % n
        faces += [4, i, j, n + j, n + i]
    return pv.PolyData(np.array(pts), faces)


def box(x0, y0, z0, dx, dy, dz):
    return pv.Box(bounds=(x0, x0 + dx, y0, y0 + dy, z0, z0 + dz))


def cena(p, x_ini=0, x_fim=L):
    conc = dict(color="#c9c9c4", smooth_shading=False, show_edges=True, edge_color="#7a7a7a", line_width=0.6)
    aco = dict(color="#d9822b", show_edges=True, edge_color="#6b3d10", line_width=0.4)
    rb = [(-0.2, 0), (0.2, 0), (0.2, H), (-0.2, H)]
    if x_ini < MAC:
        p.add_mesh(extrude(rb, 0.0, MAC, skew=False), **conc)
    p.add_mesh(extrude(SEC, max(MAC, x_ini), min(L - MAC, x_fim), skew=False), **conc)
    if x_fim > L - MAC:
        p.add_mesh(extrude(rb, L - MAC, L, skew=False), **conc)
    for s in TERCAS:
        if not (x_ini <= s <= x_fim):
            continue
        for yy in (-0.06, 0.06):                                  # ES-1 (ST-1P)
            p.add_mesh(pv.Cylinder(center=(s - 0.075, yy, H + 0.06), direction=(0, 0, 1), radius=0.008, height=0.12), **aco)
        for sg in (-1, 1):                                        # ES-3 (mão-francesa), lateral, 100 do fundo
            p.add_mesh(pv.Cylinder(center=(s - 0.025, sg * 0.23, 0.10), direction=(0, 1, 0), radius=0.008, height=0.06), **aco)
        if any(abs(s - n) < 1e-6 for n in NOS):                   # ES-2 (OR-X)
            for so in (-0.14, 0.14):
                for yy in (-0.14, 0.14):
                    p.add_mesh(pv.Cylinder(center=(s + so, yy, H + 0.025), direction=(0, 0, 1), radius=0.008, height=0.05), **aco)
    for s in ALCAS:
        if x_ini <= s <= x_fim:
            t = np.linspace(0, math.pi, 30)
            pts = np.c_[s + 0.06 * np.cos(t), 0 * t, H + 0.14 * np.sin(t)]
            p.add_mesh(pv.Spline(pts, 60).tube(radius=0.009), color="#8a8a8a")
    for s, neo in ((0.14, 0.20), (L - 0.0775, 0.10)):              # TB-3 (2 por ponta) + neoprene
        if x_ini <= s <= x_fim:
            for yy in (-0.10, 0.10):
                p.add_mesh(pv.Cylinder(center=(s + 0.0135, yy, H / 2), direction=(0.03, 0, 1), radius=0.025, height=H + 0.01),
                           color="#5a5a5a", opacity=0.55)
            p.add_mesh(box(s - neo / 2, -0.15, -0.010, neo, 0.30, 0.010), color="#202020")


def rot(p, pts, labs):
    p.add_point_labels(np.array(pts), labs, font_size=15, point_size=8, point_color="#c0392b", text_color="#111111",
                       shape_color="white", shape_opacity=0.85, margin=3, always_visible=True)


# 1) geral
p = pv.Plotter(off_screen=True, window_size=(2400, 900)); p.set_background("white")
cena(p)
rot(p, [(ALCAS[0], 0, H + 0.14), (TERCAS[3] - 0.075, 0.06, H + 0.12), (NOS[2] + 0.14, 0.14, H + 0.05),
        (TERCAS[9] - 0.025, 0.26, 0.10), (L - 0.0775, 0.2, 0.0), (0.14, 0.2, 0.0)],
    ["AL-1 (4 alças de cordoalha)", "ES-1: 2 esperas M16 do ST-1P (terça)", "ES-2: esperas das orelhas OR-X (nó do X)",
     "ES-3: esperas M16 da mão-francesa", "apoio no topo da I130: NEO-3 + 2 TB-3", "apoio no pilar: NEO-4 + 2 TB-3 (sem dente)"])
p.enable_parallel_projection()
p.camera_position = [(L * 0.5 - 8, -14, 9), (L * 0.5, 0, 0.45), (0, 0, 1)]
p.reset_camera(); p.camera.zoom(2.3)
p.add_text(f"TS-01 — viga I90 de cobertura sem dentes · {L*100:.1f} cm · 12,0 t · 14 peças".replace(".", ","), font_size=16, position="upper_left", color="#111111")
p.add_text("projeto da ND Engenharia", font_size=11, position="lower_right", color="#888888")
p.screenshot("/home/claude/letsara/pranchas/ISO-TS01-geral.png")
from PIL import Image, ImageChops
im = Image.open("/home/claude/letsara/pranchas/ISO-TS01-geral.png").convert("RGB")
bb = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
im.crop((max(bb[0] - 20, 0), max(bb[1] - 20, 0), min(bb[2] + 20, im.width), min(bb[3] + 20, im.height))).save("/home/claude/letsara/pranchas/ISO-TS01-geral-crop.png")
print("ok")

# 2) ponta: terças, ST-1P, mão-francesa (CMF-1 + MF-1) e X (OR-X) — tudo parafusado
p = pv.Plotter(off_screen=True, window_size=(1500, 1200)); p.set_background("white")
cena(p, 0, 3.0)
for s in (TERCAS[0], TERCAS[1], TERCAS[2]):
    for sg in (1, -1):
        p.add_mesh(box(s - 0.0425, 0.005 if sg > 0 else -1.6, H + 0.010, 0.085, 1.595, 0.30), color="#9fb6cc", show_edges=True, edge_color="#446666")
        pts = np.array([(s - 0.025, sg * 0.26, 0.10), (s - 0.025, sg * 1.07, H + 0.05)])
        p.add_mesh(pv.Line(*pts).tube(radius=0.012), color="#2f4f6f")
        p.add_mesh(box(s - 0.065, sg * 0.23 - 0.003, 0.06, 0.08, 0.006, 0.076), color="#4f6f93")
    p.add_mesh(box(s - 0.15, -0.11, H, 0.15, 0.22, 0.0095), color="#4f6f93")
    p.add_mesh(box(s - 0.0525, -0.11, H, 0.0095, 0.22, 0.29), color="#4f6f93")
for so in (0.14, -0.14):
    for yy in (0.14, -0.14):
        p.add_mesh(box(TERCAS[0] + so - 0.04, yy - 0.003, H, 0.08, 0.006, 0.102), color="#b03a2e")
for sg in (1, -1):
    p.add_mesh(pv.Line((TERCAS[0] + 0.14, sg * 0.14, H + 0.045), (TERCAS[2] - 0.14, sg * 1.6, H + 0.045)).tube(radius=0.008), color="#b03a2e")
p.add_mesh(pv.Box(bounds=(-0.30, -0.025, -0.2, 0.2, -0.7, H + 0.9)), color="#b9b4a8", opacity=0.45)
p.add_mesh(pv.Box(bounds=(-0.025, 0.30, -0.2, 0.2, -0.7, -0.010)), color="#b9b4a8", opacity=0.45)
rot(p, [(TERCAS[1], 0.8, H + 0.32), (TERCAS[1] - 0.08, 0.0, H + 0.30), (TERCAS[1] - 0.025, 0.7, 0.55),
        (1.2, 0.85, H + 0.05), (0.14, 0.2, -0.01), (TERCAS[1] - 0.03, 0.23, 0.08), (-0.15, 0.2, H + 0.4)],
    ["terça Ue 300×85×25×2,65", "ST-1P (chapa dobrada) nas esperas ES-1", "mão-francesa MF-1 L50×5",
     "X Ø16 nas orelhas OR-X (ES-2)", "assento do pilar: NEO-4 + 2 PN-3", "CMF-1 na espera ES-3", "cabeça do pilar"])
p.enable_parallel_projection()
p.camera_position = [(-3.2, -5.4, 2.4), (1.3, 0, 0.55), (0, 0, 1)]
p.reset_camera(); p.camera.zoom(1.15)
p.add_text("Ponta da TS-01: apoio, terças, ST-1P, mão-francesa e X — sem solda", font_size=15, position="upper_left", color="#111111")
p.add_text("projeto da ND Engenharia", font_size=11, position="lower_right", color="#888888")
p.screenshot("/home/claude/letsara/pranchas/ISO-TS01-ponta.png")
im = Image.open("/home/claude/letsara/pranchas/ISO-TS01-ponta.png").convert("RGB")
bb = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
im.crop((max(bb[0] - 20, 0), max(bb[1] - 20, 0), min(bb[2] + 20, im.width), min(bb[3] + 20, im.height))).save("/home/claude/letsara/pranchas/ISO-TS01-ponta-crop.png")
print("ok2")
