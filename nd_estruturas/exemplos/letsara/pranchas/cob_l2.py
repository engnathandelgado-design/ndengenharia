"""ND-LET-COB05 — cobertura metálica da linha 2 (rev09, DEC-048): W 310 × 32,7 A572-50 contínua de A a E no lugar das TS-01,
apoiada SÓ nos pilares (A recuo do P1-L2, B, C, D, P6 da linha 2, E recuo do P2-L2) por montantes W 150 × 22,5 com chapa de base
e 4 barras roscadas M20 embutidas (padrão Mitsubishi); emendas parafusadas com talas; terças no clip ST-W e mão-francesa MF-1 em
toda terça (trava a mesa inferior). Tudo parafusado na obra. Dados de cob_linha2.json (calc_cobertura_linha2.py) e ligacoes.json.
Cotas em mm. A1."""
import json, math, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from prancha_nd import Prancha
from geometria import X_EIXO, Y_LIN
import renomear as RN

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
CB = json.load(open(AQ + "cob_linha2.json"))
LG = json.load(open(AQ + "ligacoes.json"))
f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
M = lambda v: v * 1000
I3 = 0.03
D_W, BF_W, TF_W, TW_W = 313, 102, 10.8, 6.6                    # W 310 × 32,7 (Gerdau)
zt = lambda x: M(LG["Z0_TS"]) + I3 * x + 900 / math.cos(math.atan(I3))   # topo da W (= topo da TS-01 nas outras linhas), x em mm
LARG = M(X_EIXO["E"])
CORTES = [25] + [M(x) for x in CB["emendas_x"]] + [LARG - 25]
MT = {m["apoio"]: m for m in CB["montantes"]}
X_TER = LG["x_tercas_esq"] + [x + (2 * X_EIXO["C"] - LG["X_PONTA_CEN"]) - LG["X_PONTA_ESQ"] for x in LG["x_tercas_esq"]]
NT = len(X_TER)

pr = Prancha("A1", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="COBERTURA METÁLICA DA LINHA 2 — W 310 × 32,7 SOBRE OS PILARES: ELEVAÇÃO, MONTANTES, EMENDAS, ST-W, MÃO-FRANCESA E LISTA",
                        desenho="ND-LET-COB05", folha="01/01", fase="PARA APROVAÇÃO", rev="00"))
pr.revisao("00", "23/10/2026", "EMISSÃO INICIAL (DEC-048): LINHA 2 METÁLICA, SEM TS-01")
Q = pr.quadro
XC = Q[2] - 190
pr.cabecalho_peca("W-L2", f"VIGA DE COBERTURA DA LINHA 2 — {CB['perfil'].replace('x', '×')} ({CB['aco']}) CONTÍNUA DE A a E, {len(CORTES) - 1} MÓDULOS",
                  f"apoios só nos pilares (A, B, C, D, P6, E) por montantes {CB['montante'].replace('x', '×')}; terças no ST-W; mão-francesa MF-1 em toda terça; uso {f(CB['verificacoes']['uso_M'], 3)}",
                  largura=XC - Q[0] - 10)

# ------------------------------------------------------------------ ELEVAÇÃO 1:75 (olhando para a linha 9)
v = pr.vista("ELEVAÇÃO", (Q[0] + 55, Q[3] - 220 - 7000 / 75), 75, titulo="ELEVAÇÃO DA LINHA 2 — W 310 E MONTANTES (OLHANDO PARA A LINHA 9)",
             subtitulo="topo da W na inclinação da cobertura (3 %); módulos e emendas; terças a cada 1,26 m", unidade="mm")
zb = lambda x: zt(x) - D_W
v.poli([(CORTES[0], zb(CORTES[0])), (CORTES[-1], zb(CORTES[-1])), (CORTES[-1], zt(CORTES[-1])), (CORTES[0], zt(CORTES[0]))], "METALICA", fechada=True)
for xe in CORTES[1:-1]:
    v.linha((xe, zb(xe)), (xe, zt(xe)), "METALICA")
    v.ret(xe - 200, zt(xe), 400, 13, "METALICA"); v.ret(xe - 200, zb(xe) - 13, 400, 13, "METALICA")
