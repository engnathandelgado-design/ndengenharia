"""ND-LET-CT04 — CORTES DE MONTAGEM DAS VIGAS: cada apoio como montado (posição final), com neoprene, pinos, folgas e níveis.
Geometria lida dos mesmos JSON do cálculo (ligacoes, consolos, dentes, vm_meio_vaso, vb_geom). Concreto em cm, metálica em mm.
A0, detalhes 1:10 com o recorte 3D de cada apoio (modelo da obra)."""
import json, math, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from prancha_nd import Prancha
import vb_geom as VG

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
LG = json.load(open(AQ + "ligacoes.json"))
CO = json.load(open(AQ + "consolos.json"))
DT = json.load(open(AQ + "dentes.json"))["I130"]["geometria"]
VMP = json.load(open(AQ + "vm_meio_vaso.json"))["premissas"]
f = lambda v, d=3: f"{v:+.{d}f}".replace(".", ",")
I3 = 0.03
C3 = 1 / math.sqrt(1 + I3 * I3)
Z0 = LG["Z0_TS"] * 1000
zf = lambda x: Z0 + I3 * x                      # fundo da TS-01 (x global, mm)
HV = 900 / C3

pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="CORTES DE MONTAGEM DAS VIGAS — APOIOS COMO MONTADOS (TS-01, I130, VM, VB, LAJE ALVEOLAR)",
                        desenho="ND-LET-CT04", folha="01/01", fase="PARA APROVAÇÃO", rev="07"))
pr.revisao("07", "21/10/2026", "EMISSÃO: CORTES DE MONTAGEM DE CADA APOIO (ANTES NOS DETALHES DA LOC01/CT01)")
Q = pr.quadro


def nivel(v, x, z, txt, lado=1):
    k = v.esc
    v.linha((x, z), (x + lado * 18 * k, z), "COTA")
    v.poli([(x + lado * 6 * k - 1.2 * k, z + 2 * k), (x + lado * 6 * k + 1.2 * k, z + 2 * k), (x + lado * 6 * k, z)], "COTA", True)
    v.texto((x + lado * 8.5 * k, z + 0.6 * k), txt, "min", "BOTTOM_LEFT" if lado > 0 else "BOTTOM_RIGHT", "COTA")


def conc(v, pts, cam="CORTADO"):
    v.poli(pts, cam, True)
    if cam == "CORTADO":
        v.hachura(pts, "AR-CONC", 0.02)


def neo(v, x0, z0, w, h):
    v.chapa(x0, z0, w, h, 0.15)


def pino(v, x, z0, z1, d):
    v.ret(x - d / 2, z0, d, z1 - z0, "METALICA")


CELL = [(Q[0] + 5, Q[3] - 10), (Q[0] + 325, Q[3] - 10), (Q[0] + 645, Q[3] - 10),
        (Q[0] + 5, Q[3] - 330), (Q[0] + 325, Q[3] - 330), (Q[0] + 645, Q[3] - 330)]
IMG = ["a1", "a2", "a3", "a4", "a5", "a6"]
LEG = ["TS-01 no recuo do pilar lateral", "duas TS-01 no topo da I130", "I130 no consolo CP-I130", "VM no consolo CP-MEZ", "VB no consolo CP-VB", "laje alveolar na VM de borda"]


def org(i, xr, zr, esc=20, dx=75, dz=210):
    cx, cy = CELL[i]
    return (cx + dx - xr / esc, cy - dz - zr / esc)


def foto(i):
    from PIL import Image, ImageOps
    src = f"/home/claude/letsara/pranchas/img_ct04/{IMG[i]}.png"
    im = Image.open(src).convert("RGB")
    bb = ImageOps.invert(im).getbbox()
    im.crop(bb).save(src.replace(".png", "_c.png"))
    cx, cy = CELL[i]
    pr.imagem(cx + 210, cy - 215, cx + 315, cy - 25, src.replace(".png", "_c.png"), titulo=f"3D — {LEG[i]}", subtitulo="recorte do modelo da obra")


# ------------------------------------------------------------------ 1. TS-01 no recuo do pilar lateral (eixo A)
REC = LG["REC"][0] * 1000
d = pr.vista("DET1", org(0, 0, REC, esc=10, dx=75, dz=160), 10, titulo="1 — TS-01 NO RECUO DO PILAR LATERAL (EIXO A)",
             subtitulo="vista na direção 1–9; ponta a prumo, cunha de apoio horizontal", unidade="cm")
