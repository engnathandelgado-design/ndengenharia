"""Roda uma variante de dente (sobrescreve geometria/cordoalhas de calc_dentes.VIGAS) e grava mef_var_<nome>.json."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.argv = [sys.argv[0], "NADA"] + sys.argv[1:]
import calc_dentes as C
from nd_estruturas.dente_consolo import Dente
from nd_estruturas.mef_dente import analisar
nome, tag, over = sys.argv[2], sys.argv[3], json.loads(sys.argv[4])
v = dict(C.VIGAS[nome]); v.update(over)
D = Dente(nome, v["Vd"], v["Hd"], 400, v["hd"], v["ln"], v["a_apoio"], v["H"])
r = D.dimensionar(diam_tir=v["d_tir"], diam_sus=v["d_sus"])
g = dict(H=v["H"], b=400, bw=150, ti=v["ti"], mi=80, ts=v["ts"], ms=80, hd=v["hd"], ln=v["ln"], a_apoio=v["a_apoio"],
         x_mac=v["x_mac"], l_apoio=v["l_apoio"])
m = analisar(g, C.armaduras(v, r), v["cord"], v["Vd"], v["Hd"], fck=50.0, malha=25.0, Ls=3000.0, xP=1300.0, passos=500,
             saida_png=str(C.AQUI / f"mef_dente_{nome}_{tag}.png"), titulo=f"Dente Gerber {nome} ({tag})")
m["ok"] = m["Vu_kN"] >= 1.06 * v["Vd"]
(C.AQUI / f"mef_var_{nome}_{tag}.json").write_text(json.dumps(dict(over=over, calculo=r, mef=m), indent=1, ensure_ascii=False, default=str))
print(nome, tag, "Vu", m["Vu_kN"], "pico", m["V_pico_kN"], m["limite"], "FS", m["FS"], "prot", m["protensao_ok"])
