"""ND-LET-PP05 — ombreira metálica OM-1 da porta da vista I (rev06d, DEC-028): U dobrado 125 × 80 × 6,3 abraçando a ponta das
placas I-13 / I-14, base rotulada no baldrame e topo preso na placa I-15 (sobre a porta, 12 cordoalhas) pela chapa CL-1.
Vistas cotadas, planta (corte a +0,60), detalhes da base e da CL-1, isométrico com balões, lista de materiais, fixadores,
sequência de montagem e notas. Cotas em mm. Geometria e esforços de calc_ombreira.py (ombreira.json)."""
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
import json
import numpy as np
import fechamento as FCH
import iso_nd as I
from prancha_nd import Prancha

f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
OM = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/ombreira.json"))
G = OM["GEO"]
U, B, CL = G["U"], G["BASE"], G["CL1"]
H, BF, T, NEO = U["h"], U["b"], U["t"], U["neo"]
LU, TB, FOL, JU = G["L_U_mm"], G["T_BASE_mm"], G["FOLGA_mm"], G["JUNTA_U_mm"]
ZT = TB + LU                                  # topo do U (2490)
ZI15 = 2500.0
ZP = G["Z_PAR_mm"]
CL0, CLL, ZCLU, ZCLB = CL["z0"] * 1000, CL["L"], CL["z_par_U"] * 1000, CL["z_bucha"] * 1000
HT = 0.45
YF = H / 2                                    # face externa das abas (62,5)
YP = 50.0                                     # faces da placa (±50)
XP = -JU                                      # ponta da placa (−20), x medido da face da alma voltada para a porta (+ para dentro do vão)

pr = Prancha("A1", dict(cliente=FCH.CLIENTE, obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="FIXAÇÃO DAS PLACAS — OMBREIRA METÁLICA OM-1 DA PORTA DA VISTA I (FABRICAÇÃO E MONTAGEM)",
                        desenho="ND-LET-PP05", folha="01/01", fase="PARA APROVAÇÃO", rev="06"))
pr.revisao("06", "18/10/2026", "EMISSÃO: OMBREIRA OM-1 EM U NA PORTA DA VISTA I (DEC-028)")
Q = pr.quadro
XC = Q[2] - 250
pr.cabecalho_peca("OM", f"OMBREIRA OM-1 — U 125 × 80 × 6,3 — L = {LU:.0f} mm — 2 PEÇAS (PORTA DA VISTA I, VÃO C–D)".replace(".", ","),
                  "abraça a ponta das placas I-13 / I-14; base rotulada no baldrame; topo na placa I-15 pela chapa CL-1 · cotas em mm",
                  largura=XC - Q[0] - 10)

# ================================================================== V1 — vista pela porta (alma), 1:10
v1 = pr.vista("VISTA PELA PORTA", (Q[0] + 70, Q[1] + 105), 10.0, titulo="OM-1 — VISTA PELA PORTA", subtitulo="face da alma; placa I-13 atrás (tracejada)", unidade="mm")
v1.chapa(-YF, TB, H, LU, 1.2)
v1.chapa(-100, 0, 200, TB, 0.6)
v1.ret(-YP, 0, 2 * YP, 1250 - 5, "OCULTA")
v1.ret(-YP, ZI15, 2 * YP, 330, "VISTA")
v1.hachura([(-YP, ZI15), (YP, ZI15), (YP, ZI15 + 330), (-YP, ZI15 + 330)], "AR-CONC", 0.03)
v1.ret(YF, CL0, CL["t"], CLL, "METALICA")
v1.linha((-150, 0), (150, 0), "TERRENO")
v1.cota_v([0, TB, 1250, ZT, ZI15], -100, -10, total=False)
v1.cota_v([0, ZP[0], ZP[1], ZCLU, ZCLB], 100, 12, total=False)
v1.cota_h([-100, -YF, YF, 100], 0, -10, total=False)
v1.chamada((0, 1800), (-32, 0), "1 — U 125 × 80 × 6,3")
v1.chamada((YF + 6, CL0 + 200), (14, 8), "3 — CL-1 (face interna)")
v1.chamada((0, ZI15 + 165), (-16, 10), "placa I-15 (+2,50)")
v1.chamada((-30, 700), (-32, -10), "placa I-13 (atrás)")
I.solda(v1, (-YF, TB), (-16, -16), a=5, tipo="filete", contorno=True, cauda="oficina")

