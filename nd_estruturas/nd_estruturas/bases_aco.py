"""Bases de pilares e emendas de pilares em perfis W/HP Gerdau — Manual Gerdau "Ligações para Estruturas
de Aço" (ed. NBR 8800:2024), caps. 9 (EP1/EP2), 10 (PBR) e 11 (PBE).

Unidades (DEC-015): kN, cm, kN/cm² e kN·cm, como o manual. Entradas geométricas de placa e bloco em cm.
fck em MPa (convertido para kN/cm² na entrada). Momentos de saída em kN·m (como as tabelas PBE).
Propriedades de perfil vêm do catálogo de ``metalica_laminada`` (d, bf, tw, tf em mm; A em cm²; Zx em cm³).
Neste módulo a força normal é sempre de compressão e entra positiva (Nd ≥ 0), como no manual.

Materiais (manual 2.3): placa de base e chumbadores ASTM A36 (fy 25, fu 40 kN/cm²); perfil A572 Gr50
(fy 34,5 kN/cm²); concreto fck 20 MPa para chumbador Ø ≤ 7/8" e 25 MPa para 1" ≤ Ø ≤ 1 3/4".

Modelos (o manual só dá as fórmulas de 10.4 e 11.4 e remete à NBR 8800:2024 itens 6.6.5 e 6.7; o
procedimento abaixo foi reconstruído e calibrado contra as tabelas — ver DEC-017 e tests/test_bases_aco.py):

PBR (base rotulada, cap. 10):
  - concreto: σc,Rd = 0,85·fck/γc·√(A2/A1) ≤ 1,7·fck/γc (manual 10.4), A1 = placa, A2 = bloco;
  - flexão da placa: balanço ℓ = máx(m, n, λn') do AISC Design Guide 1 (base "tipo 2"), m = (A − 0,95d)/2,
    n = (B − 0,8bf)/2, n' = √(d·bf)/4 com λ = 1 (limite superior, a favor da segurança),
    σ·ℓ²/2 ≤ (t²/4)·fy/γa1. As tabelas PBR são reproduzidas com t_ef = t − 0,5 mm (calibração, DEC-017);
  - solda de filete opcional (perfil × placa);
  - força horizontal resistente = 10 % de Nd (manual 10.1.2);
  - Há um modo de falha das tabelas PBR (placas pouco maiores que o perfil, p.ex. HP 310 em placa 350×350)
    que NÃO foi identificado: nesses casos o cálculo dá até ~60 % acima da tabela. Por isso
    ``verificar_pbr`` limita NRd ao valor tabelado quando o detalhe existe na tabela (dados/pbr_gerdau.csv)
    e emite aviso quando o detalhe não é tabelado.

PBE (base engastada, cap. 11): método do AISC Design Guide 1 (bloco retangular de tensões):
  - excentricidade pequena (e ≤ A/2 − N/(2q), q = σc,Rd·B): Y = A − 2e, σ = N/(B·Y), sem tração;
  - excentricidade grande: σ = σc,Rd, Y = (f + A/2) − √((f + A/2)² − 2(M + N·f)/q), T = q·Y − N;
  - placa comprimida: σ·m²/2 (Y ≥ m) ou σ·Y·(m − Y/2) (Y < m) ≤ t²/4·fy/γa1, com m = (A − 0,95d)/2 sem
    tração nos chumbadores e m = (A − d)/2 com tração (calibração, DEC-017);
  - placa tracionada: T·x ≤ B·t²/4·fy/γa1, x = f − d/2 + tf/2; chumbadores: T ≤ n·0,75·Ab·fu/γa2;
  - pilar (manual 11.2): interação 5.5.1.2 com NRd = A·fy/1,1 e MRd = Zx·fy/1,1;
  - força horizontal resistente = 10 % de Nd (manual 11.1).

EP1/EP2 (cap. 9): o manual só traz emendas SOLDADAS (penetração total) com cantoneira de posicionamento
parafusada. Regra da ND: ligações de campo parafusadas. ``emenda_ep`` seleciona o detalhe do manual
(só para referência, com aviso) e ``EmendaPilarParafusada`` verifica a alternativa parafusada com talas.

(conferir) = item da NBR 8800:2024 citado pelo manual cujo texto não foi conferido na norma.
"""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from nd_estruturas.ligacoes_aco import ACOS, DIAMETROS, GA1, GA2, Fv_Rd, emenda_tala
from nd_estruturas.metalica_laminada import Perfil
from nd_estruturas.metalica_laminada import perfil as _perfil

