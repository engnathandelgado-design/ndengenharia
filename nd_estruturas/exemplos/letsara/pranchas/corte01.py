"""ND-LET-CT01 — cortes transversais da estrutura (eixos 2 e 3) e detalhes dos apoios da cobertura (A0)."""
import json, math
from prancha_nd import Prancha, _seg_rect

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
LG = json.load(open(AQ + "ligacoes.json"))
f = lambda v, d=3: f"{v:+.{d}f}".replace(".", ",")
I = 0.03
c, sn = 1 / math.sqrt(1 + I * I), I / math.sqrt(1 + I * I)
L_TS = LG["L_TS"] * 1000
XC = 19750.0
X0 = [LG["X_PONTA_ESQ"] * 1000, 2 * XC - LG["X_PONTA_CEN"] * 1000]       # pontas das duas TS-01 (rev03, sem dentes)
zf = lambda x: LG["Z0_TS"] * 1000 + I * x  # fundo da TS-01 (mm, x global em mm)
H = 900.0
t3 = 27.0 / 900.0
Z_TOP_PIL = 10000.0
Z_TOP_C = LG["Z_TOPO_I130"] * 1000                                     # topo da I130 e dos pilares centrais
H_I130 = LG["H_I130"] * 1000
Z_ASS_I130 = LG["Z_ASS_I130"] * 1000
Z_MEZ = [3150.0, 6550.0]
TER = [s * 1000 for s in LG["s_tercas"]]
PAC = LG["platibanda"]["pacote"]
TB = (140.0, L_TS - 77.5)


class Recorte:
    """Desenha numa vista só o que cai dentro de uma janela do modelo (para os detalhes ampliados)."""

    def __init__(self, v, jan=None):
        self.v, self.j = v, jan

    def _dentro(self, p):
        return self.j is None or (self.j[0] <= p[0] <= self.j[2] and self.j[1] <= p[1] <= self.j[3])

    def _clip(self, a, b):
        if self.j is None:
            return a, b
        x0, y0, x1, y1 = self.j
        dx, dy = b[0] - a[0], b[1] - a[1]
        t0, t1 = 0.0, 1.0
        for p, q in ((-dx, a[0] - x0), (dx, x1 - a[0]), (-dy, a[1] - y0), (dy, y1 - a[1])):
            if abs(p) < 1e-12:
                if q < 0:
                    return None
            else:
                t = q / p
                if p < 0:
                    t0 = max(t0, t)
                else:
                    t1 = min(t1, t)
                if t0 > t1:
                    return None
        return (a[0] + t0 * dx, a[1] + t0 * dy), (a[0] + t1 * dx, a[1] + t1 * dy)

    def linha(self, a, b, cam="VISTA"):
        s = self._clip(a, b)
        if s:
            self.v.linha(s[0], s[1], cam)

    def poli(self, pts, cam="VISTA", fechada=False):
        pp = list(pts) + ([pts[0]] if fechada else [])
        for a, b in zip(pp[:-1], pp[1:]):
            self.linha(a, b, cam)

    def ret(self, x, y, w, h, cam="CORTADO"):
        self.poli([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], cam, True)

    def hach(self, pts):
        if all(self._dentro(p) for p in pts):
            self.v.hachura(pts, "AR-CONC", 0.03)


def glob(x0, s, h):
    xb = x0 + s * c
    return (xb - h * sn, zf(xb) + h * c)


