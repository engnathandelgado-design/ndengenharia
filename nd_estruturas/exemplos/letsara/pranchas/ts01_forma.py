"""ND-LET-TS01-1 — TS-01: fôrma, insertos e manuseio (A0). Padrão de prancha de peça pré-moldada (cast unit).
Rev. 03 (14/10/2026): sem dentes Gerber (apoio direto: assento do pilar lateral e topo da I130 / pilar central), terças a
cada ~1,20 m, todas as ligações da cobertura parafusadas em esperas de barra roscada (sem solda), 8 cordoalhas."""
import json
from prancha_nd import Prancha
from ts01_dados import P, L, H, DX, PASSO_T, sec, V, peso, ALCA_Fd, f

LG = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/ligacoes.json"))
pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="TS-01 — VIGA I90 DE COBERTURA PROTENDIDA — FÔRMA, INSERTOS E MANUSEIO",
                        desenho="ND-LET-TS01-1", folha="01/03", fase="PARA APROVAÇÃO"))
pr.revisao("01", "12/10/2026", "DENTES GERBER, MÃO-FRANCESA NO FUNDO, CHUMBADORES CALCULADOS")
pr.revisao("02", "12/10/2026", "GEOMETRIA DO R01; ORELHAS DO X NA CH-T2")
pr.revisao("03", "14/10/2026", "SEM DENTES (APOIO DIRETO), TERÇAS c/1,20 m, ESPERAS ROSCADAS (SEM SOLDA), 8 CORDOALHAS")
pr.cabecalho_peca("TS-01", f"VIGA DE COBERTURA I90 PROTENDIDA — SEÇÃO I90 (b 40, bw 15, h 90) · L = {L/10:.1f} cm (entre pontas, a prumo) · 14 PEÇAS".replace(".", ","),
                  f"PESO {f(peso/9.81,1)} t   ·   VOLUME {f(V,2)} m³   ·   C50 / fckj 35   ·   {P['n_cord']} cord. Ø12,7 CP-190 RB   ·   sem dentes: apoio direto em neoprene   ·   caimento 3 %", 560)
mac, yfi, yci, ycs, yfs = P["x_mac"], 150, 230, 700, 780
TER, NOS, ALC, EST = P["tercas"], P["nos"], P["alcas"], P["estoque"]
t3 = DX / H
sk = lambda h: h * t3                      # ponta a prumo: deslocamento ao longo da peça na altura h
CONTORNO = [(0, 0), (L, 0), (L + DX, H), (DX, H)]
TB = P["tb"]
S_TB = [TB["s_ext"], L - TB["s_cen"]]                 # tubos TB-3 (no fundo; a prumo na montagem)
ES1 = lambda s: s - 75                                 # esperas do ST-1P: 75 mm antes do eixo da terça (aba horizontal)
ES3 = lambda s: s - sk(H + 50 - 100)                   # esperas da mão-francesa: no plano vertical da alma da terça, 100 do fundo
eh_no = lambda s: any(abs(s - n) < 1 for n in NOS)


def esperas_topo(v, s, plano):
    """ES-1 (2 por terça) e ES-2 (4 por nó do X). plano=True: vista de cima; False: elevação."""
    if plano:
        for yy in (-60, 60):
            v.circulo((ES1(s) + DX, yy), 8, "METALICA")
        if eh_no(s):
            for so in (-140, 140):
                for yy in (-140, 140):
                    v.circulo((s + so + DX, yy), 8, "METALICA")
    else:
        v.ret(ES1(s) + DX - 8, H, 16, 120, "METALICA")
        if eh_no(s):
            for so in (-140, 140):
                v.ret(s + so + DX - 8, H, 16, 50, "METALICA")


# ------------------------------------------------------------------ PLANTA SUPERIOR 1:25
vp = pr.vista("PLANTA SUPERIOR", (80, 752), 25, titulo="PLANTA SUPERIOR — TS-01", subtitulo="face superior; COTAS EM CM", unidade="cm")
vp.ret(DX, -200, L, 400, "VISTA")
for s in TER:
    esperas_topo(vp, s, True)
    vp.linha((s + DX, -230), (s + DX, 230), "EIXO")
