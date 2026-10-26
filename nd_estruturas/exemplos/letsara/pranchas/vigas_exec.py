"""rev07 (21/10/2026) — folhas executivas das vigas com a FÔRMA EM CIMA e a ARMAÇÃO EMBAIXO na mesma folha (padrão usina).

Composição sem duplicar desenho: a fôrma é a mesma dos geradores de fôrma (ts01_forma, viga_i.prancha_viga, viga_vm, viga_vb)
e a armação é a mesma das folhas de armadura (armaduras_vigas.spec_* + bloco), desenhadas na MESMA prancha em fases e
deslocadas em y. Da fôrma saem a "ELEVAÇÃO DE ARMAÇÃO" e a relação do aço (substituídas pela faixa de armação, padrão usina:
barras explodidas, seções, tabelas de ferros por unidade e por N unidades, resumo +10%). Folha 1189 mm de largura (A0) e altura
ajustada ao desenho (fôrma + armação).

Uso: python vigas_exec.py [ts01 i130 vm vb]
"""
import math, sys, json, contextlib, io
sys.path.insert(0, "/home/claude/letsara/pranchas")
import prancha_nd as PN
from prancha_nd import Prancha, FORMATOS, MASSA_ACO, ALTURAS, _wtext
from ezdxf import bbox as _bbox
import armaduras_vigas as AV
from arm_nd import Arm, fd, f1

PR = "/home/claude/letsara/pranchas/"
REV7 = ("07", "21/10/2026", "FÔRMA E ARMAÇÃO NA MESMA FOLHA (PADRÃO USINA)")
DADOS = dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR", fase="PARA APROVAÇÃO")


# ------------------------------------------------------------------ fases (desenho em "frame" próprio e depois deslocado)
class Fase:
    def __init__(self, pr):
        self.pr = pr
        self.h0 = {e.dxf.handle for e in pr.msp}
        self.nv, self.nb, self.ni = len(pr.vistas), len(pr.blocos_livres), len(pr.imagens)

    def ents(self):
        if getattr(self, "hs", None) is not None:
            return [e for e in self.pr.msp if e.dxf.handle in self.hs]
        return [e for e in self.pr.msp if e.dxf.handle not in self.h0]

    def fechar(self):
        self.hs = {e.dxf.handle for e in self.ents()}
        self.v1, self.b1, self.i1 = len(self.pr.vistas), len(self.pr.blocos_livres), len(self.pr.imagens)

    def bbox(self, xmin=None, xmax=None):
        es = self.ents()
        ext = _bbox.extents(es, fast=True)
        b = [ext.extmin.x, ext.extmin.y, ext.extmax.x, ext.extmax.y]
        for v in self.pr.vistas[self.nv:getattr(self, "v1", None)]:                      # títulos das vistas (ainda não finalizados): ~16 mm abaixo
            vb = v.bbox_papel()
            if vb:
                b[1] = min(b[1], vb[1] - 16)
        return b

    def mover(self, dy):
        for e in self.ents():
            if e.dxftype() == "HATCH" and e.dxf.solid_fill == 0 and e.pattern:
                # ezdxf 1.x: HATCH.translate() reaplica pattern_scale às linhas do padrão (fica 33× mais denso → AR-CONC
                # vira milhões de traços e a exportação do PDF trava). Translada e refaz o padrão com a escala original.
                nome, esc, ang = e.dxf.pattern_name, e.dxf.pattern_scale, e.dxf.pattern_angle
                e.translate(0, dy, 0)
                e.set_pattern_fill(nome, color=256, scale=esc, angle=ang)
                continue
            e.translate(0, dy, 0)
        pr = self.pr
        b1, i1 = getattr(self, "b1", len(pr.blocos_livres)), getattr(self, "i1", len(pr.imagens))
        pr.blocos_livres[self.nb:b1] = [(a, b + dy, c, d + dy, t) for (a, b, c, d, t) in pr.blocos_livres[self.nb:b1]]
        pr.imagens[self.ni:i1] = [(a, b + dy, c, d + dy, k) for (a, b, c, d, k) in pr.imagens[self.ni:i1]]


