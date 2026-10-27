"""geo_fixacao.py — geometria única das peças da fixação Trejor (rev06c), lida de fixacao_placas.json (GEO).
Sólidos para os isométricos (iso_nd) e lista de itens (nº, descrição, material, qtd, peso) de cada conjunto.

Eixos:
  NC-1  x a partir da ponta da placa (0–120), y a partir da boca (face interna da placa, 0–60), z a partir do fundo do nicho (0–200);
  CS-1  x no eixo do console, y a partir da face da CE-1 (rumo à placa), z a partir do topo da mesa.
Na montagem nominal: x_CS = x_NC − 60, y_CS = y_NC + a (25), z_CS = z_NC − (H − t_teto) + G (z_NC − 137,5).
"""
import json
import math
import iso_nd as I

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
FX = json.load(open(AQ + "fixacao_placas.json"))
G = FX["GEO"]
C, N, HX, T = G["CS1"], G["NC1"], G["hex"], G["tol"]
TCE = G.get("CE1", {}).get("t", 16.0)


def concretado(vista, largura_pilar):
    """rev06e (DEC-031): pilar concretado com a face C (placas) para cima — consoles na face C saem da fábrica soldados na CE-1
    e concretados com o pilar (CC-1, CC-1E, CC-1D). Nas faces laterais B/D (fôrma lateral, tem de abrir) e nas paredes internas
    a CE-1 vai rente e o CS-1 é soldado na obra. Fachadas A/I: o pilar de canto aparece pelo lado de 60 (face lateral)."""
    return vista in "BDEFHJ" or (vista in "AI" and round(largura_pilar) == 400)
RHO = 7.85e-6
A_NOM, G_NOM = T["a"], T["G"]
DZ = -(N["H"] - N["t_teto"]) + G_NOM            # z_CS = z_NC + DZ
DY = A_NOM
DX = -N["B"] / 2


def kg_ch(a, b, t, n=1):
    return n * a * b * t * RHO


def kg_red(d, L, n=1):
    return n * math.pi * d ** 2 / 4 * L * RHO


# ------------------------------------------------------------------ NC-1
def gr_pts(x0, x1, base=False):
    """grampo U no plano x-z, em y = y_gr: pernas soldadas no teto (sobe) ou na base (desce)."""
    if base:
        h = N["h_gr_base"]
        return [(x0, N["y_gr"], 0.0), (x0, N["y_gr"], -h), (x1, N["y_gr"], -h), (x1, N["y_gr"], 0.0)]
    h = N["h_gr_teto"]
    return [(x0, N["y_gr"], N["H"]), (x0, N["y_gr"], N["H"] + h), (x1, N["y_gr"], N["H"] + h), (x1, N["y_gr"], N["H"])]


def nc1_itens():
    B, H, P = N["B"], N["H"], N["P"]
    tt, tb, tf, tp, ta, ha = N["t_teto"], N["t_base"], N["t_fundo"], N["t_parede"], N["t_aba"], N["h_aba"]
    pf = P - tf
    L_gt = 2 * N["h_gr_teto"] + (N["x_gr"][0][1] - N["x_gr"][0][0])
    L_gb = 2 * N["h_gr_base"] + (N["x_gr"][0][1] - N["x_gr"][0][0])
    be, bd = N["aba_e"][1] - N["aba_e"][0], N["aba_d"][1] - N["aba_d"][0]
    it = [
        (1, "TETO", f"CH {tt:g} × {pf:g} × {B:g}", "ASTM A572 Gr.50", 1, kg_ch(B, pf, tt)),
        (2, "BASE", f"CH {tb:g} × {pf:g} × {B:g}", "ASTM A572 Gr.50", 1, kg_ch(B, pf, tb)),
        (3, "FUNDO", f"CH {tf:g} × {B:g} × {H:g}", "ASTM A572 Gr.50", 1, kg_ch(B, H, tf)),
        (4, "PAREDE LATERAL", f"CH {tp:g} × {pf:g} × {H - tt - tb:g}", "ASTM A36", 1, kg_ch(pf, H - tt - tb, tp)),
        (5, "ABA E (lado da ponta)", f"CH {ta:g} × {ha:g} × {be:g}", "ASTM A572 Gr.50", 1, kg_ch(be, ha, ta)),
        (6, "ABA D", f"CH {ta:g} × {ha:g} × {bd:g}", "ASTM A572 Gr.50", 1, kg_ch(bd, ha, ta)),
        (7, "GRAMPO U DO TETO", f"RED Ø{N['d_gr']:g} × {L_gt:g} (desenv.)", "ASTM A36", 2, kg_red(N["d_gr"], L_gt)),
        (8, "GRAMPO U DA BASE", f"RED Ø{N['d_gr']:g} × {L_gb:g} (desenv.)", "ASTM A36", 2, kg_red(N["d_gr"], L_gb)),
    ]
    return it


