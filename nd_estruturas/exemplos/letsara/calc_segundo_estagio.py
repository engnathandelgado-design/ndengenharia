"""Letsara — MC04: 2º estágio das vigas do mezanino VM (I90 protendida + laje alveolar h20 + capa 5 cm).

Análise em duas fases (NBR 9062:2017 item 6.3; NBR 6118:2023 item 17.4.2 para armadura mínima transversal):
  fase 1 — seção pré-moldada I90 isolada, sem escora: peso próprio + laje alveolar + capa fresca;
  fase 2 — seção composta (I90 + enchimento entre as pontas das lajes + capa C25 na largura colaborante):
           revestimento + sobrecarga. Tensões somadas às residuais da fase 1.
Cisalhamento na interface pré-moldado × concreto moldado no local: NBR 9062:2017 item 6.3.5
  τsd = Vsd / (b·d)  ≤  τRd = βs·ρ·fyd + βc·fctd  ≤ 0,25·fcd   (βs, βc da Tabela de rugosidade da 9062 — conferir)
Armadura de 2º estágio (estribos salientes N9) calculada pela interface e pelo mínimo, para a obra executar na solidarização.
Unidades: kN, m, MPa só na entrada. Compressão negativa.
"""
import json
import math
from pathlib import Path

AQ = Path(__file__).parent


def poli_props(pts):
    """Área, centroide (y) e inércia Iz em torno do centroide de um polígono (shoelace). pts em m."""
    A = Sy = Iy0 = 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        c = x0 * y1 - x1 * y0
        A += c / 2
        Sy += (y0 + y1) * c / 6
        Iy0 += (y0 ** 2 + y0 * y1 + y1 ** 2) * c / 12
    yc = Sy / A
    return A, yc, Iy0 - A * yc ** 2


# ---------------------------------------------------------------- geometria (mm → m)
b, h, ts, ti, m, bw = 0.40, 0.90, 0.12, 0.15, 0.08, 0.15
I90 = [(-b / 2, 0), (b / 2, 0), (b / 2, ti), (bw / 2, ti + m), (bw / 2, h - ts - m), (b / 2, h - ts), (b / 2, h),
       (-b / 2, h), (-b / 2, h - ts), (-bw / 2, h - ts - m), (-bw / 2, ti + m), (-b / 2, ti)]
A1, y1, I1 = poli_props(I90)
W1_inf, W1_sup = I1 / y1, I1 / (h - y1)
# laje alveolar h20 de um lado só (apoio 10 cm na mesa); enchimento sobre os 30 cm restantes da mesa, altura 20; capa 5 cm
h_laje, apoio, h_capa = 0.20, 0.10, 0.05
L = 9.27                                             # vão entre apoios (VM-02: 9,53 − 2 × 0,13)
a_cont = L                                           # biapoiada: a = L (NBR 6118:2023 14.6.2.2)
bf = b + 0.10 * a_cont                               # largura colaborante da capa: mesa + 0,10a do lado da laje (só um lado)
fck1, fck2 = 50.0, 25.0                              # pré-moldado C50; capa/enchimento C25
Ec1 = 5600 * math.sqrt(fck1) * 1.2 ** 0 * 1.0        # Eci (NBR 6118:2023 8.2.8) — relação entre os dois é o que importa
Ec2 = 5600 * math.sqrt(fck2)
n = Ec2 / Ec1
ench = [(-b / 2 + apoio, h), (b / 2, h), (b / 2, h + h_laje), (-b / 2 + apoio, h + h_laje)]
capa = [(-b / 2, h + h_laje), (-b / 2 + bf, h + h_laje), (-b / 2 + bf, h + h_laje + h_capa), (-b / 2, h + h_laje + h_capa)]
Ae, ye, Ie = poli_props(ench)
Ac, yc_, Ic = poli_props(capa)
A_h = A1 + n * (Ae + Ac)
y_h = (A1 * y1 + n * (Ae * ye + Ac * yc_)) / A_h
I_h = I1 + A1 * (y1 - y_h) ** 2 + n * (Ie + Ae * (ye - y_h) ** 2 + Ic + Ac * (yc_ - y_h) ** 2)
h_tot = h + h_laje + h_capa
Wh_inf, Wh_sup_pre, Wh_topo = I_h / y_h, I_h / (h - y_h), I_h / (h_tot - y_h)

