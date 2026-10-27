import sys; sys.path.insert(0, "/home/claude/letsara/pranchas"); import renomear as RN
"""ND-LET-VM01 rev09 (23/10/2026, DEC-047/048) — vigas do mezanino VM-01 a VM-04 RETANGULARES PROTENDIDAS 30 × 75 com 2º
estágio (decisão do Nathan: sem meio vaso; laje alveolar apoiada 10 cm no topo da viga, alças para o 2º estágio na faixa
restante, concretado com a capa) e dente Gerber 45 × 40 nas pontas (fundo do consolo CP-MEZ alinhado ao fundo da viga).
Fôrma, 2º estágio, apoio, ponta concretada (trava de montagem), insertos, protensão (posição e força no macaco) e notas da
NBR 9062:2017 5.6.1.2. Armação: faixa de baixo (vigas_exec + armaduras_vigas.spec_vm). Cálculo: calc_vm_retangular.py,
mef_vm_ret_dente.py, calc_nbr9062.py. Concreto em cm, chaparia em mm."""
import json, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha
AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
sys.path.insert(0, AQ)
from geometria import X_EIXO, Y_LIN, Z_PISOS

f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
VMJ = json.load(open(AQ + "vm_retangular.json"))
N9 = json.load(open(AQ + "nbr9062.json"))
CM = json.load(open(AQ + "cargas_mezanino.json"))
R = VMJ["VM-02"]
P = VMJ["premissas"]
H, B = round(P["h_pm"] * 1000), round(P["b"] * 1000)
B2 = B - 120                                  # faixa de 2º estágio sobre a viga (b − apoio 100 − folga 20)
HD, LN, MAC = round(P["dente"]["hd"] * 1000), round(P["dente"]["ln"] * 1000), round(P["dente"]["macico"] * 1000)
REC = H - HD
FOLGA, X_PAD, A_PAD = 30, round(P["x_pad"] * 1000), 200
HC, PROJ = round(P["dente"]["consolo_h"] * 1000), round(P["dente"]["consolo_proj"] * 1000)
H2, HCAPA, NEOF = 200, 50, 10
L = round(R["L_peca"] * 1000)
X_TB = X_PAD - FOLGA
Z_PISO = tuple(round(z * 1000) for z in Z_PISOS)
ZB = [z - HCAPA - H2 - NEOF - H for z in Z_PISO]
CORD = R["pos_cordoalhas_mm"]
F_MAC = R["protensao"]["F_macaco_kN"]
MKS = ("VM-01", "VM-02", "VM-03", "VM-04")
QT = {"VM-01": 6, "VM-02": 8, "VM-03": 2, "VM-04": 2}
POS = {"VM-01": "A–B e D–E da linha 1; A–B da linha 2 (2 níveis)", "VM-02": "B–C e C–D das linhas 1 e 2 (2 níveis)",
       "VM-03": "linha 2, D → P6 (2 níveis)", "VM-04": "linha 2, P6 → E (+7,30); escada, P6 → P7 (+3,90)"}
PESO, V_TOT = VMJ["VM-02"]["peso_t"], VMJ["VM-02"]["V_m3"]

pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="VIGAS DO MEZANINO VM-01 A VM-04 — RETANGULAR PROTENDIDA 30 × 75 COM DENTE GERBER — FÔRMA, 2º ESTÁGIO, APOIO E INSERTOS",
                        desenho="ND-LET-VM01", folha="01/01", fase="PARA APROVAÇÃO", marca="VM-02", qtd=8, peso=f(PESO, 2), volume=f(V_TOT, 2)))
pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL (I90 COM DENTE)")
pr.revisao("04", "16/10/2026", "NBR 9062: MEIO VASO COM DENTE; 2º ESTÁGIO E ALÇAS")
pr.revisao("06", "19/10/2026", "DEC-032: PERDAS 9.6.3 E γp 1,1 NO ATO; DENTE VERIFICADO POR MEF; LIBERAÇÃO GRADUAL")
pr.revisao("09", "23/10/2026", f"DEC-045/047/048/049: PISOS +3,90 / +7,30; VIGA RETANGULAR {B/10:g} × {H/10:g} (SEM MEIO VASO); VM-03 E VM-04 (ESCADA)")
pr.revisao("", "24/10/2026", "DEC-052: +7,30 DA LINHA 2 COM O MONTANTE DA COBERTURA NO MEIO DO VÃO (VM-01, VM-02, VM-03); ESPERA EM-L2 NO 2º ESTÁGIO; PEÇA SEM MUDANÇA")
pr.revisao("", "25/10/2026", "DEC-062: COTAS DO DENTE NO DETALHE D1 (COMPRIMENTO, ALTURA E RECORTE)")
Q = pr.quadro
XC = Q[2] - 200
todos = [n for mk in MKS for n in RN.nomes_de(mk)]
pr.cabecalho_peca("\x01" + RN.lista(todos), f"VIGA DO MEZANINO — RETANGULAR PROTENDIDA {B/10:g} × {H/10:g} cm (+ 2º ESTÁGIO 26 cm) — VM-02 L = {L/10:g} cm".replace(".", ","),
                  f"linhas 1 e 2 e escada, pisos (topo da capa) +3,90 e +7,30; fundo da viga e do consolo +{f(ZB[0]/1000, 2)} / +{f(ZB[1]/1000, 2)}; "
                  f"laje apoiada 10 cm no topo, 2º estágio de {B2/10:g} cm do lado da borda   ·   PESO VM-02 {f(PESO, 2)} t   ·   C40, {len(CORD)} Ø12,7 CP-190 RB na VM-02", largura=XC - Q[0] - 12)

# ------------------------------------------------------------------ planta-chave
M = lambda v: v * 1000
import chave as CH


def _rot_vm(n):
    p = CH._P[n]
    xm_, y_ = (p["x0"] + p["x1"]) / 2, p["y0"]
    ns = [RN.viga_em(nv, xm_, y_, tol=0.3) for nv in ("+3,90", "+7,30")]
    return " / ".join(x for x in ns if x)


kp = CH.planta(pr, (XC - 160, Q[3] - 100), 400, todos, subtitulo="VM das linhas 1 e 2 e da escada: nome no +3,90 / no +7,30", y_max=Y_LIN[2], rotulo=_rot_vm)

# ------------------------------------------------------------------ ELEVAÇÃO DE FÔRMA
ESC = 15
Y_EL = Q[3] - 125
ve = pr.vista("ELEVAÇÃO", (Q[0] + 40, Y_EL), ESC, titulo="ELEVAÇÃO DE FÔRMA — VM-02 (vista do lado da laje)",
              subtitulo=f"seção retangular {B/10:g} × {H/10:g}; dente {HD/10:g} × {LN/10:g} nas pontas; alças N9 saindo 20 cm em toda a viga", unidade="cm")
ve.poli([(0, REC), (LN, REC), (LN, 0), (L - LN, 0), (L - LN, REC), (L, REC), (L, H), (0, H)], "VISTA", fechada=True)
for x in range(150, L - 100, 150):
    ve.linha((x, H), (x, H + 200), "ARM_TRANSV")
for x in (X_TB, L - X_TB):
    ve.ret(x - 25, REC, 50, HD, "OCULTA")
for x in (1100, L - 1100):
    ve.poli([(x - 60, H), (x - 60, H + 90), (x, H + 130), (x + 60, H + 90), (x + 60, H)], "METALICA")
ve.cota_h([0, LN, L / 2, L - LN, L], 0, -12)
ve.cota_v([0, REC, H, H + 200], L, 12, total=False)
ve.cota_ord([0, X_TB, 1100, L - 1100, L - X_TB, L], H + 200, 12, x0=0)
ve.chamada((LN, REC / 2), (10, -14), f"recorte {REC/10:g} × {LN/10:g}")
ve.chamada((X_TB, REC + HD / 2), (10, -(REC + HD / 2) / ESC - 22), "TB-1 (2x)")
ve.chamada((L - 1100, H + 120), (10, 10), "AL-1 laço Ø12,7 (2x)")
ve.chamada((L / 2 + 75, H + 200), (8, 12), "N9 alças Ø10 c/15 (20 cm acima da peça)")
ve.marcador_corte((L / 2 - 600, -18 * ESC), (L / 2 - 600, H + 30 * ESC), "A", lado=1)
ve.marcador_corte((300, -18 * ESC), (200, H + 30 * ESC), "B", lado=1)
ve.marcador_detalhe((LN / 2, H / 2), 650, 1, ang=-150, dist=8)

