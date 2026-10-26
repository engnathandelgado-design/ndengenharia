"""ND-LET-COB07 — terças: comprimentos, transpasses e folgas de montagem em cadeia (rev11, Nathan 26/10/2026, checklist 8).
Elevação de uma linha de terças com as 8 peças em cadeia (ponta, transpasse, eixos, total), posição das 32 linhas de terças ao
longo da água (cadeia e ordenadas a partir do eixo A), tabela de comprimentos por vão e tabela de folgas. Fonte: cob_comum.py
(cobertura_metalica.json) — a mesma da COB01/COB08 e do 3D. Cotas em mm. A1."""
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha
from cob_comum import (YLmm, VAOS, XT, NT, X_C, X_E, X0E, X0D, LTS, L_TERCA, EXT, EXT_F, A_TR, B_TR, Y_COL, H_TERCA, BASE_K, PESO_UE,
                       PERFIL_TXT, cabecalho, f)

pr = Prancha("A1", cabecalho("ND-LET-COB07", "01/01", "COBERTURA METÁLICA — TERÇAS: COMPRIMENTOS, TRANSPASSES E FOLGAS DE MONTAGEM EM CADEIA"))
pr.revisao("11", "26/10/2026", "EMISSÃO: COMPRIMENTOS E FOLGAS DAS TERÇAS EM CADEIA (CHECKLIST 8)")
Q = pr.quadro
fm = lambda v: f"{v:,.0f}".replace(",", ".")

# ------------------------------------------------------------------ 1. ELEVAÇÃO DE UMA LINHA DE TERÇAS (1:125)
E1 = 125
Z_TOP = 2600                                       # peças dos vãos ímpares (1-2, 3-4...) desenhadas acima, pares abaixo
y_ini = YLmm[0] - EXT[0][0]
y_fim = YLmm[8] + EXT[7][1]
v = pr.vista("ELEVAÇÃO", (Q[0] + 70 - y_ini / E1, Q[3] - 70), E1, titulo="ELEVAÇÃO DE UMA LINHA DE TERÇAS — AS 8 PEÇAS EM CADEIA",
             subtitulo=f"{PERFIL_TXT}; peças de vãos alternados desenhadas em 2 alturas para mostrar o transpasse; mesma cadeia nas 32 linhas")
for i, yl in enumerate(YLmm):
    v.linha((yl, -2300), (yl, 0), "EIXO")                       # eixo só fora do vão entre as 2 alturas (cota do transpasse livre)
    v.linha((yl, Z_TOP), (yl, Z_TOP + H_TERCA + 300), "EIXO")
    v.circulo((yl, -2300 - 4.2 * E1), 4.2 * E1, "INDICACAO")
    v.texto((yl, -2300 - 4.2 * E1), str(i + 1), "nota", "MIDDLE_CENTER")
for k in range(8):
    a, b = YLmm[k] - EXT[k][0], YLmm[k + 1] + EXT[k][1]
    z0 = Z_TOP if k % 2 == 0 else 0
    v.ret(a, z0, b - a, H_TERCA, "METALICA")
    if k % 2 == 0:
        v.cota_h([a, b], z0 + H_TERCA, 8, total=False)
    else:
        v.cota_h([a, b], z0, -13, total=False)
    v.texto((a - 200, z0 + H_TERCA / 2), f"peça {BASE_K[k]}", "nota", "MIDDLE_RIGHT")
# transpasses entre as 2 alturas, a cada eixo interno
for i in range(1, 8):
    v.cota_h([YLmm[i] - A_TR, YLmm[i] + A_TR], H_TERCA, 9, total=False)
# eixos e total
v.cota_h(YLmm, -1500, -6, total=False)
v.cota_h([y_ini, y_fim], Z_TOP + H_TERCA, 20, total=False)
v.chamada((y_ini, Z_TOP + 150), (-6, 12), f"ponta a {EXT_F} do eixo 1")
v.chamada((y_fim, 150), (6, 12), f"ponta a {EXT[7][1]} do eixo 9")

# ------------------------------------------------------------------ 2. POSIÇÃO DAS TERÇAS AO LONGO DA ÁGUA (1:70)
E2 = 70
w = pr.vista("CADEIA DAS TERÇAS", (Q[0] + 40, Q[3] - 255), E2, titulo="POSIÇÃO DAS 32 LINHAS DE TERÇAS AO LONGO DA ÁGUA",
             subtitulo="alma de cada terça sobre as vigas de cobertura das 2 meias águas; espaçamento em cadeia (embaixo) e ordenadas a partir do eixo A (em cima)")
w.linha((0, 0), (X_E, 0), "VISTA")
for x0_ in (X0E, X0D):
    w.ret(x0_, -250, LTS, 250, "VISTA")                         # viga de cobertura de cada meia água
