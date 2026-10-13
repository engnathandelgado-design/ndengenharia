"""ND-LET-MON02 — planta de montagem do mezanino (níveis +3,15 e +6,55, linhas 1–2): pilares, vigas VM (I90 c/ dentes 45×30),
lajes alveolares h20 + capa 5; corte de montagem; lista de peças e sequência. Cotas em cm, níveis em m. A1."""
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha

f = lambda v, d=3: f"{v:.{d}f}".replace(".", ",")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
import json
from geometria import Y_LIN, X_EIXO
from lajes_placas import paineis_mez
X_FACH = list(X_EIXO.items())
Y1, Y2 = Y_LIN[0], Y_LIN[1]
LARG = X_EIXO["E"]
NIVEIS = [3.15, 6.55]
H_LAJE, H_CAPA, H_VIGA, H_DENTE = 0.20, 0.05, 0.90, 0.45          # VM I90 com dente 45: assento = nível − laje − capa − dente
ASSENTO = [round(n - H_LAJE - H_CAPA - H_DENTE, 3) for n in NIVEIS]
H_CMEZ = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/consolos.json"))["CP-MEZ"]["h_total_m"] * 1000
M = lambda v: v * 1000
A_I90 = (400 * 120 + 400 * 150 + 150 * (900 - 270) + 2 * 0.5 * 125 * 80 * 2) / 1e6            # = area_I de viga_i.py
# VM: face do pilar lateral 30 (60 em x) ou 20 (pilares B, C, D com 40 em x); folga 5 cm de cada lado
FACE = {"A": 0.30, "B": 0.20, "C": 0.20, "D": 0.20, "E": 0.30}
VM = []                                                                    # (marca, xa, xb, L)
for (na, xa), (nb, xb) in zip(X_FACH[:-1], X_FACH[1:]):
    a_, b_ = xa + FACE[na] + 0.05, xb - FACE[nb] - 0.05
    VM.append(("VM-01" if "A" in (na, nb) or "E" in (na, nb) else "VM-02", a_, b_, round(b_ - a_, 2)))
PAINEIS, QT_LAJE, L_P = paineis_mez()
PIL1 = [("PL-03", 0.0, 600, 400), ("PF-01", X_EIXO["B"], 400, 600), ("PF-02", X_EIXO["C"], 400, 600), ("PF-03", X_EIXO["D"], 400, 600), ("PL-07", LARG, 600, 400)]
PIL2 = [("PL-02", 0.0, 600, 400), ("PM-01", X_EIXO["B"], 400, 600), ("PC-01", X_EIXO["C"], 400, 600), ("PM-01", X_EIXO["D"], 400, 600), ("PL-06", LARG, 600, 400)]

pr = Prancha("A1", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="PLANTA DE MONTAGEM DO MEZANINO (+3,15 E +6,55) — VIGAS VM, LAJES ALVEOLARES, CORTE, LISTA DE PEÇAS E SEQUÊNCIA",
                        desenho="ND-LET-MON02", folha="02/02", fase="PARA APROVAÇÃO", rev="01"))
pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL")
pr.revisao("01", "12/10/2026", "GEOMETRIA DO R01; VM-01/VM-02; CONSOLOS SEM CHANFRO; CORTE 2-2 REFEITO")
Q = pr.quadro


def planta(nome, origem, nivel, assento):
    v = pr.vista(nome, origem, 100, titulo=f"PLANTA DE MONTAGEM — MEZANINO +{f(nivel, 2)}", subtitulo=f"linhas 1–2; assento dos consolos CP-MEZ em +{f(assento)}", unidade="cm")
    Lx = M(LARG)
    for nome_, x in X_FACH:
        v.eixo((M(x), -1800), (M(x), M(Y2) + 1800), 600)
        v.circulo((M(x), M(Y2) + 2600), 500, "VISTA"); v.texto((M(x), M(Y2) + 2600), nome_, "nota", "MIDDLE_CENTER")
    for k, y in ((1, Y1), (2, Y2)):
        v.eixo((-1800, M(y)), (Lx + 1800, M(y)), 600)
        v.circulo((-2600, M(y)), 500, "VISTA"); v.texto((-2600, M(y)), str(k), "nota", "MIDDLE_CENTER")
    # lajes alveolares (mesma paginação da ND-LET-LA01)
    for i, (x0, b, mk) in enumerate(PAINEIS):
        v.ret(x0, M(Y1) + 100, b - 10, L_P, "VISTA")
        if mk != "LA-01" or i % 5 == 3:
            v.texto((x0 + b / 2, M((Y1 + Y2) / 2)), mk, "min", "MIDDLE_CENTER", rot=90)
    v.poli([(M(1.5), M(3.0)), (M(1.5), M(7.0)), (M(1.35), M(6.7)), (M(1.5), M(7.0)), (M(1.65), M(6.7))], "COTA")
    v.texto((M(1.5) + 200, M(4.0)), f"vão da laje {f(Y2, 2)} m", "min", "MIDDLE_LEFT", rot=90)
    # vigas VM (I90) nas linhas 1 e 2
    for y in (Y1, Y2):
        for marca, xa, xb, L in VM:
            v.ret(M(xa), M(y) - 200, M(xb - xa), 400, "CORTADO")
            v.texto((M((xa + xb) / 2), M(y) + (-500 if y == Y1 else 500)), f"{marca} (I90, L {f(L, 2)} m)", "min", "TOP_CENTER" if y == Y1 else "BOTTOM_CENTER")
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
v1.marcador_corte((M(12.0), -3000), (M(12.0), M(Y2) + 3000), "2", lado=1)
v2 = planta("PLANTA +6,55", (Q[0] + 40, Q[3] - 357), NIVEIS[1], ASSENTO[1])

