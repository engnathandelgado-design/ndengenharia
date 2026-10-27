"""Verificação de lançamento — roda sobre o modelo BIM ANTES de qualquer prancha (gate do processo ND).

Por que existe: na Letsara (rev10 a rev12) as decisões de geometria (face externa dos pilares de canto, VM de borda,
P21/P19 da linha 4, largura dos consolos) apareceram uma a uma depois das 86 folhas geradas, e cada uma refez o jogo
inteiro. Estas checagens pegam esses casos no modelo, em segundos, antes do detalhamento.

Checagens (cada uma devolve lista de achados {regra, peca, msg, valor, esperado}):
- alinhamento_fachada: no perímetro com placas por fora, pilares, vigas de borda e consolos com a face externa no
  plano de referência da fachada (regra do Nathan: placas por fora dos pilares, sem fresta).
- largura_consolo: consolo com a mesma largura da viga que ele apoia (largura da face inferior da viga).
- vao_livre: aberturas (portões) com o vão livre face a face do arquitetônico.
- apoio_laje: comprimento de apoio de cada laje alveolar sobre a viga ≥ mínimo adotado.

Unidades: m. Tolerância padrão 5 mm (NBR 9062:2017 item 5.2.2.6: tolerâncias de montagem de ±10 mm ficam para a
obra; o projeto tem de fechar no nominal).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import re

import numpy as np

from .bim import PerfilI, PerfilPoligono

TOL = 0.005


def _contorno(perfil):
    if isinstance(perfil, PerfilPoligono):
        return [tuple(p) for p in perfil.pontos]
    if isinstance(perfil, PerfilI):
        return [(-perfil.b / 2, -perfil.h / 2), (perfil.b / 2, -perfil.h / 2), (perfil.b / 2, perfil.h / 2), (-perfil.b / 2, perfil.h / 2)]
    return [(-perfil.b / 2, -perfil.h / 2), (perfil.b / 2, -perfil.h / 2), (perfil.b / 2, perfil.h / 2), (-perfil.b / 2, perfil.h / 2)]


def _secao_mundo(p, s=0.0):
    """pontos do contorno da seção (perfil real) na posição s (m) ao longo do eixo da peça, em coordenadas globais."""
    M = np.array(p.matriz(), float)
    return np.array([(M @ np.array([u, v, s, 1.0]))[:3] for u, v in _contorno(p.perfil)])


def caixa(p):
    """caixa alinhada aos eixos globais (xmin, xmax, ymin, ymax, zmin, zmax)."""
    pts = np.vstack([_secao_mundo(p, 0.0), _secao_mundo(p, p.comprimento)])
    return (pts[:, 0].min(), pts[:, 0].max(), pts[:, 1].min(), pts[:, 1].max(), pts[:, 2].min(), pts[:, 2].max())


def _eixo_longo(c):
    dx, dy = c[1] - c[0], c[3] - c[2]
    return 0 if dx >= dy else 1


@dataclass
class Fachada:
    """plano de referência da fachada: face externa dos pilares, onde as placas encostam por fora.
    eixo 0 = plano x = valor; eixo 1 = plano y = valor. lado = +1 se o lado de fora é o de coordenada maior.
    trecho = (min, max) ao longo da fachada em que o plano vale (None = inteiro)."""
    nome: str
    eixo: int
    valor: float
    lado: int
    trecho: tuple | None = None


@dataclass
class Abertura:
    nome: str
    eixo: int            # direção do vão (0 = vão medido em x)
    linha: float         # coordenada da linha de pilares no outro eixo
    centro: float        # coordenada aproximada do meio da abertura
    vao: float           # vão livre face a face exigido (arquitetônico)


@dataclass
class ConfigLancamento:
    fachadas: list = field(default_factory=list)
    aberturas: list = field(default_factory=list)
    grupos_pilar: tuple = ("Pilares",)
    grupos_viga_borda: tuple = ()          # vigas que correm ao longo da fachada e encostam nas placas
    grupos_consolo: tuple = ("Consolos",)
    grupos_viga: tuple = ()                # vigas apoiadas em consolo (largura do consolo = largura da viga)
    grupos_laje: tuple = ()
    apoio_min_laje: float = 0.08
    faixa: float = 0.15                    # distância máxima ao plano para a peça contar como "de fachada"
    ignorar: tuple = ()                    # trechos de marca a não checar (com motivo registrado em DECISIONS)
    contagem: dict = field(default_factory=dict)   # quantos pares foram de fato conferidos (prova de que a checagem não passou vazia)


def _achado(regra, p, msg, valor=None, esperado=None):
    return dict(regra=regra, peca=p.marca if p is not None else "", msg=msg,
                valor=None if valor is None else round(float(valor), 4), esperado=None if esperado is None else round(float(esperado), 4))


def alinhamento_fachada(pecas, cfg: ConfigLancamento):
    out = []
    grupos = set(cfg.grupos_pilar) | set(cfg.grupos_viga_borda) | set(cfg.grupos_consolo)
    for p in pecas:
        if p.grupo not in grupos or any(k in p.marca for k in cfg.ignorar):
            continue
        c = caixa(p)
        for f in cfg.fachadas:
            lo, hi = (c[0], c[1]) if f.eixo == 0 else (c[2], c[3])
            ext = hi if f.lado > 0 else lo
            dist = (f.valor - ext) * f.lado                      # > 0: face recuada para dentro; < 0: sai para fora do plano
            if not (-cfg.faixa < dist < cfg.faixa):
                continue
            o = 1 - f.eixo
            a0, a1 = (c[0], c[1]) if o == 0 else (c[2], c[3])
            if f.trecho and (a1 < f.trecho[0] - 0.01 or a0 > f.trecho[1] + 0.01):
                continue
            if p.grupo in cfg.grupos_viga_borda and _eixo_longo(c) != o:
                continue                                         # viga perpendicular à fachada: não é de borda
            cfg.contagem["peças de fachada"] = cfg.contagem.get("peças de fachada", 0) + 1
            if abs(dist) > TOL:
                out.append(_achado("alinhamento_fachada", p, f"{p.grupo}: face externa {'recuada' if dist > 0 else 'para fora'} "
                                   f"{abs(dist) * 100:.1f} cm do plano da fachada {f.nome} (fresta com as placas)", ext, f.valor))
    return out


def _largura_inferior(p, transv):
    s = np.vstack([_secao_mundo(p, 0.0), _secao_mundo(p, p.comprimento)])
    zmin = s[:, 2].min()
    base = s[s[:, 2] <= zmin + 0.002]
    return base[:, transv].max() - base[:, transv].min()


def _marca_base(m):
    return re.sub(r" (dente|corpo|nariz|ponta)\b.*$", "", m)


def largura_consolo(pecas, cfg: ConfigLancamento):
    out = []
    vigas = [(p, caixa(p)) for p in pecas if p.grupo in cfg.grupos_viga and not any(k in p.marca for k in cfg.ignorar)]
    consolos = [(p, caixa(p)) for p in pecas if p.grupo in cfg.grupos_consolo and not any(k in p.marca for k in cfg.ignorar)]
    larg = {}
    for v, cv in vigas:                                   # largura da viga = a da peça inteira (dente/nariz não contam)
        b = _marca_base(v.marca)
        larg[b] = max(larg.get(b, 0.0), _largura_inferior(v, 1 - _eixo_longo(cv)))
    for v, cv in vigas:
        ax = _eixo_longo(cv)
        tr = 1 - ax
        lv = larg[_marca_base(v.marca)]
        for k, ck in consolos:
            if not (cv[4] - 0.05 <= ck[5] <= cv[4] + 0.01):     # topo do consolo logo abaixo do fundo da peça (neoprene)
                continue
            a = (ck[0], ck[1]) if ax == 0 else (ck[2], ck[3])
            t = (ck[0], ck[1]) if tr == 0 else (ck[2], ck[3])
            av = (cv[0], cv[1]) if ax == 0 else (cv[2], cv[3])
            tv = (cv[0], cv[1]) if tr == 0 else (cv[2], cv[3])
            if a[1] < av[0] - 0.05 or a[0] > av[1] + 0.05 or t[1] <= tv[0] + 0.01 or t[0] >= tv[1] - 0.01:
                continue
            lk = t[1] - t[0]
            cfg.contagem["consolo×viga"] = cfg.contagem.get("consolo×viga", 0) + 1
            if abs(lk - lv) > TOL:
                out.append(_achado("largura_consolo", k, f"consolo {k.marca} com {lk * 100:.1f} cm sob a viga {v.marca} de "
                                   f"{lv * 100:.1f} cm (consolo tem a largura da viga)", lk, lv))
    return out


def vao_livre(pecas, cfg: ConfigLancamento):
    out = []
    pil = [(p, caixa(p)) for p in pecas if p.grupo in cfg.grupos_pilar]
    for ab in cfg.aberturas:
        o = 1 - ab.eixo
        na = [(p, c) for p, c in pil if (c[0] if o == 0 else c[2]) - 0.35 <= ab.linha <= (c[1] if o == 0 else c[3]) + 0.35]
        esq = [(c[1] if ab.eixo == 0 else c[3], p) for p, c in na if (c[1] if ab.eixo == 0 else c[3]) < ab.centro]
        dir_ = [(c[0] if ab.eixo == 0 else c[2], p) for p, c in na if (c[0] if ab.eixo == 0 else c[2]) > ab.centro]
        if not esq or not dir_:
            out.append(_achado("vao_livre", None, f"abertura {ab.nome}: pilares de um dos lados não encontrados"))
            continue
        (fa, pa), (fb, pb) = max(esq, key=lambda t: t[0]), min(dir_, key=lambda t: t[0])
        cfg.contagem["aberturas"] = cfg.contagem.get("aberturas", 0) + 1
        if abs((fb - fa) - ab.vao) > TOL:
            out.append(_achado("vao_livre", pa, f"abertura {ab.nome} entre {pa.marca} e {pb.marca}: vão livre "
                               f"{(fb - fa):.3f} m, arquitetônico {ab.vao:.3f} m", fb - fa, ab.vao))
    return out


def _juntar_lajes(pecas, grupos):
    """a laje com recorte é modelada em trechos (ponta, corpo, ponta): junta os trechos da mesma marca que se tocam."""
    itens = [(p, list(caixa(p))) for p in pecas if p.grupo in grupos]
    pai = list(range(len(itens)))

    def raiz(i):
        while pai[i] != i:
            pai[i] = pai[pai[i]]
            i = pai[i]
        return i

    for i, (pi, a) in enumerate(itens):
        for j in range(i + 1, len(itens)):
            pj, b = itens[j]
            if pi.marca != pj.marca:
                continue
            gap = [max(a[2 * k], b[2 * k]) - min(a[2 * k + 1], b[2 * k + 1]) for k in range(3)]
            k0 = int(np.argmax(gap))                     # eixo de contato
            la = max(a[1] - a[0], a[3] - a[2]); lb = max(b[1] - b[0], b[3] - b[2])
            g = a if la >= lb else b                     # trecho maior (corpo) dá a direção do vão
            longo = 0 if g[1] - g[0] >= g[3] - g[2] else 1
            if max(gap) <= 0.003 and sorted(gap)[1] < -0.01 and k0 == longo:
                pai[raiz(i)] = raiz(j)
    grupos_ = {}
    for i, (p, c) in enumerate(itens):
        r = raiz(i)
        if r in grupos_:
            g = grupos_[r][1]
            grupos_[r] = (grupos_[r][0], [min(g[k], c[k]) if k % 2 == 0 else max(g[k], c[k]) for k in range(6)])
        else:
            grupos_[r] = (p, c)
    return list(grupos_.values())


def apoio_laje(pecas, cfg: ConfigLancamento):
    out = []
    lajes = _juntar_lajes(pecas, cfg.grupos_laje)
    apoios = [(p, caixa(p)) for p in pecas if p.grupo in cfg.grupos_viga or p.grupo in cfg.grupos_viga_borda]
    for l, cl in lajes:
        ax = _eixo_longo(cl)
        tr = 1 - ax
        for ponta in (0, 1):
            melhor = 0.0
            for v, cv in apoios:
                if abs(cv[5] - cl[4]) > 0.03:
                    continue
                t = max(0.0, min(cl[2 * tr + 1], cv[2 * tr + 1]) - max(cl[2 * tr], cv[2 * tr]))
                if t <= 0.01:
                    continue
                if ponta == 0:
                    ap = min(cl[2 * ax + 1], cv[2 * ax + 1]) - cl[2 * ax]
                else:
                    ap = cl[2 * ax + 1] - max(cl[2 * ax], cv[2 * ax])
                if ap > (cl[2 * ax + 1] - cl[2 * ax]) / 2:
                    continue
                melhor = max(melhor, ap)
            cfg.contagem["pontas de laje"] = cfg.contagem.get("pontas de laje", 0) + 1
            if melhor < cfg.apoio_min_laje - 0.001:
                out.append(_achado("apoio_laje", l, f"laje {l.marca}, ponta {'inicial' if ponta == 0 else 'final'}: apoio "
                                   f"{melhor * 100:.1f} cm sobre a viga (mínimo {cfg.apoio_min_laje * 100:.0f} cm)", melhor, cfg.apoio_min_laje))
    return out


def verificar(pecas, cfg: ConfigLancamento):
    """roda todas as checagens; devolve lista de achados (vazia = lançamento liberado para o detalhamento)."""
    return (alinhamento_fachada(pecas, cfg) + largura_consolo(pecas, cfg) + vao_livre(pecas, cfg) + apoio_laje(pecas, cfg))
