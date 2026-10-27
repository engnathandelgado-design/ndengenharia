"""Ligações da cobertura metálica — geometria única (rev11, 26/10/2026) para o modelo 3D (modelo_bim.py) e para os
isométricos explodidos de montagem (ND-LET-COB09). Cada função devolve as peças de UMA ligação em coordenadas locais (mm):

  {"item": n, "marca": "...", "desc": "...", "g": "caixa", "b": (x0, x1, y0, y1, z0, z1)}
  {"item": n, "marca": "...", "desc": "...", "g": "cil", "c": (x, y, z), "eixo": "x|y|z", "r": r, "h": h}   (h com sinal)
  {"item": n, "marca": "...", "desc": "...", "g": "hex", "c": ..., "eixo": ..., "r": r, "h": h}              (porca / cabeça)
  {"item": n, "marca": "...", "desc": "...", "g": "prisma_xz", "pol": [(x, z)...], "y": (y0, y1)}           (convexo)

"ctx": True marca peças de contexto (concreto, perfis principais) que o 3D já tem como peça própria.
"exp": deslocamento de explosão (mm) para o isométrico explodido.

Eixos: x ao longo da viga (TS-01 / W da linha 2, sentido da água), y ao longo da terça (entre linhas), z para cima.
Fontes: cob_linha2.json (W, montantes, emendas, apoios — DEC-052), cobertura_metalica.json (terça, ST-1P, transpasse)."""
import json
import math
from pathlib import Path

AQ = Path(__file__).resolve().parent
CB2 = json.loads((AQ / "cob_linha2.json").read_text(encoding="utf-8"))
CBM = json.loads((AQ / "cobertura_metalica.json").read_text(encoding="utf-8"))
PC = CBM["pecas"]

# perfis (mm) — mesmas dimensões do catálogo usado no cálculo (nd_estruturas.metalica_laminada)
try:
    import sys
    sys.path.insert(0, str(AQ.parents[1]))
    from nd_estruturas import metalica_laminada as _ML
    _W, _M = _ML.perfil(CB2["perfil"]), _ML.perfil(CB2["montante"])
    W = dict(d=_W.d, bf=_W.bf, tf=_W.tf, tw=_W.tw)
    MT = dict(d=_M.d, bf=_M.bf, tf=_M.tf, tw=_M.tw)
except Exception:                                          # pragma: no cover
    W = dict(d=200, bf=100, tf=5.2, tw=4.3)
    MT = dict(d=148, bf=100, tf=4.9, tw=4.3)

# terça Z 302×90/82×2,30 METSEC (mesmos números de cob_comum.py)
H_T, B_SUP, B_INF, D_SUP, D_INF, T_Z = 302, 90, 82, 19, 21, 2.30
Z_TERCA = 10                                   # fundo da terça 10 mm acima do concreto / da mesa (porca de nivelamento)
A_TR, B_TR = PC["transpasse_cada_lado_mm"], PC["furos_transpasse_da_ponta_mm"]
Z_FURO = tuple(PC["furos_z_mm"])               # furos na alma (do fundo da terça)
Y_COL = 60                                     # colunas de furos do apoio a ±60 do eixo
ST = dict(t=9.5, larg=220, h=290, aba=150)     # ST-1P
ST_W = dict(t=6.3, larg=220, h=290, aba=150)   # ST-W: chapa dobrada 6,3 (cob_linha2.json: "igual ao ST-1P")
L102, T102 = 102, 12.7                         # L 102 × 102 × 12,7 (CB-M1 / CB-M2)
Y_M = 30                                       # eixo do montante 30 mm para o lado da borda
GAB = 55                                       # gabarito das mesas (furos a ±27,5)
Y_MF = A_TR - B_TR                             # mão-francesa presa no parafuso da ponta do transpasse (sem furo novo na terça)

# torques de aperto (k = 0,20, rosca galvanizada; 70 % da carga de prova da classe 8.8) — ver notas da COB09
TORQUE = {"M12": 85, "M16": 210}


def _p(item, marca, desc, g, exp=(0, 0, 0), ctx=False, **kw):
    d = dict(item=item, marca=marca, desc=desc, g=g, exp=exp, ctx=ctx)
    d.update(kw)
    return d


