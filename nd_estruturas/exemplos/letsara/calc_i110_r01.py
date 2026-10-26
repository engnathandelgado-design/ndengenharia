"""Letsara — vigas centrais I120 (V407, V406, V405, V404 — DEC-058), verificação completa da peça protendida (DEC-032). Gera i110_r01.json,
que é a ÚNICA fonte do arranjo de cordoalhas, σpi, fckj, isolamentos, lbpt e reações para as pranchas (viga_i.py,
armaduras_vigas.py), o dente (calc_dentes.py) e a memória MC05 (calc_nbr9062.py / memoria_nbr9062.py).

Vãos (eixo a eixo, DEC-058): V407 L2→L4 20,15 m; V406 L4→P13, V405 P13→P13B e V404 P13B→L9, 16,517 m cada. Cargas: peso próprio e as TS-01
apoiadas no topo (2 por linha) como cargas concentradas nas posições reais (reações e momentos sem supor simetria).

Verificações (NBR 6118:2023 / NBR 9062:2017):
  perdas imediatas e progressivas 9.6.3 (prefabricados.perdas_pretracao; U 70 %, t0 fictícia 5 dias, cobertura aos 60 dias);
  lbpt 9.4.5 (liberação gradual); ato da protensão ao longo da peça 17.2.4.3.2 (γp 1,1; meio, fim de cada isolamento e
  ponta; armadura de tração no topo 17.2.4.3.2 c); ELS-F e ELS-D ao longo da peça (protensão limitada, CAA II, ψ1 0,6 e
  ψ2 0,4 — escritório/academia, aplicados também à sobrecarga da cobertura a favor da segurança); ELU flexão por
  compatibilidade (17.2.2, x/d ≤ 0,45) com N3; cortante ao longo da peça (17.4.2.2, modelo I, Vc do elemento protendido);
  flechas (NBR 9062:2017 Tab. 9: L/350); içamento pelas alças (NBR 9062:2017 5.3.2, βa 1,3 nas tensões e 3,0 na alça);
  reação do dente (Vd real, γn de 7.3.1.1 e Hd = 0,16·Fd). Unidades kN, m; MPa nas tensões; compressão negativa.
"""
import json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from nd_estruturas.prefabricados import (Concreto, secao_I, secao_retangular, CORD, EP, FYD_CA50, perdas_pretracao,
                                         lbpt_cordoalha, ato_pretracao, tensoes_secao, resultante_tracao, mrd_camadas,
                                         vc_protendido, gama_n_consolo, GAMA_P_ATO, SIG_ACO_ATO)
from geometria import Y_LIN, Y_PC_C