for a in CB["apoios"]:
    x = M(a["x"]); m = MT[a["nome"]]
    z0 = M(m["z_base"])
    v.ret(x - 76, z0 + 19, 152, zb(x) - z0 - 19 - 13, "METALICA")
    v.ret(x - 125, z0, 250, 19, "METALICA")
    bx = 400 if a["nome"] in ("B", "C", "D") else (250 if a["nome"] == "P6" else 300)
    v.ret(x - bx / 2, z0 - 1200, bx, 1200, "VISTA"); v.interrupcao((x - bx / 2, z0 - 1200), (x + bx / 2, z0 - 1200))
    v.texto((x, z0 - 1700), {"A": "PL-02", "B": "PM-01", "C": "PC-01", "D": "PM-01", "P6": "PE-03", "E": "PL-06"}[a["nome"]], "min", "TOP_CENTER")
    v.texto((x, z0 - 2100), f"MT-{a['nome']} h {f(m['h_m'] * 100, 0)}", "min", "TOP_CENTER")
for xt_ in X_TER:
    xw = M(xt_)
    v.ret(xw - 45, zt(xw), 90, 302, "OCULTA")
v.cota_h([M(a["x"]) for a in CB["apoios"]], 4800, -6, total=True)
v.cota_h(CORTES, zt(LARG) + 600, 10, total=False)
v.chamada((CORTES[1], zt(CORTES[1]) + 13), (6, 12), "emenda TL-1 / TL-2 (det. 2)")
v.chamada((M(14.0), zb(M(14.0)) + D_W / 2), (6, -18), f"{CB['perfil'].replace('x', '×')} contínua")

# ------------------------------------------------------------------ DETALHE 1 — base do montante (1:10)
d1 = pr.vista("DETALHE 1", (Q[0] + 70, Q[1] + 175), 10, titulo="DETALHE 1 — BASE DO MONTANTE NO PILAR", subtitulo="chapa 250 × 250 × 19 + 4 BR-M20 8.8 embutidas 400 + grampo", unidade="mm")
pil = [(-200, -500), (200, -500), (200, 0), (-200, 0)]
d1.poli(pil, "CORTADO", fechada=True); d1.hachura(pil, "AR-CONC", 0.03); d1.interrupcao((-200, -500), (200, -500))
d1.ret(-125, 0, 250, 19, "METALICA"); d1.ret(-76, 19, 152, 450, "METALICA"); d1.interrupcao((-76, 469), (76, 469))
for xx in (-75, 75):
    d1.linha((xx, -400), (xx, 80), "METALICA")
d1.poli([(-75, -400), (-75, -440), (75, -440), (75, -400)], "ARMADURA")
d1.cota_h([-125, -75, 75, 125], -500, -16, total=True); d1.cota_v([-400, 0], 230, 8, total=False)
d1.chamada((75, -200), (32, -10), "4 BR-M20 8.8 embutidas 400 (fábrica do pilar)")
d1.chamada((-75, -440), (-14, -10), "grampo Ø12,5 nas 2 barras")
d1.chamada((0, 9), (20, 14), "CB chapa 250 × 250 × 19 + graute 20 mm")
d1.chamada((0, 300), (16, 8), "MT W 150 × 22,5 (solda de oficina na CB)")

# ------------------------------------------------------------------ DETALHE 2 — emenda (1:10)
d2 = pr.vista("DETALHE 2", (Q[0] + 260, Q[1] + 175), 10, titulo="DETALHE 2 — EMENDA DA W 310", subtitulo="TL-1 nas mesas + TL-2 na alma; M16 8.8", unidade="mm")
d2.ret(-600, 0, 1200, D_W, "METALICA"); d2.linha((0, 0), (0, D_W), "METALICA")
d2.ret(-200, D_W, 400, 12.5, "METALICA"); d2.ret(-200, -12.5, 400, 12.5, "METALICA"); d2.ret(-150, (D_W - 200) / 2, 300, 200, "OCULTA")
for xx in (-150, -70, 70, 150):
    d2.circulo((xx, D_W + 6), 9, "METALICA"); d2.circulo((xx, -6), 9, "METALICA")
