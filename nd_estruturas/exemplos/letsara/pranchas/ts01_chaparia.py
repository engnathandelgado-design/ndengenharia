"""ND-LET-TS01-3 — TS-01: chaparia e insertos concretados na peça + peças de ligação da montagem (A1). Rev. 01."""
import json
from prancha_nd import Prancha
from ts01_dados import P, L, H, HD, LN, PASSO_T, f

LG = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/ligacoes.json"))
CB = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/cobertura_metalica.json"))
pr = Prancha("A1", dict(cliente="MARQUE ENGENHARIA", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="TS-01 — CHAPARIA, CHUMBADORES E PEÇAS DE LIGAÇÃO DA MONTAGEM",
                        desenho="ND-LET-TS01-3", folha="03/04", fase="PARA APROVAÇÃO"))
pr.revisao("01", "12/10/2026", "PINOS C/ CABEÇA CALCULADOS, CH-MF, CH-MF2, OR-1, CT-1 DETALHADA, TB-1 NO DENTE")
pr.revisao("02", "12/10/2026", "ST-1 SOLDADO NA CH-T (SEM LUVAS NEM CT-1); OR-1 VIRA CHAPA SOLDADA NA CH-MF")
ch = CB["chumbadores"]


def furo(v, c, d):
    v.circulo(c, d / 2, "METALICA")
    v.linha((c[0] - d * 0.8, c[1]), (c[0] + d * 0.8, c[1]), "EIXO")
    v.linha((c[0], c[1] - d * 0.8), (c[0], c[1] + d * 0.8), "EIXO")


def pino(v, c, d=16):
    v.circulo(c, d / 2, "OCULTA")
    v.circulo(c, d, "OCULTA")


# ------------------------------------------------------------------ CH-T1 (1:5)
v = pr.vista("CH-T1", (75, 500), 5, titulo="CH-T1 — PLANTA", subtitulo="6 por peça · 84 na obra")
v.ret(-100, -100, 200, 200, "METALICA")
v.ret(-4, -110, 8, 220, "OCULTA")                                       # ST-1 soldado em cima (ver COB01)
for c in ((-75, -75), (-75, 75), (75, -75), (75, 75)):
    pino(v, c)
v.cota_h([-100, -75, -4, 4, 75, 100], -100, -8, total=False)
v.cota_h([-100, 100], 100, 8)
v.cota_v([-100, -75, -50, 50, 75, 100], 100, 8, total=False)
v.chamada((4, 80), (10, 16), "ST-1 8×220×290 soldado em cima (fábrica) — ND-LET-COB01")
v.chamada((-75, -75), (4, -16), "4 pinos Ø16 c/ cabeça Ø32, L 112")
v.texto((-100, -260), "chapa 200×200×12,5 ASTM A36", "nota")

# ------------------------------------------------------------------ CH-T2 (1:5)
v = pr.vista("CH-T2", (205, 495), 5, titulo="CH-T2 — PLANTA", subtitulo="7 por peça · 98 na obra")
v.ret(-150, -190, 300, 380, "METALICA")
v.ret(-4, -110, 8, 220, "OCULTA")                                       # ST-1 soldado em cima
for so, yo in ((140, 140), (-140, 140), (140, -140), (-140, -140)):
    v.ret(so - 4.75, yo - 45, 9.5, 90, "METALICA")
for sx in (-100, 100):
    for yy in (-150, 0, 150):
        pino(v, (sx, yy))
v.poli([(-120, -170), (-120, 170), (120, 170), (120, -170)], "ARMADURA")
v.cota_h([-150, -140, -100, 0, 100, 140, 150], -190, -8, total=False)
v.cota_h([-150, 150], 190, 8)
v.cota_v([-190, -150, -50, 50, 150, 190], 150, 8, total=False)
v.linha((0, -230), (0, 230), "EIXO")
v.chamada((0, 215), (-6, 8), "eixo da terça / ST-1 soldado em cima")
v.chamada((140, 140), (10, 8), "orelha 90×80×9,5")
v.chamada((100, 0), (16, -26), "6 pinos Ø16 c/ cabeça, L 112")
v.chamada((-120, -170), (-6, -14), "2 grampos U Ø10 c/ gancho 90°, encostados nos pinos")
v.texto((-150, -340), "chapa 300×380×12,5 + 4 orelhas", "nota")