AQ = Path(__file__).parent
H_I = 1.20                                              # DEC-054 (24/10/2026): h 120 com dente 78 × 35 (antes 1,30)
DIAM = 12.7                                             # DEC-058 (24/10, Nathan): cordoalha Ø12,7 CP-190 RB (DEC-054 era Ø15,2)
A_C = CORD["12.7"]                                      # área de uma cordoalha (m²)
sec = secao_I(H_I, bs=0.40, ts=0.22, ms=0.08, bw=0.15, bi=0.40, ti=0.25, mi=0.08)
SECP = secao_retangular(0.40, H_I)                      # maciço das pontas (1,40 m)
U_AR = sum(math.dist(a, b) for a, b in zip(sec.pts, sec.pts[1:] + sec.pts[:1]))
C = Concreto(50)
FCKJ = 50.0                                             # DEC-054: liberação da protensão só com fckj 50 MPa (antes 45, DEC-032)
SIG_PI = 1453.0                                         # MPa = 0,85 fpyk (9.6.1.2.1): 143,4 kN por cordoalha no macaco
U, T0, T_G2 = 70.0, 5.0, 60.0                           # umidade (Ijuí/RS, a favor), idade fictícia na liberação, montagem das TS-01
PSI1, PSI2 = 0.6, 0.4
NIVEL = "limitada"                                      # DEC-054: protensão LIMITADA (CAA II, pré-tração: NBR 6118:2023 Tab. 13.4 nível 2); antes completa (DEC-043)
PSI_D, PSI_F = (PSI1, 1.0) if NIVEL == "completa" else (PSI2, PSI1)   # ELS-D na frequente (ψ1) e ELS-F na rara (ψ = 1)
X_MAC, LN, HD = 1.40, 0.35, 0.78                        # maciço das pontas, dente 78 × 35
N3 = (10, 20.0)                                         # rev12: 10 Ø20 em 2 camadas de 5 (regra: barras ≤ Ø20; antes 6 Ø25, DEC-054)
Y_N3 = H_I - 0.030 - 0.0063 - 0.010 - 0.0225           # centroide das 2 camadas (cobrimento 3,0 + N13 Ø6,3 + Ø/2; camadas a Ø + 25 mm)
VD_DENTE_MIN = 0.0                                      # ajustado por viga abaixo (V405/V406: 555 kN, decisão do engenheiro)
ALCA_A = 2.50                                           # alças AL-3 a 2,50 m das pontas
LACO_CAP = 2 * 98.7 * 1900 / 1000 / 4 * 0.7             # 1 laço (2 pernas) Ø12,7: 2 × Fptk/4 × 0,7 (critério ND, ts01_dados)
TRIB = 10.075
LG = json.loads((AQ / "ligacoes.json").read_text(encoding="utf-8"))
L_TS = LG["L_TS"]
G_COB = LG["cargas_cob"]["g_total_sem_terca"] + 0.123 / LG["passo_tercas"]
g_ts = (0.2225 * 25 + G_COB * TRIB) * L_TS / 2          # reação de 1 TS-01 no topo da I120
q_ts = LG["cargas_cob"]["sobrecarga"] * TRIB * L_TS / 2
P_g, P_q = 2 * g_ts, 2 * q_ts                           # duas TS por linha
VIGAS = {"V407": (Y_LIN[1], Y_LIN[3], [Y_LIN[2]]), "V406": (Y_LIN[3], Y_PC_C[0], [Y_LIN[4]]),           # DEC-058: 3 vãos de 16,517 m
         "V405": (Y_PC_C[0], Y_PC_C[1], [Y_LIN[5], Y_LIN[6]]), "V404": (Y_PC_C[1], Y_LIN[8], [Y_LIN[7]])}
FACES = {"V407": (0.30, 0.20), "V406": (0.20, 0.20), "V405": (0.20, 0.20), "V404": (0.20, 0.30)}   # PC-03 40×40
X7 = [-150, -100, -50, 0, 50, 100, 150]
X5, X4 = [-100, -50, 0, 50, 100], [-100, -50, 50, 100]
Y_LIN_C = (60, 100, 140, 180)                           # Ø12,7: espaçamento vertical livre ≥ 2φ / 20 mm (NBR 6118:2023 18.6.2.3)
ISOL = (0, 0, 2000, 4000)                               # isolamento escalonado (mm) por linha; por viga em ISOL_V
ISOL_V = {}                                             # (padrão de isolamento escolhido na busca, ver ISOLS)
TOPO = dict(y=round(H_I * 1000) - 100, xs=[-100, 100])                     # 2 cordoalhas na mesa superior, aderentes (controle do ato nas pontas)


LINHA5 = dict(y=220, xs=[-50, 50], isol=4000)          # DEC-043: 5ª linha (2 cordoalhas a 22 cm, x ±5, isoladas 4,0 m) — V405/V406


def arranjo(por_linha, topo=True, linha5=False, isol=ISOL):
    lin = [dict(y=y, xs=(X7 if n == 7 else X5 if n == 5 else X4), isol=i) for y, n, i in zip(Y_LIN_C, por_linha, isol) if n]
    if linha5:
        lin.append(dict(LINHA5))
    if topo:
        lin.append(dict(y=TOPO["y"], xs=TOPO["xs"], isol=0))
    return lin


