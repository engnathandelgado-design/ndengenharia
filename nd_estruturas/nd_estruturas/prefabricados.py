"""Pré-moldados ND — seções, protensão por pré-tração, pilares em balanço e torção.

Convenção do pacote: kN, m; tensões em kPa (kN/m²) internamente, MPa só na saída.
Compressão negativa nas tensões de seção (σ < 0 = compressão).

Normas: NBR 6118:2023 (concreto, ELS/ELU, torção 17.5), NBR 9062:2017 (pré-moldado),
NBR 8681 (combinações). Itens marcados (conferir) são simplificações de pré-dimensionamento.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math

# --------------------------------------------------------------------------- materiais


@dataclass(frozen=True)
class Concreto:
    fck: float  # MPa
    alfa_e: float = 1.0  # granito/gnaisse (basalto = 1,2)

    def __post_init__(self):
        if not 20 <= self.fck <= 90:
            raise ValueError("fck fora de 20–90 MPa")

    @property
    def fcd(self) -> float:  # kPa
        return self.fck / 1.4 * 1000

    @property
    def fctm(self) -> float:  # MPa
        return 0.3 * self.fck ** (2 / 3) if self.fck <= 50 else 2.12 * math.log(1 + 0.11 * self.fck)

    @property
    def fctk_inf(self) -> float:  # MPa
        return 0.7 * self.fctm

    @property
    def Eci(self) -> float:  # kPa
        if self.fck <= 50:
            return self.alfa_e * 5600 * math.sqrt(self.fck) * 1000
        return 21.5e3 * self.alfa_e * (self.fck / 10 + 1.25) ** (1 / 3) * 1000

    @property
    def Ecs(self) -> float:  # kPa
        ai = min(1.0, 0.8 + 0.2 * self.fck / 80)
        return ai * self.Eci


FYD_CA50 = 500 / 1.15 * 1000  # kPa
ES = 200e6  # kPa
EP = 195e6  # kPa
CORD = {"9.5": 0.548e-4, "12.7": 0.987e-4, "15.2": 1.40e-4}  # m², CP-190 RB


# --------------------------------------------------------------------------- seção poligonal


@dataclass
class Secao:
    """Polígono (x, y) em m, y para cima a partir da face inferior."""

    nome: str
    pts: list

    def _props(self):
        A = Sx = Ixx = 0.0
        p = self.pts + [self.pts[0]]
        for (x0, y0), (x1, y1) in zip(p[:-1], p[1:]):
            c = x0 * y1 - x1 * y0
            A += c
            Sx += (y0 + y1) * c
            Ixx += (y0 * y0 + y0 * y1 + y1 * y1) * c
        A /= 2
        yc = Sx / (6 * A)
        Ixx = Ixx / 12 - A * yc * yc
        return abs(A), yc, abs(Ixx)

    @property
    def A(self):
        return self._props()[0]

    @property
    def yc(self):
        return self._props()[1]

    @property
    def I(self):
        return self._props()[2]

    @property
    def h(self):
        ys = [y for _, y in self.pts]
        return max(ys) - min(ys)

    @property
    def Wi(self):  # módulo da fibra inferior
        return self.I / self.yc

    @property
    def Ws(self):
        return self.I / (self.h - self.yc)

    def largura_em(self, y):
        """Largura da seção na cota y (polígono simétrico e convexo por faixas)."""
        xs = []
        p = self.pts + [self.pts[0]]
        for (x0, y0), (x1, y1) in zip(p[:-1], p[1:]):
            if (y0 - y) * (y1 - y) <= 0 and y0 != y1:
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        return max(xs) - min(xs) if len(xs) >= 2 else 0.0


def secao_retangular(b, h, nome=None):
    return Secao(nome or f"R{b*100:.0f}x{h*100:.0f}", [(-b / 2, 0), (b / 2, 0), (b / 2, h), (-b / 2, h)])


def secao_I(h, bs=0.40, ts=0.10, ms=0.05, bw=0.12, bi=0.40, ti=0.15, mi=0.08, nome=None):
    """Viga I simétrica no eixo x: mesa sup. bs×ts com mísula ms, alma bw, mesa inf. bi×ti com mísula mi."""
    pts = [
        (-bi / 2, 0), (bi / 2, 0), (bi / 2, ti), (bw / 2, ti + mi),
        (bw / 2, h - ts - ms), (bs / 2, h - ts), (bs / 2, h), (-bs / 2, h),
        (-bs / 2, h - ts), (-bw / 2, h - ts - ms), (-bw / 2, ti + mi), (-bi / 2, ti),
    ]
    return Secao(nome or f"I{h*100:.0f}", pts)


# --------------------------------------------------------------------------- pré-tração: perdas, transferência, ato (DEC-032)

FPTK, FPYK = 1900.0, 1710.0                        # MPa, CP-190 RB (NBR 7483)
GAMA_P_ATO = 1.1                                   # NBR 6118:2023 17.2.4.3.2 a) — ato da protensão, pré-tração
SIG_ACO_ATO = 250.0                                # MPa — 17.2.4.3.2 c) acréscimo máximo na armadura de tração (barra nervurada)

# NBR 6118:2023 Tab. 8.4 — ψ1000 (%) da cordoalha de relaxação baixa (RB) em função de σp0/fptk
_PSI1000_RB = ((0.5, 0.0), (0.6, 1.3), (0.7, 2.5), (0.8, 3.5))

# NBR 6118:2023 Tab. 8.2 — valores característicos superiores de φ(t∞,t0) e εcs(t∞,t0) (‰), concretos C20 a C45
# (para C50 o bloco C20–C45 é usado a favor da segurança: o concreto mais resistente flui e retrai menos).
# chave: (U %, t0 dias) -> (φ para 2Ac/u = 20 cm, φ para 60 cm, εcs 20 cm, εcs 60 cm)
_TAB_8_2 = {
    (40, 5): (4.6, 3.8, -0.53, -0.47), (40, 30): (3.4, 3.0, -0.44, -0.45), (40, 60): (2.9, 2.7, -0.39, -0.43),
    (55, 5): (3.9, 3.3, -0.48, -0.43), (55, 30): (2.9, 2.6, -0.41, -0.41), (55, 60): (2.5, 2.3, -0.36, -0.40),
    (75, 5): (2.8, 2.4, -0.36, -0.32), (75, 30): (2.2, 2.0, -0.33, -0.31), (75, 60): (1.9, 1.8, -0.30, -0.31),
    (90, 5): (2.0, 1.9, -0.18, -0.15), (90, 30): (1.6, 1.5, -0.17, -0.15), (90, 60): (1.4, 1.4, -0.17, -0.15),
}


def sigma_pi_max(fptk=FPTK, fpyk=FPYK):
    """NBR 6118:2023 9.6.1.2.1 b) — pré-tração, aço RB: σpi ≤ 0,77 fptk e ≤ 0,85 fpyk (MPa)."""
    return min(0.77 * fptk, 0.85 * fpyk)


def psi1000_rb(r):
    """NBR 6118:2023 Tab. 8.4 — ψ1000 (%) da cordoalha RB para r = σp/fptk (interpolação linear; 0 abaixo de 0,5)."""
    if r <= 0.5:
        return 0.0
    for (a, pa), (b, pb) in zip(_PSI1000_RB[:-1], _PSI1000_RB[1:]):
        if r <= b:
            return pa + (pb - pa) * (r - a) / (b - a)
    return _PSI1000_RB[-1][1]


def relaxacao(sig, t_dias, fptk=FPTK):
    """Perda por relaxação pura (MPa) até t: NBR 6118:2023 8.4.8 — ψ(t,t0) = ψ1000·((t − t0)/41,67)^0,15 (t em dias);
    para t → ∞, ψ = 2,5·ψ1000."""
    p = psi1000_rb(sig / fptk) / 100
    psi = 2.5 * p if t_dias is None or t_dias == math.inf else p * (t_dias / 41.67) ** 0.15
    return psi * sig, psi


def eci_j(conc: Concreto, fckj):
    """NBR 6118:2023 8.2.8 — Eci(t) = (fck(t)/fck)^0,5·Eci (C20–C45) ou ^0,3 (C50–C90). kPa."""
    k = 0.5 if conc.fck < 50 else 0.3
    return (min(fckj, conc.fck) / conc.fck) ** k * conc.Eci


def fluencia_retracao(U, h_fic_cm, t0_dias):
    """NBR 6118:2023 Tab. 8.2 (C20–C45) — φ(t∞,t0) e εcs(t∞,t0) (adimensional), interpolação linear em U, 2Ac/u e t0
    (fora da tabela: valor da borda). U em %, h_fic = 2Ac/u em cm, t0 em dias (idade fictícia, Anexo A)."""
    def lin(v, a, b, fa, fb):
        return fa if b == a else fa + (fb - fa) * (v - a) / (b - a)

    def faixa(v, xs):
        v = min(max(v, xs[0]), xs[-1])
        for a, b in zip(xs[:-1], xs[1:]):
            if v <= b:
                return v, a, b
        return v, xs[-2], xs[-1]
    Us, ts = (40, 55, 75, 90), (5, 30, 60)
    u, u0, u1 = faixa(U, Us)
    t, t_0, t_1 = faixa(t0_dias, ts)
    h = min(max(h_fic_cm, 20.0), 60.0)

    def val(uu, tt):
        p20, p60, e20, e60 = _TAB_8_2[(uu, tt)]
        return lin(h, 20, 60, p20, p60), lin(h, 20, 60, e20, e60)
    out = []
    for i in range(2):
        a = [val(uu, tt)[i] for uu in (u0, u1) for tt in (t_0, t_1)]
        v0 = lin(t, t_0, t_1, a[0], a[1])
        v1 = lin(t, t_0, t_1, a[2], a[3])
        out.append(lin(u, u0, u1, v0, v1))
    return out[0], out[1] / 1000


def lbpt_cordoalha(fckj, sig_p, diam_mm=12.7, gradual=True, eta_p2=1.0, gama_c=1.4):
    """Comprimento de transferência da cordoalha de 7 fios (m) — NBR 6118:2023 9.4.5:
    fbpd = ηp1·ηp2·fctd (ηp1 = 1,2 cordoalha de 7 fios; fctd = fctk,inf(fckj)/γc);
    lbp = 7φ/36 · fpyd/fbpd; lbpt = 0,5·lbp·σ/fpyd (liberação gradual) e 0,625·lbp·σ/fpyd (liberação brusca)."""
    fctm_j = 0.3 * fckj ** (2 / 3) if fckj <= 50 else 2.12 * math.log(1 + 0.11 * fckj)
    fbpd = 1.2 * eta_p2 * 0.7 * fctm_j / gama_c
    fpyd = FPYK / 1.15
    lbp = 7 * diam_mm / 1000 / 36 * fpyd / fbpd
    k = 0.5 if gradual else 0.625
    return k * lbp * sig_p / fpyd, lbp, fbpd


def gama_n_consolo(Fg_d, Fq_d, pre_fabricado=False):
    """NBR 9062:2017 7.3.1.1 — coeficiente adicional γn dos consolos e dentes (7.4): elemento pré-moldado (12.1.1)
    1,1 quando a parcela permanente é preponderante e 1,2 nos demais casos (pré-fabricado 12.1.2: 1,0 / 1,1).
    Preponderante: parcela variável de cálculo < 50 % da força total (critério do projeto, DEC-032)."""
    base = 1.0 if pre_fabricado else 1.1
    return base if Fq_d < 0.5 * (Fg_d + Fq_d) else base + 0.1


def perdas_pretracao(sig_pi, Ap, A, I, yc, yp, Mg_t0, conc: Concreto, fckj, u_ar, L_pista=60.0, cravacao=0.006,
                     t_lib_dias=0.8, U=70.0, t0_dias=5.0, Ep=EP / 1000, fases=(), fptk=FPTK):
    """Perdas da pré-tração (MPa; kN·m e m nas entradas de seção). Seção bruta, cordoalhas com resultante em yp.

    Imediatas (antes e na liberação): cravação na pista (Δ = cravação/L_pista·Ep), relaxação até a liberação
    (8.4.8) e encurtamento elástico do concreto com Eci(t) (8.2.8 e 9.6.3.3.1), iterativo, com Mg_t0 (peso próprio).
    Progressivas (9.6.3.4), com φ e εcs da Tab. 8.2 para U, 2Ac/u = 2A/u_ar e t0 (idade fictícia):
      a) 9.6.3.4.2 processo simplificado (fase única): Δσp = [εcs·Ep − αp·σc,p0g·φ − σp0·χ] / [χp + χc·αp·η·ρp],
         χ = −ln(1 − ψ∞), ψ∞ = 2,5 ψ1000, χc = 1 + 0,5φ, χp = 1 + χ, η = 1 + ep²·A/I, ρp = Ap/A, αp = Ep/Eci;
      b) 9.6.3.4.3 processo aproximado (aço RB): Δσp/σp0 (%) = 7,4 + αp/18,7·φ^1,07·(3 + σc,p0g).
    σc,p0g (compressão positiva) com P0 e a carga permanente mobilizada em t0.
    fases: [(ΔM kN·m, t_i dias)] — cargas permanentes aplicadas depois da liberação (montagem, 2º estágio, cobertura).
    Com fases, o termo de fluência de (a) é somado por superposição (fluência linear, 8.2.11): αp·[σc,p0g·φ(∞,t0) −
    Σ Δσc,i·φ(∞,t_i)], Δσc,i = ΔM_i·ep/I (descompressão no nível do cabo) — é o que o processo simplificado faz numa fase
    e o método geral (9.6.3.4.4) faz por etapas; adota-se (a) e (b) fica como referência (supõe toda a carga em t0).
    Sem fases (carga permanente toda em t0): adota-se a MAIOR perda entre (a) e (b)."""
    Ep_k = Ep * 1000                                                  # kPa
    d_crav = cravacao / L_pista * Ep                                 # MPa
    s1 = sig_pi - d_crav
    d_rel0, _ = relaxacao(s1, t_lib_dias, fptk)                      # 8.4.8 até a liberação (fptk: fio CP-175 ou cordoalha CP-190)
    s2 = s1 - d_rel0
    Ecj = eci_j(conc, fckj)
    ap_j = Ep_k / Ecj
    e = yc - yp
    s0 = s2
    for _ in range(40):                                               # 9.6.3.3.1 — encurtamento imediato do concreto
        P = s0 * 1000 * Ap
        scp = (P / A + P * e * e / I - Mg_t0 * e / I) / 1000          # MPa, compressão +
        s0 = s2 - ap_j * scp
    P0 = s0 * 1000 * Ap
    sc = (P0 / A + P0 * e * e / I - Mg_t0 * e / I) / 1000            # σc,p0g (MPa, compressão +)
    h_fic = 2 * A / u_ar * 100
    phi, ecs = fluencia_retracao(U, h_fic, t0_dias)
    ap = Ep_k / conc.Eci
    _, psi_inf = relaxacao(s0, math.inf, fptk)
    chi = -math.log(1 - psi_inf)
    eta = 1 + e * e * A / I
    rho = Ap / A
    fl = sc * phi
    det_f = []
    for dM, ti in fases:                                              # superposição das fases de carga (8.2.11)
        phi_i, _ = fluencia_retracao(U, h_fic, ti)
        dsc = dM * e / I / 1000
        fl -= dsc * phi_i
        det_f.append(dict(dM=dM, t_dias=ti, phi=phi_i, d_sigma_c=dsc))
    d_a = -(ecs * Ep - ap * fl - s0 * chi) / ((1 + chi) + (1 + 0.5 * phi) * ap * eta * rho)          # 9.6.3.4.2
    d_b = (7.4 + ap / 18.7 * phi ** 1.07 * (3 + sc)) / 100 * s0                                       # 9.6.3.4.3 (RB)
    d_prog = d_a if fases else max(d_a, d_b)
    s_inf = s0 - d_prog
    return dict(sig_pi=sig_pi, d_cravacao=d_crav, d_relax_inicial=d_rel0, d_elastica=s2 - s0, sig_p0=s0, P0=P0,
                perda_imediata_pct=(sig_pi - s0) / sig_pi * 100, alfa_p_j=ap_j, Eci_j_MPa=Ecj / 1000,
                U=U, t0_dias=t0_dias, t_lib_dias=t_lib_dias, h_fic_cm=h_fic, phi=phi, eps_cs=ecs, sig_c_p0g=sc, fases=det_f,
                processo="9.6.3.4.2 com fases (superposição)" if fases else "maior entre 9.6.3.4.2 e 9.6.3.4.3",
                d_prog_9_6_3_4_2=d_a, d_prog_9_6_3_4_3=d_b, d_prog=d_prog, sig_pinf=s_inf, Pinf=s_inf * 1000 * Ap,
                perda_progressiva_pct=d_prog / sig_pi * 100, perda_total_pct=(sig_pi - s_inf) / sig_pi * 100)


def tensoes_secao(A, I, yc, h, P, yp, M):
    """σ (MPa) na base e no topo; P (kN) de compressão em yp; M > 0 traciona a base. Compressão negativa."""
    e = yc - yp
    sb = (-P / A - P * e * yc / I + M * yc / I) / 1000
    st = (-P / A + P * e * (h - yc) / I - M * (h - yc) / I) / 1000
    return sb, st


def resultante_tracao(sec: "Secao", sb, st, n=200):
    """Resultante (kN) das tensões de tração no estádio I (distribuição linear entre base sb e topo st, MPa)."""
    h = sec.h
    R = 0.0
    for k in range(n):
        y = (k + 0.5) * h / n
        s = sb + (st - sb) * y / h
        if s > 0:
            R += s * 1000 * sec.largura_em(y) * h / n
    return R


def ato_pretracao(sec: "Secao", sec_ponta: "Secao", x_mac, Lp, grupos, sig_p0, g1, fckj, lt, gama_p=GAMA_P_ATO,
                  dx=0.025, x_fim=None, area=None):
    """Ato da protensão ao longo da peça (pré-tração), NBR 6118:2023 17.2.4.3.2: força γp·P(x) com a transferência
    linear em lt a partir do início da aderência de cada grupo (face da ponta/dente + isolamento) e o peso próprio da
    peça apoiada nas pontas (M = g1·x·(Lp − x)/2). Seção maciça (sec_ponta) até x_mac. Limites: compressão 0,7 fckj e
    tração 1,2 fctm,j (17.2.4.3.2 b); onde há tração, armadura As = R/250 MPa (17.2.4.3.2 c).
    grupos: [dict(n, y, x0)] — n cordoalhas em y (m) aderentes a partir de x0 (m, já com o isolamento);
    area: área de uma cordoalha (m²), padrão Ø12,7 (CORD["12.7"]).
    Varre de dx até x_fim (padrão Lp/2). Retorna os extremos e os pontos de controle."""
    fctm_j = 0.3 * fckj ** (2 / 3)
    lim_c, lim_t = -0.7 * fckj, 1.2 * fctm_j
    x_fim = Lp / 2 if x_fim is None else x_fim
    area = CORD["12.7"] if area is None else area
    pts = []
    x = dx
    while x <= x_fim + 1e-9:
        P = My = 0.0
        for gr in grupos:
            f = min(1.0, max(0.0, (x - gr["x0"]) / lt)) * gr["n"] * area * sig_p0 * 1000
            P += f
            My += f * gr["y"]
        if P > 0:
            s = sec_ponta if x < x_mac else sec
            M = g1 * x * (Lp - x) / 2
            sb, st = tensoes_secao(s.A, s.I, s.yc, s.h, gama_p * P, My / P, M)
            R = resultante_tracao(s, sb, st) if max(sb, st) > 0 else 0.0
            pts.append(dict(x=round(x, 3), P=gama_p * P, base=sb, topo=st, R_tracao=R))
        x += dx
    pior_t = max(pts, key=lambda p: p["topo"])
    pior_c = min(pts, key=lambda p: p["base"])
    pior_R = max(pts, key=lambda p: p["R_tracao"])
    return dict(lim_c=lim_c, lim_t=lim_t, topo_max=pior_t["topo"], x_topo_max=pior_t["x"], base_min=pior_c["base"],
                x_base_min=pior_c["x"], R_tracao_max=pior_R["R_tracao"], x_R_max=pior_R["x"],
                As_topo_cm2=pior_R["R_tracao"] / (SIG_ACO_ATO * 1000) * 1e4, gama_p=gama_p,
                ok=pior_t["topo"] <= lim_t and pior_c["base"] >= lim_c, pontos=pts)


def mrd_camadas(sec: "Secao", fcd, cords=(), barras=(), hogging=False, n=300):
    """Momento resistente por compatibilidade (NBR 6118:2023 17.2.2): εcu 3,5 ‰, bloco 0,85·fcd em 0,8x na seção real.
    cords: [(Ap m², y m, ε de pré-alongamento)] CP-190 bilinear (fpyd até εyd, fptd a 35 ‰);
    barras: [(As m², y m)] CA-50 (fyd). hogging=False: compressão no topo. Retorna (MRd kN·m, x m, x/d)."""
    h = sec.h
    fpyd, fptd = FPYK / 1.15 * 1000, FPTK / 1.15 * 1000
    eyd = fpyd / EP

    def sp(eps):
        if eps <= eyd:
            return max(-fpyd, EP * eps)
        return min(fptd, fpyd + (fptd - fpyd) * (eps - eyd) / (0.035 - eyd))

    def forcas(x):
        yl = 0.8 * x
        C = MC = 0.0
        for k in range(n):
            t = (k + 0.5) * yl / n
            y = h - t if not hogging else t
            f = 0.85 * fcd * sec.largura_em(min(max(y, 1e-6), h - 1e-6)) * yl / n
            C += f
            MC += f * y
        T = MT = 0.0
        for Ap, y, e0 in cords:
            dist = (h - y) if not hogging else y
            s = sp(e0 + 0.0035 * (dist - x) / x) * Ap
            T += s
            MT += s * y
        for As, y in barras:
            dist = (h - y) if not hogging else y
            s = max(-FYD_CA50, min(FYD_CA50, ES * 0.0035 * (dist - x) / x)) * As
            T += s
            MT += s * y
        return C, MC, T, MT
    lo, hi = 1e-4, h
    for _ in range(80):
        x = (lo + hi) / 2
        C, _, T, _ = forcas(x)
        if C > T:
            hi = x
        else:
            lo = x
    C, MC, T, MT = forcas(x)
    yC = MC / C
    yT = MT / T if T else 0.0
    dmax = max(((h - y) if not hogging else y) for _, y, *_ in list(cords) + list(barras))
    return abs(C * (yC - yT)), x, x / dmax


def vc_protendido(conc: Concreto, bw, d, M0, Msd_max):
    """NBR 6118:2023 17.4.2.2 b), modelo I, elemento protendido: Vc = Vc0·(1 + M0/Msd,máx) ≤ 2·Vc0, Vc0 = 0,6·fctd·bw·d."""
    Vc0 = 0.6 * conc.fctk_inf / 1.4 * 1000 * bw * d
    return min(2 * Vc0, Vc0 * (1 + M0 / Msd_max)) if Msd_max > 0 else 2 * Vc0, Vc0


# --------------------------------------------------------------------------- viga pré-tracionada


@dataclass
class Carregamento:
    g1: float  # peso próprio, kN/m
    g2: float  # permanente adicional, kN/m
    q: float  # variável principal, kN/m
    w: float = 0.0  # vento (sucção positiva para cima), kN/m
    psi1: float = 0.4
    psi2: float = 0.3


@dataclass
class ResultadoViga:
    ok: bool
    n_cord: int
    linhas: dict = field(default_factory=dict)
    avisos: list = field(default_factory=list)


def verificar_viga_pretracionada(sec: Secao, L: float, carga: Carregamento, conc: Concreto,
                                 n_cord: int, diam="12.7", y_cord=0.07, fckj=None,
                                 perda_dif=None, caa="II", gama_g=1.3, gama_q=1.4,
                                 isola_pontas=True, n_sup=0, y_sup=0.05, sig_pi=None, gama_p_ato=GAMA_P_ATO,
                                 U=70.0, t0_dias=5.0, t_lib_dias=0.8, L_pista=60.0, t_g2_dias=60.0, nivel="limitada") -> ResultadoViga:
    """Viga biapoiada pré-tracionada, cordoalhas retas na mesa inferior (+ n_sup na mesa superior).

    Verifica: tensões no ato (meio do vão e apoio) com γp = 1,1 (NBR 6118:2023 17.2.4.3.2 a), ELS-F (freq.) e ELS-D
    (q. perm.) para protensão limitada (pré-tração, CAA II), ELU flexão no meio do vão, cortante (VRd2 e Vc do
    elemento protendido, 17.4.2.2 b) e flecha diferida.
    Perdas (DEC-032): imediatas e progressivas pela NBR 6118:2023 9.6.3 (perdas_pretracao), U e t0 (idade fictícia)
    da Tab. 8.2, g2 aplicada em t_g2_dias (fase de carga). perda_dif (fração fixa de σpi) só para reproduzir estudos antigos.
    """
    fckj = fckj or 0.7 * conc.fck
    Ap_inf = n_cord * CORD[diam]
    Ap = (n_cord + n_sup) * CORD[diam]
    sigma_pi = (sig_pi or sigma_pi_max()) * 1000  # kPa — NBR 6118:2023 9.6.1.2.1
    A, I, yc = sec.A, sec.I, sec.yc
    y_cg = (n_cord * y_cord + n_sup * (sec.h - y_sup)) / (n_cord + n_sup)
    ep = yc - y_cg
    Mg1 = carga.g1 * L ** 2 / 8
    Mg2 = carga.g2 * L ** 2 / 8
    Mq = carga.q * L ** 2 / 8
    Mw = carga.w * L ** 2 / 8

    u_ar = sum(math.dist(a, b) for a, b in zip(sec.pts, sec.pts[1:] + sec.pts[:1]))
    pp = perdas_pretracao(sigma_pi / 1000, Ap, A, I, yc, y_cg, Mg1, conc, fckj, u_ar, L_pista=L_pista,
                          t_lib_dias=t_lib_dias, U=U, t0_dias=t0_dias, fases=[(Mg2, t_g2_dias)] if Mg2 > 0 else ())
    sigma_p0 = pp["sig_p0"] * 1000
    P0 = Ap * sigma_p0
    Pinf = Ap * (sigma_p0 - perda_dif * sigma_pi) if perda_dif is not None else pp["Pinf"]
    phi_inf = pp["phi"]

    def tensoes(P, M):
        si = -P / A - P * ep / I * yc + M / I * yc  # fibra inferior (σ<0 compressão)
        ss = -P / A + P * ep / I * (sec.h - yc) - M / I * (sec.h - yc)
        return si / 1000, ss / 1000  # MPa

    out, av = {}, []
    fctmj = 0.3 * fckj ** (2 / 3)
    # ato da protensão — meio do vão e apoio (M=0), γp = 1,1 (NBR 6118:2023 17.2.4.3.2 a)
    si, ss = tensoes(gama_p_ato * P0, Mg1)
    out["ato_meio_inf_MPa"] = round(si, 2)
    out["ato_meio_sup_MPa"] = round(ss, 2)
    si_a, ss_a = tensoes(gama_p_ato * P0, 0)
    out["ato_apoio_inf_MPa"] = round(si_a, 2)
    out["ato_apoio_sup_MPa"] = round(ss_a, 2)
    lim_c = -0.7 * fckj
    lim_t = 1.2 * fctmj
    ok_ato = min(si, si_a) >= lim_c and max(ss, ss_a) <= lim_t
    if not ok_ato and isola_pontas and si >= lim_c and ss <= lim_t:
        # meio do vão passa; pontas resolvidas com isolamento de cordoalhas (NBR 9062 / prática de fábrica)
        av.append("Ato no apoio fora do limite: isolar cordoalhas nas pontas (detalhar comprimentos) "
                  "e/ou armadura passiva no topo")
        ok_ato = True
    out["ato_ok"] = ok_ato

    alfa = 1.3 if sec.largura_em(sec.h * 0.5) < 0.8 * sec.largura_em(0.01) else 1.5
    fct_f = alfa * conc.fctk_inf
    # NBR 6118:2023 Tab. 13.4 — nível de protensão (pré-tração): "limitada" (CAA II): ELS-F frequente, ELS-D quase
    # permanente; "completa" (nível 3): ELS-F na combinação RARA (ψ = 1) e ELS-D na FREQUENTE (ψ1). Descompressão na fibra inferior.
    psi_f, psi_d = (1.0, carga.psi1) if nivel == "completa" else (carga.psi1, carga.psi2)
    si_f, ss_f = tensoes(Pinf, Mg1 + Mg2 + psi_f * Mq)
    si_d, _ = tensoes(Pinf, Mg1 + Mg2 + psi_d * Mq)
    out["nivel_protensao"] = nivel
    out["psi_F"], out["psi_D"] = psi_f, psi_d
    out["elsf_inf_MPa"] = round(si_f, 2)
    out["elsd_inf_MPa"] = round(si_d, 2)
    out["elsf_lim_MPa"] = round(fct_f, 2)
    ok_els = si_f <= fct_f and si_d <= 0.0 and ss_f >= -0.6 * conc.fck
    # vento de sucção (G + W freq.) — topo não pode fissurar
    _, ss_w = tensoes(Pinf, Mg1 + Mg2 - 0.3 * Mw)
    out["vento_sup_MPa"] = round(ss_w, 2)
    ok_els = ok_els and ss_w <= fct_f
    out["els_ok"] = ok_els

    # ELU flexão — compatibilidade de deformações (NBR 6118 17.2.2): bloco 0,8x sobre a seção real,
    # cordoalha com pré-alongamento εpn e diagrama bilinear CP-190 (fpyd até εyd, fptd em 35‰)
    Md = gama_g * (Mg1 + Mg2) + gama_q * Mq
    fpyd, fptd = 1710 / 1.15 * 1000, 1900 / 1.15 * 1000
    eyd = fpyd / EP
    dp = sec.h - y_cord
    epn = (Pinf / Ap) / EP

    def sigma_p(ep_):
        if ep_ <= eyd:
            return ep_ * EP
        return min(fptd, fpyd + (ep_ - eyd) / (0.035 - eyd) * (fptd - fpyd))

    def Fc(x):
        y, n, F = min(0.8 * x, sec.h), 40, 0.0
        for k in range(n):
            yy = sec.h - (k + 0.5) * y / n
            F += 0.85 * conc.fcd * sec.largura_em(yy) * y / n
        return F

    def zc(x):
        y, n, F, Mz = min(0.8 * x, sec.h), 40, 0.0, 0.0
        for k in range(n):
            dy = (k + 0.5) * y / n
            f = sec.largura_em(sec.h - dy) * y / n
            F += f
            Mz += f * dy
        return Mz / F

    lo, hi = 1e-4, dp
    for _ in range(60):
        x = (lo + hi) / 2
        ep_ = epn + 0.0035 * (dp - x) / x
        if Fc(x) > Ap_inf * sigma_p(ep_):
            hi = x
        else:
            lo = x
    ep_u = epn + 0.0035 * (dp - x) / x
    sp = sigma_p(ep_u)
    MRd = Ap_inf * sp * (dp - zc(x))
    out["Md_kNm"] = round(Md, 1)
    out["MRd_kNm"] = round(MRd, 1)
    out["x_d"] = round(x / dp, 3)
    out["sigma_pd_MPa"] = round(sp / 1000)
    ok_elu = MRd >= Md and x / dp <= 0.45
    # ELU sucção: 1,0G + 1,4W com protensão — topo não pode esmagar/romper (checagem de tensão)
    Mdw = (Mg1 + Mg2) - 1.4 * Mw
    out["Md_succao_kNm"] = round(Mdw, 1)

    # cortante — biela (VRd2, modelo I) na alma
    Vd = (gama_g * (carga.g1 + carga.g2) + gama_q * carga.q) * L / 2
    bw = sec.largura_em(sec.h / 2)
    av2 = 1 - conc.fck / 250
    VRd2 = 0.27 * av2 * conc.fcd * bw * 0.9 * dp
    out["Vd_kN"] = round(Vd, 1)
    out["VRd2_kN"] = round(VRd2, 1)
    # NBR 6118:2023 17.4.2.2 b): Vc = Vc0·(1 + M0/Msd,máx) ≤ 2·Vc0, M0 com γp = 0,9 na borda inferior
    M0 = 0.9 * Pinf * (sec.Wi / A + ep)
    Vc, _ = vc_protendido(conc, bw, dp, M0, Md)
    asw = max(0.0, (Vd - Vc) / (0.9 * dp * FYD_CA50)) * 1e4  # cm²/m
    asw_min = 0.2 * conc.fctm / 500 * bw * 1e4
    out["Asw_cm2_m"] = round(max(asw, asw_min), 2)
    ok_v = Vd <= VRd2

    # flecha (estádio I, Ecs): imediata + fluência φ(t∞,t0) da Tab. 8.2 (mesma das perdas), contraflecha da protensão
    EI = conc.Ecs * I
    fg = 5 * (carga.g1 + carga.g2) * L ** 4 / (384 * EI)
    fq = 5 * carga.psi2 * carga.q * L ** 4 / (384 * EI)
    fp = -Pinf * ep * L ** 2 / (8 * EI)
    f_inf = (fg + fp) * (1 + phi_inf) + fq
    out["flecha_final_mm"] = round(f_inf * 1000, 1)
    out["flecha_lim_mm"] = round(L / 250 * 1000, 1)
    ok_f = abs(f_inf) <= L / 250

    out["P0_kN"] = round(P0, 1)
    out["Pinf_kN"] = round(Pinf, 1)
    out["perda_imediata_%"] = round((1 - sigma_p0 / sigma_pi) * 100, 1)
    out["perda_total_%"] = round((1 - Pinf / (Ap * sigma_pi)) * 100, 1)
    out["sigma_p0_MPa"] = round(sigma_p0 / 1000, 1)
    out["sigma_pinf_MPa"] = round(Pinf / Ap / 1000, 1)
    out["phi"] = round(phi_inf, 2)
    out["eps_cs"] = pp["eps_cs"]
    out["gama_p_ato"] = gama_p_ato
    out["perdas"] = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in pp.items()}
    out["A_m2"] = round(A, 4)
    out["peso_kN_m"] = round(A * 25, 2)
    ok = ok_ato and ok_els and ok_elu and ok_v and ok_f
    for k, v in [("ato", ok_ato), ("ELS", ok_els), ("ELU flexão", ok_elu), ("cortante", ok_v), ("flecha", ok_f)]:
        if not v:
            av.append(f"Não passa: {k}")
    out["n_cord_sup"] = n_sup
    return ResultadoViga(ok, n_cord, out, av)


def menor_protensao(sec, L, carga, conc, diam="12.7", nmax=24, **kw):
    """Menor número de cordoalhas (par, simétrico) que passa em tudo; None se nenhum."""
    for n_sup in (0, 2, 4):
        for n in range(2, nmax + 1, 2):
            r = verificar_viga_pretracionada(sec, L, carga, conc, n, diam, n_sup=n_sup, **kw)
            if r.ok:
                return r
    return None


# --------------------------------------------------------------------------- torção (NBR 6118 17.5)


def torcao_retangular(b, h, Td, Vd, conc: Concreto, c1=0.045, theta=45.0):
    """Modelo de treliça espacial, seção vazada equivalente. Retorna verificação de bielas e armaduras."""
    A, u = b * h, 2 * (b + h)
    he = max(2 * c1, min(A / u, b - 2 * c1))
    Ae = (b - he) * (h - he)
    ue = 2 * ((b - he) + (h - he))
    av2 = 1 - conc.fck / 250
    th = math.radians(theta)
    TRd2 = 0.5 * av2 * conc.fcd * Ae * he * math.sin(2 * th)
    d = h - c1 - 0.01
    VRd2 = 0.27 * av2 * conc.fcd * b * d
    inter = Vd / VRd2 + Td / TRd2
    a90 = Td / (2 * Ae * FYD_CA50) * math.tan(th) * 1e4  # cm²/m por ramo
    asl = Td / (2 * Ae * FYD_CA50) / math.tan(th) * ue * 1e4  # cm² total
    return dict(TRd2_kNm=round(TRd2, 1), VRd2_kN=round(VRd2, 1), interacao=round(inter, 3),
                ok=inter <= 1.0, Asw_torcao_cm2_m_ramo=round(a90, 2), Asl_torcao_cm2=round(asl, 2),
                he_m=round(he, 3))


# --------------------------------------------------------------------------- pilar em balanço


def flexao_composta_retangular(b, h, Nd, Md, conc: Concreto, c=0.045):
    """Armadura simétrica As=As' (cada face) para N (compressão +) e M, por equilíbrio
    com bloco retangular. Retorna As por face em cm² (busca numérica, ε pelo domínio)."""
    d, d2 = h - c, c
    fc = 0.85 * conc.fcd
    best = None
    for i in range(1, 2000):
        x = h * 1.2 * i / 2000
        y = min(0.8 * x, h)
        Fc = fc * b * y
        # deformações (domínios 2–5 simplificado)
        eps_cu = 0.0035
        es = eps_cu * (d - x) / x  # tração na armadura inferior (positivo)
        es2 = eps_cu * (x - d2) / x  # compressão na superior
        fs = min(abs(es) * ES, FYD_CA50) * (1 if es >= 0 else -1)
        fs2 = min(abs(es2) * ES, FYD_CA50) * (1 if es2 >= 0 else -1)
        den = fs2 - fs
        if abs(den) < 1:
            continue
        As = (Nd - Fc) / den  # equilíbrio de forças
        if As < 0:
            As = 0.0
        M = Fc * (h / 2 - y / 2) + As * fs2 * (h / 2 - d2) + As * fs * (d - h / 2)
        if M >= Md and (best is None or As < best):
            best = As
    return None if best is None else best * 1e4


def pilar_balanco(b, h, L, Nk, Hk_dist, conc: Concreto, Hk_top=0.0, Mk_perm=0.0, gama=1.4,
                  gama_g=1.3, phi=2.0, Nk_perm=None):
    """Pilar engastado no cálice, livre no topo; esforços na direção da dimensão h.

    Hk_dist: vento distribuído (kN/m); Hk_top: força no topo (kN); Mk_perm: momento permanente
    na base (ex.: excentricidade das placas). le = 2L.
    1ª ordem + fluência (NBR 6118:2023 15.8.4, e_cc) + 2ª ordem pelo pilar-padrão com rigidez κ
    (15.8.3.3.3). Para λ > 90 o item pede pilar-padrão com M-N-1/r e para λ > 140 o método geral:
    aqui o resultado é de pré-dimensionamento e deve ser confirmado por análise não linear.
    """
    le = 2 * L
    i = h / math.sqrt(12)
    lam = le / i
    Nk_perm = Nk if Nk_perm is None else Nk_perm
    Nd = gama_g * Nk
    M1 = gama * (Hk_dist * L ** 2 / 2 + Hk_top * L) + gama_g * Mk_perm
    M1min = Nd * (0.015 + 0.03 * h)  # NBR 6118 11.3.3.4.3
    M1d = max(M1, M1min)
    nu = Nd / (b * h * conc.fcd)
    # fluência (15.8.4): e_cc com Msg = Mk_perm e ea = θ1·le/2 (θ1 = 1/(100√L) ≥ 1/300)
    Ic = b * h ** 3 / 12
    Ne = 10 * conc.Eci * Ic / le ** 2
    theta1 = max(1 / 300, min(1 / 200, 1 / (100 * math.sqrt(L))))
    ea = theta1 * le / 2
    ecc = 0.0
    if lam > 90 and Nk_perm < Ne:
        ecc = (Mk_perm / max(Nk_perm, 1e-6) + ea) * (math.exp(phi * Nk_perm / (Ne - Nk_perm)) - 1)
    M1d_c = M1d + Nd * ecc
    Mtot = M1d_c
    instavel = False
    for _ in range(100):
        kappa = 32 * (1 + 5 * Mtot / (h * Nd)) * nu
        den = 1 - lam ** 2 / (120 * kappa / nu)
        if den <= 0.05:
            instavel = True
            break
        Mn = M1d_c / den
        if abs(Mn - Mtot) < 0.01:
            Mtot = Mn
            break
        Mtot = Mn
    As = None if instavel else flexao_composta_retangular(b, h, Nd, Mtot, conc)
    As_min = max(0.15 * Nd / FYD_CA50, 0.004 * b * h) * 1e4 / 2  # NBR 6118 17.3.5.3.1
    As_face = None if As is None else max(As, As_min)
    taxa = None if As_face is None else 2 * As_face / (b * h * 1e4)
    ok = As_face is not None and lam <= 200 and taxa <= 0.04
    av = []
    if lam > 140:
        av.append("λ > 140: confirmar pelo método geral (não linear física e geométrica com fluência)")
    elif lam > 90:
        av.append("90 < λ ≤ 140: confirmar com pilar-padrão acoplado a M-N-1/r ou análise não linear")
    if instavel:
        av.append("Instável pelo pilar-padrão")
    return dict(lambda_=round(lam, 1), Nd_kN=round(Nd, 1), M1d_kNm=round(M1d, 1), ecc_m=round(ecc, 4),
                Mtot_kNm=round(Mtot, 1), As_face_cm2=None if As_face is None else round(As_face, 1),
                taxa_total_pct=None if taxa is None else round(taxa * 100, 2), ok=ok, avisos=av)


# --------------------------------------------------------------------------- vento (pré-dimensionamento)


def pressao_vento(V0, z=10.0, b=0.93, Fr=0.95, p=0.115, S1=1.0, S3=1.0):
    """q (kN/m²) — NBR 6123 cat. III classe C por padrão (conferir parâmetros da revisão 2023)."""
    S2 = b * Fr * (z / 10) ** p
    Vk = V0 * S1 * S2 * S3
    return 0.613 * Vk ** 2 / 1000


# --------------------------------------------------------------------------- método geral (OpenSeesPy)


def pilar_metodo_geral(b, h, L, As_face, Nd, Hd_dist, conc: Concreto, Md_base=0.0, Hd_top=0.0,
                       phi_ef=1.0, c=0.045, n_el=10, ea_rad=None, cord=(), sig_pinf=0.0, camadas=None):
    """Pilar em balanço — não linearidade física (fibras, concreto 0,85fcd/γ e CA-50 de cálculo)
    e geométrica (corrotacional), fluência pelo alongamento do diagrama do concreto (1+φef),
    imperfeição global θ1 (NBR 6118 11.3.3.4.1). Carrega N fixo e cresce H/M até λ.
    Retorna o fator de carga último λu (passa se ≥ 1,0) e o deslocamento do topo em λ=1.
    cord: cordoalhas Ø12,7 pré-tracionadas [(y a partir do eixo, n), ...] com tensão após perdas sig_pinf (MPa):
    entram como fibras CP-190 com deformação inicial (pilar protendido centrado ou não).
    camadas: [(y a partir do eixo, m; n barras; área de cada barra, cm²), ...] — arranjo real das barras na direção de h
    (faces e barras laterais); quando dado, substitui As_face.
    """
    import openseespy.opensees as ops
    ops.wipe()
    ops.logFile("/dev/null", "-noEcho")
    ops.model("basic", "-ndm", 2, "-ndf", 3)
    if cord:
        ops.uniaxialMaterial("Steel01", 3, 0.9 * 1900 / 1.15 * 1e3, EP, 0.001)
        ops.uniaxialMaterial("InitStrainMaterial", 4, 3, sig_pinf / (EP / 1e3))
    for i in range(n_el + 1):
        ops.node(i + 1, 0.0, L * i / n_el)
    ops.fix(1, 1, 1, 1)
    fc = 0.85 * conc.fcd
    e0 = -0.002 * (1 + phi_ef)
    eu = -0.0035 * (1 + phi_ef)
    ops.uniaxialMaterial("Concrete01", 1, -fc, e0, -fc, eu)
    ops.uniaxialMaterial("Steel01", 2, FYD_CA50, ES, 0.001)
    ops.section("Fiber", 1)
    ops.patch("rect", 1, 20, 4, -h / 2, -b / 2, h / 2, b / 2)
    if camadas:
        for y, n, a1 in camadas:
            if n == 1:
                ops.fiber(y, 0.0, a1 * 1e-4, 2)
            else:
                ops.layer("straight", 2, n, a1 * 1e-4, y, -b / 2 + c, y, b / 2 - c)
    else:
        As = As_face * 1e-4
        nb = 4
        for y in (-h / 2 + c, h / 2 - c):
            ops.layer("straight", 2, nb, As / nb, y, -b / 2 + c, y, b / 2 - c)
    for y, n in cord:
        ops.layer("straight", 4, n, CORD["12.7"], y, -b / 2 + 0.05, y, b / 2 - 0.05)
    ops.geomTransf("Corotational", 1)
    ops.beamIntegration("Lobatto", 1, 1, 5)
    for i in range(n_el):
        ops.element("forceBeamColumn", i + 1, i + 1, i + 2, 1, 1)
    theta = ea_rad if ea_rad is not None else max(1 / 300, min(1 / 200, 1 / (100 * math.sqrt(L))))
    # N fixo (com imperfeição como força horizontal equivalente θ·N no topo)
    ops.timeSeries("Constant", 1)
    ops.pattern("Plain", 1, 1)
    ops.load(n_el + 1, theta * Nd, -Nd, 0.0)
    ops.system("BandGeneral"); ops.numberer("RCM"); ops.constraints("Plain")
    ops.test("NormDispIncr", 1e-8, 50); ops.algorithm("Newton")
    ops.integrator("LoadControl", 0.1); ops.analysis("Static")
    if cord:                                           # equilíbrio da protensão antes das cargas
        ops.integrator("LoadControl", 0.0)
        ops.analyze(3)
        ops.integrator("LoadControl", 0.1)
    if ops.analyze(10) != 0 or ops.nodeDisp(n_el + 1, 1) < 0:
        ops.wipe()
        return dict(lambda_u=0.0, ok=False, topo_mm=None, motivo="instável só com a força normal")
    ops.loadConst("-time", 0.0)
    ops.timeSeries("Linear", 2)
    ops.pattern("Plain", 2, 2)
    for i in range(1, n_el + 1):
        w = Hd_dist * L / n_el * (0.5 if i == n_el else 1.0)
        ops.load(i + 1, w, 0.0, 0.0)
    ops.load(n_el + 1, Hd_top, 0.0, 0.0)
    if Md_base:
        # momento permanente aplicado como binário distribuído (placas): M por nível
        for i in range(1, n_el + 1):
            ops.load(i + 1, 0.0, 0.0, -Md_base / n_el)  # Md_base > 0 no mesmo sentido do vento +x
    def rompeu():
        # ELU por deformação (NBR 6118 17.2.2): concreto εcu (alongado pela fluência) ou aço 10‰
        for e in range(1, n_el + 1):
            for ip in range(1, 6):
                d = ops.eleResponse(e, "section", ip, "deformation")
                if not d:
                    continue
                eps, kap = d[0], d[1]
                ec = min(eps - kap * h / 2, eps + kap * h / 2)
                es = max(eps - kap * (h / 2 - c), eps + kap * (h / 2 - c))
                if ec < eu or es > 0.010:
                    return True
        return False

    lam, step, topo1 = 0.0, 0.02, None
    ops.integrator("LoadControl", step)
    while lam < 3.0:
        if ops.analyze(1) != 0:
            ok = False
            for s_ in (step / 4, step / 16):
                ops.integrator("LoadControl", s_)
                if ops.analyze(1) == 0:
                    ok = True
                    lam += s_
                    break
            if not ok:
                break
            ops.integrator("LoadControl", step)
        else:
            lam += step
        if rompeu() or ops.nodeDisp(n_el + 1, 1) < 0:  # deformação última ou perda de estabilidade
            lam -= step
            break
        if topo1 is None and lam >= 1.0:
            topo1 = ops.nodeDisp(n_el + 1, 1) * 1000
    ops.wipe()
    return dict(lambda_u=round(lam, 2), ok=lam >= 1.0, topo_mm=None if topo1 is None else round(topo1, 1))


def armadura_minima_metodo_geral(b, h, L, Nd, Hd_dist, conc, Md_base=0.0, Hd_top=0.0, phi_ef=1.0,
                                 bitolas=(10.0, 12.5, 16.0, 20.0, 25.0, 32.0)):
    """Menor armadura por face (4 barras por face) que dá λu ≥ 1,0. Retorna dict ou None."""
    for d in bitolas:
        for nb in (2, 3, 4, 5, 6):
            As = nb * math.pi * (d / 1000) ** 2 / 4 * 1e4
            if not 0.004 <= 2 * As / (b * h * 1e4) <= 0.04:  # NBR 6118 17.3.5.3 (4% fora das emendas)
                continue
            r = pilar_metodo_geral(b, h, L, As, Nd, Hd_dist, conc, Md_base, Hd_top, phi_ef)
            if r["ok"]:
                r.update(barras_face=f"{nb} Ø{d:g}", As_face_cm2=round(As, 2),
                         taxa_pct=round(2 * As / (b * h * 1e4) * 100, 2))
                return r
    return None


# --------------------------------------------------------------------------- grade da cabeceira (pista ND/Marque)

# Cabeçote ativo inferior REV05: 7 colunas × 5 linhas, passo 50 (horiz.) × 42 (vert.), furos Ø17.
# Cabeçote superior: 7 × 2. Cotas a partir do fundo da fôrma (piso acabado + 300).
# A linha mais baixa fica a Y0_INF do fundo da fôrma (nota 11 da ASM.001: eixo inferior a 375 do piso
# com fundo da fôrma a 300 → 75 mm; conferir com Nathan se 375 é a linha de baixo ou o eixo do grupo).
GRADE_X = [-0.150, -0.100, -0.050, 0.0, 0.050, 0.100, 0.150]
Y0_INF, PASSO_V, N_LIN_INF = 0.075, 0.042, 5
Y_SUP = [1.050, 1.050 + PASSO_V]  # linhas do cabeçote superior, do fundo da fôrma
_ORDEM = [0.0, -0.150, 0.150, -0.100, 0.100, -0.050, 0.050]  # preenchimento simétrico


def posicoes_grade(sec: "Secao", n: int, cobrimento=0.040, diam=0.0127):
    """Distribui n cordoalhas nos furos do cabeçote inferior, de baixo para cima, simétricas.
    Só usa furos com cobrimento ≥ `cobrimento` às faces laterais na cota do furo.
    Retorna lista de (x, y) ou None se não couber."""
    pos = []
    for k in range(N_LIN_INF):
        y = Y0_INF + k * PASSO_V
        if y > sec.h - 0.05:
            break
        meia = sec.largura_em(y) / 2 - cobrimento - diam / 2
        livres = [x for x in _ORDEM if abs(x) <= meia + 1e-9]
        falta = n - len(pos)
        if falta <= 0:
            break
        usar = livres[:falta]
        if len(usar) % 2 == 0 and 0.0 in usar and falta < len(livres):
            pass
        # mantém simetria: se sobrar número par sem o central, tira o central
        if (falta % 2 == 0) and 0.0 in usar and len(usar) == falta:
            usar = [x for x in livres if x != 0.0][:falta]
        pos += [(x, y) for x in usar]
    return pos if len(pos) == n else None


def menor_protensao_grade(sec, L, carga, conc, nmax=35, sup_permitidas=(0, 2), **kw):
    """Menor número de cordoalhas Ø12,7 na grade da cabeceira que passa em todas as verificações.
    Cordoalhas superiores (se usadas) no cabeçote superior, colunas centrais, só se couberem na seção."""
    for n_sup in sup_permitidas:
        if n_sup:
            y_s = max((y for y in Y_SUP if y <= sec.h - 0.045), default=None)
            if y_s is None:
                continue
            y_sup = sec.h - y_s
        else:
            y_sup = 0.05
        for n in range(2, nmax + 1):
            pos = posicoes_grade(sec, n)
            if pos is None:
                continue
            y_cg = sum(y for _, y in pos) / n
            r = verificar_viga_pretracionada(sec, L, carga, conc, n, "12.7", y_cord=y_cg,
                                             n_sup=n_sup, y_sup=y_sup, **kw)
            if r.ok:
                r.linhas["posicoes"] = [(round(x * 1000), round(y * 1000)) for x, y in pos]
                r.linhas["y_cg_mm"] = round(y_cg * 1000)
                return r
    return None


# --------------------------------------------------------------------------- situações transitórias (NBR 9062)


def iy_secao(sec: "Secao"):
    """Momento de inércia em torno do eixo vertical (flexão lateral), por faixas."""
    n, h = 400, sec.h
    Iy = 0.0
    for k in range(n):
        y = (k + 0.5) * h / n
        b = sec.largura_em(y)
        Iy += b ** 3 / 12 * h / n
    return Iy


def icamento_viga(sec: "Secao", L: float, a: float, P: float, ep: float, conc: "Concreto",
                  fckj: float, coef_din=1.3, y_alca=0.10, e_tol=0.006, sweep=None):
    """Viga suspensa por 2 alças a 'a' das pontas (içamento, estocagem e transporte em 2 apoios).

    Tensões (MPa, σ<0 compressão) nas fibras sup./inf. no meio e na alça com protensão P (kN) e
    excentricidade ep (m); peso × coef. dinâmico (NBR 9062: 1,3 — conferir).
    Estabilidade lateral (Mast 1989/1993, PCI): FS à fissuração ≥ 1,0 e FS à ruptura ≥ 1,5.
    """
    w = sec.A * 25.0
    wd = w * coef_din
    Mm = wd * L ** 2 / 8 - wd * a * L / 2          # meio do vão (com balanços)
    Ma = -wd * a ** 2 / 2                           # no ponto da alça
    A, I, yc, h = sec.A, sec.I, sec.yc, sec.h

    def sig(M):
        si = (-P / A - P * ep * yc / I + M * yc / I) / 1000
        ss = (-P / A + P * ep * (h - yc) / I - M * (h - yc) / I) / 1000
        return round(ss, 2), round(si, 2)

    fctm_j = 0.3 * fckj ** (2 / 3)
    lim_c, lim_t = -0.7 * fckj, 1.2 * fctm_j
    s_meio, s_alca = sig(Mm), sig(Ma)
    ok_tens = all(lim_c <= v <= lim_t for v in s_meio + s_alca)
    # Mast: deslocamento lateral do CG com rotação unitária (z0), roll axis acima do CG
    Ecj = conc.Ecs * math.sqrt(fckj / conc.fck)
    Iy = iy_secao(sec)
    L1 = L - 2 * a
    z0 = w / (12 * Ecj * Iy * L) * (L1 ** 5 / 10 - a ** 2 * L1 ** 3 + 3 * a ** 4 * L1 + 6 / 5 * a ** 5)
    yr = (h - yc) + y_alca
    sweep = sweep if sweep is not None else L / 1000
    ei = e_tol + sweep * (L1 / L) ** 2 / 1.0
    theta_i = ei / yr
    M_g = w * L ** 2 / 8 - w * a * L / 2           # momento vertical sem impacto (meio)
    b_top = sec.largura_em(h - 0.01)
    fr = 0.7 * fctm_j * 1000                       # kPa
    sig_top = (-P / A + P * ep * (h - yc) / I - M_g * (h - yc) / I)   # kPa (compressão < 0)
    M_lat = (fr - sig_top) * Iy / (b_top / 2)      # momento lateral que fissura o canto da mesa sup.
    theta_max = M_lat / M_g if M_g > 0 else 1.0
    FS_c = 1 / (z0 / yr + theta_i / theta_max)
    theta_u = 0.4                                  # rad, valor usual PCI para a rotação última (conferir)
    z0u = z0 * 2.5                                 # rigidez lateral reduzida na ruptura (Mast, aprox.)
    zmax = z0u * theta_u + ei
    FS_u = yr * theta_u / zmax
    return dict(a_m=a, Mmeio_d=round(Mm, 1), Malca_d=round(Ma, 1),
                tens_meio_sup_inf=s_meio, tens_alca_sup_inf=s_alca, lim_c=round(lim_c, 1), lim_t=round(lim_t, 2),
                ok_tensoes=ok_tens, z0_mm=round(z0 * 1000, 1), ei_mm=round(ei * 1000, 1),
                FS_fissuracao=round(FS_c, 2), FS_ruptura=round(FS_u, 2),
                ok_estabilidade=FS_c >= 1.0 and FS_u >= 1.5,
                peso_kN=round(w * L, 1), carga_alca_d_kN=round(wd * L / 2, 1))


def momentos_apoios(L, w, xs, reacoes=None, n=801):
    """Diagrama de momentos de viga com peso w (kN/m) em apoios/alças nas posições xs.
    reacoes=None: reações iguais (balancim que equaliza as alças); senão, lista de reações (kN)."""
    R = reacoes or [w * L / len(xs)] * len(xs)
    pts = []
    for i in range(n):
        x = L * i / (n - 1)
        M = -w * x * x / 2 + sum(r * (x - xa) for r, xa in zip(R, xs) if xa <= x)
        pts.append((x, M))
    return pts


def transitorias_viga(sec, L, P, ep, conc, fckj, xs_icamento, xs_estoque, coef_din=1.3):
    """Desforma/montagem (alças com balancim, reações iguais) e estoque/transporte (2 calços).
    Retorna tensões extremas (MPa) no topo e no fundo e o atendimento aos limites no ato."""
    A, I, yc, h = sec.A, sec.I, sec.yc, sec.h
    lim_c, lim_t = -0.7 * fckj, 1.2 * 0.3 * fckj ** (2 / 3)
    out = {}
    for nome, xs, din in (("desforma_montagem", xs_icamento, coef_din), ("estoque_transporte", xs_estoque, coef_din)):
        w = sec.A * 25 * din
        if len(xs) == 2:
            a, b = xs
            Rb = w * L * (L / 2 - a) / (b - a); Ra = w * L - Rb
            dia = momentos_apoios(L, w, xs, [Ra, Rb])
        else:
            dia = momentos_apoios(L, w, xs)
        Mmax = max(m for _, m in dia); Mmin = min(m for _, m in dia)
        res = []
        for M in (Mmax, Mmin):
            si = (-P / A - P * ep * yc / I + M * yc / I) / 1000
            ss = (-P / A + P * ep * (h - yc) / I - M * (h - yc) / I) / 1000
            res.append((round(ss, 2), round(si, 2)))
        ok = all(lim_c <= v <= lim_t for par in res for v in par)
        out[nome] = dict(pontos_m=[round(x, 3) for x in xs], Mpos=round(Mmax, 1), Mneg=round(Mmin, 1),
                         tens_sup_inf_Mpos=res[0], tens_sup_inf_Mneg=res[1], ok=ok,
                         carga_por_ponto_kN=round(w * L / len(xs), 1))
    out["limites_MPa"] = (round(lim_c, 1), round(lim_t, 2))
    return out