for s in ALC:
    vp.ret(s - 50 + DX, -8, 100, 16, "METALICA")
for s0 in S_TB:
    for yy in TB["y"]:
        vp.circulo((s0 + DX, yy), TB["d"] / 2, "OCULTA")
vp.cota_ord([DX] + [s + DX for s in TER] + [L + DX], 200, 6, x0=DX, rotulos=["0"] + [vp.fmt(s) for s in TER] + [vp.fmt(L)])
vp.cota_ord([s + DX for s in ALC], -200, -6, x0=DX, rotulos=[vp.fmt(s) for s in ALC])
vp.chamada((ES1(TER[1]) + DX, 60), (10, 26), f"ES-1: 2 esperas M16 por terça ({len(TER)} terças), y = ±6")
vp.chamada((TER[0] + 140 + DX, 140), (8, 34), f"ES-2: 4 esperas M16 por nó do X ({len(NOS)} nós)")
vp.chamada((ALC[0] + DX, 0), (8, -26), "AL-1 (4 alças de cordoalha)")
vp.chamada((S_TB[0] + DX, -100), (-4, -30), "TB-3 (2 por ponta)")
vp.cota_v([-200, 200], L + DX, 8)

# ------------------------------------------------------------------ ELEVAÇÃO 1:25
ve = pr.vista("ELEVAÇÃO", (80, 622), 25, titulo="ELEVAÇÃO — TS-01",
              subtitulo="peça fabricada reta; pontas a prumo na posição montada (caimento 3 %); COTAS EM CM", unidade="cm")
ve.poli(CONTORNO, "VISTA", fechada=True)
for y in (yfi, yci, ycs, yfs):
    ve.linha((mac + sk(y), y), (L - mac + sk(y), y), "VISTA")
for x in (mac, L - mac):
    ve.linha((x + sk(yfi), yfi), (x + sk(yci), yci), "VISTA"); ve.linha((x + sk(ycs), ycs), (x + sk(yfs), yfs), "VISTA")
for s0 in S_TB:
    for d in (-25, 25):
        ve.linha((s0 + d, 0), (s0 + d + DX, H), "OCULTA")
for s in TER:
    esperas_topo(ve, s, False)
    ve.circulo((ES3(s), 100), 8, "METALICA")
for s in ALC:
    ve.poli([(s - 50, H), (s - 50, H + 110), (s, H + 150), (s + 50, H + 110), (s + 50, H)], "METALICA")
    for d in (-50, 50):
        ve.linha((s + d, H), (s + d - sk(H - 200), 200), "OCULTA")
cgx, cgy = L / 2 + sk(sec.yc * 1000), sec.yc * 1000
ve.circulo((cgx, cgy), 100, "INDICACAO"); ve.linha((cgx - 180, cgy), (cgx + 180, cgy), "INDICACAO")
ve.linha((cgx, cgy - 180), (cgx, cgy + 180), "INDICACAO")
ve.chamada((cgx + 70, cgy + 70), (10, 12), f"CG (s = {ve.fmt(cgx)}; h = {ve.fmt(cgy)})")
ve.chamada((ES3(TER[6]), 100), (8, -22), "ES-3: espera M16 horizontal da mão-francesa, 2 por terça (faces B e D), h = 10")
ve.chamada((S_TB[0] + 12, 700), (-14, 18), "TB-3 Ø50 a prumo")
ve.chamada((S_TB[1] + 12, 700), (14, 18), "TB-3 Ø50 a prumo")
ve.chamada((ES1(TER[3]) + DX, H + 120), (-6, 14), "ES-1 (saliência 12)")
ve.cota_h([0, ALC[0], ALC[1], ALC[2], ALC[3], L], 0, -14)
ve.cota_v([0, 100, H], 0, -10)
ve.cota((L, 0), (L + DX, H), 8, 0)
ve.marcador_corte((TER[5] + 60, -60), (TER[5] + 60 + DX, H + 60), "A", lado=1)
ve.marcador_corte((S_TB[0] + 60, -60), (S_TB[0] + 60 + DX, H + 60), "B", lado=1)
ve.marcador_corte((TER[4] + 200, -60), (TER[4] + 200 + DX, H + 60), "C", lado=1)
ve.marcador_detalhe((300, 400), 650, 1, ang=150, dist=10)
ve.marcador_detalhe((L - 150, 400), 650, 3, ang=30, dist=10)
ve.marcador_detalhe((ALC[1], H), 400, 2, ang=60, dist=6)

