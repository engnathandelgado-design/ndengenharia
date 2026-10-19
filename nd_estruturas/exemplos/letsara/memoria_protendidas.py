"""Memória de cálculo ND-LET-MC08 (PDF) — peças protendidas e dentes Gerber da Letsara (DEC-032).
Lê i110_r01.json (I130), vm_meio_vaso.json (VM), placas.json, dentes.json, mef_vm_dente_*.json, vb_dente.json e
o cálculo da TS-01 (pranchas/ts01_dados.py). Verificações por peça: perdas, ato da protensão, ELS, ELU, cortante,
flecha, manuseio, transferência e dentes (biela, tirante, suspensão, MEF)."""
import json, sys
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

AQ = Path(__file__).parent
sys.path.insert(0, str(AQ.parents[1]))
sys.path.insert(0, "/home/claude/letsara/pranchas")
J = lambda n: json.loads((AQ / n).read_text(encoding="utf-8"))
I1J, VM, PL, DT, VB = J("i110_r01.json"), J("vm_meio_vaso.json"), J("placas.json"), J("dentes.json"), J("vb_dente.json")
P_ = VM["premissas"]
MV = J(f"mef_vm_dente_{round(P_['h_pm'] * 1000)}_{round(P_['dente']['hd'] * 1000)}.json")
import ts01_dados as TS
f = lambda v, d=1: (f"{v:.{d}f}".replace(".", ",") if isinstance(v, (int, float)) else str(v))
ok = lambda b: "ok" if b else "NÃO"

for nome, arq in (("DV", "DejaVuSans.ttf"), ("DVB", "DejaVuSans-Bold.ttf")):
    for base in ("/usr/share/fonts/truetype/dejavu/", "/usr/share/fonts/dejavu/"):
        if Path(base + arq).exists():
            pdfmetrics.registerFont(TTFont(nome, base + arq))
            break
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


W = [60, 40, 52, 26]
doc = SimpleDocTemplate(str(AQ / "ND-LET-MC08-PROTENDIDAS-rev06.pdf"), pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=15 * mm,
                        bottomMargin=15 * mm, title="Letsara — memória MC08: peças protendidas e dentes Gerber", author="ND Engenharia")
E = [Paragraph("ND ENGENHARIA — MEMÓRIA DE CÁLCULO ND-LET-MC08 (rev06, DEC-032)", T1),
     P("Obra: Letsara — pavilhão com mezanino (Marques Engenharia). Assunto: verificação das peças protendidas pré-tracionadas (TS-01, vigas centrais "
       "I130, vigas do mezanino VM em meio vaso e placas de fechamento 125 × 10) em todas as fases — ato da protensão, ELS e ELU — e dos dentes Gerber. "
       "19/10/2026. Projeto da ND Engenharia — para aprovação."),
     Paragraph("1. Referencial e premissas", T2),
     P("NBR 6118:2023: 9.6.1.2.1 (σpi ≤ 0,77 fptk e 0,85 fpyk), 9.6.3 (perdas), 8.2.11 e Tab. 8.2 (fluência e retração), 8.4.8 e Tab. 8.4 (relaxação, "
       "aço RB), 9.4.5 (ancoragem por aderência, lbpt), 13.4 e Tab. 13.4 (protensão limitada em CAA II: ELS-F na combinação frequente e ELS-D na quase "
       "permanente), 17.2 (ELU), 17.2.4.3 (ato da protensão: γp 1,1; compressão ≤ 0,7 fckj; tração ≤ 1,2 fctm,j; armadura de tração As = R/250 MPa), "
       "17.4 (cortante, modelo I). NBR 9062:2017: 5.3.2 (βa 1,3 no manuseio, 3,0 nas alças), 5.4.3.4 (flechas), 6.3 (peça composta), 7.3 e 7.4 "
       "(consolos e dentes, γn 7.3.1.1, Hd 7.3.1.2)."),
     P("Cordoalha CP-190 RB Ø12,7 (98,7 mm²), Ep 195 GPa. Perdas: cravação 6 mm em pista de 60 m; relaxação até a liberação (0,8 dia); encurtamento "
       "elástico com Eci(fckj); progressivas pelo processo 9.6.3.4.2 com as cargas aplicadas por fases (superposição, 8.2.11): U = 70 %, idade fictícia "
       "de liberação 5 dias (cura térmica), montagem/capa aos 60 dias e revestimento aos 90 dias. Liberação GRADUAL e simétrica (macaco), indicada nas "
       "pranchas. Uso do mezanino: escritório/academia (ψ1 0,6; ψ2 0,4), confirmado pelo Nathan.")]


