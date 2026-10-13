"""Perfis laminados W/HP (Gerdau) — verificações da NBR 8800:2024.

Escopo: barras prismáticas de seção I/H duplamente simétrica, laminadas, alma não esbelta.
Aços: ASTM A572 Gr50 (fy 345 / fu 450 MPa, padrão Gerdau) e ASTM A36 (250 / 400 MPa).

Unidades
--------
- Entrada e saída: kN, m, kN·m (convenção do pacote). Tensões de material em MPa só na
  definição do aço.
- Propriedades de seção no catálogo (``dados/perfis_w_gerdau.csv``) nas unidades do catálogo
  Gerdau: d, bf, tw, tf, h, d' em mm; A em cm²; I em cm⁴; W, Z em cm³; r em cm; It em cm⁴;
  Cw em cm⁶; massa em kg/m; u em m²/m. Os cálculos internos são feitos em kN e cm.
- Sinal da força normal: compressão negativa, tração positiva.

Referências de item
-------------------
A numeração segue a NBR 8800:2024 onde ela foi conferida na própria "Tabela de Vãos e Cargas
Gerdau" (6ª ed., que cita a edição 2024): item 5.3.5 (Ne), 5.4.3 (cortante), Tabela D.1 e notas
D.2.5 (momento fletor, antigo Anexo G de 2008), Anexo E (viga de alma esbelta, antigo Anexo H),
Tabela B.1 (deslocamentos, antiga Tabela C.1). Os demais itens (5.2 tração, 5.3.3 χ, fator Q,
5.4.2.3 Cb, 5.5.1.2 interação) mantêm o texto da 2008; a letra/número exatos na 2024 estão
marcados "(conferir numeração 2024)".

Divergência conhecida da Tabela Gerdau: a tabela de bitolas (MRd FLM) usa σr = 0,3·fy (NBR
8800:2024), mas as tabelas TVPA foram geradas com σr = 70 MPa (valor da edição 2008). Por isso
``tvpa`` aceita ``sigma_r`` e os testes de reprodução da TVPA usam 70 MPa. Ver DECISIONS/testes.
"""
from __future__ import annotations

import csv
import math
import re
from dataclasses import dataclass, fields
from functools import lru_cache
from pathlib import Path

# ------------------------------------------------------------------ constantes (NBR 8800:2024)
# TODO: migrar para o registro de normas ("NBR8800:2024") quando ele existir (TASKS.md).
NORMA = "NBR8800:2024"
E_ACO = 20_000.0          # kN/cm² (200 000 MPa) — NBR 8800:2024 item 4.5.2.9
G_ACO = 7_700.0           # kN/cm² (77 000 MPa)
GAMA_A1 = 1.10            # escoamento, flambagem e instabilidade — NBR 8800:2024 Tabela 3
GAMA_A2 = 1.35            # ruptura — NBR 8800:2024 Tabela 3
G_GRAV = 9.80665          # m/s², peso próprio a partir da massa linear
FATOR_ASD_GERDAU = 1.50   # fator das tabelas Gerdau (resistência de cálculo / 1,5 = "admissível")

ACOS = {  # nome: (fy, fu) em MPa
    "A572-50": (345.0, 450.0),
    "A36": (250.0, 400.0),
}
_ALIAS_ACO = {"ASTMA572GR50": "A572-50", "A572GR50": "A572-50", "A572": "A572-50", "A57250": "A572-50",
              "ASTMA36": "A36", "A36": "A36"}

_CSV = Path(__file__).with_name("dados") / "perfis_w_gerdau.csv"


def aco(nome: str = "A572-50") -> tuple[float, float]:
    """(fy, fu) em kN/cm² para o aço indicado ('A572-50' ou 'A36'). Aço desconhecido gera erro."""
    chave = re.sub(r"[\s\-_.]", "", nome.upper())
    chave = _ALIAS_ACO.get(chave, nome if nome in ACOS else None)
    if chave not in ACOS:
        raise ValueError(f"aço '{nome}' não cadastrado; use um de {sorted(ACOS)}")
    fy, fu = ACOS[chave]
    return fy / 10.0, fu / 10.0


