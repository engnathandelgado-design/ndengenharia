"""ND-LET-COB01 — cobertura metálica: planta de enterçamento de todo o pavilhão (comprimentos, espaçamentos e folgas de
montagem das terças) e ligações terça × viga: suporte ST-1 soldado no inserto CH-T1, furação da terça, mão-francesa na
chapa OR-1 soldada no inserto CH-MF do fundo da viga. Metálica em mm. A1.

Padrão de apresentação: planta de terças com marcas em balão e cadeia de cotas dos espaçamentos; detalhe do suporte em
elevação + corte + planta; lista de materiais com peso (referências de pranchas de cobertura metálica do escritório).
"""
import json
import math
from prancha_nd import Prancha

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
LG = json.load(open(AQ + "ligacoes.json"))
CB = json.load(open(AQ + "cobertura_metalica.json"))
f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
YL = [0.0, 10.05, 19.705, 29.36, 38.865, 48.445, 58.025, 67.605, 76.81]          # eixos 1..9 (m)
X0E, X0D, LTS = 0.325, 20.325, 19.45                                                # vigas TS-01 (m)
ST = LG["s_tercas"]
XT = [round((X0E + s - 0.027) * 1000) for s in ST] + [round((X0D + s - 0.027) * 1000) for s in ST]   # 26 linhas de terças (mm)
YLmm = [round(y * 1000) for y in YL]
VAOS = [YLmm[i + 1] - YLmm[i] for i in range(8)]
FOLGA = 10                      # folga de montagem entre a ponta da terça e o eixo do suporte (mm) — 20 mm entre terças
L_TERCA = [v - 2 * FOLGA for v in VAOS]
E_FURO = 60                     # furo da ponta: 60 mm da ponta da terça (50 do eixo do suporte)
Z_FURO = (100, 200)             # furos centrados na alma (h 300): 100 e 200 do fundo
Z_TERCA = 10                    # fundo da terça 10 mm acima do topo do concreto (caimento/tolerância)
H_TERCA, B_TERCA = 300, 85
PESO_UE = 11.8                  # kg/m — Ue 300×85×25×3,00
ST1 = dict(t=8, larg=220, h=290)         # suporte: chapa 8 × 220 (ao longo da terça) × 290 (altura acima do concreto)
Z_DIAG = 255                             # furo Ø18 no ST-1 (só nos de borda) para a diagonal Ø16 das correntes
IT1 = dict(t=12.5, lx=200, ly=200)        # inserto no topo da viga: 150 (transv.) × 250 (long.) × 9,5; 4 pinos Ø16 c/ cabeça
IM1 = dict(t=12.5, lx=150, ly=360)        # inserto no fundo da viga: idem, 2 pinos Ø12,5 c/ cabeça (OR-1 do cálculo)
CHMF = dict(t=8, l=300, h=100)           # chapa furada (2 Ø14) soldada no CH-MF, para a mão-francesa
Y_MF = 1070                              # ponto da terça onde a mão-francesa pega (mm do eixo da viga)
N_LIN, N_T = 9, 26
pr = Prancha("A1", dict(cliente="MARQUE ENGENHARIA", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="COBERTURA METÁLICA — PLANTA DE ENTERÇAMENTO, SUPORTE DE TERÇA ST-1 E MÃO-FRANCESA",
                        desenho="ND-LET-COB01", folha="04/05", fase="PARA APROVAÇÃO", rev="01"))
pr.revisao("01", pr.dados["data"], "furos centrados na alma; suporte ST-1 + CH-T1; mão-francesa na OR-1; planta completa")
c1, mf = CB["CT1"], CB["MF1"]

# ------------------------------------------------------------------ PLANTA DE ENTERÇAMENTO 1:150 (papel: horizontal = eixo y da obra)
ESC_P = 175
v = pr.vista("PLANTA", (72, 322), ESC_P, titulo="PLANTA DE ENTERÇAMENTO — COBERTURA COMPLETA",
             subtitulo="terças Ue 300×85×25×3,00 ZAR 345 c/1579, entre os eixos 1 e 9; marcas T-1..T-8 por vão")