# ------------------------------------------------------------------ CORTE 2-2 (1:50) — plano entre B e C, olhando para C
c = pr.vista("CORTE 2-2", (Q[0] + 515, Q[3] - 370), 50, titulo="CORTE 2-2 — MEZANINO (ENTRE OS EIXOS B E C, OLHANDO PARA C)",
             subtitulo="VM-02 I90 em corte nas linhas 1 e 2; laje alveolar h20 + capa 5 em vista longitudinal; pilares do eixo C ao fundo", unidade="cm")
c.linha((-1500, 0), (M(Y2) + 1500, 0), "TERRENO")
Z_VISTA = 7600
for y, marca in ((0, "PF-02 (C1) ao fundo"), (M(Y2), "PC-01 (C2) ao fundo")):
    c.ret(y - 300, -1000, 600, 1000 + Z_VISTA, "VISTA")
    c.ret(y - 450, -1000, 900, 1000, "OCULTA")
    c.texto((y, Z_VISTA + 150), marca, "min", "BOTTOM_CENTER")
    c.interrupcao((y - 300, Z_VISTA), (y + 300, Z_VISTA))
def secao_I(yc, zt):
    """I90 (b 40, mesas 12/15, alma 15, mísulas 12,5 × 8) com topo em zt — cortada."""
    b, bw, ts, ti, m_ = 200, 75, 120, 150, 80
    pts = [(yc - b, zt - 900), (yc + b, zt - 900), (yc + b, zt - 900 + ti), (yc + bw, zt - 900 + ti + m_), (yc + bw, zt - ts - m_),
           (yc + b, zt - ts), (yc + b, zt), (yc - b, zt), (yc - b, zt - ts), (yc - bw, zt - ts - m_), (yc - bw, zt - 900 + ti + m_), (yc - b, zt - 900 + ti)]
    c.poli(pts, "CORTADO", fechada=True); c.hachura(pts, "ANSI31", 1.5, "CORTADO")
for n, a in zip(NIVEIS, ASSENTO):
    zt = M(n - H_LAJE - H_CAPA)
    for y in (0, M(Y2)):
        secao_I(y, zt)
        c.ret(y - 200, M(a) - H_CMEZ, 400, H_CMEZ, "OCULTA")                     # consolo CP-MEZ atrás da VM (fundo alinhado)
    c.ret(100, zt, M(Y2) - 200, 200, "VISTA")                                     # laje alveolar (apoio 10 cm na mesa)
    for y0, y1 in ((-200, 100), (M(Y2) - 100, M(Y2) + 200)):                      # enchimento sobre a mesa da VM
        c.hachura([(y0, zt), (y1, zt), (y1, zt + 200), (y0, zt + 200)], "AR-CONC", 0.02)
    c.hachura([(-200, zt + 200), (M(Y2) + 200, zt + 200), (M(Y2) + 200, zt + 250), (-200, zt + 250)], "AR-CONC", 0.02)   # capa
    c.ret(-200, zt + 200, M(Y2) + 400, 50, "VISTA")
    c.chamada((M(5.0), zt + 250), (10, 10), f"nível +{f(n, 2)}: laje h20 + capa 5 (tela Q138)")
c.chamada((M(Y2) - 200, M(ASSENTO[0]) - 200), (-40, -22), f"CP-MEZ {H_CMEZ/10:.0f} cm sem chanfro, oculto atrás da VM (fundos alinhados)")
c.chamada((200, M(NIVEIS[0] - 0.8)), (10, -12), f"VM-02 I90 protendida, {f(A_I90 * 25 * VM[1][3] / 10, 1)} t, içar pelas 2 alças")
c.cota_h([0, M(Y2)], -1000, -10)
c.cota_v([-1000, 0, M(ASSENTO[0]), M(NIVEIS[0]), M(ASSENTO[1]), M(NIVEIS[1])], -900, -10, total=False)
def niv(x, z, txt, lado=1):
    c.poli([(x, z), (x + lado * 120, z + 120), (x + lado * 120, z - 120), (x, z)], "COTA")
    c.linha((x + lado * 120, z), (x + lado * 700, z), "COTA")
    c.texto((x + lado * 150, z + 40), txt, "min", "BOTTOM_LEFT" if lado > 0 else "BOTTOM_RIGHT", "COTA")
