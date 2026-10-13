"""ND-LET-TS01-1 — TS-01: fôrma, insertos e transitórias (A0). Padrão de prancha de peça pré-moldada (cast unit).
Revisão 01: dentes Gerber nas duas pontas, mão-francesa presa no fundo da viga (CH-MF), chumbadores calculados."""
import json
from prancha_nd import Prancha
from ts01_dados import P, L, H, DX, HD, LN, PASSO_T, sec, R, TR, V, peso, ALCA_Fd, ALCA_cap, tipo_terca, f

LG = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/ligacoes.json"))
DT = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/dentes.json"))
CB = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/cobertura_metalica.json"))
pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="TS-01 — VIGA I90 DE COBERTURA PROTENDIDA — FÔRMA, INSERTOS E TRANSITÓRIAS",
                        desenho="ND-LET-TS01-1", folha="01/04", fase="PARA APROVAÇÃO"))
pr.revisao("01", "12/10/2026", "DENTES GERBER, MÃO-FRANCESA NO FUNDO, CHUMBADORES CALCULADOS, TERÇAS c/1579")
pr.revisao("02", "12/10/2026", "GEOMETRIA DO R01: L 19,15 m ENTRE FACES (TERÇAS c/1554); ORELHAS DO X NA CH-T2")
pr.cabecalho_peca("TS-01", f"VIGA DE COBERTURA I90 PROTENDIDA — SEÇÃO I90 (b 40, bw 15, h 90) · L = {L/10:.0f} cm (entre pontas, a prumo) · 14 PEÇAS",
                  f"PESO {f(peso/9.81,1)} t   ·   VOLUME {f(V,2)} m³   ·   C50 / fckj 35   ·   {P['n_cord']} cord. Ø12,7 CP-190 RB   ·   dentes Gerber 45 × 30 nas duas pontas   ·   caimento 3 %", 560)
mac, yfi, yci, ycs, yfs = P["x_mac"], 150, 230, 700, 780
TER, NOS, ALC, EST = P["tercas"], P["nos"], P["alcas"], P["estoque"]
t3 = DX / H
sk = lambda h: h * t3                      # ponta a prumo: deslocamento ao longo da peça na altura h
S_PINO = [P["pino_x"] + sk(HD), L - P["pino_x"] + sk(HD)]
MF_FUNDO = [s - DX for s in TER[1:-1]]     # CH-MF no fundo, no plano da terça (topo − 27 mm)
MF_LAT = [TER[0] - sk(H - HD - 75), TER[-1] - sk(H - HD - 75)]
CONTORNO = [(LN, 0), (L - LN, 0), (L - LN + sk(HD), HD), (L + sk(HD), HD), (L + DX, H), (DX, H), (sk(HD), HD), (LN + sk(HD), HD)]


def chapa_topo(v, s, plano=False):
    t = tipo_terca(s)
    ds = 150 if t == "CH-T2" else 100
    if plano:
        dy = 190 if t == "CH-T2" else 100
        v.ret(s - ds, -dy, 2 * ds, 2 * dy, "METALICA")
        for yy in (-50, 50):
            v.circulo((s + 55, yy), 9, "METALICA")
        if t == "CH-T2":
            for so, yo in ((140, 140), (-140, 140), (140, -140), (-140, -140)):
                v.ret(s + so - 5, yo - 45, 10, 90, "METALICA")
    else:
        v.ret(s - ds, H - 12.5, 2 * ds, 12.5, "METALICA")
        if t == "CH-T2":
            for so in (-140, 140):
                v.ret(so + s - 45, H, 90, 80, "METALICA")


# ------------------------------------------------------------------ PLANTA SUPERIOR 1:25
vp = pr.vista("PLANTA SUPERIOR", (80, 752), 25, titulo="PLANTA SUPERIOR — TS-01", subtitulo="face superior (topo da mesa)")
vp.ret(DX, -200, L, 400, "VISTA")
for s in TER:
    chapa_topo(vp, s, plano=True)
for s in ALC:
    vp.ret(s - 50, -8, 100, 16, "METALICA")