def nc1_solidos(explode=0.0):
    B, H, P = N["B"], N["H"], N["P"]
    tt, tb, tf, tp, ta, ha = N["t_teto"], N["t_base"], N["t_fundo"], N["t_parede"], N["t_aba"], N["h_aba"]
    pf = P - tf
    e = explode
    S = [I.caixa(0, B, 0, pf, H - tt, H, item=1, nome="teto").movido((0, 0, 1.2 * e)),
         I.caixa(0, B, 0, pf, 0, tb, item=2, nome="base").movido((0, 0, -1.0 * e)),
         I.caixa(0, B, pf, P, 0, H, item=3, nome="fundo").movido((0, 1.0 * e, 0)),
         I.caixa(B - tp, B, 0, pf, tb, H - tt, item=4, nome="parede").movido((0.9 * e, 0, 0)),
         I.caixa(N["aba_e"][0], N["aba_e"][1], 0, ta, H - tt - ha, H - tt, item=5, nome="aba E").movido((0, -1.0 * e, 0.45 * e)),
         I.caixa(N["aba_d"][0], N["aba_d"][1], 0, ta, H - tt - ha, H - tt, item=6, nome="aba D").movido((0, -1.0 * e, 0.45 * e))]
    for (x0, x1) in N["x_gr"]:
        S += I.barra_poli(gr_pts(x0, x1), N["d_gr"], item=7, cor=I.DOURADO)
        S[-1].item = 7
        S = S[:-3] + [s.movido((0, 0, 2.0 * e)) for s in S[-3:]]
        S += I.barra_poli(gr_pts(x0, x1, True), N["d_gr"], item=8, cor=I.DOURADO)
        S = S[:-3] + [s.movido((0, 0, -1.8 * e)) for s in S[-3:]]
    return S


# ------------------------------------------------------------------ CS-1
def alma_poli():
    a = C["alma"]
    return [(a["y0"], -C["mesa"]["t"]), (a["y1"], -C["mesa"]["t"]), (a["y1"], -a["h_ponta"]), (a["y0"], -a["h_raiz"])]


