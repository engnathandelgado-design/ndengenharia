"""ND-LET-PIL-A (armado) e ND-LET-PIL-P (protendido) — pilares 40×60 laterais e de fachada (A0).
Rodar: python pilares.py armado | protendido. Mesma geometria, insertos e consolos; muda só a armadura longitudinal.
Barras limitadas a Ø20. Marcas: peças iguais (geometria + insertos + armadura) têm a mesma marca."""
import json, math, sys
from prancha_nd import Prancha, MASSA_ACO

OPC = sys.argv[1] if len(sys.argv) > 1 else "armado"
PROT = OPC == "protendido"
AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
LG = json.load(open(AQ + "ligacoes.json"))
f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")

# ------------------------------------------------------------------ geometria (mm; z a partir do piso acabado)
B, H = 400, 600                 # 40 na direção y (lado da fachada lateral) × 60 na direção x
L_CAL, Z_TOP = 1000, 10000      # embutimento no cálice; topo da platibanda
L_TOT = L_CAL + Z_TOP
I_CAI = 0.03
zf = lambda x: LG["Z0_TS"] * 1000 + I_CAI * x
Z_CONS = {"P1": round(zf(475) + 450 * math.cos(math.atan(I_CAI)) - 10), "P2": round(zf(39625) + 450 * math.cos(math.atan(I_CAI)) - 10)}
CONS = dict(proj=300, h=450, hp=250, larg=400)           # consolo CP-TS: balanço 300, altura 450 na face, 250 na ponta
PINO = dict(d=20, L=700, emb=300)                        # pino Ø20 CA-50 (≤ 20 mm), 300 no consolo + 400 no TB-1
Z_PLACA = [round(1250 * k - 100) for k in range(1, 9)]  # insertos das placas (fiadas de 1,25 m), face externa
AL = [L_TOT - 3200, L_CAL + 2300]                        # alças (a partir da base): içamento na vertical e transporte
COB = 30
MARCAS = [
    ("PL-01", "P1 L3–L8", 6, "CP-TS +7,914 (x+)", "8 IP-01 (x−)"),
    ("PL-02", "P1 L2", 1, "CP-TS +7,914; 2 CP-MEZ (x+)", "8 IP-01 (x−)"),
    ("PL-03", "P1 L1 canto", 1, "CP-VB +7,460 (y+); 2 CP-MEZ", "8 IP-01 (x−) + 8 (y−)"),
    ("PL-04", "P1 L9 canto", 1, "CP-VB +7,460 (y−)", "8 IP-01 (x−) + 8 (y+)"),
    ("PL-05", "P2 L3–L8", 6, "CP-TS +9,089 (x−)", "8 IP-01 (x+)"),
    ("PL-06", "P2 L2", 1, "CP-TS +9,089; 2 CP-MEZ (x−)", "8 IP-01 (x+)"),
    ("PL-07", "P2 L1 canto", 1, "CP-VB +8,650 (y+); 2 CP-MEZ", "8 IP-01 (x+) + 8 (y−)"),
    ("PL-08", "P2 L9 canto", 1, "CP-VB +8,650 (y−)", "8 IP-01 (x+) + 8 (y+)"),
    ("PF-01", "P3 e P14", 2, "2 CP-VB +7,750 (x±); P3: 2 CP-MEZ", "8 IP-01 (y)"),
    ("PF-02", "P4 e P15", 2, "2 CP-VB +8,060 (x±); P4: 2 CP-MEZ", "8 IP-01 (y)"),
    ("PF-03", "P5 e P16", 2, "2 CP-VB +8,350 (x±); P5: 2 CP-MEZ", "8 IP-01 (y)"),
]
N_PIL = sum(m[2] for m in MARCAS)

# ------------------------------------------------------------------ armadura
if PROT:
    LONG = dict(pos="N1", n=8, d=20.0, desc="4 Ø20 por face de 60 (cantos comuns)",
                xy=[(-155, -255), (155, -255), (-155, 255), (155, 255), (-155, -85), (155, -85), (-155, 85), (155, 85)])
    CORD = [(x, y) for y in (-250, 250) for x in (-100, -50, 0, 50, 100)]
    SIG_PI = 1400