vp.cota_ord([0] + TER + [L + DX], 200, 6, x0=0, rotulos=["0"] + [f"{s:.0f}" for s in TER] + [f"{L + DX:.0f}"])
vp.cota_ord(ALC, -200, -6, x0=0, rotulos=[f"{s:.0f}" for s in ALC])
vp.chamada((TER[0], 100), (10, 30), "CH-T2 (nós de contraventamento, 7x)")
vp.chamada((TER[1], 100), (14, 26), "CH-T1 200×200×12,5 A36 embutida (terças, 6x) + ST-1 soldado depois")
vp.chamada((ALC[0], 0), (8, -26), "AL-1 (4 alças de cordoalha)")
vp.cota_v([-200, 200], L + DX, 8)

# ------------------------------------------------------------------ ELEVAÇÃO 1:25
ve = pr.vista("ELEVAÇÃO", (80, 622), 25, titulo="ELEVAÇÃO — TS-01",
              subtitulo="peça fabricada reta; pontas e faces dos dentes a prumo na posição montada (caimento 3%)")
ve.poli(CONTORNO, "VISTA", fechada=True)
for y in (yfi, yci, ycs, yfs):
    ve.linha((mac + sk(y), y), (L - mac + sk(y), y), "VISTA")
for x in (mac, L - mac):
    ve.linha((x + sk(yfi), yfi), (x + sk(yci), yci), "VISTA"); ve.linha((x + sk(ycs), ycs), (x + sk(yfs), yfs), "VISTA")
for s0 in S_PINO:
    for d in (-25, 25):
        ve.linha((s0 + d, HD), (s0 + d + sk(H - HD), H), "OCULTA")
    ve.ret(s0 - 75, HD, 150, 12.5, "METALICA")
for s in TER:
    chapa_topo(ve, s)
for s in MF_FUNDO:
    ve.ret(s - 75, 0, 150, 12.5, "METALICA")
for s in MF_LAT:
    ve.ret(s - 60, HD + 30, 120, 90, "METALICA")
for s in ALC:
    ve.poli([(s - 50, H), (s - 50, H + 110), (s, H + 150), (s + 50, H + 110), (s + 50, H)], "METALICA")
    for d in (-50, 50):
        ve.linha((s + d, H), (s + d - sk(H - 200), 200), "OCULTA")
cgx, cgy = L / 2 + sk(sec.yc * 1000), sec.yc * 1000
ve.circulo((cgx, cgy), 100, "INDICACAO"); ve.linha((cgx - 180, cgy), (cgx + 180, cgy), "INDICACAO")
ve.linha((cgx, cgy - 180), (cgx, cgy + 180), "INDICACAO")
ve.chamada((cgx + 70, cgy + 70), (10, 12), f"CG (s = {f(cgx/1000,3)} m; h = {cgy:.0f} mm)")
ve.chamada((MF_FUNDO[4], 6), (8, -18), f"CH-MF no fundo ({len(MF_FUNDO)}x, no plano das terças)")
ve.chamada((S_PINO[0] + 6, 700), (-12, 16), "TB-1 Ø50 a prumo")
ve.chamada((S_PINO[1], HD + 6), (14, -22), "CH-A1 no dente (2x)")
ve.chamada((MF_LAT[1], HD + 75), (12, 14), "CH-MF2 lateral no dente (2+2)")
ve.cota_h([LN, ALC[0], ALC[1], ALC[2], ALC[3], L - LN], 0, -14)
ve.cota_h([0, LN], 0, -14, total=False)
ve.cota_h([L - LN, L], 0, -14, total=False)
ve.cota_v([0, HD, H], 0, -10)
ve.cota((L + sk(HD), HD), (L + DX, H), 8, 0)
ve.marcador_corte((TER[5] + 60, -60), (TER[5] + 60 + DX, H + 60), "A", lado=1)
ve.marcador_corte((S_PINO[0] + 110, HD - 60), (S_PINO[0] + 110 + sk(H - HD), H + 60), "B", lado=1)
ve.marcador_corte((TER[4] + 60, -60), (TER[4] + 60 + DX, H + 60), "C", lado=1)
ve.marcador_detalhe((420, 450), 700, 1, ang=150, dist=10)
ve.marcador_detalhe((ALC[1], H), 400, 2, ang=60, dist=6)

