"""ND-LET-CT02 — CORTES DO MEZANINO COM AS LAJES ALVEOLARES (rev executiva, 21/10/2026).

CORTE 4-4 (1:50): transversal no meio do vão das lajes (y = 4,825 m), olhando para a linha 2 — lajes LP20 + capa 5 cortadas
(alvéolos reais da seção do cálculo), VM da linha 2 ao fundo, pilares da linha 2, placas laterais H e J cortadas.
CORTE 5-5 (1:25): longitudinal entre os eixos B e C (x = 14,81 m), olhando para o eixo C — VM meio vaso cortadas nas linhas
1 e 2, laje no vão de 9,35 m, 2º estágio, capa, placas I (fachada) e G (parede interna) cortadas, pilares do eixo C ao fundo.
DETALHE 1 (1:10): laje alveolar sobre a VM de borda (linha 1), com 2º estágio, capa, fita de neoprene e alças.
Geometria dos mesmos JSON do cálculo (laje_alveolar, vm_meio_vaso, consolos, geometria, lajes_placas.paineis_mez). A0."""
import json, math, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from prancha_nd import Prancha, DIM_K, DIM_DLI
from geometria import Y_LIN, X_EIXO, PILARES_ESPECIAIS
from lajes_placas import paineis_mez
import pilar_generico as _G
import pecas_obra as QT                                     # peças = mesma fonte das listas (quantitativos.py)
import fechamento as FCH

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
LAJ = json.load(open(AQ + "laje_alveolar.json"))
SEC = LAJ["secao"]
VMJ = json.load(open(AQ + "vm_meio_vaso.json"))
VMP = VMJ["premissas"]
CMZ = json.load(open(AQ + "consolos.json"))["CP-MEZ"]
LG = json.load(open(AQ + "ligacoes.json"))
PQ = {p_[1]: p_ for p_ in QT.pecas}
f = lambda v, d=3: f"{v:+.{d}f}".replace(".", ",")
fd = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
M = lambda v: v * 1000

NIV = [3150.0, 6550.0]                                   # pisos acabados do mezanino
ASS = [float(z) for z in _G.Z_MEZ_ASS]                   # assentos dos CP-MEZ
H_LA, H_CP, FITA = SEC["h"] * 1000, 50.0, 10.0           # laje 200, capa 50, fita 10
HV = VMP["h_pm"] * 1000                                  # VM 800
BA, BB, HA = VMP["b_alma"] * 1000, VMP["b_aba"] * 1000, VMP["h_aba"] * 1000
BT = BA + BB                                             # 400
HCM = CMZ["h_total_m"] * 1000
PAI, QT_LA, L_P = paineis_mez()
R_AL, PAS = SEC["d_alveolo"] * 500, SEC["passo"] * 1000
X_NERV = SEC["x_nervuras_mm"]
B_LA = SEC["b"] * 1000
ZTV = [n - H_LA - H_CP - FITA for n in NIV]               # topo da aba da VM (= apoio da laje)
Y1, Y2 = M(Y_LIN[0]), M(Y_LIN[1])
XA = {k: M(v) for k, v in X_EIXO.items()}
LARG = XA["E"]
FACE = {"A": 300.0, "B": 200.0, "C": 200.0, "D": 200.0, "E": 300.0}
VM = []
nomes = list(XA)
for na, nb in zip(nomes[:-1], nomes[1:]):
    a_, b_ = XA[na] + FACE[na] + VMP["folga_m"] * 1000, XA[nb] - FACE[nb] - VMP["folga_m"] * 1000
    VM.append(("VM-01" if "A" in (na, nb) or "E" in (na, nb) else "VM-02", a_, b_))
PIL2 = [("PL-02", XA["A"], 600, 10000.0), ("PM-01", XA["B"], 400, NIV[1]), ("PC-01", XA["C"], 400, LG["Z_TOPO_I130"] * 1000),
        ("PM-01", XA["D"], 400, NIV[1]), ("PL-06", XA["E"], 600, 10000.0)]
O_PL = 375.0                                              # eixo das placas: face do pilar 30 + folga 2,5 + meia placa 5
Z_VIS = 7300.0                                            # vista interrompida acima do mezanino superior

pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="CORTES DO MEZANINO — LAJES ALVEOLARES LP20 + CAPA, VIGAS VM EM MEIO VASO, 2º ESTÁGIO E APOIOS",
                        desenho="ND-LET-CT02", folha="01/01", fase="EXECUTIVO", rev="00"))
pr.revisao("00", "21/10/2026", "EMISSÃO: CORTES 4-4 E 5-5 DO MEZANINO E DETALHE DO APOIO DA LAJE")
Q = pr.quadro


def nivel(v, x, z, txt, lado=1):
    k = v.esc
    v.linha((x, z), (x + lado * 14 * k, z), "COTA")
    v.poli([(x + lado * 5 * k - 1.2 * k, z + 2 * k), (x + lado * 5 * k + 1.2 * k, z + 2 * k), (x + lado * 5 * k, z)], "COTA", True)
    v.texto((x + lado * 7.5 * k, z + 0.6 * k), txt, "min", "BOTTOM_LEFT" if lado > 0 else "BOTTOM_RIGHT", "COTA")


def conc(v, pts, cam="CORTADO", esc=0.02):
    v.poli(pts, cam, True)
    if cam == "CORTADO":
        v.hachura(pts, "AR-CONC", esc)


def total(v, p1, p2, base, ang, loc):
    d = pr.msp.add_linear_dim(base=v.P(base), p1=v.P(p1), p2=v.P(p2), angle=ang, location=v.P(loc), dimstyle="ND",
                              override={"dimlfac": v.esc * v.fator, "dimdec": 1, "dimzin": 8, "dimtmove": 2}, dxfattribs={"layer": "COTA"})
    d.render(); v._add(d.dimension)


def secao_laje(v, x0, b, z0, mk):
    """seção transversal do painel (largura b, fundo em z0) com os alvéolos reais (LP20: passo 198, Ø152)."""
    v.poli([(x0, z0), (x0 + b, z0), (x0 + b, z0 + H_LA), (x0, z0 + H_LA)], "CORTADO", True)
    n_al = 6 if b > 1000 else 3
    xc = x0 + b / 2
    cs = [xc + (k - (n_al - 1) / 2) * PAS for k in range(n_al)]
    for c_ in cs:
        v.circulo((c_, z0 + H_LA / 2), R_AL, "CORTADO")
    pts = [(x0, z0), (x0 + b, z0), (x0 + b, z0 + H_LA), (x0, z0 + H_LA)]
    v.hachura(pts, "AR-CONC", 0.012)


# ================================================================== CORTE 4-4 — transversal, 1:50
E1 = 50
v = pr.vista("CORTE 4-4", (Q[0] + 70, Q[3] - 250), E1, titulo="CORTE 4-4 — MEZANINO, TRANSVERSAL NO MEIO DO VÃO DAS LAJES (y = 4,825 m)",
             subtitulo="olhando para a linha 2; lajes LP20 + capa 5 cortadas; VM-01/VM-02 da linha 2 e pilares ao fundo; placas H e J cortadas", unidade="cm")
v.linha((-1300, 0), (LARG + 1300, 0), "TERRENO")
for mk, x, b, zt in PIL2:                                  # pilares da linha 2 ao fundo (vista interrompida)
    ztop = min(zt, Z_VIS)
    bandas = [(z_ + FITA, z_ + FITA + H_LA + H_CP) for z_ in ZTV]          # a laje cortada fica na frente do pilar
    cortes_z = [0.0] + [c_ for bd in bandas for c_ in bd if c_ < ztop] + [ztop]
    for xx in (x - b / 2, x + b / 2):
        for za_, zb_ in zip(cortes_z[0::2], cortes_z[1::2]):
            v.linha((xx, za_), (xx, zb_), "VISTA")
    v.linha((x - b / 2, 0), (x + b / 2, 0), "VISTA")
    if not any(a_ - 1 <= ztop <= b_ + 1 for a_, b_ in bandas):
        v.linha((x - b / 2, ztop), (x + b / 2, ztop), "VISTA")
    if zt > Z_VIS:
        v.interrupcao((x - b / 2, Z_VIS), (x + b / 2, Z_VIS))
    v.texto((x + (b / 2 + 120 if x < LARG else -b / 2 - 120), 150), f"{mk} ao fundo", "min", "BOTTOM_LEFT" if x < LARG else "BOTTOM_RIGHT")
    for za in ASS:                                         # consolos CP-MEZ (faces B/D dos pilares, ocultos atrás da VM)
        for sg in ((1,) if x == 0 else (-1,) if x == LARG else (-1, 1)):
            xa_ = x + sg * b / 2
            v.poli([(xa_, za - HCM), (xa_ + sg * CMZ["proj_m"] * 1000, za - HCM), (xa_ + sg * CMZ["proj_m"] * 1000, za), (xa_, za)], "OCULTA", True)
