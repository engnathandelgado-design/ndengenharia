"""ND-LET-PP04 — chapa de espera CE-1 (pilar), pino de travamento PT-1 (cartola), trava de pé PT-2 e tabela geral de
fixadores do sistema (rev06c): vistas cotadas, isométricos com balões, soldas, furação, roscas e listas. Cotas em mm."""
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
import json
import fechamento as FCH
import geo_fixacao as GF
import iso_nd as I
from prancha_nd import Prancha

f = lambda v, d=2: f"{v:.{d}f}".replace(".", ",")
PP01 = json.load(open("/home/claude/letsara/pranchas/pp01.json"))
NN = PP01["n"]
FXJ = GF.FX
HT = 0.45

pr = Prancha("A0", dict(cliente=FCH.CLIENTE, obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="FIXAÇÃO DAS PLACAS (SISTEMA TREJOR) — CHAPA DE ESPERA CE-1, PINO PT-1, TRAVA PT-2 E FIXADORES DO SISTEMA",
                        desenho="ND-LET-PP04", folha="01/01", fase="PARA APROVAÇÃO", rev="06"))
pr.revisao("06", "18/10/2026", "EMISSÃO: FABRICAÇÃO DA CE-1, PT-1 E PT-2; TABELA DE FIXADORES E TORQUES")
Q = pr.quadro
XC = Q[2] - 250
pr.cabecalho_peca("FX", f"CE-1 ({NN['CE1']} PÇ) · PT-1 ({NN['PT1']} PÇ) · PT-2 ({NN['PT2']} PÇ) · FIXADORES DO SISTEMA",
                  f"CE-1 embutida no pilar (fábrica dos pilares): {NN['CC1']} CC-1 + {NN['CC1E']} CC-1E + {NN['CC1D']} CC-1D concretados na face C com os CS-1 já soldados; {NN['CE1_obra']} CE-1 rentes nas faces laterais (CS-1 soldado na obra) · cotas em mm",
                  largura=XC - Q[0] - 10)

# ================================================================== CE-1 — vista frontal 1:3
v1 = pr.vista("CE-1", (Q[0] + 90, Q[1] + 440), 3.0, titulo="CE-1 — VISTA FRONTAL", subtitulo="face do pilar; CC-1 = CE-1 + 2 CS-1 (CC-1E/D: 1) soldados na fábrica (face C); laterais: CS-1 na obra", unidade="mm")
v1.chapa(-190, -165, 380, 330, 1.2)
for x in (-120, 120):
    for z in (-140, 140):
        v1.circulo((x, z), 16, "METALICA"); v1.circulo((x, z), 8, "OCULTA")
ZT = FCH.Z_NC + FCH.NC_H / 2 - GF.N["t_teto"] - GF.T["G"] - FCH.Z_CE          # topo da mesa do CS-1 em relação ao centro da CE-1
XC1 = FCH.JUNTA / 2 + FCH.X_CS                                                 # eixo do CS-1 a partir do eixo do pilar (10 + 70 = 80)
for xc in (-XC1, XC1):
    v1.ret(xc - 60, ZT + GF.C["costas"]["z0"], 120, GF.C["costas"]["z1"] - GF.C["costas"]["z0"], "METALICA")
v1.eixo((0, -165), (0, 165), ext=20)
for xr, zr in ((0, -120), (0, 120), (-165, 0), (165, 0)):                         # rev06e: respiro do CC-1 (chapa horizontal na fôrma)
    v1.circulo((xr, zr), 10, "METALICA")
v1.chamada((0, -120), (60, -45), "CC-1: 4 FUROS Ø20 DE RESPIRO (CE-1 DE OBRA SEM FUROS)")
v1.cota_h([-190, -120, -XC1, 0, XC1, 120, 190], -165, -8, total=True)
v1.cota_v([-165, -140, 0, 140, 165], 190, 10, total=True)
v1.chamada((XC1, 60), (60, 18), f"CS-1 (eixo a {XC1:g} do eixo do pilar)")
v1.chamada((120, 140), (20, 14), "pino com cabeça (21)")
# corte com pinos e N18 (armadura do pilar)
v2 = pr.vista("CE-1 CORTE", (Q[0] + 300, Q[1] + 440), 3.0, titulo="CE-1 — CORTE", subtitulo="pinos por solda de arco (stud welding) na oficina", unidade="mm")
TC = GF.TCE
v2.chapa(0, -165, TC, 330, 1.0)
for z in (-140, 140):
    v2.ret(TC, z - 8, 140, 16, "METALICA"); v2.ret(TC + 140, z - 16, 10, 32, "METALICA")
