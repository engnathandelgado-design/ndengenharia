"""ND-LET-ES02 — escada metálica EXTERNA da fachada A (rev09c, DEC-053, decisão do Nathan 24/10: opção B — entra no projeto).
Escada em L do pátio à porta do 2º pavimento (piso pronto +3,95): 5 espelhos ao longo de x, patamar +0,90 na quina, 17 espelhos ao longo da
fachada A e patamar de chegada +3,95 em frente à porta (90 × 214, y 0,89 a 1,79). Longarinas U, degraus em chapa xadrez dobrada,
vigas W 150 × 9,2 e pilaretes em tubo sobre blocos próprios BE-1 (não apoia nas placas), X de contraventamento sob a chegada (rev 01: sem a trava TR-1); porta nas
placas da vista H com ombreiras OM-2 internas. Tudo parafusado, galvanizado. Dados de geometria.ESCADA_EXT e escada_externa.json
(calc_escada_externa.py). Cotas em mm. A1."""
import json, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from prancha_nd import Prancha
from geometria import Y_LIN, ESCADA_EXT as G, Z_PISO_PRONTO
import escadas_vista as E

EJ, X = E.EJ, E.EJ["externa"]
f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
M = lambda v: round(v * 1000)
XI, XEX = M(G["x_int"]), M(G["x_ext"])
YC0, YC1 = (M(v) for v in G["y_chegada"])
YL0, YL1 = (M(v) for v in G["y_lance_cima"])
YP0, YP1 = (M(v) for v in G["y_patamar"])
XB0, XB1 = (M(v) for v in G["x_lance_baixo"])
ESP, PISO = G["espelho"] * 1000, G["piso"] * 1000
ZC = M(Z_PISO_PRONTO); ZP = round(G["n_baixo"] * ESP)
PY0, PY1 = (M(v) for v in G["porta_y"])
CX = X["contraventamento"]

pr = Prancha("A1", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="ESCADA METÁLICA EXTERNA DA FACHADA A (PÁTIO → +3,95) — PLANTA, CORTES, BASES, PORTA E LISTA DE MATERIAL",
                        desenho="ND-LET-ES02", folha="01/01", fase="PARA APROVAÇÃO", rev="01"))
pr.revisao("00", "24/10/2026", "EMISSÃO INICIAL (DEC-053/055): ESCADA EXTERNA EM L NA FACHADA A, CHEGADA NO PISO PRONTO +3,95, PORTA NA VISTA H E OMBREIRAS OM-2")
pr.revisao("01", "24/10/2026", "DEC-060: GUARDA-CORPO 1,30 E CORRIMÃOS (ES03), LONGARINAS U 203/U 152, X DE CONTRAVENTAMENTO NO LUGAR DA TRAVA TR-1, LIGAÇÕES VERIFICADAS")
pr.revisao("09", "25/10/2026", "DEC-062: CORRIMÃO DUPLO 0,92 / 0,70 (RT CBMRS 11 + NBR 9050); DETALHES NAS ND-LET-ES04 / ES05")
Q = pr.quadro
XC = Q[2] - 190
pr.cabecalho_peca("ES", "ESCADA METÁLICA EXTERNA EM L — 22 ESPELHOS (17,95 × 28) — PATAMAR +0,90 E CHEGADA +3,95 NA PORTA DO 2º PAV.",
                  f"fachada A do anexo, entre a linha 1 e a linha 2 · largura {f(G['largura'] * 100, 0)} cm · massa {f(EJ['massa_kg']['externa'] * 1.03, 0)} kg com parafusos · ASTM A36 / A572-50 galvanizado a fogo · tudo parafusado",
                  largura=XC - Q[0] - 10)


def pilar(v, x, y, bx, by):
    pts = [(x - bx / 2, y - by / 2), (x + bx / 2, y - by / 2), (x + bx / 2, y + by / 2), (x - bx / 2, y + by / 2)]
    v.poli(pts, "CORTADO", fechada=True); v.hachura(pts, "AR-CONC", 0.03)


