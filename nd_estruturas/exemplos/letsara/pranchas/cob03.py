"""ND-LET-COB03 — cobertura: calha de platibanda do eixo A, descidas, extravasores e rufos (rev06, DEC-025).
Fonte do dimensionamento: calc_calha.py (calha.json, NBR 10844:1989). Metálica em mm, níveis em m. A1."""
import json, math
from prancha_nd import Prancha
from cob_comum import cabecalho, XT, PASSO, H_TERCA, B_TERCA, B_INF, D_SUP, D_INF, YLmm, LG, f

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
CH = json.load(open(AQ + "calha.json"))
pr = Prancha("A1", cabecalho("ND-LET-COB03", "03/04", "COBERTURA — CALHA DO EIXO A, DESCIDAS, EXTRAVASORES E RUFOS"))
pr.revisao("06", "18/10/2026", "CALHA 300×150 NO EIXO A; 9 DESCIDAS Ø200; RUFOS TRANSFERIDOS PARA A ND-LET-COB04 (FUNILARIA)")
C45 = math.cos(math.radians(45))
I3 = 0.03
ZREF = 8000                                             # níveis desenhados a partir de +8,000
Z0 = LG["Z0_TS"] * 1000 - ZREF                          # fundo da TS-01 em x = 0 (mm)
zts = lambda x: Z0 + I3 * x + 900                       # topo da TS-01 (mm, x do eixo A)
X_T0 = XT[0]                                            # alma da 1ª terça (490)
ZT0 = zts(X_T0 + 27) + 10                               # fundo da 1ª terça
PAC = [("TP-40 #0,65", 40), ("cartola + lã FSR 32", 40), ("zipada 455 #0,50", 70), ("painel solar", 110)]
BC, HC = 300, 150
XC0 = 20                                                # face de trás da calha (20 da cabeça do pilar)
Z_TOP_CALHA = ZT0 + H_TERCA - I3 * (X_T0 - 250) - 40    # borda da calha 40 mm abaixo da face inferior da telha na ponta
Z_FUNDO = Z_TOP_CALHA - HC
PLAT = 10000 - ZREF


def z_terca(v, x0, z0):
    pts = [(x0 + (B_INF - D_INF * C45), z0 + D_INF * C45), (x0 + B_INF, z0), (x0, z0), (x0, z0 + H_TERCA), (x0 - B_TERCA, z0 + H_TERCA),
           (x0 - B_TERCA + D_SUP * C45, z0 + H_TERCA - D_SUP * C45)]
    v.poli(pts, "METALICA")


def telha(v, x0, x1):
    zz = 0
    for nome, h in PAC:
        z_a, z_b = ZT0 + H_TERCA + zz - I3 * (X_T0 - x0), ZT0 + H_TERCA + zz - I3 * (X_T0 - x1)
        v.poli([(x0, z_a), (x1, z_b), (x1, z_b + h), (x0, z_a + h)], "METALICA", True)
        zz += h
    return zz


def calha(v):
    pts = [(XC0 + 60, Z_TOP_CALHA + 120), (XC0, Z_TOP_CALHA + 120), (XC0, Z_FUNDO), (XC0 + BC, Z_FUNDO), (XC0 + BC, Z_TOP_CALHA), (XC0 + BC + 25, Z_TOP_CALHA)]
    v.poli(pts, "METALICA")
    v.linha((XC0 + 4, Z_FUNDO + 100), (XC0 + BC - 4, Z_FUNDO + 100), "OCULTA")      # lâmina de projeto


def suporte(v):
    v.poli([(X_T0 - 3, ZT0 + 60), (X_T0 - 60, ZT0 + 60), (XC0 + BC + 6, Z_FUNDO - 6), (XC0 - 6, Z_FUNDO - 6), (XC0 - 6, Z_FUNDO + 90)], "METALICA")
    for zz in (ZT0 + 45, ZT0 + 85):
        v.circulo((X_T0 - 3, zz), 5, "METALICA")


