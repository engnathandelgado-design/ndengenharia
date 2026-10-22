"""ND-LET-PP06 — DEC-044 (22/10/2026): o I130 do eixo C atravessa as paredes internas G (linha 2) e C (linha 4).
(1) Placas recortadas PP-05RE/RD (G-17/G-11) e PP-08RE/RD (C-17/C-11): recorte 260 × 1130 na ponta do eixo C em volta do consolo
    CP-I130 e do nariz do I130; console CS-1 dessa ponta a 330 da ponta (nicho NC-1 de 260 a 400); toco 260 × 120 embaixo.
(2) CE-1L 840 × 330 × 12,5 com asas de 220 além das faces do pilar (P8A e P11, fiada +6,25) para esse console.
(3) CS-1C (calço 100: cantos e P1B/P2B) e CS-1D (calço 75: P10 da parede C): caixa 120 × 330 × e soldada na fábrica nas costas do
    CS-1, fundo soldado na CE-1 na obra — nos pilares cuja face fica atrás do plano dos consoles.
Fonte: placas.json (recorte), fixacao_placas.json (CE1L, calcos), fechamento.py (peças, posições). Concreto em cm, metálica em mm."""
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
import json
import fechamento as FCH
import geo_fixacao as GF
import iso_nd as I
from prancha_nd import Prancha

f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
gg = lambda v: f"{v:g}".replace(".", ",")
PLJ = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/placas.json"))
REC = PLJ["recorte"]
FXJ = GF.FX
CEL, CAL = FXJ["CE1L"], FXJ["calcos"]
PP01 = json.load(open("/home/claude/letsara/pranchas/pp01.json"))["n"]
N, C, T = GF.N, GF.C, GF.T
H_PL, E_PL, RB, RZ, XCS = FCH.H_PL, FCH.E_PL, FCH.REC_B, FCH.REC_Z0, FCH.X_CS_R
NC_B, NC_H, NC_P, Z_NC = FCH.NC_B, FCH.NC_H, FCH.NC_P, FCH.Z_NC
TCE = GF.TCE
recs = FCH.RECORTADAS
tipos = sorted(set(FCH.TIPO[p["Lk"]] for _, p in recs))
n_c, n_d = PP01["CS1C"], PP01["CS1D"]

pr = Prancha("A1", dict(cliente=FCH.CLIENTE, obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="PLACAS RECORTADAS NO I130 (PAREDES G E C), CHAPA DE ESPERA CE-1L E CONSOLES COM CALÇO CS-1C / CS-1D (DEC-044)",
                        desenho="ND-LET-PP06", folha="01/01", fase="PARA APROVAÇÃO", rev="08"))
pr.revisao("08", "22/10/2026", "EMISSÃO: RECORTE DAS PLACAS NO I130 DO EIXO C; CE-1L; CS-1 COM CALÇO (DEC-044)")
Q = pr.quadro
XC = Q[2] - 235
pr.cabecalho_peca(", ".join(tipos), f"PLACAS RECORTADAS ({len(recs)} PÇ: {', '.join(p['id'] for _, p in recs)}) · CE-1L ({PP01['CE1L']} PÇ) · CS-1C ({n_c} PÇ) · CS-1D ({n_d} PÇ)",
                  f"recorte {gg(RB / 10)} × {gg((H_PL - RZ) / 10)} cm na ponta do eixo C (consolo CP-I130 + nariz do I130) · console dessa ponta a {gg(XCS / 10)} cm da ponta, na CE-1L · "
                  f"calço de 100 / 75 mm entre a CE-1 e o CS-1 onde a face do pilar fica atrás do plano dos consoles · placa típica: PP00; CS-1: PP03; CE-1: PP04",
                  largura=XC - Q[0] - 10)

# ================================================================== 1. ponta recortada — elevação pela face interna (1:10)
e = pr.vista("PONTA RECORTADA", (Q[0] + 75, Q[3] - 60 - (H_PL + 150) / 10), 10, titulo="DETALHE 1 — PONTA RECORTADA (face interna; RE — RD espelhada)",
             subtitulo="x a partir da ponta do eixo C; o consolo CP-I130 e o nariz do I130 (tracejados) passam pelo recorte; toco 26 × 12 embaixo", unidade="cm")
