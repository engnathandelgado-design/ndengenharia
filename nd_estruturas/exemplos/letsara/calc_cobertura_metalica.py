"""Letsara — cobertura metálica: terças Ue, correntes, cantoneira CT-1, mão-francesa, chapas CH-T/CH-MF e chumbadores.

Rev. 13/10/2026: esforços da terça-escora e do X lidos do modelo global R01 (modelo_global_r01.json, envoltória por vão;
rodar modelo_global_r01.py antes); X só nos vãos 2-3 e 7-8; correntes Ø10; terça-escora verificada vão a vão com a sucção
do vento 0° (faixa do oitão com Cpe médio de borda).

Normas: NBR 14762:2010 (perfis formados a frio, MRD), NBR 8800:2008 (ligações, laminados), NBR 8681:2003 e
NBR 8800 Tabela 1 (combinações), NBR 6123:1988 (vento), ACI 318-19 cap. 17 (chumbadores), AISI S100-16 (forças
de travamento por correntes em perfis C). Unidades kN, m (perfis em mm).
"""
import json, math, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from nd_estruturas.metalica_fria import (PerfilUe, parafuso_corte_Rd, parafuso_tracao_Rd, pressao_contato_fino_Rd,
                                         pressao_contato_Rd, barra_redonda_tracao_Rd, compressao_laminado_Rd)
from nd_estruturas.ancoragem import GrupoPinos, interacao, grampo_ancoragem_kN

AQUI = Path(__file__).parent
R = {}

# ------------------------------------------------------------------ dados
from geometria import VAOS_Y
LG = json.loads((AQUI / "ligacoes.json").read_text(encoding="utf-8"))
L = max(VAOS_Y)      # maior vão de terça (eixos 2–3 e 3–4: 10,075 m); demais 9,625–10,0 m
s = LG["passo_tercas"]   # espaçamento entre terças (ao longo da água)
CC = LG["cargas_cob"]   # rev03: zipada 0,65 + lã de rocha 40 + TP40 0,50 + fixações + painéis solares + instalações (ligacoes.py)
PERFIL = tuple(float(v) for v in os.environ.get("ND_TERCA", "300,85,25,2.65").split(","))
q0 = 0.874           # kN/m² — V0 45 m/s, S2 cat. III classe C, S3 0,95 (rodada 2)
cp = dict(geral=-1.0, borda=-1.6)    # Cpe −0,8 / −1,4 (faixa de borda, NBR 6123 tab. 6 — conferir) com Cpi +0,2
MG = json.loads((AQUI / "modelo_global_r01.json").read_text(encoding="utf-8"))
ELU = {k: v for k, v in MG["combinacoes"].items() if v["tipo"] == "ELU"}
u = PerfilUe(*PERFIL, "ZAR345")
g = CC["g_total_sem_terca"] + u.peso_kNm / s          # kN/m² (gravidade)
g_fav = CC["g_favoravel_sucao"] + u.peso_kNm / s     # kN/m² (sucção: painéis e instalações desprezados, a favor da segurança)
q = CC["sobrecarga"]
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
    w_suc = (1.4 * abs(c) * q0 - 1.0 * g_fav) * s
    Mg, Ms = w_grav * L ** 2 / 8, w_suc * L ** 2 / 8
    Vg, Vs = w_grav * L / 2, w_suc * L / 2
    casos[zona] = dict(w_grav_kNm=round(w_grav, 3), w_suc_kNm=round(w_suc, 3),
                       grav=dict(Msd=round(Mg, 2), MRd=round(M_grav["MRd"], 2), modo=M_grav["modo"], uso=round(Mg / M_grav["MRd"], 3)),
                       suc=dict(Msd=round(Ms, 2), MRd=round(M_suc["MRd"], 2), modo=M_suc["modo"], uso=round(Ms / M_suc["MRd"], 3)),
                       V=dict(Vsd=round(max(Vg, Vs), 2), VRd=round(VRd, 1), uso=round(max(Vg, Vs) / VRd, 3)))