# ------------------------------------------------------------------ VISTA INFERIOR 1:25
vi = pr.vista("VISTA INFERIOR", (80, 540), 25, titulo="VISTA INFERIOR — TS-01", subtitulo="fundo da fôrma e fundo dos dentes")
vi.ret(LN, -200, L - 2 * LN, 400, "VISTA")
vi.ret(0, -200, LN, 400, "OCULTA")
vi.ret(L - LN, -200, LN, 400, "OCULTA")
for s0 in S_PINO:
    vi.ret(s0 - 75, -150, 150, 300, "METALICA"); vi.circulo((s0, 0), 26, "METALICA")
for s in MF_FUNDO:
    vi.ret(s - 75, -180, 150, 360, "METALICA")
    for yy in (-150, 150):
        vi.circulo((s, yy), 9, "METALICA")
for x in EST:
    vi.poli([(x - 120, -260), (x + 120, -260), (x, -205)], "INDICACAO", fechada=True)
vi.chamada((MF_FUNDO[0], 150), (8, 12), "CH-MF 150×360×12,5 (OR-1 soldada por baixo)")
vi.chamada((EST[0], -260), (30, -26), "calço de estoque/transporte (2x)")
vi.chamada((S_PINO[1], 150), (6, 14), "CH-A1 no fundo do dente")
vi.cota_ord([0] + MF_FUNDO, -200, -6, x0=0, rotulos=["0"] + [f"{s:.0f}" for s in MF_FUNDO])

# ------------------------------------------------------------------ ESQUEMAS DE IÇAMENTO E ESTOCAGEM 1:100
vq = pr.vista("ESQUEMA DE IÇAMENTO", (60, 418), 100, titulo="IÇAMENTO — DESFORMA E MONTAGEM",
              subtitulo="4 alças AL-1, 2 balancins, cabos verticais")
vq.poli(CONTORNO, "VISTA", fechada=True)
za, zb, zg = H + 1600, H + 3000, H + 4600
for a, b in ((ALC[0], ALC[1]), (ALC[2], ALC[3])):
    vq.linha((a, H + 150), (a, za), "INDICACAO"); vq.linha((b, H + 150), (b, za), "INDICACAO")
    vq.ret(a, za, b - a, 250, "METALICA")
    vq.linha(((a + b) / 2, za + 250), ((a + b) / 2, zb), "INDICACAO")
vq.ret(ALC[0] + 1500, zb, ALC[3] - ALC[0] - 3000, 300, "METALICA")
vq.linha((L / 2, zb + 300), (L / 2, zg), "INDICACAO")
vq.chamada((L / 2, zg), (8, 3), f"gancho: {f(peso,0)} kN ({f(peso/9.81,1)} t)")
vq.chamada(((ALC[0] + ALC[1]) / 2, za + 250), (-8, 6), "balancim")
vq.cota_h([0] + ALC + [L], 0, -7)
vq.texto((0, -2600), f"Reação por alça (×1,3): {f(ALCA_Fd,1)} kN ≤ {f(ALCA_cap,1)} kN (laço Ø12,7)", "nota")

ve2 = pr.vista("ESQUEMA DE ESTOCAGEM", (60, 348), 100, titulo="ESTOQUE E TRANSPORTE",
               subtitulo="2 calços de 150 mm sob a mesa inferior, sem empilhamento")
ve2.poli(CONTORNO, "VISTA", fechada=True)
for x in EST:
    ve2.poli([(x - 250, -400), (x + 250, -400), (x, 0)], "INDICACAO", fechada=True)
ve2.cota_h([0] + EST + [L], -400, -6)

# ------------------------------------------------------------------ CORTES 1:10
pts = [(x * 1000, y * 1000) for x, y in sec.pts]


