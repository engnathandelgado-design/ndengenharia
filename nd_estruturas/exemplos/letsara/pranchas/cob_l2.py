"""ND-LET-COB05 — cobertura metálica da linha 2.
rev00 (DEC-048): W 310 × 32,7 contínua de A a E no lugar das TS-01, só nos pilares, por montantes.
rev02 (DEC-050): sem montantes nos pilares — a cabeça de concreto sobe até o fundo da W.
rev03 (DEC-052, Nathan 24/10: "viga usando praticamente 100 % do aço"): W 200 × 15,0 contínua, apoiada nos 6 pilares e em 4
montantes curtos W 150 × 13,0 no meio dos vãos A–B, B–C, C–D e D–P6, nascendo da espera EM-L2 na faixa de 2º estágio da VM do
+7,30 (montagem depois da capa curada). Tudo parafusado, sem solda: mesa inferior da W presa por parafusos no gabarito 55;
cantoneiras L 102 × 102 × 12,7 em cima e embaixo dos montantes. Dados de cob_linha2.json (calc_cobertura_linha2.py).
Cotas em mm. A1."""
import json, math, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas")
from prancha_nd import Prancha
from geometria import X_EIXO
from nd_estruturas import metalica_laminada as ML

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
CB = json.load(open(AQ + "cob_linha2.json"))
LG = json.load(open(AQ + "ligacoes.json"))
f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
M = lambda v: v * 1000
I3 = 0.03
WP, WMP = ML.perfil(CB["perfil"]), ML.perfil(CB["montante"])
D_W, BF_W, TF_W, TW_W = WP.d, WP.bf, WP.tf, WP.tw
D_M, BF_M, TF_M, TW_M = WMP.d, WMP.bf, WMP.tf, WMP.tw
NW, NM = CB["perfil"].replace("x", "×"), CB["montante"].replace("x", "×")
zt = lambda x: M(LG["Z0_TS"]) + I3 * x + 900 / math.cos(math.atan(I3))   # topo da W (= topo da TS-01 nas outras linhas), x em mm
LARG = M(X_EIXO["E"])
CORTES = [25] + [M(x) for x in CB["emendas_x"]] + [LARG - 25]
MARCA_P = {"A": "PL-02", "B": "PM-01", "C": "PC-01", "D": "PM-02", "P6": "PE-03", "E": "PL-06"}
X_TER = LG["x_tercas_esq"] + [x + (2 * X_EIXO["C"] - LG["X_PONTA_CEN"]) - LG["X_PONTA_ESQ"] for x in LG["x_tercas_esq"]]
NT = len(X_TER)
MTS = CB["montantes"]
MF = CB["mao_francesa"]
L_ANG, T_ANG = 102, 12.7                                    # L 102 × 102 × 12,7
Y_M = 30                                                    # eixo do montante 30 mm para o lado da borda (faixa de 2º estágio)

pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo=f"COBERTURA METÁLICA DA LINHA 2 — {NW} NOS PILARES E EM MONTANTES SOBRE AS VM DO +7,30: ELEVAÇÃO, APOIOS, ESPERA, EMENDAS, ST-W E LISTA",
                        desenho="ND-LET-COB05", folha="01/01", fase="PARA APROVAÇÃO", rev="03"))
pr.revisao("00", "23/10/2026", "EMISSÃO INICIAL (DEC-048): LINHA 2 METÁLICA, SEM TS-01")
pr.revisao("02", "24/10/2026", "DEC-050: SEM MONTANTES — CABEÇA DOS PILARES ATÉ O FUNDO DA W, APOIO DIRETO COM CHAPA E PRESILHAS")
pr.revisao("03", "24/10/2026", f"DEC-052: {NW} COM MONTANTES NO MEIO DOS VÃOS SOBRE AS VM DO +7,30 (ESPERA EM-L2); MESA PRESA POR PARAFUSOS (SEM PRESILHAS)")
Q = pr.quadro
XC = Q[2] - 190
vf = CB["verificacoes"]
pr.cabecalho_peca("W-L2", f"VIGA DE COBERTURA DA LINHA 2 — {NW} ({CB['aco']}) CONTÍNUA DE A a E, {len(CORTES) - 1} MÓDULOS",
                  f"apoios: 6 pilares (cabeça até a W) + 4 montantes {NM} sobre as VM do +7,30; mão-francesa MF-1 em toda terça; uso {f(vf['uso_M'], 2)}",
                  largura=XC - Q[0] - 10)

