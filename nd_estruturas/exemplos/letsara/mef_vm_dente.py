"""MEF não linear do dente Gerber da VM meio vaso com a armação e as cordoalhas EXATAMENTE como na prancha
(armaduras_vigas.armacao_vm / ND-LET-AR-VIG VM) — DEC-032.

Geometria e protensão lidas de vm_meio_vaso.json (h, dente, posições das cordoalhas, σp∞, lbpt).
Força: Fd = γn·Vd, γn 1,2 (NBR 9062:2017 7.3.1.1 — parcela variável ≈ 50 % da reação, não preponderantemente permanente),
Hd = 0,16·Fd (elastômero, 7.3.1.2). Critério: Vu ≥ 1,06·Fd (o modelo superestima ~6 % a flexão — tests).
Grava mef_vm_dente_{H}_{hd}.json (lido por armaduras_vigas.spec_vm e calc_nbr9062).
"""
import json, os, sys
from pathlib import Path
AQ = Path(__file__).parent
sys.path.insert(0, str(AQ.parents[1]))
os.environ["ND_SO_DADOS"] = "1"
from nd_estruturas.dente_consolo import Dente, AREA
from nd_estruturas.mef_dente import analisar

VMJ = json.loads((AQ / "vm_meio_vaso.json").read_text(encoding="utf-8"))
P = VMJ["premissas"]
V2 = VMJ["VM-02"]
HH, HD_, LN = round(P["h_pm"] * 1000), round(P["dente"]["hd"] * 1000), round(P["dente"]["ln"] * 1000)
MAC = round(P["dente"]["macico"] * 1000)
REC = HH - HD_
COB = 25
GAMA_N = 1.2                                                     # NBR 9062:2017 7.3.1.1 (pré-moldado, permanente não preponderante)
Vd_reacao = max(VMJ[k]["cortante"]["Vd"] for k in ("VM-01", "VM-02"))
Fd = round(GAMA_N * Vd_reacao, 1)
Hd = round(0.16 * Fd, 1)

# cordoalhas reais (mm): agrupar por altura; 2 da linha de baixo isoladas por L_ISOL nas pontas (calc_vm_meio_vaso)
from collections import Counter
cnt = Counter(y for _, y in V2["pos_cordoalhas_mm"])
n_isol = V2["isoladas_pontas"]
L_ISOL = 1500.0
cord = []
for y, n in sorted(cnt.items()):
    if y == min(cnt) and n_isol:
        cord += [dict(y=y, n=n_isol, isol=L_ISOL), dict(y=y, n=n - n_isol)]
    else:
        cord.append(dict(y=y, n=n))
sig_pe = V2["protensao"]["perdas"]["sig_pinf"]
lt = V2["ato"]["lbpt_m"] * 1000

D = Dente("VM-MV", Fd, Hd, 400, HD_, LN, 156, HH, fck=40.0)
r = D.dimensionar(diam_tir=16.0, diam_sus=16.0)
DA = r["adotado"]


