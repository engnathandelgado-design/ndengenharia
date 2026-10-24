"""Estudo (24/10/2026, pedido do Nathan): I130 das V400 (V407), V401 (V406) e V402 (V405) com seção NOVA, h 120 fixo,
dente 78 × 35 e maciço das pontas 40 × 120 (1,40 m) como hoje. Só cálculo: não altera pranchas, modelo nem i110_r01.json.
Saída: estudo_i130_secao_nova.json.

Seção nova: alma 20 (hoje 15); mesa inferior 40 × 35 + mísula 8 (hoje 40 × 25 + 8: a "almofada" sobe 10 cm); mesa superior
40 × ts + mísula 8 com ts varrido em 22 / 18 / 15 / 12 (hoje 22), mantendo h 120 e as larguras 40.
Com a mesa inferior de 35 cabem mais linhas de cordoalha a largura cheia (7 por linha, espaçamento livre ≥ 2φ / 20 mm,
NBR 6118:2023 18.6.2.3): Ø12,7 y 6/10/14/18/22/26/30 cm; Ø15,2 y 6/11/16/21/26/31 cm.

Zona maciça (pergunta 2): trecho retangular 40 × 120 de comprimento ZONA centrado em cada TS-01 (linhas 3, 5, 6, 7, 8:
cargas_concentradas de calc_i110_r01.VIGAS). Entra na verificação como seção retangular nesses trechos (ELS, ato do vão é
o da seção I, a favor) e o peso extra entra como carga concentrada permanente no ponto da TS e no peso de içamento.

Critérios: os de estudo_i130_h120 / h120_127 (ato 0,7 fckj e 1,2 fctm,j com γp 1,1, NBR 6118:2023 17.2.4.3.2; ELU com
x/d ≤ 0,45; ELS na protensão LIMITADA, Tab. 13.4, com a margem de projeto −0,25 MPa no ELS-D; cortante 17.4.2.2 com bw 20;
içamento; flechas com fluência e limites da NBR 9062:2017 Tab. 9; estabilidade lateral NBR 9062:2017 6.1; dente 7.4).
"""
import json, os, sys, time, itertools
from pathlib import Path
from multiprocessing import Pool
AQ = Path(__file__).parent
_h110 = (AQ / "estudo_i130_h110.py").read_text(encoding="utf-8")
_h110 = _h110.replace("    assert a in src, a\n    src = src.replace(a, b)", "    src = src.replace(a, b)")
_h110 = _h110.replace('    ns["CORD"] = dict(CORD0, **{"12.7": area})', '    ns["CORD"] = dict(CORD0, **{"12.7": area})\n    ns["A_C"] = area')
_src = (AQ / "estudo_i130_h120.py").read_text(encoding="utf-8").split('if __name__ == "__main__":')[0]
_src = _src.replace('(AQ / "estudo_i130_h110.py").read_text(encoding="utf-8")', "_H110_SRC")
_src = _src.replace("assert _old in _fn\n", "").replace("assert _o2 in _fn\n", "")
M = {"__file__": str(AQ / "estudo_i130_h120.py"), "__name__": "estudo_i130_h120_lib", "_H110_SRC": _h110}
exec(compile(_src, "estudo_i130_h120", "exec"), M)
G, ns = M["G"], M["ns"]
ajustar, fal, resumo, ISOLS, ALCAS, ISOL0, ALCA0, INDEP = (M[k] for k in ("ajustar", "fal", "resumo", "ISOLS", "ALCAS", "ISOL0", "ALCA0", "INDEP"))

# ---- verificar() com a zona maciça nas TS-01
_fn = M["_fn"]
for a, b in [("        s = SECP if xp < X_MAC or xp > Lp - X_MAC else sec\n",
              "        s = SECP if xp < X_MAC or xp > Lp - X_MAC or any(abs(xp - a - a_ap) < ZONA / 2 for a in xs) else sec\n"),
             ("    peso = g1 * Lp + g_mac * X_MAC * 2", "    peso = g1 * Lp + g_mac * X_MAC * 2 + g_mac * ZONA * len(xs)")]:
    assert a in _fn, a
    _fn = _fn.replace(a, b)
exec(compile(_fn, "verificar_zona", "exec"), ns)
ns["ZONA"] = 0.0
P_G0 = ns["P_g"]