M = lambda y, x: (y, x)       # modelo (y, x) → papel (horizontal, vertical)
# vigas TS-01 (duas por linha) e pilar central
for yl in YLmm:
    for x0 in (X0E, X0D):
        v.poli([M(yl - 200, x0 * 1000), M(yl + 200, x0 * 1000), M(yl + 200, (x0 + LTS) * 1000), M(yl - 200, (x0 + LTS) * 1000)], "VISTA", True)
    v.ret(yl - 250, 19850, 500, 400, "CORTADO")
    v.ret(yl - 300, -300, 600, 600, "CORTADO"); v.ret(yl - 300, 39700, 600, 600, "CORTADO")
# terças
for k in range(8):
    ya, yb = YLmm[k] + FOLGA, YLmm[k + 1] - FOLGA
    for x in XT:
        v.linha(M(ya, x), M(yb, x), "METALICA")
        v.linha(M(ya, x + B_TERCA), M(yb, x + B_TERCA), "METALICA")
# correntes (3 linhas por vão) e diagonais em X (vãos contraventados: 2-3, 4-5, 5-6, 7-8)
nos = [round((x - 0.027) * 1000) for x in LG["nos_contraventamento_x_esq"]]
for k in range(8):
    ya, yb = YLmm[k], YLmm[k + 1]
    for q in (0.25, 0.5, 0.75):
        yq = ya + q * (yb - ya)
        v.linha(M(yq, XT[0]), M(yq, XT[12]), "INDICACAO"); v.linha(M(yq, XT[13]), M(yq, XT[25]), "INDICACAO")
    if k in (1, 3, 4, 6):
        for half in (0, 20000):
            for a, b in zip(nos[:-1], nos[1:]):
                for j in range(4):
                    y1 = ya + j * (yb - ya) / 4 + 140; y2 = ya + (j + 1) * (yb - ya) / 4 - 140
                    v.linha(M(y1, a + half + 140), M(y2, b + half - 140), "ARMADURA")
                    v.linha(M(y1, b + half - 140), M(y2, a + half + 140), "ARMADURA")
# eixos e marcas
for i, yl in enumerate(YLmm):
    v.eixo(M(yl, -900), M(yl, 40900), 0)
    xp, yp = v.P(M(yl, 41900))
    pr.msp.add_circle((xp, yp), 3.2, dxfattribs={"layer": "INDICACAO"})
    pr.texto(xp, yp, str(i + 1), "sub", "TITULO", "MIDDLE_CENTER")
for lbl, x in (("A", -900), ("C", 20050), ("E", 40900)):
    v.eixo(M(-900, x), M(YLmm[-1] + 900, x), 0)
    xp, yp = v.P(M(-1900, x))
    pr.msp.add_circle((xp, yp), 3.2, dxfattribs={"layer": "INDICACAO"})
    pr.texto(xp, yp, lbl, "sub", "TITULO", "MIDDLE_CENTER")
for k in range(8):
    ym = (YLmm[k] + YLmm[k + 1]) / 2
    for x, s in ((XT[3], "esq"), (XT[16], "dir")):
        xp, yp = v.P(M(ym, x + 700))
        pr.msp.add_circle((xp, yp), 4.0, dxfattribs={"layer": "INDICACAO"})
        pr.texto(xp, yp, f"T-{k+1}", "nota", "TITULO", "MIDDLE_CENTER")
    v.texto(M(ym, XT[8] + 500), f"L = {L_TERCA[k]}", "nota", "MIDDLE_CENTER", rot=90)
    v.texto(M(ym, XT[21] + 500), f"L = {L_TERCA[k]}", "nota", "MIDDLE_CENTER", rot=90)
