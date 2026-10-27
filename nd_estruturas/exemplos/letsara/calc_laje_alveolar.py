"""Letsara — laje alveolar do mezanino (níveis +3,15 e +6,55): dimensionamento completo por fase.

Substitui calc_laje_h20.py (conta simplificada, perdas estimadas em 20 %).
Normas: NBR 14861:2022, NBR 6118:2023, NBR 9062:2017; métodos de referência EN 1168:2005+A3:2011, EN 1992-1-1:2004 e
PCI Design Handbook (8ª ed.) onde a NBR remete a ensaio ou não detalha (marcado em cada verificação).
Grava laje_alveolar.json (lido pela ND-LET-LA01). Unidades: kN, m; tensões em MPa na saída (compressão negativa).
"""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path

AQ = Path(__file__).resolve().parent
sys.path.insert(0, str(AQ.parents[1]))
from nd_estruturas.prefabricados import Concreto, CORD, FPTK, FPYK, GAMA_P_ATO, perdas_pretracao, lbpt_cordoalha, fluencia_retracao, eci_j
from nd_estruturas.laje_alveolar import SecaoAlveolar, composta, vrd_tracao_alma, vrd1_nbr, frequencia_biapoiada, PCI_MULT

EP = 195000.0                                   # MPa
# ---------------------------------------------------------------- dados da obra (iguais ao modelo e às pranchas)
_VR = json.loads((AQ / "vm_retangular.json").read_text(encoding="utf-8"))["premissas"]   # rev09 (DEC-047/048): vigas retangulares 25
L_PECA = _VR["vao_laje"]                         # rev09: 9,60 = eixo a eixo − 2 × (b/2 − apoio 10) com as VM retangulares de 25
A_APOIO = 0.10                                  # apoio nominal na aba da VM (fita de neoprene 10 mm)
L = L_PECA - A_APOIO                            # vão de cálculo entre centros de apoio = 9,35 m
B_MOD = 1.25                                    # largura de influência por painel (1245 + junta 5)
H_CAPA = 0.05                                   # NBR 9062:2017 7.2.4.1.4.1: capa nominal 5 cm (≥ 3 cm em qualquer ponto)
FCK_LAJE, FCK_CAPA = 50.0, 30.0
_CM = json.loads((AQ / "cargas_mezanino.json").read_text(encoding="utf-8"))   # fonte única das cargas (rev09)
G_REV, Q = _CM["piso_390"]["revestimento"], _CM["piso_390"]["sobrecarga"]      # +3,90 governa (o +7,30 é laje sem uso: 1,7 + 1,0)
Q_MONT = 1.0                                    # kN/m² — montagem (pessoal, equipamento leve, concretagem da capa)
PSI1, PSI2 = 0.6, 0.4                           # NBR 6118 Tab. 11.2 — locais com elevada concentração de pessoas
G_REJ = 0.10                                    # kN/m² — rejunte das chavetas (graute)
U_AR = 65.0                                     # % — ambiente interno
CONC_L, CONC_C = Concreto(FCK_LAJE), Concreto(FCK_CAPA)
GAMA_G, GAMA_Q = 1.4, 1.4                       # NBR 8681 / NBR 6118 Tab. 11.1 (combinação normal)
BETA_A = 1.3                                    # NBR 9062:2017 5.3.2.2 — saque, manuseio, montagem e transporte (permanente desfavorável)
GAMA_F_TRANS = 1.3                              # NBR 9062:2017 5.3.2.1
SIG_PI = 1450.0                                 # MPa — NBR 6118:2023 9.6.1.2.1 b): pré-tração RB σpi ≤ 0,77 fptk = 1463 e ≤ 0,90 fpyk = 1539
CAA = "I"                                       # NBR 6118:2023 Tab. 6.1 nota b: ambiente interno seco e revestido (piso com revestimento, forro) — uma classe abaixo da II
#   → Tab. 13.4: pré-tração em CAA I = protensão parcial (nível 1, ELS-W wk ≤ 0,2 mm na frequente); verificado sem fissura (ELS-F), o que dispensa a conta de abertura.
#   Em CAA II seria protensão limitada (ELS-D na quase permanente obrigatório) — fica registrado como informativo.
DY_PAR = 0.035                                  # 2 cordoalhas na nervura de borda: c/c 35 mm na vertical (livre 22 mm ≥ 20 mm e ≥ Ø, NBR 6118:2023 18.3.2.2)
Y_CORD = 0.040                                  # eixo das cordoalhas a 40 mm do fundo (c ≥ 20 mm NBR 9062 9.2.1.1; c1 = 40 → Tab. 3 incêndio)

