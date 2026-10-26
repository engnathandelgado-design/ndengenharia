"""ND-LET-EX01 — EXECUÇÃO EM OBRA: CAPEAMENTO, CHAVETEAMENTO E 2º ESTÁGIO DAS VIGAS (rev11/rev12).
Folha para a fábrica enviar ao cliente/construtora que executa essa parte. Linguagem para quem executa; sem notas internas da ND.
Dados lidos do mesmo registro do cálculo: vm_retangular.json (negativa N11/N12 por apoio), nomes.json (VM e pilares por apoio),
laje_alveolar.json (painéis, capa, tela), cargas_mezanino.json. Também sai em PDF avulso (ND-LET-EX01-rev11.pdf)."""
import json, math, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
PR = "/home/claude/letsara/pranchas/"
VM = json.load(open(AQ + "vm_retangular.json", encoding="utf-8"))
PRM = VM["premissas"]
CM = json.load(open(AQ + "cargas_mezanino.json", encoding="utf-8"))
NM = json.load(open(PR + "nomes.json", encoding="utf-8"))["pecas"]
f1 = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
kgm = lambda d: math.pi * (d / 1000) ** 2 / 4 * 7850

# ------------------------------------------------------------------ apoios internos: registro único (negativa_vm.py ← vm_retangular.json)
import negativa_vm as NV
ap = NV.apoios()
N11 = max((a["N11"] for a in ap), key=lambda d: d["n"] * d["d"] ** 2)          # típico (detalhe 3); a tabela traz cada apoio
N12 = max((a["N12"] for a in ap), key=lambda d: d["n"] * d["d"] ** 2)
pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="EXECUÇÃO EM OBRA — CAPEAMENTO, CHAVETEAMENTO E 2º ESTÁGIO DAS VIGAS DO MEZANINO (+3,90 E +7,30)",
                        desenho="ND-LET-EX01", folha="01/01", fase="PARA EXECUÇÃO EM OBRA"))
pr.revisao("00", "26/10/2026", "EMISSÃO INICIAL — FOLHA PARA A CONSTRUTORA (EXECUÇÃO DA CAPA E DO 2º ESTÁGIO)")
pr.revisao("R12", "26/10/2026", "PLANTA-CHAVE DOS APOIOS; PILARES CORRIGIDOS; ETAPAS EM 1:20; CHAVETA EM CM")
Q = pr.quadro
pr.texto(Q[0] + 8, Q[3] - 16, "EXECUÇÃO EM OBRA — CAPA, CHAVETAS E 2º ESTÁGIO DAS VIGAS", "grande", "TITULO")
pr.texto(Q[0] + 8, Q[3] - 26, "Para quem executa na obra. A fábrica entrega as peças montadas; a construtora executa os itens abaixo, nesta ordem.", "nota", "TEXTO")

# ------------------------------------------------------------------ croqui de base (corte transversal da VM com as lajes)
def base(v, etapa):
    B, H = 300, 750
    v.ret(-B / 2, 0, B, H, "VISTA")                                                     # VM pré-moldada
    for sg in (-1, 1):
        x0 = sg * (B / 2 - 100)                                                          # laje apoiada 10 cm
        v.ret(min(x0, x0 + sg * 900), H + 10, 900, 200, "VISTA")
        v.chapa(sg * (B / 2 - 50) - 25, H, 50, 10)                                        # neoprene em fita
    cor = {1: "VISTA", 2: "VISTA"}
    if etapa >= 3:                                                                       # chavetas
        for sg in (-1, 1):
            v.ret(sg * 1000 - 20, H + 10, 40, 200, "ARMADURA")
    if etapa >= 4:                                                                       # 2º estágio + negativas
        v.ret(-B / 2 + 100, H + 10, B - 200, 200, "OCULTA")
        for xx in (-60, 0, 60):
            v.circulo((xx, H + 230), 8, "ARMADURA")
    if etapa >= 5:                                                                       # tela Q138 + capa
        v.linha((-1100, H + 235), (1100, H + 235), "ARMADURA")
    if etapa >= 6:
        v.ret(-1100, H + 210, 2200, 50, "CORTADO")
    v.texto((0, -60), ["", "1 conferir montagem", "2 limpar e umedecer", "3 grautear chavetas", "4 bainhas e negativas", "5 tela Q138", "6 concretar capa + 2º est."][etapa], "nota", "TOP_CENTER")


