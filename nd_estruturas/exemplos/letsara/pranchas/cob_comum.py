"""Cobertura metálica Letsara — geometria e marcas comuns às pranchas COB01 e COB02 (mm, x = transversal, y = longitudinal).

Lógica de travamento (padrão das coberturas de referência do escritório):
  - rev05: terças Z 302×90/82×2,30 METSEC contínuas nos 8 vãos por transpasse (METLAP) sobre cada TS-01 (linhas 2–8);
    nas fachadas 1 e 9 apoiam na VB pelo ST-1V; cada peça vence um vão e passa o transpasse do apoio interno;
  - 3 linhas de correntes Ø10 por vão (L/4, L/2, 3L/4), contínuas em cada meia água (13 terças);
  - nas duas pontas de cada meia água (1º espaço de terças): tirantes rígidos L 51×51×3,2 nas 3 linhas e diagonais de
    ancoragem Ø16 do nó da corrente na 2ª terça até o ST-1 da 1ª terça (Λ);
  - contraventamento em X Ø16 com esticador de nó a nó das vigas (CH-T2), abrangendo 2 espaços de terças, só nos vãos
    2–3 e 7–8 (vizinhos aos oitões; rev. 03 — modelo global R01: X dos vãos 4–5 e 5–6 sem função, esforço no X 7,1 kN com
    2 ou 4 vãos); as terças dos nós são os montantes (escoras);
  - CH-T2 mantida em todas as TS-01 (marca única, mesma fôrma e insertos); orelhas sem uso nas linhas 4 a 6;
  - sem mão-francesa (rev05): apoio com 4 M12 8.8 na alma (ST-1P / ST-1V) resiste à torção de apoio.
"""
import json
import sys
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from geometria import Y_LIN, X_EIXO

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
LG = json.load(open(AQ + "ligacoes.json"))
CB = json.load(open(AQ + "cobertura_metalica.json"))
f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")

YL = Y_LIN
YLmm = [round(y * 1000) for y in YL]
VAOS = [YLmm[i + 1] - YLmm[i] for i in range(8)]
X_C, X_E = round(X_EIXO["C"] * 1000), round(X_EIXO["E"] * 1000)
LTS = round(LG["L_TS"] * 1000 * (1 / (1 + 0.03 ** 2)) ** 0.5)          # projeção horizontal da TS-01
X0E = round(LG["X_PONTA_ESQ"] * 1000); X0D = X_E - X0E - LTS            # pontas das vigas TS-01 (esq / dir) — rev03 sem dentes
ST = LG["s_tercas"]
XT = [round(X0E + s * 1000 - 27) for s in ST] + [round(X0D + s * 1000 - 27) for s in ST]   # linhas de terças (2 meias águas)
NT = len(ST)                             # terças por meia água (17 na rev03, passo ~1,20 m)
PASSO = round(LG["passo_tercas"] * 1000)
NOS = [round(x * 1000 - 27) for x in LG["nos_contraventamento_x_esq"]]
NOS_D = [n - X0E + X0D for n in NOS]
VAOS_X = (1, 6)                          # índice k do vão (k → eixos k+1 a k+2) com contraventamento em X: 2-3 e 7-8
PC = CB["pecas"]                         # rev05: peças METLAP (cobertura_metalica.json)
A_TR = PC["transpasse_cada_lado_mm"]     # transpasse: cada terça passa A_TR além do eixo do apoio interno (total 2·A_TR)
EXT_F = PC["extensao_fachada_mm"]        # nas fachadas (VB) a terça passa EXT_F além do eixo
B_TR = PC["furos_transpasse_da_ponta_mm"]   # furos do transpasse a B_TR da ponta
Y_COL = 60                               # colunas de furos do ST-1P / ST-1V a ±60 do eixo do apoio
Z_FURO = tuple(PC["furos_z_mm"])         # furos de fixação na alma: F = 52 da base e 302 − E = 247 (METSEC)
Z_COR = PC["furo_corrente_z_mm"]         # corrente Ø10 (rosca M10, furo Ø12) no meio da alma
Z_DIAG = 245                             # diagonal de ancoragem: furo Ø18 na alma da 2ª terça (245 do fundo) e no ST-1 (255 do concreto, no eixo)
Z_X = (35, 75)                           # cruzamento do X: furos Ø18 na alma da terça intermediária (do fundo da terça)
H_TERCA, B_TERCA, B_INF, D_SUP, D_INF, T_Z = 302, 90, 82, 19, 21, 2.30
PESO_UE = 8.92                           # kg/m (catálogo METSEC 302Z23)
PERFIL_TXT = "Z 302×90/82×2,30 METSEC (302Z23, fy 400, Z275)"
FOLGA = 0                                # sem folga ponta a ponta (rev05: transpasse)
IDX_PONTA = {0, NT - 1, NT, 2 * NT - 1}                 # 1ª terça de cada ponta de meia água
IDX_2A = {1, NT - 2, NT + 1, 2 * NT - 2}                 # 2ª terça (recebe as diagonais de ancoragem)
IDX_X = set(range(1, NT - 1, 2)) | set(range(NT + 1, 2 * NT - 1, 2))   # intermediárias dos painéis do X (cruzamento)
L_TERCA = [p["L_mm"] for p in PC["por_vao"]]
EXT = [(p["ext_ini_mm"], p["ext_fim_mm"]) for p in PC["por_vao"]]
# peça-base por (comprimento, extensões): vão de fachada 1-2 e 8-9 têm uma ponta curta (EXT_F); os internos, transpasse nas 2
_tipos = []
for k in range(8):
    tk = (L_TERCA[k], EXT[k])
    if tk not in _tipos and (L_TERCA[k], EXT[k][::-1]) not in _tipos:
        _tipos.append(tk)
BASE_K = {}
for k in range(8):
    tk = (L_TERCA[k], EXT[k])
    j = _tipos.index(tk) if tk in _tipos else _tipos.index((L_TERCA[k], EXT[k][::-1]))
    BASE_K[k] = f"T{j+1}"
BASE = {L_TERCA[k]: BASE_K[k] for k in range(8)}          # compatível com o uso por comprimento


def furos_ponta(ext):
    """Furos (distância da ponta, mm) de uma ponta de terça: fachada (2 colunas do ST-1V) ou transpasse (ST-1P + emenda)."""
    if ext == EXT_F:
        return [EXT_F - Y_COL, EXT_F + Y_COL]
    return [B_TR, A_TR - Y_COL, A_TR + Y_COL, 2 * A_TR - B_TR]


def marca(k, i):
    """Marca da terça do vão k (0..7) na linha i: peça-base + furação (D = diagonais, X = cruzamento do X)."""
    suf = ("D" if i in IDX_2A else "") + ("X" if (k in VAOS_X and i in IDX_X) else "")
    return BASE_K[k] + suf


def lista_marcas():
    q = {}
    for k in range(8):
        for i in range(2 * NT):
            m = marca(k, i)
            q.setdefault(m, dict(L=L_TERCA[k], qt=0, vaos=set()))
            q[m]["qt"] += 1
            q[m]["vaos"].add(f"{k+1}-{k+2}")
    return dict(sorted(q.items()))


def cabecalho(desenho, folha, conteudo, rev="05"):
    return dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                conteudo=conteudo, desenho=desenho, folha=folha, fase="PARA APROVAÇÃO", rev=rev)