else:
    LONG = dict(pos="N1", n=20, d=20.0, desc="5 Ø20 por face de 40 e 7 Ø20 por face de 60 (cantos comuns)",
                xy=[(x, -255) for x in (-155, -78, 0, 78, 155)] + [(x, 255) for x in (-155, -78, 0, 78, 155)] +
                   [(-155, y) for y in (-170, -85, 0, 85, 170)] + [(155, y) for y in (-170, -85, 0, 85, 170)])
    CORD = []
EST = dict(d=8.0, s_corr=150, s_dens=100, zona=1500)      # estribos Ø8: c/15 corrente, c/10 nos 1,5 m das pontas e no cálice
z_est = list(range(50, EST["zona"] + L_CAL, EST["s_dens"])) + list(range(EST["zona"] + L_CAL, L_TOT - EST["zona"], EST["s_corr"])) + \
        list(range(L_TOT - EST["zona"], L_TOT - 40, EST["s_dens"]))
z_est = sorted(set(z_est))
n_est = len(z_est)
C_EST = round((2 * (B - 2 * COB - 8) + 2 * (H - 2 * COB - 8) + 2 * 80) / 10)          # cm, com ganchos de 80
C_GR = round((H - 2 * COB - 8 + 2 * 80) / 10)                                         # grampo Ø8 no sentido de 60

pr = Prancha("A1", dict(cliente="MARQUE ENGENHARIA", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo=f"PILARES 40×60 LATERAIS E DE FACHADA — {'PRÉ-TRACIONADOS NA CABECEIRA' if PROT else 'CONCRETO ARMADO'} — FÔRMA, ARMAÇÃO E INSERTOS",
                        desenho=f"ND-LET-PIL-{'P' if PROT else 'A'}01", folha="01/01", fase="PARA APROVAÇÃO — OPÇÃO " + ("B (PROTENDIDO)" if PROT else "A (ARMADO)"),
                        marca="PL-01 a PF-03", qtd=N_PIL, peso=f(0.24 * 11 * 25, 1), volume=f(0.24 * 11, 2)))
pr.revisao("00", "12/10/2026", "EMISSÃO PARA COMPARAÇÃO DE CUSTO (OPÇÕES A E B)")

# ------------------------------------------------------------------ ELEVAÇÃO DE FÔRMA PL-01 (1:50) — deitado, face x+ (consolo) para cima
ve = pr.vista("ELEVAÇÃO DE FÔRMA", (45, 478), 25, titulo="ELEVAÇÃO DE FÔRMA — PL-01 (P1, LINHAS 3 A 8)",
              subtitulo="pilar deitado na fôrma: base à esquerda; consolo na face x+ (para cima); cotas a partir da base")
zc = Z_CONS["P1"] + L_CAL                                   # a partir da base
ve.ret(0, 0, L_TOT, H, "VISTA")
ve.linha((L_CAL, 0), (L_CAL, H), "EIXO")
for k in range(3):                                           # chaves de cisalhamento no cálice (4 faces)
    z0 = 150 + k * 300
    ve.poli([(z0, 0), (z0 + 40, -30), (z0 + 160, -30), (z0 + 200, 0)], "VISTA")
    ve.poli([(z0, H), (z0 + 40, H + 30), (z0 + 160, H + 30), (z0 + 200, H)], "VISTA")
# consolo (topo a 3 %: sobe para a ponta na direção x+, que aqui é "para cima" — no desenho deitado o 3 % fica no sentido de z)
c0, c1 = zc - CONS["h"], zc
ve.poli([(c0, H), (c1 - 0 - 0, H + CONS["proj"]), (c1 + CONS["proj"] * I_CAI + 0, H + CONS["proj"]), (c1 + 0, H)], "VISTA")
ve.poli([(c0, H), (c0 + CONS["h"] - CONS["hp"], H + CONS["proj"])], "VISTA")
ve.linha((c1 - 125, H + CONS["proj"] - 0), (c1 - 125 + 12, H + CONS["proj"]), "OCULTA")
ve.ret(zc - 125 - 10, H + CONS["proj"] - 300, 20, 300 + PINO["L"] - 300, "OCULTA")       # pino PN-1 (parte embutida)
for z in Z_PLACA:
    ve.ret(z + L_CAL - 75, -9.5, 150, 9.5, "METALICA")