# ------------------------------------------------------------------ ELEVAÇÃO 1:75 (olhando para a linha 9)
v = pr.vista("ELEVAÇÃO", (Q[0] + 55, Q[3] - 222 - 7000 / 75), 75, titulo=f"ELEVAÇÃO DA LINHA 2 — {NW} NOS PILARES E NOS MONTANTES (OLHANDO PARA A LINHA 9)",
             subtitulo="topo da W na inclinação da cobertura (3 %); VM do +7,30 da linha 2 embaixo; módulos e emendas; terças a cada 1,26 m", unidade="mm")
zb = lambda x: zt(x) - D_W
v.poli([(CORTES[0], zb(CORTES[0])), (CORTES[-1], zb(CORTES[-1])), (CORTES[-1], zt(CORTES[-1])), (CORTES[0], zt(CORTES[0]))], "METALICA", fechada=True)
for xe in CORTES[1:-1]:
    v.linha((xe, zb(xe)), (xe, zt(xe)), "METALICA")
ZP = 6600
for a in CB["apoios_diretos"]:
    x = M(a["x"]); z0 = M(a["z_concreto"])
    v.ret(x - 125, z0 + 20, 250, 19, "METALICA")
    bx = 400 if a["nome"] in ("B", "C", "D") else (250 if a["nome"] == "P6" else 300)
    v.ret(x - bx / 2, ZP, bx, z0 - ZP, "VISTA"); v.interrupcao((x - bx / 2, ZP), (x + bx / 2, ZP))
    v.texto((x, ZP - 250), MARCA_P[a["nome"]], "min", "TOP_CENTER")
    v.texto((x, ZP - 650), f"+{f(a['z_concreto'], 3)}", "min", "TOP_CENTER")
EIXO_X = {"A": 0.0, "B": X_EIXO["B"], "C": X_EIXO["C"], "D": X_EIXO["D"], "P6": 36.175}
MEIA = {"A": 300, "B": 200, "C": 200, "D": 200, "P6": 125}
for (a_, b_) in (("A", "B"), ("B", "C"), ("C", "D"), ("D", "P6")):
    xa, xb_ = M(EIXO_X[a_]) + MEIA[a_] + 30, M(EIXO_X[b_]) - MEIA[b_] - 30
    v.ret(xa, 7040 - 750, xb_ - xa, 750, "VISTA"); v.linha((xa, 7300), (xb_, 7300), "VISTA")
for m in MTS:
    x = M(m["x"])
    v.ret(x - D_M / 2, 7325, D_M, M(m["L_m"]), "METALICA")
    v.ret(x - 176, 7300, 352, 20, "VISTA")
for xt_ in X_TER:
    xw = M(xt_)
    v.ret(xw - 45, zt(xw), 90, 302, "OCULTA")
v.cota_h(sorted([M(a["x"]) for a in CB["apoios_diretos"]] + [M(m["x"]) for m in MTS]), 5300, -6, total=True)
v.cota_h(CORTES, zt(LARG) + 600, 10, total=False)
v.chamada((CORTES[1], zt(CORTES[1])), (6, 12), "emenda TL-1 / TL-2 (det. 4)")
v.chamada((M(MTS[1]["x"]), 7325 + M(MTS[1]["L_m"]) / 2), (8, 16), f"montante {NM} (det. 2 e 3)")
v.chamada((M(MTS[2]["x"]) + 700, 7040 - 300), (-10, -14), "VM do +7,30 (espera EM-L2 no 2º estágio)")

