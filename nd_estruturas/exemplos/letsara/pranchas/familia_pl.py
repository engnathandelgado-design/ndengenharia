"""Família de pilares 40×60 laterais e de fachada (PL-01 a PL-12, PF-01 a PF-06) — marcas, consolos e insertos por marca.
Faces de cada pilar: A = interna (consolo da viga principal), C = externa (placas), B e D completam no sentido anti-horário
visto de cima (A → B → C → D). Usado por pilares.py (PL-01) e pilares_familia.py (demais marcas)."""
import json, math, sys
AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
LG = json.load(open(AQ + "ligacoes.json"))
sys.path.insert(0, AQ)
from geometria import X_EIXO
f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
zf = lambda x: LG["Z0_TS"] * 1000 + 0.03 * x
# rev03: TS-01 sem dente, apoiada no recuo (assento) do pilar lateral; CP-VB = fundo da TS-01 na posição (topo da VB = linha das terças)
REC = {"P1": round(LG["REC"][0] * 1000), "P2": round(LG["REC"][1] * 1000)}
# rev04: VB 15×60 com dente 30 — assento HORIZONTAL do CP-VB = nariz do dente (fundo da VB zf + 0,30, recorte 0,30) − neoprene 0,01,
# no centro do neoprene (a 13,5 cm da face do pilar); cada face tem o seu nível (a VB sobe 3 % de A para E)
def VBz(x, sentido):
    meia = 0.30 if x in (0.0, X_EIXO["E"]) else 0.20
    return f((zf((x + sentido * (meia + 0.135)) * 1000) + 590) / 1000, 3)


VB = lambda x: VBz(x, 1 if x == 0.0 else -1)                           # cantos: a VB está do lado de dentro
RV = lambda x: f(math.ceil((zf(x * 1000) / 1000 + 0.90) / 0.05) * 0.05, 2)       # recuo das fachadas = topo da VB (5 cm)
R1, R2 = f(REC["P1"] / 1000, 2), f(REC["P2"] / 1000, 2)
# rev09b (DEC-050): na linha 2 o recuo é o apoio direto da W 310 (fundo da W − 40 mm), sem montante
_L2 = {a["nome"]: a["z_concreto"] for a in json.load(open(AQ + "cob_linha2.json"))["apoios_diretos"]}
R1L2, R2L2 = f(_L2["A"], 3), f(_L2["E"], 3)
XE = X_EIXO["E"]
# rev12b (item 4): face de fixação das placas das paredes internas (G linha 2, C linha 4) pelo registro geometria.PAREDE_INTERNA.
# Eixo A: A = +x, B = +y, C = −x, D = −y; eixo E: A = −x, B = −y, C = +x, D = +y (A → B → C → D anti-horário visto de cima).
from geometria import PAREDE_INTERNA as _PI
FY = lambda lado_e, V: ({1: "D", -1: "B"} if lado_e else {1: "B", -1: "D"})[_PI[V]["lado"]]
MARCAS = [
    ("PL-01", "P1 L5–L8", 4, f"recuo +{R1}", "8 CE-1 (C)"),
    ("PL-09", "P1 L3", 1, f"recuo +{R1}", "2 CE-1 (C, fiadas 6–7)"),
    ("PL-10", "P1 L4", 1, f"recuo +{R1}", f"8 CE-1 (C) + 5 ({FY(False, 'C')}, vista C)"),
    ("PL-02", "P1 L2", 1, f"2 CP-MEZ (A); recuo +{R1L2} (W 200 direto)", f"6 CE-1 (C) + 5 ({FY(False, 'G')}, vista G)"),
    ("PL-03", "P1 L1 canto", 1, f"CP-VB +{VB(0)} (A); 2 CP-MEZ (A); seção cheia até o topo", "6 CE-1 (C) + 6 (D)"),
    ("PL-04", "P1 L9 canto", 1, f"CP-VB +{VB(0)} (A); seção cheia até o topo", "8 CE-1 (C) + 8 (B)"),
    ("PL-05", "P2 L5–L8", 4, f"recuo +{R2}", "8 CE-1 (C)"),
    ("PL-11", "P2 L3", 1, f"recuo +{R2}", "2 CE-1 (C, fiadas 6–7)"),
    ("PL-12", "P2 L4", 1, f"recuo +{R2}", f"8 CE-1 (C) + 6 ({FY(True, 'C')}, vista C)"),
    ("PL-06", "P2 L2", 1, f"1 CP-MEZ só +7,30 (A); recuo +{R2L2} (W 200 direto)", f"6 CE-1 (C) + 6 ({FY(True, 'G')}, vista G)"),
    ("PL-07", "P2 L1 canto", 1, f"CP-VB +{VB(XE)} (A); 2 CP-MEZ (A); seção cheia até o topo; ES-1FL (D)", "6 CE-1 (C) + 6 (B)"),
    ("PL-08", "P2 L9 canto", 1, f"CP-VB +{VB(XE)} (A); seção cheia até o topo; ES-1FL (B)", "8 CE-1 (C) + 8 (D)"),
    ("PF-01", "P3 L1", 1, f"CP-VB +{VBz(9.87, -1)} (B); CP-VB +{VBz(9.87, 1)} (D); 4 CP-MEZ (B, D); recuo +{RV(9.87)}", "6 CE-1 (C)"),
    ("PF-02", "P4 L1", 1, f"CP-VB +{VBz(19.75, -1)} (B); CP-VB +{VBz(19.75, 1)} (D); 4 CP-MEZ (B, D); recuo +{RV(19.75)}", "6 CE-1 (C)"),
    ("PF-03", "P5 L1", 1, f"CP-VB +{VBz(29.63, -1)} (B); CP-VB +{VBz(29.63, 1)} (D); 4 CP-MEZ (B, D); recuo +{RV(29.63)}", "6 CE-1 (C)"),
    ("PF-05", "P3 L9", 1, f"CP-VB +{VBz(9.87, 1)} (B); CP-VB +{VBz(9.87, -1)} (D); recuo +{RV(9.87)}", "8 CE-1 (C)"),
    ("PF-04", "P14 L9", 1, f"CP-VB +{VBz(19.75, 1)} (B); CP-VB +{VBz(19.75, -1)} (D); CP-I120 +{f(LG['Z_ASS_I120'], 3)} (A); recuo +{RV(19.75)}", "8 CE-1 (C)"),
    ("PF-06", "P5 L9", 1, f"CP-VB +{VBz(29.63, 1)} (B); CP-VB +{VBz(29.63, -1)} (D); recuo +{RV(29.63)}", "8 CE-1 (C)"),
]


def marca_de(nome):
    for mk, pos, *_ in MARCAS:
        for tok in pos.replace(" canto", "").split(" e "):
            if "–" in tok:
                p, faixa = tok.split(" ")
                a, b = faixa[1:].split("–")
                if nome.startswith(p + "-L") and int(a) <= int(nome.split("L")[1]) <= int(b.lstrip("L")):
                    return mk
            elif " " in tok:
                p, l = tok.split(" ")[:2]
                if nome == f"{p}-{l}" or nome == p:
                    return mk
            elif nome == tok:
                return mk
    return "?"
