"""ND-LET — quantitativos da obra (xlsx) a partir das tabelas das próprias pranchas (*.tabelas.json gerados no salvar).
Mesma fonte das pranchas: marcas, quantidades, relações de aço, cordoalhas, chaparia, terças e travamentos."""
import json, math, re, sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

PR = Path("/home/claude/letsara/pranchas")
AQ = Path("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
SAIDA = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/claude/letsara/entregas/ND-LET-QUANTITATIVOS-rev03.xlsx")
T = {p.name.replace(".tabelas.json", ""): json.loads(p.read_text(encoding="utf-8")) for p in PR.glob("ND-LET-*.tabelas.json")}
CONS = json.loads((AQ / "consolos.json").read_text(encoding="utf-8"))
LGQ = json.loads((AQ / "ligacoes.json").read_text(encoding="utf-8"))
Z0 = LGQ["Z0_TS"]
REC_Q = tuple(LGQ["REC"])
def num(s):
    s = str(s).strip()
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(\.\d{3})+", s):
        s = s.replace(".", "")
    return float(s)
KGM = {6.3: 0.245, 8.0: 0.395, 10.0: 0.617, 12.5: 0.963, 16.0: 1.578, 20.0: 2.466}
DIAMS = [6.3, 8.0, 10.0, 12.5, 16.0, 20.0]


def tab(folha, inicio):
    for t in T[f"ND-LET-{folha}"]["tabelas"]:
        if t["titulo"].upper().startswith(inicio.upper()):
            return t
    raise KeyError((folha, inicio))


def quadro(folha):
    d = {}
    for l in tab(folha, "QUADRO")["linhas"]:
        d[l[0]] = l[1]; d[l[2]] = l[3]
    return d


def kg_diam(folha):
    """kg por bitola de UMA peça (com perdas), da relação do aço da prancha."""
    out = {d: 0.0 for d in DIAMS}
    for a in T[f"ND-LET-{folha}"]["aco"]:
        for b in a["barras"]:
            out[float(b["diam"])] += b["qtd"] * b["comp"] / 100 * KGM[float(b["diam"])] * (1 + a["perda"])
    return out


# ------------------------------------------------------------------ peças pré-moldadas
pecas = []   # (grupo, marca, descrição, seção, L m, qtd, vol unit, peso unit t, concreto, prancha)
# família 40×60 (PL / PF): volume = corpo do cálice (−1,00) ao recuo + cabeça até +10,00 + consolos da marca
VOLC = {k: v["b_m"] * v["proj_m"] * v["h_total_m"] for k, v in CONS.items()}
rec_vb = lambda x: math.ceil((Z0 + 0.03 * x + 0.90) / 0.05) * 0.05
for mk, pos, qt, cons, _ins in [l[:5] for l in tab("PIL-A01", "MARCAS")["linhas"]]:
    qt = int(qt)
    canto = "canto" in pos
    if mk.startswith("PF"):
        zr = num(re.search(r"recuo \+(\d+,\d+)", cons).group(1)); cab = 0.40 * 0.30
    elif canto:
        zr = rec_vb(0.0 if pos.startswith("P1") else 39.50); cab = 0.30 * 0.30
    else:
        zr = REC_Q[0] if pos.startswith("P1") else REC_Q[1]; cab = 0.40 * 0.30
    vc = 0.0
    for parte in cons.split(";"):
        m = re.search(r"(?:(\d+) )?(CP-[A-Z0-9]+)[^()]*(?:\(([^)]*)\))?", parte.strip())
        if m and m.group(2) in VOLC:
            n = int(m.group(1)) if m.group(1) else (len(m.group(3).split(",")) if m.group(3) else 1)
            vc += n * VOLC[m.group(2)]
    vol = 0.24 * (1.0 + zr) + cab * (10.0 - zr) + vc
    folha_mk = mk.replace("-", "")
    pecas.append(("Pilares", mk, f"{pos}; {cons}", "40×60 (cabeça recuada)", 11.00, qt, round(vol, 3), round(vol * 2.5, 2), "C40", f"ND-LET-{folha_mk}"))
for f_ in ("PC01", "PC02", "PC03", "PM01", "PG01", "PG02"):
    q = quadro(f_)
    pecas.append(("Pilares", q["MARCA"], tab(f_, "MARCAS")["linhas"][0][1], q["SEÇÃO"].replace(" cm (x × y)", ""), num(q["COMPRIMENTO"].split()[0]) / 100,
                  int(q["QUANTIDADE"].split()[0]), num(q["VOLUME"].split()[0]), num(q["PESO"].split()[0]), q["CONCRETO"], f"ND-LET-{f_}"))
q = quadro("TS01-1")
pecas.append(("Vigas de cobertura", "TS-01", "I90 protendida, sem dentes, linhas 2–8 (2 por linha)", "I90", LGQ["L_TS"], int(q["QUANTIDADE"]),
              num(q["VOLUME"].split()[0]), round(num(q["VOLUME"].split()[0]) * 2.5, 2), "C50", "ND-LET-TS01"))
for mk, pos, qt, L, p in tab("I130", "MARCAS")["linhas"]:
    pecas.append(("Vigas de cobertura", mk, pos, "I130", num(L) / 100, int(qt), round(num(p) / 2.5, 2), num(p), "C50", "ND-LET-I130"))
for mk, pos, qt, L, p in tab("VB01", "MARCAS")["linhas"]:
    pecas.append(("Vigas de borda", mk, pos, "15×90", num(L) / 100, int(qt), round(0.15 * 0.90 * num(L) / 100, 3), num(p), "C40", "ND-LET-VB01"))
for mk, pos, qt, L, p in tab("VT01", "MARCAS")["linhas"]:
    pecas.append(("Vigas de travamento", mk, f"eixos A e E, {pos}", "25×60", num(L) / 100, int(qt), round(0.25 * 0.60 * num(L) / 100, 3), num(p), "C40", "ND-LET-VT01"))
for mk, pos, qt, L, p in tab("VM01", "MARCAS")["linhas"]:
    pecas.append(("Mezanino", mk, pos, "I90", num(L) / 100, int(qt), round(num(p) / 2.5, 2), num(p), "C50", "ND-LET-VM01"))
for mk, desc, qt, p, obs in tab("LA01", "MARCAS")["linhas"]:
    pecas.append(("Mezanino", mk, f"laje alveolar {desc}; {obs}".replace("; -", ""), "h20 + capa 5", 9.45, int(qt), round(num(p) / 2.5, 3), num(p), "fabricante", "ND-LET-LA01"))
for tp, L, qt, p, vis in tab("PP00", "TIPOS")["linhas"]:
    if not tp:
        continue
    pecas.append(("Placas de fechamento", tp, f"placa protendida, vistas {vis}", "125×10", num(L) / 100, int(qt), round(1.25 * 0.10 * num(L) / 100, 3), num(p), "C40", "ND-LET-PP00"))

# ------------------------------------------------------------------ aço CA-50 (relações das pranchas)
aco = []     # (peça, prancha, qtd, {diam: kg/peça}, obs)
for p_ in [p for p in pecas if p[1][:2] in ("PL", "PF")]:
    folha_mk = p_[9].replace("ND-LET-", "")
    aco.append((f"Pilar {p_[1]}", p_[9], p_[5], kg_diam(folha_mk), "consolos e cabeça da marca"))
for f_ in ("PC01", "PC02", "PC03", "PM01", "PG01", "PG02"):
    aco.append((f"Pilar {quadro(f_)['MARCA']}", f"ND-LET-{f_}", int(quadro(f_)["QUANTIDADE"].split()[0]), kg_diam(f_), ""))
import armaduras_vigas as AV
for k_, (fam_, fn_) in enumerate(AV.SPECS, 1):
    for m_ in fn_()["marcas"]:
        kd_ = {d: 0.0 for d in DIAMS}
        for b_ in m_["barras"]:
            kd_[float(b_["diam"])] += b_["qtd"] * b_["comp"] / 100 * KGM[float(b_["diam"])] * 1.10
        aco.append((f"{fam_} {m_['marca']}" if fam_ != m_["marca"] else fam_, f"ND-LET-AR-VIG-{k_:02d}", m_["qtd"], kd_, "tabela de ferros da marca"))
pp_kg = {d: 0.0 for d in DIAMS}
n_pp = 0
for tp, n, n2, tela, kgpl, kgt in tab("PP00", "AÇO PASSIVO")["linhas"]:
    n_pp += int(n)
    pp_kg[8.0] += int(n) * 2 * num(re.search(r"C=(\d+)", n2).group(1)) / 100 * 0.395 * 1.10
pp_kg = {d: v / n_pp for d, v in pp_kg.items()}
aco.append(("Placas PP (N2 Ø8)", "ND-LET-PP00", n_pp, pp_kg, "tela Q92 das pontas na aba Telas"))

# ------------------------------------------------------------------ protensão
cord = []    # (peça, Ø, n por peça, L m, qtd, obs)
def soma_cord(f_):
    t = tab(f_, "CORDOALHAS")
    n = sum(int(l[2]) for l in t["linhas"]); return n, num(t["linhas"][0][1])
for nome, f_, L, qt in (("TS-01", "TS01-2", LGQ["L_TS"], 14), ("I130 (média)", "I130", 22.95, 3), ("VM-01/02", "VM01", 9.33, 16), ("PL protendido (opção B)", "PIL-P01", 11.0, 0)):
    n, d = soma_cord(f_)
    cord.append((nome, d, n, L, qt, "opção B não adotada (qtd 0)" if qt == 0 else ""))
n, d = 8, 12.7
L_pp = sum(p[4] * p[5] for p in pecas if p[0] == "Placas de fechamento") / n_pp
cord.append(("Placas PP (média)", d, n, round(L_pp, 3), n_pp, ""))
cord.append(("Lajes alveolares LA", 12.7, 8, 9.45, sum(p[5] for p in pecas if p[1].startswith("LA")), "fornecimento do fabricante da laje"))
KGC = {9.5: 0.432, 12.7: 0.792}

# ------------------------------------------------------------------ metálica e insertos
terc = [l for l in tab("COB01", "TERÇAS")["linhas"] if l[0]]
lig_cob = tab("COB01", "LISTA DE MATERIAIS")["linhas"]
trav = tab("COB02", "LISTA DE MATERIAIS")["linhas"]
chap_ts = {l[0]: l for l in tab("TS01-3", "LISTA DE PEÇAS")["linhas"]}
KG_UN = {k: num(v[4]) for k, v in chap_ts.items() if v[4] not in ("-", "")}

ins = []     # (prancha, peça, marca, descrição, qt por peça, peças)
def add_ins(f_, peca, qtd, titulo="INSERTOS"):
    for l in tab(f_, titulo)["linhas"]:
        try:
            q = int(str(l[2]).split()[0])
        except ValueError:
            continue
        ins.append((f"ND-LET-{f_}", peca, l[0], l[1], q, qtd))
for p_ in [p for p in pecas if p[1][:2] in ("PL", "PF")]:
    add_ins(p_[9].replace("ND-LET-", ""), p_[1], p_[5])
for f_ in ("PC01", "PC02", "PC03", "PM01", "PG01", "PG02"):
    add_ins(f_, quadro(f_)["MARCA"], int(quadro(f_)["QUANTIDADE"].split()[0]))
add_ins("I130", "I130", 3); add_ins("VM01", "VM", 16); add_ins("VB01", "VB", 8); add_ins("VT01", "VT", 14)
for k in ("ES-1", "ES-2", "ES-3", "TB-3", "AL-1"):
    l = chap_ts[k]
    ins.append(("ND-LET-TS01-3", "TS-01", k, l[1], int(l[2]), 14))
for l in tab("PP00", "INSERTOS E PEÇAS")["linhas"]:
    if l[2] != "—":
        ins.append(("ND-LET-PP00", "Placas PP", l[0], l[1], int(l[2]), n_pp))

# ------------------------------------------------------------------ planilha
wb = Workbook()
F = Font(name="Arial", size=9); FB = Font(name="Arial", size=9, bold=True); FT = Font(name="Arial", size=12, bold=True)
FI = Font(name="Arial", size=9, color="0000FF")
CAB = PatternFill("solid", fgColor="D9E1EA"); TOT = PatternFill("solid", fgColor="EEF2F6")
fina = Side(style="thin", color="9AA5B1"); BOR = Border(left=fina, right=fina, top=fina, bottom=fina)


def folha(ws, titulo, sub, cab, larg):
    ws["A1"] = titulo; ws["A1"].font = FT
    ws["A2"] = sub; ws["A2"].font = Font(name="Arial", size=8, italic=True)
    for j, (c, w) in enumerate(zip(cab, larg), 1):
        x = ws.cell(4, j, c); x.font = FB; x.fill = CAB; x.border = BOR; x.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.row_dimensions[4].height = 30
    ws.freeze_panes = "A5"
    return 5


def linha(ws, r, vals, fmts=None, entrada=()):
    for j, v in enumerate(vals, 1):
        x = ws.cell(r, j, v); x.font = FI if j in entrada else F; x.border = BOR
        if fmts and fmts.get(j):
            x.number_format = fmts[j]


def total(ws, r, rot, cols, r0, r1, ncol):
    for j in range(1, ncol + 1):
        x = ws.cell(r, j); x.fill = TOT; x.border = BOR; x.font = FB
    ws.cell(r, 1, rot)
    for c in cols:
        L = get_column_letter(c)
        ws.cell(r, c, f"=SUM({L}{r0}:{L}{r1})").number_format = "#,##0.00"


RODAPE = "PROJETO DA ND ENGENHARIA — quantitativos extraídos das pranchas rev. vigentes (13/10/2026). Números em azul vêm das pranchas; em preto, fórmulas."

# 1. pré-moldados
ws = wb.active; ws.title = "Pré-moldados"
r = folha(ws, "LETSARA — PEÇAS PRÉ-MOLDADAS", RODAPE,
          ["GRUPO", "MARCA", "POSIÇÃO / DESCRIÇÃO", "SEÇÃO", "L (m)", "QTD", "VOLUME UNIT. (m³)", "VOLUME TOTAL (m³)", "PESO UNIT. (t)", "PESO TOTAL (t)", "CONCRETO", "PRANCHA"],
          [20, 10, 62, 20, 8, 6, 12, 12, 10, 11, 11, 16])
r0 = r
for p in pecas:
    linha(ws, r, [p[0], p[1], p[2], p[3], p[4], p[5], p[6], f"=F{r}*G{r}", p[7], f"=F{r}*I{r}", p[8], p[9]],
          {5: "0.00", 7: "0.000", 8: "0.00", 9: "0.00", 10: "0.00"}, entrada=(5, 6, 7, 9))
    r += 1
total(ws, r, "TOTAL", [6, 8, 10], r0, r - 1, 12)
ws.cell(r + 2, 1, "Volumes de pilares da família 40×60: corpo do cálice (−1,00) ao recuo + cabeça recuada até +10,00 + consolos da marca (b × proj × h, sem chanfro). Placas: 125 × 15 × L. Lajes alveolares: volume equivalente pelo peso (2,5 t/m³).").font = F
RP = (r0, r - 1)

# 2. aço CA-50
ws = wb.create_sheet("Aço CA-50")
r = folha(ws, "AÇO CA-50 — RELAÇÕES DAS PRANCHAS (+10 % de perdas)", RODAPE,
          ["PEÇA", "PRANCHA", "QTD PEÇAS"] + [f"Ø{str(d).replace('.0', '').replace('.', ',')} (kg/peça)" for d in DIAMS] + ["kg/PEÇA", "kg TOTAL", "OBS."],
          [30, 16, 9] + [11] * 6 + [10, 12, 60])
r0 = r
for nome, f_, qt, kg, obs in aco:
    linha(ws, r, [nome, f_, qt] + [round(kg[d], 2) for d in DIAMS] + [f"=SUM(D{r}:I{r})", f"=C{r}*J{r}", obs],
          {**{c: "0.00" for c in range(4, 10)}, 10: "0.0", 11: "#,##0"}, entrada=tuple(range(3, 10)))
    r += 1
total(ws, r, "TOTAL (kg)", [11], r0, r - 1, 12)
r += 1
ws.cell(r, 1, "por bitola (kg)").font = FB
for j, d in enumerate(DIAMS):
    L = get_column_letter(4 + j)
    x = ws.cell(r, 4 + j, f"=SUMPRODUCT($C{r0}:$C{r - 2},{L}{r0}:{L}{r - 2})"); x.number_format = "#,##0"; x.font = FB; x.border = BOR
RA = r

# 3. telas
ws = wb.create_sheet("Telas")
r = folha(ws, "TELAS SOLDADAS", RODAPE, ["ITEM", "ONDE", "ÁREA (m²)", "kg/m²", "kg (+10 %)", "OBS."], [24, 50, 12, 10, 12, 50])
r0 = r
linha(ws, r, ["Q92", "placas PP — 2 faces × 60 cm nas 2 pontas", f"={n_pp}*{2 * 2 * 0.60 * 1.19}", 1.48, f"=C{r}*D{r}*1.1", f"{n_pp} placas"], {3: "0.0", 5: "0.0"}, entrada=(4,)); r += 1
linha(ws, r, ["Q138", "capa 5 cm do mezanino (2 níveis)", f"=2*39.5*9.65", 2.20, f"=C{r}*D{r}*1.1", "ND-LET-LA01 / VM01"], {3: "0.0", 5: "0.0"}, entrada=(4,)); r += 1
total(ws, r, "TOTAL", [3, 5], r0, r - 1, 6)

# 4. protensão
ws = wb.create_sheet("Protensão")
r = folha(ws, "CORDOALHAS CP-190 RB", RODAPE, ["PEÇA", "Ø (mm)", "CORD./PEÇA", "L PEÇA (m)", "QTD PEÇAS", "kg/m", "kg (na peça)", "OBS."], [26, 8, 11, 10, 10, 8, 12, 50])
r0 = r
for nome, d, n, L, qt, obs in cord:
    linha(ws, r, [nome, d, n, L, qt, KGC[d], f"=C{r}*D{r}*E{r}*F{r}", obs], {4: "0.00", 6: "0.000", 7: "#,##0"}, entrada=(2, 3, 4, 5, 6)); r += 1
total(ws, r, "TOTAL (kg)", [7], r0, r - 1, 8)
ws.cell(r + 2, 1, "Comprimento na peça (sem as sobras de pista entre peças e as pontas de ancoragem da pista); a fábrica soma conforme o arranjo da pista de 60 m.").font = F

# 5. cobertura metálica
ws = wb.create_sheet("Cobertura metálica")
r = folha(ws, "COBERTURA METÁLICA — TERÇAS, LIGAÇÕES E TRAVAMENTOS (parafusados)", RODAPE, ["MARCA", "DESCRIÇÃO", "QTD", "kg/un", "kg TOTAL", "ORIGEM"], [12, 70, 8, 9, 12, 18])
r0 = r
for m_, L, vaos, fur, qt, kg in terc:
    linha(ws, r, [m_, f"terça Ue 300×85×25×2,65 ZAR 345, L = {L} mm, vãos {vaos}; furação: {fur}", int(qt), round(num(kg) / int(qt), 1), f"=C{r}*D{r}", "ND-LET-COB01"],
          {4: "0.0", 5: "#,##0"}, entrada=(3, 4)); r += 1
for m_, desc, qt, onde in lig_cob:
    if m_ in ("ES-1", "ES-3"):
        continue                                              # esperas embutidas nas vigas: aba Insertos
    kgu = {"ST-1P": KG_UN.get("ST-1P", 7.4), "ST-1V": 7.4, "CMF-1": KG_UN.get("CMF-1", 0.6), "MF-1": KG_UN.get("MF-1", 4.6), "M12 8.8": 0.12, "M16": 0.08}.get(m_, 0)
    linha(ws, r, [m_, f"{desc} — {onde}", int(qt), kgu, f"=C{r}*D{r}", "ND-LET-COB01"], {4: "0.00", 5: "#,##0"}, entrada=(3, 4)); r += 1
for l in trav:
    q = int(l[1]); kg = l[4]
    linha(ws, r, [l[0], f"{l[2]} — {l[5]} (comp. {l[3]})", q, round(num(kg) / q, 2) if kg not in ("-", "") else 0, f"=C{r}*D{r}", "ND-LET-COB02"],
          {4: "0.00", 5: "#,##0"}, entrada=(3, 4)); r += 1
total(ws, r, "TOTAL (kg)", [5], r0, r - 1, 6)
RC = r

# 6. insertos
ws = wb.create_sheet("Insertos e ligações")
r = folha(ws, "INSERTOS, CHAPARIA EMBUTIDA, PINOS, NEOPRENES E ALÇAS", RODAPE, ["PRANCHA", "PEÇA", "MARCA", "DESCRIÇÃO", "QT/PEÇA", "PEÇAS", "QT TOTAL", "kg/un", "kg TOTAL"], [16, 18, 9, 70, 9, 8, 9, 8, 10])
r0 = r
for f_, peca, mk, desc, q, n in ins:
    kgu = KG_UN.get(mk, 0.0) if f_ == "ND-LET-TS01-3" else 0.0
    linha(ws, r, [f_, peca, mk, desc, q, n, f"=E{r}*F{r}", kgu, f"=G{r}*H{r}"], {8: "0.0", 9: "#,##0"}, entrada=(5, 6, 8)); r += 1
total(ws, r, "TOTAL", [7, 9], r0, r - 1, 9)
ws.cell(r + 2, 1, "kg só da chaparia da TS-01 (lista da ND-LET-TS01-3); demais insertos por unidade conforme as pranchas de cada peça.").font = F

# 7. moldado in loco
ws = wb.create_sheet("Moldado in loco")
r = folha(ws, "CONCRETO E GRAUTE MOLDADOS NA OBRA", RODAPE, ["ITEM", "DESCRIÇÃO", "QTD", "UN", "OBS."], [24, 70, 12, 6, 50])
r0 = r
linha(ws, r, ["Capa C25", "capa 5 cm sobre as lajes alveolares, 2 níveis", "=2*39.5*9.65*0.05", "m³", "ND-LET-LA01 / MON02"], {3: "0.00"}); r += 1
linha(ws, r, ["Enchimento C25", "30 × 20 sobre a mesa das VM (linhas 1 e 2, 2 níveis)", "=2*2*39.5*0.30*0.20", "m³", "ND-LET-VM01 corte C-C"], {3: "0.00"}); r += 1
linha(ws, r, ["Graute cálices", "graute fck ≥ 30 MPa nos cálices (folga 5 cm, 1,00 m)", f"={sum(p[5] for p in pecas if p[0] == 'Pilares')}*0.05*4*0.55*1.0", "m³", "estimativa: 4 faces × 5 cm × 1,00 m por pilar"], {3: "0.00"}); r += 1
linha(ws, r, ["Graute chavetas", "chavetas das lajes alveolares", "=2*31*9.45*0.006", "m³", "estimativa 0,006 m³/m"], {3: "0.00"}); r += 1

# 0. resumo
ws = wb.create_sheet("Resumo", 0)
ws["A1"] = "LETSARA — PAVILHÃO COM MEZANINO — RESUMO DE QUANTITATIVOS"; ws["A1"].font = FT
ws["A2"] = "MARQUES ENGENHARIA E CONSTRUÇÕES · ND ENGENHARIA E ASSESSORIA LTDA · 13/10/2026 · PARA APROVAÇÃO"; ws["A2"].font = Font(name="Arial", size=8, italic=True)
for j, (c, w) in enumerate(zip(["ITEM", "QUANTIDADE", "UN", "FONTE"], [48, 16, 8, 40]), 1):
    x = ws.cell(4, j, c); x.font = FB; x.fill = CAB; x.border = BOR
    ws.column_dimensions[get_column_letter(j)].width = w
P0, P1 = RP
itens = [("Peças pré-moldadas", f"='Pré-moldados'!F{P1 + 1}", "pç", "aba Pré-moldados"),
         ("Concreto pré-moldado", f"='Pré-moldados'!H{P1 + 1}", "m³", "aba Pré-moldados"),
         ("Peso das peças pré-moldadas", f"='Pré-moldados'!J{P1 + 1}", "t", "aba Pré-moldados"),
         ("  pilares (m³)", f"=SUMIF('Pré-moldados'!A{P0}:A{P1},\"Pilares\",'Pré-moldados'!H{P0}:H{P1})", "m³", ""),
         ("  vigas de cobertura (m³)", f"=SUMIF('Pré-moldados'!A{P0}:A{P1},\"Vigas de cobertura\",'Pré-moldados'!H{P0}:H{P1})", "m³", ""),
         ("  vigas de borda e travamento (m³)", f"=SUMIF('Pré-moldados'!A{P0}:A{P1},\"Vigas de borda\",'Pré-moldados'!H{P0}:H{P1})+SUMIF('Pré-moldados'!A{P0}:A{P1},\"Vigas de travamento\",'Pré-moldados'!H{P0}:H{P1})", "m³", ""),
         ("  mezanino — vigas e lajes (m³)", f"=SUMIF('Pré-moldados'!A{P0}:A{P1},\"Mezanino\",'Pré-moldados'!H{P0}:H{P1})", "m³", ""),
         ("  placas de fechamento (m³)", f"=SUMIF('Pré-moldados'!A{P0}:A{P1},\"Placas de fechamento\",'Pré-moldados'!H{P0}:H{P1})", "m³", ""),
         ("Aço CA-50 (barras)", f"='Aço CA-50'!K{RA - 1}", "kg", "aba Aço CA-50"),
         ("Telas soldadas", "='Telas'!E7", "kg", "aba Telas"),
         ("Cordoalhas CP-190 RB", "='Protensão'!G" + str(5 + len(cord)), "kg", "aba Protensão"),
         ("Cobertura metálica (terças, ligações, travamentos)", f"='Cobertura metálica'!E{RC}", "kg", "aba Cobertura metálica"),
         ("Concreto / graute moldado na obra", "=SUM('Moldado in loco'!C5:C8)", "m³", "aba Moldado in loco")]
for k, (a, b, c, d) in enumerate(itens, 5):
    for j, v in enumerate((a, b, c, d), 1):
        x = ws.cell(k, j, v); x.font = FB if not a.startswith("  ") else F; x.border = BOR
    ws.cell(k, 2).number_format = "#,##0.0"
k += 2
for t in ["Não inclui: fundações (blocos, cálices, estacas), piso, telhas e acessórios de cobertura (calhas, rufos), esquadrias e portões — fora do escopo da estrutura.",
          "Pilares P6 e P7 do anexo (R01) fora do quantitativo até a definição da função.",
          "Pilares PL/PF quantificados na opção A (concreto armado). Opção B (protendido) na prancha ND-LET-PIL-P01.",
          RODAPE]:
    ws.cell(k, 1, t).font = F; k += 1
SAIDA.parent.mkdir(parents=True, exist_ok=True)
wb.save(SAIDA)
print("ok", SAIDA, len(pecas), "marcas;", sum(p[5] for p in pecas), "peças")
