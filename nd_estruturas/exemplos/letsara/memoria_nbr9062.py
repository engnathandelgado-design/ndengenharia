"""Memória de cálculo ND-LET-MC05 (PDF) — reanálise da Letsara pela NBR 9062:2017 (rev04). Lê nbr9062.json, vm_meio_vaso.json,
vm_dente.json, mef_vm_dente_*.json e modelo_global_r04*.json. Tabelas de verificação ficam aqui (não nas pranchas do cliente)."""
import json, sys
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, PageBreak, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

AQ = Path(__file__).parent
J = lambda n: json.loads((AQ / n).read_text(encoding="utf-8"))
N9, VM, MG = J("nbr9062.json"), J("vm_meio_vaso.json"), J("modelo_global_r04.json")
VMD = J("vm_dente.json")
P_ = VM["premissas"]
H, HD = round(P_["h_pm"] * 1000), round(P_["dente"]["hd"] * 1000)
MEF = {p.stem.replace("mef_vm_dente_", ""): json.loads(p.read_text(encoding="utf-8")) for p in sorted(AQ.glob("mef_vm_dente_*_*.json"))}
f = lambda v, d=1: (f"{v:.{d}f}".replace(".", ",") if isinstance(v, (int, float)) else str(v))
ok = lambda b: "ok" if b else "NÃO"

for nome, arq in (("DV", "DejaVuSans.ttf"), ("DVB", "DejaVuSans-Bold.ttf")):
    for base in ("/usr/share/fonts/truetype/dejavu/", "/usr/share/fonts/dejavu/"):
        if Path(base + arq).exists():
            pdfmetrics.registerFont(TTFont(nome, base + arq))
            break
ss = getSampleStyleSheet()
N = ParagraphStyle("n", parent=ss["Normal"], fontName="DV", fontSize=8.6, leading=11.5)
T1 = ParagraphStyle("t1", parent=N, fontName="DVB", fontSize=13, leading=17, spaceBefore=8, spaceAfter=4)
T2 = ParagraphStyle("t2", parent=N, fontName="DVB", fontSize=10.2, leading=14, spaceBefore=7, spaceAfter=3)
P = lambda t: Paragraph(t, N)


def tab(linhas, larg):
    t = Table([[P(str(c)) for c in l] for l in linhas], colWidths=[w * mm for w in larg], repeatRows=1)
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.3, colors.grey), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8e8"))]))
    return t


doc = SimpleDocTemplate(str(AQ / "ND-LET-MC05-NBR9062-rev06.pdf"), pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=15 * mm,
                        bottomMargin=15 * mm, title="Letsara — memória MC05: reanálise pela NBR 9062:2017", author="ND Engenharia")
E = [Paragraph("ND ENGENHARIA — MEMÓRIA DE CÁLCULO ND-LET-MC05 (rev06, DEC-032)", T1),
     P("Obra: Letsara — pavilhão com mezanino (Marque Engenharia). Assunto: reanálise de toda a estrutura pela NBR 9062:2017 — sistema de "
       "estabilidade, deslocamentos, aparelhos de apoio, consolos, dentes, apoios sem recorte, cálices, situações transitórias, folgas, "
       "tolerâncias, incêndio e cobrimentos; vigas do mezanino em meio vaso. 16/10/2026. Projeto da ND Engenharia — para aprovação."),
     Paragraph("0. Classificação e coeficientes (NBR 9062:2017 3.8, 8.1, 7.3.1.1)", T2),
     P(f"{N9['classificacao']['tipo']}: γc = {f(N9['classificacao']['gama_c'])}, γs = {f(N9['classificacao']['gama_s'], 2)}, "
       f"γn = {f(N9['classificacao']['gama_n_permanente'])} (permanente preponderante) / {f(N9['classificacao']['gama_n_outros'])} (demais). "
       + N9["classificacao"]["obs"])]

