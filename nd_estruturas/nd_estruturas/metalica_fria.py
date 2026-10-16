"""Perfis formados a frio (NBR 14762:2010) — Ue/U, método da resistência direta (Anexo C) com faixas finitas.

Unidades: N, mm, MPa (convertidas para kN e kN·m na saída quando indicado).
Eixo x = eixo de simetria do Ue (horizontal, a meia altura da alma); flexão em torno de x é a flexão principal.
As forças críticas de flambagem local e distorcional saem da curva de assinatura (faixas finitas, apoios S-S);
a global (FLT e flexo-torção) sai das expressões analíticas da NBR 14762 (item 9.7.2 e 9.8.2.2).
"""
from __future__ import annotations
import inspect, math, types
import numpy as np

E_ACO, NU, G_ACO = 200_000.0, 0.3, 77_000.0
GAMA = dict(flexao=1.10, compressao=1.20, cortante=1.10, tracao_esc=1.10)   # NBR 14762:2010 Tabela 2 (γ)
ACOS = {"ZAR345": (345.0, 430.0), "USI-SAC300": (300.0, 400.0), "A1011-SS33": (230.0, 360.0), "A36": (250.0, 400.0)}


# ------------------------------------------------------------------ faixas finitas (núcleo aberto, correção p/ numpy 2)
def _modulo_fsm():
    import pycufsm.fsm as F
    import pycufsm.solve.analysis_p as AP
    src = inspect.getsource(AP).replace("int((np.argwhere(props[:, 0] == mat_num)).reshape(1))",
                                        "int(np.argwhere(props[:, 0] == mat_num).reshape(-1)[0])")
    mod = types.ModuleType("_fsm_analysis")
    exec(compile(src, "_fsm_analysis", "exec"), mod.__dict__)
    F.analysis = mod
    return F


# ------------------------------------------------------------------ propriedades de parede fina (linha média)
def props_parede_fina(pts, t):
    """Seção aberta, cadeia de pontos na linha média. Retorna A, xc, yc, Ix, Iy, x0 (CT − CG, em x), y0, J, Cw."""
    P = np.array(pts, float)
    segs = list(zip(P[:-1], P[1:]))
    L = np.array([np.linalg.norm(q - p) for p, q in segs])
    A = t * L.sum()
    xc = sum(t * l * (p[0] + q[0]) / 2 for (p, q), l in zip(segs, L)) / A
    yc = sum(t * l * (p[1] + q[1]) / 2 for (p, q), l in zip(segs, L)) / A
    Ix = Iy = Ixy = 0.0
    for (p, q), l in zip(segs, L):
        x1, y1, x2, y2 = p[0] - xc, p[1] - yc, q[0] - xc, q[1] - yc
        Ix += t * l * (y1 * y1 + y1 * y2 + y2 * y2) / 3
        Iy += t * l * (x1 * x1 + x1 * x2 + x2 * x2) / 3
        Ixy += t * l * (2 * x1 * y1 + x1 * y2 + x2 * y1 + 2 * x2 * y2) / 6
    w = [0.0]
    for p, q in segs:
        w.append(w[-1] + ((p[0] - xc) * (q[1] - yc) - (q[0] - xc) * (p[1] - yc)))
    w = np.array(w)

    def integ(a, b):
        return sum(t * l * (2 * a[i] * b[i] + a[i] * b[i + 1] + a[i + 1] * b[i] + 2 * a[i + 1] * b[i + 1]) / 6
                   for i, l in enumerate(L))
    X, Y = P[:, 0] - xc, P[:, 1] - yc
    Iwx, Iwy = integ(w, X), integ(w, Y)
    D = Ix * Iy - Ixy ** 2
    x0 = (Iwy * Iy - Iwx * Ixy) / D
    y0 = -(Iwx * Ix - Iwy * Ixy) / D
    wS = w - (x0 * Y - y0 * X)
    wS = wS - integ(wS, np.ones_like(wS)) / A
    return dict(A=A, xc=xc, yc=yc, Ix=Ix, Iy=Iy, Ixy=Ixy, x0=x0, y0=y0, J=L.sum() * t ** 3 / 3, Cw=integ(wS, wS))


