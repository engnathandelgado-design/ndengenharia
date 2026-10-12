"""ND-LET-COB02 — cobertura metálica: correntes flexíveis e rígidas, diagonais, contraventamento em X e memória das terças (A1).
Planta de enterçamento e ligações terça × viga: ND-LET-COB01."""
import json
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
                        conteudo="COBERTURA METÁLICA — CORRENTES, DIAGONAIS, CONTRAVENTAMENTO E MEMÓRIA DAS TERÇAS",
                        desenho="ND-LET-COB02", folha="05/05", fase="PARA APROVAÇÃO", rev="01"))
pr.revisao("01", pr.dados["data"], "desdobrada da COB01; correntes no meio da alma; diagonais no ST-1")
cr, tr, c1 = CB["correntes"], CB["terca"], CB["CT1"]

# ------------------------------------------------------------------ PLANTA DO VÃO TÍPICO (eixos 2–3) 1:100
v = pr.vista("PLANTA", (45, 415), 100, titulo="PLANTA DE TERÇAS — VÃO ENTRE OS EIXOS 2 E 3 (TÍPICO)",
             subtitulo="vão contraventado; demais vãos iguais, sem as diagonais em X")
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
for half in (0, 20000):
    for a, b in zip(nos[:-1], nos[1:]):
        v.linha((a + half + 140, 140), (b + half - 140, VAO - 140), "ARMADURA")
        v.linha((b + half - 140, 140), (a + half + 140, VAO - 140), "ARMADURA")
v.chamada((XT[5], VAO * 0.1), (0, -14), "terça Ue 300×85×25×3,00 c/1579 (ZAR 345)")
v.chamada((XT[7], q[1]), (6, 6), "corrente flexível Ø12,5 (3 linhas)")
v.chamada((XT[0] + 800, q[0]), (14, -16), "corrente rígida (tubo Ø42,2)")
v.chamada((XT[0] + 790, q[1] / 2), (30, -6), "diagonal Ø16")
v.chamada((nos[2] + 1000, VAO * 0.4), (10, 22), "contraventamento em X Ø12,5 A36 (CH-T2 na viga)")
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
       ["M12 na alma (pressão de contato, t 3,0)", f"{f(c1['M12_alma']['Fd'],1)} ≤ {f(c1['M12_alma']['contato_alma_Rd'],1)} kN", f"{f(c1['M12_alma']['uso'],2)}"]]
y = pr.tabela(x0, y - 4, "MEMÓRIA (NBR 14762:2010 — MRD; NBR 8800:2008)", ["ITEM", "SOLICITAÇÃO × RESISTÊNCIA", "USO"], mem, [56, 106, 18])
par = [["M12 8.8 + porca + 2 arruelas", "terça × ST-1; mão-francesa (ver COB01)", "-", "1664"],
       ["Barra Ø12,5 rosca M12", "correntes flexíveis", "-", "≈ 2.400 m"],
       ["Tubo Ø42,2×2,65", "correntes rígidas", "-", "≈ 230 m"],
       ["Barra Ø16 rosca M16", "diagonais das correntes", "-", "≈ 190 m"]]
y = pr.tabela(x0, y - 4, "PARAFUSOS E BARRAS", ["ITEM", "USO", "/VIGA", "OBRA"], par, [52, 70, 22, 36])
notas = ["Terças Ue 300×85×25×3,00 ZAR 345 galvanizadas, apoiadas nos suportes ST-1 (2 M12 por ponta) — ver ND-LET-COB01 (planta de enterçamento, comprimentos, folgas e furação).",
         "Três linhas de correntes por vão (L/4, L/2, 3L/4): com duas linhas a faixa de borda (Cpe −1,4) e a terça escora não passam.",
         "Correntes flexíveis Ø12,5 passam pelo furo Ø14 no meio da alma (a 150 do fundo). Correntes rígidas (tubo) no 1º espaço junto a cada ancoragem (beiral, eixo C e extremidade alta); diagonais Ø16 com rosca M16 ancoradas no furo Ø18 do ST-1 de borda (porca e contraporca).",
         "Mão-francesa MF-1 em toda terça (ver COB01, detalhe 2).",
         "Furos d + 2 mm feitos na fábrica; proibido furar a terça galvanizada na obra sem retoque com tinta rica em zinco.",
         "Cpe da faixa de borda adotado −1,4 (NBR 6123, conferir com a geometria final da cobertura).",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(x0, y - 4, notas, 180)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-COB02")
for a in avisos:
    print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
