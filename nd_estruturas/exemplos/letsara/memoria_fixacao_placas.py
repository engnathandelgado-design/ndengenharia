"""Memória de cálculo ND-LET-MC07 (PDF) — fixação das placas de fechamento pelo sistema Trejor (rev06, DEC-026).
Lê fixacao_placas.json (calc_fixacao_placas.py) e placas.json. Tabelas de verificação ficam aqui (não nas pranchas do cliente)."""
import json
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

AQ = Path(__file__).parent
FX = json.loads((AQ / "fixacao_placas.json").read_text(encoding="utf-8"))
PL = json.loads((AQ / "placas.json").read_text(encoding="utf-8"))
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


MP, DN, CS, SO, CE, PT, P2 = FX["mef_parede"], FX["dente_ponta"], FX["console_mef"], FX["solda"], FX["CE1"], FX["pino_travamento"], FX["trava_pe_PT2"]
NC = FX["nicho_NC1"]
DA = DN["resultado"]["adotado"]
doc = SimpleDocTemplate(str(AQ / "ND-LET-MC07-FIXACAO-PLACAS-rev06.pdf"), pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=15 * mm,
                        bottomMargin=15 * mm, title="Letsara — memória MC07: fixação das placas (sistema Trejor)", author="ND Engenharia")
E = [Paragraph("ND ENGENHARIA — MEMÓRIA DE CÁLCULO ND-LET-MC07 (rev06c)", T1),
     P("Obra: Letsara — pavilhão com mezanino (Marques Engenharia). Assunto: fixação das placas protendidas 125 × 10 do fechamento lateral "
       "pelo sistema Trejor (console soldado), decisão DEC-026 de 17/10/2026. Projeto da ND Engenharia — para aprovação."),
     Paragraph("1. Sistema adotado", T2),
     P("Cada placa leva só o próprio peso e o vento: a junta horizontal macho-fêmea tem 5 mm de folga na altura (não há empilhamento). "
       "Peso e vento entram em 2 consoles CS-1 por placa, soldados na obra nas chapas de espera CE-1 dos pilares (uma por fiada, 2 consoles por chapa); "
       "a placa encosta no pilar com o braço do console no nicho NC-1 embutido em cada ponta (teto a 104 cm da base) e desce até o teto apoiar no "
       "parafuso de nível M16; o prisioneiro frontal M16 fixa o afastamento de 25 mm e segura a sobrepressão; os 2 dentes do console ficam atrás "
       "das 2 abas laterais do nicho e seguram a sucção. Como o console fica no terço superior, o vento (resultante a 62,5 cm) gira a placa em torno da linha dos "
       "consoles: o pé é travado por 2 pinos PT-1 (cartola Trejor) por junta, ao lado das alças de içamento, nos panos contínuos até o baldrame, "
       "ou por 2 travas PT-2 nos pilares nas placas de pacote suspenso (E, F e acima das esquadrias). Única solda de campo da obra: CS-1 × CE-1."),
     Paragraph("2. Placa e pinos — MEF de casca do pano (OpenSeesPy ShellMITC4)", T2),
     P(f"{MP['modelo']}. Vento p = {f(PL['vento']['p_k'], 3)} kN/m² (Cpe −1,4 de borda + Cpi 0,2, todas as placas), γ = 1,4; peso γ = 1,4. "
       f"Conferência à mão: reação vertical {f(MP['Rz_d_kN'], 2)} kN = 1,4 × {f(MP['Rz_k_kN'], 2)} (estática, desvio < 2 %); reação de vento "
       f"{f(MP['Ry_d_kN'], 2)} kN contra {f(MP['Ry_mao_sem_pino_kN'], 2)} kN da placa biapoiada (os pinos redistribuem entre fiadas); momento "
       f"{f(MP['M_placa_d_kNm'], 2)} contra {f(MP['M_mao_kNm'], 2)} kN·m da biapoiada.")]
