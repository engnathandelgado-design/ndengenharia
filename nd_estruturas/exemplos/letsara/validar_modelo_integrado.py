"""Validação do modelo integrado r05 contra contas à mão (CLAUDE.md: MEF conferido antes de ir para a memória).

1. Equilíbrio vertical: Σ reações = Σ cargas (peso dos pilares, vigas, terças, pacote, mezanino) em 1,0 G + 1,0 Qc.
2. Equilíbrio horizontal: Σ reações em y = Σ forças de vento nas paredes (V0) + desaprumo.
3. Terça contínua: momentos de uma linha interna sob 1,0 G + 1,0 Qc contra o MEF de viga contínua com apoios rígidos
   (nd_estruturas.viga_continua) — diferença esperada pequena (apoios flexíveis no integrado).
"""
import json, math, sys
from pathlib import Path
import numpy as np
AQ = Path(__file__).resolve().parent
sys.path.insert(0, str(AQ)); sys.path.insert(0, str(AQ.parents[1]))
import modelo_integrado_r05 as M
import openseespy.opensees as ops
from nd_estruturas.viga_continua import analisar as viga_cont

cfg = dict(vaos_x=[3, 4, 5, 6, 7], painel=8)
out = {}
# 1. vertical
M.rodar(cfg, dict(G=1.3, Qc=1.0), None, None)
Rz = sum(ops.nodeReaction(p["ns"][0])[2] for p in M.pil)
carga = 0.0
for p in M.pil:
    carga += p["bx"] * p["by"] * 25 * (p["zs"][-1] - p["zs"][0]) * 1.3
for e in M.ele:
    if e["grupo"] in ("TS-01", "I120", "VB"):
        n1, n2 = ops.eleNodes(e["tag"])
        L = math.dist(ops.nodeCoord(n1), ops.nodeCoord(n2))
        carga += e["A"] * 25 * L * 1.3
for e in M.TER_ELE:
    carga += ((M.W_Z + M.CC["g_total_sem_terca"] * M.S_TER) * 1.3 + M.CC["sobrecarga"] * M.S_TER) * (e["y1"] - e["y0"])
gm = 2.8 + 1.25 + 1.0
for z in M.Z_MEZ:
    carga += 2 * sum((gm * 9.65 / 2 + M.A_VM * 25 + M.G_2E) * t for t in M.TRIB_X) * 1.3
out["vertical"] = dict(reacoes=round(Rz, 1), cargas=round(carga, 1), dif_pct=round((Rz / carga - 1) * 100, 3))
# 2. horizontal (V0, Cpi mín, sem excentricidade, sem desaprumo, 1,0 W)
cas = (0, 0, list(M.cpi_cenarios(0).values())[1])
M.rodar(cfg, dict(W=1.0), cas, None)
Ry = sum(ops.nodeReaction(p["ns"][0])[1] for p in M.pil)
M.montar(cfg)
Fw = sum(v[1] for v in M.vento_paredes(*cas).values())
out["horizontal_y"] = dict(reacoes=round(-Ry, 1), vento=round(Fw, 1), dif_pct=round((-Ry / Fw - 1) * 100, 3))
# 3. terça interna (linha 8) sob 1,3 G + 1,0 Qc: momentos de apoio e de vão vs viga contínua com apoios rígidos
M.rodar(cfg, dict(G=1.3, Qc=1.0), None, None)
lin = 8
Mvals = []
for e in sorted([e for e in M.TER_ELE if e["linha"] == lin], key=lambda e: e["y0"]):
    f = ops.eleResponse(e["tag"], "localForce")
    Mvals.append((e["y0"], -f[4])); Mvals.append((e["y1"], f[10]))
w = (M.W_Z + M.CC["g_total_sem_terca"] * M.S_TER) * 1.3 + M.CC["sobrecarga"] * M.S_TER
tr = [(M.Y[i] - M.A_TR, M.Y[i] + M.A_TR, 2.0) for i in range(1, 8)]
ref = viga_cont([M.Y[k + 1] - M.Y[k] for k in range(8)], 200e6 * M.IX_Z, w, EI_trechos=tr)
# convenção do integrado: M < 0 no vão (gravidade); a viga contínua usa M > 0 no vão
y_sup = M.Y[3]
mi_sup = max(v for y, v in Mvals if abs(y - y_sup) < 1e-3)
mr_sup = -float(ref["M"][ref["apoio_idx"][3]])
msk = (ref["x"] > M.Y[3]) & (ref["x"] < M.Y[4])
mi_vao = -min(v for y, v in Mvals if M.Y[3] < y < M.Y[4])
mr_vao = float(ref["M"][msk].max())
out["terca_linha8"] = dict(M_apoio_L4=dict(integrado=round(mi_sup, 2), viga_continua=round(mr_sup, 2)),
                            M_vao_4_5=dict(integrado=round(mi_vao, 2), viga_continua=round(mr_vao, 2)))
print(json.dumps(out, ensure_ascii=False, indent=1))
(AQ / "validacao_modelo_integrado.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
