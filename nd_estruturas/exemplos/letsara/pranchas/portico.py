"""Geometria do pórtico transversal da Letsara (eixos 2 e 3), gerada dos mesmos dados do modelo 3D (ligacoes.json, cob_linha2.json,
vm_retangular.json, consolos.json). rev11 (26/10/2026): extraída da ND-LET-CT01 para ser usada também no corte 1-1 da ND-LET-MON01;
terças Z 302 × 90/82 × 19 × 2,30 em seção real (linha média + enrijecedores, igual à COB01), ST-1P com aba e 4 M12, consolo CT-I130
com mísula e NEO-3C 150 × 300 na linha 3 (DEC-061)."""
import json, math
from prancha_nd import Prancha, _seg_rect

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
LG = json.load(open(AQ + "ligacoes.json"))
f = lambda v, d=3: f"{v:+.{d}f}".replace(".", ",")
I = 0.03
c, sn = 1 / math.sqrt(1 + I * I), I / math.sqrt(1 + I * I)
L_TS = LG["L_TS"] * 1000
XC = 19750.0
X0 = [LG["X_PONTA_ESQ"] * 1000, 2 * XC - LG["X_PONTA_CEN"] * 1000]       # pontas das duas TS-01 (rev03, sem dentes)
zf = lambda x: LG["Z0_TS"] * 1000 + I * x  # fundo da TS-01 (mm, x global em mm)
H = 900.0
t3 = 27.0 / 900.0
Z_TOP_PIL = 10000.0
Z_TOP_C = LG["Z_TOPO_I130"] * 1000                                     # topo da I130 e dos pilares centrais
H_I130 = LG["H_I130"] * 1000
Z_ASS_I130 = LG["Z_ASS_I130"] * 1000
import sys as _s; _s.path.insert(0, '/home/claude/ndengenharia/nd_estruturas/exemplos/letsara')
from geometria import Z_PISOS, P6_L2
from lajes_placas import vigas_nivel
Z_MEZ = [z * 1000 for z in Z_PISOS]                    # rev09: topo da capa +3,90 / +7,30
CB2 = json.load(open('/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/cob_linha2.json'))
ZL2 = {a["nome"]: a["z_concreto"] * 1000 for a in CB2["apoios_diretos"]}          # rev09b (DEC-050): topo do concreto na linha 2
TER = [s * 1000 for s in LG["s_tercas"]]
PAC = LG["platibanda"]["pacote"]
TB = (140.0, L_TS - 77.5)


class Recorte:
    """Desenha numa vista só o que cai dentro de uma janela do modelo (para os detalhes ampliados)."""

    def __init__(self, v, jan=None):
        self.v, self.j = v, jan

    def _dentro(self, p):
        return self.j is None or (self.j[0] <= p[0] <= self.j[2] and self.j[1] <= p[1] <= self.j[3])

    def _clip(self, a, b):
        if self.j is None:
            return a, b
        x0, y0, x1, y1 = self.j
        dx, dy = b[0] - a[0], b[1] - a[1]
        t0, t1 = 0.0, 1.0
        for p, q in ((-dx, a[0] - x0), (dx, x1 - a[0]), (-dy, a[1] - y0), (dy, y1 - a[1])):
            if abs(p) < 1e-12:
                if q < 0:
                    return None
            else:
                t = q / p
                if p < 0:
                    t0 = max(t0, t)
                else:
                    t1 = min(t1, t)
                if t0 > t1:
                    return None
        return (a[0] + t0 * dx, a[1] + t0 * dy), (a[0] + t1 * dx, a[1] + t1 * dy)

    def linha(self, a, b, cam="VISTA"):
        s = self._clip(a, b)
        if s:
            self.v.linha(s[0], s[1], cam)

    def poli(self, pts, cam="VISTA", fechada=False):
        pp = list(pts) + ([pts[0]] if fechada else [])
        for a, b in zip(pp[:-1], pp[1:]):
            self.linha(a, b, cam)

    def ret(self, x, y, w, h, cam="CORTADO"):
        self.poli([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], cam, True)

    def hach(self, pts):
        if all(self._dentro(p) for p in pts):
            self.v.hachura(pts, "AR-CONC", 0.03)


def glob(x0, s, h):
    xb = x0 + s * c
    return (xb - h * sn, zf(xb) + h * c)


def ts(R, x0):
    sk = lambda h: h * t3
    L = L_TS
    cont = [(0, 0), (L, 0), (L + 27, H), (27, H)]
    R.poli([glob(x0, s, h) for s, h in cont], "CORTADO", True)
    for h in (150, 230, 700, 780):
        R.linha(glob(x0, 1200 + sk(h), h), glob(x0, L - 1200 + sk(h), h), "VISTA")
    for s0 in TB:
        R.linha(glob(x0, s0, 0), glob(x0, s0 + 27, H), "EIXO")
    for s in TER:
        xt, zt = glob(x0, s, H)
        terca_z(R, xt, zt)
    zz = H + 10 + 302
    for k_ in ("tp40", "espacador_la", "zipada", "painel_solar"):
        zz += PAC[k_] * 1000
        a, b = glob(x0, -100, zz), glob(x0, L + 100, zz)
        R.linha(a, b, "METALICA")
    a, b = glob(x0, -100, H + 310), glob(x0, L + 100, H + 310)
    R.linha(a, b, "METALICA")


