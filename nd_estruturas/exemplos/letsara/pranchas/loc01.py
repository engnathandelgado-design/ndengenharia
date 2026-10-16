"""ND-LET-LOC01 — planta de locação de pilares e vigas de cobertura (geometria do R01), corte 1-1 do pórtico típico (linha 3)
e detalhes de apoio, com o RECUO DO PILAR acima do nível da viga/terças (cabeça do pilar 40 × 30 junto às placas, para o
rufo da platibanda ser contínuo e estreito, sem contornar os pilares). Cotas em mm na planta; níveis em m. A1."""
import json
import math
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from prancha_nd import Prancha
from geometria import Y_LIN, X_EIXO, PILARES_ESPECIAIS, Y_P13

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
LG = json.load(open(AQ + "ligacoes.json"))
f = lambda v, d=2: f"{v:.{d}f}".replace(".", ",")
YL = [round(y * 1000) for y in Y_LIN]
XA = {k: round(v * 1000) for k, v in X_EIXO.items()}
Lx, Ly = YL[-1], XA["E"]
I, C3 = 0.03, 1 / math.sqrt(1 + 0.03 ** 2)
Z0 = LG["Z0_TS"] * 1000
zf = lambda x: Z0 + I * x                                    # fundo da TS-01 (x em mm)
H_TS, T_TERCA = 900, 300
TELHA = round(sum(LG["platibanda"]["pacote"].values()) * 1000)   # rev03: TP40 + lã + zipada + painéis (260 mm)
LTS = round(LG["L_TS"] * 1000 * C3)
X0E = round(LG["X_PONTA_ESQ"] * 1000); X0D = Ly - X0E - LTS
Z_TOP_C = LG["Z_TOPO_I130"] * 1000
H_I = LG["H_I130"] * 1000
Z_I130 = Z_TOP_C
FOLGA_PL, E_PL = 25, 100                                     # placa por fora do pilar (rev03: 10 cm)
# rev03: o degrau do recuo é o ASSENTO da TS-01 (sem dente); acima dele só os 300 externos da cabeça sobem até +10,00
REC = dict(A=round(LG["REC"][0] * 1000), E=round(LG["REC"][1] * 1000), prof=300)
pr = Prancha("A1", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="LOCAÇÃO DE PILARES E VIGAS DE COBERTURA — CORTE DO PÓRTICO E RECUO DOS PILARES NA PLATIBANDA",
                        desenho="ND-LET-LOC01", folha="01/01", fase="PARA APROVAÇÃO", rev="03"))
pr.revisao("01", pr.dados["data"], "geometria do R01 (79,35 × 39,50 m); corte 1-1 refeito; recuo dos pilares acima da viga (a validar)")
pr.revisao("02", pr.dados["data"], "RECUO APROVADO; CONSOLOS SEM CHANFRO (h 44); P6/P7 FORA DO PROJETO")
pr.revisao("03", "14/10/2026", "TS-01 SEM DENTES NO RECUO E NO TOPO DA I130; COBERTURA REBAIXADA; I130; PLACAS 10 cm")
pr.revisao("04", "16/10/2026", "NBR 9062: SEM VT; PILARES LATERAIS 14 Ø20; VB 15×60 COM DENTE")

# ------------------------------------------------------------------ PLANTA 1:200 (horizontal = y da obra, vertical = x)
v = pr.vista("PLANTA", (62, 330), 200, titulo="PLANTA DE LOCAÇÃO DE PILARES E VIGAS DE COBERTURA", subtitulo="eixos e ordenadas do R01; contraventamento da cobertura em X")
pil = []
for i, y in enumerate(YL):
    pil.append(("P1" if i not in (0, 8) else "P1C", y, 0, 400, 600))
    pil.append(("P2" if i not in (0, 8) else "P2C", y, Ly, 400, 600))
for nome, x, y, bx, by in PILARES_ESPECIAIS:
    pil.append((nome, round(y * 1000), round(x * 1000), round(by * 1000), round(bx * 1000)))
for k, y in enumerate(YL):
    v.eixo((y, -1500), (y, Ly + 1500), 600)
    v.circulo((y, Ly + 2600), 700, "VISTA"); v.texto((y, Ly + 2600), str(k + 1), "nota", "MIDDLE_CENTER")