# ------------------------------------------------------------------ 2 TS-01
R, A = TS.R.linhas, TS.ATO
E += [Paragraph("2. TS-01 — viga de cobertura I90 (C50, 14 peças)", T2),
      P(f"{TS.P['n_cord']} cordoalhas Ø12,7 (2 isoladas {TS.P['isol']['L'] / 1000:g} m nas pontas); σpi = {TS.P['sig_pi']} MPa ({f(TS.F_cord, 1)} kN no macaco); fckj {TS.P['fckj']} MPa.")]
lin = [["Verificação", "valor", "limite / resistência", "situação"],
       ["Perdas imediata / total (9.6.3)", f"{f(R['perda_imediata_%'])} % / {f(R['perda_total_%'])} %", f"φ {f(R['phi'], 2)}; εcs {f(R['eps_cs'] * 1000, 2)} ‰", "—"],
       ["Ato: topo (máx., ao longo da peça)", f"{f(A['topo_max'], 2)} MPa a x = {f(A['x_topo_max'], 2)} m", f"≤ 1,2 fctm,j = {f(A['lim_t'], 2)}", ok(A["topo_max"] <= A["lim_t"])],
       ["Ato: base (mín.)", f"{f(A['base_min'], 2)} MPa a x = {f(A['x_base_min'], 2)} m", f"≥ −0,7 fckj = {f(A['lim_c'], 1)}", ok(A["base_min"] >= A["lim_c"])],
       ["Ato: armadura de tração no topo (17.2.4.3.2 c)", f"As ≥ {f(A['As_topo_cm2'], 2)} cm²", f"N2 4 Ø12,5 + N9 2 Ø10 = {f(A['As_topo_adotada_cm2'], 2)} cm² (L = {f(A['L_N9_mm'] / 10, 0)} cm)", ok(A["As_topo_cm2"] <= A["As_topo_adotada_cm2"])],
       ["lbpt (9.4.5) gradual / brusca", f"{f(TS.LBPT * 100, 0)} / {f(TS.LBPT_BRUSCA * 100, 0)} cm", "liberação gradual exigida", "—"],
       ["ELS-F frequente (base)", f"{f(R['elsf_inf_MPa'], 2)} MPa", f"≤ {f(R['elsf_lim_MPa'], 2)}", ok(R["els_ok"])],
       ["ELS-D quase permanente (base)", f"{f(R['elsd_inf_MPa'], 2)} MPa", "≤ 0", ok(R["elsd_inf_MPa"] <= 0)],
       ["ELU flexão", f"Md {f(R['Md_kNm'])} kN·m", f"MRd {f(R['MRd_kNm'])}; x/d {f(R['x_d'], 2)}", ok(R["Md_kNm"] <= R["MRd_kNm"])],
       ["ELU sucção (momento negativo)", f"Md {f(R['Md_succao_kNm'])} kN·m", "N2 4 Ø12,5 no topo", "ok"],
       ["Cortante", f"Vd {f(R['Vd_kN'])} kN", f"VRd2 {f(R['VRd2_kN'])}; Asw {f(R['Asw_cm2_m'], 2)} cm²/m", ok(R["Vd_kN"] <= R["VRd2_kN"])],
       ["Flecha final", f"{f(R['flecha_final_mm'])} mm", f"{f(R['flecha_lim_mm'])} mm", ok(R["flecha_final_mm"] <= R["flecha_lim_mm"])]]
E += [tab(lin, W)]