def _parafuso(item, marca, desc, c, eixo, d, L, exp=(0, 0, 0), porca_em=None, exp_porca=None, cabeca=True, item_porca=None):
    """parafuso (cabeça em c, fuste de comprimento L com sinal ao longo do eixo) + arruela e porca em porca_em."""
    out = []
    ax = "xyz".index(eixo)
    sg = 1 if L > 0 else -1

    def em(t):
        q = list(c)
        q[ax] += t
        return tuple(q)
    if cabeca:
        out.append(_p(item, marca, "", "hex", exp, c=em(-sg * 0.65 * d), eixo=eixo, r=0.95 * d, h=sg * 0.65 * d))
    out.append(_p(item, marca, desc, "cil", exp, c=c, eixo=eixo, r=d / 2, h=L))
    if porca_em is not None:
        ep = exp_porca if exp_porca is not None else exp
        ip = item_porca if item_porca is not None else item
        out.append(_p(ip, marca, "", "cil", ep, c=em(porca_em), eixo=eixo, r=d, h=sg * 0.15 * d))
        out.append(_p(ip, marca, "", "hex", ep, c=em(porca_em + sg * 0.15 * d), eixo=eixo, r=0.95 * d, h=sg * 0.8 * d))
    return out


def _w(item, marca, desc, x0, x1, z0, perfil=W, y0=0.0, ctx=True, exp=(0, 0, 0)):
    """perfil I ao longo de x (mesas e alma como caixas), fundo em z0, centrado em y0."""
    d, bf, tf, tw = perfil["d"], perfil["bf"], perfil["tf"], perfil["tw"]
    return [_p(item, marca, desc, "caixa", exp, ctx, b=(x0, x1, y0 - bf / 2, y0 + bf / 2, z0, z0 + tf)),
            _p(item, marca, "", "caixa", exp, ctx, b=(x0, x1, y0 - tw / 2, y0 + tw / 2, z0 + tf, z0 + d - tf)),
            _p(item, marca, "", "caixa", exp, ctx, b=(x0, x1, y0 - bf / 2, y0 + bf / 2, z0 + d - tf, z0 + d))]


def _z(item, marca, desc, xa, y0, y1, z0, exp=(0, 0, 0), ctx=True):
    """terça Z ao longo de y: alma em x ∈ [xa, xa + T_Z], aba inferior de 82 para +x, aba superior de 90 para −x."""
    c45 = math.cos(math.radians(45))
    t = T_Z
    pols = [[(xa, z0), (xa + t, z0), (xa + t, z0 + H_T), (xa, z0 + H_T)],                                     # alma
            [(xa, z0), (xa + B_INF, z0), (xa + B_INF, z0 + t), (xa, z0 + t)],                                 # aba inferior
            [(xa - B_SUP + t, z0 + H_T - t), (xa + t, z0 + H_T - t), (xa + t, z0 + H_T), (xa - B_SUP + t, z0 + H_T)],   # aba superior
            [(xa + B_INF - t, z0), (xa + B_INF, z0), (xa + B_INF - D_INF * c45, z0 + D_INF * c45), (xa + B_INF - D_INF * c45 - t, z0 + D_INF * c45)],
            [(xa - B_SUP + t, z0 + H_T - t), (xa - B_SUP + 2 * t, z0 + H_T), (xa - B_SUP + t + D_SUP * c45 + t, z0 + H_T - D_SUP * c45),
             (xa - B_SUP + t + D_SUP * c45, z0 + H_T - D_SUP * c45 - t)]]
    return [_p(item, marca, desc if k == 0 else "", "prisma_xz", exp, ctx, pol=pol, y=(y0, y1)) for k, pol in enumerate(pols)]


def _cant(item, marca, desc, x0, sx, y0, y1, z0, sz, exp=(0, 0, 0)):
    """cantoneira L 102 × 102 × 12,7 ao longo de y: canto em (x0, z0), aba horizontal para sx, aba vertical para sz."""
    xa, xb = sorted((x0, x0 + sx * L102))
    za, zb = sorted((z0, z0 + sz * T102))
    xc, xd = sorted((x0, x0 + sx * T102))
    zc, zd = sorted((z0 + sz * T102, z0 + sz * L102))
    return [_p(item, marca, desc, "caixa", exp, b=(xa, xb, y0, y1, za, zb)),
            _p(item, marca, "", "caixa", exp, b=(xc, xd, y0, y1, zc, zd))]