# ------------------------------------------------------------------ VISTA INFERIOR 1:25
vi = pr.vista("VISTA INFERIOR", (80, 540), 25, titulo="VISTA INFERIOR — TS-01", subtitulo="fundo da fôrma; COTAS EM CM", unidade="cm")
vi.ret(0, -200, L, 400, "VISTA")
for s0, (a, b) in ((S_TB[0], (40, 240)), (S_TB[1], (L - 127.5, L - 27.5))):
    vi.ret(a, -150, b - a, 300, "OCULTA")
    for yy in TB["y"]:
        vi.circulo((s0, yy), TB["d"] / 2, "METALICA")
for s in TER:
    for yy in (-200, 200):
        vi.circulo((ES3(s), yy), 8, "METALICA")
for x in EST:
    vi.poli([(x - 120, -260), (x + 120, -260), (x, -205)], "INDICACAO", fechada=True)
vi.chamada((S_TB[0], 100), (8, 16), "neoprene NEO-4 200×300×10 (no pilar)")
vi.chamada((S_TB[1], 100), (-8, 16), "neoprene NEO-3 100×300×10 (na I130)")
vi.chamada((EST[0], -260), (30, -22), "calço de estoque/transporte (2x)")
vi.cota_ord([0] + S_TB + [L], -200, -6, x0=0, rotulos=["0", vi.fmt(S_TB[0]), vi.fmt(S_TB[1]), vi.fmt(L)])
vi.cota_v([-200, -100, 100, 200], 0, -8)

# ------------------------------------------------------------------ ESQUEMAS DE IÇAMENTO E ESTOCAGEM 1:100
vq = pr.vista("ESQUEMA DE IÇAMENTO", (60, 418), 100, titulo="IÇAMENTO — DESFORMA E MONTAGEM",
              subtitulo="4 alças AL-1, 2 balancins, cabos verticais; COTAS EM CM", unidade="cm")
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

ve2 = pr.vista("ESQUEMA DE ESTOCAGEM", (60, 348), 100, titulo="ESTOQUE E TRANSPORTE",
               subtitulo="2 calços de 15 cm sob a mesa inferior, sem empilhamento; COTAS EM CM", unidade="cm")
ve2.poli(CONTORNO, "VISTA", fechada=True)
for x in EST:
    ve2.poli([(x - 250, -400), (x + 250, -400), (x, 0)], "INDICACAO", fechada=True)
ve2.cota_h([0] + EST + [L], -400, -6)

# ------------------------------------------------------------------ CORTES 1:10
pts = [(x * 1000, y * 1000) for x, y in sec.pts]


def cordoalhas(v):
    for x in P["x_cord"]:
        v.ponto_barra((x, P["y1"]), 12.7, "ARM_PROT_SECAO")
    for x in P["x_cord2"]:
        v.ponto_barra((x, P["y2"]), 12.7, "ARM_PROT_SECAO")


def espera_mf(v):
    for sg in (-1, 1):
        x0 = sg * 200
        v.ret(min(x0, x0 - sg * 110), 92, 110, 16, "METALICA")            # trecho embutido (hef 110)
        v.ret(min(x0, x0 + sg * 60), 92, 60, 16, "METALICA")              # saliência 60
        xa = x0 - sg * 110 - (6 if sg > 0 else 0)
        v.chapa(xa, 80, 6, 40, 0.25)                                       # arruela 40×40×6 + porca na ponta