# ------------------------------------------------------------------ DETALHE 1 — apoio da W na cabeça do pilar (1:10), corte ⊥ à W
d1 = pr.vista("DETALHE 1", (Q[0] + 600, Q[1] + 150), 10, titulo="DETALHE 1 — APOIO NA CABEÇA DO PILAR", subtitulo="corte ⊥ à W", unidade="mm")
pil = [(-200, -400), (200, -400), (200, 0), (-200, 0)]
d1.poli(pil, "CORTADO", fechada=True); d1.hachura(pil, "AR-CONC", 0.03); d1.interrupcao((-200, -400), (200, -400))
d1.ret(-140, 0, 280, 20, "VISTA"); d1.ret(-125, 20, 250, 19, "METALICA")
z_w = 39
d1.ret(-BF_W / 2, z_w, BF_W, TF_W, "METALICA"); d1.ret(-TW_W / 2, z_w + TF_W, TW_W, 160, "METALICA")
d1.interrupcao((-TW_W / 2 - 20, z_w + TF_W + 160), (TW_W / 2 + 20, z_w + TF_W + 160))
for yy in (-27.5, 27.5):
    d1.linha((yy, -350), (yy, z_w + TF_W + 40), "METALICA")
    d1.ret(yy - 12, z_w + TF_W, 24, 13, "METALICA"); d1.ret(yy - 12, z_w + TF_W + 13, 24, 13, "METALICA")
d1.poli([(-27.5, -350), (-27.5, -390), (27.5, -390), (27.5, -350)], "ARMADURA")
d1.cota_h([-125, -27.5, 27.5, 125], -400, -14, total=False); d1.cota_v([-350, 0], 230, 8, total=False)
d1.chamada((-27.5, -200), (-24, -8), "4 BR-M16 8.8 L 450")
d1.chamada((-27.5, -390), (-24, 6), "grampo U Ø10")
d1.chamada((130, 10), (14, 8), "graute 20 (±10)")
d1.chamada((-110, 30), (-6, 20), "CA-L2 250 × 250 × 19")
d1.chamada((27.5, z_w + TF_W + 20), (14, 18), "porca + contraporca")
d1.chamada((0, z_w + 120), (-20, 14), f"{NW} (bf {BF_W:.0f}, tf {f(TF_W)})")

# ------------------------------------------------------------------ DETALHE 2 — montante no meio do vão: corte ⊥ à W (1:10)
mt0 = MTS[0]
LM = M(mt0["L_m"])
QUEBRA = LM > 500
S_ = (LM - 420) if QUEBRA else 0                            # trecho do meio do montante interrompido no desenho
zf = 25 + LM + 5 - S_                                       # fundo da W no desenho
d2 = pr.vista("DETALHE 2", (Q[0] + 110, Q[1] + 120), 10, titulo="DETALHE 2 — MONTANTE SOBRE A VM DO +7,30", subtitulo=f"corte ⊥ à W; espera EM-L2 no 2º estágio; {NM} (L na tabela)", unidade="mm")
vm = [(-150, -450), (150, -450), (150, -260), (-150, -260)]
d2.poli(vm, "CORTADO", fechada=True); d2.hachura(vm, "AR-CONC", 0.03); d2.interrupcao((-150, -450), (150, -450))
laje = [(-560, -250), (-50, -250), (-50, -50), (-560, -50)]
d2.poli(laje, "CORTADO", fechada=True); d2.interrupcao((-560, -250), (-560, -50))
d2.ret(-150, -260, 100, 10, "VISTA")                                            # fita de neoprene
e2 = [(-30, -260), (150, -260), (150, 0), (-560, 0), (-560, -50), (-30, -50)]
d2.poli(e2, "CORTADO", fechada=True); d2.hachura(e2, "AR-CONC", 0.015)
d2.poli([(-10, -260), (-10, -60), (120, -60), (120, -260)], "ARMADURA")         # alça N9
for yy in (0, 60):
    d2.poli([(yy, 60), (yy, -75), (yy + 12, -87), (yy + 24, -75), (yy + 24, -55)], "METALICA")   # barra com gancho por baixo da alça
