"""ND-LET-ES01 — escada metálica do mezanino (rev09, DEC-045): escada em U do térreo ao piso +3,90, 22 espelhos de 17,73 × piso 28,
patamar intermediário +1,95 e patamar de chegada +3,90 junto à linha 2. Longarinas U 152 × 12,2, degraus em chapa xadrez dobrada
sobre cantoneiras, vigas W 150 × 22,5 dos patamares parafusadas nas faces dos pilares (barras roscadas M16 embutidas), pilaretes
com chumbador químico; tudo parafusado na obra. Geometria e verificações de geometria.ESCADA e escada_metalica.json
(calc_escada_metalica.py). Cotas em mm. A1."""
import json, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from prancha_nd import Prancha
from geometria import ESCADA, P6_ESC, P7_ESC, P6_L2, Y_LIN, X_EIXO, ABERTURA
import renomear as RN

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
EJ = json.load(open(AQ + "escada_metalica.json"))
G = EJ["geometria"]
f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
M = lambda v: round(v * 1000)
X6, XE = M(G["x_faces"][0]), M(G["x_faces"][1])
BL = M(G["largura_lance"])
YP0, YP1 = (M(v) for v in G["y_patamar"])
YL0, YL1 = (M(v) for v in G["y_lances"])
YC0, YC1 = (M(v) for v in G["y_chegada"])
ESP, PISO = G["espelho_m"] * 1000, G["piso_m"] * 1000
ZP, ZC = M(G["z_patamar"]), 3900
N1 = round(ZP / ESP)                                   # espelhos por lance (11)
CH = EJ["chegada_apoios"]
XT, XW = M(CH["x_tubo"]), M(CH["x_W"])

pr = Prancha("A1", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="ESCADA METÁLICA DO MEZANINO (TÉRREO → +3,90) — PLANTAS, CORTE, LIGAÇÕES PARAFUSADAS E LISTA DE MATERIAL",
                        desenho="ND-LET-ES01", folha="01/01", fase="PARA APROVAÇÃO", rev="00"))
pr.revisao("00", "23/10/2026", "EMISSÃO INICIAL (DEC-045): ESCADA EM U, PATAMAR +1,95 E CHEGADA +3,90")
Q = pr.quadro
XC = Q[2] - 190
pr.cabecalho_peca("ES", "ESCADA METÁLICA EM U — 2 LANCES DE 11 ESPELHOS (17,73 × 28) — PATAMAR +1,95 E CHEGADA +3,90",
                  f"entre o PE-01 (P6 25 × 40), o PE-02 (P7 40 × 60) e a linha 2 · lance {f(BL / 10, 0)} cm · massa {EJ['massa_kg']} kg · aço ASTM A36 / A572-50, galvanizado · tudo parafusado na obra",
                  largura=XC - Q[0] - 10)


def pilar(v, x, y, bx, by, nome):
    pts = [(x - bx / 2, y - by / 2), (x + bx / 2, y - by / 2), (x + bx / 2, y + by / 2), (x - bx / 2, y + by / 2)]
    v.poli(pts, "CORTADO", fechada=True); v.hachura(pts, "AR-CONC", 0.03)


def wplanta(v, x0, x1, y, cam="METALICA"):
    v.ret(x0, y - 76, x1 - x0, 152, cam)


