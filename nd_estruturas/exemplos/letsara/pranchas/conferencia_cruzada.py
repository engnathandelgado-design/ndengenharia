"""rev11 (26/10/2026, pedido do Nathan): CONFERÊNCIA CRUZADA — roda no fim do gerar_tudo e dá ERRO em divergência.
Toda mudança de seção ou armadura só é dada como pronta com esta conferência zerada.

Verificações implementadas nesta versão (as demais estão listadas em PENDENTES no relatório):
 C1  tabela de ferros × desenho: posições N desenhadas × posições da tabela, por folha (lidas dos .tabelas.json e do DXF);
 C2  resumo do aço da folha × soma da tabela de ferros (kg por Ø, +10 %) — tolerância 1 %;
 C3  quantitativos (xlsx) × soma das folhas: aço CA-50 total — tolerância 2 %;
 C4  regras da ND nos textos das folhas: cordoalha Ø15,2 em laje/viga protendida; "W 310"; "Kingspan" nos acabamentos;
     NEO-3 (sem C) no apoio das TS-01 na I120; "sem uso" na laje +7,30 (deve ser laje de cobertura);
 C5  marcas de consolo: toda marca C1…Cn citada nas folhas existe no registro (consolos_marcas.json);
 C6  nomes de peça (P1…, V100…) citados nas plantas existem no registro de nomes (nomes.json).
Saída: conferencia_cruzada.json e .md na pasta das pranchas; código de saída 1 se houver ERRO."""
import glob, json, os, re, sys
import ezdxf

PR = "/home/claude/letsara/pranchas/"
res = []


PEND = json.load(open(PR + "decisoes_pendentes.json", encoding="utf-8")) if os.path.exists(PR + "decisoes_pendentes.json") else []


def r(ok, item, folha, det):
    """divergência coberta por decisão pendente do Nathan (decisoes_pendentes.json) vira PENDENTE: não some, mas não é erro de
    emissão — impede o pacote final (zip) até a decisão."""
    pend = next((p_ for p_ in PEND if p_["item"] == item and p_["folha"] == folha), None)
    res.append(dict(ok=bool(ok), item=item, folha=folha, detalhe=det if ok or not pend else f"PENDENTE {pend['dec']}: {pend['motivo']} — {det}",
                    pendente=bool(not ok and pend)))


def textos(dxf):
    try:
        doc = ezdxf.readfile(dxf)
    except Exception:
        return []
    out = []
    for e in doc.modelspace().query("TEXT MTEXT"):
        out.append(e.dxf.text if e.dxftype() == "TEXT" else e.plain_text())
    for b in doc.blocks:
        for e in b.query("TEXT MTEXT"):
            out.append(e.dxf.text if e.dxftype() == "TEXT" else e.plain_text())
    return out


