"""Isométricos 3D (PyVista) das vigas I120, VB e VM para a produção ver a peça inteira (rev08, 21/10/2026).
Projeto da fábrica: imagens SEM marca. Gera ISO-I120-geral/ponta, ISO-VB-geral/ponta, ISO-VM-geral (PNG recortados).
Uso: python iso3d_vigas.py [i130 vb vm]"""
import json, math, sys
import numpy as np
import pyvista as pv
from PIL import Image, ImageChops

pv.OFF_SCREEN = True
sys.path.insert(0, "/home/claude/letsara/pranchas")
AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
sys.path.insert(0, AQ)
PR = "/home/claude/letsara/pranchas/"
CONC = dict(color="#c9c9c4", show_edges=True, edge_color="#7a7a7a", line_width=0.6)
PIL_ = dict(color="#b5b5ae", show_edges=True, edge_color="#6a6a6a", line_width=0.6)
ACO = dict(color="#d9822b", show_edges=True, edge_color="#6b3d10", line_width=0.4)
NEO = dict(color="#202020")
ALCA = dict(color="#8a8a8a")
ARM = dict(color="#c2185b")


def prisma(poly, a0, a1, plano="xz"):
    """polígono 2D extrudado: plano 'xz' (perfil lateral, extrudado em y de a0 a a1) ou 'yz' (seção, extrudada em x)."""
    n = len(poly)
    if plano == "xz":
        pts = [(u, a0, v) for u, v in poly] + [(u, a1, v) for u, v in poly]
    else:
        pts = [(a0, u, v) for u, v in poly] + [(a1, u, v) for u, v in poly]
    faces = [n] + list(range(n)) + [n] + list(range(2 * n - 1, n - 1, -1))
    for i in range(n):
        j = (i + 1) % n
        faces += [4, i, j, n + j, n + i]
    return pv.PolyData(np.array(pts, float), faces).triangulate()


def box(x0, x1, y0, y1, z0, z1):
    return pv.Box(bounds=(min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1)))


def cil(c, d, h, dirc=(0, 0, 1)):
    return pv.Cylinder(center=c, direction=dirc, radius=d / 2, height=h, resolution=24)


def alca(p, x, y, z, w=0.12, h=0.14, sentido="x"):
    t = np.linspace(0, math.pi, 30)
    if sentido == "x":
        pts = np.c_[x + w / 2 * np.cos(t), 0 * t + y, z + h * np.sin(t)]
    else:
        pts = np.c_[0 * t + x, y + w / 2 * np.cos(t), z + h * np.sin(t)]
    p.add_mesh(pv.Spline(pts, 60).tube(radius=0.009), **ALCA)


def rot(p, pts, labs, fs=38):
    p.add_point_labels(np.array(pts, float), labs, font_size=fs, point_size=8, point_color="#c0392b", text_color="#111111",
                       shape_color="white", shape_opacity=0.85, margin=3, always_visible=True)


def salvar(p, arq, cam, zoom):
    p.enable_parallel_projection()
    p.camera_position = cam
    p.reset_camera()
    p.camera.zoom(zoom)
    # rev11: enquadra a peça para ocupar ~90 % da janela (antes a viga longa ocupava ~1/3 e o recorte saía com 52–100 ppi)
    a_ = np.asarray(p.screenshot(None, return_img=True))[..., :3]
    ys_, xs_ = np.nonzero((a_ < 250).any(axis=2))
    if len(xs_):
        W_, H_ = a_.shape[1], a_.shape[0]
        cam_ = p.camera                                                       # 1) centraliza o desenho na janela (pan em projeção paralela)
        px_ = 2 * cam_.parallel_scale / H_                                    # metros por pixel
        dx_ = ((xs_.min() + xs_.max()) / 2 - W_ / 2) * px_
        dy_ = -((ys_.min() + ys_.max()) / 2 - H_ / 2) * px_
        fp_, pos_, up_ = np.array(cam_.focal_point), np.array(cam_.position), np.array(cam_.up)
        dir_ = fp_ - pos_; dir_ /= np.linalg.norm(dir_)
        up_ = up_ - dir_ * (up_ @ dir_); up_ /= np.linalg.norm(up_)
        rt_ = np.cross(dir_, up_)
        sh_ = rt_ * dx_ + up_ * dy_
        cam_.focal_point, cam_.position = tuple(fp_ + sh_), tuple(pos_ + sh_)
        fx, fy = (xs_.max() - xs_.min() + 1) / W_, (ys_.max() - ys_.min() + 1) / H_   # 2) zoom para ocupar ~92 %
        k_ = 0.92 / max(fx, fy)
        if k_ > 1.05:
            cam_.zoom(k_)
        p.render()
    p.screenshot(PR + arq, scale=2)                                      # rev11: ≥ 400 ppi no tamanho impresso
    im = Image.open(PR + arq).convert("RGB")
    bb = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
    im.crop((max(bb[0] - 20, 0), max(bb[1] - 20, 0), min(bb[2] + 20, im.width), min(bb[3] + 20, im.height))).save(PR + arq)
    p.close()
    print("ok", arq)


