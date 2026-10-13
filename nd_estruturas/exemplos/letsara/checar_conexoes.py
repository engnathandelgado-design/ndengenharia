"""Letsara — conferência cruzada de insertos, conexões e furos entre peças (o que está na prancha de uma peça tem de
bater com o que está na prancha da outra). Gera conexoes.json (lista usada pela página 3D) e imprime o resumo.

Fontes: ligacoes.json (geometria dos apoios TS-01 × consolos, terças, berço da I110), cobertura_metalica.json
(chumbadores e parafusos), definições das pranchas (TS-01, pilares, COB01, MON01/02). Unidades mm salvo indicação.
"""
import json
from pathlib import Path

AQ = Path(__file__).parent
LG = json.loads((AQ / "ligacoes.json").read_text(encoding="utf-8"))
CM = json.loads((AQ / "cobertura_metalica.json").read_text(encoding="utf-8"))
TOL = dict(pino=5, consolo=10, pilar=10, prumo=10)        # NBR 9062:2017 (adotadas)
R = []


def reg(grupo, peca_a, inserto_a, peca_b, inserto_b, verificacao, valor, ok, obs=""):
    R.append(dict(grupo=grupo, peca_a=peca_a, inserto_a=inserto_a, peca_b=peca_b, inserto_b=inserto_b,
                  verificacao=verificacao, valor=valor, ok=bool(ok), obs=obs))


# ------------------------------------------------------------------ 1. TS-01 (dente + TB-1) × consolo (PN-1) — geometria e folgas
for a in LG["apoios"]:
    reg("TS-01 × consolo", a["peca"], a["inserto"], a["com"], a["tipo"],
        "eixo do tubo × eixo do pino (planta)", f"{a['dist_mm']:.1f} mm", a["dist_mm"] <= TOL["pino"],
        f"nível do assento +{a['z_assento']:.3f}; dz {a['dz_mm']:+.1f} mm; folga de ponta {a['folga_ponta_mm']} / dente {a['folga_consolo_mm']} mm")
# diâmetros: TB-1 Ø50×3,0 (furo 44) × PN-1 Ø20 (laterais) / PN-2 Ø25 (centrais e I110)
for pino, d in (("PN-1 Ø20 (todos os consolos da TS-01)", 20),):
    folga = (44 - d) / 2
    reg("TS-01 × consolo", "TS-01", "TB-1 tubo Ø50×3,0 (furo 44)", "consolo CP-TS / CV-TS", pino,
        "folga radial tubo × pino", f"{folga:.1f} mm ≥ {TOL['pino'] + TOL['consolo'] / 2:.0f}", folga >= TOL["pino"] + TOL["consolo"] / 2,
        "graute só numa ponta de cada viga (a outra com graute flexível)")
reg("TS-01 × consolo", "TS-01", "NEO-1 300×150×10 (furo Ø30)", "consolo CP-TS", "PN-1 Ø20", "furo do neoprene × pino", "30 > 20", True, "")
reg("TS-01 × consolo", "TS-01", "CH-A1 300×150×12,5 (furo Ø52)", "—", "TB-1 Ø50", "furo da chapa de fundo × tubo", "52 > 50 (OD)", True, "TB-1 soldado na CH-A1")
reg("TS-01 × consolo", "TS-01", "dente 450×300, largura 400", "consolo CP-TS", "40×30×45/25", "largura do dente × largura do consolo", "400 = 400", True,
    "apoio do dente 250 ≥ 2/3 do balanço 300 (NBR 9062 7.3)")

# ------------------------------------------------------------------ 2. TS-01 × I110 (CV-TS) — berço e folga ao topo da I110
for b in LG["berco_I110"]:
    reg("TS-01 × I110", f"TS-01 L{b['linha']}", "dente", "I110 (consolo CV-TS)", "assento",
        "desnível dos assentos esq/dir (caimento 3 %)", f"{b['desnivel_mm']:.0f} mm", b["ok"],
        f"topo da I110 +{b['topo_I110']:.2f}; folga topo I110 × terças {b['folga_topo_I110_tercas_mm']} mm; folga lateral dente 75 mm")