# ---------------------------------------------------------------- cargas (kN/m) — laje de um lado, tributária 5,0 m
trib = 10.05 / 2
pp_laje, capa_kNm2, rev, q = 2.80, 0.05 * 25, 1.0, 5.0
g1 = A1 * 25 + (pp_laje + capa_kNm2) * trib          # fase 1: viga + laje + capa fresca (seção pré-moldada)
g2 = rev * trib                                       # fase 2: revestimento (seção composta)
q2 = q * trib                                         # fase 2: sobrecarga
M1k = g1 * L ** 2 / 8
M2k = (g2 + q2) * L ** 2 / 8
V1d = 1.3 * g1 * L / 2
V2d = (1.3 * g2 + 1.4 * q2) * L / 2
Vd_total = V1d + V2d

# ---------------------------------------------------------------- protensão (9 cordoalhas Ø12,7, σpi 1400 MPa, perdas 20 % no infinito)
n_cord, Ap, sig_pi, perdas = 9, 98.7e-6, 1400.0, 0.20
P_inf = n_cord * Ap * sig_pi * 1e3 * (1 - perdas)    # kN
y_p = (7 * 0.060 + 2 * 0.110) / 9
e_p = y1 - y_p
# tensões no infinito (MPa): fase 1 na seção pré-moldada (M1 + 1,0 g2 quase-permanente?) — ELS-F com combinação frequente
psi1 = 0.6
M_els1 = M1k
M_els2 = (g2 + psi1 * q2) * L ** 2 / 8
sig_inf = (-P_inf / A1 + P_inf * e_p / W1_inf - M_els1 / W1_inf) / 1e3 - M_els2 / Wh_inf / 1e3      # fibra inferior (+ tração)
sig_sup_pre = (-P_inf / A1 - P_inf * e_p / W1_sup + M_els1 / W1_sup) / 1e3 + M_els2 / Wh_sup_pre / 1e3   # topo do pré-moldado
sig_topo_capa = n * (M_els2 / Wh_topo / 1e3)                                                            # topo da capa (C25)
fctm1 = 0.3 * fck1 ** (2 / 3); fctk_inf1 = 0.7 * fctm1
fctd2 = 0.7 * 0.3 * fck2 ** (2 / 3) / 1.4
fcd2 = fck2 / 1.4

# ---------------------------------------------------------------- interface (NBR 9062:2017 6.3.5) — cortante da fase 2 (após a solidarização)
b_int = b                                             # topo da mesa, 40 cm, superfície rugosa (rugosidade ≥ 5 mm, pente)
d_h = h_tot - 0.04                                    # altura útil da seção composta (tela/negativa a 4 cm do topo)
tau_sd = V2d / (b_int * d_h) / 1e3                    # MPa
tau_sd_tot = Vd_total / (b_int * d_h) / 1e3           # conservador: toda a cortante na interface
beta_s, beta_c = 0.9, 0.6                             # superfície rugosa — NBR 9062:2017 Tabela 2 (conferir na norma)
fyd = 500 / 1.15
tau_c = beta_c * fctd2
tau_max = 0.25 * fcd2
As_req_m2 = max(0.0, (tau_sd_tot - tau_c) / (beta_s * fyd)) * b_int            # m²/m
As_min_m2 = 0.001 * b_int                                                       # ρ ≥ 0,10 % da interface (adotado; NBR 6118 17.4.1.1.1 ρsw,min dá 4,2 cm²/m para C50)
rho_sw_min = 0.2 * fctm1 / 500                                                  # NBR 6118:2023 17.4.1.1.1 — Asw/(bw·s) ≥ 0,2 fctm/fywk
As_sw_min_m2 = rho_sw_min * b_int
As_adot_cm2m = 2 * math.pi * 0.8 ** 2 / 4 / 0.15                                 # N9 Ø8 c/15, 2 ramos (cm²/m)
As_req = max(As_req_m2, As_min_m2, As_sw_min_m2) * 1e4
tau_rd = beta_s * (As_adot_cm2m * 1e-4 / b_int) * fyd + tau_c

