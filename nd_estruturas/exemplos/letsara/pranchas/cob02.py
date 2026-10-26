"""ND-LET-COB02 — cobertura metálica: travamento (padrão das plantas de cobertura das referências do escritório).
Planta do vão típico contraventado com marcas das terças, X de nó a nó, correntes, tirantes rígidos e diagonais de ancoragem;
detalhes: fixação do tirante nas orelhas OR-X (cantoneira parafusada na espera ES-2, sem solda), tirante Ø16 com esticador, travamento das terças (corrente flexível +
tirante rígido + diagonal), diagonal no ST-1 e cruzamento do X na terça. Lista de materiais do travamento. Metálica em mm. A1.
"""
import math
from prancha_nd import Prancha
from cob_comum import (YLmm, VAOS, X_C, X_E, LTS, X0E, X0D, XT, PASSO, NOS, NOS_D, VAOS_X, FOLGA, Z_COR, Z_DIAG, Z_X, NOS_X, NOS_X_D, ORE_S, ORE_Y, PAINEL_X, furos_x,
                       H_TERCA, B_TERCA, B_INF, D_SUP, D_INF, A_TR, IDX_2A, NT, marca, cabecalho, CB, LG, f)

pr = Prancha("A0", cabecalho("ND-LET-COB02", "02/04", "COBERTURA METÁLICA — TRAVAMENTO: CONTRAVENTAMENTO EM X, CORRENTES E DIAGONAIS"))
pr.revisao("01", pr.dados["data"], "desdobrada da COB01; correntes no meio da alma; diagonais no ST-1")
pr.revisao("02", pr.dados["data"], "X de nó a nó com esticador (sem CH-X); tirantes rígidos L 51; detalhes no padrão de referência")
pr.revisao("03", "14/10/2026", "17 TERÇAS POR MEIA ÁGUA (c/1,20 m); ORELHAS OR-X PARAFUSADAS NAS ESPERAS ES-2 (SEM SOLDA)")
pr.revisao("05", "17/10/2026", "TERÇAS Z 302 METSEC CONTÍNUAS POR TRANSPASSE; SEM MÃO-FRANCESA; FUROS DO X E DA DIAGONAL")
pr.revisao("06", "17/10/2026", "MODELO INTEGRADO: X NOS VÃOS 4-5 A 8-9 (45°); 15 ESPAÇOS DE TERÇA; FUROS OBLONGOS; ORELHAS NA VB DO EIXO 9")
cx, cr = CB["contraventamento"], CB["correntes"]
K = 4                                       # vão típico com X: eixos 5–6
VAO = VAOS[K]
q = [VAO / 4, VAO / 2, 3 * VAO / 4]
ORE = dict(s=140, y=140, larg=60, t=9.5, h_baixo=80, h_alto=120)        # orelhas da CH-T2
Z0T = 10                                     # fundo da terça acima do concreto

# ------------------------------------------------------------------ PLANTA DO VÃO TÍPICO 1:100 (papel: horizontal = x da obra)
v = pr.vista("PLANTA", (64, 676), 100, titulo="PLANTA DE TRAVAMENTO — VÃO ENTRE OS EIXOS 5 E 6 (TÍPICO DOS VÃOS COM X)",
             subtitulo="X nos vãos 4-5 a 8-9 (painéis de 8 e 7 terças); vãos 1-2 a 3-4 iguais, sem o X e sem os furos X das terças")
for y in (0, VAO):
    v.ret(X0E, y - 200, LTS, 400, "VISTA"); v.ret(X0D, y - 200, LTS, 400, "VISTA")
    v.ret(-300, y - 200, 600, 400, "CORTADO"); v.ret(X_E - 300, y - 200, 600, 400, "CORTADO"); v.ret(X_C - 200, y - 300, 400, 600, "CORTADO")
for i, x in enumerate(XT):
    v.linha((x - B_TERCA, -A_TR), (x - B_TERCA, VAO + A_TR), "METALICA"); v.linha((x + B_INF, -A_TR), (x + B_INF, VAO + A_TR), "METALICA")
    for y in (-A_TR, VAO + A_TR):
        v.linha((x - B_TERCA, y), (x + B_INF, y), "METALICA")
    xp, yp = v.P((x + 42, VAO + 900 + (i % 2) * 650))
    v.texto((x + 42, VAO + 650 + (i % 2) * 650), marca(K, i), "min", "BOTTOM_CENTER")