d2.ret(-40, 0, 140, 20, "VISTA")                                                # graute
d2.ret(-20, 20, 100, L_ANG, "VISTA")                                            # cantoneiras de baixo (vistas)
h_bx = 200 if QUEBRA else LM
d2.ret(-20, 25, BF_M, h_bx, "METALICA")                                         # montante (mesa vista)
d2.ret(Y_M - TW_M / 2, 25, TW_M, h_bx, "CORTADO")
if QUEBRA:
    d2.interrupcao((-30, 225), (90, 225))
    d2.ret(-20, zf - 5 - 200, BF_M, 200, "METALICA"); d2.ret(Y_M - TW_M / 2, zf - 5 - 200, TW_M, 200, "CORTADO")
    d2.interrupcao((-30, zf - 205), (90, zf - 205))
d2.ret(-50, zf - L_ANG, 130, L_ANG, "VISTA")                                    # cantoneiras de cima (vistas)
d2.ret(-BF_W / 2, zf, BF_W, TF_W, "METALICA"); d2.ret(-TW_W / 2, zf + TF_W, TW_W, D_W - 2 * TF_W, "METALICA"); d2.ret(-BF_W / 2, zf + D_W - TF_W, BF_W, TF_W, "METALICA")
for yy in (-27.5, 27.5):
    d2.linha((yy, zf - T_ANG - 25), (yy, zf + TF_W + 25), "METALICA")
for yy in (0, 60):
    d2.ret(yy - 12, 32.7, 24, 26, "METALICA")
d2.linha((0, -500), (0, zf + D_W + 80), "EIXO"); d2.texto((0, zf + D_W + 100), "eixo da linha 2", "min", "BOTTOM_CENTER")
d2.cota_h([-150, -50, 0, Y_M, 60, 150], -450, -14, total=False)
d2.cota_v([-260, 0, zf], 260, 10, total=False)
d2.chamada((60, -40), (26, -6), "EM-L2: 4 BR-M16 8.8 L 330 com gancho laçado na alça N9")
d2.chamada((120, -150), (20, -16), "alça N9 Ø10 da VM (existente)")
d2.chamada((-300, -25), (-6, 22), "capa + 2º estágio C30 (de obra)")
d2.chamada((-300, -150), (-4, -16), "laje alveolar (apoio 10 na VM)")
d2.chamada((-40, 10), (-10, 6), "graute 20")
d2.chamada((-20, 30), (-30, -1), "CB-M1 2 L 102 × 102 × 12,7 × 100")
d2.chamada((-50, zf - 50), (-14, 6), "CB-M2 2 L 102 × 102 × 12,7 × 130")
d2.chamada((-27.5, zf + 2), (-18, 14), "4 M16 na mesa da W (gab. 55)")
d2.chamada((Y_M, 120), (30, -4), f"{NM}")
d2.texto((-300, -700), "VM 30 × 75 (+7,30, linha 2)", "min", "TOP_CENTER")

# ------------------------------------------------------------------ DETALHE 3 — montante: vista ao longo da W (1:10)
d3 = pr.vista("DETALHE 3", (Q[0] + 380, Q[1] + 120), 10, titulo="DETALHE 3 — MONTANTE AO LONGO DA W", subtitulo="cantoneiras nas mesas do montante; barras a ±150 nas alças", unidade="mm")
d3.ret(-450, -450, 900, 190, "VISTA"); d3.interrupcao((-450, -450), (450, -450))
c2 = [(-450, -260), (450, -260), (450, 0), (-450, 0)]
d3.poli(c2, "VISTA", fechada=True); d3.hachura(c2, "AR-CONC", 0.015)
for xx in (-300, -150, 0, 150, 300):
    d3.linha((xx, -260), (xx, -60), "ARMADURA")
for xx in (-150, 150):
    d3.linha((xx + 8, 60), (xx + 8, -80), "METALICA")
