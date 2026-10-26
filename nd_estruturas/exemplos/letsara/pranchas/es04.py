"""ND-LET-ES04 (escada interna) e ND-LET-ES05 (escada externa) — rev10 (Nathan 25/10/2026): detalhamento de fabricação e montagem do
GUARDA-CORPO e do CORRIMÃO DUPLO no nível da prancha de referência que ele mandou (perspectiva com chamadas dos detalhes, vista
superior, vista lateral com o guarda-corpo cotado nos montantes, detalhes 1:20 do guarda-corpo e do corrimão duplo, corte e peças
1:5, detalhes de fixação 1–3, listas de material por item, notas técnicas e referências normativas). Tudo lido de escadas.json
(escadas_detalhe.py): mesma geometria do modelo 3D e as ligações verificadas (0 conflitos). Uso: python es04.py [interna] [externa]"""
import math
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from prancha_nd import Prancha
import escadas_vista as E

EJ = E.EJ
f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
H1, H2 = EJ.get("h_corrimao", [0.92, 0.70])


# ------------------------------------------------------------------ perspectiva (pyvista) com chamadas dos detalhes
def perspectiva(esc, arq):
    import numpy as np
    import pyvista as pv
    from PIL import Image, ImageChops
    fn = E.interna if esc == "interna" else E.externa
    pl = pv.Plotter(off_screen=True, window_size=(1800, 1500)); pl.set_background("white")
    for pc in E.P:
        if not fn(pc):
            continue
        pts = np.array(E.vertices(pc))
        try:
            m = pv.PolyData(pts).delaunay_3d().extract_surface(algorithm='dataset_surface')
        except Exception:
            continue
        if m.n_points == 0:
            continue
        gc = E.guarda(pc)
        cor = "#e07b39" if gc and "corrimão" in pc["marca"] else "#f2c14e" if gc else "#8c8c8c" if pc["grupo"] != "Piso e fundações" else "#d0d0d0"
        pl.add_mesh(m, color=cor, smooth_shading=False)
    lab, txt = [], []
    for prefixo, t in (("GI-1 montante" if esc == "interna" else "GE-1 montante", "Ver DETALHE 1"),
                       ("GI-10 cantoneira" if esc == "interna" else "GE-2 montante", "Ver DETALHE 2"),
                       ("GI-1 corrimão" if esc == "interna" else "GE-3 corrimão", "Ver DETALHE 3"),
                       ("GI-5 travessa" if esc == "interna" else "GE-5 travessa", "guarda-corpo com corrimão duplo"),
                       ("GI-4 corrimão" if esc == "interna" else "GE-2 corrimão", "corrimão duplo 0,92 / 0,70")):
        pc = next((p for p in E.P if p["marca"].startswith(prefixo) and fn(p)), None)
        if pc:
            lo, hi = E.bbox(pc)
            lab.append([(lo[i] + hi[i]) / 2 for i in range(3)]); txt.append(t)
    pl.add_point_labels(np.array(lab), txt, font_size=30, text_color="black", shape_color="white", shape_opacity=0.85, point_size=12, point_color="#c62828", always_visible=True)
    ps = [pc for pc in E.P if fn(pc)]
    lo = [min(E.bbox(p)[0][i] for p in ps) for i in range(3)]; hi = [max(E.bbox(p)[1][i] for p in ps) for i in range(3)]
    c = [(lo[i] + hi[i]) / 2 for i in range(3)]
    d = max(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])
    pl.camera_position = [(c[0] - 1.6 * d, c[1] - 1.9 * d, c[2] + 1.4 * d), tuple(c), (0, 0, 1)]
    pl.reset_camera(); pl.camera.zoom(1.15)
    pl.screenshot(arq, scale=3); pl.close()                         # rev11: ≥ 400 ppi
    im = Image.open(arq).convert("RGB")
    bb = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
    im.crop((max(bb[0] - 20, 0), max(bb[1] - 20, 0), min(bb[2] + 20, im.width), min(bb[3] + 20, im.height))).save(arq)
    return arq


