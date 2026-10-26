"""ND-LET-COB04 — cobertura: acabamentos no sistema Isoeste zipada dupla com lã de rocha (rev06c): pacote, beiral na
calha (eixo A), encosto no lado alto (eixo E), bordas laterais (linhas 1 e 9), rufo chapéu da platibanda, costura dos rufos,
planta de rufos e de clipes, lista de rufos e acessórios. Geometria: acabamentos_cob.py. Metálica em mm, níveis em m. A1."""
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
import json
import math
import acabamentos_cob as AC
from prancha_nd import Prancha
from cob_comum import cabecalho, XT, H_TERCA, B_TERCA, B_INF, D_SUP, D_INF, f

R = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/acabamentos_cobertura.json"))
S = AC.secoes()
pr = Prancha("A1", cabecalho("ND-LET-COB04", "04/04", "COBERTURA — ACABAMENTOS DE FUNILARIA (FEITOS NA OBRA): BEIRAIS, ENCOSTOS, PLATIBANDA E RUFOS"))
pr.revisao("06", "18/10/2026", "EMISSÃO: ACABAMENTOS DA COBERTURA CONFORME O MANUAL DA TELHA (P. 28 A 46)")
pr.revisao("11", "26/10/2026", "ACABAMENTOS (RUFOS, CONTRA-RUFOS, PINGADEIRAS, CAPAS) FEITOS POR FUNILEIRO NA OBRA — NÃO SÃO DE CATÁLOGO (NATHAN)")
Q = pr.quadro
XC = Q[2] - 250
C45 = math.cos(math.radians(45))
mm = lambda v: v * 1000
I3 = AC.I
CONC = "AR-CONC"


def zt(x_mm):                                    # topo da terça (mm) em x (mm)
    return mm(AC.z_terca_topo(x_mm / 1000))


def terca(v, x0):
    """seção da Z 302 com a alma em x0 (mm), aba superior de 90 para o lado A."""
    z0 = zt(x0) - H_TERCA
    pts = [(x0 + (B_INF - D_INF * C45), z0 + D_INF * C45), (x0 + B_INF, z0), (x0, z0), (x0, z0 + H_TERCA), (x0 - B_TERCA, z0 + H_TERCA),
           (x0 - B_TERCA + D_SUP * C45, z0 + H_TERCA - D_SUP * C45)]
    v.poli(pts, "METALICA")


def pacote_long(v, x0, x1, cart=()):
    """pacote em corte ao longo da água (ondas paralelas ao corte): TP-40 (vale cheio, crista tracejada), lã, zipada (fundo cheio,
    costura tracejada) e cartolas sobre as terças."""
    z = lambda x, dz: zt(x) + dz
    v.poli([(x0, z(x0, 0)), (x1, z(x1, 0))], "METALICA")
    v.poli([(x0, z(x0, 40)), (x1, z(x1, 40))], "OCULTA")
    v.hachura([(x0, z(x0, 40)), (x1, z(x1, 40)), (x1, z(x1, 80)), (x0, z(x0, 80))], "ANSI37", 0.6, "HACHURA")
    v.poli([(x0, z(x0, 80)), (x1, z(x1, 80))], "METALICA")
    v.poli([(x0, z(x0, 150)), (x1, z(x1, 150))], "OCULTA")
    for xc in cart:
        v.ret(xc - 60, z(xc, 40), 120, 40, "METALICA")


def placa(v, x0, z0, z1, larg=100):
    pts = [(x0, z0), (x0 + larg, z0), (x0 + larg, z1), (x0, z1)]
    v.poli(pts, "CORTADO", fechada=True); v.hachura(pts, CONC, 0.03)


def rufo(v, mk, conv=lambda u, w: (u, w)):
    pts = [conv(mm(a), mm(b)) for a, b in S[mk][1]]
    v.poli(pts, "METALICA")
    return pts


