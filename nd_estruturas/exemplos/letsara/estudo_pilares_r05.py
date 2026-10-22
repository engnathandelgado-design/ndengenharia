"""DEC-040 (22/10/2026) — esforços na base de cada pilar no modelo integrado r05 (2ª ordem global P-Δ e 1ª ordem),
para redimensionar a armadura longitudinal de todas as marcas. Grava estudo_pilares_r05.json."""
import json, sys, types
from pathlib import Path
AQ = Path(__file__).resolve().parent
sys.path.insert(0, str(AQ)); sys.path.insert(0, str(AQ.parent.parent))
import modelo_integrado_r05 as M
import openseespy.opensees as ops

cfg = dict(vaos_x=[3, 4, 5, 6, 7], painel=8, A_x=3.14159 * 0.016 ** 2 / 4, esperas_eixo9=4, nos_x=M.IDX_NOS_X)
_gt = ops.geomTransf


def base_pilares():
    out = {}
    for p in M.pil:
        r = ops.nodeReaction(p["ns"][0])
        segs = []
        for e in [e for e in M.ele if e.get("grupo") == "pilar" and e.get("nome") == p["nome"]]:
            f = ops.eleForce(e["tag"])                        # global: nó i (Fx,Fy,Fz,Mx,My,Mz), nó j
            segs.append([round(v, 3) for v in f])
        out[p["nome"]] = dict(N=round(r[2], 2), Vx=round(-r[0], 2), Vy=round(-r[1], 2), Mx=round(-r[3], 2), My=round(-r[4], 2),
                              bx=p["bx"], by=p["by"], H=p["zs"][-1], zs=p["zs"], segs=segs)
    return out


res = {}
for nome, fat, caso, dsp in M.combinacoes():
    item = {}
    for ordem in ("2a", "1a"):
        if ordem == "1a":
            M.ops.geomTransf = lambda tipo, *a: _gt("Linear" if tipo == "PDelta" else tipo, *a)
        else:
            M.ops.geomTransf = _gt
        ok = M.rodar(cfg, fat, caso, dsp, fator_EI=0.4 * M.C40.Eci / M.C40.Ecs)
        item[ordem] = base_pilares(); item["ok_" + ordem] = ok
    M.ops.geomTransf = _gt
    res[nome] = item
    print(nome, flush=True)
(AQ / "estudo_pilares_r05.json").write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