def corte_I(nome, org, sub, no):
    v = pr.vista(nome, org, 10, titulo=nome, subtitulo=sub, unidade="cm")
    v.poli(pts, "CORTADO", fechada=True); v.hachura(pts, "AR-CONC", 0.03)
    cordoalhas(v)
    for yy in (-60, 60):                                                   # ES-1 (2 M16, hef 150 + gancho, saliência 120)
        v.ret(yy - 8, H - 150, 16, 270, "METALICA")
        v.poli([(yy - 8, H - 150), (yy - 8 + (40 if yy < 0 else -40), H - 175)], "METALICA")
    v.ret(-110, H + 10, 220, 290, "OCULTA")                                # ST-1P montado na obra (tracejado)
    if no:
        for yy in (-140, 140):                                             # ES-2 (hef 110 + grampo U Ø10)
            v.ret(yy - 8, H - 110, 16, 160, "METALICA")
        v.poli([(-170, H - 130), (-170, H - 60), (170, H - 60), (170, H - 130)], "ARM_TRANSV")
    espera_mf(v)
    v.cota_h([-200, -60, 60, 200], H, 12 if not no else 16)
    v.cota_v([0, P["y2"], H], -200, -12)
    v.cota_v([0, 100], 200, 22, total=False)
    v.cota_v([H, H + 120], 200, 12, total=False)
    return v


va = corte_I("CORTE A-A", (118, 105), "terça comum: ES-1 + ES-3; COTAS EM CM", False)
va.chamada((60, H + 60), (16, 20), "ES-1: 2 barras roscadas M16 A36, hef 15 + gancho, saliência 12 (ST-1P parafusado na obra)")
va.chamada((200, 100), (14, -14), "ES-3: M16 horizontal, hef 11, saliência 6 (mão-francesa)")
va.chamada((40, P["y2"]), (20, 30), f"{P['n_cord']} cord. Ø12,7 (5 a 5,5 + 3 a 10 cm)")

vc = corte_I("CORTE C-C", (292, 105), "nó do X: ES-1 + 4 ES-2 + ES-3; COTAS EM CM", True)
vc.chamada((140, H + 40), (14, 20), "ES-2: M16 hef 11 + grampo U Ø10 (orelha OR-X)")
vc.cota_h([-140, 140], H, 32, total=False)

vb = pr.vista("CORTE B-B", (468, 105), 10, titulo="CORTE B-B", subtitulo="apoio: tubos TB-3 entre as cordoalhas; COTAS EM CM", unidade="cm")
rb = [(-200, 0), (200, 0), (200, H), (-200, H)]
vb.poli(rb, "CORTADO", fechada=True); vb.hachura(rb, "AR-CONC", 0.03)
for yy in TB["y"]:
    vb.ret(yy - 25, 0, 50, H, "METALICA")
cordoalhas(vb)
vb.ret(-150, -10, 300, 10, "VISTA")
vb.chamada((100, 500), (16, 10), "TB-3 tubo Ø50,8×2,0, L = 90 (passante, grauteado)")
vb.chamada((-150, -5), (-14, -12), "neoprene NEO-4 300×200×10")
vb.chamada((-155, P["y1"]), (-16, 22), "cordoalhas fora da faixa dos tubos (|x| ≤ 4 e 15,5)")
vb.cota_h([-200, -125, -75, 75, 125, 200], 0, -16, total=False)
vb.cota_h([-200, 200], H, 10)
vb.cota_v([-10, 0, H], 200, 12)

# ------------------------------------------------------------------ DETALHE 1 — apoio no assento do pilar lateral (1:10)
d1 = pr.vista("DETALHE 1", (630, 120), 20, titulo="DETALHE 1 — APOIO NO ASSENTO DO PILAR (P1/P2)",
              subtitulo="posição montada; assento no recuo, topo a 3 %; COTAS EM CM", unidade="cm")
LX = 1500
d1.poli([(LX, 0), (25, 0), (25 + DX, H), (LX + DX, H)], "VISTA")
d1.interrupcao((LX, 0), (LX + DX, H))
for y in (yfi, yci, ycs, yfs):
    d1.linha((25 + mac + sk(y), y), (LX + sk(y), y), "VISTA")
d1.linha((25 + mac + sk(yfi), yfi), (25 + mac + sk(yci), yci), "VISTA"); d1.linha((25 + mac + sk(ycs), ycs), (25 + mac + sk(yfs), yfs), "VISTA")
s0 = 25 + TB["s_ext"]
for d in (-25, 25):
    d1.linha((s0 + d, 0), (s0 + d + DX, H), "OCULTA")