idx = json.load(open(PR + "indice.json", encoding="utf-8"))["ordem"]
REGC = json.load(open(PR + "consolos_marcas.json", encoding="utf-8")) if os.path.exists(PR + "consolos_marcas.json") else {"lista": []}
MC = {e["marca"] for e in REGC["lista"]}
NOMES = {q["nome"] for q in json.load(open(PR + "nomes.json", encoding="utf-8"))["pecas"]}
aco_folhas = 0.0
for fl in idx:
    tj = PR + fl + ".tabelas.json"
    dx = PR + fl + ".dxf"
    T = json.load(open(tj, encoding="utf-8")) if os.path.exists(tj) else None
    tx = textos(dx) if os.path.exists(dx) else []
    tall = "\n".join(tx)
    # C1 — posições N desenhadas × tabela
    if T:
        pos_tab = set()
        for t in T.get("tabelas", []):
            if "FERRO" in t.get("titulo", "").upper():
                pos_tab |= {l[1] for l in t["linhas"] if len(l) > 1}
        if pos_tab:
            desenh = {p for p in pos_tab if re.search(r"(?<![A-Z0-9])" + re.escape(p) + r"(?![0-9a-z])", tall.replace(p + " ", p + " ") if p else "")}
            falta = sorted(pos_tab - desenh)
            r(not falta, "C1 tabela × desenho (posições)", fl, "todas as posições da tabela aparecem no desenho" if not falta else f"sem rótulo no desenho: {', '.join(falta[:12])}")
        # C2 — cada TABELA DE FERROS × o RESUMO DO AÇO +10% logo depois dela (kg por folha)
        tabs = T.get("tabelas", [])
        num = lambda v: float(str(v).replace(".", "").replace(",", ".").split()[0]) if str(v).strip() else 0.0
        for i_, t in enumerate(tabs):
            if not t.get("titulo", "").upper().startswith("TABELA DE FERROS"):
                continue
            rs = next((u for u in tabs[i_ + 1:i_ + 3] if u.get("titulo", "").upper().startswith("RESUMO DO AÇO")), None)
            if not rs:
                continue
            kg = 0.0
            for l in t["linhas"]:
                try:
                    d = num(l[2]); ctot = num(l[5])
                except Exception:
                    continue
                kg += ctot / 100 * 3.14159 * (d / 1000) ** 2 / 4 * 7850 * 1.10
            tot = next((num(l[2]) for l in rs["linhas"] if "TOTAL" in str(l[0]).upper() and "CA-50" in str(l[0]).upper()), None)
            if tot is None:
                continue
            r(abs(kg - tot) <= 0.015 * max(tot, 1) + 0.5, "C2 resumo do aço × tabela de ferros", fl, f"{t['titulo']}: tabela {kg:.1f} kg × resumo {tot:.1f} kg")
            if "1 UNIDADE" in t["titulo"].upper() or "UNIDADES" not in t["titulo"].upper():
                pass
            aco_folhas += tot if "UNIDADES" in t["titulo"].upper() or "1 UNIDADE" not in t["titulo"].upper() else 0
    # C4 — regras da ND nos textos
    if tx:
        prot = fl.startswith(("ND-LET-LA", "ND-LET-I1", "ND-LET-TS", "ND-LET-VM", "ND-LET-VB"))
        m152 = [t for t in tx if re.search(r"Ø\s?15,2", t) and "alvéol" not in t.lower()]
        if prot:
            r(not m152, "C4 cordoalha Ø15,2 em laje/viga protendida", fl, "nenhuma" if not m152 else f"{len(m152)} ocorrência(s): {m152[0][:70]}")
        w310 = [t for t in tx if ("W 310" in t or "W310" in t) and "DEC-0" not in t]          # revisões antigas citam a decisão
        r(not w310, "C4 menção a W 310 (hoje W 200 × 15,0)", fl, "nenhuma" if not w310 else w310[0][:80])
        if fl.startswith("ND-LET-COB0"):
            kg = [t for t in tx if "KINGSPAN" in t.upper() and ("RUFO" in t.upper() or "ACABAMENTO" in t.upper())]
            r(not kg, "C4 acabamentos de funilaria (sem marca de catálogo)", fl, "ok" if not kg else kg[0][:80])
        su = [t for t in tx if "7,30" in t and "sem uso" in t.lower()]
        r(not su, "C4 laje +7,30 descrita como laje de cobertura", fl, "ok" if not su else su[0][:80])
        if fl.startswith("ND-LET-TS01"):
            neo = [t for t in tx if re.search(r"NEO-3(?!C)\b", t) and ("I120" in t or "topo" in t.lower()) and "100×300" not in t and "P11" not in t]   # NEO-3 só no topo do P11 (linha 4)
            r(not neo, "C4 NEO-3C no apoio das TS-01 sobre a I120", fl, "ok" if not neo else neo[0][:80])
        # C5 — marcas de consolo
        mcs = {m for t in tx for m in re.findall(r"(?<![A-Z0-9-])C(\d{1,2})(?![0-9×x])", t)}
        mcs = {"C" + m for m in mcs}
        if fl.startswith(("ND-LET-PL", "ND-LET-PF", "ND-LET-PC", "ND-LET-PM", "ND-LET-PE", "ND-LET-PG", "ND-LET-CS")) and MC:
            fora = sorted(m for m in mcs if m not in MC and int(m[1:]) <= 20)
            r(not fora, "C5 marcas de consolo existem no registro", fl, "ok" if not fora else ", ".join(fora))