# ------------------------------------------------------------------ catálogo
@dataclass(frozen=True)
class Perfil:
    """Perfil laminado W/HP do catálogo Gerdau (unidades do catálogo, ver docstring do módulo)."""
    nome: str
    familia: str
    massa: float
    d: float
    bf: float
    tw: float
    tf: float
    h: float
    d_linha: float
    A: float
    Ix: float
    Wx: float
    rx: float
    Zx: float
    Iy: float
    Wy: float
    ry: float
    Zy: float
    rt: float
    It: float
    Cw: float
    u: float
    formato_H: bool
    sob_encomenda: bool

    @property
    def peso(self) -> float:
        """Peso próprio, kN/m."""
        return self.massa * G_GRAV / 1000.0

    @property
    def r0(self) -> float:
        """Raio de giração polar em relação ao centro de cisalhamento, cm (x0 = y0 = 0)."""
        return math.hypot(self.rx, self.ry)

    @property
    def esbeltez_mesa(self) -> float:
        """bf/(2·tf) — mesa (elemento AL)."""
        return self.bf / (2.0 * self.tf)

    @property
    def esbeltez_alma(self) -> float:
        """d'/tw — alma (elemento AA). d' = altura livre entre os raios de concordância (h da NBR)."""
        return self.d_linha / self.tw


def _chave(nome: str) -> tuple[str, int, float]:
    s = nome.upper().replace("(H)", "").replace("*", "").replace(" ", "").replace(",", ".")
    m = re.fullmatch(r"(W|HP)(\d+)X(\d+(?:\.\d+)?)", s)
    if not m:
        raise ValueError(f"nome de perfil não reconhecido: '{nome}' (ex.: 'W 310 x 32,7', 'W310x32.7')")
    return m.group(1), int(m.group(2)), round(float(m.group(3)), 1)


@lru_cache(maxsize=1)
def _catalogo() -> dict[tuple[str, int, float], Perfil]:
    cat = {}
    nomes_num = {f.name for f in fields(Perfil)} - {"nome", "familia", "formato_H", "sob_encomenda"}
    with open(_CSV, newline="", encoding="utf-8") as fh:
        for lin in csv.DictReader(fh):
            kw = {k: float(v) for k, v in lin.items() if k in nomes_num}
            p = Perfil(nome=lin["nome"], familia=lin["familia"], formato_H=lin["formato_H"] == "sim",
                       sob_encomenda=lin["sob_encomenda"] == "sim", **kw)
            cat[_chave(p.nome)] = p
    return cat


def perfil(nome: str) -> Perfil:
    """Busca o perfil no catálogo Gerdau. Aceita 'W 310 x 32,7', 'W310x32.7', 'HP 250 x 62,0 (H)'."""
    k = _chave(nome)
    try:
        return _catalogo()[k]
    except KeyError:
        raise KeyError(f"perfil '{nome}' não está no catálogo Gerdau ({len(_catalogo())} perfis)") from None


def listar_perfis(familia: str | None = None) -> list[str]:
    """Nomes do catálogo, na ordem do arquivo (opcionalmente só 'W' ou 'HP')."""
    return [p.nome for p in _catalogo().values() if familia is None or p.familia == familia.upper()]


# ------------------------------------------------------------------ flexão (Tabela D.1)
@dataclass
class ResultadoFlexao:
    MRd: float            # kN·m (menor dos estados-limite, já limitado a 1,5·W·fy/γa1)
    MRd_FLT: float
    MRd_FLM: float
    MRd_FLA: float
    governa: str
    classe: str           # 'compacta' | 'semicompacta' | 'esbelta' (FLM/FLA)
    Lp: float             # m
    Lr: float             # m
    Cb: float


def _mn_interp(Mpl, Mr, lam, lp, lr):
    # NBR 8800:2024 Tabela D.1 / D.2.1 — trecho inelástico (interpolação linear entre λp e λr)
    return Mpl - (Mpl - Mr) * (lam - lp) / (lr - lp)


