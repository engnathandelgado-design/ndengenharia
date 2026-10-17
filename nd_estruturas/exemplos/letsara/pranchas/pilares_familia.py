"""Pranchas individuais das marcas da família 40×60 (PL-02 a PL-12, PF-01 a PF-06) — mesma armação do PL-01 (ND-LET-PIL-A01),
cabeça recuada, consolos e insertos da marca. Rodar: python pilares_familia.py [PL-02 ...]"""
import math, re, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
import pilar_generico as G
from familia_pl import MARCAS
from geometria import Y_LIN, X_EIXO, X_FACH

num = lambda t: round(float(t.replace(",", ".")) * 1000)
Z0 = G.LG["Z0_TS"]
rec_vb = lambda x: math.ceil((Z0 + 0.03 * x + 0.90) / 0.05) * 50
Z_PL = [1250 * (k - 1) + 922 + 1000 for k in range(1, 9)]                # rev06: CE-1 (centro) das fiadas 1 a 8, a partir da base do pilar
XB, YB = 152, 252
XY = [(x, -YB) for x in (-XB, -76, 0, 76, XB)] + [(x, YB) for x in (-XB, -76, 0, 76, XB)] + \
     [(-XB, y) for y in (-84, 84)] + [(XB, y) for y in (-84, 84)]                       # rev04: 14 Ø20
H_C = G.H_C
# rev03: VT do eixo A desce uma fiada (+6,25/+6,85; assento +6,54) para o consolo CP-VT ficar no corpo do pilar, abaixo do recuo (+7,19);
# no eixo E a VT continua em +7,50/+8,10 (assento +7,79), abaixo do recuo (+8,37)
Z_ASS_VT = {"P1": 6540, "P2": 7790}


def cons_marca(txt, lado="P1"):
    out = []
    for parte in [t.strip() for t in txt.split(";")]:
        m = re.match(r"(?:(\d+) )?(CP-[A-Z0-9]+)(?: \+(\d+,\d+))? \(([^)]*)\)", parte)
        if not m:
            continue
        tipo, z, faces = m.group(2), m.group(3), [x.strip() for x in m.group(4).split(",")]
        for fc in faces:
            if tipo == "CP-TS":
                c = G.consolo(fc, num(z), "CP-TS", 400, 300, H_C["CP-TS"], H_C["CP-TS"]); c["incl"] = 0.03; out.append(c)
            elif tipo == "CP-VT":
                c = G.consolo(fc, Z_ASS_VT[lado], "CP-VT", 250, 200, H_C["CP-VT"], H_C["CP-VT"], ("PN-1", 20, 700, 300, 100), (200, 150, 10), ("2 Ø12,5", 2, 12.5)); c["incl"] = 0; out.append(c)
            elif tipo == "CP-MEZ":
                for za in G.Z_MEZ_ASS:
                    c = G.MEZ(fc, za); c["incl"] = 0; out.append(c)
            elif tipo == "CP-VB":
                c = G.consolo(fc, num(z), "CP-VB", 150, 270, H_C["CP-VB"], H_C["CP-VB"], ("PN-6", 20, 700, 300, 135), (100, 100, 10), (G.CONS_J["CP-VB"]["tirante"].split(" (")[0], G.CONS_J["CP-VB"]["n_ramos"], G.CONS_J["CP-VB"]["d_tir"])); c["incl"] = 0; out.append(c)   # rev04: topo horizontal (NBR 9062 7.2.1.6)
            elif tipo == "CP-I130":
                c = G.I130(fc); c["incl"] = 0; out.append(c)
    return out


def ip_marca(txt):
    out = []
    for m in re.finditer(r"(\d+)(?: CE-1)? \(([A-D])(?:, ([^)]*))?\)", txt):
        n, fc, extra = int(m.group(1)), m.group(2), m.group(3) or ""
        zs = Z_PL if n == 8 else (Z_PL[-n:] if "fiadas" in extra else Z_PL[:n])
        out.append(dict(face=fc, z=zs, obs=extra))
    return out


def kp_familia():
    kp = []
    for i, y in enumerate(Y_LIN, 1):
        for lado, x in (("P1", 0.0), ("P2", X_EIXO["E"])):
            nome = f"{lado}-L{i}"
            from familia_pl import marca_de
            kp.append((nome, x, y, 600, 400, marca_de(nome)))
    for j, x in enumerate(X_FACH[1:-1]):
        for nome, y in ((["P3", "P4", "P5"][j] + "-L1", 0.0), (["P3", "P14", "P5"][j] + "-L9", Y_LIN[-1])):
            mk = {"P3-L1": "PF-01", "P4-L1": "PF-02", "P5-L1": "PF-03", "P3-L9": "PF-05", "P14-L9": "PF-04", "P5-L9": "PF-06"}[nome]
            kp.append((nome, x, y, 400, 600, mk))
    return kp


