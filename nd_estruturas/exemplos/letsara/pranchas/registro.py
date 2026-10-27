"""rev12 (revisão independente rev12, causa raiz): REGISTRO ÚNICO POR MARCA para as saídas secundárias.

Toda saída que não é a folha da própria peça (PR01, IC01, CS01, CG01, LOC01, listas, xlsx, IFC/3D) tira daqui:
  - pilares: seção (x × y), cabeça (seção cheia / cabeça recuada), L, quantidade, volume e peso (QUADRO DA PEÇA gravado pelo
    gerador da folha, que calcula da geometria), consolos (geometria <MARCA>_geom.json: tipo, face, nível, excentricidade,
    pino, neoprene) e insertos (tabela INSERTOS da folha);
  - aparelhos de apoio e pinos: uma marca = uma descrição (APARELHOS / PINOS), escolhida pelo tipo do consolo.
Nada de volume, peso, seção ou neoprene digitado nas saídas secundárias."""
import json, os, re

PR = "/home/claude/letsara/pranchas/"
NOMES = json.load(open(PR + "nomes.json", encoding="utf-8"))

# ------------------------------------------------------------------ aparelhos de apoio (um por apoio) e pinos — descrição única
# chave = tipo do consolo do pilar (o neoprene é do apoio, fica no pilar; a folha da viga só cita)
APARELHOS = {
    "CP-MEZ": dict(marca="NEO-5F", dims=(200, 200, 21), desc="Neoprene fretado 200×200×21 c/ furo Ø30 — apoio do dente da VM"),
    "CP-VB": dict(marca="NEO-6", dims=(100, 100, 10), desc="Neoprene 100×100×10 c/ furo Ø30 — apoio do dente da VB"),
    "CP-I120": dict(marca="NEO-2", dims=(300, 200, 31), desc="Neoprene fretado 300×200×31 (2 × 10 + 2 × 2,5, chapas inox 2 mm) — apoio da I120"),
}
PINOS = {
    "PN-1": "Pino Ø20 CA-50 L=630 (230 no consolo, 400 livre) — CP-MEZ",
    "PN-2": "Pino Ø25 CA-50 L=900 (350 no consolo, 550 livre) — CP-I120",
    "PN-6": "Barra roscada Ø20 A36 L=700 (300 no consolo, 400 livre, 100 roscados) + porca, contraporca e arruela 60×60×6 — CP-VB",
}
# dono de cada item da lista (fonte única): itens do apoio contam pelo pilar, nunca de novo pela folha da viga
DONO = {"NEO-5F": "pilar", "NEO-6": "pilar", "NEO-2": "pilar", "PN-1": "pilar", "PN-2": "pilar", "PN-6": "pilar"}
DESC_CANON = {**{a["marca"]: a["desc"] for a in APARELHOS.values()}, **PINOS}


def num(s):
    s = str(s).strip().split()[0]
    return float(s.replace(".", "").replace(",", ".")) if "," in s else float(s)


def tab(T, inicio):
    for t in T["tabelas"]:
        if t["titulo"].upper().startswith(inicio.upper()):
            return t
    return None


def nomes_de(marca):
    return [p["nome"] for p in NOMES["pecas"] if p.get("marca") == marca]


def folha_de(marca):
    return "ND-LET-" + marca.replace("-", "")


def pilar(marca):
    """registro de um pilar (marca de fabricação)."""
    fl = folha_de(marca)
    T = json.load(open(PR + fl + ".tabelas.json", encoding="utf-8"))
    G = json.load(open(PR + marca + "_geom.json", encoding="utf-8"))
    q = {}
    for l in tab(T, "QUADRO")["linhas"]:
        q[l[0]] = l[1]; q[l[2]] = l[3]
    sec = q["SEÇÃO"].replace(" cm", "")
    cabeca = ("cabeça recuada" if G.get("rec") else "seção cheia até o topo") if marca[:2] in ("PL", "PF") else ""
    ins = []
    ti = next((t for t in T["tabelas"] if t["titulo"].upper().startswith("INSERTOS")), None)
    for l in (ti["linhas"] if ti else []):
        try:
            n = int(str(l[2]).split()[0])
        except ValueError:
            n = 0
        ins.append(dict(marca=l[0], desc=l[1], qt=n, pos=l[3] if len(l) > 3 else ""))
    return dict(marca=marca, folha=fl, nomes=nomes_de(marca), secao=sec, cabeca=cabeca, L=num(q["COMPRIMENTO"]) / 100, qt=int(num(q["QUANTIDADE"])),
                vol=num(q["VOLUME"]), peso=num(q["PESO"]), concreto=q.get("CONCRETO", "C40"), consolos=G["consolos"], insertos=ins, geom=G)


def marcas_pilar():
    out = sorted({p["marca"] for p in NOMES["pecas"] if p["tipo"] == "pilar"})
    return [m for m in out if os.path.exists(PR + folha_de(m) + ".tabelas.json")]


def pilares():
    return {m: pilar(m) for m in marcas_pilar()}


def secao_txt(R):
    return R["secao"] + (f", {R['cabeca']}" if R["cabeca"] else "")


# ------------------------------------------------------------------ valores únicos de projeto (rev12, item 11): uma fonte só
_AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
_LG = json.load(open(_AQ + "ligacoes.json", encoding="utf-8"))
_PJ = json.load(open(_AQ + "portao_l4.json", encoding="utf-8"))
_VMJ = json.load(open(_AQ + "vm_retangular.json", encoding="utf-8"))["premissas"]
import sys as _sys
_sys.path.insert(0, _AQ)
from geometria import X_EIXO as _XE
FOLGAS_MM = {                                                       # folgas de montagem na geometria do modelo (modelo_bim / lig.)
    "TS-01 no pilar lateral": round(_LG["X_PONTA_ESQ"] * 1000),
    "TS-01 entre as pontas no eixo C": round(2 * (_XE["C"] - _LG["X_PONTA_CEN"]) * 1000),
    "I120 no pilar": 75,                                            # modelo_bim: ponta a 0,075 da face (y0 = ya + meia + 0,075)
    "VB no pilar": 25,
    "VM no pilar (junta grauteada)": round(_VMJ["folga_m"] * 1000),
    "placas: junta vertical": 20, "placas: altura": 5,
}
PORTAO = dict(larg_m=min(_PJ["vao_livre_portoes_m"].values()), livre_ate=7.50)   # portões 500 × 750: livres até +7,50 (PG apoiam a TS-01A)
ESCADA_CHEGADA = 3.95                                               # piso pronto do 1º pavimento (DEC-055): chegada da escada


def f1(v, d=2):
    return f"{v:.{d}f}".replace(".", ",")


def folgas_txt():
    return "; ".join(f"{k} {f1(v / 10, 1).replace(',0', '')} cm" for k, v in FOLGAS_MM.items())


def portao_txt():
    return f"portões {PORTAO['larg_m'] * 100:.0f} × {PORTAO['livre_ate'] * 100:.0f} livres até +{f1(PORTAO['livre_ate'])}"
