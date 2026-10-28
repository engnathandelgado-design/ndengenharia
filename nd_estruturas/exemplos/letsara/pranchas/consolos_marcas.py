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
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")


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


def conferir_consolo(tipo, nome, marca_c):
    """rev12 (revisão rev12, item 2): trava pela GEOMETRIA — o pilar que usa o consolo está onde esse apoio existe:
    CP-VB nas fachadas (linhas 1 e 9), CP-MEZ na faixa do mezanino (linhas 1 e 2 e escada), CP-I120 no eixo C."""
    import renomear as RN
    from geometria import Y_LIN, X_EIXO
    p = next((q for q in NOMES["pecas"] if q["tipo"] == "pilar" and q["nome"] == nome), None)
    ok, det = p is not None, "" if p else "pilar inexistente"
    if p and tipo == "CP-VB" and p.get("linha") not in (1, 9):
        ok, det = False, f"CP-VB fora das fachadas 1/9 (y {p['y']})"
    if p and tipo == "CP-MEZ" and p["y"] > Y_LIN[1] + 0.6:
        ok, det = False, f"CP-MEZ fora do mezanino (y {p['y']} > linha 2)"
    if p and tipo == "CP-I120" and abs(p["x"] - X_EIXO["C"]) > 0.6:
        ok, det = False, f"CP-I120 fora do eixo C (x {p['x']})"
    with open(RN.TRAVA, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(dict(ok=ok, pilar=nome, onde=f"CS01 {marca_c} ({tipo})", detalhe=det), ensure_ascii=False) + "\n")
    return ok


if __name__ == "__main__":
    reg = {}
    for mk, P in todos():
        for c in P["consolos"]:
            k = AP.chave(c)
            e = reg.setdefault(k, dict(tipo=c["tipo"], larg=c["larg"], proj=c["proj"], h=c["h"], hp=c["hp"], incl=c["incl"],
                                       pino=f"{c['pino_nome']} Ø{c['pino_d']:g} L {c['pino_L']} (emb. {c['pino_emb']}, livre {c['pino_L'] - c['pino_emb']}, a {c['pino_x']:g} da face)",
                                       neo=c["neo"], exc=c.get("exc", 0), exc_face=c.get("exc_face", ""), tirante=f"{c['tir']} ({c['n_tir']} ramos Ø{c['d_tir']:g})", marcas_pilar=[], pilares=[],
                                       por_pilar={}, n=0))
            # rev12 (revisão rev12, item 2): quantidade = consolos da marca × peças da marca; lista = cada pilar com a sua contagem
            nms = nomes_da_marca(mk)
            e["n"] += P["qtd"]
            if mk not in e["marcas_pilar"]:
                e["marcas_pilar"].append(mk)
            for n_ in nms:
                e["por_pilar"][n_] = e["por_pilar"].get(n_, 0) + 1
                if n_ not in e["pilares"]:
                    e["pilares"].append(n_)
    chaves = sorted(reg, key=lambda k: (ORD_TIPO.get(reg[k]["tipo"], 9), reg[k]["h"], reg[k]["larg"], reg[k]["proj"], -reg[k]["incl"], reg[k]["exc"], k))
    por_chave, lista = {}, []
    for i, k in enumerate(chaves, 1):
        mc = f"C{i}"
        por_chave[k] = mc
        e = reg[k]
        assert e["n"] == sum(e["por_pilar"].values()), (mc, e["n"], e["por_pilar"])
        for n_ in e["pilares"]:
            conferir_consolo(e["tipo"], n_, mc)
        lista.append(dict(marca=mc, **e))
    json.dump(dict(criterio="C1, C2… por tipo (CP-VB, CP-MEZ, CP-I120) e depois altura, largura, caimento e posição na face; iguais = mesma geometria, posição, pino, neoprene e tirante",
                   por_chave=por_chave, lista=lista), open(AP._REG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for e in lista:
        print(e["marca"], e["tipo"], e["larg"], e["proj"], e["h"], e["hp"], e["n"], "consolos —", ", ".join(f"{k} ({v})" for k, v in e["por_pilar"].items()))
