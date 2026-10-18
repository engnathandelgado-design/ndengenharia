"""ND-LET-PP03 — console CS-1 (rev06c): conjunto soldado com corte cotado, vistas, símbolos de solda, isométrico montado e
explodido com balões, peças (itens), parafusos/porcas com detalhe de rosca, regulagem e lista de materiais. Cotas em mm."""
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
import json
import math
import fechamento as FCH
import geo_fixacao as GF
import iso_nd as I
from prancha_nd import Prancha

C, HX, T, N = GF.C, GF.HX, GF.T, GF.N
co, al, me, de, po = C["costas"], C["alma"], C["mesa"], C["dente"], C["ponta"]
yn, zf = C["y_nivel"], C["z_frontal"]
G0 = T["G"]
hb = G0 - HX["k"]                                        # face de baixo da cabeça do nível (posição nominal)
y_tip = T["a"] + N["P"] - N["t_fundo"]                   # ponta do prisioneiro no fundo do nicho (nominal)
f = lambda v, d=2: f"{v:.{d}f}".replace(".", ",")
PP01 = json.load(open("/home/claude/letsara/pranchas/pp01.json"))
N_OBRA = PP01["n"]["CS1"]
FXJ = GF.FX

pr = Prancha("A1", dict(cliente=FCH.CLIENTE, obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="FIXAÇÃO DAS PLACAS (SISTEMA TREJOR) — CONSOLE CS-1: CONJUNTO SOLDADO, PEÇAS, PARAFUSOS, SOLDAS E LISTA DE MATERIAIS",
                        desenho="ND-LET-PP03", folha="01/01", fase="PARA APROVAÇÃO", rev="06"))
pr.revisao("06", "18/10/2026", "EMISSÃO: FABRICAÇÃO DO CS-1 (2 DENTES 19, M16 DE NÍVEL COM PORCA SOLDADA, PRISIONEIRO FRONTAL)")
Q = pr.quadro
XC = Q[2] - 250
pr.cabecalho_peca("CS-1", f"CONSOLE CS-1 — CONJUNTO SOLDADO — {N_OBRA} PEÇAS (2 POR PLACA, EXCETO PONTAS DE PORTA)",
                  "soldado na obra na chapa de espera CE-1 do pilar (ND-LET-PP04) · recebe o peso e o vento de uma ponta de placa · cotas em mm",
                  largura=XC - Q[0] - 10)
HT = 0.45


def ch(v, x, y, w, h):
    v.chapa(x, y, w, h, HT)


# ================================================================== CORTE A-A (plano do eixo, y-z) 1:1,5
va = pr.vista("CORTE A-A", (Q[0] + 125, Q[1] + 410), 1.5, titulo="CORTE A-A (EIXO DO CONSOLE)",
              subtitulo="face da CE-1 à esquerda; parafusos na posição nominal (G = 50)", unidade="mm")
