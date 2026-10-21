"""Laje alveolar protendida (pré-tração) com capa — propriedades e verificações específicas.

Unidades: m, kN, kPa nas contas; MPa só na entrada/saída indicada. Compressão negativa nas tensões.

Normas e métodos:
- NBR 14861:2022 (lajes alveolares pré-moldadas de concreto protendido), que remete à NBR 6118 e à NBR 9062;
- NBR 6118:2023 17.4.2.2 (cortante em elementos sem armadura transversal), 17.2.4.3.2 (ato), 23.3 (vibração);
- NBR 9062:2017 5.3.2 (situações transitórias), 6.3 (peça composta), Tab. 9 (flechas);
- EN 1168:2005+A3:2011 4.3.3.2.2 / EN 1992-1-1:2004 6.2.2(2) eq. (6.4) (tração na alma, região não fissurada por flexão)
  e EN 1992-1-1 6.2.5 (interface) — método de referência onde a NBR remete a ensaio ou não detalha;
- PCI Design Handbook (8ª ed.), Tab. 5.8.2.1 — multiplicadores de flecha de longo prazo (peça com capa composta).
"""
from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass
class SecaoAlveolar:
    """Seção 'b × h' com n alvéolos circulares de diâmetro d, centrados em y_alv, com passo s (centro a centro)."""
    b: float
    h: float
    n: int
    d: float
    passo: float
    y_alv: float | None = None
    dy: float = 0.0005
    recorte: tuple | None = None          # (x0, x1) — faixa retirada em toda a altura (recorte junto ao pilar), x a partir do eixo
    preenchidos: tuple = ()               # índices dos alvéolos preenchidos com concreto/graute (contam 50 % — NBR 14861:2022)

    def __post_init__(self):
        if self.y_alv is None:
            self.y_alv = self.h / 2
        if self.n * self.d >= self.b or self.d >= self.h:
            raise ValueError("alvéolos não cabem na seção")
        if self.recorte and not (-self.b / 2 <= self.recorte[0] < self.recorte[1] <= self.b / 2):
            raise ValueError("recorte fora da largura da laje")
        if self.passo < self.d:
            raise ValueError("passo menor que o diâmetro do alvéolo")
        self._calc()

    def x_alveolos(self):
        x0 = -(self.n - 1) * self.passo / 2
        return [x0 + k * self.passo for k in range(self.n)]

    def x_nervuras(self):
        """Centro de cada nervura (n + 1): as 2 de borda e as internas, entre alvéolos."""
        xa = self.x_alveolos()
        r = self.d / 2
        borda_e = (-self.b / 2 + xa[0] - r) / 2
        borda_d = (self.b / 2 + xa[-1] + r) / 2
        return [borda_e] + [(a + c) / 2 for a, c in zip(xa[:-1], xa[1:])] + [borda_d]

    def larg_nervuras(self):
        xa = self.x_alveolos()
        r = self.d / 2
        return [xa[0] - r + self.b / 2] + [self.passo - self.d] * (self.n - 1) + [self.b / 2 - xa[-1] - r]

    def largura(self, y):
        """Largura de concreto na cota y (b menos as cordas dos alvéolos e menos o recorte, se houver;
        alvéolo preenchido conta com 50 % da corda)."""
        r = self.d / 2
        xr = self.recorte

        def dentro(a, c):                                     # comprimento de [a, c] fora do recorte
            if not xr:
                return c - a
            return max(0.0, min(c, xr[0]) - a) + max(0.0, c - max(a, xr[1]))
        w = dentro(-self.b / 2, self.b / 2)
        if abs(y - self.y_alv) < r:
            meia = math.sqrt(r * r - (y - self.y_alv) ** 2)
            for k, xa in enumerate(self.x_alveolos()):
                corda = dentro(xa - meia, xa + meia)
                w -= corda * (0.5 if k in self.preenchidos else 1.0)
        return w

    def _calc(self):
        ys, ws = [], []
        y = self.dy / 2
        while y < self.h:
            ys.append(y)
            ws.append(self.largura(y))
            y += self.dy
        A = sum(w * self.dy for w in ws)
        yc = sum(w * self.dy * y for w, y in zip(ws, ys)) / A
        I = sum(w * self.dy * (y - yc) ** 2 for w, y in zip(ws, ys))
        self.A, self.yc, self.I = A, yc, I
        self._ys, self._ws = ys, ws

    def S(self, y):
        """Momento estático (m³), em relação ao centroide, da parte acima de y."""
        return sum(w * self.dy * (yy - self.yc) for w, yy in zip(self._ws, self._ys) if yy > y)

    @property
    def Wi(self):
        return self.I / self.yc

    @property
    def Ws(self):
        return self.I / (self.h - self.yc)

    @property
    def bw_min(self):
        """Soma das nervuras na cota mais estreita (centro dos alvéolos)."""
        return self.largura(self.y_alv)

    @property
    def perimetro(self):
        """Perímetro em contato com o ar para 2Ac/u (alvéolos fechados nas pontas: só o contorno externo)."""
        return 2 * (self.b + self.h)


