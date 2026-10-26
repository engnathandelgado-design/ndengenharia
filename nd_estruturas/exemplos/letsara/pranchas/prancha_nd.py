"""prancha_nd.py — motor de pranchas técnicas da ND Engenharia (DXF + PDF em escala real).
Modelo em mm reais; papel em mm. Cada Vista: P_papel = origem + P_modelo / escala. Cotas com dimlfac = escala.
"""
from __future__ import annotations
import math
import re
import os, datetime
import ezdxf
from ezdxf import bbox
from ezdxf.enums import TextEntityAlignment

FORMATOS = {"A0": (1189, 841), "A1": (841, 594), "A2": (594, 420), "A3": (420, 297), "A4": (297, 210)}
def margens(fmt):
    m = 10 if fmt in ("A0", "A1") else 7
    return dict(esq=25, dir=m, sup=m, inf=m)

MASSA_ACO = {5.0: 0.154, 6.3: 0.245, 8.0: 0.395, 10.0: 0.617, 12.5: 0.963, 16.0: 1.578,
             20.0: 2.466, 22.0: 2.984, 25.0: 3.853, 32.0: 6.313, 40.0: 9.865}
# rev06e: padrão gráfico da usina (SP201/SP202/SP301/SP302): texto 1,8–2,0, cota 1,8 marrom com seta, armadura verde fina,
# concreto preto, chapa preta com hachura cinza, hierarquia de espessuras corte > vista > armadura > cota > hachura
# rev11 (26/10/2026, pedido do Nathan — legibilidade no celular e impresso): alturas no PAPEL (mm), iguais em qualquer escala
# (o motor desenha em mm de papel; h_modelo = h_papel × denominador). Cota ≥ 2,5; notas/rótulos ≥ 2,5; nomes de peça 3,5; títulos 5,0.
ALTURAS = {"min": 2.5, "nota": 2.5, "cota": 2.5, "peca": 3.5, "sub": 3.0, "titulo": 5.0, "grande": 6.0}
# rev11 (Nathan 26/10/2026 — quem lê na fábrica são pessoas idosas): folhas de DETALHAMENTO DE PEÇA (vão para a produção) com
# texto maior: cota 3,5; rótulos de barra/posição 3,5; tabelas e notas 3,0; títulos de vista 6,0; nome/seção/L da peça 8,0.
ALTURAS_GERAL = dict(ALTURAS)
ALTURAS_PECA = {"min": 3.0, "nota": 3.0, "cota": 3.5, "peca": 3.5, "sub": 3.5, "titulo": 6.0, "grande": 8.0}
MIN_TIPO = {"geral": dict(cota=2.5, texto=2.5), "peca": dict(cota=3.5, texto=3.0)}
_PECA_PREF = ("PL", "PF", "PC", "PM", "PG", "PE", "TS01", "I130", "VM01", "VB01", "LA01", "PP0", "PV01", "ES0", "MT01", "COB06", "COB07", "COB08", "COB09", "IC01", "EX01", "AR-", "PE0", "IC01")


def tipo_folha(desenho):
    """'peca' para as folhas de detalhamento que vão para a produção; 'geral' para plantas, cortes, montagem e gerais."""
    cod = str(desenho).replace("ND-LET-", "")
    return "peca" if cod.startswith(_PECA_PREF) and not cod.startswith("PP-") else "geral"
ALTURAS_CARIMBO = {"min": 1.6, "nota": 2.0, "cota": 1.8, "sub": 2.5, "titulo": 3.5, "grande": 5.0}   # selo: tamanhos da rev10
H_COTA_MIN = 2.5                            # gerar_tudo: ERRO se algum texto de cota sair menor que isto no papel
DIM_K, DIM_DLI = 0.65, 6.0                 # cadeias: distância à peça = 0,65 × a pedida pelo gerador; parcial → total 4,5 mm
COR_COTA = (149, 74, 0)                    # marrom da usina
CAMADAS = {
    "MOLDURA": (7, 50, "Continuous"), "CARIMBO": (7, 35, "Continuous"), "CARIMBO_FINO": (8, 18, "Continuous"),
    "CORTADO": (7, 35, "Continuous"), "VISTA": (7, 25, "Continuous"), "OCULTA": (8, 18, "ACAD_ISO02W100"),
    "EIXO": (8, 13, "ACAD_ISO10W100"), "ARMADURA": (3, 25, "Continuous"), "ARM_SECAO": (3, 25, "Continuous"),
    "ARM_TRANSV": (3, 18, "Continuous"), "ARM_PROT": (6, 35, "Continuous"), "ARM_PROT_SECAO": (6, 35, "Continuous"),
    "METALICA": (7, 25, "Continuous"), "TERRENO": (34, 25, "Continuous"), "HACHURA": (8, 9, "Continuous"),
    "COTA": (32, 13, "Continuous"), "TEXTO": (7, 18, "Continuous"), "TITULO": (7, 25, "Continuous"),
    "CHAMADA": (7, 13, "Continuous"), "INDICACAO": (7, 25, "Continuous"), "TABELA": (7, 25, "Continuous"),
    "TABELA_FINA": (8, 13, "Continuous"), "BOLHA": (8, 13, "Continuous"), "POSICAO": (1, 18, "Continuous"),
    "COR_FACHADA": (7, 0, "Continuous"),
}
# Emissão executiva (21/10/2026, decisão do Nathan): toda folha gerada sai liberada para produção e montagem.
# Uma revisão nova é acrescentada automaticamente (número = maior revisão da folha + 1) e a nota antiga
# "PARA APROVAÇÃO, NÃO EXECUTAR" é trocada. EMISSAO = None volta ao comportamento anterior.
EMISSAO = dict(data="21/10/2026", desc="EMISSÃO EXECUTIVA — LIBERADO PARA PRODUÇÃO E MONTAGEM", fase="EXECUTIVO — LIBERADO",
               nota="EMISSÃO EXECUTIVA — LIBERADO PARA PRODUÇÃO, ARMAÇÃO, CONCRETAGEM E MONTAGEM.")