for z in AL:
    ve.poli([(z - 50, 0), (z - 50, -110), (z, -150), (z + 50, -110), (z + 50, 0)], "METALICA")
ve.cota_h([0, L_CAL, c0, zc, L_TOT], 0, -12)
ve.cota_ord([L_CAL] + [z + L_CAL for z in Z_PLACA] + [L_TOT], -9.5, -34, x0=L_CAL,
            rotulos=["0"] + [f"{z}" for z in Z_PLACA] + [f"{Z_TOP}"])
ve.cota_h(AL + [L_TOT], 0, -50, total=False)
ve.cota_v([0, H], L_TOT, 8)
ve.chamada((zc - 150, H + CONS["proj"]), (10, 12), f"consolo CP-TS: topo a 3 %, assento em +{f(Z_CONS['P1']/1000,3)}")
ve.chamada((zc - 125, H + 150), (26, -16), "PN-1 pino Ø20 CA-50 L=700 (300 embutido)")
ve.chamada((Z_PLACA[2] + L_CAL, -9.5), (8, -58), "IP-01 chapa 150×150×9,5 + 2 pinos (placas, 8x)")
ve.chamada((AL[0], -150), (8, -60), "AL-2 alça laço cordoalha Ø12,7 (2x)")
ve.chamada((300, -30), (10, -62), "chaves de cisalhamento 40×200 nas 4 faces (cálice)")
ve.chamada((L_TOT - 300, H), (6, 14), "topo da platibanda +10,000")
ve.marcador_corte((5000, -120), (5000, H + 120), "A", lado=1)
ve.marcador_corte((zc - 125, -120), (zc - 125, H + 420), "B", lado=1)
ve.marcador_detalhe((zc - 100, H + 120), 420, 1, ang=30, dist=8)
ve.marcador_detalhe((L_CAL, H / 2), 520, 2, ang=120, dist=8)

# ------------------------------------------------------------------ ELEVAÇÃO DE ARMAÇÃO (1:50)
va = pr.vista("ELEVAÇÃO DE ARMAÇÃO", (45, 372), 25, titulo="ELEVAÇÃO DE ARMAÇÃO — PL-01 A PF-03",
              subtitulo="armadura igual em todas as marcas; muda só a posição dos consolos")
va.ret(0, 0, L_TOT, H, "VISTA")
for z in z_est:
    va.linha((z, COB), (z, H - COB), "ARMADURA")
va.barra([(40, COB + 10), (L_TOT - 40, COB + 10)], "N1", LONG["n"], 20, comp_cm=round((L_TOT - 80) / 10), ponto_rotulo=(4000, COB + 10), desloc=(10, -14))
if PROT:
    for y in (COB + 20 + 25, H - COB - 20 - 25):
        va.linha((0, y), (L_TOT, y), "ARMADURA")
    va.chamada((7000, COB + 45), (10, -20), "C1 — 10 cord. Ø12,7 (5 por face, a 250 do eixo)")
va.chamada((z_est[8], COB), (8, -36), f"N2 — {n_est} estribos Ø8: c/10 nos 1,5 m das pontas e no cálice, c/25 no restante".replace("c/25", f"c/{EST['s_corr']//10}"))
va.cota_h([0, EST["zona"] + L_CAL, L_TOT - EST["zona"], L_TOT], 0, -12)
va.chamada((zc - 125, H), (12, 6), "N4/N5/N6 no consolo — ver DETALHE 1")
pr.posicoes_desenho.update({"N2", "N3", "N4", "N5", "N6", "C1"} if PROT else {"N2", "N3", "N4", "N5", "N6"})

