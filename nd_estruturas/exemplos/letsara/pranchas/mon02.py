"""ND-LET-MON02 — planta de montagem do mezanino (níveis +3,15 e +6,55, linhas 1–2): pilares, vigas VM (I90 c/ dentes 45×30),
lajes alveolares h20 + capa 5; corte de montagem; lista de peças e sequência. Cotas em cm, níveis em m. A1."""
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha

f = lambda v, d=3: f"{v:.{d}f}".replace(".", ",")
X_FACH = [("A", 0.0), ("B", 9.87), ("C", 20.05), ("D", 29.63), ("E", 40.10)]
Y1, Y2 = 0.0, 10.05
NIVEIS = [3.15, 6.55]
H_LAJE, H_CAPA, H_VIGA, H_DENTE = 0.20, 0.05, 0.90, 0.45          # VM I90 com dente 45: assento = nível − laje − capa − dente
ASSENTO = [round(n - H_LAJE - H_CAPA - H_DENTE, 3) for n in NIVEIS]      # topo da viga = nível − laje − capa; apoio direto (sem dente)
M = lambda v: v * 1000
A_I70 = 0.40 * 0.15 * 2 + 0.15 * 0.60 + 2 * 0.5 * 0.125 * 0.08 * 2      # seção I90
VM = []                                                                    # (marca, xa, xb, L)
for k, ((na, xa), (nb, xb)) in enumerate(zip(X_FACH[:-1], X_FACH[1:]), 1):
    VM.append((f"VM-0{k}", xa + 0.325, xb - 0.325, round(xb - xa - 0.65, 2)))
N_LAJE = int((40.10 - 0.60) // 1.25)
PIL1 = [("PL-03", 0.0, 400, 600), ("PF-01", 9.87, 600, 400), ("PF-02", 20.05, 600, 400), ("PF-03", 29.63, 600, 400), ("PL-07", 40.10, 400, 600)]
PIL2 = [("PL-02", 0.0, 400, 600), ("PM-01", 9.87, 600, 400), ("PC-01", 20.05, 500, 500), ("PM-01", 29.63, 600, 400), ("PL-06", 40.10, 400, 600)]

pr = Prancha("A1", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="PLANTA DE MONTAGEM DO MEZANINO (+3,15 E +6,55) — VIGAS VM, LAJES ALVEOLARES, CORTE, LISTA DE PEÇAS E SEQUÊNCIA",
                        desenho="ND-LET-MON02", folha="02/02", fase="PARA APROVAÇÃO"))
pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL")
Q = pr.quadro


def planta(nome, origem, nivel, assento):
    v = pr.vista(nome, origem, 100, titulo=f"PLANTA DE MONTAGEM — MEZANINO +{f(nivel, 2)}", subtitulo=f"linhas 1–2; assento dos consolos CP-MEZ em +{f(assento)}", unidade="cm")
    Lx = M(40.10)
    for nome_, x in X_FACH:
        v.eixo((M(x), -1800), (M(x), M(Y2) + 1800), 600)
        v.circulo((M(x), M(Y2) + 2600), 500, "VISTA"); v.texto((M(x), M(Y2) + 2600), nome_, "nota", "MIDDLE_CENTER")
    for k, y in ((1, Y1), (2, Y2)):
        v.eixo((-1800, M(y)), (Lx + 1800, M(y)), 600)
        v.circulo((-2600, M(y)), 500, "VISTA"); v.texto((-2600, M(y)), str(k), "nota", "MIDDLE_CENTER")
    # lajes alveolares (31 painéis de 1,25 m, vão entre as vigas)
    for k in range(N_LAJE):
        x = 0.925 + k * 1.25
        v.ret(M(x - 0.62), M(Y1) + 200, 1240, M(Y2 - Y1) - 400, "VISTA")
        if k % 5 == 2:
            v.texto((M(x), M((Y1 + Y2) / 2)), f"LA-01 ({k + 1})", "min", "MIDDLE_CENTER", rot=90)
    v.poli([(M(1.5), M(3.0)), (M(1.5), M(7.0)), (M(1.35), M(6.7)), (M(1.5), M(7.0)), (M(1.65), M(6.7))], "COTA")
    v.texto((M(1.5) + 200, M(5.0)), "vão da laje 9,65 m", "min", "MIDDLE_LEFT", rot=90)
    # vigas VM (I90) nas linhas 1 e 2
    for y in (Y1, Y2):
        for marca, xa, xb, L in VM:
            v.ret(M(xa), M(y) - 200, M(xb - xa), 400, "CORTADO")
            v.texto((M((xa + xb) / 2), M(y) + (300 if y == Y1 else -300)), f"{marca} (I90, L {f(L, 2)} m)", "min", "BOTTOM_CENTER" if y == Y1 else "TOP_CENTER")
            for xd in (M(xa) + 150, M(xb) - 150):
                v.circulo((xd, M(y)), 50, "VISTA")
    # pilares
    for (marca, x, bx, by), y in [(p, Y1) for p in PIL1] + [(p, Y2) for p in PIL2]:
        pts = [(M(x) - bx / 2, M(y) - by / 2), (M(x) + bx / 2, M(y) - by / 2), (M(x) + bx / 2, M(y) + by / 2), (M(x) - bx / 2, M(y) + by / 2)]
        v.poli(pts, "CORTADO", fechada=True); v.hachura(pts, "SOLID", 1, "CORTADO")
        v.texto((M(x) + bx / 2 + 150, M(y) + (-700 if y == Y1 else 700)), marca, "min", "MIDDLE_LEFT")
    v.cota_h([M(x) for _, x in X_FACH], -2400, -8)
    v.cota_v([M(Y1), M(Y2)], Lx + 2400, 8, total=False)
    return v