I = u.p["Ix"] * 1e-12
delta = lambda w: 5 * w * L ** 4 / (384 * 200e6 * I) * 1000
R["terca"] = dict(L_m=L, s_m=s, Lb_suc_mm=round(Lb), MRd_grav=M_grav, MRd_suc=M_suc, casos=casos,
                  flecha_gq_mm=round(delta((g + q) * s), 1), flecha_vento_mm=round(delta((abs(cp["geral"]) * q0 - g_fav) * s), 1),
                  flecha_lim_mm=round(L * 1000 / 180, 1))

# terça escora: compressão N (modelo global R01, por vão e por linha de terça) + flexão por sucção do MESMO vento, terça a
# terça. Vento é uma ação só: em cada combinação ELU com o vento como principal (ELU-1, 90°; ELU-2, 0°) o N daquela linha
# vem do modelo (γ 1,4 no vento; G 1,3 no N, a favor da segurança) e o M da sucção com γ 1,4 e g favorável (1,0).
# Telhado de uma água, θ ≈ 1,7° (NBR 6123:1988 tabela 6, menor θ tabelado). Zonas locais (Cpe médio de borda −1,4 + Cpi +0,2
# = −1,6), tomadas como envoltória e aplicadas nos dois ângulos (a favor da segurança):
#   - faixa do oitão: vãos 1-2 e 8-9 (terça inteira dentro de y = min(h; 0,15 b) da fachada — tomada inteira);
#   - faixas de beiral: terças a até y = min(h; 0,15 b) dos eixos A e E (linhas de beiral), em todos os vãos;
# demais terças: Ce −0,8 + Cpi +0,2 = −1,0.
from geometria import X_EIXO
H_COB = 9.9                                          # m — altura da cobertura (beiral alto)
B_MENOR = X_EIXO["E"]                                # m — menor dimensão em planta
Y_LOC = min(H_COB, 0.15 * B_MENOR)                   # largura das faixas locais (5,93 m)
VAO_FAIXA_OITAO = ("1-2", "8-9")
COMB_VENTO = {"ELU-1 vento x": "90°", "ELU-2 vento y": "0°"}
esc_vaos, esc_linhas = [], []
for iv, Lv in enumerate(VAOS_Y):
    nome = f"{iv+1}-{iv+2}"
    Lb_v = Lv / (N_LIN + 1) * 1000
    NR = u.NcRd(Lv * 1000, Lb_v, Lb_v, crit=u.criticos("N", L_dist_ref=cM["L_dist"]))
    MR = u.MRd(Lb_v, Cb=1.0, crit=cM)
    pior = None
    for comb, ang_v in COMB_VENTO.items():
        for xs_, (nmin, _) in MG["combinacoes"][comb]["por_vao"]["terça-escora por linha"].get(nome, {}).items():
            x_ = float(xs_)
            beiral = x_ <= Y_LOC or x_ >= B_MENOR - Y_LOC
            zona = "borda" if (nome in VAO_FAIXA_OITAO or beiral) else "geral"
            Nd_l = max(0.0, -nmin)
            if abs(x_ - X_EIXO["C"]) < 0.01:             # linha do eixo C no modelo = 2 terças reais (última de cada TS-01, a ±292,5 mm do eixo)
                Nd_l /= 2
            w_l = (1.4 * abs(cp[zona]) * q0 - g_fav) * s
            Md_l = w_l * Lv ** 2 / 8
            amp_l = 1 / (1 - Nd_l / NR["Nex"])
            it = Nd_l / NR["NcRd"] + Md_l * amp_l / MR["MRd"]
            reg_ = dict(vao=nome, x_m=x_, faixa=" + ".join(f_ for f_, c_ in (("oitão", nome in VAO_FAIXA_OITAO), ("beiral", beiral)) if c_) or "interna",
                        vento=ang_v, cp=cp[zona], L_m=Lv, Nd=round(Nd_l, 1), NcRd=round(NR["NcRd"], 1), modo_N=NR["modo"], Md=round(Md_l, 2),
                        MRd=round(MR["MRd"], 2), amplificacao=round(amp_l, 3), interacao=round(it, 3))
            esc_linhas.append(reg_)
            if pior is None or it > pior["interacao"]:
                pior = reg_
    esc_vaos.append(pior)