def camada(pc):
    c = E.cod(pc)
    if c == "graute":
        return None
    if "concreto" in pc["marca"]:
        return "OCULTA"
    if E.guarda(pc) or "-DG" in c or c == "CHE":
        return "VISTA"
    return "METALICA"


# ------------------------------------------------------------------ PLANTA (1:50) — linha 1 em cima (y cresce para baixo)
v = pr.vista("PLANTA", (Q[0] + 150, Q[3] - 75), 50, titulo="PLANTA DA ESCADA EXTERNA (FACHADA A)",
             subtitulo="peças do modelo 3D: lance de baixo, patamar +0,90, lance de cima e chegada +3,95; X sob a chegada (oculto)", unidade="mm")
P_ = lambda x, y: (x, -y)
PXY = lambda x, y, z: (x * 1000, -y * 1000)
for yy, nm in ((0, "1"), (M(Y_LIN[1]), "2")):
    v.eixo(P_(-3700, yy), P_(1500, yy), 400); v.circulo(P_(-4300, yy), 300, "VISTA"); v.texto(P_(-4300, yy), nm, "nota", "MIDDLE_CENTER")
v.eixo(P_(0, -900), P_(0, 10300), 400); v.circulo(P_(0, -1500), 300, "VISTA"); v.texto(P_(0, -1500), "A", "nota", "MIDDLE_CENTER")
from geometria import DY_CANTO as _DYC
YK_ = -round(_DYC * 1000)                                     # rev12 (opção D): pilar de canto 10 cm para fora da linha 1
pilar(v, *P_(0, YK_), 600, 400); pilar(v, *P_(0, M(Y_LIN[1])), 600, 400)
v.texto(P_(400, -250), "P28", "min", "BOTTOM_LEFT"); v.texto(P_(400, M(Y_LIN[1]) + 250), "P29", "min", "TOP_LEFT")
for y0_, y1_ in ((YK_ - 200, PY0 - 20), (PY1 + 20, M(Y_LIN[1]) - 10)):
    v.poli([P_(-425, y0_), P_(-325, y0_), P_(-325, y1_), P_(-425, y1_)], "VISTA", fechada=True)
v.chamada(P_(-60, (PY0 + PY1) / 2), (-26, 6), "porta 90 × 214")
E.projetar(v, PXY, lambda pc: E.externa(pc) or (pc["grupo"] == "Piso e fundações" and E.bbox(pc)[1][0] < 0),
           tf=lambda pc: "OCULTA" if E.cod(pc) in ("CX-1", "CX-O") or "concreto" in pc["marca"] else camada(pc))
def lab(pt, lado, dy, tx):
    xcol = -3500 if lado < 0 else 1500
    v.chamada(pt, ((xcol - pt[0]) / 50, dy), tx)
for cc, lado, dy, tx in (("VE-2", -1, 4, "VE-2 W 150 × 9,2"), ("VE-5", -1, 8, "VE-5 borda"), ("EE-LC ", 1, 0, "EE-LC U 203 × 17,1"),
                         ("EE-LB ", -1, -12, "EE-LB U 152 × 12,2"), ("BM-2", -1, 10, "BM-2 + BE-2"), ("VE-3", 1, -10, "VE-3 W 150 × 9,2"),
                         ("GE-1 corr", -1, 0, "GE-1 (1,30)"), ("GE-2 corr", 1, 6, "GE-2 corrimão (parede)"), ("PE ", 1, 14, "PE + BE-1 (det. 2)"),
                         ("CX-1", 1, -14, "X CX-1 (det. 3)")):
    lab(E.centro(cc, PXY), lado, dy, tx)
v.cota_h([XB1, XEX, XI, 0], -(YP1 + 700), -26, total=True)
v.cota_v([-PY0, -PY1], 450, 2, total=False)

# ------------------------------------------------------------------ CORTE A-A (1:50) — plano y-z, olhando para a fachada A (+x)
c = pr.vista("CORTE A-A", (Q[0] + 285, Q[3] - 238), 50, titulo="CORTE A-A — LANCE DE CIMA (OLHANDO PARA A FACHADA A)",
             subtitulo="peças do modelo 3D: longarinas, degraus, patamar +0,90, chegada +3,95, guarda-corpo 1,30 e X sob a chegada", unidade="mm")