# ================================================================== V2 — vista lateral pela face interna, 1:10
v2 = pr.vista("VISTA LATERAL", (Q[0] + 215, Q[1] + 105), 10.0, titulo="OM-1 — VISTA LATERAL (FACE INTERNA)", subtitulo="x a partir da face da alma; porta à direita", unidade="mm")
v2.chapa(-BF, TB, BF, LU, 1.2)
v2.chapa(XP, 0, 160 - XP, TB, 0.6)
v2.ret(-400, 0, 400 + XP, 1250 - 5, "VISTA")
v2.hachura([(-400, 0), (XP, 0), (XP, 1245), (-400, 1245)], "AR-CONC", 0.03)
v2.ret(-400, ZI15, 600, 330, "VISTA")
v2.hachura([(-400, ZI15), (200, ZI15), (200, ZI15 + 330), (-400, ZI15 + 330)], "AR-CONC", 0.03)
v2.ret(-BF / 2 - CL["b"] / 2, CL0, CL["b"], CLL, "METALICA")
for z in ZP:
    v2.circulo((-50, z), 9, "METALICA")
v2.circulo((-BF / 2, ZCLU), 9, "METALICA")
v2.poli([(-BF / 2 - 9, ZCLB - 20), (-BF / 2 + 9, ZCLB - 20), (-BF / 2 + 9, ZCLB + 20), (-BF / 2 - 9, ZCLB + 20)], "METALICA", fechada=True)
for x in B["ex"]:
    v2.ret(x - 8, -125, 16, 125 + TB + 20, "OCULTA")
v2.linha((-450, 0), (250, 0), "TERRENO")
v2.ret(0, 0, 200, 2470, "OCULTA")
v2.texto((100, 1500), "PORTA", "min", "MIDDLE_CENTER", rot=90)
v2.cota_h([-BF, XP, 0, 160], 0, -14, total=False)
v2.cota_v([0, ZP[0], ZP[1], 1250, ZCLU, ZT, ZI15, ZCLB, CL0 + CLL], 200, 10, total=False)
v2.chamada((-50, ZP[0]), (-22, 10), "4 — M16 passante (furo Ø18 nas 2 abas e na placa)")
v2.chamada((-BF / 2, ZCLB), (-24, 12), "CL-1: M16 em bucha BR-1 (oblongo vertical)")
v2.chamada((B["ex"][1], -60), (14, -8), "2 chumbadores químicos M16 hef 100")
v2.chamada((XP, 600), (10, -16), "ponta da placa a 20 do vão")

# ================================================================== V3 — planta (corte a +0,60), 1:2
v3 = pr.vista("PLANTA", (Q[0] + 385, Q[1] + 345), 2.0, titulo="CORTE HORIZONTAL A +0,60 (PLANTA)", subtitulo="lado de fora embaixo; vão da porta à direita", unidade="mm")
v3.ret(-250, -YP, 250 + XP, 2 * YP, "CORTADO")
v3.hachura([(-250, -YP), (XP, -YP), (XP, YP), (-250, YP)], "AR-CONC", 0.03)
U_pts = [(-BF, -YF), (0, -YF), (0, YF), (-BF, YF), (-BF, YF - T), (-T, YF - T), (-T, -YF + T), (-BF, -YF + T)]
v3.poli(U_pts, "METALICA", fechada=True); v3.hachura(U_pts, "ANSI31", 0.25, "METALICA")
for s_ in (-1, 1):
    pts = [(-BF + 10, s_ * YP), (XP - 2, s_ * YP), (XP - 2, s_ * (YP + NEO)), (-BF + 10, s_ * (YP + NEO))]
    v3.poli(pts, "VISTA", fechada=True); v3.hachura(pts, "SOLID", 1, "HACHURA")
v3.linha((-50, -YF - 22), (-50, YF + 22), "EIXO")
v3.ret(-50 - 12, YF, 24, 14, "METALICA"); v3.ret(-50 - 12, -YF - 14, 24, 14, "METALICA")
v3.ret(XP, -100, 160 - XP, 200, "OCULTA")
for x in B["ex"]:
    v3.circulo((x, 0), 8, "OCULTA")
v3.poli([(0, -40), (200, -40), (200, -25), (0, -25)], "OCULTA", fechada=True)
v3.cota_h([-BF, -50, XP, 0], -YF, -12, total=False)
v3.cota_v([-YF, -YP, YP, YF], -BF, -12, total=False)
v3.cota_v([-100, 100], 160, 10, total=False)
v3.chamada((-180, 10), (-6, 24), "placa I-13 (10 cm)")
v3.chamada((-60, -YP - 3), (-30, -16), "calço de neoprene 6 (2 por face)")
v3.chamada((-50, YF + 10), (8, 20), "M16 × 150 passante + 2 arruelas")
v3.chamada((-T / 2, -30), (22, -22), "alma: batente da porta parafusado aqui")
v3.chamada((100, 90), (12, 12), "chapa de base (tracejada)")
v3.texto((-200, YF + 30), "LADO DE DENTRO", "min", "BOTTOM_LEFT")
v3.texto((-240, -YF - 30), "LADO DE FORA", "min", "TOP_LEFT")

