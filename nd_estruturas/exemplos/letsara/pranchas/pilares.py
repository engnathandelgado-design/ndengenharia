"""ND-LET-PIL-A01 (armado) e ND-LET-PIL-P01 (protendido) — pilares pré-moldados 40×60 laterais e de fachada (A0).
Rodar: python pilares.py armado | protendido. Mesma geometria, insertos e consolos; muda só a armadura longitudinal.

Convenções (prática de fábrica / desenho de peça pré-moldada tipo Tekla "cast unit drawing"):
- peça desenhada deitada como na fôrma, base à esquerda; vistas das faces A (consolo, para cima na fôrma), B (lado de 40)
  e C (fundo da fôrma, placas); cortes, detalhes, isométrico, planta-chave de locação, tabela de marcas, relação do aço;
- cotas de concreto em cm (NBR 7191 / NBR 9062), chaparia em mm; cotas ordenadas a partir da base do cálice (z = 0);
- marca = peças iguais (geometria + insertos + armadura); barras ≤ Ø20; cobrimento 30 mm (NBR 6118:2023 Tab. 7.2, CAA II).
"""
import json, math, subprocess, sys
from prancha_nd import Prancha, MASSA_ACO

OPC = sys.argv[1] if len(sys.argv) > 1 else "armado"
PROT = OPC == "protendido"
AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
LG = json.load(open(AQ + "ligacoes.json"))
f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")

# ------------------------------------------------------------------ geometria (modelo em mm; z = comprimento a partir da base do cálice)
B, H = 400, 600                 # 40 na direção y (ao longo da fachada lateral) × 60 na direção x (perpendicular à fachada)
L_CAL, Z_TOP = 1000, 10000      # embutimento no cálice; topo da platibanda (+10,000)
L_TOT = L_CAL + Z_TOP
I_CAI = 0.03
zf = lambda x: LG["Z0_TS"] * 1000 + I_CAI * x
sys.path.insert(0, AQ)
from geometria import Y_LIN, X_FACH, X_EIXO, Y_P13
Z_CONS = {"P1": round(zf(475) + 450 * math.cos(math.atan(I_CAI)) - 10), "P2": round(zf(X_EIXO["E"] * 1000 - 475) + 450 * math.cos(math.atan(I_CAI)) - 10)}
# RECUO DA CABEÇA (aprovado em 12/10/2026): acima do topo da TS-01 na face do pilar só os 300 mm do lado das placas (face C)
# sobem até +10,00 — cabeça 40×30. Eixo A: +8,40; eixo E: +9,55 (topo da TS-01 na face, arredondado a 5 cm).
Z_REC = {"P1": 8400, "P2": 9550}
H_CAB = 300
CONS = dict(proj=300, h=450, hp=250, larg=400)           # consolo CP-TS: balanço 300, altura 450 na face, 250 na ponta
PINO = dict(d=20, L=700, emb=300, x=175)                 # pino Ø20 CA-50: 300 no consolo + 400 no tubo TB-1 da viga; a 175 da face
Z_PLACA = [1250 * k - 100 for k in range(1, 9)]          # insertos das placas (fiadas de 1,25 m), a partir do piso
Z_PLACA_ABS = [z + L_CAL for z in Z_PLACA]
AL = [L_TOT - 3200, L_CAL + 2300]                        # alças (a partir da base): içamento na vertical e transporte
COB = 30                                                 # NBR 6118:2023 Tab. 7.2 — CAA II, pilar: 30 mm (sem a redução de 5 mm)
Z_VT = 7790 + 1000                                       # assento do consolo CP-VT: viga VT 25×60 (+7,50/+8,10) com dente 30×20 — faces B e D
VT = dict(larg=250, proj=250, h=300, hp=200)
zc = Z_CONS["P1"] + L_CAL                                # topo do consolo (a partir da base)
z_rec = Z_REC["P1"] + L_CAL                              # nível do recuo (a partir da base)
json.dump(dict(B=B, H=H, L_TOT=L_TOT, zc=zc, z_rec=z_rec, h_cab=H_CAB, cons=CONS, incl=I_CAI, pino_x=PINO["x"], z_placa_abs=Z_PLACA_ABS, al=AL),
          open("/home/claude/letsara/pranchas/pilar_geom.json", "w"))

# planta-chave (m) — eixos do R01 como no modelo BIM
MARCAS = [
    ("PL-01", "P1 L3–L8", 6, "CP-TS +7,914 (A); recuo +8,40", "8 IP-01 (C)"),
    ("PL-02", "P1 L2", 1, "CP-TS +7,914 (A); 2 CP-MEZ (A); recuo +8,40", "8 IP-01 (C)"),
    ("PL-03", "P1 L1 canto", 1, "CP-VB +7,460 (B); 2 CP-MEZ; recuo A e B", "8 IP-01 (C) + 8 (D)"),
    ("PL-04", "P1 L9 canto", 1, "CP-VB +7,460 (D); recuo A e D", "8 IP-01 (C) + 8 (B)"),
    ("PL-05", "P2 L3–L8", 6, f"CP-TS +{f(Z_CONS['P2']/1000,3)} (A); recuo +9,55", "8 IP-01 (C)"),
    ("PL-06", "P2 L2", 1, f"CP-TS +{f(Z_CONS['P2']/1000,3)} (A); 2 CP-MEZ; recuo +9,55", "8 IP-01 (C)"),
    ("PL-07", "P2 L1 canto", 1, "CP-VB +8,645 (D); 2 CP-MEZ; recuo A e D", "8 IP-01 (C) + 8 (B)"),
    ("PL-08", "P2 L9 canto", 1, "CP-VB +8,645 (B); recuo A e B", "8 IP-01 (C) + 8 (D)"),
    ("PF-01", "P3 (L1 e L9)", 2, "2 CP-VB +7,756 (B e D); L1: 2 CP-MEZ; recuo no topo da VB", "8 IP-01 (C)"),
    ("PF-02", "P4", 1, "2 CP-VB +8,053 (B e D); 2 CP-MEZ; recuo no topo da VB", "8 IP-01 (C)"),
    ("PF-04", "P14 (L9, C)", 1, "2 CP-VB +8,053; CP-I110 (V405); recuo no topo da VB", "8 IP-01 (C)"),
    ("PF-03", "P5 (L1 e L9)", 2, "2 CP-VB +8,349 (B e D); L1: 2 CP-MEZ; recuo no topo da VB", "8 IP-01 (C)"),
]
N_PIL = sum(m[2] for m in MARCAS)
def marca_de(nome):
    for mk, pos, *_ in MARCAS:
        for tok in pos.replace(" canto", "").split(" e "):
            if "–" in tok:                                   # P1 L3–L8
                p, faixa = tok.split(" ")
                a, b = faixa[1:].split("–")
                if nome.startswith(p + "-L") and int(a) <= int(nome.split("L")[1]) <= int(b.lstrip("L")):
                    return mk
            elif " " in tok:
                p, l = tok.split(" ")[:2]
                if nome == f"{p}-{l}" or nome == p:
                    return mk
            elif nome == tok:
                return mk
    return "?"