# cotas: vãos (em cima), espaçamento das terças (esquerda), totais
v.cota_h(YLmm, -900, -10, total=False)
v.cota_h([YLmm[0], YLmm[-1]], 41900, 10, total=False)
xs_e = [325] + XT[:13] + [19775]
v.cota_v(xs_e, YLmm[0] - 900, -12, total=False)
v.cota_v([325, 19775], YLmm[0] - 900, -24, total=False)
v.cota_v([20325] + XT[13:] + [39775], YLmm[0] - 900, -12, total=False)
v.cota_v([20325, 39775], YLmm[0] - 900, -24, total=False)
v.cota_v([0, 40000], YLmm[0] - 900, -36, total=False)
v.chamada(M(YLmm[2] + 4000, XT[9] + 60), (28, -8), "terça Ue 300×85×25×3,00 — alma na face +x do ST-1 (todas no mesmo lado)")
v.chamada(M(YLmm[1] + 2400, (XT[0] + XT[12]) / 2 + 0), (26, 14), "correntes flexíveis Ø12,5 (L/4, L/2, 3L/4) — ver COB02")
v.chamada(M(YLmm[4] + 4800, nos[2] + 1500), (26, 10), "contraventamento em X Ø12,5 em subpainéis 3158 × L/4 (vãos 2-3, 4-5, 5-6, 7-8) — ver COB02")
v.chamada(M(YLmm[3] + 3000, 19950), (18, 22), "pilar central PC / viga I110")
v.marcador_detalhe(M(YLmm[5], XT[20]), 600, 1, ang=60, dist=8)
v.marcador_detalhe(M(YLmm[6] + Y_MF, XT[22]), 500, 2, ang=-50, dist=8)

# ------------------------------------------------------------------ DETALHE 1 — SUPORTE DE TERÇA ST-1 (1:5): elevação, corte, planta
E5 = 5
# (a) ELEVAÇÃO — olhando ao longo da viga (plano y–z): webs das terças em vista, ST-1 atrás, parafusos
e = pr.vista("DETALHE 1A", (165, 200), E5, titulo="DETALHE 1 — SUPORTE DE TERÇA ST-1 — ELEVAÇÃO",
             subtitulo="vista no plano da terça (ao longo da viga); terças T-n / T-n+1 nas pontas")
e.ret(-600, -150, 1200, 150, "CORTADO"); e.hachura([(-600, -150), (600, -150), (600, 0), (-600, 0)], "AR-CONC", 0.03)
e.chapa(-IT1["ly"] / 2, -IT1["t"], IT1["ly"], IT1["t"], 0.2)                                   # CH-T1 nivelado no topo
e.ret(-ST1["larg"] / 2, 0, ST1["larg"], ST1["h"], "OCULTA")                                     # ST-1 (atrás das terças)
e.hachura([(-FOLGA, 0), (FOLGA, 0), (FOLGA, ST1["h"]), (-FOLGA, ST1["h"])], "ANSI31", 0.25, "METALICA")
for sg in (-1, 1):
    xa = sg * FOLGA
    xb = sg * 600
    e.poli([(xa, Z_TERCA), (xb, Z_TERCA), (xb, Z_TERCA + H_TERCA), (xa, Z_TERCA + H_TERCA)], "METALICA", True)
    e.linha((xa, Z_TERCA + B_TERCA), (xb, Z_TERCA + B_TERCA), "OCULTA"); e.linha((xa, Z_TERCA + H_TERCA - B_TERCA), (xb, Z_TERCA + H_TERCA - B_TERCA), "OCULTA")
    for z in Z_FURO:
        e.circulo((sg * (FOLGA + E_FURO), Z_TERCA + z), 7, "METALICA")
        e.circulo((sg * (FOLGA + E_FURO), Z_TERCA + z), 10.5, "METALICA")                         # cabeça/arruela
for z in Z_FURO:
    e.linha((-ST1["larg"] / 2, z + Z_TERCA), (ST1["larg"] / 2, z + Z_TERCA), "EIXO")
