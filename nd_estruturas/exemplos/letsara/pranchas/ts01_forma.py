import renomear as RN
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
pr.revisao("04", "16/10/2026", "NBR 9062: TOLERÂNCIA DE COMPRIMENTO ±10 mm (FOLGA CENTRAL 19 mm); ESTABILIDADE LATERAL")
pr.revisao("05", "17/10/2026", "TERÇAS Z CONTÍNUAS SEM MÃO-FRANCESA: RETIRADAS AS ESPERAS ES-3")
pr.revisao("06", "17/10/2026", "15 ESPAÇOS DE TERÇA (1ª A 40 cm DA CALHA); ES-2 SÓ NOS 3 NÓS DO X; GRAMPO NAS ES-1; TS-01A COM IT-P")
pr.cabecalho_peca("\x01" + RN.lista(RN.nomes_de("TS-01") + RN.nomes_de("TS-01A") + RN.nomes_de("TS-01B")), f"VIGA DE COBERTURA I90 PROTENDIDA — SEÇÃO I90 (b 40, bw 15, h 90) · L = {L/10:.1f} cm (entre pontas, a prumo) · 14 PEÇAS".replace(".", ","),
                  f"PESO {f(peso/9.81,1)} t   ·   VOLUME {f(V,2)} m³   ·   C50 / fckj 35   ·   {P['n_cord']} cord. Ø12,7 CP-190 RB   ·   sem dentes: apoio direto em neoprene   ·   caimento 3 %", 560)
mac, yfi, yci, ycs, yfs = P["x_mac"], 150, 230, 700, 780
TER, NOS, ALC, EST = P["tercas"], P["nos"], P["alcas"], P["estoque"]
t3 = DX / H
sk = lambda h: h * t3                      # ponta a prumo: deslocamento ao longo da peça na altura h
CUN = P["cunha"]                                       # rev04: cunha no fundo das pontas (NBR 9062:2017 7.2.1.6 — aparelho horizontal)
LC, EC = CUN["L"], CUN["e"]
# ponta baixa (s = 0, lado A da meia água): rebaixo de EC na ponta a 0 em LC; ponta alta (s = L): 0 na ponta a EC em L − LC (degrau)
CONTORNO = [(sk(EC), EC), (LC, 0), (L - LC, 0), (L - LC, EC), (L, 0), (L + DX, H), (DX, H)]
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
# rev08 (DEC-036): TS-01B (linha 2) — ST-1P4 na 1ª e na última terça: +2 ES-1 a 155 mm antes do eixo da terça (aba de 200)
for s in (TER[0], TER[-1]):
    for yy in (-60, 60):
        vp.circulo((ES1(s) - 80 + DX, yy), 8, "OCULTA")
vp.chamada((ES1(TER[-1]) - 80 + DX, -60), (-10, -26), "só TS-01B: +2 ES-1 (ST-1P4) na 1ª e na última terça, 15,5 antes do eixo")

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
for s in ALC:
    ve.poli([(s - 50, H), (s - 50, H + 110), (s, H + 150), (s + 50, H + 110), (s + 50, H)], "METALICA")
    for d in (-50, 50):
        ve.linha((s + d, H), (s + d - sk(H - 200), 200), "OCULTA")
