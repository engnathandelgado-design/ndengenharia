"""Estudo de largura da VM (23/10/2026): MEF não linear do dente Gerber em UMA fase (mesmo modelo da prancha,
mef_vm_ret_dente.py / nd_estruturas.mef_dente.analisar), parametrizado por candidato b × h × hd.
Conservador: a reação total Fd = γn·Vd (γn 1,2) entra na peça pré-moldada isolada (sem 2º estágio e capa), carga no topo a
1,0 m da ponta num trecho de 3 m. Critério Vu ≥ 1,06·Fd.
Uso: python3 mef_vm_largura_1f.py CONFIG.json  → CONFIG_1f.json e .png
"""
import json, os, sys
from collections import Counter
from pathlib import Path
AQ = Path(__file__).resolve().parent
sys.path.insert(0, str(AQ.parents[1]))
os.environ["ND_SO_DADOS"] = "1"
from nd_estruturas.dente_consolo import Dente, AREA
from nd_estruturas.mef_dente import analisar

cfg_path = Path(sys.argv[1])
C = json.loads(cfg_path.read_text(encoding="utf-8"))
HH, HD_, BW, LN, MAC, A_AP, COB = C["h_mm"], C["hd_mm"], C["b_mm"], 400, 1000, 181, 25
REC = HH - HD_
GAMA_N = C.get("gama_n", 1.2)
Fd = round(GAMA_N * C["Vd_kN"], 1)
Hd = round(0.16 * Fd, 1)
cnt = Counter(y for _, y in C["pos_cordoalhas_mm"])
cord = []
for y, n in sorted(cnt.items()):
    if y == min(cnt) and C["isoladas_pontas"]:
        cord += [dict(y=y, n=C["isoladas_pontas"], isol=1500.0), dict(y=y, n=n - C["isoladas_pontas"])]
    else:
        cord.append(dict(y=y, n=n))
D = Dente("VM-RET", Fd, Hd, BW, HD_, LN, A_AP, HH, fck=40.0)
r = D.dimensionar(diam_tir=16.0, diam_sus=C.get("d_sus", 16.0))
DA = r["adotado"]
if C.get("n_sus_min"):                                            # suspensão reforçada (estudo)
    DA["n_sus"] = max(DA["n_sus"], C["n_sus_min"])


def armacao(a, Ls):
    arm = [dict(tipo="h", nome="tirante", pos=REC + 55, ini=COB, fim=LN + a["ancoragem_tirante_mm"], area_total=a["n_tir"] * AREA[a["d_tir"]])]
    for k in range(a["n_sus"]):
        arm.append(dict(tipo="v", nome="suspensao", pos=LN + 40 + 50 * k, ini=ANC_INF, fim=ANC_SUP, area_total=2 * AREA[a["d_sus"]]))
    nc = a["n_cost"]
    for k in range(nc):
        arm.append(dict(tipo="h", nome="costura", pos=REC + 120 + k * (HD_ - 160) / max(nc - 1, 1), ini=COB, fim=LN + 450, area_total=2 * AREA[a["d_cost"]]))
    nv = max(2, a["n_v"])
    for k in range(nv):
        arm.append(dict(tipo="v", nome="nariz", pos=60 + k * (LN - 120) / max(nv - 1, 1), ini=REC + 40, fim=HH - 40, area_total=2 * AREA[10.0]))
    x_ult = LN + 40 + 50 * (a["n_sus"] - 1)
    for x in range(LN + 40, MAC, 100):
        if x > x_ult + 30:
            arm.append(dict(tipo="v", nome="N11", pos=x, ini=ANC_INF, fim=ANC_SUP, area_total=2 * AREA[8.0]))
    for x in list(range(MAC, 1500, 100)) + list(range(1500, int(Ls - 750), 150)):
        arm.append(dict(tipo="v", nome="N2", pos=x, ini=ANC_INF, fim=ANC_SUP, area_total=2 * AREA[8.0]))
    for xx in range(int(Ls - 750), int(Ls), 75):
        arm.append(dict(tipo="v", nome="modelo", pos=xx, ini=40, fim=HH - 40, area_total=2 * AREA[12.5]))
    arm.append(dict(tipo="h", nome="N3 topo", pos=HH - COB - 10, ini=COB, fim=Ls, area_total=2 * AREA[12.5]))
    arm.append(dict(tipo="h", nome="N12 fundo", pos=85, ini=LN + COB, fim=Ls, area_total=2 * AREA[10.0]))
    arm.append(dict(tipo="h", nome="N5 meia altura", pos=HH / 2, ini=COB, fim=Ls, area_total=2 * AREA[10.0]))
    for ex in C.get("extra_inf", []):
        arm.append(dict(tipo="h", nome="inf ponta", pos=ex["y"], ini=LN + COB, fim=LN + ex["L"], area_total=ex["n"] * AREA[ex["d"]]))
    return arm


Ls = 3000.0
# Correção de artefato (estudo de largura): no modelo original os estribos terminavam a 40 mm das faces e a barra de topo (N3) a
# 35 mm, em nós diferentes da malha de 25 mm: a força da suspensão entrava num nó isolado de concreto no topo (x = ln + 40) e
# esmagava esse elemento antes da peça. Na peça real o estribo fecha em volta de N3 e de N12: aqui terminam nos mesmos nós.
ANC_SUP = HH - COB - 10
ANC_INF = 85
g = dict(H=HH, b=BW, bw=BW, bi=BW, ti=10, mi=1, ts=200, ms=1, hd=HD_, ln=LN, a_apoio=A_AP, x_mac=MAC, l_apoio=200)
m = analisar(g, armacao(DA, Ls), cord, Fd, Hd, fck=40.0, malha=25.0, Ls=Ls, xP=1000.0, passos=500, robusto=True, rampa_fim=True,
             sig_pe=C["sig_pinf"], lt=C["lbpt_m"] * 1000, saida_png=str(cfg_path.with_name(cfg_path.stem + "_1f.png")),
             titulo=f"Dente Gerber VM {BW} x {HH} (dente {HD_} x {LN}) — 1 fase, peça isolada com Fd total")
m["ok"] = m["Vu_kN"] >= 1.06 * Fd
out = dict(config={k: v for k, v in C.items() if k != "pos_cordoalhas_mm"}, Fd=Fd, Hd=Hd, calculo=r, mef=m)
cfg_path.with_name(cfg_path.stem + "_1f.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
print(json.dumps({"Fd": Fd, **{k: m[k] for k in m if k in ("Vu_kN", "V_pico_kN", "ok", "limite", "FS")}}, ensure_ascii=False))