# ------------------------------------------------------------------ armadura (NBR 6118:2023 18.4)
# barras longitudinais: centro a COB + Øt + Ø/2 da face → 30 + 8 + 10 = 48 mm (152 do eixo no lado de 40; 252 no lado de 60)
XB, YB = B / 2 - COB - 8 - 10, H / 2 - COB - 8 - 10
if PROT:
    LONG = dict(pos="N1", n=8, d=20.0, desc="4 Ø20 por face de 60 (cantos comuns)",
                xy=[(sx * XB, sy * YB) for sx in (-1, 1) for sy in (-1, 1)] + [(sx * XB, sy * 84) for sx in (-1, 1) for sy in (-1, 1)])
    CORD = [(x, y) for y in (-250, 250) for x in (-100, -50, 0, 50, 100)]
    SIG_PI = 1400
else:
    LONG = dict(pos="N1", n=20, d=20.0, desc="5 Ø20 por face de 40 e 7 Ø20 por face de 60 (cantos comuns)",
                xy=[(x, -YB) for x in (-XB, -76, 0, 76, XB)] + [(x, YB) for x in (-XB, -76, 0, 76, XB)] +
                   [(-XB, y) for y in (-168, -84, 0, 84, 168)] + [(XB, y) for y in (-168, -84, 0, 84, 168)])
    CORD = []
# estribos: s ≤ min(200; b = 400; 12 Ø = 240) = 200 mm (18.4.3) → c/15 corrente; c/10 nos 1,5 m das pontas e no cálice
# grampos: barra a mais de 20 Øt = 160 mm de um canto de estribo precisa de estribo suplementar (18.4.3) → N3 nas linhas y = ±84
EST = dict(d=8.0, s_corr=150, s_dens=100, zona=1500, gancho=80)   # gancho 135° de 10 Øt = 80 mm (≥ 5 Øt e ≥ 50 mm, 9.4.6.1)
z_est = list(range(50, EST["zona"] + L_CAL, EST["s_dens"])) + list(range(EST["zona"] + L_CAL, L_TOT - EST["zona"], EST["s_corr"])) + \
        list(range(L_TOT - EST["zona"], L_TOT - 40, EST["s_dens"]))
z_est = sorted(set(z_est))
z_cab = [z for z in z_est if z > z_rec + 40]                                           # na cabeça 40×30: N8 (estribo menor)
z_est = [z for z in z_est if z <= z_rec + 40]
n_est = len(z_est)
n_cab = len(z_cab)
# barras longitudinais: as que estão na metade da face A (y > 0 na seção) e as do meio terminam no recuo (gancho 90° a 3 cm);
# só as 5 barras do lado das placas (face C) sobem até o topo; a cabeça ganha N7 (4 Ø16 junto à face recuada, ancoradas 60 cm
# abaixo do recuo) e estribos N8 Ø8 c/10 (34 × 24 externos)
SOBE = [xy for xy in LONG["xy"] if xy[1] <= -YB + 1]
PARA = [xy for xy in LONG["xy"] if xy not in SOBE]
N7 = dict(n=4, d=16.0, lb=600, y=-H / 2 + H_CAB - COB - 8 - 8, xs=(-XB, -50, 50, XB))
C_N8 = round((2 * (B - 2 * COB + H_CAB - 2 * COB) + 2 * EST["gancho"]) / 10)
EXT_B, EXT_H = B - 2 * COB, H - 2 * COB                                                # 340 × 540 externos
C_EST = round((2 * (EXT_B + EXT_H) + 2 * EST["gancho"]) / 10)                         # cm
C_GR = round((EXT_H + 2 * EST["gancho"]) / 10)                                        # grampo Ø8 no sentido de 60
Y_GR = (-84, 84)
VOL = (0.24 * z_rec + B * H_CAB / 1e6 * (L_TOT - z_rec)) / 1000
PESO = VOL * 25
assert max(abs(x) for x, _ in LONG["xy"]) + 10 + 8 + COB <= B / 2 + 0.01, "cobrimento do estribo < 30 mm no lado de 40"
assert max(abs(y) for _, y in LONG["xy"]) + 10 + 8 + COB <= H / 2 + 0.01, "cobrimento do estribo < 30 mm no lado de 60"

# ------------------------------------------------------------------ isométricos
subprocess.run([sys.executable, "/home/claude/letsara/pranchas/iso3d_pilar.py"], check=True, capture_output=True)

pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo=f"PILAR PRÉ-MOLDADO PL-01 (FAMÍLIA PL-01 A PF-03) 40×60 — {'PRÉ-TRACIONADO NA CABECEIRA' if PROT else 'CONCRETO ARMADO'} — FÔRMA, ARMAÇÃO, INSERTOS E LOCAÇÃO",
                        desenho=f"ND-LET-PIL-{'P' if PROT else 'A'}01", folha="01/01", fase="PARA APROVAÇÃO — OPÇÃO " + ("B (PROTENDIDO)" if PROT else "A (ARMADO)"),
                        marca="PL-01", qtd=6, peso=f(PESO, 1), volume=f(VOL, 2)))
pr.revisao("00", "12/10/2026", "EMISSÃO PARA COMPARAÇÃO DE CUSTO (OPÇÕES A E B)")
pr.revisao("01", "12/10/2026", "VISTAS DAS FACES A/B/C, ISOMÉTRICOS, PLANTA-CHAVE, COTAS EM CM, ESTRIBOS E COBRIMENTOS CONFORME NBR 6118")
pr.revisao("02", "12/10/2026", "PILAR DESENHADO EM PÉ (POSIÇÃO DE MONTAGEM); CHAPARIA HACHURADA; DETALHE DE PROTENSÃO (FORÇA NO MACACO)")
pr.revisao("03", "12/10/2026", "CONSOLOS CP-VT (DENTES DAS VIGAS DE TRAVAMENTO +6,25/+6,85) NAS FACES B E D; CORES DAS ARMADURAS")
pr.revisao("04", "12/10/2026", "GEOMETRIA DO R01; CABEÇA RECUADA 40×30 ACIMA DE +8,40 (APROVADO); VT EM +7,50/+8,10")
Q = pr.quadro                     # (25, 10, 1179, 831)
ESC = 20
XC = Q[2] - 190                   # coluna de tabelas à direita
Y0 = 92                           # papel: base do cálice (z = 0) das vistas em pé

# ------------------------------------------------------------------ identificação da peça (cabeçalho do desenho)
pr.ret(Q[0] + 4, Q[3] - 30, Q[0] + 560, Q[3] - 4, "CARIMBO")
pr.texto(Q[0] + 10, Q[3] - 24, "PL-01", "grande", "TITULO")
pr.texto(Q[0] + 48, Q[3] - 24, f"PILAR PRÉ-MOLDADO  40 × 60 cm (cabeça 40 × 30)   ·   L = {L_TOT/10:.0f} cm (cálice 100 + 1000)   ·   {'C50 / 10 cord. Ø12,7' if PROT else 'C40'}   ·   6 peças", "titulo", "TITULO")
pr.texto(Q[0] + 10, Q[3] - 14, f"POSIÇÃO: eixo A (P1), linhas 3 a 8   ·   PESO {f(PESO/10,2)} t   ·   VOLUME {f(VOL,2)} m³   ·   FACES: A = consolo (interna), B = lado de 40 (y+), C = placas (externa), D = lado de 40 (y−)   ·   desenhado em pé, como montado; demais marcas: tabela e planta-chave", "nota", "TEXTO")