cgx, cgy = L / 2 + sk(sec.yc * 1000), sec.yc * 1000
ve.circulo((cgx, cgy), 100, "INDICACAO"); ve.linha((cgx - 180, cgy), (cgx + 180, cgy), "INDICACAO")
ve.linha((cgx, cgy - 180), (cgx, cgy + 180), "INDICACAO")
ve.chamada((cgx + 70, cgy + 70), (10, 12), f"CG (s = {ve.fmt(cgx)}; h = {ve.fmt(cgy)})")
ve.chamada((S_TB[0] + 12, 700), (-14, 18), "TB-3 Ø50 a prumo")
ve.chamada((S_TB[1] + 12, 700), (14, 18), "TB-3 Ø50 a prumo")
ve.chamada((ES1(TER[3]) + DX, H + 120), (-6, 14), "ES-1 (saliência 12)")
ve.cota_h([0, ALC[0], ALC[1], ALC[2], ALC[3], L], 0, -14)
ve.cota_v([0, 100, H], 0, -10)
ve.marcador_corte((TER[5] + 60, -470), (TER[5] + 60 + DX, H + 60), "A", lado=1)
ve.marcador_corte((S_TB[0] + 60, -470), (S_TB[0] + 60 + DX, H + 60), "B", lado=1)
ve.marcador_corte((TER[4] + 200, -470), (TER[4] + 200 + DX, H + 60), "C", lado=1)
ve.marcador_detalhe((300, 400), 650, 1, ang=150, dist=10)
ve.marcador_detalhe((L - 150, 400), 650, 3, ang=30, dist=10)
ve.marcador_detalhe((ALC[1], H), 400, 2, ang=60, dist=6)

# ------------------------------------------------------------------ VISTA INFERIOR 1:25
vi = pr.vista("VISTA INFERIOR", (80, 540), 25, titulo="VISTA INFERIOR — TS-01", subtitulo="fundo da fôrma; COTAS EM CM", unidade="cm")
vi.ret(0, -200, L, 400, "VISTA")
for a, b in ((0, LC), (L - LC, L)):
    vi.hachura([(a, -200), (b, -200), (b, 200), (a, 200)], "ANSI31", 0.25)
for s0, (a, b) in ((S_TB[0], (25, 225)), (S_TB[1], (L - 127.5, L - 27.5))):
    vi.ret(a, -150, b - a, 300, "OCULTA")
    for yy in TB["y"]:
        vi.circulo((s0, yy), TB["d"] / 2, "METALICA")
for x in EST:
    vi.poli([(x - 120, -260), (x + 120, -260), (x, -205)], "INDICACAO", fechada=True)
vi.chamada((LC / 2, 150), (10, 18), f"cunha: fundo rebaixado {EC} → 0 mm (ponta baixa)")
vi.chamada((L - LC / 2, 150), (-10, 18), f"cunha: fundo rebaixado 0 → {EC} mm (ponta alta)")
vi.chamada((S_TB[0], 100), (14, 30), "NEO-4 (pilar) ou NEO-3 (I130)")
vi.chamada((S_TB[1], 100), (-14, 30), "NEO-3 (I130) ou NEO-4 (pilar)")
vi.chamada((EST[0], -260), (30, -22), "calço de estoque/transporte (2x)")
vi.cota_ord([0, S_TB[0], LC, L - LC, S_TB[1], L], -200, -6, x0=0, rotulos=["0", vi.fmt(S_TB[0]), vi.fmt(LC), vi.fmt(L - LC), vi.fmt(S_TB[1]), vi.fmt(L)])
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
    v.cota_h([-200, -140, -60, 60, 140, 200] if no else [-200, -60, 60, 200], H, 12 if not no else 16)
    v.cota_v([0, P["y2"], H], -200, -12)
    v.cota_v([H, H + 120], 200, 12, total=False)
    return v


va = corte_I("CORTE A-A", (118, 105), "apoio de terça: ES-1; COTAS EM CM", False)
va.chamada((60, H + 60), (16, 20), "ES-1: 2 M16 A36 hef 15 + gancho, sai 12 (ST-1P)")
va.chamada((40, P["y2"]), (20, 30), f"{P['n_cord']} cord. Ø12,7 (5 a 5,5 + 3 a 10 cm)")

vc = corte_I("CORTE C-C", (292, 105), "nó do X: ES-1 + 4 ES-2; COTAS EM CM", True)
vc.chamada((140, H + 40), (14, 20), "ES-2: M16 hef 11 + grampo U Ø10")

