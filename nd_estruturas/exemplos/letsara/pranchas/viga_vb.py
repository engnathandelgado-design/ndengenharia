"""ND-LET-VB01 — vigas de borda VB-01 a VB-04 (15 × 60 com dente Gerber, concreto armado C40) das fachadas 1 e 9: fôrma, armação e insertos (A1).
rev04: calc_vb_dente.py (vb_dente.json, adotado 15 × 60, dente 30, nariz 27) — consolo CP-VB escondido no recorte."""
import json
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha

f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from geometria import X_EIXO, Y_LIN as Y_LIN_R01
from cob_comum import XT, NT, IDX_NOS, ORE_S9
X_FACH = [(k, X_EIXO[k]) for k in "ABCDE"]
MEIA = {"A": 0.30, "B": 0.20, "C": 0.20, "D": 0.20, "E": 0.30}
VBD = json.load(open('/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/vb_dente.json'))['adotado']
B, H = round(VBD['b'] * 1000), round(VBD['h'] * 1000)
HD = round(VBD['hd'] * 1000)               # altura do nariz do dente
REC = H - HD                                 # recorte (consolo 290 + neoprene 10)
LN = 270                                     # comprimento do nariz
XP = 110                                     # eixo do pino PN-6 / neoprene a partir da ponta da viga (135 da face do pilar)
COB = 30
MARCAS = []
for k, ((na, xa), (nb, xb)) in enumerate(zip(X_FACH[:-1], X_FACH[1:]), 1):
    x0 = round((xa + MEIA[na] + 0.025) * 1000)                            # ponta a 25 mm da face do pilar
    L = round((xb - MEIA[nb] - 0.025) * 1000) - x0
    MARCAS.append((f"VB-0{k}", f"{na}–{nb}, fachada 1", 1, L, x0))
for k, m_ in enumerate(list(MARCAS), 5):
    MARCAS.append((f"VB-0{k}", m_[1].replace("fachada 1", "fachada 9 (espelho da " + m_[0] + ")"), 1, m_[3], m_[4]))
L, X0VB = MARCAS[1][3], MARCAS[1][4]                                         # VB-02 desenhada
TERCAS = [x - X0VB + 42 for x in XT if X0VB + 145 <= x and x - 45 <= X0VB + L - 40]   # rev06: terças com as 2 esperas dentro da VB (40 da ponta)


def esperas_marca(x0, Lm, fachada9):
    """rev06: esperas por marca (mm a partir da ponta baixa): ES-1V/ES-1R a 45 e 105 da alma de cada terça apoiada na VB;
    ES-2V (orelhas do X, só eixo 9) a ±200 da alma das terças dos nós."""
    es1, es2 = [], []
    for i, w in enumerate(XT):
        p = [w - 105 - x0, w - 45 - x0]
        if 40 <= p[0] and p[1] <= Lm - 40:
            es1 += p
        if fachada9 and (i % NT) in IDX_NOS:
            for s in (-ORE_S9, ORE_S9):
                xe = w + s - x0
                if 100 <= xe <= Lm - 100:
                    es2.append(xe)
    return [round(v) for v in es1], [round(v) for v in es2]
V = (B * H * L - 2 * B * REC * LN) / 1e9
PESO = V * 25
# rev04: Md 90,8 kN·m + tração 95,8 kN → 3 Ø16 inf.; sucção Md− 66,7 kN·m → 6 Ø10 sup.; Vd 38,5 kN; levantamento 28,3 kN (PN-6 roscado)
pr = Prancha("A1", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="VIGAS DE BORDA VB-01 A VB-08 (15×60 COM DENTE, C40) — FACHADAS 1 E 9 — FÔRMA, ARMAÇÃO E INSERTOS",
                        desenho="ND-LET-VB01", folha="01/01", fase="PARA APROVAÇÃO", marca="VB-02", qtd=1, peso=f(PESO, 1), volume=f(V, 2)))
pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL")
pr.revisao("03", "14/10/2026", "TERÇAS c/1,20 m: ESPERAS ES-1/ES-3 (SEM SOLDA); TB-1 SEM CHAPA; CARGAS COM PAINÉIS SOLARES")
pr.revisao("04", "16/10/2026", "VB 15×60 COM DENTE GERBER, CONSOLO CP-VB ESCONDIDO; NEO-6 100×100×10; PN-6 ANTI-LEVANTAMENTO")
pr.revisao("05", "17/10/2026", "TERÇAS Z CONTÍNUAS SEM MÃO-FRANCESA: RETIRADAS AS ESPERAS ES-3")
pr.revisao("06", "17/10/2026", "15 ESPAÇOS DE TERÇA; VB-05 A 08 COM ES-1R M20 + GRAMPO E ES-2V DO X; TABELA DE ESPERAS POR MARCA")
Q = pr.quadro
XC = Q[2] - 190
pr.ret(Q[0] + 4, Q[3] - 30, Q[0] + 500, Q[3] - 4, "CARIMBO")
pr.texto(Q[0] + 10, Q[3] - 24, "VB-02", "grande", "TITULO")
pr.texto(Q[0] + 62, Q[3] - 24, f"VIGA DE BORDA 15 × 60 cm COM DENTE — VB-02 (L = {L/10:.0f} cm) · VB-01 A VB-08 (VB-05 A VB-08 ESPELHADAS)", "titulo", "TITULO")
pr.texto(Q[0] + 10, Q[3] - 14, f"fachadas 1 e 9, entre os pilares de fachada; dente 30 × 27 nos consolos CP-VB (escondidos) com pino PN-6 roscado   ·   PESO {f(PESO/10, 2)} t   ·   VOLUME {f(V, 2)} m³   ·   C40, CA-50", "nota", "TEXTO")

# planta-chave
kp = pr.vista("PLANTA-CHAVE", (Q[0] + 545, Q[3] - 118), 1000, titulo="PLANTA-CHAVE", subtitulo="VB nas fachadas 1 e 9", unidade="cm")
M = lambda v: v * 1000
Y_LIN = Y_LIN_R01
for y in Y_LIN:
    kp.linha((M(-2), M(y)), (M(42), M(y)), "EIXO")
for _, x in X_FACH:
    kp.linha((M(x), M(-2)), (M(x), M(81)), "EIXO")
for i, y in enumerate(Y_LIN, 1):
    kp.texto((M(-3.5), M(y)), str(i), "min", "MIDDLE_RIGHT")
for j, (n, x) in enumerate(X_FACH):
    kp.texto((M(x), M(82)), n, "min", "BOTTOM_CENTER")
for mk, _, _, Lm, _x0 in MARCAS:
    k = (int(mk[-1]) - 1) % 4
    for y in ((0.0,) if int(mk[-1]) <= 4 else (Y_LIN[-1],)):
        kp.ret(M(X_FACH[k][1]) + 250, M(y) - 150, Lm, 300, "CORTADO")
        kp.texto((M((X_FACH[k][1] + X_FACH[k + 1][1]) / 2), M(y) + (600 if y == 0 else -600)), mk, "min", "BOTTOM_CENTER" if y == 0 else "TOP_CENTER")