e.circulo((0, Z_DIAG), 9, "METALICA")
e.chamada((0, Z_DIAG), (-30, 20), "furo Ø18 a 255 (só nos ST-1 de borda): diagonal Ø16 — ver COB02")
e.cota_h([-ST1["larg"] / 2, -(FOLGA + E_FURO), -FOLGA, FOLGA, FOLGA + E_FURO, ST1["larg"] / 2], ST1["h"] + 10, 8, total=False)
e.cota_v([0, Z_TERCA + Z_FURO[0], Z_TERCA + Z_FURO[1], Z_TERCA + H_TERCA], -600, -10, total=False)
e.cota_v([0, ST1["h"]], 600, 10, total=False)
e.chamada((-ST1["larg"] / 2 + 10, 250), (-18, 12), f"ST-1 chapa {ST1['t']:g}×{ST1['larg']}×{ST1['h']} (A36) atrás das terças")
e.chamada((FOLGA + E_FURO, Z_TERCA + Z_FURO[1]), (40, 10), "2 M12 8.8 por terça, furo Ø14 na alma e no ST-1")
e.chamada((400, Z_TERCA + 40), (12, -16), "terça T-n+1 (alma na face do ST-1)")
e.chamada((-400, Z_TERCA + 40), (-12, -16), "terça T-n")
e.chamada((0, Z_TERCA / 2), (30, -22), f"folga {FOLGA} mm de cada ponta ao eixo do suporte ({2*FOLGA} entre terças); fundo {Z_TERCA} mm acima do concreto")
e.chamada((-IT1["ly"] / 2 + 20, -IT1["t"] / 2), (-14, -12), f"CH-T1 chapa {IT1['t']:g}×{IT1['lx']}×{IT1['ly']} nivelada no topo da viga")

# (b) CORTE — perpendicular à terça (plano x–z): seção U da terça, chapa ST-1 de lado, enrijecedor, CH-T1
c = pr.vista("CORTE A-A", (355, 200), E5, titulo="CORTE A-A", subtitulo="detalhe 1, perpendicular à terça; alma contra a face +x do ST-1")
c.ret(-250, -150, 500, 150, "CORTADO"); c.hachura([(-250, -150), (250, -150), (250, 0), (-250, 0)], "AR-CONC", 0.03)
c.chapa(-IT1["lx"] / 2, -IT1["t"], IT1["lx"], IT1["t"], 0.2)
for xp in (-50, 50):                                                                             # pinos Ø16 c/ cabeça (2 em vista)
    c.ret(xp - 8, -IT1["t"] - 100, 16, 100, "METALICA"); c.ret(xp - 14, -IT1["t"] - 110, 28, 10, "METALICA")
c.chapa(-ST1["t"], 0, ST1["t"], ST1["h"], 0.25)                                                  # ST-1 de lado (face +x em x=0)
c.poli([(-ST1["t"], 0), (-ST1["t"] - 90, 0), (-ST1["t"], 90)], "METALICA", True)                 # enrijecedor
c.hachura([(-ST1["t"], 0), (-ST1["t"] - 90, 0), (-ST1["t"], 90)], "ANSI31", 0.25, "METALICA")
zb = Z_TERCA
u = [(0, zb), (B_TERCA, zb), (B_TERCA, zb + 25), (B_TERCA - 3, zb + 25), (B_TERCA - 3, zb + 3), (3, zb + 3), (3, zb + H_TERCA - 3),
     (B_TERCA - 3, zb + H_TERCA - 3), (B_TERCA - 3, zb + H_TERCA - 25), (B_TERCA, zb + H_TERCA - 25), (B_TERCA, zb + H_TERCA), (0, zb + H_TERCA)]
c.poli(u, "METALICA", True); c.hachura(u, "SOLID", 1, "METALICA")
for z in Z_FURO:                                                                                  # parafusos em vista lateral
    c.ret(-ST1["t"] - 8, zb + z - 6, ST1["t"] + 3 + 8 + 10, 12, "METALICA"); c.ret(3, zb + z - 10, 10, 20, "METALICA")