# ====================================================================== 1. terças na TS-01 (ST-1P + transpasse)
def apoio_terca_ts01(L_vis=900):
    """origem: eixo do apoio (linha), face da alma da terça interna (x = 0), topo do concreto (z = 0)."""
    t, larg, h, aba = ST["t"], ST["larg"], ST["h"], ST["aba"]
    xe = -t - 75 + 9.5                                     # esperas ES-1 no meio da aba horizontal
    zb = [Z_TERCA + z for z in Z_FURO]
    P = []
    P.append(_p(0, "V408–V419", "I90 das linhas 3 a 8 (topo, referência)", "caixa", (0, 0, 0), True, b=(-230, 120, -150, 150, -120, 0), concreto=True))
    for yy in (-Y_COL, Y_COL):
        P.append(_p(1, "ES-1", "espera M16 (hef 150 + gancho + grampo U Ø10), na viga", "cil", (0, 0, 0), c=(xe, yy, -150), eixo="z", r=8, h=150 + 120))
        P.append(_p(7, "M16", "porca + contraporca + arruela na ES-1", "hex", (0, 0, 320), c=(xe, yy, t), eixo="z", r=15, h=13))
        P.append(_p(7, "M16", "", "hex", (0, 0, 320), c=(xe, yy, t + 13), eixo="z", r=15, h=13))
    ex = (0, 0, 170)
    P.append(_p(2, "ST-1P", "chapa dobrada 9,5 × 220 A36 galv. (aba 290 + aba 150, 2 oblongos 18 × 40, 4 Ø14)", "caixa", ex, b=(-t, 0, -larg / 2, larg / 2, 0, h)))
    P.append(_p(2, "ST-1P", "", "caixa", ex, b=(-aba, -t, -larg / 2, larg / 2, 0, t)))
    # terças: interna (vão da esquerda, y de −L_vis/2 até +A_TR) e externa (vão da direita, −A_TR até +L_vis/2)
    P += _z(3, "T", "terça Z 302 do vão anterior (ponta a +450)", 0.0, -L_vis / 2, A_TR, Z_TERCA, exp=(110, 0, 0), ctx=False)
    P += _z(4, "T", "terça Z 302 do vão seguinte (ponta a −450), encaixada", T_Z, -A_TR, L_vis / 2, Z_TERCA, exp=(260, 0, 0), ctx=False)
    for yy in (-Y_COL, Y_COL):
        for z in zb:
            P += _parafuso(5, "M12 8.8", "apoio: ST-1P + 2 almas", (-t, yy, z), "x", 12, t + 2 * T_Z + 18, exp=(-170, 0, 0),
                           porca_em=t + 2 * T_Z + 1, exp_porca=(420, 0, 0), item_porca=5)
    for yy in (-(A_TR - B_TR), A_TR - B_TR):
        for z in zb:
            P += _parafuso(6, "M12 8.8", "emenda: ponta do transpasse, 2 almas", (0, yy, z), "x", 12, 2 * T_Z + 18, exp=(-170, 0, 0),
                          porca_em=2 * T_Z + 1, exp_porca=(420, 0, 0), item_porca=6)
    return P


# ====================================================================== 2. W 200 na cabeça do pilar (CA-L2 + 4 BR-M16)
def apoio_w_pilar(Lw=800):
    """origem: eixo do apoio sobre o pilar, topo do concreto (z = 0)."""
    P = [_p(0, "PILAR", "cabeça do pilar", "caixa", (0, 0, 0), True, b=(-200, 200, -150, 150, -420, 0), concreto=True)]
    P.append(_p(1, "GRAUTE", "graute de nivelamento 20 (±10)", "caixa", (0, 0, 0), b=(-140, 140, -140, 140, 0, 20)))
    for xx in (-75, 75):
        for yy in (-GAB / 2, GAB / 2):
            P.append(_p(2, "BR-M16", "barra roscada M16 8.8 L 450 (hef 350 + grampo U Ø10), embutida no pilar", "cil", (0, 0, 0),
                        c=(xx, yy, -350), eixo="z", r=8, h=350 + 39 + W["tf"] + 45))
    P.append(_p(3, "CA-L2", "chapa de apoio 250 × 250 × 19, 4 furos Ø18 (no C) / oblongos 18 × 40 em x (demais)", "caixa", (0, 0, 120),
                b=(-125, 125, -125, 125, 20, 39)))
    P += _w(4, "W-L2", f"{CB2['perfil'].replace('x', '×')} da linha 2 (furos na mesa inferior, gabarito 55)", -Lw / 2, Lw / 2, 39, ctx=False, exp=(0, 0, 300))
    for xx in (-75, 75):
        for yy in (-GAB / 2, GAB / 2):
            z0 = 39 + W["tf"]
            P.append(_p(5, "M16", "arruela + porca + contraporca (por dentro da W)", "cil", (0, 0, 480), c=(xx, yy, z0), eixo="z", r=16, h=2.4))
            P.append(_p(5, "M16", "", "hex", (0, 0, 480), c=(xx, yy, z0 + 2.4), eixo="z", r=15, h=13))  # noqa
            P.append(_p(5, "M16", "", "hex", (0, 0, 480), c=(xx, yy, z0 + 15.4), eixo="z", r=15, h=13))
    return P


