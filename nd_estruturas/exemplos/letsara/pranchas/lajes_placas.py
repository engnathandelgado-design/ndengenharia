"""ND-LET-LA01 — lajes alveolares do mezanino (planta de lajes, seção, apoio, chavetas, capa) e
placas() abaixo é OBSOLETA (125 × 15, 4 Ø9,5): a CM01 e as placas saem do fechamento.py (125 × 10, 10 fios Ø6 — DEC-035). A1."""
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha

f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from geometria import Y_LIN, X_FACH, X_EIXO
Y2 = Y_LIN[1]
LARG = X_EIXO["E"]
M = lambda v: v * 1000


def notas_padrao(pr, XC, y, extra):
    pr.notas(XC, y, extra + ["Cotas de concreto em cm, chaparia em mm, níveis em m. Não medir no desenho."], 182)


# ================================================================== LA-01
def paineis_mez():
    """Painéis de um nível do mezanino: [(x0 mm, largura mm, marca)], quantidades nos 2 níveis, L_P (mm)."""
    L_P, B_P = round((Y2 - 0.20) * 1000), 1250                          # apoio 10 cm na mesa de cada VM (eixo ± 10 cm)
    N, B2, x_ini = 30, 700, 300                                          # 30 LA-01 + 2 LA-02 de 70 cm (pontas A e E)
    pn = [(x_ini, B2, "LA-02")] + [(x_ini + B2 + k * B_P, B_P, "LA-01") for k in range(N)] + [(x_ini + B2 + N * B_P, B2, "LA-02")]
    PIL = [M(x) for x in X_FACH[1:4]]                                    # P3/P4/P5 (L1) e P8/P8A/P8B (L2): 40 em x → recorte nas pontas
    rec = lambda x0, b: any(x0 < xp + 225 and x0 + b > xp - 225 for xp in PIL)
    pn = [(x0, b, (mk + "R") if rec(x0, b) else mk) for x0, b, mk in pn]
    qt = {}
    for _, b, mk in pn:
        qt[mk] = qt.get(mk, 0) + 2
    return pn, qt, L_P


