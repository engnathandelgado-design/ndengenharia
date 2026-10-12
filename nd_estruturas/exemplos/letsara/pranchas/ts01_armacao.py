"""ND-LET-TS01-2 — TS-01: armação passiva e protensão (A1), com croquis de dobramento."""
from prancha_nd import Prancha
from ts01_dados import P, L, H, DX, sec, F_cord, Ap, f

pr = Prancha("A1", dict(cliente="MARQUE ENGENHARIA", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="TS-01 — VIGA I90 DE COBERTURA PROTENDIDA — ARMAÇÃO E PROTENSÃO",
                        desenho="ND-LET-TS01-2", folha="02/03", fase="PARA APROVAÇÃO"))
sk = lambda h: h * DX / H
mac = P["mac"]

# ------------------------------------------------------------------ ELEVAÇÃO DE ARMAÇÃO 1:40
va = pr.vista("ELEVAÇÃO DE ARMAÇÃO", (60, 455), 40, titulo="ELEVAÇÃO DE ARMAÇÃO — TS-01",
              subtitulo="cordoalhas aderentes em todo o comprimento (sem isolamento)")
va.poli([(0, 0), (L, 0), (L + DX, H), (DX, H)], "VISTA", fechada=True)
zona = 1500
x_est = list(range(60, zona + 1, 150)) + list(range(zona + 250, L - zona, 250)) + list(range(L - 60, L - zona - 1, -150))
x_est = sorted(set(x_est))
for x in x_est:
    va.linha((x + sk(40), 40), (x + sk(H - 40), H - 40), "ARMADURA")
for x0_ in (0, L - mac):
    for k in range(7):
        x = x0_ + 40 + k * 70
        va.linha((x + sk(60), 60), (x + sk(H - 60), H - 60), "ARMADURA")
n1 = len(x_est)
va.barra([(30, H - 45), (L - 30, H - 45)], "N2", 4, 12.5, comp_cm=(L - 60) / 10, ponto_rotulo=(L * 0.62, H - 45), desloc=(10, 10))
va.barra([(30, 40), (L - 30, 40)], "N5", 2, 10, comp_cm=(L - 60) / 10, ponto_rotulo=(L * 0.70, 40), desloc=(10, -12))
va.linha((0, P["y_cord"]), (L, P["y_cord"]), "ARMADURA")
va.chamada((L * 0.3, P["y_cord"]), (-10, -16), f"C1 — {P['n_cord']} cord. Ø12,7 aderentes")
va.chamada((x_est[14], 500), (12, 24), f"N1 - {n1} Ø6,3 c/15 (1,5 m nas pontas) e c/25")
va.chamada((L - mac + 250, 700), (8, 18), "N6 - 2×7 Ø8 c/7 (fretagem)")
va.cota_h([0, zona, L - zona, L], 0, -14)
va.cota_h([0, mac], 0, -24, total=False)
pr.posicoes_desenho.update({"N1", "N3", "N4", "N6", "N7", "C1"})
va.marcador_corte((L / 2 + 1500, -120), (L / 2 + 1500 + DX, H + 120), "D", lado=1)
va.marcador_corte((260, -120), (260 + DX, H + 120), "E", lado=1)

# ------------------------------------------------------------------ CORTES DE ARMAÇÃO 1:10
pts = [(x * 1000, y * 1000) for x, y in sec.pts]
vc = pr.vista("CORTE D-D", (95, 290), 10, titulo="CORTE D-D", subtitulo="seção corrente")
vc.poli(pts, "CORTADO", fechada=True)
for x in P["x_cord"]:
    vc.ponto_barra((x, P["y_cord"]), 12.7)
for x in (-160, -60, 60, 160):
    vc.ponto_barra((x, H - 45), 12.5)
for x in (-165, 165):
    vc.ponto_barra((x, 40), 10)
vc.poli([(-45, 30), (45, 30), (45, H - 30), (-45, H - 30)], "ARMADURA", fechada=True)
vc.poli([(-170, H - 30), (170, H - 30), (170, H - 100), (-170, H - 100)], "ARMADURA", fechada=True)
vc.poli([(-170, 30), (170, 30), (170, 100), (-170, 100)], "ARMADURA", fechada=True)
vc.chamada((100, P["y_cord"]), (22, -10), f"C1 - {P['n_cord']} Ø12,7")
vc.chamada((160, H - 45), (20, 8), "N2 - 4 Ø12,5")
vc.chamada((165, 40), (20, 2), "N5 - 2 Ø10")
vc.chamada((45, 450), (34, 6), "N1 Ø6,3")
vc.chamada((-170, H - 65), (-20, 8), "N3 Ø6,3 c/25")
vc.chamada((-170, 65), (-20, -12), "N4 Ø6,3 c/25")
vc.cota_h([-200, 200], 0, -10)
vc.cota_v([0, P["y_cord"], H], 200, 12)

ve = pr.vista("CORTE E-E", (265, 290), 10, titulo="CORTE E-E", subtitulo="maciço da ponta")
rb = [(-200, 0), (200, 0), (200, H), (-200, H)]
ve.poli(rb, "CORTADO", fechada=True)
ve.ret(-25, 0, 50, H, "OCULTA")
for x in P["x_cord"]:
    ve.ponto_barra((x, P["y_cord"]), 12.7)
for x in (-160, -60, 60, 160):
    ve.ponto_barra((x, H - 45), 12.5)
