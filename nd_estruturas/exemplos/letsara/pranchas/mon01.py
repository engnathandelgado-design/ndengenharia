"""ND-LET-MON01 — planta de montagem da cobertura (pilares, vigas TS-01, I130, VB-01), corte de montagem, lista de peças e
sequência. Cotas em cm (pré-moldado); níveis em m. A1."""
import json, math, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha
import pecas_obra as QT                                     # peças = mesma fonte das listas (quantitativos.py)
PQ = {p_[1]: p_ for p_ in QT.pecas}

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
LG = json.load(open(AQ + "ligacoes.json"))
fp = lambda t_: f"{t_:.1f}".replace(".", ",")
f = lambda v, d=3: f"{v:.{d}f}".replace(".", ",")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from geometria import Y_LIN, X_EIXO as X_FACH, Y_P13, Y_PC_C
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
A_I130 = 0.40 * 0.22 + 0.40 * 0.25 + 0.15 * (H_I - 0.47) + 2 * 0.5 * 0.125 * 0.08 * 2
PESO = dict(TS01=round(A_I90 * 25 * LG["L_TS"] / 10, 1), I130=lambda L: round(A_I130 * 25 * L / 10, 1), VB=lambda L: round((0.15 * 0.60 * L - 2 * 0.15 * 0.30 * 0.27) * 25 / 10, 1),
            PL=round(0.24 * 11 * 25 / 10, 1), PC=round(0.25 * 9.88 * 25 / 10, 1))

pr = Prancha("A1", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="PLANTA DE MONTAGEM DA COBERTURA — PILARES, VIGAS TS-01, I130, VB-01 A VB-08 — CORTE, LISTA DE PEÇAS E SEQUÊNCIA",
                        desenho="ND-LET-MON01", folha="01/03", fase="PARA APROVAÇÃO", rev="03"))
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
    import renomear as RN
    nm = RN.pilar_em(y / 1000, x / 1000)                                  # rev08: nome da peça na posição (planta: x = linha, y = eixo)
    v.texto((x + lado * (bx / 2 + 250), y + dy), RN.rotulo(nm) if nm else marca, "min", "MIDDLE_LEFT" if lado > 0 else "MIDDLE_RIGHT")
PL = {1: ("PL-03", "PL-07"), 2: ("PL-02", "PL-06"), 3: ("PL-09", "PL-11"), 4: ("PL-10", "PL-12"), 9: ("PL-04", "PL-08")}
for i, yl in enumerate(Y_LIN, 1):
    a, b = PL.get(i, ("PL-01", "PL-05"))
    pilar(M(yl), 0, 400, 600, a, 1, -900)
    pilar(M(yl), Ly, 400, 600, b, 1, 900)
for j, (nome, x) in enumerate((("B", X_FACH["B"]), ("C", X_FACH["C"]), ("D", X_FACH["D"]))):
    pilar(0, M(x), 600, 400, ["PF-01", "PF-02", "PF-03"][j], 1, 700)
    pilar(Lx, M(x), 600, 400, ["PF-05", "PF-04 (P14)", "PF-06"][j], -1, 700)
for marca, y, bx, by in (("PC-01 (P8A)", Y_LIN[1], 600, 400), ("PC-02 (P11)", Y_LIN[3], 400, 400), ("PC-03 (P13)", Y_PC_C[0], 400, 400), ("PC-03 (P13B)", Y_PC_C[1], 400, 400)):
    pilar(M(y), M(X_FACH["C"]), bx, by, marca, -1 if y == Y_PC_C[0] else 1, 700)
for marca, x in (("PM-01", X_FACH["B"]), ("PM-02", X_FACH["D"])):
    pilar(M(Y_LIN[1]), M(x), 600, 400, marca, 1, 700)
for marca, x, b_ in (("PG-01 (P9)", 9.87, 400), ("PG-02 (P10)", 15.195, 250), ("PG-04 (P10)", 24.305, 250), ("PG-03 (P12)", 29.63, 400)):
    pilar(M(Y_LIN[3]), M(x), b_, b_, marca, 1, -700)