NORMA = "NBR8800:2024"
GC = 1.4                                  # γc (NBR 8800:2024 tab. 3; manual 10.4)
FY_A572 = 34.5                            # kN/cm², perfis Gerdau
FY_PLACA, FU_PLACA = ACOS["A36"]          # 25 / 40 kN/cm²
FU_CHUMB = 40.0                           # chumbador ASTM A36
FW_E70 = 48.5                             # kN/cm², eletrodo E70XX
GW2 = 1.35                                # γw2 metal da solda
POL = 2.54
CHUMBADORES = {"5/8": 5 / 8, "3/4": 3 / 4, "7/8": 7 / 8, "1": 1.0, "1 1/4": 1.25, "1 1/2": 1.5, "1 3/4": 1.75}
FURO_PLACA = {"3/4": 3.3, "1": 4.5, "1 1/4": 5.0, "1 1/2": 6.0}   # cm, notas 6 das tabelas PBR/PBE
T_EF_PBR = 0.05                           # cm, redução de espessura que reproduz as tabelas PBR (DEC-017)
_CSV_PBR = Path(__file__).with_name("dados") / "pbr_gerdau.csv"


def _p(perf: Perfil | str) -> Perfil:
    return _perfil(perf) if isinstance(perf, str) else perf


# ------------------------------------------------------------------ concreto e chumbadores
def fck_minimo(diam_chumbador: str) -> float:
    """fck mínimo (MPa) do bloco conforme o diâmetro do chumbador (manual 2.3)."""
    return 20.0 if CHUMBADORES[diam_chumbador] <= 7 / 8 else 25.0


def sigma_c_Rd(fck: float, A1: float, A2: float) -> float:
    """pressão resistente no concreto (kN/cm²): 0,85·fck/γc·√(A2/A1) ≤ 1,7·fck/γc.
    Manual Gerdau 10.4 / NBR 8800:2024 item 6.6.5 (conferir). fck em MPa; A1, A2 em cm² (A2 ≥ A1)."""
    if fck < 20 or fck > 90:
        raise ValueError(f"fck = {fck} MPa fora da faixa 20–90 MPa")
    if A2 < A1:
        raise ValueError("A2 (bloco) deve ser ≥ A1 (placa)")
    f = fck / 10.0
    return min(0.85 * f / GC * math.sqrt(A2 / A1), 1.7 * f / GC)


def area_chumbador(diam: str) -> float:
    return math.pi * (CHUMBADORES[diam] * POL) ** 2 / 4


def Ft_Rd_chumbador(diam: str, fu: float = FU_CHUMB) -> float:
    """tração no chumbador: 0,75·Ab·fu/γa2 (NBR 8800:2024 6.3.3.1, como parafuso; manual 12.2.1.4)."""
    return 0.75 * area_chumbador(diam) * fu / GA2


def Fv_Rd_chumbador(diam: str, fu: float = FU_CHUMB) -> float:
    """corte no chumbador com rosca no plano: 0,45·Ab·fu/γa2 (manual 12.2.1.4)."""
    return Fv_Rd(CHUMBADORES[diam] * POL, fub=fu)


def ancoragem_minima(diam: str) -> dict:
    """embutimento mínimo 12·db e distância mínima à borda do bloco 5·db (manual 11.4, AISC DG1). cm."""
    db = CHUMBADORES[diam] * POL
    return {"embutimento_min": 12 * db, "borda_min": 5 * db}


def m_placa(t: float, fy: float = FY_PLACA) -> float:
    """momento plástico resistente da placa por unidade de largura (kN·cm/cm): t²/4·fy/γa1."""
    return t * t / 4 * fy / GA1


# ------------------------------------------------------------------ geometria
@dataclass(frozen=True)
class Placa:
    """placa de base A (paralela à alma, direção de d) × B (direção de bf) × t, em cm. Aço A36."""
    A: float
    B: float
    t: float
    fy: float = FY_PLACA

    def __post_init__(self):
        if min(self.A, self.B, self.t) <= 0:
            raise ValueError("dimensões da placa devem ser positivas")


@dataclass(frozen=True)
class Bloco:
    """bloco de fundação em planta (cm) e fck (MPa)."""
    A: float
    B: float
    fck: float

    def __post_init__(self):
        if self.fck < 20 or self.fck > 90:
            raise ValueError(f"fck = {self.fck} MPa fora da faixa 20–90 MPa")