# ------------------------------------------------------------------ CORTE A-A — seção corrente + 2º estágio + laje + capa
YR = Y_EL - 300
ca = pr.vista("CORTE A-A", (Q[0] + 95, YR), 5, titulo="CORTE A-A — SEÇÃO CORRENTE E 2º ESTÁGIO",
              subtitulo="pré-moldado (hachura) + 2º estágio e capa de obra (tracejado) + laje alveolar apoiada no topo", unidade="cm")
sec = [(0, 0), (B, 0), (B, H), (0, H)]
ca.poli(sec, "CORTADO", fechada=True); ca.hachura(sec, "AR-CONC", 0.03)
e2 = [(0, H), (B2, H), (B2, H + NEOF + H2), (0, H + NEOF + H2)]
ca.poli(e2, "OCULTA", fechada=True); ca.hachura(e2, "ANSI31", 0.6)
LAJ = 900
ca.poli([(B - 100, H + NEOF), (LAJ, H + NEOF), (LAJ, H + NEOF + H2), (B - 100, H + NEOF + H2)], "VISTA", fechada=True)
for xc in (B - 100 + 110, B - 100 + 320, B - 100 + 530):
    if xc + 76 < LAJ:
        ca.circulo((xc, H + NEOF + H2 / 2), 76, "VISTA")
ca.interrupcao((LAJ, H + NEOF - 20), (LAJ, H + NEOF + H2 + HCAPA + 20))
ca.ret(B - 100, H, 100, NEOF, "METALICA")
capa = [(0, H + NEOF + H2), (LAJ, H + NEOF + H2), (LAJ, H + NEOF + H2 + HCAPA), (0, H + NEOF + H2 + HCAPA)]
ca.poli(capa, "OCULTA", fechada=True); ca.hachura(capa, "ANSI31", 0.6)
ca.ret(25, 25, B - 50, H - 50, "ARM_TRANSV")                                  # estribo fechado N2 (armadura na faixa de baixo)
for x in (35, B2 - 15):                                                         # alça N9 do 2º estágio (dentro do estribo)
    ca.linha((x, H - 120), (x, H + 200), "ARM_TRANSV")
ca.linha((35, H - 120), (B2 - 15, H - 120), "ARM_TRANSV")
for x, y in CORD:
    ca.circulo((x, y), 6.35, "ARM_PROT_SECAO")
ca.cota_h([0, B2, B - 100, B], 0, -10, total=True)
ca.cota_v(sorted({0} | {c[1] for c in CORD[:-2]} | {H, H + NEOF + H2, H + NEOF + H2 + HCAPA}), -60, -10, total=False)
ca.chamada((B / 2, H / 3), (-54, -6), f"VM {B/10:g} × {H/10:g} protendida (pré-moldada)")
ca.chamada((B - 50, H + NEOF / 2), (16, 6), "apoio da laje 10 cm + neoprene em fita 10")
ca.chamada((60, H + 150), (30, 46), f"2º ESTÁGIO C30 (obra, com a capa), faixa de {B2/10:g} cm")
ca.chamada((LAJ - 150, H + NEOF + H2 + HCAPA), (8, 10), "capa 5 cm C30 + tela (obra)")
ca.chamada((LAJ - 120, H + NEOF + H2 / 2), (34, -30), "laje alveolar h20")
ca.chamada((B2 - 15, H + 160), (10, 24), "N9 Ø10 c/15 (alça)")
_lin = sorted({c[1] for c in CORD})
_xd = {yy: max(c[0] for c in CORD if c[1] == yy) for yy in _lin}
_n0, _ni = sum(1 for c in CORD if c[1] == _lin[0]), R["isoladas_pontas"]
_rt = {_lin[0]: f"C1 ({_ni}, isoladas 150) + C2 ({_n0 - _ni}) Ø12,7"}          # rev12: quantidades do registro (antes C2 fixo em 2)
for k_, yy in enumerate(_lin[1:]):
    _rt[yy] = f"C{k_ + 3} ({sum(1 for c in CORD if c[1] == yy)}) Ø12,7"
for k_, yy in enumerate(_lin):
    ca.chamada((_xd[yy], yy), (26, -10 + 9 * k_ if yy < H / 2 else 6), _rt[yy])