niv(M(Y2) + 400, 0, "±0,000", 1)
for n, a in zip(NIVEIS, ASSENTO):
    niv(M(Y2) + 400, M(n), f"+{f(n, 2)} piso acabado", 1); niv(M(Y2) + 400, M(a), f"+{f(a)} assento", 1)

# ------------------------------------------------------------------ coluna direita
XC = Q[2] - 200
y = Q[3] - 6
VMQ = {}
for m, _, _, L in VM:
    VMQ.setdefault(m, L)
pecas = [[m, f"Viga I90 protendida c/ dentes 45×30, L {f(L, 2)} m", "8", f(A_I90 * 25 * L / 10, 1), f"CP-MEZ +{f(ASSENTO[0])} / +{f(ASSENTO[1])}"] for m, L in VMQ.items()]
PESO_LA = 2.65 * L_P / 1000                                     # kN/m² × comprimento → kN por metro de largura
for mk in ("LA-01", "LA-01R", "LA-02", "LA-02R"):
    if mk in QT_LAJE:
        bb = 1.25 if mk.startswith("LA-01") else 0.70
        pecas.append([mk, f"Laje alveolar h20, {bb*100:.0f}×{L_P/10:.0f}{' c/ recorte' if mk.endswith('R') else ''}", f"{QT_LAJE[mk]}", f(PESO_LA * bb / 10, 1), "sobre as VM, apoio 10 cm"])
pecas += [["CP-MEZ", f"Consolo 40×30×{H_CMEZ/10:.0f} sem chanfro (pilares das linhas 1–2)", "32", "—", "nos pilares (ver pranchas)"],
          ["PM-01", "Pilar 40×60 do mezanino (B2, D2), L 755", "2", f(0.24 * 7.55 * 25 / 10, 1), "cálice −1,00"]]
y = pr.tabela(XC, y, "LISTA DE PEÇAS DE MONTAGEM — MEZANINO", ["MARCA", "DESCRIÇÃO", "QT", "PESO (t)", "APOIO / NÍVEL"], pecas, [18, 92, 10, 18, 62], h_lin=6.0)
seq = ["Pilares das linhas 1 e 2 já grauteados e com 24 h (ND-LET-MON01, etapa 2).",
       f"Nível +{f(NIVEIS[0],2)}: vigas VM-01 e VM-02 na linha 1 e depois na linha 2; neoprene no consolo, pino numa ponta grauteado, outra com graute flexível.",
       "Lajes alveolares LA-01 de A para E, apoio mínimo 10 cm sobre a viga, faixa de neoprene; chavetas grauteadas antes da capa.",
       "2º estágio: limpar e molhar o topo das VM; amarrar N10 e negativas Ø10 c/25 nos alvéolos; grautear chavetas; tela Q138; concretar enchimento 30 × 20 sobre a mesa da VM + capa de 5 cm C25 de uma vez, envolvendo os estribos salientes N9 Ø8 c/15 (ND-LET-VM01 corte C-C, MC04); não carregar antes de 7 dias (fck ≥ 20 MPa).",
       f"Repetir para o nível +{f(NIVEIS[1],2)}. A cobertura das linhas 1–2 só é montada depois da capa do +{f(NIVEIS[1],2)}.",
       "Laje alveolar h20 sem escoramento; vigas VM sem escoramento (protendidas, 2º estágio na capa)."]
y = pr.notas(XC, y - 4, seq, 200, titulo="SEQUÊNCIA DE MONTAGEM")
notas = [f"Laje alveolar h20 + 5 em {f(L_P/1000, 2)} m com 500 kgf/m²: seção genérica com 8 Ø12,7 passa (MRd 215 ≥ 192 kN·m por painel; ELS-D ok). Confirmar com a tabela do fabricante (ND-LET-LA01).",
         "Vigas VM em I90 com dentes Gerber 45 × 30 (o dente da I70 foi reprovado no MEF): assentos +2,450 e +5,850 (ND-LET-VM01 e ND-LET-PM01); pé-direito livre sob a viga = nível − 115 cm. Consolos CP-MEZ sem chanfro, h 44 cm, fundo alinhado ao da VM.",
         "Tolerâncias NBR 9062:2017: pilar ±10 mm; consolo ±10 mm; folga de ponta 25 mm; apoio da laje ≥ 10 cm medido após a montagem.",
         "Níveis em m, cotas em cm. Não medir no desenho. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(XC, y - 4, notas, 200)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-MON02")
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
for a in avisos:
    if a[0] == "ERRO" or "sobrep" in a[1]:
        print(a)
