"""ND-LET-MON02 — planta de montagem do mezanino (rev09: pisos +3,90 e +7,30, linhas 1–2): pilares, vigas VM retangulares
protendidas 30 × 75 com dente (DEC-049), lajes alveolares h20 + capa 5 (abertura da escada no +3,90, DEC-045); corte de montagem;
lista de peças e sequência. Cotas em cm, níveis em m. A1."""
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha
import pecas_obra as QT                                     # peças = mesma fonte das listas (quantitativos.py)
PQ = {p_[1]: p_ for p_ in QT.pecas}
fp = lambda t_: f"{t_:.1f}".replace(".", ",")

f = lambda v, d=3: f"{v:.{d}f}".replace(".", ",")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
import json
from geometria import Y_LIN, X_EIXO, Z_PISOS, ABERTURA, P6_ESC, P7_ESC, P6_L2
from lajes_placas import paineis_nivel
import renomear as RN
X_FACH = list(X_EIXO.items())
Y1, Y2 = Y_LIN[0], Y_LIN[1]
LARG = X_EIXO["E"]
NIVEIS = list(Z_PISOS)
NIVS = [f"+{z:.2f}".replace(".", ",") for z in NIVEIS]
VMJ = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/vm_retangular.json"))
VMP = VMJ["premissas"]
H_LAJE, H_CAPA, H_VIGA, H_DENTE, B_VM = 0.20, 0.05, VMP["h_pm"], VMP["dente"]["hd"], VMP["b"]
L_DENTE = VMP["dente"]["ln"]
import pilar_generico as _G
ASSENTO = [z / 1000 for z in _G.Z_MEZ_ASS]
H_CMEZ = VMP["dente"]["consolo_h"] * 1000
M = lambda v: v * 1000
from lajes_placas import vigas_nivel


QT_LAJE = {}
for _iz in (0, 1):
    for _p in paineis_nivel(_iz):
        QT_LAJE[_p[2]] = QT_LAJE.get(_p[2], 0) + 1
L_P = paineis_nivel(1)[1][4] - paineis_nivel(1)[1][3]
PIL = [(0.0, Y1, 600, 400), (X_EIXO["B"], Y1, 400, 600), (X_EIXO["C"], Y1, 400, 600), (X_EIXO["D"], Y1, 400, 600), (LARG, Y1, 600, 400),
       (0.0, Y2, 600, 400), (X_EIXO["B"], Y2, 400, 600), (X_EIXO["C"], Y2, 400, 600), (X_EIXO["D"], Y2, 400, 600), (P6_L2[0], Y2, 250, 400), (LARG, Y2, 600, 400)]
PIL_390 = [(P6_ESC[0], P6_ESC[1], 250, 400), (P7_ESC[0], P7_ESC[1], 600, 400)]

pr = Prancha("A1", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="PLANTA DE MONTAGEM DO MEZANINO (+3,90 E +7,30) — VIGAS VM, LAJES ALVEOLARES, CORTE, LISTA DE PEÇAS E SEQUÊNCIA",
                        desenho="ND-LET-MON02", folha="02/03", fase="PARA APROVAÇÃO", rev="04"))
pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL")
pr.revisao("01", "12/10/2026", "GEOMETRIA DO R01; VM-01/VM-02; CONSOLOS SEM CHANFRO; CORTE 2-2 REFEITO")
pr.revisao("04", "16/10/2026", "NBR 9062: VM EM MEIO VASO COM DENTE, 2º ESTÁGIO E CT-1; SEQUÊNCIA SEM ESCORAMENTO")
pr.revisao("09", "23/10/2026", "DEC-045/047/048/049: PISOS +3,90/+7,30; VM RETANGULAR 30 × 75; ESCADA (P6, P7, VM-03/VM-04, LA-03/LA-04)")
Q = pr.quadro