v = pr.vista("CH-T2 — VISTA", (330, 505), 5, titulo="CH-T2 — VISTA LATERAL", subtitulo="orelhas paralelas ao tirante (≈73°)")
v.ret(-190, 0, 380, 12.5, "METALICA")
for yo in (-140, 140):
    v.ret(yo - 45, 12.5, 90, 80, "METALICA")
furo(v, (140, 12.5 + 35), 16)
furo(v, (-140, 12.5 + 70), 16)
v.cota_v([12.5, 47.5, 82.5, 92.5], 205, 8, total=False)
v.cota_h([-190, -185, -95, 95, 185, 190], 0, -8, total=False)
v.chamada((140, 47.5), (8, 12), "furo Ø16 a 35")
v.chamada((-140, 82.5), (-8, 12), "furo Ø16 a 70")

# ------------------------------------------------------------------ CH-A1 (1:5)
v = pr.vista("CH-A1", (470, 505), 5, titulo="CH-A1 — PLANTA", subtitulo="2 por peça (fundo do dente)")
v.ret(-75, -150, 150, 300, "METALICA")
furo(v, (0, 0), 52)
for y in (-120, 120):
    for x in (-45, 45):
        v.circulo((x, y), 5, "OCULTA")
v.cota_h([-75, -45, 45, 75], -150, -8)
v.cota_v([-150, -120, 120, 150], 75, 8)
v.chamada((26, 0), (12, 4), "furo Ø52 (TB-1)")
v.chamada((45, 120), (10, 10), "4 grapas Ø10 L=200")

# ------------------------------------------------------------------ CH-MF, CH-MF2, OR-1 (1:5)
v = pr.vista("CH-MF", (565, 505), 5, titulo="CH-MF — PLANTA", subtitulo="11 por peça (fundo da viga)")
v.ret(-75, -180, 150, 360, "METALICA")
v.ret(-150, -4, 300, 8, "OCULTA")                                       # OR-1 soldada por baixo (ver COB01)
for y in (-100, 100):
    pino(v, (0, y), 12.5)
v.cota_v([-180, -150, -100, 100, 150, 180], 75, 8, total=False)
v.cota_h([-75, 75], -180, -8)
v.chamada((-75, -170), (-6, -14), "OR-1 8×300×100 soldada por baixo (fábrica)")
v.chamada((0, -100), (10, -10), "2 pinos Ø12,5 c/ cabeça, L 90")

v = pr.vista("CH-MF2", (75, 330), 5, titulo="CH-MF2", subtitulo="lateral do dente · 4 por peça")
v.ret(-60, -45, 120, 90, "METALICA")
furo(v, (0, 0), 18)
for x in (-40, 40):
    pino(v, (x, 0), 12.5)
v.cota_h([-60, -40, 0, 40, 60], -45, -8, total=False)
v.cota_v([-45, 45], 60, 8)
v.chamada((0, 0), (8, 16), "luva M16")

v = pr.vista("OR-1", (170, 330), 5, titulo="OR-1 — ORELHA DA MÃO-FRANCESA", subtitulo="chapa 8×300×100 soldada na CH-MF (fábrica)")
v.ret(-150, -100, 300, 100, "METALICA")
v.ret(-150, 0, 300, 12.5, "METALICA")
for x in (-100, 100):
    furo(v, (x, -50), 14)
v.cota_h([-150, -100, 100, 150], -100, -8, total=False)
v.cota_v([-100, -50, 0, 12.5], 150, 8, total=False)
v.chamada((100, -50), (8, -12), "2 furos Ø14 — M12 da mão-francesa (um de cada lado da viga)")
v.chamada((0, 6), (10, 10), "CH-MF (fundo da viga); filete 6 mm nos 2 lados")

# ------------------------------------------------------------------ CT-1 (1:5)
v = pr.vista("ST-1", (300, 345), 5, titulo="ST-1 — SUPORTE DA TERÇA", subtitulo="chapa 8×220×290 soldada na CH-T1/CH-T2 · 13 por viga")
v.ret(-110, 0, 220, 290, "METALICA")
for yy in (-50, 50):
    for zz in (110, 210):
        furo(v, (yy, zz), 14)
furo(v, (0, 255), 18)
v.cota_h([-110, -50, 50, 110], 0, -8, total=False)
v.cota_v([0, 110, 210, 255, 290], 110, 8, total=False)
v.chamada((50, 210), (10, 14), "4 furos Ø14 — 2 M12 por terça (furos a 60 da ponta da terça)")
v.chamada((0, 255), (-14, 10), "furo Ø18 só nos ST-1 de borda (diagonal Ø16)")
v2 = pr.vista("ST-1 PLANTA", (300, 255), 5, titulo="ST-1 — PLANTA", subtitulo="enrijecedores 8×90×90 nos 2 lados, na face oposta às terças")
v2.ret(-110, 0, 220, 8, "METALICA")
for yy in (-45, 45):
    v2.ret(yy - 4, -90, 8, 90, "METALICA")
