"""ND-LET-ES01 — escada metálica INTERNA do mezanino (rev09d, DEC-045/055/060): escada em U do térreo ao piso pronto +3,95,
22 espelhos de 17,95 × piso 28, patamar +1,975 e chegada +3,95. Plantas e corte projetados direto das peças de escadas.json
(escadas_detalhe.py: fonte única do 3D/IFC, das ligações verificadas e da lista); guarda-corpos e corrimãos na ND-LET-ES03.
Tudo parafusado, sem solda. Cotas em mm. A1."""
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from prancha_nd import Prancha
from geometria import ESCADA, P6_ESC, P7_ESC, P6_L2, Y_LIN, X_EIXO, ABERTURA, Z_PISO_PRONTO
import escadas_vista as E

EJ, I = E.EJ, E.EJ["interna"]
f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
M = lambda v: round(v * 1000)
V = I["vigas"]
ZP = M(ESCADA["z_patamar"])
L1 = ("EI-L1", "GI-1", "GI-2")
L2 = ("EI-L2", "GI-3", "GI-4")
PAT = ("GI-5", "GI-6", "GI-7", "GI-R")
de = lambda pc, nomes: any(E.cod(pc) == n or E.cod(pc).startswith(n + "-") for n in nomes)

pr = Prancha("A1", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="ESCADA METÁLICA INTERNA DO MEZANINO (TÉRREO → +3,95) — PLANTAS, CORTE, LIGAÇÕES PARAFUSADAS E LISTA DE MATERIAL",
                        desenho="ND-LET-ES01", folha="01/01", fase="PARA APROVAÇÃO", rev="04"))
pr.revisao("00", "23/10/2026", "EMISSÃO INICIAL (DEC-045): ESCADA EM U, PATAMAR +1,95 E CHEGADA +3,90")
pr.revisao("01", "24/10/2026", "BASE METÁLICA BM-1 NO TÉRREO (PÉ DO LANCE 1 E 1º DEGRAU); LIGAÇÕES SEM SOLDA (CANTONEIRAS)")
pr.revisao("02", "24/10/2026", "SEM TABELA DE VERIFICAÇÕES (MEMÓRIA MC09); REFERÊNCIA À ESCADA EXTERNA ND-LET-ES02")
pr.revisao("03", "24/10/2026", "DEC-055: CHEGADA NO PISO PRONTO +3,95 — 22 ESPELHOS DE 17,95, PATAMAR +1,975")
pr.revisao("04", "24/10/2026", "DEC-060: GUARDA-CORPOS E CORRIMÃOS (RT CBMRS 11, ES03), PERFIS NO LIMITE, VIGAS EM ASSENTOS SA, LIGAÇÕES VERIFICADAS")
pr.revisao("09", "25/10/2026", "DEC-062: CORRIMÃO DUPLO 0,92 / 0,70 (RT CBMRS 11 + NBR 9050); DETALHES NAS ND-LET-ES04 / ES05")
Q = pr.quadro
XC = Q[2] - 190
pr.cabecalho_peca("ES", "ESCADA METÁLICA INTERNA EM U — 2 LANCES DE 11 ESPELHOS (17,95 × 28) — PATAMAR +1,975 E CHEGADA +3,95",
                  f"entre o P6 (25 × 40), o P7 (40 × 60) e a linha 2 · longarinas {I['longarina']['perfil']} · massa {f(EJ['massa_kg']['interna'] * 1.03, 0)} kg com parafusos · ASTM A36 / A572-50 galvanizado · tudo parafusado",
                  largura=XC - Q[0] - 10)


def pilar(v, x, y, bx, by):
    pts = [(x - bx / 2, y - by / 2), (x + bx / 2, y - by / 2), (x + bx / 2, y + by / 2), (x - bx / 2, y + by / 2)]
    v.poli(pts, "CORTADO", fechada=True); v.hachura(pts, "AR-CONC", 0.03)


def camada(pc):
    c = E.cod(pc)
    if c.startswith(("graute",)) or "concreto" in pc["marca"]:
        return None
    if E.guarda(pc):
        return "VISTA"
    if "-DG" in c or c.startswith("CH-P"):
        return "VISTA"
    return "METALICA"


PL_XY = lambda x, y, z: (x * 1000, y * 1000)
# ------------------------------------------------------------------ PLANTAS 1:50
def lab(v, org, pt, lado, dy, texto):
    """chamada com o texto numa coluna fora do desenho da planta (x 35,70 à esquerda / 40,30 à direita)."""
    xcol = 35600 if lado < 0 else 40000
    v.chamada(pt, ((xcol - pt[0]) / 50, dy), texto)