def corte_I(nome, org, sub, s_tipo):
    v = pr.vista(nome, org, 10, titulo=nome, subtitulo=sub)
    v.poli(pts, "CORTADO", fechada=True); v.hachura(pts, "AR-CONC", 0.03)
    for x in P["x_cord"]:
        v.ponto_barra((x, P["y_cord"]), 12.7, "ARM_PROT_SECAO")
    dy = 190 if s_tipo == "CH-T2" else 100
    v.ret(-dy, H - 12.5, 2 * dy, 12.5, "METALICA")
    v.chapa(-110, H, 220, 290, 0.25)                                         # ST-1 soldado em cima, após a desforma (ND-LET-COB01)
    pinos = (-150, 0, 150) if s_tipo == "CH-T2" else (-75, 75)
    for yy in pinos:
        v.linha((yy, H - 12.5), (yy, H - 112.5), "METALICA"); v.ret(yy - 16, H - 120, 32, 8, "METALICA")
    if s_tipo == "CH-T2":
        v.poli([(-170, H - 140), (-170, H - 60), (170, H - 60), (170, H - 140)], "ARM_TRANSV")   # grampo U Ø10
    v.ret(-180, 0, 360, 12.5, "METALICA")                                       # CH-MF no fundo
    v.chapa(-150, -100, 300, 100, 0.25)                                        # OR-1 soldada por baixo, após a desforma
    for yy in (-100, 100):
        v.linha((yy, 12.5), (yy, 92.5), "METALICA"); v.ret(yy - 12.5, 92.5, 25, 7, "METALICA")
    v.cota_h([-200, -75, 75, 200], 0, -16)
    v.cota_v([0, P["y_cord"], H], 200, 12)
    v.cota_h([-dy, -50, 50, dy], H, 10)
    return v


va = corte_I("CORTE A-A", (128, 170), "terça comum: CH-T1 + ST-1; CH-MF + OR-1", "CH-T1")
va.chamada((60, H - 6), (-18, 22), "CH-T1 200×200×12,5")
va.chamada((0, H + 200), (24, 10), "ST-1 chapa 8×220×290 ASTM A36 + 2 enrij. 8×90×90, soldado na CH-T1 após a desforma (filete 6 mm, 2 lados) — terça parafusada na obra (2 M12 por ponta), ND-LET-COB01")
va.chamada((-75, H - 80), (-16, 12), "4 pinos Ø16 c/ cabeça, L = 112")
va.chamada((100, -50), (14, -40), "CH-MF 150×360×12,5 A36 + OR-1 8×300×100 A36 soldada após a desforma (M12)")
va.chamada((-100, 60), (-18, 8), "2 pinos Ø12,5 c/ cabeça")
va.chamada((100, P["y_cord"]), (22, 26), "6 cord. Ø12,7")

vc = corte_I("CORTE C-C", (300, 170), "nó do X: CH-T2 + ST-1", "CH-T2")
for yo in (-140, 140):
    vc.ret(yo - 45, H, 90, 80, "METALICA")
    vc.circulo((yo, H + 35 if yo > 0 else H + 70), 8, "METALICA")
vc.chamada((140, H + 80), (14, 18), "orelha 90×80×9,5 furo Ø16 (4x)")
vc.chamada((-120, H - 6), (-16, 26), "CH-T2 300×380×12,5")
vc.chamada((170, H - 100), (18, -8), "2 grampos U Ø10 (ancoragem da cortante)")
vc.chamada((0, H - 80), (-6, -30), "6 pinos Ø16 c/ cabeça")
vc.cota_v([H, H + 35, H + 70], 205, 22, total=False)

vb = pr.vista("CORTE B-B", (455, 215), 10, titulo="CORTE B-B", subtitulo="dente, junto ao TB-1")
rb = [(-200, 0), (200, 0), (200, H - HD), (-200, H - HD)]
vb.poli(rb, "CORTADO", fechada=True); vb.hachura(rb, "AR-CONC", 0.03)
vb.ret(-25, 0, 50, H - HD, "VISTA")
vb.ret(-150, 0, 300, 12.5, "METALICA")
for yy in (-120, 120):
    vb.poli([(yy, 12.5), (yy, 200), (yy + (25 if yy < 0 else -25), 220)], "METALICA")
for x in (-150, -60, 60, 150):
    vb.ponto_barra((x, 55), 16)
