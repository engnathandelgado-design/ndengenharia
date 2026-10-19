"""ND-LET-TS01-2 — TS-01: armação passiva e protensão (A1), com croquis de dobramento. Rev. 03: sem dentes."""
from prancha_nd import Prancha
from ts01_dados import P, L, H, DX, sec, F_cord, Ap, f, peso, V, armacao_ts01, L_N9, LBPT, LBPT_BRUSCA, ATO

pr = Prancha("A1", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="TS-01 — VIGA I90 DE COBERTURA PROTENDIDA — ARMAÇÃO E PROTENSÃO",
                        desenho="ND-LET-TS01-2", folha="02/03", fase="PARA APROVAÇÃO"))
pr.revisao("01", "12/10/2026", "ARMADURA DOS DENTES GERBER (NBR 9062 + PCI, VERIFICADA POR MEF)")
pr.revisao("02", "12/10/2026", "GEOMETRIA DO R01")
pr.revisao("03", "14/10/2026", "SEM DENTES: ARMADURA DE APOIO DIRETO; 8 CORDOALHAS (2 ISOLADAS 3,00 m)")
pr.revisao("06", "19/10/2026", "DEC-032: N9 2 Ø10 NO TOPO DAS PONTAS (ATO); PERDAS 9.6.3; FORÇA NO MACACO E lbpt NAS NOTAS")
pr.cabecalho_peca("TS-01", f"VIGA DE COBERTURA I90 PROTENDIDA — SEÇÃO I90 (b 40, bw 15, h 90) · L = {f(L/10,1)} cm (entre pontas, a prumo) · 14 PEÇAS",
                  f"PESO {f(peso/9.81,1)} t   ·   VOLUME {f(V,2)} m³   ·   C50 / fckj 35   ·   {P['n_cord']} cord. Ø12,7 CP-190 RB   ·   sem dentes   ·   caimento 3 %", 560)
sk = lambda h: h * DX / H
LC, EC = P["cunha"]["L"], P["cunha"]["e"]            # rev04: cunhas no fundo das pontas (ver folha 01)
CONTORNO = [(EC * DX / H, EC), (LC, 0), (L - LC, 0), (L - LC, EC), (L, 0), (L + DX, H), (DX, H)]
TB = P["tb"]
S_TB = [TB["s_ext"], L - TB["s_cen"]]
ISO = P["isol"]["L"]
x_est, _, barras = armacao_ts01()
n1 = len(x_est)
X_N6 = [40, 90, 190, 240, 290, 340, 390, 440]          # N6 Ø8 34×84 no maciço (8 por ponta), fora da faixa dos tubos TB-3
X_N6 = X_N6 + [L - x for x in X_N6]

# ------------------------------------------------------------------ ELEVAÇÃO DE ARMAÇÃO 1:40
va = pr.vista("ELEVAÇÃO DE ARMAÇÃO", (60, 470), 40, titulo="ELEVAÇÃO DE ARMAÇÃO — TS-01",
              subtitulo="cordoalhas aderentes até as pontas, exceto C2 (isoladas 3,00 m em cada ponta); COTAS EM CM", unidade="cm")
va.poli(CONTORNO, "VISTA", fechada=True)
for x in x_est:
    va.linha((x + sk(40), 40), (x + sk(H - 40), H - 40), "ARM_TRANSV")
for x in X_N6:
    va.linha((x + sk(30), 30), (x + sk(H - 30), H - 30), "ARM_TRANSV")
va.barra([(30, H - 45), (L - 30, H - 45)], "N2", 4, 12.5, comp_cm=(L - 60) / 10, ponto_rotulo=(L * 0.62, H - 45), desloc=(10, 10))
for xa, xb in ((30, L_N9 + 30), (L - 30 - L_N9, L - 30)):                       # DEC-032: tração no topo no ato
    va.barra([(xa, H - 70), (xb, H - 70)], "N9", 2, 10, comp_cm=L_N9 / 10, ponto_rotulo=((xa + xb) / 2, H - 70), desloc=(6, -10))
va.barra([(30, 40), (L - 30, 40)], "N5", 2, 10, comp_cm=(L - 60) / 10, ponto_rotulo=(L * 0.70, 40), desloc=(10, -12))
va.linha((0, P["y1"]), (L, P["y1"]), "ARM_PROT")
va.linha((0, P["y2"]), (L, P["y2"]), "ARM_PROT")
for a, b in ((0, ISO), (L - ISO, L)):
    va.ret(a, P["y2"] - 12, b - a, 24, "OCULTA")
va.chamada((L * 0.3, P["y1"]), (-10, -16), "C1 — 6 cord. Ø12,7 aderentes")
va.chamada((ISO / 2, P["y2"]), (10, 14), "C2 — 2 cord. Ø12,7, bainha plástica nos 3,00 m de cada ponta")
va.chamada((x_est[22], 500), (12, 24), f"N1 - {n1} Ø6,3 c/15 (1,5 m nas pontas) e c/25")
va.cota_h([0, 1500, ISO, L - ISO, L - 1500, L], 0, -14)
pr.posicoes_desenho.update({"N1", "N3", "N4", "N6", "N7", "N8", "N9", "C1", "C2"})
va.marcador_corte((L / 2 + 1500, -120), (L / 2 + 1500 + DX, H + 120), "D", lado=1)
va.marcador_corte((600, -40), (600 + DX, H + 120), "E", lado=1)
va.marcador_detalhe((350, 450), 700, 4, ang=60, dist=6)