RUNS = [(0, 1, NT - 1, NT - 2), (NT, NT + 1, 2 * NT - 1, 2 * NT - 2)]
for (p0, p1, p12, p11) in RUNS:
    for yq in q:
        v.linha((XT[p1], yq), (XT[p11], yq), "INDICACAO")
        v.linha((XT[p0], yq), (XT[p1], yq), "METALICA"); v.linha((XT[p11], yq), (XT[p12], yq), "METALICA")
    for (pa, pb) in ((p0, p1), (p12, p11)):
        for (yq, ys) in ((q[0], 0), (q[1] - 60, 0), (q[1] + 60, VAO), (q[2], VAO)):
            v.linha((XT[pb], yq), (XT[pa], ys), "OCULTA")
for nos in (NOS_X, NOS_X_D):
    for a, b in zip(nos[:-1], nos[1:]):
        v.linha((a + ORE["s"], ORE["y"]), (b - ORE["s"], VAO - ORE["y"]), "ARMADURA")
        v.linha((b - ORE["s"], ORE["y"]), (a + ORE["s"], VAO - ORE["y"]), "ARMADURA")
        for t_ in (0.3, 0.7):                                                   # esticadores (um por diagonal)
            for (x1, y1, x2, y2) in ((a + ORE["s"], ORE["y"], b - ORE["s"], VAO - ORE["y"]), (b - ORE["s"], ORE["y"], a + ORE["s"], VAO - ORE["y"])):
                if (t_ == 0.3) == (x2 > x1):
                    v.ret(x1 + t_ * (x2 - x1) - 100, y1 + t_ * (y2 - y1) - 100, 200, 200, "METALICA")
for lbl, x in (("A", 0), ("C", X_C), ("E", X_E)):
    v.eixo((x, -2100), (x, VAO + 600), 0)
    xp, yp = v.P((x, -2500)); v._add(pr.msp.add_circle((xp, yp), 3.2, dxfattribs={"layer": "INDICACAO"})); v._add(pr.texto(xp, yp, lbl, "sub", "TITULO", "MIDDLE_CENTER"))
for n, y in (("2", 0), ("3", VAO)):
    v.eixo((-3000, y), (X_E + 900, y), 0)
    xp, yp = v.P((-3300, y)); v._add(pr.msp.add_circle((xp, yp), 3.2, dxfattribs={"layer": "INDICACAO"})); v._add(pr.texto(xp, yp, n, "sub", "TITULO", "MIDDLE_CENTER"))
v.cota_v([0, q[0], q[1], q[2], VAO], -900, -14, total=False)
v.cota_h(XT[:NT], -900, -8, total=False)
v.cota_h(XT[NT:], -900, -8, total=False)
v.cota_h([0, X_C, X_E], -900, -16, total=False)
v.chamada((NOS_X_D[1] + 0.8 * (NOS_X_D[2] - NOS_X_D[1]), VAO * 0.2), (40, -24), f"X Ø16 + esticador, L ≈ {f(cx['L_diag_m'],2)} m (det. 4 e 5)")
_p = v.P((XT[NT + 3], ORE["y"] + 3 / 8 * (VAO - 2 * ORE["y"])))
v.chamada((XT[NT + 3], ORE["y"] + 3 / 8 * (VAO - 2 * ORE["y"])), (30, v.P((0, VAO + 1300))[1] + 4 - _p[1]), "furos oblongos do X nas terças X1..X7 / Y1..Y6 (det. 8)")
v.chamada((XT[2 * NT - 1], q[2] + (VAO - q[2]) * 0.3), (16, -4), "tirante rígido L 51×51×3,2 (det. 6)")
v.chamada(((XT[2 * NT - 2] + XT[2 * NT - 1]) / 2, q[2] + (VAO - q[2]) * 0.5), (16, 12), "diagonal de ancoragem Ø16 (det. 6 e 7)")
_p = v.P(((XT[NT + 7] + XT[NT + 8]) / 2, q[0]))
v.chamada(((XT[NT + 7] + XT[NT + 8]) / 2, q[0]), (v.P((X_E, 0))[0] + 16 - _p[0], -4), "corrente flexível Ø10 (det. 6)")
v.chamada((XT[2 * NT - 1] + B_INF, VAO + A_TR), (16, 20), f"terça Z 302 contínua: passa {A_TR} além de cada eixo (transpasse — COB01 det. 1)")
v.marcador_detalhe((NOS_X[1], 0), 450, 4, ang=60, dist=10)
v.marcador_detalhe((XT[1], q[0]), 450, 6, ang=-70, dist=8)
v.marcador_detalhe((XT[0], 0), 400, 7, ang=-150, dist=6)
v.marcador_detalhe((XT[3], q[1]), 400, 8, ang=110, dist=6)

