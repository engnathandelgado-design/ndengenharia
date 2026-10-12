from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
wb = Workbook()
F = "Arial"
bold = Font(name=F, bold=True); norm = Font(name=F); blue = Font(name=F, color="0000FF"); green = Font(name=F, color="008000")
yellow = PatternFill("solid", fgColor="FFFF00"); head = PatternFill("solid", fgColor="D9D9D9")
thin = Side(style="thin", color="999999"); box = Border(left=thin, right=thin, top=thin, bottom=thin)
BRL = '"R$" #,##0.00;("R$" #,##0.00);-'; KG = '#,##0.0;(#,##0.0);-'; PCT = '0.0%'

# ---------------- Premissas
ws = wb.active; ws.title = "Premissas"
ws["A1"] = "PREMISSAS DE CUSTO — PILARES LETSARA (células amarelas: editar)"; ws["A1"].font = Font(name=F, bold=True, size=12)
ws["A2"] = "Fonte dos preços: a preencher com os valores da fábrica (compra + corte/dobra + montagem). Os valores iniciais são estimativas da ND para o sul do PR, out/2026."; ws["A2"].font = Font(name=F, italic=True, size=9)
rows = [
 ("Aço CA-50 colocado (R$/kg)", 9.50, "inclui corte, dobra e montagem"),
 ("Cordoalha CP-190 RB Ø12,7 colocada (R$/kg)", 12.00, "inclui perda de pista (~8 %)"),
 ("Operação de protensão por peça (R$/peça)", 180.00, "estiramento, cabeceira, corte"),
 ("Concreto C40 lançado (R$/m³)", 650.00, "igual nas duas opções"),
 ("Fôrma metálica — uso por peça (R$/peça)", 350.00, "igual nas duas opções"),
 ("Mão de obra de armação extra por kg (R$/kg)", 0.00, "já incluída no aço colocado; use se a fábrica separa"),
 ("Massa linear Ø20 (kg/m)", 2.466, "NBR 7480"),
 ("Massa linear Ø25 (kg/m)", 3.853, "NBR 7480"),
 ("Massa linear Ø8 (kg/m)", 0.395, "NBR 7480"),
 ("Massa linear cordoalha Ø12,7 (kg/m)", 0.780, "7 fios, 98,7 mm²"),
 ("Perda de pista da cordoalha (fração)", 0.08, "comprimento morto nas cabeceiras"),
 ("Perdas/ganchos do aço passivo (fração)", 0.10, "sobre o comprimento reto"),
 ("Comprimento do pilar com cálice (m)", 11.0, "10,0 + 1,0 de embutimento"),
 ("Pilares laterais 40×60 (un)", 18, "P1 e P2, linhas 1 a 9"),
 ("Pilares de fachada 40×60 (un)", 6, "P3–P5 e P14–P16"),
]
ws.append([]); ws.append(["Item", "Valor", "Observação"])
for c in ws[4]: c.font = bold; c.fill = head; c.border = box
for i, (a, v, o) in enumerate(rows, start=5):
    ws.cell(i, 1, a).font = norm; cv = ws.cell(i, 2, v); cv.font = blue; cv.fill = yellow; cv.border = box; ws.cell(i, 3, o).font = Font(name=F, size=9, italic=True)
    cv.number_format = BRL if "R$" in a else ('0.0%' if "fração" in a else '0.000' if "kg/m" in a else '0')
ws.column_dimensions["A"].width = 48; ws.column_dimensions["B"].width = 14; ws.column_dimensions["C"].width = 50
P = {a: f"Premissas!$B${i}" for i, (a, _, _) in enumerate(rows, start=5)}
k = lambda s: P[next(a for a in P if a.startswith(s))]

