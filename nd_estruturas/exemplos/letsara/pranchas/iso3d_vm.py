"""Isométrico 3D (PyVista) — ponta da VM RETANGULAR 30 × 75 (rev09, DEC-048) com dente Gerber no consolo CP-MEZ: pilar,
consolo, NEO-5F, pino PN-1, junta da ponta concretada, alças N9, 2º estágio (transparente) e laje alveolar apoiada 10 cm no
topo da viga. Gera ISO-VM-ponta.png (sem marca: projeto da fábrica)."""
import json, numpy as np, pyvista as pv
pv.OFF_SCREEN = True
P = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/vm_retangular.json"))["premissas"]
H, B = P["h_pm"], P["b"]
D = P["dente"]
HD, LN, REC, HC, PRJ = D["hd"], D["ln"], D["recorte"], D["consolo_h"], D["consolo_proj"]
FOL, XP = 0.03, P["x_pad"]
LV = 2.2
ye, yi = -B / 2, B / 2
b2 = B - 0.12
box = lambda x0, x1, y0, y1, z0, z1: pv.Box(bounds=(x0, x1, y0, y1, z0, z1))
conc = dict(color="#c9c9c4", show_edges=True, edge_color="#7a7a7a", line_width=0.6)
pil = dict(color="#b5b5ae", show_edges=True, edge_color="#6a6a6a", line_width=0.6)
p = pv.Plotter(window_size=(1600, 1200), off_screen=True)
p.set_background("white")
x0, zb = 0.0, 0.0
p.add_mesh(box(-0.43, x0, -0.30, 0.30, -0.4, H + 0.45), **pil)                               # pilar
_bc, _hf = P.get("b_consolo", B), D.get("consolo_h_face", HC)                # rev12: largura da VM e mísula
_pp = [(x0, zb + HC - _hf), (x0 + PRJ, zb), (x0 + PRJ, zb + HC), (x0, zb + HC)]
_pts = [(x_, y_, z_) for y_ in (-_bc / 2, _bc / 2) for x_, z_ in _pp]
_fc = [4, 0, 1, 2, 3, 4, 7, 6, 5, 4] + sum(([4, i, (i + 1) % 4, 4 + (i + 1) % 4, 4 + i] for i in range(4)), [])
p.add_mesh(pv.PolyData(np.array(_pts), _fc), **pil)                              # CP-MEZ, fundo alinhado
p.add_mesh(box(x0 + XP - 0.10, x0 + XP + 0.10, -0.10, 0.10, zb + HC, zb + HC + 0.021), color="#222222")   # NEO-5F 200 × 200
xa = x0 + FOL
p.add_mesh(box(xa, xa + LN, ye, yi, zb + REC, zb + H), **conc)                                # nariz do dente
p.add_mesh(box(xa + LN, xa + LV, ye, yi, zb, zb + H), **conc)                                 # corpo
p.add_mesh(pv.Cylinder(center=(x0 + XP, 0.0, zb + HC + 0.085), direction=(0, 0, 1), radius=0.010, height=0.63), color="#444444")   # PN-1 L 630 (230 no consolo)
x = xa + 0.075
while x < xa + LV - 0.05:
    for yy in (ye + 0.03, ye + b2 - 0.03):
        p.add_mesh(pv.Cylinder(center=(x, yy, zb + H + 0.10), direction=(0, 0, 1), radius=0.005, height=0.20), color="#c2185b")
    p.add_mesh(pv.Cylinder(center=(x, ye + b2 / 2, zb + H + 0.20), direction=(0, 1, 0), radius=0.005, height=b2 - 0.06), color="#c2185b")
    x += 0.15
for k in range(2):
    xx = xa + 0.30 + k * 1.25
    p.add_mesh(box(xx, xx + 1.24, yi - 0.10, yi + 1.6, zb + H + 0.01, zb + H + 0.21), color="#e3e0d4", show_edges=True, edge_color="#8a8670", opacity=0.9)
p.add_mesh(box(x0, xa + LV, ye, ye + b2, zb + H, zb + H + 0.26), color="#7fb3d5", opacity=0.25)    # 2º estágio (até o topo da capa)
p.add_mesh(box(xa - FOL, xa, ye, yi, zb + REC, zb + H), color="#5b8fc7", opacity=0.6)        # junta da ponta concretada antes das lajes (DEC-039)
p.camera_position = [(2.3, -2.6, 0.05), (0.55, 0.1, 0.40), (0, 0, 1)]
p.screenshot("/home/claude/letsara/pranchas/ISO-VM-ponta.png", scale=3)          # rev11: ≥ 400 ppi
print("ok")