def cs1_itens():
    a, m, d, p, c = C["alma"], C["mesa"], C["dente"], C["ponta"], C["costas"]
    pol = alma_poli()
    area_alma = abs(sum(pol[i][0] * pol[(i + 1) % 4][1] - pol[(i + 1) % 4][0] * pol[i][1] for i in range(4))) / 2
    hc = c["z1"] - c["z0"]
    furo = math.pi * 18 ** 2 / 4
    return [
        (10, "COSTAS (solda de campo na CE-1)", f"CH {c['t']:g} × {c['b']:g} × {hc:g}", "ASTM A572 Gr.50", 1, kg_ch(c["b"], hc, c["t"])),
        (11, "ALMA", f"CH {a['t']:g} × {a['y1'] - a['y0']:g} × {a['h_raiz'] - m['t']:g}/{a['h_ponta'] - m['t']:g} (trapézio)", "ASTM A572 Gr.50", 2, area_alma * a["t"] * RHO),
        (12, "MESA (furo Ø18)", f"CH {m['t']:g} × {m['y1'] - m['y0']:g} × {m['b']:g}", "ASTM A572 Gr.50", 1, (m["b"] * (m["y1"] - m["y0"]) - furo) * m["t"] * RHO),
        (13, "DENTE", f"CH {d['t']:g} × {d['b']:g} × {d['h']:g}", "ASTM A572 Gr.50", 2, kg_ch(d["b"], d["h"], d["t"])),
        (14, "CHAPA DE PONTA (furo Ø18)", f"CH {p['t']:g} × {p['z1'] - p['z0']:g} × {p['b']:g}", "ASTM A572 Gr.50", 1, ((p["z1"] - p["z0"]) * p["b"] - furo) * p["t"] * RHO),
        (15, "PORCA SEXTAVADA M16 (soldada)", "M16 ISO 4032 cl. 8, rosca sobremedida p/ galv.", "aço cl. 8", 2, 0.033),
        (16, "PARAFUSO DE NÍVEL", f"M16 × {C['L_nivel']:g} ISO 4017 cl. 8.8, rosca total", "aço cl. 8.8 galv.", 1, 0.105),
        (17, "CONTRAPORCA FINA", "M16 ISO 4035 cl. 05", "aço galv.", 1, 0.018),
        (18, "PRISIONEIRO FRONTAL", f"M16 × {C['L_frontal']:g} ISO 4026 45H, sext. interno 8, ponta plana", "aço 45H zincado", 1, 0.068),
    ]


def cs1_solidos(explode=0.0, G=None, com_parafusos=True):
    a, m, d, p, c = C["alma"], C["mesa"], C["dente"], C["ponta"], C["costas"]
    G = G_NOM if G is None else G
    e = explode
    S = [I.caixa(-c["b"] / 2, c["b"] / 2, 0, c["t"], c["z0"], c["z1"], item=10, nome="costas").movido((0, -1.0 * e, 0))]
    for xa in (-a["x"], a["x"]):
        S.append(I.prisma(alma_poli(), "yz", xa - a["t"] / 2, xa + a["t"] / 2, item=11, nome="alma").movido((0.55 * e * (1 if xa > 0 else -1), 0, -0.6 * e)))
    S.append(I.caixa(-m["b"] / 2, m["b"] / 2, m["y0"], m["y1"], -m["t"], 0, item=12, nome="mesa"))
    for sg in (-1, 1):
        x0, x1 = sorted((sg * d["x0"], sg * (d["x0"] + d["b"])))
        S.append(I.caixa(x0, x1, d["y0"], d["y0"] + d["t"], 0, d["h"], item=13, nome="dente").movido((0, 0, 1.0 * e)))
    S.append(I.caixa(-p["b"] / 2, p["b"] / 2, p["y0"], p["y0"] + p["t"], p["z0"], p["z1"], item=14, nome="ponta").movido((0, 0.9 * e, -0.9 * e)))
    if com_parafusos:
        yn = C["y_nivel"]
        S.append(I.cilindro((0, yn, 0), "z", HX["e"] / 2, HX["m"], hexa=True, item=15, cor=I.CINZA_PAR, nome="porca nível").movido((0, 0, 1.6 * e)))
        S.append(I.cilindro((0, yn, HX["m"]), "z", HX["e"] / 2, HX["m_fina"], hexa=True, item=17, cor=I.CINZA_PAR, nome="contraporca").movido((0, 0, 2.3 * e)))
        hb = G - HX["k"]
        S.append(I.cilindro((0, yn, hb - C["L_nivel"]), "z", 8, C["L_nivel"], n=16, item=16, cor=I.CINZA_PAR, nome="nível").movido((0, 0, 3.2 * e)))
        S.append(I.cilindro((0, yn, hb), "z", HX["e"] / 2, HX["k"], hexa=True, item=16, cor=I.CINZA_PAR, nome="cabeça").movido((0, 0, 3.2 * e)))
        zf = C["z_frontal"]
        S.append(I.cilindro((0, p["y0"] - HX["m"], zf), "y", HX["e"] / 2, HX["m"], hexa=True, item=15, cor=I.CINZA_PAR, nome="porca frontal").movido((0, 0.9 * e, -0.9 * e)))
        yt = A_NOM + N["P"] - N["t_fundo"]
        S.append(I.cilindro((0, yt - C["L_frontal"], zf), "y", 8, C["L_frontal"], n=16, item=18, cor=I.CINZA_PAR, nome="prisioneiro").movido((0, 2.0 * e, -0.9 * e)))
    return S