ch(va, 0, co["z0"], co["t"], co["z1"] - co["z0"])                                   # costas (cortada)
va.poli(GF.alma_poli(), "VISTA", fechada=True)                                       # alma vista ao fundo
ch(va, me["y0"], -me["t"], me["y1"] - me["y0"], me["t"])                             # mesa (cortada)
va.ret(de["y0"], 0, de["t"], de["h"], "VISTA")                                       # dente visto ao fundo
ch(va, po["y0"], po["z0"], po["t"], po["z1"] - po["z0"])                             # chapa de ponta (cortada)
# nível: porca soldada + contraporca + parafuso (cabeça em cima)
e2 = HX["e"] / 2
va.ret(yn - e2, 0, HX["e"], HX["m"], "METALICA"); va.ret(yn - e2, HX["m"], HX["e"], HX["m_fina"], "METALICA")
I.parafuso_lateral(va, hb, yn, C["L_nivel"], 16, cabeca=(HX["k"], HX["s"]), sentido=-1, eixo="y")
# frontal: porca soldada atrás da chapa de ponta + prisioneiro
va.ret(po["y0"] - HX["m"], zf - e2, HX["m"], HX["e"], "METALICA")
I.parafuso_lateral(va, y_tip - C["L_frontal"], zf, C["L_frontal"], 16, sentido=1)
va.linha((y_tip, zf - 14), (y_tip, zf + 14), "OCULTA")
va.texto((y_tip + 2, zf + 16), "fundo do NC-1", "nota", "BOTTOM_LEFT")
va.cota_h([0, co["t"], de["y0"], de["y0"] + de["t"], me["y1"]], co["z0"], -8, total=False)
va.cota_h([0, yn], co["z1"], 8, total=False)
va.cota_h([y_tip - C["L_frontal"], y_tip], zf, -22, total=False)
va.cota_v([co["z0"], -al["h_raiz"], po["z0"], zf, -me["t"], 0, HX["m"], HX["m"] + HX["m_fina"], hb, G0, co["z1"]], 0, -12, total=False)
va.cota_v([0, de["h"]], de["y0"] + de["t"], 26, total=False)
I.solda(va, (co["t"], -40), (16, -30), a=6, tipo="filete", lado="ambos", cauda="alma × costas")
I.solda(va, (co["t"], -me["t"] / 2), (-30, 36), a=6, tipo="filete", lado="ambos", cauda="mesa × costas")
I.solda(va, (de["y0"], 4), (-28, 52), a=8, tipo="filete", lado="seta", contorno=True, cauda="dentes × mesa")
I.solda(va, (po["y0"], po["z0"] + 4), (20, -40), a=5, tipo="filete", lado="seta", contorno=True, cauda="ponta × almas e mesa")
I.solda(va, (po["y0"] - HX["m"], zf - 10), (-34, -58), a=5, tipo="filete", lado="seta", contorno=True, cauda="porca frontal × ponta")
I.solda(va, (yn - e2, 4), (-40, 70), a=4, tipo="filete", lado="seta", cauda="porca × mesa, 3 faces")
I.solda(va, (0, co["z0"] + 30), (-24, -20), a=6, tipo="filete", lado="seta", campo=True, comp=co["z1"] - co["z0"], cauda="OBRA: costas × CE-1, 2 lados verticais")

# ================================================================== VISTA FRONTAL (do lado da placa) 1:1,5
vf = pr.vista("VISTA FRONTAL", (Q[0] + 300, Q[1] + 410), 1.5, titulo="VISTA FRONTAL", subtitulo="pelo lado da placa", unidade="mm")
vf.ret(-co["b"] / 2, co["z0"], co["b"], co["z1"] - co["z0"], "VISTA")              # costas ao fundo
for xa in (-al["x"], al["x"]):
    ch(vf, xa - al["t"] / 2, -al["h_ponta"], al["t"], al["h_ponta"] - me["t"])     # topo das almas na ponta
    vf.ret(xa - al["t"] / 2, -al["h_raiz"], al["t"], al["h_raiz"] - al["h_ponta"], "OCULTA")
ch(vf, -me["b"] / 2, -me["t"], me["b"], me["t"])
for sg in (-1, 1):
    x0 = min(sg * de["x0"], sg * (de["x0"] + de["b"]))
    ch(vf, x0, 0, de["b"], de["h"])
ch(vf, -po["b"] / 2, po["z0"], po["b"], po["z1"] - po["z0"])
vf.circulo((0, zf), 8, "METALICA"); I.hexagono(vf, (0, zf), 8, "METALICA", rot=0)
vf.ret(-HX["s"] / 2, 0, HX["s"], HX["m"], "METALICA"); vf.ret(-HX["s"] / 2, HX["m"], HX["s"], HX["m_fina"], "METALICA")
vf.ret(-8, HX["m"] + HX["m_fina"], 16, hb - HX["m"] - HX["m_fina"], "METALICA"); vf.ret(-HX["s"] / 2, hb, HX["s"], HX["k"], "METALICA")
vf.cota_h([-co["b"] / 2, -me["b"] / 2, -de["x0"] - de["b"], -de["x0"], de["x0"], de["x0"] + de["b"], me["b"] / 2, co["b"] / 2], co["z0"], -8, total=True)
vf.cota_h([-al["x"] - al["t"] / 2, -al["x"] + al["t"] / 2, al["x"] - al["t"] / 2, al["x"] + al["t"] / 2], co["z1"], 8, total=False)
vf.cota_v([po["z0"], zf, po["z1"]], co["b"] / 2, 10, total=False)
vf.chamada((0, zf), (22, -26), "prisioneiro M16 (sext. interno 8)")

