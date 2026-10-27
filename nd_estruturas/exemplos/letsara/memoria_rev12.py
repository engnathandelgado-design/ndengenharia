"""Memória de cálculo ND-LET-MC12 (PDF) — alterações do pacote rev12 (26/10/2026); cabeçalho copiado da MC10.
(MC09: alterações do pacote rev09 (23/10/2026, DEC-045 a DEC-049):
pisos +3,90 / +7,30 (fonte única geometria.Z_PISOS), cargas do mezanino (cargas_mezanino.json), VM retangulares protendidas 30 × 75
com dente Gerber 45 (vm_retangular.json, estudo_vm_largura.json, mef_vm_ret_dente_750_450.json), consolos CP-MEZ (consolos.json),
laje alveolar LP20 (laje_alveolar.json), cobertura metálica da linha 2 (cob_linha2.json), escada metálica (escada_metalica.json),
pilares da escada e P6 da linha 2 (dimensionamento_pilares_r05.json / arranjo_pilares.json) e cargas na fundação (cargas_fundacao.json).
Substitui, para as VM, os itens de meio vaso das memórias MC05 e MC08 (rev06)."""
import json, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/letsara/pranchas")
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
import renomear as _RNm                                                       # rev12: nomes do projeto pela posição (não os do modelo)
NOME_P = lambda k: _RNm.pilar_em(CF["pilares"][k]["x"], CF["pilares"][k]["y"])
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
CFU = J("cargas_fundacao.json")["pilares"]
DPR = J("dimensionamento_pilares_r05.json")
LA_NOVA = dict(L_peca=J("vm_retangular.json")["premissas"]["vao_laje"])
E = [Paragraph("MEMÓRIA DE CÁLCULO ND-LET-MC12 — ALTERAÇÕES DO PACOTE REV12 (26 E 27/10/2026)", T1),
     P("Obra: Letsara — pavilhão com mezanino (Marques Engenharia). Correções da revisão independente da rev11 e decisões de 26/10: laje LP20 com 9 Ø12,7, família I120 (antes chamada I130, seção h 120) com N3 ≤ Ø20, "
       "vigas de borda rentes à face externa dos pilares de fachada, densidade única 2,50 t/m³; 27/10: pilares de canto 10 cm para fora (face alinhada à dos PF, VB rente à face em todos os vãos) e PG-02/PG-04 25 × 40 com a face no plano dos vizinhos. Este PDF reúne a memória vigente: MC12 (alterações rev12) seguida da MC10 e da MC09, que continuam valendo no que não foi alterado — índice abaixo. Documento para análise antes do zip com DXF e IFC."),
     Paragraph("1. Laje alveolar LP20 — 9 Ø12,7 CP-190 RB, capa 5 cm (NBR 14861:2022; NBR 6118:2023; NBR 9062:2017)", T2),
     P(f"Arranjo: 2 cordoalhas em cada nervura de borda (uma sobre a outra, eixos a 4,0 e 7,5 cm do fundo, espaço livre 2,2 cm ≥ 2 cm e ≥ Ø) + 5 nas nervuras internas a 4,0 cm; Ap = {f(LA['Ap_mm2'], 1)} mm²; "
       f"σpi = {f(LA['sig_pi'], 0)} MPa; liberação com fckj ≥ {f(LA['fckj'], 0)} MPa; lbpt = {f(LA['lbpt_m'] * 100, 0)} cm; perdas totais {f(LA['perdas']['perda_total_pct'], 1)} %. Vão de cálculo {f(LA.get('L_calc_m', 9.45), 2)} m (peça 9,55 m). "
       "Sem Ø15,2 (regra ND). PENDÊNCIA: confirmar com a fábrica que a extrusora aceita 2 cordoalhas na nervura de borda."),
     tab([["VERIFICAÇÃO", "VALOR", "LIMITE", "USO", ""]] + [[k.replace("_", " "), f(v["valor"], 2), f(v["limite"], 2), f(v["uso"], 2), ok(v["ok"])] for k, v in LV.items()], [70, 24, 24, 16, 12]),
     P(f"Flechas: contraflecha na liberação {f(LA['flechas_mm']['contraflecha_fabricacao'])} mm, na montagem {f(LA['flechas_mm']['contraflecha_montagem'])} mm, final {f(LA['flechas_mm']['final'])} mm ≤ L/250 = {f(LA['flechas_mm']['lim_final_L250'])} mm. "
       f"+7,30 (laje de cobertura): {ok(LA['nivel_730']['ok'])}. LA-03/LA-04 (escada): {LA['LA03'].get('arranjo')} — {ok(LA['LA03']['ok'])}."),
     Paragraph("2. Viga central I120 — N3 10 Ø20 em 2 camadas (antes 6 Ø25)", T2),
     P(f"As do N3 = 31,4 cm² (antes 29,5), centroide 2,25 cm mais baixo. Resultados ({NOME_I["V406"]} governante dos 3 vãos de 16,52 m: {NOME_I["V406"]}, {NOME_I["V405"]} e {NOME_I["V404"]}): ELU Md {f(I6['ELU']['Md'])} ≤ MRd {f(I6['ELU']['MRd'])} kN·m, x/d {f(I6['ELU']['x_d'], 3)} ≤ 0,45; "
       f"ato As,topo {f(I6['ato']['As_topo_cm2'], 2)} ≤ {f(I6['ato']['As_N3_cm2'], 2)} cm²; ELS {ok(I6['ELS']['ok'])}; cortante {ok(I6['cortante']['ok'])}; flecha final {f(I6['flecha']['final_mm'])} mm. "
       f"V400 (19,50 m): ELU {f(I1['V407']['ELU']['Md'])} ≤ {f(I1['V407']['ELU']['MRd'])} kN·m. Volume e peso de cada marca por um só cálculo da geometria (maciços de 1,40 m e dentes): "
       + ", ".join(f"{NOME_I[k]} {f(I1[k]['icamento']['peso_kN'] / 10, 2)} t" for k in ("V407", "V406", "V405", "V404")) + "."),
     Paragraph("3. Vigas de borda rentes à face externa dos pilares de fachada (NBR 9062:2017 7.3; NBR 6118:2023 17.2.5 e 17.5)", T2),
     P(f"Em todos os vãos das linhas 1 e 9 (VB-01 a VB-08; nos vãos de canto desde 27/10, com o pilar de canto 10 cm para fora) a VB 15×60 e o consolo CP-VB ficam rentes à face externa do pilar 40×60: eixo da VB a e = {f(CF2['e_m'] * 100, 1)} cm do eixo do pilar, 2,5 cm até a placa. "
       f"O consolo continua com a carga centrada (mesma geometria, armadura e Fd = {f(CF2['Fd_kN'])} kN do C1; tirante com cobrimento lateral 3 cm na face C) e ganha marca própria. No pilar: momento adicional Mx = Σ Vd·e somado em valor absoluto a todas as combinações e torção Td = Hd·e."),
     tab([["PILAR", "FACES", "ΔMd (kN·m)", "USO ANTES", "USO COM e", "Td / TRd2 (kN·m)", ""]] +
         [[k, ", ".join(v["faces"]), f(v["dM_kNm"]), f(v["uso_antes"], 3), f(v["uso_com_excentricidade"], 3), f"{f(v['Td_kNm'], 2)} / {f(v['TRd2_kNm'], 0)}", ok(v["ok"])] for k, v in CF2["pilares"].items()],
         [20, 16, 24, 22, 22, 34, 12]),
     P(f"Terças: o 1º e o último vão de todas as terças crescem {f(CF2['e_m'] * 1000, 0)} mm (a última do lado E, que encosta no pilar de canto, termina 1 cm depois da face interna dele e apoia no ST-1FL); ST-1V com a borda rente à ponta da terça; ponta a 85 mm do eixo da VB (borda dos furos 25 mm ≥ 22 mm, NBR 8800:2024 Tab. 14), 15 mm antes da placa. "
       f"Terça Z 302 × 2,30 com os vãos novos: uso {f(CBM['terca']['governante']['uso'], 3)} (antes 0,851); parafusos do transpasse {f(CBM['terca']['parafusos_transpasse']['uso'], 3)}. "
       "O ΔMd dos consolos entra no dimensionamento dos pilares e no Mxd das cargas na fundação."),
     Paragraph("3a. Pilares de canto 10 cm para fora (decisão de 27/10, opção D)", T2),
     P("Os 4 pilares de canto 40 × 60 (linhas 1 e 9, eixos A e E) mantêm a seção e ficam com o eixo 10 cm para fora da linha: face externa no plano da face dos pilares de fachada (−0,30 / +0,30). "
       "Cálice e bloco seguem o eixo do pilar (CG01, com o momento N·e = N·0,10 caso o bloco fique na linha). Modelo global refeito com a posição nova: envoltória sem mudança relevante. "
       "CP-VB do canto rente à face externa (e = 12,5 cm do eixo do pilar). Cargas na fundação (tf): "
       + "; ".join(f"{NOME_P(k)} Nk {f((CFU[k]['G']['N'] + CFU[k]['Q']['N']) / 10)}, Nd {f(CFU[k]['ELU']['Nd_max'] / 10)}, Mxd {f(CFU[k]['ELU']['Mxd_max'] / 10)}" for k in sorted(("P1C-L1", "P2C-L1", "P1C-L9", "P2C-L9"), key=lambda k_: int(NOME_P(k_)[1:])) if True) + ". "
       "VM de borda da linha 1: ver 3c (decisão de 27/10)."),
     Paragraph("3c. VM da linha 1 alinhada à face externa e consolos com a largura da viga (decisões de 27/10)", T2),
     P(f"A VM de borda da linha 1 (30 × 75) fica alinhada à face externa dos pilares da linha 1, a mesma das placas (PF e cantos com face em −0,30): vai de −0,30 a 0,00, eixo em −0,15, nos dois níveis e em toda a linha (2,5 cm atrás das placas, sem fresta). "
       f"Lajes do vão 1–2: de −0,10 (apoio de 10 cm na VM da linha 1) a 9,60 (apoio de 10 cm na VM da linha 2) — peça de {f(LA_NOVA['L_peca'], 2)} m (antes 9,55), vão de cálculo {f(LA_NOVA['L_peca'] - 0.10, 2)} m; LP20 com 9 Ø12,7 e capa 5: uso máximo {f(LA['uso_max'], 3)} (antes 0,852), flecha final {f(LA['flechas_mm']['final'])} mm ≤ L/250 = {f(LA['flechas_mm']['lim_final_L250'])} mm — passa. "
       f"LA-03/LA-04 (escada): {f(LA['LA03']['L_peca'], 2)} m, {LA['LA03']['arranjo']}, uso {f(LA['LA03']['uso_max'], 3)}. Recorte das LA-01R junto aos pilares de 40 × 60 da linha 1: 45 × 42,5 (linha 2: 45 × 27,5); verificação da ponta recortada sem mudança (mesma largura cortada). "
       f"VM com o vão novo das lajes: VM-01 e VM-02 com {VM['VM-01']['n_cord']} e {VM['VM-02']['n_cord']} cordoalhas (sem mudança), VM-03 {VM['VM-03']['n_cord']} (antes 6), Vd {f(VM['VM-02']['cortante']['Vd'])} kN. "
       f"Pilares: o apoio das VM da linha 1 fica excêntrico — PF da linha 1 com 4 CP-MEZ a e = 15 cm (faces B e D, 2 níveis): ΔMd = {f(CF2['mez']['PF-01']['dM_kNm'])} kN·m; cantos com 2 CP-MEZ a e = 5 cm: ΔMd = {f(CF2['mez']['PL-03']['dM_kNm'])} kN·m — somados ao Mx de todas as combinações (com o ΔM das VB). "
       f"Armadura nova dos PF da linha 1 (2ª ordem global + método geral + manuseio): {', '.join(f'{k} {DPR[k]['proposto']['n']} Ø{DPR[k]['proposto']['d']:g} (uso {f(DPR[k]['proposto']['uso_secao'], 3)})' for k in ('PF-01', 'PF-02', 'PF-03'))}; cantos sem mudança. "
       f"Fundação (CG01, tf·m): Mxd dos PF da linha 1 +{f(CF2['mez']['PF-01']['dM_kNm'] / 10)} e dos cantos da linha 1 +{f(CF2['mez']['PL-03']['dM_kNm'] / 10)}. 2º estágio e capa acompanham a VM."),
     P("Consolo com a largura da viga que ele apoia (NBR 9062:2017 7.3; aparelho a ≥ 1,5c = 4,5 cm da face lateral, 6.2.3): "
       + "; ".join(f"{k} {f(CO[k]['b_m'] * 100, 0)} × {f(CO[k]['proj_m'] * 100, 0)} × {f(CO[k]['h_total_m'] * 100, 1)}" + (f"/{f(CO[k]['h_consolo_m'] * 100, 1)}" if CO[k]['h_consolo_m'] != CO[k]['h_total_m'] else "") + f", {CO[k]['tirante']}, τwd {f(CO[k]['tau_wd_MPa'], 2)} ≤ {f(CO[k]['tau_wu_MPa'], 2)} MPa" for k in ("CP-MEZ", "CP-VB", "CP-I120", "CT-I120"))
       + ". CP-MEZ 40 → 30: reto (27,9) a biela passa de 6,48 MPa (7,02) e o tirante não cabe → mísula de fundo inclinado como o CP-I120 (40 junto ao pilar, 27,9 na ponta, fundo alinhado à VM). CP-I120 50 → 40 e CT-I120 50 → 40 passam com a armadura de antes. CP-VB continua 15; o NEO-6 passa a 100 × 60 (borda 4,5 cm; σ e estabilidade verificadas)."),
     Paragraph("3b. PG-02 e PG-04 25 × 40 (decisões de 27/10)", T2),
     P(f"Seção 25 × 40 com 40 ao longo da parede da linha 4; eixo em x = {f(PJ['pilares']['PG-02']['x_m'], 3)} e {f(PJ['pilares']['PG-04']['x_m'], 3)} m para 5,00 m livres face a face "
       f"({f(PJ['vao_livre_portoes_m']['PG-01–PG-02'], 2)} e {f(PJ['vao_livre_portoes_m']['PG-04–PG-03'], 2)} m), conferidos no arquitetônico R01 (plantas do pavilhão, de locação e de vergas: 5,00 m face a face nos dois portões). "
       f"Na direção perpendicular à linha 4 o eixo fica {f(PJ['pilares']['PG-02']['dy_linha4_m'] * 100, 1)} cm fora da linha, para o lado das placas (y = {f(PJ['pilares']['PG-02']['y_m'], 3)}): a face fica no plano dos vizinhos 40 × 40, sem fresta até as placas — mesmo princípio dos cantos. "
       f"NEO-7 pela distância à borda a0 ≥ 1,5c = {f(PJ['neoprene']['PG-02']['a0_min_cm'], 1)} cm (NBR 9062:2017 7.2): {PJ['neoprene']['PG-02']['dim_mm']} nos PG-02/PG-04 e {PJ['neoprene']['PG-01']['dim_mm']} nos PG-01/PG-03, centrado na cabeça; "
       f"na mesa da TS-01A a borda fica a {f(PJ['neoprene']['PG-02']['borda_mesa_TS_cm'], 1)} cm. A reação da TS-01A foi tomada no eixo da linha 4 (e = 7,5 cm) a favor da segurança no pilar e na fundação. "
       f"Apoio da TS-01A: Nd = {f(PJ['pilares']['PG-02']['Nd_tf'])} tf, λ = {f(PJ['pilares']['PG-02']['lambda_'])} / {f(PJ['pilares']['PG-04']['lambda_'])} ≤ 90; neoprene NEO-7 {PJ['neoprene']['PG-02']['dim_mm']} (σ {f(PJ['neoprene']['PG-02']['sigma_MPa'], 2)} MPa). "
       f"Armadura (2ª ordem global + método geral + manuseio): PG-02 {DPR['PG-02']['proposto']['n']} Ø16, PG-04 {DPR['PG-04']['proposto']['n']} Ø16. "
       "CE-1 380 × 330 cabe na face de 40; sem calço CS-1D (face no plano dos consoles). PV-1 sobre o portão com CL-V L 102 nos dois apoios. "
       f"Cargas na fundação (tf): PG-02 Nk {f((CFU['P10a']['G']['N'] + CFU['P10a']['Q']['N']) / 10)}, Nd {f(CFU['P10a']['ELU']['Nd_max'] / 10)}; PG-04 Nk {f((CFU['P10b']['G']['N'] + CFU['P10b']['Q']['N']) / 10)}, Nd {f(CFU['P10b']['ELU']['Nd_max'] / 10)}."),
     Paragraph("4. Densidade e pesos", T2),
     P("Peso = volume × 25 kN/m³; t = kN / 10 (2,50 t/m³) em todo o jogo: IC01, folhas das peças, PR01, quantitativos e montagem (antes a IC01 e a TS-01 usavam 9,81). A IC01 lê os pesos da mesma lista de peças do PR01; σ no furo FI-1 em MPa; coluna βa = 1,3 em todas as tabelas."),
     Paragraph("5. Barras das peças e pinos de ligação", T2),
     P("Armadura passiva longitudinal das vigas com Ø ≥ 12,5 (TS-01: N5 e N9 passam de Ø10 para Ø12,5; As do topo 7,36 cm²) e nenhuma barra de armadura acima de Ø20. "
       "Exceções registradas (pinos de ligação, não armadura da peça; mantidos pelo responsável técnico em 27/10): PN-2 Ø25 CA-50 (L = 900, 350 no consolo) da I120 nos consolos CP-I120 (P24, P18, P20, P22, P23 — folhas PF04, PC01, PC02, PC03) e PN-3 Ø25 CA-50 (L = 600, 300 no pilar) do assento das TS-01 no recuo dos pilares laterais (2 por pilar, 24 un. — folhas PL01, PL05, PL09 a PL12 e corte CT01)."),
     Paragraph("6. Pendências", T2),
     P("(a) Extrusora: 2 cordoalhas na nervura de borda da LP20. (b) VM de borda da linha 1: decidida em 27/10 (3c). (c) Locação dos PG-02/PG-04 decidida em 27/10 (3b). Pinos PN-2 e PN-3 Ø25 mantidos (27/10). "
       "(d) Local da obra (V0, S2, S3 da NBR 6123:2023), ART e TRRF. (e) Zip com DXF e IFC só depois da aprovação deste pacote.")]