v2.poli([(30, 300), (30, -150), (90, -150), (90, 300)], "ARMADURA")
v2.cota_h([0, TC + 140, TC + 150], -165, -8, total=False)
v2.cota_h([0, TC], -165, -16, total=False)                                        # rev08: espessura da CE-1 em linha própria
v2.cota_v([-165, -140, 140, 165], TC + 150, 10, total=False)
v2.cota_v([-150, 300], 90, 22, total=False)
v2.chamada((60, -150), (46, -10), "N18 — 2 U Ø10 C=96 (armadura do pilar)")
I.solda(v2, (TC, 140 + 8), (16, 16), tipo="ponto", lado="seta", cauda="stud ISO 13918 SD Ø16")
v2.texto((-4, 0), "FACE DO PILAR", "nota", "MIDDLE_CENTER", rot=90)
# rev06e (DEC-031): CC-1 — conjunto de fábrica concretado na face C do pilar (corte pelo eixo de um console)
vc = pr.vista("CC-1 CORTE", (Q[0] + 520, Q[1] + 314), 4.0, titulo="CC-1 — CORTE", subtitulo="CE-1 + CS-1 soldados na fábrica do pilar; face C para cima na fôrma", unidade="mm")
Cc = GF.C
vc.chapa(0, -165, TC, 330, 1.0)                                                    # CE-1 (x > 0 = dentro do pilar)
for z in (-140, 140):
    vc.ret(TC, z - 8, 140, 16, "METALICA"); vc.ret(TC + 140, z - 16, 10, 32, "METALICA")
co_, me_, de_, po_ = Cc["costas"], Cc["mesa"], Cc["dente"], Cc["ponta"]
zb = ZT                                                                            # topo da mesa (em relação ao centro da CE-1)
vc.chapa(-co_["t"], zb + co_["z0"], co_["t"], co_["z1"] - co_["z0"], 1.0)          # costas
vc.poli([(-y, zb + z) for y, z in GF.alma_poli()], "METALICA", fechada=True)       # alma (vista)
vc.chapa(-me_["y1"], zb - me_["t"], me_["y1"] - me_["y0"], me_["t"], 1.0)          # mesa
vc.ret(-(de_["y0"] + de_["t"]), zb, de_["t"], de_["h"], "METALICA")               # dente
vc.chapa(-(po_["y0"] + po_["t"]), zb + po_["z0"], po_["t"], po_["z1"] - po_["z0"], 1.0)   # chapa de ponta
vc.cota_v([zb + co_["z0"], zb, zb + co_["z1"]], -co_["t"] - 70, -10, total=False)
vc.cota_h([-me_["y1"], 0], zb + co_["z0"] - 10, -8, total=False)                # rev08: espessura das costas na PP03
I.solda(vc, (-co_["t"], zb + co_["z0"] + 20), (-30, -10), a=FXJ["solda"]["filete_mm"], tipo="filete", lado="seta", comp=round(co_["z1"] - co_["z0"]),
        cauda="FÁBRICA: costas × CE-1, 2 lados verticais")
vc.texto((TC + 4, -150), "DENTRO DO PILAR", "nota", "TOP_LEFT")
# isométrico com balões
cam = I.Camera((1.0, -1.2, 0.7))
v3 = pr.vista("CE-1 ISO", (Q[0] + 640, Q[1] + 470), 5.0, titulo="CE-1 — ISOMÉTRICO", subtitulo="explodido", unidade="mm")
S3 = GF.ce1_solidos(60)
pj = I.desenhar_iso(v3, S3, cam)
I.balao(v3, pj(S3[0].centro), (-14, 12), 20)
I.balao(v3, pj(S3[1].centro), (12, 12), 21)

# ================================================================== PT-1 — cartola (1:1,5)
hat = [(0, -110), (6.3, -110), (6.3, -40), (36.3, -40), (36.3, 40), (6.3, 40), (6.3, 110), (0, 110), (0, 33.7), (30, 33.7), (30, -33.7), (0, -33.7)]
p1 = pr.vista("PT-1", (Q[0] + 80, Q[1] + 175), 1.5, titulo="PT-1 — CARTOLA (VISTA LATERAL)", subtitulo="ch. 6,3 A36 dobrada; raio interno 6", unidade="mm")
p1.poli(hat, "METALICA", fechada=True); p1.hachura(hat, "ANSI31", HT, "METALICA")
p1.cota_v([-110, -70, -40, 0, 40, 70, 110], 36.3, 10, total=True)
p1.cota_h([0, 6.3, 36.3], -110, -8, total=False)
p1.texto((-6, -70), "Ø18", "nota", "MIDDLE_RIGHT"); p1.texto((-6, 70), "oblongo 18 × 40", "nota", "MIDDLE_RIGHT")
p2 = pr.vista("PT-1 DESENV", (Q[0] + 185, Q[1] + 175), 1.5, titulo="PT-1 — DESENVOLVIMENTO", subtitulo="corte a laser, dobrar nas linhas", unidade="mm")
p2.chapa(0, -140, 80, 280, HT)
for zz in (-140 + 70, -140 + 100, 140 - 100, 140 - 70):
    p2.linha((0, zz), (80, zz), "EIXO")
