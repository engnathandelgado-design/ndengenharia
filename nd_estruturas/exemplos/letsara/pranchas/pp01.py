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
Z_CORD = FCH.ZC_                                         # DEC-035: 10 fios Ø6 (5 por face), do placas.json

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
# rev06e (DEC-031): CE-1 da face C sai da fábrica com os consoles soldados e concretada com o pilar (CC-1 / CC-1E / CC-1D)
from collections import defaultdict as _dd
_grp = _dd(list)
for V in FCH.DADOS:
    for (x, z) in FCH.DADOS[V][1]:
        s_, w_, _ = min(FCH.VISTAS[V]["pil"], key=lambda p: abs(p[0] - x))
        _grp[(V, s_, w_, z)].append(x - s_)
N_CC = dict(CC2=0, CC1E=0, CC1D=0)
N_CE_OBRA = N_CS_OBRA = 0
for (V, s_, w_, z), xs in _grp.items():
    if GF.concretado(V, w_):
        N_CC["CC2" if len(xs) == 2 else ("CC1E" if xs[0] < 0 else "CC1D")] += 1
    else:
        N_CE_OBRA += 1; N_CS_OBRA += len(xs)
N_CS_FAB = N_CS - N_CS_OBRA
# DEC-044: CS-1 com calço (CS-1C 100 / CS-1D 75) — todos em CE-1 de obra; CE-1L (asas) nos pilares do eixo C das paredes G e C (fiada +6,25)
N_CAL = {m_: len(v_) for m_, v_ in FCH.CALCOS.items()}
N_CE1L = len({(V, p["k"]) for V, p in FCH.RECORTADAS})
KG_CAL = {m_: FX["calcos"][m_]["kg_caixa"] for m_ in N_CAL}
# NC-1 só nas pontas com console (as pontas do lado da porta da vista I não têm console nem nicho): NC-1 na ponta inicial (s0)
# e NC-1' (espelhado) na ponta final (s1) do comprimento da placa, como nas pranchas PP-x e no IFC
N_NC_E = N_NC_D = 0
for V in FCH.DADOS:
    cons = {(round(s_), round(z_)) for (s_, z_) in FCH.DADOS[V][1]}
    for pc in FCH.DADOS[V][0]:
        N_NC_E += (round(pc["s0"] + FCH.X_CS), round(pc["z0"] + FCH.Z_NC)) in cons
        N_NC_D += (round(pc["s1"] - FCH.X_CS), round(pc["z0"] + FCH.Z_NC)) in cons
N_NC = N_NC_E + N_NC_D


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
pr.cabecalho_peca("FX", f"FIXAÇÃO DAS PLACAS — {N_CS} CONSOLES CS-1 ({N_CS_FAB} CONCRETADOS) · {N_CE} CE-1 · {N_PT1} PT-1 · {N_PT2} PT-2",
                  "sistema Trejor (DEC-026): console concretado com o pilar na face C (CC-1, DEC-031) e soldado na obra nas faces laterais · placa típica ND-LET-PP00 · fabricação: NC-1 PP02, CS-1 PP03, CE-1/PT-1/PT-2 PP04 · metálica em mm, concreto em cm",
                  largura=XC - Q[0] - 10)

# ================================================================== D1 — armação da ponta (vista pela face interna, 1:10)
d1 = pr.vista("DETALHE 1", (Q[0] + 40, Q[1] + 300), 10, titulo="DETALHE 1 — ARMAÇÃO DA PONTA DA PLACA",
              subtitulo=f"vista pela face interna; as 2 pontas iguais (espelhadas); {FCH.PRT_} e tela N1 da ND-LET-PP00", unidade="cm")
d1.poli([(500, 0), (0, 0), (0, H), (500, H)], "VISTA"); d1.interrupcao((500, 0), (500, H))
for z in Z_CORD:
    d1.linha((10, z), (500, z), "ARM_PROT")
d1.ret(0, ZN0, NB, NH, "METALICA")
d1.hachura([(0, ZN0), (NB, ZN0), (NB, ZN1), (0, ZN1)], "ANSI31", 0.6, "METALICA")
d1.barra([(20, Z_N3), (500, Z_N3)], "N3", 2, 8, comp_cm=138, ponto_rotulo=(420, Z_N3), desloc=(14, 10))
d1.barra([(X_N4[0], 60), (X_N4[1], 60), (X_N4[1], 1220), (X_N4[0], 1220), (X_N4[0], 60)], "N4", 1, 8, comp_cm=256,
         ponto_rotulo=(X_N4[1], 600), desloc=(56, 0), camada="ARM_TRANSV")
