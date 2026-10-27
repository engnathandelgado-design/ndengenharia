"""Letsara rev04 — consolos dos pilares pela NBR 9062:2017 7.3 (cálculo em calc_nbr9062.py, função consolo):
γn (7.3.1.1), Hd = 0,16 Fd no elastômero (7.3.9), modelo por a/d (7.3.2.2), tirante 7.3.5 em ALÇAS HORIZONTAIS com
a2 ≥ c + 3,5Ø (Ø < 20) / c + 5Ø (Ø ≥ 20) (7.3.3), biela 7.3.4, costura 7.3.6, estribos verticais 7.3.7.
Regra ND: altura do consolo = recorte do dente da viga − neoprene, fundo do consolo alinhado ao fundo da viga.
rev04: sem CP-VT (sem vigas de travamento); CP-MEZ recebe o dente 35 × 35 da VM meio vaso (h 29, projeção 35).
Grava consolos.json no formato lido pelas pranchas dos pilares.
"""
import json
from pathlib import Path

AQ = Path(__file__).parent
N9 = json.loads((AQ / "nbr9062.json").read_text(encoding="utf-8"))
NEO = {"CP-I120": (300, 200, 31), "CP-MEZ": (200, 200, 21), "CP-VB": (60, 100, 10), "CT-I120": (300, 150, 10)}     # (b na largura, a na projeção, h) mm — NEO-2 / NEO-5F / NEO-6 / NEO-3C (rev12)
res = {}
for c in N9["consolos"]:
    nome = c["consolo"]
    if not nome.startswith(("CP-", "CT-")):
        continue
    res[nome] = dict(onde=c["onde"], b_m=c["b_m"], proj_m=c["proj_m"], a_m=c["a_m"], h_consolo_m=c.get("h_ext_m", c["h_m"]), misula_m=c.get("misula_m", 0.0), h_total_m=c["h_m"],
                     d_m=c["d_m"], a_d=c["a_d"], tipo=c["modelo"], gama_n=c["gama_n"], Vd_kN=c["Vd_kN"], Fd_kN=c["Fd_kN"], Hd_kN=c["Hd_kN"],
                     tau_wd_MPa=c["tau_wd_MPa"], tau_wu_MPa=c["tau_wu_MPa"], As_tir_cm2=c["As_tir_cm2"], tirante=c["tirante"],
                     n_ramos=int(c["tirante"].split("(")[1].split()[0]), d_tir=float(c["tirante"].split("Ø")[1].split()[0].replace(",", ".")),
                     a2_cm=c["a2_cm"], costura=c["costura"], estribos_verticais_cm2=c["estribos_verticais_cm2"], neoprene_mm=NEO[nome], ok=c["ok_geral"],
                     norma=c["norma"])
    print(f"{nome:8s} h={c['h_m']} a/d={c['a_d']} τ={c['tau_wd_MPa']}/{c['tau_wu_MPa']} As={c['As_tir_cm2']} → {c['tirante']} ok={c['ok_geral']}")
(AQ / "consolos.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