for xx in (-100, -50, 50, 100):
    for zz in (D_W / 2 - 60, D_W / 2 + 60):
        d2.circulo((xx, zz), 9, "METALICA")
d2.cota_h([-200, 0, 200], D_W + 12.5, 10, total=False); d2.cota_v([0, D_W], 620, 8, total=False)
d2.chamada((150, D_W + 12), (10, 12), "TL-1 (2 por emenda) + 8 M16 cada")
d2.chamada((100, D_W / 2 + 60), (30, 10), "TL-2 (2 por emenda) + 6 M16")

# ------------------------------------------------------------------ DETALHE 3 — terça na W: ST-W e mão-francesa (seção, 1:10)
d3 = pr.vista("DETALHE 3", (Q[0] + 470, Q[1] + 130), 10, titulo="DETALHE 3 — TERÇA NA W: ST-W E MÃO-FRANCESA", subtitulo="seção transversal; MF-1 dos dois lados, 1 M12 em cada ponta", unidade="mm")
d3.ret(-BF_W / 2, D_W - TF_W, BF_W, TF_W, "METALICA"); d3.ret(-BF_W / 2, 0, BF_W, TF_W, "METALICA"); d3.ret(-TW_W / 2, TF_W, TW_W, D_W - 2 * TF_W, "METALICA")
d3.poli([(-90, D_W + 6.3), (90, D_W + 6.3), (90, D_W + 6.3 + 150)], "METALICA")
d3.ret(-45, D_W + 6.3, 90, 302, "OCULTA")
for sy in (-1, 1):
    d3.linha((sy * 300, D_W + 60), (sy * (BF_W / 2 + 10), TF_W), "METALICA")
d3.cota_v([0, D_W, D_W + 6.3 + 302], 380, 8, total=False); d3.cota_h([-300, 0, 300], -40, -8, total=False)
d3.chamada((-200, D_W - 60), (-16, 10), "MF-1 L 51 × 51 × 4,8 (2 por terça)")
d3.chamada((60, D_W + 80), (30, 30), "ST-W 6,3 + 2 M12 (mesa) + 2 M12 (terça)")
d3.chamada((0, 160), (20, -14), "W 310 × 32,7")
d3.chamada((-20, D_W + 200), (-24, 18), "terça Z 302 (ND-LET-COB01)")

# ------------------------------------------------------------------ tabelas e notas
kgm_W, kgm_M = 32.7, 22.5
lin = [[f"W-L2 {k + 1}", f"{CB['perfil'].replace('x', '×')} A572-50", "1", f(L_, 2), f(L_ * kgm_W, 0)] for k, L_ in enumerate(CB["modulos_m"])]
lin += [[f"MT-{m['apoio']}", f"{CB['montante'].replace('x', '×')} (h {f(m['h_m'] * 100, 0)} cm)", "1", f(m["h_m"], 2), f(m["h_m"] * kgm_M, 0)] for m in CB["montantes"]]
n_e = len(CB["emendas_x"])
lin += [["CB", "chapa de base 250 × 250 × 19", str(len(CB["montantes"])), "-", f(len(CB["montantes"]) * 9.3, 0)],
        ["CT", "chapa de topo 180 × 160 × 12,5 (montante × W, 4 M16)", str(len(CB["montantes"])), "-", f(len(CB["montantes"]) * 2.8, 0)],
        ["BR-M20", "barra roscada M20 8.8 L 480 + grampo (embutida no pilar)", str(4 * len(CB["montantes"])), "0,48", f(4 * len(CB["montantes"]) * 0.48 * 2.47, 0)],
        ["TL-1", "tala de mesa 12,5 × 100 × 400", str(2 * n_e), "0,40", f(2 * n_e * 3.9, 0)],
        ["TL-2", "tala de alma 9,5 × 200 × 300", str(2 * n_e), "0,30", f(2 * n_e * 4.5, 0)],
        ["ST-W", "clip da terça, chapa dobrada 6,3", str(NT), "-", f(NT * 3.2, 0)],
        ["MF-1", "mão-francesa L 51 × 51 × 4,8 L 434", str(2 * NT), "0,43", f(2 * NT * 0.434 * 3.63, 0)],
        ["M16 8.8", "parafuso + porca + 2 arruelas (emendas e CT)", str(n_e * 28 + 4 * len(CB["montantes"])), "-", "-"],
        ["M12 8.8", "parafuso + porca + 2 arruelas (ST-W e MF-1)", str(NT * 4 + 2 * 2 * NT), "-", "-"]]