for nome, x in XA.items():
    v.eixo((-1500, x), (Lx + 1500, x), 600)
    v.circulo((-2600, x), 700, "VISTA"); v.texto((-2600, x), nome, "nota", "MIDDLE_CENTER")
for i in range(1, 8):
    for x0 in (X0E, X0D):
        v.ret(YL[i] - 200, x0, 400, LTS, "VISTA")
    v.texto((YL[i] + 350, X0E + LTS / 2), "TS-01", "min", rot=90); v.texto((YL[i] + 350, X0D + LTS / 2), "TS-01", "min", rot=90)
for (a, b), n in zip(((YL[1], YL[3]), (YL[3], round(Y_P13 * 1000)), (round(Y_P13 * 1000), YL[8])), ("V407", "V406", "V405")):
    v.ret(a + 275, XA["C"] - 200, b - a - 550, 400, "VISTA")
    v.texto(((a + b) / 2, XA["C"] - 700), f"{n} (I130)", "min", "TOP_CENTER")
for y in (YL[0], YL[8]):
    for xa, xb in zip(list(XA.values())[:-1], list(XA.values())[1:]):
        v.ret(y - 75, xa + 300, 150, xb - xa - 600, "OCULTA")
for k in (1, 6):
    for (xa, xb) in ((X0E, X0E + LTS), (X0D, X0D + LTS)):
        v.linha((YL[k], xa), (YL[k + 1], xb), "EIXO"); v.linha((YL[k], xb), (YL[k + 1], xa), "EIXO")
for nome, x, y, bx, by in pil:
    pts = [(x - bx / 2, y - by / 2), (x + bx / 2, y - by / 2), (x + bx / 2, y + by / 2), (x - bx / 2, y + by / 2)]
    v.poli(pts, "CORTADO", True); v.hachura(pts, "SOLID", 1)
for nome, x, y, bx, by in pil:
    if nome in ("P1", "P2", "P1C", "P2C"):
        continue
    v.texto((x + bx / 2 + 200, y + by / 2 + 150), nome, "min")
v.texto((YL[4], -900), "P1 40×60 (60 em x) nas linhas 2 a 8; P1C nos cantos", "min", "MIDDLE_CENTER")
v.texto((YL[4], Ly + 900), "P2 40×60 (60 em x) nas linhas 2 a 8; P2C nos cantos", "min", "MIDDLE_CENTER")
v.cota_h(YL, -1500, -14)
v.cota_v(list(XA.values()), Lx + 1500, 16)
v.chamada((YL[4] + 2500, X0D + 4000), (6, 8), "X = contraventamento Ø16 (vãos 2-3, 4-5, 5-6, 7-8)")
v.chamada((YL[8], XA["B"] + 3000), (30, 12), "VB-01 a VB-04 nas fachadas 1 e 9")
v.marcador_corte((YL[2] + 2500, -3400), (YL[2] + 2500, Ly + 3400), "1", lado=1)

# ------------------------------------------------------------------ CORTE 1-1 (linha 3, 1:150)
c = pr.vista("CORTE 1-1", (68, 150), 150, titulo="CORTE 1-1 — PÓRTICO TÍPICO (LINHA 3)",
             subtitulo="água única 3 % (sobe de A para E); TS-01 no recuo dos pilares e no topo da I130 (sem dentes); cobertura escondida na platibanda +10,00")


def pilar_lateral(v_, x_eixo, lado, z_rec):
    """Pilar 40×60 (60 em x) com recuo: abaixo de z_rec seção cheia; acima, só os 300 externos até +10,00. lado = sentido para dentro (+1 em A, −1 em E)."""
    xe = x_eixo - lado * 300                     # face externa
    xi = x_eixo + lado * 300                     # face interna
    xr = xe + lado * REC["prof"]                 # face interna da cabeça
    pts = [(xe, -1000), (xi, -1000), (xi, z_rec), (xr, z_rec), (xr, 10000), (xe, 10000)]
    v_.poli(pts, "CORTADO", True); v_.hachura(pts, "AR-CONC", 0.02)
    return xe, xi, xr


for x_e, lado, z_r in ((0, 1, REC["A"]), (Ly, -1, REC["E"])):
    xe, xi, xr = pilar_lateral(c, x_e, lado, z_r)
    xp = xe - lado * FOLGA_PL
    c.ret(min(xp, xp - lado * E_PL), 0, E_PL, 10000, "VISTA")                # placas por fora