zb = REC - 900
ZC1 = REC + 1400
conc(d, [(-300, zb), (300, zb), (300, REC), (0, REC), (0, ZC1), (-300, ZC1)])
d.interrupcao((-300, ZC1), (0, ZC1))
xa, CUN = LG["X_PONTA_ESQ"] * 1000, LG["CUNHA"] * 1000
zap = REC + 10
xe = xa + 1000
d.poli([(xa, zap), (xa + CUN, zap), (xe, zf(xe)), (xe, zf(xe) + HV), (xa, zf(xa) + HV)], "VISTA", True)
d.interrupcao((xe, zf(xe)), (xe, zf(xe) + HV))
for z_ in (150, HV - 120):
    d.linha((xa + 500, zf(xa + 500) + z_), (xe, zf(xe) + z_), "OCULTA")
x_neo = LG["apoios_ts"]["P1"]["x_neo"] * 1000
neo(d, x_neo - 100, REC, 200, 10)
xp = xa + LG["PINO_TS"] * 1000
pino(d, xp, REC - 300, REC + 300, 25)
d.ret(xp - 25, zap, 50, HV - 10, "OCULTA")
d.ret(-300 - 25 - 100, zb, 100, ZC1 - zb, "VISTA")
d.cota_h([-425, -325], zb, -8, total=False)
d.cota_h([-300, 0, x_neo, xa + 275], zb, -8, total=False)
d.chamada((xa / 2, zap + 700), (12, 10), f"folga {xa / 10:.1f}".replace(".", ",") + " (cabeça do pilar × ponta da TS-01)")
d.cota_v([REC, zap, zf(xa) + HV], xe + 200, 8, total=False)
nivel(d, -425, REC, f"assento {f(REC / 1000)}", -1)
d.chamada((x_neo, REC + 5), (16, -14), "NEO-4 200×300×10 (apoio 27,5)")
d.chamada((xp, REC - 200), (24, -8), "2 PN-3 Ø25 L=600 (300 no pilar), graute no TB-3")
d.chamada((xp, zap + 600), (14, 10), "TB-3 Ø50 na viga, a prumo")
d.chamada((-150, REC + 1200), (21, 10), "cabeça 40×30 até +10,00")
d.chamada((-375, zb + 300), (8, -14), "placa 10 (folga 2,5)")

# ------------------------------------------------------------------ 2. TS-01 no topo da I130 (eixo C)
ZT = LG["Z_TOPO_I130"] * 1000
d = pr.vista("DET2", org(1, 0, ZT, esc=10, dx=105, dz=110), 10, titulo="2 — DUAS TS-01 NO TOPO DA I130 / PILAR CENTRAL (EIXO C)",
             subtitulo="topo em 2 níveis (lado E 12 mm mais alto); NEO-3 + 2 PN-5 por TS-01", unidade="cm")
sec = [(-200, 0), (200, 0), (200, 250), (75, 330), (75, 1000), (200, 1080), (200, 1300), (-200, 1300), (-200, 1080), (-75, 1000), (-75, 330), (-200, 250)]
zbI = ZT - 1300
pts = [(x, zbI + y) for x, y in sec]
d.poli(pts, "VISTA", True)
dg = LG["DEGRAU_C"] * 1000
d.ret(0, ZT, 200, dg, "VISTA")
d.interrupcao((-200, zbI + 300), (200, zbI + 300))
for sg in (-1, 1):
    za_ = ZT + (dg if sg > 0 else 0)
    xs = sg * 37.5
    xb = sg * 700
    zfb = za_ + 10 + sg * I3 * (abs(xb) - 37.5 - CUN)
    d.poli([(xs, za_ + 10), (xs + sg * CUN, za_ + 10), (xb, zfb), (xb, zfb + HV), (xs, za_ + 10 + HV)], "VISTA", True)
    d.interrupcao((xb, zfb), (xb, zfb + HV))
    neo(d, sg * 115 - 50, za_, 100, 10)
    pino(d, sg * 115, za_ - 300, za_ + 300, 20)