p2.circulo((40, -100), 9, "METALICA")
p2.poli([(31, 80), (31, 120), (49, 120), (49, 80)], "METALICA", fechada=True)
p2.cota_v([-140, -100, -70, -40, 40, 70, 100, 140], 80, 10, total=True)
p2.cota_h([0, 40, 80], -140, -8, total=False)
# montagem PT-1 na junta (1:3)
p3 = pr.vista("PT-1 MONT", (Q[0] + 395, Q[1] + 175), 2.5, titulo="PT-1 — GUIA NA JUNTA HORIZONTAL", subtitulo="2 por junta; M16 só na placa de baixo (guia, sem esforço — DEC-035)", unidade="mm")
for z0_, z1_ in ((-150, -2.5), (2.5, 150)):
    pts = [(-100, z0_), (0, z0_), (0, z1_), (-100, z1_)]
    p3.poli(pts, "CORTADO", fechada=True); p3.hachura(pts, "AR-CONC", 0.03)
for zl in (-70, 70):
    p3.chapa(-70, zl - 8, 70, 16, 0.3)
p3.poli(hat, "METALICA", fechada=True); p3.hachura(hat, "ANSI31", 0.3, "METALICA")
I.parafuso_lateral(p3, 40, -70, 40, 16, cabeca=(10, 24), sentido=-1)              # rev08 (DEC-035): M16 só na placa de baixo
p3.chamada((36, 70), (12, 30), "sem parafuso na placa de cima")
p3.cota_v([-70, 70], 50, 14, total=False)
p3.chamada((-35, 70), (-40, 22), "luva TSA M16 hef 70 (33)")
p3.chamada((40, -70), (16, -18), "M16 × 40 (31) + arruela larga (32)")
p3.chamada((-50, 0), (-30, -44), "junta 5 (macho-fêmea)")

# ================================================================== PT-2 — cantoneira (1:1,5)
ang = [(0, 0), (102, 0), (102, 9.5), (9.5, 9.5), (9.5, 102), (0, 102)]
q1 = pr.vista("PT-2", (Q[0] + 590, Q[1] + 185), 1.5, titulo="PT-2 — CANTONEIRA (SEÇÃO)", subtitulo="L 102 × 102 × 9,5 A36, L = 150", unidade="mm")
q1.poli(ang, "METALICA", fechada=True); q1.hachura(ang, "ANSI31", HT, "METALICA")
q1.cota_h([0, 9.5, 52, 102], 0, -12, total=False)
q1.cota_v([0, 9.5, 52, 102], 0, -10, total=False)
q1.chamada((52, 5), (34, -24), "aba na placa: oblongo 18 × 40 horizontal")
q1.chamada((5, 52), (14, 18), "aba no pilar: oblongo 18 × 40 vertical")
q2 = pr.vista("PT-2 ABAS", (Q[0] + 720, Q[1] + 205), 1.5, titulo="PT-2 — FURAÇÃO DAS ABAS", subtitulo="as 2 abas rebatidas", unidade="mm")
q2.chapa(0, 0, 150, 102, HT)
q2.poli([(55, 43), (95, 43), (95, 61), (55, 61)], "METALICA", fechada=True)
q2.chapa(0, 120, 150, 102, HT)
q2.poli([(66, 151), (84, 151), (84, 191), (66, 191)], "METALICA", fechada=True)
q2.cota_h([0, 55, 95, 150], 0, -8, total=False)
q2.cota_v([0, 43, 61, 102], 150, 10, total=False)
q2.cota_v([120, 151, 191, 222], 150, 10, total=False)
q2.texto((75, 108), "aba na placa (oblongo horizontal)", "nota", "BOTTOM_CENTER")
q2.texto((75, 228), "aba no pilar (oblongo vertical)", "nota", "BOTTOM_CENTER")

# ================================================================== tabelas
it_ce = GF.ce1_itens()
it_pt = GF.pt_itens()
rows = []
kg_ce = sum(kg * q for *_, q, kg in it_ce)
for n, nome, dim, mat, q, kg in it_ce + it_pt:
    rows.append([n, nome, dim, mat, q, f(kg, 3), f(kg * q, 3)])
