"""Letsara rev05 — modelo global INTEGRADO (OpenSeesPy): toda a estrutura num modelo só.

Elementos:
  - pilares engastados na base (barras 3D, P-Δ), cabeças com recuo, mezanino com laje como diafragma rígido (+3,15/+6,55)
    e vigas VM;
  - TS-01 como vigas 3D (rigidez vertical E lateral: leva a carga no plano da cobertura), apoiadas por pinos nos recuos
    dos pilares e no topo da I130 / P8A (furo oblongo em x) / P11; I130 e VB 15×60 como vigas 3D;
  - terças Z 302×90/82×2,30 METSEC contínuas nos 8 vãos (barra 3D; 2 perfis no transpasse ±0,45 m), ligadas a cada
    TS-01 / VB pelo ST-1P: translações e torção (eixo da terça) presas, flexões livres (furos e transpasse);
  - correntes Ø10 (só tração) a L/4, L/2 e 3L/4 entre todas as terças; tirantes rígidos L 51×51×3,2 no 1º espaço de cada
    ancoragem; diagonais de ancoragem Ø16 (só tração) da 2ª terça ao apoio da 1ª;
  - contraventamento em X (só tração) parametrizado (vãos e largura do painel em espaços de terça).
Cargas: peso próprio (barras com carga distribuída), pacote da cobertura e sobrecarga nas terças, mezanino, vento
NBR 6123 completo (paredes por zona + cobertura por zona nas terças, pressão interna por compartimento com as
aberturas reais, excentricidade 6.6) e desaprumo H/400 (NBR 9062:2017 5.2.3).
Uso: import e chamar `analisar(config)`; rodar como script grava modelo_integrado_r05.json com o X adotado.
"""
from __future__ import annotations
import json, math, os, sys, types
from pathlib import Path
import openseespy.opensees as ops

AQ = Path(__file__).resolve().parent
sys.path.insert(0, str(AQ)); sys.path.insert(0, str(AQ.parents[1]))
from nd_estruturas.prefabricados import Concreto
from nd_estruturas import vento_nbr6123 as VNT
from nd_estruturas.metalica_fria import PerfilZ, barra_redonda_tracao_Rd, compressao_laminado_Rd
from geometria import Y_LIN, X_EIXO, Y_P13, LINHA_PORTOES

LG = json.loads((AQ / "ligacoes.json").read_text(encoding="utf-8"))
CB = json.loads((AQ / "cobertura_metalica.json").read_text(encoding="utf-8"))
_r4 = (AQ / "modelo_global_r04.py").read_text(encoding="utf-8")
_pil = types.ModuleType("_pil"); _pil.__dict__["math"] = math
exec(_r4[_r4.index("ARM = {"):_r4.index("verif = {}")], _pil.__dict__)     # ARM, barras, MRd, tipo_pilar (verificação dos pilares)

C40, C50 = Concreto(40), Concreto(50)
Y = Y_LIN
LARG, COMP, XC = X_EIXO["E"], Y_LIN[-1], X_EIXO["C"]
XF = [X_EIXO[k] for k in "ABCDE"]
Z0, INCL = LG["Z0_TS"], 0.03
zf = lambda x: Z0 + INCL * x                 # fundo da TS-01
REC = tuple(LG["REC"]); Z_TOP_C = LG["Z_TOPO_I130"]; Z_I130 = LG["Z_ASS_I130"]
Z_MEZ = (3.15, 6.55)
A_VM, G_2E = 0.1925, 1.5
X_PORTOES = [9.87, 15.195, 24.305, 29.63]      # pilares P9, P10a, P10b, P12 da linha 4 (portões)
TRIB_X = [(XF[min(i + 1, 4)] - XF[max(i - 1, 0)]) / 2 for i in range(5)]
# terças: posições x (linha da alma) — mesmas do modelo r04 / pranchas
# rev06 (DEC-025): 15 espaços por meia água, 1ª terça a 40 cm livres da cabeça do P1 (calha)
X_ESQ = list(LG["x_tercas_esq"])
X_DIR = [round(x + (2 * XC - LG["X_PONTA_CEN"]) - LG["X_PONTA_ESQ"], 3) for x in X_ESQ]
IDX_NOS_X = LG["idx_nos_x"]
X_TER = X_ESQ + X_DIR                        # 34 linhas de terças
NT = len(X_ESQ)
S_TER = LG["passo_tercas"]
G_CALHA, Q_CALHA = 0.12, 0.45            # kN/m: calha de chapa + suportes; água com a calha cheia (300 × 150)
CC = LG["cargas_cob"]
PC = CB["pecas"]
A_TR = PC["transpasse_cada_lado_mm"] / 1000
# terça Z 302 (propriedades de cálculo)
ZP = PerfilZ(302, 90, 19, 2.30, "METSEC400", 45.0, 82, 21)
A_Z, IX_Z, IY_Z, J_Z = ZP.p["A"] * 1e-6, ZP.p["Ix"] * 1e-12, ZP.p["Iy"] * 1e-12, ZP.p["J"] * 1e-12
W_Z = CB["perfil"]["kg_m"] * 9.81e-3
ES, GS = 200e6, 77e6
Z_TER = 0.90 + 0.010 + 0.151                 # do fundo da TS-01 ao CG da terça
VB_H = 0.60

# ------------------------------------------------------------------ estado do modelo
nos, tag = {}, [0]
pil, ele = [], []                            # ele: dict(tag, tipo, grupo, n1, n2, ...)
TER_ELE = []                                 # elementos de terça: dict(tag, linha, vao, dentro_transpasse)
CLEAT = []                                   # zeroLength dos ST-1P: (tag, linha, eixo)
PORT = []                                    # zeroLength das ligações pilar do portão × TS-01 (y)
NO_TER = {}                                  # (indice_terça, y) -> nó da terça
NO_TS = {}                                   # (linha i, x) -> nó da TS-01 / VB (CG)
_eid = [0]


def _novo_tag():
    tag[0] += 1
    return tag[0]