def classificar_secao(p: Perfil, aco_nome: str = "A572-50", sigma_r: float | None = None) -> dict:
    """Classifica a seção à flexão em x (FLM e FLA) — NBR 8800:2024 Tabela D.1.

    Retorna λ, λp, λr de mesa e alma e a classe: compacta (λ ≤ λp nas duas), semicompacta
    (λp < λ ≤ λr) ou esbelta (λ > λr em algum elemento).
    """
    fy, _ = aco(aco_nome)
    sr = 0.3 * fy if sigma_r is None else sigma_r / 10.0
    lm, la = p.esbeltez_mesa, p.esbeltez_alma
    lpm = 0.38 * math.sqrt(E_ACO / fy)           # Tabela D.1, FLM: λp = 0,38·√(E/fy)
    lrm = 0.83 * math.sqrt(E_ACO / (fy - sr))    # Nota D.2.5-f: λr = 0,83·√(E/(fy−σr)) (laminado)
    lpa = 3.76 * math.sqrt(E_ACO / fy)           # Tabela D.1, FLA: λp = 3,76·√(E/fy)
    lra = 5.70 * math.sqrt(E_ACO / fy)           # Tabela D.1, FLA: λr = 5,70·√(E/fy)
    if lm <= lpm and la <= lpa:
        classe = "compacta"
    elif lm <= lrm and la <= lra:
        classe = "semicompacta"
    else:
        classe = "esbelta"
    return {"classe": classe, "mesa": (lm, lpm, lrm), "alma": (la, lpa, lra)}


def momento_resistente(p: Perfil, Lb: float = 0.0, Cb: float = 1.0, aco_nome: str = "A572-50",
                       sigma_r: float | None = None) -> ResultadoFlexao:
    """Momento fletor resistente de cálculo em torno de x — NBR 8800:2024 item 5.4.2 e Anexo D (Tabela D.1).

    Estados-limite FLT (com Cb), FLM e FLA para seção I duplamente simétrica, alma não esbelta.
    - Lb: comprimento destravado da mesa comprimida, m (0 = travamento contínuo).
    - Cb: fator de modificação para diagrama não uniforme (item 5.4.2.3; ver ``fator_cb``).
    - sigma_r: tensão residual, MPa. Padrão 0,3·fy (NBR 8800:2024, Nota D.2.5-e). Use 70 para
      reproduzir as TVPA da Gerdau (ver docstring do módulo).
    Limite superior MRd ≤ 1,5·W·fy/γa1 (item 5.4.2.2). Alma esbelta (λ > 5,70√(E/fy)) → Anexo E,
    não implementado: gera erro.
    """
    if Lb < 0 or Cb <= 0:
        raise ValueError("Lb deve ser ≥ 0 e Cb > 0")
    fy, _ = aco(aco_nome)
    sr = 0.3 * fy if sigma_r is None else sigma_r / 10.0          # Nota D.2.5-e
    cl = classificar_secao(p, aco_nome, sigma_r)
    W, Mpl = p.Wx, p.Zx * fy                                        # kN·cm
    Mr = (fy - sr) * W                                              # Tabela D.1: Mr = (fy − σr)·W (FLT e FLM)
    Mmax = 1.5 * W * fy                                             # item 5.4.2.2

    # --- FLT — Tabela D.1 e Nota D.2.5-a
    lb = Lb * 100.0
    lam = lb / p.ry
    lp = 1.76 * math.sqrt(E_ACO / fy)                               # λp = 1,76·√(E/fy)
    b1 = (fy - sr) * W / (E_ACO * p.It)                             # β1 = (fy − σr)·W/(E·J)
    lr = (1.38 * math.sqrt(p.Iy * p.It) / (p.ry * p.It * b1)
          * math.sqrt(1 + math.sqrt(1 + 27 * p.Cw * b1 ** 2 / p.Iy)))
    if lam <= lp:
        Mn_flt = Mpl
    elif lam <= lr:
        Mn_flt = min(Cb * _mn_interp(Mpl, Mr, lam, lp, lr), Mpl)
    else:
        # Mcr = Cb·π²·E·Iy/Lb² · √(Cw/Iy·(1 + 0,039·J·Lb²/Cw))
        Mcr = Cb * math.pi ** 2 * E_ACO * p.Iy / lb ** 2 * math.sqrt(p.Cw / p.Iy * (1 + 0.039 * p.It * lb ** 2 / p.Cw))
        Mn_flt = min(Mcr, Mpl)

    # --- FLM — Tabela D.1, Nota D.2.5-f (Mcr = 0,69·E·Wc/λ²)
    lm, lpm, lrm = cl["mesa"]
    if lm <= lpm:
        Mn_flm = Mpl
    elif lm <= lrm:
        Mn_flm = _mn_interp(Mpl, Mr, lm, lpm, lrm)
    else:
        Mn_flm = 0.69 * E_ACO * W / lm ** 2

    # --- FLA — Tabela D.1 (Mr = fy·W)
    la, lpa, lra = cl["alma"]
    if la > lra:
        raise ValueError(f"{p.nome}: alma esbelta (h/tw = {la:.1f} > {lra:.1f}) — NBR 8800:2024 Anexo E não implementado")
    Mn_fla = Mpl if la <= lpa else _mn_interp(Mpl, fy * W, la, lpa, lra)

    res = {k: min(v, Mmax) / GAMA_A1 / 100.0 for k, v in (("FLT", Mn_flt), ("FLM", Mn_flm), ("FLA", Mn_fla))}
    gov = min(res, key=res.get)
    return ResultadoFlexao(MRd=res[gov], MRd_FLT=res["FLT"], MRd_FLM=res["FLM"], MRd_FLA=res["FLA"],
                           governa=gov, classe=cl["classe"], Lp=lp * p.ry / 100.0, Lr=lr * p.ry / 100.0, Cb=Cb)


