"""Ligações PARAFUSADAS em estruturas de aço — NBR 8800:2024 (item 6.3 e 6.5), conforme o Manual Gerdau "Ligações para
Estruturas de Aço" (ed. NBR 8800:2024). Regra da ND: todas as ligações de campo parafusadas, sem solda.

Unidades: kN, cm, kN/cm² (como o manual). γa1 = 1,10 (escoamento), γa2 = 1,35 (ruptura).
Parafusos ASTM F3125 A325 (fub = 82,5 → o manual usa 83 kN/cm²); chapas/cantoneiras A36 (fy 25, fu 40); perfis A572-50 (34,5 / 45).
Furo para área líquida: dh + 0,2 cm (prática do manual). (conferir) = item a confirmar no texto da NBR 8800:2024.
Validado (tests/test_ligacoes_aco.py) contra as tabelas 1 a 4 do manual (págs. 10–11) e contra exemplos e tabelas
dos caps. 3 (LCPP com recortes), 4 (LCHE), 5 (LCHS), 6 (LMPA) e 8 (LT/LMTS). LCHE, LCHS e LMPA têm solda de oficina
(chapa na viga ou no suporte); a montagem em campo é só parafusada. LMSS (cap. 7, mesas soldadas em campo) não é
implementada (regra da ND). Hipóteses do manual que diferem do texto das fórmulas estão nas docstrings de LCHS, LMPA e LT."""
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
def dados_perfil(nome):
    """propriedades do perfil W/HP do catálogo Gerdau (metalica_laminada) convertidas para cm:
    d, bf, tf, tw, d_linha (parte plana da alma), h."""
    from nd_estruturas.metalica_laminada import perfil
    p = perfil(nome)
    return {"nome": p.nome, "d": p.d / 10, "bf": p.bf / 10, "tf": p.tf / 10, "tw": p.tw / 10,
            "d_linha": p.d_linha / 10, "h": p.h / 10}


def _secao_te_recortada(H, Lv, bf, tf, tw):
    """módulo elástico (cm³) da seção T remanescente no recorte de 1 mesa: alma de altura h0 − tf + mesa inferior;
    fibra crítica = borda do recorte (a mais afastada)."""
    h0 = H - Lv
    hw = h0 - tf
    A1, y1 = bf * tf, tf / 2
    A2, y2 = tw * hw, tf + hw / 2
    yc = (A1 * y1 + A2 * y2) / (A1 + A2)
    Ix = bf * tf ** 3 / 12 + A1 * (yc - y1) ** 2 + tw * hw ** 3 / 12 + A2 * (y2 - yc) ** 2
    return Ix / max(h0 - yc, yc)


def Fbc_alma_recortada(tw, h0, Lh, H, fy):
    """tensão crítica de flambagem local da alma recortada (kN/cm²), manual pág. 20, adaptada da AISC 13ª ed. p. 9-7a:
    Fbc = 16243·(tw/h0)²·f·k, f = 2·Lh/H, k = 2,2·(h0/Lh)^1,65. O 16243 já embute φ = 0,9 da AISC (0,9·26210 ksi);
    limitada a fy/γa1 (equivalente ao Fcr ≤ Fy da AISC). Validade: Lh ≤ h0 e Lh ≤ H."""
    f = 2 * Lh / H
    k = 2.2 * (h0 / Lh) ** 1.65
    return min(16243 * (tw / h0) ** 2 * f * k, fy / GA1)


