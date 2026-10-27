"""ND-LET-LOC01 — PLANTA DE LOCAÇÃO DOS PILARES (rev07): eixos A–E e 1–9 com bolhas nos quatro lados, cotas parciais e
acumuladas, marca de fabricação, posição e seção de cada pilar, faces A (interna) e C (placas), pilares fora dos eixos cotados,
detalhes típicos de locação 1:25. A0, planta 1:100, cotas em cm. (Corte do pórtico e apoios: ND-LET-CT01 a CT04.)"""
import json, math
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from prancha_nd import Prancha
from geometria import Y_LIN, X_EIXO, PILARES_ESPECIAIS, Y_P13, Y_PC_C, PG_L4, y_canto, DY_CANTO
from familia_pl import marca_de

f = lambda v, d=2: f"{v:.{d}f}".replace(".", ",")
YL = [round(y * 1000) for y in Y_LIN]
XA = {k: round(v * 1000) for k, v in X_EIXO.items()}
Lx, Ly = YL[-1], XA["E"]
MARCA_ESP = {("P8", 9870): "PM-01", ("P8B", 29630): "PM-02", ("P8A", 19750): "PC-01", ("P11", 19750): "PC-02", ("P13", 19750): "PC-03", ("P13B", 19750): "PC-03"}
MARCA_ESP.update({(r01, round(x * 1000)): mk for mk, (r01, x, _, _) in PG_L4.items()})      # rev12: PG-02/PG-04 25×40 deslocados
X_PG2, X_PG4 = round(PG_L4["PG-02"][1] * 1000), round(PG_L4["PG-04"][1] * 1000)
DYC = round(DY_CANTO * 1000)

pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="PLANTA DE LOCAÇÃO DOS PILARES — EIXOS, MARCAS, SEÇÕES E FACES",
                        desenho="ND-LET-LOC01", folha="01/01", fase="PARA APROVAÇÃO", rev="07"))
pr.revisao("03", "14/10/2026", "TS-01 SEM DENTES; COBERTURA REBAIXADA; I120; PLACAS 10 cm")
pr.revisao("04", "16/10/2026", "NBR 9062: SEM VT; VB 15×60 COM DENTE")
pr.revisao("05", "17/10/2026", "TERÇAS Z 302 CONTÍNUAS POR TRANSPASSE")
pr.revisao("06", "20/10/2026", "X DA COBERTURA NOS VÃOS 4-5 A 8-9; VB-01 A VB-08")
pr.revisao("07", "21/10/2026", "SÓ LOCAÇÃO DOS PILARES (1:100): EIXOS NOS 4 LADOS, MARCAS, FACES; CORTES NAS CT01 A CT04")
pr.revisao("09", "23/10/2026", "DEC-045: P6 E P7 DA ESCADA E P6 DA LINHA 2 (PE-01 A PE-03); NOMES NOVOS")
pr.revisao("10", "24/10/2026", "DEC-058: EIXO C COM 2 PC-03 40×40 (y 46,317 E 62,833), 3 VÃOS DE 16,517 m; NOMES P23 A P37")

# ------------------------------------------------------------------ pilares: (marca, posição, x_planta=y obra, y_planta=x obra, bx_planta, by_planta, faces)
pil = []
for i, y in enumerate(YL, start=1):
    for lado, xo in (("P1", 0), ("P2", Ly)):
        pos = f"{lado}{'C' if i in (1, 9) else ''}-L{i}"
        yc = (y - DYC if i == 1 else y + DYC) if i in (1, 9) else y         # rev12 (opção D): canto 10 cm para fora da linha
        pil.append((marca_de(f"{lado}-L{i}"), pos, yc, xo, 400, 600, "lat", lado))