for k in range(1, 7):                                                    # rev12: etapas em 1:20 (antes miniaturas 1:30)
    v = pr.vista(f"E{k}", (Q[0] + 66 + (k - 1) * 112, Q[3] - 125), 20, titulo=f"ETAPA {k}", subtitulo="corte sobre a VM", unidade="cm")
    base(v, k)

# ------------------------------------------------------------------ detalhes ampliados
d1 = pr.vista("D1", (Q[0] + 110, Q[3] - 330), 5, titulo="DETALHE 1 — CHAVETA ENTRE PAINÉIS", subtitulo="graute ≥ 30 MPa não retrátil, antes da capa", unidade="cm")
for sg in (-1, 1):
    d1.poli([(sg * 10, 0), (sg * 10, 60), (sg * 30, 90), (sg * 30, 140), (sg * 10, 170), (sg * 10, 200), (sg * 300, 200), (sg * 300, 0)], "VISTA", True)
d1.hachura([(-10, 0), (10, 0), (10, 60), (30, 90), (30, 140), (10, 170), (10, 200), (-10, 200), (-10, 170), (-30, 140), (-30, 90), (-10, 60)], "AR-CONC", 0.02)
d1.cota_v([0, 200], 300, 8); d1.cota_h([-10, 10], 0, -12, total=False)
d1.chamada((0, 120), (6, 30), "graute ≥ 30 MPa (chaveta cheia)")
d2 = pr.vista("D2", (Q[0] + 400, Q[3] - 360), 10, titulo="DETALHE 2 — PAINEL × VM COM 2º ESTÁGIO", subtitulo="apoio 10 cm; fita de neoprene; folga 3 cm", unidade="cm")
d2.ret(-150, 0, 300, 750, "VISTA"); d2.chapa(-150, 750, 100, 10); d2.chapa(50, 750, 100, 10)
d2.ret(-1000, 760, 950, 200, "VISTA"); d2.ret(50, 760, 950, 200, "VISTA")
d2.ret(-50, 760, 100, 200, "OCULTA")
d2.ret(-1000, 960, 2000, 50, "CORTADO"); d2.hachura([(-1000, 960), (1000, 960), (1000, 1010), (-1000, 1010)], "AR-CONC", 0.03)
for xx in (-30, 30):
    d2.linha((xx, 600), (xx, 980), "ARMADURA")
d2.cota_v([0, 750, 960, 1010], 1000, 10, total=False)
d2.chamada((0, 860), (20, 16), f"2º estágio C{PRM['fck_2estagio']:g} com a capa (largura {PRM['faixa_2e']*100:g} cm)")
d2.chamada((-30, 700), (-24, -10), "alças/estribos da VM saindo para o 2º estágio")
d2.chamada((-100, 755), (-18, 14), "fita de neoprene 10 mm")
d3 = pr.vista("D3", (Q[0] + 220, Q[3] - 600), 25, titulo="DETALHE 3 — VM SOBRE O PILAR (CONTINUIDADE)", subtitulo="N11 nas bainhas do pilar + N12 na capa", unidade="cm")
d3.ret(-200, -900, 400, 2000, "VISTA")
d3.ret(-1400, 0, 1150, 750, "VISTA"); d3.ret(250, 0, 1150, 750, "VISTA")
for z in (450, 560):
    d3.ret(-200, z - 25, 400, 50, "OCULTA")
    d3.linha((-1500, z), (1500, z), "ARMADURA")
d3.linha((-1500, 980), (1500, 980), "ARMADURA")
d3.ret(-1400, 960, 2800, 50, "CORTADO")
d3.cota_h([-3000, 0, 3000], 1100, 18, total=True)
d3.chamada((-1000, 450), (-4, -46), f"N11: {N11['n']} Ø{f1(N11['d'], 0)} L {N11['L']*100:g} em 2 bainhas Ø50 grauteadas (3 + 3)")
d3.chamada((1000, 980), (4, 30), f"N12: {N12['n']} Ø{f1(N12['d'])} L {N12['L']*100:g} na capa (faixa ≤ 1,5 × largura do pilar)")
d4 = pr.vista("D4", (Q[0] + 470, Q[3] - 640), 10, titulo="DETALHE 4 — BORDA DA LAJE COM FÔRMA", subtitulo="fôrma de borda por quem faz a capa", unidade="cm")
d4.ret(0, 0, 900, 200, "VISTA"); d4.ret(0, 200, 900, 50, "CORTADO"); d4.ret(900, -50, 20, 330, "METALICA")
d4.chamada((910, 150), (12, 10), "fôrma de borda (madeira ou metálica), travada")
d4.chamada((450, 0), (-10, -14), "alvéolos fechados na ponta (tampa de fábrica)")