c.linha((-2500, 0), (Ly + 2500, 0), "TERRENO")
for (xa, xb) in ((X0E, X0E + LTS), (X0D, X0D + LTS)):
    c.poli([(xa, zf(xa)), (xb, zf(xb)), (xb, zf(xb) + H_TS), (xa, zf(xa) + H_TS)], "VISTA", True)
c.ret(XA["C"] - 200, Z_I130 - H_I, 400, H_I, "CORTADO")
c.hachura([(XA["C"] - 200, Z_I130 - H_I), (XA["C"] + 200, Z_I130 - H_I), (XA["C"] + 200, Z_I130), (XA["C"] - 200, Z_I130)], "AR-CONC", 0.02)
for s in LG["s_tercas"]:
    for x0 in (X0E, X0D):
        x = x0 + s * 1000 * C3 - 27
        c.ret(x - 42, zf(x) + H_TS * C3 + 10, 85, T_TERCA, "METALICA")
zt = lambda x: zf(x) + (H_TS + 10 + T_TERCA + TELHA) * C3
c.linha((0, zt(0)), (Ly, zt(Ly)), "METALICA")
c.cota_h([0, XA["C"], Ly], -1000, -10)
c.cota_v([0, REC["A"], 10000], -2200, -10, total=False)
c.cota_v([0, REC["E"], 10000], Ly + 2200, 10, total=False)
c.cota_v([0, Z_I130 - H_I, Z_I130], XA["C"] + 1300, 8, total=False)
c.chamada((XA["C"] / 2, zf(XA["C"] / 2) + 450), (0, -16), f"TS-01 (I90, L {f(LG['L_TS'], 2)} m, sem dentes) — 3 %")
c.chamada((XA["C"], Z_I130 - H_I / 2), (10, -14), "I130 V407 (corte): TS-01 apoiadas no topo")
c.chamada((XA["C"] * 0.35, zt(XA["C"] * 0.35)), (4, 12), "terças Ue 300 + TP40 + lã + zipada + painéis (COB01)")
c.chamada((-150, 9500), (14, 12), "cabeça do pilar 40×30 (recuo)")
c.marcador_detalhe((0, REC["A"]), 1300, 1, ang=150)
c.marcador_detalhe((XA["C"], Z_I130 - 300), 1300, 2, ang=60)
c.marcador_detalhe((Ly, REC["E"]), 1100, 3, ang=30)

# ------------------------------------------------------------------ DETALHE 1 — APOIO NO PILAR P1 (eixo A) + RECUO (1:25)
Z1 = 6800


