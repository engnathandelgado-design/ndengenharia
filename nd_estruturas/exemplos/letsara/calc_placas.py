"""Letsara — placa de fechamento maciça protendida 125 × 10 (rev03; antes 125 × 15), horizontal, entre pilares. Gera placas.json.

Esquema: placas empilhadas (junta macho-fêmea com tira de elastômero), a de baixo de cada pilha apoiada na viga
baldrame (contínuo) ou, nos panos abertos embaixo, em 2 consolos metálicos CA-1 nos pilares; fixação fora do plano
nas duas pontas por cantoneira soldada no inserto do pilar (IP) e no inserto da placa (CH-P). Fechamento isostático
e flexível: não entra no contraventamento.
Normas: NBR 6118:2023 (ELU/ELS, protensão limitada), NBR 9062:2017 (transitórias, γ = 1,3 dinâmico), NBR 6123:2023
(vento), NBR 7483 (cordoalha CP-190 RB). Unidades: kN, m; MPa nas tensões. Compressão negativa nas tensões.
"""
import json
import math
from pathlib import Path

AQ = Path(__file__).parent
CB = json.loads((AQ / "cobertura_metalica.json").read_text(encoding="utf-8")) if (AQ / "cobertura_metalica.json").exists() else {}

b, h = 1.25, 0.10                      # altura da placa (no plano) e espessura — rev03: 10 cm (Nathan, 13/10/2026)
L = 10.165                             # maior placa (canto de fachada)
L_vao = 10.075                         # maior vão entre fixações
fck, fckj = 40.0, 25.0                 # fckj na liberação da protensão / desforma
Ec = 0.85 * 5600 * math.sqrt(fck)      # NBR 6118:2023 8.2.8 (Ecs, granito)
A = b * h
W_fora = b * h ** 2 / 6                # flexão fora do plano (vento)
W_plano = h * b ** 2 / 6               # flexão no plano (peso, estocagem em pé)
pp = A * 25

# ---------------------------------------------------------------- protensão: 8 cordoalhas Ø12,7 (4 por face, alinhadas, simétrico)
Ap1 = 98.7e-6                          # m² (Ø12,7 CP-190 RB)
n_c = 8
sig_pi = 1400.0                        # MPa na pista (≤ 0,77 fptk = 1463 — NBR 6118:2023 9.6.1.2.1)
F_macaco = sig_pi * Ap1 * 1e3          # kN por cordoalha
# DEC-032: perdas pela NBR 6118:2023 9.6.3 (prefabricados.perdas_pretracao) no lugar de 7 % / 20 % fixos — protensão
# centrada (yp = yc), placa estocada deitada (Mg em t0 desprezado, a favor), U 70 %, idade fictícia 5 dias, as 2 faces ao ar
from nd_estruturas.prefabricados import perdas_pretracao, lbpt_cordoalha, Concreto as _Conc
PERD = perdas_pretracao(sig_pi, n_c * Ap1, A, b * h ** 3 / 12, h / 2, h / 2, 0.0, _Conc(fck), fckj, 2 * (b + h), U=70.0, t0_dias=5.0)
GAMA_P = 1.1                           # ato da protensão (NBR 6118:2023 17.2.4.3.2 a)
P0 = PERD["P0"]                        # após a liberação
Pinf = PERD["Pinf"]
perdas = PERD["perda_total_pct"] / 100
LBPT = lbpt_cordoalha(fckj, PERD["sig_p0"], gradual=True)[0]        # 9.4.5 — liberação gradual (indicada na prancha)
LBPT_BRUSCA = lbpt_cordoalha(fckj, PERD["sig_p0"], gradual=False)[0]
d_c = 0.020 + 0.0127 / 2               # cobrimento 2,0 cm (Nathan, 13/10/2026; redução por controle de fábrica — NBR 9062) → eixo a 2,64 cm
sig_cp_inf = -Pinf / A / 1e3           # MPa (protensão centrada)