for nome, x, y, bx, by in PILARES_ESPECIAIS:
    xm, ym = round(x * 1000), round(y * 1000)
    if nome in ("P6", "P7"):                                   # rev09 (DEC-045): P6/P7 da escada e P6 da linha 2 entram no projeto (PE)
        mk = {(36175, 3790): "PE-01", (39500, 3790): "PE-02", (36175, 9650): "PE-03"}[(xm, ym)]
        pil.append((mk, nome + (" (linha 2)" if ym == 9650 else " (escada)"), ym, xm, round(by * 1000), round(bx * 1000), "int", nome))
        continue
    if ym in (0, Lx):
        mk = marca_de(f"{nome}-L{1 if ym == 0 else 9}")
        pil.append((mk, f"{nome}-L{1 if ym == 0 else 9}", ym, xm, round(by * 1000), round(bx * 1000), "fach", "L1" if ym == 0 else "L9"))
    else:
        pil.append((MARCA_ESP[(nome, xm)], nome, ym, xm, round(by * 1000), round(bx * 1000), "int", nome))

# ------------------------------------------------------------------ PLANTA 1:100
E = 100
v = pr.vista("PLANTA", (118, 395), E, titulo="PLANTA DE LOCAÇÃO DOS PILARES",
             subtitulo="eixos do R01 (Marques); pilares centrados nos eixos, exceto onde cotado", unidade="cm")
EXT = 2400                                        # eixos passam 2,4 m além dos eixos extremos (por fora das cotas)
RB = 650                                           # raio da bolha (6,5 mm)
DB = EXT + 50 + RB                                # centro da bolha a partir do eixo extremo
for k, y in enumerate(YL):
    v.eixo((y, 0), (y, Ly), EXT)
    for xb in (-DB, Ly + DB):
        v.circulo((y, xb), RB, "BOLHA"); v.texto((y, xb), str(k + 1), "sub", "MIDDLE_CENTER")
for nome, x in XA.items():
    v.eixo((0, x), (Lx, x), EXT)
    for yb in (-DB, Lx + DB):
        v.circulo((yb, x), RB, "BOLHA"); v.texto((yb, x), nome, "sub", "MIDDLE_CENTER")
# contorno das placas (por fora dos pilares, folga 2,5 + 10) — referência
o = 425                                            # face externa das placas: face do pilar (30) + folga 2,5 + placa 10
v.poli([(-o, -o), (Lx + o, -o), (Lx + o, Ly + o), (-o, Ly + o)], "OCULTA", True)
for mk, pos, x, y, bx, by, tp, ref in pil:
    pts = [(x - bx / 2, y - by / 2), (x + bx / 2, y - by / 2), (x + bx / 2, y + by / 2), (x - bx / 2, y + by / 2)]
    if tp == "fora":
        v.poli(pts, "OCULTA", True)
        continue
    v.poli(pts, "CORTADO", True); v.hachura(pts, "SOLID", 1)
# rev08 (22/10/2026): nome de cada peça (P1…P33, sentido de leitura — nomes.json) + seção e folha de detalhamento
import renomear as RN
_NOMES = {(round(p["x"] * 1000), round(p["y"] * 1000)): p for p in RN._D["pecas"] if p["tipo"] == "pilar"}


def nome_em(x, y):
    """x, y da planta (x = linhas, obra y; y = eixos, obra x) → peça de nomes.json."""
    return _NOMES[(round(y), round(x))]


def rot(x, y, bx, by, l1, l2, dx, dy, al):
    v.texto((x + dx, y + dy), RN.novo(l1), "nota", al)
    v.texto((x + dx, y + dy - 380), RN.novo(l2), "min", al)