# ------------------------------------------------------------------ DETALHE 4 — armação da ponta (1:10)
d4 = pr.vista("DETALHE 4", (110, 135), 10, titulo="DETALHE 4 — ARMAÇÃO DA PONTA (APOIO DIRETO)",
              subtitulo="ponta do pilar; a ponta central é igual (TB-3 a 7,75 da ponta); COTAS EM CM", unidade="cm")
XF = 1600
d4.poli([(XF, 0), (0, 0), (DX, H), (XF + DX, H)], "VISTA")
d4.interrupcao((XF, 0), (XF + DX, H))
s0 = S_TB[0]
for d in (-25, 25):
    d4.linha((s0 + d, 0), (s0 + d + DX, H), "OCULTA")
for x in [x for x in x_est if x < XF]:
    d4.poli([(x + sk(40), 40), (x + sk(H - 40), H - 40)], "ARM_TRANSV")
for x in X_N6[:8]:
    d4.poli([(x + sk(30), 30), (x + sk(H - 30), H - 30)], "ARM_TRANSV")
for yy in (35, 125):
    d4.poli([(30, yy), (780, yy)], "ARM_TRANSV")
d4.poli([(630, 80), (30, 80)], "ARM_TRANSV")
d4.linha((0, P["y1"]), (XF, P["y1"]), "ARM_PROT")
d4.linha((0, P["y2"]), (XF, P["y2"]), "ARM_PROT")
d4.ret(0, P["y2"] - 12, XF, 24, "OCULTA")
d4.poli([(30, H - 45), (XF, H - 45)], "ARMADURA")
d4.chamada((X_N6[5] + sk(500), 500), (14, 18), "N6 - 8 estribos Ø8 34×84 por ponta (maciço), fora dos tubos")
d4.chamada((700, 125), (-30, 40), "N8 - 2 estribos horizontais Ø10 75×34 por ponta (y 3,5 e 12,5)")
d4.chamada((450, 80), (16, -24), "N7 - 3 grampos U Ø10 horizontais por ponta (60 × 34)")
d4.chamada((s0 + 12, 600), (-14, 20), "TB-3 Ø50 (folha 01)")
d4.chamada((1000, P["y2"]), (10, 22), "C2 com bainha (3,00 m)")
d4.chamada((x_est[3] + sk(700), 700), (12, 10), "N1 Ø6,3 c/15")
d4.cota_h([0, s0, 440], 0, -10, total=False)
d4.cota_v([0, H], XF + DX, 10, total=False)

# ------------------------------------------------------------------ CORTES DE ARMAÇÃO 1:10
pts = [(x * 1000, y * 1000) for x, y in sec.pts]


def cordoalhas(v):
    for x in P["x_cord"]:
        v.ponto_barra((x, P["y1"]), 12.7, "ARM_PROT_SECAO")
    for x in P["x_cord2"]:
        v.ponto_barra((x, P["y2"]), 12.7, "ARM_PROT_SECAO")


vc = pr.vista("CORTE D-D", (330, 300), 10, titulo="CORTE D-D", subtitulo="seção corrente; COTAS EM CM", unidade="cm")
vc.poli(pts, "CORTADO", fechada=True)
cordoalhas(vc)
for x in (-160, -60, 60, 160):
    vc.ponto_barra((x, H - 45), 12.5)
for x in (-165, 165):
    vc.ponto_barra((x, 40), 10)
vc.poli([(-45, 30), (45, 30), (45, H - 30), (-45, H - 30)], "ARM_TRANSV", fechada=True)
vc.poli([(-170, H - 30), (170, H - 30), (170, H - 100), (-170, H - 100)], "ARM_TRANSV", fechada=True)
vc.poli([(-170, 30), (170, 30), (170, 130), (-170, 130)], "ARM_TRANSV", fechada=True)
vc.chamada((155, P["y1"]), (22, -14), "C1 - 6 Ø12,7 (y 5,5: x 0, ±4, ±15,5; y 10: x 0)")
vc.chamada((40, P["y2"]), (24, 10), "C2 - 2 Ø12,7 (y 10, x ±4)")
vc.chamada((160, H - 45), (20, 8), "N2 - 4 Ø12,5")
vc.chamada((165, 40), (20, 2), "N5 - 2 Ø10")
vc.chamada((45, 450), (34, 6), "N1 Ø6,3")
vc.chamada((-170, H - 65), (-20, 8), "N3 Ø6,3 c/25")
vc.chamada((-170, 80), (-20, -12), "N4 Ø6,3 c/25")
vc.cota_h([-200, 200], 0, -10)
vc.cota_v([0, P["y2"], H], 200, 12)