def lajes():
    """rev07 (21/10/2026): FÔRMA em cima, ARMAÇÃO/PROTENSÃO embaixo (padrão usina). Dimensionamento completo em
    calc_laje_alveolar.py → laje_alveolar.json (LP20 1245 × 200, 6 alvéolos Ø152 no passo 198, 7 Ø12,7 — uma por nervura)."""
    import json
    LJ = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/laje_alveolar.json", encoding="utf-8"))
    G_ = LJ["secao"]
    paineis, qt, L_P = paineis_mez()
    B_P, B2, N = 1250, 700, 30
    B_N, H_P, N_AL, D_AL, PAS = round(G_["b"] * 1000), round(G_["h"] * 1000), G_["n_alveolos"], round(G_["d_alveolo"] * 1000), G_["passo"] * 1000
    XAL = [round(B_N / 2 + (k - (N_AL - 1) / 2) * PAS, 3) for k in range(N_AL)]   # centro dos alvéolos (mm, da borda esquerda)
    CRD = [(B_N / 2 + c["x_mm"], c["y_mm"], c["diam"]) for c in LJ["cordoalhas"]]
    Y_C, N_C, SIG_PI = CRD[0][1], len(CRD), LJ["sig_pi"]
    F_C = LJ["cordoalhas"][0]["F_macaco_kN"]
    LBPT, FCKJ, IC = LJ["lbpt_m"], LJ["fckj"], LJ["icamento"]
    FL = LJ["flechas_mm"]
    PRE = LJ["LA01R"][LJ["LA01R"]["adotado"]]["alveolos_preenchidos"]
    PESO1 = G_["peso_kN_m2"] * G_["b"] * L_P / 1000
    pr = Prancha("A1", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                            conteudo="LAJES ALVEOLARES DO MEZANINO (h20 + CAPA 5) — FÔRMA (PAGINAÇÃO, SEÇÃO, RECORTE, APOIO) E ARMAÇÃO (PROTENSÃO, CAPA, NEGATIVA)",
                            desenho="ND-LET-LA01", folha="01/01", fase="PARA APROVAÇÃO", marca="LA-01", qtd=qt.get("LA-01", 0), peso=f(PESO1, 1), volume=f(G_["A_m2"] * L_P / 1000, 2), rev="01"))
    pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL")
    pr.revisao("01", "12/10/2026", "GEOMETRIA DO R01 (VÃO 9,65 m); 8 Ø12,7; LA-02 70 cm NAS PONTAS; RECORTES NOS PILARES")
    pr.revisao("04", "16/10/2026", "NBR 9062: APOIO NA ABA DA VM EM MEIO VASO; 2º ESTÁGIO E CAPA C30 DE OBRA")
    pr.revisao("07", "21/10/2026", "FÔRMA E ARMAÇÃO NA MESMA FOLHA (PADRÃO USINA)")
    Q = pr.quadro
    XC = Q[2] - 190
    pr.cabecalho_peca("LA-01", f"LAJE ALVEOLAR h20 + CAPA 5 — LA-01 (125 × {L_P/10:.0f} cm) · LA-01R · LA-02 (70 × {L_P/10:.0f} cm)",
                      f"mezanino, níveis +3,15 e +6,55; vão 9,65 m entre as VM (linhas 1 e 2); {sum(qt.values())} painéis (2 níveis) · PESO LA-01 {f(PESO1/10, 2)} t · "
                      f"{N_C} cord. Ø12,7 CP-190 RB (uma por nervura), {f(F_C)} kN por cordoalha no macaco", largura=XC - Q[0] - 10)
    Y_SPLIT = Q[1] + 255                                                            # divisa FÔRMA (em cima) / ARMAÇÃO (embaixo)
    pr.linha((Q[0] + 4, Y_SPLIT), (XC - 8, Y_SPLIT), "CARIMBO_FINO")
    pr.texto(Q[0] + 8, Q[3] - 40, "FÔRMA", "titulo", "TITULO")
    pr.texto(Q[0] + 8, Y_SPLIT - 8, "ARMAÇÃO E PROTENSÃO", "titulo", "TITULO")
    # ================= FÔRMA
    v = pr.vista("PLANTA", (Q[0] + 45, Q[3] - 175), 100, titulo="PLANTA DE PAGINAÇÃO — NÍVEIS +3,15 E +6,55 (IGUAIS)",
                 subtitulo="painéis de A para E; LA-02 (70 cm) nas pontas; R = recorte nas pontas junto aos pilares", unidade="cm")
    for x in X_FACH:
        v.eixo((M(x), -1500), (M(x), M(Y2) + 1500), 500)
        v.circulo((M(x), M(Y2) + 2300), 500, "VISTA"); v.texto((M(x), M(Y2) + 2300), "ABCDE"[X_FACH.index(x)], "nota", "MIDDLE_CENTER")
    for k, y in ((1, 0.0), (2, Y2)):
        v.eixo((-1500, M(y)), (M(LARG) + 800, M(y)), 500)
        v.circulo((-2300, M(y)), 500, "VISTA"); v.texto((-2300, M(y)), str(k), "nota", "MIDDLE_CENTER")
    for y in (0.0, Y2):
        v.ret(300, M(y) - 200, M(LARG) - 600, 400, "VISTA")
    for i, (x0, b, mk) in enumerate(paineis):
        v.ret(x0, 100, b - 10, L_P, "VISTA" if mk == "LA-01" else "CORTADO")
        if mk != "LA-01" or i % 4 == 1:
            xt = x0 + b / 2
            if any(abs(xt - M(xx)) < 300 for xx in X_FACH):                       # rótulo fora da linha de eixo
                xt = x0 + b * 0.25
            v.texto((xt, M(Y2 / 2)), mk, "min", "MIDDLE_CENTER", rot=90)
    for x, bx, by in [(0, 600, 400)] + [(M(xx), 400, 600) for xx in X_FACH[1:4]] + [(M(LARG), 600, 400)]:
        for y in (0.0, Y2):
            v.ret(x - bx / 2, M(y) - by / 2, bx, by, "CORTADO")
    v.cota_h([M(x) for x in X_FACH], -2000, -8)
    v.cota_h([300, 300 + B2, 300 + B2 + B_P], M(Y2) + 300, 8, total=False)
    v.cota_v([100, 100 + L_P], M(LARG) + 1500, 8, total=False)
    v.cota_v([0, M(Y2)], M(LARG) + 1500, 16, total=False)
    v.chamada((M(X_FACH[3]) + 800, 100), (10, -14), "apoio 10 cm sobre a aba da VM (neoprene em fita 10 mm)")
    v.chamada((M(X_FACH[1]) + 200, 100), (6, -8), "recorte 45 × 20 cm na ponta (DETALHE 2)")
    v.marcador_detalhe((300 + B2 + 3 * B_P, 100), 600, 1, ang=-45, dist=8)
    v.marcador_detalhe((M(X_FACH[1]), M(Y2) - 100), 600, 2, ang=45, dist=8)
    v.marcador_corte((300 + B2 + 19 * B_P + B_P / 2, -600), (300 + B2 + 19 * B_P + B_P / 2, M(Y2) + 600), "A", lado=1)
    # seção de fôrma do painel (1:10)
    s = pr.vista("CORTE A-A", (Q[0] + 50, Q[3] - 268), 10, titulo="CORTE A-A — SEÇÃO DE FÔRMA DO PAINEL LA-01",
                 subtitulo=f"alveolar h20 ({N_AL} alvéolos Ø{D_AL / 10:g} no passo {PAS / 10:g}; nervuras {G_['nervuras_mm'][1] / 10:g} e bordas {G_['nervuras_mm'][0] / 10:g}) + capa 5".replace(".", ","), unidade="cm")
    s.ret(0, 0, B_N, H_P, "CORTADO")
    for xa in XAL:
        s.circulo((xa, H_P / 2), D_AL / 2, "VISTA")
    s.hachura([(0, H_P), (B_P, H_P), (B_P, H_P + 50), (0, H_P + 50)], "AR-CONC", 0.02); s.linha((0, H_P + 50), (B_P, H_P + 50), "VISTA")
    s.poli([(0, H_P), (-25, 150), (-25, 60), (0, 40)], "VISTA"); s.poli([(B_N, H_P), (B_N + 25, 150), (B_N + 25, 60), (B_N, 40)], "VISTA")
    s.cota_h([0] + XAL + [B_N], 0, -8, total=True)
    s.cota_h([0, B_P], H_P + 50, 10)
    s.cota_v([0, H_P / 2, H_P, H_P + 50], B_N + 25, 10, total=True)
    s.chamada((B_N + 25, 60), (24, -16), "chaveta grauteada (graute ≥ 30 MPa)")
    s.chamada((XAL[1], H_P / 2 + D_AL / 2), (6, 22), f"alvéolo Ø{D_AL / 10:g}".replace(".", ","))
    s.chamada((B_P / 2, H_P + 25), (10, 12), "capa 5 cm C30 de obra")
    # detalhe 2: recorte na ponta junto ao pilar (planta 1:20)
    r2 = pr.vista("DETALHE 2", (Q[0] + 261, Q[3] - 291), 25, titulo="DETALHE 2 — RECORTE NA PONTA (LA-01R)",
                  subtitulo="planta; pilar 40 × 60 na linha da VM; folga 2,5 cm; corta 3 nervuras: ficam 4 Ø12,7 na ponta", unidade="cm")
    r2.linha((0, 0), (0, 1200), "VISTA"); r2.linha((B_P - 10, 1200), (B_P - 10, 0), "VISTA")
    r2.interrupcao((0, 0), (B_P - 10, 0))
    xr0 = (B_P - 10) / 2 - 225
    r2.poli([(0, 1200), (xr0, 1200), (xr0, 1000), (xr0 + 450, 1000), (xr0 + 450, 1200), (B_P - 10, 1200)], "CORTADO")
    pil = [(xr0 + 25, 1025), (xr0 + 425, 1025), (xr0 + 425, 1300), (xr0 + 25, 1300)]
    r2.poli(pil, "VISTA", fechada=True); r2.hachura(pil, "AR-CONC", 0.03)
    r2.cota_h([0, xr0, xr0 + 450, B_P - 10], 1200, 16, total=True)
    r2.cota_v([1000, 1200], B_P - 10, 10, total=False)
    r2.interrupcao((xr0 + 25, 1300), (xr0 + 425, 1300))
    r2.chamada((xr0 + 225, 1250), (30, 6), "pilar 40 × 60")
    r2.chamada((xr0 + 450, 1100), (20, -12), "recorte 45 × 20 de fábrica")
    r2.chamada(((B_P - 10) / 2, 300), (30, -14), "posição do recorte pela planta de paginação")
    for k in PRE:                                                                   # alvéolos preenchidos 60 cm junto ao recorte (cortante na ponta)
        xa = XAL[k - 1]
        fp = [(xa - D_AL / 2, 600), (xa + D_AL / 2, 600), (xa + D_AL / 2, 1200), (xa - D_AL / 2, 1200)]
        r2.poli(fp, "OCULTA", fechada=True); r2.hachura(fp, "ANSI31", 0.8)
    if PRE:
        r2.cota_v([600, 1200], XAL[PRE[1] - 1] + D_AL / 2, 6, total=False)
        r2.chamada((XAL[PRE[1] - 1], 700), (22, -16), f"alvéolos {PRE[0]} e {PRE[1]} preenchidos 60 cm na fábrica")
    # detalhe 1: apoio na VM (1:10)
    d = pr.vista("DETALHE 1", (Q[0] + 470, Q[3] - 255), 20, titulo="DETALHE 1 — APOIO NA VIGA VM (MEIO VASO)",
                 subtitulo="laje sobre a aba da VM; 2º estágio sobre a alma, concretado com a capa", unidade="cm")
    ext = [(0, -500), (250, -500), (250, -200), (400, -200), (400, 0), (0, 0)]
    d.poli(ext, "CORTADO", fechada=True); d.hachura(ext, "AR-CONC", 0.03); d.interrupcao((-20, -500), (270, -500))
    e2 = [(0, 0), (300, 0), (300, 210), (0, 210)]
    d.poli(e2, "OCULTA", fechada=True); d.hachura(e2, "ANSI31", 0.6)
    d.ret(300, 10, 700, 200, "CORTADO"); d.ret(300, 0, 100, 10, "METALICA")
    d.circulo((450, 110), 76, "VISTA"); d.circulo((660, 110), 76, "VISTA"); d.interrupcao((1000, 0), (1000, 270))
    d.hachura([(0, 210), (1000, 210), (1000, 260), (0, 260)], "ANSI31", 0.6); d.linha((0, 260), (1000, 260), "VISTA")
    d.cota_h([0, 250, 300, 400], -500, -10, total=False); d.cota_v([-200, 0, 210, 260], 1000, 10, total=True)
    d.chamada((350, 5), (14, -16), "apoio 10 cm na aba + neoprene em fita 10")
    d.chamada((150, 120), (-26, 20), "2º estágio C30 (obra)")
    d.chamada((600, 235), (10, 14), "capa 5 cm C30")
    d.chamada((125, -450), (-20, -10), "VM meio vaso (ND-LET-VM01)")
    # ================= ARMAÇÃO E PROTENSÃO
    a = pr.vista("SEÇÃO DE ARMAÇÃO", (Q[0] + 50, Q[1] + 175), 5, titulo="SEÇÃO DE ARMAÇÃO — LA-01",
                 subtitulo=f"{N_C} cordoalhas Ø12,7 CP-190 RB aderentes, uma por nervura, eixo a {Y_C / 10:g} cm do fundo; capa com tela Q138".replace(".", ","), unidade="cm")
    a.ret(0, 0, B_N, H_P, "CORTADO")
    for xa in XAL:
        a.circulo((xa, H_P / 2), D_AL / 2, "VISTA")
    for xc, yc_, dm in CRD:                                                          # posição real de cada cordoalha
        a.ponto_barra((xc, yc_), 12.7 if dm == "12.7" else 9.5, "ARM_PROT")
    a.hachura([(0, H_P), (B_P, H_P), (B_P, H_P + 50), (0, H_P + 50)], "AR-CONC", 0.02); a.linha((0, H_P + 50), (B_P, H_P + 50), "VISTA")
    a.linha((25, H_P + 25), (B_P - 25, H_P + 25), "ARMADURA")
    a.cota_v([0, Y_C, H_P, H_P + 25, H_P + 50], B_N + 10, 12, total=False)
    a.cota_h([0] + [round(x, 3) for x, _, _ in CRD] + [B_N], 0, -10, total=True)
    a.chamada((CRD[4][0], Y_C), (20, -26), f"C1 — {N_C} Ø12,7 CP-190 RB, eixo no meio de cada nervura, a {Y_C / 10:g} cm do fundo".replace(".", ","))
    a.chamada((B_P * 0.7, H_P + 25), (14, 12), "tela Q138 a meia altura da capa (2,5 cm)")
    a.texto((0, -190), f"Protensão: σpi = {SIG_PI:.0f} MPa → {f(F_C)} kN por cordoalha no macaco (todas aderentes, sem isolamento); liberação gradual com fckj ≥ {FCKJ:.0f} MPa; transferência lbpt = {LBPT * 100:.0f} cm.".replace(".0f", ""), "nota")
    # detalhe 3: negativa e alvéolos preenchidos sobre o apoio (corte longitudinal 1:10)
    n3 = pr.vista("DETALHE 3", (Q[0] + 75, Q[1] + 75), 10, titulo="DETALHE 3 — NEGATIVA N1 E ALVÉOLOS NA PONTA (CORTE LONGITUDINAL)",
                  subtitulo="2 Ø10 por painel em cada apoio, dentro da capa (construtiva — laje biapoiada); alvéolos tampados 20 cm na ponta", unidade="cm")
    lam = [(0, 0), (2300, 0), (2300, H_P), (0, H_P)]
    n3.poli(lam, "VISTA", fechada=True); n3.interrupcao((2300, 0), (2300, H_P + 50))
    n3.ret(0, H_P / 2 - D_AL / 2, 200, D_AL, "OCULTA"); n3.hachura([(0, H_P / 2 - D_AL / 2), (200, H_P / 2 - D_AL / 2), (200, H_P / 2 + D_AL / 2), (0, H_P / 2 + D_AL / 2)], "ANSI31", 0.6)
    n3.linha((200, H_P / 2 - D_AL / 2), (2300, H_P / 2 - D_AL / 2), "OCULTA"); n3.linha((200, H_P / 2 + D_AL / 2), (2300, H_P / 2 + D_AL / 2), "OCULTA")
    n3.hachura([(-300, H_P), (2300, H_P), (2300, H_P + 50), (-300, H_P + 50)], "AR-CONC", 0.02); n3.linha((-300, H_P + 50), (2300, H_P + 50), "VISTA")
    n3.linha((-300, 0), (-300, H_P + 50), "VISTA")
    n3.linha((10, Y_C), (2290, Y_C), "ARM_PROT")
    n3.barra([(-200, H_P + 30), (1800, H_P + 30)], "N1", 2, 10, comp_cm=200, ponto_rotulo=(1200, H_P + 30), desloc=(10, 12))
    n3.linha((-280, H_P + 20), (2280, H_P + 20), "ARM_TRANSV")
    n3.cota_h([-300, 0, 200, 1800], 0, -10, total=False)
    n3.cota_v([0, Y_C, H_P, H_P + 50], 2300, 10, total=False)
    n3.chamada((100, H_P / 2), (14, 3), "alvéolo tampado 20 cm (na fábrica)")
    n3.chamada((1900, Y_C), (14, -12), f"C1 — {N_C} Ø12,7 aderentes até a ponta")
    n3.chamada((-150, H_P + 25), (-14, 14), "2º estágio / apoio na VM")
    n3.chamada((2000, H_P + 20), (14, 8), "tela Q138 (capa)")
    # barras explodidas + tabela (por painel)
    br = [dict(pos="N1", diam=10.0, qtd=4, comp=200, trechos=["200"])]
    tq = pr.tabela_croqui(Q[0] + 380, Y_SPLIT - 18, br, h_lin=10.0)
    yy = pr.tabela(Q[0] + 380, tq["y_base"] - 4, "PROTENSÃO — POR PAINEL LA-01 (LA-02: 4 Ø12,7; LA-01R: ficam 4 na ponta recortada)",
                   ["POS", "Ø (mm)", "QUANT", "y (mm)", "σpi (MPa)", "F MACACO (kN)", "ISOLAMENTO"],
                   [["C1", "12,7", N_C, Y_C, f"{SIG_PI:.0f}", f(F_C), "não"]], [14, 18, 18, 18, 24, 28, 34])
    yy = pr.tabela(Q[0] + 380, yy - 4, "PRODUÇÃO E MANUSEIO", ["ITEM", "VALOR"],
                   [["concreto / liberação", f"C50 · fckj ≥ {FCKJ:.0f} MPa, liberação gradual (macaco)"], ["transferência", f"lbpt = {LBPT * 100:.0f} cm"],
                    ["içamento", f"garra nas 2 pontas a {IC['ponto_m'] * 100:.0f} cm · {f(IC['F_por_garra_d_kN'])} kN de cálculo por garra · {f(IC['peso_t'], 2)} t"],
                    ["estocagem / transporte", f"2 calços alinhados a {IC['ponto_m'] * 100:.0f} cm das pontas, até 8 painéis"],
                    ["contraflecha estimada", f"{f(FL['contraflecha_fabricacao'])} mm na liberação · {f(FL['contraflecha_montagem'])} mm na montagem"]], [40, 104])
    yy = pr.tabela(Q[0] + 380, yy - 4, "TELAS DA CAPA (OBRA) — POR PAINEL", ["TELA", "DESCRIÇÃO", "ÁREA (m²)"],
                   [["Q138", "Ø4,2 c/10 × c/10, CA-60, a 2,5 cm do topo da capa", f(1.25 * L_P / 1000, 2)]], [16, 104, 24])
    pr.legenda_armadura(Q[0] + 380, yy - 4, True)
    pr.imagem(Q[0] + 487, Q[3] - 140, Q[0] + 612, Q[3] - 58, "/home/claude/letsara/pranchas/img/iso_la01.png",
              titulo="ISOMÉTRICO — LA-01R", subtitulo="trecho de 3,0 m: 6 alvéolos, ponta fechada 20 cm, recorte 45 × 20 e alvéolos 2 e 5 cheios")
    # tabelas da coluna direita
    y = Q[3] - 6
    y = pr.tabela(XC, y, "MARCAS — LAJES ALVEOLARES (2 NÍVEIS)", ["MARCA", "DESCRIÇÃO", "QT", "PESO (t)", "OBS."],
                  [[mk, f"{(B_P if mk.startswith('LA-01') else B2)/10:.0f} × {L_P/10:.0f} × 20, {N_C if mk.startswith('LA-01') else 4} Ø12,7", qt[mk],
                    f((B_N if mk.startswith('LA-01') else B2) / 1000 * L_P / 1000 * G_["peso_kN_m2"] / 10, 2),
                    f"recorte 45×20; alv. {PRE[0]} e {PRE[1]} cheios" if mk.endswith("R") else ("corte longit. do LA-01" if mk.startswith("LA-02") else "-")]
                   for mk in sorted(qt)], [18, 70, 12, 20, 62])
    qd = [["VÃO", f"{L_P/10 - 10:.0f} cm (entre centros de apoio)", "APOIO", "10 cm + neoprene"], ["SOBRECARGA", "500 kgf/m² + revest. 100", "CAPA", "5 cm C30, tela Q138"],
          ["h TOTAL", "25 cm", "ESCORAMENTO", "nenhum"], ["PAINÉIS", f"{sum(qt.values())} (2 níveis)", "CONTRAFLECHA", f"≈ {f(FL['contraflecha_montagem'], 0)} mm (montagem)"]]
    y = pr.tabela(XC, y - 4, "QUADRO DAS LAJES", ["ITEM", "VALOR", "ITEM", "VALOR"], qd, [30, 62, 30, 60])
    CG = LJ["cargas"]
    notas_padrao(pr, XC, y - 4, [f"Cargas consideradas: peso próprio {f(CG['g1'], 2)} kN/m², capa + rejunte {f(CG['capa_rejunte'], 2)} kN/m², revestimento {f(CG['revestimento'])} kN/m², sobrecarga {f(CG['sobrecarga'])} kN/m² (escritório); montagem: capa fresca + {f(CG['montagem'])} kN/m², sem escoramento. Vão de cálculo 9,35 m, laje biapoiada nas VM.",
                                 f"Concreto C50 da laje (fckj ≥ {FCKJ:.0f} MPa na liberação), capa C30, cordoalhas CP-190 RB; CAA I (ambiente interno seco e revestido), cobrimento da cordoalha 3,4 cm (eixo a 4 cm). Seção do painel 1245 × 200 com {N_AL} alvéolos Ø15,2 no passo {f(PAS / 10)} cm: com outra seção de extrusora a protensão tem de ser refeita.".replace(".0f", ""),
                                 f"LA-01R: o recorte 45 × 20 corta 3 nervuras e 3 cordoalhas na ponta; preencher na fábrica os alvéolos {PRE[0]} e {PRE[1]} nos 60 cm junto ao recorte (concreto da laje, vibrado) — DETALHE 2.",
                                 "Painéis apoiados 10 cm sobre a aba das VM em meio vaso, com neoprene em fita de 10 mm; chavetas grauteadas; 2º estágio sobre a alma da VM e capa de 5 cm (C30, tela Q138) concretados juntos, por quem executa a capa, após a montagem de todo o nível. Lajes e vigas sem escoramento; montar as lajes só depois de concretar as pontas das VM (junta VM × pilar) dos dois lados, com fcj ≥ 20 MPa (DEC-039).",
                                 "Armadura negativa sobre os apoios: N1 2 Ø10 por painel, L = 200 cm, dentro da capa (DETALHE 3); alvéolos fechados na fábrica nos 20 cm das pontas para o graute não entrar.",
                                 f"Içamento só por garra mecânica nas 2 pontas (a {IC['ponto_m'] * 100:.0f} cm) com balancim e cabos verticais; não usar alça de CA-50. Desforma, içamento e transporte com fcj ≥ {FCKJ:.0f} MPa; estocar sobre 2 calços alinhados a {IC['ponto_m'] * 100:.0f} cm das pontas, no máximo 8 painéis por pilha.".replace(".0f", "")])
    avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-LA01")
    print("LA01", len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos", [a for a in avisos if a[0] == "ERRO" or "sobrep" in a[1] or "cruza" in a[1]])


# ================================================================== CM-01
def placas():
    H_PL, E_PL = 1250, 150
    vaos = [(Y_LIN[i + 1] - Y_LIN[i]) for i in range(8)]
    marcas = {}
    for i, vao in enumerate(vaos):
        Lp = round(vao * 1000 - 10)
        marcas.setdefault(Lp, []).append(f"L{i+1}–L{i+2}")
    vaos_f = [(X_FACH[i + 1] - X_FACH[i]) + (0.4 if i in (0, 3) else 0.0) for i in range(4)]
    for i, vao in enumerate(vaos_f):
        Lp = round(vao * 1000 - 10)
        marcas.setdefault(Lp, []).append(f"{'ABCDE'[i]}–{'ABCDE'[i+1]} (fach.)")
    lista = sorted(marcas.items(), key=lambda t: -t[0])
    MK = {Lp: f"CM-0{k+1}" for k, (Lp, _) in enumerate(lista)}
    L0 = lista[0][0]
    peso = lambda Lp: 1.25 * 0.15 * Lp / 1000 * 25
    pr = Prancha("A1", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                            conteudo="PLACAS DE FECHAMENTO PROTENDIDAS CM-01 A CM-08 (125 × 15) — ELEVAÇÃO DE MONTAGEM, SEÇÃO, INSERTOS E LIGAÇÃO COM OS PILARES",
                            desenho="ND-LET-CM01", folha="01/01", fase="PARA APROVAÇÃO", marca="CM-01", qtd=16, peso=f(peso(L0), 1), volume=f(1.25 * 0.15 * L0 / 1000, 2)))
    pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL")
    Q = pr.quadro
    XC = Q[2] - 190
    pr.ret(Q[0] + 4, Q[3] - 30, Q[0] + 520, Q[3] - 4, "CARIMBO")
    pr.texto(Q[0] + 10, Q[3] - 24, "CM-01", "grande", "TITULO")
    pr.texto(Q[0] + 62, Q[3] - 24, f"PLACA DE FECHAMENTO PROTENDIDA 125 × 15 — CM-01 (L = {L0/10:.0f} cm) · CM-02 A CM-08", "titulo", "TITULO")
    pr.texto(Q[0] + 10, Q[3] - 14, f"8 fiadas de 125 cm (±0,00 a +10,00) por fora dos pilares; 4 cord. Ø9,5 CP-190; fixação nos IP-01 dos pilares   ·   PESO CM-01 {f(peso(L0)/10, 2)} t   ·   192 placas", "nota", "TEXTO")
    # elevação de montagem da fachada eixo A (1:200)
    v = pr.vista("ELEVAÇÃO", (Q[0] + 40, Q[3] - 150), 200, titulo="ELEVAÇÃO DE MONTAGEM — FACHADA EIXO A (EIXO E SIMÉTRICO)", subtitulo="8 fiadas; marcas por vão; juntas de 10 mm", unidade="cm")
    for i, y in enumerate(Y_LIN):
        v.ret(M(y) - 200, -1000, 400, 11000, "CORTADO")
        v.texto((M(y), 10300), str(i + 1), "nota", "BOTTOM_CENTER")
    for i, vao in enumerate(vaos):
        Lp = round(vao * 1000 - 10)
        for k in range(8):
            v.ret(M(Y_LIN[i]) + 5, k * H_PL, Lp, H_PL - 10, "VISTA")
        v.texto((M(Y_LIN[i]) + vao * 500, 4 * H_PL + 300), MK[Lp], "min", "BOTTOM_CENTER")
    v.linha((-1500, 0), (M(76.81) + 1500, 0), "TERRENO")
    v.cota_h([M(y) for y in Y_LIN], -1000, -8)
    v.cota_v([0, H_PL, 2 * H_PL, 8 * H_PL], M(76.81) + 500, 8, total=False)
    v.chamada((M(Y_LIN[2]), 7 * H_PL + 600), (8, 14), "IP-01 no pilar a cada fiada (a 10 cm abaixo do topo da placa)")
    v.marcador_detalhe((M(Y_LIN[1]), 3 * H_PL), 900, 1, ang=30, dist=8)
    # seção da placa 1:10 (cm) e insertos
    s = pr.vista("SEÇÃO", (Q[0] + 60, Q[3] - 345), 10, titulo="SEÇÃO DA PLACA", subtitulo="protendida; 2 + 2 cord. Ø9,5", unidade="cm")
    s.ret(0, 0, E_PL, H_PL, "CORTADO"); s.hachura([(0, 0), (E_PL, 0), (E_PL, H_PL), (0, H_PL)], "AR-CONC", 0.03)
    for x in (40, 110):
        for yy in (200, 1050):
            s.ponto_barra((x, yy), 9.5)
    s.poli([(30, 30), (120, 30), (120, 1220), (30, 1220)], "ARMADURA", fechada=True)
    s.poli([(0, H_PL), (20, H_PL - 20), (E_PL - 20, H_PL - 20), (E_PL, H_PL)], "VISTA"); s.poli([(0, 0), (20, 20), (E_PL - 20, 20), (E_PL, 0)], "VISTA")
    s.cota_h([0, 40, 110, E_PL], 0, -8, total=True); s.cota_v([0, 200, 1050, H_PL], E_PL, 10, total=False)
    s.chamada((110, 1050), (12, -6), "C1 — 4 cord. Ø9,5 CP-190 RB (2 + 2), 56 kN cada")
    s.chamada((120, 600), (12, 0), "tela Q92 nas duas faces + estribo de borda Ø6,3 c/20")
    s.chamada((75, H_PL), (12, 8), "encaixe macho-fêmea 2 cm (junta de 10 mm c/ selante)")
    # detalhe ligação com o pilar 1:10 (planta)
    d = pr.vista("DETALHE 1", (Q[0] + 300, Q[3] - 290), 10, titulo="DETALHE 1 — LIGAÇÃO PLACA × PILAR (PLANTA)", subtitulo="cantoneira soldada em obra ao IP-01 do pilar e ao CH-P1 da placa", unidade="cm")
    d.ret(-300, -600, 600, 400, "CORTADO"); d.hachura([(-300, -600), (300, -600), (300, -200), (-300, -200)], "AR-CONC", 0.03)
    d.chapa(-75, -200, 150, 9.5)                                                           # IP-01 na face externa (x−)... aqui face externa para cima
    for sg in (-1, 1):
        d.ret(sg * 305 if sg > 0 else -305 - 1200, -140, 1200, 150, "CORTADO")
        d.chapa(sg * 305 if sg > 0 else -305 - 100, -140 - 9.5, 100, 9.5)
    d.chapa(-75, -190.5, 150, 9.5)
    d.chapa(-60, -190.5, 63, 6.3); d.chapa(-60, -190.5, 6.3, 63)
    d.chapa(60 - 6.3, -190.5, 6.3, 63); d.chapa(-3, -190.5, 63, 6.3)
    d.cota_h([-300, 300], -600, -8); d.cota_h([-305 - 100, -305, 305, 405], -140, 10, total=False); d.cota_v([-200, -140, 10], -305 - 1200, -8, total=False)
    d.chamada((0, -195), (14, -14), "IP-01 chapa 150×150×9,5 + 2 pinos Ø12,5 (pilar)")
    d.chamada((60, -160), (16, 24), "L 63×63×6,3 L=120, soldada ao IP-01 e ao CH-P1 (solda 5 mm, 100 mm)")
    d.chamada((355, -149), (12, -10), "CH-P1 100×150×9,5 + 2 pinos Ø12,5 (na placa, 2 por ponta)")
    d.chamada((-305, 0), (-10, 8), "placa CM 125 × 15"); d.chamada((305, 5), (10, 30), "junta 10 mm (selante PU)")
    # tabelas
    y = Q[3] - 6
    linhas = [[MK[Lp], ", ".join(pos), 8 * len(pos) * (2 if "fach" not in pos[0] else 2), f"{Lp/10:.0f}", f(peso(Lp) / 10, 2)] for Lp, pos in lista]
    y = pr.tabela(XC, y, "MARCAS — PLACAS DE FECHAMENTO 125 × 15 (8 fiadas)", ["MARCA", "VÃOS", "QT", "L (cm)", "PESO (t)"], linhas, [18, 70, 12, 22, 24], h_lin=6.0)
    ins = [["CH-P1", "Chapa 100×150×9,5 + 2 pinos Ø12,5 c/ cabeça", 4, "face interna, 2 por ponta (a 15 e 110 cm)"], ["CT-P", "Cantoneira L 63×63×6,3 L=120 (solda em obra)", 4, "IP-01 × CH-P1"],
           ["AL-P", "Alça laço cordoalha Ø9,5", 2, "topo, a L/5 das pontas"]]
    y = pr.tabela(XC, y - 4, "INSERTOS POR PLACA — dimensões em mm", ["MARCA", "DESCRIÇÃO", "QT", "POSIÇÃO"], ins, [16, 100, 10, 56])
    mem = [["Vento (q 0,87 kN/m², Cpe 1,0)", "M = 12,7 kN·m por placa"], ["σ no bordo (P/A ± M/W)", "1,18 ± 2,7 → tração 1,5 ≤ fctk,inf 2,9 MPa"],
           ["Flecha (I bruto, 9,65 m)", "≈ 19 mm ≤ L/250 = 39 mm"], ["Fixação (4 cantoneiras)", "R = 2,6 kN por ponto — M12 / solda 5 mm"]]
    y = pr.tabela(XC, y - 4, "MEMÓRIA RESUMIDA (NBR 6118 / NBR 6123)", ["VERIFICAÇÃO", "RESULTADO"], mem, [70, 112])
    notas_padrao(pr, XC, y - 4, ["Placas protendidas 125 × 15 (C40, fckj 25 MPa) com 4 cordoalhas Ø9,5 (2 + 2) — vento nos dois sentidos; encaixe macho-fêmea de 2 cm entre fiadas; junta 10 mm selada.",
                                 "Fixação: em cada ponta da placa, 2 cantoneiras L 63×6,3 soldadas em obra ao IP-01 do pilar e ao CH-P1 da placa (acerta tolerâncias de ±10 mm); primeira fiada apoiada na viga baldrame (projeto de fundações).",
                                 "Montagem após a cobertura: de baixo para cima, por vão; conferir prumo da face externa a cada fiada.",
                                 "Se o fabricante preferir placa armada (sem protensão), a espessura passa a 15 cm com 2 telas Q196 e 4 Ø10 longitudinais — reapresentar para verificação."])
    avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-CM01")
    print("CM01", len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos", [a for a in avisos if a[0] == "ERRO" or "sobrep" in a[1]])


if __name__ == "__main__":
    lajes()
    # placas() — substituída por fechamento.py (CM01 rev 02 + PP00 + pranchas por vista)