GEOMETRIAS = {
    "LP20": dict(b=1.245, h=0.200, n=6, d=0.152, passo=0.198),          # 7 nervuras (2 de borda 51,5 + 5 internas 46)
    "LP26,5": dict(b=1.245, h=0.265, n=5, d=0.190, passo=0.240),        # 6 nervuras (2 de borda 47,5 + 4 internas 50)
}
OPCOES = {   # cordoalhas por nervura, da esquerda para a direita (uma por nervura, simétrico)
    "LP20": [["2x12.7"] + ["12.7"] * 5 + ["2x12.7"], ["15.2"] + ["12.7"] * 5 + ["15.2"], ["15.2", "12.7", "12.7", "15.2", "12.7", "12.7", "15.2"], ["12.7"] * 7, ["9.5"] + ["12.7"] * 5 + ["9.5"], ["9.5", "9.5"] + ["12.7"] * 3 + ["9.5", "9.5"], ["9.5"] * 7],
    "LP26,5": [["12.7"] * 6, ["9.5"] + ["12.7"] * 4 + ["9.5"], ["9.5"] * 6],
}
FCKJ_OPC = (30.0, 35.0)                          # liberação ≥ 30 MPa (lbpt curto: cortante na ponta e transferência)


def txt_arr(a):
    """['2x12.7', '12.7', …] → '9 Ø12,7' (conta as cordoalhas de cada Ø)."""
    n = {}
    for d in a:
        k, q = (d[2:], 2) if d.startswith("2x") else (d, 1)
        n[k] = n.get(k, 0) + q
    return " + ".join(f"{n[d]} Ø{d.replace('.', ',')}" for d in sorted(n, reverse=True))


def sig_pd(eps):
    """NBR 6118:2023 8.4.5 — diagrama bilinear de cálculo do aço de protensão (CP-190 RB), MPa."""
    fpyd, fptd = FPYK / 1.15, FPTK / 1.15
    e_y, e_u = fpyd / EP, 0.035
    return EP * eps if eps <= e_y else min(fptd, fpyd + (fptd - fpyd) * (eps - e_y) / (e_u - e_y))


def mrd_composta(sec, cords, sig_pinf):
    """ELU flexão positiva da seção composta (laje + capa), compatibilidade de deformações (NBR 6118 17.2.2):
    bloco retangular 0,8x com 0,85fcd de cada concreto; εcu 3,5 ‰; Δεp ≤ 10 ‰ (domínio 2). kN·m (por painel)."""
    h_t = sec.h + H_CAPA
    fcd_c, fcd_l = 0.85 * FCK_CAPA / 1.4 * 1000, 0.85 * FCK_LAJE / 1.4 * 1000
    e_pre = sig_pinf / EP

    def comp(x):
        a = 0.8 * x
        Cc, Mc, y = 0.0, 0.0, 0.0                      # profundidades medidas do topo da capa
        n = 400
        for k in range(n):
            t = a * (k + 0.5) / n
            yy = h_t - t                                # cota a partir do fundo da laje
            w, f = (B_MOD, fcd_c) if yy >= sec.h else (sec.largura(yy), fcd_l)
            dC = w * f * a / n
            Cc += dC
            Mc += dC * t
        return Cc, Mc

    def forca_aco(x):
        T, M = 0.0, 0.0
        dmax = max(h_t - y for _, y, _ in cords)
        for _, y, dm in cords:
            dp = h_t - y
            ec = 0.0035 if dmax <= x else min(0.0035, 0.010 * x / (dmax - x))     # domínio 2 (Δεp ≤ 10 ‰) ou 3
            ep = e_pre + ec * (dp - x) / x
            ep = min(ep, e_pre + 0.010)
            s = sig_pd(ep)
            T += s * 1000 * CORD[dm]
            M += s * 1000 * CORD[dm] * dp
        return T, M
    lo, hi = 1e-4, h_t
    for _ in range(80):
        x = (lo + hi) / 2
        C, _ = comp(x)
        T, _ = forca_aco(x)
        lo, hi = (x, hi) if C < T else (lo, x)
    C, Mc = comp(x)
    T, Mt = forca_aco(x)
    return Mt - Mc, x, T                              # Mt − Mc = T·dp − C·(braço do topo) ≈ momento em relação ao topo