for k, (px, titulo, sub) in enumerate(((Q[0] + 20, "PLANTA NO PATAMAR +1,975", "lance 1, patamar +1,975 e guarda-corpos (térreo → +1,975)"),
                                       (Q[0] + 166, "PLANTA NA CHEGADA +3,95", "lance 2, chegada +3,95 e guarda-corpos da abertura da laje"))):
    v = pr.vista(f"PLANTA {k + 1}", (px - 34800 / 50, Q[3] - 190 - 3000 / 50), 50, titulo=titulo, subtitulo=sub, unidade="mm")
    yl2 = M(Y_LIN[1])
    v.eixo((35300, yl2), (40300, yl2), 400); v.circulo((34500, yl2), 300, "VISTA"); v.texto((34500, yl2), "2", "nota", "MIDDLE_CENTER")
    xe = M(X_EIXO["E"])
    v.eixo((xe, 3000), (xe, 9700), 400); v.circulo((xe, 10600), 300, "VISTA"); v.texto((xe, 10600), "E", "nota", "MIDDLE_CENTER")
    pilar(v, M(P6_ESC[0]), M(P6_ESC[1]), 250, 400); pilar(v, M(P7_ESC[0]), M(P7_ESC[1]), 600, 400)
    pilar(v, M(P6_L2[0]), M(P6_L2[1]), 250, 400); pilar(v, xe, yl2, 600, 400)
    v.texto((M(P6_ESC[0]), M(P6_ESC[1]) - 300), "P6", "min", "TOP_CENTER"); v.texto((M(P7_ESC[0]) - 350, M(P7_ESC[1]) - 250), "P7", "min", "TOP_RIGHT")
    v.ret(M(ABERTURA["x0"]), M(ABERTURA["y0"]), M(ABERTURA["x1"] - ABERTURA["x0"]), M(ABERTURA["y1"] - ABERTURA["y0"]), "OCULTA")
    if k == 0:
        filt = lambda pc: E.interna(pc) and not de(pc, L2) and (E.zmin(pc) < 2.05 or de(pc, L1 + PAT))
    else:
        filt = lambda pc: E.interna(pc) and E.zmax(pc) > 1.99 and not de(pc, L1 + PAT) and not (E.cod(pc) == "PL" and E.zmax(pc) < 2.2)
    E.projetar(v, PL_XY, filt, tf=camada)
    if k == 0:
        for cc, lado, dy, tx in (("VP-1", 1, 6, "VP-1 W 150 × 13,0"), ("VP-2", 1, -6, "VP-2 (SA-1)"), ("VP-5", -1, -4, "VP-5 borda"),
                                 ("EI-L1 ", -1, 4, "EI-L1 U 152"), ("BM-1", -1, 4, "BM-1 (det. 4)"), ("GI-1 corr", -1, -6, "GI-1"), ("GI-5 corr", 1, -10, "GI-5"),
                                 ("PL ", 1, 10, "PL (det. 3)")):
            lab(v, None, E.centro(cc, PL_XY, filt), lado, dy, tx)
    else:
        for cc, lado, dy, tx in (("VP-3", -1, -6, "VP-3 (balanço)"), ("VP-4", -1, -4, "VP-4 (SA-2)"), ("VP-6", 1, 4, "VP-6 borda"),
                                 ("EI-L2 ", 1, -6, "EI-L2 U 152"), ("GI-10 corr", -1, -4, "GI-10 (laje)"), ("GI-11 corr", 1, -8, "GI-11 (laje)"),
                                 ("GI-8 corr", -1, 10, "GI-8")):
            lab(v, None, E.centro(cc, PL_XY, filt), lado, dy, tx)
    v.cota_h([36300, M(I["vigas"]["VP1"]["x1"])], 3300, -8, total=False)

# ------------------------------------------------------------------ CORTE A-A 1:25 (plano y-z, olhando para +x: lance 1 em vista, lance 2 ao fundo)
YZ = lambda x, y, z: (y * 1000, z * 1000)
c = pr.vista("CORTE A-A", (Q[0] + 330 - 3500 / 25, Q[3] - 275), 25, titulo="CORTE A-A — LANCE 1 EM VISTA (OLHANDO PARA O EIXO E)",
             subtitulo="peças do modelo 3D; lance 2 ao fundo (oculto); pé-direito livre ≥ 2,10 m em toda a faixa de circulação", unidade="mm")