for zt, za in zip(ZTV, ASS):
    for mk, xa, xb in VM:                                  # VM da linha 2 em vista: dente nas pontas (recorte 30 × 35)
        rc, ln = VMP["dente"]["recorte"] * 1000, VMP["dente"]["ln"] * 1000
        zb = zt - HV
        cont = [(xa + ln, zb), (xb - ln, zb), (xb - ln, zb + rc), (xb, zb + rc), (xb, zt), (xa, zt), (xa, zb + rc), (xa + ln, zb + rc)]
        v.poli(cont, "VISTA", True)
        v.linha((xa + ln, zt - HA), (xb - ln, zt - HA), "OCULTA")            # aba (lado de cá)
    for x0, b, mk in PAI:                                  # lajes cortadas (junta 1 cm entre painéis)
        secao_laje(v, x0 + 5, b - 10, zt + FITA, mk)
    cap = [(300, zt + FITA + H_LA), (LARG - 300, zt + FITA + H_LA), (LARG - 300, zt + FITA + H_LA + H_CP), (300, zt + FITA + H_LA + H_CP)]
    conc(v, cap, esc=0.012)
for xp, sg in ((-O_PL, -1), (LARG + O_PL, 1)):            # placas laterais H e J (eixos A e E, linhas 1–2) cortadas
    for k in range(8):
        if k in FCH.ESQ:
            continue
        z0, z1 = k * 1250 + 5, (k + 1) * 1250
        if z0 > Z_VIS:
            continue
        pts = [(xp - 50, z0), (xp + 50, z0), (xp + 50, min(z1, Z_VIS)), (xp - 50, min(z1, Z_VIS))]
        conc(v, pts, esc=0.012)
for nm, x in XA.items():
    v.linha((x, -1500), (x, Z_VIS + 600), "EIXO")
    v.circulo((x, -1950), 400, "BOLHA"); v.texto((x, -1950), nm, "sub", "MIDDLE_CENTER")
xs = list(XA.values())
v.cota_h(xs, 0, -16, total=False)
yt = -16 * DIM_K * E1 - DIM_DLI * E1
total(v, (0, 0), (LARG, 0), (0, yt), 0, (14800, yt))
v.cota_v([0, ASS[0], ZTV[0], NIV[0], ASS[1], ZTV[1], NIV[1]], -1100, -8, total=False)
for zt, n, za in zip(ZTV, NIV, ASS):
    nivel(v, LARG + 900, n, f"piso {f(n / 1000)}")
    nivel(v, LARG + 900, za, f"assento CP-MEZ {f(za / 1000)}")
nivel(v, LARG + 900, 0, "±0,000")
v.chamada((PAI[3][0] + PAI[3][1] / 2, ZTV[1] + FITA + H_LA + H_CP), (8, 12), "capa 5 cm C30 + tela Q138 (obra)")
v.chamada((PAI[4][0] + 600, ZTV[1] + FITA + H_LA / 2), (10, -18), f"LP20 {B_LA:.0f} × {H_LA:.0f}, 6 alvéolos Ø{2 * R_AL / 10:.1f}".replace(".", ","))
v.chamada((PAI[0][0] + 350, ZTV[0] + FITA + H_LA / 2), (12, -22), "LA-02 70 × 20 (borda, 3 alvéolos)")
v.chamada((12000, ZTV[0] - HV / 2), (8, -14), "VM-02 meio vaso 40 × 80 ao fundo (linha 2)")
v.chamada((XA["B"] + 200 + 175, ASS[0] - HCM / 2), (10, -12), f"CP-MEZ {CMZ['proj_m']*100:.0f} × {HCM/10:.0f} (oculto)")
v.chamada((-O_PL, 3 * 1250 + 650), (-34, 6), "placa H (10 cm)")
v.chamada((LARG + O_PL, 2 * 1250 + 600), (10, 10), "placa J 10 cm (cortada)")

