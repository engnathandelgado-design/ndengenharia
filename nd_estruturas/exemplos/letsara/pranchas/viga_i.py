"""Prancha genérica de viga pré-moldada protendida de seção I (fôrma, armação, insertos) — padrão ND.
Usada por I130 (V405/406/407) e VM (mezanino). Cotas de concreto em cm, chaparia em mm. Rodar: python viga_i.py i110 | vm"""
import json, math, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha, MASSA_ACO

f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from geometria import Y_LIN, X_FACH, X_EIXO, Y_P13
I1J = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/i110_r01.json"))
LGJ = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/ligacoes.json"))
XC = X_EIXO["C"]


def x_n8(n, ln=350, x_tb=175, r_tb=30, c=60):
    """Posições (mm, da ponta) dos estribos N8 do nariz do dente: entre 60 e ln − 60, ≥ 40 mm livres do tubo TB-2 Ø60,3
    (eixo a x_tb) — metade antes e metade depois do tubo. Igual a calc_dentes.x_n8 (o MEF usa estas posições)."""
    a1, b1 = c, x_tb - r_tb - 40 - 5
    a2, b2 = x_tb + r_tb + 40 + 5, ln - c
    n1 = (n + 1) // 2
    n2 = n - n1
    l1 = [a1 + k * (b1 - a1) / max(n1 - 1, 1) for k in range(n1)]
    l2 = [a2 + k * (b2 - a2) / max(n2 - 1, 1) for k in range(n2)] if n2 else []
    return [round(x / 5) * 5 for x in l1 + l2]


def sec_pts(b, h, ts, ti, m, bw):
    return [(-b / 2, 0), (b / 2, 0), (b / 2, ti), (bw / 2, ti + m), (bw / 2, h - ts - m), (b / 2, h - ts), (b / 2, h),
            (-b / 2, h), (-b / 2, h - ts), (-bw / 2, h - ts - m), (-bw / 2, ti + m), (-b / 2, ti)]


def area_I(b, h, ts, ti, m, bw):
    return (b * ts + b * ti + bw * (h - ts - ti) + 2 * 0.5 * (b - bw) / 2 * m * 2) / 1e6     # m²


def armacao_i(P, L, cob=30):
    """Armação passiva da viga I (por marca, comprimento L em mm): estribos N2 da alma, N3 mesa superior, N4 pele,
    N9/N10 salientes (2º estágio), N11 estribo da mesa inferior (envolve as cordoalhas), N12 2 Ø10 nos cantos da mesa inferior,
    N13 estribo da mesa superior (envolve o N3), N5–N8 dos dentes. geo = forma em escala (cm) para a prancha de armaduras."""
    H, B, bw, ts, ti = P["h"], P["b"], P["bw"], P["ts"], P["ti"]
    d_est, s1, s2, zona = P["est"]
    HD, LN = (P["dente"] or (0, 0))
    xs_e = list(range(50, zona, s2)) + list(range(zona, L - zona, s1)) + list(range(L - zona, L - 40, s2))
    if HD:                                                   # no trecho do dente valem os estribos N8 do dente
        xs_e = [x for x in xs_e if LN + 40 <= x <= L - LN - 40]
    N3n, N3d, _ = P.get("n3", (2, 10.0, ""))
    a2, b2 = (bw - 2 * cob) / 10, (H - 2 * cob) / 10
    Ll = round((L - 2 * cob) / 10)
    Lc = L - 2 * LN                                          # corpo (entre as faces dos dentes): mesa inferior, N12 e cordoalhas
    n_fl_i = round(Lc / 250) + 1
    n_fl = round(L / 250) + 1
    Ll12 = round((Lc - 2 * cob) / 10)
    af, bfi, bfs = (B - 2 * cob) / 10, (ti - 2 * cob) / 10, (ts - 2 * cob) / 10
    barras = [dict(pos="N2", diam=d_est, qtd=len(xs_e), comp=round(2 * (a2 + b2) + 16), forma=[(0, 0), (9, 0), (9, 60), (0, 60), (0, 0), (2, 2)], trechos=[f"{a2:g}", f"{b2:g}", "", ""], geo=dict(k="E", a=a2, b=b2)),
              dict(pos="N3", diam=N3d, qtd=N3n, comp=Ll, trechos=[f"{Ll}"], geo=dict(k="R", a=Ll))]
    if P.get("pele"):
        barras.append(dict(pos="N4", diam=8.0, qtd=2 * len(P["pele"]), comp=Ll, trechos=[f"{Ll}"], geo=dict(k="R", a=Ll)))
    if P.get("seg"):
        n9 = len(range(100, L - 60, 150))
        barras.append(dict(pos="N9", diam=8.0, qtd=n9, comp=round((2 * (600 + 170) + (bw - 2 * cob)) / 10), forma=[(0, 0), (0, 77), (9, 77), (9, 0)], trechos=["77", "9", "77"],
                           geo=dict(k="U", a=77, b=9, g=0)))
        barras.append(dict(pos="N10", diam=10.0, qtd=2, comp=round((L - 200) / 10), trechos=[f"{round((L-200)/10)}"], geo=dict(k="R", a=round((L - 200) / 10))))
    barras += [dict(pos="N11", diam=6.3, qtd=n_fl_i, comp=round(2 * (af + bfi) + 14), forma=[(0, 0), (34, 0), (34, 9), (0, 9), (0, 0), (1.5, 1.5)], trechos=[f"{af:g}", f"{bfi:g}", "", ""], geo=dict(k="E", a=af, b=bfi)),
               dict(pos="N12", diam=10.0, qtd=2, comp=Ll12, trechos=[f"{Ll12}"], geo=dict(k="R", a=Ll12)),
               dict(pos="N13", diam=6.3, qtd=n_fl, comp=round(2 * (af + bfs) + 14), forma=[(0, 0), (34, 0), (34, 6), (0, 6), (0, 0), (1.5, 1.5)], trechos=[f"{af:g}", f"{bfs:g}", "", ""], geo=dict(k="E", a=af, b=bfs))]
    for b in P["barras_ponta"]:
        b = dict(b)
        b["qtd"] = 2 * b["qtd"]                                # DEC-032: barras_ponta são por ponta; a peça tem as 2 pontas
        fm = b["forma"]
        if b["pos"] == "N5" and len(fm) == 4:                  # alça horizontal (U deitado)
            b["geo"] = dict(k="U", a=fm[0][0], b=fm[2][1], g=0)
        elif b["pos"] == "N5":
            b["geo"] = dict(k="L", a=fm[2][0], g=fm[0][1])
        else:
            b["geo"] = dict(k="E", a=fm[2][0], b=fm[2][1])
        barras.append(b)
    return xs_e, barras