pr.posicoes_desenho.update(f"C{i}" for i in range(1, len(_lin) + 2))

# ------------------------------------------------------------------ CORTE B-B — nariz do dente
cb = pr.vista("CORTE B-B", (Q[0] + 330, YR), 5, titulo="CORTE B-B — NARIZ DO DENTE", subtitulo=f"{B/10:g} × {HD/10:g} acima do recorte de {REC/10:g}", unidade="cm")
pb = [(0, REC), (B, REC), (B, H), (0, H)]
cb.poli(pb, "CORTADO", fechada=True); cb.hachura(pb, "AR-CONC", 0.03)
cb.linha((0, 0), (B, 0), "OCULTA"); cb.linha((0, 0), (0, REC), "OCULTA"); cb.linha((B, 0), (B, REC), "OCULTA")
cb.circulo((B / 2, REC + HD / 2), 25, "VISTA")
for x, y in CORD:
    if y > REC:
        cb.circulo((x, y), 6.35, "ARM_PROT_SECAO")
cb.cota_h([0, B], REC, -10); cb.cota_v([0, REC, H], B, 10, total=False)
cb.chamada((B / 2, REC + HD / 2), (40, 12), "TB-1 Ø50 (pino PN-1)")

# ------------------------------------------------------------------ DETALHE 1 — apoio no CP-MEZ
YD = YR - 10
d1 = pr.vista("DETALHE 1", (Q[0] + 625, YD), 6, titulo="DETALHE 1 — DENTE GERBER NO CONSOLO CP-MEZ (VISTA LATERAL)",
              subtitulo="fundo do consolo alinhado ao fundo da viga; continuidade N11 pelas bainhas do pilar", unidade="cm")
LD = 1500
d1.ret(-FOLGA - 400, -250, 400, H + NEOF + H2 + HCAPA + 350, "OCULTA")
cons = [(-FOLGA, 0), (-FOLGA + PROJ, 0), (-FOLGA + PROJ, HC), (-FOLGA, HC)]
d1.poli(cons, "CORTADO", fechada=True); d1.hachura(cons, "AR-CONC", 0.03)
d1.chapa(X_PAD - FOLGA - A_PAD / 2, HC, A_PAD, 21, 0.4)
d1.poli([(0, REC), (LN, REC), (LN, 0), (LD, 0)], "VISTA"); d1.poli([(LD, H), (0, H), (0, REC)], "VISTA")
d1.interrupcao((LD, 0), (LD, H))
d1.ret(X_TB - 25, REC, 50, HD, "OCULTA")
d1.ret(X_TB - 10, HC - 300, 20, 700, "METALICA")
e2 = [(-FOLGA, H), (LD, H), (LD, H + NEOF + H2 + HCAPA), (-FOLGA, H + NEOF + H2 + HCAPA)]
d1.poli(e2, "OCULTA", fechada=True); d1.hachura(e2, "ANSI31", 0.6)
jt = [(-FOLGA, REC), (0, REC), (0, H), (-FOLGA, H)]
d1.poli(jt, "VISTA", fechada=True); d1.hachura(jt, "AR-SAND", 0.3)
d1.linha((-FOLGA - 600, H + 120), (1100, H + 120), "ARMADURA")
d1.ret(-FOLGA - 400, H + 120 - 25, 400, 50, "OCULTA")
d1.linha((-FOLGA - 600, H + NEOF + H2 + HCAPA - 30), (1300, H + NEOF + H2 + HCAPA - 30), "ARMADURA")
for x in range(150, LD - 50, 150):
    d1.linha((x, H), (x, H + 200), "ARM_TRANSV")
