"""ND-LET-COB06 — funilaria da cobertura para o funileiro (rev11, Nathan 26/10/2026): perfil dobrado de cada rufo cotado
(abas em mm, ângulo de cada dobra, desenvolvimento = largura de corte), isométricos explodidos de canto e de emenda, tabela de
funilaria (galvalume #0,50) e conferência do sistema de telhas com o manual Isoeste. Geometria: acabamentos_cob.py (a mesma da COB04
e do 3D). Cotas em mm. A1."""
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
import json
import math
import acabamentos_cob as AC
from prancha_nd import Prancha
from cob_comum import cabecalho, f

R = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/acabamentos_cobertura.json"))
S = AC.secoes()
RUF = {r["marca"]: r for r in R["rufos"]}
pr = Prancha("A1", cabecalho("ND-LET-COB06", "01/01", "COBERTURA — FUNILARIA DA OBRA: PERFIS DOBRADOS DOS RUFOS (ABAS, DOBRAS E LARGURA DE CORTE), CANTOS, EMENDAS E CONFERÊNCIA COM O MANUAL ISOESTE"))
pr.revisao("11", "26/10/2026", "EMISSÃO: FUNILARIA EM GALVALUME #0,50 FEITA NA OBRA (NATHAN); PERFIS DOBRADOS COTADOS; CONFERÊNCIA COM O MANUAL ISOESTE")
Q = pr.quadro
ESP = 0.50                                                    # mm — galvalume #0,50 (definição do Nathan, 26/10/2026)
KG_M2 = 7850 * ESP / 1000                                     # kg/m² de chapa


def perfil(mk):
    """polilinha do rufo em mm, normalizada (primeiro ponto na origem), sem vértices colineares (não são dobras)."""
    pts = [(a * 1000, b * 1000) for a, b in S[mk][1]]
    x0, y0 = pts[0]
    pts = [(x - x0, y - y0) for x, y in pts]
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = out[-1], pts[i], pts[i + 1]
        if abs((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])) > 1e-6 * max(1, math.hypot(b[0] - a[0], b[1] - a[1]) * math.hypot(c[0] - b[0], c[1] - b[1])) * 1e3:
            out.append(b)
    out.append(pts[-1])
    return out


def segmentos(pts):
    L = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])]
    ang = []
    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        u = (a[0] - b[0], a[1] - b[1]); w = (c[0] - b[0], c[1] - b[1])
        cosv = (u[0] * w[0] + u[1] * w[1]) / (math.hypot(*u) * math.hypot(*w))
        ang.append(math.degrees(math.acos(max(-1, min(1, cosv)))))
    return L, ang


# ================================================================== perfis dobrados (1 por marca)
MARCAS = [m for m in S]
COLS, CW, RH = 4, 152, 108
X0, Y0 = Q[0] + 6, Q[3] - 8
TAB = []
for k, mk in enumerate(MARCAS):
    pts = perfil(mk)
    L, ang = segmentos(pts)
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    ext = max(max(xs) - min(xs), max(ys) - min(ys), 1)
    esc = next(e for e in (2, 5, 10, 20) if (max(xs) - min(xs)) / e <= 118 and (max(ys) - min(ys)) / e <= 62)
    c, r_ = k % COLS, k // COLS
    cx = X0 + c * CW + 14 - min(xs) / esc + (CW - 28 - (max(xs) - min(xs)) / esc) / 2
    cy = Y0 - r_ * RH - 22 - max(ys) / esc
    v = pr.vista(mk, (cx, cy), esc, titulo=f"{mk} — {RUF[mk]['chapa'].upper()}", subtitulo=f"largura de corte {sum(L):.0f} mm", unidade="mm")
    v.poli(pts, "METALICA")
    occ = []                                                               # posições já ocupadas (modelo, mm)

    def livre(q, dmin):
        return all(math.hypot(q[0] - o[0], q[1] - o[1]) > dmin for o in occ) and all(
            math.hypot(q[0] - (a_[0] + b_[0]) / 2, q[1] - (a_[1] + b_[1]) / 2) > 0 for a_, b_ in zip(pts, pts[1:]))
    for i, (a, b) in enumerate(zip(pts, pts[1:])):                        # aba: comprimento do lado de fora
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy) or 1
        nx, ny = -dy / n, dx / n
        if L[i] / esc >= 9:
            cand = [(mx + sg * nx * k * esc, my + sg * ny * k * esc) for k in (4.5, 7.5) for sg in (1, -1)]
            q = next((c_ for c_ in cand if livre(c_, 8 * esc)), cand[0])
            v.texto(q, f"{L[i]:.0f}", "cota", "MIDDLE_CENTER"); occ.append(q)
        else:                                                              # aba curta: valor com chamada para fora
            cand = [(nx * k + sx, ny * k + sy) for k in (10, 16) for sx, sy in ((4, 6), (-4, -6), (4, -6), (-4, 6))]
            d_ = next((c_ for c_ in cand if livre((mx + c_[0] * esc, my + c_[1] * esc), 9 * esc)), cand[0])
            v.chamada((mx, my), d_, f"{L[i]:.0f}", "cota"); occ.append((mx + d_[0] * esc, my + d_[1] * esc))
    for i, an in enumerate(ang):                                          # ângulo interno de cada dobra (bissetriz), sem encostar nas abas
        a, b, c = pts[i], pts[i + 1], pts[i + 2]
        u = (a[0] - b[0], a[1] - b[1]); w = (c[0] - b[0], c[1] - b[1])
        nu, nw = math.hypot(*u) or 1, math.hypot(*w) or 1
        bx, by = u[0] / nu + w[0] / nw, u[1] / nu + w[1] / nw
        nb = math.hypot(bx, by) or 1
        v.circulo(b, 1.0 * esc, "COTA")
        cand = [(b[0] + sg * bx / nb * k * esc, b[1] + sg * by / nb * k * esc) for k in (11, 16, 22) for sg in (1, -1)]
        q = next((c_ for c_ in cand if livre(c_, 9 * esc)), cand[0])
        v.texto(q, f"{an:.0f}°", "nota", "MIDDLE_CENTER"); occ.append(q)
    TAB.append([mk, " / ".join(f"{x:.0f}" for x in L), " / ".join(f"{x:.0f}°" for x in ang) or "—", f"{sum(L):.0f}", RUF[mk]["chapa"]])

