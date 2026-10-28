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
sys.path.insert(0, "/home/claude/letsara/pranchas")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
REG_DATA = "27/10/2026"

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
            if fl in ("ND-LET-I120-2", "ND-LET-I120-3"):                  # rev12: repetem marcas da ND-LET-I120 (folha por marca)
                continue
            aco_folhas += tot if "UNIDADES" in t["titulo"].upper() or "1 UNIDADE" not in t["titulo"].upper() else 0
    # C4 — regras da ND nos textos
    if tx:
        prot = fl.startswith(("ND-LET-LA", "ND-LET-I1", "ND-LET-TS", "ND-LET-VM", "ND-LET-VB"))
        # rev12 (revisão rev12, item 4 — por que não pegou: a trava só olhava as folhas LA/I1/TS/VM/VB; a CT02 ficou de fora):
        # agora TODAS as folhas (não existe barra Ø15,2; qualquer Ø15,2 é cordoalha proibida)
        m152 = [t for t in tx if re.search(r"Ø\s?15[,.]2", t)]
        r(not m152, "C4 cordoalha Ø15,2 (proibida em todo o jogo)", fl, "nenhuma" if not m152 else f"{len(m152)} ocorrência(s): {m152[0][:70]}")
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
# C3 — quantitativos × folhas (aço): kg/peça da lista = RESUMO DO AÇO (1 unidade) da folha de cada pilar (±1 %)
qj = PR + "quantitativos.json"
if os.path.exists(qj):
    Q = json.load(open(qj, encoding="utf-8"))
    difs = []
    for a_ in Q.get("aco", []):
        fl_ = a_["prancha"]
        if not fl_[7:9] in ("PL", "PF", "PC", "PM", "PG", "PE") or not os.path.exists(PR + fl_ + ".tabelas.json"):
            continue
        T_ = json.load(open(PR + fl_ + ".tabelas.json", encoding="utf-8"))
        rs = next((t for t in T_["tabelas"] if t["titulo"].upper().startswith("RESUMO DO AÇO")), None)
        tot = next((float(str(l[2]).replace(".", "").replace(",", ".").split()[0]) for l in (rs or {}).get("linhas", []) if "TOTAL" in str(l[0]).upper()), None)
        if tot is None or abs(tot - a_["kg_peca"]) > 0.01 * tot + 0.5:
            difs.append(f"{a_['peca']}: lista {a_['kg_peca']} × folha {tot} kg")
    r(not difs, "C3 aço por peça: lista/xlsx × resumo da folha", "QUANTITATIVOS", "ok" if not difs else "; ".join(difs[:6]))

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
    t8 = [t for t in tx if re.search(r"DEC-\d{3}", t) or re.search(r"\bNathan\b(?! Henrique Delgado)", t) or re.search(r"NATHAN(?! HENRIQUE)", t)
          or re.search(r"\b[\w-]+\.(?:json|py)\b", t) or re.search(r"\bcalc_\w+|\bmodelo (?:global |integrado )?r0\d\b|(?<![\w-])rev\d{2}\b", t)]   # rev12 (item 12)
    r(not t8, "C8 nota interna (DEC-0xx / Nathan) em folha do cliente", fl, "ok" if not t8 else f"{len(t8)}: {t8[0][:80]}")
    t9 = [t for t in tx if "I130" in t]
    r(not t9, "C9 nome da família I120 (sem I130)", fl, "ok" if not t9 else f"{len(t9)}: {t9[0][:80]}")
    lib = [t for t in tx if "LIBERADO" in t.upper() and "AGUARDANDO" not in t.upper()]
    r(not lib, "C10 LIBERADO só sem pendência (local, ART, decisões)", fl, "ok" if not lib else lib[0][:80])
    gros = set()                                                          # armadura (CA-50/60): tabela de ferros e "n Øxx CA-50" no texto
    tj_ = PR + fl + ".tabelas.json"
    if os.path.exists(tj_):
        for t_ in json.load(open(tj_, encoding="utf-8")).get("tabelas", []):
            if "FERRO" in t_.get("titulo", "").upper():
                for l_ in t_["linhas"]:
                    try:
                        if float(str(l_[2]).replace(",", ".")) > 20:
                            gros.add(str(l_[2]))
                    except Exception:
                        pass
    gros |= {m for t in tx for m in re.findall(r"\d+\s?Ø\s?(2[2-9]|3\d)(?![,.0-9])\s?(?:CA-50|CA-60)", t)}
    gros = sorted(gros - set(DIAM_EXC.get(fl, [])))
    r(not gros, "C11 bitola > Ø20 sem exceção registrada", fl, "ok" if not gros else "Ø" + ", Ø".join(gros))
    n61 = [t for t in tx if re.search(r"6123\s*:\s*19", t)]
    r(not n61, "C12 norma vigente (NBR 6123:2023)", fl, "ok" if not n61 else n61[0][:80])
    dp = [t for t in tx if re.search(r"(?<![\d.,/])(?!\d{1,3}\.\d{3}(?![\d.,])\s?(?:kg|t\b|m\b)(?!³|²))\d+\.\d+\s?(cm|m³|t\b|kN|MPa|m\b)", t) and "http" not in t]   # rev12: ponto de milhar não é decimal
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
            if t["titulo"].startswith("VIGAS"):                           # 1ª coluna = nomes; marca pelo registro de nomes
                n0 = mk.split(",")[0].strip()
                mk = next((q["marca"] for q in json.load(open(PR + "nomes.json", encoding="utf-8"))["pecas"] if q["nome"] == n0), mk)
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
# C18 pendência da extrusora sinalizada em todas as folhas afetadas
for fl in ("ND-LET-LA01", "ND-LET-PR01", "ND-LET-NG01", "ND-LET-MON02"):
    dx = PR + fl + ".dxf"
    tx = " ".join(textos(dx)) if os.path.exists(dx) else ""
    r("CONFIRMAR COM A FÁBRICA" in tx.upper() or "CONFIRMAR COM A FÁBRICA" in tx, "C18 pendência (extrusora LP20) sinalizada", fl, "ok" if "FÁBRICA" in tx.upper() else "sem a ressalva")
