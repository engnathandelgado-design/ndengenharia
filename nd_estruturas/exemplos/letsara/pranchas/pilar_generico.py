"""Prancha genérica de pilar pré-moldado (em pé, faces A/B/C/D, consolos em qualquer face) — padrão ND.
Usada por PC-01/02 (centrais 50×50) e PM-01 (mezanino 40×60). Rodar: python pilar_generico.py pc | pm
Faces: A = x+, B = y+, C = x−, D = y−. Modelo em mm; cotas de concreto em cm; chaparia em mm."""
import json, math, subprocess, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha

f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from geometria import Y_LIN, X_FACH, X_EIXO, Y_P13
CONS_J = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/consolos.json"))
LG = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/ligacoes.json"))
ZF = lambda x: LG["Z0_TS"] + 0.03 * x
ASS_TS = lambda x: round((ZF(x) + 0.45 * (1 / (1 + 0.03 ** 2)) ** 0.5 - 0.01) * 1000)
Z_I130 = round(LG["Z_ASS_I130"] * 1000)                          # rev03: assento da I130 = topo − 1,30 + recorte 0,52 − neoprene 0,03
Z_TOP_C = round(LG["Z_TOPO_I130"] * 1000)                         # rev03: topo dos pilares centrais = topo da I130 (TS-01 apoiada no topo)
Z_TOP_CD = round(LG["Z_TOPO_I130_DIR"] * 1000)                    # rev04: metade do lado E do topo (degrau, NBR 9062 7.2.1.6: assentos horizontais)
_VMP = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/vm_meio_vaso.json"))["premissas"]
# rev04: VM meio vaso com dente: assento do CP-MEZ = piso − capa 5 − laje 20 − fita 1 − h da VM + recorte − neoprene 1
Z_MEZ_ASS = tuple(round(z - 260 - _VMP["h_pm"] * 1000 + _VMP["dente"]["recorte"] * 1000 - 10) for z in (3150, 6550))
H_C = {k: round(v["h_total_m"] * 1000) for k, v in CONS_J.items()}
IP_C = [1250 * k + 922 + 1000 for k in range(6)]    # rev06: CE-1 (centro)            # CE-1 das paredes internas (vistas C e G): fiadas 0 a 5 (até +7,50)
COB = 30
# direção horizontal de cada vista (olhando a face de fora, z para cima): (eixo, sinal) -> coordenada à direita
VISTA = {"A": ("y", 1), "B": ("x", -1), "C": ("y", -1), "D": ("x", 1)}
DIR = {"A": "B", "B": "C", "C": "D", "D": "A"}                    # face à direita de quem olha a face de fora
ESQ = {"A": "D", "B": "A", "C": "B", "D": "C"}
OPOSTA = {"A": "C", "B": "D", "C": "A", "D": "B"}


