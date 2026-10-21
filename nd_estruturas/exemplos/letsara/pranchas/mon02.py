"""ND-LET-MON02 — planta de montagem do mezanino (níveis +3,15 e +6,55, linhas 1–2): pilares, vigas VM (rev04: meio vaso com dente),
lajes alveolares h20 + capa 5; corte de montagem; lista de peças e sequência. Cotas em cm, níveis em m. A1."""
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha
import pecas_obra as QT                                     # peças = mesma fonte das listas (quantitativos.py)
PQ = {p_[1]: p_ for p_ in QT.pecas}
fp = lambda t_: f"{t_:.1f}".replace(".", ",")

f = lambda v, d=3: f"{v:.{d}f}".replace(".", ",")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
import json
from geometria import Y_LIN, X_EIXO
from lajes_placas import paineis_mez
X_FACH = list(X_EIXO.items())
Y1, Y2 = Y_LIN[0], Y_LIN[1]
LARG = X_EIXO["E"]
NIVEIS = [3.15, 6.55]
VMJ = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/vm_meio_vaso.json"))
VMP = VMJ["premissas"]
H_LAJE, H_CAPA, H_VIGA, H_DENTE = 0.20, 0.05, VMP["h_pm"], VMP["dente"]["hd"]       # rev04: meio vaso com dente; fita de neoprene 1 cm
import pilar_generico as _G
ASSENTO = [z / 1000 for z in _G.Z_MEZ_ASS]
H_CMEZ = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/consolos.json"))["CP-MEZ"]["h_total_m"] * 1000
M = lambda v: v * 1000
PESO_VM = {k: VMJ[k]["secao"]["peso_t"] for k in ("VM-01", "VM-02")}
# VM: face do pilar lateral 30 (60 em x) ou 20 (pilares B, C, D com 40 em x); folga 5 cm de cada lado
FACE = {"A": 0.30, "B": 0.20, "C": 0.20, "D": 0.20, "E": 0.30}
VM = []                                                                    # (marca, xa, xb, L)
for (na, xa), (nb, xb) in zip(X_FACH[:-1], X_FACH[1:]):
    a_, b_ = xa + FACE[na] + 0.03, xb - FACE[nb] - 0.03
    VM.append(("VM-01" if "A" in (na, nb) or "E" in (na, nb) else "VM-02", a_, b_, round(b_ - a_, 2)))
PAINEIS, QT_LAJE, L_P = paineis_mez()
PIL1 = [("PL-03", 0.0, 600, 400), ("PF-01", X_EIXO["B"], 400, 600), ("PF-02", X_EIXO["C"], 400, 600), ("PF-03", X_EIXO["D"], 400, 600), ("PL-07", LARG, 600, 400)]
PIL2 = [("PL-02", 0.0, 600, 400), ("PM-01", X_EIXO["B"], 400, 600), ("PC-01", X_EIXO["C"], 400, 600), ("PM-01", X_EIXO["D"], 400, 600), ("PL-06", LARG, 600, 400)]

pr = Prancha("A1", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="PLANTA DE MONTAGEM DO MEZANINO (+3,15 E +6,55) — VIGAS VM, LAJES ALVEOLARES, CORTE, LISTA DE PEÇAS E SEQUÊNCIA",
                        desenho="ND-LET-MON02", folha="02/03", fase="PARA APROVAÇÃO", rev="04"))
pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL")
pr.revisao("01", "12/10/2026", "GEOMETRIA DO R01; VM-01/VM-02; CONSOLOS SEM CHANFRO; CORTE 2-2 REFEITO")
pr.revisao("04", "16/10/2026", "NBR 9062: VM EM MEIO VASO COM DENTE, 2º ESTÁGIO E CT-1; SEQUÊNCIA SEM ESCORAMENTO")
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
    # vigas VM (meio vaso) nas linhas 1 e 2
    for y in (Y1, Y2):
        for marca, xa, xb, L in VM:
            v.ret(M(xa), M(y) - 200, M(xb - xa), 400, "CORTADO")
            v.texto((M((xa + xb) / 2), M(y) + (-500 if y == Y1 else 500)), f"{marca} (meio vaso, L {f(L, 2)} m)", "min", "TOP_CENTER" if y == Y1 else "BOTTOM_CENTER")
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
v1.marcador_corte((M(12.0), -3000), (M(12.0), M(Y2) + 3000), "M", lado=1)
v2 = planta("PLANTA +6,55", (Q[0] + 40, Q[3] - 357), NIVEIS[1], ASSENTO[1])

# ------------------------------------------------------------------ CORTE 2-2 (1:50) — plano entre B e C, olhando para C
c = pr.vista("CORTE M-M", (Q[0] + 515, Q[3] - 370), 50, titulo="CORTE M-M — MEZANINO (ENTRE OS EIXOS B E C, OLHANDO PARA C)",
             subtitulo="VM-02 meio vaso em corte nas linhas 1 e 2 (alma do lado da borda); laje h20 + capa 5; pilares do eixo C ao fundo", unidade="cm")
