"""Memória de cálculo ND-LET-MC06 (PDF) — cobertura metálica rev05: terças Z 302 METSEC contínuas por transpasse (METLAP),
apoios sem mão-francesa, emendas, escoras, correntes, suporte ST-1P e esperas. Lê cobertura_metalica.json e estudo_tercas_sem_mf.json."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

AQ = Path(__file__).parent
J = lambda n: json.loads((AQ / n).read_text(encoding="utf-8"))
CB, ES = J("cobertura_metalica.json"), J("estudo_tercas_sem_mf.json")
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


pf, tc, pc, te, cr, st, ch = CB["perfil"], CB["terca"], CB["pecas"], CB["terca_escora"], CB["correntes"], CB["ST1P"], CB["chumbadores"]

# ------------------------------------------------------------------ figura: envoltória de momentos da linha de terças
env = tc["envoltoria"]
fig, ax = plt.subplots(figsize=(7.2, 2.6), dpi=170)
ax.plot(env["x"], env["M_max"], color="#c0392b", lw=1.1, label="M máx. (ELU)")
ax.plot(env["x"], env["M_min"], color="#1f4e79", lw=1.1, label="M mín. (ELU)")
ax.axhline(0, color="k", lw=0.6)
for xs in env["x_apoios"]:
    ax.axvline(xs, color="#888888", lw=0.4, ls="--")
    if 0 < xs < env["x_apoios"][-1]:
        ax.axvspan(xs - pc["transpasse_cada_lado_mm"] / 1000, xs + pc["transpasse_cada_lado_mm"] / 1000, color="#f0c419", alpha=0.35, lw=0)
for lim, cor in ((tc["MRd_contida"]["MRd"], "#c0392b"), (-tc["MRd_correntes"]["MRd"], "#1f4e79")):
    ax.axhline(lim, color=cor, lw=0.6, ls=":")
ax.set_xlabel("posição na linha de terças (m)"); ax.set_ylabel("M (kN·m)")
ax.legend(fontsize=7, loc="lower right"); ax.tick_params(labelsize=7)
ax.set_title("Terça Z 302 contínua — envoltória ELU (faixa amarela = transpasse, 2 perfis); pontilhado = MRd", fontsize=8)
fig.text(0.99, 0.01, "projeto da ND Engenharia", ha="right", fontsize=6, color="#888888")
fig.tight_layout()
FIG = AQ / "mc06_envoltoria.png"
fig.savefig(FIG); plt.close(fig)

doc = SimpleDocTemplate(str(AQ / "ND-LET-MC06-COBERTURA-rev05.pdf"), pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=15 * mm,
                        bottomMargin=15 * mm, title="Letsara — memória MC06: cobertura metálica (terças Z contínuas)", author="ND Engenharia")
E = [Paragraph("ND ENGENHARIA — MEMÓRIA DE CÁLCULO ND-LET-MC06 (rev05)", T1),
     P("Obra: Letsara — pavilhão com mezanino (Marque Engenharia). Assunto: terças da cobertura sem mão-francesa — perfil Z METSEC contínuo "
       "por transpasse (METLAP), ligações terça × viga, emendas, escoras do contraventamento, correntes, suporte ST-1P e esperas. "
       "17/10/2026. Projeto da ND Engenharia — para aprovação."),
     Paragraph("1. Escolha do perfil (estudo comparativo)", T2),
     P("Escolha automática do perfil mais leve sem mão-francesa entre os catálogos Isoeste (Ue e Z45, CIVIL 300 e ZAR 345) e METSEC / voestalpine "
       "Meincol (Z e C, fy 400), biapoiada × contínua, 2 × 3 linhas de correntes, com as mesmas cargas e a mesma escora do modelo global. "
       "Opção adotada pelo contratante: Z 302 METSEC contínua por transpasse (folga maior e encaixe das peças no transporte).")]
lin = [["opção (sem mão-francesa)", "perfil", "kg/m", "peso total (t)", "uso (governa)"]]
vistos = set()
for r in ES["melhores"]:
    k = (r["familia"], r["esquema"], r["correntes"])
    if k in vistos or len(lin) > 9:
        continue
    vistos.add(k)
    lin.append([f"{r['familia']}, {r['esquema']}, {r['correntes']} linhas", r["perfil"], f(r["kg_m"], 2), f(r["peso_total_t"], 1), f"{f(r['uso_max'], 2)} ({r['governa']})"])
E += [tab(lin, [55, 50, 16, 24, 33])]

E += [Paragraph("2. Perfil, aço e cargas", T2),
      P(f"{pf['nome']}; aço fy = {f(pf['fy'], 0)} MPa (fu = {f(pf['fu'], 0)} MPa adotado — conferir com o fabricante); galvanizado Z275. "
        f"Linha média com cantos vivos: A = {pf['A_mm2']} mm², Ix = {f(pf['Ix_cm4'])} cm⁴, Ixy = {f(pf['Ixy_cm4'])} cm⁴, W = {f(pf['W_cm3'])} cm³; "
        f"massa de catálogo {f(pf['kg_m'], 2)} kg/m. Curva de assinatura por faixas finitas (NBR 14762:2010 Anexo C, MRD): flexão — local "
        f"{f(pf['assinatura_M']['local'], 3)}·My, distorcional {f(pf['assinatura_M']['dist'], 3)}·My; compressão — local {f(pf['assinatura_N']['local'], 3)}·Ny."),
      P(f"Vãos {', '.join(f(v, 3) for v in tc['vaos_m'])} m; terças a {f(tc['s_m'], 3)} m. Carregamentos iguais ao modelo global: permanentes (zipada, lã, TP40, "
        "fixações, painéis solares, instalações) + peso da terça; sobrecarga 0,25 kN/m² alternada nos vãos; vento q0 = 0,874 kN/m² com Cp −1,0 (geral) e −1,6 "
        "(faixas de borda, envoltória em toda a linha, a favor da segurança). Combinações NBR 8681: 1,35 G + 1,5 Q; 1,0 G + 1,4 W (sucção).")]

E += [Paragraph("3. Terça contínua por transpasse — MEF", T2),
      P("Viga contínua de 8 vãos por elementos finitos (Euler-Bernoulli, nd_estruturas.viga_continua), com 2·EI no trecho do transpasse (2 perfis encaixados). "
        "M > 0 (mesa superior comprimida, presa à telha): MRd sem flambagem lateral; M < 0 (mesa inferior comprimida): MRd com Lb entre correntes; "
        "dentro do transpasse, 2 perfis; flexão + cortante pela NBR 14762:2010 9.8.5; flecha L/180 (NBR 8800:2008 Anexo C)."),
      Image(str(FIG), width=178 * mm, height=64 * mm)]
lin = [["transpasse (cada lado)", "uso máx.", "governa", "flecha (mm)", "situação"]]
for e_ in tc["estudo_transpasse"]:
    lin.append([f"{f(e_['a_m'], 2)} m", f(e_["uso"], 3), e_["governa"], f(e_["flecha_mm"]), ok(e_["ok"])])
E += [tab(lin, [30, 18, 90, 20, 18]),
      P(f"Adotado: transpasse de {pc['transpasse_cada_lado_mm']} mm para cada lado do eixo de cada TS-01 (total {pc['transpasse_total_mm']} mm); "
        f"MRd sem FLT = {f(tc['MRd_contida']['MRd'], 2)} kN·m ({tc['MRd_contida']['modo']}); MRd com Lb = {tc['Lb_corr_mm']} mm = "
        f"{f(tc['MRd_correntes']['MRd'], 2)} kN·m ({tc['MRd_correntes']['modo']}); VRd = {f(tc['VRd'])} kN. Governa {tc['governante']['tipo']} — "
        f"{tc['governante']['comb']} em x = {f(tc['governante']['x_m'], 2)} m ({tc['governante']['trecho']}): M = {f(tc['governante']['M'], 2)} kN·m, "
        f"V = {f(tc['governante']['V'], 2)} kN, uso {f(tc['governante']['uso'], 3)}. Flecha {f(tc['flecha_mm'])} mm ≤ {f(tc['flecha_lim_mm'])} mm.")]
lin = [["vão", "L (m)", "M+ máx (kN·m)", "M− máx (kN·m)"]] + [[v["vao"], f(v["L_m"], 3), f(v["M_pos"], 2), f(v["M_neg"], 2)] for v in tc["por_vao"]]
E += [tab(lin, [25, 25, 35, 35])]

pt, ap = tc["parafusos_transpasse"], tc["apoio"]
E += [Paragraph("4. Ligações: emenda por transpasse e apoio sem mão-francesa", T2),
      P(f"Emenda: {pt['desc']}. O perfil que termina leva M_apoio/2 no apoio e zero na ponta, à distância do transpasse; força nos 2 parafusos da ponta "
        f"Fd = {f(pt['Fd'], 2)} kN por parafuso ≤ {f(pt['Rd'])} kN (corte M12 8.8 / contato na alma de 2,30 — NBR 14762:2010 10.3) → uso {f(pt['uso'], 3)}."),
      P(f"Apoio: {ap['desc']}. {ap['nota']}. Apoio interno (2 terças): R = {f(ap['interno']['R'], 2)} kN, tração {f(ap['interno']['T_parafuso'], 2)} kN, "
        f"corte {f(ap['interno']['V_parafuso'], 2)} kN → interação {f(ap['interno']['interacao'], 3)}; fachada (VB): interação {f(ap['extremo']['interacao'], 3)}. "
        f"TRd = min(tração do M12 {f(ap['Ft_Rd'])} kN; arrancamento da alma pela arruela Ø24 {f(ap['arrancamento_alma_Rd'])} kN, AISI S100-16 J6.2.2). "
        "A torção de apoio do Z (carga no meio da aba superior, a 45 mm da alma) é resistida pelo binário das 2 linhas de parafusos — dispensa a mão-francesa.")]

E += [Paragraph("5. Terças escoras do contraventamento (NBR 14762:2010 9.9)", T2), P(te["nota"] + ".")]
lin = [["vão", "faixa", "vento", "Nd (kN)", "NcRd", "Md (kN·m)", "MRd", "amplif.", "interação"]]
for e_ in te["por_vao"]:
    lin.append([e_["vao"], e_["faixa"], e_["vento"], f(e_["Nd"]), f(e_["NcRd"]), f(e_["Md"], 2), f(e_["MRd"], 2), f(e_["amplificacao"], 3), f(e_["interacao"], 3)])
E += [tab(lin, [14, 26, 14, 16, 16, 20, 16, 16, 18]),
      P(f"Governa o vão {te['vao_governante']}, linha x = {f(te['linha_governante_x_m'], 2)} m ({te['faixa_governante']}): interação {f(te['interacao'], 3)} ≤ 1 — {ok(te['ok'])}.")]

E += [Paragraph("6. Correntes, tirantes rígidos e diagonais (AISI S100-16 D3.2)", T2),
      P(f"Terça Z: força lateral por corrente P = W·(Ixy/Ix) + componente do caimento 3 % (Ixy/Ix = {f(cr['Ixy_sobre_Ix'], 3)}), acumulada nas terças da meia água "
        f"(sem a restrição da telha, a favor da segurança): F = {f(cr['F_max_kN'], 2)} kN. Corrente {cr['flexivel']['barra']}: NtRd {f(cr['flexivel']['NtRd'])} kN → uso "
        f"{f(cr['flexivel']['uso'], 3)}; tirante rígido L 51×51×3,2: uso {f(cr['rigida']['uso'], 3)}; diagonal de ancoragem Ø16: Td {f(cr['diagonal']['Td'])} kN → uso {f(cr['diagonal']['uso'], 3)}.")]

E += [Paragraph("7. Suporte ST-1P e esperas no concreto", T2),
      P(f"ST-1P (chapa dobrada 9,5 A36) no apoio interno: arrancamento de cálculo {f(st['reacao_suc_kN'], 2)} kN (as 2 terças do transpasse); flexão da aba "
        f"uso {f(st['aba']['uso'], 3)}; 2 esperas ES-1 M16: tração {f(st['esperas']['Td'], 2)} kN e corte {f(st['esperas']['Vd'], 2)} kN → interação {f(st['esperas']['interacao'], 3)} "
        "(NBR 8800:2008 6.3.3).")]
lin = [["espera (ACI 318-19 cap. 17, C50 fissurado)", "descrição", "uso / interação"]]
for k, d in ch.items():
    lin.append([k, d["esperas"], f(d.get("interacao", d.get("uso")), 3)])
E += [tab(lin, [45, 95, 30])]

E += [Paragraph("8. Observações", T2),
      P(f"Peças: cada terça vence um vão e passa {pc['transpasse_cada_lado_mm']} mm além do eixo do apoio interno (nas fachadas {pc['extensao_fachada_mm']} mm); "
        f"maior peça {pc['L_max_mm']} mm (≤ 12 m, transporte). Furação de fábrica METSEC (E 55 / F 52; correntes no meio da alma)."),
      P("Conferir com a voestalpine Meincol antes do pedido: fu do aço, ângulo dos enrijecedores, encaixe dos perfis no transpasse (METLAP) e furação. "
        "Pelo método da norma brasileira o Z não ficou mais leve que o C nesta obra; o software de dimensionamento do fabricante (baseado em ensaios) "
        "pode reduzir espessuras — se usado, a verificação dele substitui as seções 3 e 5 desta memória."),
      P("Projeto da ND Engenharia — para aprovação, não executar.")]
doc.build(E)
print("ok", doc.filename)