v1 = planta("PLANTA +3,15", (Q[0] + 40, Q[3] - 165), NIVEIS[0], ASSENTO[0])
v1.marcador_corte((M(15.0), -3000), (M(15.0), M(Y2) + 3000), "2", lado=1)
v2 = planta("PLANTA +6,55", (Q[0] + 40, Q[3] - 357), NIVEIS[1], ASSENTO[1])

# ------------------------------------------------------------------ CORTE 2-2 (1:50) — linhas 1–2, dois níveis
c = pr.vista("CORTE 2-2", (Q[0] + 515, Q[3] - 370), 50, titulo="CORTE 2-2 — MEZANINO (ENTRE OS EIXOS B E C)", subtitulo="vigas VM I90 com dentes nos consolos CP-MEZ; laje alveolar h20 + capa 5", unidade="cm")
c.linha((-1500, 0), (M(Y2) + 1500, 0), "TERRENO")
for x, marca in ((0, "PF-02 (linha 1)"), (M(Y2), "PC-01 (linha 2)")):
    c.ret(x - 300, -1000, 600, 1000 + M(7.6), "VISTA")
    c.ret(x - 450, -1000, 900, 1000, "OCULTA")
    c.texto((x, M(7.6) + 150), marca, "min", "BOTTOM_CENTER")
    c.interrupcao((x - 300, M(7.6)), (x + 300, M(7.6)))
for n, a in zip(NIVEIS, ASSENTO):
    for x, sg in ((0, 1), (M(Y2), -1)):
        c.poli([(x + sg * 300, M(a) - 350), (x + sg * 600, M(a) - 200), (x + sg * 600, M(a)), (x + sg * 300, M(a))], "VISTA")   # consolo CP-MEZ
        c.ret(x + sg * 300 if sg > 0 else x - 600, M(a), 300, 10, "METALICA")                                              # neoprene
    # viga VM em corte longitudinal (I70) com dentes 425 nas pontas
    zt = M(n - H_LAJE - H_CAPA)
    c.poli([(325, zt - 450), (325, zt), (M(Y2) - 325, zt), (M(Y2) - 325, zt - 450), (M(Y2) - 625, zt - 450), (M(Y2) - 625, zt - 900),
            (625, zt - 900), (625, zt - 450)], "VISTA", fechada=True)
    c.ret(725, zt, M(Y2) - 1450, 200, "VISTA")                                                                           # laje alveolar
    c.hachura([(725, zt + 200), (M(Y2) - 725, zt + 200), (M(Y2) - 725, zt + 250), (725, zt + 250)], "AR-CONC", 0.02)   # capa
    c.linha((725, zt + 250), (M(Y2) - 725, zt + 250), "VISTA")
    c.chamada((M(5.0), zt + 250), (10, 10), f"nível +{f(n, 2)}: laje h20 + capa 5 (armada c/ tela Q138)")
    c.chamada((M(Y2) - 475, zt - 300), (12, -14), f"dente 45 × 30 + pino PN-1; assento +{f(a)}")
