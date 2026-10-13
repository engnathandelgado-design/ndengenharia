"""Ligações PARAFUSADAS em estruturas de aço — NBR 8800:2024 (item 6.3 e 6.5), conforme o Manual Gerdau "Ligações para
Estruturas de Aço" (ed. NBR 8800:2024). Regra da ND: todas as ligações de campo parafusadas, sem solda.

Unidades: kN, cm, kN/cm² (como o manual). γa1 = 1,10 (escoamento), γa2 = 1,35 (ruptura).
Parafusos ASTM F3125 A325 (fub = 82,5 → o manual usa 83 kN/cm²); chapas/cantoneiras A36 (fy 25, fu 40); perfis A572-50 (34,5 / 45).
Furo para área líquida: dh + 0,2 cm (prática do manual). (conferir) = item a confirmar no texto da NBR 8800:2024.
Validado (tests/test_ligacoes_aco.py) contra as tabelas 1 a 4 do manual (págs. 10–11)."""
from __future__ import annotations
import math
from dataclasses import dataclass, field

GA1, GA2 = 1.10, 1.35
POL = 2.54
DIAMETROS = {"5/8": 5 / 8 * POL, "3/4": 3 / 4 * POL, "7/8": 7 / 8 * POL, "1": 1.0 * POL}     # cm
FUB = {"A325": 83.0, "A307": 41.5, "A490": 103.5}                                           # kN/cm²
ACOS = {"A36": (25.0, 40.0), "A572-50": (34.5, 45.0), "MR250": (25.0, 40.0), "AR350": (35.0, 45.0), "A588": (34.5, 48.5)}
PROTENSAO_A325 = {"5/8": 85.0, "3/4": 125.0, "7/8": 173.0, "1": 227.0}                       # FTb (kN), NBR 8800 tab. 15 (conferir 2024)


def area_bruta(d):
    return math.pi * d ** 2 / 4


FUROS = {"5/8": 1.8, "3/4": 2.1, "7/8": 2.4, "1": 2.7}                                    # furo-padrão adotado pelo manual (cm)


def furo_padrao(d):
    """diâmetro do furo-padrão (cm) como no Manual Gerdau 2.4: 18 / 21 / 24 / 27 mm para 5/8", 3/4", 7/8", 1"
    (d + 1,5 mm arredondado para cima); outros diâmetros: d + 0,15 cm (NBR 8800:2024 tab. 12)."""
    for k, v in DIAMETROS.items():
        if abs(v - d) < 1e-6:
            return FUROS[k]
    return d + 0.15


# ------------------------------------------------------------------ parafusos (6.3.3)
def Ft_Rd(d, fub=83.0):
    """tração no parafuso: 0,75·Ab·fub/γa2 (6.3.3.1)."""
    return 0.75 * area_bruta(d) * fub / GA2


def Fv_Rd(d, fub=83.0, planos=1, rosca_no_plano=True):
    """corte: 0,45·Ab·fub/γa2 por plano com a rosca no plano de corte (manual 2024; era 0,40 na 2008);
    0,56·Ab·fub/γa2 com a rosca fora do plano (conferir na NBR 8800:2024)."""
    return planos * (0.45 if rosca_no_plano else 0.56) * area_bruta(d) * fub / GA2


def Fc_Rd(d, t, fu, lf=None, dh=None, deformacao_limitante=True):
    """pressão de contato / rasgamento no furo-padrão (6.3.3.3):
    1,2·lf·t·fu/γa2 ≤ 2,4·d·t·fu/γa2 (deformação no furo limitante); 1,5·lf ≤ 3,0·d caso contrário.
    lf = distância livre na direção da força (s − dh entre furos; e − dh/2 até a borda). Sem lf → só o teto."""
    a, b = (1.2, 2.4) if deformacao_limitante else (1.5, 3.0)
    teto = b * d * t * fu / GA2
    if lf is None:
        return teto
    return min(a * lf * t * fu / GA2, teto)


def Fc_entre_furos(d, t, fu, s, dh=None):
    dh = dh or furo_padrao(d)
    return Fc_Rd(d, t, fu, lf=s - dh)