def _sem_relacao(pr):
    """na fase da fôrma, a relação do aço da folha de fôrma sai (fica a da faixa de armação)."""
    def tab(x, y_topo, barras, perda=0.10, aco="CA-50", **k):
        tot = sum(b["qtd"] * b["comp"] / 100 * MASSA_ACO[float(b["diam"])] for b in barras) * (1 + perda)
        for b in barras:
            pr.posicoes_tabela.add(b["pos"])
        return dict(total_kg=tot, resumo={}, y_base=y_topo + 4)
    pr.tabela_croqui = tab
    pr.tabela_aco = tab
    pr.salvar = lambda *a, **k: []


def _restaura(pr):
    for k in ("tabela_croqui", "tabela_aco", "salvar"):
        pr.__dict__.pop(k, None)


def fase_forma(pr, runner):
    """roda o gerador da fôrma desenhando na prancha `pr` (formato do gerador) e tira a elevação de armação."""
    W0, H0, m0, f0 = pr.W, pr.H, pr.m, pr.fmt
    fase = Fase(pr)

    def fabrica(formato="A1", dados=None, **k):
        pr.W, pr.H = FORMATOS[formato]
        pr.m, pr.fmt = PN.margens(formato), formato
        for kk in ("marca", "qtd", "peso", "volume"):
            if dados and kk in dados:
                pr.dados[kk] = dados[kk]
        fase.frame = (formato, pr.quadro, pr.carimbo_bbox)
        return pr
    _sem_relacao(pr)
    orig = PN.Prancha
    PN.Prancha = fabrica
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            runner(fabrica)
    finally:
        PN.Prancha = orig
        _restaura(pr)
    fase.cb = pr.carimbo_bbox
    for v in list(pr.vistas[fase.nv:]):
        if v.titulo.upper().startswith("ELEVAÇÃO DE ARMAÇÃO"):
            for e in v.ents:
                try:
                    pr.msp.delete_entity(e)
                except Exception:
                    pass
            pr.vistas.remove(v)
    pr.W, pr.H, pr.m, pr.fmt = W0, H0, m0, f0
    fase.fechar()
    return fase


def run_script(nome):
    def r(fab):
        src = open(PR + nome, encoding="utf-8").read()
        g = {"__name__": "forma_exec", "__file__": PR + nome}
        exec(compile(src, PR + nome, "exec"), g)
    return r


def _longa_emendada(A, E, xs0, pos, tr, bar, esc, y):
    """desenha os trechos de uma barra emendada por traspasse: grupo A numa linha e grupo B (defasado) na de baixo;
    trechos alternados 1,2 mm para a sobreposição aparecer; cota do traspasse embaixo de cada emenda."""
    l0t = tr["l0t"]
    for ig, (grupo, qg) in enumerate(zip(tr["grupos"], tr["qtd"])):
        if not grupo or not qg:
            continue
        yl, ymin = y, y
        for i, (pn, x0, c) in enumerate(grupo):
            b = bar[pn]
            yy = yl - (1.2 if i % 2 else 0)
            xa = E((xs0 + x0 * 10, 0))[0]
            bb = A.forma(xa, yy, b, esc, rotulo=False)
            A.tx(xa + (1.5 if i % 2 else 0), max(bb[3], yy + 2.6) + 0.6 + (3.2 if i % 2 else 0), Arm.rotulo(b, n=qg), "min", "BOTTOM_LEFT")
            ymin = min(ymin, bb[1], yy)
            if i:                                            # emenda com o trecho anterior: cota do traspasse
                xe0 = xa
                xe1 = xa + l0t * 10 / esc
                yc_ = yl - 4.0
                A.ln((xe0, yc_), (xe1, yc_), "COTA")
                for xx in (xe0, xe1):
                    A.ln((xx, yc_ - 1.0), (xx, yc_ + 1.0), "COTA")
                A.tx((xe0 + xe1) / 2, yc_ - 0.8, f"traspasse {l0t:.0f}", 1.5, "TOP_CENTER")
                ymin = min(ymin, yc_ - 3.5)
        A.bolha(E((xs0, 0))[0] - 6, yl, pos, registrar=False)
        A.tx(E((xs0, 0))[0] - 10, yl, "A" if ig == 0 else "B", 1.6, "MIDDLE_RIGHT")
        y = ymin - 10
    return y - 2


