"""ND-LET-CT03 — CORTE LONGITUDINAL DA OBRA (eixo C) + PLANTA-CHAVE DOS CORTES + 3D (rev executiva, 21/10/2026).

CORTE 6-6 (1:100): plano no eixo C (x = 19,75 m), olhando para o eixo E — pilares do eixo C cortados (PF-02, PC-01, PC-02,
PC-03, PF-04), vigas centrais I120 V407/V406/V405 cortadas no eixo (dentes nos consolos CP-I120), pontas das TS-01 do lado E
sobre a I120 (linhas 3 a 8; na linha 2 a W 310 metálica, DEC-048), mezanino (VM ao fundo, lajes LA-01R e capa cortadas), VB das fachadas, placas I e A cortadas, paredes G e C,
pacote da cobertura e níveis. PLANTA-CHAVE (1:400) com todos os cortes do jogo executivo e a folha de cada um.
Geometria dos mesmos JSON do cálculo (ligacoes, consolos, vm_retangular, cob_linha2, laje_alveolar) e do quantitativo (comprimentos). A0."""
import json, math, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from prancha_nd import Prancha, DIM_K, DIM_DLI
from geometria import Y_LIN, X_EIXO, PILARES_ESPECIAIS, Y_P13, Y_PC_C, Z_PISOS, lado_placas_txt
import renomear as RN
import pecas_obra as QT                                     # peças = mesma fonte das listas (quantitativos.py)
import fechamento as FCH
import pilar_generico as _G

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
LG = json.load(open(AQ + "ligacoes.json"))
CO = json.load(open(AQ + "consolos.json"))
VMP = json.load(open(AQ + "vm_retangular.json"))["premissas"]
CB2 = json.load(open(AQ + "cob_linha2.json"))
PQ = {p_[1]: p_ for p_ in QT.pecas}
f = lambda v, d=3: f"{v:+.{d}f}".replace(".", ",")
fd = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
M = lambda v: v * 1000
I3 = 0.03
YL = [M(y) for y in Y_LIN]
COMP = YL[-1]
XC = M(X_EIXO["C"])
ZT_I = M(LG["Z_TOPO_I120"]); ZT_ID = M(LG["Z_TOPO_I120_DIR"])
H_I, HD_I = M(LG["H_I120"]), M(LG["HD_I120"])
Z_ASS = M(LG["Z_ASS_I120"])
CPI = CO["CP-I120"]
HC, PC_ = M(CPI["h_total_m"]), M(CPI["proj_m"])
LN_I = 350.0                                              # nariz do dente da I120 (78 × 35)
FOLGA_I = 75.0
NIV = [z * 1000 for z in Z_PISOS]
ASS_M = [float(z) for z in _G.Z_MEZ_ASS]
HV = VMP["h_pm"] * 1000; BT = VMP["b"] * 1000; HCMZ = VMP["dente"]["consolo_h"] * 1000
ZTV = [n - 260 for n in NIV]
PAC = LG["platibanda"]["pacote"]
zf = lambda x: M(LG["Z0_TS"]) + I3 * x                   # fundo da TS-01 (x em mm)
X_TS_E = XC + 37.5                                         # ponta da TS-01 do lado E sobre a I120
Z_TS_E = ZT_ID + 10                                        # fundo da ponta (NEO-3 de 10 mm)
Z_VB = zf(XC + 225) + 300                                  # fundo da VB-03 junto ao PF (zf + 0,30)
PLAT = 10000.0
O_PL = 375.0
# rev12b (item 4): paredes internas do lado das placas do registro (geometria.PAREDE_INTERNA), como no modelo: centro da placa a
# 2,5 cm (folga) + 5 cm (meia placa) da face dos pilares desse lado
from geometria import PAREDE_INTERNA as _PI, Y_FACE_L4 as _YF4
Y_PG_ = M(Y_LIN[_PI["G"]["linha"]]) + _PI["G"]["lado"] * O_PL
Y_PC_ = M(_YF4) + _PI["C"]["lado"] * 75.0

