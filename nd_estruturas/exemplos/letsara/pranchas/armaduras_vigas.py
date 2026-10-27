"""ND-LET-AR-VIG-xx — ARMADURAS DAS VIGAS no padrão de entrega de pré-moldados (ref. PCH Três Capões, SP301):
uma família por folha A0: elevação de armação da marca representativa, zonas de estribos cotadas, barras longitudinais
explodidas abaixo da elevação (mesma escala, alinhadas com a posição na peça), seções S.x e detalhe da ponta 1:20 com as
barras desenhadas ao lado, TABELA DE FERROS 1 UNIDADE / N UNIDADES por marca, RESUMO DO AÇO +10% (com cordoalhas),
Fck, volume de concreto e área de fôrma. Barras e quantidades: mesmas funções das pranchas de fôrma (viga_i.armacao_i,
ts01_dados.armacao_ts01, fechamento.vt_barras)."""
import json, math, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from prancha_nd import Prancha, _wtext, ALTURAS
from arm_nd import Arm, zonas, fd, f1, dividir_barras, nota_traspasse, aderencia_boa

COB = 30
KG_CORD = 0.775                                     # kg/m, cordoalha Ø12,7 CP-190 (98,7 mm²)


def zonas_txt(xs, pos, d, extra=""):
    return [(a, b, f"{n} {pos} Ø{fd(d)} C/{fd(s/10)}{extra}") for a, b, n, s in zonas(xs)]


# ================================================================== especificações por família
def spec_ts01():
    """TS-01 rev03: sem dentes; N6 (estribos do maciço), N7 (grampos U) e N8 (estribos horizontais) nas pontas; cordoalhas de ts01_dados (C2 isoladas). DEC-043: 10."""
    import ts01_dados as T
    L, H, DX, P = T.L, T.H, T.DX, T.P
    sk = lambda h: h * DX / H
    x_est, _, barras = T.armacao_ts01()
    barras, TR = dividir_barras(barras, P['fck'], boa={'N2': aderencia_boa(H - 45, H), 'N5': aderencia_boa(40, H)})   # barras de usina de 12 m
    X_N6 = [40, 90, 190, 240, 290, 340, 390, 440]
    cont = [(0, 0), (L, 0), (L + DX, H), (DX, H)]
    ents = [([(x + sk(40), 40), (x + sk(H - 40), H - 40)], "ARM_TRANSV") for x in x_est]
    ents += [([(x + sk(30), 30), (x + sk(H - 30), H - 30)], "ARM_TRANSV") for xs_ in (X_N6, [L - x for x in X_N6]) for x in xs_]
    ents += [([(30, H - 45), (L - 30, H - 45)], "ARMADURA"), ([(30, 40), (L - 30, 40)], "ARMADURA"),
             ([(0, P["y1"]), (L, P["y1"])], "ARM_PROT"), ([(0, P["y2"]), (L, P["y2"])], "ARM_PROT"),
             ([(30, H - 70), (30 + T.L_N9, H - 70)], "ARMADURA"), ([(L - 30 - T.L_N9, H - 70), (L - 30, H - 70)], "ARMADURA")]   # N9 (ato)
    zs = [(X_N6[0], X_N6[-1], "8 N6")] + zonas_txt(x_est, "N1", 6.3) + [(L - X_N6[-1], L - X_N6[0], "8 N6")]
    sec = [(x * 1000, y * 1000) for x, y in T.sec.pts]
    prot = [(x, P["y1"]) for x in P["x_cord"]] + [(x, P["y2"]) for x in P["x_cord2"]]
    S1 = dict(nome="SEÇÃO S.1", sub="corrente", esc=10, contorno=[sec],
              ents=[([(-45, 30), (45, 30), (45, H - 30), (-45, H - 30)], "ARM_TRANSV", True),
                    ([(-170, H - 30), (170, H - 30), (170, H - 100), (-170, H - 100)], "ARM_TRANSV", True),
                    ([(-170, 30), (170, 30), (170, 130), (-170, 130)], "ARM_TRANSV", True)],
              discos=[(x, H - 45, 12.5) for x in (-160, -60, 60, 160)] + [(x, 40, 10) for x in (-165, 165)],
              prot=prot,
              bolhas=[("N1", (45, 450), (8, 0)), ("N2", (160, H - 45), (8, 6)), ("N3", (-170, H - 65), (-8, 4)), ("N4", (-170, 80), (-8, -4)), ("N5", (165, 40), (8, -6))],
              formas=["N1", "N3", "N4"], prot_txt=f"C1/C2 — {P['n_cord']} cord. Ø12,7 ({T.TXT_LINHAS})")
    S2 = dict(nome="SEÇÃO S.2", sub="maciço da ponta (tubos TB-3 a y = ±10)", esc=10, contorno=[[(-200, 0), (200, 0), (200, H), (-200, H)]],
              ents=[([(-170, 30), (170, 30), (170, H - 30), (-170, H - 30)], "ARM_TRANSV", True),
                    ([(-125, 0), (-75, 0), (-75, H), (-125, H)], "OCULTA", True), ([(75, 0), (125, 0), (125, H), (75, H)], "OCULTA", True)],
              discos=[(x, H - 45, 12.5) for x in (-160, -60, 60, 160)] + [(x, H - 70, 10) for x in (-110, 110)], prot=prot,
              bolhas=[("N6", (170, 560), (8, 4)), ("N2", (-160, H - 45), (-8, 6)), ("N9", (110, H - 70), (14, 3))], formas=["N6"])
    det = [([(1600, 0), (0, 0), (DX, H), (1600 + DX, H)], "VISTA", False),
           ([(0, P["y1"]), (1600, P["y1"])], "ARM_PROT", False), ([(0, P["y2"]), (1600, P["y2"])], "ARM_PROT", False)]
    det += [([(x + sk(30), 30), (x + sk(H - 30), H - 30)], "ARM_TRANSV", False) for x in X_N6]
    det += [([(30, yy), (780, yy)], "ARM_TRANSV", False) for yy in (35, 125)] + [([(30, 80), (630, 80)], "ARM_TRANSV", False)]
    det += [([(115, 0), (115 + DX, H)], "OCULTA", False), ([(165, 0), (165 + DX, H)], "OCULTA", False)]
    D1 = dict(nome="DETALHE D1 — PONTA (APOIO DIRETO)", sub=f"as duas pontas iguais (TB-3 a 14 e 7,75 cm da ponta); face da ponta a prumo na posição montada: topo {fd(DX/10)} cm à frente do fundo", esc=10, contorno=[], ents=det, discos=[], prot=[],
              cotas=[((0, 0), (DX, H), 0, 80, f"{fd(DX/10)} (topo × fundo)"), ((0, 0), (DX, H), 90, -150, f"{fd(H/10)}"), ((0, 0), (300, 0), 0, -100, "30 (cunha)")],
              bolhas=[("N6", (290 + sk(500), 500), (8, 8)), ("N7", (400, 80), (10, -16)), ("N8", (600, 125), (8, 10))],
              formas=["N6", "N7", "N8"])
    V = T.V
    per = sum(math.dist(a, b) for a, b in zip(sec, sec[1:] + sec[:1])) / 1000
    area = per * L / 1000 - 0.40 * L / 1000 + 2 * 0.40 * 0.90               # laterais + fundo (topo livre) + topos
    cord = (P["n_cord"], P["n_cord"] * L / 1000)
    return dict(fam="TS-01", titulo="VIGA DE COBERTURA TS-01 (I90 PROTENDIDA, SEM DENTES)", forma="ND-LET-TS01-1", fck=50, L=L, H=H, esc=40,
                contorno=[cont], ents=ents, zonas=zs, cortes=[(L / 2 + 1500, "S.1"), (600, "S.2")], dets=[(350, "D1")],
                longas=[("N2", 30), ("N5", 30), ("N9", 30)], blocos=[S1, S2, D1],
                marcas=[dict(marca="TS-01", qtd=P["qtd"], L=L, barras=barras, V=V, area=area, cord=cord, traspasse=TR)],
                notas=[f"Concreto C{P['fck']}; liberar as cordoalhas com fckj ≥ {P['fckj']} MPa. Cordoalhas CP-190 RB Ø12,7: {T.TXT_LINHAS}; C2: {T.TXT_C2}; σpi = {P['sig_pi']} MPa. Protensão completa (NBR 6118:2023 Tab. 13.4, DEC-043).",
                       "Sem dentes: N6 (estribos verticais do maciço, fora da faixa dos tubos TB-3), N7 (grampos U horizontais) e N8 (estribos horizontais da mesa inferior) nas duas pontas.",
                       "Estribos N1 a prumo na fôrma (ponta inclinada 3 %); alças AL-1 e esperas ES-1/ES-2 entre estribos, sem cortar armadura."] + ([nota_traspasse(TR)] if TR else []))