def momento_resistente_y(p: Perfil, aco_nome: str = "A572-50", sigma_r: float | None = None) -> float:
    """Momento resistente de cálculo em torno de y (menor inércia), kN·m — NBR 8800:2024 Tabela D.1.

    Seções I/H fletidas em torno do eixo de menor inércia: só FLM (λr = 0,83√(E/(fy−σr)),
    Mcr = 0,69·E·Wy/λ²), Mpl = Zy·fy ≤ 1,5·Wy·fy.
    """
    fy, _ = aco(aco_nome)
    sr = 0.3 * fy if sigma_r is None else sigma_r / 10.0
    Mpl = p.Zy * fy
    lm, lpm, lrm = classificar_secao(p, aco_nome, sigma_r)["mesa"]
    if lm <= lpm:
        Mn = Mpl
    elif lm <= lrm:
        Mn = _mn_interp(Mpl, (fy - sr) * p.Wy, lm, lpm, lrm)
    else:
        Mn = 0.69 * E_ACO * p.Wy / lm ** 2
    return min(Mn, 1.5 * p.Wy * fy) / GAMA_A1 / 100.0          # item 5.4.2.2: MRd ≤ 1,5·W·fy/γa1


def fator_cb(Mmax: float, MA: float, MB: float, MC: float, Rm: float = 1.0) -> float:
    """Cb = 12,5·Mmax / (2,5·Mmax + 3·MA + 4·MB + 3·MC) · Rm ≤ 3,0 — NBR 8800:2024 item 5.4.2.3
    (conferir numeração 2024). Momentos em valor absoluto: máximo e nos quartos do trecho destravado.
    Rm = 1,0 para seção duplamente simétrica.
    """
    Mmax, MA, MB, MC = (abs(x) for x in (Mmax, MA, MB, MC))
    if Mmax == 0:
        return 1.0
    return min(12.5 * Mmax / (2.5 * Mmax + 3 * MA + 4 * MB + 3 * MC) * Rm, 3.0)