def no(x, y, z, unico=False):
    k = (round(x, 4), round(y, 4), round(z, 4))
    if unico or k not in nos:
        t = _novo_tag()
        ops.node(t, *k)
        if unico:
            nos[k + (t,)] = t
            return t
        nos[k] = t
    return nos[k]


def _e():
    _eid[0] += 1
    return _eid[0]


TR_V, TR_X, TR_Y, TR_Z = 1, 2, 3, 4          # transformações: pilar (vertical), barra em x, barra em y, haste vertical


def montar(cfg):
    """cfg: dict(vaos_x=[k...], painel=n, A_x=m², fator_EI=float)."""
    ops.wipe(); ops.model("basic", "-ndm", 3, "-ndf", 6)
    nos.clear(); tag[0] = 0; pil.clear(); ele.clear(); TER_ELE.clear(); CLEAT.clear(); PORT.clear(); NO_TER.clear(); NO_TS.clear(); _eid[0] = 0
    ops.geomTransf("PDelta", TR_V, 1, 0, 0)
    ops.geomTransf("Linear", TR_X, 0, 0, 1)
    ops.geomTransf("Linear", TR_Y, 0, 0, 1)
    ops.geomTransf("Linear", TR_Z, 1, 0, 0)
    ops.uniaxialMaterial("Elastic", 10, ES, 0.0, 0.0)      # aço só tração (correntes, diagonais, X)
    ops.uniaxialMaterial("Elastic", 11, ES)                # aço tração e compressão (tirante rígido)
    ops.uniaxialMaterial("Elastic", 20, 1e9)               # rígido (ligações)
    fEI = cfg.get("fator_EI", 1.0)
    Ep, Gp = C40.Ecs * fEI, C40.Ecs * fEI / 2.4
    Ev, Gv = C50.Ecs, C50.Ecs / 2.4

    def pilar(nome, x, y, bx, by, ztop, zs_extra=(), rec=None, cab=None):
        zs = sorted(set([0.0, 2.5, 5.0, ztop] + [z for z in zs_extra if z < ztop] + ([rec] if rec else [])))
        ns = [no(x, y, z) for z in zs]
        ops.fix(ns[0], 1, 1, 1, 1, 1, 1)
        for k, (a, b) in enumerate(zip(ns[:-1], ns[1:])):
            sx, sy = (cab if (rec and zs[k] >= rec - 1e-6) else (bx, by))
            A, Iy, Iz = sx * sy, sy * sx ** 3 / 12, sx * sy ** 3 / 12
            J = 0.2 * min(sx, sy) ** 3 * max(sx, sy)
            t = _e(); ops.element("elasticBeamColumn", t, a, b, A, Ep, Gp, J, Iy, Iz, TR_V)
            ele.append(dict(tag=t, grupo="pilar", nome=nome, A=A))
        pil.append(dict(nome=nome, x=x, y=y, bx=bx, by=by, zs=zs, ns=ns))
        return ns

    def at(nome, z):
        p = next(p for p in pil if p["nome"] == nome)
        return p["ns"][p["zs"].index(min(p["zs"], key=lambda zz: abs(zz - z)))]

    def viga(n1, n2, A, Iy, Iz, J, grupo, transf, E=Ev, G=Gv, extra=None):
        t = _e(); ops.element("elasticBeamColumn", t, n1, n2, A, E, G, J, Iy, Iz, transf)
        d = dict(tag=t, grupo=grupo, n1=n1, n2=n2, A=A)
        if extra:
            d.update(extra)
        ele.append(d)
        return t

    def barra(n1, n2, A, grupo, mat, extra=None):
        t = _e(); ops.element("Truss", t, n1, n2, A, mat)
        d = dict(tag=t, grupo=grupo, n1=n1, n2=n2, A=A)
        if extra:
            d.update(extra)
        ele.append(d)
        return t

    # ---------------- pilares (como o r04)
    for i, y in enumerate(Y):
        canto = i in (0, 8)
        for nome, x0, k in (("P1", 0.0, 0), ("P2", LARG, 1)):
            zs = [REC[k]] + (list(Z_MEZ) if i <= 1 else []) + [7.50, 8.75]
            zr = REC[k] if not canto else math.ceil((zf(x0) + 0.90) / 0.05) * 0.05
            pilar(f"{nome}{'C' if canto else ''}-L{i+1}", x0, y, 0.60, 0.40, 10.0, zs, rec=zr, cab=(0.30, 0.30 if canto else 0.40))
    for j, x in enumerate(XF[1:4]):
        for nome, y in ((["P3", "P4", "P5"][j] + "-L1", 0.0), (["P3", "P14", "P5"][j] + "-L9", COMP)):
            zs = [zf(x) + 0.30] + (list(Z_MEZ) if y == 0 else []) + ([Z_I130] if "P14" in nome else []) + [7.50, 8.75]
            pilar(nome, x, y, 0.40, 0.60, 10.0, zs, rec=math.ceil((zf(x) + 0.90) / 0.05) * 0.05, cab=(0.40, 0.30))
    pilar("P8A", XC, Y[1], 0.40, 0.60, Z_TOP_C, [Z_I130] + list(Z_MEZ))
    pilar("P11", XC, Y[3], 0.40, 0.40, Z_TOP_C, [Z_I130])
    pilar("P13", XC, Y_P13, 0.60, 0.60, Z_TOP_C, [Z_I130])
    for nome, x in (("P8", XF[1]), ("P8B", XF[3])):
        pilar(nome, x, Y[1], 0.40, 0.60, Z_MEZ[1], list(Z_MEZ))
    for nome, x, b in (("P9", 9.87, 0.40), ("P10a", 15.195, 0.25), ("P10b", 24.305, 0.25), ("P12", 29.63, 0.40)):
        # rev05 (DEC-024): cabeça dos pilares dos portões a 2 cm do fundo da TS-01 (ligação em y por 2 chapas parafusadas)
        pilar(nome, x, Y[LINHA_PORTOES], b, b, round(zf(x) - 0.02, 3) if cfg.get("ligar_portoes", True) else 7.50, [6.25, 7.40])

    # ---------------- TS-01 (linhas 2 a 8): vigas 3D no CG (fundo + 0,45), nós em todas as terças
    A_TS, Iy_TS, Iz_TS, J_TS = 0.2225, 0.0198, 0.00177, 0.0016
    lin_cen = {}
    for i in range(1, 8):
        y = Y[i]
        for lado, xs, (xa, xb) in (("E", X_ESQ, (0.0, XC)), ("D", X_DIR, (XC, LARG))):
            cadeia = []
            extra_x = [xp for xp in X_PORTOES if xa < xp < xb] if (i == LINHA_PORTOES and cfg.get("ligar_portoes", True)) else []
            for x in sorted([xa + (0.15 if lado == "E" else 0.135)] + xs + extra_x + [xb - (0.135 if lado == "E" else 0.15)]):
                n = no(x, y, zf(x) + 0.45)
                cadeia.append(n)
                NO_TS[(i, round(x, 3))] = n
            for a, b in zip(cadeia[:-1], cadeia[1:]):
                viga(a, b, A_TS, Iy_TS, Iz_TS, J_TS, "TS-01", TR_X)
            # apoios: pinos (translações) + torção presa (2 pinos a ±0,10)
            n0, n1 = cadeia[0], cadeia[-1]
            if lado == "E":
                ops.equalDOF(at(f"P1-L{i+1}", REC[0]), n0, 1, 2, 3, 4)
                ncen = n1
            else:
                ops.equalDOF(at(f"P2-L{i+1}", REC[1]), n1, 1, 2, 3, 4)
                ncen = n0
            lin_cen.setdefault(i, []).append(ncen)
    # I130: P8A → L3 → P11 → L5 → L6 → P13 → L7 → L8 → P14 (viga 3D nos consolos dos pilares)
    A_I, Iy_I, Iz_I, J_I = 0.32, 0.0626, 0.0029, 0.0030
    pts_i = [("P8A", Y[1]), ("L3", Y[2]), ("P11", Y[3]), ("L5", Y[4]), ("L6", Y[5]), ("P13", Y_P13), ("L7", Y[6]), ("L8", Y[7]), ("P14-L9", COMP)]
    ni = {}
    for nome, y in pts_i:
        ni[nome] = no(XC, y, Z_I130 + 0.65, unico=True)
    for (na, _), (nb, _) in zip(pts_i[:-1], pts_i[1:]):
        viga(ni[na], ni[nb], A_I, Iy_I, Iz_I, J_I, "I130", TR_Y)
    for nome in ("P8A", "P11", "P13", "P14-L9"):
        ops.equalDOF(at(nome, Z_I130), ni[nome], 1, 2, 3, 5)
    # TS-01 no centro: linha 2 sobre o P8A (oblongo em x), linha 4 sobre o P11, demais sobre a I130
    for i, ns in lin_cen.items():
        for n in ns:
            if i == 1:
                ops.equalDOF(at("P8A", Z_TOP_C), n, 2, 3)
            elif i == 3:
                ops.equalDOF(at("P11", Z_TOP_C), n, 1, 2, 3)
            else:
                ops.equalDOF(ni[f"L{i+1}"], n, 1, 2, 3)
    # pilares dos portões (linha 4): cabeça ligada à TS-01 só em y (cantoneira com furo oblongo vertical) — leva a parede
    # interna da linha 4 para a cobertura (cfg ligar_portoes)
    if cfg.get("ligar_portoes", True):
        for nm, xp in zip(("P9", "P10a", "P10b", "P12"), X_PORTOES):
            p_ = next(pp for pp in pil if pp["nome"] == nm)
            t = _e()
            ops.element("zeroLength", t, NO_TS[(LINHA_PORTOES, round(xp, 3))], p_["ns"][-1], "-mat", 20, "-dir", 2)
            PORT.append(dict(tag=t, nome=nm, x=xp))
    # torção da TS no centro (2 pinos) — presa pelo par de pinos: rotação em x igual à do apoio
    # (o apoio central não tem rigidez à torção relevante; deixado livre)

    # ---------------- VB 15×60 das fachadas 1 e 9 (vigas 3D articuladas nos pilares, nós nas terças)
    A_VB, Iy_VB, Iz_VB, J_VB = 0.15 * VB_H, 0.15 * VB_H ** 3 / 12, VB_H * 0.15 ** 3 / 12, 0.2 * 0.15 ** 3 * VB_H
    for il, nomes in ((0, ["P1C-L1", "P3-L1", "P4-L1", "P5-L1", "P2C-L1"]), (8, ["P1C-L9", "P3-L9", "P14-L9", "P5-L9", "P2C-L9"])):
        y = Y[il]
        for k in range(4):
            xa, xb = XF[k], XF[k + 1]
            za, zb = zf(xa) + 0.90 - VB_H / 2, zf(xb) + 0.90 - VB_H / 2
            ea, eb = no(xa, y, za, unico=True), no(xb, y, zb, unico=True)
            for e_, nm in ((ea, nomes[k]), (eb, nomes[k + 1])):
                solta = cfg.get("vb_solta") and e_ == (ea if cfg.get("vb_solta") == "baixa" else eb)   # estudo DEC-033: ponta solta em x (nicho sem graute)
                ops.equalDOF(at(nm, zf(XF[nomes.index(nm)]) + 0.30), e_, *((2, 3, 5) if solta else (1, 2, 3, 5)))
            cadeia = [ea]
            for x in X_TER:
                if xa + 0.05 < x < xb - 0.05:
                    n = no(x, y, zf(x) + 0.90 - VB_H / 2)
                    NO_TS[(il, round(x, 3))] = n
                    cadeia.append(n)
            cadeia.append(eb)
            for x in (xa, xb):
                NO_TS.setdefault((il, round(x, 3)), ea if x == xa else eb)
            for a, b in zip(cadeia[:-1], cadeia[1:]):
                viga(a, b, A_VB, Iy_VB, Iz_VB, J_VB, "VB", TR_X, E=C40.Ecs, G=C40.Ecs / 2.4)

    # ---------------- terças Z contínuas (8 vãos), apoio ST-1P (haste rígida + zeroLength: translações + torção)
    ys_ter = []
    for k in range(8):
        ya, yb = Y[k], Y[k + 1]
        L = yb - ya
        pts = [ya, ya + L / 4, ya + L / 2, ya + 3 * L / 4]
        if k > 0:
            pts.append(ya + A_TR)
        if k < 7:
            pts.append(yb - A_TR)
        if k == 0:
            pts.append(ya + (0.0))
        ys_ter += pts
    ys_ter = sorted(set(round(v, 4) for v in ys_ter + [Y[8]]))
    ops.uniaxialMaterial("Elastic", 21, 1e7)
    for it, x in enumerate(X_TER):
        z_t = lambda: zf(x) + Z_TER
        ns = []
        for y in ys_ter:
            n = no(x, y, zf(x) + Z_TER, unico=True)
            NO_TER[(it, round(y, 4))] = n
            ns.append(n)
        for a, b, ya_, yb_ in zip(ns[:-1], ns[1:], ys_ter[:-1], ys_ter[1:]):
            ym = (ya_ + yb_) / 2
            dentro = any(abs(ym - Y[j]) < A_TR for j in range(1, 8))
            f = 2.0 if dentro else 1.0
            kv = max(kk for kk in range(8) if Y[kk] <= ym + 1e-9)
            t = viga(a, b, A_Z * f, IX_Z * f, IY_Z * f, J_Z * f, "terça", TR_Y, E=ES, G=GS,
                     extra=dict(linha=it, vao=f"{kv+1}-{kv+2}", y0=ya_, y1=yb_, transpasse=dentro))
            TER_ELE.append(ele[-1])
        # apoios em todas as linhas 1..9
        for il, yl in enumerate(Y):
            nt = NO_TER[(it, round(yl, 4))]
            base = NO_TS.get((il, round(x, 3)))
            if base is None:                                     # terça sobre pilar de canto/P4 (fachada): nó da VB mais próximo
                cand = [(abs(kx - x), n) for (ii, kx), n in NO_TS.items() if ii == il]
                base = min(cand)[1]
            topo = no(x, yl, zf(x) + Z_TER, unico=True)
            viga(base, topo, 0.05, 1e-2, 1e-2, 1e-2, "haste ST", TR_Z, E=ES, G=GS)
            t = _e()
            ops.element("zeroLength", t, topo, nt, "-mat", 20, 20, 20, 20, "-dir", 1, 2, 3, 5)
            CLEAT.append(dict(tag=t, linha=it, eixo=il, x=x, y=yl))

    # ---------------- correntes (só tração), tirantes rígidos e diagonais de ancoragem
    A10, A16, AL51 = math.pi * 0.010 ** 2 / 4, math.pi * 0.016 ** 2 / 4, 313e-6
    meias = [list(range(0, NT)), list(range(NT, 2 * NT))]
    for k in range(8):
        ya, yb = Y[k], Y[k + 1]
        L = yb - ya
        for yq in (ya + L / 4, ya + L / 2, ya + 3 * L / 4):
            for m in meias:
                for a, b in zip(m[:-1], m[1:]):
                    rig = (a == m[0]) or (b == m[-1])
                    barra(NO_TER[(a, round(yq, 4))], NO_TER[(b, round(yq, 4))], AL51 if rig else A10,
                          "tirante rígido" if rig else "corrente", 11 if rig else 10, extra=dict(vao=f"{k+1}-{k+2}"))
        # diagonais de ancoragem: da 2ª terça (nó da corrente) ao apoio da 1ª, nas duas pontas de cada meia água
        for m in meias:
            for p1, p2 in ((m[0], m[1]), (m[-1], m[-2])):
                for yq, ys_ in ((ya + L / 4, [ya]), (ya + L / 2, [ya, yb]), (ya + 3 * L / 4, [yb])):
                    for ysup in ys_:
                        barra(NO_TER[(p2, round(yq, 4))], NO_TER[(p1, round(ysup, 4))], A16, "diagonal de ancoragem", 10,
                              extra=dict(vao=f"{k+1}-{k+2}"))

    # ---------------- contraventamento em X (só tração), nós nas TS-01 / VB
    n_p = cfg.get("painel", 8)
    def lado(xs, x0, x1):
        if cfg.get("nos_x"):                                  # rev06: nós explícitos (terças 0, 8, 15)
            return [xs[i] for i in cfg["nos_x"]]
        idx = sorted(set(list(range(0, len(xs), n_p)) + [len(xs) - 1]))
        return [xs[i] for i in idx]
    xs_x = lado(X_ESQ, 0, XC) + lado(X_DIR, XC, LARG)
    def nts(il, x):
        n = NO_TS.get((il, round(x, 3)))
        if n is None:
            cand = [(abs(kx - x), n) for (ii, kx), n in NO_TS.items() if ii == il]
            n = min(cand)[1]
        return n
    for k in cfg.get("vaos_x", []):
        for lad in (lado(X_ESQ, 0, XC), lado(X_DIR, XC, LARG)):
            for a, b in zip(lad[:-1], lad[1:]):
                barra(nts(k, a), nts(k + 1, b), cfg.get("A_x", math.pi * 0.016 ** 2 / 4), "X", 10, extra=dict(vao=f"{k+1}-{k+2}"))
                barra(nts(k, b), nts(k + 1, a), cfg.get("A_x", math.pi * 0.016 ** 2 / 4), "X", 10, extra=dict(vao=f"{k+1}-{k+2}"))

    # ---------------- mezanino: VM + laje alveolar como diafragma rígido
    for z in Z_MEZ:
        l1 = [at(n, z) for n in ("P1C-L1", "P3-L1", "P4-L1", "P5-L1", "P2C-L1")]
        l2 = [at(n, z) for n in ("P1-L2", "P8", "P8A", "P8B", "P2-L2")]
        for row in (l1, l2):
            for a, b in zip(row[:-1], row[1:]):
                barra(a, b, 0.2225, "VM", 20)
        mestre = no(XC, Y[1] / 2, z, unico=True)
        ops.fix(mestre, 0, 0, 1, 1, 1, 0)
        ops.rigidDiaphragm(3, mestre, *(l1 + l2))
    montar.at = at