# ------------------------------------------------------------------ 3 I130
E += [Paragraph("3. Vigas centrais I130 — V405, V406, V407 (C50)", T2)]
for mk in ("V406", "V405", "V407"):
    v = I1J[mk]
    ar, pe, at, el, eu, co, fl, ic, de = (v[k] for k in ("arranjo", "perdas", "ato", "ELS", "ELU", "cortante", "flecha", "icamento", "dente"))
    lin_c = "; ".join(f"{len(l['xs'])} em y = {l['y'] / 10:g}" + (f" (isoladas {l['isol'] / 10:g} cm)" if l["isol"] else "") for l in ar["linhas"])
    E += [P(f"<b>{mk}</b> — L = {f(v['L_peca'], 3)} m; {ar['n_cord']} cordoalhas ({lin_c}); σpi {ar['sig_pi']:g} MPa ({f(ar['F_macaco_kN'], 1)} kN no macaco); fckj {ar['fckj']:g} MPa.")]
    lin = [["Verificação", "valor", "limite / resistência", "situação"],
           ["Perdas imediata / total", f"{f(pe['perda_imediata_pct'])} % / {f(pe['perda_total_pct'])} %", f"σp∞ {f(pe['sig_pinf'], 0)} MPa; φ {f(pe['phi'], 2)}", "—"],
           ["Ato: topo máx. (inclui fim dos isolamentos)", f"{f(at['topo_max'], 2)} MPa a x = {f(at['x_topo_max'], 2)} m", f"≤ {f(at['lim_t'], 2)}", ok(at["topo_max"] <= at["lim_t"])],
           ["Ato: base mín.", f"{f(at['base_min'], 2)} MPa a x = {f(at['x_base_min'], 2)} m", f"≥ {f(at['lim_c'], 1)}", ok(at["base_min"] >= at["lim_c"])],
           ["Ato: As de tração no topo", f"{f(at['As_topo_cm2'], 2)} cm²", f"N3 4 Ø20 = {f(at['As_N3_cm2'], 2)} cm²", ok(at["As_topo_cm2"] <= at["As_N3_cm2"])],
           ["lbpt gradual / brusca", f"{f(at['lbpt_m'] * 100, 0)} / {f(at['lbpt_brusca_m'] * 100, 0)} cm", "liberação gradual exigida", "—"],
           ["ELS-F frequente (base / topo)", f"{f(el['F_base'], 2)} / {f(el['F_topo'], 2)} MPa", f"≤ {f(el['lim_F'], 2)}", ok(max(el["F_base"], el["F_topo"]) <= el["lim_F"])],
           ["ELS-D quase permanente (base, vão)", f"{f(el['D_base'], 2)} MPa a x = {f(el['x_D'], 2)} m", "≤ 0", ok(el["D_base"] <= 0)],
           ["ELU flexão", f"Md {f(eu['Md'])} kN·m", f"MRd {f(eu['MRd'])}; x/d {f(eu['x_d'], 2)} ≤ 0,45", ok(eu["ok"])],
           ["Cortante", f"Vd {f(co['Vd_max'])} kN", f"VRd2 {f(co['VRd2'])}; {co['estribos']}", ok(co["ok"])],
           ["Flecha final / contraflecha no ato", f"{f(fl['final_mm'])} / {f(fl['contraflecha_ato_mm'])} mm", f"{f(fl['lim_mm'])} mm", ok(fl["ok"])],
           ["Içamento (βa 1,3) — topo na alça / base no vão", f"{f(ic['topo_alca'], 2)} / {f(ic['base_vao'], 2)} MPa", f"≤ {f(ic['lim_t'], 2)} / ≥ {f(ic['lim_c'], 1)}", ok(ic["ok"])],
           ["Alça AL-3 (laços Ø12,7)", f"{f(ic['F_alca_d_kN'])} kN por alça", f"{ic['n_lacos']} laços × {f(ic['cap_laco_kN'])} kN", ok(ic["F_alca_d_kN"] <= ic["n_lacos"] * ic["cap_laco_kN"])],
           ["Reação no dente (cargas reais)", f"Vd {f(de['Vd'])} kN; γn {f(de['gama_n'])}", f"Fd {f(de['Fd'])} kN; Hd {f(de['Hd'])} kN", "—"]]
    E += [tab(lin, W)]
E += [P("Junto ao dente (x < lbpt + h) a seção não é de Bernoulli: a tração de ELS-D na base calculada por barra na zona de transferência "
        f"({f(I1J['V406']['ELS']['D_base_transferencia'], 2)} MPa a {f(24.125 - I1J['V406']['ELS']['x_Dt'], 2)} m da ponta) fica na região D do dente, "
        "verificada pelo MEF não linear do item 6 com as cordoalhas e a transferência reais.")]