# ---------------------------------------------------------------- vento (NBR 6123:2023): q0 do estudo da obra, coef. líquido de zona de borda
q0 = 0.874                             # kN/m² (V0 45 m/s, S2 cat. III classe C) — calc_letsara_r2
cp_liq = 1.4 + 0.2                     # Cpe −1,4 (faixa de borda) + Cpi +0,2 → 1,6 (a favor da segurança em todas as placas)
p_k = q0 * cp_liq                      # kN/m²
w_k = p_k * b                          # kN/m na placa
M_k = w_k * L_vao ** 2 / 8
M_d = 1.4 * M_k
sig_vento = M_k / W_fora / 1e3         # MPa
fctm = 0.3 * fck ** (2 / 3)
fctk_inf = 0.7 * fctm
fct_f = 1.5 * fctk_inf                 # seção retangular: α = 1,5 (NBR 6118:2023 17.3.1)
# ELS-F (combinação frequente, ψ1 vento 0,3) e ELS-D (quase permanente, ψ2 = 0): protensão limitada (CAA II)
sig_els_f = sig_cp_inf + 0.3 * sig_vento
sig_rara = sig_cp_inf + sig_vento
# ELU fora do plano: 4 cordoalhas tracionadas a d = h − 4 cm; fpyd ≈ 0,9·1710/1,15
fpd = 1710 / 1.15
Ap_t = 4 * Ap1
d = h - d_c
fcd = fck / 1.4
x = Ap_t * fpd / (0.85 * fcd * 0.8 * b)          # m (bloco retangular λ 0,8, αc 0,85)
MRd = Ap_t * fpd * 1e3 * (d - 0.4 * x)           # kN·m
# flecha fora do plano (vento característico, seção bruta, protendida não fissurada)
I_fora = b * h ** 3 / 12
flecha = 5 * w_k * L_vao ** 4 / (384 * Ec * 1e3 * I_fora) * 1000     # mm
lim_flecha = L_vao * 1000 / 250
flecha_freq = 0.3 * flecha                                       # combinação frequente (ψ1 vento 0,3) — critério adotado (rev03)

# ---------------------------------------------------------------- transitórias (fckj = 25 MPa)
fctk_j = 0.7 * 0.3 * fckj ** (2 / 3)
# desforma deitada pelas 2 alças do topo com basculamento? — adota-se: desforma deitada por 4 pontos (2 alças + 2 insertos de desforma) a 0,207 L
M_desf = 0.0054 * pp * 1.3 * 1.2 * L ** 2        # 4 pontos com balancim (PCI) × dinâmico × sucção (por placa, fora do plano)
sig_desf = -GAMA_P * P0 / A / 1e3 + M_desf / W_fora / 1e3
# içamento/montagem em pé pelas 2 alças do topo a 0,207 L: flexão no plano
M_ic = 0.0214 * pp * 1.3 * L ** 2
sig_ic = -GAMA_P * P0 / A / 1e3 + M_ic / W_plano / 1e3
# estocagem deitada em 2 calços a 0,207 L (pilha de até 6 placas com calços alinhados)
M_est = 0.0214 * pp * L ** 2
sig_est = -GAMA_P * P0 / A / 1e3 + M_est / W_fora / 1e3
# alça (2 alças, γdin 1,3, cabo a 60°)
F_alca = pp * L * 1.3 / 2 / math.sin(math.radians(60))
peso_t = pp * L / 9.81

# ---------------------------------------------------------------- fixação nos pilares — rev03: tudo parafusado, sem solda
R_vento_ponta_d = 1.4 * w_k * L_vao / 2          # kN (cada ponta de cada placa)
R_grav_k_pacote2 = 2 * pp * L_vao / 2            # pacote suspenso de 2 placas (E/F) sobre 2 consolos CA-1: por consolo
R_grav_k_pacote3 = 3 * pp * L_vao / 2            # pacote de 3 placas sobre a faixa de esquadria (H/J/I)
R_ca_d = 1.4 * R_grav_k_pacote3
# CL-1: cantoneira L 102×102×12,5 A36, L = 150: aba 1 na face lateral do pilar (parafuso T M16 8.8 no trilho vertical TR-1),
# aba 2 na face interna da placa (M16 8.8 na bucha BR-1 embutida na placa, furo oblongo 18×40 horizontal). Flexão da aba no canto:
# braço = 50 mm (eixo do furo à face da outra aba) — NBR 8800:2008 5.4.2.2 (seção retangular, plastificação limitada a 1,0 Wel·fy)
fy36 = 250e3
M_cl = R_vento_ponta_d * 0.050
MRd_cl = 0.150 * 0.0125 ** 2 / 6 * fy36 / 1.10
Ft_M16 = 0.75 * 201e-6 * 800e3 / 1.35            # kN (NBR 8800:2008 6.3.3.1)
Fv_M16 = 0.4 * 157e-6 * 800e3 / 1.35            # kN (NBR 8800:2008 6.3.3.2, rosca no plano de corte)
# CA-1: cantoneira L 152×102×19 A572-50, L = 300, aba de 152 horizontal (assento do pacote), aba de 102 pendurada, 2 M20 8.8 nas
# luvas roscadas IB-1 do pilar (face C), a 60 mm abaixo do assento. Carga no assento a e = 25 + 50 = 75 mm da face do pilar.
fy50 = 345e3
e_ca = 0.075
M_ca = R_ca_d * (e_ca - 0.019 - 0.010)             # na raiz da aba horizontal (espessura + raio)
MRd_ca = 0.300 * 0.019 ** 2 / 6 * fy50 / 1.10
T_ca = R_ca_d * e_ca / 0.060 / 2                   # tração por parafuso (binário com o apoio da aba na base)
V_ca = R_ca_d / 2
Ft_M20 = 0.75 * 314e-6 * 800e3 / 1.35
Fv_M20 = 0.4 * 245e-6 * 800e3 / 1.35
int_ca = (T_ca / Ft_M20) ** 2 + (V_ca / Fv_M20) ** 2

