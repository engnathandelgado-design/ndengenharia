"""Estudo (24/10/2026, pergunta do Nathan): eixo C com UM pilar a mais, padronizando vãos e marcas de I130.

Hoje (rev09, DEC-054): apoios no eixo C nas linhas 2 (P18, y 9,65), 4 (P20, y 29,80), P22 (y 54,575, 60×60) e 9 (P23, y 79,35)
→ V400 20,15 m (13 a 18 Ø15,2), V401 e V402 24,775 m (24 Ø15,2, no limite: dente 78×35 + consolo com mísula, protensão limitada).

Arranjos estudados (P22 pode mudar de lugar; sempre 5 apoios entre as linhas 2 e 9):
  A — linhas 2, 4, 6, 8, 9: vãos 20,15 / 19,925 / 20,00 / 9,625 (pilares sob as TS-01 das linhas 6 e 8);
  B — linhas 2, 4, 5, 7, 9: vãos 20,15 / 9,925 / 20,00 / 19,625 (pilares sob as TS-01 das linhas 5 e 7);
  C — linhas 2 e 4 fixas + 3 vãos iguais de 16,517 m até a linha 9 (pilares em y 46,317 e 62,833, entre as TS-01);
  D — 4 vãos iguais de 17,425 m de 2 a 9 (pilar da linha 4 vai para y 27,075 — só para registro: tira o P20 da linha 4).
Cada família de vãos parecidos recebe UM arranjo de cordoalhas (mesma pista, mesma forma → mesma marca de seção, só o
comprimento muda). Verificação: a mesma de estudo_i130_h120_127.py (calc_i110_r01.verificar com geometria de apoio atual,
dente 78 × 35, flechas com fluência NBR 6118:2023 Anexo A e NBR 9062:2017 5.4.3.4 Tab. 9, estabilidade lateral 9062 6.1,
ato 17.2.4.3.2, ELS Tab. 13.4, ELU 17.2.2, cortante 17.4.2.2, içamento 9062 5.3.2). Cargas: peso próprio + TS-01 nas posições
reais; TS-01 que cai sobre um pilar vai direto para o pilar.

Pilar novo: 40×40 (como o PC-02), H 7,776 m + 1,00 m de embutimento, N das reações + TS-01 no topo; vento pela parcela de
rigidez (proporcional a I) tirada do P20/P11 no modelo integrado r05; 2ª ordem pelo método geral do pilar isolado em
balanço (NBR 6118:2023 15.8.3.2, prefabricados.pilar_metodo_geral, φef 0,5). Fundação: cargas em tf e estimativa de
estacas com uma estaca de referência (premissa — a fundação é projeto próprio, ND-LET-CG01).

Só cálculo: NÃO altera i110_r01.json, pranchas, modelo nem geradores. Saída: estudo_i130_pilar_extra.json.
Desenhos e quadro de decisão: scratchpad/conf/desenho_pilar_extra.py (lê o json).
"""
import json, math, os, sys, time
from pathlib import Path
from multiprocessing import Pool
AQ = Path(__file__).parent
os.environ["SEM_MEF"] = "1"
_l = (AQ / "estudo_i130_h120_127.py").read_text(encoding="utf-8").rsplit('if __name__ == "__main__":', 1)[0]
M = {"__file__": str(AQ / "estudo_i130_h120_127.py"), "__name__": "estudo_i130_h120_127_lib"}
exec(compile(_l, "estudo_i130_h120_127", "exec"), M)
ns, rodar, ajustar, fal, resumo, descr = M["ns"], M["rodar"], M["ajustar"], M["fal"], M["resumo"], M["descr"]
CAND, ISOLS, ALCAS, ISOL0, ALCA0, INDEP = M["CAND"], M["ISOLS"], M["ALCAS"], M["ISOL0"], M["ALCA0"], M["INDEP"]
L120 = M["M"]                                     # namespace do estudo_i130_h120 (GEOS, geo_atual)
sys.path.insert(0, str(AQ))
from geometria import Y_LIN

