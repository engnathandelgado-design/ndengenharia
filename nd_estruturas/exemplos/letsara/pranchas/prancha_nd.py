"""prancha_nd.py — motor de pranchas técnicas da ND Engenharia (DXF + PDF em escala real).
Modelo em mm reais; papel em mm. Cada Vista: P_papel = origem + P_modelo / escala. Cotas com dimlfac = escala.
"""
from __future__ import annotations
import math, datetime
import ezdxf
from ezdxf import bbox
from ezdxf.enums import TextEntityAlignment

FORMATOS = {"A0": (1189, 841), "A1": (841, 594), "A2": (594, 420), "A3": (420, 297), "A4": (297, 210)}
def margens(fmt):
    m = 10 if fmt in ("A0", "A1") else 7
    return dict(esq=25, dir=m, sup=m, inf=m)

MASSA_ACO = {5.0: 0.154, 6.3: 0.245, 8.0: 0.395, 10.0: 0.617, 12.5: 0.963, 16.0: 1.578,
             20.0: 2.466, 22.0: 2.984, 25.0: 3.853, 32.0: 6.313, 40.0: 9.865}
ALTURAS = {"min": 1.8, "nota": 2.5, "cota": 2.5, "sub": 3.5, "titulo": 5.0, "grande": 7.0}
CAMADAS = {
    "MOLDURA": (7, 70, "Continuous"), "CARIMBO": (7, 35, "Continuous"), "CARIMBO_FINO": (8, 18, "Continuous"),
    "CORTADO": (7, 70, "Continuous"), "VISTA": (7, 35, "Continuous"), "OCULTA": (8, 25, "ACAD_ISO02W100"),
    "EIXO": (8, 18, "ACAD_ISO10W100"), "ARMADURA": (5, 50, "Continuous"), "ARM_SECAO": (5, 50, "Continuous"),
    "METALICA": (30, 50, "Continuous"), "TERRENO": (34, 35, "Continuous"), "HACHURA": (8, 13, "Continuous"),
    "COTA": (1, 18, "Continuous"), "TEXTO": (7, 25, "Continuous"), "TITULO": (7, 50, "Continuous"),
    "CHAMADA": (7, 18, "Continuous"), "INDICACAO": (7, 50, "Continuous"), "TABELA": (7, 25, "Continuous"),
    "TABELA_FINA": (8, 13, "Continuous"),
}
EMPRESA = dict(nome="ND ENGENHARIA E ASSESSORIA LTDA", cnpj="46.745.157/0001-47",
               rt="Eng. Civil Nathan Henrique Delgado", crea="CREA-SC 168298-1", site="ndengenharia.com")
AREA_CORD = {9.5: 55.5, 12.7: 98.7, 15.2: 140.0}   # mm², cordoalhas de 7 fios CP-190 RB (NBR 7483 — conferir)
FONTE = "DejaVuSansCondensed.ttf"
_FONT_CACHE = {}


def _wtext(s, h):
    """largura REAL do texto no papel (métrica da fonte), em mm."""
    try:
        from ezdxf.fonts import fonts
        f = _FONT_CACHE.get(h) or _FONT_CACHE.setdefault(h, fonts.make_font(FONTE, h))
        return f.text_width(s)
    except Exception:
        return 0.75 * h * len(s)


def quebrar(s, largura, h):
    linhas, atual = [], ""
    for w in s.split():
        cand = (atual + " " + w).strip()
        if _wtext(cand, h) <= largura or not atual:
            atual = cand
        else:
            linhas.append(atual)
            atual = w
    if atual:
        linhas.append(atual)
    return linhas


def _seg_rect(p, q, r):
    """segmento p-q intercepta retângulo r=(x0,y0,x1,y1)? (Liang–Barsky)"""
    x0, y0, x1, y1 = r
    dx, dy = q[0] - p[0], q[1] - p[1]
    t0, t1 = 0.0, 1.0
    for pp, qq in ((-dx, p[0] - x0), (dx, x1 - p[0]), (-dy, p[1] - y0), (dy, y1 - p[1])):
        if abs(pp) < 1e-12:
            if qq < 0:
                return False
        else:
            t = qq / pp
            if pp < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
            if t0 > t1:
                return False
    return True


def _ovl(a, b, folga):
    return (min(a[2], b[2]) - max(a[0], b[0]) > -folga and min(a[3], b[3]) - max(a[1], b[1]) > -folga)


