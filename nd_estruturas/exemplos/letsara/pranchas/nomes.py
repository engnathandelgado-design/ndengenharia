"""Nomenclatura das peças da Letsara — padrão do Nathan (22/10/2026). FASE 1: só calcula; as folhas ainda não usam.

Regras
- Pilares: P1, P2, P3… — um nome por PEÇA (por posição), em sentido de leitura da planta de locação como desenhada na
  ND-LET-LOC01: horizontal da planta = linhas 1 → 9 (obra y), vertical = eixos A (embaixo) → E (em cima) (obra x).
  Lê-se de cima para baixo por fila de eixo (E, D, C, B, A) e, em cada fila, da esquerda para a direita (linha 1 → 9).
  Pilar fora do eixo entra na fila do eixo mais próximo (pela coordenada vertical da planta); empate na mesma linha
  (mesma coordenada horizontal) resolve de cima para baixo.
- Vigas: série por nível — V100 nível zero (não há), V200 = 1º nível acima (mezanino +3,90), V300 = +7,30,
  V400 = cobertura (TS-01, VB, I120). Um nome por peça. Convenção de leitura (padrão usual de projeto):
  primeiro as vigas HORIZONTAIS da planta (de cima para baixo e, na mesma fila, da esquerda para a direita),
  depois as VERTICAIS (da esquerda para a direita e, na mesma coluna, de cima para baixo).
- Peças iguais continuam com UMA folha; a folha lista os nomes que detalha ("P5, P6, P7, P8 — 4 peças").
- Lajes (LA) e placas (PP) mantêm o nome atual.

Fonte: geometria.py (eixos, linhas e pilares do R01), familia_pl.MARCAS (marcas dos pilares laterais/fachada),
viga_vb.py / viga_vm.py / viga_i.py (posição das marcas de viga). Nada de número fixo à mão.
Saída: nomes.json (pecas, marca_para_nomes, nome_para_marca). Rodar: python nomes.py
"""
import json, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from geometria import Y_LIN, X_EIXO, X_FACH, PILARES_ESPECIAIS, Y_PC_C
from familia_pl import marca_de

PR = "/home/claude/letsara/pranchas/"
EIXOS = sorted(X_EIXO.items(), key=lambda kv: kv[1])
# marcas dos pilares internos (mesma tabela da LOC01; chave = nome R01 + x em mm)
MARCA_INT = {("P8", 9870): "PM-01", ("P8B", 29630): "PM-02", ("P8A", 19750): "PC-01", ("P9", 9870): "PG-01", ("P10", 15195): "PG-02",
             ("P11", 19750): "PC-02", ("P10", 24305): "PG-04", ("P12", 29630): "PG-03", ("P13", 19750): "PC-03", ("P13B", 19750): "PC-03"}
FOLHA = lambda mk: "ND-LET-" + mk.replace("-", "")


def pilares_obra():
    """(marca, nome_R01, x, y, secao) de cada pilar da obra (33). x = eixo A→E, y = linha 1→9 (m)."""
    out = []
    for i, y in enumerate(Y_LIN, start=1):
        for lado, x in (("P1", 0.0), ("P2", X_EIXO["E"])):
            out.append((marca_de(f"{lado}-L{i}"), f"{lado} L{i}", x, y, "40×60"))
    for nome, x, y, bx, by in PILARES_ESPECIAIS:
        if nome in ("P6", "P7"):                                # rev09 (DEC-045): pilares da escada
            mk = "PE-02" if nome == "P7" else ("PE-03" if abs(y - Y_LIN[1]) < 1e-6 else "PE-01")
            out.append((mk, f"{nome} ({'linha 2' if mk == 'PE-03' else 'escada'})", x, y, f"{round(min(bx, by) * 100)}×{round(max(bx, by) * 100)}"))
            continue
        sec = f"{round(min(bx, by) * 100)}×{round(max(bx, by) * 100)}"
        if y in (Y_LIN[0], Y_LIN[-1]):
            li = 1 if y == Y_LIN[0] else 9
            out.append((marca_de(f"{nome}-L{li}"), f"{nome} L{li}", x, y, sec))
        else:
            out.append((MARCA_INT[(nome, round(x * 1000))], nome, x, y, sec))
    return out


def eixo_proximo(x):
    return min(EIXOS, key=lambda kv: abs(kv[1] - x))


def numerar_pilares():
    pil = pilares_obra()
    # fila = eixo mais próximo; filas de cima (E) para baixo (A); na fila, esquerda→direita (y), empate: de cima para baixo (x desc)
    ordem = sorted(pil, key=lambda p: (-eixo_proximo(p[2])[1], p[3], -p[2]))
    res = []
    for k, (mk, r01, x, y, sec) in enumerate(ordem, 1):
        fila = eixo_proximo(x)
        res.append(dict(nome=f"P{k}", tipo="pilar", marca=mk, folha=FOLHA(mk), nivel="fundação", x=x, y=y, secao=sec, ref_R01=r01,
                        fila=fila[0], fora_do_eixo=abs(fila[1] - x) > 1e-6, linha=(Y_LIN.index(y) + 1) if y in Y_LIN else None))
    return res


