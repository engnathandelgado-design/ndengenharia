"""ND-LET-MON01 — planta de montagem da cobertura (pilares, vigas TS-01, I110, VB-01), corte de montagem, lista de peças e
sequência. Cotas em cm (pré-moldado); níveis em m. A1."""
import json, math, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
LG = json.load(open(AQ + "ligacoes.json"))
f = lambda v, d=3: f"{v:.{d}f}".replace(".", ",")
Y_LIN = [0.0, 10.05, 19.705, 29.36, 38.865, 48.445, 58.025, 67.605, 76.81]
X_FACH = {"A": 0.0, "B": 9.87, "C": 20.05, "D": 29.63, "E": 40.10}
Y_P13 = Y_LIN[5] + 4.6
INCL, Z0 = 0.03, LG["Z0_TS"]
zf = lambda x: Z0 + INCL * x
C3 = math.cos(math.atan(INCL))
L_TS = LG["L_TS"] * C3
PONTAS = [(0.325, 0.325 + L_TS), (2 * 20.05 - (0.325 + L_TS), 2 * 20.05 - 0.325)]
M = lambda v: v * 1000                                   # m -> mm (modelo)
Z_AS = dict(P1=round(zf(0.475) + 0.45 * C3 - 0.01, 3), P2=round(zf(39.625) + 0.45 * C3 - 0.01, 3),
            C_esq=round(zf(PONTAS[0][1] - 0.15) + 0.45 * C3 - 0.01, 3), C_dir=round(zf(PONTAS[1][0] + 0.15) + 0.45 * C3 - 0.01, 3))
# pesos (kN/m³ = 25)
A_I90 = 0.40 * 0.15 * 2 + 0.15 * 0.60 + 2 * 0.5 * 0.125 * 0.08 * 2
A_I110 = 0.40 * 0.25 * 2 + 0.15 * 0.60 + 2 * 0.5 * 0.125 * 0.08 * 2
PESO = dict(TS01=round(A_I90 * 25 * LG["L_TS"] / 10, 1), I110=lambda L: round(A_I110 * 25 * L / 10, 1), VB=lambda L: round(0.15 * 0.70 * 25 * L / 10, 1),
            PL=round(0.24 * 11 * 25 / 10, 1), PC=round(0.25 * 9.88 * 25 / 10, 1))

pr = Prancha("A1", dict(cliente="MARQUE ENGENHARIA", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="PLANTA DE MONTAGEM DA COBERTURA — PILARES, VIGAS TS-01, I110 E VB-01 — CORTE, LISTA DE PEÇAS E SEQUÊNCIA",
                        desenho="ND-LET-MON01", folha="01/02", fase="PARA APROVAÇÃO"))
pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL")
Q = pr.quadro

# ------------------------------------------------------------------ PLANTA DE MONTAGEM 1:200 (x = comprimento 1–9, y = largura A–E)
v = pr.vista("PLANTA", (Q[0] + 45, Q[3] - 268), 200, titulo="PLANTA DE MONTAGEM — COBERTURA", subtitulo="marcas das peças; níveis dos assentos; sentido de montagem 1 → 9", unidade="cm")
Lx, Ly = M(Y_LIN[-1]), M(X_FACH["E"])
for k, yl in enumerate(Y_LIN):
    v.eixo((M(yl), -2500), (M(yl), Ly + 2500), 800)
    v.circulo((M(yl), Ly + 3800), 700, "VISTA"); v.texto((M(yl), Ly + 3800), str(k + 1), "nota", "MIDDLE_CENTER")
    v.circulo((M(yl), -3800), 700, "VISTA"); v.texto((M(yl), -3800), str(k + 1), "nota", "MIDDLE_CENTER")
for nome, xx in X_FACH.items():
    v.eixo((-2500, M(xx)), (Lx + 2500, M(xx)), 800)
    v.circulo((-3800, M(xx)), 700, "VISTA"); v.texto((-3800, M(xx)), nome, "nota", "MIDDLE_CENTER")
# pilares
def pilar(x, y, bx, by, marca, lado=1, dy=0):
    pts = [(x - bx / 2, y - by / 2), (x + bx / 2, y - by / 2), (x + bx / 2, y + by / 2), (x - bx / 2, y + by / 2)]
    v.poli(pts, "CORTADO", fechada=True); v.hachura(pts, "SOLID", 1, "CORTADO")
    v.texto((x + lado * (bx / 2 + 250), y + dy), marca, "min", "MIDDLE_LEFT" if lado > 0 else "MIDDLE_RIGHT")
