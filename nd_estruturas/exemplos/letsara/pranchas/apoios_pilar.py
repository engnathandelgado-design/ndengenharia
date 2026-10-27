"""rev11 (26/10/2026, pedido do Nathan — item 13): esperas e chumbadores dos apoios de viga nos pilares.

Para CADA ponto de apoio (consolo, assento no recuo, topo do pilar, esperas de face) monta uma linha com:
nível (a partir da base e do piso ±0,00), face, elemento e dimensões, barra (tipo, Ø, aço), comprimento embutido, livre
(para fora), total, trecho roscado, ancoragem e posição em planta (mm, até as faces). Confere a pilha do que a barra atravessa
(graute, chapa, mesa, arruela, porcas, 2 fios) contra o comprimento livre. Devolve erros para o verificar() da folha.

Desenha o DETALHE 3 (1:10): cabeça/recuo do pilar em corte com as barras, a chapa/neoprene e a viga apoiada, cotado.
"""
import json, os

_REG = "/home/claude/letsara/pranchas/consolos_marcas.json"


def f2(v):
    return f"{v:.2f}".replace(".", ",")


def g(v):
    return f"{v:g}".replace(".", ",")


def marca_consolo(c):
    """C1, C2… pelo registro global (consolos_marcas.py); chave = geometria + pino + neoprene + tirante."""
    if not os.path.exists(_REG):
        return c["tipo"]
    R = json.load(open(_REG, encoding="utf-8"))
    return R["por_chave"].get(chave(c), c["tipo"])


def chave(c):
    return "|".join(str(x) for x in (c["tipo"], c["larg"], c["proj"], c["h"], c["hp"], c.get("incl", 0.03), c["pino_nome"], c["pino_d"], c["pino_L"],
                                       c["pino_emb"], c["pino_x"], tuple(c["neo"]), c["n_tir"], c["d_tir"], c.get("exc", 0)))


def aco_pino(nome):
    return "aço ASTM A36 roscado, zincado a fogo" if nome == "PN-6" else "CA-50 (NBR 7480)"


