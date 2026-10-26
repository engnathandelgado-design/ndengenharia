"""ND-LET-AR-PIL-xx — ARMADURAS DOS PILARES no padrão de entrega de pré-moldados (ref. PCH Três Capões, SP302):
4 pilares por folha A0 (1:50), barras longitudinais explodidas ao lado do pilar em pé, zonas de estribos cotadas,
seções S.1/S.2 (1:25) com os estribos desenhados ao lado, detalhe dos consolos com as barras explodidas,
TABELA DE FERROS 1 UNIDADE / N UNIDADES, RESUMO DO AÇO +10%, Fck, volume de concreto e área de fôrma.
Dados: arm/<MARCA>.json exportados por pilar_generico.prancha_pilar (mesma fonte das pranchas de fôrma)."""
import json, math, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha, _wtext, ALTURAS
from arm_nd import Arm, zonas, fd, f1

ORDEM = ["PL-01", "PL-02", "PL-03", "PL-04", "PL-05", "PL-06", "PL-07", "PL-08", "PL-09", "PL-10", "PL-11", "PL-12",
         "PF-01", "PF-02", "PF-03", "PF-04", "PF-05", "PF-06", "PC-01", "PC-02", "PC-03", "PM-01", "PM-02", "PG-01", "PG-02"]
FORMA = {}
E50, E25 = 50.0, 25.0
QW, QH = 485.0, 410.0