def vigas_obra():
    """(nivel, marca, orientação na planta, x0, y0, x1, y1, descrição) de cada viga.
    orientação: 'H' = horizontal na planta (corre ao longo das linhas, obra y); 'V' = vertical (corre ao longo do eixo, obra x)."""
    v = []
    # mezanino (rev09, DEC-045/048): VM retangulares nas linhas 1 e 2; na linha 2 o vão D–E é D → P6 (VM-03) e P6 → E (VM-04, só no +7,30);
    # viga P6–P7 da escada (VM-04) no +3,90
    from geometria import P6_L2, P6_ESC, P7_ESC
    for iz, niv in enumerate(("+3,90", "+7,30")):
        for k, (xa, xb) in enumerate(zip(X_FACH[:-1], X_FACH[1:])):
            v.append((niv, "VM-01" if k in (0, 3) else "VM-02", "V", xa, Y_LIN[0], xb, Y_LIN[0], f"linha 1, {'ABCDE'[k]}–{'ABCDE'[k + 1]}"))
        for k, (xa, xb) in enumerate(zip(X_FACH[:-2], X_FACH[1:-1])):
            v.append((niv, "VM-01" if k == 0 else "VM-02", "V", xa, Y_LIN[1], xb, Y_LIN[1], f"linha 2, {'ABCDE'[k]}–{'ABCDE'[k + 1]}"))
        v.append((niv, "VM-03", "V", X_FACH[3], Y_LIN[1], P6_L2[0], Y_LIN[1], "linha 2, D–P6"))
        if iz == 1:
            v.append((niv, "VM-04", "V", P6_L2[0], Y_LIN[1], X_FACH[4], Y_LIN[1], "linha 2, P6–E"))
        else:
            v.append((niv, "VM-04", "V", P6_ESC[0], P6_ESC[1], P7_ESC[0], P7_ESC[1], "escada, P6–P7 (y 3,79)"))
    # cobertura: I120 no eixo C (horizontal na planta)
    xc = X_EIXO["C"]
    for mk, ya, yb, d in (("V407", Y_LIN[1], Y_LIN[3], "eixo C, linhas 2–4"), ("V406", Y_LIN[3], Y_PC_C[0], "eixo C, linha 4 → PC-03"),   # DEC-058
                          ("V405", Y_PC_C[0], Y_PC_C[1], "eixo C, PC-03 → PC-03"), ("V404", Y_PC_C[1], Y_LIN[8], "eixo C, PC-03 → linha 9")):
        v.append(("cobertura", mk, "H", xc, ya, xc, yb, d))
    # cobertura: VB nas fachadas 1 e 9 (VB-01..04 linha 1, VB-05..08 linha 9, de A para E)
    for li, base in ((0, 1), (8, 5)):
        for k, (xa, xb) in enumerate(zip(X_FACH[:-1], X_FACH[1:])):
            v.append(("cobertura", f"VB-0{base + k}", "V", xa, Y_LIN[li], xb, Y_LIN[li], f"linha {li + 1}, {'ABCDE'[k]}–{'ABCDE'[k + 1]}"))
    # cobertura: TS-01 nas linhas 2 a 8, duas peças por linha (A–C e C–E); TS-01B na linha 2 (ST-1P4), TS-01A na linha 4 (IT-P)
    for li in range(2, 8):                                   # rev09 (DEC-048): linha 2 com cobertura metálica (W 310), sem TS-01
        mk = {3: "TS-01A"}.get(li, "TS-01")
        for xa, xb, d in ((0.0, xc, "A–C"), (xc, X_EIXO["E"], "C–E")):
            v.append(("cobertura", mk, "V", xa, Y_LIN[li], xb, Y_LIN[li], f"linha {li + 1}, {d}"))
    return v


SERIE = {"+3,90": 200, "+7,30": 300, "cobertura": 400}
FOLHA_V = {"VM": "ND-LET-VM01", "VB": "ND-LET-VB01", "TS": "ND-LET-TS01-1", "V4": "ND-LET-I120"}


def numerar_vigas():
    res = []
    vig = vigas_obra()
    for niv, base in SERIE.items():
        vs = [w for w in vig if w[0] == niv]
        hor = sorted([w for w in vs if w[2] == "H"], key=lambda w: (-w[3], min(w[4], w[6])))          # de cima p/ baixo, esq→dir
        ver = sorted([w for w in vs if w[2] == "V"], key=lambda w: (w[4], -max(w[3], w[5])))           # esq→dir, de cima p/ baixo
        for k, w in enumerate(hor + ver, 0):
            niv_, mk, ori, x0, y0, x1, y1, d = w
            res.append(dict(nome=f"V{base + k}", tipo="viga", marca=mk, folha=FOLHA_V[mk[:2]], nivel=niv_, orientacao_planta=ori,
                            x0=x0, y0=y0, x1=x1, y1=y1, posicao=d))
    return res


def calcular():
    pecas = numerar_pilares() + numerar_vigas()
    m2n = {}
    for p in pecas:
        m2n.setdefault(p["marca"], []).append(p["nome"])
    n2m = {p["nome"]: p["marca"] for p in pecas}
    return dict(regras=__doc__.split("Fonte:")[0].strip(), pecas=pecas, marca_para_nomes=m2n, nome_para_marca=n2m)


if __name__ == "__main__":
    d = calcular()
    json.dump(d, open(PR + "nomes.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for mk, ns in d["marca_para_nomes"].items():
        print(f"{mk:8s} {len(ns):2d}  {', '.join(ns)}")
    print(len([p for p in d["pecas"] if p["tipo"] == "pilar"]), "pilares,", len([p for p in d["pecas"] if p["tipo"] == "viga"]), "vigas")