c.linha((-ST1["t"], 0), (-ST1["t"] - 6, -6), "METALICA"); c.linha((0, 0), (6, -6), "METALICA")   # soldas
c.cota_h([-ST1["t"] - 90, -ST1["t"], 0, B_TERCA], -IT1["t"] - 120, -10, total=False)
c.cota_v([0, zb, zb + Z_FURO[0], zb + Z_FURO[1], zb + H_TERCA], B_TERCA + 20, 10, total=False)
c.chamada((-ST1["t"] - 45, 40), (-16, 14), "enrijecedor chapa 8 × 90 × 90, nos 2 lados do furo")
c.chamada((-ST1["t"] / 2, 200), (-14, 6), "solda ST-1 × CH-T1: filete 6 mm nos 2 lados (fábrica)")
c.chamada((B_TERCA - 3, zb + 150), (14, 10), "Ue 300×85×25×3,00")
c.chamada((50, -IT1["t"] - 100), (16, -12), "4 pinos Ø16 c/ cabeça, hef 100 (CH-T1)")
c.marcador_corte((-200, 330), (200, 330), "A", lado=-1)

# (c) PLANTA do suporte (x–y): CH-T1, ST-1, mesas das terças, folgas
p = pr.vista("DETALHE 1C", (485, 200), E5, titulo="DETALHE 1 — PLANTA", subtitulo="topo da viga TS-01; terças chegando de cada lado")
p.ret(-200, -300, 400, 600, "VISTA")                                                             # topo da viga (b 400)
p.chapa(-IT1["lx"] / 2, -IT1["ly"] / 2, IT1["lx"], IT1["ly"], 0.2)
p.chapa(-ST1["t"], -ST1["larg"] / 2, ST1["t"], ST1["larg"], 0.3)
for sg in (-1, 1):
    ya, yb = sg * FOLGA, sg * 300
    p.poli([(0, ya), (B_TERCA, ya), (B_TERCA, yb), (0, yb)], "METALICA", True)
    p.linha((3, ya), (3, yb), "OCULTA")
    p.circulo((0, sg * (FOLGA + E_FURO)), 7, "OCULTA")
p.poli([(-ST1["t"], -45), (-ST1["t"] - 90, -45), (-ST1["t"] - 90, 45), (-ST1["t"], 45)], "METALICA", True)
p.cota_v([-ST1["larg"] / 2, -(FOLGA + E_FURO), -FOLGA, FOLGA, FOLGA + E_FURO, ST1["larg"] / 2], B_TERCA + 20, 10, total=False)
p.cota_h([-200, -IT1["lx"] / 2, -ST1["t"], 0, B_TERCA, IT1["lx"] / 2, 200], -300, -10, total=False)
p.chamada((B_TERCA / 2, 250), (14, 10), "mesa da terça (85) — alma na face +x")
p.chamada((-ST1["t"] - 60, 0), (-12, 16), "ST-1 + enrijecedor")
p.chamada((-60, -80), (-10, -14), "CH-T1 200×200")

# ------------------------------------------------------------------ DETALHE 2 — MÃO-FRANCESA (1:10): CH-MF + OR-1 + MF-1 L 50×5
E10 = 12.5
d = pr.vista("DETALHE 2", (180, 58), E10, titulo="DETALHE 2 — MÃO-FRANCESA MF-1 NA ORELHA OR-1 (FUNDO DA VIGA)",
             subtitulo="plano da terça; OR-1 soldada no inserto CH-MF na fábrica, parafusada na montagem")
