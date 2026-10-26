"""ND-LET-COB01 — cobertura metálica: planta de enterçamento e travamento de todo o pavilhão (terças Z contínuas por transpasse
com marcas, transpasses, correntes, tirantes rígidos, diagonais de ancoragem e contraventamento em X) e ligações terça × viga,
todas parafusadas, sem solda e sem mão-francesa (rev05): suporte ST-1P nas esperas ES-1 da TS-01 com as 2 terças do transpasse,
ST-1V na VB das fachadas, emenda por transpasse (METLAP) e furação das terças.
Metálica em mm. A1. Padrão de apresentação: planta do banzo superior / planta da cobertura das referências do escritório.
"""
import math
from prancha_nd import Prancha
from cob_comum import (YLmm, VAOS, X_C, X_E, LTS, X0E, X0D, XT, PASSO, NOS, NOS_D, VAOS_X, Z_FURO, Z_COR, Z_DIAG, Z_X, NOS_X, NOS_X_D, ORE_S, ORE_S9, ORE_Y, PAINEL_X, IDX_X, furos_x, sufixo_x, marca,
                       H_TERCA, B_TERCA, B_INF, D_SUP, D_INF, T_Z, PESO_UE, PERFIL_TXT, IDX_2A, L_TERCA, EXT, BASE_K, NT, A_TR,
                       EXT_F, B_TR, Y_COL, furos_ponta, lista_marcas, cabecalho, CB, LG, f)

ST1 = dict(t=9.5, larg=220, h=290, aba=150)   # ST-1P: chapa dobrada 9,5 × 220 (ao longo da terça); aba vertical 290, horizontal 150
Z_TERCA = 10
N_LIN, N_T = 9, 2 * NT
pr = Prancha("A0", cabecalho("ND-LET-COB01", "01/04", "COBERTURA METÁLICA — PLANTA DE ENTERÇAMENTO E TRAVAMENTO, APOIOS E EMENDAS POR TRANSPASSE"))
pr.revisao("01", pr.dados["data"], "furos centrados na alma; suporte ST-1 + CH-T1; mão-francesa na OR-1; planta completa")
pr.revisao("02", pr.dados["data"], "geometria do R01 (79,35 m; TS-01 19,15 m); X de nó a nó; correntes e MF no padrão de referência")
pr.revisao("03", "14/10/2026", "TERÇAS c/1,20 m Ue 300×2,65; PACOTE TP40 + LÃ 40 + ZIPADA + PAINÉIS; ST-1P E MF PARAFUSADOS (SEM SOLDA)")
pr.revisao("05", "17/10/2026", "TERÇAS Z 302×2,30 METSEC CONTÍNUAS POR TRANSPASSE (METLAP); SEM MÃO-FRANCESA; APOIO COM 4 M12")
pr.revisao("06", "17/10/2026", "MODELO INTEGRADO: X NOS VÃOS 4-5 A 8-9; 15 ESPAÇOS (CALHA 40 cm NO EIXO A); FUROS X/Y; ST-1V-R NO EIXO 9")
st, chb, tc = CB["ST1P"], CB["chumbadores"], CB["terca"]

# ------------------------------------------------------------------ PLANTA DE ENTERÇAMENTO E TRAVAMENTO 1:175 (papel: horizontal = y da obra)
ESC_P = 175
v = pr.vista("PLANTA", (86, 560), ESC_P, titulo="PLANTA DE ENTERÇAMENTO E TRAVAMENTO DA COBERTURA",
             subtitulo=f"terças {PERFIL_TXT} c/{PASSO} (ao longo da água), contínuas por transpasse; caimento 3 %")
M = lambda y, x: (y, x)
for yl in YLmm:
    for x0 in (X0E, X0D):
        v.poli([M(yl - 200, x0), M(yl + 200, x0), M(yl + 200, x0 + LTS), M(yl - 200, x0 + LTS)], "VISTA", True)
    v.ret(yl - 300, X_C - 200, 600, 400, "CORTADO")
    v.ret(yl - 200, -300, 400, 600, "CORTADO"); v.ret(yl - 200, X_E - 300, 400, 600, "CORTADO")