# I130 central (eixo C)
for marca, ya, yb in (("V407", Y_LIN[1], Y_LIN[3]), ("V406", Y_LIN[3], Y_PC_C[0]), ("V405", Y_PC_C[0], Y_PC_C[1]), ("V404", Y_PC_C[1], Y_LIN[8])):   # DEC-058
    Lm_ = PQ[marca][4]                                                   # comprimento da peça (folha ND-LET-I130)
    v.ret(M((ya + yb) / 2 - Lm_ / 2), M(X_FACH["C"]) - 200, M(Lm_), 400, "VISTA")
    x_t = M(Y_LIN[5]) + 600 if marca == "V405" else (M(Y_LIN[7]) + 400 if marca == "V404" else (M(Y_LIN[2]) + 500 if marca == "V407" else M(ya) + 1500))   # rótulo fora dos eixos e dos rótulos dos PC
    import renomear as RN
    nm_ = RN.viga_em("cobertura", X_FACH["C"], (ya + yb) / 2)             # rev11: nome + seção (pedido do Nathan, 26/10)
    v.texto((x_t, M(X_FACH["C"]) - 500), RN.novo(RN.rotulo(nm_)[1:] + f" — L {f(Lm_, 2)}") if nm_ else f"{marca} (I130, L = {f(Lm_, 2)} m)", "min", "TOP_LEFT")
# TS-01 (linhas 2 a 8, dois vãos)
for i in range(2, 9):
    y = M(Y_LIN[i - 1])
    for lado, (xa, xb) in zip("ab", PONTAS):
        v.ret(y - 200, M(xa), 400, M(xb - xa), "VISTA")
        xm = M((xa + xb) / 2)
        import renomear as RN
        nm = RN.viga_em("cobertura", (xa + xb) / 2, Y_LIN[i - 1])
        v.texto((y - 750, xm + 2600), RN.rotulo(nm) if nm else RN.novo(f"TS-01 L{i}{lado}"), "min", "MIDDLE_CENTER", rot=90)     # fora do eixo B / D
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
        import renomear as RN
        nm = RN.viga_em("cobertura", (xa + xb) / 2, y)
        v.texto((M(y) + (-750 if y == 0 else 750), M((xa + xb) / 2)), RN.rotulo(nm) if nm else RN.novo(f"VB-0{k}"), "min", "MIDDLE_CENTER", rot=90)
# níveis dos assentos
v.texto((M((Y_LIN[4] + Y_LIN[5]) / 2), -1500), f"assento A +{f(Z_AS['P1'])}", "min", "MIDDLE_CENTER")
v.texto((M((Y_LIN[4] + Y_LIN[5]) / 2), Ly + 1500), f"assento E +{f(Z_AS['P2'])}", "min", "MIDDLE_CENTER")
v.texto((M(Y_LIN[4]) + 5000, M(X_FACH["C"]) - 900), RN.novo(f"topo I130 +{f(Z_TC)}"), "min", "MIDDLE_CENTER")
v.cota_h([M(y) for y in Y_LIN], -4600, -8)
v.cota_v([M(x) for x in xs], Lx + 4600, 8)
# sentido de montagem
v.poli([(M(Y_LIN[5]), Ly + 6200), (M(Y_LIN[3]), Ly + 6200), (M(Y_LIN[3]) + 600, Ly + 6500), (M(Y_LIN[3]), Ly + 6200), (M(Y_LIN[3]) + 600, Ly + 5900)], "INDICACAO")
v.texto((M(Y_LIN[3]), Ly + 6700), "SENTIDO DA COBERTURA: linha 9 → linha 3; linhas 1–2 (TS-01 L2, VB-01 a 04) depois do mezanino", "nota")
v.marcador_corte((M(Y_LIN[2]) - 1200, -7600), (M(Y_LIN[2]) - 1200, Ly + 7600), "1", lado=1)

# ------------------------------------------------------------------ CORTE DE MONTAGEM 1:100 — pórtico da linha 3
# rev11 (26/10/2026): gerado da MESMA geometria do modelo 3D e da ND-LET-CT01 (portico.py): TS-01 I90 em elevação com o caimento,
# terças Z 302 × 90/82 × 19 × 2,30 em seção real sobre o ST-1P, pacote da cobertura em escala, I130 (h 120) em corte com os
# consolos CT-I130 com mísula e o NEO-3C, pilares no cálice com o embutimento cotado.
import portico as PT
import pe_pilar as PP
c = pr.vista("CORTE 1-1", (Q[0] + 75, Q[3] - 458), 100, titulo="CORTE 1-1 — PÓRTICO DE MONTAGEM (LINHA 3)",
             subtitulo="gerado do modelo 3D (mesma geometria da ND-LET-CT01); pilares no cálice; TS-01 no recuo dos pilares e no topo da I130", unidade="cm")