import cob_comum as _CC
C45 = math.cos(math.radians(45))


def terca_z(R, xt, zt):
    """Terça Z 302 × 90/82 × 19 × 2,30 METSEC em seção real (contorno da chapa de 2,30 com os enrijecedores a 45°, mesma
    orientação da COB01: aba superior de 90 para −x sobre o ST-1P, inferior de 82 para +x) + ST-1P (aba vertical 290 × 9,5 junto
    à alma, aba horizontal 150 sobre o topo da viga) e 4 M12 na alma. zt = topo do concreto da viga no ponto."""
    h_, bs, bi, ds, di, t = _CC.H_TERCA, _CC.B_TERCA, _CC.B_INF, _CC.D_SUP, _CC.D_INF, _CC.T_Z
    z0 = zt + 10
    lm = [(xt + (bi - di * C45), z0 + di * C45), (xt + bi, z0), (xt, z0), (xt, z0 + h_), (xt - bs, z0 + h_), (xt - (bs - ds * C45), z0 + h_ - ds * C45)]
    R.poli(lm, "METALICA")                                                       # linha média
    R.poli([(x_ + (t if i in (2, 3) else 0), z_ + (t if i in (1, 2) else -t if i in (3, 4) else 0)) for i, (x_, z_) in enumerate(lm)], "METALICA")   # 2ª face (espessura)
    R.ret(xt - 9.5, zt, 9.5, 290, "METALICA")                                    # ST-1P — aba vertical (alma da terça encostada)
    R.ret(xt - 150, zt, 150 - 9.5, 9.5, "METALICA")                              # ST-1P — aba horizontal sobre a viga
    for zb in (z0 + 62, z0 + 257):                                               # 2 M12 em cada furo da alma (4 por apoio, nas 2 terças do transpasse)
        R.linha((xt - 40, zb), (xt + 25, zb), "METALICA")


def ct_i130(R):
    """rev11 (DEC-061): consolos CT-I130 com mísula nas duas faces da mesa superior da I130 (linhas 3, 5–8), topo no topo da viga;
    NEO-3C 150 × 300 × 10 sob a ponta de cada TS-01, de 12 a 27 cm da ponta (consolos.json / ligacoes.json)."""
    CT = json.load(open(AQ + "consolos.json"))["CT-I130"]
    bm = 200.0                                                                   # meia largura da mesa superior (b 40)
    pj, ht, hc = CT["proj_m"] * 1000, CT["h_total_m"] * 1000, CT["h_consolo_m"] * 1000
    for sg in (-1, 1):
        x1, x2 = XC + sg * bm, XC + sg * (bm + pj)
        pts = [(x1, Z_TOP_C), (x2, Z_TOP_C), (x2, Z_TOP_C - hc), (x1, Z_TOP_C - ht)]
        R.poli(pts, "CORTADO", True); R.hach(pts)
    xt = LG["X_PONTA_CEN"] * 1000                                                # ponta da TS-01 do lado A (a 37,5 mm do eixo C)
    for sg, tip in ((-1, xt), (1, 2 * XC - xt)):
        a_, b_ = tip + sg * 120, tip + sg * 270
        R.ret(min(a_, b_), Z_TOP_C, abs(b_ - a_), 10, "METALICA")                 # NEO-3C


def apoio(R, x, z, larg):
    """Neoprene (10 mm) sob a ponta da TS-01, centrado em x."""
    R.ret(x - larg / 2, z - 10, larg, 10, "METALICA")


def consolo(R, face, lado, z_seat, proj=300, alt=440, inc=I):
    """Consolo sem chanfro (h = dente da viga − neoprene; fundo alinhado ao da viga), topo com inclinação inc passando
    por z_seat no centro do apoio."""
    xa, xb = face, face + lado * proj
    xm = face + lado * (proj - 125)
    zt = lambda x: z_seat + inc * (x - xm)
    pts = [(xa, zt(xa)), (xb, zt(xb)), (xb, zt(xb) - alt), (xa, zt(xa) - alt)]
    R.poli(pts, "CORTADO", True)
    R.hach(pts)


def pilar(R, x, larg, z_top, nome=None):
    pts = [(x - larg / 2, 0), (x + larg / 2, 0), (x + larg / 2, z_top), (x - larg / 2, z_top)]
    R.poli(pts, "CORTADO", True)