def ts(R, x0):
    sk = lambda h: h * t3
    L = L_TS
    cont = [(0, 0), (L, 0), (L + 27, H), (27, H)]
    R.poli([glob(x0, s, h) for s, h in cont], "CORTADO", True)
    for h in (150, 230, 700, 780):
        R.linha(glob(x0, 1200 + sk(h), h), glob(x0, L - 1200 + sk(h), h), "VISTA")
    for s0 in TB:
        R.linha(glob(x0, s0, 0), glob(x0, s0 + 27, H), "EIXO")
    for s in TER:
        xt, zt = glob(x0, s, H)
        R.poli([(xt + 82, zt + 10), (xt, zt + 10), (xt, zt + 312), (xt - 90, zt + 312)], "METALICA")   # terça Z 302
        R.ret(xt - 9.5, zt + 10, 9.5, 290, "METALICA")            # ST-1P (aba vertical)
    zz = H + 10 + 302
    for k_ in ("tp40", "espacador_la", "zipada", "painel_solar"):
        zz += PAC[k_] * 1000
        a, b = glob(x0, -100, zz), glob(x0, L + 100, zz)
        R.linha(a, b, "METALICA")
    a, b = glob(x0, -100, H + 310), glob(x0, L + 100, H + 310)
    R.linha(a, b, "METALICA")


def apoio(R, x, z, larg):
    """Neoprene (10 mm) sob a ponta da TS-01, centrado em x."""
    R.ret(x - larg / 2, z - 10, larg, 10, "METALICA")


def consolo(R, face, lado, z_seat, proj=300, alt=440, inc=I):
    """Consolo sem chanfro (h = dente da viga − neoprene; fundo alinhado ao da viga), topo com inclinação inc passando
    por z_seat no centro do apoio."""
    xa, xb = face, face + lado * proj
    xm = face + lado * (proj - 125)
    zt = lambda x: z_seat + inc * (x - xm)
    pts = [(xa, zt(xa)), (xb, zt(xb)), (xb, zt(xb) - alt), (xa, zt(xa) - alt)]
    R.poli(pts, "CORTADO", True)
    R.hach(pts)


def pilar(R, x, larg, z_top, nome=None):
    pts = [(x - larg / 2, 0), (x + larg / 2, 0), (x + larg / 2, z_top), (x - larg / 2, z_top)]
    R.poli(pts, "CORTADO", True)


REC = tuple(r * 1000 for r in LG["REC"])  # assento da TS-01 no recuo da cabeça dos pilares laterais (rev03)


def pilar_rec(R, x, lado, z_rec):
    """Pilar lateral 40×60 com a cabeça recuada (só os 300 externos sobem acima de z_rec). lado = sentido para dentro."""
    pts = [(x - lado * 300, 0), (x + lado * 300, 0), (x + lado * 300, z_rec), (x, z_rec), (x, Z_TOP_PIL), (x - lado * 300, Z_TOP_PIL)]
    R.poli(pts, "CORTADO", True)


def estrutura(R, eixo):
    pilar_rec(R, 0, 1, REC[0]); pilar_rec(R, 39500, -1, REC[1])
    apoio(R, X0[0] + 140, zf(X0[0] + 140) , 200); apoio(R, 39500 - X0[0] - 140, zf(39500 - X0[0] - 140), 200)
    for xp in (-325 - 50, 39500 + 325 + 50):                          # placas de fechamento 10 cm por fora (folga 25)
        R.ret(xp - 50, 0, 100, Z_TOP_PIL, "VISTA")
    if eixo == 2:
        pilar(R, XC, 400, Z_TOP_C)
        for xm in (9870, 29630):
            pilar(R, xm, 400, Z_MEZ[1])
        faces = [(300, 9670), (10070, 19550), (19950, 29430), (29830, 39200)]
        for zm in Z_MEZ:
            topo = zm - 260                                  # rev04: laje h20 + capa 5 + fita 1; topo da VM = apoio da laje
            _P = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/vm_meio_vaso.json"))["premissas"]
            HV, RC = round(_P["h_pm"] * 1000), round(_P["dente"]["recorte"] * 1000)
            for a, b in faces:
                xa, xb = a + 30, b - 30
                cont = [(xa + 350, topo - HV), (xb - 350, topo - HV), (xb - 350, topo - HV + RC), (xb, topo - HV + RC), (xb, topo), (xa, topo),
                        (xa, topo - HV + RC), (xa + 350, topo - HV + RC)]                         # VM meio vaso com dente (rev04)
                R.poli(cont, "VISTA", True)
                consolo(R, a, 1, topo - HV + RC - 10, proj=350, alt=RC - 10, inc=0); consolo(R, b, -1, topo - HV + RC - 10, proj=350, alt=RC - 10, inc=0)
            R.ret(300, zm - 250, 38900, 200, "VISTA")
            R.ret(300, zm - 50, 38900, 50, "VISTA")
    else:
        sec = [(-200, 0), (200, 0), (200, 250), (75, 330), (75, 1000), (200, 1080), (200, 1300), (-200, 1300), (-200, 1080),
               (-75, 1000), (-75, 330), (-200, 250)]
        base = Z_TOP_C - H_I130
        R.poli([(XC + x, base + y) for x, y in sec], "CORTADO", True)
        R.hach([(XC + x, base + y) for x, y in sec])
    for sg in (-1, 1):
        apoio(R, XC + sg * 115, Z_TOP_C + sg * 0, 100)
    for x0 in X0:
        ts(R, x0)


