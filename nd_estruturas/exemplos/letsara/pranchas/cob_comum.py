"""Cobertura metálica Letsara — geometria e marcas comuns às pranchas COB01 e COB02 (mm, x = transversal, y = longitudinal).

Lógica de travamento (padrão das coberturas de referência do escritório):
  - rev05: terças Z 302×90/82×2,30 METSEC contínuas nos 8 vãos por transpasse (METLAP) sobre cada TS-01 (linhas 2–8);
    nas fachadas 1 e 9 apoiam na VB pelo ST-1V; cada peça vence um vão e passa o transpasse do apoio interno;
  - 3 linhas de correntes Ø10 por vão (L/4, L/2, 3L/4), contínuas em cada meia água (13 terças);
  - nas duas pontas de cada meia água (1º espaço de terças): tirantes rígidos L 51×51×3,2 nas 3 linhas e diagonais de
    ancoragem Ø16 do nó da corrente na 2ª terça até o ST-1 da 1ª terça (Λ);
  - rev06 (DEC-024, modelo integrado r05): contraventamento em X Ø16 com esticador nos 5 vãos do pavilhão (4-5 a 8-9),
    painel de 8 espaços de terças (nós nas terças 0, 8 e 15 de cada meia água, painéis de 8 e 7 espaços, diagonal ≈ 45°); as diagonais atravessam as
    terças intermediárias por furos oblongos 18 × 28 (marcas X1..X7 e Y1..Y6); terças dos nós = escoras;
  - ES-2 (orelhas OR-X) só nos 3 nós de cada TS-01 (marca única); no eixo 9 as orelhas ficam na VB (ES-2V);
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
NOS = [round(x * 1000 - 27) for x in LG["nos_contraventamento_x_esq"]]   # rev06: = os 3 nós do X
NOS_D = [n - X0E + X0D for n in NOS]
VAOS_X = tuple(LG["vaos_x"])             # rev05 (DEC-024): índice k do vão (k → eixos k+1 a k+2) com X: 4-5 a 8-9
PAINEL_X = LG["painel_x"]                # espaços de terça por painel do X (8: nós nas terças 0, 8 e 16 de cada meia água)
IDX_NOS = LG["idx_nos_x"]                # rev06: nós do X nas terças 0, 8 e 15 de cada meia água (painéis de 8 e 7 espaços)
NOS_X = [XT[i] for i in IDX_NOS]         # mm, linha da alma
NOS_X_D = [XT[NT + i] for i in IDX_NOS]
ORE_S, ORE_Y = 140, 140                  # orelhas OR-X: s = ±140 do eixo da terça do nó, y = ±140 do eixo da TS-01
ORE_S9 = 200                             # VB do eixo 9: orelha no eixo da VB (y = 0) a s = ±200 (ES-2V fora das ES-1V)
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
IDX_NO_X = set(IDX_NOS) | {NT + i for i in IDX_NOS}                                  # terças dos nós do X (escoras)
IDX_X = set(range(2 * NT)) - IDX_NO_X                                                  # terças atravessadas pelo X (furos oblongos)
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
# rev12 (fresta, opção B): terças da faixa entre os pilares de fachada PF (eixos B a D) apoiam na VB deslocada para fora →
# o vão 1-2 e o 8-9 dessas terças são mais longos. Índices virtuais de vão: 8 = vão 1-2 na faixa PF, 9 = vão 8-9 na faixa PF.
PF_X = tuple(round(x * 1000) for x in PC.get("faixa_pf_x", (9.87, 29.63)))
IDX_PF = {i for i, x in enumerate(XT) if PF_X[0] < x < PF_X[1]} if PC.get("por_vao_faixa_pf") else set()
K_REAL = {k: k for k in range(8)}
DESL_VB = 0
for kv, pp in zip((8, 9), PC.get("por_vao_faixa_pf", [])):
    kr = 0 if kv == 8 else 7
    K_REAL[kv] = kr
    DESL_VB = pp["desloc_vb_mm"]
    VAOS.append(pp["L_vao_mm"]); L_TERCA.append(pp["L_mm"]); EXT.append((pp["ext_ini_mm"], pp["ext_fim_mm"]))
    tk = (pp["L_mm"], EXT[kv])
    j_ = next((BASE_K[q] for q in (8,) if q in BASE_K and (L_TERCA[q], EXT[q][::-1]) == tk), None)
    BASE_K[kv] = j_ or f"T{len(set(BASE_K.values())) + 1}"
# rev12 (opção D): última terça do lado E nos vãos 1-2 / 8-9 encosta no canto deslocado (ST-1FL) → vãos virtuais 10 / 11
IDX_FL = {i for i, x in enumerate(XT) if x > round(PC.get("faixa_pf_x", (0, 1e9))[1] * 1000)} if PC.get("por_vao_canto_fl") else set()
EXT_FL = None
for kv_, pp in zip((10, 11), PC.get("por_vao_canto_fl", [])):
    K_REAL[kv_] = 0 if kv_ == 10 else 7
    VAOS.append(pp["L_vao_mm"]); L_TERCA.append(pp["L_mm"]); EXT.append((pp["ext_ini_mm"], pp["ext_fim_mm"]))
    EXT_FL = pp["ext_ini_mm"] if kv_ == 10 else EXT_FL
    BASE_K[kv_] = f"T{len(set(BASE_K.values())) + 1}"
FURO_FL = PC.get("por_vao_canto_fl", [{}])[0].get("furo_fl_da_ponta_mm", 50) if PC.get("por_vao_canto_fl") else 50
K_TODOS = sorted(K_REAL)


def kv(k, i):
    """vão virtual da terça i no vão k (0..7): 8/9 nas terças da faixa PF dos vãos de fachada."""
    if i in IDX_PF and k in (0, 7) and (8 if k == 0 else 9) in K_REAL:
        return 8 if k == 0 else 9
    if i in IDX_FL and k in (0, 7) and (10 if k == 0 else 11) in K_REAL:
        return 10 if k == 0 else 11
    return k


# rev12 (opção D): só as peças usadas recebem marca, numeradas em ordem (T1, T2…) — com a VB rente à face em toda a fachada
# as peças "de fachada" no eixo da linha deixam de existir
_usadas = []
for _k in range(8):
    for _i in range(2 * NT):
        _q = kv(_k, _i)
        if BASE_K[_q] not in _usadas:
            _usadas.append(BASE_K[_q])
_REN = {b_: f"T{j + 1}" for j, b_ in enumerate(_usadas)}
K_TODOS = [q for q in K_TODOS if BASE_K[q] in _REN]
BASE_K = {q: _REN[b_] for q, b_ in BASE_K.items() if b_ in _REN}


def y_peca(k, i):
    """(ya, yb) mm da peça da terça i no vão k, com a VB deslocada na faixa PF."""
    q = kv(k, i)
    ya = YLmm[k] - EXT[q][0] - (DESL_VB if q == 8 else 0)
    yb = YLmm[k + 1] + EXT[q][1] + (DESL_VB if q == 9 else 0)
    return ya, yb


def furos_ponta(ext):
    """Furos (distância da ponta, mm) de uma ponta de terça: fachada (2 colunas do ST-1V) ou transpasse (ST-1P + emenda)."""
    if EXT_FL is not None and ext == EXT_FL:                    # rev12: ponta no ST-1FL do canto (1 coluna)
        return [FURO_FL]
    if ext == EXT_F:
        return [EXT_F - Y_COL, EXT_F + Y_COL]
    return [B_TR, A_TR - Y_COL, A_TR + Y_COL, 2 * A_TR - B_TR]


def marca(k, i):
    """Marca da terça do vão k (0..7) na linha i: peça-base + furação (D = diagonais, X = cruzamento do X)."""
    suf = ("D" if i in IDX_2A else "") + (sufixo_x(i) if (k in VAOS_X and i in IDX_X) else "")
    return BASE_K[kv(k, i)] + suf


def sufixo_x(i):
    """X1..X7: terças do painel de 8 espaços; Y1..Y6: do painel de 7 (contadas a partir do nó de menor x)."""
    j = i % NT
    return f"X{j}" if j < IDX_NOS[1] else f"Y{j - IDX_NOS[1]}"


def furos_x(k, i):
    """Furos oblongos do X na alma da terça i do vão k: lista de (y do eixo k em mm, z do fundo da terça em mm, diagonal).
    As 2 diagonais de cada painel vão da orelha de um nó (s = ±140, y = +140 da linha k) à do nó seguinte na linha k+1
    (y = −140; na VB do eixo 9, y = 0)."""
    if k not in VAOS_X or i not in IDX_X:
        return []
    meia = NOS_X if i < NT else NOS_X_D
    x = XT[i]
    a, b = next((a, b) for a, b in zip(meia[:-1], meia[1:]) if a < x < b)
    ya = ORE_Y
    sb = ORE_S9 if k == 7 else ORE_S
    out = []
    for nome, x1, x2, z in (("/", a + ORE_S, b - sb, Z_X[0]), ("\\", b - ORE_S, a + sb, Z_X[1])):
        yb = VAOS[k] - (0 if k == 7 else ORE_Y) + (DESL_VB if k == 7 and PF_X[0] < x2 < PF_X[1] else 0)   # rev12: orelha no eixo da VB deslocada
        t = (x - x1) / (x2 - x1)
        out.append((round(ya + t * (yb - ya)), z, nome))
    return out


def lista_marcas():
    q = {}
    for k in range(8):
        for i in range(2 * NT):
            m = marca(k, i)
            q.setdefault(m, dict(L=L_TERCA[kv(k, i)], qt=0, vaos=set(), k=kv(k, i)))
            q[m]["qt"] += 1
            q[m]["vaos"].add(f"{k+1}-{k+2}" + (" (canto E)" if kv(k, i) >= 10 else ""))
    return dict(sorted(q.items()))


def cabecalho(desenho, folha, conteudo, rev="06"):
    return dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                conteudo=conteudo, desenho=desenho, folha=folha, fase="PARA APROVAÇÃO", rev=rev)