# pilares do eixo C: (marca, y, by, z_topo, rec)
_ZC = M(next(a_ for a_ in CB2["apoios_diretos"] if a_["nome"] == "C")["z_concreto"])     # rev09b (DEC-050): P8A até o fundo da W 310
PIL = [("PF-02", YL[0], 600, PLAT), ("PC-01", YL[1], 600, _ZC), ("PC-02", YL[3], 400, ZT_I), ("PC-03", M(Y_PC_C[0]), 400, ZT_I), ("PC-03", M(Y_PC_C[1]), 400, ZT_I), ("PF-04", YL[8], 600, PLAT)]   # DEC-058
# I120 entre faces + folga 7,5 (comprimentos = quantitativos)
I120 = []
_YP = {"P13": M(Y_PC_C[0]), "P13B": M(Y_PC_C[1])}
for mk, (ia, ya_f), (ib, yb_f) in (("V407", (1, 300), (3, 200)), ("V406", (3, 200), ("P13", 200)), ("V405", ("P13", 200), ("P13B", 200)), ("V404", ("P13B", 200), (8, 300))):
    ya = (YL[ia] if isinstance(ia, int) else _YP[ia]) + ya_f + FOLGA_I
    yb = (YL[ib] if isinstance(ib, int) else _YP[ib]) - yb_f - FOLGA_I
    I120.append((mk, ya, yb))

pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="CORTE LONGITUDINAL DA OBRA (EIXO C), PLANTA-CHAVE DOS CORTES E VISTAS 3D DA ESTRUTURA",
                        desenho="ND-LET-CT03", folha="01/01", fase="EXECUTIVO", rev="00"))
pr.revisao("00", "21/10/2026", "EMISSÃO: CORTE 6-6 LONGITUDINAL, PLANTA-CHAVE DOS CORTES E 3D")
pr.revisao("01", "23/10/2026", "DEC-045/047/048/049: PISOS +3,90/+7,30; VM 30 × 75; LINHA 2 METÁLICA (DEC-048)")
pr.revisao("02", "24/10/2026", "DEC-052/054: LINHA 2 COM W 200 × 15,0; I120 COM h 120 E CONSOLO COM MÍSULA")
pr.revisao("03", "24/10/2026", "DEC-058: 2 PC-03 40×40 NO EIXO C, I120 EM 3 VÃOS DE 16,517 m (V406, V405, V404)")
Q = pr.quadro


def conc(v, pts, cam="CORTADO", esc=0.02):
    v.poli(pts, cam, True)
    if cam == "CORTADO":
        v.hachura(pts, "AR-CONC", esc)


def nivel(v, x, z, txt, lado=1):
    k = v.esc
    v.linha((x, z), (x + lado * 12 * k, z), "COTA")
    v.poli([(x + lado * 4 * k - 1.0 * k, z + 1.7 * k), (x + lado * 4 * k + 1.0 * k, z + 1.7 * k), (x + lado * 4 * k, z)], "COTA", True)
    v.texto((x + lado * 6 * k, z + 0.5 * k), txt, "min", "BOTTOM_LEFT" if lado > 0 else "BOTTOM_RIGHT", "COTA")


def total(v, p1, p2, base, ang, loc):
    d = pr.msp.add_linear_dim(base=v.P(base), p1=v.P(p1), p2=v.P(p2), angle=ang, location=v.P(loc), dimstyle="ND",
                              override={"dimlfac": v.esc * v.fator, "dimdec": 1, "dimzin": 8, "dimtmove": 2}, dxfattribs={"layer": "COTA"})
    d.render(); v._add(d.dimension)