d1.barra([(15, Z_N5), (175, Z_N5)], "N5", 1, 6.3, comp_cm=54, ponto_rotulo=(100, Z_N5), desloc=(36, 18), camada="ARM_TRANSV")
d1.barra([(15, Z_N6), (175, Z_N6)], "N6", 1, 6.3, comp_cm=54, ponto_rotulo=(100, Z_N6), desloc=(60, -10), camada="ARM_TRANSV")
d1.barra([(X_N7[0], 1050), (X_N7[1], 1050), (X_N7[1], 1225), (X_N7[0], 1225), (X_N7[0], 1050)], "N7", 1, 6.3, comp_cm=46,
         ponto_rotulo=(X_N7[1], 1180), desloc=(30, 16), camada="ARM_TRANSV")
d1.cota_h([0, NB, X_N4[0], X_N4[1], 500], 0, -10, total=False)
d1.cota_v([0, 60, Z_N6, ZN0, ZN1, Z_N3, 1220, H], 0, -10, total=False)
for (xa, xb) in GF.N["x_gr"]:
    d1.poli([(xa, ZN1), (xa, ZN1 + GF.N["h_gr_teto"]), (xb, ZN1 + GF.N["h_gr_teto"]), (xb, ZN1)], "METALICA")
    d1.poli([(xa, ZN0), (xa, ZN0 - GF.N["h_gr_base"]), (xb, ZN0 - GF.N["h_gr_base"]), (xb, ZN0)], "METALICA")
d1.chamada((60, FCH.Z_NC), (60, -6), "NC-1 (ND-LET-PP02) — tela N1 recortada no nicho")
d1.chamada((GF.N["x_gr"][1][1], ZN1 + 30), (60, 1), "grampos do NC-1 dentro do N5 / N6")
d1.chamada((300, 781), (40, -12), f"C1 {FCH.PRT_} (ND-LET-PP00)")

# ================================================================== D2 — corte B-B pela ponta (1:5)
d2 = pr.vista("DETALHE 2", (Q[0] + 265, Q[1] + 290), 5, titulo="DETALHE 2 — CORTE B-B NA PONTA",
              subtitulo=f"espessura da placa (face interna à esquerda): barras no plano médio, entre os {FCH.PRT_}", unidade="cm")
pts = [(0, 700), (E, 700), (E, H), (0, H)]
d2.poli(pts, "CORTADO", fechada=True); d2.hachura(pts, "AR-CONC", 0.03)
d2.interrupcao((0, 700), (E, 700))
for z in [z_ for z_ in Z_CORD if z_ > 700]:
    for y in (FCH.EX_, E - FCH.EX_):
        d2.ponto_barra((y, z), FCH.DC_, "ARM_PROT_SECAO")
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
d2.cota_v([700, Z_N6, ZN0, ZN1, Z_N3, H], E, 10, total=False)
d2.chamada((50, 900), (36, -22), "N4 / N7 no plano médio (y = 5)")
d2.chamada((60, Z_N3), (30, 4), "N3 — 2 Ø8 (y = 4 e 6)")
d2.chamada((70, Z_N5), (36, 22), f"N5 Ø6,3 fechado (horizontal), {f((Z_N5 - Z_N3) / 10)} acima do N3, cobrimento 2,0")
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
d3.chapa(-GF.TCE, -55.5 - 165, GF.TCE, 330, 0.6)                                 # CE-1 embutida
for z in (-140, 140):
    d3.ret(-GF.TCE - 140, -55.5 + z - 8, 140, 16, "METALICA")
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
d3.cota_v([co["z0"], zt_, zf, 0, G0, zn1], a0 + 100, 16, total=False)
d3.cota_v([co["z0"], co["z1"]], a0 + 100, 26, total=False)                      # rev08: altura das costas do CS-1
d3.chamada((-60, 100), (-14, 18), "pilar")
d3.chamada((a0 + 70, -200), (14, -12), "placa 10 cm (ND-LET-PP00)")
d3.chamada((-8, -55.5 - 120), (-30, -26), "CE-1 (PP04)")
d3.chamada((8, -120), (-24, -32), "CS-1 (PP03)")
d3.chamada((a0 + 30, zn1 - 6), (70, 26), "NC-1 (PP02)")
d3.chamada((a0 + 6, zn1 - 30), (-18, 40), "abas laterais (tracejadas)")
d3.chamada((yt, zf), (56, -16), "prisioneiro no fundo")
d3.chamada((yn, G0), (-10, 40), "M16 de nível sob o teto")