# Reemissão do pacote rev09 (23/10/2026, DEC-045/047/048): depois da revisão da emissão executiva, mais uma revisão com a data
# abaixo; revisões manuais da folha com esta data viram a descrição dela (sem número próprio). Folha sem revisão manual
# nesta data recebe a descrição padrão. REEMISSAO = None desliga.
REEMISSAO = dict(data="23/10/2026", desc="REEMISSÃO EXECUTIVA (PACOTE REV09): PISOS +3,90/+7,30; NOMES E REFERÊNCIAS")
# 24/10/2026 (DEC-050/051): segunda reemissão do pacote rev09 — só nas folhas que têm revisão manual com esta data (numerada depois da REEMISSAO)
REEMISSAO2 = dict(data="24/10/2026")
# 25/10/2026 (pacote rev10, DEC-061/062): terceira reemissão — só nas folhas com revisão manual desta data
REEMISSAO3 = dict(data="25/10/2026")
# rev11 (26/10/2026): TODAS as folhas mudam (textos e cotas ≥ 2,5 mm no papel, imagens ≥ 400 ppi) — revisão automática em todas;
# as folhas com revisão manual nesta data acrescentam a descrição própria.
REEMISSAO4 = dict(data="26/10/2026", padrao="REV11: TEXTOS E COTAS ≥ 2,5 MM NO PAPEL; IMAGENS EM ALTA RESOLUÇÃO; PÉ DOS PILARES NO CÁLICE NOS CORTES")
_NOTAS_ANTIGAS = ("PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR.", "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR",
                  "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO.", "PARA APROVAÇÃO, NÃO EXECUTAR.", "PARA APROVAÇÃO, NÃO EXECUTAR")


try:                                                       # nomenclatura nova da obra (P1…, V200…): troca no texto desenhado
    from renomear import renomear as _RENOMEAR, MARCA_NOVO as _MNOVO
except Exception:                                          # obra sem nomes.json: texto como veio
    _RENOMEAR, _MNOVO = (lambda t: t), "\x01"


def _emissao_txt(s):
    if EMISSAO and isinstance(s, str):
        for a in _NOTAS_ANTIGAS:
            if a in s:
                s = s.replace(a, EMISSAO["nota"])
    return s


EMPRESA = dict(nome="ND ENGENHARIA E ASSESSORIA LTDA", cnpj="46.745.157/0001-47",
               rt="Eng. Civil Nathan Henrique Delgado", crea="CREA-SC 168298-1", site="ndengenharia.com",
               contato="WhatsApp (46) 92000-4685 · Saudade do Iguaçu/PR")
AREA_CORD = {9.5: 55.5, 12.7: 98.7, 15.2: 140.0,   # mm², cordoalhas de 7 fios CP-190 RB (NBR 7483 — conferir)
             4.0: 12.6, 5.0: 19.6, 6.0: 28.3, 7.0: 38.5, 8.0: 50.3}   # fios CP-175 RB (NBR 7482)