ve.poli([(-170, 30), (170, 30), (170, H - 30), (-170, H - 30)], "ARMADURA", fechada=True)
for yy in (250, 450, 650):
    ve.poli([(-120, yy + 60), (-170, yy + 60), (-170, yy), (170, yy), (170, yy + 60), (120, yy + 60)], "ARMADURA")
ve.chamada((170, 520), (20, 6), "N6 Ø8 c/7 (7 por ponta)")
ve.chamada((-170, 250), (-20, -6), "N7 Ø10 grampo (4 por ponta)")
ve.cota_h([-200, 200], 0, -10)

# ------------------------------------------------------------------ DETALHE 3 — grade da cabeceira (1:5)
d3 = pr.vista("DETALHE 3", (420, 300), 5, titulo="DETALHE 3 — CORDOALHAS NA GRADE DA CABECEIRA",
              subtitulo="cabeçote REV05: 7 colunas c/50, linhas c/42 a partir de 75")
d3.poli([(-200, 0), (200, 0), (200, 150), (75, 230), (75, 300)], "VISTA")
d3.poli([(-200, 0), (-200, 150), (-75, 230), (-75, 300)], "VISTA")
for c in range(-150, 151, 50):
    for r in range(5):
        y = 75 + 42 * r
        if abs(c) > 75 and y > 150 or abs(c) <= 75 and y > 300:
            continue
        if r == 0 and c in P["x_cord"]:
            d3.ponto_barra((c, y), 12.7)
        else:
            d3.circulo((c, y), 8.5, "OCULTA")
d3.cota_h([-150, -100, -50, 0, 50, 100, 150], 0, -8, total=False)
d3.cota_v([0, 75, 117, 159, 201], 200, 10, total=False)
d3.chamada((150, 75), (22, -10), "cordoalha usada (6)")
d3.chamada((0, 117), (16, 26), "furo livre Ø17 da grade")

# ------------------------------------------------------------------ coluna direita
x0, y = pr.quadro[2] - 180, pr.quadro[3] - 6
cN1, cN3, cN6 = round((2 * (90 + 840) + 140) / 10), round((2 * (340 + 70) + 140) / 10), round((2 * (340 + 840) + 140) / 10)
n3 = round(L / 250) + 1
barras = [dict(pos="N1", diam=6.3, qtd=n1, comp=cN1, forma=[(0, 0), (9, 0), (9, 84), (0, 84), (0, 0), (1.5, 1.5)],
               trechos=["9", "84", "9", "84"]),
          dict(pos="N2", diam=12.5, qtd=4, comp=round((L - 60) / 10), trechos=[f"{(L - 60) / 10:.0f}"]),
          dict(pos="N3", diam=6.3, qtd=n3, comp=cN3, forma=[(0, 0), (34, 0), (34, 7), (0, 7), (0, 0), (1.5, 1.5)],
               trechos=["34", "7", "34", "7"]),
          dict(pos="N4", diam=6.3, qtd=n3, comp=cN3, forma=[(0, 0), (34, 0), (34, 7), (0, 7), (0, 0), (1.5, 1.5)],
               trechos=["34", "7", "34", "7"]),
          dict(pos="N5", diam=10.0, qtd=2, comp=round((L - 60) / 10), trechos=[f"{(L - 60) / 10:.0f}"]),
          dict(pos="N6", diam=8.0, qtd=14, comp=cN6, forma=[(0, 0), (34, 0), (34, 84), (0, 84), (0, 0), (1.5, 1.5)],
               trechos=["34", "84", "34", "84"]),
          dict(pos="N7", diam=10.0, qtd=8, comp=94, forma=[(0, 6), (0, 0), (34, 0), (34, 6)], trechos=["6", "34", "6"])]
for b in barras:
    if b["pos"] in ("N3", "N4", "N2", "N5"):
        pass
barras[2]["trechos"] = barras[3]["trechos"] = ["34", "7", "34", "7"]
ta = pr.tabela_croqui(x0, y, barras)
tc = pr.tabela_cordoalhas(x0, ta["y_base"] - 4, [dict(pos="C1", diam=12.7, qtd=P["n_cord"], y=P["y_cord"],
                                                      forca=F_cord, isol=0)], P["L_pista"])
kg_cord = Ap * 1e4 * L / 1000 * 0.785
notas = [f"Concreto C{P['fck']}; liberar as cordoalhas só com fckj ≥ {P['fckj']} MPa (corpo de prova curado com a peça).",
         f"Cordoalhas CP-190 RB Ø12,7 aderentes, linha inferior da grade (y = {P['y_cord']} mm), colunas ±50/±100/±150; σpi = {P['sig_pi']} MPa; liberação gradual e simétrica.",
         f"Pista de {P['L_pista']} m: até 3 peças por linha; alongamento medido × teórico dentro de ±7%. Cordoalhas por peça: {f(kg_cord,0)} kg.",
         "Estribos N1 e N6 seguem a inclinação de 3% das pontas apenas no maciço (N6); no restante, verticais na fôrma.",
         "As alças AL-1 (laço de cordoalha) estão na folha 01 e são posicionadas entre os estribos N1, sem cortar armadura.",
         "Cobrimento 30 mm (CAA II). Dobramento conforme NBR 6118:2023 item 9.4.6. Medidas em cm na tabela e mm no desenho.",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(x0, tc["y_base"] - 4, notas, 180)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-TS01-2")
for a in avisos:
    print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos;", f"aço {ta['total_kg']:.0f} kg")
