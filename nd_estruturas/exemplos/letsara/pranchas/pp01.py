"""ND-LET-PP01 — fixação das placas pelo sistema Trejor (rev06, DEC-026): armadura da ponta da placa (dente Gerber) com
relação do aço, e desenhos de fabricação das peças metálicas NC-1, CS-1, CE-1, PT-1 e PT-2 com lista de material.
Lê fixacao_placas.json (calc_fixacao_placas.py) e fechamento.py (quantidades). Concreto em cm, metálica em mm."""
import json
import math
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
import fechamento as FCH
import geo_fixacao as GF
import iso_nd as I
from prancha_nd import Prancha

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
FX = json.load(open(AQ + "fixacao_placas.json"))
f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
RHO = 7.85e-6                                            # kg/mm³
H, E = 1250, 100
NB, NH, NP = FCH.NC_B, FCH.NC_H, FCH.NC_P               # 120 × 200 × 60
ZN0, ZN1 = FCH.Z_NC - NH / 2, FCH.Z_NC + NH / 2          # 840 / 1040
Z_N3, Z_N5, Z_N6 = 1060, 1075, 820                       # tirante, estribo de ancoragem do teto, estribo de ancoragem da base
X_N4 = (130, 170)                                        # estribo de suspensão no plano médio
X_N7 = (40, 80)                                          # estribo vertical do nariz (Av do PCI)
Z_CORD = (156, 469, 781, 1094)

# quantidades na obra (peça a peça nas vistas)
PEC = [p for V in FCH.DADOS for p in FCH.DADOS[V][0]]
N_CS = sum(len(FCH.DADOS[V][1]) for V in FCH.DADOS)
N_PT1 = sum(2 for p in PEC if p["trava"] == "PT-1")
N_PT2 = sum(len(p["pt2"]) for p in PEC)
CE = set()
for V in FCH.DADOS:
    pil = [s for s, _, _ in FCH.VISTAS[V]["pil"]]
    for (x, z) in FCH.DADOS[V][1]:
        CE.add((V, min(pil, key=lambda s: abs(s - x)), z))
N_CE, N_PL = len(CE), len(PEC)


def kg_ch(a, b, t, n=1):
    return n * a * b * t * RHO


def kg_barra(d, L, n=1):
    return n * math.pi * d ** 2 / 4 * L * RHO


pr = Prancha("A1", dict(cliente=FCH.CLIENTE, obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="FIXAÇÃO DAS PLACAS (SISTEMA TREJOR) — ARMADURA DA PONTA, CONJUNTO MONTADO, TOLERÂNCIAS, SEQUÊNCIA DE MONTAGEM E LISTAS",
                        desenho="ND-LET-PP01", folha="01/01", fase="PARA APROVAÇÃO", rev="06"))
pr.revisao("06", "18/10/2026", "EXECUTIVO DA FIXAÇÃO TREJOR (DEC-026): ARMADURA DA PONTA, CONJUNTO MONTADO; FABRICAÇÃO NAS PP02 A PP04")
Q = pr.quadro
XC = Q[2] - 190
pr.cabecalho_peca("FX", f"FIXAÇÃO DAS PLACAS — {N_CS} CONSOLES CS-1 · {N_CE} CE-1 · {N_PT1} PT-1 · {N_PT2} PT-2",
                  "sistema Trejor, console soldado (DEC-026) · placa típica ND-LET-PP00 · fabricação: NC-1 PP02, CS-1 PP03, CE-1/PT-1/PT-2 PP04 · metálica em mm, concreto em cm",
                  largura=XC - Q[0] - 10)

# ================================================================== D1 — armação da ponta (vista pela face interna, 1:10)
d1 = pr.vista("DETALHE 1", (Q[0] + 40, Q[1] + 300), 10, titulo="DETALHE 1 — ARMAÇÃO DA PONTA DA PLACA",
              subtitulo="vista pela face interna; as 2 pontas iguais (espelhadas); cordoalhas e tela N1 da ND-LET-PP00", unidade="cm")
