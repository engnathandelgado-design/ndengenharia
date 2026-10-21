"""CT-1 / CT-1P — cantoneira antigiro da VM meio vaso sem trilho (DEC-038, 21/10/2026).
Força: H_CT1,d da torção de montagem (calc_vm_meio_vaso.py → vm_meio_vaso.json, NBR 9062:2017 11.1 e 7.2.2.2).
- CT-1 (pilares com face mais larga que a VM: PF, PC, PM): L 152×102×19 + 2 nervuras 12,5 × 100 (oficina); aba 102 na face do CP-MEZ
  com 2 buchas BR-3 M16 (cisalhamento ao longo da face, para dentro do pilar); aba 152 na VM, 1 M20 na bucha BR-2.
- CT-1P (PL, pilar 40 em y = largura da VM, faces coplanares): chapa 250 × 150 × 19 + 2 nervuras 12,5 × 100 na face lateral externa;
  2 BR-3 M16 na face lateral do pilar (tração) e 1 M20 na BR-2 da VM.
Buchas pelo ACI 318-19 cap. 17 (nd_estruturas.ancoragem), C40 fissurado; chapas e parafusos pela NBR 8800:2024."""
import json, math, sys
from pathlib import Path
AQ = Path(__file__).parent
sys.path.insert(0, str(AQ.parent.parent))
from nd_estruturas.ancoragem import GrupoPinos, interacao

VM = json.loads((AQ / "vm_meio_vaso.json").read_text(encoding="utf-8"))
TM = VM["VM-02"]["torcao_montagem"]
H = TM["H_CT1_d_kN"]                                   # kN (γ 1,3 já aplicado)
Nu_sec = 0.2 * H                                       # tração parasita na BR-3 da CT-1 (excentricidade da aba)
FY, GA1 = 250.0, 1.10
R = dict(H_CT1_d_kN=H, origem="vm_meio_vaso.json VM-02 torcao_montagem (T_F1 15,0 kN·m, z 0,695 m)")

# BR-3: inserto rosqueado M16, hef 150, barra transversal Ø10 (cabeça equivalente 30 mm); 2 por peça, s = 80 vertical
BR3 = dict(d=16, d_cabeca=30, hef=150, s=80)
# CT-1: aba 102 na face do CP-MEZ; buchas a 60 da aresta externa (borda c1 = 60 para fora, 540 para dentro); força para dentro
g = GrupoPinos(d=16, d_cabeca=30, hef=150, nx=1, ny=2, sx=0, sy=80, cx_neg=60, cx_pos=540, cy_neg=300, cy_pos=300, ha=400, fc=40.0)
t, vin, vout = g.tracao(), g.cortante("x+"), g.cortante("x-")
H_out = 1.3 * abs(TM["T_peca_sozinha_k"]) / TM["z_CT1_m"]
it_ct1 = max(interacao(Nu_sec, t["phiNn_kN"], H, vin["phiVn_kN"])[0], interacao(Nu_sec, t["phiNn_kN"], H_out, vout["phiVn_kN"])[0])
R["BR3_CT1"] = dict(phiNn=round(t["phiNn_kN"], 1), phiVn_dentro=round(vin["phiVn_kN"], 1), modo=vin["modo"], phiVn_fora=round(vout["phiVn_kN"], 1),
                    H_fora=round(H_out, 1), Nu=round(Nu_sec, 1), interacao=round(it_ct1, 3))
# CT-1P: buchas na face lateral do PL, a 70 da aresta da face do CP-MEZ; tração H
gp = GrupoPinos(d=16, d_cabeca=30, hef=150, nx=1, ny=2, sx=0, sy=80, cx_neg=70, cx_pos=530, cy_neg=400, cy_pos=400, ha=400, fc=40.0)
tp = gp.tracao()
R["BR3_CT1P"] = dict(phiNn=round(tp["phiNn_kN"], 1), modo=tp["modo"], Nu=round(H, 1), uso=round(H / tp["phiNn_kN"], 3))
# BR-2 na VM (M20 hef 120, face externa da alma, 75 do topo, ~140 da ponta): tração H
gv = GrupoPinos(d=20, d_cabeca=36, hef=120, nx=1, ny=1, sx=0, sy=0, cx_neg=140, cx_pos=2000, cy_neg=2000, cy_pos=75, ha=250, fc=40.0)
tv = gv.tracao()
R["BR2_VM"] = dict(phiNn=round(tv["phiNn_kN"], 1), modo=tv["modo"], Nu=round(H, 1), uso=round(H / tv["phiNn_kN"], 3))


def W_T(bf, tf, tw, hw):
    """módulo elástico mínimo de um T: mesa bf × tf (chapa da aba) + nervuras somadas tw × hw (perpendiculares)."""
    A1, A2 = bf * tf, tw * hw
    y1, y2 = tf / 2, tf + hw / 2
    yc = (A1 * y1 + A2 * y2) / (A1 + A2)
    I = bf * tf ** 3 / 12 + A1 * (yc - y1) ** 2 + tw * hw ** 3 / 12 + A2 * (y2 - yc) ** 2
    return I / max(yc, tf + hw - yc)


# CT-1: aba 152 em balanço do canto até o M20 (110 da ponta da VM + 30 de junta = 140)
M_ct1 = H * 0.140
W_ct1 = W_T(150, 19, 2 * 12.5, 100)
R["CT1_aba"] = dict(M_kNm=round(M_ct1, 2), W_mm3=round(W_ct1), MRd_kNm=round(FY * W_ct1 / GA1 / 1e6, 2), uso=round(M_ct1 / (FY * W_ct1 / GA1 / 1e6), 3),
                    sem_nervura_MRd_kNm=round(FY * 150 * 12.5 ** 2 / 6 / GA1 / 1e6, 2))
# CT-1P: chapa entre a bucha (70 da aresta) e o M20 (140 da aresta): braço 210
M_p = H * 0.210
R["CT1P_chapa"] = dict(M_kNm=round(M_p, 2), W_mm3=round(W_ct1), MRd_kNm=round(FY * W_ct1 / GA1 / 1e6, 2), uso=round(M_p / (FY * W_ct1 / GA1 / 1e6), 3))
# parafusos 8.8 (NBR 8800:2024 6.3.3): M16 corte 2 planos? 1 plano por parafuso; M20 tração
FV16 = 0.4 * 800 * 157 / 1.35 / 1e3
FT20 = 0.75 * 800 * 314 / 1.35 / 1e3
R["parafusos"] = dict(M16_corte_2x_kN=round(2 * FV16, 1), uso_M16=round(H / (2 * FV16), 3), M16_tracao_2x_kN=round(2 * 0.75 * 800 * 157 / 1.35 / 1e3, 1),
                      M20_tracao_kN=round(FT20, 1), uso_M20=round(H / FT20, 3))
R["BR3"] = BR3
ok = all(v <= 1.0 for v in (R["BR3_CT1"]["interacao"], R["BR3_CT1P"]["uso"], R["BR2_VM"]["uso"], R["CT1_aba"]["uso"], R["CT1P_chapa"]["uso"], R["parafusos"]["uso_M16"], R["parafusos"]["uso_M20"]))
R["ok"] = ok
(AQ / "ct1.json").write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(R, ensure_ascii=False, indent=1))