PL = {1: ("PL-03", "PL-07"), 2: ("PL-02", "PL-06"), 9: ("PL-04", "PL-08")}
for i, yl in enumerate(Y_LIN, 1):
    a, b = PL.get(i, ("PL-01", "PL-05"))
    pilar(M(yl), 0, 400, 600, a, 1, -900)
    pilar(M(yl), Ly, 400, 600, b, 1, 900)
for j, (nome, x) in enumerate((("B", 9.87), ("C", 20.05), ("D", 29.63))):
    pilar(0, M(x), 600, 400, ["PF-01", "PF-02", "PF-03"][j], 1, 700)
    pilar(Lx, M(x), 600, 400, ["PF-01", "PF-04 (P14: recebe a V405)", "PF-03"][j], -1, 700)
for marca, y in (("PC-01", Y_LIN[1]), ("PC-01", Y_LIN[3]), ("PC-02", Y_P13)):
    pilar(M(y), M(20.05), 500, 500, marca, 1, 700)
for marca, x in (("PM-01", 9.87), ("PM-01", 29.63)):
    pilar(M(Y_LIN[1]), M(x), 400, 600, marca, 1, 700)
# I110 central (eixo C)
for marca, ya, yb in (("V407", Y_LIN[1], Y_LIN[3]), ("V406", Y_LIN[3], Y_P13), ("V405", Y_P13, Y_LIN[8])):
    v.ret(M(ya) + 275, M(20.05) - 200, M(yb - ya) - 550, 400, "VISTA")
    v.texto((M((ya + yb) / 2), M(20.05) + 500), f"{marca} (I110, L = {f(yb - ya - 0.55, 2)} m)", "min", "BOTTOM_CENTER")
# TS-01 (linhas 2 a 8, dois vãos)
for i in range(2, 9):
    y = M(Y_LIN[i - 1])
    for lado, (xa, xb) in zip("ab", PONTAS):
        v.ret(y - 200, M(xa), 400, M(xb - xa), "VISTA")
        xm = M((xa + xb) / 2)
        v.texto((y - 450, xm), f"TS-01 L{i}{lado}", "min", "MIDDLE_CENTER", rot=90)
        # seta do caimento (3 % subindo para E)
        v.poli([(y, xm - 1500), (y, xm + 1500), (y - 150, xm + 1200), (y, xm + 1500), (y + 150, xm + 1200)], "COTA")
        for xd in (M(xa) + 150, M(xb) - 150):                                       # pinos / dentes
            v.circulo((y, xd), 60, "VISTA")
# vigas de borda VB-01 (fachadas 1 e 9)
xs = list(X_FACH.values())
for y in (0.0, Y_LIN[-1]):
    for xa, xb in zip(xs[:-1], xs[1:]):
        v.ret(M(y) - 75, M(xa) + 250, 150, M(xb - xa) - 500, "VISTA")
        v.texto((M(y) + (-400 if y == 0 else 400), M((xa + xb) / 2)), "VB-01", "min", "MIDDLE_CENTER", rot=90)
# níveis dos assentos
v.texto((M(Y_LIN[4]), -1500), f"assento CP-TS eixo A: +{f(Z_AS['P1'])}", "min", "MIDDLE_CENTER")
v.texto((M(Y_LIN[4]), Ly + 1500), f"assento CP-TS eixo E: +{f(Z_AS['P2'])}", "min", "MIDDLE_CENTER")
v.texto((M(Y_LIN[4]) + 2500, M(20.05) - 800), f"assentos no eixo C: +{f(Z_AS['C_esq'])} (lado A) / +{f(Z_AS['C_dir'])} (lado E); topo da I110 +8,880", "min", "MIDDLE_CENTER")
v.cota_h([M(y) for y in Y_LIN], -4600, -8)
v.cota_v([M(x) for x in xs], Lx + 4600, 8)
# sentido de montagem
v.poli([(M(Y_LIN[3]), Ly + 6200), (M(Y_LIN[5]), Ly + 6200), (M(Y_LIN[5]) - 600, Ly + 6500), (M(Y_LIN[5]), Ly + 6200), (M(Y_LIN[5]) - 600, Ly + 5900)], "INDICACAO")
v.texto((M(Y_LIN[3]), Ly + 6700), "SENTIDO DE MONTAGEM: linha 1 → linha 9 (mezanino antes da cobertura nas linhas 1–2)", "nota")
v.marcador_corte((M(Y_LIN[2]), -5500), (M(Y_LIN[2]), Ly + 5500), "1", lado=1)

