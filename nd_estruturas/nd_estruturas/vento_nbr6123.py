"""Vento em edificações — NBR 6123:1988 (coeficientes a conferir na revisão vigente; marcados "conferir").

Funções puras (kN, m):
  - fator S2 (Tabela 1/2) e pressão dinâmica q(z) = 0,613·Vk² (item 4.2);
  - Cpe das paredes de planta retangular (Tabela 4), com as zonas A1/A2, B1/B2, C1/C2, D1/D2;
  - Cpe da cobertura de duas águas / plana com θ ≤ 5° (Tabela 5) por faixa, e a faixa local de borda;
  - Cpi por compartimento (item 6.2.5): permeabilidade uniforme, duas faces opostas permeáveis e abertura dominante;
  - excentricidade da força de arrasto (item 6.6).
Convenção: α = 0° → vento paralelo ao lado maior a (incide na face menor b, faces C barlavento / D sotavento);
α = 90° → vento perpendicular a a (face A barlavento, B sotavento).
"""
from __future__ import annotations
import math

# NBR 6123:1988 Tabela 1 — parâmetros meteorológicos (b, p) por categoria e classe; Fr da categoria II
_S2 = {"I": {"A": (1.10, 0.06), "B": (1.11, 0.065), "C": (1.12, 0.07)},
       "II": {"A": (1.00, 0.085), "B": (1.00, 0.09), "C": (1.00, 0.10)},
       "III": {"A": (0.94, 0.10), "B": (0.94, 0.105), "C": (0.93, 0.115)},
       "IV": {"A": (0.86, 0.12), "B": (0.85, 0.125), "C": (0.84, 0.135)},
       "V": {"A": (0.74, 0.15), "B": (0.73, 0.16), "C": (0.71, 0.175)}}
_FR = {"A": 1.00, "B": 0.98, "C": 0.95}


def S2(z, categoria="III", classe="C"):
    """NBR 6123:1988 item 5.3.3: S2 = b·Fr·(z/10)^p."""
    b, p = _S2[categoria][classe]
    return b * _FR[classe] * (max(z, 0.0) / 10.0) ** p


def q(z, V0, S1=1.0, S3=1.0, categoria="III", classe="C"):
    """Pressão dinâmica (kN/m²), item 4.2: Vk = V0·S1·S2·S3; q = 0,613·Vk²."""
    Vk = V0 * S1 * S2(z, categoria, classe) * S3
    return 0.613 * Vk ** 2 / 1000.0


def _interp(x, x0, x1, y0, y1):
    if x <= x0:
        return y0
    if x >= x1:
        return y1
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


# NBR 6123:1988 Tabela 4 — paredes, planta retangular (valores para h/b ≤ 1/2 e 1/2 < h/b ≤ 3/2) — conferir
_T4 = {
    "baixo": {1.5: dict(a0=dict(A1=-0.8, A2=-0.5, C=0.7, D=-0.4), a90=dict(A=0.7, B=-0.4, C1=-0.8, C2=-0.4), medio=-0.9),
              2.0: dict(a0=dict(A1=-0.8, A2=-0.4, C=0.7, D=-0.3), a90=dict(A=0.7, B=-0.5, C1=-0.9, C2=-0.5), medio=-1.0)},
    "medio": {1.5: dict(a0=dict(A1=-0.9, A2=-0.5, C=0.7, D=-0.5), a90=dict(A=0.7, B=-0.5, C1=-0.9, C2=-0.5), medio=-1.1),
              2.0: dict(a0=dict(A1=-0.9, A2=-0.5, C=0.7, D=-0.3), a90=dict(A=0.7, B=-0.6, C1=-0.9, C2=-0.5), medio=-1.1)},
}


def cpe_paredes(h, a, b):
    """Cpe médios das paredes (Tabela 4). a ≥ b (lados em planta), h = altura. Retorna dict com as zonas para
    α = 0° e 90°, a extensão das zonas 1 (m) e o Cpe médio local. Interpola em a/b entre 1,5 e 2."""
    if a < b:
        a, b = b, a
    linha = _T4["baixo" if h / b <= 0.5 else "medio"]
    r = a / b
    t = _interp(r, 1.5, 2.0, 0.0, 1.0)
    out = {}
    for k in ("a0", "a90"):
        out[k] = {z: round(linha[1.5][k][z] * (1 - t) + linha[2.0][k][z] * t, 3) for z in linha[1.5][k]}
    out["medio_local"] = round(linha[1.5]["medio"] * (1 - t) + linha[2.0]["medio"] * t, 3)
    out["zona1_alfa0"] = min(max(b / 3, a / 4), 2 * h)        # A1/B1 (Fig. da Tabela 4) — conferir
    out["zona1_alfa90"] = min(max(b / 3, a / 4), 2 * h)       # C1/D1 — conferir
    return out


def cpe_cobertura(h, b, theta_graus=0.0):
    """Cobertura de duas águas ou plana, θ ≤ 5° (Tabela 5, h/b ≤ 1/2) — conferir. Faixa de barlavento de
    profundidade b/2 (α = 90°: EF; α = 0°: EG) e restante (GH / FH); faixa local de borda com largura
    min(h, 0,15·b)."""
    if theta_graus > 5:
        raise ValueError("cpe_cobertura: só θ ≤ 5° implementado")
    alto = h / b > 0.5
    return dict(barlavento=-0.8, sotavento=-0.6 if alto else -0.4, profundidade_barlavento=b / 2,
                local=-1.4, largura_local=min(h, 0.15 * b), obs="Tabela 5, θ ≤ 5° (conferir valores locais −1,4 / −2,0 nos cantos)")


def cpi_uniforme():
    """6.2.5 b: quatro faces igualmente permeáveis → Cpi = −0,3 ou 0 (o mais nocivo)."""
    return (-0.3, 0.0)


def cpi_duas_faces(vento_normal_as_permeaveis: bool):
    """6.2.5 a: duas faces opostas igualmente permeáveis, as outras impermeáveis."""
    return 0.2 if vento_normal_as_permeaveis else -0.3


def cpi_abertura_dominante(razao, posicao, cpe_face=None):
    """6.2.5 c: abertura dominante. razao = área da abertura dominante / área das demais aberturas.
    posicao: 'barlavento' (Cpi de +0,1 a +0,8), 'sotavento' ou 'paralela' (Cpi = Cpe da face no local)."""
    if posicao == "barlavento":
        pts = [(1.0, 0.1), (1.5, 0.3), (2.0, 0.5), (3.0, 0.6), (6.0, 0.8)]
        if razao <= 1.0:
            return 0.1
        for (r0, c0), (r1, c1) in zip(pts[:-1], pts[1:]):
            if razao <= r1:
                return round(_interp(razao, r0, r1, c0, c1), 3)
        return 0.8
    if cpe_face is None:
        raise ValueError("cpi_abertura_dominante: informe o Cpe da face (sotavento / paralela)")
    return cpe_face


def excentricidade(a, b):
    """6.6: e_a = 0,075·a (vento perpendicular a a) e e_b = 0,075·b (vento perpendicular a b)."""
    return 0.075 * a, 0.075 * b