d1.poli([(500, 0), (0, 0), (0, H), (500, H)], "VISTA"); d1.interrupcao((500, 0), (500, H))
for z in Z_CORD:
    d1.linha((10, z), (500, z), "ARM_PROT")
d1.ret(0, ZN0, NB, NH, "METALICA")
d1.hachura([(0, ZN0), (NB, ZN0), (NB, ZN1), (0, ZN1)], "ANSI31", 0.6, "METALICA")
d1.barra([(20, Z_N3), (500, Z_N3)], "N3", 2, 8, comp_cm=138, ponto_rotulo=(420, Z_N3), desloc=(14, 10))
d1.barra([(X_N4[0], 60), (X_N4[1], 60), (X_N4[1], 1220), (X_N4[0], 1220), (X_N4[0], 60)], "N4", 1, 8, comp_cm=256,
         ponto_rotulo=(X_N4[1], 600), desloc=(22, 0), camada="ARM_TRANSV")
d1.barra([(15, Z_N5), (175, Z_N5)], "N5", 1, 6.3, comp_cm=54, ponto_rotulo=(100, Z_N5), desloc=(36, 18), camada="ARM_TRANSV")
d1.barra([(15, Z_N6), (175, Z_N6)], "N6", 1, 6.3, comp_cm=54, ponto_rotulo=(100, Z_N6), desloc=(36, -10), camada="ARM_TRANSV")
d1.barra([(X_N7[0], 1050), (X_N7[1], 1050), (X_N7[1], 1225), (X_N7[0], 1225), (X_N7[0], 1050)], "N7", 1, 6.3, comp_cm=46,
         ponto_rotulo=(X_N7[1], 1180), desloc=(30, 16), camada="ARM_TRANSV")
d1.cota_h([0, NB, X_N4[0], X_N4[1], 500], 0, -10, total=False)
d1.cota_v([0, 60, Z_N6, ZN0, ZN1, Z_N3, 1220, H], 0, -10, total=False)
for (xa, xb) in GF.N["x_gr"]:
    d1.poli([(xa, ZN1), (xa, ZN1 + GF.N["h_gr_teto"]), (xb, ZN1 + GF.N["h_gr_teto"]), (xb, ZN1)], "METALICA")
    d1.poli([(xa, ZN0), (xa, ZN0 - GF.N["h_gr_base"]), (xb, ZN0 - GF.N["h_gr_base"]), (xb, ZN0)], "METALICA")
d1.chamada((60, FCH.Z_NC), (36, -6), "NC-1 (ND-LET-PP02) — tela N1 recortada no nicho")
d1.chamada((GF.N["x_gr"][1][1], ZN1 + 30), (40, 4), "grampos do NC-1 dentro do N5 / N6")
d1.chamada((300, 781), (18, -12), "C1 cordoalhas (ND-LET-PP00)")

# ================================================================== D2 — corte B-B pela ponta (1:5)
d2 = pr.vista("DETALHE 2", (Q[0] + 265, Q[1] + 290), 5, titulo="DETALHE 2 — CORTE B-B NA PONTA",
              subtitulo="espessura da placa (face interna à esquerda): barras no plano médio, entre as cordoalhas", unidade="cm")
pts = [(0, 700), (E, 700), (E, H), (0, H)]
d2.poli(pts, "CORTADO", fechada=True); d2.hachura(pts, "AR-CONC", 0.03)
d2.interrupcao((0, 700), (E, 700))
for z in (781, 1094):
    for y in (26.4, 73.6):
        d2.ponto_barra((y, z), 12.7, "ARM_PROT_SECAO")
d2.ret(0, ZN0, NP, NH, "OCULTA")
yg = GF.N["y_gr"]
d2.ret(yg - 3.15, ZN1, 6.3, GF.N["h_gr_teto"], "METALICA"); d2.ret(yg - 3.15, ZN0 - GF.N["h_gr_base"], 6.3, GF.N["h_gr_base"], "METALICA")
d2.linha((50, 710), (50, 1220), "ARM_TRANSV")                                             # N4 no plano médio
for y in (40, 60):
    d2.ponto_barra((y, Z_N3), 8)