c.linha((-1500, 0), (M(Y2) + 1500, 0), "TERRENO")
Z_VISTA = 7600
for y, marca in ((0, "PF-02 (C1) ao fundo"), (M(Y2), "PC-01 (C2) ao fundo")):
    c.ret(y - 300, -1000, 600, 1000 + Z_VISTA, "VISTA")
    c.ret(y - 450, -1000, 900, 1000, "OCULTA")
    c.texto((y, Z_VISTA + 150), marca, "min", "BOTTOM_CENTER")
    c.interrupcao((y - 300, Z_VISTA), (y + 300, Z_VISTA))
def secao_mv(yc, zt, so):
    """Meio vaso (alma 25 do lado da borda so = −1/+1, aba 15 × 20 para dentro) com topo em zt — cortada; 2º estágio por cima."""
    hv, ba, bt = H_VIGA * 1000, VMP["b_alma"] * 1000, (VMP["b_alma"] + VMP["b_aba"]) * 1000
    ye = yc + so * bt / 2                                   # face externa
    yw, yi = ye - so * ba, ye - so * bt
    pts = [(ye, zt - hv), (yw, zt - hv), (yw, zt - 200), (yi, zt - 200), (yi, zt), (ye, zt)]
    c.poli(pts, "CORTADO", fechada=True); c.hachura(pts, "ANSI31", 1.5, "CORTADO")
    e2 = [(ye, zt), (ye - so * (bt - 100), zt), (ye - so * (bt - 100), zt + 210), (ye, zt + 210)]
    c.poli(e2, "OCULTA", fechada=True); c.hachura(e2, "AR-CONC", 0.02)
for n, a in zip(NIVEIS, ASSENTO):
    zt = M(n - H_LAJE - H_CAPA) - 10
    for y, so in ((0, -1), (M(Y2), 1)):
        secao_mv(y, zt, so)
        c.ret(y - 200, M(a) - H_CMEZ, 400, H_CMEZ, "OCULTA")                     # consolo CP-MEZ atrás da VM (fundo alinhado)
    c.ret(100, zt + 10, M(Y2) - 200, 200, "VISTA")                                # laje alveolar (apoio 10 cm na aba)
    c.hachura([(-200, zt + 210), (M(Y2) + 200, zt + 210), (M(Y2) + 200, zt + 260), (-200, zt + 260)], "AR-CONC", 0.02)   # capa
    c.ret(-200, zt + 210, M(Y2) + 400, 50, "VISTA")
    c.chamada((M(5.0), zt + 260), (10, 10), f"nível +{f(n, 2)}: laje h20 + capa 5 (tela Q138)")
c.chamada((M(Y2) - 200, M(ASSENTO[0]) - 200), (-40, -22), f"CP-MEZ {H_CMEZ/10:.0f} cm sem chanfro, oculto atrás da VM (fundos alinhados)")
c.chamada((0, M(ASSENTO[0]) + 150), (14, -12), f"VM-02 meio vaso 40 × {H_VIGA*100:.0f} protendida, {fp(PQ['VM-02'][7])} t, 2 alças")
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
LAJ = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/laje_alveolar.json"))
X_JL = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/vm_meio_vaso.json"))["VM-02"]["torcao_montagem"]["junta"]["fcj_lajes_MPa"]   # DEC-039
pecas = [[m, f"Meio vaso 40×{H_VIGA*100:.0f} protendido, dente {H_DENTE*100:.0f}×35, L {f(PQ[m][4], 2)} m", str(PQ[m][5]), fp(PQ[m][7]), f"CP-MEZ +{f(ASSENTO[0])} / +{f(ASSENTO[1])}"] for m in ("VM-01", "VM-02")]
for mk, ds in (("LA-01", "Laje alveolar LP20 125×945, 7 Ø12,7"), ("LA-01R", "LA-01 c/ recorte 45×20, alv. 2 e 5 cheios"), ("LA-02", "Laje alveolar LP20 70×945, 4 Ø12,7")):
    pecas.append([mk, ds, str(PQ[mk][5]), fp(PQ[mk][7]), "sobre a aba das VM, apoio 10 cm"])
pecas += [["CP-MEZ", f"Consolo 40×35×{H_CMEZ/10:.0f} sem chanfro (pilares das linhas 1–2)", "32", "—", "nos pilares (ver pranchas)"],
          ["PM-01", f"Pilar 40×60 do mezanino (B2, D2), L {PQ['PM-01'][4]*100:.0f}", str(PQ["PM-01"][5]), fp(PQ["PM-01"][7]), "cálice −1,00"]]