gov = max(esc_linhas, key=lambda e: e["interacao"])
Nd = max(e["Nd"] for e in esc_linhas)                     # maior compressão de escora (ligações CT-1 / CH-T2)
bei = [e for e in esc_linhas if "beiral" in e["faixa"]]
gov_bei = max(bei, key=lambda e: e["interacao"])
assert all(c["suc"]["uso"] <= 1 and c["grav"]["uso"] <= 1 for c in casos.values()) and gov["interacao"] <= 1, (casos, gov)
R["terca_escora"] = dict(Nd=gov["Nd"], NcRd=gov["NcRd"], modo_N=gov["modo_N"], Md=gov["Md"], amplificacao=gov["amplificacao"],
                         MRd=gov["MRd"], interacao=gov["interacao"], ok=gov["interacao"] <= 1.0, vao_governante=gov["vao"],
                         linha_governante_x_m=gov["x_m"], faixa_governante=gov["faixa"], vento_governante=gov["vento"], Nd_max=Nd,
                         faixa_beiral=dict(y_m=round(Y_LOC, 2), Nd_max=max(e["Nd"] for e in bei), governante=gov_bei),
                         por_vao=esc_vaos, fonte="modelo_global_r01.json (ELU-1 e ELU-2, por vão e por linha de terça)",
                         nota="N e M do mesmo vento (0° ou 90°), γ 1,4; faixas locais de oitão e de beiral (y = min(h; 0,15 b)) com Cpe médio −1,4 "
                              "+ Cpi +0,2 em envoltória; demais Ce −0,8 + Cpi +0,2 (NBR 6123:1988 tabela 6); NBR 14762:2010 item 9.9 — "
                              "Nc,Sd/Nc,Rd + Cm·Mx,Sd/[(1 − Nc,Sd/Nex)·Mx,Rd] ≤ 1, Cm = 1,0")

# ------------------------------------------------------------------ correntes (AISI S100-16 D3.2.1(a) — perfil C, carga uniforme)
d_terca = u.bw
a = L / (N_LIN + 1)
n_run = len(LG["s_tercas"])     # terças por meia água entre ancoragens (beiral, meio do vão no eixo C, cumeeira alta)
casos_c = {}
for nome, wq, incl in (("sucção", (1.4 * abs(cp["geral"]) * q0 - g_fav) * s, 0.0), ("gravidade", (1.35 * g + 1.5 * q) * s, 0.03)):
    W = wq * a
    PL = 1.5 * (u.m_ct / d_terca) * W + incl * W           # torção do perfil C + componente do caimento de 3%
    casos_c[nome] = dict(W_kN=round(W, 2), PL_por_terca_kN=round(PL, 3), F_acumulada_kN=round(PL * n_run, 2))