class PerfilUe:
    """Ue bw×bf×D×t (dimensões externas, mm), cantos vivos na linha média."""

    def __init__(self, bw, bf, D, t, aco="ZAR345"):
        self.bw, self.bf, self.D, self.t, self.aco = bw, bf, D, t, aco
        self.fy, self.fu = ACOS[aco]
        h, b, d = bw - t, bf - t, D - t / 2
        self.pts = [(b, h - d), (b, h), (0, h), (0, 0), (b, 0), (b, d)]
        self.p = props_parede_fina(self.pts, t)
        self.h_lm = h
        self.W = self.p["Ix"] / (h / 2 + t / 2)                 # módulo elástico à face externa
        self.peso_kNm = self.p["A"] * 7850e-9 * 9.81
        self.m_ct = -(self.p["x0"] + self.p["xc"])              # distância do CT à linha média da alma (lado oposto às mesas)

    @property
    def nome(self):
        return f"Ue {self.bw:g}×{self.bf:g}×{self.D:g}×{self.t:.2f}".replace(".", ",")

    # -------------------------------------------------- curva de assinatura
    def assinatura(self, carga="M", Ls=None, n_div=(4, 8, 20, 8, 4)):
        F = _modulo_fsm()
        P = [np.array(v, float) for v in self.pts]
        nodes = []
        for i in range(5):
            for k in range(n_div[i]):
                nodes.append(P[i] + (P[i + 1] - P[i]) * k / n_div[i])
        nodes.append(P[5])
        yc = self.p["yc"]
        if carga == "M":       # compressão na mesa superior, σ = fy na face externa
            st = [self.fy * (y - yc) / (self.h_lm / 2 + self.t / 2) for _, y in nodes]
        else:
            st = [self.fy] * len(nodes)
        N = np.array([[i, x, y, 1, 1, 1, 1, s] for i, ((x, y), s) in enumerate(zip(nodes, st))], float)
        El = np.array([[i, i, i + 1, self.t, 100] for i in range(len(nodes) - 1)], float)
        props = np.array([[100, E_ACO, E_ACO, NU, NU, G_ACO]])
        Ls = np.unique(np.round(np.logspace(1.4, 4.0, 70))) if Ls is None else np.asarray(Ls, float)
        m_all = np.array([np.array([1.0]) for _ in Ls], dtype=object)
        p = self.p
        sp = {"cx": p["xc"], "cy": yc, "x0": p["x0"] + p["xc"], "y0": yc, "phi": 0, "A": p["A"], "Ixx": p["Ix"],
              "Iyy": p["Iy"], "Ixy": 0, "I11": p["Ix"], "I22": p["Iy"], "Cw": p["Cw"], "J": p["J"], "B1": 0, "B2": 0,
              "wn": np.array([])}
        gbt = {"glob": [0], "dist": [0], "local": [0], "other": [0], "o_space": 1, "norm": 0, "couple": 1, "orth": 1}
        sig, _, _ = F.strip(props=props, nodes=N, elements=El, lengths=Ls, springs=np.array([]), constraints=np.array([]),
                             GBT_con=gbt, B_C="S-S", m_all=m_all, n_eigs=3, sect_props=sp)
        return Ls, np.array([float(np.ravel(s)[0]) for s in sig])

    def criticos(self, carga="M", L_dist_ref=None):
        """Mínimos da curva de assinatura (razão crítico/escoamento): local (1º mínimo) e distorcional (2º mínimo).
        Sem 2º mínimo distinto (comum na compressão), toma o valor da curva no comprimento distorcional de referência
        (o da flexão, se dado; senão 3 × L_local) — a curva é o menor modo, logo o valor é a favor da segurança."""
        Ls, f = self.assinatura(carga)
        mins = [i for i in range(1, len(f) - 1) if f[i] <= f[i - 1] and f[i] <= f[i + 1] and Ls[i] < 0.5 * Ls[-1]]
        loc = mins[0]
        if len(mins) > 1:
            dist, obs = mins[1], "mínimo distinto"
        else:
            Lr = L_dist_ref or 3 * Ls[loc]
            dist, obs = int(np.argmin(abs(Ls - Lr))), f"sem mínimo distinto: curva em L = {Lr:.0f} mm"
        return dict(f_local=f[loc], L_local=Ls[loc], f_dist=f[dist], L_dist=Ls[dist], obs_dist=obs, Ls=Ls, f=f)

    # -------------------------------------------------- global (analítico)
    def r0(self):
        p = self.p
        return math.sqrt(p["Ix"] / p["A"] + p["Iy"] / p["A"] + p["x0"] ** 2 + p["y0"] ** 2)

    def Ne_flt(self, Lb, Cb=1.0, Kz=1.0):
        """Momento crítico de FLT, flexão em torno do eixo de simetria x (NBR 14762:2010 item 9.8.2.2), N·mm."""
        p, r0 = self.p, self.r0()
        Ney = math.pi ** 2 * E_ACO * p["Iy"] / Lb ** 2
        Nez = (math.pi ** 2 * E_ACO * p["Cw"] / (Kz * Lb) ** 2 + G_ACO * p["J"]) / r0 ** 2
        return Cb * r0 * math.sqrt(Ney * Nez)

    def Ne_compressao(self, Lx, Ly, Lz):
        """Força axial de flambagem global elástica (NBR 14762:2010 item 9.7.2.2 — monossimétrica, x = eixo de simetria), N."""
        p, r0 = self.p, self.r0()
        Nex = math.pi ** 2 * E_ACO * p["Ix"] / Lx ** 2
        Ney = math.pi ** 2 * E_ACO * p["Iy"] / Ly ** 2
        Nez = (math.pi ** 2 * E_ACO * p["Cw"] / Lz ** 2 + G_ACO * p["J"]) / r0 ** 2
        k = 1 - (p["x0"] / r0) ** 2
        Nexz = (Nex + Nez) / (2 * k) * (1 - math.sqrt(1 - 4 * Nex * Nez * k / (Nex + Nez) ** 2))
        return dict(Nex=Nex, Ney=Ney, Nez=Nez, Nexz=Nexz, Ne=min(Ney, Nexz))

    # -------------------------------------------------- MRD (NBR 14762:2010 Anexo C)
    def MRd(self, Lb, Cb=1.0, crit=None, contida=False):
        """Momento resistente de cálculo (kN·m). contida=True: mesa comprimida travada continuamente (sem FLT)."""
        crit = crit or self.criticos("M")
        My = self.W * self.fy
        if contida:
            chi, lam0, Me = 1.0, 0.0, float("inf")
        else:
            Me = self.Ne_flt(Lb, Cb)
            lam0 = math.sqrt(My / Me)
            chi = 1.0 if lam0 <= 0.6 else (1.11 * (1 - 0.278 * lam0 ** 2) if lam0 < 1.336 else 1 / lam0 ** 2)
        MRe = chi * My
        Ml, Md = crit["f_local"] * My, crit["f_dist"] * My
        lam_l = math.sqrt(MRe / Ml)
        MRl = MRe if lam_l <= 0.776 else MRe * (1 - 0.15 / lam_l ** 0.8) / lam_l ** 0.8
        lam_d = math.sqrt(My / Md)
        MRdist = My if lam_d <= 0.673 else My * (1 - 0.22 / lam_d) / lam_d
        MR, modo = min([(MRe, "global (FLT)" if chi < 1 else "escoamento"), (MRl, "local"), (MRdist, "distorcional")],
                       key=lambda v: v[0])
        return dict(MRd=MR / GAMA["flexao"] / 1e6, modo=modo, My=My / 1e6, Me=Me / 1e6, lam0=lam0, chi=chi,
                    lam_l=lam_l, lam_dist=lam_d, MRe=MRe / 1e6, MRl=MRl / 1e6, MRdist=MRdist / 1e6)

    def NcRd(self, Lx, Ly, Lz, crit=None):
        crit = crit or self.criticos("N")
        A, fy = self.p["A"], self.fy
        Ne = self.Ne_compressao(Lx, Ly, Lz)
        lam0 = math.sqrt(A * fy / Ne["Ne"])
        chi = 0.658 ** (lam0 ** 2) if lam0 <= 1.5 else 0.877 / lam0 ** 2
        NRe = chi * A * fy
        Nl, Nd = crit["f_local"] * A * fy, crit["f_dist"] * A * fy
        lam_l = math.sqrt(NRe / Nl)
        NRl = NRe if lam_l <= 0.776 else NRe * (1 - 0.15 / lam_l ** 0.8) / lam_l ** 0.8
        lam_d = math.sqrt(A * fy / Nd)
        NRdist = A * fy if lam_d <= 0.561 else A * fy * (1 - 0.25 / lam_d ** 1.2) / lam_d ** 1.2
        NR, modo = min([(NRe, "global"), (NRl, "local-global"), (NRdist, "distorcional")], key=lambda v: v[0])
        return dict(NcRd=NR / GAMA["compressao"] / 1e3, modo=modo, lam0=lam0, chi=chi, lam_l=lam_l, lam_dist=lam_d,
                    Nex=Ne["Nex"] / 1e3, Ne=Ne["Ne"] / 1e3)

    def VRd(self):
        """Cortante resistente da alma sem enrijecedores (NBR 14762:2010 item 9.8.3, kv = 5,0), kN."""
        h, t, fy, kv = self.bw - 2 * self.t, self.t, self.fy, 5.0
        r = h / t
        l1, l2 = 1.08 * math.sqrt(E_ACO * kv / fy), 1.40 * math.sqrt(E_ACO * kv / fy)
        if r <= l1:
            V = 0.6 * fy * h * t
        elif r <= l2:
            V = 0.65 * t ** 2 * math.sqrt(kv * fy * E_ACO)
        else:
            V = 0.905 * E_ACO * kv * t ** 3 / h
        return V / GAMA["cortante"] / 1e3