# ------------------------------------------------------------------ CORTES 1:10
def secao(nome, org, sub, consolo=False):
    v = pr.vista(nome, org, 10, titulo=nome, subtitulo=sub)
    pts = [(-B / 2, -H / 2), (B / 2, -H / 2), (B / 2, H / 2), (-B / 2, H / 2)]
    if consolo:
        pts = [(-B / 2, -H / 2), (B / 2, -H / 2), (B / 2, H / 2 + CONS["proj"]), (-B / 2, H / 2 + CONS["proj"]), (-B / 2, H / 2)]
    v.poli(pts, "CORTADO", fechada=True); v.hachura(pts, "AR-CONC", 0.03)
    e = [(-B / 2 + COB, -H / 2 + COB), (B / 2 - COB, -H / 2 + COB), (B / 2 - COB, H / 2 - COB), (-B / 2 + COB, H / 2 - COB)]
    v.poli(e, "ARMADURA", fechada=True)
    v.linha((-B / 2 + COB, 0), (B / 2 - COB, 0), "ARMADURA")                    # N3 grampo
    for x, y in LONG["xy"]:
        v.ponto_barra((x, y), 20)
    for x, y in CORD:
        v.ponto_barra((x, y), 12.7)
    v.cota_h([-B / 2, B / 2], -H / 2, -10)
    v.cota_v([-H / 2, H / 2], B / 2, 10)
    return v

va_ = secao("CORTE A-A", (75, 215), "seção corrente", False)
va_.chamada((155, 255), (14, 10), f"N1 — {LONG['n']} Ø20 ({LONG['desc']})")
va_.chamada((B / 2 - COB, 100), (14, 0), f"N2 Ø8 c/{EST['s_corr']//10} (c/10 nas pontas)")
va_.chamada((0, 0), (14, -16), "N3 grampo Ø8 (mesmo passo)")
if PROT:
    va_.chamada((100, -250), (14, -20), "C1 — cord. Ø12,7 c/50, a 250 do eixo (grade da cabeceira)")
    va_.cota_h([-100, -50, 0, 50, 100], -H / 2, -20, total=False)
vb_ = secao("CORTE B-B", (200, 215), "no consolo CP-TS (pino PN-1)", True)
vb_.ret(-10, H / 2 + CONS["proj"] - 300, 20, 300, "OCULTA")
vb_.poli([(-170, H / 2 + CONS["proj"] - 55), (-170, -H / 2 + COB + 50), (170, -H / 2 + COB + 50), (170, H / 2 + CONS["proj"] - 55)], "ARMADURA")
for x in (-150, 0, 150):
    vb_.ponto_barra((x, H / 2 + CONS["proj"] - 55), 16)
vb_.chamada((150, H / 2 + CONS["proj"] - 55), (14, 10), "N4 — 3 Ø16 tirante em U (pernas de 850 + dobra)")
vb_.chamada((10, H / 2 + CONS["proj"] - 150), (16, -10), "PN-1 Ø20 (300 embutido)")

# ------------------------------------------------------------------ DETALHE 1 — consolo CP-TS (1:20) — pilar na vertical, consolo na face x+
d1 = pr.vista("DETALHE 1", (380, 190), 20, titulo="DETALHE 1 — CONSOLO CP-TS", subtitulo="armadura e pino; topo a 3 % (sobe para a ponta)")
PW = H                                                       # largura do pilar na direção do consolo (600)
zc0 = 1000
d1.poli([(-PW, 0), (-PW, 1700), (0, 1700), (0, 0)], "VISTA")
d1.interrupcao((-PW, 0), (0, 0)); d1.interrupcao((-PW, 1700), (0, 1700))
d1.poli([(0, zc0 - CONS["h"]), (CONS["proj"], zc0 - CONS["hp"]), (CONS["proj"], zc0 + CONS["proj"] * I_CAI), (0, zc0)], "VISTA")
d1.ret(175 - 10, zc0 - 300 + 5, 20, PINO["L"], "OCULTA")                         # PN-1
d1.ret(25, zc0 - 10 + 1, 300 - 50, 10, "METALICA")                               # neoprene (montagem)
# N4: 3 Ø16 em U horizontal — pernas atravessam o pilar e dobram 150 para baixo na face oposta
d1.poli([(-PW + COB + 8, zc0 - 55 - 150), (-PW + COB + 8, zc0 - 55), (CONS["proj"] - 40, zc0 - 55)], "ARMADURA")
d1.poli([(CONS["proj"] - 40, zc0 - 55), (CONS["proj"] - 40, zc0 - 55 - 30)], "ARMADURA")
for dz in (-150, -250):                                                           # N5 costura (estribos horizontais)
    d1.poli([(CONS["proj"] - 40, zc0 + dz), (-PW + COB, zc0 + dz)], "ARMADURA")
