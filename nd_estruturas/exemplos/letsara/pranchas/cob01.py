"""ND-LET-COB01 — cobertura metálica: planta de enterçamento e travamento de todo o pavilhão (terças com marcas, espaçamentos,
folgas, correntes, tirantes rígidos, diagonais de ancoragem, contraventamento em X e mãos-francesas) e ligações terça × viga,
todas parafusadas (rev03, sem solda): suporte ST-1P (chapa dobrada) nas esperas ES-1 da TS-01, mão-francesa MF-1 no clipe
CMF-1 da espera lateral ES-3 e na alma da terça; furação das terças.
Metálica em mm. A1. Padrão de apresentação: planta do banzo superior / planta da cobertura das referências do escritório.
"""
import math
from prancha_nd import Prancha
from cob_comum import (YLmm, VAOS, X_C, X_E, LTS, X0E, X0D, XT, PASSO, NOS, NOS_D, VAOS_X, FOLGA, E_FURO, Z_FURO, Z_COR,
                       Z_MF, Y_MF, Z_DIAG, Z_X, H_TERCA, B_TERCA, PESO_UE, IDX_2A, L_TERCA, BASE, NT, lista_marcas, cabecalho, CB, LG, f)

ST1 = dict(t=9.5, larg=220, h=290, aba=150)   # ST-1P: chapa dobrada 9,5 × 220 (ao longo da terça); aba vertical 290, horizontal 150
Z_TERCA = 10
N_LIN, N_T = 9, 2 * NT
pr = Prancha("A0", cabecalho("ND-LET-COB01", "04/05", "COBERTURA METÁLICA — PLANTA DE ENTERÇAMENTO E TRAVAMENTO, SUPORTE ST-1P E MÃO-FRANCESA"))
pr.revisao("01", pr.dados["data"], "furos centrados na alma; suporte ST-1 + CH-T1; mão-francesa na OR-1; planta completa")
pr.revisao("02", pr.dados["data"], "geometria do R01 (79,35 m; TS-01 19,15 m); X de nó a nó; correntes e MF no padrão de referência")
pr.revisao("03", "14/10/2026", "TERÇAS c/1,20 m Ue 300×2,65; PACOTE TP40 + LÃ 40 + ZIPADA + PAINÉIS; ST-1P E MF PARAFUSADOS (SEM SOLDA)")
st, mf, chb = CB["ST1P"], CB["MF1"], CB["chumbadores"]

