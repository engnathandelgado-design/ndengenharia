"""Viga contínua por elementos finitos (Euler-Bernoulli, rigidez direta) com EI variável ao longo do eixo.

Uso típico: terça contínua por transpasse (trecho do transpasse com 2 perfis = 2·EI), vigas de vários vãos.
Unidades: kN, m, kN·m; carga distribuída w (kN/m, positiva para baixo) por vão; apoios simples verticais.
Sinal de saída: M positivo traciona a fibra inferior; deslocamento positivo para baixo.
"""
from __future__ import annotations
import numpy as np


def analisar(vaos, EI, w, n_div=40, EI_trechos=None):
    """vaos: lista de comprimentos (m); EI (kN·m²) da seção simples; w: kN/m uniforme ou lista por vão.
    EI_trechos: lista de (x_ini, x_fim, fator) em coordenada global — EI multiplicado pelo fator nesses trechos.
    Retorna dict com x, M, V, deslocamento (m), reações (kN, para cima) e posição dos apoios."""
    vaos = list(vaos)
    ws = list(w) if hasattr(w, "__len__") else [w] * len(vaos)
    xa = np.concatenate([[0.0], np.cumsum(vaos)])
    xs = []
    for i, L in enumerate(vaos):
        xs.extend(np.linspace(xa[i], xa[i + 1], n_div + 1)[:-1])
    pts = sorted(set(np.round(list(xs) + [xa[-1]] + [t for tr in (EI_trechos or []) for t in tr[:2] if 0 < t < xa[-1]], 9)))
    x = np.array(pts)
    ne, nn = len(x) - 1, len(x)
    K = np.zeros((2 * nn, 2 * nn))
    F = np.zeros(2 * nn)
    ele = []
    for e in range(ne):
        a, b = x[e], x[e + 1]
        L = b - a
        xm = (a + b) / 2
        k_ei = EI
        for (t0, t1, fat) in (EI_trechos or []):
            if t0 <= xm <= t1:
                k_ei = EI * fat
        iv = min(int(np.searchsorted(xa, xm) - 1), len(vaos) - 1)
        q = ws[iv]
        k = k_ei / L ** 3 * np.array([[12, 6 * L, -12, 6 * L], [6 * L, 4 * L * L, -6 * L, 2 * L * L],
                                       [-12, -6 * L, 12, -6 * L], [6 * L, 2 * L * L, -6 * L, 4 * L * L]])
        fe = q * np.array([L / 2, L * L / 12, L / 2, -L * L / 12])      # carga para baixo = positiva em v
        dof = [2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3]
        K[np.ix_(dof, dof)] += k
        F[dof] += fe
        ele.append((dof, k, fe, q, L))
    apoio = [int(np.argmin(abs(x - xi))) for xi in xa]
    fix = [2 * n for n in apoio]
    livre = [d for d in range(2 * nn) if d not in fix]
    u = np.zeros(2 * nn)
    u[livre] = np.linalg.solve(K[np.ix_(livre, livre)], F[livre])
    R = K @ u - F
    M = np.zeros(nn)
    V = np.zeros(nn)
    for e, (dof, k, fe, q, L) in enumerate(ele):
        f = k @ u[dof] - fe            # forças nas extremidades do elemento (convenção v para baixo)
        # M que traciona a fibra inferior: M_i = f[1] (início), M_j = −f[3] (fim)
        M[e] = f[1]
        M[e + 1] = -f[3]
        V[e] = f[0]
    return dict(x=x, M=M, V=V, v=u[0::2], reacoes=-R[fix], x_apoios=xa, apoio_idx=apoio)


def envoltoria(res_list):
    M = np.array([r["M"] for r in res_list])
    return M.max(axis=0), M.min(axis=0)