# ------------------------------------------------------------------ CORTE 1 — ENTRE PILARES (placa da platibanda)
c1 = pr.vista("CORTE 1", (140, 300), 5, titulo="CORTE 1 — CALHA NO EIXO A, ENTRE PILARES", subtitulo="seção transversal à calha; placa de 10 cm por fora dos pilares (rufos na ND-LET-COB04); cotas em mm")
ZB = Z_FUNDO - 250
ZTOPO = Z_TOP_CALHA + 650
c1.ret(-400, ZB, 100, ZTOPO - ZB, "CORTADO"); c1.hachura([(-400, ZB), (-300, ZB), (-300, ZTOPO), (-400, ZTOPO)], "AR-CONC", 0.03)
c1.interrupcao((-420, ZTOPO), (-280, ZTOPO))
c1.poli([(-300, Z_TOP_CALHA + 220), (-300, Z_TOP_CALHA + 160), (XC0 - 10, Z_TOP_CALHA + 130), (XC0 - 10, Z_TOP_CALHA + 60)], "METALICA")   # RF-2
z_terca(c1, X_T0, ZT0)
telha(c1, 250, 900)
calha(c1); suporte(c1)
c1.linha((0, ZB), (0, ZTOPO), "EIXO")
c1.cota_h([-400, -300, 0, XC0, XC0 + BC, X_T0 - B_TERCA, X_T0], ZB, -12, total=False)
c1.cota_v([Z_FUNDO, Z_FUNDO + 100, Z_TOP_CALHA], XC0 + BC, 14, total=False)
c1.texto((0, ZTOPO + 40), "eixo A (face da cabeça do P1)", "min", "BOTTOM_CENTER")
c1.texto((-450, Z_FUNDO), "+" + f((Z_FUNDO + ZREF) / 1000, 3), "min", "MIDDLE_RIGHT")
c1.texto((-450, Z_TOP_CALHA), "+" + f((Z_TOP_CALHA + ZREF) / 1000, 3), "min", "MIDDLE_RIGHT")
c1.chamada((-150, Z_TOP_CALHA + 180), (40, 66), "RF-2 rufo de fechamento placa → calha")
c1.chamada((XC0 + BC / 2, Z_FUNDO), (6, -36), f"calha {BC} × {HC} #18, i = 0,5 %")
c1.chamada((XC0 + BC / 2, Z_FUNDO + 100), (-40, -40), "lâmina de projeto 100 (folga 50)")
c1.chamada((X_T0 - 40, ZT0 + 60), (26, -40), "SC-1 ferro chato 38×6,35 c/750, 2 M10 na alma da 1ª terça")
c1.chamada((280, ZT0 + H_TERCA + 30), (10, 52), "telha avança 150 além da aba da terça; pingadeira 100 dentro da calha")
c1.chamada((X_T0, ZT0 + 150), (20, 12), "1ª terça Z 302 (40 cm livres)")

# ------------------------------------------------------------------ CORTE 2 — NA LINHA DO PILAR (descida ao lado)
c2 = pr.vista("CORTE 2", (405, 300), 10, titulo="CORTE 2 — CALHA NA LINHA DO PILAR P1", subtitulo="cabeça do pilar 40×30 até +10,00; TS-01 no recuo; descida Ø200 ao lado do pilar")
REC = LG["REC"][0] * 1000 - ZREF
c2.ret(-300, ZB, 600, REC - ZB, "CORTADO"); c2.hachura([(-300, ZB), (300, ZB), (300, REC), (-300, REC)], "AR-CONC", 0.03)
c2.ret(-300, REC, 300, PLAT - REC, "CORTADO"); c2.hachura([(-300, REC), (0, REC), (0, PLAT), (-300, PLAT)], "AR-CONC", 0.03)
c2.ret(-400, ZB, 100, PLAT - ZB, "VISTA")
c2.poli([(25, REC + 10), (900, REC + 10 + I3 * 875), (900, zts(900)), (25, zts(25))], "VISTA", True)              # TS-01
c2.poli([(-420, PLAT - 60), (-420, PLAT + 8), (-280, PLAT + 8), (-280, PLAT - 60)], "METALICA")
c2.poli([(-40, Z_TOP_CALHA + 200), (-10, Z_TOP_CALHA + 200), (-10, Z_TOP_CALHA + 130), (XC0 - 10, Z_TOP_CALHA + 130), (XC0 - 10, Z_TOP_CALHA + 60)], "METALICA")
z_terca(c2, X_T0, ZT0)
telha(c2, 250, 900)
calha(c2)
c2.ret(XC0 + 50, ZB, 200, Z_FUNDO - ZB, "OCULTA")                                                               # descida (atrás, y + 350)
c2.cota_v([REC, zts(25), Z_FUNDO, Z_TOP_CALHA, PLAT], -400, -8, total=False)
c2.chamada((XC0 + 150, Z_FUNDO - 300), (78, -56), "descida Ø200 a 0,35 m da linha, bocal no fundo")
c2.chamada((-150, PLAT - 400), (24, 10), "cabeça do P1 40×30 (platibanda)")
c2.chamada((-25, Z_TOP_CALHA + 170), (30, 40), "RF-2 contra-rufo na face da cabeça, vedado com PU")
c2.chamada((450, zts(450) - 300), (50, -4), "TS-01 no assento do pilar")
for z, t in ((REC, "+" + f((REC + ZREF) / 1000, 3)), (Z_FUNDO, "+" + f((Z_FUNDO + ZREF) / 1000, 3)), (Z_TOP_CALHA, "+" + f((Z_TOP_CALHA + ZREF) / 1000, 3)), (PLAT, "+10,000")):
    c2.texto((-600, z), t, "min", "MIDDLE_RIGHT")

