"""ND-LET-VM01 rev04 — vigas do mezanino VM-01 / VM-02 em MEIO VASO (padrão ND: vigas de apoio de laje alveolar), com
dente Gerber 35 × 35 na ponta maciça (fundo do consolo CP-MEZ alinhado ao fundo da viga). Fôrma, 2º estágio, apoio,
cantoneira antigiro CT-1, insertos, protensão (posição e força no macaco) e notas da NBR 9062:2017 5.6.1.2.
Armadura passiva: ND-LET-AR-VIG-03 (padrão de armação). Cálculo: calc_vm_meio_vaso.py, calc_vm_dente.py, mef_vm_dente.py,
calc_nbr9062.py. Concreto em cm, chaparia em mm."""
import json, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha
AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
sys.path.insert(0, AQ)
from geometria import X_EIXO, Y_LIN

f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
VMJ = json.load(open(AQ + "vm_meio_vaso.json"))
N9 = json.load(open(AQ + "nbr9062.json"))
R = VMJ["VM-02"]
P = VMJ["premissas"]
H, BA, BB, HA = round(P["h_pm"] * 1000), round(P["b_alma"] * 1000), round(P["b_aba"] * 1000), round(P["h_aba"] * 1000)
B = BA + BB
HD, LN, MAC = round(P["dente"]["hd"] * 1000), round(P["dente"]["ln"] * 1000), round(P["dente"]["macico"] * 1000)
REC = H - HD                                  # recorte 300
FOLGA, X_PAD, A_PAD = 30, 186, 150            # mm, a partir da face do pilar
HC, PROJ = round(P["dente"]["consolo_h"] * 1000), round(P["dente"]["consolo_proj"] * 1000)
H2, HCAPA, NEOF = 200, 50, 10                 # 2º estágio (= laje h20), capa, neoprene em fita da laje
L = round(R["L_peca"] * 1000)
L1 = round(VMJ["VM-01"]["L_peca"] * 1000)
X_TB = X_PAD - FOLGA                          # eixo do tubo TB-1 a partir da ponta da viga (156)
Z_PISO = (3150, 6550)
ZB = [z - HCAPA - H2 - NEOF - H for z in Z_PISO]          # fundo da VM: +2,24 / +5,64
ZA = [z + H for z in ZB]                                  # topo da peça = apoio da laje (−1 cm de fita)
CORD = R["pos_cordoalhas_mm"]
F_MAC = R["protensao"]["F_macaco_kN"]
PESO = R["secao"]["peso_t"]
V = R["secao"]["volume_m3"]
V_MAC = (B * H / 1e6 - R["secao"]["A"]) * MAC / 1000 * 2 - B * REC * LN / 1e9 * 2
V_TOT = V + V_MAC
PESO_TOT = V_TOT * 2.5

pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="VIGAS DO MEZANINO VM-01 / VM-02 — MEIO VASO PROTENDIDO COM DENTE GERBER — FÔRMA, 2º ESTÁGIO, APOIO E INSERTOS",
                        desenho="ND-LET-VM01", folha="01/01", fase="PARA APROVAÇÃO", marca="VM-02", qtd=8, peso=f(PESO_TOT, 2), volume=f(V_TOT, 2)))
pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL (I90 COM DENTE)")
pr.revisao("03", "14/10/2026", "SEM SOLDA: TB-1 PASSANTE, SEM CHAPA CH-A1")
pr.revisao("04", "16/10/2026", f"NBR 9062: MEIO VASO 40 × {H/10:g} (ALMA 25 + ABA 15 × 20) COM DENTE {HD/10:g} × 35; 2º ESTÁGIO E ALÇAS; CT-1")
pr.revisao("06", "19/10/2026", "DEC-032: PERDAS 9.6.3 E γp 1,1 NO ATO; DENTE VERIFICADO POR MEF COM A ARMAÇÃO DA PRANCHA (γn 1,2); LIBERAÇÃO GRADUAL")
Q = pr.quadro
XC = Q[2] - 200
pr.cabecalho_peca("VM-02", f"VIGA DO MEZANINO — MEIO VASO 40 × {H/10:g} cm (+ 2º ESTÁGIO 26 cm) — L = {L/10:g} cm  ·  VM-01: L = {L1/10:g} cm".replace(".", ","),
                  f"linhas 1 e 2, pisos +3,15 e +6,55; fundo da viga e do consolo +{f(ZB[0]/1000, 2)} / +{f(ZB[1]/1000, 2)}; alma 25 do lado da borda, aba 15 × 20 para dentro (apoio da laje)   ·   "
                  f"PESO {f(PESO_TOT, 2)} t   ·   VOLUME {f(V_TOT, 2)} m³   ·   C40, {len(CORD)} Ø12,7 CP-190 RB", largura=XC - Q[0] - 12)