# ================================================================== DET 1 — beiral na calha (eixo A, entre pilares) 1:10
ZPA = mm(AC.PLAT)
zc = mm(AC.Z_TOP_CALHA)
d1 = pr.vista("DET 1", (Q[0] + 75, Q[1] + 400 - zc / 10), 10, titulo="DETALHE 1 — BEIRAL NA CALHA (EIXO A, ENTRE PILARES)",
              subtitulo="corte ao longo da água; zipada com perfil pingadeira PG-1 dentro da calha (manual p. 42)", unidade="mm")
zc = mm(AC.Z_TOP_CALHA)
placa(d1, mm(AC.X_PLACA_A) - 100, zc - 400, zc + 520)
d1.interrupcao((mm(AC.X_PLACA_A) - 110, zc + 520), (mm(AC.X_PLACA_A) + 10, zc + 520))
c0 = mm(AC.XC0)
d1.poli([(c0 + 60, zc + 120), (c0, zc + 120), (c0, zc - 150), (c0 + 300, zc - 150), (c0 + 300, zc), (c0 + 325, zc)], "METALICA")
terca(d1, XT[0])
pacote_long(d1, mm(AC.X_TELHA_A), XT[0] + 420, cart=(XT[0] - 45,))
for mk in ("RF-2", "PG-1"):
    rufo(d1, mk)
d1.cota_h([mm(AC.X_PLACA_A), c0, c0 + 300, XT[0] - B_TERCA, XT[0]], zc - 400, -10, total=False)
d1.chamada((mm(AC.X_PLACA_A), zc + 220), (8, 30), "RF-2: PAR Tapper a cada 500 + PU")
d1.chamada((mm(AC.X_TELHA_A) - 15, zc - 60), (8, -24), "PG-1 pingadeira (100 na calha)")
d1.chamada((c0 + 150, zc - 150), (6, -26), "calha CA-1 300 × 150 (ND-LET-COB03)")
d1.chamada((XT[0] - 45, zt(XT[0] - 45) + 60), (6, 36), "perfil cartola #0,65 sobre a terça")
d1.chamada((XT[0] + 250, zt(XT[0] + 250) + 60), (6, 22), "lã de rocha FSR 32")
d1.chamada((XT[0] + 350, zt(XT[0] + 350) + 80), (4, 12), "zipada 455 #0,50")
d1.chamada((XT[0] + 380, zt(XT[0] + 380)), (6, -10), "TP-40 STD #0,65")
d1.texto((c0 + 330, zc + 6), f"+{AC.Z_TOP_CALHA:.3f}".replace(".", ","), "nota", "BOTTOM_LEFT")

# ================================================================== DET 2 — na cabeça do P1 (eixo A) 1:10
d2 = pr.vista("DET 2", (Q[0] + 255, Q[1] + 400 - zc / 10), 10, titulo="DETALHE 2 — CALHA NA CABEÇA DO P1", subtitulo="contra-rufo RF-2C na face da cabeça do P1 (40 × 30); calha a 20 da face", unidade="mm")
pts = [(-300, zc - 400), (0, zc - 400), (0, zc + 520), (-300, zc + 520)]
d2.poli(pts, "CORTADO", fechada=True); d2.hachura(pts, CONC, 0.03)
d2.interrupcao((-310, zc + 520), (10, zc + 520))
d2.poli([(c0 + 60, zc + 120), (c0, zc + 120), (c0, zc - 150), (c0 + 300, zc - 150), (c0 + 300, zc), (c0 + 325, zc)], "METALICA")
rufo(d2, "RF-2C")
d2.chamada((0, zc + 200), (14, 16), "RF-2C: PAR Tapper a cada 250 + PU no topo")
d2.cota_h([-300, 0, c0 + 300], zc - 400, -10, total=False)

# ================================================================== DET 3 — encosto no lado alto (eixo E) 1:10
XE = mm(AC.LARG)
zE = mm(AC.z_zip(AC.X_TELHA_E))
d3 = pr.vista("DET 3", (Q[0] + 432 - XE / 10, Q[1] + 400 - zE / 10), 10, titulo="DETALHE 3 — ENCOSTO NO LADO ALTO (EIXO E, ENTRE PILARES)",
              subtitulo="rufo de topo liso RF-3 com veda-onda; sobe por baixo do rufo chapéu RF-1 (manual p. 40)", unidade="mm")