def analisar(nome_geo, arranjo, fckj):
    g = GEOMETRIAS[nome_geo]
    sec = SecaoAlveolar(**g)
    xn = sec.x_nervuras()
    C_LAT = 0.027                                     # eixo da cordoalha de borda a 27 mm da face: cobrimento lateral ≥ 20 mm (NBR 9062 9.2.1.1, alveolar)
    xn = [max(xn[0], -g["b"] / 2 + C_LAT)] + xn[1:-1] + [min(xn[-1], g["b"] / 2 - C_LAT)]
    cords = []
    for x, dm in zip(xn, arranjo):                    # "2x12.7": 2 cordoalhas na mesma nervura (de borda), uma sobre a outra, c/c DY_PAR
        if dm.startswith("2x"):                       # (rev12, decisão do engenheiro: LP20 9 Ø12,7; extrusora a confirmar com a fábrica)
            cords += [(x, Y_CORD, dm[2:]), (x, Y_CORD + DY_PAR, dm[2:])]
        else:
            cords.append((x, Y_CORD, dm))
    Ap = sum(CORD[dm] for _, _, dm in cords)
    yp = sum(CORD[dm] * y for _, y, dm in cords) / Ap
    e = sec.yc - yp
    g1 = sec.A * 25.0                                 # kN/m (peso da laje)
    g_capa = (H_CAPA * 25.0 + G_REJ) * B_MOD
    g_rev, q, q_m = G_REV * B_MOD, Q * B_MOD, Q_MONT * B_MOD
    M = lambda w: w * L * L / 8
    Mg1, Mcapa, Mrev, Mq, Mm = M(g1), M(g_capa), M(g_rev), M(q), M(q_m)
    # ---- perdas (NBR 6118 9.6.3), com fases: capa aos 30 d e revestimento aos 60 d (superposição 8.2.11)
    per = perdas_pretracao(SIG_PI, Ap, sec.A, sec.I, sec.yc, yp, Mg1, CONC_L, fckj, sec.perimetro,
                           L_pista=120.0, cravacao=0.006, t_lib_dias=0.75, U=U_AR, t0_dias=3.0,
                           fases=((Mcapa, 30.0), (Mrev, 60.0)))
    P0, Pinf, s0, sinf = per["P0"], per["Pinf"], per["sig_p0"], per["sig_pinf"]
    # ---- seções
    Ec_l, Ec_c = CONC_L.Ecs, CONC_C.Ecs
    nmod = Ec_c / Ec_l
    cp = composta(sec, B_MOD, H_CAPA, nmod)
    Wi_c = cp["I"] / cp["yc"]
    W_topo_laje_c = cp["I"] / (sec.h - cp["yc"]) if sec.h > cp["yc"] else 1e9
    W_topo_capa_c = cp["I"] / (cp["h_tot"] - cp["yc"]) / nmod
    sb = lambda P, Mm_: (-P / sec.A - P * e / sec.Wi + Mm_ / sec.Wi) / 1000          # MPa fundo, seção simples
    st = lambda P, Mm_: (-P / sec.A + P * e / sec.Ws - Mm_ / sec.Ws) / 1000          # MPa topo, seção simples
    fctm_j = 0.3 * fckj ** (2 / 3)
    fctk_j = 0.7 * fctm_j
    R = dict(geometria=nome_geo, secao=dict(b=g["b"], h=g["h"], n_alveolos=g["n"], d_alveolo=g["d"], passo=g["passo"],
                                           A_m2=round(sec.A, 5), yc_m=round(sec.yc, 4), I_m4=sec.I, peso_kN_m2=round(g1 / g["b"], 2),
                                           nervuras_mm=[round(v * 1000, 1) for v in sec.larg_nervuras()], x_nervuras_mm=[round(v * 1000, 1) for v in xn],
                                           bw_min_mm=round(sec.bw_min * 1000, 1)),
             cordoalhas=[dict(x_mm=round(x * 1000, 1), y_mm=round(y * 1000), diam=dm, F_macaco_kN=round(SIG_PI * CORD[dm] * 1000, 1)) for x, y, dm in cords],
             Ap_mm2=round(Ap * 1e6, 1), n_cord=len(cords), fckj=fckj, sig_pi=SIG_PI,
             perdas={k: (round(v, 3) if isinstance(v, float) else v) for k, v in per.items() if k != "fases"}, verif={})
    V = R["verif"]

    def reg(nome, valor, limite, uso, item, ok=None):
        V[nome] = dict(valor=round(valor, 3), limite=round(limite, 3), uso=round(uso, 3), ok=(uso <= 1.0) if ok is None else ok, item=item)
    # ---- transferência (NBR 6118 9.4.5)
    lbpt = max(lbpt_cordoalha(fckj, s0, diam_mm=float(dm.replace(",", ".")), gradual=True)[0] for _, _, dm in cords)
    R["lbpt_m"] = round(lbpt, 3)
    # ---- ato da protensão (NBR 6118 17.2.4.3.2): seção no fim da transferência (Mg mínimo) e no meio do vão
    Pato = GAMA_P_ATO * P0
    x = lbpt
    Mg_x = g1 * x * (L_PECA - x) / 2
    reg("ato_topo_fim_transferencia_MPa", st(Pato, Mg_x), 1.2 * fctm_j, st(Pato, Mg_x) / (1.2 * fctm_j), "NBR 6118:2023 17.2.4.3.2 b) (σt ≤ 1,2 fctm,j)")
    sc_ato = min(sb(Pato, Mg_x), sb(Pato, Mg1))
    reg("ato_fundo_MPa", sc_ato, -0.7 * fckj, sc_ato / (-0.7 * fckj), "NBR 6118:2023 17.2.4.3.2 a) (σc ≤ 0,7 fckj)")
    # ---- desforma, içamento por garras nas pontas, estocagem e transporte em 2 apoios a 0,30 m das pontas (βa 1,3)
    a_ap = 0.30
    Lh = L_PECA - 2 * a_ap
    M_mid = BETA_A * g1 * (Lh * Lh / 8 - a_ap * a_ap / 2)
    M_bal = BETA_A * g1 * a_ap * a_ap / 2
    P_ap = P0 * min(1.0, a_ap / lbpt)
    s_bal_topo = (-P_ap / sec.A + P_ap * e / sec.Ws + M_bal / sec.Ws) / 1000
    reg("manuseio_topo_no_apoio_MPa", s_bal_topo, fctk_j, s_bal_topo / fctk_j, "NBR 9062:2017 5.3.2 (βa 1,3) — sem fissura: σt ≤ fctk,inf(j)")
    s_mid_b = sb(P0, M_mid)
    reg("manuseio_fundo_meio_MPa", s_mid_b, -0.7 * fckj, s_mid_b / (-0.7 * fckj) if s_mid_b < 0 else 0.0, "NBR 9062:2017 5.3.2 (βa 1,3); compressão ≤ 0,7 fckj")
    s_mid_t = st(P0, BETA_A * 0.8 / BETA_A * M_mid)
    reg("transporte_topo_meio_favoravel_MPa", s_mid_t, fctk_j, s_mid_t / fctk_j, "NBR 9062:2017 5.3.2.2 (βa 0,8, permanente favorável)")
    Fgarra = GAMA_F_TRANS * BETA_A * g1 * L_PECA / 2
    R["icamento"] = dict(metodo="garra mecânica (pinça) nas 2 pontas, cabos verticais com balancim; sem alça embutida (NBR 9062 5.3.3: alça só em aço permitido)",
                         ponto_m=a_ap, peso_peca_kN=round(g1 * L_PECA, 2), peso_t=round(g1 * L_PECA / 9.81, 2), F_por_garra_d_kN=round(Fgarra, 1),
                         fcj_icamento=fckj, estocagem="calços de madeira alinhados a 0,30 m das pontas, até 8 peças por pilha (conferir com o fabricante)")
    # ---- montagem sem escoramento: laje isolada + capa fresca + rejunte + 1 kN/m² (NBR 9062 5.2.1.4 / 11.3)
    Md_m = GAMA_F_TRANS * (Mg1 + Mcapa + Mm)
    s_mont = sb(Pinf, Mg1 + Mcapa + Mm)
    reg("montagem_fundo_MPa", s_mont, CONC_L.fctk_inf, max(0.0, s_mont) / CONC_L.fctk_inf, "NBR 9062:2017 5.2.1.4 — laje isolada com capa fresca + 1 kN/m²; σt ≤ fctk,inf")
    # ---- retração diferencial capa × laje (EN 1168 4.3.1.2; NBR 9062 5.2.1.3 / 6.3)
    phi_c, ecs_c = fluencia_retracao(U_AR, 20.0, 7.0)
    _, ecs_l = fluencia_retracao(U_AR, 2 * sec.A / sec.perimetro * 100, 3.0)
    d_eps = abs(ecs_c) - 0.5 * abs(ecs_l)                       # metade da retração da laje já ocorreu na montagem (30 d)
    E_eff = Ec_c / (1 + 0.8 * phi_c)
    Ncs = d_eps * E_eff * B_MOD * H_CAPA                       # kN
    ecap = cp["y_capa"] - cp["yc"]
    s_cs_b = (-Ncs / cp["A"] + Ncs * ecap * cp["yc"] / cp["I"]) / 1000    # MPa no fundo: −N (compressão) no centroide da capa, na seção composta
    R["retracao_diferencial"] = dict(d_eps=round(d_eps * 1000, 3), N_kN=round(Ncs, 1), sig_fundo_MPa=round(s_cs_b, 3), phi_capa=round(phi_c, 2))
    # ---- serviço, seção composta (NBR 6118 13.4.2 Tab. 13.4: pré-tração CAA II → protensão limitada)
    base = (-Pinf / sec.A - Pinf * e / sec.Wi + (Mg1 + Mcapa) / sec.Wi) / 1000 + Mrev / Wi_c / 1000 + s_cs_b
    s_qp = base + PSI2 * Mq / Wi_c / 1000
    s_fr = base + PSI1 * Mq / Wi_c / 1000
    s_ra = base + Mq / Wi_c / 1000
    fct_f = 1.2 * CONC_L.fctk_inf                              # NBR 6118 17.3.1 (α = 1,2 seção T/duplo T)
    s_P = (-Pinf / sec.A - Pinf * e / sec.Wi) / 1000                     # pré-compressão do fundo (uso = carga / pré-compressão disponível)
    if CAA == "I":
        R["informativo_ELS_D"] = dict(valor=round(s_qp, 3), uso=round((s_qp - s_P) / (-s_P), 3),
                                      nota="ELS-D (descompressão, ψ2 0,4) só seria exigido em CAA II (protensão limitada)")
    else:
        reg("ELS_D_quase_perm_fundo_MPa", s_qp, 0.0, (s_qp - s_P) / (-s_P), "NBR 6118:2023 Tab. 13.4 — ELS-D (ψ2 0,4): σ ≤ 0")
    reg("ELS_F_frequente_fundo_MPa", s_fr, fct_f, (s_fr - s_P) / (fct_f - s_P),
        "NBR 6118:2023 Tab. 13.4 — " + ("ELS-W (CAA I, parcial): sem fissura na frequente (ψ1 0,6), σ ≤ 1,2 fctk,inf → wk = 0" if CAA == "I" else "ELS-F (ψ1 0,6): σ ≤ 1,2 fctk,inf"))
    R["classe_protensao"] = "parcial (nível 1) — CAA I, ambiente interno seco e revestido" if CAA == "I" else "limitada (nível 2) — CAA II"
    R["ELS_rara_fundo_MPa"] = round(s_ra, 3)
    s_top_c = (-Pinf / sec.A + Pinf * e / sec.Ws - (Mg1 + Mcapa) / sec.Ws) / 1000 - (Mrev + Mq) / W_topo_laje_c / 1000
    reg("ELS_compressao_topo_laje_MPa", s_top_c, -0.6 * FCK_LAJE, s_top_c / (-0.6 * FCK_LAJE), "NBR 6118:2023 17.2.4.3 (σc ≤ 0,6 fck, rara)")
    # ---- ELU flexão (seção composta)
    Md = GAMA_G * (Mg1 + Mcapa + Mrev) + GAMA_Q * Mq
    MRd, xln, Tp = mrd_composta(sec, cords, sinf)
    reg("ELU_flexao_kNm", Md, MRd, Md / MRd, "NBR 6118:2023 17.2.2 — seção composta (NBR 9062 6.3: monolítica no ELU)")
    V["ELU_flexao_kNm"]["x_LN_mm"] = round(xln * 1000, 1)
    reg("ELU_montagem_laje_isolada_kNm", Md_m, mrd_simples(sec, cords, sinf), Md_m / mrd_simples(sec, cords, sinf), "NBR 9062:2017 5.4.1 / 11.3 — laje isolada, capa fresca")
    # ---- cortante (sem armadura transversal)
    w_d = GAMA_G * (g1 + g_capa + g_rev) + GAMA_Q * q
    Vd_ap = w_d * L / 2
    lx = A_APOIO + sec.h / 2                                   # seção crítica: h/2 além da face interna do apoio (EN 1168 4.3.3.2.2)
    al = min(1.0, lx / (1.2 * lbpt))                           # EN 1992-1-1 6.2.2(2): αl = lx/lpt2 ≤ 1, lpt2 = 1,2 lpt
    fctd_l = CONC_L.fctk_inf / 1.4
    VRdc, ycrit = vrd_tracao_alma(sec, fctd_l, Pinf, alfa_l=al)
    Vd_x = Vd_ap - w_d * (lx - A_APOIO / 2)
    reg("ELU_cortante_tracao_alma_kN", Vd_x, VRdc, Vd_x / VRdc, "EN 1168 4.3.3.2.2 / EN 1992-1-1 eq. (6.4) — região não fissurada; NBR 14861:2022 (cortante sem estribos)")
    V["ELU_cortante_tracao_alma_kN"].update(alfa_l=round(al, 3), y_crit_mm=round(ycrit * 1000))
    d_c = sec.h + H_CAPA - yp
    VRd1 = vrd1_nbr(sec.bw_min, d_c, FCK_LAJE, Ap / (sec.bw_min * d_c), 0.9 * Pinf / sec.A / 1000)
    reg("ELU_cortante_flexao_VRd1_kN", Vd_ap, VRd1, Vd_ap / VRd1, "NBR 6118:2023 17.4.2.2 (bw = soma das nervuras, k = 1,6 − d, σcp com γp 0,9)")
    # ---- LA-01R: recorte 45 × 20 na ponta junto ao pilar (pilar 40 + 2 × 2,5 de folga) — corta as nervuras e cordoalhas centrais;
    #      a reação do painel passa pelas nervuras que sobram. Alternativa: preencher na fábrica os 2 alvéolos vizinhos ao recorte
    #      (concreto da laje, 60 cm a partir da ponta), que contam 50 % na largura de alma (NBR 14861:2022 — alvéolos preenchidos).
    XR = (-0.225, 0.225)
    for tag, pre in (("sem_preencher", ()), ("alveolos_preenchidos", tuple(k for k, xa in enumerate(sec.x_alveolos()) if abs(abs(xa) - 0.297) < 0.01))):
        sr = SecaoAlveolar(**g, recorte=XR, preenchidos=pre)
        ficam = [c for c in cords if not (XR[0] - 0.01 < c[0] < XR[1] + 0.01)]
        Ap_r = sum(CORD[dm] for _, _, dm in ficam)
        P_r = Pinf * Ap_r / Ap
        Vr, _ = vrd_tracao_alma(sr, fctd_l, P_r, alfa_l=al)
        V1r = vrd1_nbr(sr.bw_min, d_c, FCK_LAJE, Ap_r / (sr.bw_min * d_c), 0.9 * P_r / sr.A / 1000)
        R.setdefault("LA01R", {})[tag] = dict(alveolos_preenchidos=[k + 1 for k in pre], n_cord_ponta=len(ficam), bw_mm=round(sr.bw_min * 1000),
                                              VRd_tracao_alma=round(Vr, 1), VRd1=round(V1r, 1), Vd=round(Vd_x, 1), Vd_apoio=round(Vd_ap, 1),
                                              uso=round(max(Vd_x / Vr, Vd_ap / V1r), 3))
    la = R["LA01R"]
    adot = "sem_preencher" if la["sem_preencher"]["uso"] <= 1 else "alveolos_preenchidos"
    la["adotado"] = adot
    reg("LA01R_cortante_ponta_recortada_kN", Vd_ap, min(la[adot]["VRd_tracao_alma"], la[adot]["VRd1"]), la[adot]["uso"],
        "LA-01R: EN 1168 4.3.3.2.2 + NBR 6118 17.4.2.2 com as nervuras que ficam (" + ("sem preenchimento" if adot == "sem_preencher" else "2 alvéolos preenchidos 60 cm, 50 % — NBR 14861:2022") + ")")
    # ---- interface capa × laje (NBR 9062 6.3; EN 1992-1-1 6.2.5 superfície lisa/extrudada: c = 0,20)
    Vd2 = (GAMA_G * g_rev + GAMA_Q * q) * L / 2
    tau = Vd2 * cp["Ac_hom"] * ecap / cp["I"] / g["b"] / 1000
    fctd_c = CONC_C.fctk_inf / 1.4
    v_rdi = 0.20 * fctd_c
    reg("interface_capa_MPa", tau, v_rdi, tau / v_rdi, "EN 1992-1-1:2004 6.2.5 (c = 0,20, superfície extrudada sem rugosidade intencional); NBR 9062:2017 6.3.3 (As = 0)")
    # ---- apoio (EN 1992-1-1 10.9.5.2; NBR 9062 7.2) e neoprene em fita
    Rk = (g1 + g_capa + g_rev + q) * L_PECA / 2
    Rd = Vd_ap
    a1 = max(0.025, Rd / (g["b"] * 0.4 * CONC_C.fcd))           # 10.9.5.2: a1 = FEd/(b·fRd), fRd = 0,4fcd (apoio a seco), mín. 25 mm (Tab. 10.2)
    a_nec = a1 + 0.005 + 0.0 + math.sqrt(0.010 ** 2 + (L_PECA / 2500) ** 2)
    reg("apoio_m", a_nec, A_APOIO, a_nec / A_APOIO, "EN 1992-1-1 10.9.5.2 (a = a1 + a2 + a3 + √(Δa2² + Δa3²)); nominal 10 cm na aba da VM")
    s_neo = Rk / (g["b"] * 0.05) / 1000
    reg("neoprene_fita_MPa", s_neo, 7.0, s_neo / 7.0, "fita de neoprene 10 × 50 mm contínua; σ ≤ 7 MPa (conferir catálogo)")
    # ---- flechas (PCI 5.8.2.1; limites NBR 9062:2017 Tab. 9)
    Eci_j_ = eci_j(CONC_L, fckj)
    d_p = P0 * e * L * L / (8 * Eci_j_ * sec.I)
    d5 = lambda w, E, I: 5 * w * L ** 4 / (384 * E * I)
    d_g1 = d5(g1, Eci_j_, sec.I)
    d_capa = d5(g_capa, Ec_l, sec.I)
    d_rev = d5(g_rev, Ec_l, cp["I"])
    d_q = d5(q, Ec_l, cp["I"])
    m1, mf = PCI_MULT["montagem"], PCI_MULT["final_composta"]
    fab = d_p - d_g1
    mont = m1["P"] * d_p - m1["g1"] * d_g1
    iso = mont - d_capa
    final_sem_q = mf["P"] * d_p - mf["g1"] * d_g1 - mf["capa"] * d_capa - mf["g_sup"] * d_rev
    final = final_sem_q - mf["g_sup"] * PSI2 * d_q
    R["flechas_mm"] = dict(contraflecha_fabricacao=round(fab * 1000, 1), lim_L300=round(L / 300 * 1000, 1),
                           contraflecha_montagem=round(mont * 1000, 1), lim_L250=round(L / 250 * 1000, 1),
                           peca_isolada_apos_capa=round(-iso * 1000, 1), lim_L500=round(L / 500 * 1000, 1),
                           solidarizada_sem_q=round(-final_sem_q * 1000, 1), lim_L350=round(L / 350 * 1000, 1),
                           final=round(-final * 1000, 1), lim_final_L250=round(L / 250 * 1000, 1),
                           convencao="positivo = para baixo nas flechas; contraflechas positivas para cima")
    reg("flecha_final_mm", max(0.0, -final * 1000), L / 250 * 1000, max(0.0, -final) / (L / 250), "NBR 9062:2017 Tab. 9 (L ≤ 15 m: L/250), PCI 5.8.2.1")
    reg("contraflecha_montagem_mm", max(0.0, mont * 1000), L / 250 * 1000, max(0.0, mont) / (L / 250), "NBR 9062:2017 Tab. 9 (contraflecha na montagem ≤ L/250)")
    reg("contraflecha_fabricacao_mm", max(0.0, fab * 1000), L / 300 * 1000, max(0.0, fab) / (L / 300), "NBR 9062:2017 Tab. 9 (contraflecha de fabricação ≤ L/300)")
    # ---- vibração (NBR 6118:2023 23.3): f ≥ 1,2 fcrit
    EI_dyn = CONC_L.Eci * cp["I"]
    m = (g1 + g_capa + g_rev) / 9.81
    f1 = frequencia_biapoiada(EI_dyn, m, L)
    R["vibracao"] = dict(f1_Hz=round(f1, 2), f_min_academia_Hz=round(1.2 * 8.0, 1), f_min_escritorio_Hz=round(1.2 * 4.0, 1),
                         ok_academia=f1 >= 9.6, ok_escritorio=f1 >= 4.8,
                         item="NBR 6118:2023 23.3 (Tab. 23.1: ginásio/academia 8,0 Hz; escritório 3,0–4,0 Hz)")
    R["incendio"] = dict(c1_mm=round(Y_CORD * 1000), h_total_mm=round((sec.h + H_CAPA) * 1000),
                         nota="NBR 9062:2017 Tab. 3 (biapoiada): c1 40 mm atende TRRF 90 min até MSd,fi/MRd 59 % — conferir o TRRF exigido pelo CBM")
    R["cargas"] = dict(g1=round(g1 / B_MOD, 2), capa_rejunte=round(g_capa / B_MOD, 2), revestimento=G_REV, sobrecarga=Q, montagem=Q_MONT, unidade="kN/m²",
                       Md_kNm=round(Md, 1), Vd_kN=round(Vd_ap, 1), Rk_kN=round(Rk, 1))
    R["ok"] = all(v["ok"] for v in V.values())
    R["uso_max"] = round(max(v["uso"] for v in V.values()), 3)
    return R