# ================================================================== D4 — planta do conjunto (1:2), logo abaixo do teto
d4 = pr.vista("DETALHE 4", (Q[0] + 380, Q[1] + 145), 2.0, titulo="DETALHE 4 — PLANTA DO CONJUNTO", subtitulo="corte logo abaixo do teto do nicho; posição nominal", unidade="mm")
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
AX = xp - FCH.JUNTA / 2                                    # rev06e: eixo do pilar a 10 da ponta (junta 20) → console a 80 do eixo
d4.chapa(AX - 190, -16, 380, 16, 0.6)
d4.poli([(AX - 200, -16), (AX - 200, -120), (AX + 200, -120), (AX + 200, -16)], "CORTADO")
d4.interrupcao((AX - 200, -120), (AX + 200, -120))
d4.cota_h([xp, xp + N["aba_e"][1], xp + N["aba_d"][0], xp + N["aba_d"][1], xp + N["B"]], a0 + 100, 10, total=False)
d4.cota_h([AX, 0], -120, -8, total=False)
XV = AX - FCH.JUNTA / 2                                    # ponta da placa vizinha
d4.poli([(XV, a0), (XV - 190, a0), (XV - 190, a0 + 100), (XV, a0 + 100)], "OCULTA", fechada=True)
d4.ret(XV - N["B"] / 2 - co["b"] / 2, 0, co["b"], co["t"], "OCULTA")
d4.chamada((XV - 100, a0 + 95), (4, 16), "placa vizinha (NC-1' e CS-1 espelhados)")
d4.cota_v([-16, 0, a0, a0 + N["t_aba"], de["y0"], de["y0"] + de["t"], a0 + N["P"], a0 + 100], xp + 320, 10, total=False)
d4.chamada((xp, a0 + 80), (10, 44), f"ponta da placa (junta {FCH.JUNTA:g} no eixo do pilar)")
d4.chamada((0, yn), (64, -40), "M16 de nível (meio livre, sem aba)")
d4.eixo((AX, -120), (AX, a0 + 100), ext=10)
d4.texto((AX, -150), "eixo do pilar", "nota", "TOP_CENTER")
d4.chamada((60, -70), (14, -10), "pilar")

# ================================================================== D5 — sequência de montagem (cortes esquemáticos 1:5)
MOJ = FX["montagem_CS1_NC1"]["janela_R_mm"][f"G={T['G']:g}"]
R_m = round((MOJ[0] + MOJ[1]) / 2)


def esquema(v, dy, dz, seta=None):
    v.chapa(-GF.TCE, -55.5 - 165, GF.TCE, 330, 0.8)
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
              subtitulo=f"esquema; janela R = {MOJ[0]:g} a {MOJ[1]:g} com G = {T['G']:g}".replace(".", ","), unidade="mm")