# ELEVAÇÃO 1:20 (cm)
ESC = 20
import vb_geom as VG
# rev04: peça fabricada reta; na montagem (caimento 3 %) as pontas, os recortes e os tubos ficam a prumo e as faces de apoio dos
# dentes ficam horizontais (NBR 9062:2017 7.2.1.6) — no desenho da peça essas linhas aparecem inclinadas 3 %
PERF = VG.peca(L)
LU = PERF[5][0]                                                     # ponta alta, na face de apoio (u)
Tm = lambda x, z: (x * VG.C + z * VG.S, -x * VG.S + z * VG.C)       # posição montada → peça
ZB = lambda x: VG.I * x
ZT = lambda x: VG.I * x + H / VG.C
ZNL, ZNR = ZB(XP) + REC, ZB(L - XP) + REC
TUBOS = [[Tm(x + d, zn) for d in (-25, 25)] + [Tm(x + d, ZT(x) - 60) for d in (25, -25)] for x, zn in ((XP, ZNL), (L - XP, ZNR))]
NICHOS = [[Tm(x - 60, ZT(x) - 60), Tm(x + 60, ZT(x) - 60), Tm(x + 60, ZT(x)), Tm(x - 60, ZT(x))] for x in (XP, L - XP)]
ve = pr.vista("ELEVAÇÃO", (Q[0] + 40, Q[3] - 175), ESC, titulo="ELEVAÇÃO DE FÔRMA — VB-02", subtitulo="peça fabricada reta; ponta baixa à esquerda (lado A); dentes, pontas e tubos a prumo na montagem", unidade="cm")
ve.poli(PERF, "VISTA", fechada=True)
for tb_, ni_ in zip(TUBOS, NICHOS):
    ve.poli(tb_, "OCULTA", fechada=True); ve.poli(ni_, "OCULTA", fechada=True)
for s_ in TERCAS:
    for dx in (45, 105):
        ve.ret(s_ - dx - 8, H, 16, 120, "METALICA")
for s_ in (1500, L - 1500):
    ve.poli([(s_ - 60, H), (s_ - 60, H + 100), (s_, H + 140), (s_ + 60, H + 100), (s_ + 60, H)], "METALICA")
ve.cota_ord([PERF[7][0], round(Tm(XP, ZT(XP))[0])] + TERCAS + [round(Tm(L - XP, ZT(L - XP))[0]), PERF[6][0]], H + 140, 14, x0=PERF[7][0])
ve.cota_h([PERF[0][0], PERF[2][0], 1500, L - 1500, PERF[3][0], LU], 0, -10)
ve.cota_v([0, PERF[4][1], H], PERF[6][0], 10)
ve.chamada(Tm(XP, ZNL + 150), (14, -Tm(XP, ZNL + 150)[1] / ESC - 34), "TB-1 Ø50×3,0 L=240 a prumo + nicho 12×12×6 (2x)")
ve.chamada(PERF[1], (16, -PERF[1][1] / ESC - 25), "face de apoio do dente: HORIZONTAL na montagem (3 % na peça)")
ve.chamada((TERCAS[2] - 45, H + 120), (10, 34), f"ES-1V: 2 M16 no eixo por terça ({len(TERCAS)} terças, ST-1V)")
ve.chamada((1500, H + 140), (10, 34), "AL-1 alça (2x)")
ve.marcador_corte((L / 2 + 400, -22 * ESC), (L / 2 + 400, H + 24 * ESC), "A", lado=1)
ve.marcador_detalhe((LN / 2, REC), 500, 1, ang=-120, dist=8)

# ARMAÇÃO 1:20
va = pr.vista("ARMAÇÃO", (Q[0] + 40, Q[3] - 275), ESC, titulo="ELEVAÇÃO DE ARMAÇÃO — VB-02", subtitulo="igual nas 4 marcas (muda só o comprimento)", unidade="cm")
va.poli(PERF, "VISTA", fechada=True)
XN = [50, 200]                                                      # N4 no nariz (desvia do TB-1)
XS = [LN + 40, LN + 90]                                             # N6 suspensão junto ao recorte
xs_e = list(range(LN + 150, 1500, 100)) + list(range(1500, L - 1500, 150)) + list(range(L - 1500, L - LN - 140, 100))
for x in xs_e:
    va.linha((x, COB), (x, H - COB), "ARM_TRANSV")
for x0 in (0, L):
    sg = 1 if x0 == 0 else -1
    for x in XN:
        va.linha((x0 + sg * x, REC + COB), (x0 + sg * x, H - COB), "ARM_TRANSV")
    for x in XS:
        va.linha((x0 + sg * x, COB), (x0 + sg * x, H - COB), "ARMADURA")
    va.poli([(x0 + sg * COB, REC + COB + 20), (x0 + sg * (LN + 430), REC + COB + 20)], "ARMADURA")
    for k in (1, 2):
        yk = REC + COB + 20 + k * 70
        va.poli([(x0 + sg * COB, yk), (x0 + sg * (LN + 300), yk)], "ARM_TRANSV")