SEC_HOJE = dict(bs=0.40, ts=0.22, ms=0.08, bi=0.40, ti=0.25, mi=0.08)
Y_NOVA = {12.7: (60, 100, 140, 180, 220, 260, 300), 15.2: (60, 110, 160, 210, 260, 310)}
XS = {7: [-150, -100, -50, 0, 50, 100, 150], 5: [-100, -50, 0, 50, 100], 4: [-100, -50, 50, 100], 2: [-50, 50]}


def linhas(diam, por_linha, l5, topo, H):
    """por_linha: nº de cordoalhas por linha, de baixo para cima (Y_NOVA). Linhas acima da 4ª isoladas como a 4ª."""
    isol = list(ns["ISOL"])
    lin = [dict(y=y, xs=list(XS[n]), isol=isol[min(k, 3)]) for k, (y, n) in enumerate(zip(G["Y_L"][diam], por_linha)) if n]
    if topo:
        lin.append(dict(y=round(H * 1000 - 100), xs=[-100, 100] if topo == 2 else [-150, -50, 50, 150], isol=0))
    return lin


G["linhas"] = linhas


def secao(nova, ts):
    G["SECAO"] = dict(bs=0.40, ts=ts, ms=0.08, bi=0.40, ti=0.35, mi=0.08) if nova else dict(SEC_HOJE)
    G["Y_L"] = dict(Y_NOVA) if nova else {12.7: (60, 100, 140, 180, 220), 15.2: (60, 110, 160, 210, 260)}


def cand(nova, diam):
    """Arranjos por nº total crescente; mesma contagem → centroide mais baixo primeiro."""
    if not nova:
        out = [(sum(pl) + l5 + tp, pl + ((l5,) if l5 else ()), tp) for pl in itertools.product((7, 5, 4, 0), repeat=4)
               if pl[0] >= pl[1] >= pl[2] >= pl[3] and pl[1] for l5 in (0, 2, 4) for tp in (0, 2, 4)]
    else:
        nl = len(Y_NOVA[diam])
        out = []
        for pl in itertools.product((7, 5, 4, 2, 0), repeat=nl):
            if not (pl[0] and pl[1]) or any(pl[k] < pl[k + 1] for k in range(nl - 1)):
                continue
            pl = tuple(x for x in pl if x)
            for tp in (0, 2, 4):
                out.append((sum(pl) + tp, pl, tp))
    Y = Y_NOVA[diam] if nova else (60, 100, 140, 180, 220) if diam == 12.7 else (60, 110, 160, 210, 260)
    return sorted(set(out), key=lambda c: (c[0], sum(n * y for n, y in zip(c[1], Y)) / max(1, sum(c[1]))))


def descr(pl, tp):
    return "+".join(str(x) for x in pl) + (f" + {tp} topo" if tp else "")


def rodar(nome, nova, ts, zona, diam, pl, tp):
    secao(nova, ts)
    ns["ZONA"] = zona
    sec = G["config"](1.20, 0.20 if nova else 0.15, diam)
    g_mac = (ns["SECP"].A - sec.A) * 25
    ns["P_g"] = P_G0 + g_mac * zona                     # peso do trecho maciço como carga permanente no ponto da TS-01
    r = G["rodar"](nome, 1.20, 0.20 if nova else 0.15, diam, pl, 0, tp)
    S = G["SECAO"]
    r["mesas"] = f"sup 40×{S['ts']*100:g} + mísula 8; inf 40×{S['ti']*100:g} + mísula 8; alma {r['bw_cm']}"
    r["arranjo"] = descr(pl, tp)
    r["zona_macica_m"] = zona
    r["secao"] = dict(A_m2=round(sec.A, 4), I_m4=round(sec.I, 5), yc_m=round(sec.yc, 3), g1_kNm=round(sec.A * 25, 2),
                      g_zona_kN=round(g_mac * zona, 1))
    return r


GRUPOS = {"V407": ["V407"], "V406+V405": ["V406", "V405"]}
NOMES = {"V407": "V400", "V406": "V401", "V405": "V402"}


