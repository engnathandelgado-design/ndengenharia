"""ND-LET-PP02 — nicho NC-1 (rev06c): desenho de fabricação no padrão das pranchas de fôrma ND — vistas cotadas com
símbolos de solda, isométrico montado e explodido com balões, peças (itens) cotadas, lista de materiais e notas de fabricação.
Geometria: geo_fixacao.py (fixacao_placas.json, GEO). Cotas em mm."""
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
import json
import fechamento as FCH
import geo_fixacao as GF
gg = lambda v: f"{v:g}".replace(".", ",")
AS = GF.N["a_solda"]
import iso_nd as I
from prancha_nd import Prancha

N = GF.N
B, H, P = N["B"], N["H"], N["P"]
tt, tb, tf, tp, ta, ha = N["t_teto"], N["t_base"], N["t_fundo"], N["t_parede"], N["t_aba"], N["h_aba"]
pf = P - tf
yg, dg = N["y_gr"], N["d_gr"]
hgt, hgb = N["h_gr_teto"], N["h_gr_base"]
XG = [x for par in N["x_gr"] for x in par]
AE, AD = N["aba_e"], N["aba_d"]
za = H - tt - ha                                    # face de baixo das abas
f = lambda v, d=2: f"{v:.{d}f}".replace(".", ",")
PP01 = json.load(open("/home/claude/letsara/pranchas/pp01.json"))
N_OBRA, N_E, N_D = PP01["n"]["NC1"], PP01["n"]["NC1_E"], PP01["n"]["NC1_D"]

pr = Prancha("A1", dict(cliente=FCH.CLIENTE, obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="FIXAÇÃO DAS PLACAS (SISTEMA TREJOR) — NICHO NC-1: CONJUNTO SOLDADO, PEÇAS, SOLDAS E LISTA DE MATERIAIS",
                        desenho="ND-LET-PP02", folha="01/01", fase="PARA APROVAÇÃO", rev="06"))
pr.revisao("06", "18/10/2026", "EMISSÃO: FABRICAÇÃO DO NC-1 (ESPESSURA DE CADA CHAPA PELO MEF, GRAMPOS Ø6,3)")
Q = pr.quadro
XC = Q[2] - 190
pr.cabecalho_peca("NC-1", f"NICHO NC-1 — CONJUNTO SOLDADO — {N_E} NC-1 + {N_D} NC-1' (ESPELHADO) = {N_OBRA} PEÇAS",
                  f"embutido nas 2 pontas de cada placa (ND-LET-PP00/PP01) · {B:g} × {H:g} × {P:g} · aberto na boca e na ponta · cotas em mm",
                  largura=XC - 60 - Q[0] - 10)


def chapa_lat(v, x, y, w, h):
    v.chapa(x, y, w, h, 0.45)


# ================================================================== VISTA FRONTAL (pela boca) 1:1,5
vf = pr.vista("VISTA FRONTAL", (Q[0] + 40, Q[1] + 345), 2.0, titulo="VISTA FRONTAL (PELA BOCA)",
              subtitulo="pela face interna; ponta à esquerda", unidade="mm")
vf.ret(0, tb, B - tp, H - tt - tb, "VISTA")                                     # fundo, visto ao fundo
chapa_lat(vf, 0, H - tt, B, tt)                                                 # teto
chapa_lat(vf, 0, 0, B, tb)                                                      # base
chapa_lat(vf, B - tp, tb, tp, H - tt - tb)                                      # parede
chapa_lat(vf, AE[0], za, AE[1] - AE[0], ha)                                     # aba E
chapa_lat(vf, AD[0], za, AD[1] - AD[0], ha)                                     # aba D
for (x0, x1) in N["x_gr"]:
    vf.poli([(x0, H), (x0, H + hgt), (x1, H + hgt), (x1, H)], "ARMADURA")
    vf.poli([(x0, 0), (x0, -hgb), (x1, -hgb), (x1, 0)], "ARMADURA")
vf.cota_h([0, AE[1], AD[0], AD[1], B], -hgb, -8, total=True)
vf.cota_h([0] + XG + [B], H + hgt, 6, total=False)
vf.cota_v([-hgb, 0, tb, za, H - tt, H, H + hgt], 0, -10, total=False)
vf.cota_v([0, H], 0, -18, total=False)                                          # rev08: altura total à esquerda (direita fica para as soldas)
vf.texto((-4, H / 2), "PONTA DA PLACA", "nota", "MIDDLE_CENTER", rot=90)
I.solda(vf, (AE[1] - 6, H - tt), (36, -30), a=None, tipo="chanfro", lado="seta", cauda=f"CJP + filete {gg(AS['aba_teto'])} (det. A)")
I.solda(vf, (B - tp, 160), (24, 14), a=AS["parede"], tipo="filete", lado="ambos", contorno=True, cauda="parede: 3 lados, dentro e fora")
I.solda(vf, (XG[3], H + 20), (40, 6), a=AS["grampo"], tipo="filete", lado="ambos", comp=20, cauda="cada perna (4×)")
vf.marcador_corte((25, -45), (25, H + 60), "A", lado=1)

