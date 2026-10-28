"""ND-LET-PR01 — QUADRO DE PRODUÇÃO E CONCRETAGEM DAS PEÇAS, POR MARCA (rev07, emissão executiva 21/10/2026).

Uma linha por marca: quantidade, seção e comprimento, volume e peso (unitário e total), concreto, fcj de liberação e de desforma,
fôrma/pista, protensão (nº × Ø e força no macaco), aço passivo por peça e total, pontos de içamento (das tabelas de insertos de
cada folha), estocagem/transporte e folha de referência. Totais por família e gerais (concreto por fck, aço por bitola,
cordoalhas e fios). Fonte: quantitativos.py (que lê as tabelas das próprias folhas) e os JSON de cálculo — mesma origem das listas.
Uso: python pr01.py"""
import json, re, sys, math
sys.path.insert(0, "/home/claude/letsara/pranchas")
import quantitativos as Q
from prancha_nd import Prancha, ALTURAS, _wtext

PR = "/home/claude/letsara/pranchas/"
AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
J = lambda n: json.load(open(AQ + n + ".json", encoding="utf-8"))
f = lambda v, d=1: f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
LAJ, PLJ, VMJ, IJ, NBR, OMJ = J("laje_alveolar"), J("placas"), J("vm_retangular"), J("i110_r01"), J("nbr9062"), J("ombreira")
PISTA = 60.0           # pista de protensão (tabelas "PISTA 60 m" das folhas)
VAO_PISTA = 0.50       # espaço entre peças na pista para corte das cordoalhas (a confirmar com a fábrica)


def tab(folha, inicio, folhas_alt=()):
    for fl in (folha, *folhas_alt):
        try:
            d = json.load(open(PR + fl + ".tabelas.json", encoding="utf-8"))
        except FileNotFoundError:
            continue
        for t in d["tabelas"]:
            if t["titulo"].upper().startswith(inicio.upper()):
                return t
    return None


def icamento(folha):
    """alças, furos e insertos de içamento da tabela de insertos da folha."""
    t = tab(folha, "INSERTOS")
    out = []
    for l in (t["linhas"] if t else []):
        if re.match(r"(AL-|FI-|IZ-)", l[0]):
            out.append(re.sub(r"(\d)\.(\d)", r"\1,\2", f"{l[0]} ×{l[2]} ({l[3]})"))
    return "; ".join(out)


# ------------------------------------------------------------------ dados por família
TSQ = tab("ND-LET-TS01-1", "MANUSEIO") or {"linhas": []}
TS_EST = next((l for l in TSQ["linhas"] if l[0].startswith("Estoque")), ["", "2 calços a 210 cm das pontas", ""])
TS_DESF = next((l for l in TSQ["linhas"] if l[0].startswith("Desforma")), ["", "4 alças AL-1 + 2 balancins", ""])
TS_CORD = (tab("ND-LET-TS01-1", "CORDOALHAS", ("ND-LET-TS01-2",)) or {"linhas": []})["linhas"]
LA_MARCAS = {l[0]: l for l in tab("ND-LET-LA01", "MARCAS")["linhas"]}
LA_F = tab("ND-LET-LA01", "PROTENSÃO")["linhas"][0][5]
PP_ACO = {l[0]: l for l in tab("ND-LET-PP00", "AÇO PASSIVO")["linhas"]}
P_ = PLJ["protensao"]
KGM = Q.KGM


def kg_aco(nome):
    for a in Q.aco:
        if a[0] == nome:
            return sum(a[3].values())
    return None


