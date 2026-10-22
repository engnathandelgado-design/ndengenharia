"""Otimização I130 (V400–V402, marcas V407/V406/V405 internas): testa arranjos de cordoalhas além dos do cálculo vigente
(calc_i110_r01.py, sem alterar o JSON vigente) e escolhe o menor que passa em tudo (ato, ELS-F/D, ELU, cortante, flecha,
içamento) com a mesma folga de ELS-D (MARGEM_D) do critério vigente. Saída: otimizar_i130.json."""
import json, itertools
from pathlib import Path
AQ = Path(__file__).parent
src = (AQ / "calc_i110_r01.py").read_text(encoding="utf-8").split("\nres = {}")[0]
ns = {"__file__": str(AQ / "calc_i110_r01.py")}
exec(compile(src, "calc_i110_r01", "exec"), ns)
vig = json.loads((AQ / "i110_r01.json").read_text(encoding="utf-8"))
KG_M = 0.792                                                  # kg/m cordoalha Ø12,7 CP-190
out = {}
cands = sorted({c for c in itertools.product((7, 5, 4), repeat=4) if c[0] >= c[1] >= c[2] >= c[3]}, key=sum)
for nome, (ya, yb, cargas) in ns["VIGAS"].items():
    atual = vig[nome]["arranjo"]["n_cord"]
    Lp = vig[nome]["L_peca"]
    tent = []
    for pl in cands:
        for topo in (False, True):
            lin = ns["arranjo"](pl, topo)
            n = sum(len(l["xs"]) for l in lin)                  # conta real (arranjo() usa X4 para n ≠ 5/7)
            if n >= atual:
                continue
            try:
                r = ns["verificar"](nome, ya, yb, cargas, lin)
            except Exception as e:
                continue
            ok = r["ok_geral"] and r["ELS"]["D_base"] <= -ns["MARGEM_D"]
            okv = {k: v for k, v in r["ok"].items() if k != "ELS"}
            ok_caa1 = all(okv.values()) and r["ELS"]["F_base"] <= r["ELS"]["lim_F"] and r["ELS"]["F_topo"] <= r["ELS"]["lim_F"] and r["ELS"]["D_base_transferencia"] <= r["ELS"]["lim_F"]  # CAA I: protensão parcial, sem ELS-D
            tent.append(dict(arranjo="+".join(map(str, pl)) + (" +2 topo" if topo else ""), n=n, ok=ok, ok_caa1=ok_caa1, ELS_F=r["ELS"]["F_base"], lim_F=r["ELS"]["lim_F"],
                             falhas=[k for k, v in r["ok"].items() if not v], ELS_D=r["ELS"]["D_base"], ELU=round(r["ELU"]["Md"] / r["ELU"]["MRd"], 2)))
    ok = sorted([t for t in tent if t["ok"]], key=lambda t: t["n"])
    best = ok[0] if ok else None
    ok1 = sorted([t for t in tent if t["ok_caa1"]], key=lambda t: t["n"])
    best1 = ok1[0] if ok1 else None
    out[nome] = dict(L=Lp, atual=atual, melhor=best, melhor_caa1=best1, kg_atual=round(atual * Lp * KG_M, 1),
                     kg_melhor=round(best["n"] * Lp * KG_M, 1) if best else None, testados=len(tent),
                     menores_que_falham=sorted([t for t in tent if not t["ok"]], key=lambda t: -t["n"])[:4])
    print(nome, "atual", atual, "->", best and best["n"], "| CAA I ->", best1 and (best1["n"], best1["arranjo"]))
(AQ / "otimizar_i130.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