def planta(nome, origem, iz):
    nivel, assento = NIVEIS[iz], ASSENTO[iz]
    v = pr.vista(nome, origem, 100, titulo=f"PLANTA DE MONTAGEM — PISO {NIVS[iz]}",
                 subtitulo=f"linhas 1–2; assento dos consolos CP-MEZ em +{f(assento)}" + ("; abertura da escada metálica (ND-LET-ES01)" if iz == 0 else "; laje de cobertura do bloco (acesso só para manutenção), contínua"), unidade="cm")
    Lx = M(LARG)
    for nome_, x in X_FACH:
        v.eixo((M(x), -1800), (M(x), M(Y2) + 1800), 600)
        v.circulo((M(x), M(Y2) + 2600), 500, "VISTA"); v.texto((M(x), M(Y2) + 2600), nome_, "nota", "MIDDLE_CENTER")
    for k, y in ((1, Y1), (2, Y2)):
        v.eixo((-1800, M(y)), (Lx + 1800, M(y)), 600)
        v.circulo((-2600, M(y)), 500, "VISTA"); v.texto((-2600, M(y)), str(k), "nota", "MIDDLE_CENTER")
    for i, (x0, b, mk, y0, y1) in enumerate(paineis_nivel(iz)):
        v.ret(x0, y0, b - 10, y1 - y0, "VISTA")
        if mk != "LA-01" or i % 5 == 3:
            v.texto((x0 + b / 2, (y0 + y1) / 2), f"{mk} LP20+5", "min", "MIDDLE_CENTER", rot=90)
    v.poli([(M(1.5), M(3.0)), (M(1.5), M(7.0)), (M(1.35), M(6.7)), (M(1.5), M(7.0)), (M(1.65), M(6.7))], "COTA")
    v.texto((M(1.5) + 200, M(4.0)), f"laje {f(L_P / 1000, 2)} m", "min", "MIDDLE_LEFT", rot=90)
    if iz == 0:
        ab = [(M(ABERTURA["x0"]), M(ABERTURA["y0"])), (M(ABERTURA["x1"]), M(ABERTURA["y0"])), (M(ABERTURA["x1"]), M(ABERTURA["y1"])), (M(ABERTURA["x0"]), M(ABERTURA["y1"]))]
        v.poli(ab, "OCULTA", fechada=True)
        v.texto(((ab[0][0] + ab[2][0]) / 2, (ab[0][1] + ab[2][1]) / 2), "ESCADA METÁLICA (ES01)", "min", "MIDDLE_CENTER", rot=90)
    for marca, xa, xb, y in vigas_nivel(iz):
        v.ret(M(xa), M(y) - M(B_VM) / 2, M(xb - xa), M(B_VM), "CORTADO")
        nv = RN.viga_em(NIVS[iz], (xa + xb) / 2, y) or marca
        acima = y == Y2 or (iz == 0 and abs(y - P6_ESC[1]) < 0.01)
        sec_ = RN.secao(nv)                                                  # rev11: nome + seção (pedido do Nathan, 26/10)
        txt = f"{nv} {sec_} (L {f(xb - xa, 2)})" if xb - xa > 5 else f"{nv} {sec_}"
        dz_ = 500 if xb - xa > 5 else 1050                                   # vigas curtas: rótulo afastado dos nomes dos pilares
        v.texto((M((xa + xb) / 2), M(y) + (dz_ if acima else -dz_)), RN.novo(txt.strip()), "min", "BOTTOM_CENTER" if acima else "TOP_CENTER")
        for xd in (M(xa) + M(VMP["x_pad"]) - 30, M(xb) - M(VMP["x_pad"]) + 30):
            v.circulo((xd, M(y)), 50, "VISTA")
    for x, y, bx, by in PIL + (PIL_390 if iz == 0 else []):
        pts = [(M(x) - bx / 2, M(y) - by / 2), (M(x) + bx / 2, M(y) - by / 2), (M(x) + bx / 2, M(y) + by / 2), (M(x) - bx / 2, M(y) + by / 2)]
        v.poli(pts, "CORTADO", fechada=True); v.hachura(pts, "SOLID", 1, "CORTADO")
        nm = RN.pilar_em(x, y)
        if nm:
            esc_ = abs(y - P6_ESC[1]) < 0.01
            v.texto((M(x) + (bx / 2 + 150 if x < LARG - 1 else -bx / 2 - 150), M(y) + (700 if esc_ else (-700 if y == Y1 else 700))), RN.rotulo(nm), "min",
                    "MIDDLE_LEFT" if x < LARG - 1 else "MIDDLE_RIGHT")
    v.cota_h([M(x) for _, x in X_FACH], -2400, -8)
    v.cota_v([M(Y1), M(Y2)], Lx + 2400, 8, total=False)
    return v

v1 = planta("PLANTA +3,90", (Q[0] + 40, Q[3] - 160), 0)
v1.marcador_corte((M(12.6), -4400), (M(12.6), M(Y2) + 3000), "M", lado=1)
v2 = planta("PLANTA +7,30", (Q[0] + 40, Q[3] - 342), 1)