# DEC-043 (protensão completa): menor arranjo da família que passa (ELS-D na frequente, ELS-F na rara, ato, ELU, içamento)
# com folga de MARGEM_D no ELS-D (histórico: DEC-043/054, Ø15,2, vãos de 24,775 m).
# DEC-058 (Ø12,7, arranjo C): menor arranjo que passa com folga de MARGEM_D no ELS-D (estudo_i130_pilar_extra: V407 18 =
# 7+5+4 + 2 (y 22); V406/V405/V404 13 = 5+4+4, marca única de seção e cordoalha). Tenta antes os arranjos menores.
_PEQ = [((4, 4, 4), False, False), ((5, 4, 4), False, False), ((5, 5, 4), False, False)]
CANDIDATOS = {"V407": [((7, 4, 4), False, True), ((7, 5, 4), False, True), ((7, 5, 4, 4), False, False), ((7, 5, 4), True, True)],
              "V406": _PEQ, "V405": _PEQ, "V404": _PEQ}
MARGEM_D = 0.25                                         # MPa (critério de escolha do arranjo, não da norma)


VD_MIN = {"V404": 0.0, "V405": 0.0, "V406": 0.0, "V407": 0.0}   # DEC-058: reação real (antes 555 kN fixo nas de 24,775 m)