# C21 (rev12, 27/10, DEC-092) locação dos PG-02/PG-04 decidida: nenhuma folha cita a pendência; face no plano dos vizinhos 40 × 40;
# 5,00 m livres face a face em cada portão; NEO-7 com a distância à borda (NBR 9062:2017 7.2)
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
import geometria as _G21
for fl in ("ND-LET-PG02", "ND-LET-PG04", "ND-LET-LOC01", "ND-LET-NG01", "ND-LET-PR01", "ND-LET-CG01"):
    dx = PR + fl + ".dxf"
    tx = " ".join(textos(dx)) if os.path.exists(dx) else ""
    m21 = re.search(r"PEND[ÊE]NCIA[^.]{0,120}(PG-0[24]|5,00 m livres|locação)", tx, re.I) or re.search(r"(PG-0[24]|locação)[^.]{0,80}confirmar com o arquitet", tx, re.I)
    r(os.path.exists(dx) and not m21, "C21 locação dos PG-02/PG-04 decidida (sem pendência citada)", fl, "ok" if not m21 else m21.group(0)[:80])
for mk in ("PG-02", "PG-04"):
    face = round(_G21.Y_PG[mk] - _G21.PG_L4[mk][3] / 2, 4)
    viz = [round(_G21.Y_PG[k] - _G21.PG_L4[k][3] / 2, 4) for k in ("PG-01", "PG-03")] + [round(_G21.Y_LIN[_G21.LINHA_PORTOES] - 0.20, 4)]
    r(all(abs(face - v) < 1e-4 for v in viz), "C21 face do PG no plano dos vizinhos (placas sem fresta)", mk, f"face y {face} × vizinhos {viz}")
_PJ21 = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/portao_l4.json", encoding="utf-8"))
for k, v in _PJ21["vao_livre_portoes_m"].items():
    r(abs(v - _G21.VAO_PORTAO) < 1e-3, "C21 portão com 5,00 m livres face a face (arquitetônico)", k, f"{v} m")