# ------------------------------------------------------------------ PLANTAS (1:50): +1,95 (lance 1 e patamar) e +3,90 (lance 2 e chegada)
for k, (xo, titulo, sub) in enumerate(((Q[0] + 45, "PLANTA NO PATAMAR +1,95", "lance 1 e patamar +1,95"),
                                       (Q[0] + 198, "PLANTA NA CHEGADA +3,90", "lance 2 e chegada +3,90"))):
    v = pr.vista(f"PLANTA {k + 1}", (xo - (X6 - 1900) / 50, Q[3] - 205 - 3300 / 50), 50, titulo=titulo, subtitulo=sub, unidade="mm")
    for yy, nm in ((M(Y_LIN[1]), "2"),):
        v.eixo((X6 - 1200, yy), (XE + 1200, yy), 400)
        v.circulo((X6 - 1700, yy), 300, "VISTA"); v.texto((X6 - 1700, yy), nm, "nota", "MIDDLE_CENTER")
    v.eixo((M(X_EIXO["E"]), 3000), (M(X_EIXO["E"]), 10000), 400)
    v.circulo((M(X_EIXO["E"]), 10700), 300, "VISTA"); v.texto((M(X_EIXO["E"]), 10700), "E", "nota", "MIDDLE_CENTER")
    pilar(v, M(P6_ESC[0]), M(P6_ESC[1]), 250, 400, "P6")
    pilar(v, M(P7_ESC[0]), M(P7_ESC[1]), 600, 400, "P7")
    pilar(v, M(P6_L2[0]), M(P6_L2[1]), 250, 400, "P6-L2")
    pilar(v, M(X_EIXO["E"]), M(Y_LIN[1]), 600, 400, "P2-L2")
    v.texto((M(P6_ESC[0]), M(P6_ESC[1]) - 300), "PE-01", "min", "TOP_CENTER")
    v.texto((M(P6_L2[0]), M(P6_L2[1]) + 300), "PE-03", "min", "BOTTOM_CENTER")
    v.ret(X6, YP0, XE - X6, YC1 - YP0, "OCULTA")                               # abertura da laje +3,90
    # lances: degraus (linhas de bocel)
    for (xa, xb), sobe in (((X6, X6 + BL), -1), ((XE - BL, XE), 1)):
        y_ini = YL1 if sobe < 0 else YL0
        cam = "VISTA" if (k == 0 and sobe < 0) or (k == 1 and sobe > 0) else "OCULTA"
        for j in range(N1):
            yy = y_ini + sobe * j * PISO
            v.linha((xa, yy), (xb, yy), cam)
        v.linha((xa + 25, YL0), (xa + 25, YL1), "METALICA"); v.linha((xb - 25, YL0), (xb - 25, YL1), "METALICA")
        xm = (xa + xb) / 2
        v.poli([(xm, y_ini + sobe * 150), (xm, y_ini + sobe * (N1 - 1) * PISO)], "COTA")
        v.poli([(xm - 60, y_ini + sobe * ((N1 - 1) * PISO - 150)), (xm, y_ini + sobe * (N1 - 1) * PISO), (xm + 60, y_ini + sobe * ((N1 - 1) * PISO - 150))], "COTA")
        v.texto((xm + 80, (YL0 + YL1) / 2), "SOBE" if cam == "VISTA" else "", "min", "MIDDLE_LEFT", rot=90)
    if k == 0:
        for yv in (YP0 + 80, YP1 - 80):
            wplanta(v, X6 + 10, XE - 10, yv)
        for xp in (X6 + 90, XE - 90):
            v.ret(xp - 76, YP1 - 80 - 76, 152, 152, "CORTADO")
        for j in range(5):
            v.linha((X6 + 300 + j * 600, YP0 + 160), (X6 + 300 + j * 600, YP1 - 160), "OCULTA")
        v.chamada((X6 + 300, YP0 + 80), (-10, -10), "VP-1 (fundo)")
        v.chamada((X6 + 90, YP1 - 80), (-10, 8), "VP-1 + PL-1")
        v.chamada((X6 + 300, (YP0 + YP1) / 2), (-12, 2), "CH-P 6,3")
        v.chamada((X6 + 25, YL1 - 150), (-8, 10), "pé (det. 4)")
    else:
        for yv in (YC0 + 80, YC1 - 80):
            wplanta(v, X6 + 10, XE - 10, yv)
        v.ret(XT - 40, YC0 + 80 - 40, 80, 80, "CORTADO")
        v.ret(XW - 76, YC0 + 80 - 76, 152, 152, "CORTADO")
        v.chamada((XT, YC0 + 80), (-4, -26), "PL-3")
        v.chamada((XW, YC0 + 80), (-4, -40), "PL-2")
        v.chamada((X6 + 300, YC0 + 80), (-10, -8), "VP-1 (balanço 1,45)")
        v.chamada((X6 + 300, YC1 - 80), (-10, 6), "VP-1 (fundo)")
    v.cota_h([X6, X6 + BL, XE], YP0 - 300, -10, total=False)
    v.cota_v([YP0, YP1, YL1, YC1], XE + 700, 10, total=True)

# ------------------------------------------------------------------ CORTE A-A (1:50): lance 1 em vista, lance 2 ao fundo
c = pr.vista("CORTE A-A", (Q[0] + 350 - (YP0 - 1300) / 50, Q[3] - 175), 50, titulo="CORTE A-A — PELO LANCE 1 (OLHANDO PARA O EIXO E)",
             subtitulo="longarinas U 152, degraus, patamar +1,95 e chegada +3,90; lance 2 ao fundo (oculto)", unidade="mm")
c.linha((YP0 - 1200, 0), (YC1 + 1200, 0), "TERRENO")
for j in range(N1):                                     # lance 1 (de y 8,35 para 5,55): degraus em vista
    y_ = YL1 - j * PISO
    z_ = (j + 1) * ESP
    c.poli([(y_, z_ - ESP), (y_, z_), (y_ - PISO, z_)], "VISTA")
c.linha((YL1 + 60, 90), (YL0 - 60, ZP - 100), "METALICA"); c.linha((YL1 + 60, 90 - 150), (YL0 - 60, ZP - 100 - 152), "METALICA")
for j in range(N1):                                     # lance 2 ao fundo
    y_ = YL0 + j * PISO
    z_ = ZP + (j + 1) * ESP
    c.poli([(y_, z_ - ESP), (y_, z_), (y_ + PISO, z_)], "OCULTA")