# ------------------------------------------------------------------ planta-chave
M = lambda v: v * 1000
kp = pr.vista("PLANTA-CHAVE", (XC - 120, Q[3] - 125), 1000, titulo="PLANTA-CHAVE", subtitulo="VM nas linhas 1 e 2 (2 níveis)", unidade="cm")
XF = [X_EIXO[k] for k in "ABCDE"]
for y in Y_LIN[:3]:
    kp.linha((M(-2), M(y)), (M(42), M(y)), "EIXO")
for x in XF:
    kp.linha((M(x), M(-2)), (M(x), M(22)), "EIXO")
for i, y in enumerate(Y_LIN[:3], 1):
    kp.texto((M(-3.5), M(y)), str(i), "min", "MIDDLE_RIGHT")
for n, x in zip("ABCDE", XF):
    kp.texto((M(x), M(23)), n, "min", "BOTTOM_CENTER")
for y in Y_LIN[:2]:
    for k in range(4):
        kp.ret(M(XF[k]) + 300, M(y) - 200, M(XF[k + 1] - XF[k]) - 600, 400, "CORTADO")
        kp.texto((M((XF[k] + XF[k + 1]) / 2), M(y) + (-700 if y == 0 else 700)), "VM-01" if k in (0, 3) else "VM-02", "min", "TOP_CENTER" if y == 0 else "BOTTOM_CENTER")
kp.ret(M(0), M(0) + 200, M(XF[-1]), M(Y_LIN[1]) - 400, "OCULTA")
kp.texto((M(19.75), M(Y_LIN[1] / 2)), "laje alveolar h20 + 5", "min", "MIDDLE_CENTER")

# ------------------------------------------------------------------ ELEVAÇÃO DE FÔRMA 1:20 (vista de dentro, lado da aba)
ESC = 15
Y_EL = Q[3] - 125
ve = pr.vista("ELEVAÇÃO", (Q[0] + 40, Y_EL), ESC, titulo="ELEVAÇÃO DE FÔRMA — VM-02 (vista do lado da laje)",
              subtitulo=f"pontas maciças 40 × {H/10:g} em 100 cm; dente {HD/10:g} × 35; alças N9 saindo 20 cm em toda a viga", unidade="cm")
ve.poli([(0, REC), (LN, REC), (LN, 0), (L - LN, 0), (L - LN, REC), (L, REC), (L, H), (0, H)], "VISTA", fechada=True)
ve.linha((MAC, H - HA), (L - MAC, H - HA), "VISTA")                      # fundo da aba (visto de dentro)
for x in (MAC, L - MAC):
    ve.linha((x, 0), (x, H - HA), "VISTA")                                # transição maciço × seção T
for x in range(150, L - 100, 150):
    ve.linha((x, H), (x, H + 200), "ARM_TRANSV")                          # alças N9
for x in (X_TB, L - X_TB):
    ve.ret(x - 25, REC, 50, HD, "OCULTA")                                 # TB-1
for x in (1100, L - 1100):
    ve.poli([(x - 60, H), (x - 60, H + 90), (x, H + 130), (x + 60, H + 90), (x + 60, H)], "METALICA")   # AL-1