y = pr.tabela(XC, Q[3] - 6, "LISTA DE MATERIAIS — CE-1 (1 CJ), PT-1 (1 CJ), PT-2 (1 CJ)", ["Nº", "DESCRIÇÃO", "DIMENSÃO (mm)", "MATERIAL", "QTD", "kg/un", "kg"],
              rows, [9, 48, 72, 38, 10, 22, 31], h_lin=5.4)
pr.texto(XC, y - 3.5, f"CE-1: {f(kg_ce, 2)} kg/cj × {NN['CE1']} = {f(kg_ce * NN['CE1'], 0)} kg. PT-1 com itens 30–33; PT-2 com itens 40, 31, 32 e 43.", "nota", "TEXTO")
fix = [["16", "M16 × 45 ISO 4017", "8.8 galv. fogo", "rosca total", "nível do CS-1", "contraporca 120", NN["CS1"]],
       ["15", "porca M16 ISO 4032", "8, sobremedida", "6H + 0,4", "soldada (CS-1)", "—", 2 * NN["CS1"]],
       ["17", "contraporca M16 ISO 4035", "05 galv.", "6H + 0,4", "trava do nível", "120", NN["CS1"]],
       ["18", "prisioneiro M16 × 45 ISO 4026", "45H zincado", "sext. int. 8", "frontal do CS-1", "trava química", NN["CS1"]],
       ["31", "M16 × 40 ISO 4017", "8.8 galv. fogo", "b = 38", "PT-1 e PT-2", "80 (oblongo livre)", 2 * NN["PT1"] + 2 * NN["PT2"]],
       ["32", "arruela larga M16 ISO 7093", "200 HV galv.", "17 × 50 × 3", "PT-1 e PT-2", "—", 2 * NN["PT1"] + 2 * NN["PT2"]],
       ["33", "luva TSA M16 (Trejor)", "zincada", "hef 70", "placas (PT-1)", "—", 2 * NN["PT1"]],
       ["43", "bucha BR-1 / BR-2 M16", "zincada", "hef 70 / 100", "placa / pilar (PT-2)", "—", 2 * NN["PT2"]]]
y = pr.tabela(XC, y - 8, "FIXADORES DO SISTEMA — OBRA (torque em N·m)", ["Nº", "PEÇA", "CLASSE", "ROSCA", "USO", "APERTO", "QTD"], fix, [9, 54, 30, 26, 38, 30, 23], h_lin=5.4)
pr.notas(XC, y - 4, [
    "Medidas em mm. Tolerâncias gerais NBR ISO 2768-1 classe m; furos Ø18 ± 0,3; oblongos 18 × 40 ± 0,5.",
    "CE-1: chapa A36 cortada a laser; pinos com cabeça Ø16 × 150 soldados por arco (stud welding, AWS D1.1 cap. 7) — ensaio de dobramento a 15° em 1 pino a cada 100; galvanização a fogo após a solda. Na fôrma do pilar: rente à face, centrada, posição ±5 (gabarito), N18 por baixo do pino de baixo de cada coluna.",
    "PT-1: chapa 6,3 A36 dobrada a frio (raio interno 6), galvanizada a fogo. Furo Ø18 na placa de baixo e oblongo vertical 18 × 40 na de cima: não travar o deslocamento vertical (aperto 80 N·m com arruela larga).",
    "PT-2: cantoneira A36 galvanizada; oblongo vertical na aba do pilar e horizontal na aba da placa (tolerâncias de montagem).",
    "Roscas métricas grossas ISO 261/965 (6g/6H); peças galvanizadas a fogo com porca sobremedida (6H + 0,4) ou rosca repassada; não lubrificar o prisioneiro antes da trava química.",
    f"DEC-044: na fiada +6,25 dos pilares P8A (PC-01) e P11 (PC-02) a CE-1 é a CE-1L 840 × 330 × {GF.TCE:g} (asas de 220 além das faces, mesmos pinos e N18) — {NN['CE1L']} pç; nos pilares com CS-1C / CS-1D a CE-1 é a comum, com 1 console e a caixa de calço soldada na obra no fundo da caixa (filete 6, 2 × 330) — ND-LET-PP06.".replace(".", ",").replace("ND-LET-PP06,", "ND-LET-PP06."),
    "EMISSÃO EXECUTIVA — LIBERADO PARA PRODUÇÃO E MONTAGEM."], 250)
FCH.chave_todas(pr)                                     # rev11 (checklist 6): planta-chave com as paredes nas cores A–J
av = pr.salvar("/home/claude/letsara/pranchas/ND-LET-PP04")
print("PP04", len([a for a in av if a[0] == "ERRO"]), "erros,", len(av), "avisos", av)
