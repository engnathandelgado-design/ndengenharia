"""OBSOLETO (DEC-039, 21/10/2026): a CT-1/CT-1P foi REMOVIDA — o giro de montagem da VM é travado pela ponta concretada
(calc_vm_meio_vaso.py, torcao_montagem.junta). Mantido só como registro da DEC-038.

CT-1 / CT-1P — peças antigiro da VM meio vaso, SEM trilho e SEM solda (DEC-038, 21/10/2026).

Força: H_CT1,d da torção de montagem (calc_vm_meio_vaso.py → vm_meio_vaso.json, NBR 9062:2017 11.1 e 7.2.2.2), no topo da VM.
- CT-1 (24 un., pilares PF/PC/PM — pilar 10 cm mais largo que a VM do lado externo): cantoneira laminada L 152×102×15,9 L = 150
  (L limitado pela trava PT-2 das placas na mesma face do PF, 16,5 cm abaixo do topo da VM — colisao_ct1.py).
  Aba 152 na face externa da VM, 1 M20 8.8 na bucha BR-4 (M20 hef 200 + barra Ø10) a 5 cm da ponta da VM (8 cm da face do
  pilar), 7,5 cm abaixo do topo, oblongo 22×52 horizontal (junta 3 ± 1,5 cm); aba 102 na face do CP-MEZ com 2 BR-3 (M16 hef 150 +
  barra Ø10, s 7 vertical, 4 e 11 abaixo do topo, 5 cm da aresta externa = gabarito 50 do dorso), oblongos 18×36 verticais (±9 mm). A VM puxa a aba 152 (BR-4 à tração) e a aba trabalha em balanço até a raiz.
- CT-1P (8 un., pilares PL — pilar 40 em y = largura da VM, faces coplanares, sem lugar para a aba 102 do lado): a mesma cantoneira
  no TOPO da VM: aba 152 horizontal sobre a alma, 1 M20 vertical na bucha BR-5 (M20 hef 150 + grampo U Ø10) a 7 cm da ponta; aba
  102 vertical na face do CP-MEZ acima da VM com 2 BR-3 lado a lado (s 8). Força no plano das abas (cisalhamento), embutida no 2º
  estágio. Checagem de colisão: colisao_ct1.py (a CT-1P lateral bate na descida DE-1 no P1 da linha 2).
Buchas pelo ACI 318-19 cap. 17 (nd_estruturas.ancoragem), C40 fissurado; cantoneira e parafusos pela NBR 8800:2024."""
import json, sys
from pathlib import Path
AQ = Path(__file__).parent
sys.path.insert(0, str(AQ.parent.parent))
from nd_estruturas.ancoragem import GrupoPinos, interacao, grampo_ancoragem_kN

VM = json.loads((AQ / "vm_meio_vaso.json").read_text(encoding="utf-8"))
TM = VM["VM-02"]["torcao_montagem"]
H = TM["H_CT1_d_kN"]                                   # kN, γ 1,3 já aplicado
H_fora = 1.3 * abs(TM["T_peca_sozinha_k"]) / TM["z_CT1_m"]
FY, GA1 = 250.0, 1.10                                   # A36, NBR 8800:2024 γa1
T, R_RAIZ = 15.9, 13.0                                  # L 152×102×15,9 (5/8"): espessura e raio de concordância (mm)
JUNTA, TOL_J = 30.0, 15.0                               # junta VM × pilar e tolerância de montagem (NBR 9062:2017 5.2.2.6)
R = dict(H_CT1_d_kN=H, H_fora_kN=round(H_fora, 1), origem="vm_meio_vaso.json VM-02 torcao_montagem (T_F1 15,0 kN·m, z 0,695 m)",
         cantoneira="L 152×102×15,9 A36 (laminada inteira, sem solda); CT-1 e CT-1P L=150")
L_CT1, S_BR3, C_BR3, Z_BR4 = 150.0, 70.0, 50.0, 75.0   # comprimento, s vertical das BR-3, borda no pilar, BR-4 abaixo do topo (mm)