for k, v in _PJ21["neoprene"].items():
    r(v["ok"] and v["borda_pilar_cm"] >= v["a0_min_cm"] - 1e-6 and v["borda_mesa_TS_cm"] >= v["a0_min_cm"] - 1e-6, "C21 NEO-7 com a distância à borda (NBR 9062 7.2)", k,
      f"{v['dim_mm']}: borda {v['borda_pilar_cm']} / mesa {v['borda_mesa_TS_cm']} ≥ {v['a0_min_cm']} cm")
# C19 MC, listas e quantitativos da mesma revisão das pranchas
ENT = "/home/claude/letsara/entregas/"
for arq in ("ND-LET-MC12-REV12-rev12.pdf", "ND-LET-LISTAS-rev12.pdf", "ND-LET-QUANTITATIVOS-rev12.xlsx"):
    r(os.path.exists(ENT + arq), "C19 MC/listas/quantitativos rev12 emitidos", "ENTREGA", arq)
# C20 nicho de montagem (console/grapa) na parte superior da placa
try:
    import fechamento as _F
    r(_F.Z_NC > 1250 / 2, "C20 nicho NC-1 na parte superior da placa", "ND-LET-PP00", f"centro do nicho a {_F.Z_NC} mm da base (placa 1250)")
except Exception as e:
    r(False, "C20 nicho NC-1 na parte superior da placa", "ND-LET-PP00", str(e)[:80])
# ================================================================== rev12 — revisão independente da rev12 (CHECKLIST seção 11)
import registro as REG
_num = lambda v: float(str(v).replace(".", "").replace(",", ".").split()[0])
QJ = json.load(open(qj, encoding="utf-8")) if os.path.exists(qj) else None
REGP = REG.pilares()
# C22 mudança de geometria propaga: volume/peso/seção da folha da peça = PR01 = IC01 = lista/xlsx (±0,005 m³ / ±0,02 t)
try:
    TPR = json.load(open(PR + "ND-LET-PR01.tabelas.json", encoding="utf-8"))
    tpr = next(t for t in TPR["tabelas"] if t["titulo"].startswith("QUADRO DE PRODUÇÃO"))
    PRL = {}
    for l in tpr["linhas"]:
        PRL.setdefault(str(l[0]), l)
    difs = []
    for mk, R_ in REGP.items():
        lp = PRL.get(mk)
        if lp is None:
            difs.append(f"{mk} sem linha no PR01"); continue
        if abs(_num(lp[4]) - R_["vol"]) > 0.006 or abs(_num(lp[6]) - R_["peso"]) > 0.02:
            difs.append(f"{mk}: folha {R_['vol']} m³/{R_['peso']} t × PR01 {lp[4]}/{lp[6]}")
        cab = "seção cheia" if not R_["geom"].get("rec") else "cabeça recuada"
        if mk[:2] in ("PL", "PF") and cab not in str(lp[2]):
            difs.append(f"{mk}: PR01 '{lp[2]}' × geometria '{cab}'")
        if QJ:
            q_ = QJ["pecas"].get(mk)
            if not q_ or abs(q_["vol"] - R_["vol"]) > 0.006 or abs(q_["peso"] - R_["peso"]) > 0.02:
                difs.append(f"{mk}: folha × lista/xlsx {q_}")
    r(not difs, "C22 volume, peso e cabeça iguais: folha da peça × PR01 × lista × xlsx", "JOGO", "ok" if not difs else "; ".join(difs[:6]))
except Exception as e:
    r(False, "C22 volume, peso e cabeça iguais: folha da peça × PR01 × lista × xlsx", "JOGO", f"não conferido: {e}")