# ---------------- Pilares (quantitativos por peça)
w2 = wb.create_sheet("Pilares")
w2["A1"] = "QUANTITATIVOS POR PILAR 40×60 × 11 m — ARMADO × PROTENDIDO"; w2["A1"].font = Font(name=F, bold=True, size=12)
w2["A2"] = "Armaduras das verificações pelo método geral (DEC-012). Estribos Ø8 c/15 iguais nas duas opções. Cordoalhas a 250 mm do eixo, 5 por face."; w2["A2"].font = Font(name=F, italic=True, size=9)
w2.append([]); w2.append(["Item", "Unid.", "Armado", "Protendido", "Como foi calculado"])
for c in w2[4]: c.font = bold; c.fill = head; c.border = box
L = k("Comprimento do pilar")
lines = [
 ("Concreto C40", "m³", f"=0.40*0.60*{L}", f"=0.40*0.60*{L}", "0,40 × 0,60 × L"),
 ("Barras Ø20 (un)", "un", 10, 8, "armado: 5 por face de 40; protendido: 8 Ø20 (4 por face de 60)"),
 ("Barras Ø25 (un)", "un", 6, 0, "armado: 3 intermediárias por face de 60 (4 Ø25 por face com os cantos)"),
 ("Aço longitudinal CA-50", "kg", f"=(C6*{k('Massa linear Ø20')}+C7*{k('Massa linear Ø25')})*{L}*(1+{k('Perdas/ganchos')})",
                                   f"=(D6*{k('Massa linear Ø20')}+D7*{k('Massa linear Ø25')})*{L}*(1+{k('Perdas/ganchos')})", "n × kg/m × L × (1 + perdas)"),
 ("Estribos Ø8 c/15", "kg", f"=ROUNDUP({L}/0.15,0)*1.90*{k('Massa linear Ø8')}", f"=ROUNDUP({L}/0.15,0)*1.90*{k('Massa linear Ø8')}", "perímetro 1,78 m + ganchos = 1,90 m por estribo"),
 ("Aço CA-50 total", "kg", "=C8+C9", "=D8+D9", ""),
 ("Cordoalhas Ø12,7 (un)", "un", 0, 10, "5 por face a 250 mm do eixo"),
 ("Cordoalha CP-190", "kg", f"=C11*{L}*{k('Massa linear cordoalha')}*(1+{k('Perda de pista')})", f"=D11*{L}*{k('Massa linear cordoalha')}*(1+{k('Perda de pista')})", "n × L × kg/m × (1 + perda de pista)"),
 ("Taxa de aço passivo", "%", "=C10/(C5*7850)", "=D10/(D5*7850)", "kg de aço / kg de concreto (7850 kg/m³ de aço)"),
]
for i, (a, u, ca, cp, o) in enumerate(lines, start=5):
    w2.cell(i, 1, a).font = norm; w2.cell(i, 2, u).font = norm
    for col, v in ((3, ca), (4, cp)):
        c = w2.cell(i, col, v); c.border = box
        c.font = blue if isinstance(v, (int, float)) else norm
        if isinstance(v, (int, float)): c.fill = yellow
        c.number_format = PCT if u == "%" else ('0.000' if u == "m³" else KG if u == "kg" else '0')
    w2.cell(i, 5, o).font = Font(name=F, size=9, italic=True)
w2.column_dimensions["A"].width = 30; w2.column_dimensions["B"].width = 7; w2.column_dimensions["C"].width = 14; w2.column_dimensions["D"].width = 14; w2.column_dimensions["E"].width = 60
w2["A17"] = "Custo por pilar"; w2["A17"].font = bold
cost = [
 ("Concreto", f"=C5*{k('Concreto C40')}", f"=D5*{k('Concreto C40')}"),
 ("Aço CA-50", f"=C10*({k('Aço CA-50')}+{k('Mão de obra de armação')})", f"=D10*({k('Aço CA-50')}+{k('Mão de obra de armação')})"),
 ("Cordoalha", f"=C12*{k('Cordoalha CP-190')}", f"=D12*{k('Cordoalha CP-190')}"),
 ("Operação de protensão", f"=IF(C11>0,{k('Operação de protensão')},0)", f"=IF(D11>0,{k('Operação de protensão')},0)"),
 ("Fôrma", f"={k('Fôrma metálica')}", f"={k('Fôrma metálica')}"),
 ("TOTAL por pilar", "=SUM(C18:C22)", "=SUM(D18:D22)"),
]
for i, (a, ca, cp) in enumerate(cost, start=18):
    w2.cell(i, 1, a).font = bold if "TOTAL" in a else norm
    for col, v in ((3, ca), (4, cp)):
        c = w2.cell(i, col, v); c.number_format = BRL; c.border = box; c.font = bold if "TOTAL" in a else norm
