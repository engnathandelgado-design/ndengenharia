"""ND-LET-COB01 — cobertura metálica: planta de enterçamento e travamento de todo o pavilhão (terças com marcas, espaçamentos,
folgas, correntes, tirantes rígidos, diagonais de ancoragem, contraventamento em X e mãos-francesas) e ligações terça × viga:
suporte ST-1 soldado no inserto CH-T1, mão-francesa na alma da terça e na OR-1 soldada no inserto CH-MF, furação das terças.
Metálica em mm. A1. Padrão de apresentação: planta do banzo superior / planta da cobertura das referências do escritório.
"""
import math
from prancha_nd import Prancha
from cob_comum import (YLmm, VAOS, X_C, X_E, LTS, X0E, X0D, XT, PASSO, NOS, NOS_D, VAOS_X, FOLGA, E_FURO, Z_FURO, Z_COR,
                       Z_MF, Y_MF, Z_DIAG, Z_X, H_TERCA, B_TERCA, PESO_UE, IDX_2A, L_TERCA, BASE, lista_marcas, cabecalho, CB, f)

ST1 = dict(t=8, larg=220, h=290)         # suporte: chapa 8 × 220 (ao longo da terça) × 290 (altura acima do concreto)
IT1 = dict(t=12.5, lx=200, ly=200)       # CH-T1 no topo da viga
IM1 = dict(t=12.5, lx=150, ly=360)       # CH-MF no fundo da viga
CHMF = dict(t=8, l=300, h=100)           # OR-1
Z_TERCA = 10
N_LIN, N_T = 9, 26
pr = Prancha("A1", cabecalho("ND-LET-COB01", "04/05", "COBERTURA METÁLICA — PLANTA DE ENTERÇAMENTO E TRAVAMENTO, SUPORTE ST-1 E MÃO-FRANCESA"))
pr.revisao("01", pr.dados["data"], "furos centrados na alma; suporte ST-1 + CH-T1; mão-francesa na OR-1; planta completa")
pr.revisao("02", pr.dados["data"], "geometria do R01 (79,35 m; TS-01 19,15 m); X de nó a nó; correntes e MF no padrão de referência")
c1, mf = CB["CT1"], CB["MF1"]

# ------------------------------------------------------------------ PLANTA DE ENTERÇAMENTO E TRAVAMENTO 1:175 (papel: horizontal = y da obra)
ESC_P = 175
v = pr.vista("PLANTA", (72, 322), ESC_P, titulo="PLANTA DE ENTERÇAMENTO E TRAVAMENTO DA COBERTURA",
             subtitulo="terças Ue 300×85×25×3,00 ZAR 345 c/1554 (ao longo da água); caimento 3 % de A para E")
M = lambda y, x: (y, x)
for yl in YLmm:
    for x0 in (X0E, X0D):
        v.poli([M(yl - 200, x0), M(yl + 200, x0), M(yl + 200, x0 + LTS), M(yl - 200, x0 + LTS)], "VISTA", True)
    v.ret(yl - 300, X_C - 200, 600, 400, "CORTADO")
    v.ret(yl - 200, -300, 400, 600, "CORTADO"); v.ret(yl - 200, X_E - 300, 400, 600, "CORTADO")
for k in range(8):
    ya, yb = YLmm[k] + FOLGA, YLmm[k + 1] - FOLGA
    for x in XT:
        v.linha(M(ya, x), M(yb, x), "METALICA")
        v.linha(M(ya, x + B_TERCA), M(yb, x + B_TERCA), "METALICA")
