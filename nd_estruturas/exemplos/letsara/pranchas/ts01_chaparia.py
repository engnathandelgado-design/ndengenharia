"""ND-LET-TS01-3 — TS-01: chaparia e insertos concretados na peça + peças de interface da montagem (A1)."""
import json
from prancha_nd import Prancha
from ts01_dados import P, L, H, DX, f

LG = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/ligacoes.json"))
pr = Prancha("A1", dict(cliente="MARQUE ENGENHARIA", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="TS-01 — CHAPARIA, INSERTOS E PEÇAS DE LIGAÇÃO DA MONTAGEM",
                        desenho="ND-LET-TS01-3", folha="03/03", fase="PARA APROVAÇÃO"))


def furo(v, c, d):
    v.circulo(c, d / 2, "METALICA")
    v.linha((c[0] - d * 0.8, c[1]), (c[0] + d * 0.8, c[1]), "EIXO")
    v.linha((c[0], c[1] - d * 0.8), (c[0], c[1] + d * 0.8), "EIXO")


# ------------------------------------------------------------------ CH-T1 (1:5)
v = pr.vista("CH-T1", (75, 500), 5, titulo="CH-T1 — PLANTA", subtitulo="6 por peça · 84 na obra")
v.ret(-100, -100, 200, 200, "METALICA")
for y in (-50, 50):
    furo(v, (55, y), 18)
for y in (-70, 70):
    v.circulo((-60, y), 5, "OCULTA")
v.cota_h([-100, 55, 100], -100, -8)
v.cota_v([-100, -50, 50, 100], 100, 8)
v.chamada((55, 50), (10, 14), "2 furos Ø18 + luva M16 soldada")
v.chamada((-60, -70), (4, -14), "2 grapas Ø10 L=150")
v.texto((-100, -230), "chapa 200×200×12,5 ASTM A36", "nota")

# ------------------------------------------------------------------ CH-T2 (1:5)
v = pr.vista("CH-T2", (205, 495), 5, titulo="CH-T2 — PLANTA", subtitulo="7 por peça · 98 na obra")
v.ret(-150, -190, 300, 380, "METALICA")
for y in (-50, 50):
    furo(v, (55, y), 18)
for so, yo in ((140, 140), (-140, 140), (140, -140), (-140, -140)):
    v.ret(so - 4.75, yo - 45, 9.5, 90, "METALICA")
for y in (-120, 120):
    v.circulo((0, y), 5, "OCULTA")
v.cota_h([-150, -140, 0, 55, 140, 150], -190, -8, total=False)
v.cota_h([-150, 150], 190, 8)
v.cota_v([-190, -140, -50, 50, 140, 190], 150, 8)
v.linha((0, -230), (0, 230), "EIXO")
v.chamada((0, 215), (-6, 8), "eixo da terça")
v.chamada((140, 140), (10, 8), "orelha 90×80×9,5")
v.texto((-150, -330), "chapa 300×380×12,5 + 4 orelhas; 2 grapas Ø10", "nota")

v = pr.vista("CH-T2 — VISTA", (330, 500), 5, titulo="CH-T2 — VISTA LATERAL", subtitulo="orelhas paralelas ao tirante (≈72°)")
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
v = pr.vista("CH-A1", (465, 500), 5, titulo="CH-A1 — PLANTA", subtitulo="2 por peça · 28 na obra")
v.ret(-75, -150, 150, 300, "METALICA")
furo(v, (0, 0), 52)
for y in (-120, 120):
    for x in (-45, 45):
        v.circulo((x, y), 5, "OCULTA")
v.cota_h([-75, -45, 45, 75], -150, -8)
v.cota_v([-150, -120, 120, 150], 75, 8)
v.chamada((26, 0), (12, 4), "furo Ø52 (TB-1)")
v.chamada((45, 120), (10, 10), "4 grapas Ø10 L=300")
v.texto((-75, -260), "chapa 300×150×12,5; face no fundo da fôrma", "nota")