def spec_i(qual):
    import viga_i as VI
    P = VI.dados_i110() if qual == "i110" else VI.dados_vm()
    H, B, L, bw, ts, ti = P["h"], P["b"], P["L"], P["bw"], P["ts"], P["ti"]
    HD, LN = P["dente"]
    cob = COB
    xs_e, barras = VI.armacao_i(P, L)
    bar = {b["pos"]: b for b in barras}
    cont = [(0, H - HD), (LN, H - HD), (LN, 0), (L - LN, 0), (L - LN, H - HD), (L, H - HD), (L, H), (0, H)]
    ents = [([(x, cob), (x, H - cob)], "ARM_TRANSV") for x in xs_e]
    for y, xs, isol in P["cord"]:
        x0c = LN if y < H - HD else 0                                   # cordoalhas da mesa superior vão de ponta a ponta
        ents.append(([(x0c, y), (L - x0c, y)], "ARM_PROT"))
    ents.append(([(cob, H - cob - 5), (L - cob, H - cob - 5)], "ARMADURA"))
    for yy in P.get("pele", []):
        ents.append(([(cob, yy), (L - cob, yy)], "ARMADURA"))
    ents.append(([(LN + cob, cob + 5), (L - LN - cob, cob + 5)], "ARMADURA"))
    n_sus, n_cost, n_v = P["n_sus"], P["n_cost"], P["n_v"]
    for x0_, sg in ((0, 1), (L, -1)):
        y_t = H - HD + 55
        ents.append(([(x0_ + sg * cob, y_t), (x0_ + sg * P["anc"], y_t)], "ARMADURA"))          # N5: alças horizontais (U deitado)
        for k in range(n_sus):
            x = x0_ + sg * (LN + 60 + k * 80)
            ents.append(([(x, cob), (x, H - cob)], "ARM_TRANSV"))
        for xk in VI.x_n8(n_v, LN, P["pino_x"]):
            x = x0_ + sg * xk
            ents.append(([(x, H - HD + cob), (x, H - cob)], "ARM_TRANSV"))
    SEG = P.get("seg")
    if SEG:
        for x in range(100, L - 60, 150):
            ents.append(([(x, H), (x, H + 170)], "ARM_TRANSV"))
        ents.append(([(100, H + 160), (L - 100, H + 160)], "ARMADURA"))
    d_est = P["est"][0]
    zs = zonas_txt(xs_e, "N2", d_est)
    pts = VI.sec_pts(B, H, ts, ti, P["m"], bw)
    N3n, N3d, _ = P.get("n3", (2, 10.0, ""))
    _p3 = VI.pos_n3(P, B, H, cob)
    xs3 = [x for x, _ in _p3]
    s1_ents = [([(-bw / 2 + cob, cob), (bw / 2 - cob, cob), (bw / 2 - cob, H - cob), (-bw / 2 + cob, H - cob)], "ARM_TRANSV", True),
               ([(-B / 2 + cob, cob), (B / 2 - cob, cob), (B / 2 - cob, ti - cob), (-B / 2 + cob, ti - cob)], "ARM_TRANSV", True),
               ([(-B / 2 + cob, H - ts + cob), (B / 2 - cob, H - ts + cob), (B / 2 - cob, H - cob), (-B / 2 + cob, H - cob)], "ARM_TRANSV", True)]
    discos = [(x, y3, N3d) for x, y3 in _p3] + [(x, cob + 5, 10) for x in (-B / 2 + cob, B / 2 - cob)]
    discos += [(x, yy, 8) for yy in P.get("pele", []) for x in (-bw / 2 + cob, bw / 2 - cob)]
    bol = [("N2", (bw / 2 - cob, (ti + H - ts) / 2), (10, 2)), ("N3", (xs3[-1], H - cob - 5), (8, 6)), ("N13", (-B / 2 + cob, H - ts + cob + 20), (-8, 2)),
           ("N11", (-B / 2 + cob, ti - cob - 20), (-8, -2)), ("N12", (B / 2 - cob, cob + 5), (8, -6))]
    if P.get("pele"):
        bol.append(("N4", (-bw / 2 + cob, P["pele"][0]), (-10, 0)))
    if SEG:
        xs9 = (-bw / 2 + cob, bw / 2 - cob)
        s1_ents.append(([(xs9[0], H - 200), (xs9[0], H + 170), (xs9[1], H + 170), (xs9[1], H - 200)], "ARM_TRANSV", False))
        discos += [(x, H + 160, 10) for x in xs9]
        bol += [("N9", (xs9[1], H + 100), (10, 2)), ("N10", (xs9[0], H + 160), (-8, 4))]
    prot = [(x, y) for y, xs, _ in P["cord"] for x in xs]
    n_cord = sum(len(xs) for _, xs, _ in P["cord"])
    S1 = dict(nome="SEÇÃO S.1", sub="corrente", esc=10, contorno=[pts], ents=s1_ents, discos=discos, prot=prot, bolhas=bol,
              formas=["N2", "N11", "N13"] + (["N9"] if SEG else []), prot_txt=f"C1 — {n_cord} cord. {P.get('cord_txt', 'Ø12,7')}")
    LD = max(1800, 2 * LN + 800)
    y_t = H - HD + 55
    det = [([(0, H - HD), (LN, H - HD), (LN, 0), (LD, 0)], "VISTA", False), ([(LD, H), (0, H), (0, H - HD)], "VISTA", False),
           ([(cob, y_t), (P["anc"] if P["anc"] < LD else LD, y_t)], "ARMADURA", False)]
    det += [([(LN + 60 + k * 80, cob), (LN + 60 + k * 80, H - cob)], "ARM_TRANSV", False) for k in range(n_sus)]
    det += [([(cob, H - HD + 150 + k * 100), (min(LN + 900, LD), H - HD + 150 + k * 100)], "ARM_TRANSV", False) for k in range(n_cost)]
    det += [([(xk, H - HD + cob), (xk, H - cob)], "ARM_TRANSV", False) for xk in VI.x_n8(n_v, LN, P["pino_x"])]
    det += [([(LN if y < H - HD else 0, y), (LD, y)], "ARM_PROT", False) for y, _, _ in P["cord"]]
    D1 = dict(nome="DETALHE D1 — DENTE GERBER", sub=f"dente {HD/10:g} × {LN/10:g}; as duas pontas iguais", esc=10, contorno=[], ents=det, discos=[], prot=[],
              cotas=[((0, H - HD), (LN, 0), 0, -100, f"{fd(LN/10)}"), ((0, H - HD), (0, H), 90, -60, f"{fd(HD/10)}"), ((LN, 0), (LN, H - HD), 90, -60, f"{fd((H-HD)/10)} (recorte)"), ((LD, 0), (LD, H), 90, 120, f"{fd(H/10)}")],
              bolhas=[("N5", (LN + 300, y_t), (4, 8)), ("N6", (LN + 60, H / 2), (10, -10)), ("N7", (LN + 500, H - HD + 150), (10, -14)), ("N8", (100, H - 100), (-26, 14))],
              formas=["N5", "N6", "N7", "N8"], corte_x=LD)
    blocos_extra = []
    CTp = P.get("ct")
    if CTp:                                                                  # rev10 (DEC-061): consolo lateral CT-I120
        bw2, pj, hc, he = bw / 2, CTp["proj"], CTp["h"], CTp["h_ext"]
        pdd = [(-B / 2, H - 450), (-bw2, H - 450), (-bw2, H - hc), (-B / 2, H - hc), (-B / 2 - pj, H - he), (-B / 2 - pj, H), (B / 2 + pj, H), (B / 2 + pj, H - he),
               (B / 2, H - hc), (bw2, H - hc), (bw2, H - 450)]
        xe = B / 2 + pj - cob
        ents_ct = [([(-xe, H - CTp["c_tir"]), (xe, H - CTp["c_tir"])], "ARMADURA", False)] + [([(-xe, yy), (xe, yy)], "ARM_TRANSV", False) for yy in (H - 140, H - 200)]
        for sg in (-1, 1):
            x0_, x1_ = sg * (B / 2 + 30), sg * (B / 2 + pj - cob)
            ents_ct.append(([(x0_, H - 120), (x1_, H - 120), (x1_, H - cob), (x0_, H - cob)], "ARM_TRANSV", True))
        blocos_extra.append(dict(nome="DETALHE D2 — CONSOLO LATERAL CT-I120", sub=f"nas 2 faces, em cada linha de TS-01; b {CTp['b']/10:g}, projeção {pj/10:g}, h {hc/10:g}/{he/10:g}", esc=10,
                                 contorno=[pdd], ents=ents_ct, discos=[], prot=[],
                                 bolhas=[("N14", (xe * 0.6, H - CTp["c_tir"]), (6, 10)), ("N15", (-xe * 0.6, H - 200), (-6, -10)), ("N16", (B / 2 + pj - cob, H - 120), (10, -8))],
                                 formas=["N14", "N15", "N16"],
                                 cotas=[((-B / 2 - pj, H), (-B / 2, H), 0, 60, f"{fd(pj/10)}"), ((B / 2 + pj, H - he), (B / 2 + pj, H), 90, 80, f"{fd(he/10)}"), ((-B / 2 - pj, H - hc), (-B / 2 - pj, H), 90, -80, f"{fd(hc/10)}")]))
    marcas = []
    BOA_I = {"N3": aderencia_boa(H - cob - 15, H), "N4": aderencia_boa(max(P.get("pele") or [0]), H), "N12": aderencia_boa(cob + 5, H),
             "N10": aderencia_boa(H + 160, H)}
    if qual == "i110":
        for mk in ("V407", "V406", "V405", "V404"):                             # DEC-058
            Lm = round(VI.I1J[mk]["L_peca"] * 1000)
            _, bm = VI.armacao_i(P, Lm, n_ct=P.get("ct_n", {}).get(mk, 0))
            bm, TRm = dividir_barras(bm, P["fck"], boa=BOA_I)                     # barras de usina de 12 m
            A = VI.area_I(B, H, ts, ti, P["m"], bw)
            Vm = A * Lm / 1000 + (B * H / 1e6 - A) * P["x_mac"] / 1000 * 2 - 2 * B * (H - HD) * LN / 1e9
            nc_mk = VI.I1J[mk]["arranjo"]["n_cord"] if "arranjo" in VI.I1J[mk] else n_cord
            marcas.append(dict(marca=mk, qtd=1, L=Lm, barras=bm, V=Vm, area=_area_I(pts, B, H, Lm), cord=(nc_mk, nc_mk * Lm / 1000), traspasse=TRm,
                               ctxt=P.get("cord_txt", "Ø12,7"), kgc={"Ø15,2": 1.102}.get(P.get("cord_txt"), KG_CORD)))   # DEC-054: Ø15,2 = 1,102 kg/m
        fam, tit, forma = "I120", f"VIGAS CENTRAIS I120 PROTENDIDAS — V404, V405, V406, V407", "ND-LET-I120"
    else:
        L1 = round((VI.X_EIXO["B"] - 0.20 - 0.30 - 0.10) * 1000)
        for mk, Lm in (("VM-01", L1), ("VM-02", L)):
            _, bm = VI.armacao_i(P, Lm)
            bm, TRm = dividir_barras(bm, P["fck"], boa=BOA_I)
            A = VI.area_I(B, H, ts, ti, P["m"], bw)
            Vm = A * Lm / 1000 + (B * H / 1e6 - A) * P["x_mac"] / 1000 * 2 - 2 * B * (H - HD) * LN / 1e9
            marcas.append(dict(traspasse=TRm, marca=mk, qtd=8, L=Lm, barras=bm, V=Vm, area=_area_I(pts, B, H, Lm), cord=(n_cord, n_cord * Lm / 1000)))
        fam, tit, forma = "VM", "VIGAS DO MEZANINO I90 PROTENDIDAS — VM-01, VM-02", "ND-LET-VM01"
    longas = [("N3", cob)] + ([("N4", cob)] if P.get("pele") else []) + [("N12", LN + cob)] + ([("N10", 100)] if SEG else [])
    return dict(fam=fam, titulo=tit, forma=forma, fck=P["fck"], L=L, H=H, esc=40 if L > 13000 else 20, rep=P["marca"],
                contorno=[cont], ents=ents, zonas=zs, cortes=[(L / 2, "S.1")], dets=[(LN, "D1")], longas=longas, blocos=[S1, D1] + blocos_extra, marcas=marcas,
                notas=[n for n in P["notas"][:3]] + [t for t in (nota_traspasse(*[m.get("traspasse") for m in marcas]),) if t] + ["N11/N13: estribos das mesas c/25 (N11 envolve as cordoalhas; N13 o N3). N12: 2 Ø12,5 nos cantos da mesa inferior (porta-estribos; Ø ≥ 12,5 nas longitudinais de viga).",
                                                     "No trecho dos dentes os estribos N2 são substituídos pelos N8 (dente) e N6 (suspensão)."])