for z in (Z_N5, Z_N6):
    d2.linha((23, z), (77, z), "ARM_TRANSV")
d2.linha((50, 1050), (50, 1225), "ARM_TRANSV")
d2.cota_h([0, yg, 50, E], 700, -10, total=False)
d2.cota_v([700, Z_N6, ZN0, ZN1, Z_N3, Z_N5, H], E, 10, total=False)
d2.chamada((50, 900), (16, -14), "N4 / N7 no plano médio (y = 5)")
d2.chamada((60, Z_N3), (14, 10), "N3 — 2 Ø8 (y = 4 e 6)")
d2.chamada((70, Z_N5), (16, 22), "N5 Ø6,3 fechado (horizontal), cobrimento 2,0")
d2.chamada((70, Z_N6), (16, -12), "N6 Ø6,3 fechado (horizontal)")
d2.chamada((30, 960), (-14, 10), "NC-1")
d2.chamada((yg, ZN1 + 20), (-16, 14), "grampo Ø6,3 (y = 3,1)")


# ================================================================== D3 — conjunto montado: corte vertical no eixo do console (1:2)
C, N, HX, T = GF.C, GF.N, GF.HX, GF.T
co, al, me, de, po = C["costas"], C["alma"], C["mesa"], C["dente"], C["ponta"]
a0, G0 = T["a"], T["G"]
zt_ = GF.DZ                                              # base do nicho em coordenadas do console
zn1 = zt_ + N["H"]
d3 = pr.vista("DETALHE 3", (Q[0] + 110, Q[1] + 150), 2.0, titulo="DETALHE 3 — CONJUNTO MONTADO (CORTE NO EIXO DO CONSOLE)",
              subtitulo="posição nominal; tolerâncias na tabela; nível z = 0 no topo da mesa do CS-1", unidade="mm")
ZB, ZT2 = -245.0, 130.0
pil = [(-190, ZB), (0, ZB), (0, ZT2), (-190, ZT2)]
d3.poli(pil, "CORTADO", fechada=True); d3.hachura(pil, "AR-CONC", 0.03)
d3.chapa(-16, -55.5 - 165, 16, 330, 0.6)                                 # CE-1 embutida
for z in (-140, 140):
    d3.ret(-16 - 140, -55.5 + z - 8, 140, 16, "METALICA")
d3.chapa(0, co["z0"], co["t"], co["z1"] - co["z0"], 0.6)
d3.poli(GF.alma_poli(), "VISTA", fechada=True)
d3.chapa(me["y0"], -me["t"], me["y1"] - me["y0"], me["t"], 0.6)
d3.ret(de["y0"], 0, de["t"], de["h"], "VISTA")
d3.chapa(po["y0"], po["z0"], po["t"], po["z1"] - po["z0"], 0.6)
e2 = HX["e"] / 2
yn, zf = C["y_nivel"], C["z_frontal"]
d3.ret(yn - e2, 0, HX["e"], HX["m"] + HX["m_fina"], "METALICA"); d3.ret(yn - 8, HX["m"] + HX["m_fina"], 16, G0 - HX["k"] - HX["m"] - HX["m_fina"], "METALICA")
d3.ret(yn - e2, G0 - HX["k"], HX["e"], HX["k"], "METALICA")
d3.ret(po["y0"] - HX["m"], zf - e2, HX["m"], HX["e"], "METALICA")
yt = a0 + N["P"] - N["t_fundo"]
d3.ret(yt - C["L_frontal"], zf - 8, C["L_frontal"], 16, "METALICA")
# placa com o nicho (y a partir da face do pilar)
PLC = [(a0, zn1), (a0, ZT2), (a0 + 100, ZT2), (a0 + 100, ZB), (a0, ZB), (a0, zt_), (a0 + N["P"], zt_), (a0 + N["P"], zn1)]
d3.poli(PLC, "CORTADO", fechada=True)
d3.hachura(PLC, "AR-CONC", 0.03)
d3.chapa(a0, zn1 - N["t_teto"], N["P"] - N["t_fundo"], N["t_teto"], 0.6)
d3.chapa(a0, zt_, N["P"] - N["t_fundo"], N["t_base"], 0.6)
d3.chapa(a0 + N["P"] - N["t_fundo"], zt_, N["t_fundo"], N["H"], 0.6)
d3.ret(a0, zn1 - N["t_teto"] - N["h_aba"], N["t_aba"], N["h_aba"], "OCULTA")      # abas (laterais, fora do plano do corte)
d3.interrupcao((-190, ZB), (-190, ZT2)); d3.interrupcao((a0, ZB), (a0 + 100, ZB)); d3.interrupcao((a0, ZT2), (a0 + 100, ZT2))
d3.cota_h([-16, 0, a0, de["y0"], me["y1"], a0 + N["P"], a0 + 100], ZB, -10, total=False)
d3.cota_v([co["z0"], zt_, zf, 0, G0, zn1, co["z1"]], a0 + 100, 16, total=False)
d3.chamada((-60, 100), (-14, 18), "pilar")
d3.chamada((a0 + 70, -200), (14, -12), "placa 10 cm (ND-LET-PP00)")
d3.chamada((-8, -55.5 - 120), (-30, -16), "CE-1 (PP04)")
d3.chamada((8, -120), (-24, -32), "CS-1 (PP03)")
d3.chamada((a0 + 30, zn1 - 6), (24, 26), "NC-1 (PP02)")
d3.chamada((a0 + 6, zn1 - 30), (-18, 30), "abas laterais (tracejadas)")
d3.chamada((yt, zf), (24, -16), "prisioneiro no fundo")
d3.chamada((yn, G0), (-10, 40), "M16 de nível sob o teto")