# ---------------- CT-1 (lateral) ----------------
X_BR4 = 50.0                                            # BR-4 a 50 mm da ponta da VM
braco = JUNTA + TOL_J + X_BR4 - T - R_RAIZ              # do furo à raiz da aba 102 (pior junta)
M = H * braco / 1000
Z = L_CT1 * T ** 2 / 4                                  # aba L_CT1 (altura) × 15,9, flexão fora do plano (Z ≤ 1,5 W)
MRd = FY * Z / GA1 / 1e6
R["CT1_aba152"] = dict(braco_mm=round(braco, 1), M_kNm=round(M, 2), Z_mm3=round(Z), MRd_kNm=round(MRd, 2), uso=round(M / MRd, 3),
                       comparacao=dict(L152x102x12_5=round(H * (JUNTA + TOL_J + X_BR4 - 12.5 - R_RAIZ) / 1000 / (FY * L_CT1 * 12.5 ** 2 / 4 / GA1 / 1e6), 2),
                                       antiga_furo_a_140=round(H * 0.140 / (FY * 150 * 12.5 ** 2 / 4 / GA1 / 1e6), 2)))
g3 = GrupoPinos(d=16, d_cabeca=30, hef=150, nx=1, ny=2, sx=0, sy=S_BR3, cx_neg=C_BR3, cx_pos=540, cy_neg=300, cy_pos=300, ha=400, fc=40.0)
t3, v3i, v3o = g3.tracao(), g3.cortante("x+"), g3.cortante("x-")
it3 = max(interacao(0.2 * H, t3["phiNn_kN"], H, v3i["phiVn_kN"])[0], interacao(0.2 * H, t3["phiNn_kN"], H_fora, v3o["phiVn_kN"])[0])
R["BR3_CT1"] = dict(desc="2 BR-3 M16 hef 150 + barra Ø10, s 70 vertical, 50 da aresta", phiNn=round(t3["phiNn_kN"], 1), phiVn_dentro=round(v3i["phiVn_kN"], 1),
                    phiVn_fora=round(v3o["phiVn_kN"], 1), interacao=round(it3, 3))
g4 = GrupoPinos(d=20, d_cabeca=36, hef=200, nx=1, ny=1, sx=0, sy=0, cx_neg=X_BR4, cx_pos=2000, cy_neg=2000, cy_pos=Z_BR4, ha=400, fc=40.0)
t4 = g4.tracao()
R["BR4_VM"] = dict(desc="BR-4 M20 hef 200 + barra Ø10 na ponta maciça da VM (50 da ponta, 75 do topo)", phiNn=round(t4["phiNn_kN"], 1), modo=t4["modo"],
                   uso=round(H / t4["phiNn_kN"], 3))

# folgas de montagem das porcas/arruelas (NBR 8800:2024 6.3.11 e Tabela 14; arruela M16 Ø30, M20 Ø37)
g_br3 = 100.0 - C_BR3                                   # gabarito do furo da aba 102 a partir do dorso (pilar 10 cm além da VM)
R["gabaritos"] = dict(CT1_aba102_g_mm=g_br3, folga_arruela_raiz_mm=round(g_br3 - 15 - T - R_RAIZ, 1),
                      CT1_aba102_borda_ponta_mm=102 - g_br3, CT1_borda_oblongo_topo_mm=40 - 18, CT1_aba152_folga_arruela_raiz_mm=round(JUNTA + X_BR4 - 18.5 - T - R_RAIZ, 1),
                      CT1P_aba102_folga_arruela_raiz_mm=round(45 - 15 - R_RAIZ, 1), CT1P_aba102_borda_topo_mm=round(102 - 45 - T, 1), CT1P_furo_borda_ponta_mm=25.0,
                      borda_min_M16_Tab14_mm=22.0)
assert min(R["gabaritos"][k] for k in ("folga_arruela_raiz_mm", "CT1_aba152_folga_arruela_raiz_mm", "CT1P_aba102_folga_arruela_raiz_mm")) > 0
assert min(R["gabaritos"][k] for k in ("CT1_aba102_borda_ponta_mm", "CT1_borda_oblongo_topo_mm", "CT1P_aba102_borda_topo_mm", "CT1P_furo_borda_ponta_mm")) >= 22