# correntes, tirantes rígidos e diagonais de ancoragem (todas as meias águas, todos os vãos)
RUNS = [(0, 1, 12, 11), (13, 14, 25, 24)]
for k in range(8):
    ya, yb = YLmm[k], YLmm[k + 1]
    q = [ya + (yb - ya) * t for t in (0.25, 0.5, 0.75)]
    for (p0, p1, p12, p11) in RUNS:
        for yq in q:
            v.linha(M(yq, XT[p1]), M(yq, XT[p11]), "INDICACAO")                               # flexível
            v.linha(M(yq, XT[p0]), M(yq, XT[p1]), "METALICA"); v.linha(M(yq, XT[p11]), M(yq, XT[p12]), "METALICA")   # rígidos
        for (pa, pb) in ((p0, p1), (p12, p11)):
            for (yq, ys) in ((q[0], ya), (q[1] - 60, ya), (q[1] + 60, yb), (q[2], yb)):
                v.linha(M(yq, XT[pb]), M(ys, XT[pa]), "OCULTA")
    if k in VAOS_X:
        for nos in (NOS, NOS_D):
            for a, b in zip(nos[:-1], nos[1:]):
                v.linha(M(ya + 140, a + 140), M(yb - 140, b - 140), "ARMADURA")
                v.linha(M(ya + 140, b - 140), M(yb - 140, a + 140), "ARMADURA")
# MF em cada apoio de terça (dois lados da viga)
for i, yl in enumerate(YLmm):
    for x in XT:
        for sg in ((1,) if i == 0 else (-1,) if i == 8 else (-1, 1)):
            v.texto(M(yl + sg * 700, x + 200), "MF", "min", "MIDDLE_CENTER")
# eixos e marcas
for i, yl in enumerate(YLmm):
    v.eixo(M(yl, -900), M(yl, X_E + 900), 0)
    xp, yp = v.P(M(yl, X_E + 1900))
    pr.msp.add_circle((xp, yp), 3.2, dxfattribs={"layer": "INDICACAO"})
    pr.texto(xp, yp, str(i + 1), "sub", "TITULO", "MIDDLE_CENTER")
for lbl, x in (("A", 0), ("C", X_C), ("E", X_E)):
    v.eixo(M(-900, x), M(YLmm[-1] + 900, x), 0)
    xp, yp = v.P(M(-1900, x))
    pr.msp.add_circle((xp, yp), 3.2, dxfattribs={"layer": "INDICACAO"})
    pr.texto(xp, yp, lbl, "sub", "TITULO", "MIDDLE_CENTER")
for k in range(8):
    ym = (YLmm[k] + YLmm[k + 1]) / 2
    for x in (XT[6] + 700, XT[19] + 700):
        xp, yp = v.P(M(ym + 1800, x))
        pr.msp.add_circle((xp, yp), 4.0, dxfattribs={"layer": "INDICACAO"})
        pr.texto(xp, yp, BASE[L_TERCA[k]], "nota", "TITULO", "MIDDLE_CENTER")
    v.texto(M(ym - 1800, XT[8] + 500), f"L = {L_TERCA[k]}", "min", "MIDDLE_CENTER", rot=90)
    v.texto(M(ym - 1800, XT[21] + 500), f"L = {L_TERCA[k]}", "min", "MIDDLE_CENTER", rot=90)
v.cota_h(YLmm, -900, -10, total=False)
v.cota_h([YLmm[0], YLmm[-1]], X_E + 1900, 10, total=False)
v.cota_v(XT[:13], YLmm[0] - 900, -12, total=False)
v.cota_v([325, X0E + LTS], YLmm[0] - 900, -24, total=False)
v.cota_v(XT[13:], YLmm[0] - 900, -12, total=False)
v.cota_v([X0D, X0D + LTS], YLmm[0] - 900, -24, total=False)
v.cota_v([0, X_C, X_E], YLmm[0] - 900, -36, total=False)
RX = YLmm[8] - 300
v.chamada(M(YLmm[8] - 2500, XT[24] + 40), (16, 8), "terça Ue 300×85×25×3,00 (alma na face +x do ST-1)")
v.chamada(M(YLmm[7] + VAOS[7] * 0.75, (XT[18] + XT[19]) / 2), (18, 4), "corrente flexível Ø12,5 (L/4, L/2, 3L/4)")
v.chamada(M(YLmm[7] + VAOS[7] * 0.75, (XT[0] + XT[1]) / 2), (14, -14), "tirante rígido L 51×51×3,2 no 1º espaço")
v.chamada(M(YLmm[7] + VAOS[7] * 0.15, (XT[24] + XT[25]) / 2), (24, 12), "diagonal de ancoragem Ø16")
_ym = (YLmm[6] + YLmm[7]) / 2
v.chamada(M(_ym, (NOS_D[4] + NOS_D[5]) / 2), (66, -6), "X Ø16 c/ esticador, de nó a nó das vigas")
v.chamada(M(YLmm[8] - 700, XT[14] + 200), (16, -6), "MF = mão-francesa (det. 2)")
v.chamada(M(YLmm[8] - 200, X_C), (16, -8), "pilar central / I110 (eixo C)")
v.marcador_detalhe(M(YLmm[5], XT[20]), 600, 1, ang=60, dist=8)
v.marcador_detalhe(M(YLmm[6] + Y_MF, XT[22]), 500, 2, ang=-50, dist=8)