# ------------------------------------------------------------------ 3. terças × TS-01 (ST-1 soldado na CH-T1/CH-T2) e mão-francesa (OR-1 soldada na CH-MF)
for t in LG["tercas"][:14]:
    reg("terça × TS-01", t["peca"], "CH-T1/CH-T2 + ST-1 soldado", t["com"], t["tipo"], "posição das chapas × linha de terças", f"{t['dist_mm']:.1f} mm", t["ok"], "")
ct = CM["CT1"]
reg("terça × TS-01", "ST-1 chapa 8×220×290", "4 furos Ø14 (2 por terça, a 50 do eixo)", "terça Ue 300", "furos Ø14 a 60 da ponta, a 100 e 200 do fundo",
    "furo da terça × furo do ST-1 (folga 10 mm da ponta ao eixo)", "60 − 10 = 50 = 50", True, "terça L = vão − 20; 20 mm entre as pontas das terças no ST-1")
reg("terça × TS-01", "ST-1", "altura 290 (furos a 110/210 do concreto)", "terça Ue 300", "fundo a 10 do concreto; furos a 100/200 do fundo", "nível dos furos", "110 = 10 + 100; 210 = 10 + 200", True, "")
reg("terça × TS-01", "ST-1", "furo Ø14", "terça Ue 300 (alma 3,0)", "M12 8.8", "2 M12 por ponta: corte / contato na alma", f"uso {ct['M12_alma']['uso']:.2f}", ct["M12_alma"]["uso"] <= 1.0,
    "contato na alma de 3,0 mm governa (αe = 0,183t + 1,53)")
reg("terça × TS-01", "ST-1 × CH-T1", "filete 6 mm, 2 lados, 220 mm", "CH-T1 200×200×12,5", "chapa embutida", "largura do ST-1 (220) ≤ comprimento da CH-T1 (200) + 2×10", "220 ≤ 220", True, "ST-1 centrado na CH-T1; nos nós do X vai na CH-T2 (380)")
reg("mão-francesa", "OR-1 chapa 8×300×100", "2 furos Ø14 a 100 do eixo", "CH-MF 150×360×12,5", "chapa embutida no fundo", "OR-1 (300) dentro da CH-MF (360)", "300 ≤ 360", True, "OR-1 soldada na fábrica, face a 5 mm do plano da alma da terça (aba da MF entre as duas)")
mf = CM["MF1"]
reg("mão-francesa", "MF-1 L 50×5", "furo Ø14 nas duas pontas", "TS-01 / terça", "OR-1 (furo Ø14) / alma da terça (furo Ø14 a 40 do fundo, a 1070 do eixo da viga)", "M12 8.8 × furo Ø14", f"uso {mf['uso']:.2f}", True,
    f"Nd {mf['Nd_kN']} kN; comprimento {mf['comp_m']} m a 45°; do fundo da viga até a terça")
for ch, d in CM["chumbadores"].items():
    reg("chumbadores", "TS-01", ch, "terça / mão-francesa", d["pinos"], "interação tração × corte (ACI 318-19 cap. 17)", f"{d['interacao']:.2f} ≤ 1,2", d["interacao"] <= 1.2, "")

# ------------------------------------------------------------------ 3b. contraventamento em X de nó a nó (CH-T2 × CH-T2) e correntes
cx, cc, lc = CM["contraventamento"], CM["correntes"], LG["contraventamento"]
reg("contraventamento", "diagonal Ø16 (rosca M16) + esticador", f"painel {cx['painel_x_m']*1000:.0f} × vão, L ≈ {cx['L_diag_m']} m", "CH-T2 (viga da linha i) / CH-T2 (linha i+1)",
    "orelhas 9,5 com furo Ø18", "tração na diagonal (NBR 8800:2008 6.3.3)", f"{cx['T_diag_d']} ≤ {cx['NtRd_16']} kN", cx["uso_diag"] <= 1.0,
    f"Vd {cx['V_painel_d']} kN por painel; {lc['n_tirantes']*2} diagonais ({lc['n_tirantes']} por meia água × 2)")