# ================================================================== isométricos explodidos
CO, SI = math.cos(math.radians(30)), math.sin(math.radians(30))


def iso(x, y, z):
    return ((x - y) * CO, z + (x + y) * SI)


def peca_iso(v, prof, eixo, L, dx=0.0, dy=0.0, dz=0.0, mitra=True):
    """extrusão de um perfil (u horizontal para dentro, w vertical) ao longo de x (eixo 'x') ou y; ponta da quina em mitra a 45°."""
    def P(t, u, w):
        x, y = (t, u) if eixo == "x" else (u, t)
        return iso(x + dx, y + dy, w + dz)
    t0 = [(u if mitra else 0.0) for u, w in prof]
    for (u, w), ts in zip(prof, t0):
        v.linha(P(ts, u, w), P(L, u, w), "METALICA")
    v.poli([P(ts, u, w) for (u, w), ts in zip(prof, t0)], "METALICA")
    v.poli([P(L, u, w) for u, w in prof], "METALICA")


rf1 = [(a * 1000, b * 1000 - AC.PLAT * 1000) for a, b in S["RF-1"][1]]
vi1 = pr.vista("ISO1", (Q[0] + 140, Q[1] + 62), 10, titulo="ISOMÉTRICO 1 — CANTO EXTERNO DA PLATIBANDA (RF-1 / RF-1C)",
               subtitulo="explodido; mitra a 45°, 30 de sobreposição, 2 rebites 4,0 × 10 por aba + PU", unidade="mm")
peca_iso(vi1, rf1, "x", 900, dx=120)
peca_iso(vi1, rf1, "y", 900, dy=120)
for p_, t_ in ((iso(900 + 120, 60, 40), "RF-1 (ao longo da linha 1)"), (iso(60, 900 + 120, 40), "RF-1C (ao longo do eixo A)")):
    vi1.chamada(p_, (6, 10), t_)
vi1.chamada(iso(140, 140, 20), (-40, -14), "rebites + PU na sobreposição de 30 da mitra")

rf4 = [(a * 1000, b * 1000) for a, b in S["RF-4"][1]]
w0 = min(w for u, w in rf4)
rf4 = [(u, w - w0) for u, w in rf4]
vi2 = pr.vista("ISO2", (Q[0] + 400, Q[1] + 40), 15, titulo="ISOMÉTRICO 2 — EMENDA DE RUFOS (TÍPICA, EX.: RF-4)",
               subtitulo="peças de 3000; transpasse de 200; 3 rebites por aba + PU", unidade="mm")
peca_iso(vi2, rf4, "x", 1200, mitra=False)
peca_iso(vi2, rf4, "x", 1200, dx=1000, dz=60, mitra=False)
vi2.chamada(iso(1100, 30, 160), (-30, 26), "transpasse 200 (rebites + PU)")
vi2.chamada(iso(300, 60, 0), (-6, -16), "peça de 3000 (corte com tesoura, sem esmerilhadeira)")

# ================================================================== tabelas
XC = Q[2] - 180
rows = []
for mk, segs, angs, des, ch in TAB:
    r = RUF[mk]
    n3 = math.ceil(r["comprimento_m"] / 2.8)                               # peças de 3 m com 200 de transpasse
    esp = 1.25 if "1,25" in ch else ESP
    kg = r["comprimento_m"] * float(des) / 1000 * 7850 * esp / 1000
    rows.append([mk, segs, angs, des, ch.replace("galvalume ", "galv. "), f(r["comprimento_m"], 1), n3, f(kg, 0)])
