"""ND-LET-LOC01 — planta de locação de pilares e vigas de cobertura, corte do pórtico e detalhes de apoio."""
import sys, math
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha

YL = [0, 10050, 19705, 29360, 38865, 48445, 58025, 67605, 76810]       # eixos 1..9 (mm)
XA = {"A": 0, "B": 9870, "C": 20050, "D": 29630, "E": 40100}           # eixos A..E
f = lambda v: f"{v:.2f}".replace(".", ",")
pr = Prancha("A1", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="LOCAÇÃO DE PILARES, VIGAS DE COBERTURA E DETALHES DE APOIO",
                        desenho="ND-LET-LOC01", folha="01/01", fase="PARA APROVAÇÃO"))

# ------------------------------------------------------------------ PLANTA 1:200 (x = comprimento, y = largura)
v = pr.vista("PLANTA", (55, 300), 200, titulo="PLANTA DE LOCAÇÃO E VIGAS DE COBERTURA", subtitulo="pilares e vigas pré-moldadas")
Lx, Ly = YL[-1], XA["E"]
pil = []   # (nome, x, y, bx, by)
for i, yl in enumerate(YL):
    pil.append(("P1" if 0 < i < 8 else ("P1A" if i == 0 else "P1C"), yl, 0, 400, 600))
    pil.append(("P2" if 0 < i < 8 else ("P2A" if i == 0 else "P2C"), yl, Ly, 400, 600))
for nome, xx in (("P3", "B"), ("P4", "C"), ("P5", "D")):
    pil.append((nome, 0, XA[xx], 600, 400))
for nome, xx in (("P15", "B"), ("P14", "C"), ("P16", "D")):
    pil.append((nome, YL[8], XA[xx], 600, 400))
pil += [("P8", YL[1], XA["B"], 400, 600), ("P8A", YL[1], XA["C"], 400, 600), ("P8B", YL[1], XA["D"], 400, 600),
        ("P11", YL[3], XA["C"], 500, 500), ("P13", YL[5] + 4600, XA["C"], 500, 500)]
# eixos
for k, yl in enumerate(YL):
    v.eixo((yl, -1500), (yl, Ly + 1500), 600)
    v.texto((yl - 250, Ly + 3500), str(k + 1), "sub")
for nome, xx in XA.items():
    v.eixo((-1500, xx), (Lx + 1500, xx), 600)
    v.texto((-4200, xx - 250), nome, "sub")
# vigas I90 de cobertura (TS-01): eixo lateral → centro, nas linhas 2..8
for i in range(1, 8):
    for (ya, yb) in ((300, XA["C"] - 225), (XA["C"] + 225, Ly - 300)):
        v.linha((YL[i] - 200, ya), (YL[i] - 200, yb), "VISTA"); v.linha((YL[i] + 200, ya), (YL[i] + 200, yb), "VISTA")
    v.texto((YL[i] + 350, XA["C"] / 2), "TS-01", "nota", rot=90)
    v.texto((YL[i] + 350, XA["C"] + 8000), "TS-01", "nota", rot=90)
# viga central I110 (V407, V406, V405) no eixo C
apoios_c = [YL[1], YL[3], YL[5] + 4600, YL[8]]
nomes_c = ["V407", "V406", "V405"]
for (a, b), n in zip(zip(apoios_c[:-1], apoios_c[1:]), nomes_c):
    v.linha((a + 300, XA["C"] - 200), (b - 300, XA["C"] - 200), "VISTA")
    v.linha((a + 300, XA["C"] + 200), (b - 300, XA["C"] + 200), "VISTA")
    v.texto(((a + b) / 2 - 1500, XA["C"] - 900), f"{n} (I110)", "nota")
# vigas de borda das fachadas (VB-01, 15×70) e contraventamento (barras Ø16 A36)
for yl in (YL[0], YL[8]):
    v.linha((yl, 300), (yl, Ly - 300), "OCULTA")
for (ia, ib) in ((0, 1), (1, 2), (3, 4), (4, 5), (6, 7), (7, 8)):
    for (xa, xb) in ((0, XA["C"]), (XA["C"], Ly)):
        v.linha((YL[ia], xa), (YL[ib], xb), "EIXO"); v.linha((YL[ia], xb), (YL[ib], xa), "EIXO")
for nome, x, y, bx, by in pil:
    v.ret(x - bx / 2, y - by / 2, bx, by, "CORTADO")
    v.hachura([(x - bx / 2, y - by / 2), (x + bx / 2, y - by / 2), (x + bx / 2, y + by / 2), (x - bx / 2, y + by / 2)], "SOLID", 1)
    v.texto((x + 450, y + (500 if y < Ly / 2 else -1300)), f"{nome} {bx//10}×{by//10}", "min")
v.cota_h(YL, -1500, -14)
v.cota_v(list(XA.values()), Lx + 1500, 16)
v.chamada((YL[4] + 2000, XA["B"] + 2400), (8, 6), "X = contraventamento Ø16 A36")
v.marcador_corte((YL[2] + 2500, -2500), (YL[2] + 2500, Ly + 2500), "1", lado=1)

