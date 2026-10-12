"""Prancha de produção TS-01 — viga I90 de cobertura (Letsara). mm no modelo; A1."""
import math, sys, json
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas")
from prancha_nd import Prancha, MASSA_ACO
from nd_estruturas.prefabricados import (Concreto, Carregamento, secao_I, verificar_viga_pretracionada,
                                         icamento_viga, pressao_vento, CORD)

# ------------------------------------------------------------------ dados únicos (memória = prancha)
P = dict(marca="TS-01", qtd=14, L=19710, h=900, b=400, ts=120, ti=150, m=80, bw=150, maciço=500,
         fck=50, fckj=35, n_cord=6, y_cord=75, x_cord=[-150, -100, -50, 50, 100, 150],
         a_alca=2000, terca_ini=255, terca_passo=1600, n_tercas=13, insert_dx=100,
         pino_x=150, L_pista=60, sig_pi=1453)
C = Concreto(P["fck"])
sec = secao_I(P["h"] / 1000, bs=0.40, ts=0.12, ms=0.08, bw=0.15, bi=0.40, ti=0.15, mi=0.08)
L_calc = (P["L"] - 2 * P["pino_x"]) / 1000
TRIB, qv = 9.655, pressao_vento(45.0, S3=0.95)
car = Carregamento(sec.A * 25, 0.25 * TRIB, 0.25 * TRIB, w=qv * TRIB, psi1=0.4, psi2=0.0)
ycg_c = P["y_cord"] / 1000
R = verificar_viga_pretracionada(sec, L_calc, car, C, P["n_cord"], y_cord=ycg_c, fckj=P["fckj"])
Ap = P["n_cord"] * CORD["12.7"]
ICA = icamento_viga(sec, P["L"] / 1000, P["a_alca"] / 1000, R.linhas["P0_kN"], sec.yc - ycg_c, C, P["fckj"])
V = sec.A * P["L"] / 1000 + (P["b"] * P["h"] / 1e6 - sec.A) * P["maciço"] / 1000 * 2
peso = V * 25
F_cord = P["sig_pi"] * 98.7 / 1000
Md_neg = max(0.0, (1.4 * car.w - car.g1 - car.g2) * L_calc ** 2 / 8)
assert R.ok and ICA["ok_tensoes"] and ICA["ok_estabilidade"], (R.avisos, ICA)
f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")

pr = Prancha("A1", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo=f"{P['marca']} — VIGA I90 DE COBERTURA (PROTENDIDA) — FÔRMA, ARMAÇÃO E INSERTOS",
                        desenho="ND-LET-TS01", folha="01/01", fase="PARA APROVAÇÃO"))
L, H = P["L"], P["h"]
yf_inf, yc_inf, yc_sup, yf_sup = 150, 230, 700, 780   # mesa inf. | fim chanfro inf. | início chanfro sup. | mesa sup.

# ------------------------------------------------------------------ 1. ELEVAÇÃO DE FÔRMA (1:40)
v = pr.vista("ELEVAÇÃO DE FÔRMA", (60, 470), 40, titulo=f"ELEVAÇÃO DE FÔRMA — {P['marca']}",
             subtitulo="peça reta, montada com caimento de 3%")
v.ret(0, 0, L, H, "VISTA")
mc = P["maciço"]
for y, cam in ((yf_inf, "VISTA"), (yc_inf, "VISTA"), (yc_sup, "VISTA"), (yf_sup, "VISTA")):
    v.linha((mc, y), (L - mc, y), cam)
for x in (mc, L - mc):
    v.linha((x, yf_inf), (x, yc_inf), "VISTA"); v.linha((x, yc_sup), (x, yf_sup), "VISTA")
# tubos do pino (TB-1) e chapas de apoio (CH-A1)
for x in (P["pino_x"], L - P["pino_x"]):
    v.linha((x - 25, 0), (x - 25, H), "OCULTA"); v.linha((x + 25, 0), (x + 25, H), "OCULTA")
    v.ret(x - 150, -12, 300, 12, "METALICA")
# alças AL-1
for x in (P["a_alca"], L - P["a_alca"]):
    v.poli([(x - 60, H), (x - 60, H + 120), (x + 60, H + 120), (x + 60, H)], "METALICA")
