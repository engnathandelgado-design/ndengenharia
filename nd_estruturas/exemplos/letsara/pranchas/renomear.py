"""Nomenclatura nova da Letsara (padrão do Nathan, 22/10/2026) aplicada no texto das folhas.

Regra: pilares P1…P36 e vigas V200…/V300…/V400… (um nome por peça, sentido de leitura — nomes.py/nomes.json).
Os geradores continuam usando as marcas internas (PL-01, TS-01B, VB-03…) e as referências do projeto do cliente (R01:
"P1 L5", "P8A", "P13"…) como chave; este módulo troca, no TEXTO desenhado, cada marca interna pela lista de nomes das
peças que ela representa e cada referência R01 pelo nome novo da posição. Um passe só (regex com todas as chaves), então
um nome novo nunca é trocado de novo. Texto que já vem com nome novo começa com MARCA_NOVO (é só tirado o marcador).
"""
import json, os, re, sys
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
PR = "/home/claude/letsara/pranchas/"
MARCA_NOVO = "\x01"
NV0, NV1 = "\x0e", "\x0f"          # rev12: proteção INLINE de nome novo (pode estar no meio do texto)
_D = json.load(open(PR + "nomes.json", encoding="utf-8"))
M2N = {k: v for k, v in _D["marca_para_nomes"].items()}
# I120: no R01 / nas folhas antigas as vigas centrais eram V405/V406/V407
I120_ANT = {"V404", "V405", "V406", "V407"}   # DEC-058: 4 vigas centrais


def _num(n):
    return int(re.sub(r"\D", "", n))


def lista(nomes, sep=", "):
    """['V409','V410','V413',...,'V420'] → 'V409, V410, V413, V414, …, V420'.
    Regra do Nathan (22/10/2026): SEMPRE o nome de cada peça escrito por extenso — nunca "P29 a P32" (a fôrma confunde)."""
    ns = sorted(set(nomes), key=lambda n: (n[0], _num(n)))
    out, i = [], 0
    while i < len(ns):
        j = i
        while j + 1 < len(ns) and ns[j + 1][0] == ns[i][0] and _num(ns[j + 1]) == _num(ns[j]) + 1:
            j += 1
        out += ns[i:j + 1]
        i = j + 1
    return sep.join(out)


def nomes_de(marca):
    return M2N.get(marca, [])


# referências do R01 → nome novo
R01 = {}
for p in _D["pecas"]:
    if p["tipo"] == "pilar":
        R01.setdefault(p["ref_R01"], []).append(p["nome"])
def _pil_xy(x, y):
    return min((p for p in _D["pecas"] if p["tipo"] == "pilar"), key=lambda p: (p["x"] - x) ** 2 + (p["y"] - y) ** 2)["nome"]


_Y4 = sorted({p["y"] for p in _D["pecas"] if p["tipo"] == "pilar" and p.get("linha") == 4})[0]
P10A, P10B = _pil_xy(15.195, _Y4), _pil_xy(24.305, _Y4)          # rev09: calculados (a numeração muda com os pilares da escada)
R01["P10a"], R01["P10b"] = [P10A], [P10B]
_P6E, _P7E, _P5L2 = _pil_xy(36.175, 3.79), _pil_xy(39.5, 3.79), _pil_xy(36.175, 9.65)   # rev12: pilares da escada e da linha 2 (R01 P6/P7)          # portões: P10a = PG-02 (x 15,195), P10b = PG-04 (x 24,305)
# R01 sem a linha (P3 = P3 L1 e P3 L9 …); P1/P2 sozinhos são tratados à parte (famílias dos eixos A/E)
for k, v in list(R01.items()):
    if " L" in k:
        R01.setdefault("BASE:" + k.split()[0], []).extend(v)
for k in [k for k in R01 if k.startswith("BASE:")]:
    base = k[5:]
    if base not in R01 and base not in ("P1", "P2"):
        R01[base] = R01[k]
    del R01[k]