# ------------------------------------------------------------------ cargas
def _faixas(p):
    zs = p["zs"]
    out = []
    for k in range(1, len(zs)):
        z0 = (zs[k] + zs[k - 1]) / 2
        z1 = (zs[k] + zs[k + 1]) / 2 if k + 1 < len(zs) else zs[k]
        out.append((p["ns"][k], z0, z1, zs[k]))
    return out


V0, S3 = 45.0, 0.95
QV = lambda z: VNT.q(max(z, 3.0), V0, S3=S3)
H_ED = 10.0
CPE_P = VNT.cpe_paredes(H_ED, COMP, LARG)
CPE_C = VNT.cpe_cobertura(H_ED, LARG)
Y_AB = (Y[1], Y[3]); Z_ABERTO = 7.50
PORTOES_L4 = [(9.87, 15.195), (24.305, 29.63)]


def compartimento(y):
    return "anexo" if y < Y[1] else ("aberta" if y < Y[3] else "pavilhao")


def cpi_cenarios(d):
    """Pressões internas (anexo, área aberta, pavilhão) — 2 cenários extremos por direção."""
    cab = VNT.cpi_duas_faces(d in (90, 270)) if d in (90, 270) else (CPE_P["a0"]["A1"] if d == 0 else CPE_P["a0"]["A2"])
    return {"Cpi máx (sucção máx na cobertura)": (0.0, cab, max(0.0, cab)), "Cpi mín": (-0.3, cab, -0.3)}