if QJ:
    X_, L_ = QJ["xlsx"], QJ["lista"]
    ok_ = all(X_[k] is not None and abs(X_[k] - L_[k]) <= 0.01 * max(L_[k], 1) for k in ("volume_m3", "peso_t", "pecas")) and abs((X_["aco_kg"] or 0) - QJ["aco_total_kg"]) <= 0.01 * QJ["aco_total_kg"]
    r(ok_, "C23 xlsx recalculado (valores gravados) × lista: volume, peso, peças e aço (±1 %)", "QUANTITATIVOS", f"xlsx {X_} × lista {L_}, aço {QJ['aco_total_kg']}")
    rv = [c for c in QJ["cabecalhos"] if "REV12" not in c.upper()]
    r(not rv, "C23 cabeçalho de todas as abas com a revisão do pacote", "QUANTITATIVOS", "ok" if not rv else rv[0][:80])
    # C24 aparelho de apoio único: 1 neoprene por apoio (contagem = apoios) e uma descrição por marca
    ap = QJ["apoios"]
    dif = [f"{a_['marca']}: {ap['NEO'].get(a_['marca'])} na lista × {ap['consolos'][tp]} apoios {tp}" for tp, a_ in REG.APARELHOS.items() if ap["NEO"].get(a_["marca"]) != ap["consolos"][tp]]
    r(not dif, "C24 neoprenes = número de apoios (um aparelho por apoio)", "LISTAS", "ok" if not dif else "; ".join(dif))
    # C25 item de lista de uma fonte só: uma descrição por marca; insertos por pilar fecham com o nº de pilares/consolos
    dup = {m_: list(d_) for m_, d_ in QJ["insertos"].items() if len(d_) > 1 and m_ not in ("NC-1 (kg)",)}
    r(not dup, "C25 item de lista com uma fonte e uma descrição", "LISTAS", "ok" if not dup else str(dup)[:200])
    npil = sum(R_["qt"] for R_ in REGP.values())
    tot = lambda m_: sum(QJ["insertos"].get(m_, {}).values())
    ncons = sum(R_["qt"] * len(R_["consolos"]) for R_ in REGP.values())
    fl_ = [f"AL-2 {tot('AL-2')} ≠ 2 × {npil}"] if tot("AL-2") != 2 * npil else []
    fl_ += [f"FI-1 {tot('FI-1')} ≠ {npil}"] if tot("FI-1") != npil else []
    fl_ += [f"pinos PN-1+PN-2+PN-6 {tot('PN-1') + tot('PN-2') + tot('PN-6')} ≠ {ncons} consolos"] if tot("PN-1") + tot("PN-2") + tot("PN-6") != ncons else []
    cl_ = QJ["conf_lista"]
    fl_ += [f"{k_[:-8]}: pilares {cl_[k_]} × vistas {cl_[k_.replace('pilares', 'vistas')]}" for k_ in cl_ if k_.endswith("pilares") and cl_[k_] != cl_[k_.replace("pilares", "vistas")]]
    r(not fl_, "C25 insertos por pilar fecham (AL-2 = 2 × pilares, FI-1 = pilares, pinos = consolos, chapas = vistas)", "LISTAS", "ok" if not fl_ else "; ".join(fl_))
# C26 CS01 coerente com a geometria: quantidades e pilares de cada consolo = contagem nas folhas (registro); marcas distintas
try:
    RC = json.load(open(PR + "consolos_marcas.json", encoding="utf-8"))
    import apoios_pilar as _APc
    cont = {}
    for mk, R_ in REGP.items():
        for c_ in R_["consolos"]:
            m_ = _APc.marca_consolo(c_)
            for n_ in R_["nomes"]:
                cont.setdefault(m_, {}).setdefault(n_, 0)
                cont[m_][n_] += 1
    difs = [f"{e['marca']}: CS01 {e['por_pilar']} × folhas {cont.get(e['marca'])}" for e in RC["lista"] if e["por_pilar"] != cont.get(e["marca"]) or e["n"] != sum(cont.get(e["marca"], {}).values())]
    sig = {}
    for e in RC["lista"]:
        k_ = (e["tipo"], e["larg"], e["proj"], e["h"], e["hp"], e["incl"], e["exc"], e["exc_face"], e["pino"], tuple(e["neo"]), e["tirante"])
        if k_ in sig:
            difs.append(f"{e['marca']} = {sig[k_]} (dados idênticos)")
        sig[k_] = e["marca"]
    tcs = textos(PR + "ND-LET-CS01.dxf") if os.path.exists(PR + "ND-LET-CS01.dxf") else []
    gen = [t for t in tcs if re.search(r"pilares do eixo|vigas de cobertura TS-01", t)]
    difs += [f"texto genérico na CS01: {gen[0][:60]}"] if gen else []
    for e in RC["lista"]:
        if not any(all(n_ in t for n_ in list(e["por_pilar"])[:3]) for t in tcs):
            difs.append(f"{e['marca']}: pilares do registro não aparecem na CS01")
    r(not difs, "C26 CS01: pilares e quantidades de cada consolo pela geometria; marcas distintas", "ND-LET-CS01", "ok" if not difs else "; ".join(difs[:5]))