ve = pr.vista("CORTE E-E", (500, 300), 10, titulo="CORTE E-E", subtitulo="maciço da ponta; COTAS EM CM", unidade="cm")
rb = [(-200, 0), (200, 0), (200, H), (-200, H)]
ve.poli(rb, "CORTADO", fechada=True)
for yy in TB["y"]:
    ve.ret(yy - 25, 0, 50, H, "OCULTA")
cordoalhas(ve)
for x in (-160, -60, 60, 160):
    ve.ponto_barra((x, H - 45), 12.5)
ve.poli([(-170, 30), (170, 30), (170, H - 30), (-170, H - 30)], "ARM_TRANSV", fechada=True)
ve.poli([(-45, 40), (45, 40), (45, H - 40), (-45, H - 40)], "ARM_TRANSV", fechada=True)
ve.chamada((170, 520), (20, 6), "N6 Ø8 34×84 (8 por ponta)")
ve.chamada((-100, 450), (-22, 10), "TB-3 (2x)")
ve.cota_h([-200, -100, 100, 200], 0, -10)

# ------------------------------------------------------------------ DETALHE 3 — cordoalhas na cabeceira (1:5)
d3 = pr.vista("DETALHE 3", (520, 130), 5, titulo="DETALHE 3 — CORDOALHAS NA CABECEIRA",
              subtitulo="furação da grade da TS-01 rev03 (confirmar com a fábrica); COTAS EM CM", unidade="cm")
d3.poli([(-200, 0), (200, 0), (200, 150), (75, 230), (75, 300)], "VISTA")
d3.poli([(-200, 0), (-200, 150), (-75, 230), (-75, 300)], "VISTA")
for yy in TB["y"]:
    d3.circulo((yy, 75), 25, "OCULTA")
cordoalhas(d3)
d3.cota_h([-200, -155, -40, 0, 40, 155, 200], 0, -8, total=False)
d3.cota_v([0, P["y1"], P["y2"]], 200, 10, total=False)
d3.chamada((155, P["y1"]), (22, -10), "C1")
d3.chamada((40, P["y2"]), (16, 26), "C2 (isoladas)")
d3.chamada((-100, 100), (-16, 30), "faixa dos tubos TB-3 (sem cordoalha)")

# ------------------------------------------------------------------ coluna direita
x0, y = pr.quadro[2] - 180, pr.quadro[3] - 6
ta = pr.tabela_croqui(x0, y, barras, h_lin=11.0)
tc = pr.tabela_cordoalhas(x0, ta["y_base"] - 4, [dict(pos="C1", diam=12.7, qtd=6, y=(5 * P["y1"] + P["y2"]) / 6, forca=F_cord, isol=0),
                                                  dict(pos="C2", diam=12.7, qtd=2, y=P["y2"], forca=F_cord, isol=ISO)], P["L_pista"])
kg_cord = Ap * 1e4 * L / 1000 * 0.785
notas = [f"Concreto C{P['fck']}; liberar as cordoalhas só com fckj ≥ {P['fckj']} MPa (corpo de prova curado com a peça).",
         f"Cordoalhas CP-190 RB Ø12,7: 5 a 5,5 cm (x = 0, ±4, ±15,5) e 3 a 10 cm (x = 0, ±4); σpi = {P['sig_pi']} MPa ({f(F_cord, 1)} kN por cordoalha no macaco); liberação GRADUAL e simétrica (lbpt = {f(LBPT * 100, 0)} cm; brusca daria {f(LBPT_BRUSCA * 100, 0)} cm, não permitida).",
         f"N9 2 Ø10 no topo, {f(L_N9 / 10, 0)} cm a partir de cada ponta: tração no topo no ato da protensão (NBR 6118:2023 17.2.4.3.2 c, As ≥ {f(ATO['As_topo_cm2'], 1)} cm² com N2).",
         "C2 (x = ±4, y = 10) com bainha plástica estanque nos 3,00 m de cada ponta, vedada com fita nas extremidades.",
         f"Pista de {P['L_pista']} m: até 3 peças por linha; alongamento medido × teórico dentro de ±7 %. Cordoalhas por peça: {f(kg_cord,0)} kg.",
         "Sem dentes: N6 (estribos do maciço), N7 (grampos U) e N8 (estribos horizontais da mesa inferior) absorvem a reação de apoio e a transferência da protensão; estribos verticais fora da faixa dos tubos TB-3.",
         "As alças AL-1, os tubos TB-3 e as esperas ES-1/ES-2 estão na folha 01; posicionar entre os estribos N1, sem cortar armadura.",
         "Cobrimento 3,0 cm (CAA II), medido também nas cunhas das pontas: nos 30 cm de cada ponta os espaçadores do fundo são de 4,0 cm (face rebaixada até 9 mm); cordoalhas a 5,5 cm ficam com 3,9 cm na ponta. Dobramento conforme NBR 6118:2023 item 9.4.6. Medidas em cm.",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
yl = pr.legenda_armadura(x0, tc["y_base"] - 4, True)
pr.notas(x0, yl - 4, notas, 180)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-TS01-2")
for a in avisos:
    print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos;", f"aço {ta['total_kg']:.0f} kg")
