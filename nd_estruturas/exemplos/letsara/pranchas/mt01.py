"""ND-LET-MT01 — peças de fixação das placas para a metalúrgica: nicho NC-1 / NC-1' e console CS-1 (rev06c).
Folha 01/02 (A0): os desenhos de fabricação das pranchas PP02 e PP03 (mesma geometria, geo_fixacao) lado a lado, listas de
materiais, quantidades de produção e notas de fabricação. Folha 02/02 (A1): imagens sombreadas (render_pecas.py), plano de
corte por chapa e identificação/embalagem. Cotas em mm. PDF único das 2 folhas."""
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
import json
import math
import re
import fitz
import fechamento as FCH
import geo_fixacao as GF
from prancha_nd import Prancha

f = lambda v, d=2: f"{v:.{d}f}".replace(".", ",")
PP01 = json.load(open("/home/claude/letsara/pranchas/pp01.json"))
NN = PP01["n"]
N_NC, N_E, N_D, N_CS = NN["NC1"], NN["NC1_E"], NN["NC1_D"], NN["CS1"]
RES = 0.05                                                  # reserva de produção (5 %)
DADOS = dict(cliente=FCH.CLIENTE, obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR", fase="PARA PRODUÇÃO", rev="06")


class Proxy:
    """recebe o código de desenho das pranchas A1 e o coloca deslocado na folha A0."""
    def __init__(self, real, dx, dy, pref):
        self.real, self.dx, self.dy, self.pref = real, dx, dy, pref
        self.quadro = (25, 10, 831, 584)

    def vista(self, nome, origem, esc, **kw):
        return self.real.vista(self.pref + nome, (origem[0] + self.dx, origem[1] + self.dy), esc, **kw)

    def __getattr__(self, k):
        return getattr(self.real, k)


def desenhar(arq, proxy):
    src = open(arq, encoding="utf-8").read()
    src = re.sub(r"pr = Prancha\(.*?rev=\"06\"\)\)", "pr = PR", src, flags=re.S)
    src = re.sub(r"pr\.revisao\(.*?\)\n", "", src)
    src = re.sub(r"pr\.cabecalho_peca\(.*?largura=.*?\)\n", "", src, flags=re.S)
    src = src.split("# ================================================================== tabelas")[0]
    ns = dict(PR=proxy, __name__="mt01_exec")
    exec(compile(src, arq, "exec"), ns)
    return ns


# ================================================================== folha 01/02 — desenhos e listas (A0)
pr = Prancha("A0", dict(DADOS, conteudo="PEÇAS DE FIXAÇÃO DAS PLACAS — NICHO NC-1 E CONSOLE CS-1: DESENHOS DE FABRICAÇÃO, LISTAS E QUANTIDADES",
                        desenho="ND-LET-MT01", folha="01/02"))
pr.revisao("06", "18/10/2026", "EMISSÃO PARA PRODUÇÃO NA METALÚRGICA")
Q = pr.quadro
pr.cabecalho_peca("MT", f"NICHO NC-1 ({N_E} + {N_D} NC-1' ESPELHADO = {N_NC} PÇ) · CONSOLE CS-1 ({N_CS} PÇ) — FABRICAÇÃO",
                  "aço A572-50 (parede do nicho e grampos A36) · solda de oficina MIG · galvanizado a fogo · cotas em mm", largura=Q[2] - Q[0] - 10)
DY = 250
desenhar("/home/claude/letsara/pranchas/pp02.py", Proxy(pr, 0, DY, "NC "))
desenhar("/home/claude/letsara/pranchas/pp03.py", Proxy(pr, 585, DY, "CS "))
pr.linha((Q[0] + 588, Q[1] + 300), (Q[0] + 588, Q[3] - 34), "VISTA")
pr.texto(Q[0] + 10, Q[3] - 40, "NICHO NC-1 — embutido na ponta da placa (fábrica de pré-moldados)", "titulo", "TITULO")
pr.texto(Q[0] + 600, Q[3] - 40, "CONSOLE CS-1 — soldado na chapa de espera do pilar na obra", "titulo", "TITULO")

# listas
itn, itc = GF.nc1_itens(), GF.cs1_itens()
kg_n = sum(kg * q for *_, q, kg in itn)
kg_c = sum(kg * q for *_, q, kg in itc)
rn = [[n, nome, dim.replace(".", ","), mat, q, q * N_NC, f(kg * q * N_NC, 1)] for n, nome, dim, mat, q, kg in itn]
rn.append(["", f"total NC-1 ({f(kg_n, 2)} kg/cj)", "", "", "", "", f(kg_n * N_NC, 0)])
y = pr.tabela(Q[0] + 5, Q[1] + 292, f"LISTA DE MATERIAIS — NC-1 / NC-1' ({N_NC} CONJUNTOS)", ["Nº", "DESCRIÇÃO", "DIMENSÃO (mm)", "MATERIAL", "QT/CJ", "QT TOTAL", "kg TOTAL"],
              rn, [9, 46, 60, 30, 13, 18, 20], h_lin=5.2, destaque_ultima=True)
rc = [[n, nome, dim.replace(", sext. interno 8, ponta plana", ", sext. int. 8").replace(".", ","), mat, q, q * N_CS, f(kg * q * N_CS, 1)] for n, nome, dim, mat, q, kg in itc]
rc.append(["", f"total CS-1 ({f(kg_c, 2)} kg/cj)", "", "", "", "", f(kg_c * N_CS, 0)])
pr.tabela(Q[0] + 205 + 5, Q[1] + 292, f"LISTA DE MATERIAIS — CS-1 ({N_CS} CONJUNTOS)", ["Nº", "DESCRIÇÃO", "DIMENSÃO (mm)", "MATERIAL", "QT/CJ", "QT TOTAL", "kg TOTAL"],
          rc, [9, 58, 74, 30, 13, 18, 20], h_lin=5.2, destaque_ultima=True)
qt = [["NC-1", "ponta inicial da placa", N_E, math.ceil(N_E * RES), N_E + math.ceil(N_E * RES), f(kg_n * N_E, 0)],
      ["NC-1'", "ponta final — espelhado (abas e parede do outro lado)", N_D, math.ceil(N_D * RES), N_D + math.ceil(N_D * RES), f(kg_n * N_D, 0)],
      ["CS-1", "console (porcas soldadas; parafusos à parte)", N_CS, math.ceil(N_CS * RES), N_CS + math.ceil(N_CS * RES), f(kg_c * N_CS, 0)]]
y2 = pr.tabela(Q[0] + 440, Q[1] + 292, "QUANTIDADES DE PRODUÇÃO", ["PEÇA", "USO", "OBRA", "RESERVA 5 %", "PRODUZIR", "kg (obra)"], qt, [16, 78, 14, 20, 18, 20], h_lin=5.2)
pr.notas(Q[0] + 440, y2 - 4, [
    "Medidas em mm. Tolerâncias gerais NBR ISO 2768-1 classe m; furos Ø18 ± 0,3; esquadros ± 0,5°; NC-1: vão interno teto–base 178 ± 1 e profundidade 47,5 ± 1 (gabarito).",
    "Corte a laser ou plasma de alta definição; sem rebarbas; quebrar cantos vivos 1 mm. Chapas A572-50 (parede do NC-1 e grampos em A36).",
    "Solda de oficina GMAW (MIG) ER70S-6 com Ar + 20 % CO₂, soldador qualificado (AWS D1.1), soldas contínuas e inspeção visual 100 %. Sequência e símbolos nas vistas.",
    "Montar cada lote no gabarito; conferir 1 CS-1 encaixado em 1 NC-1 por lote (encaixe dos dentes nas abas e altura do M16 de nível).",
    "Galvanização a fogo após a solda (NBR 6323, ≥ 85 µm); repassar as roscas das porcas soldadas depois da galvanização.",
    "Identificar cada peça com a marca (NC-1, NC-1', CS-1) em punção ou etiqueta metálica; embalar em lotes de 20 por marca.",
    "Parafusos de nível (16), contraporcas (17) e prisioneiros (18): fornecimento em kit por console, galvanizados (prisioneiro zincado).",
    "PROJETO DA ND ENGENHARIA."], 300)
av1 = pr.salvar("/home/claude/letsara/pranchas/ND-LET-MT01-1")
print("MT01-1", len([a for a in av1 if a[0] == "ERRO"]), "erros,", len(av1), "avisos", [a for a in av1 if a[0] == "ERRO" or "sobrep" in a[1] or "sai" in a[1]][:20])

# ================================================================== folha 02/02 — imagens e plano de corte (A1)
p2 = Prancha("A1", dict(DADOS, conteudo="PEÇAS DE FIXAÇÃO DAS PLACAS — IMAGENS DAS PEÇAS E PLANO DE CORTE", desenho="ND-LET-MT01", folha="02/02"))
p2.revisao("06", "18/10/2026", "EMISSÃO PARA PRODUÇÃO NA METALÚRGICA")
Q2 = p2.quadro
p2.cabecalho_peca("MT", "IMAGENS DAS PEÇAS (REFERÊNCIA VISUAL) E PLANO DE CORTE", "as cotas valem pela folha 01/02", largura=Q2[2] - Q2[0] - 270)
IM = [("cs1_montado.png", "CS-1 montado"), ("cs1_explodido.png", "CS-1 explodido"), ("conjunto.png", "CS-1 no NC-1 (posição final)"),
      ("nc1_montado.png", "NC-1 montado"), ("nc1_explodido.png", "NC-1 explodido")]
W_IM, H_IM = 170, 142
quadros = []
for k, (arq, tit) in enumerate(IM):
    cx = Q2[0] + 8 + (k % 3) * (W_IM + 8)
    cy = Q2[3] - 40 - (k // 3 + 1) * (H_IM + 8)
    p2.imagem(cx, cy + 16, cx + W_IM, cy + H_IM, "/home/claude/letsara/pranchas/img/" + arq, titulo=tit)   # rev08: pelo motor (entra no PDF da folha)
    quadros.append((arq, cx, cy))
# plano de corte (chapas por espessura)
corte = {}
for itens, n_obra in ((itn, N_NC), (itc, N_CS)):
    for n, nome, dim, mat, q, kg in itens:
        if "CH" in dim:
            esp = dim.split("CH")[1].split("×")[0].strip()
            corte.setdefault((esp, mat), []).append((n, nome, dim, q * math.ceil(n_obra * (1 + RES)), kg * q * math.ceil(n_obra * (1 + RES))))
lin = []
for (esp, mat), v in sorted(corte.items(), key=lambda t: float(t[0][0].replace(",", "."))):
    for n, nome, dim, q, kg in v:
        lin.append([f"CH {esp}".replace(".", ","), mat, n, nome, dim.replace(".", ","), q, f(kg, 1)])
y = p2.tabela(Q2[2] - 250, Q2[3] - 6, "PLANO DE CORTE — PEÇAS PLANAS (OBRA + 5 %)", ["CHAPA", "MATERIAL", "Nº", "PEÇA", "DIMENSÃO", "QT", "kg"],
              lin, [20, 30, 9, 50, 78, 14, 20], h_lin=5.2)
kg_esp = {}
for (esp, mat), v in corte.items():
    kg_esp[(esp, mat)] = kg_esp.get((esp, mat), 0) + sum(t[4] for t in v)
y = p2.tabela(Q2[2] - 250, y - 6, "RESUMO POR CHAPA (sem perda de corte)", ["CHAPA", "MATERIAL", "kg"],
              [[f"CH {e}".replace(".", ","), m, f(k, 0)] for (e, m), k in sorted(kg_esp.items(), key=lambda t: float(t[0][0].replace(",", ".")))], [30, 60, 30], h_lin=5.2)
p2.notas(Q2[2] - 250, y - 6, [
    "Imagens só como referência visual da montagem das peças; dimensões, soldas e tolerâncias pela folha 01/02.",
    "Grampos U do NC-1 (itens 7 e 8): redondo Ø6,3 A36 dobrado a frio, raio interno 10.",
    "PROJETO DA ND ENGENHARIA."], 245)
av2 = p2.salvar("/home/claude/letsara/pranchas/ND-LET-MT01-2")
print("MT01-2", len([a for a in av2 if a[0] == "ERRO"]), "erros,", len(av2), "avisos", [a for a in av2 if a[0] == "ERRO" or "sobrep" in a[1]][:10])

# rev08 (22/10/2026): as imagens entram pelo motor (Prancha.imagem) no próprio ND-LET-MT01-2.pdf. Antes eram coladas
# só no PDF de entrega da metalúrgica (ND-LET-MT01-rev06.pdf) e o PDF único das pranchas pegava a folha sem imagens.
d2 = fitz.open("/home/claude/letsara/pranchas/ND-LET-MT01-2.pdf")
out = fitz.open()
out.insert_pdf(fitz.open("/home/claude/letsara/pranchas/ND-LET-MT01-1.pdf"))
out.insert_pdf(d2)
out.save("/home/claude/letsara/entregas/ND-LET-MT01-rev06.pdf", deflate=True)
print("ok")