Y_TS = Y_LIN[2:8]                                   # TS-01 das linhas 3 a 8 (a da linha 4 é a TS-01A) sobre o eixo C
Y_TS_L4 = Y_LIN[3]                                  # TS-01A da linha 4 (no topo do P20 hoje)
MEIA = {"L2": 0.30, "L9": 0.30, "P20": 0.20, "P22": 0.30, "novo": 0.20}   # meia dimensão do pilar na direção y (m)
ARRANJOS = {
    "HOJE": dict(apoios=[(9.65, "L2", "P18"), (29.80, "P20", "P20"), (54.575, "P22", "P22"), (79.35, "L9", "P23")],
                 familias=[[0], [1, 2]], titulo="Hoje: 2 · 4 · P22 (54,575) · 9"),
    "A": dict(apoios=[(9.65, "L2", "P18"), (29.80, "P20", "P20"), (49.725, "novo", "P22 → linha 6"), (69.725, "novo", "PN linha 8"), (79.35, "L9", "P23")],
              familias=[[0, 1, 2], [3]], titulo="A: apoios nas linhas 2 · 4 · 6 · 8 · 9"),
    "B": dict(apoios=[(9.65, "L2", "P18"), (29.80, "P20", "P20"), (39.725, "novo", "P22 → linha 5"), (59.725, "novo", "PN linha 7"), (79.35, "L9", "P23")],
              familias=[[0, 2, 3], [1]], titulo="B: apoios nas linhas 2 · 4 · 5 · 7 · 9"),
    "C": dict(apoios=[(9.65, "L2", "P18"), (29.80, "P20", "P20"), (29.80 + 49.55 / 3, "novo", "P22 → y 46,317"),
                      (29.80 + 2 * 49.55 / 3, "novo", "PN y 62,833"), (79.35, "L9", "P23")],
              familias=[[0], [1, 2, 3]], titulo="C: 2 · 4 fixas + 3 vãos iguais de 16,52 m"),
    "D": dict(apoios=[(9.65 + k * 69.70 / 4, t, n) for k, (t, n) in enumerate([("L2", "P18"), ("novo", "P20 → y 27,075"), ("novo", "P22 → y 44,50"),
                                                                                   ("novo", "PN y 61,925"), ("L9", "P23")])],
              familias=[[0, 1, 2, 3]], titulo="D: 4 vãos iguais de 17,425 m (tira o P20 da linha 4)"),
}
CFGS = [(1.20, 15.2, "limitada"), (1.10, 15.2, "limitada"), (1.20, 12.7, "limitada"), (1.10, 12.7, "limitada"),
        (1.20, 15.2, "completa"), (1.10, 15.2, "completa"), (1.20, 12.7, "completa")]
FCKJ_TESTE = (35.0, 40.0, 45.0)


def registrar():
    """cria no ns as vigas de cada arranjo (VIGAS, FACES, VD_MIN, GEO)."""
    geos = L120["GEOS"]["atual"]
    for nome, a in ARRANJOS.items():
        ap = a["apoios"]
        a["vaos"] = []
        for i, ((ya, ta, _), (yb, tb, _)) in enumerate(zip(ap[:-1], ap[1:])):
            k = f"{nome}{i + 1}"
            ts = [y for y in Y_TS if ya + 0.5 < y < yb - 0.5]
            ns["VIGAS"][k] = (ya, yb, sorted(ts))
            ns["FACES"][k] = (MEIA[ta], MEIA[tb])
            ns["VD_MIN"][k] = 0.0
            geos[k] = L120["geo_atual"](k)
            a["vaos"].append(dict(viga=k, ya=round(ya, 3), yb=round(yb, 3), L_eixos=round(yb - ya, 3), ts=[round(t, 3) for t in sorted(ts)]))


registrar()


