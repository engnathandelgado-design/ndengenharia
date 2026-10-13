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
Z_PL = [1250 * k - 100 + 1000 for k in range(1, 9)]                       # IP-01 das fiadas 1 a 8 (a partir da base)
XB, YB = 152, 252
XY = [(x, -YB) for x in (-XB, -76, 0, 76, XB)] + [(x, YB) for x in (-XB, -76, 0, 76, XB)] + \
     [(-XB, y) for y in (-168, -84, 0, 84, 168)] + [(XB, y) for y in (-168, -84, 0, 84, 168)]
H_C = G.H_C


def cons_marca(txt):
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
                c = G.consolo(fc, 7790, "CP-VT", 250, 200, H_C["CP-VT"], H_C["CP-VT"], ("PN-1", 20, 700, 300, 100), (200, 150, 10), ("2 Ø12,5", 2, 12.5)); c["incl"] = 0; out.append(c)
            elif tipo == "CP-MEZ":
                for za in G.Z_MEZ_ASS:
                    c = G.MEZ(fc, za); c["incl"] = 0; out.append(c)
            elif tipo == "CP-VB":
                c = G.consolo(fc, num(z), "CP-VB", 300, 300, H_C["CP-VB"], H_C["CP-VB"], ("PN-1", 20, 700, 300, 150), (300, 150, 10), ("2 Ø12,5", 2, 12.5)); c["incl"] = 0.03; out.append(c)
            elif tipo == "CP-I110":
                c = G.I110(fc); c["incl"] = 0; out.append(c)
    return out


def ip_marca(txt):
    out = []
    for m in re.finditer(r"(\d+)(?: IP-01)? \(([A-D])(?:, ([^)]*))?\)", txt):
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
        zr = rec_vb(39.50 if lado_e else 0.0) if canto else (9550 if lado_e else 8400)
    d = {"A": 300}
    if canto:
        fc = re.search(r"recuo A e ([BD])", cons_t).group(1)
        d[fc] = 100
    cons = cons_marca(cons_t)
    ips = ip_marca(ins_t)
    n_pn1 = sum(1 for c in cons if c["pino_nome"] == "PN-1")
    n_pn2 = sum(1 for c in cons if c["pino_nome"] == "PN-2")
    ins = []
    if n_pn1:
        ins.append(["PN-1", "Pino Ø20 CA-50 L=700 (300 no consolo)", n_pn1, ", ".join(sorted(set(c["tipo"] for c in cons if c["pino_nome"] == "PN-1")))])
    if n_pn2:
        ins.append(["PN-2", "Pino Ø25 CA-50 L=900 (350 no consolo)", n_pn2, "CP-I110"])
    for tipo, desc in (("CP-TS", "Neoprene 300×150×10 c/ furo Ø30"), ("CP-MEZ", "Neoprene 300×150×10 c/ furo Ø30"), ("CP-VB", "Neoprene 300×150×10 c/ furo Ø30"),
                       ("CP-VT", "Neoprene 200×150×10 c/ furo Ø30"), ("CP-I110", "Neoprene 300×250×30 fretado")):
        n = sum(1 for c in cons if c["tipo"] == tipo)
        if n:
            ins.append(["NEO-2" if tipo == "CP-I110" else "NEO-1", desc, n, tipo])
    for ip in ips:
        ins.append(["IP-01", "Chapa A36 150×150×9,5 + 2 pinos Ø12,5 c/ cabeça", len(ip["z"]), f"face {ip['face']}" + (f", {ip['obs']}" if ip["obs"] else "")])
    ins.append(["AL-2", "Alça laço cordoalha Ø12,7 (2 pernas 700), 40 kN", 2, "face A: 320 cm do topo e 230 cm da base"])
    tipos = sorted(set(c["tipo"] for c in cons))
    lin = "fachada " + ("1" if "L1" in pos else "9") if mk.startswith("PF") else ("eixo E" if lado_e else "eixo A")
    cab = f"{(400 - d.get('B', 0) - d.get('D', 0))/10:g} × {(600 - 300)/10:g}"
    P = G.base(mk, qt, 400, 600, 10000, cons, XY, f"ND-LET-{mk.replace('-', '')}",
               f"PILAR PRÉ-MOLDADO {mk} (FAMÍLIA 40×60) — {pos} — FÔRMA, ARMAÇÃO, INSERTOS E LOCAÇÃO",
               f"POSIÇÃO: {pos} ({lin}); cabeça {cab} acima de +{zr/1000:.2f}".replace(".", ","), "FAMÍLIA DE PILARES 40×60",
               [[mk, pos, qt, cons_t, ins_t]], ins,
               ["Concreto C40; armação igual à do PL-01 (ND-LET-PIL-A01): 20 Ø20 retos (N1 sobem até o topo só na fileira da face C; N1A param no recuo com gancho 90°), N13 Ø16 na cabeça ancorados 60 cm no corpo, estribos N2 Ø8 c/15 (c/10 nos 150 cm do cálice e abaixo do recuo) + grampos N3, N14 Ø8 c/10 na cabeça.",
                G.NOTA_CONS.replace("CP-I110 41 cm", "CP-I110 41, CP-VB 35, CP-VT 29 cm") + " " + ", ".join(tipos) + " nesta marca.",
                f"CABEÇA RECUADA: acima de +{zr/1000:.2f}".replace(".", ",") + f" só a parte externa do pilar sobe até +10,00 ({cab} cm), para a cobertura ficar escondida na platibanda sem rufos contornando o pilar.",
                "Faces: A = interna (consolo da viga principal), C = externa (placas); B e D no sentido anti-horário visto de cima (A → B → C → D). Pilar concretado deitado com a face A para cima.",
                "Insertos IP-01 na face das placas a cada fiada (125 cm a partir do piso); chaves de cisalhamento nas 4 faces do trecho embutido (100 cm).",
                NOTA_LAT(cons, ips)],
               ip01=[dict(face=ip["face"], z=ip["z"]) for ip in ips], grampos=(-84, 84), vistas=("A", lateral(cons, ips), "C"), zoom=3.0)
    P.update(rec=dict(z=zr + 1000, d=d), sobe_w=-240, n13_inner=4, kp=KP, al=[11000 - 3200, 1000 + 2300],
             secao_txt=f"60 × 40 cm (A–C × B–D), cabeça {cab}", faces_txt="FACES: A = interna, C = externa (placas), B e D anti-horário")
    return P


if __name__ == "__main__":
    alvo = sys.argv[1:] or [m[0] for m in MARCAS]
    for mk in alvo:
        G.prancha_pilar(dados(mk))