class Clip:
    """Vista recortada numa faixa de y (coordenada horizontal do corte): o corte 6-6 sai em 2 partes a 1:50."""
    def __init__(self, v, a, b):
        self.v, self.a, self.b = v, a, b
        self.esc, self.fator = v.esc, v.fator
        self.P, self._add = v.P, v._add
    def _dentro(self, p):
        return self.a - 1 <= p[0] <= self.b + 1
    def _seg(self, p, q):
        (x1, y1), (x2, y2) = p, q
        if max(x1, x2) < self.a or min(x1, x2) > self.b:
            return None
        if x1 != x2:
            t0, t1 = sorted(((self.a - x1) / (x2 - x1), (self.b - x1) / (x2 - x1)))
            t0, t1 = max(t0, 0.0), min(t1, 1.0)
            p = (x1 + t0 * (x2 - x1), y1 + t0 * (y2 - y1)); q = (x1 + t1 * (x2 - x1), y1 + t1 * (y2 - y1))
        return p, q
    def _poly(self, pts):
        out = list(pts)
        for lim, sg in ((self.a, 1), (self.b, -1)):
            if not out:
                break
            res = []
            for i in range(len(out)):
                P_, Q_ = out[i - 1], out[i]
                inP, inQ = sg * (P_[0] - lim) >= 0, sg * (Q_[0] - lim) >= 0
                if inQ:
                    if not inP:
                        t = (lim - P_[0]) / (Q_[0] - P_[0]); res.append((lim, P_[1] + t * (Q_[1] - P_[1])))
                    res.append(Q_)
                elif inP:
                    t = (lim - P_[0]) / (Q_[0] - P_[0]); res.append((lim, P_[1] + t * (Q_[1] - P_[1])))
            out = res
        return out
    def linha(self, p, q, cam="VISTA"):
        s_ = self._seg(p, q)
        if s_:
            self.v.linha(s_[0], s_[1], cam)
    def poli(self, pts, cam="VISTA", fechada=False):
        pp = list(pts) + ([pts[0]] if fechada else [])
        for p, q in zip(pp[:-1], pp[1:]):
            self.linha(p, q, cam)
    def hachura(self, pts, *a, **k):
        c_ = self._poly(pts)
        if len(c_) >= 3:
            self.v.hachura(c_, *a, **k)
    def texto(self, p, *a, **k):
        if self._dentro(p):
            self.v.texto(p, *a, **k)
    def circulo(self, c, r, cam="VISTA"):
        if self._dentro(c):
            self.v.circulo(c, r, cam)
    def chamada(self, p, *a, **k):
        if self._dentro(p):
            self.v.chamada(p, *a, **k)
    def cota_h(self, xs, y, d, total=True):
        xs_ = [x for x in xs if self.a - 1 <= x <= self.b + 1]
        if len(xs_) >= 2:
            self.v.cota_h(xs_, y, d, total=total)
    def cota_v(self, ys, x, d, total=True):
        if self.a - 3000 <= x <= self.b + 3000:
            self.v.cota_v(ys, x, d, total=total)


