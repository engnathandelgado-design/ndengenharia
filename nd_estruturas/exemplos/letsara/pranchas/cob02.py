"""ND-LET-COB02 — cobertura metálica: correntes flexíveis e rígidas, diagonais, contraventamento em X e memória das terças (A1).
Planta de enterçamento e ligações terça × viga: ND-LET-COB01."""
import json
import math
from prancha_nd import Prancha

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
LG = json.load(open(AQ + "ligacoes.json"))
CB = json.load(open(AQ + "cobertura_metalica.json"))
f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
YL = [0.0, 10.05, 19.705, 29.36, 38.865, 48.445, 58.025, 67.605, 76.81]
X0E, X0D = 0.325, 20.325
ST = LG["s_tercas"]
XT = [round((X0E + s - 0.027) * 1000) for s in ST] + [round((X0D + s - 0.027) * 1000) for s in ST]
VAO = round((YL[2] - YL[1]) * 1000)
pr = Prancha("A1", dict(cliente="MARQUE ENGENHARIA", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="COBERTURA METÁLICA — CORRENTES, DIAGONAIS, CONTRAVENTAMENTO E DIAGONAIS",
                        desenho="ND-LET-COB02", folha="05/05", fase="PARA APROVAÇÃO", rev="01"))
pr.revisao("01", pr.dados["data"], "desdobrada da COB01; correntes no meio da alma; diagonais no ST-1")
cr, tr, c1 = CB["correntes"], CB["terca"], CB["CT1"]

# ------------------------------------------------------------------ PLANTA DO VÃO TÍPICO (eixos 2–3) 1:100
v = pr.vista("PLANTA", (45, 415), 100, titulo="PLANTA DE TERÇAS — VÃO ENTRE OS EIXOS 2 E 3 (TÍPICO)",
             subtitulo="vão contraventado (2-3, 4-5, 5-6, 7-8); demais vãos iguais, sem as diagonais em X nem as CH-X")
for y in (0, VAO):
    v.ret(325, y - 200, 19450, 400, "VISTA"); v.ret(20325, y - 200, 19450, 400, "VISTA")
v.ret(19850, -200, 400, VAO + 400, "OCULTA")
for x in XT:
    v.linha((x, 0), (x, VAO), "METALICA")
q = [VAO / 4, VAO / 2, 3 * VAO / 4]
for xa, xb in ((XT[0], XT[12]), (XT[13], XT[25])):
    for y in q:
        v.linha((xa, y), (xb, y), "INDICACAO")
    ext = [(xa, xa + 1579), (xb - 1579, xb)]
    for (a, b) in ext:
        for y in q:
            v.ret(a, y - 60, b - a, 120, "METALICA")
    for xs, xd in ((xa + 1579, xa), (xb - 1579, xb)):
        for y, ys in ((q[0], 0), (q[1], 0), (q[2], VAO)):
            v.linha((xs, y), (xd, ys), "ARMADURA")
nos = [round((x - 0.027 + 0.0) * 1000) for x in LG["nos_contraventamento_x_esq"]]
NSUB = CB["contraventamento"]["subpaineis"]
for half in (0, 20000):
    for a, b in zip(nos[:-1], nos[1:]):
        for j in range(NSUB):
            ya = j * VAO / NSUB + (140 if j == 0 else 100); yb = (j + 1) * VAO / NSUB - (140 if j == NSUB - 1 else 100)
            v.linha((a + half + 140, ya), (b + half - 140, yb), "ARMADURA")
            v.linha((b + half - 140, ya), (a + half + 140, yb), "ARMADURA")
        for j in range(1, NSUB):                                   # nós CH-X nas terças das linhas de correntes
            for xn in (a + half, b + half):
                v.ret(xn - 125, j * VAO / NSUB - 100, 250, 200, "METALICA")
# correntes rígidas (tubo) em todos os espaços dos painéis contraventados
for xa_, xb_ in ((XT[0], XT[12]), (XT[13], XT[25])):
    for y in q:
        v.ret(xa_, y - 60, xb_ - xa_, 120, "METALICA")