def prancha_viga(P):
    H, B, L = P["h"], P["b"], P["L"]
    HD, LN = (P["dente"] or (0, 0))
    ESC = P["esc"]
    A = area_I(B, H, P["ts"], P["ti"], P["m"], P["bw"])
    V = A * L / 1000 + (B * H / 1e6 - A) * P["x_mac"] / 1000 * 2 - (2 * B * (H - HD) * LN / 1e9 if HD else 0)
    peso = V * 25
    n_cord = sum(len(xs) for _, xs, _ in P["cord"])
    F_cord = P["sig_pi"] * P.get("a_cord", 98.7) / 1000
    CT = P.get("cord_txt", "Ø12,7")
    A1 = P.get("fmt", "A0") == "A1"
    pr = Prancha(P.get("fmt", "A0"), dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                            conteudo=P["titulo"] + " — FÔRMA, ARMAÇÃO E INSERTOS", desenho=P["desenho"], folha="01/01", fase="PARA APROVAÇÃO",
                            marca=P["marca"], qtd=P["qtd"], peso=f(peso, 1), volume=f(V, 2)))
    pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL")
    for rv in P.get("revs", []):
        pr.revisao(*rv)
    Q = pr.quadro
    XC = Q[2] - 190
    # cabeçalho (rev08: motor padrão; nomes de cada peça por extenso)
    import renomear as RN
    import chave as CH
    _ms = sorted({rot for *_, rot in P["kp_pecas"]})
    _nomes = [n for m in _ms for n in RN.nomes_de(m)]
    pr.cabecalho_peca("\x01" + RN.lista(_nomes), P["titulo"], P["subtitulo"] + f"   ·   PESO {f(peso/10, 2)} t   ·   VOLUME {f(V, 2)} m³   ·   {n_cord} cord. {CT} CP-190 RB")

    # ------------------------------------------------------------ planta-chave: círculo + chamada em cada peça (rev08)
    CH.planta(pr, (Q[0] + (560 if A1 else 880), Q[3] - (112 if A1 else 165)), 1000 if A1 else 600, _nomes, subtitulo=P["kp_sub"], lado_fixo=-1)

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
        if P.get("cha", True):
            ve.chapa(x - 150, (H - HD if HD else 0) - 12.5, 300, 12.5)                  # CH-A no fundo
    for s in P.get("tercas", []):
        ve.chapa(s - 75, H, 150, 12.5)
    for s0 in P.get("pinos_topo", []):                                                 # apoios das TS-01 no topo: NEO-3 + PN-5
        for dn in (-115, 115):
            ve.ret(s0 - 150, H, 300, 10, "VISTA")
        for ds in (-100, 100):
            ve.ret(s0 + ds - 10, H - 300, 20, 600, "METALICA")
    for s in P.get("alcas", []):
        ve.poli([(s - 60, H), (s - 60, H + 100), (s, H + 140), (s + 60, H + 100), (s + 60, H)], "METALICA")
    for s, z_topo in P.get("consolos", []):                                             # consolos CV-TS (I130): vistos de lado
        ve.ret(s - 500, z_topo - 440, 1000, 440, "OCULTA")
        ve.linha((s - 500, 0), (s - 500, H), "OCULTA"); ve.linha((s + 500, 0), (s + 500, H), "OCULTA")
    xs_cota = [0] + ([LN] if HD else []) + [P["x_mac"], L - P["x_mac"]] + ([L - LN] if HD else []) + [L]
    ve.cota_h(sorted(set(xs_cota)), 0 if not HD else 0, -10)
    ords = sorted(set([0, P["pino_x"]] + list(P.get("tercas", [])) + [s for s, _ in P.get("consolos", [])] + list(P.get("pinos_topo", [])) + list(P.get("alcas", [])) + [L - P["pino_x"], L]))
    ve.cota_ord(ords, H + (140 if P.get("alcas") else 0), 14, x0=0)
    ve.cota_v([0, H - HD, H] if HD else [0, H], L, 10, total=False)
    ve.chamada((P["pino_x"], H - HD + P["tb"][1] / 2 if HD else P["tb"][1] / 2), (12, 16), f"{P['tb_nome'].split(' ')[0]} (2x)")
    if HD:
        ve.chamada((LN / 2, H - HD / 2), (-8, -16), f"dente {HD/10:g} × {LN/10:g} cm")
    if P.get("tercas"):
        ve.chamada((P["tercas"][2], H + 12), (8, 12), "CH-T1 150×150×12,5 (terças)")
    if P.get("pinos_topo"):
        ve.chamada((P["pinos_topo"][0] + 100, H + 200), (10, 26), "apoio das TS-01: 2 NEO-3 + 4 PN-5 Ø20 por linha")
    if P.get("consolos"):
        ve.chamada((P["consolos"][0][0], P["consolos"][0][1] - 225), (10, -16), "consolos CV-TS nos dois lados (maciço de 100 cm)")
    xA = L / 2 + 1200                                                       # fora dos textos centrais das cotas
    ve.marcador_corte((xA, -22 * ESC), (xA, H + 24 * ESC), "A", lado=1)
    ve.marcador_corte((P["x_mac"] * 0.8, -22 * ESC), (P["x_mac"] * 0.8, H + 24 * ESC), "B", lado=1)
    if P.get("seg"):
        ve.marcador_corte((L * 0.7, -22 * ESC), (L * 0.7, H + 24 * ESC), "C", lado=1)
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
    for s0 in P.get("pinos_topo", []):
        for dn in (-115, 115):
            vp.ret(s0 - 150, dn - 50, 300, 100, "OCULTA")
            for ds in (-100, 100):
                vp.circulo((s0 + ds, dn), 10, "METALICA")
    if P.get("pinos_topo"):
        vp.chamada((P["pinos_topo"][0] + 100, 115), (8, 14), "PN-5 Ø20 a ±10 do eixo da linha, ±11,5 do eixo da viga")
    vp.cota_v([-B / 2, B / 2], L, 10)
    if P.get("consolos"):
        vp.cota_v([-B / 2 - 350, -B / 2], 0, -10, total=False)
        vp.chamada((P["consolos"][1][0], B / 2 + 175), (8, 12), "CV-TS 100 × 35 × 44 com PN-1 Ø20 — assento +8,480 (lado A) / +8,505 (lado E)")

    # ------------------------------------------------------------ ISOMÉTRICOS (iso3d_vigas.py) — rev08, só I130 (A0)
    if not A1 and P["desenho"] == "ND-LET-I130":
        pr.imagem(Q[0] + 35, Q[1] + 312, Q[0] + 600, Q[1] + 458, "/home/claude/letsara/pranchas/ISO-I130-geral.png",
                  titulo=f"ISOMÉTRICO — {P['marca']}", subtitulo="peça inteira: dentes, alças AL-3, apoios das TS-01 (NEO-3 + PN-5), TB-2")
        pr.imagem(Q[0] + 640, Q[1] + 292, Q[0] + 900, Q[1] + 458, "/home/claude/letsara/pranchas/ISO-I130-ponta.png",
                  titulo="ISOMÉTRICO — PONTA NO CONSOLO CP-I130", subtitulo="dente, NEO-2 fretado, PN-2 no TB-2")

    # ------------------------------------------------------------ CORTES 1:10
    pts = sec_pts(B, H, P["ts"], P["ti"], P["m"], P["bw"])
    YR = Q[3] - (455 if A1 else 700)
    def corte(nome, org, sub, macico=False):
        v = pr.vista(nome, org, 10, titulo=nome, subtitulo=sub, unidade="cm")
        pp = [(-B / 2, 0), (B / 2, 0), (B / 2, H), (-B / 2, H)] if macico else pts
        v.poli(pp, "CORTADO", fechada=True); v.hachura(pp, "AR-CONC", 0.03)
        for y, xs, _ in P["cord"]:
            for x in xs:
                v.ponto_barra((x, y), P.get("d_cord", 12.7), "ARM_PROT_SECAO")
        v.cota_h([-B / 2, -P["bw"] / 2, P["bw"] / 2, B / 2], H, 12, total=True)
        v.cota_v([0, P["ti"], H - P["ts"], H], B / 2, 12)
        return v
    va = corte("CORTE A-A", (Q[0] + (60 if A1 else 105), YR), "seção corrente")
    cob = 30
    e = [(-P["bw"] / 2 + cob, cob), (P["bw"] / 2 - cob, cob), (P["bw"] / 2 - cob, H - cob), (-P["bw"] / 2 + cob, H - cob)]
    va.poli(e, "ARM_TRANSV", fechada=True)
    va.poli([(-B / 2 + cob, cob), (B / 2 - cob, cob), (B / 2 - cob, P["ti"] - cob), (-B / 2 + cob, P["ti"] - cob)], "ARM_TRANSV", fechada=True)          # N11
    va.poli([(-B / 2 + cob, H - P["ts"] + cob), (B / 2 - cob, H - P["ts"] + cob), (B / 2 - cob, H - cob), (-B / 2 + cob, H - cob)], "ARM_TRANSV", fechada=True)  # N13
    va.chamada((B / 2 - cob, P["ti"] - cob), (16, 7), "N11 Ø6,3 c/25 (mesa inf.)")
    va.chamada((B / 2 - cob, H - P["ts"] + cob), (24, 4), "N13 Ø6,3 c/25 (mesa sup.)")
    va.chamada((-B / 2 + cob, cob + 5), (-28, -14), "N12 — 2 Ø10")
    N3n, N3d, N3t = P.get("n3", (2, 10.0, "porta-estribos (mesa superior)"))
    xs3 = (-B / 2 + cob + 10, B / 2 - cob - 10) if N3n == 2 else tuple(-B / 2 + cob + 10 + k * (B - 2 * cob - 20) / (N3n - 1) for k in range(N3n))
    for x in xs3:
        va.ponto_barra((x, H - cob - 5 - N3d / 2), N3d)
    for x in (-B / 2 + cob, B / 2 - cob):
        va.ponto_barra((x, cob + 5), 10)
    for yy in P.get("pele", []):
        va.ponto_barra((-P["bw"] / 2 + cob, yy), 8); va.ponto_barra((P["bw"] / 2 - cob, yy), 8)
    va.chamada((P["bw"] / 2 - cob, H / 2), (36, 10), f"N2 estribo Ø{P['est'][0]:g} c/{P['est'][1]//10} (c/{P['est'][2]//10} nos {P['est'][3]/1000:g} m das pontas)")
    va.chamada((xs3[-1], H - cob - 5), (12, 8), f"N3 — {N3n} Ø{N3d:g} {N3t}")
    va.chamada((P["cord"][0][1][-1], P["cord"][0][0]), (14, -12), f"C1 — {n_cord} cord. {CT} (ver tabela)")
    if P.get("pele"):
        va.chamada((-P["bw"] / 2 + cob, P["pele"][0]), (-30, -4), "N4 pele 2 Ø8 por face")
    va.cota_v([0] + [y for y, _, _ in P["cord"]], -B / 2, -12, total=False)
    _sets = []
    for _, xs, _ in P["cord"]:
        if tuple(xs) not in _sets:
            _sets.append(tuple(xs))
    _sets = [xs_ for xs_ in _sets if not any(set(xs_) < set(o_) for o_ in _sets)]   # subconjuntos já cotados (X5 dentro do X7)
    for k_, xs_ in enumerate(_sets):
        va.cota_h(list(xs_), 0, -12 - 8 * k_, total=False)
    vb = corte("CORTE B-B", (Q[0] + (250 if A1 else 315), YR), "maciço da ponta (TB e CH-A)", macico=True)
    vb.chapa(-P["tb"][0] / 2, 0, P["tb"][0], H - HD if HD else H * 0.6)
    if P.get("cha", True):
        vb.chapa(-150, -12.5, 300, 12.5)
        for x in (-120, 120):
            vb.poli([(x, 0), (x, 180), (x + (25 if x < 0 else -25), 200)], "METALICA")
    vb.chamada((-P["tb"][0] / 2, (H - HD) * 0.9 if HD else H * 0.55), (-28, 14), P["tb_nome"].split(" ")[0] + " (passante)")
    if P.get("cha", True):
        vb.chamada((150, -6), (14, -10), "CH-A 300×150×12,5 + 2 grapas Ø12,5")
    vb.chamada((-B / 2 + cob, H - cob - 5), (-8, 14), "N2 c/" + f"{P['est'][2]//10}")

    # ------------------------------------------------------------ DETALHE 1 — ponta (1:10) com armação
    d1 = pr.vista("DETALHE 1", (Q[0] + (400 if A1 else 500), YR), 10, titulo="DETALHE 1 — PONTA, APOIO E ARMAÇÃO" + (" DO DENTE" if HD else ""),
                  subtitulo=("NBR 9062:2017 7.4 / PCI 5.6 — verificado por MEF não linear" if HD else "apoio direto no consolo (sem dente)"), unidade="cm")
    LD = max(1800, 2 * LN + 800)
    if HD:
        d1.poli([(0, H - HD), (LN, H - HD), (LN, 0), (LD, 0), (LD, H), (0, H)], "VISTA", fechada=True)
        d1.interrupcao((LD, 0), (LD, H))
        d1.chapa(P["pino_x"] - P["tb"][0] / 2, H - HD, P["tb"][0], P["tb"][1])
        if P.get("cha", True):
            d1.chapa(P["pino_x"] - 150, H - HD - 12.5, 300, 12.5)
        d1.ret(P["pino_x"] - 125, H - HD - 30, 250, 30, "VISTA")                              # neoprene
        y_t = H - HD + 55
        d1.poli([(cob, y_t), (P["anc"], y_t)], "ARMADURA")                                      # N5 tirante: alças horizontais (U deitado)
        d1.chamada((P["anc"] * 0.6, y_t), (10, (H - y_t) / 10 + 16), (f"N5 tirante — {P['n5_u']} alças horizontais Ø20 (U deitado, curva na face do dente), ramos de {P['anc']/10:.0f} cm"
                                                     if P.get("n5_u") else f"N5 tirante — {P['tir']} (ancoragem {P['anc']/10:.0f} cm)"))
        for k in range(P["n_sus"]):                                                          # N6 suspensão
            x = LN + 60 + k * 80
            d1.poli([(x, cob), (x, H - cob)], "ARM_TRANSV")
        d1.chamada((LN + 60 + 80, H - cob - 100), (-12, 13 + cob / 10), f"N6 suspensão — {P['sus']} (até 1/2 hd da reentrância)")
        for k in range(P["n_cost"]):                                                         # N7 costura
            y = H - HD + 150 + k * 100
            d1.poli([(cob, y), (LN + 900, y)], "ARM_TRANSV")
        d1.chamada((LN + 400, H - HD + 150 + 100 * (P["n_cost"] - 1)), (40, 10), f"N7 costura — {P['cost']}")
        for x in x_n8(P["n_v"], LN, P["pino_x"]):                                            # N8 estribos verticais no nariz, fora do TB-2
            d1.poli([(x, H - HD + cob), (x, H - cob)], "ARM_TRANSV")
        d1.chamada((100, H - 60), (-14, -10), f"N8 — {P["n_v"]} estribos Ø10 no dente")
        d1.cota_v([0, H - HD, H], LD, 10, total=False)
        d1.cota_h([0, P["pino_x"], LN, LD], H - HD, -12, total=False)
        d1.chamada((P["pino_x"], H - HD + 60), (-12, -(H - HD + 60) / 10 - 14), f"{P['tb_nome'].split(' ')[0]}; pino Ø{P['pino_d']} grauteado numa ponta")
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

    # ------------------------------------------------------------ CORTE C-C — 2º ESTÁGIO (só VM): laje alveolar + enchimento + capa + N9 salientes
    SEG = P.get("seg")
    if SEG:
        z0 = 700
        vc = pr.vista("CORTE C-C", (Q[0] + 120, Q[1] - 42), 10, titulo="CORTE C-C — 2º ESTÁGIO (SOLIDARIZAÇÃO)",
                      subtitulo="laje alveolar h20 apoiada 10 cm na mesa; enchimento + capa C25 moldados na obra; N9 salientes", unidade="cm")
        top = [(-P["bw"] / 2, z0), (P["bw"] / 2, z0), (B / 2, H - P["ts"]), (B / 2, H), (-B / 2, H), (-B / 2, H - P["ts"])]
        vc.poli(top, "CORTADO", fechada=True); vc.hachura(top, "AR-CONC", 0.03)
        vc.interrupcao((-P["bw"] / 2, z0), (P["bw"] / 2, z0), "CORTADO")
        xl0, xl1 = B / 2 - 100, B / 2 - 100 + 600                                            # laje alveolar (lado da laje)
        vc.ret(xl0, H + 10, xl1 - xl0, 190, "CORTADO"); vc.interrupcao((xl1, H + 10), (xl1, H + 200), "CORTADO")
        for xc_ in (xl0 + 160, xl0 + 400):
            vc.circulo((xc_, H + 105), 70, "VISTA")
        vc.ret(xl0, H, 150, 10, "METALICA")                                                   # neoprene 10 mm
        ench = [(-B / 2, H), (xl0, H), (xl0, H + 200), (-B / 2, H + 200)]
        vc.poli(ench, "VISTA", fechada=True); vc.hachura(ench, "AR-CONC", 0.045)
        capa = [(-B / 2, H + 200), (xl1, H + 200), (xl1, H + 250), (-B / 2, H + 250)]
        vc.poli(capa, "VISTA", fechada=True); vc.hachura(capa, "AR-CONC", 0.045)
        vc.linha((-B / 2 + 20, H + 225), (xl1, H + 225), "ARMADURA")                         # tela Q138
        vc.linha((-B / 2 + 30, H + 215), (xl1, H + 215), "ARMADURA")                         # negativa Ø10 c/25
        xs9 = (-P["bw"] / 2 + cob, P["bw"] / 2 - cob)
        vc.poli([(xs9[0], z0), (xs9[0], H + 170), (xs9[1], H + 170), (xs9[1], z0)], "ARM_TRANSV")   # N9 saliente
        for x9 in xs9:
            vc.ponto_barra((x9, H + 160), 10)                                                  # N10
        for x in (-B / 2 + cob, B / 2 - cob):
            vc.ponto_barra((x, H - cob - 5), 10)
        vc.cota_v([H, H + 200, H + 250], xl1, 10, total=False)
        vc.cota_h([-B / 2, xl0, B / 2], H, -10, total=False)
        vc.chamada((xs9[1], H + 60), (70, -4), f"N9 estribo saliente Ø8 c/15 (2 ramos, sai 17 cm do topo) — interface 9062 6.3.5: τsd {f(SEG['interface']['tau_sd_total_MPa'],2)} ≤ {f(SEG['interface']['tau_Rd_MPa'],2)} MPa")
        vc.chamada((xs9[0], H + 160), (-10, -12), "N10 — 2 Ø10 nos cantos do N9")
        vc.chamada((xl0 + 300, H + 225), (36, 6), "tela Q138 na capa de 5 cm, por cima da viga")
        vc.chamada((xl0 + 450, H + 215), (40, -10), "negativa Ø10 c/25 L=150 (alvéolo grauteado + capa sobre a viga)")
        vc.chamada((-B / 2 + 80, H + 100), (-6, 10), "enchimento C25 (30 × 20)")
        vc.chamada((xl0 + 75, H + 5), (12, -18), "neoprene 10 mm; apoio 10 cm")
        vc.chamada((xl0 + 400, H + 105), (28, 14), "laje alveolar h20 (ND-LET-LA01)")
        vc.chamada((B / 2 - cob, H - cob - 5), (14, 6), "N3")

    # ------------------------------------------------------------ ELEVAÇÃO DE ARMAÇÃO
    varm = pr.vista("ARMAÇÃO", (Q[0] + 40, Q[3] - (325 if A1 else 430)), ESC, titulo=f"ELEVAÇÃO DE ARMAÇÃO — {P['marca']}", subtitulo="estribos N2; cordoalhas C1; pontas conforme DETALHE 1", unidade="cm")
    if HD:
        varm.poli([(0, H - HD), (LN, H - HD), (LN, 0), (L - LN, 0), (L - LN, H - HD), (L, H - HD), (L, H), (0, H)], "VISTA", fechada=True)
    else:
        varm.ret(0, 0, L, H, "VISTA")
    d_est, s1, s2, zona = P["est"]
    xs_e, _ = armacao_i(P, L)
    for x in xs_e:
        varm.linha((x, cob if x > LN and x < L - LN or not HD else H - HD + cob), (x, H - cob), "ARM_TRANSV")
    for y, xs, isol in P["cord"]:
        varm.linha((LN, y), (L - LN, y), "ARM_PROT")
    varm.linha((cob, H - cob - 5), (L - cob, H - cob - 5), "ARMADURA")
    varm.chamada((L / 2, H - cob - 5), (10, 12), f"N3 — {N3n} Ø{N3d:g} {N3t}")
    if SEG:
        xs9e = list(range(100, L - 60, 150))
        for x in xs9e:
            varm.linha((x, H), (x, H + 170), "ARM_TRANSV")
        varm.linha((100, H + 160), (L - 100, H + 160), "ARMADURA")
        varm.chamada((L - 400, H + 120), (8, 2), f"N9 — {len(xs9e)} estribos salientes Ø8 c/15 + N10 2 Ø10 (CORTE C-C)")
    varm.chamada((zona + 300, cob + 50), (10, -16), f"N2 — {len(xs_e)} estribos Ø{d_est:g}: c/{s1//10} corrente, c/{s2//10} nos {zona/1000:g} m das pontas")
    varm.chamada((L / 2, P["cord"][0][0]), (10, -14), f"C1 — {n_cord} cord. {CT}" + (f"; {P['n_isol']} isoladas {P['isol_mm']/1000:g} m nas pontas" if P.get("n_isol") else ""))
    varm.cota_h([0, zona, L - zona, L], 0, -10)

    # ------------------------------------------------------------ coluna direita
    y = Q[3] - 6
    y = pr.tabela(XC, y, f"MARCAS — {P['familia']}", ["MARCA", "POSIÇÃO", "QT", "L (cm)", "PESO (t)"], P["marcas"], [18, 70, 10, 24, 24], h_lin=6.0)
    _, barras = armacao_i(P, L, cob)
    ta = pr.tabela_croqui(XC, y - 4, barras, h_lin=9.0)
    y = ta["y_base"]
    cords = []
    for k, (yy, xs, isol) in enumerate(P["cord"], 1):
        cords.append(dict(pos="C1", diam=P.get("d_cord", 12.7), qtd=len(xs), y=yy, forca=F_cord, isol=isol))
    tc = pr.tabela_cordoalhas(XC, y - 4, cords, P["L_pista"])
    y = tc["y_base"]
    y = pr.tabela(XC, y - 4, "INSERTOS POR PEÇA — dimensões em mm", ["MARCA", "DESCRIÇÃO", "QT", "POSIÇÃO"], P["insertos"], [16, 104, 10, 52])
    qd = [["MARCA", P["marca"], "SEÇÃO", f"I{H/10:g} (b {B/10:g}, bw {P['bw']/10:g})"],
          ["COMPRIMENTO", f"{L/10:g} cm", "CONCRETO", f"C{P['fck']} / fckj {P['fckj']} MPa"],
          ["VOLUME", f"{f(V, 2)} m³", "PESO", f"{f(peso/10, 2)} t"],
          ["AÇO CA-50", f"{f(ta['total_kg'], 0)} kg", "PROTENSÃO", f"{n_cord} cord. {CT} — {f(F_cord, 1)} kN/cord."],
          ["DENTE", f"{HD/10:g} × {LN/10:g} cm" if HD else "sem dente (apoio direto)", "COBRIMENTO", "3,0 cm (CAA II)"]]
    y = pr.tabela(XC, y - 4, "QUADRO DA PEÇA", ["ITEM", "VALOR", "ITEM", "VALOR"], qd, [30, 62, 30, 60])
    y = pr.legenda_armadura(XC, y - 4, True)
    pr.notas(XC, y - 4, P["notas"] + ["Cotas de concreto em cm, chaparia em mm, níveis em m. Não medir no desenho. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."], 182)
    for pos in (("N5", "N6", "N7", "N8", "C1") if HD else ("N5", "C1")) + (("N9", "N10") if SEG else ()) + ("N11", "N12", "N13", "N2", "N3") + (("N4",) if P.get("pele") else ()):
        pr.posicoes_desenho.add(pos)
    avisos = pr.salvar(f"/home/claude/letsara/pranchas/{P['desenho']}")
    print(P["desenho"], len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
    for a in avisos:
        if True:
            print(a)
    return pr


# ================================================================== I130 — V405 / V406 / V407
def dados_i110():
    L = round(I1J["V406"]["L_peca"] * 1000)
    y0 = Y_LIN[3] + 0.20 + 0.075                                    # ponta da V406 (face do P11 + 75)
    pinos = [round((Y_LIN[k] - y0) * 1000) for k in (4, 5)]          # TS-01 das linhas 5 e 6 apoiadas no topo (rev03)
    Lm = {k: I1J[k]["L_peca"] for k in ("V405", "V406", "V407")}
    DTI = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/dentes.json"))["I130"]["calculo"]["adotado"]
    anc = DTI["ancoragem_tirante_mm"]
    zt, za = LGJ["Z_TOPO_I130"], LGJ["Z_ASS_I130"]
    ztd, dgc = LGJ["Z_TOPO_I130_DIR"], round(LGJ["DEGRAU_C"] * 1000)
    Fz = lambda z: f"{z:.3f}".replace(".", ",")
    HI = round(LGJ["H_I130"] * 1000)                                  # DEC-054: h 120 (antes 130)
    A = area_I(400, HI, 220, 250, 80, 150)
    ARR = I1J["V406"]["arranjo"]                                     # DEC-032: cordoalhas, σpi e fckj saem do cálculo (uma fonte só)
    cord = [(l["y"], l["xs"], l["isol"]) for l in ARR["linhas"]]
    n_inf, n_sup = ARR["n_inf"], ARR["n_cord"] - ARR["n_inf"]
    n_isol = sum(len(l["xs"]) for l in ARR["linhas"] if l["isol"])
    isol_txt = " e ".join(f"{len(l['xs'])} em y = {l['y']/10:g} cm isoladas {l['isol']/10:g} cm" for l in ARR["linhas"] if l["isol"])
    ader_txt = ", ".join(f"{len(l['xs'])} em y = {l['y']/10:g}" for l in ARR["linhas"] if not l["isol"] and l["y"] < 600)
    sup_txt = f"; {n_sup} na mesa superior (y = {max(l['y'] for l in ARR['linhas'])/10:g} cm, aderentes)" if n_sup else ""
    n_u = -(-DTI["n_tir"] // 2)                                      # N5: alças horizontais (U deitado), 2 ramos cada
    ICJ = I1J["V406"]["icamento"]
    return dict(
        revs=[("03", "14/10/2026", "I110 → I130 (h 130), DENTE 78 × 35, 26 CORD.; TS-01 NO TOPO (SEM CV-TS); SEM SOLDA"), ("04", "16/10/2026", "NBR 9062: NEO-2 FRETADO; TOPO HORIZONTAL EM 2 NÍVEIS (APOIO DAS TS-01); TOLERÂNCIAS"),
              ("06", "19/10/2026", "DEC-032: 28 + 2 CORDOALHAS, σpi 1453, ISOLAMENTO 2/4 m, fckj 45; DENTE COM A REAÇÃO REAL; N5 EM ALÇAS HORIZONTAIS; AL-3 COM 3 LAÇOS"),
              ("07", "24/10/2026", "DEC-054: h 120 COM DENTE 78 × 35; 24 Ø15,2 (7+5+5+5 + 2 TOPO); PROTENSÃO LIMITADA; LIBERAÇÃO COM fckj 50; N3 6 Ø25; V407 TAMBÉM h 120")],
        marca="V406", qtd=1, familia=f"VIGAS CENTRAIS I{HI // 10} (EIXO C)", desenho="ND-LET-I130", h=HI, d_cord=float(ARR.get("cordoalha", "Ø12.7")[1:]), a_cord={"Ø15.2": 140.0}.get(ARR.get("cordoalha"), 98.7), cord_txt=ARR.get("cordoalha", "Ø12.7").replace(".", ","), b=400, ts=220, ti=250, m=80, bw=150, L=L, esc=30,
        x_mac=1400, dente=(780, 350), pino_x=175, tb=(60.3, 780), tb_nome="TB-2 tubo Ø60,3×3,6 L=780 (passante no dente)", pino_d=25, cha=False,
        n3=(6, 25.0, "CA-50 na mesa superior (compressão no ELU e tração no ato junto às pontas)"),
        cord=cord, n_isol=n_isol, isol_mm=max(l["isol"] for l in ARR["linhas"]), sig_pi=ARR["sig_pi"], L_pista=60, fck=ARR["fck"], fckj=ARR["fckj"],
        lbpt=ARR["lbpt_m"], pele=[p_ for p_ in (500, 650, 800, 950) if p_ < HI - 300], n5_u=n_u,
        est=(8.0, 150, 100, 2000), Vd=round(I1J["V406"]["linhas"]["Vd_kN"]), alcas=[2500, L - 2500], tercas=[],
        consolos=[], pinos_topo=pinos, anc=anc, tir=DTI["tirante"].split(" (")[0], n_sus=DTI["n_sus"], sus=DTI["suspensao"].split(" (")[0],
        n_cost=DTI["n_cost"], cost=DTI["costura"].split(" (")[0], n_v=DTI["n_v"],
        titulo=f"VIGA CENTRAL I{HI // 10} PROTENDIDA — V406 (L = {L/10:.1f} cm) · V405 · V407".replace(".", ","),
        subtitulo=f"eixo C; dentes Gerber 78 × 35 nos consolos CP-I130 (assento +{Fz(za)}); TS-01 apoiadas no topo horizontal em 2 níveis (+{Fz(zt)} lado A / +{Fz(ztd)} lado E) nas linhas 3, 5, 6, 7 e 8",
        kp_sub="vigas centrais no eixo C", kp_pecas=[(XC, Y_LIN[1], XC, Y_LIN[3], "V407"), (XC, Y_LIN[3], XC, Y_P13, "V406"), (XC, Y_P13, XC, Y_LIN[8], "V405")],
        marcas=[["V407", f"C: PC-01 → PC-02; TS-01 na L3 ({I1J['V407']['arranjo']['n_cord']} cord.)", 1, f"{Lm['V407']*100:.1f}".replace(".", ","), f(A * 25 * Lm['V407'] / 10, 1)],
                ["V406", "C: PC-02 → PC-03; TS-01 nas L5, L6", 1, f"{Lm['V406']*100:.1f}".replace(".", ","), f(A * 25 * Lm['V406'] / 10, 1)],
                ["V405", "C: PC-03 → PF-04; TS-01 nas L7, L8", 1, f"{Lm['V405']*100:.1f}".replace(".", ","), f(A * 25 * Lm['V405'] / 10, 1)]],
        barras_ponta=[dict(pos="N5", diam=DTI["d_tir"], qtd=n_u, comp=round(2 * (round(anc / 10) + 3) + 0.5 * 3.1416 * 19 + 10),
                           forma=[(round(anc / 10) + 3, 0), (0, 0), (0, 19), (round(anc / 10) + 3, 19)], trechos=[f"{round(anc / 10) + 3}", "19", f"{round(anc / 10) + 3}"]),
                      dict(pos="N6", diam=16.0, qtd=DTI["n_sus"], comp=round((2 * (90 + HI - 60) + 160) / 10), forma=[(0, 0), (9, 0), (9, (HI - 60) // 10), (0, (HI - 60) // 10), (0, 0), (2, 2)], trechos=["9", f"{(HI - 60) // 10}", "", ""]),
                      dict(pos="N7", diam=10.0, qtd=DTI["n_cost"], comp=round((2 * (340 + 1250) + 140) / 10), forma=[(0, 0), (125, 0), (125, 34), (0, 34), (0, 0), (2, 2)], trechos=["125", "34", "", ""]),
                      dict(pos="N8", diam=10.0, qtd=DTI["n_v"], comp=round((2 * (340 + 720) + 140) / 10), forma=[(0, 0), (34, 0), (34, 72), (0, 72), (0, 0), (2, 2)], trechos=["34", "72", "", ""])],
        insertos=[["TB-2", "Tubo Ø60,3×3,6 L=780, passante, sem solda", 2, "pontas, a 175 da face"],
                  ["AL-3", f"{ICJ['n_lacos']} laços de cordoalha Ø12,7 ({2 * ICJ['n_lacos']} pernas) por alça", 2, f"a {ICJ['a_alca_m'] * 100:g} cm das pontas"],
                  ["PN-5", "Pino Ø20 CA-50 L=600 (300 na viga), apoio das TS-01", 4 * len(pinos), "topo, ±100 da linha, ±115 do eixo"],
                  ["NEO-3", "Neoprene 100×300×10 c/ 2 furos Ø30 (assento das TS-01)", 2 * len(pinos), "topo, nas linhas"],
                  ["NEO-2", "Neoprene 300×200×31 fretado, chapas inox (apoio nos PC)", 2, "sobre os consolos CP-I130"]],
        memoria=[],
        notas=[f"Concreto C{ARR['fck']}; {ARR['n_cord']} cordoalhas CP-190 RB {ARR.get('cordoalha', 'Ø12.7').replace('.', ',')}: {ader_txt} cm (aderentes), {isol_txt} nas pontas (bainha plástica estanque){sup_txt}. σpi = {ARR['sig_pi']:g} MPa ({f(ARR['F_macaco_kN'], 1)} kN por cordoalha no macaco); liberação GRADUAL e simétrica SÓ COM fckj ≥ {ARR['fckj']:g} MPa comprovado por corpo de prova da peça (DEC-054; CP-V e cura térmica) (lbpt = {f(ARR['lbpt_m'] * 100, 0)} cm). Protensão LIMITADA (NBR 6118:2023 Tab. 13.4 nível 2, CAA II, DEC-054): descompressão na combinação quase permanente e sem fissuração na frequente. V407 (vão menor): {I1J['V407']['arranjo']['n_cord']} cordoalhas — " + ", ".join(f"{len(l['xs'])} em y = {l['y']/10:g}" + (f" (isoladas {l['isol']/10:g} cm)" if l['isol'] else "") for l in I1J['V407']['arranjo']['linhas']) + " cm, sem cordoalhas na mesa superior (ver tabela de marcas).",
               "N3 = 6 Ø25 CA-50 na mesa superior: compressão do ELU (x/d ≤ 0,45) e tração no ato junto às pontas (NBR 6118:2023 17.2.4.3.2 b).",
               f"Dentes Gerber 78 × 35 nas duas pontas (NBR 9062:2017 7.4; Fd = γn·Vd = {f(I1J['V406']['dente']['Fd'], 0)} kN, verificado por MEF não linear com esta armação): N5 tirante em {n_u} alças HORIZONTAIS (U deitado) Ø{DTI['d_tir']:g} por ponta, ramos no nível do tirante, dobra interna ≥ 8φ (16 cm), curva junto à face do dente; N6 suspensão, N7 costura, N8 estribos do nariz; maciço de 140 cm nas pontas; TB-2 passante no dente, sem chapa soldada.",
               f"TS-01 apoiadas direto no topo da viga (sem consolos CV-TS), neoprene NEO-3 100×300×10 e 4 pinos PN-5 Ø20 por linha (2 por TS-01), grauteados nos tubos TB-3 das TS-01. TOPO HORIZONTAL EM 2 NÍVEIS ao longo de toda a viga (NBR 9062:2017 7.2.1.6, aparelho horizontal): metade do lado A em +{Fz(zt)} e metade do lado E {dgc} mm acima (+{Fz(ztd)}), degrau no eixo da viga feito com régua-guia no acabamento do topo; h = {HI // 10} cm na metade A e {f(HI / 10 + dgc / 10, 1)} cm na metade E. As pontas das TS-01 têm cunha no fundo e a face de apoio fica horizontal.",
               f"Apoio nos pilares centrais PC: neoprene NEO-2 300×200×31 fretado (2 camadas de 10 + 2 de 2,5 mm, chapas inox 2 mm — NBR 9062:2017 7.2.1.6) e pino PN-2 Ø25 no consolo CP-I130 com mísula (assento +{Fz(za)}; consolo 49 junto ao pilar e 39 na ponta, alinhado ao fundo da viga — DEC-054); graute só numa ponta de cada viga. V405 vai até o consolo do P14 (PF-04).",
               f"Içar pelas 2 alças AL-3 ({ICJ['n_lacos']} laços cada, {f(ICJ['F_alca_d_kN'], 0)} kN de cálculo por alça com βa 1,3); estocar sobre 2 calços nas alças; não virar a peça."])


# ================================================================== VM — vigas do mezanino I90 com dentes 45×30
SEG_VM = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/segundo_estagio.json"))


def dados_vm():
    L1 = round((X_EIXO["B"] - 0.20 - 0.30 - 0.10) * 1000)            # VM-01: A–B e D–E (face 30 do pilar lateral / 20 do P3, P8)
    L = round((X_EIXO["C"] - 0.20 - (X_EIXO["B"] + 0.20) - 0.10) * 1000)  # VM-02: B–C e C–D (faces de 20 dos dois lados)
    return dict(
        fmt="A1", marca="VM-02", qtd=8, familia="VIGAS DO MEZANINO I90", desenho="ND-LET-VM01", h=900, b=400, ts=120, ti=150, m=80, bw=150, L=L, esc=20,
        x_mac=1200, dente=(450, 300), pino_x=150, tb=(50, 450), tb_nome="TB-1 tubo Ø50×3,0 L=450", pino_d=20, cha=False,
        revs=[("03", "14/10/2026", "SEM SOLDA: TB-1 PASSANTE, SEM CHAPA CH-A1")],
        cord=[(60, [-150, -100, -50, 0, 50, 100, 150], 0), (110, [-50, 50], 0)],
        sig_pi=1400, L_pista=60, fck=50, fckj=35, pele=[500, 650],
        est=(8.0, 200, 100, 1500), Vd=383, alcas=[1900, L - 1900], tercas=[], consolos=[],
        anc=1122, tir="3 Ø20", n_sus=3, sus="3 estribos Ø16 fechados", n_cost=3, cost="3 estribos Ø10", n_v=3,
        titulo=f"VIGA DO MEZANINO I90 PROTENDIDA — VM-02 (L = {L/10:g} cm) · VM-01", subtitulo="linhas 1 e 2, níveis +3,15 e +6,55; dentes Gerber 45 × 30 nos consolos CP-MEZ (44 cm, fundo alinhado); laje alveolar h20 + 5 sobre a mesa",
        kp_sub="VM nas linhas 1 e 2", kp_pecas=[(0.0, 0.0, X_EIXO["B"], 0.0, "VM-01"), (X_EIXO["B"], Y_LIN[1], XC, Y_LIN[1], "VM-02"), (XC, 0.0, X_EIXO["D"], 0.0, "VM-02"), (X_EIXO["D"], Y_LIN[1], X_EIXO["E"], Y_LIN[1], "VM-01")],
        marcas=[["VM-01", "A–B e D–E, linhas 1 e 2, 2 níveis", 8, f"{L1/10:g}".replace(".", ","), f(area_I(400, 900, 120, 150, 80, 150) * 25 * L1 / 1e4, 1)],
                ["VM-02", "B–C e C–D, linhas 1 e 2, 2 níveis", 8, f"{L/10:g}".replace(".", ","), f(area_I(400, 900, 120, 150, 80, 150) * 25 * L / 1e4, 1)]],
        barras_ponta=[dict(pos="N5", diam=20.0, qtd=3, comp=127, forma=[(0, 15), (0, 0), (112, 0)], trechos=["15", "112"]),
                      dict(pos="N6", diam=16.0, qtd=3, comp=round((2 * (90 + 840) + 160) / 10), forma=[(0, 0), (9, 0), (9, 84), (0, 84), (0, 0), (2, 2)], trechos=["9", "84", "", ""]),
                      dict(pos="N7", diam=10.0, qtd=3, comp=round((2 * (340 + 1200) + 140) / 10), forma=[(0, 0), (120, 0), (120, 34), (0, 34), (0, 0), (2, 2)], trechos=["120", "34", "", ""]),
                      dict(pos="N8", diam=10.0, qtd=3, comp=round((2 * (340 + 390) + 140) / 10), forma=[(0, 0), (34, 0), (34, 39), (0, 39), (0, 0), (2, 2)], trechos=["34", "39", "", ""])],
        insertos=[["TB-1", "Tubo Ø50×3,0 L=450 a prumo, passante, sem solda", 2, "pontas, a 150 da face"],
                  ["AL-1", "Laço de cordoalha Ø12,7 (2 pernas)", 2, "a 190 cm das pontas"],
                  ["NEO-1", "Neoprene 300×150×10 (furo Ø30)", 2, "sobre os consolos CP-MEZ"]],
        seg=SEG_VM,
        memoria=[["ELU flexão (laje h20+5, 500 kgf/m²)", "atende na seção pré-moldada (fase 1 + 2) — ND-LET-MC02"], ["ELS-F no infinito (fase 2 na seção composta)", f"σinf {f(SEG_VM['tensoes_infinito_MPa']['fibra_inf'],2)} MPa ≤ fctk,inf {f(SEG_VM['tensoes_infinito_MPa']['fctk_inf_C50'],2)} (I composta = {f(SEG_VM['secao_composta']['ganho_inercia'],2)} I)"],
                 ["Interface 2º estágio (NBR 9062:2017 6.3.5)", f"τsd {f(SEG_VM['interface']['tau_sd_total_MPa'],2)} ≤ τRd {f(SEG_VM['interface']['tau_Rd_MPa'],2)} MPa; N9 {f(SEG_VM['interface']['As_adotada_cm2_m'],1)} ≥ {f(SEG_VM['interface']['As_req_cm2_m'],1)} cm²/m"],
                 ["Dente 45 × 30 (MEF não linear)", "Vu 436 ≥ 1,06 Vd = 406 kN (FS 1,14)"], ["Cortante no apoio (Vd 383 kN)", "Ø8 c/10 nos 150 cm: 11,2 ≥ 8,2 cm²/m"],
                 ["Içamento (2 pontos a 1,9 m)", "σt ≤ fctk,j — sem fissura"]],
        notas=["Concreto C50; 9 cordoalhas CP-190 RB Ø12,7 (7 em y = 60 e 2 em y = 110 mm), todas aderentes. σpi = 1400 MPa; liberar com fckj ≥ 35 MPa.",
               "Dentes Gerber 45 × 30 nas duas pontas (seção I90: o dente da I70 foi reprovado no MEF), armadura N5/N6/N7/N8 (NBR 9062:2017 7.4 e PCI 5.6), verificados por MEF não linear; maciço de 120 cm nas pontas.",
               "Apoio 20 cm sobre o consolo CP-MEZ (assento = nível do piso − 70 cm: +2,45 e +5,85); pé-direito livre sob a viga = nível − 115 cm.",
               "2º ESTÁGIO (CORTE C-C, MC04): laje h20 apoia 10 cm na mesa (neoprene 10); enchimento 30 × 20 + capa 5 cm em C25 com tela Q138; N9 Ø8 c/15 salientes 17 cm (topo da viga rugoso, pente 5 mm) + N10 2 Ø10; negativas Ø10 c/25 L=150 nos alvéolos. Fase 1 (viga + laje + capa) na seção pré-moldada sem escora; fase 2 (revestimento + sobrecarga) na seção composta.",
               "Obra: lajes → topo da viga limpo e molhado → N10 e negativas → chavetas grauteadas → tela → enchimento + capa de uma vez → cura 7 dias, carregar só com fck ≥ 20 MPa. Calços de estoque fora dos N9.",
               "Pino PN-1 Ø20 do consolo entra no TB-1: grauteado numa ponta só de cada viga; a outra com graute flexível.",
               "Içar pelas 2 alças AL-1; estocar sobre 2 calços nas alças."])


if __name__ == "__main__":
    qual = sys.argv[1] if len(sys.argv) > 1 else "i110"
    prancha_viga(dados_i110() if qual == "i110" else dados_vm())