for mk, pos, x, y, bx, by, tp, ref in pil:
    sec = f"{min(bx, by) // 10}×{max(bx, by) // 10}" if bx != by else f"{bx // 10}×{by // 10}"
    if tp != "fora":
        pn = nome_em(x, y)
        mk, pos = pn["nome"], f"{sec} · {pn['folha'].replace('ND-LET-', '')}"
        sec = ""
    if tp == "lat":
        yy = y + (by / 2 + 500 if ref == "P1" else -by / 2 - 900)
        if ref == "P1":
            rot(x + 250, -by / 2 - 450, bx, by, mk, pos, 0, 0, "BOTTOM_LEFT")
        else:
            rot(x + 250, Ly + by / 2 + 750, bx, by, mk, pos, 0, 0, "BOTTOM_LEFT")
    elif tp == "fach":
        if ref == "L1":
            rot(x + bx / 2 + 250, y + 1100, bx, by, mk, pos, 0, 0, "BOTTOM_LEFT")
        else:                                                                  # linha 9: rótulo para dentro (esquerda)
            rot(x - bx / 2 - 250, y + 1100, bx, by, mk, pos, 0, 0, "BOTTOM_RIGHT")
    elif tp == "int":
        rot(x + bx / 2 + 250, y + by / 2 + 350, bx, by, mk, pos, 0, 0, "BOTTOM_LEFT")
    else:
        pass
# faces A (interna) e C (placas) — letras junto às faces (pilares de borda)
for mk, pos, x, y, bx, by, tp, ref in pil:
    if tp == "lat":
        sg = 1 if ref == "P1" else -1                       # sentido para dentro (x obra); letra ao lado do eixo
        v.texto((x - 140, y - sg * (o + 140)), "C", "min", "MIDDLE_CENTER")
        v.texto((x - 140, y + sg * (by / 2 + 160)), "A", "min", "MIDDLE_CENTER")
    elif tp == "fach":
        sg = 1 if ref == "L1" else -1
        v.texto((x - sg * (o + 140), y + 140), "C", "min", "MIDDLE_CENTER")
        v.texto((x + sg * (bx / 2 + 160), y + 140), "A", "min", "MIDDLE_CENTER")
# cotas: parciais + acumuladas (cm) nos quatro lados
from prancha_nd import DIM_K, DIM_DLI
def total(p1, p2, base, ang, loc):
    """cota acumulada (total entre eixos extremos) com o texto deslocado para fora dos eixos internos."""
    d = pr.msp.add_linear_dim(base=v.P(base), p1=v.P(p1), p2=v.P(p2), angle=ang, location=v.P(loc), dimstyle="ND",
                              override={"dimlfac": v.esc * v.fator, "dimdec": 1, "dimzin": 8, "dimtmove": 2}, dxfattribs={"layer": "COTA"})
    d.render(); v._add(d.dimension)
xs = list(XA.values())
for yr, dp in ((-1350, -2), (Ly + 1550, 2)):
    v.cota_h(YL, yr, dp, total=False)
    yt = yr + (dp * DIM_K + math.copysign(DIM_DLI, dp)) * E
    total((0, yr), (Lx, yr), (0, yt), 0, ((YL[4] + YL[5]) / 2, yt))
for xr, dp in ((-1150, -3), (Lx + 1650, 3)):
    v.cota_v(xs, xr, dp, total=False)
    xt = xr + (dp * DIM_K + math.copysign(DIM_DLI, dp)) * E
    total((xr, 0), (xr, Ly), (xt, 0), 90, (xt, (XA["B"] + XA["C"]) / 2))
# faces externas
# pilares fora dos eixos: PG-02 / PG-04 (linha 4) e os dois PC-03 (DEC-058)
y4 = YL[3]
v.cota_h([XA["B"], 15195, XA["C"], 24305, XA["D"]], y4 - 1500, 0, total=False) if False else None
v.cota_v([XA["B"], X_PG2, XA["C"], X_PG4, XA["D"]], y4 - 2200, -4, total=False)
v.cota_h([YL[3], round(Y_PC_C[0] * 1000), round(Y_PC_C[1] * 1000), YL[8]], XA["C"] - 1700, -4, total=False)
v.chamada((y4, X_PG2), (14, -10), "PG-02 e PG-04 fora do eixo (portões)")
# rev12 (opção D): pilares de canto 10 cm para fora das linhas 1 e 9 — cotados a partir dos dois eixos (linha e eixo A/E)
for xc_, yc_ in ((0, 0), (0, Ly), (Lx, 0), (Lx, Ly)):
    sx_ = -1 if xc_ == 0 else 1
    sy_ = 1 if yc_ == 0 else -1
    v.cota_h([xc_ + sx_ * DYC, xc_] if sx_ < 0 else [xc_, xc_ + sx_ * DYC], yc_ + sy_ * 900, 0, total=False)