ve.cota_h([0, LN, MAC, L / 2, L - MAC, L - LN, L], 0, -12)
ve.cota_v([0, REC, H - HA, H, H + 200], L, 12, total=False)
ve.cota_ord([0, X_TB, 1100, L - 1100, L - X_TB, L], H + 200, 12, x0=0)
ve.chamada((LN, REC / 2), (10, -14), f"recorte {REC/10:g} × 35 (dente)")
ve.chamada((X_TB, REC + HD / 2), (14, 16), f"TB-1 Ø50×3,0 L={HD} (pino PN-1 do CP-MEZ)")
ve.chamada((L - 1100, H + 120), (10, 10), "AL-1 laço Ø12,7 (2x)")
ve.chamada((L / 2 + 75, H + 200), (8, 12), "N9 alças Ø10 c/15 (20 cm acima da peça)")
ve.chamada((L - MAC, H - HA - 60), (10, -14), "fim da ponta maciça")
ve.marcador_corte((L / 2 - 600, -18 * ESC), (L / 2 - 600, H + 22 * ESC), "A", lado=1)
ve.marcador_corte((600, -18 * ESC), (600, H + 22 * ESC), "B", lado=1)
ve.marcador_detalhe((LN / 2, H / 2), 650, 1, ang=-150, dist=8)

# ------------------------------------------------------------------ CORTE A-A 1:10 — seção corrente + 2º estágio + laje + capa
YR = Y_EL - 300
ca = pr.vista("CORTE A-A", (Q[0] + 95, YR), 5, titulo="CORTE A-A — SEÇÃO CORRENTE E 2º ESTÁGIO",
              subtitulo="pré-moldado (hachura) + 2º estágio e capa de obra (tracejado) + laje alveolar", unidade="cm")
sec = [(0, 0), (BA, 0), (BA, H - HA), (B, H - HA), (B, H), (0, H)]
ca.poli(sec, "CORTADO", fechada=True); ca.hachura(sec, "AR-CONC", 0.03)
e2 = [(0, H), (B - 100, H), (B - 100, H + NEOF + H2), (0, H + NEOF + H2)]
ca.poli(e2, "OCULTA", fechada=True); ca.hachura(e2, "ANSI31", 0.6)
LAJ = 1000
ca.poli([(B - 100, H + NEOF), (LAJ, H + NEOF), (LAJ, H + NEOF + H2), (B - 100, H + NEOF + H2)], "VISTA", fechada=True)
for xc in (B - 100 + 110, B - 100 + 320, B - 100 + 530):
    if xc + 76 < LAJ:
        ca.circulo((xc, H + NEOF + H2 / 2), 76, "VISTA")
ca.interrupcao((LAJ, H + NEOF - 20), (LAJ, H + NEOF + H2 + HCAPA + 20))
ca.ret(B - 100, H, 100, NEOF, "METALICA")
capa = [(0, H + NEOF + H2), (LAJ, H + NEOF + H2), (LAJ, H + NEOF + H2 + HCAPA), (0, H + NEOF + H2 + HCAPA)]
ca.poli(capa, "OCULTA", fechada=True); ca.hachura(capa, "ANSI31", 0.6)
for x in (40, BA - 40):
    ca.linha((x, 35), (x, H + 200), "ARM_TRANSV")                             # N9 (pernas da alça)
ca.linha((40, 35), (BA - 40, 35), "ARM_TRANSV")
for x, y in CORD:
    ca.circulo((x, y), 6.35, "ARM_PROT_SECAO")
ca.cota_h([0, BA, B - 100, B], 0, -10, total=True)
ca.cota_v(sorted({0} | {c[1] for c in CORD[:-2]} | {H - HA, H, H + NEOF + H2, H + NEOF + H2 + HCAPA}), -60, -10, total=False)
ca.chamada((BA / 2, H / 3), (-26, -6), "alma 25 (lado da borda)")
ca.chamada((B - 50, H - HA / 2), (14, -12), "aba 15 × 20")
ca.chamada((B - 50, H + NEOF / 2), (16, 6), "apoio da laje 10 cm + neoprene em fita 10")
ca.chamada((120, H + 120), (-24, 14), "2º ESTÁGIO C30 (obra, com a capa)")
ca.chamada((LAJ - 150, H + NEOF + H2 + HCAPA), (8, 10), "capa 5 cm C30 + tela (obra)")
ca.chamada((LAJ - 120, H + NEOF + H2 / 2), (8, -14), "laje alveolar h20")
ca.chamada((BA - 40, H + 160), (10, 8), "N9 Ø10 c/15 (alça)")
ca.chamada((CORD[0][0], CORD[0][1]), (-20, -12), f"{len(CORD) - 2} cord. Ø12,7 (y = " + " / ".join(sorted({f"{c[1]/10:g}" for c in CORD[:-2]})) + ")")
ca.chamada((CORD[-1][0], CORD[-1][1]), (14, 4), f"2 cord. Ø12,7 na aba (y = {CORD[-1][1]/10:g})")