# ================================================================== I120 (V406)
def i130():
    import viga_i as VI
    P = VI.dados_i110()
    L, H, B, BW, TS, TI, M_ = P["L"] / 1e3, P["h"] / 1e3, P["b"] / 1e3, P["bw"] / 1e3, P["ts"] / 1e3, P["ti"] / 1e3, P["m"] / 1e3
    HD, LN = P["dente"][0] / 1e3, P["dente"][1] / 1e3
    MAC = P["x_mac"] / 1e3
    sec = [(x / 1e3, y / 1e3) for x, y in VI.sec_pts(P["b"], P["h"], P["ts"], P["ti"], P["m"], P["bw"])]
    rb = [(-B / 2, 0), (B / 2, 0), (B / 2, H), (-B / 2, H)]
    nariz = [(-B / 2, H - HD), (B / 2, H - HD), (B / 2, H), (-B / 2, H)]

    def peca(p, x_ini=0.0, x_fim=L):
        for a, b, s in ((0, LN, nariz), (LN, MAC, rb), (MAC, L - MAC, sec), (L - MAC, L - LN, rb), (L - LN, L, nariz)):
            a2, b2 = max(a, x_ini), min(b, x_fim)
            if b2 > a2:
                p.add_mesh(prisma(s, a2, b2, "yz"), **CONC)
        for xp in (P["pino_x"] / 1e3, L - P["pino_x"] / 1e3):            # TB-2 no nariz
            if x_ini <= xp <= x_fim:
                p.add_mesh(cil((xp, 0, H - HD / 2), P["tb"][0] / 1e3, HD + 0.01), color="#5a5a5a", opacity=0.6)
        for s in P["alcas"]:
            if x_ini <= s / 1e3 <= x_fim:
                for dy in (-0.06, 0.0, 0.06):
                    alca(p, s / 1e3, dy, H, w=0.10, h=0.14)
        for s0 in P["pinos_topo"]:
            s0 /= 1e3
            if not (x_ini <= s0 <= x_fim):
                continue
            CT = P.get("ct")
            if CT:                                                     # rev10 (DEC-061): consolo lateral CT-I120 com mísula nas 2 faces
                pj, hh, he = CT["proj"] / 1e3, CT["h"] / 1e3, CT["h_ext"] / 1e3
                for sg in (-1, 1):
                    pol = [(sg * BW / 2, H - hh), (sg * B / 2, H - hh), (sg * (B / 2 + pj), H - he), (sg * (B / 2 + pj), H), (sg * BW / 2, H)]
                    p.add_mesh(prisma(pol if sg > 0 else pol[::-1], s0 - CT["b"] / 2e3, s0 + CT["b"] / 2e3, "yz"), **CONC)
                    yn = sg * CT["y_neo"] / 1e3
                    p.add_mesh(box(s0 - 0.15, s0 + 0.15, yn - CT["a_neo"] / 2e3, yn + CT["a_neo"] / 2e3, H, H + 0.01), **NEO)
            for dn in (-0.115, 0.115):
                if not CT:
                    p.add_mesh(box(s0 + dn - 0.05, s0 + dn + 0.05, -0.15, 0.15, H, H + 0.01), **NEO)
                for ds in (-0.10, 0.10):
                    p.add_mesh(cil((s0 + ds, dn, H + 0.15), 0.020, 0.30), **ACO)
    p = pv.Plotter(off_screen=True, window_size=(2600, 900)); p.set_background("white")
    peca(p)
    s0 = P["pinos_topo"][0] / 1e3
    rot(p, [(P["alcas"][0] / 1e3, 0, H + 0.14), (s0 + 0.115, 0.10, H + 0.30), (LN / 2, 0.2, H - HD), (P["pino_x"] / 1e3, 0, H + 0.02), (MAC + 1.0, 0.2, H * 0.5)],
        ["AL-3 alça de içamento (2x)", "apoio das vigas de cobertura: consolos CT-I120 com mísula + NEO-3C + 4 PN-5", f"dente Gerber {HD*100:.0f} × {LN*100:.0f}",
         "TB-2 passante no dente", f"seção I{round(H * 100)} (b 40, bw 15)"], fs=23)
    salvar(p, "ISO-I120-geral.png", [(L * 0.5 - 6, -15, 11), (L * 0.5, 0, H * 0.5), (0, 0, 1)], 1.05)
    # ponta no consolo CP-I120 do pilar central
    p = pv.Plotter(off_screen=True, window_size=(1500, 1200)); p.set_background("white")
    F = 0.075                                                                              # ponta da viga a 75 mm da face do pilar
    p.add_mesh(box(-0.60 - F, -F, -0.30, 0.30, -1.2, H + 0.25), **PIL_)                    # pilar 60 × 60 (até o topo da viga)
    PJ = 0.40                                                                              # projeção do CP-I120 (consolos.json): termina 25 mm antes do corpo da viga
    _CJ = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/consolos.json"))["CP-I120"]   # DEC-054: consolo com mísula
    _zt = H - HD - 0.031
    p.add_mesh(prisma([(-F, _zt - _CJ["h_total_m"]), (-F + PJ, _zt - _CJ["h_consolo_m"]), (-F + PJ, _zt), (-F, _zt)], -0.25, 0.25, "xz"), **PIL_)   # consolo
    p.add_mesh(box(P["pino_x"] / 1e3 - 0.10, P["pino_x"] / 1e3 + 0.10, -0.15, 0.15, H - HD - 0.031, H - HD), **NEO)   # NEO-2 fretado
    p.add_mesh(cil((P["pino_x"] / 1e3, 0, H - HD + 0.05), 0.025, 0.60), **ACO)                # PN-2
    peca(p, 0, 3.2)
    rot(p, [(P["pino_x"] / 1e3, 0.15, H - HD - 0.015), (P["pino_x"] / 1e3, 0, H - HD + 0.35), (PJ / 2, 0.30, H - HD - 0.4), (-0.3, 0.3, H)],
        ["NEO-2 300×200×31 fretado", "PN-2 Ø25 no TB-2 (graute numa ponta)", "consolo CP-I120 com mísula (49 / 39)", "pilar central PC"])
    salvar(p, "ISO-I120-ponta.png", [(3.2, -4.6, -0.2), (0.6, 0, H * 0.4), (0, 0, 1)], 1.1)   # DEC-054: vista um pouco de baixo (mísula do consolo)