FONTE = "DejaVuSansCondensed.ttf"
# logos dos clientes no selo (campo à direita de CLIENTE/OBRA/LOCAL); chave = nome do cliente em maiúsculas
LOGOS_CLIENTES = {"MARQUES ENGENHARIA E CONSTRUÇÕES": os.path.join(os.path.dirname(os.path.abspath(__file__)), "logos", "marques.jpg")}
MEMORIA_NA_PRANCHA = False   # tabelas "MEMÓRIA..." / "VERIFICAÇÕES..." não entram nas pranchas de detalhamento (pedido do cliente)
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
        self.tipo = tipo_folha(self.dados.get("desenho", ""))                  # rev11: tamanhos de texto por tipo de folha
        ALTURAS.clear(); ALTURAS.update(ALTURAS_PECA if self.tipo == "peca" else ALTURAS_GERAL)
        self._carimbo_ativo, self._txt_pequenos = False, []
        if EMISSAO:
            self.dados["fase"] = EMISSAO["fase"]
        self.cor = cor
        self.revisoes, self.vistas, self.refs, self.blocos_livres = [], [], [], []
        self.posicoes_desenho, self.posicoes_tabela = set(), set()
        self.avisos_extra, self.imagens = [], []
        doc = ezdxf.new("R2018", setup=True, units=4)
        doc.header["$LTSCALE"] = 0.5
        doc.header["$PSLTSCALE"] = 0
        doc.header["$LWDISPLAY"] = 1
        self.doc, self.msp = doc, doc.modelspace()
        for nome, padrao, desc in (("ACAD_ISO02W100", [15.0, 12.0, -3.0], "ISO dashed __ __ __"),
                                   ("ACAD_ISO10W100", [18.0, 12.0, -3.0, 0.0, -3.0], "ISO dash dot __ . __ .")):
            if nome not in doc.linetypes:                                 # sem a definição o AutoCAD recusa abrir o DXF
                doc.linetypes.add(nome, pattern=padrao, description=desc)
        doc.styles.new("ND", dxfattribs={"font": fonte, "width": 1.0})
        for n, (c, lw, lt) in CAMADAS.items():
            doc.layers.add(n, color=c, lineweight=lw, linetype=lt)
        doc.layers.get("COTA").rgb = COR_COTA
        ds = doc.dimstyles.new("ND")
        for k, v in dict(dimtxsty="ND", dimtxt=ALTURAS["cota"], dimtsz=0, dimasz=3.0 if self.tipo == "peca" else 2.5, dimexo=1.5, dimexe=1.5,
                         dimdle=0, dimgap=0.5, dimdli=DIM_DLI, dimtad=1, dimtih=0, dimtoh=0, dimdec=0, dimzin=8,
                         dimdsep=ord(","), dimclrd=256, dimclre=256, dimclrt=256, dimlwd=18, dimlwe=18, dimtmove=0).items():
            setattr(ds.dxf, k, v)

    @property
    def quadro(self):
        m = self.m
        return (m["esq"], m["inf"], self.W - m["dir"], self.H - m["sup"])

    @property
    def carimbo_bbox(self):
        x0, y0, x1, y1 = self.quadro
        extra = 8 if self.dados.get("marca") else 0
        n = max(len(self.revisoes), 1) + (1 if EMISSAO and not getattr(self, "_emitida", False) else 0)
        return (x1 - 180, y0, x1, y0 + 78 + extra + 5 * n + 6)

    def texto(self, x, y, s, h="nota", camada="TEXTO", alinh="BOTTOM_LEFT", rot=0, registrar=True):
        hh = ALTURAS[h] if isinstance(h, str) else h
        if not isinstance(h, str) and not self._carimbo_ativo:          # rev11: altura numérica abaixo do mínimo sobe ao mínimo (nunca reduzir)
            hh = max(hh, MIN_TIPO[self.tipo]["texto"])
        if not self._carimbo_ativo and hh < MIN_TIPO[self.tipo]["texto"] - 1e-6 and str(s).strip():
            self._txt_pequenos.append((round(hh, 2), str(s)[:30]))
        s = _RENOMEAR(_emissao_txt(s))
        t = self.msp.add_text(s, height=hh, rotation=rot, dxfattribs={"layer": camada, "style": "ND"})
        t.set_placement((x, y), align=TextEntityAlignment[alinh])
        return t

    def linha(self, p1, p2, camada="CARIMBO"):
        return self.msp.add_line(p1, p2, dxfattribs={"layer": camada})

    def ret(self, x0, y0, x1, y1, camada="CARIMBO"):
        return self.msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True,
                                       dxfattribs={"layer": camada})

    def vista(self, nome, origem, escala, titulo=None, subtitulo=None, unidade="mm"):
        """unidade: "mm" (metálica) ou "cm" (concreto pré-moldado — NBR 7191/prática de fábrica)."""
        v = Vista(self, nome, origem, escala, titulo, subtitulo, unidade)
        self.vistas.append(v)
        return v

    def tabela(self, x, y_topo, titulo, cab, linhas, larg, h_lin=6.0, destaque_ultima=False):
        self.__dict__.setdefault("_tabs", []).append(dict(titulo=titulo, cab=list(cab), linhas=[[str(c) for c in l] for l in linhas]))
        if not MEMORIA_NA_PRANCHA and titulo.upper().startswith(("MEMÓRIA", "VERIFICAÇ", "TRANSITÓRIAS", "CHECAGEM")):
            return y_topo + 4          # prancha de detalhamento para o cliente: a memória fica no documento MC, não na prancha
        W = sum(larg)
        y = y_topo
        self.ret(x, y - 8, x + W, y, "TABELA")
        self.texto(x + W / 2, y - 4, titulo, "sub", "TITULO", "MIDDLE_CENTER")
        y -= 8
        hn = ALTURAS["nota"]
        for row_i, row in enumerate([cab] + linhas):
            camada = "TABELA" if row_i == 0 or (destaque_ultima and row_i == len(linhas)) else "TABELA_FINA"
            # rev08: texto que não cabe na coluna quebra em linhas dentro da célula (a linha da tabela cresce)
            cel = []
            for c, w in zip(row, larg):
                t = _RENOMEAR(_emissao_txt(str(c)))
                cel.append(quebrar(t, w - 1.6, hn) if _wtext(t, hn) > w - 1.6 else [t])
            nl = max(len(c) for c in cel)
            hr = h_lin if nl == 1 else max(h_lin, nl * hn * 1.45 + 1.6)
            self.linha((x, y - hr), (x + W, y - hr), camada)
            xx = x
            for ls, w in zip(cel, larg):
                for k, t in enumerate(ls):
                    yk = y - hr / 2 + (len(ls) - 1) * hn * 1.45 / 2 - k * hn * 1.45
                    self.texto(xx + w / 2, yk, _MNOVO + t, "nota", "TEXTO", "MIDDLE_CENTER")
                xx += w
            y -= hr
        xx = x
        for w in larg[:-1]:
            xx += w
            self.linha((xx, y_topo - 8), (xx, y), "TABELA_FINA")
        self.ret(x, y, x + W, y_topo, "TABELA")
        self.blocos_livres.append((x, y, x + W, y_topo, titulo))
        return y

    def tabela_aco(self, x, y_topo, barras, perda=0.10, aco="CA-50"):
        self.__dict__.setdefault("_aco", []).append(dict(perda=perda, aco=aco, barras=[{k: b[k] for k in ("pos", "diam", "qtd", "comp", "forma", "trechos", "esp", "obs") if k in b} for b in barras]))
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

    def tabela_cordoalhas(self, x, y_topo, cordoalhas, L_pista_m, Ep=195e3, fptk=1900.0, nome="CORDOALHAS", cunha_mm=6.0, tol=0.05):
        """cordoalhas: dict(pos='C1', diam=12.7, qtd=2, y=51 (mm da base), forca=137 (kN/cordoalha na pista),
        isol=3350 (mm isolado, 0 = aderente) e local='CENTRO'|'PONTAS'). ΔL teórico = F·L_pista/(Ep·Ap) (mm).
        Confere σpi ≤ min(0,77 fptk; 0,85 fpyk), fpyk = 0,9 fptk (pré-tração, RB — NBR 6118 9.6.1.2.1, conferir).
        Registra as posições como tabeladas (as cordoalhas desenhadas com v.barra não viram ERRO)."""
        lim, linhas, av = min(0.77 * fptk, 0.85 * 0.9 * fptk), [], []
        for c in cordoalhas:
            Ap = AREA_CORD[float(c["diam"])]
            sig = c["forca"] * 1e3 / Ap
            dL0 = c["forca"] * 1e3 * L_pista_m * 1e3 / (Ep * Ap)          # alongamento elástico da pista inteira (cabeceira a cabeceira)
            dL = dL0 + cunha_mm                                            # a medir no macaco: + acomodação das cunhas (perda a compensar)
            c["_dL0"], c["_dL"] = dL0, dL
            if sig > lim + 1e-6:
                av.append(("ERRO", f"{c['pos']}: σpi = {sig:.0f} MPa > {lim:.0f} MPa"))
            isol = f"{c['isol']:.0f} {c.get('local', 'PONTAS')}" if c.get("isol") else "ADERENTE"
            linhas.append([c["pos"], f"{c['diam']:g}".replace(".", ","), c["qtd"], f"{c['y']:.0f}",
                           f"{c['forca']:.1f}".replace(".", ","), f"{dL:.0f}", isol])
            self.posicoes_tabela.add(c["pos"])
        y = self.tabela(x, y_topo, f"{nome} CP-{fptk/10:.0f} RB — PISTA {L_pista_m:g} m".replace(".", ","),
                        ["POS", "Ø (mm)", "QUANT", "y (mm)", "F (kN)", "ΔL MEDIR (mm)", "ISOLAM. (mm)"],
                        linhas, [12, 14, 14, 14, 18, 22, 34])
        # rev08 (22/10/2026, pedido do Nathan): alongamento para a pista de 60 m explicado embaixo da tabela
        c0 = cordoalhas[0]
        Ap0 = AREA_CORD[float(c0["diam"])]
        txt = (f"Alongamento para a pista de {L_pista_m:g} m entre cabeceiras (todas as peças da pista protendidas juntas): "
               f"ΔL = F·L/(Ep·Ap) = {c0['forca']:.1f} kN × {L_pista_m:g} m / ({Ep/1e3:g} GPa × {Ap0:g} mm²) = {c0['_dL0']:.0f} mm "
               f"+ {cunha_mm:g} mm de acomodação das cunhas = {c0['_dL']:.0f} mm a medir por {'fio' if 'FIO' in nome.upper() else 'cordoalha'}, "
               f"(Com pré-carga de 10 % para alinhar o cabo, o medido a partir dela é 0,9 × {c0['_dL0']:.0f} + {cunha_mm:g} = {0.9 * c0['_dL0'] + cunha_mm:.0f} mm.) "
               f"Tolerância ±{tol*100:.0f} % entre o medido e o teórico (NBR 14931 — conferir); fora dela, parar e verificar atrito, manômetro e o Ep do certificado do lote. "
               f"Se a pista usada tiver outro comprimento, ΔL é proporcional ao comprimento.")
        txt = re.sub(r"(?<=\d)\.(?=\d)", ",", txt).replace(",0 ", " ")          # só a vírgula decimal (o ponto final fica)
        hh = ALTURAS["min"]
        yt = yy = y - 2.5                                                 # 2,5 mm abaixo da tabela (folga mínima do verificar = 2 mm)
        for k, lin in enumerate(quebrar(txt, 128, hh)):
            self.texto(x, yy - hh, lin, "min")
            yy -= hh * 1.55
        self.blocos_livres.append((x, yy, x + 128, yt, "NOTA ALONGAMENTO"))
        y = yy
        self.avisos_extra += av                     # entram no verificar()/salvar()
        return dict(y_base=y, avisos=av, sig_lim=lim)

    def legenda_armadura(self, x, y_topo, protensao=True):
        """Legenda (rev06e, padrão usina): aço passivo em verde (longitudinal mais grossa), protensão em magenta."""
        self.texto(x, y_topo - ALTURAS["sub"], "LEGENDA DAS ARMADURAS", "sub", "TITULO")
        y = y_topo - ALTURAS["sub"] - 6
        itens = [("ARMADURA", "longitudinal (barras N, tirantes, pele)"), ("ARM_TRANSV", "transversal (estribos, grampos, suspensão, costura)")]
        if protensao:
            itens.append(("ARM_PROT", "protensão (cordoalhas)"))
        for cam, txt in itens:
            self.linha((x, y + 1), (x + 14, y + 1), cam)
            self.texto(x + 17, y, txt, "nota")
            y -= 5
        self.blocos_livres.append((x, y, x + 170, y_topo, "LEGENDA DAS ARMADURAS"))
        return y

    def notas(self, x, y_topo, linhas, largura=170, titulo="NOTAS"):
        """Notas numeradas, quebra pela largura real. Use f-strings com os parâmetros (nota paramétrica)."""
        h = ALTURAS["nota"]
        linhas = [_RENOMEAR(_emissao_txt(t)) for t in linhas]   # troca antes de quebrar; as linhas quebradas não passam de novo
        self.texto(x, y_topo - ALTURAS["sub"], titulo, "sub", "TITULO")
        y = y_topo - ALTURAS["sub"] - 4
        for i, s in enumerate(linhas, 1):
            for k, p in enumerate(quebrar(f"{i}. {s}", largura - 6, h)):
                self.texto(x + (0 if k == 0 else 4), y - h, _MNOVO + p, "nota")
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
        self.__dict__.setdefault("_aco", []).append(dict(perda=perda, aco=aco, barras=[{k: b[k] for k in ("pos", "diam", "qtd", "comp", "forma", "trechos", "esp", "obs") if k in b} for b in barras]))
        """Relação do aço com croqui de dobramento (padrão de mercado BIM). barras: dict(pos, diam, qtd, comp (cm),
        forma=[(x,y) cm ...] polilinha da barra, trechos=['84','14',...] rótulos na ordem dos segmentos)."""
        larg = [13, 13, 14, 20, 66, 20, 20]
        W = sum(larg)
        cab = ["POS", "Ø", "QUANT", "C. UNIT (cm)", "CROQUI (cm)", "C. TOTAL (m)", "MASSA (kg)"]
        self.ret(x, y_topo - 8, x + W, y_topo, "TABELA")
        self.texto(x + W / 2, y_topo - 4, "RELAÇÃO DO AÇO — CROQUIS DE DOBRAMENTO", "sub", "TITULO", "MIDDLE_CENTER")
        y = y_topo - 8
        hn = ALTURAS["nota"]
        cel = [quebrar(c, w - 1.6, hn) if _wtext(c, hn) > w - 1.6 else [c] for c, w in zip(cab, larg)]   # rev11: cabeçalho quebra na célula
        hc = max(6.0, max(len(c_) for c_ in cel) * hn * 1.45 + 1.6)
        self.linha((x, y - hc), (x + W, y - hc), "TABELA")
        xx = x
        for ls, w in zip(cel, larg):
            for k, t in enumerate(ls):
                self.texto(xx + w / 2, y - hc / 2 + (len(ls) - 1) * hn * 1.45 / 2 - k * hn * 1.45, t, "nota", "TEXTO", "MIDDLE_CENTER")
            xx += w
        y -= hc
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

    def cabecalho_peca(self, marca, titulo, linha2, largura=500):
        """Quadro no canto superior esquerdo: nomes das peças (grande), título (seção, comprimento) e linha de dados.
        rev08: os nomes vêm por extenso (P29, P30, P31, P32); se nomes + título não cabem numa linha, o título desce para
        uma 2ª linha e o quadro cresce (a altura usada fica em self.cab_y0 para quem desenha abaixo)."""
        Q = self.quadro
        marca = _RENOMEAR(marca)                            # rev08: nomes das peças (P1…, V200…) antes de medir
        wm, wt = _wtext(marca, ALTURAS["grande"]), _wtext(titulo, ALTURAS["titulo"])
        duas = wm + 8 + wt > largura - 16
        larg = max(largura, (max(wm, wt) if duas else wm + 8 + wt) + 16)     # o quadro acompanha o texto mais longo
        y0 = Q[3] - 30                                                    # altura fixa: nada abaixo precisa mudar
        self.ret(Q[0] + 4, y0, Q[0] + larg, Q[3] - 4, "CARIMBO")
        if duas:                                                          # linha de dados, nomes e título em 3 linhas
            self.texto(Q[0] + 10, Q[3] - 10, linha2, "nota", "TEXTO")
            self.texto(Q[0] + 10, Q[3] - 18.5, _MNOVO + marca, "grande", "TITULO")
            self.texto(Q[0] + 10, Q[3] - 26.5, titulo, "titulo", "TITULO")
        else:
            self.texto(Q[0] + 10, Q[3] - 14, linha2, "nota", "TEXTO")
            self.texto(Q[0] + 10, Q[3] - 24, _MNOVO + marca, "grande", "TITULO")
            self.texto(Q[0] + 10 + wm + 8, Q[3] - 24, titulo, "titulo", "TITULO")
        largura = larg
        self.cab_y0 = y0
        self.blocos_livres.append((Q[0] + 4, y0, Q[0] + largura, Q[3] - 4, "CABEÇALHO"))

    def revisao(self, rev, data, descricao):
        self.revisoes.append((rev, data, descricao))
        self.dados["rev"] = rev

    def _moldura_carimbo(self):
        """rev11: o carimbo (selo padrão ND) mantém as alturas de texto da rev10 — o aumento vale para os desenhos."""
        salvo = dict(ALTURAS)
        ALTURAS.update(ALTURAS_CARIMBO)
        self._carimbo_ativo = True
        try:
            return self._moldura_carimbo0()
        finally:
            ALTURAS.clear(); ALTURAS.update(salvo)
            self._carimbo_ativo = False

    def _moldura_carimbo0(self):
        self._emitir()
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
        for a, b, lab, val in [(0, 32, "ESCALA", esc), (32, 60, "DATA", d["data"]), (60, 100, "DESENHO", d["desenhista"]),
                               (100, 140, "VERIFICADO", d["verificado"] or "-"), (140, 180, "APROVADO", d.get("aprovado") or "-")]:
            if a:
                self.linha((cx0 + a, y), (cx0 + a, y + h2))
            self.texto(cx0 + a + 1.5, y + h2 - 2.5, lab, "min")
            self.texto(cx0 + (a + b) / 2, y + 3.2, val, "nota", alinh="MIDDLE_CENTER")
        y += h2
        h3 = 14
        self.ret(cx0, y, cx1, y + h3)
        self.texto(cx0 + 1.5, y + h3 - 2.5, "CONTEÚDO", "min")
        parts = quebrar(_RENOMEAR(d["conteudo"]), L - 8, ALTURAS["sub"])[:2]
        for k, p in enumerate(parts):
            self.texto(cx0 + L / 2, y + (5.5 if len(parts) == 1 else 7.6 - k * 4.6), _MNOVO + p, "sub", "TITULO", "MIDDLE_CENTER")
        y += h3
        if d.get("marca"):                                  # faixa da peça (prancha de produção): marca, quantidade, peso
            h35 = 8
            self.ret(cx0, y, cx1, y + h35)
            for a, b, lab, val in [(0, 50, "PEÇAS" if len(_RENOMEAR(str(d["marca"])).split(",")) > 1 or " a " in _RENOMEAR(str(d["marca"])) else "PEÇA", d["marca"]), (50, 90, "QUANTIDADE", str(d.get("qtd", "-"))),
                                   (90, 135, "PESO (kN)", str(d.get("peso", "-"))), (135, 180, "VOLUME (m³)", str(d.get("volume", "-")))]:
                if a:
                    self.linha((cx0 + a, y), (cx0 + a, y + h35))
                self.texto(cx0 + a + 1.5, y + h35 - 2.5, lab, "min")
                val = _RENOMEAR(str(val))
                if _wtext(val, ALTURAS["nota"]) > b - a - 3:              # rev08: lista de peças longa → 2 linhas menores
                    ls = quebrar(val, b - a - 3, ALTURAS["min"])
                    if len(ls) > 2:
                        ls = [ls[0], ls[1].rstrip(",") + " …"]
                    for kk, t in enumerate(ls):
                        self.texto(cx0 + (a + b) / 2, y + (3.9 if len(ls) > 1 else 2.2) - kk * 2.6, _MNOVO + t, "min", "TITULO", "MIDDLE_CENTER")
                else:
                    self.texto(cx0 + (a + b) / 2, y + 2.2, _MNOVO + val, "nota", "TITULO", "MIDDLE_CENTER")
            y += h35
        h4 = 22                                             # cliente / obra / local + campo da logo do cliente
        self.ret(cx0, y, cx1, y + h4)
        lx0 = cx1 - 26
        self.linha((lx0, y), (lx0, y + h4))
        for k, (lab, val) in enumerate([("CLIENTE", d["cliente"]), ("OBRA", d["obra"]), ("LOCAL", d["local"])]):
            yy = y + h4 - 6 - k * 6
            self.texto(cx0 + 1.5, yy, lab + ":", "min")
            for kk, p in enumerate(quebrar(val, lx0 - cx0 - 20, ALTURAS["nota"])[:1]):
                self.texto(cx0 + 18, yy, p, "nota")
        logo = d.get("logo_cliente") or LOGOS_CLIENTES.get(str(d["cliente"]).upper())
        if logo and os.path.exists(logo):
            self.imagens.append((lx0 + 2, y + 1, cx1 - 2, y + h4 - 1, logo))
        else:
            self.texto((lx0 + cx1) / 2, y + h4 / 2, "LOGO DO CLIENTE", "min", alinh="MIDDLE_CENTER")
        y += h4
        h5 = 20
        self.ret(cx0, y, cx1, y + h5)
        self.texto(cx0 + 3, y + 6, "ND", 7.0, "TITULO")
        self.texto(cx0 + 19, y + h5 - 5.5, EMPRESA["nome"], "sub", "TITULO")
        self.texto(cx0 + 19, y + h5 - 9.5, f"CNPJ {EMPRESA['cnpj']} · {EMPRESA['site']} · {EMPRESA['contato']}", "min")
        self.texto(cx0 + 19, y + 5.8, f"RESP. TÉCNICO: {EMPRESA['rt']} — {EMPRESA['crea']}", "min")
        self.texto(cx0 + 19, y + 2.0, f"ART Nº: {d.get('art') or '________________'}", "min")
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
            self.texto(cx0 + 41.5, y + 1.5, _MNOVO + ds[:70], "min")   # histórico de revisões fica como foi emitido
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
        # rev11: tamanhos mínimos no papel por tipo de folha (peça: cota 3,5 / texto 3,0; geral: 2,5 / 2,5)
        mn = MIN_TIPO[self.tipo]
        ds_ = self.doc.dimstyles.get("ND")
        if ds_.dxf.dimtxt < mn["cota"] - 1e-6:
            avisos.append(("ERRO", f"texto de cota {ds_.dxf.dimtxt:g} mm < {mn['cota']:g} mm (folha de {self.tipo})"))
        for hh_, t_ in self._txt_pequenos[:5]:
            avisos.append(("ERRO", f"texto de {hh_:g} mm < {mn['texto']:g} mm (folha de {self.tipo}): '{t_}'"))
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
                    av.append(("AVISO", f"textos sobrepostos: '{textos[i][1][:28]}' x '{textos[j][1][:28]}' @({ri[0]:.0f},{ri[1]:.0f})"))
        for r, txt, dono in textos:
            for a, b, d2, lay in segs:
                if dono is not None and d2 == dono:
                    continue
                if _seg_rect(a, b, r):
                    av.append(("AVISO", f"linha ({lay}) cruza o texto '{txt[:30]}' @({r[0]:.0f},{r[1]:.0f})"))
                    break
        return av

    def _emitir(self):
        if EMISSAO and not getattr(self, "_emitida", False):
            tardias = []                                           # reemissões de 24/10 e 25/10 (só nas folhas com revisão manual na data)
            for RE in (REEMISSAO2, REEMISSAO3, REEMISSAO4):
                if not RE:
                    continue
                nv = [d for _, dt, d in self.revisoes if dt == RE["data"]]
                self.revisoes = [t for t in self.revisoes if t[1] != RE["data"]]
                if RE.get("padrao"):
                    nv = [RE["padrao"]] + nv
                if nv:
                    tardias.append((RE["data"], nv))
            if not self.revisoes and tardias:                      # folha nova: só as emissões dessas datas
                for k, (dt, nv) in enumerate(tardias):
                    self.revisoes.append((f"{k:02d}", dt, "; ".join(nv)))
                    self.dados["rev"], self.dados["data"] = f"{k:02d}", dt
                self._emitida = True
                return
            self._emitir1()
            for dt, nv in tardias:
                r = f"{int(self.dados['rev']) + 1:02d}"
                self.revisoes.append((r, dt, "; ".join(nv)))
                self.dados["rev"], self.dados["data"] = r, dt
            self._emitida = True

    def _emitir1(self):
        if True:
            nums = [int(r) for r, _, _ in self.revisoes if str(r).isdigit()] or ([int(self.dados["rev"])] if str(self.dados.get("rev", "")).isdigit() else [0])
            if not self.revisoes:
                self.revisoes.append((self.dados["rev"], self.dados["data"], "EMISSÃO INICIAL"))
            novas = [d for _, dt, d in self.revisoes if REEMISSAO and dt == REEMISSAO["data"]]
            self.revisoes = [t for t in self.revisoes if not (REEMISSAO and t[1] == REEMISSAO["data"])]
            if not self.revisoes and novas:                       # folha nova do pacote rev09: só a emissão desta data
                self.revisoes.append(("00", REEMISSAO["data"], "; ".join(novas)))
                self.dados["rev"], self.dados["data"] = "00", REEMISSAO["data"]
                return
            nums = [int(r) for r, _, _ in self.revisoes if str(r).isdigit()] or nums
            r = f"{max(nums) + 1:02d}"
            self.revisoes.append((r, EMISSAO["data"], EMISSAO["desc"]))
            self.dados["rev"], self.dados["data"] = r, EMISSAO["data"]
            if REEMISSAO:
                r = f"{int(r) + 1:02d}"
                self.revisoes.append((r, REEMISSAO["data"], "; ".join(novas) if novas else REEMISSAO["desc"]))
                self.dados["rev"], self.dados["data"] = r, REEMISSAO["data"]

    def salvar(self, base, png_dpi=110):
        self.ppi_imagens = []
        for v in self.vistas:
            v._finalizar()
        self._moldura_carimbo()
        avisos = self.verificar()
        import os, json as _json
        with open(base + ".tabelas.json", "w", encoding="utf-8") as fh:
            _json.dump(dict(folha=os.path.basename(base), dados=getattr(self, "dados", {}), tabelas=self.__dict__.get("_tabs", []),
                            aco=self.__dict__.get("_aco", [])), fh, ensure_ascii=False, indent=1, default=str)
        self.doc.saveas(base + ".dxf")
        _exportar_pdf(self.doc, base + ".pdf", self.W, self.H, self.cor)
        import os as _os
        for *_, cam in self.imagens:                   # rev08: imagem que falta é ERRO (antes a folha saía com o quadro vazio)
            if not _os.path.exists(cam):
                avisos.append(("ERRO", f"imagem não encontrada: {cam}"))
        try:
            import pymupdf
            k = 72 / 25.4
            if self.imagens:
                pdf = pymupdf.open(base + ".pdf")
                pg = pdf[0]
                for x0, y0, x1, y1, cam in self.imagens:
                    if not _os.path.exists(cam):
                        continue
                    rr = pymupdf.Rect(x0 * k + 1, (self.H - y1) * k + 1, x1 * k - 1, (self.H - y0) * k - 1)
                    if cam.lower().endswith(".pdf"):                      # rev11: desenho vetorial (matplotlib → PDF) entra como vetor
                        src = pymupdf.open(cam)
                        pg.show_pdf_page(rr, src, 0, keep_proportion=True)
                        src.close()
                        continue
                    pg.insert_image(rr, filename=cam, keep_proportion=True)
                    # rev11 (26/10/2026): nitidez no zoom do celular — raster com ≥ 400 ppi efetivos no tamanho impresso
                    try:
                        from PIL import Image as _Im
                        with _Im.open(cam) as _im:
                            wpx, hpx = _im.size
                        ppi = max(wpx / ((x1 - x0) / 25.4), hpx / ((y1 - y0) / 25.4))
                        self.ppi_imagens.append((_os.path.basename(cam), wpx, hpx, round(ppi)))
                        if ppi < PPI_MIN and not any(k_ in _os.path.basename(cam).lower() for k_ in ("logo", "marques")):   # logos: exceção
                            avisos.append(("AVISO", f"imagem com {ppi:.0f} ppi (< {PPI_MIN}) no tamanho impresso: {_os.path.basename(cam)} — re-renderizar"))
                    except Exception:
                        pass
                # rev11 (26/10/2026): reescreve o PDF com as imagens comprimidas sem perda (FlateDecode). O salvamento incremental
                # deixava o raster do render 3D cru no arquivo (4500 × 7800 px = 100 MB por folha, push recusado no GitHub).
                pdf.save(base + ".tmp.pdf", garbage=3, deflate=True, deflate_images=True, deflate_fonts=True)
                pdf.close()
                os.replace(base + ".tmp.pdf", base + ".pdf")
                chk = pymupdf.open(base + ".pdf")
                n_img = len(chk[0].get_images())
                if n_img < len({c for *_, c in self.imagens if _os.path.exists(c) and not c.lower().endswith(".pdf")}):
                    avisos.append(("ERRO", f"PDF saiu com {n_img} imagens de {len(self.imagens)} previstas"))
                chk.close()
            pymupdf.open(base + ".pdf")[0].get_pixmap(dpi=png_dpi).save(base + ".png")
        except Exception as e:
            avisos.append(("ERRO", f"falha ao inserir imagens/PNG: {e}"))
        if os.environ.get("AVISOS_LOG"):                 # rev08: log depois das imagens, para os erros delas entrarem
            with open(os.environ["AVISOS_LOG"], "a", encoding="utf-8") as fh:
                fh.write(_json.dumps({"folha": os.path.basename(base), "avisos": avisos, "imagens": self.ppi_imagens}, ensure_ascii=False) + "\n")
        return avisos