def _area_I(pts, B, H, L):
    per = sum(math.dist(a, b) for a, b in zip(pts, pts[1:] + pts[:1])) / 1000
    return per * L / 1000 - B / 1000 * L / 1000 + 2 * B * H / 1e6


def spec_vb():
    """VB 15 × 60 com dente Gerber 30 × 27 (rev04, calc_vb_dente.py) — mesmas posições da fôrma ND-LET-VB01."""
    from geometria import X_EIXO
    MEIA = {"A": 0.30, "B": 0.20, "C": 0.20, "D": 0.20, "E": 0.30}
    XF = [(k, X_EIXO[k]) for k in "ABCDE"]
    B, H, HD, LN = 150, 600, 300, 270
    REC = H - HD
    XN, XS = [50, 200], [LN + 40, LN + 90]
    he, hn = round((H - 2 * COB) / 10), round((HD - 2 * COB) / 10)

    def barras_vb(L):
        Lb = round((L - 2 * COB) / 10)
        L1 = round((L - 2 * LN - 2 * COB) / 10)
        xs_e = list(range(LN + 150, 1500, 100)) + list(range(1500, L - 1500, 150)) + list(range(L - 1500, L - LN - 140, 100))
        return xs_e, [dict(pos="N1", diam=16.0, qtd=3, comp=L1 + 40, geo=dict(k="C", a=L1, g=20, dir=1)),
                      dict(pos="N2", diam=12.5, qtd=6, comp=Lb + 40, geo=dict(k="C", a=Lb, g=20, dir=-1)),   # rev11: longitudinal de viga ≥ Ø12,5
                      dict(pos="N3", diam=6.3, qtd=len(xs_e), comp=2 * (he + 9) + 12, geo=dict(k="E", a=9, b=he)),
                      dict(pos="N4", diam=6.3, qtd=4, comp=2 * (hn + 9) + 12, geo=dict(k="E", a=9, b=hn)),
                      dict(pos="N5", diam=10.0, qtd=2, comp=2 * 70 + 8, geo=dict(k="U", a=70, b=8)),
                      dict(pos="N6", diam=10.0, qtd=4, comp=2 * (he + 8) + 16, geo=dict(k="E", a=8, b=he)),
                      dict(pos="N7", diam=6.3, qtd=4, comp=2 * 55 + 8, geo=dict(k="U", a=55, b=8))]
    marcas = []
    for k, ((na, xa), (nb, xb)) in enumerate(zip(XF[:-1], XF[1:]), 1):
        x0 = round((xa + MEIA[na] + 0.025) * 1000)
        Lm = round((xb - MEIA[nb] - 0.025) * 1000) - x0
        _, bm = barras_vb(Lm)
        V = (B * H * Lm - 2 * B * REC * LN) / 1e9
        import renomear as _RNv                                         # rev12 (item 17): nome de cada peça por extenso (sem "V406/06")
        marcas.append(dict(marca=_RNv.N(", ".join(_RNv.nomes_de(f"VB-0{k}") + _RNv.nomes_de(f"VB-0{k + 4}"))), qtd=2, L=Lm, barras=bm, V=V, area=(2 * H + B) * Lm / 1e6 + 2 * B * H / 1e6, cord=None))
    L = marcas[1]["L"]
    xs_e, _ = barras_vb(L)
    import vb_geom as VG
    cont = VG.peca(L)                          # rev04: pontas/recortes a prumo e faces de apoio horizontais na montagem
    ents = [([(x, COB), (x, H - COB)], "ARM_TRANSV") for x in xs_e]
    for x0, sg in ((0, 1), (L, -1)):
        ents += [([(x0 + sg * x, REC + COB), (x0 + sg * x, H - COB)], "ARM_TRANSV") for x in XN]
        ents += [([(x0 + sg * x, COB), (x0 + sg * x, H - COB)], "ARMADURA") for x in XS]
        ents += [([(x0 + sg * COB, REC + COB + 20), (x0 + sg * (LN + 430), REC + COB + 20)], "ARMADURA")]
        ents += [([(x0 + sg * COB, REC + COB + 20 + k * 70), (x0 + sg * (LN + 300), REC + COB + 20 + k * 70)], "ARM_TRANSV") for k in (1, 2)]
    ents += [([(LN + COB, COB + 200), (LN + COB, COB + 10), (L - LN - COB, COB + 10), (L - LN - COB, COB + 200)], "ARMADURA"),
             ([(COB, H - COB - 200), (COB, H - COB - 10), (L - COB, H - COB - 10), (L - COB, H - COB - 200)], "ARMADURA")]
    xi = -B / 2 + COB + 6.3 + 8
    S1 = dict(nome="SEÇÃO S.1", sub="corrente", esc=10, contorno=[[(-B / 2, 0), (B / 2, 0), (B / 2, H), (-B / 2, H)]],
              ents=[([(-B / 2 + COB, COB), (B / 2 - COB, COB), (B / 2 - COB, H - COB), (-B / 2 + COB, H - COB)], "ARM_TRANSV", True)],
              discos=[(xi, COB + 14.3, 16), (-xi, COB + 14.3, 16), (xi, COB + 50.3, 16)] +
                     [(x, y, 10) for x in (-B / 2 + COB + 11.3, 0, B / 2 - COB - 11.3) for y in (H - COB - 11.3, H - COB - 41.3)],
              prot=[], bolhas=[("N1", (-xi, COB + 14.3), (10, -6)), ("N2", (B / 2 - COB - 11.3, H - COB - 11.3), (8, 4)), ("N3", (B / 2 - COB, 300), (8, 0))],
              formas=["N3", "N4", "N6", "N5", "N7"])
    return dict(fam="VB", titulo="VIGAS DE BORDA VB-01 A VB-08 (15 × 60 COM DENTE, CONCRETO ARMADO)", forma="ND-LET-VB01", fck=40, L=L, H=H, esc=20, rep=marcas[1]["marca"],
                contorno=[cont], ents=ents, zonas=zonas_txt(xs_e, "N3", 6.3), cortes=[(L / 2, "S.1")], dets=[],
                longas=[("N2", COB), ("N1", COB)], blocos=[S1], marcas=marcas,
                notas=["Concreto C40, aço CA-50. N1 com gancho de 20 cm junto ao recorte; N2 com dobra de 20 cm nas pontas; sucção do vento: N2 6 Ø10.",
                       "Dente Gerber 30 × 27 (NBR 9062:2017 7.4): N4 estribos do nariz, N5 alça-tirante, N6 suspensão, N7 costura. Apoio no CP-VB com NEO-6 e PN-6 Ø20 roscado com porca (ver ND-LET-VB01)."])


