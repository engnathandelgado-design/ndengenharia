"""ND-LET-COB02 — cobertura metálica: travamento (padrão das plantas de cobertura das referências do escritório).
Planta do vão típico contraventado com marcas das terças, X de nó a nó, correntes, tirantes rígidos e diagonais de ancoragem;
detalhes: fixação do tirante na CH-T2 (orelhas), tirante Ø16 com esticador, travamento das terças (corrente flexível +
tirante rígido + diagonal), diagonal no ST-1 e cruzamento do X na terça. Lista de materiais do travamento. Metálica em mm. A1.
"""
import math
from prancha_nd import Prancha
from cob_comum import (YLmm, VAOS, X_C, X_E, LTS, X0E, X0D, XT, PASSO, NOS, NOS_D, VAOS_X, FOLGA, Z_COR, Z_DIAG, Z_X,
                       H_TERCA, B_TERCA, IDX_2A, marca, cabecalho, CB, LG, f)

pr = Prancha("A1", cabecalho("ND-LET-COB02", "05/05", "COBERTURA METÁLICA — TRAVAMENTO: CONTRAVENTAMENTO EM X, CORRENTES E DIAGONAIS"))
pr.revisao("01", pr.dados["data"], "desdobrada da COB01; correntes no meio da alma; diagonais no ST-1")
pr.revisao("02", pr.dados["data"], "X de nó a nó com esticador (sem CH-X); tirantes rígidos L 51; detalhes no padrão de referência")
cx, cr = CB["contraventamento"], CB["correntes"]
K = 1                                       # vão típico: eixos 2–3
VAO = VAOS[K]
q = [VAO / 4, VAO / 2, 3 * VAO / 4]
ORE = dict(s=140, y=140, larg=60, t=9.5, h_baixo=80, h_alto=120)        # orelhas da CH-T2
Z0T = 10                                     # fundo da terça acima do concreto

# ------------------------------------------------------------------ PLANTA DO VÃO TÍPICO 1:100 (papel: horizontal = x da obra)
v = pr.vista("PLANTA", (64, 436), 100, titulo="PLANTA DE TRAVAMENTO — VÃO ENTRE OS EIXOS 2 E 3 (TÍPICO DOS VÃOS COM X)",
             subtitulo="vãos 2-3, 4-5, 5-6 e 7-8 com X; nos demais vãos tudo igual, sem o X e sem os furos X das terças")
for y in (0, VAO):
    v.ret(X0E, y - 200, LTS, 400, "VISTA"); v.ret(X0D, y - 200, LTS, 400, "VISTA")
    v.ret(-300, y - 200, 600, 400, "CORTADO"); v.ret(X_E - 300, y - 200, 600, 400, "CORTADO"); v.ret(X_C - 200, y - 300, 400, 600, "CORTADO")
for i, x in enumerate(XT):
    v.linha((x, FOLGA), (x, VAO - FOLGA), "METALICA"); v.linha((x + B_TERCA, FOLGA), (x + B_TERCA, VAO - FOLGA), "METALICA")
    for y in (300, VAO - 300):
        v.texto((x + 200, y), "MF", "min", "MIDDLE_CENTER")
    xp, yp = v.P((x + 42, VAO + 900 + (i % 2) * 650))
    v.texto((x + 42, VAO + 650 + (i % 2) * 650), marca(K, i), "min", "BOTTOM_CENTER")
RUNS = [(0, 1, 12, 11), (13, 14, 25, 24)]
for (p0, p1, p12, p11) in RUNS:
    for yq in q:
        v.linha((XT[p1], yq), (XT[p11], yq), "INDICACAO")
        v.linha((XT[p0], yq), (XT[p1], yq), "METALICA"); v.linha((XT[p11], yq), (XT[p12], yq), "METALICA")
    for (pa, pb) in ((p0, p1), (p12, p11)):
        for (yq, ys) in ((q[0], 0), (q[1] - 60, 0), (q[1] + 60, VAO), (q[2], VAO)):
            v.linha((XT[pb], yq), (XT[pa], ys), "OCULTA")
