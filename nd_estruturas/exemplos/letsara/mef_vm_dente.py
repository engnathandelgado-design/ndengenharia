"""MEF não linear do dente Gerber da VM meio vaso (rev04): alma 25 + aba 15 x 20, h 65, dente 35 x 35, ponta maciça 40 x 100."""
import json, os, sys
from pathlib import Path
AQ = Path(__file__).parent
sys.path.insert(0, str(AQ.parents[1]))
os.environ["ND_SO_DADOS"] = "1"
from nd_estruturas.dente_consolo import Dente, AREA
from nd_estruturas.mef_dente import analisar
import calc_dentes as CD

HD_ = int(sys.argv[1]) if len(sys.argv) > 1 else 350
HH = int(sys.argv[2]) if len(sys.argv) > 2 else 650
INF = sys.argv[3] if len(sys.argv) > 3 else "2x10"          # armadura inferior passiva no corpo: "nxØ"
n_inf, d_inf = int(INF.split("x")[0]), float(INF.split("x")[1])
SUF = "" if INF == "2x10" else f"_inf{INF}"
Vd = round(1.2 * 440.5, 1)                     # γn 1,2 x Vd do apoio interno (continuidade)
v = dict(Vd=Vd, Hd=round(0.16 * Vd, 1), H=HH, ti=10, ts=200, hd=HD_, ln=350, a_apoio=156, x_mac=1000, l_apoio=150,
         cord=[dict(y=50, n=2, isol=1500), dict(y=50, n=2), dict(y=120, n=4), dict(y=190, n=2), dict(y=HH - 50, n=2)],
         estribo=(10.0, 75), sup=2 * AREA[12.5], inf=n_inf * AREA[d_inf], d_tir=16.0, d_sus=16.0)
D = Dente("VM-MV", v["Vd"], v["Hd"], 400, v["hd"], v["ln"], v["a_apoio"], v["H"], fck=40.0)
r = D.dimensionar(diam_tir=16.0, diam_sus=16.0)
g = dict(H=HH, b=400, bw=250, bi=250, ti=10, mi=1, ts=200, ms=1, hd=v["hd"], ln=v["ln"], a_apoio=v["a_apoio"], x_mac=v["x_mac"], l_apoio=v["l_apoio"])
m = analisar(g, CD.armaduras(v, r), v["cord"], v["Vd"], v["Hd"], fck=40.0, malha=25.0, Ls=3000.0, xP=1300.0, passos=500, robusto=True, rampa_fim=True,
             saida_png=str(AQ / f"mef_dente_VM-MV_{HH}_{HD_}{SUF}.png"), titulo=f"Dente Gerber VM meio vaso h{HH} (dente {HD_} x 350)")
m["ok"] = m["Vu_kN"] >= 1.06 * v["Vd"]
out = dict(geometria=g, Vd=v["Vd"], Hd=v["Hd"], calculo=r, mef=m)
(AQ / f"mef_vm_dente_{HH}_{HD_}{SUF}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
print(json.dumps(r["adotado"], ensure_ascii=False)); print({k: m[k] for k in m if k in ("Vu_kN", "ok", "modo", "FS")})
