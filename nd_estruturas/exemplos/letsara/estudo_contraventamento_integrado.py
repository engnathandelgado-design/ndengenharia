"""Letsara rev05 — otimização do contraventamento no MODELO INTEGRADO (modelo_integrado_r05.py): cada variante de X
(vãos e largura do painel) é analisada com toda a estrutura (pilares, TS-01, I130, VB, mezanino rígido, terças Z
contínuas, correntes, tirantes, diagonais de ancoragem) nas 33 combinações ELU com vento NBR 6123 completo.
Saída: estudo_contraventamento_integrado.json."""
import json, math, sys
from multiprocessing import Pool
from pathlib import Path
AQ = Path(__file__).resolve().parent
sys.path.insert(0, str(AQ)); sys.path.insert(0, str(AQ.parents[1]))
import modelo_integrado_r05 as M
from nd_estruturas.metalica_fria import barra_redonda_tracao_Rd

VARIANTES = [((), 8), ((1, 6), 2), ((1, 6), 8), ((6, 7), 8), ((0, 7), 8), ((0, 1, 6, 7), 8), ((5, 6, 7), 8),
             ((3, 4, 5, 6, 7), 8), ((3, 4, 5, 6, 7), 4), ((3, 4, 5, 6, 7), 16), ((1, 3, 5, 7), 8), ((2, 3, 4, 5, 6, 7), 8),
             ((1, 2, 5, 6, 7), 8), (tuple(range(8)), 8)]


def avaliar(v):
    vaos, n = v
    cfg = dict(vaos_x=list(vaos), painel=n, A_x=math.pi * 0.016 ** 2 / 4)
    res = M.analisar(cfg)
    env = M.envoltoria(res)
    T = env.get("X", {}).get("max", 0.0)
    d = next((dd for dd in (12.5, 16.0, 19.0, 22.0) if barra_redonda_tracao_Rd(dd) >= T), 25.0)
    # geometria do X
    xs = lambda lst: [lst[i] for i in sorted(set(list(range(0, len(lst), n)) + [len(lst) - 1]))]
    Ld = []
    for k in vaos:
        Ly = M.Y[k + 1] - M.Y[k]
        for lad in (xs(M.X_ESQ), xs(M.X_DIR)):
            for a, b in zip(lad[:-1], lad[1:]):
                Ld += [math.hypot(b - a, Ly)] * 2
    kg = sum(Ld) * math.pi * (d / 1000) ** 2 / 4 * 7850
    nd = len(Ld)
    custo = 14 * kg + (55 + 60 + 80) * nd
    return dict(vaos=[f"{k+1}-{k+2}" for k in vaos], painel=n, n_diagonais=nd, diametro=d, kg_X=round(kg), T_X=T, custo_X=round(custo),
                terca_it=env["terca"]["it"], terca_pior=env["terca"], pilar_uso=env["pilar_uso_max"], M_base=env["M_base_max"],
                ST1P=env["ST1P_verif"], ST1P_reprovados=env["ST1P_reprovados_max"], corrente=env["usos"]["corrente"],
                diagonal=env["usos"]["diagonal"], TS01_M_lateral=env["TS01_M_lateral"])


if __name__ == "__main__":
    with Pool(2) as p:
        out = p.map(avaliar, VARIANTES, chunksize=1)
    (AQ / "estudo_contraventamento_integrado.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    for r in out:
        print(r["vaos"], r["painel"], f"X {r['n_diagonais']}×Ø{r['diametro']} {r['kg_X']} kg T {r['T_X']}", "terça", r["terca_it"], "pilar", r["pilar_uso"],
              "Mb", r["M_base"], "ST1P", r["ST1P"]["it"], r["ST1P_reprovados"], "corr", r["corrente"], "diag", r["diagonal"], "R$", r["custo_X"], flush=True)