# insertos de terça IM-T1 (pares) no topo
xt = [P["terca_ini"] + k * P["terca_passo"] for k in range(P["n_tercas"])]
for x in xt:
    v.ret(x - 100, H - 13, 200, 13, "METALICA")                 # CH-T1 faceando o topo
    v.circulo((x, H - 300), 10, "METALICA")                      # TB-2 passante na alma
# CG
cgx, cgy = L / 2, sec.yc * 1000
v.circulo((cgx, cgy), 120, "INDICACAO"); v.linha((cgx - 200, cgy), (cgx + 200, cgy), "INDICACAO")
v.linha((cgx, cgy - 200), (cgx, cgy + 200), "INDICACAO")
v.chamada((cgx + 85, cgy + 85), (14, 10), f"CG (x = {f(L/2000,3)} m; y = {f(cgy,0)} mm)")
v.chamada((P["a_alca"], H + 120), (-4, 34), "AL-1 (2x)")
v.chamada((xt[3], H), (6, 34), f"CH-T1 — {len(xt)} chapas com furos (terças a cada {P['terca_passo']})")
v.chamada((xt[7], H - 300), (6, 46), f"TB-2 — {len(xt)} furos passantes Ø20 na alma (mão-francesa)")
v.chamada((P["pino_x"], 300), (14, -30), "TB-1 Ø50 (furo do pino)")
v.chamada((L - P["pino_x"], -12), (10, -12), "CH-A1 (2x)")
v.cota_h([0, P["a_alca"], L - P["a_alca"], L], 0, -14)
v.cota_h([0, mc, L - mc, L], 0, -24, total=False)
v.cota_h([0] + xt + [L], H, 16, total=False)
v.marcador_corte((L / 2 - 1500, -150), (L / 2 - 1500, H + 150), "A", lado=1)
v.marcador_corte((P["pino_x"] + 120, -150), (P["pino_x"] + 120, H + 150), "B", lado=1)

# ------------------------------------------------------------------ 2. ELEVAÇÃO DE ARMAÇÃO (1:40)
va = pr.vista("ELEVAÇÃO DE ARMAÇÃO", (60, 330), 40, titulo=f"ELEVAÇÃO DE ARMAÇÃO — {P['marca']}", subtitulo="armadura passiva e cordoalhas")
va.ret(0, 0, L, H, "VISTA")
# estribos N1: c/15 nos 1,5 m das pontas, c/25 no restante
zona = 1500
x_est = []
x = 50
while x <= zona:
    x_est.append(x); x += 150
x = zona + 250
while x <= L - zona:
    x_est.append(x); x += 250
x = L - zona
while x <= L - 50:
    x_est.append(x); x += 150
x_est = sorted(set(round(v_, 0) for v_ in x_est))
for x in x_est:
    va.linha((x, 40), (x, H - 40), "ARMADURA")
n1 = len(x_est)
cN1 = 2 * (90 + 840) + 2 * 70
va.barra([(30, H - 45), (L - 30, H - 45)], "N2", 4, 12.5, comp_cm=(L - 60) / 10, ponto_rotulo=(L * 0.62, H - 45), desloc=(10, 10))
va.barra([(30, 40), (L - 30, 40)], "N5", 2, 10, comp_cm=(L - 60) / 10, ponto_rotulo=(L * 0.70, 40), desloc=(10, -12))
va.linha((0, P["y_cord"]), (L, P["y_cord"]), "ARMADURA")
va.chamada((L * 0.3, P["y_cord"]), (-10, -16), f"C1 — {P['n_cord']} cord. Ø12,7 (aderentes)")
va.chamada((x_est[12], 500), (12, 22), f"N1 - {n1} Ø6,3 c/15 (1,5 m nas pontas) e c/25 C={cN1/10:.0f}")
va.cota_h([0, zona, L - zona, L], 0, -14)
pr.posicoes_desenho.update({"N1", "N3", "N4", "N6", "N7", "C1"})

# ------------------------------------------------------------------ 3. CORTE A-A (1:10) e CORTE B-B (1:10)
pts = [(x * 1000, y * 1000) for x, y in sec.pts]
vc = pr.vista("CORTE A-A", (110, 140), 10, titulo="CORTE A-A", subtitulo="seção corrente")
vc.poli(pts, "CORTADO", fechada=True); vc.hachura(pts, "AR-CONC", 0.03)
for x in P["x_cord"]:
    vc.ponto_barra((x, P["y_cord"]), 12.7)
for x in (-160, -60, 60, 160):
    vc.ponto_barra((x, H - 45), 12.5)