@dataclass(frozen=True)
class Chumbadores:
    """chumbadores ASTM A36: diâmetro ('3/4' … '1 3/4'), n por lado tracionado (PBE: 2), distância f do eixo do
    pilar à linha de chumbadores (cm, direção de d) e total de chumbadores na base."""
    diam: str = "1"
    n_lado: int = 2
    f: float = 0.0
    n_total: int = 4

    def __post_init__(self):
        if self.diam not in CHUMBADORES:
            raise ValueError(f"chumbador '{self.diam}' não cadastrado: {sorted(CHUMBADORES)}")


def _sol_filete(p: Perfil, a_mesa: float, a_alma: float) -> float:
    """resistência (kN) dos filetes perfil × placa, cordões dos dois lados de mesas e alma:
    0,6·fw·(0,7a)·L/γw2 (NBR 8800:2024 tab. 8). a em cm."""
    bf, tw, d, tf = p.bf / 10, p.tw / 10, p.d / 10, p.tf / 10
    L_mesa = 2 * (bf + bf - tw)
    L_alma = 2 * (d - 2 * tf)
    q = lambda a: 0.6 * FW_E70 * 0.7 * a / GW2
    return q(a_mesa) * L_mesa + q(a_alma) * L_alma


# ------------------------------------------------------------------ PBR
@lru_cache(maxsize=1)
def _tabela_pbr() -> list[dict]:
    with open(_CSV_PBR, newline="", encoding="utf-8") as fh:
        return [dict(r) for r in csv.DictReader(fh)]


def pbr_tabela(perf: str | None = None) -> list[dict]:
    """linhas das tabelas PBR (págs. 181–207) em mm/kN; filtra pelo nome do perfil se dado."""
    rows = _tabela_pbr()
    if perf is None:
        return list(rows)
    nome = _p(perf).nome
    return [r for r in rows if _norm(r["perfil"]) == _norm(nome)]


def _norm(s: str) -> str:
    return s.upper().replace(" ", "").replace("(H)", "")


def _pbr_tabelado(p: Perfil, placa: Placa) -> float | None:
    for r in pbr_tabela(p.nome):
        if (abs(float(r["A_pb_mm"]) - placa.A * 10) < 0.5 and abs(float(r["B_pb_mm"]) - placa.B * 10) < 0.5
                and abs(float(r["t_pb_mm"]) - placa.t * 10) < 0.05):
            return float(r["Nd_max_kN"])
    return None


@dataclass
class ResultadoBase:
    resistencias: dict
    governante: str
    valor: float
    avisos: list = field(default_factory=list)


def pbr_NRd(perf: Perfil | str, placa: Placa, bloco: Bloco, solda_mm: tuple | None = None,
            usar_tabela: bool = True, reducao_t: float = T_EF_PBR) -> ResultadoBase:
    """força normal de compressão resistente (kN) da base rotulada PBR.
    solda_mm = (a_mesa, a_alma) em mm para filetes; None = penetração total (não verifica).
    reducao_t: redução de espessura (cm) da calibração com as tabelas (0 = AISC DG1 puro)."""
    p = _p(perf)
    d, bf = p.d / 10, p.bf / 10
    A1, A2 = placa.A * placa.B, bloco.A * bloco.B
    sc = sigma_c_Rd(bloco.fck, A1, A2)
    r = {"concreto": sc * A1}
    m = (placa.A - 0.95 * d) / 2          # AISC DG1 eq. 3.3.? (balanços m, n, n')
    n = (placa.B - 0.8 * bf) / 2
    n_l = math.sqrt(d * bf) / 4            # λ = 1
    ell = max(m, n, n_l)
    te = placa.t - reducao_t
    r["flexão da placa"] = te * te * placa.fy / (2 * GA1 * ell * ell) * A1   # σ·ℓ²/2 = t²/4·fy/γa1
    if solda_mm:
        r["solda de filete"] = _sol_filete(p, solda_mm[0] / 10, solda_mm[1] / 10)
    av = []
    if usar_tabela:
        nt = _pbr_tabelado(p, placa)
        if nt is not None:
            r["tabela Gerdau PBR"] = nt
        else:
            av.append("detalhe não tabelado no manual: o modo de falha das placas pouco maiores que o perfil "
                      "não foi identificado (DEC-017); conferir com a tabela PBR mais próxima")
    gov = min(r, key=r.get)
    return ResultadoBase(r, gov, r[gov], av)