# ------------------------------------------------------------------ DETALHE 1 — SUPORTE DE TERÇA ST-1 (1:5): elevação, corte, planta
E5 = 5
e = pr.vista("DETALHE 1A", (165, 200), E5, titulo="DETALHE 1 — SUPORTE DE TERÇA ST-1 — ELEVAÇÃO",
             subtitulo="vista no plano da terça (ao longo da viga); terças nas pontas")
e.ret(-600, -150, 1200, 150, "CORTADO"); e.hachura([(-600, -150), (600, -150), (600, 0), (-600, 0)], "AR-CONC", 0.03)
e.chapa(-IT1["ly"] / 2, -IT1["t"], IT1["ly"], IT1["t"], 0.2)
e.ret(-ST1["larg"] / 2, 0, ST1["larg"], ST1["h"], "OCULTA")
e.hachura([(-FOLGA, 0), (FOLGA, 0), (FOLGA, ST1["h"]), (-FOLGA, ST1["h"])], "ANSI31", 0.25, "METALICA")
for sg in (-1, 1):
    xa, xb = sg * FOLGA, sg * 600
    e.poli([(xa, Z_TERCA), (xb, Z_TERCA), (xb, Z_TERCA + H_TERCA), (xa, Z_TERCA + H_TERCA)], "METALICA", True)
    e.linha((xa, Z_TERCA + B_TERCA), (xb, Z_TERCA + B_TERCA), "OCULTA"); e.linha((xa, Z_TERCA + H_TERCA - B_TERCA), (xb, Z_TERCA + H_TERCA - B_TERCA), "OCULTA")
    for z in Z_FURO:
        e.circulo((sg * (FOLGA + E_FURO), Z_TERCA + z), 7, "METALICA")
        e.circulo((sg * (FOLGA + E_FURO), Z_TERCA + z), 10.5, "METALICA")
for z in Z_FURO:
    e.linha((-ST1["larg"] / 2, z + Z_TERCA), (ST1["larg"] / 2, z + Z_TERCA), "EIXO")
e.circulo((0, Z_DIAG + Z_TERCA), 9, "METALICA")
e.chamada((0, Z_DIAG + Z_TERCA), (16, 34), "furo Ø18 (ST-1 das pontas): diagonal Ø16")
e.cota_h([-ST1["larg"] / 2, -(FOLGA + E_FURO), -FOLGA, FOLGA, FOLGA + E_FURO, ST1["larg"] / 2], Z_TERCA + H_TERCA + 30, 8, total=False)
e.ret(-600, Z_TERCA + H_TERCA, 1200, 30, "METALICA")
e.cota_v([0, Z_TERCA + Z_FURO[0], Z_TERCA + Z_FURO[1], Z_TERCA + H_TERCA, Z_TERCA + H_TERCA + 30], -600, -10, total=False)
e.cota_v([0, ST1["h"]], 600, 10, total=False)
e.chamada((-ST1["larg"] / 2 + 10, 250), (-18, 12), f"ST-1 chapa {ST1['t']:g}×{ST1['larg']}×{ST1['h']} (A36) atrás das terças")
e.chamada((FOLGA + E_FURO, Z_TERCA + Z_FURO[1]), (40, 10), "2 M12 8.8 por terça, furo Ø14 na alma e no ST-1")
e.chamada((400, Z_TERCA + 40), (12, -16), "terça da direita (alma na face do ST-1)")
e.chamada((-400, Z_TERCA + 40), (-12, -16), "terça da esquerda")
e.chamada((0, Z_TERCA / 2), (30, -22), f"folga {FOLGA} mm de cada ponta ao eixo do suporte ({2*FOLGA} entre terças); fundo {Z_TERCA} mm acima do concreto")
e.chamada((-IT1["ly"] / 2 + 20, -IT1["t"] / 2), (-14, -12), f"CH-T1 chapa {IT1['t']:g}×{IT1['lx']}×{IT1['ly']} nivelada no topo da viga")