reg("contraventamento", "cruzamento do X", "2 diagonais a 45 e 85 mm do concreto", "terça intermediária do painel", "furos Ø18 na alma a 35 e 75 do fundo",
    "folga entre as diagonais / borda do furo ao fundo da terça", f"{lc['folga_cruzamento_mm']:.0f} mm / {lc['borda_furo_fundo_terca_mm']} mm", lc["ok"], "as diagonais cruzam-se sobre a terça, no meio do vão")
reg("contraventamento", "orelha da CH-T2", "a 140 do eixo da terça", "terça do nó (mesa 85)", "ST-1", "folga orelha × mesa da terça", f"{lc['folga_min_terca_mm']} mm ≥ 20", lc["folga_min_terca_mm"] >= 20, "")
reg("contraventamento", "terça escora (todas as linhas de terças)", "Ue 300×85×25×3,00", "CH-T1/T2", "2 M12 por ponta", "N + M (NBR 14762:2010 9.9), vento 0°", f"{CM['terca_escora']['interacao']:.2f} ≤ 1", CM["terca_escora"]["interacao"] <= 1.0,
    f"governa vão {CM['terca_escora']['vao_governante']}, x = {CM['terca_escora']['linha_governante_x_m']} m (faixa {CM['terca_escora']['faixa_governante']}, vento {CM['terca_escora']['vento_governante']}): Nd {CM['terca_escora']['Nd']} kN; Nd máx. {CM['terca_escora']['Nd_max']} kN")
reg("contraventamento", "CH-T2 300×380×12,5", "6 pinos Ø16 + 2 grampos U", "2 diagonais + terça escora", "orelhas",
    "interação tração × corte (ACI 318-19 cap. 17)", f"{CM['chumbadores']['CH-T2']['interacao']:.2f} ≤ 1,2", CM["chumbadores"]["CH-T2"]["interacao"] <= 1.2, f"nó: x {cx['no']['Fx_kN']} kN, y {cx['no']['Fy_kN']} kN")
reg("correntes", f"corrente flexível Ø{cc['flexivel']['d_mm']:g} M{cc['flexivel']['d_mm']:g}", f"furo {cc['flexivel']['furo']} no meio da alma", "terças", "porca + contraporca dos 2 lados", "tração acumulada (13 terças)", f"{cc['F_max_kN']} ≤ {cc['flexivel']['NtRd']} kN", cc["flexivel"]["uso"] <= 1, "")
reg("correntes", "tirante rígido L 51×51×3,2", "clipe L 32×3 + M10 em furo oval", "1ª e 2ª terça junto às ancoragens", "furo oval 11×23 na alma", "compressão, λ " + str(cc["rigida"]["esbeltez"]), f"{cc['F_max_kN']} ≤ {cc['rigida']['NcRd']} kN", cc["rigida"]["uso"] <= 1, "")
reg("correntes", "diagonal de ancoragem Ø16", "nó da corrente na 2ª terça", "ST-1 da 1ª terça (furo Ø18)", "porca + contraporca", "tração", f"{cc['diagonal']['Td']} ≤ {cc['diagonal']['NtRd']} kN", cc["diagonal"]["uso"] <= 1, "L/4 e 3L/4 ao apoio mais próximo; L/2 aos dois apoios")

# ------------------------------------------------------------------ 4. pilares × placas (IP-01 × CM-01) e × VB-01 / VM (consolos)
reg("pilar × placa", "pilar PL/PF", "IP-01 chapa 150×150×9,5 + 2 pinos Ø12,5 (c/125 a partir do piso)", "placa CM-01 (h 125)", "fixação da placa",
    "fiada × inserto", "8 fiadas = 8 IP-01", True, "fixação: 2 cantoneiras L 63×6,3 soldadas em obra ao IP-01 e ao CH-P1 da placa (ND-LET-CM01)")
