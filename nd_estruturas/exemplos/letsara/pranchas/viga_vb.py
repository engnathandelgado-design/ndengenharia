"""ND-LET-VB01 — vigas de borda VB-01 a VB-04 (15 × 90, concreto armado C40) das fachadas 1 e 9: fôrma, armação e insertos (A1)."""
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha

f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
X_FACH = [("A", 0.0), ("B", 9.87), ("C", 20.05), ("D", 29.63), ("E", 40.10)]
B, H = 150, 900
COB = 30
MARCAS = []
for k, ((na, xa), (nb, xb)) in enumerate(zip(X_FACH[:-1], X_FACH[1:]), 1):
    L = round((xb - xa) * 1000 - 500)                                     # 25 cm de folga da face de cada pilar
    MARCAS.append((f"VB-0{k}", f"{na}–{nb}, fachadas 1 e 9", 2, L))
L = MARCAS[1][3]                                                            # VB-02 desenhada (9,68 m)
PASSO_T = 1579
TERCAS = [round(255 + PASSO_T * k) for k in range(7) if 255 + PASSO_T * k < L - 200]
PESO = 0.15 * 0.90 * 25 * L / 1000
V = 0.15 * 0.90 * L / 1000
# cargas: peso próprio 3,4 + telha/terças/vento (5 m de tributária) ≈ 1,6 kN/m → M ≈ 59 kN·m; vento de sucção simétrico
pr = Prancha("A1", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="VIGAS DE BORDA VB-01 A VB-04 (15×90, C40) — FACHADAS 1 E 9 — FÔRMA, ARMAÇÃO E INSERTOS",
                        desenho="ND-LET-VB01", folha="01/01", fase="PARA APROVAÇÃO", marca="VB-02", qtd=2, peso=f(PESO, 1), volume=f(V, 2)))
pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL")
Q = pr.quadro
XC = Q[2] - 190
pr.ret(Q[0] + 4, Q[3] - 30, Q[0] + 500, Q[3] - 4, "CARIMBO")
pr.texto(Q[0] + 10, Q[3] - 24, "VB-02", "grande", "TITULO")
pr.texto(Q[0] + 62, Q[3] - 24, f"VIGA DE BORDA 15 × 90 cm — VB-02 (L = {L/10:.0f} cm) · VB-01 · VB-03 · VB-04", "titulo", "TITULO")
pr.texto(Q[0] + 10, Q[3] - 14, f"fachadas 1 e 9, entre os pilares de fachada; apoio nos consolos CP-VB com pino PN-1   ·   PESO {f(PESO/10, 2)} t   ·   VOLUME {f(V, 2)} m³   ·   C40, CA-50", "nota", "TEXTO")

# planta-chave
kp = pr.vista("PLANTA-CHAVE", (Q[0] + 545, Q[3] - 118), 1000, titulo="PLANTA-CHAVE", subtitulo="VB nas fachadas 1 e 9", unidade="cm")
M = lambda v: v * 1000
Y_LIN = [0.0, 10.05, 19.705, 29.36, 38.865, 48.445, 58.025, 67.605, 76.81]
for y in Y_LIN:
    kp.linha((M(-2), M(y)), (M(42), M(y)), "EIXO")
for _, x in X_FACH:
    kp.linha((M(x), M(-2)), (M(x), M(79)), "EIXO")
for i, y in enumerate(Y_LIN, 1):
    kp.texto((M(-3.5), M(y)), str(i), "min", "MIDDLE_RIGHT")
for j, (n, x) in enumerate(X_FACH):
    kp.texto((M(x), M(80)), n, "min", "BOTTOM_CENTER")
for mk, _, _, Lm in MARCAS:
    k = int(mk[-1]) - 1
    for y in (0.0, 76.81):
        kp.ret(M(X_FACH[k][1]) + 250, M(y) - 150, Lm, 300, "CORTADO")
        kp.texto((M((X_FACH[k][1] + X_FACH[k + 1][1]) / 2), M(y) + (600 if y == 0 else -600)), mk, "min", "BOTTOM_CENTER" if y == 0 else "TOP_CENTER")

