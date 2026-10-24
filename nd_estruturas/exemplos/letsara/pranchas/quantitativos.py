"""ND-LET — quantitativos da obra (xlsx) a partir das tabelas das próprias pranchas (*.tabelas.json gerados no salvar).
Mesma fonte das pranchas: marcas, quantidades, relações de aço, cordoalhas, chaparia, terças e travamentos."""
import json, math, re, sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

PR = Path("/home/claude/letsara/pranchas")
AQ = Path("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
sys.path.insert(0, str(AQ)); sys.path.insert(0, str(PR))
SAIDA = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/claude/letsara/entregas/ND-LET-QUANTITATIVOS-rev09.xlsx")
LAJ = json.loads((AQ / "laje_alveolar.json").read_text(encoding="utf-8"))
VMJ = json.loads((AQ / "vm_retangular.json").read_text(encoding="utf-8"))   # rev09 (DEC-049): VM retangular 30 × 75
FCK_CAPA = 30                                  # capa 5 cm C30 (ND-LET-LA01, quadro das lajes; laje_alveolar.json)
FCK_2E = int(VMJ["premissas"].get("fck_2estagio", 30))  # 2º estágio das VM: C30
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
    """kg por bitola de UMA peça (com perdas), da relação do aço da prancha. rev07: pilares (fôrma + armação na mesma folha) leem
    arm/<MARCA>.json, gravado pelo próprio gerador da folha — mesma fonte da tabela de ferros desenhada."""
    out = {d: 0.0 for d in DIAMS}
    arq = PR / "arm" / (re.sub(r"^([A-Z]+)(\d+)$", r"\1-\2", folha) + ".json")
    if arq.exists():
        for b in json.loads(arq.read_text(encoding="utf-8"))["barras"]:
            out[float(b["diam"])] += b["qtd"] * b["comp"] / 100 * KGM[float(b["diam"])] * 1.10
        return out
    for a in T[f"ND-LET-{folha}"]["aco"]:
        for b in a["barras"]:
            out[float(b["diam"])] += b["qtd"] * b["comp"] / 100 * KGM[float(b["diam"])] * (1 + a["perda"])
    return out


# ------------------------------------------------------------------ peças pré-moldadas
pecas = []   # (grupo, marca, descrição, seção, L m, qtd, vol unit, peso unit t, concreto, prancha)
# família 40×60 (PL / PF): volume = corpo do cálice (−1,00) ao recuo + cabeça até +10,00 + consolos da marca
VOLC = {k: v["b_m"] * v["proj_m"] * v["h_total_m"] for k, v in CONS.items()}
rec_vb = lambda x: math.ceil((Z0 + 0.03 * x + 0.90) / 0.05) * 0.05
from familia_pl import MARCAS as _MARCAS_PL                      # rev04: direto da família (a PIL-A01 não é mais emitida)
for mk, pos, qt, cons, _ins in [l[:5] for l in _MARCAS_PL]:
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
PIL_OUTROS = ("PC01", "PC02", "PC03", "PM01", "PG01", "PG02", "PG03", "PG04", "PE01", "PE02", "PE03")   # rev09: PE (escada / P6 da linha 2)
for f_ in PIL_OUTROS:
    q = quadro(f_)
    pecas.append(("Pilares", q["MARCA"], tab(f_, "MARCAS")["linhas"][0][1], q["SEÇÃO"].replace(" cm (x × y)", ""), num(q["COMPRIMENTO"].split()[0]) / 100,
                  int(q["QUANTIDADE"].split()[0]), num(q["VOLUME"].split()[0]), num(q["PESO"].split()[0]), q["CONCRETO"], f"ND-LET-{f_}"))
q = quadro("TS01-1")
pecas.append(("Vigas de cobertura", "TS-01", "I90 protendida, sem dentes, linhas 3–8 (2 por linha; linha 2 metálica, DEC-048)", "I90", LGQ["L_TS"], int(q["QUANTIDADE"]),
              num(q["VOLUME"].split()[0]), round(num(q["VOLUME"].split()[0]) * 2.5, 2), "C50", "ND-LET-TS01"))
for mk, pos, qt, L, p in tab("I130", "MARCAS")["linhas"]:
    pecas.append(("Vigas de cobertura", mk, pos, "I130", num(L) / 100, int(qt), round(num(p) / 2.5, 2), num(p), "C50", "ND-LET-I130"))
for mk, pos, qt, L, p in tab("VB01", "MARCAS")["linhas"]:
    pecas.append(("Vigas de borda", mk, pos, "15×60 c/ dente", num(L) / 100, int(qt), round(num(p) / 2.5, 3), num(p), "C40", "ND-LET-VB01"))
VMP_H, VMP_B = round(VMJ["premissas"]["h_pm"] * 100), round(VMJ["premissas"]["b"] * 100)
for mk, pos, qt, L, _nc, p in tab("VM01", "MARCAS")["linhas"]:
    pecas.append(("Mezanino", mk, pos, f"retangular {VMP_B:g}×{VMP_H:g} c/ dente", num(L) / 100, int(qt), round(num(p) / 2.5, 2), num(p), "C40", "ND-LET-VM01"))
for mk, desc, qt, p, obs in tab("LA01", "MARCAS")["linhas"]:
    pecas.append(("Mezanino", mk, f"laje alveolar {desc}; {obs}".replace("; -", ""), "h20 + capa 5", num(re.search(r"× (\d+) ×", desc).group(1)) / 100, int(qt), round(num(p) / 2.5, 3), num(p), "C50", "ND-LET-LA01"))
for tp, L, qt, p, vis in tab("PP00", "TIPOS")["linhas"]:
    if not tp:
        continue
    pecas.append(("Placas de fechamento", tp, f"placa protendida, vistas {vis}", "125×10", num(L) / 100, int(qt), round(1.25 * 0.10 * num(L) / 100, 3), num(p), "C40", "ND-LET-PP00"))

# ------------------------------------------------------------------ aço CA-50 (relações das pranchas)
aco = []     # (peça, prancha, qtd, {diam: kg/peça}, obs)
for p_ in [p for p in pecas if p[1][:2] in ("PL", "PF")]:
    folha_mk = p_[9].replace("ND-LET-", "")
    aco.append((f"Pilar {p_[1]}", p_[9], p_[5], kg_diam(folha_mk), "consolos e cabeça da marca"))
for f_ in PIL_OUTROS:
    aco.append((f"Pilar {quadro(f_)['MARCA']}", f"ND-LET-{f_}", int(quadro(f_)["QUANTIDADE"].split()[0]), kg_diam(f_), ""))
import armaduras_vigas as AV
FOLHA_VIGA = {"TS-01": "ND-LET-TS01-1", "I130": "ND-LET-I130", "VM": "ND-LET-VM01", "VB": "ND-LET-VB01"}   # rev07: fôrma + armação na mesma folha
for k_, (fam_, fn_) in enumerate(AV.SPECS, 1):
    for m_ in fn_()["marcas"]:
        kd_ = {d: 0.0 for d in DIAMS}
        for b_ in m_["barras"]:
            kd_[float(b_["diam"])] += b_["qtd"] * b_["comp"] / 100 * KGM[float(b_["diam"])] * 1.10
        aco.append((f"{fam_} {m_['marca']}" if fam_ != m_["marca"] else fam_, FOLHA_VIGA[fam_], m_["qtd"], kd_, "tabela de ferros da marca"))
pp_kg = {d: 0.0 for d in DIAMS}
n_pp = 0
for tp, n, n2, tela, kgpl, kgt in tab("PP00", "AÇO PASSIVO")["linhas"]:
    n_pp += int(n)
    pp_kg[8.0] += int(n) * 2 * num(re.search(r"C=(\d+)", n2).group(1)) / 100 * 0.395 * 1.10
pp_kg = {d: v / n_pp for d, v in pp_kg.items()}
aco.append(("Placas PP (N2 Ø8)", "ND-LET-PP00", n_pp, pp_kg, "tela Q92 das pontas na aba Telas"))
_kp = {d: 0.0 for d in DIAMS}                                         # rev06b: armadura das 2 pontas (dente Gerber), ND-LET-PP01
_kp[6.3] = (2 * 54 + 2 * 54 + 2 * 46) / 100 * KGM[6.3] * 1.10
_kp[8.0] = (4 * 138 + 2 * 256) / 100 * KGM[8.0] * 1.10
aco.append(("Placas PP (ponta N3–N7)", "ND-LET-PP01", n_pp, _kp, "dente Gerber das 2 pontas"))

# ------------------------------------------------------------------ protensão
cord = []    # (peça, Ø, n por peça, L m, qtd, obs)
def soma_cord(f_):
    for g_ in ([f_, "TS01-2"] if f_.startswith("TS01") else [f_]):
        try:
            t = tab(g_, "CORDOALHAS"); break
        except KeyError:
            continue
    else:
        raise KeyError((f_, "CORDOALHAS"))
    n = sum(int(l[2]) for l in t["linhas"]); return n, num(t["linhas"][0][1])
import renomear as _RNq
PROTEGIDAS = set()
for nome, f_, L, qt in ((_RNq.MARCA_NOVO + _RNq.lista(_RNq.TS_TODAS), "TS01-1", LGQ["L_TS"], 12),):   # DEC-041: nomes por extenso; rev09: 12 TS-01 (linha 2 metálica)
    n, d = soma_cord(f_)
    cord.append((nome, d, n, L, qt, ""))
for _mk in ("VM-01", "VM-02", "VM-03", "VM-04"):                          # rev09: cordoalhas por marca (vm_retangular.json)
    _q = next(p[5] for p in pecas if p[1] == _mk)
    cord.append((_RNq.MARCA_NOVO + _RNq.lista(_RNq.nomes_de(_mk)), 12.7, VMJ[_mk]["n_cord"], VMJ[_mk]["L_peca"], _q, ""))
_IJ = json.loads((AQ / "i110_r01.json").read_text(encoding="utf-8"))          # I130: número de cordoalhas por marca (V407 20, V405/V406 30)
for p_ in [p for p in pecas if p[9] == "ND-LET-I130"]:
    cord.append((f"I130 {p_[1]}", 12.7, _IJ[p_[1]]["arranjo"]["n_cord"], _IJ[p_[1]]["L_peca"], p_[5], ""))
_PLJ = __import__("json").load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/placas.json"))["protensao"]
_OMJ = __import__("json").load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/ombreira.json"))["placa_I15"]
n, d = _PLJ["n"], _PLJ["diam_mm"]                                          # DEC-035: 10 fios Ø6 CP-175 RB
L_pp = sum(p[4] * p[5] for p in pecas if p[0] == "Placas de fechamento") / n_pp
cord.append(("Placas PP (média) — fios CP-175 RB", d, n, round(L_pp, 3), n_pp, "fios entalhados, 5 por face"))
if _OMJ["n_total"] > n:
    cord.append((f"Placa PP-05P (I-15, sobre a porta): +{_OMJ['n_total'] - n}", d, _OMJ["n_total"] - n, 9.86, 1, f"{_OMJ['n_total']} nesta placa (topo das ombreiras OM-1)"))
for p_ in [p for p in pecas if p[1].startswith("LA")]:                   # rev09: Ø15,2 / Ø12,7 / Ø9,5 da descrição da marca
    for n_, d_ in re.findall(r"(\d+) Ø(\d+,\d)", p_[2]):
        cord.append((f"Laje alveolar {p_[1]}", num(d_), int(n_), p_[4], p_[5], "uma por nervura (ND-LET-LA01)"))
KGC = {5.0: 0.154, 6.0: 0.222, 9.5: 0.432, 12.7: 0.792, 15.2: 1.126}                # kg/m: fios CP-175 Ø5/Ø6 (19,6/28,3 mm²); cordoalhas CP-190

# ------------------------------------------------------------------ metálica e insertos
terc = [l for l in tab("COB01", "TERÇAS")["linhas"] if l[0]]
lig_cob = tab("COB01", "LISTA DE MATERIAIS")["linhas"]
# rev09 (DEC-048): sem TS-01 na linha 2 — sem ST-1P4 (as terças da linha 2 apoiam no ST-W da W 310, lista da COB01)
trav = tab("COB02", "LISTA DE MATERIAIS")["linhas"]
chap_ts, chap_extra = {}, []
for l in tab("TS01-3", "LISTA DE PEÇAS")["linhas"]:                   # 1ª linha de cada marca = por peça; linhas repetidas = acréscimos (ex.: ES-1 da TS-01B)
    (chap_extra.append(l) if l[0] in chap_ts else chap_ts.__setitem__(l[0], l))
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
for f_ in ("PC01", "PC02", "PC03", "PM01", "PG01", "PG02", "PG03", "PG04"):
    add_ins(f_, quadro(f_)["MARCA"], int(quadro(f_)["QUANTIDADE"].split()[0]))
add_ins("I130", "I130", 3); add_ins("VM01", "VM", sum(p[5] for p in pecas if p[1].startswith("VM-"))); add_ins("VB01", "VB", 8)
for k in ("ES-1", "ES-2", "TB-3", "AL-1"):
    l = chap_ts[k]
    ins.append(("ND-LET-TS01-3", "TS-01", k, l[1], int(l[2]), 12))
for l in chap_extra:                                                     # acréscimo total (coluna total), não por peça
    if l[0] in ("ES-1", "ES-2", "TB-3", "AL-1"):
        ins.append(("ND-LET-TS01-3", "TS-01B", l[0], l[1], int(l[3]), 1))
for l in tab("PP00", "INSERTOS E PEÇAS")["linhas"]:
    if l[0] in ("NC-1", "TSA", "AL-P"):                                  # por placa (rev06: NC-1 nas 2 pontas, TSA dos pinos PT-1)
        if l[0] == "NC-1":                                               # só nas pontas com console (lado da porta sem nicho): contagem do PP01
            ins.append(("ND-LET-PP02", "Placas PP", "NC-1", l[1], 1, json.load(open("/home/claude/letsara/pranchas/pp01.json"))["n"]["NC1"]))
        else:
            ins.append(("ND-LET-PP00", "Placas PP", l[0], l[1], int(l[2]), n_pp))
# rev06 (DEC-026): consoles, chapas de espera, pinos e travas contados peça a peça nas vistas (fechamento.py)
import fechamento as _FC
_pec = [p_ for V in _FC.DADOS for p_ in _FC.DADOS[V][0]]
_n_cs = sum(len(_FC.DADOS[V][1]) for V in _FC.DADOS)
_n_pt1 = sum(2 for p_ in _pec if p_["trava"] == "PT-1")
_n_pt2 = sum(len(p_["pt2"]) for p_ in _pec)
_ce = set()
for V in _FC.DADOS:
    pil = [s_ for s_, _, _ in _FC.VISTAS[V]["pil"]]
    for (x_, z_) in _FC.DADOS[V][1]:
        _ce.add((V, min(pil, key=lambda s_: abs(s_ - x_)), z_))
_kg01 = json.load(open("/home/claude/letsara/pranchas/pp01.json"))
_n01 = _kg01["n"]
assert _n01["CS1"] == _n_cs and _n01["CE1"] == len(_ce), (_n01, _n_cs, len(_ce))
_TCE = __import__("geo_fixacao").TCE
ins += [("ND-LET-PP03", "Placas PP (obra)", "CS-1 obra", f"Console soldado A572-50 (costas, almas, mesa, 2 dentes, ponta) + M16 de nível + prisioneiro, soldado na obra na CE-1 lateral — {_kg01['kg_CS1']:.2f} kg/un".replace(".", ","), 1, _n01["CS1_obra"]),
        ("ND-LET-PP06", "Placas PP (obra)", "CS-1C", f"CS-1 (dos acima) + caixa de calço 120×330×100 chapa 9,5 soldada nas costas na fábrica (cantos A/I, PL-02/PL-06) — +{__import__('geo_fixacao').FX['calcos']['CS-1C']['kg_caixa']:.1f} kg/un (DEC-044)".replace(".", ","), 1, _n01["CS1C"]),
        ("ND-LET-PP06", "Placas PP (obra)", "CS-1D", f"CS-1 (dos acima) + caixa de calço 120×330×75 chapa 9,5 (PG-02/PG-04 da vista C) — +{__import__('geo_fixacao').FX['calcos']['CS-1D']['kg_caixa']:.1f} kg/un (DEC-044)".replace(".", ","), 1, _n01["CS1D"]),
        ("ND-LET-PP06", "Pilares (fábrica)", "CE-1L", f"Chapa de espera A36 840×330×{_TCE:g} com asas + 4 pinos Ø16×150 + 2 N18 (P8A e P11, fiada +6,25; das CE-1 acima) — DEC-044".replace(".", ","), 1, _n01["CE1L"]),
        ("ND-LET-PP03", "Pilares (fábrica)", "CS-1 fábrica", f"Console CS-1 soldado na fábrica do pilar sobre a CE-1 (compõe o CC-1) — {_kg01['kg_CS1']:.2f} kg/un".replace(".", ","), 1, _n01["CS1_fabrica"]),
        ("ND-LET-PP04", "Pilares (fábrica)", "CC-1", "CE-1 + 2 CS-1 soldados na fábrica, concretados na face C (DEC-031)", 1, _n01["CC1"]),
        ("ND-LET-PP04", "Pilares (fábrica)", "CC-1E/D", "CE-1 + 1 CS-1 (esquerdo/direito) soldados na fábrica, face C", 1, _n01["CC1E"] + _n01["CC1D"]),
        ("ND-LET-PP04", "Pilares (fábrica)", "CE-1", f"Chapa de espera A36 380×330×{_TCE:g} + 4 pinos Ø16×150 + 2 grampos N18 — {_kg01['kg_CE1']:.2f} kg/un (total; {_n01['CE1_obra']} lisas p/ solda na obra)".replace(".", ","), 1, len(_ce)),
        ("ND-LET-PP04", "Placas PP (obra)", "PT-1", f"Cartola 6,3 × 80 + 2 M16 8.8 (junta de baixo) — {_kg01['kg_PT1']:.2f} kg/un".replace(".", ","), 1, _n_pt1),
        ("ND-LET-PP04", "Placas PP (obra)", "PT-2", f"L 102×102×9,5 L=150 + 2 M16 + BR-1 (placa) + BR-2 (pilar) — {_kg01['kg_PT2']:.2f} kg/un".replace(".", ","), 1, _n_pt2),
        ("ND-LET-PP05", "Placas PP (obra)", "OM-1", f"Ombreira U 130×75×6,3 L=2478 + chapa de base + CL-1 + 2 chumbadores químicos M16 + 2 M16 passantes — {json.load(open('/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/ombreira.json'))['kg_un']:.1f} kg/un".replace(".", ","), 1, 2),
        ("ND-LET-PP05", "Placas PP", "BR-1 (I-15)", "Bucha M16 hef 70 na face interna da I-15 (topo das OM-1)", 2, 1),
        ("ND-LET-PP02", "Placas PP", "NC-1 (kg)", f"Caixa A572-50 do nicho (parede lateral A36) — {_kg01['kg_NC1']:.2f} kg/un; aço estrutural total {_kg01['kg_NC1']*_kg01['n']['NC1'] + _kg01['kg_CS1']*_n_cs + _kg01['kg_CE1']*len(_ce) + _kg01['kg_PT1']*_n_pt1 + _kg01['kg_PT2']*_n_pt2:.0f} kg".replace(".", ","), 0, n_pp)]

ACB = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/acabamentos_cobertura.json"))


def gerar_xlsx(SAIDA=SAIDA):
    global wb
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
            if isinstance(v, str) and v.startswith("\x01"):                 # nome novo já resolvido (renomear.MARCA_NOVO): o passe final não mexe
                v = _RNq.renomear(v); x = ws.cell(r, j, v); x.font = FI if j in entrada else F; x.border = BOR
                PROTEGIDAS.add((ws.title, r, j)); continue
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


    RODAPE = "PACOTE REV09 (23/10/2026, para análise) — quantitativos extraídos das tabelas das próprias pranchas vigentes. Números em azul vêm das pranchas; em preto, fórmulas."

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
    ws.cell(r + 2, 1, "Volumes de pilares da família 40×60: corpo do cálice (−1,00) ao recuo + cabeça recuada até +10,00 + consolos da marca (b × proj × h, sem chanfro). Placas: 125 × 10 × L (seção concretada). Lajes alveolares: volume equivalente pelo peso (2,5 t/m³).").font = F
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
    r = folha(ws, "CORDOALHAS CP-190 RB E FIOS CP-175 RB", RODAPE, ["PEÇA", "Ø (mm)", "CORD./PEÇA", "L PEÇA (m)", "QTD PEÇAS", "kg/m", "kg (na peça)", "OBS."], [26, 8, 11, 10, 10, 8, 12, 50])
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
        linha(ws, r, [m_, f"terça Z 302×90/82×2,30 METSEC (302Z23, fy 400, Z275), contínua por transpasse, L = {L} mm, vãos {vaos}; furação: {fur}", int(qt), round(num(kg) / int(qt), 1), f"=C{r}*D{r}", "ND-LET-COB01"],
              {4: "0.0", 5: "#,##0"}, entrada=(3, 4)); r += 1
    for m_, desc, qt, onde in lig_cob:
        if m_ in ("ES-1",):
            continue                                              # esperas embutidas nas vigas: aba Insertos
        kgu = {"ST-1P": KG_UN.get("ST-1P", 7.4), "ST-1P4": KG_UN.get("ST-1P4", KG_UN.get("ST-1P", 7.4)), "ST-1V": 7.4, "CMF-1": KG_UN.get("CMF-1", 0.6), "MF-1": KG_UN.get("MF-1", 4.6), "M12 8.8": 0.12, "M16": 0.08}.get(m_, 0)
        linha(ws, r, [m_, f"{desc} — {onde}", int(qt), kgu, f"=C{r}*D{r}", "ND-LET-COB01"], {4: "0.00", 5: "#,##0"}, entrada=(3, 4)); r += 1
    for l in trav:
        q = int(l[1]); kg = l[4]
        linha(ws, r, [l[0], f"{l[2]} — {l[5]} (comp. {l[3]})", q, round(num(kg) / q, 2) if kg not in ("-", "") else 0, f"=C{r}*D{r}", "ND-LET-COB02"],
              {4: "0.00", 5: "#,##0"}, entrada=(3, 4)); r += 1
    for f_, tit_ in (("COB05", "LISTA DE MATERIAL — COBERTURA DA LINHA 2"), ("ES01", "LISTA DE MATERIAL — ESCADA METÁLICA")):   # rev09 (DEC-045/048)
        for l in tab(f_, tit_)["linhas"]:
            if not l[0] or l[-1] in ("-", ""):
                continue
            q_ = int(l[2]) if str(l[2]).isdigit() else 1
            linha(ws, r, [l[0], f"{l[1]}" + (f" (L {l[3]} m)" if f_ == "COB05" and l[3] not in ("-", "") else ""), q_, round(num(l[-1]) / q_, 2), f"=C{r}*D{r}", f"ND-LET-{f_}"],
                  {4: "0.00", 5: "#,##0"}, entrada=(3, 4)); r += 1
    total(ws, r, "TOTAL (kg)", [5], r0, r - 1, 6)
    RC = r

    # 5a. cobertura Kingspan (telhas, cartolas, lã, clipes, fixações e rufos) — acabamentos_cob.py
    ACB = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/acabamentos_cobertura.json"))
    ws = wb.create_sheet("Cobertura Kingspan")
    r = folha(ws, f"COBERTURA KINGSPAN ZIPADA DUPLA COM LÃ DE ROCHA (manual p. 28) — área {ACB['telhas']['area_m2']:.0f} m²".replace(".", ","), RODAPE,
              ["ITEM", "UN", "LÍQUIDO", "COMPRA", "OBS.", "PRANCHA"], [48, 8, 10, 10, 90, 14])
    RK0 = r
    for t in ACB["telhas"]["itens"]:
        linha(ws, r, [t["item"], t["un"], t["liq"], t["compra"], t["obs"], "ND-LET-COB04"], {3: "#,##0.#", 4: "#,##0"}, entrada=(3, 4)); r += 1
    for t in ACB["rufos"]:
        linha(ws, r, [f"Rufo {t['marca']} {t['chapa']} desenv. {t['desenv_mm']}", "pç", t["pecas"], t["pecas"], f"{t['comprimento_m']:.1f} m — {t['descricao']}".replace(".", ",", 1), "ND-LET-COB04"], {3: "#,##0", 4: "#,##0"}, entrada=(3, 4)); r += 1
    for t in ACB["acessorios"]:
        linha(ws, r, [t["item"], "un", t["qtd"], t["qtd"], t["uso"], "ND-LET-COB04"], {3: "#,##0", 4: "#,##0"}, entrada=(3, 4)); r += 1
    ws.cell(r + 1, 1, "Compra: +5 % em lã, clipes e parafusos; telhas e cartolas pela contagem de peças. Valores a confirmar com a Kingspan (cotação e paginação).").font = F

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
    _b2, _h2 = VMJ["premissas"]["b"] - 0.12, 0.26                                 # rev09: faixa de 2º estágio 13 × 26 sobre a VM retangular
    from geometria import ABERTURA as _AB
    _A_ab = (_AB["x1"] - _AB["x0"]) * (_AB["y1"] - _AB["y0"])
    _L_vm = sum(p[4] * p[5] for p in pecas if p[1].startswith("VM-"))
    _n_la = sum(p[5] for p in pecas if p[1].startswith("LA-"))
    _L_la = sum(p[4] * p[5] for p in pecas if p[1].startswith("LA-"))
    linha(ws, r, [f"Capa C{FCK_CAPA}", "capa 5 cm sobre as lajes alveolares, 2 níveis (menos a abertura da escada no +3,90), tela Q138", f"=(2*39.5*9.65-{_A_ab:.2f})*0.05", "m³", "ND-LET-LA01 / MON02"], {3: "0.00"}); r += 1
    linha(ws, r, [f"2º estágio C{FCK_2E}", f"{_b2 * 100:.0f} × {_h2 * 100:.0f} sobre as VM retangulares (todas as marcas, 2 níveis), com a capa", f"={_L_vm:.2f}*{_b2:.2f}*{_h2:.2f}", "m³", "ND-LET-VM01"], {3: "0.00"}); r += 1
    linha(ws, r, ["Graute cálices", "graute fck ≥ 30 MPa nos cálices (folga 5 cm, 1,00 m)", f"={sum(p[5] for p in pecas if p[0] == 'Pilares')}*0.05*4*0.55*1.0", "m³", "estimativa: 4 faces × 5 cm × 1,00 m por pilar"], {3: "0.00"}); r += 1
    linha(ws, r, ["Graute chavetas", "chavetas das lajes alveolares", f"={_L_la:.1f}*0.006", "m³", "estimativa 0,006 m³/m"], {3: "0.00"}); r += 1

    # 0. resumo
    ws = wb.create_sheet("Resumo", 0)
    ws["A1"] = "LETSARA — PAVILHÃO COM MEZANINO — RESUMO DE QUANTITATIVOS"; ws["A1"].font = FT
    ws["A2"] = "MARQUES ENGENHARIA E CONSTRUÇÕES · ND ENGENHARIA E ASSESSORIA LTDA · 23/10/2026 · PACOTE REV09 (PARA ANÁLISE)"; ws["A2"].font = Font(name="Arial", size=8, italic=True)
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
             ("Cordoalhas CP-190 RB e fios CP-175 RB", "='Protensão'!G" + str(5 + len(cord)), "kg", "aba Protensão"),
             ("Cobertura metálica (terças, ligações, travamentos)", f"='Cobertura metálica'!E{RC}", "kg", "aba Cobertura metálica"),
             ("Cobertura Kingspan — telha zipada 455 + TP-40 + lã (área)", ACB["telhas"]["area_m2"], "m²", "aba Cobertura Kingspan"),
             ("Concreto / graute moldado na obra", "=SUM('Moldado in loco'!C5:C8)", "m³", "aba Moldado in loco")]
    for k, (a, b, c, d) in enumerate(itens, 5):
        for j, v in enumerate((a, b, c, d), 1):
            x = ws.cell(k, j, v); x.font = FB if not a.startswith("  ") else F; x.border = BOR
        ws.cell(k, 2).number_format = "#,##0.0"
    k += 2
    for t in ["Não inclui: fundações (blocos, cálices, estacas), piso, calhas e descidas, esquadrias e portões — fora do escopo da estrutura.",
              "Rev09 (DEC-045/048/049): pilares P6 e P7 da escada e P6 da linha 2 (PE-01 a PE-03), VM retangulares 30 × 75, escada metálica e cobertura metálica da linha 2 incluídos.",
              "Pilares PL/PF em concreto armado (opção A adotada).",
              RODAPE]:
        ws.cell(k, 1, t).font = F; k += 1
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    import renomear as _RN                                   # rev08: nomes novos das peças (P1…, V200…) nas listas
    for ws_ in wb.worksheets:
        for row_ in ws_.iter_rows():
            for c_ in row_:
                if isinstance(c_.value, str) and (ws_.title, c_.row, c_.column) not in PROTEGIDAS:
                    c_.value = _RN.renomear(c_.value)
    wb.save(SAIDA)
    print("ok", SAIDA, len(pecas), "marcas;", sum(p[5] for p in pecas), "peças")