def nivel(v, x, z, txt, lado=1):
    v.linha((x, z), (x + lado * 900, z), "INDICACAO")
    v.poli([(x + lado * 450 - 150, z + 260), (x + lado * 450 + 150, z + 260), (x + lado * 450, z)], "INDICACAO", True)
    v.texto((x + lado * 650, z + 80), txt, "nota", alinh="BOTTOM_LEFT" if lado > 0 else "BOTTOM_RIGHT")


pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="CORTES TRANSVERSAIS DA ESTRUTURA (EIXOS 2 E 3) E APOIOS DA COBERTURA",
                        desenho="ND-LET-CT01", folha="01/01", fase="PARA APROVAÇÃO", rev="03"))
pr.revisao("01", pr.dados["data"], "geometria do R01 (79,35 × 39,50 m); cabeça dos pilares laterais recuada; placas 15 cm por fora")
pr.revisao("02", pr.dados["data"], "CONSOLOS SEM CHANFRO (FUNDO ALINHADO À VIGA); VM I90 COM DENTE 45×30; LAJE 8 Ø12,7")
pr.revisao("03", "14/10/2026", "TS-01 SEM DENTES (APOIO NO RECUO E NO TOPO DA I130); PACOTE COM PAINÉIS; COBERTURA REBAIXADA; PLACAS 10 cm")
pr.revisao("04", "16/10/2026", "NBR 9062: SEM VT; MEZANINO EM MEIO VASO COM DENTE")
pr.revisao("05", "17/10/2026", "TERÇAS Z 302 CONTÍNUAS POR TRANSPASSE, SEM MÃO-FRANCESA")
z_tel = lambda x: zf(x) + (H + 10 + 300 + sum(PAC.values()) * 1000) * c       # topo dos painéis solares
for k, (eixo, org, nome) in enumerate(((2, (70, 590), "CORTE 2-2"), (3, (70, 330), "CORTE 3-3"))):
    v = pr.vista(nome, org, 50, titulo=f"{nome} — EIXO {eixo} (y = {[9.65, 19.725][k]:.3f} m)".replace(".", ","),
                 subtitulo="olhando para o eixo 9; cotas de nível em metros" + ("; mezanino entre os eixos 1 e 2" if eixo == 2 else ""))
    R = Recorte(v)
    v.linha((-1500, 0), (41000, 0), "TERRENO")
    estrutura(R, eixo)
    for x, nomex in ((0, "A"), (9870, "B"), (19750, "C"), (29630, "D"), (39500, "E")):
        v.linha((x, -900), (x, 11600), "EIXO")
        v.circulo((x, -1300), 400, "INDICACAO"); v.texto((x, -1300), nomex, "sub", alinh="MIDDLE_CENTER")
    v.cota_h([0, 9870, 19750, 29630, 39500], 0, -40)
    nivel(v, -300, 0, "±0,000", -1)
    nivel(v, 600, REC[0], f"assento TS {f(REC[0] / 1000)}")
    nivel(v, 300, Z_TOP_PIL, f"platibanda {f(Z_TOP_PIL / 1000)}", -1)
    nivel(v, 38900, REC[1], f"assento TS {f(REC[1] / 1000)}", -1)
    nivel(v, 39800, Z_TOP_PIL, f"platibanda {f(Z_TOP_PIL / 1000)} (painéis {f(z_tel(39475) / 1000)})")
    nivel(v, 20400, Z_TOP_C, f"topo I130 / pilar central {f(Z_TOP_C / 1000)}")
    if eixo == 3:
        nivel(v, 19950, Z_TOP_C - H_I130, f"fundo I130 {f((Z_TOP_C - H_I130) / 1000)}")
    else:
        for zm in Z_MEZ:
            nivel(v, 4500, zm, f"piso mezanino {f(zm / 1000)}")
    v.chamada((30000, z_tel(30000)), (6, 14), f"TP40 + lã 40 + zipada 0,65 (480 × 70) + painéis solares sobre terças Z 302×2,30 contínuas c/{LG['passo_tercas']*100:.1f} cm nos ST-1P — ND-LET-COB01".replace(".", ","))
    v.chamada((10000, zf(10000) + 450), (8, -16), "TS-01 — viga I90 protendida, caimento 3 %, sem dentes (apoio direto)")
    v.chamada((39900, 5000), (6, 0), "placa de fechamento 10 cm (por fora)")
    v.chamada((39350, 9950), (8, 20), f"cabeça 40×30; folga de {Z_TOP_PIL - z_tel(39475):.0f} mm do topo dos painéis à platibanda")
    if eixo == 3:
        v.chamada((XC, Z_TOP_C - 650), (10, -30), "I130 (h 130): TS-01 apoiadas no topo (NEO-3 + 2 PN-5 por viga)")
    else:
        v.chamada((XC, 5000), (10, 10), "P8A 40×60 (40 em x): TS-01 apoiadas no topo")
        v.chamada((15000, Z_MEZ[1] - 600), (8, 16), "vigas do mezanino em meio vaso com dente + laje h20 + capa 5")