Lb1 = L - 2 * LN - 2 * COB
va.barra([(LN + COB, COB + 200), (LN + COB, COB + 10), (L - LN - COB, COB + 10), (L - LN - COB, COB + 200)], "N1", 3, 16.0, comp_cm=round((Lb1 + 400) / 10), ponto_rotulo=(L / 3, COB + 10), desloc=(10, -14))
va.barra([(COB, H - COB - 200), (COB, H - COB - 10), (L - COB, H - COB - 10), (L - COB, H - COB - 200)], "N2", 6, 10.0, comp_cm=round((L - 2 * COB + 400) / 10), ponto_rotulo=(L / 3, H - COB - 10), desloc=(10, 14))
va.chamada((L / 2, H - COB), (10, 16), f"N3 — {len(xs_e)} estribos Ø6,3: c/15 corrente, c/10 até 150 cm das pontas")
va.chamada((L - XN[1], REC + 150), (-40, 16), "N4 — 2 estribos Ø6,3 no nariz (por ponta)")
va.chamada((XS[1], 150), (14, 14), "N6 — 2 estribos fechados Ø10 de suspensão (por ponta)")
va.chamada((LN + 300, REC + COB + 20), (14, -12), "N5 — 1 alça horizontal Ø10 (tirante do dente)")
va.chamada((LN + 200, REC + COB + 160), (16, 10), "N7 — 2 alças horizontais Ø6,3 (costura)")
va.cota_h([0, LN, 1500, L - 1500, L - LN, L], 0, -10)
pr.posicoes_desenho.update({"N3", "N4", "N5", "N6", "N7"})

# CORTE A-A 1:10 e DETALHE 1 (ponta) 1:10
YR = Q[3] - 455
ca = pr.vista("CORTE A-A", (Q[0] + 60, YR), 10, titulo="CORTE A-A", subtitulo="seção corrente; cobrimento 3,0 cm", unidade="cm")
pts = [(-B / 2, 0), (B / 2, 0), (B / 2, H), (-B / 2, H)]
ca.poli(pts, "CORTADO", fechada=True); ca.hachura(pts, "AR-CONC", 0.03)
ca.poli([(-B / 2 + COB, COB), (B / 2 - COB, COB), (B / 2 - COB, H - COB), (-B / 2 + COB, H - COB)], "ARM_TRANSV", fechada=True)
xi = -B / 2 + COB + 6.3 + 8
for x in (xi, -xi):
    ca.ponto_barra((x, COB + 6.3 + 8), 16)
ca.ponto_barra((xi, COB + 6.3 + 8 + 36), 16)
for x in (-B / 2 + COB + 6.3 + 5, 0, B / 2 - COB - 6.3 - 5):
    ca.ponto_barra((x, H - COB - 6.3 - 5), 10); ca.ponto_barra((x, H - COB - 6.3 - 5 - 30), 10)
ca.ret(-8, H - 150, 16, 270, "METALICA")
ca.poli([(-8, H - 150), (-8, H - 170), (52, H - 170)], "METALICA")
ca.cota_h([-B / 2, B / 2], 0, -10); ca.cota_v([0, H], B / 2, 10)
ca.chamada((B / 2 - COB - 11, H - COB - 11), (14, 12), "N2 — 6 Ø10 (2 camadas de 3)")
ca.chamada((-xi, COB + 14), (14, -12), "N1 — 3 Ø16 (2 + 1)")
ca.chamada((B / 2 - COB, 300), (14, -6), "N3 Ø6,3 c/15")
ca.chamada((0, H + 60), (14, 14), "ES-1V M16 hef 150 + gancho, saliência 120 (no eixo)")