for dx in (60, 140, 220):                                                         # N6 estribos verticais do consolo
    d1.poli([(dx, zc0 - 30 + dx * I_CAI), (dx, zc0 - CONS["h"] + (CONS["h"] - CONS["hp"]) * dx / CONS["proj"] + 30)], "ARMADURA")
for z in range(100, 1700, 100):                                                   # N2 c/10 na zona do consolo
    d1.linha((-PW + COB, z), (-COB, z), "ARMADURA")
for x in (-PW + COB + 10, -COB - 10):
    d1.linha((x, 0), (x, 1700), "ARMADURA")
d1.cota_v([zc0 - CONS["h"], zc0, zc0 + CONS["proj"] * I_CAI], CONS["proj"], 10, total=False)
d1.cota_h([0, 175, CONS["proj"]], zc0 - CONS["h"], -10, total=False)
d1.cota_h([-PW, 0], 0, -10)
d1.chamada((-PW + 300, zc0 - 55), (-8, 14), "N4 — 3 Ø16 (U horizontal, pernas 850 + dobra 150)")
d1.chamada((-200, zc0 - 150), (-14, -16), "N5 — 2 Ø10 estribos horizontais (costura)")
d1.chamada((140, zc0 - 250), (14, -14), "N6 — 3 Ø8 estribos verticais")
d1.chamada((175, zc0 + 350), (10, 14), "PN-1 Ø20 CA-50 L=700, 300 embutido; ponta com chanfro")
d1.chamada((150, zc0 - 4), (20, 24), "NEO-1 300×150×10 c/ furo Ø30 (montagem)")
d1.chamada((CONS["proj"], zc0 + 9), (12, 8), f"assento: PL-01 +{f(Z_CONS['P1']/1000,3)} / PL-05 +{f(Z_CONS['P2']/1000,3)}")
d1.chamada((-COB - 10, 1500), (-12, 8), "N1 / N2 c/10 na zona do consolo")

# ------------------------------------------------------------------ DETALHE 2 — base no cálice (1:20)
d2 = pr.vista("DETALHE 2", (560, 200), 20, titulo="DETALHE 2 — BASE DO PILAR NO CÁLICE", subtitulo="embutimento 1,00 m; chaves de cisalhamento; armadura reta até 40 mm da base")
d2.ret(-B / 2 - 50, 0, B + 100, 0, "VISTA")
d2.poli([(-H / 2, 0), (H / 2, 0), (H / 2, 1600), (-H / 2, 1600)], "VISTA")
for k in range(3):
    z0 = 150 + k * 300
    for sg in (-1, 1):
        d2.poli([(sg * H / 2, z0), (sg * (H / 2 + 30), z0 + 40), (sg * (H / 2 + 30), z0 + 160), (sg * H / 2, z0 + 200)], "VISTA")
d2.linha((-H / 2 - 400, L_CAL), (H / 2 + 400, L_CAL), "EIXO")
d2.poli([(-H / 2 - 150, L_CAL), (-H / 2 - 150, -500), (H / 2 + 150, -500), (H / 2 + 150, L_CAL)], "OCULTA")
for x in (-H / 2 + COB + 10, H / 2 - COB - 10):
    d2.linha((x, 40), (x, 1600), "ARMADURA")
