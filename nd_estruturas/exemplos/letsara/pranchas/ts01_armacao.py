"""ND-LET-TS01-2 — TS-01: armação passiva e protensão (A1), com croquis de dobramento."""
import json
from prancha_nd import Prancha
from ts01_dados import P, L, H, DX, HD, LN, sec, F_cord, Ap, f, peso, V, armacao_ts01

DT = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/dentes.json"))["TS-01"]
AD = DT["calculo"]["adotado"]
pr = Prancha("A1", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="TS-01 — VIGA I90 DE COBERTURA PROTENDIDA — ARMAÇÃO, DENTES E PROTENSÃO",
                        desenho="ND-LET-TS01-2", folha="02/04", fase="PARA APROVAÇÃO"))
pr.revisao("01", "12/10/2026", "ARMADURA DOS DENTES GERBER (NBR 9062 + PCI, VERIFICADA POR MEF)")
pr.revisao("02", "12/10/2026", "GEOMETRIA DO R01: L 19,15 m ENTRE FACES")
pr.cabecalho_peca("TS-01", f"VIGA DE COBERTURA I90 PROTENDIDA — SEÇÃO I90 (b 40, bw 15, h 90) · L = {L/10:.0f} cm (entre pontas, a prumo) · 14 PEÇAS",
                  f"PESO {f(peso/9.81,1)} t   ·   VOLUME {f(V,2)} m³   ·   C50 / fckj 35   ·   {P['n_cord']} cord. Ø12,7 CP-190 RB   ·   dentes Gerber 45 × 30 nas duas pontas   ·   caimento 3 %", 560)
sk = lambda h: h * DX / H
mac = P["x_mac"]
ANC = AD["ancoragem_tirante_mm"]
CONTORNO = [(LN, 0), (L - LN, 0), (L - LN + sk(HD), HD), (L + sk(HD), HD), (L + DX, H), (DX, H), (sk(HD), HD), (LN + sk(HD), HD)]
X_SUS = [LN + 40 + k * 60 for k in range(AD["n_sus"])]
X_VD = [75, 225]

# ------------------------------------------------------------------ ELEVAÇÃO DE ARMAÇÃO 1:40
va = pr.vista("ELEVAÇÃO DE ARMAÇÃO", (60, 470), 40, titulo="ELEVAÇÃO DE ARMAÇÃO — TS-01",
              subtitulo="cordoalhas aderentes, cortadas rente à face dos dentes")
va.poli(CONTORNO, "VISTA", fechada=True)
zona = 1500
ini = LN + 40 + AD["n_sus"] * 60 + 100
x_est = list(range(ini, zona + 1, 150)) + list(range(zona + 250, L - zona, 250)) + list(range(L - ini, L - zona - 1, -150))
x_est = sorted(set(x_est))
for x in x_est:
    va.linha((x + sk(40), 40), (x + sk(H - 40), H - 40), "ARM_TRANSV")
for xs_ in (X_SUS, [L - x for x in X_SUS]):
    for x in xs_:
        va.linha((x + sk(40), 40), (x + sk(H - 40), H - 40), "ARM_TRANSV")
n1 = len(x_est)
va.barra([(30, H - 45), (L - 30, H - 45)], "N2", 4, 12.5, comp_cm=(L - 60) / 10, ponto_rotulo=(L * 0.62, H - 45), desloc=(10, 10))
va.barra([(LN + 30, 40), (L - LN - 30, 40)], "N5", 2, 10, comp_cm=(L - 2 * LN - 60) / 10, ponto_rotulo=(L * 0.70, 40), desloc=(10, -12))
va.linha((LN, P["y_cord"]), (L - LN, P["y_cord"]), "ARM_PROT")
for x0_, sg in ((0, 1), (L, -1)):
    va.linha((x0_ + sg * 30, HD + 55), (x0_ + sg * (LN + ANC), HD + 55), "ARMADURA")
va.chamada((L * 0.3, P["y_cord"]), (-10, -16), f"C1 — {P['n_cord']} cord. Ø12,7 aderentes")
va.chamada((x_est[22], 500), (12, 24), f"N1 - {n1} Ø6,3 c/15 (1,5 m nas pontas) e c/25")
va.chamada((LN + 900, HD + 55), (10, -30), "N8 tirante do dente (ver detalhe 4)")
va.cota_h([0, LN, zona, L - zona, L - LN, L], 0, -14)
pr.posicoes_desenho.update({"N1", "N3", "N4", "N6", "N7", "N8", "N9", "N10", "N11", "C1"})
va.marcador_corte((L / 2 + 1500, -120), (L / 2 + 1500 + DX, H + 120), "D", lado=1)
va.marcador_corte((LN + 750, -40), (LN + 750 + DX, H + 120), "E", lado=1)
va.marcador_detalhe((LN + 300, 450), 900, 4, ang=60, dist=6)