# ------------------------------------------------------------------ CORTE B-B 1:10 — ponta maciça
cb = pr.vista("CORTE B-B", (Q[0] + 355, YR), 5, titulo="CORTE B-B — PONTA MACIÇA", subtitulo=f"40 × {H/10:g} nos 100 cm das pontas", unidade="cm")
pb = [(0, 0), (B, 0), (B, H), (0, H)]
cb.poli(pb, "CORTADO", fechada=True); cb.hachura(pb, "AR-CONC", 0.03)
cb.linha((BA, 0), (BA, H - HA), "OCULTA")
for x, y in CORD:
    cb.circulo((x, y), 6.35, "ARM_PROT_SECAO")
cb.cota_h([0, BA, B], 0, -10); cb.cota_v([0, REC, H], B, 10, total=False)
cb.chamada((BA, H / 3), (12, -8), "seção T tracejada")

# ------------------------------------------------------------------ DETALHE 1 — apoio no CP-MEZ (vista do lado de fora)
YD = YR - 10
d1 = pr.vista("DETALHE 1", (Q[0] + 585, YD), 6, titulo="DETALHE 1 — DENTE GERBER NO CONSOLO CP-MEZ (VISTA DE FORA)",
              subtitulo="fundo do consolo alinhado ao fundo da viga; continuidade N11 pelas bainhas do pilar", unidade="cm")
LD = 1500
d1.ret(-FOLGA - 400, -250, 400, H + NEOF + H2 + HCAPA + 350, "OCULTA")                         # pilar (40 na direção da viga)
cons = [(-FOLGA, 0), (-FOLGA + PROJ, 0), (-FOLGA + PROJ, HC), (-FOLGA, HC)]
d1.poli(cons, "CORTADO", fechada=True); d1.hachura(cons, "AR-CONC", 0.03)
d1.chapa(X_PAD - FOLGA - A_PAD / 2, HC, A_PAD, NEOF, 0.4)                                          # NEO-5
d1.poli([(0, REC), (LN, REC), (LN, 0), (LD, 0)], "VISTA"); d1.poli([(LD, H), (0, H), (0, REC)], "VISTA")
d1.interrupcao((LD, 0), (LD, H))
d1.ret(X_TB - 25, REC, 50, HD, "OCULTA")
d1.ret(X_TB - 10, HC - 300, 20, 700, "METALICA")                                                  # PN-1 Ø20 L=700 (300 no consolo)
e2 = [(-FOLGA, H), (LD, H), (LD, H + NEOF + H2), (-FOLGA, H + NEOF + H2)]
d1.poli(e2, "OCULTA", fechada=True); d1.hachura(e2, "ANSI31", 0.6)
cp_ = [(-FOLGA - 400, H + NEOF + H2), (LD, H + NEOF + H2), (LD, H + NEOF + H2 + HCAPA), (-FOLGA - 400, H + NEOF + H2 + HCAPA)]
d1.poli(cp_, "OCULTA", fechada=True)
jt = [(-FOLGA, REC), (0, REC), (0, H), (-FOLGA, H)]
d1.poli(jt, "VISTA", fechada=True); d1.hachura(jt, "AR-SAND", 0.3)
d1.linha((-FOLGA - 600, H + 120), (1100, H + 120), "ARMADURA")                                    # N11 (bainha no pilar)
d1.ret(-FOLGA - 400, H + 120 - 25, 400, 50, "OCULTA")
d1.linha((-FOLGA - 600, H + NEOF + H2 + HCAPA - 30), (1300, H + NEOF + H2 + HCAPA - 30), "ARMADURA")   # N12 na capa
d1.chapa(-FOLGA, H - 150, 152, 150, 0.4)                                                           # CT-1 (aba de 152 na face externa)
d1.circulo((110, H - 75), 12, "METALICA")
for x in range(150, LD - 50, 150):
    d1.linha((x, H), (x, H + 200), "ARM_TRANSV")