for x in (-165, 165):
    vc.ponto_barra((x, 35), 10)
vc.poli([(-45, 30), (45, 30), (45, H - 30), (-45, H - 30)], "ARMADURA", fechada=True)
vc.poli([(-170, H - 30), (170, H - 30), (170, H - 100), (-170, H - 100)], "ARMADURA", fechada=True)
vc.poli([(-170, 30), (170, 30), (170, 120), (-170, 120)], "ARMADURA", fechada=True)
vc.chamada((100, P["y_cord"]), (22, -8), f"C1 - {P['n_cord']} Ø12,7 (y = {P['y_cord']})")
vc.chamada((160, H - 45), (20, 6), "N2 - 4 Ø12,5")
vc.chamada((165, 35), (20, -10), "N5 - 2 Ø10")
vc.chamada((45, 450), (24, 0), "N1 Ø6,3 (alma)")
vc.chamada((170, H - 65), (20, -4), "N3 Ø6,3 c/25 (mesa sup.)")
vc.chamada((-170, 75), (-22, 10), "N4 Ø6,3 c/25 (mesa inf.)")
vc.cota_h([-200, -75, 75, 200], H, 10)
vc.cota_v([0, 150, 230, 700, 780, 900], -200, -14)
vc.cota_h([-200, -150, -100, -50, 50, 100, 150, 200], 0, -10, total=False)

vb = pr.vista("CORTE B-B", (300, 140), 10, titulo="CORTE B-B", subtitulo="maciço da ponta")
rb = [(-200, 0), (200, 0), (200, H), (-200, H)]
vb.poli(rb, "CORTADO", fechada=True); vb.hachura(rb, "AR-CONC", 0.03)
vb.ret(-25, 0, 50, H, "VISTA")
vb.ret(-150, -12, 300, 12, "METALICA")
for x in P["x_cord"]:
    vb.ponto_barra((x, P["y_cord"]), 12.7)
vb.poli([(-170, 30), (170, 30), (170, H - 30), (-170, H - 30)], "ARMADURA", fechada=True)
vb.chamada((25, 600), (22, 6), "TB-1 tubo Ø50 (pino Ø25 grauteado)")
vb.chamada((150, -6), (20, -10), "CH-A1 chapa 300×150×12,5 + grapas")
vb.chamada((170, 500), (22, -14), "N6 Ø8 c/7,5 (fretagem, 50 cm)")
vb.chamada((-170, 300), (-22, 8), "N7 Ø10 (grampos do maciço)")
vb.cota_h([-200, -25, 25, 200], H, 10)
vb.cota_v([0, H], 200, 14)

# ------------------------------------------------------------------ 4. coluna da direita: tabelas e notas
x0, y = pr.quadro[2] - 180, pr.quadro[3] - 6
cN3 = 2 * (340 + 70) + 140
barras = [dict(pos="N1", diam=6.3, qtd=n1, comp=round(cN1 / 10)),
          dict(pos="N2", diam=12.5, qtd=4, comp=round((L - 60) / 10)),
          dict(pos="N3", diam=6.3, qtd=round(L / 250) + 1, comp=round(cN3 / 10)),
          dict(pos="N4", diam=6.3, qtd=round(L / 250) + 1, comp=round(cN3 / 10)),
          dict(pos="N5", diam=10.0, qtd=2, comp=round((L - 60) / 10)),
          dict(pos="N6", diam=8.0, qtd=14, comp=round(cN3 / 10)),
          dict(pos="N7", diam=10.0, qtd=8, comp=180)]
ta = pr.tabela_aco(x0, y, barras)
tc = pr.tabela_cordoalhas(x0, ta["y_base"] - 4, [dict(pos="C1", diam=12.7, qtd=P["n_cord"], y=P["y_cord"],
                                                      forca=F_cord, isol=0)], P["L_pista"])
ins = [["AL-1", "Alça de içamento, cordoalha Ø12,7 dupla, 60 cm na alma", 2, f"a {P['a_alca']} das pontas"],
       ["CH-T1", "Chapa 200×120×12,5 c/ 2 furos Ø18 e porca M16", len(xt), f"c/{P['terca_passo']}"],
       ["TB-2", "Tubo Ø20 passante na alma (mão-francesa)", len(xt), "300 abaixo do topo"],
       ["TB-1", "Tubo Ø50 vertical (furo do pino Ø25)", 2, f"a {P['pino_x']} das pontas"],
       ["CH-A1", "Chapa de apoio 300×150×12,5 + 4 grapas Ø10", 2, "face inferior"]]