# ------------------------------------------------------------------ DETALHE 4 — FIXAÇÃO DO TIRANTE NA CH-T2 (planta 1:5) + CORTE C-C
d4 = pr.vista("DETALHE 4", (108, 470), 5, titulo="DETALHE 4 — FIXAÇÃO DO X NAS ORELHAS OR-X", subtitulo="planta no topo da viga, nó do contraventamento (sem solda)")
d4.ret(-260, -200, 520, 400, "VISTA")                                         # topo da viga (400)
d4.chapa(-150, -110, 150, 220, 0.3)                                           # ST-1P (aba horizontal)
for yy in (-60, 60):
    d4.circulo((-75, yy), 8, "METALICA")                                       # ES-1
d4.poli([(-B_TERCA, -210), (B_INF, -210), (B_INF, 210), (-B_TERCA, 210)], "METALICA", True)      # 2 Z no transpasse
d4.linha((0, -210), (0, 210), "OCULTA")
ang = math.radians(cx["ang_graus"])
ux, uy = math.cos(ang), math.sin(ang)
for (ss, sy) in ((1, 1), (-1, -1), (-1, 1), (1, -1)):
    cxo, cyo = ss * ORE["s"], sy * ORE["y"]
    dx, dy = ss * ux, sy * uy                                                 # direção do tirante saindo do nó
    px, py = -dy, dx
    w, t = ORE["larg"] / 2, ORE["t"]
    pts = [(cxo + px * w, cyo + py * w), (cxo - px * w, cyo - py * w), (cxo - px * w + dx * t, cyo - py * w + dy * t), (cxo + px * w + dx * t, cyo + py * w + dy * t)]
    d4.poli(pts, "METALICA", True); d4.hachura(pts, "ANSI31", 0.2, "METALICA")
    d4.circulo((cxo - dx * 45, cyo - dy * 45), 8, "METALICA")                  # ES-2 na aba horizontal do OR-X
    d4.linha((cxo - dx * 40, cyo - dy * 40), (cxo + dx * 150, cyo + dy * 150), "ARMADURA")
    d4.ret(cxo - dx * 14 - 6, cyo - dy * 14 - 6, 12, 12, "METALICA")      # porcas (atrás da orelha)
d4.cota_h([-ORE["s"], -B_TERCA, 0, B_INF, ORE["s"]], -200, -10, total=False)
d4.cota_v([-ORE["y"], 0, ORE["y"]], 260, 8, total=False)
d4.chamada((ORE["s"], ORE["y"]), (16, 26), "OR-X L 102×76×6,3 na ES-2")
d4.chamada((-ORE["s"] - 14 * ux, -ORE["y"] - 14 * uy), (6, -22), "arruela + porca + contraporca")
d4.chamada((ORE["s"] + 120 * ux, -ORE["y"] - 120 * uy), (10, -8), f"X Ø16 a {cx['ang_graus']:.0f}° do eixo da viga")
d4.chamada((-120, 80), (4, 40), "ST-1P nas esperas ES-1 (ND-LET-COB01)")