# ------------------------------------------------------------------ CORTE DE MONTAGEM 1:100 — pórtico eixo 3
c = pr.vista("CORTE 1-1", (Q[0] + 75, Q[3] - 432), 100, titulo="CORTE 1-1 — PÓRTICO DE MONTAGEM (LINHA 3)", subtitulo="níveis de montagem; pilares no cálice; TS-01 nos consolos", unidade="cm")
c.linha((-2000, 0), (Ly + 2000, 0), "TERRENO")
for x, bx, top, marca in ((0, 600, 10.0, "PL-01"), (M(20.05), 500, 8.88, "PC-01"), (Ly, 600, 10.0, "PL-05")):
    c.ret(x - bx / 2, -1000, bx, M(top) + 1000, "VISTA")
    c.ret(x - bx / 2 - 150, -1000, bx + 300, 1000, "OCULTA")
    c.texto((x, M(top) + 250), marca, "nota", "BOTTOM_CENTER")
# consolos e TS-01 (perfil inclinado)
for (xa, xb) in PONTAS:
    pts = [(M(xa), M(zf(xa))), (M(xb), M(zf(xb))), (M(xb), M(zf(xb) + 0.90)), (M(xa), M(zf(xa) + 0.90))]
    c.poli(pts, "VISTA", fechada=True)
c.ret(300, M(Z_AS["P1"] - 0.45), 300, 450, "VISTA"); c.ret(Ly - 600, M(Z_AS["P2"] - 0.45), 300, 450, "VISTA")
c.ret(M(20.05) - 650, M(Z_AS["C_esq"] - 0.45), 400, 450, "VISTA"); c.ret(M(20.05) + 250, M(Z_AS["C_dir"] - 0.45), 400, 450, "VISTA")
c.ret(M(20.05) - 200, M(8.88 - 1.10), 400, 1100, "OCULTA")                               # I110 (atrás do corte)
c.texto((M(20.05), M(8.88 - 1.10) - 150), "I110 V407 (atrás)", "min", "TOP_CENTER")
# terças e telha (cobertura escondida)
for s in LG["s_tercas"]:
    for xa, _ in PONTAS:
        x = xa + s * C3 - 0.027
        c.ret(M(x) - 42, M(zf(x) + 0.9125), 85, 300, "METALICA")
c.linha((300, M(zf(0.30) + 1.2275)), (Ly - 300, M(zf(Ly / 1000 - 0.30) + 1.2275)), "METALICA")
c.texto((M(10), M(zf(10) + 1.6)), "telha + terças Ue 300 (ver ND-LET-COB01)", "min", "BOTTOM_CENTER")
# níveis
def niv(x, z, txt, lado=1):
    c.poli([(x, z), (x + lado * 250, z + 250), (x + lado * 250, z - 250), (x, z)], "COTA")
    c.linha((x + lado * 250, z), (x + lado * 1200, z), "COTA")
    c.texto((x + lado * 300, z + 60), txt, "min", "BOTTOM_LEFT" if lado > 0 else "BOTTOM_RIGHT", "COTA")
niv(-300, 0, "±0,000 piso", -1); niv(-300, M(10.0), "+10,000 platibanda", -1)
niv(-300, M(Z_AS["P1"]), f"+{f(Z_AS['P1'])} assento", -1); niv(Ly + 300, M(Z_AS["P2"]), f"+{f(Z_AS['P2'])} assento", 1)
niv(Ly + 300, M(10.0), "+10,000", 1); niv(M(20.05) + 250, M(8.88), "+8,880 topo PC / I110", 1)
c.cota_h([0, M(20.05), Ly], -1000, -10)
c.cota_v([-1000, 0, M(Z_AS["P1"]), M(10.0)], -1800, -10, total=False)
c.chamada((M(PONTAS[0][0]) + 150, M(zf(PONTAS[0][0]) + 0.45)), (12, 18), "dente 45×30 + pino PN-1 grauteado (só nesta ponta)")
c.chamada((M(PONTAS[1][1]) - 150, M(zf(PONTAS[1][1]) + 0.45)), (-12, 18), "pino com graute flexível (ponta livre)")
c.chamada((Ly / 4, M(zf(Ly / 4000) + 0.9)), (8, -24), "TS-01: 11,6 t, içar pelas 4 alças AL-1")