def composta(sec: SecaoAlveolar, b_capa, h_capa, n_mod):
    """Seção homogeneizada laje + capa (capa com fator n = Ec,capa/Ec,laje). Devolve A, yc, I (da laje 'equivalente')."""
    Ac = b_capa * h_capa * n_mod
    yc_capa = sec.h + h_capa / 2
    A = sec.A + Ac
    yc = (sec.A * sec.yc + Ac * yc_capa) / A
    I = sec.I + sec.A * (sec.yc - yc) ** 2 + n_mod * b_capa * h_capa ** 3 / 12 + Ac * (yc_capa - yc) ** 2
    return dict(A=A, yc=yc, I=I, Ac_hom=Ac, y_capa=yc_capa, h_tot=sec.h + h_capa)


def vrd_tracao_alma(sec: SecaoAlveolar, fctd_MPa, P_kN, alfa_l=1.0, n_pts=60):
    """Tração na alma (região não fissurada por flexão) — EN 1168 4.3.3.2.2 / EN 1992-1-1 6.2.2(2) eq. (6.4):
    VRd,c = I·bw(y)/S(y) · √(fctd² + αl·σcp(y)·fctd), mínimo ao longo da altura (aqui σcp = αl·P/A uniforme,
    simplificação a favor da segurança na fibra do centroide, onde S é máximo). Devolve (VRd kN, y crítico m)."""
    fctd = fctd_MPa * 1000
    scp = alfa_l * P_kN / sec.A                                  # kPa (compressão positiva)
    melhor = (1e99, None)
    for k in range(1, n_pts):
        y = sec.h * k / n_pts
        S = sec.S(y)
        if S <= 0:
            continue
        v = sec.I * sec.largura(y) / S * math.sqrt(fctd ** 2 + scp * fctd)
        melhor = min(melhor, (v, y))
    return melhor


def vrd1_nbr(bw, d, fck_MPa, rho1, sig_cp_MPa, k=None, gama_c=1.4):
    """NBR 6118:2023 17.4.2.2 — VRd1 = [τRd·k·(1,2 + 40ρ1) + 0,15σcp]·bw·d, τRd = 0,25 fctd,
    fctd = fctk,inf/γc; k = |1,6 − d| ≥ 1 (armadura que chega ao apoio ≥ 50 %); ρ1 ≤ 0,02; σcp compressão positiva. kN."""
    fctm = 0.3 * fck_MPa ** (2 / 3) if fck_MPa <= 50 else 2.12 * math.log(1 + 0.11 * fck_MPa)
    fctd = 0.7 * fctm / gama_c
    tau = 0.25 * fctd
    k = max(1.0, abs(1.6 - d)) if k is None else k
    rho = min(rho1, 0.02)
    return (tau * k * (1.2 + 40 * rho) + 0.15 * sig_cp_MPa) * bw * d * 1000


def frequencia_biapoiada(EI_kNm2, m_t_por_m, L):
    """Primeira frequência natural de viga biapoiada (Hz): f = π/(2L²)·√(EI/m)."""
    return math.pi / (2 * L * L) * math.sqrt(EI_kNm2 / m_t_por_m)


# PCI Design Handbook 8ª ed., Tab. 5.8.2.1 — multiplicadores (sem capa / com capa composta)
PCI_MULT = {
    "montagem": dict(g1=1.85, P=1.80),
    "final": dict(g1=2.70, P=2.45, g_sup=3.00),
    "final_composta": dict(g1=2.40, P=2.20, g_sup=3.00, capa=2.30),
}