d1.ret(s0 - 100, -10, 200, 10, "VISTA")                                    # neoprene NEO-4
d1.ret(s0 - 12.5, -300, 25, 600, "METALICA")                               # pino PN-3 Ø25 (300 no pilar)
cab = [(-300, -700), (0, -700), (0, H + 300), (-300, H + 300)]             # cabeça 30 cm (sobe até a platibanda)
d1.poli(cab, "CORTADO", fechada=True); d1.hachura(cab, "AR-CONC", 0.03)
d1.interrupcao((-300, H + 300), (0, H + 300))
corpo = [(0, -700), (300, -700), (300, -10), (0, -10)]                     # assento (recuo) do corpo do pilar
d1.poli(corpo, "CORTADO", fechada=True); d1.hachura(corpo, "AR-CONC", 0.03)
d1.cota_h([0, s0, 300], -10, -24, total=False)
d1.cota_v([-10, 0, H], LX + DX, 10, total=False)
d1.chamada((12, 400), (-14, 12), "folga 2,5 (mastique)")
d1.chamada((s0, 450), (16, 30), "TB-3 Ø50 a prumo, grauteado na montagem")
d1.chamada((s0 + 60, -5), (26, -10), "NEO-4 200×300×10 c/ 2 furos Ø35")
d1.chamada((s0, -200), (16, -16), "2 pinos PN-3 Ø25 CA-50 (pilar), y = ±10")
d1.chamada((-150, 600), (-12, 8), "cabeça do pilar 40 × 30")
d1.chamada((200, -400), (10, -10), "assento: apoio útil 27,5")

# ------------------------------------------------------------------ DETALHE 3 — apoio no topo da I130 (1:10)
d3 = pr.vista("DETALHE 3", (850, 120), 20, titulo="DETALHE 3 — APOIO NO TOPO DA I130 / PILAR CENTRAL",
              subtitulo="pontas das 2 TS-01 a 3,75 do eixo C; COTAS EM CM", unidade="cm")
for sg in (-1, 1):
    pe = sg * 37.5
    pf = sg * 1200
    d3.poli([(pf, 0), (pe, 0), (pe, H), (pf, H)], "VISTA")
    sc = sg * (37.5 + TB["s_cen"])
    for d in (-25, 25):
        d3.linha((sc + d, 0), (sc + d, H), "OCULTA")
    d3.ret(sc - 50, -10, 100, 10, "VISTA")
    d3.ret(sc - 10, -300, 20, 600, "METALICA")
d3.interrupcao((-1200, 0), (-1200, H)); d3.interrupcao((1200, 0), (1200, H))
i130 = [(-200, -900), (200, -900), (200, -10), (-200, -10)]
d3.poli(i130, "CORTADO", fechada=True); d3.hachura(i130, "AR-CONC", 0.03)
d3.linha((0, -1000), (0, H + 150), "EIXO")
d3.cota_h([-115, 115], -10, -24, total=False)
d3.chamada((115, -5), (18, -10), "NEO-3 100×300×10 c/ 2 furos Ø30")
d3.chamada((-115, -200), (-16, -16), "2 pinos PN-5 Ø20 por TS-01 (na I130), y = ±10")
d3.chamada((115, 450), (16, 20), "TB-3 Ø50 grauteado")
d3.chamada((0, -500), (14, -6), "mesa superior da I130 (b 40)")

# ------------------------------------------------------------------ DETALHE 2 — alça AL-1 (1:10)
d2 = pr.vista("DETALHE 2", (720, 300), 10, titulo="DETALHE 2 — ALÇA AL-1", subtitulo="laço de cordoalha Ø12,7 CP-190 RB; COTAS EM CM", unidade="cm")
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

# ------------------------------------------------------------------ ISOMÉTRICO
pr.imagem(280, 240, 640, 488, "/home/claude/letsara/pranchas/ISO-TS01-geral-crop.png", "ISOMÉTRICO — TS-01",
          "modelo 3D da peça com esperas (sem escala)")

