"""Gera saidas/letsara_portico.html — deformadas ELU/ELS do modelo global (three.js), a partir de modelo_global_r01.json."""
import json
from pathlib import Path

AQ = Path(__file__).parent
R = json.loads((AQ / "modelo_global_r01.json").read_text(encoding="utf-8"))
nos = {int(k): v for k, v in R["nos"].items()}
ids = sorted(nos)
idx = {n: i for i, n in enumerate(ids)}
P = [c for n in ids for c in nos[n]]
pil = [[idx[n] for n in p["ns"]] for p in R["pilares"]]
grupos = sorted(set(b["grupo"] for b in R["barras"]))
bars = [[idx[b["n1"]], idx[b["n2"]], grupos.index(b["grupo"])] for b in R["barras"]]
comb = {}
for nome, c in R["combinacoes"].items():
    d = [0.0] * (3 * len(ids))
    for k, v in c["deslocamentos"].items():
        i = idx[int(k)]
        d[3 * i:3 * i + 3] = v
    comb[nome] = dict(tipo=c["tipo"], d=[round(x, 2) for x in d], dmax=c["desl_max_mm"], pilar=c["pilar_desl_max"],
                      gz=c.get("gama_z_aprox"), lim=c.get("limite_mm"), ok=c.get("ok_ELS"), forcas=c["forcas_barras"])
def acha(x, y, z):
    return next(idx[n] for n, v in nos.items() if abs(v[0] - x) < 1e-3 and abs(v[1] - y) < 1e-3 and abs(v[2] - z) < 0.02)
from geometria import Y_LIN, X_EIXO
diaf = [[acha(0, 0, z), acha(X_EIXO["E"], 0, z), acha(X_EIXO["E"], Y_LIN[1], z), acha(0, Y_LIN[1], z)] for z in (3.15, 6.55)]
from collections import Counter
cnt = Counter(b["grupo"] for b in R["barras"])
CONF = [["Pilares (engastados no cálice)", "33", f"{len(R['pilares'])} barras verticais"],
        ["TS-01 I90 (linhas 2–8, 2 vãos)", "14", f"{cnt['TS-01']} trechos de treliça (nós em cada terça)"],
        ["I110 V407 / V406 / V405", "3", f"{cnt['I110']} trechos articulados"],
        ["VB 15×90 (fachadas 1 e 9)", "8", f"{cnt['VB']} trechos de viga, articulada nos pilares"],
        ["VT 25×60 (eixos A e E, L2–L9)", "14", f"{cnt['VT']} barras articuladas"],
        ["VM I90 (mezanino, 2 níveis)", "16", f"{cnt['VM']} barras articuladas"],
        ["Laje alveolar + capa (2 níveis)", "2 × 32 painéis", "diafragma rígido (rigidDiaphragm) em +3,15 e +6,55"],
        ["Terças Ue 300 (26 linhas × 8 vãos)", "208", f"{cnt['terça-escora']} escoras (25 alinhamentos × 8 vãos: as 2 terças junto ao eixo C num nó só), inclusive vãos de oitão 1–2 e 8–9 sobre a VB"],
        ["Contraventamento X Ø16 (só tração)", "COB02", f"{cnt['X Ø16']} diagonais"]]
ver = sorted(R["verificacao_pilares"].items(), key=lambda kv: -kv[1]["uso"])
DATA = dict(diaf=diaf, conf=CONF, P=P, pil=pil, bars=bars, grupos=grupos, comb=comb, ver=ver, mg=R.get("metodo_geral"))
html = open(AQ / "portico_template.html", encoding="utf-8").read().replace("/*DATA*/null", json.dumps(DATA, ensure_ascii=False, separators=(",", ":")))
(AQ / "saidas" / "letsara_portico.html").write_text(html, encoding="utf-8")
print("ok", len(ids), "nós", len(bars), "barras", (AQ / "saidas" / "letsara_portico.html").stat().st_size // 1024, "kB")