# ------------------------------------------------------------------ rev12: PLANTA-CHAVE dos apoios de continuidade (VM sobre pilar)
import renomear as RN
from geometria import X_EIXO, Y_LIN
kp = pr.vista("KP", (Q[0] + 700, Q[1] + 150), 200, titulo="PLANTA-CHAVE — APOIOS DE CONTINUIDADE DAS VM (+3,90 E +7,30)",
              subtitulo="círculo = apoio com N11 nas bainhas do pilar e N12 na capa (tabela ao lado); linha 1 embaixo", unidade="cm")
for vg in [q for q in NM if q.get("tipo") == "viga" and str(q.get("marca", "")).startswith("VM") and q.get("nivel") == "+3,90"]:
    x0, x1, y0_ = vg["x0"] * 1000, vg["x1"] * 1000, vg["y0"] * 1000
    kp.ret(min(x0, x1) + 200, y0_ - 150, abs(x1 - x0) - 400, 300, "VISTA")
    kp.texto(((x0 + x1) / 2, y0_ + (450 if y0_ < 5000 else -450)), RN.N(vg["nome"]) + " / " + RN.N(next((q["nome"] for q in NM if q.get("tipo") == "viga" and q.get("nivel") == "+7,30"
             and abs(q["x0"] - vg["x0"]) < 0.01 and abs(q["y0"] - vg["y0"]) < 0.01), "")), "min", "BOTTOM_CENTER" if y0_ < 5000 else "TOP_CENTER")
for x in (0.0, X_EIXO["B"], X_EIXO["C"], X_EIXO["D"], X_EIXO["E"]):
    for y in (Y_LIN[0], Y_LIN[1]):
        kp.ret(x * 1000 - 200, y * 1000 - 200, 400, 400, "CORTADO")
_vis = {}
for a in ap:
    _vis.setdefault((a["nome_pilar"], round(a["x"], 3), round(a["y"], 3)), []).append(a["niv"])
for (nm_, x_, y_), nivs in _vis.items():
    kp.circulo((x_ * 1000, y_ * 1000), 700, "INDICACAO")
    kp.texto((x_ * 1000, y_ * 1000 + (-900 if y_ < 5 else 900)), RN.N(nm_ + ("" if len(nivs) > 1 else f" ({nivs[0]})")), "nota", "TOP_CENTER" if y_ < 5 else "BOTTOM_CENTER")
for lb, x in (("A", 0.0), ("B", X_EIXO["B"]), ("C", X_EIXO["C"]), ("D", X_EIXO["D"]), ("E", X_EIXO["E"])):
    kp.eixo((x * 1000, -1800), (x * 1000, Y_LIN[1] * 1000 + 1800), 0); kp.texto((x * 1000, -2300), lb, "nota", "TOP_CENTER")
for lb, y in (("1", Y_LIN[0]), ("2", Y_LIN[1])):
    kp.eixo((-1800, y * 1000), (X_EIXO["E"] * 1000 + 1800, y * 1000), 0); kp.texto((-2300, y * 1000), lb, "nota", "MIDDLE_RIGHT")