c = pr.vista("CORTE A-A", (355, 200), E5, titulo="CORTE A-A", subtitulo="detalhe 1, perpendicular à terça; alma contra a face +x do ST-1")
c.ret(-250, -150, 500, 150, "CORTADO"); c.hachura([(-250, -150), (250, -150), (250, 0), (-250, 0)], "AR-CONC", 0.03)
c.chapa(-IT1["lx"] / 2, -IT1["t"], IT1["lx"], IT1["t"], 0.2)
for xp in (-50, 50):
    c.ret(xp - 8, -IT1["t"] - 100, 16, 100, "METALICA"); c.ret(xp - 14, -IT1["t"] - 110, 28, 10, "METALICA")
c.chapa(-ST1["t"], 0, ST1["t"], ST1["h"], 0.25)
c.poli([(-ST1["t"], 0), (-ST1["t"] - 90, 0), (-ST1["t"], 90)], "METALICA", True)
c.hachura([(-ST1["t"], 0), (-ST1["t"] - 90, 0), (-ST1["t"], 90)], "ANSI31", 0.25, "METALICA")
zb = Z_TERCA
u = [(0, zb), (B_TERCA, zb), (B_TERCA, zb + 25), (B_TERCA - 3, zb + 25), (B_TERCA - 3, zb + 3), (3, zb + 3), (3, zb + H_TERCA - 3),
     (B_TERCA - 3, zb + H_TERCA - 3), (B_TERCA - 3, zb + H_TERCA - 25), (B_TERCA, zb + H_TERCA - 25), (B_TERCA, zb + H_TERCA), (0, zb + H_TERCA)]
c.poli(u, "METALICA", True); c.hachura(u, "SOLID", 1, "METALICA")
for z in Z_FURO:
    c.ret(-ST1["t"] - 8, zb + z - 6, ST1["t"] + 3 + 8 + 10, 12, "METALICA"); c.ret(3, zb + z - 10, 10, 20, "METALICA")
c.linha((-ST1["t"], 0), (-ST1["t"] - 6, -6), "METALICA"); c.linha((0, 0), (6, -6), "METALICA")
c.cota_h([-ST1["t"] - 90, 0, B_TERCA], -IT1["t"] - 120, -10, total=False)
c.cota_v([0, zb, zb + Z_FURO[0], zb + Z_FURO[1], zb + H_TERCA], B_TERCA + 20, 10, total=False)
c.chamada((-ST1["t"] - 45, 40), (-16, 14), "enrijecedor chapa 8 × 90 × 90, nos 2 lados do furo")
c.chamada((-ST1["t"] / 2, 200), (-14, 6), "solda ST-1 × CH-T1: filete 6 mm nos 2 lados (fábrica)")
c.chamada((B_TERCA - 3, zb + 150), (14, 10), "Ue 300×85×25×3,00")
c.chamada((50, -IT1["t"] - 100), (16, -12), "4 pinos Ø16 c/ cabeça, hef 100 (CH-T1)")
c.ret(-250, zb + H_TERCA, 500, 30, "METALICA"); c.hachura([(-250, zb + H_TERCA), (250, zb + H_TERCA), (250, zb + H_TERCA + 30), (-250, zb + H_TERCA + 30)], "ANSI37", 0.5, "METALICA")
c.linha((60, zb + H_TERCA + 30), (60, zb + H_TERCA - 15), "METALICA")
c.chamada((200, zb + H_TERCA + 15), (12, 3), "telha sanduíche PIR 30 mm (aço 0,5/0,5), parafuso autobrocante 12-14×2" + chr(34) + " c/ EPDM na mesa superior")
c.marcador_corte((-200, 430), (200, 430), "A", lado=-1)