LV = 1100
cont = [(0, 0), (LV, 0), (LV, H_PL), (RB, H_PL), (RB, RZ), (0, RZ)]
e.poli(cont, "VISTA", fechada=True)
e.interrupcao((LV, 0), (LV, H_PL))
for z in FCH.ZC_:                                                                    # fios: param na face do recorte
    e.linha((RB + 10, z), (LV, z), "ARM_PROT")
e.ret(RB, Z_NC - NC_H / 2, NC_B, NC_H, "METALICA")                                   # NC-1 (aberto na face do recorte e na face interna)
e.chapa(RB, Z_NC + NC_H / 2 - N["t_teto"], NC_B, N["t_teto"], 0.15)
e.chapa(RB + NC_B - N["t_parede"], Z_NC - NC_H / 2 + N["t_base"], N["t_parede"], NC_H - N["t_base"] - N["t_teto"], 0.15)
e.chapa(RB, Z_NC - NC_H / 2, NC_B - 9.5, 9.5, 0.15)
for (xa_, xb_) in N["x_gr"]:
    e.poli([(RB + xa_, Z_NC + NC_H / 2), (RB + xa_, Z_NC + NC_H / 2 + 40), (RB + xb_, Z_NC + NC_H / 2 + 40), (RB + xb_, Z_NC + NC_H / 2)], "METALICA")
# consolo CP-I130 (50 × 49, fundo 226 acima da base) e nariz do I130 (40 largo, de 746 a 1526): atravessam a parede, em tracejado
X_AX = -FCH.JUNTA / 2                                                                # eixo do pilar/I130: 10 mm além da ponta
e.ret(X_AX - 250, 226, 500, 490, "OCULTA")
e.ret(X_AX - 200, 746, 400, H_PL + 150 - 746, "OCULTA")
e.ret(X_AX - 200, -500, 400, 500 + 226 - 40, "OCULTA")                                # pilar P8A / P11 (400 na direção da parede)
e.linha((X_AX, -500), (X_AX, -130), "EIXO"); e.linha((X_AX, H_PL + 30), (X_AX, H_PL + 150), "EIXO")
# armadura do dente (igual à PP01 det. 1, com a ponta na face do recorte) e do toco
Z_N3_, Z_N5_, Z_N6_, X_N4_, X_N7_ = 1060, 1075, 820, (130, 170), (40, 80)
e.barra([(RB + 20, Z_N3_), (LV, Z_N3_)], "N3", 2, 8, comp_cm=138, ponto_rotulo=(RB + 700, Z_N3_), desloc=(10, 22))
e.barra([(RB + X_N4_[0], RZ + 30), (RB + X_N4_[0], 1220), (RB + X_N4_[1], 1220), (RB + X_N4_[1], RZ + 30)], "N4", 1, 8, comp_cm=256,
        ponto_rotulo=(RB + X_N4_[1], 700), desloc=(30, 8), camada="ARM_TRANSV")
e.barra([(RB + 15, Z_N5_), (RB + 175, Z_N5_)], "N5", 1, 6.3, comp_cm=54, ponto_rotulo=(RB + 100, Z_N5_), desloc=(40, 20), camada="ARM_TRANSV")
e.barra([(RB + 15, Z_N6_), (RB + 175, Z_N6_)], "N6", 1, 6.3, comp_cm=54, ponto_rotulo=(RB + 150, Z_N6_), desloc=(34, -14), camada="ARM_TRANSV")
e.barra([(RB + X_N7_[0], 1050), (RB + X_N7_[1], 1050), (RB + X_N7_[1], 1225), (RB + X_N7_[0], 1225), (RB + X_N7_[0], 1050)], "N7", 1, 6.3, comp_cm=46,
        ponto_rotulo=(RB + X_N7_[0], 1225), desloc=(-8, 12), camada="ARM_TRANSV")
e.barra([(20, RZ - 25), (20, 25), (620, 25)], "N8", 2, 8, comp_cm=70, ponto_rotulo=(400, 25), desloc=(30, -22))                 # borda de baixo do toco, ancorada na placa
e.barra([(20, RZ - 25), (RB + 25, RZ - 25), (RB + 25, 700)], "N9", 2, 8, comp_cm=82, ponto_rotulo=(RB + 25, 640), desloc=(40, 44))  # borda do canto reentrante (L)
e.barra([(300, 40), (560, 300)], "N10", 2, 8, comp_cm=37, ponto_rotulo=(560, 300), desloc=(16, -12))                               # diagonal no canto reentrante
for xe in (60, 140, 220):
    e.poli([(xe, 20), (xe, RZ - 20), (xe + 6, RZ - 20)], "ARM_TRANSV")
