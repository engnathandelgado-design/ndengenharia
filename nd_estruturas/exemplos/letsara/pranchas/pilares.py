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
Z_CONS = {"P1": round(zf(475) + 450 * math.cos(math.atan(I_CAI)) - 10), "P2": round(zf(39625) + 450 * math.cos(math.atan(I_CAI)) - 10)}
CONS = dict(proj=300, h=450, hp=250, larg=400)           # consolo CP-TS: balanço 300, altura 450 na face, 250 na ponta
PINO = dict(d=20, L=700, emb=300, x=175)                 # pino Ø20 CA-50: 300 no consolo + 400 no tubo TB-1 da viga; a 175 da face
Z_PLACA = [1250 * k - 100 for k in range(1, 9)]          # insertos das placas (fiadas de 1,25 m), a partir do piso
Z_PLACA_ABS = [z + L_CAL for z in Z_PLACA]
AL = [L_TOT - 3200, L_CAL + 2300]                        # alças (a partir da base): içamento na vertical e transporte
COB = 30                                                 # NBR 6118:2023 Tab. 7.2 — CAA II, pilar: 30 mm (sem a redução de 5 mm)
zc = Z_CONS["P1"] + L_CAL                                # topo do consolo (a partir da base)
json.dump(dict(B=B, H=H, L_TOT=L_TOT, zc=zc, cons=CONS, incl=I_CAI, pino_x=PINO["x"], z_placa_abs=Z_PLACA_ABS, al=AL),
          open("/home/claude/letsara/pranchas/pilar_geom.json", "w"))

