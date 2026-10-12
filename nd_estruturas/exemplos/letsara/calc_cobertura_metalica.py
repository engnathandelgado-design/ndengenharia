"""Letsara — cobertura metálica: terças Ue, correntes, cantoneira CT-1, mão-francesa, chapas CH-T/CH-MF e chumbadores.

Normas: NBR 14762:2010 (perfis formados a frio, MRD), NBR 8800:2008 (ligações, laminados), NBR 8681:2003 e
NBR 8800 Tabela 1 (combinações), NBR 6123:1988 (vento), ACI 318-19 cap. 17 (chumbadores), AISI S100-16 (forças
de travamento por correntes em perfis C). Unidades kN, m (perfis em mm).
"""
import json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from nd_estruturas.metalica_fria import (PerfilUe, parafuso_corte_Rd, parafuso_tracao_Rd, pressao_contato_fino_Rd,
                                         pressao_contato_Rd, barra_redonda_tracao_Rd, compressao_laminado_Rd)
from nd_estruturas.ancoragem import GrupoPinos, interacao, grampo_ancoragem_kN

AQUI = Path(__file__).parent
R = {}

# ------------------------------------------------------------------ dados
L = 10.05            # maior vão de terça (entre eixos 1 e 2); demais 9,2–9,7 m
s = 1.60             # espaçamento entre terças
g, q = 0.25, 0.25    # kN/m² — telha 0,5 + PIR 30 (0,07), terça (0,07), instalações (0,10); sobrecarga NBR 8800 Anexo B
q0 = 0.874           # kN/m² — V0 45 m/s, S2 cat. III classe C, S3 0,95 (rodada 2)
cp = dict(geral=-1.0, borda=-1.6)    # Cpe −0,8 / −1,4 (faixa de borda, NBR 6123 tab. 6 — conferir) com Cpi +0,2
N_escora_k = 27.5    # kN — terça escora do contraventamento (modelo global, vento longitudinal)
u = PerfilUe(300, 85, 25, 3.0, "ZAR345")
cM = u.criticos("M")
cN = u.criticos("N", L_dist_ref=cM["L_dist"])
R["perfil"] = dict(nome=u.nome, aco=u.aco, A_mm2=round(u.p["A"]), Ix_cm4=round(u.p["Ix"] / 1e4, 1), W_cm3=round(u.W / 1e3, 1),
                   peso_kNm=round(u.peso_kNm, 3), m_ct_mm=round(u.m_ct, 1),
                   assinatura_M=dict(local=round(cM["f_local"], 3), L_local=cM["L_local"], dist=round(cM["f_dist"], 3), L_dist=cM["L_dist"]),
                   assinatura_N=dict(local=round(cN["f_local"], 3), L_local=cN["L_local"], dist=round(cN["f_dist"], 3), obs=cN["obs_dist"]))

# ------------------------------------------------------------------ terça corrente (NBR 14762)
N_LIN = 3                         # linhas de correntes por vão (L/4, L/2, 3L/4): com 2 linhas (L/3) a faixa de borda e a terça escora não passam
Lb = L / (N_LIN + 1) * 1000
M_grav = u.MRd(0, crit=cM, contida=True)          # mesa superior (comprimida) presa à telha
M_suc = u.MRd(Lb, Cb=1.0, crit=cM)                # mesa inferior comprimida, travada pelas correntes a L/3
VRd = u.VRd()
casos = {}
for zona, c in cp.items():
    w_grav = (1.35 * g + 1.5 * q) * s
    w_suc = (1.4 * abs(c) * q0 - 1.0 * g) * s
    Mg, Ms = w_grav * L ** 2 / 8, w_suc * L ** 2 / 8
    Vg, Vs = w_grav * L / 2, w_suc * L / 2
    casos[zona] = dict(w_grav_kNm=round(w_grav, 3), w_suc_kNm=round(w_suc, 3),
                       grav=dict(Msd=round(Mg, 2), MRd=round(M_grav["MRd"], 2), modo=M_grav["modo"], uso=round(Mg / M_grav["MRd"], 3)),
                       suc=dict(Msd=round(Ms, 2), MRd=round(M_suc["MRd"], 2), modo=M_suc["modo"], uso=round(Ms / M_suc["MRd"], 3)),
                       V=dict(Vsd=round(max(Vg, Vs), 2), VRd=round(VRd, 1), uso=round(max(Vg, Vs) / VRd, 3)))