e.chamada((220, RZ - 20), (30, 28), "N11 - 3 Ø6,3 c/8 C=40 (estribo do toco)")
pr.posicoes_desenho.add("N11")
e.cota_h([0, RB, RB + NC_B, RB + 20, LV], 0, -10, total=False)
e.cota_h([X_AX - 250, X_AX, X_AX + 250], H_PL + 150, 8, total=False)
e.cota_v([0, RZ, 226, Z_NC - NC_H / 2, Z_NC + NC_H / 2, H_PL], 0, -14, total=False)
e.cota_v([0, H_PL], LV, 10, total=False)
e.chamada((RB + NC_B - 20, Z_NC + NC_H / 2), (30, 50), f"NC-1 a {gg(RB / 10)} da ponta (PP02)")
e.chamada((X_AX - 100, 600), (-16, 30), "CP-I130 50 × 49 (folga 2)")
e.chamada((X_AX - 100, 1000), (-16, 30), "nariz do I130 (folga 7)")
e.chamada((130, RZ - 40), (16, -22), f"toco {gg(RB / 10)} × {gg(RZ / 10)} sem fios")
e.marcador_corte((60, -250), (60, RZ + 150), "A", lado=1)
# ---- corte A-A pelo toco (1:5)
a = pr.vista("CORTE A-A", (Q[0] + 232, Q[3] - 190), 5, titulo="CORTE A-A — TOCO", subtitulo="12 × 10 cm, sem protensão", unidade="cm")
pts = [(0, 0), (100, 0), (100, RZ), (0, RZ)]
a.poli(pts, "CORTADO", fechada=True); a.hachura(pts, "AR-CONC", 0.03)
a.poli([(23, 20), (77, 20), (77, RZ - 20), (23, RZ - 20), (23, 20), (31, 20)], "ARM_TRANSV")
for (x_, z_) in ((23, 25), (77, 25), (23, RZ - 25), (77, RZ - 25)):
    a.circulo((x_, z_), 4, "ARMADURA")
a.cota_h([0, 100], 0, -8, total=False)
a.cota_v([0, RZ], 100, 8, total=False)
a.chamada((23, 25), (-8, -10), "N8")
a.chamada((23, RZ - 25), (-8, 10), "N9")
a.chamada((50, RZ - 20), (12, 12), "N11")

# ================================================================== 2. CE-1L — vista frontal (1:4) e planta (1:4)
v1 = pr.vista("CE-1L", (Q[0] + 140, Q[1] + 112), 4.0, titulo="DETALHE 2 — CE-1L: VISTA FRONTAL (face B dos pilares P8A e P11, fiada +6,25)",
              subtitulo="chapa 840 × 330 × 12,5 com asas de 220 além das faces do pilar (400); 4 pinos iguais à CE-1; CS-1 a ±340 do eixo", unidade="mm")
v1.chapa(-420, -165, 840, 330, 1.2)
v1.ret(-200, -165 - 60, 400, 330 + 120, "OCULTA")
for x in (-120, 120):
    for z in (-140, 140):
        v1.circulo((x, z), 16, "METALICA"); v1.circulo((x, z), 8, "OCULTA")
ZT = Z_NC + NC_H / 2 - N["t_teto"] - T["G"] - FCH.Z_CE                                # topo da mesa do CS-1 em relação ao centro da CE-1
for xc in (-340, 340):
    v1.ret(xc - C["costas"]["b"] / 2, ZT + C["costas"]["z0"], C["costas"]["b"], C["costas"]["z1"] - C["costas"]["z0"], "METALICA")
    I.solda(v1, (xc - C["costas"]["b"] / 2, ZT + C["costas"]["z1"]), (10, 26), a=FXJ["solda"]["filete_mm"], tipo="filete", lado="ambos", campo=True, comp=f"2 × {gg(C['costas']['z1'] - C['costas']['z0'])}")