O5 = d5.o
for k, (tit, dy_, dz_, st) in enumerate(ESQ):
    d5.o = (O5[0] + (0, 72, 116)[k], O5[1])                                      # rev08: o passo 1 (placa afastada 150) não encosta no passo 2
    esquema(d5, dy_, dz_, st)
    d5.texto(((-GF.TCE + a0 + dy_ + 100) / 2, 300), tit, "nota", "BOTTOM_CENTER")
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
rows = [["NC-1 / NC-1'", "caixa soldada + grampos (pontas com console)", "ND-LET-PP02", N_NC, f(kg_nc, 2), f(kg_nc * N_NC, 0)],
        ["CC-1", "CE-1 + 2 CS-1 soldados na fábrica (face C, concretado)", "PP03/PP04", N_CC["CC2"], f(kg_ce + 2 * kg_cs, 2), f((kg_ce + 2 * kg_cs) * N_CC["CC2"], 0)],
        ["CC-1E", "CE-1 + 1 CS-1 à esquerda (face C, concretado)", "PP03/PP04", N_CC["CC1E"], f(kg_ce + kg_cs, 2), f((kg_ce + kg_cs) * N_CC["CC1E"], 0)],
        ["CC-1D", "CE-1 + 1 CS-1 à direita (face C, concretado)", "PP03/PP04", N_CC["CC1D"], f(kg_ce + kg_cs, 2), f((kg_ce + kg_cs) * N_CC["CC1D"], 0)],
        ["CE-1", "chapa de espera + 4 pinos (faces laterais, rente)", "ND-LET-PP04", N_CE_OBRA - N_CE1L, f(kg_ce, 2), f(kg_ce * (N_CE_OBRA - N_CE1L), 0)],
        ["CE-1L", "CE-1 840 × 330 com asas (P8A e P11, fiada +6,25; DEC-044)", "ND-LET-PP06", N_CE1L, f(kg_ce + kg_ch(840 - 380, 330, GF.TCE), 2), f((kg_ce + kg_ch(840 - 380, 330, GF.TCE)) * N_CE1L, 0)],
        ["CS-1", "console soldado na obra na CE-1 lateral", "ND-LET-PP03", N_CS_OBRA - sum(N_CAL.values()), f(kg_cs, 2), f(kg_cs * (N_CS_OBRA - sum(N_CAL.values())), 0)],
        ["CS-1C", "CS-1 + caixa de calço 100 (cantos, PL-02/PL-06; DEC-044)", "ND-LET-PP06", N_CAL.get("CS-1C", 0), f(kg_cs + KG_CAL.get("CS-1C", 0), 2), f((kg_cs + KG_CAL.get("CS-1C", 0)) * N_CAL.get("CS-1C", 0), 0)],
        ["CS-1D", "CS-1 + caixa de calço 75 (PG-02/PG-04; DEC-044)", "ND-LET-PP06", N_CAL.get("CS-1D", 0), f(kg_cs + KG_CAL.get("CS-1D", 0), 2), f((kg_cs + KG_CAL.get("CS-1D", 0)) * N_CAL.get("CS-1D", 0), 0)],
        ["PT-1", "cartola + 2 M16 + 2 arruelas", "ND-LET-PP04", N_PT1, f(kg_pt1, 2), f(kg_pt1 * N_PT1, 0)],
        ["PT-2", "cantoneira + 2 M16 + 2 arruelas", "ND-LET-PP04", N_PT2, f(kg_pt2, 2), f(kg_pt2 * N_PT2, 0)]]
OMJ = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/ombreira.json"))
kg_om = OMJ["kg_un"] + 0.94 + 0.32 * 2 + 0.25 * 2 + 0.10 * 2
rows.append(["OM-1", "ombreira em U + base + CL-1 (porta da vista I)", "ND-LET-PP05", 2, f(kg_om, 2), f(kg_om * 2, 0)])
tot = kg_nc * N_NC + kg_cs * N_CS + kg_ce * N_CE + kg_pt1 * N_PT1 + kg_pt2 * N_PT2 + kg_om * 2 + sum(KG_CAL[m_] * N_CAL[m_] for m_ in N_CAL) + kg_ch(840 - 380, 330, GF.TCE) * N_CE1L
rows.append(["", "total da fixação (sem luvas e buchas)", "", "", "", f(tot, 0)])
y = pr.tabela(XC, y - 8, "RESUMO DAS PEÇAS METÁLICAS — OBRA", ["MARCA", "COMPOSIÇÃO", "FOLHA", "QT", "kg/un", "kg"], rows, [24, 76, 26, 14, 20, 30], h_lin=5.2, destaque_ultima=True)
MO = FX["montagem_CS1_NC1"]
fo = MO["folgas_mm"]
tol = [["afastamento placa–pilar (a)", f"{T['a']:g} ± {T['a_tol']:g}", "prisioneiro frontal"],
       ["G: mesa → teto do nicho", f"{T['G']:g} ± {T['G_tol']:g}", "M16 de nível"],
       ["posição do console × nicho (x)", f"± {T['x_tol']:g}", "fábrica ±5, pilar ±10, placa ±5"],
       ["engate aba × dente (G máx.)", f"≥ {fo['engate aba–dente com G máximo (z)']:g}", "sucção"],
       ["folga aba × dente (a máx.)", f"≥ {fo['aba atrás x dente (y)']:g}", "montagem"],
       ["janela de montagem R", f"{MOJ[0]:g} a {MOJ[1]:g} (G = {T['G']:g})", "teto acima da final"]]