# ------------------------------------------------------------------ quantitativos por item (guarda-corpo e corrimão)
def quantitativos(esc):
    pre = "GI-" if esc == "interna" else "GE-"
    G = [g for g in EJ["guardas"] if g["cod"].startswith(pre)]
    lst = [r for r in EJ["lista"] if r["escada"] == esc]
    gc_, cr_ = {}, {}

    def add(d, k, desc, mat, q, un):
        r = d.setdefault(k, [desc, mat, 0.0, un])
        r[2] += q
    n_mont = 0
    for g in G:
        gc = g["gc"]
        nm = g["n_vaos"] + 1
        n_mont += nm
        mp = gc["montante"]["perfil"]
        add(gc_, "m_" + mp, f"Montante {mp} (topo com tampa)", "ASTM A500 gr. B galv.", nm, "pç")
        add(gc_, "tampa", "Tampa do montante — chapa dobrada # 3 mm (PEÇA 2)", "ASTM A36 galv.", nm, "pç")
        if not g["so_corrimao"]:
            add(gc_, "t_" + gc["travessa"]["perfil"], f"Travessa superior {gc['travessa']['perfil']}", "ASTM A500 gr. B galv.", g["L"], "m")
            add(gc_, "L38", "Cantoneira L 38 × 38 × 4,8 das barras (2 por vão)", "ASTM A36 galv.", 2 * g["L"], "m")
            add(gc_, "pM10", "Parafuso M10 × 30 8.8 + porca + 2 arruelas (cantoneira L 38 no montante)", "ISO 898-1 cl. 8.8 galv.", 4 * g["n_vaos"], "cj")
            br = gc.get("barra")
            if br:
                nb = int(round(g["L"] / (br["s_mm"] / 1000)))
                add(gc_, "b_" + br["perfil"], f"{br['perfil'].replace('barra redonda', 'Barra redonda')} c/{br['s_mm']}, pontas roscadas (vão livre {br['vao_livre_mm']} mm)", "SAE 1020 galv.", nb, "pç")
                add(gc_, "porcas", "Porca + contraporca M10 das barras (2 pontas)", "classe 8 galv.", 4 * nb, "pç")
        if g["fix"] in ("longarina", "viga", "degrau"):
            add(gc_, "pM12", "Parafuso M12 × 110 8.8 + porca + 2 arruelas (montante na longarina / viga) — DETALHE 1", "ISO 898-1 cl. 8.8 galv.", 2 * nm, "cj")
            if g["fix"] != "degrau":
                add(gc_, "bucha", "Bucha tubo Ø21,3 × 2,6 L 46 (espaçador entre as mesas)", "ASTM A53 galv.", 2 * nm, "pç")
        if g["fix"] == "laje":
            add(gc_, "L102", "Cantoneira L 102 × 102 × 9,5 L 150 (base do montante na laje) — DETALHE 2", "ASTM A36 galv.", 2 * nm, "pç")
            add(gc_, "pM12p", "Parafuso M12 × 80 8.8 passante (cantoneiras × montante)", "ISO 898-1 cl. 8.8 galv.", 2 * nm, "cj")
            add(gc_, "chq", "Chumbador químico M10 hef 70 (barra 5.8 + resina epóxi) — conferir catálogo", "barra 5.8 galv. + epóxi", 4 * nm, "pç")
        # corrimão duplo
        Lc = 2 * (g["L"] + sum(g["prolongamentos"]))
        add(cr_, "tubo", f"Corrimão {gc['corrimao']['perfil']} (2 alturas: {f(H1, 2)} e {f(H2, 2)} m)", "ASTM A53 / NBR 5590 galv.", Lc, "m")
        add(cr_, "sup", "Suporte do corrimão CR-S — chapa dobrada # 4,75 × 40 em L (PEÇA 1)", "ASTM A36 galv.", 2 * nm, "pç")
        add(cr_, "abr", "Abraçadeira # 3 × 25 do tubo Ø38,1 (PEÇA 1)", "ASTM A36 galv.", 2 * nm, "pç")
        add(cr_, "M10s", "Parafuso M10 × 70 8.8 + porca (suporte no montante)", "ISO 898-1 cl. 8.8 galv.", 2 * nm, "cj")
        add(cr_, "M8", "Parafuso M8 × 25 8.8 + porca (abraçadeira)", "ISO 898-1 cl. 8.8 galv.", 4 * nm, "cj")
        n_term = 2 * sum(1 for e in g["prolongamentos"] if e > 0) + 2 * sum(1 for e in g["prolongamentos"] if e <= 0)
        add(cr_, "term", "Terminal do corrimão: curva 90° + tampa # 3 soldada de fábrica (DETALHE 3)", "ASTM A53 / A36 galv.", n_term, "pç")
    for r in lst:                                           # retorno do corrimão no patamar (só a interna)
        if r["item"] == "GI-R":
            add(cr_, "tubo", "", "", round(r["kg"] / 1.78, 2), "m")
    tubo_m = cr_["tubo"][2]
    cr_["luva"] = ["Luva de emenda Ø34 × 3 L 150 com 2 M8 (1 a cada 6 m de tubo)", "ASTM A53 galv.", math.ceil(tubo_m / 6.0), "pç"]
    fm = lambda r: [r[0], r[1], f(r[2], 2) if r[3] == "m" else f"{int(round(r[2]))}", r[3]]
    linhas = lambda d: [[str(i)] + fm(r) for i, r in enumerate(d.values(), 1)]
    return linhas(gc_), linhas(cr_), n_mont


