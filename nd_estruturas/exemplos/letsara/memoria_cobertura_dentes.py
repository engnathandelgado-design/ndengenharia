"""Memória de cálculo (PDF) — cobertura metálica, ligações e dentes Gerber da Letsara. Lê os JSON dos cálculos."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from nd_estruturas.metalica_fria import PerfilUe

AQ = Path(__file__).parent
CB = json.loads((AQ / "cobertura_metalica.json").read_text(encoding="utf-8"))
DT = json.loads((AQ / "dentes.json").read_text(encoding="utf-8"))
LG = json.loads((AQ / "ligacoes.json").read_text(encoding="utf-8"))
f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")

for nome, arq in (("DV", "DejaVuSans.ttf"), ("DVB", "DejaVuSans-Bold.ttf")):
    for base in ("/usr/share/fonts/truetype/dejavu/", "/usr/share/fonts/dejavu/"):
        if Path(base + arq).exists():
            pdfmetrics.registerFont(TTFont(nome, base + arq))
            break
ss = getSampleStyleSheet()
N = ParagraphStyle("n", parent=ss["Normal"], fontName="DV", fontSize=9, leading=12)
T1 = ParagraphStyle("t1", parent=N, fontName="DVB", fontSize=13, leading=17, spaceBefore=8, spaceAfter=4)
T2 = ParagraphStyle("t2", parent=N, fontName="DVB", fontSize=10.5, leading=14, spaceBefore=6, spaceAfter=3)
P = lambda t: Paragraph(t, N)


def tab(linhas, larg, cab=True):
    t = Table([[P(str(c)) for c in l] for l in linhas], colWidths=[w * mm for w in larg])
    st = [("GRID", (0, 0), (-1, -1), 0.3, colors.grey), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]
    if cab:
        st.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8e8")))
    t.setStyle(TableStyle(st))
    return t


# figura: curva de assinatura do Ue
u = PerfilUe(300, 85, 25, 3.0)
fig, ax = plt.subplots(figsize=(7.5, 3.4), dpi=150)
for carga, cor, rot in (("M", "#c0392b", "flexão (Mcr/My)"), ("N", "#2c3e50", "compressão (Ncr/Ny)")):
    Ls, fs = u.assinatura(carga)
    ax.semilogx(Ls, fs, color=cor, label=rot)
ax.set_ylim(0, 3)
ax.set_xlabel("meio comprimento de onda (mm)")
ax.set_ylabel("fator de carga crítica")
ax.grid(alpha=0.3, which="both")
ax.legend()
ax.set_title("Ue 300×85×25×3,00 — curva de assinatura (faixas finitas)", fontsize=10)
fig.text(0.99, 0.01, "projeto da ND Engenharia", ha="right", fontsize=7, color="gray")
fig.tight_layout()
fig.savefig(AQ / "assinatura_ue300.png")
plt.close(fig)

doc = SimpleDocTemplate(str(AQ / "ND-LET-MC02-cobertura-dentes.pdf"), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                        topMargin=16 * mm, bottomMargin=16 * mm, title="Letsara — memória de cálculo: cobertura e dentes Gerber",
                        author="ND Engenharia")
E = []
E += [Paragraph("ND ENGENHARIA — MEMÓRIA DE CÁLCULO ND-LET-MC02", T1),
      P("Obra: Letsara — pavilhão com mezanino (Marque Engenharia). Assunto: terças metálicas, correntes, ligação terça × viga, "
        "mão-francesa, chapas embutidas e chumbadores, dentes Gerber das vigas e consolos que os recebem. Revisão 00 — 12/10/2026. "
        "Projeto da ND Engenharia — para aprovação."),
      Paragraph("1. Normas e critérios", T2),
      P("NBR 8681:2003 e NBR 8800:2008 (combinações, ligações, laminados); NBR 14762:2010 (perfis formados a frio, método da "
        "resistência direta, Anexo C); NBR 6123:1988 (vento); NBR 6118:2023 e NBR 9062:2017 (concreto e pré-moldados: consolos 7.3 e "
        "dentes 7.4). Complementos: PCI Design Handbook 8ª ed. seção 5.6 (extremidades rebaixadas), ACI 318-19 cap. 17 (chumbadores), "
        "AISI S100-16 D3.2.1 (forças nas correntes de perfis C). Ações: permanente da cobertura 0,25 kN/m², sobrecarga 0,25 kN/m², "
        "vento q = 0,874 kN/m² (V0 45 m/s, S2 cat. III classe C, S3 0,95), Cpe −0,8 geral e −1,4 na faixa de borda, Cpi +0,2."),
      Paragraph("2. Terças Ue 300×85×25×3,00 — ZAR 345", T2)]
pf, tr = CB["perfil"], CB["terca"]
E += [P(f"A = {pf['A_mm2']} mm²; Ix = {f(pf['Ix_cm4'])} cm⁴; W = {f(pf['W_cm3'])} cm³; peso {f(pf['peso_kNm'],3)} kN/m; centro de torção a "
        f"{f(pf['m_ct_mm'])} mm da alma. Vão máximo {f(tr['L_m'],2)} m, espaçamento 1,579 m (cálculo com 1,60 m). Correntes a L/4, L/2 e 3L/4."),
      P(f"Flambagem local e distorcional por faixas finitas (curva de assinatura). Flexão: local {pf['assinatura_M']['local']} My "
        f"(L = {pf['assinatura_M']['L_local']:.0f} mm), distorcional {pf['assinatura_M']['dist']} My (L = {pf['assinatura_M']['L_dist']:.0f} mm). "
        f"Compressão: local {pf['assinatura_N']['local']} Ny; distorcional {pf['assinatura_N']['dist']} Ny ({pf['assinatura_N']['obs']}). "
        "A parte global da curva foi conferida com o Me analítico da NBR 14762 9.8.2.2 (diferença de 1% em L = 3,24 m)."),
      Image(str(AQ / "assinatura_ue300.png"), width=165 * mm, height=75 * mm)]
lin = [["Caso", "w (kN/m)", "Md (kN·m)", "MRd (kN·m)", "Modo", "Uso"]]
for z, c in tr["casos"].items():
    lin.append([f"{z} — gravidade (mesa sup. presa à telha)", f(c["w_grav_kNm"], 2), f(c["grav"]["Msd"], 2), f(c["grav"]["MRd"], 2), c["grav"]["modo"], f(c["grav"]["uso"], 2)])
    lin.append([f"{z} — sucção (Lb = L/4)", f(c["w_suc_kNm"], 2), f(c["suc"]["Msd"], 2), f(c["suc"]["MRd"], 2), c["suc"]["modo"], f(c["suc"]["uso"], 2)])
E += [tab(lin, [58, 18, 20, 22, 30, 14]), Spacer(1, 3 * mm)]
te = CB["terca_escora"]
E += [P(f"Cortante: VRd = {tr['casos']['geral']['V']['VRd']} kN (uso {f(tr['casos']['borda']['V']['uso'],2)}). Flecha g + q = {f(tr['flecha_gq_mm'])} mm ≤ L/180 = "
        f"{f(tr['flecha_lim_mm'])} mm. Terça escora do contraventamento: Nd = {te['Nd']} kN (Nc,Rd = {te['NcRd']} kN, modo {te['modo_N']}) + "
        f"Md = {te['Md']} kN·m, amplificação {te['amplificacao']} → interação {f(te['interacao'],3)} ≤ 1. "
        "Com duas linhas de correntes (L/3) a faixa de borda (uso 1,20) e a escora (1,06) não passavam: adotadas três linhas.")]
cr = CB["correntes"]
E += [Paragraph("3. Correntes", T2),
      P(f"Força de travamento por terça (AISI S100-16 D3.2.1, perfil C): P_L = 1,5 (m/d) W + W·sen θ. Sucção: P_L = {cr['casos']['sucção']['PL_por_terca_kN']} kN; "
        f"gravidade: {cr['casos']['gravidade']['PL_por_terca_kN']} kN. Acumulada em 13 terças entre ancoragens: {f(cr['F_max_kN'],2)} kN."),
      tab([["Elemento", "Seção", "Esforço (kN)", "Resistência (kN)", "Uso"],
           ["Corrente flexível", "Ø12,5 A36, rosca M12", f(cr["F_max_kN"]), f(cr["flexivel"]["NtRd"]), f(cr["flexivel"]["uso"], 2)],
           ["Corrente rígida (1º vão junto às ancoragens)", "tubo Ø42,2×2,65 + Ø12,5", f(cr["F_max_kN"]), f(cr["rigida"]["NcRd"]), f(cr["rigida"]["uso"], 2)],
           ["Diagonal de ancoragem (até a CT-1)", f"Ø16, L = {f(cr['diagonal']['comp_m'],2)} m", f(cr["diagonal"]["Td"]), f(cr["diagonal"]["NtRd"]), f(cr["diagonal"]["uso"], 2)]],
          [52, 46, 24, 28, 16])]
c1, mf = CB["CT1"], CB["MF1"]
E += [Paragraph("4. Ligação terça × viga (CT-1) e mão-francesa", T2),
      P(f"Reação por terça: gravidade {f(c1['reacao_grav_kN'],2)} kN; sucção {f(c1['reacao_suc_kN'],2)} kN. CT-1 = {c1['perfil']}, 2 M16 8.8 na CH-T e 2 M12 8.8 por terça na alma."),
      tab([["Verificação", "Solicitação", "Resistência", "Uso"],
           ["M12 na alma de 3,00 (pressão de contato NBR 14762 10.3.2) + corte", f"{f(c1['M12_alma']['Fd'],2)} kN", f"{f(min(c1['M12_alma']['corte_Rd'], c1['M12_alma']['contato_alma_Rd']),1)} kN", f(c1["M12_alma"]["uso"], 2)],
           ["M16 tração + corte (NBR 8800 6.3.3.4)", f"T {f(c1['M16_chapa']['Td'],2)} / V {f(c1['M16_chapa']['Vd'],2)} kN", f"{f(c1['M16_chapa']['Ft_Rd'],1)} / {f(c1['M16_chapa']['Fv_Rd'],1)} kN", f(c1["M16_chapa"]["interacao"], 2)],
           ["Aba horizontal da CT-1 (alavanca)", f"{f(c1['aba']['Md_kNm'],3)} kN·m", f"{f(c1['aba']['MRd_kNm'],3)} kN·m", f(c1["aba"]["uso"], 2)],
           ["Mão-francesa L 50×5 a 45° (binário de torção no apoio)", f"{f(mf['Nd_kN'],2)} kN", f"{f(mf['NcRd'],1)} kN", f(mf["uso"], 2)]],
          [78, 34, 34, 14]),
      P(f"Mão-francesa: torção no apoio T = q·e·L/2 com e = {f(mf['e_torcao_mm'])} mm (carga no meio da mesa × centro de torção) = "
        f"{f(mf['T_apoio_kNm'],3)} kN·m, resistida pelo binário CT-1 (topo) × mão-francesa (mesa inferior): H = {f(mf['H_kN'],2)} kN.")]
ch = CB["chumbadores"]
E += [Paragraph("5. Chapas embutidas e chumbadores (ACI 318-19 cap. 17, C50 fissurado)", T2),
      tab([["Chapa", "Pinos", "Nd / Vd (kN)", "φNn / φVn (kN)", "Modo", "Interação"]] +
          [[k, v["pinos"], f"{f(v['Nu'])} / {f(v['Vu'])}", f"{f(v['phiNn'])} / {f(v['phiVn'])}", f"{v.get('modoN','-')} / {v.get('modoV','-')}", f(v["interacao"], 2)]
           for k, v in ch.items()], [18, 52, 24, 26, 22, 18]),
      P("Na CH-T2 a borda lateral da mesa fica a 50 mm dos pinos: a ruptura de borda por cortante (14 kN) não atende sozinha; "
        "2 grampos U Ø10 envolvendo os pinos funcionam como armadura de ancoragem (ACI 17.5.2.1), φ·As·fy = 99 kN.")]
E.append(PageBreak())
E += [Paragraph("6. Dentes Gerber", T2),
      P("Todas as pontas de viga que apoiam em consolo receberam dente: TS-01 (no pilar lateral, no pilar central e na I110), "
        "I110 (no pilar central) e vigas do mezanino. Dimensionamento pela NBR 9062:2017 (consolo curto/muito curto + suspensão "
        "≥ Vd/fyd) e pelo PCI 5.6 (flexão e tração no dente, cisalhamento direto, tração diagonal no canto reentrante e no dente), "
        "adotando a maior armadura. I110: dente de 660 mm (60% da altura) e 10 das 24 cordoalhas isoladas por 2 m nas pontas; "
        "com as 24 aderentes junto ao dente a protensão fissurava o topo da extremidade e o MEF não sustentava a carga. "
        "Assento da I110 no consolo do pilar central: fundo da I110 + 440 mm = 8,84 m.")]
lin = [["Viga", "Vd / Hd (kN)", "Dente h × l (mm)", "Tirante", "Suspensão", "Costura", "a/d"]]
for k in ("TS-01", "I110", "MEZ-I90"):
    v = DT[k]; a = v["calculo"]["adotado"]
    lin.append([k, f"{v['Vd']:.0f} / {v['Hd']:.0f}", f"{v['geometria']['hd']} × {v['geometria']['ln']}", a["tirante"], a["suspensao"].split(" a até")[0],
                a["costura"].split(" nos")[0], f(v["calculo"]["NBR"]["a_d"], 2)])
E += [tab(lin, [18, 20, 22, 26, 38, 34, 12])]
E += [P("Consolos que recebem os dentes (NBR 9062 7.3):"),
      tab([["Consolo", "Tipo", "a/d", "Tirante", "τwd / τwu (MPa)"]] +
          [[c["nome"], c["tipo"], f(c["a_d"], 2), c["tirante"], f"{f(c['tau_wd'],2)} / {f(c['tau_lim'],2)}"] for c in DT["consolos"]],
          [70, 24, 14, 32, 30])]
E += [Paragraph("7. Verificação dos dentes por MEF não linear", T2),
      P("Modelo 2D em estado plano de tensões (OpenSeesPy): concreto com dano à tração e à compressão (ASDConcrete3D, IMPL-EX), "
        "armaduras e cordoalhas como barras aderentes (cordoalhas cortadas na face do dente, com deformação inicial crescendo no "
        "comprimento de transferência de 760 mm), aparelho de apoio como placa de aço sobre um único pino. Resistências de cálculo "
        "(fcd, fctd, fyd). Trecho de 3 m com carga no topo; a força no dente é lida na reação do apoio. Validação: viga retangular "
        "400×600 com 3 Ø20 — o MEF deu 226 kN·m contra 213,7 kN·m da NBR 6118 (+6%); por isso exige-se Vu ≥ 1,06 Vd. "
        "A etapa de protensão é levada ao equilíbrio (resíduo < 1 N) antes da carga; a reação residual é descontada. "
        "Critério de ruptura: primeiro entre 10‰ no aço, 3,5‰ no concreto (fora das placas de apoio e de carga) ou pico da curva.")]
lin = [["Viga", "Vd (kN)", "Vu MEF (kN)", "Vu/Vd", "Critério de parada", "Atende"]]
for k in ("TS-01", "I110", "MEZ-I90"):
    m = DT[k].get("mef")
    if m:
        crit = (m.get("limite") or {}).get("criterio", "pico da curva (perda de convergência)")
        if DT[k].get("nota_mef"):
            crit = "limite inferior: análise parou sem atingir os limites de deformação"
        lin.append([k, f"{DT[k]['Vd']:.0f}", f(m["Vu_kN"]), f(m["FS"], 2), crit, "sim" if m["ok"] else "NÃO"])
E += [tab(lin, [20, 18, 24, 16, 60, 16])]
for k in ("TS-01", "I110", "MEZ-I90"):
    png = AQ / f"mef_dente_{k}.png"
    if png.exists() and DT[k].get("mef"):
        E += [Spacer(1, 2 * mm), Image(str(png), width=170 * mm, height=115 * mm)]
E += [Paragraph("8. Compatibilidade das ligações no modelo 3D", T2),
      P(f"Erros: {LG['erros']}. Comprimento da TS-01 entre pontas {f(LG['L_TS'],3)} m, terças a cada {f(LG['passo_tercas'],3)} m. "
        f"Pinos × TB-1 nos 28 apoios: desvio máximo {max(a['dist_mm'] for a in LG['apoios']):.1f} mm; folgas ponta × face e consolo × dente "
        f"≥ {min(min(a['folga_ponta_mm'], a['folga_consolo_mm']) for a in LG['apoios'])} mm. Tirantes: folga à terça do nó "
        f"{LG['contraventamento']['folga_min_terca_mm']} mm e entre diagonais {f(LG['contraventamento']['folga_cruzamento_mm'],1)} mm. "
        f"Topo da I110 a {LG['berco_I110'][0]['topo_I110']} m, {LG['berco_I110'][0]['folga_topo_I110_tercas_mm']} mm abaixo das terças."),
      Paragraph("9. Premissas a confirmar", T2),
      P("Cpe −1,4 na faixa de borda (conferir com a geometria final); força horizontal de 28 kN na TS-01 vinda do modelo global; "
        "linha inferior das cordoalhas a 75 mm do fundo da fôrma; altura da platibanda no lado alto (assento da TS-01 no P2 a 9,71 m).")]
doc.build(E)
print("ok")