I = u.p["Ix"] * 1e-12
delta = lambda w: 5 * w * L ** 4 / (384 * 200e6 * I) * 1000
R["terca"] = dict(L_m=L, s_m=s, Lb_suc_mm=round(Lb), MRd_grav=M_grav, MRd_suc=M_suc, casos=casos,
                  flecha_gq_mm=round(delta((g + q) * s), 1), flecha_vento_mm=round(delta((abs(cp["geral"]) * q0 - g) * s), 1),
                  flecha_lim_mm=round(L * 1000 / 180, 1))

# terça escora (nós do contraventamento): compressão + flexão por sucção (vento longitudinal como principal)
Nd = 1.4 * N_escora_k
NRd = u.NcRd(L * 1000, Lb, Lb, crit=cN)
w_suc = (1.4 * abs(cp["geral"]) * q0 - g) * s
Md = w_suc * L ** 2 / 8
amp = 1 / (1 - Nd / NRd["Nex"])
inter = Nd / NRd["NcRd"] + Md * amp / M_suc["MRd"]
assert all(c["suc"]["uso"] <= 1 and c["grav"]["uso"] <= 1 for c in casos.values()) and inter <= 1, (casos, inter)
R["terca_escora"] = dict(Nd=round(Nd, 1), NcRd=round(NRd["NcRd"], 1), modo_N=NRd["modo"], Md=round(Md, 2), amplificacao=round(amp, 3),
                         MRd=round(M_suc["MRd"], 2), interacao=round(inter, 3), ok=inter <= 1.0,
                         nota="vento como ação principal; NBR 14762:2010 item 9.9 — Nc,Sd/Nc,Rd + Cm·Mx,Sd/[(1 − Nc,Sd/Nex)·Mx,Rd] ≤ 1, Cm = 1,0")

# ------------------------------------------------------------------ correntes (AISI S100-16 D3.2.1(a) — perfil C, carga uniforme)
d_terca = u.bw
a = L / (N_LIN + 1)
n_run = 13                      # terças por meia água entre ancoragens (beiral, meio do vão no eixo C, cumeeira alta)
casos_c = {}
for nome, wq, incl in (("sucção", (1.4 * abs(cp["geral"]) * q0 - g) * s, 0.0), ("gravidade", (1.35 * g + 1.5 * q) * s, 0.03)):
    W = wq * a
    PL = 1.5 * (u.m_ct / d_terca) * W + incl * W           # torção do perfil C + componente do caimento de 3%
    casos_c[nome] = dict(W_kN=round(W, 2), PL_por_terca_kN=round(PL, 3), F_acumulada_kN=round(PL * n_run, 2))
Fc = max(v["F_acumulada_kN"] for v in casos_c.values())
cf = barra_redonda_tracao_Rd(12.0)        # Ø12,5 rosqueada M12 — área da rosca pela barra Ø12
tubo = dict(D=42.2, t=2.65)
A_t = math.pi / 4 * (tubo["D"] ** 2 - (tubo["D"] - 2 * tubo["t"]) ** 2)
r_t = math.sqrt(tubo["D"] ** 2 + (tubo["D"] - 2 * tubo["t"]) ** 2) / 4
cr, lam0_cr, esb_cr = compressao_laminado_Rd(A_t, r_t, s * 1000, fy=250)
diag_len = math.hypot(s, L / 2)           # pior diagonal: a da corrente do meio do vão (L/2) até o apoio
T_diag = Fc * diag_len / s
td = barra_redonda_tracao_Rd(16.0)
R["correntes"] = dict(linhas_por_vao=N_LIN, posicao="a L/4, L/2 e 3L/4, furos Ø14 na alma a 75 mm da face inferior", casos=casos_c,
                      F_max_kN=Fc,
                      flexivel=dict(barra="Ø12,5 A36, roscas M12 + 2 porcas e arruela em cada terça", NtRd=round(cf, 1), uso=round(Fc / cf, 3)),
                      rigida=dict(perfil="tubo Ø42,2×2,65 (A36) com Ø12,5 passante", L_mm=s * 1000, NcRd=round(cr, 1),
                                  esbeltez=round(esb_cr), uso=round(Fc / cr, 3), onde="1º vão de terças junto a cada ancoragem"),
                      diagonal=dict(barra="Ø16 A36, rosca M16", comp_m=round(diag_len, 2), Td=round(T_diag, 1), NtRd=round(td, 1),
                                    uso=round(T_diag / td, 3), liga="do ponto de corrente da 2ª terça à cantoneira CT-1 da 1ª terça"))