p = pr.vista("DETALHE 1C", (485, 200), E5, titulo="DETALHE 1 — PLANTA", subtitulo="topo da viga TS-01; terças chegando de cada lado")
p.ret(-200, -300, 400, 600, "VISTA")
p.chapa(-IT1["lx"] / 2, -IT1["ly"] / 2, IT1["lx"], IT1["ly"], 0.2)
p.chapa(-ST1["t"], -ST1["larg"] / 2, ST1["t"], ST1["larg"], 0.3)
for sg in (-1, 1):
    ya, yb = sg * FOLGA, sg * 300
    p.poli([(0, ya), (B_TERCA, ya), (B_TERCA, yb), (0, yb)], "METALICA", True)
    p.linha((3, ya), (3, yb), "OCULTA")
    p.circulo((0, sg * (FOLGA + E_FURO)), 7, "OCULTA")
p.poli([(-ST1["t"], -45), (-ST1["t"] - 90, -45), (-ST1["t"] - 90, 45), (-ST1["t"], 45)], "METALICA", True)
p.cota_v([-ST1["larg"] / 2, -(FOLGA + E_FURO), -FOLGA, FOLGA, FOLGA + E_FURO, ST1["larg"] / 2], B_TERCA + 20, 10, total=False)
p.cota_h([-200, -IT1["lx"] / 2, 0, B_TERCA, IT1["lx"] / 2, 200], -300, -10, total=False)
p.chamada((B_TERCA / 2, 250), (14, 10), "mesa da terça (85) — alma na face +x")
p.chamada((-ST1["t"] - 60, 0), (-12, 16), "ST-1 + enrijecedor")
p.chamada((-60, -80), (-10, -14), "CH-T1 200×200")

# ------------------------------------------------------------------ DETALHE 2 — MÃO-FRANCESA (1:12,5) + CORTE B-B (1:5)
E10 = 12.5
d = pr.vista("DETALHE 2", (180, 58), E10, titulo="DETALHE 2 — MÃO-FRANCESA MF-1",
             subtitulo="plano da alma da terça; MF parafusada na OR-1 (fundo da viga) e na alma da terça, dos dois lados")
H = 900
pts = [(-200, 0), (200, 0), (200, 150), (75, 230), (75, 700), (200, 780), (200, 900), (-200, 900), (-200, 780), (-75, 700), (-75, 230), (-200, 150)]
d.poli(pts, "CORTADO", fechada=True); d.hachura(pts, "AR-CONC", 0.03)
d.chapa(-IT1["ly"] / 2, H - IT1["t"], IT1["ly"], IT1["t"], 0.2)
d.chapa(-ST1["larg"] / 2, H, ST1["larg"], ST1["h"], 0.25)
d.chapa(-IM1["ly"] / 2, 0, IM1["ly"], IM1["t"], 0.2)
d.chapa(-CHMF["l"] / 2, -CHMF["h"], CHMF["l"], CHMF["h"], 0.25)
for sg in (1, -1):
    d.ret(sg * FOLGA if sg > 0 else -1450, H + Z_TERCA, 1440, H_TERCA, "METALICA")
    d.linha((sg * FOLGA, H + Z_TERCA + B_TERCA), (sg * 1450, H + Z_TERCA + B_TERCA), "OCULTA")
    xa, za = sg * 100, -50
    xb, zb2 = sg * Y_MF, H + Z_TERCA + Z_MF
    L = math.hypot(xb - xa, zb2 - za); ux, uz = (xb - xa) / L, (zb2 - za) / L
    nx, nz = -uz * 50, ux * 50
    d.poli([(xa - ux * 40, za - uz * 40), (xb + ux * 40, zb2 + uz * 40), (xb + ux * 40 - nx * sg, zb2 + uz * 40 - nz * sg),
            (xa - ux * 40 - nx * sg, za - uz * 40 - nz * sg)], "METALICA", True)
    d.circulo((xa, za), 7, "METALICA"); d.circulo((xb, zb2), 7, "METALICA")