@dataclass
class LCPP:
    """viga apoiada ligada por 2 cantoneiras parafusadas nas duas abas (LCPP do manual, cap. 3, caso 1: só cortante,
    págs. 14–20). n parafusos por aba em linha vertical, espaçamento s, borda vertical e, gabarito g (do canto ao furo),
    cantoneira L b×t_c com comprimento L_c; alma da viga apoiada tw, altura H.
    Recortes (recortes = 0, 1 ou 2): Lv = altura do recorte, Lh = comprimento horizontal do recorte, ya = distância do
    topo da viga ao primeiro furo (75 mm nos W250–W610 do manual); com recorte exige bf e tf (ou perfil=)."""
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
    recortes: int = 0
    Lv: float = 0.0
    Lh: float = 0.0
    ya: float = 7.5
    bf: float | None = None
    tf: float | None = None
    perfil: str | None = None
    detalhes: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.perfil:
            p = dados_perfil(self.perfil)
            self.tw, self.H, self.bf, self.tf = p["tw"], p["d"], p["bf"], p["tf"]
        if self.recortes not in (0, 1, 2):
            raise ValueError("recortes deve ser 0, 1 ou 2")
        if self.recortes and (self.Lv <= 0 or self.Lh <= 0):
            raise ValueError("viga recortada: informe Lv > 0 e Lh > 0 (cm)")
        if self.recortes == 1 and (self.bf is None or self.tf is None):
            raise ValueError("1 recorte: informe bf e tf (ou perfil=) para o módulo da seção T")

    @property
    def L_c(self):
        return (self.n - 1) * self.s + 2 * self.e

    def Vd_Rd(self):
        d = DIAMETROS[self.diam]
        dh = furo_padrao(d)
        fyc, fuc = ACOS[self.aco_cant]
        fyv, fuv = ACOS[self.aco_viga]
        n, t, tw = self.n, self.t_c, self.tw
        r = {}
        r["corte parafusos (2 planos)"] = 2 * n * Fv_Rd(d, self.fub)                      # NBR 8800:2024 6.3.3.2
        rasg = Fc_borda(d, t, fuc, self.e, dh) + (n - 1) * Fc_entre_furos(d, t, fuc, self.s, dh)
        r["contato nas cantoneiras"] = 2 * rasg                                              # NBR 8800:2024 6.3.3.3
        r["contato na alma"] = n * Fc_Rd(d, tw, fuv, lf=self.s - dh)          # alma sem borda livre vertical
        Lc = self.L_c
        r["cisalhamento das cantoneiras"] = 2 * cisalhamento_chapa(Lc * t, (Lc - n * (dh + 0.2)) * t, fyc, fuc)
        Hr = self.H - self.recortes * self.Lv                                 # manual pág. 18: H, H − Lv, H − 2Lv
        r["cisalhamento da alma"] = cisalhamento_chapa(Hr * tw, (Hr - n * (dh + 0.2)) * tw, fyv, fuv)  # 6.5.5
        Agv = ((n - 1) * self.s + self.e) * t
        Anv = Agv - (n - 0.5) * (dh + 0.2) * t
        Agt = (self.b_aba - self.g) * t
        Ant = Agt - 0.5 * (dh + 0.2) * t
        r["bloco de cisalhamento das cantoneiras"] = 2 * bloco_cisalhamento(Agv, Anv, Ant, fyc, fuc)   # 6.5.6
        if self.recortes:
            # bloco de cisalhamento da alma recortada (manual pág. 19; NBR 8800:2024 6.5.6)
            Agvw = (Lc - 2 * self.e + self.ya - self.Lv) * tw
            Anvw = Agvw - (n - 0.5) * (dh + 0.2) * tw
            Agtw = (self.g - 1.0) * tw                     # g − folga de 10 mm = borda horizontal na alma
            Antw = Agtw - 0.5 * (dh + 0.2) * tw
            r["bloco de cisalhamento da alma"] = bloco_cisalhamento(Agvw, Anvw, Antw, fyv, fuv)
            # início de escoamento por flexão na seção recortada (manual pág. 19): fy·W/[(Lh + 1,0)·1,1]
            if self.recortes == 1:
                h0 = self.H - self.Lv
                W = _secao_te_recortada(self.H, self.Lv, self.bf, self.tf, tw)
            else:
                h0 = self.H - 2 * self.Lv
                W = tw * h0 ** 2 / 6
            braco = self.Lh + 1.0                          # + folga de 10 mm entre viga e apoio
            r["flexão na seção recortada"] = fyv * W / (braco * GA1)
            # flambagem local da alma no recorte (manual pág. 19–20; AISC 13ª ed. p. 9-7a), Lh ≤ h0
            if self.Lh > h0:
                raise ValueError(f"Lh = {self.Lh} > h0 = {h0:.1f} cm: fora do campo de validade (manual pág. 19)")
            r["flambagem local da alma recortada"] = Fbc_alma_recortada(tw, h0, self.Lh, self.H, fyv) * W / braco
        self.detalhes = r
        return min(r.values())


# ------------------------------------------------------------------ interação de Drucker (chapas e cantoneiras com Nd)
def _drucker(M0, V0, braco):
    """resolve (V·braco/M0) + (V/V0)^4 = 1 em V (força por unidade de comprimento, kN/cm) por bisseção."""
    lo, hi = 0.0, min(V0, M0 / braco)
    for _ in range(200):
        V = (lo + hi) / 2
        if V * braco / M0 + (V / V0) ** 4 > 1:
            hi = V
        else:
            lo = V
    return lo


