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
VB = lambda x: f(zf(x * 1000) / 1000, 3)
RV = lambda x: f(math.ceil((zf(x * 1000) / 1000 + 0.90) / 0.05) * 0.05, 2)       # recuo das fachadas = topo da VB (5 cm)
R1, R2 = f(REC["P1"] / 1000, 2), f(REC["P2"] / 1000, 2)
XE = X_EIXO["E"]
MARCAS = [
    ("PL-01", "P1 L5–L8", 4, f"recuo +{R1}", "8 IP-01 (C)"),
    ("PL-09", "P1 L3", 1, f"recuo +{R1}", "2 IP-01 (C, fiadas 6–7)"),
    ("PL-10", "P1 L4", 1, f"recuo +{R1}", "8 IP-01 (C) + 5 (B, vista C)"),
    ("PL-02", "P1 L2", 1, f"2 CP-MEZ (A); recuo +{R1}", "6 IP-01 (C) + 5 (B, vista G)"),
    ("PL-03", "P1 L1 canto", 1, f"CP-VB +{VB(0)} (A); 2 CP-MEZ (A); recuo A e B", "6 IP-01 (C) + 6 (D)"),
    ("PL-04", "P1 L9 canto", 1, f"CP-VB +{VB(0)} (A); recuo A e D", "8 IP-01 (C) + 8 (B)"),
    ("PL-05", "P2 L5–L8", 4, f"recuo +{R2}", "8 IP-01 (C)"),
    ("PL-11", "P2 L3", 1, f"recuo +{R2}", "2 IP-01 (C, fiadas 6–7)"),
    ("PL-12", "P2 L4", 1, f"recuo +{R2}", "8 IP-01 (C) + 6 (D, vista C)"),
    ("PL-06", "P2 L2", 1, f"2 CP-MEZ (A); recuo +{R2}", "6 IP-01 (C) + 6 (D, vista G)"),
    ("PL-07", "P2 L1 canto", 1, f"CP-VB +{VB(XE)} (A); 2 CP-MEZ (A); recuo A e D", "6 IP-01 (C) + 6 (B)"),
    ("PL-08", "P2 L9 canto", 1, f"CP-VB +{VB(XE)} (A); recuo A e B", "8 IP-01 (C) + 8 (D)"),
    ("PF-01", "P3 L1", 1, f"2 CP-VB +{VB(9.87)} (B, D); 4 CP-MEZ (B, D); recuo +{RV(9.87)}", "6 IP-01 (C)"),
    ("PF-02", "P4 L1", 1, f"2 CP-VB +{VB(19.75)} (B, D); 4 CP-MEZ (B, D); recuo +{RV(19.75)}", "6 IP-01 (C)"),
    ("PF-03", "P5 L1", 1, f"2 CP-VB +{VB(29.63)} (B, D); 4 CP-MEZ (B, D); recuo +{RV(29.63)}", "6 IP-01 (C)"),
    ("PF-05", "P3 L9", 1, f"2 CP-VB +{VB(9.87)} (B, D); recuo +{RV(9.87)}", "8 IP-01 (C)"),
    ("PF-04", "P14 L9", 1, f"2 CP-VB +{VB(19.75)} (B, D); CP-I130 +{f(LG['Z_ASS_I130'], 3)} (A); recuo +{RV(19.75)}", "8 IP-01 (C)"),
    ("PF-06", "P5 L9", 1, f"2 CP-VB +{VB(29.63)} (B, D); recuo +{RV(29.63)}", "8 IP-01 (C)"),
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