# ================================================================== D4 — planta do conjunto (1:2), logo abaixo do teto
d4 = pr.vista("DETALHE 4", (Q[0] + 300, Q[1] + 145), 2.0, titulo="DETALHE 4 — PLANTA DO CONJUNTO", subtitulo="corte logo abaixo do teto do nicho; posição nominal", unidade="mm")
xp = -N["B"] / 2                                          # ponta da placa (x do console)
pl = [(xp, a0), (xp + 320, a0), (xp + 320, a0 + 100), (xp, a0 + 100)]
d4.poli([(xp, a0 + N["P"]), (xp, a0 + 100), (xp + 320, a0 + 100), (xp + 320, a0), (xp + N["B"], a0), (xp + N["B"], a0 + N["P"])], "CORTADO", fechada=True)
d4.hachura([(xp, a0 + N["P"]), (xp, a0 + 100), (xp + 320, a0 + 100), (xp + 320, a0), (xp + N["B"], a0), (xp + N["B"], a0 + N["P"])], "AR-CONC", 0.03)
d4.chapa(xp, a0 + N["P"] - N["t_fundo"], N["B"], N["t_fundo"], 0.6)
d4.chapa(xp + N["B"] - N["t_parede"], a0, N["t_parede"], N["P"] - N["t_fundo"], 0.6)
for (u0, u1) in (N["aba_e"], N["aba_d"]):
    d4.chapa(xp + u0, a0, u1 - u0, N["t_aba"], 0.6)
d4.ret(-co["b"] / 2, 0, co["b"], co["t"], "METALICA"); d4.ret(-me["b"] / 2, me["y0"], me["b"], me["y1"] - me["y0"], "VISTA")
for sg in (-1, 1):
    x0 = min(sg * de["x0"], sg * (de["x0"] + de["b"]))
    d4.chapa(x0, de["y0"], de["b"], de["t"], 0.6)