def vento_paredes(d, ecc, interno):
    F = {}
    def add(n, fx, fy):
        v = F.setdefault(n, [0.0] * 6); v[0] += fx; v[1] += fy
    cb = CPE_P["a0"]["C"] if d in (0, 180) else CPE_P["a90"]["A"]
    cs = CPE_P["a0"]["D"] if d in (0, 180) else CPE_P["a90"]["B"]
    lista = []
    if d in (0, 180):
        sg = 1 if d == 0 else -1
        for yface, nomes in ((0.0, ["P1C-L1", "P3-L1", "P4-L1", "P5-L1", "P2C-L1"]), (COMP, ["P1C-L9", "P3-L9", "P14-L9", "P5-L9", "P2C-L9"])):
            barl = (yface == 0.0) == (d == 0)
            cp = cb if barl else -cs
            for i, nm in enumerate(nomes):
                p = next(pp for pp in pil if pp["nome"] == nm)
                for n, z0, z1, zk in _faixas(p):
                    lista.append((n, p["x"], sg * cp * QV(zk) * TRIB_X[i] * (z1 - z0)))
        R = sum(f for *_, f in lista)
        xm = sum(x * f for _, x, f in lista) / R
        den = sum(f * (x - xm) ** 2 for _, x, f in lista)
        c = 0.075 * LARG * ecc * R / den
        for n, x, f in lista:
            add(n, 0.0, f * (1 + c * (x - xm)))
        ca, cab, cpv = interno
        for iy, nomes, xs, dp, port in ((1, ["P1-L2", "P8", "P8A", "P8B", "P2-L2"], XF, ca - cab, []),
                                        (3, ["P1-L4", "P9", "P10a", "P11", "P10b", "P12", "P2-L4"], [0.0, 9.87, 15.195, XC, 24.305, 29.63, LARG], cab - cpv, PORTOES_L4)):
            for i, nm in enumerate(nomes):
                p = next(pp for pp in pil if pp["nome"] == nm)
                xa = xs[i - 1] if i > 0 else xs[i]; xb = xs[i + 1] if i + 1 < len(xs) else xs[i]
                for n, z0, z1, zk in _faixas(p):
                    zm = (z0 + z1) / 2
                    if zm > 7.50:
                        continue
                    w = 0.0
                    for a, b in ((xa, xs[i]), (xs[i], xb)):
                        # rev05: a folha do portão fechado leva a diferença de pressão aos pilares (a favor da segurança, sempre)
                        aberto = False
                        if not aberto:
                            w += abs(b - a) / 2
                    add(n, 0.0, dp * QV(zk) * w * (z1 - z0))
    else:
        sg = 1 if d == 90 else -1
        for xface, nomes in ((0.0, ["P1C-L1"] + [f"P1-L{i+1}" for i in range(1, 8)] + ["P1C-L9"]),
                             (LARG, ["P2C-L1"] + [f"P2-L{i+1}" for i in range(1, 8)] + ["P2C-L9"])):
            barl = (xface == 0.0) == (d == 90)
            cp = cb if barl else -cs
            for i, nm in enumerate(nomes):
                p = next(pp for pp in pil if pp["nome"] == nm)
                ya = Y[i - 1] if i > 0 else Y[i]; yb = Y[i + 1] if i + 1 < len(Y) else Y[i]
                for n, z0, z1, zk in _faixas(p):
                    zm = (z0 + z1) / 2
                    w = sum((b - a) / 2 for a, b in ((ya, Y[i]), (Y[i], yb))
                            if not ((a >= Y_AB[0] - 1e-6 and b <= Y_AB[1] + 1e-6) and zm < Z_ABERTO))
                    lista.append((n, p["y"], sg * cp * QV(zk) * w * (z1 - z0)))
        R = sum(f for *_, f in lista)
        ym = sum(y * f for _, y, f in lista) / R
        den = sum(f * (y - ym) ** 2 for _, y, f in lista)
        c = 0.075 * COMP * ecc * R / den
        for n, y, f in lista:
            add(n, f * (1 + c * (y - ym)), 0.0)
    return F