for z in range(50, 1500, 100):
    d2.linha((-H / 2 + COB, z), (H / 2 - COB, z), "ARMADURA")
d2.cota_v([0, L_CAL, 1500], H / 2 + 150, 10, total=False)
d2.cota_h([-H / 2, H / 2], 0, -10)
d2.chamada((H / 2 + 30, 250), (12, 10), "chaves 40×200 (4 faces)")
d2.chamada((H / 2 - COB, 1350), (14, 10), "N2 Ø8 c/10 até 1,50 m")
d2.chamada((H / 2 + 150, -300), (8, -8), "cálice (projeto de fundações)")
d2.chamada((H / 2, L_CAL), (12, 14), "piso ±0,000; graute no cálice")
if PROT:
    d2.chamada((-H / 2 + COB + 10, 600), (-10, -8), "cordoalhas cortadas rente e seladas; transferência 760 mm dentro do cálice")

# ------------------------------------------------------------------ coluna direita
x0c, y = pr.quadro[2] - 180, pr.quadro[3] - 6
y = pr.tabela(x0c, y, "MARCAS — PILARES 40×60 (MESMA ARMAÇÃO; 2 AL-2 CADA)", ["MARCA", "POSIÇÃO", "QT", "CONSOLOS (nível do assento)", "INSERTOS DE PLACA"],
              [[m[0], m[1], m[2], m[3], m[4]] for m in MARCAS], [14, 26, 8, 78, 54], h_lin=6.0)
L_N1 = round((L_TOT - 80) / 10)
barras = [dict(pos="N1", diam=20.0, qtd=LONG["n"], comp=L_N1, trechos=[f"{L_N1}"]),
          dict(pos="N2", diam=8.0, qtd=n_est, comp=C_EST, forma=[(0, 0), (34, 0), (34, 54), (0, 54), (0, 0), (1.5, 1.5)], trechos=["34", "54", "34", "54"]),
          dict(pos="N3", diam=8.0, qtd=n_est, comp=C_GR, forma=[(0, 4), (0, 0), (54, 0), (54, 4)], trechos=["8", "54", "8"]),
          dict(pos="N4", diam=16.0, qtd=3, comp=234, forma=[(0, 15), (0, 0), (85, 0), (85, 34), (0, 34), (0, 49)], trechos=["15", "85", "34", "85", "15"]),
          dict(pos="N5", diam=10.0, qtd=2, comp=round((2 * (340 + 700) + 140) / 10), forma=[(0, 0), (70, 0), (70, 34), (0, 34), (0, 0), (1.5, 1.5)], trechos=["70", "34", "70", "34"]),
          dict(pos="N6", diam=8.0, qtd=3, comp=round((2 * (340 + 400) + 140) / 10), forma=[(0, 0), (34, 0), (34, 40), (0, 40), (0, 0), (1.5, 1.5)], trechos=["34", "40", "34", "40"])]
ta = pr.tabela_croqui(x0c, y - 4, barras, h_lin=9.0)
y = ta["y_base"]
if PROT:
    tc = pr.tabela_cordoalhas(x0c, y - 4, [dict(pos="C1", diam=12.7, qtd=10, y=250, forca=SIG_PI * 98.7 / 1000, isol=0)], 60)
    y = tc["y_base"]
ins = [["PN-1", "Pino Ø20 CA-50 L=700 (300 no consolo)", 1, "consolo"],
       ["IP-01", "Chapa 150×150×9,5 + 2 pinos Ø12,5 c/ cabeça (p/ CM-01)", 8, "face externa, c/1,25"],
       ["AL-2", "Alça laço cordoalha Ø12,7 (2 pernas 700)", 2, "3,20 do topo; 2,30 da base"],
       ["NEO-1", "Neoprene 300×150×10 c/ furo Ø30 (montagem)", 1, "sobre o consolo"]]
