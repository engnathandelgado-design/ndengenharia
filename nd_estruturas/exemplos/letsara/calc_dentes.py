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
# DEC-032: o dente da I130 usa a reação REAL (TS-01 fora do centro: 1,22·P no apoio do P13), lida de i110_r01.json
# (calc_i110_r01.py) — Vd 555 kN, γn 1,1 (parcela permanente preponderante, NBR 9062:2017 7.3.1.1), Fd = γn·Vd e
# Hd = 0,16·Fd; o MEF roda com a armação da prancha (armaduras_i130) e as cordoalhas, σp∞ e lbpt do cálculo da viga.
I1J = json.loads((AQUI / "i110_r01.json").read_text(encoding="utf-8"))
_V = max((k for k in I1J if k != "V407"), key=lambda k: I1J[k]["dente"]["Fd"])   # DEC-058: V405 (P13 → P13B, 2 TS-01 no topo)
_DI = I1J[_V]["dente"]
_FAT = {"Ø15.2": 140.0 / 98.7}.get(I1J[_V]["arranjo"].get("cordoalha"), 1.0)     # DEC-054: Ø15,2 no MEF como n·(140/98,7) cordoalhas Ø12,7 equivalentes
_CORD_I130 = [dict(y=l["y"], n=len(l["xs"]) * _FAT, **({"isol": l["isol"]} if l["isol"] else {})) for l in I1J[_V]["arranjo"]["linhas"]]
_H_I130 = round(json.loads((AQUI / "ligacoes.json").read_text(encoding="utf-8"))["H_I130"] * 1000)   # DEC-054: 1200
VIGAS = {
    # I130: dente 78 × 35; 28 cordoalhas embaixo (linhas 14 e 18 isoladas 2,0 e 4,0 m) + 2 na mesa superior (DEC-032)
    "I130": dict(Vd=_DI["Fd"], Hd=_DI["Hd"], gama_n=_DI["gama_n"], Vd_reacao=_DI["Vd"], viga=_V, H=_H_I130, ti=250, ts=220, hd=780, ln=350,
                 a_apoio=175, x_mac=1400, l_apoio=250, cord=_CORD_I130, estribo=(8.0, 150), sup=6 * AREA[25.0], inf=2 * AREA[10.0],
                 d_tir=20.0, d_sus=16.0, Ls=3600.0, xP=1600.0, rampa_fim=True, robusto=True, du=0.02,   # DEC-054: passo de 0,02 mm (com 0,05 o 1º passo não converge depois da fissuração da protensão)
                 sig_pe=I1J[_V]["perdas"]["sig_pinf"], lt=I1J[_V]["ato"]["lbpt_m"] * 1000, prancha=True),
    "MEZ-I90": dict(Vd=383.0, Hd=65.0, H=900, ti=150, ts=120, hd=450, ln=300, a_apoio=150, x_mac=1200, l_apoio=200,
                    cord=[dict(y=75, n=7), dict(y=117, n=1)], estribo=(8.0, 150), sup=4 * AREA[12.5], inf=2 * AREA[10.0],
                    d_tir=20.0, d_sus=16.0),
    # opção do mezanino com laje h20+5: I70 (mesma fôrma, mesas 12/15), dente de 425 (61%)
    "MEZ-I70": dict(Vd=345.0, Hd=58.0, H=700, ti=150, ts=120, hd=425, ln=300, a_apoio=150, x_mac=1000, l_apoio=200,
                    cord=[dict(y=75, n=7), dict(y=117, n=3)], estribo=(8.0, 150), sup=4 * AREA[12.5], inf=2 * AREA[10.0],
                    d_tir=20.0, d_sus=16.0),
}
NOTAS_H = {"MEZ-I70": "Hd = 0,16 Vd + diafragma",
           "I130": "Fd = γn·Vd (NBR 9062:2017 7.3.1.1); Hd = 0,16 Fd (elastômero, 7.3.1.2) ≥ 1,4 × 23 kN do modelo global",
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


def x_n8(n, ln=350, x_tb=175, r_tb=30, c=60):
    """Posições (mm, da ponta) dos estribos verticais N8 do dente da I130: entre 60 e ln − 60, afastados ≥ 40 mm (livre)
    do tubo TB-2 Ø60,3 do pino (eixo a x_tb) — metade antes e metade depois do tubo."""
    a1, b1 = c, x_tb - r_tb - 40 - 5
    a2, b2 = x_tb + r_tb + 40 + 5, ln - c
    n1 = (n + 1) // 2
    n2 = n - n1
    l1 = [a1 + k * (b1 - a1) / max(n1 - 1, 1) for k in range(n1)]
    l2 = [a2 + k * (b2 - a2) / max(n2 - 1, 1) for k in range(n2)] if n2 else []
    return [round(x / 5) * 5 for x in l1 + l2]


def armaduras_i130(v, a):
    """Armação da ponta da I130 exatamente como na prancha ND-LET-I130 / AR-VIG-02 (viga_i.dados_i110):
    N5 tirante em alças horizontais Ø20 (todos os ramos no nível y_t = recorte + 55), N6 suspensão Ø16 a LN + 60 + 80k,
    N7 costura Ø10 a recorte + 150 + 100k até LN + 900, N8 Ø10 no dente (x_n8, fora do TB-2), N2 Ø8 (2 ramos) c/10 nos 2,0 m e
    c/15 depois, N3 4 Ø20 no topo, N12 2 Ø10 no fundo, N4 pele 2 Ø8 por face (y 500, 650, 800, 950)."""
    H, hd, ln = v["H"], v["hd"], v["ln"]
    rec = H - hd
    Ls = v["Ls"]
    arm = [dict(tipo="h", nome="tirante", pos=rec + 55, ini=25, fim=a["ancoragem_tirante_mm"], area_total=a["n_tir"] * AREA[a["d_tir"]])]
    for k in range(a["n_sus"]):
        arm.append(dict(tipo="v", nome="suspensao", pos=ln + 60 + 80 * k, ini=40, fim=H - 40, area_total=2 * AREA[a["d_sus"]]))
    for k in range(a["n_cost"]):
        arm.append(dict(tipo="h", nome="costura", pos=rec + 150 + 100 * k, ini=25, fim=ln + 900, area_total=2 * AREA[a["d_cost"]]))
    for x in x_n8(a["n_v"], ln):
        arm.append(dict(tipo="v", nome="vertical_dente", pos=x, ini=rec + 40, fim=H - 40, area_total=2 * AREA[10.0]))
    xs_e = [x for x in list(range(50, 2000, 100)) + list(range(2000, int(Ls), 150)) if x >= ln + 40]
    for x in xs_e:
        arm.append(dict(tipo="v", nome="estribo", pos=x, ini=40, fim=H - 40, area_total=2 * AREA[8.0]))
    for xx in range(int(Ls - 750), int(Ls), 75):          # reforço só do modelo junto ao apoio fictício (ruptura fica no dente)
        arm.append(dict(tipo="v", nome="modelo", pos=xx, ini=40, fim=H - 40, area_total=2 * AREA[12.5]))
    arm.append(dict(tipo="h", nome="longitudinal_sup", pos=H - 45, ini=25, fim=Ls, area_total=v["sup"]))
    arm.append(dict(tipo="h", nome="longitudinal_inf", pos=35, ini=ln + 30, fim=Ls, area_total=v["inf"]))
    for y in (y_ for y_ in (500, 650, 800, 950) if y_ < H - 300):     # pele só na alma (mesma regra da prancha)
        arm.append(dict(tipo="h", nome="pele", pos=y, ini=25, fim=Ls, area_total=2 * AREA[8.0]))
    return arm


res = {}
for nome, v in VIGAS.items():
    D = Dente(nome, v["Vd"], v["Hd"], 400, v["hd"], v["ln"], v["a_apoio"], v["H"])
    r = D.dimensionar(diam_tir=v["d_tir"], diam_sus=v["d_sus"])
    r["nota_Hd"] = NOTAS_H[nome]
    res[nome] = dict(geometria={k: v[k] for k in ("H", "hd", "ln", "a_apoio", "x_mac", "l_apoio")}, Vd=v["Vd"], Hd=v["Hd"], calculo=r,
                     **({k: v[k] for k in ("gama_n", "Vd_reacao", "viga")} if "gama_n" in v else {}))
    if not SO_DADOS and (not SO or nome in SO):
        g = dict(H=v["H"], b=400, bw=150, ti=v["ti"], mi=80, ts=v["ts"], ms=80, hd=v["hd"], ln=v["ln"], a_apoio=v["a_apoio"],
                 x_mac=v["x_mac"], l_apoio=v["l_apoio"])
        arm = armaduras_i130(v, r["adotado"]) if v.get("prancha") else armaduras(v, r)
        kw = dict(sig_pe=v["sig_pe"], lt=v["lt"]) if "sig_pe" in v else {}
        m = analisar(g, arm, v["cord"], v["Vd"], v["Hd"], fck=50.0, malha=25.0, Ls=v.get("Ls", 3000.0), xP=v.get("xP", 1300.0), passos=500, du=v.get("du", 0.05), rampa_fim=v.get("rampa_fim", False), robusto=v.get("robusto", False),
                     saida_png=str(AQUI / f"mef_dente_{nome}.png"), titulo=f"Dente Gerber {nome}", **kw)
        m["ok"] = m["Vu_kN"] >= 1.06 * v["Vd"]          # validação: o modelo superestima a flexão em ~6% (tests); Vd aqui já é Fd = γn·Vd
        m["criterio"] = f"Vu ≥ 1,06·Fd = {1.06 * v['Vd']:.1f} kN"
        m["armacao"] = "da prancha (armaduras_i130)" if v.get("prancha") else "genérica (armaduras)"
        res[nome]["mef"] = m
        print(nome, "Vd", v["Vd"], "Vu MEF", m["Vu_kN"], "pico", m["V_pico_kN"], m["limite"], "FS", m["FS"])

# consolos que recebem os dentes (topo inclinado 3% quando recebe TS-01)
res["consolos"] = [
    consolo("CP-I130 pilar central (recebe I130)", VIGAS["I130"]["Vd"], VIGAS["I130"]["Hd"], 500, 490, a=200 + 25, diam=20.0),
    consolo("CP-MEZ pilar (recebe viga do mezanino)", 383, 65, 400, 550, a=175 + 25, diam=20.0),
]
prev = {}
if (AQUI / "dentes.json").exists():
    prev = json.loads((AQUI / "dentes.json").read_text(encoding="utf-8"))
for k, v in prev.items():
    if k in res and "mef" in v and "mef" not in res[k] and abs(v.get("Vd", 0) - res[k]["Vd"]) < 0.5:
        res[k]["mef"] = v["mef"]                         # só reaproveita o MEF anterior se a força for a mesma
if not SO_DADOS:
    (AQUI / "dentes.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
if not SO_DADOS:
    print(json.dumps({k: (v["calculo"]["adotado"] if "calculo" in v else v) for k, v in res.items()}, ensure_ascii=False, indent=0)[:3000])