def corte(v):
    v.linha((-1500, 0), (COMP + 1500, 0), "TERRENO")
    for mk, y, by, zt in PIL:                                  # pilares cortados (cabeça recuada no lado interno dos PF)
        if mk.startswith("PF"):
            sg = 1 if y == 0 else -1                           # para dentro
            zr = 8700.0
            pts = [(y - sg * by / 2, -1000), (y + sg * by / 2, -1000), (y + sg * by / 2, zr), (y, zr), (y, zt), (y - sg * by / 2, zt)]
        else:
            pts = [(y - by / 2, -1000), (y + by / 2, -1000), (y + by / 2, zt), (y - by / 2, zt)]
        conc(v, pts, esc=0.012)
        import pe_pilar as PP                                               # rev11: cálice em corte + cota do embutimento
        PP.pe(v, X_EIXO["C"], y / 1000, y, "y", cotar=(y == YL[0]), lado=-1)
    for mk, ya, yb in I120:                                    # I120 cortada no eixo, dentes 78 × 35 nos consolos
        zb = ZT_I - H_I
        pts = [(ya, ZT_I - HD_I), (ya + LN_I, ZT_I - HD_I), (ya + LN_I, zb), (yb - LN_I, zb), (yb - LN_I, ZT_I - HD_I), (yb, ZT_I - HD_I), (yb, ZT_I), (ya, ZT_I)]
        conc(v, pts, esc=0.012)
        for yy, sg in ((ya - FOLGA_I, 1), (yb + FOLGA_I, -1)):  # consolo CP-I120 (no plano, cortado com o pilar)
            conc(v, [(yy, Z_ASS - HC), (yy + sg * PC_, Z_ASS - HC), (yy + sg * PC_, Z_ASS), (yy, Z_ASS)], esc=0.012)
        v.texto((ya + 0.3 * (yb - ya), ZT_I - H_I / 2), f"{mk} — I120, L {fd(PQ[mk][4], 2)} m", "min", "MIDDLE_CENTER")
    for i in range(2, 8):                                      # pontas das TS-01 do lado E (linhas 3 a 8), vistas
        y = YL[i]
        v.poli([(y - 200, Z_TS_E), (y + 200, Z_TS_E), (y + 200, Z_TS_E + 900), (y - 200, Z_TS_E + 900)], "VISTA", True)
    _mc = next(m_ for m_ in CB2["apoios_diretos"] if m_["nome"] == "C")    # linha 2 (DEC-050): W 310 contínua (cortada) direto na cabeça do P8A
    v.poli([(YL[1] - 125, M(_mc["z_concreto"]) + 20), (YL[1] + 125, M(_mc["z_concreto"]) + 20), (YL[1] + 125, M(_mc["z_concreto"]) + 39), (YL[1] - 125, M(_mc["z_concreto"]) + 39)], "METALICA", True)
    zw = M(_mc["z_fundo_w"])
    DW = 200 if "200" in CB2["perfil"] else 313                     # DEC-052: W 200 × 15,0 (bf 100)
    v.poli([(YL[1] - 50, zw), (YL[1] + 50, zw), (YL[1] + 50, zw + DW), (YL[1] - 50, zw + DW)], "CORTADO", True)
    z_ter = Z_TS_E + 900 + 10                                  # terças Z 302 e pacote (linhas em vista, do lado E)
    for dz, cam in ((0, "METALICA"), (302, "METALICA"), (302 + 1000 * (PAC["tp40"] + PAC["espacador_la"] + PAC["zipada"]), "METALICA"),
                    (302 + 1000 * sum(PAC.values()), "METALICA")):
        v.linha((300, z_ter + dz), (COMP - 300, z_ter + dz), cam)
    for y in (YL[0], YL[8]):                                   # VB-03 / VB-07 ao fundo (pontas junto ao PF)
        v.poli([(y - 75, Z_VB), (y + 75, Z_VB), (y + 75, Z_VB + 600), (y - 75, Z_VB + 600)], "VISTA", True)
    for zt, za in zip(ZTV, ASS_M):                             # mezanino entre as linhas 1 e 2
        for yc in (YL[0], YL[1]):                              # VM 30 × 75 ao fundo (retangular, DEC-048)
            v.poli([(yc - BT / 2, zt - HV), (yc + BT / 2, zt - HV), (yc + BT / 2, zt), (yc - BT / 2, zt)], "VISTA", True)
            v.poli([(yc - BT / 2, za - HCMZ), (yc + BT / 2, za - HCMZ), (yc + BT / 2, za), (yc - BT / 2, za)], "OCULTA", True)   # CP-MEZ (face D)
        yl1, yl2 = YL[0] + BT / 2 - 100, YL[1] - BT / 2 + 100                                                # pontas da laje (apoio 10 cm no topo)
        v.poli([(yl1, zt + 10), (yl2, zt + 10), (yl2, zt + 210), (yl1, zt + 210)], "VISTA", True)
        conc(v, [(YL[0] - BT / 2, zt + 210), (YL[1] + BT / 2, zt + 210), (YL[1] + BT / 2, zt + 260), (YL[0] - BT / 2, zt + 260)], esc=0.012)
    for yp, V in ((YL[0] - O_PL, "I"), (YL[8] + O_PL, "A")):  # placas das fachadas cortadas
        for k in range(8):
            if V == "I" and k in FCH.ESQ:
                continue
            conc(v, [(yp - 50, k * 1250 + 5), (yp + 50, k * 1250 + 5), (yp + 50, (k + 1) * 1250), (yp - 50, (k + 1) * 1250)], esc=0.012)
    for yp, kmax in ((Y_PG_, 5), (Y_PC_, 4)):                  # paredes G (linha 2) e C (linha 4) em vista (lado E), do lado das placas do registro
        for k in range(kmax + 1):
            v.poli([(yp - 50, k * 1250 + 5), (yp + 50, k * 1250 + 5), (yp + 50, (k + 1) * 1250), (yp - 50, (k + 1) * 1250)], "VISTA", True)
    for k, y in enumerate(YL):
        v.linha((y, -1700), (y, PLAT + 700), "EIXO")
        v.circulo((y, -2250), 450, "BOLHA"); v.texto((y, -2250), str(k + 1), "sub", "MIDDLE_CENTER")
    v.cota_h(YL, -1300, -4, total=False)                                     # rev11: abaixo do cálice
    v.cota_v([0, ZT_I - H_I, Z_ASS, ZT_I, PLAT], COMP + 2400, 4, total=False)
    v.cota_v([0, NIV[0], NIV[1], PLAT], -2400, -4, total=False)
    for z, t in ((0, "±0,000"), (NIV[0], f"piso mezanino {f(NIV[0] / 1000)}"), (NIV[1], f"piso mezanino {f(NIV[1] / 1000)}"), (PLAT, f"platibanda {f(PLAT / 1000)}")):
        nivel(v, -700, z, t, -1)
    for z, t in ((ZT_I - H_I, f"fundo I120 {f((ZT_I - H_I) / 1000)}"), (Z_ASS, f"assento I120 {f(Z_ASS / 1000)}"), (ZT_I, f"topo I120 {f(ZT_I / 1000)} / {f(ZT_ID / 1000)}"),
                 (PLAT, f"platibanda {f(PLAT / 1000)}")):
        nivel(v, COMP + 700, z, t, 1)
    import pe_pilar as PP, renomear as RN_
    for mk, y, by, zt in PIL:                                                  # rev11: nome, seção e comprimento total
        v.texto((y + (by / 2 + 120 if y < COMP else -by / 2 - 120), 180), PP.rotulo(RN_.pilar_em(X_EIXO["C"], y / 1000)), "nota", "BOTTOM_LEFT" if y < COMP else "BOTTOM_RIGHT")
    nivel(v, COMP + 700, -1000, "fundo dos pilares −1,000; cálice −1,050 (graute 5 cm)", 1)
    v.chamada((YL[2], Z_TS_E + 450), (6, 10), "TS-01 (ponta do lado E) no topo da I120: NEO-3 + 2 PN-5")
    v.chamada((YL[1], zw + DW), (-6, 12), "linha 2: W 200 × 15,0 na cabeça do P8A (ND-LET-COB05)")
    v.chamada((YL[6] + 2500, z_ter + 302), (6, 8), "terças Z 302 + TP-40 + lã de rocha 40 + zipada #0,50 + painéis solares (ND-LET-COB01)")
    v.chamada((YL[0] + 75, Z_VB + 300), (8, 9), "VB-03 15×60 (fachada 1)")
    v.chamada((YL[8] - 75, Z_VB + 300), (-8, 9), "VB-07 15×60 (fachada 9)")
    v.chamada((YL[0] - O_PL, 1250 * 6 + 600), (-8, 8), "placas I")
    v.chamada((YL[8] + O_PL, 1250 * 6 + 600), (8, 8), "placas A")
    v.chamada((Y_PG_, 1250 * 4 + 600), (8 * _PI["G"]["lado"], -8), "parede G (vista)")
    v.chamada((Y_PC_, 1250 * 4 + 600), (8 * _PI["C"]["lado"], -8), "parede C — portões (vista)")
    v.chamada((5000, NIV[1]), (6, 8), "mezanino: LP20 + capa 5 (ND-LET-CT02)")
    v.chamada((YL[1] + 300 + PC_ / 2, Z_ASS - HC / 2), (8, -14), f"CP-I120 {M(CPI['b_m']) / 10:g} × {PC_ / 10:g} × {HC / 10:g}/{M(CPI['h_consolo_m']) / 10:g} + NEO-2")