# ------------------------------------------------------------------ cantoneira CT-1 e parafusos
Vsuc_end = casos["geral"]["w_suc_kNm"] * L / 2      # reação de arrancamento por terça
Vgrav_end = casos["geral"]["w_grav_kNm"] * L / 2
fu_terca = u.fu
b_web = pressao_contato_fino_Rd(12, 3.0, fu_terca)       # M12 na alma de 3,00
v_M12 = parafuso_corte_Rd(12, "8.8")
v_M16 = parafuso_corte_Rd(16, "8.8")
t_M16 = parafuso_tracao_Rd(16, "8.8")
# cada terça: 2 M12 na alma (força axial de escora + reação vertical) — resultante por parafuso
F_M12 = math.hypot(Nd / 2, Vsuc_end / 2)
# CT-1 recebe as 2 terças (topo a topo sobre a viga): arrancamento 2·Vsuc, cortante horizontal Nd (escora) ou T_diag·s/diag
T_ct = 2 * Vsuc_end
e_alavanca = 55 - 9.5                                     # furo M16 a 55 mm da face da aba vertical
M_aba = T_ct * e_alavanca / 2 / 1000                      # aba engastada-guiada (alavanca)
W_aba = 200 * 9.5 ** 2 / 4
MRd_aba = W_aba * 250 / 1.10 / 1e6
Q_alav = 0.25 * T_ct                                      # efeito alavanca estimado (25%)
T_M16 = (T_ct + Q_alav) / 2
V_M16 = Nd / 2
R["CT1"] = dict(perfil="L 102×102×9,5 (A36) L=200", reacao_suc_kN=round(Vsuc_end, 2), reacao_grav_kN=round(Vgrav_end, 2),
                M12_alma=dict(Fd=round(F_M12, 2), corte_Rd=round(v_M12, 1), contato_alma_Rd=round(b_web, 1),
                              uso=round(F_M12 / min(v_M12, b_web), 3), furo="Ø14 (padrão)", parafuso="M12 8.8, arruela lisa e porca"),
                M16_chapa=dict(Td=round(T_M16, 2), Vd=round(V_M16, 2), Ft_Rd=round(t_M16, 1), Fv_Rd=round(v_M16, 1),
                               interacao=round((T_M16 / t_M16) ** 2 + (V_M16 / v_M16) ** 2, 3),
                               parafuso="M16 8.8 na luva soldada da CH-T, furo Ø18 na aba"),
                aba=dict(Md_kNm=round(M_aba, 3), MRd_kNm=round(MRd_aba, 3), uso=round(M_aba / MRd_aba, 3)),
                contato_aba=round(pressao_contato_Rd(16, 9.5, 400, 35 - 9), 1),
                rasgamento_alma=dict(e_mm=45, Fd=round(Nd / 2, 2), Rd=round(3.0 * 45 * fu_terca / 1.45 / 1e3, 1),
                                     nota="NBR 14762:2010 10.3.1 — t·e·fu/1,45, furo a 45 mm da ponta da terça"))

# ------------------------------------------------------------------ mão-francesa MF-1 (fundo da viga → mesa inferior da terça)
e_carga = u.bf / 2 + u.m_ct            # carga na mesa superior (meio da mesa) × centro de torção
T_tors = casos["geral"]["w_suc_kNm"] * e_carga / 1000 * L / 2
H_mf = T_tors / (u.bw / 1000)          # binário cantoneira (topo) × mão-francesa (mesa inferior)
dz = 0.90 + 0.0125                      # fundo da viga I90 até a face inferior da terça
dy = 0.90                               # 45°
N_mf = H_mf * math.hypot(dy, dz) / dy
A_mf, r_mf = 4.80e2, 9.8                 # L 50×5: A = 4,80 cm², rz = 0,98 cm
Ncr_mf, l0_mf, esb_mf = compressao_laminado_Rd(A_mf, r_mf, math.hypot(dy, dz) * 1000)
R["MF1"] = dict(perfil="L 50×5 (A36)", comp_m=round(math.hypot(dy, dz), 2), angulo="45°", e_torcao_mm=round(e_carga, 1),
                T_apoio_kNm=round(T_tors, 3), H_kN=round(H_mf, 2), Nd_kN=round(N_mf, 2), NcRd=round(Ncr_mf, 1), esbeltez=round(esb_mf),
                uso=round(N_mf / Ncr_mf, 3), parafusos="M12 8.8 na mesa inferior da terça (furo Ø14) e M12 na orelha OR-1",
                contato_mesa_terca_Rd=round(pressao_contato_fino_Rd(12, 3.0, fu_terca), 1))