# ====================================================================== 3. montante W 150 sobre a VM (EM-L2 + CB-M1 + CB-M2)
def montante(L_mt):
    """origem: eixo do montante na linha 2 (y = 0 no eixo da linha), topo da capa (z = 0). L_mt em mm."""
    d, bf, tf, tw = MT["d"], MT["bf"], MT["tf"], MT["tw"]
    zf = 25 + L_mt + 5                                   # fundo da W
    P = [_p(0, "VM", "VM 30 × 75 do +7,30 + capa (2º estágio)", "caixa", (0, 0, 0), True, b=(-300, 300, -150, 150, -260, 0), concreto=True)]
    P.append(_p(1, "GRAUTE", "graute 20", "caixa", (0, 0, 0), b=(-200, 200, -40, 100, 0, 20)))
    for xx in (-(d / 2 + 84), d / 2 + 84):
        for yy in (0, 60):
            P.append(_p(2, "EM-L2", "barra roscada M16 8.8 L 330 com gancho laçado na alça N9 (espera do 2º estágio)", "cil", (0, 0, 0),
                        c=(xx, yy, -270), eixo="z", r=8, h=270 + 20 + T102 + 45))
            P.append(_p(9, "M16", "arruela + porca + contraporca", "hex", (0, 0, 520), c=(xx, yy, 20 + T102), eixo="z", r=15, h=13))
            P.append(_p(9, "M16", "", "hex", (0, 0, 520), c=(xx, yy, 20 + T102 + 13), eixo="z", r=15, h=13))
    # montante: mesas ⊥ a x (planos y-z) em x = ±d/2, alma no plano x-z (y = Y_M)
    z0m, z1m = 25, 25 + L_mt
    exm = (0, 0, 0)
    for sg in (-1, 1):
        xa, xb = sorted((sg * d / 2, sg * (d / 2 - tf)))
        P.append(_p(3, "MT-L2", f"montante {CB2['montante'].replace('x', '×')}", "caixa", exm, b=(xa, xb, Y_M - bf / 2, Y_M + bf / 2, z0m, z1m)))
    P.append(_p(3, "MT-L2", "", "caixa", exm, b=(-d / 2 + tf, d / 2 - tf, Y_M - tw / 2, Y_M + tw / 2, z0m, z1m)))
    # CB-M1 (base, 100 em y) e CB-M2 (topo, 130 em y)
    for sg in (-1, 1):
        P += _cant(4, "CB-M1", "L 102 × 102 × 12,7 × 100 (base), 2 + 2 furos Ø18", sg * d / 2, sg, -20, 80, 20, 1, exp=(sg * 160, 0, 0))
        P += _cant(5, "CB-M2", "L 102 × 102 × 12,7 × 130 (topo), 2 + 2 furos Ø18", sg * d / 2, sg, -50, 80, zf, -1, exp=(sg * 160, 0, 0))
        for yy in (Y_M - 25, Y_M + 25):
            P += _parafuso(6, "M16 8.8", "cantoneira × mesa do montante", (sg * (d / 2 + T102), yy, 80), "x", 16, -sg * (T102 + tf + 20),
                          exp=(sg * 320, 0, 0), porca_em=-sg * (T102 + tf + 1), exp_porca=(sg * 60, 0, 0))
            P += _parafuso(6, "M16 8.8", "", (sg * (d / 2 + T102), yy, zf - 55), "x", 16, -sg * (T102 + tf + 20),
                           exp=(sg * 320, 0, 0), porca_em=-sg * (T102 + tf + 1), exp_porca=(sg * 60, 0, 0))
        for yy in (-GAB / 2, GAB / 2):
            P += _parafuso(7, "M16 8.8", "CB-M2 × mesa inferior da W (gabarito 55)", (sg * (d / 2 + 55), yy, zf + W["tf"] + 0.0), "z", 16,
                           -(W["tf"] + T102 + 20), exp=(0, 0, 420), porca_em=-(W["tf"] + T102 + 1), exp_porca=(sg * 160, 0, -120))
    P += _w(8, "W-L2", f"{CB2['perfil'].replace('x', '×')}", -350, 350, zf, ctx=True, exp=(0, 0, 300))
    return P