def verificar_pbr(perf: Perfil | str, Nd: float, placa: Placa, bloco: Bloco, chumb: Chumbadores,
                  Vd: float = 0.0, solda_mm: tuple | None = None, altura_chumbador: float | None = None,
                  usar_tabela: bool = True) -> dict:
    """verificação completa da base rotulada: Nd ≤ NRd, Vd ≤ 0,10·Nd (manual 10.1.2), fck mínimo do chumbador,
    embutimento e borda mínimos. Retorna dict com razões (≤ 1 passa) e avisos."""
    if Nd < 0:
        raise ValueError("Nd é compressão e entra positiva neste módulo")
    res = pbr_NRd(perf, placa, bloco, solda_mm, usar_tabela)
    out = {"NRd": res.valor, "governante": res.governante, "detalhes": res.resistencias,
           "Nd/NRd": Nd / res.valor, "Vd/(0,1Nd)": (Vd / (0.1 * Nd)) if Nd > 0 else (math.inf if Vd else 0.0),
           "avisos": list(res.avisos)}
    if bloco.fck < fck_minimo(chumb.diam):
        out["avisos"].append(f"fck {bloco.fck} < {fck_minimo(chumb.diam)} MPa exigido para Ø{chumb.diam}\"")
    anc = ancoragem_minima(chumb.diam)
    if altura_chumbador is not None and altura_chumbador < anc["embutimento_min"]:
        out["avisos"].append(f"embutimento {altura_chumbador:.1f} < 12db = {anc['embutimento_min']:.1f} cm")
    folga = min(bloco.A - placa.A, bloco.B - placa.B) / 2
    if folga < anc["borda_min"]:
        out["avisos"].append(f"distância placa–borda do bloco {folga:.1f} cm < 5db = {anc['borda_min']:.1f} cm")
    return out