I.hexagono(d4, (0, yn), HX["s"], "METALICA")
d4.chapa(-190 + (-70 - 0) + 70 - 70, -16, 380, 16, 0.6)
d4.poli([(-270, -16), (-270, -120), (130, -120), (130, -16)], "CORTADO")
d4.interrupcao((-270, -120), (130, -120))
d4.cota_h([xp, xp + N["aba_e"][1], xp + N["aba_d"][0], xp + N["aba_d"][1], xp + N["B"]], a0 + 100, 10, total=False)
d4.cota_h([-70, 0], -120, -8, total=False)
PV = [(-80 - 320, a0), (-80, a0), (-80, a0 + 100), (-80 - 320, a0 + 100)]
d4.poli([(-80, a0), (-80 - 190, a0), (-80 - 190, a0 + 100), (-80, a0 + 100)], "OCULTA", fechada=True)
d4.ret(-200, 0, 120, 16, "OCULTA")
d4.chamada((-170, a0 + 95), (4, 16), "placa vizinha (NC-1' e CS-1 espelhados)")
d4.cota_v([-16, 0, a0, a0 + N["t_aba"], de["y0"], de["y0"] + de["t"], a0 + N["P"], a0 + 100], xp + 320, 10, total=False)
d4.chamada((xp, a0 + 80), (-14, 10), "ponta da placa (junta 20 no eixo do pilar)")
d4.chamada((0, yn), (30, -40), "M16 de nível (meio livre, sem aba)")
d4.eixo((-70, -120), (-70, a0 + 100), ext=10)
d4.texto((-70, -128), "eixo do pilar", "nota", "TOP_CENTER")
d4.chamada((60, -70), (14, -10), "pilar")

# ================================================================== D5 — sequência de montagem (cortes esquemáticos 1:5)
MOJ = FX["montagem_CS1_NC1"]["janela_R_mm"]["G=50"]
R_m = round((MOJ[0] + MOJ[1]) / 2)


def esquema(v, dy, dz, seta=None):
    v.chapa(-16, -55.5 - 165, 16, 330, 0.8)
    v.chapa(0, co["z0"], co["t"], co["z1"] - co["z0"], 0.8)
    v.poli(GF.alma_poli(), "METALICA", fechada=True)
    v.chapa(me["y0"], -me["t"], me["y1"] - me["y0"], me["t"], 0.8)
    v.ret(de["y0"], 0, de["t"], de["h"], "METALICA")
    v.chapa(po["y0"], po["z0"], po["t"], po["z1"] - po["z0"], 0.8)
    v.ret(yn - 12, G0 - HX["k"], 24, HX["k"], "METALICA"); v.ret(yn - 8, 0, 16, G0 - HX["k"], "METALICA")
    v.ret(yt - C["L_frontal"], zf - 8, C["L_frontal"], 16, "METALICA")
    A, Z0, Z1 = a0 + dy, zt_ + dz, zn1 + dz
    PL_ = [(A, Z1), (A, 160 + dz), (A + 100, 160 + dz), (A + 100, -240 + dz), (A, -240 + dz), (A, Z0), (A + N["P"], Z0), (A + N["P"], Z1)]
    v.poli(PL_, "CORTADO", fechada=True); v.hachura(PL_, "AR-CONC", 0.02)
    v.chapa(A, Z1 - N["t_teto"], N["P"] - N["t_fundo"], N["t_teto"], 0.8)
    v.chapa(A, Z0, N["P"] - N["t_fundo"], N["t_base"], 0.8)
    v.chapa(A + N["P"] - N["t_fundo"], Z0, N["t_fundo"], N["H"], 0.8)
    v.chapa(A, Z1 - N["t_teto"] - N["h_aba"], N["t_aba"], N["h_aba"], 0.8)
    if seta:
        (x0_, y0_), (x1_, y1_) = seta
        v.linha((x0_, y0_), (x1_, y1_), "INDICACAO")
        import math as _m
        an = _m.atan2(y1_ - y0_, x1_ - x0_)
        for sg_ in (1, -1):
            v.linha((x1_, y1_), (x1_ - 14 * _m.cos(an + sg_ * 0.4), y1_ - 14 * _m.sin(an + sg_ * 0.4)), "INDICACAO")


ESQ = [("1 — APROXIMAR", 150, R_m, ((260, 90), (150, 90))), ("2 — ENCOSTAR", 0, R_m, ((70, 160 + R_m + 30), (70, 160 + R_m + 2))), ("3 — BAIXAR", 0, 0, ((70, 230), (70, 175)))]
d5 = pr.vista("DETALHE 5", (Q[0] + 448, Q[1] + 360), 5.0, titulo="DETALHE 5 — SEQUÊNCIA DE MONTAGEM",
              subtitulo=f"esquema; janela R = {MOJ[0]:g} a {MOJ[1]:g} com G = 50", unidade="mm")