v.chamada((round(Y_PC_C[0] * 1000), XA["C"]), (-12, -14), "PC-03 fora das linhas (cotados)")
v.chamada((round(Y_PC_C[1] * 1000), XA["C"]), (12, -14), "3 vãos de 1651,7 da linha 4 à 9")
# rev12: pilares da escada e da linha 2 fora dos eixos (P3, P2, P5) cotados a partir de dois eixos (1/2 e D/E)
v.cota_h([YL[0], 3790, YL[1]], XA["D"] + 2600, 0, total=False)
v.cota_v([XA["D"], 36175, XA["E"]], 3790 + 2200, 0, total=False)
v.cota_v([XA["D"], 36175], YL[1] - 1600, 0, total=False)
v.chamada((3790, 36175), (8, 44), RN.novo(f"{RN.pilar_em(36.175, 3.79)}, {RN.pilar_em(39.5, 3.79)} (escada) e {RN.pilar_em(36.175, 9.65)} (linha 2): cotados dos eixos 1, 2, D e E"))

# ------------------------------------------------------------------ DETALHES TÍPICOS DE LOCAÇÃO 1:25 (cm)
def det(nome, org, titulo, bx, by, chamadas, sub):
    d = pr.vista(nome, org, 25, titulo=titulo, subtitulo=sub, unidade="cm")
    d.eixo((0, -by / 2), (0, by / 2), 120); d.eixo((-bx / 2, 0), (bx / 2, 0), 120)
    pts = [(-bx / 2, -by / 2), (bx / 2, -by / 2), (bx / 2, by / 2), (-bx / 2, by / 2)]
    d.poli(pts, "CORTADO", True); d.hachura(pts, "AR-CONC", 0.02)
    d.cota_h([-bx / 2, 0, bx / 2], by / 2, 8)
    d.cota_v([-by / 2, 0, by / 2], bx / 2, 8)
    for p, dl, t in chamadas:
        d.chamada(p, dl, t)
    return d
X0d, Y0d = 95, 250
det("D1", (X0d, Y0d), "DETALHE 1 — PILAR LATERAL", 400, 600,
    [((0, -300), (-14, -8), "face C (placas) — lado do eixo A"), ((-100, 300), (-14, 8), "face A (interna)")], "PL: 60 × 40 (x × y), 60 na direção A–E")
det("D2", (X0d + 150, Y0d), "DETALHE 2 — PILAR DE FACHADA", 600, 400,
    [((-300, -100), (-12, -10), "face C (placas) — L1: lado do eixo 1"), ((300, -100), (12, -10), "face A (interna)")], "PF: 40 × 60 (x × y), 60 na direção 1–9")
det("D3", (X0d, Y0d - 110), "DETALHE 3 — CENTRAIS", 400, 400, [((-200, -150), (-12, -8), "PC-02 / PC-03 40×40")], "PC-02/PC-03 40×40 (PC-01/PM-01/PM-02 40×60)")
det("D4", (X0d + 150, Y0d - 110), "DETALHE 4 — PORTÕES", 400, 400, [((-200, -150), (-12, -8), "PG-01 / PG-03 40×40")], "PG-01/03 40×40; PG-02/04 25×40 (40 ao longo da parede)")

# ------------------------------------------------------------------ quadro de pilares: nomes × detalhamento × R01
grupos = {}
for p in RN._D["pecas"]:
    if p["tipo"] != "pilar":
        continue
    g = grupos.setdefault(p["folha"], dict(nomes=[], sec=p["secao"], r01=[]))
    g["nomes"].append(p["nome"]); g["r01"].append(p["ref_R01"])