zE = mm(AC.z_zip(AC.X_TELHA_E))
placa(d3, mm(AC.X_PLACA_E), zE - 600, ZPA)
d3.interrupcao((mm(AC.X_PLACA_E) - 10, zE - 600), (mm(AC.X_PLACA_E) + 110, zE - 600))
terca(d3, XT[-1])
pacote_long(d3, XT[-1] - 700, mm(AC.X_TELHA_E), cart=(XT[-1] - 45,))
for mk in ("RF-3", "CR-1"):
    rufo(d3, mk)
xv = mm(AC.X_TELHA_E)
d3.ret(xv - 40, zE, 40, 70, "METALICA"); d3.hachura([(xv - 40, zE), (xv, zE), (xv, zE + 70), (xv - 40, zE + 70)], "ANSI37", 0.3, "HACHURA")
rufo(d3, "RF-1", lambda u, w: (mm(AC.X_PLACA_E) + 100 - u, w))
d3.poli([(XT[-1] - 700, zt(XT[-1] - 700) + 150), (xv - 200, zt(xv - 200) + 150), (xv - 200, zt(xv - 200) + 260), (XT[-1] - 700, zt(XT[-1] - 700) + 260)], "OCULTA")
d3.cota_h([XT[-1] - B_TERCA, XT[-1], xv, XE, mm(AC.X_PLACA_E), mm(AC.X_PLACA_E) + 100], zE - 600, -10, total=False)
d3.cota_v([zE, zE + 70, ZPA], mm(AC.X_PLACA_E) + 100, 14, total=False)
d3.chamada((xv - 20, zE + 35), (-30, -22), "veda-onda + Z do veda-onda + massa")
d3.chamada((mm(AC.X_PLACA_E) - 20, mm(AC.z_zip(AC.X_TELHA_E)) + 80), (-40, 44), "CR-1 L 40 × 40 #1,25 (Tapper a cada 500)")
d3.chamada((xv - 250, zt(xv - 250) + 230), (-22, 18), "painel solar (tracejado)")
d3.chamada((xv + 100, zE + 95), (6, 34), "RF-3 rufo de topo liso")
d3.chamada((mm(AC.X_PLACA_E) + 50, ZPA + 10), (8, 12), "RF-1 rufo chapéu (det. 5)")
d3.texto((mm(AC.X_PLACA_E) + 200, ZPA), "+10,000", "nota", "MIDDLE_LEFT")

# ================================================================== DET 4 — borda lateral (linhas 1 e 9) 1:5, corte transversal às ondas
d4 = pr.vista("DET 4", (Q[0] + 45, Q[1] + 205), 5, titulo="DETALHE 4 — BORDA LATERAL (LINHAS 1 E 9)",
              subtitulo="corte transversal às ondas; início (linha 1) RB-1, fim (linha 9) RB-2 espelhado (manual p. 34 e 37)", unidade="mm")
zl = 0.0                                                   # referência local: topo da terça
yp = 0.0                                                   # face interna da placa (u = 0)
placa(d4, -100, -500, 420)
d4.interrupcao((-110, -500), (10, -500)); d4.interrupcao((-110, 420), (10, 420))
yb = mm(AC.Y_TELHA_1 - AC.Y_PLACA_1)                       # borda da cobertura (175 da placa)
yv0 = mm(-0.075 - AC.Y_PLACA_1)                            # face da VB
vb = [(yv0, -500), (yv0 + 150, -500), (yv0 + 150, -H_TERCA - 10), (yv0, -H_TERCA - 10)]
d4.poli(vb, "CORTADO", fechada=True); d4.interrupcao((yv0 - 10, -500), (yv0 + 160, -500)); d4.hachura(vb, CONC, 0.03)
d4.ret(yb + 40, -H_TERCA, 640, H_TERCA, "VISTA")           # terça (alma vista) até a ponta
# TP-40 (passo 245, crista 32, base 90) e zipada (costuras a cada 455, altura 70)
pts, u = [], yb
while u < yb + 700:
    pts += [(u, 0), (u + 77, 0), (u + 106, 40), (u + 138, 40), (u + 167, 0)]
    u += 245