lin = [["Grandeza", "Valor", "Resistente / limite", "Uso"],
       ["Momento na placa (kN·m)", f(MP["M_placa_d_kNm"], 2), f(MP["MRd_placa_kNm"], 2), f(MP["uso_flexao_placa"], 3)],
       ["Pico local Mxx (kN·m/m)", f(MP["Mxx_local_max_kNm_m"], 2), f(MP["MRd_por_m"], 2), f(MP["Mxx_local_max_kNm_m"] / MP["MRd_por_m"], 3)],
       ["Vento por console (kN, d)", f(MP["Ry_d_kN"], 2), "—", "—"],
       ["Força no pino PT-1 (kN, d)", f(MP["F_pino_d_kN"], 2), f(min(PT["Ft_M16_kN"], PT["luva_phiN_kN"]), 1), f(PT["uso"], 3)],
       ["Deslocamento característico (mm)", f(MP["uy_k_mm"], 1), "frequente 0,3 × = " + f(0.3 * MP["uy_k_mm"], 1) + " ≤ L/250 = 40", ok(0.3 * MP["uy_k_mm"] <= 40.3)]]
E += [tab(lin, [62, 30, 56, 20]), Spacer(1, 3),
      P("Estudo feito no MEF (17/10/2026): com 1 pino só no meio da junta o momento chega a 37,5 kN·m (uso 1,00) e o pico local passa 8 % do "
        "resistente — a força do pino vira carga concentrada no meio do vão; com 2 pinos ao lado das alças, uso 0,90. Em pacotes suspensos com 2 placas "
        "e pinos entre elas a placa de baixo passa de MRd (40,1 kN·m): por isso cada placa desses pacotes tem a sua trava de pé PT-2."),
      Paragraph("3. Ponta da placa — dente Gerber por bielas e tirantes (NBR 9062:2017 7.3 e 7.4; PCI 5.6)", T2),
      P(f"Nariz = concreto acima do nicho: h = {DN['nariz_mm']['h']} mm, ln = {DN['nariz_mm']['ln']} mm, b = {DN['nariz_mm']['b']} mm; apoio a 60 mm da ponta. "
        f"Vd = {f(DN['Vd_kN'], 2)} kN (γf 1,3 × βa 1,3 de montagem, NBR 9062:2017 5.3.2, maior que 1,4 da fase final; γn = 1,0, 7.3.1.1), "
        f"Hd = {f(DN['Hd_kN'], 2)} kN (μ 0,4 aço × aço). a/d = {f(DN['resultado']['NBR']['a_d'], 3)} ({DN['resultado']['NBR']['tipo']}); "
        f"τwd = {f(DN['resultado']['NBR']['tau_wd'], 2)} ≤ {f(DN['resultado']['NBR']['tau_lim'], 2)} MPa (biela).")]
lin = [["Armadura", "Calculada (mm²)", "Adotada"],
       ["Tirante (NBR / PCI)", f"{DN['resultado']['NBR']['As_tir']} / {DN['resultado']['PCI']['As']}", "N3 " + DA["tirante"]],
       ["Suspensão", f"{DN['resultado']['NBR']['As_sus']} / {DN['resultado']['PCI']['Ash']}", "N4 " + DA["suspensao"].split(" a até")[0]],
       ["Costura", f"{DN['resultado']['NBR']['As_cost']} / {DN['resultado']['PCI']['Ah']}", "N5 " + DA["costura"].split(" nos")[0]],
       ["Vertical do nariz", f"{DA['Av']}", "N7 1 estribo Ø6,3 (2 ramos, 62 mm²)"],
       ["Ancoragem da base do nicho", "—", "N6 1 estribo horizontal Ø6,3"]]
