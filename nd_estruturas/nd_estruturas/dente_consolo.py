"""Dentes Gerber (extremidades rebaixadas) e consolos — dimensionamento por bielas e tirantes.

Base: NBR 9062:2017 item 7.3 (consolos) e 7.4 (dentes de apoio), complementada pelo método do PCI Design Handbook
(8ª ed., seção 5.6, extremidades rebaixadas: flexão e tração no dente, cisalhamento direto, tração diagonal no canto
reentrante, tração diagonal no dente). Adota-se a maior armadura das duas abordagens.
Unidades de entrada: kN, mm, MPa. Sinais: Vd, Hd positivos (Hd = tração horizontal no apoio).
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field

FYK, GAMA_S = 500.0, 1.15
AREA = {6.3: 31.2, 8.0: 50.3, 10.0: 78.5, 12.5: 122.7, 16.0: 201.1, 20.0: 314.2, 25.0: 490.9}


def barras(As_mm2, diam, minimo=2):
    n = max(minimo, math.ceil(As_mm2 / AREA[diam] - 1e-9))
    return n, n * AREA[diam]


@dataclass
class Dente:
    """Dente: b (largura), h_dente (altura do dente), ln (comprimento do dente, da face da ponta à face reentrante),
    a_apoio (distância da ponta ao centro do apoio), h_total (altura da viga cheia), cobrimento ao CG do tirante."""
    nome: str
    Vd: float
    Hd: float
    b: float
    h_dente: float
    ln: float
    a_apoio: float
    h_total: float
    fck: float = 50.0
    c_tir: float = 55.0
    x_ash: float = 60.0           # centro da armadura de suspensão a partir da face reentrante
    res: dict = field(default_factory=dict)

    def dimensionar(self, diam_tir=16.0, diam_sus=12.5, diam_cost=10.0, ramos_sus=2):
        b, h, Vd, Hd, fck = self.b, self.h_dente, self.Vd * 1e3, self.Hd * 1e3, self.fck
        fyd = FYK / GAMA_S
        d = h - self.c_tir
        a = self.ln - self.a_apoio + self.x_ash          # vão de cisalhamento até a suspensão (PCI 5.6.2.1)
        a_face = self.ln - self.a_apoio                  # até a face reentrante (NBR 9062, modelo de consolo)
        r = {}
        # ---------- NBR 9062:2017 7.3 / 7.4 — dente tratado como consolo curto invertido + suspensão
        ad = a_face / d
        if ad <= 0.5:
            tipo = "muito curto (atrito-cisalhamento)"
            mu = 1.4
            As_nbr = Vd / (mu * fyd) * 0.8 + Hd / fyd    # 7.3.3.3 (aprox.: 0,8 Vd/μ fyd + Hd/fyd)
        elif ad <= 1.0:
            tipo = "curto (biela e tirante)"
            As_nbr = (0.1 + ad) * Vd / fyd + Hd / fyd    # 7.3.3.2
        else:
            tipo = "longo (viga em balanço)"
            As_nbr = Vd * a_face / (0.85 * d * fyd) + Hd / fyd
        Asus_nbr = Vd / fyd                              # 7.4 — armadura de suspensão ≥ Vd/fyd junto à face reentrante
        Acost_nbr = 0.4 * As_nbr                         # costura horizontal no dente (≥ 0,4 As,tir)
        tau = Vd / (b * d)
        tau_u = min(0.18 * fck / 1.4 * 1.0, 6.0 * 1.0)   # limite de compressão da biela (≈ 0,2 fcd, conservador)
        r["NBR"] = dict(tipo=tipo, a_d=round(ad, 3), As_tir=round(As_nbr), As_sus=round(Asus_nbr), As_cost=round(Acost_nbr),
                        tau_wd=round(tau, 2), tau_lim=round(tau_u, 2), ok_biela=tau <= tau_u)
        # ---------- PCI (φ do ACI; cargas de cálculo da NBR 8681)
        fy, phi_f, phi_v = FYK, 0.90, 0.75
        Nu = max(Hd, 0.2 * Vd)
        As_flex = (Vd * a / d + Nu * h / d) / (phi_f * fy)                                   # 5.6.2.1
        mu_e = min(6.9 * 1.0 * b * h * 1.4 / Vd, 3.4)
        Af = 2 * Vd / (3 * phi_v * fy * mu_e)                                                 # 5.6.2.2
        An = Nu / (phi_v * fy)
        As_cis = Af + An
        As_min = 0.04 * fck / fy * b * d
        As_pci = max(As_flex, As_cis, As_min)
        Ah = 0.5 * (As_pci - An)
        Ash = Vd / (phi_v * fy)                                                               # 5.6.2.3
        Vmax = phi_v * min(0.2 * fck, 5.5) * b * d
        Vc = 0.166 * math.sqrt(fck) * b * d
        Av = max(0.0, (Vd / phi_v - Vc) / fy - Ah) if Vd / phi_v > Vc else 0.0                 # 5.6.2.4 (Av + Ah) fy + Vc
        Av = max(Av, 0.5 * Ah)
        r["PCI"] = dict(a_mm=round(a), As_flex=round(As_flex), As_cis=round(As_cis), As_min=round(As_min), As=round(As_pci),
                        Ah=round(Ah), Ash=round(Ash), Av=round(Av), Vmax_kN=round(Vmax / 1e3, 1), ok_Vmax=Vd <= Vmax, mu_e=round(mu_e, 2))
        # ---------- adotado
        As = max(As_nbr, As_pci)
        Asus = max(Asus_nbr, Ash)
        Acost = max(Acost_nbr, Ah)
        n_t, A_t = barras(As, diam_tir)
        n_s, A_s = barras(Asus, diam_sus, minimo=2)
        n_s = math.ceil(n_s / ramos_sus)                  # estribos fechados de 2 ramos
        A_s = n_s * ramos_sus * AREA[diam_sus]
        n_c, A_c = barras(Acost, diam_cost, minimo=2)
        n_c = math.ceil(n_c / 2)
        A_c = n_c * 2 * AREA[diam_cost]
        n_v, A_v = barras(Av, 10.0, minimo=2)
        n_v = math.ceil(n_v / 2)
        lb = 44 * diam_tir                                # ancoragem reta CA-50, boa aderência, C50 (NBR 6118 9.4.2.4 ≈ 44φ c/ fbd C50 — conferir)
        r["adotado"] = dict(As_tir=round(As), tirante=f"{n_t} Ø{diam_tir:g} ({A_t:.0f} mm²)",
                            As_sus=round(Asus), suspensao=f"{n_s} estribos Ø{diam_sus:g} fechados ({A_s:.0f} mm²) a até {0.5*self.h_dente:.0f} mm da face reentrante",
                            As_cost=round(Acost), costura=f"{n_c} estribos horizontais Ø{diam_cost:g} ({A_c:.0f} mm²) nos 2/3 superiores do dente".replace("superiores", "inferiores"),
                            Av=round(Av), vertical_dente=f"{n_v} estribos verticais Ø10 no dente",
                            ancoragem_tirante_mm=round(max(lb, self.h_total - self.h_dente + 1.7 * d)),
                            ok=r["PCI"]["ok_Vmax"] and r["NBR"]["ok_biela"],
                            n_tir=n_t, d_tir=diam_tir, n_sus=n_s, d_sus=diam_sus, n_cost=n_c, d_cost=diam_cost, n_v=n_v)
        self.res = r
        return r


def consolo(nome, Vd, Hd, b, h, a, fck=50.0, c=55.0, diam=16.0):
    """Consolo curto (NBR 9062:2017 7.3) — a = distância da carga à face do pilar/viga, h = altura na face."""
    d = h - c
    fyd = FYK / GAMA_S
    ad = a / d
    if ad <= 0.5:
        As = 0.8 * Vd * 1e3 / (1.4 * fyd) + Hd * 1e3 / fyd
        tipo = "muito curto"
    elif ad <= 1.0:
        As = (0.1 + ad) * Vd * 1e3 / fyd + Hd * 1e3 / fyd
        tipo = "curto"
    else:
        raise ValueError("consolo longo: a/d > 1")
    tau = Vd * 1e3 / (b * d)
    tau_u = 0.18 * fck / 1.4
    n, A = barras(As, diam)
    Ast = 0.4 * As                                      # estribos horizontais (costura) nos 2/3 superiores
    return dict(nome=nome, tipo=tipo, a_d=round(ad, 3), As_tir=round(As), tirante=f"{n} Ø{diam:g} ({A:.0f} mm²)",
                As_cost=round(Ast), tau_wd=round(tau, 2), tau_lim=round(tau_u, 2), ok=tau <= tau_u)