v.chamada((XT[5], VAO * 0.1), (10, -24), "terça Ue 300×85×25×3,00 c/1579 (ZAR 345)")
v.chamada((XT[7], q[1]), (6, 54), "corrente flexível Ø12,5 (3 linhas)")
v.chamada((XT[0] + 800, q[0]), (6, -34), "corrente rígida (tubo Ø42,2) em todo o vão contraventado; nos demais vãos só no 1º espaço junto às ancoragens")
v.chamada((XT[0] + 790, q[1] / 2), (60, -46), "diagonal Ø16")
v.chamada((nos[2] + 1000, VAO * 0.15), (10, 94), f"contraventamento em X Ø12,5 A36 em subpainéis {CB['contraventamento']['painel_x_m']*1000:.0f} × L/{NSUB} (diag. ≈ {CB['contraventamento']['L_sub_m']:.1f} m): CH-T2 na viga, CH-X nas terças")
v.chamada((nos[3] + 125, VAO / 2 + 100), (14, 66), "CH-X (nó do X na linha de corrente) — ver DETALHE 8")
v.chamada((20050, VAO * 0.85), (12, 14), "I110 / pilar central")
v.cota_v([0, q[0], q[1], q[2], VAO], 0, -8)
v.cota_h([0] + XT[:3], 0, -6, total=False)

# ------------------------------------------------------------------ DETALHE 6 — CORRENTES (1:5)
c6 = pr.vista("DETALHE 6", (120, 230), 10, titulo="DETALHE 6 — CORRENTES", subtitulo="flexível (barra) e rígida (barra em tubo)")
for x in (0, 400, 800):
    c6.ret(x - 1.5, -150, 3, 300, "METALICA")
c6.linha((-60, 0), (460, 0), "ARMADURA")
for x in (0, 400):
    for sg in (-1, 1):
        c6.ret(x + sg * 12 - (10 if sg < 0 else 0), -10, 10, 20, "METALICA")
c6.ret(400 + 3, -21, 397 - 3, 42, "METALICA")
c6.linha((400, 0), (860, 0), "ARMADURA")
c6.chamada((200, 0), (-4, 18), "Ø12,5 rosca M12, porca e arruela dos 2 lados")
c6.chamada((600, 21), (-2, 30), "tubo Ø42,2×2,65 (corrente rígida)")
c6.cota_h([0, 400, 800], -150, -8, total=False)
c6.texto((-60, -400), "fora de escala no comprimento", "nota")

# ------------------------------------------------------------------ DETALHE 7 — ANCORAGEM DA DIAGONAL Ø16 NO ST-1 (planta 1:10)
d7 = pr.vista("DETALHE 7", (420, 200), 10, titulo="DETALHE 7 — DIAGONAL Ø16 E CORRENTE NO SUPORTE ST-1", subtitulo="planta no topo da viga; terça de borda (1ª e 13ª de cada metade)")
d7.ret(-200, -600, 400, 1200, "VISTA")                                   # topo da viga
d7.chapa(-75, -125, 150, 250, 0.2)                                        # IT-1
d7.chapa(-8, -110, 8, 220, 0.3)                                           # ST-1
for sg in (-1, 1):
    d7.poli([(0, sg * 10), (85, sg * 10), (85, sg * 600), (0, sg * 600)], "METALICA", True)
d7.linha((0, 0), (420, 640), "ARMADURA"); d7.interrupcao((420, 640), (520, 790), "ARMADURA")   # diagonal Ø16 até o nó da corrente (L/4) na 2ª terça
d7.linha((0, 0), (-120, 0), "ARMADURA"); d7.ret(-60, -14, 24, 28, "METALICA"); d7.ret(-100, -14, 24, 28, "METALICA")
d7.chamada((300, 457), (10, 10), "diagonal Ø16 rosca M16 até o nó da corrente (L/4) na terça seguinte")
d7.chamada((-70, 0), (-16, -14), "porca + contraporca no furo Ø18 do ST-1 (ver COB01)")
d7.chamada((40, 400), (14, 6), "terça de borda")
d7.cota_h([-200, -8, 0, 85, 200], -600, -10, total=False)