# ------------------------------------------------------------------ cortante (5.4.3)
def cortante_resistente(p: Perfil, a: float | None = None, aco_nome: str = "A572-50") -> float:
    """Força cortante resistente de cálculo na direção da alma, kN — NBR 8800:2024 item 5.4.3.1.

    - a: distância entre enrijecedores transversais, m (None = sem enrijecedores, kv = 5,0).
      kv = 5 + 5/(a/h)²; kv = 5,0 se a/h > 3 ou a/h > [260/(h/tw)]².
    - λ = h/tw (h = d', altura livre), λp = 1,10√(kv·E/fy), λr = 1,37√(kv·E/fy).
    - Vpl = 0,60·Aw·fy, Aw = d·tw.
      λ ≤ λp: Vpl/γa1;  λp < λ ≤ λr: (λp/λ)·Vpl/γa1;  λ > λr: 1,24·(λp/λ)²·Vpl/γa1.
    """
    fy, _ = aco(aco_nome)
    h = p.d_linha / 10.0                      # cm
    lam = p.esbeltez_alma
    kv = 5.0
    if a is not None:
        if a <= 0:
            raise ValueError("a deve ser > 0")
        ah = a * 100.0 / h
        if ah <= 3.0 and ah <= (260.0 / lam) ** 2:
            kv = 5.0 + 5.0 / ah ** 2
    elif lam > 260.0:
        raise ValueError(f"{p.nome}: h/tw > 260 exige enrijecedores (item 5.4.3.1.1)")
    lp = 1.10 * math.sqrt(kv * E_ACO / fy)
    lr = 1.37 * math.sqrt(kv * E_ACO / fy)
    Vpl = 0.60 * (p.d / 10.0) * (p.tw / 10.0) * fy
    if lam <= lp:
        Vn = Vpl
    elif lam <= lr:
        Vn = lp / lam * Vpl
    else:
        Vn = 1.24 * (lp / lam) ** 2 * Vpl
    return Vn / GAMA_A1


# ------------------------------------------------------------------ compressão (5.3)
@dataclass
class ResultadoCompressao:
    NcRd: float           # kN (valor positivo)
    chi: float
    Q: float
    Qs: float
    Qa: float
    lambda0: float
    Ne: float             # kN, menor força de flambagem elástica
    modo: str             # 'x' | 'y' | 'z'
    esbeltez_max: float   # KL/r
    esbeltez_ok: bool     # KL/r ≤ 200 (item 5.3.4)


def fator_chi(lambda0: float) -> float:
    """χ = 0,658^(λ0²) para λ0 ≤ 1,5; χ = 0,877/λ0² para λ0 > 1,5 — NBR 8800:2024 item 5.3.3."""
    return 0.658 ** (lambda0 ** 2) if lambda0 <= 1.5 else 0.877 / lambda0 ** 2


def fator_q(p: Perfil, aco_nome: str = "A572-50", sigma: float | None = None) -> tuple[float, float, float]:
    """(Q, Qs, Qa) — método Q da NBR 8800:2008 (Anexo F), mantido para comparação e para a coluna
    Qs/Qa da tabela de bitolas Gerdau. O cálculo padrão de ``compressao_resistente`` usa
    ``area_efetiva`` (forma da 2024).

    Mesas (AL, grupo 4 — perfis laminados): b/t = bf/(2tf);
      ≤ 0,56√(E/fy): Qs = 1; ≤ 1,03√(E/fy): Qs = 1,415 − 0,74·(b/t)·√(fy/E); senão Qs = 0,69·E/(fy·(b/t)²).
    Alma (AA, grupo 2): b/t = d'/tw; se > 1,49√(E/fy):
      bef = 1,92·t·√(E/σ)·[1 − (ca/(b/t))·√(E/σ)] ≤ b, ca = 0,34; Qa = Aef/Ag.
    - sigma: tensão na alma, kN/cm² (None = fy, a favor da segurança, como a coluna Qa da Tabela Gerdau).
    """
    fy, _ = aco(aco_nome)
    bt = p.esbeltez_mesa
    r = math.sqrt(E_ACO / fy)
    if bt <= 0.56 * r:
        Qs = 1.0
    elif bt <= 1.03 * r:
        Qs = 1.415 - 0.74 * bt / r
    else:
        Qs = 0.69 * E_ACO / (fy * bt ** 2)
    sig = fy if sigma is None else sigma
    bw, tw = p.d_linha / 10.0, p.tw / 10.0
    Qa = 1.0
    if p.esbeltez_alma > 1.49 * r:
        rs = math.sqrt(E_ACO / sig)
        bef = min(1.92 * tw * rs * (1 - 0.34 / p.esbeltez_alma * rs), bw)
        Qa = (p.A - (bw - bef) * tw) / p.A
    return Qs * Qa, Qs, Qa


def _largura_efetiva(b: float, lam: float, lam_r: float, sigma: float, fy: float, c1: float, c2: float) -> float:
    # Largura efetiva de elemento comprimido esbelto (forma da NBR 8800:2024, igual a AISC 360-16 E7):
    # se λ > λr·√(fy/σ): bef = b·(1 − c1·√(σel/σ))·√(σel/σ), σel = (c2·λr/λ)²·fy
    if lam <= lam_r * math.sqrt(fy / sigma):
        return b
    rel = math.sqrt((c2 * lam_r / lam) ** 2 * fy / sigma)
    return b * (1.0 - c1 * rel) * rel