def det_lateral(nome, org, x_eixo, lado, z_rec, z0, titulo):
    """Detalhe 1:25 em coordenadas locais (x a partir do eixo do pilar); níveis pela TS real."""
    d = pr.vista(nome, org, 25, titulo=titulo, subtitulo="TS-01 no recuo; cabeça 40×30; placas até +10,00")
    z = lambda v_: v_ - z0
    zfl = lambda xl: zf(x_eixo + xl)                               # fundo da TS no x local
    xe, xi = -lado * 300, lado * 300
    xr = xe + lado * REC["prof"]
    pts = [(xe, z(z0)), (xi, z(z0)), (xi, z(z_rec)), (xr, z(z_rec)), (xr, z(10000)), (xe, z(10000))]
    d.poli(pts, "CORTADO", True); d.hachura(pts, "AR-CONC", 0.02)
    xs = xr + lado * 25                                             # ponta da TS-01 a 25 mm da face da cabeça
    zc = z_rec
    d.chapa(min(xs + lado * 40, xs + lado * 240), z(zc - 10), 200, 10)        # NEO-4
    xb = xs + lado * 1500
    d.poli([(xs, z(zfl(xs))), (xb, z(zfl(xb))), (xb, z(zfl(xb) + H_TS)), (xs + lado * 27, z(zfl(xs) + H_TS))], "VISTA", True)
    d.interrupcao((xb, z(zfl(xb))), (xb, z(zfl(xb) + H_TS)))
    d.ret(xs + lado * 140 - 12.5, z(zc - 300), 25, 600, "OCULTA")
    xt = xs + lado * 255
    d.ret(xt - 42, z(zfl(xt) + H_TS * C3 + 10), 85, T_TERCA, "METALICA")
    zt_ = lambda xl: zfl(xl) + (H_TS + 10 + T_TERCA + TELHA) * C3
    xp = xe - lado * FOLGA_PL
    d.ret(min(xp, xp - lado * E_PL), z(z0), E_PL, z(10000), "VISTA")
    calha = lado > 0                                               # lado baixo (A): calha; lado alto (E): só rufo
    xc0, xc1 = xr + lado * 30, xr + lado * 330
    xend = xr + lado * (180 if calha else 30)
    d.linha((xend, z(zt_(xend))), (xb, z(zt_(xb))), "METALICA"); d.linha((xend, z(zt_(xend) - TELHA)), (xb, z(zt_(xb) - TELHA)), "METALICA")
    zr = zt_(xend)
    if calha:
        zc_top = zr - TELHA - 10
        d.poli([(xc0, z(zc_top)), (xc0, z(zc_top - 150)), (xc1, z(zc_top - 150)), (xc1, z(zc_top))], "METALICA")
        d.chamada(((xc0 + xc1) / 2, z(zc_top - 150)), (lado * 12, -12), "calha 300 × 150 contínua, por dentro das cabeças")
    zcr = min(zr + 300, 10020)
    d.poli([(xp, z(zcr + 60)), (xp, z(zcr)), (xend - lado * 40 if calha else xend + lado * 120, z(zcr)),
            (xend - lado * 40 if calha else xend + lado * 120, z(zr) + (-40 if calha else 20))], "OCULTA")
    d.cota_h(sorted([xp - lado * E_PL, xe, xr, xi]), z(z0), -10, total=False)
    d.cota_v(sorted([z(z0), z(z_rec), z(10000)]), xp - lado * E_PL - lado * 300, -lado * 12, total=False)
    d.chamada((xr - lado * 150, z(10000) - 300), (-lado * 10, 8), "cabeça 40×30: só a parte externa sobe")
    d.chamada((xi, z(z_rec)), (lado * 10, -16), f"assento da TS-01 no recuo +{f(z_rec / 1000, 3)}")
    d.chamada((xr + lado * 15, z(zcr)), (lado * 14, 16), "contra-rufo reto nas placas (tracejado: entre pilares)")
    d.chamada((xs + lado * 140, z(zc - 250)), (lado * 22, -24), "NEO-4 + 2 PN-3 Ø25")
    d.chamada((xp - lado * E_PL / 2, z(z0) + 400), (-lado * 8, -10), "placas 125×10 por fora (folga 25)")
    return d


det_lateral("DETALHE 1", (414, 100), 0, 1, REC["A"], Z1, "DETALHE 1 — PILAR P1 (EIXO A, LADO BAIXO)")
det_lateral("DETALHE 3", (582, 154), Ly, -1, REC["E"], 7900, "DETALHE 3 — PILAR P2 (EIXO E, LADO ALTO)")

# ------------------------------------------------------------------ DETALHE 2 — APOIO CENTRAL NA I130 (1:25)
d2 = pr.vista("DETALHE 2", (735, 160), 25, titulo="DETALHE 2 — APOIO CENTRAL NO TOPO DA I130", subtitulo="duas TS-01 sem dente, NEO-3 + 2 PN-5 Ø20 cada")
zb = Z_I130 - H_I
z = lambda v_: v_ - zb
d2.poli([(-200, 0), (200, 0), (200, 250), (75, 330), (75, 1000), (200, 1080), (200, 1300), (-200, 1300), (-200, 1080), (-75, 1000), (-75, 330), (-200, 250)], "CORTADO", True)
for lado in (-1, 1):
    xs = XA["C"] + lado * 37.5
    xb = XA["C"] + lado * 1700
    d2.poli([(lado * 37.5, z(zf(xs))), (lado * 1700, z(zf(xb))), (lado * 1700, z(zf(xb) + H_TS)), (lado * 37.5, z(zf(xs) + H_TS))], "VISTA", True)
    d2.chapa(min(lado * 65, lado * 165), z(zf(XA["C"] + lado * 115)) - 10, 100, 10)
    d2.ret(lado * 115 - 10, z(Z_I130) - 300, 20, 600, "OCULTA")