d1.cota_h([-FOLGA, 0, X_TB, LN, -FOLGA + PROJ], 0, -14, total=False)
d1.cota_h([-FOLGA, X_PAD - FOLGA - A_PAD / 2, X_PAD - FOLGA + A_PAD / 2], HC + 21, 10, total=False)
d1.cota_v([0, HC, REC, H, H + NEOF + H2 + HCAPA], LD, 12, total=False)
cmz = next(c for c in N9["consolos"] if c["consolo"] == "CP-MEZ")
d1.chamada((-FOLGA + PROJ / 2, HC / 2), (-70, -34), f"CP-MEZ {P.get('b_consolo', B / 1000) * 100:g} × {PROJ/10:g} × {HC/10:g} (sem chanfro), tirante {cmz['tirante'].split(' (')[0]}".replace(".", ","))
d1.chamada((X_PAD - FOLGA, HC + 5), (50, -16), "NEO-5F 200×200 fretado (furo Ø30)")
d1.chamada((X_TB, HC - 250), (90, -34), "PN-1 Ø20 L=630 (230 no consolo), grauteado")
d1.chamada((-FOLGA / 2, REC + HD / 2), (-26, 10), "junta 3 cm concretada ANTES das lajes (det. 2)")
d1.chamada((-FOLGA - 300, H + 120), (-14, 14), "N11 6 Ø16 em 2 bainhas BA-1 Ø50 (obra)")
d1.chamada((1200, H + NEOF + H2 + HCAPA - 30), (8, 14), "N12 9 Ø12,5 na capa (obra)")
d1.chamada((800, H + 100), (10, 10), "2º estágio (obra)")

# ------------------------------------------------------------------ DETALHE 2 — ponta concretada (planta)
d2 = pr.vista("DETALHE 2", (Q[0] + 190, YR - 210), 4, titulo="DETALHE 2 — PONTA CONCRETADA (PLANTA NO TOPO DA VM)",
              subtitulo="junta VM × pilar concretada nas duas pontas ANTES das lajes (sem torção de montagem, sem peça metálica)", unidade="mm")
d2.ret(-400, -300, 400, 600, "CORTADO"); d2.hachura([(-400, -300), (0, -300), (0, 300), (-400, 300)], "AR-CONC", 0.02)
d2.ret(FOLGA, -B / 2, 450, B, "VISTA"); d2.interrupcao((FOLGA + 450, -B / 2 - 20), (FOLGA + 450, B / 2 + 20))
jt2 = [(0, -B / 2), (FOLGA, -B / 2), (FOLGA, B / 2), (0, B / 2)]
d2.poli(jt2, "VISTA", fechada=True); d2.hachura(jt2, "ANSI31", 0.25)
for yy in (-B / 2, B / 2):
    sg_ = 1 if yy > 0 else -1
    d2.ret(0, yy if sg_ > 0 else yy - 20, FOLGA + 60, 20, "OCULTA")
d2.ret(X_TB - 25, -25, 50, 50, "OCULTA")
d2.cota_h([0, FOLGA, FOLGA + 150], -340, -10, total=False)
d2.cota_v([-B / 2, B / 2], FOLGA + 480, 10, total=False)
d2.chamada((FOLGA / 2, 60), (40, 70), f"junta {FOLGA/10:g} cm concretada: graute ou concreto fck ≥ 30 MPa, do recorte do dente ao topo da VM")
d2.chamada((FOLGA / 2 - 20, -B / 2 - 10), (-30, -28), "fôrma lateral da junta nas 2 faces (retirar após 24 h)")
d2.chamada((FOLGA + 2, -60), (30, -30), "ponta da VM e face do pilar ÁSPERAS (≥ 5 mm a cada 30 mm)")
d2.chamada((FOLGA + 300, 60), (-30, 40), f"VM {B/10:g} × {H/10:g}")
d2.chamada((-200, 0), (-10, 16), "pilar")

# ------------------------------------------------------------------ isométricos
import subprocess
subprocess.run([sys.executable, "/home/claude/letsara/pranchas/iso3d_vm.py"], check=True, capture_output=True)
subprocess.run([sys.executable, "/home/claude/letsara/pranchas/iso3d_vigas.py", "vm"], check=True, capture_output=True)
pr.imagem(Q[0] + 418, Q[1] + 150, Q[0] + 664, Q[1] + 262, "/home/claude/letsara/pranchas/ISO-VM-geral.png",
          titulo="ISOMÉTRICO — VM-02", subtitulo=f"peça inteira: retangular {B/10:g} × {H/10:g}, dentes, alças N9 e AL-1")
pr.imagem(Q[0] + 676, Q[1] + 40, Q[0] + 886, Q[1] + 265, "/home/claude/letsara/pranchas/ISO-VM-ponta.png",
          titulo="ISOMÉTRICO — PONTA DA VM NO PILAR", subtitulo="dente no CP-MEZ (fundos alinhados), junta concretada, PN-1, alças N9, 2º estágio (azul) e laje no topo")

