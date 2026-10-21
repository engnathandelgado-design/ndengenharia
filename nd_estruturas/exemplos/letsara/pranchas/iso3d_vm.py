"""Isométrico 3D (PyVista) — ponta da VM meio vaso com dente Gerber no consolo CP-MEZ: pilar, consolo, NEO-5, pino PN-1,
cantoneira CT-1, alças N9, 2º estágio (transparente) e laje alveolar. Gera ISO-VM-ponta.png (sem marca: projeto da fábrica)."""
import json, math, numpy as np, pyvista as pv
pv.OFF_SCREEN = True
P = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/vm_meio_vaso.json"))["premissas"]
H, BA, BB, HA = P["h_pm"], P["b_alma"], P["b_aba"], P["h_aba"]
D = P["dente"]
HD, LN, REC, HC, PRJ, MAC = D["hd"], D["ln"], D["recorte"], D["consolo_h"], D["consolo_proj"], D["macico"]
B = BA + BB
FOL, XP = 0.03, 0.186
LV = 2.2                                       # trecho desenhado da viga (m)
ye, yw, yi = -B / 2, -B / 2 + BA, B / 2         # face externa (alma), face interna da alma, face interna da aba
box = lambda x0, x1, y0, y1, z0, z1: pv.Box(bounds=(x0, x1, y0, y1, z0, z1))
conc = dict(color="#c9c9c4", show_edges=True, edge_color="#7a7a7a", line_width=0.6)
pil = dict(color="#b5b5ae", show_edges=True, edge_color="#6a6a6a", line_width=0.6)
aco = dict(color="#d9822b", show_edges=True, edge_color="#6b3d10", line_width=0.4)
p = pv.Plotter(window_size=(1600, 1200), off_screen=True)
p.set_background("white")
x0 = 0.0                                        # face do pilar
zb = 0.0                                        # fundo da VM = fundo do consolo
p.add_mesh(box(-0.43, x0, -0.30, 0.30, -0.4, H + 0.45), **pil)                               # pilar (40 na direção da viga)
p.add_mesh(box(x0, x0 + PRJ, -B / 2, B / 2, zb, zb + HC), **pil)                              # CP-MEZ, fundo alinhado
p.add_mesh(box(x0 + XP - 0.075, x0 + XP + 0.075, -0.15, 0.15, zb + HC, zb + HC + 0.01), color="#222222")   # NEO-5
xa = x0 + FOL
# viga: nariz (largura total) + recorte; alma; aba; ponta maciça
p.add_mesh(box(xa, xa + MAC, ye, yi, zb + REC, zb + H), **conc)                               # ponta maciça acima do recorte (nariz)
p.add_mesh(box(xa + LN, xa + MAC, ye, yi, zb, zb + REC), **conc)                              # ponta maciça abaixo
p.add_mesh(box(xa + MAC, xa + LV, ye, yw, zb, zb + H), **conc)                                # alma
p.add_mesh(box(xa + MAC, xa + LV, yw, yi, zb + H - HA, zb + H), **conc)                        # aba
p.add_mesh(pv.Cylinder(center=(x0 + XP, 0.0, zb + HC + 0.30), direction=(0, 0, 1), radius=0.010, height=0.70), color="#444444")   # PN-1
# CT-1 na face externa (lado da alma), parafusada no trilho do pilar e na bucha da viga
p.add_mesh(box(x0, x0 + 0.152, ye - 0.0125, ye, zb + H - 0.15, zb + H), **aco)
p.add_mesh(box(x0, x0 + 0.0125, ye - 0.102, ye, zb + H - 0.15, zb + H), **aco)
# alças N9 (U invertido saindo 20 cm), a cada 15 cm
x = xa + 0.075
while x < xa + LV - 0.05:
    z0 = zb + (REC if x < xa + LN else 0) + 0.035
    for yy in (ye + 0.04, yw - 0.04):
        p.add_mesh(pv.Cylinder(center=(x, yy, zb + H + 0.10), direction=(0, 0, 1), radius=0.005, height=0.20), color="#c2185b")
    p.add_mesh(pv.Cylinder(center=(x, (ye + yw) / 2, zb + H + 0.20), direction=(0, 1, 0), radius=0.005, height=BA - 0.08), color="#c2185b")
    x += 0.15
# laje alveolar (2 painéis) apoiada 10 cm na aba, fita de neoprene, e 2º estágio transparente
for k in range(2):
    xx = xa + 0.30 + k * 1.25
    p.add_mesh(box(xx, xx + 1.24, yi - 0.10, yi + 1.6, zb + H + 0.01, zb + H + 0.21), color="#e3e0d4", show_edges=True, edge_color="#8a8670", opacity=0.9)
p.add_mesh(box(x0, xa + LV, ye, yi - 0.10, zb + H, zb + H + 0.21), color="#7fb3d5", opacity=0.25)
p.add_mesh(box(xa - FOL, xa, ye, yi, zb + REC, zb + H), color="#7fb3d5", opacity=0.35)       # junta grauteada
p.camera_position = [(2.3, -2.6, 0.05), (0.55, 0.1, 0.40), (0, 0, 1)]
p.screenshot("/home/claude/letsara/pranchas/ISO-VM-ponta.png")
print("ok")
