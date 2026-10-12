"""ND-LET-CT01 — cortes transversais da estrutura (eixos 2 e 3) e detalhes dos apoios da cobertura (A0)."""
import json, math
from prancha_nd import Prancha, _seg_rect

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
LG = json.load(open(AQ + "ligacoes.json"))
f = lambda v, d=3: f"{v:+.{d}f}".replace(".", ",")
I = 0.03
c, sn = 1 / math.sqrt(1 + I * I), I / math.sqrt(1 + I * I)
L_TS = LG["L_TS"] * 1000
X0 = [325.0, 20325.0]                    # pontas das duas TS-01 (a prumo)
zf = lambda x: LG["Z0_TS"] * 1000 + I * x  # fundo da TS-01 (mm, x global em mm) — cobertura baixada 0,62 m
HD, LN, H = 450.0, 300.0, 900.0
t3 = 27.0 / 900.0
Z_TOP_PIL, Z_I110 = 10000.0, 8880.0
Z_MEZ = [3150.0, 6550.0]
TER = [s * 1000 for s in LG["s_tercas"]]


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
    cont = [(LN, 0), (L - LN, 0), (L - LN + sk(HD), HD), (L + sk(HD), HD), (L + 27, H), (27, H), (sk(HD), HD), (LN + sk(HD), HD)]
    R.poli([glob(x0, s, h) for s, h in cont], "CORTADO", True)
    for h in (150, 230, 700, 780):
        R.linha(glob(x0, 1200 + sk(h), h), glob(x0, L - 1200 + sk(h), h), "VISTA")
    for s0 in (150 + sk(HD), L - 150 + sk(HD)):
        R.linha(glob(x0, s0, HD), glob(x0, s0 + sk(H - HD), H), "EIXO")
    for s in TER:
        xt, zt = glob(x0, s, H)
        R.ret(xt - 42.5, zt + 12.5, 85, 300, "METALICA")
        R.ret(xt - 50, zt, 100, 12.5, "METALICA")
        R.ret(xt - 4, zt + 12.5, 8, 290, "METALICA")                 # ST-1
        xb_, zb_ = glob(x0, s - 27, 0)
        if s > 1000 and s < L - 1000:
            R.linha((xb_, zb_), (xt, zt + 12.5), "OCULTA")       # mão-francesa (vista de topo, no plano da terça)
    a, b = glob(x0, -100, H + 12.5 + 300 + 30), glob(x0, L + 100, H + 12.5 + 300 + 30)
    R.linha(a, b, "METALICA")
    a2, b2 = glob(x0, -100, H + 12.5 + 300), glob(x0, L + 100, H + 12.5 + 300)
    R.linha(a2, b2, "METALICA")


def consolo(R, face, lado, z_seat, proj=300, alt=450, alt_ponta=250):
    """Consolo com topo a 3% passando por z_seat no centro do apoio (a 150+25+... da face)."""
    xa, xb = face, face + lado * proj
    xm = face + lado * (proj - 125)
    zt = lambda x: z_seat + I * (x - xm)
    pts = [(xa, zt(xa)), (xb, zt(xb)), (xb, zt(xb) - alt_ponta), (xa, zt(xa) - alt)]
    R.poli(pts, "CORTADO", True)
    R.hach(pts)


def pilar(R, x, larg, z_top, nome=None):
    pts = [(x - larg / 2, 0), (x + larg / 2, 0), (x + larg / 2, z_top), (x - larg / 2, z_top)]
    R.poli(pts, "CORTADO", True)


