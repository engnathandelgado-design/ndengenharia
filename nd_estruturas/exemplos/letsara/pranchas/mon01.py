"""ND-LET-MON01 — planta de montagem da cobertura (pilares, vigas TS-01, I130, VB-01), corte de montagem, lista de peças e
sequência. Cotas em cm (pré-moldado); níveis em m. A1."""
import json, math, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
LG = json.load(open(AQ + "ligacoes.json"))
f = lambda v, d=3: f"{v:.{d}f}".replace(".", ",")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from geometria import Y_LIN, X_EIXO as X_FACH, Y_P13
INCL, Z0 = 0.03, LG["Z0_TS"]
zf = lambda x: Z0 + INCL * x
C3 = math.cos(math.atan(INCL))
L_TS = LG["L_TS"] * C3
X0P = LG["X_PONTA_ESQ"]
PONTAS = [(X0P, X0P + L_TS), (X_FACH["E"] - X0P - L_TS, X_FACH["E"] - X0P)]
M = lambda v: v * 1000                                   # m -> mm (modelo)
Z_AS = dict(P1=LG["REC"][0], P2=LG["REC"][1], C_esq=LG["Z_TOPO_I130"], C_dir=LG["Z_TOPO_I130"])   # rev03: recuo (assento) e topo da I130
Z_TC, H_I = LG["Z_TOPO_I130"], LG["H_I130"]
# pesos (kN/m³ = 25)
A_I90 = 0.40 * 0.15 * 2 + 0.15 * 0.60 + 2 * 0.5 * 0.125 * 0.08 * 2
A_I130 = 0.40 * 0.22 + 0.40 * 0.25 + 0.15 * (1.30 - 0.47) + 2 * 0.5 * 0.125 * 0.08 * 2
PESO = dict(TS01=round(A_I90 * 25 * LG["L_TS"] / 10, 1), I130=lambda L: round(A_I130 * 25 * L / 10, 1), VB=lambda L: round((0.15 * 0.60 * L - 2 * 0.15 * 0.30 * 0.27) * 25 / 10, 1),
            PL=round(0.24 * 11 * 25 / 10, 1), PC=round(0.25 * 9.88 * 25 / 10, 1))

pr = Prancha("A1", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="PLANTA DE MONTAGEM DA COBERTURA — PILARES, VIGAS TS-01, I130, VB-01 A VB-08 — CORTE, LISTA DE PEÇAS E SEQUÊNCIA",
                        desenho="ND-LET-MON01", folha="01/02", fase="PARA APROVAÇÃO", rev="03"))
pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL")
pr.revisao("01", "12/10/2026", "geometria do R01 (79,35 × 39,50 m); corte 1-1 com I130 em corte e recuo dos pilares")
pr.revisao("02", "12/10/2026", "MARCAS DOS PILARES POR LINHA; VB-01 A VB-04 15×90; PILARES DOS PORTÕES; CONSOLOS SEM CHANFRO")
pr.revisao("03", "14/10/2026", "TS-01 SEM DENTES (RECUO E TOPO DA I130); I130; COBERTURA REBAIXADA")
pr.revisao("04", "16/10/2026", "NBR 9062: SEM VT; NEOPRENES E CONSOLOS REVISTOS; MEZANINO MEIO VASO; VB 15×60 COM DENTE")
pr.revisao("05", "17/10/2026", "TERÇAS Z 302 CONTÍNUAS POR TRANSPASSE, SEM MÃO-FRANCESA")
pr.revisao("06", "20/10/2026", "REVISÃO DE OBRA: MARCAS PG-03/PG-04, NEO-2, VB-01 A 08 ESCORADAS, PLACAS INTERNAS ANTES DAS TS-01, CUNHAS E GRAUTE, RIGGING E TRANSPORTE")
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
PL = {1: ("PL-03", "PL-07"), 2: ("PL-02", "PL-06"), 3: ("PL-09", "PL-11"), 4: ("PL-10", "PL-12"), 9: ("PL-04", "PL-08")}
for i, yl in enumerate(Y_LIN, 1):
    a, b = PL.get(i, ("PL-01", "PL-05"))
    pilar(M(yl), 0, 400, 600, a, 1, -900)
    pilar(M(yl), Ly, 400, 600, b, 1, 900)