d3.ret(-200, 0, 400, 20, "VISTA")
for sg in (-1, 1):
    x0 = sg * D_M / 2
    d3.poli([(x0, 20), (x0 + sg * L_ANG, 20), (x0 + sg * L_ANG, 20 + T_ANG), (x0 + sg * T_ANG, 20 + T_ANG), (x0 + sg * T_ANG, 20 + L_ANG), (x0, 20 + L_ANG)], "METALICA", fechada=True)
    d3.poli([(x0, zf), (x0 + sg * L_ANG, zf), (x0 + sg * L_ANG, zf - T_ANG), (x0 + sg * T_ANG, zf - T_ANG), (x0 + sg * T_ANG, zf - L_ANG), (x0, zf - L_ANG)], "METALICA", fechada=True)
    d3.linha((x0 - sg * 10, 80), (x0 + sg * (T_ANG + 25), 80), "METALICA")
    d3.linha((x0 - sg * 10, zf - 55), (x0 + sg * (T_ANG + 25), zf - 55), "METALICA")
    d3.linha((sg * (D_M / 2 + 55), zf - T_ANG - 25), (sg * (D_M / 2 + 55), zf + TF_W + 25), "METALICA")
d3.ret(-D_M / 2, 25, D_M, h_bx, "METALICA")
if QUEBRA:
    d3.interrupcao((-D_M / 2 - 10, 225), (D_M / 2 + 10, 225))
    d3.ret(-D_M / 2, zf - 5 - 200, D_M, 200, "METALICA"); d3.interrupcao((-D_M / 2 - 10, zf - 205), (D_M / 2 + 10, zf - 205))
d3.ret(-450, zf, 900, TF_W, "METALICA"); d3.ret(-450, zf + D_W - TF_W, 900, TF_W, "METALICA"); d3.linha((-450, zf + TF_W), (450, zf + TF_W), "OCULTA")
d3.cota_h([-150 - 8, -D_M / 2, D_M / 2, 150 + 8], -450, -14, total=False)
d3.cota_h([-(D_M / 2 + 55), D_M / 2 + 55], zf + D_W, 10, total=False)
d3.chamada((158, 40), (16, 10), "BR-M16 + arruela + porca + contraporca")
d3.chamada((-300, -150), (-22, -14), "alças N9 c/15 (eixo do montante sobre uma alça)")
d3.chamada((D_M / 2 + T_ANG, 80), (18, 26), "2 M16 na mesa do montante (por cantoneira)")
d3.chamada((D_M / 2 + 55, zf - 10), (20, -4), "furo oblongo ao longo da W")
d3.texto((0, -620), "faixa de 2º estágio da VM", "min", "TOP_CENTER")

# ------------------------------------------------------------------ DETALHE 4 — emenda (1:10)
d4 = pr.vista("DETALHE 4", (Q[0] + 560, Q[1] + 290), 10, titulo=f"DETALHE 4 — EMENDA DA {NW}", subtitulo="TL-1 nas mesas + TL-2 na alma; M16 8.8", unidade="mm")
d4.ret(-400, 0, 800, D_W, "METALICA"); d4.linha((0, 0), (0, D_W), "METALICA")
d4.ret(-150, D_W, 300, 9.5, "METALICA"); d4.ret(-150, -9.5, 300, 9.5, "METALICA"); d4.ret(-100, (D_W - 130) / 2, 200, 130, "OCULTA")
for xx in (-110, -50, 50, 110):
    d4.circulo((xx, D_W + 5), 9, "METALICA"); d4.circulo((xx, -5), 9, "METALICA")
for xx in (-50, 50):
    for zz in (D_W / 2 - 35, D_W / 2 + 35):
        d4.circulo((xx, zz), 9, "METALICA")
d4.cota_h([-150, 0, 150], D_W + 9.5, 10, total=False); d4.cota_v([0, D_W], 420, 8, total=False)
d4.chamada((110, D_W + 9), (10, 12), "TL-1 9,5 × 100 × 300 (2 por emenda), 8 M16 cada")
d4.chamada((50, D_W / 2 + 35), (30, 6), "TL-2 6,3 × 130 × 200 (2), 4 M16")