d4.poli(pts + [(yb + 700, 0)], "METALICA")
d4.ret(yb + 40, 40, 660, 40, "VISTA")                      # cartola (ao longo da terça)
d4.hachura([(yb, 40), (yb + 700, 40), (yb + 700, 80), (yb, 80)], "ANSI37", 0.6, "HACHURA")
zp = []
u = yb + 60
zp = [(yb + 20, 80)]
while u < yb + 700:
    zp += [(u - 15, 80), (u - 8, 150), (u + 8, 150), (u + 15, 80)]
    u += 455
d4.poli(zp + [(yb + 700, 80)], "METALICA")
conv4 = lambda a, b: (a, b - mm(AC.z_zip(AC.LARG / 2)) - 70 + 80 + 70)
for mk in ("RF-4", "RF-4C", "RB-1/2"):
    rufo(d4, mk, lambda a, b: (a, b - mm(AC.z_zip(AC.LARG / 2) + AC.PAC["zipada"]) + 150))
d4.cota_h([-100, 0, yv0, yb, yb + 60], -540, -8, total=False)
d4.cota_v([0, 40, 80, 150], yb + 700, 10, total=False)
d4.chamada((30, 230), (10, 22), "RF-4C contra-rufo: Tapper a cada 500 + PU")
d4.chamada((yb + 60, 130), (30, 16), "RB-1 / RB-2 rufo de borda + base deslizante")
d4.chamada((yb / 2, 168), (8, 24), "RF-4 rufo de acabamento lateral")
d4.chamada((yv0 + 75, -420), (14, -6), "VB 15 × 60")
d4.chamada((yb + 300, -150), (10, -14), "terça Z 302 (passa 110 do eixo da VB)")

# ================================================================== DET 5 — rufo chapéu (RF-1 e RF-1C) 1:5
d5 = pr.vista("DET 5", (Q[0] + 294, Q[1] + 238 - ZPA / 5), 5, titulo="DETALHE 5 — RUFO CHAPÉU DA PLATIBANDA", subtitulo="RF-1 sobre a placa; RF-1C sobre a cabeça do pilar + placa (manual p. 46)", unidade="mm")
placa(d5, 0, ZPA - 260, ZPA)
d5.interrupcao((-10, ZPA - 260), (110, ZPA - 260))
rufo(d5, "RF-1")
d5.cota_h([-20, 0, 100, 120], ZPA - 290, -8, total=False)
d5.cota_v([ZPA - 100, ZPA - 70, ZPA], 135, 10, total=False)
d5.chamada((-20, ZPA - 40), (-12, 10), "aba externa 70 + pingadeira")
d5.chamada((120, ZPA - 60), (8, 34), "aba interna 100: Tapper a cada 500 + PU")
d5.chamada((50, ZPA + 8), (-24, 14), "caimento 5 % para dentro")
X5 = 300
pts = [(X5, ZPA - 260), (X5 + 100, ZPA - 260), (X5 + 100, ZPA), (X5, ZPA)]
d5.poli(pts, "CORTADO", fechada=True); d5.hachura(pts, CONC, 0.03)
pts = [(X5 + 125, ZPA - 260), (X5 + 425, ZPA - 260), (X5 + 425, ZPA), (X5 + 125, ZPA)]
d5.poli(pts, "CORTADO", fechada=True); d5.hachura(pts, CONC, 0.03)
d5.interrupcao((X5 - 10, ZPA - 260), (X5 + 435, ZPA - 260))
rufo(d5, "RF-1C", lambda u, w: (X5 + u, w))
d5.cota_h([X5 - 20, X5, X5 + 100, X5 + 125, X5 + 425, X5 + 445], ZPA - 290, -8, total=False)
d5.chamada((X5 + 270, ZPA + 12), (6, 14), "RF-1C (peça de 600 sobre cada cabeça)")
d5.texto((X5 + 275, ZPA - 120), "cabeça do pilar", "nota", "MIDDLE_CENTER")
d5.texto((X5 + 50, ZPA - 120), "placa", "nota", "MIDDLE_CENTER", rot=90)