# ------------------------------------------------------------------ tabelas
y = Q[3] - 132
mk = [[m_, POS[m_], QT[m_], f"{VMJ[m_]['L_peca'] * 100:.0f}", str(VMJ[m_]["n_cord"]), f(VMJ[m_]["peso_t"], 2)] for m_ in MKS]
y = pr.tabela(XC, y, "MARCAS — VIGAS DO MEZANINO", ["MARCA", "POSIÇÃO", "QT", "L (cm)", "CORD.", "PESO (t)"], mk, [16, 80, 9, 18, 14, 19])
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
outras = [[m_, str(VMJ[m_]["n_cord"]), " + ".join(f"{n_} em y {yy/10:g}" for yy, n_ in sorted(Counter(c[1] for c in VMJ[m_]["pos_cordoalhas_mm"]).items()))] for m_ in ("VM-01", "VM-03", "VM-04")]
y = pr.tabela(XC, y - 4, "CORDOALHAS DAS OUTRAS MARCAS (mesma força no macaco)", ["MARCA", "Ø12,7", "POSIÇÃO (cm do fundo)"], outras, [18, 16, 134])
ins = [["TB-1", f"Tubo Ø50×3,0 L={HD} a prumo no nariz do dente, sem solda", 2, f"a {X_TB/10:g} cm das pontas, no eixo"],
       ["AL-1", "Laço de cordoalha Ø12,7 (2 pernas), não engraxada", 2, "a 110 cm das pontas"],
       ["NEO-5F", "Neoprene fretado 200×200×21 (furo Ø30) — no pilar", 2, "sobre os consolos CP-MEZ"]]
y = pr.tabela(XC, y - 4, "INSERTOS POR PEÇA — mm", ["MARCA", "DESCRIÇÃO", "QT", "POSIÇÃO"], ins, [16, 92, 10, 50])
obra = [["N11", "6 Ø16 L=600 em 2 bainhas BA-1 do pilar (negativa)", "apoios internos"], ["N12", "9 Ø12,5 L=600 na capa (negativa)", "apoios internos"],
        ["CAPA", f"C30, 5 cm + tela; 2º estágio C30 ({B2/10:g} × 26)", "quem faz a capa"], ["GRAUTE", "junta 3 cm e bainhas, fck ≥ 30 MPa", "antes da capa"]]
y = pr.tabela(XC, y - 4, "ARMADURA E CONCRETO DE OBRA (NBR 9062 5.6.1.2 e)", ["ITEM", "DESCRIÇÃO", "ONDE"], obra, [16, 110, 42])
qd = [["CONCRETO", "C40 (CAA II)", "fcj LIBERAÇÃO", f"{P['fckj']:g} MPa"], ["fcj IÇAMENTO", f"{P['fckj']:g} MPa", "Eci / Ecs", f"{P['Eci_MPa']/1000:.1f} / {P['Ecs_MPa']/1000:.1f} GPa".replace(".", ",")],
      ["COBRIMENTO", "2,5 (estribo) / 3,0 (cord.)", "F MACACO", f"{f(F_MAC)} kN/cord."], ["VOLUME VM-02", f"{f(V_TOT, 2)} m³", "PESO VM-02", f"{f(PESO, 2)} t"]]