class Prancha:
    def __init__(self, formato="A1", dados: dict | None = None, cor=True, fonte=FONTE):
        self.fmt = formato
        self.W, self.H = FORMATOS[formato]
        self.m = margens(formato)
        self.dados = dict(cliente="", obra="", local="", conteudo="", desenho="", rev="00",
                          data=datetime.date.today().strftime("%d/%m/%Y"), folha="01/01",
                          projeto=EMPRESA["rt"], desenhista="ND Engenharia", verificado="", fase="EXECUTIVO")
        self.dados.update(dados or {})
        self.cor = cor
        self.revisoes, self.vistas, self.refs, self.blocos_livres = [], [], [], []
        self.posicoes_desenho, self.posicoes_tabela = set(), set()
        self.avisos_extra, self.imagens = [], []
        doc = ezdxf.new("R2018", setup=True, units=4)
        doc.header["$LTSCALE"] = 0.5
        doc.header["$PSLTSCALE"] = 0
        doc.header["$LWDISPLAY"] = 1
        self.doc, self.msp = doc, doc.modelspace()
        doc.styles.new("ND", dxfattribs={"font": fonte, "width": 1.0})
        for n, (c, lw, lt) in CAMADAS.items():
            doc.layers.add(n, color=c, lineweight=lw, linetype=lt)
        ds = doc.dimstyles.new("ND")
        for k, v in dict(dimtxsty="ND", dimtxt=ALTURAS["cota"], dimtsz=1.0, dimasz=2.0, dimexo=1.5, dimexe=1.5,
                         dimdle=1.0, dimgap=0.8, dimtad=1, dimtih=0, dimtoh=0, dimdec=0, dimzin=8,
                         dimdsep=ord(","), dimclrd=1, dimclre=1, dimclrt=1, dimlwd=18, dimlwe=18, dimtmove=0).items():
            setattr(ds.dxf, k, v)

    @property
    def quadro(self):
        m = self.m
        return (m["esq"], m["inf"], self.W - m["dir"], self.H - m["sup"])

    @property
    def carimbo_bbox(self):
        x0, y0, x1, y1 = self.quadro
        return (x1 - 180, y0, x1, y0 + 70 + 5 * max(len(self.revisoes), 1) + 6)

    def texto(self, x, y, s, h="nota", camada="TEXTO", alinh="BOTTOM_LEFT", rot=0, registrar=True):
        hh = ALTURAS[h] if isinstance(h, str) else h
        t = self.msp.add_text(s, height=hh, rotation=rot, dxfattribs={"layer": camada, "style": "ND"})
        t.set_placement((x, y), align=TextEntityAlignment[alinh])
        return t

    def linha(self, p1, p2, camada="CARIMBO"):
        return self.msp.add_line(p1, p2, dxfattribs={"layer": camada})

    def ret(self, x0, y0, x1, y1, camada="CARIMBO"):
        return self.msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True,
                                       dxfattribs={"layer": camada})

    def vista(self, nome, origem, escala, titulo=None, subtitulo=None):
        v = Vista(self, nome, origem, escala, titulo, subtitulo)
        self.vistas.append(v)
        return v

    def tabela(self, x, y_topo, titulo, cab, linhas, larg, h_lin=6.0, destaque_ultima=False):
        W = sum(larg)
        y = y_topo
        self.ret(x, y - 8, x + W, y, "TABELA")
        self.texto(x + W / 2, y - 4, titulo, "sub", "TITULO", "MIDDLE_CENTER")
        y -= 8
        for row_i, row in enumerate([cab] + linhas):
            camada = "TABELA" if row_i == 0 or (destaque_ultima and row_i == len(linhas)) else "TABELA_FINA"
            self.linha((x, y - h_lin), (x + W, y - h_lin), camada)
            xx = x
            for c, w in zip(row, larg):
                self.texto(xx + w / 2, y - h_lin / 2, str(c), "nota", "TEXTO", "MIDDLE_CENTER")
                xx += w
            y -= h_lin
        xx = x
        for w in larg[:-1]:
            xx += w
            self.linha((xx, y_topo - 8), (xx, y), "TABELA_FINA")
        self.ret(x, y, x + W, y_topo, "TABELA")
        self.blocos_livres.append((x, y, x + W, y_topo, titulo))
        return y

    def tabela_aco(self, x, y_topo, barras, perda=0.10, aco="CA-50"):
        """barras: dict(pos='N1', diam=16, qtd=8, comp=250 cm). Relação + resumo (NBR 7480 + perdas)."""
        linhas, resumo = [], {}
        for b in barras:
            ct = b["qtd"] * b["comp"] / 100.0
            linhas.append([b["pos"], b.get("aco", aco), f"{b['diam']:g}".replace(".", ","),
                           b["qtd"], f"{b['comp']:.0f}", f"{ct:.2f}".replace(".", ",")])
            key = (b.get("aco", aco), float(b["diam"]))
            resumo[key] = resumo.get(key, 0.0) + ct
            self.posicoes_tabela.add(b["pos"])
        y = self.tabela(x, y_topo, "RELAÇÃO DO AÇO", ["POS", "AÇO", "Ø (mm)", "QUANT", "C. UNIT (cm)", "C. TOTAL (m)"],
                        linhas, [14, 18, 16, 16, 24, 26])
        lin_r, total = [], 0.0
        for (a, d), c in sorted(resumo.items()):
            kg = c * MASSA_ACO[d] * (1 + perda)
            total += kg
            lin_r.append([a, f"{d:g}".replace(".", ","), f"{c:.2f}".replace(".", ","), f"{kg:.1f}".replace(".", ",")])
        lin_r.append(["", "", "TOTAL (kg)", f"{total:.1f}".replace(".", ",")])
        y = self.tabela(x, y - 4, f"RESUMO DO AÇO (+{perda*100:.0f}% perdas)", ["AÇO", "Ø (mm)", "C. TOTAL (m)", "MASSA (kg)"],
                        lin_r, [28, 24, 32, 30], destaque_ultima=True)
        return dict(total_kg=total, resumo=resumo, y_base=y)

    def tabela_cordoalhas(self, x, y_topo, cordoalhas, L_pista_m, Ep=195e3, fptk=1900.0):
        """cordoalhas: dict(pos='C1', diam=12.7, qtd=2, y=51 (mm da base), forca=137 (kN/cordoalha na pista),
        isol=3350 (mm isolado, 0 = aderente) e local='CENTRO'|'PONTAS'). ΔL teórico = F·L_pista/(Ep·Ap) (mm).
        Confere σpi ≤ min(0,77 fptk; 0,85 fpyk), fpyk = 0,9 fptk (pré-tração, RB — NBR 6118 9.6.1.2.1, conferir).
        Registra as posições como tabeladas (as cordoalhas desenhadas com v.barra não viram ERRO)."""
        lim, linhas, av = min(0.77 * fptk, 0.85 * 0.9 * fptk), [], []
        for c in cordoalhas:
            Ap = AREA_CORD[float(c["diam"])]
            sig = c["forca"] * 1e3 / Ap
            dL = c["forca"] * 1e3 * L_pista_m * 1e3 / (Ep * Ap)
            if sig > lim + 1e-6:
                av.append(("ERRO", f"{c['pos']}: σpi = {sig:.0f} MPa > {lim:.0f} MPa"))
            isol = f"{c['isol']:.0f} {c.get('local', 'PONTAS')}" if c.get("isol") else "ADERENTE"
            linhas.append([c["pos"], f"{c['diam']:g}".replace(".", ","), c["qtd"], f"{c['y']:.0f}",
                           f"{c['forca']:.1f}".replace(".", ","), f"{dL:.0f}", isol])
            self.posicoes_tabela.add(c["pos"])
        y = self.tabela(x, y_topo, f"CORDOALHAS CP-{fptk/10:.0f} RB — PISTA {L_pista_m:g} m".replace(".", ","),
                        ["POS", "Ø (mm)", "QUANT", "y (mm)", "F (kN)", "ΔL (mm)", "ISOLAM. (mm)"],
                        linhas, [12, 14, 14, 14, 18, 18, 38])
        self.avisos_extra += av                     # entram no verificar()/salvar()
        return dict(y_base=y, avisos=av, sig_lim=lim)

    def notas(self, x, y_topo, linhas, largura=170, titulo="NOTAS"):
        """Notas numeradas, quebra pela largura real. Use f-strings com os parâmetros (nota paramétrica)."""
        h = ALTURAS["nota"]
        self.texto(x, y_topo - ALTURAS["sub"], titulo, "sub", "TITULO")
        y = y_topo - ALTURAS["sub"] - 4
        for i, s in enumerate(linhas, 1):
            for k, p in enumerate(quebrar(f"{i}. {s}", largura - 6, h)):
                self.texto(x + (0 if k == 0 else 4), y - h, p, "nota")
                y -= h * 1.6
            y -= h * 0.4
        self.blocos_livres.append((x, y, x + largura, y_topo, titulo))
        return y

    def imagem(self, x0, y0, x1, y1, caminho, titulo=None, subtitulo=None):
        """Imagem raster (ex.: isométrico 3D) num retângulo do papel (mm). Entra no PDF/PNG; no DXF fica o quadro."""
        self.ret(x0, y0, x1, y1, "CARIMBO_FINO")
        self.imagens.append((x0, y0, x1, y1, caminho))
        yb = y0
        if titulo:
            cx = (x0 + x1) / 2
            w1 = _wtext(titulo.upper(), ALTURAS["titulo"])
            self.texto(cx, y0 - 8, titulo.upper(), "titulo", "TITULO", "BOTTOM_CENTER")
            self.linha((cx - w1 / 2, y0 - 9.2), (cx + w1 / 2, y0 - 9.2), "TITULO")
            if subtitulo:
                self.texto(cx, y0 - 14.5, subtitulo, "nota", "TEXTO", "BOTTOM_CENTER")
            yb = y0 - 15
        self.blocos_livres.append((x0, yb, x1, y1, titulo or caminho))

    def tabela_croqui(self, x, y_topo, barras, perda=0.10, aco="CA-50", h_lin=13.0):
        """Relação do aço com croqui de dobramento (padrão de mercado BIM). barras: dict(pos, diam, qtd, comp (cm),
        forma=[(x,y) cm ...] polilinha da barra, trechos=['84','14',...] rótulos na ordem dos segmentos)."""
        larg = [13, 13, 14, 20, 66, 20, 20]
        W = sum(larg)
        cab = ["POS", "Ø", "QUANT", "C. UNIT (cm)", "CROQUI (cm)", "C. TOTAL (m)", "MASSA (kg)"]
        self.ret(x, y_topo - 8, x + W, y_topo, "TABELA")
        self.texto(x + W / 2, y_topo - 4, "RELAÇÃO DO AÇO — CROQUIS DE DOBRAMENTO", "sub", "TITULO", "MIDDLE_CENTER")
        y = y_topo - 8
        self.linha((x, y - 6), (x + W, y - 6), "TABELA")
        xx = x
        for c, w in zip(cab, larg):
            self.texto(xx + w / 2, y - 3, c, "nota", "TEXTO", "MIDDLE_CENTER"); xx += w
        y -= 6
        resumo, total = {}, 0.0
        for b in barras:
            ct = b["qtd"] * b["comp"] / 100.0
            kg = ct * MASSA_ACO[float(b["diam"])]
            key = (b.get("aco", aco), float(b["diam"]))
            resumo[key] = resumo.get(key, 0.0) + ct
            self.posicoes_tabela.add(b["pos"])
            vals = [b["pos"], f"{b['diam']:g}".replace(".", ","), b["qtd"], f"{b['comp']:.0f}", None,
                    f"{ct:.2f}".replace(".", ","), f"{kg:.1f}".replace(".", ",")]
            xx = x
            for k, (c, w) in enumerate(zip(vals, larg)):
                if c is not None:
                    self.texto(xx + w / 2, y - h_lin / 2, str(c), "nota", "TEXTO", "MIDDLE_CENTER")
                else:
                    pts = b.get("forma") or [(0, 0), (b["comp"], 0)]
                    xs_, ys_ = [p[0] for p in pts], [p[1] for p in pts]
                    bw_, bh_ = max(xs_) - min(xs_), max(ys_) - min(ys_)
                    esc = min((w - 16) / max(bw_, 1e-6), (h_lin - 6) / max(bh_, 1e-6))
                    cx0 = xx + w / 2 - bw_ * esc / 2 - min(xs_) * esc
                    cy0 = y - h_lin / 2 - bh_ * esc / 2 - min(ys_) * esc
                    pp = [(cx0 + px * esc, cy0 + py * esc) for px, py in pts]
                    self.msp.add_lwpolyline(pp, dxfattribs={"layer": "ARMADURA"})
                    for (a, c2), t in zip(zip(pp[:-1], pp[1:]), b.get("trechos", [f"{b['comp']:.0f}"])):
                        mx, my = (a[0] + c2[0]) / 2, (a[1] + c2[1]) / 2
                        vert = abs(c2[0] - a[0]) < abs(c2[1] - a[1])
                        if vert:
                            lado = -1 if mx < xx + w / 2 else 1
                            self.texto(mx + lado * 1.0, my, t, "min", "TEXTO", "MIDDLE_LEFT" if lado > 0 else "MIDDLE_RIGHT")
                        else:
                            acima = my >= y - h_lin / 2
                            self.texto(mx, my + (0.8 if acima else -0.8), t, "min", "TEXTO",
                                       "BOTTOM_CENTER" if acima else "TOP_CENTER")
                xx += w
            self.linha((x, y - h_lin), (x + W, y - h_lin), "TABELA_FINA")
            y -= h_lin
        xx = x
        for w in larg[:-1]:
            xx += w
            self.linha((xx, y_topo - 8), (xx, y), "TABELA_FINA")
        self.ret(x, y, x + W, y_topo, "TABELA")
        self.blocos_livres.append((x, y, x + W, y_topo, "RELAÇÃO DO AÇO"))
        lin_r = []
        for (a, d), c in sorted(resumo.items()):
            kg = c * MASSA_ACO[d] * (1 + perda)
            total += kg
            lin_r.append([a, f"{d:g}".replace(".", ","), f"{c:.2f}".replace(".", ","), f"{kg:.1f}".replace(".", ",")])
        lin_r.append(["", "", "TOTAL (kg)", f"{total:.1f}".replace(".", ",")])
        y = self.tabela(x, y - 4, f"RESUMO DO AÇO (+{perda*100:.0f}% perdas)", ["AÇO", "Ø (mm)", "C. TOTAL (m)", "MASSA (kg)"],
                        lin_r, [40, 34, 46, 46], destaque_ultima=True)
        return dict(total_kg=total, resumo=resumo, y_base=y)

    def revisao(self, rev, data, descricao):
        self.revisoes.append((rev, data, descricao))
        self.dados["rev"] = rev

    def _moldura_carimbo(self):
        x0, y0, x1, y1 = self.quadro
        self.ret(0, 0, self.W, self.H, "CARIMBO_FINO")
        self.ret(x0, y0, x1, y1, "MOLDURA")
        for (a, b) in [((self.W / 2, 0), (self.W / 2, y0)), ((self.W / 2, y1), (self.W / 2, self.H)),
                       ((0, self.H / 2), (x0, self.H / 2)), ((x1, self.H / 2), (self.W, self.H / 2))]:
            self.linha(a, b, "MOLDURA")
        cx0, cy0, cx1, cy1 = self.carimbo_bbox
        d, L, y = self.dados, cx1 - cx0, cy0
        h1 = 12
        self.ret(cx0, y, cx1, y + h1)
        for a, b, lab, val, hh in [(0, 80, "DESENHO Nº", d["desenho"], "titulo"), (80, 110, "REV.", d["rev"], "titulo"),
                                   (110, 150, "FOLHA", d["folha"], "sub"), (150, 180, "FORMATO", self.fmt, "sub")]:
            if a:
                self.linha((cx0 + a, y), (cx0 + a, y + h1))
            self.texto(cx0 + a + 1.5, y + h1 - 2.5, lab, "min")
            self.texto(cx0 + (a + b) / 2, y + 4.5, val, hh, "TITULO", "MIDDLE_CENTER")
        y += h1
        h2 = 10
        self.ret(cx0, y, cx1, y + h2)
        esc = d.get("escala") or self._escalas_txt()
        for a, b, lab, val in [(0, 40, "ESCALA", esc), (40, 70, "DATA", d["data"]), (70, 125, "DESENHO", d["desenhista"]),
                               (125, 180, "VERIFICADO", d["verificado"] or "-")]:
            if a:
                self.linha((cx0 + a, y), (cx0 + a, y + h2))
            self.texto(cx0 + a + 1.5, y + h2 - 2.5, lab, "min")
            self.texto(cx0 + (a + b) / 2, y + 3.2, val, "nota", alinh="MIDDLE_CENTER")
        y += h2
        h3 = 14
        self.ret(cx0, y, cx1, y + h3)
        self.texto(cx0 + 1.5, y + h3 - 2.5, "CONTEÚDO", "min")
        parts = quebrar(d["conteudo"], L - 8, ALTURAS["sub"])[:2]
        for k, p in enumerate(parts):
            self.texto(cx0 + L / 2, y + (5.5 if len(parts) == 1 else 7.6 - k * 4.6), p, "sub", "TITULO", "MIDDLE_CENTER")
        y += h3
        h4 = 16
        self.ret(cx0, y, cx1, y + h4)
        for k, (lab, val) in enumerate([("CLIENTE", d["cliente"]), ("OBRA", d["obra"]), ("LOCAL", d["local"])]):
            yy = y + h4 - 4.5 - k * 5
            self.texto(cx0 + 1.5, yy, lab + ":", "min")
            self.texto(cx0 + 18, yy, val, "nota")
        y += h4
        h5 = 18
        self.ret(cx0, y, cx1, y + h5)
        self.texto(cx0 + 3, y + 5, "ND", 7.0, "TITULO")
        self.texto(cx0 + 19, y + h5 - 6, EMPRESA["nome"], "sub", "TITULO")
        self.texto(cx0 + 19, y + h5 - 10.5, f"CNPJ {EMPRESA['cnpj']} · {EMPRESA['site']}", "min")
        self.texto(cx0 + 19, y + 2.5, f"RESP. TÉCNICO: {EMPRESA['rt']} — {EMPRESA['crea']}", "min")
        self.texto(cx1 - 2, y + h5 - 6, d.get("fase", ""), "nota", "TITULO", "BOTTOM_RIGHT")
        y += h5
        nrev = max(len(self.revisoes), 1)
        self.ret(cx0, y, cx1, y + 6)
        for a, lab in [(0, "REV"), (14, "DATA"), (40, "DESCRIÇÃO")]:
            self.texto(cx0 + a + 1.5, y + 1.8, lab, "min")
        self.linha((cx0 + 14, y), (cx0 + 14, y + 6 + 5 * nrev))
        self.linha((cx0 + 40, y), (cx0 + 40, y + 6 + 5 * nrev))
        y += 6
        for r, dt, ds in (self.revisoes or [(d["rev"], d["data"], "EMISSÃO INICIAL")]):
            self.ret(cx0, y, cx1, y + 5, "CARIMBO_FINO")
            self.texto(cx0 + 7, y + 1.5, r, "min", alinh="BOTTOM_CENTER")
            self.texto(cx0 + 27, y + 1.5, dt, "min", alinh="BOTTOM_CENTER")
            self.texto(cx0 + 41.5, y + 1.5, ds[:70], "min")
            y += 5
        sx, sy = cx0 - 22, cy0 + 6   # símbolo 1º diedro
        self.msp.add_circle((sx + 15, sy + 5), 4, dxfattribs={"layer": "CARIMBO"})
        self.msp.add_circle((sx + 15, sy + 5), 2, dxfattribs={"layer": "CARIMBO"})
        self.msp.add_lwpolyline([(sx, sy + 2), (sx + 8, sy), (sx + 8, sy + 10), (sx, sy + 8)], close=True,
                                dxfattribs={"layer": "CARIMBO"})
        self.texto(sx + 9, sy - 4, "1º DIEDRO", "min", alinh="BOTTOM_CENTER")

    def _escalas_txt(self):
        es = sorted({v.esc for v in self.vistas}, reverse=True)
        if not es:
            return "-"
        return "INDICADAS" if len(es) > 1 else f"1:{es[0]:g}"

    def verificar(self):
        """Checagens automáticas antes de emitir. Retorna lista de (nível, mensagem)."""
        avisos = []
        for k in ["cliente", "obra", "local", "conteudo", "desenho", "rev", "data", "folha"]:
            if not str(self.dados.get(k, "")).strip():
                avisos.append(("ERRO", f"carimbo: campo '{k}' vazio"))
        avisos += self._checar_textos() + self.avisos_extra
        qx0, qy0, qx1, qy1 = self.quadro
        caixas = [(v.nome, v.bbox_papel()) for v in self.vistas] + [(t[4], t[:4]) for t in self.blocos_livres]
        caixas = [(n, b) for n, b in caixas if b]
        cb = self.carimbo_bbox
        for n, b in caixas:
            if b[0] < qx0 or b[1] < qy0 or b[2] > qx1 or b[3] > qy1:
                avisos.append(("ERRO", f"'{n}' sai do quadro da folha"))
            if _ovl(b, cb, 0):
                avisos.append(("ERRO", f"'{n}' invade o carimbo"))
        for i in range(len(caixas)):
            for j in range(i + 1, len(caixas)):
                if _ovl(caixas[i][1], caixas[j][1], 2.0):
                    avisos.append(("AVISO", f"'{caixas[i][0]}' encosta/sobrepõe '{caixas[j][0]}' (folga < 2 mm)"))
        nomes = {v.nome.upper() for v in self.vistas}
        for tipo, rot in self.refs:
            if not any(f"{tipo} {rot}".upper() in n for n in nomes):
                avisos.append(("ERRO", f"marcador {tipo} {rot} sem vista correspondente na folha"))
        for v in self.vistas:
            vistos = set()
            for k in v._cotas:
                if k in vistos:
                    avisos.append(("AVISO", f"{v.nome}: cota duplicada {k}"))
                vistos.add(k)
        fal = self.posicoes_desenho - self.posicoes_tabela
        sob = self.posicoes_tabela - self.posicoes_desenho
        if fal:
            avisos.append(("ERRO", f"posições desenhadas sem linha na tabela de aço: {sorted(fal)}"))
        if sob:
            avisos.append(("AVISO", f"posições na tabela sem chamada no desenho: {sorted(sob)}"))
        return avisos

    def _checar_textos(self, tol=0.25):
        LIN = {"CORTADO", "VISTA", "ARMADURA", "ARM_SECAO", "METALICA", "TERRENO", "COTA", "CHAMADA", "INDICACAO",
               "EIXO", "CARIMBO", "CARIMBO_FINO", "TABELA", "TABELA_FINA", "TITULO", "MOLDURA", "0"}
        textos, segs = [], []
        def coleta(e, dono):
            t = e.dxftype()
            if t in ("TEXT", "MTEXT"):
                ext = bbox.extents([e], fast=False)
                if ext.has_data:
                    txt = e.dxf.text if t == "TEXT" else e.plain_text()
                    textos.append(((ext.extmin.x + tol, ext.extmin.y + tol, ext.extmax.x - tol, ext.extmax.y - tol), txt, dono))
            elif e.dxf.layer in LIN or dono is not None:
                if t == "LINE":
                    segs.append(((e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y), dono, e.dxf.layer))
                elif t == "LWPOLYLINE":
                    pts = [(p[0], p[1]) for p in e.get_points("xy")]
                    if e.closed:
                        pts.append(pts[0])
                    for a, b in zip(pts[:-1], pts[1:]):
                        segs.append((a, b, dono, e.dxf.layer))
        for k, e in enumerate(self.msp):
            if e.dxftype() == "DIMENSION":
                for v in e.virtual_entities():
                    if v.dxftype() != "INSERT":
                        coleta(v, ("dim", k))
            else:
                coleta(e, None)
        av = []
        for i in range(len(textos)):
            ri = textos[i][0]
            for j in range(i + 1, len(textos)):
                rj = textos[j][0]
                if min(ri[2], rj[2]) > max(ri[0], rj[0]) and min(ri[3], rj[3]) > max(ri[1], rj[1]):
                    av.append(("AVISO", f"textos sobrepostos: '{textos[i][1][:28]}' x '{textos[j][1][:28]}'"))
        for r, txt, dono in textos:
            for a, b, d2, lay in segs:
                if dono is not None and d2 == dono:
                    continue
                if _seg_rect(a, b, r):
                    av.append(("AVISO", f"linha ({lay}) cruza o texto '{txt[:30]}'"))
                    break
        return av

    def salvar(self, base, png_dpi=110):
        for v in self.vistas:
            v._finalizar()
        self._moldura_carimbo()
        avisos = self.verificar()
        self.doc.saveas(base + ".dxf")
        _exportar_pdf(self.doc, base + ".pdf", self.W, self.H, self.cor)
        try:
            import pymupdf
            k = 72 / 25.4
            if self.imagens:
                pdf = pymupdf.open(base + ".pdf")
                pg = pdf[0]
                for x0, y0, x1, y1, cam in self.imagens:
                    pg.insert_image(pymupdf.Rect(x0 * k + 1, (self.H - y1) * k + 1, x1 * k - 1, (self.H - y0) * k - 1),
                                    filename=cam, keep_proportion=True)
                pdf.save(base + ".pdf", incremental=True, encryption=0)
                pdf.close()
            pymupdf.open(base + ".pdf")[0].get_pixmap(dpi=png_dpi).save(base + ".png")
        except Exception:
            pass
        return avisos