R01["P1"], R01["P2"] = [_pil_xy(0.0, 0.0)], [_pil_xy(39.5, 0.0)]               # só usados se a célula for exatamente "P1"/"P2" (raro)
POS_V = {p["nome"]: p.get("posicao", "") for p in _D["pecas"] if p["tipo"] == "viga"}
TS_TODAS = sorted({n for k in ("TS-01", "TS-01A", "TS-01B") for n in M2N.get(k, [])}, key=_num)

CHAVES = {}
for k, v in M2N.items():
    CHAVES[k] = v
for k, v in R01.items():
    for var in {k, k.replace(" L", "-L")}:
        CHAVES.setdefault(var, v)
_pat = re.compile(r"(?<![\w-])(" + "|".join(re.escape(k) for k in sorted(CHAVES, key=len, reverse=True)) + r")(?![\w])")
LOG = []


def _renomear(s):
    if not isinstance(s, str) or not s:
        return s
    if s.startswith(MARCA_NOVO):
        return s[1:].replace(NV0, "").replace(NV1, "")
    prot = []

    def guarda(txt):
        prot.append(txt)
        return f"\x02{len(prot) - 1}\x03"
    # rev12 (revisão independente rev11, causa raiz): nome novo vindo do código (N(), pilar/viga por posição) fica protegido
    # mesmo no meio do texto — a renomeação é aplicada UMA vez só (P13 novo nunca vira o "P13" do R01).
    s = re.sub(NV0 + "(.*?)" + NV1, lambda m: guarda(m.group(1)), s)
    # rev12: nomes do R01 da escada/linha 2 (P6/P7 do R01 colidem com P6/P7 do projeto) — sempre convertidos pela posição
    s = re.sub(r"(?<![\w-])P6 e (o )?P7 da escada(?![\w])", lambda m: guarda(_P6E) + " e " + (m.group(1) or "") + guarda(_P7E) + " da escada", s)
    s = re.sub(r"(?<![\w-])P6/P7(?![\w])", lambda m: guarda(_P6E) + "/" + guarda(_P7E), s)
    s = re.sub(r"(?<![\w-])P6(?:-L2| \(linha 2\)| da linha 2| na linha 2)(?![\w])", lambda m: guarda(_P5L2), s)
    s = re.sub(r"(?<![\w-])P6(?:E| \(escada\)| da escada)(?![\w])", lambda m: guarda(_P6E), s)
    s = re.sub(r"(?<![\w-])P7(?:E| \(escada\)| da escada)(?![\w])", lambda m: guarda(_P7E), s)
    s = re.sub(r"(?<![\w-])D\s*(–|-|→)\s*P6(?![\w])", lambda m: "D " + m.group(1) + " " + guarda(_P5L2), s)
    s = re.sub(r"(?<![\w-])P6\s*(–|-|→)\s*E(?![\w])", lambda m: guarda(_P5L2) + " " + m.group(1) + " E", s)
    s = re.sub(r"(?<![\w-])P6\s*(–|-|→|/)\s*P7(?![\w])", lambda m: guarda(_P6E) + " " + m.group(1) + " " + guarda(_P7E), s)
    s = re.sub(r"(?<![\w-])(o |do |entre o |entre )?P6, (o |do )?P7(?![\w])", lambda m: (m.group(1) or "") + guarda(_P6E) + ", " + (m.group(2) or "") + guarda(_P7E), s)
    s = re.sub(r"(?<![\w-])P6 e (o )?P7(?![\w])", lambda m: guarda(_P6E) + " e " + (m.group(1) or "") + guarda(_P7E), s)
    inteiro = s.strip() in CHAVES

    def rep(m):
        k = m.group(1)
        if k == "TS-01" and not inteiro:                   # na prosa "TS-01" é a família inteira das vigas de cobertura
            return "vigas de cobertura TS-01"
        if k in ("P1", "P2") and not inteiro:              # R01: P1/P2 sozinhos = pilares laterais dos eixos A/E
            return "pilares do eixo " + ("A" if k == "P1" else "E")
        return lista(CHAVES[k])
    # pré-passes: faixas do R01 ("P2 L5–L8") e "TS-01 … da linha N" — o resultado vai num marcador protegido do passe principal
    def faixa(m):
        lado, a, b = m.group(1), int(m.group(2)), int(m.group(3))
        return guarda(lista([n for li in range(a, b + 1) for n in R01.get(f"P{lado} L{li}", [])]))
    s2 = re.sub(r"(?<![\w-])P([12]) L(\d)\s*[–-]\s*L?(\d)", faixa, s)

    def ts_linha(m):
        li = m.group(3)
        ns = [n for n in TS_TODAS if POS_V.get(n, "").startswith(f"linha {li}")]
        return (guarda(lista(ns)) if ns else m.group(1)) + m.group(2) + li
    s2 = re.sub(r"(?<![\w-])(TS-01[AB]?)(\s+(?:da|na|das|nas)\s+linhas?\s+)(\d)", ts_linha, s2)
    # marca + referência do R01 da MESMA peça ("PL-01 (P1-L5)", "P1-L5 PL-01", "P8 / P8B PM-01"): fica só o nome da posição
    MK = r"(?:PL|PF|PC|PM|PG|PE)-\d\d"
    RF = r"(?:P\d+[ -]L\d|P8A|P8B|P10a|P10b|P\d+)"
    nome_r = lambda r: lista(R01.get(r, R01.get(r.replace("-L", " L"), [r])))
    s2 = re.sub(r"P10 \(x 15,195\)", lambda m: guarda(P10A) + " (x 15,195)", s2)
    s2 = re.sub(r"P10 \(x 24,305\)", lambda m: guarda(P10B) + " (x 24,305)", s2)
    s2 = re.sub(rf"(?<![\w-]){MK} \(({RF})\)", lambda m: guarda(nome_r(m.group(1))), s2)
    def ref_mk(m):
        refs = [r.strip() for r in m.group(1).split("/")]
        mk = m.group(2)
        out = []
        for r in refs:
            ns = R01.get(r, R01.get(r.replace("-L", " L"), []))
            if len(ns) != 1:                                   # R01 ambíguo (P10): vale a marca, se ela for uma peça só
                ns = [n for n in M2N.get(mk, []) if n in ns] or M2N.get(mk, ns)
            out.append(lista(ns))
        return guarda(" / ".join(out))
    s2 = re.sub(rf"(?<![\w-])({RF}(?:\s*/\s*{RF})*) ({MK})(?![\w-])", ref_mk, s2)
    s2 = re.sub(r"(?<![\w-])VB-0(\d) a (?:VB-)?0(\d)", lambda m: guarda(lista([n for k in range(int(m.group(1)), int(m.group(2)) + 1) for n in M2N.get(f"VB-0{k}", [])])), s2)
    s2 = re.sub(r"(?<![\w-])VB-0(\d) A (?:VB-)?0(\d)", lambda m: guarda(lista([n for k in range(int(m.group(1)), int(m.group(2)) + 1) for n in M2N.get(f"VB-0{k}", [])])), s2)
    s2 = re.sub(r"assento (?:da |das )?TS-01(?![\w-])", lambda m: "assento da " + guarda("viga de cobertura TS-01"), s2)
    # "TS-01" na prosa = a família das vigas de cobertura (cada peça tem o seu nome na planta e na folha das vigas)
    s2 = re.sub(r"(?<![\w-])(d|n)?(as|os) TS-01(?![\w-])", lambda m: (m.group(1) or "") + m.group(2) + " " + guarda("vigas de cobertura TS-01"), s2)
    s2 = re.sub(r"(?<![\w-])(d|n)?(a|o) TS-01(?![\w-])", lambda m: (m.group(1) or "") + m.group(2) + " " + guarda("viga de cobertura TS-01"), s2)
    s2 = re.sub(r"(?<![\w-])(d|n|a)o (P[12])(?![\w\s]*L\d)(?![\w])", lambda m: f"{m.group(1)}os {guarda('pilares do eixo ' + ('A' if m.group(2) == 'P1' else 'E'))}", s2)
    t = _pat.sub(rep, s2)
    for _ in range(3):                                                    # marcadores podem estar aninhados
        t = re.sub("\x02(\\d+)\x03", lambda m: prot[int(m.group(1))], t)
    t = t.replace(NV0, "").replace(NV1, "")
    t = re.sub(r"(vigas? de cobertura TS-01) (?:de|da) cobertura", r"\1", t)          # rev12: sem "de cobertura de cobertura"
    t = re.sub(r"(?<![\w-])((?:[PV]\d+)(?:(?:, | a )[PV]\d+)*) \(\1\)", r"\1", t)     # "P10 (P10)" → "P10"
    t = re.sub(r"(?<![\w-])([PV]\d+) \(\1, ", r"\1 (", t)                                   # "P15 (P15, 40×60)" → "P15 (40×60)"
    if t != s:
        LOG.append((s, t))
        if os.environ.get("RENOMEAR_LOG"):
            with open(os.environ["RENOMEAR_LOG"], "a", encoding="utf-8") as fh:
                fh.write(json.dumps([s, t], ensure_ascii=False) + "\n")
    return t