# ------------------------------------------------------------------ PBE
@dataclass
class BasePBE:
    """base engastada (manual cap. 11): perfil, placa, bloco e chumbadores (f = distância eixo–linha de
    chumbadores, cm). m_tracao: 'face' (m = (A − d)/2 com chumbadores tracionados, calibração DEC-017) ou
    '0.95d' (AISC DG1 puro, a favor da segurança)."""
    perfil: Perfil | str
    placa: Placa
    bloco: Bloco
    chumb: Chumbadores
    m_tracao: str = "face"
    fy_perfil: float = FY_A572

    def __post_init__(self):
        self.p = _p(self.perfil)
        if self.chumb.f <= self.p.d / 20:
            raise ValueError("f (eixo → chumbadores) deve ficar fora da mesa do pilar")
        if self.m_tracao not in ("face", "0.95d"):
            raise ValueError("m_tracao: 'face' ou '0.95d'")

    # propriedades auxiliares (cm, kN)
    @property
    def sigma_c(self) -> float:
        return sigma_c_Rd(self.bloco.fck, self.placa.A * self.placa.B, self.bloco.A * self.bloco.B)

    @property
    def mp(self) -> float:
        return m_placa(self.placa.t, self.placa.fy)

    def analisar(self, Nd: float, Md_kNm: float) -> dict:
        """distribuição de tensões (AISC DG1) e razões solicitante/resistente para (Nd, Md). Nd em kN (compr.),
        Md em kN·m. Retorna dict com Y (cm), σ (kN/cm²), T (kN, total na linha tracionada) e razões."""
        A, B, f = self.placa.A, self.placa.B, self.chumb.f
        d, tf = self.p.d / 10, self.p.tf / 10
        M = abs(Md_kNm) * 100.0
        q = self.sigma_c * B
        if Nd > 0 and M / Nd <= A / 2 - Nd / (2 * q):           # pequena excentricidade
            e = M / Nd
            Y, T = A - 2 * e, 0.0
            sig = Nd / (B * Y)
        else:                                                   # grande excentricidade
            k = f + A / 2
            disc = k * k - 2 * (M + Nd * f) / q
            if disc < 0:
                return {"Y": None, "sigma": None, "T": None, "razoes": {"equilíbrio (concreto/chumbadores)": math.inf}}
            Y = k - math.sqrt(disc)
            sig, T = self.sigma_c, q * Y - Nd
        m = (A - (1.0 if (T > 0 and self.m_tracao == "face") else 0.95) * d) / 2
        mc = sig * m * m / 2 if Y >= m else sig * Y * (m - Y / 2)
        raz = {"concreto": sig / self.sigma_c, "placa (lado comprimido)": mc / self.mp}
        if T > 0:
            x = f - d / 2 + tf / 2
            raz["placa (lado tracionado)"] = T * x / (B * self.mp)
            raz["chumbadores (tração)"] = T / (self.chumb.n_lado * Ft_Rd_chumbador(self.chumb.diam))
        raz["pilar 5.5.1.2"] = self._interacao_pilar(Nd, M)
        return {"Y": Y, "sigma": sig, "T": T, "razoes": raz}

    def _interacao_pilar(self, Nd: float, M: float) -> float:
        """NBR 8800:2024 5.5.1.2 (conferir numeração) na seção junto à base, NRd = A·fy/1,1, MRd = Zx·fy/1,1."""
        NRd = self.p.A * self.fy_perfil / GA1
        MRd = self.p.Zx * self.fy_perfil / GA1
        r = Nd / NRd
        return r + 8 / 9 * M / MRd if r >= 0.2 else r / 2 + M / MRd

    def Md_max(self, Nd: float) -> float:
        """momento resistente máximo (kN·m) para Nd (tabelas PBE). Bisseção sobre M."""
        def ok(M):
            return max(self.analisar(Nd, M)["razoes"].values()) <= 1.0 + 1e-9
        if not ok(0.0):
            return 0.0
        lo, hi = 0.0, 10.0
        while ok(hi):
            hi *= 2
            if hi > 1e6:
                break
        for _ in range(60):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if ok(mid) else (lo, mid)
        return lo

    def verificar(self, Nd: float, Md_kNm: float, Vd: float = 0.0, altura_chumbador: float | None = None) -> dict:
        """verificação completa: razões da análise, Vd ≤ 0,10·Nd (manual 11.1), fck, ancoragem e disposição
        (distância transversal entre chumbadores ≤ bf: manual 11.1.1 — conferir no desenho)."""
        a = self.analisar(Nd, Md_kNm)
        raz = dict(a["razoes"])
        raz["cortante (0,1 Nd)"] = Vd / (0.1 * Nd) if Nd > 0 else (math.inf if Vd else 0.0)
        av = []
        if self.bloco.fck < fck_minimo(self.chumb.diam):
            av.append(f"fck {self.bloco.fck} < {fck_minimo(self.chumb.diam)} MPa exigido para Ø{self.chumb.diam}\"")
        anc = ancoragem_minima(self.chumb.diam)
        if altura_chumbador is not None and altura_chumbador < anc["embutimento_min"]:
            av.append(f"embutimento {altura_chumbador:.1f} < 12db = {anc['embutimento_min']:.1f} cm")
        gov = max(raz, key=raz.get)
        return {"Y": a["Y"], "sigma": a["sigma"], "T": a["T"], "razoes": raz, "governante": gov,
                "passa": raz[gov] <= 1.0, "avisos": av}


# ------------------------------------------------------------------ emendas EP1/EP2 (cap. 9)
EP2_CHAPA = {  # (série superior, série inferior) -> tcht (mm); "W200(demais)" e afins pela regra do manual
    ("W 150", "W 200"): 37.5,
    ("W 200 x 86,0", "W 250"): 50.0, ("W 200 x 100,0", "W 250"): 50.0, ("W 200", "W 250"): 37.5,
    ("W 200 x 86,0", "HP 250"): 50.0, ("W 200 x 100,0", "HP 250"): 50.0, ("W 200", "HP 250"): 37.5,
    ("HP 200", "W 250"): 37.5, ("HP 200", "HP 250"): 37.5,
    ("W 310", "W 360"): 50.0, ("HP 310", "W 360"): 50.0,
    ("W 360", "W 410"): 50.0, ("W 410", "W 460"): 50.0,
}


def _serie(p: Perfil) -> tuple[str, int]:
    fam, alt = p.nome.split(" x ")[0].split()
    return fam, int(alt)