# ------------------------------------------------------------------ PLANTA-CHAVE 1:750 (locação dos pilares e marcas) — canto superior esquerdo
kp = pr.vista("PLANTA-CHAVE", (Q[0] + 487, Q[3] - 172), 750, titulo="PLANTA-CHAVE — LOCAÇÃO DOS PILARES 40×60",
              subtitulo="PL-01 hachurado", unidade="cm")
Xm = lambda m: m * 1000
for y in Y_LIN:
    kp.linha((Xm(-2.5), Xm(y)), (Xm(42.0), Xm(y)), "EIXO")
for x in X_FACH:
    kp.linha((Xm(x), Xm(-2.5)), (Xm(x), Xm(85.5)), "EIXO")
for i, y in enumerate(Y_LIN, 1):
    kp.circulo((Xm(-2.5), Xm(y)), 1100, "VISTA"); kp.texto((Xm(-2.5), Xm(y)), str(i), "nota", "MIDDLE_CENTER")
for j, x in enumerate(X_FACH):
    kp.circulo((Xm(x), Xm(85.5)), 1100, "VISTA"); kp.texto((Xm(x), Xm(85.5)), "ABCDE"[j], "nota", "MIDDLE_CENTER")
def pil_kp(nome, x, y, bx, by, lado):
    mk = marca_de(nome)
    pts = [(Xm(x) - bx / 2, Xm(y) - by / 2), (Xm(x) + bx / 2, Xm(y) - by / 2), (Xm(x) + bx / 2, Xm(y) + by / 2), (Xm(x) - bx / 2, Xm(y) + by / 2)]
    kp.poli(pts, "CORTADO", fechada=True)
    if mk == "PL-01":
        kp.hachura(pts, "ANSI31", 0.3)
    if lado == 0:
        kp.texto((Xm(x), Xm(y) - 2000), f"{nome} {mk}", "min", "TOP_CENTER")
    elif lado == 2:
        kp.texto((Xm(x), Xm(y) + 2000), f"{nome} {mk}", "min", "BOTTOM_CENTER")
    else:
        kp.texto((Xm(x) + lado * 700, Xm(y) + 500), f"{nome} {mk}", "min", "BOTTOM_LEFT" if lado > 0 else "BOTTOM_RIGHT")
for i, y in enumerate(Y_LIN, 1):
    pil_kp(f"P1-L{i}", 0.0, y, 600, 400, 1)
    pil_kp(f"P2-L{i}", X_EIXO["E"], y, 600, 400, -1)
for j, x in enumerate(X_FACH[1:-1]):
    pil_kp(["P3", "P4", "P5"][j], x, 0.0, 400, 600, 0)
    pil_kp(["P3", "P14", "P5"][j], x, Y_LIN[-1], 400, 600, 2)
for nome, y, bx, by in (("P8A", Y_LIN[1], 400, 600), ("P11", Y_LIN[3], 400, 400), ("P13", Y_P13, 600, 600)):
    xc_ = Xm(X_EIXO["C"])
    pts = [(xc_ - bx / 2, Xm(y) - by / 2), (xc_ + bx / 2, Xm(y) - by / 2), (xc_ + bx / 2, Xm(y) + by / 2), (xc_ - bx / 2, Xm(y) + by / 2)]
    kp.poli(pts, "VISTA", fechada=True); kp.texto((xc_ + 700, Xm(y) + 500), nome, "min", "BOTTOM_LEFT")
for nome, x in (("P8", X_EIXO["B"]), ("P8B", X_EIXO["D"])):
    pts = [(Xm(x) - 200, Xm(Y_LIN[1]) - 300), (Xm(x) + 200, Xm(Y_LIN[1]) - 300), (Xm(x) + 200, Xm(Y_LIN[1]) + 300), (Xm(x) - 200, Xm(Y_LIN[1]) + 300)]
    kp.poli(pts, "VISTA", fechada=True); kp.texto((Xm(x), Xm(Y_LIN[1]) - 700), nome, "min", "TOP_CENTER")
kp.cota_h([Xm(x) for x in X_FACH], Xm(-2.5), -6)
kp.cota_v([Xm(y) for y in Y_LIN], Xm(42.0), 6)
kp.poli([(Xm(46.4), Xm(70)), (Xm(46.4), Xm(75)), (Xm(45.6), Xm(73.5)), (Xm(46.4), Xm(75)), (Xm(47.2), Xm(73.5))], "VISTA")
kp.texto((Xm(46.4), Xm(76.5)), "N (a confirmar)", "min", "BOTTOM_CENTER")

# ------------------------------------------------------------------ vistas de fôrma 1:20 em pé — cotas em cm
def chaves_lado(v, x_face, sg):
    """chaves de cisalhamento vistas de perfil numa face lateral (rebaixo 30, 40 de rampa, 200 de altura)."""
    for k in range(3):
        z0 = 150 + k * 300
        v.poli([(x_face, z0), (x_face + sg * 30, z0 + 40), (x_face + sg * 30, z0 + 160), (x_face, z0 + 200)], "VISTA")
def chaves_frente(v, larg):
    for k in range(3):
        z0 = 150 + k * 300
        v.ret(50, z0 + 40, larg - 100, 120, "OCULTA")
def nivel(v, x, z, txt, lado=1):
    v.poli([(x, z), (x + lado * 60, z + 60), (x + lado * 60, z - 60), (x, z)], "COTA")
    v.linha((x + lado * 60, z), (x + lado * 260, z), "COTA")
    v.texto((x + lado * 70, z + 10), txt, "min", "BOTTOM_LEFT" if lado > 0 else "BOTTOM_RIGHT", "COTA")
ORD = [0, L_CAL] + Z_PLACA_ABS + [zc, L_TOT]
ORD_R = [f"{z/10:g}".replace(".", ",") for z in ORD]

# FACE A (x+, consolo): largura visível 40 (y)
vA = pr.vista("FACE A", (Q[0] + 50, Y0), ESC, titulo="FACE A (CONSOLO)", subtitulo="pilar em pé", unidade="cm")
vA.ret(0, 0, B, L_TOT, "VISTA")
vA.linha((0, L_CAL), (B, L_CAL), "EIXO")
vA.linha((0, z_rec), (B, z_rec), "VISTA")                                                  # aresta do recuo (cabeça 30 cm atrás)
vA.chamada((B / 2, z_rec + 400), (12, 8), "face recuada 30 cm (cabeça 40×30)")
vA.ret(0, zc - CONS["h"], B, CONS["h"], "VISTA")                                          # consolo visto de frente
vA.linha((0, zc - CONS["hp"]), (B, zc - CONS["hp"]), "VISTA")                             # aresta ponta/chanfro
vA.ret(B / 2 - PINO["d"] / 2, zc - PINO["emb"], PINO["d"], PINO["emb"], "OCULTA")
vA.chapa(B / 2 - PINO["d"] / 2, zc, PINO["d"], PINO["L"] - PINO["emb"])                   # pino saliente
vA.chapa(B / 2 - 75, zc, 150, 10)                                                         # NEO-1 no assento
for z in AL:
    vA.linha((B / 2 - 50, z), (B / 2 + 50, z), "METALICA"); vA.circulo((B / 2 - 50, z), 6.35, "METALICA"); vA.circulo((B / 2 + 50, z), 6.35, "METALICA")