# ------------------------------------------------------------------ CORTE 1-1 (pórtico típico, 1:150)
c = pr.vista("CORTE 1-1", (70, 110), 150, titulo="CORTE 1-1 — PÓRTICO TÍPICO (EIXO 3)", subtitulo="água única 3%, platibanda nos pilares")
zP1, zP2, zC, zT = 8080, 9280, 8680, 10000
for x0, bx in ((0, 600), (Ly, 600)):
    c.ret(x0 - bx / 2, 0, bx, zT, "CORTADO")
c.ret(XA["C"] - 200, zC - 1100, 400, 1100, "CORTADO")                 # I110 em corte
c.ret(XA["C"] - 200, zC - 1100 - 50, 400, 50, "METALICA")             # (neoprene no consolo do pilar central)
for (xa, za, xb, zb) in ((300 + 25, zP1, XA["C"] - 15, zC), (XA["C"] + 15, zC, Ly - 325, zP2)):
    c.poli([(xa, za), (xb, zb), (xb, zb + 900), (xa, za + 900)], "VISTA", fechada=True)
c.linha((-2000, 0), (Ly + 2000, 0), "TERRENO")
c.cota_v([0, zP1, zP1 + 900, zT], -1200, -12)
c.cota_v([0, zC - 1100, zC, zC + 900], XA["C"] - 1500, -10)
c.cota_v([0, zP2, zT], Ly + 1200, 12)
c.cota_h([0, XA["C"], Ly], 0, -10)
c.chamada((XA["C"] / 2, (zP1 + zC) / 2 + 450), (0, 10), "TS-01 (I90) — 3%")
c.chamada((XA["C"], zC - 550), (14, -12), "I110 (corte)")
c.marcador_detalhe((0, zP1 + 300), 1300, 1, ang=150)
c.marcador_detalhe((XA["C"], zC), 1300, 2, ang=60)
c.marcador_detalhe((XA["C"] + 2500, zC - 600), 1300, 3, ang=30)

# ------------------------------------------------------------------ DETALHES 1:25
# DET 1 — I90 no consolo do pilar lateral (lado baixo), platibanda. Origem local z = +6,08 m
d1 = pr.vista("DETALHE 1", (500, 320), 25, titulo="DETALHE 1 — APOIO LATERAL", subtitulo="I90 no consolo do pilar · platibanda")
z = lambda v_: v_ - 6080
d1.ret(-300, 0, 600, z(10000), "CORTADO")
d1.poli([(300, z(7680)), (650, z(7680)), (650, z(8040)), (300, z(8040))], "CORTADO", fechada=True)
d1.ret(325, z(8040), 300, 10, "METALICA")
d1.poli([(325, z(8080)), (1500, z(8080) + 35), (1500, z(8980) + 35), (325, z(8980))], "VISTA", fechada=True)
d1.interrupcao((1500, z(8080) + 35), (1500, z(8980) + 35))
d1.linha((475, z(7700)), (475, z(8980)), "OCULTA")
d1.ret(-460, 120, 100, z(10000) - 120, "VISTA")
d1.chamada((475, z(8600)), (16, 12), "pino Ø25 grauteado (TB-1)")
d1.chamada((500, z(8045)), (20, -4), "neoprene 300×150×10 + CH-A1")
d1.chamada((650, z(7800)), (16, -14), "consolo do pilar")
d1.chamada((0, z(9700)), (-16, 10), "platibanda (pilar até +10,00)")
d1.chamada((-410, 800), (-14, -6), "placa de fechamento")
d1.cota_v([z(7680), z(8040), z(8080), z(8980), z(10000)], -700, -12)
d1.cota_h([-300, 300, 650], z(7680), -10)
d1.texto((-300, -400), "+6,08 (trecho)", "min")

# DET 2 — duas I90 sobre a I110 no centro. Origem local z = +7,58 m (fundo da I110)
d2 = pr.vista("DETALHE 2", (655, 290), 25, titulo="DETALHE 2 — APOIO CENTRAL", subtitulo="duas TS-01 sobre a I110")
d2.poli([(-200, 0), (200, 0), (200, 150), (75, 230), (75, 860), (200, 940), (200, 1100),
         (-200, 1100), (-200, 940), (-75, 860), (-75, 230), (-200, 150)], "CORTADO", fechada=True)