# ------------------------------------------------------------------ chapa de extremidade (LCHE), manual cap. 4
@dataclass
class LCHE:
    """viga apoiada com chapa de extremidade soldada (oficina) na alma e parafusada no suporte (LCHE, cap. 4,
    págs. 55–58). Chapa de altura L_fch = (Nps/2 − 1)·s + 2e, largura 200 mm, gabarito horizontal g_ch = 120 mm,
    Nps parafusos em 2 linhas verticais; filetes de perna b_solda dos dois lados da alma (E70XX).
    Padrão do manual: 5/8" → s = 6, e = 3 cm; 3/4" e 7/8" → s = 7,5, e = 4 cm; CH 6,3 com solda 5 mm, CH 8,0 com 6 mm.
    Vd_Rd(): força cortante máxima com Nd = 0. Nd_Rd(): Nd que, com Vd = 50% de Vd,max, plastifica a chapa
    (Drucker, manual pág. 58) — Nd atua no centro da ligação. A chapa de 6,3 mm usa t = 0,63 cm (como o manual)."""
    diam: str = "3/4"
    nps: int = 4
    t_ch: float = 0.63
    s: float | None = None
    e: float | None = None
    g_ch: float = 12.0
    b_solda: float | None = None
    tw: float | None = None
    perfil: str | None = None
    aco_ch: str = "A36"
    aco_viga: str = "A572-50"
    fub: float = 83.0
    detalhes: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.perfil:
            self.tw = dados_perfil(self.perfil)["tw"]
        if self.tw is None:
            raise ValueError("informe tw (cm) ou perfil=")
        if self.nps < 4 or self.nps % 2:
            raise ValueError("LCHE: número de parafusos par, ≥ 4 (2 linhas verticais)")
        pequeno = self.diam == "5/8"
        self.s = self.s if self.s is not None else (6.0 if pequeno else 7.5)
        self.e = self.e if self.e is not None else (3.0 if pequeno else 4.0)
        if self.b_solda is None:
            self.b_solda = 0.5 if self.t_ch <= 0.65 else 0.6

    @property
    def L_fch(self):
        return (self.nps / 2 - 1) * self.s + 2 * self.e

    def Vd_Rd(self):
        d = DIAMETROS[self.diam]
        dh = furo_padrao(d)
        fyc, fuc = ACOS[self.aco_ch]
        fy, _ = ACOS[self.aco_viga]
        t, N, L, s, e = self.t_ch, self.nps, self.L_fch, self.s, self.e
        r = {}
        r["corte parafusos"] = 0.45 * area_bruta(d) * self.fub * N / GA2                  # NBR 8800:2024 6.3.3.2
        r["contato sem rasgamento"] = 2.4 * d * t * fuc * N / GA2                         # NBR 8800:2024 6.3.3.3
        r["contato com rasgamento entre furos"] = 1.2 * (s - dh) * t * fuc * N / GA2
        r["contato com rasgamento furo-borda"] = 1.2 * (e - dh / 2) * t * fuc * N / GA2
        r["escoamento da chapa (cisalhamento)"] = 2 * 0.6 * fyc * L * t / GA1             # NBR 8800:2024 6.5.5
        r["ruptura da chapa (cisalhamento)"] = 2 * 0.6 * fuc * (L * t - N / 2 * (dh + 0.2) * t) / GA2
        r["cisalhamento da alma da viga"] = 0.6 * fy * L * self.tw / GA1                  # NBR 8800:2024 6.5.5.a
        # flexão da chapa de extremidade, manual pág. 58: [4·t·Lfch²/(6·g)]·fy/1,1 (expressão do manual, reproduz
        # as tabelas LCHE: ex. 4 Ø 3/4", Lfch = 15,5 → 191 kN)
        r["flexão da chapa"] = 4 * t * L ** 2 / (6 * self.g_ch) * fyc / GA1
        # solda E70XX (oficina), NBR 8800:2024 6.2.5.1: 41,14 = 2·0,6·48,5·0,707; 30 = 2·0,6·25 (metal-base)
        r["ruptura da solda"] = 41.14 * L * self.b_solda / GA2
        r["escoamento do metal-base"] = 30.0 * L * self.b_solda / GA1
        self.detalhes = r
        return min(r.values())

    def Nd_Rd(self, Vd_max=None):
        """força normal que, com Vdm = Vd,max/2, plastifica a chapa (Drucker, manual pág. 58). Retorna (Nd, Vdm)."""
        Vd_max = Vd_max if Vd_max is not None else self.Vd_Rd()
        fyc, _ = ACOS[self.aco_ch]
        t, L = self.t_ch, self.L_fch
        Vdm = Vd_max / 2
        Vz = Vdm / (2 * L)                                       # cortante por unidade de comprimento em cada face
        t_li = Vz / (0.6 * fyc / GA1)                            # espessura reservada ao cortante
        V0 = 0.6 * fyc * (t - t_li) / GA1                        # (Vo)x
        M0 = 0.25 * (t ** 2 - t_li ** 2) * fyc / GA1             # (Mo)z
        braco = (self.g_ch - self.tw) / 4                        # (M)z = (V)x/2 · (g − tw)/2
        Vx = _drucker(M0, V0, braco)
        Nd = 2 * L * Vx
        # a solda deve resistir a √(Nd² + Vdm²)
        Rw = min(41.14 * L * self.b_solda / GA2, 30.0 * L * self.b_solda / GA1)
        Nd = min(Nd, math.sqrt(max(Rw ** 2 - Vdm ** 2, 0.0)))
        return Nd, Vdm

    def verificar(self, Vd, Nd=0.0):
        """retorna (ok, mensagens). Com Nd ≠ 0 vale o par tabelado (Nd,max com 50% de Vd,max)."""
        VR = self.Vd_Rd()
        msgs = []
        if Nd == 0:
            ok = Vd <= VR
            msgs.append(f"Vd = {Vd:.1f} ≤ Vd,Rd = {VR:.1f} kN" if ok else f"Vd = {Vd:.1f} > Vd,Rd = {VR:.1f} kN")
            return ok, msgs
        NR, Vdm = self.Nd_Rd(VR)
        ok = abs(Nd) <= NR and Vd <= Vdm
        msgs.append(f"Nd = {abs(Nd):.1f} / Nd,Rd = {NR:.1f}; Vd = {Vd:.1f} / {Vdm:.1f} kN (50% de Vd,max)")
        return ok, msgs


