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
SO = sys.argv[1:]            # opcional: nomes das vigas a rodar no MEF

# geometria (mm) — mesma fôrma I: largura 400, alma 150, chanfros 80
VIGAS = {
    "TS-01": dict(Vd=138.0, Hd=40.0, H=900, ti=150, ts=120, hd=450, ln=300, a_apoio=150, x_mac=1200, l_apoio=150,
                  cord=[dict(y=75, n=6)], estribo=(6.3, 150), sup=4 * AREA[12.5], inf=2 * AREA[10.0], d_tir=16.0, d_sus=12.5),
    "I110": dict(Vd=448.0, Hd=72.0, H=1100, ti=250, ts=220, hd=550, ln=350, a_apoio=175, x_mac=1400, l_apoio=200,
                 cord=[dict(y=75, n=7), dict(y=117, n=7), dict(y=159, n=7), dict(y=201, n=3)], estribo=(8.0, 150),
                 sup=4 * AREA[12.5], inf=2 * AREA[12.5], d_tir=20.0, d_sus=16.0),
    "MEZ-I90": dict(Vd=383.0, Hd=65.0, H=900, ti=150, ts=120, hd=450, ln=300, a_apoio=150, x_mac=1200, l_apoio=200,
                    cord=[dict(y=75, n=7), dict(y=117, n=1)], estribo=(8.0, 150), sup=4 * AREA[12.5], inf=2 * AREA[10.0],
                    d_tir=20.0, d_sus=16.0),
}
NOTAS_H = {"TS-01": "Hd = 1,4 × 28 kN (tirante do pórtico no modelo global) ≥ 0,16 Vd",
           "I110": "Hd = 0,16 Vd (neoprene) ≥ 1,4 × 36,6 kN do modelo global",
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
    while x < 3000:
        arm.append(dict(tipo="v", nome="estribo", pos=x, ini=40, fim=H - 40, area_total=2 * AREA[de]))
        x += se
    # reforço só do modelo no trecho além da carga (apoio da extremidade do segmento), para a ruptura ficar no dente
    for xx in range(2250, 3000, 75):
        arm.append(dict(tipo="v", nome="modelo", pos=xx, ini=40, fim=H - 40, area_total=2 * AREA[12.5]))
    arm.append(dict(tipo="h", nome="longitudinal_sup", pos=H - 45, ini=25, fim=3000, area_total=v["sup"]))
    arm.append(dict(tipo="h", nome="longitudinal_inf", pos=40, ini=ln + 25, fim=3000, area_total=v["inf"]))
    return arm


res = {}
for nome, v in VIGAS.items():
    D = Dente(nome, v["Vd"], v["Hd"], 400, v["hd"], v["ln"], v["a_apoio"], v["H"])
    r = D.dimensionar(diam_tir=v["d_tir"], diam_sus=v["d_sus"])
    r["nota_Hd"] = NOTAS_H[nome]
    res[nome] = dict(geometria={k: v[k] for k in ("H", "hd", "ln", "a_apoio", "x_mac", "l_apoio")}, Vd=v["Vd"], Hd=v["Hd"], calculo=r)
    if not SO or nome in SO:
        g = dict(H=v["H"], b=400, bw=150, ti=v["ti"], mi=80, ts=v["ts"], ms=80, hd=v["hd"], ln=v["ln"], a_apoio=v["a_apoio"],
                 x_mac=v["x_mac"], l_apoio=v["l_apoio"])
        m = analisar(g, armaduras(v, r), v["cord"], v["Vd"], v["Hd"], fck=50.0, malha=25.0, Ls=3000.0, xP=1300.0, passos=500,
                     saida_png=str(AQUI / f"mef_dente_{nome}.png"), titulo=f"Dente Gerber {nome}")
        m["ok"] = m["Vu_kN"] >= 1.06 * v["Vd"]          # validação: o modelo superestima a flexão em ~6% (tests)
        res[nome]["mef"] = m
        print(nome, "Vd", v["Vd"], "Vu MEF", m["Vu_kN"], "pico", m["V_pico_kN"], m["limite"], "FS", m["FS"])

# consolos que recebem os dentes (topo inclinado 3% quando recebe TS-01)
res["consolos"] = [
    consolo("CP-TS pilar lateral (recebe TS-01)", 138, 40, 400, 450, a=175 + 25),
    consolo("CV-TS na I110 (recebe TS-01, cada lado)", 138, 40, 400, 450, a=75 + 150),
    consolo("CP-I110 pilar central (recebe I110)", 448, 72, 500, 600, a=200 + 25, diam=20.0),
    consolo("CP-MEZ pilar (recebe viga do mezanino)", 383, 65, 400, 550, a=175 + 25, diam=20.0),
]
prev = {}
if (AQUI / "dentes.json").exists():
    prev = json.loads((AQUI / "dentes.json").read_text(encoding="utf-8"))
for k, v in prev.items():
    if k in res and "mef" in v and "mef" not in res[k]:
        res[k]["mef"] = v["mef"]
(AQUI / "dentes.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
print(json.dumps({k: (v["calculo"]["adotado"] if "calculo" in v else v) for k, v in res.items()}, ensure_ascii=False, indent=0)[:3000])