def trabalho(cfg):
    grupo, nova, ts, zona, diam, nivel, fckj = cfg
    vigas = GRUPOS[grupo]
    melhor, sol, n_aval = None, None, 0
    for n, pl, tp in cand(nova, diam):
        if grupo != "V407" and n < 16:
            continue
        ajustar(1.20, True, nivel, ISOL0, ALCA0, "atual", fckj)
        try:
            r = rodar(vigas[0], nova, ts, zona, diam, pl, tp)
            n_aval += 1
        except Exception:
            continue
        f = fal(r)
        if f and set(f) & INDEP:
            if melhor is None or (len(f), r["usos"]["ELS_D_MPa"]) < (len(melhor["falhas"]), melhor["ELS_D"]):
                melhor = dict(resumo(r), arranjo=descr(pl, tp), isol=list(ISOL0), alca=ALCA0, viga=vigas[0])
            continue
        achou = None
        for isol in ISOLS:
            for alca in ALCAS:
                ajustar(1.20, True, nivel, isol, alca, "atual", fckj)
                try:
                    rs = [rodar(v, nova, ts, zona, diam, pl, tp) for v in vigas]
                    n_aval += len(vigas)
                except Exception:
                    rs = []
                if not rs:
                    continue
                fv = sorted({k for x in rs for k in fal(x)})
                if not fv:
                    achou = (isol, alca, rs)
                    break
                if melhor is None or (len(fv), rs[0]["usos"]["ELS_D_MPa"]) < (len(melhor["falhas"]), melhor["ELS_D"]):
                    melhor = dict(resumo(rs[0]), falhas=fv, arranjo=descr(pl, tp), isol=list(isol), alca=alca, viga=vigas[0])
            if achou:
                break
        if achou:
            isol, alca, rs = achou
            for x in rs:
                x["isolamento_mm"], x["alca_m"], x["N3"] = list(isol), alca, "6 Ø25"
            sol = {v: x for v, x in zip(vigas, rs)}
            break
    return dict(grupo=grupo, secao="nova" if nova else "hoje", ts=ts, zona=zona, diam=diam, nivel=nivel, fckj=fckj,
                solucao=sol, melhor_falha=melhor, n_aval=n_aval)


def _limpa(o):
    if isinstance(o, dict):
        return {k: _limpa(v) for k, v in o.items() if k != "_lin"}
    if isinstance(o, list):
        return [_limpa(v) for v in o]
    return o


if __name__ == "__main__":
    t0 = time.time()
    cfgs = []
    for g in GRUPOS:
        for diam in (15.2, 12.7):
            cfgs.append((g, False, 0.22, 0.0, diam, "limitada", 50.0))               # referência (seção de hoje, alma 15)
            for ts in (0.22, 0.18, 0.15, 0.12):
                for fj in (45.0, 50.0):
                    cfgs.append((g, True, ts, 0.0, diam, "limitada", fj))
            cfgs.append((g, True, 0.15, 1.0, diam, "limitada", 50.0))              # zona maciça de 1,0 m nas TS-01
            cfgs.append((g, True, 0.15, 0.5, diam, "limitada", 50.0))              # zona maciça de 0,5 m
            cfgs.append((g, True, 0.15, 0.0, diam, "completa", 50.0))              # só informação
    if len(sys.argv) > 1:
        cfgs = cfgs[: int(sys.argv[1])]
    out = []
    with Pool(int(os.environ.get("NPROC", 2))) as p:
        for k, r in enumerate(p.imap_unordered(trabalho, cfgs, chunksize=1)):
            out.append(_limpa(r))
            tag = f"{r['grupo']} {r['secao']} ts{r['ts']} zona{r['zona']} Ø{r['diam']} {r['nivel']} fckj{r['fckj']:g}"
            if r["solucao"]:
                s = list(r["solucao"].values())[0]
                print(f"[{k+1}/{len(cfgs)} {time.time()-t0:.0f}s] OK {tag}: {s['arranjo']} ({s['n_cord']}) aval {r['n_aval']}", flush=True)
            else:
                mf = r["melhor_falha"] or {}
                print(f"[{k+1}/{len(cfgs)} {time.time()-t0:.0f}s] -- {tag}: {mf.get('arranjo')} {mf.get('falhas')} ELS_D {mf.get('ELS_D')}", flush=True)
            (AQ / "estudo_i130_secao_nova.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    print("FIM", time.time() - t0)
