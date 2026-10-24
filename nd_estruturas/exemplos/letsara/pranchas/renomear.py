"""Nomenclatura nova da Letsara (padrão do Nathan, 22/10/2026) aplicada no texto das folhas.

Regra: pilares P1…P36 e vigas V200…/V300…/V400… (um nome por peça, sentido de leitura — nomes.py/nomes.json).
Os geradores continuam usando as marcas internas (PL-01, TS-01B, VB-03…) e as referências do projeto do cliente (R01:
"P1 L5", "P8A", "P13"…) como chave; este módulo troca, no TEXTO desenhado, cada marca interna pela lista de nomes das
peças que ela representa e cada referência R01 pelo nome novo da posição. Um passe só (regex com todas as chaves), então
um nome novo nunca é trocado de novo. Texto que já vem com nome novo começa com MARCA_NOVO (é só tirado o marcador).
"""
import json, os, re
PR = "/home/claude/letsara/pranchas/"
MARCA_NOVO = "\x01"
_D = json.load(open(PR + "nomes.json", encoding="utf-8"))
M2N = {k: v for k, v in _D["marca_para_nomes"].items()}
# I130: no R01 / nas folhas antigas as vigas centrais eram V405/V406/V407
I130_ANT = {"V405", "V406", "V407"}


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
R01["P10a"], R01["P10b"] = [P10A], [P10B]          # portões: P10a = PG-02 (x 15,195), P10b = PG-04 (x 24,305)
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


def renomear(s):
    if not isinstance(s, str) or not s:
        return s
    if s.startswith(MARCA_NOVO):
        return s[1:]
    inteiro = s.strip() in CHAVES

    def rep(m):
        k = m.group(1)
        if k == "TS-01" and not inteiro:                   # na prosa "TS-01" é a família inteira das vigas de cobertura
            return "vigas de cobertura"
        if k in ("P1", "P2") and not inteiro:              # R01: P1/P2 sozinhos = pilares laterais dos eixos A/E
            return "pilares do eixo " + ("A" if k == "P1" else "E")
        return lista(CHAVES[k])
    # pré-passes: faixas do R01 ("P2 L5–L8") e "TS-01 … da linha N" — o resultado vai num marcador protegido do passe principal
    prot = []

    def guarda(txt):
        prot.append(txt)
        return f"\x02{len(prot) - 1}\x03"

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
    s2 = re.sub(r"assento (?:da |das )?TS-01(?![\w-])", lambda m: "assento da " + guarda("viga de cobertura"), s2)
    # "TS-01" na prosa = a família das vigas de cobertura (cada peça tem o seu nome na planta e na folha das vigas)
    s2 = re.sub(r"(?<![\w-])(d|n)?(as|os) TS-01(?![\w-])", lambda m: (m.group(1) or "") + m.group(2) + " " + guarda("vigas de cobertura"), s2)
    s2 = re.sub(r"(?<![\w-])(d|n)?(a|o) TS-01(?![\w-])", lambda m: (m.group(1) or "") + m.group(2) + " " + guarda("viga de cobertura"), s2)
    s2 = re.sub(r"(?<![\w-])(d|n|a)o (P[12])(?![\w\s]*L\d)(?![\w])", lambda m: f"{m.group(1)}os {guarda('pilares do eixo ' + ('A' if m.group(2) == 'P1' else 'E'))}", s2)
    t = _pat.sub(rep, s2)
    t = re.sub("\x02(\\d+)\x03", lambda m: prot[int(m.group(1))], t)
    t = re.sub(r"(?<![\w-])((?:[PV]\d+)(?:(?:, | a )[PV]\d+)*) \(\1\)", r"\1", t)     # "P10 (P10)" → "P10"
    t = re.sub(r"(?<![\w-])([PV]\d+) \(\1, ", r"\1 (", t)                                   # "P15 (P15, 40×60)" → "P15 (40×60)"
    if t != s:
        LOG.append((s, t))
        if os.environ.get("RENOMEAR_LOG"):
            with open(os.environ["RENOMEAR_LOG"], "a", encoding="utf-8") as fh:
                fh.write(json.dumps([s, t], ensure_ascii=False) + "\n")
    return t


def novo(s):
    """marca um texto que já está com o nome novo (não passa pela troca)."""
    return MARCA_NOVO + s


def pilar_em(x, y, tol=0.6):
    """nome do pilar na posição da obra (x = eixo A→E, y = linha 1→9, em m)."""
    ps = [p for p in _D["pecas"] if p["tipo"] == "pilar"]
    p = min(ps, key=lambda p: (p["x"] - x) ** 2 + (p["y"] - y) ** 2)
    return p["nome"] if ((p["x"] - x) ** 2 + (p["y"] - y) ** 2) ** 0.5 <= tol else None


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