d1 = pr.vista("DETALHE 1", (Q[0] + 300, YR - 10), 10, titulo="DETALHE 1 — DENTE NO CONSOLO CP-VB (POSIÇÃO MONTADA)", subtitulo="ponta baixa; viga a 3 %; face de apoio e topo do consolo horizontais; PN-6 com porca", unidade="cm")
LD = 1100
FP = -25                                                            # face do pilar (folga 2,5 cm)
Rp = lambda u, v: (u * VG.C - v * VG.S, u * VG.S + v * VG.C)       # peça → posição montada
CT = ZNL - 10                                                       # topo horizontal do CP-VB
d1.poli([(FP - 300, -150), (FP, -150), (FP, H + 150), (FP - 300, H + 150)], "VISTA", fechada=True)
d1.interrupcao((FP - 300, -150), (FP - 300, H + 150))
cons = [(FP, CT - 290), (FP + 270, CT - 290), (FP + 270, CT), (FP, CT)]
d1.poli(cons, "CORTADO", fechada=True); d1.hachura(cons, "AR-CONC", 0.03)
d1.chapa(XP - 50, CT, 100, 10)
d1.poli([(0, ZNL), (LN, ZNL), (LN, ZB(LN)), (LD, ZB(LD)), (LD, ZT(LD)), (0, ZT(0))], "VISTA", fechada=True); d1.interrupcao((LD, ZB(LD)), (LD, ZT(LD)))
d1.ret(XP - 25, ZNL, 50, ZT(XP) - 60 - ZNL, "OCULTA"); d1.ret(XP - 60, ZT(XP) - 60, 120, 60, "OCULTA")
d1.poli([(XP - 10, CT - 300), (XP - 10, ZT(XP) - 25), (XP + 10, ZT(XP) - 25), (XP + 10, CT - 300)], "METALICA")
d1.chapa(XP - 30, ZT(XP) - 31, 60, 6)
pl = lambda pts, cam: d1.poli([Rp(u, v) for u, v in pts], cam)
for x in XN:
    pl([(x, REC + COB), (x, H - COB)], "ARM_TRANSV")
for x in XS:
    pl([(x, COB), (x, H - COB)], "ARMADURA")
for x in range(LN + 150, LD, 100):
    pl([(x, COB), (x, H - COB)], "ARM_TRANSV")
pl([(COB, REC + COB + 20), (LD, REC + COB + 20)], "ARMADURA")
pl([(LN + COB, COB + 200), (LN + COB, COB + 10), (LD, COB + 10)], "ARMADURA")
pl([(COB, H - COB - 200), (COB, H - COB - 10), (LD, H - COB - 10)], "ARMADURA")
d1.cota_h([FP, 0, XP, LN, LD], ZT(LD) + 150, 12, total=False)
d1.cota_v([CT - 290, CT, ZNL], FP + 270, -14, total=False)
d1.cota_h([FP, FP + 270], CT - 290, -12, total=False)
d1.chamada((XP, ZT(XP) - 30), (40, 48), "PN-6 Ø20 roscado A36 L=700 (300 no consolo) + porca, contraporca e arruela 60×60×6; nicho grauteado")
d1.chamada((XP, CT + 5), (-62, 30), "NEO-6 100×100×10 (furo Ø30) horizontal")
d1.chamada((FP + 200, CT - 170), (60, -30), "CP-VB 15 × 27 × 29, topo HORIZONTAL (ver prancha do pilar)")
d1.chamada(Rp(LN, REC + COB + 20), (14, 10), "N5 alça Ø10 (tirante)")
d1.chamada(Rp(XS[0], 150), (70, -16), "N6 suspensão 2 Ø10")
d1.chamada(Rp(LN + COB, COB + 100), (12, 14), "N1 com gancho de 20 cm no recorte")

# isométricos (iso3d_vigas.py) — rev08
pr.imagem(540, 172, 985, 240, "/home/claude/letsara/pranchas/ISO-VB-geral.png", titulo="ISOMÉTRICO — VB-02",
          subtitulo="dentes, esperas ES-1V das terças, alças AL-1, TB-1 + nicho")