lin = []
for fl, g in sorted(grupos.items(), key=lambda kv: int(kv[1]["nomes"][0][1:])):
    import pe_pilar as PP                                                     # rev11: comprimento total e embutimento no cálice
    d_ = PP.peca(g["nomes"][0])
    lin.append([RN.novo(RN.lista(g["nomes"])), g["sec"], str(len(g["nomes"])), PP.f2(d_["L"]), PP.f2(d_["emb"]), fl.replace("ND-LET-", ""), RN.novo(", ".join(g["r01"]))])
lin.append(["TOTAL", "", str(sum(len(g["nomes"]) for g in grupos.values())), "", "", "", RN.novo("inclui P6 e P7 da escada e P6 da linha 2 (DEC-045)")])
x0 = 360
y = pr.tabela(x0, 318, "QUADRO DE PILARES — NOME × FOLHA × PROJETO DO CLIENTE (R01)", ["PILARES", "SEÇÃO (cm)", "QT", "L TOTAL (m)", "EMB. (m)", "FOLHA", "NOME NO R01"], lin,
              [40, 18, 9, 18, 15, 18, 76], h_lin=5.2, destaque_ultima=True)
pr.notas(560, 318, [
    "Eixos e ordenadas da PLANTA BAIXA — LOCAÇÃO DE PILARES do R01 (Marques Engenharia): 79,35 m entre os eixos 1 e 9 e 39,50 m entre os eixos A e E. Conferir a locação no terreno antes de concretar os blocos.",
    "Pilares de canto (linhas 1 e 9, eixos A e E): eixo 10 cm para fora da linha, no eixo A / E — a face externa fica no plano da face dos pilares de fachada (cotados a partir dos dois eixos).",
    "PENDÊNCIA (confirmar com o arquitetônico/cliente): PG-02 e PG-04 passam a 25 × 40 (40 ao longo da parede da linha 4) com o eixo 7,5 cm para longe do portão, para manter os 5,00 m livres face a face de cada portão.",
    "Todos os pilares são centrados nos eixos, exceto os pilares da escada e o PE-03 da linha 2 (cotados dos eixos 1, 2, D e E), PG-02 e PG-04 (linha 4, portões) e os dois PC-03 (eixo C, y 46,317 e 62,833 — 3 vãos iguais de 16,517 m da linha 4 à 9, DEC-058): posições cotadas na planta.",
    "Faces: A = interna (consolo da viga principal), C = externa (placas de fechamento, por fora dos pilares, folga 2,5 cm; contorno tracejado). B e D completam no sentido anti-horário visto de cima.",
    RN.novo("Nomes P1 a P37: um por peça, em sentido de leitura desta planta (de cima para baixo, eixo E → A, e da esquerda para a direita, linha 1 → 9). Peças iguais têm a mesma folha de detalhamento (coluna FOLHA). A coluna NOME NO R01 é só correspondência com o projeto do cliente, que usa P1 a P14 com outro significado."),
    "Tolerância de locação (NBR 9062:2017 5.2.2.6): ±1,0 cm entre apoios consecutivos, acumulado ≤ 0,1 % do comprimento; prumo ±H/300 até 2,5 cm.",
    "Cargas na fundação: ND-LET-CG01. Cortes: ND-LET-CT01 a CT04 (planta-chave dos cortes na CT03). Montagem: ND-LET-MON01 a MON03.",
    "Cotas em cm; níveis em m a partir do piso acabado (±0,00). L TOTAL = comprimento da peça; EMB. = trecho embutido no cálice (fundo do pilar −1,00; topo do cálice ±0,00; fundo do cálice −1,05 com 5 cm de graute — NBR 9062:2017 7.7).",
    "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."], 240)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-LOC01")
for a in avisos:
    print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