# ================================================================== V4 — chapa de base, 1:3 · V5 — CL-1, 1:3
v4 = pr.vista("BASE", (Q[0] + 330, Q[1] + 175), 3.0, titulo="2 — CHAPA DE BASE (PLANTA)", subtitulo="12,5 × 200 × 180 A36; U soldado na oficina", unidade="mm")
v4.chapa(XP, -100, 160 - XP, 200, HT)
v4.poli([(max(-BF, XP), -YF), (0, -YF), (0, YF), (max(-BF, XP), YF)], "VISTA")
for x in B["ex"]:
    v4.circulo((x, 0), 9, "METALICA")
v4.cota_h([XP, 0, B["ex"][0], B["ex"][1], 160], -100, -8, total=True)
v4.cota_v([-100, 0, 100], 160, 8, total=True)
v4.texto((95, -30), "2 furos Ø18", "nota", "TOP_CENTER")
v5 = pr.vista("CL-1", (Q[0] + 425, Q[1] + 130), 3.0, titulo="3 — CHAPA CL-1", subtitulo="12,5 × 100 × 360 A36", unidade="mm")
v5.chapa(0, 0, CL["b"], CLL, HT)
v5.circulo((50, ZCLU - CL0), 9, "METALICA")
v5.poli([(41, ZCLB - CL0 - 20), (59, ZCLB - CL0 - 20), (59, ZCLB - CL0 + 20), (41, ZCLB - CL0 + 20)], "METALICA", fechada=True)
v5.cota_v([0, ZCLU - CL0, ZCLB - CL0, CLL], CL["b"], 8, total=True)
v5.cota_h([0, 50, CL["b"]], 0, -8, total=False)
v5.texto((62, ZCLU - CL0), "Ø18 (aba do U)", "min", "MIDDLE_LEFT")
v5.texto((62, ZCLB - CL0), "oblongo 18 × 40 (I-15)", "min", "MIDDLE_LEFT")

# ================================================================== V6 — isométrico explodido com balões
cam = I.Camera((-1.0, -1.25, 0.75))
S = []
S.append(I.caixa(-T, 0, -YF, YF, TB, ZT, item=1, cor=I.AZUL_ACO))
S.append(I.caixa(-BF, -T, YF - T, YF, TB, ZT, item=1, cor=I.AZUL_ACO))
S.append(I.caixa(-BF, -T, -YF, -YF + T, TB, ZT, item=1, cor=I.AZUL_ACO))
S.append(I.caixa(XP, 160, -100, 100, -300, -300 + TB, item=2, cor=I.AZUL_ACO))
S.append(I.caixa(-BF / 2 - 50, -BF / 2 + 50, YF + 150, YF + 150 + CL["t"], CL0, CL0 + CLL, item=3, cor=I.AZUL_ACO))
for z in ZP:
    S.append(I.cilindro((-50, -YF - 180, z), "y", 8, 2 * YF + 360, item=4, cor=I.CINZA_PAR, liso=True))
for x in B["ex"]:
    S.append(I.cilindro((x, 0, -600), "z", 8, 160, item=6, cor=I.CINZA_PAR, liso=True))
S.append(I.caixa(-BF + 10, XP - 2, YP + 80, YP + 80 + NEO, 60, 1200, item=7, cor=(70, 70, 70)))
v6 = pr.vista("ISO", (Q[0] + 525, Q[1] + 140), 9.0, titulo="OM-1 — ISOMÉTRICO EXPLODIDO", subtitulo="balões = itens da lista", unidade="mm")
pj = I.desenhar_iso(v6, S, cam)
I.balao(v6, pj((0, 0, 1700)), (14, 6), 1)
I.balao(v6, pj((80, 0, -300)), (14, -6), 2)
I.balao(v6, pj((-BF / 2, YF + 150, CL0 + 300)), (-14, 8), 3)
I.balao(v6, pj((-50, YF + 180, ZP[1])), (-16, 4), 4)
I.balao(v6, pj((B["ex"][1], 0, -560)), (12, -6), 6)
I.balao(v6, pj((-40, YP + 80, 900)), (-16, -6), 7)