c.linha((-2000, 0), (Ly + 2000, 0), "TERRENO")
PT.estrutura(PT.Recorte(c), 3)
for x, lado in ((0, 1), (Ly, -1)):
    nm_ = PP.pe(c, x / 1000, Y_LIN[2], x, "x", cotar=(x == 0), lado=-1)
    c.texto((x + lado * 450, 250), PP.rotulo(nm_), "nota", "BOTTOM_LEFT" if lado > 0 else "BOTTOM_RIGHT")
nmI = RN.viga_em("cobertura", X_FACH["C"], (Y_LIN[1] + Y_LIN[3]) / 2)
c.chamada((M(X_FACH["C"]), PT.Z_TOP_C - PT.H_I130 / 2), (14, -22), RN.novo(f"{nmI} I130 h{PT.H_I130 / 10:.0f} em corte (b 40, bw 15) — TS-01 no topo, consolos CT-I130 com mísula + NEO-3C"))
c.cota_v([PT.Z_TOP_C - PT.H_I130, PT.Z_TOP_C], M(X_FACH["C"]) + 900, 4, total=False)
def niv(x, z, txt, lado=1):
    c.poli([(x, z), (x + lado * 250, z + 250), (x + lado * 250, z - 250), (x, z)], "COTA")
    c.linha((x + lado * 250, z), (x + lado * 1200, z), "COTA")
    c.texto((x + lado * 300, z + 60), txt, "min", "BOTTOM_LEFT" if lado > 0 else "BOTTOM_RIGHT", "COTA")
zA0, zC0 = PT.zf(PT.X0[0]), PT.Z_TOP_C + 10                                     # fundo da TS-01: no recuo do P1 e no topo da I130
niv(-300, 0, "±0,000 piso", -1); niv(-300, M(10.0), "+10,000 platibanda", -1)
niv(Ly + 600, -1000, "fundo dos pilares −1,000; fundo do cálice −1,050 (graute 5 cm)", 1)
niv(-300, zA0, RN.novo(f"+{f(zA0 / 1000)} fundo"), -1); niv(-300, zA0 + 900 * PT.c, RN.novo(f"+{f((zA0 + 900 * PT.c) / 1000)} topo"), -1)
niv(Ly + 300, PT.zf(Ly - PT.X0[0]), f"+{f(Z_AS['P2'])} assento", 1); niv(Ly + 300, M(10.0), "+10,000 platibanda", 1)
c.chamada((M(X_FACH["C"]) - 300, PT.Z_TOP_C), (-26, 34), RN.novo(f"+{f(Z_TC)} topo I130 (fundo da viga de cobertura +10 mm do NEO-3C)"))
c.texto((M(9.0), PT.zf(9000) + 900 * PT.c + 700), "i = 3 % (caimento da TS-01 e da cobertura)", "nota", "BOTTOM_CENTER")
c.cota_h([0, M(X_FACH["C"]), Ly], -1300, -10)
c.cota_v([-1000, 0, zA0, M(10.0)], -3800, -10, total=False)
c.chamada((M(PONTAS[0][0]) + 140, M(zf(PONTAS[0][0]) + 0.45)), (12, 18), "apoio no recuo: NEO-4 + 2 PN-3 Ø25 grauteados")
c.chamada((M(PONTAS[1][1]) - 140, M(zf(PONTAS[1][1]) + 0.45)), (-14, -26), "apoio no recuo do pilar do eixo E")
c.chamada((Ly / 4, M(zf(Ly / 4000) + 0.2)), (12, -40), f"TS-01 I90 (h 90, sem dentes — apoio direto): {fp(PQ['TS-01'][7])} t, içar pelas 4 alças AL-1")
c.chamada((M(25), M(zf(25)) + 900 * PT.c + 160), (6, 20), "terças Z 302×90/82×19×2,30 nos ST-1P (4 M12) + TP40 + lã 40 + zipada + painéis (ND-LET-COB01)")

# ------------------------------------------------------------------ coluna direita: lista de peças, sequência, notas
XC = Q[2] - 200
y = Q[3] - 6
import json as _j
I130 = _j.load(open(AQ + "i110_r01.json"))

def grupo(mks, desc, apoio):
    qt = sum(PQ[m][5] for m in mks)
    pesos = sorted({PQ[m][7] for m in mks})
    pz = fp(pesos[0]) if len(pesos) == 1 else f"{fp(pesos[0])} a {fp(pesos[-1])}"
    nome = ", ".join(mks)                                  # rev08: nome de cada peça por extenso (regra do Nathan)
    return [nome, desc, str(qt), pz, apoio]