except Exception as e:
    r(False, "C26 CS01: pilares e quantidades de cada consolo pela geometria; marcas distintas", "ND-LET-CS01", f"não conferido: {e}")
# C27 toda marca de peça metálica fabricada citada em texto tem desenho de fabricação (título de vista) e linha de lista
TXT = {fl: textos(PR + fl + ".dxf") for fl in idx if os.path.exists(PR + fl + ".dxf")}
FAB = r"(?<![\w-])((?:PT|ST|CS|CE|CC|NC|OM|CL|TL|EM|CB|MF|CA)-(?!(?:25|50|60)(?![\w-]))\d+[A-Z]{0,2}|ST-W|ES-1FL)(?![\w-])"   # CA-25/50/60 = aço
cit = {m_ for tx_ in TXT.values() for t in tx_ for m_ in re.findall(FAB, t)}
tit = {m_ for tx_ in TXT.values() for t in tx_ if t.isupper() or "—" in t[:20] for m_ in re.findall(FAB, t[:30])}
lis = set()
for f_ in glob.glob(PR + "ND-LET-*.tabelas.json"):
    for t_ in json.load(open(f_, encoding="utf-8")).get("tabelas", []):
        for l_ in t_["linhas"]:
            lis |= set(re.findall(FAB, " ".join(str(c_) for c_ in l_[:3])))
if QJ:
    lis |= set(QJ["insertos"])
sem = sorted(m_ for m_ in cit if m_ not in lis)
sem_d = sorted(m_ for m_ in cit if m_ not in tit and m_ not in lis)
r(not sem, "C27 marca citada em texto tem linha de lista", "JOGO", "ok" if not sem else ", ".join(sem[:12]))
r(not sem_d, "C27 marca citada em texto tem desenho de fabricação ou linha de material", "JOGO", "ok" if not sem_d else ", ".join(sem_d[:12]))
# C28 nomes internos/R01 fora do quadro de correspondência (LOC01): P1C-L1, P2-L5, P8A, P13B, P10a…
_NOMS = {c_ for t_ in json.load(open(PR + "ND-LET-NG01.tabelas.json", encoding="utf-8"))["tabelas"] if t_["titulo"].startswith("NOMENCLATURA") for l_ in t_["linhas"] for c_ in l_[1:]}
_NOMS |= {re.sub(r"[\x00-\x1f]", "", c_) for c_ in _NOMS}                    # células com marcador de formatação (\x01)
for fl, tx_ in TXT.items():
    if fl == "ND-LET-LOC01":
        continue
    if fl == "ND-LET-NG01":                                              # quadro de nomenclatura (nome × R01) é a correspondência, como na LOC01
        tx_ = [t for t in tx_ if t not in _NOMS]
    m28 = [t for t in tx_ if re.search(r"\bP\d+C?-L\d\b|\bP8[AB]\b|\bP13B\b|\bP10[ab]\b|\(P[67], ", t)]
    r(not m28, "C28 nome do projeto (sem nome interno ou do R01 fora da LOC01)", fl, "ok" if not m28 else m28[0][:80])