for z in Z_PLACA_ABS:
    vA.ret(B / 2 - 75, z - 75, 150, 150, "OCULTA")
chaves_frente(vA, B)
for x0, lado in ((B, 1), (0, -1)):
    vA.poli([(x0, Z_VT - VT["h"]), (x0 + lado * VT["proj"], Z_VT - VT["hp"]), (x0 + lado * VT["proj"], Z_VT), (x0, Z_VT)], "VISTA")
    vA.chapa(x0 + (25 if lado > 0 else -25 - 150), Z_VT, 150, 10)
vA.chamada((B + VT["proj"], Z_VT), (10, 10), "CP-VT (faces B e D) +7,790")
vA.cota_v([0, L_CAL, Z_VT, zc - CONS["h"], zc, z_rec, L_TOT], 0, -9)
vA.cota_v([L_CAL, AL[1], AL[0], L_TOT], B, 9, total=False)
vA.cota_h([0, B], 0, -8)
vA.chamada((B / 2, zc - 225), (12, -12), "CP-TS 40×30×45/25")
vA.chamada((B / 2 + 50, AL[0]), (10, -10), "AL-2 (2x)")
vA.chamada((B / 2, zc + 350), (12, 12), "PN-1 Ø20")
vA.chamada((B / 2 + 75, Z_PLACA_ABS[2]), (10, 10), "IP-01 (face C)")
vA.chamada((B / 2, 400), (12, 14), "chaves 4×20")
vA.texto((B / 2, L_TOT + 120), "FACE A", "sub", "BOTTOM_CENTER")
vA.marcador_corte((-80, 5000), (B + 80, 5000), "A", lado=1)
vA.marcador_corte((-80, zc - 125), (B + 80, zc - 125), "B", lado=1)

# FACE B (y+, lado de 40): perfil com o consolo em projeção para a direita (face A) e IP-01 para a esquerda (face C)
vB = pr.vista("FACE D", (Q[0] + 150, Y0), ESC, titulo="FACE D (LADO DE 40)", subtitulo="face B simétrica; consolo (A) à direita", unidade="cm")
vB.poli([(0, 0), (H, 0), (H, z_rec), (H_CAB, z_rec), (H_CAB, L_TOT), (0, L_TOT)], "VISTA", True)
vB.linha((0, L_CAL), (H, L_CAL), "EIXO")
vB.chamada((H_CAB + 150, z_rec), (10, 14), f"recuo +{f(Z_REC['P1']/1000,2)}: cabeça 40×30 até +10,00")
chaves_lado(vB, 0, -1); chaves_lado(vB, H, 1)
c0, c1 = zc - CONS["h"], zc
vB.poli([(H, c0), (H + CONS["proj"], c0 + CONS["h"] - CONS["hp"]), (H + CONS["proj"], c1 + CONS["proj"] * I_CAI), (H, c1)], "VISTA")
vB.ret(H + PINO["x"] - PINO["d"] / 2, zc - PINO["emb"], PINO["d"], PINO["emb"], "OCULTA")
vB.chapa(H + PINO["x"] - PINO["d"] / 2, zc, PINO["d"], PINO["L"] - PINO["emb"])
vB.chapa(H + 25, zc, 250, 10)                                                             # NEO-1
for z in Z_PLACA_ABS:
    vB.chapa(-9.5, z - 75, 9.5, 150)
for z in AL:
    vB.poli([(H, z - 50), (H + 110, z - 50), (H + 150, z), (H + 110, z + 50), (H, z + 50)], "METALICA")
vB.ret((H - VT["larg"]) / 2, Z_VT - VT["h"], VT["larg"], VT["h"], "VISTA"); vB.linha(((H - VT["larg"]) / 2, Z_VT - VT["hp"]), ((H + VT["larg"]) / 2, Z_VT - VT["hp"]), "VISTA")
vB.chapa(H / 2 - 10, Z_VT, 20, 300); vB.chapa(H / 2 - 75, Z_VT, 150, 10)
vB.chamada((H / 2, Z_VT - 150), (12, -12), "CP-VT 25×25×30/20 + PN-1 (dente da VT) +7,790")
vB.cota_ord_v(ORD, 0, -9, y0=0, rotulos=ORD_R)
vB.cota_v([0, L_CAL, c0, zc, z_rec, L_TOT], H + CONS["proj"], 9)
vB.cota_h([0, H, H + CONS["proj"]], 0, -8, total=False)
vB.cota_h([H, H + PINO["x"], H + CONS["proj"]], zc + 540, 8, total=False)
nivel(vB, H + 700, zc, f"+{f(Z_CONS['P1']/1000,3)} assento", 1)
nivel(vB, H_CAB, L_TOT, "+10,000", 1)
nivel(vB, H, z_rec, f"+{f(Z_REC['P1']/1000,3)} recuo", 1)
vB.cota_h([0, H_CAB, H], L_TOT, 8, total=False)
vB.chamada((H + 150, zc - 250), (12, -30), "consolo CP-TS, topo a 3 %")
vB.chamada((H + PINO["x"], zc + 300), (12, 10), "PN-1 Ø20 L=70")
vB.chamada((-9.5, Z_PLACA_ABS[4]), (-10, 10), "IP-01 (8x)")
vB.chamada((H + 150, AL[1]), (10, 10), "AL-2")
vB.texto((H / 2, L_TOT + 120), "FACE D", "sub", "BOTTOM_CENTER")
vB.texto((H / 2, L_TOT / 2 - 150), "CG", "min", "MIDDLE_CENTER"); vB.circulo((H / 2, L_TOT / 2 - 150), 40, "COTA")
vB.marcador_detalhe((H + 100, zc - 100), 400, 1, ang=-30, dist=8)
vB.marcador_detalhe((H / 2, L_CAL - 150), 380, 2, ang=-20, dist=8)

# FACE C (x−, placas)
vC = pr.vista("FACE C", (Q[0] + 275, Y0), ESC, titulo="FACE C (PLACAS)", subtitulo="face externa", unidade="cm")
vC.ret(0, 0, B, L_TOT, "VISTA")
vC.linha((0, L_CAL), (B, L_CAL), "EIXO")
for z in Z_PLACA_ABS:
    vC.chapa(B / 2 - 75, z - 75, 150, 150)
    for dy in (-40, 40):
        vC.circulo((B / 2 + dy, z), 6.25, "VISTA")
