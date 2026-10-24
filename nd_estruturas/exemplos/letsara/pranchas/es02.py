"""ND-LET-ES02 — escada metálica EXTERNA da fachada A (rev09c, DEC-053, decisão do Nathan 24/10: opção B — entra no projeto).
Escada em L do pátio à porta do 2º pavimento (+3,90): 5 espelhos ao longo de x, patamar +0,89 na quina, 17 espelhos ao longo da
fachada A e patamar de chegada +3,90 em frente à porta (90 × 214, y 0,89 a 1,79). Longarinas U, degraus em chapa xadrez dobrada,
vigas e pilaretes W 150 × 13,0 sobre blocos próprios BE-1 (não apoia nas placas), trava no P28 e X de contraventamento; porta nas
placas da vista H com ombreiras OM-2 internas. Tudo parafusado, galvanizado. Dados de geometria.ESCADA_EXT e escada_externa.json
(calc_escada_externa.py). Cotas em mm. A1."""
import json, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from prancha_nd import Prancha
from geometria import Y_LIN

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
EJ = json.load(open(AQ + "escada_externa.json"))
G = EJ["geometria"]
f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
M = lambda v: round(v * 1000)
XI, XEX = M(G["x"][0]), M(G["x"][1])
YC0, YC1 = (M(v) for v in G["y_chegada"])
YL0, YL1 = (M(v) for v in G["y_lance_cima"])
YP0, YP1 = (M(v) for v in G["y_patamar"])
XB0, XB1 = (M(v) for v in G["x_lance_baixo"])      # −1950 → −3070
ESP, PISO = G["espelho_m"] * 1000, G["piso_m"] * 1000
ZP, ZC = M(G["z_patamar"]), M(G["z_chegada"])
PY0, PY1 = (M(v) for v in G["porta_y"])
LC, LB = EJ["longarina_cima"], EJ["longarina_baixo"]

pr = Prancha("A1", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="ESCADA METÁLICA EXTERNA DA FACHADA A (PÁTIO → +3,90) — PLANTA, CORTES, BASES, PORTA E LISTA DE MATERIAL",
                        desenho="ND-LET-ES02", folha="01/01", fase="PARA APROVAÇÃO", rev="00"))
pr.revisao("00", "24/10/2026", "EMISSÃO INICIAL (DEC-053): ESCADA EXTERNA EM L NA FACHADA A, PORTA DO 2º PAV. NA VISTA H E OMBREIRAS OM-2")
Q = pr.quadro
XC = Q[2] - 190
pr.cabecalho_peca("ES", "ESCADA METÁLICA EXTERNA EM L — 22 ESPELHOS (17,73 × 28) — PATAMAR +0,89 E CHEGADA +3,90 NA PORTA DO 2º PAV.",
                  f"fachada A do anexo, entre a linha 1 e a linha 2 · largura {f(G['largura'] * 100, 0)} cm · massa {EJ['massa_kg']} kg · aço ASTM A36 / A572-50 galvanizado a fogo · tudo parafusado",
                  largura=XC - Q[0] - 10)


def pilar(v, x, y, bx, by):
    pts = [(x - bx / 2, y - by / 2), (x + bx / 2, y - by / 2), (x + bx / 2, y + by / 2), (x - bx / 2, y + by / 2)]
    v.poli(pts, "CORTADO", fechada=True); v.hachura(pts, "AR-CONC", 0.03)


# ------------------------------------------------------------------ PLANTA (1:50) — eixo x da obra na horizontal, y na vertical
v = pr.vista("PLANTA", (136, 505), 50, titulo="PLANTA DA ESCADA EXTERNA (FACHADA A)",
             subtitulo="lance de baixo, patamar +0,89, lance de cima ao longo da fachada e chegada +3,90 na porta", unidade="mm")
P_ = lambda x, y: (x, -y)                                # planta com a linha 1 em cima (y cresce para baixo)
for yy, nm in ((0, "1"), (M(Y_LIN[1]), "2")):
    v.eixo(P_(-3800, yy), P_(1500, yy), 400); v.circulo(P_(-4300, yy), 300, "VISTA"); v.texto(P_(-4300, yy), nm, "nota", "MIDDLE_CENTER")