d.cota_h([-Y_MF, -100, 0, 100, Y_MF], -CHMF["h"] - 20, -10, total=False)
d.cota_v([-CHMF["h"], -50, 0, H, H + Z_TERCA + Z_MF, H + Z_TERCA + H_TERCA], -1450, -10, total=False)
d.chamada((-650, 470), (-14, 10), f"MF-1 L 50×5 (A36) L = {f(mf['comp_m'],2)} m entre furos, a 45°")
d.chamada((100, -50), (36, 8), f"OR-1 {CHMF['t']:g}×{CHMF['l']}×{CHMF['h']}: 2 Ø14 a ±100; M12 8.8")
d.chamada((-IM1["ly"] / 2 + 20, IM1["t"] / 2), (-16, 12), f"CH-MF chapa {IM1['t']:g}×{IM1['lx']}×{IM1['ly']} nivelada no fundo, 2 pinos Ø12,5 hef 80")
d.chamada((Y_MF, H + Z_TERCA + Z_MF), (10, -14), f"M12 8.8 na alma da terça: furo Ø14 a {Z_MF} do fundo")
d.chamada((-80, H + 60), (-26, -16), "ST-1 / CH-T1 — ver DETALHE 1")
d.marcador_corte((-160, -110), (-160, 120), "B", lado=1)

bb = pr.vista("CORTE B-B", (392, 118), E5, titulo="CORTE B-B", subtitulo="plano da MF")
bb.ret(-200, -60, 400, 60, "CORTADO"); bb.hachura([(-200, -60), (200, -60), (200, 0), (-200, 0)], "AR-CONC", 0.03)
bb.chapa(-75, 0, 150, IM1["t"], 0.2)                                           # CH-MF (fundo da viga, invertido no desenho: concreto acima)
bb.chapa(-13, -CHMF["h"] + IM1["t"] - 60, 8, CHMF["h"], 0.25)                  # OR-1 (face +x a −5)
bb.ret(-5, -CHMF["h"] + IM1["t"] - 60, 5, 60, "METALICA"); bb.ret(-5, -CHMF["h"] + IM1["t"] - 60, -45, 5, "METALICA")   # aba e aba saliente da MF
bb.ret(-30, -CHMF["h"] + IM1["t"] - 18, 36, 12, "METALICA")                   # parafuso M12
bb.cota_h([-13, 0], -CHMF["h"] + IM1["t"] - 60, -10, total=False)
bb.texto((0, 40), "fundo da TS-01 (concreto)", "min", "BOTTOM_CENTER")
bb.chamada((-9, -CHMF["h"] + IM1["t"] - 20), (-10, -8), "OR-1 a 5 mm da alma")
bb.chamada((-2, -CHMF["h"] + IM1["t"] - 50), (10, -8), "aba da MF L 50×5")

# ------------------------------------------------------------------ DETALHE 3 — SEÇÃO E FURAÇÃO DA TERÇA (1:5) + esquema por marca (sem escala no comprimento)
s5 = pr.vista("SEÇÃO DA TERÇA", (455, 48), E5, titulo="DETALHE 3 — TERÇA: SEÇÃO E FURAÇÃO", subtitulo="Ue 300×85×25×3,00 ZAR 345; furos na alma")
u = [(B_TERCA, H_TERCA - 25), (B_TERCA, H_TERCA), (0, H_TERCA), (0, 0), (B_TERCA, 0), (B_TERCA, 25)]
s5.poli(u, "METALICA")
for z, cam in ((Z_FURO[0], "METALICA"), (Z_FURO[1], "METALICA"), (Z_COR, "OCULTA"), (Z_MF, "OCULTA"), (Z_DIAG, "OCULTA"), (Z_X[0], "OCULTA"), (Z_X[1], "OCULTA")):
    s5.circulo((0, z), 7 if z in (Z_FURO + (Z_COR, Z_MF)) else 9, cam)