H = 900
pts = [(-200, 0), (200, 0), (200, 150), (75, 230), (75, 700), (200, 780), (200, 900), (-200, 900), (-200, 780), (-75, 700), (-75, 230), (-200, 150)]
d.poli(pts, "CORTADO", fechada=True); d.hachura(pts, "AR-CONC", 0.03)
d.chapa(-IT1["ly"] / 2, H - IT1["t"], IT1["ly"], IT1["t"], 0.2)                                   # CH-T1
d.chapa(-ST1["larg"] / 2, H, ST1["larg"], ST1["h"], 0.25)                                         # ST-1
d.chapa(-IM1["ly"] / 2, 0, IM1["ly"], IM1["t"], 0.2)                                              # CH-MF nivelado no fundo
d.chapa(-CHMF["l"] / 2, -CHMF["h"], CHMF["l"], CHMF["h"], 0.25)                                   # OR-1 pendurada
for sg in (1, -1):
    d.ret(sg * FOLGA if sg > 0 else -1250, H + Z_TERCA, 1240, H_TERCA, "METALICA")
    d.linha((sg * FOLGA, H + Z_TERCA + B_TERCA), (sg * 1250, H + Z_TERCA + B_TERCA), "OCULTA")
    d.circulo((sg * 100, -50), 7, "METALICA")                                                     # furo Ø14 na OR-1
    for z in Z_FURO:
        d.circulo((sg * (FOLGA + E_FURO), H + Z_TERCA + z), 7, "METALICA")
    xa, za = sg * 100, -50
    xb, zb2 = sg * Y_MF, H + Z_TERCA - 30
    L = math.hypot(xb - xa, zb2 - za); ux, uz = (xb - xa) / L, (zb2 - za) / L
    nx, nz = -uz * 50, ux * 50
    d.poli([(xa - ux * 40, za - uz * 40), (xb + ux * 40, zb2 + uz * 40), (xb + ux * 40 + nx * sg, zb2 + uz * 40 + nz * sg),
            (xa - ux * 40 + nx * sg, za - uz * 40 + nz * sg)], "METALICA", True)
    d.circulo((xb, zb2 + 30), 7, "METALICA")
d.cota_h([-Y_MF, -100, 0, 100, Y_MF], -CHMF["h"] - 20, -10, total=False)
d.cota_v([-CHMF["h"], 0, H, H + Z_TERCA, H + Z_TERCA + H_TERCA], -1250, -10, total=False)
d.cota_h([-CHMF["l"] / 2, -100, 100, CHMF["l"] / 2], -CHMF["h"], 8, total=False)
d.chamada((-700, 520), (-14, 10), f"MF-1 L 50×5 (A36) L = {f(mf['comp_m'],2)} m, a 45°")
d.chamada((100, -50), (36, 10), f"OR-1 chapa {CHMF['t']:g}×{CHMF['l']}×{CHMF['h']}: 2 furos Ø14 a 100 do eixo; M12 8.8")
d.chamada((-IM1["ly"] / 2 + 20, IM1["t"] / 2), (-16, 12), f"CH-MF chapa {IM1['t']:g}×{IM1['lx']}×{IM1['ly']} nivelada no fundo, 2 pinos Ø12,5 hef 80")
d.chamada((Y_MF, H + Z_TERCA), (10, -14), "M12 8.8 na mesa inferior da terça (furo Ø14)")
d.chamada((-80, H + 60), (-26, -16), "ST-1 / CH-T1 — ver DETALHE 1")

# ------------------------------------------------------------------ DETALHE 3 — SEÇÃO E FURAÇÃO DA TERÇA (1:5) + esquema da terça (1:20)
s5 = pr.vista("SEÇÃO DA TERÇA", (330, 48), E5, titulo="DETALHE 3 — TERÇA: SEÇÃO E FURAÇÃO", subtitulo="Ue 300×85×25×3,00 ZAR 345; furos centrados na alma")
u = [(B_TERCA, H_TERCA - 25), (B_TERCA, H_TERCA), (0, H_TERCA), (0, 0), (B_TERCA, 0), (B_TERCA, 25)]
s5.poli(u, "METALICA")
for z in Z_FURO:
    s5.circulo((0, z), 7, "METALICA")
s5.circulo((0, 150), 7, "OCULTA")
s5.circulo((42, 0), 7, "METALICA")
s5.cota_v([0, Z_FURO[0], 150, Z_FURO[1], H_TERCA], -10, -10, total=False)
s5.cota_h([0, 42, B_TERCA], H_TERCA, 8, total=False)
s5.chamada((0, Z_FURO[1]), (14, 12), "2 Ø14 nas pontas (ST-1), a 100 e 200 do fundo")
s5.chamada((0, 150), (16, -6), "Ø14 no meio da alma: correntes (L/4, L/2, 3L/4) — ver COB02")
s5.chamada((42, 0), (14, -18), "Ø14 na mesa inferior a 1070 do apoio: mão-francesa")

