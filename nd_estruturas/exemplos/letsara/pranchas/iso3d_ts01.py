"""Isométrico 3D (PyVista) — TS-01 com chaparia nomeada. Gera ISO-TS01-geral.png e ISO-TS01-ponta.png."""
import json, math, numpy as np, pyvista as pv
pv.OFF_SCREEN = True
LG = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/ligacoes.json"))
L, H, MAC, HD, LN = LG["L_TS"], 0.90, 1.20, 0.45, 0.30
TERCAS = LG["s_tercas"]
NOS = [TERCAS[k] for k in range(0, 13, 2)]
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
    nib = [(-0.2, HD), (0.2, HD), (0.2, H), (-0.2, H)]
    if x_ini < MAC:
        p.add_mesh(extrude(nib, 0.0, LN, skew=False), **conc)
        p.add_mesh(extrude(rb, LN, MAC, skew=False), **conc)
    p.add_mesh(extrude(SEC, max(MAC, x_ini), min(L - MAC, x_fim), skew=False), **conc)
    if x_fim > L - MAC:
        p.add_mesh(extrude(rb, L - MAC, L - LN, skew=False), **conc)
        p.add_mesh(extrude(nib, L - LN, L, skew=False), **conc)
    for s in TERCAS[1:-1]:                                     # CH-MF no fundo (plano da terça)
        if x_ini <= s <= x_fim:
            p.add_mesh(box(s - 0.027 - 0.075, -0.18, -0.0125, 0.15, 0.36, 0.0125), **aco)
    lab_pts, labs = [], []
    for k, s in enumerate(TERCAS):
        if not (x_ini <= s <= x_fim):
            continue
        no = any(abs(s - n) < 1e-6 for n in NOS)
        w = 0.30 if no else 0.20
        p.add_mesh(box(s - w / 2, -0.06 if not no else -0.10, H, w, 0.12 if not no else 0.20, 0.0125), **aco)
    for s in ALCAS:
        if x_ini <= s <= x_fim:
            t = np.linspace(0, math.pi, 30)
            pts = np.c_[s + 0.06 * np.cos(t), 0 * t, H + 0.14 * np.sin(t)]
            p.add_mesh(pv.Spline(pts, 60).tube(radius=0.009), color="#8a8a8a")
    for s in (0.15, L - 0.15):
        if x_ini <= s <= x_fim:
            p.add_mesh(pv.Cylinder(center=(s + 0.0135, 0, (H + HD) / 2), direction=(0.03, 0, 1), radius=0.025, height=H - HD + 0.02),
                       color="#5a5a5a", opacity=0.55)
            p.add_mesh(box(s - 0.075, -0.15, HD - 0.0125, 0.15, 0.30, 0.0125), **aco)
            p.add_mesh(box(s - 0.075, -0.15, HD - 0.0225, 0.15, 0.30, 0.010), color="#202020")
            p.add_mesh(pv.Cylinder(center=(s, 0, HD - 0.10), direction=(0, 0, 1), radius=0.0125, height=0.16), color="#444444")
            # consolo do pilar (topo no fundo do dente − neoprene), folga de 25 mm até a face do dente
            xs_ = -0.025 if s < L / 2 else L + 0.025
            dx_ = 0.30 if s < L / 2 else -0.30
            p.add_mesh(pv.Box(bounds=(min(xs_, xs_ + dx_), max(xs_, xs_ + dx_), -0.2, 0.2, HD - 0.46, HD - 0.0225)),
                       color="#b9b4a8", opacity=0.45)


def rot(p, pts, labs):
    p.add_point_labels(np.array(pts), labs, font_size=15, point_size=8, point_color="#c0392b", text_color="#111111",
                       shape_color="white", shape_opacity=0.85, margin=3, always_visible=True)