KP = kp_familia()


def NOTA_LAT(cons, ips):
    tem = lambda fc: sorted((c["tipo"], c["z"]) for c in cons if c["face"] == fc) + sorted((len(i["z"]),) for i in ips if i["face"] == fc)
    b, d = tem("B"), tem("D")
    if b == d:
        return "Faces B e D iguais (simétricas): desenhada a face B." if b else "Faces B e D lisas (só as chaves do cálice): desenhada a face B."
    lado = "D" if (d and not b) else "B"
    outra = "B" if lado == "D" else "D"
    return f"Face {outra}: " + ("lisa (só as chaves do cálice)." if not tem(outra) else "ver tabela de marcas e isométrico (consolos/insertos listados).")


def lateral(cons, ips):
    """face lateral mostrada: a que tem consolo/inserto; se B e D têm o mesmo conteúdo (simétricas), B."""
    tem = lambda fc: sorted((c["tipo"], c["z"]) for c in cons if c["face"] == fc) + sorted((len(i["z"]),) for i in ips if i["face"] == fc)
    if tem("D") and not tem("B"):
        return "D"
    return "B"


def dados(mk):
    _, pos, qt, cons_t, ins_t = next(m for m in MARCAS if m[0] == mk)
    canto = "canto" in pos
    lado_e = pos.startswith("P2")
    m = re.search(r"recuo \+(\d+,\d+)", cons_t)
    if m:
        zr = num(m.group(1))
    else:
        zr = rec_vb(39.50 if lado_e else 0.0) if canto else (G.LG and round(G.LG["REC"][1 if lado_e else 0] * 1000))
    d = {"A": 300}
    if canto:
        fc = re.search(r"recuo A e ([BD])", cons_t).group(1)
        d[fc] = 100
    cons = cons_marca(cons_t, "P2" if lado_e else "P1")
    ips = ip_marca(ins_t)
    n_pn1 = sum(1 for c in cons if c["pino_nome"] == "PN-1")
    n_pn2 = sum(1 for c in cons if c["pino_nome"] == "PN-2")
    ins = []
    if n_pn1:
        ins.append(["PN-1", "Pino Ø20 CA-50 L=700 (300 no consolo)", n_pn1, ", ".join(sorted(set(c["tipo"] for c in cons if c["pino_nome"] == "PN-1")))])
    n_pn6 = sum(1 for c in cons if c["pino_nome"] == "PN-6")
    if n_pn6:
        ins.append(["PN-6", "Barra roscada Ø20 A36 L=700 (300 no consolo)", n_pn6, "CP-VB"])
    if n_pn2:
        ins.append(["PN-2", "Pino Ø25 CA-50 L=900 (350 no consolo)", n_pn2, "CP-I130"])
    for tipo, nm, desc in (("CP-MEZ", "NEO-5", "Neoprene 300×150×10 c/ furo Ø30 (dente da VM)"), ("CP-VB", "NEO-6", "Neoprene 100×100×10 c/ furo Ø30 (dente da VB)"),
                           ("CP-I130", "NEO-2", "Neoprene 300×200×31 fretado (2 × 10 + 2 × 2,5, chapas inox 2 mm)")):
        n = sum(1 for c in cons if c["tipo"] == tipo)
        if n:
            ins.append([nm, desc, n, tipo])
    n_mez = sum(1 for c in cons if c["tipo"] == "CP-MEZ")
    if n_mez and len({c["face"] for c in cons if c["tipo"] == "CP-MEZ"}) == 2:      # apoio interno: continuidade da VM atravessa o pilar
        ins.append(["BA-1", "Bainha corrugada Ø50 horizontal (N11)", n_mez, "12 cm acima da VM"])
    if n_mez:
        ins.append(["IP-02", "Trilho TR-2 40/22 L=250 vertical (CT-1)", n_mez, "face do CP-MEZ"])
    for ip in ips:
        ins.append(["CE-1", "CE-1 380×330×16 + 4 pinos Ø16 + 2 grampos N18", len(ip["z"]), f"face {ip['face']}, centro 92 acima da fiada" + (f", {ip['obs']}" if ip["obs"] else "")])
        ins.append(["BR-2", "Bucha M16 hef 100 (trava PT-2)", "—", f"laterais junto à {ip['face']}, pacotes suspensos"])
    if not canto and mk.startswith("PL"):                                     # rev03: TS-01 apoiada no recuo (sem consolo CP-TS)
        ins.append(["PN-3", "Pino Ø25 CA-50 L=600 (300 no pilar), a 102,5 mm da face da cabeça", 2, "assento da TS-01 (y = ±100)"])
        ins.append(["NEO-4", "Neoprene 200×300×10 com 2 furos Ø35", 1, "assento horizontal da TS-01, de 50 a 250 mm da cabeça"])
    if mk in ("PL-07", "PL-08"):                                              # rev06: última terça do lado E apoia no recuo do canto
        ins.append(["ES-1F", "2 barras roscadas M20 A36 L=520 c/ gancho (ST-1F da última terça)", 2, "topo do recuo, x = −22,3 e −16,3 cm do eixo E, no eixo da linha"])
    ins.append(["AL-2", "Alça laço cordoalha Ø12,7 (2 pernas 700), 40 kN", 2, "face A: 320 cm do topo e 230 cm da base"])
    tipos = sorted(set(c["tipo"] for c in cons))
    lin = "fachada " + ("1" if "L1" in pos else "9") if mk.startswith("PF") else ("eixo E" if lado_e else "eixo A")
    cab = f"{(400 - d.get('B', 0) - d.get('D', 0))/10:g} × {(600 - 300)/10:g}"
    P = G.base(mk, qt, 400, 600, 10000, cons, XY, f"ND-LET-{mk.replace('-', '')}",
               f"PILAR PRÉ-MOLDADO {mk} (FAMÍLIA 40×60) — {pos} — FÔRMA, ARMAÇÃO, INSERTOS E LOCAÇÃO",
               f"POSIÇÃO: {pos} ({lin}); cabeça {cab} acima de +{zr/1000:.2f}".replace(".", ","), "FAMÍLIA DE PILARES 40×60",
               [[mk, pos, qt, cons_t, ins_t]], ins,
               ["Concreto C40; armação igual à do PL-01 (ND-LET-PIL-A01): 14 Ø20 retos (N1 sobem até o topo só na fileira da face C; N1A param no recuo com gancho 90°), N13 Ø16 na cabeça ancorados 60 cm no corpo, estribos N2 Ø8 c/15 (c/10 nos 150 cm do cálice e abaixo do recuo) + grampos N3, N14 Ø8 c/10 na cabeça.",
                G.NOTA_CONS.replace("CP-I130 49 cm", "CP-I130 49, CP-VB 29 cm (dente 30 da VB 15×60)") + " " + ", ".join(tipos) + " nesta marca.",
                f"CABEÇA RECUADA: acima de +{zr/1000:.2f}".replace(".", ",") + f" só a parte externa do pilar sobe até +10,00 ({cab} cm), para a cobertura ficar escondida na platibanda." +
                (" O degrau do recuo é o ASSENTO DA TS-01: topo HORIZONTAL (NBR 9062:2017 7.2.1.6; a cunha no fundo da ponta da TS-01 deixa a face de apoio horizontal), neoprene NEO-4 200×300×10 e 2 pinos PN-3 Ø25 a 10,25 cm da cabeça, grauteados nos tubos da viga; apoio útil de 27,5 cm." if (not canto and mk.startswith("PL")) else ""),
                "Faces: A = interna (consolo da viga principal), C = externa (placas); B e D no sentido anti-horário visto de cima (A → B → C → D). Pilar concretado deitado com a face A para cima.",
                "CE-1 (rev06, sistema Trejor, DEC-026): chapa de espera 380 × 330 × 16 com 4 pinos Ø16 × 150 c/ cabeça e 2 grampos U Ø10 (N18, C=96, sob o pino de baixo de cada coluna; ND-LET-PP01 det. 5), rente à face das placas, centrada no pilar, uma por fiada (centro 92 cm acima da base de cada fiada de 125 cm); os 2 consoles CS-1 das placas são soldados nela na obra (ND-LET-PP00 det. 2 e 4; fabricação no ND-LET-PP01). Nas fiadas de pacote suspenso (E, F e acima das esquadrias): buchas BR-2 M16 nas faces laterais para a trava PT-2. Chaves de cisalhamento nas 4 faces do trecho embutido (100 cm).",
                NOTA_LAT(cons, ips)],
               ip01=[dict(face=ip["face"], z=ip["z"]) for ip in ips], grampos=(-84, 84), vistas=("A", lateral(cons, ips), "C"), zoom=3.0)
    if not canto and mk.startswith("PL"):
        P["assento"] = dict(neo=(200, 300, 10), neo_nome="NEO-4 200×300", x_neo=(50, 250), x_pino=102.5, y_pinos=(-100, 100), d=25, L=600, emb=300, pino="PN-3 Ø25")
    P.update(rec=dict(z=zr + 1000, d=d), sobe_w=-240, n13_inner=4, kp=KP, al=[11000 - 3200, 1000 + 2300],
             secao_txt=f"60 × 40 cm (A–C × B–D), cabeça {cab}", faces_txt="FACES: A = interna, C = externa (placas), B e D anti-horário")
    return P


if __name__ == "__main__":
    alvo = sys.argv[1:] or [m[0] for m in MARCAS]
    for mk in alvo:
        G.prancha_pilar(dados(mk))