def lche_rotacao_ok(theta_rad, dist_cm):
    """manual pág. 56: rotação de apoio (rad) × distância vertical do centro da mesa inferior aos parafusos
    superiores ≤ 2 mm."""
    return theta_rad * dist_cm <= 0.2


# ------------------------------------------------------------------ chapa simples / shear tab (LCHS), manual cap. 5
C_LCHS = {2: 0.88, 3: 1.75, 4: 2.81, 5: 3.90, 6: 4.98}    # AISC 16ª ed. tab. 7-6 (ex = 75 mm), 3/4" a 1" (pág. 86)
C_LCHS_5_8 = 0.74                                         # 5/8" (manual pág. 86)


@dataclass
class LCHS:
    """chapa simples soldada (oficina) no suporte e parafusada na alma da viga (LCHS/shear tab, cap. 5, págs. 85–89).
    np parafusos em 1 linha vertical a ec = 7,5 cm da solda; borda horizontal da chapa e_h = 4 cm; viga a 1 cm do
    suporte. Padrão: 5/8" → s = 6, e = 2,5 cm; demais → s = 7,5, e = 4 cm. Filete duplo de perna b_solda.
    Hipótese que reproduz as tabelas LCHS (págs. 90–99): no rasgamento lf = e − (dh + 0,2)/2 (borda) e
    s − (dh + 0,2) (entre furos), e o coeficiente c de excentricidade multiplica corte e contato.
    Caso 2 (manual pág. 89): Vd = 0,5·Vd,max com Nd,max = 0,25·Vd,max, verificando a chapa e a solda."""
    diam: str = "3/4"
    np_: int = 3
    t_c: float = 0.63
    s: float | None = None
    e: float | None = None
    e_h: float = 4.0
    ec: float = 7.5
    b_solda: float = 0.5
    tw: float | None = None
    H: float | None = None
    perfil: str | None = None
    aco_ch: str = "A36"
    aco_viga: str = "A572-50"
    fub: float = 83.0
    detalhes: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.perfil:
            p = dados_perfil(self.perfil)
            self.tw, self.H = p["tw"], p["d"]
        if self.tw is None or self.H is None:
            raise ValueError("informe tw e H (cm) ou perfil=")
        if self.np_ not in C_LCHS:
            raise ValueError("LCHS: 2 a 6 parafusos (coeficientes c da AISC tab. 7-6)")
        pequeno = self.diam == "5/8"
        self.s = self.s if self.s is not None else (6.0 if pequeno else 7.5)
        self.e = self.e if self.e is not None else (2.5 if pequeno else 4.0)

    @property
    def c(self):
        return C_LCHS_5_8 if self.diam == "5/8" else C_LCHS[self.np_]

    @property
    def L_c(self):
        return (self.np_ - 1) * self.s + 2 * self.e

    def _W(self):
        """módulos elásticos bruto e líquido da chapa (cm³) na linha de parafusos."""
        d = DIAMETROS[self.diam]
        dn = furo_padrao(d) + 0.2
        L, t = self.L_c, self.t_c
        I = t * L ** 3 / 12
        In = I
        for i in range(self.np_):
            y = -L / 2 + self.e + i * self.s
            In -= t * dn ** 3 / 12 + t * dn * y ** 2
        return t * L ** 2 / 6, In / (L / 2)

    def Vd_Rd(self):
        d = DIAMETROS[self.diam]
        dh = furo_padrao(d)
        dn = dh + 0.2
        fyc, fuc = ACOS[self.aco_ch]
        fy, fu = ACOS[self.aco_viga]
        N, c, t, tw, L = self.np_, self.c, self.t_c, self.tw, self.L_c
        r = {}
        r["corte parafusos"] = 0.45 * area_bruta(d) * self.fub * c / GA2                 # NBR 8800:2024 6.3.3.2
        lf_c = min(self.e - dn / 2, self.s - dn)
        r["contato na chapa"] = min(2.4 * d, 1.2 * lf_c) * t * fuc * c / GA2               # NBR 8800:2024 6.3.3.3
        lf_w = self.s - dn                                     # alma: sem borda livre na direção da força
        r["contato na alma"] = min(2.4 * d, 1.2 * lf_w) * tw * fu * c / GA2
        # bloco de cisalhamento da chapa (desprezando a excentricidade), NBR 8800:2024 6.5.6 (manual pág. 87)
        Agv = ((N - 1) * self.s + self.e) * t
        Anv = Agv - (N - 0.5) * dn * t
        Agt = self.e_h * t
        Ant = Agt - 0.5 * dn * t
        r["bloco de cisalhamento da chapa"] = bloco_cisalhamento(Agv, Anv, Ant, fyc, fuc)
        # bloco de cisalhamento da alma (manual pág. 88): Agt = 2·(g − 1,0)·tw, g = ec
        Agvw = (N - 1) * self.s * tw
        Anvw = Agvw - (N - 1) * dn * tw
        Agtw = 2 * (self.ec - 1.0) * tw
        Antw = Agtw - dn * tw
        r["bloco de cisalhamento da alma"] = bloco_cisalhamento(Agvw, Anvw, Antw, fy, fu)
        r["cisalhamento da chapa"] = cisalhamento_chapa(L * t, (L - N * dn) * t, fyc, fuc)   # 6.5.5
        r["cisalhamento da alma"] = cisalhamento_chapa(self.H * tw, (self.H - N * dn) * tw, fy, fu)
        W, Wn = self._W()
        r["flexão da chapa (escoamento)"] = fyc * W / GA1 / self.ec                        # manual pág. 88
        r["flexão da chapa (ruptura)"] = fuc * Wn / GA2 / self.ec
        Rw = min(41.14 * L * self.b_solda / GA2, 30.0 * L * self.b_solda / GA1)          # NBR 8800:2024 6.2.5.1
        r["solda"] = Rw
        self.detalhes = r
        return min(r.values())

    def Nd_Rd(self, Vd_max=None):
        """caso 2 (manual pág. 89): Nd,max = 0,25·Vd,max com Vd = 0,5·Vd,max; confere a chapa sob M + N e a solda
        (50% para Vd e 50% para Nd). Retorna (Nd, Vd, verificações)."""
        Vd_max = Vd_max if Vd_max is not None else self.Vd_Rd()
        fyc, fuc = ACOS[self.aco_ch]
        d = DIAMETROS[self.diam]
        dn = furo_padrao(d) + 0.2
        Vd, Nd = 0.5 * Vd_max, 0.25 * Vd_max
        W, Wn = self._W()
        L, t = self.L_c, self.t_c
        chk = {"chapa, escoamento": (fyc / GA1 - Vd * self.ec / W) * L * t,
               "chapa, ruptura": (fuc / GA2 - Vd * self.ec / Wn) * (L - self.np_ * dn) * t,
               "solda (50%)": 0.5 * min(41.14 * L * self.b_solda / GA2, 30.0 * L * self.b_solda / GA1)}
        return Nd, Vd, chk

    def disposicoes(self):
        """limitações do manual pág. 85/89: t ≥ max(6,3 mm; Lc/64) (8 mm com 6 parafusos), t ≤ d/2 + 2 mm."""
        d = DIAMETROS[self.diam]
        nc = []
        tmin = max(0.63 if self.np_ <= 5 else 0.8, self.L_c / 64)
        if self.t_c < tmin - 1e-9:
            nc.append(f"t = {self.t_c} < tmin = {tmin:.2f} cm")
        if self.t_c > d / 2 + 0.2 + 1e-9:
            nc.append(f"t = {self.t_c} > d/2 + 0,2 = {d / 2 + 0.2:.2f} cm")
        return nc


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