# ================================================================== CORTE 5-5 — longitudinal, 1:25
E2 = 25
XC5 = 14810.0
w = pr.vista("CORTE 5-5", (Q[0] + 75, Q[3] - 622), E2, titulo="CORTE 5-5 — MEZANINO, LONGITUDINAL ENTRE OS EIXOS B E C (x = 14,81 m)",
             subtitulo="olhando para o eixo C; VM-02 meio vaso cortadas nas linhas 1 e 2; laje LP20 no vão; placas I (fachada) e G (parede interna) cortadas", unidade="cm")
w.linha((-900, 0), (Y2 + 900, 0), "TERRENO")
for y, mk, b in ((Y1, "PF-02", 600), (Y2, "PC-01", 600)):     # pilares do eixo C ao fundo (60 em y)
    w.poli([(y - b / 2, 0), (y + b / 2, 0), (y + b / 2, Z_VIS), (y - b / 2, Z_VIS)], "VISTA", True)
    w.interrupcao((y - b / 2, Z_VIS), (y + b / 2, Z_VIS))
    w.texto((y + (b / 2 + 80 if y == Y1 else -b / 2 - 80), 120), f"{mk} ao fundo (eixo C)", "min", "BOTTOM_LEFT" if y == Y1 else "BOTTOM_RIGHT")


def meio_vaso(yc, zt, so):
    """meio vaso cortado: alma 25 do lado externo (so = −1 na linha 1, +1 na linha 2), aba 15 × 20 para dentro."""
    ye = yc + so * BT / 2
    yw, yi = ye - so * BA, ye - so * BT
    pts = [(ye, zt - HV), (yw, zt - HV), (yw, zt - HA), (yi, zt - HA), (yi, zt), (ye, zt)]
    conc(w, pts, esc=0.03)
    yl = yw - so * 50                                       # ponta da laje: 5 cm da face da alma
    e2 = [(ye, zt), (yl, zt), (yl, zt + FITA + H_LA), (ye, zt + FITA + H_LA)]
    w.poli(e2, "VISTA", True); w.hachura(e2, "AR-CONC", 0.015)
    for k_ in (60, BA - 60):                                # alças N9 (vista lateral)
        yy = ye - so * k_
        w.linha((yy, zt - 150), (yy, zt + FITA + H_LA - 30), "ARMADURA")
    w.linha((ye - so * 60, zt + FITA + H_LA - 30), (ye - so * (BA - 60), zt + FITA + H_LA - 30), "ARMADURA")
    w.chapa(min(yl, yi), zt, abs(yi - yl), FITA, 0.08)       # fita de neoprene sob a laje
    return yl


for zt, n, za in zip(ZTV, NIV, ASS):
    yl1 = meio_vaso(Y1, zt, -1)
    yl2 = meio_vaso(Y2, zt, 1)
    zl = zt + FITA
    w.poli([(yl1, zl), (yl2, zl), (yl2, zl + H_LA), (yl1, zl + H_LA)], "VISTA", True)     # laje em vista longitudinal
    for zz in (H_LA / 2 - R_AL, H_LA / 2 + R_AL):          # alvéolo (oculto) com tampão de 20 cm nas pontas
        w.linha((yl1 + 200, zl + zz), (yl2 - 200, zl + zz), "OCULTA")
    for yy in (yl1 + 200, yl2 - 200):
        w.linha((yy, zl + H_LA / 2 - R_AL), (yy, zl + H_LA / 2 + R_AL), "OCULTA")
    w.linha((yl1 + 30, zl + 40), (yl2 - 30, zl + 40), "ARM_PROT")                        # cordoalha Ø12,7 a 4 cm do fundo
    cap = [(Y1 - BT / 2, zl + H_LA), (Y2 + BT / 2, zl + H_LA), (Y2 + BT / 2, zl + H_LA + H_CP), (Y1 - BT / 2, zl + H_LA + H_CP)]
    conc(w, cap, esc=0.015)
    w.linha((Y1 - BT / 2 + 30, zl + H_LA + 25), (Y2 + BT / 2 - 30, zl + H_LA + 25), "ARMADURA")   # tela Q138
    for y in (Y1, Y2):                                      # consolo CP-MEZ do pilar do eixo C (oculto atrás da VM)
        w.poli([(y - 200, za - HCM), (y + 200, za - HCM), (y + 200, za), (y - 200, za)], "OCULTA", True)