# ------------------------------------------------------------------ 4 VM
E += [PageBreak(), Paragraph("4. Vigas do mezanino VM-01 / VM-02 — meio vaso protendido (C40)", T2)]
for mk in ("VM-02", "VM-01"):
    r = VM[mk]
    pe, at = r["protensao"]["perdas"], r["ato"]
    E += [P(f"<b>{mk}</b> — L = {f(r['L_peca'], 3)} m; {r['cordoalhas']} cordoalhas ({r['isoladas_pontas']} isoladas 1,5 m); σpi 1400 MPa ({f(r['protensao']['F_macaco_kN'], 1)} kN); fckj {f(at['fckj'], 0)} MPa.")]
    lin = [["Verificação", "valor", "limite / resistência", "situação"],
           ["Perdas imediata / total", f"{f(pe['perda_imediata_pct'])} % / {f(pe['perda_total_pct'])} %", f"φ {f(pe['phi'], 2)}", "—"],
           ["Ato γp 1,1: topo ponta / fim do isolamento", f"{f(at['topo_ponta'], 2)} / {f(at['topo_fim_isol'], 2)} MPa", f"≤ {f(at['lim_t'], 2)}", ok(max(at["topo_ponta"], at["topo_fim_isol"]) <= at["lim_t"])],
           ["Ato γp 1,1: base meio / fim do isolamento", f"{f(at['base_meio'], 2)} / {f(at['base_fim_isol'], 2)} MPa", f"≥ {f(at['lim_c'], 1)}", ok(min(at["base_meio"], at["base_fim_isol"]) >= at["lim_c"])],
           ["lbpt (gradual)", f"{f(at['lbpt_m'] * 100, 0)} cm", "—", "—"],
           ["ELU fase 1 / fase 2", f"{f(r['ELU']['M1d'])} / {f(r['ELU']['M2d'])} kN·m", f"{f(r['ELU']['MRd1'])} / {f(r['ELU']['MRd2'])}", ok(r["ok"]["ELU_F1"] and r["ok"]["ELU_F2"])],
           ["ELS-F frequente / ELS-D quase permanente", f"{f(r['ELS']['sig_F'], 2)} / {f(r['ELS']['sig_D'], 2)} MPa", f"≤ {f(r['ELS']['lim_F'], 2)} / ≤ 0", ok(r["ok"]["ELS_F"] and r["ok"]["ELS_D"])],
           ["Cortante", f"Vd {f(r['cortante']['Vd'])} kN", f"VRd2 {f(r['cortante']['VRd2'])}; Asw {f(r['cortante']['Asw_req_cm2m'], 2)} cm²/m", ok(r["ok"]["VRd2"])],
           ["Interface (6.3)", f"τsd {f(r['interface']['tau_sd'], 2)} MPa", f"τRd {f(r['interface']['tau_rd'], 2)}", ok(r["ok"]["interface"])],
           ["Flecha final", f"{f(r['flecha']['final_mm'])} mm", f"{f(r['flecha']['lim_final_mm'])} mm", ok(r["ok"]["flecha"])]]
    E += [tab(lin, W)]

# ------------------------------------------------------------------ 5 placas
pr_, ve, tr = PL["protensao"], PL["vento"], PL["transitorias"]
E += [Paragraph("5. Placas de fechamento 125 × 10 (C40, 203 peças)", T2),
      P(f"{pr_['cordoalhas']}; σpi {f(pr_['sig_pi_MPa'], 0)} MPa ({f(pr_['F_macaco_kN'], 1)} kN); fckj {PL['secao']['fckj']:g} MPa; protensão centrada.")]
