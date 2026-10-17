import json, math, sys
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from geometria import Y_LIN, X_EIXO
T = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/estudo_contraventamento_integrado.json"))
for r in T: r["painel_espacos"] = r["painel"]
LARG, XC = X_EIXO["E"], X_EIXO["C"]
def acha(vaos, n):
    return next(r for r in T if r["vaos"] == vaos and r["painel"] == n)
V5 = ["4-5", "5-6", "6-7", "7-8", "8-9"]
opc = [("Atual (rev05)", "X nos vãos 2-3 e 7-8, painel de 2 terças (75°)", acha(["2-3", "7-8"], 2)),
       ("Sem X", "só terças-escora, correntes e tirantes", acha([], 8)),
       ("Fundo, 2 vãos", "X nos vãos 7-8 e 8-9, painel de 8 terças (45°)", acha(["7-8", "8-9"], 8)),
       ("Fundo, 3 vãos", "X nos vãos 6-7 a 8-9, painel de 8 terças (45°)", acha(["6-7", "7-8", "8-9"], 8)),
       ("Recomendado", "X nos 5 vãos do pavilhão (4-5 a 8-9), painel de 8 terças (45°)", acha(V5, 8)),
       ("5 vãos, painel longo", "X nos vãos 4-5 a 8-9, painel de 16 terças (60°)", acha(V5, 16)),
       ("Todos os vãos", "X nos 8 vãos, painel de 8 terças (45°)", acha([f"{k+1}-{k+2}" for k in range(8)], 8))]
ESQ = [0.0, 1.454, 2.653, 3.852, 5.051, 6.25, 7.449, 8.648, 9.847, 11.046, 12.245, 13.444, 14.643, 15.842, 17.041, 18.24, XC]
def nos(n):
    idx = sorted(set(list(range(0, 17, n)) + [16]))
    e = [ESQ[i] for i in idx]
    return e + [LARG - x for x in reversed(e[:-1])]
def planta(r):
    W, H = 360, 190
    sx, sy = (W - 40) / Y_LIN[-1], (H - 30) / LARG
    X = lambda y: 20 + y * sx
    Yp = lambda x: 15 + x * sy
    s = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="planta do contraventamento: {", ".join(r["vaos"]) or "sem X"}">']
    for x in [Y_LIN[0]] + [0]:
        pass
    for k in range(17 * 2 - 1):
        pass
    xs_t = ESQ + [LARG - x for x in reversed(ESQ[:-1])]
    for x in xs_t:
        s.append(f'<line x1="{X(0):.1f}" y1="{Yp(x):.1f}" x2="{X(Y_LIN[-1]):.1f}" y2="{Yp(x):.1f}" class="terca"/>')
    for i, y in enumerate(Y_LIN):
        s.append(f'<line x1="{X(y):.1f}" y1="{Yp(0):.1f}" x2="{X(y):.1f}" y2="{Yp(LARG):.1f}" class="viga"/>')
        s.append(f'<text x="{X(y):.1f}" y="{H - 3}" class="eixo">{i+1}</text>')
    for lb, x in (("A", 0), ("C", XC), ("E", LARG)):
        s.append(f'<text x="8" y="{Yp(x) + 3:.1f}" class="eixo">{lb}</text>')
    ns = nos(r["painel_espacos"])
    for v in r["vaos"]:
        k = int(v.split("-")[0]) - 1
        ya, yb = Y_LIN[k], Y_LIN[k + 1]
        for a, b in zip(ns[:-1], ns[1:]):
            s.append(f'<line x1="{X(ya):.1f}" y1="{Yp(a):.1f}" x2="{X(yb):.1f}" y2="{Yp(b):.1f}" class="x"/>')
            s.append(f'<line x1="{X(ya):.1f}" y1="{Yp(b):.1f}" x2="{X(yb):.1f}" y2="{Yp(a):.1f}" class="x"/>')
    # áreas: anexo (1-2), área aberta (2-4)
    s.append(f'<rect x="{X(Y_LIN[1]):.1f}" y="{Yp(0) - 9:.1f}" width="{X(Y_LIN[3]) - X(Y_LIN[1]):.1f}" height="6" class="aberto"/>')
    s.append(f'<rect x="{X(Y_LIN[1]):.1f}" y="{Yp(LARG) + 3:.1f}" width="{X(Y_LIN[3]) - X(Y_LIN[1]):.1f}" height="6" class="aberto"/>')
    s.append("</svg>")
    return "".join(s)

