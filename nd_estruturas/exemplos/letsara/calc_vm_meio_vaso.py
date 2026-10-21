"""Letsara rev04 — vigas do mezanino VM em MEIO VASO (padrão ND, skill vigas-apoio-laje-alveolar-nd).

A laje alveolar do mezanino vence 9,65 m entre as linhas 1 e 2 e apoia de UM lado só em cada VM: as duas linhas são
vigas de borda -> meio vaso. Alma de 25 no lado de fora (linha 1: fachada; linha 2: lado do pavilhão), aba de 15 x 20 para
dentro, topo plano no nível de apoio da laje (piso - 25 cm). Acima da alma e do vão até a ponta da laje: 2º estágio C30
concretado com a capa por quem executa a capa; estribos da alma saem em alças (N9) ao longo de toda a viga.

Peça: tratada como PRÉ-MOLDADA (NBR 9062:2017 3.8 / 12.1.1) -> γc 1,4 e γs 1,15 (8.1), até a fábrica comprovar o controle
de pré-fabricado (12.1.2); 2º estágio e capa moldados no local: γc 1,4. Sem escoramento (padrão ND, 11.6). Apoio sem recorte (7.5) em consolo CP-MEZ na face do pilar.

Apoio (rev04, pedido do Nathan): dente Gerber 35 × 35 na ponta maciça (40 × 65 em 1,00 m), fundo do consolo CP-MEZ alinhado
ao fundo da viga — escolha em calc_vm_dente.py (varredura de alma e altura de 5 em 5 cm, solução mais econômica).

Fases (5.2.1.4 e 11.3):
  F0 ato da protensão (fckj 28 MPa), saque, içamento (βa 1,3, 5.3.2.2) e estocagem;
  F1 montagem: só a peça pré-moldada leva peso próprio + laje + capa e 2º estágio frescos + 1 kN/m² de montagem;
     torção de montagem (laje de um lado só) equilibrada no apoio (neoprene deslocado + pinos);
  F2 final: seção composta (6.3) com revestimento + sobrecarga 5 kN/m²; continuidade sobre os apoios B, C e D pela
     armadura negativa do 2º estágio (passa no pilar por bainhas grauteadas — NBR 9062:2017 5.1.2.10 tipologia 1).
     Momento positivo dimensionado biapoiado (a continuidade fica como reserva, a favor do ELS) e o negativo pelo
     contínuo elástico (envoltória a favor da segurança nos dois sinais).
Unidades: kN, m; MPa só nas entradas. Compressão negativa nas tensões de ELS.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

AQ = Path(__file__).parent

# ------------------------------------------------------------------ materiais
FCK, FCKJ, FCK2 = 40.0, 32.0, 30.0                       # peça C40 (liberação e içamento 32 MPa), 2º estágio e capa C30
GC_PF, GS_PF, GC_LOC = 1.4, 1.15, 1.4                     # NBR 9062:2017 8.1 (pré-moldado) e NBR 6118 (moldado no local)
FCD, FCD2 = FCK / GC_PF * 1e3, FCK2 / GC_LOC * 1e3
FYD = 500 / GS_PF * 1e3
FYD_ALCA = min(FYD, 435e3)                                # NBR 9062:2017 6.3 / 7.3.6: fyd ≤ 435 MPa nas costuras
EP, ES = 195e6, 200e6
FPTK, FPYK = 1900e3, 1710e3
AP1 = 98.7e-6                                             # Ø12,7 CP-190 RB
SIG_PI = 1400e3                                           # kPa na pista (138,2 kN por cordoalha no macaco)
# DEC-032: perdas pela NBR 6118:2023 9.6.3 (prefabricados.perdas_pretracao) no lugar de 5 % / 20 % fixos:
# U 70 % (Ijuí/RS, a favor), t0 fictícia 5 dias (liberação com ~0,8 dia e cura térmica), laje + capa + 2º estágio aos 60 dias,
# revestimento aos 90 dias (superposição das fases, 8.2.11); γp 1,1 no ato (17.2.4.3.2 a)
U_AMB, T0_LIB, T_MONT, T_REV = 70.0, 5.0, 60.0, 90.0
GAMA_N_DENTE = 1.2                                        # NBR 9062:2017 7.3.1.1: parcela variável ≈ 50 % do Vd → 1,2 (decisão do engenheiro)
ECI = lambda fck: 5600 * math.sqrt(fck) * 1e3             # NBR 6118:2023 8.2.8 (granito)
ECS = lambda fck: (0.8 + 0.2 * fck / 80) * ECI(fck)
FCTM = lambda fck: 0.3 * fck ** (2 / 3)

# ------------------------------------------------------------------ geometria da obra (laje e vãos)
H_LAJE, H_CAPA = 0.20, 0.05
APOIO_LAJE = 0.10                                         # skill: apoio mínimo 10 cm na aba, neoprene em fita
B_ALMA, B_ABA, H_ABA = 0.25, 0.15, 0.20
B_TOT = B_ALMA + B_ABA                                    # 40 = largura do pilar
X_PONTA_LAJE = B_TOT - APOIO_LAJE                         # ponta da laje a 30 cm da face externa
VAO_LAJE = 9.65 - 2 * (B_TOT / 2 - APOIO_LAJE)            # laje de ponta a ponta = 9,45 m (VM centradas nos eixos)
TRIB = VAO_LAJE / 2
FOLGA = 0.03                                              # folga viga x face do pilar (tloc ±1 cm + tex ±1,5 cm + Δ) — 3.1 e 5.2.2
PAD = (0.15, 0.30, 0.010)                                 # neoprene a (vão) x b x h — NEO-5 150 × 300 × 10 (σk ≤ 7 MPa, 7.2.1.6)
X_PAD = 0.111 + PAD[0] / 2                                # rev04 com dente Gerber 35 × 35 (calc_vm_dente.py): centro do neoprene a
                                                          # 18,6 cm da face do pilar — a2 ≥ c + 3,5Ø (alças Ø16) no dente e no consolo
DENTE = dict(hd=0.50, ln=0.35, recorte=0.30, consolo_h=0.29, consolo_proj=0.35, macico=1.00)
VAOS = {"VM-01": 9.37, "VM-02": 9.48}                     # entre faces de pilar (A–B: P1 60 / P3 40; B–C: 40 / 40)

Y_LINHAS = (0.050, 0.120, 0.190)                         # linhas de cordoalhas: folga para os grampos N7 Ø12,5 do apoio a y = 85 mm
A_ALCA, L_ISOL = 1.10, 1.50                               # alças AL-1 a 1,10 m das pontas (prancha VM01); 2 cordoalhas isoladas por 1,5 m em cada ponta
# cargas (kN/m²)
PP_LAJE, CAPA, REV, Q_MEZ, Q_MONT = 2.80, H_CAPA * 25, 1.0, 5.0, 1.0


def retangulos(h):
    """Peça pré-moldada (x a partir da face externa, y do fundo)."""
    return [(0.0, B_ALMA, 0.0, h), (B_ALMA, B_TOT, h - H_ABA, h)]


def props(rects, n=None):
    n = n or [1.0] * len(rects)
    A = sum((x1 - x0) * (y1 - y0) * k for (x0, x1, y0, y1), k in zip(rects, n))
    yc = sum((x1 - x0) * (y1 - y0) * k * (y0 + y1) / 2 for (x0, x1, y0, y1), k in zip(rects, n)) / A
    xc = sum((x1 - x0) * (y1 - y0) * k * (x0 + x1) / 2 for (x0, x1, y0, y1), k in zip(rects, n)) / A
    I = sum(k * ((x1 - x0) * (y1 - y0) ** 3 / 12 + (x1 - x0) * (y1 - y0) * ((y0 + y1) / 2 - yc) ** 2)
            for (x0, x1, y0, y1), k in zip(rects, n))
    return A, xc, yc, I


def cordoalhas(n, h, n_top=0):
    """Grade 50 mm na alma (4 por linha a 50/100/150/200 mm da face externa), linhas a 50, 120 e 190 mm do fundo;
    n_top cordoalhas superiores na alma a 50 mm do topo (controle do ato da protensão)."""
    xs = [round(0.050 + 0.050 * k, 3) for k in range(int(round((B_ALMA - 0.100) / 0.050)) + 1)]
    pos = []
    for y in Y_LINHAS:
        for x in (xs if n - len(pos) >= len(xs) else ([round(B_ALMA / 2 - 0.05, 3), round(B_ALMA / 2 + 0.05, 3)] if n - len(pos) == 2 else xs[: n - len(pos)])):
            if len(pos) < n:
                pos.append((x, y))
    # superiores na ABA (x = B_ALMA + 0,05 e + 0,10): a resultante de todas as cordoalhas fica no centroide em x da seção T
    # (sem flecha lateral pela protensão) e o eixo da viga fica livre para o tubo TB-1 do pino do dente
    return pos + [(round(x, 3), h - 0.050) for x in (B_ALMA + 0.05, B_ALMA + 0.10)[:n_top]]


def sigma_p(eps):
    """CP-190 RB bilinear (NBR 6118:2023 8.4.5): elástico até fpyd, encruamento até fptd a 35 ‰."""
    fpyd, fptd = FPYK / GS_PF, FPTK / GS_PF
    ey = fpyd / EP
    if eps <= ey:
        return EP * eps
    return min(fptd, fpyd + (fptd - fpyd) * (eps - ey) / (0.035 - ey))


def MRd(rects_fcd, cords, barras, h_tot, eps_p_pre):
    """Momento resistente positivo (kN·m) por compatibilidade (εcu 3,5 ‰, retângulo 0,85 fcd com λ 0,8 — NBR 6118:2023
    17.2.2). rects_fcd: (x0,x1,y0,y1,fcd) com y do fundo; cords: (A, y); barras: (A, y) tracionadas."""
    def forca(x):
        yl = h_tot - 0.8 * x
        C = 0.0; Mc = 0.0
        for x0, x1, y0, y1, fcd in rects_fcd:
            a, b = max(y0, yl), y1
            if b > a:
                f = 0.85 * fcd * (x1 - x0) * (b - a)
                C += f; Mc += f * (a + b) / 2
        T = Mt = 0.0
        for A, y in cords:
            e = eps_p_pre + 0.0035 * (h_tot - y - x) / x
            s = sigma_p(e) * A; T += s; Mt += s * y
        for A, y in barras:
            e = 0.0035 * (h_tot - y - x) / x
            s = max(-FYD, min(FYD, ES * e)) * A; T += s; Mt += s * y
        return C - T, Mc - Mt, C, T
    lo, hi = 1e-4, h_tot
    for _ in range(80):
        x = (lo + hi) / 2
        if forca(x)[0] > 0:
            hi = x
        else:
            lo = x
    x = (lo + hi) / 2
    _, _, C, T = forca(x)
    yl = h_tot - 0.8 * x
    # braço: momento da compressão em torno da resultante de tração
    yT = sum(sigma_p(eps_p_pre + 0.0035 * (h_tot - y - x) / x) * A * y for A, y in cords) + \
        sum(max(-FYD, min(FYD, ES * 0.0035 * (h_tot - y - x) / x)) * A * y for A, y in barras)
    yT /= T
    yC = 0.0
    for x0, x1, y0, y1, fcd in rects_fcd:
        a, b = max(y0, yl), y1
        if b > a:
            yC += 0.85 * fcd * (x1 - x0) * (b - a) * (a + b) / 2
    yC /= C
    dmax = h_tot - min([y for _, y in cords] + [y for _, y in barras])
    return C * (yC - yT), x, x / dmax


def larguras(b_alma):
    """Muda a largura da alma (passo de 5 cm): recalcula a largura total, a ponta da laje e o vão da laje."""
    global B_ALMA, B_TOT, X_PONTA_LAJE, VAO_LAJE, TRIB
    B_ALMA = b_alma
    B_TOT = B_ALMA + B_ABA
    X_PONTA_LAJE = B_TOT - APOIO_LAJE
    VAO_LAJE = 9.65 - 2 * (B_TOT / 2 - APOIO_LAJE)
    TRIB = VAO_LAJE / 2


def analisar(h, n, nome, L_faces, cont=True, n_isol=2, n_top=0):
    L = L_faces - 2 * X_PAD                            # vão de cálculo entre centros dos neoprenes
    Lp = L_faces - 2 * FOLGA                           # comprimento da peça
    R = retangulos(h)
    A, xc, yc, I = props(R)
    Wi, Ws = I / yc, I / (h - yc)
    pos = cordoalhas(n, h, n_top)
    n = len(pos)
    Ap = n * AP1
    yp = sum(y for _, y in pos) / n
    ep = yc - yp
    # ---- cargas (kN/m)
    larg_capa = TRIB + B_TOT                            # capa sobre a laje tributária + sobre a viga
    g_pm = A * 25
    g_laje = PP_LAJE * TRIB
    g_capa = CAPA * larg_capa
    g_2e = X_PONTA_LAJE * H_LAJE * 25                   # 2º estágio 30 x 20 (acima da alma, até a ponta da laje)
    q_mont = Q_MONT * larg_capa
    g1 = g_pm + g_laje + g_capa + g_2e
    g2 = REV * larg_capa
    q2 = Q_MEZ * larg_capa
    M = lambda w: w * L ** 2 / 8

    # ---- seção composta (homogeneizada para o C40 da peça)
    n2 = ECS(FCK2) / ECS(FCK)
    bf = min(0.10 * L, TRIB) + B_TOT                    # capa colaborante (NBR 6118:2023 14.6.2.2, um lado só)
    Rc = R + [(0.0, X_PONTA_LAJE, h, h + H_LAJE), (0.0, bf, h + H_LAJE, h + H_LAJE + H_CAPA)]
    Ac, xcc, ycc, Ic = props(Rc, [1, 1, n2, n2])
    htot = h + H_LAJE + H_CAPA
    Wci = Ic / ycc

    # ---- perdas (NBR 6118:2023 9.6.3) — seção pré-moldada; fase 1 (laje, capa, 2º estágio) na peça isolada e o
    # revestimento na seção composta, convertido em momento equivalente na peça (mesma descompressão no nível do cabo)
    u_ar = h + B_ALMA + (h - H_ABA) + B_ABA + H_ABA + B_TOT  # perímetro da peça (T) em contato com o ar na liberação
    M_rev_eq = M(g2) * (ycc - yp) / Ic * I / ep
    from nd_estruturas.prefabricados import perdas_pretracao, Concreto as _C
    PP = perdas_pretracao(SIG_PI / 1e3, Ap, A, I, yc, yp, M(g_pm), _C(FCK), FCKJ, u_ar, U=U_AMB, t0_dias=T0_LIB,
                          fases=[(M(g1 - g_pm), T_MONT), (M_rev_eq, T_REV)])
    P0 = PP["P0"]
    Pinf = PP["Pinf"]
    eps_inf = Pinf / Ap / EP

    # ---- ELU
    # F1: pré-moldado isolado, combinação de construção (NBR 8681: γg 1,3 pré-moldado; γq 1,3 montagem)
    M1d = M(1.3 * g1 + 1.3 * q_mont)
    rects1 = [(x0, x1, y0, y1, FCD) for x0, x1, y0, y1 in R]
    MR1, x1, xd1 = MRd(rects1, [(AP1, y) for _, y in pos], [], h, eps_inf)
    # F2: seção composta, combinação última normal (γg 1,3 pré-moldado / 1,4 moldado local — usar 1,4 no rev + capa)
    M2d = M(1.4 * g1 + 1.4 * g2 + 1.4 * q2)                # combinação normal final (γg 1,4 em todas as permanentes — revisão independente)
    rects2 = rects1 + [(0.0, X_PONTA_LAJE, h, h + H_LAJE, FCD2), (0.0, bf, h + H_LAJE, htot, FCD2)]
    MR2, x2, xd2 = MRd(rects2, [(AP1, y) for _, y in pos], [], htot, eps_inf)

    # ---- ELS (protensão limitada, CAA II: ELS-F frequente e ELS-D quase permanente — NBR 6118:2023 tab. 13.4)
    sig = lambda Mpm, Mcomp, P: (-P / A - P * ep / Wi + Mpm / Wi + Mcomp / Wci) / 1e3   # fibra inferior (+ tração)
    sF = sig(M(g1), M(g2 + 0.6 * q2), Pinf)
    sD = sig(M(g1), M(g2 + 0.4 * q2), Pinf)
    sR = sig(M(g1), M(g2 + q2), Pinf)
    fctk = 0.7 * FCTM(FCK)
    fctf = 1.2 * fctk                                    # NBR 6118:2023 17.3.4 (seção T: α 1,2)
    # topo da peça em F1 (compressão) e topo da capa
    s_topo_F1 = (-Pinf / A + Pinf * ep / Ws - M(g1 + q_mont) / Ws) / 1e3
    # ---- ato da protensão (pontas: sem momento de peso; cordoalhas isoladas reduzem P0 na ponta)
    n_ponta = n - n_isol
    pos_p = pos[n_isol:]                                     # isoladas: as primeiras da linha de baixo (centrais no relatório)
    GP = 1.1                                                 # γp no ato (NBR 6118:2023 17.2.4.3.2 a), pré-tração
    P0p = GP * PP["sig_p0"] * 1e3 * n_ponta * AP1
    yp_p = sum(y for _, y in pos_p) / max(n_ponta, 1)
    ep_p = yc - yp_p
    s_ato_topo = (-P0p / A + P0p * ep_p / Ws) / 1e3
    s_ato_base = (-P0p / A - P0p * ep_p / Wi) / 1e3
    fctmj, fcj = FCTM(FCKJ), FCKJ
    # meio do vão no ato (com peso próprio)
    s_ato_meio_t = (-GP * P0 / A + GP * P0 * ep / Ws - M(g_pm) / Ws) / 1e3
    s_ato_meio_b = (-GP * P0 / A - GP * P0 * ep / Wi + M(g_pm) / Wi) / 1e3
    # fim do isolamento + lbpt: todas as cordoalhas aderentes, momento do peso próprio ainda pequeno (pior topo)
    from nd_estruturas.prefabricados import lbpt_cordoalha
    lbpt = lbpt_cordoalha(FCKJ, PP["sig_p0"])[0]
    x_iso = L_ISOL + lbpt
    M_iso = g_pm * x_iso * (Lp - x_iso) / 2
    s_ato_iso_t = (-GP * P0 / A + GP * P0 * ep / Ws - M_iso / Ws) / 1e3
    s_ato_iso_b = (-GP * P0 / A - GP * P0 * ep / Wi + M_iso / Wi) / 1e3

    # ---- flechas (NBR 9062:2017 5.4.3.4, Tab. 9; módulo secante Ecs; fluência φ 2,0 na parcela permanente)
    E = ECS(FCK)
    contra = -(Pinf * ep * L ** 2 / 8) / (E * I)          # contraflecha da protensão (negativo = para cima)
    f_pp = 5 * g_pm * L ** 4 / (384 * E * I)
    f_F1 = 5 * (g1 - g_pm) * L ** 4 / (384 * E * I)
    f_g2 = 5 * g2 * L ** 4 / (384 * E * Ic)
    f_q = 5 * 0.4 * q2 * L ** 4 / (384 * E * Ic)
    phi = PP["phi"]                                       # φ(t∞,t0) da Tab. 8.2 (mesmo das perdas)
    f_mont = contra + f_pp + f_F1                          # imediata após a montagem (peça isolada)
    f_final = (contra + f_pp + f_F1) * (1 + phi) + f_g2 * (1 + phi) + f_q * (1 + phi)
    lim_final = L / 250                                    # Tab. 9: final solidarizada L ≤ 15 m

    # ---- cortante (NBR 6118:2023 17.4.2.2, modelo I) na seção composta, Vd no apoio com continuidade (1,25 wL/2 no apoio interno)
    # fase 1 biapoiada (peça isolada); fase 2 contínua: reação no 1º apoio interno = 1,25 × biapoiada (a favor da segurança)
    Vd = 1.3 * g1 * L / 2 + (1.4 * g2 + 1.4 * q2) * L / 2 * (1.25 if cont else 1.0)
    d_c = htot - yp
    bw = B_ALMA
    VRd2 = 0.27 * (1 - FCK / 250) * FCD * bw * d_c
    fctd = 0.7 * FCTM(FCK) / GC_PF * 1e3
    Vc0 = 0.6 * fctd * bw * d_c
    Asw = max(0.0, (Vd - Vc0)) / (0.9 * d_c * min(FYD, 435e3)) * 1e4     # cm²/m
    Asw_min = 0.2 * FCTM(FCK) / 500 * bw * 1e4
    Asw_req = max(Asw, Asw_min)

    # ---- interface pré-moldado x 2º estágio (NBR 9062:2017 6.3.3; Tab. 10 — superfície áspera ≥ 5 mm a cada 30 mm)
    b_int = X_PONTA_LAJE
    z2 = htot - H_CAPA / 2 - yp
    Fmd = M(1.4 * g2 + 1.4 * q2) / z2                       # força no concreto de 2º estágio (só cargas após a solidarização)
    av = L / 2
    tau_sd = Fmd / (av * b_int) / 1e3                       # MPa
    fctd2 = 0.7 * FCTM(FCK2) / GC_LOC
    # alças N9 Ø8 c/15 (2 ramos) — rho = As/(b s)
    As_alca, s_alca = 2 * math.pi * 0.010 ** 2 / 4, 0.15              # alças N9 Ø10 c/15 (2 ramos) em toda a viga
    rho = As_alca / (b_int * s_alca)
    t = min(1.0, max(0.0, (rho - 0.002) / (0.005 - 0.002)))
    bs, bc = 0.9 * t, 0.3 + 0.3 * t
    tau_rd = bs * FYD_ALCA / 1e3 * rho + bc * fctd2
    tau_max = 0.25 * FCK2 / GC_LOC

    # ---- torção de montagem (F1): laje de um lado só
    xs_c = B_ALMA / 2                                       # centro de cisalhamento ≈ eixo da alma (seção T aberta)
    x_laje = B_TOT - APOIO_LAJE / 2                         # reação da laje no meio do apoio de 10 cm
    e_t = x_laje - xs_c
    w_exc = g_laje + CAPA * TRIB + Q_MONT * TRIB            # o que apoia na aba (excêntrico)
    t_k = w_exc * e_t                                        # kN·m/m
    T_ap_k = t_k * L / 2
    T_ap_d = 1.3 * T_ap_k
    from nd_estruturas.prefabricados import Concreto, torcao_retangular
    tor = torcao_retangular(B_ALMA, h, T_ap_d, 1.3 * (g1 + q_mont) * L / 2, Concreto(FCK))
    # equilíbrio no apoio: resultante de cargas permanentes F1 (sem montagem) — neoprene centrado nela
    R_perm = g1 * L / 2
    x_R = ((g_pm * xc + g_2e * X_PONTA_LAJE / 2 + (g_laje + CAPA * TRIB) * x_laje + CAPA * B_TOT * B_TOT / 2) / g1)
    e_mont = Q_MONT * TRIB * L / 2 * (x_laje - x_R) / (R_perm + Q_MONT * TRIB * L / 2)   # deslocamento da resultante com a montagem
    # neoprene NEO-5 centrado no eixo da peça (x = 20 cm). A resultante muda de lado durante a montagem: peça sozinha
    # (centroide a xc < 20 cm, gira para fora) e laje + capa (gira para dentro). O giro é impedido pela cantoneira CT-1
    # parafusada (buchas BR-3 no pilar + BR-4/BR-5 na VM, sem trilho nem solda — DEC-038, calc_ct1.py): NBR 9062:2017 11.1 (viga com torção ->
    # dispositivo contra giro) e 7.2.2.2 (dispositivo parafusado). Binário: neoprene embaixo + CT-1 no topo.
    nucleo = PAD[1] / 6
    x_pad = B_TOT / 2
    R_so = g_pm * L / 2
    T_so = R_so * (xc - x_pad)                                   # peça sozinha (negativo: gira para fora)
    R_f1 = (g1 + q_mont) * L / 2
    x_f1 = (g1 * x_R + q_mont * x_laje) / (g1 + q_mont)
    T_f1 = R_f1 * (x_f1 - x_pad)
    z_ct = h - 0.10 - PAD[2] / 2                                  # da face do neoprene ao parafuso da CT-1
    H_ct_d = 1.3 * max(abs(T_so), abs(T_f1)) / z_ct
    # sem a CT-1 a resultante sairia do núcleo do neoprene (b/6):
    sai_nucleo = max(abs(T_so) / R_so, abs(T_f1) / R_f1) > nucleo

    # ---- içamento e estocagem (βa 1,3 — 5.3.2.2): 2 alças a 0,21 Lp; tensões no topo e na base
    a_ic = A_ALCA                                             # alças dentro do trecho isolado (L_ISOL): força reduzida no balanço
    w_ic = 1.3 * g_pm
    M_bal = w_ic * a_ic ** 2 / 2
    M_vao = w_ic * (Lp - 2 * a_ic) ** 2 / 8 - M_bal
    P_alca = P0p if a_ic < L_ISOL else P0
    e_alca = ep_p if a_ic < L_ISOL else ep
    s_ic_t_bal = (-P_alca / A + P_alca * e_alca / Ws + M_bal / Ws) / 1e3
    s_ic_b_vao = (-P0 / A - P0 * ep / Wi + M_vao / Wi) / 1e3
    F_alca = 3.0 * g_pm * Lp / 2                              # βa 3,0 (5.3.2.2) — dimensionamento da alça (ruptura)
    # estabilidade lateral (6.1): L/bf ≤ 50 e L·h/bf² ≤ 500, bf = largura comprimida = 40 (topo)
    lat = (Lp / B_TOT, Lp * h / B_TOT ** 2)

    x_res = sum(x for x, _ in pos) / n
    ok_ct = H_ct_d <= 2 * 37.2                              # CT-1: 2 M16 8.8 ao corte (Fv,Rd 37,2 kN cada)
    ok = dict(ELU_F1=MR1 >= M1d and xd1 <= 0.45, ELU_F2=MR2 >= M2d and xd2 <= 0.45, ELS_F=sF <= fctf, ELS_D=sD <= 0.0,
              ato=max(s_ato_topo, s_ato_iso_t) <= 1.2 * fctmj and min(s_ato_base, s_ato_meio_b, s_ato_iso_b) >= -0.7 * fcj,
              flecha=f_final <= lim_final, VRd2=Vd <= VRd2, interface=tau_sd <= tau_rd and tau_sd <= tau_max,
              torcao=tor["ok"], apoio=ok_ct, icamento=s_ic_t_bal <= 1.2 * fctmj, lateral=lat[0] <= 50 and lat[1] <= 500)
    return dict(
        marca=nome, h_premoldado=h, h_final=round(htot, 2), cordoalhas=n, isoladas_pontas=n_isol, pos_cordoalhas_mm=[(round(x * 1000), round(y * 1000)) for x, y in pos],
        L_faces=L_faces, L_peca=round(Lp, 3), L_calculo=round(L, 3),
        secao=dict(A=round(A, 4), yc=round(yc, 4), xc=round(xc, 4), I=round(I, 6), Ac_hom=round(Ac, 4), yc_comp=round(ycc, 4), I_comp=round(Ic, 6), bf_capa=round(bf, 2), peso_t=round(g_pm * Lp / 10, 2), volume_m3=round(A * Lp, 3)),
        cargas=dict(g_pm=round(g_pm, 2), g_laje=round(g_laje, 2), g_capa=round(g_capa, 2), g_2e=round(g_2e, 2), q_mont=round(q_mont, 2), g1=round(g1, 2), g2=round(g2, 2), q2=round(q2, 2)),
        protensao=dict(P0=round(P0, 1), Pinf=round(Pinf, 1), ep=round(ep, 4), F_macaco_kN=round(SIG_PI * AP1, 1), sigma_pi=1400, perdas={k: (round(v, 3) if isinstance(v, float) else v) for k, v in PP.items()}),
        ELU=dict(M1d=round(M1d, 1), MRd1=round(MR1, 1), xd1=round(xd1, 3), M2d=round(M2d, 1), MRd2=round(MR2, 1), xd2=round(xd2, 3),
                 norma="NBR 9062:2017 6.3 (F1 peça isolada, F2 composta) e NBR 6118:2023 17.2"),
        ELS=dict(sig_F=round(sF, 2), lim_F=round(fctf, 2), sig_D=round(sD, 2), sig_rara=round(sR, 2), topo_F1=round(s_topo_F1, 2)),
        ato=dict(topo_ponta=round(s_ato_topo, 2), base_ponta=round(s_ato_base, 2), lim_t=round(1.2 * fctmj, 2), lim_c=-0.7 * fcj,
                 topo_meio=round(s_ato_meio_t, 2), base_meio=round(s_ato_meio_b, 2), topo_fim_isol=round(s_ato_iso_t, 2), base_fim_isol=round(s_ato_iso_b, 2),
                 x_fim_isol=round(x_iso, 2), lbpt_m=round(lbpt, 3), gama_p=GP, fckj=FCKJ, norma="NBR 6118:2023 17.2.4.3.2 (γp 1,1; 0,7 fckj; 1,2 fctm,j)"),
        flecha=dict(contraflecha_mm=round(contra * 1e3, 1), montagem_mm=round(f_mont * 1e3, 1), final_mm=round(f_final * 1e3, 1),
                    lim_final_mm=round(lim_final * 1e3, 1), lim_montagem_L500=round(L / 500 * 1e3, 1), norma="NBR 9062:2017 5.4.3.4 Tab. 9"),
        cortante=dict(Vd=round(Vd, 1), VRd2=round(VRd2, 1), Vc0=round(Vc0, 1), Asw_req_cm2m=round(Asw_req, 2)),
        interface=dict(tau_sd=round(tau_sd, 3), tau_rd=round(tau_rd, 3), tau_max=round(tau_max, 2), rho_alcas=round(rho * 100, 3), beta_s=round(bs, 2), beta_c=round(bc, 2),
                       b_int=b_int, norma="NBR 9062:2017 6.3.3 e Tab. 10"),
        torcao_montagem=dict(e_m=round(e_t, 3), t_kNm_m=round(t_k, 2), T_apoio_k=round(T_ap_k, 1), T_apoio_d=round(T_ap_d, 1), **tor,
                             x_resultante_perm_m=round(x_R, 3), desloc_resultante_montagem_m=round(e_mont, 3), nucleo_neoprene_m=round(nucleo, 3),
                             T_peca_sozinha_k=round(T_so, 1), T_F1_k=round(T_f1, 1), sai_do_nucleo_sem_CT1=sai_nucleo, z_CT1_m=round(z_ct, 3),
                             H_CT1_d_kN=round(H_ct_d, 1), CT1_cap_kN="2 M16 8.8 ao corte: 2 x 37,2 = 74,4 kN", norma_CT1="NBR 9062:2017 11.1 e 7.2.2.2"),
        negativa=negativa(L, g2, q2, h),
        icamento=dict(a_alca_m=a_ic, sig_topo_balanco=round(s_ic_t_bal, 2), sig_base_vao=round(s_ic_b_vao, 2), lim_t=round(1.2 * fctmj, 2), F_alca_ruptura_kN=round(F_alca, 1),
                      lateral_L_bf=round(lat[0], 1), lateral_Lh_bf2=round(lat[1], 1)),
        excentricidade_lateral_protensao_m=round(x_res - xc, 4),
        ok=ok, ok_geral=all(ok.values()),
    )


def negativa(L, g2, q2, h=0.65):
    """Continuidade (F2) nos apoios B, C, D: 4 vãos iguais, só cargas após a solidarização (rev + sobrecarga).
    M- máx no 1º apoio interno = 0,107 wL² (permanente) e 0,121 wL² (sobrecarga alternada) — ligação tratada como rígida
    (a favor da segurança na negativa; a positiva foi dimensionada biapoiada). Tipologia 1 da NBR 9062:2017 5.1.2.10
    (bainha corrugada grauteada + junta vertical grauteada entre o nariz do dente e o pilar + elastômero).
    Seção crítica: face do pilar, onde só existe o NARIZ do dente (h 35, largura 40 maciça) + 2º estágio + capa; a compressão
    fica no fundo do nariz e passa ao pilar pela junta grauteada (fck ≥ 30 MPa).
    N11: 6 Ø16 em 2 bainhas Ø50 (3 em cada) no pilar, a 12 cm acima do topo da peça; N12: 8 Ø12,5 na capa a 3 cm do topo,
    numa faixa ≤ 1,5 x 40 cm de cada lado do pilar (5.1.2.9), ≥ 50 % da negativa atravessando o pilar."""
    hd = DENTE["hd"]
    Md = (1.4 * 0.107 * g2 + 1.4 * 0.121 * q2) * L ** 2
    d1, d2 = hd + 0.12, hd + H_LAJE + H_CAPA - 0.03
    A1, A2 = 6 * math.pi * 1.6 ** 2 / 4, 8 * math.pi * 1.25 ** 2 / 4
    T = (A1 + A2) * 1e-4 * FYD_ALCA
    x = T / (0.85 * FCD * B_TOT * 0.8)
    dm = (A1 * d1 + A2 * d2) / (A1 + A2)
    MRd_ = T * (dm - 0.4 * x)
    phi = 0.016
    Led = 25 * phi + X_PAD
    Rsec = 0.75 * (A1 + A2) * 1e-4 * ES * dm ** 2 / Led
    return dict(Md_kNm=round(Md, 1), MRd_kNm=round(MRd_, 1), secao="face do pilar: nariz 40 × 35 + 2º estágio + capa", d_pilar_m=round(d1, 3),
                d_capa_m=round(d2, 3), x_m=round(x, 3), x_d=round(x / dm, 3),
                adotado="N11: 6 Ø16 em 2 bainhas corrugadas Ø50 no pilar (3 em cada, graute) + N12: 8 Ø12,5 na capa; L = 600 cm (armadura de obra)",
                As_ef_cm2=round(A1 + A2, 2), frac_no_pilar=round(A1 / (A1 + A2), 2), ok=MRd_ >= Md and A1 / (A1 + A2) >= 0.5 and x / dm <= 0.45,
                Rsec_kNm_rad=round(Rsec), Led_m=round(Led, 3), norma="NBR 9062:2017 5.1.2.9 e 5.1.2.10 (tipologia 1)")


H_PM, N_INF, N_SUP = 0.80, 8, 2                           # rev04 adotado: meio vaso h 80 com dente 50 × 35 (MEF Vu 484 kN ≥ 1,06·γn·Vd) — DEC-020

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(AQ.parents[1]))
    out = {k: analisar(H_PM, N_INF, k, L, n_top=N_SUP) for k, L in VAOS.items()}
    out["premissas"] = dict(fck=FCK, fckj=FCKJ, fcj_icamento=FCKJ, fck_2estagio=FCK2, tipo="pré-moldado (NBR 9062:2017 12.1.1)",
                            gama_c=GC_PF, gama_s=GS_PF, folga_m=FOLGA, neoprene=PAD, trib_laje=round(TRIB, 3), sem_escoramento=True,
                            Eci_MPa=round(ECI(FCK) / 1e3), Ecs_MPa=round(ECS(FCK) / 1e3), Eci_j_MPa=round(ECI(FCKJ) / 1e3),
                            h_pm=H_PM, n_inf=N_INF, n_sup=N_SUP, b_alma=B_ALMA, b_aba=B_ABA, h_aba=H_ABA, dente=DENTE, x_pad=X_PAD, pad=PAD)
    (AQ / "vm_meio_vaso.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    for k in VAOS:
        r = out[k]
        print(k, r["ok_geral"], {a: v for a, v in r["ok"].items() if not v}, r["ELU"], r["ELS"], r["ato"], r["torcao_montagem"]["H_CT1_d_kN"], r["negativa"])