for nos in (NOS, NOS_D):
    for a, b in zip(nos[:-1], nos[1:]):
        v.linha((a + ORE["s"], ORE["y"]), (b - ORE["s"], VAO - ORE["y"]), "ARMADURA")
        v.linha((b - ORE["s"], ORE["y"]), (a + ORE["s"], VAO - ORE["y"]), "ARMADURA")
for lbl, x in (("A", 0), ("C", X_C), ("E", X_E)):
    v.eixo((x, -2100), (x, VAO + 600), 0)
    xp, yp = v.P((x, -2500)); v._add(pr.msp.add_circle((xp, yp), 3.2, dxfattribs={"layer": "INDICACAO"})); v._add(pr.texto(xp, yp, lbl, "sub", "TITULO", "MIDDLE_CENTER"))
for n, y in (("2", 0), ("3", VAO)):
    v.eixo((-3000, y), (X_E + 900, y), 0)
    xp, yp = v.P((-3300, y)); v._add(pr.msp.add_circle((xp, yp), 3.2, dxfattribs={"layer": "INDICACAO"})); v._add(pr.texto(xp, yp, n, "sub", "TITULO", "MIDDLE_CENTER"))
v.cota_v([0, q[0], q[1], q[2], VAO], -900, -14, total=False)
v.cota_h(XT[:13], -900, -8, total=False)
v.cota_h(XT[13:], -900, -8, total=False)
v.cota_h([0, X_C, X_E], -900, -16, total=False)
v.chamada(((NOS_D[5] + NOS_D[6]) / 2, VAO * 0.25), (40, -24), f"X Ø16 + esticador, L ≈ {f(cx['L_diag_m'],2)} m (det. 4 e 5)")
v.chamada((XT[25], q[2] + (VAO - q[2]) * 0.3), (16, -4), "tirante rígido L 51×51×3,2 (det. 6)")
v.chamada(((XT[24] + XT[25]) / 2, q[2] + (VAO - q[2]) * 0.5), (16, 12), "diagonal de ancoragem Ø16 (det. 6 e 7)")
v.chamada(((XT[20] + XT[21]) / 2, q[0]), (50, -18), "corrente flexível Ø12,5 (det. 6)")
v.chamada((XT[25] + 200, VAO - 300), (16, 20), "MF = mão-francesa (ND-LET-COB01 det. 2)")
v.marcador_detalhe((NOS[3], 0), 450, 4, ang=60, dist=10)
v.marcador_detalhe((XT[1], q[0]), 450, 6, ang=-110, dist=8)
v.marcador_detalhe((XT[0], 0), 400, 7, ang=-150, dist=6)
v.marcador_detalhe((XT[3], q[1]), 400, 8, ang=110, dist=6)

# ------------------------------------------------------------------ DETALHE 4 — FIXAÇÃO DO TIRANTE NA CH-T2 (planta 1:5) + CORTE C-C
d4 = pr.vista("DETALHE 4", (108, 300), 5, titulo="DETALHE 4 — FIXAÇÃO DO X NA CH-T2", subtitulo="planta no topo da viga, nó do contraventamento")
d4.ret(-260, -200, 520, 400, "VISTA")                                         # topo da viga (400)
d4.chapa(-150, -190, 300, 380, 0.8)                                           # CH-T2 300 (ao longo da viga) × 380
d4.chapa(-8, -110, 8, 220, 0.3)                                               # ST-1
for sg in (-1, 1):
    d4.poli([(0, sg * FOLGA), (B_TERCA, sg * FOLGA), (B_TERCA, sg * 210), (0, sg * 210)], "METALICA", True)
ang = math.radians(cx["ang_graus"])
ux, uy = math.cos(ang), math.sin(ang)
for (ss, sy) in ((1, 1), (-1, -1), (-1, 1), (1, -1)):
    cxo, cyo = ss * ORE["s"], sy * ORE["y"]
    dx, dy = ss * ux, sy * uy                                                 # direção do tirante saindo do nó
    px, py = -dy, dx
    w, t = ORE["larg"] / 2, ORE["t"]
    pts = [(cxo + px * w, cyo + py * w), (cxo - px * w, cyo - py * w), (cxo - px * w + dx * t, cyo - py * w + dy * t), (cxo + px * w + dx * t, cyo + py * w + dy * t)]
    d4.poli(pts, "METALICA", True); d4.hachura(pts, "ANSI31", 0.2, "METALICA")
    d4.linha((cxo - dx * 40, cyo - dy * 40), (cxo + dx * 150, cyo + dy * 150), "ARMADURA")
    d4.ret(cxo - dx * 14 - 6, cyo - dy * 14 - 6, 12, 12, "METALICA")      # porcas (atrás da orelha)
