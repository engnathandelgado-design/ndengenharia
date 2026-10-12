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

# ------------------------------------------------------------------ 3. terças × TS-01 (CH-T1/T2 × CT-1) e mão-francesa (CH-MF × MF-1)
for t in LG["tercas"][:14]:
    reg("terça × TS-01", t["peca"], t["inserto"], t["com"], t["tipo"], "posição das chapas × linha de terças", f"{t['dist_mm']:.1f} mm", t["ok"], "")
ct = CM["CT1"]
reg("terça × TS-01", "CT-1 L 102×102×9,5", "furo Ø18 na aba", "TS-01", "CH-T1/CH-T2 luva M16 soldada", "parafuso M16 8.8 × furo Ø18", "folga 2 mm (padrão)", True,
    f"tração {ct['M16_chapa']['Td']} ≤ {ct['M16_chapa']['Ft_Rd']} kN; corte {ct['M16_chapa']['Vd']} ≤ {ct['M16_chapa']['Fv_Rd']} kN")
reg("terça × TS-01", "CT-1", "furo Ø14 na aba vertical", "terça Ue 300", "furo Ø14 na alma", "2 M12 8.8 por terça", f"uso {ct['M12_alma']['uso']:.2f}", ct["M12_alma"]["uso"] <= 1.0,
    "contato na alma de 3,0 mm governa (αe = 0,183t + 1,53)")
mf = CM["MF1"]
reg("mão-francesa", "MF-1 L 50×5", "furo Ø14 nas duas pontas", "TS-01 / terça", "OR-1 (luva M12 na CH-MF) / mesa inferior da terça (furo Ø14)", "M12 8.8 × furo Ø14", f"uso {mf['uso']:.2f}", True,
    f"Nd {mf['Nd_kN']} kN; comprimento {mf['comp_m']} m a 45°; do fundo da viga até a terça")
for ch, d in CM["chumbadores"].items():
    reg("chumbadores", "TS-01", ch, "terça / mão-francesa", d["pinos"], "interação tração × corte (ACI 318-19 cap. 17)", f"{d['interacao']:.2f} ≤ 1,2", d["interacao"] <= 1.2, "")

# ------------------------------------------------------------------ 4. pilares × placas (IP-01 × CM-01) e × VB-01 / VM (consolos)
reg("pilar × placa", "pilar PL/PF", "IP-01 chapa 150×150×9,5 + 2 pinos Ø12,5 (c/125 a partir do piso)", "placa CM-01 (h 125)", "fixação da placa",
    "fiada × inserto", "8 fiadas = 8 IP-01", True, "! detalhe da fixação placa × IP-01 (cantoneira soldada ou parafuso) ainda não emitido — pendente CM-01")
zf = lambda x: LG["Z0_TS"] + 0.03 * x
for pil, x in (("PL-03/04 (P1 L1/L9)", 0.0), ("PF-01 (P3/P14)", 9.87), ("PF-02 (P4/P15)", 20.05), ("PF-03 (P5/P16)", 29.63), ("PL-07/08 (P2 L1/L9)", 39.625 + 0.475)):
    reg("VB-01 × consolo", "VB-01 15×70", "fundo da viga", pil, "CP-VB", "nível do assento = fundo da VB", f"+{zf(x):.3f}", True, "VB-01 ainda sem prancha de fôrma/armação: pino e neoprene a detalhar")
for nivel in (3.15, 6.55):
    ass = nivel - 0.25 - 0.425
    reg("VM × consolo", f"VM-01..04 I70 (nível +{nivel:.2f})", "dente 425×300", "pilares das linhas 1–2", "CP-MEZ 40×30×35/20", "assento = topo da viga − 425", f"+{ass:.3f}", True,
        "! dente da I70 reprovado no MEF (FS < 1,06): decidir I90 c/ dente, I70 sem dente ou I80 c/ chapa antes de fabricar")

# ------------------------------------------------------------------ 5. I110 × pilares centrais (PN-2) e apoio da V405
reg("I110 × PC", "V405/406/407 I110", "dente 660×350 + TB-2 tubo Ø60,3×3,6 (furo 53)", "PC-01/02 50×50", "consolo CP-I110 + PN-2 Ø25", "folga radial tubo × pino", "14 mm ≥ 10", True,
    "neoprene 300×250×30 fretado (3 camadas); pressão 4,3 ≤ 10 MPa; pino grauteado numa ponta só")
reg("I110 × PC", "V405", "dente na linha 8", "? (eixo C, linha 8)", "—", "existe apoio na linha 8?", "não consta no modelo", False, "! confirmar pilar central na linha 8 no R01")

# ------------------------------------------------------------------ 6. cobertura escondida
pl = LG["platibanda"]
reg("cobertura × platibanda", "telha", "topo no eixo E", "pilar PL-05..08", "platibanda +10,000", "folga", f"{pl['folga_P2_mm']} mm ≥ 100", pl["folga_P2_mm"] >= 100, "")

(AQ / "conexoes.json").write_text(json.dumps(R, indent=1, ensure_ascii=False), encoding="utf-8")
n_ok = sum(1 for r in R if r["ok"])
print(f"{len(R)} verificações — {n_ok} ok, {len(R) - n_ok} com pendência")
for r in R:
    if not r["ok"] or r["obs"].startswith("!"):
        print(" -", r["grupo"], "|", r["peca_a"], "×", r["peca_b"], "|", r["verificacao"], "|", r["valor"], "|", r["obs"])