y = pr.tabela(x0, tc["y_base"] - 4, "INSERTOS", ["SIGLA", "DESCRIÇÃO", "QT", "POSIÇÃO"], ins, [16, 104, 10, 50])
kg_cord = Ap * 1e4 * P["L"] / 1000 * 0.785
quadro = [["MARCA", P["marca"], "QUANTIDADE", f"{P['qtd']}"],
          ["COMPRIMENTO", f"{f(L/1000,2)} m", "VOLUME", f"{f(V,3)} m³"],
          ["PESO", f"{f(peso,1)} kN ({f(peso/9.81,2)} t)", "CG", f"L/2; y = {f(sec.yc*1000,0)} mm"],
          ["CONCRETO", f"C{P['fck']} · fckj {P['fckj']} MPa", "AÇO PASSIVO", f"{f(ta['total_kg'],0)} kg"],
          ["CORDOALHAS", f"{P['n_cord']} Ø12,7 · {f(kg_cord,0)} kg", "CAA / COBR.", "II / 30 mm"]]
y = pr.tabela(x0, y - 4, "QUADRO DA PEÇA", ["ITEM", "VALOR", "ITEM", "VALOR"], quadro, [30, 60, 30, 60])
mem = [["ELU flexão", f"Md {f(R.linhas['Md_kNm'],0)} ≤ MRd {f(R.linhas['MRd_kNm'],0)} kN·m"],
       ["ELS-F / ELS-D (fundo)", f"{f(R.linhas['elsf_inf_MPa'],2)} / {f(R.linhas['elsd_inf_MPa'],2)} MPa"],
       ["Ato (meio, inf./sup.)", f"{f(R.linhas['ato_meio_inf_MPa'],1)} / {f(R.linhas['ato_meio_sup_MPa'],1)} MPa"],
       ["Flecha final", f"{f(R.linhas['flecha_final_mm'],0)} mm ≤ L/250 = {f(R.linhas['flecha_lim_mm'],0)} mm"],
       ["Sucção do vento (ELU)", f"Md,neg {f(Md_neg,0)} kN·m → N2 4 Ø12,5"],
       ["Içamento (a = 2,0 m, ×1,3)", f"FS fiss. {f(ICA['FS_fissuracao'],1)} · FS rupt. {f(ICA['FS_ruptura'],1)}"],
       ["Carga por alça (cálculo)", f"{f(ICA['carga_alca_d_kN'],0)} kN"]]
y = pr.tabela(x0, y - 4, "MEMÓRIA RESUMIDA", ["VERIFICAÇÃO", "RESULTADO"], mem, [62, 118])
notas = [f"Concreto C{P['fck']}; liberar as cordoalhas, desformar e içar só com fckj ≥ {P['fckj']} MPa (CP curado com a peça).",
         f"Cordoalhas CP-190 RB Ø12,7 aderentes, nos furos do cabeçote REV05 (linha inferior a {P['y_cord']} mm do fundo da fôrma, passo 50 mm); σpi = {P['sig_pi']} MPa; liberação gradual e simétrica.",
         f"Pista de {P['L_pista']} m: até 3 peças por linha; conferir alongamento medido × teórico (±7%).",
         f"Içamento, estocagem e transporte somente pelas alças AL-1, a {f(P['a_alca']/1000,1)} m das pontas, com balancim e cabos verticais; calços nos mesmos pontos.",
         "Apoio: neoprene fretado 300×150×10 sobre o consolo do pilar e sobre a viga I110; pino Ø25 grauteado no TB-1 (transmite a força horizontal de tirante).",
         "Terças Ue 300×85×25×3,00: suporte ST-1 soldado na CH-T1 (2 M12 por ponta de terça) e mão-francesa L 50×5 na OR-1 do fundo (ND-LET-COB01).",
         "CH-T1 alinhadas com o eixo das terças; tolerância ±5 mm.",
         "Cobrimento 30 mm (CAA II). Tolerâncias de fabricação NBR 9062. Medidas em mm. Não medir no desenho.",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(x0, y - 4, notas, 180)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-TS01")
print("avisos:", avisos)
json.dump(dict(P=P, V=V, peso=peso, aco=ta["total_kg"], R=R.linhas, ICA=ICA), open("/home/claude/letsara/pranchas/ts01.json", "w"), default=str)