E.insert(2, tab([["PARTE", "CONTEÚDO", "SITUAÇÃO"],
                 ["MC12 (esta parte)", "laje LP20 9 Ø12,7; I120 N3 Ø20; VB rente; cantos 10 cm para fora; PG-02/PG-04 25 × 40; pesos; bitolas e pinos", "vigente; prevalece sobre as anteriores"],
                 ["MC10 (anexada)", "revisão do Nathan sobre a rev09: consolo CT-I120, escadas, içamento das placas, cotas", "vigente no que a MC12 não alterou"],
                 ["MC09 (anexada)", "pisos +3,90/+7,30, VM retangulares 30 × 75, laje alveolar, cobertura da linha 2, escada metálica, pilares da escada, fundação", "vigente no que a MC10/MC12 não alteraram"]], [32, 100, 44]))
doc.build(E)
# rev12 (revisão rev12, item 11): memória vigente num documento só — MC12 + MC10 + MC09
import pymupdf as _fz
_ENT = Path("/home/claude/letsara/entregas")
_out = _fz.open(str(SAI))
for _a in ("ND-LET-MC10-REV10-rev10.pdf", "ND-LET-MC09-REV09-rev09.pdf"):
    if (_ENT / _a).exists():
        _out.insert_pdf(_fz.open(str(_ENT / _a)))
_tmp = SAI.with_suffix(".tmp.pdf")
_out.save(str(_tmp), garbage=3, deflate=True); _out.close(); _tmp.replace(SAI)
print("ok", SAI)
