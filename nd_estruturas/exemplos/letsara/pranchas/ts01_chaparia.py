"""ND-LET-TS01-3 — TS-01: esperas e insertos concretados + peças de ligação da cobertura (A1). Rev. 03: tudo parafusado,
sem solda (esperas de barra roscada M16 concretadas na viga; peças da montagem dobradas/cortadas e furadas)."""
import json
from prancha_nd import Prancha
from ts01_dados import P, L, H, f, peso, V

CB = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/cobertura_metalica.json"))
pr = Prancha("A1", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="TS-01 — ESPERAS, INSERTOS E PEÇAS DE LIGAÇÃO DA COBERTURA (SEM SOLDA)",
                        desenho="ND-LET-TS01-3", folha="03/03", fase="PARA APROVAÇÃO"))
pr.revisao("01", "12/10/2026", "PINOS C/ CABEÇA CALCULADOS, CH-MF, CH-MF2, OR-1, CT-1, TB-1 NO DENTE")
pr.revisao("02", "12/10/2026", "ST-1 SOLDADO NA CH-T; OR-1 SOLDADA NA CH-MF")
pr.revisao("03", "14/10/2026", "SEM SOLDA: ESPERAS ES-1/2/3, ST-1P, OR-X, CMF-1; SEM DENTES")
pr.cabecalho_peca("TS-01", f"VIGA DE COBERTURA I90 PROTENDIDA — L = {f(L/10,1)} cm · 14 PEÇAS — esperas e peças de ligação (medidas em mm)",
                  f"PESO {f(peso/9.81,1)} t   ·   VOLUME {f(V,2)} m³   ·   todas as ligações da cobertura parafusadas, sem solda em fábrica ou obra", 560)
nt, nn = len(P["tercas"]), len(P["nos"])


def furo(v, c, d):
    v.circulo(c, d / 2, "METALICA")
    v.linha((c[0] - d * 0.8, c[1]), (c[0] + d * 0.8, c[1]), "EIXO")
    v.linha((c[0], c[1] - d * 0.8), (c[0], c[1] + d * 0.8), "EIXO")


def oblongo(v, c, d, comp, horiz=True):
    a = (comp - d) / 2
    if horiz:
        v.poli([(c[0] - a, c[1] - d / 2), (c[0] + a, c[1] - d / 2)], "METALICA"); v.poli([(c[0] - a, c[1] + d / 2), (c[0] + a, c[1] + d / 2)], "METALICA")
        v.circulo((c[0] - a, c[1]), d / 2, "METALICA"); v.circulo((c[0] + a, c[1]), d / 2, "METALICA")
    else:
        v.poli([(c[0] - d / 2, c[1] - a), (c[0] - d / 2, c[1] + a)], "METALICA"); v.poli([(c[0] + d / 2, c[1] - a), (c[0] + d / 2, c[1] + a)], "METALICA")
        v.circulo((c[0], c[1] - a), d / 2, "METALICA"); v.circulo((c[0], c[1] + a), d / 2, "METALICA")


def barra_roscada(v, x, y0, hef, sai, gancho=True, cabeca=False):
    v.ret(x - 8, y0 - hef, 16, hef + sai, "METALICA")
    for k in range(int(sai / 8)):
        yy = y0 + 4 + 8 * k
        v.linha((x - 8, yy), (x + 8, yy + 4), "METALICA")
    if gancho:
        v.poli([(x - 8, y0 - hef), (x - 8, y0 - hef - 20), (x + 52, y0 - hef - 20), (x + 52, y0 - hef + 4)], "METALICA")
    if cabeca:
        v.chapa(x - 20, y0 - hef - 6, 40, 6, 0.25)
        v.ret(x - 13, y0 - hef - 20, 26, 14, "METALICA")
    v.linha((x - 40, y0), (x + 40, y0), "VISTA")