def emenda_ep(inferior: Perfil | str, superior: Perfil | str) -> dict:
    """seleciona o detalhe EP1/EP2 do manual (cap. 9, págs. 170–178). Condições 9.1.2: bfi ≥ bfs, tfi ≥ tfs e
    twi ≥ tws; EP1 se as distâncias internas entre mesas h são iguais, EP2 se as alturas nominais diferem ≤ 50 mm.
    Detalhe do manual = solda de penetração total + cantoneira L102×102×9,5 parafusada (só posicionamento)."""
    pi, ps = _p(inferior), _p(superior)
    nc = []
    if pi.bf < ps.bf:
        nc.append("bf inferior < bf superior")
    if pi.tf < ps.tf:
        nc.append("tf inferior < tf superior")
    if pi.tw < ps.tw:
        nc.append("tw inferior < tw superior")
    (fi, hi), (fs, hs) = _serie(pi), _serie(ps)
    h_int_i, h_int_s = pi.d - 2 * pi.tf, ps.d - 2 * ps.tf
    paraf = "4 Ø 5/8\" A325N" if hs == 150 else "4 Ø 3/4\" A325N"
    base = {"cantoneira": "L 102×102×9,5 (gabarito 65 mm)", "parafusos": paraf, "eletrodo": "E70XX",
            "aviso": "emenda do manual SOLDADA (penetração total): contraria a regra ND de ligações de campo "
                     "parafusadas — usar EmendaPilarParafusada", "nao_conformidades": nc}
    if hi == hs:   # mesma série nominal: mesma h entre faces internas (catálogo Gerdau)
        base["h_interno_mm"] = (h_int_i, h_int_s)
        return {"tipo": "EP1", "chapa": "CH 12,5 ASTM A36", **base}
    if 0 < hi - hs <= 50:
        inf_key = f"{fi} {hi}"
        t = EP2_CHAPA.get((ps.nome, inf_key), EP2_CHAPA.get((f"{fs} {hs}", inf_key)))
        if t is None:
            t = 37.5 if hs <= 200 else 50.0          # regra 9.1.1
        return {"tipo": "EP2", "chapa_topo_mm": t, **base}
    nc.append("alturas nominais diferem mais de 50 mm ou o inferior é menor: fora das tabelas EP")
    return {"tipo": None, **base}


@dataclass
class EmendaPilarParafusada:
    """emenda de pilar W por talas parafusadas (alternativa ND às EP1/EP2 soldadas). Talas externas nas mesas
    (1 plano de corte) e duplas na alma (2 planos). Esforços na emenda: Nd (compressão +), Md (kN·m), Vd (kN).
    Força por mesa: Ff = Md/(d − tf) ± N·Af/A; com contato usinado (contato=True) a compressão passa por contato
    e as talas recebem só a tração líquida (Ff,t = Md/(d − tf) − N·Af/A ≥ 0) — prática do AISC 16ª ed.
    (J1.4) e da NBR 8800:2024 (emendas de pilares por contato — conferir item). Unidades: cm, kN."""
    perfil: Perfil | str
    diam_mesa: str = "7/8"
    n_paraf_mesa: int = 8                 # por lado da emenda, por mesa
    t_tala_mesa: float = 1.25
    b_tala_mesa: float | None = None      # padrão: bf do perfil
    diam_alma: str = "3/4"
    n_paraf_alma: int = 4                 # por lado da emenda
    t_tala_alma: float = 0.8
    contato: bool = True
    s: float = 7.5
    e: float = 4.0

    def verificar(self, Nd: float, Md_kNm: float, Vd: float) -> dict:
        p = _p(self.perfil)
        d, bf, tf = p.d / 10, p.bf / 10, p.tf / 10
        Af = bf * tf
        M = abs(Md_kNm) * 100
        Fm = M / (d - tf)
        Fn = Nd * Af / p.A
        Ff = max(Fm - Fn, 0.0) if self.contato else Fm + abs(Fn)
        b_tala = self.b_tala_mesa or bf
        FRd, det, _ = emenda_tala(Ff, self.diam_mesa, self.n_paraf_mesa, 1, self.t_tala_mesa, b_tala, tf,
                                  s=self.s, e=self.e)
        if not self.contato:   # tala comprimida: escoamento da área bruta (placa curta, sem flambagem)
            det["compressão na tala"] = b_tala * self.t_tala_mesa * FY_PLACA / GA1
            FRd = min(det.values())
        VRd = self.n_paraf_alma * Fv_Rd(DIAMETROS[self.diam_alma], planos=2)
        return {"Ff": Ff, "FRd_mesa": FRd, "Ff/FRd": Ff / FRd if FRd else math.inf, "detalhes_mesa": det,
                "VRd_alma": VRd, "Vd/VRd": Vd / VRd}