# ------------------------------------------------------------------ faixa de armação (corpo de armaduras_vigas.folha, sem a folha)
XMAX_FAIXA = 1179 - 190          # a faixa de armação não passa da coluna do carimbo (x = 989)


def fase_armacao(pr, S, x0=None, esc=None):
    """desenha a armação no frame A0 (quadro 25..1179 × 10..831). Devolve a fase e os dados da coluna direita.
    rev08: x0/esc = origem e escala da ELEVAÇÃO DE FÔRMA (armação na mesma escala e no mesmo x da fôrma, padrão usina);
    se a elevação invade a coluna das tabelas, as tabelas de ferros descem para baixo dos cortes."""
    fase = Fase(pr)
    A = Arm(pr)
    Q = (25, 10, 1179, 831)
    rep = next(m for m in S["marcas"] if m["marca"] == S.get("rep", S["marcas"][0]["marca"]))
    bar = {b["pos"]: b for b in rep["barras"]}
    L, H = S["L"], S["H"]
    esc = esc or S["esc"]
    x0 = x0 if x0 is not None else Q[0] + 30
    ncol = len(S["marcas"])
    XT = Q[0] + 970 - 98 * max(ncol, 2)
    tab_baixo = x0 + max(p[0] for c in S["contorno"] for p in c) / esc + 8 > XT
    yt = Q[3] - 12
    A.titulo(x0, yt, f"ELEVAÇÃO DE ARMAÇÃO — {rep['marca']} (L = {fd(rep['L']/10)} cm)",
             f"esc. 1:{esc:g} · demais marcas: mesma armação, comprimentos e quantidades na tabela de cada marca · mesma escala da elevação de fôrma acima")
    y_top_el = yt - 20 - (180 / esc if any(p[1] > H for e in S["ents"] for p in e[0]) else 0)
    ye = y_top_el - H / esc
    E = lambda p: (x0 + p[0] / esc, ye + p[1] / esc)
    for c in S["contorno"]:
        A.pl([E(p) for p in c], "VISTA", True)
    for pts, lay in S["ents"]:
        A.pl([E(p) for p in pts], lay)
    ytopo = max(p[1] for e in S["ents"] for p in e[0]) / esc + ye
    for xc, nome in S["cortes"]:
        for y1, y2 in ((ye - 6, ye - 2), (ytopo + 2, ytopo + 6)):
            A.ln((E((xc, 0))[0], y1), (E((xc, 0))[0], y2), "INDICACAO")
        A.tx(E((xc, 0))[0] + 1, ytopo + 6.5, nome, "min", "BOTTOM_LEFT", lay="TITULO")
    for xd, nome in S.get("dets", []):
        c = E((xd, H / 2))
        r = H * 0.75 / esc
        A.msp.add_circle(c, r, dxfattribs={"layer": "INDICACAO", "linetype": "ACAD_ISO02W100"})
        A.bolha_lider((c[0] + r * 0.7, c[1] + r * 0.7), c[0] + r + 4, c[1] + r + 4, nome, r=3.2, registrar=False)
    yc = ye - 10
    zs = S["zonas"]
    xs = [E((zs[0][0], 0))[0]] + [E(((a[1] + b[0]) / 2, 0))[0] for a, b in zip(zs[:-1], zs[1:])] + [E((zs[-1][1], 0))[0]]
    A.ln((xs[0], yc), (xs[-1], yc), "COTA")
    for x in xs:
        A.ln((x - 1.2, yc - 1.2), (x + 1.2, yc + 1.2), "COTA"); A.ln((x, yc - 2), (x, yc + 2), "COTA")
    alt = 0
    for (xa, xb), (_, _, t) in zip(zip(xs[:-1], xs[1:]), zs):
        if xb - xa > _wtext(t, ALTURAS["min"]) + 2:
            A.tx((xa + xb) / 2, yc + 0.8, t, "min", "BOTTOM_CENTER")
        else:
            A.tx((xa + xb) / 2, yc - 2.8 - alt * 3.0, t, 1.5, "TOP_CENTER")
            alt = 1 - alt
    pr.posicoes_desenho.update({z[2].split()[1] for z in zs})
    y = yc - 14
    TR = rep.get("traspasse") or {}
    for pos, xs0 in S["longas"]:
        if pos in TR:                                       # barra emendada (usina 12 m): trechos na posição real, um grupo por linha
            y = _longa_emendada(A, E, xs0, pos, TR[pos], bar, esc, y)
            continue
        b = bar[pos]
        g = b["geo"]
        if g["k"] == "C" and g.get("dir", 1) > 0:
            y -= g["g"] * 10 / esc
        bb = A.forma(E((xs0, 0))[0], y, b, esc, rotulo=False)
        A.tx(E((xs0, 0))[0], max(bb[3], y + 2.6) + 0.6, Arm.rotulo(b), "min", "BOTTOM_LEFT")
        A.bolha(E((xs0, 0))[0] - 6, y, pos)
        y = min(bb[1], y) - 12
    xb, yb_top, hrow = Q[0] + 20, y - 4, 0
    for blk in S["blocos"]:
        allp = [p for c in blk["contorno"] for p in c] + [p for e in blk["ents"] for p in e[0]]
        w_est = (max(p[0] for p in allp) - min(p[0] for p in allp)) / blk["esc"] + 30 + max(
            bar[p]["geo"]["a"] * 10 / blk.get("esc_f", 20) + 4 for p in blk["formas"]) + 20
        lim = XMAX_FAIXA - 6 if tab_baixo else (XT - 6 if yb_top > Q[3] - 400 else XMAX_FAIXA - 6)
        if xb + w_est > lim and xb > Q[0] + 20:
            xb, yb_top, hrow = Q[0] + 20, yb_top - hrow - 10, 0
        w, h = AV.bloco(A, blk, bar, xb, yb_top)
        xb += w + 8
        hrow = max(hrow, h)
    fim_blocos = (xb, yb_top, hrow)
    y_tab0 = yb_top - hrow - 14 if tab_baixo else Q[3] - 8
    ncl = max(1, int((XMAX_FAIXA - Q[0] - 20) // 100))
    for k, m in enumerate(S["marcas"]):
        if tab_baixo:
            xt, yy = Q[0] + 20 + sum(200 if mm["qtd"] > 1 else 100 for mm in S["marcas"][:k]), y_tab0
        else:
            xt, yy = XT + 98 * k, Q[3] - 8
        cordm = [("CORD. CP-190 Ø12,7", m["cord"][1], m["cord"][1] * AV.KG_CORD)] if m.get("cord") else None
        # rev08: nomes das peças desta marca (V200, V203…) + comprimento e quantidade; quebra na largura da coluna
        import renomear as RN
        from prancha_nd import quebrar as _qb
        wcol = (196 if (tab_baixo and m["qtd"] > 1 and xt + 200 <= XMAX_FAIXA) else 94)
        cab_ = f"{RN.renomear(m['marca'])} — L = {fd(m['L']/10)} cm — {m['qtd']} {'UNIDADE' if m['qtd'] == 1 else 'UNIDADES IGUAIS'}"
        lin_ = _qb(cab_, wcol, ALTURAS["sub"])
        for kk, t_ in enumerate(lin_):
            A.tx(xt, yy - 4 - kk * 4.8, RN.novo(t_), "sub", lay="TITULO")
        y_ini = yy - 8 - (len(lin_) - 1) * 4.8
        yy = A.tabela_ferros(xt, y_ini, m["barras"], 1)
        yy, kg = A.resumo(xt, yy - 3, m["barras"], 1, fck=S["fck"], vol=m["V"], area=m["area"], cordoalhas=cordm)
        m["kg"] = kg
        if m["qtd"] > 1:
            cordn = [("CORD. CP-190 Ø12,7", m["cord"][1] * m["qtd"], m["cord"][1] * m["qtd"] * AV.KG_CORD)] if m.get("cord") else None
            if tab_baixo and xt + 200 <= XMAX_FAIXA:          # N unidades ao lado da de 1 unidade
                xt, yy = xt + 100, y_ini + 6
            yy = A.tabela_ferros(xt, yy - 6, m["barras"], m["qtd"])
            yy, _ = A.resumo(xt, yy - 3, m["barras"], m["qtd"], fck=S["fck"], vol=m["V"], area=m["area"], cordoalhas=cordn)
    fase.fim_blocos = fim_blocos
    fase.fechar()
    return fase


def coluna_direita(pr, S, x, y, extras=(), notas_extra=()):
    lin = [[m["marca"], m["qtd"], fd(round(m["L"] / 10, 1)), f1(m["V"] * m["qtd"]), f1(m["kg"] * m["qtd"], 1),
            f1(m["cord"][1] * m["qtd"] * AV.KG_CORD, 1) if m.get("cord") else "—"] for m in S["marcas"]]
    lin.append(["TOTAL", sum(m["qtd"] for m in S["marcas"]), "", f1(sum(m["V"] * m["qtd"] for m in S["marcas"])),
                f1(sum(m["kg"] * m["qtd"] for m in S["marcas"]), 1),
                f1(sum(m["cord"][1] * m["qtd"] * AV.KG_CORD for m in S["marcas"] if m.get("cord")), 1) if any(m.get("cord") for m in S["marcas"]) else "—"])
    y = pr.tabela(x, y, "RESUMO DA FOLHA (+10%)", ["MARCA", "QT", "L (cm)", "CONC. m³", "CA-50 kg", "CORD. kg"], lin, [24, 12, 30, 34, 34, 34], h_lin=5.0, destaque_ultima=True)
    for fn in extras:
        y = fn(x, y - 5)
    y = pr.legenda_armadura(x, y - 4, True)
    notas = list(notas_extra) + S["notas"] + [
        "Armação: dimensões em centímetro; níveis em metro. Cobrimento 3,0 cm (CAA II). Aço CA-50 (NBR 7480); C= comprimento de corte com dobras; RESUMO com +10% de perdas (cordoalhas sem perdas).",
        "Dobramento NBR 6118:2023 tab. 9.1; estribos com ganchos 135° e ponta de 10Ø (mín. 7 cm). Barras longitudinais sem emenda.",
        "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
    return pr.notas(x, y - 4, notas, 168, titulo="NOTAS DA ARMAÇÃO")


# ------------------------------------------------------------------ composição
def _elev_forma(pr, fase):
    for v in pr.vistas[fase.nv:]:
        t = v.titulo.upper()
        if t.startswith("ELEVAÇÃO") and "ARMAÇÃO" not in t:
            return v
    return None


def compor(desenho, conteudo, folha, runner, S, extras_col=(), notas_extra=(), pos_extra=None, qtd=None, folga_col=0.0):
    pr = Prancha("A0", dict(DADOS, conteudo=conteudo, desenho=desenho, folha=folha))
    FF = fase_forma(pr, runner)
    ve = _elev_forma(pr, FF)
    FA = fase_armacao(pr, S, x0=ve.o[0] if ve else None, esc=ve.esc if ve else None)
    bA = FA.bbox()
    bF = FF.bbox()
    fmtF, QF, cbF = FF.frame
    dyA = 14 - bA[1]
    FA.mover(dyA)
    topA = bA[3] + dyA
    # rev08: a fôrma começa logo acima da faixa de armação (pelo desenho, não pela moldura da folha da fôrma)
    dyF = topA + 20 - bF[1] + folga_col
    FF.mover(dyF)
    Ht = math.ceil(max(bF[3], QF[3]) + dyF + 10)
    pr.W, pr.H = 1189, Ht
    pr.m, pr.fmt = dict(esq=25, dir=10, sup=10, inf=10), f"1189×{Ht}"
    # divisória entre as faixas: rótulo da armação logo acima dela, rótulo da fôrma acima da linha
    yl = topA + 10
    pr.linha((25, yl), (1179 - 190, yl), "CARIMBO_FINO")
    pr.texto(30, yl + 2, "FÔRMA", "sub", "TITULO")
    pr.texto(30, yl - 5.5, "ARMAÇÃO E PROTENSÃO", "sub", "TITULO")
    if pos_extra:
        pos_extra(pr, FA, dyA)
    pr.revisao(*REV7)
    # coluna da armação: x = 989 (sob a coluna da fôrma), do ponto livre mais alto até o carimbo
    xcol = 1179 - 180
    ocup = [e for e in FF.ents() if _ext(e) and _ext(e)[2] > xcol - 25]
    ycol = min([_ext(e)[1] for e in ocup] + [Ht - 10]) - 9
    y_fim = coluna_direita(pr, S, xcol, ycol, extras_col, notas_extra)
    falta = pr.carimbo_bbox[3] + 4 + 22 - y_fim                         # rev11: as revisões da emissão entram depois (carimbo cresce)
    if falta > 0:
        print(f"  ~ coluna da armação desce até o carimbo ({falta:.0f} mm): refazendo com folga")
        return None, falta
    # cordoalhas: desenhadas nas seções (círculos vazados) e cotadas no texto do bloco — a posição conta como desenhada
    pr.posicoes_desenho.update(p for p in pr.posicoes_tabela if p[:1] == "C" and p[1:].isdigit())
    # barras emendadas (usina 12 m): a posição original não existe mais — valem os trechos (N3a, N3b…) das tabelas de ferros
    emend = {p for m in S["marcas"] for p in (m.get("traspasse") or {})}
    pr.posicoes_tabela -= emend
    pr.posicoes_desenho -= emend
    # as demais marcas têm a mesma armação da representativa (elevação desenhada): os trechos delas valem como chamados
    pr.posicoes_desenho |= {pn for m in S["marcas"] for t in (m.get("traspasse") or {}).values() for g in t["grupos"] for pn, _, _ in g}
    av = pr.salvar(PR + desenho)
    err = [a for a in av if a[0] == "ERRO"]
    sob = [a for a in av if "sobrep" in a[1] or "cruza" in a[1] or "encosta" in a[1]]
    print(f"{desenho}: {pr.fmt} — {len(err)} erros, {len(sob)} sobreposições/encostos, {len(av)} avisos (dyF = {dyF:.1f}, dyA = {dyA:.1f})")
    for a in av:
        print("   ", a)
    return pr, av


def compor_ok(*a, **k):
    """refaz a composição com a folga que a coluna da direita (notas da armação) pedir."""
    folga = 0.0
    for _ in range(4):
        r = compor(*a, folga_col=folga, **k)
        if r[0] is not None:
            return r
        folga += r[1] + 6
    raise RuntimeError("coluna da direita não coube")


def _ext(e):
    try:
        x = _bbox.extents([e], fast=True)
        return (x.extmin.x, x.extmin.y, x.extmax.x, x.extmax.y) if x.has_data else None
    except Exception:
        return None


# ------------------------------------------------------------------ famílias
def ts01():
    from ts01_dados import P, F_cord, LBPT, LBPT_BRUSCA, ATO, L_N9, L, N_ATIVAS, N_ISOL, Y_ATIVAS, TXT_C1, TXT_C2
    S = AV.spec_ts01()
    ISO = P["isol"]["L"]

    def cord_tab(x, y):
        tc = PR_ATUAL[0].tabela_cordoalhas(x, y, [dict(pos="C1", diam=12.7, qtd=N_ATIVAS, y=Y_ATIVAS, forca=F_cord, isol=0),
                                                  dict(pos="C2", diam=12.7, qtd=N_ISOL, y=P["y2"], forca=F_cord, isol=ISO)], P["L_pista"])
        return tc["y_base"]

    def chave_tab(x, y):                                            # rev08: planta-chave com círculo + chamada em cada TS-01
        import chave as CH, renomear as RN
        esc = 700
        alto = 79.35 * 1000 / esc
        CH.planta(PR_ATUAL[0], (x + 40, y - 8 - alto), esc, RN.nomes_de("TS-01") + RN.nomes_de("TS-01A") + RN.nomes_de("TS-01B"),
                  subtitulo="vigas de cobertura desta folha")
        return y - 8 - alto - 26
    notas = [f"PROTENSÃO: C{P['fck']}; liberar as cordoalhas só com fckj ≥ {P['fckj']} MPa (corpo de prova curado com a peça). CP-190 RB Ø12,7, σpi = {P['sig_pi']} MPa ({f1(F_cord, 1)} kN por cordoalha no macaco); liberação GRADUAL e simétrica (lbpt = {f1(LBPT * 100, 0)} cm; brusca daria {f1(LBPT_BRUSCA * 100, 0)} cm, não permitida).",
             f"C1: {TXT_C1}. C2: {TXT_C2} (bainha plástica estanque, vedada com fita nas extremidades). Protensão completa: descompressão na combinação frequente e sem fissuração na rara (NBR 6118:2023 Tab. 13.4, DEC-043).",
             f"N9 2 Ø10 no topo, {f1(L_N9 / 10, 0)} cm a partir de cada ponta: tração no topo no ato da protensão (NBR 6118:2023 17.2.4.3.2 c, As ≥ {f1(ATO['As_topo_cm2'], 1)} cm² com N2).",
             f"Pista de {P['L_pista']} m: até 3 peças por linha; alongamento a medir e tolerância na nota da tabela de cordoalhas."]
    return compor_ok("ND-LET-TS01-1", "TS-01 — VIGA I90 DE COBERTURA PROTENDIDA — FÔRMA, INSERTOS, ARMAÇÃO E PROTENSÃO", "01/02",
                  run_script("ts01_forma.py"), S, extras_col=(cord_tab, chave_tab), notas_extra=notas)


def i130():
    import viga_i as VI
    S = AV.spec_i("i110")
    return compor_ok("ND-LET-I120", "VIGAS CENTRAIS I120 V404 / V405 / V406 / V407 — FÔRMA, INSERTOS, ARMAÇÃO E PROTENSÃO", "01/01",
                  lambda fab: (setattr(VI, "Prancha", fab), VI.prancha_viga(VI.dados_i110())), S)


def i130_marcas():
    """rev12 (checklist 10): elevação de fôrma própria da V400 (V407 do R01, 19,50 m) e da V402 (V405, 2 vigas de cobertura no topo)."""
    import viga_i as VI
    for mk in ("V407", "V405"):
        VI.prancha_viga(VI.dados_i110(mk))


def vm():
    S = AV.spec_vm()
    import json as _js
    _cb = _js.loads(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/cob_linha2.json", encoding="utf-8").read())
    _vj = _js.loads(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/vm_retangular.json", encoding="utf-8").read())
    _u = {mk: max(round(c["ELU"]["M2d"] / c["ELU"]["MRd2"], 2) for c in _vj[mk]["casos"] if c["caso"] == "+7,30 linha 2") for mk in ("VM-01", "VM-02", "VM-03")}
    _p = _cb["carga_vm"]
    _f = lambda v, n=1: f"{v:.{n}f}".replace(".", ",")
    notas = [("DEC-052 — +7,30 DA LINHA 2: montante W 150 × 13,0 da cobertura metálica no MEIO do vão das VM-01 (A–B), VM-02 (B–C e C–D) e VM-03 (D–P6) "
              f"(P característico G/Q {_f(_p['VM-01']['Pg'])}/{_f(_p['VM-01']['Pq'])}, {_f(_p['VM-02']['Pg'])}/{_f(_p['VM-02']['Pq'])} e {_f(_p['VM-03']['Pg'])}/{_f(_p['VM-03']['Pq'])} kN; "
              f"sucção de cálculo até {_f(_p['VM-01']['Pup_d'], 0)} kN). A PEÇA NÃO MUDA (mesmas marcas, cordoalhas e dente; protensão completa mantida). A espera EM-L2 (4 barras roscadas M16 com gancho laçado nas alças N9) "
              "vai na faixa de 2º estágio, posta por quem faz a capa, com gabarito — ND-LET-COB05. Não cortar nem dobrar as N9 nesses trechos.")]
    return compor_ok("ND-LET-VM01", "VIGAS DO MEZANINO VM-01 A VM-04 — RETANGULAR PROTENDIDA 30 × 75 COM DENTE GERBER — FÔRMA, 2º ESTÁGIO, ARMAÇÃO E PROTENSÃO", "01/01",
                  run_script("viga_vm.py"), S, notas_extra=notas)


def vb():
    S = AV.spec_vb()
    return compor_ok("ND-LET-VB01", "VIGAS DE BORDA VB-01 A VB-08 (15×60 COM DENTE, C40) — FÔRMA, INSERTOS E ARMAÇÃO", "01/01",
                  run_script("viga_vb.py"), S)


PR_ATUAL = [None]
_orig_init = Prancha.__init__


def _init(self, *a, **k):
    _orig_init(self, *a, **k)
    PR_ATUAL[0] = self
Prancha.__init__ = _init

if __name__ == "__main__":
    alvo = sys.argv[1:] or ["ts01", "i130", "i130_marcas", "vm", "vb"]
    for a in alvo:
        globals()[a]()