d1.cota_h([-FOLGA, 0, X_TB, LN, -FOLGA + PROJ], 0, -14, total=False)
d1.cota_h([-FOLGA, X_PAD - FOLGA - A_PAD / 2, X_PAD - FOLGA + A_PAD / 2], HC + NEOF, 10, total=False)
d1.cota_v([0, HC, REC, H, H + NEOF + H2, H + NEOF + H2 + HCAPA], LD, 12, total=False)
d1.chamada((-FOLGA + PROJ / 2, HC / 2), (-30, -14), f"CP-MEZ 40 × {PROJ/10:g} × {HC/10:g} (sem chanfro), tirante {N9['consolos'][1]['tirante'].split(' (')[0]}")
d1.chamada((X_PAD - FOLGA, HC + 5), (22, -16), "NEO-5 300×150×10 (furo Ø30)")
d1.chamada((X_TB, HC - 250), (30, -12), "PN-1 Ø20 L=700 (300 no consolo), grauteado")
d1.chamada((-FOLGA / 2, REC + HD / 2), (-26, 10), "junta 3 cm grauteada (obra, antes da capa)")
d1.chamada((60, H - 40), (10, 22), "CT-1 L 152×102×12,5 L=150 + 1 M20 (BR-2) — det. 2")
d1.chamada((-FOLGA - 300, H + 120), (-14, 14), "N11 6 Ø16 em 2 bainhas BA-1 Ø50 (obra)")
d1.chamada((1200, H + NEOF + H2 + HCAPA - 30), (8, 14), "N12 8 Ø12,5 na capa (obra)")
d1.chamada((800, H + 100), (10, 10), "2º estágio (obra)")

# ------------------------------------------------------------------ DETALHE 2 — CT-1 em planta (mm)
d2 = pr.vista("DETALHE 2", (Q[0] + 190, YR - 210), 4, titulo="DETALHE 2 — CANTONEIRA ANTIGIRO CT-1 (PLANTA)",
              subtitulo="parafusada, sem solda; trava a torção de montagem (laje de um lado só)", unidade="mm")
d2.ret(-400, -300, 400, 600, "CORTADO"); d2.hachura([(-400, -300), (0, -300), (0, 300), (-400, 300)], "AR-CONC", 0.02)   # pilar
d2.ret(30, -200, 450, 400, "VISTA"); d2.interrupcao((480, -220), (480, 220))                                           # VM (face externa em y = −200)
d2.chapa(0, -200 - 102, 12.5, 102, 0.4)                                                            # aba de 102 na face do pilar
d2.chapa(0, -200 - 12.5, 152, 12.5, 0.4)                                                           # aba de 152 na face da VM
d2.ret(-22, -260, 22, 40, "METALICA")                                                              # trilho TR-2 embutido
d2.linha((-22, -240), (12.5, -240), "METALICA")
d2.linha((110, -200 - 12.5), (110, -80), "METALICA")                                               # M20 na bucha BR-2
d2.ret(100, -200, 20, 120, "OCULTA")
d2.cota_h([0, 30, 110, 152], -330, -10, total=False)
d2.cota_v([-302, -200, 200], 480, 10, total=False)
d2.chamada((-11, -250), (-24, -12), "trilho TR-2 HTA-CE 40/22 vertical (IP-02 no pilar) + 2 parafusos T M16")
d2.chamada((76, -206), (14, -18), "CT-1: aba 152 com furo oblongo 22×40 horizontal")
d2.chamada((110, -120), (16, 12), "bucha BR-2 M20 hef 120 + barra transversal")
d2.chamada((300, 100), (10, 10), "VM (alma 25 do lado da borda)")
d2.chamada((-200, 0), (-10, 16), "pilar")