for yp, V in ((Y1 - O_PL, "I"), (Y2 + O_PL, "G")):         # placas cortadas: fachada I (linha 1) e parede G (linha 2)
    for k in range(8):
        if V == "I" and k in FCH.ESQ:
            continue
        if V == "G" and k > 5:
            continue
        z0, z1 = k * 1250 + 5, (k + 1) * 1250
        if z0 > Z_VIS:
            continue
        conc(w, [(yp - 50, z0), (yp + 50, z0), (yp + 50, min(z1, Z_VIS)), (yp - 50, min(z1, Z_VIS))], esc=0.012)
for y, nm in ((Y1, "1"), (Y2, "2")):
    w.linha((y, -1300), (y, Z_VIS + 400), "EIXO")
    w.circulo((y, -1700), 350, "BOLHA"); w.texto((y, -1700), nm, "sub", "MIDDLE_CENTER")
w.cota_h([Y1 - O_PL - 50, Y1 - BT / 2, Y1, Y1 + BT / 2], -300, -10, total=False)
w.cota_h([Y2 - BT / 2, Y2, Y2 + BT / 2, Y2 + O_PL + 50], -300, -10, total=False)
w.cota_h([Y1, Y2], -300, -22, total=False)
w.cota_h([yl1, yl2], NIV[1] + 250, 10, total=False)
w.cota_v([0, ZTV[0] - HV, ZTV[0], ZTV[0] + FITA + H_LA, NIV[0]], Y2 + 1150, 10, total=False)
w.cota_v([ZTV[1] - HV, ZTV[1], ZTV[1] + FITA + H_LA, NIV[1]], Y2 + 1150, 10, total=False)
for n, za in zip(NIV, ASS):
    nivel(w, Y1 - O_PL - 80, n, f"piso {f(n / 1000)}", -1)
    nivel(w, Y1 - O_PL - 80, za, f"assento {f(za / 1000)}", -1)
nivel(w, Y1 - O_PL - 80, 0, "±0,000", -1)
w.chamada((Y1 - 100, ZTV[0] - HV / 2), (20, -10), f"VM-02 meio vaso 40 × 80 protendida ({fd(PQ['VM-02'][7])} t)")
w.chamada((Y2 + 100, ZTV[0] - HV / 2), (-20, -10), "VM-02 (alma do lado da borda)")
w.chamada((4800, ZTV[0] + FITA + 40), (10, -14), f"7 Ø12,7 CP-190 RB, eixo a 4 cm do fundo (σpi {LAJ['sig_pi']:.0f} MPa)")
w.chamada((7400, ZTV[0] + FITA + H_LA / 2 + R_AL), (6, 14), "alvéolos tampados 20 cm nas pontas")
w.chamada((2000, NIV[0]), (-6, 12), "capa 5 C30 + tela Q138")
w.chamada((Y1 - 100, ZTV[1] + 120), (18, 18), "2º estágio C30 com a capa (obra)")
w.chamada((Y2 - 250, ZTV[1] + 5), (-12, 16), "fita de neoprene 10 × 50, apoio 10")
w.chamada((Y1 - O_PL, 2 * 1250 + 600), (-10, 10), "placa I (fachada da linha 1)")
w.chamada((Y2 + O_PL, 3 * 1250 + 600), (10, 10), "placa G (parede interna)")
w.marcador_corte if False else None

# ================================================================== DETALHE 1 — apoio da laje na VM de borda, 1:10
E3 = 10
d = pr.vista("DET1", (Q[0] + 655, Q[3] - 470), E3, titulo="DETALHE 1 — LAJE ALVEOLAR NA VM DE BORDA (LINHA 1)",
             subtitulo="seção da VM no meio do vão; linha 2 espelhada; 2º estágio e capa concretados juntos por quem executa a capa", unidade="cm")