E = 50
YS = YL[4]                                                 # divisão na linha 5
v1 = pr.vista("CORTE 6-6", (Q[0] + 70 + 1600 / E, Q[3] - 6 - 10700 / E), E, titulo="CORTE 6-6 — LONGITUDINAL NO EIXO C (x = 19,75 m) — LINHAS 1 A 5",
              subtitulo="olhando para o eixo E; pilares do eixo C e vigas I120 cortados; TS-01 do lado E no topo da I120; mezanino entre as linhas 1 e 2; continua abaixo", unidade="cm")
v2 = pr.vista("CORTE 6-6 (CONT.)", (Q[0] + 70 + 1600 / E - (YS - 1200) / E, Q[3] - 6 - 10700 / E - 290), E, titulo="CORTE 6-6 (CONTINUAÇÃO) — LINHAS 5 A 9",
              subtitulo="olhando para o eixo E; continuação do corte acima a partir da linha 5", unidade="cm")
corte(Clip(v1, -1600, YS + 1200))
corte(Clip(v2, YS - 1200, COMP + 1600))
for vv, (ya_, yb_), yy_ in ((v1, (0, YS), YS + 1200), (v2, (YS, COMP), YS - 1200)):   # interrupção e total de cada parte
    vv.interrupcao((yy_, -1300), (yy_, PLAT + 400))
    yt = -1300 - 4 * DIM_K * E - DIM_DLI * E
    total(vv, (ya_, -1300), (yb_, -1300), (ya_, yt), 0, (ya_ + 0.62 * (yb_ - ya_), yt))