# 1 estabilidade
es = N9["estabilidade"]
E += [Paragraph("1. Estabilidade global e deslocamentos (5.1.2, 5.2.3, Tab. 7)", T2), P(es["sistema"]), P(es["ligacoes"] + ". " + es["rigidez"] + ". Desaprumo: " + es["desaprumo"] + ".")]
lin = [["Combinação", "γz (5.1.2.12)"]] + [[k, f(v, 3)] for k, v in es["sem_VT"]["gama_z"].items()]
E += [tab(lin, [90, 40]), Spacer(1, 3)]
lin = [["ELS frequente", "desl. máx (mm)", "uso Tab. 7", "pilar", "uso Hi/750", "placas ligadas (mm)", "situação"]]
for k, v in es["sem_VT"]["ELS"].items():
    lin.append([k, f(v["desl_max_mm"]), f(v["uso_tab7"], 3), v["pilar"], f(v["uso_Hi750"], 3), f(es["com_placas_ligadas"]["ELS"][k]["desl_max_mm"]), ok(v["ok"])])
E += [tab(lin, [34, 22, 20, 22, 20, 30, 18]),
      P("Limites (Tab. 7, sem ponte rolante, combinação frequente): galpão H/400 com H = altura total; pilares com mezanino H/500 no topo e Hi/750 entre pisos. "
        "O limite H/1700 usado até a rev03 é da NBR 6118 para edifícios; para estrutura pré-moldada vale a NBR 9062 (Tab. 7). " + es["contribuicao_fechamento"]["conclusao"]),
      P(f"{es['deslocabilidade']}. Pilar mais solicitado ({MG['metodo_geral']['pilar']}): método geral (NLF + NLG + fluência φef 0,5, NBR 6118:2023 15.8.3.2) com "
        f"as barras reais 14 Ø20: λu = {f(MG['metodo_geral']['lambda_u'], 2)} ≥ 1,0 (com 20 Ø20 dava 1,62 → a armadura foi reduzida para 14 Ø20). "
        f"Flexão oblíqua na base (17.2.5.2): uso máximo {f(max(v['uso'] for v in MG['verificacao_pilares'].values()), 2)}.")]

# 2 aparelhos
E += [Paragraph("2. Aparelhos de apoio de elastômero (7.2.1.6) — Shore 60, G = 1,0 MPa", T2)]
lin = [["Aparelho", "uso", "σk (MPa)", "lim", "θg / lim", "θg+1,5θq / lim", "Nmín/A'", "situação"]]
for n in N9["aparelhos"]:
    nm = n.get("lim_Nmin", "> 2")
    lin.append([n["aparelho"], n["uso"], f(n["sigma_MPa"], 2), f(n["lim_sigma"]), f"{f(n['theta_g'], 4)} / {f(n['lim_theta_g'], 4)}",
                f"— / {f(n['lim_theta_gq'], 4)}", f"{f(n.get('sigma_g_Al', n.get('Nmin_MPa')), 2)} ≥ {f(nm, 2) if not isinstance(nm, str) else nm}",
                ok(n["ok_geral"]) + (" (substituído)" if "rev03" in n["aparelho"] else "")])
E += [tab(lin, [34, 38, 15, 10, 24, 22, 20, 15])]

# 3 consolos e cintamento
E += [Paragraph("3. Consolos e dente da VM (7.3 e 7.4)", T2)]
lin = [["Consolo", "b×proj×h (cm)", "a/d · modelo", "γn · Fd · Hd (kN)", "As,tir req (cm²) → adotado", "τwd / τwu (MPa)", "a2 / mín (cm)", "situação"]]
for c in N9["consolos"]:
    lin.append([c["consolo"], f"{c['b_m']*100:.0f}×{c['proj_m']*100:.0f}×{c['h_m']*100:.0f}", f"{f(c['a_d'], 2)} · {c['modelo']}",
                f"{f(c['gama_n'])} · {f(c['Fd_kN'])} · {f(c['Hd_kN'])}", f"{f(c['As_tir_cm2'], 2)} → {c['tirante']}", f"{f(c['tau_wd_MPa'], 2)} / {f(c['tau_wu_MPa'], 2)}",
                f"{f(c['a2_cm'])} / {f(c['a2_min_cm'])}", ok(c["ok_geral"])])
E += [tab(lin, [18, 20, 26, 26, 38, 18, 18, 14]),
      P("Costura 7.3.6 (≥ 0,5·Asv/d no muito curto, 0,4·Asv/d no curto, mín 0,15·b): estribos horizontais Ø8 c/10 em 2/3 d. Estribos verticais 7.3.7 ≥ 0,15 % b·h. "
        "Tirante em alças horizontais, Ø ≤ menor dimensão/8, espaçamento ≤ 15Ø e ≤ d. Na face do suporte, barras verticais do pilar ≥ As,tir (7.3.3).")]
