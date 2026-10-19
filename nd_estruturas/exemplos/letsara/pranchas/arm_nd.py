"""arm_nd.py — desenho de pranchas de ARMADURAS no padrão de entrega de pré-moldados (ref. PCH Três Capões SP301/SP302):
barras "explodidas" em escala ao lado da peça com forma, trechos e rótulo "4 N2 Ø12,5 C/15 C=483"; bolhas de posição;
seções S.x com o estribo desenhado ao lado; TABELA DE FERROS — 1 UNIDADE / — N UNIDADES; RESUMO DO AÇO +10%; PESO TOTAL;
Fck, VOLUME DE CONCRETO e ÁREA DE FÔRMA. Tudo em coordenadas de papel (mm); barras em cm."""
import math
from prancha_nd import Prancha, MASSA_ACO, ALTURAS, _wtext

fd = lambda v: f"{v:g}".replace(".", ",")
f1 = lambda v, d=2: f"{v:.{d}f}".replace(".", ",")


class Arm:
    def __init__(self, pr: Prancha):
        self.pr, self.msp = pr, pr.msp

    # ---------------------------------------------------------------- primitivas (papel)
    def pl(self, pts, lay="ARMADURA", fechada=False):
        return self.msp.add_lwpolyline(pts, close=fechada, dxfattribs={"layer": lay})

    def ln(self, a, b, lay="ARMADURA"):
        return self.msp.add_line(a, b, dxfattribs={"layer": lay})

    def tx(self, x, y, s, h="min", al="BOTTOM_LEFT", rot=0, lay="TEXTO"):
        return self.pr.texto(x, y, s, h, lay, al, rot)

    def circ(self, c, r, lay="INDICACAO"):
        return self.msp.add_circle(c, r, dxfattribs={"layer": lay})

    def disco(self, c, r):
        self.msp.add_circle(c, r, dxfattribs={"layer": "ARM_SECAO"})
        h = self.msp.add_hatch(color=256, dxfattribs={"layer": "ARM_SECAO"})              # rev06e: cor da camada (verde)
        h.paths.add_edge_path().add_arc(c, r, 0, 360)

    def bolha(self, x, y, pos, r=2.6, registrar=True):
        self.circ((x, y), r, "BOLHA")                                                    # rev06e: bolha cinza fina, posição em vermelho (usina)
        self.tx(x, y, pos, 1.5 if len(pos) > 2 else "min", "MIDDLE_CENTER", lay="POSICAO")
        if registrar:
            self.pr.posicoes_desenho.add(pos)

    def bolha_lider(self, alvo, bx, by, pos, r=2.6, registrar=True):
        """bolha em (bx, by) com linha até o ponto da barra."""
        d = math.dist(alvo, (bx, by))
        if d > r:
            ux, uy = (alvo[0] - bx) / d, (alvo[1] - by) / d
            self.ln((bx + ux * r, by + uy * r), alvo, "CHAMADA")
        self.bolha(bx, by, pos, r, registrar)

    def chamada(self, alvo, x1, y1, texto, h="min"):
        lado = 1 if x1 >= alvo[0] else -1
        w = _wtext(texto, ALTURAS[h] if isinstance(h, str) else h)
        self.pl([alvo, (x1, y1), (x1 + lado * (w + 2), y1)], "CHAMADA")
        self.tx(x1 + lado, y1 + 0.6, texto, h, "BOTTOM_LEFT" if lado > 0 else "BOTTOM_RIGHT")

    def titulo(self, x, y, t1, t2=None):
        w = _wtext(t1, ALTURAS["sub"])
        self.tx(x, y, t1, "sub", "BOTTOM_LEFT", lay="TITULO")
        self.ln((x, y - 1.0), (x + w, y - 1.0), "TITULO")
        if t2:
            self.tx(x, y - 4.6, t2, "min")

    def escala_grafica(self, x, y, esc, m=2.0):
        """régua 0 – 0,5 – 1,0 – 2,0 m na escala da vista."""
        L = m * 1000 / esc
        self.ln((x, y), (x + L, y), "CARIMBO")
        for k, v in enumerate((0, 0.5, 1.0, m)):
            xx = x + v * 1000 / esc
            self.ln((xx, y), (xx, y + 1.5), "CARIMBO")
            self.tx(xx, y - 0.6, fd(v), 1.5, "TOP_CENTER")
        self.pl([(x, y + 0.6), (x + 0.5 * 1000 / esc, y + 0.6)], "CARIMBO")
        self.tx(x + L + 2, y, f"1:{esc:g}", 1.5, "MIDDLE_LEFT")

    # ---------------------------------------------------------------- rótulo de barra
    @staticmethod
    def rotulo(b, n=None, esp=None):
        q = b["qtd"] if n is None else n
        s = f"{q} {b['pos']} Ø{fd(b['diam'])}"
        esp = esp if esp is not None else b.get("esp")
        if esp:
            s += f" C/{fd(esp)}"
        return s + f" C={b['comp']:.0f}"

    # ---------------------------------------------------------------- barra explodida
    def barra_vertical(self, x, y0, b, esc, rot_lado=1, texto=None):
        """barra reta (k=R) ou com gancho no topo (k=L), desenhada em pé na escala esc, base em y0 (papel).
        Rótulo girado 90° ao lado; comprimento dos trechos junto ao traço."""
        g = b["geo"]
        a = g["a"] * 10 / esc
        pts = [(x, y0), (x, y0 + a)]
        if g["k"] == "L":
            pts.append((x + g.get("dir", 1) * g["g"] * 10 / esc, y0 + a))
        self.pl(pts, "ARMADURA")
        tl = texto or self.rotulo(b)
        # rótulo girado: à esquerda do traço, centrado
        self.tx(x - 1.2 * rot_lado, y0 + a / 2, tl, "min", "BOTTOM_CENTER" if rot_lado > 0 else "TOP_CENTER", rot=90)
        self.tx(x + 1.2 * rot_lado, y0 + a / 2, f"{g['a']:.0f}", "min", "TOP_CENTER" if rot_lado > 0 else "BOTTOM_CENTER", rot=90)
        if g["k"] == "L":
            self.tx(x + g.get("dir", 1) * g["g"] * 10 / esc / 2, y0 + a + 0.8, f"{g['g']:.0f}", 1.5, "BOTTOM_CENTER")
        return pts

    def forma(self, x, y, b, esc, rotulo=True, n=None, esp=None, rot_pos="abaixo"):
        """barra explodida de forma geral, canto inferior esquerdo em (x, y). Retorna bbox (x0, y0, x1, y1).
        k=E estribo fechado a × b com ganchos 135°; k=G grampo a com ganchos g; k=U U em planta (pernas a, base b, ganchos g);
        k=R reta horizontal; k=L reta + gancho g (horizontal)."""
        g = b["geo"]
        k = g["k"]
        s = 10 / esc
        hmin = ALTURAS["min"]
        if k == "E":
            A, B = g["a"] * s, g["b"] * s
            self.pl([(x, y), (x + A, y), (x + A, y + B), (x, y + B)], "ARM_TRANSV", True)
            hk = min(2.4, 0.3 * min(A, B))
            self.pl([(x, y + B), (x + hk, y + B - hk)], "ARM_TRANSV")
            self.pl([(x, y + B - 0.6), (x + hk, y + B - 0.6 - hk)], "ARM_TRANSV")
            self.tx(x + A / 2, y - 0.7, f"{g['a']:.0f}", "min", "TOP_CENTER")
            self.tx(x + A + 0.8, y + B / 2, f"{g['b']:.0f}", "min", "MIDDLE_LEFT")
            bb = [x, y - 0.7 - hmin, x + A + 0.8 + _wtext(f"{g['b']:.0f}", hmin), y + B]
        elif k == "G":
            A, gg = g["a"] * s, max(g["g"] * s, 1.5)
            self.pl([(x - gg * 0.7, y + gg * 0.7), (x, y), (x + A, y), (x + A + gg * 0.7, y + gg * 0.7)], "ARM_TRANSV")
            self.tx(x + A / 2, y - 0.7, f"{g['a']:.0f}", "min", "TOP_CENTER")
            self.tx(x + A / 2, y + 0.7, f"gancho 135° {g['g']:.0f}", 1.5, "BOTTOM_CENTER")
            bb = [x - gg, y - 0.7 - hmin, x + A + gg, y + 0.7 + 1.5]
        elif k == "U":
            A, B, gg = g["a"] * s, g["b"] * s, g.get("g", 0) * s
            self.pl([(x, y), (x + A, y), (x + A, y + B), (x, y + B)], "ARMADURA")
            if gg:
                self.ln((x, y), (x, y - gg), "ARMADURA"); self.ln((x, y + B), (x, y + B + gg), "ARMADURA")
                self.tx(x - 0.8, y + B + gg / 2, f"{g['g']:.0f}", 1.5, "MIDDLE_RIGHT")
            self.tx(x + A / 2, y - 0.7, f"{g['a']:.0f}", "min", "TOP_CENTER")
            self.tx(x + A + 0.8, y + B / 2, f"{g['b']:.0f}", "min", "MIDDLE_LEFT")
            bb = [x - (0.8 + _wtext("15", 1.5) if gg else 0), y - gg - 0.7 - hmin, x + A + 0.8 + _wtext(f"{g['b']:.0f}", hmin), y + B + gg]
        elif k == "C":                                   # reta com dobras g nas duas pontas (dir +1 para cima, −1 para baixo)
            A, gg, sg = g["a"] * s, g["g"] * s, g.get("dir", 1)
            self.pl([(x, y + sg * gg), (x, y), (x + A, y), (x + A, y + sg * gg)], "ARMADURA")
            self.tx(x + A / 2, y + (0.7 if sg < 0 else -0.7), f"{g['a']:.0f}", "min", "BOTTOM_CENTER" if sg < 0 else "TOP_CENTER")
            self.tx(x - 0.8, y + sg * gg / 2, f"{g['g']:.0f}", 1.5, "MIDDLE_RIGHT")
            self.tx(x + A + 0.8, y + sg * gg / 2, f"{g['g']:.0f}", 1.5, "MIDDLE_LEFT")
            y_lo, y_hi = min(y, y + sg * gg), max(y, y + sg * gg)
            bb = [x - 3, y_lo - (0.7 + hmin if sg > 0 else 0), x + A + 3, y_hi + (0.7 + hmin if sg < 0 else 0)]
        elif k in ("R", "L"):
            A = g["a"] * s
            pts = [(x, y), (x + A, y)]
            if k == "L":
                pts.append((x + A, y + g["g"] * s))
                self.tx(x + A + 0.8, y + g["g"] * s / 2, f"{g['g']:.0f}", 1.5, "MIDDLE_LEFT")
            self.pl(pts, "ARMADURA")
            self.tx(x + A / 2, y + 0.7, f"{g['a']:.0f}", "min", "BOTTOM_CENTER")
            bb = [x, y - 0.5, x + A + (3 if k == "L" else 0), y + 0.7 + hmin + (g["g"] * s if k == "L" else 0)]
        else:
            raise ValueError(k)
        if rotulo:
            t = self.rotulo(b, n, esp)
            if rot_pos == "abaixo":
                yy = bb[1] - 0.8
                self.tx(x, yy, t, "min", "TOP_LEFT")
                bb[1] = yy - hmin - 0.4
                bb[2] = max(bb[2], x + _wtext(t, hmin))
            else:                                        # acima
                yy = bb[3] + 0.8
                self.tx(x, yy, t, "min", "BOTTOM_LEFT")
                bb[3] = yy + hmin + 0.4
                bb[2] = max(bb[2], x + _wtext(t, hmin))
        self.pr.posicoes_desenho.add(b["pos"])
        return tuple(bb)

    # ---------------------------------------------------------------- tabelas no padrão
    def tabela_ferros(self, x, y_topo, barras, n=1, titulo=None, aco="CA-50", h_lin=4.4):
        """TABELA DE FERROS — n UNIDADE(S): TIPO, POS., BIT., QUANT., C.UNIT (cm), C.TOT (cm)."""
        lin = []
        for b in barras:
            q = b["qtd"] * n
            lin.append([aco, b["pos"], fd(b["diam"]), q, f"{b['comp']:.0f}", f"{q * b['comp']:.0f}"])
            self.pr.posicoes_tabela.add(b["pos"])
        t = titulo or f"TABELA DE FERROS — {n} UNIDADE{'S' if n > 1 else ''}"
        return self.pr.tabela(x, y_topo, t, ["TIPO", "POS.", "BIT.", "QUANT.", "C.UNIT (cm)", "C.TOT (cm)"], lin, [14, 12, 12, 15, 20, 21], h_lin=h_lin)

    def resumo(self, x, y_topo, barras, n=1, fck=None, vol=None, area=None, aco="CA-50", perda=0.10, h_lin=4.4, cordoalhas=None):
        """RESUMO DO AÇO +10%: comprimento por bitola (m, já com perdas) e peso (kg); PESO TOTAL; Fck, volume e área de fôrma."""
        res = {}
        for b in barras:
            res[float(b["diam"])] = res.get(float(b["diam"]), 0) + b["qtd"] * n * b["comp"] / 100 * (1 + perda)
        lin, tot = [], 0.0
        for d in sorted(res):
            kg = res[d] * MASSA_ACO[d]
            tot += kg
            lin.append([f"PESO {aco} Ø {fd(d)}", f"{f1(res[d])} m", f"{f1(kg)} kg"])
        lin.append([f"PESO TOTAL {aco}", "", f"{f1(tot)} kg"])
        if cordoalhas:
            for desc, m, kg in cordoalhas:
                lin.append([desc, f"{f1(m)} m", f"{f1(kg)} kg"])
        y = self.pr.tabela(x, y_topo, f"RESUMO DO AÇO +{perda*100:.0f}%" + (f" — {n} UNIDADES" if n > 1 else ""), ["DESCRIÇÃO", "COMPR.", "PESO"], lin, [44, 25, 25], h_lin=h_lin, destaque_ultima=not cordoalhas)
        if fck is not None:
            fx = [[f"Fck = {fck} MPa"], [f"VOLUME DE CONCRETO = {f1(vol * n)} m³"], [f"ÁREA DE FÔRMA = {f1(area * n)} m²"]]
            yy = y
            self.pr.ret(x, yy - 3 * h_lin, x + 94, yy, "TABELA")
            for k, (t,) in enumerate(fx):
                self.tx(x + 47, yy - (k + 0.5) * h_lin, t, "nota", "MIDDLE_CENTER")
            y = yy - 3 * h_lin
        return y, tot

    def cadeia_v(self, x, ys, rotulos, lado=1):
        """cadeia vertical de zonas (papel): traço com ticks em ys e rótulo girado no meio de cada zona."""
        self.ln((x, ys[0]), (x, ys[-1]), "COTA")
        for y in ys:
            self.ln((x - 1.2, y - 1.2), (x + 1.2, y + 1.2), "COTA")
            self.ln((x - 2, y), (x + 2, y), "COTA")
        for (a, b), t in zip(zip(ys[:-1], ys[1:]), rotulos):
            if t:
                self.tx(x + lado * 1.0, (a + b) / 2, t, "min", "TOP_CENTER" if lado > 0 else "BOTTOM_CENTER", rot=90)

    def cadeia_h(self, y, xs, rotulos, acima=True):
        self.ln((xs[0], y), (xs[-1], y), "COTA")
        for x in xs:
            self.ln((x - 1.2, y - 1.2), (x + 1.2, y + 1.2), "COTA")
            self.ln((x, y - 2), (x, y + 2), "COTA")
        for (a, b), t in zip(zip(xs[:-1], xs[1:]), rotulos):
            if t:
                self.tx((a + b) / 2, y + (0.8 if acima else -0.8), t, "min", "BOTTOM_CENTER" if acima else "TOP_CENTER")

    def corte(self, xa, xb, y, nome):
        """marcador de seção S.x: traço curto com nome nas duas pontas."""
        for x0, x1 in ((xa - 5, xa), (xb, xb + 5)):
            self.ln((x0, y), (x1, y), "INDICACAO")
        self.tx(xa - 5.5, y, nome, "min", "MIDDLE_RIGHT", lay="TITULO")
        self.tx(xb + 5.5, y, nome, "min", "MIDDLE_LEFT", lay="TITULO")


def zonas(zs):
    """agrupa cotas de estribos em zonas de espaçamento constante: [(z0, z1, n, s)]"""
    zs = sorted(zs)
    out = []
    i = 0
    while i < len(zs):
        j = i
        s = zs[i + 1] - zs[i] if i + 1 < len(zs) else None
        while j + 1 < len(zs) and zs[j + 1] - zs[j] == s:
            j += 1
        out.append([zs[i], zs[j], j - i + 1, s])
        i = j + 1
    # junta zonas de 1 estribo à vizinha
    res = []
    for z in out:
        if res and (z[2] == 1 or res[-1][2] == 1):
            a = res.pop()
            res.append([a[0], z[1], a[2] + z[2], a[3] or z[3]])
        else:
            res.append(z)
    return res