c.linha((3300, 0), (10000, 0), "TERRENO")
E.projetar(c, YZ, E.interna, tf=lambda pc: None if camada(pc) is None else ("OCULTA" if E.bbox(pc)[0][0] > 37.70 and not E.cod(pc).startswith("VP") else camada(pc)))
for yy in (M(P6_ESC[1]), M(Y_LIN[1])):
    c.ret(yy - 200, -300, 400, Z_PISO_PRONTO * 1000 + 900, "VISTA"); c.interrupcao((yy - 200, 4500), (yy + 200, 4500))
c.ret(M(P6_ESC[1]) - 200 - 900, 3650, 900, 250, "CORTADO")
c.cota_v([0, ZP, M(Z_PISO_PRONTO)], 9900, 10, total=False)
c.cota_h([M(V["VP2"]["eixo"]), M(V["VP1"]["eixo"]), M(V["VP3"]["eixo"]), M(V["VP4"]["eixo"])], -300, -10, total=True)
c.texto((M(V["VP2"]["eixo"]) + 200, ZP + 1150), "patamar +1,975", "min", "BOTTOM_LEFT")
c.texto((M(V["VP3"]["eixo"]) + 100, M(Z_PISO_PRONTO) + 1150), "chegada +3,95", "min", "BOTTOM_LEFT")
pd = min(p["pe_direito_min_m"] for p in EJ["pe_direito"] if p["pe_direito_min_m"])
c.texto((5600, 6000), f"pé-direito mínimo {f(pd, 2)} m (chegada, sob o fundo da laje +7,30)", "min", "BOTTOM_LEFT")
for cc, dxy, tx in (("EI-L1-T", (-30, -10), "topo do lance (det. 5)"), ("EI-L1-DG", (12, -6), "degrau (det. 1)"), ("SA-1", (-20, -12), "SA-1 (det. 2)"),
                    ("GI-1 corr", (8, 14), "corrimão duplo 0,92 / 0,70 · guarda 0,92 (ES03/ES04)")):
    c.chamada(E.centro(cc, YZ), dxy, tx)

# ------------------------------------------------------------------ DETALHES 1:5
lg = {l["cod"]: l for l in EJ["ligacoes"]}
d1 = pr.vista("DETALHE 1", (Q[0] + 30, Q[1] + 190), 5, titulo="DETALHE 1 — DEGRAU NA LONGARINA", subtitulo=lg["EI-L1-1"]["furos"], unidade="mm")
d1.ret(0, 0, 48.8, 152.4, "METALICA"); d1.ret(5.1, 0, 43.7, 8.7, "VISTA"); d1.ret(5.1, 143.7, 43.7, 8.7, "VISTA")
d1.ret(48.8, 70, 4.8, 51, "METALICA"); d1.ret(48.8, 121, 51, 4.8, "METALICA")
d1.poli([(53.6, 125.8), (330, 125.8), (330, 90)], "METALICA")
for zz in (85, 105):
    d1.circulo((24, zz), 5.5, "METALICA")
d1.circulo((75, 123), 4.5, "METALICA")
d1.cota_v([0, 121, 152.4], -20, -8, total=False)
d1.chamada((24, 105), (6, 28), "2 M10 8.8 (alma)")
d1.chamada((75, 125.8), (10, 18), "1 M8 escareado")
d1.chamada((250, 125.8), (8, 10), "DG chapa xadrez 4,75 dobrada")
d1.chamada((60, 80), (16, -14), "CT L 51 × 51 × 4,8 × 80")
d1.chamada((24, 30), (-10, -14), I["longarina"]["perfil"].split(" (")[0])
d2 = pr.vista("DETALHE 2", (Q[0] + 240, Q[1] + 190), 5, titulo="DETALHE 2 — VIGA NO ASSENTO SA-1", subtitulo=lg["EI-SA"]["furos"], unidade="mm")
pts = [(-200, -150), (0, -150), (0, 260), (-200, 260)]
d2.poli(pts, "CORTADO", fechada=True); d2.hachura(pts, "AR-CONC", 0.03)
d2.ret(0, 0, 9.5, 102, "METALICA"); d2.ret(0, 92.5, 152, 9.5, "METALICA")
d2.ret(10, 102, 98, 3.6, "METALICA"); d2.ret(57.5, 105.6, 3.1, 138.8, "METALICA"); d2.ret(10, 244.4, 98, 3.6, "METALICA")
for zz in (30, 70):
    d2.linha((-150, zz), (25, zz), "METALICA")