# ------------------------------------------------------------------ DETALHE 4 — armação do dente (1:10)
d4 = pr.vista("DETALHE 4", (110, 135), 10, titulo="DETALHE 4 — ARMAÇÃO DO DENTE GERBER",
              subtitulo=f"Vd = {DT['Vd']:.0f} kN, Hd = {DT['Hd']:.0f} kN (as duas pontas iguais)")
XF = LN + ANC + 300
d4.poli([(XF, 0), (LN, 0), (LN + sk(HD), HD), (sk(HD), HD), (DX, H), (XF + DX, H)], "VISTA")
d4.interrupcao((XF, 0), (XF + DX, H))
d4.barra([(30, HD + 55), (LN + ANC, HD + 55)], "N8", AD["n_tir"], AD["d_tir"], comp_cm=2 * (LN + ANC) / 10 + 30,
         ponto_rotulo=(LN + 700, HD + 55), desloc=(10, -14))
for x in X_SUS:
    d4.poli([(x, 40), (x, H - 40)], "ARM_TRANSV")
d4.chamada((X_SUS[-1], 250), (14, -16), f"N9 - {AD['n_sus']} estribos Ø{AD['d_sus']:g} (suspensão)".replace(".", ","))
d_ = HD - 55
for k in range(AD["n_cost"]):
    yk = HD + 55 + (k + 1) * (2 / 3 * d_) / (AD["n_cost"] + 1)
    d4.poli([(30, yk), (LN + 450, yk)], "ARM_TRANSV")
d4.chamada((LN + 400, HD + 55 + (2 / 3 * d_) / (AD["n_cost"] + 1)), (16, 20), f"N10 - {AD['n_cost']} estribos horiz. Ø10 (costura)")
for x in X_VD:
    d4.poli([(x, HD + 30), (x, H - 30)], "ARM_TRANSV")
d4.chamada((X_VD[0], H - 100), (-10, 12), "N11 - 2 estribos Ø10 no dente")
d4.linha((LN, P["y_cord"]), (XF, P["y_cord"]), "ARM_PROT")
d4.chamada((LN + 200, P["y_cord"]), (8, -10), "C1 começa na face do dente (transferência 760 mm)")
d4.cota_h([sk(HD), LN + sk(HD)], HD, 34, total=False)
d4.cota_h([30, LN, LN + ANC], HD + 55, 22, total=False)
d4.cota_h([LN, X_SUS[0], X_SUS[-1]], 0, -10, total=False)
d4.cota_v([0, HD, HD + 55, H], XF + DX, 10, total=False)

# ------------------------------------------------------------------ CORTES DE ARMAÇÃO 1:10
pts = [(x * 1000, y * 1000) for x, y in sec.pts]
vc = pr.vista("CORTE D-D", (330, 300), 10, titulo="CORTE D-D", subtitulo="seção corrente")
vc.poli(pts, "CORTADO", fechada=True)
for x in P["x_cord"]:
    vc.ponto_barra((x, P["y_cord"]), 12.7, "ARM_PROT_SECAO")
for x in (-160, -60, 60, 160):
    vc.ponto_barra((x, H - 45), 12.5)
for x in (-165, 165):
    vc.ponto_barra((x, 40), 10)
vc.poli([(-45, 30), (45, 30), (45, H - 30), (-45, H - 30)], "ARM_TRANSV", fechada=True)
vc.poli([(-170, H - 30), (170, H - 30), (170, H - 100), (-170, H - 100)], "ARM_TRANSV", fechada=True)
vc.poli([(-170, 30), (170, 30), (170, 100), (-170, 100)], "ARM_TRANSV", fechada=True)
vc.chamada((100, P["y_cord"]), (22, -10), f"C1 - {P['n_cord']} Ø12,7")
vc.chamada((160, H - 45), (20, 8), "N2 - 4 Ø12,5")
vc.chamada((165, 40), (20, 2), "N5 - 2 Ø10")
vc.chamada((45, 450), (34, 6), "N1 Ø6,3")
vc.chamada((-170, H - 65), (-20, 8), "N3 Ø6,3 c/25")
vc.chamada((-170, 65), (-20, -12), "N4 Ø6,3 c/25")
vc.cota_h([-200, 200], 0, -10)
vc.cota_v([0, P["y_cord"], H], 200, 12)