c4 = pr.vista("CORTE C-C", (258, 470), 5, titulo="CORTE C-C — PELA ORELHA OR-X", subtitulo="orelhas: baixa (45) e alta (85)")
c4.ret(-160, -60, 320, 60, "CORTADO"); c4.hachura([(-160, -60), (160, -60), (160, 0), (-160, 0)], "AR-CONC", 0.03)
c4.chapa(-150, -12.5, 300, 12.5, 0.2)
c4.chapa(-120, 0, 76, 6.3, 0.25); c4.chapa(-50.3, 0, 6.3, 102, 0.25)                # OR-X (L 102×76×6,3)
c4.ret(-90, -110, 16, 165, "METALICA"); c4.ret(-95, 6.3, 26, 14, "METALICA")            # ES-2 + porca
c4.circulo((-47, 45), 9, "METALICA"); c4.circulo((-47, 85), 9, "METALICA")
c4.cota_v([0, 45, 85, 102], -130, -8, total=False)
c4.chamada((-82, -60), (54, -10), "ES-2 M16, hef 110 + grampo U Ø10")
c4.chamada((-47, 85), (12, 12), "2 furos Ø18: X '/' a 45 e X '\\' a 85 do concreto")
c4.chamada((-82, 20), (50, 10), "porca M16 + arruela; OR-X apoiada no concreto")

# ------------------------------------------------------------------ DETALHE 5 — TIRANTE Ø16 COM ESTICADOR (1:10, comprimento fora de escala)
d5 = pr.vista("DETALHE 5", (430, 540), 10, titulo="DETALHE 5 — TIRANTE DO X Ø16 COM ESTICADOR",
              subtitulo="trechos A e B unidos por esticador M16; comprimento fora de escala")
R = 8
d5.chapa(-10, -40, 10, 80, 0.25); d5.chapa(2390, -40, 10, 80, 0.25)                       # orelhas das duas pontas
d5.ret(0, -R, 700, 2 * R, "ARMADURA"); d5.interrupcao((700, 0), (900, 0), "ARMADURA"); d5.ret(900, -R, 500, 2 * R, "ARMADURA")
d5.ret(1400, -18, 200, 36, "METALICA"); d5.ret(1420, -12, 160, 24, "VISTA")                # esticador (corpo aberto)
d5.ret(1600, -R, 400, 2 * R, "ARMADURA"); d5.interrupcao((2000, 0), (2100, 0), "ARMADURA"); d5.ret(2100, -R, 290, 2 * R, "ARMADURA")
for x in (-36, -22, 2412, 2426):
    d5.ret(x - 6, -14, 12, 28, "METALICA")                                                 # porca + contraporca
d5.cota_h([-60, 0, 120], -R, -10, total=False); d5.cota_h([1400, 1600], -18, -10, total=False); d5.cota_h([2280, 2400, 2460], -R, -10, total=False)
d5.texto((450, 60), "trecho A", "nota", "BOTTOM_CENTER"); d5.texto((2000, 60), "trecho B", "nota", "BOTTOM_CENTER")
d5.chamada((60, R), (-4, 16), "rosca M16 120, porca + contraporca + arruela")
d5.chamada((1500, 18), (6, 14), "esticador M16 forjado galvanizado (corpo 200), rosca direita/esquerda")

# ------------------------------------------------------------------ DETALHE 6 — TRAVAMENTO DAS TERÇAS (planta 1:10) + CORTE D-D (1:5)
d6 = pr.vista("DETALHE 6", (66, 210), 15, titulo="DETALHE 6 — TRAVAMENTO DAS TERÇAS", subtitulo="planta; 1º espaço da meia água (1ª e 2ª terça), linha L/4")
for x in (0, PASSO):
    d6.ret(x, -350, 3, 700, "METALICA"); d6.ret(x, -350, B_TERCA, 3, "METALICA"); d6.linha((x + B_TERCA, -350), (x + B_TERCA, 350), "OCULTA")
d6.linha((PASSO + 3, 0), (PASSO + 300, 0), "ARMADURA"); d6.interrupcao((PASSO + 300, 0), (PASSO + 400, 0), "ARMADURA")
d6.ret(-40, -16, 40, 32, "METALICA")                                                       # clipe na 1ª terça (lado de fora? lado de dentro)
d6.ret(3, -16, 40, 32, "METALICA"); d6.ret(PASSO - 40, -16, 40, 32, "METALICA")            # clipes L 32×32×3 (aba saliente)
d6.ret(43, -25, PASSO - 83, 51, "METALICA"); d6.linha((43, 0), (PASSO - 40, 0), "OCULTA")  # L 51×51×3,2
for x in (PASSO + 3 + 8, PASSO + 3 + 22, PASSO - 46, PASSO - 60):
    d6.ret(x - 5, -12, 10, 24, "METALICA")