# ================================================================== rev04: LISTAS EM PDF ÚNICO (preferência: pranchas num PDF, listas em outro)
# tubos: comprados em barras de 6 m da usina — soma dos comprimentos de corte por bitola ÷ 6 m (arredondado para cima)
def listas_pdf(caminho):
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    for nome, arq in (("DV", "DejaVuSans.ttf"), ("DVB", "DejaVuSans-Bold.ttf")):
        for base in ("/usr/share/fonts/truetype/dejavu/", "/usr/share/fonts/dejavu/"):
            if Path(base + arq).exists():
                pdfmetrics.registerFont(TTFont(nome, base + arq)); break
    ss = getSampleStyleSheet()
    Nn = ParagraphStyle("n", parent=ss["Normal"], fontName="DV", fontSize=7.6, leading=9.6)
    T1 = ParagraphStyle("t1", parent=Nn, fontName="DVB", fontSize=12, leading=15, spaceAfter=4)
    T2 = ParagraphStyle("t2", parent=Nn, fontName="DVB", fontSize=9.5, leading=12, spaceBefore=6, spaceAfter=3)
    import renomear as _RN
    Pp = lambda t: Paragraph(_RN.renomear(str(t)), Nn)
    fm = lambda v, d=1: f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def tb(lin, larg, tot=False):
        t = Table([[Pp(c) for c in l] for l in lin], colWidths=[w * mm for w in larg], repeatRows=1)
        st = [("GRID", (0, 0), (-1, -1), 0.3, colors.grey), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9e1ea")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]
        if tot:
            st.append(("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#eef2f6")))
        t.setStyle(TableStyle(st)); return t

    def rodape(c, d):
        c.saveState(); c.setFont("DV", 7)
        c.drawString(12 * mm, 7 * mm, "LETSARA — LISTAS DE MATERIAIS rev09 — 23/10/2026 (PARA ANÁLISE)")
        c.drawRightString(285 * mm, 7 * mm, f"página {d.page}"); c.restoreState()

    doc = SimpleDocTemplate(str(caminho), pagesize=landscape(A4), leftMargin=12 * mm, rightMargin=12 * mm, topMargin=12 * mm, bottomMargin=13 * mm,
                            title="Letsara — listas de materiais rev07", author="ND Engenharia")
    E = [Paragraph("LETSARA — LISTAS DE MATERIAIS (rev09, 23/10/2026, PARA ANÁLISE)", T1),
         Pp("Extraídas das tabelas das próprias pranchas (mesmos números). Aço CA-50 com +10 % de perdas; cordoalhas sem perdas; tubos em barras de 6 m (soma dos cortes ÷ 6 m). "
            "Rev07: placas 10 fios Ø6 CP-175 RB (só peso próprio, DEC-035); lajes alveolares LP20 com 7 Ø12,7 por painel e capa C30; ST-1P4 nos beirais do eixo 2 (DEC-033); fôrma e armação na mesma folha por marca.")]
    # 1 peças
    E.append(Paragraph("1. Peças pré-moldadas", T2))
    lin = [["GRUPO", "MARCA", "POSIÇÃO / DESCRIÇÃO", "SEÇÃO", "L (m)", "QT", "VOL. UNIT (m³)", "VOL. TOTAL (m³)", "PESO UNIT (t)", "CONCRETO", "PRANCHA"]]
    vt = pt = qt_ = 0
    for g, mk, pos, sec, L, q, v, p, c, fl in pecas:
        lin.append([g, mk, pos[:90], sec, fm(L, 2), q, fm(v, 3), fm(v * q, 2), fm(p, 2), c, fl]); vt += v * q; pt += p * q; qt_ += q
    lin.append(["TOTAL", "", "", "", "", qt_, "", fm(vt, 1), f"{fm(pt, 0)} t", "", ""])
    E.append(tb(lin, [24, 14, 76, 26, 12, 11, 18, 18, 16, 16, 30], tot=True))
    # 2 aço
    E += [PageBreak(), Paragraph("2. Aço CA-50 por peça e bitola (kg, +10 %)", T2)]
    ds = sorted({d for _, _, _, kd, _ in aco for d, v in kd.items() if v > 0})
    lin = [["PEÇA", "PRANCHA", "QT"] + [f"Ø{str(d).replace('.0', '').replace('.', ',')}" for d in ds] + ["kg/peça", "kg total"]]
    tot = {d: 0.0 for d in ds}
    for pe, fl, q, kd, _ in aco:
        if not q:
            continue
        kp = sum(kd.get(d, 0) for d in ds)
        lin.append([pe, fl, q] + [fm(kd.get(d, 0) * q, 0) if kd.get(d, 0) else "—" for d in ds] + [fm(kp, 1), fm(kp * q, 0)])
        for d in ds:
            tot[d] += kd.get(d, 0) * q
    lin.append(["TOTAL", "", ""] + [fm(tot[d], 0) for d in ds] + ["", fm(sum(tot.values()), 0)])
    E.append(tb(lin, [42, 30, 10] + [17] * len(ds) + [18, 20], tot=True))
    # 3 cordoalhas
    E.append(Paragraph("3. Cordoalhas CP-190 RB e fios CP-175 RB", T2))
    lin = [["PEÇA", "Ø (mm)", "CORD./PEÇA", "L (m)", "PEÇAS", "COMPR. TOTAL (m)", "kg", "OBS."]]
    tk = 0
    for pe, d, n, L, q, ob in cord:
        if not q:
            continue
        m_ = n * L * q; kg = m_ * KGC.get(float(d), 0.792); tk += kg
        lin.append([pe, fm(d, 1), n, fm(L, 2), q, fm(m_, 0), fm(kg, 0), ob])
    lin.append(["TOTAL", "", "", "", "", "", fm(tk, 0), "comprimento de pista e pontas de ancoragem: conferir com a fábrica"])
    E.append(tb(lin, [50, 14, 20, 16, 14, 26, 20, 100], tot=True))
    # 4 insertos e chaparia (com tubos em barras de 6 m)
    E += [PageBreak(), Paragraph("4. Insertos, chaparia e aparelhos de apoio (por tipo)", T2)]
    agg = {}
    for fl, pe, mk, desc, q, n in ins:
        k = (mk, desc)
        a = agg.setdefault(k, [0, set()]); a[0] += q * n; a[1].add(fl.replace("ND-LET-", ""))
    lin = [["MARCA", "DESCRIÇÃO", "QT TOTAL", "PRANCHAS"]]
    tubos = {}
    for (mk, desc), (q, fls) in sorted(agg.items()):
        lin.append([mk, desc, q, ", ".join(sorted(fls))[:60]])
        mt = re.search(r"[Tt]ubo (Ø[\d,]+×[\d,]+).*?L ?= ?(\d+)", desc)
        if mt:
            t = tubos.setdefault(mt.group(1), [0.0, 0]); t[0] += q * int(mt.group(2)) / 1000; t[1] += q
    E.append(tb(lin, [22, 150, 22, 66]))
    E.append(Paragraph("4.1 Tubos — compra em barras de 6 m", T2))
    lin = [["TUBO", "PEÇAS", "COMPR. TOTAL (m)", "BARRAS DE 6 m (com perda de corte)"]]
    for tu, (m_, q) in sorted(tubos.items()):
        cortes = max(1, int(6000 // max(1, round(m_ * 1000 / q))))
        lin.append([tu, q, fm(m_, 2), f"{math.ceil(q / cortes)} barras ({cortes} cortes por barra; {fm(m_ / 6, 1)} barras pela soma)"])
    E.append(tb(lin, [40, 20, 34, 120]))
    # 5 cobertura metálica
    E += [PageBreak(), Paragraph("5. Cobertura metálica — terças, ligações e travamento (tudo parafusado)", T2)]
    t_ = tab("COB01", "TERÇAS")
    E.append(tb([t_["cab"]] + t_["linhas"], [18, 20, 30, 90, 14, 20]))
    E.append(Spacer(1, 4))
    E.append(tb([["MARCA", "DESCRIÇÃO", "QT", "ONDE"]] + lig_cob, [20, 150, 16, 70]))
    E.append(Spacer(1, 4))
    t2 = tab("COB02", "LISTA DE MATERIAIS")
    E.append(tb([t2["cab"]] + t2["linhas"], [16, 14, 30, 30, 16, 150]))
    for f_, tit_, w_ in (("COB05", "LISTA DE MATERIAL — COBERTURA DA LINHA 2", [22, 150, 16, 20, 22]), ("ES01", "LISTA DE MATERIAL — ESCADA METÁLICA", [18, 150, 14, 18, 18, 22])):
        t3 = tab(f_, tit_)
        E += [Spacer(1, 6), Paragraph(f"{tit_.capitalize()} — ND-LET-{f_} (rev09)", T2)]
        E.append(tb([t3["cab"]] + t3["linhas"], w_))
    E += [PageBreak(), Paragraph(f"6. Cobertura Kingspan zipada dupla com lã de rocha (manual p. 28) — área {fm(ACB['telhas']['area_m2'], 0)} m² — ND-LET-COB04", T2)]
    lin = [["ITEM", "UN", "LÍQUIDO", "COMPRA", "OBSERVAÇÃO"]] + [[t["item"], t["un"], fm(t["liq"], 1 if isinstance(t["liq"], float) else 0), fm(t["compra"], 0), t["obs"].replace(".", ",")] for t in ACB["telhas"]["itens"]]
    E.append(tb(lin, [70, 14, 18, 18, 150]))
    E.append(Spacer(1, 4))
    lin = [["RUFO", "CHAPA", "DESENV. (mm)", "COMPR. (m)", "PEÇAS", "DESCRIÇÃO"]] + [[t["marca"], t["chapa"], t["desenv_mm"], fm(t["comprimento_m"], 1), t["pecas"], t["descricao"]] for t in ACB["rufos"]]
    E.append(tb(lin, [18, 30, 20, 20, 14, 168]))
    E.append(Spacer(1, 4))
    lin = [["ACESSÓRIO", "USO", "QTD"]] + [[t["item"], t["uso"], fm(t["qtd"], 0)] for t in ACB["acessorios"]]
    E.append(tb(lin, [80, 170, 20]))
    E.append(Pp("Compra: +5 % em lã, clipes e parafusos. Rufos em peças de 3 m com transpasse de 200 (peças de 600 nos pilares). Confirmar com a Kingspan."))
    doc.build(E, onFirstPage=rodape, onLaterPages=rodape)
    return caminho


if __name__ == "__main__":
    gerar_xlsx(SAIDA)
    print("ok", listas_pdf(SAIDA.with_name(SAIDA.name.replace("QUANTITATIVOS", "LISTAS").replace(".xlsx", ".pdf"))))