# ====================================================================== 4. emenda da W (TL-1 + TL-2)
def emenda_w(Lw=500):
    """origem: junta (x = 0), eixo da W (y = 0), fundo da W (z = 0)."""
    d, bf, tf, tw = W["d"], W["bf"], W["tf"], W["tw"]
    P = _w(1, "W-L2", "módulo da W (esquerda)", -Lw, -1, 0, ctx=True, exp=(-120, 0, 0)) + _w(1, "W-L2", "módulo da W (direita)", 1, Lw, 0, ctx=True, exp=(120, 0, 0))
    P.append(_p(2, "TL-1", "tala de mesa 9,5 × 100 × 300, 8 furos Ø18", "caixa", (0, 0, 160), b=(-150, 150, -50, 50, d, d + 9.5)))
    P.append(_p(2, "TL-1", "tala de mesa 9,5 × 100 × 300, 8 furos Ø18", "caixa", (0, 0, -160), b=(-150, 150, -50, 50, -9.5, 0)))
    for sy in (-1, 1):
        ya, yb = sorted((sy * tw / 2, sy * (tw / 2 + 6.3)))
        P.append(_p(3, "TL-2", "tala de alma 6,3 × 130 × 200, 4 furos Ø18", "caixa", (0, sy * 150, 0), b=(-100, 100, ya, yb, (d - 130) / 2, (d + 130) / 2)))
    for xx in (-110, -50, 50, 110):
        for yy in (-GAB / 2, GAB / 2):
            P += _parafuso(4, "M16 8.8", "talas de mesa (16 por emenda)", (xx, yy, d + 9.5), "z", 16, -(9.5 + tf + 22), exp=(0, 0, 300),
                           porca_em=-(9.5 + tf + 1), exp_porca=(0, 0, 160))
            P += _parafuso(4, "M16 8.8", "talas de mesa (16 por emenda)", (xx, yy, -9.5), "z", 16, 9.5 + tf + 22, exp=(0, 0, -300),
                           porca_em=9.5 + tf + 1, exp_porca=(0, 0, -160))
    for xx in (-50, 50):
        for zz in (d / 2 - 35, d / 2 + 35):
            P += _parafuso(5, "M16 8.8", "talas de alma (4 por emenda)", (xx, -(tw / 2 + 6.3), zz), "y", 16, tw + 2 * 6.3 + 22, exp=(0, -300, 0),
                           porca_em=tw + 2 * 6.3 + 1, exp_porca=(0, 300, 0))
    return P