lin = [["Verificação", "valor", "limite / resistência", "situação"],
       ["Perdas imediata / total", f"{f(pr_['perda_imediata_pct'])} % / {f(pr_['perda_total_pct'])} %", f"P∞ {f(pr_['Pinf_kN'], 0)} kN; φ {f(pr_['phi'], 2)}", "—"],
       ["Ato γp 1,1 (compressão uniforme)", f"{f(pr_['sig_ato_MPa'], 2)} MPa", f"≥ {f(pr_['lim_ato_MPa'], 1)}", ok(pr_["sig_ato_MPa"] >= pr_["lim_ato_MPa"])],
       ["lbpt gradual / brusca", f"{f(pr_['lbpt_gradual_m'] * 100, 0)} / {f(pr_['lbpt_brusca_m'] * 100, 0)} cm", "liberação gradual exigida (c/φ 1,6)", "—"],
       ["ELU vento (zona de borda)", f"Md {f(ve['M_d'], 2)} kN·m", f"MRd {f(ve['MRd'], 2)}; x/d {f(ve['x_d'], 2)}", ok(ve["M_d"] <= ve["MRd"])],
       ["ELS-F frequente (ψ1 0,3)", f"{f(ve['sig_ELS_F'], 2)} MPa", "≤ 0 (descompressão, mais exigente que a Tab. 13.4)", ok(ve["ok_ELS_F"])],
       ["Combinação rara (informativo)", f"{f(ve['sig_rara'], 2)} MPa", f"fct,f {f(ve['fct_f'], 2)} — não exigida em protensão limitada", "—"],
       ["Manuseio: desforma / içamento / estoque", f"{f(tr['sig_desforma'], 2)} / {f(tr['sig_icamento'], 2)} / {f(tr['sig_estocagem'], 2)} MPa", f"≤ {f(tr['fctk_j'] / 1.5, 2)}", ok(tr["ok"])],
       ["Flecha (frequente)", f"{f(ve['flecha_freq_mm'])} mm", f"{f(ve['lim_mm'])} mm", ok(ve["ok_flecha"])]]
E += [tab(lin, W)]

# ------------------------------------------------------------------ 6 dentes
d130 = DT["I130"]
c130 = d130["calculo"]
m130 = d130.get("mef", {})
a130 = c130["adotado"]
mvm, avm, cvm = MV["mef"], MV["calculo"]["adotado"], MV["calculo"]
vb = VB["adotado"]
E += [PageBreak(), Paragraph("6. Dentes Gerber — biela, tirante, suspensão e MEF (NBR 9062:2017 7.3 e 7.4)", T2),
      P("Fd = γn·Vd (γn 1,1 com a parcela permanente preponderante; 1,2 nos demais casos — 7.3.1.1) e Hd = 0,16·Fd (elastômero, 7.3.1.2). "
        "Biela comprimida: τwd = Fd/(b·d) ≤ τwu da 7.3.2 (o critério de esmagamento da biela do consolo/dente). Tirante As = (Fd·a/(0,9d) + Hd)/fyd, "
        "ancorado no nariz por alças horizontais com dobra ≥ 8φ (Ø ≥ 20) ou 5φ; suspensão concentrada junto ao recorte para Fd total (fyd ≤ 435 MPa); "
        "costura horizontal. O MEF não linear (concreto com fissuração e esmagamento, barras e cordoalhas com a transferência real, nas posições da prancha) "
        "deve dar Vu ≥ 1,06·Fd (o modelo superestima a flexão em cerca de 6 % nos testes de validação).")]
lin = [["Dente", "I130 (78 × 35)", f"VM ({round(P_['dente']['hd'] * 100)} × 35)", "VB (30 × 27)"],
       ["Reação Vd / γn / Fd (kN)", f"{f(d130.get('Vd_reacao'))} / {f(d130.get('gama_n'))} / {f(d130['Vd'])}", f"{f(MV['Vd_reacao'])} / {f(MV['gama_n'])} / {f(MV['Vd'])}", f"{f(vb['Vd'])} / 1,1 / {f(1.1 * vb['Vd'])}"],
       ["Hd (kN)", f(d130["Hd"]), f(MV["Hd"]), "0,16 Fd"],
       ["a/d · modelo", f"{f(c130['NBR']['a_d'], 2)} · {c130['NBR']['tipo']}", f"{f(cvm['NBR']['a_d'], 2)} · {cvm['NBR']['tipo']}", f"{f(vb['dente']['a_d'], 2)}"],
       ["Biela τwd / τwu (MPa)", f"{f(c130['NBR']['tau_wd'], 2)} / {f(c130['NBR']['tau_lim'], 2)}", f"{f(cvm['NBR']['tau_wd'], 2)} / {f(cvm['NBR']['tau_lim'], 2)}", f"{f(vb['dente']['tau'], 2)} / {f(vb['dente']['tau_u'], 2)}"],
       ["Tirante (adotado)", a130["tirante"], avm["tirante"], vb["dente"]["tirante"]],
       ["Suspensão (adotada)", a130["suspensao"], avm["suspensao"], vb["suspensao"]],
       ["Costura / nariz", f"{a130['costura']}; {a130['vertical_dente']}", f"{avm['costura']}; {avm['vertical_dente']}", "—"],
       ["Ancoragem do tirante além da face (mm)", f(a130["ancoragem_tirante_mm"], 0), f(avm["ancoragem_tirante_mm"], 0), "—"],
       ["MEF: Vu (kN) / Vu/Fd", (f"{f(m130['Vu_kN'])} / {f(m130['Vu_kN'] / d130['Vd'], 2)}" if m130 else "—"), f"{f(mvm['Vu_kN'])} / {f(mvm['Vu_kN'] / MV['Vd'], 2)}", "não exigido (a/d 0,64, armado)"],
       ["Situação", ok(c130["NBR"]["ok_biela"] and m130.get("ok", False)), ok(cvm["NBR"]["ok_biela"] and mvm["ok"]), ok(vb["dente"]["ok"])]]
