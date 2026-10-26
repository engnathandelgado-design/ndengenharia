"""ND-LET-CG01 — PLANTA DE CARGAS NA FUNDAÇÃO (rev07): reações na base de cada pilar do modelo global integrado (OpenSeesPy),
em tf e tf·m (1 tf = 10 kN). Características por ação (G, Q, V) e de cálculo (envoltória ELU). Lê exemplos/letsara/cargas_fundacao.json
(calc_cargas_fundacao.py). A0, planta 1:100."""
import json, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from prancha_nd import Prancha
from geometria import Y_LIN, X_EIXO
from familia_pl import marca_de

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
CG = json.load(open(AQ + "cargas_fundacao.json"))
P = CG["pilares"]
t = lambda kn: f"{kn / 10:.1f}".replace(".", ",").replace("-0,0", "0,0")      # kN → tf (NBR 9062: g = 10)
ESP = {"P8": "PM-01", "P8B": "PM-02", "P8A": "PC-01", "P11": "PC-02", "P13": "PC-03", "P13B": "PC-03", "P9": "PG-01", "P10a": "PG-02", "P10b": "PG-04", "P12": "PG-03",
       "P6E": "PE-01", "P7E": "PE-02", "P6-L2": "PE-03"}          # rev09 (DEC-045): pilares da escada e P6 da linha 2


def marca(nm):
    if nm in ESP:
        return ESP[nm]
    base = nm.replace("C-", "-")
    return marca_de(base)


YL = [round(y * 1000) for y in Y_LIN]
XA = {k: round(v * 1000) for k, v in X_EIXO.items()}
Lx, Ly = YL[-1], XA["E"]
pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="PLANTA DE CARGAS NA FUNDAÇÃO — REAÇÕES NA BASE DOS PILARES (tf, tf·m)",
                        desenho="ND-LET-CG01", folha="01/01", fase="PARA APROVAÇÃO", rev="07"))
pr.revisao("07", "21/10/2026", "EMISSÃO: CARGAS NA FUNDAÇÃO DO MODELO GLOBAL INTEGRADO (G, Q, V CARACTERÍSTICAS E ENVOLTÓRIA ELU)")
pr.revisao("09", "23/10/2026", "DEC-045/049: PISOS +3,90/+7,30; PILARES DA ESCADA; VM 30 × 75; LINHA 2 METÁLICA")
pr.revisao("10", "24/10/2026", "DEC-058/059: 2 PC-03 NO EIXO C (I130 EM 3 VÃOS DE 16,517 m, Ø12,7); PG-01 A PG-04 APOIAM A TS-01A (PORTÕES)")
E = 100
import math
from prancha_nd import DIM_K, DIM_DLI
v = pr.vista("PLANTA", (118, 390), E, titulo="PLANTA DE CARGAS NA FUNDAÇÃO",
             subtitulo="por pilar: Nk = G + Q característico; Nd máx / Nd mín, Mxd, Myd e Hd de cálculo (envoltória ELU) — tf e tf·m", unidade="cm")
EXT, RB = 2400, 650
DB = EXT + 50 + RB
for k, y in enumerate(YL):
    v.eixo((y, 0), (y, Ly), EXT)
    for xb in (-DB, Ly + DB):
        v.circulo((y, xb), RB, "BOLHA"); v.texto((y, xb), str(k + 1), "sub", "MIDDLE_CENTER")
for nome, x in XA.items():
    v.eixo((0, x), (Lx, x), EXT)
    for yb in (-DB, Lx + DB):
        v.circulo((yb, x), RB, "BOLHA"); v.texto((yb, x), nome, "sub", "MIDDLE_CENTER")


def total(p1, p2, base, ang, loc):
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
DL = 330                                                                # entrelinha dos rótulos (3,3 mm)
for nm, d in P.items():
    xp, yp = round(d["y"] * 1000), round(d["x"] * 1000)               # planta: horizontal = y da obra, vertical = x
    bx, by = round(d["by"] * 1000), round(d["bx"] * 1000)
    pts = [(xp - bx / 2, yp - by / 2), (xp + bx / 2, yp - by / 2), (xp + bx / 2, yp + by / 2), (xp - bx / 2, yp + by / 2)]
    v.poli(pts, "CORTADO", True); v.hachura(pts, "SOLID", 1)
    nk = d["G"]["N"] + d["Q"]["N"]
    e = d["ELU"]
    lin_ = [(f"{marca(nm)} ({nm})", "nota"), (f"Nk {t(nk)}  (G {t(d['G']['N'])} + Q {t(d['Q']['N'])})", "min"),
            (f"Nd {t(e['Nd_max'])} / {t(e['Nd_min'])}", "min"), (f"Mxd {t(e['Mxd_max'])} · Myd {t(e['Myd_max'])}", "min"),
            (f"Hd {t(e['Hd_max'])}", "min")]
    dx, al = (bx / 2 + 200, "BOTTOM_LEFT")
    if xp == Lx:                                                        # linha 9: rótulo para dentro
        dx, al = (-bx / 2 - 200, "BOTTOM_RIGHT")
    if yp == 0:                                                         # eixo A: acima (para dentro)
        y0 = by / 2 + 250 + DL * (len(lin_) - 1)
    elif yp == Ly:                                                      # eixo E: abaixo (para dentro)
        y0 = Ly - by / 2 - 450
    else:
        y0 = yp + by / 2 + 250 + DL * (len(lin_) - 1)
    if nm in ("P6E", "P7E", "P6-L2"):                                  # rev09: pilares do anexo/escada — rótulo à esquerda, para baixo
        dx, al = ((bx / 2 + 200, "BOTTOM_LEFT") if nm == "P7E" else (-bx / 2 - 200, "BOTTOM_RIGHT"))
        y0 = yp - by / 2 - 300 if nm != "P6-L2" else yp + by / 2 + 250 + DL * (len(lin_) - 1)
    for k, (s_, h_) in enumerate(lin_):
        v.texto((xp + dx, y0 - k * DL), s_, h_, al)