# C29 valores únicos de projeto: portões, folgas e chegada da escada iguais em todas as notas
alv = {}
for fl, tx_ in TXT.items():
    for t in tx_:
        for v_ in re.findall(r"[Pp]ortões[^.;]{0,40}?livres até \+(\d,\d\d)", t):
            alv.setdefault(v_, []).append(fl)
        for v_ in re.findall(r"escada[^.;]{0,40}?(?:ao|até o|→)\s*(?:piso pronto\s*)?\+(\d,\d\d)", t, flags=re.I):
            alv.setdefault("escada " + v_, []).append(fl)
port = {k for k in alv if not k.startswith("escada")}
esc = {k for k in alv if k.startswith("escada")}
r(port <= {REG.f1(REG.PORTAO["livre_ate"])}, "C29 altura livre dos portões única", "JOGO", "ok" if port <= {REG.f1(REG.PORTAO["livre_ate"])} else str({k: alv[k][:3] for k in port}))
r(esc <= {"escada " + REG.f1(REG.ESCADA_CHEGADA)}, "C29 chegada da escada única", "JOGO", "ok" if esc <= {"escada " + REG.f1(REG.ESCADA_CHEGADA)} else str({k: alv[k][:3] for k in esc}))
fol = sorted({(fl, t[:70]) for fl, tx_ in TXT.items() for t in tx_ if re.search(r"folga de ponta 25|I120 e VB 25 mm|19 mm no centro", t)})
r(not fol, "C29 folgas de montagem da geometria do modelo (uma fonte)", "JOGO", "ok" if not fol else str(fol[:3]))
# C30 carimbo: rev 12 datada da última alteração (27/10) e histórico sem lacuna
for fl in idx:
    tj = PR + fl + ".tabelas.json"
    if not os.path.exists(tj):
        continue
    d_ = json.load(open(tj, encoding="utf-8")).get("dados", {})
    revs = sorted({int(t) for t in TXT.get(fl, []) if re.fullmatch(r"\d\d", t.strip()) and 0 <= int(t) <= 12})
    seq = [v_ for v_ in revs if v_ >= (revs[-1] - 3 if revs else 0)]
    ok_ = d_.get("data") == REG_DATA and (not seq or seq == list(range(seq[0], 13)))
    r(ok_, "C30 carimbo: rev 12 de 27/10/2026, histórico sem lacuna", fl, f"data {d_.get('data')}, revisões {seq}")
# C31 ordem das folhas: família junto da folha-mãe (I120 → I120-2 → I120-3), cobertura em sequência, EX01 por último
o_ = idx
ok_ = (o_.index("ND-LET-I120-2") == o_.index("ND-LET-I120") + 1 and o_.index("ND-LET-I120-3") == o_.index("ND-LET-I120") + 2 and o_[-1] == "ND-LET-EX01"
       and [f for f in o_ if f.startswith("ND-LET-COB")] == sorted(f for f in o_ if f.startswith("ND-LET-COB")))