# ------------------------------------------------------------------ tabelas
lin = [[a["niv"], a["pilar"], a["esq"], a["dir"], NV.txt(a["N11"]), NV.txt(a["N12"]), "2 bainhas Ø50"] for a in ap]
y = pr.tabela(Q[0] + 690, Q[3] - 40, "ARMADURA DE CONTINUIDADE POR APOIO (VM sobre pilar)", ["NÍVEL", "PILAR", "VM ESQ.", "VM DIR.", "N11 (bainhas)", "N12 (capa)", "GRAUTE"], lin, [18, 18, 20, 20, 36, 36, 30], h_lin=6.4)
nap = len(ap)
kg11 = sum(a["N11"]["n"] * a["N11"]["L"] * kgm(a["N11"]["d"]) for a in ap); kg12 = sum(a["N12"]["n"] * a["N12"]["L"] * kgm(a["N12"]["d"]) for a in ap)
mat = [[f"N11 Ø{N11['d']:g} CA-50 L {N11['L']*100:g}", f"{sum(a['N11']['n'] for a in ap)} barras", f"{f1(kg11 * 1.1, 0)} kg (+10 %)"],
       [f"N12 Ø{N12['d']:g} CA-50 L {N12['L']*100:g}".replace(".", ","), f"{sum(a['N12']['n'] for a in ap)} barras", f"{f1(kg12 * 1.1, 0)} kg (+10 %)"],
       ["tela Q138 (capa)", "área dos dois níveis", "conforme planta da LA01"],
       ["graute ≥ 30 MPa não retrátil", f"{2 * nap} bainhas + chavetas", "chavetas: ≈ 1,2 L/m"],
       [f"concreto C{PRM['fck_2estagio']:g} (capa 5 cm + 2º estágio)", "por nível", "ver quantitativos"]]
y = pr.tabela(Q[0] + 690, y - 8, "MATERIAIS DE OBRA", ["ITEM", "QUANTIDADE", "OBS."], mat, [70, 50, 58], h_lin=5.6)
esp = [["concreto da capa e 2º estágio", f"C{PRM['fck_2estagio']:g}, abatimento 10 ± 2 cm, brita 1 (máx. 19 mm)"],
       ["graute", "≥ 30 MPa, não retrátil, fluido"], ["aço", "CA-50 (NBR 7480); tela Q138"], ["cobrimento", "2,5 cm na capa; 3,0 cm no 2º estágio"],
       ["cura", "úmida 7 dias; carregar só com fck ≥ 20 MPa"], ["carga de montagem", f"até {f1(1.0, 1)} kN/m² sem escoramento (concreto fresco + pessoas)"],
       ["sobrecarga final", f"+3,90: {f1(CM['piso_390']['sobrecarga'], 1)} kN/m²; +7,30: {f1(CM['laje_730']['sobrecarga'], 1)} kN/m² (laje de cobertura)"]]
y = pr.tabela(Q[0] + 690, y - 8, "ESPECIFICAÇÕES", ["ITEM", "VALOR"], esp, [60, 118], h_lin=5.6)
pr.notas(Q[0] + 690, y - 8, [
    "Escopo da fábrica: pilares, vigas VM, lajes alveolares montadas, com as pontas das VM concretadas antes das lajes. Escopo da obra: graute das chavetas e das bainhas, armadura de obra (N11, N12, negativa da laje e tela), 2º estágio, capa, fôrma de borda e cura.",
    "Sequência: (1) conferir a montagem (apoio de 10 cm das lajes, neoprene em fita, folgas); (2) limpar e umedecer as superfícies (face rugosa da VM e da laje, NBR 9062 6.3); (3) grautear as chavetas entre painéis; (4) passar as N11 nas bainhas dos pilares e grautear; posicionar as N12 e a negativa da laje; (5) tela Q138 com espaçadores; fechar alvéolos e bordas; (6) concretar o 2º estágio e a capa juntos; (7) curar 7 dias; (8) liberar a carga com fck ≥ 20 MPa.",
    f"Bainhas Ø50 com 3 Ø{N11['d']:g} cada: barras ocupam {f1(3 * math.pi * N11['d'] ** 2 / 4 / (math.pi * 50 ** 2 / 4) * 100, 0)} % da seção da bainha (≤ 40 %); grautear por baixo com graute fluido até sair pelo respiro de cima.",
    "Antes de concretar, conferir: chavetas cheias; bainhas grauteadas com as barras centradas; N12 e tela no lugar com cobrimento; fôrma de borda travada; superfície limpa e úmida (sem água empoçada).",
    "NÃO FAZER: furar a laje sem consultar a engenharia; cortar cordoalha; apoiar carga concentrada (paletes, máquinas) antes da cura; concretar a capa sem grautear chavetas e bainhas."], 178)
av = pr.salvar(PR + "ND-LET-EX01")
print("ND-LET-EX01", len([a for a in av if a[0] == "ERRO"]), "erros,", len(av), "avisos")
for a in av:
    print("  ", a)