# ------------------------------------------------------------------ DETALHE 8 — CH-X: nó do X na terça (planta 1:5)
cx = CB["contraventamento"]
d8 = pr.vista("DETALHE 8", (655, 235), 5, titulo="DETALHE 8 — CH-X: NÓ DO CONTRAVENTAMENTO NA TERÇA", subtitulo="planta; chapa parafusada por baixo da mesa inferior da terça, nas linhas de correntes")
d8.chapa(-125, -100, 250, 200, 0.25)                                    # CH-X 9,5×250×200
d8.ret(0, -220, 85, 440, "OCULTA")                                      # mesa inferior da terça (por cima)
for yy in (-60, 60):
    d8.circulo((42, yy), 7, "METALICA")                                 # 2 M12 na mesa (Ø14)
for so, yo in ((110, 80), (-110, 80), (110, -80), (-110, -80)):
    d8.ret(so - 4.75, yo - 35, 9.5, 70, "METALICA")                     # orelhas 70×60×9,5
    d8.circulo((so, yo), 7, "METALICA")
d8.linha((0, -250), (0, 250), "EIXO")
for sg in (1, -1):
    d8.linha((sg * 110, 80), (sg * 300, 80 + 190 * math.tan(math.radians(cx["ang_graus"]))), "ARMADURA")
    d8.linha((sg * 110, -80), (sg * 300, -80 - 190 * math.tan(math.radians(cx["ang_graus"]))), "ARMADURA")
d8.cota_h([-125, -110, 0, 42, 85, 110, 125], -100, -10, total=False)
d8.cota_v([-100, -80, -60, 60, 80, 100], 125, 10, total=False)
d8.chamada((42, 60), (16, 12), "2 M12 8.8 na mesa inferior (furos Ø14)")
d8.chamada((-110, -80), (-14, -12), "4 orelhas 70×60×9,5, furo Ø14, a 38,5° (como a CH-T2)")
d8.chamada((250, 80 + 140 * math.tan(math.radians(cx["ang_graus"]))), (6, 8), "diagonal Ø12,5 rosca M12, porca + contraporca; esticador")
d8.chamada((-125, 0), (-12, 14), "CH-X chapa 9,5×250×200 A36")

# ------------------------------------------------------------------ tabelas
x0, y = pr.quadro[2] - 180, pr.quadro[3] - 6
vaos = [(f"{i+1}–{i+2}", round((YL[i + 1] - YL[i]) * 1000) - 20) for i in range(8)]
tabT = [[f"T-{k+1}", f"eixos {n}", f"{Lt}", "26", "X" if k in (1, 3, 4, 6) else "-"] for k, (n, Lt) in enumerate(vaos)]
y = pr.tabela(x0, y, "TERÇAS (26 por vão) — L = vão − 20, ver COB01", ["MARCA", "VÃO", "COMPR. (mm)", "QT", "DIAGONAIS X"], tabT, [22, 40, 44, 24, 50])
mem = [["Terça — gravidade", f"Md {tr['casos']['geral']['grav']['Msd']} / MRd {tr['casos']['geral']['grav']['MRd']} kN·m ({tr['MRd_grav']['modo']})", f"{f(tr['casos']['geral']['grav']['uso'],2)}"],
       ["Terça — sucção (faixa de borda)", f"Md {tr['casos']['borda']['suc']['Msd']} / MRd {tr['casos']['borda']['suc']['MRd']} kN·m, Lb = L/4", f"{f(tr['casos']['borda']['suc']['uso'],2)}"],
       ["Terça escora (N + M)", f"Nd {CB['terca_escora']['Nd']} kN + Md {CB['terca_escora']['Md']} kN·m", f"{f(CB['terca_escora']['interacao'],2)}"],
       ["Flecha (g + q)", f"{f(tr['flecha_gq_mm'],1)} ≤ L/180 = {f(tr['flecha_lim_mm'],1)} mm", f"{f(tr['flecha_gq_mm']/tr['flecha_lim_mm'],2)}"],
       ["Corrente flexível Ø12,5", f"{f(cr['F_max_kN'],1)} ≤ {f(cr['flexivel']['NtRd'],1)} kN", f"{f(cr['flexivel']['uso'],2)}"],
       ["Corrente rígida (tubo)", f"{f(cr['F_max_kN'],1)} ≤ {f(cr['rigida']['NcRd'],1)} kN", f"{f(cr['rigida']['uso'],2)}"],
       ["Diagonal Ø16", f"{f(cr['diagonal']['Td'],1)} ≤ {f(cr['diagonal']['NtRd'],1)} kN", f"{f(cr['diagonal']['uso'],2)}"],
       [f"X Ø12,5 (subpainel, {CB['contraventamento']['ang_graus']}°)", f"Vd painel {f(CB['contraventamento']['V_painel_d'],1)} kN → T {f(CB['contraventamento']['T_diag_d'],2)} ≤ {f(CB['contraventamento']['NtRd_12'],1)} kN", f"{f(CB['contraventamento']['uso_diag'],2)}"],
       ["Corrente rígida no vão com X", f"{f(CB['contraventamento']['corrente_rigida']['Nd'],1)} ≤ {f(CB['contraventamento']['corrente_rigida']['NcRd'],1)} kN", f"{f(CB['contraventamento']['corrente_rigida']['uso'],2)}"],
       ["M12 na alma (pressão de contato, t 3,0)", f"{f(c1['M12_alma']['Fd'],1)} ≤ {f(c1['M12_alma']['contato_alma_Rd'],1)} kN", f"{f(c1['M12_alma']['uso'],2)}"]]