YZ = lambda x, y, z: (y * 1000, z * 1000)
c.linha((-600, 0), (YP1 + 1000, 0), "TERRENO")
E.projetar(c, YZ, lambda pc: E.externa(pc) or (pc["grupo"] == "Piso e fundações" and E.bbox(pc)[1][0] < 0), tf=camada)
c.ret(PY0, ZC, PY1 - PY0, 2140, "OCULTA")
c.ret(YK_ - 200, -300, 400, ZC + 1800, "VISTA"); c.texto((YK_, ZC + 1900), "P28", "min", "BOTTOM_CENTER")
c.cota_v([0, ZP, ZC], YP1 + 600, 10, total=False)
c.cota_h([YC0, YL0, YL1, YP1], -900, -10, total=True)
c.texto(((YC0 + YL0) / 2, ZC + 1500), "chegada +3,95", "min", "BOTTOM_CENTER")
c.texto(((YP0 + YP1) / 2, ZP + 1500), "patamar +0,90", "min", "BOTTOM_CENTER")

# ------------------------------------------------------------------ CORTE B-B (1:50) — plano x-z, lance de baixo
b = pr.vista("CORTE B-B", (Q[0] + 330, Q[3] - 345), 50, titulo="CORTE B-B — LANCE DE BAIXO", subtitulo="5 espelhos, do pátio ao patamar +0,90 (pé na BM-2 sobre a BE-2)", unidade="mm")
XZ = lambda x, y, z: (x * 1000, z * 1000)
b.linha((XB1 - 700, 0), (500, 0), "TERRENO")
E.projetar(b, XZ, lambda pc: (E.externa(pc) or pc["grupo"] == "Piso e fundações") and E.bbox(pc)[0][1] > 6.5 and E.bbox(pc)[1][0] < 0, tf=camada)
b.ret(-425, -300, 100, 2000, "VISTA"); b.interrupcao((-425, 1500), (-325, 1500))
b.cota_h([XB1, XEX, XI], -800, -10, total=True)
b.cota_v([0, ZP], XB1 - 900, -6, total=False)

# ------------------------------------------------------------------ DETALHES 1:10 / 1:5
d2 = pr.vista("DETALHE 2", (104, 140), 10, titulo="DETALHE 2 — PILARETE NO BLOCO BE-1", subtitulo="chapa 200 × 200 × 12,5, 4 químicos M16, 2 L 102 (sem solda)", unidade="mm")
d2.linha((-500, 0), (500, 0), "TERRENO")
pts = [(-300, -600), (300, -600), (300, -20), (-300, -20)]
d2.poli(pts, "CORTADO", fechada=True); d2.hachura(pts, "AR-CONC", 0.05)
d2.ret(-100, -20, 200, 20, "VISTA"); d2.ret(-100, 0, 200, 12.5, "METALICA")
d2.ret(-30, 12.5, 60, 400, "METALICA")
for sg in (-1, 1):
    d2.linha((sg * 70, -140), (sg * 70, 40), "METALICA")