v2.cota_h([-110, -45, 45, 110], -90, -8, total=False)
v2.cota_v([-90, 0, 8], 110, 8, total=False)
v2.chamada((45, -45), (10, 10), "enrijecedor 8×90×90 (2x)")

# ------------------------------------------------------------------ TB-1, AL-1, PN-1, NEO-1, MF-1
v = pr.vista("TB-1", (420, 300), 10, titulo="TB-1", subtitulo="2 por peça (no dente)")
v.ret(-25, 0, 50, H - HD, "METALICA")
v.cota_v([0, H - HD], 25, 8)
v.cota_h([-25, 25], H - HD, 6)
v.chamada((25, 225), (8, 6), "tubo Ø50×3,0 L=450")
v.chamada((0, 0), (8, -8), "soldado na CH-A1")

v = pr.vista("AL-1", (505, 200), 10, titulo="AL-1", subtitulo="4 por peça · cordoalha Ø12,7")
v.poli([(-50, 0), (-50, 810), (0, 850), (50, 810), (50, 0)], "ARMADURA")
for d in (-50, 50):
    v.linha((d, 0), (d - 40, -80), "ARMADURA"); v.linha((d, 0), (d + 40, -80), "ARMADURA")
v.cota_v([0, 700, 850], 50, 10, total=False)
v.chamada((0, 850), (8, 6), "cordoalha de 1,90 m")

v = pr.vista("PN-1", (580, 230), 10, titulo="PN-1 / PN-2", subtitulo="pino no consolo (interface)")
v.ret(-12.5, 0, 25, 700, "METALICA")
v.linha((-80, 300), (80, 300), "EIXO")
v.cota_v([0, 300, 700], 12.5, 8, total=False)
v.chamada((12.5, 150), (8, 4), "Ø25 CA-50 no consolo")
v.chamada((12.5, 550), (8, 4), "entra no TB-1, grauteado")

v = pr.vista("NEO-1", (75, 210), 5, titulo="NEO-1", subtitulo="neoprene 10 mm, 60 Shore A")
v.ret(-75, -150, 150, 300, "VISTA")
furo(v, (0, 0), 40)
v.cota_h([-75, 75], -150, -8)
v.cota_v([-150, 150], 75, 8)

mf = CB["MF1"]
Lmf = round(mf["comp_m"] * 1000)
v = pr.vista("MF-1", (150, 110), 10, titulo="MF-1 — MÃO-FRANCESA", subtitulo=f"L 50×5, L = {Lmf} · 2 por terça")
v.linha((0, 0), (Lmf, 0), "METALICA"); v.linha((0, 50), (Lmf, 50), "METALICA")
v.linha((0, 0), (0, 50), "METALICA"); v.linha((Lmf, 0), (Lmf, 50), "METALICA")
furo(v, (30, 25), 14); furo(v, (Lmf - 30, 25), 14)
v.cota_h([0, 30, Lmf - 30, Lmf], 0, -8, total=False)
v.chamada((30, 25), (-4, 12), "M12 na OR-1 (chapa soldada)")
v.chamada((Lmf - 30, 25), (4, 12), "M12 na mesa inferior da terça")

# ------------------------------------------------------------------ ISO da ponta
pr.imagem(330, 32, 640, 175, "/home/claude/letsara/pranchas/ISO-TS01-ponta-crop.png", "ISOMÉTRICO — LIGAÇÕES NA PONTA",
          "dente Gerber, terças, ST-1, mão-francesa no fundo e contraventamento")