# ================================================================== VISTA SUPERIOR 1:1,5
vs = pr.vista("VISTA SUPERIOR", (Q[0] + 300, Q[1] + 475), 1.5, titulo="VISTA SUPERIOR", subtitulo="face da CE-1 embaixo", unidade="mm")
ch(vs, -co["b"] / 2, 0, co["b"], co["t"])
ch(vs, -me["b"] / 2, me["y0"], me["b"], me["y1"] - me["y0"])
for sg in (-1, 1):
    x0 = min(sg * de["x0"], sg * (de["x0"] + de["b"]))
    vs.ret(x0, de["y0"], de["b"], de["t"], "METALICA")
I.hexagono(vs, (0, yn), HX["s"], "METALICA", rot=0); vs.circulo((0, yn), 8, "METALICA")
vs.cota_h([-me["b"] / 2, 0, me["b"] / 2], me["y1"], 8, total=False)
vs.cota_v([0, co["t"], yn, me["y1"]], co["b"] / 2, 10, total=False)

# ================================================================== isométricos
cam = I.Camera((1.1, 1.35, 0.85))
vi = pr.vista("ISO", (Q[0] + 418, Q[1] + 430), 2.2, titulo="ISOMÉTRICO", subtitulo="lado da placa", unidade="mm")
I.desenhar_iso(vi, GF.cs1_solidos(0), cam)
ve = pr.vista("EXPLODIDO", (Q[0] + 498, Q[1] + 440), 2.8, titulo="ISOMÉTRICO EXPLODIDO", subtitulo="balões = itens", unidade="mm")
SE = GF.cs1_solidos(34)
pj = I.desenhar_iso(ve, SE, cam)
anc = {}
for s in SE:
    if s.item and s.item not in anc:
        anc[s.item] = s.centro
desl = {10: (-14, -10), 11: (-14, -6), 12: (-16, 4), 13: (12, 8), 14: (12, -8), 15: (14, 2), 16: (12, 6), 17: (-14, 4), 18: (12, -4)}
for k, p in anc.items():
    I.balao(ve, pj(p), desl.get(k, (10, 6)), k)

# ================================================================== peças 1:1,5
yP = Q[1] + 200
p10 = pr.vista("ITEM 10 — COSTAS", (Q[0] + 30, Q[1] + 60), 1.5, titulo="ITEM 10 — COSTAS", subtitulo="CH 16 A572-50", unidade="mm")
ch(p10, 0, 0, co["b"], co["z1"] - co["z0"])
p10.ret((co["b"] - me["b"]) / 2, co["z1"] - co["z0"] - 30 - me["t"], me["b"], me["t"], "OCULTA")
p10.cota_h([0, (co["b"] - me["b"]) / 2, (co["b"] + me["b"]) / 2, co["b"]], 0, -8, total=True)
p10.cota_v([0, co["z1"] - co["z0"] - 30 - me["t"], co["z1"] - co["z0"] - 30, co["z1"] - co["z0"]], co["b"], 10, total=False)
p10.chamada((co["b"] / 2, co["z1"] - co["z0"] - 38), (16, -12), "traçar a mesa")

p11 = pr.vista("ITEM 11 — ALMA", (Q[0] + 140, Q[1] + 105), 1.5, titulo="ITEM 11 — ALMA (2×)", subtitulo="CH 9,5 A572-50", unidade="mm")
pa = [(y - al["y0"], z + me["t"]) for y, z in GF.alma_poli()]
p11.poli(pa, "METALICA", fechada=True); p11.hachura(pa, "ANSI31", HT, "METALICA")
p11.cota_h([0, al["y1"] - al["y0"]], -(al["h_raiz"] - me["t"]), -8, total=False)
p11.cota_v([-(al["h_raiz"] - me["t"]), -(al["h_ponta"] - me["t"]), 0], al["y1"] - al["y0"], 10, total=False)

p12 = pr.vista("ITEM 12 — MESA", (Q[0] + 140, Q[1] + 175), 1.5, titulo="ITEM 12 — MESA", subtitulo="CH 16 A572-50, furo Ø18", unidade="mm")
ch(p12, 0, 0, me["b"], me["y1"] - me["y0"])
p12.circulo((me["b"] / 2, yn - me["y0"]), 9, "METALICA")
p12.cota_h([0, me["b"] / 2, me["b"]], 0, -8, total=False)
p12.cota_v([0, yn - me["y0"], me["y1"] - me["y0"]], me["b"], 10, total=False)
p12.cota_diam((me["b"] / 2, yn - me["y0"]), 9, ang=135)