d2.circulo((35, 97), 6.5, "METALICA"); d2.circulo((85, 97), 6.5, "METALICA")
d2.cota_v([0, 102, 248], -230, -8, total=False)
d2.chamada((-100, 30), (-6, -40), "2 BR-M16 8.8 embutidas 150 + grampo (fábrica do pilar)")
d2.chamada((85, 97), (18, -24), "2 M12 na mesa inferior")
d2.chamada((120, 97), (16, -6), "SA-1 L 152 × 102 × 9,5 × 160")
d2.chamada((59, 180), (14, 14), "VP-2 W 150 × 9,2")
d3 = pr.vista("DETALHE 3", (Q[0] + 400, Q[1] + 190), 5, titulo="DETALHE 3 — PILARETE (TOPO E BASE)", subtitulo="tubo 60 × 60 × 2 + 2 L 76 × 76 × 6,3 × 100 em cada ponta", unidade="mm")
d3.ret(-30, 20, 60, 230, "METALICA"); d3.ret(-60, 0, 120, 20, "VISTA"); d3.linha((-200, 0), (200, 0), "TERRENO")
for sg in (-1, 1):
    x0 = 30 if sg > 0 else -30 - 6.3
    d3.ret(x0, 20, 6.3, 76, "METALICA"); d3.ret(30 if sg > 0 else -106, 20, 76, 6.3, "METALICA")
    d3.linha((sg * 70, -100), (sg * 70, 35), "METALICA")
    d3.ret(x0, 250 - 76, 6.3, 76, "METALICA"); d3.ret(30 if sg > 0 else -106, 250 - 6.3, 76, 6.3, "METALICA")
d3.ret(-49, 250, 98, 3.6, "METALICA"); d3.ret(-1.55, 253.6, 3.1, 60, "METALICA")
d3.linha((-45, 60), (45, 60), "METALICA"); d3.linha((-45, 215), (45, 215), "METALICA")
d3.chamada((70, -60), (14, -8), "2 chumbadores químicos M12 hef 100")
d3.chamada((40, 60), (16, 6), "1 M12 passante no tubo (base e topo)")
d3.chamada((-60, 250), (-14, 10), "2 M12 na mesa (a 25 da alma)")
d3.chamada((-50, 10), (-12, -6), "graute 20")
d4 = pr.vista("DETALHE 4", (Q[0] + 548, Q[1] + 190), 5, titulo="DETALHE 4 — BASE METÁLICA BM-1", subtitulo="U 152 em pé entre as longarinas: pé do lance 1 e 1º degrau", unidade="mm")
d4.linha((-170, 0), (300, 0), "TERRENO")
d4.ret(-60, 10, 48.8, 8.7, "METALICA"); d4.ret(-60, 10, 5.1, 152.4, "METALICA"); d4.ret(-60, 153.7, 48.8, 8.7, "METALICA")
d4.ret(-80, 0, 100, 10, "VISTA")
d4.ret(-136, 10, 76, 6.3, "METALICA"); d4.ret(-66.3, 10, 6.3, 76, "METALICA")
d4.linha((-100, -90), (-100, 25), "METALICA")
d4.ret(-11.2, 30, 6.3, 100, "METALICA"); d4.ret(-11.2, 30, 76, 6.3, "METALICA")
d4.poli([(-4.9, 40), (200, 160)], "METALICA")
d4.cota_v([0, 10, 162.4], -200, -8, total=False)
d4.chamada((-100, -60), (14, -10), "CB-1 L 76 + chumbador químico M12 hef 100 (3)")
d4.chamada((-36, 100), (-12, 18), "BM-1 U 152 × 12,2")
d4.chamada((30, 33), (14, -12), lg["EI-L1-P"]["furos"].replace("; ", " "))
d4.chamada((-60, 5), (-20, -8), "graute 10")
d5 = pr.vista("DETALHE 5", (Q[0] + 60, Q[1] + 130), 5, titulo="DETALHE 5 — TOPO DO LANCE NA VIGA", subtitulo=lg["EI-L1-T"]["furos"], unidade="mm")
d5.ret(-49, 0, 98, 3.6, "METALICA"); d5.ret(-1.55, 3.6, 3.1, 138.8, "METALICA"); d5.ret(-49, 142.4, 98, 3.6, "METALICA")
d5.ret(1.55, 30, 6.3, 80, "METALICA"); d5.ret(1.55, 30, 102, 6.3, "METALICA")
d5.ret(60, 10, 5.1, 130, "METALICA")
for zz in (50, 90):
    d5.circulo((30, zz), 6.5, "METALICA") if False else d5.linha((-20, zz), (10, zz), "METALICA")
    d5.linha((50, zz), (80, zz), "METALICA")