# ================================================================== PLANTA-CHAVE DOS CORTES (1:400)
EK = 400
k_ = pr.vista("CHAVE", (Q[0] + 45, 82), EK, titulo="PLANTA-CHAVE DOS CORTES", subtitulo="posição de cada corte do jogo executivo e a folha onde está", unidade="cm")
XA = {k: M(v_) for k, v_ in X_EIXO.items()}
for k, y in enumerate(YL):
    k_.linha((y, -1500), (y, XA["E"] + 1500), "EIXO")
    k_.circulo((y, XA["E"] + 2600), 1000, "BOLHA"); k_.texto((y, XA["E"] + 2600), str(k + 1), "nota", "MIDDLE_CENTER")
for nm, x in XA.items():
    k_.linha((-1500, x), (COMP + 1500, x), "EIXO")
    k_.circulo((-2600, x), 1000, "BOLHA"); k_.texto((-2600, x), nm, "nota", "MIDDLE_CENTER")
k_.poli([(-425, -425), (COMP + 425, -425), (COMP + 425, XA["E"] + 425), (-425, XA["E"] + 425)], "VISTA", True)
for y in YL:
    for x in XA.values():
        k_.ret(y - 200, x - 300, 400, 600, "CORTADO")
CORTES = [("1", YL[2] - 1200, "y", "ND-LET-MON01", "pórtico de montagem, linha 3"), ("2", YL[1], "y", "ND-LET-CT01", "transversal, eixo 2"),
          ("3", YL[2], "y", "ND-LET-CT01", "transversal, eixo 3"), ("4", 4825, "y", "ND-LET-CT02", "mezanino, meio do vão das lajes"),
          ("5", 14810, "x", "ND-LET-CT02", "mezanino, entre os eixos B e C"), ("6", XC, "x", "ND-LET-CT03", "longitudinal, eixo C"),
          ("M", 12600, "x", "ND-LET-MON02", "montagem do mezanino")]