v.eixo(P_(0, -1000), P_(0, 10800), 400); v.circulo(P_(0, -1500), 300, "VISTA"); v.texto(P_(0, -1500), "A", "nota", "MIDDLE_CENTER")
pilar(v, *P_(0, 0), 600, 400); pilar(v, *P_(0, M(Y_LIN[1])), 600, 400)
v.texto(P_(400, -250), "P28", "min", "BOTTOM_LEFT"); v.texto(P_(400, M(Y_LIN[1]) + 250), "P29", "min", "TOP_LEFT")
for y0_, y1_ in ((-200, PY0 - 20), (PY1 + 20, M(Y_LIN[1]) - 10)):              # placas da fachada A (vista H) e vão da porta
    v.poli([P_(-425, y0_), P_(-325, y0_), P_(-325, y1_), P_(-425, y1_)], "VISTA", fechada=True)
v.texto(P_(-375, (PY0 + PY1) / 2), "PORTA 90 × 214", "min", "MIDDLE_CENTER", rot=90)
for yj in (PY0 - 20 - 48, PY1 + 20):                                             # ombreiras OM-2 internas
    v.ret(*P_(-325, yj + 48), 152, 48, "CORTADO")
v.chamada(P_(-250, PY1 + 44), (14, -10), "OM-2 interna (det. 4)")
v.poli([P_(XEX, YC0), P_(XI, YC0), P_(XI, YP1), P_(XEX, YP1)], "METALICA", fechada=True)
v.poli([P_(XB1, YP0), P_(XEX, YP0), P_(XEX, YP1), P_(XB1, YP1)], "METALICA", fechada=True)
for j in range(17):
    yy = YL1 - j * PISO
    v.linha(P_(XEX, yy), P_(XI, yy), "VISTA")
for j in range(5):
    xx = XB1 + j * PISO
    v.linha(P_(xx, YP0), P_(xx, YP1), "VISTA")
xm = (XI + XEX) / 2
v.poli([P_(xm, YL1 - 150), P_(xm, YL0 + 150)], "COTA"); v.poli([P_(xm - 60, YL0 + 300), P_(xm, YL0 + 150), P_(xm + 60, YL0 + 300)], "COTA")
v.texto(P_(XEX - 250, (YL0 + YL1) / 2), "SOBE (17)", "min", "MIDDLE_CENTER", rot=90)
v.texto(P_((XB0 + XB1) / 2, YP0 - 250), "SOBE (5)", "min", "MIDDLE_CENTER")
v.texto(P_(xm, (YC0 + YC1) / 2), "chegada +3,90", "min", "MIDDLE_CENTER")
v.texto(P_(xm, (YP0 + YP1) / 2), "patamar +0,89", "min", "MIDDLE_CENTER")
for (ya, yb) in ((YC0, YC1), (YP0, YP1)):
    for xp in (XI - 50, XEX + 50):
        for yp in (ya + 60, yb - (120 if ya == YC0 else 60)):
            v.ret(*P_(xp - 50, yp + 74), 100, 148, "CORTADO")
            v.ret(*P_(xp - 300, yp + 300), 600, 600, "OCULTA")
v.chamada(P_(XEX + 50, YC0 + 60), (-14, 8), "PE-1 + bloco BE-1 (det. 2)")
v.chamada(P_(XEX + 50, YP1 - 60), (-14, -8), "PE-2 + bloco BE-1")
v.linha(P_(XI - 50, YC0 + 60), P_(XI - 50, 20), "METALICA")
v.chamada(P_(XI - 50, 110), (12, 10), "TR-1 trava no P28 (det. 3)")
v.linha(P_(XEX + 50, YC1 - 120), P_(XEX + 50, YP0 + 60), "OCULTA")
v.cota_h([XB1, XEX, XI, 0], -(YP1 + 700), -8, total=True)
v.cota_v([-YC0, -YC1, -YL1, -YP1], XB1 - 700, -10, total=True)
v.cota_v([-PY0, -PY1], 700, 8, total=False)

