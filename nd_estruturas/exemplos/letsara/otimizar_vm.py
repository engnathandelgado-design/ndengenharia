"""Otimização VM meio vaso (V200–V207, V300–V307): altura do pré-moldado de 5 em 5 cm e nº de cordoalhas (inferiores + superiores),
com as mesmas verificações de calc_vm_meio_vaso.analisar (ELU, ELS, ato, montagem sem escoramento, içamento, cortante, flechas,
vibração, torção). O dente Gerber (MEF, DEC-020) foi validado para h 80: alturas menores exigem novo MEF do dente — marcado.
Saída: otimizar_vm.json."""
import json, sys, io, contextlib
from pathlib import Path
AQ = Path(__file__).parent
sys.path.insert(0, str(AQ.parents[1]))
import calc_vm_meio_vaso as VM
KG_M = 0.792
out = {}
for nome, L in VM.VAOS.items():
    tent = []
    for h in (0.70, 0.75, 0.80):
        for n_inf in (4, 6, 8):
            for n_sup in (0, 2):
                try:
                    with contextlib.redirect_stdout(io.StringIO()):
                        r = VM.analisar(h, n_inf, nome, L, n_top=n_sup)
                except Exception as e:
                    tent.append(dict(h=h, n_inf=n_inf, n_sup=n_sup, erro=str(e)[:80])); continue
                n = n_inf + n_sup
                Lp = L - 2 * VM.FOLGA
                vol = r.get("volume_m3") or r.get("V_m3")
                tent.append(dict(h=h, n_inf=n_inf, n_sup=n_sup, ok=r["ok_geral"], falhas=[k for k, v in r["ok"].items() if not v],
                                 kg_cord=round(n * Lp * KG_M, 1), vol=vol))
    oks = [t for t in tent if t.get("ok")]
    best = min(oks, key=lambda t: (t["kg_cord"] + 25 * 100 * (t["h"] - 0.70), t["h"])) if oks else None
    out[nome] = dict(atual=dict(h=VM.H_PM, n_inf=VM.N_INF, n_sup=VM.N_SUP), melhor=best, tent=tent)
    print(nome, best, [ (t['h'],t['n_inf'],t['n_sup'],t.get('falhas')) for t in tent if not t.get('ok')][:6])
(AQ / "otimizar_vm.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