# ================================================================== VB (VB-02)
def vb():
    import vb_geom as VG
    from cob_comum import XT
    from geometria import X_EIXO
    VBD = json.load(open(AQ + "vb_dente.json"))["adotado"]
    B, H = VBD["b"], VBD["h"]
    xa, xb = X_EIXO["B"], X_EIXO["C"]
    x0 = round((xa + 0.20 + 0.025) * 1000)
    Lmm = round((xb - 0.20 - 0.025) * 1000) - x0
    perf = [(u / 1e3, v / 1e3) for u, v in VG.peca(Lmm)]
    es = []
    for w in XT:
        pp = [w - 105 - x0, w - 45 - x0]
        if 40 <= pp[0] and pp[1] <= Lmm - 40:
            es += [v / 1e3 for v in pp]
    L = perf[5][0]
    XP = VG.XP / 1e3

    LNm, RECm = VG.LN / 1e3, VG.REC / 1e3

    def peca(p, ui=-1.0, uf=99.0):
        for a, b, z0 in ((0, LNm, RECm), (LNm, L - LNm, 0.0), (L - LNm, L, RECm)):     # nariz / corpo / nariz (3 % desprezível no 3D)
            a2, b2 = max(a, ui), min(b, uf)
            if b2 > a2:
                p.add_mesh(box(a2, b2, -B / 2, B / 2, z0, H), **CONC)
        for u in es:
            if ui <= u <= uf:
                p.add_mesh(cil((u, 0, H + 0.06), 0.016, 0.12), **ACO)
        for s in (1.5, L - 1.5):
            if ui <= s <= uf:
                alca(p, s, 0, H)
        for u in (XP, L - XP):
            if ui <= u <= uf:
                p.add_mesh(cil((u, 0, (VG.REC / 1e3 + H) / 2), 0.050, H - VG.REC / 1e3 - 0.06), color="#5a5a5a", opacity=0.6)
                p.add_mesh(box(u - 0.06, u + 0.06, -0.06, 0.06, H - 0.06, H), color="#7fb3d5", opacity=0.5)
    p = pv.Plotter(off_screen=True, window_size=(2400, 800)); p.set_background("white")
    peca(p)
    rot(p, [(es[2], 0, H + 0.12), (1.5, 0, H + 0.14), (VG.LN / 2e3, B / 2, VG.REC / 1e3), (XP, 0, H)],
        ["ES-1V: 2 esperas M16 por terça (ST-1V)", "AL-1 alça (2x)", "dente 30 × 27 (consolo CP-VB escondido)", "TB-1 + nicho do PN-6"], fs=23)
    salvar(p, "ISO-VB-geral.png", [(L * 0.5 - 5, -12, 9), (L * 0.5, 0, H * 0.5), (0, 0, 1)], 1.05)
    p = pv.Plotter(off_screen=True, window_size=(1400, 1100)); p.set_background("white")
    F = 0.075                                                                              # ponta da viga a 75 mm da face do pilar
    p.add_mesh(box(-0.40 - F, -F, -0.25, 0.25, -0.8, H + 0.4), **PIL_)
    zc = VG.REC / 1e3 - 0.010
    p.add_mesh(box(-F, -F + 0.27, -B / 2, B / 2, zc - 0.29, zc), **PIL_)                    # CP-VB 15 × 27 × 29
    p.add_mesh(box(XP - 0.05, XP + 0.05, -0.05, 0.05, zc, zc + 0.010), **NEO)
    p.add_mesh(cil((XP, 0, zc + 0.05), 0.020, 0.70), **ACO)
    peca(p, 0, 2.2)
    rot(p, [(XP, 0.05, zc + 0.005), (XP, 0, H + 0.02), (0.13, B / 2, zc - 0.15), (-0.2, 0.25, H)],
        ["NEO-6 100×100×10", "PN-6 Ø20 roscado + porca (nicho grauteado)", "consolo CP-VB escondido no recorte", "pilar de fachada"])
    salvar(p, "ISO-VB-ponta.png", [(3.2, -3.4, 1.8), (0.4, 0, H * 0.4), (0, 0, 1)], 1.1)