def prancha_pilar(P):
    B, H, L_CAL, Z_TOP = P["B"], P["H"], P["L_CAL"], P["Z_TOP"]
    L_TOT = L_CAL + Z_TOP
    D1 = P.get("d1", 20.0)
    AL = P["al"]
    cons = P["consolos"]
    REC = P.get("rec")                                                   # cabeça recuada: dict(z = nível abs (mm), d = {face: recuo mm})
    rd = (lambda fc: REC["d"].get(fc, 0)) if REC else (lambda fc: 0)
    z_rec = REC["z"] if REC else L_TOT
    HB, HH = B - rd("B") - rd("D"), H - rd("A") - rd("C")               # seção da cabeça (B–D × A–C)
    V = (B * H * z_rec + HB * HH * (L_TOT - z_rec)) / 1e9 + sum(c["larg"] * c["proj"] * c["h"] for c in cons) / 1e9
    PESO = V * 25
    json.dump(dict(B=B, H=H, L_TOT=L_TOT, consolos=cons, ip01=P.get("ip01", []), al=AL, marca=P["marca"], z_topo=Z_TOP / 1000, zoom=P.get("zoom", 3.2), rec=REC),
              open(f"/home/claude/letsara/pranchas/{P['marca']}_geom.json", "w"))
    subprocess.run([sys.executable, "/home/claude/letsara/pranchas/iso3d_pilar_gen.py", f"/home/claude/letsara/pranchas/{P['marca']}_geom.json",
                    "/home/claude/letsara/pranchas/"], check=True, capture_output=True)
    # armadura
    xy = P["xy"]
    EST = P["est"]
    z_est = sorted(set(list(range(50, EST["zona"] + L_CAL, EST["s_dens"])) + list(range(EST["zona"] + L_CAL, L_TOT - EST["zona"], EST["s_corr"])) +
                       list(range(L_TOT - EST["zona"], L_TOT - 40, EST["s_dens"]))))
    if REC:                                                              # corpo até o recuo; cabeça com estribos próprios (N14 c/10)
        z_est = [z for z in z_est if z <= z_rec + 40]
        z_cab = list(range(z_rec + 100, L_TOT - 40, 100))
        u0, u1 = -B / 2 + rd("D"), B / 2 - rd("B")
        w0, w1 = -H / 2 + rd("C"), H / 2 - rd("A")
        dentro = lambda u, w: u0 + 40 <= u <= u1 - 40 and w0 + 40 <= w <= w1 - 40
        sw = P.get("sobe_w")
        xy_sobe = [p_ for p_ in xy if dentro(*p_) and (sw is None or p_[1] <= sw)]
        xy_para = [p_ for p_ in xy if p_ not in xy_sobe]
        cantos = [(u, w) for u in (u0 + COB + 18, u1 - COB - 18) for w in (w0 + COB + 18, w1 - COB - 18)]
        n_in = P.get("n13_inner", 0)
        if n_in:
            cantos += [(u0 + COB + 18 + k * (u1 - u0 - 2 * (COB + 18)) / (n_in - 1), w1 - COB - 16) for k in range(n_in)]
        xy_cab = []
        for c_ in cantos:
            if all(math.hypot(c_[0] - a, c_[1] - b) > 40 for a, b in xy_sobe + xy_cab):
                xy_cab.append((round(c_[0]), round(c_[1])))
    else:
        z_cab, xy_sobe, xy_para, xy_cab = [], xy, [], []
    n_est = len(z_est)
    pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                            conteudo=P["conteudo"], desenho=P["desenho"], folha="01/01", fase="PARA APROVAÇÃO",
                            marca=P["marca"], qtd=P["qtd"], peso=f(PESO, 1), volume=f(V, 2)))
    pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL")
    pr.revisao("04", "16/10/2026", "NBR 9062: SEM CP-VT; CONSOLOS COM ALÇAS; NEOPRENES REVISTOS; CP-MEZ P/ DENTE DA VM; CP-VB 15×27×29 P/ DENTE DA VB; PL 14 Ø20")
    r06 = ["CE-1 DOS CONSOLES CS-1 DAS PLACAS (TREJOR) NO LUGAR DOS TRILHOS TR-1"]
    if P["marca"] in ("PL-07", "PL-08"):
        r06.insert(0, "ESPERAS ES-1F DO APOIO ST-1F DA ÚLTIMA TERÇA")
    if P["marca"].startswith("PG"):
        r06.insert(0, "CABEÇA A 2 cm DA TS-01; INSERTOS IL-1 (LIGAÇÃO EM y COM A TS-01)")
    pr.revisao("06", "17/10/2026", "; ".join(r06))
    Q = pr.quadro
    XC = Q[2] - 190
    Y0 = 92
    ESC = 20
    pr.ret(Q[0] + 4, Q[3] - 30, Q[0] + 560, Q[3] - 4, "CARIMBO")
    pr.texto(Q[0] + 10, Q[3] - 24, P["marca"], "grande", "TITULO")
    pr.texto(Q[0] + 62, Q[3] - 24, f"PILAR PRÉ-MOLDADO  {P.get('secao_txt', f'{H/10:g} × {B/10:g} cm (x × y)')}   ·   L = {L_TOT/10:g} cm (cálice {L_CAL/10:g} + {Z_TOP/10:g})   ·   C40   ·   {P['qtd']} {'peça' if P['qtd'] == 1 else 'peças'}", "titulo", "TITULO")
    pr.texto(Q[0] + 10, Q[3] - 14, P["posicao"] + f"   ·   PESO {f(PESO/10, 2)} t   ·   VOLUME {f(V, 2)} m³   ·   {P.get('faces_txt', 'FACES: A = x+, B = y+, C = x−, D = y−')}   ·   desenhado em pé, como montado", "nota", "TEXTO")

    # planta-chave 1:750
    kp = pr.vista("PLANTA-CHAVE", (Q[0] + 487, Q[3] - 172), 750, titulo="PLANTA-CHAVE", subtitulo=f"{P['marca']} hachurado", unidade="cm")
    Xm = lambda m: m * 1000
    for y in Y_LIN:
        kp.linha((Xm(-2.5), Xm(y)), (Xm(42.0), Xm(y)), "EIXO")
    for x in X_FACH:
        kp.linha((Xm(x), Xm(-2.5)), (Xm(x), Xm(85.5)), "EIXO")
    for i, y in enumerate(Y_LIN, 1):
        kp.circulo((Xm(-2.5), Xm(y)), 1100, "VISTA"); kp.texto((Xm(-2.5), Xm(y)), str(i), "nota", "MIDDLE_CENTER")
    for j, x in enumerate(X_FACH):
        kp.circulo((Xm(x), Xm(85.5)), 1100, "VISTA"); kp.texto((Xm(x), Xm(85.5)), "ABCDE"[j], "nota", "MIDDLE_CENTER")
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
        dr, dl = rd(DIR[face]), rd(ESQ[face])
        v.poli([(0, 0), (W, 0), (W, z_rec), (W - dr, z_rec), (W - dr, L_TOT), (dl, L_TOT), (dl, z_rec), (0, z_rec)], "VISTA", True)
        if REC and rd(face):
            v.linha((dl, z_rec), (W - dr, z_rec), "VISTA")
        AS = P.get("assento")                                                                # rev03: TS-01 apoiada no recuo (neoprene + pinos)
        if AS and REC:
            nx_, ny_ = AS["neo"][0], AS["neo"][1]
            if rd(face) and face == "A":                                                     # frontal: assento visto de frente
                v.chapa(W / 2 - ny_ / 2, z_rec, ny_, 10)
                for dy in AS["y_pinos"]:
                    v.ret(W / 2 + dy - AS["d"] / 2, z_rec - AS["emb"], AS["d"], AS["emb"], "OCULTA")
                    v.chapa(W / 2 + dy - AS["d"] / 2, z_rec + 10, AS["d"], AS["L"] - AS["emb"])
                v.chamada((W / 2 + AS["y_pinos"][-1], z_rec + 150), (14, 12), f"{len(AS['y_pinos'])} {AS['pino']} + {AS['neo_nome']}")
            elif dr or dl:                                                                   # lateral: degrau do recuo
                xa = (W - dr) if dr else dl
                sgn = 1 if dr else -1
                x_n0, x_n1 = sorted((xa + sgn * AS["x_neo"][0], xa + sgn * AS["x_neo"][1]))
                v.chapa(x_n0, z_rec, x_n1 - x_n0, 10)
                xp_ = xa + sgn * AS["x_pino"]
                v.ret(xp_ - AS["d"] / 2, z_rec - AS["emb"], AS["d"], AS["emb"], "OCULTA")
                v.chapa(xp_ - AS["d"] / 2, z_rec + 10, AS["d"], AS["L"] - AS["emb"])
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
                v.chamada((W / 2, zc - h + hp / 2), (12, -44 if c["tipo"] == "CP-I130" else -30), f"{c['tipo']} {larg/10:g}×{proj/10:g}×{h/10:g}" + (f"/{hp/10:g}" if hp != h else ""))
            elif c["face"] == OPOSTA[face]:
                v.ret((W - larg) / 2, zc - h, larg, h, "OCULTA")
            else:                                                                            # lateral: projeção para fora
                lado = 1 if (VISTA[face][0] == "y" and c["face"] == "B") or (VISTA[face][0] == "x" and c["face"] == "A") else -1
                lado *= sg if VISTA[face][0] == "y" else 1
                # regra: à direita da vista fica a face cuja coordenada cresce no sentido de `sg`
                lado = 1 if ((c["face"] == "B" and eixo == "y" and sg > 0) or (c["face"] == "D" and eixo == "y" and sg < 0) or
                             (c["face"] == "A" and eixo == "x" and sg > 0) or (c["face"] == "C" and eixo == "x" and sg < 0)) else -1
                x0 = W if lado > 0 else 0
                v.poli([(x0, zc - h), (x0 + lado * proj, zc - hp), (x0 + lado * proj, zc + proj * c.get("incl", 0.03)), (x0, zc)], "VISTA")
                v.ret(x0 + lado * c["pino_x"] - c["pino_d"] / 2, zc - c["pino_emb"], c["pino_d"], c["pino_emb"], "OCULTA")
                v.chapa(x0 + lado * c["pino_x"] - c["pino_d"] / 2, zc, c["pino_d"], c["pino_L"] - c["pino_emb"])
                v.chapa(x0 + (25 if lado > 0 else -25 - c["neo"][1]), zc, c["neo"][1], 10)
        for ip in P.get("ip01", []):                                                       # rev06: CE-1 = chapa de espera 380 × 330 na face
            F_ = ip["face"]                                                                # das placas, centrada (consoles CS-1 soldados)
            if F_ == face:
                for z in ip["z"]:
                    v.chapa((W - 380) / 2, z - 165, 380, 330)
            elif F_ != OPOSTA[face]:
                lado = 1 if ((F_ == "B" and eixo == "y" and sg > 0) or (F_ == "D" and eixo == "y" and sg < 0) or
                             (F_ == "A" and eixo == "x" and sg > 0) or (F_ == "C" and eixo == "x" and sg < 0)) else -1
                xt = (W - 12.5) if lado > 0 else 0
                for z in ip["z"]:
                    v.chapa(xt, z - 165, 12.5, 330)
                    v.ret(W - 162.5 if lado > 0 else 12.5, z - 148, 150, 16, "OCULTA"); v.ret(W - 162.5 if lado > 0 else 12.5, z + 132, 150, 16, "OCULTA")
        if face == "A":
            for z in AL:
                v.linha((W / 2 - 50, z), (W / 2 + 50, z), "METALICA"); v.circulo((W / 2 - 50, z), 6.35, "METALICA"); v.circulo((W / 2 + 50, z), 6.35, "METALICA")
        cf = [c for c in cons if c["face"] == face]
        zs = sorted(set([0, L_CAL] + [c["z"] for c in cf] + [c["z"] - c["h"] for c in cf] + ([z_rec] if REC else []) + [L_TOT]))
        v.cota_v(zs, 0, -9)
        ords = sorted(set([0, L_CAL] + [c["z"] for c in cons if c["face"] == face] + [z for ip in P.get("ip01", []) if ip["face"] == face for z in ip["z"]] + [L_TOT]))
        if len(ords) > 3:
            v.cota_ord_v(ords, W, 9, y0=0)
        v.cota_h([0, W], 0, -8)
        if REC and (dl or dr):
            v.cota_h(sorted(set([0, dl, W - dr, W])), L_TOT, 8, total=False)
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
    if REC:
        vA.marcador_corte((-20, (z_rec + L_TOT) / 2), (largura(P["vistas"][0]) + 20, (z_rec + L_TOT) / 2), "C", lado=1)
        nivel(vA, 0, z_rec, f"+{f((z_rec - L_CAL)/1000, 3)} recuo", -1)

    # ------------------------------------------------------------ ARMAÇÃO
    va = pr.vista("ARMAÇÃO", (xp, Y0), ESC, titulo="ARMAÇÃO", subtitulo="vista pela face A", unidade="cm")
    W = B
    dl_, dr_ = rd("D"), rd("B")
    va.poli([(0, 0), (W, 0), (W, z_rec), (W - dr_, z_rec), (W - dr_, L_TOT), (dl_, L_TOT), (dl_, z_rec), (0, z_rec)], "VISTA", True)
    for z in z_est:
        va.linha((COB, z), (W - COB, z), "ARM_TRANSV")
    for z in z_cab:
        va.linha((dl_ + COB, z), (W - dr_ - COB, z), "ARM_TRANSV")
    va.barra([(COB + 18, 40), (COB + 18, (L_TOT if not dl_ else z_rec) - 40)], "N1" if not dl_ else "N1A", len(xy_sobe) if not dl_ else len(xy_para), D1,
             comp_cm=round(((L_TOT if not dl_ else z_rec) - 80) / 10), ponto_rotulo=(COB + 18, 3000), desloc=(14, 12))
    va.linha((W - COB - 18, 40), (W - COB - 18, (L_TOT if not dr_ else z_rec) - 40), "ARMADURA")
    if REC:
        va.cota_v([z_rec, L_TOT], 0, -18, total=False)
        va.chamada((W / 2, z_rec - 100), (10, 6), "N1A param no recuo")
        va.chamada((W / 2, z_rec + 250), (14, 24), "N14 Ø8 c/10 (cabeça)")
        if dl_:
            va.linha((dl_ + COB + 18, z_rec - 600), (dl_ + COB + 18, L_TOT - 40), "ARMADURA")
    va.chamada((W - COB, 5000), (12, 10), f"N2 Ø8 c/{EST['s_corr']//10}" + (" + N3" if P["grampos"] else ""))
    va.chamada((W - COB, 600), (12, 10), f"N2 Ø8 c/{EST['s_dens']//10}" + (" + N3" if P["grampos"] else ""))
    va.cota_v([0, EST["zona"] + L_CAL, L_TOT - EST["zona"], L_TOT], 0, -9)
    if cons:
        va.chamada((W, max(cons, key=lambda c: c["h"])["z"] - 200), (10, 16), "N4/N5/N6 — DET. 1")
    va.texto((W / 2, L_TOT + 120), "ARMAÇÃO", "sub", "BOTTOM_CENTER")
    pr.posicoes_desenho.update({"N2"} | ({"N3"} if P["grampos"] else set()))
    xp += 40 + W / ESC

    # ------------------------------------------------------------ isométrico geral
    pr.imagem(xp + 5, Y0 - 10, xp + 120, Y0 + 540, f"/home/claude/letsara/pranchas/ISO-{P['marca']}-geral.png", titulo="ISOMÉTRICO", subtitulo="faces B e C; sem escala")

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
        v.ponto_barra((x, y), D1)
    v.cota_h([-B / 2, B / 2], -H / 2, -8); v.cota_v([-H / 2, H / 2], B / 2, 8)
    v.texto((0, H / 2 + 30), "FACE A", "min", "BOTTOM_CENTER"); v.texto((0, -H / 2 - 130), "FACE C", "min", "TOP_CENTER")
    v.texto((B / 2 + 110, 0), "FACE B", "min", "MIDDLE_LEFT", rot=90); v.texto((-B / 2 - 30, 0), "FACE D", "min", "MIDDLE_RIGHT", rot=90)
    v.chamada((-xy[0][0], xy[0][1]), (-10, 10), f"N1 — {len(xy)} Ø{D1:g}".replace(".", ","))
    v.chamada((-B / 2 + COB, 100), (-10, 0), "N2 Ø8")
    if P["grampos"]:
        v.chamada((0, P["grampos"][0]), (-10, -14), "N3 grampo Ø8")

    if REC:
        vc = pr.vista("CORTE C-C", (XD + 165, YS), 10, titulo="CORTE C-C", subtitulo="cabeça recuada", unidade="cm")
        u0, u1 = -B / 2 + rd("D"), B / 2 - rd("B")
        w0, w1 = -H / 2 + rd("C"), H / 2 - rd("A")
        vc.poli([(-B / 2, -H / 2), (B / 2, -H / 2), (B / 2, H / 2), (-B / 2, H / 2)], "OCULTA", fechada=True)
        pc = [(u0, w0), (u1, w0), (u1, w1), (u0, w1)]
        vc.poli(pc, "CORTADO", fechada=True); vc.hachura(pc, "AR-CONC", 0.03)
        vc.poli([(u0 + COB, w0 + COB), (u1 - COB, w0 + COB), (u1 - COB, w1 - COB), (u0 + COB, w1 - COB)], "ARM_TRANSV", fechada=True)
        for x_, y_ in xy_sobe:
            vc.ponto_barra((x_, y_), D1)
        for x_, y_ in xy_cab:
            vc.ponto_barra((x_, y_), 16.0)
        vc.cota_h([u0, u1], w0, -8); vc.cota_v([w0, w1], u1, 8)
        vc.chamada((xy_sobe[0][0], xy_sobe[0][1]) if xy_sobe else (0, w0 + 50), (-10, -12), f"N1 — {len(xy_sobe)} Ø{D1:g}".replace(".", ","))
        if xy_cab:
            vc.chamada(xy_cab[-1], (10, 12), f"N13 — {len(xy_cab)} Ø16")
        vc.chamada((u1 - COB, (w0 + w1) / 2), (10, 0), "N14 Ø8 c/10")

    # ------------------------------------------------------------ DETALHE 1 — consolo (1:10) e DETALHE 2 — base (1:20)
    YM = Q[3] - 455
    if cons:
        c0 = max(cons, key=lambda c: c["h"])
        d1 = pr.vista("DETALHE 1", (XD + 70, YM - 40), 10, titulo=f"DETALHE 1 — CONSOLO {c0['tipo']}", subtitulo="armadura e pino; NBR 9062:2017 7.3", unidade="cm")
        PW = largura(OPOSTA[c0["face"]]) if c0["face"] in "BD" else H
        PW = H if c0["face"] in "AC" else B
        zc0, Z1, Z2 = 1000, 400, 1450
        proj, h, hp = c0["proj"], c0["h"], c0["hp"]
        d1.poli([(-PW, Z1), (-PW, Z2), (0, Z2), (0, Z1)], "VISTA"); d1.interrupcao((-PW, Z1), (0, Z1)); d1.interrupcao((-PW, Z2), (0, Z2))
        d1.poli([(0, zc0 - h), (proj, zc0 - hp), (proj, zc0 + proj * c0.get("incl", 0.03)), (0, zc0)], "VISTA")
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
        d1.cota_v(sorted(set([zc0 - h, zc0 - hp, zc0] + ([zc0 + proj * c0.get("incl", 0.03)] if c0.get("incl", 0.03) else []))), proj, 10, total=False)
        d1.cota_h([0, c0["pino_x"], proj], zc0 - h, -8, total=False); d1.cota_h([-PW, 0], Z1, -8)
        d1.chamada((-PW + 300, zc0 - 55), (-4, 12), f"N4 — {c0['tir']} U ({(PW + proj - 80)/10:.0f} + 15)")
        d1.chamada((-200, zc0 - 250), (-6, -12), "N5 — 2 Ø10 (costura)")
        d1.chamada((140, zc0 - 300), (14, -24), f"N6 — {len(range(60, proj - 40, 80))} Ø8")
        d1.chamada((c0["pino_x"], zc0 + 350), (10, 10), f"{c0['pino_nome']} Ø{c0['pino_d']} {'roscado A36' if c0['pino_nome'] == 'PN-6' else 'CA-50'} L={c0['pino_L']/10:g}")
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
    y = pr.tabela(XC, y, f"MARCAS — {P['familia']}", ["MARCA", "POSIÇÃO", "QT", "CONSOLOS (face)", "INSERTOS"], P["marcas"], [16, 22, 8, 86, 50], h_lin=6.0)
    L_N1 = round((L_TOT - 80) / 10)
    EXT_B, EXT_H = B - 2 * COB, H - 2 * COB
    L_N1A = round((z_rec - 30 - 40) / 10 + 15)
    barras = ([dict(pos="N1", diam=D1, qtd=len(xy_sobe), comp=L_N1, trechos=[f"{L_N1}"], geo=dict(k="R", a=L_N1))] if xy_sobe else []) + \
             ([dict(pos="N1A", diam=D1, qtd=len(xy_para), comp=L_N1A, forma=[(0, 0), (85, 0), (85, 8)], trechos=[f"{L_N1A - 15}", "15"], geo=dict(k="L", a=L_N1A - 15, g=15))] if xy_para else []) + \
             ([dict(pos="N13", diam=16.0, qtd=len(xy_cab), comp=round((L_TOT - 40 - (z_rec - 600)) / 10), trechos=[f"{round((L_TOT - 40 - (z_rec - 600)) / 10)}"], geo=dict(k="R", a=round((L_TOT - 40 - (z_rec - 600)) / 10)))] if xy_cab else []) + \
             ([dict(pos="N14", diam=8.0, qtd=len(z_cab), comp=round((2 * (HB - 60 + HH - 60) + 160) / 10), forma=[(0, 0), ((HB - 60) / 10, 0), ((HB - 60) / 10, (HH - 60) / 10), (0, (HH - 60) / 10), (0, 0), (2, 2)], trechos=[f"{(HB-60)/10:g}", f"{(HH-60)/10:g}", "", ""], geo=dict(k="E", a=(HH - 60) / 10, b=(HB - 60) / 10))] if z_cab else []) + [
              dict(pos="N2", diam=P.get("d_est", 8.0), qtd=n_est, comp=round((2 * (EXT_B + EXT_H) + 160) / 10), forma=[(0, 0), (EXT_B / 10, 0), (EXT_B / 10, EXT_H / 10), (0, EXT_H / 10), (0, 0), (2, 2)], trechos=[f"{EXT_B/10:g}", f"{EXT_H/10:g}", "", ""], geo=dict(k="E", a=EXT_H / 10, b=EXT_B / 10))]
    if P["grampos"]:
        barras.append(dict(pos="N3", diam=8.0, qtd=len(P["grampos"]) * n_est, comp=round((EXT_B + 160) / 10), forma=[(0, 6), (0, 0), (EXT_B / 10, 0), (EXT_B / 10, 6)], trechos=["8", f"{EXT_B/10:g}", "8"], geo=dict(k="G", a=EXT_B / 10, g=8)))
    n_ce = sum(len(i["z"]) for i in P.get("ip01", []))
    if n_ce:                                                                               # rev06b: N18 = 2 grampos U Ø10 por CE-1 (ND-LET-PP01 det. 5)
        barras.append(dict(pos="N18", diam=10.0, qtd=2 * n_ce, comp=96, forma=[(0, 45), (0, 0), (6, 0), (6, 45)], trechos=["45", "6", "45"], geo=dict(k="U", a=45, b=6, g=0)))
        pr.posicoes_desenho.add("N18")
    grupos, arm_cons = {}, []
    for c in cons:
        PWc = (H if c["face"] in "AC" else B)
        grupos.setdefault((c["n_tir"], c["d_tir"], c["proj"], PWc, c["larg"], c["h"]), []).append(c)
    nomes_pos = [("N4", "N5", "N6"), ("N7", "N8", "N9"), ("N10", "N11", "N12"), ("N15", "N16", "N17")]
    for k, ((nt, dt, proj, PWc, lg, hc), cs) in enumerate(grupos.items()):
        pa, pb, pc = nomes_pos[k]
        n_cons = len(cs)
        tipos = "/".join(sorted(set(c["tipo"] for c in cs)))
        lgu, wu, hu = round((PWc + proj - 80) / 10), round((lg - 60) / 10), round((hc - 60) / 10)       # perna do U, largura útil e altura útil (cm)
        barras += [dict(pos=pa, diam=dt, qtd=nt * n_cons, comp=2 * lgu + wu + 30, forma=[(0, 15), (0, 0), (85, 0), (85, 34), (0, 34), (0, 49)], trechos=["15", f"{lgu}", f"{wu}", "", "15"],
                        geo=dict(k="U", a=lgu, b=wu, g=15)),
                   dict(pos=pb, diam=10.0, qtd=2 * n_cons, comp=2 * (lgu + wu) + 16, forma=[(0, 0), (70, 0), (70, 34), (0, 34), (0, 0), (2, 2)], trechos=[f"{lgu}", f"{wu}", "", ""],
                        geo=dict(k="E", a=lgu, b=wu)),
                   dict(pos=pc, diam=8.0, qtd=len(range(60, proj - 40, 80)) * n_cons, comp=2 * (wu + hu) + 16, forma=[(0, 0), (34, 0), (34, 40), (0, 40), (0, 0), (2, 2)], trechos=[f"{wu}", f"{hu}", "", ""],
                        geo=dict(k="E", a=wu, b=hu))]
        arm_cons.append(dict(pos=(pa, pb, pc), tipos=tipos, n=n_cons, nt=nt, dt=dt, proj=proj, PW=PWc, larg=lg, h=hc, n6=len(range(60, proj - 40, 80)),
                             faces=[(c["face"], c["z"], c["tipo"]) for c in cs], incl=cs[0].get("incl", 0.03)))
        pr.posicoes_desenho.update({pa, pb, pc})
        if k > 0:
            va.chamada((W, cs[0]["z"] - 150), (10, -16), f"{pa}/{pb}/{pc} — {tipos} ({nt} Ø{dt:g} tirante)".replace(".", ","))
    area_f = (2 * (B + H) * z_rec + 2 * (HB + HH) * (L_TOT - z_rec) + B * H + (B * H - HB * HH) +
              sum(2 * c["proj"] * c["h"] + c["larg"] * c["h"] + c["larg"] * c["proj"] - c["larg"] * c["h"] for c in cons)) / 1e6
    json.dump(dict(marca=P["marca"], qtd=P["qtd"], desenho=P["desenho"], posicao=P["posicao"], B=B, H=H, L_TOT=L_TOT, L_CAL=L_CAL, Z_TOP=Z_TOP, COB=COB,
                   rec=REC, z_rec=z_rec, HB=HB, HH=HH, D1=D1, xy=xy, xy_sobe=xy_sobe, xy_para=xy_para, xy_cab=xy_cab, grampos=P["grampos"],
                   z_est=z_est, z_cab=z_cab, est=EST, d_est=P.get("d_est", 8.0), cons=[dict(face=c["face"], z=c["z"], tipo=c["tipo"], larg=c["larg"], proj=c["proj"], h=c["h"], hp=c["hp"], incl=c.get("incl", 0.03)) for c in cons],
                   arm_cons=arm_cons, barras=barras, V=V, area_forma=area_f, al=AL, n_ip=sum(len(i["z"]) for i in P.get("ip01", []))),
              open(f"/home/claude/letsara/pranchas/arm/{P['marca']}.json", "w"), ensure_ascii=False, indent=1)
    if P.get("so_arm"):
        return
    ta = pr.tabela_croqui(XC, y - 4, barras, h_lin=9.0)
    y = ta["y_base"]
    y = pr.tabela(XC, y - 4, f"INSERTOS POR PILAR ({P['marca']}) — dimensões em mm", ["MARCA", "DESCRIÇÃO", "QT", "POSIÇÃO"], P["insertos"], [14, 100, 10, 58])
    qd = [["MARCA", P["marca"], "SEÇÃO", f"{H/10:g} × {B/10:g} cm (x × y)"], ["COMPRIMENTO", f"{L_TOT/10:g} cm", "CONCRETO", "C40"],
          ["VOLUME", f"{f(V, 2)} m³", "PESO", f"{f(PESO/10, 2)} t"], ["AÇO CA-50", f"{f(ta['total_kg'], 0)} kg", "TAXA", f"{f(len(xy) * 3.1416 * (D1 / 10) ** 2 / 4 / (B * H / 100) * 100, 2)} %"],
          ["QUANTIDADE", f"{P['qtd']}", "COBRIMENTO", "3,0 cm (CAA II)"]] + ([["CABEÇA", f"{HB/10:g} × {HH/10:g} cm acima de +{f((z_rec - L_CAL)/1000, 2)}", "", ""]] if REC else [])
    y = pr.tabela(XC, y - 4, "QUADRO DA PEÇA", ["ITEM", "VALOR", "ITEM", "VALOR"], qd, [30, 60, 30, 62])
    y = pr.tabela(XC, y - 4, "MEMÓRIA RESUMIDA (NBR 6118:2023)", ["VERIFICAÇÃO", "RESULTADO"], P["memoria"], [70, 112])
    y = pr.legenda_armadura(XC, y - 4, False)
    pr.notas(XC, y - 4, P["notas"] + ["Cotas de concreto em cm, chaparia em mm, níveis em m. Não medir no desenho. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."], 182)
    pr.posicoes_desenho.update({b["pos"] for b in barras if b["pos"] in ("N1", "N1A", "N13", "N14")})
    pr.posicoes_desenho.discard("N1") if not xy_sobe else None
    avisos = pr.salvar(f"/home/claude/letsara/pranchas/{P['desenho']}")
    print(P["desenho"], len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
    for a in avisos:
        if a[0] == "ERRO" or "sobrep" in a[1]:
            print(a)


def consolo(face, z_assento, tipo, larg, proj, h, hp, pino=("PN-1", 20, 700, 300, 175), neo=(300, 150, 10), tir=("3 Ø16", 3, 16.0)):
    return dict(face=face, z=z_assento + 1000, tipo=tipo, larg=larg, proj=proj, h=h, hp=hp, pino_nome=pino[0], pino_d=pino[1], pino_L=pino[2],
                pino_emb=pino[3], pino_x=pino[4], neo=list(neo), tir=tir[0], n_tir=tir[1], d_tir=tir[2])


KP_CEN = [("P8A", X_EIXO["C"], Y_LIN[1], 400, 600, "PC-01"), ("P11", X_EIXO["C"], Y_LIN[3], 400, 400, "PC-02"), ("P13", X_EIXO["C"], Y_P13, 600, 600, "PC-03"),
          ("P8", X_EIXO["B"], Y_LIN[1], 400, 600, "PM-01"), ("P8B", X_EIXO["D"], Y_LIN[1], 400, 600, "PM-01"),
          ("P9", 9.87, Y_LIN[3], 400, 400, "PG-01"), ("P12", 29.63, Y_LIN[3], 400, 400, "PG-03"), ("P10", 15.195, Y_LIN[3], 250, 250, "PG-02"), ("P10", 24.305, Y_LIN[3], 250, 250, "PG-04")]
F = lambda v: f"{v/1000:.3f}".replace(".", ",")
TS_E, TS_A = ASS_TS(20.175), ASS_TS(19.325)
I130 = lambda face: consolo(face, Z_I130, "CP-I130", 500, 400, H_C["CP-I130"], H_C["CP-I130"], ("PN-2", 25, 900, 350, 200), (300, 200, 31), (CONS_J["CP-I130"]["tirante"].split(" (")[0], CONS_J["CP-I130"]["n_ramos"], CONS_J["CP-I130"]["d_tir"]))   # rev04: NEO-2 200 × 300 fretado; a2 = 10 cm
TSC = lambda face, z: consolo(face, z, "CP-TS", 400, 300, H_C["CP-TS"], H_C["CP-TS"])
MEZ = lambda face, z: consolo(face, z, "CP-MEZ", 400, 350, H_C["CP-MEZ"], H_C["CP-MEZ"], ("PN-1", 20, 700, 300, 186), (300, 150, 10), (CONS_J["CP-MEZ"]["tirante"].split(" (")[0], CONS_J["CP-MEZ"]["n_ramos"], CONS_J["CP-MEZ"]["d_tir"]))   # rev04: dente da VM meio vaso
EST_STD = dict(s_corr=150, s_dens=100, zona=1500)
NOTA_CONS = "Consolos sem chanfro: altura = recorte do dente da viga − neoprene, fundo do consolo alinhado ao fundo da viga (CP-MEZ 29, CP-I130 49 cm — memória consolos.json, NBR 9062:2017 7.3). Tirante em alças horizontais (7.3.3: a2 ≥ c + 3,5Ø), costura Ø8 c/10 em 2/3 d."


def bars_ret(B, H, nb, nh, c=48):
    """Barras no perímetro: nb ao longo de B (faces de cima/baixo da seção), nh ao longo de H (inclui cantos)."""
    xs = [-B / 2 + c + k * (B - 2 * c) / (nb - 1) for k in range(nb)]
    ys = [-H / 2 + c + k * (H - 2 * c) / (nh - 1) for k in range(nh)]
    pts = {(round(x), round(y)) for x in xs for y in (ys[0], ys[-1])} | {(round(x), round(y)) for y in ys for x in (xs[0], xs[-1])}
    return sorted(pts)


def base(marca, qtd, B, H, ztop, cons, xy, desenho, conteudo, posicao, familia, marcas, insertos, notas, ip01=(), d1=20.0, grampos=(), vistas=("A", "B", "C"), zoom=3.2):
    return dict(marca=marca, qtd=qtd, B=B, H=H, L_CAL=1000, Z_TOP=ztop, al=[ztop + 1000 - 2500, 1000 + 1500], consolos=cons, xy=xy, grampos=list(grampos),
                est=EST_STD, vistas=list(vistas), ip01=list(ip01), d1=d1, zoom=zoom, desenho=desenho, conteudo=conteudo, posicao=posicao, familia=familia,
                kp=KP_CEN, marcas=marcas, insertos=insertos, memoria=[], notas=notas)


def dados_pc1():
    cons = [I130("B"), MEZ("A", Z_MEZ_ASS[0]), MEZ("C", Z_MEZ_ASS[0]), MEZ("A", Z_MEZ_ASS[1]), MEZ("C", Z_MEZ_ASS[1])]
    return base("PC-01", 1, 600, 400, Z_TOP_C, cons, bars_ret(600, 400, 4, 3), "ND-LET-PC01",
                "PILAR CENTRAL PC-01 (P8A, 40×60) — EIXO C, LINHA 2 — FÔRMA, ARMAÇÃO, INSERTOS E LOCAÇÃO",
                "POSIÇÃO: eixo C, linha 2 (P8A); 40 em x × 60 em y", "PILAR CENTRAL PC-01",
                [["PC-01", "P8A (C2)", 1, "topo: 2 TS-01 (oblongo); CP-I130 (B); 2 CP-MEZ (A, C)", "6 CE-1 (B); 2 AL-2"]],
                [["PN-2", "Pino Ø25 CA-50 L=900 (350 no consolo) — CP-I130", 1, "face B"], ["PN-1", "Pino Ø20 CA-50 L=700 — CP-MEZ", 4, "faces A e C"], ["PN-5", "Pino Ø20 CA-50 L=600 (300 no pilar) — topo (TS-01)", 4, "topo, x ±115, y ±100"],
                 ["NEO-2", "Neoprene 300×200×31 fretado (rev04)", 1, "CP-I130"], ["NEO-5", "Neoprene 300×150×10 c/ furo Ø30 (dente da VM)", 4, "CP-MEZ"], ["BA-1", "Bainha corrugada Ø50 horizontal (N11)", 4, "12 cm acima da VM"], ["IP-02", "Trilho TR-2 40/22 L=250 vertical (CT-1)", 4, "face do CP-MEZ"], ["NEO-3", "Neoprene 100×300×10 c/ 2 furos Ø30", 2, "topo (TS-01)"],
                 ["CE-1", "CE-1 380×330×16 + 4 pinos Ø16 + 2 N18 (CS-1, vista G)", 6, "face B, centrada, fiadas 0 a 5"], ["AL-2", "Alça laço cordoalha Ø12,7", 2, "face A"]],
                ["Concreto C40; 10 Ø20 retos de ponta a ponta; estribos N2 Ø8 c/15 (c/10 nos 150 cm do topo e no cálice), ganchos 135°.", NOTA_CONS,
                 f"TS-01 da linha 2 apoiadas no topo do pilar (topo horizontal em 2 níveis: +{F(Z_TOP_C)} na metade do lado A e +{F(Z_TOP_CD)} na metade do lado E, degrau no eixo C), NEO-3 100×300 e 2 pinos PN-5 Ø20 por TS-01, com os tubos TB-3 da viga preenchidos com mastique (sem graute: a viga desliza ±15 mm em x, o mezanino já trava o pilar); CP-I130 na face B (+{F(Z_I130)}) para a ponta da V407; CP-MEZ nas faces A e C para as VM dos dois níveis.",
                 f"Topo do pilar horizontal em 2 níveis: +{F(Z_TOP_C)} (metade do lado A) e +{F(Z_TOP_CD)} (metade do lado E), degrau de {Z_TOP_CD - Z_TOP_C} mm no eixo C, igual ao topo da I130. CE-1 (chapa de espera dos consoles CS-1) na face B para as placas da parede interna da linha 2 (vista G)."],
                ip01=[dict(face="B", z=IP_C)])


def dados_pc2():
    cons = [I130("B"), I130("D")]
    return base("PC-02", 1, 400, 400, Z_TOP_C, cons, bars_ret(400, 400, 3, 3), "ND-LET-PC02",
                "PILAR CENTRAL PC-02 (P11, 40×40) — EIXO C, LINHA 4 — FÔRMA, ARMAÇÃO, INSERTOS E LOCAÇÃO",
                "POSIÇÃO: eixo C, linha 4 (P11), parede dos portões", "PILAR CENTRAL PC-02",
                [["PC-02", "P11 (C4)", 1, "topo: 2 TS-01; CP-I130 (B, D)", "6 CE-1 (B); 2 AL-2"]],
                [["PN-2", "Pino Ø25 CA-50 L=900 — CP-I130", 2, "faces B e D"], ["PN-5", "Pino Ø20 CA-50 L=600 (300 no pilar) — topo (TS-01)", 4, "topo, x ±115, y ±100"],
                 ["NEO-2", "Neoprene 300×200×31 fretado (rev04)", 2, "CP-I130"], ["NEO-3", "Neoprene 100×300×10 c/ 2 furos Ø30", 2, "topo (TS-01)"],
                 ["CE-1", "CE-1 380×330×16 + 4 pinos Ø16 + 2 N18 (CS-1, vista C)", 6, "face B, centrada"], ["AL-2", "Alça laço cordoalha Ø12,7", 2, "face A"]],
                ["Concreto C40; 8 Ø20 retos; estribos N2 Ø8 c/15 (c/10 nos 150 cm do topo e no cálice), ganchos 135°.", NOTA_CONS,
                 f"CP-I130 nas faces B (V406) e D (V407), assento +{F(Z_I130)}; TS-01 da linha 4 apoiadas no topo (topo horizontal em 2 níveis: +{F(Z_TOP_C)} lado A / +{F(Z_TOP_CD)} lado E), NEO-3 100×300 e 2 pinos PN-5 Ø20 por TS-01, grauteados nos tubos TB-3.",
                 "CE-1 (chapa de espera dos consoles CS-1) na face B para as placas da parede dos portões (vista C, fiadas até +7,50)."],
                ip01=[dict(face="B", z=IP_C)])


def dados_pc3():
    cons = [I130("B"), I130("D")]
    return base("PC-03", 1, 600, 600, Z_TOP_C, cons, bars_ret(600, 600, 4, 4), "ND-LET-PC03",
                "PILAR CENTRAL PC-03 (P13, 60×60) — EIXO C — FÔRMA, ARMAÇÃO, INSERTOS E LOCAÇÃO",
                "POSIÇÃO: eixo C, y = 54,575 m (P13), entre as V406 e V405", "PILAR CENTRAL PC-03",
                [["PC-03", "P13", 1, "CP-I130 (B, D)", "2 AL-2"]],
                [["PN-2", "Pino Ø25 CA-50 L=900 — CP-I130", 2, "faces B e D"], ["NEO-2", "Neoprene 300×200×31 fretado (rev04)", 2, "CP-I130"],
                 ["AL-2", "Alça laço cordoalha Ø12,7", 2, "face A"]],
                ["Concreto C40; 12 Ø20 retos; estribos N2 Ø8 c/15 (c/10 nos 150 cm do topo e no cálice), ganchos 135°.", NOTA_CONS,
                 f"CP-I130 nas faces B (V405) e D (V406), assento +{F(Z_I130)}; sem TS-01 (P13 fica entre as linhas 6 e 7)."])


def dados_pm():
    cons = [MEZ("A", Z_MEZ_ASS[0]), MEZ("C", Z_MEZ_ASS[0]), MEZ("A", Z_MEZ_ASS[1]), MEZ("C", Z_MEZ_ASS[1])]
    return base("PM-01", 2, 600, 400, 6550, cons, bars_ret(600, 400, 4, 3), "ND-LET-PM01",
                "PILARES DO MEZANINO PM-01 (P8 E P8B, 40×60) — FÔRMA, ARMAÇÃO, INSERTOS E LOCAÇÃO",
                "POSIÇÃO: linha 2, eixos B e D (P8 e P8B); 40 em x × 60 em y", "PILARES DO MEZANINO PM-01",
                [["PM-01", "P8, P8B", 2, "2 CP-MEZ (A, C)", "6 CE-1 (B); 2 AL-2"]],
                [["PN-1", "Pino Ø20 CA-50 L=700 (300 no consolo)", 4, "consolos CP-MEZ"], ["NEO-5", "Neoprene 300×150×10 c/ furo Ø30 (dente da VM)", 4, "CP-MEZ"], ["BA-1", "Bainha corrugada Ø50 horizontal (N11)", 4, "12 cm acima da VM"], ["IP-02", "Trilho TR-2 40/22 L=250 vertical (CT-1)", 4, "face do CP-MEZ"],
                 ["CE-1", "CE-1 380×330×16 + 4 pinos Ø16 + 2 N18 (CS-1, vista G)", 6, "face B, centrada"], ["AL-2", "Alça laço cordoalha Ø12,7", 2, "face A"]],
                ["Concreto C40; 10 Ø20 retos; estribos N2 Ø8 c/15 (c/10 nos 150 cm das pontas e no cálice), ganchos 135°.", NOTA_CONS,
                 f"CP-MEZ nas faces A e C: assentos +{F(Z_MEZ_ASS[0])} e +{F(Z_MEZ_ASS[1])} (VM meio vaso com dente Gerber: fundo do consolo = fundo da viga); pino PN-1 Ø20 no TB-1 do dente; trilho IP-02 para a cantoneira CT-1 antigiro.",
                 "Topo do pilar em +6,550 (piso superior do mezanino). CE-1 na face B para as placas da parede interna da linha 2 (vista G)."],
                ip01=[dict(face="B", z=IP_C)])


# rev06 (DEC-024): cabeça dos pilares dos portões a 2 cm do fundo da TS-01 da linha 4, ligada à viga em y por 2 cantoneiras
# L 102×102×9,5 (faces x do pilar) — 4 comprimentos → 4 marcas (mesma fôrma e armação por seção)
IL1 = ["IL-1", "Inserto rosqueado M16 hef 100 (cantoneira CL-P)", 2, "faces B e D, 75 do topo"]
NOTA_LIG = ("Cabeça a 2 cm do fundo da TS-01 da linha 4 (a viga sobe 3 % de A para E): em cada face lateral (B e D) uma cantoneira "
            "L 102×102×9,5 L = 250 (CL-P) parafusada com 1 M16 8.8 no inserto IL-1 (furo oblongo vertical 18 × 50, a TS-01 flete livre) e com 2 M16 8.8 "
            "nos insertos do fundo da TS-01; segura só em y a parede dos portões (Fd até 23 kN, cobertura_metalica.json). Portões livres até +7,40.")


def _pg(marca, nome, x, b, ztop, desenho, d1, est=None):
    secao = f"{b//10}×{b//10}"
    P = base(marca, 1, b, b, ztop, [], bars_ret(b, b, 2, 2), desenho,
             f"PILAR DOS PORTÕES {marca} ({nome}, {secao}) — LINHA 4, x = {x:.3f} m — FÔRMA, ARMAÇÃO, INSERTOS E LOCAÇÃO".replace(".", ","),
             f"POSIÇÃO: linha 4, x = {x:.3f} m ({nome}); topo +{ztop/1000:.2f} (2 cm abaixo da TS-01)".replace(".", ","), "PILARES DA PAREDE DOS PORTÕES",
             [["PG-01", "P9", 1, "sem consolo; topo +7,47", "CE-1 (B); 2 IL-1; 2 AL-2"], ["PG-02", "P10 (x 15,195)", 1, "sem consolo; topo +7,63", "CE-1 (B); 2 IL-1; 2 AL-2"],
              ["PG-04", "P10 (x 24,305)", 1, "sem consolo; topo +7,90", "CE-1 (B); 2 IL-1; 2 AL-2"], ["PG-03", "P12", 1, "sem consolo; topo +8,06", "CE-1 (B); 2 IL-1; 2 AL-2"]],
             [["CE-1", "CE-1 380×330×16 + 4 pinos Ø16 + 2 N18 (CS-1)", 5 if b == 400 else 6, "face B, centrada"], IL1,
              ["AL-2", "Alça laço cordoalha Ø12,7", 2, "face A"]],
             [("Concreto C40; 4 Ø20 retos (cantos); " if b == 400 else "Concreto C40; 4 Ø16 retos (cantos); ") + "estribos c/15 (c/10 nos 150 cm das pontas e no cálice), ganchos 135°.",
              NOTA_LIG,
              "Pilar de fechamento da parede dos portões (vista C): recebe as placas, a folha do portão e o vento; apoiado em y na TS-01 pela cabeça (modelo integrado r05)."],
             ip01=[dict(face="B", z=IP_C[:5] if b == 400 else IP_C)], d1=d1, zoom=2.8 if b == 400 else 2.4)
    if est:
        P |= dict(d_est=est)
    return P


def dados_pg1():
    return _pg("PG-01", "P9", 9.87, 400, 7470, "ND-LET-PG01", 20.0)


def dados_pg2():
    return _pg("PG-02", "P10a", 15.195, 250, 7630, "ND-LET-PG02", 16.0, 6.3)


def dados_pg3():
    return _pg("PG-03", "P12", 29.63, 400, 8060, "ND-LET-PG03", 20.0)


def dados_pg4():
    return _pg("PG-04", "P10b", 24.305, 250, 7900, "ND-LET-PG04", 16.0, 6.3)


DADOS = dict(pc1=dados_pc1, pc2=dados_pc2, pc3=dados_pc3, pm=dados_pm, pg1=dados_pg1, pg2=dados_pg2, pg3=dados_pg3, pg4=dados_pg4)


if __name__ == "__main__":
    for q in (sys.argv[1:] or list(DADOS)):
        prancha_pilar(DADOS[q]())
