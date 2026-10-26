"""rev11 (26/10/2026, pedido do Nathan): pé dos pilares nos CORTES — trecho embutido no cálice, cálice em corte, cotas do
embutimento, níveis (fundo do pilar, topo e fundo do cálice) e rótulo "Pxx 40×60 — L = 11,00 m (emb. 1,00)".
Fonte: <marca>_geom.json (L_TOT e z_topo da folha de detalhamento: embutimento = L_TOT − z_topo, fundo do pilar = −emb).
Cálice: fundações (projeto de terceiros) — aqui só a geometria de compatibilização: topo no piso ±0,00, folga de 5 cm em volta
para o graute e 5 cm no fundo para calços de nivelamento e graute (NBR 9062:2017 7.7; conferir no projeto de fundações).
Embutimento × NBR 9062:2017 7.7.2: Lemb = 1,00 m ≥ 1,6 h = 0,96 m (h = 60 cm, interface com chaves, caso mais desfavorável)."""
import json, os, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
import renomear as RN
PR = "/home/claude/letsara/pranchas/"
FOLGA_FUNDO, FOLGA_LAT, PAREDE, LAJE_FUNDO = 50, 50, 200, 250        # mm
f2 = lambda v: f"{v:.2f}".replace(".", ",")


def peca(nome):
    p = next(q for q in RN._D["pecas"] if q["nome"] == nome)
    G = json.load(open(PR + f"{p['marca']}_geom.json"))
    L = G["L_TOT"] / 1000
    emb = round(L - G["z_topo"], 3)
    return dict(nome=nome, marca=p["marca"], secao=p["secao"], L=L, emb=emb, z_fundo=-emb)


def rotulo(nome):
    d = peca(nome)
    return RN.novo(f"{nome} {d['secao']} — L = {f2(d['L'])} m (emb. {f2(d['emb'])})")


def calice(v, xc, b, nome, cotar=False, lado=-1, niveis=False, oculto=False):
    """desenha o cálice em corte em volta do pilar (coordenada horizontal xc, largura b no plano do corte, mm; z = 0 no piso).
    lado: −1 cota à esquerda, +1 à direita."""
    d = peca(nome)
    e = round(d["emb"] * 1000)
    zf, zb = -e - FOLGA_FUNDO, -e - FOLGA_FUNDO - LAJE_FUNDO
    xi0, xi1 = xc - b / 2 - FOLGA_LAT, xc + b / 2 + FOLGA_LAT
    xo0, xo1 = xi0 - PAREDE, xi1 + PAREDE
    pts = [(xo0, 0), (xi0, 0), (xi0, zf), (xi1, zf), (xi1, 0), (xo1, 0), (xo1, zb), (xo0, zb)]
    v.poli(pts, "OCULTA", fechada=True)                                   # cálice (fundações — terceiros)
    cam = "OCULTA" if oculto else "VISTA"                                  # oculto: pilar ao fundo (cálice e pé enterrados, tracejados)
    if not oculto:
        v.hachura(pts, "ANSI31", 0.6, "HACHURA")
        for x0, x1 in ((xi0, xc - b / 2), (xc + b / 2, xi1)):            # graute lateral
            v.hachura([(x0, 0), (x1, 0), (x1, -e), (x0, -e)], "AR-SAND", 0.02, "HACHURA")
        v.hachura([(xi0, -e), (xi1, -e), (xi1, zf), (xi0, zf)], "AR-SAND", 0.02, "HACHURA")
    for xx in (xc - b / 2, xc + b / 2):                                   # trecho embutido do pilar (dentro do cálice)
        v.linha((xx, 0), (xx, -e), cam)
    v.linha((xc - b / 2, -e), (xc + b / 2, -e), cam)                     # fundo do pilar
    if cotar:
        xc_ = (xo0 - 250) if lado < 0 else (xo1 + 250)
        v.cota_v([-e, 0], xc_, 6 * lado, total=False)                     # embutimento (a folga de 5 cm vai na nota de níveis)
    if niveis:
        return dict(z_fundo=-e, z_calice=zf, emb=e)
    return None


def dims(x, y):
    """(bx, by) do pilar na posição da obra (m): x = eixo A→E, y = linha 1→9."""
    sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
    from geometria import PILARES_ESPECIAIS, X_EIXO
    for n_, xx, yy, bx, by in PILARES_ESPECIAIS:
        if abs(xx - x) < 0.05 and abs(yy - y) < 0.05:
            return bx, by
    if abs(x) < 0.05 or abs(x - X_EIXO["E"]) < 0.05:
        return 0.60, 0.40
    return 0.40, 0.60


def pe(v, x_obra, y_obra, h_corte, eixo_corte="x", cotar=False, lado=-1, oculto=False):
    """atalho: cálice em corte do pilar da posição (x_obra, y_obra) num corte cuja coordenada horizontal (mm) é h_corte;
    eixo_corte = 'x' (corte transversal, largura bx) ou 'y' (corte longitudinal, largura by). Devolve o nome do pilar."""
    nome = RN.pilar_em(x_obra, y_obra)
    bx, by = dims(x_obra, y_obra)
    calice(v, h_corte, (bx if eixo_corte == "x" else by) * 1000, nome, cotar=cotar, lado=lado, oculto=oculto)
    return nome