pr.imagem(560, 88, 760, 150, "/home/claude/letsara/pranchas/ISO-VB-ponta.png", titulo="ISOMÉTRICO — PONTA NO CP-VB",
          subtitulo="consolo escondido no recorte, NEO-6, PN-6 com porca")

# tabelas
y = Q[3] - 6
y = pr.tabela(XC, y, "MARCAS — VIGAS DE BORDA 15×60 COM DENTE", ["MARCA", "POSIÇÃO", "QT", "L (cm)", "PESO (t)"], [[m, p, q, f"{Lm/10:.0f}", f((B * H * Lm - 2 * B * REC * LN) / 1e9 * 25 / 10, 2)] for m, p, q, Lm, _x in MARCAS], [18, 70, 10, 24, 24])
Lb = round((L - 2 * COB) / 10)
L1 = round(Lb1 / 10)
he, hn = round((H - 2 * COB) / 10), round((HD - 2 * COB) / 10)
barras = [dict(pos="N1", diam=16.0, qtd=3, comp=L1 + 40, forma=[(0, 20), (0, 0), (L1, 0), (L1, 20)], trechos=["20", f"{L1}", "20"]),
          dict(pos="N2", diam=10.0, qtd=6, comp=Lb + 40, forma=[(0, 0), (0, 20), (Lb, 20), (Lb, 0)], trechos=["20", f"{Lb}", "20"]),
          dict(pos="N3", diam=6.3, qtd=len(xs_e), comp=round((2 * (he + 9) + 12)), forma=[(0, 0), (9, 0), (9, he), (0, he), (0, 0), (2, 2)], trechos=["9", f"{he}", "", ""]),
          dict(pos="N4", diam=6.3, qtd=4, comp=round((2 * (hn + 9) + 12)), forma=[(0, 0), (9, 0), (9, hn), (0, hn), (0, 0), (2, 2)], trechos=["9", f"{hn}", "", ""]),
          dict(pos="N5", diam=10.0, qtd=2, comp=2 * 70 + 8, forma=[(70, 0), (0, 0), (0, 8), (70, 8)], trechos=["70", "8", "70"]),
          dict(pos="N6", diam=10.0, qtd=4, comp=round((2 * (he + 8) + 16)), forma=[(0, 0), (8, 0), (8, he), (0, he), (0, 0), (2, 2)], trechos=["8", f"{he}", "", ""]),
          dict(pos="N7", diam=6.3, qtd=4, comp=2 * 55 + 8, forma=[(55, 0), (0, 0), (0, 8), (55, 8)], trechos=["55", "8", "55"])]
ta = pr.tabela_croqui(XC, y - 4, barras, h_lin=9.0)
y = ta["y_base"]
tabE = []
for m_, p_, q_, Lm_, x0_ in MARCAS:
    e1, e2 = esperas_marca(x0_, Lm_, "fachada 9" in p_)
    ts_ = [round((e1[k] + e1[k + 1]) / 2 + 75) for k in range(0, len(e1), 2)]          # alma da terça a partir da ponta
    tabE.append([m_, "ES-1R M20" if "fachada 9" in p_ else "ES-1V M16", f"{len(ts_)}", f"{ts_[0]/10:.1f}".replace(".", ","), f"{(ts_[1]-ts_[0])/10:.1f}".replace(".", ","),
                 (" · ".join(f"{v/10:.1f}".replace(".", ",") for v in e2)) or "—"])
y = pr.tabela(XC, y - 4, "ESPERAS NO TOPO POR MARCA (cm, da ponta baixa; par a 4,5/10,5 antes da alma)", ["MARCA", "ESPERA", "TERÇAS", "1ª ALMA", "PASSO", "ES-2V (X)"], tabE, [16, 26, 16, 18, 16, 90], h_lin=5.0)
ins = [["TB-1", "Tubo Ø50×3,0 L=240 no nariz + nicho 120×120×60", 2, "a 110 das pontas"],
       ["ES-1V", "VB-01 a 04: 2 M16 L=330 c/ gancho por terça", 2 * len(TERCAS), "topo, a 45/105 da terça"],
       ["ES-1R", "VB-05 a 08: 2 M20 L=520 gancho + grampo U Ø10", 2 * len(TERCAS), "topo, a 45/105 da terça"],
       ["ES-2V", "VB-05 a 08: M16 L=220 gancho + grampo (OR-X)", "tab.", "eixo, ±200 da terça do nó"],
       ["AL-1", "Laço de cordoalha Ø12,7 (2 pernas)", 2, "a 150 cm das pontas"],
       ["NEO-6", "Neoprene 100×100×10 (furo Ø30)", 2, "sobre os consolos CP-VB"],
       ["PN-6", "Porca, contraporca e arruela 60×60×6 do PN-6", 2, "no nicho do TB-1"]]