Fc = max(v["F_acumulada_kN"] for v in casos_c.values())
D_COR = 10.0                               # corrente flexível Ø10 A36, rosca M10 (rev. 13/10/2026; antes Ø12,5)
cf = barra_redonda_tracao_Rd(D_COR)
# tirante rígido (1º espaço de terças junto a cada ancoragem): L 51×51×3,2 (A36), A 3,13 cm², rz 1,00 cm
A_L51, rz_L51 = 313.0, 10.0
cr, lam0_cr, esb_cr = compressao_laminado_Rd(A_L51, rz_L51, s * 1000, fy=250)
# diagonais de ancoragem (Λ) no 1º espaço: do nó da corrente na 2ª terça até o suporte ST-1 da 1ª terça (na viga):
# L/4 → apoio mais próximo; L/2 → os dois apoios (metade da força em cada); 3L/4 → apoio mais próximo
d_q = math.hypot(s, L / 4); d_m = math.hypot(s, L / 2)
T_q, T_m = Fc * d_q / s, Fc / 2 * d_m / s
T_diag, diag_len = max(T_q, T_m), (d_q if T_q >= T_m else d_m)
td = barra_redonda_tracao_Rd(16.0)
R["correntes"] = dict(linhas_por_vao=N_LIN, posicao="a L/4, L/2 e 3L/4, furo Ø12 no meio da alma (150 do fundo)", casos=casos_c,
                      F_max_kN=Fc,
                      flexivel=dict(barra="Ø10 A36, roscas M10, porca + contraporca e arruela dos 2 lados de cada terça", d_mm=D_COR, furo="Ø12",
                                    NtRd=round(cf, 1), uso=round(Fc / cf, 3)),
                      rigida=dict(perfil="L 51×51×3,2 (A36), presa em clipe L 32×32×3 com 1 M10 em furo oval 11×23 na alma", L_mm=round(s * 1000), NcRd=round(cr, 1),
                                  esbeltez=round(esb_cr), uso=round(Fc / cr, 3), onde="1º espaço de terças junto a cada ancoragem (beiral e eixo C de cada meia água)"),
                      diagonal=dict(barra="Ø16 A36, rosca M16", comp_L4_m=round(d_q, 2), comp_L2_m=round(d_m, 2), Td_L4=round(T_q, 1), Td_L2=round(T_m, 1),
                                    Td=round(T_diag, 1), NtRd=round(td, 1), uso=round(T_diag / td, 3),
                                    liga="do nó da corrente na 2ª terça (L/4, L/2, 3L/4) ao furo Ø18 do ST-1 da 1ª terça, na viga"))

# ------------------------------------------------------------------ contraventamento em X (padrão das coberturas de referência)
# Treliça no plano da cobertura: cordas = vigas TS-01 das duas linhas do vão; montantes = terças dos nós (escoras, a cada
# 2 espaços de terças); diagonais em X Ø16 A36 de nó a nó (CH-T2 de uma viga à CH-T2 da outra), cada uma com esticador.
T_X_d = max(c["forcas_barras"].get("X Ø16", [0.0, 0.0])[1] for c in ELU.values())      # tração de cálculo na diagonal (modelo R01)
P_X = 2 * s
amostra = LG["contraventamento"]["amostra"][0]
L_X = amostra["comp_m"]
ang = math.radians(amostra["ang_eixo_viga"])
T_X = T_X_d
V_d = T_X * math.sin(ang)                                                          # cortante do painel (componente y)
t16 = barra_redonda_tracao_Rd(16.0)
Fx_no = 2 * T_X * math.cos(ang)                                                    # 2 diagonais no mesmo nó (painéis vizinhos)
Fy_no = 2 * T_X * math.sin(ang)
R["contraventamento"] = dict(painel_x_m=round(P_X, 3), subpaineis=1, L_diag_m=L_X, ang_graus=amostra["ang_eixo_viga"],
                             vaos=["2-3", "7-8"], fonte="modelo_global_r01.json (máx. ELU)", V_painel_d=round(V_d, 1), T_diag_d=round(T_X, 2),
                             NtRd_16=round(t16, 1), uso_diag=round(T_X / t16, 3),
                             no=dict(Fx_kN=round(Fx_no, 2), Fy_kN=round(Fy_no, 2)),
                             barra="Ø16 A36 em 2 trechos (≈ 9,0 m + 1,2 m) unidos por esticador M16 (rosca direita/esquerda), pré-tensão manual",
                             nota="X de nó a nó das vigas, abrangendo 2 espaços de terças, só nos vãos 2-3 e 7-8 (vizinhos aos oitões); terças dos nós trabalham como escoras")

