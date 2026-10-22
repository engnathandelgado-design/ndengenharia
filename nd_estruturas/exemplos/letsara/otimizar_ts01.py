"""Otimização vigas de cobertura I90 (V407–V420, ex-TS-01): nº de cordoalhas (pares simétricos) com a mesma seção, cargas e
verificações de ts01_dados.py (verificar_viga_pretracionada + transitórias + alça). Altura/largura NÃO variam: a altura amarra
os níveis da cobertura escondida (folga de 15 cm na platibanda) e a largura é a da fôrma. Saída: otimizar_ts01.json."""
import json, sys, os
from pathlib import Path
AQ = Path(__file__).parent
sys.path.insert(0, "/home/claude/letsara/pranchas")
cwd = os.getcwd(); os.chdir("/home/claude/letsara/pranchas")
import ts01_dados as T
os.chdir(cwd)
from nd_estruturas.prefabricados import verificar_viga_pretracionada, transitorias_viga, GAMA_P_ATO
P = T.P
KG_M = 0.792
out = dict(atual=dict(n=P["n_cord"], y_mm=P["y_cord"]), tent=[])
for n in range(4, P["n_cord"] + 1, 2):
    n2 = 2 if n >= 6 else 0                                  # 2 cordoalhas na 2ª camada (y2) e o resto em y1, como hoje
    y = ((n - n2) * P["y1"] + n2 * P["y2"]) / n
    R = verificar_viga_pretracionada(T.sec, T.L_calc, T.car, T.C, n, y_cord=y / 1000, fckj=P["fckj"], sig_pi=P["sig_pi"])
    ativas = n - (2 if n >= 6 else 0)                         # 2 isoladas 3 m nas pontas (como hoje)
    y_at = P["y1"] if ativas == n - n2 or n2 == 0 else y
    TR = transitorias_viga(T.sec, T.L / 1000, GAMA_P_ATO * R.linhas["P0_kN"] * ativas / n, T.sec.yc - y_at / 1000, T.C, P["fckj"],
                           [a / 1000 for a in P["alcas"]], [a / 1000 for a in P["estoque"]])
    ok = R.ok and TR["desforma_montagem"]["ok"] and TR["estoque_transporte"]["ok"]
    fal = [k for k, v in (R.verificacoes.items() if hasattr(R, "verificacoes") else []) if isinstance(v, dict) and not v.get("ok", True)]
    out["tent"].append(dict(n=n, y_mm=round(y, 1), ok=ok, R_ok=R.ok, transit=TR["desforma_montagem"]["ok"] and TR["estoque_transporte"]["ok"],
                            linhas={k: R.linhas[k] for k in list(R.linhas)[:14]}, kg_por_viga=round(n * T.L / 1000 * KG_M, 1)))
    print(n, ok, R.ok, round(y, 1))
oks = [t for t in out["tent"] if t["ok"]]
out["melhor"] = min(oks, key=lambda t: t["n"]) if oks else None
(AQ / "otimizar_ts01.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