def area_efetiva(p: Perfil, sigma: float, aco_nome: str = "A572-50") -> float:
    """Área efetiva à compressão, cm², sob a tensão σ (kN/cm²) — método de larguras efetivas.

    Alma (AA): λ = d'/tw, λr = 1,49·√(E/fy), c1 = 0,18, c2 = 1,31.
    Mesas (AL, laminado): λ = bf/(2tf), λr = 0,56·√(E/fy), c1 = 0,22, c2 = 1,49 (4 meias-mesas).
    Forma conferida contra a TCPA Gerdau (NBR 8800:2024) para almas esbeltas: desvio ≤ 0,05 %
    (W 410×38,8 e W 610×82,0, eixo y). A TCPA não reduz as mesas (HP 310×79: até 0,9 % a menos
    aqui, a favor da segurança). Numeração do anexo na 2024: conferir.
    """
    fy, _ = aco(aco_nome)
    r = math.sqrt(E_ACO / fy)
    bw, bfh = p.d_linha / 10.0, p.bf / 20.0
    perda_alma = (bw - _largura_efetiva(bw, p.esbeltez_alma, 1.49 * r, sigma, fy, 0.18, 1.31)) * p.tw / 10.0
    perda_mesas = 4.0 * (bfh - _largura_efetiva(bfh, p.esbeltez_mesa, 0.56 * r, sigma, fy, 0.22, 1.49)) * p.tf / 10.0
    return p.A - perda_alma - perda_mesas


def compressao_resistente(p: Perfil, KLx: float, KLy: float, KLz: float | None = None,
                          aco_nome: str = "A572-50", metodo: str = "2024") -> ResultadoCompressao:
    """Força axial de compressão resistente de cálculo, kN — NBR 8800:2024 item 5.3.

    Ne por 5.3.5 (seção duplamente simétrica): Nex = π²EIx/(KLx)², Ney = π²EIy/(KLy)²,
    Nez = [π²ECw/(KLz)² + GJ]/r0²; χ por 5.3.3 (``fator_chi``).
    - metodo '2024' (padrão): λ0 = √(Ag·fy/Ne), NcRd = χ·Aef·fy/γa1, Aef por larguras efetivas
      com σ = χ·fy (``area_efetiva``). É o que reproduz a TCPA Gerdau (NBR 8800:2024).
    - metodo '2008': NcRd = χ·Q·Ag·fy/γa1, λ0 = √(Q·Ag·fy/Ne), Q = Qs·Qa (``fator_q``, σ = fy).
    - KLx, KLy, KLz: comprimentos de flambagem, m (KLz padrão = max(KLx, KLy)).
    - Retorna também KL/r máximo e o limite 200 (item 5.3.4).
    """
    if min(KLx, KLy) <= 0 or (KLz is not None and KLz <= 0):
        raise ValueError("comprimentos de flambagem devem ser > 0")
    fy, _ = aco(aco_nome)
    KLz = max(KLx, KLy) if KLz is None else KLz
    lx, ly, lz = KLx * 100, KLy * 100, KLz * 100
    Ne = {"x": math.pi ** 2 * E_ACO * p.Ix / lx ** 2,                                   # 5.3.5 a)
          "y": math.pi ** 2 * E_ACO * p.Iy / ly ** 2,                                   # 5.3.5 b)
          "z": (math.pi ** 2 * E_ACO * p.Cw / lz ** 2 + G_ACO * p.It) / p.r0 ** 2}      # 5.3.5 c)
    modo = min(Ne, key=Ne.get)
    esb = max(lx / p.rx, ly / p.ry)
    if metodo == "2024":
        lam0 = math.sqrt(p.A * fy / Ne[modo])
        chi = fator_chi(lam0)
        Q = area_efetiva(p, chi * fy, aco_nome) / p.A
        NcRd = chi * Q * p.A * fy / GAMA_A1
        Qs = Qa = float("nan")
    elif metodo == "2008":
        Q, Qs, Qa = fator_q(p, aco_nome)
        lam0 = math.sqrt(Q * p.A * fy / Ne[modo])
        chi = fator_chi(lam0)
        NcRd = chi * Q * p.A * fy / GAMA_A1
    else:
        raise ValueError("metodo deve ser '2024' ou '2008'")
    return ResultadoCompressao(NcRd=NcRd, chi=chi, Q=Q, Qs=Qs, Qa=Qa, lambda0=lam0, Ne=Ne[modo], modo=modo,
                               esbeltez_max=esb, esbeltez_ok=esb <= 200.0)