for j, (nome, x) in enumerate((("B", X_FACH["B"]), ("C", X_FACH["C"]), ("D", X_FACH["D"]))):
    pilar(0, M(x), 600, 400, ["PF-01", "PF-02", "PF-03"][j], 1, 700)
    pilar(Lx, M(x), 600, 400, ["PF-05", "PF-04 (P14)", "PF-06"][j], -1, 700)
for marca, y, bx, by in (("PC-01 (P8A)", Y_LIN[1], 600, 400), ("PC-02 (P11)", Y_LIN[3], 400, 400), ("PC-03 (P13)", Y_P13, 600, 600)):
    pilar(M(y), M(X_FACH["C"]), bx, by, marca, 1, 700)
for marca, x in (("PM-01", X_FACH["B"]), ("PM-01", X_FACH["D"])):
    pilar(M(Y_LIN[1]), M(x), 600, 400, marca, 1, 700)
for marca, x, b_ in (("PG-01 (P9)", 9.87, 400), ("PG-02 (P10)", 15.195, 250), ("PG-04 (P10)", 24.305, 250), ("PG-03 (P12)", 29.63, 400)):
    pilar(M(Y_LIN[3]), M(x), b_, b_, marca, 1, -700)
# I130 central (eixo C)
for marca, ya, yb in (("V407", Y_LIN[1], Y_LIN[3]), ("V406", Y_LIN[3], Y_P13), ("V405", Y_P13, Y_LIN[8])):
    v.ret(M(ya) + 275, M(X_FACH["C"]) - 200, M(yb - ya) - 550, 400, "VISTA")
    v.texto((M((ya + yb) / 2), M(X_FACH["C"]) + 500), f"{marca} (I130, L = {f(yb - ya - 0.55, 2)} m)", "min", "BOTTOM_CENTER")
# TS-01 (linhas 2 a 8, dois vãos)
for i in range(2, 9):
    y = M(Y_LIN[i - 1])
    for lado, (xa, xb) in zip("ab", PONTAS):
        v.ret(y - 200, M(xa), 400, M(xb - xa), "VISTA")
        xm = M((xa + xb) / 2)
        v.texto((y - 450, xm), f"TS-01 L{i}{lado}", "min", "MIDDLE_CENTER", rot=90)
        # seta do caimento (3 % subindo para E)
        v.poli([(y, xm - 1500), (y, xm + 1500), (y - 150, xm + 1200), (y, xm + 1500), (y + 150, xm + 1200)], "COTA")
        for xd in (M(xa) + 140, M(xb) - 77.5):                                     # pinos (2 por ponta)
            for dy in (-100, 100):
                v.circulo((y + dy, xd), 40, "VISTA")
# vigas de borda VB-01 a VB-04 (fachadas 1 e 9)
xs = list(X_FACH.values())
for y in (0.0, Y_LIN[-1]):
    for k, (xa, xb) in enumerate(zip(xs[:-1], xs[1:]), 1):
        v.ret(M(y) - 75, M(xa) + 250, 150, M(xb - xa) - 500, "VISTA")
        v.texto((M(y) + (-400 if y == 0 else 400), M((xa + xb) / 2)), f"VB-0{k}", "min", "MIDDLE_CENTER", rot=90)
# níveis dos assentos
v.texto((M((Y_LIN[4] + Y_LIN[5]) / 2), -1500), f"assento no recuo, eixo A: +{f(Z_AS['P1'])}", "min", "MIDDLE_CENTER")
v.texto((M((Y_LIN[4] + Y_LIN[5]) / 2), Ly + 1500), f"assento no recuo, eixo E: +{f(Z_AS['P2'])}", "min", "MIDDLE_CENTER")
v.texto((M(Y_LIN[4]) + 2500, M(X_FACH["C"]) - 800), f"eixo C: TS-01 no topo da I130 / P8A / P11, +{f(Z_TC)}", "min", "MIDDLE_CENTER")
v.cota_h([M(y) for y in Y_LIN], -4600, -8)
v.cota_v([M(x) for x in xs], Lx + 4600, 8)
# sentido de montagem
v.poli([(M(Y_LIN[3]), Ly + 6200), (M(Y_LIN[5]), Ly + 6200), (M(Y_LIN[5]) - 600, Ly + 6500), (M(Y_LIN[5]), Ly + 6200), (M(Y_LIN[5]) - 600, Ly + 5900)], "INDICACAO")
v.texto((M(Y_LIN[3]), Ly + 6700), "SENTIDO DE MONTAGEM: linha 1 → linha 9 (mezanino antes da cobertura nas linhas 1–2)", "nota")
v.marcador_corte((M(Y_LIN[2]), -5500), (M(Y_LIN[2]), Ly + 5500), "1", lado=1)

