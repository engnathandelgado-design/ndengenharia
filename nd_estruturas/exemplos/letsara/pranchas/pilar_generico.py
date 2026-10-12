"""Prancha genérica de pilar pré-moldado (em pé, faces A/B/C/D, consolos em qualquer face) — padrão ND.
Usada por PC-01/02 (centrais 50×50) e PM-01 (mezanino 40×60). Rodar: python pilar_generico.py pc | pm
Faces: A = x+, B = y+, C = x−, D = y−. Modelo em mm; cotas de concreto em cm; chaparia em mm."""
import json, math, subprocess, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha

f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
Y_LIN = [0.0, 10.05, 19.705, 29.36, 38.865, 48.445, 58.025, 67.605, 76.81]
X_FACH = [0.0, 9.87, 20.05, 29.63, 40.10]
COB = 30
# direção horizontal de cada vista (olhando a face de fora, z para cima): (eixo, sinal) -> coordenada à direita
VISTA = {"A": ("y", 1), "B": ("x", -1), "C": ("y", -1), "D": ("x", 1)}
OPOSTA = {"A": "C", "B": "D", "C": "A", "D": "B"}


def prancha_pilar(P):
    B, H, L_CAL, Z_TOP = P["B"], P["H"], P["L_CAL"], P["Z_TOP"]
    L_TOT = L_CAL + Z_TOP
    PESO = B * H / 1e6 * L_TOT / 1000 * 25
    V = B * H / 1e6 * L_TOT / 1000
    AL = P["al"]
    cons = P["consolos"]
    json.dump(dict(B=B, H=H, L_TOT=L_TOT, consolos=cons, ip01=P.get("ip01", []), al=AL, marca=P["marca"], z_topo=Z_TOP / 1000, zoom=P.get("zoom", 3.2)),
              open(f"/home/claude/letsara/pranchas/{P['marca']}_geom.json", "w"))
    subprocess.run([sys.executable, "/home/claude/letsara/pranchas/iso3d_pilar_gen.py", f"/home/claude/letsara/pranchas/{P['marca']}_geom.json",
                    "/home/claude/letsara/pranchas/"], check=True, capture_output=True)
    # armadura
    xy = P["xy"]
    EST = P["est"]
    z_est = sorted(set(list(range(50, EST["zona"] + L_CAL, EST["s_dens"])) + list(range(EST["zona"] + L_CAL, L_TOT - EST["zona"], EST["s_corr"])) +
                       list(range(L_TOT - EST["zona"], L_TOT - 40, EST["s_dens"]))))
    n_est = len(z_est)
    pr = Prancha("A0", dict(cliente="MARQUE ENGENHARIA", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                            conteudo=P["conteudo"], desenho=P["desenho"], folha="01/01", fase="PARA APROVAÇÃO",
                            marca=P["marca"], qtd=P["qtd"], peso=f(PESO, 1), volume=f(V, 2)))
    pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL")
    Q = pr.quadro
    XC = Q[2] - 190
    Y0 = 92
    ESC = 20
    pr.ret(Q[0] + 4, Q[3] - 30, Q[0] + 560, Q[3] - 4, "CARIMBO")
    pr.texto(Q[0] + 10, Q[3] - 24, P["marca"], "grande", "TITULO")
    pr.texto(Q[0] + 62, Q[3] - 24, f"PILAR PRÉ-MOLDADO  {B/10:g} × {H/10:g} cm   ·   L = {L_TOT/10:g} cm (cálice {L_CAL/10:g} + {Z_TOP/10:g})   ·   C40   ·   {P['qtd']} peças", "titulo", "TITULO")
    pr.texto(Q[0] + 10, Q[3] - 14, P["posicao"] + f"   ·   PESO {f(PESO/10, 2)} t   ·   VOLUME {f(V, 2)} m³   ·   FACES: A = x+, B = y+, C = x−, D = y−   ·   desenhado em pé, como montado", "nota", "TEXTO")

    # planta-chave 1:750
    kp = pr.vista("PLANTA-CHAVE", (Q[0] + 487, Q[3] - 172), 750, titulo="PLANTA-CHAVE", subtitulo=f"{P['marca']} hachurado", unidade="cm")
    Xm = lambda m: m * 1000
    for y in Y_LIN:
        kp.linha((Xm(-2.5), Xm(y)), (Xm(42.6), Xm(y)), "EIXO")
    for x in X_FACH:
        kp.linha((Xm(x), Xm(-2.5)), (Xm(x), Xm(83)), "EIXO")
    for i, y in enumerate(Y_LIN, 1):
        kp.circulo((Xm(-2.5), Xm(y)), 1100, "VISTA"); kp.texto((Xm(-2.5), Xm(y)), str(i), "nota", "MIDDLE_CENTER")
    for j, x in enumerate(X_FACH):
        kp.circulo((Xm(x), Xm(83)), 1100, "VISTA"); kp.texto((Xm(x), Xm(83)), "ABCDE"[j], "nota", "MIDDLE_CENTER")
    for nome, x, y, bx, by, mk in P["kp"]:
        pts = [(Xm(x) - bx / 2, Xm(y) - by / 2), (Xm(x) + bx / 2, Xm(y) - by / 2), (Xm(x) + bx / 2, Xm(y) + by / 2), (Xm(x) - bx / 2, Xm(y) + by / 2)]
        kp.poli(pts, "CORTADO", fechada=True)
        if mk == P["marca"]:
            kp.hachura(pts, "ANSI31", 0.3)
            kp.texto((Xm(x) + 700, Xm(y) + 500), f"{nome} {mk}", "min", "BOTTOM_LEFT")

    # ------------------------------------------------------------ vistas das faces (em pé)
    def largura(face):
        return B if face in "AC" else H
    def nivel(v, x, z, txt, lado=1):
        v.poli([(x, z), (x + lado * 60, z + 60), (x + lado * 60, z - 60), (x, z)], "COTA")
        v.linha((x + lado * 60, z), (x + lado * 260, z), "COTA")
        v.texto((x + lado * 70, z + 10), txt, "min", "BOTTOM_LEFT" if lado > 0 else "BOTTOM_RIGHT", "COTA")

    def vista_face(face, x_papel):
        W = largura(face)
        eixo, sg = VISTA[face]
        v = pr.vista(f"FACE {face}", (x_papel, Y0), ESC, titulo=f"FACE {face}" + (" (CONSOLOS)" if any(c["face"] == face for c in cons) else ""), subtitulo="pilar em pé", unidade="cm")
        v.ret(0, 0, W, L_TOT, "VISTA")
        v.linha((0, L_CAL), (W, L_CAL), "EIXO")
        for k in range(3):                                                                   # chaves de cisalhamento (frontal)
            v.ret(50, 150 + k * 300 + 40, W - 100, 120, "OCULTA")
        for c in cons:
            zc, proj, h, hp, larg = c["z"], c["proj"], c["h"], c["hp"], c["larg"]
            if c["face"] == face:                                                            # frontal
                v.ret((W - larg) / 2, zc - h, larg, h, "VISTA")
                v.linha(((W - larg) / 2, zc - hp), ((W + larg) / 2, zc - hp), "VISTA")
                v.ret(W / 2 - c["pino_d"] / 2, zc - c["pino_emb"], c["pino_d"], c["pino_emb"], "OCULTA")
                v.chapa(W / 2 - c["pino_d"] / 2, zc, c["pino_d"], c["pino_L"] - c["pino_emb"])
                v.chapa(W / 2 - c["neo"][0] / 2, zc, c["neo"][0], 10)
                v.chamada((W / 2, zc - h + hp / 2), (12, -12), f"{c['tipo']} {larg/10:g}×{proj/10:g}×{h/10:g}/{hp/10:g}")
            elif c["face"] == OPOSTA[face]:
                v.ret((W - larg) / 2, zc - h, larg, h, "OCULTA")
            else:                                                                            # lateral: projeção para fora
                lado = 1 if (VISTA[face][0] == "y" and c["face"] == "B") or (VISTA[face][0] == "x" and c["face"] == "A") else -1
                lado *= sg if VISTA[face][0] == "y" else 1
                # regra: à direita da vista fica a face cuja coordenada cresce no sentido de `sg`
                lado = 1 if ((c["face"] == "B" and eixo == "y" and sg > 0) or (c["face"] == "D" and eixo == "y" and sg < 0) or
                             (c["face"] == "A" and eixo == "x" and sg > 0) or (c["face"] == "C" and eixo == "x" and sg < 0)) else -1
                x0 = W if lado > 0 else 0
                v.poli([(x0, zc - h), (x0 + lado * proj, zc - hp), (x0 + lado * proj, zc + proj * 0.03), (x0, zc)], "VISTA")
                v.ret(x0 + lado * c["pino_x"] - c["pino_d"] / 2, zc - c["pino_emb"], c["pino_d"], c["pino_emb"], "OCULTA")
                v.chapa(x0 + lado * c["pino_x"] - c["pino_d"] / 2, zc, c["pino_d"], c["pino_L"] - c["pino_emb"])
                v.chapa(x0 + (25 if lado > 0 else -25 - c["neo"][1]), zc, c["neo"][1], 10)
        for ip in P.get("ip01", []):
            if ip["face"] == face:
                for z in ip["z"]:
                    v.chapa(W / 2 - 75, z - 75, 150, 150)
                    for dy in (-40, 40):
                        v.circulo((W / 2 + dy, z), 6.25, "VISTA")
            elif ip["face"] == OPOSTA[face]:
                for z in ip["z"]:
                    v.ret(W / 2 - 75, z - 75, 150, 150, "OCULTA")
        if face == "A":
            for z in AL:
                v.linha((W / 2 - 50, z), (W / 2 + 50, z), "METALICA"); v.circulo((W / 2 - 50, z), 6.35, "METALICA"); v.circulo((W / 2 + 50, z), 6.35, "METALICA")
        cf = [c for c in cons if c["face"] == face]
        zs = sorted(set([0, L_CAL] + [c["z"] for c in cf] + [c["z"] - c["h"] for c in cf] + [L_TOT]))
        v.cota_v(zs, 0, -9)
        ords = sorted(set([0, L_CAL] + [c["z"] for c in cons if c["face"] == face] + [z for ip in P.get("ip01", []) if ip["face"] == face for z in ip["z"]] + [L_TOT]))
        if len(ords) > 3:
            v.cota_ord_v(ords, W, 9, y0=0)
        v.cota_h([0, W], 0, -8)
        v.texto((W / 2, L_TOT + 120), f"FACE {face}", "sub", "BOTTOM_CENTER")
        return v

    xs_faces = {}
    xp = Q[0] + 50
    for face in P["vistas"]:
        xs_faces[face] = vista_face(face, xp)
        xp += 60 + (largura(face) + 2 * max([c["proj"] for c in cons] + [0])) / ESC
    vA = xs_faces[P["vistas"][0]]
    nivel(vA, 0, L_CAL, "±0,000 piso", -1)
    nivel(vA, 0, L_TOT, f"+{f(Z_TOP/1000, 3)} topo", -1)
    for c in cons:
        if c["face"] == P["vistas"][0]:
            nivel(vA, 0, c["z"], f"+{f((c['z'] - L_CAL)/1000, 3)} assento", -1)
    vA.marcador_corte((-80, 4300), (largura(P["vistas"][0]) + 80, 4300), "A", lado=1)

    # ------------------------------------------------------------ ARMAÇÃO
    va = pr.vista("ARMAÇÃO", (xp, Y0), ESC, titulo="ARMAÇÃO", subtitulo="vista pela face A", unidade="cm")
    W = B
    va.ret(0, 0, W, L_TOT, "VISTA")
    for z in z_est:
        va.linha((COB, z), (W - COB, z), "ARM_TRANSV")
    va.barra([(COB + 18, 40), (COB + 18, L_TOT - 40)], "N1", len(xy), 20, comp_cm=round((L_TOT - 80) / 10), ponto_rotulo=(COB + 18, 3000), desloc=(14, 12))
    va.linha((W - COB - 18, 40), (W - COB - 18, L_TOT - 40), "ARMADURA")
    va.chamada((W - COB, 5000), (12, 10), f"N2 Ø8 c/{EST['s_corr']//10}" + (" + N3" if P["grampos"] else ""))
    va.chamada((W - COB, 600), (12, 10), f"N2 Ø8 c/{EST['s_dens']//10}" + (" + N3" if P["grampos"] else ""))
    va.cota_v([0, EST["zona"] + L_CAL, L_TOT - EST["zona"], L_TOT], 0, -9)
    for z in sorted(set(round(c["z"] / 500) * 500 for c in cons)):
        va.chamada((W, z - 200), (10, 8), "N4/N5/N6 — DET. 1")
    va.texto((W / 2, L_TOT + 120), "ARMAÇÃO", "sub", "BOTTOM_CENTER")
    pr.posicoes_desenho.update({"N2", "N4", "N5", "N6"} | ({"N3"} if P["grampos"] else set()))
    xp += 40 + W / ESC

    # ------------------------------------------------------------ isométrico geral
    pr.imagem(Q[0] + 455 + 0, Y0 - 10, Q[0] + 575, Y0 + 540, f"/home/claude/letsara/pranchas/ISO-{P['marca']}-geral.png", titulo="ISOMÉTRICO", subtitulo="faces B e C; sem escala")

    # ------------------------------------------------------------ CORTE A-A (1:10)
    XD = Q[0] + 625
    YS = Q[3] - 150
    v = pr.vista("CORTE A-A", (XD + 40, YS), 10, titulo="CORTE A-A", subtitulo="corrente; cobr. 3,0 cm", unidade="cm")
    pts = [(-B / 2, -H / 2), (B / 2, -H / 2), (B / 2, H / 2), (-B / 2, H / 2)]
    v.poli(pts, "CORTADO", fechada=True); v.hachura(pts, "AR-CONC", 0.03)
    v.poli([(-B / 2 + COB, -H / 2 + COB), (B / 2 - COB, -H / 2 + COB), (B / 2 - COB, H / 2 - COB), (-B / 2 + COB, H / 2 - COB)], "ARM_TRANSV", fechada=True)
    v.poli([(-B / 2 + COB, H / 2 - COB), (-B / 2 + COB + 60, H / 2 - COB - 60)], "ARM_TRANSV"); v.poli([(-B / 2 + COB + 60, H / 2 - COB), (-B / 2 + COB, H / 2 - COB - 60)], "ARM_TRANSV")
    for yg in P["grampos"]:
        v.linha((-B / 2 + COB, yg), (B / 2 - COB, yg), "ARM_TRANSV")
    for x, y in xy:
        v.ponto_barra((x, y), 20)
    v.cota_h([-B / 2, B / 2], -H / 2, -8); v.cota_v([-H / 2, H / 2], B / 2, 8)
    v.texto((0, H / 2 + 30), "FACE A", "min", "BOTTOM_CENTER"); v.texto((0, -H / 2 - 130), "FACE C", "min", "TOP_CENTER")
    v.texto((B / 2 + 110, 0), "FACE B", "min", "MIDDLE_LEFT", rot=90); v.texto((-B / 2 - 30, 0), "FACE D", "min", "MIDDLE_RIGHT", rot=90)
    v.chamada((-xy[0][0], xy[0][1]), (-10, 10), f"N1 — {len(xy)} Ø20")
    v.chamada((-B / 2 + COB, 100), (-10, 0), "N2 Ø8")
    if P["grampos"]:
        v.chamada((0, P["grampos"][0]), (-10, -14), "N3 grampo Ø8")

    # ------------------------------------------------------------ DETALHE 1 — consolo (1:10) e DETALHE 2 — base (1:20)
    c0 = max(cons, key=lambda c: c["h"])
    YM = Q[3] - 455
    d1 = pr.vista("DETALHE 1", (XD + 70, YM - 40), 10, titulo=f"DETALHE 1 — CONSOLO {c0['tipo']}", subtitulo="armadura e pino; NBR 9062:2017 7.3", unidade="cm")
    PW = largura(OPOSTA[c0["face"]]) if c0["face"] in "BD" else H
    PW = H if c0["face"] in "AC" else B
    zc0, Z1, Z2 = 1000, 400, 1450
    proj, h, hp = c0["proj"], c0["h"], c0["hp"]
    d1.poli([(-PW, Z1), (-PW, Z2), (0, Z2), (0, Z1)], "VISTA"); d1.interrupcao((-PW, Z1), (0, Z1)); d1.interrupcao((-PW, Z2), (0, Z2))
    d1.poli([(0, zc0 - h), (proj, zc0 - hp), (proj, zc0 + proj * 0.03), (0, zc0)], "VISTA")
    d1.ret(c0["pino_x"] - c0["pino_d"] / 2, zc0 - c0["pino_emb"] + 5, c0["pino_d"], c0["pino_emb"], "OCULTA")
    d1.chapa(c0["pino_x"] - c0["pino_d"] / 2, zc0 + 5, c0["pino_d"], c0["pino_L"] - c0["pino_emb"])
    d1.chapa(25, zc0 + 1, c0["neo"][1], 10)
    d1.poli([(-PW + COB + 8, zc0 - 55 - 150), (-PW + COB + 8, zc0 - 55), (proj - 40, zc0 - 55)], "ARMADURA"); d1.poli([(proj - 40, zc0 - 55), (proj - 40, zc0 - 85)], "ARMADURA")
    for dz in (-150, -250):
        d1.poli([(proj - 40, zc0 + dz), (-PW + COB, zc0 + dz)], "ARM_TRANSV")
    for dx in range(60, proj - 40, 80):
        d1.poli([(dx, zc0 - 30 + dx * 0.03), (dx, zc0 - h + (h - hp) * dx / proj + 30)], "ARM_TRANSV")
    for z in range(500, Z2, 100):
        d1.linha((-PW + COB, z), (-COB, z), "ARM_TRANSV")
    for x in (-PW + COB + 18, -COB - 18):
        d1.linha((x, Z1), (x, Z2), "ARMADURA")
    d1.cota_v([zc0 - h, zc0 - hp, zc0, zc0 + proj * 0.03], proj, 10, total=False)
    d1.cota_h([0, c0["pino_x"], proj], zc0 - h, -8, total=False); d1.cota_h([-PW, 0], Z1, -8)
    d1.chamada((-PW + 300, zc0 - 55), (-4, 12), f"N4 — {c0['tir']} U ({(PW + proj - 80)/10:.0f} + 15)")
    d1.chamada((-200, zc0 - 250), (-6, -12), "N5 — 2 Ø10 (costura)")
    d1.chamada((140, zc0 - 300), (14, -12), f"N6 — {len(range(60, proj - 40, 80))} Ø8")
    d1.chamada((c0["pino_x"], zc0 + 350), (10, 10), f"{c0['pino_nome']} Ø{c0['pino_d']} CA-50 L={c0['pino_L']/10:g}")
    d1.chamada((150, zc0 + 6), (16, 20), f"neoprene {c0['neo'][0]}×{c0['neo'][1]}×{c0['neo'][2]} mm")
    d1.chamada((-COB - 18, 1350), (-8, 8), "N1 / N2 c/10")

    d2 = pr.vista("DETALHE 2", (XD + 245, YM - 15), 20, titulo="DETALHE 2 — BASE NO CÁLICE", subtitulo="embutimento 100 cm; chaves", unidade="cm")
    d2.poli([(-H / 2, 0), (H / 2, 0), (H / 2, 1600), (-H / 2, 1600)], "VISTA")
    for k in range(3):
        z0 = 150 + k * 300
        for sg in (-1, 1):
            d2.poli([(sg * H / 2, z0), (sg * (H / 2 + 30), z0 + 40), (sg * (H / 2 + 30), z0 + 160), (sg * H / 2, z0 + 200)], "VISTA")
    d2.linha((-H / 2 - 400, L_CAL), (H / 2 + 400, L_CAL), "EIXO")
    d2.poli([(-H / 2 - 150, L_CAL), (-H / 2 - 150, -500), (H / 2 + 150, -500), (H / 2 + 150, L_CAL)], "OCULTA")
    for x in (-H / 2 + COB + 18, H / 2 - COB - 18):
        d2.linha((x, 40), (x, 1600), "ARMADURA")
    for z in range(50, 1500, 100):
        d2.linha((-H / 2 + COB, z), (H / 2 - COB, z), "ARM_TRANSV")
    d2.cota_v([0, L_CAL, 1500], H / 2 + 150, 10, total=False); d2.cota_h([-H / 2, H / 2], 0, -8)
    d2.chamada((H / 2 + 30, 250), (14, 4), "chaves 4×20 (4 faces)"); d2.chamada((H / 2 - COB, 1350), (12, 8), "N2 Ø8 c/10")
    d2.chamada((H / 2 + 150, -300), (8, -8), "cálice (fundações)"); d2.chamada((H / 2, L_CAL), (16, 18), "piso ±0,000; graute")

    pr.imagem(XD - 15, Y0 - 55, XD + 175, Y0 + 115, f"/home/claude/letsara/pranchas/ISO-{P['marca']}-consolo.png", titulo="ISOMÉTRICO — CONSOLOS", subtitulo="sem escala")

    # ------------------------------------------------------------ tabelas
    y = Q[3] - 6
    y = pr.tabela(XC, y, f"MARCAS — {P['familia']}", ["MARCA", "POSIÇÃO", "QT", "CONSOLOS (nível do assento, face)", "INSERTOS"], P["marcas"], [16, 22, 8, 92, 44], h_lin=6.0)
    L_N1 = round((L_TOT - 80) / 10)
    EXT_B, EXT_H = B - 2 * COB, H - 2 * COB
    barras = [dict(pos="N1", diam=20.0, qtd=len(xy), comp=L_N1, trechos=[f"{L_N1}"]),
              dict(pos="N2", diam=8.0, qtd=n_est, comp=round((2 * (EXT_B + EXT_H) + 160) / 10), forma=[(0, 0), (EXT_B / 10, 0), (EXT_B / 10, EXT_H / 10), (0, EXT_H / 10), (0, 0), (2, 2)], trechos=[f"{EXT_B/10:g}", f"{EXT_H/10:g}", "", ""])]
    if P["grampos"]:
        barras.append(dict(pos="N3", diam=8.0, qtd=len(P["grampos"]) * n_est, comp=round((EXT_H + 160) / 10), forma=[(0, 6), (0, 0), (EXT_H / 10, 0), (EXT_H / 10, 6)], trechos=["8", f"{EXT_H/10:g}", "8"]))
    n_cons = len(cons)
    PWc = (H if c0["face"] in "AC" else B)
    barras += [dict(pos="N4", diam=c0["d_tir"], qtd=c0["n_tir"] * n_cons, comp=round((2 * (PWc + c0["proj"] - 80) + 300) / 10), forma=[(0, 15), (0, 0), (85, 0), (85, 34), (0, 34), (0, 49)], trechos=["15", f"{(PWc + c0['proj'] - 80)/10:.0f}", "34", "", "15"]),
               dict(pos="N5", diam=10.0, qtd=2 * n_cons, comp=round((2 * (340 + PWc + c0["proj"] - 80) + 160) / 10), forma=[(0, 0), (70, 0), (70, 34), (0, 34), (0, 0), (2, 2)], trechos=[f"{(PWc + c0['proj'] - 80)/10:.0f}", "34", "", ""]),
               dict(pos="N6", diam=8.0, qtd=len(range(60, c0["proj"] - 40, 80)) * n_cons, comp=round((2 * (340 + 400) + 160) / 10), forma=[(0, 0), (34, 0), (34, 40), (0, 40), (0, 0), (2, 2)], trechos=["34", "40", "", ""])]
    ta = pr.tabela_croqui(XC, y - 4, barras, h_lin=9.0)
    y = ta["y_base"]
    y = pr.tabela(XC, y - 4, f"INSERTOS POR PILAR ({P['marca']}) — dimensões em mm", ["MARCA", "DESCRIÇÃO", "QT", "POSIÇÃO"], P["insertos"], [14, 100, 10, 58])
    qd = [["MARCA", P["marca"], "SEÇÃO", f"{B/10:g} × {H/10:g} cm"], ["COMPRIMENTO", f"{L_TOT/10:g} cm", "CONCRETO", "C40"],
          ["VOLUME", f"{f(V, 2)} m³", "PESO", f"{f(PESO/10, 2)} t"], ["AÇO CA-50", f"{f(ta['total_kg'], 0)} kg", "TAXA", f"{f(len(xy) * 3.14 / (B * H / 100) * 100, 2)} %"],
          ["QUANTIDADE", f"{P['qtd']}", "COBRIMENTO", "3,0 cm (CAA II)"]]
    y = pr.tabela(XC, y - 4, "QUADRO DA PEÇA", ["ITEM", "VALOR", "ITEM", "VALOR"], qd, [30, 60, 30, 62])
    y = pr.tabela(XC, y - 4, "MEMÓRIA RESUMIDA (NBR 6118:2023)", ["VERIFICAÇÃO", "RESULTADO"], P["memoria"], [70, 112])
    y = pr.legenda_armadura(XC, y - 4, False)
    pr.notas(XC, y - 4, P["notas"] + ["Cotas de concreto em cm, chaparia em mm, níveis em m. Não medir no desenho. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."], 182)
    pr.posicoes_desenho.add("N1")
    avisos = pr.salvar(f"/home/claude/letsara/pranchas/{P['desenho']}")
    print(P["desenho"], len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
    for a in avisos:
        if a[0] == "ERRO" or "sobrep" in a[1]:
            print(a)


def consolo(face, z_assento, tipo, larg, proj, h, hp, pino=("PN-1", 20, 700, 300, 175), neo=(300, 150, 10), tir=("3 Ø16", 3, 16.0)):
    return dict(face=face, z=z_assento + 1000, tipo=tipo, larg=larg, proj=proj, h=h, hp=hp, pino_nome=pino[0], pino_d=pino[1], pino_L=pino[2],
                pino_emb=pino[3], pino_x=pino[4], neo=list(neo), tir=tir[0], n_tir=tir[1], d_tir=tir[2])


def dados_pc():
    z_i110 = 8190                                                   # assento da I110: topo 8,88 − dente 0,66 − neoprene 0,03
    cons = [consolo("A", 8514, "CP-TS", 400, 300, 450, 250), consolo("C", 8489, "CP-TS", 400, 300, 450, 250),
            consolo("B", z_i110, "CP-I110", 500, 400, 500, 300, ("PN-2", 25, 900, 350, 200), (300, 250, 30), ("4 Ø16", 4, 16.0)),
            consolo("D", z_i110, "CP-I110", 500, 400, 500, 300, ("PN-2", 25, 900, 350, 200), (300, 250, 30), ("4 Ø16", 4, 16.0))]
    xy = [(sx * 202, sy * 202) for sx in (-1, 1) for sy in (-1, 1)] + [(sx * 67, sy * 202) for sx in (-1, 1) for sy in (-1, 1)] + [(sx * 202, sy * 67) for sx in (-1, 1) for sy in (-1, 1)]
    return dict(marca="PC-01", qtd=2, B=500, H=500, L_CAL=1000, Z_TOP=8880, al=[8880 + 1000 - 3000, 1000 + 2000], consolos=cons, xy=xy, grampos=[],
                est=dict(s_corr=150, s_dens=100, zona=1500), vistas=["A", "B", "C"], ip01=[],
                desenho="ND-LET-PC01", conteudo="PILARES CENTRAIS PC-01 E PC-02 (50×50) — EIXO C — FÔRMA, ARMAÇÃO, INSERTOS E LOCAÇÃO",
                posicao="POSIÇÃO: eixo C, linhas 2 e 4 (PC-01) e P13 (PC-02, sem CP-TS)", familia="PILARES CENTRAIS 50×50 (EIXO C)",
                kp=[("P8A", 20.05, 10.05, 500, 500, "PC-01"), ("P11", 20.05, 29.36, 500, 500, "PC-01"), ("P13", 20.05, 53.05, 500, 500, "PC-02")],
                marcas=[["PC-01", "C2, C4", 2, "CP-I110 +8,190 (B e D); CP-TS +8,489 (C) e +8,514 (A)", "2 AL-2"],
                        ["PC-02", "C, P13", 1, "CP-I110 +8,190 (B e D)", "2 AL-2"],
                        ["PC-??", "C8 ?", "?", "apoio da V405 — confirmar no R01", ""]],
                insertos=[["PN-2", "Pino Ø25 CA-50 L=900 (350 no consolo) — CP-I110", 2, "consolos B e D"], ["PN-1", "Pino Ø20 CA-50 L=700 (300 no consolo) — CP-TS", 2, "consolos A e C"],
                          ["NEO-2", "Neoprene 300×250×30 fretado (3 camadas)", 2, "CP-I110"], ["NEO-1", "Neoprene 300×150×10 c/ furo Ø30", 2, "CP-TS"],
                          ["AL-2", "Alça laço cordoalha Ø12,7 (2 pernas 700)", 2, "face A: 300 do topo; 200 da base"]],
                memoria=[["Nd (I110 + 2 TS-01 + pp)", "≈ 1,4 × 600 = 840 kN"], ["λ (balanço 9,88 m, i = 14,4 cm)", "137 < 140 — método geral"], ["Armadura mínima (0,4 %)", "37,7 ≥ 10,0 cm²"],
                         ["ELU método geral (λu)", "a emitir na memória MC03"], ["Consolo CP-I110 (Vd 448 kN)", "4 Ø16 tirante; As,min atendida"], ["Estribos (18.4.3)", "s = 15 ≤ min(20; 50; 24) cm; sem grampos (barras a ≤ 16 cm dos cantos)"]],
                notas=["Concreto C40; 12 Ø20 retos de ponta a ponta; estribos N2 Ø8 c/15 (c/10 nos 150 cm do topo e no cálice), ganchos 135°.",
                       "Consolos CP-I110 nas faces B e D (eixo C): assento +8,190 = topo da I110 +8,880 − dente 66 − neoprene 3; pino PN-2 Ø25 no TB-2 da viga.",
                       "Consolos CP-TS nas faces A e C (só PC-01, linhas 2 e 4): assentos +8,489 (lado A, face C) e +8,514 (lado E, face A), pino PN-1 Ø20 no TB-1 da TS-01.",
                       "Topo do pilar em +8,880 (nível do topo da I110); as terças passam 86 mm acima. FACE D igual à FACE B (consolo CP-I110 +8,190).",
                       "! Apoio da V405 na linha 8: não há pilar central no modelo recebido — confirmar no R01 antes de fabricar."])


def dados_pm():
    cons = [consolo("A", 2450, "CP-MEZ", 400, 300, 450, 250), consolo("C", 2450, "CP-MEZ", 400, 300, 450, 250),
            consolo("A", 5850, "CP-MEZ", 400, 300, 450, 250), consolo("C", 5850, "CP-MEZ", 400, 300, 450, 250)]
    xy = [(sx * 152, sy * 252) for sx in (-1, 1) for sy in (-1, 1)] + [(sx * 152, sy * 84) for sx in (-1, 1) for sy in (-1, 1)] + [(0, 252), (0, -252)]
    return dict(marca="PM-01", qtd=2, B=400, H=600, L_CAL=1000, Z_TOP=6550, al=[6550 + 1000 - 2500, 1000 + 1500], consolos=cons, xy=xy, grampos=[-84, 84],
                est=dict(s_corr=150, s_dens=100, zona=1500), vistas=["A", "B", "C"], ip01=[], zoom=2.6,
                desenho="ND-LET-PM01", conteudo="PILARES DO MEZANINO PM-01 (40×60) — B2 E D2 — FÔRMA, ARMAÇÃO, INSERTOS E LOCAÇÃO",
                posicao="POSIÇÃO: linha 2, eixos B e D (P8 e P8B); consolos CP-MEZ nas faces A e C nos níveis +3,15 e +6,55", familia="PILARES DO MEZANINO 40×60",
                kp=[("P8", 9.87, 10.05, 600, 400, "PM-01"), ("P8B", 29.63, 10.05, 600, 400, "PM-01")],
                marcas=[["PM-01", "B2, D2", 2, "CP-MEZ +2,450 e +5,850 (A e C)", "2 AL-2"]],
                insertos=[["PN-1", "Pino Ø20 CA-50 L=700 (300 no consolo)", 4, "consolos CP-MEZ"], ["NEO-1", "Neoprene 300×150×10 c/ furo Ø30", 4, "CP-MEZ"],
                          ["AL-2", "Alça laço cordoalha Ø12,7 (2 pernas 700)", 2, "face A: 250 do topo; 150 da base"]],
                memoria=[["Nd (2 níveis de mezanino)", "≈ 1,4 × 2 × 383 = 1072 kN"], ["λ (balanço 7,55 m, i = 17,3 cm)", "87 — método geral"], ["Armadura mínima (0,4 %)", "31,4 ≥ 9,6 cm²"],
                         ["ELU método geral (λu)", "a emitir na memória MC03"], ["Consolo CP-MEZ (Vd 383 kN)", "3 Ø16 tirante (NBR 9062 7.3)"], ["Grampos (18.4.3)", "2 N3 por estribo (linhas a 8,4 cm do eixo)"]],
                notas=["Concreto C40; 10 Ø20 retos; estribos N2 Ø8 c/15 (c/10 nos 150 cm das pontas e no cálice), ganchos 135°; 2 grampos N3 por estribo.",
                       "Consolos CP-MEZ nas faces A e C (eixo da linha 2): assentos +2,450 e +5,850 (viga VM I90 com dente 45: nível − 25 − 45); pino PN-1 Ø20 no TB-1 da VM.",
                       "Topo do pilar em +6,550 (nível do piso superior do mezanino); a cobertura das linhas 1–2 apoia nas VB-01 e TS-01 L2, não neste pilar."])


if __name__ == "__main__":
    qual = sys.argv[1] if len(sys.argv) > 1 else "pc"
    prancha_pilar(dados_pc() if qual == "pc" else dados_pm())