y = pr.tabela(Q[0] + 6, Y0 - 3 * RH - 4, "TABELA DE FUNILARIA — ABAS (mm), DOBRAS, LARGURA DE CORTE, COMPRIMENTO E PEÇAS DE 3 m",
              ["MARCA", "ABAS (mm, na ordem)", "DOBRAS", "CORTE", "CHAPA", "m", "PÇ 3 m", "kg"], rows, [16, 150, 92, 16, 30, 16, 16, 14], h_lin=5.2)

CONF = [
    ["Sistema (p. 5, 27–28)", "Zipada Dupla com lã de rocha: TP-40 STD 980 #0,65 + cartola #0,65 + lã FSR-32 + clipe + zipada 455 #0,50", "igual", "confere"],
    ["Inclinação mínima (p. 4)", "2,5 %", "3 %", "confere"],
    ["Clipes (p. 29–30)", "fixo ou deslizante a cada terça, 2 PB 12-14 × 3/4\" P03", "igual; fixos nas 2 terças do meio da água", "confere"],
    ["Base deslizante (p. 30)", "#0,80 sob o clipe deslizante", "igual", "confere"],
    ["TP-40 × terça (p. 28)", "4 PB 12-14 × 3/4\" P03 por telha por terça", "igual (uso 0,22 na sucção de borda)", "confere"],
    ["Cartola × TP-40 (p. 28)", "PB 1/4\"-14 × 7/8\" P01 a cada 2 ondas", "em todas as ondas (sucção de borda)", "mais rigoroso"],
    ["Lã de rocha (p. 28)", "FSR-32 em rolos 600 × 3600, enchendo o vão entre telhas", "FSR-32 40 mm (altura da cartola)", "confere"],
    ["Dilatação (p. 31–32)", "clipes deslizantes; junta de dilatação quando necessário", "ponto fixo no meio da água de 39,6 m (≈ 12 mm por ponta)", "confirmar curso com a Isoeste"],
    ["Beiral na calha (p. 42)", "rufo pingadeira", "PG-1, 100 dentro da calha", "confere"],
    ["Lado alto (p. 40)", "rufo de topo liso + veda-onda", "RF-3 + veda-onda + massa", "confere"],
    ["Bordas laterais (p. 34, 37, 41)", "RB-1 / RB-2 e rufo de acabamento lateral", "RB-1/2 + RF-4 + RF-4C", "confere"],
    ["Platibanda (p. 46–47)", "rufo chapéu", "RF-1 / RF-1C", "confere"],
    ["Acabamentos (p. 39–47)", "catálogo #0,65 pré-pintado", "funilaria da obra galvalume #0,50 (Nathan)", "decisão ND"],
    ["Vão entre terças", "manual de instalação sem tabela vão × carga", f"terças a {min(AC.XT_TER) if hasattr(AC, 'XT_TER') else 813}–1264 mm; fixações verificadas (MC06)", "pedir tabela à Isoeste"],
    ["Painéis solares", "não tratado no manual", "trilhos nas costuras da zipada, sem furar", "confirmar com o fornecedor"],
]
y = pr.tabela(XC, Q[3] - 6, "CONFERÊNCIA COM O MANUAL ISOESTE", ["ITEM (PÁG.)", "MANUAL", "PROJETO", "SITUAÇÃO"], CONF, [34, 62, 56, 28], h_lin=5.2)
pr.notas(XC, y - 4, [
    "Telhas: Isoeste — Telha Zipada Dupla com lã de rocha FSR-32 (manual de instalação Kingspan Isoeste, p. 27–28). A alternativa Rock Felt (manta, p. 48–49) também é lã de rocha; a FSR-32 foi mantida (placa entre as telhas, montagem sanduíche).",
    f"Funilaria feita na obra pelo funileiro: galvalume #0,50 ({KG_M2:.2f} kg/m²), exceto a cantoneira de apoio CR-1 (#1,25 galvanizada, é suporte). Medidas das abas na ordem do desenho, da primeira para a última; dobras com o ângulo interno indicado (tolerância ±2°, abas ±2 mm).",
    "Dobrar em dobradeira; cortar com tesoura ou serra, nunca esmerilhadeira; limpar limalhas no mesmo dia. Peças de 3000 com transpasse de 200 (ISO 2); cantos em mitra com 30 de sobreposição, rebitados e selados com PU (ISO 1); sem solda.",
    "Fixação no concreto: PAR Tapper 1/4\" × 2 3/4\" a cada 500 (250 nas peças de pilar), selante PU no topo dos contra-rufos. Posição de cada peça montada: ND-LET-COB04 (detalhes 1 a 6). Calha: ND-LET-COB03.",
    "PROJETO DA ND ENGENHARIA."], 180)
av = pr.salvar("/home/claude/letsara/pranchas/ND-LET-COB06")
print("COB06", len([a for a in av if a[0] == "ERRO"]), "erros,", len(av), "avisos", av[:12])
