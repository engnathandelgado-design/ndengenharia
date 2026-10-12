"""ND-LET-COB01 — cobertura metálica: terças Ue, correntes flexíveis e rígidas, diagonais, ligação terça × viga (A1)."""
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
                        conteudo="COBERTURA METÁLICA — TERÇAS, CORRENTES, DIAGONAIS E LIGAÇÃO TERÇA × VIGA",
                        desenho="ND-LET-COB01", folha="04/04", fase="PARA APROVAÇÃO"))
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
v.chamada((nos[2] + 1000, VAO * 0.4), (10, 22), "contraventamento em X Ø12,5 A36 (CH-T2)")
v.chamada((20050, VAO * 0.85), (12, 14), "I110 / pilar central")
v.cota_v([0, q[0], q[1], q[2], VAO], 0, -8)
v.cota_h([0] + XT[:3], 0, -6, total=False)

# ------------------------------------------------------------------ DETALHE 5 — LIGAÇÃO TERÇA × VIGA (1:10)
d = pr.vista("DETALHE 5", (300, 175), 10, titulo="DETALHE 5 — LIGAÇÃO TERÇA × VIGA E MÃO-FRANCESA",
             subtitulo="corte paralelo às terças, no plano da terça")
H = 900
pts = [(-200, 0), (200, 0), (200, 150), (75, 230), (75, 700), (200, 780), (200, 900), (-200, 900), (-200, 780), (-75, 700),
       (-75, 230), (-200, 150)]
d.poli(pts, "CORTADO", fechada=True); d.hachura(pts, "AR-CONC", 0.03)
d.ret(-100, H - 12.5, 200, 12.5, "METALICA")                      # CH-T1
d.ret(-180, 0, 360, 12.5, "METALICA")                             # CH-MF
d.poli([(-100, H), (-100, H + 9.5), (100, H + 9.5), (100, H)], "METALICA")
d.ret(-4.75, H + 9.5, 9.5, 92.5, "METALICA")                      # aba vertical CT-1
for sg in (1, -1):
    d.ret(sg * 5 if sg > 0 else -1200, H + 12.5, 1195, 300, "METALICA")   # terças em vista
    d.linha((sg * 5, H + 12.5 + 85 - 3), (sg * 1200, H + 12.5 + 85 - 3), "OCULTA")
    xa, za = sg * 150, -12.5
    xb, zb = sg * 1070, H + 12.5
    d.linha((xa, za), (xb, zb), "METALICA"); d.linha((xa + sg * 35, za), (xb + sg * 35, zb), "METALICA")
    d.ret(xa - 32 if sg > 0 else xa - 32, -76, 64, 64, "METALICA")   # OR-1
    for zz in (40, 80):
        d.circulo((sg * 50, H + 12.5 + zz), 7, "METALICA")
d.chamada((60, H + 60), (16, 24), "CT-1 + 2 M16 na CH-T1 + 2 M12 por terça")
d.chamada((-600, H + 200), (-10, 18), "terça Ue 300 (alma em vista)")
d.chamada((-600, 450), (-14, 8), "MF-1 L 50×5 (45°)")
d.chamada((150, -44), (40, -16), "OR-1 parafusada na luva M16 da CH-MF")
d.chamada((1070, H + 12.5), (8, -12), "M12 na mesa inferior da terça")
d.cota_h([-1070, -150, 0, 150, 1070], -76, -8, total=False)
d.cota_v([0, H, H + 12.5, H + 312.5], -1230, -8, total=False)

# ------------------------------------------------------------------ SEÇÃO DA TERÇA com furações (1:5)
s5 = pr.vista("SEÇÃO DA TERÇA", (560, 255), 2.5, titulo="TERÇA — SEÇÃO E FURAÇÃO", subtitulo="Ue 300×85×25×3,00 ZAR 345")
s5.poli([(85, 275), (85, 300), (0, 300), (0, 0), (85, 0), (85, 25)], "METALICA")
for z, dm in ((40, 14), (80, 14)):
    s5.circulo((0, z), dm / 2, "METALICA")
s5.circulo((0, 75), 7, "METALICA")
s5.circulo((0, 35), 8, "OCULTA"); s5.circulo((0, 70), 8, "OCULTA")
s5.circulo((42, 0), 7, "METALICA")
s5.cota_v([0, 35, 40, 70, 75, 80, 300], -10, -8, total=False)
s5.cota_h([0, 42, 85], 300, 8, total=False)
s5.chamada((0, 80), (10, 10), "furos da CT-1 (Ø14) nas pontas")
s5.chamada((0, 75), (14, -4), "corrente Ø14 a 75 (perto da mesa comprimida na sucção)")
s5.chamada((0, 35), (16, -22), "Ø16 a 35/70: terça do meio do painel em X")
s5.chamada((42, 0), (10, -34), "Ø14 na mesa — mão-francesa")