# ------------------------------------------------------------------ chapa de cabeça parafusada assimétrica (LMPA), cap. 6
FW_E70 = 48.5          # kN/cm², eletrodo E70XX (manual 2.3)


def _flm_forca_mesa(bf, tf, d, fy, E=20000.0, sigma_r_frac=0.3):
    """força resistente da mesa comprimida pelo estado-limite FLM (NBR 8800:2024 anexo de flexão), considerando só as
    mesas resistindo ao momento (manual pág. 104): Cpl = bf·tf·fy/γa1; Cr = 0,7·fy·W_mesas/(d − tf)/γa1 com
    W_mesas = bf·tf·(d − tf)²/d; λp = 0,38√(E/fy), λr = 0,83√(E/(0,7fy)). Mesa esbelta → erro (fora do manual)."""
    lam = bf / (2 * tf)
    lp = 0.38 * math.sqrt(E / fy)
    lr = 0.83 * math.sqrt(E / ((1 - sigma_r_frac) * fy))
    Cpl = bf * tf * fy / GA1
    if lam <= lp:
        return Cpl
    Cr = (1 - sigma_r_frac) * fy * bf * tf * (d - tf) / d / GA1
    if lam <= lr:
        return Cpl - (Cpl - Cr) * (lam - lp) / (lr - lp)
    raise ValueError(f"mesa esbelta (bf/2tf = {lam:.1f} > λr = {lr:.1f}): fora do campo do manual")