# ================================================================== CORTE A-A (lateral) 1:1,5
va = pr.vista("CORTE A-A", (Q[0] + 205, Q[1] + 345), 2.0, titulo="CORTE A-A", subtitulo="boca à esquerda", unidade="mm")
va.ret(0, tb, pf, H - tt - tb, "VISTA")                                        # parede lateral vista ao fundo
chapa_lat(va, 0, H - tt, pf, tt)
chapa_lat(va, 0, 0, pf, tb)
chapa_lat(va, pf, 0, tf, H)
chapa_lat(va, 0, za, ta, ha)
va.ret(yg - dg / 2, H, dg, hgt, "ARMADURA"); va.ret(yg - dg / 2, -hgb, dg, hgb, "ARMADURA")
va.cota_h([0, ta, yg, pf, P], -hgb, -8, total=True)
va.cota_v([-hgb, 0, tb, za, H - tt, H, H + hgt], P, 14, total=False)
va.texto((-4, H / 2), "BOCA", "nota", "MIDDLE_CENTER", rot=90)
I.solda(va, (pf, H - tt / 2), (22, 16), a=AS["teto_fundo"], tipo="filete", lado="ambos", cauda="teto × fundo")
I.solda(va, (pf, tb / 2), (30, -30), a=AS["base_fundo"], tipo="filete", lado="ambos", cauda="base × fundo")
I.solda(va, (ta, H - tt - 2), (44, -40), a=AS["aba_teto"], tipo="filete", lado="seta", cauda="aba × teto (atrás)")

# ================================================================== VISTA SUPERIOR 1:1,5
vs = pr.vista("VISTA SUPERIOR", (Q[0] + 290, Q[1] + 507), 2.0, titulo="VISTA SUPERIOR", subtitulo="boca embaixo; abas e parede tracejadas", unidade="mm")
chapa_lat(vs, 0, 0, B, pf)
chapa_lat(vs, 0, pf, B, tf)
vs.ret(B - tp, 0, tp, pf, "OCULTA")
vs.ret(AE[0], 0, AE[1] - AE[0], ta, "OCULTA"); vs.ret(AD[0], 0, AD[1] - AD[0], ta, "OCULTA")
for (x0, x1) in N["x_gr"]:
    vs.ret(x0 - dg / 2, yg - dg / 2, x1 - x0 + dg, dg, "ARMADURA")
vs.cota_h([0] + XG + [B], 0, -8, total=False)
vs.cota_v([0, yg, pf, P], B, 10, total=False)

# ================================================================== isométricos
cam = I.Camera((-1.0, -1.35, 0.85))
vi = pr.vista("ISO", (Q[0] + 395, Q[1] + 400), 2.5, titulo="ISOMÉTRICO", subtitulo="vista pela boca", unidade="mm")
I.desenhar_iso(vi, GF.nc1_solidos(0), cam)
ve = pr.vista("EXPLODIDO", (Q[0] + 490, Q[1] + 420), 2.7, titulo="ISOMÉTRICO EXPLODIDO", subtitulo="balões = itens da lista de materiais", unidade="mm")
SE = GF.nc1_solidos(34)
pj = I.desenhar_iso(ve, SE, cam)
ancora = {}
for s in SE:
    if s.item and s.item not in ancora:
        ancora[s.item] = s.centro
desl = {1: (16, 18), 2: (-26, -14), 3: (12, 10), 4: (12, -8), 5: (-14, 4), 6: (12, 6), 7: (-12, 6), 8: (12, -6)}
for k, p in ancora.items():
    I.balao(ve, pj(p), desl[k], k)

# ================================================================== peças (itens) 1:2
y0p = Q[1] + 120


def peca(nome, org, esc=2.0, sub=None):
    return pr.vista(nome, org, esc, titulo=nome, subtitulo=sub, unidade="mm")


p1 = peca("ITEM 1 — TETO", (Q[0] + 25, y0p + 95), sub=f"CH {gg(tt)} A572-50; traçar a posição dos grampos")
chapa_lat(p1, 0, 0, B, pf)
for x in XG:
    p1.circulo((x, yg), dg / 2, "ARMADURA")
p1.cota_h([0] + XG + [B], 0, -8, total=False)
p1.cota_v([0, yg, pf], B, 10, total=False)
p1.chamada((B / 2, pf), (4, 8), f"esp. {gg(tt)} — 1 por conjunto")