d4.cota_h([-150, -ORE["s"], 0, B_TERCA, ORE["s"], 150], -190, -10, total=False)
d4.cota_v([-190, -ORE["y"], 0, ORE["y"], 190], 150, 10, total=False)
d4.chamada((ORE["s"], ORE["y"]), (16, 26), f"orelha chapa {str(ORE["t"]).replace(".", ",")}×{ORE['larg']}, ⊥ ao tirante; furo Ø18")
d4.chamada((-ORE["s"] - 14 * ux, -ORE["y"] - 14 * uy), (6, -22), "arruela + porca + contraporca")
d4.chamada((ORE["s"] + 120 * ux, -ORE["y"] - 120 * uy), (10, -8), f"X Ø16 a {cx['ang_graus']:.0f}° do eixo da viga")
d4.chamada((-120, 170), (-6, 20), "CH-T2 12,5×300×380")
d4.marcador_corte((ORE["s"] - 50, ORE["y"] + 60), (ORE["s"] + 50, ORE["y"] + 60), "C", lado=1)

c4 = pr.vista("CORTE C-C", (222, 300), 5, titulo="CORTE C-C", subtitulo="orelhas: baixa (45) e alta (85)")
c4.ret(-160, -60, 320, 60, "CORTADO"); c4.hachura([(-160, -60), (160, -60), (160, 0), (-160, 0)], "AR-CONC", 0.03)
c4.chapa(-150, -12.5, 300, 12.5, 0.2)
for xo, h, z in ((-70, ORE["h_baixo"], 45 + 0), (70, ORE["h_alto"], 85)):
    c4.chapa(xo - ORE["larg"] / 2, 0, ORE["larg"], h, 0.25)
    c4.circulo((xo, z), 9, "METALICA"); c4.circulo((xo, z), 8, "ARMADURA")
    c4.linha((xo - ORE["larg"] / 2, 0), (xo - ORE["larg"] / 2 - 6, 6), "METALICA"); c4.linha((xo + ORE["larg"] / 2, 0), (xo + ORE["larg"] / 2 + 6, 6), "METALICA")
c4.cota_v([0, 45, ORE["h_baixo"]], -110, -8, total=False)
c4.cota_v([0, 85, ORE["h_alto"]], 110, 8, total=False)
c4.cota_h([-100, -70, -40], ORE["h_alto"] + 10, 6, total=False)
c4.chamada((-100, 40), (-10, 12), "filete 6 mm, 3 lados (fábrica)")
c4.chamada((70, 85), (10, 12), "furo Ø18")