PPI_MIN = 400                                   # rev11: resolução mínima das imagens raster no tamanho impresso
_CAP, _DESC = 0.729, 0.236                      # DejaVu Sans: altura de maiúscula e descendente (fração do corpo)


def _fonte_ttf():
    import glob
    for c in ("/usr/share/fonts/truetype/dejavu/" + FONTE, *glob.glob("/usr/share/fonts/**/" + FONTE, recursive=True)):
        if os.path.exists(c):
            return c
    return None


def _textos_pdf(doc, ctx, cor):
    """TEXT do modelspace e MTEXT das cotas como (texto, x, y, h, rot, halign, valign, rgb) em mm (texto real no PDF)."""
    def rgb(e):
        if not cor:
            return (0, 0, 0)
        try:
            c = ctx.resolve_all(e).color
            return tuple(int(c[i:i + 2], 16) / 255 for i in (1, 3, 5))
        except Exception:
            return (0, 0, 0)
    out = []
    for e in doc.modelspace():
        t = e.dxftype()
        if t == "TEXT":
            ha, va = e.dxf.get("halign", 0), e.dxf.get("valign", 0)
            pt = e.dxf.insert if (ha == 0 and va == 0) or ha in (3, 5) else e.dxf.get("align_point", e.dxf.insert)
            out.append((e.dxf.text, pt[0], pt[1], e.dxf.height, e.dxf.get("rotation", 0.0), ha if ha != 4 else 1, va if ha != 4 else 2, rgb(e)))
        elif t == "DIMENSION":
            for v in e.virtual_entities():
                if v.dxftype() == "MTEXT":
                    ap = v.dxf.get("attachment_point", 5)
                    ha = (ap - 1) % 3
                    va = {0: 3, 1: 2, 2: 1}[(ap - 1) // 3]
                    rot = v.dxf.get("rotation", 0.0)
                    if v.dxf.hasattr("text_direction"):
                        dx, dy = v.dxf.text_direction[0], v.dxf.text_direction[1]
                        rot = math.degrees(math.atan2(dy, dx))
                    v.dxf.layer = e.dxf.layer
                    out.append((v.plain_text(), v.dxf.insert[0], v.dxf.insert[1], v.dxf.char_height, rot, ha, va, rgb(v)))
    return out


def _exportar_pdf(doc, caminho, W, H, cor=True):
    """PDF vetorial pelo ezdxf. rev06f: os textos vão como TEXTO REAL (fonte DejaVu embutida) e não como curvas — o PDF
    das 66 folhas caiu de ~60 MB para poucos MB (antes 85 % do arquivo eram os contornos das letras) e o texto fica pesquisável."""
    from ezdxf.addons.drawing import Frontend, RenderContext, pymupdf as pmb, layout, config
    import pymupdf
    ttf = _fonte_ttf()
    be = pmb.PyMuPdfBackend()
    cfg = config.Configuration(
        background_policy=config.BackgroundPolicy.WHITE,
        color_policy=config.ColorPolicy.COLOR if cor else config.ColorPolicy.BLACK,
        lineweight_policy=config.LineweightPolicy.ABSOLUTE, lineweight_scaling=1.0,
        min_lineweight=0.13 / 0.3527777, hatch_policy=config.HatchPolicy.NORMAL,
        text_policy=config.TextPolicy.IGNORE if ttf else config.TextPolicy.FILLING)
    ctx = RenderContext(doc)
    Frontend(ctx, be, config=cfg).draw_layout(doc.modelspace())
    page = layout.Page(W, H, layout.Units.mm, margins=layout.Margins.all(0))
    data = be.get_pdf_bytes(page, settings=layout.Settings(fit_page=False, scale=1.0))
    if ttf:
        k = 72 / 25.4
        pdf = pymupdf.open("pdf", data)
        pg = pdf[0]
        F = pymupdf.Font(fontfile=ttf)
        pg.insert_font(fontname="ND", fontfile=ttf)
        for s, x, y, h, rot, ha, va, c in _textos_pdf(doc, ctx, cor):
            s = s.replace("\n", " ").replace("\\P", " ")
            if not s.strip():
                continue
            fs = h / _CAP * k
            w = F.text_length(s, fontsize=fs)
            dx = -w * (0, 0.5, 1)[min(ha, 2)]
            dy = {0: 0.0, 1: _DESC * fs, 2: -h * k / 2, 3: -h * k}[va]          # deslocamento da linha de base (pt, y para cima)
            a = math.radians(rot)
            px, py = x * k, (H - y) * k
            bx = px + dx * math.cos(a) - dy * math.sin(a)
            by = py - (dx * math.sin(a) + dy * math.cos(a))
            pg.insert_text((bx, by), s, fontsize=fs, fontname="ND", color=c,
                           morph=(pymupdf.Point(bx, by), pymupdf.Matrix(rot)) if abs(rot) > 1e-6 else None)
        data = pdf.tobytes(garbage=3, deflate=True)
    with open(caminho, "wb") as f:
        f.write(data)


class Vista:
    def __init__(self, pr, nome, origem, esc, titulo=None, subtitulo=None, unidade="mm"):
        self.pr, self.nome, self.o, self.esc = pr, nome, origem, esc
        self.titulo, self.subtitulo = titulo or nome, subtitulo
        if unidade not in ("mm", "cm"):
            raise ValueError("unidade deve ser 'mm' ou 'cm'")
        self.unidade = unidade
        self.fator = 1.0 if unidade == "mm" else 0.1          # modelo sempre em mm; o texto da cota sai na unidade pedida
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
            h.set_solid_fill(color=256)
        else:
            h.set_pattern_fill(padrao, color=256, scale=escala_papel, angle=angulo)     # rev06e: sem color=256 o ezdxf pinta de preto (cor 7)
        return self._add(h)

    def eixo(self, p1, p2, ext=300):
        (x1, y1), (x2, y2) = p1, p2
        L = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        return self.linha((x1 - ux * ext, y1 - uy * ext), (x2 + ux * ext, y2 + uy * ext), "EIXO")

    def texto(self, p, s, h="nota", alinh="BOTTOM_LEFT", camada="TEXTO", rot=0):
        x, y = self.P(p)
        return self._add(self.pr.texto(x, y, s, h, camada, alinh, rot))

    def fmt(self, v_mm):
        """Número na unidade da vista: mm inteiro ou cm com uma decimal só quando precisa (25 mm -> '2,5')."""
        if self.fator == 1:
            return f"{v_mm:.0f}"
        return f"{v_mm / 10:.1f}".rstrip("0").rstrip(".").replace(".", ",")

    def _dim(self, base, p1, p2, ang, texto="<>"):
        self._cotas.append((ang % 180, tuple(sorted([tuple(round(c, 1) for c in p1), tuple(round(c, 1) for c in p2)]))))
        d = self.pr.msp.add_linear_dim(base=self.P(base), p1=self.P(p1), p2=self.P(p2), angle=ang, text=texto,
                                       dimstyle="ND", override={"dimlfac": self.esc * self.fator, "dimdec": 1,
                                                                "dimzin": 8}, dxfattribs={"layer": "COTA"})
        d.render()
        return self._add(d.dimension)

    def cota(self, p1, p2, dist_papel=-10.0, ang=0, texto="<>"):
        dist_papel = dist_papel * DIM_K
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
        dist_papel = dist_papel * DIM_K
        yb = y_ref + dist_papel * self.esc
        for a, b in zip(xs[:-1], xs[1:]):
            self._dim((a, yb), (a, y_ref), (b, y_ref), 0)
        if total and len(xs) > 2:
            yt = yb + math.copysign(DIM_DLI, dist_papel) * self.esc
            self._dim((xs[0], yt), (xs[0], y_ref), (xs[-1], y_ref), 0)

    def cota_v(self, ys, x_ref, dist_papel=-10.0, total=True):
        dist_papel = dist_papel * DIM_K
        xb = x_ref + dist_papel * self.esc
        for a, b in zip(ys[:-1], ys[1:]):
            self._dim((xb, a), (x_ref, a), (x_ref, b), 90)
        if total and len(ys) > 2:
            xt = xb + math.copysign(DIM_DLI, dist_papel) * self.esc
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
            t = rotulos[k] if rotulos else self.fmt(x - x0)
            self._add(self.pr.texto(xp - 0.6, yp + sg * 1.6, t, "cota", "COTA", "MIDDLE_LEFT" if sg > 0 else "MIDDLE_RIGHT", rot=90))

    def cota_ord_v(self, ys, x_ref, dist_papel=12.0, y0=None, rotulos=None):
        """Cotas ordenadas verticais (acumuladas a partir de y0), texto horizontal — peça desenhada em pé."""
        y0 = ys[0] if y0 is None else y0
        xb = x_ref + dist_papel * self.esc
        sg = 1 if dist_papel >= 0 else -1
        self.linha((xb, min(ys)), (xb, max(ys)), "COTA")
        for k, y in enumerate(ys):
            self.linha((x_ref + sg * 1.5 * self.esc, y), (xb + sg * 1.0 * self.esc, y), "COTA")
            xp, yp = self.P(xb, y)
            self._add(self.pr.msp.add_line((xp - 0.8, yp - 0.8), (xp + 0.8, yp + 0.8), dxfattribs={"layer": "COTA"}))
            t = rotulos[k] if rotulos else self.fmt(y - y0)
            self._add(self.pr.texto(xp + sg * 1.4, yp + 0.6, t, "cota", "COTA", "BOTTOM_LEFT" if sg > 0 else "BOTTOM_RIGHT"))

    def chapa(self, x, y, w, h, escala_papel=0.25, camada="METALICA"):
        """Chapa/inserto metálico: contorno preto + hachura ANSI31 cinza fina (padrão da usina; chaparia sempre hachurada)."""
        pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        self.poli(pts, camada, fechada=True)
        return self.hachura(pts, "ANSI31", escala_papel, "HACHURA", 0)

    def cota_diam(self, c, r, ang=45, prefixo="Ø"):
        ux, uy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        return self.chamada((c[0] + r * ux, c[1] + r * uy), (8 * ux, 8 * uy), f"{prefixo}{2*r:g}".replace(".", ","))

    def chamada(self, p_modelo, desloc_papel, texto, h="nota"):
        x0, y0 = self.P(p_modelo)
        x1, y1 = x0 + desloc_papel[0], y0 + desloc_papel[1]
        lado = 1 if desloc_papel[0] >= 0 else -1
        x2 = x1 + lado * (_wtext(texto, ALTURAS[h]) + 2)
        self._add(self.pr.msp.add_lwpolyline([(x0, y0), (x1, y1), (x2, y1)], dxfattribs={"layer": "CHAMADA"}))
        L_ = math.hypot(x1 - x0, y1 - y0) or 1.0                                  # rev06e: seta cheia na ponta (padrão usina)
        ux_, uy_ = (x0 - x1) / L_, (y0 - y1) / L_
        bx_, by_ = x0 - ux_ * 1.2, y0 - uy_ * 1.2
        sh_ = self.pr.msp.add_solid([(x0, y0), (bx_ - uy_ * 0.3, by_ + ux_ * 0.3), (bx_ + uy_ * 0.3, by_ - ux_ * 0.3)], dxfattribs={"layer": "CHAMADA"})
        self._add(sh_)
        return self._add(self.pr.texto(x1 + lado, y1 + 0.8, texto, h, "TEXTO", "BOTTOM_LEFT" if lado > 0 else "BOTTOM_RIGHT"))

    def destaque(self, p_modelo, nome, desloc_papel=(8, 6), r_papel=3.0, p_fim=None):
        """Planta-chave (regra do Nathan, 22/10/2026): marca a peça com CÍRCULO em volta e LINHA DE CHAMADA com o nome,
        para ficar claro onde ela está. Pilar: p_modelo = centro. Viga: p_modelo e p_fim = pontas (círculo no meio + traço
        grosso ao longo da viga)."""
        if p_fim is not None:
            self._add(self.pr.msp.add_lwpolyline([self.P(p_modelo), self.P(p_fim)], dxfattribs={"layer": "INDICACAO", "const_width": 0.7}))
            c = ((p_modelo[0] + p_fim[0]) / 2, (p_modelo[1] + p_fim[1]) / 2)
        else:
            c = p_modelo
        self._add(self.pr.msp.add_circle(self.P(c), r_papel, dxfattribs={"layer": "INDICACAO"}))
        dx, dy = desloc_papel
        d = math.hypot(dx, dy) or 1.0
        p0 = (c[0] + dx / d * r_papel * self.esc, c[1] + dy / d * r_papel * self.esc)     # chamada sai da borda do círculo
        return self.chamada(p0, (dx - dx / d * r_papel, dy - dy / d * r_papel), nome, "sub")

    def barra(self, pts, pos, n, diam, espac=None, comp_cm=None, ponto_rotulo=None, desloc=(10, 8), camada="ARMADURA"):
        """Armadura em vista longitudinal + rótulo NBR 7191: 'N1 - 8 Ø16 c/15 C=250'. camada: ARMADURA (longitudinal) ou ARM_TRANSV."""
        self.poli(pts, camada)
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
            self._add(self.pr.texto(lx, ly, letra, "sub", "TITULO", "MIDDLE_CENTER"))
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
        self.pr.texto(cx, y - 5.0, f"ESC. 1:{self.esc:g} — COTAS EM {self.unidade.upper()}" + (f" — {self.subtitulo}" if self.subtitulo else ""), "nota", "TEXTO", "BOTTOM_CENTER")
        self._bbox_titulo = (cx - w1 / 2, y - 7, cx + w1 / 2, y + 5)