def cpe_cob(d, x, y):
    loc = CPE_C["largura_local"]
    if x <= loc or x >= LARG - loc or y <= loc or y >= COMP - loc:
        return CPE_C["local"]
    prof = CPE_C["profundidade_barlavento"]
    dist = {0: y, 180: COMP - y, 90: x, 270: LARG - x}[d]
    return CPE_C["barlavento"] if dist <= prof else CPE_C["sotavento"]


def aplicar(caso, fatores, desaprumo):
    """Aplica as cargas do caso: G, Qc, Qm (com fatores) e o vento (d, ecc, interno) com fator."""
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    fG, fQc, fQm, fW = fatores.get("G", 0), fatores.get("Qc", 0), fatores.get("Qm", 0), fatores.get("W", 0)
    nodal = {}
    def addn(n, f):
        v = nodal.setdefault(n, [0.0] * 6)
        for k in range(6):
            v[k] += f[k]
    # pilares (peso próprio)
    for p in pil:
        for k, (za, zb) in enumerate(zip(p["zs"][:-1], p["zs"][1:])):
            P = p["bx"] * p["by"] * 25 * (zb - za) * fG
            addn(p["ns"][k], [0, 0, -P / 2, 0, 0, 0]); addn(p["ns"][k + 1], [0, 0, -P / 2, 0, 0, 0])
    # vigas (peso próprio distribuído)
    for e in ele:
        if e["grupo"] in ("TS-01", "I130", "VB"):
            ops.eleLoad("-ele", e["tag"], "-type", "-beamUniform", 0.0, -e["A"] * 25 * fG)
    # terças: peso + pacote + sobrecarga + vento na cobertura
    for e in TER_ELE:
        x = X_TER[e["linha"]]; ym = (e["y0"] + e["y1"]) / 2
        w = -(W_Z + CC["g_total_sem_terca"] * S_TER) * fG - CC["sobrecarga"] * S_TER * fQc
        if fG < 1.2:                                   # combinação com G favorável: painéis e instalações desprezados (sucção)
            w = -(W_Z + CC["g_favoravel_sucao"] * S_TER) * fG
        if fW and caso:
            d, ecc, interno = caso
            ci = {"anexo": interno[0], "aberta": interno[1], "pavilhao": interno[2]}[compartimento(ym)]
            w += -(cpe_cob(d, x, ym) - ci) * QV(H_ED) * S_TER * fW
        if e["linha"] == 0:                            # rev06: calha do eixo A presa na 1ª terça (chapa + água com a calha cheia)
            w += -G_CALHA * fG - Q_CALHA * max(fQc, 0.7 if fG >= 1.2 else 0.0)
        ops.eleLoad("-ele", e["tag"], "-type", "-beamUniform", 0.0, w)
    # mezanino (reações nos pilares, como r04)
    at = montar.at
    gm, qm = 2.8 + 1.25 + 1.0, 5.0
    for z in Z_MEZ:
        for row in (("P1C-L1", "P3-L1", "P4-L1", "P5-L1", "P2C-L1"), ("P1-L2", "P8", "P8A", "P8B", "P2-L2")):
            for k, nm in enumerate(row):
                addn(at(nm, z), [0, 0, -(gm * 9.65 / 2 + A_VM * 25 + G_2E) * TRIB_X[k] * fG - qm * 9.65 / 2 * TRIB_X[k] * fQm, 0, 0, 0])
    if fW and caso:
        for n, f in vento_paredes(*caso).items():
            addn(n, [v * fW for v in f])
    # desaprumo H/400 nas cabeças dos pilares (NBR 9062 5.2.3), com a carga vertical total do pilar estimada
    if desaprumo:
        dx, dy = desaprumo
        for p in pil:
            N = sum(-nodal.get(n, [0] * 6)[2] for n in p["ns"])
            Ncob = 0.0
            addn(p["ns"][-1], [dx * (N + Ncob) / 400, dy * (N + Ncob) / 400, 0, 0, 0, 0])
    for n, v in nodal.items():
        ops.load(n, *v)