R = dict(
    secao=dict(b_m=b, h_m=h, A_m2=A, pp_kNm=round(pp, 2), L_max_m=L, peso_t=round(peso_t, 2), fck=fck, fckj=fckj, Ec_MPa=round(Ec)),
    protensao=dict(cordoalhas=f"{n_c} Ø12,7 CP-190 RB (4 por face, alinhadas, eixo a 2,6 cm das faces)", Ap_mm2=round(n_c * Ap1 * 1e6, 1),
                   sig_pi_MPa=sig_pi, F_macaco_kN=round(F_macaco, 1), P0_kN=round(P0, 1), Pinf_kN=round(Pinf, 1),
                   sig_cp_inf_MPa=round(sig_cp_inf, 2), along_pista_60m_mm=round(sig_pi / 195000 * 60000),
                   perda_imediata_pct=round(PERD["perda_imediata_pct"], 1), perda_total_pct=round(PERD["perda_total_pct"], 1), phi=round(PERD["phi"], 2),
                   lbpt_gradual_m=round(LBPT, 2), lbpt_brusca_m=round(LBPT_BRUSCA, 2), gama_p_ato=GAMA_P, sig_ato_MPa=round(-GAMA_P * P0 / A / 1e3, 2),
                   lim_ato_MPa=round(-0.7 * fckj, 1), norma="NBR 6118:2023 9.6.3 (perdas), 9.4.5 (lbpt), 17.2.4.3.2 (ato)"),
    vento=dict(q0_kNm2=q0, cp_liq=cp_liq, p_k=round(p_k, 3), M_k=round(M_k, 2), M_d=round(M_d, 2), MRd=round(MRd, 2),
               uso_ELU=round(M_d / MRd, 3), x_d=round(x / d, 3), sig_vento_MPa=round(sig_vento, 2), sig_ELS_F=round(sig_els_f, 2), sig_rara=round(sig_rara, 2),
               fct_f=round(fct_f, 2), ok_ELS_F=sig_els_f <= 0, ok_rara=sig_rara <= fct_f, flecha_mm=round(flecha, 1), flecha_freq_mm=round(flecha_freq, 1), lim_mm=round(lim_flecha, 1), ok_flecha=flecha_freq <= lim_flecha),
    transitorias=dict(fctk_j=round(fctk_j, 2), sig_desforma=round(sig_desf, 2), sig_icamento=round(sig_ic, 2), sig_estocagem=round(sig_est, 2),
                      ok=all(s <= fctk_j / 1.5 for s in (sig_desf, sig_ic, sig_est)), F_alca_kN=round(F_alca, 1)),
    fixacoes=dict(R_vento_ponta_d=round(R_vento_ponta_d, 2), Fv_M16_Rd=round(Fv_M16, 1), Ft_M16_Rd=round(Ft_M16, 1),
                  CL1=dict(peca="L 102×102×12,5 A36 L=150", M_kNm=round(M_cl, 3), MRd_kNm=round(MRd_cl, 3), uso=round(M_cl / MRd_cl, 3),
                           trilho="TR-1 tipo HTA-CE 40/22 (ou equivalente): carga de cálculo ≥ 12,4 kN por ponto (catálogo)",
                           bucha="BR-1 bucha M16 com barra transversal, hef ≥ 70 (catálogo, ≥ 12,4 kN)"),
                  R_consolo_CA1_k=round(R_grav_k_pacote3, 1), R_consolo_CA1_d=round(R_ca_d, 1),
                  CA1=dict(peca="L 152×102×19 A572-50 L=300 + 2 M20 8.8 em luvas IB-1", M_kNm=round(M_ca, 2), MRd_kNm=round(MRd_ca, 2),
                           uso_aba=round(M_ca / MRd_ca, 3), T_parafuso=round(T_ca, 1), V_parafuso=round(V_ca, 1), interacao_M20=round(int_ca, 3)),
                  ok=R_vento_ponta_d <= Fv_M16 and M_cl <= MRd_cl and M_ca <= MRd_ca and int_ca <= 1),
)
(AQ / "placas.json").write_text(json.dumps(R, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(R, indent=1, ensure_ascii=False))