# ------------------------------------------------------------------ isométrico da ponta (iso3d_vm.py)
import subprocess
subprocess.run([sys.executable, "/home/claude/letsara/pranchas/iso3d_vm.py"], check=True, capture_output=True)
pr.imagem(Q[0] + 560, Q[1] + 40, Q[0] + 560 + 300, Q[1] + 40 + 225, "/home/claude/letsara/pranchas/ISO-VM-ponta.png",
          titulo="ISOMÉTRICO — PONTA DA VM NO PILAR", subtitulo="dente no CP-MEZ (fundos alinhados), CT-1, PN-1, alças N9, 2º estágio (azul) e laje")

# ------------------------------------------------------------------ tabelas (coluna direita)
y = Q[3] - 132
mk = [["VM-01", "A–B e D–E, linhas 1 e 2, 2 níveis", 8, f"{L1/10:g}".replace(".", ","), f(VMJ["VM-01"]["secao"]["peso_t"] + V_MAC * 2.5, 2)],
      ["VM-02", "B–C e C–D, linhas 1 e 2, 2 níveis", 8, f"{L/10:g}".replace(".", ","), f(PESO_TOT, 2)]]
y = pr.tabela(XC, y, "MARCAS — VIGAS DO MEZANINO", ["MARCA", "POSIÇÃO", "QT", "L (cm)", "PESO (t)"], mk, [18, 92, 10, 24, 24])
from collections import Counter
_rows = sorted(Counter(c[1] for c in CORD).items())
_cl = []
for k_, (yy, nn) in enumerate(_rows):
    if k_ == 0:
        _cl += [dict(pos="C1", diam=12.7, qtd=2, y=yy, forca=F_MAC, isol=1500), dict(pos="C2", diam=12.7, qtd=nn - 2, y=yy, forca=F_MAC, isol=0)]
    else:
        _cl.append(dict(pos=f"C{k_ + 2}", diam=12.7, qtd=nn, y=yy, forca=F_MAC, isol=0))
tc = pr.tabela_cordoalhas(XC, y - 4, _cl, 60)
y = tc["y_base"]
ins = [["TB-1", f"Tubo Ø50×3,0 L={HD} a prumo no nariz do dente, sem solda", 2, f"a {X_TB/10:g} cm das pontas, no eixo"],
       ["BR-2", "Bucha M20 hef 120 c/ barra transversal (CT-1)", 2, "face ext., 11 da ponta, 7,5 do topo"],
       ["AL-1", "Laço de cordoalha Ø12,7 (2 pernas), não engraxada", 2, "a 110 cm das pontas"],
       ["CT-1", "L 152×102×12,5 A36 L=150 + 1 M20 8.8 + 2 T M16", 2, "obra: trilho IP-02 do pilar × BR-2"],
       ["NEO-5", "Neoprene 300×150×10 (furo Ø30) — no pilar", 2, "sobre os consolos CP-MEZ"]]
y = pr.tabela(XC, y - 4, "INSERTOS POR PEÇA (VM-02) — mm", ["MARCA", "DESCRIÇÃO", "QT", "POSIÇÃO"], ins, [16, 92, 10, 50])
obra = [["N11", "6 Ø16 L=600 em 2 bainhas BA-1 do pilar (negativa)", "apoios B, C, D"], ["N12", "8 Ø12,5 L=600 na capa (negativa)", "apoios B, C, D"],
        ["CAPA", "C30, 5 cm + tela; 2º estágio C30 (26 cm)", "quem faz a capa"], ["GRAUTE", "junta 3 cm e bainhas, fck ≥ 30 MPa", "antes da capa"]]
