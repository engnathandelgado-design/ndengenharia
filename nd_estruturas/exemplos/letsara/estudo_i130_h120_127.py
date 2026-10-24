"""Estudo (24/10/2026, pergunta do Nathan): V400 (V407), V401 (V406) e V402 (V405) com h 120 e cordoalha Ø12,7 (CP-190 RB)
no lugar da Ø15,2 adotada na rev09 (DEC-054). Mesmo procedimento de estudo_i130_h120.py (verificar() com geometria de
apoio atual, flechas com fluência, estabilidade lateral, protensão LIMITADA por padrão). Só cálculo — não altera
pranchas, modelo nem i110_r01.json. Saída: estudo_i130_h120_127.json.

Capacidade da mesa inferior (40 cm, Y_L Ø12,7 = 60/100/140/180/220 mm): 4 linhas de 7 + 4 na 5ª linha = 32 na mesa
inferior (espaçamento horizontal e vertical livres ≥ 2φ / 20 mm, NBR 6118:2023 18.6.2.3), + 2 ou 4 no topo → máx. 36.
"""
import json, os, sys, time
from pathlib import Path
from multiprocessing import Pool
AQ = Path(__file__).parent
# calc_i110_r01 já foi atualizado para Ø15,2/h 120 (DEC-054, globais DIAM e A_C): as substituições de texto dos estudos
# anteriores viram condicionais e o config() passa a ajustar também A_C, para valer a cordoalha de cada rodada.
_h110 = (AQ / "estudo_i130_h110.py").read_text(encoding="utf-8")
_h110 = _h110.replace("    assert a in src, a\n    src = src.replace(a, b)", "    src = src.replace(a, b)")
_h110 = _h110.replace('    ns["CORD"] = dict(CORD0, **{"12.7": area})', '    ns["CORD"] = dict(CORD0, **{"12.7": area})\n    ns["A_C"] = area')
_src = (AQ / "estudo_i130_h120.py").read_text(encoding="utf-8").split('if __name__ == "__main__":')[0]
_src = _src.replace('(AQ / "estudo_i130_h110.py").read_text(encoding="utf-8")', "_H110_SRC")
_src = _src.replace("assert _old in _fn\n", "").replace("assert _o2 in _fn\n", "")
M = {"__file__": str(AQ / "estudo_i130_h120.py"), "__name__": "estudo_i130_h120_lib", "_H110_SRC": _h110}
exec(compile(_src, "estudo_i130_h120", "exec"), M)
ns, rodar, ajustar, fal, resumo, descr = M["ns"], M["rodar"], M["ajustar"], M["fal"], M["resumo"], M["descr"]
CAND, ISOLS, ALCAS, ISOL0, ALCA0, INDEP = M["CAND"], M["ISOLS"], M["ALCAS"], M["ISOL0"], M["ALCA0"], M["INDEP"]
GRUPOS = {"V407": ["V407"], "V406+V405": ["V406", "V405"]}     # V401 e V402 na mesma pista → mesmo arranjo
NOMES = {"V407": "V400", "V406": "V401", "V405": "V402"}


def trabalho(cfg):
    grupo, bw, diam, nivel, fckj = cfg
    vigas = GRUPOS[grupo]
    H, dente, geo = 1.20, True, "atual"
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
                melhor = dict(resumo(r), arranjo=descr(diam, pl, l5, tp), isol=list(ISOL0), alca=ALCA0, viga=vigas[0])
            if not r["ok"]["ELU"] and r["usos"]["x_d"] > 0.45:
                break
            continue
        achou = None
        for isol in ISOLS:
            for alca in ALCAS:
                ajustar(H, dente, nivel, isol, alca, geo, fckj)
                rs = []
                try:
                    for v in vigas:
                        rs.append(rodar(v, H, bw, diam, pl, l5, tp))
                except Exception:
                    rs = []
                if not rs:
                    continue
                fv = sorted({k for x in rs for k in fal(x)})
                if not fv:
                    achou = (isol, alca, rs)
                    break
                if melhor is None or (len(fv), rs[0]["usos"]["ELS_D_MPa"]) < (len(melhor["falhas"]), melhor["ELS_D"]):
                    melhor = dict(resumo(rs[0]), falhas=fv, arranjo=descr(diam, pl, l5, tp), isol=list(isol), alca=alca, viga=vigas[0])
            if achou:
                break
        if achou:
            isol, alca, rs = achou
            for x in rs:
                x.pop("_lin", None)
                x["arranjo"], x["isolamento_mm"], x["alca_m"], x["N3"] = descr(diam, pl, l5, tp), list(isol), alca, "6 Ø25"
            sol = {v: x for v, x in zip(vigas, rs)}
            break
    return dict(grupo=grupo, bw=bw, diam=diam, nivel=nivel, fckj=fckj, solucao=sol, melhor_falha=melhor)


if __name__ == "__main__":
    t0 = time.time()
    cfgs = [(g, bw, 12.7, "limitada", fj) for g in GRUPOS for fj in (45.0, 50.0) for bw in (0.15, 0.20, 0.25)]
    cfgs += [(g, 0.15, 15.2, "limitada", fj) for g in GRUPOS for fj in (45.0, 50.0)]          # referência rev09
    cfgs += [(g, 0.15, 12.7, "completa", 50.0) for g in GRUPOS]                                 # só informação
    out = []
    with Pool(int(os.environ.get("NPROC", 4))) as p:
        for k, r in enumerate(p.imap_unordered(trabalho, cfgs, chunksize=1)):
            out.append(r)
            tag = f"{r['grupo']} bw{r['bw']} Ø{r['diam']} {r['nivel']} fckj{r['fckj']:g}"
            if r["solucao"]:
                s = list(r["solucao"].values())[0]
                print(f"[{k+1}/{len(cfgs)} {time.time()-t0:.0f}s] OK {tag}: {s['arranjo']} ({s['n_cord']})", flush=True)
            else:
                mf = r["melhor_falha"] or {}
                print(f"[{k+1}/{len(cfgs)} {time.time()-t0:.0f}s] -- {tag}: {mf.get('arranjo')} {mf.get('falhas')} ELS_D {mf.get('ELS_D')} ato {mf.get('ato_base')}", flush=True)
            (AQ / "estudo_i130_h120_127.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    print("FIM", time.time() - t0)