# detalhes ampliados 1:20
for k, (nome, org, jan, eixo, txt) in enumerate((
        ("DETALHE 1", (80, 50), (-900, REC[0] - 800, 1700, 10300), 3, "apoio no pilar P1 — lado baixo"),
        ("DETALHE 2", (330, 50), (18600, Z_TOP_C - 1400, 20900, Z_TOP_C + 1700), 3, "apoio no topo da I130 — eixo 3"),
        ("DETALHE 3", (640, 50), (37900, REC[1] - 800, 40400, 10400), 3, "apoio no pilar P2 — lado alto"))):
    v = pr.vista(nome, (org[0] - jan[0] / 20, org[1] - jan[1] / 20), 20, titulo=f"{nome} — {txt.upper()}", subtitulo="")
    R = Recorte(v, jan)
    estrutura(R, eixo)
    v.poli([(jan[0], jan[1]), (jan[2], jan[1]), (jan[2], jan[3]), (jan[0], jan[3])], "CARIMBO_FINO", True)
    if k == 0:
        zs = REC[0]
        v.cota_h([0, X0[0], X0[0] + 140, 300], zs - 300, -8, total=False)
        v.cota_v([zs, zs + 10, zf(X0[0]) + 900], 1600, 8, total=False)
        nivel(v, -800, zs, f"{f(zs / 1000)}")
        nivel(v, 800, Z_TOP_PIL, f"{f(Z_TOP_PIL / 1000)}")
        v.chamada((X0[0] + 140, zs + 200), (10, 18), "2 pinos PN-3 Ø25 + NEO-4 200×300×10; apoio 27,5")
        v.chamada((-400, 9200), (-6, 18), "placa 10 cm")
    elif k == 1:
        v.cota_h([XC - 200, XC - 37.5, XC + 37.5, XC + 200], Z_TOP_C - 300, -8, total=False)
        nivel(v, 20800, Z_TOP_C, f"{f(Z_TOP_C / 1000)}", -1)
        v.chamada((XC + 115, Z_TOP_C + 200), (10, 24), "NEO-3 100×300 + 2 PN-5 Ø20 por TS-01; apoio 16,25")
        v.chamada((XC - 600, zf(19200) + 1300), (-14, 14), "terças acima das TS-01")
    else:
        zs = REC[1]
        v.cota_v([zs, Z_TOP_PIL - 150, Z_TOP_PIL], 40400 - 300, -6, total=False)
        nivel(v, 40300, Z_TOP_PIL, f"{f(Z_TOP_PIL / 1000)}", -1)
        v.chamada((39350, Z_TOP_PIL), (-10, 20), f"cabeça 40×30; folga de {(Z_TOP_PIL - z_tel(39475)):.0f} mm acima dos painéis")

