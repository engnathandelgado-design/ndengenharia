"""Fechamento em placas protendidas 125 × 15 — conforme as VISTAS DO FECHAMENTO LATERAL do R01 (vistas A a J).

Gera:
  ND-LET-CM01 rev 02 — locação das placas, vistas por letra, ordem de montagem das vistas, pendências;
  ND-LET-PP00        — placa típica para produção: fôrma, seção, protensão (força no macaco), insertos, alças, ligações;
  ND-LET-PP-<V>      — uma prancha por vista (A, B, C, D, E-F, G, H-J, I): elevação com as peças numeradas na ordem de
                       produção e montagem, lista da vista e apoio de cada peça;
  ND-LET-VT01 rev 02 — vigas de travamento 25 × 60 a +7,50/+8,10, escondidas atrás da fiada +7,50/+8,75.
Geometria: geometria.py (planta de locação de pilares do R01). Concreto em cm, metálica em mm, níveis em m.
"""
import json
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from prancha_nd import Prancha
from geometria import X_FACH, Y_LIN, X_L4, LARG, COMP

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
PL = json.load(open(AQ + "placas.json"))
f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
M = lambda v: round(v * 1000)
H_PL, E_PL, JUNTA, FOLGA = 1250, 150, 10, 25           # altura e espessura da placa, junta vertical, folga placa × pilar (mm)
Z_TOPO = 10000
Z_VT0, Z_VT1, Z_ASS_VT = 7500, 8100, 7790              # VT 25×60 atrás da fiada +7,50/+8,75; dente 30×20 → assento do CP-VT
PP_KNM = PL["secao"]["pp_kNm"]
FIADAS = list(range(8))
ESQ = (1, 4)                                            # fiadas sem placa (faixas de esquadria) nas vistas H, J e I
PORTA_I = (M(23.79), M(25.59))                          # porta da vista I (fiada 1, vão C–D) — R01: 1,80 m (a confirmar)
FACE_X = (-300, M(LARG) + 300)                          # faces externas dos pilares de canto (direção x)
FACE_Y = (-200, M(COMP) + 200)
CLIENTE = "MARQUES ENGENHARIA E CONSTRUÇÕES"


def eixos_lat(i0, i1):
    return [(M(Y_LIN[i]), 400, f"L{i+1}") for i in range(i0, i1 + 1)]


def eixos_transv(xs, nomes, larg):
    return [(M(x), b, n) for x, b, n in zip(xs, larg, nomes)]


TRANSV = eixos_transv(X_FACH, ["A", "B", "C", "D", "E"], [600, 400, 400, 400, 600])
VISTAS = {
    "A": dict(titulo="VISTA A — FACHADA DA LINHA 9 (vista de fora)", pil=TRANSV, ini=FACE_X[0], fim=FACE_X[1],
              fiadas=lambda k, b: True, nomes_pil=["P1C", "P3", "P14", "P5", "P2C"]),
    "B": dict(titulo="VISTA B — LATERAL DO EIXO A, LINHAS 4 A 9 (vista de fora)", pil=eixos_lat(3, 8), ini=M(Y_LIN[3]) + JUNTA // 2, fim=FACE_Y[1],
              fiadas=lambda k, b: True, vt=True),
    "C": dict(titulo="VISTA C — PAREDE INTERNA DA LINHA 4 (PORTÕES)",
              pil=eixos_transv(X_L4, ["A", "", "", "C", "", "", "E"], [600, 400, 250, 400, 250, 400, 600]), ini=FACE_X[0], fim=FACE_X[1],
              fiadas=lambda k, b: k <= 5, portoes=[1, 4], nomes_pil=["P1", "P9", "P10", "P11", "P10", "P12", "P2"]),
    "D": dict(titulo="VISTA D — LATERAL DO EIXO E, LINHAS 4 A 9 (vista de fora)", pil=eixos_lat(3, 8), ini=M(Y_LIN[3]) + JUNTA // 2, fim=FACE_Y[1],
              fiadas=lambda k, b: True, vt=True),
    "E": dict(titulo="VISTA E — LATERAL DO EIXO A, LINHAS 2 A 4 (aberta até +7,50)", pil=eixos_lat(1, 3), ini=M(Y_LIN[1]) + JUNTA // 2, fim=M(Y_LIN[3]) - JUNTA // 2,
              fiadas=lambda k, b: k >= 6, vt=True),
    "F": dict(titulo="VISTA F — LATERAL DO EIXO E, LINHAS 2 A 4 (aberta até +7,50)", pil=eixos_lat(1, 3), ini=M(Y_LIN[1]) + JUNTA // 2, fim=M(Y_LIN[3]) - JUNTA // 2,
              fiadas=lambda k, b: k >= 6, vt=True),
    "G": dict(titulo="VISTA G — PAREDE INTERNA DA LINHA 2 (face do pavilhão)", pil=TRANSV, ini=FACE_X[0], fim=FACE_X[1],
              fiadas=lambda k, b: k <= 5, nomes_pil=["P1B", "P8", "P8A", "P8B", "P2B"]),
    "H": dict(titulo="VISTA H — LATERAL DO ANEXO, EIXO A, LINHAS 1 A 2", pil=eixos_lat(0, 1), ini=FACE_Y[0], fim=M(Y_LIN[1]) - JUNTA // 2,
              fiadas=lambda k, b: k not in ESQ, esquadria=True),
    "I": dict(titulo="VISTA I — FACHADA DA LINHA 1 (anexo, vista de fora)", pil=TRANSV, ini=FACE_X[0], fim=FACE_X[1],
              fiadas=lambda k, b: k not in ESQ, esquadria=True, porta=(2, 0, PORTA_I), nomes_pil=["P1A", "P3", "P4", "P5", "P2A"]),
    "J": dict(titulo="VISTA J — LATERAL DO ANEXO, EIXO E, LINHAS 1 A 2", pil=eixos_lat(0, 1), ini=FACE_Y[0], fim=M(Y_LIN[1]) - JUNTA // 2,
              fiadas=lambda k, b: k not in ESQ, esquadria=True),
}
ORDEM_VISTAS = ["I", "H", "J", "G", "E", "F", "C", "B", "D", "A"]      # anexo → área aberta → pavilhão → fachada da linha 9


