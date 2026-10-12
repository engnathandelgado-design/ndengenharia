"""Prancha genérica de viga pré-moldada protendida de seção I (fôrma, armação, insertos) — padrão ND.
Usada por I110 (V405/406/407) e VM (mezanino). Cotas de concreto em cm, chaparia em mm. Rodar: python viga_i.py i110 | vm"""
import math, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha, MASSA_ACO

f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
Y_LIN = [0.0, 10.05, 19.705, 29.36, 38.865, 48.445, 58.025, 67.605, 76.81]
X_FACH = [0.0, 9.87, 20.05, 29.63, 40.10]


def sec_pts(b, h, ts, ti, m, bw):
    return [(-b / 2, 0), (b / 2, 0), (b / 2, ti), (bw / 2, ti + m), (bw / 2, h - ts - m), (b / 2, h - ts), (b / 2, h),
            (-b / 2, h), (-b / 2, h - ts), (-bw / 2, h - ts - m), (-bw / 2, ti + m), (-b / 2, ti)]


def area_I(b, h, ts, ti, m, bw):
    return (b * ts + b * ti + bw * (h - ts - ti) + 2 * 0.5 * (b - bw) / 2 * m * 2) / 1e6     # m²


def prancha_viga(P):
    H, B, L = P["h"], P["b"], P["L"]
    HD, LN = (P["dente"] or (0, 0))
    ESC = P["esc"]
    A = area_I(B, H, P["ts"], P["ti"], P["m"], P["bw"])
    V = A * L / 1000 + (B * H / 1e6 - A) * P["x_mac"] / 1000 * 2 - (2 * B * (H - HD) * LN / 1e9 if HD else 0)
    peso = V * 25
    n_cord = sum(len(xs) for _, xs, _ in P["cord"])
    F_cord = P["sig_pi"] * 98.7 / 1000
    A1 = P.get("fmt", "A0") == "A1"
    pr = Prancha(P.get("fmt", "A0"), dict(cliente="MARQUE ENGENHARIA", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                            conteudo=P["titulo"] + " — FÔRMA, ARMAÇÃO E INSERTOS", desenho=P["desenho"], folha="01/01", fase="PARA APROVAÇÃO",
                            marca=P["marca"], qtd=P["qtd"], peso=f(peso, 1), volume=f(V, 2)))
    pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL")
    Q = pr.quadro
    XC = Q[2] - 190
    # cabeçalho
    pr.ret(Q[0] + 4, Q[3] - 30, Q[0] + (500 if A1 else 600), Q[3] - 4, "CARIMBO")
    pr.texto(Q[0] + 10, Q[3] - 24, P["marca"], "grande", "TITULO")
    pr.texto(Q[0] + 60, Q[3] - 24, P["titulo"], "titulo", "TITULO")
    pr.texto(Q[0] + 10, Q[3] - 14, P["subtitulo"] + f"   ·   PESO {f(peso/10, 2)} t   ·   VOLUME {f(V, 2)} m³   ·   {n_cord} cord. Ø12,7 CP-190 RB", "nota", "TEXTO")

    # ------------------------------------------------------------ planta-chave (posição das marcas) 1:1000
    kp = pr.vista("PLANTA-CHAVE", (Q[0] + (560 if A1 else 800), Q[3] - (112 if A1 else 165)), 1000 if A1 else 600, titulo="PLANTA-CHAVE", subtitulo=P["kp_sub"], unidade="cm")
    M = lambda v: v * 1000
    for y in Y_LIN:
        kp.linha((M(-2), M(y)), (M(42), M(y)), "EIXO")
    for x in X_FACH:
        kp.linha((M(x), M(-2)), (M(x), M(79)), "EIXO")
    for i, y in enumerate(Y_LIN, 1):
        kp.texto((M(-3.5), M(y)), str(i), "min", "MIDDLE_RIGHT")
    for j, x in enumerate(X_FACH):
        kp.texto((M(x), M(80)), "ABCDE"[j], "min", "BOTTOM_CENTER")
    for (x0, y0, x1, y1, rot) in P["kp_pecas"]:
        kp.ret(M(min(x0, x1)) - 200, M(min(y0, y1)) - 200, abs(M(x1 - x0)) + 400, abs(M(y1 - y0)) + 400, "CORTADO")
        kp.texto((M((x0 + x1) / 2) + 500, M((y0 + y1) / 2)), rot, "min", "MIDDLE_LEFT")

    # ------------------------------------------------------------ ELEVAÇÃO DE FÔRMA
    ve = pr.vista("ELEVAÇÃO", (Q[0] + 40, Q[3] - (165 if A1 else 225)), ESC, titulo=f"ELEVAÇÃO DE FÔRMA — {P['marca']}", subtitulo="vista lateral; ponta esquerda = ponta 1", unidade="cm")
    if HD:
        ve.poli([(0, H - HD), (LN, H - HD), (LN, 0), (L - LN, 0), (L - LN, H - HD), (L, H - HD), (L, H), (0, H)], "VISTA", fechada=True)
        ve.ret(LN, 0, L - 2 * LN, 0, "VISTA")
    else:
        ve.ret(0, 0, L, H, "VISTA")
    for x0 in (P["x_mac"], L - P["x_mac"]):
        ve.linha((x0, 0 if not HD else 0), (x0, H), "OCULTA")
    ve.linha((LN if HD else 0, P["ti"]), (L - (LN if HD else 0), P["ti"]), "OCULTA"); ve.linha((LN if HD else 0, H - P["ts"]), (L - (LN if HD else 0), H - P["ts"]), "OCULTA")
    for x in (P["pino_x"], L - P["pino_x"]):                                           # tubo TB na ponta (oculto)
        ve.ret(x - P["tb"][0] / 2, H - HD if HD else 0, P["tb"][0], P["tb"][1], "OCULTA")
        ve.chapa(x - 150, (H - HD if HD else 0) - 12.5, 300, 12.5)                      # CH-A no fundo
    for s in P.get("tercas", []):
        ve.chapa(s - 75, H, 150, 12.5)
    for s in P.get("alcas", []):
        ve.poli([(s - 60, H), (s - 60, H + 100), (s, H + 140), (s + 60, H + 100), (s + 60, H)], "METALICA")
    for s, z_topo in P.get("consolos", []):                                             # consolos CV-TS (I110): vistos de lado
        ve.ret(s - 500, z_topo - 450, 1000, 450, "OCULTA")
        ve.linha((s - 500, 0), (s - 500, H), "OCULTA"); ve.linha((s + 500, 0), (s + 500, H), "OCULTA")
    xs_cota = [0] + ([LN] if HD else []) + [P["x_mac"], L - P["x_mac"]] + ([L - LN] if HD else []) + [L]
    ve.cota_h(sorted(set(xs_cota)), 0 if not HD else 0, -10)
    ords = sorted(set([0, P["pino_x"]] + list(P.get("tercas", [])) + [s for s, _ in P.get("consolos", [])] + list(P.get("alcas", [])) + [L - P["pino_x"], L]))
    ve.cota_ord(ords, H + (140 if P.get("alcas") else 0), 14, x0=0)
    ve.cota_v([0, H - HD, H] if HD else [0, H], L, 10, total=False)
    ve.chamada((P["pino_x"], H - HD + P["tb"][1] / 2 if HD else P["tb"][1] / 2), (12, 16), f"{P['tb_nome']} (2x)")
    if HD:
        ve.chamada((LN / 2, H - HD / 2), (-8, -16), f"dente {HD/10:g} × {LN/10:g} cm")
    if P.get("tercas"):
        ve.chamada((P["tercas"][2], H + 12), (8, 12), "CH-T1 150×150×12,5 (terças)")
    if P.get("consolos"):
        ve.chamada((P["consolos"][0][0], P["consolos"][0][1] - 225), (10, -16), "consolos CV-TS nos dois lados (maciço de 100 cm)")
    ve.marcador_corte((L / 2, -22 * ESC), (L / 2, H + 24 * ESC), "A", lado=1)
    ve.marcador_corte((P["x_mac"] / 2 + 100, -22 * ESC), (P["x_mac"] / 2 + 100, H + 24 * ESC), "B", lado=1)
    ve.marcador_detalhe((P["pino_x"] + 200, H / 2), max(H * 0.9, 700), 1, ang=-120, dist=8)

    # ------------------------------------------------------------ PLANTA SUPERIOR
    vp = pr.vista("PLANTA", (Q[0] + 40, Q[3] - (240 if A1 else 320)), ESC, titulo=f"PLANTA SUPERIOR — {P['marca']}", subtitulo="topo da mesa; insertos e consolos", unidade="cm")
    vp.ret(0, -B / 2, L, B, "VISTA")
    for x0 in (P["x_mac"], L - P["x_mac"]):
        vp.linha((x0, -B / 2), (x0, B / 2), "OCULTA")
    vp.linha((0, -P["bw"] / 2), (L, -P["bw"] / 2), "OCULTA"); vp.linha((0, P["bw"] / 2), (L, P["bw"] / 2), "OCULTA")
    for x in (P["pino_x"], L - P["pino_x"]):
        vp.circulo((x, 0), P["tb"][0] / 2, "VISTA")
    for s in P.get("tercas", []):
        vp.chapa(s - 75, -75, 150, 150)
    for s, z_topo in P.get("consolos", []):
        vp.ret(s - 500, -B / 2 - 350, 1000, 350, "VISTA"); vp.ret(s - 500, B / 2, 1000, 350, "VISTA")
        vp.circulo((s, -B / 2 - 175), 10, "VISTA"); vp.circulo((s, B / 2 + 175), 10, "VISTA")
    for s in P.get("alcas", []):
        vp.linha((s, -60), (s, 60), "METALICA")
    vp.cota_v([-B / 2, B / 2], L, 10)
    if P.get("consolos"):
        vp.cota_v([-B / 2 - 350, -B / 2], 0, -10, total=False)
        vp.chamada((P["consolos"][1][0], B / 2 + 175), (8, 12), "CV-TS 100 × 35 × 45/25 com PN-1 Ø20 — assento +8,489 (lado A) / +8,514 (lado E)")

    # ------------------------------------------------------------ CORTES 1:10
    pts = sec_pts(B, H, P["ts"], P["ti"], P["m"], P["bw"])
    YR = Q[3] - (455 if A1 else 700)
    def corte(nome, org, sub, macico=False):
        v = pr.vista(nome, org, 10, titulo=nome, subtitulo=sub, unidade="cm")
        pp = [(-B / 2, 0), (B / 2, 0), (B / 2, H), (-B / 2, H)] if macico else pts
        v.poli(pp, "CORTADO", fechada=True); v.hachura(pp, "AR-CONC", 0.03)
        for y, xs, _ in P["cord"]:
            for x in xs:
                v.ponto_barra((x, y), 12.7, "ARM_PROT_SECAO")
        v.cota_h([-B / 2, -P["bw"] / 2, P["bw"] / 2, B / 2], 0, -12, total=True)
        v.cota_v([0, P["ti"], H - P["ts"], H], B / 2, 12)
        return v
    va = corte("CORTE A-A", (Q[0] + 60, YR), "seção corrente")
    cob = 30
    e = [(-P["bw"] / 2 + cob, P["ti"] - 20), (P["bw"] / 2 - cob, P["ti"] - 20), (P["bw"] / 2 - cob, H - cob), (-P["bw"] / 2 + cob, H - cob)]
    va.poli(e, "ARM_TRANSV", fechada=True)
    for x in (-B / 2 + cob, B / 2 - cob):
        va.ponto_barra((x, H - cob - 5), 10); va.ponto_barra((x, cob + 5), 10)
    for yy in P.get("pele", []):
        va.ponto_barra((-P["bw"] / 2 + cob, yy), 8); va.ponto_barra((P["bw"] / 2 - cob, yy), 8)
    va.chamada((P["bw"] / 2 - cob, H / 2), (12, 10), f"N2 estribo Ø{P['est'][0]:g} c/{P['est'][1]//10} (c/{P['est'][2]//10} nos {P['est'][3]/1000:g} m das pontas)")
    va.chamada((B / 2 - cob, H - cob - 5), (12, 8), "N3 — 2 Ø10 porta-estribos (mesa superior)")
    va.chamada((P["cord"][0][1][-1], P["cord"][0][0]), (14, -12), f"C1 — {n_cord} cord. Ø12,7 (ver tabela)")
    if P.get("pele"):
        va.chamada((P["bw"] / 2 - cob, P["pele"][0]), (12, -8), "N4 pele 2 Ø8 por face")
    va.cota_v([0] + [y for y, _, _ in P["cord"]], -B / 2, -12, total=False)
    va.cota_h(sorted(set(x for _, xs, _ in P["cord"] for x in xs)), 0, -24, total=False)
    vb = corte("CORTE B-B", (Q[0] + (250 if A1 else 270), YR), "maciço da ponta (TB e CH-A)", macico=True)
    vb.chapa(-P["tb"][0] / 2, 0, P["tb"][0], H - HD if HD else H * 0.6)
    vb.chapa(-150, -12.5, 300, 12.5)
    for x in (-120, 120):
        vb.poli([(x, 0), (x, 180), (x + (25 if x < 0 else -25), 200)], "METALICA")
    vb.chamada((-P["tb"][0] / 2, (H - HD) * 0.9 if HD else H * 0.55), (-12, 14), P["tb_nome"])
    vb.chamada((150, -6), (14, -10), "CH-A 300×150×12,5 + 2 grapas Ø12,5")
    vb.chamada((-B / 2 + cob, H - cob - 5), (-8, 14), "N2 c/" + f"{P['est'][2]//10}")

    # ------------------------------------------------------------ DETALHE 1 — ponta (1:10) com armação
    d1 = pr.vista("DETALHE 1", (Q[0] + (400 if A1 else 450), YR), 10, titulo="DETALHE 1 — PONTA, APOIO E ARMAÇÃO" + (" DO DENTE" if HD else ""),
                  subtitulo=("NBR 9062:2017 7.4 / PCI 5.6 — verificado por MEF não linear" if HD else "apoio direto no consolo (sem dente)"), unidade="cm")
    LD = max(1800, 2 * LN + 800)
    if HD:
        d1.poli([(0, H - HD), (LN, H - HD), (LN, 0), (LD, 0), (LD, H), (0, H)], "VISTA", fechada=True)
        d1.interrupcao((LD, 0), (LD, H))
        d1.chapa(P["pino_x"] - P["tb"][0] / 2, H - HD, P["tb"][0], P["tb"][1])
        d1.chapa(P["pino_x"] - 150, H - HD - 12.5, 300, 12.5)
        d1.chapa(P["pino_x"] - 125, H - HD - 22.5, 250, 10)                                   # neoprene
        y_t = H - HD + 55
        d1.poli([(cob, y_t - 150), (cob, y_t), (P["anc"], y_t)], "ARMADURA")                   # N5 tirante
        d1.chamada((P["anc"] * 0.6, y_t), (10, 12), f"N5 tirante — {P['tir']} (ancoragem {P['anc']/10:.0f} cm) c/ dobra")
        for k in range(P["n_sus"]):                                                          # N6 suspensão
            x = LN + 60 + k * 80
            d1.poli([(x, cob), (x, H - cob)], "ARM_TRANSV")
        d1.chamada((LN + 60 + 80, H - cob - 100), (12, 10), f"N6 suspensão — {P['sus']} (até 1/2 hd da reentrância)")
        for k in range(P["n_cost"]):                                                         # N7 costura
            y = H - HD + 150 + k * 100
            d1.poli([(cob, y), (LN + 900, y)], "ARM_TRANSV")
        d1.chamada((LN + 400, H - HD + 150 + 100 * (P["n_cost"] - 1)), (12, 10), f"N7 costura — {P['cost']} (estribos horizontais)")
        for k in range(P["n_v"]):                                                            # N8 estribos verticais no dente
            x = 100 + k * 80
            d1.poli([(x, H - HD + cob), (x, H - cob)], "ARM_TRANSV")
        d1.chamada((100, H - 60), (-8, 14), f"N8 — {P['n_v']} estribos Ø10 no dente")
        d1.cota_v([0, H - HD, H], LD, 10, total=False)
        d1.cota_h([0, P["pino_x"], LN, LD], H - HD, -12, total=False)
        d1.chamada((P["pino_x"], H - HD + 60), (10, -26), f"{P['tb_nome']}; pino do consolo Ø{P['pino_d']} grauteado só numa ponta")
    else:
        d1.poli([(0, 0), (LD, 0), (LD, H), (0, H)], "VISTA", fechada=True)
        d1.interrupcao((LD, 0), (LD, H))
        d1.chapa(P["pino_x"] - P["tb"][0] / 2, 0, P["tb"][0], P["tb"][1])
        d1.chapa(P["pino_x"] - 150, -12.5, 300, 12.5)
        d1.chapa(P["pino_x"] - 125, -22.5, 250, 10)
        for k in range(6):
            x = 60 + k * 100
            d1.poli([(x, cob), (x, H - cob)], "ARM_TRANSV")
        d1.chamada((360, H - cob - 100), (12, 10), f"N2 Ø{P['est'][0]:g} c/{P['est'][2]//10} na zona de apoio (Vd {P['Vd']} kN)")
        d1.poli([(cob, cob + 60), (cob, cob), (1500, cob)], "ARMADURA"); d1.chamada((900, cob), (10, -12), "N5 — 2 Ø16 no fundo (fretagem do apoio)")
        d1.cota_v([0, H], LD, 10)
        d1.cota_h([0, P["pino_x"], 250, LD], 0, -12, total=False)
        d1.chamada((P["pino_x"], P["tb"][1] / 2), (14, 20), f"{P['tb_nome']}; pino do consolo Ø{P['pino_d']}; apoio 25 cm no consolo CP-MEZ")
    d1.ret(-25, -30, 300, 10, "OCULTA"); d1.chamada((250, -25), (12, -22), "NEO 300×150×10 e consolo (ver prancha do pilar)")

    # ------------------------------------------------------------ ELEVAÇÃO DE ARMAÇÃO
    varm = pr.vista("ARMAÇÃO", (Q[0] + 40, Q[3] - (325 if A1 else 430)), ESC, titulo=f"ELEVAÇÃO DE ARMAÇÃO — {P['marca']}", subtitulo="estribos N2; cordoalhas C1; pontas conforme DETALHE 1", unidade="cm")
    if HD:
        varm.poli([(0, H - HD), (LN, H - HD), (LN, 0), (L - LN, 0), (L - LN, H - HD), (L, H - HD), (L, H), (0, H)], "VISTA", fechada=True)
    else:
        varm.ret(0, 0, L, H, "VISTA")
    d_est, s1, s2, zona = P["est"]
    xs_e = list(range(50, zona, s2)) + list(range(zona, L - zona, s1)) + list(range(L - zona, L - 40, s2))
    for x in xs_e:
        varm.linha((x, cob if x > LN and x < L - LN or not HD else H - HD + cob), (x, H - cob), "ARM_TRANSV")
    for y, xs, isol in P["cord"]:
        varm.linha((0, y), (L, y), "ARM_PROT")
    varm.linha((cob, H - cob - 5), (L - cob, H - cob - 5), "ARMADURA")
    varm.chamada((L / 2, H - cob - 5), (10, 12), "N3 — 2 Ø10 porta-estribos")
    varm.chamada((zona + 300, cob + 50), (10, -16), f"N2 — {len(xs_e)} estribos Ø{d_est:g}: c/{s1//10} corrente, c/{s2//10} nos {zona/1000:g} m das pontas")
    varm.chamada((L / 2, P["cord"][0][0]), (10, -14), f"C1 — {n_cord} cord. Ø12,7" + (f"; {P['n_isol']} isoladas {P['isol_mm']/1000:g} m nas pontas" if P.get("n_isol") else ""))
    varm.cota_h([0, zona, L - zona, L], 0, -10)

    # ------------------------------------------------------------ coluna direita
    y = Q[3] - 6
    y = pr.tabela(XC, y, f"MARCAS — {P['familia']}", ["MARCA", "POSIÇÃO", "QT", "L (cm)", "PESO (t)"], P["marcas"], [18, 70, 10, 24, 24], h_lin=6.0)
    nE = len(xs_e)
    C_E = round((2 * (P["bw"] - 2 * cob + H - 2 * cob) + 160) / 10)
    barras = [dict(pos="N2", diam=d_est, qtd=nE, comp=C_E, forma=[(0, 0), (9, 0), (9, 60), (0, 60), (0, 0), (2, 2)], trechos=[f"{(P['bw']-2*cob)/10:g}", f"{(H-2*cob)/10:g}", "", ""]),
              dict(pos="N3", diam=10.0, qtd=2, comp=round((L - 2 * cob) / 10), trechos=[f"{round((L-2*cob)/10)}"])]
    if P.get("pele"):
        barras.append(dict(pos="N4", diam=8.0, qtd=2 * len(P["pele"]), comp=round((L - 2 * cob) / 10), trechos=[f"{round((L-2*cob)/10)}"]))
    barras += P["barras_ponta"]
    ta = pr.tabela_croqui(XC, y - 4, barras, h_lin=9.0)
    y = ta["y_base"]
    cords = []
    for k, (yy, xs, isol) in enumerate(P["cord"], 1):
        cords.append(dict(pos="C1", diam=12.7, qtd=len(xs), y=yy, forca=F_cord, isol=isol))
    tc = pr.tabela_cordoalhas(XC, y - 4, cords, P["L_pista"])
    y = tc["y_base"]
    y = pr.tabela(XC, y - 4, "INSERTOS POR PEÇA — dimensões em mm", ["MARCA", "DESCRIÇÃO", "QT", "POSIÇÃO"], P["insertos"], [16, 104, 10, 52])
    qd = [["MARCA", P["marca"], "SEÇÃO", f"I{H/10:g} (b {B/10:g}, bw {P['bw']/10:g})"],
          ["COMPRIMENTO", f"{L/10:g} cm", "CONCRETO", f"C{P['fck']} / fckj {P['fckj']} MPa"],
          ["VOLUME", f"{f(V, 2)} m³", "PESO", f"{f(peso/10, 2)} t"],
          ["AÇO CA-50", f"{f(ta['total_kg'], 0)} kg", "PROTENSÃO", f"{n_cord} cord. Ø12,7 — {f(F_cord, 1)} kN/cord."],
          ["DENTE", f"{HD/10:g} × {LN/10:g} cm" if HD else "sem dente (apoio direto)", "COBRIMENTO", "3,0 cm (CAA II)"]]
    y = pr.tabela(XC, y - 4, "QUADRO DA PEÇA", ["ITEM", "VALOR", "ITEM", "VALOR"], qd, [30, 62, 30, 60])
    y = pr.tabela(XC, y - 4, "MEMÓRIA RESUMIDA", ["VERIFICAÇÃO", "RESULTADO"], P["memoria"], [70, 112])
    y = pr.legenda_armadura(XC, y - 4, True)
    pr.notas(XC, y - 4, P["notas"] + ["Cotas de concreto em cm, chaparia em mm, níveis em m. Não medir no desenho. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."], 182)
    for pos in (("N5", "N6", "N7", "N8", "C1") if HD else ("N5", "C1")):
        pr.posicoes_desenho.add(pos)
    avisos = pr.salvar(f"/home/claude/letsara/pranchas/{P['desenho']}")
    print(P["desenho"], len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
    for a in avisos:
        if a[0] == "ERRO" or "sobrep" in a[1]:
            print(a)
    return pr


# ================================================================== I110 — V405 / V406 / V407
def dados_i110():
    L = 23140
    z_esq, z_dir = 8489, 8514
    # consolos CV-TS nas linhas 5 e 6 (dentro da V406: L4 → P13); topo do consolo medido do fundo da viga (+7,78)
    consolos = [(round((Y_LIN[k] - Y_LIN[3]) * 1000 + 275), 8489 - 7780) for k in (4, 5)]
    return dict(
        marca="V406", qtd=1, familia="VIGAS CENTRAIS I110 (EIXO C)", desenho="ND-LET-I110", h=1100, b=400, ts=220, ti=250, m=80, bw=150, L=L, esc=30,
        x_mac=1400, dente=(660, 350), pino_x=175, tb=(60.3, 600), tb_nome="TB-2 tubo Ø60,3×3,6 L=600", pino_d=25,
        cord=[(60, [-150, -100, -50, 0, 50, 100, 150], 0), (110, [-150, -100, -50, 0, 50, 100, 150], 0),
              (160, [-150, -100, -50, 0, 50, 100, 150], 2000), (210, [-50, 0, 50], 2000)],
        n_isol=10, isol_mm=2000, sig_pi=1400, L_pista=60, fck=50, fckj=35, pele=[400, 600, 800],
        est=(8.0, 150, 100, 2000), Vd=448, alcas=[2500, L - 2500], tercas=[],
        consolos=consolos, anc=1468, tir="4 Ø20", n_sus=3, sus="3 estribos Ø16 fechados", n_cost=3, cost="3 estribos Ø10", n_v=3,
        titulo="VIGA CENTRAL I110 PROTENDIDA — V406 (L = 2314 cm) · V405 · V407", subtitulo="eixo C, entre P11 (linha 4) e P13; dentes Gerber 66 × 35; consolos CV-TS para as TS-01 nas linhas 3, 5, 6, 7 e 8; V405 vai até o P14 (linha 9)",
        kp_sub="V405/406/407 no eixo C", kp_pecas=[(20.05, 10.05, 20.05, 29.36, "V407"), (20.05, 29.36, 20.05, 53.05, "V406"), (20.05, 53.05, 20.05, 76.81, "V405")],
        marcas=[["V407", "eixo C, L2 → L4 (PC-01 / PC-01)", 1, "1876", f(area_I(400, 1100, 220, 250, 80, 150) * 25 * 18.76 / 10, 1)],
                ["V406", "eixo C, L4 → P13 (PC-01 / PC-02)", 1, "2314", f(area_I(400, 1100, 220, 250, 80, 150) * 25 * 23.14 / 10, 1)],
                ["V405", "eixo C, P13 → L9 (PC-02 / PF-04 = P14)", 1, "2321", f(area_I(400, 1100, 220, 250, 80, 150) * 25 * 23.21 / 10, 1)]],
        barras_ponta=[dict(pos="N5", diam=20.0, qtd=4, comp=165, forma=[(0, 15), (0, 0), (150, 0)], trechos=["15", "150"]),
                      dict(pos="N6", diam=16.0, qtd=3, comp=round((2 * (90 + 1040) + 160) / 10), forma=[(0, 0), (9, 0), (9, 104), (0, 104), (0, 0), (2, 2)], trechos=["9", "104", "", ""]),
                      dict(pos="N7", diam=10.0, qtd=3, comp=round((2 * (340 + 1250) + 140) / 10), forma=[(0, 0), (125, 0), (125, 34), (0, 34), (0, 0), (2, 2)], trechos=["125", "34", "", ""]),
                      dict(pos="N8", diam=10.0, qtd=3, comp=round((2 * (340 + 600) + 140) / 10), forma=[(0, 0), (34, 0), (34, 60), (0, 60), (0, 0), (2, 2)], trechos=["34", "60", "", ""])],
        insertos=[["TB-2", "Tubo Ø60,3×3,6 L=600 a prumo, soldado na CH-A2", 2, "pontas, a 175 da face"],
                  ["CH-A2", "Chapa 350×300×12,5 + 4 grapas Ø12,5 (fundo do dente)", 2, "fundo dos dentes"],
                  ["AL-3", "2 laços de cordoalha Ø12,7 (4 pernas) por alça", 2, "a 250 cm das pontas"],
                  ["PN-1", "Pino Ø20 CA-50 L=700 nos consolos CV-TS (2 por linha)", 10, "consolos (linhas 3, 5, 6, 7, 8)"],
                  ["NEO-2", "Neoprene 300×250×30 fretado (apoio nos PC)", 2, "sobre os consolos CP-I110"]],
        memoria=[["ELU flexão (V406)", "MRd ≥ Md — ver ND-LET-MC02"], ["ELS-F / ELS-D (CAA II)", "atende (protensão limitada)"],
                 ["Dente 66 × 35 (MEF não linear)", "Vu ≥ 1,06 Vd = 475 kN"], ["Estribo mínimo (ρsw)", "Ø8 c/15 = 6,7 ≥ 2,4 cm²/m"],
                 ["Pele (h > 60 cm)", "2 Ø8 por face a cada 20 cm"], ["Içamento (2 pontos a 2,5 m)", "σt ≤ fctk,j — sem fissura"]],
        notas=["Concreto C50; cordoalhas CP-190 RB Ø12,7 em 4 linhas (y = 60, 110, 160 e 210 mm): 10 isoladas 200 cm nas pontas (linhas 160 e 210). σpi = 1400 MPa; liberar com fckj ≥ 35 MPa.",
               "Dentes Gerber 66 × 35 nas duas pontas, armadura N5/N6/N7/N8 (NBR 9062:2017 7.4 e PCI 5.6), verificados por MEF não linear; maciço de 140 cm nas pontas.",
               "Consolos CV-TS dos dois lados nas linhas 3, 5, 6, 7 e 8 (maciço de 100 cm na alma): topo a 3 %, pino PN-1 Ø20, assento +8,489 (lado A) e +8,514 (lado E).",
               "Apoio nos pilares centrais PC: neoprene NEO-2 300×250×30 fretado e pino PN-2 Ø25 no consolo CP-I110; graute só numa ponta de cada viga.",
               "V405 (P13 → linha 9) apoia na ponta sobre o consolo CP-I110 do pilar de fachada P14 (PF-04), face voltada ao pavilhão, assento +8,190.",
               "Içar pelas 2 alças AL-3 (2 laços cada); estocar sobre 2 calços nas alças; não virar a peça."])


# ================================================================== VM — vigas do mezanino I90 com dentes 45×30
def dados_vm():
    L = 9530
    return dict(
        fmt="A1", marca="VM-02", qtd=4, familia="VIGAS DO MEZANINO I90 (LINHAS 1 E 2, NÍVEIS +3,15 E +6,55)", desenho="ND-LET-VM01", h=900, b=400, ts=120, ti=150, m=80, bw=150, L=L, esc=20,
        x_mac=1200, dente=(450, 300), pino_x=150, tb=(50, 450), tb_nome="TB-1 tubo Ø50×3,0 L=450", pino_d=20,
        cord=[(60, [-150, -100, -50, 0, 50, 100, 150], 0), (110, [-50, 50], 0)],
        sig_pi=1400, L_pista=60, fck=50, fckj=35, pele=[400, 600],
        est=(8.0, 200, 100, 1500), Vd=383, alcas=[1900, L - 1900], tercas=[], consolos=[],
        anc=1122, tir="3 Ø20", n_sus=3, sus="3 estribos Ø16 fechados", n_cost=3, cost="3 estribos Ø10", n_v=3,
        titulo="VIGA DO MEZANINO I90 PROTENDIDA — VM-02 (L = 953 cm) · VM-01 · VM-03 · VM-04", subtitulo="linhas 1 e 2, níveis +3,15 e +6,55; dentes Gerber 45 × 30 nos consolos CP-MEZ; laje alveolar h20 + 5 sobre a mesa",
        kp_sub="VM nas linhas 1 e 2", kp_pecas=[(0.0, 0.0, 9.87, 0.0, "VM-01"), (9.87, 10.05, 20.05, 10.05, "VM-02"), (20.05, 0.0, 29.63, 0.0, "VM-03"), (29.63, 10.05, 40.10, 10.05, "VM-04")],
        marcas=[["VM-01", "A–B, linhas 1 e 2, 2 níveis", 4, "922", f(area_I(400, 900, 120, 150, 80, 150) * 25 * 9.22 / 10, 1)],
                ["VM-02", "B–C, linhas 1 e 2, 2 níveis", 4, "953", f(area_I(400, 900, 120, 150, 80, 150) * 25 * 9.53 / 10, 1)],
                ["VM-03", "C–D, linhas 1 e 2, 2 níveis", 4, "893", f(area_I(400, 900, 120, 150, 80, 150) * 25 * 8.93 / 10, 1)],
                ["VM-04", "D–E, linhas 1 e 2, 2 níveis", 4, "982", f(area_I(400, 900, 120, 150, 80, 150) * 25 * 9.82 / 10, 1)]],
        barras_ponta=[dict(pos="N5", diam=20.0, qtd=3, comp=127, forma=[(0, 15), (0, 0), (112, 0)], trechos=["15", "112"]),
                      dict(pos="N6", diam=16.0, qtd=3, comp=round((2 * (90 + 840) + 160) / 10), forma=[(0, 0), (9, 0), (9, 84), (0, 84), (0, 0), (2, 2)], trechos=["9", "84", "", ""]),
                      dict(pos="N7", diam=10.0, qtd=3, comp=round((2 * (340 + 1200) + 140) / 10), forma=[(0, 0), (120, 0), (120, 34), (0, 34), (0, 0), (2, 2)], trechos=["120", "34", "", ""]),
                      dict(pos="N8", diam=10.0, qtd=3, comp=round((2 * (340 + 390) + 140) / 10), forma=[(0, 0), (34, 0), (34, 39), (0, 39), (0, 0), (2, 2)], trechos=["34", "39", "", ""])],
        insertos=[["TB-1", "Tubo Ø50×3,0 L=450 a prumo, soldado na CH-A1", 2, "pontas, a 150 da face"],
                  ["CH-A1", "Chapa 300×150×12,5 + 2 grapas Ø12,5 (fundo)", 2, "fundo das pontas"],
                  ["AL-1", "Laço de cordoalha Ø12,7 (2 pernas)", 2, "a 190 cm das pontas"],
                  ["NEO-1", "Neoprene 300×150×10 (furo Ø30)", 2, "sobre os consolos CP-MEZ"]],
        memoria=[["ELU flexão (laje h20+5, 500 kgf/m²)", "atende — ver ND-LET-MC02"], ["ELS-F / ELS-D (CAA II)", "atende (protensão limitada)"],
                 ["Dente 45 × 30 (MEF não linear)", "Vu 436 ≥ 1,06 Vd = 406 kN (FS 1,14)"], ["Cortante no apoio (Vd 383 kN)", "Ø8 c/10 nos 150 cm: 11,2 ≥ 8,2 cm²/m"],
                 ["Içamento (2 pontos a 1,9 m)", "σt ≤ fctk,j — sem fissura"]],
        notas=["Concreto C50; 9 cordoalhas CP-190 RB Ø12,7 (7 em y = 60 e 2 em y = 110 mm), todas aderentes. σpi = 1400 MPa; liberar com fckj ≥ 35 MPa.",
               "Dentes Gerber 45 × 30 nas duas pontas (seção I90: o dente da I70 foi reprovado no MEF), armadura N5/N6/N7/N8 (NBR 9062:2017 7.4 e PCI 5.6), verificados por MEF não linear; maciço de 120 cm nas pontas.",
               "Apoio 20 cm sobre o consolo CP-MEZ (assento = nível do piso − 70 cm: +2,45 e +5,85); pé-direito livre sob a viga = nível − 115 cm.",
               "Laje alveolar h20 apoia 10 cm sobre a mesa superior (b = 40); capa de 5 cm (2º estágio) com tela Q138; chavetas grauteadas antes da capa.",
               "Pino PN-1 Ø20 do consolo entra no TB-1: grauteado numa ponta só de cada viga; a outra com graute flexível.",
               "Içar pelas 2 alças AL-1; estocar sobre 2 calços nas alças."])


if __name__ == "__main__":
    qual = sys.argv[1] if len(sys.argv) > 1 else "i110"
    prancha_viga(dados_i110() if qual == "i110" else dados_vm())