# coluna direita: tabela de níveis e notas
x0, y = pr.quadro[2] - 180, pr.quadro[3] - 6
niv = [["Assento da TS-01 no P1 (recuo)", f(REC[0] / 1000)], ["Assento da TS-01 no P2 (recuo)", f(REC[1] / 1000)],
       ["Topo da I130 / pilares centrais", f(Z_TOP_C / 1000)], ["Fundo da I130", f((Z_TOP_C - H_I130) / 1000)], ["Assento da I130 (CP-I130)", f(Z_ASS_I130 / 1000)],
       ["Topo dos painéis junto ao P1 / ao P2", f"{f(z_tel(X0[0]) / 1000)} / {f(z_tel(39475) / 1000)}"], ["Platibanda (todas)", f(Z_TOP_PIL / 1000)],
       ["Pisos do mezanino", f"{f(Z_MEZ[0] / 1000)} / {f(Z_MEZ[1] / 1000)}"]]
y = pr.tabela(x0, y, "NÍVEIS (m)", ["ELEMENTO", "NÍVEL"], niv, [110, 70])
notas = ["Cortes gerados do mesmo modelo usado na checagem das ligações.",
         f"Cobertura rebaixada (rev03) para o pacote TP40 + lã 40 + zipada 70 + painéis solares: topo dos painéis junto ao P2 em {f(z_tel(39475) / 1000)}, {(Z_TOP_PIL - z_tel(39475)):.0f} mm abaixo da platibanda +10,000 (pedido: ≥ 150 mm).",
         f"TS-01 com {LG['L_TS']:.3f} m entre pontas (a prumo), sem dentes: apoio de 27,5 cm no recuo dos pilares laterais (NEO-4 + 2 PN-3 Ø25) e de 16,25 cm no topo da I130 / pilar central (NEO-3 + 2 PN-5 Ø20); terças c/{LG['passo_tercas']:.3f} m.".replace(".", ","),
         "Cabeça dos pilares laterais recuada acima do assento da TS-01: só os 30 cm externos sobem até +10,00 (consolos externos pela cabeça).",
         "Vigas centrais I130 (h 130) com dentes 78 × 35 nos consolos CP-I130; vigas do mezanino VM em meio vaso com dente Gerber nos consolos CP-MEZ (fundo alinhado; rev04, ND-LET-VM01).",
         f"Pé-direito (rev03): fundo da TS-01 de +7,19 (eixo A) a +7,78 (eixo C); no mezanino superior (+6,55), fundo das terças entre as linhas 1 e 2 de {f((REC[0] + 900 + 10) / 1000)} (eixo A) a {f((Z_TOP_C + 10) / 1000)} (eixo C) — conferir o uso do piso superior. Portões da linha 4 livres até +7,40.",
         "Fundações e cálices em projeto próprio. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(x0, y - 4, notas, 180)
pr.posicoes_desenho.clear()
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-CT01")
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
for a in avisos:
    if a[0] == "ERRO" or "sai" in a[1]:
        print(a)
