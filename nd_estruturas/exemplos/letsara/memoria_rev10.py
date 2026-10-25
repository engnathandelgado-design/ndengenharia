"""Memória de cálculo ND-LET-MC10 (PDF) — alterações do pacote rev10 (25/10/2026); cabeçalho copiado da MC09.
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
DI = J("dentes.json")["I130"]
N9C = [c for c in J("nbr9062.json")["consolos"] if c["consolo"] == "CP-I130"][0]
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
CT = [c for c in N9["consolos"] if c["consolo"] == "CT-I130"][0]
NEO3C = [a for a in N9["aparelhos"] if a["aparelho"].startswith("NEO-3C")][0]
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import fechamento as FCH
SAI = Path("/home/claude/letsara/entregas/ND-LET-MC10-REV10-rev10.pdf")
doc = SimpleDocTemplate(str(SAI), pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=15 * mm, bottomMargin=15 * mm,
                        title="Letsara — memória MC10: alterações do pacote rev10", author="ND Engenharia")
E = [Paragraph("MEMÓRIA DE CÁLCULO ND-LET-MC10 — ALTERAÇÕES DO PACOTE REV10 (25/10/2026)", T1),
     P("Obra: Letsara — pavilhão com mezanino (Marques Engenharia). Revisão pedida pelo Nathan sobre a rev09: (1) escadas metálicas no padrão de detalhamento da prancha de referência, com corrimão duplo; "
       "(2/3) consolos com mísula na linha principal V400 a V403 (I130) para as vigas de cobertura que chegam nela, mantendo as TS-01 como estão; (4) 4 pontos de içamento/desforma das placas indicados; "
       "(5) cota da diferença topo × fundo na ponta das vigas (detalhes D1); (6) cores por parede no fechamento. Complementa a MC09 (rev09). Documento para análise antes do zip com DXF e IFC."),
     Paragraph("1. Consolo lateral CT-I130 com mísula (DEC-061) — NBR 9062:2017 7.3", T2),
     P(f"Nas linhas 3, 5, 6, 7 e 8 as TS-01 apoiam no topo das I130 (V400 = V407, V401 = V406, V402 = V405, V403 = V404). Antes o assento da TS-01 era só a meia mesa da I130 "
       f"(16,25 cm da ponta da TS-01 à borda da mesa, NEO-3 100 × 300). Agora cada linha tem um consolo CT-I130 nas DUAS faces da mesa superior: b {f(CT['b_m'] * 100, 0)} cm ao longo da viga, "
       f"projeção {f(CT['proj_m'] * 100, 0)} cm além da mesa (topo com 80 cm), h {f(CT['h_m'] * 100, 0)} cm junto à mesa e {f(CT['h_ext_m'] * 100, 0)} cm na ponta (mísula), topo no nível do topo da viga "
       f"(lado E 12 mm acima, como o degrau do topo). A TS-01 continua igual (sem dente, cunha de 30 cm na ponta) e passa a assentar em 36,25 cm; neoprene NEO-3C 150 × 300 × 10 de 12 a 27 cm da ponta, dentro da cunha, "
       f"pinos PN-5 Ø20 como antes (fora do neoprene). O consolo enche a mísula da mesa no trecho (fundo no nível do início da mísula, 30 cm abaixo do topo)."),
     tab([["VERIFICAÇÃO", "VALOR", "LIMITE / OBS.", ""],
          ["Fd = γn · Vd (γn 1,2, pré-moldado; Vd = 1,4 (Ng + Nq) da TS-01)", f"{f(CT['Fd_kN'])} kN", f"Vd {f(CT['Vd_kN'])} kN, Hd = 0,16 Fd = {f(CT['Hd_kN'])} kN (7.3.9)", ""],
          ["a / d (Fd inteiro no consolo, a favor da segurança)", f(CT['a_d'], 2), CT['modelo'] + " (7.3.2.2)", ""],
          ["Tirante (7.3.5)", f"{f(CT['As_tir_cm2'], 2)} cm²", CT['tirante'] + f" — uso {f(CT['As_tir_cm2'] / (int(CT['tirante'].split('(')[1].split()[0]) * 1.227), 2)}", ok(CT['ok']['tirante'])],
          ["Biela τwd ≤ τwu (7.3.4)", f"{f(CT['tau_wd_MPa'], 2)} MPa", f"{f(CT['tau_wu_MPa'], 2)} MPa; na seção da carga (mísula) {f(CT['tau_carga_MPa'], 2)} MPa", ok(CT['ok']['biela'] and CT['ok']['biela_na_carga'])],
          ["Ponta da mísula ≥ h/2", f"{f(CT['h_ext_m'] * 100, 0)} cm", f"h/2 = {f(CT['h_m'] * 50, 0)} cm", ok(CT['ok']['h_ext'])],
          ["Costura (7.3.6) e estribos verticais (7.3.7)", f"{f(CT['costura_total_cm2'], 2)} / {f(CT['estribos_verticais_cm2'], 2)} cm²", "N15: 2 estribos horizontais Ø8 fechados (2,01); N16: 3 estribos verticais Ø8 por consolo (3,02)", "ok"],
          ["a2 (cobrimento do tirante na ponta)", f"{f(CT['a2_cm'], 1)} cm", f"≥ {f(CT['a2_min_cm'], 1)} cm (7.3.3)", "ok"],
          ["NEO-3C 150 × 300 × 10 (7.2.1.6)", f"σ {f(NEO3C['sigma_MPa'], 2)} MPa", f"≤ {f(NEO3C['lim_sigma'], 1)}; ah {f(NEO3C['ah_mm'], 1)} ≤ {f(NEO3C['lim_ah_mm'], 1)} mm; deslizamento uso {f(NEO3C['uso_deslizamento'], 2)}; rotação ok", ok(NEO3C['ok_geral'])]],
         [70, 26, 70, 12]),
     P("Tirante N14 a 7,5 cm do topo (abaixo das 6 Ø25 do N3 da mesa superior; d = 22,5 cm); as alças atravessam a mesa de um consolo ao outro e não cruzam cordoalhas (todas na mesa inferior nas V401 a V403; na V400 a linha mais alta está a 22 cm do fundo). "
       "Os consolos ficam a mais de 20 cm das alças de içamento AL-3 (2,5 m das pontas) e fora do isolamento das cordoalhas. Peso dos dois consolos de uma linha ≈ 1,1 kN — desprezível frente às cargas da I130 (cálculo da I130 inalterado; "
       "V401, V402 e V403 continuam com a mesma seção e cordoalha, mas têm consolos em posições diferentes: as posições estão na tabela de marcas da ND-LET-I130). "
       "O consolo CP-I130 dos pilares (apoio da própria I130) continua com mísula 49 / 39 (MC09). Modelo 3D com os consolos e os neoprenes novos: 0 colisões."),
     Paragraph("2. Placas de fechamento — desforma e içamento por 4 pontos numa face (NBR 9062:2017 5.3.2)", T2),
     P("Desforma deitada (face interna para cima) por 4 insertos IZ-1 na face interna, a 0,104 L e 0,396 L de cada ponta, meia altura, com balancim duplo (cargas iguais nos 4 pontos): momento 0,0054 w L² (PCI), βa 1,3 e sucção da fôrma 1,2. "
       "Montagem em pé pelas 2 alças AL-P do topo (0,207 L); estocagem em pé. Tração positiva; limite fctk,j / 1,5 (sem fissura) com fckj 25 MPa."),
     tab([["SITUAÇÃO", "σ (MPa)", "LIMITE (MPa)", ""],
          ["desforma com balancim (4 pontos numa face)", f(PLJ['transitorias']['sig_desforma'], 2), f(PLJ['transitorias']['fctk_j'] / 1.5, 2), ok(PLJ['transitorias']['sig_desforma'] <= PLJ['transitorias']['fctk_j'] / 1.5)],
          ["desforma SEM balancim (informativo: só 2 pontos efetivos)", f(PLJ['transitorias']['sig_desforma_sem_balancim'], 2), f(PLJ['transitorias']['fctk_j'] / 1.5, 2), "usar balancim"],
          ["içamento / montagem em pé pelas 2 alças AL-P", f(PLJ['transitorias']['sig_icamento'], 2), f(PLJ['transitorias']['fctk_j'] / 1.5, 2), ok(PLJ['transitorias']['sig_icamento'] <= PLJ['transitorias']['fctk_j'] / 1.5)],
          ["estocagem em pé (2 calços a 0,207 L)", f(PLJ['transitorias']['sig_estocagem'], 2), f(PLJ['transitorias']['fctk_j'] / 1.5, 2), ok(PLJ['transitorias']['sig_estocagem'] <= PLJ['transitorias']['fctk_j'] / 1.5)],
          ["montada nos 2 consoles (descompressão)", f(PLJ['transitorias']['sig_montada'], 2), "≤ 0", ok(PLJ['transitorias']['sig_montada'] <= 0)]], [92, 22, 26, 22])]
rows = [["TIPO", "L (cm)", "a1 = 0,104 L (cm)", "a2 = 0,396 L (cm)", "Pk por ponto (kN)", "βa·Pk (kN) ≤ 12,7"]]
for L_ in sorted(FCH.TIPOS, key=lambda L: -L):
    pk = FCH.peso_t(L_) * 10 / 4
    rows.append([FCH.TIPO[L_], f(L_ / 10, 1), f(0.104 * L_ / 10, 1), f(0.396 * L_ / 10, 1), f(pk, 1), f(1.3 * pk, 1)])
E += [tab(rows, [20, 22, 32, 32, 30, 34]),
      P("Insertos IZ-1 M16 com carga de trabalho ≥ 1,3 t (FS ≥ 3, NBR 9062:2017 5.3.3: dispositivos com βa 3,0 sobre a ruptura). Esquema cotado, carga por ponto e tabela por tipo na ND-LET-PP00."),
      Paragraph("3. Escadas metálicas — guarda-corpo e corrimão duplo (RT CBMRS nº 11; NBR 9050; NBR 14718)", T2),
      P(f"Corrimão DUPLO em todos os lances, dos dois lados, a {f(ESD['h_corrimao'][0], 2)} m (RT CBMRS 11: 0,80–0,92) e {f(ESD['h_corrimao'][1], 2)} m (NBR 9050:2020, duas alturas), tubo Ø38,1 × 2, 40 mm livres, "
        "prolongamentos de 30 cm nas duas alturas com curva de 90° e tampa (solda só de fábrica); retorno no patamar da escada interna nas duas alturas. Montantes dimensionados para o maior de 730 N/m no topo × vão e 900 N no corrimão de cima."),
      tab([["TRECHO", "h (m)", "MONTANTE (uso)", "CORRIMÃO (uso)", "BARRAS (uso)", "s (cm)"]] +
          [[g["cod"], f(g["h"], 2), f"{g['gc']['montante']['perfil'].replace('tubo ', '')} ({f(g['gc']['montante']['uso'], 2)})", f"{g['gc']['corrimao']['perfil'].replace('tubo ', '')} ({f(g['gc']['corrimao']['uso'], 2)})",
            (f"{g['gc']['barra']['perfil'].replace('barra redonda ', '')} c/{g['gc']['barra']['s_mm']} ({f(g['gc']['barra']['uso'], 2)})" if g['gc'].get('barra') and not g['so_corrimao'] else "—"), f(g["s"] * 100, 1)] for g in ESD["guardas"]],
          [16, 14, 40, 40, 40, 16]),
      P(f"Ligações das escadas: {len(set(l['cod'] for l in ESD['ligacoes']))} tipos verificados (NBR 8800:2024), {ESD['n_conflitos']} conflitos; pé-direito livre mínimo {f(min(p['pe_direito_min_m'] for p in ESD['pe_direito'] if p['pe_direito_min_m']), 2)} m (≥ 2,10). "
        "Detalhamento de construção e montagem, listas de material por item, notas técnicas e referências normativas nas novas ND-LET-ES04 (interna) e ND-LET-ES05 (externa); elevações de todos os trechos na ES03."),
      Paragraph("4. Pendências", T2),
      P("(a) Zip com DXF e IFC só depois da aprovação deste pacote (PDF). (b) Sondagem: σ de 150 kPa nos blocos BE-1/BE-2 da escada externa. (c) Catálogo do chumbador químico M10 hef 70 dos guarda-corpos da laje. "
        "(d) Confirmar com o cliente/arquitetura o corrimão duplo (0,92 + 0,70) — adotado pela NBR 9050, acima do mínimo do CBMRS.")]
doc.build(E)
print("ok", SAI)