# ------------------------------------------------------------------ ESPERAS (1:5)
v = pr.vista("ES-1", (90, 470), 5, titulo="ES-1 — ESPERA DO ST-1P", subtitulo=f"2 por terça · {2*nt} por peça · {2*nt*14} na obra")
barra_roscada(v, 0, 0, 150, 120)
v.cota_v([-170, -150, 0, 120], 40, 10, total=False)
v.chamada((0, 60), (10, 14), "barra roscada M16 A36 (rosca laminada) — 120 rosqueados")
v.chamada((40, -170), (10, -6), "gancho 90°, 60")
v.chamada((-40, 0), (-4, -16), "face superior da TS-01")

v = pr.vista("ES-2", (225, 470), 5, titulo="ES-2 — ESPERA DA ORELHA OR-X", subtitulo=f"4 por nó do X · {4*nn} por peça · {4*nn*14} na obra")
barra_roscada(v, 0, 0, 110, 50)
v.poli([(-40, -30), (-40, -90), (40, -90), (40, -30)], "ARM_TRANSV")
v.cota_v([-130, -110, 0, 50], 40, 10, total=False)
v.chamada((0, 30), (10, 14), "barra roscada M16 A36 — 50 rosqueados")
v.chamada((40, -60), (12, -14), "grampo U Ø10 CA-50, pernas 300")

v = pr.vista("ES-3", (375, 440), 5, titulo="ES-3 — ESPERA DA MÃO-FRANCESA", subtitulo=f"horizontal, faces B e D · {2*nt} por peça")
v.ret(-110, -8, 170, 16, "METALICA")
for k in range(7):
    v.linha((4 + 8 * k, -8), (8 + 8 * k, 8), "METALICA")
v.chapa(-116, -20, 6, 40, 0.25)
v.ret(-110, -13, 14, 26, "METALICA")
v.linha((0, -40), (0, 40), "VISTA")
v.cota_h([-116, -110, 0, 60], -20, -10, total=False)
v.chamada((30, 8), (6, 14), "barra roscada M16 A36 — 60 para fora da face")
v.chamada((-113, 20), (-8, 12), "porca M16 + arruela 40×40×6 (ancoragem)")
v.chamada((0, -40), (6, -10), "face lateral da mesa inferior (h = 100 do fundo)")

# ------------------------------------------------------------------ TB-3, PN-3, PN-5, NEO-3, NEO-4 (1:10)
v = pr.vista("TB-3", (480, 455), 10, titulo="TB-3", subtitulo="tubo dos pinos · 4 por peça")
v.ret(-25, -450, 50, 900, "METALICA")
v.cota_v([-450, 450], 25, 8)
v.cota_h([-25, 25], 450, 6)
v.chamada((25, 0), (6, 6), "tubo Ø50,8×2,0 L=900, passante")
v.chamada((25, -440), (6, -6), "graute ≥ 40 MPa")

v = pr.vista("PN-3", (590, 455), 10, titulo="PN-3 / PN-5", subtitulo="pinos nos pilares / na I130")
v.ret(-12.5, -300, 25, 600, "METALICA")
v.ret(60 - 10, -300, 20, 600, "METALICA")
v.linha((-60, 0), (100, 0), "EIXO")
v.cota_v([-300, 0, 300], -12.5, -8, total=False)
v.chamada((0, 150), (-8, 10), "PN-3 Ø25 L=600 (P1/P2)")
v.chamada((0, -150), (-8, -10), "PN-5 Ø20 L=600 (I130/centro)")
v.chamada((-60, 0), (-6, 4), "topo do apoio")

v = pr.vista("NEO-4", (110, 290), 5, titulo="NEO-4 / NEO-3", subtitulo="neoprene 10 mm, 60 Shore A")
v.ret(-100, -150, 200, 300, "VISTA")
for yy in (-100, 100):
    furo(v, (0, yy), 35)
v.ret(160, -150, 100, 300, "VISTA")
for yy in (-100, 100):
    furo(v, (210, yy), 30)
v.cota_h([-100, 0, 100], -150, -8, total=False)
v.cota_h([160, 260], -150, -8)
v.cota_v([-150, -100, 100, 150], 260, 8, total=False)
v.chamada((0, 0), (4, 40), "NEO-4 200×300 (pilar lateral)")
v.chamada((210, 0), (10, 50), "NEO-3 100×300 (I130 / centro)")