# ELEVAÇÃO 1:20 (cm)
ESC = 20
ve = pr.vista("ELEVAÇÃO", (Q[0] + 40, Q[3] - 175), ESC, titulo="ELEVAÇÃO DE FÔRMA — VB-02", subtitulo="face interna; CH-T1 no topo nos passos das terças", unidade="cm")
ve.ret(0, 0, L, H, "VISTA")
for x in (150, L - 150):
    ve.ret(x - 25, 0, 50, 450, "OCULTA")
    ve.chapa(x - 150, -12.5, 300, 12.5)
for s in TERCAS:
    ve.chapa(s - 75, H, 150, 12.5)
for s in (1500, L - 1500):
    ve.poli([(s - 60, H), (s - 60, H + 100), (s, H + 140), (s + 60, H + 100), (s + 60, H)], "METALICA")
ve.cota_ord([0, 150] + TERCAS + [L - 150, L], H + 140, 14, x0=0)
ve.cota_h([0, 150, L - 150, L], 0, -10)
ve.cota_v([0, H], L, 10)
ve.chamada((150, 225), (14, 16), "TB-1 tubo Ø50×3,0 L=450 + CH-A1 (2x)")
ve.chamada((TERCAS[2], H + 12), (10, 12), f"CH-T1 150×150×12,5 — {len(TERCAS)}x (terças Ue 300)")
ve.chamada((1500, H + 140), (10, 10), "AL-1 alça (2x)")
ve.marcador_corte((L / 2, -22 * ESC), (L / 2, H + 24 * ESC), "A", lado=1)
ve.marcador_detalhe((400, H / 2), 700, 1, ang=-120, dist=8)

# ARMAÇÃO 1:20
va = pr.vista("ARMAÇÃO", (Q[0] + 40, Q[3] - 290), ESC, titulo="ELEVAÇÃO DE ARMAÇÃO — VB-02", subtitulo="igual nas 4 marcas (muda só o comprimento)", unidade="cm")
va.ret(0, 0, L, H, "VISTA")
xs_e = list(range(50, 1500, 100)) + list(range(1500, L - 1500, 150)) + list(range(L - 1500, L - 40, 100))
for x in xs_e:
    va.linha((x, COB), (x, H - COB), "ARM_TRANSV")
va.barra([(COB, COB + 10), (L - COB, COB + 10)], "N1", 3, 12.5, comp_cm=round((L - 2 * COB) / 10), ponto_rotulo=(L / 3, COB + 10), desloc=(10, -14))
va.barra([(COB, H - COB - 10), (L - COB, H - COB - 10)], "N2", 3, 12.5, comp_cm=round((L - 2 * COB) / 10), ponto_rotulo=(L / 3, H - COB - 10), desloc=(10, 14))
for y in (300, 600):
    va.linha((COB, y), (L - COB, y), "ARMADURA")
va.chamada((2 * L / 3, 600), (10, 12), "N3 pele — 2 Ø8 por face a cada 30 cm")
va.chamada((L / 2, H - COB), (10, 16), f"N4 — {len(xs_e)} estribos Ø6,3: c/15 corrente, c/10 nos 150 cm das pontas")
va.cota_h([0, 1500, L - 1500, L], 0, -10)
pr.posicoes_desenho.update({"N3", "N4"})

# CORTE A-A 1:10 e DETALHE 1 (ponta) 1:10
YR = Q[3] - 470
ca = pr.vista("CORTE A-A", (Q[0] + 60, YR), 10, titulo="CORTE A-A", subtitulo="seção corrente; cobrimento 3,0 cm", unidade="cm")
pts = [(-B / 2, 0), (B / 2, 0), (B / 2, H), (-B / 2, H)]
ca.poli(pts, "CORTADO", fechada=True); ca.hachura(pts, "AR-CONC", 0.03)
ca.poli([(-B / 2 + COB, COB), (B / 2 - COB, COB), (B / 2 - COB, H - COB), (-B / 2 + COB, H - COB)], "ARM_TRANSV", fechada=True)
for x in (-B / 2 + COB + 10, 0, B / 2 - COB - 10):
    ca.ponto_barra((x, COB + 10), 12.5); ca.ponto_barra((x, H - COB - 10), 12.5)