# ------------------------------------------------------------------ PLANTA PARCIAL 1:50 (linhas 1 a 3)
pp = pr.vista("PLANTA", (606, 296), 100, titulo="PLANTA PARCIAL — EIXO A, LINHAS 1 E 2 (TÍPICO)", subtitulo="saídas junto aos pilares P1 de todas as linhas; caimento 0,5 % para as saídas")
Y3 = YLmm[1] + 3000
pp.ret(-400, -300, 100, Y3 + 300, "CORTADO")
for y in YLmm[:2]:
    pp.ret(-300, y - 200, 600, 400, "CORTADO")
    pp.ret(25, y - 200, 1500, 400, "VISTA")
    pp.circulo((XC0 + 150, y + (535 if y == YLmm[1] else 350)), 100, "METALICA")   # 22/10: linha 2 — na frente da parede G
    pp.linha((-900, y), (2000, y), "EIXO")
pp.ret(XC0, -150, BC, Y3 + 150, "METALICA")
pp.linha((X_T0 - B_TERCA, -110), (X_T0 - B_TERCA, Y3), "METALICA"); pp.linha((X_T0 + B_INF, -110), (X_T0 + B_INF, Y3), "METALICA")
for y0, y1 in zip(YLmm[:1], YLmm[1:2]):
    ym = (y0 + y1) / 2
    pp.linha((XC0 + 150, ym - 1500), (XC0 + 150, y0 + 900), "INDICACAO"); pp.linha((XC0 + 150, ym + 1500), (XC0 + 150, y1 - 900), "INDICACAO")
    pp.texto((XC0 + 150, ym), "i = 0,5 %", "min", "MIDDLE_CENTER", rot=90)
pp.chamada((XC0 + 150, YLmm[1] + 350), (30, 6), "saída / descida Ø200 (9 no total)")
pp.chamada((-350, YLmm[0] - 200), (20, -12), "extravasor Ø100 (saída por dentro da obra)")
pp.chamada((XC0 + BC, YLmm[1] + 2400), (14, 24), f"calha {BC}×{HC} contínua, juntas a cada ≈ 20 m")

# ------------------------------------------------------------------ DETALHE SC-1 e RUFOS
d = pr.vista("SC-1", (170, 150), 5, titulo="DETALHE 3 — SUPORTE DA CALHA SC-1", subtitulo="ferro chato 38 × 6,35 A36 galvanizado, a cada 750 mm")
d.poli([(0, 0), (-60, 0), (-60 - (X_T0 - 60 - XC0 - BC - 6), -(ZT0 + 60 - Z_FUNDO + 6)), (-X_T0 + XC0 - 6, -(ZT0 + 60 - Z_FUNDO + 6)), (-X_T0 + XC0 - 6, -(ZT0 + 60 - Z_FUNDO + 6) + 96)], "METALICA")
d.ret(-3, -40, 3, 400, "METALICA")
for zz in (-15, 25):
    d.circulo((0, zz), 5, "METALICA")