for nm, pos, dirc, fl, ds in CORTES:
    if dirc == "y":
        k_.marcador_corte((pos, -1100) if nm != "4" else (pos, -1100), (pos, XA["E"] + 1100), nm, lado=1)
    else:
        L1 = YL[1] + 1600 if nm in ("5", "M") else COMP + 1100
        k_.marcador_corte((-2600, pos), (L1, pos), nm, lado=-1)

pr.refs[:] = [r_ for r_ in pr.refs if r_[1] == "6-6"]                  # os outros cortes estão nas folhas indicadas (tabela)

# ------------------------------------------------------------------ 3D e coluna direita
def recorte_png(src):
    from PIL import Image, ImageOps
    im = Image.open(src).convert("RGB")
    bb = ImageOps.invert(im).getbbox()
    pad = 20
    bb = (max(bb[0] - pad, 0), max(bb[1] - pad, 0), min(bb[2] + pad, im.width), min(bb[3] + pad, im.height))
    dst = src.replace(".png", "_c.png"); im.crop(bb).save(dst)
    return dst

pr.imagem(Q[0] + 330, 48, Q[0] + 630, 238, recorte_png("/home/claude/letsara/pranchas/img_ct03/geral.png"),
          titulo="3D — ESTRUTURA COMPLETA", subtitulo="modelo da obra sem telhas e placas")
pr.imagem(Q[0] + 655, 48, Q[0] + 955, 238, recorte_png("/home/claude/letsara/pranchas/img_ct03/eixoC.png"),
          titulo="3D — RECORTE NO EIXO C", subtitulo="pilares centrais, I120 e TS-01 apoiadas no topo")
xt, ytop = Q[2] - 180, Q[3] - 6
lin = [[nm + "-" + nm, ds, fl] for nm, _, _, fl, ds in CORTES]
yy = pr.tabela(xt, ytop, "CORTES DA OBRA", ["CORTE", "POSIÇÃO", "FOLHA"], lin, [20, 105, 55], h_lin=5.2)
notas = ["Corte 6-6 gerado da mesma geometria do modelo e das pranchas das peças: pilares do eixo C cortados (PF-02 e PF-04 com a cabeça recuada no lado interno acima de +8,70), vigas centrais I120 cortadas no eixo, consolos CP-I120 no plano.",
         f"I120: V407 (PC-01 → PC-02), V406 (PC-02 → P13), V405 (P13 → P13B), V404 (P13B → PF-04) — DEC-058; folga de {FOLGA_I / 10:.1f} cm".replace(".", ",") + " entre o nariz do dente e a face do pilar; assento +6,966 com NEO-2 300 × 200 × 31 fretado e PN-2 Ø25 grauteado numa ponta só.",
         "TS-01 das linhas 3 a 8 apoiadas no topo da I120 (lado A +7,776, lado E +7,788) com NEO-3 e 2 PN-5 por viga; folga de 7,5 cm entre as pontas no eixo C (ND-LET-CT04, det. 2). Na linha 2 a cobertura é a W 200 × 15,0 metálica contínua apoiada na cabeça dos pilares (que sobe até o fundo da W) e em montantes no meio dos vãos (DEC-052, ND-LET-COB05).",
         f"Placas de fechamento por fora dos pilares nas fachadas I (linha 1) e A (linha 9); parede interna G (linha 2) {lado_placas_txt('G')} e C (linha 4, portões) {lado_placas_txt('C')}; cada placa nos seus 2 consoles, folgas de 0,5 cm na altura e 2 cm no comprimento.",
         "Cortes transversais: ND-LET-CT01 (eixos 2 e 3); mezanino: CT02; apoios como montados: CT04; montagem: MON01 a MON03.",
         "Cotas em cm, níveis em m. Não medir no desenho. EMISSÃO EXECUTIVA — LIBERADO PARA PRODUÇÃO, ARMAÇÃO, CONCRETAGEM E MONTAGEM."]
pr.notas(xt, yy - 4, notas, 178)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-CT03")
for a in avisos:
    print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