p2 = peca("ITEM 2 — BASE", (Q[0] + 25, y0p - 30), sub=f"CH {gg(tb)} A572-50")
chapa_lat(p2, 0, 0, B, pf)
for x in XG:
    p2.circulo((x, yg), dg / 2, "ARMADURA")
p2.cota_h([0, B], 0, -8, total=False)
p2.cota_v([0, yg, pf], B, 10, total=False)
p2.chamada((B / 2, pf), (4, 8), f"esp. {gg(tb)} — 1 por conjunto")

p3 = peca("ITEM 3 — FUNDO", (Q[0] + 135, y0p - 30), sub=f"CH {gg(tf)} A572-50")
chapa_lat(p3, 0, 0, B, H)
p3.cota_h([0, B], 0, -8, total=False)
p3.cota_v([0, H], B, 10, total=False)
p3.chamada((B / 2, H), (4, 8), f"esp. {gg(tf)} — 1 por conjunto")

p4 = peca("ITEM 4 — PAREDE", (Q[0] + 245, y0p - 30), sub=f"CH {gg(tp)} A36, filete {gg(AS['parede'])} dos dois lados")
chapa_lat(p4, 0, 0, pf, H - tt - tb)
p4.cota_h([0, pf], 0, -8, total=False)
p4.cota_v([0, H - tt - tb], pf, 10, total=False)
p4.chamada((pf / 2, H - tt - tb), (4, 8), f"esp. {gg(tp)} — 1 por conjunto")

p5 = peca("ITEM 5 — ABA E", (Q[0] + 345, y0p + 95), sub=f"CH {gg(ta)} A572-50")
chapa_lat(p5, 0, 0, AE[1] - AE[0], ha)
p5.cota_h([0, AE[1] - AE[0]], 0, -8, total=False)
p5.cota_v([0, ha], AE[1] - AE[0], 10, total=False)
X5 = 60                                                                        # perfil do chanfro (vista lateral da aba)
p5.poli([(X5, 0), (X5 + ta, 0), (X5 + ta, ha), (X5 + 6, ha), (X5, ha - 6)], "METALICA", fechada=True)
p5.hachura([(X5, 0), (X5 + ta, 0), (X5 + ta, ha), (X5 + 6, ha), (X5, ha - 6)], "ANSI31", 0.45, "METALICA")
p5.cota_h([X5, X5 + 6, X5 + ta], ha, 8, total=False)
p5.chamada((X5 + 2, ha - 3), (8, 10), "chanfro 45° × 6 (lado da boca)")

p6 = peca("ITEM 6 — ABA D", (Q[0] + 345, y0p - 10), sub=f"CH {gg(ta)} A572-50, chanfro igual ao 5")
chapa_lat(p6, 0, 0, AD[1] - AD[0], ha)
p6.cota_h([0, AD[1] - AD[0]], 0, -8, total=False)
p6.cota_v([0, ha], AD[1] - AD[0], 10, total=False)

p7 = peca("ITENS 7 E 8 — GRAMPOS U", (Q[0] + 460, y0p - 10), sub=f"RED Ø{dg:g} A36 dobrado a frio, raio interno 10")
L7 = XG[1] - XG[0]
p7.poli([(0, 0), (0, hgt), (L7, hgt), (L7, 0)], "ARMADURA")
p7.cota_h([0, L7], hgt, 8, total=False)
p7.cota_v([0, hgt], 0, -10, total=False)
p7.texto((L7 / 2, -10), f"7 (teto): desenv. {2 * hgt + L7:g}", "nota", "TOP_CENTER")
X8 = 110
p7.poli([(X8, 0), (X8, hgb), (X8 + L7, hgb), (X8 + L7, 0)], "ARMADURA")
p7.cota_h([X8, X8 + L7], hgb, 8, total=False)
p7.cota_v([0, hgb], X8 + L7, 10, total=False)
p7.texto((X8 + L7 / 2, -10), f"8 (base): desenv. {2 * hgb + L7:g}", "nota", "TOP_CENTER")

# detalhe A: junta aba × teto (1:1)
dA = peca("DETALHE A — JUNTA ABA × TETO", (Q[0] + 500, y0p + 105), 1.0, sub=f"penetração total pela boca + filete {gg(AS['aba_teto'])} atrás")
dA.chapa(-10, ha, 70, tt, 0.5)                                                 # teto (corte)
dA.poli([(0, 0), (ta, 0), (ta, ha), (6, ha), (0, ha - 6)], "METALICA", fechada=True)
dA.hachura([(0, 0), (ta, 0), (ta, ha), (6, ha), (0, ha - 6)], "ANSI31", 0.5, "METALICA")
dA.hachura([(0, ha - 6), (6, ha), (0, ha)], "SOLID", 0.06, "METALICA")
dA.hachura([(ta, ha), (ta + 6, ha), (ta, ha - 6)], "SOLID", 0.06, "METALICA")
dA.cota_h([0, 6, ta], 0, -8, total=False)
dA.chamada((2, ha - 1), (-14, 8), "CJP, esmerilhar rente à boca")
dA.chamada((ta + 2, ha - 2), (12, -6), f"filete {gg(AS['aba_teto'])}")
dA.texto((-6, ha / 2), "BOCA", "nota", "MIDDLE_CENTER", rot=90)