# ------------------------------------------------------------------ DETALHE 5 — terça na W: ST-W e mão-francesa (seção, 1:10)
d5 = pr.vista("DETALHE 5", (Q[0] + 800, Q[1] + 150), 10, titulo="DETALHE 5 — TERÇA NA W", subtitulo="ST-W e MF-1", unidade="mm")
d5.ret(-BF_W / 2, D_W - TF_W, BF_W, TF_W, "METALICA"); d5.ret(-BF_W / 2, 0, BF_W, TF_W, "METALICA"); d5.ret(-TW_W / 2, TF_W, TW_W, D_W - 2 * TF_W, "METALICA")
d5.poli([(-90, D_W + 6.3), (90, D_W + 6.3), (90, D_W + 6.3 + 150)], "METALICA")
d5.ret(-45, D_W + 6.3, 90, 302, "OCULTA")
for sy in (-1, 1):
    d5.linha((sy * 300, D_W + 60), (sy * (BF_W / 2 + 10), TF_W), "METALICA")
d5.cota_v([0, D_W, D_W + 6.3 + 302], 360, 8, total=False); d5.cota_h([-300, 0, 300], -40, -8, total=False)
d5.chamada((-200, D_W - 20), (-12, 16), "MF-1 L 51 × 51 × 4,8")
d5.chamada((60, D_W + 80), (22, 26), "ST-W 6,3: 2 M12 na mesa + 4 M12 nas almas (ISO 5, COB09)")
d5.chamada((-20, D_W + 250), (-16, 20), "terça Z 302 (COB01)")

# ------------------------------------------------------------------ tabelas e notas
kgm_W, kgm_M = WP.massa, WMP.massa
na, nm, n_e = len(CB["apoios_diretos"]), len(MTS), len(CB["emendas_x"])
KG_L102, KG_M16 = 19.0, 1.58                                   # L 102 × 102 × 12,7 e barra roscada M16 (kg/m)
L_mf = MF["L_m"] if MF else 0.0
lin = [[f"W-L2 {k + 1}", f"{NW} A572-50", "1", f(L_, 2), f(L_ * kgm_W, 0)] for k, L_ in enumerate(CB["modulos_m"])]
lin += [[f"MT-L2 {k + 1}", f"montante {NM} ({m['vao']}, sobre a {m['vm']})", "1", f(m["L_m"], 3), f(m["L_m"] * kgm_M, 1)] for k, m in enumerate(MTS)]
lin += [["CB-M1", "L 102 × 102 × 12,7 × 100 (base do montante), 2 + 2 furos Ø18", str(2 * nm), "0,10", f(2 * nm * 0.10 * KG_L102, 1)],
        ["CB-M2", "L 102 × 102 × 12,7 × 130 (topo do montante), 2 + 2 furos Ø18", str(2 * nm), "0,13", f(2 * nm * 0.13 * KG_L102, 1)],
        ["EM-L2", "barra roscada M16 8.8 L 330 com gancho 180° (espera no 2º estágio)", str(4 * nm), "0,33", f(4 * nm * 0.33 * KG_M16, 1)],
        ["CA-L2", "chapa de apoio 250 × 250 × 19, 4 furos Ø18 (graute 20 por baixo)", str(na), "-", f(na * 9.3, 0)],
        ["BR-M16", "barra roscada M16 8.8 L 450 + grampo (embutida no pilar)", str(4 * na), "0,45", f(4 * na * 0.45 * KG_M16, 1)],
        ["TL-1", "tala de mesa 9,5 × 100 × 300", str(2 * n_e), "0,30", f(2 * n_e * 2.24, 1)],
        ["TL-2", "tala de alma 6,3 × 130 × 200", str(2 * n_e), "0,20", f(2 * n_e * 1.29, 1)],
        ["ST-W", "clip da terça, chapa dobrada 6,3 × 220 (ISO 5, COB09)", str(NT), "-", f(NT * 3.2, 0)]]