@dataclass
class LMPA:
    """ligação rígida com chapa de cabeça parafusada assimétrica (LMPA, cap. 6, págs. 101–104): momento sempre
    tracionando os parafusos superiores. Caso 2: 6 parafusos (4 tracionados: 2 acima e 2 abaixo da mesa superior,
    2 na mesa inferior), dimensões e1, e3, e4, e5. Caso 1: 12 parafusos (8 tracionados), e1 a e5.
    Soldas: bsf (mesas) e bsw (alma) = perna do filete em cm; 0 = penetração total. Chapa A36, perfil A572-50.
    Para inversão de momento, a ligação deve ser simétrica (repetir o detalhe superior embaixo).
    Hipótese do manual (descoberta na reprodução das tabelas, págs. 105–126): na interação tração-corte dos parafusos
    o manual usa Fv,Rd multiplicado por 0,75 (corte calculado com 0,75·Ab) — fator_corte = 0,75; com 1,0 (texto da
    pág. 103) o momento resistente sobe até ~4%."""
    perfil: str
    diam: str = "1"
    tc: float = 3.15
    caso: int = 2
    e1: float = 5.5
    e2: float = 6.0
    e3: float = 11.0
    e4: float = 4.5
    e5: float = 4.5
    bsf: float = 0.0
    bsw: float = 0.0
    aco_ch: str = "A36"
    aco_viga: str = "A572-50"
    fub: float = 83.0
    fator_corte: float = 0.75
    detalhes: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.caso not in (1, 2):
            raise ValueError("LMPA: caso 1 (12 parafusos) ou 2 (6 parafusos)")
        self.p_ = dados_perfil(self.perfil)

    @property
    def np_(self):
        return 12 if self.caso == 1 else 6

    def largura_tributaria(self):
        db = DIAMETROS[self.diam]
        lim = self.e5 + 0.5 * db
        if self.caso == 2:                                   # manual pág. 103
            return min(self.e1, lim) + min(self.e3 / 2, lim)
        p1 = min(self.e1, lim) + min(self.e2 / 2, lim)
        p2 = min(self.e2 / 2, lim) + min(self.e3 / 2, lim)
        return min(p1, p2)

    def disposicoes(self):
        """disposições construtivas do manual pág. 103 (lista de não conformidades)."""
        db = DIAMETROS[self.diam]
        P, tc, nc = self.p_, self.tc, []
        lim14 = min(15.0, 12 * tc)
        for nome, v in (("e1", self.e1), ("e4", self.e4)):
            if not (1.75 * db - 1e-9 <= v <= lim14 + 1e-9):
                nc.append(f"{nome} = {v} fora de [1,75db; min(15; 12tc)]")
        lim23 = min(18.0, 14 * tc)
        pares = (("e2", self.e2), ("e3", self.e3)) if self.caso == 1 else (("e3", self.e3),)
        for nome, v in pares:
            if not (3 * db - 1e-9 <= v <= lim23 + 1e-9):
                nc.append(f"{nome} = {v} fora de [3db; min(18; 14tc)]")
        if self.e3 < 2.7 * db + P["tw"] + 2 * (self.bsw or 0.5) - 1e-9:
            nc.append("e3 < 2,7db + tw + 2bsw")
        if self.e5 < 1.35 * db + (self.bsf or 0.5) - 1e-9:
            nc.append("e5 < 1,35db + bsf")
        larg = 2 * self.e1 + self.e3 + (2 * self.e2 if self.caso == 1 else 0)
        if not (P["bf"] + 2.0 - 1e-9 <= larg <= P["bf"] + 2 * db + 1e-9):
            nc.append(f"largura de furação {larg:.1f} fora de [bf + 2 cm; bf + 2db]")
        return nc

    def Md_Rd(self, Nd=0.0, Vd=0.0):
        """momento resistente (kN·m) para Nd (tração +, kN) e Vd (kN) dados (manual págs. 103–104)."""
        P = self.p_
        db = DIAMETROS[self.diam]
        Ab = area_bruta(db)
        fyc, fuc = ACOS[self.aco_ch]
        fy, _ = ACOS[self.aco_viga]
        fw = FW_E70
        r = {}
        # força cortante: limites da alma e da solda da alma (pág. 103)
        r["Vd,max alma"] = P["d_linha"] * P["tw"] * 0.6 * fy / GA1
        if self.bsw:
            r["Vd,max solda da alma"] = 2 * 0.7 * self.bsw * P["d_linha"] * 0.6 * fw / GA2
        if Vd > min(v for k, v in r.items() if k.startswith("Vd,max")) + 1e-9:
            raise ValueError(f"Vd = {Vd} kN acima do limite da alma/solda {r}")
        # parafusos: interação tração + corte (NBR 8800:2024 6.3.3.4)
        FvSd = Vd / self.np_
        FvRd = 0.45 * self.fub * Ab / GA2 * self.fator_corte
        FtRd = 0.75 * self.fub * Ab / GA2
        F1 = FtRd * math.sqrt(max(0.0, 1 - (FvSd / FvRd) ** 2))
        # flexão da chapa de cabeça e efeito alavanca (pág. 104), α = 1
        p = self.largura_tributaria()
        dh = db + 0.32
        b = self.e5
        MRd = p * self.tc ** 2 / 4 * fyc / GA1
        delta = min((p - dh) * (fuc / GA2) / (p * fyc / GA1), 1.0)
        F2 = (delta * MRd + MRd) / b
        FfSd = min(F1, F2)
        r.update({"F't,Sd (tração+corte)": F1, "F''t,Sd (alavanca)": F2, "p": p, "delta": delta})
        # força de tração máxima na mesa (pág. 104)
        TS = {"parafusos": self.np_ / 1.5 * FfSd, "mesa": P["bf"] * P["tf"] * fy / GA1}
        CI = {"FLM": _flm_forca_mesa(P["bf"], P["tf"], P["d"], fy)}
        if self.bsf:
            Rw = 2 * 0.7 * self.bsf * P["bf"] * 0.6 * fw / GA2
            TS["solda da mesa"] = Rw
            CI["solda da mesa"] = Rw
        Ts, Ci = min(TS.values()), min(CI.values())
        braco = P["d"] - P["tf"]
        Md = min((Ts - Nd / 2) * braco, (Ci + Nd / 2) * braco) / 100
        if self.caso == 1 and self.diam == "3/4":
            # caso 1 com Ø 3/4": a tabela Gerdau (pág. 125) dá ~4,6% menos que o modelo e a hipótese do manual não foi
            # identificada; reduz 5% para não ficar contra a segurança (DEC-017)
            Md *= 0.95
            r["aviso"] = "LMPA caso 1 Ø3/4\": Md reduzido 5% (tabela Gerdau pág. 125 menor que o modelo; conferir)"
        r.update({"TS": TS, "CI": CI})
        self.detalhes = r
        return Md