# ------------------------------------------------------------------ CORTE A-A (1:50) — ao longo da fachada (plano x = −1,20)
c = pr.vista("CORTE A-A", (218, 418), 50, titulo="CORTE A-A — LANCE DE CIMA (OLHANDO PARA A FACHADA A)",
             subtitulo="longarinas LE-1, degraus, patamar +0,89 e chegada +3,90; porta do 2º pav. ao fundo", unidade="mm")
c.linha((-600, 0), (YP1 + 1200, 0), "TERRENO")
for j in range(17):                                     # lance de cima: de y 6,92 (+0,89) a 2,44 (+3,90)
    y_ = YL1 - j * PISO
    z_ = ZP + (j + 1) * ESP
    c.poli([(y_, z_ - ESP), (y_, z_), (y_ - PISO, z_)], "VISTA")
c.linha((YL1, ZP + 50), (YL0, ZC - 150), "METALICA"); c.linha((YL1, ZP + 50 - LC["kg_m"] * 0 - 203), (YL0, ZC - 150 - 203), "METALICA")
for (ya, yb), z in (((YC0, YC1), ZC), ((YP0, YP1), ZP)):
    c.ret(ya, z - 6, yb - ya, 6, "METALICA")
    for yp in (ya + 60, yb - (120 if ya == YC0 else 60)):
        c.ret(yp - 50, 12, 100, z - 160, "METALICA")
        c.ret(yp - 300, -620, 600, 600, "CORTADO"); c.hachura([(yp - 300, -620), (yp + 300, -620), (yp + 300, -20), (yp - 300, -20)], "AR-CONC", 0.03)
c.ret(PY0, ZC, PY1 - PY0, 2140, "OCULTA"); c.texto(((PY0 + PY1) / 2, ZC + 1070), "porta", "min", "MIDDLE_CENTER", rot=90)
c.ret(-200, -300, 400, ZC + 1500, "VISTA"); c.texto((0, ZC + 1600), "P28", "min", "BOTTOM_CENTER")
c.linha((YC0 + 60, ZC - 160), (YC1 - 120, 400), "OCULTA"); c.linha((YC0 + 60, 400), (YC1 - 120, ZC - 160), "OCULTA")
c.cota_v([0, ZP, ZC], YP1 + 700, 10, total=False)
c.cota_h([YC0, YC1, YL1, YP1], -900, -10, total=True)
c.texto(((YC0 + YC1) / 2, ZC + 150), "chegada +3,90", "min", "BOTTOM_CENTER")
c.texto(((YP0 + YP1) / 2, ZP + 150), "patamar +0,89", "min", "BOTTOM_CENTER")

# ------------------------------------------------------------------ CORTE B-B (1:50) — lance de baixo (plano y = 7,67)
b = pr.vista("CORTE B-B", (507, 424), 50, titulo="CORTE B-B — LANCE DE BAIXO", subtitulo="5 espelhos, do pátio ao patamar +0,89", unidade="mm")
b.linha((XB1 - 800, 0), (XI + 600, 0), "TERRENO")
for j in range(5):
    x_ = XB1 + j * PISO
    z_ = (j + 1) * ESP
    b.poli([(x_, z_ - ESP), (x_, z_), (x_ + PISO, z_)], "VISTA")
b.linha((XB1, 90), (XEX, ZP - 100), "METALICA")
b.ret(XEX, ZP - 6, XI - XEX, 6, "METALICA")
for xp in (XEX + 50, XI - 50):
    b.ret(xp - 50, 12, 100, ZP - 160, "METALICA")
b.ret(-425, -300, 100, ZC + 600, "VISTA")
b.cota_h([XB1, XEX, XI], -300, -10, total=True)
b.cota_v([0, ZP], XB1 - 500, -10, total=False)

# ------------------------------------------------------------------ DETALHES 1:10 / 1:5
d2 = pr.vista("DETALHE 2", (110, 140), 10, titulo="DETALHE 2 — PILARETE NO BLOCO BE-1", subtitulo="chapa 200 × 200 × 12,5, 4 químicos M16, 2 L 102 (sem solda)", unidade="mm")
d2.linha((-500, 0), (500, 0), "TERRENO")
pts = [(-300, -600), (300, -600), (300, -20), (-300, -20)]
d2.poli(pts, "CORTADO", fechada=True); d2.hachura(pts, "AR-CONC", 0.05)
d2.ret(-100, -20, 200, 20, "VISTA"); d2.ret(-100, 0, 200, 12.5, "METALICA")
d2.ret(-50, 12.5, 100, 400, "METALICA")
for sg in (-1, 1):
    d2.linha((sg * 70, -140), (sg * 70, 40), "METALICA")