def rodar(cfg, fatores, caso=None, desaprumo=None, fator_EI=1.0):
    montar(dict(cfg, fator_EI=fator_EI))
    aplicar(caso, fatores, desaprumo)
    ops.system("UmfPack"); ops.numberer("RCM"); ops.constraints("Transformation")
    ops.test("NormDispIncr", 1e-7, 60); ops.algorithm("Newton")
    ops.integrator("LoadControl", 0.25); ops.analysis("Static")
    ok = ops.analyze(4)
    if ok != 0:
        ops.algorithm("ModifiedNewton"); ok = ops.analyze(4)
    ops.reactions()
    return ok == 0


# ------------------------------------------------------------------ resultados e verificações
TE = {e["vao"]: e for e in CB["terca_escora"]["por_vao"]}
MRc, MRb = CB["terca"]["MRd_contida"]["MRd"], CB["terca"]["MRd_correntes"]["MRd"]
W_FRACO = ZP.p["Iy"] / (max(abs(v[0]) for v in ZP.pts) + 1.15) * 1e-9          # m³ (eixo fraco)
MRz = W_FRACO * ZP.fy * 1e3 / 1.10
NT10, NT16 = barra_redonda_tracao_Rd(10.0), barra_redonda_tracao_Rd(16.0)
NCR_L51 = compressao_laminado_Rd(313.0, 10.0, S_TER * 1000, fy=250)[0]