y = pr.tabela(x0c, y - 4, "INSERTOS POR PILAR (PL-01)", ["MARCA", "DESCRIÇÃO", "QT", "POSIÇÃO"], ins, [14, 108, 10, 48])
kg = ta["total_kg"]
qd = [["SEÇÃO", "40 × 60", "COMPRIMENTO", f"{L_TOT} mm"],
      ["CONCRETO", "C40 (C50 se protendido)" if not PROT else "C50 / fckj 28", "VOLUME", f"{f(0.24 * L_TOT / 1000, 2)} m³"],
      ["PESO", f"{f(0.24 * L_TOT / 1000 * 25, 1)} kN", "AÇO CA-50", f"{f(kg, 0)} kg/pilar"],
      ["TAXA", f"{f(LONG['n'] * 3.14 / 2400 * 100, 2)} %", "PROTENSÃO", "10 cord. Ø12,7 (92 kg)" if PROT else "—"],
      ["PILARES", f"{N_PIL}", "CG", f"{L_TOT / 2 / 1000:.2f} m da base".replace(".", ",")]]
y = pr.tabela(x0c, y - 4, "QUADRO DA PEÇA", ["ITEM", "VALOR", "ITEM", "VALOR"], qd, [26, 64, 30, 60])
mem = [["ELU, vento lado 60 (λu)", "1,22" if PROT else "1,03"], ["ELU, vento lado 40 (λu)", "1,38" if PROT else "1,08"],
       ["Fachada, vento lado 40 (λu)", "1,30" if PROT else "1,01"], ["Armadura mínima (0,4 %)", f"{f(LONG['n'] * 3.14, 1)} ≥ 9,6 cm²"],
       ["Fissuração (freq.)", "σ = −2,7 MPa (comprimido)" if PROT else "σ = 1,45 ≤ 2,46 MPa (estádio I)"],
       ["Içamento (2 pontos)", "σ ≤ 1,7 MPa com ×1,3 — sem fissura"]]
y = pr.tabela(x0c, y - 4, "MEMÓRIA RESUMIDA (método geral, NBR 6118:2023)", ["VERIFICAÇÃO", "RESULTADO"], mem, [70, 110])
notas = [("Concreto C50; cordoalhas CP-190 RB Ø12,7 na grade da cabeceira (passo 50), 5 por face a 250 mm do eixo: cabeceira regulada em 525 mm "
          "(pilar deitado com o lado de 60 na vertical). σpi = 1400 MPa; liberar com fckj ≥ 28 MPa; cortar rente e selar." if PROT else
          "Concreto C40. Barras longitudinais retas de ponta a ponta (sem emenda); nenhuma bitola acima de Ø20."),
         f"Estribos N2 Ø8 fechados com ganchos de 135°, c/{EST['s_corr']//10} no trecho corrente e c/10 nos 1,5 m junto ao consolo, no topo e no cálice; grampos N3 em todo estribo.",
         "Consolos CP-TS (topo a 3 % subindo para a ponta), CP-VB e CP-MEZ com a mesma armadura N4/N5/N6; posição por marca na tabela.",
         "Pino PN-1 Ø20 CA-50 (resiste a 82 kN de corte ≥ Hd 40 kN): concretado no consolo; tubo TB-1 da viga passa a Ø40.",
         "Insertos IP-01 na face externa a cada fiada de placa (1,25 m); cobrimento 30 mm (CAA II); chaves de cisalhamento nas 4 faces do trecho embutido.",
         "Içar na horizontal pelas 2 alças AL-2 e levantar à vertical pela alça superior com a base apoiada; estocar sobre 2 calços nas alças.",
         "Marca = geometria + insertos + armadura iguais; qualquer consolo a mais é marca nova. Cotas em mm, níveis em m. Não medir no desenho.",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(x0c, y - 4, notas, 180)
pr.posicoes_desenho.add("N1")
avisos = pr.salvar(f"/home/claude/letsara/pranchas/ND-LET-PIL-{'P' if PROT else 'A'}01")
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
for a in avisos:
    if a[0] == "ERRO":
        print(a)