# ---------------- CT-1P (topo, PL) ----------------
g5 = GrupoPinos(d=20, d_cabeca=36, hef=150, nx=1, ny=1, sx=0, sy=0, cx_neg=125, cx_pos=275, cy_neg=70, cy_pos=2000, ha=800, fc=40.0)
v5s = g5.cortante("x-")
gr = grampo_ancoragem_kN(10, pernas=2)
v5 = g5.cortante("x-", armadura_ancoragem_kN=gr)
R["BR5_VM"] = dict(desc="BR-5 M20 hef 150 vertical + grampo U Ø10 no topo da ponta maciça (70 da ponta, 125 da face externa)",
                   phiVn_sem_grampo=round(v5s["phiVn_kN"], 1), phiVn=round(v5["phiVn_kN"], 1), modo=v5["modo"], uso=round(H / v5["phiVn_kN"], 3))
S_T, Z_T = 100.0, 45.0                                  # BR-3 do CT-1P: lado a lado a s = 100, eixo 45 acima da aba horizontal
g3t = GrupoPinos(d=16, d_cabeca=30, hef=150, nx=2, ny=1, sx=S_T, sy=0, cx_neg=75, cx_pos=225, cy_neg=500, cy_pos=500, ha=600, fc=40.0)
v3ti, v3to = g3t.cortante("x+"), g3t.cortante("x-")
R["BR3_CT1P"] = dict(desc="2 BR-3 M16 hef 150 lado a lado (s 100), 75 da aresta externa, eixo 45 acima da aba horizontal",
                     phiVn_dentro=round(v3ti["phiVn_kN"], 1), phiVn_fora=round(v3to["phiVn_kN"], 1), uso=round(max(H / v3ti["phiVn_kN"], H_fora / v3to["phiVn_kN"]), 3))
e_z = (Z_T + T) / 1000                                   # força no topo da VM × eixo dos parafusos (binário no plano da aba 102)
Fz = H * e_z / (S_T / 1000)
F1 = ((H / 2) ** 2 + Fz ** 2) ** 0.5
phiVsa = 0.65 * 0.6 * 157 * 450 / 1e3                    # ACI 318-19 17.7.1.2, por bucha
R["CT1P_parafusos"] = dict(M_plano_kNm=round(H * e_z, 2), F_por_M16_kN=round(F1, 1), phiVsa_bucha_kN=round(phiVsa, 1), uso_aco_bucha=round(F1 / phiVsa, 3))

# ---------------- parafusos 8.8 (NBR 8800:2024 6.3.3.2 / 6.3.3.1) ----------------
FV16 = 0.4 * 800 * 157 / 1.35 / 1e3
FT20 = 0.75 * 800 * 314 / 1.35 / 1e3
FV20 = 0.4 * 800 * 245 / 1.35 / 1e3
R["parafusos"] = dict(Fv_Rd_M16=round(FV16, 1), Ft_Rd_M20=round(FT20, 1), Fv_Rd_M20=round(FV20, 1),
                      uso_M16_CT1=round(H / 2 / FV16, 3), uso_M20_CT1_tracao=round(H / FT20, 3),
                      uso_M16_CT1P=round(R["CT1P_parafusos"]["F_por_M16_kN"] / FV16, 3), uso_M20_CT1P_corte=round(H / FV20, 3))
usos = [R["CT1P_parafusos"]["uso_aco_bucha"], R["CT1_aba152"]["uso"], R["BR3_CT1"]["interacao"], R["BR4_VM"]["uso"], R["BR5_VM"]["uso"], R["BR3_CT1P"]["uso"]] + [v for k, v in R["parafusos"].items() if k.startswith("uso")]
R["uso_max"] = max(usos)
R["ok"] = R["uso_max"] <= 1.0
R["BR3"] = dict(d=16, hef=150, s=S_BR3, desc="inserto rosqueado M16 (bucha de aço) hef 150 com barra transversal Ø10 — tipo de catálogo, carga de cálculo ≥ 30 kN ao corte")
(AQ / "ct1.json").write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(R, ensure_ascii=False, indent=1))
assert R["ok"], R["uso_max"]