def aco_viga(fam, marca):
    """kg/peça da relação da marca (armaduras_vigas): nomes 'I120 V407', 'VM VM-01', 'VB VB-01/05' (a marca e a sua espelhada)."""
    import re as _re
    NMj = json.load(open("/home/claude/letsara/pranchas/nomes.json", encoding="utf-8"))["pecas"]
    for nome, _, _, kd, _ in Q.aco:
        if not nome.startswith(fam + " "):
            continue
        tag = _re.sub(r"[\x00-\x1f]", "", nome[len(fam) + 1:]).strip()
        cands = {tag.split("/")[0], tag.split("/")[0][:-2] + tag.split("/")[1]} if "/" in tag else {tag}
        # rev12b (revisão rev12b, item 5): depois da renomeação a relação traz os NOMES das peças (V407, V423); a marca sai do registro de nomes
        cands |= {q["marca"] for n_ in tag.split(",") for q in NMj if q["nome"] == n_.strip() and q["marca"].startswith(fam)}
        if marca in cands:
            return sum(kd.values())
    return None


def por_pista(L):
    return int((PISTA + VAO_PISTA) // (L + VAO_PISTA))


def linha(p):
    grupo, mk, desc, sec, L, qt, v, peso, conc, folha = p
    fl = folha.replace("ND-LET-", "")
    if grupo == "Pilares":
        fam = "Pilares"
        lib, desf = "—", "25"
        forma = "fôrma de pilar, peça deitada"
        prot = "—"
        kg = kg_aco(f"Pilar {mk}")
        ic = icamento(folha) or "AL-2 ×2; FI-1"
        ic = "desforma e transporte pelas 2 AL-2; verticalizar e montar pelo FI-1 — " + ic
        est = "deitado em 2 calços a 0,21 L das pontas; não apoiar em consolos ou chapas"
    elif mk == "TS-01":
        fam = "Vigas de cobertura"
        lib = desf = "35"
        n = sum(int(l[2]) for l in TS_CORD)
        forma = f"pista {PISTA:g} m (≤ {por_pista(L)} por pista)"
        prot = f"{n} Ø12,7 CP-190 RB, {TS_CORD[0][4]} kN" + (f" ({TS_CORD[-1][2]} isoladas {TS_CORD[-1][6].lower()})" if len(TS_CORD) > 1 else "")
        kg = kg_aco("TS-01")
        ic = f"desforma: {TS_DESF[1]} ({TS_DESF[2]}) — {icamento('ND-LET-TS01-1')}"
        est = f"{TS_EST[1]} ({TS_EST[2]}); transportar nos mesmos pontos"
    elif fl == "I120":
        fam = "Vigas de cobertura"
        a = IJ[mk]["arranjo"]
        lib = desf = f"{a['fckj']:.0f}"
        forma = f"pista {PISTA:g} m (≤ {por_pista(L)} por pista)"
        prot = f"{a['n_cord']} Ø12,7 CP-190 RB, {f(a['F_macaco_kN'])} kN"
        kg = aco_viga("I120", mk)
        _ic = IJ[mk]["icamento"]                                        # rev12b (item 13): laços e posição da alça do cálculo da marca
        ic = f"2 alças AL-3 ({_ic['n_lacos']} laços cada) a {f(_ic['a_alca_m'], 2)} m das pontas — " + icamento(folha)
        est = "2 calços sob as alças; não virar a peça; travar contra tombamento no transporte"
    elif fl == "VM01":
        fam = "Mezanino"
        lib, desf = f"{VMJ['premissas']['fckj']:.0f}", f"{VMJ['premissas']['fcj_icamento']:.0f}"
        forma = f"pista {PISTA:g} m (≤ {por_pista(L)} por pista)"
        prot = f"{VMJ[mk]['n_cord']} Ø12,7 CP-190 RB, {f(VMJ[mk]['protensao']['F_macaco_kN'])} kN ({VMJ[mk]['isoladas_pontas']} isoladas nas pontas)"
        kg = aco_viga("VM", mk)
        ic = icamento(folha) + " (cabos ≥ 45°)"
        est = "2 calços sob as alças (≤ 0,3 fcj); transportar nos mesmos pontos, travada contra tombamento"
    elif fl == "VB01":
        fam = "Vigas de borda"
        lib, desf = "—", "25"
        forma = "fôrma de viga com dente"
        prot = "—"
        kg = aco_viga("VB", mk)
        ic = icamento(folha)
        est = "2 calços sob as alças"
    elif fl == "LA01":
        fam = "Mezanino"
        lib = f"{LAJ['fckj']:.0f}"; desf = f"{LAJ['icamento']['fcj_icamento']:.0f}"
        cds = " + ".join(f"{n_} Ø{d_}" for n_, d_ in re.findall(r"(\d+) Ø(\d+,\d)", LA_MARCAS[mk][1]))   # rev09: Ø15,2 / Ø12,7 / Ø9,5
        forma = "pista de lajes alveolares (seção LP20 desenhada)"
        prot = f"{cds} CP-190 RB (σpi {LAJ['sig_pi']:.0f} MPa)" + (f"; {LA_MARCAS[mk][4]}" if LA_MARCAS[mk][4] not in ("-", "") else "")
        kg = None
        ic = f"garra mecânica nas 2 pontas a {f(LAJ['icamento']['ponto_m'] * 100, 0)} cm ({f(LAJ['icamento']['F_por_garra_d_kN'])} kN de cálculo por garra); sem alça"
        est = f"2 calços alinhados a {f(LAJ['icamento']['ponto_m'] * 100, 0)} cm das pontas, até 8 por pilha"
    else:                                                              # placas
        fam = "Placas de fechamento"
        lib = desf = f"{PLJ['secao']['fckj']:.0f}"
        n = OMJ["placa_I15"]["n_total"] if mk == "PP-05P" else P_["n"]
        forma = f"pista {PISTA:g} m, deitada face interna p/ cima (≤ {por_pista(L)} por pista)"
        prot = f"{n} fios Ø{P_['diam_mm']:g} CP-175 RB ({n // 2} por face), {f(P_['F_macaco_kN'])} kN"
        kg = (Q.num(PP_ACO[mk][4]) - Q.num(PP_ACO[mk][3]) * 1.48 * 1.10) if mk in PP_ACO else None    # sem a tela Q92 (como nas listas)
        ic = f"desforma: 4 IZ-1 numa face a 0,104 L e 0,396 L, com balancim; giro e montagem de pé pelos mesmos 4 IZ-1 (balancim duplo)"
        est = "EM PÉ em cavalete, 2 calços a 0,21 L da base (deitada empena)"
    return dict(fam=fam, marca=mk, qt=qt, sec=sec, L=L, v=v, peso=peso, conc=conc, lib=lib, desf=desf, forma=forma, prot=prot,
                kg=kg, ic=ic, est=est, folha=fl)


LINHAS = [linha(p) for p in Q.pecas]
FAMS = ["Pilares", "Vigas de cobertura", "Vigas de borda", "Mezanino", "Placas de fechamento"]


def totais():
    conc, fam = {}, {}
    for r in LINHAS:
        c = r["conc"]; conc[c] = conc.get(c, 0) + r["v"] * r["qt"]
        t = fam.setdefault(r["fam"], dict(qt=0, v=0.0, p=0.0, kg=0.0))
        t["qt"] += r["qt"]; t["v"] += r["v"] * r["qt"]; t["p"] += r["peso"] * r["qt"]; t["kg"] += (r["kg"] or 0) * r["qt"]
    bit = {d: 0.0 for d in Q.DIAMS}
    for _, _, qt, kd, _ in Q.aco:
        for d, v in kd.items():
            bit[d] += v * qt
    prot = {}
    for nome, d, n, L, qt, _ in Q.cord:
        k = ("fio CP-175 RB Ø" if d < 9 else "cordoalha CP-190 RB Ø") + f"{d:g}".replace(".", ",")
        a = prot.setdefault(k, [0.0, 0.0]); a[0] += n * L * qt; a[1] += n * L * qt * Q.KGC[float(d)]
    return conc, fam, bit, prot


def gerar():
    import prancha_nd as _PN
    _PN.ALTURAS["nota"] = 2.8                     # quadro de produção: texto maior (só nesta folha)
    pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                            conteudo="QUADRO DE PRODUÇÃO E CONCRETAGEM DAS PEÇAS — POR MARCA", desenho="ND-LET-PR01", folha="01/01", rev="06"))
    pr.revisao("06", "21/10/2026", "QUADRO DE PRODUÇÃO E CONCRETAGEM")
    pr.revisao("R12", "27/10/2026", "VM DA LINHA 1 ALINHADA À FACE EXTERNA; LAJES DO VÃO 1–2 COM 9,70 m; CONSOLOS COM A LARGURA DA VIGA; BAINHAS BA-1, AÇO DAS VB E NOMES DAS PEÇAS DO REGISTRO")
    x0, y0, x1, y1 = pr.quadro
    cab = ["MARCA", "QT", "SEÇÃO", "L (m)", "VOL. un (m³)", "VOL. tot (m³)", "PESO un (t)", "PESO tot (t)", "CONCR.", "fcj LIB.", "fcj DESF.",
           "FÔRMA / PISTA", "PROTENSÃO (força no macaco por cabo)", "AÇO kg/pç", "AÇO kg tot", "IÇAMENTO (desforma, verticalização, montagem)", "ESTOCAGEM E TRANSPORTE", "FOLHA"]
    larg = [15, 7, 30, 11, 15, 15, 13, 14, 12, 11, 11, 62, 98, 13, 15, 252, 112, 18]
    lin = []
    conc, fam, bit, prot = totais()
    for F in FAMS:
        rs = [r for r in LINHAS if r["fam"] == F]
        for r in rs:
            lin.append([Q.marca_txt(r["marca"], r["qt"]), r["qt"], r["sec"], f(r["L"], 2), f(r["v"], 3), f(r["v"] * r["qt"], 2), f(r["peso"], 2), f(r["peso"] * r["qt"], 1),
                        r["conc"], r["lib"], r["desf"], r["forma"], r["prot"], f(r["kg"], 0) if r["kg"] else "—", f(r["kg"] * r["qt"], 0) if r["kg"] else "—",
                        r["ic"], r["est"], r["folha"]])
        t = fam[F]
        lin.append(["SUBTOTAL", t["qt"], F.upper(), "", "", f(t["v"], 1), "", f(t["p"], 1), "", "", "", "", "", "", f(t["kg"], 0), "", "", ""])
    T = dict(qt=sum(t["qt"] for t in fam.values()), v=sum(t["v"] for t in fam.values()), p=sum(t["p"] for t in fam.values()), kg=sum(t["kg"] for t in fam.values()))
    lin.append(["TOTAL", T["qt"], "", "", "", f(T["v"], 1), "", f(T["p"], 1), "", "", "", "", "", "", f(T["kg"], 0), "", "", ""])
    # texto da célula alinhado à esquerda nas colunas longas: a tabela do motor centraliza — as colunas são largas o bastante
    hn = ALTURAS["nota"]
    larg = [max(_wtext(str(c), hn) for c in col) + 3.5 for col in zip(cab, *lin)]
    k_ = min(1.0, (x1 - x0 - 12) / sum(larg))
    larg = [w * k_ for w in larg]
    k2 = (x1 - x0 - 12) / sum(larg)
    larg = [w * k2 for w in larg]                 # sobra distribuída por todas as colunas
    y = pr.tabela(x0 + 6, y1 - 6, f"QUADRO DE PRODUÇÃO E CONCRETAGEM — {T['qt']} PEÇAS, {f(T['v'], 1)} m³, {f(T['p'], 0)} t", cab, lin, larg, h_lin=7.2)
    # ---------- totais
    yt = y - 12
    hn = ALTURAS["nota"]
    W = lambda cab_, lin_, mn=0: [max(mn, max(_wtext(str(c), hn) for c in col) + 6) for col in zip(cab_, *lin_)]
    lc = [[c, f(v, 1)] for c, v in sorted(conc.items())] + [["TOTAL", f(sum(conc.values()), 1)]]
    xx = x0 + 6
    c_ = ["CONCRETO", "VOLUME (m³)"]; w_ = W(c_, lc, 30)
    pr.tabela(xx, yt, "CONCRETO POR CLASSE (m³)", c_, lc, w_, h_lin=6.5, destaque_ultima=True); xx += sum(w_) + 10
    lb = [[f"Ø{d:g}".replace(".", ","), f(v, 0)] for d, v in bit.items() if v > 0] + [["TOTAL CA-50", f(sum(bit.values()), 0)]]
    c_ = ["BITOLA", "MASSA (kg)"]; w_ = W(c_, lb, 34)
    pr.tabela(xx, yt, "AÇO CA-50 POR BITOLA (kg, +10 %)", c_, lb, w_, h_lin=6.5, destaque_ultima=True); xx += sum(w_) + 10
    lp = [[k, f(m, 0), f(kg, 0)] for k, (m, kg) in prot.items()] + [["TOTAL", "", f(sum(a[1] for a in prot.values()), 0)]]
    c_ = ["AÇO", "COMPR. (m)", "MASSA (kg)"]; w_ = W(c_, lp)
    pr.tabela(xx, yt, "PROTENSÃO (comprimento na peça)", c_, lp, w_, h_lin=6.5, destaque_ultima=True); xx += sum(w_) + 10
    lf = [[F, fam[F]["qt"], f(fam[F]["v"], 1), f(fam[F]["p"], 1), f(fam[F]["kg"], 0), f(fam[F]["kg"] / fam[F]["v"], 0) if fam[F]["kg"] else "—"] for F in FAMS]
    c_ = ["FAMÍLIA", "PEÇAS", "m³", "t", "AÇO kg", "kg/m³"]; w_ = W(c_, lf, 18)
    pr.tabela(xx, yt, "RESUMO POR FAMÍLIA", c_, lf, w_, h_lin=6.5); xx += sum(w_) + 12
    pr.notas(xx, yt + 2, [
        "Valores das tabelas das próprias folhas de cada marca (quadro da peça, marcas, cordoalhas, insertos e relação do aço); o mesmo dado das listas de materiais e dos quantitativos da mesma revisão (rev12). Pendências que impedem produzir: ND-LET-NG01 (A CONFIRMAR ANTES DA PRODUÇÃO) — LA-01/LA-01R: CONFIRMAR COM A FÁBRICA a extrusora (2 cordoalhas na nervura de borda).",
        "fcj em MPa, de corpos de prova curados junto com a peça: LIB. = liberação da protensão (sempre gradual e simétrica); DESF. = desforma, içamento e transporte. Peças armadas: só desforma.",
        "Aço CA-50 com +10 % de perdas, sem as telas (Q92 das pontas das placas e Q138 da capa) e sem as alças. Protensão: comprimento dentro da peça, sem as sobras de pista e de ancoragem.",
        f"Peças por pista: pista de {PISTA:g} m com {VAO_PISTA * 100:g} cm entre peças para o corte — confirmar o arranjo, as cabeceiras e o número de pistas com a fábrica.",
        "Içamento (NBR 9062:2017 5.3): alças em laço de cordoalha Ø12,7 não engraxada, βa 3; peça içada com βa 1,3. Ângulo dos cabos ≥ 45° com a peça ou balancim conforme a folha.",
        "Estocagem: calços de madeira alinhados nos pontos indicados, pressão ≤ 0,3 fcj (NBR 9062:2017 10.2); pilhas só onde a folha permite.",
        "Lajes alveolares: protensão válida para a seção desenhada (ND-LET-LA01); se o fabricante extrudar outra seção, refazer a verificação.",
    ], x1 - 6 - xx, "NOTAS")
    return pr


if __name__ == "__main__":
    pr = gerar()
    av = pr.salvar(PR + "ND-LET-PR01")
    for a in av:
        print(a)
    print(len([a for a in av if a[0] == "ERRO"]), "erros,", len(av), "avisos")
