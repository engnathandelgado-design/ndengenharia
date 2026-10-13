"""Letsara — estudo da placa de fechamento protendida com 10 cm (125 × 10), comparada com a atual (125 × 15).
Cordoalhas alinhadas nas 2 faces (mesmas posições da PP00: 15,6 / 46,9 / 78,1 / 109,4 cm), cobrimento 2,0 cm (Nathan, 13/10/2026).
Mesmo esquema da calc_placas.py: placa horizontal entre pilares, isostática para vento fora do plano, cordoalhas
pré-tracionadas simétricas (metade em cada face, vento nos 2 sentidos). Gera placa_h10.json.
Normas: NBR 6118:2023 (13.4 protensão limitada p/ pré-tração em CAA II; 17.3 ELS; 17.2 ELU), NBR 9062:2017
(transitórias, coef. dinâmico 1,3), NBR 6123:2023 (vento). kN, m; MPa nas tensões; compressão negativa.
"""
import json, math
from pathlib import Path
AQ = Path(__file__).parent

b, L, L_vao = 1.25, 10.165, 10.075
fck, fckj = 40.0, 25.0
fptk, fpyk, Ep = 1900.0, 1710.0, 195000.0
CORD = {"9,5": 55.5e-6, "12,7": 98.7e-6}
SIG_PI = 1400.0                            # MPa na pista (≤ 0,77 fptk = 1463; 0,85 fpyk = 1453)
PERDA_IMED, PERDA_TOT = 0.07, 0.20         # estimativas (encurtamento, retração, fluência, relaxação)
q0 = 0.874                                 # kN/m² (V0 45 m/s, S2 cat. III cl. C, S3 0,95 — rodada 2)
ZONAS = {"borda (Cpe -1,4 + Cpi 0,2)": 1.6, "corrente (Cpe +0,7 + Cpi -0,3)": 1.0}
fctm = 0.3 * fck ** (2 / 3); fctk_inf = 0.7 * fctm
fct_f = 1.5 * fctk_inf                     # NBR 6118:2023 17.3.1 — seção retangular α = 1,5 (conferir)
fctk_j = 0.7 * 0.3 * fckj ** (2 / 3)
Ec = 0.85 * 5600 * math.sqrt(fck)