def Fc_borda(d, t, fu, e, dh=None):
    dh = dh or furo_padrao(d)
    return Fc_Rd(d, t, fu, lf=e - dh / 2)


def interacao_tracao_corte(Ft_Sd, Ft_Rd_, Fv_Sd, Fv_Rd_):
    """(Ft,Sd/Ft,Rd)² + (Fv,Sd/Fv,Rd)² ≤ 1,0 (6.3.3.4)."""
    return (Ft_Sd / Ft_Rd_) ** 2 + (Fv_Sd / Fv_Rd_) ** 2


def Ff_Rd(diam_pol, ns=1, mu=0.35, Ch=1.0, Ft_Sd=0.0, gamma_e=1.2):
    """deslizamento crítico (6.3.4.3): 1,13·μ·Ch·FTb·ns·(1 − Ft,Sd/(1,13·FTb))/γe. diam_pol em '5/8','3/4','7/8','1'.
    μ 0,35 (classe A) / 0,50 (B); Ch 1,0 padrão, 0,85 alargado/pouco alongado, 0,70 muito alongado. (conferir 2024)"""
    FTb = PROTENSAO_A325[diam_pol]
    return 1.13 * mu * Ch * FTb * ns * (1 - Ft_Sd / (1.13 * FTb)) / gamma_e


# ------------------------------------------------------------------ elementos de ligação (6.5)
def tracao_chapa(Ag, An, fy, fu, Ct=1.0):
    """escoamento da área bruta Ag·fy/γa1 e ruptura da área líquida efetiva Ct·An·fu/γa2 (5.2)."""
    return min(Ag * fy / GA1, Ct * An * fu / GA2)


def cisalhamento_chapa(Agv, Anv, fy, fu):
    """escoamento 0,6·fy·Agv/γa1; ruptura 0,6·fu·Anv/γa2 (6.5.5)."""
    return min(0.6 * fy * Agv / GA1, 0.6 * fu * Anv / GA2)


def bloco_cisalhamento(Agv, Anv, Ant, fy, fu, Cts=1.0):
    """colapso por rasgamento (6.5.6): (0,6·fu·Anv + Cts·fu·Ant)/γa2 ≤ (0,6·fy·Agv + Cts·fu·Ant)/γa2."""
    return min((0.6 * fu * Anv + Cts * fu * Ant) / GA2, (0.6 * fy * Agv + Cts * fu * Ant) / GA2)


# ------------------------------------------------------------------ disposições construtivas
EMIN_SERRA = {1.6: 2.9, 1.9: 3.2, 2.2: 3.8, 2.4: 4.2, 2.7: 4.8, 3.0: 5.2, 3.6: 6.4}       # cm, borda cortada (tab. 14)
EMIN_LAMIN = {1.6: 2.2, 1.9: 2.6, 2.2: 2.8, 2.4: 3.1, 2.7: 3.4, 3.0: 3.8, 3.6: 4.6}       # cm, borda laminada/maçarico


def checar_disposicoes(d, s, e, t, borda="laminada", pintado=True):
    """lista de não conformidades: s ≥ 2,7d (pref. 3d); e ≥ tab. 14; e ≤ 12t ≤ 15 cm; s ≤ 24t ≤ 30 cm (pintado)."""
    nc = []
    dm = min(EMIN_LAMIN, key=lambda k: abs(k - d))
    emin = (EMIN_LAMIN if borda == "laminada" else EMIN_SERRA)[dm] if d <= 3.6 else (1.25 if borda == "laminada" else 1.75) * d
    if s < 2.7 * d:
        nc.append(f"espaçamento {s:.1f} < 2,7d = {2.7*d:.1f} cm")
    if e < emin:
        nc.append(f"borda {e:.1f} < {emin:.1f} cm (tab. 14)")
    if e > min(12 * t, 15.0):
        nc.append(f"borda {e:.1f} > 12t ≤ 15 cm")
    if s > (min(24 * t, 30.0) if pintado else min(14 * t, 18.0)):
        nc.append(f"espaçamento {s:.1f} acima do máximo")
    return nc