v1.eixo((0, -165), (0, 165), ext=20)
v1.cota_h([-420, -340, -200, -120, 0, 120, 200, 340, 420], -165, -8, total=True)
v1.cota_v([-165, -140, 0, 140, 165], 420, 10, total=True)
v1.chamada((-340, ZT - 30), (16, -22), "CS-1 (PP03) soldado na obra na asa")
v1.chamada((120, -140), (30, -24), "pino Ø16 × 150 c/ cabeça (PP04 item 21)")
v1.chamada((200, 100), (14, 40), "face do pilar (400)")
# planta (corte horizontal pelo console)
v2 = pr.vista("CE-1L PLANTA", (Q[0] + 445, Q[1] + 150), 5.0, titulo="DETALHE 3 — CE-1L: PLANTA NO NÍVEL DO CONSOLE", subtitulo="pilar 400 (direção da parede); asas no plano da face; CS-1 e nicho da placa a 330 da ponta recortada", unidade="mm")
pil = [(-200, 0), (200, 0), (200, 300), (-200, 300)]
v2.poli(pil, "CORTADO", fechada=True); v2.hachura(pil, "AR-CONC", 0.03)
v2.chapa(-420, 0, 840, TCE, 0.4)
for xs_ in (-120, 120):
    v2.ret(xs_ - 8, TCE, 16, 140, "METALICA"); v2.ret(xs_ - 16, TCE + 140, 32, 10, "METALICA")
FOL = FCH.FOLGA
for sg in (-1, 1):
    x0 = sg * FCH.JUNTA / 2
    xr = sg * (FCH.JUNTA / 2 + RB)                                                     # face do recorte
    pts = [(xr, -FOL), (sg * 600, -FOL), (sg * 600, -FOL - E_PL), (xr, -FOL - E_PL)]
    v2.poli(pts, "CORTADO", fechada=True); v2.hachura(pts, "AR-CONC", 0.03)
    v2.interrupcao((sg * 600, -FOL), (sg * 600, -FOL - E_PL))
    v2.poli([(xr, -FOL - NC_P), (xr + sg * NC_B, -FOL - NC_P), (xr + sg * NC_B, -FOL)], "METALICA")
    xc = sg * 340
    v2.chapa(xc - C["costas"]["b"] / 2, -C["costas"]["t"], C["costas"]["b"], C["costas"]["t"], 0.4)
    for dx in (-C["alma"]["x"], C["alma"]["x"]):
        v2.chapa(xc + dx - C["alma"]["t"] / 2, -C["alma"]["y1"], C["alma"]["t"], C["alma"]["y1"] - C["costas"]["t"], 0.4)
    v2.ret(min(x0, xr), -FOL - E_PL, abs(xr - x0), E_PL, "OCULTA")                     # toco (abaixo do nível do corte)
v2.ret(-250, -FOL - 20 - 400, 500, 400, "OCULTA")                                       # consolo CP-I130 (50 × 40) atrás/abaixo
v2.cota_h([-420, -340, -200, 0, 200, 340, 420], 300, 8, total=False)
v2.cota_h([-FCH.JUNTA / 2 - RB - NC_B, -FCH.JUNTA / 2 - RB, -FCH.JUNTA / 2, FCH.JUNTA / 2, FCH.JUNTA / 2 + RB, FCH.JUNTA / 2 + RB + NC_B], -FOL - E_PL, -8, total=False)
v2.cota_v([-FOL - E_PL - 20 - 400, -FOL - E_PL, -FOL - NC_P, -FOL, 0, TCE, 300], -600, -8, total=False)
v2.chamada((0, -FOL - E_PL - 200), (40, -60), "CP-I130 50 × 40 (face B), abaixo do nível do console")
v2.chamada((FCH.JUNTA / 2 + RB / 2, -FOL - E_PL), (26, -14), f"toco 26 × 12 (abaixo); junta {FCH.JUNTA} no eixo")
v2.chamada((-340, -C["alma"]["y1"]), (10, -40), "CS-1 no nicho NC-1 da placa recortada")

# ================================================================== 3. CS-1C / CS-1D — corte vertical pelo console (1:4) e vista frontal (1:4)
cx0 = Q[0] + 338
E_ = 100.0
H_CX, B_CX, T_CX = 330.0, 120.0, 9.5
ZC_ = FCH.Z_CE
ZT_ = Z_NC + NC_H / 2 - N["t_teto"] - T["G"]
c3 = pr.vista("CALCO CORTE", (cx0, Q[3] - 60 - (ZC_ + 300) / 4), 4.0, titulo="DETALHE 4 — CALÇO CS-1C / CS-1D: CORTE", subtitulo="caixa 120 × 330 × e (e = 100 CS-1C; 75 CS-1D) entre a CE-1 e as costas do CS-1; CE-1 na face real do pilar", unidade="mm")
pilp = [(E_, ZC_ - 300), (E_ + 240, ZC_ - 300), (E_ + 240, ZC_ + 300), (E_, ZC_ + 300)]
c3.poli(pilp, "CORTADO", fechada=True); c3.hachura(pilp, "AR-CONC", 0.03)
c3.chapa(E_, ZC_ - 165, TCE, 330, 1.0)                                                  # CE-1 na face real do pilar
for z in (-140, 140):
    c3.ret(E_ + TCE, ZC_ + z - 8, 140, 16, "METALICA"); c3.ret(E_ + TCE + 140, ZC_ + z - 16, 10, 32, "METALICA")