# ------------------------------------------------------------------ tração (5.2)
def tracao_resistente(p: Perfil, An: float | None = None, Ct: float = 1.0, aco_nome: str = "A572-50") -> float:
    """Força axial de tração resistente de cálculo, kN — NBR 8800:2024 item 5.2.2.

    NtRd = min(Ag·fy/γa1 ; Ae·fu/γa2), Ae = Ct·An (item 5.2.3). An em cm² (None = Ag, sem furos).
    """
    if not 0 < Ct <= 1.0:
        raise ValueError("Ct deve estar em (0; 1]")
    fy, fu = aco(aco_nome)
    An = p.A if An is None else An
    return min(p.A * fy / GAMA_A1, Ct * An * fu / GAMA_A2)


# ------------------------------------------------------------------ flexo-compressão / flexo-tração (5.5.1.2)
def interacao(NSd: float, MxSd: float, MySd: float, NRd: float, MxRd: float, MyRd: float) -> float:
    """Razão de interação força normal + momentos — NBR 8800:2024 item 5.5.1.2 (conferir numeração
    2024; mesma forma de AISC 360 eq. H1-1a/b).

    NSd/NRd ≥ 0,2:  NSd/NRd + 8/9·(MxSd/MxRd + MySd/MyRd) ≤ 1,0
    NSd/NRd < 0,2:  NSd/(2·NRd) + (MxSd/MxRd + MySd/MyRd) ≤ 1,0
    Valores em módulo; NRd = NcRd (compressão) ou NtRd (tração).
    """
    n = abs(NSd) / NRd
    m = abs(MxSd) / MxRd + (abs(MySd) / MyRd if MySd else 0.0)
    return n + 8.0 / 9.0 * m if n >= 0.2 else n / 2.0 + m


def verificar_barra(p: Perfil, N: float = 0.0, Mx: float = 0.0, My: float = 0.0, Vy: float = 0.0,
                    KLx: float = 1.0, KLy: float = 1.0, KLz: float | None = None, Lb: float = 0.0,
                    Cb: float = 1.0, aco_nome: str = "A572-50", An: float | None = None) -> dict:
    """Verificação completa de barra W/HP sob N (compressão negativa), Mx, My e Vy de cálculo.

    Junta 5.2/5.3 (NRd), 5.4.2 (MxRd, MyRd), 5.4.3 (VRd) e 5.5.1.2 (interação). Retorna dict com
    resistências (kN, kN·m) e razões solicitante/resistente.
    """
    if N < 0:
        rc = compressao_resistente(p, KLx, KLy, KLz, aco_nome)
        NRd, esb_ok = rc.NcRd, rc.esbeltez_ok
    else:
        NRd, esb_ok = tracao_resistente(p, An=An, aco_nome=aco_nome), True
    fx = momento_resistente(p, Lb, Cb, aco_nome)
    MyRd = momento_resistente_y(p, aco_nome)
    VRd = cortante_resistente(p, aco_nome=aco_nome)
    r_int = interacao(N, Mx, My, NRd, fx.MRd, MyRd)
    return {"NRd": NRd, "MxRd": fx.MRd, "MyRd": MyRd, "VRd": VRd, "governa_Mx": fx.governa,
            "razao_interacao": r_int, "razao_cortante": abs(Vy) / VRd, "esbeltez_ok": esb_ok,
            "ok": r_int <= 1.0 and abs(Vy) <= VRd and esb_ok}


# ------------------------------------------------------------------ deslocamentos (Anexo B)
LIMITES_FLECHA = {  # NBR 8800:2024 Tabela B.1 (denominador de L/x)
    "travessa": 250, "terca": 250, "viga_cobertura": 250, "viga_piso": 350,
}