# ================================================================== DET 6 — costura transversal (1:2,5) e DET 7 — pacote (1:5)
d6 = pr.vista("DET 6", (Q[0] + 235, Q[1] + 40), 4, titulo="DETALHE 6 — COSTURA TRANSVERSAL DOS RUFOS", subtitulo="transpasse 200 com fita Tacky Tape e massa", unidade="mm")
d6.linha((0, 0), (400, 0), "METALICA"); d6.linha((200, 3), (600, 3), "METALICA")
d6.ret(250, 0.5, 60, 2, "COTA")
for x in (300, 350):
    d6.linha((x, -10), (x, 14), "METALICA")
d6.cota_h([200, 300, 400], 3, 8, total=True)
d6.chamada((280, 1.5), (-8, -10), "fita Tacky Tape 9,5 + massa vedante")
d6.chamada((350, 14), (20, 6), "2 costuras PB 1/4\"-14 × 7/8\" P01")

d7 = pr.vista("DET 7", (Q[0] + 565, Q[1] + 214), 5, titulo="DETALHE 7 — PACOTE DA COBERTURA (SANDUÍCHE)", subtitulo="corte transversal às ondas sobre a terça (manual p. 28 e 29)", unidade="mm")
d7.ret(0, -50, 400, 50, "VISTA")
pts, u = [], 0
while u < 400:
    pts += [(u, 0), (u + 77, 0), (u + 106, 40), (u + 138, 40), (u + 167, 0)]
    u += 245
d7.poli(pts[:-1] + [(400, 0)], "METALICA")
for xc in (106, 351):
    d7.poli([(xc - 30, 40), (xc - 30, 40), (xc - 15, 40), (xc - 15, 80), (xc + 47, 80), (xc + 47, 40), (xc + 62, 40)], "METALICA")
d7.hachura([(0, 40), (400, 40), (400, 80), (0, 80)], "ANSI37", 0.6, "HACHURA")
d7.poli([(0, 80), (190, 80), (197, 150), (213, 150), (220, 80), (400, 80)], "METALICA")
d7.poli([(195, 80), (195, 95), (215, 95), (215, 80)], "METALICA")
d7.cota_v([-50, 0, 40, 80, 150], 0, -10, total=False)
for k, (yy, t) in enumerate([(-30, "0 terça Z 302 (cliente)"), (20, "1º TP-40 STD 980 #0,65 — PB 12-14 × 3/4\" P03, 4/telha/terça"),
                             (60, "2º cartola #0,65 — PB 1/4\"-14 × 7/8\" P01 em todas as ondas"), (70, "3º lã de rocha FSR 32 (40 mm)"),
                             (90, "4º clipe fixo/deslizante #0,65 — 2 PB 12-14 × 3/4\""), (130, "5º zipada 455 #0,50")]):
    d7.chamada((390, yy), (22, -30 + 13 * k), t)