# ------------------------------------------------------------------ tabelas
x0, y = pr.quadro[2] - 180, pr.quadro[3] - 6
lista = [["CH-T1", "200×200×12,5 + 4 pinos Ø16", 6, 84, "4,6", "386"],
         ["CH-T2", "300×380×12,5 + 4 orelhas + 6 pinos + 2 U", 7, 98, "14,3", "1401"],
         ["CH-A1", "300×150×12,5 + 4 grapas", 2, 28, "5,2", "146"],
         ["CH-MF", "150×360×12,5 + 2 pinos Ø12,5", 11, 154, "5,7", "878"],
         ["CH-MF2", "120×90×9,5 + luva + 2 pinos", 4, 56, "1,3", "73"],
         ["TB-1", "tubo Ø50×3,0 L=450", 2, 28, "1,6", "45"],
         ["AL-1", "cordoalha Ø12,7 L=1,90 m", 4, 56, "1,5", "84"],
         ["ST-1", "chapa 8×220×290 + 2 enrij. (soldado, fábrica)", 13, 182, "5,0", "910"],
         ["OR-1", "chapa 8×300×100 (soldada, fábrica)", 11, 154, "1,9", "293"],
         ["MF-1", f"L 50×5 L={Lmf} (montagem)", 26, 364, "4,8", "1747"],
         ["NEO-1", "neoprene 300×150×10", 2, 28, "-", "-"],
         ["PN-1/2", "pino Ø25 L=700 (no consolo)", 2, 28, "2,7", "76"]]
y = pr.tabela(x0, y, "LISTA DE CHAPARIA — TS-01", ["MARCA", "DESCRIÇÃO", "/PEÇA", "OBRA", "kg/un", "kg obra"], lista,
              [16, 78, 16, 18, 22, 30])
ct1 = CB["CT1"]
cal = [["Pinos CH-T1 (4 Ø16)", f"Nd {f(ch['CH-T1']['Nu'],1)} / Vd {f(ch['CH-T1']['Vu'],1)} kN", f"{f(ch['CH-T1']['interacao'],2)}"],
       ["Pinos CH-T2 + 2 U Ø10", f"Nd {f(ch['CH-T2']['Nu'],1)} / Vd {f(ch['CH-T2']['Vu'],1)} kN", f"{f(ch['CH-T2']['interacao'],2)}"],
       ["Pinos CH-MF (2 Ø12,5)", f"Nd {f(ch['CH-MF']['Nu'],1)} / Vd {f(ch['CH-MF']['Vu'],1)} kN", f"{f(ch['CH-MF']['interacao'],2)}"],
       ["M12 na alma da terça (3,00)", f"{f(ct1['M12_alma']['Fd'],1)} ≤ {f(min(ct1['M12_alma']['corte_Rd'], ct1['M12_alma']['contato_alma_Rd']),1)} kN", f"{f(ct1['M12_alma']['uso'],2)}"],
       ["Solda ST-1 × CH-T (filete 6, 2 lados)", f"V {f(ct1['M16_chapa']['Vd'],1)} kN ≤ 2×220×0,7×6×0,6×485/1,35 /1000 = 232 kN", "0,08"],
       ["Rasgamento da alma (furo a 60 da ponta)", f"{f(ct1['rasgamento_alma']['Fd'],1)} ≤ {f(ct1['rasgamento_alma']['Rd'],1)} kN", f"{f(ct1['rasgamento_alma']['Fd']/ct1['rasgamento_alma']['Rd'],2)}"],
       ["Mão-francesa MF-1", f"{f(mf['Nd_kN'],1)} ≤ {f(mf['NcRd'],1)} kN (λ = {mf['esbeltez']})", f"{f(mf['uso'],2)}"]]
y = pr.tabela(x0, y - 4, "VERIFICAÇÕES (ELU)", ["ITEM", "SOLICITAÇÃO × RESISTÊNCIA", "USO"], cal, [62, 98, 20])
notas = ["Chaparia ASTM A36; pinos com cabeça (stud) fu ≥ 450 MPa soldados por arco. ST-1 e OR-1 soldados às chapas embutidas na fábrica de pré-moldados, com gabarito, após a desforma (ND-LET-COB01, detalhes 1 e 2).",
         "Soldas de filete 5 mm contínuas, E70XX; grapas Ø10 CA-50 com 2 filetes de 40 mm.",
         "Parafusos (montagem): M12 8.8 (terça × ST-1, 2 por ponta; mão-francesa × OR-1 e × terça); furos padrão d + 2 mm; arruelas lisas e de pressão.",
         "CH-T2 é uma só peça para todos os nós: simétrica por rotação de 180°.",
         "Chumbadores pelo ACI 318-19 cap. 17 (cone, arrancamento, aço, borda, pryout), concreto fissurado C50. Grampos U da CH-T2 encostados nos pinos (≤ 25 mm), pernas de 300 com gancho de 90°.",
         "Proteção: galvanização a fogo ou fundo epóxi após a desforma, retocado após a montagem.",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(x0, y - 4, notas, 180)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-TS01-3")
for a in avisos:
    print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