for y in (300, 600):
    ca.ponto_barra((-B / 2 + COB + 6, y), 8); ca.ponto_barra((B / 2 - COB - 6, y), 8)
ca.chapa(-75, H, 150, 12.5)
for yy in (-50, 50):
    ca.linha((yy, H), (yy, H - 100), "METALICA"); ca.chapa(yy - 12, H - 108, 24, 8)
ca.cota_h([-B / 2, B / 2], 0, -10); ca.cota_v([0, 300, 600, H], B / 2, 10)
ca.chamada((B / 2 - COB - 10, H - COB - 10), (14, 10), "N2 — 3 Ø12,5")
ca.chamada((B / 2 - COB - 10, COB + 10), (14, -10), "N1 — 3 Ø12,5")
ca.chamada((B / 2 - COB - 6, 600), (14, 0), "N3 — 2 Ø8 por face")
ca.chamada((B / 2 - COB, 450), (14, -14), "N4 Ø6,3 c/15")
ca.chamada((75, H + 6), (14, 14), "CH-T1 150×150×12,5 + 2 pinos Ø12,5 c/ cabeça L=100")

d1 = pr.vista("DETALHE 1", (Q[0] + 230, YR), 10, titulo="DETALHE 1 — PONTA E APOIO NO CONSOLO CP-VB", subtitulo="pino PN-1 Ø20 no TB-1; neoprene 300×150×10", unidade="cm")
LD = 1400
d1.poli([(0, 0), (LD, 0), (LD, H), (0, H)], "VISTA", fechada=True); d1.interrupcao((LD, 0), (LD, H))
d1.chapa(150 - 25, 0, 50, 450); d1.chapa(0, -12.5, 300, 12.5); d1.chapa(25, -22.5, 250, 10)
for x in (50, 150, 250, 350, 450, 550, 650, 750):
    d1.linha((x, COB), (x, H - COB), "ARM_TRANSV")
d1.poli([(COB, COB + 200), (COB, COB), (LD, COB)], "ARMADURA"); d1.poli([(COB, H - COB - 200), (COB, H - COB), (LD, H - COB)], "ARMADURA")
d1.ret(-25, -32, 300, 10, "OCULTA")
d1.cota_h([0, 150, 300, LD], 0, -12, total=False); d1.cota_v([0, 450, H], LD, 10, total=False)
d1.chamada((150, 300), (14, 12), "TB-1 Ø50×3,0 L=450 soldado na CH-A1 300×150×12,5")
d1.chamada((COB, COB + 200), (12, 10), "N1/N2 com dobra de 20 cm nas pontas (ancoragem)")
d1.chamada((400, COB + 100), (12, 14), "N4 c/10 nos 150 cm")
d1.chamada((140, -27), (24, -22), "NEO-1 e consolo CP-VB 30×40×35/20 (ver prancha do pilar); assento = fundo da viga")

# tabelas
y = Q[3] - 6
y = pr.tabela(XC, y, "MARCAS — VIGAS DE BORDA 15×90", ["MARCA", "POSIÇÃO", "QT", "L (cm)", "PESO (t)"], [[m, p, q, f"{Lm/10:.0f}", f(0.15 * 0.9 * 25 * Lm / 1000 / 10, 2)] for m, p, q, Lm in MARCAS], [18, 70, 10, 24, 24])
Lb = round((L - 2 * COB) / 10)
barras = [dict(pos="N1", diam=12.5, qtd=3, comp=Lb + 40, forma=[(0, 20), (0, 0), (Lb, 0), (Lb, 20)], trechos=["20", f"{Lb}", "20"]),
          dict(pos="N2", diam=12.5, qtd=3, comp=Lb + 40, forma=[(0, 0), (0, 20), (Lb, 20), (Lb, 0)], trechos=["20", f"{Lb}", "20"]),
          dict(pos="N3", diam=8.0, qtd=4, comp=Lb, trechos=[f"{Lb}"]),
          dict(pos="N4", diam=6.3, qtd=len(xs_e), comp=round((2 * (90 + 840) + 120) / 10), forma=[(0, 0), (9, 0), (9, 84), (0, 84), (0, 0), (2, 2)], trechos=["9", "84", "", ""])]