d2.ret(-195, 1100, 175, 10, "METALICA"); d2.ret(20, 1100, 175, 10, "METALICA")
d2.poli([(-1400, 1110 + 41), (-15, 1110), (-15, 2010), (-1400, 2010 + 41)], "VISTA", fechada=True)
d2.poli([(15, 1110), (1400, 1110 + 41), (1400, 2010 + 41), (15, 2010)], "VISTA", fechada=True)
d2.interrupcao((-1400, 1151), (-1400, 2051)); d2.interrupcao((1400, 1151), (1400, 2051))
d2.linha((-100, 700), (-100, 2010), "OCULTA"); d2.linha((100, 700), (100, 2010), "OCULTA")
d2.chamada((-100, 1700), (-14, 14), "pino Ø25 (TB-1)")
d2.chamada((100, 1105), (16, -14), "neoprene 175×300×10")
d2.chamada((0, 500), (16, -10), "I110 em corte")
d2.cota_h([-200, -15, 15, 200], 2051, 12)
d2.cota_v([0, 1100, 2010], 1550, 10)

# DET 3 — I110 no pilar central (P11): consolos dos dois lados e TS-01 no topo. Origem local z = +6,00 m
d3 = pr.vista("DETALHE 3", (500, 140), 25, titulo="DETALHE 3 — PILAR CENTRAL P11", subtitulo="I110 nos consolos · TS-01 no topo")
z = lambda v_: v_ - 6000
d3.ret(-250, 0, 500, z(8680), "CORTADO")
for s_ in (-1, 1):
    d3.poli([(s_ * 250, z(7180)), (s_ * 600, z(7180)), (s_ * 600, z(7570)), (s_ * 250, z(7570))], "CORTADO", fechada=True)
    d3.poli([(s_ * 275, z(7580)), (s_ * 1900, z(7580)), (s_ * 1900, z(8680)), (s_ * 275, z(8680))], "VISTA", fechada=True)
    d3.interrupcao((s_ * 1900, z(7580)), (s_ * 1900, z(8680)))
d3.ret(-200, z(8680), 400, 10, "METALICA")
d3.poli([(-200, z(8690)), (200, z(8690)), (200, z(9590)), (-200, z(9590))], "VISTA", fechada=True)
d3.chamada((450, z(7300)), (14, -12), "consolo (2x)")
d3.chamada((1200, z(8100)), (10, 14), "V406 / V407 (I110)")
d3.chamada((0, z(9200)), (14, 12), "TS-01 (corte)")
d3.cota_v([0, z(7180), z(7580), z(8680), z(9590)], -900, -12)

# ------------------------------------------------------------------ tabela de pilares e notas
x0, y = pr.quadro[2] - 180, pr.quadro[3] - 6
tab = [["P1 / P2", "40×60", "14", "60 ⊥ fachada lateral", "+8,08 / +9,28"],
       ["P1A P2A P1C P2C", "40×60", "4", "60 ⊥ fachada lateral", "cantos"],
       ["P3 P4 P5 / P14 P15 P16", "40×60", "6", "60 ⊥ fachada frente/fundo", "+8,68 (VB)"],
       ["P8 P8B", "40×60", "2", "mezanino", "+3,15 / +6,55"],
       ["P8A", "40×60", "1", "apoio TS-01 e V407", "+8,68"],
       ["P11 P13", "50×50", "2", "apoio I110 + TS-01", "+7,58 / +8,68"]]
y = pr.tabela(x0, y, "PILARES", ["MARCA", "SEÇÃO", "QT", "ORIENTAÇÃO", "CONSOLO"], tab, [44, 18, 10, 64, 44])
vg = [["TS-01", "I90", "14", "19,71", "cobertura, linhas 2 a 8"],
      ["V407", "I110", "1", "≈ 18,7", "eixo C, 2–4"],
      ["V406", "I110", "1", "≈ 23,1", "eixo C, 4–P13"],
      ["V405", "I110", "1", "≈ 23,2", "eixo C, P13–9"],
      ["VB-01", "15×70", "8", "≈ 9,9", "bordas das fachadas 1 e 9"]]
y = pr.tabela(x0, y - 4, "VIGAS DE COBERTURA", ["MARCA", "SEÇÃO", "QT", "COMPR. (m)", "POSIÇÃO"], vg, [22, 20, 12, 26, 100])
pr.notas(x0, y - 4, [
    "Água única de 3%, caindo do eixo E (alto) para o eixo A (baixo). Topo de todos os pilares de borda em +10,00 (platibanda).",
    "TS-01 apoia em consolo nos pilares laterais (DET 1) e, no centro, sobre a I110 (DET 2) ou no topo dos pilares P8A, P11 e P13 (DET 3).",
    "Todos os apoios: neoprene fretado + pino Ø25 grauteado — a TS-01 trabalha como tirante entre os pilares (placas dos dois lados).",
    "Contraventamento da cobertura em barras redondas A36 Ø16 nos vãos 1-2, 2-3, 4-5, 5-6, 7-8 e 8-9; terças ligadas aos pilares das fachadas.",
    "Pilares das fachadas de frente e fundo com o lado de 60 perpendicular à fachada (placas penduradas).",
    "Níveis em metros a partir do piso acabado; cotas em mm. Locação dos pilares conforme R01 — conferir com o arquitetônico.",
    "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."], 180)
print(pr.salvar("/home/claude/letsara/pranchas/ND-LET-LOC01"))
