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
Z_CONS = {"P1": round(zf(475) + 450 * math.cos(math.atan(0.03)) - 10), "P2": round(zf(X_EIXO["E"] * 1000 - 475) + 450 * math.cos(math.atan(0.03)) - 10)}
MARCAS = [
    ("PL-01", "P1 L5–L8", 4, "CP-TS +7,914 (A); CP-VT (B, D); recuo +8,40", "8 IP-01 (C)"),
    ("PL-09", "P1 L3", 1, "CP-TS +7,914 (A); CP-VT (B, D); recuo +8,40", "2 IP-01 (C, fiadas 6–7)"),
    ("PL-10", "P1 L4", 1, "CP-TS +7,914 (A); CP-VT (B, D); recuo +8,40", "8 IP-01 (C) + 6 (B, vista C)"),
    ("PL-02", "P1 L2", 1, "CP-TS +7,914 (A); 2 CP-MEZ (A); CP-VT (B); recuo +8,40", "6 IP-01 (C) + 6 (B, vista G)"),
    ("PL-03", "P1 L1 canto", 1, "CP-VB +7,460 (A); 2 CP-MEZ (A); recuo A e B", "6 IP-01 (C) + 6 (D)"),
    ("PL-04", "P1 L9 canto", 1, "CP-VB +7,460 (A); CP-VT (D); recuo A e D", "8 IP-01 (C) + 8 (B)"),
    ("PL-05", "P2 L5–L8", 4, f"CP-TS +{f(Z_CONS['P2']/1000,3)} (A); CP-VT (B, D); recuo +9,55", "8 IP-01 (C)"),
    ("PL-11", "P2 L3", 1, f"CP-TS +{f(Z_CONS['P2']/1000,3)} (A); CP-VT (B, D); recuo +9,55", "2 IP-01 (C, fiadas 6–7)"),
    ("PL-12", "P2 L4", 1, f"CP-TS +{f(Z_CONS['P2']/1000,3)} (A); CP-VT (B, D); recuo +9,55", "8 IP-01 (C) + 6 (D, vista C)"),
    ("PL-06", "P2 L2", 1, f"CP-TS +{f(Z_CONS['P2']/1000,3)} (A); 2 CP-MEZ (A); CP-VT (D); recuo +9,55", "6 IP-01 (C) + 6 (D, vista G)"),
    ("PL-07", "P2 L1 canto", 1, "CP-VB +8,645 (A); 2 CP-MEZ (A); recuo A e D", "6 IP-01 (C) + 6 (B)"),
    ("PL-08", "P2 L9 canto", 1, "CP-VB +8,645 (A); CP-VT (B); recuo A e B", "8 IP-01 (C) + 8 (D)"),
    ("PF-01", "P3 L1", 1, "2 CP-VB +7,756 (B, D); 4 CP-MEZ (B, D); recuo +8,70", "6 IP-01 (C)"),
    ("PF-02", "P4 L1", 1, "2 CP-VB +8,053 (B, D); 4 CP-MEZ (B, D); recuo +9,00", "6 IP-01 (C)"),
    ("PF-03", "P5 L1", 1, "2 CP-VB +8,349 (B, D); 4 CP-MEZ (B, D); recuo +9,25", "6 IP-01 (C)"),
    ("PF-05", "P3 L9", 1, "2 CP-VB +7,756 (B, D); recuo +8,70", "8 IP-01 (C)"),
    ("PF-04", "P14 L9", 1, "2 CP-VB +8,053 (B, D); CP-I110 +8,190 (A); recuo +9,00", "8 IP-01 (C)"),
    ("PF-06", "P5 L9", 1, "2 CP-VB +8,349 (B, D); recuo +9,25", "8 IP-01 (C)"),
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