def trabalho(cfg):
    vigas, H, diam, nivel = cfg
    bw, dente, geo, fckj = 0.15, True, "atual", 50.0
    vigas = sorted(vigas, key=lambda v: -(ns["VIGAS"][v][1] - ns["VIGAS"][v][0]))
    melhor, sol = None, None
    for n, pl, l5, tp in CAND:
        ajustar(H, dente, nivel, ISOL0, ALCA0, geo, fckj)
        try:
            r = rodar(vigas[0], H, bw, diam, pl, l5, tp)
        except Exception:
            continue
        f = fal(r)
        if f and set(f) & INDEP:
            if melhor is None or (len(f), r["usos"]["ELS_D_MPa"]) < (len(melhor["falhas"]), melhor["ELS_D"]):
                melhor = dict(resumo(r), arranjo=descr(diam, pl, l5, tp), viga=vigas[0])
            if not r["ok"]["ELU"] and r["usos"]["x_d"] > 0.45:
                break
            continue
        achou = None
        for isol in ISOLS:
            for alca in ALCAS:
                ajustar(H, dente, nivel, isol, alca, geo, fckj)
                try:
                    rs = [rodar(v, H, bw, diam, pl, l5, tp) for v in vigas]
                except Exception:
                    continue
                fv = sorted({k for x in rs for k in fal(x)})
                if not fv:
                    achou = (isol, alca, rs)
                    break
                if melhor is None or len(fv) < len(melhor["falhas"]):
                    melhor = dict(resumo(rs[0]), falhas=fv, arranjo=descr(diam, pl, l5, tp), viga=vigas[0])
            if achou:
                break
        if achou:
            isol, alca, rs = achou
            fj_min = fckj
            for fj in FCKJ_TESTE:                            # menor fckj de liberação com o mesmo arranjo
                ajustar(H, dente, nivel, isol, alca, geo, fj)
                try:
                    if all(not fal(rodar(v, H, bw, diam, pl, l5, tp)) for v in vigas):
                        fj_min = fj
                        break
                except Exception:
                    pass
            out = {}
            for v, x in zip(vigas, rs):
                x.pop("_lin", None)
                fl = x["flechas"]
                out[v] = dict(L_peca=x["L_peca"], n=x["n_cord"], kg_cord=x["kg_cordoalha"], peso_t=x["peso_t"], m3=x["m3"], F_total_kN=x["F_total_macaco_kN"],
                              usos=x["usos"], e1_mm=fl["e1_liberacao"], e2_mm=fl["e2_montagem"], e3_mm=fl["e3_apos_cobertura"], e4_mm=fl["e4_final_qp"],
                              lim=fl["lim"], lateral_FS=x["lateral"]["FS_min"], reacao_k=x["dente"]["reacao_k"], Vd=x["dente"]["Vd"])
            sol = dict(arranjo=descr(diam, pl, l5, tp), n=n, isol=list(isol), alca=alca, fckj_min=fj_min, vigas=out)
            break
    return dict(vigas=vigas, H=H, diam=diam, nivel=nivel, solucao=sol, melhor_falha=melhor)


# ------------------------------------------------------------------ pilar novo e fundação
from nd_estruturas.prefabricados import Concreto, pilar_metodo_geral
C40 = Concreto(40)
H_PIL, EMB = 7.776, 1.00
LG = json.loads((AQ / "ligacoes.json").read_text(encoding="utf-8"))
G_COB = LG["cargas_cob"]["g_total_sem_terca"] + 0.123 / LG["passo_tercas"]
P_TS_G = 2 * (0.2225 * 25 + G_COB * 10.075) * LG["L_TS"] / 2   # duas TS-01 por linha no topo do pilar (calc_i110_r01)
P_TS_Q = 2 * LG["cargas_cob"]["sobrecarga"] * 10.075 * LG["L_TS"] / 2
EST = json.loads((AQ / "estudo_pilares_r05.json").read_text(encoding="utf-8"))
CF = json.loads((AQ / "cargas_fundacao.json").read_text(encoding="utf-8"))["pilares"]
EST_TF = 60.0                                       # estaca de referência (premissa): hélice contínua Ø40, ~60 tf de serviço


import ast as _ast
_r05 = (AQ / "dimensionar_pilares_r05.py").read_text(encoding="utf-8")
R05 = dict(math=math, C40=C40, COB=0.030, PHI_T=0.0063, EST=EST)
exec("\n".join(_ast.get_source_segment(_r05, n) for n in _ast.parse(_r05).body
               if isinstance(n, _ast.FunctionDef) and n.name in ("barras", "camadas", "cargas_nos", "mg_nodal", "criticos")), R05)
CRIT_P11 = R05["criticos"](["P11"])
NK_P11 = CF["P11"]["G"]["N"] + CF["P11"]["Q"]["N"]        # N característico do P11 no r05 (referência das cargas nodais)
SECOES = [(0.40, 0.40), (0.40, 0.60), (0.60, 0.40), (0.50, 0.50), (0.60, 0.60)]