c3.chapa(0, ZC_ - H_CX / 2, T_CX, H_CX, 1.0)                                              # frente da caixa (recebe as costas do CS-1)
c3.chapa(E_ - T_CX, ZC_ - H_CX / 2, T_CX, H_CX, 1.0)                                      # fundo da caixa (soldado na CE-1 na obra)
c3.chapa(T_CX, ZC_ + H_CX / 2 - T_CX, E_ - 2 * T_CX, T_CX, 1.0)                           # topo
c3.chapa(T_CX, ZC_ - H_CX / 2, E_ - 2 * T_CX, T_CX, 1.0)                                  # fundo
co, me, de = C["costas"], C["mesa"], C["dente"]
X = lambda y_: -y_
c3.chapa(X(co["t"]), ZT_ + co["z0"], co["t"], co["z1"] - co["z0"], 1.0)                   # costas do CS-1
c3.poli([(X(y_), ZT_ + z_) for y_, z_ in GF.alma_poli()], "METALICA", fechada=True)
c3.chapa(X(me["y1"]), ZT_ - me["t"], me["y1"] - me["y0"], me["t"], 1.0)
c3.ret(X(de["y0"] + de["t"]), ZT_, de["t"], de["h"], "METALICA")
ppl = [(-me["y1"] - FOL - E_PL, ZC_ - 300), (-me["y1"] - FOL, ZC_ - 300), (-me["y1"] - FOL, ZC_ + 300), (-me["y1"] - FOL - E_PL, ZC_ + 300)]
c3.poli(ppl, "OCULTA", fechada=True)
c3.ret(-me["y1"] - FOL - NC_P, ZT_ + T["G"] + N["t_teto"] - NC_H, NC_P, NC_H, "OCULTA")
I.solda(c3, (0, ZT_ + co["z0"]), (-18, -20), a=C["a_solda"].get("costas_caixa", 5), tipo="filete", lado="ambos", cauda=f"oficina, 2 × {gg(co['z1'] - co['z0'])}")
I.solda(c3, (E_, ZC_ - H_CX / 2), (12, -16), a=CAL["CS-1C"]["solda_campo"]["filete_mm"], tipo="filete", lado="ambos", campo=True, comp=f"2 × {gg(H_CX)}")
c3.cota_h([-me["y1"], 0, E_, E_ + TCE + 150], ZC_ - 300, -8, total=False)
c3.chamada((E_ + TCE / 2, ZC_ - 60), (26, -8), f"CE-1 {gg(TCE)}")
c3.cota_v([ZC_ - 165, ZC_ - 140, ZC_, ZC_ + 140, ZC_ + 165], E_ + TCE + 150, 8, total=False)
c3.cota_v([ZC_ - H_CX / 2, ZT_, ZC_ + H_CX / 2], E_ + TCE + 150, 18, total=False)
c3.chamada((E_ / 2, ZC_ + H_CX / 2 - 5), (-20, 36), "caixa do calço 120 × 330 × e, chapa 9,5 (fábrica)")
c3.texto((-me["y1"] - FOL - E_PL / 2, ZC_ + 150), "PLACA (plano dos consoles)", "nota", "MIDDLE_CENTER", rot=90)
c3.chamada((E_ + 180, ZC_ - 250), (-60, -14), "pilar (face real, e atrás do plano dos consoles)")
c3.chamada((X(me["y1"] / 2), ZT_ - 16), (-20, -70), "CS-1 (PP03), inalterado")
c3.chamada((E_ + TCE / 2, ZC_ + 165), (10, 30), "CE-1 (PP04)")
# vista frontal da caixa (pela placa)
c4 = pr.vista("CALCO FRENTE", (cx0 + 180, Q[3] - 60 - (ZC_ + 300) / 4), 4.0, titulo="DETALHE 5 — CALÇO: FRENTE", subtitulo="caixa 120 × 330 centrada no eixo do console; CE-1 atrás", unidade="mm")
c4.chapa(-190, ZC_ - 165, 380, 330, 1.2)
c4.chapa(-60, ZC_ - 165, 120, 330, 0.6)
c4.ret(-co["b"] / 2, ZT_ + co["z0"], co["b"], co["z1"] - co["z0"], "METALICA")
c4.ret(-me["b"] / 2, ZT_ - me["t"], me["b"], me["t"], "METALICA")
for x in (-120, 120):
    for z in (-140, 140):
        c4.circulo((x, ZC_ + z), 16, "OCULTA")