# ------------------------------------------------------------------ chumbadores (ACI 318-19 cap. 17), C50
# CH-T1 200×200: 4 pinos Ø16 c/ cabeça Ø32, hef 100, grade 150 × 150 (fora das luvas M16); mesa de 400 → borda lateral 125
# CH-T2 300×380: 6 pinos Ø16, grade 2 × 3 (s 200, y 2×150); borda lateral 200 − 150 = 50 → grampos de ancoragem
ch = {}
g1 = GrupoPinos(d=16, d_cabeca=32, hef=100, nx=2, ny=2, sx=150, sy=150, cx_neg=2000, cx_pos=2000, cy_neg=125, cy_pos=125, ha=200)
Nu1, Vu1 = T_ct, 0.0
Vx1 = T_diag * s / diag_len if True else 0.0      # 1ª terça das ancoragens das correntes: componente na direção da viga
t1, v1 = g1.tracao(), g1.cortante("x+")
ch["CH-T1"] = dict(pinos="4 Ø16 c/ cabeça, hef 100, nos cantos (grade 150×150)", Nu=round(Nu1, 1), Vu=round(Vx1, 1), phiNn=round(t1["phiNn_kN"], 1),
                   modoN=t1["modo"], phiVn=round(v1["phiVn_kN"], 1), modoV=v1["modo"],
                   interacao=round(interacao(Nu1, t1["phiNn_kN"], Vx1, v1["phiVn_kN"])[0], 3))
g2 = GrupoPinos(d=16, d_cabeca=32, hef=100, nx=2, ny=3, sx=200, sy=150, cx_neg=2000, cx_pos=2000, cy_neg=50, cy_pos=50, ha=200)
Vu2 = math.hypot(Nd, 2 * 1.4 * 9.1 * math.cos(math.radians(72.6)))     # escora (direção y) + 2 tirantes (componente x)
gr = grampo_ancoragem_kN(10, pernas=2)
t2 = g2.tracao()
v2_sem = g2.cortante("y+")
v2 = g2.cortante("y+", armadura_ancoragem_kN=2 * gr)
ch["CH-T2"] = dict(pinos="6 Ø16 c/ cabeça, hef 100 (2 × 3, s 200 × 150)", Nu=round(T_ct, 1), Vu=round(Vu2, 1),
                   phiNn=round(t2["phiNn_kN"], 1), modoN=t2["modo"], phiVn_sem_grampo=round(v2_sem["phiVn_kN"], 1),
                   grampos="2 grampos U Ø10 CA-50 envolvendo os pinos, pernas de 300 na mesa (ancoragem da cortante)",
                   phiVn=round(v2["phiVn_kN"], 1), modoV=v2["modo"],
                   interacao=round(interacao(T_ct, t2["phiNn_kN"], Vu2, v2["phiVn_kN"])[0], 3))
g3 = GrupoPinos(d=12.5, d_cabeca=25, hef=80, nx=1, ny=2, sx=0, sy=200, cx_neg=2000, cx_pos=2000, cy_neg=100, cy_pos=100, ha=150)
t3, v3 = g3.tracao(), g3.cortante("y+")
Nmf_v = 2 * N_mf * dz / math.hypot(dy, dz)
Vmf = 2 * H_mf
ch["CH-MF"] = dict(pinos="2 Ø12,5 c/ cabeça, hef 80", Nu=round(Nmf_v, 2), Vu=round(Vmf, 2), phiNn=round(t3["phiNn_kN"], 1),
                   phiVn=round(v3["phiVn_kN"], 1), interacao=round(interacao(Nmf_v, t3["phiNn_kN"], Vmf, v3["phiVn_kN"])[0], 3))
R["chumbadores"] = ch

(AQUI / "cobertura_metalica.json").write_text(json.dumps(R, indent=1, ensure_ascii=False, default=float), encoding="utf-8")
if __name__ == "__main__":
    print(json.dumps(R, indent=1, ensure_ascii=False, default=float)[:6000])