# ================================================================== PLANTA DE RUFOS E CLIPES (1:400)
pl = pr.vista("PLANTA", (Q[0] + 470, Q[1] + 36), 800, titulo="PLANTA DE COBERTURA — RUFOS E CLIPES", subtitulo="água única de 3 % do eixo A para o eixo E; montagem da linha 1 para a 9", unidade="mm")
W, Lc = mm(AC.LARG), mm(AC.COMP)
pl.ret(mm(AC.X_PLACA_A) - 100, mm(AC.Y_PLACA_1) - 100, W + 650 + 200, Lc + 650 + 200, "VISTA")
pl.ret(mm(AC.X_PLACA_A), mm(AC.Y_PLACA_1), W + 650, Lc + 650, "VISTA")
pl.ret(mm(AC.X_TELHA_A), mm(AC.Y_TELHA_1), mm(AC.X_TELHA_E - AC.X_TELHA_A), Lc + 300, "METALICA")
xm = mm(AC.LARG / 2)
pl.ret(xm - 1300, mm(AC.Y_TELHA_1), 2600, Lc + 300, "OCULTA")
pl.texto((xm, Lc / 2), "clipes FIXOS (2 terças no meio da água)", "nota", "MIDDLE_CENTER", rot=90)
pl.texto((xm / 2, Lc / 2), "clipes deslizantes", "nota", "MIDDLE_CENTER", rot=90)
pl.texto((xm * 1.5, Lc / 2), "clipes deslizantes", "nota", "MIDDLE_CENTER", rot=90)
pl.chamada((mm(AC.X_PLACA_A) + 200, Lc * 0.7), (-16, 0), "eixo A: calha, PG-1, RF-2/RF-2C (det. 1 e 2)")
pl.chamada((W + 200, Lc * 0.7), (16, 0), "eixo E: RF-3/RF-3P, CR-1 (det. 3)")
pl.chamada((xm * 0.6, mm(AC.Y_PLACA_1) + 100), (6, -12), "linha 1: RF-4, RF-4C, RB-1 (det. 4)")
pl.chamada((xm * 0.6, Lc + 200), (6, 12), "linha 9: RF-4, RF-4C, RB-2 (det. 4)")
pl.chamada((W + 400, Lc * 0.3), (16, -6), "perímetro: RF-1 / RF-1C (det. 5)")
pl.texto((xm, -900), "sobe 3 % →", "nota", "TOP_CENTER")

# ================================================================== tabelas
rows = [[r["marca"], r["descricao"][:58] + ("…" if len(r["descricao"]) > 58 else ""), r["chapa"], r["desenv_mm"], f(r["comprimento_m"], 1), r["pecas"]] for r in R["rufos"]]
y = pr.tabela(XC, Q[3] - 6, "LISTA DE RUFOS — FUNILARIA DA OBRA (chapa dobrada)", ["MARCA", "DESCRIÇÃO", "CHAPA", "DESENV.", "m", "PÇ"], rows, [16, 132, 30, 18, 18, 16], h_lin=5.2)
ac = [[a["item"], a["uso"], a["qtd"]] for a in R["acessorios"]]
y = pr.tabela(XC, y - 4, "ACESSÓRIOS E FIXAÇÕES DOS ACABAMENTOS — OBRA", ["ITEM", "USO", "QTD"], ac, [68, 148, 14], h_lin=5.2)
TL = R["telhas"]
tl = [[t["item"], t["un"], t["liq"] if not isinstance(t["liq"], float) else f(t["liq"], 1), t["compra"], (t["obs"][:60] + ("…" if len(t["obs"]) > 60 else "")).replace(".", ",")] for t in TL["itens"]]
y = pr.tabela(XC, y - 4, f"TELHAS, CARTOLAS E FIXAÇÕES — ÁREA {f(TL['area_m2'], 0)} m² (COMPRA: +{TL['perda'] * 100:.0f} %)",
              ["ITEM", "UN", "LÍQ.", "COMPRA", "OBSERVAÇÃO"], tl, [84, 14, 14, 16, 102], h_lin=5.2)