def armacao_vm(L, P, DA):
    """rev09 (DEC-049): VM RETANGULAR 30 × 75 (mm): N2 estribo fechado, N9 alças U saindo 20 cm na faixa de 2º estágio (lado da
    borda), N9A alças curtas no nariz, N3/N4/N5/N12 longitudinais, N11 estribos densos nos 100 cm das pontas e dente Gerber
    (NBR 9062:2017 7.4): N6 tirante em alças horizontais, N7 suspensão, N8 costura horizontal, N10 estribos verticais do nariz."""
    H, HD, LN, MAC = round(P["h_pm"] * 1000), round(P["dente"]["hd"] * 1000), round(P["dente"]["ln"] * 1000), round(P["dente"]["macico"] * 1000)
    B = round(P["b"] * 1000)
    B2 = B - 120                                       # faixa de 2º estágio (b − apoio 100 − folga 20)
    REC = H - HD
    ext = lambda a, b: round(2 * (a + b) + 16)
    xs_mac = [x for x in range(LN + 40, MAC, 100)] + [L - x for x in range(LN + 40, MAC, 100)]
    xs_e = [x for x in list(range(MAC, 1500, 100)) + list(range(1500, L - 1500, 150)) + list(range(L - 1500, L - MAC + 1, 100))]
    xs_9 = list(range(75, L - 60, 150))
    n9a = sum(1 for x in xs_9 if x < LN or x > L - LN)
    a9, b9 = (H - 35 + 200) / 10, (B2 - 50) / 10
    a9a = (HD - 35 + 200) / 10
    Ll = round((L - 2 * COB) / 10)
    L12 = round((L - 2 * LN - 2 * COB) / 10)
    nt, dt, anc = DA["n_tir"], DA["d_tir"], DA["ancoragem_tirante_mm"]
    ns, ds, nc, dc, nv = DA["n_sus"], DA["d_sus"], DA["n_cost"], DA["d_cost"], max(2, DA["n_v"])
    bh, bb = (H - 2 * COB) / 10, (B - 2 * COB) / 10
    barras = [dict(pos="N2", diam=8.0, qtd=len(xs_e), comp=ext(bb, bh), geo=dict(k="E", a=bb, b=bh)),
              dict(pos="N3", diam=12.5, qtd=2, comp=Ll, geo=dict(k="R", a=Ll)),
              dict(pos="N4", diam=12.5, qtd=2, comp=Ll, geo=dict(k="R", a=Ll)),               # rev11: longitudinal de viga ≥ Ø12,5 (era Ø10)
              dict(pos="N5", diam=12.5, qtd=2, comp=Ll, geo=dict(k="R", a=Ll)),
              dict(pos="N6", diam=dt, qtd=nt // 2 * 2 or 2, comp=round(2 * (LN + anc) / 10 + bb), geo=dict(k="U", a=round((LN + anc) / 10), b=bb)),
              dict(pos="N7", diam=ds, qtd=2 * ns, comp=ext(bb, bh), geo=dict(k="E", a=bb, b=bh)),
              dict(pos="N8", diam=dc, qtd=2 * nc, comp=ext(round((LN + 450) / 10), bb), geo=dict(k="E", a=round((LN + 450) / 10), b=bb)),
              dict(pos="N9", diam=10.0, qtd=len(xs_9) - n9a, comp=round(2 * a9 + b9), geo=dict(k="U", a=a9, b=b9)),
              dict(pos="N9A", diam=10.0, qtd=n9a, comp=round(2 * a9a + b9), geo=dict(k="U", a=a9a, b=b9)),
              dict(pos="N10", diam=10.0, qtd=2 * nv, comp=ext(bb, (HD - 2 * COB) / 10), geo=dict(k="E", a=bb, b=(HD - 2 * COB) / 10)),
              dict(pos="N11", diam=8.0, qtd=len(xs_mac), comp=ext(bb, bh), geo=dict(k="E", a=bb, b=bh)),
              dict(pos="N12", diam=12.5, qtd=2, comp=L12, geo=dict(k="R", a=L12))]   # rev11: ≥ Ø12,5 (era Ø10)
    for ex in P.get("extra_inf", []):                  # DEC-049: 4 Ø16 retas no fundo a partir do canto reentrante (cada ponta), MEF
        Lx = round(ex["L"] / 10)
        barras.append(dict(pos="N13", diam=ex["d"], qtd=2 * ex["n"], comp=Lx, geo=dict(k="R", a=Lx)))
    if P.get("extra_inf"):                             # fretagem da zona de transferência no canto inferior (ressalva do MEF): estribos
        hf = 250                                       # fechados Ø8 c/5 em 50 cm a partir do canto reentrante, envolvendo as 2 camadas de cordoalhas
        barras.append(dict(pos="N14", diam=8.0, qtd=2 * 10, comp=ext(bb, (hf - COB) / 10), geo=dict(k="E", a=bb, b=(hf - COB) / 10)))
    for b in barras:
        b["comp"] = round(b["comp"])
    return xs_e, xs_mac, xs_9, barras


def spec_vm():
    """VM retangular protendida 30 × 75 rev09 (DEC-049), dente Gerber 45 × 40 nas pontas; marcas VM-01 a VM-04."""
    AQ_ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
    VMJ = json.load(open(AQ_ + "vm_retangular.json"))
    P = VMJ["premissas"]
    H, HD, LN, MAC = round(P["h_pm"] * 1000), round(P["dente"]["hd"] * 1000), round(P["dente"]["ln"] * 1000), round(P["dente"]["macico"] * 1000)
    B = round(P["b"] * 1000)
    B2 = B - 120
    REC = H - HD
    MV = json.load(open(AQ_ + f"mef_vm_ret_dente_{H}_{HD}.json"))
    DA = MV["calculo"]["adotado"]
    QT = {"VM-01": 6, "VM-02": 8, "VM-03": 2, "VM-04": 2}
    marcas = []
    for mk in ("VM-01", "VM-02", "VM-03", "VM-04"):
        Lm = round(VMJ[mk]["L_peca"] * 1000)
        _, _, _, bm = armacao_vm(Lm, P, DA)
        V = VMJ[mk]["V_m3"]
        nc = len(VMJ[mk]["pos_cordoalhas_mm"])
        marcas.append(dict(marca=mk, qtd=QT[mk], L=Lm, barras=bm, V=V, area=(2 * H + B) * Lm / 1e6, cord=(nc, nc * Lm / 1000)))
    L = marcas[1]["L"]
    xs_e, xs_mac, xs_9, barras = armacao_vm(L, P, DA)
    cont = [(0, REC), (LN, REC), (LN, 0), (L - LN, 0), (L - LN, REC), (L, REC), (L, H), (0, H)]
    ents = [([(x, COB), (x, H - COB)], "ARM_TRANSV") for x in xs_e + xs_mac]
    ents += [([(x, (REC if (x < LN or x > L - LN) else 0) + 35), (x, H + 200)], "ARM_TRANSV") for x in xs_9]
    ents += [([(COB, H - COB - 10), (L - COB, H - COB - 10)], "ARMADURA"), ([(LN + COB, 85), (L - LN - COB, 85)], "ARMADURA"),
             ([(COB, H / 2), (L - COB, H / 2)], "ARMADURA")]
    for y in sorted({c[1] for c in VMJ["VM-02"]["pos_cordoalhas_mm"]}):
        ents.append(([(LN if y < REC else 0, y), (L - LN if y < REC else L, y)], "ARM_PROT"))
    for x0_, sg in ((0, 1), (L, -1)):
        for ex in P.get("extra_inf", []):
            ents.append(([(x0_ + sg * (LN + COB), ex["y"]), (x0_ + sg * (LN + COB + ex["L"]), ex["y"])], "ARMADURA"))
        if P.get("extra_inf"):
            for k in range(10):
                xx = x0_ + sg * (LN + 30 + k * 50)
                ents.append(([(xx, COB), (xx, 250)], "ARM_TRANSV"))
        ents.append(([(x0_ + sg * COB, REC + 55), (x0_ + sg * (LN + DA["ancoragem_tirante_mm"]), REC + 55)], "ARMADURA"))
        for k in range(DA["n_sus"]):
            xx = x0_ + sg * (LN + 40 + k * 50)
            ents.append(([(xx, COB), (xx, H - COB)], "ARM_TRANSV"))
    zs = [(xs_mac[0], max(x for x in xs_mac if x < L / 2), f"{sum(1 for x in xs_mac if x < L / 2)} N11")] + zonas_txt(xs_e, "N2", 8.0) + \
         [(min(x for x in xs_mac if x > L / 2), xs_mac[-1], f"{sum(1 for x in xs_mac if x > L / 2)} N11")]
    sec = [(0, 0), (B, 0), (B, H), (0, H)]
    prot = [tuple(c) for c in VMJ["VM-02"]["pos_cordoalhas_mm"]]
    S1 = dict(nome="SEÇÃO S.1", sub="corrente (retangular 30 × 75); alças N9 para o 2º estágio", esc=10, contorno=[sec],
              ents=[([(COB, COB), (B - COB, COB), (B - COB, H - COB), (COB, H - COB)], "ARM_TRANSV", True),
                    ([(COB + 10, H + 200), (COB + 10, 35), (B2 - 15, 35), (B2 - 15, H + 200)], "ARM_TRANSV", False)],
              discos=[(x, H - COB - 10, 12.5) for x in (40, B - 40)] + [(x, H / 2, 10) for x in (35, B - 35)] + [(x, 85, 10) for x in (75, B - 75)],
              prot=prot, bolhas=[("N2", (B - COB, H / 2 - 80), (10, -4)), ("N9", (B2 - 15, H + 150), (10, 4)),
                                 ("N3", (40, H - COB - 10), (-10, 4)), ("N5", (35, H / 2), (-10, 0)), ("N12", (75, 85), (-14, -4))],
              formas=["N2", "N9"], prot_txt=f"{len(prot)} cord. Ø12,7")
    S2 = dict(nome="SEÇÃO S.2", sub="nariz do dente (acima do recorte)", esc=10, contorno=[[(0, REC), (B, REC), (B, H), (0, H)]],
              ents=[([(COB, REC + COB), (B - COB, REC + COB), (B - COB, H - COB), (COB, H - COB)], "ARM_TRANSV", True)],
              discos=[(x, REC + 55, DA["d_tir"]) for x in (45, B - 45)] + [(x, H - COB - 10, 12.5) for x in (40, B - 40)], prot=[tuple(c) for c in prot if c[1] > REC],
              bolhas=[("N10", (B - COB, REC + HD / 2), (10, 0)), ("N6", (B - 45, REC + 55), (10, -6)), ("N9A", (30, H + 120), (-12, 6))], formas=["N10", "N9A"])
    _a9 = next(b_["geo"]["a"] for b_ in barras if b_["pos"] == "N9A") * 10
    S2["ents"].append(([(COB + 10, H + 200), (COB + 10, H + 200 - _a9), (B2 - 15, H + 200 - _a9), (B2 - 15, H + 200)], "ARM_TRANSV", False))
    det = [([(0, REC), (LN, REC), (LN, 0), (1600, 0)], "VISTA", False), ([(1600, H), (0, H), (0, REC)], "VISTA", False),
           ([(COB, REC + 55), (min(LN + DA["ancoragem_tirante_mm"], 1600), REC + 55)], "ARMADURA", False)]
    det += [([(LN + 40 + k * 50, COB), (LN + 40 + k * 50, H - COB)], "ARM_TRANSV", False) for k in range(DA["n_sus"])]
    det += [([(COB, REC + 120 + k * (HD - 160) / max(DA["n_cost"] - 1, 1)), (LN + 450, REC + 120 + k * (HD - 160) / max(DA["n_cost"] - 1, 1))], "ARM_TRANSV", False) for k in range(DA["n_cost"])]
    det += [([(60 + k * (LN - 120) / max(DA["n_v"] - 1, 1), REC + COB), (60 + k * (LN - 120) / max(DA["n_v"] - 1, 1), H - COB)], "ARM_TRANSV", False) for k in range(max(2, DA["n_v"]))]
    det += [([(LN if y < REC else 0, y), (1600, y)], "ARM_PROT", False) for y in sorted({c[1] for c in prot})]
    for ex in P.get("extra_inf", []):
        det.append(([(LN + COB, ex["y"]), (1600, ex["y"])], "ARMADURA", False))
    if P.get("extra_inf"):
        det += [([(LN + 30 + k * 50, COB), (LN + 30 + k * 50, 250)], "ARM_TRANSV", False) for k in range(10)]
    D1 = dict(nome="DETALHE D1 — DENTE GERBER", sub=f"dente {HD/10:g} × {LN/10:g}, recorte {REC/10:g}; as duas pontas iguais", esc=10, contorno=[], ents=det, discos=[], prot=[],
              cotas=[((0, REC), (LN, 0), 0, -100, f"{fd(LN/10)}"), ((0, REC), (0, H), 90, -120, f"{fd((H-REC)/10)}"), ((LN, 0), (LN, REC), 90, -60, f"{fd(REC/10)} (recorte)"), ((1600, 0), (1600, H), 90, 120, f"{fd(H/10)}")],
              bolhas=[("N6", (LN + 300, REC + 55), (4, -8)), ("N7", (LN + 40, H / 2), (10, -10)), ("N8", (LN + 300, REC + 120), (8, 8)), ("N10", (60, H - 80), (-16, 20))]
              + ([("N13", (1300, P["extra_inf"][0]["y"]), (6, -8)), ("N14", (LN + 280, 200), (8, -14))] if P.get("extra_inf") else []),
              formas=["N6", "N7", "N8"] + (["N14"] if P.get("extra_inf") else []), corte_x=1600)
    return dict(fam="VM", titulo=f"VIGAS DO MEZANINO VM-01 A VM-04 (RETANGULAR {B/10:g} × {H/10:g} PROTENDIDA, DENTE GERBER)", forma="ND-LET-VM01", fck=40, L=L, H=H, esc=25, rep="VM-02",
                contorno=[cont], ents=ents, zonas=zs, cortes=[(L / 2 - 700, "S.1"), (200, "S.2")], dets=[(LN / 2, "D1")],
                longas=[("N3", COB), ("N4", COB), ("N5", COB), ("N12", LN + COB)], blocos=[S1, S2, D1], marcas=marcas,
                notas=["Concreto C40, aço CA-50; liberar a protensão com fcj ≥ 32 MPa. Cobrimento 2,5 cm (estribos) e 3,0 cm (cordoalhas) — pré-moldado, CAA II.",
                       f"N9 / N9A: alças saindo 20 cm acima da peça em toda a viga, na faixa de 2º estágio de {B2/10:g} cm do lado da borda (o lado da laje fica livre para o apoio de 10 cm); não cortar nem dobrar na fábrica.",
                       f"Dente Gerber {HD/10:g} × {LN/10:g} (NBR 9062:2017 7.4, verificado por MEF não linear): N6 tirante em alças horizontais, N7 suspensão concentrada junto ao recorte (fyd ≤ 435 MPa), N8 costura, N10 estribos do nariz; N11 nos 100 cm das pontas.",
                       "N13 (4 Ø16 retas no fundo, 250 cm a partir do canto reentrante, nas duas pontas) e N14 (fretagem: estribos fechados Ø8 c/5 nos 50 cm a partir do canto reentrante, envolvendo as cordoalhas inferiores): zona de transferência no canto do dente, onde o MEF mostrou compressão acima de 3,5‰ a ~290 kN (DEC-049; memória de cálculo do dente).",
                       "Negativa de continuidade (N11 6 Ø16 pelas bainhas do pilar e N12 9 Ø12,5 na capa) é armadura de OBRA, não entra nesta lista (ND-LET-VM01).",
                       "VM-01, VM-03 e VM-04: mesma seção, mesmo dente e mesmas posições; muda o comprimento e o número de cordoalhas (tabela de ferros por marca)."])


def spec_vt():
    import fechamento as F
    agr = {}
    for i in range(1, 8):
        agr.setdefault(round(F.Y_LIN[i + 1] - F.Y_LIN[i] - 0.40, 3), []).append(f"L{i+1}–L{i+2}")
    lista = sorted(agr.items(), key=lambda t: -t[0])
    B, H, HDv, LNv = 250, 600, 300, 200

    def geo_vt(bs):
        out = []
        for b in bs:
            b = dict(b)
            fm = b["forma"]
            if b["pos"] in ("N1", "N2", "N3"):
                b["geo"] = dict(k="R", a=b["comp"])
            elif b["pos"] == "N5":
                b["geo"] = dict(k="L", a=fm[2][0], g=fm[0][1])
            else:
                b["geo"] = dict(k="E", a=fm[2][0], b=fm[2][1])
            out.append(b)
        return out
    marcas = []
    for k, (Lm_, pos) in enumerate(lista):
        Lm = round(Lm_ * 1000)
        V = (B * H * Lm - 2 * B * HDv * LNv) / 1e9
        marcas.append(dict(marca=f"VT-{k+1:02d}", qtd=2 * len(pos), L=Lm, barras=geo_vt(F.vt_barras(Lm / 10)), V=V,
                           area=(2 * H + B) * Lm / 1e6 + 2 * B * H / 1e6, cord=None))
    L = marcas[0]["L"]
    n4 = marcas[0]["barras"][3]["qtd"]
    xs4 = [230 + 150 * k for k in range(n4)]
    cont = [(0, H - HDv), (LNv, H - HDv), (LNv, 0), (L - LNv, 0), (L - LNv, H - HDv), (L, H - HDv), (L, H), (0, H)]
    ents = [([(x, COB), (x, H - COB)], "ARM_TRANSV") for x in xs4]
    ents += [([(230, 45), (L - 230, 45)], "ARMADURA"), ([(30, 555), (L - 30, 555)], "ARMADURA")] + [([(230, y), (L - 230, y)], "ARMADURA") for y in (220, 380)]
    for x0_, sg in ((0, 1), (L, -1)):
        ents.append(([(x0_ + sg * 35, 360), (x0_ + sg * 35, 330), (x0_ + sg * 675, 330)], "ARMADURA"))
        ents += [([(x0_ + sg * x, COB), (x0_ + sg * x, H - COB)], "ARM_TRANSV") for x in (235, 315)]
        ents += [([(x0_ + sg * x, H - HDv + COB), (x0_ + sg * x, H - COB)], "ARM_TRANSV") for x in (60, 110, 160)]
    S1 = dict(nome="SEÇÃO S.1", sub="corrente", esc=10, contorno=[[(0, 0), (B, 0), (B, H), (0, H)]],
              ents=[([(30, 30), (220, 30), (220, 570), (30, 570)], "ARM_TRANSV", True)],
              discos=[(x, y, 12.5) for x in (45, 125, 205) for y in (45, 555)] + [(x, y, 8) for x in (40, 210) for y in (220, 380)], prot=[],
              bolhas=[("N1", (205, 45), (8, -4)), ("N2", (205, 555), (8, 4)), ("N3", (40, 380), (-8, 0)), ("N4", (220, 300), (8, 0))], formas=["N4"])
    LD = 1000
    det = [([(0, H - HDv), (LNv, H - HDv), (LNv, 0), (LD, 0)], "VISTA", False), ([(LD, H), (0, H), (0, H - HDv)], "VISTA", False),
           ([(35, 360), (35, 330), (675, 330)], "ARMADURA", False)]
    det += [([(x, COB), (x, H - COB)], "ARM_TRANSV", False) for x in (235, 315)]
    det += [([(x, H - HDv + COB), (x, H - COB)], "ARM_TRANSV", False) for x in (60, 110, 160)]
    det += [([(x, COB), (x, H - COB)], "ARM_TRANSV", False) for x in (380, 530, 680, 830)]
    D1 = dict(nome="DETALHE D1 — DENTE GERBER", sub="dente 30 × 20; as duas pontas iguais", esc=10, contorno=[], ents=det, discos=[], prot=[],
              cotas=[((0, H - HDv), (LNv, 0), 0, -100, f"{fd(LNv/10)}"), ((0, H - HDv), (0, H), 90, -120, f"{fd(HDv/10)}"), ((LNv, 0), (LNv, H - HDv), 90, -60, f"{fd((H-HDv)/10)} (recorte)"), ((LD, 0), (LD, H), 90, 120, f"{fd(H/10)}")],
              bolhas=[("N5", (500, 330), (4, 8)), ("N6", (315, 150), (10, -6)), ("N7", (110, H - 60), (-4, 8)), ("N4", (680, 450), (8, 6))],
              formas=["N5", "N6", "N7"], corte_x=LD)
    return dict(fam="VT", titulo="VIGAS DE TRAVAMENTO VT-01 A VT-04 (25 × 60, CONCRETO ARMADO)", forma="ND-LET-VT01", fck=40, L=L, H=H, esc=20, rep="VT-01",
                contorno=[cont], ents=ents, zonas=zonas_txt(xs4, "N4", 6.3), cortes=[(L / 2, "S.1")], dets=[(LNv, "D1")],
                longas=[("N2", 30), ("N1", 230), ("N3", 230)], blocos=[S1, D1], marcas=marcas,
                notas=["Concreto C40, aço CA-50. N1 e N3 só no corpo (entre os dentes); N2 de ponta a ponta.",
                       "Dentes Gerber 30 × 20 nos consolos CP-VT: N5 tirante 2 Ø12,5 por ponta, N6 suspensão 2 estribos Ø8, N7 3 estribos Ø6,3 no dente (NBR 9062:2017 7.4)."])


SPECS = [("TS-01", spec_ts01), ("I120", lambda: spec_i("i110")), ("VM", spec_vm), ("VB", spec_vb)]          # rev04: sem VT


# ================================================================== desenho
def bloco(A: Arm, b, bar, x, ytop):
    """seção/detalhe com bolhas e barras explodidas à direita. Retorna (largura, altura) usadas."""
    esc = b["esc"]
    escf = b.get("esc_f", 20)
    allp = [p for c in b["contorno"] for p in c] + [p for e in b["ents"] for p in e[0]]
    xmin, xmax = min(p[0] for p in allp), max(p[0] for p in allp)
    ymin, ymax = min(p[1] for p in allp), max(p[1] for p in allp)
    ox, oy = x + 14 - xmin / esc, ytop - 10 - ymax / esc
    T = lambda p: (ox + p[0] / esc, oy + p[1] / esc)
    for c in b["contorno"]:
        A.pl([T(p) for p in c], "CORTADO", True)
    for pts, lay, *fch in b["ents"]:
        A.pl([T(p) for p in pts], lay, bool(fch and fch[0]))
    for (xx, yy, d) in b["discos"]:
        A.disco(T((xx, yy)), max(d / 2 / esc, 0.5))
    for (xx, yy) in b["prot"]:
        c = T((xx, yy))
        A.circ(c, max(12.7 / 2 / esc, 0.5), "ARM_PROT_SECAO")
    if b.get("corte_x"):
        cx = b["corte_x"]
        A.ln(T((cx, ymin - 60)), T((cx, ymax + 60)), "CARIMBO_FINO")
    for p1, p2, ang, dist, txt in b.get("cotas", []):       # rev10: cotas do detalhe (texto em cm; dist em mm da peça)
        q1, q2 = T(p1), T(p2)
        base = (q1[0], max(q1[1], q2[1]) + dist / esc) if ang == 0 else (min(q1[0], q2[0]) + dist / esc, q1[1])
        if dist < 0 and ang == 0:
            base = (q1[0], min(q1[1], q2[1]) + dist / esc)
        d = A.pr.msp.add_linear_dim(base=base, p1=q1, p2=q2, angle=ang, text=txt, dimstyle="ND", dxfattribs={"layer": "COTA"})
        d.render()
    for pos, alvo, (dx, dy) in b["bolhas"]:
        p = T(alvo)
        A.bolha_lider(p, p[0] + dx, p[1] + dy, pos, registrar=pos in bar)   # barra emendada: as posições dos trechos vêm da elevação
    x_dir = T((xmax, 0))[0] + 14
    yb = oy + ymin / esc - max([-c[3] / esc + 6 for c in b.get("cotas", []) if c[2] == 0 and c[3] < 0] or [0])
    # barras explodidas em coluna à direita (1:20)
    y = ytop - 6
    xr_max = x_dir
    for pos in [p for p in b["formas"] if p in bar]:
        g = bar[pos]["geo"]
        hgt = (g.get("b", 0) + (g.get("g", 0) if g["k"] in ("U", "L") else 0)) * 10 / escf
        bb = A.forma(x_dir, y - hgt - (0 if g["k"] != "U" or not g.get("g") else g["g"] * 10 / escf), bar[pos], escf)
        y = bb[1] - 5
        xr_max = max(xr_max, bb[2])
    ybot = min(yb, y + 5) - 6
    A.titulo(x + 4, ybot, b["nome"], f"{b['sub']}" + (f" · {b['prot_txt']} (círculos vazados)" if b.get("prot_txt") else "") + f" · esc. 1:{esc:g} (barras 1:{escf:g})")
    return xr_max - x + 6, ytop - (ybot - 8)


def folha(num, total, S):
    pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                            conteudo=f"ARMADURAS — PRÉ-MOLDADOS — {S['titulo']} — SEÇÕES E LISTA DO AÇO",
                            desenho=f"ND-LET-AR-VIG-{num:02d}", folha=f"{num:02d}/{total:02d}", fase="PARA APROVAÇÃO"))
    pr.revisao("00", "13/10/2026", "EMISSÃO INICIAL — PADRÃO DE ARMADURAS")
    pr.revisao("04", "16/10/2026", "NBR 9062: SEM VT; VM EM MEIO VASO COM DENTE")
    pr.revisao("06", "19/10/2026", "DEC-032: I120 28 + 2 CORD., N5 EM ALÇAS HORIZONTAIS, BARRAS DOS DENTES NAS 2 PONTAS; DENTE DA VM PELO MEF COM A ARMAÇÃO DA PRANCHA; TS-01 N9")
    A = Arm(pr)
    Q = pr.quadro
    rep = next(m for m in S["marcas"] if m["marca"] == S.get("rep", S["marcas"][0]["marca"]))
    bar = {b["pos"]: b for b in rep["barras"]}
    L, H, esc = S["L"], S["H"], S["esc"]
    x0 = Q[0] + 30
    ncol = len(S["marcas"])
    XT = Q[0] + 970 - 98 * max(ncol, 2)
    # ------------------------------------------------ elevação
    yt = Q[3] - 30
    A.titulo(x0, yt, f"ELEVAÇÃO DE ARMAÇÃO — {rep['marca']} (L = {fd(rep['L']/10)} cm)",
             f"esc. 1:{esc:g} · demais marcas: mesma armação, comprimentos e quantidades na tabela de cada marca · fôrma e insertos: {S['forma']}")
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
    # cadeia de zonas
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
    for p in ("N1", "N2", "N4") :
        pass
    pr.posicoes_desenho.update({z[2].split()[1] for z in zs})
    # barras longitudinais explodidas
    y = yc - 14
    for pos, xs0 in S["longas"]:
        b = bar[pos]
        g = b["geo"]
        up = g["k"] == "C" and g.get("dir", 1) > 0
        if up:
            y -= g["g"] * 10 / esc
        bb = A.forma(E((xs0, 0))[0], y, b, esc, rotulo=False)
        A.tx(E((xs0, 0))[0], max(bb[3], y + 2.6) + 0.6, Arm.rotulo(b), "min", "BOTTOM_LEFT")
        A.bolha(E((xs0, 0))[0] - 6, y, pos)
        y = min(bb[1], y) - 12
    # ------------------------------------------------ seções e detalhes (fluxo)
    xb, yb_top, hrow = x0 - 10, y - 2, 0
    for blk in S["blocos"]:
        allp = [p for c in blk["contorno"] for p in c] + [p for e in blk["ents"] for p in e[0]]
        w_est = (max(p[0] for p in allp) - min(p[0] for p in allp)) / blk["esc"] + 30 + max(
            bar[p]["geo"]["a"] * 10 / blk.get("esc_f", 20) + 4 for p in blk["formas"]) + 20
        if xb + w_est > XT - 6 and xb > x0:
            xb, yb_top, hrow = x0 - 10, yb_top - hrow - 6, 0
        w, h = bloco(A, blk, bar, xb, yb_top)
        xb += w + 8
        hrow = max(hrow, h)
    # ------------------------------------------------ tabelas por marca
    for k, m in enumerate(S["marcas"]):
        xt = XT + 98 * k
        yy = Q[3] - 8
        cordm = [(f"CORD. CP-190 {m.get('ctxt', 'Ø12,7')}", m["cord"][1], m["cord"][1] * m.get("kgc", KG_CORD))] if m.get("cord") else None
        A.tx(xt, yy - 4, f"{m['marca']} — L = {fd(m['L']/10)} cm — {m['qtd']} {'UNIDADE' if m['qtd'] == 1 else 'UNIDADES'}", "sub", lay="TITULO")
        yy = A.tabela_ferros(xt, yy - 8, m["barras"], 1)
        yy, kg = A.resumo(xt, yy - 3, m["barras"], 1, fck=S["fck"], vol=m["V"], area=m["area"], cordoalhas=cordm)
        m["kg"] = kg
        if m["qtd"] > 1:
            cordn = [(f"CORD. CP-190 {m.get('ctxt', 'Ø12,7')}", m["cord"][1] * m["qtd"], m["cord"][1] * m["qtd"] * m.get("kgc", KG_CORD))] if m.get("cord") else None
            yy = A.tabela_ferros(xt, yy - 6, m["barras"], m["qtd"])
            yy, _ = A.resumo(xt, yy - 3, m["barras"], m["qtd"], fck=S["fck"], vol=m["V"], area=m["area"], cordoalhas=cordn)
    # ------------------------------------------------ coluna direita
    xr = Q[0] + 976
    A.ln((xr - 6, Q[1]), (xr - 6, Q[3]), "CARIMBO")
    lin = [[m["marca"], m["qtd"], fd(round(m["L"] / 10, 1)), f1(m["V"] * m["qtd"]), f1(m["kg"] * m["qtd"], 1),
            f1(m["cord"][1] * m["qtd"] * m.get("kgc", KG_CORD), 1) if m.get("cord") else "—"] for m in S["marcas"]]
    lin.append(["TOTAL", sum(m["qtd"] for m in S["marcas"]), "", f1(sum(m["V"] * m["qtd"] for m in S["marcas"])), f1(sum(m["kg"] * m["qtd"] for m in S["marcas"]), 1),
                f1(sum(m["cord"][1] * m["qtd"] * m.get("kgc", KG_CORD) for m in S["marcas"] if m.get("cord")), 1) if any(m.get("cord") for m in S["marcas"]) else "—"])
    y = pr.tabela(xr, Q[3] - 6, "RESUMO DA FOLHA (+10%)", ["MARCA", "QT", "L (cm)", "CONC. m³", "CA-50 kg", "CORD. kg"], lin, [24, 12, 30, 34, 34, 34], h_lin=5.0, destaque_ultima=True)
    pr.notas(xr, y - 6, S["notas"] + [
        "Todas as dimensões em centímetro, exceto onde indicado; níveis em metro. Cobrimento 3,0 cm (CAA II).",
        "Aço CA-50 (NBR 7480). C= comprimento de corte com dobras; RESUMO com +10% de perdas (cordoalhas sem perdas).",
        "Dobramento NBR 6118:2023 tab. 9.1; estribos com ganchos 135° e ponta de 10Ø (mín. 7 cm). Barras longitudinais sem emenda.",
        f"Fôrma, insertos, alças e chaparia: {S['forma']}.",
        "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."], 168)
    avisos = pr.salvar(f"/home/claude/letsara/pranchas/ND-LET-AR-VIG-{num:02d}")
    err = [a for a in avisos if a[0] == "ERRO"]
    sob = [a for a in avisos if "sobrep" in a[1] or "cruza" in a[1]]
    print(f"ND-LET-AR-VIG-{num:02d} ({S['fam']})", len(err), "erros,", len(sob), "sobreposições/cruzamentos,", len(avisos), "avisos")
    for a in err + sob:
        print("  ", a)
    return S


if __name__ == "__main__":
    alvo = [int(a) for a in sys.argv[1:]] or range(1, len(SPECS) + 1)
    for n in alvo:
        folha(n, len(SPECS), SPECS[n - 1][1]())