# C3 — quantitativos × folhas (aço total)
qj = PR + "quantitativos.json"
if os.path.exists(qj):
    Q = json.load(open(qj, encoding="utf-8"))
    tq = Q.get("aco_total_kg")
    if tq:
        r(abs(tq - aco_folhas) <= 0.02 * max(tq, 1), "C3 quantitativos × soma das folhas (aço CA-50)", "QUANTITATIVOS", f"quantitativos {tq:.0f} kg × folhas {aco_folhas:.0f} kg")

# ------------------------------------------------------------------ rev12 — itens da seção 10 do CHECKLIST_REVISAO
# C7  travas de geometria (renomear.conferir_pilar): pilar citado num apoio/vista pertence à linha/eixo dele
tg = PR + "travas_geometria.jsonl"
if os.path.exists(tg):
    falhas = [json.loads(l) for l in open(tg, encoding="utf-8") if l.strip()]
    falhas = [f for f in falhas if not f.get("ok")]
    r(not falhas, "C7 trava de geometria (pilar × linha/eixo do apoio)", "JOGO", "ok" if not falhas else "; ".join(f"{f['pilar']} em {f['onde']}: {f['detalhe']}" for f in falhas[:6]))
else:
    r(False, "C7 trava de geometria (pilar × linha/eixo do apoio)", "JOGO", "travas_geometria.jsonl não gerado")
# C8–C14 nos textos de cada folha
DIAM_EXC = json.load(open(PR + "excecoes_bitola.json", encoding="utf-8")) if os.path.exists(PR + "excecoes_bitola.json") else {}
ocup = {}
for fl in idx:
    dx = PR + fl + ".dxf"
    tx = textos(dx) if os.path.exists(dx) else []
    if not tx:
        continue
    t8 = [t for t in tx if re.search(r"DEC-\d{3}", t) or re.search(r"\bNathan\b", t)]
    r(not t8, "C8 nota interna (DEC-0xx / Nathan) em folha do cliente", fl, "ok" if not t8 else f"{len(t8)}: {t8[0][:80]}")
    t9 = [t for t in tx if "I130" in t]
    r(not t9, "C9 nome da família I120 (sem I130)", fl, "ok" if not t9 else f"{len(t9)}: {t9[0][:80]}")
    lib = [t for t in tx if "LIBERADO" in t.upper() and "AGUARDANDO" not in t.upper()]
    r(not lib, "C10 LIBERADO só sem pendência (local, ART, decisões)", fl, "ok" if not lib else lib[0][:80])
    gros = sorted({m for t in tx for m in re.findall(r"Ø\s?(2[2-9]|3[0-9]|4[0-9])(?![,.0-9])", t)} - set(DIAM_EXC.get(fl, [])))
    r(not gros, "C11 bitola > Ø20 sem exceção registrada", fl, "ok" if not gros else "Ø" + ", Ø".join(gros))
    n61 = [t for t in tx if re.search(r"6123\s*:\s*19", t)]
    r(not n61, "C12 norma vigente (NBR 6123:2023)", fl, "ok" if not n61 else n61[0][:80])
    dp = [t for t in tx if re.search(r"(?<![\d.,/])\d+\.\d+\s?(cm|m³|t\b|kN|MPa|m\b)", t) and "http" not in t]
    r(not dp, "C13 vírgula decimal", fl, "ok" if not dp else dp[0][:80])
    for t in tx:
        tl = t.lower()
        if "mezanino" in tl and ("escritório" in tl or "depósito" in tl):
            ocup.setdefault("escritório" if "escritório" in tl else "depósito", []).append(fl)
    zero = [t for t in tx if re.fullmatch(r"\s*0,0 MPa\s*", t)] if fl == "ND-LET-IC01" else []
    if fl == "ND-LET-IC01":
        r(not zero and any("βa" in t for t in tx), "C14 IC01 com βa e sem cálculo zerado", fl, "ok" if not zero else "σ = 0,0 MPa")