def rigidez_vento():
    """Σ by·bx³ (vento em x) e Σ bx·by³ (vento em y) dos pilares do r05 que recebem a cobertura (exclui os PG dos portões)."""
    tot = {"x": 0.0, "y": 0.0}
    for nome, p in CF.items():
        if nome.startswith("P10") or nome in ("P9", "P12"):
            continue
        tot["x"] += p["by"] * p["bx"] ** 3
        tot["y"] += p["bx"] * p["by"] ** 3
    return tot


def I_dir(bx, by):
    return dict(x=by * bx ** 3, y=bx * by ** 3)


def candidatos_barras(bx, by):
    out = []
    for nx in range(3, 8):
        for ny in range(3, 8):
            brs, c = R05["barras"](bx, by, nx, ny, 16.0)
            if max((bx - 2 * c) / (nx - 1), (by - 2 * c) / (ny - 1)) > 0.40:
                continue                                   # espaçamento ≤ 40 cm (18.4.2.2)
            if len(brs) * 2.01 < 0.004 * bx * by * 1e4:
                continue                                   # ρ ≥ 0,4 % (17.3.5.3)
            out.append((len(brs), nx, ny, brs, c))
    return sorted(out, key=lambda t: (t[0], t[1] + t[2]))


def pilar_novo(Nk, sec_todos, remove):
    """pilar interno do eixo C. Mesmo procedimento do dimensionar_pilares_r05 (método geral do pilar isolado em balanço,
    NBR 6118:2023 15.8.3.2, fibras + corrotacional + fluência φef 0,5 + θ1) com as cargas NODAIS do P11 (40×40, mesmo topo
    +7,776, mesmas ligações) no r05: forças verticais × Nk/Nk(P11); horizontais e momentos × parcela de rigidez
    (I do pilar / I do P11) × redistribuição pela troca de pilares (Σ I hoje / Σ I novo). Devolve a menor seção/armadura."""
    rig = rigidez_vento()
    rN = Nk / NK_P11
    I11 = I_dir(0.40, 0.40)
    for bx, by in SECOES:
        Is = I_dir(bx, by)
        novo = {e: rig[e] - sum(I_dir(*b)[e] for b in remove) + sum(I_dir(*b)[e] for b in sec_todos(bx, by)) for e in ("x", "y")}
        fat = {e: rig[e] / novo[e] for e in ("x", "y")}
        for nb, nx, ny, brs, c in candidatos_barras(bx, by):
            lams = []
            for eixo, nc, p in CRIT_P11:
                b = EST[nc]["1a"][p]
                h, bb = (bx, by) if eixo == "x" else (by, bx)
                rH = Is[eixo] / I11[eixo] * fat[eixo]
                car = [(z, Fh * rH, Fv * rN, Mm * rH) for z, Fh, Fv, Mm in R05["cargas_nos"](b, eixo)]
                lam = R05["mg_nodal"](bb, h, b["zs"], car, R05["camadas"](brs, eixo), c)
                lams.append((lam, eixo, nc))
                if lam < 1.0:
                    break
            if min(l for l, *_ in lams) >= 1.0:
                M1 = max(abs(EST[nc]["1a"]["P11"]["My" if e == "x" else "Mx"]) * Is[e] / I11[e] * fat[e] for e, nc, _ in CRIT_P11)
                kg = nb * 2.01e-4 * (H_PIL + EMB + 0.50) * 7850 + 2 * (bx + by) * 0.245 * (H_PIL + EMB) / 0.15 * 1.1
                return dict(secao=f"{bx * 100:.0f}×{by * 100:.0f}", bx=bx, by=by, barras=f"{nb} Ø16 ({nx} × {ny})", As_cm2=round(nb * 2.01, 1),
                            lambda_u_min=min(l for l, *_ in lams), rN=round(rN, 2), fat_rigidez={e: round(v, 3) for e, v in fat.items()},
                            M1d_base_kNm=round(M1, 1), lambda_esbeltez=round(2 * H_PIL * math.sqrt(12) / min(bx, by), 1),
                            m3=round(bx * by * (H_PIL + EMB), 2), kg_aco=round(kg), ok=True,
                            consolos="2 consolos para os dentes 78×35 das I130 (como no PC-02), cabeça no +7,776 para a TS-01",
                            norma="NBR 6118:2023 15.8.3.2 (método geral, φef 0,5, θ1) — cargas nodais do P11 no r05 (NBR 9062:2017 Anexo A)")
    return dict(ok=False, rN=round(rN, 2))