# ------------------------------------------------------------------ CORTE M-M (1:50) — plano entre B e C, olhando para C
c = pr.vista("CORTE M-M", (Q[0] + 90, Q[1] + 48), 75, titulo="CORTE M-M — MEZANINO (ENTRE OS EIXOS B E C, OLHANDO PARA C)",
             subtitulo="VM retangulares 30 × 75 em corte nas linhas 1 e 2 (2º estágio do lado da borda); laje h20 + capa 5; pilares do eixo C ao fundo", unidade="cm")
c.linha((-1500, 0), (M(Y2) + 1500, 0), "TERRENO")
Z_VISTA = 8300
for y, marca in ((0, RN.pilar_em(X_EIXO["C"], Y1)), (M(Y2), RN.pilar_em(X_EIXO["C"], Y2))):
    c.ret(y - 300, 0, 600, Z_VISTA, "VISTA")
    import pe_pilar as PP                                                   # rev11: pé no cálice (ao fundo: tracejado) + L total
    PP.pe(c, X_EIXO["C"], y / 1000, y, "y", cotar=False, lado=-1, oculto=True)   # embutimento já na cota de níveis (−1,00 → ±0,00)
    c.texto((y, Z_VISTA + 450), RN.novo(PP.rotulo(marca)[1:] + " — ao fundo"), "min", "BOTTOM_CENTER")
    c.interrupcao((y - 300, Z_VISTA), (y + 300, Z_VISTA))
BV, B2E = M(B_VM), M(B_VM) - 120


def secao_vm(yc, zt, so):
    """VM retangular (cortada) com topo em zt; 2º estágio na faixa do lado da borda (oposto a so = lado da laje) até o topo da capa."""
    pts = [(yc - BV / 2, zt - M(H_VIGA)), (yc + BV / 2, zt - M(H_VIGA)), (yc + BV / 2, zt), (yc - BV / 2, zt)]
    c.poli(pts, "CORTADO", fechada=True); c.hachura(pts, "ANSI31", 1.5, "CORTADO")
    ye = yc - so * BV / 2
    e2 = [(ye, zt), (ye + so * B2E, zt), (ye + so * B2E, zt + 260), (ye, zt + 260)]
    c.poli(e2, "OCULTA", fechada=True); c.hachura(e2, "AR-CONC", 0.02)
for n, a in zip(NIVEIS, ASSENTO):
    zt = M(n - H_LAJE - H_CAPA) - 10
    for y, so in ((0, 1), (M(Y2), -1)):
        secao_vm(y, zt, so)
        c.ret(y - BV / 2, M(a) - H_CMEZ, BV, H_CMEZ, "OCULTA")
    y0_, y1_ = paineis_nivel(1)[1][3], paineis_nivel(1)[1][4]
    c.ret(y0_, zt + 10, y1_ - y0_, 200, "VISTA")
    c.hachura([(-BV / 2, zt + 210), (M(Y2) + BV / 2, zt + 210), (M(Y2) + BV / 2, zt + 260), (-BV / 2, zt + 260)], "AR-CONC", 0.02)
    c.ret(-BV / 2, zt + 210, M(Y2) + BV, 50, "VISTA")
    c.chamada((M(2.5), zt + 260), (8, 6), f"piso {NIVS[NIVEIS.index(n)]}: laje h20 + capa 5")
c.chamada((M(Y2), M(ASSENTO[0]) - 200), (-40, -22), f"CP-MEZ 40 × 40 × {H_CMEZ/10:.1f} oculto".replace(".", ","))
c.chamada((0, M(ASSENTO[0]) + 150), (14, -12), f"VM {B_VM*100:.0f} × {H_VIGA*100:.0f} protendida ({fp(PQ['VM-02'][7])} t)")
c.cota_h([0, M(Y2)], -1000, -10)
c.cota_v([-1000, 0, M(ASSENTO[0]), M(NIVEIS[0]), M(ASSENTO[1]), M(NIVEIS[1])], -900, -10, total=False)
def niv(x, z, txt, lado=1):
    c.poli([(x, z), (x + lado * 120, z + 120), (x + lado * 120, z - 120), (x, z)], "COTA")
    c.linha((x + lado * 120, z), (x + lado * 700, z), "COTA")
    c.texto((x + lado * 150, z + 40), txt, "min", "BOTTOM_LEFT" if lado > 0 else "BOTTOM_RIGHT", "COTA")
niv(M(Y2) + 400, 0, "±0,000", 1)
niv(M(Y2) + 400, -1000, "−1,000 fundo do pilar (cálice −1,050, graute 5 cm)", 1)   # rev11
for n, a in zip(NIVEIS, ASSENTO):
    niv(M(Y2) + 400, M(n), f"+{f(n, 2)} topo da capa", 1); niv(M(Y2) + 400, M(a), f"+{f(a)} assento", 1)