for k in range(8):
    ya, yb = YLmm[k] - EXT[k][0], YLmm[k + 1] + EXT[k][1]          # peça: passa o transpasse (ou EXT_F na fachada)
    dx = 0 if k % 2 == 0 else 40                                  # peças de vãos alternados desenhadas 40 deslocadas (ver transpasse)
    for x in XT:
        v.linha(M(ya, x - B_TERCA + dx), M(yb, x - B_TERCA + dx), "METALICA")
        v.linha(M(ya, x + B_INF + dx), M(yb, x + B_INF + dx), "METALICA")
        for yy in (ya, yb):
            v.linha(M(yy, x - B_TERCA + dx), M(yy, x + B_INF + dx), "METALICA")
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
        yb_ = yb - (0 if k == 7 else ORE_Y)                       # eixo 9: orelha no eixo da VB
        sb = ORE_S9 if k == 7 else ORE_S
        for nos in (NOS_X, NOS_X_D):
            for a, b in zip(nos[:-1], nos[1:]):
                v.linha(M(ya + ORE_Y, a + ORE_S), M(yb_, b - sb), "ARMADURA")
                v.linha(M(ya + ORE_Y, b - ORE_S), M(yb_, a + sb), "ARMADURA")
# eixos e marcas
for i, yl in enumerate(YLmm):
    v.eixo(M(yl, -900), M(yl, X_E + 900), 0)
    xp, yp = v.P(M(yl, X_E + 1900))
    pr.msp.add_circle((xp, yp), 3.2, dxfattribs={"layer": "INDICACAO"})
    pr.texto(xp, yp, str(i + 1), "sub", "TITULO", "MIDDLE_CENTER")
for lbl, x in (("A", 0), ("C", X_C), ("E", X_E)):
    v.eixo(M(-8400, x), M(YLmm[-1] + 900, x), 0)                   # rev08: bolhas à esquerda das cotas (sem linha de cota cruzando)
    xp, yp = v.P(M(-9000, x))
    pr.msp.add_circle((xp, yp), 3.2, dxfattribs={"layer": "INDICACAO"})
    pr.texto(xp, yp, lbl, "sub", "TITULO", "MIDDLE_CENTER")
