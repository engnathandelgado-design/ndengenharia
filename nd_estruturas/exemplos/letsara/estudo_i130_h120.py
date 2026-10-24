"""Estudo (24/10/2026, liberação do Nathan): V401 (V406) e V402 (V405) com h = 120 cm.
Liberado: alma mais larga, fck 50 MPa, protensão LIMITADA, tirar o dente Gerber e baixar o consolo, e apoio
"centralizado" nos dois pilares do meio da linha C (P11 e P13). Só cálculo — NÃO altera i110_r01.json, pranchas nem
geradores. Saída: estudo_i130_h120.json (+ _bruto).

Base: estudo_i130_h110.py / estudo_i130_hmin.py (calc_i110_r01.verificar + flechas com fluência NBR 6118:2023 Anexo A e
NBR 9062:2017 5.4.3.4 Tab. 9 + estabilidade lateral 6.1). Acrescenta:
  - geometria de apoio parametrizada (GEO): "atual" = pino a 175 da ponta, ponta a 75 da face do pilar (consolo na face);
    "centralizado" = as duas vigas apoiam no TOPO do pilar (P11 40×40, P13 60×60), ponta a 10 mm do eixo (junta de 20 mm),
    aparelho centrado na metade do pilar de cada viga; na P14 (linha 9, fachada) continua o consolo na face;
  - 2 ou 4 cordoalhas na mesa superior; mais esquemas de isolamento e alças a 1,50 / 2,50 / 3,50 m;
  - fck 50 (já é o vigente, calc_i110_r01 C = Concreto(50)) com fckj 45 na liberação; fckj 50 só como informação.
Nível: CAA II (nbr9062.json) e pré-tração → NBR 6118:2023 Tab. 13.4 permite protensão LIMITADA (nível 2: ELS-F na
combinação frequente, ELS-D na quase permanente). Completa (DEC-043) a h 120 já reprovou em todas as variantes
(estudo_i130_hmin) — com apoio centralizado o vão cresce, então não é refeita aqui.
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

# ---- verificar() com a geometria de apoio parametrizada
_calc = (AQ / "calc_i110_r01.py").read_text(encoding="utf-8")
_fn = "def verificar" + _calc.split("def verificar", 1)[1].split("\nres = {}")[0]
_old = ("    fa, fb = FACES[nome]\n"
        "    x0 = ya + fa + 0.075 + 0.175                        # pino a 175 da ponta; ponta a 75 da face\n"
        "    x1 = yb - fb - 0.075 - 0.175\n")
assert _old in _fn
_fn = _fn.replace(_old, "    _g = GEO[nome]\n    x0 = ya + _g['pa'] + _g['aa']\n    x1 = yb - _g['pb'] - _g['ab']\n")
_o2 = "    Lp = (yb - fb - 0.075) - (ya + fa + 0.075)\n    a_ap = 0.175 "
assert _o2 in _fn
_fn = _fn.replace(_o2, "    Lp = (yb - _g['pb']) - (ya + _g['pa'])\n    a_ap = _g['aa'] ")
for a, b in [("    bw = 0.15\n", "    bw = BW\n"),
             ('lbpt_cordoalha(FCKJ, pp["sig_p0"], gradual=True)', 'lbpt_cordoalha(FCKJ, pp["sig_p0"], diam_mm=DIAM, gradual=True)'),
             ('lbpt_cordoalha(FCKJ, pp["sig_p0"], gradual=False)', 'lbpt_cordoalha(FCKJ, pp["sig_p0"], diam_mm=DIAM, gradual=False)'),
             ("SIG_PI * 98.7 / 1000", "SIG_PI * CORD['12.7'] * 1000")]:
    if a in _fn:
        _fn = _fn.replace(a, b)
exec(compile(_fn, "verificar_geo", "exec"), ns)

FACES = ns["FACES"]
P_MEIO = {"P11": 0.40, "P13": 0.60}                       # dimensão do pilar na direção da viga (geometria.py)


def geo_atual(nome):
    fa, fb = FACES[nome]
    return dict(pa=fa + 0.075, pb=fb + 0.075, aa=0.175, ab=0.175)


def geo_centralizado(nome):
    g = geo_atual(nome)
    cen = lambda b: (0.010, (b / 2 - 0.010) / 2)          # ponta a 10 mm do eixo; aparelho no meio da metade do pilar
    if nome == "V406":                                    # P11 → P13
        g["pa"], g["aa"] = cen(P_MEIO["P11"])
        g["pb"], g["ab"] = cen(P_MEIO["P13"])
    elif nome == "V405":                                  # P13 → P14 (linha 9: consolo na face, como hoje)
        g["pa"], g["aa"] = cen(P_MEIO["P13"])
    return g


GEOS = {"atual": {n: geo_atual(n) for n in FACES}, "centralizado": {n: geo_centralizado(n) for n in FACES}}

# ---- linhas de cordoalhas com 0, 2 ou 4 na mesa superior
_linhas0 = G["linhas"]


def linhas(diam, por_linha, l5, topo, H):
    lin = _linhas0(diam, por_linha, l5, False, H)
    if topo:
        lin.append(dict(y=round(H * 1000 - 100), xs=[-100, 100] if topo == 2 else [-150, -50, 50, 150], isol=0))
    return lin


G["linhas"] = linhas

LN0, HD0, ISOL0, ALCA0 = ns["LN"], ns["HD"], ns["ISOL"], ns["ALCA_A"]
PSI = dict(completa=(ns["PSI1"], 1.0), limitada=(ns["PSI2"], ns["PSI1"]))
ISOLS = [ISOL0, (0, 2000, 2000, 4000), (0, 2000, 4000, 6000), (0, 3000, 3000, 6000), (0, 3000, 5000, 7000), (0, 4000, 6000, 8000)]
ALCAS = [ALCA0, 1.50, 3.50]
N3 = (6, 25.0)
combos = sorted({c for c in itertools.product((7, 5, 4, 0), repeat=4) if c[0] >= c[1] >= c[2] >= c[3] and c[0] > 0 and c[1] > 0})
CAND = sorted(((sum(pl) + l5 + tp, pl, l5, tp) for pl in combos for l5 in (0, 2, 4) for tp in (0, 2, 4)), key=lambda c: (c[0], -c[1][0]))
INDEP = {"ELS_D_margem", "ELU", "lateral"}


def ajustar(H, dente, nivel, isol, alca, geo, fckj):
    ns["LN"], ns["HD"] = (LN0, HD0) if dente else (0.0, H)
    ns["PSI_D"], ns["PSI_F"] = PSI[nivel]
    ns["N3"], ns["ISOL"], ns["ALCA_A"], ns["GEO"], ns["FCKJ"] = N3, isol, alca, GEOS[geo], fckj


def fal(r):
    return sorted(k for k, v in r["ok"].items() if not v)


def resumo(r):
    return dict(arranjo=r["arranjo"], n=r["n_cord"], cordoalha=r["cordoalha"], bw_cm=r["bw_cm"], falhas=fal(r), ELS_D=r["usos"]["ELS_D_MPa"],
                x_d=r["usos"]["x_d"], ato_base=r["usos"]["ato_base_MPa"], ato_topo=r["usos"]["ato_topo_MPa"], icam=r["usos"]["icamento_topo_MPa"])


def descr(diam, pl, l5, tp):
    return "+".join(str(x) for x in pl) + (f" + {l5} (y {G['Y_L'][diam][4] / 10:g})" if l5 else "") + (f" + {tp} topo" if tp else "")


def trabalho(cfg):
    H, bw, diam, dente, nivel, geo, fckj = cfg
    melhor_falha, sol = None, None
    for n, pl, l5, tp in CAND:
        ajustar(H, dente, nivel, ISOL0, ALCA0, geo, fckj)
        try:
            r = rodar("V406", H, bw, diam, pl, l5, tp)
        except Exception:
            continue
        f = fal(r)
        if f and set(f) & INDEP:
            if melhor_falha is None or (len(f), r["usos"]["ELS_D_MPa"]) < (len(melhor_falha["falhas"]), melhor_falha["ELS_D"]):
                melhor_falha = dict(resumo(r), arranjo=descr(diam, pl, l5, tp), isol=list(ISOL0), alca=ALCA0)
            if not r["ok"]["ELU"] and r["usos"]["x_d"] > 0.45:
                break
            continue
        ok_var = None
        for isol in ISOLS:
            for alca in ALCAS:
                ajustar(H, dente, nivel, isol, alca, geo, fckj)
                try:
                    rv = rodar("V406", H, bw, diam, pl, l5, tp)
                except Exception:
                    continue
                fv = fal(rv)
                if not fv:
                    ok_var = (isol, alca, rv)
                    break
                if melhor_falha is None or (len(fv), rv["usos"]["ELS_D_MPa"]) < (len(melhor_falha["falhas"]), melhor_falha["ELS_D"]):
                    melhor_falha = dict(resumo(rv), arranjo=descr(diam, pl, l5, tp), isol=list(isol), alca=alca)
            if ok_var:
                break
        if ok_var:
            isol, alca, rv = ok_var
            ajustar(H, dente, nivel, isol, alca, geo, fckj)
            r5 = rodar("V405", H, bw, diam, pl, l5, tp)
            if not fal(r5):
                for x in (rv, r5):
                    x.pop("_lin", None)
                    x["arranjo"] = descr(diam, pl, l5, tp)
                    x["isolamento_mm"], x["alca_m"], x["N3"] = list(isol), alca, "6 Ø25"
                sol = dict(V406=rv, V405=r5)
                break
            if melhor_falha is None or len(fal(r5)) <= len(melhor_falha["falhas"]):
                melhor_falha = dict(resumo(r5), arranjo=descr(diam, pl, l5, tp), isol=list(isol), alca=alca, viga="V405")
    return dict(h=H, bw=bw, diam=diam, dente=dente, nivel=nivel, geo=geo, fckj=fckj, solucao=sol, melhor_falha=melhor_falha)


if __name__ == "__main__":
    t0 = time.time()
    BWS = (0.15, 0.20, 0.25, 0.30, 0.35, 0.40)
    cfgs = [(1.20, bw, d, dn, "limitada", geo, 45.0) for bw in BWS for d in (15.2, 12.7) for dn in (True, False) for geo in ("atual", "centralizado")]
    cfgs += [(1.15, bw, 15.2, True, "limitada", "atual", 45.0) for bw in BWS]
    cfgs += [(1.20, bw, 15.2, True, "limitada", "atual", 50.0) for bw in (0.15, 0.20, 0.25)]
    out = []
    with Pool(int(os.environ.get("NPROC", 2))) as p:
        for k, r in enumerate(p.imap_unordered(trabalho, cfgs, chunksize=1)):
            out.append(r)
            tag = f"h{r['h']} bw{r['bw']} Ø{r['diam']} {'dente' if r['dente'] else 'semD'} {r['nivel']} {r['geo']} fckj{r['fckj']:g}"
            if r["solucao"]:
                s = r["solucao"]["V406"]
                print(f"[{k+1}/{len(cfgs)} {time.time()-t0:.0f}s] OK {tag}: {s['arranjo']} ({s['n_cord']})", flush=True)
            else:
                mf = r["melhor_falha"] or {}
                print(f"[{k+1}/{len(cfgs)} {time.time()-t0:.0f}s] -- {tag}: {mf.get('falhas')} ELS_D {mf.get('ELS_D')} ato {mf.get('ato_base')} n {mf.get('n')}", flush=True)
            (AQ / "estudo_i130_h120_bruto.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    print("FIM", time.time() - t0)