y = pr.tabela(XC, y - 4, "TOLERÂNCIAS E FOLGAS DE MONTAGEM (mm)", ["ITEM", "VALOR", "AJUSTE / OBS."], tol, [70, 60, 60], h_lin=5.0)
seq = [
    f"Face C dos pilares: consoles já concretados (CC-1). Topografia confere o nível real do topo da mesa de cada console e calcula G para cada um (G nominal {T['G']:g}).",
    f"Faces laterais (CE-1 rente): topografia marca o nível; soldar o CS-1 na CE-1 (filete {FX['solda']['filete_mm']:g}, 2 lados verticais, ND-LET-PP03), eixo a {FCH.JUNTA // 2 + FCH.X_CS:g} do eixo do pilar, mesa nivelada ±3; galvanização a frio no cordão.",
    f"Regular em cada console o M16 de nível (topo da cabeça a G da mesa, {T['G'] - T['G_tol']:g} a {T['G'] + T['G_tol']:g}) e o prisioneiro frontal (afastamento {T['a']:g} ± {T['a_tol']:g}); travar contraporca e trava química.",
    f"Içar a placa de pé pelos 4 IZ-1 da face interna com balancim duplo (ND-LET-MON03 det. 2c), aproximar pela face interna com o teto dos nichos {MOJ[0]:g} a {MOJ[1]:g} mm acima da posição final (as abas passam por cima dos dentes) até o fundo encostar no prisioneiro.",
    "Baixar até o teto apoiar nas cabeças dos 2 M16 de nível; conferir nível, prumo e junta de 5 mm com a placa de baixo.",
    "Pinos guia PT-1: antes de montar a placa de cima, parafusar as 2 cartolas no topo da placa de baixo (M16 só nela); a placa de cima desce guiada, sem parafuso — o PT-1 não transmite esforço (DEC-035). Nas placas de pacote suspenso, apertar as 2 travas PT-2 no pé antes de soltar o guindaste. Selar a junta vertical (tarucel + PU).",
    "Soltar o guindaste e retirar os 4 cabeçotes dos IZ-1; tampar os insertos (tampa plástica); só então montar a placa de cima."]
y = pr.notas(XC, y - 4, seq, 190, titulo="SEQUÊNCIA DE MONTAGEM")
NM = FX["nicho_NC1"]
pr.notas(XC, y - 2, [
    "Ponta da placa = dente Gerber (bielas e tirantes, NBR 9062:2017 7.3/7.4): N3 tirante sobre o teto, N4 suspensão no plano médio até os fios de baixo, N5/N6 costura e ancoragem (os grampos do NC-1 ficam dentro deles), N7 estribo do nariz.",
    f"Barras da ponta no plano médio, entre os {FCH.PRT_} (eixo a {f(FCH.EX_ / 10, 2)} cm das faces); estribos horizontais com cobrimento 2,0. Tela N1 da PP00 recortada no nicho.",
    "Medidas das peças Trejor (CS-1, NC-1, cartola) de pré-dimensionamento: confirmar com o catálogo 09 da Trejor antes da compra.",
    "Cotas metálicas em mm; concreto em cm."], 190)
json.dump(dict(kg_ponta_por_placa=KG_PONTA, kg_NC1=kg_nc, kg_CS1=kg_cs, kg_CE1=kg_ce, kg_PT1=kg_pt1, kg_PT2=kg_pt2, kg_OM1=kg_om, n=dict(OM1=2, NC1=N_NC, NC1_E=N_NC_E, NC1_D=N_NC_D, CS1=N_CS, CS1_obra=N_CS_OBRA, CS1_fabrica=N_CS_FAB, CS1C=N_CAL.get("CS-1C", 0), CS1D=N_CAL.get("CS-1D", 0), CE1=N_CE, CE1_obra=N_CE_OBRA, CE1L=N_CE1L, CC1=N_CC["CC2"], CC1E=N_CC["CC1E"], CC1D=N_CC["CC1D"], PT1=N_PT1, PT2=N_PT2)),
          open("/home/claude/letsara/pranchas/pp01.json", "w"), indent=1)
FCH.chave_todas(pr)                                     # rev11 (checklist 6): planta-chave com as paredes nas cores A–J
av = pr.salvar("/home/claude/letsara/pranchas/ND-LET-PP01")
print("PP01", len([a for a in av if a[0] == "ERRO"]), "erros,", len(av), "avisos", av)