ve = pr.vista("CORTE E-E", (480, 300), 10, titulo="CORTE E-E", subtitulo="maciço junto ao dente")
rb = [(-200, 0), (200, 0), (200, H), (-200, H)]
ve.poli(rb, "CORTADO", fechada=True)
ve.ret(-25, 0, 50, H, "OCULTA")
for x in P["x_cord"]:
    ve.ponto_barra((x, P["y_cord"]), 12.7, "ARM_PROT_SECAO")
for x in (-160, -60, 60, 160):
    ve.ponto_barra((x, H - 45), 12.5)
ve.poli([(-170, 30), (170, 30), (170, H - 30), (-170, H - 30)], "ARM_TRANSV", fechada=True)
for yy in (250, 450, 650):
    ve.poli([(-120, yy + 60), (-170, yy + 60), (-170, yy), (170, yy), (170, yy + 60), (120, yy + 60)], "ARM_TRANSV")
ve.chamada((170, 520), (20, 6), "N6 Ø8 c/7 (7 por ponta, após a suspensão)")
ve.chamada((-170, 250), (-20, -6), "N7 Ø10 grampo (4 por ponta)")
ve.cota_h([-200, 200], 0, -10)

# ------------------------------------------------------------------ DETALHE 3 — grade da cabeceira (1:5)
d3 = pr.vista("DETALHE 3", (520, 130), 5, titulo="DETALHE 3 — CORDOALHAS NA GRADE DA CABECEIRA",
              subtitulo="cabeçote REV05: 7 colunas c/50, linhas c/42 a partir de 75")
d3.poli([(-200, 0), (200, 0), (200, 150), (75, 230), (75, 300)], "VISTA")
d3.poli([(-200, 0), (-200, 150), (-75, 230), (-75, 300)], "VISTA")
for c in range(-150, 151, 50):
    for r in range(5):
        y = 75 + 42 * r
        if abs(c) > 75 and y > 150 or abs(c) <= 75 and y > 300:
            continue
        if r == 0 and c in P["x_cord"]:
            d3.ponto_barra((c, y), 12.7, "ARM_PROT_SECAO")
        else:
            d3.circulo((c, y), 8.5, "OCULTA")
d3.cota_h([-150, -100, -50, 0, 50, 100, 150], 0, -8, total=False)
d3.cota_v([0, 75, 117, 159, 201], 200, 10, total=False)
d3.chamada((150, 75), (22, -10), "cordoalha usada (6)")
d3.chamada((0, 117), (16, 26), "furo livre Ø17 da grade")

# ------------------------------------------------------------------ coluna direita
x0, y = pr.quadro[2] - 180, pr.quadro[3] - 6
_, _, barras = armacao_ts01()
ta = pr.tabela_croqui(x0, y, barras, h_lin=11.0)
tc = pr.tabela_cordoalhas(x0, ta["y_base"] - 4, [dict(pos="C1", diam=12.7, qtd=P["n_cord"], y=P["y_cord"],
                                                      forca=F_cord, isol=0)], P["L_pista"])
kg_cord = Ap * 1e4 * L / 1000 * 0.785
notas = [f"Concreto C{P['fck']}; liberar as cordoalhas só com fckj ≥ {P['fckj']} MPa (corpo de prova curado com a peça).",
         f"Cordoalhas CP-190 RB Ø12,7 aderentes, linha inferior da grade (y = {P['y_cord']} mm), colunas ±50/±100/±150; σpi = {P['sig_pi']} MPa; liberação gradual e simétrica.",
         f"Pista de {P['L_pista']} m: até 3 peças por linha; alongamento medido × teórico dentro de ±7%. Cordoalhas por peça: {f(kg_cord,0)} kg.",
         "Estribos N1, N6 e N9 verticais na fôrma; N9 (suspensão) fechados, envolvendo as cordoalhas e o N2, o mais perto possível da face do dente.",
         f"N8 (tirante do dente) em U horizontal, com a curva na ponta, junto à CH-A1; ancoragem de {ANC} mm além da face do dente. N10 envolve o N8.",
         "As alças AL-1 (laço de cordoalha) estão na folha 01 e são posicionadas entre os estribos N1, sem cortar armadura.",
         "Cobrimento 30 mm (CAA II). Dobramento conforme NBR 6118:2023 item 9.4.6. Medidas em cm na tabela e mm no desenho.",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
yl = pr.legenda_armadura(x0, tc["y_base"] - 4, True)
pr.notas(x0, yl - 4, notas, 180)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-TS01-2")
for a in avisos:
    print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos;", f"aço {ta['total_kg']:.0f} kg")