d.cota_h([-200, -115, -37.5, 37.5, 115, 200], ZT, 8, total=False)
nivel(d, -700, ZT, f"topo I130 {f(ZT / 1000)} (lado A)", -1)
nivel(d, 700, ZT + dg, f"{f((ZT + dg) / 1000)} (lado E)", 1)
d.chamada((-115, ZT + 5), (-18, -16), "NEO-3 100×300×10 (apoio 16,25)")
d.chamada((115, ZT - 200), (16, -16), "2 PN-5 Ø20 L=600 por TS-01")
d.chamada((0, ZT + 400), (4, 18), "folga 7,5 entre as pontas")

# ------------------------------------------------------------------ 3. I130 no consolo CP-I130
ZA = LG["Z_ASS_I130"] * 1000
cp = CO["CP-I130"]
hcp, pcp = cp["h_total_m"] * 1000, cp["proj_m"] * 1000
hd, ln = DT["hd"], DT["ln"]
d = pr.vista("DET3", org(2, 0, ZA, esc=10, dx=55, dz=120), 10, titulo="3 — I130 NO CONSOLO CP-I130 (P8A / P11 / P13 / P14)",
             subtitulo="vista na direção A–E; dente 78 × 35, fundo do consolo = fundo da viga", unidade="cm")
zbv = ZT - 1300
conc(d, [(-450, zbv - 300), (0, zbv - 300), (0, ZT + 200), (-450, ZT + 200)])
d.interrupcao((-450, zbv - 300), (-450, ZT + 200))
conc(d, [(0, ZA - hcp), (pcp, ZA - hcp), (pcp, ZA), (0, ZA)])
u0 = 75
d.poli([(u0, ZT - hd), (u0 + ln, ZT - hd), (u0 + ln, zbv), (u0 + 1100, zbv), (u0 + 1100, ZT), (u0, ZT)], "VISTA", True)
d.interrupcao((u0 + 1100, zbv), (u0 + 1100, ZT))
neo(d, 100, ZA, 200, 31)
pino(d, 200, ZA - 350, ZA + 550, 25)
d.cota_h([0, u0, 200, u0 + ln, pcp], zbv, -8, total=False)
d.cota_v([zbv, ZA, ZA + 31, ZT], u0 + 1100, 8, total=False)
nivel(d, 0, ZA, f"assento {f(ZA / 1000)}", -1)
nivel(d, u0 + 1100, ZT + 0, f"topo {f(ZT / 1000)}", 1)
d.chamada((200, ZA + 15), (14, 10), "NEO-2 300×200×31 fretado")
d.chamada((200, ZA + 500), (14, 14), "PN-2 Ø25 L=900 (350 no consolo); graute numa ponta só")
d.chamada((u0 + 800, zbv + 150), (-6, -22), "ponta maciça 1,40 m")
d.chamada((u0 / 2, ZA + 400), (-14, 14), "folga 7,5")

# ------------------------------------------------------------------ 4. VM no CP-MEZ
H_V, HDV, LNV, RCV = VMP["h_pm"] * 1000, VMP["dente"]["hd"] * 1000, VMP["dente"]["ln"] * 1000, VMP["dente"]["recorte"] * 1000
cm = CO["CP-MEZ"]
hcm, pcm = cm["h_total_m"] * 1000, cm["proj_m"] * 1000
ZN = 3150
ZTV = ZN - 260
ZAV = ZTV - HDV - 10
zbv = ZTV - H_V
d = pr.vista("DET4", org(3, 0, ZAV, esc=10, dx=50, dz=125), 10, titulo="4 — VM (MEIO VASO) NO CONSOLO CP-MEZ",
             subtitulo="vista na direção A–E; nível +3,15 (o +6,55 é igual); junta de 3 cm grauteada", unidade="cm")
