"""Letsara — placa de fechamento maciça protendida 125 × 15 (horizontal, entre pilares). Gera placas.json.

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

b, h = 1.25, 0.15                      # altura da placa (no plano) e espessura
L = 10.165                             # maior placa (canto de fachada)
L_vao = 10.075                         # maior vão entre fixações
fck, fckj = 40.0, 25.0                 # fckj na liberação da protensão / desforma
Ec = 0.85 * 5600 * math.sqrt(fck)      # NBR 6118:2023 8.2.8 (Ecs, granito)
A = b * h
W_fora = b * h ** 2 / 6                # flexão fora do plano (vento)
W_plano = h * b ** 2 / 6               # flexão no plano (peso, estocagem em pé)
pp = A * 25

# ---------------------------------------------------------------- protensão: 8 cordoalhas Ø9,5 (4 por face, simétrico)
Ap1 = 55.5e-6                          # m² (Ø9,5 CP-190 RB)
n_c = 8
sig_pi = 1400.0                        # MPa na pista (≤ 0,77 fptk = 1463 — NBR 6118:2023 9.6.1.2.1)
F_macaco = sig_pi * Ap1 * 1e3          # kN por cordoalha
perdas = 0.20                          # perdas totais no infinito (estimativa: encurtamento + retração + fluência + relaxação)
P0 = n_c * F_macaco * (1 - 0.07)       # após a liberação (perdas imediatas ~7 %)
Pinf = n_c * F_macaco * (1 - perdas)
d_c = 0.040                            # eixo da cordoalha a 4 cm de cada face (cobrimento 3,5 cm ≥ 3,0 CAA II)
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
fct_f = 1.2 * fctk_inf                 # seção retangular (NBR 6118:2023 17.3.1: α = 1,2... conferir 1,5 p/ ret.)
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

# ---------------------------------------------------------------- transitórias (fckj = 25 MPa)
fctk_j = 0.7 * 0.3 * fckj ** (2 / 3)
# desforma deitada pelas 2 alças do topo com basculamento? — adota-se: desforma deitada por 4 pontos (2 alças + 2 insertos de desforma) a 0,207 L
M_desf = 0.0054 * pp * 1.3 * 1.2 * L ** 2        # 4 pontos com balancim (PCI) × dinâmico × sucção (por placa, fora do plano)
sig_desf = -P0 / A / 1e3 + M_desf / W_fora / 1e3
# içamento/montagem em pé pelas 2 alças do topo a 0,207 L: flexão no plano
M_ic = 0.0214 * pp * 1.3 * L ** 2
sig_ic = -P0 / A / 1e3 + M_ic / W_plano / 1e3
# estocagem deitada em 2 calços a 0,207 L (pilha de até 6 placas com calços alinhados)
M_est = 0.0214 * pp * L ** 2
sig_est = -P0 / A / 1e3 + M_est / W_fora / 1e3
# alça (2 alças, γdin 1,3, cabo a 60°)
F_alca = pp * L * 1.3 / 2 / math.sin(math.radians(60))
peso_t = pp * L / 9.81

# ---------------------------------------------------------------- fixação nos pilares (cantoneira CT-P, por ponta)
R_vento_ponta_d = 1.4 * w_k * L_vao / 2          # kN (cada ponta de cada placa)
R_grav_k_pacote2 = 2 * pp * L_vao / 2            # pacote suspenso de 2 placas (E/F) sobre 2 consolos CA-1: por consolo
R_grav_k_pacote3 = 3 * pp * L_vao / 2            # pacote de 3 placas sobre a faixa de esquadria (H/J/I)
# consolo metálico CA-1: chapa 16 mm em T (alma 150 × 200 + mesa 200 × 16) soldada no IP do pilar; solda filete 8 mm
R_ca_d = 1.4 * R_grav_k_pacote3
solda_Rd = 2 * 0.200 * 0.7 * 0.008 * 0.6 * 485e3 / 1.35          # kN (2 filetes de 200 mm, E70)
# cantoneira L 76 × 76 × 8 (furo oblongo 18 × 40 na aba da placa, M16 8.8; solda na aba do pilar) — corte do parafuso
Fv_M16 = 0.4 * 157e-6 * 800e3 / 1.35            # kN (NBR 8800:2008 6.3.3.2, rosca no plano de corte)

R = dict(
    secao=dict(b_m=b, h_m=h, A_m2=A, pp_kNm=round(pp, 2), L_max_m=L, peso_t=round(peso_t, 2), fck=fck, fckj=fckj, Ec_MPa=round(Ec)),
    protensao=dict(cordoalhas=f"{n_c} Ø9,5 CP-190 RB (4 por face, eixo a 4 cm das faces)", Ap_mm2=round(n_c * Ap1 * 1e6, 1),
                   sig_pi_MPa=sig_pi, F_macaco_kN=round(F_macaco, 1), P0_kN=round(P0, 1), Pinf_kN=round(Pinf, 1),
                   sig_cp_inf_MPa=round(sig_cp_inf, 2), along_pista_60m_mm=round(sig_pi / 195000 * 60000)),
    vento=dict(q0_kNm2=q0, cp_liq=cp_liq, p_k=round(p_k, 3), M_k=round(M_k, 2), M_d=round(M_d, 2), MRd=round(MRd, 2),
               uso_ELU=round(M_d / MRd, 3), sig_vento_MPa=round(sig_vento, 2), sig_ELS_F=round(sig_els_f, 2), sig_rara=round(sig_rara, 2),
               fct_f=round(fct_f, 2), ok_ELS_F=sig_els_f <= 0, ok_rara=sig_rara <= fct_f, flecha_mm=round(flecha, 1), lim_mm=round(lim_flecha, 1)),
    transitorias=dict(fctk_j=round(fctk_j, 2), sig_desforma=round(sig_desf, 2), sig_icamento=round(sig_ic, 2), sig_estocagem=round(sig_est, 2),
                      ok=all(s <= fctk_j / 1.5 for s in (sig_desf, sig_ic, sig_est)), F_alca_kN=round(F_alca, 1)),
    fixacoes=dict(R_vento_ponta_d=round(R_vento_ponta_d, 2), Fv_M16_Rd=round(Fv_M16, 1),
                  R_consolo_CA1_k=round(R_grav_k_pacote3, 1), R_consolo_CA1_d=round(R_ca_d, 1), solda_CA1_Rd=round(solda_Rd, 1),
                  ok=R_vento_ponta_d <= Fv_M16 and R_ca_d <= solda_Rd),
)
(AQ / "placas.json").write_text(json.dumps(R, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(R, indent=1, ensure_ascii=False))