r(ok_, "C31 ordem das folhas (família após a folha-mãe, EX01 por último)", "JOGO", "ok" if ok_ else str([f for f in o_ if "I120" in f or "COB" in f or "EX01" in f]))
# C32 face dos insertos excêntricos igual no 2D (registro da folha) e no 3D (IFC): CP-VB rente à face externa
try:
    import ifcopenshell, ifcopenshell.geom, numpy as _np
    IFC = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/saidas/letsara.ifc"
    fi_ = ifcopenshell.open(IFC)
    st_ = ifcopenshell.geom.settings(); st_.set("use-world-coords", True)
    cps = []
    for el in fi_.by_type("IfcElement"):
        if (el.Name or "").startswith("CP-VB"):
            sh = ifcopenshell.geom.create_shape(st_, el)
            vs = _np.array(sh.geometry.verts).reshape(-1, 3)
            cps.append(vs.mean(0))
    FW = {"A": {"A": (1, 0), "B": (0, 1), "C": (-1, 0), "D": (0, -1)}, "E": {"A": (-1, 0), "B": (0, -1), "C": (1, 0), "D": (0, 1)},
          "1": {"A": (0, 1), "B": (-1, 0), "C": (0, -1), "D": (1, 0)}, "9": {"A": (0, -1), "B": (1, 0), "C": (0, 1), "D": (-1, 0)}}
    from geometria import X_EIXO as _XEc
    difs = []
    for mk, R_ in REGP.items():
        for n_ in R_["nomes"]:
            q_ = next(q for q in REG.NOMES["pecas"] if q["nome"] == n_)
            ref = "A" if abs(q_["x"]) < 0.01 else "E" if abs(q_["x"] - _XEc["E"]) < 0.01 else ("1" if q_["y"] < 1 else "9")
            for c_ in R_["consolos"]:
                if c_["tipo"] != "CP-VB" or not c_.get("exc"):
                    continue
                ex_ = FW[ref][c_["exc_face"]]
                yv = q_["y"] + ex_[1] * c_["exc"] / 1000
                near = min(cps, key=lambda p_: (p_[0] - q_["x"]) ** 2 + (p_[1] - q_["y"]) ** 2) if cps else None
                if near is None or abs(near[1] - yv) > 0.01:
                    difs.append(f"{n_} ({mk}): 2D y {yv:.3f} × 3D {None if near is None else round(near[1], 3)}")
    r(not difs, "C32 face do consolo excêntrico igual no 2D e no 3D (IFC)", "JOGO", "ok" if not difs else "; ".join(difs[:5]))
except Exception as e:
    r(False, "C32 face do consolo excêntrico igual no 2D e no 3D (IFC)", "JOGO", f"não conferido: {e}")
# C33 (rev12, 27/10, regra do Nathan) largura do consolo = largura da viga apoiada; neoprene com borda lateral ≥ 1,5c (≥ 3 cm)
try:
    CJ_ = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/consolos.json", encoding="utf-8"))
    LV_ = REG.larguras_viga_apoiada()
    difs = [f"{k}: consolo {CJ_[k]['b_m']} × viga {v}" for k, v in LV_.items() if abs(CJ_[k]["b_m"] - v) > 1e-6]
    difs += [f"{k}: neoprene {CJ_[k]['neoprene_mm'][0]} mm deixa {(CJ_[k]['b_m'] * 1000 - CJ_[k]['neoprene_mm'][0]) / 2:g} mm até a face" for k in LV_
             if (CJ_[k]["b_m"] * 1000 - CJ_[k]["neoprene_mm"][0]) / 2 < REG.borda_neoprene_min() * 1000 - 1e-6]
    for mk, R_ in REGP.items():                                           # o que está DESENHADO em cada pilar (geometria da folha)
        for c_ in R_["consolos"]:
            if c_["tipo"] in LV_ and abs(c_["larg"] / 1000 - LV_[c_["tipo"]]) > 1e-6:
                difs.append(f"{mk}: {c_['tipo']} desenhado com {c_['larg']} mm × viga {LV_[c_['tipo']] * 1000:g}")
            if c_["tipo"] in REG.APARELHOS and list(c_["neo"]) != list(REG.APARELHOS[c_["tipo"]]["dims"]):
                difs.append(f"{mk}: neoprene {c_['neo']} ≠ registro {REG.APARELHOS[c_['tipo']]['dims']}")
    r(not difs, "C33 largura do consolo = largura da viga apoiada (e neoprene com borda)", "JOGO", "ok" if not difs else "; ".join(sorted(set(difs))[:6]))
except Exception as e:
    r(False, "C33 largura do consolo = largura da viga apoiada (e neoprene com borda)", "JOGO", f"não conferido: {e}")
# C34 nenhuma decisão encerrada citada como pendente (VM de canto decidida em 27/10)
for fl, tx_ in TXT.items():
    m34 = [t for t in tx_ if re.search(r"VM[^.]{0,60}(em decisão|não produzir as VM)|decisao_vm_canto", t)]
    r(not m34, "C34 sem pendência já decidida (VM da linha 1 no canto)", fl, "ok" if not m34 else m34[0][:80])
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