s5.cota_v([0, Z_X[0], Z_X[1], Z_COR, Z_DIAG, H_TERCA], -10, -10, total=False)
s5.cota_v([0, Z_MF, Z_FURO[0], Z_FURO[1], H_TERCA], B_TERCA, 10, total=False)
s5.chamada((0, Z_FURO[1]), (30, 6), "pontas: 2 Ø14 a 100 e 200")
s5.chamada((0, Z_COR), (30, 6), "correntes Ø14")
s5.chamada((0, Z_DIAG), (30, 4), "diagonal Ø18 (marcas D)")
s5.chamada((0, Z_X[1]), (30, -4), "cruzamento do X 2 Ø18 (marcas X)")
s5.chamada((0, Z_MF), (30, -14), "mão-francesa Ø14")

t20 = pr.vista("ESQUEMA DA TERÇA", (650, 215), 20, titulo="ESQUEMA DE FURAÇÃO DAS TERÇAS", subtitulo="cotas a partir da ponta; L, L/4… pela tabela de marcas")
LT = 1900
t20.ret(0, 0, 800, H_TERCA, "METALICA"); t20.ret(LT - 800, 0, 800, H_TERCA, "METALICA")
t20.interrupcao((800, 0), (LT - 800, 0), "METALICA"); t20.interrupcao((800, H_TERCA), (LT - 800, H_TERCA), "METALICA")
for x in (E_FURO, LT - E_FURO):
    for z in Z_FURO:
        t20.circulo((x, z), 7, "METALICA")
for x in (Y_MF - FOLGA, LT - Y_MF + FOLGA):
    t20.circulo((x, Z_MF), 7, "METALICA")
t20.circulo((560, Z_COR), 7, "METALICA"); t20.circulo((560, Z_DIAG), 9, "METALICA")
t20.cota_h([0, E_FURO, 560, Y_MF - FOLGA], 0, -10, total=False); t20.cota_h([LT - Y_MF + FOLGA, LT - E_FURO, LT], 0, -10, total=False)
t20.texto((LT / 2, H_TERCA + 60), "L (ver tabela)", "nota", "BOTTOM_CENTER")
t20.chamada((560, Z_COR), (8, 18), "correntes a a/4−10, a/2−10, 3a/4−10")
t20.chamada((Y_MF - FOLGA, Z_MF), (-4, -20), f"MF a {Y_MF - FOLGA} das 2 pontas")

# ------------------------------------------------------------------ tabelas
x0, y = pr.quadro[2] - 196, pr.quadro[3] - 6
LM = lista_marcas()
tabT = []
for m_, dd in LM.items():
    fur = "pontas, correntes, MF" + (" + diag. Ø18" if "D" in m_[2:] else "") + (" + X 2 Ø18" if "X" in m_[2:] else "")
    tabT.append([m_, f"{dd['L']}", ", ".join(sorted(dd["vaos"])), fur, f"{dd['qt']}", f"{dd['qt']*dd['L']/1000*PESO_UE:,.0f}".replace(",", ".")])
qt_t = sum(dd["qt"] for dd in LM.values())
kg_t = sum(dd["qt"] * dd["L"] / 1000 * PESO_UE for dd in LM.values())
tabT.append(["", "", "", "total", f"{qt_t}", f"{kg_t:,.0f}".replace(",", ".")])
y = pr.tabela(x0, y, f"TERÇAS Ue 300×85×25×3,00 ZAR 345 ({PESO_UE} kg/m) — L = vão − 20", ["MARCA", "L (mm)", "VÃOS", "FURAÇÃO", "QT", "kg"], tabT,
              [16, 16, 30, 98, 14, 22], destaque_ultima=True)