c4.eixo((0, ZC_ - 190), (0, ZC_ + 190), ext=10)
c4.cota_h([-190, -60, 0, 60, 190], ZC_ - 165, -8, total=False)
c4.cota_v([ZC_ - 165, ZT_, ZC_ + 165], -190, -10, total=False)
c4.chamada((60, ZC_ + 100), (-20, 22), "caixa 120 × 330")
c4.chamada((-120, ZC_ - 140), (-24, -12), "pinos da CE-1 (atrás)")

# ================================================================== tabelas
rows = [[p["id"], FCH.TIPO[p["Lk"]], f"{p['L'] / 10:.1f}".replace(".", ","), "esquerda" if p["rec"] == "s0" else "direita", f"ND-LET-PP-{V}", f"+{f(p['z0'] / 1000, 2)}",
         f"{gg(p['xcs'][0] / 10)} / {gg(p['xcs'][1] / 10)}", f(FCH.peso_t(p["Lk"]), 2)] for V, p in recs]
y = pr.tabela(XC, Q[3] - 6, "PLACAS RECORTADAS (DEC-044)", ["PEÇA", "TIPO", "L (cm)", "RECORTE NA PONTA", "VISTA", "BASE", "CONSOLES (cm da ponta)", "PESO (t)"],
              rows, [16, 22, 18, 28, 30, 16, 40, 20], h_lin=5.2)
ce = [[20, "CHAPA DE ESPERA CE-1L", f"CH {gg(TCE)} × 330 × 840", "ASTM A36", 1, f(GF.kg_ch(840, 330, TCE), 3)],
      [21, "PINO COM CABEÇA (stud)", "Ø16 × 150, cabeça Ø32 × 10 — ISO 13918 SD", "S235J2 + C450", 4, f(GF.kg_red(16, 140) + GF.kg_red(32, 10), 3)]]
kg_cel = GF.kg_ch(840, 330, TCE) + 4 * (GF.kg_red(16, 140) + GF.kg_red(32, 10))
y = pr.tabela(XC, y - 6, f"LISTA DE MATERIAIS — CE-1L (1 CJ) — {PP01['CE1L']} PÇ: P8A E P11, FIADA +6,25", ["Nº", "DESCRIÇÃO", "DIMENSÃO (mm)", "MATERIAL", "QTD", "kg/un"], ce, [9, 48, 76, 36, 12, 24], h_lin=5.2)
pr.texto(XC, y - 3.5, f"CE-1L: {f(kg_cel, 2)} kg/cj; pinos, N18 e furação iguais à CE-1 (PP04). Asa: M {gg(CEL['asa']['M_kNm'])} kN·m + T {gg(CEL['asa']['T_kNm'])} kN·m → von Mises {gg(CEL['asa']['von_mises_MPa'])} ≤ {gg(CEL['asa']['lim_MPa'])} MPa (uso {gg(CEL['asa']['uso'])}); pinos como na CE-1 (2 consoles).", "nota", "TEXTO")
cal = []
for mk_, ee in (("CS-1C", 100.0), ("CS-1D", 75.0)):
    cal += [[mk_, "chapa lateral", f"CH 9,5 × 330 × {gg(ee)}", "ASTM A36", 2, f(GF.kg_ch(330, ee, 9.5), 3)],
            ["", "chapa topo / fundo", f"CH 9,5 × 101 × {gg(ee)}", "ASTM A36", 2, f(GF.kg_ch(101, ee, 9.5), 3)],
            ["", "chapa frente / fundo", "CH 9,5 × 120 × 330", "ASTM A36", 2, f(GF.kg_ch(120, 330, 9.5), 3)],
            ["", f"caixa completa ({gg(CAL[mk_]['kg_caixa'])} kg) + CS-1 (PP03)", f"120 × 330 × {gg(ee)}", "", 1, f(CAL[mk_]["kg_caixa"] + json.load(open('/home/claude/letsara/pranchas/pp03.json'))["kg_CS1"], 2)]]
