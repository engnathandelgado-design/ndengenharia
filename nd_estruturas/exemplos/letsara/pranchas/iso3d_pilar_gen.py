"""Isométricos (PyVista) de pilar genérico com consolos em qualquer face, pinos, CE-1 e alças — lê pilar_gen_geom.json.
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
    R = G.get("rec")
    if R:
        zr = R["z"] / 1000
        d = {k: v / 1000 for k, v in R["d"].items()}
        if z0 < zr:
            p.add_mesh(box(-H / 2, -B / 2, z0, H, B, min(zr, z1) - z0), **conc)
        if z1 > zr:
            xa, xb = -H / 2 + d.get("C", 0), H / 2 - d.get("A", 0)
            ya, yb = -B / 2 + d.get("D", 0), B / 2 - d.get("B", 0)
            p.add_mesh(box(xa, ya, max(zr, z0), xb - xa, yb - ya, z1 - max(zr, z0)), **conc)
    else:
        p.add_mesh(box(-H / 2, -B / 2, z0, H, B, z1 - z0), **conc)
    labs = []
    VISTOS = set()
    AS = G.get("assento")
    if AS and R and z0 <= R["z"] / 1000 <= z1:                    # DEC-040: pinos PN-3 do assento da TS-01 no recuo
        zr_ = R["z"] / 1000
        xa_ = H / 2 - R["d"].get("A", 0) / 1000
        sai = (AS["L"] - AS["emb"]) / 1000
        for dy in AS["y_pinos"]:
            p.add_mesh(pv.Cylinder(center=(xa_ + AS["x_pino"] / 1000, dy / 1000, zr_ + 0.01 + sai / 2), direction=(0, 0, 1), radius=AS["d"] / 2000, height=sai), color="#b03a2e")
        p.add_mesh(box(xa_ + AS["x_neo"][0] / 1000, -AS["neo"][1] / 2000, zr_, (AS["x_neo"][1] - AS["x_neo"][0]) / 1000, AS["neo"][1] / 1000, 0.01), color="#202020")
        labs.append(((xa_ + AS["x_pino"] / 1000, AS["y_pinos"][-1] / 1000, zr_ + 0.01 + sai), f"assento da viga de cobertura: {len(AS['y_pinos'])} {AS['pino']}"))
    PT = G.get("pinos_topo")
    if PT and z1 >= L - 0.01:                                        # DEC-040: pinos PN-5 no topo (TS-01 apoiada no topo)
        sai = (PT["L"] - PT["emb"]) / 1000
        for x_, y_ in PT["xy"]:
            p.add_mesh(pv.Cylinder(center=(x_ / 1000, y_ / 1000, L + sai / 2), direction=(0, 0, 1), radius=PT["d"] / 2000, height=sai), color="#b03a2e")
        labs.append(((PT["xy"][-1][0] / 1000, PT["xy"][-1][1] / 1000, L + sai), f"{len(PT['xy'])} pinos {PT['nome']} Ø{PT['d']:g} (viga de cobertura)"))
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
        sai = (c["pino_L"] - c["pino_emb"]) / 1000                 # DEC-040: só o trecho saliente aparece, em vermelho, com rótulo
        p.add_mesh(pv.Cylinder(center=(cx, cy, zc + 0.01 + sai / 2), direction=(0, 0, 1), radius=c["pino_d"] / 2000, height=sai), color="#b03a2e")
        if c["pino_nome"] not in VISTOS:
            VISTOS.add(c["pino_nome"]); labs.append(((cx, cy, zc + 0.01 + sai), f"pino {c['pino_nome']} Ø{c['pino_d']:g}"))
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
                x_lat = (-H / 2 + 0.005) if ip.get("aresta_C") else -0.19             # DEC-042: CE-1 junto à aresta da face C (ponta de parede)
                p.add_mesh(box(nx * fd + (0 if nx > 0 else -0.0125 if nx < 0 else x_lat), ny * fd + (0 if ny > 0 else -0.0125 if ny < 0 else -0.19), z - 0.165,
                               0.0125 if nx else 0.38, 0.0125 if ny else 0.38, 0.33), **aco)       # rev06e: CE-1 380 × 330 × 12,5
                for k_, z_ in enumerate(ip["z"]):                                          # rev06e (DEC-031): CS-1 do CC-1 (face C, x−)
                    if ip["face"] != "C" or not ip.get("lados") or abs(z_ / 1000 - z) > 1e-6:
                        continue
                    zt = z + 0.0545
                    fo = fd + 0.0125
                    for ld in ip["lados"][k_]:
                        yc = 0.08 if ld == "E" else -0.08                                      # vista de fora (de x−): esquerda = B = y+
                        p.add_mesh(box(-fo - 0.0095, yc - 0.06, zt - 0.100, 0.0095, 0.12, 0.13), color="#c46a2a")      # costas
                        p.add_mesh(box(-fo - 0.064, yc - 0.052, zt - 0.016, 0.0545, 0.104, 0.016), color="#c46a2a")   # mesa
                        for xa in (-0.045, 0.045):
                            p.add_mesh(box(-fo - 0.064, yc + xa - 0.00315, zt - 0.080, 0.0545, 0.0063, 0.064), color="#c46a2a")   # almas
                        for xd in (0.039, -0.052):
                            p.add_mesh(box(-fo - 0.0635, yc + xd, zt, 0.019, 0.013, 0.035), color="#c46a2a")   # dentes
    FI = G.get("fi")
    if FI:                                                                                  # rev07: furo de içamento FI-1 (tubo Ø60)
        zf_ = FI["z"] / 1000
        if z0 <= zf_ <= z1:
            ax_ = (0, 1, 0) if FI["eixo"] == "BD" else (1, 0, 0)
            Lt = (B if FI["eixo"] == "BD" else H) + 0.012
            p.add_mesh(pv.Cylinder(center=(0, 0, zf_), direction=ax_, radius=FI["d"] / 2000 + 0.004, height=Lt, resolution=40), color="#d9822b")
            p.add_mesh(pv.Cylinder(center=(0, 0, zf_), direction=ax_, radius=FI["d"] / 2000 - 0.002, height=Lt + 0.004, resolution=40), color="#111111")
            labs.append((((0, B / 2 + 0.01, zf_) if FI["eixo"] == "BD" else (-H / 2 - 0.01, 0, zf_)), "FI-1 furo de içamento"))
    for z in G.get("al", []):
        z = z / 1000
        if z0 <= z <= z1:
            t = np.linspace(0, math.pi, 30)
            sx = -1 if G.get("al_face", "A") == "C" else 1                                # rev06e: AL-2 na face C (de cima na fôrma)
            pts = np.c_[sx * (H / 2 + 0.14 * np.sin(t)), 0.05 * np.cos(t), z + 0 * t]
            p.add_mesh(pv.Spline(pts, 60).tube(radius=0.009), color="#3a6ea5")
            labs.append(((sx * (H / 2 + 0.14), 0, z), "AL-2 alça"))
    for ip in G.get("ip01", []):
        nx, ny = FACE_N[ip["face"]]
        fd = H / 2 if nx else B / 2
        zs_ = [z / 1000 for z in ip["z"] if z0 <= z / 1000 <= z1]
        if zs_:
            labs.append(((nx * (fd + 0.07), ny * (fd + 0.07), zs_[-1]), ("CC-1 (CS-1 de fábrica)" if ip["face"] == "C" and ip.get("lados") else "CE-1") + f" face {ip['face']} ×{len(ip['z'])}"))
    if R and z1 > zr:
        labs.append(((-H / 2 + d.get("C", 0), 0, (zr + L) / 2), "cabeça recuada"))
    return labs


def rot(p, pts, labs, fs=23):
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
import renomear as _RN
_NM = _RN.lista(_RN.nomes_de(G["marca"]))
p.add_text(f"{G['marca']} ({_NM}) em pé", font_size=23, position="upper_left", color="#111111")
p.screenshot(SAIDA + f"ISO-{G['marca']}-geral.png")

# rev07: duas vistas (frente C/B e costas A/D), para a produção
p = pv.Plotter(off_screen=True, shape=(1, 2), window_size=(1500, 2600), border=False); p.set_background("white")
for k_, (cam, nome_v) in enumerate((((-9.0, 7.5, L / 2 + 2.5), "faces C e B"), ((9.0, -7.5, L / 2 + 2.5), "faces A e D"))):
    p.subplot(0, k_)
    labs = cena(p)
    rot(p, [l[0] for l in labs], [l[1] for l in labs], fs=30)
    p.enable_parallel_projection()
    p.camera_position = [cam, (0.0, 0, L / 2), (0, 0, 1)]
    p.reset_camera(); p.camera.zoom(G.get("zoom", 3.2) * 1.0)
    p.add_text(f"{G['marca']} ({_NM}) — {nome_v}", font_size=30, position="upper_left", color="#111111")
pass
p.screenshot(SAIDA + f"ISO-{G['marca']}-2v.png")

c0 = G["consolos"][0] if G["consolos"] else None
zc = c0["z"] / 1000 if c0 else L - 0.9
p = pv.Plotter(off_screen=True, window_size=(1400, 1130), lighting="three lights"); p.set_background("white")
labs = cena(p, zc - 1.0, zc + 0.9, chaves=False)
rot(p, [l[0] for l in labs], [l[1] for l in labs])
p.enable_parallel_projection()
p.camera_position = [(H / 2 + 4.0, -3.4, zc + 2.3), (0, 0, zc - 0.1), (0, 0, 1)]
p.reset_camera(); p.camera.zoom(1.3)
p.add_text(f"Detalhe — {'consolos' if c0 else 'topo e insertos'} do {G['marca']}", font_size=26, position="upper_left", color="#111111")
p.screenshot(SAIDA + f"ISO-{G['marca']}-consolo.png")
print("ok")