# ------------------------------------------------------------------ TB-1, TB-2, AL-1, PN-1, NEO-1, cantoneira, mão-francesa
v = pr.vista("TB-1", (60, 245), 10, titulo="TB-1", subtitulo="2 por peça")
v.ret(-25, 0, 50, H, "METALICA")
v.ret(-25, 0, 50, H, "OCULTA")
v.cota_v([0, H], 25, 8)
v.cota_h([-25, 25], H, 6)
v.chamada((25, 450), (8, 6), "tubo Ø50×3,0 L=900")
v.chamada((0, 0), (8, -8), "soldado na CH-A1")

v = pr.vista("TB-2", (150, 330), 5, titulo="TB-2", subtitulo="13 por peça")
v.ret(-75, -12.5, 150, 25, "METALICA")
v.cota_h([-75, 75], -12.5, -8)
v.chamada((75, 0), (8, 8), "tubo Ø25×2,0 (furo Ø21) — parafuso M16")

v = pr.vista("AL-1", (150, 200), 10, titulo="AL-1", subtitulo="4 por peça · cordoalha Ø12,7 CP-190 RB")
v.poli([(-50, 0), (-50, 810), (0, 850), (50, 810), (50, 0)], "ARMADURA")
for d in (-50, 50):
    v.linha((d, 0), (d - 40, -80), "ARMADURA"); v.linha((d, 0), (d + 40, -80), "ARMADURA")
v.cota_v([0, 700, 850], 50, 10, total=False)
v.chamada((0, 850), (8, 6), "comprimento da cordoalha 1,90 m")
v.chamada((-50, 350), (-8, 6), "2 pernas")

v = pr.vista("PN-1", (260, 230), 10, titulo="PN-1 / PN-2", subtitulo="pino no consolo / berço (interface)")
v.ret(-12.5, 0, 25, 700, "METALICA")
v.linha((-80, 300), (80, 300), "EIXO")
v.cota_v([0, 300, 700], 12.5, 8, total=False)
v.chamada((12.5, 150), (8, 4), "Ø25 CA-50 no consolo")
v.chamada((12.5, 550), (8, 4), "entra no TB-1, grauteado")

v = pr.vista("NEO-1", (355, 300), 5, titulo="NEO-1", subtitulo="neoprene 10 mm, dureza 60 Shore A")
v.ret(-75, -150, 150, 300, "VISTA")
furo(v, (0, 0), 40)
v.cota_h([-75, 75], -150, -8)
v.cota_v([-150, 150], 75, 8)

v = pr.vista("CANTONEIRA DA TERÇA", (470, 300), 5, titulo="CT-1 — CANTONEIRA DA TERÇA", subtitulo="L 102×102×9,5 L=200")
v.poli([(0, 0), (102, 0), (102, 9.5), (9.5, 9.5), (9.5, 102), (0, 102)], "METALICA", fechada=True)
furo(v, (55, 4.75), 18)
furo(v, (4.75, 60), 14)
v.cota_h([0, 55, 102], 0, -8, total=False)
v.cota_v([0, 60, 102], 0, -8, total=False)
v.chamada((55, 9.5), (10, 14), "2 M16 na CH-T1")
v.chamada((9.5, 60), (8, 10), "2+2 M12 nas almas das terças")

v = pr.vista("MÃO-FRANCESA", (560, 230), 10, titulo="MF-1 — MÃO-FRANCESA", subtitulo="L 50×5, 2 por terça")
v.linha((0, 0), (700, 300), "METALICA"); v.linha((0, 8), (700, 308), "METALICA")
furo(v, (25, 15), 18); furo(v, (675, 293), 14)
v.cota((0, 0), (700, 0), -8, 0)
v.cota((700, 0), (700, 300), 8, 90)
v.chamada((25, 15), (-6, -10), "M16 no TB-2")
v.chamada((675, 293), (-4, 8), "M12 na mesa inferior da terça")