conc(d, [(-400, zbv - 300), (0, zbv - 300), (0, ZN + 300), (-400, ZN + 300)])
d.interrupcao((-400, zbv - 300), (-400, ZN + 300))
conc(d, [(0, ZAV - hcm), (pcm, ZAV - hcm), (pcm, ZAV), (0, ZAV)])
u0 = VMP["folga_m"] * 1000
d.poli([(u0, ZAV + 10), (u0 + LNV, ZAV + 10), (u0 + LNV, zbv), (u0 + 1200, zbv), (u0 + 1200, ZTV), (u0, ZTV)], "VISTA", True)
d.interrupcao((u0 + 1200, zbv), (u0 + 1200, ZTV))
gr = [(0, ZAV + 10), (u0, ZAV + 10), (u0, ZTV), (0, ZTV)]
d.poli(gr, "VISTA", True); d.hachura(gr, "AR-CONC", 0.01)
xpd = VMP["x_pad"] * 1000
neo(d, xpd - 75, ZAV, 150, 10)
pino(d, xpd, ZAV - 300, ZAV + 400, 20)
d.chapa(u0 + 20, ZTV - 152, 102, 12.5, 0.1)
d.ret(0, ZTV + 10, u0 + 1200, 200, "OCULTA")
d.ret(-400, ZTV + 210, u0 + 1600, 50, "VISTA")
d.cota_h([0, u0, xpd, u0 + LNV, pcm], zbv, -8, total=False)
d.cota_v([zbv, ZAV, ZAV + 10, ZTV, ZTV + 210, ZN], u0 + 1250, 8, total=False)
nivel(d, 0, ZAV, f"assento {f(ZAV / 1000)}", -1)
nivel(d, u0 + 1200, ZN, f"piso {f(ZN / 1000)}", 1)
d.chamada((xpd, ZAV + 200), (14, 8), "NEO-5 300×150×10 + PN-1 Ø20 L=700 (300 no consolo)")
d.chamada((u0 + 70, ZTV - 140), (16, 6), "CT-1 L152×102×12,5 antigiro (bucha M16 no pilar)")
d.chamada((u0 / 2, ZTV - 200), (-14, 12), "junta 3 grauteada")
d.chamada((u0 + 900, ZTV + 235), (6, 10), "laje h20 + capa 5")

# ------------------------------------------------------------------ 5. VB no CP-VB
cv = CO["CP-VB"]
d = pr.vista("DET5", org(4, 0, 300, esc=10, dx=50, dz=150), 10, titulo="5 — VB 15×60 NO CONSOLO CP-VB (FACHADAS 1 E 9)",
             subtitulo="vista na direção 1–9; ponta baixa; face de apoio e topo do consolo horizontais", unidade="cm")
Lh = 1100
cont = VG.montada(9300)
zr = cont[0][1]
pts = [(25 + x, z) for x, z in cont if x <= Lh] 
vb = [(25 + 0, zr), (25 + VG.LN, zr), (25 + VG.LN, VG.I * VG.LN), (25 + Lh, VG.I * Lh), (25 + Lh, VG.I * Lh + VG.H / VG.C), (25, VG.H / VG.C)]
d.poli(vb, "VISTA", True)
d.interrupcao((25 + Lh, VG.I * Lh), (25 + Lh, VG.I * Lh + VG.H / VG.C))
zcv = zr - 10
conc(d, [(0, zcv - cv["h_total_m"] * 1000), (cv["proj_m"] * 1000, zcv - cv["h_total_m"] * 1000), (cv["proj_m"] * 1000, zcv), (0, zcv)])
conc(d, [(-400, -400), (0, -400), (0, 1000), (-400, 1000)])
d.interrupcao((-400, -400), (-400, 1000))
xb_ = 25 + VG.XP
neo(d, xb_ - 50, zcv, 100, 10)
pino(d, xb_, zcv - 300, zcv + 400, 20)
d.ret(xb_ - 60, VG.H / VG.C - 60 + I3 * xb_, 120, 60, "OCULTA")
d.cota_h([0, xb_, 25 + VG.LN, cv["proj_m"] * 1000], -400, -8, total=False)
d.chamada((xb_, zcv + 5), (16, -14), "NEO-6 100×100×10")
d.chamada((xb_, zcv + 350), (16, 14), "PN-6 Ø20 roscado L=700 + porca e contraporca")
d.chamada((xb_, VG.H / VG.C - 30), (14, 10), "nicho 12×12×6 grauteado só numa ponta")
d.chamada((12, zr + 100), (-14, 10), "folga 2,5")