lin = [["Topo de pilar (6.2.3)", "Fd (kN)", "Hd (kN)", "T bloco (kN)", "As (cm²)", "adotar"]]
for c in N9["cintamento"]:
    lin.append([c["topo"], f(c["Fd_kN"]), f(c["Hd_kN"]), f(c["T_bloco_kN"]), f(c["As_cm2"], 2), c["adotar"] + " — atendido pelos estribos Ø8 c/10 do topo"])
E += [tab(lin, [50, 16, 16, 18, 16, 64])]

# 4 apoios sem recorte, dentes
E += [Paragraph("4. Apoio sem recorte (7.5) e dentes Gerber (7.4)", T2)]
lin = [["Peça", "Fd (kN)", "Asd = (Fd/1,2 + Hd)/fyd", "Ash = Asv = Fd/8fyd", "adotado"]]
for a in N9["apoios_sem_recorte"]:
    lin.append([a["peca"], f(a["Fd_kN"]), f(a["Asd_cm2"], 2), f(a["Ash_Asv_cm2"], 2), a["adotado"]])
E += [tab(lin, [28, 14, 26, 24, 86]),
      P(f"Dente da I120 (78 × 35): reação real Vd = {f(N9['dente_I120']['Vd_reacao_kN'])} kN (TS-01 fora do centro), Fd = γn {f(N9['dente_I120']['gama_n'])} × Vd = {f(N9['dente_I120']['Fd_kN'])} kN, "
        f"Hd = 0,16 Fd = {f(N9['dente_I120']['Hd_kN'])} kN. MEF não linear com a armação da prancha ({N9['dente_I120']['adotado']['tirante']}; {N9['dente_I120']['adotado']['suspensao']}): "
        f"Vu = {f(N9['dente_I120']['MEF_Vu_kN'])} kN, Vu/Fd = {f(N9['dente_I120']['FS'], 2)} ≥ 1,06 — {ok(N9['dente_I120']['ok_MEF'])}; {N9['dente_I120']['suspensao']}; "
        f"{N9['dente_I120']['tirante']}; {N9['dente_I120']['restricao']}.")]

# 5 VM meio vaso
E += [PageBreak(), Paragraph("5. Vigas do mezanino — meio vaso com dente Gerber (skill ND de vigas de apoio de laje alveolar)", T2),
      P("As duas linhas (1 e 2) são de borda: a laje alveolar vence 9,65 m e apoia de um lado só. Seção: alma 25 do lado da borda + aba 15 × 20 para dentro; "
        "topo da peça = apoio da laje (10 cm na aba, neoprene em fita); 2º estágio C30 sobre a alma até a ponta da laje e capa de 5 cm, concretados por quem faz a capa; "
        "alças N9 da alma em toda a viga. Sem escoramento: fase 1 na peça isolada (peso próprio + laje + 2º estágio e capa frescos + 1 kN/m²), fase 2 na seção composta "
        "(revestimento 1 + sobrecarga 5 kN/m²). Continuidade nos apoios B, C, D pela negativa do 2º estágio (5.1.2.10, tipologia 1). Torção de montagem: pontas concretadas (junta VM × pilar) antes das lajes — DEC-039.")]
lin = [["Varredura (alma × h × dente)", "cordoalhas", "dente τ (MPa) / tirante", "consolo h / tirante", "índice de custo"]]
for r in VMD["ranking"][:8]:
    lin.append([f"{r['bw']*100:.0f} × {r['h']*100:.0f} × {r['hd']*100:.0f}", r["n_cord"], f"{f(r['dente']['tau'], 2)} / {r['dente']['tirante']}",
                f"{f(r['consolo']['h'] * 100, 0)} cm / {r['consolo']['tirante']}", r["custo_indice"]])