# ------------------------------------------------------------------ suporte ST-1P (rev03): chapa dobrada 9,5 mm A36, sem solda,
# parafusada em 2 esperas de barra roscada M16 (ASTM A36, rosca laminada, gancho na ponta) concretadas na mesa superior da TS-01,
# a ±60 mm do eixo da viga, 120 mm acima do concreto; furos oblongos 18 × 40 na aba horizontal (ajuste ±11 mm). Terças com 2 M12 8.8.
Vsuc_end = casos["geral"]["w_suc_kNm"] * L / 2      # reação de arrancamento por terça
Vgrav_end = casos["geral"]["w_grav_kNm"] * L / 2
fu_terca = u.fu
b_web = pressao_contato_fino_Rd(12, u.t, fu_terca)       # M12 na alma da terça
v_M12 = parafuso_corte_Rd(12, "8.8")
F_M12 = math.hypot(Nd / 2, Vsuc_end / 2)
T_st = 2 * Vsuc_end                                       # 2 terças (topo a topo) no mesmo suporte
e_al = 75 - 9.5 - 8                                       # espera a 75 mm da dobra; braço até a face da aba vertical − raio
M_aba = T_st * 1.25 * e_al / 2 / 1000                     # alavanca (+25 %)
MRd_aba = 220 * 9.5 ** 2 / 4 * 250 / 1.10 / 1e6
Ab16 = 157.0                                              # área efetiva da rosca M16
Ft_esp = 0.75 * math.pi * 16 ** 2 / 4 * 400 / 1.35 / 1e3     # NBR 8800 6.3.3.1 (barra redonda rosqueada A36: fu 400)
Fv_esp = 0.4 * math.pi * 16 ** 2 / 4 * 400 / 1.35 / 1e3
Td_esp, Vd_esp = T_st * 1.25 / 2, Nd / 2
R["ST1P"] = dict(peca="chapa dobrada 9,5 × 220 (aba vertical 290, aba horizontal 150) A36 galvanizada", reacao_suc_kN=round(Vsuc_end, 2), reacao_grav_kN=round(Vgrav_end, 2),
                 M12_alma=dict(Fd=round(F_M12, 2), corte_Rd=round(v_M12, 1), contato_alma_Rd=round(b_web, 1), uso=round(F_M12 / min(v_M12, b_web), 3)),
                 aba=dict(Md_kNm=round(M_aba, 3), MRd_kNm=round(MRd_aba, 3), uso=round(M_aba / MRd_aba, 3)),
                 esperas=dict(barra="2 barras roscadas M16 A36 (fu 400) com gancho, hef 150, saliência 120", Td=round(Td_esp, 2), Vd=round(Vd_esp, 2),
                              Ft_Rd=round(Ft_esp, 1), Fv_Rd=round(Fv_esp, 1), interacao=round((Td_esp / Ft_esp) ** 2 + (Vd_esp / Fv_esp) ** 2, 3)),
                 rasgamento_alma=dict(e_mm=45, Fd=round(Nd / 2, 2), Rd=round(u.t * 45 * fu_terca / 1.45 / 1e3, 1)))

# ------------------------------------------------------------------ mão-francesa MF-1 (rev03): da espera horizontal na lateral da mesa inferior da
# TS-01 (barra roscada M16, saliência 60 mm, a 100 mm do fundo, hef 110 com porca e arruela na ponta) à alma da terça; L 50×5 parafusada (sem solda), 45°
e_carga = u.bf / 2 + u.m_ct            # carga na mesa superior (meio da mesa) × centro de torção
T_tors = casos["geral"]["w_suc_kNm"] * e_carga / 1000 * L / 2
H_mf = T_tors / (u.bw / 1000)          # binário ST-1P (topo) × mão-francesa (mesa inferior)
dz = 0.90 + 0.010 + 0.040 - 0.100       # espera (100 do fundo da viga) até o furo da MF na alma da terça (40 acima do fundo dela)
dy = 1.07 - 0.20                        # furo da terça a 1070 do eixo da viga; espera na face lateral (b/2 = 200)
N_mf = H_mf * math.hypot(dy, dz) / dy
A_mf, r_mf = 4.80e2, 9.8                 # L 50×5: A = 4,80 cm², rz = 0,98 cm
Ncr_mf, l0_mf, esb_mf = compressao_laminado_Rd(A_mf, r_mf, math.hypot(dy, dz) * 1000)
R["MF1"] = dict(perfil="L 50×5 (A36)", comp_m=round(math.hypot(dy, dz), 2), angulo=f"{math.degrees(math.atan2(dz, dy)):.0f}°", e_torcao_mm=round(e_carga, 1),
                T_apoio_kNm=round(T_tors, 3), H_kN=round(H_mf, 2), Nd_kN=round(N_mf, 2), NcRd=round(Ncr_mf, 1), esbeltez=round(esb_mf),
                uso=round(N_mf / Ncr_mf, 3), parafusos="M12 8.8 na alma da terça (furo Ø14 a 40 mm do fundo) e porca M16 na espera da viga (furo Ø18 na aba da MF)",
                contato_alma_terca_Rd=round(pressao_contato_fino_Rd(12, u.t, fu_terca), 1),
                espera=dict(barra="barra roscada M16 A36 horizontal, hef 110 na mesa inferior (a 100 do fundo), porca + arruela 40×40×6 na ponta, saliência 60", Vd=round(N_mf, 2), Fv_Rd=round(Fv_esp, 1),
                            uso=round(N_mf / Fv_esp, 3)))