# ------------------------------------------------------------------ folha
def folha(esc):
    des = "ND-LET-ES04" if esc == "interna" else "ND-LET-ES05"
    pre = "GI-" if esc == "interna" else "GE-"
    fn = E.interna if esc == "interna" else E.externa
    G = [g for g in EJ["guardas"] if g["cod"].startswith(pre)]
    pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                            conteudo=f"ESCADA METÁLICA {esc.upper()} — GUARDA-CORPO E CORRIMÃO DUPLO: DETALHES DE CONSTRUÇÃO E MONTAGEM",
                            desenho=des, folha="01/01", fase="PARA APROVAÇÃO", rev="00"))
    pr.revisao("00", "25/10/2026", "EMISSÃO INICIAL (rev10): DETALHAMENTO DO GUARDA-CORPO E DO CORRIMÃO DUPLO, LISTAS DE MATERIAL E NOTAS TÉCNICAS")
    Q = pr.quadro
    XC = Q[2] - 190
    hs = sorted({g["h"] for g in G if not g["so_corrimao"]})
    pr.cabecalho_peca("GC", f"GUARDA-CORPO E CORRIMÃO DUPLO — ESCADA {esc.upper()} ({', '.join(g['cod'] for g in G)})",
                      f"guarda-corpo h {' / '.join(f(h, 2) for h in hs)} m · corrimão duplo {f(H1, 2)} e {f(H2, 2)} m nos dois lados · RT CBMRS nº 11 · NBR 9050 · NBR 14718 · ligações de campo parafusadas, galvanizado",
                      largura=XC - Q[0] - 10)
    # ---- perspectiva
    img = perspectiva(esc, f"/home/claude/letsara/pranchas/img/iso_gc_{esc}.png")
    pr.imagem(Q[0] + 6, Q[3] - 236, Q[0] + 236, Q[3] - 34, img, titulo="PERSPECTIVA", subtitulo="guarda-corpo (amarelo) e corrimão duplo (laranja); chamadas dos detalhes 1, 2 e 3 — sem escala")
    # ---- vista superior e vista lateral 1:50 (projeção das peças)
    ps = [pc for pc in E.P if fn(pc)]
    lo = [min(E.bbox(p)[0][i] for p in ps) for i in range(3)]; hi = [max(E.bbox(p)[1][i] for p in ps) for i in range(3)]
    ESC = 50
    SUP = lambda x, y, z: (x * 1000, y * 1000)
    LAT = lambda x, y, z: (y * 1000, z * 1000)
    x0v = Q[0] + 262
    vs = pr.vista("VISTA SUPERIOR", (x0v - lo[0] * 1000 / ESC, Q[3] - 44 - hi[1] * 1000 / ESC), ESC, titulo="VISTA SUPERIOR", subtitulo="planta do trecho", unidade="mm")
    E.projetar(vs, SUP, lambda pc: fn(pc) and not E.guarda(pc) and pc["grupo"] != "Piso e fundações", cam="OCULTA")
    E.projetar(vs, SUP, lambda pc: fn(pc) and E.guarda(pc), cam="METALICA")
    vs.cota_h([lo[0] * 1000, hi[0] * 1000], lo[1] * 1000, -8, total=False)
    vs.cota_v([lo[1] * 1000, hi[1] * 1000], hi[0] * 1000, 8, total=False)
    w_sup = (hi[0] - lo[0]) * 1000 / ESC
    x0l = x0v + w_sup + 70
    vl = pr.vista("VISTA LATERAL", (x0l - lo[1] * 1000 / ESC, Q[3] - 60 - hi[2] * 1000 / ESC), ESC, titulo="VISTA LATERAL", subtitulo="guarda-corpo cotado nos montantes; corrimão duplo", unidade="mm")
    E.projetar(vl, LAT, lambda pc: fn(pc) and not E.guarda(pc) and pc["grupo"] != "Piso e fundações", cam="OCULTA")
    E.projetar(vl, LAT, lambda pc: fn(pc) and E.guarda(pc), cam="METALICA")
    gref = next(g for g in G if not g["so_corrimao"] and g["fix"] == "longarina")
    mts = sorted([pc for pc in E.P if pc["marca"].startswith(gref["cod"] + " montante")], key=lambda pc: E.bbox(pc)[0][1])
    us = [round((E.bbox(pc)[0][1] + E.bbox(pc)[1][1]) / 2 * 1000) for pc in mts]
    if len(set(us)) > 1:
        vl.cota_h(sorted(set(us)), lo[2] * 1000, -8, total=True)
    pc0 = mts[0]
    b0, b1 = E.bbox(pc0)
    zn = b1[2] * 1000 + 10
    vl.chamada(((b0[1] + b1[1]) * 500, zn), (10, (hi[2] * 1000 - zn) / ESC + 5), f"{gref['cod']}: montantes {gref['gc']['montante']['perfil']} c/{f(gref['s'] * 100, 1)} cm, guarda h {f(gref['h'], 2)} m (vertical do bocel)")
    # ---- detalhe do guarda-corpo 1:20 (módulo típico de 2 vãos)
    gd = max((g for g in G if not g["so_corrimao"]), key=lambda g: g["h"])
    gc = gd["gc"]
    bm, tr, s = gc["montante"]["b"], gc["travessa"]["b"], round(gd["s"] * 1000)
    h = round(gd["h"] * 1000)
    br = gc["barra"]
    yb = Q[1] + 420 - max(0, h - 1050) / 20
    d1 = pr.vista("DET GC", (Q[0] + 40, yb), 20, titulo="DETALHE DO GUARDA-CORPO", subtitulo=f"{gd['cod']} ({gd['nome']}) — módulo típico", unidade="mm")
    d1.linha((-250, 0), (2 * s + 250, 0), "TERRENO")
    for k in range(3):
        x = k * s
        d1.ret(x - bm / 2, -190 if gd["fix"] != "laje" else 0, bm, h - tr + (190 if gd["fix"] != "laje" else 0), "METALICA")
    d1.ret(-bm / 2, h - tr, 2 * s + bm, tr, "METALICA")
    for zz in (100, h - 50):
        d1.ret(bm / 2, zz - 19, 2 * s - bm, 38, "VISTA")
    nb = 0
    for k in range(2):
        xa = k * s + bm / 2
        n_ = max(1, round((s - bm) / br["s_mm"]))
        sp = (s - bm) / n_
        for j in range(n_):
            xb = xa + sp / 2 + j * sp
            d1.linha((xb, 100), (xb, h - 50), "METALICA"); nb += 1
            if k == 0 and j < 2:
                pass
    for hc in (H1, H2):
        zc = round(hc * 1000)
        d1.linha((-250, zc), (2 * s + 250, zc), "VISTA")
    d1.cota_h([0, s, 2 * s], -190, -8, total=True)
    xs_b = [bm / 2 + (s - bm) / max(1, round((s - bm) / br["s_mm"])) * (j + 0.5) for j in range(2)]
    d1.cota_v([0, 100, round(H2 * 1000), round(H1 * 1000), h - 50, h], -bm / 2, -16, total=False)
    d1.chamada((s, h - tr / 2), (6, 14), f"travessa {gc['travessa']['perfil']}")
    d1.chamada((2 * s + bm / 2, h * 0.30), (28, 0), f"montante {gc['montante']['perfil']} c/{f(gd['s'] * 100, 1)} cm (≤ 120)")
    d1.chamada((2 * s - bm, 100), (34, -6), "L 38 × 38 × 4,8 (2 por vão), 1 M10 em cada montante")
    d1.chamada((s + xs_b[0], h - 50), (2, 24), f"{br['perfil']} c/{br['s_mm']} — vão livre {br['vao_livre_mm']} < 150")
    d1.chamada((2 * s + 250, round(H1 * 1000)), (30, 10), f"corrimão Ø38,1 a {f(H1, 2)}")
    d1.chamada((2 * s + 250, round(H2 * 1000)), (30, -6), f"corrimão Ø38,1 a {f(H2, 2)}")
    # ---- detalhe do corrimão duplo 1:20 (trecho inclinado + prolongamento + terminal)
    ang = math.atan2(17.95, 28.0)
    Lh = 1800
    xc0 = Q[0] + 400
    d2 = pr.vista("DET CR", (xc0, yb - 27), 20, titulo="DETALHE DO CORRIMÃO DUPLO", subtitulo=f"nos dois lados dos lances; {f(H1, 2)} e {f(H2, 2)} m acima do bocel", unidade="mm")
    zt = lambda x: x * math.tan(ang)
    pts_n = []
    for k in range(7):
        x = k * 280
        pts_n += [(x, zt(x)), (x + 280, zt(x))]
    d2.poli(pts_n[:-1], "VISTA")
    d2.linha((0, 0), (Lh, zt(Lh)), "EIXO")
    for hc in (H1, H2):
        zc = hc * 1000
        d2.linha((0, zc), (Lh, zt(Lh) + zc), "METALICA")
        d2.linha((0, zc), (-300, zc), "METALICA")
        d2.poli([(-300, zc), (-330, zc - 30), (-330, zc - 120)], "METALICA")
    for xm in (140, 140 + 1120):
        d2.ret(xm - 25, zt(xm), 50, H1 * 1000 + 60, "OCULTA")
    d2.cota_v([0, H2 * 1000, H1 * 1000], 0, -30, total=False)
    d2.cota_h([-300, 0], H1 * 1000, 10, total=False)
    d2.chamada((Lh, zt(Lh) + H1 * 1000), (6, 8), "corrimão sup. Ø38,1 (RT CBMRS 11)")
    d2.chamada((Lh, zt(Lh) + H2 * 1000), (10, -6), "corrimão inf. Ø38,1 (NBR 9050)")
    d2.chamada((-330, H2 * 1000 - 120), (-6, -28), "prolongamento 30 cm + curva 90° (DETALHE 3)")
    d2.chamada((Lh, zt(Lh)), (10, -4), "linha dos bocéis")
    d2.chamada((1260, zt(1260) + H1 * 1000 + 60), (-8, 12), "montante (suportes CR-S nas 2 alturas)")
    # ---- corte A-A 1:10 (seção do guarda-corpo na longarina)
    yc_ = Q[1] + 70
    ca = pr.vista("CORTE A-A", (Q[0] + 760, Q[1] + 405), 5, titulo="CORTE A-A", subtitulo="na longarina", unidade="mm")
    hc_ = min(h, 1050)
    ca.ret(-152, -190, 152, 152, "METALICA")                                   # longarina U (vista de topo da seção)
    ca.ret(0, -190, bm, hc_ - tr + 190, "METALICA")
    ca.ret(0, hc_ - tr, bm, tr, "METALICA")
    D = gc["corrimao"]["D"]
    for hc in (H1, H2):
        zc = hc * 1000
        xcr = -40 - D / 2
        ca.circulo((xcr, zc), D / 2, "METALICA")
        ca.poli([(0, zc - 30), (-20, zc - 30), (-20, zc - 5)], "METALICA")
    for zz in (100, hc_ - 50):
        ca.ret(bm, zz - 19, 38, 38, "VISTA")
    ca.linha((bm + 19, 100), (bm + 19, hc_ - 50), "METALICA")
    for zz in (-140, -70):
        ca.linha((-170, zz), (bm + 20, zz), "METALICA")
    ca.cota_h([-40 - D, -40, 0, bm], hc_, 12, total=False)
    ca.cota_v([-190, 0, H2 * 1000, H1 * 1000], bm + 60, 10, total=False)
    ca.chamada((-40 - D / 2, H1 * 1000 + D / 2), (-4, 22), "40 mm livres (RT CBMRS 11)")
    ca.chamada((-76, -100), (-2, -24), "longarina (mesas para fora)")
    ca.chamada((bm + 10, -105), (12, -8), "2 M12 + bucha (DETALHE 1)")
    # ---- peça 1 (suporte CR-S) e peça 2 (tampa do montante) 1:5
    p1 = pr.vista("PEÇA 1", (Q[0] + 790, Q[1] + 70), 5, titulo="PEÇA 1 — SUPORTE CR-S", subtitulo="# 4,75 × 40 + abraçadeira", unidade="mm")
    p1.ret(0, 0, 4.75, 70, "METALICA"); p1.ret(-40, 0, 40, 4.75, "METALICA")
    p1.circulo((2.4, 45), 5.5, "VISTA")
    p1.circulo((-40 - 19.05 - 2, 2.4), 19.05, "METALICA"); p1.circulo((-40 - 19.05 - 2, 2.4), 22.05, "METALICA")
    p1.cota_h([-40, 0], 0, -10, total=False)
    p1.cota_v([0, 45, 70], -90, -6, total=False)
    p1.chamada((2.4, 45), (12, 6), "furo Ø11 (M10 no montante)")
    p1.chamada((-61, 24.5), (-10, 10), "abraçadeira 2 M8 (furos Ø9)")
    p2 = pr.vista("PEÇA 2", (Q[0] + 790, Q[1] + 170), 5, titulo="PEÇA 2 — TAMPA DO MONTANTE", subtitulo="chapa dobrada # 3, 1 M6, sem solda", unidade="mm")
    p2.ret(0, 20, bm + 6, 3, "METALICA"); p2.ret(0, 0, 3, 20, "METALICA"); p2.ret(bm + 3, 0, 3, 20, "METALICA")
    p2.ret(3, -60, bm, 80, "OCULTA")
    p2.cota_h([0, bm + 6], 23, 10, total=False)
    p2.cota_v([0, 20], bm + 6, 8, total=False)
    p2.chamada((bm + 4.5, 10), (12, -6), "1 M6 (furo Ø7) na aba")
    # ---- detalhes 1, 2, 3 de fixação (1:5)
    dA = pr.vista("DETALHE 1", (Q[0] + 110, Q[1] + 110), 5, titulo="DETALHE 1 — MONTANTE NA LONGARINA / VIGA", subtitulo="2 M12 8.8 a 70 + bucha Ø21,3 × 2,6 entre as mesas", unidade="mm")
    dA.ret(0, 0, 5.1, 152.4, "METALICA"); dA.ret(5.1, 0, 43.7, 8.7, "METALICA"); dA.ret(5.1, 143.7, 43.7, 8.7, "METALICA")
    dA.ret(48.8, -60, bm, 330, "METALICA")
    for zz in (41, 111):
        dA.ret(5.1, zz - 10.65, 43.7, 21.3, "VISTA"); dA.linha((-15, zz), (48.8 + bm + 15, zz), "METALICA")
    dA.cota_v([0, 41, 111, 152.4], 48.8 + bm + 25, 8, total=False)
    dA.chamada((48.8 + bm / 2, 220), (12, 10), f"montante {gc['montante']['perfil']}")
    dA.chamada((25, 41), (-14, -14), "bucha L 46")
    dA.chamada((-12, 111), (-12, 10), "M12 × 110 + porca + 2 arruelas")
    if esc == "interna":
        lg = next(l for l in EJ["ligacoes"] if l["cod"] == "GC-LAJE")
        dB = pr.vista("DETALHE 2", (Q[0] + 330, Q[1] + 150), 5, titulo="DETALHE 2 — MONTANTE NA LAJE (GI-10 / GI-11)", subtitulo="2 L 102 + 4 químicos M10", unidade="mm")
        pts = [(-150, -200), (250, -200), (250, 0), (-150, 0)]
        dB.poli(pts, "CORTADO", fechada=True); dB.hachura(pts, "AR-CONC", 0.03)
        dB.ret(100, 0, 50, 250, "METALICA")
        dB.ret(150, 0, 9.5, 102, "METALICA"); dB.ret(150, 0, 102, 9.5, "METALICA")
        dB.ret(90.5, 0, 9.5, 102, "METALICA"); dB.ret(-2, 0, 102, 9.5, "METALICA")
        dB.linha((205, -70), (205, 20), "METALICA"); dB.linha((45, -70), (45, 20), "METALICA")
        dB.linha((80, 60), (170, 60), "METALICA")
        dB.cota_h([-2, 45, 100, 150, 205, 252], 0, -8, total=False)
        dB.cota_v([-70, 0, 60, 102], 252, 10, total=False)
        dB.chamada((45, -50), (40, -50), "chumbador químico M10 hef 70 (4) — conferir catálogo")
        dB.chamada((170, 60), (14, 12), "2 L 102 × 102 × 9,5 × 150 + 2 M12 passantes")
        dB.chamada((-120, -100), (-6, -16), "borda da laje ≥ 60")
    else:
        dB = pr.vista("DETALHE 2", (Q[0] + 365, Q[1] + 130), 5, titulo="DETALHE 2 — MONTANTE DO CORRIMÃO NA ALMA (GE-2)", subtitulo="lado da parede", unidade="mm")
        dB.ret(0, -150, 6.3, 300, "METALICA")
        dB.ret(-40, -20, 40, 240, "METALICA")
        dB.ret(-90, -24, 90, 4, "VISTA")
        for zz in (40, 110):
            dB.linha((-55, zz), (25, zz), "METALICA")
        dB.cota_v([-20, 40, 110], -60, -8, total=False)
        dB.chamada((3, 120), (12, 10), "alma da longarina (lado dos degraus)")
        dB.chamada((-20, 180), (-14, 10), "montante 40 × 40 × 4 + 2 M12 8.8")
        dB.chamada((-60, -22), (-10, -12), "degrau (apoio do pé)")
    dC = pr.vista("DETALHE 3", (Q[0] + 560, Q[1] + 160), 10, titulo="DETALHE 3 — TERMINAL E EMENDA DO CORRIMÃO", subtitulo="terminal com curva e emenda com luva", unidade="mm")
    Dm = D
    dC.ret(0, 0, 180, Dm, "METALICA")
    dC.poli([(0, 0), (-30, -30), (-30 - Dm, -30), (-Dm, Dm)], "METALICA")
    dC.ret(-30 - Dm, -60, Dm, 30, "METALICA")
    dC.ret(-30 - Dm - 2, -63, Dm + 4, 3, "METALICA")
    dC.ret(220, -2, 150, Dm + 4, "OCULTA")
    dC.ret(180, 0, 220, Dm, "METALICA")
    for xx in (255, 335):
        dC.circulo((xx, Dm / 2), 4.5, "VISTA")
    dC.cota_h([220, 255, 335, 370], Dm + 2, 10, total=False)
    dC.chamada((-30 - Dm / 2, -63), (-4, -10), "tampa # 3 (solda de fábrica)")
    dC.chamada((365, 0), (8, -12), "luva Ø34 L 150 + 2 M8")
    dC.chamada((-15, -15), (-8, 12), "curva 90°")
    # ---- tabelas e notas
    tg, tc_, nmont = quantitativos(esc)
    y = Q[3] - 6
    y = pr.tabela(XC, y, "LISTA DE MATERIAIS — GUARDA-CORPO", ["ITEM", "DESCRIÇÃO", "MATERIAL", "QUANT.", "UN."], tg, [10, 104, 42, 18, 12], h_lin=4.6)
    y = pr.tabela(XC, y - 4, f"LISTA DE MATERIAIS — CORRIMÃO DUPLO ({f(H1, 2)} / {f(H2, 2)} m)", ["ITEM", "DESCRIÇÃO", "MATERIAL", "QUANT.", "UN."], tc_, [10, 104, 42, 18, 12], h_lin=4.6)
    notas = ["Medidas em mm, níveis em m. Cotas de alturas do guarda-corpo e do corrimão medidas na vertical a partir da linha dos bocéis (lances) ou do piso acabado (patamares e laje).",
             "Aço: tubos estruturais ASTM A500 gr. B, tubo do corrimão ASTM A53 / NBR 5590 (Ø38,1 × 2), chapas e cantoneiras ASTM A36, barras do fechamento SAE 1020 com pontas roscadas.",
             "Soldas SÓ DE FÁBRICA (tampa e curva dos terminais do corrimão): eletrodo E70XX / arame ER70S-6, filete contínuo de 3 mm, procedimento e soldador qualificados (AWS D1.1), inspeção visual 100 %. Ligações de campo TODAS parafusadas (montante × longarina/viga, cantoneiras, suportes, emendas), sem solda na obra.",
             "Parafusos ISO 898-1 classe 8.8 (M12, M10, M8, M6) galvanizados a fogo, porca classe 8 e 2 arruelas lisas; aperto normal (snug tight). Chumbadores químicos M10 hef 70 com resina epóxi em furo limpo, distância à borda ≥ 60 mm — conferir no catálogo do fornecedor antes da compra.",
             "Proteção: galvanização a fogo de todas as peças depois de furadas e soldadas (NBR 6323, camada média ≥ 85 µm); retoques em cortes e furos de obra com tinta rica em zinco. Opcional para acabamento: primer epóxi + esmalte PU na cor definida pela arquitetura.",
             f"Cargas: {f(EJ['cargas']['guarda_corpo_kN_m'], 2)} kN/m horizontal no topo do guarda-corpo, {f(EJ['cargas']['fechamento_kPa'], 2)} kPa no fechamento e {f(EJ['cargas']['corrimao_kN'], 2)} kN no corrimão (NBR 14718), γf 1,5; montantes, travessa, corrimão e barras dimensionados no limite (uso na ND-LET-ES03).",
             "Corrimão duplo contínuo nos dois lados dos lances e no patamar, afastado 40 mm de qualquer peça, prolongamento de 30 cm nas pontas livres com curva de 90° para baixo; guarda-corpo com vão livre < 150 mm (esfera de 15 cm não passa).",
             "Montagem: fixar os montantes (DETALHE 1/2), conferir prumo e alinhamento, colocar travessa, cantoneiras e barras, depois os suportes e o corrimão; emendas do corrimão por luva parafusada fora dos suportes. Geometria completa das escadas nas ND-LET-ES01/ES02 e elevações de todos os trechos na ND-LET-ES03.",
             "REFERÊNCIAS NORMATIVAS: RT CBMRS nº 11 Parte 01/2016 (saídas de emergência); NBR 9050:2020 (acessibilidade — corrimão em duas alturas); NBR 14718:2019 (guarda-corpos — requisitos e ensaios); NBR 9077 (saídas de emergência); NBR 8800:2024 (estruturas de aço — ligações); NBR 6323 (galvanização a fogo); AWS D1.1 (soldagem)."]
    pr.notas(XC, y - 4, notas, 182)
    for pos in ():
        pr.posicoes_desenho.add(pos)
    avisos = pr.salvar(f"/home/claude/letsara/pranchas/{des}")
    print(des, len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
    for a in avisos:
        print("  ", a)
    return avisos


if __name__ == "__main__":
    for esc in (sys.argv[1:] or ["interna", "externa"]):
        folha(esc)