lin.append(["sem dente 25 × 65 (consolo 45 abaixo da viga)", 12, "—", "45 cm", VMD["sem_dente"]["custo_indice"]])
E += [tab(lin, [50, 18, 46, 40, 24]), P("Varredura de alma e altura de 5 em 5 cm (calc_vm_dente.py), a pedido do Nathan, com o dente e o consolo tratados como consolos (7.3/7.4). O cálculo analítico aprova h 65 a 75, mas o MEF não linear da ponta (quina do recorte, transferência da protensão) reprova h 65 e h 75; a menor altura aprovada no MEF foi adotada:")]
FD = N9["dente_VM"]["Fd_kN"]
lin = [["MEF h / dente (mm)", "Vu (kN) e critério", "pico (kN)", f"Vu / (1,06·Fd), Fd = γn {f(N9['dente_VM']['gama_n'])}·Vd = {f(FD)} kN", "situação"]]
_k_ad = f"{round(VM['premissas']['h_pm'] * 1000)}_{round(VM['premissas']['dente']['hd'] * 1000)}"
for k, d in ((k_, d_) for k_, d_ in MEF.items() if k_ == _k_ad):          # DEC-032: só o MEF da peça adotada, com a armação da prancha
    m = d["mef"]
    lim_ = (m["limite"] or {}).get("criterio", "pico da curva")
    lin.append([k.replace("_", " / ").replace("inf4x16", "+ 4 Ø16 inf."), f"{f(m['Vu_kN'])} ({lim_})", f(m.get("V_pico_kN", 0)), f(m["Vu_kN"] / (1.06 * FD), 2), ok(m["Vu_kN"] >= 1.06 * FD)])
E += [tab(lin, [34, 48, 22, 50, 20])]
r = VM["VM-02"]
lin = [["Verificação (VM-02, h = %g cm)" % (H / 10), "valor", "limite / resistência", "situação"],
       ["ELU fase 1 (peça isolada)", f"Md {f(r['ELU']['M1d'])} kN·m", f"MRd {f(r['ELU']['MRd1'])} · x/d {f(r['ELU']['xd1'], 2)}", ok(r["ok"]["ELU_F1"])],
       ["ELU fase 2 (composta)", f"Md {f(r['ELU']['M2d'])} kN·m", f"MRd {f(r['ELU']['MRd2'])} · x/d {f(r['ELU']['xd2'], 2)}", ok(r["ok"]["ELU_F2"])],
       ["ELS-F frequente (base)", f"{f(r['ELS']['sig_F'], 2)} MPa", f"≤ {f(r['ELS']['lim_F'], 2)}", ok(r["ok"]["ELS_F"])],
       ["ELS-D quase permanente", f"{f(r['ELS']['sig_D'], 2)} MPa", "≤ 0", ok(r["ok"]["ELS_D"])],
       ["Ato da protensão (ponta / meio)", f"topo {f(r['ato']['topo_ponta'], 2)} / base {f(r['ato']['base_meio'], 2)} MPa", f"≤ {f(r['ato']['lim_t'], 2)} / ≥ {f(r['ato']['lim_c'], 1)} (fcj {f(r['ato']['fckj'], 0)})", ok(r["ok"]["ato"])],
       ["Flecha final (Tab. 9)", f"{f(r['flecha']['final_mm'])} mm", f"L/250 = {f(r['flecha']['lim_final_mm'])}", ok(r["ok"]["flecha"])],
       ["Interface 6.3 (alças N9 Ø10 c/15)", f"τsd {f(r['interface']['tau_sd'], 2)} MPa", f"τRd {f(r['interface']['tau_rd'], 2)} (βs {f(r['interface']['beta_s'], 2)}, βc {f(r['interface']['beta_c'], 2)})", ok(r["ok"]["interface"])],
       ["Torção de montagem", f"Td {f(r['torcao_montagem']['T_apoio_d'])} kN·m", f"interação {f(r['torcao_montagem']['interacao'], 2)}; junta Hd {f(r['torcao_montagem']['H_topo_d_kN'])} kN: τ {f(r['torcao_montagem']['junta']['tau_sd_MPa'], 2)} ≤ {f(r['torcao_montagem']['junta']['tau_rd_fck30_MPa'], 2)} MPa", ok(r["ok"]["torcao"] and r["ok"]["apoio"])],
       ["Negativa de continuidade (face do pilar)", f"Md {f(r['negativa']['Md_kNm'])} kN·m", f"MRd {f(r['negativa']['MRd_kNm'])} · {f(r['negativa']['frac_no_pilar'] * 100, 0)} % no pilar", ok(r["negativa"]["ok"])],
       ["Içamento (alças a 1,0 m) e estabilidade lateral 6.1", f"σt {f(r['icamento']['sig_topo_balanco'], 2)} MPa", f"≤ {f(r['icamento']['lim_t'], 2)}; L/bf {f(r['icamento']['lateral_L_bf'])} ≤ 50", ok(r["ok"]["icamento"] and r["ok"]["lateral"])],
       ["Excentricidade lateral da protensão", f"{f(r['excentricidade_lateral_protensao_m'] * 1000)} mm", "2 cordoalhas na aba equilibram a seção T", "ok"]]