d2.cota_h([-300, -100, 100, 300], -600, -8, total=True)
d2.cota_v([-600, -20], -340, -8, total=False)
d2.chamada((70, -100), (28, -4), "4 chumbadores químicos M16 hef 120")
d2.chamada((200, -450), (16, -10), "BE-1 60 × 60 × 60 C25 (malha Ø8 c/15)")
d2.chamada((50, 300), (10, 8), "PE tubo 60 × 60 × 2 + 2 L 76 × 76 × 6,3 × 100")
d2.chamada((-90, -10), (-14, 12), "graute 20 + chapa 12,5")
d3 = pr.vista("DETALHE 3", (300, 135), 5, titulo="DETALHE 3 — CONTRAVENTAMENTO X (CX-1)", subtitulo=f"barra {CX['barra']}, garfo + pino M12 na orelha, esticador; Nd {f(CX['Nd'])} ≤ {f(CX['NRd'])} kN", unidade="mm")
d3.ret(-30, -200, 60, 400, "METALICA")
d3.ret(30, -50, 6.3, 100, "METALICA"); d3.ret(30, -3.15, 76, 6.3, "METALICA")
d3.poli([(80, 0), (300, 160)], "METALICA"); d3.poli([(80, -10), (300, 150)], "METALICA")
d3.ret(60, -12, 40, 24, "VISTA"); d3.circulo((68, 0), 6.5, "METALICA")
d3.linha((-45, 30), (45, 30), "METALICA")
d3.cota_h([30, 106], -60, -8, total=False)
d3.chamada((68, 0), (20, -22), "pino M12 do garfo (corte duplo)")
d3.chamada((40, 30), (12, 26), "1 M12 passante no tubo")
d3.chamada((33, -40), (-20, -18), "orelha L 76 × 76 × 6,3 × 100")
d3.chamada((250, 124), (10, 10), "barra Ø12,5 (pontas M12) + esticador")
d3.chamada((0, 150), (-16, 10), "PE tubo 60 × 60 × 2")
d4 = pr.vista("DETALHE 4", (590, 54), 25, titulo="DETALHE 4 — OMBREIRA OM-2 (PORTA DO 2º PAV.)", subtitulo="U 152 interna do piso a +5,00; console L 102 da placa da fiada +3,75", unidade="mm")
d4.linha((-600, 0), (600, 0), "TERRENO")
d4.ret(-425, 0, 100, 3740, "VISTA"); d4.ret(-425, 5010, 100, 1240, "VISTA")
d4.ret(-425, 3760, 100, 1240, "VISTA")
d4.ret(-325, 12.5, 152, 4987, "METALICA"); d4.ret(-325, 0, 200, 12.5, "METALICA")
d4.ret(-325, 3740.5, 102, 9.5, "METALICA")
for zt in (3900, 4900):
    d4.ret(-325, zt - 38, 152, 76, "OCULTA")
d4.cota_v([0, 3750, 5000, 6250], 450, 8, total=False)
d4.chamada((-325, 3745), (-14, -6), "console L 102 × 9,5 + 2 M12 (placa H-03/H-04)")
d4.chamada((-325, 2000), (-14, 0), "OM-2 U 152 × 12,2 (interna)")
d4.chamada((-325, 4900), (-14, 8), "travas L 76 (P28 ou soleira)")
d4.chamada((-325, 6), (-14, -8), "chapa 200 × 200 × 12,5 + 4 químicos M12")

# ------------------------------------------------------------------ lista e notas (verificações na memória MC09)
y = Q[3] - 6
lin = E.linhas_lista("externa", f)
om2 = [("OM-2", "ombreira interna U 152 × 12,2 L 5,00 (porta do 2º pav.)", 2, 5.0 * 12.2), ("OM-T", "trava L 76 × 76 × 6,3 da OM-2 (P28 / soleira)", 3, 1.2 * 7.29),
       ("OM-C", "console L 102 × 102 × 9,5 × 110 da OM-2", 2, 0.11 * 14.6), ("OM-B", "chapa de base 200 × 200 × 12,5 da OM-2", 2, 0.20 * 19.6)]
lin += [[a, b_, str(q), f(q * kg, 1)] for a, b_, q, kg in om2]
massa = EJ["massa_kg"]["externa"] + sum(q * kg for _, _, q, kg in om2)
lin.append(["", "parafusos M8/M10/M12/M16 8.8 galv., chumbadores químicos M12/M16, garfos, pinos e esticadores do X (+3 %)", "", f(massa * 0.03, 0)])
lin.append(["", "TOTAL", "", f(massa * 1.03, 0)])
y = pr.tabela(XC, y, "LISTA DE MATERIAL — ESCADA EXTERNA E OMBREIRAS", ["ITEM", "DESCRIÇÃO", "QT", "kg"], lin, [22, 118, 10, 20], h_lin=4.4, destaque_ultima=True)
n_be = sum(1 for pc in E.P if pc["marca"].startswith("BE-1 "))
lin2 = [["BE-1", "bloco de concreto C25 60 × 60 × 60 sob cada pilarete (malha Ø8 c/15 + 4 Ø8)", str(n_be), f(n_be * 0.216, 2) + " m³"],
        ["BE-2", "viga de concreto C25 1,80 × 0,40 × 0,40 sob o pé do lance de baixo (4 Ø10 + Ø5 c/20)", "1", f(1.8 * 0.16, 2) + " m³"]]