y = pr.tabela(XC, y - 4, "ARMADURA E CONCRETO DE OBRA (NBR 9062 5.6.1.2 e)", ["ITEM", "DESCRIÇÃO", "ONDE"], obra, [16, 110, 42])
qd = [["CONCRETO", "C40 (CAA II)", "fcj LIBERAÇÃO", f"{P['fckj']:g} MPa"], ["fcj IÇAMENTO", f"{P['fckj']:g} MPa", "Eci / Ecs", f"{P['Eci_MPa']/1000:.1f} / {P['Ecs_MPa']/1000:.1f} GPa".replace(".", ",")],
      ["Eci,j (ato)", f"{P['Eci_j_MPa']/1000:.1f} GPa".replace(".", ","), "COBRIMENTO", "2,5 (estribo) / 3,0 (cord.)"],
      ["VOLUME", f"{f(V_TOT, 2)} m³", "PESO", f"{f(PESO_TOT, 2)} t"], ["F MACACO", f"{f(F_MAC)} kN/cord.", "σpi", "1400 MPa"]]
y = pr.tabela(XC, y - 4, "QUADRO DA PEÇA (VM-02)", ["ITEM", "VALOR", "ITEM", "VALOR"], qd, [30, 54, 30, 54])
notas = [
    f"MEIO VASO (padrão ND): peça pré-moldada termina no nível de apoio da laje (topo plano); acima da alma e até a ponta da laje vai o 2º ESTÁGIO, concretado junto com a capa POR QUEM EXECUTA A CAPA. Alças N9 Ø10 c/15 em toda a viga (interface NBR 9062:2017 6.3: τsd {f(R['interface']['tau_sd'], 2)} ≤ τRd {f(R['interface']['tau_rd'], 2)} MPa). Topo da peça rugoso (pente, ≥ 5 mm a cada 30 mm), limpo e saturado antes da concretagem.",
    "SEM ESCORAMENTO: a peça isolada leva peso próprio, laje, 2º estágio e capa frescos e 1 kN/m² de montagem (fase 1); revestimento e sobrecarga de 5 kN/m² na seção composta (fase 2).",
    f"Dente Gerber {HD/10:g} × 35 nas pontas maciças (NBR 9062:2017 7.4; MEF não linear): fundo do consolo CP-MEZ = fundo da viga (+{f(ZB[0]/1000, 2)} e +{f(ZB[1]/1000, 2)}). Pino PN-1 Ø20 grauteado no TB-1 numa ponta; na outra graute flexível.",
    "TORÇÃO DE MONTAGEM (laje de um lado só): instalar a CT-1 nas duas pontas ANTES de soltar a viga do guindaste e antes de montar a laje (NBR 9062:2017 11.1); montar as lajes do vão a partir da VM; a CT-1 fica definitiva.",
    "Obra (sequência): VM + CT-1 → lajes alveolares (apoio 10 cm, neoprene em fita) → grautear junta das pontas e bainhas BA-1 com N11 → limpar e saturar o topo → N12, tela e chavetas → 2º estágio + capa de uma vez → cura 7 dias; carregar com fck ≥ 20 MPa.",
    f"Protensão: {len(CORD)} cordoalhas Ø12,7 CP-190 RB aderentes (posição no corte A-A e na tabela), σpi = 1400 MPa; C1 isoladas 150 cm nas pontas; as 2 da aba equilibram a excentricidade lateral (resultante no centroide da seção T). Liberação GRADUAL e simétrica com fcj ≥ 32 MPa (lbpt = {f(R['ato']['lbpt_m'] * 100, 0)} cm; perdas pela NBR 6118 9.6.3 — total {f(R['protensao']['perdas']['perda_total_pct'])} %).",
    "Içar pelas 2 alças AL-1 (cabos ≥ 45°); estocar sobre 2 calços sob as alças, pressão ≤ 0,3 fcj; transportar apoiada nos mesmos pontos, travada contra tombamento.",
    "Tolerâncias (NBR 9062:2017 5.2.2): comprimento ±15 mm, seção −5/+10 mm, linearidade ±L/1000, insertos ±15 mm, cordoalhas ±10 mm (resultante ±5); montagem: nível do apoio ±10 mm, planta ±10 mm. Folga de 3 cm na ponta.",
    "Cotas de concreto em cm, chaparia em mm. Armadura passiva: ND-LET-AR-VIG-03. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
y = pr.notas(XC, y - 4, notas, 190)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-VM01")
print("VM01", len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
for a in avisos:
    if a[0] == "ERRO" or "sobrep" in a[1] or "cruza" in a[1]:
        print(" ", a)