# ------------------------------------------------------------------ CORTE DE MONTAGEM 1:100 — pórtico eixo 3
c = pr.vista("CORTE 1-1", (Q[0] + 75, Q[3] - 445), 100, titulo="CORTE 1-1 — PÓRTICO DE MONTAGEM (LINHA 3)", subtitulo="níveis de montagem; pilares no cálice; TS-01 no recuo dos pilares e no topo da I130", unidade="cm")
c.linha((-2000, 0), (Ly + 2000, 0), "TERRENO")
REC = tuple(LG["REC"])                                    # recuo = assento da TS-01 (rev03)
for x, bx, top, marca in ((0, 600, 10.0, "PL-09"), (Ly, 600, 10.0, "PL-11")):
    lado = 1 if x == 0 else -1
    zr = M(REC[0] if x == 0 else REC[1])
    c.poli([(x - lado * 300, -1000), (x + lado * 300, -1000), (x + lado * 300, zr), (x, zr), (x, M(top)), (x - lado * 300, M(top))], "VISTA", True)
    c.texto((x, M(top) + 250), marca, "nota", "BOTTOM_CENTER")
for x, bx, top, marca in ((M(X_FACH["C"]), 400, Z_TC, "I130 (linha 3: entre P8A e P11)"),):
    c.ret(x - bx / 2, M(top - H_I), bx, M(H_I), "CORTADO")
# consolos e TS-01 (perfil inclinado)
for (xa, xb) in PONTAS:
    pts = [(M(xa), M(zf(xa))), (M(xb), M(zf(xb))), (M(xb), M(zf(xb) + 0.90)), (M(xa), M(zf(xa) + 0.90))]
    c.poli(pts, "VISTA", fechada=True)
c.texto((M(X_FACH["C"]), M(Z_TC - H_I) - 150), "I130 V407 (corte): TS-01 no topo", "min", "TOP_CENTER")
# terças e telha (cobertura escondida)
for s in LG["s_tercas"]:
    for xa, _ in PONTAS:
        x = xa + s * C3 - 0.027
        c.ret(M(x) - 42, M(zf(x) + 0.91), 85, 300, "METALICA")
c.linha((300, M(zf(0.30) + 1.21)), (Ly - 300, M(zf(Ly / 1000 - 0.30) + 1.21)), "METALICA")
c.linha((300, M(zf(0.30) + 1.47)), (Ly - 300, M(zf(Ly / 1000 - 0.30) + 1.47)), "METALICA")
c.texto((M(10), M(zf(10) + 1.8)), "TP40 + lã 40 + zipada + painéis solares sobre terças Z 302 contínuas nos ST-1P (ND-LET-COB01)", "min", "BOTTOM_CENTER")
# níveis
def niv(x, z, txt, lado=1):
    c.poli([(x, z), (x + lado * 250, z + 250), (x + lado * 250, z - 250), (x, z)], "COTA")
    c.linha((x + lado * 250, z), (x + lado * 1200, z), "COTA")
    c.texto((x + lado * 300, z + 60), txt, "min", "BOTTOM_LEFT" if lado > 0 else "BOTTOM_RIGHT", "COTA")
niv(-300, 0, "±0,000 piso", -1); niv(-300, M(10.0), "+10,000 platibanda", -1)
niv(-300, M(Z_AS["P1"]), f"+{f(Z_AS['P1'])} assento", -1); niv(Ly + 300, M(Z_AS["P2"]), f"+{f(Z_AS['P2'])} assento", 1)
niv(Ly + 300, M(10.0), "+10,000", 1); niv(M(X_FACH["C"]) + 250, M(Z_TC) - 400, f"+{f(Z_TC)} topo I130", 1)
c.cota_h([0, M(X_FACH["C"]), Ly], -1000, -10)
c.cota_v([-1000, 0, M(Z_AS["P1"]), M(10.0)], -1800, -10, total=False)
c.chamada((M(PONTAS[0][0]) + 140, M(zf(PONTAS[0][0]) + 0.45)), (12, 18), "apoio no recuo: NEO-4 + 2 PN-3 Ø25 grauteados")
c.chamada((M(PONTAS[1][1]) - 140, M(zf(PONTAS[1][1]) + 0.45)), (-12, 18), "apoio no recuo do P2")
c.chamada((Ly / 4, M(zf(Ly / 4000) + 0.9)), (8, -24), "TS-01: 12,0 t, içar pelas 4 alças AL-1")