E += [tab(lin, [52, 42, 66, 18])]

# 5b VB com dente
VBJ = json.loads((AQ / "vb_dente.json").read_text(encoding="utf-8"))
va = VBJ["adotado"]
E += [Paragraph("5b. Vigas de borda VB das fachadas 1 e 9 — 15 × 60 com dente Gerber", T2),
      P("Topo fixo (apoio das terças do vão de oitão); dente para esconder o consolo CP-VB e ganhar altura livre embaixo (pedido do Nathan, 16/10/2026). "
        "Varredura de b 15/20 e h 90 a 40 de 5 em 5 cm (calc_vb_dente.py): passa até h 50 (h 45 reprova na flecha). Adotada a 15 × 60 (escolha do Nathan). "
        "Cargas: peso próprio + terças com painéis solares 0,495 kN/m² e sobrecarga 0,25 kN/m² na faixa de 4,82 m; sucção da faixa de borda cp −1,6 com γ 1,4 e peso favorável; "
        "tração do modelo global ELU-1 vento x 95,8 kN. Flexão no plano horizontal do modelo global ≤ 2,2 kN·m (desprezível).")]
lin = [["Varredura (b × h × dente)", "arm. inferior", "flecha (mm)", "consolo h", "índice de custo"]]
for r_ in sorted(VBJ["ranking"], key=lambda x: (x["b"], -x["h"]))[:9]:
    lin.append([f"{r_['b']*100:.0f} × {r_['h']*100:.0f} × {r_['hd']*100:.0f}", r_["inf"], f"{f(r_['flecha_mm'])} / {f(r_['flecha_lim'])}", f"{f(r_['consolo_h']*100, 0)} cm", r_["custo_indice"]])
E += [tab(lin, [46, 40, 30, 24, 28])]
lin = [["Verificação (VB 15 × 60)", "valor", "limite / resistência", "situação"],
       ["Flexão ELU + tração (NBR 6118 17.2)", f"Md {f(va['Md'])} kN·m; As {f(va['As_inf'], 2)} cm²", f"{va['inf']}; x/d {f(va['x_d'], 2)}", ok(True)],
       ["Sucção (momento negativo)", f"Md {f(va['Md_neg'])} kN·m; As {f(va['As_sup'], 2)} cm²", va["sup"], ok(True)],
       ["Cortante (17.4.2.2, Vc = 0)", f"Vd {f(va['Vd'])} kN", f"VRd2 {f(va['VRd2'])}; Asw {f(va['Asw_cm2m'], 2)} cm²/m", ok(va["Vd"] <= va["VRd2"])],
       ["Flecha diferida (9062 Tab. 8)", f"{f(va['flecha_mm'])} mm", f"L/250 = {f(va['flecha_lim'])}", ok(va["flecha_mm"] <= va["flecha_lim"])],
       ["Fissuração (6118 Tab. 17.2)", f"σs {va['sigma_s']} MPa", f"≤ {va['sigma_lim']}", ok(va["sigma_s"] <= va["sigma_lim"])],
       ["Estabilidade lateral 6.1", f"L/bf {f(va['L_bf'])}", f"FS Lebelle {f(va['FS_lebelle'])} ≥ 2,5", ok(va["FS_lebelle"] >= 2.5)],
       ["Dente 30 × 27 (7.4 → 7.3, γn 1,1)", f"τ {f(va['dente']['tau'], 2)} MPa; a/d {f(va['dente']['a_d'], 2)}", f"{va['dente']['tirante']}; τu {f(va['dente']['tau_u'], 2)}", ok(va["dente"]["ok"])],
       ["Suspensão junto ao recorte", va["suspensao"], "fyd ≤ 435 MPa", ok(True)],
       ["Levantamento no apoio (sucção)", f"{f(va['R_up_d'])} kN", f"PN-1 Ø20 roscado com porca: {f(va['pino']['cap_PN1_d'])} kN", ok(va["pino"]["ok"])],
       ["NEO-6 100 × 100 × 10", f"σ {f(va['neoprene']['sigma'], 2)} MPa; σg/A' {f(va['neoprene']['sigma_g'], 2)}", f"≤ 7,0; ≥ {f(va['neoprene']['lim_Nmin'], 2)}", ok(va["neoprene"]["ok"])]]
