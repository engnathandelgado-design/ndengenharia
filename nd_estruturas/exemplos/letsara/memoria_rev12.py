"""Memória de cálculo ND-LET-MC12 (PDF) — alterações do pacote rev12 (26/10/2026); cabeçalho copiado da MC10.
(MC09: alterações do pacote rev09 (23/10/2026, DEC-045 a DEC-049):
pisos +3,90 / +7,30 (fonte única geometria.Z_PISOS), cargas do mezanino (cargas_mezanino.json), VM retangulares protendidas 30 × 75
com dente Gerber 45 (vm_retangular.json, estudo_vm_largura.json, mef_vm_ret_dente_750_450.json), consolos CP-MEZ (consolos.json),
laje alveolar LP20 (laje_alveolar.json), cobertura metálica da linha 2 (cob_linha2.json), escada metálica (escada_metalica.json),
pilares da escada e P6 da linha 2 (dimensionamento_pilares_r05.json / arranjo_pilares.json) e cargas na fundação (cargas_fundacao.json).
Substitui, para as VM, os itens de meio vaso das memórias MC05 e MC08 (rev06)."""
import json, sys
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

AQ = Path(__file__).parent
J = lambda n: json.loads((AQ / n).read_text(encoding="utf-8"))
VM, ES, LA, CB, ESC, CM, CF, CO = (J("vm_retangular.json"), J("estudo_vm_largura.json"), J("laje_alveolar.json"), J("cob_linha2.json"),
                                   J("escada_metalica.json"), J("cargas_mezanino.json"), J("cargas_fundacao.json"), J("consolos.json"))
MV = J("mef_vm_ret_dente_750_450.json")
EX, I1 = J("escada_externa.json"), J("i110_r01.json")
ESD, PJ, DP = J("escadas.json"), J("portao_l4.json"), J("arranjo_pilares.json")
NOME_I = {"V407": "V400", "V406": "V401", "V405": "V402", "V404": "V403"}
DI = J("dentes.json")["I120"]
N9C = [c for c in J("nbr9062.json")["consolos"] if c["consolo"] == "CP-I120"][0]
P_ = VM["premissas"]
f = lambda v, d=1: (f"{v:.{d}f}".replace(".", ",") if isinstance(v, (int, float)) else str(v))
ok = lambda b: "ok" if b else "NÃO"
for nome, arq in (("DV", "DejaVuSans.ttf"), ("DVB", "DejaVuSans-Bold.ttf")):
    for base in ("/usr/share/fonts/truetype/dejavu/", "/usr/share/fonts/dejavu/"):
        if Path(base + arq).exists():
            pdfmetrics.registerFont(TTFont(nome, base + arq)); break
ss = getSampleStyleSheet()
N = ParagraphStyle("n", parent=ss["Normal"], fontName="DV", fontSize=8.4, leading=11.2)
T1 = ParagraphStyle("t1", parent=N, fontName="DVB", fontSize=13, leading=17, spaceBefore=8, spaceAfter=4)
T2 = ParagraphStyle("t2", parent=N, fontName="DVB", fontSize=10.2, leading=14, spaceBefore=7, spaceAfter=3)
P = lambda t: Paragraph(t, N)


def tab(linhas, larg):
    t = Table([[P(str(c)) for c in l] for l in linhas], colWidths=[w * mm for w in larg], repeatRows=1)
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.3, colors.grey), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8e8"))]))
    return t



import math, sys as _sys
_sys.path.insert(0, "/home/claude/letsara/pranchas")
N9 = J("nbr9062.json"); LG = J("ligacoes.json"); PLJ = J("placas.json")
CT = [c for c in N9["consolos"] if c["consolo"] == "CT-I120"][0]
NEO3C = [a for a in N9["aparelhos"] if a["aparelho"].startswith("NEO-3C")][0]
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import fechamento as FCH
SAI = Path("/home/claude/letsara/entregas/ND-LET-MC12-REV12-rev12.pdf")
doc = SimpleDocTemplate(str(SAI), pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=15 * mm, bottomMargin=15 * mm,
                        title="Letsara — memória MC12: alterações do pacote rev12", author="ND Engenharia")