def linhas(P, cons, L_CAL, L_TOT, z_rec, REC, rd, B, H):
    """Linhas do QUADRO DE APOIOS E ESPERAS e lista de erros (ERRO se faltar cota ou comprimento)."""
    rows, err = [], []
    niv = lambda z: ("+" if z >= L_CAL else "−") + f2(abs(z - L_CAL) / 1000)

    def chk(nome, emb, livre, tot, pilha=None):
        if not (emb and emb > 0 and livre and livre > 0 and tot and abs(tot - emb - livre) < 1):
            err.append(("ERRO", f"apoio {nome}: espera sem os três comprimentos (embutido {emb}, livre {livre}, total {tot})"))
        if pilha:
            s = sum(t for _, t in pilha)
            if s > livre + 0.1:
                err.append(("ERRO", f"apoio {nome}: comprimento livre {g(livre)} mm < pilha {g(round(s, 1))} mm ({' + '.join(n for n, _ in pilha)})"))
    for c in sorted(cons, key=lambda c: (c["z"], c["face"])):
        mk = marca_consolo(c)
        emb, tot = c["pino_emb"], c["pino_L"]
        livre = tot - emb
        if c.get("z") is None:
            err.append(("ERRO", f"consolo {c['tipo']} sem nível"))
        dim = f"{g(c['larg'] / 10)}×{g(c['proj'] / 10)}×{g(round(c['h'] / 10, 1))}" + (f"/{g(round(c['hp'] / 10, 1))}" if c["hp"] != c["h"] else "")
        rows.append([f"{mk} ({c['tipo']})", f"{c['face']}", f"{niv(c['z'])} ({g(c['z'] / 10)})", dim,
                     f"1 {c['pino_nome']} Ø{g(c['pino_d'])}", g(emb / 10), g(livre / 10), g(tot / 10),
                     f"{aco_pino(c['pino_nome'])}; reta; a {g(c['pino_x'] / 10)} cm da face, no eixo do consolo; " + (f"consolo RENTE À FACE {c['exc_face']} (eixo do consolo a {g(c['exc'] / 10)} cm do eixo da face {c['face']}); " if c.get("exc") else "") + f"neoprene {c['neo'][0]}×{c['neo'][1]}×{c['neo'][2]}"])
        chk(f"{mk} face {c['face']} {niv(c['z'])}", emb, livre, tot)
    AS = P.get("assento")
    if AS and REC:
        f_rec = [k for k, v in REC["d"].items() if v > 0]
        nb = len(AS.get("x_pinos", (AS["x_pino"],))) * len(AS["y_pinos"])
        livre = AS["L"] - AS["emb"]
        xs = ", ".join(g(x / 10) for x in AS.get("x_pinos", (AS["x_pino"],)))
        ys = " e ".join(g(abs(y) / 10) for y in AS["y_pinos"][:1]) if len(set(abs(y) for y in AS["y_pinos"])) == 1 else ", ".join(g(y / 10) for y in AS["y_pinos"])
        rows.append([f"ESP-1 ({AS.get('marca_b', AS['pino'])})", "recuo " + "/".join(f_rec), f"{niv(z_rec)} ({g(z_rec / 10)})", f"{AS['neo_nome']}",
                     f"{nb} {AS.get('marca_b', AS['pino'])} Ø{g(AS['d'])}", g(AS["emb"] / 10), g(livre / 10), g(AS["L"] / 10),
                     f"{AS.get('aco', '')}; {AS.get('anc', '')}; " + (f"rosca {g(AS['rosca'] / 10)} cm na ponta livre; " if AS.get("rosca") else "") +
                     f"a {xs} cm da face da cabeça e ±{ys} do eixo da face; {AS.get('destino', '')}" +
                     (f"; pilha sobre o concreto: " + " + ".join(f"{n} ({g(t)} mm)" for n, t in AS["pilha"]) + f" = {g(round(sum(t for _, t in AS['pilha']), 1))} mm, menor que os {g(livre)} mm livres" if AS.get("pilha") else "")])
        chk("ESP-1 (recuo)", AS["emb"], livre, AS["L"], AS.get("pilha"))
    PT = P.get("pinos_topo")
    if PT:
        livre = PT["L"] - PT["emb"]
        xs = sorted({abs(q[0]) for q in PT["xy"]}); ys = sorted({abs(q[1]) for q in PT["xy"]})
        rows.append([f"ESP-2 ({PT['nome']})", "topo", f"+{f2((L_TOT - L_CAL) / 1000)} ({g(L_TOT / 10)})", "topo do pilar",
                     f"{len(PT['xy'])} {PT['nome']} Ø{g(PT['d'])}", g(PT["emb"] / 10), g(livre / 10), g(PT["L"] / 10),
                     f"{PT.get('aco', '')}; {PT.get('anc', '')}; " + (f"rosca {g(PT['rosca'] / 10)} na ponta livre; " if PT.get("rosca") else "") +
                     f"x ±{'/'.join(g(x / 10) for x in xs)} (A–C) e y ±{'/'.join(g(y / 10) for y in ys)} (B–D) do centro; {PT.get('destino', '')}"])
        chk("ESP-2 (topo)", PT["emb"], livre, PT["L"], PT.get("pilha"))
    for k, es in enumerate(P.get("esperas_face", []), 3):
        rows.append([f"ESP-{k} ({es['rot'].split()[0]})", f"face {es['face']}", f"{niv(es['z'])} ({g(es['z'] / 10)})", "face lateral",
                     f"{len(es['da'])} M{g(es['d'])} A36 roscada", g(es["emb"] / 10), g(es["sai"] / 10), g((es["emb"] + es["sai"]) / 10),
                     f"gancho + grampo U Ø10; a {', '.join(g(a / 10) for a in es['da'])} da aresta da face A"])
        chk(f"ESP-{k}", es["emb"], es["sai"], es["emb"] + es["sai"])
    return rows, err


