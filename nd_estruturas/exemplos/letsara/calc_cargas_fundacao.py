"""Letsara — cargas na fundação por pilar (reações na base do modelo global integrado r05, mesma config do __main__).
Características por ação: G (permanentes), Q (sobrecargas de cobertura + mezanino, com G), V (vento: (G+V) − G em cada um dos
casos de vento NBR 6123, envoltória); de cálculo: envoltória das combinações ELU do modelo (NBR 8681 / 6118). Unidades: kN, kN·m.
Grava cargas_fundacao.json (lido pela prancha ND-LET-CG01)."""
import json, math, os, sys
from pathlib import Path
AQ = Path(__file__).resolve().parent
sys.path.insert(0, str(AQ))
POS = os.environ.get("CF_POS") == "1"          # rev12: só o pós-processamento (somas) sobre o cargas_fundacao.json existente
if not POS:
    import modelo_integrado_r05 as M
    import openseespy.opensees as ops

if not POS:
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


if not POS:
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


def somar_portoes(out):
    """DEC-059: os PG-01 a PG-04 apoiam a TS-01A depois do graute (calc_portao_l4.py → portao_l4.json). O modelo r05 mantém os PG
    ligados à TS-01A só em y; a reação vertical da fase 2 (g2 + q na viga contínua) é SOMADA aqui aos PG, sem descontar dos
    pilares da linha 4 / P11 (a favor da segurança nos dois). Idempotente (marca 'portao_l4' no json)."""
    pj = AQ / "portao_l4.json"
    if not pj.exists() or out.get("portao_l4"):
        return out
    PJ = json.loads(pj.read_text(encoding="utf-8"))
    nome = {"PG-01": "P9", "PG-02": "P10a", "PG-04": "P10b", "PG-03": "P12"}
    for m in PJ["ts01a"].values():
        for r in m["reacoes"]:
            d = out["pilares"][nome[r["pg"]]]
            d["G"]["N"] = round(d["G"]["N"] + r["Rg"], 1)
            d["Q"]["N"] = round(d["Q"]["N"] + r["Rq"], 1)
            d["ELU"]["Nd_max"] = round(d["ELU"]["Nd_max"] + r["Rd"], 1)
    out["portao_l4"] = "reação vertical da TS-01A somada aos PG (DEC-059)"
    return out


def somar_exc_consolos(out):
    """rev12 (opção D / fresta B): CP-VB rentes à face externa — momento adicional Mx = Σ Vd·e na base dos pilares de fachada e de
    canto (o r05 liga a VB no eixo do pilar). Somado em valor absoluto ao Mxd máx (ELU). Idempotente (marca 'exc_consolos')."""
    if out.get("exc_consolos"):
        return out
    from geometria import E_VB_FACE, DY_CANTO
    vd = json.loads((AQ / "consolos.json").read_text(encoding="utf-8"))["CP-VB"]["Vd_kN"]
    dm = {p: 2 * vd * E_VB_FACE for p in ("P3-L1", "P4-L1", "P5-L1", "P3-L9", "P14-L9", "P5-L9")}
    dm.update({p: vd * (E_VB_FACE - DY_CANTO) for p in ("P1C-L1", "P2C-L1", "P1C-L9", "P2C-L9")})
    for p, v in dm.items():
        d = out["pilares"][p]["ELU"]
        d["Mxd_max"] = round(d["Mxd_max"] + v, 1)
        d["Md_res_max"] = round(d["Md_res_max"] + v, 1)
    out["exc_consolos"] = "ΔMxd = Σ Vd·e dos CP-VB rentes à face somado ao Mxd máx (rev12)"
    return out


def somar_exc_mez(out):
    """rev12 (27/10): VM da linha 1 alinhada à face externa — CP-MEZ rentes à face nos PF (4 consolos, e = 0,15) e nos cantos da
    linha 1 (2 consolos, e = 0,05): ΔMxd = Σ Vd·e somado ao Mxd máx. Idempotente (marca 'exc_mez')."""
    if out.get("exc_mez"):
        return out
    import dimensionar_pilares_r05 as _DP
    for p, v in _DP.DM_MEZ.items():
        d = out["pilares"][p]["ELU"]
        d["Mxd_max"] = round(d["Mxd_max"] + v, 1)
        d["Md_res_max"] = round(d["Md_res_max"] + v, 1)
    out["exc_mez"] = {p: round(v, 1) for p, v in _DP.DM_MEZ.items()}
    return out


def somar_exc_pg(out):
    """rev12 (27/10, DEC-092): PG-02/PG-04 com o eixo 7,5 cm fora da linha 4 (face no plano dos vizinhos 40 × 40). Coordenada y da base
    corrigida e, a favor da segurança, reação da TS-01A tomada no eixo da linha 4 (o NEO-7 é centrado no pilar, e = 0 nominal):
    ΔMxd = Rd·e somado ao Mxd máx. A excentricidade das placas (CS-1 na face) diminui 7,5 cm — desprezada (a favor). Idempotente."""
    if out.get("exc_pg"):
        return out
    from geometria import Y_PG, DY_PG
    PJ = json.loads((AQ / "portao_l4.json").read_text(encoding="utf-8"))
    nome = {"PG-01": "P9", "PG-02": "P10a", "PG-04": "P10b", "PG-03": "P12"}
    reg = {}
    for mk, nm in nome.items():
        d = out["pilares"][nm]
        d["y"] = Y_PG[mk]
        if DY_PG[mk]:
            rd = max(r["Rd"] for m in PJ["ts01a"].values() for r in m["reacoes"] if r["pg"] == mk)
            dm = rd * DY_PG[mk]
            d["ELU"]["Mxd_max"] = round(d["ELU"]["Mxd_max"] + dm, 1)
            d["ELU"]["Md_res_max"] = round(d["ELU"]["Md_res_max"] + dm, 1)
            reg[nm] = round(dm, 2)
    out["exc_pg"] = reg
    return out


if POS:
    out = json.loads((AQ / "cargas_fundacao.json").read_text(encoding="utf-8"))
    pil = out["pilares"]
out = somar_portoes(out)
out = somar_exc_consolos(out)
out = somar_exc_mez(out)
out = somar_exc_pg(out)
(AQ / "cargas_fundacao.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(pil), "pilares")