# ------------------------------------------------------------------ esperas no concreto (ACI 318-19 cap. 17), C50
# ST-1P: 2 M16 com gancho (≈ pino com cabeça de 32 mm), hef 150, s 120 em y; mesa superior 400 (borda lateral 140)
ch = {}
g1 = GrupoPinos(d=16, d_cabeca=32, hef=150, nx=1, ny=2, sx=0, sy=120, cx_neg=2000, cx_pos=2000, cy_neg=140, cy_pos=140, ha=900)
Nu1 = T_st * 1.25
Vx1 = T_diag * s / diag_len           # 1ª terça das ancoragens das correntes: componente na direção da viga
t1, v1 = g1.tracao(), g1.cortante("x+")
ch["ST-1P"] = dict(esperas="2 M16 com gancho, hef 150 (s 120)", Nu=round(Nu1, 1), Vu=round(Vx1, 1), phiNn=round(t1["phiNn_kN"], 1),
                   modoN=t1["modo"], phiVn=round(v1["phiVn_kN"], 1), modoV=v1["modo"],
                   interacao=round(interacao(Nu1, t1["phiNn_kN"], Vx1, v1["phiVn_kN"])[0], 3))
# nó do X (vãos 2-3 e 7-8): ST-1P + 2 OR-X (L 76×76×6,3) cada uma em 1 espera M16 a y = ±140 (borda 60) com grampo U Ø10
g2 = GrupoPinos(d=16, d_cabeca=32, hef=110, nx=1, ny=1, sx=0, sy=0, cx_neg=2000, cx_pos=2000, cy_neg=60, cy_pos=340, ha=900)
gr = grampo_ancoragem_kN(10, pernas=2)
T_or = T_X_d
v2 = g2.cortante("y-", armadura_ancoragem_kN=gr)
Vor = 2 * T_or                          # 2 diagonais do X na mesma orelha (painéis vizinhos), a favor da segurança
ch["OR-X"] = dict(esperas="1 M16 com gancho por orelha, hef 110 + grampo U Ø10", Vu=round(Vor, 1), phiVn=round(v2["phiVn_kN"], 1), modoV=v2["modo"],
                  uso=round(Vor / v2["phiVn_kN"], 3))
g3 = GrupoPinos(d=16, d_cabeca=40, hef=110, nx=1, ny=1, sx=0, sy=0, cx_neg=100, cx_pos=100, cy_neg=2000, cy_pos=2000, ha=400)
t3, v3 = g3.tracao(), g3.cortante("x+")
Nmf_h = N_mf * dy / math.hypot(dy, dz); Vmf = N_mf * dz / math.hypot(dy, dz)
ch["MF-espera"] = dict(esperas="1 M16 horizontal por lado, hef 110, a 100 do fundo", Nu=round(Nmf_h, 2), Vu=round(Vmf, 2), phiNn=round(t3["phiNn_kN"], 1),
                       phiVn=round(v3["phiVn_kN"], 1), interacao=round(interacao(Nmf_h, t3["phiNn_kN"], Vmf, v3["phiVn_kN"])[0], 3))
R["chumbadores"] = ch

(AQUI / "cobertura_metalica.json").write_text(json.dumps(R, indent=1, ensure_ascii=False, default=float), encoding="utf-8")
if __name__ == "__main__":
    print(json.dumps(R, indent=1, ensure_ascii=False, default=float)[:6000])