def _exportar_pdf(doc, caminho, W, H, cor=True):
    from ezdxf.addons.drawing import Frontend, RenderContext, pymupdf as pmb, layout, config
    be = pmb.PyMuPdfBackend()
    cfg = config.Configuration(
        background_policy=config.BackgroundPolicy.WHITE,
        color_policy=config.ColorPolicy.COLOR if cor else config.ColorPolicy.BLACK,
        lineweight_policy=config.LineweightPolicy.ABSOLUTE, lineweight_scaling=1.0,
        min_lineweight=0.13 / 0.3527777, hatch_policy=config.HatchPolicy.NORMAL)
    Frontend(RenderContext(doc), be, config=cfg).draw_layout(doc.modelspace())
    page = layout.Page(W, H, layout.Units.mm, margins=layout.Margins.all(0))
    data = be.get_pdf_bytes(page, settings=layout.Settings(fit_page=False, scale=1.0))
    with open(caminho, "wb") as f:
        f.write(data)


class Vista:
    def __init__(self, pr, nome, origem, esc, titulo=None, subtitulo=None):
        self.pr, self.nome, self.o, self.esc = pr, nome, origem, esc
        self.titulo, self.subtitulo = titulo or nome, subtitulo
        self.ents, self._cotas = [], []

    def P(self, x, y=None):
        if y is None:
            x, y = x
        return (self.o[0] + x / self.esc, self.o[1] + y / self.esc)

    def _add(self, e):
        self.ents.append(e)
        return e

    def linha(self, p1, p2, camada="VISTA"):
        return self._add(self.pr.msp.add_line(self.P(p1), self.P(p2), dxfattribs={"layer": camada}))

    def poli(self, pts, camada="VISTA", fechada=False):
        return self._add(self.pr.msp.add_lwpolyline([self.P(p) for p in pts], close=fechada, dxfattribs={"layer": camada}))

    def ret(self, x, y, w, h, camada="CORTADO"):
        return self.poli([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], camada, True)

    def circulo(self, c, r, camada="VISTA"):
        return self._add(self.pr.msp.add_circle(self.P(c), r / self.esc, dxfattribs={"layer": camada}))

    def ponto_barra(self, c, diam, camada="ARM_SECAO"):
        r = max(diam / 2 / self.esc, 0.4)
        h = self.pr.msp.add_hatch(color=256, dxfattribs={"layer": camada})
        h.paths.add_edge_path().add_arc(self.P(c), r, 0, 360)
        self._add(h)
        return self.circulo(c, max(diam / 2, 0.4 * self.esc), camada)

    def hachura(self, pts, padrao="AR-CONC", escala_papel=0.03, camada="HACHURA", angulo=0):
        h = self.pr.msp.add_hatch(color=256, dxfattribs={"layer": camada})
        h.paths.add_polyline_path([self.P(p) for p in pts], is_closed=True)
        if padrao == "SOLID":
            h.set_solid_fill()
        else:
            h.set_pattern_fill(padrao, scale=escala_papel, angle=angulo)
        return self._add(h)

    def eixo(self, p1, p2, ext=300):
        (x1, y1), (x2, y2) = p1, p2
        L = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        return self.linha((x1 - ux * ext, y1 - uy * ext), (x2 + ux * ext, y2 + uy * ext), "EIXO")

    def texto(self, p, s, h="nota", alinh="BOTTOM_LEFT", camada="TEXTO", rot=0):
        x, y = self.P(p)
        return self._add(self.pr.texto(x, y, s, h, camada, alinh, rot))

    def _dim(self, base, p1, p2, ang, texto="<>"):
        self._cotas.append((ang % 180, tuple(sorted([tuple(round(c, 1) for c in p1), tuple(round(c, 1) for c in p2)]))))
        d = self.pr.msp.add_linear_dim(base=self.P(base), p1=self.P(p1), p2=self.P(p2), angle=ang, text=texto,
                                       dimstyle="ND", override={"dimlfac": self.esc}, dxfattribs={"layer": "COTA"})
        d.render()
        return self._add(d.dimension)

    def cota(self, p1, p2, dist_papel=-10.0, ang=0, texto="<>"):
        if ang == 0:
            return self._dim((p1[0], p1[1] + dist_papel * self.esc), p1, p2, 0, texto)
        return self._dim((p1[0] + dist_papel * self.esc, p1[1]), p1, p2, 90, texto)

    def interrupcao(self, p1, p2, camada="VISTA"):
        (x1, y1), (x2, y2) = self.P(p1), self.P(p2)
        L = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        nx, ny = -uy, ux
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        pts = [(x1, y1), (mx - ux * 2, my - uy * 2), (mx - ux * 0.7 + nx * 3, my - uy * 0.7 + ny * 3),
               (mx + ux * 0.7 - nx * 3, my + uy * 0.7 - ny * 3), (mx + ux * 2, my + uy * 2), (x2, y2)]
        return self._add(self.pr.msp.add_lwpolyline(pts, dxfattribs={"layer": camada}))

    def cota_h(self, xs, y_ref, dist_papel=-10.0, total=True):
        yb = y_ref + dist_papel * self.esc
        for a, b in zip(xs[:-1], xs[1:]):
            self._dim((a, yb), (a, y_ref), (b, y_ref), 0)
        if total and len(xs) > 2:
            yt = yb + math.copysign(7.0, dist_papel) * self.esc
            self._dim((xs[0], yt), (xs[0], y_ref), (xs[-1], y_ref), 0)

    def cota_v(self, ys, x_ref, dist_papel=-10.0, total=True):
        xb = x_ref + dist_papel * self.esc
        for a, b in zip(ys[:-1], ys[1:]):
            self._dim((xb, a), (x_ref, a), (x_ref, b), 90)
        if total and len(ys) > 2:
            xt = xb + math.copysign(7.0, dist_papel) * self.esc
            self._dim((xt, ys[0]), (x_ref, ys[0]), (x_ref, ys[-1]), 90)

    def cota_ord(self, xs, y_ref, dist_papel=12.0, x0=None, rotulos=None):
        """Cotas ordenadas (acumuladas a partir de x0), texto vertical — padrão de prancha de peça pré-moldada."""
        x0 = xs[0] if x0 is None else x0
        yb = y_ref + dist_papel * self.esc
        sg = 1 if dist_papel >= 0 else -1
        self.linha((min(xs), yb), (max(xs), yb), "COTA")
        for k, x in enumerate(xs):
            self.linha((x, y_ref + sg * 1.5 * self.esc), (x, yb + sg * 1.0 * self.esc), "COTA")
            xp, yp = self.P(x, yb)
            self._add(self.pr.msp.add_line((xp - 0.8, yp - 0.8), (xp + 0.8, yp + 0.8), dxfattribs={"layer": "COTA"}))
            t = rotulos[k] if rotulos else f"{x - x0:.0f}"
            self._add(self.pr.texto(xp - 0.6, yp + sg * 1.6, t, "cota", "COTA", "MIDDLE_LEFT" if sg > 0 else "MIDDLE_RIGHT", rot=90))

    def cota_diam(self, c, r, ang=45, prefixo="Ø"):
        ux, uy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        return self.chamada((c[0] + r * ux, c[1] + r * uy), (8 * ux, 8 * uy), f"{prefixo}{2*r:g}".replace(".", ","))

    def chamada(self, p_modelo, desloc_papel, texto, h="nota"):
        x0, y0 = self.P(p_modelo)
        x1, y1 = x0 + desloc_papel[0], y0 + desloc_papel[1]
        lado = 1 if desloc_papel[0] >= 0 else -1
        x2 = x1 + lado * (_wtext(texto, ALTURAS[h]) + 2)
        self._add(self.pr.msp.add_lwpolyline([(x0, y0), (x1, y1), (x2, y1)], dxfattribs={"layer": "CHAMADA"}))
        self._add(self.pr.msp.add_circle((x0, y0), 0.5, dxfattribs={"layer": "CHAMADA"}))
        return self._add(self.pr.texto(x1 + lado, y1 + 0.8, texto, h, "TEXTO", "BOTTOM_LEFT" if lado > 0 else "BOTTOM_RIGHT"))

    def barra(self, pts, pos, n, diam, espac=None, comp_cm=None, ponto_rotulo=None, desloc=(10, 8)):
        """Armadura em vista longitudinal + rótulo NBR 7191: 'N1 - 8 Ø16 c/15 C=250'."""
        self.poli(pts, "ARMADURA")
        if comp_cm is None:
            comp_cm = sum(math.dist(a, b) for a, b in zip(pts[:-1], pts[1:])) / 10
        rot = f"{pos} - {n} Ø{diam:g}".replace(".", ",") + (f" c/{espac:g}" if espac else "") + f" C={comp_cm:.0f}"
        self.pr.posicoes_desenho.add(pos)
        if ponto_rotulo is None:
            a, b = pts[len(pts) // 2 - 1], pts[len(pts) // 2]
            ponto_rotulo = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        self.chamada(ponto_rotulo, desloc, rot)
        return comp_cm

    def marcador_corte(self, p1, p2, letra, lado=1):
        (x1, y1), (x2, y2) = self.P(p1), self.P(p2)
        L = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        nx, ny = -uy * lado, ux * lado
        msp = self.pr.msp
        self._add(msp.add_line((x1, y1), (x2, y2), dxfattribs={"layer": "EIXO"}))
        for (x, y, s) in [(x1, y1, 1), (x2, y2, -1)]:
            self._add(msp.add_line((x, y), (x + ux * 6 * s, y + uy * 6 * s), dxfattribs={"layer": "INDICACAO"}))
            tip = (x + nx * 6, y + ny * 6)
            self._add(msp.add_line((x, y), tip, dxfattribs={"layer": "INDICACAO"}))
            for sgn in (1, -1):
                self._add(msp.add_line(tip, (tip[0] - nx * 2.2 + ux * sgn, tip[1] - ny * 2.2 + uy * sgn),
                                       dxfattribs={"layer": "INDICACAO"}))
            lx, ly = x + nx * 3.5 - ux * 5.5 * s, y + ny * 3.5 - uy * 5.5 * s   # letra ao lado da seta, para fora
            self._add(self.pr.texto(lx, ly, letra, "titulo", "TITULO", "MIDDLE_CENTER"))
        self.pr.refs.append(("CORTE", f"{letra}-{letra}"))

    def marcador_detalhe(self, c, r, num, ang=45, dist=6):
        x, y = self.P(c)
        rr = r / self.esc
        self._add(self.pr.msp.add_circle((x, y), rr, dxfattribs={"layer": "INDICACAO", "linetype": "ACAD_ISO02W100"}))
        ux, uy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        bx, by = x + ux * (rr + dist + 3.5), y + uy * (rr + dist + 3.5)
        self._add(self.pr.msp.add_line((x + ux * rr, y + uy * rr), (bx - ux * 3.5, by - uy * 3.5), dxfattribs={"layer": "INDICACAO"}))
        self._add(self.pr.msp.add_circle((bx, by), 3.5, dxfattribs={"layer": "INDICACAO"}))
        self._add(self.pr.texto(bx, by, str(num), "sub", "TITULO", "MIDDLE_CENTER"))
        self.pr.refs.append(("DETALHE", str(num)))

    def bbox_papel(self):
        if not self.ents:
            return None
        ext = bbox.extents(self.ents, fast=True)
        if not ext.has_data:
            return None
        b = (ext.extmin.x, ext.extmin.y, ext.extmax.x, ext.extmax.y)
        t = getattr(self, "_bbox_titulo", None)
        if t:
            b = (min(b[0], t[0]), min(b[1], t[1]), max(b[2], t[2]), max(b[3], t[3]))
        return b

    def _finalizar(self):
        b = self.bbox_papel()
        if not b:
            return
        cx, y = (b[0] + b[2]) / 2, b[1] - 8
        t1 = self.titulo.upper()
        w1 = _wtext(t1, ALTURAS["titulo"])
        self.pr.texto(cx, y, t1, "titulo", "TITULO", "BOTTOM_CENTER")
        self._add(self.pr.msp.add_line((cx - w1 / 2, y - 1.2), (cx + w1 / 2, y - 1.2), dxfattribs={"layer": "TITULO"}))
        self._add(self.pr.msp.add_line((cx - w1 / 2, y - 2.0), (cx + w1 / 2, y - 2.0), dxfattribs={"layer": "CHAMADA"}))
        self.pr.texto(cx, y - 6.5, f"ESC. 1:{self.esc:g}" + (f" — {self.subtitulo}" if self.subtitulo else ""), "nota", "TEXTO", "BOTTOM_CENTER")
        self._bbox_titulo = (cx - w1 / 2, y - 7, cx + w1 / 2, y + 5)