dg = (-PASSO * 0.0, -350)
d6.linha((PASSO, 40), (0 + 40, -350 + 20), "ARMADURA")
d6.ret(PASSO - 30, 40, 30, 30, "METALICA")
d6.cota_h([0, 43, PASSO - 40, PASSO], -350, -10, total=False)
d6.chamada(((43 + PASSO - 40) / 2, 25), (4, 24), f"tirante rígido L 51×51×3,2, L = {PASSO - 83}")
d6.chamada((PASSO + 200, 0), (6, 16), "corrente Ø10")
d6.chamada((PASSO - 15, 55), (12, 26), "calço biselado")
d6.chamada((PASSO * 0.5, -150), (14, -34), "diagonal Ø16 → ST-1P (det. 7)")
d6.chamada((3, -300), (4, -10), "1ª terça")
d6.chamada((PASSO + 3, -300), (6, -6), "2ª terça (D)")
d6.marcador_corte((PASSO - 25, -160), (PASSO - 25, 160), "D", lado=-1)

c6 = pr.vista("CORTE D-D", (260, 200), 5, titulo="CORTE D-D", subtitulo="clipe do tirante rígido na alma da terça")
C45 = math.cos(math.radians(45))
u = [(B_INF - D_INF * C45, D_INF * C45), (B_INF, 0), (0, 0), (0, H_TERCA), (-B_TERCA, H_TERCA), (-B_TERCA + D_SUP * C45, H_TERCA - D_SUP * C45)]
c6.poli(u, "METALICA")
c6.chapa(-3, Z_COR - 50, 3, 100, 0.2); c6.chapa(-35, Z_COR - 50, 32, 3, 0.2)                # clipe L 32×32×3 (aba na alma e aba saliente)
c6.circulo((0, Z_COR), 6, "METALICA")
c6.ret(-30, Z_COR + 15, 25, 25, "OCULTA")
c6.circulo((0, Z_DIAG), 9, "METALICA")
c6.cota_v([0, Z_COR - 50, Z_COR, Z_COR + 50, Z_DIAG, H_TERCA], -B_TERCA, -10, total=False)
c6.chamada((-3, Z_COR + 30), (24, 30), "clipe L 32×32×3 L 100, furo oval 11×23")
c6.chamada((0, Z_COR), (24, -12), "furo Ø12 (corrente M10)")
c6.chamada((0, Z_DIAG), (34, 8), "furo Ø18 (diagonal, só marcas D)")

# ------------------------------------------------------------------ DETALHE 7 — DIAGONAL DE ANCORAGEM NO ST-1 (planta 1:10)
d7 = pr.vista("DETALHE 7", (420, 225), 10, titulo="DETALHE 7 — DIAGONAL NO SUPORTE ST-1P", subtitulo="planta no topo da viga; 1ª terça das pontas de meia água")
d7.ret(-200, -600, 400, 1200, "VISTA")
d7.chapa(-100, -100, 200, 200, 0.2)
d7.chapa(-8, -110, 8, 220, 0.3)
d7.poli([(-B_TERCA, -600), (B_INF, -600), (B_INF, 600), (-B_TERCA, 600)], "METALICA", True)      # 1ª terça (transpasse no apoio)
d7.linha((0, -600), (0, 600), "OCULTA")
d7.linha((-8, 0), (-8 - 330, 540), "ARMADURA"); d7.linha((-8, 0), (-8 - 200, -560), "ARMADURA")
d7.ret(-60, -14, 24, 28, "METALICA"); d7.ret(-36, -18, 28, 36, "METALICA")
d7.chamada((-8 - 250, 410), (50, 14), "diagonal Ø16 (a/4) da 2ª terça")
d7.chamada((-8 - 150, -420), (42, -10), "diagonal Ø16 (a/2) do vão vizinho")
d7.chamada((-30, 0), (36, 14), "calço biselado + 2 porcas")
d7.cota_h([-200, -8, B_INF, 200], -600, -10, total=False)