for x in XT:
    w.ret(x - 45, 0, 90, 180, "METALICA")
for lbl, x in (("A", 0), ("C", X_C), ("E", X_E)):
    w.linha((x, -2300), (x, 180), "EIXO")
    w.circulo((x, -2300 - 4.2 * E2), 4.2 * E2, "INDICACAO")
    w.texto((x, -2300 - 4.2 * E2), lbl, "nota", "MIDDLE_CENTER")
w.cota_h(XT[:NT], -250, -8, total=False)
w.cota_h(XT[NT:], -250, -8, total=False)
w.cota_h([XT[0], XT[NT - 1]], -250, -18, total=False)
w.cota_h([XT[NT], XT[-1]], -250, -18, total=False)
w.cota_h([0, X_C, X_E], -250, -28, total=False)
w.cota_ord(XT, 180, 10, x0=0)
w.chamada((X_C, -250), (14, -36), f"eixo C: {X_C - XT[NT - 1]} e {XT[NT] - X_C} das terças vizinhas")
w.chamada((X_E, -250), (-14, -36), f"eixo E: {X_E - XT[-1]} da última terça")
w.chamada((0, -250), (14, -36), f"eixo A: {XT[0]} até a 1ª terça (calha)")

# ------------------------------------------------------------------ 3. tabelas
lin = []
for k in range(8):
    lin.append([f"{k + 1}-{k + 2}", fm(VAOS[k]), f"{EXT[k][0]}", f"{EXT[k][1]}", fm(L_TERCA[k]), BASE_K[k], f"{2 * NT}",
                f(2 * NT * L_TERCA[k] / 1000 * PESO_UE, 0)])
tot = sum(2 * NT * L_TERCA[k] / 1000 * PESO_UE for k in range(8))
lin.append(["TOTAL", fm(YLmm[-1] - YLmm[0]), "", "", fm(sum(L_TERCA) - 7 * 2 * A_TR) + " *", "", f"{16 * NT}", f(tot, 0)])
x0t = Q[0] + 8
y = pr.tabela(x0t, Q[3] - 360, "COMPRIMENTO DAS TERÇAS POR VÃO", ["VÃO", "ENTRE EIXOS", "ANTES DO EIXO INICIAL", "DEPOIS DO EIXO FINAL", "L DA PEÇA",
                                                                    "PEÇA", "QT", "kg"], lin, [18, 26, 38, 38, 26, 16, 14, 22], destaque_ultima=True)
pr.notas(x0t, y - 2, [f"* comprimento da linha montada de ponta a ponta = soma das peças − 7 transpasses de {2 * A_TR} = {fm(y_fim - y_ini)}."], 200, titulo="")
FOL = [["transpasse em cada apoio interno", f"{2 * A_TR} ({A_TR} para cada lado do eixo)", "2 Z encaixados (METLAP); sem folga ponta a ponta"],
       ["ponta da terça na fachada", f"{EXT_F} além do eixo da VB = {EXT_F - 75} além da face", "folga até a placa de fechamento ≥ 75"],
       ["furos da alma (M12)", "Ø14 (+2 mm)", "fábrica; proibido furar na obra"],
       ["aba do ST-1P / ST-1V nas esperas", "oblongo 18 × 40 (±11 ao longo da viga)", "absorve a tolerância da viga e do alinhamento"],
       ["nivelamento do ST-1P", "porca de nivelamento + 10 sob a terça", "fundo da terça 10 acima do concreto"],
       ["tolerância de montagem por vão", "±5 (eixo a eixo); ±10 acumulado na linha", "acima disso: corrigir a viga antes de montar"],
       ["linhas de terças (alma)", "±5 em planta; ±3 entre terças vizinhas", "alinhar com linha de nylon antes do aperto final"]]
y = pr.tabela(Q[0] + 230, Q[3] - 360, "FOLGAS E TOLERÂNCIAS DE MONTAGEM", ["ONDE", "FOLGA / TOLERÂNCIA", "OBSERVAÇÃO"], FOL, [58, 70, 80])
notas = [f"Terças {PERFIL_TXT}, contínuas por transpasse; cada peça vence um vão e passa {A_TR} do eixo de cada apoio interno; nas fachadas passa {EXT_F} do eixo da VB.",
         f"Furação das peças por marca na ND-LET-COB08; ligações (ST-1P, transpasse, ST-W) nos isométricos da ND-LET-COB09; planta e marcas na ND-LET-COB01.",
         "Montar do vão 1-2 para o 8-9: cada peça encaixada na anterior no transpasse; aperto final só com a linha inteira montada e alinhada."]
pr.notas(Q[0] + 230, y - 4, notas, 210)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-COB07")
for a in avisos:
    print(a)