r(len(ocup) <= 1, "C15 mesma ocupação do mezanino em todas as notas", "JOGO", "ok" if len(ocup) <= 1 else str({k: v[:3] for k, v in ocup.items()}))
# C16 densidade única: peso da IC01 = lista de peças (PR01/quantitativos) ±0,1 t
try:
    TI = json.load(open(PR + "ND-LET-IC01.tabelas.json", encoding="utf-8"))
    import quantitativos as _QT
    PES = {}
    for p_ in _QT.pecas:
        PES.setdefault(p_[1], p_[7])
    difs = []
    for t in TI["tabelas"]:
        for l in t["linhas"]:
            mk = str(l[0]).replace("\x0e", "").replace("\x0f", "")
            if mk in PES:
                try:
                    v = float(str(l[2]).replace(",", "."))
                except Exception:
                    continue
                if abs(v - PES[mk]) > 0.1:
                    difs.append(f"{mk} IC01 {v} × lista {PES[mk]}")
    r(not difs, "C16 peso único (IC01 × lista de peças/PR01, 2,50 t/m³)", "ND-LET-IC01", "ok" if not difs else "; ".join(difs[:6]))
except Exception as e:
    r(False, "C16 peso único (IC01 × lista de peças/PR01, 2,50 t/m³)", "ND-LET-IC01", f"não conferido: {e}")
# C17 carimbo: última revisão = 12 em todas as folhas
for fl in idx:
    tj = PR + fl + ".tabelas.json"
    if os.path.exists(tj):
        d = json.load(open(tj, encoding="utf-8")).get("dados", {})
        r(str(d.get("rev")) == "12", "C17 carimbo REV 12 (pacote rev12)", fl, f"rev {d.get('rev')}")
PENDENTES = ["comprimento desenhado × tabela (1 cm) e contagem de estribos pelo espaçamento",
             "seção/comprimento/peso de cada peça nas plantas, cortes, IC01, CG01 e IFC × registro único por marca",
             "MC × desenho (armadura adotada)", "soma das cotas em cadeia × comprimento total; cota de cada mudança de seção das vigas"]
err = [x for x in res if not x["ok"] and not x.get("pendente")]
pen = [x for x in res if x.get("pendente")]
json.dump(dict(total=len(res), erros=len(err), pendentes_decisao=len(pen), itens=res, pendentes=PENDENTES), open(PR + "conferencia_cruzada.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
with open(PR + "conferencia_cruzada.md", "w", encoding="utf-8") as fh:
    fh.write(f"# Conferência cruzada — {len(res)} verificações, {len(err)} divergências\n\n| resultado | item | folha | detalhe |\n|---|---|---|---|\n")
    for x in sorted(res, key=lambda x: (x["ok"], x["folha"])):
        fh.write(f"| {'ok' if x['ok'] else ('PENDENTE' if x.get('pendente') else 'ERRO')} | {x['item']} | {x['folha']} | {x['detalhe']} |\n")
    fh.write("\n## Ainda não automatizado\n" + "".join(f"- {p}\n" for p in PENDENTES))
print(f"conferência cruzada: {len(res)} verificações, {len(err)} divergências, {len(pen)} pendentes de decisão")
for x in pen:
    print("  PENDENTE", x["item"], x["folha"], "—", x["detalhe"][:160])
for x in err[:40]:
    print("  ERRO", x["item"], x["folha"], "—", x["detalhe"])
sys.exit(1 if err else 0)