# ------------------------------------------------------------------ coluna direita
XC = Q[2] - 200
y = Q[3] - 6
LAJ = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/laje_alveolar.json"))
CMZ = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/cargas_mezanino.json"))
X_JL = 20
pecas = [[m, f"VM retangular {B_VM*100:.0f}×{H_VIGA*100:.0f} protendida, dente {H_DENTE*100:.0f}×{L_DENTE*100:.0f}, L {f(PQ[m][4], 2)} m", str(PQ[m][5]), fp(PQ[m][7]),
          {"VM-04": f"CP-MEZ; P6–P7 só {NIVS[0]}, P6–E só {NIVS[1]}"}.get(m, f"CP-MEZ {NIVS[0]} / {NIVS[1]}")] for m in ("VM-01", "VM-02", "VM-03", "VM-04")]
for mk in sorted(m_ for m_ in PQ if m_.startswith("LA-")):
    pecas.append([mk, PQ[mk][2].replace("laje alveolar ", "LP20 ")[:60], str(PQ[mk][5]), fp(PQ[mk][7]), "topo das VM, apoio 10 cm"])
n_cmz = 2 * sum(len(vigas_nivel(iz)) for iz in (0, 1))
pecas += [["CP-MEZ", f"Consolo 40×40×{H_CMEZ/10:.1f} sem chanfro (pilares das linhas 1–2 e escada)".replace(".", ","), str(n_cmz), "—", "nos pilares (ver pranchas)"],
          ["PM-01", f"Pilar 40×60 do mezanino (B2), L {PQ['PM-01'][4]*100:.0f}", str(PQ["PM-01"][5]), fp(PQ["PM-01"][7]), "cálice −1,00; cabeça até a W 200"],
          ["PM-02", f"Pilar 40×60 do mezanino (D2), L {PQ['PM-02'][4]*100:.0f}", str(PQ["PM-02"][5]), fp(PQ["PM-02"][7]), "cálice −1,00; cabeça até a W 200"]]
for mk, ds in (("PE-01", "P6 da escada 25×40"), ("PE-02", "P7 da escada 40×60"), ("PE-03", "P6 da linha 2 25×40")):
    pecas.append([mk, f"Pilar {ds}, L {PQ[mk][4]*100:.0f}", str(PQ[mk][5]), fp(PQ[mk][7]), "cálice −1,00"])
y = pr.tabela(XC, y, "LISTA DE PEÇAS DE MONTAGEM — MEZANINO", ["MARCA", "DESCRIÇÃO", "QT", "PESO (t)", "APOIO / NÍVEL"], pecas, [18, 92, 10, 18, 62], h_lin=6.0)
seq = [f"Pré-requisitos (ND-LET-MON01): pilares (incluindo P6 e P7 da escada e P6 da linha 2) grauteados há 24 h (graute ≥ 15 MPa); cobertura das linhas 3 a 9 montada; W 200 × 15,0 da linha 2 (com os montantes W 150 × 13,0), VB-01 a VB-04 e terças dos vãos 1–2 e 2–3 AINDA NÃO montadas (sem elas a laje de {f(L_P / 1000, 2)} m não passa entre a VB da linha 1 e a W 200 da linha 2).",
       f"Guindaste dentro do pavilhão no vão 2–3 (entrada pela abertura lateral das vistas E/F, livre até +7,50), afastado da I120 V407 do eixo C: duas posições (perto dos eixos B e D), raio até ~14 m para a linha 1; peça mais pesada VM-02 {fp(PQ['VM-02'][7])} t.",
       f"Piso {NIVS[0]}: VM das linhas 1 e 2 e a VM-04 P6–P7 (sem escoramento): NEO-5F 200×200 no consolo, pino PN-1 no TB-1 do dente (graute numa ponta, graute flexível na outra); soltar do guindaste com a viga calçada no neoprene e conferida no nível.",
       f"CONCRETAR AS PONTAS das VM dos dois lados (junta 3 cm VM × pilar, do recorte do dente ao topo, graute ou concreto fck ≥ 30 MPa, fôrma lateral; ND-LET-VM01 det. 2) e aguardar fcj ≥ {X_JL} MPa (corpo de prova da obra) ANTES de montar as lajes (DEC-039, NBR 9062:2017 11.1).",
       f"Lajes do {NIVS[0]} vão a vão alternando os lados dos PM-01/PM-02 (A–B, B–C, D–E, C–D) para limitar o desequilíbrio nos pilares, içadas só por garra nas 2 pontas ({fp(PQ['LA-01'][7])} t), apoio de 10 cm no topo da VM sobre fita de neoprene 10 × 100; LA-01R junto aos pilares; no vão da escada as LA-03/LA-03R/LA-04 (linha 1 → VM-04); chavetas grauteadas.",
       "Grautear as bainhas BA-1 com as N11 (6 Ø16); limpar e saturar o topo das VM; 2º estágio + capa 5 C30 com tela Q138, N12 e N1, de uma vez, por quem executa a capa; cura úmida 7 dias.",
       f"Piso {NIVS[1]}: VM (as de cima só depois das lajes de baixo — a laje não passa entre as VM do nível superior; VM-04 P6–E da linha 2 só neste nível), pontas concretadas e fcj ≥ {X_JL} MPa, lajes, 2º estágio e capa, igual ao {NIVS[0]}. Carregar só com fck ≥ 20 MPa na capa.",
       f"Escada metálica (ND-LET-ES01): depois da capa do {NIVS[0]} com fck ≥ 20 MPa — vigas de patamar parafusadas nas faces dos pilares P6 e P7 da escada, do P6 da linha 2 e do pilar da linha 2 no eixo E (barras roscadas M16 embutidas), pilaretes com chumbador químico, longarinas e degraus; tudo parafusado.",
       "Estabilidade provisória: pilares das linhas 1–2 engastados nos cálices, sem escoramento nem contraventamento provisório (sem placas, o vento atua só nos pilares, bem abaixo do caso final com as placas); a laje passa a diafragma com a capa ≥ 15 MPa. Vigas e lajes sem escoramento.",
       "Depois: parede G da linha 2, W 200 × 15,0 da linha 2 nos pilares e nos montantes W 150 × 13,0 sobre as VM do +7,30, com presilhas e mãos-francesas (ND-LET-COB05), VB-01 a VB-04 e terças dos vãos 1–2 e 2–3 (ND-LET-MON01)."]