# ------------------------------------------------------------------ DETALHE 5 — TIRANTE Ø16 COM ESTICADOR (1:10, comprimento fora de escala)
d5 = pr.vista("DETALHE 5", (290, 330), 10, titulo="DETALHE 5 — TIRANTE DO X Ø16 COM ESTICADOR",
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
d6 = pr.vista("DETALHE 6", (66, 170), 15, titulo="DETALHE 6 — TRAVAMENTO DAS TERÇAS", subtitulo="planta; 1º espaço da meia água (1ª e 2ª terça), linha L/4")
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
d6.chamada((PASSO + 200, 0), (6, 16), "corrente Ø12,5")
d6.chamada((PASSO - 15, 55), (-30, 12), "calço biselado")
d6.chamada((PASSO * 0.5, -150), (4, -14), "diagonal Ø16 → ST-1 (det. 7)")
d6.chamada((3, -300), (4, -10), "1ª terça")
d6.chamada((PASSO + 3, -300), (6, -6), "2ª terça (D)")
d6.marcador_corte((PASSO - 25, -60), (PASSO - 25, 60), "D", lado=-1)

c6 = pr.vista("CORTE D-D", (250, 160), 5, titulo="CORTE D-D", subtitulo="clipe do tirante rígido na alma da terça")
u = [(85, 275), (85, 300), (0, 300), (0, 0), (85, 0), (85, 25)]
c6.poli(u, "METALICA")
c6.chapa(-3, Z_COR - 50, 3, 100, 0.2); c6.chapa(-35, Z_COR - 50, 32, 3, 0.2)                # clipe L 32×32×3 (aba na alma e aba saliente)
c6.circulo((0, Z_COR), 7, "METALICA")
c6.ret(-30, Z_COR + 15, 25, 25, "OCULTA")
c6.circulo((0, Z_DIAG), 9, "METALICA")
c6.cota_v([0, Z_COR - 50, Z_COR, Z_COR + 50, Z_DIAG, 300], 85, 10, total=False)
c6.chamada((-3, Z_COR + 30), (24, 30), "clipe L 32×32×3 L 100, furo oval 11×23")
c6.chamada((0, Z_COR), (24, -12), "furo Ø14 (corrente / M12)")
c6.chamada((0, Z_DIAG), (14, 8), "furo Ø18 (diagonal, só marcas D)")

# ------------------------------------------------------------------ DETALHE 7 — DIAGONAL DE ANCORAGEM NO ST-1 (planta 1:10)
d7 = pr.vista("DETALHE 7", (378, 185), 10, titulo="DETALHE 7 — DIAGONAL NO SUPORTE ST-1", subtitulo="planta no topo da viga; 1ª terça das pontas de meia água")
d7.ret(-200, -600, 400, 1200, "VISTA")
d7.chapa(-100, -100, 200, 200, 0.2)
d7.chapa(-8, -110, 8, 220, 0.3)
for sg in (-1, 1):
    d7.poli([(0, sg * FOLGA), (B_TERCA, sg * FOLGA), (B_TERCA, sg * 600), (0, sg * 600)], "METALICA", True)
d7.linha((-8, 0), (-8 - 330, 540), "ARMADURA"); d7.linha((-8, 0), (-8 - 200, -560), "ARMADURA")
d7.ret(-60, -14, 24, 28, "METALICA"); d7.ret(-36, -18, 28, 36, "METALICA")
d7.chamada((-8 - 250, 410), (30, 14), "diagonal Ø16 (a/4) da 2ª terça")
d7.chamada((-8 - 150, -420), (32, -10), "diagonal Ø16 (a/2) do vão vizinho")
d7.chamada((-30, 0), (36, 6), "calço biselado + porca + contraporca, furo Ø18 do ST-1")
d7.cota_h([-200, -8, 0, B_TERCA, 200], -600, -10, total=False)

# ------------------------------------------------------------------ DETALHE 8 — CRUZAMENTO DO X NA TERÇA (elevação 1:5)
d8 = pr.vista("DETALHE 8", (540, 180), 5, titulo="DETALHE 8 — CRUZAMENTO DO X", subtitulo="terça intermediária do painel (marca X), no meio do vão")
d8.ret(-400, 0, 800, H_TERCA, "METALICA"); d8.linha((-400, 25), (400, 25), "OCULTA"); d8.linha((-400, 275), (400, 275), "OCULTA")
for z in Z_X:
    d8.circulo((0, z), 9, "METALICA"); d8.circulo((0, z), 8, "ARMADURA")
d8.linha((-400, Z_COR), (-60, Z_COR), "OCULTA"); d8.linha((60, Z_COR), (400, Z_COR), "OCULTA"); d8.circulo((0, Z_COR), 7, "METALICA")
d8.cota_v([0, Z_X[0], Z_X[1], Z_COR, H_TERCA], 400, 10, total=False)
d8.chamada((0, Z_X[0]), (-20, -14), "X '/' (orelha baixa): furo Ø18 a 35 do fundo")
d8.chamada((0, Z_X[1]), (-20, 14), "X '\\' (orelha alta): furo Ø18 a 75 do fundo")
d8.chamada((0, Z_COR), (20, 12), "corrente L/2 (Ø14, 150)")

# ------------------------------------------------------------------ LISTA DE MATERIAIS DO TRAVAMENTO
x0, y = pr.quadro[2] - 196, pr.quadro[3] - 6
W = dict(r12=0.963, r16=1.578, L51=2.46)
lin = []
n_half = 2
# contraventamento X por vão
for k in VAOS_X:
    pass
xs = {}
for k in VAOS_X:
    Lx = round(math.hypot(2 * PASSO - 2 * ORE["s"], VAOS[k] - 2 * ORE["y"]))
    xs.setdefault(Lx, []).append(f"{k+1}-{k+2}")
pos = 1
for Lx, vs in sorted(xs.items(), reverse=True):
    n = 12 * n_half * len(vs)
    Lb = Lx + 2 * 54 - 200 + 150
    lin.append([f"X{pos}", f"{n}", "Ø16 A36", f"{9000} + {Lb - 9000}", f"{n * Lb / 1000 * W['r16']:,.0f}".replace(",", "."), f"X, vãos {', '.join(vs)} (c-c furos {Lx})"]); pos += 1
nx_tot = 12 * n_half * len(VAOS_X)
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
lin.append(["C1", f"{n_cf}", "Ø12,5 A36", f"{L_cf}", f"{n_cf * L_cf / 1000 * W['r12']:,.0f}".replace(",", "."), "corrente flexível (rosca M12 40 nas pontas)"])
n_tr = 3 * 2 * n_half * 8
lin.append(["R1", f"{n_tr}", "L 51×51×3,2", f"{PASSO - 83}", f"{n_tr * (PASSO - 83) / 1000 * W['L51']:,.0f}".replace(",", "."), "tirante rígido (2 furos oval 11×23)"])
lin.append(["CL", f"{2 * n_tr}", "L 32×32×3", "100", "-", "clipe do tirante rígido"])
lin.append(["OR", f"{4 * 7 * 2 * 7}", f"CH {ORE['t']:g}×{ORE['larg']}", f"{ORE['h_baixo']}/{ORE['h_alto']}", "-", "orelhas soldadas nas CH-T2 (fábrica)"])
lin.append(["CB", f"{4 * 2 * n_half * 8 * 2}", "CH 6,3×50×50", "-", "-", "calço biselado das diagonais"])
y = pr.tabela(x0, y, "LISTA DE MATERIAIS — TRAVAMENTO DA COBERTURA", ["POS.", "QT", "PERFIL", "COMP. (mm)", "kg", "DESCRIÇÃO"], lin, [12, 12, 28, 26, 16, 102])
notas = ["Lógica do travamento: terças apoiadas de viga a viga; 3 linhas de correntes por vão (L/4, L/2, 3L/4), contínuas na meia água; nas duas pontas de cada meia água, tirantes rígidos no 1º espaço e diagonais Ø16 do nó da corrente na 2ª terça até o ST-1 da 1ª terça; X Ø16 de nó a nó das vigas a cada 2 espaços de terças, com as terças dos nós como escoras.",
         "X: orelhas soldadas na CH-T2 (4 por nó, peça única simétrica), perpendiculares ao tirante, furo Ø18 a 45 (orelha baixa) e 85 mm (alta) do concreto; as duas diagonais cruzam-se no meio do vão, passando pelos furos Ø18 da terça intermediária (marca X), sem porca.",
         "Esticador a 9,0 m da ponta (trecho A); tensionar após o aperto de todas as terças e MF, até eliminar a flecha visível da barra, sem empenar a terça. Porca + contraporca em todas as pontas.",
         "Diagonais de ancoragem: calço biselado de chapa 6,3 na alma da 2ª terça e no ST-1, porca + contraporca. Tirante rígido preso por clipes L 32×32×3 parafusados (M10, furo oval para ajuste); a corrente flexível passa pelo clipe e pela alma da 2ª terça.",
         "Barras A36 e chapas galvanizadas a fogo; roscas laminadas; porcas classe 5. Proibido soldar na obra.",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(x0, y - 4, notas, 190)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-COB02")
for a in avisos:
    if a[0] == "ERRO" or "sai do quadro" in a[1]:
        print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
