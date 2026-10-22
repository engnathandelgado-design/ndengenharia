"""Planta-chave padrão das folhas de peça (regra do Nathan, 22/10/2026): cada peça detalhada na folha aparece com
CÍRCULO em volta e LINHA DE CHAMADA com o nome próprio (P1…, V200…), para ficar claro onde ela está.

Uso: chave.planta(pr, origem_papel, esc, nomes=["V407", ...], titulo=..., subtitulo=..., y_max=None)
  - desenha eixos (linhas 1–9 e A–E), contorno dos pilares e, para cada nome, o destaque (Vista.destaque);
  - os rótulos saem para fora da planta (esquerda para peças da metade A–C, direita para C–E), empilhados sem
    sobreposição e fora da altura dos números das linhas.
Coordenadas da obra em m (x = eixos A→E, y = linhas 1→9), do nomes.json."""
import json, math
from geometria import Y_LIN, X_EIXO

PR = "/home/claude/letsara/pranchas/"
_P = {p["nome"]: p for p in json.load(open(PR + "nomes.json", encoding="utf-8"))["pecas"]}
M = lambda v: v * 1000.0
XA, XE = X_EIXO["A"], X_EIXO["E"]


def _alvo(n):
    p = _P[n]
    if p["tipo"] == "pilar":
        return (p["x"], p["y"]), None
    return (p["x0"], p["y0"]), (p["x1"], p["y1"])


def planta(pr, origem, esc, nomes, titulo="PLANTA-CHAVE", subtitulo=None, y_max=None, rotulo=None, dist_lado=9.0, lado_fixo=None, numeros=None):
    """numeros: linhas (1–9) cujo número é escrito; padrão = todas."""
    """rotulo: função nome → texto (ex.: 'V200 / V300' para duas peças na mesma posição); padrão = o próprio nome.
    y_max: corta a planta acima dessa linha (m), p.ex. só as linhas 1–3 do mezanino."""
    y_top = y_max if y_max is not None else Y_LIN[-1]
    lins = [y for y in Y_LIN if y <= y_top + 1e-6]
    kp = pr.vista("PLANTA-CHAVE", origem, esc, titulo=titulo, subtitulo=subtitulo or "círculo e chamada = peças desta folha", unidade="cm")
    for y in lins:
        kp.linha((M(XA - 2), M(y)), (M(XE + 2), M(y)), "EIXO")
        if numeros is None or (Y_LIN.index(y) + 1) in numeros:
            kp.texto((M(XA - 2.6), M(y)), str(Y_LIN.index(y) + 1), "min", "MIDDLE_RIGHT")
    for k, x in X_EIXO.items():
        kp.linha((M(x), M(-2)), (M(x), M(y_top + 2)), "EIXO")
        kp.texto((M(x), M(-2.6)), k, "min", "TOP_CENTER")              # letras dos eixos embaixo (rótulos saem pelos lados)
    for p in _P.values():                                           # pilares de fundo (contorno fino)
        if p["tipo"] == "pilar" and p["y"] <= y_top + 1e-6:
            kp.ret(M(p["x"]) - 200, M(p["y"]) - 200, 400, 400, "VISTA")
    vistos, alvos = set(), []
    for n in nomes:
        a, b = _alvo(n)
        key = (round(a[0], 2), round(a[1], 2), round(b[0], 2) if b else None, round(b[1], 2) if b else None)
        if key in vistos:                                           # mesma posição em outro nível (VM +3,15 / +6,55)
            continue
        vistos.add(key)
        c = a if b is None else ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        alvos.append((n, a, b, c))
    h = 2.5 * 1.6                                                   # passo mínimo entre rótulos (mm de papel)
    y_lin_p = [M(y) / esc for y in lins]
    for lado in (-1, 1):
        if lado_fixo:
            grupo = sorted(alvos, key=lambda t: t[3][1]) if lado == lado_fixo else []
        else:
            grupo = sorted([t for t in alvos if (t[3][0] < (XA + XE) / 2) == (lado < 0)], key=lambda t: t[3][1])
        ocup = []
        for n, a, b, c in grupo:
            ylab = M(c[1]) / esc + 3.0                               # papel, relativo à origem da vista
            ylab = max([ylab] + [o + h for o in ocup])
            while any(abs(ylab - yl) < 2.2 for yl in y_lin_p) or any(abs(ylab - o) < h for o in ocup):
                ylab += 0.8
            ocup.append(ylab)
            xlab = (M(XA) / esc - dist_lado) if lado < 0 else (M(XE) / esc + dist_lado)
            dx, dy = xlab - M(c[0]) / esc, ylab - M(c[1]) / esc
            kp.destaque((M(a[0]), M(a[1])), "\x01" + (rotulo(n) if rotulo else n), (dx, dy), 2.2, p_fim=(M(b[0]), M(b[1])) if b else None)   # \x01: nome já novo (não renomear)
    return kp