p13 = pr.vista("ITEM 13 — DENTE", (Q[0] + 262, Q[1] + 175), 1.5, titulo="ITEM 13 — DENTE (2×)", subtitulo="CH 19 A572-50", unidade="mm")
ch(p13, 0, 0, de["b"], de["h"])
p13.cota_h([0, de["b"]], 0, -8, total=False)
p13.cota_v([0, de["h"]], de["b"], 10, total=False)
p13.chamada((de["b"] / 2, de["h"]), (6, 8), "esp. 19")

p14 = pr.vista("ITEM 14 — CHAPA DE PONTA", (Q[0] + 230, Q[1] + 95), 1.5, titulo="ITEM 14 — CHAPA DE PONTA", subtitulo="CH 9,5 A572-50, furo Ø18", unidade="mm")
hp = po["z1"] - po["z0"]
ch(p14, 0, 0, po["b"], hp)
p14.circulo((po["b"] / 2, zf - po["z0"]), 9, "METALICA")
p14.cota_h([0, po["b"] / 2, po["b"]], 0, -8, total=False)
p14.cota_v([0, zf - po["z0"], hp], po["b"], 10, total=False)

# ================================================================== parafusos e porcas (1:1) com rosca
vp = pr.vista("FIXADORES", (Q[0] + 360, Q[1] + 200), 1.0, titulo="ITENS 15 A 18 — PARAFUSOS E PORCAS", subtitulo="ESC. 1:1; rosca métrica grossa M16 × 2 (6g/6H), dmín. 13,5", unidade="mm")
# 16 — M16 × 45 rosca total
I.parafuso_lateral(vp, 0, 0, C["L_nivel"], 16, cabeca=(HX["k"], HX["s"]), sentido=1)
vp.cota_h([-HX["k"], 0, C["L_nivel"]], -14, -8, total=False)
vp.cota_v([-8, 8], C["L_nivel"], 10, total=False)
vp.texto((C["L_nivel"] / 2, 17), f"16 — M16 × {C['L_nivel']:g} ISO 4017 8.8, rosca total", "nota", "BOTTOM_CENTER")
# 18 — prisioneiro
X18 = 90
I.parafuso_lateral(vp, X18, 0, C["L_frontal"], 16, sentido=1)
vp.ret(X18, -4, 6, 8, "OCULTA")
vp.cota_h([X18, X18 + 6, X18 + C["L_frontal"]], -14, -8, total=False)
vp.texto((X18 + C["L_frontal"] / 2, 17), "18 — prisioneiro M16 × 45 ISO 4026 45H", "nota", "BOTTOM_CENTER")
vp.texto((X18 + C["L_frontal"] / 2, 12), "sext. interno 8 × 6, ponta plana", "nota", "BOTTOM_CENTER")
# 15 — porca e 17 — contraporca (vista lateral e de topo)
X15 = 0
Y15 = -70
I.porca_lateral(vp, X15, Y15, HX["m"], HX["s"])
vp.cota_h([X15, X15 + HX["m"]], Y15 - HX["e"] / 2, -6, total=False)
vp.cota_v([Y15 - HX["s"] / 2, Y15 + HX["s"] / 2], X15 + HX["m"], 6, total=False)
I.hexagono(vp, (X15 + 45, Y15), HX["s"]); I.furo_roscado(vp, (X15 + 45, Y15), 16)
vp.texto((X15 + 25, Y15 - 28), "15 — porca M16 ISO 4032 cl. 8 (m 14,8, s 24)", "nota", "TOP_CENTER")
X17 = 95
I.porca_lateral(vp, X17, Y15, HX["m_fina"], HX["s"])
vp.cota_h([X17, X17 + HX["m_fina"]], Y15 - HX["e"] / 2, -6, total=False)
I.hexagono(vp, (X17 + 35, Y15), HX["s"]); I.furo_roscado(vp, (X17 + 35, Y15), 16)
vp.texto((X17 + 20, Y15 - 28), "17 — contraporca M16 ISO 4035 (m 8)", "nota", "TOP_CENTER")