FT = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/fixacao_telhas.json"))
bo = FT["zonas"]["borda"]["ligacoes"]
pr.notas(XC, y - 4, [
    "Sistema Isoeste — Telha Zipada Dupla com lã de rocha FSR-32 (manual de instalação da telha zipada, p. 28): 1º TP-40 STD 980 #0,65 na terça; 2º perfil cartola #0,65 sobre cada terça; 3º lã de rocha FSR 32; 4º clipe fixo ou deslizante #0,65 na cartola; 5º zipada 455 #0,50 perfilada na obra (comprimento da água 39,6 m, sem emenda).",
    f"Fixações verificadas à sucção (zona de borda, NBR 6123): TP-40 × terça uso {f(bo['TP-40 → terça (PB 12-14 × 3/4\" P03, 4 por telha)']['uso'], 2)}; cartola × TP-40 com costura em TODAS as ondas uso {f(bo['cartola → TP-40 (PB 1/4\"-14 × 7/8\" P01, em todas as ondas)']['uso'], 2)} (a cada 2 ondas, como no manual, daria {f(bo['cartola → TP-40 (PB 1/4\"-14 × 7/8\" P01, a cada 2 ondas)']['uso'], 2)}); clipe × cartola {f(bo['clipe → cartola (PB 12-14 × 3/4\", 2 por clipe)']['uso'], 2)}. Confirmar com a Isoeste os valores de arrancamento em #0,65.",
    "Clipes fixos nas 2 terças do meio da água (dilatação para os dois lados, ≈ 20 m); deslizantes nas demais. Água de 39,6 m: confirmar com a Isoeste se dispensa junta de dilatação transversal (manual p. 32).",
    "Rufos em galvalume #0,50 (funilaria feita na obra), peças de 3 m com transpasse de 200 (det. 6); nos pilares, peças de 600 recortadas e dobradas, cantos rebitados e selados (sem solda). Cortes com tesoura ou serra, nunca esmerilhadeira; limpar as limalhas no mesmo dia.",
    "Fixação no concreto (placas e cabeças): PAR Tapper 1/4\" × 2 3/4\" a cada 500 mm (250 nas peças de pilar), furos com broca de vídia, selante PU no topo dos contra-rufos. Não fixar a 50 mm das bordas das placas nem sobre as cordoalhas (eixo a 26 mm das faces).",
    "Sequência: calha e RF-2 → TP-40 → cartolas → lã → clipes → zipada (da linha 1 para a 9) → PG-1, veda-ondas e RF-3 → RB e RF-4 → RF-1 / RF-1C por último. Não pisar nos rufos; circular sobre as costuras da zipada.",
    f"Níveis: borda da calha +{f(AC.Z_TOP_CALHA, 3)}; zipada (fundo) +{f(AC.z_zip(AC.X_TELHA_A), 3)} no eixo A e +{f(AC.z_zip(AC.X_TELHA_E), 3)} no eixo E; platibanda +10,000.",
    "DEC-042 — cantos (pilares P1, P9, P25 e P33): seção cheia 40 × 60 até +10,00, sem platibanda recuada — a face interna fica 30 cm mais para dentro que a cabeça dos demais pilares do eixo. RF-2C (eixo A) e RF-3P (eixo E) dos cantos acompanham essa face; a TP-40, a lã, a zipada e os painéis das faixas junto às fachadas 1 e 9 são recortados no canto (x de 0,31 a 39,19 m até 21 cm do eixo da linha) e o RF-4, o RF-4C e o RB vão de face a face dos cantos (x 0,31 a 39,19 m).",
    "Cabeças 40 × 30 dos pilares de fachada (eixos B, C e D das linhas 1 e 9, 6 cabeças): a TP-40, a lã, a zipada e os painéis são recortados em volta da cabeça (42 × 16 cm, até 1 cm da face da cabeça) e o RF-4, o RF-4C e o RB são interrompidos nela; a cabeça leva o RF-4P — peça de 600 recortada e dobrada nas 3 faces, por cima da zipada e subindo 15 cm na cabeça, cantos rebitados e selados com PU (6 peças).",
    "Onde um PT-1 ou PT-2 da junta das placas fica na altura do RF-4 / RF-4C (linhas 1 e 9), a aba vertical do rufo é recortada 10 cm em volta da peça e selada com PU. Nos cantos de seção cheia o RF-1C tem 745 mm de desenvolvimento no topo (cobre a placa, a folga e os 60 cm do pilar) e o RF-2C / RF-3P vão só até a face lateral do pilar.",
    "Calha, descidas e extravasores: ND-LET-COB03. Terças e apoios: ND-LET-COB01. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."], 250)
av = pr.salvar("/home/claude/letsara/pranchas/ND-LET-COB04")
print("COB04", len([a for a in av if a[0] == "ERRO"]), "erros,", len(av), "avisos", [a for a in av if a[0] == "ERRO" or "sobrep" in a[1]][:16])