chaves_frente(vC, B)
vC.ret(0, zc - CONS["h"], B, CONS["h"], "OCULTA")
vC.linha((0, z_rec), (B, z_rec), "OCULTA")
for x0, lado in ((B, 1), (0, -1)):
    vC.poli([(x0, Z_VT - VT["h"]), (x0 + lado * VT["proj"], Z_VT - VT["hp"]), (x0 + lado * VT["proj"], Z_VT), (x0, Z_VT)], "VISTA")
vC.cota_ord_v([0, L_CAL] + Z_PLACA_ABS + [L_TOT], B, 9, y0=0, rotulos=[f"{z/10:g}" for z in [0, L_CAL] + Z_PLACA_ABS + [L_TOT]])
vC.cota_v([L_CAL, Z_PLACA_ABS[0], Z_PLACA_ABS[1]], 0, -9, total=False)
vC.cota_h([0, B / 2 - 75, B / 2 + 75, B], 0, -8)
vC.chamada((B / 2 + 75, Z_PLACA_ABS[5]), (-8, 12), "IP-01 150×150×9,5")
vC.texto((B / 2, L_TOT + 120), "FACE C", "sub", "BOTTOM_CENTER")

# ------------------------------------------------------------------ ELEVAÇÃO DE ARMAÇÃO 1:20 em pé (lado de 60 visível, como a face B)
va = pr.vista("ARMAÇÃO", (Q[0] + 375, Y0), ESC, titulo="ARMAÇÃO", subtitulo="igual nas 11 marcas", unidade="cm")
va.poli([(0, 0), (H, 0), (H, z_rec), (H_CAB, z_rec), (H_CAB, L_TOT), (0, L_TOT)], "VISTA", True)
for z in z_est:
    va.linha((COB, z), (H - COB, z), "ARM_TRANSV")
for z in z_cab:
    va.linha((COB, z), (H_CAB - COB, z), "ARM_TRANSV")