vb.chamada((25, 300), (20, 6), "TB-1 tubo Ø50, L = 450")
vb.chamada((140, 6), (18, -12), "CH-A1 300×150×12,5")
vb.chamada((-150, 55), (-18, 14), "tirante do dente 4 Ø16 (folha 02)")
vb.cota_h([-200, -150, -25, 25, 150, 200], 0, -16)
vb.cota_v([0, H - HD], 200, 12)

# ------------------------------------------------------------------ DETALHE 1 — ponta com dente (1:10)
d1 = pr.vista("DETALHE 1", (610, 160), 10, titulo="DETALHE 1 — DENTE GERBER E APOIO NO CONSOLO",
              subtitulo="posição montada: caimento 3%; consolo do pilar com topo a 3%")
d1.poli([(1500, 0), (LN, 0), (LN + sk(HD), HD), (sk(HD), HD), (DX, H), (1500 + DX, H)], "VISTA")
d1.interrupcao((1500, 0), (1500 + DX, H))
for y in (yfi, yci, ycs, yfs):
    d1.linha((mac + sk(y), y), (1500 + sk(y), y), "VISTA")
d1.linha((mac + sk(yfi), yfi), (mac + sk(yci), yci), "VISTA"); d1.linha((mac + sk(ycs), ycs), (mac + sk(yfs), yfs), "VISTA")
s0 = S_PINO[0]
for d in (-25, 25):
    d1.linha((s0 + d, HD), (s0 + d + sk(H - HD), H), "OCULTA")
d1.ret(s0 - 75, HD, 150, 12.5, "METALICA")
d1.ret(s0 - 75, HD - 10, 150, 10, "VISTA")                                  # neoprene
d1.ret(s0 - 12.5, HD - 310, 25, 700, "OCULTA")                              # pino PN-1
d1.poli([(-25, HD - 10), (LN - 25 + sk(HD - 10), HD - 10 - 0), (LN - 25, -200), (-25, -200)], "OCULTA")   # consolo
d1.linha((-25, -300), (-25, H + 100), "EIXO")
d1.cota_h([sk(HD), s0 - 75, s0, s0 + 75, LN + sk(HD)], HD, 14, total=False)
d1.cota_h([LN, mac], 0, -14, total=False)
d1.cota((sk(HD), HD), (DX, H), 8, 0)
d1.cota_v([0, HD - 10, HD, H], 1500 + DX, 10, total=False)
d1.cota((LN - 25, -200), (LN, -200), -8, 0)
d1.chamada((DX / 2 + sk(HD) / 2, (H + HD) / 2), (-12, 12), "ponta a prumo")
d1.chamada((s0, 700), (14, 30), "TB-1 Ø50 inclinado 3% na fôrma")
d1.chamada((s0 + 60, HD - 5), (26, -10), "neoprene 300×150×10 c/ furo Ø40")
d1.chamada((s0, HD - 250), (-10, -8), "pino PN-1 Ø20 (consolo)")
d1.chamada((LN - 25, -120), (8, -14), "consolo CP-TS, folga 25 até a face do dente")
d1.chamada((-25, 200), (-8, 10), "face do pilar")

# ------------------------------------------------------------------ DETALHE 2 — alça AL-1 (1:10)
d2 = pr.vista("DETALHE 2", (865, 150), 10, titulo="DETALHE 2 — ALÇA AL-1", subtitulo="laço de cordoalha Ø12,7 CP-190 RB")
d2.poli([(-300, 0), (300, 0), (300, H), (-300, H)], "VISTA")
for y in (yfi, yci, ycs, yfs):
    d2.linha((-300, y), (300, y), "VISTA")
d2.poli([(-50, 200), (-50, H + 110), (0, H + 150), (50, H + 110), (50, 200)], "ARMADURA")
for d in (-50, 50):
    d2.linha((d, 200), (d - 40, 120), "ARMADURA"); d2.linha((d, 200), (d + 40, 120), "ARMADURA")
d2.cota_v([200, H, H + 150], 50, 18, total=False)
d2.cota_h([-50, 50], H + 150, 8)
d2.chamada((-50, 500), (-14, 10), "2 pernas na alma")
d2.chamada((50, 160), (12, -8), "pontas desfiadas")
d2.chamada((0, H + 150), (10, 10), "laço livre 150")