t20 = pr.vista("ESQUEMA DA TERÇA", (655, 200), 20, titulo="ESQUEMA DA TERÇA T-n", subtitulo="comprimento L = vão − 20; furos nas pontas e nas correntes")
LT = 1900
t20.ret(0, 0, 800, H_TERCA, "METALICA"); t20.ret(LT - 800, 0, 800, H_TERCA, "METALICA")
t20.interrupcao((800, 0), (LT - 800, 0), "METALICA"); t20.interrupcao((800, H_TERCA), (LT - 800, H_TERCA), "METALICA")
for x in (E_FURO, LT - E_FURO):
    for z in Z_FURO:
        t20.circulo((x, z), 7, "METALICA")
t20.circulo((500, 150), 7, "OCULTA"); t20.circulo((LT - 500, 150), 7, "OCULTA")
t20.cota_h([0, E_FURO, 500], 0, -10, total=False); t20.cota_h([LT - 500, LT - E_FURO, LT], 0, -10, total=False)
t20.cota_v([0, Z_FURO[0], Z_FURO[1], H_TERCA], 0, -10, total=False)
t20.texto((LT / 2, H_TERCA + 60), "L = vão − 20 (ver tabela)", "nota", "BOTTOM_CENTER")
t20.chamada((LT - 500, 150), (12, 12), "furos das correntes a L/4, L/2 e 3L/4 (não a 500)")

# ------------------------------------------------------------------ tabelas
x0, y = pr.quadro[2] - 196, pr.quadro[3] - 6
tabT = [[f"T-{k+1}", f"{k+1}–{k+2}", f"{VAOS[k]}", f"{L_TERCA[k]}", f"{N_T}", f"{N_T*L_TERCA[k]/1000*PESO_UE:,.0f}".replace(",", ".")]
        for k in range(8)]
tabT.append(["", "", "total", f"{sum(L_TERCA)*N_T/1000:,.0f} m".replace(",", "."), f"{8*N_T}", f"{sum(N_T*L/1000*PESO_UE for L in L_TERCA):,.0f}".replace(",", ".")])
y = pr.tabela(x0, y, f"TERÇAS Ue 300×85×25×3,00 ZAR 345 ({PESO_UE} kg/m)", ["MARCA", "EIXOS", "VÃO (mm)", "L (mm)", "QT", "kg"], tabT,
              [22, 24, 36, 36, 20, 52], destaque_ultima=True)
n_sup = N_LIN * N_T
n_m12_st = N_T * (7 * 4 + 2 * 2)
n_mf = N_T * (7 * 2 + 2)
lm = [["CH-T1", f"chapa {IT1['t']:g}×{IT1['lx']}×{IT1['ly']} A36 + 4 pinos Ø16 c/ cabeça hef 100", f"{n_sup - 7*14}", "topo da TS-01 (CH-T2 nos 7 nós do X)"],
      ["ST-1", f"chapa {ST1['t']:g}×{ST1['larg']}×{ST1['h']} A36 + 2 enrij. 8×90×90; 4 Ø14 (+1 Ø18 borda)", f"{n_sup}", "soldado na CH-T1/T2 (fábrica)"],
      ["CH-MF", f"chapa {IM1['t']:g}×{IM1['lx']}×{IM1['ly']} A36 + 2 pinos Ø12,5 c/ cabeça hef 80", f"{n_sup}", "fundo da TS-01, em cada terça"],
      ["OR-1", f"chapa {CHMF['t']:g}×{CHMF['l']}×{CHMF['h']} A36, 2 furos Ø14", f"{n_sup}", "soldada na CH-MF (fábrica)"],
      ["MF-1", f"L 50×5 A36 L = {f(mf['comp_m'],2)} m, 2 furos Ø14", f"{n_mf}", "parafusada na montagem"],
      ["M12 8.8", "parafuso + porca + 2 arruelas, zincado", f"{n_m12_st + 2 * n_mf}", f"{n_m12_st} no ST-1 + {2*n_mf} nas MF"]]