y = pr.tabela(XC, y - 4, "INSERTOS POR PEÇA (VB-02) — dimensões em mm", ["MARCA", "DESCRIÇÃO", "QT", "POSIÇÃO"], ins, [16, 104, 10, 52])
qd = [["MARCA", "VB-02", "SEÇÃO", "15 × 60 cm, dente 30"], ["COMPRIMENTO", f"{L/10:.0f} cm", "CONCRETO", "C40"], ["VOLUME", f"{f(V, 2)} m³", "PESO", f"{f(PESO/10, 2)} t"],
      ["AÇO CA-50", f"{f(ta['total_kg'], 0)} kg", "TAXA", f"{f(ta['total_kg'] / V, 0)} kg/m³"], ["QUANTIDADE", "1 (família: 8)", "COBRIMENTO", "3,0 cm (CAA II)"]]
pr.tabela(Q[0] + 330, Q[3] - 308, "QUADRO DA PEÇA", ["ITEM", "VALOR", "ITEM", "VALOR"], qd, [30, 62, 30, 60])
notas = ["Concreto C40 (fcj 25 MPa para desformar e içar), aço CA-50; cobrimento 3,0 cm (CAA II). N1 com gancho de 20 cm junto ao recorte; N2 com dobra de 20 cm nas pontas.",
         "Topo da VB alinhado com o topo das TS-01: as terças do vão de oitão apoiam na VB pelo ST-1V (= ST-1P com os 2 furos oblongos no eixo, VB de 15 cm) parafusado nas esperas ES-1V, com 4 M12 8.8 na alma da terça Z (sem mão-francesa) — ND-LET-COB01. Nenhuma solda.",
         "Dente Gerber 30 × 27 nas duas pontas (NBR 9062:2017 7.4): o consolo CP-VB (15 × 27 × 29) fica escondido no recorte. A VB sobe 3 % (de A para E): na montagem as pontas, as faces dos recortes e os tubos TB-1 ficam a prumo e a face de apoio de cada dente fica horizontal, sobre o neoprene e o topo horizontal do consolo (NBR 9062:2017 7.2.1.6); na fôrma reta essas linhas são inclinadas 3 % (cotas na elevação). Ponta baixa sempre no lado A; folga de 2,5 cm nas pontas.",
         "Sucção do vento na cobertura levanta a VB no apoio (28 kN de cálculo): pino PN-6 Ø20 roscado com porca, contraporca e arruela no nicho do topo do dente, apertado depois do neoprene assentado; graute do nicho só numa ponta (a outra livre para dilatar).",
         "VB-05 a 08 (fachada 9): mesma fôrma e armação; ES-1R M20 hef 400 + grampo U Ø10 no lugar das ES-1V (escora das terças, até 49 kN) e ES-2V das orelhas do X (tabela). Última terça do lado E apoiada no recuo do pilar de canto (ST-1F, PL-07/PL-08).",
         "Placas por fora da viga, fixadas nos pilares (a VB não recebe carga das placas). Içar pelas 2 alças AL-1; estocar sobre 2 calços nas alças. Concreto em cm, chaparia em mm.",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
y = pr.legenda_armadura(XC, y - 4, False)
pr.notas(XC, y - 4, notas, 182)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-VB01")
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
for a in avisos:
    if a[0] == "ERRO" or "sobrep" in a[1]:
        print(a)