E += [tab(lin, [50, 40, 80]),
      Paragraph("4. Console CS-1 — MEF de casca das chapas + NBR 8800:2008", T2),
      P(f"Costas 16 × 120 × 130 (só a altura da ligação: z −100 a +30), 2 almas 9,5 (raiz 80, ponta 50, braço até 64 mm do plano da CE-1), mesa 16 × 48 × 80, 2 dentes 19 × 13 × 32 sobre as almas, "
        f"chapa de ponta 9,5 × 34 × 60,5 entre as almas com porca soldada do prisioneiro frontal; A572-50 (fy 345). Engaste nas linhas de solda; chapa de ponta incluída no modelo; "
        f"carga do M16 de nível na área da porca soldada; momento dos dentes como binário vertical sobre as almas. "
        f"Conferência à mão: almas na raiz σ = {f(FX['console_mao']['sigma_almas_MPa'])} MPa, τ = {f(FX['console_mao']['tau_almas_MPa'])} MPa.")]
lin = [["Caso", "von Mises máx (MPa)", "p99 (MPa)", "flecha (mm)"]] + [[k, f(v["vm_max_MPa"]), f(v["vm_p99_MPa"]), f(v["flecha_mm"], 3)] for k, v in CS.items() if isinstance(v, dict)]
E += [tab(lin, [60, 36, 30, 30]), P(CS["criterio"] + f" — uso {f(CS['uso'], 3)}."),
      P(f"Solda de filete {f(SO['filete_mm'], 0)} mm, {SO['cordoes']}, {SO['eletrodo']}: resultante {f(SO['f_res_MPa'])} MPa ≤ {f(SO['fw_Rd_MPa'])} MPa "
        f"(6.2.5.1) — uso {f(SO['uso'], 3)}. {SO['obs']}."),
      P(f"Dentes: {FX['dentes_CS1']['peca']}; F = {f(FX['dentes_CS1']['F_por_dente_kN'], 2)} kN por dente a {f(FX['dentes_CS1']['braco_mm'], 0)} mm da mesa (engate mínimo 10): "
        f"σ = {f(FX['dentes_CS1']['sigma_MPa'])} ≤ {f(FX['dentes_CS1']['lim_MPa'])} MPa (uso {f(FX['dentes_CS1']['uso'], 3)}); solda {f(FX['dentes_CS1']['solda_MPa'])} ≤ {f(FX['dentes_CS1']['solda_lim_MPa'])} MPa."),
      P(f"Parafusos de ajuste: M16 × 45 8.8 de nível (y = 48 mm, porca soldada + contraporca) N = {f(FX['parafusos_ajuste']['M16_nivel']['N_Sd_kN'])} kN ≤ {f(FX['parafusos_ajuste']['M16_nivel']['N_Rd_kN'])} kN; "
        f"prisioneiro M16 × 45 frontal N = {f(FX['parafusos_ajuste']['M16_frontal']['N_Sd_kN'])} kN ≤ {f(FX['parafusos_ajuste']['M16_frontal']['N_Rd_kN'])} kN; contato da cabeça do M16 de nível no teto: {f(FX['parafusos_ajuste']['contato_teto_nicho']['sigma_MPa'])} MPa."),
      Paragraph("4a. Nicho NC-1 — caixa fechada e ancoragem no concreto", T2),
      P(f"{NC['caixa']}. Caminho das forças: peso → M16 de nível → teto → nariz (compressão {f(NC['teto_compressao']['sigma_MPa'])} ≤ fcd {f(NC['teto_compressao']['fcd_MPa'])} MPa); "
        f"sucção → 2 dentes → 2 abas laterais (σ {f(NC['aba']['sigma_MPa'])} MPa, uso {f(NC['aba']['uso'], 3)}) → teto → grampos + N5; sobrepressão → prisioneiro frontal → fundo 12,5 como viga entre teto e base "
        f"(M = {f(NC['fundo']['M_kNmm'], 0)} kN·mm, σ {f(NC['fundo']['sigma_MPa'])} ≤ {f(NC['fundo']['lim_MPa'])} MPa, uso {f(NC['fundo']['uso'], 3)}) → teto e base → grampos + N5 / N6. "
        f"A parede de concreto de 40 mm atrás do fundo, sozinha, não passaria ({f(NC['sem_caixa_parede_40mm']['V_Rd_kN'])} < {f(NC['sem_caixa_parede_40mm']['F_kN'])} kN) e não é contada. "
        f"Ancoragem do teto: F = {f(NC['ancoragem_teto']['F_kN'])} kN contra N5 {f(NC['ancoragem_teto']['N5_phi_kN'])} kN + grampos {f(NC['ancoragem_teto']['grampos_phi_kN'])} kN (uso {f(NC['ancoragem_teto']['uso'], 3)}); "
        f"da base: F = {f(NC['ancoragem_base']['F_kN'])} kN (uso {f(NC['ancoragem_base']['uso'], 2)}). Parede lateral 3 mm sem esforço (só fecha o concreto). Armação da ponta: ND-LET-PP01; fabricação: ND-LET-PP02."),
      Paragraph("4b. Compatibilidade geométrica e janela de montagem", T2),
      P("Conferido no pior caso das tolerâncias (afastamento 25 ± 5, G 50 ± 10, posição do console ± 5): " + "; ".join(f"{k} {f(v, 1)}" for k, v in FX["montagem_CS1_NC1"]["folgas_mm"].items()) + " mm. A placa encosta com o teto do nicho R acima da posição final: " + "; ".join(f"{k}: R = {f(v[0], 0)} a {f(v[1], 1)}" for k, v in FX["montagem_CS1_NC1"]["janela_R_mm"].items()) + " mm (aba por cima dos dentes e base por baixo do braço, 5 mm de folga)."),
      Paragraph("5. Chapa de espera CE-1 no pilar (ACI 318-19 cap. 17, concreto fissurado)", T2),
      P(f"{CE['peca']}. Por chapa (2 consoles): V = {f(CE['V_kN'])} kN, M = {f(CE['M_kNm'], 2)} kN·m, tração na linha superior "
        f"{f(CE['T_linha_sup_kN'])} kN ≤ {f(CE['phiN_linha_kN'])} kN ({CE['modo_N']}); cortante φVn = {f(CE['phiV_kN'])} kN ({CE['modo_V']}: pinos a 80 mm das "
        f"faces laterais do pilar de 40, ruptura de borda paralela; grampos U Ø10 N18 C=96 sob o pino de baixo de cada coluna, como armadura de ancoragem, 17.5.2.1). Interação 17.8: {f(CE['interacao'], 3)} — {ok(CE['ok'])}."),
      Paragraph("6. Pino PT-1 e trava de pé PT-2", T2),
      P(f"PT-1: {PT['peca']}. F = {f(PT['F_d_kN'], 2)} kN; luva TSA M16 hef 70 na placa (fckj 25): φNn = {f(PT['luva_phiN_kN'])} kN ({PT['modo']}); uso {f(PT['uso'], 3)}."),
      P(f"PT-2: {P2['peca']}. F = {f(P2['F_d_kN'], 2)} kN; aba M = {f(P2['M_aba_kNm'], 3)} ≤ {f(P2['MRd_aba_kNm'], 3)} kN·m; bucha da placa φNn = {f(P2['bucha_placa_phiN_kN'])} kN; "
        f"bucha do pilar φVn = {f(P2['bucha_pilar_phiV_kN'])} kN ({P2['modo_pilar']}); uso {f(P2['uso'], 3)}."),
      Paragraph("7. Pendências", T2),
      P("(a) Medidas do CS-1, NC-1 e cartola PT-1 são de pré-dimensionamento: trocar pelas do catálogo 09 da Trejor (consoles metálicos para painéis "
        "de fachada) e conferir as capacidades declaradas pelo fornecedor. (b) Pinos PT-1 da 1ª fiada: luva TSA no topo da viga baldrame (projeto de "
        "fundações). (c) Solda de campo: procedimento qualificado, soldador certificado, inspeção visual 100 % e líquido penetrante por amostragem, "
        "galvanização a frio.")]
doc.build(E)
print("ok", doc.filename)