_RX_NATHAN = [
    (re.compile(r"\s*\([^()]*\bNathan\b[^()]*\)"), ""),
    (re.compile(r"\s*[,;—–-]?\s*\b(?:decisão|decisões|pedido|regra|padrão|definição|opção [A-Z])(?: pendente)? do Nathan\b(?:,?\s*\(?\d{2}/\d{2}(?:/\d{4})?\)?)?"), ""),
    (re.compile(r"\s*[,;—–-]?\s*\bNathan\b(?:,?\s*\d{2}/\d{2}(?:/\d{4})?)?"), ""),
    (re.compile(r"\bDEC-\d{3}(?:/\d{3})*(?:\s*(?:e|,|/)\s*DEC-\d{3}(?:/\d{3})*)*"), ""),
    (re.compile(r"\(\s*[,;:—–-]?\s*(?:rev\d{2}\s*[,;]?\s*)?\)"), ""),
    (re.compile(r"\(\s*[,;:]\s*"), "("),
    (re.compile(r"\s*[,;]\s*\)"), ")"),
    (re.compile(r"\(\s+"), "("),
    (re.compile(r"(^\s*|[.(]\s*)[—–:-]\s+"), r"\1"),
    (re.compile(r"[ \t]+([,;:.)])"), r"\1"),
    (re.compile(r"([,;:])(?:\s*[,;:])+"), r"\1"),
    (re.compile(r"[ \t]{2,}"), " "),
]