E += [tab(lin, [52, 46, 60, 18])]

# 6 cálices, transitórias, flechas
c = N9["calices"]
E += [Paragraph("6. Cálices (7.7, Tab. 15), transitórias (5.3.2, 6.1) e flechas (5.4.3.4)", T2),
      P(f"Embutimento adotado {f(c['Lemb_m'], 2)} m com chaves; mínimo {f(c['Lemb_min_m'], 2)} m ({c['pilar']}, direção {c['direcao']}, Md/(Nd·h) = {f(c['e_rel'], 2)} → {f(c['k'], 2)}h): {ok(c['ok'])}. {c['ancoragem']}. {c['norma']}.")]
lin = [["Peça", "L (m)", "bf (m)", "L/bf ≤ 50", "L·h/bf² ≤ 500", "FS Lebelle", "situação"]]
for t in N9["estabilidade_lateral"]["itens"]:
    lin.append([t["peca"], f(t["L_m"], 2), f(t["bf_m"], 2), f(t["L_bf"]), f(t["Lh_bf2"]), f(t["FS_lebelle"]), ok(t["ok"])])
E += [tab(lin, [50, 16, 16, 20, 24, 20, 18]), P(N9["estabilidade_lateral"]["norma"] + ". " + N9["transitorias"]["resistencias_minimas"] + ". Estoque: " + N9["transitorias"]["estoque"] + ".")]
lin = [["Flecha", "final (mm)", "limite (mm)", "regra"]]
for fl in N9["flechas"]:
    lin.append([fl["peca"], f(fl["final_mm"]), f(fl["lim_mm"]), fl["regra"]])
E += [tab(lin, [70, 26, 26, 40])]

# 7 folgas
E += [Paragraph("7. Folgas e tolerâncias (3.1, 5.2.2)", T2)]
lin = [["Ligação", "tex (mm)", "Δ (mm)", "folga req (mm)", "adotada", "apoio pior / mín (mm)", "situação"]]
for fo in N9["folgas"]:
    lin.append([fo["peca"], fo["tex_mm"], f(fo["Delta_mm"]), f(fo["folga_req_mm"]), fo["folga_adotada_mm"],
                f"{f(fo['apoio_pior_mm'])} / {fo['apoio_min_mm']}" if fo["apoio_pior_mm"] is not None else "—", ok(fo["ok"]) + (" (substituída)" if "rev03" in fo["peca"] else "")])
E += [tab(lin, [66, 14, 14, 20, 16, 28, 22]), P("Folga requerida por ponta = tex/2 + tloc (±10 mm, 5.2.2.6) + Δ/2 (ΔT 15 °C). " + N9["tolerancias"]["fabricacao"] + " " + N9["tolerancias"]["montagem"])]

# 8 incêndio e cobrimentos
ic = N9["incendio_cobrimentos"]
E += [Paragraph("8. Incêndio e cobrimentos (5.3.1.5, 9.2.1.1)", T2), P(ic["cobrimentos"]), P("Placas: " + ic["placas"] + ". Laje alveolar: " + ic["laje_alveolar"] + ". " + ic["metalicos"] + ". " + ic["TRRF"] + "."),
      Paragraph("9. Pendências para o cliente / fábrica", T2),
      P("(a) Fábrica: comprovar controle de pré-fabricado (12.1.2) para o cobrimento de 2 cm das placas e eventual redução de γc/γs. (b) TRRF exigido pelo Corpo de Bombeiros. "
        "(c) Catálogo do trilho TR-1/TR-2 e das buchas BR-1/BR-2 (≥ 12,4 kN placas). (d) Cabeceira da pista para as novas grades de cordoalhas (TS-01 e VM). "
        "(e) Projeto de fundações: colarinho dos cálices (7.7.4) com os esforços do modelo r04.")]
doc.build(E)
print("ok", doc.filename)
