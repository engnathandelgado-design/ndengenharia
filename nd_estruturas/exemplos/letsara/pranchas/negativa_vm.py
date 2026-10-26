"""Armadura de continuidade das VM sobre os pilares (registro único): lê vm_retangular.json (campo negativa.adotado de cada marca,
saída do cálculo calc_vm_retangular.py) e nomes.json (VM e pilar de cada apoio). Usado pela ND-LET-LA01 e pela ND-LET-EX01."""
import json, math, re, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
import renomear as RN

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
PR = "/home/claude/letsara/pranchas/"


def _barras(txt):
    m11 = re.search(r"N11:\s*(\d+)\s*Ø\s*([\d,]+)", txt); m12 = re.search(r"N12:\s*(\d+)\s*Ø\s*([\d,]+)", txt)
    L = float(re.search(r"L\s*=\s*([\d,]+)\s*cm", txt).group(1).replace(",", ".")) / 100
    return (dict(n=int(m11.group(1)), d=float(m11.group(2).replace(",", ".")), L=L),
            dict(n=int(m12.group(1)), d=float(m12.group(2).replace(",", ".")), L=L))


def apoios():
    VM = json.load(open(AQ + "vm_retangular.json", encoding="utf-8"))
    NM = json.load(open(PR + "nomes.json", encoding="utf-8"))["pecas"]
    vigas = [p for p in NM if p["tipo"] == "viga" and p["nivel"] in ("+3,90", "+7,30")]
    pil = [p for p in NM if p["tipo"] == "pilar"]
    out = []
    for niv in ("+3,90", "+7,30"):
        vs = [p for p in vigas if p["nivel"] == niv]
        for a in vs:
            for b in vs:
                if a is b or abs(a["y0"] - b["y0"]) > 0.05 or abs(a["x1"] - b["x0"]) > 0.05:
                    continue
                x, y = a["x1"], a["y0"]
                pn = min(pil, key=lambda q: math.hypot(q["x"] - x, q["y"] - y))["nome"]
                na, nb = _barras(VM[a["marca"]]["negativa"]["adotado"]), _barras(VM[b["marca"]]["negativa"]["adotado"])
                n11 = max((na[0], nb[0]), key=lambda d: d["n"] * d["d"] ** 2)       # o lado mais armado governa o apoio
                n12 = max((na[1], nb[1]), key=lambda d: d["n"] * d["d"] ** 2)
                RN.conferir_pilar(pn, f"continuidade VM {niv} {a['nome']}/{b['nome']}", x=x, y=y)      # rev12: trava pela geometria
                # rev12: nomes novos protegidos (renomeação uma vez só — rev11 trocava P13/P14/P5 de novo pelo R01)
                out.append(dict(niv=niv, pilar=RN.N(pn), nome_pilar=pn, x=x, y=y, esq=RN.N(a["nome"]), dir=RN.N(b["nome"]), marca=(a["marca"], b["marca"]), N11=n11, N12=n12))
    return out


def txt(d):
    return f"{d['n']} Ø{d['d']:g} L {d['L'] * 100:g}".replace(".", ",")