d.chamada((0, 25), (14, 10), "2 M10 + arruelas na alma da 1ª terça (furos Ø12 de fábrica)")
d.chamada((-300, -(ZT0 + 60 - Z_FUNDO + 6)), (10, -16), "berço da calha (dobrado, sem solda)")
# ------------------------------------------------------------------ tabelas e notas
x0, y = pr.quadro[2] - 196, pr.quadro[3] - 6
cc, ca, de, su = CH["contribuicao"], CH["calha"], CH["descidas"], CH["suportes"]
L_desc = 9 * ((Z_FUNDO + ZREF) / 1000 + 0.5)
lin = [["CA-1", f"{ca['L_m']:.0f} m", f"calha {BC}×{HC}, chapa galv. 1,25, desenv. 700", "eixo A, linhas 1 a 9"],
       ["SC-1", f"{su['n']}", "suporte ferro chato 38×6,35 A36 galv. + 2 M10", "c/750, na 1ª terça"],
       ["BO-1", f"{de['n']}", "bocal de saída Ø200 com ralo hemisférico", "junto aos pilares P1"],
       ["DE-1", f"{math.ceil(L_desc / 6)} barras", f"tubo PVC Ø200 série R (≈ {L_desc:.0f} m em barras de 6 m)".replace(".", ","), "descidas até a caixa de areia"],
       ["EX-1", "2", "extravasor Ø100 (tubo + flange); furo na placa feito na obra", "pontas da calha, fachadas 1 e 9"]]
y = pr.tabela(x0, y, "LISTA DE MATERIAIS — CALHA E DESCIDAS (RUFOS NA ND-LET-COB04)", ["MARCA", "QT", "DESCRIÇÃO", "ONDE"], lin, [16, 24, 100, 56])
notas = [f"Dimensionamento (NBR 10844:1989): intensidade I = {CH['chuva']['I_mm_h']:.0f} mm/h (T = 5 anos) — CONFIRMAR com a tabela 5 / dados da cidade da obra; área de contribuição {cc['A_por_m_m2']} m² por metro de calha (água de 39,50 m a 3 %), {cc['area_total_m2']:.0f} m² no total.",
         f"Calha {BC} × {HC}, i = 0,5 %, n = 0,011: capacidade {ca['Q_cap_L_s']} L/s com lâmina de 100 mm ≥ {cc['Q_lado_L_s']} L/s que chega a cada saída por lado (uso {ca['uso']}). Fundo com caimento de 0,5 % para as saídas (25 mm por meio vão), dado pelos berços dos SC-1.",
         f"Descidas Ø200 nas 9 linhas: capacidade da saída {de['Q_cap_L_s']} L/s ≥ {cc['Q_saida_L_s']} L/s (uso {de['uso']}); descida aparente ao lado do pilar P1 (y = linha + 0,35 m, fora da TS-01; na linha 2, y = linha + 0,535 m, na frente da parede interna G, que ocupa a faixa de 0,325 a 0,425 m), presa por abraçadeiras em buchas, até a caixa de areia (projeto de drenagem).",
         "Espaço livre de 40 cm entre a face da cabeça dos pilares P1 e a aba da 1ª terça (ND-LET-COB01); a calha fica de 20 a 320 mm do eixo A. A telha avança 150 mm além da aba da terça, com pingadeira 100 mm dentro da calha.",
         "Extravasores Ø100 nas duas pontas da calha (fachadas 1 e 9), 50 mm abaixo da borda, para a água sair pela fachada se uma saída entupir.",
         "DEC-042: os pilares de canto (linhas 1 e 9) têm seção cheia 40 × 60 até +10,00: a calha começa e termina a 22 cm do eixo das linhas 1 e 9, com a cabeceira a 2 cm da face lateral do pilar; saída do extravasor por dentro da obra; furo na placa executado na obra.",
         "Juntas de dilatação da calha a cada ≈ 20 m (sobre as linhas 3, 5 e 7), com tampa e selante; emendas rebitadas e vedadas com PU (sem solda).",
         "Rufos, pingadeira, encostos e capa da platibanda feitos por funileiro na obra (chapa dobrada, não de catálogo): ND-LET-COB04 (RF-2/RF-2C da calha no det. 1 e 2 de lá).",
         "Carga da calha cheia na 1ª terça (0,12 kN/m de chapa + 0,45 kN/m de água) considerada no modelo integrado r05.",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(x0, y - 4, notas, 190)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-COB03")
for a in avisos:
    if a[0] == "ERRO" or "sobrep" in a[1] or "sai do quadro" in a[1]:
        print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