y = pr.tabela(XC, y, "LISTA DE PEÇAS DE MONTAGEM — MEZANINO", ["MARCA", "DESCRIÇÃO", "QT", "PESO (t)", "APOIO / NÍVEL"], pecas, [18, 92, 10, 18, 62], h_lin=6.0)
seq = ["Pré-requisitos (ND-LET-MON01): pilares grauteados há 24 h (graute ≥ 15 MPa); cobertura das linhas 3 a 9 montada; TS-01 da linha 2, VB-01 a VB-04 e terças dos vãos 1–2 e 2–3 AINDA NÃO montadas (sem elas a laje de 9,45 m não passa: entre a VB da linha 1 e a TS-01 da linha 2 o vão livre é 9,37 m).",
       "Guindaste dentro do pavilhão no vão 2–3 (entrada pela abertura lateral das vistas E/F, livre até +7,50), afastado da I130 V407 do eixo C: duas posições (perto dos eixos B e D), raio até ~14 m para a linha 1; peça mais pesada VM-02 5,7 t.",
       f"Nível +{f(NIVEIS[0],2)}: VM-01 e VM-02 na linha 1 e depois na linha 2 (sem escoramento): NEO-5 no consolo, pino PN-1 no TB-1 do dente (graute numa ponta, graute flexível na outra); soltar do guindaste com a viga calçada no neoprene e conferida no nível.",
       f"CONCRETAR AS PONTAS das VM dos dois lados (junta 3 cm VM × pilar, do recorte do dente ao topo, graute ou concreto fck ≥ 30 MPa, fôrma lateral; ND-LET-VM01 det. 2) e aguardar fcj ≥ {X_JL} MPa (corpo de prova da obra) ANTES de montar as lajes: a junta é que segura o giro de montagem do meio vaso (DEC-039, NBR 9062:2017 11.1).",
       f"Lajes LA-01/LA-01R/LA-02 do +{f(NIVEIS[0],2)} vão a vão alternando os lados dos PM-01 (A–B, B–C, D–E, C–D) para limitar o desequilíbrio nos pilares, içadas só por garra nas 2 pontas ({fp(PQ['LA-01'][7])} t), apoio de 10 cm na aba sobre fita de neoprene 10 × 50; LA-01R junto aos pilares; chavetas grauteadas.",
       "Grautear as bainhas BA-1 com as N11 (6 Ø16); limpar e saturar o topo das VM; 2º estágio + capa 5 C30 com tela Q138, N12 e N1, de uma vez, por quem executa a capa; cura úmida 7 dias.",
       f"Nível +{f(NIVEIS[1],2)}: VM (as de cima só depois das lajes de baixo — a laje não passa entre as VM do nível superior), pontas concretadas e fcj ≥ {X_JL} MPa, lajes, 2º estágio e capa, igual ao +{f(NIVEIS[0],2)}. Carregar só com fck ≥ 20 MPa na capa.",
       "Estabilidade provisória: pilares das linhas 1–2 engastados nos cálices, sem escoramento nem contraventamento provisório (sem placas, o vento atua só nos pilares, bem abaixo do caso final com as placas); a laje passa a diafragma com a capa ≥ 15 MPa. Vigas e lajes sem escoramento.",
       "Depois: parede G da linha 2, TS-01 da linha 2, VB-01 a VB-04 e terças dos vãos 1–2 e 2–3 (ND-LET-MON01)."]
y = pr.notas(XC, y - 4, seq, 200, titulo="SEQUÊNCIA DE MONTAGEM")
notas = [f"Laje alveolar LP20 (1245 × 200, 6 alvéolos Ø15,2) + capa 5 C30 em {f(L_P/1000, 2)} m, vão de cálculo 9,35 m: 7 Ø12,7 CP-190 RB, uma por nervura, σpi 1450 MPa ({fp(LAJ['cordoalhas'][0]['F_macaco_kN'])} kN por cordoalha), liberação com fckj ≥ {LAJ['fckj']:.0f} MPa; sobrecarga 5,0 kN/m² (escritório) + revestimento 1,0 kN/m² (ND-LET-LA01).",
         f"Vigas VM em meio vaso 40 × {H_VIGA*100:.0f} (alma do lado da borda, aba para dentro, topo = apoio da laje) com dente Gerber {H_DENTE*100:.0f} × 35 (NBR 9062:2017 7.4, MEF): assentos +{f(ASSENTO[0])} e +{f(ASSENTO[1])}; fundo da viga e do consolo +{f(ASSENTO[0] - H_CMEZ/1000 + 0.0)} / +{f(ASSENTO[1] - H_CMEZ/1000)}; altura total com laje e capa {H_VIGA*100 + 26:.0f} cm.",
         "Tolerâncias NBR 9062:2017 (5.2.2.6): pilar ±10 mm em planta; nível dos apoios ±10 mm; folga de ponta 30 mm; apoio da laje ≥ 10 cm medido após a montagem.",
         "Níveis em m, cotas em cm. Não medir no desenho. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(XC, y - 4, notas, 200)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-MON02")
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
for a in avisos:
    if a[0] == "ERRO" or "sobrep" in a[1]:
        print(a)
