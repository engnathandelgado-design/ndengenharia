"""Estudo (23/10/2026, pergunta do Nathan): altura mínima da V401 (V406) e V402 (V405), com e sem dente Gerber.
Só cálculo — NÃO altera i110_r01.json, pranchas nem geradores. Saída: estudo_i130_hmin.json.

Reaproveita integralmente o cálculo de estudo_i130_h110.py (calc_i110_r01.verificar + flechas com fluência no tempo,
NBR 9062:2017 5.4.3.4 Tab. 9 + estabilidade lateral 6.1) e varre:
  h 110/115/120/125/130 · alma 15…40 · Ø12,7 e Ø15,2 · todos os arranjos (inclusive < 20 cordoalhas) · 4 isolamentos ·
  alças 2,50/1,50 m · mesa superior N3 4Ø20 ou 6Ø25 · com dente (78 × 35, recorte h−0,78) e SEM dente (seção cheia
  até a ponta, apoio direto no consolo/topo do pilar, todas as cordoalhas a partir da ponta).
Protensão completa (DEC-043: ELS-D frequente, ELS-F rara) com a folga de projeto ELS-D ≤ −0,25 MPa (MARGEM_D; a norma
pede ≤ 0) e, só como informação, protensão limitada (ELS-D quase permanente, ELS-F frequente) para h < 130.
Poda: isolamento e alças só afetam as pontas (ato, içamento, transferência) — com ELS-D no meio, ELU ou estabilidade
reprovados as variantes não são testadas; com x/d > 0,45 ou ato da base no meio reprovado, arranjos maiores também
reprovam e a busca daquela configuração para.
"""
import json, os, sys, itertools, time
from pathlib import Path
from multiprocessing import Pool
AQ = Path(__file__).parent
os.environ["SEM_MEF"] = "1"
_src = (AQ / "estudo_i130_h110.py").read_text(encoding="utf-8").split("# ------------------------------------------------------------------ HOJE")[0]
G = {"__file__": str(AQ / "estudo_i130_h110.py"), "__name__": "estudo_i130_h110_lib"}
exec(compile(_src, "estudo_i130_h110", "exec"), G)
ns, rodar = G["ns"], G["rodar"]
LN0, HD0, ISOL0, ALCA0, N30 = ns["LN"], ns["HD"], ns["ISOL"], ns["ALCA_A"], ns["N3"]
PSI = dict(completa=(ns["PSI1"], 1.0), limitada=(ns["PSI2"], ns["PSI1"]))
ISOLS = [ISOL0, (0, 2000, 2000, 4000), (0, 2000, 4000, 6000), (0, 3000, 3000, 6000)]
ALCAS = [ALCA0, 1.50]
N3S = [N30, (6, 25.0)]
combos = sorted({c for c in itertools.product((7, 5, 4, 0), repeat=4) if c[0] >= c[1] >= c[2] >= c[3] and c[0] > 0 and c[1] > 0})
CAND = sorted(((sum(pl) + l5 + 2 * tp, pl, l5, tp) for pl in combos for l5 in (0, 2, 4) for tp in (False, True)), key=lambda c: (c[0], -c[1][0]))
INDEP = {"ELS_D_margem", "ELU", "lateral"}          # não dependem de isolamento nem de alças


def ajustar(H, dente, nivel, n3, isol, alca):
    ns["LN"], ns["HD"] = (LN0, HD0) if dente else (0.0, H)
    ns["PSI_D"], ns["PSI_F"] = PSI[nivel]
    ns["N3"], ns["ISOL"], ns["ALCA_A"] = n3, isol, alca


def fal(r):
    return sorted(k for k, v in r["ok"].items() if not v)


def resumo(r):
    return dict(arranjo=r["arranjo"], n=r["n_cord"], cordoalha=r["cordoalha"], bw_cm=r["bw_cm"], falhas=fal(r), ELS_D=r["usos"]["ELS_D_MPa"],
                x_d=r["usos"]["x_d"], ato_base=r["usos"]["ato_base_MPa"], ato_topo=r["usos"]["ato_topo_MPa"], icam=r["usos"]["icamento_topo_MPa"])


def trabalho(cfg):
    H, bw, diam, n3, dente, nivel = cfg
    melhor_falha, sol = None, None
    for n, pl, l5, tp in CAND:
        ajustar(H, dente, nivel, n3, ISOL0, ALCA0)
        try:
            r = rodar("V406", H, bw, diam, pl, l5, tp)
        except Exception:
            continue
        f = fal(r)
        cand_falha = dict(resumo(r), isol=list(ISOL0), alca=ALCA0)
        if f and set(f) & INDEP:
            if melhor_falha is None or (len(f), r["usos"]["ELS_D_MPa"]) < (len(melhor_falha["falhas"]), melhor_falha["ELS_D"]):
                melhor_falha = cand_falha
            if not r["ok"]["ELU"] and r["usos"]["x_d"] > 0.45:
                break                                   # excesso de armadura ativa: maiores também reprovam
            continue
        ok_var = None
        for isol in ISOLS:
            for alca in ALCAS:
                ajustar(H, dente, nivel, n3, isol, alca)
                try:
                    rv = rodar("V406", H, bw, diam, pl, l5, tp)
                except Exception:
                    continue
                fv = fal(rv)
                if not fv:
                    ok_var = (isol, alca, rv)
                    break
                if melhor_falha is None or (len(fv), rv["usos"]["ELS_D_MPa"]) < (len(melhor_falha["falhas"]), melhor_falha["ELS_D"]):
                    melhor_falha = dict(resumo(rv), isol=list(isol), alca=alca)
            if ok_var:
                break
        if ok_var:
            isol, alca, rv = ok_var
            ajustar(H, dente, nivel, n3, isol, alca)
            r5 = rodar("V405", H, bw, diam, pl, l5, tp)
            if not fal(r5):
                for x in (rv, r5):
                    x.pop("_lin", None)
                    x["isolamento_mm"], x["alca_m"], x["N3"] = list(isol), alca, f"{n3[0]} Ø{n3[1]:g}"
                sol = dict(V406=rv, V405=r5)
                break
    return dict(h=H, bw=bw, diam=diam, N3=f"{n3[0]} Ø{n3[1]:g}", dente=dente, nivel=nivel, solucao=sol, melhor_falha=melhor_falha)


if __name__ == "__main__":
    t0 = time.time()
    HS, BWS = (1.10, 1.15, 1.20, 1.25, 1.30), (0.15, 0.20, 0.25, 0.30, 0.35, 0.40)
    cfgs = [(h, bw, d, n3, dn, "completa") for h in HS for bw in BWS for d in (12.7, 15.2) for n3 in N3S for dn in (True, False)]
    cfgs += [(h, bw, d, n3, True, "limitada") for h in HS[:-1] for bw in BWS for d in (12.7, 15.2) for n3 in N3S]
    out = []
    with Pool(int(os.environ.get("NPROC", 2))) as p:
        for k, r in enumerate(p.imap_unordered(trabalho, cfgs, chunksize=1)):
            out.append(r)
            if r["solucao"]:
                s = r["solucao"]["V406"]
                print(f"[{k+1}/{len(cfgs)} {time.time()-t0:.0f}s] OK h{r['h']} bw{r['bw']} Ø{r['diam']} {r['N3']} dente={r['dente']} {r['nivel']}: {s['arranjo']} ({s['n_cord']})", flush=True)
            elif (k + 1) % 20 == 0:
                print(f"[{k+1}/{len(cfgs)} {time.time()-t0:.0f}s]", flush=True)
    (AQ / "estudo_i130_hmin_bruto.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    print("FIM", time.time() - t0)