for (ya, yb), z in (((YP0, YP1), ZP), ((YC0, YC1), ZC)):
    c.ret(ya, z - 6, yb - ya, 6, "METALICA")
    for yv in (ya + 80, yb - 80):
        c.ret(yv - 51, z - 158, 102, 152, "METALICA")
c.ret(YP1 - 80 - 76, 0, 152, ZP - 158, "METALICA")
c.ret(YC0 + 80 - 40, 0, 80, ZC - 158, "OCULTA")
c.ret(M(P6_ESC[1]) - 200, -300, 400, ZC + 600, "VISTA"); c.interrupcao((M(P6_ESC[1]) - 200, ZC + 300), (M(P6_ESC[1]) + 200, ZC + 300))
c.ret(M(Y_LIN[1]) - 200, -300, 400, ZC + 600, "VISTA"); c.interrupcao((M(Y_LIN[1]) - 200, ZC + 300), (M(Y_LIN[1]) + 200, ZC + 300))
c.ret(M(P6_ESC[1]) - 200 - 1000, ZC - 250, 1000, 250, "CORTADO")                # laje +3,90 do lado da linha 1 (LA-03 / VM-04)
c.cota_v([0, ZP, ZC], YC1 + 700, 10, total=False)
c.cota_h([YP0, YP1, YL1, YC1], -300, -10, total=True)
c.texto(((YP0 + YP1) / 2, ZP + 150), "patamar +1,95", "min", "BOTTOM_CENTER")
c.texto(((YC0 + YC1) / 2, ZC + 150), "chegada +3,90", "min", "BOTTOM_CENTER")

# ------------------------------------------------------------------ DETALHES 1:5
d1 = pr.vista("DETALHE 1", (Q[0] + 50, Q[1] + 150), 5, titulo="DETALHE 1 — DEGRAU", subtitulo="DG-1 sobre L 38; 2 M10 por ponta", unidade="mm")
d1.ret(0, 0, 48.5, 152, "METALICA"); d1.ret(48.5, 100, 38, 4.8, "METALICA"); d1.ret(48.5, 100, 4.8, 38, "METALICA")
d1.poli([(48.5, 104.8), (360, 104.8), (360, 60)], "METALICA")
for zz in (115, 128):
    d1.circulo((24, zz), 5, "METALICA")
d1.cota_v([0, 100, 152], -20, -8, total=False); d1.cota_h([48.5, 360], 104.8, 10, total=False)
d1.chamada((24, 128), (6, 24), "2 M10 8.8")
d1.chamada((250, 104.8), (8, 12), "DG-1 xadrez 4,75")
d1.chamada((40, 40), (20, -12), "LG-1 U 152 × 12,2")
d2 = pr.vista("DETALHE 2", (Q[0] + 250, Q[1] + 150), 5, titulo="DETALHE 2 — VIGA NO PILAR", subtitulo="chapa de topo 12,5 + 4 M16 embutidas", unidade="mm")
pts = [(-200, -150), (0, -150), (0, 250), (-200, 250)]
d2.poli(pts, "CORTADO", fechada=True); d2.hachura(pts, "AR-CONC", 0.03)
d2.ret(0, -50, 12.5, 250, "METALICA"); d2.ret(12.5, 0, 300, 152, "METALICA")
for zz in (10, 140):
    d2.linha((-150, zz), (40, zz), "METALICA")
d2.cota_v([-50, 0, 152, 200], 330, 10, total=False)
d2.chamada((-75, 140), (-50, 40), "4 BR-M16 embutidas + grampo")
d2.chamada((150, 76), (10, 34), "VP-1 W 150 (solda de oficina)")
d3 = pr.vista("DETALHE 3", (Q[0] + 425, Q[1] + 150), 5, titulo="DETALHE 3 — BASE DO PILARETE", subtitulo="chapa 12,5 + 4 M12 químicos", unidade="mm")
d3.ret(-100, 0, 200, 12.5, "METALICA"); d3.ret(-76, 12.5, 152, 250, "METALICA")
for xx in (-70, 70):
    d3.linha((xx, -100), (xx, 40), "METALICA")
d3.linha((-250, 0), (250, 0), "TERRENO")
d3.cota_h([-100, -70, 70, 100], -100, -8, total=False)
d3.chamada((70, -60), (12, -8), "chumbador químico M12 hef 100 (piso)")
d4 = pr.vista("DETALHE 4", (Q[0] + 555, Q[1] + 150), 5, titulo="DETALHE 4 — PÉ DA LONGARINA", subtitulo="chapa 200 × 150 × 12,5 + 2 M12", unidade="mm")
d4.ret(-100, 0, 200, 12.5, "METALICA"); d4.poli([(-60, 12.5), (60, 12.5), (60 + 152 * 0.6, 12.5 + 152)], "METALICA")
d4.linha((-250, 0), (250, 0), "TERRENO")
for xx in (-60, 60):
    d4.linha((xx, -100), (xx, 40), "METALICA")