# ------------------------------------------------------------------ coluna da direita
x0, y = pr.quadro[2] - 180, pr.quadro[3] - 6
nn = len(NOS)
ins = [["AL-1", "Alça laço cordoalha Ø12,7, 2 pernas 700", 4, "ver planta"],
       ["TB-3", "Tubo Ø50,8×2,0 L=900, passante, a prumo", 4, "2 por ponta, y = ±100"],
       ["ES-1", "Barra roscada M16 L=330, gancho, sai 120", 2 * len(TER), "2 por terça, y = ±60"],
       ["ES-2", "Barra roscada M16 L=220, gancho, sai 50 + grampo U Ø10", 4 * nn, "4 por nó do X"],
       ["ES-3", "Barra roscada M16 L=170, sai 60, porca + arruela", 2 * len(TER), "faces B e D, h = 100"]]
y = pr.tabela(x0, y, "INSERTOS (DETALHES NA FOLHA 03) — mm", ["MARCA", "DESCRIÇÃO", "QT", "POSIÇÃO"], ins, [16, 108, 10, 46])
qd = [["MARCA", P["marca"], "QUANTIDADE", f"{P['qtd']}"],
      ["COMPRIMENTO", f"{L/10:.1f} cm (fundo)".replace(".", ","), "PONTAS", f"a prumo (desl. {DX/10:.1f} cm)".replace(".", ",")],
      ["VOLUME", f"{f(V,3)} m³", "PESO", f"{f(peso,1)} kN ({f(peso/9.81,2)} t)"],
      ["CONCRETO", f"C{P['fck']} / fckj {P['fckj']}", "PROTENSÃO", f"{P['n_cord']} cord. Ø12,7"],
      ["APOIO EXTERNO", "assento do pilar, 27,5 cm", "APOIO CENTRAL", "topo I130, 16,25 cm"]]
y = pr.tabela(x0, y - 4, "QUADRO DA PEÇA", ["ITEM", "VALOR", "ITEM", "VALOR"], qd, [30, 60, 30, 60])
mn = [["Desforma / içamento", "4 alças AL-1 + 2 balancins", f"{f(ALCA_Fd,1)} kN por alça"],
      ["Estoque / transporte", f"2 calços a {EST[0]/10:.0f} cm das pontas", f"{f(peso/2,1)} kN por calço"],
      ["Liberação", f"fckj ≥ {P['fckj']} MPa", "—"]]
y = pr.tabela(x0, y - 4, "MANUSEIO", ["FASE", "APOIO", "CARGA"], mn, [50, 70, 60])
notas = [f"Fabricar a peça reta com {f(L/10,1)} cm de fundo; cabeceiras inclinadas 3 % (topo deslocado {f(DX/10,1)} cm) para ficarem a prumo na montagem.",
         "Cotas ordenadas a partir do ponto 0 = encontro da face da ponta esquerda (a prumo, lado do pilar P1/P2) com o plano do fundo.",
         "Sem dentes Gerber: a viga apoia direto no assento do pilar lateral (recuo, NEO-4) e no topo da I130 / pilar central (NEO-3), sempre com 2 pinos grauteados nos tubos TB-3.",
         "Cordoalhas: 5 a 5,5 cm (x = 0, ±4, ±15,5) e 3 a 10 cm (x = 0, ±4); as 2 de 10 cm em x = ±4 isoladas com bainha nos 3,00 m de cada ponta (folha 02).",
         "Esperas ES-1/ES-2/ES-3 com gabarito de aço preso na fôrma (tolerância ±3 mm); rosca protegida com fita até a montagem. Ligações da cobertura todas parafusadas, sem solda (ND-LET-COB01/02).",
         f"Desforma, içamento e montagem só pelas 4 alças AL-1 com 2 balancins e cabos verticais; liberar com fckj ≥ {P['fckj']} MPa.",
         "Estoque e transporte sobre 2 calços de madeira de 15 cm sob a mesa inferior, sem empilhamento; as esperas ES-3 sobressaem 6 cm das faces laterais.",
         f"Terças a cada {f(PASSO_T/10,1)} cm ({len(TER)} por viga). Esperas e barras roscadas A36, galvanizadas a fogo. Concreto em cm; aço em mm.",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(x0, y - 4, notas, 180)
pr.posicoes_desenho.clear()
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-TS01-1")
for a in avisos:
    print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