def fundacao(Nk_g, Nk_q, Mk):
    Nk = Nk_g + Nk_q
    n = max(2, math.ceil((1.10 * Nk / 9.81 + 2 * Mk / 9.81 / 1.2) / EST_TF - 1e-9))   # +10 % bloco; binário de estacas a 1,20 m
    return dict(Nk_tf=round(Nk / 9.81, 1), Ng_tf=round(Nk_g / 9.81, 1), Nq_tf=round(Nk_q / 9.81, 1), Mk_tf_m=round(Mk / 9.81, 1),
                estacas=n, premissa=f"estaca de referência {EST_TF:g} tf (hélice Ø40) — a confirmar no projeto de fundações")


def pilares(nome, sols):
    """reações características nos pilares do eixo C para a solução de referência (h 120, Ø15,2, limitada) e o pilar novo
    (uma marca só para os pilares novos do arranjo, dimensionada pelo de maior N)."""
    a = ARRANJOS[nome]
    reac = {}
    for v in a["vaos"]:
        for fam in sols:
            if fam and v["viga"] in fam["vigas"]:
                reac[v["viga"]] = fam["vigas"][v["viga"]]["reacao_k"]
    out = []
    for j, (y, tipo, rot) in enumerate(a["apoios"]):
        g = q = 0.0
        if j > 0:
            r = reac[a["vaos"][j - 1]["viga"]]["B"]
            g, q = g + r["g"], q + r["q"]
        if j < len(a["apoios"]) - 1:
            r = reac[a["vaos"][j]["viga"]]["A"]
            g, q = g + r["g"], q + r["q"]
        ts = any(abs(y - t) < 0.5 for t in Y_TS)
        if ts:
            g, q = g + P_TS_G, q + P_TS_Q
        out.append(dict(y=round(y, 3), tipo=tipo, rotulo=rot, ts_no_topo=ts, Nk_g_vigas_ts=round(g, 1), Nk_q=round(q, 1)))
    novos = [d for d in out if d["tipo"] == "novo"]
    remove = [(0.60, 0.60)] + ([(0.40, 0.40)] if nome == "D" else [])
    if novos:
        pior = max(novos, key=lambda d: d["Nk_g_vigas_ts"] + d["Nk_q"])
        # peso próprio entra depois de escolhida a seção (1ª passada com 40×40, 2ª com a seção achada)
        sec = (0.40, 0.40)
        for _ in range(2):
            pp = sec[0] * sec[1] * (H_PIL + EMB) * 25 + 6.0
            dim = pilar_novo(pior["Nk_g_vigas_ts"] + pp + pior["Nk_q"], lambda bx, by: [(bx, by)] * len(novos), remove)
            if not dim["ok"] or (dim["bx"], dim["by"]) == sec:
                break
            sec = (dim["bx"], dim["by"])
        for d in novos:
            d["pilar"] = dim
    hoje22 = None
    for d in out:
        bx, by = ((0.60, 0.60) if d["tipo"] == "P22" else (d["pilar"]["bx"], d["pilar"]["by"]) if d["tipo"] == "novo" and d["pilar"]["ok"] else (0.40, 0.40))
        if d["tipo"] in ("novo", "P22", "P20"):
            d["Nk_g"] = round(d["Nk_g_vigas_ts"] + bx * by * (H_PIL + EMB) * 25 + 6.0, 1)
            if d["tipo"] == "novo" and d["pilar"]["ok"]:
                Mk = d["pilar"]["M1d_base_kNm"] / 1.4
            elif d["tipo"] == "P22":
                Mk = CF["P13"]["V"]["My_max"]
                hoje22 = pilar_novo(d["Nk_g"] + d["Nk_q"], lambda bx, by: [(bx, by)], [(0.60, 0.60)])   # calibração do método
                d["pilar_metodo"] = hoje22
            else:
                Mk = CF["P11"]["V"]["My_max"]
            d["fundacao"] = fundacao(d["Nk_g"], d["Nk_q"], Mk)
    return out