def estrutura(R, eixo):
    z1 = LG["apoios"][0]["z_assento"] * 1000
    pilar(R, 0, 600, Z_TOP_PIL); pilar(R, 40100, 600, Z_TOP_PIL)
    consolo(R, 300, 1, zf(475) + HD * c - 10)
    consolo(R, 39800, -1, zf(39625) + HD * c - 10)
    for xp in (-400, 40500):                                            # placas de fechamento (10 cm)
        R.ret(xp - 50, 0, 100, Z_TOP_PIL, "VISTA")
    ze, zd = zf(19625) + HD * c - 10, zf(20475) + HD * c - 10
    if eixo == 2:
        pilar(R, 20050, 500, Z_I110)
        consolo(R, 19800, -1, ze); consolo(R, 20300, 1, zd)
        for xm in (9870, 29630):
            pilar(R, xm, 600, Z_MEZ[1])
        faces = [(300, 9570), (10170, 19800), (20300, 29330), (29930, 39800)]
        for zm in Z_MEZ:
            topo = zm - 250                                  # laje alveolar h20 + capa 5
            for a, b in faces:
                xa, xb = a + 25, b - 25
                cont = [(xa + LN, topo - 700), (xb - LN, topo - 700), (xb - LN, topo - 425), (xb, topo - 425), (xb, topo), (xa, topo),
                        (xa, topo - 425), (xa + LN, topo - 425)]
                R.poli(cont, "CORTADO", True)
                consolo(R, a, 1, topo - 425 - 10, proj=300, alt=500); consolo(R, b, -1, topo - 425 - 10, proj=300, alt=500)
            R.ret(300, zm - 250, 39500, 200, "VISTA")
            R.ret(300, zm - 50, 39500, 50, "VISTA")
    else:
        sec = [(-200, 0), (200, 0), (200, 250), (75, 330), (75, 800), (200, 880), (200, 1100), (-200, 1100), (-200, 880),
               (-75, 800), (-75, 330), (-200, 250)]
        base = Z_I110 - 1100
        R.poli([(20050 + x, base + y) for x, y in sec], "OCULTA", True)
        dia = [(19850, base), (20250, base), (20250, Z_I110), (19850, Z_I110)]
        R.poli(dia, "CORTADO", True); R.hach(dia)
        consolo(R, 19850, -1, ze, proj=350); consolo(R, 20250, 1, zd, proj=350)
    for x0 in X0:
        ts(R, x0)


def nivel(v, x, z, txt, lado=1):
    v.linha((x, z), (x + lado * 900, z), "INDICACAO")
    v.poli([(x + lado * 450 - 150, z + 260), (x + lado * 450 + 150, z + 260), (x + lado * 450, z)], "INDICACAO", True)
    v.texto((x + lado * 650, z + 80), txt, "nota", alinh="BOTTOM_LEFT" if lado > 0 else "BOTTOM_RIGHT")


pr = Prancha("A0", dict(cliente="MARQUE ENGENHARIA", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="CORTES TRANSVERSAIS DA ESTRUTURA (EIXOS 2 E 3) E APOIOS DA COBERTURA",
                        desenho="ND-LET-CT01", folha="01/01", fase="PARA ANÁLISE"))