c.chamada((M(2.0), M(NIVEIS[0] - 0.8)), (10, -12), "VM-02 I90 protendida, 5,2 t, içar pelas 2 alças")
c.cota_h([0, M(Y2)], -1000, -10)
c.cota_v([-1000, 0, M(ASSENTO[0]), M(NIVEIS[0]), M(ASSENTO[1]), M(NIVEIS[1])], -500, -10, total=False)
def niv(x, z, txt, lado=1):
    c.poli([(x, z), (x + lado * 120, z + 120), (x + lado * 120, z - 120), (x, z)], "COTA")
    c.linha((x + lado * 120, z), (x + lado * 700, z), "COTA")
    c.texto((x + lado * 150, z + 40), txt, "min", "BOTTOM_LEFT" if lado > 0 else "BOTTOM_RIGHT", "COTA")
niv(M(Y2) + 300, 0, "±0,000", 1)
for n, a in zip(NIVEIS, ASSENTO):
    niv(M(Y2) + 300, M(n), f"+{f(n, 2)} piso acabado", 1); niv(M(Y2) + 300, M(a), f"+{f(a)} assento", 1)

# ------------------------------------------------------------------ coluna direita
XC = Q[2] - 200
y = Q[3] - 6
pecas = [[m, f"Viga I90 protendida c/ dentes 45×30, L {f(L, 2)} m", "4", f(A_I70 * 25 * L / 10, 1), f"CP-MEZ +{f(ASSENTO[0])} / +{f(ASSENTO[1])}"] for m, _, _, L in VM]
pecas += [["LA-01", "Laje alveolar h20, 125×965 (confirmar c/ fabricante)", f"{2 * N_LAJE}", "3,2", "sobre as VM, apoio 10 cm + neoprene"],
          ["CP-MEZ", "Consolo 40×30×35/20 nos pilares das linhas 1–2 (2 níveis)", "20", "—", "ver pranchas dos pilares"],
          ["PM-01", "Pilar 40×60 do mezanino (B2, D2), topo +6,55 + capa", "2", "4,6", "cálice −1,00"]]
y = pr.tabela(XC, y, "LISTA DE PEÇAS DE MONTAGEM — MEZANINO", ["MARCA", "DESCRIÇÃO", "QT", "PESO (t)", "APOIO / NÍVEL"], pecas, [18, 92, 10, 18, 62], h_lin=6.0)
seq = ["Pilares das linhas 1 e 2 já grauteados e com 24 h (ND-LET-MON01, etapa 2).",
       f"Nível +{f(NIVEIS[0],2)}: vigas VM-01 a VM-04 na linha 1 e depois na linha 2; neoprene no consolo, pino numa ponta grauteado, outra com graute flexível.",
       "Lajes alveolares LA-01 de A para E, apoio mínimo 10 cm sobre a viga, faixa de neoprene; chavetas grauteadas antes da capa.",
       "2º estágio: limpar e molhar o topo das VM; amarrar N10 e negativas Ø10 c/25 nos alvéolos; grautear chavetas; tela Q138; concretar enchimento 30 × 20 sobre a mesa da VM + capa de 5 cm C25 de uma vez, envolvendo os estribos salientes N9 Ø8 c/15 (ND-LET-VM01 corte C-C, MC04); não carregar antes de 7 dias (fck ≥ 20 MPa).",
       f"Repetir para o nível +{f(NIVEIS[1],2)}. A cobertura das linhas 1–2 só é montada depois da capa do +{f(NIVEIS[1],2)}.",
       "Laje alveolar h20 sem escoramento; vigas VM sem escoramento (protendidas, 2º estágio na capa)."]
y = pr.notas(XC, y - 4, seq, 200, titulo="SEQUÊNCIA DE MONTAGEM")
notas = ["Laje alveolar h20 + 5 em 9,65 m com 500 kgf/m²: a seção genérica (7 Ø12,7) NÃO passou no ELU; o fabricante deve apresentar tabela de carga ou subir para h26,5 + 5.",
         "Vigas VM em I90 com dentes Gerber 45 × 30 (o dente da I70 foi reprovado no MEF): assentos +2,450 e +5,850 (ND-LET-VM01 e ND-LET-PM01); pé-direito livre sob a viga = nível − 115 cm.",
         "Tolerâncias NBR 9062:2017: pilar ±10 mm; consolo ±10 mm; folga de ponta 25 mm; apoio da laje ≥ 10 cm medido após a montagem.",
         "Níveis em m, cotas em cm. Não medir no desenho. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(XC, y - 4, notas, 200)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-MON02")
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
for a in avisos:
    if a[0] == "ERRO" or "sobrep" in a[1]:
        print(a)