def verificar(nome, ya, yb, cargas, lin):
    global VD_DENTE_MIN
    VD_DENTE_MIN = VD_MIN[nome]
    fa, fb = FACES[nome]
    x0 = ya + fa + 0.075 + 0.175                        # pino a 175 da ponta; ponta a 75 da face
    x1 = yb - fb - 0.075 - 0.175
    L = x1 - x0
    Lp = (yb - fb - 0.075) - (ya + fa + 0.075)
    a_ap = 0.175                                        # apoio a 175 da ponta da peça
    xs = [y - x0 for y in cargas]
    g1 = sec.A * 25
    g_mac = (SECP.A - sec.A) * 25                       # acréscimo do maciço (kN/m) nos 1,40 m
    # ---- esforços ao longo do vão (x da ponta da peça; apoio em a_ap) — sem supor simetria
    def RA(P):
        return sum(P * (L - a) / L for a in xs)
    def M_pont(P, xx):                                  # x a partir do apoio A
        return RA(P) * xx - sum(P * (xx - a) for a in xs if a < xx)
    def V_pont(P, xx):
        return RA(P) - sum(P for a in xs if a < xx)
    def M_g1(xx):
        return g1 * xx * (L - xx) / 2
    xs_scan = [L * k / 400 for k in range(401)]
    Mg2_max = max(M_pont(P_g, x) for x in xs_scan)
    Mq_max = max(M_pont(P_q, x) for x in xs_scan)
    x_Mmax = max(xs_scan, key=lambda x: M_g1(x) + M_pont(P_g, x) + M_pont(P_q, x))
    Mg1_m = M_g1(x_Mmax)
    # ---- arranjo e perdas (seção de momento máximo)
    n_inf = sum(len(l["xs"]) for l in lin if l["y"] < 600)
    n = sum(len(l["xs"]) for l in lin)
    Ap = n * A_C
    yp = sum(len(l["xs"]) * l["y"] for l in lin) / n / 1000
    pp = perdas_pretracao(SIG_PI, Ap, sec.A, sec.I, sec.yc, yp, Mg1_m, C, FCKJ, U_AR, U=U, t0_dias=T0,
                          fases=[(M_pont(P_g, x_Mmax), T_G2)])
    lt, lbp, fbpd = lbpt_cordoalha(FCKJ, pp["sig_p0"], diam_mm=DIAM, gradual=True)
    lt_b = lbpt_cordoalha(FCKJ, pp["sig_p0"], diam_mm=DIAM, gradual=False)[0]
    grupos = [dict(n=len(l["xs"]), y=l["y"] / 1000, x0=(LN if l["y"] / 1000 < H_I - HD else 0.0) + l["isol"] / 1000) for l in lin]
    ato = ato_pretracao(sec, SECP, X_MAC, Lp, grupos, pp["sig_p0"], g1, FCKJ, lt, area=A_C)
    As_N3 = N3[0] * math.pi * (N3[1] / 1000) ** 2 / 4 * 1e4
    # pontos de controle do ato: ponta (fim do lbpt das aderentes), fim de cada isolamento + lbpt, meio
    ctrl = {"ponta (fim do lbpt)": LN + lt}
    for l in lin:
        if l["isol"]:
            ctrl[f"fim do isolamento de {l['isol']/1000:g} m (linha {l['y']/10:g})"] = LN + l["isol"] / 1000 + lt
    ctrl["meio do vão"] = Lp / 2
    pts = ato["pontos"]
    ato_ctrl = {}
    for k, xc in ctrl.items():
        p = min(pts, key=lambda q: abs(q["x"] - xc))
        ato_ctrl[k] = dict(x=p["x"], topo=round(p["topo"], 2), base=round(p["base"], 2), As_cm2=round(p["R_tracao"] / (SIG_ACO_ATO * 1000) * 1e4, 2))

    def P_x(xp, sig):                                   # força e cota da resultante na seção xp (da ponta da peça)
        F = My = 0.0
        for gr in grupos:
            f = min(1.0, max(0.0, (xp - gr["x0"]) / lt)) * gr["n"] * A_C * sig * 1000
            F += f
            My += f * gr["y"]
        return F, (My / F if F else yp)
    # ---- ELS ao longo da peça (NIVEL: "completa" = ELS-D frequente + ELS-F rara; "limitada" = ELS-D q.perm. + ELS-F freq.; NBR 6118 Tab. 13.4)
    fctk = C.fctk_inf
    lim_F = 1.3 * fctk                                  # 17.3.4: α = 1,3 seção I
    # ELS-D (descompressão) onde as cordoalhas inferiores já estão com a força toda (x ≥ face do dente + lbpt): é a
    # proteção da armadura ativa. No trecho de transferência (dente e maciço) vale o ELS-F (sem fissura) — o maior valor
    # da base nesse trecho fica registrado (D_base_transferencia) para conferência.
    x_plena = LN + lt
    els = dict(D_base=-99.0, F_base=-99.0, F_topo=-99.0, D_base_transferencia=-99.0)
    for k in range(1, 200):
        xx = L * k / 200
        xp = xx + a_ap
        s = SECP if xp < X_MAC or xp > Lp - X_MAC else sec
        F, yq = P_x(min(xp, Lp - xp), pp["sig_pinf"])
        Mg = M_g1(xx) + M_pont(P_g, xx)
        Mq = M_pont(P_q, xx)
        sbD, _ = tensoes_secao(s.A, s.I, s.yc, s.h, F, yq, Mg + PSI_D * Mq)
        sbF, stF = tensoes_secao(s.A, s.I, s.yc, s.h, F, yq, Mg + PSI_F * Mq)
        _, stG = tensoes_secao(s.A, s.I, s.yc, s.h, F, yq, Mg)
        if min(xp, Lp - xp) < x_plena:
            if sbD > els["D_base_transferencia"]:
                els.update(D_base_transferencia=sbD, x_Dt=xp)
        elif sbD > els["D_base"]:
            els.update(D_base=sbD, x_D=xp)
        if sbF > els["F_base"]:
            els.update(F_base=sbF, x_F=xp)
        if stG > els["F_topo"]:
            els.update(F_topo=stG, x_Ft=xp)
    els = {k: round(v, 3) for k, v in els.items()}
    els.update(lim_F=round(lim_F, 2), lim_D=0.0, psi1=PSI1, psi2=PSI2, nivel=NIVEL, psi_D=PSI_D, psi_F=PSI_F, x_cordoalhas_plenas=round(x_plena, 3),
               ok=els["D_base"] <= 0 and els["F_base"] <= lim_F and els["F_topo"] <= lim_F and els["D_base_transferencia"] <= lim_F)
    # ---- ELU flexão (seção de momento máximo, cordoalhas plenas)
    Md = 1.3 * (Mg1_m + M_pont(P_g, x_Mmax)) + 1.4 * M_pont(P_q, x_Mmax)
    e_pre = pp["sig_pinf"] / (EP / 1000)
    cords = [(len(l["xs"]) * A_C, l["y"] / 1000, e_pre) for l in lin]
    MRd, x_ln, xd = mrd_camadas(sec, C.fcd, cords, [(As_N3 * 1e-4, Y_N3)])
    MRd0, _, xd0 = mrd_camadas(sec, C.fcd, cords, [])
    elu = dict(Md=round(Md, 1), MRd=round(MRd, 1), x_d=round(xd, 3), MRd_sem_N3=round(MRd0, 1), x_d_sem_N3=round(xd0, 3),
               x_Mmax=round(x_Mmax + a_ap, 2), ok=MRd >= Md and xd <= 0.45)
    # ---- cortante ao longo da peça (17.4.2.2, modelo I, θ 45°)
    bw = 0.15
    d = H_I - sum(len(l["xs"]) * l["y"] for l in lin if l["y"] < 600) / n_inf / 1000
    fywd = min(FYD_CA50, 435e3)
    VRd2 = 0.27 * (1 - C.fck / 250) * C.fcd * bw * 0.9 * d
    Asw_min = 0.2 * C.fctm / 500 * bw * 1e4
    est = (8.0, 0.10, 0.15, 2.0)                        # N2 Ø8 (2 ramos) c/10 nos 2,0 m das pontas, c/15 corrente (prancha)
    A2 = 2 * math.pi * 0.008 ** 2 / 4 * 1e4
    Md_meio = [1.3 * (M_g1(x) + M_pont(P_g, x)) + 1.4 * M_pont(P_q, x) for x in xs_scan]
    corte = []
    for k in range(0, 201):
        xx = L * k / 200
        xp = xx + a_ap
        if xp < LN + 0.5 * d or xp > Lp - LN - 0.5 * d:
            continue                                     # trecho do dente: armadura N6/N8 (calc_dentes)
        Vd = abs(1.3 * (g1 * (L / 2 - xx) + V_pont(P_g, xx)) + 1.4 * V_pont(P_q, xx))
        F, yq = P_x(min(xp, Lp - xp), pp["sig_pinf"])
        e = sec.yc - yq
        M0 = 0.9 * F * (sec.Wi / sec.A + e)
        meia = [m for x, m in zip(xs_scan, Md_meio) if (x <= L / 2) == (xx <= L / 2)]
        Vc, Vc0 = vc_protendido(C, bw, d, M0, max(meia))
        req = max(Asw_min, max(0.0, Vd - Vc) / (0.9 * d * fywd) * 1e4)
        s_ = est[1] if (xp <= est[3] or xp >= Lp - est[3]) else est[2]
        corte.append(dict(x=round(xp, 2), Vd=round(Vd, 1), Vc=round(Vc, 1), Asw_req=round(req, 2), Asw_ef=round(A2 / s_, 2)))
    pior = max(corte, key=lambda c: c["Asw_req"] / c["Asw_ef"])
    Vd_max = max(c["Vd"] for c in corte)
    cortante = dict(VRd2=round(VRd2, 1), Vd_max=Vd_max, Asw_min=round(Asw_min, 2), d=round(d, 3), pior=pior,
                    estribos="N2 Ø8 c/10 nos 2,0 m das pontas, c/15 corrente (2 ramos)", ok=Vd_max <= VRd2 and pior["Asw_req"] <= pior["Asw_ef"],
                    Vc0=round(0.6 * C.fctk_inf / 1.4 * 1000 * bw * d, 1))
    # ---- flechas (Ecs, estádio I; φ da Tab. 8.2 — mesmos de 9.6.3.4) — NBR 9062:2017 5.4.3.4 Tab. 9: L/350 (L > 20 m)
    EI = C.Ecs * sec.I
    def f_pont(P, a):                                   # flecha no meio do vão por carga concentrada em a
        b = min(a, L - a)
        return P * b * (3 * L ** 2 - 4 * b ** 2) / (48 * EI)
    from nd_estruturas.prefabricados import fluencia_retracao
    phi1, _ = fluencia_retracao(U, pp["h_fic_cm"], T_G2)
    fg1 = 5 * g1 * L ** 4 / (384 * EI)
    fg2 = sum(f_pont(P_g, a) for a in xs)
    fq = sum(f_pont(P_q, a) for a in xs)
    fp = -pp["Pinf"] * (sec.yc - yp) * L ** 2 / (8 * EI)
    fp0 = -pp["P0"] * (sec.yc - yp) * L ** 2 / (8 * EI)
    f_final = (fg1 + fp) * (1 + pp["phi"]) + fg2 * (1 + phi1) + PSI2 * fq
    flecha = dict(contraflecha_ato_mm=round((fg1 + fp0) * 1000, 1), final_mm=round(f_final * 1000, 1), lim_mm=round(L / 350 * 1000, 1),
                  phi_t0=round(pp["phi"], 2), phi_montagem=round(phi1, 2), ok=abs(f_final) <= L / 350)
    # ---- içamento e estoque pelas alças AL-3 (NBR 9062:2017 5.3.2: βa 1,3 nas tensões; alça: βa 3,0 na ruptura)
    peso = g1 * Lp + g_mac * X_MAC * 2 - 2 * 0.40 * (H_I - HD) * LN * 25
    F_alca = 1.3 * peso / 2
    n_lacos = max(2, math.ceil(F_alca / LACO_CAP - 1e-9))
    rup = n_lacos * 2 * 98.7 * 1900 / 1000 * 0.7
    F_i, y_i = P_x(ALCA_A, pp["sig_p0"])
    M_bal = -1.3 * (g1 * ALCA_A ** 2 / 2 + g_mac * X_MAC * (ALCA_A - X_MAC / 2))
    sb_i, st_i = tensoes_secao(sec.A, sec.I, sec.yc, sec.h, GAMA_P_ATO * F_i, y_i, M_bal)
    Lv = Lp - 2 * ALCA_A
    M_vao = 1.3 * g1 * Lv ** 2 / 8 + M_bal
    F_m, y_m = P_x(Lp / 2, pp["sig_p0"])
    sb_m, st_m = tensoes_secao(sec.A, sec.I, sec.yc, sec.h, F_m, y_m, M_vao)
    R_i = resultante_tracao(sec, sb_i, st_i) if st_i > 0 else 0.0
    icamento = dict(a_alca_m=ALCA_A, peso_kN=round(peso, 1), F_alca_d_kN=round(F_alca, 1), cap_laco_kN=round(LACO_CAP, 1), n_lacos=n_lacos,
                    ruptura_lacos_kN=round(rup, 1), F_alca_beta3_kN=round(3.0 * peso / 2, 1), topo_alca=round(st_i, 2), base_alca=round(sb_i, 2),
                    base_vao=round(sb_m, 2), topo_vao=round(st_m, 2), lim_t=round(ato["lim_t"], 2), lim_c=round(ato["lim_c"], 1),
                    As_topo_cm2=round(R_i / (SIG_ACO_ATO * 1000) * 1e4, 2),
                    ok=st_i <= ato["lim_t"] and sb_m >= ato["lim_c"] and 3.0 * peso / 2 <= rup)
    # ---- reação no dente (Vd real com as TS-01 fora do centro) e γn (NBR 9062:2017 7.3.1.1)
    RgA, RgB = RA(P_g) + g1 * L / 2 + g_mac * X_MAC, len(xs) * P_g - RA(P_g) + g1 * L / 2 + g_mac * X_MAC
    RqA, RqB = RA(P_q), len(xs) * P_q - RA(P_q)
    lado = "B" if 1.3 * RgB + 1.4 * RqB >= 1.3 * RgA + 1.4 * RqA else "A"
    Fg_d, Fq_d = (1.3 * RgB, 1.4 * RqB) if lado == "B" else (1.3 * RgA, 1.4 * RqA)
    Vd_calc = Fg_d + Fq_d
    # DEC-032: o engenheiro fixou Vd = 555 kN (auditoria, cargas da rev06b); com as cargas atuais (cobertura Kingspan) a reação
    # dá um pouco menos — fica o maior valor
    Vd_dente = max(Vd_calc, VD_DENTE_MIN)
    Fg_d, Fq_d = Fg_d * Vd_dente / Vd_calc, Fq_d * Vd_dente / Vd_calc
    gn = gama_n_consolo(Fg_d, Fq_d)
    dente = dict(lado=lado, Vd=round(Vd_dente, 1), Vd_cargas_atuais=round(Vd_calc, 1), Fg_d=round(Fg_d, 1), Fq_d=round(Fq_d, 1), parcela_variavel=round(Fq_d / Vd_dente, 3),
                 gama_n=gn, Fd=round(gn * Vd_dente, 1), Hd=round(0.16 * gn * Vd_dente, 1),
                 reacao_k=dict(A=dict(g=round(RgA, 1), q=round(RqA, 1)), B=dict(g=round(RgB, 1), q=round(RqB, 1))),
                 norma="NBR 9062:2017 7.3.1.1 (γn), 7.3.1.2 (Hd = 0,16 Fd, elastômero) e 7.4")
    ok = dict(ato=ato["ok"] and ato["As_topo_cm2"] <= As_N3, ELS=els["ok"], ELU=elu["ok"], cortante=cortante["ok"], flecha=flecha["ok"], icamento=icamento["ok"])
    ato_out = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in ato.items() if k != "pontos"}
    ato_out.update(controle=ato_ctrl, As_N3_cm2=round(As_N3, 2), fckj=FCKJ, lbpt_m=round(lt, 3), lbpt_brusca_m=round(lt_b, 3), lbp_m=round(lbp, 3))
    return dict(L_eixos=round(yb - ya, 3), L_peca=round(Lp, 3), L_calc=round(L, 3), cargas_concentradas_kN=dict(g=round(P_g, 1), q=round(P_q, 1)),
                x_cargas_m=[round(a, 3) for a in xs], g2_equiv=round(8 * Mg2_max / L ** 2, 2), q_equiv=round(8 * Mq_max / L ** 2, 2),
                arranjo=dict(linhas=lin, n_cord=n, n_inf=n_inf, y_cg_mm=round(yp * 1000, 1), sig_pi=SIG_PI, F_macaco_kN=round(SIG_PI * A_C * 1000, 1), cordoalha=f"Ø{DIAM:g}",
                             fckj=FCKJ, fck=C.fck, liberacao="gradual (macaco), simétrica, só com fckj atingido", lbpt_m=round(lt, 3), lbpt_brusca_m=round(lt_b, 3)),
                perdas={k: (round(v, 7) if isinstance(v, float) else v) for k, v in pp.items()},
                ato=ato_out, ELS=els, ELU=elu, cortante=cortante, flecha=flecha, icamento=icamento, dente=dente, ok=ok, ok_geral=all(ok.values()),
                linhas=dict(Vd_kN=round(Vd_dente, 1), peso_kN_m=round(g1, 2), P0_kN=round(pp["P0"], 1), Pinf_kN=round(pp["Pinf"], 1),
                            flecha_final_mm=flecha["final_mm"], Md_kNm=elu["Md"], MRd_kNm=elu["MRd"], x_d=elu["x_d"],
                            elsd_inf_MPa=els["D_base"], elsf_inf_MPa=els["F_base"], elsf_lim_MPa=els["lim_F"],
                            perda_imediata_pct=round(pp["perda_imediata_pct"], 1), perda_total_pct=round(pp["perda_total_pct"], 1)))