f = lambda v, d=0: f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
base = opc[0][2]
def dl(r):
    dp = (r["pilar_uso"] / base["pilar_uso"] - 1) * 100
    return f"""<dl><div><dt>Diagonais</dt><dd>{(str(r["n_diagonais"]) + " × Ø" + f(r["diametro"],1)) if r["n_diagonais"] else "—"}</dd></div>
<div><dt>Aço do X</dt><dd>{f(r["kg_X"])} kg</dd></div>
<div><dt>Tração máx. na diagonal</dt><dd>{(f(r["T_X"],1) + " kN") if r["n_diagonais"] else "—"}</dd></div>
<div><dt>Uso máx. dos pilares</dt><dd>{f(r["pilar_uso"],2)} <small>({dp:+.0f} %)</small></dd></div>
<div><dt>Momento máx. na base</dt><dd>{f(r["M_base"])} kN·m</dd></div>
<div><dt>Terça Z 302, pior interação</dt><dd>{f(r["terca_it"],2)}</dd></div>
<div><dt>Diagonal de ancoragem Ø16</dt><dd>{f(r["diagonal"],2)}</dd></div>
<div><dt>Custo estimado do X</dt><dd>R$ {f(r["custo_X"])}</dd></div></dl>"""
cards = []
for nome, desc, r in opc:
    cls = " rec" if nome == "Recomendado" else ""
    cards.append(f'<article class="op{cls}"><header><h3>{nome}</h3><p>{desc}</p></header>{planta(r)}{dl(r)}</article>')
# gráfico: aço do X x uso dos pilares (14 arranjos)
W, H, L, R_, TOP, BOT = 640, 280, 56, 20, 20, 44
xmx, ymn, ymx = 1500, 0.58, 0.74
px = lambda k: L + k * (W - L - R_) / xmx
py = lambda u: TOP + (ymx - u) * (H - TOP - BOT) / (ymx - ymn)
s = [f'<svg viewBox="0 0 {W} {H}" class="graf" role="img" aria-label="aço do X contra uso máximo dos pilares nos 14 arranjos">']
for u in (0.60, 0.64, 0.68, 0.72):
    s.append(f'<line x1="{L}" x2="{W-R_}" y1="{py(u):.1f}" y2="{py(u):.1f}" class="grade"/><text x="{L-6}" y="{py(u)+4:.1f}" class="tick" text-anchor="end">{f(u,2)}</text>')
for k in range(0, 1501, 300):
    s.append(f'<text x="{px(k):.1f}" y="{H-BOT+18}" class="tick" text-anchor="middle">{k}</text>')
rec = acha(V5, 8)
for r in T:
    c = "pt rec" if r is rec else "pt"
    s.append(f'<circle cx="{px(r["kg_X"]):.1f}" cy="{py(r["pilar_uso"]):.1f}" r="{6 if r is rec else 4}" class="{c}"><title>{", ".join(r["vaos"]) or "sem X"} (painel {r["painel"]}): {r["kg_X"]} kg, uso {r["pilar_uso"]:.3f}</title></circle>')
s.append(f'<text x="{px(rec["kg_X"])+10:.1f}" y="{py(rec["pilar_uso"])+16:.1f}" class="anot">recomendado</text>')
s.append(f'<text x="{(L + W - R_)/2}" y="{H-6}" class="tick" text-anchor="middle">aço do X (kg)</text>')
s.append(f'<text x="14" y="{(TOP + H - BOT)/2}" class="tick" text-anchor="middle" transform="rotate(-90 14 {(TOP + H - BOT)/2})">uso máx. pilares</text>')
s.append("</svg>")
tab = "".join(f"<tr{' class=rec' if r is rec else ''}><td>{', '.join(r['vaos']) or '—'}</td><td>{r['painel']}</td><td>{r['n_diagonais']}</td><td>{r['kg_X']}</td><td>{f(r['T_X'],1)}</td><td>{f(r['pilar_uso'],3)}</td><td>{f(r['M_base'])}</td><td>{f(r['terca_it'],3)}</td><td>{f(r['ST1P']['it'],2)}</td><td>{f(r['custo_X'])}</td></tr>"
              for r in sorted(T, key=lambda r: r["kg_X"]))
html = open("modelo_integrado.html").read()
html = html.replace("%%CARDS%%", "".join(cards)).replace("%%GRAF%%", "".join(s)).replace("%%TAB%%", tab)
open("estudo_contraventamento.html", "w").write(html)
print("ok")