y = pr.tabela(x0, y - 4, "LISTA DE MATERIAIS — LIGAÇÕES TERÇA × VIGA", ["MARCA", "DESCRIÇÃO", "QT", "ONDE"], lm, [18, 106, 14, 58])
mem = [["Reação da terça (sucção)", f"{f(c1['reacao_suc_kN'],2)} kN por apoio", "—"],
       ["M12 na alma (corte / contato, t 3,0)", f"{f(c1['M12_alma']['Fd'],1)} ≤ {f(c1['M12_alma']['contato_alma_Rd'],1)} kN", f"{f(c1['M12_alma']['uso'],2)}"],
       ["Rasgamento da alma (furo a 60 da ponta)", f"{f(c1['rasgamento_alma']['Fd'],1)} ≤ {f(c1['rasgamento_alma']['Rd'],1)} kN", f"{f(c1['rasgamento_alma']['Fd']/c1['rasgamento_alma']['Rd'],2)}"],
       ["CH-T1 — pinos (tração × corte, ACI 318-19 cap. 17)", f"{f(CB['chumbadores']['CH-T1']['interacao'],2)} ≤ 1,2", f"{f(CB['chumbadores']['CH-T1']['interacao']/1.2,2)}"],
       ["CH-MF — pinos", f"{f(CB['chumbadores']['CH-MF']['interacao'],2)} ≤ 1,2", f"{f(CB['chumbadores']['CH-MF']['interacao']/1.2,2)}"],
       ["MF-1 L 50×5 (compressão, λ 131)", f"{f(mf['Nd_kN'],2)} ≤ {f(mf['NcRd'],1)} kN", f"{f(mf['uso'],2)}"]]
y = pr.tabela(x0, y - 4, "MEMÓRIA DAS LIGAÇÕES (NBR 14762:2010, NBR 8800:2008)", ["ITEM", "SOLICITAÇÃO × RESISTÊNCIA", "USO"], mem, [80, 90, 20])
notas = [f"Terças Ue 300×85×25×3,00 ZAR 345 galvanizadas, simplesmente apoiadas: comprimento L = vão entre eixos − {2*FOLGA} mm (folga de {FOLGA} mm de cada ponta ao eixo do suporte). Todas com a alma na face +x do ST-1.",
         f"Furos das pontas: 2 Ø14 a {E_FURO} mm da ponta, a {Z_FURO[0]} e {Z_FURO[1]} mm do fundo (centrados na alma). Furos das correntes Ø14 no meio da alma a L/4, L/2 e 3L/4; furo Ø14 na mesa inferior a {Y_MF} mm do eixo da viga para a mão-francesa. Tudo feito na fábrica; proibido furar na obra sem retoque com tinta rica em zinco.",
         "CH-T1 (CH-T2 nos nós do contraventamento) e CH-MF são os insertos embutidos na fôrma da TS-01 (ND-LET-TS01), nivelados com o concreto, nas 26 posições de terça de cada viga; o ST-1 e a OR-1 são soldados a eles na fábrica de pré-moldados, com gabarito, antes do transporte (filete 6 mm, eletrodo E7018). Conferir posição ±5 mm.",
         "Montagem: a terça é posicionada com o fundo 10 mm acima do concreto, parafusada com 2 M12 8.8 por ponta (aperto com chave, sem protensão). A reação passa pelos parafusos (corte + pressão de contato na alma).",
         "Mão-francesa MF-1 em toda terça, dos dois lados da viga nas linhas 2 a 8 e de um lado nas linhas 1 e 9: L 50×5 a 45°, M12 na OR-1 e M12 na mesa inferior da terça.",
         "Correntes, diagonais e contraventamento em X: ver ND-LET-COB02. Memória completa: ND-LET-MC02.",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(x0, y - 4, notas, 190)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-COB01")
for a in avisos:
    print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