# ------------------------------------------------------------------ ISOMÉTRICO
pr.imagem(400, 312, 980, 488, "/home/claude/letsara/pranchas/ISO-TS01-geral-crop.png", "ISOMÉTRICO — TS-01",
          "modelo 3D da peça com insertos (sem escala)")

# ------------------------------------------------------------------ coluna da direita
x0, y = pr.quadro[2] - 180, pr.quadro[3] - 6
n2 = sum(tipo_terca(s) == "CH-T2" for s in TER)
ins = [["AL-1", "Alça laço cordoalha Ø12,7, 2 pernas 700", 4, "1,5", "ver planta"],
       ["CH-T1", "Chapa 200×200×12,5 + 4 pinos Ø16 (+ ST-1 soldado)", len(TER) - n2, "4,6", "terças pares"],
       ["CH-T2", "Chapa 300×380×12,5 + 4 orelhas + 6 pinos (+ ST-1)", n2, "14,3", f"nós c/ {2*PASSO_T}"],
       ["CH-MF", "Chapa 150×360×12,5 + 2 pinos Ø12,5 (+ OR-1 soldada)", len(MF_FUNDO), "5,7", "fundo, terça − 27"],
       ["CH-MF2", "Chapa 120×90×9,5 + luva M16 + 2 pinos (lateral)", 4, "1,3", "dente, 2 faces"],
       ["TB-1", "Tubo Ø50×3,0 L=450 a prumo (pino PN-1 Ø20)", 2, "1,6", "no dente"],
       ["CH-A1", "Chapa 300×150×12,5 furo Ø52 + 4 grapas Ø10", 2, "5,2", "fundo do dente"]]
y = pr.tabela(x0, y, "INSERTOS (CHAPARIA NA FOLHA 03)", ["MARCA", "DESCRIÇÃO", "QT", "kg/un", "POSIÇÃO"], ins,
              [16, 92, 10, 16, 46])
qd = [["MARCA", P["marca"], "QUANTIDADE", f"{P['qtd']}"],
      ["COMPR. FÔRMA", f"{L - 2 * LN} mm (fundo)", "ENTRE PONTAS", f"{L} mm (ponto 0)"],
      ["VOLUME", f"{f(V,3)} m³", "PESO", f"{f(peso,1)} kN ({f(peso/9.81,2)} t)"],
      ["CONCRETO", f"C{P['fck']} / fckj {P['fckj']}", "PROTENSÃO", f"{P['n_cord']} cord. Ø12,7"],
      ["DENTE", f"{HD} × {LN} (2 pontas)", "PONTA", f"a prumo (desl. {DX} mm)"]]
y = pr.tabela(x0, y - 4, "QUADRO DA PEÇA", ["ITEM", "VALOR", "ITEM", "VALOR"], qd, [30, 60, 30, 60])
dm, es = TR["desforma_montagem"], TR["estoque_transporte"]
tr = [["Desforma / montagem", "4 alças", f"{f(dm['Mpos'],0)} / {f(dm['Mneg'],0)}",
       f"{f(max(dm['tens_sup_inf_Mpos'][0], dm['tens_sup_inf_Mneg'][0]),2)} / {f(min(dm['tens_sup_inf_Mpos'][1], dm['tens_sup_inf_Mneg'][1]),2)}", "OK"],
      ["Estoque / transporte", "2 calços", f"{f(es['Mpos'],0)} / {f(es['Mneg'],0)}",
       f"{f(max(es['tens_sup_inf_Mpos'][0], es['tens_sup_inf_Mneg'][0]),2)} / {f(min(es['tens_sup_inf_Mpos'][1], es['tens_sup_inf_Mneg'][1]),2)}", "OK"]]
y = pr.tabela(x0, y - 4, f"TRANSITÓRIAS (×1,3; limites {f(TR['limites_MPa'][0],1)} / {f(TR['limites_MPa'][1],2)} MPa)",
              ["FASE", "APOIO", "M+ / M- (kN·m)", "σ sup. / inf. (MPa)", "OK"], tr, [42, 22, 38, 60, 18])