vb = pr.vista("CORTE B-B", (468, 105), 10, titulo="CORTE B-B", subtitulo="apoio: tubos TB-3 entre as cordoalhas; COTAS EM CM", unidade="cm")
rb = [(-200, 0), (200, 0), (200, H), (-200, H)]
vb.poli(rb, "CORTADO", fechada=True); vb.hachura(rb, "AR-CONC", 0.03)
for yy in TB["y"]:
    vb.ret(yy - 25, 0, 50, H, "METALICA")
cordoalhas(vb)
vb.ret(-150, -10, 300, 10, "VISTA")
vb.chamada((100, 500), (16, 54), "TB-3 Ø50,8×2,0 L = 90, passante, grauteado")
vb.chamada((-150, -5), (-14, -12), "NEO-4 300×200×10")
vb.chamada((-155, P["y1"]), (-16, 22), "cord. fora dos tubos")
vb.cota_h([-200, -125, -75, 75, 125, 200], 0, -16, total=False)
vb.cota_h([-200, 200], H, 10)
vb.cota_v([-10, 0, H], 200, 12)

# ------------------------------------------------------------------ DETALHES 1, 3 e 4 — apoios na POSIÇÃO MONTADA (1:20)
# z = 0 na face de apoio horizontal da ponta; viga com caimento 3 %; pontas e tubos a prumo; assentos horizontais
HV = H * (1 + 0.03 ** 2) ** 0.5
LX = 1500
PIN, NEOX = TB["s_ext"], 125                      # pino a 7,75 cm da ponta (os 4 apoios); centro do NEO-4 a 12,5 cm


def viga_montada(v, x_ponta, sg, z_ponta_fundo, zface=0.0):
    """Contorno da TS-01 montada: ponta em x_ponta, corpo para o lado sg (+1 direita, −1 esquerda); fundo da viga sem rebaixo
    em z_fundo(x) = z_ponta_fundo + 0,03·(x − x_ponta); rebaixo horizontal em z = 0 entre a ponta e x_ponta + sg·LC."""
    zf_ = lambda x: z_ponta_fundo + 0.03 * (x - x_ponta)
    xe = x_ponta + sg * LX
    xc = x_ponta + sg * LC
    fundo = [(x_ponta, zface), (xc, zface)] + ([(xc, zf_(xc))] if abs(zf_(xc) - zface) > 0.5 else []) + [(xe, zf_(xe))]
    pts = fundo + [(xe, zf_(xe) + HV), (x_ponta, zf_(x_ponta) + HV)]
    v.poli(pts, "VISTA", fechada=True)
    for y in (yfi, yci, ycs, yfs):
        v.linha((x_ponta + sg * mac, zf_(x_ponta + sg * mac) + y), (xe, zf_(xe) + y), "VISTA")
    v.interrupcao((xe, zf_(xe)), (xe, zf_(xe) + HV))
    xt = x_ponta + sg * PIN
    for d in (-25, 25):
        v.linha((xt + d, zface), (xt + d, zf_(xt + d) + HV), "OCULTA")
    return zf_, xt


# DETALHE 1 — ponta baixa no pilar P1 (eixo A)
d1 = pr.vista("DETALHE 1", (630, 120), 20, titulo="DETALHE 1 — APOIO NO PILAR P1 (PONTA BAIXA)",
              subtitulo="posição montada; assento horizontal no recuo; cunha 9 → 0 mm; COTAS EM CM", unidade="cm")