if MF:
    lin.append(["MF-1", f"mão-francesa L 51 × 51 × 4,8 L {M(L_mf):.0f}", str(2 * NT), f(L_mf, 2), f(2 * NT * L_mf * 3.63, 0)])
n_m16 = n_e * 20 + nm * 8
lin += [["M16 8.8", "parafuso + porca + 2 arruelas (emendas e montantes); porcas das barras", f"{n_m16} + {2 * (4 * na + 4 * nm)}", "-", "-"],
        ["M12 8.8", "ST-W × mesa (2/terça), MF-1 × mesa inf. (1/MF); almas: COB01", str(NT * 2 + (2 * NT if MF else 0)), "-", "-"]]
TOT = sum(float(l[4].replace(",", ".")) for l in lin if l[4] != "-")
lin.append(["", "TOTAL (sem parafusos)", "", "", f(TOT, 0)])
y = pr.tabela(XC, Q[3] - 6, "LISTA DE MATERIAL — COBERTURA DA LINHA 2", ["MARCA", "DESCRIÇÃO", "QT", "L (m)", "kg"], lin, [18, 100, 12, 18, 22], destaque_ultima=True)
fl = CB["flecha"]
ap, mt = CB["apoios_diretos"], MTS
ver = [[f"Flexão — mesa sup. (Lb {f(vf['Lb_m'], 2)} m)", f(vf["M_mesa_sup"]) + " / " + f(vf["MRd_Lb_terca"]), f(vf["M_mesa_sup"] / vf["MRd_Lb_terca"], 2)],
       ["Flexão — mesa inf. (com MF-1)", f(vf["M_mesa_inf"]) + " / " + f(vf["MRd"]), f(vf["M_mesa_inf"] / vf["MRd"], 2)],
       [f"Sem MF-1 (Lb {f(vf['Lb_trecho_m'], 2)} m)", "MF-1 em toda terça", f(vf["uso_sem_mao_francesa"], 2)],
       ["Cortante", f(vf["Vsd"]) + " / " + f(vf["VRd"]), f(vf["uso_V"], 2)],
       ["Flecha G + Q (L/250, com a VM)", f"{f(fl['GQ_mm'])} / {f(fl['lim_L250_mm'])} mm", f(fl["GQ_mm"] / fl["lim_L250_mm"], 2)],
       ["Pilares: barras / alma / mesa (T-stub)", "-", f"{f(max(m['uso_barra'] for m in ap), 2)} / {f(max(m['uso_alma'] for m in ap), 2)} / {f(max(m['uso_mesa'] for m in ap), 2)}"],
       ["Montante: compressão / tração", f"Nc {f(max(m['Nc_d'] for m in mt))} / Nt {f(max(m['Nt_d'] for m in mt))} kN", f"{f(max(m['uso_compressao'] for m in mt), 2)} / {f(max(m['uso_tracao'] for m in mt), 2)}"],
       ["Montante: parafusos / cantoneiras / mesa", "-", f"{f(max(m['uso_parafusos'] for m in mt), 2)} / {f(max(m['uso_cantoneiras'] for m in mt), 2)} / {f(max(m['uso_mesa_w'] for m in mt), 2)}"],
       ["Espera EM-L2: barra / alça N9 / graute", "-", f"{f(max(m['espera']['uso_barra'] for m in mt), 2)} / {f(max(m['espera']['uso_alca'] for m in mt), 2)} / {f(max(m['espera']['uso_graute'] for m in mt), 2)}"],
       ["Emendas TL-1 / TL-2", "-", f"{f(max(e['uso_TL1'] for e in CB['emendas']), 2)} / {f(max(e['uso_TL2'] for e in CB['emendas']), 2)}"]]