y = pr.tabela(XC, y - 4, "QUADRO DA PEÇA", ["ITEM", "VALOR", "ITEM", "VALOR"], qd, [30, 54, 30, 54])
c39, c73 = CM["piso_390"], CM["laje_730"]
notas = [
    f"VIGA RETANGULAR COM 2º ESTÁGIO (DEC-047/048, decisão do Nathan): a laje alveolar apoia 10 cm sobre o TOPO da viga (neoprene em fita 10 mm); na faixa restante de {B2/10:g} cm do lado da borda saem as alças N9 Ø10 c/15 para o 2º ESTÁGIO, concretado junto com a capa POR QUEM EXECUTA A CAPA (interface NBR 9062:2017 6.3: τsd {f(R['interface']['tau_sd'], 2)} ≤ τRd {f(R['interface']['tau_rd'], 2)} MPa). Topo da peça rugoso (≥ 5 mm a cada 30 mm), limpo e saturado antes da concretagem.",
    f"SEM ESCORAMENTO: a peça isolada leva peso próprio, laje, 2º estágio e capa frescos e 1 kN/m² de montagem (fase 1); revestimento e sobrecarga na seção composta (fase 2): +3,90 revestimento {f(c39['revestimento'])} e sobrecarga {f(c39['sobrecarga'])} kN/m²; +7,30 (laje de cobertura do bloco, acesso apenas para manutenção, NBR 6120:2019 Tab. 10): sobrecarga {f(c73['sobrecarga'])} + regularização/impermeabilização {f(c73['revestimento'])} kN/m².",
    f"Dente Gerber {HD/10:g} × {LN/10:g} nas pontas (NBR 9062:2017 7.4; MEF não linear): fundo do consolo CP-MEZ = fundo da viga (+{f(ZB[0]/1000, 2)} e +{f(ZB[1]/1000, 2)}). Pino PN-1 Ø20 grauteado no TB-1 numa ponta; na outra graute flexível.",
    "SEM TORÇÃO DE MONTAGEM (regra do Nathan, DEC-039): antes de montar as lajes, CONCRETAR AS PONTAS da VM dos dois lados (junta 3 cm VM × pilar, do recorte do dente ao topo, graute ou concreto fck ≥ 30 MPa; det. 2) e aguardar fcj ≥ 20 MPa. Sem peça metálica.",
    "Obra (sequência): VM (NEO-5F, PN-1) → concretar as pontas dos dois lados (det. 2) → aguardar fcj ≥ 20 MPa → lajes alveolares (apoio 10 cm no topo, neoprene em fita) → grautear as bainhas BA-1 com N11 → limpar e saturar o topo → N12, tela e chavetas → 2º estágio + capa de uma vez → cura 7 dias; carregar com fck ≥ 20 MPa.",
    f"Protensão: {len(CORD)} cordoalhas Ø12,7 CP-190 RB aderentes na VM-02 (posição no corte A-A e na tabela; outras marcas na tabela própria), σpi = 1400 MPa; C1 isoladas 150 cm nas pontas; 2 no topo controlam o ato. Liberação GRADUAL e simétrica com fcj ≥ 32 MPa (lbpt = {f(R['ato']['lbpt_m'] * 100, 0)} cm; perdas pela NBR 6118 9.6.3 — total {f(R['protensao']['perdas']['perda_total_pct'])} %). Protensão COMPLETA (NBR 6118:2023 Tab. 13.4, DEC-043).",
    f"Zona de transferência no canto do dente (DEC-049, MEF): o elemento do canto inferior junto ao recorte, onde as cordoalhas começam a transferir, passa de 3,5‰ a ~290 kN (pico do modelo 520 kN ≥ Fd 476 kN) — FRETAR: N14 estribos fechados Ø8 c/5 nos 50 cm a partir do canto reentrante envolvendo as 2 camadas inferiores + N13 4 Ø16 retas no fundo (250 cm) e N7 3 Ø20 de suspensão (faixa de baixo). Registrado na memória de cálculo.",
    "Içar pelas 2 alças AL-1 (cabos ≥ 45°); estocar sobre 2 calços sob as alças, pressão ≤ 0,3 fcj; transportar apoiada nos mesmos pontos, travada contra tombamento.",
    "Tolerâncias (NBR 9062:2017 5.2.2): comprimento ±15 mm, seção −5/+10 mm, linearidade ±L/1000, insertos ±15 mm, cordoalhas ±10 mm (resultante ±5); montagem: nível do apoio ±10 mm, planta ±10 mm. Folga de 3 cm na ponta.",
    "Cotas de concreto em cm, chaparia em mm. Armação e protensão na faixa de baixo desta folha."]
notas.append("PENDÊNCIA (decisão em aberto): VM da linha 1 nos vãos A–B e D–E — o pilar de canto passou a ficar 10 cm para fora da linha "
             "e o dente da VM no eixo fica 5 cm fora do CP-MEZ; não produzir as VM da linha 1 antes da resposta (ND-LET-NG01).")   # rev12
y = pr.notas(XC, y - 4, notas, 190)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-VM01")
print("VM01", len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
for a in avisos:
    print(" ", a)