O5 = d5.o
for k, (tit, dy_, dz_, st) in enumerate(ESQ):
    d5.o = (O5[0] + 58 * k, O5[1])
    esquema(d5, dy_, dz_, st)
    d5.texto((110, 300), tit, "nota", "BOTTOM_CENTER")
d5.o = O5
# ================================================================== tabelas
y = Q[3] - 6
barras = [dict(pos="N3", diam=8.0, qtd=4, comp=138, trechos=["138"]),
          dict(pos="N4", diam=8.0, qtd=2, comp=256, forma=[(0, 0), (4, 0), (4, 116), (0, 116), (0, 0), (1, 1)], trechos=["4", "116", "", ""]),
          dict(pos="N5", diam=6.3, qtd=2, comp=54, forma=[(0, 0), (16, 0), (16, 5.4), (0, 5.4), (0, 0), (1, 1)], trechos=["16", "5,4", "", ""]),
          dict(pos="N6", diam=6.3, qtd=2, comp=54, forma=[(0, 0), (16, 0), (16, 5.4), (0, 5.4), (0, 0), (1, 1)], trechos=["16", "5,4", "", ""]),
          dict(pos="N7", diam=6.3, qtd=2, comp=46, forma=[(0, 0), (4, 0), (4, 17.5), (0, 17.5), (0, 0), (1, 1)], trechos=["4", "17,5", "", ""])]
ta = pr.tabela_croqui(XC, y, barras, h_lin=8.0)
KG_PONTA = ta["total_kg"]
y = ta["y_base"]
pr.texto(XC, y - 3, f"Por placa (2 pontas). Obra: {N_PL} placas → {f(KG_PONTA * N_PL, 0)} kg (soma ao aço da ND-LET-PP00).", "min", "TEXTO")
kg = lambda its: sum(k * q for *_, q, k in its)
kg_nc, kg_cs, kg_ce = kg(GF.nc1_itens()), kg(GF.cs1_itens()), kg(GF.ce1_itens())
pti = {n: (q, k) for n, _, _, _, q, k in GF.pt_itens()}
kg_pt1 = sum(pti[n][0] * pti[n][1] for n in (30, 31, 32))
kg_pt2 = pti[40][1] + pti[31][0] * pti[31][1] + pti[32][0] * pti[32][1]
rows = [["NC-1 / NC-1'", "caixa soldada + grampos (2 por placa)", "ND-LET-PP02", 2 * N_PL, f(kg_nc, 2), f(kg_nc * 2 * N_PL, 0)],
        ["CS-1", "console soldado + parafusos de ajuste", "ND-LET-PP03", N_CS, f(kg_cs, 2), f(kg_cs * N_CS, 0)],
        ["CE-1", "chapa de espera + 4 pinos (no pilar)", "ND-LET-PP04", N_CE, f(kg_ce, 2), f(kg_ce * N_CE, 0)],
        ["PT-1", "cartola + 2 M16 + 2 arruelas", "ND-LET-PP04", N_PT1, f(kg_pt1, 2), f(kg_pt1 * N_PT1, 0)],
        ["PT-2", "cantoneira + 2 M16 + 2 arruelas", "ND-LET-PP04", N_PT2, f(kg_pt2, 2), f(kg_pt2 * N_PT2, 0)]]