# ------------------------------------------------------------------ 6. laje alveolar sobre a VM (seção transversal da VM, 1:10)
ba, bb, ha = VMP["b_alma"] * 1000, VMP["b_aba"] * 1000, VMP["h_aba"] * 1000
d = pr.vista("DET6", org(5, 0, 0, esc=10, dx=60, dz=110), 10, titulo="6 — LAJE ALVEOLAR NA VM DE BORDA (SEÇÃO)",
             subtitulo="meio vaso: alma 25 no lado da borda, aba 15 × 20; 2º estágio e capa por quem faz a capa", unidade="cm")
bt = ba + bb
conc(d, [(0, -H_V), (ba, -H_V), (ba, -ha), (bt, -ha), (bt, 0), (0, 0)])
d.interrupcao((0, -500), (ba, -500))
fita = [(ba + 50, 0), (bt, 0), (bt, 10), (ba + 50, 10)]
d.chapa(ba + 50, 0, bb - 50, 10, 0.05)
d.ret(ba + 50, 10, 500, 200, "VISTA")
d.interrupcao((ba + 550, 10), (ba + 550, 210))
LAJ = json.load(open(AQ + "laje_alveolar.json"))["secao"]                 # LP20: borda 51,5, alvéolos Ø152 no passo 198
_r, _p = LAJ["d_alveolo"] * 500, LAJ["passo"] * 1000
_x1 = LAJ["nervuras_mm"][0] + _r
for k in range(2):
    d.circulo((ba + 50 + _x1 + k * _p, 100), _r, "VISTA")
e2 = [(0, 0), (ba + 50, 0), (ba + 50, 210), (0, 210)]
d.poli(e2, "OCULTA", True); d.hachura(e2, "AR-CONC", 0.01)
d.ret(0, 210, ba + 550, 50, "VISTA")
d.poli([(40, -60), (40, 180), (ba - 40, 180), (ba - 40, -60)], "ARMADURA")
d.cota_h([0, ba, ba + 50, bt], -H_V, -8, total=False)
d.cota_v([-H_V, -ha, 0, 10, 210, 260], -150, -8, total=False)
d.chamada((ba + 100, 5), (14, -16), "fita de neoprene 1 cm; apoio 10")
d.chamada((ba / 2, 100), (-12, 16), "2º estágio C30 (com a capa)")
d.chamada((ba - 40, 150), (16, 22), "alças N9 Ø10 c/15 da alma")
d.chamada((ba + 400, 235), (8, 12), "capa 5 C30 + tela Q138")
d.chamada((ba + 50 + _x1 + _p, 100 + _r), (10, 22), "LP20 1245 × 200, 6 alvéolos Ø15,2, 7 Ø12,7")

for i_ in range(6):
    foto(i_)
notas = ["Apoios desenhados na posição montada, com as folgas reais (NBR 9062:2017 3.1): TS-01 2,5 cm da cabeça do pilar e 7,5 cm entre pontas no eixo C; I130 7,5 cm; VM 3 cm (junta grauteada); VB 2,5 cm.",
         "Neoprenes: NEO-2 fretado 300×200×31 (I130); NEO-3 100×300×10 e NEO-4 200×300×10 (TS-01); NEO-5 300×150×10 (VM); NEO-6 100×100×10 (VB); fita 1 cm sob a laje alveolar.",
         "Pinos: grautear o tubo/nicho só depois do alinhamento e do nível conferidos; nas I130 e VB, graute numa ponta só (a outra livre para dilatar).",
         "VM: parafusar as 2 cantoneiras CT-1 nas buchas rosqueadas M16 embutidas no pilar antes de soltar a viga do guindaste (torção de montagem do meio vaso). Lajes só depois das CT-1.",
         "Tolerâncias de montagem (NBR 9062:2017 5.2.2.6): nível dos apoios ±1,0 cm; apoio da laje ≥ 10 cm medido depois de montada.",
         "Imagens 3D: recortes do modelo da obra (concreto das vigas transparente para mostrar neoprene e pinos).",
         "Sequência completa: ND-LET-MON01 (pilares, vigas e cobertura), MON02 (mezanino) e MON03 (fechamento e sequência geral). Cotas em cm, níveis em m.",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(Q[2] - 180, Q[3] - 6, notas, 178)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-CT04")
for a in avisos:
    if a[0] == "ERRO" or "sobrep" in a[1] or "sai" in a[1]:
        print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