# ------------------------------------------------------------------ coluna direita: lista de peças, sequência, notas
XC = Q[2] - 200
y = Q[3] - 6
from viga_vb import MARCAS as VBM
import json as _j
I130 = _j.load(open(AQ + "i110_r01.json"))
def peso_pil(b, h, zr, cab):                                    # corpo b×h do cálice (−1,00) ao recuo + cabeça até +10,00
    return round((b * h * (1.0 + zr) + cab * (10.0 - zr)) * 25 / 10, 1)
R1, R2 = REC
pecas = [["PL-01 / 05", "Pilar 40×60 lateral (L5–L8), L 1100", "8", f"{f(peso_pil(.4, .6, R1, .12), 1)} / {f(peso_pil(.4, .6, R2, .12), 1)}", "cálice −1,00; topo +10,00"],
         ["PL-09..12", "Pilar 40×60 lateral (L3, L4), L 1100", "4", f"{f(peso_pil(.4, .6, R1, .12), 1)} / {f(peso_pil(.4, .6, R2, .12), 1)}", "cálice −1,00; topo +10,00"],
         ["PL-02 / 06", "Pilar 40×60 lateral c/ CP-MEZ (L2)", "2", f"{f(peso_pil(.4, .6, R1, .12), 1)} / {f(peso_pil(.4, .6, R2, .12), 1)}", "cálice −1,00; topo +10,00"],
         ["PL-03/04/07/08", "Pilar 40×60 de canto, cabeça 30×30", "4", f(peso_pil(.4, .6, 8.70, .09), 1), "cálice −1,00; topo +10,00"],
         ["PF-01..06", "Pilar 40×60 de fachada (1 e 9)", "6", f(peso_pil(.4, .6, 9.25, .12), 1), "cálice −1,00; topo +10,00"],
         ["PC-01..03", f"P8A 40×60, P11 40×40, P13 60×60, L {(Z_TC + 1) * 100:.0f}", "3", f"{f(.24*(Z_TC+1)*2.5, 1)} / {f(.16*(Z_TC+1)*2.5, 1)} / {f(.36*(Z_TC+1)*2.5, 1)}", f"cálice −1,00; topo +{f(Z_TC)}"],
         ["PM-01", "Pilar do mezanino 40×60 (B2, D2)", "2", f(.24 * 7.55 * 2.5, 1), "ver ND-LET-MON02"],
         ["PG-01 / PG-03", "Pilares dos portões 40×40 (P9 / P12, linha 4)", "1 + 1", f"{f(.16*8.47*2.5, 1)} / {f(.16*9.06*2.5, 1)}", "cálice −1,00; topo +7,47 / +8,06"],
         ["PG-02 / PG-04", "Pilares dos portões 25×25 (P10, x 15,20 / 24,31)", "1 + 1", f"{f(.0625*8.63*2.5, 1)} / {f(.0625*8.90*2.5, 1)}", "cálice −1,00; topo +7,63 / +7,90"],
         ["TS-01", f"Viga I90 de cobertura, L {LG['L_TS']*100:.0f}, sem dentes", "14", "12,0", f"recuo +{f(Z_AS['P1'])} / topo I130 +{f(Z_TC)} / recuo +{f(Z_AS['P2'])}"]]
for mk in ("V407", "V406", "V405"):
    Lm = {"V407": 19.5, "V406": 24.125, "V405": 24.025}[mk]
    pecas.append([mk, f"Viga I130 central, L {f(Lm, 2)} m", "1", f(PESO["I130"](Lm), 1), f"consolos CP-I130 (+{f(LG['Z_ASS_I130'])})"])
for mk, pos, qt, Lmm, _x in VBM:
    pecas.append([mk, f"Viga de borda 15×60 c/ dente, L {Lmm/10:.0f} cm ({pos.split(',')[0]})", str(qt), f(PESO["VB"](Lmm / 1000), 1), "consolos CP-VB"])