ta = pr.tabela_croqui(XC, y - 4, barras, h_lin=9.0)
y = ta["y_base"]
ins = [["TB-1", "Tubo Ø50×3,0 L=450 a prumo, soldado na CH-A1", 2, "a 150 das pontas"], ["CH-A1", "Chapa 300×150×12,5 + 2 grapas Ø12,5 (fundo)", 2, "fundo das pontas"],
       ["CH-T1", "Chapa 150×150×12,5 + 2 pinos Ø12,5 c/ cabeça (terças)", len(TERCAS), "topo, c/157,9 (passo das terças)"], ["AL-1", "Laço de cordoalha Ø12,7 (2 pernas)", 2, "a 150 cm das pontas"],
       ["NEO-1", "Neoprene 300×150×10 (furo Ø30)", 2, "sobre os consolos CP-VB"]]
y = pr.tabela(XC, y - 4, "INSERTOS POR PEÇA (VB-02) — dimensões em mm", ["MARCA", "DESCRIÇÃO", "QT", "POSIÇÃO"], ins, [16, 104, 10, 52])
qd = [["MARCA", "VB-02", "SEÇÃO", "15 × 90 cm"], ["COMPRIMENTO", f"{L/10:.0f} cm", "CONCRETO", "C40"], ["VOLUME", f"{f(V, 2)} m³", "PESO", f"{f(PESO/10, 2)} t"],
      ["AÇO CA-50", f"{f(ta['total_kg'], 0)} kg", "TAXA", f"{f(ta['total_kg'] / V, 0)} kg/m³"], ["QUANTIDADE", "2 (família: 8)", "COBRIMENTO", "3,0 cm (CAA II)"]]
y = pr.tabela(XC, y - 4, "QUADRO DA PEÇA", ["ITEM", "VALOR", "ITEM", "VALOR"], qd, [30, 62, 30, 60])
mem = [["Md (g + q, 5 m tributários)", "≈ 59 kN·m"], ["As necessária / adotada", "1,8 / 3,7 cm² (3 Ø12,5)"], ["As mínima (0,15 %)", "2,0 cm² ≤ 3,7"],
       ["Sucção do vento (uplift)", "simétrica: N2 = N1"], ["Cortante (Vd 35 kN)", "Ø6,3 c/15 ≥ mínimo"], ["Pele (h > 60)", "2 Ø8 / face"]]
y = pr.tabela(XC, y - 4, "MEMÓRIA RESUMIDA (NBR 6118:2023)", ["VERIFICAÇÃO", "RESULTADO"], mem, [70, 112])
notas = ["Concreto C40, aço CA-50; cobrimento 3,0 cm (CAA II). Barras N1/N2 com dobra de 20 cm nas pontas.",
         "Topo da VB alinhado com o topo das TS-01 (H = 90): as terças do primeiro vão apoiam na VB pelas CH-T1 e cantoneiras CT-1 (ND-LET-COB01).",
         "Apoio nos consolos CP-VB dos pilares de fachada e de canto: NEO-1 e pino PN-1 Ø20 no TB-1; graute só numa ponta.",
         "Placas de fechamento CM-01 por fora da viga; a VB não recebe carga das placas (fixadas nos pilares pelos IP-01).",
         "Içar pelas 2 alças AL-1; estocar sobre 2 calços nas alças. Cotas de concreto em cm, chaparia em mm. Não medir no desenho.",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
y = pr.legenda_armadura(XC, y - 4, False)
pr.notas(XC, y - 4, notas, 182)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-VB01")
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
for a in avisos:
    if a[0] == "ERRO" or "sobrep" in a[1]:
        print(a)