# ------------------------------------------------------------------ PLANTA DE ENTERÇAMENTO E TRAVAMENTO 1:175 (papel: horizontal = y da obra)
ESC_P = 175
v = pr.vista("PLANTA", (72, 560), ESC_P, titulo="PLANTA DE ENTERÇAMENTO E TRAVAMENTO DA COBERTURA",
             subtitulo=f"terças Ue 300×85×25×2,65 ZAR 345 c/{PASSO} (ao longo da água); caimento 3 % de A para E")
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
RUNS = [(0, 1, NT - 1, NT - 2), (NT, NT + 1, 2 * NT - 1, 2 * NT - 2)]
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
    for x in (XT[NT // 2 - 1] + 700, XT[NT + NT // 2 - 1] + 700):
        xp, yp = v.P(M(ym + 1800, x))
        pr.msp.add_circle((xp, yp), 4.0, dxfattribs={"layer": "INDICACAO"})
        pr.texto(xp, yp, BASE[L_TERCA[k]], "nota", "TITULO", "MIDDLE_CENTER")
    v.texto(M(ym - 1800, XT[NT // 2 + 1] + 500), f"L = {L_TERCA[k]}", "min", "MIDDLE_CENTER", rot=90)
    v.texto(M(ym - 1800, XT[NT + NT // 2 + 1] + 500), f"L = {L_TERCA[k]}", "min", "MIDDLE_CENTER", rot=90)
v.cota_h(YLmm, -900, -10, total=False)
v.cota_h([YLmm[0], YLmm[-1]], X_E + 1900, 10, total=False)
v.cota_v(XT[:NT], YLmm[0] - 900, -12, total=False)
v.cota_v([X0E, X0E + LTS], YLmm[0] - 900, -24, total=False)
v.cota_v(XT[NT:], YLmm[0] - 900, -12, total=False)
v.cota_v([X0D, X0D + LTS], YLmm[0] - 900, -24, total=False)
v.cota_v([0, X_C, X_E], YLmm[0] - 900, -36, total=False)
RX = YLmm[8] - 300
v.chamada(M(YLmm[8] - 2500, XT[2 * NT - 2] + 40), (16, 8), "terça Ue 300×85×25×2,65 (alma na face +x do ST-1P)")
v.chamada(M(YLmm[7] + VAOS[7] * 0.75, (XT[NT + 5] + XT[NT + 6]) / 2), (18, 4), "corrente flexível Ø10 (L/4, L/2, 3L/4)")
v.chamada(M(YLmm[7] + VAOS[7] * 0.75, (XT[0] + XT[1]) / 2), (14, -14), "tirante rígido L 51×51×3,2 no 1º espaço")
v.chamada(M(YLmm[7] + VAOS[7] * 0.15, (XT[2 * NT - 2] + XT[2 * NT - 1]) / 2), (24, 12), "diagonal de ancoragem Ø16")
_ym = (YLmm[6] + YLmm[7]) / 2
v.chamada(M(_ym, (NOS_D[4] + NOS_D[5]) / 2), (66, -6), "X Ø16 c/ esticador (vãos 2-3 e 7-8)")
v.chamada(M(YLmm[8] - 700, XT[NT + 1] + 200), (16, -6), "MF = mão-francesa (det. 2)")
v.chamada(M(YLmm[8] - 200, X_C), (16, -8), "pilar central / I130 (eixo C)")
v.marcador_detalhe(M(YLmm[5], XT[NT + 8]), 600, 1, ang=60, dist=8)
v.marcador_detalhe(M(YLmm[6] + Y_MF, XT[NT + 11]), 500, 2, ang=-50, dist=8)

# ------------------------------------------------------------------ DETALHE 1 — SUPORTE DE TERÇA ST-1P (1:5): elevação, corte, planta
E5 = 5
e = pr.vista("DETALHE 1A", (175, 390), E5, titulo="DETALHE 1 — SUPORTE DE TERÇA ST-1P — ELEVAÇÃO",
             subtitulo="vista no plano da alma da terça (perpendicular à viga); terças topo a topo")
e.ret(-600, -150, 1200, 150, "CORTADO"); e.hachura([(-600, -150), (600, -150), (600, 0), (-600, 0)], "AR-CONC", 0.03)
for yy in (-60, 60):                                                      # ES-1 (atrás da aba vertical)
    e.ret(yy - 8, -150, 16, 270, "OCULTA")
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
e.chamada((0, Z_DIAG + Z_TERCA), (16, 34), "furo Ø18 (ST-1P das pontas): diagonal Ø16")
e.cota_h([-ST1["larg"] / 2, -(FOLGA + E_FURO), -FOLGA, FOLGA, FOLGA + E_FURO, ST1["larg"] / 2], Z_TERCA + H_TERCA + 30, 8, total=False)
e.cota_v([0, Z_TERCA + Z_FURO[0], Z_TERCA + Z_FURO[1], Z_TERCA + H_TERCA], -600, -10, total=False)
e.cota_v([0, ST1["h"]], 600, 10, total=False)
e.chamada((-ST1["larg"] / 2 + 10, 250), (-18, 12), f"ST-1P aba vertical {ST1['t']:g}×{ST1['larg']}×{ST1['h']} (A36) atrás das terças")
e.chamada((FOLGA + E_FURO, Z_TERCA + Z_FURO[1]), (40, 10), "2 M12 8.8 por terça, furo Ø14 na alma e no ST-1P")
e.chamada((400, Z_TERCA + 40), (12, -16), "terça da direita")
e.chamada((-400, Z_TERCA + 40), (-12, -16), "terça da esquerda")
e.chamada((0, Z_TERCA / 2), (30, -22), f"folga {FOLGA} mm de cada ponta ao eixo do suporte; fundo da terça {Z_TERCA} mm acima do concreto")
e.chamada((60, -100), (14, -10), "2 esperas ES-1 M16 (y = ±60), na TS-01")

c = pr.vista("CORTE A-A", (420, 390), E5, titulo="CORTE A-A", subtitulo="detalhe 1, ao longo da viga; alma da terça contra a aba vertical")
c.ret(-250, -150, 500, 150, "CORTADO"); c.hachura([(-250, -150), (250, -150), (250, 0), (-250, 0)], "AR-CONC", 0.03)
xe = -ST1["t"] - 75 + 9.5
c.ret(xe - 8, -150, 16, 270, "METALICA")                                   # ES-1
c.poli([(xe - 8, -150), (xe - 8, -170), (xe + 52, -170)], "METALICA")
c.chapa(-ST1["aba"], 0, ST1["aba"] - ST1["t"], ST1["t"], 0.25)                # aba horizontal
c.chapa(-ST1["t"], 0, ST1["t"], ST1["h"], 0.25)                             # aba vertical
c.ret(xe - 13, ST1["t"], 26, 14, "METALICA"); c.ret(xe - 13, ST1["t"] + 14, 26, 14, "METALICA")   # porca + contraporca
zb = Z_TERCA
u = [(0, zb), (B_TERCA, zb), (B_TERCA, zb + 25), (B_TERCA - 2.65, zb + 25), (B_TERCA - 2.65, zb + 2.65), (2.65, zb + 2.65), (2.65, zb + H_TERCA - 2.65),
     (B_TERCA - 2.65, zb + H_TERCA - 2.65), (B_TERCA - 2.65, zb + H_TERCA - 25), (B_TERCA, zb + H_TERCA - 25), (B_TERCA, zb + H_TERCA), (0, zb + H_TERCA)]
c.poli(u, "METALICA", True); c.hachura(u, "SOLID", 1, "METALICA")
for z in Z_FURO:
    c.ret(-ST1["t"] - 8, zb + z - 6, ST1["t"] + 3 + 8 + 10, 12, "METALICA"); c.ret(3, zb + z - 10, 10, 20, "METALICA")
c.cota_h([-ST1["aba"], xe, -ST1["t"], 0, B_TERCA], -170, -10, total=False)
c.cota_v([0, zb, zb + Z_FURO[0], zb + Z_FURO[1], zb + H_TERCA], B_TERCA + 20, 10, total=False)
c.chamada((xe, 60), (-16, 20), "ES-1 M16, hef 150 + gancho; furo oblongo 18 × 40 na aba")
c.chamada((xe, ST1["t"] + 20), (-12, 32), "porca + contraporca M16 (arruela lisa)")
c.chamada((-ST1["t"] / 2, 200), (-14, 6), "ST-1P chapa dobrada 9,5 (sem solda)")
c.chamada((B_TERCA - 3, zb + 150), (14, 10), "Ue 300×85×25×2,65")
pk = [(-250, zb + H_TERCA), (250, zb + H_TERCA)]
zz = zb + H_TERCA
for nome_, hh, hach in (("TP40 0,50", 40, "ANSI37"), ("lã de rocha 40", 40, "AR-CONC"), ("zipada 0,65 (h 70)", 70, "ANSI37"), ("painel solar", 110, "ANSI31")):
    c.ret(-250, zz, 500, hh, "METALICA")
    c.texto((260, zz + hh / 2), nome_, "min", "MIDDLE_LEFT")
    zz += hh
c.cota_v([zb + H_TERCA, zz], -250, -10, total=False)

p = pr.vista("DETALHE 1C", (620, 390), E5, titulo="DETALHE 1 — PLANTA", subtitulo="topo da viga TS-01; terças chegando de cada lado")
p.ret(-250, -300, 500, 600, "VISTA")
p.chapa(-ST1["aba"], -ST1["larg"] / 2, ST1["aba"], ST1["larg"], 0.3)
for yy in (-60, 60):
    p.circulo((xe, yy), 8, "METALICA"); p.ret(xe - 20, yy - 9, 40, 18, "METALICA")
for sg in (-1, 1):
    ya, yb = sg * FOLGA, sg * 300
    p.poli([(0, ya), (B_TERCA, ya), (B_TERCA, yb), (0, yb)], "METALICA", True)
    p.circulo((0, sg * (FOLGA + E_FURO)), 7, "OCULTA")
p.cota_v([-ST1["larg"] / 2, -60, 60, ST1["larg"] / 2], -ST1["aba"], -10, total=False)
p.cota_h([-ST1["aba"], xe, 0, B_TERCA], -300, -10, total=False)
p.chamada((B_TERCA / 2, 250), (14, 10), "mesa da terça (85)")
p.chamada((xe, 60), (-12, 18), "furos oblongos 18 × 40 (ajuste ±11 ao longo da viga)")

# ------------------------------------------------------------------ DETALHE 2 — MÃO-FRANCESA (1:12,5) + CORTE B-B (1:5)
E10 = 12.5
d = pr.vista("DETALHE 2", (200, 140), E10, titulo="DETALHE 2 — MÃO-FRANCESA MF-1",
             subtitulo="plano da alma da terça; MF parafusada no clipe CMF-1 (espera ES-3 na lateral da mesa inferior) e na alma da terça")
H = 900
pts = [(-200, 0), (200, 0), (200, 150), (75, 230), (75, 700), (200, 780), (200, 900), (-200, 900), (-200, 780), (-75, 700), (-75, 230), (-200, 150)]
d.poli(pts, "CORTADO", fechada=True); d.hachura(pts, "AR-CONC", 0.03)
d.chapa(-ST1["larg"] / 2, H, ST1["larg"], ST1["h"], 0.25)
for sg in (1, -1):
    d.ret(sg * FOLGA if sg > 0 else -1450, H + Z_TERCA, 1440, H_TERCA, "METALICA")
    d.linha((sg * FOLGA, H + Z_TERCA + B_TERCA), (sg * 1450, H + Z_TERCA + B_TERCA), "OCULTA")
    d.ret(min(sg * 200, sg * 260), 92, 60, 16, "METALICA")                       # ES-3 saliente
    d.ret(min(sg * 110, sg * 200), 92, 90, 16, "OCULTA")                         # ES-3 embutida
    d.chapa(sg * 260 - (6.3 if sg > 0 else 0), 62, 6.3, 76, 0.25)                 # CMF-1 (aba na espera)
    xa, za = sg * 300, 100
    xb, zb2 = sg * Y_MF, H + Z_TERCA + Z_MF
    L = math.hypot(xb - xa, zb2 - za); ux, uz = (xb - xa) / L, (zb2 - za) / L
    nx, nz = -uz * 50, ux * 50
    d.poli([(xa - ux * 40, za - uz * 40), (xb + ux * 40, zb2 + uz * 40), (xb + ux * 40 - nx * sg, zb2 + uz * 40 - nz * sg),
            (xa - ux * 40 - nx * sg, za - uz * 40 - nz * sg)], "METALICA", True)
    d.circulo((xa, za), 7, "METALICA"); d.circulo((xb, zb2), 7, "METALICA")
d.cota_h([-Y_MF, -300, -200, 0, 200, 300, Y_MF], -20, -10, total=False)
d.cota_v([0, 100, H, H + Z_TERCA + Z_MF, H + Z_TERCA + H_TERCA], -1450, -10, total=False)
d.chamada((-650, 470), (-14, 10), f"MF-1 L 50×5 (A36) L = {f(mf['comp_m'],2)} m, {mf['angulo']}")
d.chamada((230, 100), (30, -8), "ES-3 M16 (sai 60) + CMF-1 L 76×76×6,3 com porca M16")
d.chamada((300, 100), (36, 26), "M12 8.8: MF-1 × CMF-1")
d.chamada((Y_MF, H + Z_TERCA + Z_MF), (10, -14), f"M12 8.8 na alma da terça: furo Ø14 a {Z_MF} do fundo")
d.chamada((-80, H + 60), (-26, -16), "ST-1P — ver DETALHE 1")
d.marcador_corte((-260, 20), (-260, 180), "B", lado=1)

bb = pr.vista("CORTE B-B", (440, 170), E5, titulo="CORTE B-B", subtitulo="clipe CMF-1 na espera ES-3 (vista lateral da viga)")
bb.ret(-200, 0, 400, 150, "CORTADO"); bb.hachura([(-200, 0), (200, 0), (200, 150), (-200, 150)], "AR-CONC", 0.03)
bb.chapa(-40, 62, 80, 6.3, 0.25)
bb.chapa(-40, 62, 6.3, 76, 0.25)
bb.circulo((0, 100), 8, "METALICA"); bb.ret(-13, 87, 26, 26, "METALICA")
bb.cota_v([0, 62, 100, 138], 200, 10, total=False)
bb.texto((0, -20), "face lateral da mesa inferior da TS-01", "min", "TOP_CENTER")
bb.chamada((0, 100), (14, 16), "ES-3 M16 + porca e arruela")
bb.chamada((-37, 120), (-10, 22), "CMF-1 L = 80 (furo Ø14 da MF-1)")

# ------------------------------------------------------------------ DETALHE 3 — SEÇÃO E FURAÇÃO DA TERÇA (1:5) + esquema por marca (sem escala no comprimento)
s5 = pr.vista("SEÇÃO DA TERÇA", (600, 130), E5, titulo="DETALHE 3 — TERÇA: SEÇÃO E FURAÇÃO", subtitulo="Ue 300×85×25×2,65 ZAR 345; furos na alma")
u = [(B_TERCA, H_TERCA - 25), (B_TERCA, H_TERCA), (0, H_TERCA), (0, 0), (B_TERCA, 0), (B_TERCA, 25)]
s5.poli(u, "METALICA")
for z, cam in ((Z_FURO[0], "METALICA"), (Z_FURO[1], "METALICA"), (Z_COR, "OCULTA"), (Z_MF, "OCULTA"), (Z_DIAG, "OCULTA"), (Z_X[0], "OCULTA"), (Z_X[1], "OCULTA")):
    s5.circulo((0, z), 6 if z == Z_COR else 7 if z in (Z_FURO + (Z_MF,)) else 9, cam)
s5.cota_v([0, Z_X[0], Z_X[1], Z_COR, Z_DIAG, H_TERCA], -10, -10, total=False)
s5.cota_v([0, Z_MF, Z_FURO[0], Z_FURO[1], H_TERCA], B_TERCA, 10, total=False)
s5.chamada((0, Z_FURO[1]), (30, 6), "pontas: 2 Ø14 a 100 e 200")
s5.chamada((0, Z_COR), (30, 6), "correntes Ø12")
s5.chamada((0, Z_DIAG), (30, 4), "diagonal Ø18 (marcas D)")
s5.chamada((0, Z_X[1]), (30, -4), "cruzamento do X 2 Ø18 (marcas X)")
s5.chamada((0, Z_MF), (30, -14), "mão-francesa Ø14")

t20 = pr.vista("ESQUEMA DA TERÇA", (760, 330), 20, titulo="ESQUEMA DE FURAÇÃO DAS TERÇAS", subtitulo="cotas a partir da ponta; L, L/4… pela tabela de marcas")
LT = 1900
t20.ret(0, 0, 800, H_TERCA, "METALICA"); t20.ret(LT - 800, 0, 800, H_TERCA, "METALICA")
t20.interrupcao((800, 0), (LT - 800, 0), "METALICA"); t20.interrupcao((800, H_TERCA), (LT - 800, H_TERCA), "METALICA")
for x in (E_FURO, LT - E_FURO):
    for z in Z_FURO:
        t20.circulo((x, z), 7, "METALICA")
for x in (Y_MF - FOLGA, LT - Y_MF + FOLGA):
    t20.circulo((x, Z_MF), 7, "METALICA")
t20.circulo((560, Z_COR), 6, "METALICA"); t20.circulo((560, Z_DIAG), 9, "METALICA")
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
y = pr.tabela(x0, y, f"TERÇAS Ue 300×85×25×2,65 ZAR 345 ({PESO_UE} kg/m) — L = vão − 20", ["MARCA", "L (mm)", "VÃOS", "FURAÇÃO", "QT", "kg"], tabT,
              [16, 16, 30, 98, 14, 22], destaque_ultima=True)
n_sup = 7 * N_T                         # ST-1P: só nas TS-01 (linhas 2 a 8); nas fachadas a terça apoia na VB
n_m12_st = N_T * (7 * 4 + 2 * 2)
n_mf = N_T * (7 * 2 + 2)
lm = [["ES-1", "2 esperas M16 por terça, concretadas na TS-01 (ND-LET-TS01-3)", f"{7 * 2 * N_T}", "topo da TS-01"],
      ["ES-3", "espera M16 horizontal, lateral da mesa inferior (ND-LET-TS01-3)", f"{7 * 2 * N_T}", "faces B e D da TS-01"],
      ["ST-1P", "chapa dobrada 9,5×220 A36, 4 Ø14 + 2 oblongos", f"{n_sup}", "nas ES-1 (porca + contraporca)"],
      ["ST-1V", "como o ST-1P, 2 oblongos no eixo (VB 15 cm)", f"{2 * N_T}", "nas ES-1V das VB (linhas 1 e 9)"],
      ["CMF-1", "L 76×76×6,3 L=80 A36; 1 Ø18 + 1 Ø14", f"{n_mf}", "nas ES-3"],
      ["MF-1", f"L 50×5 A36, {f(mf['comp_m'],2)} m entre furos, 2 furos Ø14", f"{n_mf}", "parafusada na montagem"],
      ["M12 8.8", "parafuso + porca + 2 arruelas, zincado", f"{n_m12_st + 2 * n_mf}", f"{n_m12_st} no ST-1P + {2*n_mf} nas MF"],
      ["M16", "porca + arruela (contraporca no ST-1P), galvanizadas", f"{3 * 7 * 2 * N_T + n_mf}", "ES-1 e ES-3"]]
y = pr.tabela(x0, y - 4, "LISTA DE MATERIAIS — LIGAÇÕES TERÇA × VIGA (SEM SOLDA)", ["MARCA", "DESCRIÇÃO", "QT", "ONDE"], lm, [18, 106, 14, 58])
cc = LG["cargas_cob"]
notas = [f"Terças simplesmente apoiadas de viga a viga: L = vão entre eixos − {2*FOLGA} mm. Todas com a alma na face +x do ST-1P. Marca = comprimento (T1..T5) + furação: D = 2ª terça das pontas de meia água (diagonais de ancoragem), X = terça intermediária dos painéis do contraventamento.",
         f"Pacote da cobertura sobre as terças (rev03): telha inferior TP40 0,50 + lã de rocha 40 mm + telha zipada 0,65 (trapézio 480 × 70) + painéis solares em toda a cobertura. Cargas permanentes {f(cc['g_total_sem_terca'],3)} kN/m² (painéis {f(cc['paineis_solares'],2)}; instalações {f(cc['instalacoes'],2)}) + terças; sobrecarga {f(cc['sobrecarga'],2)} kN/m². Folga ≥ 15 cm do topo dos painéis ao topo da platibanda (+10,00).",
         "Ligações todas parafusadas, sem solda na fábrica e na obra: ST-1P (chapa dobrada) nas 2 esperas ES-1 da TS-01, com porca de nivelamento por baixo e porca + contraporca por cima; furos oblongos para o ajuste ao longo da viga.",
         "Furação toda de fábrica (d + 2 mm): proibido furar a terça galvanizada na obra sem retoque com tinta rica em zinco.",
         "Montagem: ST-1P nivelado → terça com o fundo 10 mm acima do concreto, 2 M12 8.8 por ponta → CMF-1 na ES-3 e MF-1 (M12 no CMF-1 e na alma da terça) → correntes, tirantes rígidos e diagonais → por último o X, tensionado no esticador até tirar a flecha.",
         "Mão-francesa MF-1 em toda terça, dos dois lados da viga nas linhas 2 a 8 e de um lado nas linhas 1 e 9 (VB): L 50×5 com a aba na alma da terça e no CMF-1.",
         "Telhas, lã e painéis: fixação conforme o fornecedor (clipes da zipada na mesa superior da terça; trilhos dos painéis presos nas costuras da zipada, sem furar a telha).",
         "Correntes, tirantes rígidos, diagonais e X: detalhes na ND-LET-COB02.",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(x0, y - 4, notas, 190)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-COB01")
for a in avisos:
    print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