y = pr.tabela(XC, y - 8, f"CAIXAS DE CALÇO — CS-1C ({n_c} PÇ, e = 100) E CS-1D ({n_d} PÇ, e = 75)", ["MARCA", "PEÇA", "DIMENSÃO (mm)", "MATERIAL", "QTD", "kg"], cal, [16, 56, 52, 30, 12, 24], h_lin=5.0)
pos = []
for mk_ in ("CS-1C", "CS-1D"):
    cont = {}
    for (V, b_, k_) in FCH.CALCOS.get(mk_, []):
        nm = FCH.VISTAS[V].get("nomes_pil", [None] * 9)[b_] or f"pilar {b_ + 1}"
        cont.setdefault((V, nm), []).append(k_)
    for (V, nm), ks in sorted(cont.items()):
        pos.append([mk_, f"vista {V}", nm, len(ks), ", ".join(f"+{f(k * 1.25, 2)}" for k in sorted(ks))])
y = pr.tabela(XC, y - 8, "ONDE VÃO OS CALÇOS (por pilar e fiada — base da fiada)", ["MARCA", "VISTA", "PILAR", "QT", "FIADAS (base)"], pos, [16, 20, 20, 10, 124], h_lin=4.6)
pr.notas(XC, y - 4, [
    f"DEC-044: o I130 do eixo C (V407 na linha 2; V406/V407 na linha 4) e seus consolos CP-I130 atravessam as paredes internas G e C. As 4 placas da fiada +6,25 que chegam ao eixo C ({', '.join(p['id'] for _, p in recs)}) recebem recorte de {gg(RB / 10)} × {gg((H_PL - RZ) / 10)} cm nessa ponta (folga 2 cm ao consolo, 7 cm ao nariz; {REC['folga_consolo_mm']} mm entre o toco e o fundo do consolo descontada a janela de montagem de 40). RE/RD = recorte à esquerda/direita na elevação das PP-G/PP-C (não é a mesma peça virada: a face interna fica para o pilar).",
    f"Placa recortada: fôrma, seção, {FCH.NC_} fios, insertos e alças da PP00; os fios param na face do recorte (lbpt {gg(PLJ['protensao']['lbpt_gradual_m'])} m contada dela). Console dessa ponta a {gg(XCS / 10)} cm da ponta: nicho NC-1 de {gg(RB / 10)} a {gg((RB + NC_B) / 10)} cm, aberto na face do recorte; dente Gerber N3–N7 igual à PP01 (det. 1) com a ponta na face do recorte. Toco {gg(RB / 10)} × {gg(RZ / 10)} sem protensão: N8/N9 2 Ø8 de borda, N10 2 Ø8 diagonais no canto reentrante, N11 estribos Ø6,3 c/8 (mínima {gg(REC['toco']['As_min_cm2'])} cm²). Tela N1 recortada no nicho e no recorte.",
    f"Verificação (placas.json): desforma deitada em 4 pontos com balancim (0,104 L / 0,396 L, como a típica): face do recorte {gg(REC['desforma']['sig_face_MPa'])} MPa, toco {gg(REC['desforma']['sig_toco_MPa'])} MPa, ponto de desforma {gg(REC['desforma']['sig_ponto_desforma_MPa'])} MPa ≤ {gg(REC['desforma']['lim_MPa'])} (fctk,j/1,5); montada nos 2 consoles (vão {gg(REC['montada']['L_vao_m'])} m): {gg(REC['montada']['sig_MPa'])} MPa ≤ 0 (descompressão). Içamento em pé pelas alças AL-P (0,21 L, fora do recorte) como a típica.",
    f"CE-1L (fixacao_placas.json): chapa 840 × 330 × {gg(TCE)} A36 com os mesmos 4 pinos e N18 da CE-1, centrada no pilar, fiada +6,25 dos P8A (PC-01) e P11 (PC-02); as asas de 220 ficam no plano da face, além do pilar — balanço de {gg(CEL['asa']['balanco_mm'])} mm até o CS-1: flexão no plano {gg(CEL['asa']['sigma_MPa'])} MPa + torção {gg(CEL['asa']['tau_MPa'])} MPa → von Mises {gg(CEL['asa']['von_mises_MPa'])} ≤ {gg(CEL['asa']['lim_MPa'])} MPa; giro da asa {gg(CEL['asa']['rotacao_rad'])} rad ({gg(CEL['asa']['flecha_ponta_console_mm'])} mm na ponta do console). Folga de 4 cm entre a CE-1L e o topo do CP-I130. Na fôrma do pilar: asas por fora da fôrma lateral (gabarito), posição ±5.",
    f"CS-1C / CS-1D (DEC-044): nos cantos (vistas A e I: {', '.join(sorted(set(r[2] for r in pos if r[1] in ('vista A', 'vista I'))))}), nos PL-02/PL-06 da vista G e nos P10 da vista C a face do pilar fica 100 / 75 mm atrás do plano dos consoles (40 ou 25 ⊥ à parede, contra 60 dos PF). O CS-1 (PP03) recebe na fábrica uma caixa fechada de chapa 9,5, 120 × 330 × e, soldada nas costas (filete 5 de oficina, 2 × 130); na obra o fundo da caixa é soldado na CE-1 (filete {gg(CAL['CS-1C']['solda_campo']['filete_mm'])} E70XX nos 2 lados verticais de 330, inspeção visual 100 % + LP 10 %, galvanização a frio). Nesses pilares a CE-1 recebe 1 console só.",
    f"Verificação do calço (fixacao_placas.json, Vd {gg(FXJ['cargas_por_console']['Vd_kN'])} kN por console): CS-1C braço {gg(CAL['CS-1C']['braco_mm'])} mm, M {gg(CAL['CS-1C']['M_kNm'])} kN·m — pinos da CE-1 T {gg(CAL['CS-1C']['CE1_1_console']['T_linha_sup_kN'])} ≤ {gg(CAL['CS-1C']['CE1_1_console']['phiN_linha_kN'])} kN (interação {gg(CAL['CS-1C']['CE1_1_console']['interacao'])}), flexão local da CE-1 {gg(CAL['CS-1C']['CE1_1_console']['flexao_chapa_MPa'])} ≤ {gg(CAL['CS-1C']['CE1_1_console']['lim_MPa'])} MPa, caixa {gg(CAL['CS-1C']['caixa']['von_mises_MPa'])} MPa, solda de campo {gg(CAL['CS-1C']['solda_campo']['f_res_MPa'])} ≤ {gg(CAL['CS-1C']['solda_campo']['fw_Rd_MPa'])} MPa; CS-1D: M {gg(CAL['CS-1D']['M_kNm'])} kN·m, interação {gg(CAL['CS-1D']['CE1_1_console']['interacao'])}, flexão local {gg(CAL['CS-1D']['CE1_1_console']['flexao_chapa_MPa'])} MPa. Regulagem (G, afastamento, janela) igual à PP03.",
    "Galvanização a fogo da caixa com o CS-1 (NBR 6323); CE-1L galvanizada após os pinos. Tolerâncias NBR ISO 2768-1 m. Cotas de concreto em cm, metálica em mm; não medir no desenho.",
    "EMISSÃO EXECUTIVA — LIBERADO PARA PRODUÇÃO E MONTAGEM."], 235)
bar = [dict(pos="N3", diam=8, qtd=2, comp=138), dict(pos="N4", diam=8, qtd=1, comp=256), dict(pos="N5", diam=6.3, qtd=1, comp=54), dict(pos="N6", diam=6.3, qtd=1, comp=54),
       dict(pos="N7", diam=6.3, qtd=1, comp=46), dict(pos="N8", diam=8, qtd=2, comp=70), dict(pos="N9", diam=8, qtd=2, comp=82), dict(pos="N10", diam=8, qtd=2, comp=37), dict(pos="N11", diam=6.3, qtd=3, comp=40)]
pr.texto(Q[0] + 40, Q[3] - 282, "AÇO DA PONTA RECORTADA (1 PONTA; N3–N7 da PP01)", "sub", "TITULO")
pr.tabela_aco(Q[0] + 40, Q[3] - 286, bar)
av = pr.salvar("/home/claude/letsara/pranchas/ND-LET-PP06")
print("PP06", len([a for a in av if a[0] == "ERRO"]), "erros,", len(av), "avisos", [a for a in av if a[0] == "ERRO" or "sobrep" in a[1]][:14])