z_tel = lambda x: zf(x) + (H + 12.5 + 330) * c
for k, (eixo, org, nome) in enumerate(((2, (70, 590), "CORTE 2-2"), (3, (70, 330), "CORTE 3-3"))):
    v = pr.vista(nome, org, 50, titulo=f"{nome} — EIXO {eixo} (y = {[10.05, 19.705][k]:.3f} m)".replace(".", ","),
                 subtitulo="olhando para o eixo 9; cotas de nível em metros" + ("; mezanino entre os eixos 1 e 2" if eixo == 2 else ""))
    R = Recorte(v)
    v.linha((-1500, 0), (41600, 0), "TERRENO")
    estrutura(R, eixo)
    for x, nomex in ((0, "A"), (9870, "B"), (20050, "C"), (29630, "D"), (40100, "E")):
        v.linha((x, -900), (x, 11600), "EIXO")
        v.circulo((x, -1300), 400, "INDICACAO"); v.texto((x, -1300), nomex, "sub", alinh="MIDDLE_CENTER")
    v.cota_h([0, 9870, 20050, 29630, 40100], 0, -40)
    nivel(v, -300, 0, "±0,000", -1)
    nivel(v, 600, zf(475) + HD * c - 10, f"consolo {f((zf(475) + HD * c - 10) / 1000)}")
    nivel(v, 300, Z_TOP_PIL, f"platibanda {f(Z_TOP_PIL / 1000)}", -1)
    nivel(v, 39500, zf(39625) + HD * c - 10, f"consolo {f((zf(39625) + HD * c - 10) / 1000)}", -1)
    nivel(v, 40400, Z_TOP_PIL, f"platibanda {f(Z_TOP_PIL / 1000)}")
    nivel(v, 40400, z_tel(39775), f"telha {f(z_tel(39775) / 1000)}")
    nivel(v, 19400 if eixo == 2 else 19400, zf(19625) + HD * c - 10, f"consolo {f((zf(19625) + HD * c - 10) / 1000)}", -1)
    nivel(v, 20700, zf(20475) + HD * c - 10, f"consolo {f((zf(20475) + HD * c - 10) / 1000)}")
    if eixo == 3:
        nivel(v, 20250, Z_I110, f"topo I110 {f(Z_I110 / 1000)}")
        nivel(v, 20250, Z_I110 - 1100, f"fundo I110 {f((Z_I110 - 1100) / 1000)}")
    else:
        for zm in Z_MEZ:
            nivel(v, 4500, zm, f"piso mezanino {f(zm / 1000)}")
    v.chamada((30000, z_tel(30000)), (6, 14), "telha sanduíche PIR 30 (aço 0,5/0,5) sobre terças Ue 300 c/1,579 nos suportes ST-1 — ND-LET-COB01")
    v.chamada((10000, zf(10000) + 450), (8, -16), "TS-01 — viga I90 protendida, caimento 3%, dentes Gerber nas pontas")
    v.chamada((40500, 5000), (6, 0), "placa de fechamento 10 cm")
    v.chamada((40100, 9950), (8, 20), f"platibanda {Z_TOP_PIL - z_tel(39800):.0f} mm acima da telha (cobertura escondida)")
    if eixo == 3:
        v.chamada((20050, Z_I110 - 550), (10, -30), "I110 (diafragma maciço na linha da TS) + consolos CV-TS")
    else:
        v.chamada((20050, 5000), (10, 10), "P8A 50×50 (alterado de 40×60)")
        v.chamada((15000, Z_MEZ[1] - 600), (8, 16), "vigas do mezanino I70 com dentes + laje alveolar h20 + capa 5 (ver nota 5)")

# detalhes ampliados 1:20
for k, (nome, org, jan, eixo, txt) in enumerate((
        ("DETALHE 1", (80, 50), (-900, 7100, 1700, 10300), 3, "apoio no pilar P1 — lado baixo"),
        ("DETALHE 2", (330, 50), (18900, 7600, 21200, 9600), 3, "apoio na I110 — eixo 3"),
        ("DETALHE 3", (640, 50), (38500, 8400, 41000, 10400), 3, "apoio no pilar P2 — lado alto"))):
    v = pr.vista(nome, (org[0] - jan[0] / 20, org[1] - jan[1] / 20), 20, titulo=f"{nome} — {txt.upper()}", subtitulo="")
    R = Recorte(v, jan)
    estrutura(R, eixo)
    v.poli([(jan[0], jan[1]), (jan[2], jan[1]), (jan[2], jan[3]), (jan[0], jan[3])], "CARIMBO_FINO", True)
    if k == 0:
        zs = zf(475) + HD * c - 10
        v.cota_h([300, 325, 475, 625], zs, -16, total=False)
        v.cota_v([zs, zs + 10, zf(325) + 900], 1600, 8, total=False)
        nivel(v, -800, zs, f"{f(zs / 1000)}")
        nivel(v, -800, Z_TOP_PIL, f"{f(Z_TOP_PIL / 1000)}")
        nivel(v, -800, z_tel(325), f"telha {f(z_tel(325) / 1000)}")
        v.chamada((475, zs + 200), (10, 18), "pino PN-1 Ø25 + neoprene 10")
        v.chamada((450, zs - 300), (12, -14), "consolo CP-TS (3 Ø16), topo a 3%")
        v.chamada((-400, 9200), (-6, 18), "placa")
    elif k == 1:
        ze, zd = zf(19625) + HD * c - 10, zf(20475) + HD * c - 10
        v.cota_h([19500, 19775, 19850, 20250, 20325, 20600], ze - 350, -12, total=False)
        nivel(v, 19000, ze, f"{f(ze / 1000)}", 1)
        nivel(v, 21100, zd, f"{f(zd / 1000)}", -1)
        nivel(v, 21100, Z_I110, f"{f(Z_I110 / 1000)}", -1)
        v.chamada((20050, 9300), (10, 24), "diafragma da I110 na linha da TS")
        v.chamada((19600, ze - 200), (-10, -20), "CV-TS 350")
        v.chamada((19700, zf(19500) + 1300), (-14, 14), "terças 86 mm acima do topo da I110")
    else:
        zs = zf(39625) + HD * c - 10
        v.cota_v([zs, Z_TOP_PIL, z_tel(39775)], 41000 - 300, -6, total=False)
        nivel(v, 40900, Z_TOP_PIL, f"{f(Z_TOP_PIL / 1000)}", -1)
        nivel(v, 40900, z_tel(39775), f"telha {f(z_tel(39775) / 1000)}", -1)
        v.chamada((40100, Z_TOP_PIL), (-10, 20), f"folga de {(Z_TOP_PIL - z_tel(39800)):.0f} mm acima da telha")