def detalhe3(pr, P, REC, rd, B, H, L_TOT, z_rec, org):
    """DETALHE 3 (1:10) — apoio no recuo: corte pela cabeça na direção do recuo. x = 0 na face da cabeça; recuo em x > 0."""
    AS = P.get("assento")
    if not (AS and REC):
        return None
    f_rec = max(REC["d"], key=lambda k: REC["d"][k])
    R = REC["d"][f_rec]                                        # profundidade do recuo (mm)
    HW = (H if f_rec in "AC" else B) - R                       # profundidade da cabeça na mesma direção
    hc = min(L_TOT - z_rec, 450)                               # trecho de cabeça desenhado
    emb, livre = AS["emb"], AS["L"] - AS["emb"]
    zb = -emb - 150
    v = pr.vista("DETALHE 3", org, 10, titulo=f"DETALHE 3 — APOIO NO RECUO ({AS.get('marca_b', AS['pino'])})",
                 subtitulo=f"corte pela cabeça (face {f_rec}); concreto e barras em cm, chapas em mm nos textos", unidade="cm")
    pts = [(-HW, zb), (R, zb), (R, 0), (0, 0), (0, hc), (-HW, hc)]
    v.poli(pts, "CORTADO", True); v.hachura(pts, "AR-CONC", 0.03)
    v.interrupcao((-HW, zb), (R, zb)); v.interrupcao((-HW, hc), (0, hc))
    xs = AS.get("x_pinos", (AS["x_pino"],))
    pilha = AS.get("pilha", [])
    zt = 0
    BR = AS.get("rosca")
    if BR:                                                     # graute + CA-L2 + mesa da W
        g0 = 20; v.ret(AS["x_neo"][0], 0, AS["x_neo"][1] - AS["x_neo"][0], g0, "OCULTA")
        v.chapa(AS["x_neo"][0], g0, AS["x_neo"][1] - AS["x_neo"][0], 19)
        zm = g0 + 19
        v.chapa(20, zm, R + 130, 5.2)                          # mesa inferior da W (termina a 20 mm da face da cabeça)
        v.linha((20, zm + 200), (R + 150, zm + 200), "VISTA"); v.linha((20, zm + 194.8), (R + 150, zm + 194.8), "VISTA"); v.linha((20, zm), (20, zm + 200), "VISTA")
        v.interrupcao((R + 150, zm), (R + 150, zm + 200))
        zt = zm + 5.2
        for x in xs:
            v.ret(x - 15, zt, 30, 3, "METALICA"); v.ret(x - 12, zt + 3, 24, 13, "METALICA"); v.ret(x - 12, zt + 16, 24, 13, "METALICA")
        v.chamada((AS["x_neo"][1] - 30, g0 + 10), ((R + 300 - AS["x_neo"][1]) / 10, -12), "CA-L2 250×250×19 A36 galv.; graute 20")
        v.chamada((R + 100, zm + 100), (20, 10), f"{AS.get('viga', 'W')} (mesa com furo Ø18 / oblongo)")
        v.chamada((xs[-1] + 12, zt + 22), ((R + 300 - xs[-1]) / 10, 2), "arruela + porca + contraporca M16")
    else:                                                      # neoprene + ponta da TS-01 com furo grauteado
        v.chapa(AS["x_neo"][0], 0, AS["x_neo"][1] - AS["x_neo"][0], 10)
        FOLGA = 25                                             # rev12: folga de montagem cabeça × ponta da viga (NG01, montagem)
        v.poli([(FOLGA, 10), (R + 150, 10), (R + 150, 10 + 400), (FOLGA, 10 + 400)], "VISTA")
        v.interrupcao((R + 150, 10), (R + 150, 410)); v.interrupcao((FOLGA, 410), (R + 150, 410))
        v.cota_h([0, FOLGA], 410, 8, total=False)
        v.chamada((FOLGA / 2, 405), (10, 18), f"folga de montagem {FOLGA} mm")
        for x in xs:
            v.ret(x - 25, 10, 50, livre + 20, "OCULTA")
        v.chamada((AS["x_neo"][1] - 20, 5), (12, -8), f"{AS['neo_nome']}")
        v.chamada((R + 90, 300), (10, 6), f"ponta da {AS.get('viga', 'viga')}: furo Ø50 grauteado")
    for x in xs:                                               # barra: embutida (oculta) + livre (cheia)
        v.ret(x - AS["d"] / 2, -emb, AS["d"], emb, "OCULTA")
        v.chapa(x - AS["d"] / 2, 0, AS["d"], livre)
        if "grampo" in AS.get("anc", ""):
            v.poli([(x - 60, -emb + 60), (x - 60, -emb + 10), (x + 60, -emb + 10), (x + 60, -emb + 60)], "ARMADURA")
    if BR:
        v.linha((xs[0] - 30, livre - BR), (xs[-1] + 30, livre - BR), "OCULTA")
    v.cota_v([-emb, 0, livre], -HW, -9)
    v.cota_h([0] + list(xs) + [R], zb, -19, total=False)
    v.cota_h([-HW, 0], hc, 8)
    v.chamada((xs[-1], -emb + 90), ((R - xs[-1]) / 10 + 30, -4), f"{AS.get('marca_b', AS['pino'])} Ø{g(AS['d'])}: L {g(AS['L'])} = {g(emb)} emb. + {g(livre)} livre")
    v.chamada((xs[-1], -emb + 30), ((R - xs[-1]) / 10 + 30, -14), AS.get("anc", ""))
    lin = []
    if pilha:
        lin.append(f"pilha sobre o concreto {g(round(sum(t for _, t in pilha), 1))} mm, menor que os {g(livre)} mm livres (quadro APOIOS E ESPERAS)")
    lin.append("gabarito na fôrma: barras ±2 mm")
    for k, t in enumerate(lin):
        v.texto((R + 120, hc + 40 - k * 9 * v.esc), t, "nota", "TOP_LEFT")
    return v
