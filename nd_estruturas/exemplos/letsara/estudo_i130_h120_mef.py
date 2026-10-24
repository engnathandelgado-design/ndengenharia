"""MEF não linear do dente Gerber da I130 com h 120 (opção com dente, protensão limitada, fckj 50): estudo_i130_h120.
Mesmo procedimento de estudo_i130_h110.py (calc_dentes.armaduras_i130 + nd_estruturas.mef_dente.analisar), Fd 610,5 kN."""
import json, os, sys
from pathlib import Path
AQ = Path(__file__).parent
sys.path.insert(0, str(AQ.parents[1])); sys.path.insert(0, str(AQ))
os.environ["ND_SO_DADOS"] = "1"
sys.argv = [sys.argv[0]]
import nd_estruturas.prefabricados as PF
CORD0 = dict(PF.CORD)
import calc_dentes as CD
from nd_estruturas.dente_consolo import Dente
from nd_estruturas.mef_dente import analisar
B = json.loads((AQ / "estudo_i130_h120_bruto.json").read_text(encoding="utf-8"))
sol = [r for r in B if r["solucao"] and r["dente"] and r["bw"] == 0.15 and r["fckj"] == 50.0][0]["solucao"]
rr = max(sol.values(), key=lambda r: r["dente"]["Fd"])
H = 1200
fator = CORD0["15.2"] / CORD0["12.7"]
Y = {12.7: (60, 100, 140, 180, 220), 15.2: (60, 110, 160, 210, 260)}[15.2]
pl = [int(x) for x in rr["arranjo"].split(" + ")[0].split("+")]
isol = rr["isolamento_mm"]
cord = [dict(y=y, n=n * fator, **({"isol": i} if i else {})) for y, n, i in zip(Y, pl, isol) if n]
if "topo" in rr["arranjo"]:
    cord.append(dict(y=H - 100, n=2 * fator))
SM = int(os.environ.get("SMEAR", 1))   # cordoalhas distribuídas em SM linhas de nós da mesa (modelo plano: a camada real ocupa a largura da mesa)
if SM > 1:
    m_ = float(os.environ.get("MALHA", 25.0))
    cord = [dict(c, y=c["y"] + (k - (SM - 1) / 2) * m_, n=c["n"] / SM) for c in cord for k in range(SM)]
v = dict(CD.VIGAS["I130"])
v.update(H=H, Vd=max(rr["dente"]["Fd"], v["Vd"]), Hd=max(rr["dente"]["Hd"], v["Hd"]), cord=cord, sig_pe=rr["sig_pinf"], lt=rr["lbpt_m"] * 1000)
D = Dente("I120", v["Vd"], v["Hd"], 400, v["hd"], v["ln"], v["a_apoio"], v["H"])
rd = D.dimensionar(diam_tir=v["d_tir"], diam_sus=v["d_sus"])
g = dict(H=H, b=400, bw=150, ti=v["ti"], mi=80, ts=v["ts"], ms=80, hd=v["hd"], ln=v["ln"], a_apoio=v["a_apoio"], x_mac=v["x_mac"], l_apoio=v["l_apoio"])
arm = CD.armaduras_i130(v, rd["adotado"])
arm = [a for a in arm if not (a.get("nome") == "pele" and a["pos"] > H - 100)]
m = analisar(g, arm, cord, v["Vd"], v["Hd"], fck=50.0, malha=float(os.environ.get("MALHA",25.0)), Ls=v["Ls"], xP=v["xP"], passos=int(os.environ.get("PASSOS",500)), du=float(os.environ.get("DU",0.05)), rampa_fim=v["rampa_fim"],
             robusto=v["robusto"], sig_pe=v["sig_pe"], lt=v["lt"], saida_png=str(AQ / os.environ.get("PNG","mef_dente_I130_h120.png")), titulo="Dente Gerber I130 com h 120 (estudo)")
print("LIM", m["limite"], "PICO", m["V_pico_kN"], "lt", v["lt"]); m.pop("curva", None)
out = dict(geometria=dict(H=H, hd=v["hd"], ln=v["ln"], recorte_mm=H - v["hd"], bw=150), Fd=v["Vd"], Hd=v["Hd"], calculo=rd["adotado"],
           MEF=dict(Vu_kN=m["Vu_kN"], FS=m["FS"], ok=m["Vu_kN"] >= 1.06 * v["Vd"], protensao_ok=m.get("protensao_ok")), cordoalhas=cord)
(AQ / os.environ.get("SAIDA","estudo_i130_h120_mef.json")).write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
print("MEF", out["MEF"], rd["adotado"].get("ok"))
