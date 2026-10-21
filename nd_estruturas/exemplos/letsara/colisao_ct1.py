"""Checagem geométrica de colisão (caixas envolventes reais, não visual) das peças antigiro da VM com o modelo da obra (DEC-038).

Monta o modelo_bim.montar() SEM as CT-1 antigas e testa, em cada ponta de VM (2 níveis × 2 linhas × 4 vãos × 2 pontas = 32):
  A) CT-1 lateral (L 152×102 na face externa da VM, aba 102 na face do CP-MEZ do pilar) — a solução antiga;
  B) CT-1P lateral (cantoneira larga na face lateral externa do PL, aba saliente 102) — a proposta para os PL;
  C) CT-1T no topo (aba horizontal sobre a VM, aba vertical na face do pilar acima da VM) — dentro da largura da VM.
Colisão = interpenetração > 1 mm com peça que não seja a hospedeira (contato de face é permitido) e sem estar dentro do
2º estágio (concretado depois, embute a peça). Também confere se a aba que deveria apoiar no pilar tem pilar atrás (caso A nos PL).
Saída: colisao_ct1.json."""
import json, math, sys
from pathlib import Path
AQ = Path(__file__).parent
sys.path.insert(0, str(AQ)); sys.path.insert(0, str(AQ.parent.parent))
import modelo_bim as MB
from nd_estruturas.bim import PerfilRetangular, PerfilI, PerfilPoligono

TOL = 0.001


def aabb(p):
    M = p.matriz()
    pf = p.perfil
    if isinstance(pf, PerfilPoligono):
        loc = [(x, y) for x, y in pf.pontos]
    elif isinstance(pf, PerfilI):
        loc = [(-pf.b / 2, -pf.h / 2), (pf.b / 2, pf.h / 2)]
    else:
        loc = [(-pf.b / 2, -pf.h / 2), (pf.b / 2, -pf.h / 2), (pf.b / 2, pf.h / 2), (-pf.b / 2, pf.h / 2)]
    L = p.comprimento
    pts = []
    for (a, b) in loc:
        for c in (0.0, L):
            pts.append(tuple(M[i][0] * a + M[i][1] * b + M[i][2] * c + M[i][3] for i in range(3)))
    return tuple(min(q[i] for q in pts) for i in range(3)), tuple(max(q[i] for q in pts) for i in range(3))


def pen(a, b):
    """menor interpenetração entre duas caixas (m); <= 0 = não se tocam."""
    return min(min(a[1][i], b[1][i]) - max(a[0][i], b[0][i]) for i in range(3))


m = MB.montar()
NOVAS = ("CT-1", "BR-3", "BR-4", "BR-5")
pecas = [p for p in m.pecas if not p.marca.startswith(NOVAS)]
caixas = [(p, aabb(p)) for p in pecas]
VMP = MB.json.loads((AQ / "vm_meio_vaso.json").read_text(encoding="utf-8"))["premissas"]
bt, hv = VMP["b_alma"] + VMP["b_aba"], VMP["h_pm"]
from geometria import X_EIXO, Y_LIN
LARG = MB.LARG
faces = [(0.30, X_EIXO["B"] - 0.20), (X_EIXO["B"] + 0.20, X_EIXO["C"] - 0.20), (X_EIXO["C"] + 0.20, X_EIXO["D"] - 0.20), (X_EIXO["D"] + 0.20, LARG - 0.30)]
T, A1, A2 = 0.0159, 0.152, 0.102
out = dict(casos={}, resumo={})


def pilar_em(x, y, z):
    for p, bb in caixas:
        if p.tipo == "pilar" and bb[0][0] - 0.05 <= x <= bb[1][0] + 0.05 and bb[0][1] - 1e-6 <= y <= bb[1][1] + 1e-6 and bb[0][2] <= z <= bb[1][2]:
            return p, bb
    return None, None


def testa(nome, cx, hosp):
    res = []
    for p, bb in caixas:
        if p is hosp[0] or p is hosp[1]:
            continue
        d = pen(cx, bb)
        if d > TOL and "2º estágio" not in p.marca and "graute" not in p.marca:
            res.append(dict(peca=p.marca, grupo=p.grupo, penetracao_mm=round(d * 1000, 1)))
    return res


