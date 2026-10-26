"""rev11 (26/10/2026, pedido do Nathan): marca própria de cada consolo de pilar — C1, C2, C3…
Consolos iguais (mesma geometria, pino, neoprene e tirante) têm a mesma marca. Critério de numeração: pelo tipo
(CP-VB, CP-MEZ, CP-I120, outros) e depois pela altura e largura, crescente. Gera consolos_marcas.json com a marca,
a geometria e os pilares (nomes P1…) que usam cada uma. Rodar antes das folhas de pilares (gerar_tudo)."""
import json, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
import pilar_generico as G
import pilares_familia as PF
from familia_pl import MARCAS
import apoios_pilar as AP

ORD_TIPO = {"CP-VB": 0, "CP-MEZ": 1, "CP-I120": 2}
NOMES = json.load(open("/home/claude/letsara/pranchas/nomes.json", encoding="utf-8"))


def nomes_da_marca(mk):
    v = NOMES.get(mk) or NOMES.get("por_marca", {}).get(mk)
    if isinstance(v, list):
        return [q if isinstance(q, str) else q.get("nome") for q in v]
    return [q["nome"] for q in NOMES["pecas"] if q.get("marca") == mk]


def todos():
    out = []
    for m in MARCAS:
        P = PF.dados(m[0])
        out.append((P["marca"], P))
    for k, fn in G.DADOS.items():
        P = fn()
        out.append((P["marca"], P))
    return out


if __name__ == "__main__":
    reg = {}
    for mk, P in todos():
        for c in P["consolos"]:
            k = AP.chave(c)
            e = reg.setdefault(k, dict(tipo=c["tipo"], larg=c["larg"], proj=c["proj"], h=c["h"], hp=c["hp"], incl=c.get("incl", 0.03),
                                       pino=f"{c['pino_nome']} Ø{c['pino_d']:g} L {c['pino_L']} (emb. {c['pino_emb']}, livre {c['pino_L'] - c['pino_emb']}, a {c['pino_x']:g} da face)",
                                       neo=c["neo"], exc=c.get("exc", 0), exc_face=c.get("exc_face", ""), tirante=f"{c['tir']} ({c['n_tir']} ramos Ø{c['d_tir']:g})", marcas_pilar=[], pilares=[], n=0))
            e["n"] += 1
            if mk not in e["marcas_pilar"]:
                e["marcas_pilar"].append(mk)
                e["pilares"] += [n for n in nomes_da_marca(mk) if n not in e["pilares"]]
    chaves = sorted(reg, key=lambda k: (ORD_TIPO.get(reg[k]["tipo"], 9), reg[k]["h"], reg[k]["larg"], reg[k]["proj"], k))
    por_chave, lista = {}, []
    for i, k in enumerate(chaves, 1):
        mc = f"C{i}"
        por_chave[k] = mc
        lista.append(dict(marca=mc, **reg[k]))
    json.dump(dict(criterio="C1, C2… por tipo (CP-VB, CP-MEZ, CP-I120) e depois altura/largura; iguais = mesma geometria, pino, neoprene e tirante",
                   por_chave=por_chave, lista=lista), open(AP._REG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for e in lista:
        print(e["marca"], e["tipo"], e["larg"], e["proj"], e["h"], e["hp"], e["n"], "consolos —", ", ".join(e["pilares"][:12]), "…" if len(e["pilares"]) > 12 else "")