def coletar(cfg):
    R = dict(terca=None, grupos={})
    # terças: N, My (vertical) e Mz (lateral) por elemento; interação NBR 14762 9.9 (com amplificação no N)
    pior = dict(it=0)
    for e in TER_ELE:
        f = ops.eleResponse(e["tag"], "localForce")
        N = -f[0]                                        # compressão positiva
        for My, Mz in ((-f[4], -f[5]), (f[10], f[11])):         # momento na seção: −M_i no início, +M_j no fim (M < 0 = vão sob G)
            fat = 2.0 if e["transpasse"] else 1.0
            te = TE[e["vao"]]
            Nex = math.pi ** 2 * ES * IX_Z / te["L_m"] ** 2
            Nc = max(N, 0.0)
            amp = 1 / (1 - Nc / (fat * Nex)) if Nc < fat * Nex else 99
            MR = MRc if My < 0 else MRb                      # convenção calibrada: My < 0 → mesa superior comprimida (vão sob G)
            it = Nc / (fat * te["NcRd"]) + abs(My) * amp / (fat * MR) + abs(Mz) / (fat * MRz)
            if it > pior["it"]:
                pior = dict(it=round(it, 3), linha=e["linha"], x=X_TER[e["linha"]], vao=e["vao"], N=round(N, 1), My=round(My, 2), Mz=round(Mz, 2),
                            transpasse=e["transpasse"])
    R["terca"] = pior
    for g in ("corrente", "tirante rígido", "diagonal de ancoragem", "X", "TS-01", "VB", "I130"):
        vals = []
        for e in ele:
            if e["grupo"] != g:
                continue
            if g in ("TS-01", "VB", "I130"):
                f = ops.eleResponse(e["tag"], "localForce")
                vals.append(max(abs(f[5]), abs(f[11])))          # momento lateral (eixo fraco: plano da cobertura)
            else:
                vals.append(ops.basicForce(e["tag"])[0])
        if vals:
            R["grupos"][g] = dict(max=round(max(vals), 2), min=round(min(vals), 2))
    # ST-1P: forças no zeroLength (global): Fx, Fy, Fz, Ty
    ap = dict(Fz_up=0.0, Fz_down=0.0, Fy=0.0, Fx=0.0, T=0.0)
    for c in CLEAT:
        f = ops.eleResponse(c["tag"], "force")          # 12 componentes (nó i, nó j)
        ap["Fz_up"] = max(ap["Fz_up"], f[2]); ap["Fz_down"] = min(ap["Fz_down"], f[2])
        ap["Fy"] = max(ap["Fy"], abs(f[1])); ap["Fx"] = max(ap["Fx"], abs(f[0])); ap["T"] = max(ap["T"], abs(f[4]))
    R["ST1P"] = {k: round(v, 2) for k, v in ap.items()}
    # verificação de cada ST-1P (4 M12 8.8 na alma + 2 esperas M16 na viga), com os esforços do próprio modelo
    apo = CB["terca"]["apoio"]; st = CB["ST1P"]
    TRd, VbRd = min(apo["Ft_Rd"], apo["arrancamento_alma_Rd"]), apo["Vb_Rd"]
    FtE, FvE = st["esperas"]["Ft_Rd"], st["esperas"]["Fv_Rd"]
    e_t, z_p = 0.045, 0.195
    pc_ = dict(it=0.0)
    n_falha = 0
    n_esp9 = cfg.get("esperas_eixo9", 4)                  # rev05 (DEC-024): ST-1V-R com 4 esperas no eixo 9
    por_grupo = {}
    x_ponta = {e_: max(c["x"] for c in CLEAT if c["eixo"] == e_) for e_ in (0, 8)}   # 22/10 (DEC-042): terça de ponta do lado E nos cantos → ST-1FL
    for c in CLEAT:
        f = ops.eleResponse(c["tag"], "force")
        Rz, Fy, Fx = f[2], f[1], f[0]
        Tb = abs(Rz) * e_t / z_p / 2
        Vb = math.sqrt(Rz ** 2 + Fy ** 2 + Fx ** 2) / 4
        it_b = (Tb / TRd) ** 2 + (Vb / VbRd) ** 2
        ne = n_esp9 if c["eixo"] == 8 else 2
        Te = max(-Rz, 0.0) * 1.25 / ne                        # arrancamento (Rz < 0: a terça puxa o ST-1P para cima)
        Ve = math.hypot(Fy, Fx) / ne
        it_e = (Te / FtE) ** 2 + (Ve / FvE) ** 2
        it = max(it_b, it_e)
        if it > 1.0:
            n_falha += 1
        gr_ = "ST-1V eixo 1" if c["eixo"] == 0 else "ST-1V-R eixo 9" if c["eixo"] == 8 else "ST-1P"
        pg = por_grupo.setdefault(gr_, dict(it=0.0, Fy_max=0.0, Fx_max=0.0, Rz_up=0.0, Rz_down=0.0, esperas=ne))
        pg["Fy_max"] = max(pg["Fy_max"], round(abs(Fy), 2)); pg["Fx_max"] = max(pg["Fx_max"], round(abs(Fx), 2))
        pg["Rz_up"] = max(pg["Rz_up"], round(-Rz, 2)); pg["Rz_down"] = max(pg["Rz_down"], round(Rz, 2))
        if c["eixo"] in (0, 8) and abs(c["x"] - x_ponta[c["eixo"]]) < 1e-6:
            fl = por_grupo.setdefault("ST-1FL canto", dict(it=0.0, Fy_max=0.0, Fx_max=0.0, Rz_up=0.0, Rz_down=0.0, V_max=0.0, x=round(c["x"], 2)))
            fl["Fy_max"] = max(fl["Fy_max"], round(abs(Fy), 2)); fl["Fx_max"] = max(fl["Fx_max"], round(abs(Fx), 2))
            fl["Rz_up"] = max(fl["Rz_up"], round(-Rz, 2)); fl["Rz_down"] = max(fl["Rz_down"], round(Rz, 2))
            fl["V_max"] = max(fl["V_max"], round(math.sqrt(Rz ** 2 + Fy ** 2 + Fx ** 2), 2))
        if it > pg["it"]:
            pg.update(it=round(it, 3), parafusos=round(it_b, 3), esperas_it=round(it_e, 3), linha=c["linha"], x=round(c["x"], 2), Rz=round(Rz, 1),
                      Fy=round(Fy, 1), Fx=round(Fx, 1))
        if it > pc_["it"]:
            pc_ = dict(it=round(it, 3), parafusos=round(it_b, 3), esperas=round(it_e, 3), linha=c["linha"], x=round(c["x"], 2), eixo=c["eixo"] + 1,
                       Rz=round(Rz, 1), Fy=round(Fy, 1), Fx=round(Fx, 1))
    R["ST1P_verif"] = dict(pior=pc_, n_reprovados=n_falha, por_grupo=por_grupo)
    R["portoes"] = {p_["nome"]: round(abs(ops.eleResponse(p_["tag"], "force")[1]), 2) for p_ in PORT}
    # pilares
    base, uso = {}, {}
    for p in pil:
        r = ops.nodeReaction(p["ns"][0])
        Mx, My, N = -r[3], -r[4], r[2]
        base[p["nome"]] = (round(N, 1), round(Mx, 1), round(My, 1))
        tp = _pil.tipo_pilar(p["nome"])
        d1, d2, n1, n2, dd = _pil.ARM[tp]
        bx, by = p["bx"], p["by"]
        nx, ny = (n1, n2) if abs(bx - d1) < 1e-6 else (n2, n1)
        brs = _pil.barras(bx, by, nx, ny, dd)
        MRx = _pil.MRd(bx, by, brs, max(N, 0), "y"); MRy = _pil.MRd(by, bx, brs, max(N, 0), "x")
        uso[p["nome"]] = round((abs(Mx) / MRx) ** 1.2 + (abs(My) / MRy) ** 1.2, 3)
    R["pilar_uso_max"] = max(uso.values()); R["pilar_critico"] = max(uso, key=uso.get)
    R["M_base_max"] = round(max(math.hypot(v[1], v[2]) for v in base.values()), 1)
    R["desl_topo_max_mm"] = round(max(math.hypot(ops.nodeDisp(p["ns"][-1], 1), ops.nodeDisp(p["ns"][-1], 2)) for p in pil) * 1000, 1)
    return R


