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


# ------------------------------------------------------------------ rev12b (revisão rev12b, itens 1 e 2): bainhas BA-1 por pilar — registro único
# Quantidade: cada apoio de continuidade (VM dos dois lados do pilar) leva ceil(N11 / BARRAS_POR_BAINHA) bainhas Ø50, com 3 barras em cada
# (área das barras ≤ 40 % da bainha). Posição: centro 12 cm acima do topo da VM (calc_vm_retangular: "a 12 cm acima do topo da peça"),
# dentro da faixa da VM, a ¼ e ¾ da largura da viga (eixos a B/4 do eixo da VM) — com a VM excêntrica (rente à face), a bainha acompanha a VM.
# Pilares, folhas de pilar, EX01, LA01 e listas leem daqui.
BARRAS_POR_BAINHA = 3
D_BAINHA = 50                 # mm
Z_ACIMA_VM = 120              # mm, centroide das N11 acima do topo da VM (altura útil do cálculo da negativa)
# rev12b: as 2 bainhas ficam UMA SOBRE A OUTRA (centroide no mesmo 12 cm do cálculo), na faixa do 2º estágio da VM e fora das barras
# longitudinais do pilar — lado a lado não cabem na faixa de 18 cm da VM rente da linha 1 sem pegar as barras da face externa.
S_V_BAINHA = D_BAINHA + 50    # mm entre centros (5 cm livres entre bainhas)
FOLGA_BARRA = 10              # mm livres entre a bainha (Ø nominal) e a barra longitudinal do pilar: corrugação + tolerância de montagem


def z_bainhas(n):
    """centros (mm acima do topo da VM) das n bainhas empilhadas, centroide em Z_ACIMA_VM."""
    return [Z_ACIMA_VM + (k - (n - 1) / 2) * S_V_BAINHA for k in range(n)]


def lado_laje(y_vm):
    """+1 se a laje do mezanino está do lado +y da VM na posição y_vm (a laje vai até a outra linha de VM), −1 se do lado −y."""
    P_ = json.load(open(AQ + "vm_retangular.json", encoding="utf-8"))["premissas"]
    ys = sorted(P_["y_vm"].values())
    este = min(ys, key=lambda y: abs(y - y_vm))
    outro = max(ys, key=lambda y: abs(y - este))
    return 1 if outro > este else -1


def premissas():
    return json.load(open(AQ + "vm_retangular.json", encoding="utf-8"))["premissas"]


def n_bainhas(a):
    return math.ceil(a["N11"]["n"] / BARRAS_POR_BAINHA)


def bainhas_pilar(nome):
    """apoios de continuidade no pilar `nome` (nome do projeto): [dict(niv, n, N11)]."""
    return [dict(niv=a["niv"], n=n_bainhas(a), N11=a["N11"], esq=a["esq"], dir=a["dir"], y=a["y"]) for a in apoios() if a["nome_pilar"] == nome]


def total_bainhas():
    return sum(n_bainhas(a) for a in apoios())