dts = DT["TS-01"]
mef = dts.get("mef", {})
ct = LG["contraventamento"]
lg = [["TB-1 × pino nos consolos", "28 apoios", f"{max(a['dist_mm'] for a in LG['apoios']):.1f} mm", "OK"],
      ["Ponta × face / consolo × dente", "28 apoios", f"folgas ≥ {min(min(a['folga_ponta_mm'], a['folga_consolo_mm']) for a in LG['apoios'])} mm", "OK"],
      ["CH-T1/T2 × linha de terças", "14 vigas", f"{max(t['dist_mm'] for t in LG['tercas']):.1f} mm", "OK"],
      ["Tirante × terça / tirante (X)", f"{ct['n_tirantes']} tirantes", f"{ct['folga_min_terca_mm']} / {f(ct['folga_cruzamento_mm'],1)} mm", "OK"]]
y = pr.tabela(x0, y - 4, f"CHECAGEM DE LIGAÇÕES NO MODELO (tol. {LG['tol_mm']:.0f} mm)", ["LIGAÇÃO", "INSTÂNCIAS", "DESVIO / FOLGA", "OK"],
              lg, [62, 38, 62, 18])
ch = CB["chumbadores"]
mem = [["ELU flexão", f"Md {f(R.linhas['Md_kNm'],0)} ≤ MRd {f(R.linhas['MRd_kNm'],0)} kN·m"],
       ["ELS-F / ELS-D (fundo)", f"{f(R.linhas['elsf_inf_MPa'],2)} / {f(R.linhas['elsd_inf_MPa'],2)} MPa"],
       ["Flecha final", f"{f(R.linhas['flecha_final_mm'],0)} mm ≤ {f(R.linhas['flecha_lim_mm'],0)} mm"],
       ["Dente (NBR 9062 + PCI)", f"Vd {dts['Vd']:.0f} kN, Hd {dts['Hd']:.0f} kN — {dts['calculo']['adotado']['tirante']}"],
       ["Dente — MEF não linear", f"Vu = {mef.get('Vu_kN', '-')} kN ≥ Vd (Vu/Vd = {mef.get('FS', '-')})".replace(".", ",")],
       ["Chumbadores CH-T1 / CH-T2", f"interação {f(ch['CH-T1']['interacao'],2)} / {f(ch['CH-T2']['interacao'],2)} (ACI 318-19 cap. 17)"]]
y = pr.tabela(x0, y - 4, "MEMÓRIA RESUMIDA", ["VERIFICAÇÃO", "RESULTADO"], mem, [52, 128])
notas = [f"Fabricar a peça reta; fundo da fôrma com {L - 2 * LN} mm entre as faces dos dentes. Cabeceiras e faces dos dentes inclinadas 3% (topo deslocado {DX} mm) para ficarem a prumo na montagem.",
         "Cotas ordenadas a partir do ponto 0 = encontro da face da ponta esquerda (a prumo) com o plano do fundo da viga.",
         "TB-1 a prumo na posição final (inclinado 3% na fôrma, gabarito). Cordoalhas cortadas rente à face do dente.",
         f"Desforma, içamento e montagem só pelas 4 alças AL-1 com 2 balancins e cabos verticais; liberar com fckj ≥ {P['fckj']} MPa.",
         "Estoque e transporte sobre 2 calços de madeira de 150 mm sob a mesa inferior, sem empilhamento; as orelhas OR-1 sobressaem 100 mm do fundo (calços de 150 mm fora das OR-1). ST-1 e OR-1 soldados na fábrica após a desforma (ND-LET-COB01).",
         "Chapas de topo e de fundo faceando o concreto, niveladas; tolerância ±5 mm.",
         f"Terças a cada {PASSO_T} mm; CH-MF no fundo deslocada 27 mm em relação à CH-T do topo (plano vertical da terça). Primeira e última terça: mão-francesa na CH-MF2, na face lateral do dente.",
         "Chaparia ASTM A36, galvanizada a fogo ou fundo epóxi após a desforma. Medidas em mm.",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(x0, y - 4, notas, 180)
pr.posicoes_desenho.clear()
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-TS01-1")
for a in avisos:
    print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