w2["A25"] = "Diferença por pilar (protendido − armado)"; w2["A25"].font = bold
w2["C25"] = "=D23-C23"; w2["C25"].number_format = BRL; w2["C25"].font = bold
w2["D25"] = "=IF(C23=0,0,D23/C23-1)"; w2["D25"].number_format = PCT

# ---------------- Comparativo
w3 = wb.create_sheet("Comparativo")
w3["A1"] = "COMPARATIVO — 24 PILARES 40×60 (laterais + fachadas)"; w3["A1"].font = Font(name=F, bold=True, size=12)
w3.append([]); w3.append(["", "Armado", "Protendido", "Diferença"])
for c in w3[3]: c.font = bold; c.fill = head; c.border = box
n = f"({k('Pilares laterais')}+{k('Pilares de fachada')})"
comp = [
 ("Pilares (un)", f"={n}", f"={n}", "=C4-B4", '0'),
 ("Aço CA-50 total (kg)", f"=Pilares!C10*{n}", f"=Pilares!D10*{n}", "=C5-B5", KG),
 ("Cordoalha total (kg)", f"=Pilares!C12*{n}", f"=Pilares!D12*{n}", "=C6-B6", KG),
 ("Concreto total (m³)", f"=Pilares!C5*{n}", f"=Pilares!D5*{n}", "=C7-B7", '0.0'),
 ("Custo total (R$)", f"=Pilares!C23*{n}", f"=Pilares!D23*{n}", "=C8-B8", BRL),
 ("Custo por pilar (R$)", "=Pilares!C23", "=Pilares!D23", "=C9-B9", BRL),
 ("Variação (%)", "", "", "=IF(B8=0,0,C8/B8-1)", PCT),
]
for i, (a, b_, c_, d_, fmt) in enumerate(comp, start=4):
    w3.cell(i, 1, a).font = norm
    for col, v in ((2, b_), (3, c_), (4, d_)):
        c = w3.cell(i, col, v); c.number_format = fmt; c.border = box; c.font = green if "Pilares!" in str(v) or "Premissas!" in str(v) else norm
w3["A12"] = "O que não entra no custo e pesa na decisão"; w3["A12"].font = bold
for j, t in enumerate(["Protendido: pilar sem fissura na combinação frequente e no içamento (menos reparo e melhor aparência).",
                       "Protendido: cabeceira regulada em 525 mm; ocupa pista de protensão (concorre com as vigas).",
                       "Armado: fissura na combinação rara de vento (8,8 MPa de tração) e perde rigidez depois disso; protendido também fissura na rara (4,7 MPa), mas com 16 cordoalhas não fissuraria.",
                       "Os dois atendem à armadura mínima passiva (0,4 % Ac = 9,6 cm²): armado 51 cm² (2,1 %), protendido 25 cm² (1,05 %).",
                       "Preços em amarelo são estimativas: trocar pelos da fábrica antes de decidir."], start=13):
    w3.cell(j, 1, f"{j-12}. {t}").font = Font(name=F, size=9)
w3.column_dimensions["A"].width = 30
for col in "BCD": w3.column_dimensions[col].width = 16
w3["A20"] = "Legenda: amarelo/azul = entrada editável; preto = fórmula; verde = vem de outra aba."; w3["A20"].font = Font(name=F, size=9, italic=True)
wb.save("/home/claude/letsara/custo/Letsara-custo-pilares.xlsx")
print("ok")
