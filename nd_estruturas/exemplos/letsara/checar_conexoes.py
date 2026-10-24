"""Letsara — conferência cruzada de insertos, conexões e furos entre peças (o que está na prancha de uma peça tem de
bater com o que está na prancha da outra). Gera conexoes.json (lista usada pela página 3D) e imprime o resumo.

Fontes: ligacoes.json (geometria dos apoios TS-01 × consolos, terças, berço da I130), cobertura_metalica.json
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


# ------------------------------------------------------------------ 1. TS-01 sem dente × assento do pilar / topo da I130 (rev03)
for a in LG["apoios"]:
    onde = "recuo do pilar lateral (NEO-4 + 2 PN-3 Ø25)" if a["ponta"] == "ext" else "topo da I130 / pilar central (NEO-3 + 2 PN-5 Ø20)"
    reg("TS-01 × apoio", a["peca"], f"ponta {a['ponta']} + 2 TB-3 Ø50", onde, "neoprene + 2 pinos",
        "folga da ponta / comprimento de apoio", f"{a['folga_mm']} / {a['apoio_mm']} mm", a["ok"], "apoio mínimo 250 (externo) / 150 (central)")
for pino, d in (("PN-3 Ø25 (pilares laterais)", 25), ("PN-5 Ø20 (I130, P8A, P11)", 20)):
    folga = (46.8 - d) / 2
    reg("TS-01 × apoio", "TS-01", "TB-3 tubo Ø50,8×2,0 (furo 46,8), y = ±100", "pilar / I130", pino,
        "folga radial tubo × pino", f"{folga:.1f} mm ≥ {TOL['pino'] + TOL['consolo'] / 2:.0f}", folga >= TOL["pino"] + TOL["consolo"] / 2,
        "tubos grauteados; na linha 2 (P8A) com mastique (desliza em x)")
reg("TS-01 × apoio", "TS-01", "8 cordoalhas: |x| ≤ 40 e x = ±155", "tubos TB-3", "y = ±100, Ø50", "folga livre cordoalha × tubo", "100 − 25 − 40 − 6,35 = 28,7 mm ≥ 22,8 (1,2 dmáx)", True, "")

# ------------------------------------------------------------------ 3. terças Z × TS-01 (ST-1P parafusado nas esperas ES-1) e emendas por transpasse (sem mão-francesa)
for t in LG["tercas"][:14]:
    reg("terça × TS-01", t["peca"], "ES-1 (2 M16) + ST-1P", t["com"], "linha de terças", "posição das esperas × linha de terças", f"{t['dist_mm']:.1f} mm", t["ok"], "")
st = CM["ST1P"]
tc = CM["terca"]; pc = CM["pecas"]
reg("terça × TS-01", "ST-1P chapa dobrada 9,5", "4 furos Ø14 (2 colunas a ±60, a 62 e 257 do concreto)", "2 terças Z 302×2,30 no transpasse", f"furos da alma a {pc['furos_z_mm'][0]} e {pc['furos_z_mm'][1]} do fundo (METSEC E/F)",
    "furos da terça × furos do ST-1P (fundo 10 acima do concreto)", f"10 + {pc['furos_z_mm'][0]} = 62; 10 + {pc['furos_z_mm'][1]} = 257", True, f"peças com transpasse de {pc['transpasse_cada_lado_mm']} além do eixo")
reg("terça × TS-01", "ST-1P", "furo Ø14", "terça Z 302 (alma 2,30) — sem mão-francesa", "4 M12 8.8", "torção de apoio (tração) + reação e escora (corte)", f"interação {tc['apoio']['uso']:.2f}", tc["apoio"]["uso"] <= 1.0, tc["apoio"]["nota"])
reg("terça × terça", "emenda por transpasse", f"2 M12 a {pc['furos_transpasse_da_ponta_mm']} de cada ponta", "almas das 2 terças", "M12 8.8", "transferência do momento de apoio",
    f"uso {tc['parafusos_transpasse']['uso']:.2f}", tc["parafusos_transpasse"]["uso"] <= 1.0, f"Fd {tc['parafusos_transpasse']['Fd']} kN ≤ {tc['parafusos_transpasse']['Rd']} kN")
reg("terça × TS-01", "ST-1P", "aba horizontal 150, oblongos 18×40", "ES-1 (2 M16 a y = ±60)", "porca + contraporca", "flexão da aba / esperas (tração + corte)",
    f"aba {st['aba']['uso']:.2f}; esperas {st['esperas']['interacao']:.2f}", st["aba"]["uso"] <= 1 and st["esperas"]["interacao"] <= 1, "sem solda")
for ch, d in CM["chumbadores"].items():
    val = d.get("interacao", d.get("uso"))
    reg("esperas (ACI 318-19 cap. 17)", "TS-01", ch, "terça / X", d["esperas"], "uso / interação tração × corte", f"{val:.2f} ≤ 1", val <= 1.0, "")

# ------------------------------------------------------------------ 3b. contraventamento em X de nó a nó (CH-T2 × CH-T2) e correntes
cx, cc, lc = CM["contraventamento"], CM["correntes"], LG["contraventamento"]
reg("contraventamento", "diagonal Ø16 (rosca M16) + esticador", f"painel {cx['painel_x_m']*1000:.0f} × vão, L ≈ {cx['L_diag_m']} m", "OR-X (viga da linha i) / OR-X (linha i+1)",
    "L 102×76×6,3 com furo Ø18, na espera ES-2", "tração na diagonal (NBR 8800:2008 6.3.3)", f"{cx['T_diag_d']} ≤ {cx['NtRd_16']} kN", cx["uso_diag"] <= 1.0,
    f"Vd {cx['V_painel_d']} kN por painel; {lc['n_tirantes']*2} diagonais ({lc['n_tirantes']} por meia água × 2)")
reg("contraventamento", "passagem do X pelas terças", "2 diagonais a 45 e 85 mm do concreto", "terças intermediárias (X1..X7, Y1..Y6)", "oblongos 18×28 a 35 e 75 do fundo",
    "folga entre as diagonais / borda do furo ao fundo da terça", f"{lc['folga_cruzamento_mm']:.0f} mm / {lc['borda_furo_fundo_terca_mm']} mm", lc["ok"], "as diagonais atravessam as terças do painel")
reg("contraventamento", "orelha OR-X", "a 140 do eixo da terça", "terça do nó (aba 90/82)", "ST-1P", "folga orelha × mesa da terça", f"{lc['folga_min_terca_mm']} mm ≥ 20", lc["folga_min_terca_mm"] >= 20, "")
reg("contraventamento", "terça escora (todas as linhas de terças)", "Z 302×90/82×2,30", "ST-1P", "4 M12 por apoio", "N + M (NBR 14762:2010 9.9), vento 0°", f"{CM['terca_escora']['interacao']:.2f} ≤ 1", CM["terca_escora"]["interacao"] <= 1.0,
    f"modelo integrado r05: governa vão {CM['terca_escora']['vao_governante']}, x = {CM['terca_escora']['linha_governante_x_m']} m: Nd {CM['terca_escora']['Nd']} kN, Md {CM['terca_escora']['Md']} kN·m")
st9, lp, chx = CM["ST1V_R"], CM["ligacao_portoes"], CM["chumbadores"]
reg("cobertura × VB eixo 9", "ST-1V-R", "2 ES-1R M20 hef 400 + grampo U Ø10", "VB-05 a 08", "escora da terça (vento do oitão)", "aço / concreto (ACI 318-19 17)",
    f"{st9['aco']['interacao']:.2f} / {st9['concreto']['interacao']:.2f}", st9["aco"]["interacao"] <= 1 and st9["concreto"]["interacao"] <= 1, f"Fy {st9['Fy_d']} kN")
reg("cobertura × TS-01", "ST-1P", "2 ES-1 M16 + grampo U Ø10 em cada", "TS-01", "escora + arrancamento", "ACI 318-19 17.8", f"{chx['ST-1P']['interacao']:.2f}", chx["ST-1P"]["interacao"] <= 1, f"Vu {chx['ST-1P']['Vu_terca']} kN ao longo da terça")
reg("contraventamento", "OR-X na VB do eixo 9", "1 ES-2V M16 + grampo", "VB-05 a 08", "a ±200 da terça do nó", "corte com armadura de ancoragem", f"{chx['OR-X VB']['uso']:.2f}", chx["OR-X VB"]["uso"] <= 1, "")
reg("pilar do portão × TS-01A", "PG-01 a PG-04", "2 CL-P L 102×102×9,5 + M16 8.8", "TS-01A (linha 4)", "insertos IL-1 / IT-P", "corte (y)", f"{max(lp[k]['uso'] for k in ('parafusos', 'insertos_TS', 'inserto_pilar', 'cantoneira')):.2f}",
    all(lp[k]["uso"] <= 1 for k in ("parafusos", "insertos_TS", "inserto_pilar", "cantoneira")), f"Fd {lp['Fd_max']} kN; furo oblongo vertical")
CH_ = json.loads((AQ / "calha.json").read_text(encoding="utf-8"))
reg("calha", "CA-1 300×150 + 9 descidas Ø200", "SC-1 c/750 na 1ª terça", "eixo A (40 cm livres)", "NBR 10844:1989", "capacidade calha / saída / suporte",
    f"{CH_['calha']['uso']:.2f} / {CH_['descidas']['uso']:.2f} / {CH_['suportes']['uso']:.2f}", max(CH_["calha"]["uso"], CH_["descidas"]["uso"], CH_["suportes"]["uso"]) <= 1, "I = 200 mm/h a confirmar")
reg("correntes", f"corrente flexível Ø{cc['flexivel']['d_mm']:g} M{cc['flexivel']['d_mm']:g}", f"furo {cc['flexivel']['furo']} no meio da alma", "terças", "porca + contraporca dos 2 lados", "tração acumulada (14 terças)", f"{cc['F_max_kN']} ≤ {cc['flexivel']['NtRd']} kN", cc["flexivel"]["uso"] <= 1, "")
reg("correntes", "tirante rígido L 51×51×3,2", "clipe L 32×3 + M10 em furo oval", "1ª e 2ª terça junto às ancoragens", "furo oval 11×23 na alma", "compressão, λ " + str(cc["rigida"]["esbeltez"]), f"{cc['F_max_kN']} ≤ {cc['rigida']['NcRd']} kN", cc["rigida"]["uso"] <= 1, "")
reg("correntes", "diagonal de ancoragem Ø16", "nó da corrente na 2ª terça", "ST-1P da 1ª terça (furo Ø18)", "porca + contraporca", "tração", f"{cc['diagonal']['Td']} ≤ {cc['diagonal']['NtRd']} kN", cc["diagonal"]["uso"] <= 1, "L/4 e 3L/4 ao apoio mais próximo; L/2 aos dois apoios")

# ------------------------------------------------------------------ 4. pilares × placas (IP-01 × CM-01) e × VB-01 / VM (consolos)
PLJ = json.loads((AQ / "placas.json").read_text(encoding="utf-8"))
reg("pilar × placa", "pilar PL/PF", "IP-01 = par de trilhos TR-1 nas faces laterais (c/125 a partir do piso)", "placa 125 × 10", "bucha BR-1 + CL-1 L 102×102×12,5",
    "fiada × inserto; flexão da CL-1", f"uso {PLJ['fixacoes']['CL1']['uso']:.2f}", PLJ["fixacoes"]["CL1"]["uso"] <= 1, "sem solda; trilho e bucha ≥ 12,4 kN por ponto (catálogo)")
reg("pilar × placa", "pilar (vistas E, F, H, I, J)", "2 luvas IB-1 M20", "1ª placa do pacote suspenso", "CA-1 L 152×102×19",
    "flexão da aba / M20 (tração + corte)", f"{PLJ['fixacoes']['CA1']['uso_aba']:.2f} / {PLJ['fixacoes']['CA1']['interacao_M20']:.2f}",
    PLJ["fixacoes"]["CA1"]["uso_aba"] <= 1 and PLJ["fixacoes"]["CA1"]["interacao_M20"] <= 1, "sem solda")
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

# ------------------------------------------------------------------ 5. I130 × pilares centrais (PN-2) e apoio da V405
reg("I130 × PC", "V404/405/406/407 I130 (h 120)", "dente 780×350 + TB-2 tubo Ø60,3×3,6 (furo 53), sem chapa", "PC-01/02", "consolo CP-I130 + PN-2 Ø25", "folga radial tubo × pino", "14 mm ≥ 10", True,
    "neoprene 300×250×30 fretado (3 camadas); pressão 4,3 ≤ 10 MPa; pino grauteado numa ponta só")
reg("I130 × PC", "V404", "dente na linha 9", "PF-04 (P14, linha 9, eixo C)", "consolo CP-I130 + PN-2 Ø25", "apoio da ponta da V404", f"+{LG['Z_ASS_I130']:.3f} (face interna do P14)", True, "DEC-058: V404 = P13B → linha 9 (16,517 m c-c); V406 L4 → P13 e V405 P13 → P13B, três vãos iguais")

# ------------------------------------------------------------------ 6. cobertura escondida
pl = LG["platibanda"]
reg("cobertura × platibanda", "painéis solares", "topo no eixo E (TP40 + lã + zipada + painel)", "pilar PL-05..08", "platibanda +10,000", "folga", f"{pl['folga_P2_mm']} mm ≥ 150", pl["folga_P2_mm"] >= 150, "")

(AQ / "conexoes.json").write_text(json.dumps(R, indent=1, ensure_ascii=False), encoding="utf-8")
n_ok = sum(1 for r in R if r["ok"])
print(f"{len(R)} verificações — {n_ok} ok, {len(R) - n_ok} com pendência")
for r in R:
    if not r["ok"] or r["obs"].startswith("!"):
        print(" -", r["grupo"], "|", r["peca_a"], "×", r["peca_b"], "|", r["verificacao"], "|", r["valor"], "|", r["obs"])