class PerfilZ(PerfilUe):
    """Z enrijecido ponto-simétrico (enrijecedores de borda a `ang` graus, padrão 45°), bw×bf×D×t externos (mm).
    Flexão em torno do eixo geométrico x (horizontal): a telha trava a mesa superior (AISI S100 / prática corrente para Z).
    FLT da seção ponto-simétrica: Me = 0,5·Cb·r0·√(Ney·Nez) (NBR 14762:2010 9.8.2.2 c). CT = CG (m_ct = 0)."""

    def __init__(self, bw, bf, D, t, aco="ZAR345", ang=45.0):
        self.bw, self.bf, self.D, self.t, self.aco, self.ang = bw, bf, D, t, aco, ang
        self.fy, self.fu = ACOS[aco]
        h, b, d = bw - t, bf - t / 2, D - t / 2
        c, sn = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        # mesa inferior para a esquerda, superior para a direita; enrijecedores voltados para dentro da seção
        self.pts = [(-b + d * c, d * sn), (-b, 0), (0, 0), (0, h), (b, h), (b - d * c, h - d * sn)]
        self.p = props_parede_fina(self.pts, t)
        self.h_lm = h
        self.W = self.p["Ix"] / (h / 2 + t / 2)
        self.peso_kNm = self.p["A"] * 7850e-9 * 9.81
        self.m_ct = 0.0

    @property
    def nome(self):
        return f"Z{self.ang:.0f} {self.bw:g}×{self.bf:g}×{self.D:g}×{self.t:.2f}".replace(".", ",")

    def Ne_flt(self, Lb, Cb=1.0, Kz=1.0):
        p, r0 = self.p, self.r0()
        Ney = math.pi ** 2 * E_ACO * p["Iy"] / Lb ** 2
        Nez = (math.pi ** 2 * E_ACO * p["Cw"] / (Kz * Lb) ** 2 + G_ACO * p["J"]) / r0 ** 2
        return 0.5 * Cb * r0 * math.sqrt(Ney * Nez)

    def Ne_compressao(self, Lx, Ly, Lz):
        """Ponto-simétrica: CT = CG; flexão nos eixos principais (I1, I2) e torção pura. Eixo menor travado em Ly."""
        p, r0 = self.p, self.r0()
        m, d = (p["Ix"] + p["Iy"]) / 2, math.sqrt(((p["Ix"] - p["Iy"]) / 2) ** 2 + p["Ixy"] ** 2)
        I1, I2 = m + d, m - d
        Nex = math.pi ** 2 * E_ACO * I1 / Lx ** 2
        Ney = math.pi ** 2 * E_ACO * I2 / Ly ** 2
        Nez = (math.pi ** 2 * E_ACO * p["Cw"] / Lz ** 2 + G_ACO * p["J"]) / r0 ** 2
        return dict(Nex=Nex, Ney=Ney, Nez=Nez, Nexz=Nez, Ne=min(Nex, Ney, Nez))