# ------------------------------------------------------------------ ISO da ponta
pr.imagem(30, 32, 300, 160, "/home/claude/letsara/pranchas/ISO-TS01-ponta-crop.png", "ISOMÉTRICO — LIGAÇÕES NA PONTA",
          "terças, cantoneiras, mão-francesa e contraventamento")

# ------------------------------------------------------------------ tabelas
x0, y = pr.quadro[2] - 180, pr.quadro[3] - 6
lista = [["CH-T1", "200×200×12,5 + 2 luvas + 2 grapas", 6, 84, "4,6", "386"],
         ["CH-T2", "300×380×12,5 + 4 orelhas + 2 grapas", 7, 98, "13,2", "1294"],
         ["CH-A1", "300×150×12,5 + 4 grapas", 2, 28, "5,2", "146"],
         ["TB-1", "tubo Ø50×3,0 L=900", 2, 28, "3,2", "90"],
         ["TB-2", "tubo Ø25×2,0 L=150", 13, 182, "0,2", "36"],
         ["AL-1", "cordoalha Ø12,7 L=1,90 m", 4, 56, "1,5", "84"],
         ["CT-1", "L 102×102×9,5 L=200 (montagem)", 13, 182, "2,9", "528"],
         ["MF-1", "L 50×5 L≈780 (montagem)", 26, 364, "2,9", "1056"],
         ["NEO-1", "neoprene 300×150×10 (montagem)", 2, 28, "-", "-"],
         ["PN-1/2", "pino Ø25 L=700 (no pilar/berço)", 2, 28, "2,7", "76"]]
y = pr.tabela(x0, y, "LISTA DE CHAPARIA — TS-01", ["MARCA", "DESCRIÇÃO", "/PEÇA", "OBRA", "kg/un", "kg obra"], lista,
              [16, 78, 16, 18, 22, 30])
ct = LG["contraventamento"]
lg = [["Pino × TB-1", "28", f"{max(a['dist_mm'] for a in LG['apoios']):.1f} mm"],
      ["Terça × CH-T", "14 vigas", f"{max(t['dist_mm'] for t in LG['tercas']):.1f} mm"],
      ["Tirante × terça do nó", f"{ct['n_tirantes']}", f"folga {ct['folga_min_terca_mm']} mm"],
      ["Tirante × tirante", "cruz.", f"folga {f(ct['folga_cruzamento_mm'],1)} mm"],
      ["Berço BR-1 (I110)", "5 linhas", f"{f(LG['berco_I110'][0]['desnivel_mm'],1)} mm de desnível"]]
y = pr.tabela(x0, y - 4, "COMPATIBILIDADE NO MODELO 3D", ["LIGAÇÃO", "N", "RESULTADO"], lg, [70, 30, 80])
notas = ["Chaparia ASTM A36; tubos NBR 5590 ou equivalente; luvas M16 classe 8.8 soldadas por baixo da chapa, tamponadas.",
         "Soldas de filete 5 mm contínuas, eletrodo E70XX; grapas Ø10 CA-50 soldadas com 2 filetes de 40 mm.",
         "Chapas de topo niveladas no plano da mesa com gabarito fixo à fôrma, nas posições da folha 01 (cotas ordenadas).",
         "CH-T2 é uma só peça para todos os nós: simétrica por rotação de 180°; as orelhas ficam paralelas ao tirante (≈72° com o eixo da viga).",
         f"Tirantes Ø12,5 A36 com rosca M12 nas pontas e esticador; maior comprimento {f(ct['comp_max_m'],2)} m; furos Ø16 na alma da terça intermediária a 35 e 70 mm do apoio.",
         "Proteção: galvanização a fogo ou fundo epóxi após a desforma, retocado após a solda de montagem.",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(x0, y - 4, notas, 180)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-TS01-3")
for a in avisos:
    print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