y = pr.tabela(XC, y, "LISTA DE PEÇAS DE MONTAGEM — COBERTURA", ["MARCA", "DESCRIÇÃO", "QT", "PESO (t)", "APOIO / NÍVEL"], pecas, [26, 72, 14, 18, 70], h_lin=6.0)
seq = ["Locar os cálices (±10 mm), nivelar o fundo com calços; conferir prumo das paredes do cálice.",
       "Pilares linha a linha, 1 → 9: içar na horizontal pelas 2 AL-2 (face C), levantar à vertical, descer no cálice com a face C para fora, aprumar (10 mm/10 m) e travar com cunhas de madeira dura nas 4 faces antes de soltar o guindaste; grautear o cálice no mesmo dia (fck ≥ 30 MPa) e só apoiar vigas depois de 24 h (graute ≥ 15 MPa). Pilar sem graute não fica de um dia para o outro.",
       "Mezanino (linhas 1–2): vigas VM e lajes do +3,15, depois do +6,55 — ver ND-LET-MON02.",
       "Vigas centrais I130 V407, V406 e V405 nos consolos CP-I130 dos PC: neoprene NEO-2 300×200×31 fretado; pino PN-2 grauteado numa ponta só. São as peças mais pesadas (até 20,1 t, 24,1 m): içar pelas 2 alças AL-3 (3 laços cada).",
       "TS-01 L2 a L8, dois vãos por linha: neoprene NEO-4 no recuo dos pilares laterais (2 PN-3 Ø25) e NEO-3 no topo da I130 / P8A / P11 (2 PN-5 Ø20); grautear os tubos TB-3 (na linha 2, sobre o P8A, mastique: ponta livre em x).",
       "VB-01 a VB-08 das fachadas 1 e 9 (dente sobre os consolos CP-VB; ponta marcada LADO A no lado do eixo A; apertar a porca do PN-6 após assentar). A VB tem 15 cm de largura e 9,4 m: escorar contra tombamento até as terças do vão de oitão estarem parafusadas. Travar as TS-01 com as terças e correntes da linha montada antes de soltar a próxima (ND-LET-COB01).",
       "Terças, correntes e contraventamento em X (tudo parafusado, sem mão-francesa); TP40, lã, zipada e painéis solares.",
       "Placas de fechamento (ND-LET-CM01, ordem I, H, J, G, E, F, C, B, D, A): as das paredes internas G (linha 2) e C (linha 4), que ficam embaixo das TS-01, e as do anexo são montadas ANTES das TS-01 dessas linhas (o guindaste não desce placa de 10 m por baixo da cobertura); as das fachadas e laterais externas podem ir depois, pelo lado de fora."]
y = pr.notas(XC, y - 4, seq, 200, titulo="SEQUÊNCIA DE MONTAGEM")
notas = ["Tolerâncias de montagem (NBR 9062:2017): pilar em planta ±10 mm; prumo 10 mm em 10 m; consolo ±10 mm; folga de ponta 25 mm e de dente 25 mm já previstas.",
         f"TS-01 só pode ser solta do guindaste com os pinos encaixados nos tubos TB-3 e a linha anterior travada; viga de {f(LG['L_TS'], 2)} m: içar pelas 4 alças com balancins.",
         "Plano de rigging (NBR 9062:2017 3.17 e 11) a cargo da montadora, com os pesos desta lista: posição do guindaste, raio, patolas e capacidade do solo. Transporte: I130 com 24,1 m e TS-01 com 19,7 m exigem carreta extensível e autorização especial de trânsito; transportar apoiadas nos pontos das alças.",
         f"Cobertura escondida: topo dos painéis solares {LG['platibanda']['folga_P2_mm']} mm abaixo da platibanda +10,00 no eixo E (mínimo pedido 150 mm).",
         "V405 vai do P13 até a linha 9 e apoia no consolo CP-I130 do pilar P14 (PF-04), como na planta de vigas de cobertura do R01.",
         "Níveis em m, cotas em cm. Não medir no desenho. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(XC, y - 4, notas, 200)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-MON01")
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
for a in avisos:
    if a[0] == "ERRO" or "sobrep" in a[1]:
        print(a)