d2.cota_h([-300, -100, 100, 300], -600, -8, total=True)
d2.cota_v([-600, -20], -340, -8, total=False)
d2.chamada((70, -100), (28, -4), "4 chumbadores químicos M16 hef 120")
d2.chamada((200, -450), (16, -10), "BE-1 60 × 60 × 60 C25 (malha Ø8 c/15)")
d2.chamada((50, 300), (14, 8), "PE W 150 × 13,0 + 2 L 102 × 102 × 9,5 × 200 (2 M16)")
d2.chamada((-90, -10), (-14, 12), "graute 20 + chapa 12,5")
d3 = pr.vista("DETALHE 3", (330, 200), 5, titulo="DETALHE 3 — TRAVA TR-1 NO P28", subtitulo="tubo 80 × 80 × 4,75 + chapa 12,5 + 2 BR-M16 embutidas", unidade="mm")
pts = [(0, -200), (300, -200), (300, 200), (0, 200)]
d3.poli(pts, "CORTADO", fechada=True); d3.hachura(pts, "AR-CONC", 0.03)
d3.ret(-12.5, -100, 12.5, 200, "METALICA")
d3.ret(-450, -40, 437.5, 80, "METALICA")
for zz in (-60, 60):
    d3.linha((-20, zz), (150, zz), "METALICA")
d3.cota_h([-450, -12.5], -200, -8, total=False)
d3.chamada((100, 60), (44, 16), "2 BR-M16 8.8 embutidas 150 + grampo (fábrica do P28)")
d3.chamada((-250, 0), (-6, -24), "TR-1 tubo 80 × 80 × 4,75 (2 M16 na VE-1)")
d4 = pr.vista("DETALHE 4", (580, 60), 25, titulo="DETALHE 4 — OMBREIRA OM-2 (PORTA DO 2º PAV.)", subtitulo="U 152 interna do piso a +5,00; console L 102 da placa da fiada +3,75", unidade="mm")
d4.linha((-600, 0), (600, 0), "TERRENO")
d4.ret(-425, 0, 100, 3740, "VISTA"); d4.ret(-425, 5010, 100, 1240, "VISTA")
d4.ret(-425, 3760, 100, 1240, "VISTA")
d4.ret(-325, 12.5, 152, 4987, "METALICA"); d4.ret(-325, 0, 200, 12.5, "METALICA")
d4.ret(-325, 3740.5, 102, 9.5, "METALICA")
for zt in (3900, 4900):
    d4.ret(-325, zt - 38, 152, 76, "OCULTA")
d4.cota_v([0, 3750, 5000, 6250], 450, 8, total=False)
d4.chamada((-325, 3745), (-14, -6), "console L 102 × 102 × 9,5 + 2 M12 (ponta da placa H-03/H-04)")
d4.chamada((-325, 2000), (-14, 0), "OM-2 U 152 × 12,2 (interna, atrás das fiadas 0 e 2)")
d4.chamada((-325, 4900), (-14, 8), "2 travas L 76 até o P28 (+3,90 e +4,90)")
d4.chamada((-325, 6), (-14, -8), "chapa 200 × 200 × 12,5 + 4 químicos M12 (piso do térreo)")

# ------------------------------------------------------------------ lista e notas (sem tabela de verificações: memória MC09)
y = Q[3] - 6
lin = [[i["item"], i["desc"], str(i["qt"]), f(i["L_m"], 2), f(i["kg_m"], 1), f(i["qt"] * i["L_m"] * i["kg_m"], 0)] for i in EJ["lista"]]
om2 = [("OM-2", "ombreira interna U 152 × 12,2 (porta do 2º pav.)", 2, 5.0, 12.2), ("OM-T", "trava L 76 × 76 × 6,3 da OM-2 ao P28", 4, 1.2, 7.29),
       ("OM-C", "console L 102 × 102 × 9,5 × 110 da OM-2", 2, 0.11, 14.6), ("OM-B", "chapa de base 200 × 200 × 12,5 da OM-2", 2, 0.20, 19.6)]