# ------------------------------------------------------------------ tabela completa
ordem = sorted(P, key=lambda n: (marca(n)[:2] != "PL", marca(n)[:2] != "PF", marca(n)[:2] != "PC", marca(n)[:2] != "PM", marca(n), n))
lin = []
for nm in ordem:
    d = P[nm]; g, q, w, e = d["G"], d["Q"], d["V"], d["ELU"]
    lin.append([nm, marca(nm), t(g["N"]), t(q["N"]), f"{t(w['N_min'])} / {t(w['N_max'])}", t(w["Mx_max"]), t(w["My_max"]), t(w["H_max"]),
                t(e["Nd_max"]), t(e["Nd_min"]), t(e["Mxd_max"]), t(e["Myd_max"]), t(e["Hd_max"])])
cab = ["PILAR", "MARCA", "G: N", "Q: N", "V: N mín / máx", "V: Mx", "V: My", "V: H", "Nd máx", "Nd mín", "Mxd", "Myd", "Hd"]
y = pr.tabela(35, 318, "CARGAS NA FUNDAÇÃO POR PILAR — CARACTERÍSTICAS POR AÇÃO E DE CÁLCULO (ELU) — tf e tf·m",
              cab, lin, [18, 16, 15, 15, 30, 14, 14, 14, 17, 17, 15, 15, 14], h_lin=4.6)
pr.notas(470, 318, [
    "Valores na base de cada pilar (topo do bloco/cálice, cota −1,00), do modelo global integrado da estrutura (OpenSeesPy, P-Δ, pilares com 0,4 Eci·Ic — NBR 9062:2017 Anexo A; cobertura, terças, correntes, contraventamento, vigas e mezanino com a laje como diafragma). Unidades: tf e tf·m, com 1 tf = 10 kN.",
    "Convenção: N positivo = compressão na fundação, negativo = tração (arrancamento). x = direção A→E, y = direção 1→9; Mx = momento em torno de x, My = em torno de y; H = resultante horizontal. Momentos e H em valor absoluto (o sentido inverte com o vento).",
    "Características por ação: G = permanentes (peso próprio, cobertura completa com painéis solares 0,15 kN/m² e instalações 0,10 kN/m², placas, mezanino com laje, capa e revestimento); Q = sobrecargas (cobertura 0,25 kN/m² — NBR 6120; piso +3,90: sobrecarga 5,0 kN/m² (depósito) + revestimento 1,0 kN/m²; +7,30: laje de cobertura do bloco (acesso apenas para manutenção, NBR 6120:2019 Tab. 10): sobrecarga 1,0 + regularização/impermeabilização 1,7 kN/m² — ND-LET-LA01); V = vento NBR 6123 nas 4 direções, Cpi máximo e mínimo e excentricidade ±e (6.6), dado como (G+V) − G, envoltória mín/máx.",
    "De cálculo (ELU, NBR 8681 / 6118): 1,3 G + 1,4 V + 0,7·1,4 Q (sobrecarga secundária) e 1,0 G + 1,4 V (sucção, G favorável), com desaprumo H/400 (NBR 9062:2017 5.2.3); e 1,3 G + 1,4 Q. Nd mín negativo = tração de cálculo na fundação.",
    "Pilares PG-01, PG-02, PG-03 e PG-04 não recebem cobertura (V só horizontal pelas placas/portões).",
    "Dimensionar blocos, cálices e estacas em projeto próprio com estes valores; o cálice segue as cargas e o embutimento das pranchas dos pilares.",
    "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."], 300)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-CG01")
for a in avisos:
    if a[0] == "ERRO" or "sobrep" in a[1] or "sai" in a[1]:
        print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