# ================================================================== tabelas
it = GF.nc1_itens()
rows, tot = [], 0.0
for n, nome, dim, mat, q, kg in it:
    rows.append([n, nome, dim, mat, q, f(kg, 3), f(kg * q, 3)])
    tot += kg * q
rows.append(["", "PESO TOTAL DO CONJUNTO (kg)", "", "", "", "", f(tot, 2)])
y = pr.tabela(XC - 60, Q[3] - 6, "LISTA DE MATERIAIS — NC-1 (1 CONJUNTO)", ["Nº", "DESCRIÇÃO", "DIMENSÃO (mm)", "MATERIAL", "QTD", "kg/un", "kg"],
              rows, [9, 50, 52, 34, 10, 22, 23], h_lin=5.4, destaque_ultima=True)
y = pr.tabela(XC - 60, y - 4, "QUANTIDADE NA OBRA", ["CONJUNTO", "USO", "QTD", "kg"],
              [["NC-1", "ponta inicial da placa (início do comprimento na vista PP-x)", N_E, f(tot * N_E, 0)],
               ["NC-1'", "ponta final — espelhado (abas e parede trocam de lado)", N_D, f(tot * N_D, 0)],
               ["", "total", N_OBRA, f(tot * N_OBRA, 0)]], [22, 120, 18, 40], h_lin=5.4, destaque_ultima=True)
json.dump(dict(kg_NC1=tot), open("/home/claude/letsara/pranchas/pp02.json", "w"))
pr.notas(XC - 60, y - 4, [
    "Medidas em mm. Tolerâncias gerais NBR ISO 2768-1 classe m (corte e esquadro ±0,5); vão interno teto–base 178 ± 1 e profundidade 47,5 ± 1 (gabarito). Planicidade das chapas ≤ 1 mm.",
    "Corte a laser ou guilhotina; peças isentas de rebarbas e arestas cortantes; quebrar cantos vivos 1 mm.",
    "Soldagem de oficina GMAW (MIG) ER70S-6 Ø1,0 com Ar + 20 % CO₂ (ou FCAW E71T-1 com CO₂), soldador qualificado (AWS D1.1); soldas contínuas, isentas de trincas, porosidade e mordeduras; inspeção visual 100 %.",
    "Sequência: (1) teto + fundo + base no gabarito, pontear e conferir o vão 178 e o esquadro; (2) soldas teto × fundo e base × fundo; (3) abas pela boca (CJP, det. A) e filete atrás; (4) parede lateral; (5) grampos (filete " + gg(AS["grampo"]) + " × 20 nos 2 lados de cada perna).",
    f"Espessura de cada chapa pelo cálculo (MEF): teto e abas {gg(tt)} e fundo {gg(tf)} recebem as forças do console; base {gg(tb)} e parede {gg(tp)} são finas — "
    f"soldar a parede com MIG de baixa corrente (Ø0,8), filete {gg(AS['parede'])} contínuo dentro e fora (AWS D1.3), sem furar a chapa. Itens 1 a 3, 5 e 6 em A572-50; parede em A36.",
    "Galvanização a fogo após a soldagem (NBR 6323, ≥ 85 µm); retocar com galvanização a frio onde houver dano.",
    "Na fôrma da placa: boca rente à face interna (lado da fôrma) e ponta rente à cabeceira, preso no gabarito (posição ±5); vedar a cavidade com isopor antes de concretar. NC-1 na ponta inicial e NC-1' (espelhado) na final; pontas do lado da porta (vista I) sem nicho.",
    "Grampos dentro dos estribos N5 (teto) e N6 (base) da armação da ponta (ND-LET-PP01, det. 1 e 2).",
    "EMISSÃO EXECUTIVA — LIBERADO PARA PRODUÇÃO E MONTAGEM."], 250)
FCH.chave_todas(pr)                                     # rev11 (checklist 6): planta-chave com as paredes nas cores A–J
av = pr.salvar("/home/claude/letsara/pranchas/ND-LET-PP02")
print("PP02", len([a for a in av if a[0] == "ERRO"]), "erros,", len(av), "avisos", av)