for k in range(8):
    ym = (YLmm[k] + YLmm[k + 1]) / 2
    for x in (XT[NT // 2 - 1] + 700, XT[NT + NT // 2 - 1] + 700):
        xp, yp = v.P(M(ym + 1800, x))
        pr.msp.add_circle((xp, yp), 4.0, dxfattribs={"layer": "INDICACAO"})
        pr.texto(xp, yp, BASE_K[k], "nota", "TITULO", "MIDDLE_CENTER")
    for kk in (NT // 2 + 1, NT + NT // 2 + 1):                      # rev08: entre duas terças, paralelo a elas
        v.texto(M(YLmm[k] + 0.375 * VAOS[k], (XT[kk] + B_INF + XT[kk + 1] - B_TERCA) / 2), f"L {L_TERCA[k]}", "min", "MIDDLE_CENTER")   # rev11: entre as correntes
v.cota_h(YLmm, -900, -10, total=False)
v.cota_h([YLmm[0], YLmm[-1]], X_E + 3000, 8, total=False)
v.cota_v([XT[0], XT[NT - 1]], YLmm[0] - 900, -12, total=False)
v.texto(M(YLmm[0] - 1700, (XT[0] + XT[NT - 1]) / 2), f"{NT - 1} × {PASSO}", "min", "MIDDLE_CENTER", rot=90)
v.cota_v([X0E, X0E + LTS], YLmm[0] - 900, -24, total=False)
v.cota_v([XT[NT], XT[2 * NT - 1]], YLmm[0] - 900, -12, total=False)
v.texto(M(YLmm[0] - 1700, (XT[NT] + XT[2 * NT - 1]) / 2), f"{NT - 1} × {PASSO}", "min", "MIDDLE_CENTER", rot=90)
v.cota_v([X0D, X0D + LTS], YLmm[0] - 900, -24, total=False)
v.cota_v([0, X_C, X_E], YLmm[0] - 900, -36, total=False)
RX = YLmm[8] - 300
v.chamada(M(YLmm[8] - 2500, XT[2 * NT - 2] + 40), (16, 14), "terça Z 302 (alma na face +x do ST-1P, aba de 90 sobre o ST-1P)")
def ch_dir(pm, dy, txt, x_txt=562):
    xp_, _ = v.P(pm)
    v.chamada(pm, (x_txt - xp_, dy), txt)
ch_dir(M(YLmm[6] + A_TR / 2, XT[NT - 3]), -4, f"transpasse {2 * A_TR} sobre cada TS-01 (det. 1)")
v.chamada(M(YLmm[7] + VAOS[7] * 0.75, (XT[NT + 5] + XT[NT + 6]) / 2), (18, 4), "corrente flexível Ø10 (L/4, L/2, 3L/4)")
v.chamada(M(YLmm[7] + VAOS[7] * 0.75, (XT[0] + XT[1]) / 2), (14, -14), "tirante rígido L 51×51×3,2 no 1º espaço")
ch_dir(M(YLmm[7] + VAOS[7] * 0.15, (XT[2 * NT - 2] + XT[2 * NT - 1]) / 2), 2, "diagonal de ancoragem Ø16")
_ym = (YLmm[6] + YLmm[7]) / 2
v.chamada(M(YLmm[7] + 7200, NOS_X[1] - 2300), (40, -22), "X Ø16 c/ esticador (vãos 4-5 a 8-9, painéis de 8 e 7 terças; COB02)")
v.chamada(M(YLmm[8], XT[NT + 2]), (16, -6), f"fachada: terça passa {EXT_F} do eixo, ST-1V na VB (eixo 9: ST-1V-R, det. 2)")
v.chamada(M(YLmm[8] - 200, X_C), (16, -8), "pilar central / I130 (eixo C)")
v.marcador_detalhe(M(YLmm[5], (XT[NT + 8] + XT[NT + 9]) / 2), 600, 1, ang=0, dist=0.5)     # rev11: número no vão entre terças
v.marcador_detalhe(M(YLmm[8], (XT[NT + 11] + XT[NT + 12]) / 2), 500, 2, ang=180, dist=0.5)

# ------------------------------------------------------------------ geometria dos detalhes (mm)
ST1 = dict(t=9.5, larg=220, h=290, aba=150)   # ST-1P: chapa dobrada 9,5 × 220 (ao longo da terça); aba vertical 290, horizontal 150
Z_TERCA = 10                                  # fundo da terça 10 mm acima do concreto (calço/porca de nivelamento)
N_LIN, N_T = 9, 2 * NT
C45 = math.cos(math.radians(45))
ZB = [Z_TERCA + z for z in Z_FURO]            # furos da alma medidos do concreto (62 e 257)


def z_secao(vw, x0, z0, s=-1):
    """Linha média do Z (aba superior de 90 para o lado s, inferior de 82 para o outro), enrijecedores a 45°."""
    pts = [(x0 - s * (B_INF - D_INF * C45), z0 + D_INF * C45), (x0 - s * B_INF, z0), (x0, z0), (x0, z0 + H_TERCA),
           (x0 + s * B_TERCA, z0 + H_TERCA), (x0 + s * (B_TERCA - D_SUP * C45), z0 + H_TERCA - D_SUP * C45)]
    vw.poli(pts, "METALICA")
    return pts


def parafuso_h(vw, x0, x1, z):
    """Parafuso M12 visto de lado (corte): fuste + cabeça e porca."""
    vw.ret(min(x0, x1), z - 6, abs(x1 - x0), 12, "METALICA")
    vw.ret(min(x0, x1) - 8, z - 10, 8, 20, "METALICA"); vw.ret(max(x0, x1), z - 10, 10, 20, "METALICA")


# ------------------------------------------------------------------ DETALHE 1 — APOIO INTERNO NA TS-01 E EMENDA POR TRANSPASSE (elevação 1:10)
E10, E5 = 10, 5
XL = A_TR + 250
e = pr.vista("DETALHE 1A", (148, 385), E10, titulo="DETALHE 1 — APOIO E EMENDA POR TRANSPASSE (METLAP)",
             subtitulo=f"elevação no plano da alma; terça do vão da esquerda por trás, a da direita na frente; transpasse {2 * A_TR}")
e.ret(-XL, -150, 2 * XL, 150, "CORTADO"); e.hachura([(-XL, -150), (XL, -150), (XL, 0), (-XL, 0)], "AR-CONC", 0.03)
for yy in (-60, 60):
    e.ret(yy - 8, -150, 16, 270, "OCULTA")                                   # ES-1
e.ret(-ST1["larg"] / 2, 0, ST1["larg"], ST1["h"], "OCULTA")                  # ST-1P atrás das almas
# terça da esquerda (por trás): de −XL até +A_TR ; terça da direita (na frente): de −A_TR até +XL
e.poli([(-XL, Z_TERCA), (A_TR, Z_TERCA), (A_TR, Z_TERCA + H_TERCA), (-XL, Z_TERCA + H_TERCA)], "OCULTA")
e.linha((-XL, Z_TERCA), (-A_TR, Z_TERCA), "METALICA"); e.linha((-XL, Z_TERCA + H_TERCA), (-A_TR, Z_TERCA + H_TERCA), "METALICA")
dz = T_Z
e.poli([(-A_TR, Z_TERCA + dz), (XL, Z_TERCA + dz), (XL, Z_TERCA + dz + H_TERCA), (-A_TR, Z_TERCA + dz + H_TERCA)], "METALICA", True)
for yy in (-Y_COL, Y_COL, -(A_TR - B_TR), A_TR - B_TR):
    for z in ZB:
        e.circulo((yy, z), 7, "METALICA"); e.circulo((yy, z), 10.5, "METALICA")
for z in ZB:
    e.linha((-A_TR - 30, z), (A_TR + 30, z), "EIXO")
e.eixo((0, -150), (0, Z_TERCA + H_TERCA + 60), 0)
e.circulo((0, Z_DIAG + Z_TERCA), 9, "OCULTA")
e.chamada((0, Z_DIAG + Z_TERCA), (-14, (Z_TERCA + H_TERCA + 30) / E10 + 26 - (Z_DIAG + Z_TERCA) / E10), "furo Ø18 no ST-1P das pontas de meia água: diagonal Ø16")
e.cota_h([-A_TR, -(A_TR - B_TR), -Y_COL, 0, Y_COL, A_TR - B_TR, A_TR], Z_TERCA + H_TERCA + 30, 8, total=False)
e.cota_h([-A_TR, A_TR], Z_TERCA + H_TERCA + 30, 16, total=False)
e.cota_v([0, ZB[0], ZB[1], Z_TERCA + H_TERCA], -XL, -10, total=False)
e.cota_v([0, ST1["h"]], XL, 10, total=False)
e.chamada((A_TR - B_TR, ZB[1]), (8, 24), f"emenda: 2 M12 8.8 a {B_TR} de cada ponta")
e.chamada((Y_COL, ZB[0]), (-30, -ZB[0] / E10 - 30), "apoio: 4 M12 8.8 (2 colunas a ±60) — ST-1P + 2 almas")
e.chamada((-ST1["larg"] / 2 + 10, 230), (-40, 26), "ST-1P 9,5×220×290 (A36) atrás das almas")
e.chamada((-XL + 100, Z_TERCA + 60), (-8, -29), "terça do vão da esquerda")
e.chamada((XL - 100, Z_TERCA + 60), (8, -40), "terça do vão da direita")
e.chamada((60, -100), (4, -12), "2 esperas ES-1 M16 (y = ±60) na viga")

c = pr.vista("CORTE A-A", (415, 385), E5, titulo="CORTE A-A", subtitulo="apoio interno: ST-1P + 2 Z encaixados no transpasse")
c.ret(-250, -150, 500, 150, "CORTADO"); c.hachura([(-250, -150), (250, -150), (250, 0), (-250, 0)], "AR-CONC", 0.03)
xe = -ST1["t"] - 75 + 9.5
c.ret(xe - 8, -150, 16, 270, "METALICA")                                   # ES-1
c.poli([(xe - 8, -150), (xe - 8, -170), (xe + 52, -170)], "METALICA")
c.chapa(-ST1["aba"], 0, ST1["aba"] - ST1["t"], ST1["t"], 0.25)                # aba horizontal
c.chapa(-ST1["t"], 0, ST1["t"], ST1["h"], 0.25)                             # aba vertical
c.ret(xe - 13, ST1["t"], 26, 14, "METALICA"); c.ret(xe - 13, ST1["t"] + 14, 26, 14, "METALICA")   # porca + contraporca
z_secao(c, T_Z / 2, Z_TERCA, s=-1)                                         # terça interna (contra o ST-1P)
z_secao(c, 1.5 * T_Z, Z_TERCA + T_Z, s=-1)                                 # terça externa, encaixada
for z in ZB:
    parafuso_h(c, -ST1["t"], 2 * T_Z + 3, z)
c.cota_h([-ST1["aba"], xe, 0, B_INF], -170, -10, total=False)
c.cota_h([-B_TERCA, 0], Z_TERCA + H_TERCA + 20, 8, total=False)
c.cota_v([Z_TERCA, ZB[0], ZB[1], Z_TERCA + H_TERCA], 250, 10, total=False)
c.cota_v([0, Z_TERCA], 250, 22, total=False)
c.chamada((xe, 60), (-16, 20), "ES-1 M16, hef 150 + gancho + grampo U Ø10; oblongo 18 × 40 na aba")
c.chamada((xe, ST1["t"] + 20), (-12, 34), "porca + contraporca M16 (arruela lisa)")
c.chamada((-ST1["t"] / 2, 180), (-16, 10), "ST-1P chapa dobrada 9,5 (sem solda)")
c.chamada((B_INF - 10, Z_TERCA + 8), ((250 - B_INF + 10) / E5 + 26, -12), "2 Z 302×2,30 encaixados")
c.chamada((2 * T_Z + 8, ZB[1]), (20, -8), "M12 8.8 + arruelas Ø24")
zz = Z_TERCA + H_TERCA + T_Z
for nome_, hh in (("TP-40 #0,65", 40), ("lã de rocha FSR-32 40", 40), ("zipada 455 #0,50 (h 70)", 70), ("painel solar", 110)):
    c.ret(-250, zz, 500, hh, "METALICA")
    c.texto((260, zz + hh / 2), nome_, "min", "MIDDLE_LEFT")
    zz += hh
c.cota_v([Z_TERCA + H_TERCA + T_Z, zz], -250, -10, total=False)

p = pr.vista("DETALHE 1C", (645, 385), E10, titulo="DETALHE 1 — PLANTA", subtitulo="topo da TS-01: transpasse das terças sobre o ST-1P")
p.ret(-250, -XL, 500, 2 * XL, "VISTA")
p.chapa(-ST1["aba"], -ST1["larg"] / 2, ST1["aba"], ST1["larg"], 0.3)
for yy in (-60, 60):
    p.circulo((xe, yy), 8, "METALICA"); p.ret(xe - 20, yy - 9, 40, 18, "METALICA")
for (y0, y1, dx, cam) in ((-XL, A_TR, 0, "OCULTA"), (-A_TR, XL, T_Z, "METALICA")):
    p.poli([(-B_TERCA + dx, y0), (B_INF + dx, y0), (B_INF + dx, y1), (-B_TERCA + dx, y1)], cam, True)
    p.linha((dx, y0), (dx, y1), cam)
for yy in (-Y_COL, Y_COL, -(A_TR - B_TR), A_TR - B_TR):
    p.circulo((0, yy), 7, "OCULTA")
p.cota_v([-A_TR, -Y_COL, Y_COL, A_TR], B_INF + 20, 10, total=False)
p.cota_h([-ST1["aba"], -B_TERCA, 0, B_INF], -XL, -10, total=False)
p.chamada((-B_TERCA / 2, XL - 120), (-24, 10), "aba superior 90 (lado A)")
p.chamada((xe, 60), (-22, 18), "furos oblongos 18 × 40 (ajuste ±11 ao longo da viga)")
p.chamada((B_INF / 2, A_TR - 20), (24, 6), f"ponta da terça da esquerda (+{A_TR})")
p.chamada((B_INF / 2, -A_TR + 20), (24, -6), f"ponta da terça da direita (−{A_TR})")

# ------------------------------------------------------------------ DETALHE 2 — APOIO NA FACHADA (VB, ST-1V) — elevação 1:10 + CORTE B-B 1:5
d = pr.vista("DETALHE 2", (150, 160), E10, titulo="DETALHE 2 — APOIO NA FACHADA: TERÇA SOBRE A VB (ST-1V)",
             subtitulo=f"elevação no plano da alma; terça passa {EXT_F} do eixo da VB; 4 M12 8.8, sem mão-francesa")
d.ret(-75, -600, 150, 600, "CORTADO"); d.hachura([(-75, -600), (75, -600), (75, 0), (-75, 0)], "AR-CONC", 0.03)
d.ret(-ST1["larg"] / 2, 0, ST1["larg"], ST1["h"], "OCULTA")
d.poli([(-EXT_F, Z_TERCA), (700, Z_TERCA), (700, Z_TERCA + H_TERCA), (-EXT_F, Z_TERCA + H_TERCA)], "METALICA", True)
d.interrupcao((700, Z_TERCA), (700, Z_TERCA + H_TERCA), "METALICA")
for yy in (-Y_COL, Y_COL):
    for z in ZB:
        d.circulo((yy, z), 7, "METALICA"); d.circulo((yy, z), 10.5, "METALICA")
d.eixo((0, -600), (0, Z_TERCA + H_TERCA + 60), 0)
d.cota_h([-EXT_F, -Y_COL, 0, Y_COL, ST1["larg"] / 2], Z_TERCA + H_TERCA + 30, 8, total=False)
d.cota_h([-75, 75], -600, -8, total=False)
d.cota_v([0, ZB[0], ZB[1], Z_TERCA + H_TERCA], 700, 10, total=False)
d.chamada((Y_COL, ZB[1]), (20, 14), "4 M12 8.8 (2 colunas a ±60)")
d.chamada((ST1["larg"] / 2 - 10, 230), (16, 27), "ST-1V 9,5×220×290 nas 2 ES-1V (eixo da VB)")
d.chamada((0, -300), (16, -6), "VB 15×60 (fachadas 1 e 9)")
d.chamada((-45, -450), (16, -10), "eixo 9 (ST-1V-R): 2 ES-1R M20 hef 400 + grampo U Ø10 em cada")
d.marcador_corte((-EXT_F - 60, 120), (-EXT_F - 60, 260), "B", lado=-1)

bb = pr.vista("CORTE B-B", (415, 160), E5, titulo="CORTE B-B", subtitulo="apoio na VB: ST-1V + 1 Z")
bb.ret(-200, -150, 400, 150, "CORTADO"); bb.hachura([(-200, -150), (200, -150), (200, 0), (-200, 0)], "AR-CONC", 0.03)
bb.chapa(-ST1["aba"], 0, ST1["aba"] - ST1["t"], ST1["t"], 0.25)
bb.chapa(-ST1["t"], 0, ST1["t"], ST1["h"], 0.25)
for xx in (-45, -105):
    bb.ret(xx - 8, -150, 16, 270, "METALICA"); bb.ret(xx - 13, ST1["t"], 26, 14, "METALICA")
z_secao(bb, T_Z / 2, Z_TERCA, s=-1)
for z in ZB:
    parafuso_h(bb, -ST1["t"], T_Z + 3, z)
bb.cota_h([-ST1["aba"], -105, -45, 0, B_INF], -150, -10, total=False)
bb.cota_v([Z_TERCA, ZB[0], ZB[1], Z_TERCA + H_TERCA], 200, 10, total=False)
bb.cota_v([0, Z_TERCA], 200, 22, total=False)
bb.chamada((-75, 60), (-14, 18), "eixo 1: 2 ES-1V M16 hef 150; eixo 9: 2 ES-1R M20 hef 400 + grampo")
bb.chamada((B_INF - 10, Z_TERCA + 8), ((200 - B_INF + 10) / E5 + 26, -12), "Z 302×2,30")

# ------------------------------------------------------------------ DETALHE 3 — SEÇÃO E FURAÇÃO DA TERÇA (1:5) + esquema por marca
s5 = pr.vista("SEÇÃO DA TERÇA", (585, 150), E5, titulo="DETALHE 3 — TERÇA Z: SEÇÃO E FURAÇÃO", subtitulo=f"{PERFIL_TXT}; furos na alma")
z_secao(s5, 0, 0, s=-1)
for z, cam, r in ((Z_FURO[0], "METALICA", 7), (Z_FURO[1], "METALICA", 7), (Z_COR, "OCULTA", 6), (Z_DIAG, "OCULTA", 9), (Z_X[0], "OCULTA", 9), (Z_X[1], "OCULTA", 9)):
    s5.circulo((0, z), r, cam)
s5.cota_h([-B_TERCA, 0], H_TERCA + 20, 8, total=False)
s5.cota_h([0, B_INF], -20, -8, total=False)
s5.cota_v([0, Z_X[0], Z_X[1], Z_COR, Z_DIAG, H_TERCA], -B_TERCA - 20, -10, total=False)
s5.cota_v([0, Z_FURO[0], Z_FURO[1], H_TERCA], B_INF + 20, 10, total=False)
s5.chamada((0, Z_FURO[1]), (38, 14), f"fixação: Ø14 a {Z_FURO[0]} e {Z_FURO[1]} (E 55 / F 52)")
s5.chamada((0, Z_COR), (38, 6), "correntes Ø12")
s5.chamada((0, Z_DIAG), (-34, -8), "diagonal Ø18 (marcas D)")
s5.chamada((0, Z_X[0]), (-34, -14), "X: oblongos 18×28 (marcas X / Y)")
s5.chamada((-B_TERCA + 8, H_TERCA - 8), (-10, 10), f"enrijecedores {D_SUP} / {D_INF} a 45°")

t20 = pr.vista("ESQUEMA DA TERÇA", (760, 244), 12.5, titulo="ESQUEMA DE FURAÇÃO DAS TERÇAS",
               subtitulo="cotas a partir de cada ponta; pontas de transpasse (vãos internos) e de fachada (VB)")
LT = 2600
t20.ret(0, 0, 1000, H_TERCA, "METALICA"); t20.ret(LT - 1000, 0, 1000, H_TERCA, "METALICA")
t20.interrupcao((1000, 0), (LT - 1000, 0), "METALICA"); t20.interrupcao((1000, H_TERCA), (LT - 1000, H_TERCA), "METALICA")
fp_t, fp_f = furos_ponta(A_TR), furos_ponta(EXT_F)
for xx in fp_t:
    for z in Z_FURO:
        t20.circulo((xx, z), 7, "METALICA")
for xx in fp_f:
    for z in Z_FURO:
        t20.circulo((LT - xx, z), 7, "METALICA")
t20.circulo((A_TR + 400, Z_COR), 6, "METALICA")
t20.cota_h([0] + fp_t, 0, -10, total=False)
t20.cota_h([LT - x_ for x_ in reversed(fp_f)] + [LT], 0, -10, total=False)
t20.texto((LT / 2, H_TERCA + 60), "L (ver tabela)", "nota", "BOTTOM_CENTER")
t20.texto((500, H_TERCA + 60), "ponta de transpasse", "min", "BOTTOM_CENTER")
t20.texto((LT - 500, H_TERCA + 60), "ponta de fachada (T1, T5)", "min", "BOTTOM_CENTER")
t20.chamada((A_TR + 400, Z_COR), (30, 30), "correntes a L/4, L/2, 3L/4 do eixo do apoio")
t20.chamada((B_TR, Z_FURO[1]), (-6, 20), f"emenda: a {B_TR} e {2 * A_TR - B_TR}")
t20.chamada((A_TR + Y_COL, Z_FURO[0]), (14, -22), f"apoio: a {A_TR - Y_COL} e {A_TR + Y_COL}")

# ------------------------------------------------------------------ tabelas
x0, y = pr.quadro[2] - 196, pr.quadro[3] - 6
# furos do X por marca: y (mm) a partir do eixo do apoio do início do vão; '/' a 35 e '\\' a 75 do fundo da terça
_bk = {BASE_K[k]: k for k in VAOS_X}
tabX = []
for j in sorted(i_ for i_ in IDX_X if i_ < NT):
    lin_ = [sufixo_x(j)]
    for bm, k in sorted(_bk.items()):
        (y1, _, _), (y2, _, _) = furos_x(k, j)
        lin_ += [f"{y1}", f"{y2}"]
    tabX.append(lin_)
cabX = ["FURO"] + sum(([f"{bm} /35", f"{bm} \\75"] for bm in sorted(_bk)), [])
y = pr.tabela(x0, y, "FUROS DO X (OBLONGOS 18×28) — y DO EIXO INICIAL DO VÃO, mm", cabX, tabX,
              [16] + [30] * (len(cabX) - 1))
y -= 4
LM = lista_marcas()
tabT = []
for m_, dd in LM.items():
    fur = "pontas (apoio + emenda), correntes" + (" + diag. Ø18" if "D" in m_[2:] else "") + (f" + X {m_[-2:]}" if ("X" in m_[2:] or "Y" in m_[2:]) else "")
    tabT.append([m_, f"{dd['L']}", ", ".join(sorted(dd["vaos"])), fur, f"{dd['qt']}", f"{dd['qt']*dd['L']/1000*PESO_UE:,.0f}".replace(",", ".")])
qt_t = sum(dd["qt"] for dd in LM.values())
kg_t = sum(dd["qt"] * dd["L"] / 1000 * PESO_UE for dd in LM.values())
tabT.append(["", "", "", "total", f"{qt_t}", f"{kg_t:,.0f}".replace(",", ".")])
y = pr.tabela(x0, y, f"TERÇAS Z 302×90/82×2,30 METSEC ({PESO_UE} kg/m) — L com os transpasses", ["MARCA", "L (mm)", "VÃOS", "FURAÇÃO", "QT", "kg"], tabT,
              [16, 16, 30, 98, 14, 22], destaque_ultima=True)
n_sup = 6 * N_T                           # ST-1P: TS-01 (linhas 3 a 8), 1 por apoio; rev09 (DEC-048): na linha 2 a terça apoia no ST-W da W 310
n_m12 = N_T * (7 * (4 + 4) + 2 * 4)       # por linha: 7 apoios internos (4 no ST-1P / ST-W + 2×2 nas pontas do transpasse) + 2 fachadas (4)
lm = [["ES-1", "2 esperas M16 por apoio, concretadas na TS-01 (TS01-3)", f"{6 * 2 * N_T}", "topo da TS-01"],
      ["ST-1P", "chapa dobrada 9,5×220 A36, 4 Ø14 + 2 oblongos", f"{n_sup}", "nas ES-1 (porca + contraporca)"],
      ["ST-W", "clip da terça na mesa da W 200 da linha 2: 2 M12 na mesa + 4 M12 nas almas (ND-LET-COB05, ISO 5 da COB09)", f"{N_T}", "linha 2"],
      ["MF-1", "mão-francesa L 51×51×4,8 do parafuso da ponta do transpasse à mesa inferior da W 200 (ND-LET-COB05)", f"{2 * N_T}", "linha 2, 2 por terça"],
      ["GR-1", "grampo U Ø10 em cada ES-1 (armadura de ancoragem)", f"{6 * 2 * N_T}", "TS-01, com as ES-1"],
      ["ST-1V", "como o ST-1P, 2 oblongos 18×40 no eixo (VB 15 cm)", f"{N_T}", "nas ES-1V da VB do eixo 1"],
      ["ST-1V-R", "como o ST-1V, oblongos 22×44 (esperas M20)", f"{N_T}", "nas ES-1R da VB do eixo 9 (det. 2)"],
      ["M12 8.8", "parafuso + porca + 2 arruelas Ø24, zincado", f"{n_m12}", f"{N_T * (7 * 4 + 2 * 4)} nos apoios + {N_T * 7 * 4} nas emendas"],
      ["M16", "porca + arruela (contraporca no ST-1P), galvanizadas", f"{3 * 6 * 2 * N_T + 3 * 2 * N_T}", "ES-1 e ES-1V"],
      ["M20", "porca + arruela + contraporca, galvanizadas", f"{3 * 2 * N_T}", "ES-1R (eixo 9)"]]
y = pr.tabela(x0, y - 4, "LISTA DE MATERIAIS — APOIOS E EMENDAS DAS TERÇAS (SEM SOLDA)", ["MARCA", "DESCRIÇÃO", "QT", "ONDE"], lm, [18, 106, 14, 58])
cc = LG["cargas_cob"]
notas = [f"Terças Z 302×90/82×2,30 METSEC (302Z23, fy 400 MPa, galvanizadas Z275) contínuas nos 8 vãos pelo sistema de transpasse (METLAP): cada peça vence um vão e passa {A_TR} além do eixo de cada TS-01 (transpasse total {2*A_TR}); nas fachadas passa {EXT_F} além do eixo da VB. Marca = peça (T1..T5) + furação: D = 2ª terça das pontas de meia água (diagonais), Xj / Yj = j-ésima terça dentro do painel do X de 8 espaços (X1..X7) ou de 7 espaços (Y1..Y6), com os 2 furos oblongos da tabela de furos do X.",
         f"Aba superior de 90 voltada para o lado A (sobre a aba vertical do ST-1P); aba inferior de 82 para o lado E. No transpasse os 2 perfis encaixam um no outro conforme o sistema METLAP do fabricante; furação de fábrica METSEC (E 55 / F 52) — conferir com a voestalpine Meincol antes do pedido.",
         f"Sem mão-francesa: em cada apoio 4 M12 8.8 atravessam o ST-1P (ou ST-1V) e as almas (2 colunas a ±{Y_COL} do eixo, furos a {Z_FURO[0]} e {Z_FURO[1]} do fundo); em cada ponta do transpasse 2 M12 8.8 pelas 2 almas, a {B_TR} da ponta.",
         f"Cobertura Isoeste — Telha Zipada Dupla com lã de rocha FSR-32 (manual de instalação, p. 28): 1º TP-40 STD 980 #0,65 na terça (PB 12-14 × 3/4\" P03, 4 por telha por terça); 2º perfil cartola #0,65 sobre cada terça, costurado na TP-40 com PB 1/4\"-14 × 7/8\" P01 EM TODAS AS ONDAS (o manual indica a cada 2 ondas: não passa na sucção desta obra); 3º lã de rocha FSR 32 40 mm; 4º clipe fixo/deslizante #0,65 na cartola (2 PB 12-14 × 3/4\"); 5º zipada 455 #0,50; painéis solares nas costuras da zipada. Cargas permanentes {f(cc['g_total_sem_terca'],3)} kN/m² + terças; sobrecarga {f(cc['sobrecarga'],2)} kN/m².",
         "Linha 2 (rev09, DEC-048): sem TS-01; as terças apoiam no clip ST-W sobre a W 200 × 15,0 contínua (nos pilares e em 4 montantes W 150 × 13,0 sobre as VM do +7,30) e levam mão-francesa MF-1 em toda terça para travar a mesa inferior da W 200 (ND-LET-COB05).",
         "Ligações todas parafusadas, sem solda na fábrica e na obra: ST-1P nas 2 esperas ES-1 da TS-01, com porca de nivelamento por baixo e porca + contraporca por cima; furos oblongos para o ajuste ao longo da viga.",
         "Furação toda de fábrica (d + 2 mm): proibido furar a terça galvanizada na obra sem retoque com tinta rica em zinco.",
         "Montagem: ST-1P nivelados em toda a linha → terças do vão 1-2 ao 8-9, cada peça encaixada na anterior no transpasse → 4 M12 por apoio e 2 M12 em cada ponta do transpasse (aperto final só com a linha inteira montada) → correntes, tirantes rígidos e diagonais → por último o X, tensionado no esticador até tirar a flecha.",
         "Fixações da cobertura verificadas à sucção (NBR 6123, zona geral e faixa de borda; memória ND-LET-MC06): costura cartola × TP-40 em todas as ondas (uso 0,90 na borda); clipes com 2 parafusos (0,96 na borda); TP-40 × terça 0,22. Confirmar com a Isoeste os valores de arrancamento em chapa #0,65 e a distribuição de clipes; trilhos dos painéis nas costuras da zipada, sem furar a telha.",
         "Correntes, tirantes rígidos, diagonais e X: detalhes na ND-LET-COB02.",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(x0, y - 4, notas, 190)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-COB01")
for a in avisos:
    print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