# ------------------------------------------------------------------ ligações parafusadas (chapas finas e laminados)
AREA_PARAF = {10: 78.5, 12: 113.1, 16: 201.1, 20: 314.2}           # área bruta do fuste (mm²)
FUB = {"A307": 415.0, "8.8": 800.0, "A325": 825.0}


def parafuso_corte_Rd(d, classe="8.8", planos=1, norma="NBR8800"):
    """Força cortante resistente por parafuso, plano de corte passando pela rosca (kN).
    NBR 8800:2008 item 6.3.3.2: Fv,Rd = 0,4 Ab fub / γa2 (γa2 = 1,35)."""
    return planos * 0.4 * AREA_PARAF[d] * FUB[classe] / 1.35 / 1e3


def parafuso_tracao_Rd(d, classe="8.8"):
    """NBR 8800:2008 item 6.3.3.1: Ft,Rd = 0,75 Ab fub / γa2 (kN)."""
    return 0.75 * AREA_PARAF[d] * FUB[classe] / 1.35 / 1e3


def pressao_contato_fino_Rd(d, t, fu):
    """Pressão de contato em chapa fina, NBR 14762:2010 item 10.3.2 — Fc,Rd = αe d t fu / γ, γ = 1,55,
    αe = 0,183 t + 1,53 para t < 4,75 mm e 2,4 para 4,75 ≤ t ≤ 6,35 mm (kN)."""
    ae = 0.183 * t + 1.53 if t < 4.75 else 2.4
    return ae * d * t * fu / 1.55 / 1e3