zt0 = 0.0
pts = [(0, -HV), (BA, -HV), (BA, -HA), (BT, -HA), (BT, 0), (0, 0)]
conc(d, pts, esc=0.03)
d.interrupcao((0, -HV + 250), (BA, -HV + 250))
d.chapa(BA + 50, 0, BB - 50, FITA, 0.05)
xl = BA + 50
LV = 900.0
d.poli([(xl, FITA), (xl + LV, FITA), (xl + LV, FITA + H_LA), (xl, FITA + H_LA)], "CORTADO", True)
d.interrupcao((xl + LV, FITA), (xl + LV, FITA + H_LA))
NB = SEC["nervuras_mm"][0]                                                      # nervura de borda 51,5
x_al = [xl + NB + R_AL + k * PAS for k in range(4)]
for c_ in x_al:
    if c_ + R_AL < xl + LV:
        d.circulo((c_, FITA + H_LA / 2), R_AL, "CORTADO")
for xc_ in [c["x_mm"] for c in LAJ["cordoalhas"]]:                               # cordoalhas nas nervuras (posição do cálculo), eixo a 4 cm
    xn = xl + xc_ + B_LA / 2
    if xn < xl + LV - 20:
        d.circulo((xn, FITA + 40), 6.35, "ARM_PROT_SECAO")
e2 = [(0, 0), (xl, 0), (xl, FITA + H_LA), (0, FITA + H_LA)]
d.poli(e2, "VISTA", True); d.hachura(e2, "AR-CONC", 0.008)
cap = [(0, FITA + H_LA), (xl + LV, FITA + H_LA), (xl + LV, FITA + H_LA + H_CP), (0, FITA + H_LA + H_CP)]
d.poli(cap, "VISTA", True); d.hachura(cap, "AR-CONC", 0.008)
d.linha((25, FITA + H_LA + 25), (xl + LV - 20, FITA + H_LA + 25), "ARMADURA")       # tela Q138 a meia capa
d.poli([(40, -500), (40, FITA + H_LA - 25), (BA - 40, FITA + H_LA - 25), (BA - 40, -500)], "ARMADURA")   # alça N9
for xx in (40, BA - 40):
    d.circulo((xx, FITA + H_LA - 40), 6, "ARM_SECAO")
d.cota_h([0, BA, BA + 50, BT], -HV + 250, -10, total=False)
d.cota_h([xl, xl + NB, xl + NB + 2 * R_AL, xl + NB + PAS], FITA + H_LA + H_CP, 10, total=False)
d.cota_v([-HA, 0, FITA, FITA + H_LA, FITA + H_LA + H_CP], xl + LV + 80, 10, total=False)
d.cota_v([-HV + 250, -HA, 0], -60, -10, total=False)
d.chamada((BA + 100, FITA / 2), (30, -12), "fita de neoprene 10 × 50; apoio 10 cm")
d.chamada((BA / 2, FITA + H_LA / 2), (-14, 14), "2º estágio C30 (com a capa)")
d.chamada((BA - 40, -600), (-22, -12), "alças N9 Ø10 c/15 da alma (sobem até a capa)")
d.chamada((xl + 400, FITA + H_LA + 25), (12, 14), "tela Q138 a meia altura da capa")
d.chamada((xl + LAJ["cordoalhas"][4]["x_mm"] + B_LA / 2, FITA + 40), (8, -34), "cordoalha Ø12,7 (1 por nervura), eixo a 4 cm")
d.chamada((x_al[1], FITA + H_LA / 2 + R_AL), (10, 26), "LP20: alvéolos Ø15,2 no passo 19,8; nervura de borda 5,15")
d.chamada((BT - 60, -HA / 2), (16, -26), "aba 15 × 20 da VM (apoio da laje)")
nivel(d, xl + LV + 300, FITA + H_LA + H_CP, "piso (+3,150 / +6,550)")
nivel(d, xl + LV + 300, 0, "topo da VM (+2,890 / +6,290)")