for nivel in MB.NIVEIS_MEZ:
    za = nivel - MB.H_LAJE - 0.01
    for y, so in ((Y_LIN[0], -1), (Y_LIN[1], 1)):
        for fa, fb in faces:
            for xf, sg in ((fa, 1), (fb, -1)):
                vm = next(p for p, bb in caixas if p.tipo == "viga" and "alma" in p.marca and f"{nivel:+.2f}" in p.marca and abs(((bb[0][1] + bb[1][1]) / 2) - (y + so * (bt / 2 - VMP["b_alma"] / 2))) < 0.01 and bb[0][0] - 0.05 <= xf + sg * 0.5 <= bb[1][0] + 0.05)
                pil, pbb = pilar_em(xf - sg * 0.05, y, za - 0.1)
                tipo_p = "PL" if xf in (0.30, LARG - 0.30) else "PF/PC/PM"
                yext = y + so * bt / 2                                   # face externa da VM
                folga_lat = (pbb[1][1] - yext) if so > 0 else (yext - pbb[0][1])   # quanto o pilar passa da face externa da VM
                # A) CT-1 lateral: aba 152 na VM (de xf para dentro), aba 102 na face do pilar (para fora da VM)
                a152 = ((min(xf, xf + sg * A1), min(yext, yext + so * T), za - 0.15), (max(xf, xf + sg * A1), max(yext, yext + so * T), za))
                a102 = ((min(xf, xf + sg * T), min(yext, yext + so * A2), za - 0.15), (max(xf, xf + sg * T), max(yext, yext + so * A2), za))
                apoio_A = folga_lat >= A2 - 0.002 - 1e-6
                colA = testa("A", a152, (vm, pil)) + testa("A", a102, (vm, pil))
                # B) CT-1P lateral (só faz sentido nos PL): cantoneira L = 250 ao longo de x na face lateral, aba 102 saliente na base
                cB1 = ((min(xf - sg * 0.11, xf + sg * 0.14), min(yext, yext + so * T), za - A1), (max(xf - sg * 0.11, xf + sg * 0.14), max(yext, yext + so * T), za))
                cB2 = ((cB1[0][0], min(yext, yext + so * A2), za - A1), (cB1[1][0], max(yext, yext + so * A2), za - A1 + T))
                colB = testa("B", cB1, (vm, pil)) + testa("B", cB2, (vm, pil))
                # C) CT-1T no topo: aba horizontal 152 sobre a VM (da face do pilar para dentro) e aba vertical 102 na face do pilar
                yc = y + so * (bt / 2 - 0.125)                           # sobre a alma (25), centrada nela
                cC1 = ((min(xf, xf + sg * A1), yc - 0.075, za), (max(xf, xf + sg * A1), yc + 0.075, za + T))
                cC2 = ((min(xf, xf + sg * T), yc - 0.075, za), (max(xf, xf + sg * T), yc + 0.075, za + A2))
                colC = testa("C", cC1, (vm, pil)) + testa("C", cC2, (vm, pil))
                k = f"{nivel:+.2f} L{1 if so < 0 else 2} x={xf:.2f}"
                out["casos"][k] = dict(pilar=pil.marca, tipo=tipo_p, folga_lateral_mm=round(folga_lat * 1000), A_aba102_com_pilar_atras=apoio_A,
                                       A_colisoes=colA, B_colisoes=colB, C_colisoes=colC)
cs = out["casos"].values()
for tp in ("PL", "PF/PC/PM"):
    sel = [c for c in cs if c["tipo"] == tp]
    out["resumo"][tp] = dict(pontas=len(sel), A_sem_apoio=sum(not c["A_aba102_com_pilar_atras"] for c in sel), A_colide=sum(bool(c["A_colisoes"]) for c in sel),
                             B_colide=sum(bool(c["B_colisoes"]) for c in sel), C_colide=sum(bool(c["C_colisoes"]) for c in sel),
                             exemplos_B=sorted({x["peca"] for c in sel for x in c["B_colisoes"]})[:6], exemplos_C=sorted({x["peca"] for c in sel for x in c["C_colisoes"]})[:6],
                             exemplos_A=sorted({x["peca"] for c in sel for x in c["A_colisoes"]})[:6])
# checagem final: as peças adotadas como estão no 3D (CT-1 nos PF/PC/PM, CT-1P no topo dos PL, buchas) contra todo o resto
fin = []
for p in m.pecas:
    if not p.marca.startswith(NOVAS):
        continue
    bb = aabb(p)
    for q, qb in caixas:
        if q.tipo in ("pilar", "viga") or "2º estágio" in q.marca or "graute" in q.marca or "consolo" == q.tipo:
            continue                                             # hospedeiras (buchas dentro do concreto; abas encostadas)
        d = pen(bb, qb)
        if d > TOL:
            fin.append(dict(peca=p.marca, contra=q.marca, penetracao_mm=round(d * 1000, 1)))
out["final"] = dict(pecas=sum(1 for p in m.pecas if p.marca.startswith(NOVAS)), colisoes=fin)
out["resumo"]["final"] = dict(pecas=out["final"]["pecas"], colisoes=len(fin), exemplos=fin[:5])
(AQ / "colisao_ct1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(out["resumo"], ensure_ascii=False, indent=1))