n_sup = N_LIN * N_T
n_m12_st = N_T * (7 * 4 + 2 * 2)
n_mf = N_T * (7 * 2 + 2)
lm = [["CH-T1", f"chapa {IT1['t']:g}×{IT1['lx']}×{IT1['ly']} A36 + 4 pinos Ø16 c/ cabeça hef 100", f"{7*2*6}", "topo da TS-01 (CH-T2 nos 7 nós)"],
      ["ST-1", f"chapa {ST1['t']:g}×{ST1['larg']}×{ST1['h']} A36 + 2 enrij. 8×90×90; 4 Ø14 (+1 Ø18 nas pontas)", f"{n_sup}", "soldado na CH-T1/T2 (fábrica)"],
      ["CH-MF", f"chapa {IM1['t']:g}×{IM1['lx']}×{IM1['ly']} A36 + 2 pinos Ø12,5 c/ cabeça hef 80", f"{7*2*13}", "fundo da TS-01, em cada terça"],
      ["OR-1", f"chapa {CHMF['t']:g}×{CHMF['l']}×{CHMF['h']} A36, 2 furos Ø14", f"{n_sup}", "soldada na CH-MF (fábrica)"],
      ["MF-1", f"L 50×5 A36, {f(mf['comp_m'],2)} m entre furos, 2 furos Ø14", f"{n_mf}", "parafusada na montagem"],
      ["M12 8.8", "parafuso + porca + 2 arruelas, zincado", f"{n_m12_st + 2 * n_mf}", f"{n_m12_st} no ST-1 + {2*n_mf} nas MF"]]
y = pr.tabela(x0, y - 4, "LISTA DE MATERIAIS — LIGAÇÕES TERÇA × VIGA", ["MARCA", "DESCRIÇÃO", "QT", "ONDE"], lm, [18, 106, 14, 58])
notas = [f"Terças simplesmente apoiadas de viga a viga: L = vão entre eixos − {2*FOLGA} mm (folga de {FOLGA} mm de cada ponta ao eixo do suporte). Todas com a alma na face +x do ST-1. Marca = comprimento (T1..T5) + furação: D = 2ª terça das pontas de meia água (diagonais de ancoragem), X = terça intermediária dos painéis do contraventamento. Furos: diag. Ø18 em a/4, a/2 ± 60 e 3a/4; X 2 Ø18 em a/2 (esquema de furação).",
         "Furação toda de fábrica (d + 2 mm): proibido furar a terça galvanizada na obra sem retoque com tinta rica em zinco.",
         "CH-T1 (CH-T2 nos nós do X) e CH-MF são os insertos embutidos na fôrma da TS-01 (ND-LET-TS01); o ST-1 e a OR-1 são soldados a eles na fábrica de pré-moldados, com gabarito, antes do transporte (filete 6 mm, E7018). Conferir posição ±5 mm.",
         "Montagem: terça com o fundo 10 mm acima do concreto, 2 M12 8.8 por ponta (aperto com chave). Depois as MF (M12 na OR-1 e na alma da terça), depois correntes, tirantes rígidos e diagonais; por último o X, tensionado no esticador até tirar a flecha da barra.",
         "Mão-francesa MF-1 em toda terça, dos dois lados da viga nas linhas 2 a 8 e de um lado nas linhas 1 e 9: L 50×5 a 45°, com a aba encostada na alma da terça e na OR-1 (mesmo plano).",
         "Telha sanduíche PIR 30 mm (aço 0,5/0,5) na mesa superior com autobrocante 12-14×2\" c/ EPDM, 2 por apoio; costura lateral c/ 500.",
         "Correntes, tirantes rígidos, diagonais e X: detalhes na ND-LET-COB02. Memória: ND-LET-MC02.",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(x0, y - 4, notas, 190)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-COB01")
for a in avisos:
    print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