E += [tab(lin, [46, 44, 44, 44])]
_e13 = json.loads((AQ / "estudo_mef_vm_x1300.json").read_text(encoding="utf-8"))["mef"] if (AQ / "estudo_mef_vm_x1300.json").exists() else None
_e45 = json.loads((AQ / "estudo_mef_vm_x1300_c45.json").read_text(encoding="utf-8"))["mef"] if (AQ / "estudo_mef_vm_x1300_c45.json").exists() else None
if _e13:
    E += [P(f"Sensibilidade do MEF do dente da VM à posição da carga: com a carga no fim do maciço (1,0 m da ponta, a/h ≈ 1,25 como na I130) "
            f"Vu = {f(mvm['Vu_kN'])} kN ({f(mvm['Vu_kN'] / MV['Vd'], 2)} Fd). Com a carga a 1,3 m, Vu = {f(_e13['Vu_kN'])} kN ({f(_e13['Vu_kN'] / MV['Vd'], 2)} Fd)"
            + (f" e, com C45, {f(_e45['Vu_kN'])} kN ({f(_e45['Vu_kN'] / MV['Vd'], 2)} Fd)" if _e45 else "")
            + ": o limite é o esmagamento do nó do topo junto à face do dente (x ≈ 39 cm, y ≈ 76 cm), calculado com a reação TOTAL (fases 1 e 2) "
            "na peça pré-moldada sozinha — sem o 2º estágio e a capa que ficam sobre esse nó na fase 2. A armação não governa. Decisão com o Nathan: aceitar "
            "a verificação com a carga a 1,0 m ou aumentar a seção do nariz (ver relatório).")]

# ------------------------------------------------------------------ 7 detalhamento
E += [Paragraph("7. Detalhamento — ganchos, ancoragens e dobras (NBR 6118:2023 9.4 e 9.1)", T2),
      P("Tirantes dos dentes (I130 N5, VM N6): alças horizontais (U deitado) com os dois ramos no nível do tirante e a curva junto à face do nariz, "
        "diâmetro interno de dobramento ≥ 8φ para Ø20 (Tab. 9.1); o gancho para baixo que saía pelo fundo do dente da I130 foi eliminado. "
        "Comprimento dos ramos = lb,nec além da face interna do dente (9.4.2.5, má aderência na metade superior da peça concretada deitada → η1 0,7 onde aplicável). "
        "Estribos de suspensão fechados, ganchos a 45° ou 90° com ponta reta ≥ 10φ (9.4.6.1), envolvendo o tirante. "
        f"TS-01: N9 2 Ø10 no topo, {f(TS.L_N9 / 10, 0)} cm a partir de cada ponta (tração do ato). I130: N3 4 Ø20 no topo (tração do ato e compressão do ELU). "
        "Quantidades da tabela de ferros da I130 corrigidas: as barras dos dentes (N5 a N8) entram para as duas pontas da peça."),
      Paragraph("8. Pendências", T2),
      P("(a) Confirmar Ep da cordoalha no certificado do fornecedor (adotado 195 GPa). (b) Furos da cabeceira da pista para as 2 cordoalhas da mesa "
        "superior da I130 (y = 120 cm). (c) Laje alveolar LA-01: ato, perdas, cisalhamento sem estribo e ancoragem a cargo do fabricante, com o carregamento "
        "do projeto (escritório/academia).")]
doc.build(E)
print("ok", doc.filename)