def nc1_no_console(explode=0.0):
    """NC-1 nas coordenadas do console (montagem nominal)."""
    return [s.movido((DX, DY, DZ)) for s in nc1_solidos(explode)]


def placa_ponta(L=320.0, z0=-360.0, z1=260.0):
    """concreto da ponta da placa em volta do nicho (coordenadas do console), sem o vazio do nicho."""
    y0, y1 = DY, DY + 100
    xa, xb = DX, DX + L
    zn0, zn1 = DZ, DZ + N["H"]
    yp = DY + N["P"]
    cor = I.CONCRETO
    return [I.caixa(xa, xb, y0, y1, zn1, z1, item=None, cor=cor, nome="concreto acima"),
            I.caixa(xa, xb, y0, y1, z0, zn0, item=None, cor=cor, nome="concreto abaixo"),
            I.caixa(DX + N["B"], xb, y0, y1, zn0, zn1, item=None, cor=cor, nome="concreto ao lado"),
            I.caixa(xa, DX + N["B"], yp, y1, zn0, zn1, item=None, cor=cor, nome="concreto atrás")]


# ------------------------------------------------------------------ CE-1, PT-1, PT-2
def ce1_itens():
    return [(20, "CHAPA DE ESPERA", f"CH {TCE:g} × 330 × 380", "ASTM A36", 1, kg_ch(380, 330, TCE)),
            (21, "PINO COM CABEÇA (stud)", "Ø16 × 150, cabeça Ø32 × 10 — ISO 13918 SD", "S235J2 + C450", 4, kg_red(16, 140) + kg_red(32, 10))]


def ce1_solidos(explode=0.0):
    S = [I.caixa(-190, 190, -TCE, 0, -165, 165, item=20, nome="CE-1")]
    for x in (-120, 120):
        for z in (-140, 140):
            S.append(I.cilindro((x, -TCE - 140, z), "y", 8, 140, n=14, item=21, cor=I.CINZA_PAR).movido((0, -explode, 0)))
            S.append(I.cilindro((x, -TCE - 150, z), "y", 16, 10, n=18, item=21, cor=I.CINZA_PAR).movido((0, -explode, 0)))
    return S


def pt_itens():
    return [(30, "CARTOLA PT-1", "CH 6,3 × 80, dobrada (desenv. 280)", "ASTM A36", 1, kg_ch(80, 280, 6.3)),
            (31, "PARAFUSO PT-1/PT-2", "M16 × 40 ISO 4017 cl. 8.8", "aço cl. 8.8 galv.", 2, 0.097),
            (32, "ARRUELA LARGA", "M16 ISO 7093 (17 × 50 × 3)", "aço galv.", 2, 0.040),
            (33, "LUVA TSA M16 (Trejor)", "hef 70, embutida nas placas", "aço zincado", 2, 0.09),
            (34, "CHAPA PT-1R", "CH 6,3 × 80 × 220, plana (junta em frente à VB)", "ASTM A36", 1, kg_ch(80, 220, 6.3)),
            (40, "CANTONEIRA PT-2", "L 102 × 102 × 9,5 L = 150", "ASTM A36", 1, 14.6 * 0.150),
            (43, "BUCHA BR-1 / BR-2", "M16 hef 70 (placa) / hef 100 (pilar)", "aço zincado", 2, 0.10)]