# ================================================================== tabelas
it = GF.cs1_itens()
rows, tot = [], 0.0
for n, nome, dim, mat, q, kg in it:
    rows.append([n, nome, dim, mat, q, f(kg, 3), f(kg * q, 3)])
    tot += kg * q
rows.append(["", "PESO TOTAL DO CONJUNTO (kg)", "", "", "", "", f(tot, 2)])
y = pr.tabela(XC, Q[3] - 6, "LISTA DE MATERIAIS — CS-1 (1 CONJUNTO)", ["Nº", "DESCRIÇÃO", "DIMENSÃO (mm)", "MATERIAL", "QTD", "kg/un", "kg"],
              rows, [9, 54, 78, 38, 10, 20, 21], h_lin=5.4, destaque_ultima=True)
pr.texto(XC, y - 3.5, f"Obra: {N_OBRA} conjuntos → {f(tot * N_OBRA, 0)} kg (aço + parafusos).", "nota", "TEXTO")
json.dump(dict(kg_CS1=tot), open("/home/claude/letsara/pranchas/pp03.json", "w"))
MO = FXJ["montagem_CS1_NC1"]
reg = [["M16 de nível (16)", f"topo da cabeça a G = {G0:g} ± {T['G_tol']:g} acima da mesa", "contraporca (17) 120 N·m"],
       ["prisioneiro (18)", f"ponta a {y_tip:g} ± {T['a_tol']:g} da face da CE-1 (afastamento {T['a']:g})", "trava química média"],
       ["placa na montagem", f"teto do nicho {MO['janela_R_mm']['G=50'][0]:g} a {MO['janela_R_mm']['G=50'][1]:g} acima da final (G = 50)", "encostar e baixar"]]
y = pr.tabela(XC, y - 8, "REGULAGEM (ANTES DE IÇAR A PLACA)", ["PEÇA", "AJUSTE", "TRAVAMENTO"], reg, [40, 130, 60], h_lin=5.4)
pr.notas(XC, y - 4, [
    "Medidas em mm. Tolerâncias gerais NBR ISO 2768-1 classe m; furos Ø18 ± 0,3; esquadro mesa × costas 90° ± 0,5°.",
    "Corte a laser ou plasma de alta definição; peças isentas de rebarbas e arestas cortantes; quebrar cantos vivos 1 mm.",
    "Soldagem de oficina GMAW (MIG) ER70S-6 Ø1,0 com Ar + 20 % CO₂ (ou FCAW E71T-1 com CO₂), soldador qualificado (AWS D1.1); soldas contínuas, isentas de trincas, porosidade e mordeduras; inspeção visual 100 %.",
    "Sequência: (1) almas e mesa nas costas (gabarito, esquadro); (2) chapa de ponta entre as almas; (3) dentes sobre as almas; (4) porcas (15) centradas nos furos com um parafuso-guia, solda 4 em 3 faces alternadas (nível) e 5 no contorno (frontal), sem respingo na rosca.",
    "Galvanização a fogo após a soldagem (NBR 6323, ≥ 85 µm); porcas soldadas com rosca sobremedida (repassar a rosca depois da galvanização). Parafusos galvanizados a fogo, prisioneiro zincado.",
    f"Solda de obra só costas × CE-1: filete 6 E70XX nos 2 lados verticais ({co["z1"] - co["z0"]:g} mm), soldador qualificado, inspeção visual 100 % e líquido penetrante em 10 %; galvanização a frio no cordão. Nível do topo da mesa pela topografia (±3).",
    f"Folgas verificadas no pior caso das tolerâncias (afastamento {T['a']:g} ± {T['a_tol']:g}, G {G0:g} ± {T['G_tol']:g}, posição ± {T['x_tol']:g}): engate aba × dente ≥ {MO['folgas_mm']['engate aba–dente com G máximo (z)']:g}, rosca do nível ≥ 16 fios-mm, janela de montagem ≥ 15 (memória ND-LET-MC07).",
    "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."], 250)
av = pr.salvar("/home/claude/letsara/pranchas/ND-LET-PP03")
print("PP03", len([a for a in av if a[0] == "ERRO"]), "erros,", len(av), "avisos", [a for a in av if a[0] == "ERRO" or "sobrep" in a[1]][:14])