# planta-chave (m) — eixos do R01 como no modelo BIM
Y_LIN = [0.0, 10.05, 19.705, 29.36, 38.865, 48.445, 58.025, 67.605, 76.81]
X_FACH = [0.0, 9.87, 20.05, 29.63, 40.10]
MARCAS = [
    ("PL-01", "P1 L3–L8", 6, "CP-TS +7,914 (A)", "8 IP-01 (C)"),
    ("PL-02", "P1 L2", 1, "CP-TS +7,914 (A); 2 CP-MEZ (A)", "8 IP-01 (C)"),
    ("PL-03", "P1 L1 canto", 1, "CP-VB +7,460 (B); 2 CP-MEZ", "8 IP-01 (C) + 8 (D)"),
    ("PL-04", "P1 L9 canto", 1, "CP-VB +7,460 (D)", "8 IP-01 (C) + 8 (B)"),
    ("PL-05", "P2 L3–L8", 6, "CP-TS +9,089 (A)", "8 IP-01 (C)"),
    ("PL-06", "P2 L2", 1, "CP-TS +9,089 (A); 2 CP-MEZ", "8 IP-01 (C)"),
    ("PL-07", "P2 L1 canto", 1, "CP-VB +8,650 (D); 2 CP-MEZ", "8 IP-01 (C) + 8 (B)"),
    ("PL-08", "P2 L9 canto", 1, "CP-VB +8,650 (B)", "8 IP-01 (C) + 8 (D)"),
    ("PF-01", "P3 e P14", 2, "2 CP-VB +7,750 (B e D); P3: 2 CP-MEZ", "8 IP-01 (C)"),
    ("PF-02", "P4 e P15", 2, "2 CP-VB +8,060 (B e D); P4: 2 CP-MEZ", "8 IP-01 (C)"),
    ("PF-03", "P5 e P16", 2, "2 CP-VB +8,350 (B e D); P5: 2 CP-MEZ", "8 IP-01 (C)"),
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
                p, l = tok.split(" ")
                if nome == f"{p}-{l}":
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
n_est = len(z_est)
EXT_B, EXT_H = B - 2 * COB, H - 2 * COB                                                # 340 × 540 externos
C_EST = round((2 * (EXT_B + EXT_H) + 2 * EST["gancho"]) / 10)                         # cm
C_GR = round((EXT_H + 2 * EST["gancho"]) / 10)                                        # grampo Ø8 no sentido de 60
Y_GR = (-84, 84)
PESO = 0.24 * L_TOT / 1000 * 25
assert max(abs(x) for x, _ in LONG["xy"]) + 10 + 8 + COB <= B / 2 + 0.01, "cobrimento do estribo < 30 mm no lado de 40"
assert max(abs(y) for _, y in LONG["xy"]) + 10 + 8 + COB <= H / 2 + 0.01, "cobrimento do estribo < 30 mm no lado de 60"

# ------------------------------------------------------------------ isométricos
subprocess.run([sys.executable, "/home/claude/letsara/pranchas/iso3d_pilar.py"], check=True, capture_output=True)

pr = Prancha("A0", dict(cliente="MARQUE ENGENHARIA", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo=f"PILAR PRÉ-MOLDADO PL-01 (FAMÍLIA PL-01 A PF-03) 40×60 — {'PRÉ-TRACIONADO NA CABECEIRA' if PROT else 'CONCRETO ARMADO'} — FÔRMA, ARMAÇÃO, INSERTOS E LOCAÇÃO",
                        desenho=f"ND-LET-PIL-{'P' if PROT else 'A'}01", folha="01/01", fase="PARA APROVAÇÃO — OPÇÃO " + ("B (PROTENDIDO)" if PROT else "A (ARMADO)"),
                        marca="PL-01", qtd=6, peso=f(PESO, 1), volume=f(0.24 * L_TOT / 1000, 2)))
pr.revisao("00", "12/10/2026", "EMISSÃO PARA COMPARAÇÃO DE CUSTO (OPÇÕES A E B)")
pr.revisao("01", "12/10/2026", "VISTAS DAS FACES A/B/C, ISOMÉTRICOS, PLANTA-CHAVE, COTAS EM CM, ESTRIBOS E COBRIMENTOS CONFORME NBR 6118")
Q = pr.quadro                     # (25, 10, 1179, 831)
ESC = 20
X0 = Q[0] + 30
XC = Q[2] - 190                   # coluna de tabelas à direita

# ------------------------------------------------------------------ identificação da peça (cabeçalho do desenho)
pr.ret(Q[0] + 4, Q[3] - 30, Q[0] + 420, Q[3] - 4, "CARIMBO")
pr.texto(Q[0] + 10, Q[3] - 24, "PL-01", "grande", "TITULO")
pr.texto(Q[0] + 48, Q[3] - 24, f"PILAR PRÉ-MOLDADO  40 × 60 cm   ·   L = {L_TOT/10:.0f} cm (cálice 100 + 1000)   ·   {'C50 / 10 cord. Ø12,7' if PROT else 'C40'}   ·   6 peças", "titulo", "TITULO")
pr.texto(Q[0] + 10, Q[3] - 14, f"POSIÇÃO: eixo A (P1), linhas 3 a 8   ·   PESO {f(PESO/10,2)} t   ·   VOLUME {f(0.24*L_TOT/1000,2)} m³   ·   FACES: A = consolo (interna), B = lado de 40 (y+), C = placas (externa), D = lado de 40 (y−)   ·   demais marcas da família: ver tabela de marcas e planta-chave", "nota", "TEXTO")

# ------------------------------------------------------------------ PLANTA-CHAVE 1:500 (locação dos pilares e marcas)
kp = pr.vista("PLANTA-CHAVE", (X0 + 740, Q[3] - 192), 500, titulo="PLANTA-CHAVE — LOCAÇÃO DOS PILARES 40×60",
              subtitulo="marcas PL/PF; pilar desenhado nesta prancha hachurado; centrais 50×50 e mezanino em prancha própria", unidade="cm")
Xm = lambda m: m * 1000
for y in Y_LIN:
    kp.linha((Xm(-2.5), Xm(y)), (Xm(42.6), Xm(y)), "EIXO")
for x in X_FACH:
    kp.linha((Xm(x), Xm(-2.5)), (Xm(x), Xm(80.8)), "EIXO")
for i, y in enumerate(Y_LIN, 1):
    kp.circulo((Xm(-2.5), Xm(y)), 900, "VISTA"); kp.texto((Xm(-2.5), Xm(y)), str(i), "nota", "MIDDLE_CENTER")
for j, x in enumerate(X_FACH):
    kp.circulo((Xm(x), Xm(80.8)), 900, "VISTA"); kp.texto((Xm(x), Xm(80.8)), "ABCDE"[j], "nota", "MIDDLE_CENTER")
def pil_kp(nome, x, y, bx, by, lado):
    mk = marca_de(nome)
    pts = [(Xm(x) - bx / 2, Xm(y) - by / 2), (Xm(x) + bx / 2, Xm(y) - by / 2), (Xm(x) + bx / 2, Xm(y) + by / 2), (Xm(x) - bx / 2, Xm(y) + by / 2)]
    kp.poli(pts, "CORTADO", fechada=True)
    if mk == "PL-01":
        kp.hachura(pts, "ANSI31", 0.4)
    if lado == 0:
        kp.texto((Xm(x), Xm(y) - 700), f"{nome} {mk}", "min", "TOP_CENTER")
    elif lado == 2:
        kp.texto((Xm(x), Xm(y) + 700), f"{nome} {mk}", "min", "BOTTOM_CENTER")
    else:
        kp.texto((Xm(x) + lado * 500, Xm(y) + 350), f"{nome} {mk}", "min", "BOTTOM_LEFT" if lado > 0 else "BOTTOM_RIGHT")
for i, y in enumerate(Y_LIN, 1):
    pil_kp(f"P1-L{i}", 0.0, y, 600, 400, 1)
    pil_kp(f"P2-L{i}", 40.10, y, 600, 400, -1)
for j, x in enumerate(X_FACH[1:-1]):
    pil_kp(["P3", "P4", "P5"][j], x, 0.0, 400, 600, 0)
    pil_kp(["P14", "P15", "P16"][j], x, 76.81, 400, 600, 2)
for nome, y in (("P8A", Y_LIN[1]), ("P11", Y_LIN[3]), ("P13", Y_LIN[5] + 4.6)):
    pts = [(Xm(20.05) - 250, Xm(y) - 250), (Xm(20.05) + 250, Xm(y) - 250), (Xm(20.05) + 250, Xm(y) + 250), (Xm(20.05) - 250, Xm(y) + 250)]
    kp.poli(pts, "VISTA", fechada=True); kp.texto((Xm(20.05) + 500, Xm(y)), f"{nome} 50×50", "min", "MIDDLE_LEFT")
for nome, x in (("P8", 9.87), ("P8B", 29.63)):
    pts = [(Xm(x) - 300, Xm(10.05) - 200), (Xm(x) + 300, Xm(10.05) - 200), (Xm(x) + 300, Xm(10.05) + 200), (Xm(x) - 300, Xm(10.05) + 200)]
    kp.poli(pts, "VISTA", fechada=True); kp.texto((Xm(x) + 500, Xm(10.05)), f"{nome} mez.", "min", "MIDDLE_LEFT")
kp.cota_h([Xm(x) for x in X_FACH], Xm(-2.5), -8)
kp.cota_v([Xm(y) for y in Y_LIN], Xm(42.6), 8)
kp.poli([(Xm(43.5), Xm(70)), (Xm(43.5), Xm(74)), (Xm(43.0), Xm(73)), (Xm(43.5), Xm(74)), (Xm(44.0), Xm(73))], "VISTA")
kp.texto((Xm(43.5), Xm(75)), "N (a confirmar)", "min", "BOTTOM_CENTER")
kp.texto((Xm(0), Xm(-6.5)), "eixo A: FACE A do pilar voltada para o interior (consolo CP-TS); FACE C para fora (placas)", "min", "MIDDLE_LEFT")

# ------------------------------------------------------------------ vistas de fôrma 1:25 (pilar deitado, base à esquerda) — cotas em cm
def chaves_h(v, y_face, sg):
    for k in range(3):
        z0 = 150 + k * 300
        v.poli([(z0, y_face), (z0 + 40, y_face + sg * 30), (z0 + 160, y_face + sg * 30), (z0 + 200, y_face)], "VISTA")

# FACE A (x+, consolo para cima na fôrma): o observador olha a face A; largura visível = 40 (y)
vA = pr.vista("FACE A", (X0, Q[3] - 175), ESC, titulo="VISTA DE FÔRMA — FACE A (CONSOLO)", subtitulo="pilar deitado, face A para cima na fôrma; base do cálice à esquerda", unidade="cm")
vA.ret(0, 0, L_TOT, B, "VISTA")
vA.linha((L_CAL, 0), (L_CAL, B), "EIXO")
vA.ret(zc - CONS["h"], 0, CONS["h"], B, "VISTA")                                      # consolo visto de frente (40 de largura)
vA.linha((zc - CONS["hp"], 0), (zc - CONS["hp"], B), "VISTA")                                 # aresta ponta/chanfro
vA.ret(zc - PINO["emb"], B / 2 - PINO["d"] / 2, PINO["emb"], PINO["d"], "OCULTA")             # pino: parte embutida (oculta)
vA.ret(zc, B / 2 - PINO["d"] / 2, PINO["L"] - PINO["emb"], PINO["d"], "METALICA")             # pino: parte saliente
vA.ret(zc, B / 2 - 75, 10, 150, "METALICA")                                                   # NEO-1 sobre o assento
for z in AL:
    vA.linha((z, B / 2 - 50), (z, B / 2 + 50), "METALICA"); vA.circulo((z, B / 2 - 50), 6.35, "METALICA"); vA.circulo((z, B / 2 + 50), 6.35, "METALICA")
for z in Z_PLACA_ABS:                                                                  # IP-01 na face oposta (oculto)
    vA.ret(z - 75, B / 2 - 75, 150, 150, "OCULTA")
for k in range(3):
    z0 = 150 + k * 300
    vA.ret(z0 + 40, 50, 120, B - 100, "OCULTA")                                        # chave da face A (rebaixo visto de frente)
vA.cota_h([0, L_CAL, zc - CONS["h"], zc, L_TOT], 0, -10)
vA.cota_h([L_CAL, AL[1], AL[0], L_TOT], B, 10, total=False)
vA.cota_v([0, B], L_TOT, 8)
vA.chamada((zc - 225, B), (6, 14), "consolo CP-TS 40 × 30 × 45/25 — assento em +7,914 (PL-01) — ver DETALHE 1")
vA.chamada((AL[0], B / 2 + 60), (10, 12), "AL-2 alça de içamento (2x) — ver tabela de insertos")
vA.chamada((zc + 300, B / 2 + 10), (14, -14), "PN-1 pino Ø20 (40 saliente)")
vA.chamada((Z_PLACA_ABS[1], B / 2 + 75), (8, -16), "IP-01 na face C (oculto)")
vA.chamada((300, B - 50), (8, 10), "chaves de cisalhamento 4×20 (4 faces)")
vA.texto((L_TOT + 420, B / 2), "FACE A", "sub", "MIDDLE_LEFT")
vA.marcador_corte((5000, -80), (5000, B + 80), "A", lado=1)
vA.marcador_corte((zc - PINO["x"], -80), (zc - PINO["x"], B + 80), "B", lado=1)

# FACE B (y+, lado de 40): perfil com o consolo em projeção para cima (face A) e IP-01 para baixo (face C)
vB = pr.vista("FACE B", (X0, Q[3] - 262), ESC, titulo="VISTA DE FÔRMA — FACE B (LADO DE 40)", subtitulo="face D simétrica; consolo para cima (face A), insertos IP-01 para baixo (face C)", unidade="cm")
vB.ret(0, 0, L_TOT, H, "VISTA")
vB.linha((L_CAL, 0), (L_CAL, H), "EIXO")
chaves_h(vB, 0, -1); chaves_h(vB, H, 1)
c0, c1 = zc - CONS["h"], zc
vB.poli([(c0, H), (c0 + CONS["h"] - CONS["hp"], H + CONS["proj"]), (c1 + CONS["proj"] * I_CAI, H + CONS["proj"]), (c1, H)], "VISTA")
vB.ret(zc - PINO["emb"], H + PINO["x"] - PINO["d"] / 2, PINO["emb"], PINO["d"], "OCULTA")
vB.ret(zc, H + PINO["x"] - PINO["d"] / 2, PINO["L"] - PINO["emb"], PINO["d"], "METALICA")
vB.ret(zc, H + 25, 10, 250, "METALICA")                                                       # NEO-1 no assento (face z+ do consolo)
for z in Z_PLACA_ABS:
    vB.ret(z - 75, -9.5, 150, 9.5, "METALICA")
for z in AL:
    vB.poli([(z - 50, H), (z - 50, H + 110), (z, H + 150), (z + 50, H + 110), (z + 50, H)], "METALICA")
vB.cota_h([0, L_CAL, c0, zc, L_TOT], 0, -10)
vB.cota_ord([L_CAL] + Z_PLACA_ABS + [L_TOT], -9.5, -32, x0=0, rotulos=[f"{L_CAL/10:.0f}"] + [f"{z/10:.0f}" for z in Z_PLACA_ABS] + [f"{L_TOT/10:.0f}"])
vB.cota_v([0, H, H + CONS["proj"]], L_TOT, 8, total=False)
vB.cota_h([c0, c0 + CONS["h"] - CONS["hp"], zc], H + CONS["proj"], 8, total=False)
vB.chamada((zc - 150, H + CONS["proj"]), (8, 14), "consolo CP-TS: topo a 3 % subindo para a ponta; NEO-1 30×15×1")
vB.chamada((zc + 350, H + PINO["x"]), (14, -12), "PN-1 pino Ø20 CA-50 L=70 (30 embutido, 40 saliente)")
vB.chamada((Z_PLACA_ABS[2], -9.5), (8, -54), "IP-01 chapa 150×150×9,5 mm + 2 pinos Ø12,5 (8x, c/125 a partir do piso)")
vB.chamada((AL[1], H + 150), (8, 12), "AL-2 (2x)")
vB.chamada((L_TOT - 300, H), (6, 14), "topo da platibanda +10,000")
vB.chamada((L_CAL, H), (-8, 16), "piso acabado ±0,000 (fim do cálice)")
vB.texto((L_TOT + 420, H / 2), "FACE B", "sub", "MIDDLE_LEFT")
vB.texto((L_TOT / 2, H / 2), "CG", "min", "MIDDLE_CENTER"); vB.circulo((L_TOT / 2, H / 2), 40, "COTA")
vB.marcador_detalhe((zc - 100, H + 120), 420, 1, ang=30, dist=8)
vB.marcador_detalhe((L_CAL + 150, H / 2), 380, 2, ang=60, dist=8)

# FACE C (x−, placas — fundo da fôrma)
vC = pr.vista("FACE C", (X0, Q[3] - 342), ESC, titulo="VISTA DE FÔRMA — FACE C (EXTERNA, PLACAS)", subtitulo="fundo da fôrma; insertos IP-01 centrados na largura, a cada fiada de placa (125 cm)", unidade="cm")
vC.ret(0, 0, L_TOT, B, "VISTA")
vC.linha((L_CAL, 0), (L_CAL, B), "EIXO")
for z in Z_PLACA_ABS:
    vC.ret(z - 75, B / 2 - 75, 150, 150, "METALICA")
    for dy in (-40, 40):
        vC.circulo((z, B / 2 + dy), 6.25, "METALICA")
for k in range(3):
    z0 = 150 + k * 300
    vC.ret(z0 + 40, 50, 120, B - 100, "OCULTA")
vC.ret(zc - CONS["h"], 0, CONS["h"], B, "OCULTA")                                     # consolo na face oposta
vC.cota_ord([L_CAL] + Z_PLACA_ABS + [L_TOT], 0, -14, x0=0, rotulos=[f"{L_CAL/10:.0f}"] + [f"{z/10:.0f}" for z in Z_PLACA_ABS] + [f"{L_TOT/10:.0f}"])
vC.cota_h([0, L_CAL, Z_PLACA_ABS[0], Z_PLACA_ABS[1], L_TOT], B, 10, total=False)
vC.cota_v([0, B / 2 - 75, B / 2 + 75, B], L_TOT, 8)
vC.chamada((Z_PLACA_ABS[4], B / 2 + 75), (8, 12), "IP-01 (8x) — chapa 150×150×9,5 mm, face rente ao concreto; furos Ø18 das placas conforme CM-01")
vC.texto((L_TOT + 420, B / 2), "FACE C", "sub", "MIDDLE_LEFT")

# ------------------------------------------------------------------ ELEVAÇÃO DE ARMAÇÃO 1:25 (face A para cima, como as vistas de fôrma)
va = pr.vista("ARMAÇÃO", (X0, Q[3] - 432), ESC, titulo="ELEVAÇÃO DE ARMAÇÃO — PL-01 A PF-03", subtitulo="armadura igual em todas as marcas da família; muda só a posição dos consolos", unidade="cm")
va.ret(0, 0, L_TOT, H, "VISTA")
for z in z_est:
    va.linha((z, COB), (z, H - COB), "ARMADURA")
va.barra([(40, COB + 18), (L_TOT - 40, COB + 18)], "N1", LONG["n"], 20, comp_cm=round((L_TOT - 80) / 10), ponto_rotulo=(4000, COB + 18), desloc=(10, -14))
va.linha((40, H - COB - 18), (L_TOT - 40, H - COB - 18), "ARMADURA")
if PROT:
    for y in (H / 2 - 250, H / 2 + 250):
        va.linha((0, y), (L_TOT, y), "ARMADURA")
    va.chamada((7000, H / 2 + 250), (10, 12), "C1 — 10 cord. Ø12,7 (5 por face de 60, a 25 do eixo), cortadas rente nas pontas")
va.chamada((z_est[8], H - COB), (8, 14), f"N2 — {n_est} estribos Ø8 c/15 (c/10 nos 150 cm das pontas e no cálice) + 2 N3 grampos por estribo")
va.cota_h([0, EST["zona"] + L_CAL, L_TOT - EST["zona"], L_TOT], 0, -10)
va.cota_h([0, 40, 40 + 15 * EST["s_dens"]], H, 10, total=False)
va.chamada((zc - 125, H), (12, 6), "N4 / N5 / N6 no consolo — ver DETALHE 1 e CORTE B-B")
pr.posicoes_desenho.update({"N2", "N3", "N4", "N5", "N6"} | ({"C1"} if PROT else set()))

# ------------------------------------------------------------------ CORTES 1:10 (cm)
Y_ROW = Q[3] - 585
def secao(nome, org, sub, consolo=False):
    v = pr.vista(nome, org, 10, titulo=nome, subtitulo=sub, unidade="cm")
    pts = [(-B / 2, -H / 2), (B / 2, -H / 2), (B / 2, H / 2), (-B / 2, H / 2)]
    if consolo:
        pts = [(-B / 2, -H / 2), (B / 2, -H / 2), (B / 2, H / 2 + CONS["proj"]), (-B / 2, H / 2 + CONS["proj"])]
    v.poli(pts, "CORTADO", fechada=True); v.hachura(pts, "AR-CONC", 0.03)
    e = [(-B / 2 + COB, -H / 2 + COB), (B / 2 - COB, -H / 2 + COB), (B / 2 - COB, H / 2 - COB), (-B / 2 + COB, H / 2 - COB)]
    v.poli(e, "ARMADURA", fechada=True)
    v.poli([(-B / 2 + COB, H / 2 - COB), (-B / 2 + COB + 60, H / 2 - COB - 60)], "ARMADURA")       # gancho 135°
    v.poli([(-B / 2 + COB + 60, H / 2 - COB), (-B / 2 + COB, H / 2 - COB - 60)], "ARMADURA")
    for y in Y_GR:                                                                                   # N3 grampos
        v.linha((-B / 2 + COB, y), (B / 2 - COB, y), "ARMADURA")
        v.poli([(-B / 2 + COB, y), (-B / 2 + COB + 50, y - 50)], "ARMADURA"); v.poli([(B / 2 - COB, y), (B / 2 - COB - 50, y + 50)], "ARMADURA")
    for x, y in LONG["xy"]:
        v.ponto_barra((x, y), 20)
    for x, y in CORD:
        v.ponto_barra((x, y), 12.7)
    v.cota_h([-B / 2, B / 2], -H / 2, -10)
    v.cota_v([-H / 2, H / 2], B / 2, 10)
    v.cota_v([-H / 2, -H / 2 + COB], -B / 2, -8, total=False)
    v.texto((0, H / 2 + (CONS["proj"] if consolo else 0) + 40), "FACE A", "min", "BOTTOM_CENTER")
    v.texto((0, -H / 2 - 40), "FACE C", "min", "TOP_CENTER")
    v.texto((B / 2 + 25, 0), "FACE B", "min", "MIDDLE_LEFT", rot=90); v.texto((-B / 2 - 25, 0), "FACE D", "min", "MIDDLE_RIGHT", rot=90)
    return v

va_ = secao("CORTE A-A", (X0 + 110, Y_ROW), "seção corrente — cobrimento 3,0 cm (CAA II)", False)
va_.chamada((-XB, YB), (-12, 10), f"N1 — {LONG['n']} Ø20 ({'4 por face de 60' if PROT else '5/face de 40, 7/face de 60'})")
va_.chamada((-B / 2 + COB, 150), (-12, 0), "N2 Ø8 c/15 (c/10 nas pontas), ganchos 135°")
va_.chamada((0, Y_GR[0]), (-12, -16), "N3 grampo Ø8 c/ ganchos 135° (2 por estribo)")
if PROT:
    va_.chamada((100, -250), (14, -26), "C1 — cord. Ø12,7 c/5, a 25 do eixo (grade da cabeceira)")
    va_.cota_h([-100, -50, 0, 50, 100], -H / 2, -20, total=False)
vb_ = secao("CORTE B-B", (X0 + 240, Y_ROW), "no consolo CP-TS (pino PN-1)", True)
vb_.ret(-10, H / 2 + CONS["proj"] - 300, 20, 300, "OCULTA")
vb_.poli([(-170, H / 2 + CONS["proj"] - 55), (-170, -H / 2 + COB + 50), (170, -H / 2 + COB + 50), (170, H / 2 + CONS["proj"] - 55)], "ARMADURA")
for x in (-150, 0, 150):
    vb_.ponto_barra((x, H / 2 + CONS["proj"] - 55), 16)
vb_.chamada((-150, H / 2 + CONS["proj"] - 55), (-12, 10), "N4 — 3 Ø16 tirante em U")
vb_.chamada((10, H / 2 + CONS["proj"] - 150), (16, -10), "PN-1 Ø20 (30 embutido)")
vb_.cota_h([-150, 0, 150], H / 2 + CONS["proj"], 8, total=False)

# ------------------------------------------------------------------ DETALHE 1 — consolo CP-TS (1:20, cm)
d1 = pr.vista("DETALHE 1", (X0 + 410, Y_ROW - 40), 10, titulo="DETALHE 1 — CONSOLO CP-TS", subtitulo="armadura e pino; topo a 3 % (sobe para a ponta); NBR 9062:2017 7.3", unidade="cm")
PW = H
zc0 = 1000
Z1, Z2 = 400, 1450
d1.poli([(-PW, Z1), (-PW, Z2), (0, Z2), (0, Z1)], "VISTA")
d1.interrupcao((-PW, Z1), (0, Z1)); d1.interrupcao((-PW, Z2), (0, Z2))
d1.poli([(0, zc0 - CONS["h"]), (CONS["proj"], zc0 - CONS["hp"]), (CONS["proj"], zc0 + CONS["proj"] * I_CAI), (0, zc0)], "VISTA")
d1.ret(PINO["x"] - 10, zc0 - 300 + 5, 20, PINO["L"], "OCULTA")
d1.ret(25, zc0 + 1, 250, 10, "METALICA")
d1.poli([(-PW + COB + 8, zc0 - 55 - 150), (-PW + COB + 8, zc0 - 55), (CONS["proj"] - 40, zc0 - 55)], "ARMADURA")
d1.poli([(CONS["proj"] - 40, zc0 - 55), (CONS["proj"] - 40, zc0 - 55 - 30)], "ARMADURA")
for dz in (-150, -250):
    d1.poli([(CONS["proj"] - 40, zc0 + dz), (-PW + COB, zc0 + dz)], "ARMADURA")
for dx in (60, 140, 220):
    d1.poli([(dx, zc0 - 30 + dx * I_CAI), (dx, zc0 - CONS["h"] + (CONS["h"] - CONS["hp"]) * dx / CONS["proj"] + 30)], "ARMADURA")
for z in range(500, Z2, 100):                                                     # N2 c/10 na zona do consolo
    d1.linha((-PW + COB, z), (-COB, z), "ARMADURA")
for x in (-PW + COB + 18, -COB - 18):
    d1.linha((x, Z1), (x, Z2), "ARMADURA")
d1.cota_v([zc0 - CONS["h"], zc0 - CONS["hp"], zc0, zc0 + CONS["proj"] * I_CAI], CONS["proj"], 10, total=False)
d1.cota_h([0, PINO["x"], CONS["proj"]], zc0 - CONS["h"], -10, total=False)
d1.cota_h([-PW, 0], Z1, -10)
d1.chamada((-PW + 300, zc0 - 55), (-8, 14), "N4 — 3 Ø16 (U horizontal, pernas 85 + dobra 15)")
d1.chamada((-200, zc0 - 150), (-14, -16), "N5 — 2 Ø10 estribos horizontais (costura)")
d1.chamada((140, zc0 - 250), (14, -14), "N6 — 3 Ø8 estribos verticais")
d1.chamada((PINO["x"], zc0 + 350), (10, 14), "PN-1 Ø20 CA-50 L=70, 30 embutido; ponta com chanfro")
d1.chamada((150, zc0 + 6), (20, 24), "NEO-1 30×15×1 cm c/ furo Ø30 mm (montagem)")
d1.chamada((CONS["proj"], zc0 + 9), (12, 8), f"assento: PL-01 +{f(Z_CONS['P1']/1000,3)} / PL-05 +{f(Z_CONS['P2']/1000,3)}")
d1.chamada((-COB - 18, 1350), (-12, 8), "N1 / N2 c/10 na zona do consolo")

# ------------------------------------------------------------------ DETALHE 2 — base no cálice (1:20, cm)
d2 = pr.vista("DETALHE 2", (X0 + 625, Y_ROW + 25), 20, titulo="DETALHE 2 — BASE DO PILAR NO CÁLICE", subtitulo="embutimento 100 cm; chaves de cisalhamento; armadura reta até 4 cm da base", unidade="cm")
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
    d2.linha((-H / 2 + COB, z), (H / 2 - COB, z), "ARMADURA")
d2.cota_v([0, L_CAL, 1500], H / 2 + 150, 10, total=False)
d2.cota_v([150, 350, 450, 650, 750, 950], -H / 2 - 30, -8, total=False)
d2.cota_h([-H / 2, H / 2], 0, -10)
d2.chamada((H / 2 + 30, 250), (18, 4), "chaves 4×20 cm, rebaixo 3 cm (4 faces)")
d2.chamada((H / 2 - COB, 1350), (14, 10), "N2 Ø8 c/10 até 150 cm")
d2.chamada((H / 2 + 150, -300), (8, -8), "cálice (projeto de fundações)")
d2.chamada((H / 2, L_CAL), (12, 14), "piso ±0,000; graute no cálice")
if PROT:
    d2.chamada((-H / 2 + COB + 18, 600), (-10, -8), "cordoalhas cortadas rente e seladas; transferência 76 cm dentro do cálice")

# ------------------------------------------------------------------ DETALHE 3 — inserto IP-01 (1:5, mm — chaparia)
d3 = pr.vista("DETALHE 3", (X0 + 805, Y_ROW + 30), 5, titulo="DETALHE 3 — INSERTO IP-01", subtitulo="chapa ASTM A36 150×150×9,5 + 2 pinos Ø12,5 c/ cabeça (NBR 8800 / ACI 318 cap. 17)", unidade="mm")
d3.ret(-75, -75, 150, 150, "METALICA")
for dy in (-40, 40):
    d3.circulo((0, dy), 6.25, "METALICA")
d3.cota_h([-75, 75], -75, -8); d3.cota_v([-75, -40, 40, 75], 75, 8, total=False)
d3.ret(130, -75, 9.5, 150, "METALICA")                                                # vista lateral
for dy in (-40, 40):
    d3.ret(139.5, dy - 6.25, 100, 12.5, "METALICA"); d3.ret(239.5, dy - 12.5, 8, 25, "METALICA")
d3.cota_h([130, 139.5, 239.5, 247.5], -75, -8, total=False)
d3.chamada((0, 40), (-12, 14), "pino Ø12,5 L=100 c/ cabeça Ø25 (soldado por fusão)")
d3.chamada((75, 60), (10, 8), "chapa 150×150×9,5 — galvanizada a fogo")
d3.chamada((60, -75), (10, -14), "furos Ø18 na chapa das placas (CM-01) — não furar o IP-01")

# ------------------------------------------------------------------ isométricos
pr.imagem(X0 + 10, 45, X0 + 590, 215, "/home/claude/letsara/pranchas/ISO-PIL-geral.png",
          titulo="ISOMÉTRICO — PL-01 com consolo, pino, insertos e alças", subtitulo="sem escala; faces A (consolo) e C (placas) indicadas")
pr.imagem(X0 + 605, 45, X0 + 815, 215, "/home/claude/letsara/pranchas/ISO-PIL-consolo.png",
          titulo="ISOMÉTRICO — CONSOLO CP-TS", subtitulo="sem escala")

# ------------------------------------------------------------------ coluna direita
y = Q[3] - 6
y = pr.tabela(XC, y, "MARCAS — FAMÍLIA DE PILARES 40×60 (MESMA ARMAÇÃO; 2 AL-2 CADA)", ["MARCA", "POSIÇÃO", "QT", "CONSOLOS (nível do assento, face)", "INSERTOS DE PLACA"],
              [[m[0], m[1], m[2], m[3], m[4]] for m in MARCAS], [14, 24, 8, 86, 50], h_lin=6.0)
L_N1 = round((L_TOT - 80) / 10)
barras = [dict(pos="N1", diam=20.0, qtd=LONG["n"], comp=L_N1, trechos=[f"{L_N1}"]),
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
ins = [["PN-1", "Pino Ø20 CA-50 L=700 (300 no consolo), a 175 mm da face", 1, "consolo, face A"],
       ["IP-01", "Chapa A36 150×150×9,5 + 2 pinos Ø12,5 c/ cabeça (p/ CM-01)", 8, "face C, c/1250 a partir do piso"],
       ["AL-2", "Alça laço cordoalha Ø12,7 (2 pernas 700), carga 40 kN", 2, "face A: 3200 do topo; 2300 da base"],
       ["NEO-1", "Neoprene 300×150×10 c/ furo Ø30 (montagem)", 1, "sobre o consolo"]]
y = pr.tabela(XC, y - 4, "INSERTOS POR PILAR (PL-01) — dimensões em mm", ["MARCA", "DESCRIÇÃO", "QT", "POSIÇÃO"], ins, [14, 100, 10, 58])
kg = ta["total_kg"]
qd = [["MARCA", "PL-01", "SEÇÃO", "40 × 60 cm"],
      ["COMPRIMENTO", f"{L_TOT/10:.0f} cm", "CONCRETO", "C50 / fckj 28 MPa" if PROT else "C40"],
      ["VOLUME", f"{f(0.24 * L_TOT / 1000, 2)} m³", "PESO", f"{f(PESO/10, 2)} t"],
      ["AÇO CA-50", f"{f(kg, 0)} kg", "TAXA", f"{f(LONG['n'] * 3.14 / 2400 * 100, 2)} %"],
      ["PROTENSÃO", "10 cord. Ø12,7 (92 kg)" if PROT else "—", "CG", f"{L_TOT / 2 / 1000:.2f} m da base".replace(".", ",")],
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
         "Consolos CP-TS (topo a 3 % subindo para a ponta), CP-VB e CP-MEZ com a mesma armadura N4/N5/N6 (NBR 9062:2017 7.3); posição e face por marca na tabela.",
         "Pino PN-1 Ø20 CA-50 (resiste 82 kN ≥ Hd 40 kN): concretado no consolo; tubo TB-1 da viga Ø40, grauteado numa ponta só de cada viga.",
         "Faces: A = consolo (interna), B e D = lados de 40, C = placas (externa). Pilar concretado deitado com a face A para cima e a face C no fundo da fôrma.",
         "Insertos IP-01 na face C a cada fiada de placa (125 cm a partir do piso); chaves de cisalhamento nas 4 faces do trecho embutido (100 cm).",
         "Içar na horizontal pelas 2 alças AL-2 e levantar à vertical pela alça superior com a base apoiada; estocar sobre 2 calços nas alças.",
         "Marca = geometria + insertos + armadura iguais; qualquer consolo a mais é marca nova. Cotas de concreto em cm, chaparia em mm, níveis em m. Não medir no desenho.",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(XC, y - 4, notas, 182)
pr.posicoes_desenho.add("N1")
avisos = pr.salvar(f"/home/claude/letsara/pranchas/ND-LET-PIL-{'P' if PROT else 'A'}01")
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
for a in avisos:
    print(a)