d4.chamada((60, -60), (12, -8), "2 chumbadores químicos M12 hef 100")

# ------------------------------------------------------------------ tabelas e notas
y = Q[3] - 6
lin = [[i["item"], i["desc"], str(i["qt"]), f(i["L_m"], 2), f(i["kg_m"], 1), f(i["qt"] * i["L_m"] * i["kg_m"], 0)] for i in EJ["lista"]]
lin.append(["", "parafusos M10/M12/M16 8.8, chumbadores químicos M12, barras roscadas M16 embutidas (+3 %)", "", "", "", f(EJ["massa_kg"] * 0.03, 0)])
lin.append(["", "TOTAL", "", "", "", f(EJ["massa_kg"] * 1.03, 0)])
y = pr.tabela(XC, y, "LISTA DE MATERIAL — ESCADA METÁLICA", ["ITEM", "DESCRIÇÃO", "QT", "L (m)", "kg/m", "kg"], lin, [14, 92, 10, 18, 16, 20], destaque_ultima=True)
ver = [["Longarina LG-1 (flexão, NBR 8800)", f(EJ["longarina"]["uso"], 2), f"flecha {f(EJ['longarina']['flecha_mm'])} ≤ {f(EJ['longarina']['lim_L350_mm'])} mm; f1 {f(EJ['longarina']['f1_Hz'])} Hz"],
       ["VP-1 frente do patamar", f(EJ["patamar_frente"]["uso"], 2), f"flecha {f(EJ['patamar_frente']['flecha_mm'])} ≤ {f(EJ['patamar_frente']['lim_L350_mm'])} mm"],
       ["VP-1 frente da chegada (balanço 1,45 m)", f(EJ["chegada_frente"]["uso"], 2), f"flecha {f(EJ['chegada_frente']['flecha_mm'])} mm"],
       ["Pilaretes PL-1 / PL-2 / PL-3", f(max(p_["uso"] for p_ in EJ["pilaretes"]), 3), "compressão com flambagem"],
       ["Ligação na face do pilar (4 M16)", f(EJ["ligacoes_face"][0]["uso"], 3), "cisalhamento nas barras roscadas"]]
y = pr.tabela(XC, y - 4, "VERIFICAÇÕES (calc_escada_metalica.py)", ["ELEMENTO", "USO", "OBS."], ver, [70, 16, 84])
notas = [f"Cargas (NBR 6120:2019): sobrecarga {f(EJ['cargas']['q_kN_m2'])} kN/m² (escada com acesso público); peso próprio dos degraus {f(EJ['cargas']['g_degraus'], 2)} e dos patamares {f(EJ['cargas']['g_patamar'], 2)} kN/m². ELU 1,4 G + 1,5 Q; flecha L/350 (NBR 8800:2024 Anexo B).",
         f"Geometria: {G['n_espelhos']} espelhos de {f(ESP / 10, 2)} cm e piso de {f(PISO / 10, 0)} cm (2e + p = {f(G['blondel_m'] * 100, 1)} cm, NBR 9050 / NBR 9077); lance de {f(BL / 10, 0)} cm; patamar intermediário +1,95 e chegada no piso +3,90 do mezanino (abertura da laje entre o P6, o P7 e a linha 2 — ND-LET-LA01).",
         "Ligações na obra todas parafusadas (M10/M12/M16 8.8 galvanizados); soldas só de oficina (chapa de topo das VP-1, chapa do pé da longarina). Barras roscadas M16 das faces do P6, do P7, do P6 da linha 2 e do P2 concretadas na fábrica dos pilares (ND-LET-PE01, PE02, PE03 e PL).",
         "Aço: perfis W em ASTM A572 Gr. 50; U, cantoneiras, chapas e tubos em ASTM A36; galvanização a fogo após a fabricação. Chapa xadrez antiderrapante.",
         "Guarda-corpo e corrimão (h ≥ 1,10 m e 0,92 m, NBR 9077 / NBR 14718) fora do escopo estrutural: fixar nas longarinas e nas vigas VP-1 com parafusos, sem furar os pilares.",
         "Montagem: depois da capa do +3,90 com fck ≥ 20 MPa — VP-1 de fundo nas faces dos pilares → pilaretes e VP-1 de frente → longarinas e degraus → pisos dos patamares. Conferir na obra as cotas dos pilares antes de fabricar.",
         "Cotas em mm, níveis em m. Não medir no desenho."]
pr.notas(XC, y - 4, notas, 182)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-ES01")
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
for a in avisos:
    print(a)