def pressao_contato_Rd(d, t, fu, lf):
    """NBR 8800:2008 item 6.3.3.3 (furo padrão, deformação limitada): min(1,2 lf t fu; 2,4 d t fu) / 1,35 (kN)."""
    return min(1.2 * lf * t * fu, 2.4 * d * t * fu) / 1.35 / 1e3


def barra_redonda_tracao_Rd(d, fy=250.0, fu=400.0):
    """Barra redonda rosqueada (NBR 8800:2008 item 6.3.3.1, Ab bruta, fator 0,75 na rosca) e escoamento da bruta (kN)."""
    Ab = math.pi * d ** 2 / 4
    return min(0.75 * Ab * fu / 1.35, Ab * fy / 1.10) / 1e3


def compressao_laminado_Rd(A, r, L, fy=250.0, K=1.0, Q=1.0):
    """NBR 8800:2008 item 5.3 — barra comprimida (perfil laminado/tubo), curva única χ (kN). A mm², r mm, L mm."""
    Ne = math.pi ** 2 * E_ACO * A * r ** 2 / (K * L) ** 2
    lam0 = math.sqrt(Q * A * fy / Ne)
    chi = 0.658 ** (lam0 ** 2) if lam0 <= 1.5 else 0.877 / lam0 ** 2
    return chi * Q * A * fy / 1.10 / 1e3, lam0, K * L / r