def limpar_interno(s):
    """rev12 (checklist 10): folha do cliente sem nota interna da ND — sem "DEC-0xx" nem "decisão/pedido/regra do Nathan"."""
    if not isinstance(s, str) or ("DEC-" not in s and "Nathan" not in s):
        return s
    for rx, rep in _RX_NATHAN:
        s = rx.sub(rep, s)
    return s.strip() if s.strip() else s


def renomear(s):
    return limpar_interno(_renomear(s))


def novo(s):
    """marca um texto que já está com o nome novo (não passa pela troca)."""
    return MARCA_NOVO + s


def pilar_em(x, y, tol=0.6):
    """nome do pilar na posição da obra (x = eixo A→E, y = linha 1→9, em m)."""
    ps = [p for p in _D["pecas"] if p["tipo"] == "pilar"]
    p = min(ps, key=lambda p: (p["x"] - x) ** 2 + (p["y"] - y) ** 2)
    return p["nome"] if ((p["x"] - x) ** 2 + (p["y"] - y) ** 2) ** 0.5 <= tol else None


def N(nome):
    """rev12: protege um nome novo (P…, V…, lista de nomes) dentro de qualquer texto — não passa pela troca do R01."""
    return NV0 + str(nome) + NV1 if nome else nome


def N_pilar(x, y, tol=0.6):
    n = pilar_em(x, y, tol)
    return N(n) if n else n