# ------------------------------------------------------------------ DETALHE 6 — CORRENTES (1:5)
c6 = pr.vista("DETALHE 6", (535, 95), 10, titulo="DETALHE 6 — CORRENTES", subtitulo="flexível (barra) e rígida (barra em tubo)")
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

# ------------------------------------------------------------------ tabelas
x0, y = pr.quadro[2] - 180, pr.quadro[3] - 6
vaos = [(f"{i+1}–{i+2}", round((YL[i + 1] - YL[i]) * 1000) - 10) for i in range(8)]
tabT = [[f"T-{k+1}", f"eixos {n}", f"{Lt}", "26", "X" if k in (1, 3, 4, 6) else "-"] for k, (n, Lt) in enumerate(vaos)]
y = pr.tabela(x0, y, "TERÇAS (26 por vão)", ["MARCA", "VÃO", "COMPR. (mm)", "QT", "FUROS X"], tabT, [22, 40, 44, 24, 50])
mem = [["Terça — gravidade", f"Md {tr['casos']['geral']['grav']['Msd']} / MRd {tr['casos']['geral']['grav']['MRd']} kN·m ({tr['MRd_grav']['modo']})", f"{f(tr['casos']['geral']['grav']['uso'],2)}"],
       ["Terça — sucção (faixa de borda)", f"Md {tr['casos']['borda']['suc']['Msd']} / MRd {tr['casos']['borda']['suc']['MRd']} kN·m, Lb = L/4", f"{f(tr['casos']['borda']['suc']['uso'],2)}"],
       ["Terça escora (N + M)", f"Nd {CB['terca_escora']['Nd']} kN + Md {CB['terca_escora']['Md']} kN·m", f"{f(CB['terca_escora']['interacao'],2)}"],
       ["Flecha (g + q)", f"{f(tr['flecha_gq_mm'],1)} ≤ L/180 = {f(tr['flecha_lim_mm'],1)} mm", f"{f(tr['flecha_gq_mm']/tr['flecha_lim_mm'],2)}"],
       ["Corrente flexível Ø12,5", f"{f(cr['F_max_kN'],1)} ≤ {f(cr['flexivel']['NtRd'],1)} kN", f"{f(cr['flexivel']['uso'],2)}"],
       ["Corrente rígida (tubo)", f"{f(cr['F_max_kN'],1)} ≤ {f(cr['rigida']['NcRd'],1)} kN", f"{f(cr['rigida']['uso'],2)}"],
       ["Diagonal Ø16", f"{f(cr['diagonal']['Td'],1)} ≤ {f(cr['diagonal']['NtRd'],1)} kN", f"{f(cr['diagonal']['uso'],2)}"],
       ["M12 na alma (pressão de contato)", f"{f(c1['M12_alma']['Fd'],1)} ≤ {f(c1['M12_alma']['contato_alma_Rd'],1)} kN", f"{f(c1['M12_alma']['uso'],2)}"]]
y = pr.tabela(x0, y - 4, "MEMÓRIA (NBR 14762:2010 — MRD; NBR 8800:2008)", ["ITEM", "SOLICITAÇÃO × RESISTÊNCIA", "USO"], mem, [56, 106, 18])
par = [["M16 8.8 + porca + 2 arruelas", "CT-1 × CH-T; OR-1 × CH-MF", "52", "728"],
       ["M12 8.8 + porca + 2 arruelas", "terça × CT-1; mão-francesa", "104", "1456"],
       ["Barra Ø12,5 rosca M12", "correntes flexíveis", "-", "≈ 2.400 m"],
       ["Tubo Ø42,2×2,65", "correntes rígidas", "-", "≈ 230 m"],
       ["Barra Ø16 rosca M16", "diagonais das correntes", "-", "≈ 190 m"]]
y = pr.tabela(x0, y - 4, "PARAFUSOS E BARRAS", ["ITEM", "USO", "/VIGA", "OBRA"], par, [52, 70, 22, 36])
notas = ["Terças Ue 300×85×25×3,00 em aço ZAR 345 galvanizado, simplesmente apoiadas entre vigas, ligadas pela CT-1 (2 M12 por terça).",
         "Três linhas de correntes por vão (L/4, L/2, 3L/4): com duas linhas a faixa de borda (Cpe −1,4) e a terça escora não passam.",
         "Correntes rígidas no 1º espaço entre terças junto a cada ancoragem (beiral, eixo C e extremidade alta) e diagonais Ø16 até a CT-1.",
         "Mão-francesa em toda terça: do fundo da viga (CH-MF + OR-1) até a mesa inferior da terça, a 45°.",
         "Furos d + 2 mm feitos na fábrica; proibido furar a terça galvanizada na obra sem retoque com tinta rica em zinco.",
         "Cpe da faixa de borda adotado −1,4 (NBR 6123, conferir com a geometria final da cobertura).",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(x0, y - 4, notas, 180)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-COB01")
for a in avisos:
    print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