d5.chamada((-5, 90), (-14, 10), "2 M12 na alma da viga")
d5.chamada((65, 50), (14, -10), "2 M12 na alma da longarina")
d5.chamada((50, 33), (14, 12), "L 102 × 102 × 6,3 × 80")

# ------------------------------------------------------------------ lista e notas
y = Q[3] - 6
lin = E.linhas_lista("interna", f)
massa = EJ["massa_kg"]["interna"]
lin.append(["", "parafusos M8/M10/M12 8.8 galv., chumbadores químicos M12, BR-M16 embutidas (+3 %)", "", f(massa * 0.03, 0)])
lin.append(["", "TOTAL", "", f(massa * 1.03, 0)])
y = pr.tabela(XC, y, "LISTA DE MATERIAL — ESCADA INTERNA (escadas_detalhe.py)", ["ITEM", "DESCRIÇÃO", "QT", "kg"], lin, [16, 124, 10, 20], h_lin=4.4, destaque_ultima=True)
notas = [f"Cargas (NBR 6120:2019): sobrecarga {f(EJ['cargas']['q_kN_m2'])} kN/m²; guarda-corpo {f(EJ['cargas']['guarda_corpo_kN_m'], 2)} kN/m no topo e {f(EJ['cargas']['fechamento_kPa'], 2)} kPa no fechamento; corrimão {f(EJ['cargas']['corrimao_kN'], 2)} kN (RT CBMRS 11). ELU 1,4 G + 1,5 Q; flecha L/350.",
         f"Geometria: 22 espelhos de {f(ESCADA['espelho'] * 100, 2)} cm e piso de 28 cm; patamar +1,975 e chegada no piso pronto +3,95 do mezanino (abertura da laje entre o P6, o P7 e a linha 2 — ND-LET-LA01).",
         f"Perfis no limite (o mais leve que passa): longarinas {I['longarina']['perfil']} (uso {f(I['longarina']['uso'], 2)}; o U 102 não comporta a cantoneira do degrau); VP-1 {I['viga_patamar_frente']['perfil']} (uso {f(I['viga_patamar_frente']['uso'], 2)}); demais vigas W 150 × 9,2; barrotes {I['barrote']['perfil']}; pilaretes {I['pilarete_chegada']['perfil']} (uso {f(I['pilarete_chegada']['uso'], 2)}).",
         "Vigas de fundo VP-2 e VP-4 apoiadas em assentos SA-1/SA-2 (cantoneiras nas faces do P6, do P7, do P6 da linha 2 e do P2, com 2 BR-M16 embutidas na fábrica do pilar); VP-3 em balanço até a borda da laje; vigas de borda VP-5/VP-6 recebem os montantes do guarda-corpo.",
         f"Ligações todas parafusadas, SEM SOLDA, conferidas uma a uma em escadas_detalhe.py (furos nas duas peças, bordas, espaçamentos, folga de chave, faixa comum de altura, corte e contato — NBR 8800:2024 6.3): {len(EJ['ligacoes'])} ligações, {EJ['n_conflitos']} conflitos; 3D sem colisões.",
         "Guarda-corpos e corrimãos (RT CBMRS nº 11 Parte 01/2016): corrimão DUPLO nos dois lados de cada lance a 0,92 e 0,70 m (NBR 9050), guarda-corpo 0,92 m nos lances e 1,05 m nos patamares e na abertura da laje — elevações, fixações e tabela na ND-LET-ES03.",
         "Aço: W em ASTM A572 Gr. 50; U, cantoneiras, chapas e tubos em ASTM A36; galvanização a fogo após a fabricação. Montagem depois da capa do +3,90: assentos e VP-2/VP-4 → pilaretes, VP-1 e VP-3 → longarinas e degraus → pisos → guarda-corpos.",
         "Cotas em mm, níveis em m. Conferir na obra as faces dos pilares antes de fabricar. Não medir no desenho."]
pr.notas(XC, y - 4, notas, 182)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-ES01")
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
for a in avisos:
    print(a)