# ------------------------------------------------------------------ ST-1P (1:5)
st = CB["ST1P"]
v = pr.vista("ST-1P", (250, 280), 5, titulo="ST-1P — SUPORTE DA TERÇA", subtitulo=f"chapa dobrada 9,5 A36 · 1 por terça · {nt*14} na obra")
v.chapa(-110, 0, 220, 9.5)
v.chapa(-110, 9.5, 9.5, 280.5)
v.texto((-100, 320), "perfil da dobra", "nota")
v2 = pr.vista("ST-1P FRENTE", (330, 280), 5, titulo="ST-1P — ABA VERTICAL", subtitulo="furos das terças")
v2.ret(-110, 0, 220, 290, "METALICA")
for yy in (-50, 50):
    for zz in (110, 210):
        furo(v2, (yy, zz), 14)
v2.cota_h([-110, -50, 50, 110], 0, -8, total=False)
v2.cota_v([0, 110, 210, 290], 110, 8, total=False)
v2.chamada((50, 210), (10, 18), "4 furos Ø14: 2 M12 8.8 por terça")
v3 = pr.vista("ST-1P PLANTA", (440, 290), 5, titulo="ST-1P — ABA HORIZONTAL", subtitulo="furos oblongos (ajuste ±11)")
v3.ret(0, -110, 150, 220, "METALICA")
for yy in (-60, 60):
    oblongo(v3, (75, yy), 18, 40, horiz=True)
v3.cota_v([-110, -60, 60, 110], 150, 8, total=False)
v3.cota_h([0, 75, 150], -110, -8, total=False)
v3.chamada((75, 60), (8, 24), "2 oblongos 18 × 40 (ES-1)")

# ------------------------------------------------------------------ OR-X, CMF-1, MF-1 (1:5 e 1:10)
v = pr.vista("OR-X", (600, 300), 2.5, titulo="OR-X — ORELHA DO X", subtitulo="L 102×76×6,3 A36, L = 80 · vãos 2-3 e 7-8")
v.ret(0, 0, 76, 6.3, "METALICA")
v.ret(0, 0, 6.3, 102, "METALICA")
furo(v, (45, 3), 18)
v.circulo((3, 45), 9, "METALICA"); v.circulo((3, 85), 9, "METALICA")
v.cota_v([0, 45, 85, 102], -10, -8, total=False)
v.cota_h([0, 45, 76], 0, -14, total=False)
v.chamada((3, 85), (-10, 14), "2 furos Ø18 (diagonal a 45 ou 85)")
v.chamada((45, 6), (6, -20), "furo Ø18 na ES-2")

mf = CB["MF1"]
Lmf = round(mf["comp_m"] * 1000)
v = pr.vista("CMF-1", (90, 125), 2.5, titulo="CMF-1 — CLIPE DA MÃO-FRANCESA", subtitulo=f"L 76×76×6,3 A36, L = 80 · 2 por terça")
v.ret(0, 0, 76, 6.3, "METALICA")
v.ret(0, 0, 6.3, 76, "METALICA")
furo(v, (40, 3), 18)
v.circulo((3, 40), 7, "METALICA")
v.cota_h([0, 40, 76], 0, -14, total=False)
v.cota_v([0, 40, 76], -10, -8, total=False)
v.chamada((40, 6), (10, 24), "furo Ø18 na ES-3 (porca M16)")
v.chamada((3, 40), (-6, 20), "furo Ø14: M12 na MF-1")

v = pr.vista("MF-1", (215, 110), 10, titulo="MF-1 — MÃO-FRANCESA", subtitulo=f"L 50×5 A36, L = {Lmf} · 2 por terça · {mf['angulo']}")
v.linha((0, 0), (Lmf, 0), "METALICA"); v.linha((0, 50), (Lmf, 50), "METALICA")
v.linha((0, 0), (0, 50), "METALICA"); v.linha((Lmf, 0), (Lmf, 50), "METALICA")
furo(v, (30, 25), 14); furo(v, (Lmf - 30, 25), 14)
v.cota_h([0, 30, Lmf - 30, Lmf], 0, -8, total=False)
v.chamada((30, 25), (-4, 14), "M12 8.8 no CMF-1")
v.chamada((Lmf - 30, 25), (-30, 24), "M12 8.8 na alma da terça (a 40 do fundo)")