tot = kg_nc * 2 * N_PL + kg_cs * N_CS + kg_ce * N_CE + kg_pt1 * N_PT1 + kg_pt2 * N_PT2
rows.append(["", "total da fixação (sem luvas e buchas)", "", "", "", f(tot, 0)])
y = pr.tabela(XC, y - 8, "RESUMO DAS PEÇAS METÁLICAS — OBRA", ["MARCA", "COMPOSIÇÃO", "FOLHA", "QT", "kg/un", "kg"], rows, [24, 76, 26, 14, 20, 30], h_lin=5.2, destaque_ultima=True)
MO = FX["montagem_CS1_NC1"]
fo = MO["folgas_mm"]
tol = [["afastamento placa–pilar (a)", f"{T['a']:g} ± {T['a_tol']:g}", "prisioneiro frontal"],
       ["G: mesa → teto do nicho", f"{T['G']:g} ± {T['G_tol']:g}", "M16 de nível"],
       ["posição do console × nicho (x)", f"± {T['x_tol']:g}", "placa ±5, solda ±3"],
       ["engate aba × dente (G máx.)", f"≥ {fo['engate aba–dente com G máximo (z)']:g}", "sucção"],
       ["folga aba × dente (a máx.)", f"≥ {fo['aba atrás x dente (y)']:g}", "montagem"],
       ["janela de montagem R", f"{MO['janela_R_mm']['G=50'][0]:g} a {MO['janela_R_mm']['G=50'][1]:g} (G = 50)", "teto acima da final"]]
y = pr.tabela(XC, y - 4, "TOLERÂNCIAS E FOLGAS DE MONTAGEM (mm)", ["ITEM", "VALOR", "AJUSTE / OBS."], tol, [70, 60, 60], h_lin=5.0)
seq = [
    "Topografia marca na CE-1 de cada pilar o nível do topo da mesa dos 2 consoles (cota do teto do nicho − 50).",
    "Soldar os CS-1 na CE-1 (filete 6, 2 lados verticais, ND-LET-PP03), eixo a 70 do eixo do pilar, mesa nivelada ±3; galvanização a frio no cordão.",
    "Regular em cada console o M16 de nível (topo da cabeça a G da mesa, 40 a 60) e o prisioneiro frontal (afastamento 25 ± 5); travar contraporca e trava química.",
    f"Içar a placa pelas alças AL-P, aproximar pela face interna com o teto dos nichos {MO['janela_R_mm']['G=50'][0]:g} a {MO['janela_R_mm']['G=50'][1]:g} mm acima da posição final (as abas passam por cima dos dentes) até o fundo encostar no prisioneiro.",
    "Baixar até o teto apoiar nas cabeças dos 2 M16 de nível; conferir nível, prumo e junta de 5 mm com a placa de baixo.",
    "Instalar os 2 pinos PT-1 na junta de baixo (ou as 2 travas PT-2 nas placas de pacote suspenso) antes de soltar o guindaste; selar a junta vertical (tarucel + PU)."]
y = pr.notas(XC, y - 4, seq, 190, titulo="SEQUÊNCIA DE MONTAGEM")
NM = FX["nicho_NC1"]
pr.notas(XC, y - 2, [
    "Ponta da placa = dente Gerber (bielas e tirantes, NBR 9062:2017 7.3/7.4): N3 tirante sobre o teto, N4 suspensão no plano médio até as cordoalhas de baixo, N5/N6 costura e ancoragem (os grampos do NC-1 ficam dentro deles), N7 estribo do nariz.",
    "Barras da ponta no plano médio, entre as cordoalhas (eixo a 2,64 cm das faces); estribos horizontais com cobrimento 2,0. Tela N1 da PP00 recortada no nicho.",
    "Medidas das peças Trejor (CS-1, NC-1, cartola) de pré-dimensionamento: confirmar com o catálogo 09 da Trejor antes da compra.",
    "Cotas metálicas em mm; concreto em cm. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."], 190)
json.dump(dict(kg_ponta_por_placa=KG_PONTA, kg_NC1=kg_nc, kg_CS1=kg_cs, kg_CE1=kg_ce, kg_PT1=kg_pt1, kg_PT2=kg_pt2, n=dict(NC1=2 * N_PL, CS1=N_CS, CE1=N_CE, PT1=N_PT1, PT2=N_PT2)),
          open("/home/claude/letsara/pranchas/pp01.json", "w"), indent=1)
av = pr.salvar("/home/claude/letsara/pranchas/ND-LET-PP01")
print("PP01", len([a for a in av if a[0] == "ERRO"]), "erros,", len(av), "avisos", [a for a in av if a[0] == "ERRO" or "sobrep" in a[1]][:14])