# 1) geral
p = pv.Plotter(off_screen=True, window_size=(2400, 900)); p.set_background("white")
cena(p)
rot(p, [(ALCAS[0], 0, H + 0.14), (ALCAS[1], 0, H + 0.14), (TERCAS[3], 0, H + 0.0125), (NOS[2], 0, H + 0.0125),
        (TERCAS[9] - 0.027, 0.18, -0.0125), (L - 0.15, 0.2, HD), (0.15, 0.2, 0.70)],
    ["AL-1 (4 alças de cordoalha)", "AL-1", "CH-T1 (terça)", "CH-T2 (terça + contraventamento)",
     "CH-MF no fundo (mão-francesa)", "dente + CH-A1 + neoprene + pino", "dente Gerber / ponta a prumo"])
p.enable_parallel_projection()
p.camera_position = [(L * 0.5 - 8, -14, 9), (L * 0.5, 0, 0.45), (0, 0, 1)]
p.reset_camera(); p.camera.zoom(2.3)
p.add_text(f"TS-01 — viga I90 de cobertura com dentes Gerber · {L*1000:.0f} mm · 11,6 t · 14 peças".replace(",", ".").replace(".6 t", ",6 t"), font_size=16, position="upper_left", color="#111111")
p.add_text("projeto da ND Engenharia", font_size=11, position="lower_right", color="#888888")
p.screenshot("/home/claude/letsara/pranchas/ISO-TS01-geral.png")
# 2) ponta com terça, cantoneira, mão-francesa e contraventamento
p = pv.Plotter(off_screen=True, window_size=(1500, 1200)); p.set_background("white")
cena(p, 0, 3.6)
for s in (TERCAS[0], TERCAS[1], TERCAS[2]):
    for sg in (1, -1):
        p.add_mesh(box(s - 0.0425, 0.04 if sg > 0 else -1.6, H + 0.0125, 0.085, 1.56, 0.30), color="#9fb6cc", show_edges=True, edge_color="#446666")
        p.add_mesh(box(s - 0.11, -0.06, H + 0.0125, 0.065, 0.12, 0.10), color="#4f6f93")
        if s < LN:                                    # 1ª terça: mão-francesa na CH-MF2, face lateral do dente
            pts = np.array([(s, sg * 0.21, HD + 0.075), (s, sg * 0.60, H + 0.0125)])
        else:                                         # demais: CH-MF no fundo da viga, 45°
            pts = np.array([(s - 0.027, sg * 0.15, -0.0125), (s, sg * 1.07, H + 0.0125)])
        p.add_mesh(pv.Line(*pts).tube(radius=0.012), color="#2f4f6f")
for sg in (1, -1):
    p.add_mesh(pv.Line((NOS[0], sg * 0.12, H + 0.02), (NOS[1], sg * 1.6, H + 0.02)).tube(radius=0.007), color="#b03a2e")
rot(p, [(TERCAS[1], 0.8, H + 0.32), (TERCAS[1] - 0.08, -0.03, H + 0.11), (TERCAS[1] - 0.01, 0.6, 0.45),
        (1.2, 0.85, H + 0.03), (0.15, 0.2, HD - 0.2), (TERCAS[1] - 0.027, -0.15, -0.0125), (0.3, -0.2, 0.2)],
    ["terça Ue 300×85×25×3,00", "cantoneira CT-1 (2 M16 na CH-T1)", "mão-francesa L50×5 (do fundo da viga até a terça)",
     "contraventamento Ø12,5 A36 (CH-T2)", "consolo + neoprene + pino PN-1", "CH-MF + orelha OR-1", "dente Gerber"])
p.enable_parallel_projection()
p.camera_position = [(-3.2, -5.4, 1.6), (1.5, 0, 0.45), (0, 0, 1)]
p.reset_camera(); p.camera.zoom(1.1)
p.add_text("Detalhe A — ponta, apoio, terças e contraventamento", font_size=15, position="upper_left", color="#111111")
p.add_text("projeto da ND Engenharia", font_size=11, position="lower_right", color="#888888")
p.screenshot("/home/claude/letsara/pranchas/ISO-TS01-ponta.png")
print("ok")