va.barra([(COB + 18, 40), (COB + 18, L_TOT - 40)], "N1", len(SOBE), 20, comp_cm=round((L_TOT - 80) / 10), ponto_rotulo=(COB + 18, 4000), desloc=(14, 12))
va.poli([(H - COB - 18, 40), (H - COB - 18, z_rec - 40), (H - COB - 18 - 150, z_rec - 40)], "ARMADURA")
va.chamada((H - COB - 18, 3000), (12, 10), f"N1A — {len(PARA)} Ø20 até o recuo (gancho 90°)")
xn7 = H_CAB - COB - 16
va.poli([(xn7, z_rec - N7["lb"]), (xn7, L_TOT - 40), (xn7 - 120, L_TOT - 40)], "ARMADURA")
va.chamada((xn7, z_rec - 300), (20, -40), f"N7 — 4 Ø16 (ancoragem {N7['lb']/10:.0f} cm)")
va.chamada((H_CAB - COB, z_cab[len(z_cab) // 2]), (10, 6), f"N8 Ø8 c/10 (cabeça)")
va.linha((H_CAB, z_rec), (H_CAB + 120, z_rec - 120), "ARMADURA")
va.chamada((H_CAB + 60, z_rec - 60), (20, 34), "N9 — 2 Ø12,5 a 45° no canto")
if PROT:
    for x in (H / 2 - 250, H / 2 + 250):
        va.linha((x, 0), (x, L_TOT), "ARM_PROT")
    va.chamada((H / 2 + 250, 6500), (12, 10), "C1 — 10 cord. Ø12,7")
va.chamada((H - COB, z_rec - 200), (12, 10), f"N2 Ø8 c/10 + 2 N3")
va.chamada((H - COB, 5000), (12, 10), "N2 Ø8 c/15 + 2 N3")
va.chamada((H - COB, 600), (12, 10), "N2 Ø8 c/10 + 2 N3")
va.cota_v([0, EST["zona"] + L_CAL, L_TOT - EST["zona"], z_rec, L_TOT], 0, -9)
va.chamada((H, zc), (10, 12), "N4/N5/N6 — DET. 1")
va.texto((H / 2, L_TOT + 120), "ARMAÇÃO", "sub", "BOTTOM_CENTER")
nivel(va, H, L_CAL, "±0,000 piso", 1)
nivel(va, H_CAB, L_TOT, "+10,000", 1)
pr.posicoes_desenho.update({"N1A", "N2", "N3", "N4", "N5", "N6", "N7", "N8", "N9"} | ({"C1"} if PROT else set()))

# ------------------------------------------------------------------ isométrico geral (pilar em pé)
pr.imagem(Q[0] + 455, Y0 - 10, Q[0] + 575, Y0 + 540, "/home/claude/letsara/pranchas/ISO-PIL-geral.png",
          titulo="ISOMÉTRICO", subtitulo="faces B e C; sem escala")

# ------------------------------------------------------------------ CORTES 1:10 (cm) — linha de cima da área de detalhes
XD = Q[0] + 625
YS = Q[3] - 150
def secao(nome, org, sub, consolo=False):
    v = pr.vista(nome, org, 10, titulo=nome, subtitulo=sub, unidade="cm")
    pts = [(-B / 2, -H / 2), (B / 2, -H / 2), (B / 2, H / 2), (-B / 2, H / 2)]
    if consolo:
        pts = [(-B / 2, -H / 2), (B / 2, -H / 2), (B / 2, H / 2 + CONS["proj"]), (-B / 2, H / 2 + CONS["proj"])]
    v.poli(pts, "CORTADO", fechada=True); v.hachura(pts, "AR-CONC", 0.03)
    e = [(-B / 2 + COB, -H / 2 + COB), (B / 2 - COB, -H / 2 + COB), (B / 2 - COB, H / 2 - COB), (-B / 2 + COB, H / 2 - COB)]
    v.poli(e, "ARM_TRANSV", fechada=True)
    v.poli([(-B / 2 + COB, H / 2 - COB), (-B / 2 + COB + 60, H / 2 - COB - 60)], "ARM_TRANSV")       # gancho 135°
    v.poli([(-B / 2 + COB + 60, H / 2 - COB), (-B / 2 + COB, H / 2 - COB - 60)], "ARM_TRANSV")
    for y in Y_GR:                                                                                   # N3 grampos
        v.linha((-B / 2 + COB, y), (B / 2 - COB, y), "ARM_TRANSV")
        v.poli([(-B / 2 + COB, y), (-B / 2 + COB + 50, y - 50)], "ARM_TRANSV"); v.poli([(B / 2 - COB, y), (B / 2 - COB - 50, y + 50)], "ARM_TRANSV")
    for x, y in LONG["xy"]:
        v.ponto_barra((x, y), 20)
    for x, y in CORD:
        v.ponto_barra((x, y), 12.7, "ARM_PROT_SECAO")
    v.cota_h([-B / 2, B / 2], -H / 2, -8)
    v.cota_v([-H / 2, H / 2], B / 2, 8)
    v.texto((0, H / 2 + (CONS["proj"] if consolo else 0) + 30), "FACE A", "min", "BOTTOM_CENTER")
    v.texto((0, -H / 2 - 130), "FACE C", "min", "TOP_CENTER")
    v.texto((B / 2 + 110, 0), "FACE B", "min", "MIDDLE_LEFT", rot=90); v.texto((-B / 2 - 30, 0), "FACE D", "min", "MIDDLE_RIGHT", rot=90)
    return v

va_ = secao("CORTE A-A", (XD + 40, YS), "corrente; cobr. 3,0 cm", False)
va_.chamada((-XB, -YB), (-10, -10), f"N1 — {len(SOBE)} Ø20 (sobem)")
va_.chamada((-XB, YB), (-10, 10), f"N1A — {len(PARA)} Ø20 (até o recuo)")
va_.chamada((-B / 2 + COB, 150), (-10, 0), "N2 Ø8")
va_.chamada((0, Y_GR[0]), (-10, -14), "N3 grampo Ø8 (2/estribo)")
va_.cota_v([-H / 2, -H / 2 + COB], -B / 2, -8, total=False)
vb_ = secao("CORTE B-B", (XD + 150, YS), "no consolo", True)
vb_.chapa(-10, H / 2 + CONS["proj"] - 300, 20, 300)
vb_.poli([(-170, H / 2 + CONS["proj"] - 55), (-170, -H / 2 + COB + 50), (170, -H / 2 + COB + 50), (170, H / 2 + CONS["proj"] - 55)], "ARMADURA")
for x in (-150, 0, 150):
    vb_.ponto_barra((x, H / 2 + CONS["proj"] - 55), 16)
vb_.chamada((-150, H / 2 + CONS["proj"] - 55), (-10, 10), "N4 — 3 Ø16")
vb_.chamada((10, H / 2 + CONS["proj"] - 150), (12, -8), "PN-1 Ø20")
vb_.cota_h([-150, 0, 150], H / 2 + CONS["proj"], 8, total=False)

# CORTE C-C — cabeça recuada 40×30
vcc = pr.vista("CORTE C-C", (XD + 95, YS - 125), 10, titulo="CORTE C-C", subtitulo="cabeça 40×30 (acima do recuo)", unidade="cm")
pts = [(-B / 2, -H / 2), (B / 2, -H / 2), (B / 2, -H / 2 + H_CAB), (-B / 2, -H / 2 + H_CAB)]
vcc.poli(pts, "CORTADO", True); vcc.hachura(pts, "AR-CONC", 0.03)
vcc.poli([(-B / 2, -H / 2 + H_CAB), (-B / 2, H / 2), (B / 2, H / 2), (B / 2, -H / 2 + H_CAB)], "OCULTA")
vcc.poli([(-B / 2 + COB, -H / 2 + COB), (B / 2 - COB, -H / 2 + COB), (B / 2 - COB, -H / 2 + H_CAB - COB), (-B / 2 + COB, -H / 2 + H_CAB - COB)], "ARM_TRANSV", True)
for x, y in SOBE:
    vcc.ponto_barra((x, y), 20)
for x in N7["xs"]:
    vcc.ponto_barra((x, N7["y"]), 16)
for x, y in CORD:
    if y < 0:
        vcc.ponto_barra((x, y), 12.7, "ARM_PROT_SECAO")
vcc.cota_h([-B / 2, B / 2], -H / 2, -8)
vcc.cota_v([-H / 2, -H / 2 + H_CAB, H / 2], B / 2, 8, total=False)
vcc.chamada((-XB, -YB), (-10, -10), f"N1 — {len(SOBE)} Ø20")
vcc.chamada((50, N7["y"]), (10, 12), "N7 — 4 Ø16")
vcc.chamada((B / 2 - COB, -H / 2 + 150), (12, -6), "N8 Ø8 c/10")
vcc.texto((0, -H / 2 - 130), "FACE C (placas)", "min", "TOP_CENTER")
vcc.texto((0, H / 2 + 30), "contorno do pilar abaixo do recuo", "min", "BOTTOM_CENTER")
vA.marcador_corte((-80, L_TOT - 300), (B + 80, L_TOT - 300), "C", lado=1)

# DETALHE 4 — protensão: posição das cordoalhas e força no macaco (só na opção B)
if PROT:
    F_MAC = SIG_PI * 98.7 / 1000                                    # kN por cordoalha (σpi × Ap)
    d4 = pr.vista("DETALHE 4", (XD + 280, YS), 10, titulo="DETALHE 4 — PROTENSÃO", subtitulo="cordoalhas e força no macaco", unidade="cm")
    pts = [(-B / 2, -H / 2), (B / 2, -H / 2), (B / 2, H / 2), (-B / 2, H / 2)]
    d4.poli(pts, "VISTA", fechada=True)
    d4.linha((-B / 2 - 100, 0), (B / 2 + 100, 0), "EIXO"); d4.linha((0, -H / 2 - 100), (0, H / 2 + 100), "EIXO")
    for k, (x, y) in enumerate(CORD, 1):
        d4.ponto_barra((x, y), 12.7, "ARM_PROT_SECAO")
        d4.texto((x, y + (18 if y > 0 else -18)), str(k), "min", "BOTTOM_CENTER" if y > 0 else "TOP_CENTER")
    d4.cota_h([-100, -50, 0, 50, 100], -H / 2, -8, total=False)
    d4.cota_v([-250, 0, 250], B / 2, 8, total=False)
    d4.chamada((-100, 250), (-8, 12), f"C1 — 10 cord. Ø12,7: {f(F_MAC,1)} kN no macaco (cada)")
    d4.texto((0, -H / 2 - 150), "pista: lado de 60 na vertical; cabeceira a 525 mm", "min", "TOP_CENTER")

# ------------------------------------------------------------------ DETALHE 1 — consolo CP-TS (1:10, cm) e DETALHE 2 — base no cálice (1:20)
YM = Q[3] - 455
d1 = pr.vista("DETALHE 1", (XD + 70, YM - 40), 10, titulo="DETALHE 1 — CONSOLO CP-TS", subtitulo="armadura e pino; topo a 3 % (sobe para a ponta); NBR 9062:2017 7.3", unidade="cm")
PW = H
zc0 = 1000
Z1, Z2 = 400, 1450
d1.poli([(-PW, Z1), (-PW, Z2), (0, Z2), (0, Z1)], "VISTA")
d1.interrupcao((-PW, Z1), (0, Z1)); d1.interrupcao((-PW, Z2), (0, Z2))
d1.poli([(0, zc0 - CONS["h"]), (CONS["proj"], zc0 - CONS["hp"]), (CONS["proj"], zc0 + CONS["proj"] * I_CAI), (0, zc0)], "VISTA")
d1.ret(PINO["x"] - 10, zc0 - 300 + 5, 20, 300, "OCULTA")
d1.chapa(PINO["x"] - 10, zc0 + 5, 20, 400)
d1.chapa(25, zc0 + 1, 250, 10)
d1.poli([(-PW + COB + 8, zc0 - 55 - 150), (-PW + COB + 8, zc0 - 55), (CONS["proj"] - 40, zc0 - 55)], "ARMADURA")
d1.poli([(CONS["proj"] - 40, zc0 - 55), (CONS["proj"] - 40, zc0 - 55 - 30)], "ARMADURA")
for dz in (-150, -250):
    d1.poli([(CONS["proj"] - 40, zc0 + dz), (-PW + COB, zc0 + dz)], "ARM_TRANSV")
for dx in (60, 140, 220):
    d1.poli([(dx, zc0 - 30 + dx * I_CAI), (dx, zc0 - CONS["h"] + (CONS["h"] - CONS["hp"]) * dx / CONS["proj"] + 30)], "ARM_TRANSV")
for z in range(500, Z2, 100):
    d1.linha((-PW + COB, z), (-COB, z), "ARM_TRANSV")
for x in (-PW + COB + 18, -COB - 18):
    d1.linha((x, Z1), (x, Z2), "ARMADURA")
d1.cota_v([zc0 - CONS["h"], zc0 - CONS["hp"], zc0, zc0 + CONS["proj"] * I_CAI], CONS["proj"], 10, total=False)
d1.cota_h([0, PINO["x"], CONS["proj"]], zc0 - CONS["h"], -8, total=False)
d1.cota_h([-PW, 0], Z1, -8)
d1.chamada((-PW + 300, zc0 - 55), (-4, 12), "N4 — 3 Ø16 U (85 + 15)")
d1.chamada((-200, zc0 - 250), (-6, -12), "N5 — 2 Ø10 (costura)")
d1.chamada((140, zc0 - 300), (14, -12), "N6 — 3 Ø8")
d1.chamada((PINO["x"], zc0 + 350), (10, 10), "PN-1 Ø20 CA-50 L=70")
d1.chamada((150, zc0 + 6), (16, 20), "NEO-1 30×15×1 (furo Ø30)")
d1.chamada((CONS["proj"], zc0 + 9), (12, 6), f"PL-01 +{f(Z_CONS['P1']/1000,3)} / PL-05 +{f(Z_CONS['P2']/1000,3)}")
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
d2.cota_v([0, L_CAL, 1500], H / 2 + 150, 10, total=False)
d2.cota_v([150, 350, 450, 650, 750, 950], -H / 2 - 30, -8, total=False)
d2.cota_h([-H / 2, H / 2], 0, -8)
d2.chamada((H / 2 + 30, 250), (14, 4), "chaves 4×20 (4 faces)")
d2.chamada((H / 2 - COB, 1350), (12, 8), "N2 Ø8 c/10")
d2.chamada((H / 2 + 150, -300), (8, -8), "cálice (fundações)")
d2.chamada((H / 2, L_CAL), (16, 18), "piso ±0,000; graute")
if PROT:
    d2.chamada((-H / 2 + COB + 18, 600), (-10, -8), "cordoalhas cortadas rente e seladas")

# ------------------------------------------------------------------ linha de baixo: isométrico do consolo e DETALHE 3 — IP-01 (1:5, mm)
pr.imagem(XD - 15, Y0 - 55, XD + 175, Y0 + 115, "/home/claude/letsara/pranchas/ISO-PIL-consolo.png",
          titulo="ISOMÉTRICO — CONSOLO CP-TS", subtitulo="sem escala")
d3 = pr.vista("DETALHE 3", (XD + 245, Y0 + 60), 5, titulo="DETALHE 3 — INSERTO IP-01", subtitulo="chapa A36 + 2 pinos c/ cabeça", unidade="mm")
d3.chapa(-75, -75, 150, 150, 0.6)
for dy in (-40, 40):
    d3.circulo((0, dy), 6.25, "VISTA")
d3.cota_h([-75, 75], -75, -8); d3.cota_v([-75, -40, 40, 75], 75, 8, total=False)
d3.chapa(130, -75, 9.5, 150, 0.6)                                                        # vista lateral (chapa cortada)
for dy in (-40, 40):
    d3.chapa(139.5, dy - 6.25, 100, 12.5, 0.6); d3.chapa(239.5, dy - 12.5, 8, 25, 0.6)
d3.cota_h([130, 139.5, 239.5, 247.5], -75, -8, total=False)
d3.chamada((0, 40), (-12, 14), "pino Ø12,5 L=100 c/ cabeça Ø25")
d3.chamada((200, 46), (8, 12), "chapa galvanizada a fogo")
d3.chamada((60, -75), (10, -14), "furos Ø18 na chapa das placas (CM-01)")

# ------------------------------------------------------------------ coluna direita
y = Q[3] - 6
y = pr.tabela(XC, y, "MARCAS — FAMÍLIA DE PILARES 40×60 (MESMA ARMAÇÃO; 2 AL-2 CADA)", ["MARCA", "POSIÇÃO", "QT", "CONSOLOS (nível do assento, face)", "INSERTOS DE PLACA"],
              [[m[0], m[1], m[2], m[3], m[4]] for m in MARCAS], [14, 24, 8, 86, 50], h_lin=6.0)
L_N1 = round((L_TOT - 80) / 10)
L_N1A = round((z_rec - 80) / 10)
L_N7 = round((L_TOT - 40 - (z_rec - N7["lb"])) / 10)
barras = [dict(pos="N1", diam=20.0, qtd=len(SOBE), comp=L_N1, trechos=[f"{L_N1}"]),
          dict(pos="N1A", diam=20.0, qtd=len(PARA), comp=L_N1A + 15, forma=[(0, 0), (0, 60), (6, 60)], trechos=[f"{L_N1A}", "15"]),
          dict(pos="N7", diam=16.0, qtd=4, comp=L_N7 + 12, forma=[(0, 0), (0, 60), (5, 60)], trechos=[f"{L_N7}", "12"]),
          dict(pos="N8", diam=8.0, qtd=n_cab, comp=C_N8, forma=[(0, 0), (34, 0), (34, 24), (0, 24), (0, 0), (2, 2)], trechos=["34", "24", "34", "24"]),
          dict(pos="N9", diam=12.5, qtd=2, comp=60, trechos=["60"]),
          dict(pos="N2", diam=8.0, qtd=n_est, comp=C_EST, forma=[(0, 0), (34, 0), (34, 54), (0, 54), (0, 0), (2, 2)], trechos=["34", "54", "34", "54"]),
          dict(pos="N3", diam=8.0, qtd=2 * n_est, comp=C_GR, forma=[(0, 6), (0, 0), (54, 0), (54, 6)], trechos=["8", "54", "8"]),
          dict(pos="N4", diam=16.0, qtd=3, comp=234, forma=[(0, 15), (0, 0), (85, 0), (85, 34), (0, 34), (0, 49)], trechos=["15", "85", "34", "85", "15"]),
          dict(pos="N5", diam=10.0, qtd=2, comp=round((2 * (340 + 700) + 160) / 10), forma=[(0, 0), (70, 0), (70, 34), (0, 34), (0, 0), (2, 2)], trechos=["70", "34", "70", "34"]),
          dict(pos="N6", diam=8.0, qtd=3, comp=round((2 * (340 + 400) + 160) / 10), forma=[(0, 0), (34, 0), (34, 40), (0, 40), (0, 0), (2, 2)], trechos=["34", "40", "34", "40"])]
ta = pr.tabela_croqui(XC, y - 4, barras, h_lin=9.0)
y = ta["y_base"]
if PROT:
    tc = pr.tabela_cordoalhas(XC, y - 4, [dict(pos="C1", diam=12.7, qtd=10, y=250, forca=SIG_PI * 98.7 / 1000, isol=0)], 60)
    y = tc["y_base"]
ins = [["PN-1", "Pino Ø20 CA-50 L=700 (300 no consolo), a 175 mm da face", 3, "CP-TS (face A) e 2 CP-VT (faces B e D)"],
       ["CP-VT", "Consolo 25×25×30/20 p/ dente da VT 25×60 (+7,790)", 2, "faces B e D (canto: 1)"],
       ["IP-01", "Chapa A36 150×150×9,5 + 2 pinos Ø12,5 c/ cabeça (p/ CM-01)", 8, "face C, c/1250 a partir do piso"],
       ["AL-2", "Alça laço cordoalha Ø12,7 (2 pernas 700), carga 40 kN", 2, "face A: 3200 do topo; 2300 da base"],
       ["NEO-1", "Neoprene 300×150×10 c/ furo Ø30 (montagem)", 1, "sobre o consolo"]]
y = pr.tabela(XC, y - 4, "INSERTOS POR PILAR (PL-01) — dimensões em mm", ["MARCA", "DESCRIÇÃO", "QT", "POSIÇÃO"], ins, [14, 100, 10, 58])
kg = ta["total_kg"]
qd = [["MARCA", "PL-01", "SEÇÃO", "40 × 60 (cabeça 40 × 30)"],
      ["COMPRIMENTO", f"{L_TOT/10:.0f} cm", "CONCRETO", "C50 / fckj 28 MPa" if PROT else "C40"],
      ["VOLUME", f"{f(VOL, 2)} m³", "PESO", f"{f(PESO/10, 2)} t"],
      ["AÇO CA-50", f"{f(kg, 0)} kg", "TAXA", f"{f(LONG['n'] * 3.14 / 2400 * 100, 2)} %"],
      ["PROTENSÃO", "10 cord. Ø12,7 — 138,2 kN/cord. (1382 kN)" if PROT else "—", "CG", f"{L_TOT / 2 / 1000:.2f} m da base".replace(".", ",")],
      ["QUANTIDADE", "6 (família: 29)", "COBRIMENTO", "3,0 cm (CAA II)"]]
y = pr.tabela(XC, y - 4, "QUADRO DA PEÇA", ["ITEM", "VALOR", "ITEM", "VALOR"], qd, [30, 60, 30, 62])
mem = [["ELU, vento lado 60 (λu)", "1,22" if PROT else "1,03"], ["ELU, vento lado 40 (λu)", "1,38" if PROT else "1,08"],
       ["Fachada, vento lado 40 (λu)", "1,30" if PROT else "1,01"], ["Armadura mínima (0,4 %)", f"{f(LONG['n'] * 3.14, 1)} ≥ 9,6 cm²"],
       ["Estribos (18.4.3)", "s = 15 ≤ min(20; 40; 12Ø = 24) cm"], ["Grampos (18.4.3)", "barras a > 20Øt = 16 cm do canto → N3"],
       ["Fissuração (freq.)", "σ = −2,7 MPa (comprimido)" if PROT else "σ = 1,45 ≤ 2,46 MPa (estádio I)"],
       ["Içamento (2 pontos)", "σ ≤ 1,7 MPa com ×1,3 — sem fissura"]]
y = pr.tabela(XC, y - 4, "MEMÓRIA RESUMIDA (método geral, NBR 6118:2023)", ["VERIFICAÇÃO", "RESULTADO"], mem, [70, 112])
notas = [("Concreto C50; cordoalhas CP-190 RB Ø12,7 na grade da cabeceira (passo 50 mm), 5 por face a 25 cm do eixo: cabeceira regulada em 525 mm "
          "(pilar deitado com o lado de 60 na vertical). σpi = 1400 MPa; liberar com fckj ≥ 28 MPa; cortar rente e selar." if PROT else
          "Concreto C40. Barras longitudinais retas de ponta a ponta (sem emenda); nenhuma bitola acima de Ø20."),
         "Cobrimento nominal 3,0 cm aos estribos (NBR 6118:2023 Tab. 7.2, CAA II); espaçadores plásticos a cada 100 cm nas 4 faces.",
         f"Estribos N2 Ø8 fechados com ganchos de 135° (8 cm), c/15 no trecho corrente e c/10 nos 150 cm junto ao topo e no cálice; "
         "2 grampos N3 Ø8 por estribo nas linhas a 8,4 cm do eixo (NBR 6118:2023 18.4.3).",
         "Consolos CP-TS (topo a 3 % subindo para a ponta), CP-VB e CP-MEZ com a mesma armadura N4/N5/N6 (NBR 9062:2017 7.3); posição e face por marca na tabela. Consolos CP-VT (2 Ø12,5 tirante + 2 estribos Ø8) nas faces B e D em +7,790 para os dentes das vigas de travamento VT 25×60 (+7,50/+8,10, ND-LET-VT01).",
         "Pino PN-1 Ø20 CA-50 (resiste 82 kN ≥ Hd 40 kN): concretado no consolo; tubo TB-1 Ø50×3,0 da viga (furo 44), grauteado numa ponta só de cada viga.",
         f"CABEÇA RECUADA: acima de +{f(Z_REC['P1']/1000,2)} (PL-01 a PL-04; +{f(Z_REC['P2']/1000,2)} em PL-05 a PL-08; fachada: topo da VB) o pilar segue só com os 30 cm do lado das placas (40×30) até +10,00. N1A param no recuo com gancho; N7 (4 Ø16) ancoram 60 cm no corpo; N8 Ø8 c/10 na cabeça; 2 N9 Ø12,5 a 45° no canto reentrante. Fôrma: tampa de 30 cm na face A acima do recuo." + (" Cordoalhas da face A cortadas rente no degrau e seladas." if PROT else ""),
         "Faces: A = consolo (interna), B e D = lados de 40, C = placas (externa). Pilar concretado deitado com a face A para cima e a face C no fundo da fôrma.",
         "Insertos IP-01 na face C a cada fiada de placa (125 cm a partir do piso); chaves de cisalhamento nas 4 faces do trecho embutido (100 cm).",
         "Içar na horizontal pelas 2 alças AL-2 e levantar à vertical pela alça superior com a base apoiada; estocar sobre 2 calços nas alças.",
         "Marca = geometria + insertos + armadura iguais; qualquer consolo a mais é marca nova. Cotas de concreto em cm, chaparia em mm, níveis em m. Não medir no desenho.",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
y = pr.legenda_armadura(XC, y - 4, PROT)
pr.notas(XC, y - 4, notas, 182)
pr.posicoes_desenho.add("N1")
avisos = pr.salvar(f"/home/claude/letsara/pranchas/ND-LET-PIL-{'P' if PROT else 'A'}01")
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
for a in avisos:
    print(a)
