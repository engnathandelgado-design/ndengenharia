"""Letsara — cargas na fundação por pilar (reações na base do modelo global integrado r05, mesma config do __main__).
Características por ação: G (permanentes), Q (sobrecargas de cobertura + mezanino, com G), V (vento: (G+V) − G em cada um dos
casos de vento NBR 6123, envoltória); de cálculo: envoltória das combinações ELU do modelo (NBR 8681 / 6118). Unidades: kN, kN·m.
Grava cargas_fundacao.json (lido pela prancha ND-LET-CG01)."""
import json, math, os, sys
from pathlib import Path
AQ = Path(__file__).resolve().parent
sys.path.insert(0, str(AQ))
import modelo_integrado_r05 as M
import openseespy.opensees as ops

cfg = dict(vaos_x=[3, 4, 5, 6, 7], painel=8, A_x=math.pi * 0.016 ** 2 / 4, esperas_eixo9=4, nos_x=M.IDX_NOS_X)
FEI = 0.4 * M.C40.Eci / M.C40.Ecs


def reacoes():
    ops.reactions()
    out = {}
    for p in M.pil:
        r = ops.nodeReaction(p["ns"][0])
        # ação do pilar na fundação: N (+ compressão), Hx, Hy, Mx, My (reação com sinal trocado nas horizontais e momentos)
        out[p["nome"]] = dict(N=r[2], Hx=-r[0], Hy=-r[1], Mx=-r[3], My=-r[4], x=p["x"], y=p["y"], bx=p["bx"], by=p["by"])
    return out


def caso(fat, c=None, dsp=None):
    M.rodar(cfg, fat, c, dsp, fator_EI=FEI)
    return reacoes()


res = {}
res["G"] = caso(dict(G=1.0))
res["G+Q"] = caso(dict(G=1.0, Qc=1.0, Qm=1.0))
ventos = {}
for nome, fat, c, dsp in M.combinacoes():
    if nome.endswith("G1,0"):
        nv = nome.replace("ELU ", "").replace(" G1,0", "")
        ventos[nv] = caso(dict(G=1.0, W=1.0), c, dsp)
elu = {}
for nome, fat, c, dsp in M.combinacoes():
    elu[nome] = caso(fat, c, dsp)
    print(nome, flush=True)

pil = {}
for nm, g in res["G"].items():
    q = res["G+Q"][nm]
    d = dict(x=g["x"], y=g["y"], bx=g["bx"], by=g["by"])
    d["G"] = {k: round(g[k], 1) for k in ("N", "Hx", "Hy", "Mx", "My")}
    d["Q"] = {k: round(q[k] - g[k], 1) for k in ("N", "Hx", "Hy", "Mx", "My")}
    dv = [{k: v[nm][k] - g[k] for k in ("N", "Hx", "Hy", "Mx", "My")} for v in ventos.values()]
    d["V"] = dict(N_max=round(max(x["N"] for x in dv), 1), N_min=round(min(x["N"] for x in dv), 1),
                  H_max=round(max(math.hypot(x["Hx"], x["Hy"]) for x in dv), 1),
                  Mx_max=round(max(abs(x["Mx"]) for x in dv), 1), My_max=round(max(abs(x["My"]) for x in dv), 1))
    ev = [v[nm] for v in elu.values()]
    d["ELU"] = dict(Nd_max=round(max(x["N"] for x in ev), 1), Nd_min=round(min(x["N"] for x in ev), 1),
                    Hd_max=round(max(math.hypot(x["Hx"], x["Hy"]) for x in ev), 1),
                    Mxd_max=round(max(abs(x["Mx"]) for x in ev), 1), Myd_max=round(max(abs(x["My"]) for x in ev), 1),
                    Md_res_max=round(max(math.hypot(x["Mx"], x["My"]) for x in ev), 1))
    pil[nm] = d
out = dict(fonte="modelo_integrado_r05 (OpenSeesPy, P-Δ, 0,4 Eci Ic nos pilares — NBR 9062:2017 Anexo A)", unidades="kN, kN·m",
           combinacoes_ELU=list(elu), casos_vento=list(ventos), pilares=pil)
(AQ / "cargas_fundacao.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(pil), "pilares")