zf1, xt1 = viga_montada(d1, 25, 1, -EC)
d1.chapa(25 + NEOX - 100, -10, 200, 10)                                      # NEO-4 horizontal
d1.ret(xt1 - 12.5, -300, 25, 600, "METALICA")                               # PN-3
cab = [(-300, -700), (0, -700), (0, H + 300), (-300, H + 300)]
d1.poli(cab, "CORTADO", fechada=True); d1.hachura(cab, "AR-CONC", 0.03)
d1.interrupcao((-300, H + 300), (0, H + 300))
corpo = [(0, -700), (300, -700), (300, -10), (0, -10)]
d1.poli(corpo, "CORTADO", fechada=True); d1.hachura(corpo, "AR-CONC", 0.03)
d1.cota_h([25, 25 + LC], -10, -24, total=False)
d1.chamada((12, 400), (-20, -6), "folga 2,5 (mastique)")
d1.chamada((xt1, 450), (16, 30), "TB-3 Ø50 a prumo, grauteado")
d1.chamada((25 + NEOX + 60, -5), (30, -26), "NEO-4 200×300×10 horizontal, centro a 12,5 da ponta")
d1.chamada((xt1, -200), (-24, -40), "2 PN-3 Ø25 a 10,25 da face, y = ±10")
d1.chamada((150, 2), (30, -12), f"cunha: face de apoio horizontal ({EC} mm na ponta)")
d1.chamada((-150, 900), (-14, 10), "cabeça do pilar 40 × 30")
d1.chamada((150, -600), (26, -8), f"assento HORIZONTAL +{f(LG['REC'][0], 3)}")

# DETALHE 4 — ponta alta no pilar P2 (eixo E)
d4 = pr.vista("DETALHE 4", (895, 285), 20, titulo="DETALHE 4 — APOIO NO PILAR P2 (PONTA ALTA)",
              subtitulo="posição montada; assento horizontal; cunha 0 → 9 mm com degrau; COTAS EM CM", unidade="cm")
zf4, xt4 = viga_montada(d4, -25, -1, 0)
d4.chapa(-25 - NEOX - 100, -10, 200, 10)
d4.ret(xt4 - 12.5, -300, 25, 600, "METALICA")
cab = [(0, -700), (300, -700), (300, H + 300), (0, H + 300)]
d4.poli(cab, "CORTADO", fechada=True); d4.hachura(cab, "AR-CONC", 0.03)
d4.interrupcao((0, H + 300), (300, H + 300))
corpo = [(-300, -700), (0, -700), (0, -10), (-300, -10)]
d4.poli(corpo, "CORTADO", fechada=True); d4.hachura(corpo, "AR-CONC", 0.03)
d4.cota_h([-25 - LC, -25], -10, -24, total=False)
d4.chamada((-25 - LC, -EC / 2), (-30, -10), f"degrau de {EC} mm no fim da cunha")
d4.chamada((-25 - NEOX - 60, -5), (-24, -24), "NEO-4 200×300×10 horizontal")
d4.chamada((-150, -500), (-34, -38), f"assento HORIZONTAL +{f(LG['REC'][1], 3)}")
d4.chamada((xt4, 450), (-16, 26), "TB-3 a prumo / 2 PN-3 Ø25")

# DETALHE 3 — topo da I130 / pilar central: ponta alta da TS-01 do lado A e ponta baixa da TS-01 do lado E
DG = round(LG["DEGRAU_C"] * 1000)
d3 = pr.vista("DETALHE 3", (850, 120), 20, titulo="DETALHE 3 — APOIO NO TOPO DA I130 / PILAR CENTRAL",
              subtitulo=f"posição montada; topo horizontal em 2 níveis (degrau {DG} mm no eixo C); COTAS EM CM", unidade="cm")