def armacao_prancha(a, Ls):
    """Barras do trecho modelado, nas posições do desenho (armaduras_vigas.armacao_vm)."""
    arm = [dict(tipo="h", nome="tirante N6", pos=REC + 55, ini=COB, fim=LN + a["ancoragem_tirante_mm"], area_total=a["n_tir"] * AREA[a["d_tir"]])]
    for k in range(a["n_sus"]):
        arm.append(dict(tipo="v", nome="suspensao N7", pos=LN + 40 + 50 * k, ini=40, fim=HH - 40, area_total=2 * AREA[a["d_sus"]]))
    nc = a["n_cost"]
    for k in range(nc):
        arm.append(dict(tipo="h", nome="costura N8", pos=REC + 120 + k * (HD_ - 160) / max(nc - 1, 1), ini=COB, fim=LN + 450,
                        area_total=2 * AREA[a["d_cost"]]))
    nv = max(2, a["n_v"])
    for k in range(nv):
        arm.append(dict(tipo="v", nome="nariz N10", pos=60 + k * (LN - 120) / max(nv - 1, 1), ini=REC + 40, fim=HH - 40, area_total=2 * AREA[10.0]))
    x_ult = LN + 40 + 50 * (a["n_sus"] - 1)
    for x in range(LN + 40, MAC, 100):                           # N11 Ø8 c/10 na ponta maciça
        if x > x_ult + 30:
            arm.append(dict(tipo="v", nome="N11", pos=x, ini=40, fim=HH - 40, area_total=2 * AREA[8.0]))
    for x in list(range(MAC, 1500, 100)) + list(range(1500, int(Ls - 750), 150)):   # N2 Ø8 c/10 até 1,5 m, c/15 depois
        arm.append(dict(tipo="v", nome="N2", pos=x, ini=40, fim=HH - 40, area_total=2 * AREA[8.0]))
    for xx in range(int(Ls - 750), int(Ls), 75):                 # reforço só do modelo junto ao apoio fictício
        arm.append(dict(tipo="v", nome="modelo", pos=xx, ini=40, fim=HH - 40, area_total=2 * AREA[12.5]))
    arm.append(dict(tipo="h", nome="N3 2Ø12,5 topo", pos=HH - COB - 10, ini=COB, fim=Ls, area_total=2 * AREA[12.5]))
    arm.append(dict(tipo="h", nome="N12 2Ø10 fundo", pos=85, ini=LN + COB, fim=Ls, area_total=2 * AREA[10.0]))
    arm.append(dict(tipo="h", nome="N5 2Ø10 meia altura", pos=HH / 2, ini=COB, fim=Ls, area_total=2 * AREA[10.0]))
    return arm


# carga concentrada no topo no fim do maciço (x = 1,0 m): vão de cisalhamento a/h ≈ 1,25, o mesmo da I120 (xP 1,6 m, h 1,3);
# estudo DEC-032: com xP 1,3 m o nó comprimido do topo junto ao dente (x 39, y 76 cm) esmaga em 452 kN com a reação TOTAL
# aplicada só na peça pré-moldada (sem 2º estágio e capa) — ver estudo_mef_vm_x1300.json
XP = float(os.environ.get("MEF_XP", 1000.0))
VAR = os.environ.get("MEF_VAR", "")                             # variante de estudo: grava em arquivo separado
Ls = 3000.0
g = dict(H=HH, b=400, bw=250, bi=250, ti=10, mi=1, ts=200, ms=1, hd=HD_, ln=LN, a_apoio=156, x_mac=MAC, l_apoio=150)
FCK_M = float(os.environ.get("MEF_FCK", 40.0))
m = analisar(g, armacao_prancha(DA, Ls), cord, Fd, Hd, fck=FCK_M, malha=25.0, Ls=Ls, xP=XP, passos=500, robusto=True, rampa_fim=True,
             sig_pe=sig_pe, lt=lt, saida_png=str(AQ / f"mef_dente_VM-MV_{HH}_{HD_}{VAR}.png"), titulo=f"Dente Gerber VM meio vaso h{HH} (dente {HD_} x {LN})")
m["ok"] = m["Vu_kN"] >= 1.06 * Fd
m["criterio"] = f"Vu ≥ 1,06·Fd = {1.06 * Fd:.1f} kN (Fd = γn {GAMA_N} × Vd {Vd_reacao:.1f})"
m["armacao"] = "da prancha (armaduras_vigas.armacao_vm)"
out = dict(geometria=g, Vd=Fd, Vd_reacao=Vd_reacao, gama_n=GAMA_N, Hd=Hd, cordoalhas=cord, sig_pe=sig_pe, lt=lt, calculo=r, mef=m)
(AQ / (f"mef_vm_dente_{HH}_{HD_}.json" if not VAR else f"estudo_mef_vm{VAR}.json")).write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
print(json.dumps(DA, ensure_ascii=False)); print({k: m[k] for k in m if k in ("Vu_kN", "V_pico_kN", "ok", "limite", "FS", "criterio")})