LV = LA["verif"]
CF2 = J("consolos_face.json")
CBM = J("cobertura_metalica.json")
I6 = I1["V406"]
E = [Paragraph("MEMÓRIA DE CÁLCULO ND-LET-MC12 — ALTERAÇÕES DO PACOTE REV12 (26/10/2026)", T1),
     P("Obra: Letsara — pavilhão com mezanino (Marques Engenharia). Correções da revisão independente da rev11 e decisões de 26/10: laje LP20 com 9 Ø12,7, família I120 (antes chamada I130, seção h 120) com N3 ≤ Ø20, "
       "vigas de borda rentes à face externa dos pilares de fachada nos vãos entre PF, densidade única 2,50 t/m³. Complementa a MC09 e a MC10. Documento para análise antes do zip com DXF e IFC."),
     Paragraph("1. Laje alveolar LP20 — 9 Ø12,7 CP-190 RB, capa 5 cm (NBR 14861:2022; NBR 6118:2023; NBR 9062:2017)", T2),
     P(f"Arranjo: 2 cordoalhas em cada nervura de borda (uma sobre a outra, eixos a 4,0 e 7,5 cm do fundo, espaço livre 2,2 cm ≥ 2 cm e ≥ Ø) + 5 nas nervuras internas a 4,0 cm; Ap = {f(LA['Ap_mm2'], 1)} mm²; "
       f"σpi = {f(LA['sig_pi'], 0)} MPa; liberação com fckj ≥ {f(LA['fckj'], 0)} MPa; lbpt = {f(LA['lbpt_m'] * 100, 0)} cm; perdas totais {f(LA['perdas']['perda_total_pct'], 1)} %. Vão de cálculo {f(LA.get('L_calc_m', 9.45), 2)} m (peça 9,55 m). "
       "Sem Ø15,2 (regra ND). PENDÊNCIA: confirmar com a fábrica que a extrusora aceita 2 cordoalhas na nervura de borda."),
     tab([["VERIFICAÇÃO", "VALOR", "LIMITE", "USO", ""]] + [[k.replace("_", " "), f(v["valor"], 2), f(v["limite"], 2), f(v["uso"], 2), ok(v["ok"])] for k, v in LV.items()], [70, 24, 24, 16, 12]),
     P(f"Flechas: contraflecha na liberação {f(LA['flechas_mm']['contraflecha_fabricacao'])} mm, na montagem {f(LA['flechas_mm']['contraflecha_montagem'])} mm, final {f(LA['flechas_mm']['final'])} mm ≤ L/250 = {f(LA['flechas_mm']['lim_final_L250'])} mm. "
       f"+7,30 (laje de cobertura): {ok(LA['nivel_730']['ok'])}. LA-03/LA-04 (escada): {LA['LA03'].get('arranjo')} — {ok(LA['LA03']['ok'])}."),
     Paragraph("2. Viga central I120 — N3 10 Ø20 em 2 camadas (antes 6 Ø25)", T2),
     P(f"As do N3 = 31,4 cm² (antes 29,5), centroide 2,25 cm mais baixo. Resultados (calc_i110_r01, V406 governante dos 3 vãos de 16,52 m): ELU Md {f(I6['ELU']['Md'])} ≤ MRd {f(I6['ELU']['MRd'])} kN·m, x/d {f(I6['ELU']['x_d'], 3)} ≤ 0,45; "
       f"ato As,topo {f(I6['ato']['As_topo_cm2'], 2)} ≤ {f(I6['ato']['As_N3_cm2'], 2)} cm²; ELS {ok(I6['ELS']['ok'])}; cortante {ok(I6['cortante']['ok'])}; flecha final {f(I6['flecha']['final_mm'])} mm. "
       f"V400 (19,50 m): ELU {f(I1['V407']['ELU']['Md'])} ≤ {f(I1['V407']['ELU']['MRd'])} kN·m. Volume e peso de cada marca por um só cálculo (viga_i.vol_viga, maciços de 1,40 m e dentes): "
       + ", ".join(f"{NOME_I[k]} {f(I1[k]['icamento']['peso_kN'] / 10, 2)} t" for k in ("V407", "V406", "V405", "V404")) + "."),
     Paragraph("3. Vigas de borda rentes à face externa dos pilares de fachada (NBR 9062:2017 7.3; NBR 6118:2023 17.2.5 e 17.5)", T2),
     P(f"Nos vãos B–C e C–D das linhas 1 e 9 (VB-02, VB-03, VB-06, VB-07) a VB 15×60 e o consolo CP-VB ficam rentes à face externa do pilar 40×60: eixo da VB a e = {f(CF2['e_m'] * 100, 1)} cm do eixo do pilar, 2,5 cm até a placa. "
       f"O consolo continua com a carga centrada (mesma geometria, armadura e Fd = {f(CF2['Fd_kN'])} kN do C1; tirante com cobrimento lateral 3 cm na face C) e ganha marca própria. No pilar: momento adicional Mx = Σ Vd·e somado em valor absoluto a todas as combinações e torção Td = Hd·e."),
     tab([["PILAR", "FACES", "ΔMd (kN·m)", "USO ANTES", "USO COM e", "Td / TRd2 (kN·m)", ""]] +
         [[k, ", ".join(v["faces"]), f(v["dM_kNm"]), f(v["uso_antes"], 3), f(v["uso_com_excentricidade"], 3), f"{f(v['Td_kNm'], 2)} / {f(v['TRd2_kNm'], 0)}", ok(v["ok"])] for k, v in CF2["pilares"].items()],
         [20, 16, 24, 22, 22, 34, 12]),
     P(f"Terças: o 1º e o último vão das terças da faixa B–D crescem {f(CF2['e_m'] * 1000, 0)} mm (peças T6/T7); ponta a 85 mm do eixo da VB (borda dos furos 25 mm ≥ 22 mm, NBR 8800:2024 Tab. 14), 15 mm antes da placa. "
       f"Terça Z 302 × 2,30 com os vãos novos: uso {f(CBM['terca']['governante']['uso'], 3)} (antes 0,851); parafusos do transpasse {f(CBM['terca']['parafusos_transpasse']['uso'], 3)}. "
       "Vãos de canto e VM de borda da linha 1: em decisão (quadro decisao_fresta_canto) — o pilar de canto tem 40 em y e a face fica 10 cm atrás da dos PF."),
     Paragraph("4. Densidade e pesos", T2),
     P("Peso = volume × 25 kN/m³; t = kN / 10 (2,50 t/m³) em todo o jogo: IC01, folhas das peças, PR01, quantitativos e montagem (antes a IC01 e a TS-01 usavam 9,81). A IC01 lê os pesos da mesma lista de peças do PR01; σ no furo FI-1 em MPa; coluna βa = 1,3 em todas as tabelas."),
     Paragraph("5. Barras das peças e pinos de ligação", T2),
     P("Armadura passiva longitudinal das vigas com Ø ≥ 12,5 (TS-01: N5 e N9 passam de Ø10 para Ø12,5; As do topo 7,36 cm²) e nenhuma barra de armadura acima de Ø20. "
       "Única exceção registrada (DEC-083): pino de ligação PN-2 Ø25 CA-50 (L = 900, 350 no consolo) da I120 nos consolos CP-I120 (PF04, PC01, PC02, PC03) — inserto de ligação, não armadura; a confirmar."),
     Paragraph("6. Pendências", T2),
     P("(a) Extrusora: 2 cordoalhas na nervura de borda da LP20. (b) Decisão: fresta nos vãos de canto das VB e na VM de borda da linha 1. (c) Decisão: CE-1 dos PG-02/PG-04 (face de 25 cm). (c2) Confirmar o pino PN-2 Ø25 da I120 (ou trocar por Ø20). "
       "(d) Local da obra (V0, S2, S3 da NBR 6123:2023), ART e TRRF. (e) Zip com DXF e IFC só depois da aprovação deste pacote.")]
doc.build(E)
print("ok", SAI)