# ------------------------------------------------------------------ 3D, quadro de níveis e notas
cb = pr.carimbo_bbox
pr.imagem(Q[2] - 180, cb[3] + 26, Q[2], cb[3] + 26 + 260, "/home/claude/letsara/pranchas/img_ct02/mez.png",
          titulo="3D — MEZANINO ENTRE OS EIXOS B E C", subtitulo="recorte do modelo da obra; lajes e 2º estágio transparentes")
xt, ytop = Q[2] - 180, Q[3] - 6
niv = [["Piso acabado do mezanino inferior / superior", f"{f(NIV[0] / 1000)} / {f(NIV[1] / 1000)}"],
       ["Topo da capa = piso (capa 5 cm C30)", f"{f(NIV[0] / 1000)} / {f(NIV[1] / 1000)}"],
       ["Fundo da laje (fita de neoprene 1 cm)", f"{f((ZTV[0] + FITA) / 1000)} / {f((ZTV[1] + FITA) / 1000)}"],
       ["Topo da aba da VM (apoio da laje)", f"{f(ZTV[0] / 1000)} / {f(ZTV[1] / 1000)}"],
       ["Assento dos consolos CP-MEZ", f"{f(ASS[0] / 1000)} / {f(ASS[1] / 1000)}"],
       ["Fundo da VM e dos consolos", f"{f((ZTV[0] - HV) / 1000)} / {f((ZTV[1] - HV) / 1000)}"]]
yy = pr.tabela(xt, ytop, "NÍVEIS DO MEZANINO (m)", ["ELEMENTO", "INFERIOR / SUPERIOR"], niv, [112, 68], h_lin=5.2)
notas = [f"Lajes alveolares LP20 {B_LA:.0f} × {H_LA:.0f} (6 alvéolos Ø15,2, passo 19,8) + capa 5 cm C30 com tela Q138, vão de cálculo 9,35 m, biapoiadas nas abas das VM; 7 Ø12,7 CP-190 RB por painel (uma por nervura), σpi {LAJ['sig_pi']:.0f} MPa ({LAJ['cordoalhas'][0]['F_macaco_kN']:.1f} kN por cordoalha); liberação com fckj ≥ {LAJ['fckj']:.0f} MPa (ND-LET-LA01).".replace(".", ","),
         "Cargas consideradas: peso próprio 2,80 kN/m², capa + rejunte 1,35 kN/m², revestimento 1,0 kN/m², sobrecarga 5,0 kN/m² (escritório); montagem sem escoramento com a capa fresca + 1,0 kN/m².",
         f"VM-01 e VM-02 em meio vaso 40 × 80 protendidas (alma 25 do lado da borda, aba 15 × 20 para dentro), dente Gerber 50 × 35 nos consolos CP-MEZ; topo da aba = apoio da laje (ND-LET-VM01).",
         "Apoio da laje 10 cm sobre fita de neoprene 10 × 50 contínua; ponta da laje a 5 cm da face da alma; alvéolos tampados 20 cm na fábrica; chavetas entre painéis grauteadas antes da capa.",
         "2º estágio sobre a alma das VM (largura 30, até o topo da laje) e capa concretados juntos, por quem executa a capa, depois de todo o nível montado; alças N9 Ø10 c/15 da alma ancoram o 2º estágio; negativas N11/N12 sobre os pilares (ND-LET-VM01) e N1 2 Ø10 sobre os apoios das lajes (ND-LET-LA01).",
         "Lajes içadas só por garra mecânica nas 2 pontas; montar as lajes só depois das cantoneiras antigiro CT-1/CT-1P das VM parafusadas nas buchas BR-3 (torção do meio vaso; sem solda). Lajes e vigas sem escoramento.",
         "Placas: H e J (laterais do anexo) e I (fachada da linha 1) por fora dos pilares; G (parede interna da linha 2) do lado do pavilhão; cada placa independente nos seus consoles (ND-LET-PP00).",
         "Sequência: ND-LET-MON02. Apoios como montados: ND-LET-CT04. Cotas em cm, níveis em m. Não medir no desenho.",
         "EMISSÃO EXECUTIVA — LIBERADO PARA PRODUÇÃO, ARMAÇÃO, CONCRETAGEM E MONTAGEM."]
pr.notas(xt, yy - 4, notas, 178)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-CT02")
for a in avisos:
    print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