def quantitativos(nome, sols, pil):
    kg, m3, t = 0.0, 0.0, 0.0
    comp = {}
    for fam in sols:
        if not fam:
            continue
        for v, x in fam["vigas"].items():
            kg += x["kg_cord"]; m3 += x["m3"]; t += x["peso_t"]
            comp.setdefault(f"{x['L_peca']:.2f}", []).append(v)
    ints = [p for p in pil if p["tipo"] in ("novo", "P20", "P22")]
    vol_p = aco_p = 0.0
    for p in ints:
        if p["tipo"] == "novo" and p["pilar"]["ok"]:
            vol_p += p["pilar"]["m3"]; aco_p += p["pilar"]["kg_aco"]
        elif p["tipo"] == "P22":                                  # PC-03 60×60, 16 Ø16 (dimensionamento r05)
            vol_p += 0.36 * (H_PIL + EMB); aco_p += 16 * 2.01e-4 * (H_PIL + EMB + 0.5) * 7850 + 2.4 * 0.245 * (H_PIL + EMB) / 0.15 * 1.1
        else:                                                     # PC-02 40×40, 14 Ø16
            vol_p += 0.16 * (H_PIL + EMB); aco_p += 14 * 2.01e-4 * (H_PIL + EMB + 0.5) * 7850 + 1.6 * 0.245 * (H_PIL + EMB) / 0.15 * 1.1
    est = sum(p["fundacao"]["estacas"] for p in ints)
    return dict(pilares_internos=len(ints), marcas_I130=len(comp), comprimentos=comp, familias_cordoalha=sum(1 for f in sols if f),
                kg_cordoalha=round(kg), m3_I130=round(m3, 1), t_I130=round(t, 1), m3_pilares_int=round(vol_p, 2), kg_aco_pilares_int=round(aco_p),
                estacas_int=est, Nk_int_tf=[p["fundacao"]["Nk_tf"] for p in ints])


def main():
    t0 = time.time()
    jobs = []
    so = [x for x in os.environ.get("SO", "").split(",") if x]       # SO=D roda só esses arranjos e junta ao json existente
    for nome, a in ARRANJOS.items():
        if so and nome not in so:
            continue
        for fi, fam in enumerate(a["familias"]):
            keys = [a["vaos"][i]["viga"] for i in fam]
            for cfg in CFGS:
                if nome == "D" and cfg != CFGS[0]:
                    continue                                # D só para registro (conflita com a linha 4): só a referência
                jobs.append((nome, fi, (keys,) + cfg))
    arq = AQ / "estudo_i130_pilar_extra.json"
    res = json.loads(arq.read_text(encoding="utf-8")) if so and arq.exists() else {}
    for n, a in ARRANJOS.items():
        if not so or n in so:
            res[n] = dict(titulo=a["titulo"], apoios=[dict(y=round(y, 3), tipo=t, rotulo=r) for y, t, r in a["apoios"]], vaos=a["vaos"], familias={})
    with Pool(int(os.environ.get("NPROC", 2))) as p:
        for k, ((nome, fi, cfg), r) in enumerate(zip(jobs, p.imap(trabalho, [j[2] for j in jobs], chunksize=1))):
            tag = f"h{r['H']:g} Ø{r['diam']:g} {r['nivel']}"
            res[nome]["familias"].setdefault(str(fi), {})[tag] = r
            s = r["solucao"]
            print(f"[{k + 1}/{len(jobs)} {time.time() - t0:.0f}s] {nome} fam{fi} {cfg[0]} {tag}: " +
                  (f"{s['arranjo']} ({s['n']}) fckj≥{s['fckj_min']:g}" if s else f"NÃO PASSA {r['melhor_falha'] and r['melhor_falha'].get('falhas')}"), flush=True)
            arq.with_suffix(".parcial.json").write_text(json.dumps(res, ensure_ascii=False, default=str), encoding="utf-8")
    REF = "h1.2 Ø15.2 limitada"
    for nome, a in res.items():
        if so and nome not in so:
            continue
        sols = [f.get(REF, {}).get("solucao") for f in a["familias"].values()]
        a["pilares"] = pilares(nome, sols)
        a["quant_ref"] = quantitativos(nome, sols, a["pilares"])
    arq.write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    print("FIM", time.time() - t0)


if __name__ == "__main__":
    main()