d2.texto((0, z(Z_I130) + 1100), f"topo +{f(Z_I130 / 1000, 3)}", "min", "BOTTOM_CENTER")
d2.cota_v([0, H_I], -700, -10, total=False)
d2.chamada((0, 80), (-10, -14), "I130 V407 (40 × 130)")
d2.chamada((115, z(Z_I130) - 5), (6, -26), "NEO-3 100×300 + 2 PN-5 Ø20 por TS-01")

# ------------------------------------------------------------------ tabelas e notas
x0, y = pr.quadro[2] - 180, pr.quadro[3] - 6
tab = [["P1 / P2", "40×60", "14", "laterais (A e E), linhas 2–8", f"recuo +{f(REC['A']/1000)} (A) / +{f(REC['E']/1000)} (E)"],
       ["P1C / P2C", "40×60", "4", "cantos", "recuo nas duas faces internas"],
       ["P3 P4 P5 / P3 P14 P5", "40×60", "6", "fachadas 1 e 9", "recuo acima da VB"],
       ["P8 P8B / P8A", "40×60", "3", "linha 2 (mezanino / eixo C)", "-"],
       ["P9 P11 P12 / P10", "40×40 / 25×25", "5", "linha 4 (portões)", "-"],
       ["P13", "60×60", "1", "eixo C (apoio V405/V406)", "-"],
       ["P6 / P7", "25×40 / 60×40", "3", "anexo do eixo E", "fora do projeto (a definir)"]]
y = pr.tabela(x0, y, "PILARES (R01)", ["MARCA", "SEÇÃO", "QT", "POSIÇÃO", "CABEÇA"], tab, [38, 24, 10, 54, 54])
vg = [["TS-01", "I90", "14", f(LTS / 1000), "cobertura, linhas 2 a 8 (2 por linha), sem dentes"],
      ["V407", "I130", "1", f(LG["H_I130"] * 0 + (YL[3] - YL[1] - 550) / 1000), "eixo C, linha 2 → linha 4"],
      ["V406", "I130", "1", f((Y_P13 * 1000 - YL[3] - 550) / 1000), "eixo C, linha 4 → P13"],
      ["V405", "I130", "1", f((YL[8] - Y_P13 * 1000 - 550) / 1000), "eixo C, P13 → linha 9"],
      ["VB-01..04", "15×60", "8", "9,32–9,43", "bordas das fachadas 1 e 9, com dente (ND-LET-VB01)"]]
y = pr.tabela(x0, y - 4, "VIGAS DE COBERTURA", ["MARCA", "SEÇÃO", "QT", "L (m)", "POSIÇÃO"], vg, [22, 18, 10, 20, 110])
pr.notas(x0, y - 4, [
    "Geometria do R01 (locação de pilares): 79,35 m entre os eixos 1 e 9; 39,50 m entre os eixos A e E. Água única de 3 %, subindo de A para E; cobertura escondida pela platibanda +10,00 (placas por fora dos pilares).",
    f"RECUO DOS PILARES (rev03): o degrau do recuo é o assento da TS-01 (+{f(REC['A']/1000, 3)} no eixo A, +{f(REC['E']/1000, 3)} no eixo E), com neoprene NEO-4 200×300×10 e 2 pinos PN-3 Ø25; acima dele o pilar sobe só com os 300 mm externos (cabeça 40×30) até +10,00, segurando as placas da platibanda. Pacote da cobertura e calha por dentro da linha das cabeças; folga ≥ 15 cm do topo dos painéis solares ao topo da platibanda.",
    "TS-01 sem dentes: apoio direto no recuo dos pilares (eixos A e E, 27,5 cm) e no topo da I130 ou dos pilares P8A/P11 (eixo C, 16,25 cm), com neoprene e 2 pinos grauteados nos tubos TB-3 da viga.",
    "Contraventamento da cobertura em X Ø16 nos vãos 2-3 e 7-8 (ND-LET-COB02).",
    "Níveis em metros a partir do piso acabado; cotas em mm. Conferir a locação com o arquitetônico.",
    "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."], 180)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-LOC01")
for a in avisos:
    if a[0] == "ERRO" or "sobrep" in a[1]:
        print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos", REC)