# ================================================================== tabelas
kgU = OM["U"]["kg_m"] * LU / 1000
kgB = TB * B["by"] * B["bx"] * 7.85e-6
kgC = CL["t"] * CL["b"] * CLL * 7.85e-6
itens = [[1, "PERFIL U DOBRADO", f"U 125×80×6,3 L={LU:.0f}; Ø18 nas abas +{ZP[0]:.0f}/+{ZP[1]:.0f}/+{ZCLU:.0f}", "ASTM A36", 1, f(kgU, 2)],
         [2, "CHAPA DE BASE", "12,5 × 200 × 180, 2 furos Ø18", "ASTM A36", 1, f(kgB, 2)],
         [3, "CHAPA DE LIGAÇÃO CL-1", "12,5 × 100 × 360, Ø18 + oblongo 18 × 40", "ASTM A36", 1, f(kgC, 2)],
         [4, "PARAFUSO PASSANTE", "M16 × 150 ISO 4014 + porca + 2 arruelas", "cl. 8.8 galv.", 2, "0,32"],
         [5, "PARAFUSO CL-1", "M16 × 40 ISO 4017 (aba do U) e M16 × 40 (bucha BR-1)", "cl. 8.8 galv.", 2, "0,10"],
         [6, "CHUMBADOR QUÍMICO", "barra M16 × 160 5.8 + adesivo epóxi, hef 100", "cl. 5.8 galv.", 2, "0,25"],
         [7, "CALÇO DE NEOPRENE", "6 × 50 × 1150 (2 por face da placa)", "neoprene dureza 60", 4, "0,40"],
         [8, "CALÇO DE CL-1", "12 × 100 × 100 (entre CL-1 e a placa I-15)", "ASTM A36", 1, "0,94"],
         [9, "BUCHA BR-1 (na placa I-15)", "M16 hef 70, embutida na fábrica", "aço zincado", 1, "0,10"]]
y = pr.tabela(XC, Q[3] - 6, "LISTA DE MATERIAIS — 1 OM-1 (OBRA: 2 PEÇAS IGUAIS)", ["Nº", "DESCRIÇÃO", "DIMENSÃO (mm)", "MATERIAL", "QTD", "kg/un"], itens,
              [9, 50, 94, 35, 12, 20], h_lin=5.4)
pr.texto(XC, y - 3.5, f"Aço por peça (itens 1–3 e 8): {f(kgU + kgB + kgC + 0.94, 1)} kg · obra: 2 peças = {f(2 * (kgU + kgB + kgC + 0.94), 0)} kg. Galvanização a fogo após a solda.", "nota", "TEXTO")
seq = [
    "Placas I-13 e I-14 montadas nos consoles CS-1, com a ponta do lado da porta a 20 mm do vão (furos passantes Ø18 deixados na fábrica a +0,31 e +0,94, a 30 mm da ponta).",
    "Colar os calços de neoprene nas 2 faces da ponta da placa; encaixar o U por cima da ponta, prumo ±2 mm, alma no alinhamento do vão (vão livre 1,80).",
    "Furar o baldrame pela chapa de base (broca Ø18, limpar o furo), aplicar o adesivo e colocar os 2 chumbadores; cura conforme o fabricante antes de apertar (80 N·m).",
    "Passar os 2 M16 pela aba, placa e aba; aperto à mão + 1/4 de volta (não esmagar o neoprene).",
    "Montar a placa I-15 (PP-05P) nos consoles, com 10 mm de folga sobre o topo do U.",
    "Instalar a CL-1 com o calço 12: M16 na aba interna do U e M16 na bucha BR-1 da I-15 pelo oblongo vertical (80 N·m, sem travar o oblongo).",
    "Fornecedor da esquadria: batente da porta parafusado na alma do U; caixilhos da faixa encaixados nas abas, com vedação PU."]
y = pr.notas(XC, y - 8, seq, 220, titulo="SEQUÊNCIA DE MONTAGEM")
pr.notas(XC, y - 4, [
    f"Função: dar apoio fora do plano à ponta das placas I-13 / I-14 do lado da porta e ao batente. Base rotulada (só cortante); topo na placa I-15, que tem 12 cordoalhas por receber o topo das 2 ombreiras (tipo PP-05P, ND-LET-PP00).",
    "A placa I-15 leva 2 buchas BR-1 M16 hef 70 na face interna, 150 acima da base, a 40 mm de cada lado do vão para dentro das placas (eixo da CL-1).",
    "Chapas A36; U dobrado a frio (raio interno 6); solda de oficina U × chapa de base: filete 5 E70XX em todo o contorno, inspeção visual 100 %. Galvanização a fogo (NBR 6323) depois da solda; furos galvanizados repassados.",
    "Tolerâncias NBR ISO 2768-1 classe m; furos Ø18 ± 0,3; oblongo 18 × 40 ± 0,5. Prumo da ombreira 2 mm em 2,5 m.",
    "Chumbador químico M16 5.8 hef 100 (Hilti HIT-RE 500 V4, Fischer FIS EM Plus ou equivalente), borda mínima 75 mm no baldrame; seguir o tempo de cura do fabricante.",
    "Medidas em mm. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."], 250)
av = pr.salvar("/home/claude/letsara/pranchas/ND-LET-PP05")
print("PP05", len([a for a in av if a[0] == "ERRO"]), "erros,", len(av), "avisos", [a for a in av if a[0] == "ERRO" or "sobrep" in a[1]][:14])