# ------------------------------------------------------------------ DETALHE 8 — CRUZAMENTO DO X NA TERÇA (elevação 1:5)
d8 = pr.vista("DETALHE 8", (660, 220), 5, titulo="DETALHE 8 — PASSAGEM DO X PELA TERÇA",
              subtitulo="terças X1..X7 e Y1..Y6; posições y na tabela da COB01")
d8.ret(-400, 0, 800, H_TERCA, "METALICA"); d8.linha((-400, D_INF), (400, D_INF), "OCULTA"); d8.linha((-400, H_TERCA - D_SUP), (400, H_TERCA - D_SUP), "OCULTA")
for z, xx in ((Z_X[0], -150), (Z_X[1], 150)):
    d8.linha((xx - 5, z - 9), (xx + 5, z - 9), "METALICA"); d8.linha((xx - 5, z + 9), (xx + 5, z + 9), "METALICA")
    d8.circulo((xx - 5, z), 9, "METALICA"); d8.circulo((xx + 5, z), 9, "METALICA"); d8.circulo((xx, z), 8, "ARMADURA")
    d8.linha((xx - 120, z - 30), (xx + 120, z + 30), "ARMADURA")
d8.linha((-400, Z_COR), (-60, Z_COR), "OCULTA"); d8.linha((60, Z_COR), (400, Z_COR), "OCULTA"); d8.circulo((0, Z_COR), 6, "METALICA")
d8.cota_v([0, Z_X[0], Z_X[1], Z_COR, H_TERCA], 400, 10, total=False)
d8.cota_h([-164, -136], Z_X[0] - 9, -8, total=False)
d8.chamada((-150, Z_X[0]), (-20, -14), f"X '/': oblongo 18×28 a {Z_X[0]} do fundo")
d8.chamada((150, Z_X[1]), (-10, (H_TERCA - Z_X[1]) / 5 + 10), f"X '\\': oblongo 18×28 a {Z_X[1]} do fundo")
d8.chamada((0, Z_COR), (-24, 6), f"corrente L/2 (Ø12, {Z_COR})")

# ------------------------------------------------------------------ LISTA DE MATERIAIS DO TRAVAMENTO
x0, y = pr.quadro[2] - 196, pr.quadro[3] - 6
W = dict(r10=0.617, r16=1.578, L51=2.46)
lin = []
n_half = 2
D_COR = cr["flexivel"]["d_mm"]                                   # corrente flexível (calc_cobertura_metalica.py)
xs = {}
for t_ in LG["contraventamento"]["tirantes"]:
    Lx = round(t_["comp_m"] * 1000)
    xs.setdefault(Lx, set()).add(t_["vao"].replace("L", ""))
pos = 1
nx_tot = 0
for Lx, vs in sorted(xs.items(), reverse=True):
    n = sum(1 for t_ in LG["contraventamento"]["tirantes"] if round(t_["comp_m"] * 1000) == Lx) * 2      # 2 meias águas
    nx_tot += n
    Lb = Lx + 2 * 54 - 200 + 150
    LA = 9000
    lin.append([f"X{pos}", f"{n}", "Ø16 A36", f"{LA} + {Lb - LA}", f"{n * Lb / 1000 * W['r16']:,.0f}".replace(",", "."), f"X, vãos {', '.join(sorted(vs))} (orelha a orelha {Lx})"]); pos += 1
lin.append(["ES", f"{nx_tot}", "esticador M16", "-", "-", "um por diagonal do X"])
# diagonais de ancoragem
dd = {}
for k in range(8):
    a = VAOS[k]
    for nome, d in (("a/4", math.hypot(PASSO, a / 4)), ("a/2", math.hypot(PASSO, a / 2 - 60))):
        Lr = round(d / 10) * 10 + 2 * 60
        dd.setdefault((nome, Lr), []).append(k)