# ====================================================================== 5. terça na W da linha 2 (ST-W + MF-1)
def terca_w(L_vis=1000):
    """origem: eixo da linha 2 (y = 0), face da alma da terça interna (x = 0), topo da W (z = 0)."""
    d, bf, tf = W["d"], W["bf"], W["tf"]
    t, larg, h, aba = ST_W["t"], ST_W["larg"], ST_W["h"], ST_W["aba"]
    zb = [Z_TERCA + z for z in Z_FURO]
    P = []
    # W ao longo de x, sob a terça (alma da terça em x = 0; o ST-W vai para −x)
    P += _w(0, "W-L2", f"{CB2['perfil'].replace('x', '×')} da linha 2", -420, 220, -d, ctx=True)
    ex = (0, 0, 170)
    P.append(_p(1, "ST-W", "chapa dobrada 6,3 × 220 A36 galv. (aba 290 + aba 150), 2 Ø14 na aba + 4 Ø14 na alma", "caixa", ex, b=(-t, 0, -larg / 2, larg / 2, 0, h)))
    P.append(_p(1, "ST-W", "", "caixa", ex, b=(-aba, -t, -larg / 2, larg / 2, 0, t)))
    for yy in (-GAB / 2, GAB / 2):
        P += _parafuso(2, "M12 8.8", "ST-W × mesa superior da W (gabarito 55)", (-75, yy, t), "z", 12, -(t + tf + 16), exp=(0, 0, 420),
                       porca_em=-(t + tf + 1), exp_porca=(0, 0, -150))
    P += _z(3, "T", "terça do vão 1-2 (ponta a +450)", 0.0, -L_vis / 2, A_TR, Z_TERCA, exp=(110, 0, 0), ctx=False)
    P += _z(4, "T", "terça do vão 2-3 (ponta a −450)", T_Z, -A_TR, L_vis / 2, Z_TERCA, exp=(260, 0, 0), ctx=False)
    for yy in (-Y_COL, Y_COL):
        for z in zb:
            P += _parafuso(5, "M12 8.8", "ST-W + 2 almas", (-t, yy, z), "x", 12, t + 2 * T_Z + 18, exp=(-170, 0, 0),
                           porca_em=t + 2 * T_Z + 1, exp_porca=(420, 0, 0))
    # mão-francesa MF-1: do parafuso da ponta do transpasse (y = ±Y_MF, furo de baixo) à borda da mesa inferior da W
    for sy in (-1, 1):
        ya, za = sy * Y_MF, zb[0]
        yb, zb_ = sy * GAB / 2, -d + tf                    # ponta dobrada sobre a mesa inferior, no gabarito 55
        n = 12
        L = math.hypot(ya - yb, za - zb_)
        # cantoneira L 51 × 51 × 4,8 como barra de seção 51 × 4,8 (aba encostada na alma) — prisma ao longo da reta
        P.append(_p(6, "MF-1", f"mão-francesa L 51 × 51 × 4,8 L {L:.0f}, 1 M12 em cada ponta", "barra", (380, 0, 0),
                    a=(2 * T_Z + 4.8 / 2, ya, za), b=(2 * T_Z + 4.8 / 2, yb, zb_), s=(4.8, 51)))
        P += _parafuso(7, "M12 8.8", "MF-1 × ponta do transpasse (o mesmo furo da emenda, parafuso 10 mm mais longo)", (0, ya, za), "x", 12,
                       2 * T_Z + 4.8 + 18, exp=(-170, 0, 0), porca_em=2 * T_Z + 4.8 + 1, exp_porca=(560, 0, 0))
        P += _parafuso(8, "M12 8.8", "MF-1 × mesa inferior da W (ponta dobrada, furo Ø14 na mesa)", (2 * T_Z + 2.4, yb, zb_ + 4.8), "z", 12,
                       -(4.8 + tf + 16), exp=(380, 0, 120), porca_em=-(4.8 + tf + 1), exp_porca=(380, 0, -120))
    return P


def L_MF():
    """comprimento da mão-francesa MF-1 (m), entre furos — para o cálculo (calc_cobertura_linha2.py) e as listas."""
    zb0 = Z_TERCA + Z_FURO[0]
    return math.hypot((Y_MF - GAB / 2) / 1000, (zb0 + W["d"] - W["tf"]) / 1000)


# ====================================================================== 6. terça na VB (ST-1V) — rev12 (revisão rev12, rev11 #27)
def apoio_terca_vb(L_vis=700):
    """origem: alma da terça (x = 0), eixo da VB (y = 0; −y = para fora, fachada), topo do concreto da VB (z = 0).
    Mesma geometria do modelo 3D (modelo_bim.suporte_st): chapa com a borda rente à ponta da terça (ext. de fachada)."""
    t, larg, h, aba = ST["t"], ST["larg"], ST["h"], ST["aba"]
    ext = PC["extensao_fachada_mm"]
    yc = 110 - ext                                          # centro da chapa (borda rente à ponta da terça, em y = −ext)
    P = [_p(0, "VB", "viga de borda 15 × 60 (topo, referência)", "caixa", (0, 0, 0), True, b=(-260, 140, -75, 75, -160, 0), concreto=True)]
    for xe in (-45, -105):
        P.append(_p(1, "ES-1V", "espera M16 (hef 150 + gancho + grampo U Ø10), na VB", "cil", (0, 0, 0), c=(xe, 0, -150), eixo="z", r=8, h=150 + 120))
        P.append(_p(7, "M16", "porca + contraporca + arruela na ES-1V", "hex", (0, 0, 320), c=(xe, 0, t), eixo="z", r=15, h=13))
        P.append(_p(7, "M16", "", "hex", (0, 0, 320), c=(xe, 0, t + 13), eixo="z", r=15, h=13))
    ex = (0, 0, 170)
    P.append(_p(2, "ST-1V", "chapa dobrada 9,5 × 220 A36 galv. (aba 290 + aba 150), borda rente à ponta da terça", "caixa", ex, b=(-t, 0, yc - larg / 2, yc + larg / 2, 0, h)))
    P.append(_p(2, "ST-1V", "", "caixa", ex, b=(-aba, -t, yc - larg / 2, yc + larg / 2, 0, t)))
    P += _z(3, "T", f"terça Z 302 de ponta (passa {ext} do eixo da VB)", 0.0, -ext, L_vis, Z_TERCA, exp=(160, 0, 0), ctx=False)
    for yy in (yc - Y_COL, yc + Y_COL):
        for z in (Z_TERCA + zz for zz in Z_FURO):
            P += _parafuso(5, "M12 8.8", "apoio: ST-1V + alma da terça", (-t, yy, z), "x", 12, t + T_Z + 18, exp=(-170, 0, 0),
                           porca_em=t + T_Z + 1, exp_porca=(380, 0, 0), item_porca=5)
    return P