def placa(h, diam, n_face, cob=0.020, zona=1.6):
    A = b * h; W = b * h ** 2 / 6; I = b * h ** 3 / 12; pp = 25 * A
    Ap1 = CORD[diam]; phi = float(diam.replace(",", ".")) / 1000
    dc = cob + phi / 2                                   # eixo da cordoalha à face
    n = 2 * n_face
    Fmac = SIG_PI * Ap1 * 1e3
    P0 = n * Fmac * (1 - PERDA_IMED); Pinf = n * Fmac * (1 - PERDA_TOT)
    s_p0, s_pinf = -P0 / A / 1e3, -Pinf / A / 1e3       # protensão centrada (simétrica)
    wk = q0 * zona * b; Mk = wk * L_vao ** 2 / 8; Md = 1.4 * Mk
    s_v = Mk / W / 1e3
    # ELU: face tracionada com n_face cordoalhas a d; as da face comprimida desprezadas (a favor)
    # tensão na cordoalha: pré-alongamento + ε da flexão; simplificação fpd (escoamento) — conferir εp ≥ εpyd
    fpd = fpyk / 1.15; fcd = fck / 1.4
    d = h - dc
    x = n_face * Ap1 * fpd / (0.85 * fcd * 0.8 * b)
    MRd = n_face * Ap1 * fpd * 1e3 * (d - 0.4 * x)
    # NBR 6118 17.3.5.2.1: armadura mínima de flexão — MRd ≥ 1,2·Mcr (Mcr com fctk,sup e protensão)
    fctk_sup = 1.3 * fctm
    Mcr = (fctk_sup + abs(s_pinf)) * W * 1e3
    flecha = 5 * wk * L_vao ** 4 / (384 * Ec * 1e3 * I) * 1000
    # transitórias (fckj): estocagem deitada em 2 calços a 0,207L, desforma deitada 4 pontos (dinâmico 1,3 × sucção 1,2)
    M_est = 0.0214 * pp * L ** 2; M_desf = 0.0054 * pp * 1.3 * 1.2 * L ** 2
    M_ic = 0.0214 * pp * 1.3 * L ** 2; W_pl = h * b ** 2 / 6
    t = dict(estocagem=s_p0 + M_est / W / 1e3, desforma=s_p0 + M_desf / W / 1e3, icamento_em_pe=s_p0 + M_ic / W_pl / 1e3)
    comp_lib = s_p0 - max(M_est, M_desf) / W / 1e3
    return dict(h_cm=h * 100, cordoalhas=f"{n} Ø{diam} ({n_face} por face)", eixo_a_face_mm=round(dc * 1000, 1),
                Ap_mm2=round(n * Ap1 * 1e6), F_macaco_kN=round(Fmac, 1), P0_kN=round(P0), Pinf_kN=round(Pinf),
                sig_cp_inf=round(s_pinf, 2), sig_cp_0=round(s_p0, 2),
                peso_t=round(pp * L / 9.81, 2), vol_m3=round(A * L, 3),
                Mk=round(Mk, 2), Md=round(Md, 2), MRd=round(MRd, 2), uso_ELU=round(Md / MRd, 2),
                Mcr=round(Mcr, 2), MRd_1_2Mcr=round(MRd / (1.2 * Mcr), 2),
                sig_vento=round(s_v, 2), ELS_F=round(s_pinf + 0.3 * s_v, 2), fct_f=round(fct_f, 2),
                rara=round(s_pinf + s_v, 2), flecha_mm=round(flecha, 1), flecha_lim_L250=round(L_vao * 1000 / 250, 1),
                transit={k: round(v, 2) for k, v in t.items()}, lim_tracao_j=round(fctk_j / 1.5 * 1.5, 2),
                compressao_liberacao=round(comp_lib, 2), lim_comp_lib=round(-0.7 * fckj, 1),
                ok=dict(ELU=Md <= MRd, ELS_F=s_pinf + 0.3 * s_v <= fct_f, rara_sem_fissura=s_pinf + s_v <= fct_f,
                        flecha=flecha <= L_vao * 1000 / 250, transit=all(v <= fctk_j for v in t.values()),
                        comp_lib=comp_lib >= -0.7 * fckj))

R = {"atual_h15_8x9,5_borda": placa(0.15, "9,5", 4, cob=0.035)}
for z, c in ZONAS.items():
    for diam in ("9,5", "12,7"):
        for nf in range(2, 8):
            r = placa(0.10, diam, nf, zona=c)
            R[f"h10_{nf * 2}x{diam}_{z.split()[0]}"] = r
(AQ / "placa_h10.json").write_text(json.dumps(R, indent=1, ensure_ascii=False), encoding="utf-8")
hdr = f"{'caso':30s} {'ELU':>5s} {'1,2Mcr':>6s} {'ELS-F':>6s} {'rara':>6s} {'flecha':>7s} {'estoc':>6s} {'desf':>6s} {'σ0':>6s} ok"
print(hdr)
for k, r in R.items():
    print(f"{k:30s} {r['uso_ELU']:5.2f} {r['MRd_1_2Mcr']:6.2f} {r['ELS_F']:6.2f} {r['rara']:6.2f} {r['flecha_mm']:5.1f}/{r['flecha_lim_L250']:.0f} "
          f"{r['transit']['estocagem']:6.2f} {r['transit']['desforma']:6.2f} {r['compressao_liberacao']:6.2f} {all(v for kk,v in r['ok'].items() if kk!='rara_sem_fissura')}")
print("fct_f", round(fct_f, 2), "fctk_j", round(fctk_j, 2), "Ec", round(Ec))