def combinacoes():
    out = []
    for d in (0, 180, 90, 270):
        for nome_c, interno in cpi_cenarios(d).items():
            for ecc in (-1, 1):
                caso = (d, ecc, interno)
                dsp = (0, 1) if d == 0 else (0, -1) if d == 180 else (1, 0) if d == 90 else (-1, 0)
                out.append((f"ELU V{d} {nome_c} e{ecc:+d} G1,3", dict(G=1.3, W=1.4, Qc=0.7, Qm=0.98), caso, dsp))
                out.append((f"ELU V{d} {nome_c} e{ecc:+d} G1,0", dict(G=1.0, W=1.4), caso, dsp))
    out.append(("ELU sobrecarga", dict(G=1.3, Qc=1.4, Qm=1.4), None, None))
    return out


def analisar(cfg, combs=None, verbose=False):
    res = {}
    for nome, fat, caso, dsp in (combs or combinacoes()):
        ok = rodar(cfg, fat, caso, dsp, fator_EI=0.4 * C40.Eci / C40.Ecs)
        r = coletar(cfg); r["ok"] = ok
        res[nome] = r
        if verbose:
            print(f"{nome:55s} ok={ok} terça {r['terca']['it']:.2f} pilar {r['pilar_uso_max']:.2f} X {r['grupos'].get('X', {}).get('max', 0):.1f} "
                  f"corr {r['grupos']['corrente']['max']:.1f} diag {r['grupos']['diagonal de ancoragem']['max']:.1f}", flush=True)
    return res


def envoltoria(res):
    env = dict(terca=max((r["terca"] for r in res.values()), key=lambda t: t["it"]),
               pilar_uso_max=max(r["pilar_uso_max"] for r in res.values()),
               M_base_max=max(r["M_base_max"] for r in res.values()))
    for g in ("corrente", "tirante rígido", "diagonal de ancoragem", "X"):
        vs = [r["grupos"][g] for r in res.values() if g in r["grupos"]]
        if vs:
            env[g] = dict(max=max(v["max"] for v in vs), min=min(v["min"] for v in vs))
    env["ST1P"] = {k: max((r["ST1P"][k] for r in res.values()), key=abs) for k in ("Fz_up", "Fz_down", "Fy", "Fx", "T")}
    env["ST1P_verif"] = max((r["ST1P_verif"]["pior"] for r in res.values()), key=lambda d: d["it"])
    env["ST1P_reprovados_max"] = max(r["ST1P_verif"]["n_reprovados"] for r in res.values())
    env["ST1P_grupos"] = {}
    for r in res.values():
        for k_, v_ in r["ST1P_verif"]["por_grupo"].items():
            e_ = env["ST1P_grupos"].setdefault(k_, dict(v_))
            for c_ in ("Fy_max", "Fx_max", "Rz_up", "Rz_down", "V_max"):
                if c_ in v_:
                    e_[c_] = max(e_[c_], v_[c_])
            if v_["it"] > e_["it"]:
                e_.update({c_: v_[c_] for c_ in v_ if c_ not in ("Fy_max", "Fx_max", "Rz_up", "Rz_down", "V_max")})
    env["portoes"] = {k_: max(r["portoes"].get(k_, 0.0) for r in res.values()) for k_ in ("P9", "P10a", "P10b", "P12")}
    env["TS01_M_lateral"] = max(r["grupos"]["TS-01"]["max"] for r in res.values())
    env["usos"] = dict(corrente=round(env["corrente"]["max"] / NT10, 3), diagonal=round(env["diagonal de ancoragem"]["max"] / NT16, 3),
                       tirante=round(-env["tirante rígido"]["min"] / NCR_L51, 3))
    return env


if __name__ == "__main__":
    cfg = dict(vaos_x=[int(v) for v in os.environ.get("VAOS_X", "3,4,5,6,7").split(",") if v != ""], painel=int(os.environ.get("PAINEL", "8")),
               A_x=math.pi * 0.016 ** 2 / 4, esperas_eixo9=4, nos_x=IDX_NOS_X)
    res = analisar(cfg, verbose=True)
    env = envoltoria(res)
    print(json.dumps(env, ensure_ascii=False, indent=1))
    (AQ / "modelo_integrado_r05.json").write_text(json.dumps(dict(config=cfg, envoltoria=env, combinacoes=res), ensure_ascii=False), encoding="utf-8")