# ====================================================================== 7. última terça no pilar de canto (ST-1FL + ES-1FL) — rev12
def apoio_terca_canto():
    """origem: alma da terça (x = 0), face lateral interna do pilar de canto (plano y = 0; pilar em y > 0), fundo da chapa (z = 0).
    Mesma geometria do modelo 3D (modelo_bim.suporte_fl): aba 190 na face, aba 100 na alma, 2 ES-1FL M20 horizontais."""
    t = 9.5
    xA = 6.5                                                # face A do pilar de canto
    P = [_p(0, "PILAR", "pilar de canto (face lateral interna, referência)", "caixa", (0, 0, 0), True, b=(xA, xA + 400, 0, 260, -180, 470), concreto=True)]
    P.append(_p(2, "ST-1FL", "chapa dobrada 9,5 × 290 A36 galv.: aba 190 na face do pilar (2 furos Ø22) + aba 100 na alma (2 Ø14)", "caixa", (0, -120, 0),
                b=(-t, xA + 175, -t, 0, 0, 290)))
    P.append(_p(2, "ST-1FL", "", "caixa", (0, -120, 0), b=(-t, 0, -100, -t, 0, 290)))
    for xe in (xA + 70, xA + 150):
        P.append(_p(1, "ES-1FL", "barra roscada M20 A36 L=400 horizontal (hef 150 + grampo U Ø10), embutida na face", "cil", (0, 0, 0), c=(xe, 320, 145), eixo="y", r=10, h=-400))
        P.append(_p(8, "M20", "arruela + porca + contraporca na ES-1FL", "hex", (0, -260, 0), c=(xe, -t, 145), eixo="y", r=19, h=-16))
        P.append(_p(8, "M20", "", "hex", (0, -260, 0), c=(xe, -t - 16, 145), eixo="y", r=19, h=-16))
    P += _z(3, "T", "última terça do lado E (termina 10 mm antes da face do pilar)", 0.0, -900, -10, Z_TERCA - 10, exp=(-200, -120, 0), ctx=False)
    for z in (Z_TERCA - 10 + zz for zz in Z_FURO):
        P += _parafuso(5, "M12 8.8", "aba 100 do ST-1FL + alma da terça", (-t, -60, z), "x", 12, t + T_Z + 18, exp=(-170, -120, 0),
                       porca_em=t + T_Z + 1, exp_porca=(380, -120, 0), item_porca=5)
    return P


ITENS = {
    "ISO 1": ("TERÇAS NA VIGA DE COBERTURA: ST-1P E TRANSPASSE", apoio_terca_ts01),
    "ISO 2": ("W DA LINHA 2 NA CABEÇA DO PILAR", apoio_w_pilar),
    "ISO 3": ("MONTANTE W 150 SOBRE A VM DO +7,30", lambda: montante(CB2["montantes"][1]["L_m"] * 1000)),
    "ISO 4": ("EMENDA DA W DA LINHA 2", emenda_w),
    "ISO 5": ("TERÇA NA W DA LINHA 2: ST-W E MF-1", terca_w),
    "ISO 6": ("TERÇA NA VIGA DE BORDA: ST-1V", apoio_terca_vb),
    "ISO 7": ("ÚLTIMA TERÇA NO PILAR DE CANTO: ST-1FL E ES-1FL", apoio_terca_canto),
}