def flecha_biapoiada(p: Perfil, L: float, q: float = 0.0, P: float = 0.0) -> float:
    """Flecha no meio do vão de viga biapoiada, m: 5qL⁴/(384EI) + PL³/(48EI).

    q em kN/m (uniforme), P em kN (concentrada no meio do vão), L em m. Comparar com L/x da
    NBR 8800:2024 Tabela B.1 (``LIMITES_FLECHA``), com ações de serviço.
    """
    Lc, EI = L * 100.0, E_ACO * p.Ix
    return (5 * (q / 100.0) * Lc ** 4 / (384 * EI) + P * Lc ** 3 / (48 * EI)) / 100.0


# ------------------------------------------------------------------ Tabela de Vãos e Cargas Gerdau (TVPA)
CASOS_TVPA = {  # caso: (K do momento, e da flecha, fator do limite de cortante sobre V)
    1: (8.0, 0.013, 2.0),       # TVPA-1: carga uniforme, valor = carga total q·L
    2: (4.0, 0.021, 2.0),       # TVPA-2: uma carga P no meio do vão
    3: (3.0, 0.036, 1.0),       # TVPA-3: duas cargas P nos terços (valor = cada P)
    4: (2.0, 0.050, 1.0 / 1.5),  # TVPA-4: três cargas P nos quartos (valor = cada P)
}


def tvpa(p: Perfil | str, L: float, caso: int = 1, aco_nome: str = "A572-50", Lb: float | None = None,
         Cb: float = 1.0, sigma_r: float | None = None, fator: float = FATOR_ASD_GERDAU) -> float:
    """Carga "admissível" de viga biapoiada no formato da Tabela de Vãos e Cargas Gerdau, kN.

    valor = min( K·(MRd/1,5 − pp·L²/8)/L ; f_V·VRd/1,5 )
    - MRd por ``momento_resistente`` (Tabela D.1; Lb = None → mesa comprimida travada, Lb ≤ Lp e
      Cb = 1, hipótese da tabela), VRd por ``cortante_resistente`` (5.4.3), pp = peso próprio.
    - K e f_V por ``CASOS_TVPA`` (1 = uniforme: valor é a carga total; 2/3/4 = cada carga P).
    - O valor é de serviço (ELU/1,5), com o peso próprio já descontado — confirmado contra a
      tabela (o texto do item 2.4 do PDF diz o contrário; os números seguem esta fórmula).
    - A tabela Gerdau está em tf = kN/10. As TVPA foram geradas com σr = 70 MPa: passe
      sigma_r=70 para reproduzi-las (o padrão é 0,3·fy da NBR 8800:2024).
    - Não verifica flecha: ver ``tvpa_vao_limite_flecha``.
    """
    p = perfil(p) if isinstance(p, str) else p
    if caso not in CASOS_TVPA:
        raise ValueError("caso deve ser 1, 2, 3 ou 4")
    if L <= 0:
        raise ValueError("L deve ser > 0")
    K, _, fv = CASOS_TVPA[caso]
    M = momento_resistente(p, 0.0 if Lb is None else Lb, Cb, aco_nome, sigma_r).MRd / fator
    V = cortante_resistente(p, aco_nome=aco_nome) / fator
    return max(min(K * (M - p.peso * L ** 2 / 8.0) / L, fv * V), 0.0)


def tvpa_vao_limite_flecha(p: Perfil | str, caso: int = 1, limite: int = 350, aco_nome: str = "A572-50",
                           sigma_r: float | None = None, fator: float = FATOR_ASD_GERDAU) -> float:
    """Vão (m) a partir do qual a carga da TVPA (no limite do momento) dá flecha > L/limite.

    Llim = E·Ix/(limite·e·K·MRd_ASD) — coluna "Llim (1/350)" da Tabela Gerdau; para L/250 use
    limite=250 (NBR 8800:2024 Tabela B.1).
    """
    p = perfil(p) if isinstance(p, str) else p
    K, e, _ = CASOS_TVPA[caso]
    M = momento_resistente(p, 0.0, 1.0, aco_nome, sigma_r).MRd / fator * 100.0   # kN·cm
    return E_ACO * p.Ix / (limite * e * K * M) / 100.0