pecas = [grupo(["PL-01", "PL-05", "PL-09", "PL-10", "PL-11", "PL-12"], "Pilar 40×60 lateral (L3 a L8), L 1100, cabeça recuada", "cálice −1,00; topo +10,00"),
         grupo(["PL-02", "PL-06"], "Pilar 40×60 lateral c/ 2 CP-MEZ (L2)", "cálice −1,00; topo +10,00"),
         grupo(["PL-03", "PL-04", "PL-07", "PL-08"], "Pilar 40×60 de canto (L1, L9), cabeça recuada", "cálice −1,00; topo +10,00"),
         grupo(["PF-01", "PF-02", "PF-03", "PF-04", "PF-05", "PF-06"], "Pilar 40×60 de fachada (1 e 9) c/ CP-VB", "cálice −1,00; topo +10,00"),
         grupo(["PC-01", "PC-02", "PC-03"], "P8A 40×60, P11 40×40, P13 e P13B 40×40 (eixo C)", f"cálice −1,00; topo +{f(Z_TC)}"),
         grupo(["PM-01", "PM-02"], "Pilar do mezanino 40×60 (B2, D2), cabeça até o fundo da W 200", "ver ND-LET-MON02"),
         grupo(["PG-01", "PG-03"], "Pilares dos portões 40×40 (P9 / P12, linha 4)", "cálice −1,00; topo +7,47 / +8,06"),
         grupo(["PG-02", "PG-04"], "Pilares dos portões 25×25 (P10)", "cálice −1,00; topo +7,63 / +7,90"),
         grupo(["TS-01"], f"Viga I90 de cobertura, L {LG['L_TS']*100:.0f}, sem dentes", f"recuo +{f(Z_AS['P1'])} / topo I130 +{f(Z_TC)} / recuo +{f(Z_AS['P2'])}")]
for mk in ("V407", "V406", "V405", "V404"):
    pecas.append(grupo([mk], f"Viga I130 central, L {f(PQ[mk][4], 2)} m", f"consolos CP-I130 (+{f(LG['Z_ASS_I130'])})"))
for mk in [f"VB-0{k}" for k in range(1, 9)]:
    pecas.append(grupo([mk], f"Viga de borda 15×60 c/ dente, L {PQ[mk][4]*100:.0f} cm ({PQ[mk][2].split(',')[0]}{', fach. 9' if mk > 'VB-04' else ', fach. 1'})", "consolos CP-VB"))