def quadrante(A: Arm, P, qx, qy, ref=None, esc=None, qh=None):
    ESC_E = esc or E50
    QH_ = qh or QH
    pr = A.pr
    B, H, L, LC, COB = P["B"], P["H"], P["L_TOT"], P["L_CAL"], P["COB"]
    REC, zr = P["rec"], P["z_rec"]
    d = (REC or {}).get("d", {}) if REC else {}
    rd = lambda fc: d.get(fc, 0)
    w0, w1 = -H / 2 + rd("C"), H / 2 - rd("A")
    u0, u1 = -B / 2 + rd("D"), B / 2 - rd("B")
    bar = {b["pos"]: b for b in P["barras"]}
    xe, y0 = qx + 82, qy + 34
    Pp = lambda w, z: (xe + w / ESC_E, y0 + z / ESC_E)

    # ------------------------------------------------ elevação (vista pela face D: A à direita, C à esquerda)
    A.pl([Pp(-H / 2, 0), Pp(H / 2, 0), Pp(H / 2, zr), Pp(w1, zr), Pp(w1, L), Pp(w0, L), Pp(w0, zr), Pp(-H / 2, zr)], "VISTA", True)
    A.ln(Pp(-H / 2 - 150, LC), Pp(-H / 2, LC), "EIXO")
    proj_A = max([c["proj"] for c in P["cons"] if c["face"] == "A"] + [0])
    for c in P["cons"]:
        z, pj, h, hp, lg, inc = c["z"], c["proj"], c["h"], c["hp"], c["larg"], c["incl"]
        if c["face"] in "AC":
            s = 1 if c["face"] == "A" else -1
            x0 = s * H / 2
            A.pl([Pp(x0, z - h), Pp(x0 + s * pj, z - hp), Pp(x0 + s * pj, z + pj * inc), Pp(x0, z)], "VISTA")
        else:
            A.pl([Pp(-lg / 2, z - h), Pp(lg / 2, z - h), Pp(lg / 2, z), Pp(-lg / 2, z)], "VISTA" if c["face"] == "D" else "OCULTA", True)
    # barras longitudinais na elevação
    ws_sobe = sorted({p[1] for p in P["xy_sobe"]})
    ws_para = sorted({p[1] for p in P["xy_para"]})
    if ws_sobe:
        A.ln(Pp(ws_sobe[0], 40), Pp(ws_sobe[0], L - 40))
        if not REC:
            A.ln(Pp(ws_sobe[-1], 40), Pp(ws_sobe[-1], L - 40))
    if ws_para:
        wp = ws_para[-1]
        A.pl([Pp(wp, 40), Pp(wp, zr - 40), Pp(wp - 150, zr - 40)])
    if P["xy_cab"]:
        wc = max(p[1] for p in P["xy_cab"])
        A.ln(Pp(wc, zr - P.get("emb13", 600)), Pp(wc, L - 40))
    for z in P["z_est"]:
        A.ln(Pp(-H / 2 + COB, z), Pp(H / 2 - COB, z), "ARM_TRANSV")
    for z in P["z_cab"]:
        A.ln(Pp(w0 + COB, z), Pp(w1 - COB, z), "ARM_TRANSV")
    # cadeia das zonas de estribos (à direita, depois dos consolos da face A)
    xch = xe + H / 2 / ESC_E + max(proj_A / ESC_E + 7, 19)
    n2 = bar["N2"]
    zs = zonas(P["z_est"])
    segs = []
    for z0_, z1_, n, s in zs:
        segs.append((z0_, z1_, f"{n} N2 Ø{fd(n2['diam'])} C/{fd(s/10)}" + (" + N3" if "N3" in bar else "") + (" + N3A" if "N3A" in bar else "")))
    if P["z_cab"]:
        for z0_, z1_, n, s in zonas(P["z_cab"]):
            segs.append((z0_, z1_, f"{n} N14 Ø{fd(bar['N14']['diam'])} C/{fd(s/10)}"))
    ys = [y0 + segs[0][0] / ESC_E] + [y0 + ((a[1] + b[0]) / 2) / ESC_E for a, b in zip(segs[:-1], segs[1:])] + [y0 + segs[-1][1] / ESC_E]
    A.ln((xch, ys[0]), (xch, ys[-1]), "COTA")
    for y in ys:
        A.ln((xch - 1.2, y - 1.2), (xch + 1.2, y + 1.2), "COTA"); A.ln((xch - 2, y), (xch + 2, y), "COTA")
    for (ya, yb), (_, _, t) in zip(zip(ys[:-1], ys[1:]), segs):
        if yb - ya > _wtext(t, ALTURAS["min"]) + 3:
            A.tx(xch + 1.0, (ya + yb) / 2, t, "min", "TOP_CENTER", rot=90)
        else:                                                            # rev11: zona curta — texto em pé a partir do início da zona (não sai da coluna)
            A.tx(xch + 1.0, ya + 0.5, t, "min", "TOP_LEFT", rot=90)
    A.tx(Pp(-H / 2 - 150, 0)[0] - 1, y0 + LC / ESC_E, "±0,000", "min", "MIDDLE_RIGHT")
    pr.posicoes_desenho.update({"N2"} | ({"N3"} if "N3" in bar else set()) | ({"N3A"} if "N3A" in bar else set()) | ({"N14"} if P["z_cab"] else set()))
    # seções
    livres = [z for z in range(LC + 800, (zr if REC else L) - 600, 100) if all(not (c["z"] - c["h"] - 300 < z < c["z"] + 300) for c in P["cons"])]
    z_s1 = livres[len(livres) // 2] if livres else (LC + zr) / 2
    A.corte(Pp(-H / 2, 0)[0] - 1, Pp(H / 2, 0)[0] + 1, y0 + z_s1 / ESC_E, "S.1")
    if REC:
        A.corte(Pp(w0, 0)[0] - 1, Pp(w1, 0)[0] + 1, y0 + (zr + L) / 2 / ESC_E, "S.2")

    # ------------------------------------------------ barras longitudinais explodidas (esquerda)
    xb = qx + 14
    for pos in ("N1", "N1A", "N13"):
        if pos in bar:
            b = bar[pos]
            zb = 40 if pos != "N13" else zr - P.get("emb13", 600)
            g = dict(b["geo"])
            if g["k"] == "L":
                g["dir"] = 1
            A.barra_vertical(xb, y0 + zb / ESC_E, b | {"geo": g}, ESC_E)
            A.bolha(xb - (4 if g["k"] == "L" else 0), y0 + zb / ESC_E + g["a"] * 10 / ESC_E + 6 + (6 if g["k"] == "L" else 0), pos)   # rev11: acima do gancho
            xb += 17
    # ------------------------------------------------ título do quadrante
    mk = P["marca"]
    A.titulo(qx + 6, qy + 12, (f"ARMAÇÃO — {mk}" if ref else f"PILAR {mk}") + f" — {P['qtd']} {'UNIDADE' if P['qtd'] == 1 else 'UNIDADES'}",
             f"{P['posicao'].replace('POSIÇÃO: ', '')} · ESC. 1:{ESC_E:g} (seções e estribos 1:10, consolos 1:20) · fôrma e insertos: {ref or FORMA.get(mk, P['desenho'])}")
    A.escala_grafica(qx + 6, qy + 2.5, ESC_E)

    # ------------------------------------------------ coluna do meio: seções e consolos
    xm = qx + 150
    ytop = qy + QH_ - 10
    ES_ = 10.0                                                             # rev11: seções e estribos em 1:10 (≥ 2× a elevação 1:25)
    # S.1
    sx, sy = xm + 4, ytop - 8 - B / ES_
    R = lambda w, u, ox=sx, oy=sy: (ox + (w + H / 2) / ES_, oy + (u + B / 2) / ES_)
    A.pl([R(-H / 2, -B / 2), R(H / 2, -B / 2), R(H / 2, B / 2), R(-H / 2, B / 2)], "CORTADO", True)
    A.pl([R(-H / 2 + COB, -B / 2 + COB), R(H / 2 - COB, -B / 2 + COB), R(H / 2 - COB, B / 2 - COB), R(-H / 2 + COB, B / 2 - COB)], "ARM_TRANSV", True)
    for wg in P["grampos"]:
        A.ln(R(wg, -B / 2 + COB), R(wg, B / 2 - COB), "ARM_TRANSV")
    for ug in P.get("grampos_h", []):                                      # DEC-040: grampos N3A na direção A–C
        A.ln(R(-H / 2 + COB, ug), R(H / 2 - COB, ug), "ARM_TRANSV")
    for (u, w) in P["xy"]:
        A.disco(R(w, u), max(P["D1"] / 2 / ES_, 0.55))
    s1t = "SEÇÃO S.1"
    A.titulo(sx, sy - 9, s1t)
    xr = R(-H / 2, 0)[0]
    if P["xy_sobe"]:
        u, w = min(P["xy_sobe"], key=lambda p: (p[1], p[0]))
        A.bolha_lider(R(w, u), xr - 6, R(w, u)[1] + 4, "N1")
    if P["xy_para"]:
        u, w = max(P["xy_para"], key=lambda p: (p[1], p[0]))
        A.bolha_lider(R(w, u), R(H / 2, 0)[0] + 5, R(w, u)[1] + 5, "N1A")
    A.bolha_lider(R(-H / 2 + COB + 60, B / 2 - COB), R(-H / 2 + COB + 60, B / 2)[0] - 2, R(0, B / 2)[1] + 5, "N2")
    if "N3" in bar:
        A.bolha_lider(R(P["grampos"][-1], B / 2 - COB - 40), R(P["grampos"][-1], 0)[0] + 3, R(0, B / 2)[1] + 5, "N3")
    if "N3A" in bar:
        ug = P["grampos_h"][-1]
        A.bolha_lider(R(H / 2 - COB - 60, ug), R(H / 2, 0)[0] + 5, R(0, ug)[1] - 4, "N3A")
    xs = R(H / 2, 0)[0] + 16
    bb = A.forma(xs, sy + 2, n2 | {"geo": n2["geo"]}, ES_)
    if "N3" in bar:
        b3 = A.forma(bb[2] + 10, sy + 6, bar["N3"], ES_)
        bb = (bb[0], min(bb[1], b3[1]), max(bb[2], b3[2]), bb[3])
    if "N3A" in bar:
        b3 = A.forma(xs + 1.5, bb[1] - 6.5, bar["N3A"], ES_)
        bb = (bb[0], min(bb[1], b3[1]), max(bb[2], b3[2]), bb[3])
    yb_ = min(sy - 14, bb[1] - 4)
    # S.2 (cabeça)
    if REC:
        HB, HH = u1 - u0, w1 - w0
        sy2 = yb_ - 6 - B / ES_
        R2 = lambda w, u: (sx + (w + H / 2) / ES_, sy2 + (u + B / 2) / ES_)
        A.pl([R2(-H / 2, -B / 2), R2(H / 2, -B / 2), R2(H / 2, B / 2), R2(-H / 2, B / 2)], "OCULTA", True)
        A.pl([R2(w0, u0), R2(w1, u0), R2(w1, u1), R2(w0, u1)], "CORTADO", True)
        A.pl([R2(w0 + COB, u0 + COB), R2(w1 - COB, u0 + COB), R2(w1 - COB, u1 - COB), R2(w0 + COB, u1 - COB)], "ARM_TRANSV", True)
        for (u, w) in P["xy_sobe"]:
            A.disco(R2(w, u), max(P["D1"] / 2 / ES_, 0.55))
        for (u, w) in P["xy_cab"]:
            A.disco(R2(w, u), max(16 / 2 / ES_, 0.5))
        A.titulo(sx, sy2 - 9, "SEÇÃO S.2 (CABEÇA)")
        if P["xy_sobe"]:
            u, w = min(P["xy_sobe"], key=lambda p: (p[1], p[0]))
            A.bolha_lider(R2(w, u), R2(-H / 2, 0)[0] - 6, R2(w, u)[1] + 4, "N1")
        if P["xy_cab"]:
            u, w = max(P["xy_cab"], key=lambda p: (p[1], -p[0]))
            A.bolha_lider(R2(w, u), R2(H / 2, 0)[0] + 5, R2(w, u)[1] + 6, "N13")
        A.bolha_lider(R2(w1 - COB, (u0 + u1) / 2), R2(H / 2, 0)[0] + 5, R2(0, (u0 + u1) / 2)[1] - 4, "N14")
        bb2 = A.forma(R2(H / 2, 0)[0] + 16, sy2 + 2, bar["N14"], ES_)
        yb_ = min(sy2 - 14, bb2[1] - 4)
    # consolos (1:20)
    ED = 20.0
    for k, g in enumerate(P["arm_cons"], 1):
        pa, pb, pc = g["pos"]
        PW, pj, h, lg = g["PW"], g["proj"], g["h"], g["larg"]
        zt, zb = 150, -h - 250
        zc = yb_ - 10 - zt / ED                       # assento (papel)
        x0 = xm + 10 + PW / ED                        # face do pilar
        D = lambda w, z: (x0 + w / ED, zc + z / ED)
        A.ln(D(-PW, zb), D(-PW, zt), "VISTA"); A.ln(D(0, zb), D(0, -h), "VISTA"); A.ln(D(0, 0), D(0, zt), "VISTA")
        A.pl([D(0, -h), D(pj, -h), D(pj, pj * g["incl"]), D(0, 0)], "VISTA")
        for zz in (zb, zt):
            A.ln(D(-PW - 40, zz), D(40, zz), "CARIMBO_FINO")
        A.ln(D(-PW + COB + 18, zb), D(-PW + COB + 18, zt), "ARMADURA"); A.ln(D(-COB - 18, zb), D(-COB - 18, zt), "ARMADURA")
        A.pl([D(-PW + COB + 8, -55 - 150), D(-PW + COB + 8, -55), D(pj - 40, -55), D(pj - 40, -85)])
        for dz in (-150, -250):
            A.ln(D(-PW + COB, dz), D(pj - 40, dz), "ARM_TRANSV")
        xs6 = list(range(60, pj - 40, 80))
        for dx in xs6:
            A.ln(D(dx, -30), D(dx, -h + 30), "ARM_TRANSV")
        A.bolha_lider(D(-PW / 2, -55), D(-PW / 2, 0)[0], D(0, zt)[1] + 4, pa)
        A.bolha_lider(D(-PW + COB, -250), D(-PW, 0)[0] - 6, D(0, -250)[1], pb)
        A.bolha_lider(D(xs6[0], -h / 2), D(pj, 0)[0] + 6, D(0, -h / 2)[1] - 4, pc)
        # barras explodidas do consolo (1:20)
        xq = D(pj, 0)[0] + 18
        gU = bar[pa]["geo"]
        bU = A.forma(xq, yb_ - 6 - (gU["b"] + gU["g"]) * 10 / ED, bar[pa], ED)
        bE = A.forma(xq, bU[1] - 5 - bar[pb]["geo"]["b"] * 10 / ED, bar[pb], ED)
        b6 = A.forma(max(bU[2], bE[2]) + 10, yb_ - 6 - bar[pc]["geo"]["b"] * 10 / ED, bar[pc], ED)
        ybot = min(D(0, zb)[1] - 2, bE[1], b6[1])
        faces = "; ".join(sorted({f"face {fc}" for fc, _, _ in g["faces"]}))
        A.titulo(xm + 4, ybot - 5, f"DETALHE C{k} — {g['tipos']}", f"{g['n']} consolo{'s' if g['n'] > 1 else ''} ({faces}) · tirante {g['nt']} Ø{fd(g['dt'])} · esc. 1:20")
        yb_ = ybot - 16

    # ------------------------------------------------ tabelas (direita)
    xt = qx + QW - 98
    y = qy + QH_ - 8
    y = A.tabela_ferros(xt, y, P["barras"], 1)
    y, kg1 = A.resumo(xt, y - 3, P["barras"], 1, fck=40, vol=P["V"], area=P["area_forma"])
    if P["qtd"] > 1:
        y = A.tabela_ferros(xt, y - 6, P["barras"], P["qtd"])
        y, kgn = A.resumo(xt, y - 3, P["barras"], P["qtd"], fck=40, vol=P["V"], area=P["area_forma"])
    return dict(marca=mk, qtd=P["qtd"], kg=kg1, V=P["V"], area=P["area_forma"], ybase=min(y, yb_), ymeio=yb_, ytab=y)


def folha(num, total, marcas):
    pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                            conteudo=f"ARMADURAS — PRÉ-MOLDADOS — PILARES {', '.join(marcas)} — SEÇÕES E LISTA DO AÇO",
                            desenho=f"ND-LET-AR-PIL-{num:02d}", folha=f"{num:02d}/{total:02d}", fase="PARA APROVAÇÃO"))
    pr.revisao("00", "13/10/2026", "EMISSÃO INICIAL — PADRÃO DE ARMADURAS")
    pr.revisao("04", "16/10/2026", "NBR 9062: PILARES LATERAIS 14 Ø20 (MÉTODO GERAL)")
    A = Arm(pr)
    Q = pr.quadro
    X0, Y0 = Q[0], Q[1]
    res = []
    for i, mk in enumerate(marcas):
        P = json.load(open(f"/home/claude/letsara/pranchas/arm/{mk}.json"))
        qx = X0 + (i % 2) * QW
        qy = Y0 + (1 - i // 2) * QH
        res.append(quadrante(A, P, qx, qy))
    # divisões
    xm = X0 + QW
    A.ln((xm, Y0), (xm, Q[3]), "CARIMBO_FINO"); A.ln((X0, Y0 + QH), (X0 + 2 * QW, Y0 + QH), "CARIMBO_FINO"); A.ln((X0 + 2 * QW, Y0), (X0 + 2 * QW, Q[3]), "CARIMBO")
    # coluna da direita: resumo da folha + notas
    xr = X0 + 2 * QW + 6
    y = Q[3] - 6
    lin = [[r["marca"], r["qtd"], f1(r["V"] * r["qtd"]), f1(r["kg"] * r["qtd"], 1)] for r in res]
    lin.append(["TOTAL", sum(r["qtd"] for r in res), f1(sum(r["V"] * r["qtd"] for r in res)), f1(sum(r["kg"] * r["qtd"] for r in res), 1)])
    y = pr.tabela(xr, y, "RESUMO DA FOLHA (+10%)", ["MARCA", "QT", "CONC. (m³)", "CA-50 (kg)"], lin, [36, 20, 52, 60], h_lin=5.0, destaque_ultima=True)
    pr.notas(xr, y - 6, [
        "Todas as dimensões em centímetro, exceto onde indicado; níveis em metro.",
        "Cobrimento da armadura 3,0 cm (CAA II, NBR 6118:2023 tab. 7.2); espaçadores plásticos a cada 80 cm.",
        "Aço CA-50 (NBR 7480). Comprimentos C= já com dobras; RESUMO com +10% de perdas.",
        "Dobramento: pino de dobra 5Ø (Ø < 20) e 8Ø (Ø 20) nas barras; 3Ø nos estribos (NBR 6118:2023 tab. 9.1).",
        "Estribos com ganchos 135° e ponta reta de 10Ø (mín. 7 cm); grampos N3 a cada estribo.",
        f"N1 e N1A sem emenda (barras inteiras). N1A param no recuo da cabeça com gancho 90°; N13 (armadura da cabeça, Ø{P.get('d13', 16):g}) ancoram {P.get('emb13', 600) / 10:g} cm no corpo (traspasse NBR 6118:2023 9.5.2.2, α0t 2,0, má aderência).",
        "Consolos: tirante N em U por cima do pino, costura N horizontal e estribos verticais (NBR 9062:2017 7.3).",
        "Fôrma, insertos (IP-01, pinos PN, neoprene) e alças de içamento AL-2: ver a prancha de fôrma de cada marca indicada no título.",
        "Concreto C40; desforma e içamento com fcj ≥ 21 MPa. Pilar concretado deitado, face A para cima.",
        "Armação conforme opção A (concreto armado); alternativa protendida em estudo na ND-LET-PIL-P01.",
        "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."], 168)
    avisos = pr.salvar(f"/home/claude/letsara/pranchas/ND-LET-AR-PIL-{num:02d}")
    err = [a for a in avisos if a[0] == "ERRO"]
    sob = [a for a in avisos if "sobrep" in a[1] or "cruza" in a[1]]
    print(f"ND-LET-AR-PIL-{num:02d}", len(err), "erros,", len(sob), "sobreposições/cruzamentos,", len(avisos), "avisos")
    for a in err + sob:
        print("  ", a)
    return res


if __name__ == "__main__":
    grupos = [ORDEM[i:i + 4] for i in range(0, len(ORDEM), 4)]
    alvo = [int(a) for a in sys.argv[1:]] or range(1, len(grupos) + 1)
    for n in alvo:
        folha(n, len(grupos), grupos[n - 1])