lin += [[a, b_, str(q), f(L, 2), f(k, 1), f(q * L * k, 0)] for a, b_, q, L, k in om2]
massa = EJ["massa_kg"] + sum(q * L * k for _, _, q, L, k in om2)
lin.append(["", "parafusos M10/M12/M16 8.8 galvanizados, chumbadores químicos M12/M16, barras roscadas M16 embutidas no P28 (+3 %)", "", "", "", f(massa * 0.03, 0)])
lin.append(["", "TOTAL", "", "", "", f(massa * 1.03, 0)])
y = pr.tabela(XC, y, "LISTA DE MATERIAL — ESCADA EXTERNA E OMBREIRAS", ["ITEM", "DESCRIÇÃO", "QT", "L (m)", "kg/m", "kg"], lin, [14, 92, 10, 18, 16, 20], destaque_ultima=True)
lin2 = [["BE-1", "bloco de concreto C25 60 × 60 × 60 sob cada pilarete (malha Ø8 c/15 + 4 Ø8)", "8", f(8 * 0.216, 2) + " m³"]]
y = pr.tabela(XC, y - 4, "CONCRETO DE OBRA — BASES DA ESCADA", ["ITEM", "DESCRIÇÃO", "QT", "VOLUME"], lin2, [14, 110, 12, 34])
notas = [f"Cargas consideradas (NBR 6120:2019): sobrecarga {f(EJ['cargas']['q_kN_m2'])} kN/m² (escada com acesso público); guarda-corpo {f(EJ['cargas']['guarda_corpo_kN_m'])} kN/m horizontal no topo (NBR 14718:2019); peso próprio dos degraus {f(EJ['cargas']['g_degraus'], 2)} e dos patamares {f(EJ['cargas']['g_patamar'], 2)} kN/m².",
         f"Geometria do arquitetônico: {22} espelhos de {f(ESP / 10, 2)} cm e piso de {f(PISO / 10, 0)} cm (2e + p = {f(G['blondel_m'] * 100, 1)} cm); 5 espelhos no lance de baixo, patamar +0,89 na quina, 17 no lance de cima; chegada +3,90 em frente à porta. A escada fica 15 cm mais afastada da fachada que no arquitetônico, para passar livre das placas (face interna da escada a 2,5 cm da face externa das placas).",
         "A escada não apoia nas placas de fechamento: pilaretes em blocos próprios BE-1 (tensão no solo adotada 150 kPa — CONFIRMAR com a sondagem; se menor, aumentar o bloco); estabilidade pela trava TR-1 no P28 e pelo X de barras Ø12,5 com esticador no plano externo.",
         "PORTA DO 2º PAV. (vista H, ND-LET-PP-H): a fiada +3,75/+5,00 é cortada entre y 0,87 e 1,81 (placas H-03 PP-11 e H-04 PP-10); a faixa +5,00/+6,25 já é de esquadria. A ponta de cada placa junto ao vão apoia no console da ombreira OM-2 interna (U 152 do piso do térreo a +5,00, travada no P28 a +3,90 e +4,90) — nenhuma placa apoia em outra.",
         "Ligações todas parafusadas, SEM SOLDA (M10/M12/M16 8.8 galvanizados). Barras roscadas M16 da face externa do P28 (trava TR-1 e travas da OM-2) concretadas na fábrica do pilar (ND-LET-PL03).",
         "Aço: perfis W em ASTM A572 Gr. 50; U, cantoneiras, chapas, tubos e barras em ASTM A36; galvanização a fogo (NBR 6323) depois da fabricação; chapa xadrez antiderrapante. Guarda-corpo e corrimão por terceiros, parafusados nas longarinas e vigas.",
         "Montagem: blocos BE-1 curados → pilaretes e vigas dos patamares → longarinas e degraus → X e trava TR-1 → pisos. As OM-2 entram antes das placas da fiada +3,75 da vista H.",
         "Cotas em mm, níveis em m. Não medir no desenho."]
pr.notas(XC, y - 4, notas, 182)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-ES02")
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
for a in avisos:
    print(a)