# ------------------------------------------------------------------ perfis T laminados (LT) e ligação LMTS, cap. 8
@dataclass
class LT:
    """resistências de um perfil T (cortado de W laminado, TC no centro ou TM fora do centro) bolted ao pilar pela
    mesa (4 parafusos: gabarito G na mesa, espaçamento Y ao longo de Lt) e à mesa da viga pela alma (4 parafusos:
    2 linhas a X, bordas e e espaçamento s ao longo de Ht). Manual cap. 8, págs. 140–143. Perfil A572-50.
    Td = menor de Fr,nf (flexão da mesa com alavanca) e Fr,ny (escoamento da alma do T);
    Cd = menor de Fr,npv (parafusos da alma: corte e contato) e Fr,ny.
    Hipóteses que reproduzem as tabelas LT (págs. 144–163, desvio ≤ 1,1%):
    - Fr,nf usa o braço b1 (furo à face da alma do T), e não b' = b1 − 0,5d como no texto da pág. 142,
      e MRd = p·tf²·fy/4,44 (4/0,9, AISC 13ª ed.); com b' e 4,4 do texto o Td sobe ~35% (contra a segurança),
      por isso o padrão é a forma das tabelas; `braco_texto=True` dá a forma do texto (só para comparação);
    - contato na alma do T: lf = e − (dh + 0,2)/2 em todos os parafusos (como na LCHS)."""
    perfil: str
    Lt: float
    diam: str = "3/4"
    G: float = 8.0
    X: float = 7.5
    Y: float = 8.0
    e: float = 4.0
    s: float = 7.5
    fub: float = 83.0
    braco_texto: bool = False
    detalhes: dict = field(default_factory=dict)

    def __post_init__(self):
        self.p_ = dados_perfil(self.perfil)
        if self.Y >= self.Lt or self.X >= self.Lt:
            raise ValueError("X e Y devem ser menores que Lt")

    def resistencias(self):
        P = self.p_
        db = DIAMETROS[self.diam]
        dh = furo_padrao(db)
        Ab = area_bruta(db)
        fy, fu = ACOS["A572-50"]
        bft, tf, twt = P["bf"], P["tf"], P["tw"]
        Np2 = Np1 = 4
        a = (bft - self.G) / 2                                   # manual pág. 142
        b1 = (bft - twt) / 2 - a
        bl = b1 - 0.5 * db
        dl = db + 0.2
        x = (self.Lt - self.Y) / 2
        p = min(2 * (b1 + 0.5 * db), self.Y / 2 + x, b1 + 0.5 * db + x)
        delta = min((p - dl) * (fu / GA2) / (p * fy / GA1), 1.0)
        if self.braco_texto:
            MRd, braco = p * tf ** 2 * fy / 4.4, bl
        else:
            MRd, braco = p * tf ** 2 * fy / 4.44, b1
        r = {}
        r["Fr,nf (mesa, alavanca)"] = (delta * MRd + MRd) / braco * Np2
        r["Fr,ny (escoamento da alma)"] = fy * self.Lt * twt / GA1                          # NBR 8800:2024 6.5.3.a
        r["Fr,nu (ruptura da alma)"] = fu * (self.Lt - 2 * dl) * twt / GA2                  # NBR 8800:2024 6.5.3.b
        r["Fr,nt (parafusos tracionados)"] = 0.75 * Ab * self.fub / GA2 * 0.67 * Np2       # pág. 143
        lf = min(self.e - (dh + 0.2) / 2, self.s - (dh + 0.2))
        r["Fr,npv (parafusos da alma)"] = min(0.45 * Ab * self.fub * Np1 / GA2,          # NBR 8800:2024 6.3.3.2
                                              min(1.2 * lf, 2.4 * db) * twt * fu * Np1 / GA2)  # 6.3.3.3
        # bloco de cisalhamento da alma do T (NBR 8800:2024 6.5.6): 2 planos de cisalhamento ao longo de Ht
        Agv = 2 * (self.e + self.s) * twt
        Anv = Agv - 2 * 1.5 * dl * twt
        blocos = []
        for Agt_l, nfuros in (((self.Lt - self.X), 1.0), (self.X, 1.0)):   # caso 1: 2 blocos nas pontas; caso 2: central
            Agt = Agt_l * twt
            Ant = Agt - nfuros * dl * twt
            blocos.append(bloco_cisalhamento(Agv, Anv, Ant, fy, fu))
        r["Fr,nd (bloco de cisalhamento)"] = min(blocos)
        Td = min(r["Fr,nf (mesa, alavanca)"], r["Fr,ny (escoamento da alma)"])
        Cd = min(r["Fr,npv (parafusos da alma)"], r["Fr,ny (escoamento da alma)"])
        outros = ("Fr,nu (ruptura da alma)", "Fr,nt (parafusos tracionados)", "Fr,npv (parafusos da alma)",
                  "Fr,nd (bloco de cisalhamento)")
        r["ductilidade (Td < demais)"] = all(Td < r[k] for k in outros)                # pág. 141
        r.update({"p": p, "b1": b1, "delta": delta})
        self.detalhes = r
        return Td, Cd