y = pr.tabela(x0, y - 4, "MEMÓRIA (NBR 14762:2010 — MRD; NBR 8800:2008)", ["ITEM", "SOLICITAÇÃO × RESISTÊNCIA", "USO"], mem, [56, 106, 18])
par = [["M12 8.8 + porca + 2 arruelas", "terça × ST-1; mão-francesa (ver COB01)", "-", "1664"],
       ["Barra Ø12,5 rosca M12", "correntes flexíveis (vãos sem X)", "-", "≈ 1.200 m"],
       ["Ø12,5 M12 + esticador", f"contraventamento em X ({2*LG['contraventamento']['n_tirantes']} diagonais de ≈ {CB['contraventamento']['L_sub_m']:.1f} m)", "-", f"≈ {2*LG['contraventamento']['n_tirantes']*CB['contraventamento']['L_sub_m']:,.0f} m".replace(",", ".")],
       ["Tubo Ø42,2×2,65", "correntes rígidas (vãos com X + 1º espaço nos demais)", "-", "≈ 500 m"],
       ["CH-X 9,5×250×200 + 4 orelhas", "nós do X nas terças (linhas de correntes)", "-", f"{2*LG['contraventamento']['n_nos_CHX']}"],
       ["Barra Ø16 rosca M16", "diagonais das correntes", "-", "≈ 190 m"]]
y = pr.tabela(x0, y - 4, "PARAFUSOS E BARRAS", ["ITEM", "USO", "/VIGA", "OBRA"], par, [48, 90, 14, 28])
notas = ["Terças Ue 300×85×25×3,00 ZAR 345 galvanizadas, apoiadas nos suportes ST-1 (2 M12 por ponta) — ver ND-LET-COB01 (planta de enterçamento, comprimentos, folgas e furação).",
         "Três linhas de correntes por vão (L/4, L/2, 3L/4): com duas linhas a faixa de borda (Cpe −1,4) e a terça escora não passam.",
         "Correntes flexíveis Ø12,5 passam pelo furo Ø14 no meio da alma (a 150 do fundo). Correntes rígidas (tubo) em todos os espaços dos vãos contraventados (fazem de corda intermediária do X) e no 1º espaço junto a cada ancoragem nos demais vãos; diagonais Ø16 com rosca M16 ancoradas no furo Ø18 do ST-1 de borda (porca e contraporca).",
         f"Contraventamento em X Ø12,5 A36 em subpainéis curtos ({CB['contraventamento']['painel_x_m']*1000:.0f} × L/4, diagonal ≈ {CB['contraventamento']['L_sub_m']:.1f} m a {CB['contraventamento']['ang_graus']}°): nós na CH-T2 da viga e nas CH-X das terças; cada diagonal com esticador e porca + contraporca; as duas diagonais do X cruzam-se a 35/70 mm acima da viga, passando pela alma da terça intermediária (furos Ø16).",
         "Mão-francesa MF-1 em toda terça (ver COB01, detalhe 2).",
         "Furos d + 2 mm feitos na fábrica; proibido furar a terça galvanizada na obra sem retoque com tinta rica em zinco.",
         "Cpe da faixa de borda adotado −1,4 (NBR 6123, conferir com a geometria final da cobertura).",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(x0, y - 4, notas, 180)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-COB02")
for a in avisos:
    print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