R = dict(
    secao_premoldada=dict(A_m2=round(A1, 4), yc_m=round(y1, 4), I_m4=round(I1, 6), W_inf_m3=round(W1_inf, 5), W_sup_m3=round(W1_sup, 5)),
    secao_composta=dict(bf_m=round(bf, 2), n=round(n, 3), A_hom_m2=round(A_h, 4), yc_m=round(y_h, 4), I_m4=round(I_h, 6),
                        ganho_inercia=round(I_h / I1, 2), W_inf_m3=round(Wh_inf, 5), h_total_m=h_tot),
    cargas=dict(L_m=L, g1_fase1_kNm=round(g1, 2), g2_fase2_kNm=round(g2, 2), q_fase2_kNm=round(q2, 2),
                M1k_kNm=round(M1k, 1), M2k_kNm=round(M2k, 1), V1d_kN=round(V1d, 1), V2d_kN=round(V2d, 1), Vd_total_kN=round(Vd_total, 1)),
    tensoes_infinito_MPa=dict(P_inf_kN=round(P_inf, 1), fibra_inf=round(sig_inf, 2), topo_premoldado=round(sig_sup_pre, 2), topo_capa=round(sig_topo_capa, 2),
                              fctk_inf_C50=round(fctk_inf1, 2), ok_ELS_F=sig_inf <= fctk_inf1, obs="fase 1 na seção pré-moldada, fase 2 na composta (combinação frequente, ψ1 0,6)"),
    interface=dict(norma="NBR 9062:2017 item 6.3.5", b_m=b_int, d_m=round(d_h, 3), tau_sd_fase2_MPa=round(tau_sd, 3), tau_sd_total_MPa=round(tau_sd_tot, 3),
                   beta_s=beta_s, beta_c=beta_c, fctd_capa_MPa=round(fctd2, 2), tau_c_MPa=round(tau_c, 3), tau_max_MPa=round(tau_max, 2),
                   As_req_cm2_m=round(As_req, 2), As_adotada_cm2_m=round(As_adot_cm2m, 2), tau_Rd_MPa=round(tau_rd, 3),
                   uso=round(tau_sd_tot / tau_rd, 3), ok=tau_sd_tot <= tau_rd and tau_sd_tot <= tau_max),
    armadura_2_estagio=dict(N9="estribo saliente Ø8 c/15, 2 ramos (U invertido saindo 20 cm do topo da viga, pernas de 60 cm na alma)",
                            N10="2 Ø10 longitudinais nos cantos do N9, dentro do enchimento (porta-estribos do 2º estágio)",
                            tela="Q138 na capa de 5 cm (toda a laje), traspasse 1 malha; passa por cima da viga",
                            negativa="Ø10 c/25 (uma por alvéolo) L = 150 cm: 75 cm dentro da chaveta/alvéolo grauteado e 75 cm na capa sobre a viga (ND-LET-LA01)",
                            enchimento="concreto C25 entre a ponta da laje e a borda da mesa (30 × 20 cm) + capa 5 cm, lançados junto; brita 1; adensar"),
    sequencia_obra=["montar as VM e as lajes alveolares (apoio 10 cm, faixa de neoprene)", "limpar e molhar o topo da viga (superfície rugosa de fábrica, pente 5 mm)",
                    "conferir os N9 salientes e amarrar os N10 e as negativas Ø10 nos alvéolos", "grautear as chavetas, estender a tela Q138",
                    "concretar enchimento + capa C25 de uma vez; curar 7 dias; não carregar antes de fck ≥ 20 MPa"],
)
(AQ / "segundo_estagio.json").write_text(json.dumps(R, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(R, indent=1, ensure_ascii=False))