# ------------------------------------------------------------------ coluna direita: lista de peças, sequência, notas
XC = Q[2] - 200
y = Q[3] - 6
pecas = [["PL-01 / 05", "Pilar 40×60 lateral, L 1100", "12", f(PESO["PL"], 1), "cálice −1,00; topo +10,00"],
         ["PL-02 / 06", "Pilar 40×60 lateral c/ CP-MEZ (linha 2)", "2", f(PESO["PL"], 1), "cálice −1,00; topo +10,00"],
         ["PL-03 / 04 / 07 / 08", "Pilar 40×60 de canto", "4", f(PESO["PL"], 1), "cálice −1,00; topo +10,00"],
         ["PF-01 a 03", "Pilar 40×60 de fachada (1 e 9)", "6", f(PESO["PL"], 1), "cálice −1,00; topo +10,00"],
         ["PC-01 / 02", "Pilar central 50×50, L 988", "3", f(PESO["PC"], 1), "cálice −1,00; topo +8,88"],
         ["PM-01", "Pilar do mezanino 40×60 (B2, D2)", "2", "—", "ver ND-LET-MON02"],
         ["TS-01", f"Viga I90 de cobertura, L {LG['L_TS']*100:.0f}, dentes 45×30", "14", f(PESO["TS01"], 1), f"+{f(Z_AS['P1'])} / +{f(Z_AS['C_esq'])} / +{f(Z_AS['P2'])}"],
         ["V407", f"Viga I110 central, L {f(Y_LIN[3]-Y_LIN[1]-0.55, 2)} m", "1", f(PESO["I110"](Y_LIN[3] - Y_LIN[1] - 0.55), 1), "consolos PC-01 (+7,78)"],
         ["V406", f"Viga I110 central, L {f(Y_P13-Y_LIN[3]-0.55, 2)} m", "1", f(PESO["I110"](Y_P13 - Y_LIN[3] - 0.55), 1), "consolos PC-01/02 (+7,78)"],
         ["V405", f"Viga I110 central, L {f(Y_LIN[8]-Y_P13-0.55, 2)} m", "1", f(PESO["I110"](Y_LIN[8] - Y_P13 - 0.55), 1), "consolos PC-02 / PF-04 (P14, linha 9)"],
         ["VB-01", "Viga de borda 15×70, L ≈ 9,4–9,7 m", "8", f(PESO["VB"](9.6), 1), "consolos CP-VB (+7,46 a +8,65)"]]
y = pr.tabela(XC, y, "LISTA DE PEÇAS DE MONTAGEM — COBERTURA", ["MARCA", "DESCRIÇÃO", "QT", "PESO (t)", "APOIO / NÍVEL"], pecas, [26, 72, 14, 18, 70], h_lin=6.0)
seq = ["Locar os cálices (±10 mm), nivelar o fundo com calços; conferir prumo das paredes do cálice.",
       "Pilares linha a linha, 1 → 9: içar na horizontal pelas 2 AL-2, levantar à vertical, descer no cálice, aprumar (10 mm/10 m) com cunhas, grautear (fck ≥ 30 MPa) e só soltar após 24 h.",
       "Mezanino (linhas 1–2): vigas VM e lajes do +3,15, depois do +6,55 — ver ND-LET-MON02.",
       "Vigas centrais I110 V407, V406 e V405 nos consolos dos PC: neoprene 300×250×30 fretado; pino grauteado numa ponta só.",
       "TS-01 L2 a L8, dois vãos por linha: neoprene NEO-1, pino PN-1 pela ponta do eixo A (graute) e ponta do eixo C/E com graute flexível.",
       "VB-01 das fachadas nos consolos CP-VB; travar as TS-01 com as terças e correntes da linha montada antes de soltar a próxima (ND-LET-COB01).",
       "Terças, correntes, mãos-francesas e contraventamento; telhas; placas de fechamento (CM-01) por último."]
y = pr.notas(XC, y - 4, seq, 200, titulo="SEQUÊNCIA DE MONTAGEM")
notas = ["Tolerâncias de montagem (NBR 9062:2017): pilar em planta ±10 mm; prumo 10 mm em 10 m; consolo ±10 mm; folga de ponta 25 mm e de dente 25 mm já previstas.",
         "TS-01 só pode ser solta do guindaste com os dois pinos encaixados e a linha anterior travada; viga de 19,46 m: içar pelas 4 alças com balancim (ângulo ≥ 60°).",
         "Pino PN-1 Ø20 no consolo; tubo TB-1 Ø40 na viga; grautear o tubo de uma ponta só por viga (a outra recebe graute flexível) para não travar o encurtamento.",
         "Cobertura escondida: telha 104 mm abaixo da platibanda +10,00 no eixo E; nenhuma peça pode ficar acima de +9,90.",
         "V405 vai do P13 até a linha 9 e apoia no consolo CP-I110 do pilar P14 (PF-04), como na planta de vigas de cobertura do R01.",
         "Níveis em m, cotas em cm. Não medir no desenho. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(XC, y - 4, notas, 200)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-MON01")
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
for a in avisos:
    if a[0] == "ERRO" or "sobrep" in a[1]:
        print(a)