def mrd_simples(sec, cords, sig_pinf):
    """MRd da laje isolada (sem capa) — mesma rotina com a capa anulada."""
    global H_CAPA
    h0 = H_CAPA
    H_CAPA = 1e-6
    try:
        return mrd_composta(sec, cords, sig_pinf)[0]
    finally:
        H_CAPA = h0


if __name__ == "__main__":
    estudos = []
    for geo, ops in OPCOES.items():
        for arr in ops:
            for fj in FCKJ_OPC:
                r = analisar(geo, arr, fj)
                falhas = [k for k, v in r["verif"].items() if not v["ok"]]
                estudos.append(dict(geometria=geo, arranjo=txt_arr(arr),
                                    Ap_mm2=r["Ap_mm2"], fckj=fj, ok=r["ok"], uso_max=r["uso_max"], falhas=falhas, f1_Hz=r["vibracao"]["f1_Hz"]))
                print(f"{geo:7s} {estudos[-1]['arranjo']:22s} fckj {fj:4.0f}  Ap {r['Ap_mm2']:6.1f}  ok={r['ok']!s:5s} uso {r['uso_max']:.2f}  falhas {falhas}")
    # adotada: LP20 (não muda a VM nem o nível), menor Ap e menor fckj que passam
    cand = [e for e in estudos if e["ok"] and e["geometria"] == "LP20" and "15,2" not in e["arranjo"]] or [e for e in estudos if e["ok"] and "15,2" not in e["arranjo"]]   # cordoalha só Ø12,7 ou Ø9,5 (regra ND)
    esc = min(cand, key=lambda e: (e["Ap_mm2"], e["fckj"]))
    geo = esc["geometria"]
    arr = next(a for a in OPCOES[geo] if txt_arr(a) == esc["arranjo"])
    R = analisar(geo, arr, esc["fckj"])
    R["estudo_alternativas"] = estudos
    R["normas"] = ["NBR 14861:2022", "NBR 6118:2023", "NBR 9062:2017", "EN 1168:2005+A3:2011 (referência)", "EN 1992-1-1:2004 (referência)", "PCI Design Handbook 8ª ed. (flechas)"]
    # rev09: laje de cima (+7,30, sem uso) com a mesma peça — conferência; e laje curta LA-03/LA-04 (escada, +3,90)
    G_REV, Q = _CM["laje_730"]["revestimento"], _CM["laje_730"]["sobrecarga"]
    R730 = analisar(geo, arr, esc["fckj"])
    R["nivel_730"] = dict(ok=R730["ok"], uso_max=R730["uso_max"], cargas=R730["cargas"], flechas_mm=R730["flechas_mm"],
                          falhas=[k for k, v in R730["verif"].items() if not v["ok"]], obs="mesma marca LA-01 (o +3,90 governa)")
    G_REV, Q = _CM["piso_390"]["revestimento"], _CM["piso_390"]["sobrecarga"]
    L_LONGA = L_PECA
    from geometria import Y_VM1 as _YV1, P6_ESC as _P6E
    _bv = _VR["b"]
    L_PECA = round((_P6E[1] - (_bv / 2 - A_APOIO)) - (_YV1 + _bv / 2 - A_APOIO), 3)   # rev12: VM da linha 1 (eixo −0,15) à viga P6–P7, apoio 10 cm em cada
    L = L_PECA - A_APOIO
    curta = None
    for a_ in sorted(OPCOES[geo], key=lambda a: sum(CORD[d[2:]] * 2 if d.startswith("2x") else CORD[d] for d in a)):
        for fj in FCKJ_OPC:
            rc = analisar(geo, a_, fj)
            if rc["ok"]:
                curta = (a_, fj, rc)
                break
        if curta:
            break
    if curta:
        a_, fj, rc = curta
        R["LA03"] = dict(L_peca=L_PECA, arranjo=txt_arr(a_), fckj=fj,
                         cordoalhas=rc["cordoalhas"], ok=rc["ok"], uso_max=rc["uso_max"], flechas_mm=rc["flechas_mm"], peso_t=rc["icamento"]["peso_t"] if "peso_t" in rc["icamento"] else None,
                         obs="laje curta entre a linha 1 e a viga P6–P7 (+3,90), só no vão da escada")
    else:
        R["LA03"] = dict(L_peca=L_PECA, ok=False)
    L_PECA = L_LONGA; L = L_PECA - A_APOIO
    (AQ / "laje_alveolar.json").write_text(json.dumps(R, indent=1, ensure_ascii=False), encoding="utf-8")
    print("\n+7,30:", R["nivel_730"]["ok"], R["nivel_730"]["falhas"], " LA-03:", R["LA03"].get("arranjo"), R["LA03"]["ok"], R["LA03"].get("uso_max"))
    print("\nADOTADA:", geo, esc["arranjo"], "fckj", esc["fckj"])
    for k, v in R["verif"].items():
        print(f"  {k:40s} {v['valor']:9.3f}  lim {v['limite']:9.3f}  uso {v['uso']:.2f}  {'ok' if v['ok'] else 'NÃO'}")
    print(" lbpt", R["lbpt_m"], " perdas", round(R["perdas"]["perda_total_pct"], 1), "%  flechas", R["flechas_mm"], "\n vibração", R["vibracao"], "\n cs", R["retracao_diferencial"])