zl, xl = viga_montada(d3, -37.5, -1, 0)                       # lado A: ponta alta
zr, xr = viga_montada(d3, 37.5, 1, DG - EC, DG)               # lado E: ponta baixa (face de apoio em z = DG)
d3.chapa(-37.5 - PIN - 50, -10, 100, 10); d3.chapa(37.5 + PIN - 50, DG - 10, 100, 10)
d3.ret(xl - 10, -300, 20, 600, "METALICA"); d3.ret(xr - 10, DG - 300, 20, 600, "METALICA")
i130 = [(-200, -900), (200, -900), (200, DG - 10), (0, DG - 10), (0, -10), (-200, -10)]
d3.poli(i130, "CORTADO", fechada=True); d3.hachura(i130, "AR-CONC", 0.03)
d3.linha((0, -1000), (0, H + 150), "EIXO")
d3.cota_h([-115, 0, 115], -10, -24, total=False)
d3.chamada((115, DG - 5), (18, -10), "NEO-3 100×300×10 c/ 2 furos Ø30 (horizontais)")
d3.chamada((-115, -200), (-34, -38), "2 PN-5 Ø20 por TS-01, y = ±10")
d3.chamada((100, DG - 10), (16, -24), f"topo +{f(LG['Z_TOPO_I130_DIR'], 3)} (lado E)")
d3.chamada((-100, -10), (-40, -10), f"topo +{f(LG['Z_TOPO_I130'], 3)} (lado A)")
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
d2.chamada((50, 160), (30, -10), "pontas desfiadas")

# ------------------------------------------------------------------ ISOMÉTRICO
pr.imagem(280, 248, 640, 486, "/home/claude/letsara/pranchas/ISO-TS01-geral-crop.png", "ISOMÉTRICO — TS-01",
          "modelo 3D da peça com esperas (sem escala)")

# ------------------------------------------------------------------ coluna da direita
x0, y = pr.quadro[2] - 180, pr.quadro[3] - 6
nn = len(NOS)
ins = [["AL-1", "Alça laço cordoalha Ø12,7, 2 pernas 700", 4, "ver planta"],
       ["TB-3", "Tubo Ø50,8×2,0 L=900, passante, a prumo", 4, "a 77,5 das pontas, y = ±100"],
       ["ES-1", "Barra roscada M16 L=330, gancho, sai 120 + grampo U Ø10", 2 * len(TER), "2 por terça, y = ±60"],
       ["ES-1", "Só TS-01B (linha 2): +4 ES-1 do ST-1P4 + grampo U Ø10", 4, "1ª e última terça, s − 15,5"],
       ["ES-2", "Barra roscada M16 L=220, gancho, sai 50 + grampo U Ø10", 4 * nn, f"4 por nó do X ({nn} nós)"],
       ["IT-P", "Só TS-01A (linha 4): inserto rosqueado M16 hef 80 no fundo", 6, "fundo, ver nota 11"]]
y = pr.tabela(x0, y, "INSERTOS (DETALHES NA ND-LET-TS01-3) — mm", ["MARCA", "DESCRIÇÃO", "QT", "POSIÇÃO"], ins, [16, 108, 10, 46])
qd = [["MARCA", P["marca"], "QUANTIDADE", f"{P['qtd']}"],
      ["COMPRIMENTO", f"{L/10:.1f} cm (fundo)".replace(".", ","), "PONTAS", f"a prumo (desl. {DX/10:.1f} cm)".replace(".", ",")],
      ["VOLUME", f"{f(V,3)} m³", "PESO", f"{f(peso,1)} kN ({f(peso/9.81,2)} t)"],
      ["CONCRETO", f"C{P['fck']} / fckj {P['fckj']}", "PROTENSÃO", f"{P['n_cord']} cord. Ø12,7"],
      ["APOIO EXTERNO", "assento do pilar, 27,5 cm", "APOIO CENTRAL", "topo I130, 16,25 cm"],
      ["CUNHAS", f"{LC/10:.0f} cm, 0 → {EC} mm", "TUBOS TB-3", f"a {f(PIN/10, 2)} cm das 2 pontas"]]
y = pr.tabela(x0, y - 4, "QUADRO DA PEÇA", ["ITEM", "VALOR", "ITEM", "VALOR"], qd, [30, 60, 30, 60])
mn = [["Desforma / içamento", "4 alças AL-1 + 2 balancins", f"{f(ALCA_Fd,1)} kN por alça"],
      ["Estoque / transporte", f"2 calços a {EST[0]/10:.0f} cm das pontas", f"{f(peso/2,1)} kN por calço"],
      ["Liberação", f"fckj ≥ {P['fckj']} MPa", "—"]]
