"""Letsara — dentes Gerber de todas as vigas e consolos que os recebem, com verificação por MEF não linear 2D.

Dimensionamento: nd_estruturas.dente_consolo (NBR 9062:2017 7.3/7.4 + PCI 5.6, adota a maior armadura).
Verificação: nd_estruturas.mef_dente (OpenSeesPy, ASDConcrete3D em estado plano, armaduras e cordoalhas como
barras aderentes, resistências de cálculo, ruptura por 10‰ no aço ou 3,5‰ no concreto).
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from nd_estruturas.dente_consolo import Dente, consolo, AREA
from nd_estruturas.mef_dente import analisar

AQUI = Path(__file__).parent
import os
SO = sys.argv[1:]            # opcional: nomes das vigas a rodar no MEF
SO_DADOS = bool(os.environ.get("ND_SO_DADOS"))   # importado por outro script: não roda MEF nem grava

# geometria (mm) — mesma fôrma I: largura 400, alma 150, chanfros 80
VIGAS = {
    # rev03: TS-01 sem dente (apoio direto no assento do pilar e no topo da viga central).
    # I130 (rev03, antes I110): dente de 780 (60% da altura), 14 das 26 cordoalhas (linhas 140 e 180) isoladas por 2 m nas pontas
    "I130": dict(Vd=472.0, Hd=76.0, H=1300, ti=250, ts=220, hd=780, ln=350, a_apoio=175, x_mac=1400, l_apoio=250,
                 cord=[dict(y=60, n=6), dict(y=100, n=6), dict(y=140, n=7, isol=2000), dict(y=180, n=7, isol=2000)], estribo=(8.0, 150),
                 sup=4 * AREA[12.5], inf=2 * AREA[12.5], d_tir=20.0, d_sus=16.0, Ls=3600.0, xP=1600.0, rampa_fim=True, robusto=True),
    "MEZ-I90": dict(Vd=383.0, Hd=65.0, H=900, ti=150, ts=120, hd=450, ln=300, a_apoio=150, x_mac=1200, l_apoio=200,
                    cord=[dict(y=75, n=7), dict(y=117, n=1)], estribo=(8.0, 150), sup=4 * AREA[12.5], inf=2 * AREA[10.0],
                    d_tir=20.0, d_sus=16.0),
    # opção do mezanino com laje h20+5: I70 (mesma fôrma, mesas 12/15), dente de 425 (61%)
    "MEZ-I70": dict(Vd=345.0, Hd=58.0, H=700, ti=150, ts=120, hd=425, ln=300, a_apoio=150, x_mac=1000, l_apoio=200,
                    cord=[dict(y=75, n=7), dict(y=117, n=3)], estribo=(8.0, 150), sup=4 * AREA[12.5], inf=2 * AREA[10.0],
                    d_tir=20.0, d_sus=16.0),
}
NOTAS_H = {"MEZ-I70": "Hd = 0,16 Vd + diafragma",
           "I130": "Hd = 0,16 Vd (neoprene) ≥ 1,4 × 23 kN do modelo global (rev03)",
           "MEZ-I90": "Hd = 0,16 Vd + diafragma"}


def armaduras(v, r):
    H, hd, ln = v["H"], v["hd"], v["ln"]
    yd = H - hd
    a = r["adotado"]
    arm = [dict(tipo="h", nome="tirante", pos=yd + 55, ini=25, fim=ln + a["ancoragem_tirante_mm"], area_total=a["n_tir"] * AREA[a["d_tir"]])]
    n = a["n_sus"]
    s_sus = min(60.0, (0.5 * hd - 40) / max(n - 1, 1))
    for k in range(n):
        arm.append(dict(tipo="v", nome="suspensao", pos=ln + 40 + k * s_sus, ini=40, fim=H - 40, area_total=2 * AREA[a["d_sus"]]))
    d = hd - 55
    for k in range(a["n_cost"]):
        arm.append(dict(tipo="h", nome="costura", pos=yd + 55 + (k + 1) * (2 / 3 * d) / (a["n_cost"] + 1), ini=25, fim=ln + 450,
                        area_total=2 * AREA[a["d_cost"]]))
    nv = max(2, a["n_v"])
    for k in range(nv):
        arm.append(dict(tipo="v", nome="vertical_dente", pos=50 + k * (ln - 100) / max(nv - 1, 1), ini=yd + 40, fim=H - 40,
                        area_total=2 * AREA[10.0]))
    de, se = v["estribo"]
    x = ln + 40 + n * s_sus + se
    Ls = v.get("Ls", 3000.0)
    while x < Ls:
        arm.append(dict(tipo="v", nome="estribo", pos=x, ini=40, fim=H - 40, area_total=2 * AREA[de]))
        x += se
    # reforço só do modelo no trecho além da carga (apoio da extremidade do segmento), para a ruptura ficar no dente
    for xx in range(int(Ls - 750), int(Ls), 75):
        arm.append(dict(tipo="v", nome="modelo", pos=xx, ini=40, fim=H - 40, area_total=2 * AREA[12.5]))
    arm.append(dict(tipo="h", nome="longitudinal_sup", pos=H - 45, ini=25, fim=Ls, area_total=v["sup"]))
    arm.append(dict(tipo="h", nome="longitudinal_inf", pos=40, ini=ln + 25, fim=Ls, area_total=v["inf"]))
    return arm


res = {}
for nome, v in VIGAS.items():
    D = Dente(nome, v["Vd"], v["Hd"], 400, v["hd"], v["ln"], v["a_apoio"], v["H"])
    r = D.dimensionar(diam_tir=v["d_tir"], diam_sus=v["d_sus"])
    r["nota_Hd"] = NOTAS_H[nome]
    res[nome] = dict(geometria={k: v[k] for k in ("H", "hd", "ln", "a_apoio", "x_mac", "l_apoio")}, Vd=v["Vd"], Hd=v["Hd"], calculo=r)
    if not SO_DADOS and (not SO or nome in SO):
        g = dict(H=v["H"], b=400, bw=150, ti=v["ti"], mi=80, ts=v["ts"], ms=80, hd=v["hd"], ln=v["ln"], a_apoio=v["a_apoio"],
                 x_mac=v["x_mac"], l_apoio=v["l_apoio"])
        m = analisar(g, armaduras(v, r), v["cord"], v["Vd"], v["Hd"], fck=50.0, malha=25.0, Ls=v.get("Ls", 3000.0), xP=v.get("xP", 1300.0), passos=500, rampa_fim=v.get("rampa_fim", False), robusto=v.get("robusto", False),
                     saida_png=str(AQUI / f"mef_dente_{nome}.png"), titulo=f"Dente Gerber {nome}")
        m["ok"] = m["Vu_kN"] >= 1.06 * v["Vd"]          # validação: o modelo superestima a flexão em ~6% (tests)
        res[nome]["mef"] = m
        print(nome, "Vd", v["Vd"], "Vu MEF", m["Vu_kN"], "pico", m["V_pico_kN"], m["limite"], "FS", m["FS"])

# consolos que recebem os dentes (topo inclinado 3% quando recebe TS-01)
res["consolos"] = [
    consolo("CP-I130 pilar central (recebe I130)", 472, 76, 500, 490, a=200 + 25, diam=20.0),
    consolo("CP-MEZ pilar (recebe viga do mezanino)", 383, 65, 400, 550, a=175 + 25, diam=20.0),
]
prev = {}
if (AQUI / "dentes.json").exists():
    prev = json.loads((AQUI / "dentes.json").read_text(encoding="utf-8"))
for k, v in prev.items():
    if k in res and "mef" in v and "mef" not in res[k]:
        res[k]["mef"] = v["mef"]
if not SO_DADOS:
    (AQUI / "dentes.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
if not SO_DADOS:
    print(json.dumps({k: (v["calculo"]["adotado"] if "calculo" in v else v) for k, v in res.items()}, ensure_ascii=False, indent=0)[:3000])