REC = tuple(r * 1000 for r in LG["REC"])  # assento da TS-01 no recuo da cabeça dos pilares laterais (rev03)


def pilar_rec(R, x, lado, z_rec):
    """Pilar lateral 40×60 com a cabeça recuada (só os 300 externos sobem acima de z_rec). lado = sentido para dentro."""
    pts = [(x - lado * 300, 0), (x + lado * 300, 0), (x + lado * 300, z_rec), (x, z_rec), (x, Z_TOP_PIL), (x - lado * 300, Z_TOP_PIL)]
    R.poli(pts, "CORTADO", True)


def estrutura(R, eixo):
    if eixo == 2:
        pilar_rec(R, 0, 1, ZL2["A"]); pilar_rec(R, 39500, -1, ZL2["E"])
    else:
        pilar_rec(R, 0, 1, REC[0]); pilar_rec(R, 39500, -1, REC[1])
    if eixo != 2:
        apoio(R, X0[0] + 140, zf(X0[0] + 140) , 200); apoio(R, 39500 - X0[0] - 140, zf(39500 - X0[0] - 140), 200)
    for xp in (-325 - 50, 39500 + 325 + 50):                          # placas de fechamento 10 cm por fora (folga 25)
        R.ret(xp - 50, 0, 100, Z_TOP_PIL, "VISTA")
    if eixo == 2:
        pilar(R, XC, 400, ZL2["C"])
        for xm, ap in ((9870, "B"), (29630, "D")):
            pilar(R, xm, 400, ZL2[ap])
        R.ret(P6_L2[0] * 1000 - 125, 0, 250, ZL2["P6"], "CORTADO")             # P6 da linha 2 (25 em x), cabeça até a W 310
        _P = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/vm_retangular.json"))["premissas"]
        HV, RC, LN = round(_P["h_pm"] * 1000), round(_P["dente"]["recorte"] * 1000), round(_P["dente"]["ln"] * 1000)
        for iz, zm in enumerate(Z_MEZ):
            topo = zm - 260                                  # laje h20 + capa 5 + fita 1; topo da VM = apoio da laje
            vs = [(xa * 1000, xb * 1000) for _, xa, xb, y in vigas_nivel(iz) if y > 9]
            for xa, xb in vs:
                cont = [(xa + LN, topo - HV), (xb - LN, topo - HV), (xb - LN, topo - HV + RC), (xb, topo - HV + RC), (xb, topo), (xa, topo),
                        (xa, topo - HV + RC), (xa + LN, topo - HV + RC)]                          # VM retangular 30 × 75 com dente (rev09)
                R.poli(cont, "VISTA", True)
                consolo(R, xa - 30, 1, topo - HV + RC - 21, proj=400, alt=RC - 21, inc=0); consolo(R, xb + 30, -1, topo - HV + RC - 21, proj=400, alt=RC - 21, inc=0)
            x_fim = max(xb for _, xb in vs)
            R.ret(300, zm - 250, x_fim - 300, 200, "VISTA")
            R.ret(300, zm - 50, x_fim - 300, 50, "VISTA")
        ap = CB2["apoios_diretos"]                         # linha 2 (DEC-050): W 310 contínua direto na cabeça dos pilares
        zb0 = ap[0]["z_fundo_w"] * 1000
        zbw = lambda x: zb0 + I * (x - ap[0]["x"] * 1000)
        xw0, xw1 = ap[0]["x"] * 1000 - 100, ap[-1]["x"] * 1000 + 100
        DW = 200 if "200" in CB2["perfil"] else 313                 # DEC-052: W 200 × 15,0
        R.poli([(xw0, zbw(xw0)), (xw1, zbw(xw1)), (xw1, zbw(xw1) + DW), (xw0, zbw(xw0) + DW)], "METALICA", True)
        for mt_ in CB2.get("montantes", []):                      # DEC-052: montantes W 150 no meio dos vãos, sobre as VM do +7,30
            R.ret(mt_["x"] * 1000 - 74, mt_["z_base"] * 1000, 148, mt_["L_m"] * 1000, "METALICA")
        for a_ in ap:
            x_ = a_["x"] * 1000
            R.ret(x_ - 125, a_["z_concreto"] * 1000 + 20, 250, 19, "METALICA")
    else:
        _H = H_I130                                                 # DEC-054: h 120
        sec = [(-200, 0), (200, 0), (200, 250), (75, 330), (75, _H - 300), (200, _H - 220), (200, _H), (-200, _H), (-200, _H - 220),
               (-75, _H - 300), (-75, 330), (-200, 250)]
        base = Z_TOP_C - H_I130
        R.poli([(XC + x, base + y) for x, y in sec], "CORTADO", True)
        R.hach([(XC + x, base + y) for x, y in sec])
    if eixo != 2:
        ct_i130(R)                                                                 # rev11: consolo CT-I130 + NEO-3C (DEC-061)
        for x0 in X0:
            ts(R, x0)