# ================================================================== VM (VM-02) peça inteira — rev09: retangular 30 × 75 (DEC-049)
def vm():
    VMJ = json.load(open(AQ + "vm_retangular.json"))
    P = VMJ["premissas"]
    H, B = P["h_pm"], P["b"]
    HD, LN = P["dente"]["hd"], P["dente"]["ln"]
    REC = H - HD
    L = VMJ["VM-02"]["L_peca"]
    ye, yi = -B / 2, B / 2
    b2 = B - 0.12                                                                       # faixa de 2º estágio (alças), lado da borda
    p = pv.Plotter(off_screen=True, window_size=(2400, 800)); p.set_background("white")
    for a, b in ((0, LN), (L - LN, L)):
        p.add_mesh(box(a, b, ye, yi, REC, H), **CONC)                                     # nariz do dente
    p.add_mesh(box(LN, L - LN, ye, yi, 0, H), **CONC)                                     # corpo
    x = 0.15
    while x < L - 0.10:
        for yy in (ye + 0.03, ye + b2 - 0.03):
            p.add_mesh(cil((x, yy, H + 0.10), 0.010, 0.20), **ARM)
        p.add_mesh(cil((x, ye + b2 / 2, H + 0.20), 0.010, b2 - 0.06, (0, 1, 0)), **ARM)
        x += 0.15
    for s in (1.1, L - 1.1):
        alca(p, s, 0.0, H, w=0.12, h=0.13)
    for u in (P["x_pad"] - 0.03, L - P["x_pad"] + 0.03):
        p.add_mesh(cil((u, 0.0, REC + HD / 2), 0.050, HD + 0.01), color="#5a5a5a", opacity=0.6)
    rot(p, [(L * 0.5, ye + b2 / 2, H + 0.20), (L * 0.35, yi, H - 0.02), (L * 0.6, ye, H * 0.4), (LN / 2, yi, REC), (1.1, 0.0, H + 0.13)],
        ["N9 alças Ø10 c/15 (2º estágio, lado da borda)", "apoio da laje 10 cm (topo)", f"retangular {B*100:.0f} × {H*100:.0f} protendida", f"dente {HD*100:.0f} × {LN*100:.0f}", "AL-1 alça (2x)"], fs=23)
    salvar(p, "ISO-VM-geral.png", [(L * 0.5 - 5, -10, 9), (L * 0.5, 0, H * 0.5), (0, 0, 1)], 1.05)


if __name__ == "__main__":
    for a in (sys.argv[1:] or ["i130", "vb", "vm"]):
        globals()[a]()