def montar(V):
    """Peças da vista na ordem de produção/montagem: vão a vão (esquerda → direita), de baixo para cima."""
    d = VISTAS[V]
    pil = d["pil"]
    pecas, ca1, abert = [], [], []
    n = 0
    for b, ((sa, ba, _), (sb, bb, _)) in enumerate(zip(pil[:-1], pil[1:])):
        s0 = d["ini"] if b == 0 else sa + JUNTA // 2
        s1 = d["fim"] if b == len(pil) - 2 else sb - JUNTA // 2
        if b in d.get("portoes", []):
            abert.append((sa + ba // 2, sb - bb // 2, 0, 7500, "portão"))
            continue
        ks = [k for k in FIADAS if d["fiadas"](k, b)]
        if d.get("esquadria"):
            for k in ESQ:
                abert.append((s0, s1, k * H_PL, (k + 1) * H_PL, "esquadria"))
        for k in ks:
            z0 = k * H_PL
            if k == 0:
                apoio = "viga baldrame"
            elif (k - 1) in ks:
                apoio = "placa de baixo"
            else:
                apoio = "2 consolos CA-1"
                ca1 += [(sa, z0), (sb, z0)]
            trechos = [(s0, s1)]
            if d.get("porta") and d["porta"][0] == b and d["porta"][1] == k:
                p0, p1 = d["porta"][2]
                trechos = [(s0, p0 - JUNTA // 2), (p1 + JUNTA // 2, s1)]
                abert.append((p0, p1, 0, 2 * H_PL, "porta"))
            for (t0, t1) in trechos:
                n += 1
                pecas.append(dict(id=f"{V}-{n:02d}", seq=n, bay=b, k=k, s0=t0, s1=t1, z0=z0, z1=z0 + H_PL, L=t1 - t0, apoio=apoio))
    return pecas, ca1, abert


DADOS = {V: montar(V) for V in VISTAS}
TIPOS = {}
for V, (pecas, _, _) in DADOS.items():
    for p in pecas:
        TIPOS.setdefault(p["L"], []).append((V, p["id"]))
TIPO = {L: f"PP-{i+1:02d}" for i, L in enumerate(sorted(TIPOS, key=lambda L: -L))}
N_TOT = sum(len(v) for v in TIPOS.values())
peso_t = lambda L: PP_KNM * L / 1000 / 9.81
PESO_TOT = sum(len(v) * peso_t(L) for L, v in TIPOS.items())


def carimbo(desenho, conteudo, folha, rev="00", fmt="A1"):
    return Prancha(fmt, dict(cliente=CLIENTE, obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR", conteudo=conteudo,
                             desenho=desenho, folha=folha, fase="PARA APROVAÇÃO", rev=rev))


# ================================================================== elevação de uma vista
def desenhar_elev(pr, V, origem, esc):
    d = VISTAS[V]
    pecas, ca1, abert = DADOS[V]
    vv = pr.vista(f"VISTA {V}", origem, esc, titulo=d["titulo"], subtitulo="peças numeradas na ordem de produção e montagem (vão a vão, de baixo para cima)", unidade="cm")
    nomes = d.get("nomes_pil")
    for i, (s, b, _) in enumerate(d["pil"]):
        zt = 7500 if nomes and nomes[i] == "P10" else Z_TOPO
        vv.ret(s - b / 2, -500, b, zt + 500, "OCULTA")
        if nomes:
            vv.texto((s, zt + 200), nomes[i], "min", "BOTTOM_CENTER")
    vv.linha((d["ini"] - 800, 0), (d["fim"] + 800, 0), "TERRENO")
    vv.ret(d["ini"], -500, d["fim"] - d["ini"], 500, "VISTA")                                     # viga baldrame (fundação)
    if d.get("vt"):
        for (sa, ba, _), (sb, bb, _) in zip(d["pil"][:-1], d["pil"][1:]):
            vv.ret(sa + ba / 2 + 25, Z_VT0, sb - sa - (ba + bb) / 2 - 50, Z_VT1 - Z_VT0, "OCULTA")
    for (a0, a1, z0, z1, rot) in abert:
        pts = [(a0, z0), (a1, z0), (a1, z1), (a0, z1)]
        vv.hachura(pts, "ANSI37", 3.0, "HACHURA")
        vv.poli(pts, "EIXO", fechada=True)
        vv.texto(((a0 + a1) / 2, (z0 + z1) / 2), {"portão": "PORTÃO — livre até +7,50", "porta": "PORTA", "esquadria": "esquadria"}[rot], "min", "MIDDLE_CENTER")
    for p in pecas:
        vv.ret(p["s0"], p["z0"] + JUNTA / 2, p["L"], H_PL - JUNTA, "VISTA")
        vv.texto(((p["s0"] + p["s1"]) / 2, p["z0"] + H_PL * 0.6), p["id"], "nota", "MIDDLE_CENTER")
        vv.texto(((p["s0"] + p["s1"]) / 2, p["z0"] + H_PL * 0.22), TIPO[p["L"]], "min", "MIDDLE_CENTER")
    for (s, z) in ca1:
        vv.chapa(s - 100, z - 175, 200, 175, 3.0)
    vv.cota_h([s for s, _, _ in d["pil"]], -500, -8, total=False)
    vv.cota_h([d["ini"], d["fim"]], -500, -16, total=False)
    vv.cota_v([k * H_PL for k in range(0, 9)], d["fim"], 10, total=False)
    for (s, b, nome) in d["pil"]:
        if nome:
            x, y = vv.P(s, -500)
            vv._add(pr.msp.add_circle((x, y - 30), 3.4, dxfattribs={"layer": "INDICACAO"}))
            vv._add(pr.texto(x, y - 30, nome, "min", "TITULO", "MIDDLE_CENTER"))
    return vv


# ================================================================== corte vertical da parede e planta-chave (pranchas por vista)
def corte_parede(pr, V, origem, esc=50):
    """Corte vertical típico da parede da vista: pilha de placas, baldrame, IP-01 / CL-1 nas fiadas, CA-1 e VT quando houver."""
    d = VISTAS[V]
    pecas, ca1, _ = DADOS[V]
    ks = sorted(set(p["k"] for p in pecas if p["bay"] == pecas[0]["bay"]))
    c = pr.vista(f"CORTE {V}", origem, esc, titulo=f"CORTE TÍPICO DA PAREDE — VISTA {V}", subtitulo="placas por fora do pilar; ligação em cada fiada", unidade="cm")
    c.ret(-FOLGA - E_PL - 100, -500, 500, 500, "CORTADO"); c.hachura([(-FOLGA - E_PL - 100, -500), (-FOLGA - E_PL + 400, -500), (-FOLGA - E_PL + 400, 0), (-FOLGA - E_PL - 100, 0)], "AR-CONC", 0.02)
    c.ret(0, -500, 600, Z_TOPO + 500, "OCULTA")                                                     # pilar (lado de 60), atrás
    for k in ks:
        z0 = k * H_PL
        pts = [(-FOLGA - E_PL, z0 + 5), (-FOLGA, z0 + 5), (-FOLGA, z0 + H_PL - 5), (-FOLGA - E_PL, z0 + H_PL - 5)]
        c.poli(pts, "CORTADO", fechada=True); c.hachura(pts, "AR-CONC", 0.02)
        c.chapa(-9.5, z0 + H_PL - 175, 9.5, 150, 3.0)                                               # IP-01
        c.chapa(-FOLGA, z0 + H_PL - 150, FOLGA - 9.5, 100, 3.0)                                     # CL-1 + CH-P1
        if (k - 1) not in ks and k > 0:
            c.chapa(-FOLGA - E_PL, z0 - 16, FOLGA + E_PL, 16, 3.0)                                  # CA-1
    if d.get("vt"):
        c.ret(175, Z_VT0, 250, Z_VT1 - Z_VT0, "OCULTA")
        c.chamada((300, Z_VT1), (10, 8), "VT 25×60 entre os pilares (atrás)")
    c.cota_v([k * H_PL for k in range(0, 9)], -FOLGA - E_PL, -10, total=False)
    c.cota_h([-FOLGA - E_PL, -FOLGA, 0, 600], -500, -8, total=False)
    k0 = ks[-1]
    c.chamada((-FOLGA - E_PL / 2, k0 * H_PL + 600), (-14, 8), "placa 125 × 15")
    c.chamada((-12, k0 * H_PL + H_PL - 100), (16, 10), "IP-01 + CL-1 + CH-P1 (PP00, det. 2)")
    if ks[0] > 0 or len(ks) < 8:
        kk = [k for k in ks if k > 0 and (k - 1) not in ks]
        if kk:
            c.chamada((-FOLGA - E_PL / 2, kk[0] * H_PL - 8), (-14, -10), "consolo CA-1 (PP00, det. 4)")
    if 0 in ks:
        c.chamada((-FOLGA - E_PL, -250), (-12, -8), "viga baldrame (fundação)")
    return c


def planta_chave(pr, Vs, origem, esc=1000):
    k = pr.vista("PLANTA-CHAVE", origem, esc, titulo="PLANTA-CHAVE", subtitulo="parede da(s) vista(s) em destaque", unidade="cm")
    k.ret(FACE_X[0], FACE_Y[0], FACE_X[1] - FACE_X[0], FACE_Y[1] - FACE_Y[0], "VISTA")
    for i, y in enumerate(Y_LIN):
        k.linha((FACE_X[0] - 1500, M(y)), (FACE_X[1] + 1500, M(y)), "EIXO")
        k.texto((FACE_X[0] - 2500, M(y)), str(i + 1), "min", "MIDDLE_RIGHT")
    for j, x in enumerate(X_FACH):
        k.linha((M(x), FACE_Y[0] - 1500), (M(x), FACE_Y[1] + 1500), "EIXO")
        k.texto((M(x), FACE_Y[1] + 2500), "ABCDE"[j], "min", "BOTTOM_CENTER")
    linhas = {"A": ((FACE_X[0], FACE_Y[1]), (FACE_X[1], FACE_Y[1])), "I": ((FACE_X[0], FACE_Y[0]), (FACE_X[1], FACE_Y[0])),
              "G": ((FACE_X[0], M(Y_LIN[1])), (FACE_X[1], M(Y_LIN[1]))), "C": ((FACE_X[0], M(Y_LIN[3])), (FACE_X[1], M(Y_LIN[3]))),
              "B": ((FACE_X[0], M(Y_LIN[3])), (FACE_X[0], FACE_Y[1])), "D": ((FACE_X[1], M(Y_LIN[3])), (FACE_X[1], FACE_Y[1])),
              "E": ((FACE_X[0], M(Y_LIN[1])), (FACE_X[0], M(Y_LIN[3]))), "F": ((FACE_X[1], M(Y_LIN[1])), (FACE_X[1], M(Y_LIN[3]))),
              "H": ((FACE_X[0], FACE_Y[0]), (FACE_X[0], M(Y_LIN[1]))), "J": ((FACE_X[1], FACE_Y[0]), (FACE_X[1], M(Y_LIN[1])))}
    for V in Vs:
        (a, b) = linhas[V]
        horiz = a[1] == b[1]
        k.ret(min(a[0], b[0]) - (0 if horiz else 600), min(a[1], b[1]) - (600 if horiz else 0), abs(b[0] - a[0]) + (0 if horiz else 1200), abs(b[1] - a[1]) + (1200 if horiz else 0), "CORTADO")
        k.hachura([(min(a[0], b[0]) - (0 if horiz else 600), min(a[1], b[1]) - (600 if horiz else 0)), (max(a[0], b[0]) + (0 if horiz else 600), min(a[1], b[1]) - (600 if horiz else 0)),
                   (max(a[0], b[0]) + (0 if horiz else 600), max(a[1], b[1]) + (600 if horiz else 0)), (min(a[0], b[0]) - (0 if horiz else 600), max(a[1], b[1]) + (600 if horiz else 0))], "SOLID", 1, "CORTADO")
        cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        off = (0, 3500) if horiz and a[1] > 40000 else (0, -3500) if horiz and a[1] < 1000 else (0, 3000) if horiz else (-3500, 0) if a[0] < 0 else (3500, 0)
        k.circulo((cx + off[0], cy + off[1]), 1800, "INDICACAO")
        k.texto((cx + off[0], cy + off[1]), V, "nota", "MIDDLE_CENTER")
    return k


# ================================================================== prancha de produção/montagem por vista
def prancha_vista(Vs, desenho, folha):
    lista = [p for V in Vs for p in DADOS[V][0]]
    nome = " E ".join(Vs)
    pr = carimbo(desenho, f"PLACAS DE FECHAMENTO PROTENDIDAS — VISTA{'S' if len(Vs) > 1 else ''} {nome}: PRODUÇÃO E MONTAGEM EM SEQUÊNCIA", folha)
    pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL — CONFORME AS VISTAS DO FECHAMENTO DO R01")
    Q = pr.quadro
    XC = Q[2] - 190
    pesos = sum(peso_t(p["L"]) for p in lista)
    pr.cabecalho_peca(f"VISTA {nome}", f"PLACAS PROTENDIDAS 125 × 15 — {len(lista)} PEÇAS — {f(pesos, 1)} t",
                      " · ".join(VISTAS[V]["titulo"].split(" — ")[1] for V in Vs) + " · produzir e montar na ordem dos números · placa típica: ND-LET-PP00",
                      largura=XC - Q[0] - 10)
    larg_util = XC - Q[0] - 50
    y_band = Q[1] + 255                                   # faixa de baixo: corte da parede + planta-chave
    alt_top = (Q[3] - 40) - y_band
    n = len(Vs)
    w_slot = larg_util / n
    for j, V in enumerate(Vs):
        d = VISTAS[V]
        comp = d["fim"] - d["ini"] + 1600
        e = next(e for e in (50, 75, 100, 125, 150, 200, 250) if comp / e <= w_slot - 12 and (Z_TOPO + 1500) / e <= alt_top - 40)
        x_slot = Q[0] + 35 + j * w_slot
        y0 = Q[3] - 46 - (Z_TOPO + 500) / e
        desenhar_elev(pr, V, (x_slot + (w_slot - comp / e) / 2 + 800 / e - d["ini"] / e, y0), e)
    corte_parede(pr, Vs[0], (Q[0] + 70, Q[1] + 42))
    planta_chave(pr, Vs, (Q[0] + 330, Q[1] + 60), 700)
    # lista de produção
    y = Q[3] - 6
    rows = [[p["seq"], p["id"], TIPO[p["L"]], f"{p['L']/10:.1f}".replace(".", ","), f"+{f(p['z0']/1000, 2)}", f(peso_t(p["L"]), 2), p["apoio"]] for p in lista]
    h = 4.4 if len(rows) > 32 else 5.0
    y = pr.tabela(XC, y, "LISTA DE PRODUÇÃO E MONTAGEM (na ordem)", ["SEQ", "PEÇA", "TIPO", "L (cm)", "BASE", "PESO (t)", "APOIO DA PEÇA"],
                  rows, [10, 18, 18, 18, 18, 18, 90], h_lin=h)
    res = {}
    for p in lista:
        res.setdefault(TIPO[p["L"]], [0, p["L"]])[0] += 1
    rr = [[t, f"{L/10:.1f}".replace(".", ","), n_, f(n_ * peso_t(L), 1)] for t, (n_, L) in sorted(res.items())]
    rr.append(["", "total", len(lista), f(pesos, 1)])
    y = pr.tabela(XC, y - 4, "RESUMO POR TIPO", ["TIPO", "L (cm)", "QT", "PESO (t)"], rr, [40, 50, 30, 70], h_lin=5.0, destaque_ultima=True)
    n_ca = sum(len(DADOS[V][1]) for V in Vs)
    notas = [f"Produzir na ordem da coluna SEQ e etiquetar cada peça com o código (ex.: {lista[0]['id']}) e o tipo; estocar por vista, na ordem inversa da montagem.",
             "Montagem vão a vão, de baixo para cima; em cada ponta, chapa CL-1 soldada no IP-01 do pilar e no CH-P1 da placa antes de soltar o guindaste.",
             "Placa protendida 125 × 15, C40, 8 cord. Ø9,5 CP-190 RB, 77,7 kN por cordoalha no macaco: seção, insertos, alças e ligações na ND-LET-PP00."]
    if n_ca:
        notas.append(f"Consolos metálicos CA-1 ({n_ca} nesta prancha, hachurados na elevação) soldados no IP-01 do pilar antes de montar a peça que apoiam (PP00, detalhe 4).")
    if "C" in Vs:
        notas.append("Placas até +7,50; acima, até a telha, fechamento leve na face da TS-01 (as terças cruzam a linha 4 acima de +8,37) — pendência. Portões P9–P10 e P10–P12 livres até +7,50.")
    if "G" in Vs:
        notas.append("Placas na face do pavilhão (a laje do mezanino passa na face do anexo), até +7,50; acima, fechamento leve até a telha — pendência.")
    if any(V in Vs for V in ("H", "J", "I")):
        notas.append("Faixas hachuradas: esquadrias do anexo (R01), sem placa, de +1,25 a +2,50 e de +5,00 a +6,25; placa acima de cada faixa apoiada em 2 CA-1." + (" Porta: 180 × 250 (a confirmar)." if "I" in Vs else ""))
    if any(V in Vs for V in ("E", "F")):
        notas.append("Abertas até +7,50 (R01): as 2 fiadas de cima apoiam em consolos CA-1; a VT fica atrás da fiada +7,50/+8,75 (ND-LET-VT01).")
    notas.append("Cotas de concreto em cm, níveis em m. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR.")
    pr.notas(XC, y - 4, notas, 190)
    avisos = pr.salvar(f"/home/claude/letsara/pranchas/{desenho}")
    print(desenho, len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos", [a for a in avisos if a[0] == "ERRO" or "sobrep" in a[1]][:6])


# ================================================================== ND-LET-PP00 — placa típica
def prancha_tipo():
    P = PL
    pr = carimbo("ND-LET-PP00", "PLACA DE FECHAMENTO PROTENDIDA 125 × 15 — FÔRMA, PROTENSÃO, INSERTOS, ALÇAS, LIGAÇÕES E TIPOS (PRODUÇÃO)", "01/01")
    pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL")
    Q = pr.quadro
    XC = Q[2] - 190
    Ls = sorted(TIPOS)
    pr.cabecalho_peca("PP", f"PLACA MACIÇA PROTENDIDA 125 × 15 cm — L = {Ls[0]/10:.1f} A {Ls[-1]/10:.1f} cm — {len(TIPO)} TIPOS — {N_TOT} PEÇAS".replace(".", ","),
                      f"C{P['secao']['fck']:.0f} / fckj {P['secao']['fckj']:.0f} MPa · 8 cord. Ø9,5 CP-190 RB (4 por face) · σpi 1400 MPa · {f(P['protensao']['F_macaco_kN'])} kN por cordoalha no macaco · {f(PP_KNM, 2)} kN/m",
                      largura=XC - Q[0] - 10)
    # ---- elevação da placa típica (1:25), interrompida
    e = pr.vista("ELEVAÇÃO", (Q[0] + 45, Q[3] - 125), 25, titulo="ELEVAÇÃO DE FÔRMA — PLACA TÍPICA (face interna)", subtitulo="comprimento L pela tabela de tipos; desenho interrompido", unidade="cm")
    LD, LE = 3500, 2200
    for (a, b) in ((0, LD), (LD + 500, LD + 500 + LE)):
        e.linha((a, 0), (b, 0), "VISTA"); e.linha((a, H_PL), (b, H_PL), "VISTA")
        for z in (156, 469, 781, 1094):
            e.linha((a, z), (b, z), "ARM_PROT")
    e.linha((0, 0), (0, H_PL), "VISTA"); e.linha((LD + 500 + LE, 0), (LD + 500 + LE, H_PL), "VISTA")
    e.interrupcao((LD, 0), (LD, H_PL)); e.interrupcao((LD + 500, 0), (LD + 500, H_PL))
    e.chapa(60 - 50, H_PL - 150, 100, 100, 1.5); e.chapa(LD + 500 + LE - 110, H_PL - 150, 100, 100, 1.5)
    for xa in (2100, LD + 500 + LE - 2100 + 900):
        e.poli([(xa - 60, H_PL), (xa - 60, H_PL + 120), (xa + 60, H_PL + 120), (xa + 60, H_PL)], "METALICA")
    e.cota_h([0, 60, 2100, LD], H_PL, 16, total=False)
    e.cota_v([0, 156, 469, 781, 1094, H_PL], 0, -10, total=False)
    e.cota_v([H_PL - 150, H_PL - 100, H_PL - 50, H_PL], LD + 500 + LE, 10, total=False)
    e.chamada((60, H_PL - 100), (12, -14), "CH-P1 nas 2 pontas, centro a 6,5 cm do eixo do pilar e 10 cm do topo")
    e.chamada((2100, H_PL + 120), (10, 10), "AL-P alça de cordoalha Ø12,7 (2 por placa, a 0,21 L das pontas)")
    e.chamada((1500, 781), (12, -20), "C1 — 8 cord. Ø9,5 (4 por face), aderentes, cortadas rente às pontas")
    e.marcador_corte((2800, -350), (2800, H_PL + 350), "A", lado=1)
    # ---- corte A-A (1:5)
    s = pr.vista("CORTE A-A", (Q[0] + 520, Q[1] + 70), 10, titulo="CORTE A-A", subtitulo="encaixe macho-fêmea, cordoalhas, cobrimento 3,5", unidade="cm")
    pts = [(0, 0), (45, 0), (45, 35), (105, 35), (105, 0), (150, 0), (150, 1250), (105, 1250), (105, 1280), (45, 1280), (45, 1250), (0, 1250)]
    s.poli(pts, "CORTADO", fechada=True); s.hachura(pts, "AR-CONC", 0.03)
    for z in (156, 469, 781, 1094):
        for xx in (40, 110):
            s.ponto_barra((xx, z), 9.5, "ARM_PROT_SECAO")
    s.poli([(25, 70), (25, 1210)], "ARM_TRANSV"); s.poli([(125, 70), (125, 1210)], "ARM_TRANSV")
    s.ponto_barra((75, 1215), 8); s.ponto_barra((75, 80), 8)
    s.cota_h([0, 40, 110, 150], 0, -10, total=True)
    s.cota_v([0, 35, 156, 469, 781, 1094, 1250, 1280], 150, 10, total=False)
    s.chamada((110, 469), (16, 6), "C1 — 8 cord. Ø9,5 (4 por face, eixo a 4 cm)")
    s.chamada((125, 900), (16, 8), "N1 — tela Q92 nos 60 cm das pontas")
    s.chamada((75, 1215), (-14, 10), "N2 — 1 Ø8 no macho")
    s.chamada((75, 80), (-14, -12), "N2 — 1 Ø8 sobre a fêmea")
    s.chamada((75, 1265), (14, 12), "macho 6 × 3")
    s.chamada((75, 17), (16, -14), "fêmea 6 × 3,5")
    # ---- detalhe 1: CH-P1 (1:5 mm)
    d1 = pr.vista("DETALHE 1", (Q[0] + 70, Q[3] - 240), 5, titulo="DETALHE 1 — INSERTO CH-P1 DA PLACA", subtitulo="2 por placa, face interna, galvanizado a fogo", unidade="mm")
    d1.chapa(-50, -50, 100, 100, 0.6)
    for dz in (-30, 30):
        d1.circulo((0, dz), 5, "VISTA")
    d1.cota_h([-50, 50], -50, -8); d1.cota_v([-50, -30, 30, 50], 50, 8, total=False)
    d1.chapa(120, -50, 9.5, 100, 0.6)
    for dz in (-30, 30):
        d1.chapa(129.5, dz - 5, 80, 10, 0.6); d1.chapa(209.5, dz - 10, 6, 20, 0.6)
    d1.cota_h([120, 129.5, 209.5, 215.5], -50, -8, total=False)
    d1.chamada((-30, 30), (-8, 14), "chapa 100 × 100 × 9,5 A36")
    d1.chamada((170, 30), (6, 14), "2 pinos Ø10 L=80 c/ cabeça Ø20")
    # ---- detalhe 2: ligação placa × pilar (planta, 1:5 mm)
    d2 = pr.vista("DETALHE 2", (Q[0] + 330, Q[3] - 300), 5, titulo="DETALHE 2 — LIGAÇÃO PLACA × PILAR (PLANTA)", subtitulo="pilar com lado de 40 na parede; junta 10 no eixo; folga 25; solda em obra", unidade="mm")
    pil = [(-200, 0), (200, 0), (200, 450), (-200, 450)]
    d2.poli(pil, "CORTADO", fechada=True); d2.hachura(pil, "AR-CONC", 0.03)
    for sg in (-1, 1):
        x0 = sg * 5
        pts = [(x0, -FOLGA), (sg * 650, -FOLGA), (sg * 650, -FOLGA - 150), (x0, -FOLGA - 150)]
        d2.poli(pts, "CORTADO", fechada=True); d2.hachura(pts, "AR-CONC", 0.03)
        d2.chapa(sg * 65 - 50, -FOLGA, 100, 9.5, 0.4)                        # CH-P1 (face interna da placa)
        d2.chapa(sg * 65 - 30, -FOLGA + 9.5, 60, FOLGA - 9.5 - 9.5, 0.4)      # CL-1
    d2.chapa(-75, -9.5, 150, 9.5, 0.4)                                       # IP-01 do pilar
    d2.cota_h([-650, -115, -15, -5, 5, 15, 115, 650], -FOLGA - 150, -10, total=False)
    d2.cota_v([-FOLGA - 150, -FOLGA, 0, 450], 200, 10, total=False)
    d2.chamada((0, -5), (12, 18), "IP-01 150 × 150 × 9,5 do pilar")
    d2.chamada((65, -FOLGA / 2), (30, 4), "CL-1 chapa 6 × 60 × 80 A36, filete 6 mm nos 2 lados")
    d2.chamada((-65, -FOLGA + 5), (-16, 14), "CH-P1 da placa")
    d2.chamada((-400, -100), (-10, -14), "placa 15 cm")
    d2.chamada((0, -FOLGA - 100), (8, -24), "junta 10 mm: tarucel + selante PU")
    # ---- detalhe 4: consolo metálico CA-1 (corte vertical, 1:5 mm)
    d4 = pr.vista("DETALHE 4", (Q[0] + 330, Q[1] + 115), 5, titulo="DETALHE 4 — CONSOLO METÁLICO CA-1", subtitulo="apoio da 1ª placa de pacote suspenso (vistas E, F, H, I, J)", unidade="mm")
    d4.ret(0, -350, 400, 750, "VISTA")
    d4.chapa(-9.5, -175, 9.5, 150, 0.4)                                       # IP-01 (fiada de baixo)
    d4.chapa(-9.5 - FOLGA - 150, -16, FOLGA + 150, 16, 0.4)                   # mesa
    d4.chapa(-9.5 - 120, -166, 120, 150, 0.4)                                 # nervura
    d4.ret(-9.5 - FOLGA - 140, 0, 130, 10, "METALICA")                       # neoprene 10
    pts = [(-9.5 - FOLGA - 150, 10), (-9.5 - FOLGA, 10), (-9.5 - FOLGA, 400), (-9.5 - FOLGA - 150, 400)]
    d4.poli(pts, "CORTADO", fechada=True); d4.hachura(pts, "AR-CONC", 0.03)
    d4.cota_v([-166, -16, 0, 10], -9.5 - FOLGA - 150, -10, total=False)
    d4.cota_h([-9.5 - FOLGA - 150, -9.5 - FOLGA, -9.5, 0], -166, -10, total=False)
    d4.chamada((-60, -8), (-16, -20), "CA-1: mesa 16 × 175 × 200 + nervura 16 × 120 × 150 (A36)")
    d4.chamada((-5, -110), (14, -12), "IP-01 do pilar")
    d4.chamada((-100, 5), (-14, 16), "neoprene 130 × 150 × 10")
    d4.chamada((-120, 250), (-12, 10), "1ª placa do pacote")
    d4.chamada((-60, -100), (12, -26), f"filete 8 mm (2 × 200): Rd {f(P['fixacoes']['R_consolo_CA1_d'])} kN ≪ {f(P['fixacoes']['solda_CA1_Rd'], 0)} kN")
    # ---- detalhe 5: alça AL-P (1:10)
    d5 = pr.vista("DETALHE 5", (Q[0] + 110, Q[1] + 110), 10, titulo="DETALHE 5 — ALÇA AL-P", subtitulo="cordoalha Ø12,7 CP-190 RB", unidade="cm")
    d5.ret(-250, -600, 500, 600, "VISTA")
    d5.poli([(-60, -550), (-60, 80), (0, 120), (60, 80), (60, -550)], "ARMADURA")
    for xx in (-60, 60):
        d5.linha((xx, -550), (xx - 40, -620), "ARMADURA")
    d5.cota_v([-550, 0, 120], 250, 8, total=False)
    d5.chamada((0, 120), (-30, 10), f"laço de 1,40 m; {f(P['transitorias']['F_alca_kN'])} kN por alça")
    # ---- tabelas
    y = Q[3] - 6
    rows = []
    for L in sorted(TIPOS, key=lambda L: -L):
        vis = sorted(set(v for v, _ in TIPOS[L]))
        rows.append([TIPO[L], f"{L/10:.1f}".replace(".", ","), len(TIPOS[L]), f(peso_t(L), 2), ", ".join(vis)])
    rows.append(["", "total", N_TOT, f(PESO_TOT, 1), ""])
    y = pr.tabela(XC, y, f"TIPOS DE PLACA — {N_TOT} PEÇAS", ["TIPO", "L (cm)", "QT", "PESO (t)", "VISTAS"], rows, [18, 22, 14, 22, 114], destaque_ultima=True)
    tc = pr.tabela_cordoalhas(XC, y - 4, [dict(pos="C1", diam=9.5, qtd=8, y=40, forca=P["protensao"]["F_macaco_kN"], isol=0)], 60)
    y = tc["y_base"]
    ins = [["CH-P1", "Chapa 100×100×9,5 + 2 pinos Ø10 c/ cabeça (galv.)", 2, "face interna, pontas, 10 cm do topo"],
           ["AL-P", "Laço de cordoalha Ø12,7 (1,40 m)", 2, "topo, a 0,21 L das pontas"],
           ["CL-1", "Chapa 6×60×80 A36 (obra)", 2, "entre IP-01 e CH-P1"],
           ["CA-1", "Consolo metálico, mesa 16 + nervura 16", "—", "sob a 1ª placa de pacote suspenso"]]
    y = pr.tabela(XC, y - 4, "INSERTOS E PEÇAS METÁLICAS — mm", ["MARCA", "DESCRIÇÃO", "QT/PL", "POSIÇÃO"], ins, [14, 86, 14, 76])
    y = pr.legenda_armadura(XC, y - 4, True)
    pr.notas(XC, y - 4, [
        f"Concreto C{P['secao']['fck']:.0f}; liberar a protensão, desformar e bascular com fckj ≥ {P['secao']['fckj']:.0f} MPa. Cobrimento 3,5 cm (CAA II).",
        f"Protensão: 8 cordoalhas Ø9,5 CP-190 RB aderentes, 4 por face, σpi = 1400 MPa — {f(P['protensao']['F_macaco_kN'])} kN por cordoalha no macaco; alongamento teórico {P['protensao']['along_pista_60m_mm']} mm em pista de 60 m (tolerância ±7 %).",
        "Produção deitada, face interna para cima (CH-P1 nivelados com a face); basculamento e montagem pelas alças AL-P do topo; estocagem deitada em 2 calços a 0,21 L, até 6 placas com calços alinhados.",
        "Montagem: 1ª placa de cada pano na viga baldrame ou em 2 consolos CA-1; as demais encaixadas na de baixo com tira de elastômero 10 mm; CL-1 soldada nas duas pontas antes de soltar o guindaste.",
        "Tipo = comprimento; nas pontas de canto a placa vai até a face externa do pilar de canto. Posição de cada peça: pranchas das vistas (ND-LET-PP-A … PP-I).",
        "Cotas de concreto em cm, metálicas em mm. Não medir no desenho. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."], 190)
    avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-PP00")
    print("PP00", len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos", [a for a in avisos if a[0] == "ERRO" or "sobrep" in a[1]][:8])


# ================================================================== ND-LET-CM01 rev 02 — locação e ordem das vistas
def prancha_cm():
    pr = carimbo("ND-LET-CM01", "PLACAS DE FECHAMENTO — LOCAÇÃO CONFORME AS VISTAS DO R01 (A A J), ORDEM DE MONTAGEM DAS VISTAS E PENDÊNCIAS", "01/01", rev="02")
    pr.revisao("01", "12/10/2026", "LOCAÇÃO E VISTAS CONFORME R01 (A–J)")
    pr.revisao("02", "12/10/2026", "GEOMETRIA DA LOCAÇÃO DO R01; H/J LATERAIS DO ANEXO; E/F ABERTAS ATÉ +7,50; 2 PORTÕES; PRANCHAS POR VISTA")
    Q = pr.quadro
    XC = Q[2] - 190
    pr.cabecalho_peca("CM", f"PLACAS PROTENDIDAS 125 × 15 — {N_TOT} PEÇAS · {len(TIPO)} TIPOS · 10 VISTAS · {f(PESO_TOT, 0)} t",
                      "locação das vistas; cada vista tem a sua prancha de produção e montagem (ND-LET-PP-A a PP-I); placa típica na ND-LET-PP00", largura=XC - Q[0] - 10)
    E = 200
    kp = pr.vista("LOCAÇÃO", (Q[0] + 160, Q[1] + 70), E, titulo="PLANTA DE LOCAÇÃO DAS PLACAS", subtitulo="letras = vistas do R01; pç = peças da vista", unidade="cm")
    for i, y in enumerate(Y_LIN):
        kp.linha((-3000, M(y)), (M(LARG) + 3000, M(y)), "EIXO"); kp.texto((-3500, M(y)), str(i + 1), "nota", "MIDDLE_RIGHT")
    for j, x in enumerate(X_FACH):
        kp.linha((M(x), -3000), (M(x), M(COMP) + 3000), "EIXO"); kp.texto((M(x), M(COMP) + 3300), "ABCDE"[j], "nota", "BOTTOM_CENTER")
    for y in Y_LIN:
        kp.ret(-300, M(y) - 200, 600, 400, "CORTADO"); kp.ret(M(LARG) - 300, M(y) - 200, 600, 400, "CORTADO")
    for x in X_FACH[1:-1]:
        for y in (Y_LIN[0], Y_LIN[1], Y_LIN[8]):
            kp.ret(M(x) - 200, M(y) - 300, 400, 600, "CORTADO")
    for x, b in zip(X_L4[1:-1], (400, 250, 400, 250, 400)):
        kp.ret(M(x) - b / 2, M(Y_LIN[3]) - b / 2, b, b, "CORTADO")
    kp.ret(M(19.75) - 300, M(54.575) - 300, 600, 600, "CORTADO")
    o = FOLGA
    xe0, xe1 = -300 - o - 150, -300 - o
    xd0, xd1 = M(LARG) + 300 + o, M(LARG) + 300 + o + 150
    for (a, b, oc) in ((FACE_Y[0], M(Y_LIN[1]), False), (M(Y_LIN[1]), M(Y_LIN[3]), True), (M(Y_LIN[3]), FACE_Y[1], False)):
        kp.ret(xe0, a, 150, b - a, "OCULTA" if oc else "CORTADO"); kp.ret(xd0, a, 150, b - a, "OCULTA" if oc else "CORTADO")
    kp.ret(FACE_X[0], FACE_Y[0] - o - 150, FACE_X[1] - FACE_X[0], 150, "CORTADO")                        # I
    kp.ret(FACE_X[0], FACE_Y[1] + o, FACE_X[1] - FACE_X[0], 150, "CORTADO")                              # A
    kp.ret(FACE_X[0], M(Y_LIN[1]) + 300 + o, FACE_X[1] - FACE_X[0], 150, "CORTADO")                     # G
    for b, (xa, xb) in enumerate(zip(X_L4[:-1], X_L4[1:])):
        if b in (1, 4):
            continue
        x0 = FACE_X[0] if b == 0 else M(xa)
        x1 = FACE_X[1] if b == 5 else M(xb)
        kp.ret(x0, M(Y_LIN[3]) - 200 - o - 150, x1 - x0, 150, "CORTADO")                                # C
    pos = {"A": (19.75, 82.8), "B": (-5.5, 54.5), "C": (19.75, 25.5), "D": (45.0, 54.5), "E": (-5.5, 19.7), "F": (45.0, 19.7),
           "G": (19.75, 13.5), "H": (-5.5, 4.8), "I": (19.75, -3.6), "J": (45.0, 4.8)}
    for V, (x, y) in pos.items():
        kp.circulo((M(x), M(y)), 1500, "INDICACAO")
        kp.texto((M(x), M(y) + 250), V, "titulo", "MIDDLE_CENTER")
        kp.texto((M(x), M(y) - 700), f"{len(DADOS[V][0])} pç", "min", "MIDDLE_CENTER")
    kp.texto((M(19.75), M(45)), "PAVILHÃO (fechado por B, D, A e C)", "nota", "MIDDLE_CENTER")
    kp.texto((M(19.75), M(19.7)), "laterais E e F abertas até +7,50", "min", "MIDDLE_CENTER")
    kp.texto((M(19.75), M(5.5)), "ANEXO / MEZANINO (H, J, I, G)", "nota", "MIDDLE_CENTER")
    for xp in (12.5, 27.0):
        kp.texto((M(xp), M(Y_LIN[3]) - 1300), "portão", "min", "MIDDLE_CENTER")
    kp.cota_h([M(x) for x in X_FACH], -5600, -4, total=False)
    kp.cota_h([FACE_X[0], FACE_X[1]], -5600, -11, total=False)
    kp.cota_v([M(y) for y in Y_LIN], M(LARG) + 7500, 4, total=False)
    kp.cota_v([FACE_Y[0], FACE_Y[1]], M(LARG) + 7500, 12, total=False)
    y = Q[3] - 40
    rows = []
    for i, V in enumerate(ORDEM_VISTAS, 1):
        pec = DADOS[V][0]
        folha = {"E": "PP-EF", "F": "PP-EF", "H": "PP-HJ", "J": "PP-HJ"}.get(V, f"PP-{V}")
        rows.append([i, V, VISTAS[V]["titulo"].split(" — ")[1].split(" (")[0], len(pec), f(sum(peso_t(p["L"]) for p in pec), 1), f"ND-LET-{folha}"])
    rows.append(["", "", "total", N_TOT, f(PESO_TOT, 1), ""])
    y = pr.tabela(XC, y, "ORDEM DE MONTAGEM DAS VISTAS", ["ORD.", "VISTA", "PAREDE", "PEÇAS", "PESO (t)", "PRANCHA"], rows, [10, 12, 82, 16, 20, 50], h_lin=5.5, destaque_ultima=True)
    tab = []
    for L in sorted(TIPOS, key=lambda L: -L):
        cont = {}
        for V, _ in TIPOS[L]:
            cont[V] = cont.get(V, 0) + 1
        tab.append([TIPO[L], f"{L/10:.1f}".replace(".", ","), len(TIPOS[L]), "  ".join(f"{V}: {n}" for V, n in sorted(cont.items()))])
    y = pr.tabela(XC, y - 4, "TIPOS × VISTAS", ["TIPO", "L (cm)", "QT", "VISTA: QUANTIDADE"], tab, [16, 22, 14, 138], h_lin=5.0)
    pr.notas(XC, y - 4, [
        "Geometria pela PLANTA BAIXA - LOCAÇÃO DE PILARES do R01: eixos A–E a 9,87 / 9,88 / 9,88 / 9,87 m; linhas 1–9 a 9,65 / 10,075 / 10,075 / 9,925 / 10,00 / 10,00 / 10,00 / 9,625 m (79,35 m entre eixos).",
        "Vistas como no R01: B e D (linhas 4–9) fechadas, 8 fiadas; E e F (linhas 2–4) só as 2 fiadas de cima; H, J (anexo) e I (fachada da linha 1) com faixas de esquadria de +1,25 a +2,50 e de +5,00 a +6,25 e porta na I; A (linha 9) fechada.",
        "PENDÊNCIA: paredes internas C (linha 4) e G (linha 2) com placas até +7,50; acima, as terças cruzam essas linhas (a partir de +8,37) e o trecho até a telha fica com fechamento leve — confirmar com o cliente.",
        "Linha 4: 2 portões (P9–P10 e P10–P12), livres até +7,50, sob a TS-01; o trecho P10–P11–P10 é fechado.",
        "Placas por fora dos pilares (folga 25 mm), juntas verticais de 10 mm no eixo dos pilares; nas pontas de canto até a face externa do pilar. Ligações e consolos CA-1: ND-LET-PP00.",
        "VT 25×60 (eixos A e E, linhas 2–9) de +7,50 a +8,10, atrás da fiada +7,50/+8,75: ND-LET-VT01.",
        "Cotas de concreto em cm, níveis em m. Não medir no desenho. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."], 190)
    avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-CM01")
    print("CM01", len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos", [a for a in avisos if a[0] == "ERRO" or "sobrep" in a[1]][:8])


# ================================================================== ND-LET-VT01 rev 02 — vigas de travamento
def prancha_vt():
    agr = {}
    for i in range(1, 8):
        agr.setdefault(round(Y_LIN[i + 1] - Y_LIN[i] - 0.40, 3), []).append(f"L{i+1}–L{i+2}")
    lista = sorted(agr.items(), key=lambda t: -t[0])
    MK = {L: f"VT-{k+1:02d}" for k, (L, _) in enumerate(lista)}
    peso = lambda L: 0.25 * 0.60 * L * 25
    pr = carimbo("ND-LET-VT01", "VIGAS DE TRAVAMENTO VT 25 × 60 (EIXOS A E E, +7,50 A +8,10, DENTES GERBER) — PLANTA, ELEVAÇÃO, SEÇÃO E APOIO", "01/01", rev="02")
    pr.revisao("01", "12/10/2026", "VT/VV A +6,25/+6,85 COM DENTES GERBER")
    pr.revisao("02", "12/10/2026", "GEOMETRIA DO R01; VT A +7,50/+8,10 ATRÁS DA FIADA +7,50; SEM VERGAS (PORTÕES SOB A TS-01)")
    Q = pr.quadro
    XC = Q[2] - 190
    pr.cabecalho_peca("VT", f"VIGA DE TRAVAMENTO 25 × 60 cm — L = {lista[-1][0]*100:.1f} A {lista[0][0]*100:.1f} cm — 14 PEÇAS".replace(".", ","),
                      "eixos A e E, linhas 2 a 9; fundo +7,50, topo +8,10; dentes Gerber 30 × 20 nos consolos CP-VT (assento +7,79); atrás da fiada de placas +7,50/+8,75", largura=XC - Q[0] - 10)
    v = pr.vista("PLANTA", (Q[0] + 50, Q[1] + 60), 400, titulo="PLANTA — VT (+7,50 / +8,10)", subtitulo="eixos A e E, linhas 2 a 9", unidade="cm")
    for i, y in enumerate(Y_LIN):
        v.linha((-1500, M(y)), (M(LARG) + 1500, M(y)), "EIXO"); v.texto((-2200, M(y)), str(i + 1), "min", "MIDDLE_RIGHT")
        v.ret(-300, M(y) - 200, 600, 400, "CORTADO"); v.ret(M(LARG) - 300, M(y) - 200, 600, 400, "CORTADO")
    for j, x in enumerate(X_FACH):
        v.linha((M(x), -1500), (M(x), M(COMP) + 1500), "EIXO"); v.texto((M(x), M(COMP) + 1800), "ABCDE"[j], "min", "BOTTOM_CENTER")
    for i in range(1, 8):
        L = round(Y_LIN[i + 1] - Y_LIN[i] - 0.40, 3)
        for xx in (0.0, LARG):
            v.ret(M(xx) - 125, M(Y_LIN[i]) + 200, 250, M(L), "VISTA")
        v.texto((1200, M((Y_LIN[i] + Y_LIN[i + 1]) / 2)), MK[L], "min", "MIDDLE_LEFT", rot=90)
    v.cota_v([M(y) for y in Y_LIN], M(LARG) + 1500, 6, total=False)
    v.cota_h([M(x) for x in X_FACH], -1500, -6, total=False)
    e = pr.vista("ELEVAÇÃO", (Q[0] + 75 - M(Y_LIN[1]) / 150, Q[3] - 140), 150, titulo="ELEVAÇÃO — EIXO A, LINHAS 2 A 9 (vista de dentro)", subtitulo="VT atrás das placas; linhas 2–4: placas só acima de +7,50", unidade="cm")
    for i in range(1, 9):
        e.ret(M(Y_LIN[i]) - 200, -500, 400, 10500, "CORTADO"); e.texto((M(Y_LIN[i]), 10250), f"L{i+1}", "min", "BOTTOM_CENTER")
    e.linha((M(Y_LIN[1]) - 1000, 0), (M(Y_LIN[8]) + 1000, 0), "TERRENO")
    for i in range(1, 8):
        L = round(Y_LIN[i + 1] - Y_LIN[i] - 0.40, 3)
        xi, Lm = M(Y_LIN[i]) + 225, M(L) - 50
        e.poli([(xi, Z_VT0 + 300), (xi + 200, Z_VT0 + 300), (xi + 200, Z_VT0), (xi + Lm - 200, Z_VT0), (xi + Lm - 200, Z_VT0 + 300), (xi + Lm, Z_VT0 + 300), (xi + Lm, Z_VT1), (xi, Z_VT1)], "VISTA", fechada=True)
        e.texto((M((Y_LIN[i] + Y_LIN[i + 1]) / 2), Z_VT1 + 250), MK[L], "min", "BOTTOM_CENTER")
        for z in range(7500 if i <= 2 else 0, 10000, H_PL):
            e.ret(M(Y_LIN[i]) + 5, z + 5, M(Y_LIN[i + 1] - Y_LIN[i]) - 10, H_PL - 10, "OCULTA")
    e.cota_h([M(y) for y in Y_LIN[1:]], -500, -8, total=False)
    e.cota_v([0, Z_VT0, Z_VT1, 8750, 10000], M(Y_LIN[8]) + 400, 8, total=False)
    e.chamada((M(Y_LIN[2]) + 3000, Z_VT1), (8, 24), "fiada de placas +7,50/+8,75 (por fora) esconde a VT")
    s = pr.vista("SEÇÃO", (Q[0] + 300, Q[1] + 60), 10, titulo="SEÇÃO VT", subtitulo="25 × 60, C40", unidade="cm")
    pts = [(0, 0), (250, 0), (250, 600), (0, 600)]
    s.poli(pts, "CORTADO", fechada=True); s.hachura(pts, "AR-CONC", 0.03)
    s.poli([(30, 30), (220, 30), (220, 570), (30, 570)], "ARM_TRANSV", fechada=True)
    for x in (45, 125, 205):
        s.ponto_barra((x, 45), 12.5); s.ponto_barra((x, 555), 12.5)
    for yy in (220, 380):
        s.ponto_barra((40, yy), 8); s.ponto_barra((210, yy), 8)
    s.cota_h([0, 250], 0, -8); s.cota_v([0, 600], 250, 8)
    s.chamada((205, 555), (12, 8), "N1/N2 — 3 Ø12,5 em cima e embaixo"); s.chamada((210, 380), (12, 0), "N3 pele 2 Ø8/face"); s.chamada((220, 300), (12, -10), "N4 Ø6,3 c/15")
    a = pr.vista("DETALHE 1", (Q[0] + 500, Q[1] + 75), 20, titulo="DETALHE 1 — DENTE GERBER DA VT NO CONSOLO CP-VT", subtitulo="dente 30 × 20; CP-VT + PN-1 Ø20; neoprene 200×150×10", unidade="cm")
    a.ret(-600, -500, 600, 1700, "VISTA")
    a.poli([(0, 0), (250, 0), (250, 100), (0, 300)], "VISTA")
    a.ret(125 - 10, 100, 20, 400, "OCULTA"); a.chapa(25, 300, 200, 10)
    a.poli([(25, 310), (225, 310), (225, 610), (1025, 610), (1025, 910), (25, 910)], "VISTA", fechada=True)
    a.interrupcao((1025, 610), (1025, 910))
    a.poli([(60, 370), (60, 340), (700, 340)], "ARMADURA"); a.poli([(260, 640), (260, 880)], "ARM_TRANSV"); a.poli([(340, 640), (340, 880)], "ARM_TRANSV")
    a.cota_h([-600, 0, 250, 1025], -500, -8, total=False); a.cota_v([0, 300, 610, 910], 1025, 8, total=False)
    a.chamada((100, 150), (14, -30), "CP-VT nas faces laterais dos pilares (assento +7,79)")
    a.chamada((125, 450), (14, 10), "PN-1 Ø20 no TB-1 Ø50 da viga"); a.chamada((-300, 1000), (-10, 8), "pilar")
    a.chamada((500, 340), (12, -22), "N5 tirante 2 Ø12,5 (NBR 9062:2017 7.4)"); a.chamada((300, 760), (12, 10), "N6 suspensão 2 estribos Ø8")
    y = Q[3] - 40
    linhas = [[MK[L], ", ".join(pos), 2 * len(pos), f"{L*100:.1f}".replace(".", ","), f(peso(L) / 9.81, 2)] for L, pos in lista]
    y = pr.tabela(XC, y, "MARCAS — VT 25×60 (eixos A e E)", ["MARCA", "TRECHO (linhas)", "QT", "L (cm)", "PESO (t)"], linhas, [18, 90, 12, 24, 26], h_lin=5.5)
    ins = [["TB-1", "Tubo Ø50×3,0 L=280 a prumo (no dente)", 2, "a 10 cm das pontas"], ["CH-A3", "Chapa 200×150×9,5 + 2 grapas Ø10", 2, "fundo das pontas"], ["AL-1", "Laço de cordoalha Ø12,7", 2, "a L/5 das pontas"]]
    y = pr.tabela(XC, y - 4, "INSERTOS POR VIGA — mm", ["MARCA", "DESCRIÇÃO", "QT", "POSIÇÃO"], ins, [16, 100, 10, 64])
    y = pr.legenda_armadura(XC, y - 4, False)
    pr.notas(XC, y - 4, ["Todas no mesmo nível: fundo +7,50, topo +8,10, atrás da fiada de placas +7,50/+8,75 (placa inteira por fora); dentes Gerber 30 × 20 nos consolos CP-VT dos pilares (assento +7,79).",
                         "Linha 4 sem verga: os portões ficam sob a TS-01 da linha 4, livres até +7,50.",
                         "Linhas 2–4 (vistas E e F) abertas até +7,50: a VT fica aparente por dentro e escondida por fora pela fiada +7,50.",
                         "Cotas de concreto em cm, níveis em m. Não medir no desenho. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."], 190)
    avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-VT01")
    print("VT01", len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos", [a for a in avisos if a[0] == "ERRO" or "sobrep" in a[1]][:8])


PRANCHAS_VISTA = [(["A"], "ND-LET-PP-A"), (["B"], "ND-LET-PP-B"), (["C"], "ND-LET-PP-C"), (["D"], "ND-LET-PP-D"), (["E", "F"], "ND-LET-PP-EF"),
                  (["G"], "ND-LET-PP-G"), (["H", "J"], "ND-LET-PP-HJ"), (["I"], "ND-LET-PP-I")]

if __name__ == "__main__":
    so = [a.lower() for a in sys.argv[1:]]
    if not so or "cm" in so:
        prancha_cm()
    if not so or "pp00" in so:
        prancha_tipo()
    if not so or "vt" in so:
        prancha_vt()
    for k, (Vs, des) in enumerate(PRANCHAS_VISTA, 1):
        if not so or des.split("-")[-1].lower() in so:
            prancha_vista(Vs, des, f"{k:02d}/{len(PRANCHAS_VISTA):02d}")
    print({V: len(DADOS[V][0]) for V in VISTAS}, "total", N_TOT, f"{PESO_TOT:.1f} t", {TIPO[L]: (L, len(v)) for L, v in TIPOS.items()})
