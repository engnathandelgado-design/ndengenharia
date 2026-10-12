"""Chumbadores pré-concretados (pinos com cabeça) em chapas embutidas — ACI 318-19 capítulo 17 (unidades N, mm, MPa).

A NBR 9062:2017 remete a ancoragem de insertos a modelos consagrados; aqui se usa o método CCD do ACI 318-19
(cone de concreto, arrancamento, ruptura do aço, fendilhamento lateral, pryout), concreto fissurado (ψc = 1,0),
condição B (sem armadura suplementar) salvo quando se declara armadura de ancoragem para cortante.
"""
from __future__ import annotations
import math
from dataclasses import dataclass


@dataclass
class GrupoPinos:
    """Grupo retangular nx × ny de pinos com cabeça, espaçamentos sx (direção x) e sy (direção y).
    Distâncias às bordas do elemento: cx_neg, cx_pos, cy_neg, cy_pos (mm, a partir dos pinos extremos).
    ha = espessura do elemento na direção do pino."""
    d: float                 # diâmetro do fuste
    d_cabeca: float
    hef: float
    nx: int
    ny: int
    sx: float
    sy: float
    cx_neg: float
    cx_pos: float
    cy_neg: float
    cy_pos: float
    ha: float
    futa: float = 450.0      # pino com cabeça (stud) fu ≥ 450 MPa
    fya: float = 350.0
    fc: float = 50.0
    lam: float = 1.0

    @property
    def n(self):
        return self.nx * self.ny

    @property
    def Ase(self):
        return math.pi * self.d ** 2 / 4

    # ------------------------------------------------------------ tração
    def tracao(self):
        h = self.hef
        futa = min(self.futa, 1.9 * self.fya, 860.0)
        Nsa = self.n * self.Ase * futa                                             # 17.6.1.2
        c = lambda v: min(v, 1.5 * h)
        ANc = (c(self.cx_neg) + (self.nx - 1) * self.sx + c(self.cx_pos)) * (c(self.cy_neg) + (self.ny - 1) * self.sy + c(self.cy_pos))
        ANco = 9 * h ** 2
        cmin = min(self.cx_neg, self.cx_pos, self.cy_neg, self.cy_pos)
        psi_ed = 1.0 if cmin >= 1.5 * h else 0.7 + 0.3 * cmin / (1.5 * h)        # 17.6.2.4.1
        Nb = 10 * self.lam * math.sqrt(self.fc) * h ** 1.5                         # 17.6.2.2.1 (kc = 10, pré-concretado)
        Ncbg = ANc / ANco * psi_ed * 1.0 * 1.0 * Nb                                 # ψec = ψc = ψcp = 1
        Abrg = math.pi * (self.d_cabeca ** 2 - self.d ** 2) / 4
        Npn = self.n * 8 * Abrg * self.fc                                          # 17.6.3.2.2 (ψc,P = 1,0 fissurado)
        Nsb = None
        if cmin < 0.4 * h:                                                         # 17.6.4.1 fendilhamento lateral
            Nsb = self.n * 13 * cmin * math.sqrt(Abrg) * self.lam * math.sqrt(self.fc)
        R = dict(aco=0.75 * Nsa, cone=0.70 * Ncbg, arrancamento=0.70 * Npn)
        if Nsb:
            R["fendilhamento"] = 0.70 * Nsb
        k = min(R, key=R.get)
        return dict(phiNn_kN=R[k] / 1e3, modo=k, todos_kN={a: round(b / 1e3, 1) for a, b in R.items()}, Ncbg_kN=Ncbg / 1e3)

    # ------------------------------------------------------------ cortante
    def cortante(self, direcao="x+", ca1=None, armadura_ancoragem_kN=0.0):
        """direcao: borda para onde a força aponta ('x+', 'x-', 'y+', 'y-'). Ruptura de borda pela fileira mais próxima."""
        futa = min(self.futa, 1.9 * self.fya, 860.0)
        Vsa = self.n * 0.6 * self.Ase * futa                                       # 17.7.1.2 (pino com cabeça)
        if direcao[0] == "x":
            c1 = ca1 or (self.cx_pos if direcao == "x+" else self.cx_neg)
            s_perp, n_perp, c2a, c2b = self.sy, self.ny, self.cy_neg, self.cy_pos
        else:
            c1 = ca1 or (self.cy_pos if direcao == "y+" else self.cy_neg)
            s_perp, n_perp, c2a, c2b = self.sx, self.nx, self.cx_neg, self.cx_pos
        # 17.7.2.1.2 — seção estreita e delgada: limita ca1
        if max(c2a, c2b) < 1.5 * c1 and self.ha < 1.5 * c1:
            c1 = max(max(c2a, c2b) / 1.5, self.ha / 1.5, s_perp * (n_perp - 1) / 3)
        le = min(self.hef, 8 * self.d)
        Vb = min(0.6 * (le / self.d) ** 0.2 * math.sqrt(self.d) * self.lam * math.sqrt(self.fc) * c1 ** 1.5,
                 3.7 * self.lam * math.sqrt(self.fc) * c1 ** 1.5)                 # 17.7.2.2.1
        lim = 1.5 * c1
        AVc = (min(c2a, lim) + (n_perp - 1) * s_perp + min(c2b, lim)) * min(1.5 * c1, self.ha)
        AVco = 4.5 * c1 ** 2
        c2 = min(c2a, c2b)
        psi_ed = 1.0 if c2 >= 1.5 * c1 else 0.7 + 0.3 * c2 / (1.5 * c1)
        psi_h = max(1.0, math.sqrt(1.5 * c1 / self.ha))
        Vcbg = AVc / AVco * psi_ed * 1.0 * psi_h * Vb                              # 17.7.2.1 (ψc,V = 1,0)
        t = self.tracao()
        kcp = 1.0 if self.hef < 65 else 2.0
        Vcpg = kcp * t["Ncbg_kN"] * 1e3                                            # 17.7.3
        R = dict(aco=0.65 * Vsa, borda=0.70 * Vcbg, pryout=0.70 * Vcpg)
        if armadura_ancoragem_kN:
            R["borda"] = max(R["borda"], armadura_ancoragem_kN * 1e3)              # 17.5.2.1 — armadura de ancoragem
        k = min(R, key=R.get)
        return dict(phiVn_kN=R[k] / 1e3, modo=k, todos_kN={a: round(b / 1e3, 1) for a, b in R.items()}, ca1=c1)


def interacao(Nu, phiNn, Vu, phiVn):
    """ACI 318-19 17.8: N/φNn + V/φVn ≤ 1,2 (quando ambos > 0,2), senão cada um ≤ 1."""
    rn, rv = Nu / phiNn, Vu / phiVn
    if rn <= 0.2:
        return rv, rv <= 1.0
    if rv <= 0.2:
        return rn, rn <= 1.0
    return (rn + rv) / 1.2, rn + rv <= 1.2


def grampo_ancoragem_kN(diam, pernas=2, fy=420.0):
    """Armadura de ancoragem para cortante (grampo em U envolvendo os pinos), φ = 0,75, fy ≤ 420 MPa — ACI 318-19 17.5.2.1(a)."""
    return 0.75 * pernas * math.pi * diam ** 2 / 4 * fy / 1e3