pos = 1
for (nome, Lr), ks in sorted(dd.items()):
    n = 2 * 2 * n_half * len(ks)
    lin.append([f"D{pos}", f"{n}", "Ø16 A36", f"{Lr}", f"{n * Lr / 1000 * W['r16']:,.0f}".replace(",", "."), f"diagonal {nome}, vãos {', '.join(f'{k+1}-{k+2}' for k in ks)}"]); pos += 1
n_cf = 3 * 10 * n_half * 8
L_cf = PASSO + 2 * 40
lin.append(["C1", f"{n_cf}", f"Ø{D_COR:g} A36", f"{L_cf}", f"{n_cf * L_cf / 1000 * W['r10']:,.0f}".replace(",", "."), f"corrente flexível (rosca M{D_COR:g} 40 nas pontas)"])
n_tr = 3 * 2 * n_half * 8
lin.append(["R1", f"{n_tr}", "L 51×51×3,2", f"{PASSO - 83}", f"{n_tr * (PASSO - 83) / 1000 * W['L51']:,.0f}".replace(",", "."), "tirante rígido (2 furos oval 11×23)"])
lin.append(["CL", f"{2 * n_tr}", "L 32×32×3", "100", "-", "clipe do tirante rígido"])
lin.append(["OR-X", f"{2 * nx_tot}", "L 102×76×6,3", "80", "-", f"{2 * nx_tot - 8} nas TS-01 (linhas 4 a 8) + 8 na VB do eixo 9"])
lin.append(["CB", f"{4 * 2 * n_half * 8 * 2}", "CH 6,3×50×50", "-", "-", "calço biselado das diagonais"])
y = pr.tabela(x0, y, "LISTA DE MATERIAIS — TRAVAMENTO DA COBERTURA", ["POS.", "QT", "PERFIL", "COMP. (mm)", "kg", "DESCRIÇÃO"], lin, [12, 12, 28, 26, 16, 102])
notas = ["Lógica do travamento (modelo integrado r05, DEC-024): terças Z contínuas por transpasse sobre as vigas (sem mão-francesa); 3 linhas de correntes Ø10 por vão (L/4, L/2, 3L/4), contínuas na meia água; nas duas pontas de cada meia água, tirantes rígidos no 1º espaço e diagonais Ø16 do nó da corrente na 2ª terça até o ST-1 da 1ª terça; X Ø16 nos 5 vãos do pavilhão (4-5 a 8-9), painéis de 8 e 7 espaços de terças (nós nas terças 1, 9 e 16 de cada meia água, ≈ 45°), terças dos nós como escoras; 15 espaços c/1,263 m por meia água, 1ª terça com 40 cm livres no eixo A para a calha (COB03).",
         "Esperas ES-2 nos 3 nós de todas as TS-01 (marca única; sem uso nas linhas 2 e 3); no eixo 9 as orelhas ficam no eixo da VB (ES-2V, ND-LET-VB01).",
         "X: orelhas OR-X (cantoneira L 102×76×6,3) parafusadas nas esperas ES-2 com 1 M16, giradas perpendiculares ao tirante, furo Ø18 a 45 (X /) e 85 mm (X \\) do concreto; 1 orelha por diagonal (nós de ponta: 1 por lado; nó do meio: 2 por lado). As diagonais atravessam as 7 terças intermediárias do painel por furos oblongos 18×28 de fábrica (marcas X1..X7 e Y1..Y6, tabela na COB01), sem porca.",
         "Esticador a 9,0 m da ponta (trecho A); tensionar após o aperto de todas as terças, até eliminar a flecha visível da barra, sem empenar a terça. Porca + contraporca em todas as pontas.",
         "Diagonais de ancoragem: calço biselado de chapa 6,3 na alma da 2ª terça e no ST-1P, porca + contraporca. Tirante rígido preso por clipes L 32×32×3 parafusados (M10, furo oval para ajuste); a corrente flexível passa pelo clipe e pela alma da 2ª terça.",
         "Barras A36 e chapas galvanizadas a fogo; roscas laminadas; porcas classe 5. Nenhuma solda (fábrica ou obra).",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(x0, y - 4, notas, 190)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-COB02")
for a in avisos:
    if a[0] == "ERRO" or "sai do quadro" in a[1]:
        print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