# coluna direita: tabela de níveis e notas
x0, y = pr.quadro[2] - 180, pr.quadro[3] - 6
niv = [["Consolo P1 (lado baixo)", f((zf(475) + HD * c - 10) / 1000)], ["Consolo centro, lado esq.", f((zf(19625) + HD * c - 10) / 1000)],
       ["Consolo centro, lado dir.", f((zf(20475) + HD * c - 10) / 1000)], ["Consolo P2 (lado alto)", f((zf(39625) + HD * c - 10) / 1000)],
       ["Topo / fundo da I110", f"{f(Z_I110 / 1000)} / {f((Z_I110 - 1100) / 1000)}"], ["Assento da I110 no pilar central", f((Z_I110 - 1100 + 440) / 1000)],
       ["Telha junto ao P1 / ao P2", f"{f(z_tel(325) / 1000)} / {f(z_tel(39775) / 1000)}"], ["Platibanda (todas)", f(Z_TOP_PIL / 1000)],
       ["Pisos do mezanino", f"{f(Z_MEZ[0] / 1000)} / {f(Z_MEZ[1] / 1000)}"]]
y = pr.tabela(x0, y, "NÍVEIS (m)", ["ELEMENTO", "NÍVEL"], niv, [110, 70])
notas = ["Cortes gerados do mesmo modelo usado na checagem das ligações (pinos, folgas e terças conferidos em 28 apoios).",
         "Cobertura baixada 0,62 m para ficar escondida: telha junto ao P2 em " + f(z_tel(39800) / 1000) + ", " + f"{(Z_TOP_PIL - z_tel(39800)):.0f}" + " mm abaixo da platibanda +10,000 (pedido: 100 mm).",
         f"TS-01 com {LG['L_TS']:.3f} m entre pontas (a prumo), dentes de 450 × 300 nas duas pontas; terças c/{LG['passo_tercas']:.3f} m.".replace(".", ","),
         "Pilar central P8A 50×50 (era 40×60): com 60 na direção x a face ficava 25 mm dentro da ponta da TS-01.",
         "LAJE h20 + 5 (pedido): com 500 kgf/m² em 9,75 m e 7 Ø12,7 por painel NÃO atende na seção genérica — ELU 209 > 192 kN·m por painel, descompressão só até 9,05 m. Desenhada para análise; confirmar na tabela do fabricante ou voltar à h26,5 + 5.",
         "Vigas do mezanino I70 (mesma fôrma, 10 Ø12,7): atendem à flexão com a laje h20; dente de 425 em verificação por MEF. Ganham 20 cm de pé-direito sobre a I90.",
         "Fundações e cálices em projeto próprio. PROJETO DA ND ENGENHARIA — PARA ANÁLISE, NÃO EXECUTAR."]
pr.notas(x0, y - 4, notas, 180)
pr.posicoes_desenho.clear()
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-CT01")
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
for a in avisos:
    if a[0] == "ERRO" or "sai" in a[1]:
        print(a)