def lmts_verificar(Md, Nd, Vd, d, Td, Cd, Vd_Rd):
    """condições da LMTS (manual pág. 141): Md/d + Nd/2 ≤ Td e Md/d − Nd/2 ≤ Cd (Md em kN·m, d em cm),
    Vd ≤ Vd,Rd das 2 cantoneiras L102×102×8 (use LCPP(n=2, b_aba=10.16, t_c=0.8, g=6.5, ...)). Retorna (ok, T, C)."""
    T = Md * 100 / d + Nd / 2
    C = Md * 100 / d - Nd / 2
    return (T <= Td and C <= Cd and Vd <= Vd_Rd), T, C


# ------------------------------------------------------------------ elemento suporte (pilar): forças localizadas
def verificar_pilar_suporte(perfil_pilar, F_tracao=0.0, F_compressao=0.0, ln=0.0, V_painel=0.0, N_pilar=0.0,
                            aco="A572-50", E=20000.0):
    """forças concentradas das mesas da viga (kN) na mesa/alma do pilar e cisalhamento do painel de alma.
    Fórmulas da NBR 8800:2008 item 5.7 / AISC 360 J10 (o manual Gerdau manda "verificar obrigatoriamente o elemento
    suporte" sem dar as fórmulas) — numeração e coeficientes a conferir na NBR 8800:2024. Forças longe da
    extremidade do pilar (≥ d). ln = comprimento de atuação da força (espessura da mesa da viga + 2·solda), cm.
    Retorna (resistências, enrijecedor_necessario, area_minima_enrijecedor_cm2 por lado)."""
    P = dados_perfil(perfil_pilar)
    fy, _ = ACOS[aco]
    tf, tw, d, h = P["tf"], P["tw"], P["d"], P["d_linha"]
    k = (d - P["h"]) / 2 + tf if P["h"] < d - 2 * tf - 1e-9 else tf   # distância da face externa da mesa ao pé do raio
    k = max(k, tf)
    R = {}
    R["flexão local da mesa (tração)"] = 6.25 * tf ** 2 * fy / GA1                      # 5.7.2
    R["escoamento local da alma"] = 1.10 * (5 * k + ln) * fy * tw / GA1                  # 5.7.3
    R["enrugamento da alma"] = 0.66 * tw ** 2 * (1 + 3 * (ln / d) * (tw / tf) ** 1.5) * math.sqrt(E * fy * tf / tw) / GA1  # 5.7.4
    R["flambagem da alma (compressão)"] = 24 * tw ** 3 * math.sqrt(E * fy) / (h * GA1)  # 5.7.6 (forças opostas)
    Ny = None
    from nd_estruturas.metalica_laminada import perfil as _p
    Ny = _p(perfil_pilar).A * fy
    fat = 1.0 if N_pilar <= 0.4 * Ny else (1.4 - N_pilar / Ny)
    R["painel de alma (cisalhamento)"] = 0.6 * fy * d * tw * fat / GA1                   # AISC J10.6 / NBR 5.7.x
    falta_t = max(0.0, F_tracao - min(R["flexão local da mesa (tração)"], R["escoamento local da alma"]))
    falta_c = max(0.0, F_compressao - min(R["escoamento local da alma"], R["enrugamento da alma"],
                                          R["flambagem da alma (compressão)"]))
    falta = max(falta_t, falta_c)
    enrij = falta > 0
    Ast = falta * GA1 / fy / 2 if enrij else 0.0                 # 2 enrijecedores (um de cada lado da alma)
    painel_ok = V_painel <= R["painel de alma (cisalhamento)"]
    R["painel ok"] = painel_ok
    return R, enrij, Ast