TRAVA = os.environ.get("TRAVAS_LOG") or (PR + "travas_geometria.jsonl")


def conferir_pilar(nome, onde, linha=None, eixo=None, x=None, y=None, tol=0.6):
    """rev12 (trava pela geometria): o pilar citado num apoio/vista/tabela tem de estar na linha/eixo/posição daquele apoio.
    Divergência vai para travas_geometria.jsonl e a conferência cruzada dá ERRO."""
    nome = str(nome).replace(NV0, "").replace(NV1, "").replace(MARCA_NOVO, "")
    p = next((q for q in _D["pecas"] if q["tipo"] == "pilar" and q["nome"] == nome), None)
    ok, det = True, ""
    if p is None:
        ok, det = False, "pilar inexistente"
    else:
        from geometria import Y_LIN as _YL, X_EIXO as _XE
        if linha is not None and abs(p["y"] - _YL[linha - 1]) > tol:
            ok, det = False, f"não está na linha {linha} (y {p['y']})"
        if eixo is not None and abs(p["x"] - _XE[eixo]) > tol:
            ok, det = False, f"não está no eixo {eixo} (x {p['x']})"
        if x is not None and y is not None and ((p["x"] - x) ** 2 + (p["y"] - y) ** 2) ** 0.5 > tol:
            ok, det = False, f"não está em ({x}, {y})"
    with open(TRAVA, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(dict(ok=ok, pilar=nome, onde=onde, detalhe=det), ensure_ascii=False) + "\n")
    return ok


def viga_em(nivel, x, y, tol=0.6, marcas=None):
    """nome da viga do nível ('+3,90', '+7,30', 'cobertura') mais próxima do ponto (x, y) da obra (m) — distância ao
    eixo da peça em planta (segmento x0,y0 → x1,y1)."""
    best, dmin = None, 1e9
    for p in _D["pecas"]:
        if p["tipo"] != "viga" or p["nivel"] != nivel or (marcas and not p["marca"].startswith(tuple(marcas))):
            continue
        ax, ay, bx, by = p["x0"], p["y0"], p["x1"], p["y1"]
        dx, dy = bx - ax, by - ay
        t = 0.0 if dx == dy == 0 else max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
        d = ((ax + t * dx - x) ** 2 + (ay + t * dy - y) ** 2) ** 0.5
        if d < dmin - 1e-9:
            best, dmin = p["nome"], d
    return best if dmin <= tol else None


# rev11 (26/10/2026, pedido do Nathan): plantas de fôrmas/montagem indicam NOME + SEÇÃO de cada peça (ex.: "V400 I120 h120",
# "V200 30×75", "P11 40×40"). Seções lidas das fontes das folhas de detalhamento (nada digitado solto).
def _secoes_vigas():
    AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
    LG = json.load(open(AQ + "ligacoes.json"))
    vp = json.load(open(AQ + "vm_retangular.json"))["premissas"]          # mesma fonte da MON02 / VM01
    b_vm, h_vm = round(vp["b"] * 100), round(vp["h_pm"] * 100)
    import ts01_dados as TD
    return {"VM": f"{b_vm}×{h_vm}", "VB": "15×60", "TS": f"I{TD.H // 10} h{TD.H // 10}", "V4": "I120"}


_SEC_V = None


def secao(nome):
    """seção da peça (cm) pelo nome novo (P…, V…)."""
    global _SEC_V
    p = next((q for q in _D["pecas"] if q["nome"] == nome), None)
    if p is None:
        return ""
    if p["tipo"] == "pilar":
        return p["secao"]
    if _SEC_V is None:
        _SEC_V = _secoes_vigas()
    return _SEC_V.get(p["marca"][:2], "")


def rotulo(nome):
    """'V400 I120 h120' — nome por extenso + seção (já marcado como nome novo)."""
    s = secao(nome)
    return novo(f"{nome} {s}" if s else nome)