MARCA_UNICA = ("V406", "V405", "V404")                 # DEC-058: mesma pista, mesma seção e mesma cordoalha


# Pedido do Nathan (24/10): busca entre os 4 padrões de isolamento escalonado (linha de baixo sempre aderente), com o
# comprimento isolado medido da face do dente (início do fundo da viga) em cada ponta. Escolhe o arranjo com menos cordoalhas;
# no empate, o primeiro padrão da lista (menos isolamento).
ISOLS = [(0, 0, 2000, 4000), (0, 2000, 2000, 4000), (0, 2000, 4000, 6000), (0, 3000, 3000, 6000)]


def escolher(nome, ya, yb, cargas, cands, isols=ISOLS):
    tent = []
    for k, (por_linha, topo, l5) in enumerate(cands):
        for ji, iso in enumerate(isols):
            r = verificar(nome, ya, yb, cargas, arranjo(por_linha, topo, l5, iso))
            tent.append(dict(arranjo=f"{'+'.join(map(str, por_linha))}" + (" + 2 (y 22)" if l5 else "") + (" + 2 topo" if topo else ""), isol=list(iso),
                             n=r["arranjo"]["n_cord"], ok=r["ok"], ELS_D=r["ELS"]["D_base"]))
            if r["ok_geral"] and r["ELS"]["D_base"] <= -MARGEM_D:
                r["tentativas"] = tent
                r["isolamento_padrao"] = list(iso)
                return (k, ji), r
    r["tentativas"] = tent
    return (len(cands) - 1, len(isols) - 1), r