tot = sum(float(l[4].replace(",", ".")) for l in lin if l[4] != "-")
lin.append(["", "TOTAL (sem parafusos)", "", "", f(tot, 0)])
y = pr.tabela(XC, Q[3] - 6, "LISTA DE MATERIAL — COBERTURA DA LINHA 2", ["MARCA", "DESCRIÇÃO", "QT", "L (m)", "kg"], lin, [18, 100, 12, 18, 22], destaque_ultima=True)
vf = CB["verificacoes"]; fl = CB["flecha"]; e1 = CB["esforcos"]
ver = [["Flexão (ELU sucção 1,0 G + 1,4 W)", f(vf["Msd"]) + " / " + f(vf["MRd"]), f(vf["uso_M"], 3)],
       ["Cortante", f(vf["Vsd"]) + " / " + f(vf["VRd"]), f(vf["uso_V"], 3)],
       ["Flecha G + Q (L/250)", f"{f(fl['GQ_mm'])} / {f(fl['lim_L250_mm'])} mm", f(fl["GQ_mm"] / fl["lim_L250_mm"], 3)],
       ["Montantes (compressão)", "-", f(max(m["uso_compressao"] for m in CB["montantes"]), 3)],
       ["Barras M20 (tração na sucção)", "-", f(max(m["uso_barra"] for m in CB["montantes"]), 3)]]
y = pr.tabela(XC, y - 4, "VERIFICAÇÕES (NBR 8800:2024)", ["ITEM", "Sd / Rd", "USO"], ver, [80, 60, 30])
notas = [f"W 310 × 32,7 contínua de A a E (vão máximo {f(CB['vao_max_m'], 2)} m), apoiada só nos pilares: A (recuo do P1-L2), B, C (topo do P8A), D, P6 da linha 2 e E (recuo do P2-L2). Faixa de influência {f(CB['trib_m'], 2)} m; cargas g {f(CB['cargas_kN_m']['g_k'], 2)}, q {f(CB['cargas_kN_m']['q_k'], 2)} e sucção {f(CB['cargas_kN_m']['w_suc_corpo'], 2)} kN/m (NBR 6123:2023).",
         f"Flambagem lateral: mesa superior travada pelas terças (ST-W a cada {f(CB['verificacoes']['Lb_m'], 2)} m); mesa inferior (comprimida na sucção) travada pelas mãos-francesas MF-1 em TODA terça, dos dois lados ({CB['mao_francesa']['norma']}).",
         "Montantes W 150 × 22,5 soldados de oficina nas chapas de base CB e de topo CT; na obra: CB sobre porcas de nivelamento nas 4 BR-M20 embutidas no topo do pilar (graute 20 mm), CT parafusada na mesa inferior da W com 4 M16 8.8.",
         "Emendas nas posições da elevação (fora dos apoios), talas TL-1 nas duas mesas e TL-2 nos dois lados da alma, M16 8.8 com aperto controlado; furos padrão (d + 1,5 mm).",
         "Tudo parafusado na obra; aço A572-50 (perfis) e A36 (chapas e cantoneiras), galvanizado a fogo. Terças, telhas e acessórios: ND-LET-COB01 a COB04.",
         "Montagem: depois do mezanino e da parede G da linha 2 (ND-LET-MON01/MON02): montantes → módulos da W de A para E com as emendas → ST-W e terças → mãos-francesas.",
         "Cotas em mm, níveis em m. Não medir no desenho."]
pr.notas(XC, y - 4, notas, 182)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-COB05")
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
for a in avisos:
    print(a)