y = pr.tabela(x0, y - 4, "MANUSEIO", ["FASE", "APOIO", "CARGA"], mn, [50, 70, 60])
notas = ["Tolerância de comprimento de projeto ±10 mm (mais apertada que a Tab. 2 da NBR 9062:2017 — 5.2.1.2): necessária para a folga de 19 mm entre as pontas das duas TS-01 sobre a I130; seção −5/+10 mm, linearidade ±L/1000, insertos ±15 mm. Estabilidade lateral no içamento: L/bf 49 ≤ 50 (6.1).",
         f"Fabricar a peça reta com {f(L/10,1)} cm de fundo; cabeceiras inclinadas 3 % (topo deslocado {f(DX/10,1)} cm) para ficarem a prumo na montagem.",
         "Cotas ordenadas a partir do ponto 0 = encontro da face da ponta esquerda (a prumo, lado do pilar P1/P2) com o plano do fundo.",
         "Sem dentes Gerber: a viga apoia direto no assento do pilar lateral (recuo, NEO-4) e no topo da I130 / pilar central (NEO-3), com 2 pinos grauteados nos tubos TB-3, a 7,75 cm das duas pontas (peça simétrica: a mesma TS-01 serve às duas meias águas, sempre com a ponta baixa para o lado A).",
         f"CUNHAS no fundo das duas pontas (NBR 9062:2017 7.2.1.6 — aparelho de apoio horizontal): calço de aço em cunha 3 % fixado no fundo da fôrma, {LC/10:.0f} cm × 40 cm; ponta baixa rebaixo {EC} → 0 mm, ponta alta 0 → {EC} mm (degrau de {EC} mm). Na montagem a face de apoio fica horizontal sobre o neoprene e sobre o assento horizontal.",
         "Cordoalhas: 5 a 5,5 cm (x = 0, ±4, ±15,5) e 3 a 10 cm (x = 0, ±4); as 2 de 10 cm em x = ±4 isoladas com bainha nos 3,00 m de cada ponta (faixa de armação abaixo).",
         "Esperas ES-1/ES-2 com gabarito de aço preso na fôrma (tolerância ±3 mm); rosca protegida com fita até a montagem. Ligações da cobertura todas parafusadas, sem solda (ND-LET-COB01/02).",
         f"Desforma, içamento e montagem só pelas 4 alças AL-1 com 2 balancins e cabos verticais; liberar com fckj ≥ {P['fckj']} MPa.",
         "Estoque e transporte sobre 2 calços de madeira de 15 cm sob a mesa inferior, sem empilhamento.",
         f"Terças a cada {f(PASSO_T/10,1)} cm ({len(TER)} por viga). Esperas e barras roscadas A36, galvanizadas a fogo. Concreto em cm; aço em mm.",
         "TS-01A (as 2 peças da linha 4): igual à TS-01 + 6 insertos IT-P no fundo (s = 452,0 / 984,8 / 1517,7 cm, y = ±9,75 cm, entre as colunas de cordoalhas) para as cantoneiras CL-P dos pilares dos portões (ND-LET-PG01 a 04).",
         "TS-01B (as 2 peças da linha 2, beirais): igual à TS-01 + 2 ES-1 extras (com grampo U Ø10) na 1ª e na última terça, a 15,5 cm antes do eixo da terça, y = ±6 — recebem o suporte ST-1P4 (aba de 20 cm, 4 esperas; DEC-036). Marcas: TS-01 = 10, TS-01A = 2, TS-01B = 2 (total 14).",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(x0, y - 4, notas, 180)
pr.posicoes_desenho.clear()
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-TS01-1")
for a in avisos:
    print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