# ------------------------------------------------------------------ ligação flexível com dupla cantoneira parafusada (LCPP, caso 1)
@dataclass
class LCPP:
    """viga apoiada ligada por 2 cantoneiras parafusadas nas duas abas (LCPP do manual, cap. 3, caso 1: só cortante).
    n parafusos por aba em linha vertical, espaçamento s, borda vertical e, gabarito g (do canto ao furo),
    cantoneira L b×t_c com comprimento L_c; alma da viga apoiada tw, altura H (sem recorte) — recortes não modelados aqui."""
    diam: str = "3/4"
    n: int = 3
    s: float = 7.5
    e: float = 4.0
    b_aba: float = 7.62
    t_c: float = 0.635
    g: float = 4.5
    tw: float = 0.65
    H: float = 35.0
    aco_cant: str = "A36"
    aco_viga: str = "A572-50"
    fub: float = 83.0
    detalhes: dict = field(default_factory=dict)

    @property
    def L_c(self):
        return (self.n - 1) * self.s + 2 * self.e

    def Vd_Rd(self):
        d = DIAMETROS[self.diam]
        dh = furo_padrao(d)
        fyc, fuc = ACOS[self.aco_cant]
        fyv, fuv = ACOS[self.aco_viga]
        n, t = self.n, self.t_c
        r = {}
        r["corte parafusos (2 planos)"] = 2 * n * Fv_Rd(d, self.fub)
        rasg = Fc_borda(d, t, fuc, self.e, dh) + (n - 1) * Fc_entre_furos(d, t, fuc, self.s, dh)
        r["contato nas cantoneiras"] = 2 * rasg
        r["contato na alma"] = n * Fc_Rd(d, self.tw, fuv, lf=self.s - dh)          # alma sem borda livre (viga sem recorte)
        Lc = self.L_c
        r["cisalhamento das cantoneiras"] = 2 * cisalhamento_chapa(Lc * t, (Lc - n * (dh + 0.2)) * t, fyc, fuc)
        r["cisalhamento da alma"] = cisalhamento_chapa(self.H * self.tw, (self.H - n * (dh + 0.2)) * self.tw, fyv, fuv)
        Agv = ((n - 1) * self.s + self.e) * t
        Anv = Agv - (n - 0.5) * (dh + 0.2) * t
        Agt = (self.b_aba - self.g) * t
        Ant = Agt - 0.5 * (dh + 0.2) * t
        r["bloco de cisalhamento das cantoneiras"] = 2 * bloco_cisalhamento(Agv, Anv, Ant, fyc, fuc)
        self.detalhes = r
        return min(r.values())


# Chapa de extremidade (LCHE): NÃO implementada — o valor tabelado do manual (ex.: W250×28,4, CH 6,3, 4 Ø3/4" → 93 kN)
# é governado por verificação (flexão/rotação da chapa) cujas fórmulas não foram lidas (págs. 57–58 corrompidas na extração).
# Implementar só depois de ler o manual completo.


# ------------------------------------------------------------------ emenda parafusada de mesa/alma (talas) — força por tala
def emenda_tala(F_Sd, diam, n_paraf, planos, t_tala, b_tala, t_peca, aco_tala="A36", aco_peca="A572-50", s=7.5, e=4.0, fub=83.0, n_linhas=2):
    """emenda por talas (mesa ou alma): força F_Sd transmitida por n_paraf de cada lado. Verifica corte dos parafusos,
    contato (menor espessura), tração na tala (área bruta e líquida com n_linhas furos por seção). Retorna (FRd, detalhes)."""
    d = DIAMETROS[diam]
    dh = furo_padrao(d)
    fyt, fut = ACOS[aco_tala]
    fyp, fup = ACOS[aco_peca]
    tmin, fu_min = (t_tala * planos, fut) if t_tala * planos * fut <= t_peca * fup else (t_peca, fup)
    por_linha = n_paraf // n_linhas
    r = {"corte parafusos": n_paraf * Fv_Rd(d, fub, planos),
         "contato": n_linhas * (Fc_borda(d, tmin, fu_min, e, dh) + (por_linha - 1) * Fc_entre_furos(d, tmin, fu_min, s, dh)),
         "tração na tala": planos * tracao_chapa(b_tala * t_tala, (b_tala - n_linhas * (dh + 0.2)) * t_tala, fyt, fut)}
    FRd = min(r.values())
    return FRd, r, F_Sd / FRd