y = pr.tabela(XC, y - 4, "CONCRETO DE OBRA — BASES DA ESCADA", ["ITEM", "DESCRIÇÃO", "QT", "VOLUME"], lin2, [14, 110, 12, 34])
notas = [f"Cargas (NBR 6120:2019 / RT CBMRS 11): sobrecarga {f(EJ['cargas']['q_kN_m2'])} kN/m²; guarda-corpo {f(EJ['cargas']['guarda_corpo_kN_m'], 2)} kN/m no topo e {f(EJ['cargas']['fechamento_kPa'], 2)} kPa no fechamento; corrimão {f(EJ['cargas']['corrimao_kN'], 2)} kN; vento 0,8 kPa na faixa do guarda-corpo.",
         f"Geometria do arquitetônico: 22 espelhos de {f(ESP / 10, 2)} cm e piso de {f(PISO / 10, 0)} cm; 5 espelhos no lance de baixo, patamar +0,90, 17 no lance de cima; chegada +3,95 em frente à porta. Face interna da escada a 2,5 cm da face externa das placas.",
         f"Perfis no limite: longarinas {X['longarina_cima']['perfil']} no lance de cima (uso {f(X['longarina_cima']['uso'], 2)}; o U 152 não passa na flecha) e {X['longarina_baixo']['perfil']} no de baixo; vigas W 150 × 9,2 (o menor W); barrotes {X['barrote']['perfil']} (uso {f(X['barrote']['uso'], 2)}); pilaretes {X['pilarete_chegada']['perfil']} (uso {f(X['pilarete_chegada']['uso'], 2)}).",
         f"A escada não apoia nas placas: pilaretes em blocos BE-1 (σ no solo adotada 150 kPa — CONFIRMAR com a sondagem). Estabilidade lateral pelo X de barras Ø12,5 sob a chegada em 3 planos (Nd {f(CX['Nd'])} kN, uso {f(CX['uso'], 2)}), com garfo, pino e esticador — sem solda. A trava TR-1 da rev 00 foi retirada (não alcançava a face do P28).",
         "PORTA DO 2º PAV. (vista H, ND-LET-PP-H): a fiada +3,75/+5,00 é cortada no vão da porta; a ponta de cada placa apoia no console da ombreira OM-2 interna (U 152 do piso a +5,00). A OM-2 do lado do P28 é travada no pilar a +4,30 e +4,90; a outra, na primeira a +3,88 (abaixo da soleira) — nenhuma trava atravessa o vão.",
         f"Ligações todas parafusadas, SEM SOLDA, conferidas em escadas_detalhe.py (NBR 8800:2024 6.3): {len(EJ['ligacoes'])} ligações das duas escadas, {EJ['n_conflitos']} conflitos. Guarda-corpo 1,30 m e corrimãos nos dois lados (RT CBMRS 11): ND-LET-ES03.",
         "Aço: W em ASTM A572 Gr. 50; U, cantoneiras, chapas, tubos e barras em ASTM A36; galvanização a fogo (NBR 6323) depois da fabricação. Montagem: BE-1/BE-2 curados → pilaretes e vigas → X → longarinas e degraus → pisos → guarda-corpos. As OM-2 entram antes das placas da fiada +3,75.",
         "Cotas em mm, níveis em m. Não medir no desenho."]
pr.notas(XC, y - 4, notas, 182)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-ES02")
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
for a in avisos:
    print(a)