res = {}
kmax = max(escolher(n, *VIGAS[n], CANDIDATOS[n])[0] for n in MARCA_UNICA)          # (arranjo, padrão de isolamento) comum às três
for nome, (ya, yb, cargas) in VIGAS.items():
    if nome in MARCA_UNICA:
        _, r = escolher(nome, ya, yb, cargas, CANDIDATOS[nome][kmax[0]:kmax[0] + 1], ISOLS[kmax[1]:kmax[1] + 1])
    else:
        _, r = escolher(nome, ya, yb, cargas, CANDIDATOS[nome])
    res[nome] = r
    print(nome, "L", r["L_peca"], "n", r["arranjo"]["n_cord"], "ok", r["ok_geral"], {k: v for k, v in r["ok"].items() if not v})
    print("   perdas imed %.1f %% total %.1f %% (φ %.2f, εcs %.2e)" % (r["perdas"]["perda_imediata_pct"], r["perdas"]["perda_total_pct"], r["perdas"]["phi"], r["perdas"]["eps_cs"]),
          "lbpt", r["ato"]["lbpt_m"], "| ato topo %.2f@%.2f base %.2f@%.2f (lim %.2f/%.1f) As %.2f ≤ %.2f" % (
              r["ato"]["topo_max"], r["ato"]["x_topo_max"], r["ato"]["base_min"], r["ato"]["x_base_min"], r["ato"]["lim_t"], r["ato"]["lim_c"], r["ato"]["As_topo_cm2"], r["ato"]["As_N3_cm2"]))
    print("   ELS", r["ELS"], "\n   ELU", r["ELU"], "\n   V", {k: v for k, v in r["cortante"].items()}, "\n   flecha", r["flecha"], "\n   içamento", r["icamento"], "\n   dente", r["dente"])
(AQ / "i110_r01.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
