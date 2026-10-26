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


SAI = Path("/home/claude/letsara/entregas/ND-LET-MC09-REV09-rev09.pdf")
doc = SimpleDocTemplate(str(SAI), pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=15 * mm, bottomMargin=15 * mm,
                        title="Letsara — memória MC09: alterações do pacote rev09", author="ND Engenharia")
c39, c73, ce = CM["piso_390"], CM["laje_730"], CM["escada"]
E = [Paragraph("MEMÓRIA DE CÁLCULO ND-LET-MC09 — ALTERAÇÕES DO PACOTE REV09 (23 e 24/10/2026)", T1),
     P("Obra: Letsara — pavilhão com mezanino (Marques Engenharia). Decisões do Nathan: DEC-045 (pisos +3,90 / +7,30, abertura e escada metálica, "
       "P6/P7 da escada e P6 da linha 2), DEC-046 (laje de cima: laje de cobertura do bloco, acesso apenas para manutenção), DEC-047 (vigas do mezanino retangulares protendidas com 2º estágio, sem meio vaso), "
       "DEC-048 (linha 2 sem TS-01, cobertura metálica), DEC-049 (VM 30 × 75 com dente Gerber 45 em todas as marcas) e, em 24/10, DEC-050/052 (linha 2: W 200 × 15,0 contínua nos pilares e em montantes no meio dos vãos), "
       "DEC-051 (escada interna sem solda, base BM-1), DEC-053 (escada metálica externa em L na fachada A), DEC-054 (I130 com h 120, dente Gerber e consolo com mísula), "
       "DEC-055 (2º pavimento = topo da capa +3,90, piso pronto ~+3,95: as duas escadas chegam no piso pronto com 22 espelhos de 17,95), DEC-056 (doca com piso nivelado) e DEC-057 (sem ponte rolante). "
       "Documento para análise do Nathan antes da emissão do zip com DXF e IFC."),
     Paragraph("1. Níveis e cargas do mezanino", T2),
     tab([["NÍVEL / USO", "SOBRECARGA (kN/m²)", "REVESTIMENTO (kN/m²)", "OBS."],
          ["+3,90 — 2º pavimento (depósito)", f(c39["sobrecarga"]), f(c39["revestimento"]), "5,0 confirmada pelo Nathan em 23/10/2026 (NBR 6120:2019)"],
          ["+7,30 — laje de cobertura do bloco (acesso apenas para manutenção, NBR 6120:2019 Tab. 10)", f(c73["sobrecarga"]), f(c73["revestimento"]), c73["uso"]],
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
      Paragraph("7. Escadas metálicas interna e externa (escadas_detalhe.py) — DEC-045/053/055/060", T2),
      P(f"Modelo único de detalhamento das duas escadas: peças do 3D/IFC, ligações, lista e folhas ND-LET-ES01, ES02 e ES03 saem de escadas_detalhe.py. "
        f"Sobrecarga {f(ESD['cargas']['q_kN_m2'])} kN/m²; guarda-corpo {f(ESD['cargas']['guarda_corpo_kN_m'], 2)} kN/m no topo e {f(ESD['cargas']['fechamento_kPa'], 2)} kPa no fechamento; corrimão {f(ESD['cargas']['corrimao_kN'], 2)} kN ({ESD['norma']}). "
        "Perfis no limite: para cada peça foi escolhido o mais leve da lista que passa em resistência, flecha L/350, vibração e geometria das ligações."),
      tab([["PEÇA", "PERFIL", "USO", "OBS."]] +
          [[nm, d_["perfil"], f(d_["uso"], 2), ob] for nm, d_, ob in (
              ("longarina interna", ESD["interna"]["longarina"], f"flecha {f(ESD['interna']['longarina']['flecha_mm'])} ≤ {f(ESD['interna']['longarina']['lim_mm'])} mm; U 102 não comporta a cantoneira do degrau"),
              ("VP-1 frente do patamar", ESD["interna"]["viga_patamar_frente"], f"flecha {f(ESD['interna']['viga_patamar_frente']['flecha_mm'])} ≤ {f(ESD['interna']['viga_patamar_frente']['lim_mm'])} mm"),
              ("VP-2 / VP-4 fundo (assentos SA)", ESD["interna"]["viga_patamar_fundo"], "W 150 × 9,2 é o menor W"),
              ("VP-3 frente da chegada (balanço)", ESD["interna"]["viga_chegada_frente"], f"balanço {f(ESD['interna']['viga_chegada_frente']['balanco'], 2)} m"),
              ("barrote interno", ESD["interna"]["barrote"], ""), ("pilarete da chegada (interna)", ESD["interna"]["pilarete_chegada"], f"λ {ESD['interna']['pilarete_chegada']['lambda_']}"),
              ("longarina externa (lance de cima)", ESD["externa"]["longarina_cima"], f"flecha {f(ESD['externa']['longarina_cima']['flecha_mm'])} ≤ {f(ESD['externa']['longarina_cima']['lim_mm'])} mm"),
              ("longarina externa (lance de baixo)", ESD["externa"]["longarina_baixo"], ""), ("barrote externo", ESD["externa"]["barrote"], ""),
              ("pilarete da chegada (externa)", ESD["externa"]["pilarete_chegada"], f"λ {ESD['externa']['pilarete_chegada']['lambda_']}; contraventado pelo X"),
              ("X de contraventamento (externa)", dict(perfil=ESD["externa"]["contraventamento"]["barra"], uso=ESD["externa"]["contraventamento"]["uso"]), f"Nd {f(ESD['externa']['contraventamento']['Nd'])} ≤ {f(ESD['externa']['contraventamento']['NRd'])} kN"))],
          [52, 40, 14, 72]),
      P("Guarda-corpos e corrimãos (RT CBMRS nº 11 Parte 01/2016): corrimão nos dois lados de todos os lances a 0,90 m do bocel, tubo Ø38,1, 40 mm livres, contínuo nos patamares e com 30 cm de prolongamento nas pontas livres; "
        "guarda-corpo 0,92 m nos lances internos, 1,05 m nos patamares e na abertura da laje, 1,30 m em toda a escada externa; barras verticais com vão livre < 150 mm (esfera de 15 cm)."),
      tab([["TRECHO", "LOCAL", "h (m)", "MONTANTE (uso)", "CORRIMÃO (uso)", "BARRAS", "FIXAÇÃO (uso)"]] +
          [[g["cod"], g["nome"], f(g["h"], 2), f"{g['gc']['montante']['perfil']} ({f(g['gc']['montante']['uso'], 2)})", f"{g['gc']['corrimao']['perfil']} ({f(g['gc']['corrimao']['uso'], 2)})",
            "—" if g.get("so_corrimao") else f"{g['gc']['barra']['perfil'].replace('barra redonda ', '')} c/{g['gc']['barra']['s_mm']}", f"{g['fix']} ({f(g['gc']['fixacao_montante']['uso'], 2)})"] for g in ESD["guardas"]],
          [14, 50, 11, 30, 28, 22, 23]),
      P(f"Ligações (NBR 8800:2024 6.3, todas parafusadas, sem solda): cada uma conferida automaticamente — furos dentro das duas peças, bordas (M10 18, M12 22, M16 29 mm), espaçamento ≥ 3d, folga de chave, faixa comum de altura entre as peças, corte do parafuso e pressão de contato. "
        f"{len(ESD['ligacoes'])} ligações, {ESD['n_conflitos']} conflitos; modelo 3D com 0 colisões > 3 mm (colisao_modelo.py). A trava TR-1 da escada externa (rev 00) foi retirada: não alcançava a face do P28 (x −0,55 contra −0,30, atrás das placas); a estabilidade passa ao X de barras Ø12,5 sob a chegada em 3 planos."),
      tab([["COD", "LIGAÇÃO", "PARAFUSOS / ELEMENTOS", "Vd / VRd (kN)", "USO"]] +
          [[l["cod"], l["tipo"], l["furos"], f"{f(l['Vd'], 1)} / {f(l['VRd'], 1)}", f(l["uso"], 2)] for l in ESD["ligacoes"]],
          [18, 34, 86, 24, 14]),
      P("Pé-direito livre (≥ 2,10 m): " + "; ".join(f"{q['faixa']} {f(q['pe_direito_min_m'], 2) + ' m' if q['pe_direito_min_m'] else 'livre'}" for q in ESD["pe_direito"]) + "."),
      P(f"Massa: escada interna {f(ESD['massa_kg']['interna'] * 1.03, 0)} kg e externa {f(ESD['massa_kg']['externa'] * 1.03, 0)} kg (com 3 % de parafusos; sem as ombreiras OM-2)."),
      Paragraph("10. Vigas centrais I130 h 120 com cordoalha Ø12,7 (calc_i110_r01.py, calc_dentes.py) — DEC-054/058", T2),
      P("Eixo C no arranjo C (DEC-058): P20 na linha 4, P22 (antes P13) em y 46,317 e pilar novo P23 em y 62,833 — três vãos iguais de 16,517 m; as três I130 novas (V401, V402 e V403) são uma só marca de fôrma e de armação, e a V400 (20,15 m) segue igual. "
        "h 120, dente Gerber 78 × 35, consolo com mísula, protensão LIMITADA (ELS-D na quase permanente com margem de −0,25 MPa, ELS-F na frequente), C50, liberação só com fckj 50 MPa, cordoalha Ø12,7 CP-190 RB. "
        "Busca automática: para cada marca, os arranjos candidatos × os 4 padrões de isolamento escalonado (linha de baixo sempre aderente); adotado o que passa em tudo (ELU, ELS-D, ELS-F, ato, flecha, içamento e dente) com MENOS cordoalha."),
      tab([["VIGA", "L (m)", "Ø12,7", "padrão de isolamento (mm)", "Md / MRd (kN·m)", "σ ELS-D (MPa)", "σ ELS-F (MPa)", "ato topo / base (MPa)", "flecha final (mm)", "Fd dente (kN)"]] +
          [[f"{NOME_I[mk]}", f(I1[mk]["L_peca"], 2), str(I1[mk]["arranjo"]["n_cord"]), " / ".join(str(v) for v in I1[mk]["isolamento_padrao"]), f"{f(I1[mk]['ELU']['Md'], 0)} / {f(I1[mk]['ELU']['MRd'], 0)}",
            f(I1[mk]["ELS"]["D_base"], 2), f"{f(I1[mk]['ELS']['F_base'], 2)} ≤ {f(I1[mk]['ELS']['lim_F'], 2)}",
            f"{f(I1[mk]['ato']['topo_max'], 2)} / {f(I1[mk]['ato']['base_min'], 2)}", f"{f(I1[mk]['flecha']['final_mm'])} ≤ {f(I1[mk]['flecha']['lim_mm'])}", f(I1[mk]["dente"]["Fd"])]
           for mk in ("V407", "V406", "V405", "V404")], [14, 11, 11, 26, 22, 15, 18, 20, 20, 15]),
      P("Isolamento por linha (bainha plástica de PEAD vedada nas pontas com fita e mastique, medida a partir da FACE DA PEÇA; a linha de baixo é sempre aderente):"),
      tab([["VIGA", "linha y (cm)", "cordoalhas", "isoladas", "isolado em cada ponta (cm, da face)", "lbpt (cm)", "ato no fim do isolamento topo / base (MPa)"]] +
          [[NOME_I[mk], f(ln_["y"] / 10, 0), str(len(ln_["xs"])), str(len(ln_["xs"]) if ln_["isol"] else 0), f((ln_["isol"] + 350) / 10, 0) if ln_["isol"] else "aderente",
            f(I1[mk]["ato"]["lbpt_m"] * 100, 1),
            next((f"{f(c_['topo'], 2)} / {f(c_['base'], 2)}" for k_, c_ in I1[mk]["ato"]["controle"].items() if "isolamento" in k_ and f"de {round(ln_['isol'] / 1000)} m" in k_), "—") if ln_["isol"] else "—"]
           for mk in ("V407", "V405") for ln_ in I1[mk]["arranjo"]["linhas"]], [14, 18, 18, 16, 38, 16, 50]),
      P(f"V401, V402 e V403 têm o mesmo arranjo (marca única). Limites do ato com fckj 50: tração {f(I1['V405']['ato']['lim_t'], 3)} MPa (resistida pela armadura N3 da mesa) e compressão {f(I1['V405']['ato']['lim_c'], 0)} MPa; "
        f"os pontos de controle são o fim do lbpt na ponta e o fim de cada trecho isolado + lbpt. Força no macaco {f(I1['V405']['arranjo']['F_macaco_kN'], 1)} kN por cordoalha (σpi {f(I1['V405']['arranjo']['sig_pi'], 0)} MPa); "
        f"perdas totais {f(I1['V405']['perdas']['perda_total_pct'], 1)} %."),
      P(f"Dente (NBR 9062:2017 7.4, Fd = {f(I1['V405']['dente']['Fd'])} kN com γn 1,1, Hd = {f(I1['V405']['dente']['Hd'])} kN, reação real da V402, a mais carregada): {DI['calculo']['adotado']['tirante']}; {DI['calculo']['adotado']['suspensao']}; {DI['calculo']['adotado']['costura']}. "
        + (f"MEF não linear (mef_dente.analisar com a armação da prancha e as cordoalhas Ø12,7, passo de deslocamento 0,02 mm): Vu = {f(DI['mef']['Vu_kN'])} kN, FS = Vu/Fd = {f(DI['mef']['FS'], 2)} ≥ 1,06 ({ok(DI['mef']['ok'])})."
           if DI.get("mef") else "MEF: ver estudo_i130_h120_mef.json.")),
      P(f"Cordoalha total das 4 I130: {f(sum(I1[mk]['arranjo']['n_cord'] for mk in I1) * 0.792 * 0 + sum(I1[mk]['arranjo']['n_cord'] * I1[mk]['L_peca'] for mk in I1) * 0.792, 0)} kg (comprimento das peças; a pista de 60 m entra no consumo da fábrica)."),
      P(f"Consolo CP-I130 com MÍSULA de concreto (NBR 9062:2017 7.3): {f(CO['CP-I130']['b_m'] * 100, 0)} × {f(CO['CP-I130']['proj_m'] * 100, 0)}, h {f(CO['CP-I130']['h_total_m'] * 100, 0)} junto ao pilar e {f(CO['CP-I130']['h_consolo_m'] * 100, 0)} na ponta "
        f"(fundo da ponta alinhado ao fundo da viga +6,576; ponta ≥ h/2), a/d {f(CO['CP-I130']['a_d'], 2)} ({CO['CP-I130']['tipo']}), Fd {f(CO['CP-I130']['Fd_kN'])} kN: τwd {f(CO['CP-I130']['tau_wd_MPa'], 2)} ≤ {f(CO['CP-I130']['tau_wu_MPa'], 2)} MPa "
        f"(na seção da carga, com a altura reduzida pela mísula: {f(N9C['tau_carga_MPa'], 2)} MPa); tirante {CO['CP-I130']['tirante']} (As {f(CO['CP-I130']['As_tir_cm2'], 2)} cm², uso {f(CO['CP-I130']['As_tir_cm2'] / 16.09, 2)}). "
        "Pilares PC-01, PC-02, PC-03 (P22 e P23) e PF-04 com o consolo novo; assento +6,966 inalterado."),
      Paragraph("8. Pilares novos e cargas na fundação (tf, 1 tf = 10 kN)", T2)]
lin = [["PILAR", "Nk G + Q", "Nd máx", "Nd mín", "Md res máx (tf·m)", "Hd máx"]]
for nm, nn in (("P6E", "P6 da escada (PE-01)"), ("P7E", "P7 da escada (PE-02)"), ("P6-L2", "P6 da linha 2 (PE-03)"), ("P13", "P22 — PC-03 (y 46,317)"), ("P13B", "P23 — PC-03 novo (y 62,833)")):
    d = CF["pilares"][nm]
    lin.append([nn, f((d["G"]["N"] + d["Q"]["N"]) / 10), f(d["ELU"]["Nd_max"] / 10), f(d["ELU"]["Nd_min"] / 10), f(d["ELU"]["Md_res_max"] / 10), f(d["ELU"]["Hd_max"] / 10)])
pc3 = DP["PC-03"]
E += [tab(lin, [46, 22, 22, 22, 32, 20]),
      P(f"PC-03 40 × 40 (P22 e P23): {pc3['n']} Ø{f(pc3['d'], 0)} (As {f(pc3['As_cm2'], 2)} cm², barras ≤ Ø20), uso da seção {f(pc3['uso_secao'], 3)} no método geral com 2ª ordem (dimensionar_pilares_r05.py), λ/λ1 {f(pc3['lambda_u'], 2)}; "
        f"manuseio: " + "; ".join(f"{m_['caso']} uso {f(m_['uso'], 2)}" for m_ in pc3["manuseio"]) + "."),
      P("Modelo global r05 (modelo_integrado_r05.py) revisto nesta emissão: (1) I130 como vãos simplesmente apoiados (antes cadeia contínua, que subestimava o P22); (2) montantes da linha 2 (DEC-052) incluídos; "
        "(3) a combinação com G favorável só tira painéis e instalações quando há vento (antes valia também nos casos característicos e reduzia as cargas da CG01). Cargas de todos os pilares na ND-LET-CG01, em tf."),
      Paragraph("11. Portões da linha 4 — opção A (calc_portao_l4.py) — DEC-059", T2),
      P("Os PG-01 a PG-04 passam a APOIAR a TS-01A (neoprene + graute depois da montagem): a viga fica contínua sobre os PG para g2 + q e o fundo no vão do portão fica em +7,50 (portões 500 × 750 livres). "
        "Sobre o portão PG-04–PG-03 (P19–D), placa PV-1 10 × 37 de +7,50 a +7,88 apoiada nas cantoneiras CL-V das faces dos PG (folha ND-LET-PV01)."),
      tab([["TRECHO", "Md neg / MRd (kN·m)", "uso", "σ topo sobre o PG (MPa, rara)", "reações Rd (kN)"]] +
          [[k, f"{f(v['Md_neg_kNm'])} / {f(v['MRd_neg_kNm'])}", f(v["uso_neg"], 3), " / ".join(f(x, 3) for x in v["sig_topo_PG_rara_MPa"]) + f" ≤ {f(v['lim_F_MPa'], 2)}",
            "; ".join(f"{r['pg']} {f(r['Rd'])}" for r in v["reacoes"])] for k, v in PJ["ts01a"].items()], [30, 34, 14, 50, 50]),
      tab([["PILAR", "Nd (tf)", "λ", "uso N", "neoprene", "σ (MPa)"]] +
          [[k, f(v["Nd_tf"]), f(v["lambda_"], 1), f(v["uso_N"], 3), PJ["neoprene"][k]["dim_mm"], f(PJ["neoprene"][k]["sigma_MPa"], 2)] for k, v in PJ["pilares"].items()], [24, 20, 16, 18, 40, 20]),
      P("As reações dos PG entram nas cargas da fundação (calc_cargas_fundacao.somar_portoes) e na CG01."),
      Paragraph("9. Pendências e observações", T2),
      P("(a) Zip com DXF e IFC só depois da aprovação deste pacote (PDF). (b) Confirmar com a sondagem a σ adotada de 150 kPa nos blocos BE-1/BE-2 da escada externa. "
        "(c) Conferir no catálogo do fornecedor o chumbador químico M10 hef 70 dos guarda-corpos da laje (GI-10/GI-11). (d) Fretagem da zona de transferência do dente conforme item 4.")]
doc.build(E)
print("ok", SAI)
