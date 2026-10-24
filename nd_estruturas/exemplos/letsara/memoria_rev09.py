"""Memória de cálculo ND-LET-MC09 (PDF) — alterações do pacote rev09 (23/10/2026, DEC-045 a DEC-049):
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


SAI = Path("/home/claude/letsara/entregas/ND-LET-MC09-REV09-rev09.pdf")
doc = SimpleDocTemplate(str(SAI), pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=15 * mm, bottomMargin=15 * mm,
                        title="Letsara — memória MC09: alterações do pacote rev09", author="ND Engenharia")
c39, c73, ce = CM["piso_390"], CM["laje_730"], CM["escada"]
E = [Paragraph("MEMÓRIA DE CÁLCULO ND-LET-MC09 — ALTERAÇÕES DO PACOTE REV09 (23 e 24/10/2026)", T1),
     P("Obra: Letsara — pavilhão com mezanino (Marques Engenharia). Decisões do Nathan: DEC-045 (pisos +3,90 / +7,30, abertura e escada metálica, "
       "P6/P7 da escada e P6 da linha 2), DEC-046 (laje de cima sem uso), DEC-047 (vigas do mezanino retangulares protendidas com 2º estágio, sem meio vaso), "
       "DEC-048 (linha 2 sem TS-01, cobertura metálica), DEC-049 (VM 30 × 75 com dente Gerber 45 em todas as marcas) e, em 24/10, DEC-050/052 (linha 2: W 200 × 15,0 contínua nos pilares e em montantes no meio dos vãos), "
       "DEC-051 (escada interna sem solda, base BM-1), DEC-053 (escada metálica externa em L na fachada A), DEC-054 (I130 com h 120, dente Gerber e consolo com mísula), "
       "DEC-055 (2º pavimento = topo da capa +3,90, piso pronto ~+3,95: as duas escadas chegam no piso pronto com 22 espelhos de 17,95), DEC-056 (doca com piso nivelado) e DEC-057 (sem ponte rolante). "
       "Documento para análise do Nathan antes da emissão do zip com DXF e IFC."),
     Paragraph("1. Níveis e cargas do mezanino", T2),
     tab([["NÍVEL / USO", "SOBRECARGA (kN/m²)", "REVESTIMENTO (kN/m²)", "OBS."],
          ["+3,90 — 2º pavimento (depósito)", f(c39["sobrecarga"]), f(c39["revestimento"]), "5,0 confirmada pelo Nathan em 23/10/2026 (NBR 6120:2019)"],
          ["+7,30 — laje de cobertura do bloco, sem uso", f(c73["sobrecarga"]), f(c73["revestimento"]), c73["uso"]],
          ["Escada metálica", f(ce["sobrecarga"]), "—", ce["uso"]]], [52, 26, 28, 72]),
     P("Pisos = topo da capa. Laje alveolar h20 + capa 5 apoiada 10 cm no topo da VM sobre fita de neoprene 10 mm: topo da VM = piso − 0,26; fundo da VM = topo − 0,75 "
       f"(+{f(3.90 - 0.26 - P_['h_pm'], 2)} e +{f(7.30 - 0.26 - P_['h_pm'], 2)}). Única fonte: geometria.Z_PISOS e cargas_mezanino.json."),
     Paragraph("2. Vigas do mezanino — estudo de largura e solução adotada (DEC-049)", T2),
     P("Estudo (estudo_vm_largura.py): para b = 25, 30, 35 e 40 cm, menor h (de 5 em 5 cm) em que TODAS as marcas passam em todas as verificações da "
       "calc_vm_retangular (protensão completa, montagem sem escoramento, seção composta, flechas, interface, continuidade) e o menor dente que passa na "
       "NBR 9062:2017 7.4 (biela τwd ≤ 0,18 fck/1,4 e consolo invertido) e no PCI (Vmax), com γn = 1,2 (7.3.1.1: parcela variável ≈ 45 % da reação). "
       "O dente 25 × 35 da solução anterior (25 × 80) reprovou no MEF (Vu 224 kN < 1,06 Fd 497 kN) e na biela (6,35 > 5,14 MPa)."),
     tab([["b × h (cm)", "dente (cm)", "fundo (m)", "faixa 2º est. (cm)", "custo índice"]] +
         [[f"{f(c['b'] * 100, 0)} × {f(c['h'] * 100, 0)}", f(c["hd"] * 100, 0), f"{f(c['fundo'][0], 2)} / {f(c['fundo'][1], 2)}", f(c["faixa_2e"] * 100, 0), f"{c['custo_total']:,}".replace(",", ".")] for c in ES],
         [30, 22, 34, 30, 30]),
     P(f"Adotado (Nathan, 23/10/2026): retangular {f(P_['b'] * 100, 0)} × {f(P_['h_pm'] * 100, 0)} protendida em todas as marcas (fôrma única), dente Gerber "
       f"{f(P_['dente']['hd'] * 100, 0)} × {f(P_['dente']['ln'] * 100, 0)}, recorte {f(P_['dente']['recorte'] * 100, 0)}, consolo CP-MEZ com a largura da face do pilar "
       f"({f(P_['b_consolo'] * 100, 0)}) × {f(P_['dente']['consolo_proj'] * 100, 0)} × {f(P_['dente']['consolo_h'] * 100, 1)}, NEO-5F 200 × 200 × 21 fretado, "
       f"faixa de 2º estágio de {f(P_['faixa_2e'] * 100, 0)} cm do lado da borda, C{P_['fck']:.0f} (fckj {P_['fckj']:.0f} MPa), CP-190 RB Ø12,7.")]
lin = [["MARCA", "L (m)", "CORD.", "PESO (t)", "M2d / MRd2", "σ ELS-D (MPa)", "flecha final (mm)", "Vd (kN)", "Fd dente (kN)", "OK"]]
for mk in ("VM-01", "VM-02", "VM-03", "VM-04"):
    v = VM[mk]
    gov = max(v["casos"], key=lambda r: r["ELU"]["M2d"])
    lin.append([mk, f(v["L_peca"], 2), str(v["n_cord"]), f(v["peso_t"], 2), f"{f(gov['ELU']['M2d'], 0)} / {f(gov['ELU']['MRd2'], 0)}", f(gov["ELS"]["sig_D"], 2),
                f"{f(gov['flecha']['final_mm'])} ≤ {f(gov['flecha']['lim_final_mm'])}", f(v["cortante"]["Vd"]), f(v["dente"]["Fd"]), ok(v["ok"])])
E += [tab(lin, [14, 13, 12, 14, 24, 18, 26, 14, 18, 10]),
      P("Casos por marca: VM-01/VM-02 nas linhas 1 e 2 dos dois pisos; VM-03 linha 2 D → P6; VM-04 P6 → P7 (+3,90, escada) e P6 → E (+7,30). "
        "A marca leva o caso que governa; protensão completa (ELS-D na frequente, NBR 6118:2023 Tab. 13.4, DEC-043).")]
v2 = VM["VM-02"]
E += [P(f"VM-02 (governa): perdas totais {f(v2['protensao']['perdas']['perda_total_pct'])} %; ato da protensão (γp 1,1): topo {f(v2['ato']['topo_ponta'], 2)} ≤ {f(v2['ato']['lim_t'], 2)} MPa, "
        f"base {f(v2['ato']['base_meio'], 2)} ≥ {f(v2['ato']['lim_c'], 2)} MPa; interface (6.3.3): τsd {f(v2['interface']['tau_sd'], 2)} ≤ τRd {f(v2['interface']['tau_rd'], 2)} MPa; "
        f"negativa de continuidade (5.1.2.10): Md {f(v2['negativa']['Md_kNm'], 0)} ≤ MRd {f(v2['negativa']['MRd_kNm'], 0)} kN·m — {v2['negativa']['adotado']}.")]
dn = v2["dente"]["nbr_pci"]
E += [Paragraph("3. Dente Gerber 45 × 40 e consolo CP-MEZ (NBR 9062:2017 7.3 e 7.4)", T2),
      tab([["VERIFICAÇÃO", "VALOR", "LIMITE", "OK"],
           ["Biela do dente τwd (7.4)", f(dn["NBR"]["tau_wd"], 2) + " MPa", f(dn["NBR"]["tau_lim"], 2) + " MPa", ok(dn["NBR"]["ok_biela"])],
           ["PCI Vmax", f(dn["PCI"]["Vmax_kN"]) + " kN", f(v2["dente"]["Fd"]) + " kN", ok(dn["PCI"]["ok_Vmax"])],
           ["Consolo CP-MEZ τwd", f(CO["CP-MEZ"]["tau_wd_MPa"], 2) + " MPa", f(CO["CP-MEZ"]["tau_wu_MPa"], 2) + " MPa", ok(CO["CP-MEZ"]["ok"])]], [70, 36, 36, 20]),
      P(f"Armadura do dente (VM-02): tirante {MV['calculo']['adotado']['tirante']}; suspensão {MV['calculo']['adotado']['suspensao']}; costura {MV['calculo']['adotado']['costura']}; "
        f"{MV['calculo']['adotado']['vertical_dente']}; + 4 Ø16 retas no fundo (L 250 cm) a partir do canto reentrante. Consolo CP-MEZ: {CO['CP-MEZ']['tirante']}."),
      Paragraph("4. MEF não linear do dente (mef_vm_largura_1f.py) e RESSALVA da zona de transferência", T2),
      P(f"Modelo 2D em estado plano (OpenSeesPy, ASDConcrete3D, {MV['mef']['n_elem']} elementos), seção 30 × 75, dente 45, suspensão 3 Ø20, 4 Ø16 retas no fundo, "
        f"protensão aplicada com a transferência (lt {f(MV.get('lt', 880) / 10 if isinstance(MV.get('lt'), (int, float)) else 88, 0)} cm). Resultado: pico de {f(MV['mef']['V_pico_kN'])} kN ≥ Fd {f(MV['Fd'])} kN (γn 1,2); "
        f"pelo critério de 3,5‰ no concreto o primeiro elemento a passar do limite é o do canto inferior junto ao recorte, onde as cordoalhas começam a transferir "
        f"(x {MV['mef']['limite']['xy_concreto_mm'][0]} mm, y {MV['mef']['limite']['xy_concreto_mm'][1]} mm), a {f(MV['mef']['Vu_kN'])} kN (~290 kN)."),
      P("Ressalva registrada (DEC-049): é esmagamento local na zona de ancoragem das cordoalhas, não ruptura do dente (aço do tirante e da suspensão abaixo do escoamento "
        "nesse passo; a peça segue ganhando carga até o pico). Tratamento: fretagem N14 (estribos fechados Ø8 c/5 nos 50 cm a partir do canto reentrante, "
        "envolvendo as 2 camadas inferiores de cordoalhas) + N13 4 Ø16 retas no fundo, e liberação gradual com fcj ≥ 32 MPa. Detalhado na ND-LET-VM01 (armação).")]
img = AQ / "mef_dente_VM-RET_750_450.png"
if img.exists():
    E.append(Image(str(img), width=170 * mm, height=95 * mm))
E += [PageBreak(), Paragraph("5. Laje alveolar LP20 (calc_laje_alveolar.py)", T2),
      P(f"Peça {f(P_['vao_laje'], 2)} m (apoio 10 cm no topo das VM 30 × 75), vão de cálculo {f(P_['vao_laje'] - 0.10, 2)} m; "
        f"{sum(1 for c in LA['cordoalhas'] if c['diam'] == '15.2')} Ø15,2 + {sum(1 for c in LA['cordoalhas'] if c['diam'] == '12.7')} Ø12,7 CP-190 RB; uso máximo {f(LA['uso_max'], 2)} ({ok(LA['ok'])}); "
        f"+7,30 com a mesma marca: uso {f(LA['nivel_730']['uso_max'], 2)} ({ok(LA['nivel_730']['ok'])}); LA-03/LA-04 curtas ({f(LA['LA03']['L_peca'], 2)} m, {LA['LA03']['arranjo']}): uso {f(LA['LA03']['uso_max'], 2)}. "
        f"Vibração (NBR 6118:2023 23.3): f1 = {f(LA['vibracao']['f1_Hz'], 2)} Hz — abaixo de 4,8 Hz (referência de escritório com folga); aceitável para depósito, reavaliar se o uso mudar."),
      Paragraph("6. Cobertura metálica da linha 2 (calc_cobertura_linha2.py, NBR 8800:2024) — DEC-052", T2),
      P(f"{CB['perfil']} {CB['aco']} contínua de A a E em 4 módulos, apoiada na cabeça de concreto dos 6 pilares (CA-L2 250 × 250 × 19 sobre graute, 4 BR-M16 L 450 pela mesa) "
        f"e em 4 montantes {CB['montante']} no meio dos vãos A–B, B–C, C–D e D–P6, sobre as VM do +7,30 (espera EM-L2 laçada na alça N9, posta antes da capa); faixa de influência {f(CB['trib_m'], 2)} m. "
        f"ELU: Msd {f(CB['verificacoes']['Msd'])} ≤ MRd {f(CB['verificacoes']['MRd'])} kN·m (uso {f(CB['verificacoes']['uso_M'], 2)}; sem mão-francesa seria {f(CB['verificacoes']['uso_sem_mao_francesa'], 2)}), "
        f"Vsd {f(CB['verificacoes']['Vsd'])} ≤ VRd {f(CB['verificacoes']['VRd'])} kN (uso {f(CB['verificacoes']['uso_V'], 2)}); flecha G + Q {f(CB['flecha']['GQ_mm'])} ≤ {f(CB['flecha']['lim_L250_mm'])} mm (com a mola da VM). "
        f"Mão-francesa {CB['mao_francesa']['perfil']} em toda terça. W 200 × 15,0 é o W mais leve que passa: W 150 × 13,0 dá flexão 1,20 e flecha 21,2 mm. "
        f"Aço: viga {CB['aco_kg']['viga']} kg + montantes {CB['aco_kg']['montantes']} kg (antes, W 310 × 32,7 só nos pilares: ≈ 1,3 t)."),
      tab([["MONTANTE", "VÃO", "VM", "L (m)", "Nc,d (kN)", "Nt,d (kN)", "uso compr.", "uso tração", "uso cantoneiras", "barra espera", "alça N9 da VM"]] +
          [[m["nome"], m["vao"], m["vm"], f(m["L_m"], 3), f(m["Nc_d"]), f(m["Nt_d"]), f(m["uso_compressao"], 2), f(m["uso_tracao"], 2), f(m["uso_cantoneiras"], 2),
            f(m["espera"]["uso_barra"], 2), f(m["espera"]["uso_alca"], 2)] for m in CB["montantes"]],
          [16, 12, 14, 12, 15, 15, 15, 15, 18, 16, 18]),
      P("A espera EM-L2 (4 BR-M16 8.8 L 330 com gancho laçado na alça N9 Ø10 da VM) leva a tração de sucção ao 2º estágio: no MAB, Nt,d 77,3 kN → alça com uso 0,735 (governa). "
        "As VM-01/02/03 foram verificadas com a carga concentrada do montante no meio do vão (calc_vm_retangular.py, item 2)."),
      tab([["APOIO", "ONDE", "topo concreto (m)", "sobe (m)", "Nc,d (kN)", "Nt,d (kN)"]] +
          [[m["nome"], m["onde"], f(m["z_concreto"], 3), f(m["sobe_m"], 2), f(m["Nc_d"]), f(m["Nt_d"])] for m in CB["apoios_diretos"]],
          [12, 60, 24, 18, 20, 20]),
      Paragraph("7. Escada metálica (calc_escada_metalica.py)", T2),
      P(f"Escada em U, {ESC['geometria']['n_espelhos']} espelhos de {f(ESC['geometria']['espelho_m'] * 100, 2)} cm, piso {f(ESC['geometria']['piso_m'] * 100, 0)} cm, patamar +{f(ESC['geometria']['z_patamar'], 3)}, chegada no piso pronto +3,95 (DEC-055); "
        f"sobrecarga {f(ESC['cargas']['q_kN_m2'])} kN/m². Longarina {ESC['longarina']['perfil']}: uso {f(ESC['longarina']['uso'], 2)}, flecha {f(ESC['longarina']['flecha_mm'])} ≤ {f(ESC['longarina']['lim_L350_mm'])} mm, f1 {f(ESC['longarina']['f1_Hz'])} Hz; "
        f"VP-1 W 150: uso máx. {f(max(ESC[k]['uso'] for k in ('patamar_frente', 'patamar_fundo', 'chegada_frente', 'chegada_fundo')), 2)}; pilaretes uso máx. {f(max(p['uso'] for p in ESC['pilaretes']), 3)}; "
        f"ligação na face do pilar (2 L 76 + 4 M16, sem solda) uso {f(ESC['ligacoes_face'][0]['uso'], 3)}; base metálica BM-1 ({ESC['base_metalica']['perfil']} L {f(ESC['base_metalica']['L_m'], 2)} m no pé do lance 1): σ piso {f(ESC['base_metalica']['sigma_piso_MPa'], 2)} MPa, uso chumbadores {f(ESC['base_metalica']['uso_chumbador'], 3)}; piso: {ESC['base_metalica']['piso']}. Massa {ESC['massa_kg']} kg (+3 % de parafusos)."),
      Paragraph("7b. Escada metálica externa da fachada A (calc_escada_externa.py) — DEC-053", T2),
      P(f"Escada em L junto à fachada A: {EX['geometria']['n_espelhos'] if 'n_espelhos' in EX['geometria'] else 22} espelhos de {f(EX['geometria']['espelho_m'] * 100, 2)} cm, piso {f(EX['geometria']['piso_m'] * 100, 0)} cm (Blondel {f(EX['geometria']['blondel_m'] * 100, 1)} cm), "
        f"largura {f(EX['geometria']['largura'], 2)} m, patamar +{f(EX['geometria']['z_patamar'], 3)} e chegada +{f(EX['geometria']['z_chegada'], 2)} na porta do 2º pavimento (vista H). "
        f"Sobrecarga {f(EX['cargas']['q_kN_m2'])} kN/m² ({EX['cargas']['norma']}). Longarina do lance de cima {EX['longarina_cima']['perfil']}: uso {f(EX['longarina_cima']['uso'], 2)}, flecha {f(EX['longarina_cima']['flecha_mm'])} ≤ {f(EX['longarina_cima']['lim_L350_mm'])} mm, f1 {f(EX['longarina_cima']['f1_Hz'])} Hz "
        f"(U 152 não passa na flecha: {f(EX['alternativas_longarina_cima'][0]['flecha_mm'])} mm); lance de baixo {EX['longarina_baixo']['perfil']}: uso {f(EX['longarina_baixo']['uso'], 2)}; "
        f"vigas W 150 × 13,0: chegada {f(EX['viga_chegada']['uso'], 2)}, patamar {f(EX['viga_patamar']['uso'], 2)}; pilaretes uso {f(EX['pilarete_chegada']['uso'], 3)}. "
        "Bases próprias em blocos BE-1 60 × 60 × 60 C25 (σadm do solo 150 kPa a confirmar), sem apoio nas placas; travamento TR-1 no pilar P28 (eixo A). Porta na vista H: as placas acima do vão "
        "apoiam nas ombreiras internas OM-2 U 152 do piso do térreo. Tudo parafusado e galvanizado a fogo. Folha ND-LET-ES02."),
      Paragraph("10. Vigas centrais I130 com h 120 (calc_i110_r01.py, calc_dentes.py, calc_nbr9062.py) — DEC-054", T2),
      P("Decisão do Nathan (24/10, opção A do estudo estudo_i130_h120): V401 (V406) e V402 (V405) com h 120, dente Gerber 78 × 35 mantido (recorte 52 → 42), "
        "protensão LIMITADA (CAA II, pré-tração: NBR 6118:2023 Tab. 13.4 nível 2 — ELS-D na quase permanente, ELS-F na frequente), C50 e liberação da protensão SÓ com fckj 50 MPa. "
        "A V400 (V407) passa para h 120 também (fôrma única das três)."),
      tab([["VIGA", "L (m)", "CORDOALHAS Ø15,2", "Md / MRd (kN·m)", "x/d", "σ ELS-D (MPa)", "σ ELS-F (MPa)", "ato topo / base (MPa)", "flecha final (mm)", "Fd dente (kN)"]] +
          [[f"{mk} ({ {'V407': 'V400', 'V406': 'V401', 'V405': 'V402'}[mk] })", f(I1[mk]["L_peca"], 2), str(I1[mk]["arranjo"]["n_cord"]), f"{f(I1[mk]['ELU']['Md'], 0)} / {f(I1[mk]['ELU']['MRd'], 0)}",
            f(I1[mk]["ELU"]["x_d"], 3), f(I1[mk]["ELS"]["D_base"], 2), f"{f(I1[mk]['ELS']['F_base'], 2)} ≤ {f(I1[mk]['ELS']['lim_F'], 2)}",
            f"{f(I1[mk]['ato']['topo_max'], 2)} / {f(I1[mk]['ato']['base_min'], 2)}", f"{f(I1[mk]['flecha']['final_mm'])} ≤ {f(I1[mk]['flecha']['lim_mm'])}", f(I1[mk]["dente"]["Fd"])]
           for mk in ("V407", "V406", "V405")], [20, 12, 16, 22, 12, 15, 19, 22, 24, 16]),
      P("Arranjo V405/V406: 7 + 5 + 5 + 5 Ø15,2 nas linhas y 6/11/16/21 cm (as de 16 e 21 isoladas 2,0 e 4,0 m nas pontas) + 2 na mesa superior; V407: 5 + 5 + 4 + 4. "
        "σpi 1453 MPa; N3 = 6 Ø25 na mesa superior (ato junto às pontas e compressão do ELU)."),
      P(f"Dente (NBR 9062:2017 7.4, Fd = {f(I1['V406']['dente']['Fd'])} kN, Hd = {f(I1['V406']['dente']['Hd'])} kN): {DI['calculo']['adotado']['tirante']}; {DI['calculo']['adotado']['suspensao']}; {DI['calculo']['adotado']['costura']}. "
        + (f"MEF não linear (mef_dente.analisar, armação da prancha, cordoalhas Ø15,2 como n·140/98,7 Ø12,7 equivalentes): Vu = {f(DI['mef']['Vu_kN'])} kN, FS = Vu/Fd = {f(DI['mef']['FS'], 2)} ≥ 1,06 ({ok(DI['mef']['ok'])}). "
           if DI.get("mef") else "MEF: ver estudo_i130_h120_mef.json. ")
        + "Convergência: com passo de deslocamento de 0,05 mm o primeiro passo de carga não convergia (a protensão de 24 Ø15,2 fissura a ponta e a zona de transferência antes da carga); "
          "com 0,02 mm a análise segue até o pico de carga (Vu = pico, antes de qualquer limite de deformação) sem trocar o modelo nem o critério (3,5‰ no concreto / 10‰ no aço)."),
      P(f"Consolo CP-I130 com MÍSULA de concreto (NBR 9062:2017 7.3): {f(CO['CP-I130']['b_m'] * 100, 0)} × {f(CO['CP-I130']['proj_m'] * 100, 0)}, h {f(CO['CP-I130']['h_total_m'] * 100, 0)} junto ao pilar e {f(CO['CP-I130']['h_consolo_m'] * 100, 0)} na ponta "
        f"(fundo da ponta alinhado ao fundo da viga +6,576; ponta ≥ h/2), a/d {f(CO['CP-I130']['a_d'], 2)} ({CO['CP-I130']['tipo']}), Fd {f(CO['CP-I130']['Fd_kN'])} kN: τwd {f(CO['CP-I130']['tau_wd_MPa'], 2)} ≤ {f(CO['CP-I130']['tau_wu_MPa'], 2)} MPa "
        f"(na seção da carga, com a altura reduzida pela mísula: {f(N9C['tau_carga_MPa'], 2)} MPa); tirante {CO['CP-I130']['tirante']} (As {f(CO['CP-I130']['As_tir_cm2'], 2)} cm², uso {f(CO['CP-I130']['As_tir_cm2'] / 16.09, 2)}). "
        "Pilares P18 (PC-01), P20 (PC-02), P22 (PC-03) e P23 (PF-04) com o consolo novo; assento +6,966 inalterado."),
      Paragraph("8. Pilares novos e cargas na fundação (tf, 1 tf = 10 kN)", T2)]
lin = [["PILAR (modelo)", "Nk G + Q", "Nd máx", "Nd mín", "Md res máx (tf·m)", "Hd máx"]]
for nm in ("P6E", "P7E", "P6-L2"):
    d = CF["pilares"][nm]
    lin.append([{"P6E": "P6 da escada (PE-01)", "P7E": "P7 da escada (PE-02)", "P6-L2": "P6 da linha 2 (PE-03)"}[nm], f((d["G"]["N"] + d["Q"]["N"]) / 10),
                f(d["ELU"]["Nd_max"] / 10), f(d["ELU"]["Nd_min"] / 10), f(d["ELU"]["Md_res_max"] / 10), f(d["ELU"]["Hd_max"] / 10)])
E += [tab(lin, [46, 22, 22, 22, 32, 20]),
      P("Pilares dimensionados pelo método geral (dimensionar_pilares_r05.py, flexão oblíqua com 2ª ordem) e verificados no manuseio (manuseio_pilares_r05.py); arranjos nas folhas ND-LET-PE01 a PE03. "
        "Cargas na fundação de todos os pilares na ND-LET-CG01 (modelo global integrado r05)."),
      Paragraph("9. Pendências e observações", T2),
      P("(a) Portões da linha 4 (500 × 750): no vão B–P21 o fundo da TS-01A fica 7,497 na face do PG-01 e desce ~3 cm depois da montagem — quadro de decisão enviado ao Nathan. (b) Zip com DXF e IFC só depois da aprovação deste pacote (PDF). "
        "(c) Guarda-corpo e corrimão da escada fora do escopo estrutural. (d) Fretagem da zona de transferência do dente conforme item 4.")]
doc.build(E)
print("ok", SAI)