# ------------------------------------------------------------------ ISO da ponta
pr.imagem(400, 40, 640, 210, "/home/claude/letsara/pranchas/ISO-TS01-ponta-crop.png", "ISOMÉTRICO — LIGAÇÕES DA COBERTURA",
          "terça, ST-1P, mão-francesa e contraventamento — tudo parafusado")

# ------------------------------------------------------------------ tabelas
x0, y = pr.quadro[2] - 180, pr.quadro[3] - 6
k = lambda kgm, Lm: f(kgm * Lm, 1)
lista = [["ES-1", "barra roscada M16 L=330 c/ gancho", 2 * nt, 2 * nt * 14, k(1.58, 0.33)],
         ["ES-2", "barra roscada M16 L=220 c/ gancho + U Ø10", 4 * nn, 4 * nn * 14, k(1.58, 0.22)],
         ["ES-3", "barra roscada M16 L=170 + porca + arruela", 2 * nt, 2 * nt * 14, k(1.58, 0.17)],
         ["TB-3", "tubo Ø50,8×2,0 L=900", 4, 56, k(2.41, 0.90)],
         ["AL-1", "cordoalha Ø12,7 L=1,90 m", 4, 56, "1,5"],
         ["ST-1P", "chapa dobrada 9,5 × 220 (150 + 290)", nt, nt * 14, "7,4"],
         ["ST-1V", "igual ao ST-1P, 2 oblongos no eixo (VB)", "-", 4 * nt, "7,4"],
         ["OR-X", "L 102×76×6,3 L=80", "-", 4 * nn * 4, "0,7"],
         ["CMF-1", "L 76×76×6,3 L=80", "-", 2 * nt * 14, "0,6"],
         ["MF-1", f"L 50×5 L={Lmf}", "-", 2 * nt * 14, k(3.77, Lmf / 1000)],
         ["PN-3", "pino Ø25 CA-50 L=600 (pilar)", "-", 28, "2,3"],
         ["PN-5", "pino Ø20 CA-50 L=600 (I130/pilar central)", "-", 28, "1,5"],
         ["NEO-4", "neoprene 200×300×10, 2 furos Ø35", "-", 14, "-"],
         ["NEO-3", "neoprene 100×300×10, 2 furos Ø30", "-", 14, "-"]]
y = pr.tabela(x0, y, "LISTA DE PEÇAS — TS-01 E LIGAÇÕES DA COBERTURA", ["MARCA", "DESCRIÇÃO", "/VIGA", "OBRA", "kg/un"], lista,
              [16, 92, 18, 22, 32])
notas = ["Nenhuma solda na fábrica ou na obra: esperas de barra roscada M16 A36 (rosca laminada) concretadas com gabarito; peças da montagem cortadas, dobradas e furadas; ligações com parafusos M12 8.8 e porcas M16.",
         "ST-1P: assentar sobre porca de nivelamento + arruela, apertar com porca e contraporca; furos oblongos 18 × 40 para ajuste ±11 mm ao longo da viga.",
         "Mão-francesa MF-1 em todas as terças, dos dois lados da viga: CMF-1 na espera ES-3 (porca M16) e MF-1 parafusada no CMF-1 e na alma da terça.",
         "OR-X só nos nós dos vãos contraventados (2-3 e 7-8); as esperas ES-2 existem em todas as TS-01 (marca única). Diagonais Ø16 A36 com esticador (ND-LET-COB02).",
         "Pinos PN-3/PN-5 concretados no pilar / na I130, passando pelo neoprene e pelos tubos TB-3, grauteados após o alinhamento das vigas.",
         "Proteção: esperas, barras e peças galvanizadas a fogo (NBR 6323); retocar com tinta rica em zinco após a montagem.",
         "Cálculo das esperas pelo ACI 318-19 cap. 17 (C50, concreto fissurado) e das peças pela NBR 8800:2024 — memória de cálculo em separado.",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(x0, y - 4, notas, 180)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-TS01-3")
for a in avisos:
    print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