y = pr.tabela(XC, y, "LISTA DE PEÇAS DE MONTAGEM — COBERTURA", ["MARCA", "DESCRIÇÃO", "QT", "PESO (t)", "APOIO / NÍVEL"], pecas, [26, 72, 14, 18, 70], h_lin=6.0)
seq = ["Ordem geral (decisão do Nathan, 21/10/2026): pilares → vigas → cobertura → mezanino → fechamento. Exceções obrigatórias, por geometria (ver ND-LET-MON03): a W 200 × 15,0 da linha 2 (metálica, com montantes W 150 × 13,0 sobre as VM, ND-LET-COB05), as VB-01 a VB-04 (fachada 1) e as terças dos vãos 1–2 e 2–3 ficam para DEPOIS do mezanino; a parede C (linha 4) vai ANTES da TS-01 da linha 4 e a parede G (linha 2) antes da W 200 da linha 2.",
       "Locar os cálices (±10 mm), nivelar o fundo com calços; conferir prumo das paredes do cálice.",
       "Pilares, todas as linhas: içar na horizontal pelas 2 AL-2 (face C), verticalizar e montar pelo furo FI-1, descer no cálice com a face C para fora, aprumar (10 mm/10 m) e travar com cunhas de madeira dura nas 4 faces antes de soltar o guindaste; grautear o cálice no mesmo dia (fck ≥ 30 MPa) e só apoiar vigas depois de 24 h (graute ≥ 15 MPa). Pilares engastados: ficam em balanço sem escoramento até receber as vigas (só peso próprio e vento nos pilares, sem placas).",
       f"Vigas centrais I130 V407, V406, V405 e V404 nos consolos CP-I130 dos PC: neoprene NEO-2 300×200×31 fretado; pino PN-2 grauteado numa ponta só. São as peças mais pesadas (até {fp(max(PQ[m][7] for m in ('V404', 'V405', 'V406', 'V407')))} t, {f(max(PQ[m][4] for m in ('V404', 'V405', 'V406', 'V407')), 1)} m): içar pelas 2 alças AL-3 ({I130['V407']['icamento']['n_lacos']} laços cada).",
       "Parede C da linha 4 (portões, ND-LET-MON03) antes da TS-01 da linha 4: depois dela o balancim da placa não passa entre a TS-01 e as terças do vão 4–5.",
       "TS-01 das linhas 8 → 3 (linha 2 sem TS-01, DEC-048; o guindaste trabalha de ré, sempre no vão ainda sem cobertura): NEO-4 no recuo dos pilares laterais (2 PN-3 Ø25) e NEO-3 no topo da I130 / P11 (2 PN-5 Ø20); grautear os tubos TB-3. VB-05 a VB-08 da fachada 9 (dente sobre os CP-VB; PN-6 grauteado só numa ponta, porca apertada após assentar), escoradas contra tombamento até as terças do vão 8–9.",
       "Cobertura dos vãos 3–4 a 8–9, atrás do guindaste: terças, correntes e X dos vãos 4–5 a 8–9 (tudo parafusado, sem mão-francesa), TP40, lã, zipada e painéis. A TS-01 da linha 3 fica travada pelas terças do vão 3–4 (um lado) até a cobertura do vão 2–3.",
       "Mezanino das linhas 1–2, pisos +3,90 e +7,30, com a escada metálica (ND-LET-MON02, ES01), com a cobertura dos vãos 1–2 e 2–3 ainda aberta: guindaste dentro do pavilhão no vão 2–3, entrando pela abertura lateral das vistas E/F (livre até +7,50 entre as linhas 2 e 4).",
       "Parede G da linha 2 e, depois, W 200 × 15,0 da linha 2 (apoiada direto na cabeça dos pilares A, B, C, D, P6 e E com chapa CA-L2 e presilhas e nos 4 montantes W 150 × 13,0 sobre as VM do +7,30, módulos com emendas parafusadas — ND-LET-COB05), VB-01 a VB-04 da fachada 1, terças do vão 1–2 (ST-W e mão-francesa MF-1 em toda terça da linha 2) e por último as do vão 2–3, com o guindaste saindo pela abertura lateral.",
       "Fechamento externo pelo lado de fora (ND-LET-MON03): fachada I e anexo (H, J), E e F (fiadas altas), laterais B e D e fachada A."]
y = pr.notas(XC, y - 4, seq, 200, titulo="SEQUÊNCIA DE MONTAGEM")
notas = ["Tolerâncias de montagem (NBR 9062:2017): pilar em planta ±10 mm; prumo 10 mm em 10 m; consolo ±10 mm; folga de ponta 25 mm e de dente 25 mm já previstas.",
         f"TS-01 só pode ser solta do guindaste com os pinos encaixados nos tubos TB-3 e a linha anterior travada; viga de {f(LG['L_TS'], 2)} m: içar pelas 4 alças com balancins.",
         f"Guindaste principal (pilares, I130, TS-01, VB, VM): autopropelido classe 90–100 t para a I130 V407 de {fp(PQ['V407'][7])} t a ~10–12 m de raio, dentro do pavilhão, sobre base compactada para as patolas (conferir a tabela de carga e o solo). Altura livre sob a cobertura montada: fundo da TS-01 de +7,19 (eixo A) a +7,78 (eixo C) — nenhuma peça é içada por baixo da cobertura.",
         f"Plano de rigging (NBR 9062:2017 3.17 e 11) a cargo da montadora, com os pesos desta lista: posição do guindaste, raio, patolas e capacidade do solo. Transporte: I130 V407 com {f(PQ['V407'][4], 1)} m e TS-01 com 19,7 m exigem carreta extensível e autorização especial de trânsito; transportar apoiadas nos pontos das alças.",
         f"Cobertura escondida: topo dos painéis solares {LG['platibanda']['folga_P2_mm']} mm abaixo da platibanda +10,00 no eixo E (mínimo pedido 150 mm).",
         "DEC-058: eixo C com dois PC-03 (P13 em y 46,317 e P13B em y 62,833); V404 vai do P13B até a linha 9 e apoia no consolo CP-I130 do pilar P14 (PF-04).",
         "Níveis em m, cotas em cm. Não medir no desenho. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(XC, y - 4, notas, 200)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-MON01")
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
for a in avisos:
    if a[0] == "ERRO" or "sobrep" in a[1]:
        print(a)