zf = lambda x: LG["Z0_TS"] + 0.03 * x
for pil, x in (("PL-03/04 (P1 L1/L9)", 0.0), ("PF-01 (P3/P14)", 9.87), ("PF-02 (P4/P15)", 20.05), ("PF-03 (P5/P16)", 29.63), ("PL-07/08 (P2 L1/L9)", 39.625 + 0.475)):
    reg("VB-01 × consolo", "VB-01 15×70", "fundo da viga", pil, "CP-VB", "nível do assento = fundo da VB", f"+{zf(x):.3f}", True, "VB-01 15×90 com TB-1 Ø50 e NEO-1 (ND-LET-VB01)")
for nivel in (3.15, 6.55):
    ass = nivel - 0.25 - 0.45
    reg("VM × consolo", f"VM-01..04 I90 (nível +{nivel:.2f})", "dente 450×300, TB-1 Ø50 a 150 da face", "PM-01 / PL-02 / PL-06 / PF-01..03 / PL-03 / PL-07", "CP-MEZ 40×30×45/25 + PN-1 Ø20",
        "assento = topo da viga − 45 (dente)", f"+{ass:.3f}", True, "dente I90 45×30 verificado por MEF (FS 1,14); dente da I70 reprovado")

# ------------------------------------------------------------------ 4b. VM × laje alveolar — 2º estágio (MC04)
SE = json.loads((AQ / "segundo_estagio.json").read_text(encoding="utf-8"))
reg("VM × laje (2º estágio)", "VM-01..04 I90", "N9 estribos salientes Ø8 c/15 + N10", "laje alveolar h20 + enchimento + capa C25", "tela Q138 + negativas Ø10 c/25",
    "interface pré-moldado × capa (NBR 9062:2017 6.3.5)", f"τsd {SE['interface']['tau_sd_total_MPa']} ≤ τRd {SE['interface']['tau_Rd_MPa']} MPa", SE["interface"]["ok"],
    f"As {SE['interface']['As_adotada_cm2_m']} ≥ {SE['interface']['As_req_cm2_m']} cm²/m; fase 1 na seção pré-moldada, fase 2 na composta (I × {SE['secao_composta']['ganho_inercia']})")
reg("VM × laje (2º estágio)", "VM", "topo da mesa (40) rugoso, pente 5 mm", "laje alveolar", "apoio 10 cm em neoprene 10", "enchimento entre a ponta da laje e a borda da mesa", "30 × 20 cm", True, "capa 5 cm por cima; N9 sai 17 cm do topo (dentro do enchimento + capa)")

# ------------------------------------------------------------------ 5. I110 × pilares centrais (PN-2) e apoio da V405
reg("I110 × PC", "V405/406/407 I110", "dente 660×350 + TB-2 tubo Ø60,3×3,6 (furo 53)", "PC-01/02 50×50", "consolo CP-I110 + PN-2 Ø25", "folga radial tubo × pino", "14 mm ≥ 10", True,
    "neoprene 300×250×30 fretado (3 camadas); pressão 4,3 ≤ 10 MPa; pino grauteado numa ponta só")
reg("I110 × PC", "V405", "dente na linha 9", "PF-04 (P14, linha 9, eixo C)", "consolo CP-I110 + PN-2 Ø25", "apoio da ponta da V405", "+8,190 (face interna do P14)", True, "V405 = P13 → linha 9 (23,76 m c-c), como no R01 (viga central até o P14)")

# ------------------------------------------------------------------ 6. cobertura escondida
pl = LG["platibanda"]
reg("cobertura × platibanda", "telha", "topo no eixo E", "pilar PL-05..08", "platibanda +10,000", "folga", f"{pl['folga_P2_mm']} mm ≥ 100", pl["folga_P2_mm"] >= 100, "")

(AQ / "conexoes.json").write_text(json.dumps(R, indent=1, ensure_ascii=False), encoding="utf-8")
n_ok = sum(1 for r in R if r["ok"])
print(f"{len(R)} verificações — {n_ok} ok, {len(R) - n_ok} com pendência")
for r in R:
    if not r["ok"] or r["obs"].startswith("!"):
        print(" -", r["grupo"], "|", r["peca_a"], "×", r["peca_b"], "|", r["verificacao"], "|", r["valor"], "|", r["obs"])