y = pr.notas(XC, y - 4, seq, 200, titulo="SEQUÊNCIA DE MONTAGEM")
c39, c73 = CMZ["piso_390"], CMZ["laje_730"]
n15 = sum(1 for c_ in LAJ["cordoalhas"] if c_["diam"] == "15.2")
notas = ["PENDÊNCIA (decisão em aberto, quadro de decisão anexo ao pacote): VM de borda da linha 1 nos vãos de canto (+3,90 e +7,30) — com os pilares de canto 10 cm para fora, o apoio no CP-MEZ do canto está em decisão; não montar (nem produzir) essas VM, as lajes do vão 1–2 junto aos cantos e os pilares de canto da linha 1 antes da resposta.",
         f"Laje alveolar LP20 (1245 × 200, 6 alvéolos de 15,2 cm) + capa 5 C30 em {f(L_P/1000, 2)} m, vão de cálculo {f((L_P - 100)/1000, 2)} m: {LAJ['n_cord']} Ø12,7 CP-190 RB (2 em cada nervura de borda — confirmar com a fábrica a extrusora), liberação com fckj ≥ {LAJ['fckj']:.0f} MPa; {NIVS[0]}: sobrecarga {f(c39['sobrecarga'], 1)} kN/m² (depósito) + revestimento {f(c39['revestimento'], 1)}; {NIVS[1]}: laje de cobertura do bloco (acesso apenas para manutenção, NBR 6120:2019 Tab. 10): sobrecarga {f(c73['sobrecarga'], 1)} + regularização/impermeabilização {f(c73['revestimento'], 1)} kN/m² (ND-LET-LA01).",
         f"Vigas VM retangulares {B_VM*100:.0f} × {H_VIGA*100:.0f} protendidas (laje apoiada 10 cm no topo, 2º estágio de 18 cm do lado da borda) com dente Gerber {H_DENTE*100:.0f} × {L_DENTE*100:.0f} (NBR 9062:2017 7.4, MEF): assentos +{f(ASSENTO[0])} e +{f(ASSENTO[1])}; fundo da viga e do consolo +{f(ASSENTO[0] - H_CMEZ/1000)} / +{f(ASSENTO[1] - H_CMEZ/1000)}; altura total com laje e capa {H_VIGA*100 + 26:.0f} cm.",
         "Tolerâncias NBR 9062:2017 (5.2.2.6): pilar ±10 mm em planta; nível dos apoios ±10 mm; folga de ponta 30 mm; apoio da laje ≥ 10 cm medido após a montagem.",
         "Níveis em m, cotas em cm. Não medir no desenho."]
pr.notas(XC, y - 4, notas, 200)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-MON02")
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
for a in avisos:
    print(a)