# rev09c: sem tabela de verificações na prancha do cliente (fica na memória MC09)
# y = pr.tabela(XC, y - 4, "VERIFICAÇÕES (NBR 8800:2024)", ["ITEM", "Sd / Rd", "USO"], ver, [80, 60, 30])
tm = [[f"MT-L2 {k + 1}", m["vao"], f(m["x"], 3), f(m["L_m"], 3), f(m["Nc_d"]), f(m["Nt_d"])] for k, m in enumerate(MTS)]
y = pr.tabela(XC, y - 4, "MONTANTES (x do eixo A; N de cálculo, kN)", ["MARCA", "VÃO", "x (m)", "L (m)", "Nc", "Nt"], tm, [30, 24, 30, 30, 30, 26])
notas = [f"{NW} contínua de A a E, apoiada nos 6 pilares (A recuo do P1-L2, B, C topo do P8A, D, P6 da linha 2, E recuo do P2-L2) e nos 4 montantes {NM} do meio dos vãos A–B, B–C, C–D e D–P6 (maior trecho {f(CB['vao_max_m'], 2)} m). Faixa {f(CB['trib_m'], 2)} m; g {f(CB['cargas_kN_m']['g_k'], 2)}, q {f(CB['cargas_kN_m']['q_k'], 2)}, sucção {f(CB['cargas_kN_m']['w_suc_corpo'], 2)} (faixa local {f(CB['cargas_kN_m']['w_suc_local'], 2)}) kN/m. Viga calculada com o apoio do meio rígido e com a mola da VM; vale a envoltória.",
         f"Flambagem lateral: mesa superior travada pelas terças; mesa inferior pelas mãos-francesas MF-1 em TODA terça (sem elas o uso seria {f(vf['uso_sem_mao_francesa'], 2)}).",
         "Pilares (DEC-050/052): cabeça de concreto até 39 mm abaixo do fundo da W; CA-L2 sobre porcas de nivelamento, graute 20 por baixo; as 4 BR-M16 atravessam a chapa e a mesa inferior (gabarito 55); arruela, porca e contraporca por dentro da W. No C (fixo): furo padrão e torque. Nos demais: furo oblongo 18 × 40 ao longo da W e porca encostada (folga ≤ 1 mm).",
         "Montantes (DEC-052): espera EM-L2 posta por quem faz a capa, ANTES da concretagem, com gabarito de chapa 6,3 (furos 300 × 60, eixo do montante sobre uma alça N9, barras a 0 e 60 do eixo da linha 2 para o lado da borda): cada barra laçada com o gancho por baixo da alça. Montar o montante só com a capa curada (fck ≥ 21 MPa): graute 20 sob as CB-M1, montante + CB-M1/CB-M2, W apoiada e parafusada nos 4 M16 da mesa (furo oblongo ao longo da W). Eixo do montante 30 mm para dentro da faixa de 2º estágio (excentricidade no cálculo). Topo travado pela W e pelas terças; base pelas 4 barras.",
         "Emendas nas posições da elevação (perto do momento nulo, módulos ≤ 12 m): TL-1 nas mesas e TL-2 nos dois lados da alma, M16 8.8 com aperto controlado; furos padrão (d + 1,5 mm).",
         "Tudo parafusado na obra, SEM SOLDA; perfis A572-50, chapas e cantoneiras A36, galvanizado a fogo. Terças, telhas e acessórios: ND-LET-COB01 a COB04. VM do +7,30: ND-LET-VM01 (peça sem mudança).",
         "Montagem: mezanino, capa curada e parede G da linha 2 (ND-LET-MON01/MON02) → CA-L2 niveladas e grauteadas nos pilares → montantes nas esperas → módulos da W de A para E com as emendas → ST-W e terças → mãos-francesas.",
         "Cotas em mm, níveis em m. Não medir no desenho."]
pr.notas(XC, y - 4, notas, 182)
json.dump(dict(total_kg=round(TOT), linhas=lin), open("/home/claude/letsara/pranchas/cob05_lista.json", "w"), ensure_ascii=False, indent=1)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-COB05")
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
for a in avisos:
    print(a)
