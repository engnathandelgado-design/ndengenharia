import math
"""Fechamento em placas protendidas 125 × 10 (rev03; antes 125 × 15) — conforme as VISTAS DO FECHAMENTO LATERAL do R01 (vistas A a J).

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
import geo_fixacao as GF
from geometria import X_FACH, Y_LIN, X_L4, LARG, COMP

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
PL = json.load(open(AQ + "placas.json"))
_PR = PL["protensao"]                                 # DEC-035: 10 fios Ø6 CP-175 RB (5 por face), z simétricos fora do nicho — tudo lido do placas.json
ZC_, DC_, NC_, EX_ = tuple(_PR["z_mm"]), _PR["diam_mm"], _PR["n"], _PR["eixo_face_mm"]
DCt_ = f"{DC_:g}".replace(".", ",")
CB_ = "fios" if _PR.get("aco") == "fio" else "cord."                 # DEC-035: fios Ø6 CP-175 RB
AC_ = "CP-175 RB" if _PR.get("aco") == "fio" else "CP-190 RB"
PRT_ = "fios" if _PR.get("aco") == "fio" else "cordoalhas"           # rev08: concordância (os fios … alinhados / as cordoalhas … alinhadas)
ALN_ = "alinhados" if _PR.get("aco") == "fio" else "alinhadas"
ADR_ = "aderentes"
CRT_ = "cortados" if _PR.get("aco") == "fio" else "cortadas"
SIG_PI_ = _PR.get("sig_pi_MPa", 1400)
EP_ = 200e3 if _PR.get("aco") == "fio" else 195e3                    # mesmo Ep da tabela de fios da PP00
ALONG_ = round(_PR["F_macaco_kN"] * 1e3 * 60e3 / (EP_ * _PR["Ap_mm2"] / _PR["n"]))
f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
M = lambda v: round(v * 1000)
H_PL, E_PL, JUNTA, FOLGA = 1250, 100, 20, 25           # rev04: junta vertical 20 mm (tex ±5 de projeto + tloc ±10 + Δ — NBR 9062:2017 3.1/5.2.2); mantida (Nathan 21/10/2026); 5 mm na altura
FX = json.load(open(AQ + "fixacao_placas.json"))        # rev06 (DEC-026): sistema Trejor — console soldado CS-1 + nicho NC-1 + pino PT-1
NC_B, NC_H, NC_P, Z_NC = GF.N["B"], GF.N["H"], GF.N["P"], 940   # rev06e: geometria do GEO (DEC-031: nicho 140)              # nicho NC-1: comprimento a partir da ponta, altura, profundidade, centro acima da base da placa
X_CS = NC_B / 2                                         # eixo do console = eixo do nicho, a partir da ponta da placa (70)
CE_B, CE_H, Z_CE = 380, 330, 922                        # CE-1 no pilar: largura, altura, centro acima da base da fiada
# DEC-044 (22/10): o I130 do eixo C atravessa as paredes internas G (linha 2) e C (linha 4) — consolo CP-I130 (50 × 40) e nariz do dente
# entram 24 / 19 cm na placa de cima dessas paredes. Recorte na ponta do eixo C das 4 placas da fiada +6,25 (PP-xxR): b = 260 mm desde
# a ponta (consolo 240 + folga 20), de z0 = 160 mm acima da base (fundo do consolo 226 − janela 40 − folga ≥ 20; abaixo do fio de 156: os 10 fios param na face do recorte) até o topo.
# O console CS-1 dessa ponta passa para 330 mm da ponta (nicho NC-1 de 260 a 400) e cai fora da CE-1 do pilar: CE-1L (840 × 330).
REC_B, REC_Z0, X_CS_R = 260, 120, 260 + X_CS
CE1L_B = 840
REC_VISTAS = ("G", "C")
# DEC-044: calço entre a CE-1 e o CS-1 onde a face do pilar fica atrás do plano dos consoles — 100 mm nos cantos (vistas A e I) e nos
# P1B/P2B da vista G (40 ⊥ à parede, contra 60 dos PF) e 75 mm nos P10 da vista C (25 ⊥ à parede). Marcas CS-1C (100) e CS-1D (75).
CALCO = {("I", 0): 100, ("I", 4): 100, ("A", 0): 100, ("A", 4): 100, ("G", 0): 100, ("G", 4): 100, ("C", 2): 75, ("C", 4): 75}
CALCO_MARCA = {100: "CS-1C", 75: "CS-1D"}
X_PT = lambda L: round(0.21 * L + 150)                  # pinos PT-1: 15 cm para dentro de cada alça AL-P
Z_TOPO = 10000
Z_VT0, Z_VT1, Z_ASS_VT = 7500, 8100, 7790              # VT 25×60 do eixo E atrás da fiada +7,50/+8,75; dente 30×20 → assento do CP-VT
Z_VT_A = (6250, 6850, 6540)                             # rev03: VT do eixo A rebaixada (CP-VT abaixo do recuo +7,19), atrás da fiada +6,25/+7,50
VT_LADO = {"A": Z_VT_A, "E": (Z_VT0, Z_VT1, Z_ASS_VT)}
PP_KNM = PL["secao"]["pp_kNm"]
FIADAS = list(range(8))
ESQ = (1, 4)                                            # fiadas sem placa (faixas de esquadria) nas vistas H, J e I
PORTA_I = (M(23.79), M(25.59))                          # porta da vista I (fiada 1, vão C–D) — R01: 1,80 m (a confirmar)
# rev09c (DEC-053, 24/10): porta do 2º pavimento na fachada A do anexo (vista H) para a escada externa — arquitetônico 90 × 214,
# y 0,89 a 1,79, piso +3,90 (topo +6,04): corta só a fiada 3 (+3,75/+5,00); a de cima (+5,00/+6,25) já é faixa de esquadria.
# As pontas das placas da fiada 3 junto ao vão apoiam em ombreiras metálicas OM-2 INTERNAS (U 152, do piso do térreo a +5,00, por
# trás das fiadas 0 e 2, travadas no P28) — nenhuma placa apoia em outra.
PORTA_H = (890, 1790)
J_OM = 20                                               # rev06d (DEC-028): ponta da placa a 20 mm do vão da porta (alma da ombreira OM-1 em U + junta)
OMB = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/ombreira.json"))
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
              fiadas=lambda k, b: True),
    "C": dict(titulo="VISTA C — PAREDE INTERNA DA LINHA 4 (PORTÕES)",
              pil=eixos_transv(X_L4, ["A", "", "", "C", "", "", "E"], [600, 400, 250, 400, 250, 400, 600]), ini=FACE_X[0], fim=FACE_X[1],
              fiadas=lambda k, b: k <= (4 if b == 0 else 5), portoes=[1, 4], nomes_pil=["P1", "P9", "P10", "P11", "P10", "P12", "P2"]),
    "D": dict(titulo="VISTA D — LATERAL DO EIXO E, LINHAS 4 A 9 (vista de fora)", pil=eixos_lat(3, 8), ini=M(Y_LIN[3]) + JUNTA // 2, fim=FACE_Y[1],
              fiadas=lambda k, b: True),
    "E": dict(titulo="VISTA E — LATERAL DO EIXO A, LINHAS 2 A 4 (aberta até +7,50)", pil=eixos_lat(1, 3), ini=M(Y_LIN[1]) + JUNTA // 2, fim=M(Y_LIN[3]) - JUNTA // 2,
              fiadas=lambda k, b: k >= 6),
    "F": dict(titulo="VISTA F — LATERAL DO EIXO E, LINHAS 2 A 4 (aberta até +7,50)", pil=eixos_lat(1, 3), ini=M(Y_LIN[1]) + JUNTA // 2, fim=M(Y_LIN[3]) - JUNTA // 2,
              fiadas=lambda k, b: k >= 6),
    "G": dict(titulo="VISTA G — PAREDE INTERNA DA LINHA 2 (face do pavilhão)", pil=TRANSV, ini=FACE_X[0], fim=FACE_X[1],
              fiadas=lambda k, b: k <= (4 if b == 0 else 5), nomes_pil=["P1B", "P8", "P8A", "P8B", "P2B"]),
    "H": dict(titulo="VISTA H — LATERAL DO ANEXO, EIXO A, LINHAS 1 A 2", pil=eixos_lat(0, 1), ini=FACE_Y[0], fim=M(Y_LIN[1]) - JUNTA // 2,
              fiadas=lambda k, b: k not in ESQ, esquadria=True, porta=(0, 3, PORTA_H)),
    "I": dict(titulo="VISTA I — FACHADA DA LINHA 1 (anexo, vista de fora)", pil=TRANSV, ini=FACE_X[0], fim=FACE_X[1],
              fiadas=lambda k, b: k not in ESQ, esquadria=True, porta=(2, 0, PORTA_I), nomes_pil=["P1A", "P3", "P4", "P5", "P2A"]),
    "J": dict(titulo="VISTA J — LATERAL DO ANEXO, EIXO E, LINHAS 1 A 2", pil=eixos_lat(0, 1), ini=FACE_Y[0], fim=M(Y_LIN[1]) - JUNTA // 2,
              fiadas=lambda k, b: k not in ESQ, esquadria=True),
}
ORDEM_VISTAS = ["C", "G", "I", "H", "J", "E", "F", "B", "D", "A"]      # rev08 (MON03): internas C e G antes da viga de cobertura da própria linha (TS-01 / W 310); depois as externas


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
            abert.append((sa + ba // 2, sb - bb // 2, 0, 7500, "portão"))          # DEC-059: livres até +7,50 (PG apoiam a TS-01A)
            continue
        ks = [k for k in FIADAS if d["fiadas"](k, b)]
        if d.get("esquadria"):
            for k in ESQ:
                abert.append((s0, s1, k * H_PL, (k + 1) * H_PL, "esquadria"))
        for k in ks:
            z0 = k * H_PL
            apoio = "2 consoles CS-1"                                # rev06: cada placa no seu console (folga de 5 mm na junta)
            trechos = [(s0, s1)]
            if d.get("porta") and d["porta"][0] == b and d["porta"][1] == k:
                p0, p1 = d["porta"][2]
                trechos = [(s0, p0 - J_OM), (p1 + J_OM, s1)]
                abert.append((p0, p1, 0, 2 * H_PL, "porta") if k == 0 else (p0, p1, k * H_PL, (k + 1) * H_PL, "porta"))
            x_c = next((s for s, _, nm in pil if nm == "C"), None)
            for (t0, t1) in trechos:
                n += 1
                ap = apoio if (t0 == s0 and t1 == s1) else ("CS-1 + baldrame + OM-1" if d["porta"][1] == 0 else "CS-1 + console da OM-2 (ombreira interna)")
                esp = bool(d.get("porta") and d["porta"][0] == b and d["porta"][1] == 0 and k == 2)     # placa sobre a porta (PP-05P): recebe o topo das 2 OM-1; mesma protensão da típica (DEC-035) + 2 buchas BR-1
                if esp:
                    ap = "2 CS-1 + topo das 2 OM-1"
                # DEC-044: recorte na ponta do eixo C da fiada +6,25 das paredes internas (I130 + CP-I130 atravessam a parede)
                rec = None
                if V in REC_VISTAS and k == 5 and x_c is not None:
                    rec = "s1" if abs(t1 - x_c) <= JUNTA else "s0" if abs(t0 - x_c) <= JUNTA else None
                xcs = (X_CS_R if rec == "s0" else X_CS, X_CS_R if rec == "s1" else X_CS)     # eixo do console a partir de cada ponta
                if rec:
                    ap = "2 CS-1 (ponta recortada: CS-1 na CE-1L)"
                cont = all(j in ks for j in range(k))                       # pano contínuo até o baldrame → pinos PT-1; senão trava de pé PT-2
                trava = "PT-1" if cont else "PT-2"
                pt2 = [] if cont else [(sa + ba / 2 + 51, z0 + 150), (sb - bb / 2 - 51, z0 + 150)]
                calco = (CALCO.get((V, b), 0) if t0 == s0 else 0, CALCO.get((V, b + 1), 0) if t1 == s1 else 0)   # DEC-044: calço do CS-1 em cada ponta
                pecas.append(dict(id=f"{V}-{n:02d}", seq=n, bay=b, k=k, s0=t0, s1=t1, z0=z0, z1=z0 + H_PL, L=t1 - t0, Lk=(t1 - t0) + (0.1 if esp else 0.2 if rec == "s0" else 0.3 if rec == "s1" else 0), especial=esp,
                                  apoio=ap + (" + 2 PT-1 (guia)" if cont else " + 2 PT-2 (pé)"), trava=trava, pt2=pt2, rec=rec, xcs=xcs, calco=calco))
                ca1 += [(t + sg * xo, z0 + Z_NC) for t, sg, xo, ok in ((t0, 1, xcs[0], t0 == s0), (t1, -1, xcs[1], t1 == s1)) if ok]   # consoles CS-1 (só nas pontas sobre pilar)
    return pecas, ca1, abert


def poligono_placa(p):
    """contorno da placa (mm, no plano da vista): retângulo, ou L com o recorte do DEC-044 na ponta do eixo C."""
    s0, s1, z0, z1 = p["s0"], p["s1"], p["z0"] + JUNTA / 2, p["z1"] - JUNTA / 2
    if p.get("rec") == "s1":
        return [(s0, z0), (s1, z0), (s1, p["z0"] + REC_Z0), (s1 - REC_B, p["z0"] + REC_Z0), (s1 - REC_B, z1), (s0, z1)]
    if p.get("rec") == "s0":
        return [(s0, z0), (s1, z0), (s1, z1), (s0 + REC_B, z1), (s0 + REC_B, p["z0"] + REC_Z0), (s0, p["z0"] + REC_Z0)]
    return [(s0, z0), (s1, z0), (s1, z1), (s0, z1)]


DADOS = {V: montar(V) for V in VISTAS}
TIPOS = {}
for V, (pecas, _, _) in DADOS.items():
    for p in pecas:
        TIPOS.setdefault(p["Lk"], []).append((V, p["id"]))
_FIXA = [10160, 10055, 9980, 9905, 9860, 9840, 9815, 4535, 4010]   # rev09c: marcas já emitidas não mudam; placas novas (porta da vista H) entram no fim
_INT = [L for L in _FIXA if L in TIPOS] + sorted([L for L in TIPOS if L == int(L) and L not in _FIXA], key=lambda L: -L)
TIPO = {L: f"PP-{_FIXA.index(L) + 1 if L in _FIXA else len(_FIXA) + 1 + [x for x in _INT if x not in _FIXA].index(L):02d}" for L in _INT}
for _L in sorted([L for L in TIPOS if L != int(L)]):        # rev06d: variante PP-05P (placa sobre a porta da vista I) — rev08: mesma protensão, só as buchas BR-1
    _suf = {1: "P", 2: "RE", 3: "RD"}[round((_L - int(_L)) * 10)]   # DEC-044: RE/RD = recorte na ponta esquerda/direita (na elevação da vista) — não são a mesma peça virada (face interna)
    if int(_L) not in TIPO:
        TIPO[int(_L)] = f"PP-{len([t for t in TIPO.values() if t[-1].isdigit()]) + 1:02d}"
    TIPO[_L] = TIPO[int(_L)] + _suf
RECORTADAS = [(V, p) for V, (pecas, _, _) in DADOS.items() for p in pecas if p.get("rec")]
CALCOS = {}                                                  # DEC-044: (marca do calço) → [(vista, bay do pilar, k)]
for V, (pecas, _, _) in DADOS.items():
    for p in pecas:
        for j, c_ in enumerate(p["calco"]):
            if c_:
                CALCOS.setdefault(CALCO_MARCA[c_], []).append((V, p["bay"] + j, p["k"]))
N_TOT = sum(len(v) for v in TIPOS.values())
REC_T = PP_KNM * REC_B / 1000 * (H_PL - REC_Z0) / H_PL / 9.81          # DEC-044: peso do recorte (t)
peso_t = lambda L: PP_KNM * int(L) / 1000 / 9.81 - (REC_T if round((L - int(L)) * 10) in (2, 3) else 0)
PESO_TOT = sum(len(v) * peso_t(L) for L, v in TIPOS.items())


def carimbo(desenho, conteudo, folha, rev="00", fmt="A1"):
    return Prancha(fmt, dict(cliente=CLIENTE, obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR", conteudo=conteudo,
                             desenho=desenho, folha=folha, fase="PARA APROVAÇÃO", rev=rev))


# ================================================================== elevação de uma vista
# rev10 (Nathan 25/10/2026): cada parede (vista) com uma cor própria — mesma cor nas elevações PP-x, na planta da CM01 e no
# isométrico (iso_fachadas.py), hachura sólida com transparência de 60 %
COR_VISTA = {"A": (31, 119, 180), "B": (255, 127, 14), "C": (44, 160, 44), "D": (214, 39, 40), "E": (148, 103, 189),
             "F": (140, 86, 75), "G": (227, 119, 194), "H": (23, 190, 207), "I": (188, 189, 34), "J": (127, 127, 127)}


def hachura_cor(vv, pts, V, transp=0.6):
    h = vv.pr.msp.add_hatch(dxfattribs={"layer": "COR_FACHADA"})
    h.set_solid_fill(rgb=COR_VISTA[V])
    h.transparency = transp
    h.paths.add_polyline_path([vv.P(p) for p in pts], is_closed=True)
    return vv._add(h)


def desenhar_elev(pr, V, origem, esc):
    d = VISTAS[V]
    pecas, ca1, abert = DADOS[V]
    vv = pr.vista(f"VISTA {V}", origem, esc, titulo=d["titulo"], subtitulo="peças numeradas na ordem de produção e montagem (vão a vão, de baixo para cima)", unidade="cm")
    nomes = d.get("nomes_pil")
    for i, (s, b, _) in enumerate(d["pil"]):
        zt = Z_TOPO
        if nomes and nomes[i] in ("P9", "P10", "P12"):                # rev06: cabeça a 2 cm do fundo da TS-01 (ligação em y)
            _lg = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/ligacoes.json"))
            zt = round((_lg["Z0_TS"] + 0.03 * s / 1000) * 1000 - 20)
        vv.ret(s - b / 2, -500, b, zt + 500, "OCULTA")
        if nomes:
            vv.texto((s, zt + 200), nomes[i], "min", "BOTTOM_CENTER")
    vv.linha((d["ini"] - 800, 0), (d["fim"] + 800, 0), "TERRENO")
    vv.ret(d["ini"], -500, d["fim"] - d["ini"], 500, "VISTA")                                     # viga baldrame (fundação)
    if d.get("vt"):
        z0v, z1v, _ = d["vt"]
        for (sa, ba, _), (sb, bb, _) in zip(d["pil"][:-1], d["pil"][1:]):
            vv.ret(sa + ba / 2 + 25, z0v, sb - sa - (ba + bb) / 2 - 50, z1v - z0v, "OCULTA")
    for (a0, a1, z0, z1, rot) in abert:
        pts = [(a0, z0), (a1, z0), (a1, z1), (a0, z1)]
        vv.hachura(pts, "ANSI37", 3.0, "HACHURA")
        vv.poli(pts, "EIXO", fechada=True)
        vv.texto(((a0 + a1) / 2, z0 + (z1 - z0) * (0.3 if rot == "porta" else 0.5)), {"portão": "PORTÃO 500 × 750 — livre até +7,50", "porta": "PORTA", "esquadria": "esquadria"}[rot], "min", "MIDDLE_CENTER")
        if rot == "porta" and z0 == 0:                                              # rev06d: ombreiras OM-1 em U nos 2 lados (ND-LET-PP05)
            for xa in (a0 - 20, a1):
                vv.ret(xa, 12, 20, z1 - 22, "METALICA")
            vv.chamada((a0 - 10, z1 * 0.55), (-10, 6), "OM-1 (PP05)")
        elif rot == "porta":                                                        # rev09c: ombreiras OM-2 internas (atrás das placas), do piso a +5,00
            for xa in (a0 - 20 - 48, a1 + 20):
                vv.ret(xa, 0, 48, z1, "OCULTA")
            vv.chamada((a0 - 44, z0 - 1900), (10, -4), "OM-2 interna (ES02)")
    for p in pecas:
        hachura_cor(vv, poligono_placa(p), V)
        vv.poli(poligono_placa(p), "VISTA", fechada=True)
        if p.get("rec"):
            xr = p["s1"] - REC_B if p["rec"] == "s1" else p["s0"] + REC_B
            vv.chamada((xr, p["z0"] + REC_Z0 + 400), (-6 if p["rec"] == "s1" else 6, 8), f"recorte {REC_B / 10:g} × {(H_PL - REC_Z0) / 10:g} — PP06")
        vv.texto(((p["s0"] + p["s1"]) / 2, p["z0"] + H_PL * 0.6), p["id"], "nota", "MIDDLE_CENTER")
        vv.texto(((p["s0"] + p["s1"]) / 2, p["z0"] + H_PL * 0.22), TIPO[p["Lk"]], "min", "MIDDLE_CENTER")
    if V == "C":                                                                    # DEC-059: placa PV-1 sobre o portão P19–D (ND-LET-PV01)
        _pj = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/portao_l4.json"))
        s0v, s1v = d["pil"][4][0] + JUNTA // 2, d["pil"][5][0] - JUNTA // 2
        z0v, z1v = round(_pj["placa_P19_D"]["z0"] * 1000) + 5, round(_pj["placa_P19_D"]["z1"] * 1000)
        vv.poli([(s0v, z0v), (s1v, z0v), (s1v, z1v), (s0v, z1v)], "VISTA", fechada=True)
        vv.chamada(((s0v + s1v) / 2, (z0v + z1v) / 2), (6, 10), "PV-1 10 × 37 sobre o portão (ND-LET-PV01)")
    for (s, z) in ca1:                                                              # rev06: nichos NC-1 / consoles CS-1 (atrás da placa)
        vv.ret(s - NC_B / 2, z - NC_H / 2, NC_B, NC_H, "OCULTA")
    for p in pecas:                                                                 # pinos PT-1 na junta de baixo / travas PT-2 no pé
        if p["trava"] == "PT-1":
            for xp in (p["s0"] + X_PT(p["L"]), p["s1"] - X_PT(p["L"])):
                vv.circulo((xp, p["z0"]), 45, "OCULTA")
        for (xp, zp) in p["pt2"]:
            vv.ret(xp - 51, zp - 75, 102, 150, "OCULTA")
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
    """Corte vertical típico da parede da vista: placas, baldrame, CE-1 + CS-1 + NC-1 em cada fiada, PT-1 nas juntas (rev06)."""
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
        zt = z0 + Z_NC + NC_H / 2 - 12.5 - 50                                                      # topo do braço do CS-1
        c.chapa(0, z0 + Z_CE - CE_H / 2, 16, CE_H, 3.0)                                             # CE-1 (embutida no pilar)
        c.chapa(-16, zt + GF.C["costas"]["z0"], 16, GF.C["costas"]["z1"] - GF.C["costas"]["z0"], 3.0)                                                        # CS-1: costas soldadas na CE-1
        c.chapa(-64, zt - 80, 48, 80, 3.0)                                                      # CS-1: braço dentro do nicho
        c.ret(-FOLGA - NC_P, z0 + Z_NC - NC_H / 2, NC_P, NC_H, "METALICA")                          # NC-1 nicho na face interna da placa
        tv = next((p_["trava"] for p_ in pecas if p_["bay"] == pecas[0]["bay"] and p_["k"] == k), "PT-1")
        if tv == "PT-1":
            c.chapa(-FOLGA - 6.3, z0 - 40, 6.3, 80, 3.0)                                            # PT-1 na junta de baixo
        else:
            c.chapa(-FOLGA, z0 + 100, FOLGA + 9.5, 100, 3.0)                                        # PT-2 no pé (ao lado do pilar)
    if d.get("vt"):
        c.ret(175, d["vt"][0], 250, d["vt"][1] - d["vt"][0], "OCULTA")
        c.chamada((300, Z_VT1), (10, 8), "VT 25×60 entre os pilares (atrás)")
    c.cota_v([k * H_PL for k in range(0, 9)], -FOLGA - E_PL, -10, total=False)
    c.cota_h([-FOLGA - E_PL, 600], -500, -8, total=False)
    c.cota_h([0, 600], -500, -16, total=False)
    k0 = ks[-1]
    c.chamada((-FOLGA - E_PL / 2, k0 * H_PL + 600), (-14, 8), "placa 125 × 10 + folga 2,5")
    c.chamada((-40, k0 * H_PL + Z_NC), (16, 10), "console CS-1 na CE-1 do pilar (CC-1 concretado na face C ou soldado na obra nas laterais) + nicho NC-1 da placa (PP00, det. 2 e 4)")
    tv0 = next(p_["trava"] for p_ in pecas if p_["bay"] == pecas[0]["bay"] and p_["k"] == k0)
    c.chamada((-FOLGA - 3, k0 * H_PL + (150 if tv0 == "PT-2" else 0)), (16, -12), "PT-1 pino guia de montagem (PP00, det. 3)" if tv0 == "PT-1" else "PT-2 trava de pé nos pilares (PP00, det. 6)")
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
        hachura_cor(k, [(min(a[0], b[0]) - (0 if horiz else 600), min(a[1], b[1]) - (600 if horiz else 0)), (max(a[0], b[0]) + (0 if horiz else 600), min(a[1], b[1]) - (600 if horiz else 0)),
                        (max(a[0], b[0]) + (0 if horiz else 600), max(a[1], b[1]) + (600 if horiz else 0)), (min(a[0], b[0]) - (0 if horiz else 600), max(a[1], b[1]) + (600 if horiz else 0))], V, 0.0)
        cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        off = (0, 5600) if horiz and a[1] > 40000 else (0, -3500) if horiz and a[1] < 1000 else (M(4.94), 3000) if horiz else (-5600, 0) if a[0] < 0 else (3500, 0)
        k.circulo((cx + off[0], cy + off[1]), 1800, "INDICACAO")
        k.texto((cx + off[0], cy + off[1]), V, "nota", "MIDDLE_CENTER")
    return k


# ================================================================== prancha de produção/montagem por vista
def prancha_vista(Vs, desenho, folha):
    lista = [p for V in Vs for p in DADOS[V][0]]
    nome = " E ".join(Vs)
    pr = carimbo(desenho, f"PLACAS DE FECHAMENTO PROTENDIDAS — VISTA{'S' if len(Vs) > 1 else ''} {nome}: PRODUÇÃO E MONTAGEM EM SEQUÊNCIA", folha)
    pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL — CONFORME AS VISTAS DO FECHAMENTO DO R01")
    pr.revisao("03", "14/10/2026", "PLACA 125 × 10 (8 Ø12,7); LIGAÇÕES PARAFUSADAS (TRILHO + BUCHA), SEM SOLDA; VT DO EIXO A A +6,25")
    pr.revisao("04", "16/10/2026", "NBR 9062: SEM VT; JUNTA VERTICAL 20 mm")
    pr.revisao("06", "17/10/2026", "FIXAÇÃO TREJOR: CONSOLE CS-1 (CC-1 NA FACE C OU NA CE-1) + NICHO NC-1 + 2 PINOS PT-1")
    if "C" in Vs:
        pr.revisao("10", "24/10/2026", "DEC-059: PORTÕES LIVRES ATÉ +7,50 (PG APOIAM A TS-01A); PLACA PV-1 SOBRE O PORTÃO PG-04–PG-03")
    Q = pr.quadro
    XC = Q[2] - 190
    pesos = sum(peso_t(p["Lk"]) for p in lista)
    pr.cabecalho_peca(f"VISTA {nome}", f"PLACAS PROTENDIDAS 125 × 10 — {len(lista)} PEÇAS — {f(pesos, 1)} t",
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
    rows = [[p["seq"], p["id"], TIPO[p["Lk"]], f"{p['L']/10:.1f}".replace(".", ","), f"+{f(p['z0']/1000, 2)}", f(peso_t(p["Lk"]), 2), p["apoio"]] for p in lista]
    h = 4.4 if len(rows) > 32 else 5.0
    y = pr.tabela(XC, y, "LISTA DE PRODUÇÃO E MONTAGEM (na ordem)", ["SEQ", "PEÇA", "TIPO", "L (cm)", "BASE", "PESO (t)", "APOIO DA PEÇA"],
                  rows, [10, 18, 18, 18, 18, 18, 90], h_lin=h)
    res = {}
    for p in lista:
        res.setdefault(TIPO[p["Lk"]], [0, p["Lk"]])[0] += 1
    rr = [[t, f"{int(L)/10:.1f}".replace(".", ","), n_, f(n_ * peso_t(L), 1)] for t, (n_, L) in sorted(res.items())]
    rr.append(["", "total", len(lista), f(pesos, 1)])
    y = pr.tabela(XC, y - 4, "RESUMO POR TIPO", ["TIPO", "L (cm)", "QT", "PESO (t)"], rr, [40, 50, 30, 70], h_lin=5.0, destaque_ultima=True)
    n_ca = sum(len(DADOS[V][1]) for V in Vs)
    n_cc = sum(1 for V in Vs for (x, z) in DADOS[V][1] if GF.concretado(V, min(VISTAS[V]["pil"], key=lambda p: abs(p[0] - x))[1]))
    notas = [f"Produzir na ordem da coluna SEQ e etiquetar cada peça com o código (ex.: {lista[0]['id']}) e o tipo; estocar por vista, na ordem inversa da montagem.",
             f"Montagem vão a vão, de baixo para cima. Consoles da face C dos pilares: já vêm concretados com o pilar (CC-1, DEC-031). Consoles das faces laterais e das paredes internas: antes da placa, soldar o CS-1 na CE-1 no nível marcado pela topografia. A placa encosta no pilar com o braço do console entrando no nicho NC-1 de cada ponta e desce até o teto do nicho apoiar no parafuso de nível M16 (G {GF.T['G']:g} ± {GF.T['G_tol']:g} mm); afastamento {GF.T['a']:g} ± {GF.T['a_tol']:g} mm pelo parafuso frontal M16. Cada placa leva só o próprio peso: folga de 5 mm na junta macho-fêmea. Pinos guia PT-1: parafusados só no topo da placa de baixo; a placa de cima desce guiada, sem parafuso (não transmitem esforço — DEC-035). Nas placas de pacote suspenso, apertar as 2 travas PT-2 no pé antes de soltar o guindaste (PP00, det. 2 a 6).",
             f"Placa protendida 125 × 10, C{PL['secao']['fck']:.0f}, {NC_} {CB_} Ø{DCt_} {AC_} {ALN_} ({NC_ // 2} por face, cobrimento 2,0), {f(PL['protensao']['F_macaco_kN'])} kN por {"fio" if _PR.get("aco") == "fio" else "cordoalha"} no macaco: seção, insertos, alças e ligações na ND-LET-PP00."]
    if n_ca:
        notas.append(f"Consoles CS-1 nesta prancha: {n_ca} (tracejado na elevação = nicho NC-1 atrás da placa; círculo tracejado = pino PT-1 na junta de baixo; retângulo tracejado no pé = trava PT-2 nos pilares, nas placas sem pano contínuo até o baldrame). Consoles concretados (CC-1, face C) nesta prancha: {n_cc}; soldados na obra (faces laterais): {n_ca - n_cc} — filete {FX['solda']['filete_mm']:g} mm E70XX nos 2 lados verticais, inspeção visual 100 %, galvanização a frio.")
    if "C" in Vs:
        notas.append("Placas até +7,50 (vão A–P9 até +6,25: a TS-01 desce até +7,19 junto ao eixo A); acima, até a telha, fechamento metálico leve na face da TS-01. Portões P9–P10 e P10–P12 (500 × 750) livres até +7,50 (DEC-059): os PG-01 a PG-04 apoiam a TS-01A (neoprene + graute depois da montagem) e a viga não desce no vão; sobre o portão entre o PG-04 e o PG-03, placa PV-1 de 10 × 37 (+7,50 a +7,88) apoiada nas cantoneiras CL-V dos PG (ND-LET-PV01).")
    if "G" in Vs:
        notas.append("Placas na face do pavilhão (a laje do mezanino passa na face do anexo), até +7,50 (vão A–B até +6,25, mantido do rev08 por conservadorismo); acima, fechamento metálico leve até a telha, fixado na W 310 da linha 2 (rev09, DEC-048: sem TS-01 nesta linha, ND-LET-COB05).")
    if any(V in Vs for V in ("H", "J", "I")):
        notas.append("Faixas hachuradas: esquadrias do anexo (R01), sem placa, de +1,25 a +2,50 e de +5,00 a +6,25; toda placa fica nos seus 2 consoles CS-1, também acima das faixas." + (" Porta: 180 × 250 (a confirmar); as placas ao lado da porta têm console só na ponta do pilar e apoiam no baldrame / na placa de baixo do lado da porta." if "I" in Vs else ""))
    if any(V in Vs for V in ("E", "F")):
        notas.append("E (eixo A) e F (eixo E): abertas até +7,50; as 2 fiadas de cima ficam nos seus consoles CS-1 e vencem o vão entre os pilares; cada uma trava no pé com 2 PT-2 nos pilares (sem vigas de travamento — não há ponte rolante; NBR 9062:2017 5.1.2.1).")
    recs = [p for p in lista if p.get("rec")]
    if recs:
        notas.append(f"DEC-044 — {', '.join(p['id'] for p in recs)} ({', '.join(sorted(set(TIPO[p['Lk']] for p in recs)))}): recorte de {REC_B / 10:g} × {(H_PL - REC_Z0) / 10:g} cm na ponta do eixo C (o consolo CP-I130 e o nariz do I130 atravessam a parede); o console CS-1 dessa ponta fica a {X_CS_R / 10:g} cm da ponta, numa CE-1L (840 × 330) no pilar P11 — fôrma, armação e CE-1L na ND-LET-PP06.")
    calcs = sorted(set(CALCO_MARCA[c_] for p in lista for c_ in p["calco"] if c_))
    if calcs:
        n_cal = {m_: sum(1 for p in lista for c_ in p["calco"] if c_ and CALCO_MARCA[c_] == m_) for m_ in calcs}
        notas.append("DEC-044 — " + "; ".join(f"{m_} ({n_cal[m_]} nesta prancha): CS-1 com calço de {k_} mm, soldado na fábrica, nos pilares cuja face fica {k_} mm atrás do plano dos consoles" for k_, m_ in CALCO_MARCA.items() if m_ in calcs) + " (" + ", ".join(sorted(set(VISTAS[V]["nomes_pil"][b_] for V in Vs for p in DADOS[V][0] for j, c_ in enumerate(p["calco"]) if c_ for b_ in [p["bay"] + j] if VISTAS[V].get("nomes_pil")))) + ") — ND-LET-PP06.")
    notas.append("Cotas de concreto em cm, níveis em m. Não medir no desenho.")
    pr.notas(XC, y - 4, notas, 190)
    avisos = pr.salvar(f"/home/claude/letsara/pranchas/{desenho}")
    print(desenho, len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos", [a for a in avisos if a[0] == "ERRO" or "sobrep" in a[1]][:6])


# ================================================================== ND-LET-PP00 — placa típica
TELA_PL = 2 * 2 * 0.60 * 1.19                      # N1: tela Q92 nas 2 faces, 60 cm em cada ponta (m²/placa)
KG_DENTE = json.load(open("/home/claude/letsara/pranchas/pp01.json"))["kg_ponta_por_placa"] / 1.10   # rev06b: N3–N7 das 2 pontas (ND-LET-PP01, sem perdas)


def prancha_tipo():
    P = PL
    pr = carimbo("ND-LET-PP00", "PLACA DE FECHAMENTO PROTENDIDA 125 × 10 — FÔRMA (INSERTOS, ALÇAS, LIGAÇÕES) E ARMAÇÃO (PROTENSÃO, ARMADURA PASSIVA) — TIPOS PP-01 A PP-09", "01/01", fmt="A0")
    pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL")
    pr.revisao("03", "14/10/2026", "PLACA 10 cm, 8 Ø12,7 ALINHADAS (COB. 2,0); LIGAÇÕES PARAFUSADAS SEM SOLDA")
    pr.revisao("04", "16/10/2026", "NBR 9062: JUNTA 20 mm, TOLERÂNCIAS, ESTABILIDADE NO IÇAMENTO")
    pr.revisao("06", "17/10/2026", "FIXAÇÃO TREJOR: NICHO NC-1 NAS PONTAS, CONSOLE CS-1, PINOS PT-1, TRAVA PT-2; ARMADURA DO DENTE")
    pr.revisao("07", "21/10/2026", "FÔRMA E ARMAÇÃO NA MESMA FOLHA (PADRÃO USINA)")
    Q = pr.quadro
    XC = Q[2] - 190
    Ls = sorted(TIPOS)
    Y_SPLIT = Q[1] + 372                                                        # divisa FÔRMA (em cima) / ARMAÇÃO (embaixo)
    pr.linha((Q[0] + 4, Y_SPLIT), (XC - 8, Y_SPLIT), "CARIMBO_FINO")
    pr.texto(Q[0] + 8, Q[3] - 40, "FÔRMA, INSERTOS E LIGAÇÕES", "titulo", "TITULO")
    pr.texto(Q[0] + 8, Y_SPLIT - 8, "ARMAÇÃO E PROTENSÃO", "titulo", "TITULO")
    pr.cabecalho_peca("PP", f"PLACA MACIÇA PROTENDIDA 125 × 10 cm — L = {Ls[0]/10:.1f} A {Ls[-1]/10:.1f} cm — {len(TIPO)} TIPOS — {N_TOT} PEÇAS".replace(".", ","),
                      f"C{P['secao']['fck']:.0f} / fckj {P['secao']['fckj']:.0f} MPa · {NC_} {CB_} Ø{DCt_} {AC_} ({NC_ // 2} por face, {ALN_}) · σpi {SIG_PI_:.0f} MPa · {f(P['protensao']['F_macaco_kN'])} kN por {"fio" if _PR.get("aco") == "fio" else "cordoalha"} no macaco · {f(PP_KNM, 2)} kN/m",
                      largura=XC - Q[0] - 10)
    # ---- elevação da placa típica (1:25), interrompida
    e = pr.vista("ELEVAÇÃO", (Q[0] + 45, Q[3] - 120), 25, titulo="ELEVAÇÃO DE FÔRMA — PLACA TÍPICA (face interna)", subtitulo="comprimento L pela tabela de tipos; desenho interrompido", unidade="cm")
    LD, LE = 3500, 2200
    for (a, b) in ((0, LD), (LD + 500, LD + 500 + LE)):
        e.linha((a, 0), (b, 0), "VISTA"); e.linha((a, H_PL), (b, H_PL), "VISTA")
    e.linha((0, 0), (0, H_PL), "VISTA"); e.linha((LD + 500 + LE, 0), (LD + 500 + LE, H_PL), "VISTA")
    e.interrupcao((LD, 0), (LD, H_PL)); e.interrupcao((LD + 500, 0), (LD + 500, H_PL))
    LT = LD + 500 + LE
    for x0n in (0, LT - NC_B):                                                                   # NC-1 nas 2 pontas (face interna)
        e.ret(x0n, Z_NC - NC_H / 2, NC_B, NC_H, "METALICA")
        e.hachura([(x0n, Z_NC - NC_H / 2), (x0n + NC_B, Z_NC - NC_H / 2), (x0n + NC_B, Z_NC + NC_H / 2), (x0n, Z_NC + NC_H / 2)], "ANSI31", 0.3, "METALICA")
    for xt in (2250, LT - 1350):                                                      # luvas TSA M16 dos pinos PT-1 (topo e base)
        for zt_ in (60, H_PL - 60):
            e.circulo((xt, zt_), 25, "METALICA")
    for xa in (2100, LD + 500 + LE - 2100 + 900):
        e.poli([(xa - 60, H_PL), (xa - 60, H_PL + 120), (xa + 60, H_PL + 120), (xa + 60, H_PL)], "METALICA")
    e.cota_h([0, NC_B, 2100, 2250, LD], H_PL, 16, total=False)
    e.cota_v([0, H_PL], 0, -10, total=False)
    e.cota_v([0, 60, Z_NC - NC_H / 2, Z_NC + NC_H / 2, H_PL - 60, H_PL], LD + 500 + LE, 10, total=False)
    e.chamada((NC_B / 2, Z_NC + NC_H / 2), (75, 30), "NC-1 nicho Trejor encostado nas 2 pontas, teto a 104 cm da base (DETALHE 2)")
    e.chamada((2250, 60), (10, -16), "TSA M16 dos pinos guia PT-1: topo e base, a 0,21 L + 15 cm das pontas (DETALHE 3)")
    e.chamada((2100, H_PL + 120), (24, 12), "AL-P cordoalha Ø12,7 (2/placa, 0,21 L) — cortar após montar")
    # DEC-035: desforma deitada por 4 pontos na face interna (de cima na fôrma), com balancim — a 0,104 L e 0,396 L de cada ponta
    for xi in (round(0.104 * 10160), LT - round(0.104 * 10160)):
        e.ret(xi - 40, H_PL / 2 - 40, 80, 80, "METALICA"); e.circulo((xi, H_PL / 2), 20, "METALICA")
    e.chamada((round(0.104 * 10160), H_PL / 2 - 40), (30, -44), "IZ-1 desforma: 4 por placa na face interna, a 0,104 L e 0,396 L de cada ponta, meia altura (balancim)")
    e.cota_h([0, round(0.104 * 10160)], H_PL / 2, -6, total=False)
    e.marcador_corte((1200, -350), (1200, H_PL + 30), "A", lado=1)
    # ---- corte A-A (1:10)
    s = pr.vista("CORTE A-A", (Q[0] + 360, Q[3] - 205), 10, titulo="CORTE A-A — SEÇÃO DE FÔRMA", subtitulo="seção concretada 125 × 10 cm (+ macho 3 cm); encaixe macho-fêmea", unidade="cm")
    pts = [(0, 0), (30, 0), (30, 35), (70, 35), (70, 0), (100, 0), (100, 1250), (70, 1250), (70, 1280), (30, 1280), (30, 1250), (0, 1250)]
    SEC_MF = list(pts)                                                          # rev08: seção macho-fêmea (reutilizada no corte B-B)
    s.poli(pts, "CORTADO", fechada=True); s.hachura(pts, "AR-CONC", 0.03)
    s.cota_h([0, 30, 70, 100], 0, -10, total=False)
    s.cota_v([0, 35, 1250, 1280], 100, 10, total=False)
    s.cota_h([0, 100], 0, -22, total=False)                                     # espessura total concretada
    s.cota_v([0, 1250], 0, -14, total=False)                                    # altura da placa (sem o macho)
    s.cota_v([0, 1280], 0, -26, total=False)                                    # altura com o macho
    s.chamada((50, 1265), (14, 12), "macho 4 × 3")
    s.chamada((50, 17), (16, -14), "fêmea 4 × 3,5")
    # ================= rev06 (DEC-026): fixação Trejor — console soldado CS-1, nicho NC-1, pinos PT-1, trava PT-2
    DN = FX["dente_ponta"]["resultado"]["adotado"]
    import geo_fixacao as GF
    zt_cs = Z_NC + NC_H / 2 - GF.N['t_teto'] - GF.T['G']                     # topo da mesa do CS-1 (G = 50 sob o teto do nicho, PP03)
    # ---- detalhe 1: ponta da placa com o nicho NC-1 = dente Gerber (vista pela face interna, 1:10 mm)
    d1 = pr.vista("DETALHE 1", (Q[0] + 338, Q[1] + 190), 10, titulo="DETALHE 1 — PONTA DA PLACA: NICHO NC-1 E ARMADURA DO DENTE",
                  subtitulo="vista pela face interna; nariz acima do nicho calculado como dente Gerber (bielas e tirantes)", unidade="mm")
    d1.poli([(0, 600), (0, H_PL), (420, H_PL)], "VISTA"); d1.interrupcao((420, 600), (420, H_PL)); d1.linha((0, 600), (420, 600), "VISTA")
    for z in [z_ for z_ in ZC_ if z_ > 600]:
        d1.linha((10, z), (420, z), "ARM_PROT")
    d1.ret(0, Z_NC - NC_H / 2, NC_B, NC_H, "METALICA")
    d1.chapa(0, Z_NC + NC_H / 2 - 12.5, NC_B, 12.5, 0.15)                                   # teto (chapa de apoio)
    d1.chapa(NC_B - GF.N["t_parede"], Z_NC - NC_H / 2 + GF.N["t_base"], GF.N["t_parede"], NC_H - GF.N["t_base"] - GF.N["t_teto"], 0.15)   # parede lateral
    d1.chapa(0, Z_NC - NC_H / 2, NC_B - 9.5, 9.5, 0.15)                                    # base do nicho
    for (xa_, xb_) in GF.N["x_gr"]:                                                         # grampos Ø6,3 do NC-1
        d1.poli([(xa_, Z_NC + NC_H / 2), (xa_, Z_NC + NC_H / 2 + 40), (xb_, Z_NC + NC_H / 2 + 40), (xb_, Z_NC + NC_H / 2)], "METALICA")
    # rev08: armadura do dente com a mesma geometria da ND-LET-PP01 (det. 1): N3 tirante, N4 suspensão, N5/N6 costura, N7 nariz
    Z_N3_, Z_N5_, Z_N6_, X_N4_, X_N7_ = 1060, 1075, 820, (130, 170), (40, 80)
    d1.barra([(20, Z_N3_), (420, Z_N3_)], "N3", 2, 8, comp_cm=138, ponto_rotulo=(360, Z_N3_), desloc=(16, 8))
    d1.barra([(X_N4_[0], 610), (X_N4_[0], 1220), (X_N4_[1], 1220), (X_N4_[1], 610)], "N4", 1, 8, comp_cm=256,
             ponto_rotulo=(X_N4_[1], 680), desloc=(30, -4), camada="ARM_TRANSV")
    d1.barra([(15, Z_N5_), (175, Z_N5_)], "N5", 1, 6.3, comp_cm=54, ponto_rotulo=(100, Z_N5_), desloc=(40, 20), camada="ARM_TRANSV")
    d1.barra([(15, Z_N6_), (175, Z_N6_)], "N6", 1, 6.3, comp_cm=54, ponto_rotulo=(150, Z_N6_), desloc=(34, -6), camada="ARM_TRANSV")
    d1.barra([(X_N7_[0], 1050), (X_N7_[1], 1050), (X_N7_[1], 1225), (X_N7_[0], 1225), (X_N7_[0], 1050)], "N7", 1, 6.3, comp_cm=46,
             ponto_rotulo=(X_N7_[0], 1225), desloc=(-8, 12), camada="ARM_TRANSV")
    d1.cota_h([0, NC_B, NC_B + 50], 600, -10, total=False)
    d1.cota_v([600, Z_NC - NC_H / 2, Z_NC + NC_H / 2, H_PL], 0, -10, total=False)
    d1.chamada((60, Z_NC), (70, -14), f"NC-1 caixa {NC_B:g} × {NC_H:g} × {NC_P:g} aberta na ponta e na face interna (PP01 det. 3)")
    d1.chamada((60, Z_NC + NC_H / 2 - 6), (60, -3), f"teto {GF.N['t_teto']:g}: apoio do M16 de nível; armação completa N3–N7 no ND-LET-PP01".replace(".", ","))
    # ---- detalhe 2: planta da ligação placa × pilar
    d2 = pr.vista("DETALHE 2", (Q[0] + 760, Q[3] - 210), 5, titulo="DETALHE 2 — LIGAÇÃO PLACA × PILAR (PLANTA NA ALTURA DO CONSOLE)",
                  subtitulo=f"2 consoles CS-1 na CE-1 do pilar (CC-1 de fábrica na face C); junta {JUNTA} no eixo; folga 25", unidade="mm")
    pil = [(-200, 0), (200, 0), (200, 450), (-200, 450)]
    d2.poli(pil, "CORTADO", fechada=True); d2.hachura(pil, "AR-CONC", 0.03)
    d2.chapa(-CE_B / 2, 0, CE_B, GF.TCE, 0.4)                                                # CE-1
    for xs_ in (-120, 120):
        d2.ret(xs_ - 8, GF.TCE, 16, 140, "METALICA"); d2.ret(xs_ - 16, GF.TCE + 140, 32, 10, "METALICA")   # pinos Ø16 × 150 com cabeça
    d2.poli([(-150, 190), (-150, 210), (150, 210), (150, 190)], "ARM_TRANSV")              # grampo U Ø10
    for sg in (-1, 1):
        x0 = sg * 10
        pts = [(x0, -FOLGA), (sg * 450, -FOLGA), (sg * 450, -FOLGA - E_PL), (x0, -FOLGA - E_PL)]
        d2.poli(pts, "CORTADO", fechada=True); d2.hachura(pts, "AR-CONC", 0.03)
        d2.interrupcao((sg * 450, -FOLGA), (sg * 450, -FOLGA - E_PL))
        xe = x0 + sg * NC_B
        d2.poli([(x0, -FOLGA - NC_P), (xe, -FOLGA - NC_P), (xe, -FOLGA)], "METALICA")    # nicho aberto na ponta e na face interna
        xc = sg * (10 + X_CS)
        tc_ = GF.C["costas"]["t"]; ta_ = GF.C["alma"]["t"]
        d2.chapa(xc - GF.C["costas"]["b"] / 2, -tc_, GF.C["costas"]["b"], tc_, 0.4)              # costas do CS-1
        for dx in (-GF.C["alma"]["x"], GF.C["alma"]["x"]):
            d2.chapa(xc + dx - ta_ / 2, -GF.C["alma"]["y1"], ta_, GF.C["alma"]["y1"] - tc_, 0.4)   # almas
    d2.cota_h([-10 - NC_B, -10 - X_CS, -10, 10, 10 + X_CS, 10 + NC_B], -FOLGA - E_PL, -10, total=False)
    d2.cota_v([-FOLGA - E_PL, -FOLGA - NC_P, -FOLGA, 0, 450], 450, 10, total=False)
    d2.chamada((150, 6), (76, 61), f"CE-1 380×330×{GF.TCE:g}".replace(".", ",") + " + 4 pinos Ø16×150 + 2 U Ø10 (PP04)")
    d2.chamada((70, -8), (92, 6), f"CS-1: filete {FX['solda']['filete_mm']:g} E70XX nas costas (fábrica ou obra)")
    d2.chamada((-70, -FOLGA - 50), (-34, 22), "NC-1 nicho da placa (aberto na ponta)")
    d2.chamada((-350, -FOLGA - 60), (-6, -16), "placa 10 cm")
    d2.chamada((0, -FOLGA - 90), (6, -16), f"junta {JUNTA} mm: tarucel Ø25 + selante PU (±25 %)")
    # ---- detalhe 3: pino de travamento PT-1 (corte vertical na junta) e trava de pé PT-2 (planta)
    d3 = pr.vista("DETALHE 3", (Q[0] + 95, Q[1] + 490), 5, titulo="DETALHE 3 — PINO GUIA PT-1 (CARTOLA)",
                  subtitulo="GUIA DE MONTAGEM (DEC-035): M16 só na placa de baixo; na de cima a aba encosta sem parafuso — não transmite esforço", unidade="mm")
    for z0_, z1_ in ((-150, -5), (5, 150)):
        pts = [(-E_PL, z0_), (0, z0_), (0, z1_), (-E_PL, z1_)]
        d3.poli(pts, "CORTADO", fechada=True); d3.hachura(pts, "AR-CONC", 0.03)
    for zl in (-70, 70):
        d3.chapa(-70, zl - 8, 70, 16, 0.15)                                                  # luvas TSA M16 (hef 70)
    hat = [(0, -110), (6.3, -110), (6.3, -40), (36.3, -40), (36.3, 40), (6.3, 40), (6.3, 110), (0, 110), (0, 33.7), (30, 33.7), (30, -33.7), (0, -33.7)]
    d3.poli(hat, "METALICA", fechada=True); d3.hachura(hat, "ANSI31", 0.15, "METALICA")
    d3.ret(0, -70 - 8, 22, 16, "METALICA")                                         # rev08 (DEC-035): M16 só na placa de baixo
    d3.cota_v([-110, -70, 70, 110], 40, 10, total=False)
    d3.chamada((36, 0), (16, 6), "PT-1 cartola Trejor 6,3 × 80 (aço galv.)")
    d3.chamada((10, -70), (24, -24), "M16 8.8 só na placa de baixo (oblongo 18 × 40 vertical)")
    d3.chamada((-35, 70), (20, 18), "luva TSA M16 hef 70 (as 2 placas; a de cima fica livre)")
    d3.chamada((-50, 0), (-16, 14), "folga 5 mm (macho-fêmea)")
    # ---- detalhe 4: corte vertical pelo console CS-1
    d4 = pr.vista("DETALHE 4", (Q[0] + 390, Y_SPLIT + 18 - (Z_NC - NC_H / 2 - 250) / 5), 5, titulo="DETALHE 4 — CONSOLE CS-1 E NICHO NC-1 (CORTE VERTICAL)",
                  subtitulo="cada placa no seu console: peso + vento; M16 de nível, prisioneiro frontal, 2 dentes; fabricação nas PP02–PP04", unidade="mm")
    zb, za_ = Z_NC + NC_H / 2, Z_NC - NC_H / 2
    d4.ret(0, za_ - 250, 250, 600, "VISTA")
    d4.chapa(0, Z_CE - CE_H / 2, 16, CE_H, 0.4)                                            # CE-1 (embutida, rente à face)
    for zp in (Z_CE - 140, Z_CE + 140):
        d4.ret(16, zp - 8, 150, 16, "METALICA")
    pts = [(-FOLGA - E_PL, za_ - 250), (-FOLGA, za_ - 250), (-FOLGA, zb + 210), (-FOLGA - E_PL, zb + 210)]
    d4.poli(pts, "CORTADO", fechada=True); d4.hachura(pts, "AR-CONC", 0.03)
    d4.ret(-FOLGA - NC_P, za_, NC_P, NC_H, "METALICA")                                        # cavidade do nicho
    Nn, Cc = GF.N, GF.C
    pf_ = Nn["P"] - Nn["t_fundo"]
    d4.chapa(-FOLGA - pf_, zb - Nn["t_teto"], pf_, Nn["t_teto"], 0.4)                          # teto
    d4.ret(-FOLGA - Nn["t_aba"], zb - Nn["t_teto"] - Nn["h_aba"], Nn["t_aba"], Nn["h_aba"], "OCULTA")   # abas laterais (fora do corte)
    d4.chapa(-FOLGA - pf_, za_, pf_, Nn["t_base"], 0.4)                                         # base
    d4.chapa(-FOLGA - Nn["P"], za_, Nn["t_fundo"], NC_H, 0.4)                                   # fundo
    al_ = [(-y, zt_cs + z) for y, z in GF.alma_poli()]
    d4.chapa(-16, zt_cs + Cc["costas"]["z0"], 16, Cc["costas"]["z1"] - Cc["costas"]["z0"], 0.4)  # costas do CS-1
    d4.poli(al_, "METALICA", fechada=True); d4.hachura(al_, "ANSI31", 0.4, "METALICA")
    d4.chapa(-Cc["mesa"]["y1"], zt_cs - Cc["mesa"]["t"], Cc["mesa"]["y1"] - Cc["mesa"]["y0"], Cc["mesa"]["t"], 0.4)
    d4.chapa(-Cc["dente"]["y0"] - Cc["dente"]["t"], zt_cs, Cc["dente"]["t"], Cc["dente"]["h"], 0.4)   # dentes (laterais)
    d4.chapa(-Cc["ponta"]["y0"] - Cc["ponta"]["t"], zt_cs + Cc["ponta"]["z0"], Cc["ponta"]["t"], Cc["ponta"]["z1"] - Cc["ponta"]["z0"], 0.4)
    yn_ = Cc["y_nivel"]
    d4.ret(-yn_ - 12, zt_cs, 24, 22.8, "METALICA"); d4.ret(-yn_ - 8, zt_cs + 22.8, 16, GF.T["G"] - 10 - 22.8, "METALICA"); d4.ret(-yn_ - 12, zt_cs + GF.T["G"] - 10, 24, 10, "METALICA")
    yt_ = FOLGA + NC_P - Nn["t_fundo"]
    d4.ret(-yt_, zt_cs + Cc["z_frontal"] - 8, Cc["L_frontal"], 16, "METALICA")
    d4.cota_v([za_, zt_cs, zb - Nn["t_teto"], zb], -FOLGA - E_PL, -10, total=False)
    d4.cota_h([-FOLGA - E_PL, -FOLGA - NC_P, -FOLGA, -16, 0], za_ - 250, -10, total=False)
    cs = FX["console_mef"]
    d4.chamada((-6, Z_CE + 150), (54, 16), "CE-1 + pinos Ø16 × 150 (pilar, PP04)")
    d4.chamada((-8, zt_cs - 150), (-30, -24), "CS-1: costas, almas, mesa, 2 dentes, chapa de ponta (PP03)")
    d4.chamada((-yn_, zt_cs + 30), (-30, 22), f"M16 de nível: G = {GF.T['G']:g} ± {GF.T['G_tol']:g} sob o teto")
    d4.chamada((-yt_ + 10, zt_cs + Cc["z_frontal"]), (-30, 2), f"prisioneiro M16 frontal: afastamento {GF.T['a']:g} ± {GF.T['a_tol']:g}")
    d4.chamada((-Cc["dente"]["y0"] - 10, zt_cs + 25), (-30, 40), f"2 dentes {Cc['dente']['t']:g} atrás das 2 abas {GF.N['t_aba']:g} (sucção)".replace(".", ","))
    d4.chamada((-FOLGA - E_PL / 2, za_ - 120), (-14, -10), "placa 10 cm")
    # ---- detalhe 6: trava de pé PT-2 (planta, 1:5 mm) — placas de pacote suspenso (sem pano contínuo até o baldrame)
    d6 = pr.vista("DETALHE 6", (Q[0] + 680, Q[1] + 470), 5, titulo="DETALHE 6 — TRAVA DE PÉ PT-2 (PLANTA)",
                  subtitulo="placas de pacote suspenso (E, F e acima das esquadrias): 2 por placa, 15 cm acima da base", unidade="mm")
    pil6 = [(-200, 0), (0, 0), (0, 200), (-200, 200)]
    d6.poli(pil6, "CORTADO", fechada=True); d6.hachura(pil6, "AR-CONC", 0.03)
    pl6 = [(-200, -FOLGA), (260, -FOLGA), (260, -FOLGA - E_PL), (-200, -FOLGA - E_PL)]
    d6.poli(pl6, "CORTADO", fechada=True); d6.hachura(pl6, "AR-CONC", 0.03); d6.interrupcao((260, -FOLGA), (260, -FOLGA - E_PL))
    d6.chapa(0, -FOLGA, 9.5, FOLGA + 102, 0.15)                                               # aba no pilar (face lateral)
    d6.chapa(0, -FOLGA, 102, 9.5, 0.15)                                                       # aba na placa
    d6.ret(-100, 52 - 8, 100, 16, "METALICA")                                                 # BR-2 M16 hef 100 no pilar
    d6.ret(51 - 8, -FOLGA - 70, 16, 70, "METALICA")                                           # BR-1 M16 hef 70 na placa
    d6.cota_v([-FOLGA - E_PL, -FOLGA, 52, 77], 260, 10, total=False)
    d6.chamada((5, 60), (14, 14), "PT-2 L 102×102×9,5 L=150; oblongo 18 × 40 vertical na aba do pilar")
    d6.chamada((-60, 52), (30, 26), "bucha BR-2 M16 hef 100 (face lateral do pilar)")
    d6.chamada((51, -FOLGA - 50), (16, -24), "bucha BR-1 M16 hef 70 (placa)")
    # ---- detalhe 5: alça AL-P (1:10)
    d5 = pr.vista("DETALHE 5", (Q[0] + 520, Q[3] - 110), 10, titulo="DETALHE 5 — ALÇA AL-P", subtitulo="cordoalha Ø12,7 CP-190 RB — cortada rente ao topo após a montagem, ponta com epóxi", unidade="cm")
    d5.ret(-250, -600, 500, 600, "VISTA")
    d5.poli([(-60, -550), (-60, 80), (0, 120), (60, 80), (60, -550)], "ARMADURA")
    for xx in (-60, 60):
        d5.linha((xx, -550), (xx - 40, -620), "ARMADURA")
    d5.linha((-110, 0), (110, 0), "OCULTA")
    d5.chamada((80, 0), (26, -14), "linha de corte rente ao topo (após montar)")
    d5.cota_v([-550, 0, 120], 250, 8, total=False)
    d5.chamada((0, 120), (-30, 10), f"laço de 1,40 m; {f(P['transitorias']['F_alca_kN'])} kN por alça")
    # ================= ARMAÇÃO E PROTENSÃO
    Lmax = max(L for L in TIPOS if L == int(L))
    ea = pr.vista("ELEVAÇÃO DE ARMAÇÃO", (Q[0] + 45, Y_SPLIT - 85), 25, titulo=f"ELEVAÇÃO DE ARMAÇÃO — PLACA TÍPICA (face interna; barras para o {TIPO[Lmax]})",
                  subtitulo=f"{PRT_} {ADR_} {CRT_} rente às pontas; tela N1 nas 2 pontas; armadura do dente N3–N7 no DETALHE 1", unidade="cm")
    for (a_, b_) in ((0, LD), (LD + 500, LT)):
        ea.linha((a_, 0), (b_, 0), "VISTA"); ea.linha((a_, H_PL), (b_, H_PL), "VISTA")
        for z in ZC_:
            ea.linha((a_, z), (b_, z), "ARM_PROT")
    ea.linha((0, 0), (0, H_PL), "VISTA"); ea.linha((LT, 0), (LT, H_PL), "VISTA")
    ea.interrupcao((LD, 0), (LD, H_PL)); ea.interrupcao((LD + 500, 0), (LD + 500, H_PL))
    for x0t in (0, LT - 600):                                                     # tela Q92 nas pontas (60 cm)
        for z in range(100, H_PL - 50, 150):
            ea.linha((x0t + 25, z), (x0t + 575, z), "ARM_TRANSV")
        for xx in range(int(x0t) + 25, int(x0t) + 600, 150):
            ea.linha((xx, 80), (xx, H_PL - 80), "ARM_TRANSV")
    ea.barra([(30, 1215), (LD, 1215)], "N2", 2, 8, comp_cm=(Lmax - 60) / 10, ponto_rotulo=(1800, 1215), desloc=(10, 12))
    ea.linha((LD + 500, 1215), (LT - 30, 1215), "ARMADURA")
    ea.linha((30, 80), (LD, 80), "ARMADURA"); ea.linha((LD + 500, 80), (LT - 30, 80), "ARMADURA")
    ea.cota_v([0] + [z for z in ZC_ if z not in (156, 1094)] + [H_PL], 0, -10, total=False)
    ea.cota_h([0, 600, LD], 0, -10, total=False)
    ea.chamada((5000, 781), (14, 24), f"C1 — {NC_} {CB_} Ø{DCt_} ({NC_ // 2}/face), {ADR_}")
    pr.posicoes_desenho.add("C1")
    ea.chamada((300, 400), (16, -26), "N1 — tela Q92 (2 faces), 60 cm em cada ponta")
    ea.chamada((2900, 80), (8, -20), "N2 — 1 Ø8 sobre a fêmea")
    ea.marcador_corte((400, -350), (400, H_PL + 100), "B", lado=1)
    sb = pr.vista("CORTE B-B", (Q[0] + 360, Q[1] + 40), 10, titulo="CORTE B-B — SEÇÃO DE ARMAÇÃO",
                  subtitulo=f"{PRT_} {ALN_}, eixo a {f(EX_ / 10, 2)} cm das faces (cobrimento 2,0); N1 e N2 (corte na ponta, dentro da tela N1)", unidade="cm")
    sb.poli(SEC_MF, "CORTADO", fechada=True)                                   # rev08: antes desenhava por engano o contorno do DETALHE 4
    for z in ZC_:
        for xx in (EX_, 100 - EX_):
            sb.ponto_barra((xx, z), DC_, "ARM_PROT_SECAO")
    sb.poli([(50, 70), (50, 1210)], "ARM_TRANSV")
    sb.ponto_barra((50, 1215), 8); sb.ponto_barra((50, 80), 8)
    sb.cota_h([EX_, 100 - EX_], 0, -10, total=False)
    sb.cota_h([0, 100], 0, -18, total=False)
    sb.cota_v([0] + [z for z in ZC_ if z not in (156, 1094)] + [1250], 100, 10, total=False)
    sb.chamada((100 - EX_, 469), (12, 4), f"C1 — {NC_} {CB_} Ø{DCt_} (eixo a {f(EX_ / 10, 2)}; cob. 2,0); z = " + " / ".join(f(z / 10, 1) for z in ZC_) + " cm")
    sb.chamada((50, 900), (16, 8), "N1 — tela Q92 no plano médio (pontas)")
    sb.chamada((50, 1215), (-14, 10), "N2 — 1 Ø8 no macho")
    sb.chamada((50, 80), (-14, -12), "N2 — 1 Ø8 sobre a fêmea")
    PP1 = json.load(open("/home/claude/letsara/pranchas/pp01.json"))
    barras_pl = [dict(pos="N2", diam=8.0, qtd=2, comp=round((Lmax - 60) / 10), trechos=[f"{(Lmax - 60) / 10:.0f}"]),
                 dict(pos="N3", diam=8.0, qtd=4, comp=138, trechos=["138"]),
                 dict(pos="N4", diam=8.0, qtd=2, comp=256, forma=[(0, 0), (4, 0), (4, 116), (0, 116), (0, 0), (1, 1)], trechos=["4", "116", "", ""]),
                 dict(pos="N5", diam=6.3, qtd=2, comp=54, forma=[(0, 0), (16, 0), (16, 5.4), (0, 5.4), (0, 0), (1, 1)], trechos=["16", "5,4", "", ""]),
                 dict(pos="N6", diam=6.3, qtd=2, comp=54, forma=[(0, 0), (16, 0), (16, 5.4), (0, 5.4), (0, 0), (1, 1)], trechos=["16", "5,4", "", ""]),
                 dict(pos="N7", diam=6.3, qtd=2, comp=46, forma=[(0, 0), (4, 0), (4, 17.5), (0, 17.5), (0, 0), (1, 1)], trechos=["4", "17,5", "", ""])]
    XT = Q[0] + 560
    pr.texto(XT, Y_SPLIT - 20, f"BARRAS POR PLACA — {TIPO[Lmax]} (L = {Lmax / 10:.1f} cm); demais tipos: N2 = L − 6 cm (tabela AÇO PASSIVO POR TIPO)".replace(".", ","), "nota")
    tq = pr.tabela_croqui(XT, Y_SPLIT - 24, barras_pl, h_lin=9.0)
    tc = pr.tabela_cordoalhas(XT + 175, Y_SPLIT - 24, [dict(pos="C1", diam=DC_, qtd=NC_, y=round(EX_), forca=P["protensao"]["F_macaco_kN"], isol=0)], 60, Ep=200e3 if _PR.get("aco") == "fio" else 195e3, fptk=_PR.get("fptk", 1900.0), nome="FIOS" if _PR.get("aco") == "fio" else "CORDOALHAS")
    yt = pr.tabela(XT + 175, tc["y_base"] - 4, "TELA POR PLACA", ["POS", "TELA", "POSIÇÃO", "m²/pl"],
                   [["N1", "Q92 (Ø4,2 c/15)", "2 faces, 60 cm em cada ponta", f(TELA_PL, 2)]], [12, 30, 60, 26])
    pr.legenda_armadura(XT + 175, yt - 4, True)
    for t_ in pr.msp.query("TEXT"):                                               # rev08: protensão em fios
        if t_.dxf.text == "protensão (cordoalhas)" and _PR.get("aco") == "fio":
            t_.dxf.text = "protensão (fios)"
    pr.imagem(Q[0] + 12, Q[1] + 40, Q[0] + 300, Q[1] + 168, "/home/claude/letsara/pranchas/img/iso_pp_tipica.png",
              titulo="ISOMÉTRICO — PLACA TÍPICA (FACE INTERNA)", subtitulo="NC-1 nas 2 pontas, alças AL-P e luvas TSA no topo, macho-fêmea")
    pr.imagem(Q[0] + 560, Q[1] + 40, Q[0] + 760, Q[1] + 165, "/home/claude/letsara/pranchas/img/iso_pp_ponta.png",
              titulo="ISOMÉTRICO — PONTA DA PLACA", subtitulo="nicho NC-1 aberto na ponta e na face interna")
    # ---- rev10 (Nathan 25/10/2026): ESQUEMA DOS 4 PONTOS DE DESFORMA/IÇAMENTO NUMA FACE, placa inteira (sem interrupção), cotado,
    # com carga por ponto; tabela das posições por tipo. NBR 9062:2017 5.3.2 (βa 1,3 saque/manuseio) e 5.3.3 (dispositivos βa 3,0).
    Lt = max(TIPOS)
    xs4 = [round(0.104 * Lt), round(0.396 * Lt), Lt - round(0.396 * Lt), Lt - round(0.104 * Lt)]
    ei = pr.vista("IÇAMENTO", (Q[0] + 790, Q[1] + 190), 60, titulo="ESQUEMA DE DESFORMA E IÇAMENTO — 4 PONTOS NA FACE INTERNA (IZ-1)",
                  subtitulo=f"placa deitada na fôrma, face interna para cima; balancim duplo; placa {TIPO[Lt]} (L {Lt/10:.1f} cm) — demais tipos na tabela".replace(".", ","), unidade="cm")
    ei.ret(0, 0, Lt, H_PL, "VISTA")
    for xi in xs4:
        ei.ret(xi - 40, H_PL / 2 - 40, 80, 80, "METALICA"); ei.circulo((xi, H_PL / 2), 20, "METALICA")
    zb, zg = H_PL + 350, H_PL + 650                                            # balancins (esquema, fora de escala na altura)
    for a_, b_ in ((xs4[0], xs4[1]), (xs4[2], xs4[3])):
        ei.linha((a_, H_PL / 2), ((a_ + b_) / 2, zb), "METALICA"); ei.linha((b_, H_PL / 2), ((a_ + b_) / 2, zb), "METALICA")
        ei.ret((a_ + b_) / 2 - 300, zb, 600, 60, "METALICA")
    xm1, xm2 = (xs4[0] + xs4[1]) / 2, (xs4[2] + xs4[3]) / 2
    ei.ret(xm1, zg, xm2 - xm1, 60, "METALICA")
    ei.linha((xm1, zb + 60), (xm1, zg), "METALICA"); ei.linha((xm2, zb + 60), (xm2, zg), "METALICA")
    ei.linha((Lt / 2, zg + 60), (Lt / 2, zg + 250), "METALICA")
    ei.cota_h([0] + xs4 + [Lt], 0, -10, total=True)
    ei.cota_v([0, H_PL / 2, H_PL], Lt, 10, total=False)
    Pk = peso_t(Lt) * 10 / 4
    ei.chamada((xs4[0], H_PL / 2), (6, 42), f"IZ-1 (4x) a 0,104 L e 0,396 L de cada ponta, meia altura: {f(Pk, 1)} kN por ponto (peso/4); com βa 1,3: {f(1.3 * Pk, 1)} kN ≤ 12,7 kN (1,3 t, FS ≥ 3)")
    ei.chamada((Lt / 2, zg + 200), (14, 3), "balancim duplo (cargas iguais nos 4 pontos); cabos a prumo")
    rows_i = []
    for L_ in sorted(TIPOS, key=lambda L: -L):
        a1, a2 = round(0.104 * L_), round(0.396 * L_)
        pk = peso_t(L_) * 10 / 4
        rows_i.append([TIPO[L_], f"{L_/10:.1f}".replace(".", ","), f"{a1/10:.1f}".replace(".", ","), f"{a2/10:.1f}".replace(".", ","), f(pk, 1), f(1.3 * pk, 1)])
    pr.tabela(Q[0] + 780, Q[1] + 150, "PONTOS DE DESFORMA / IÇAMENTO IZ-1 POR TIPO (4 por placa, face interna)", ["TIPO", "L (cm)", "a1 (cm)", "a2 (cm)", "Pk (kN)", "βa·Pk (kN)"],
              rows_i, [22, 28, 28, 28, 28, 34], h_lin=4.6)
    # ---- tabelas
    y = Q[3] - 6
    rows = []
    for L in sorted(TIPOS, key=lambda L: -L):
        vis = sorted(set(v for v, _ in TIPOS[L]))
        rows.append([TIPO[L], f"{L/10:.1f}".replace(".", ","), len(TIPOS[L]), f(peso_t(L), 2), ", ".join(vis)])
    rows.append(["", "total", N_TOT, f(PESO_TOT, 1), ""])
    y = pr.tabela(XC, y, f"TIPOS DE PLACA — {N_TOT} PEÇAS", ["TIPO", "L (cm)", "QT", "PESO (t)", "VISTAS"], rows, [18, 22, 14, 22, 114], destaque_ultima=True)
    ins = [["NC-1", f"Caixa {NC_B:g}×{NC_H:g}×{NC_P:g} (ND-LET-PP02)", 2, "face int., 2 pontas (1 junto à porta)"],
           ["TSA", "Luva roscada M16 hef 70 (PT-1)", 4, "topo e base, 0,21 L + 15"],
           ["AL-P", "Laço de cordoalha Ø12,7 (1,40 m)", 2, "topo, a 0,21 L; cortar após montar"],
           ["IZ-1", "Inserto de içamento M16, trabalho ≥ 1,3 t (FS ≥ 3)", 4, "face int., 0,104 e 0,396 L, meia altura"],
           ["BR-1", "Bucha M16 hef 70 (só com PT-2)", "(2)", "pé, ao lado do pilar"],
           ["CS-1", "Console (ND-LET-PP03)", "2", "CC-1 na face C ou CE-1 lateral"],
           ["PT-1", "Cartola 6,3 × 80 + 2 M16", "2", "junta de baixo (det. 3)"],
           ["PT-2", "L 102×102×9,5 L=150 + 2 M16", "(2)", "pé, pacote suspenso (det. 6)"]]
    y = pr.tabela(XC, y - 4, "INSERTOS E PEÇAS METÁLICAS — mm", ["MARCA", "DESCRIÇÃO", "QT/PL", "POSIÇÃO"], ins, [14, 92, 12, 72])
    rows_a = []
    for L in sorted(TIPOS, key=lambda L: -L):
        n = len(TIPOS[L])
        kg_n2 = 2 * (L - 60) / 1000 * 0.395 * 1.10
        kg_den = KG_DENTE * 1.10
        rows_a.append([TIPO[L], n, f"2 Ø8 C={(L - 60)/10:.0f}".replace(".", ","), f(TELA_PL, 2), f(kg_n2 + TELA_PL * 1.48 * 1.10 + kg_den, 1), f((kg_n2 + TELA_PL * 1.48 * 1.10 + kg_den) * n, 0)])
    y = pr.tabela(XC, y - 4, "AÇO PASSIVO POR TIPO (+10% perdas)", ["TIPO", "QT", "N2 (macho/fêmea)", "N1 Q92 (m²/pl)", "kg/pl (c/ N3–N7)", "kg total"], rows_a, [16, 12, 44, 38, 30, 30])
    pr.notas(XC, y - 4, [
        f"Concreto C{P['secao']['fck']:.0f}; liberar a protensão (GRADUAL e simétrica — lbpt {f(P['protensao']['lbpt_gradual_m'] * 100, 0)} cm; liberação brusca proibida: c/φ 1,6), desformar e bascular com fckj ≥ {P['secao']['fckj']:.0f} MPa. Cobrimento da protensão 2,0 cm (faces interna e externa): elemento delgado, exige fábrica com controle de pré-fabricado (NBR 9062:2017 9.2.1.1 e 12.1.2), fck ≥ 40 MPa, a/c ≤ 0,45 e CAA II — confirmar.",
        f"PP-05RE/RD e PP-08RE/RD (G-17/G-11 e C-17/C-11): mesma fôrma e protensão da PP-05 / PP-08 com recorte de {REC_B / 10:g} × {(H_PL - REC_Z0) / 10:g} cm na ponta do eixo C (I130 + CP-I130), nicho NC-1 a {REC_B / 10:g} cm da ponta e armadura do toco — ND-LET-PP06 (DEC-044).",
        f"PP-05P (placa I-15, sobre a porta da vista I): mesma fôrma e protensão da PP-05 e 2 buchas BR-1 M16 hef 70 na face interna, 150 acima da base, nos eixos das ombreiras OM-1. Placa típica: {NC_} {CB_} Ø{DCt_} {AC_} aderentes, {NC_ // 2} por face, {ALN_}, a " + " / ".join(f(z / 10, 1) for z in ZC_) + f" cm da base (eixo a {f(EX_ / 10, 2)} cm das faces), σpi = {SIG_PI_:.0f} MPa — {f(P['protensao']['F_macaco_kN'])} kN por {"fio" if _PR.get("aco") == "fio" else "cordoalha"} no macaco; alongamento teórico {ALONG_} mm em pista de 60 m (Ep {EP_ / 1000:.0f} GPa) (tolerância ±7 %).",
        f"Produção deitada, face interna para cima: nichos NC-1 e luvas TSA presos na fôrma com gabarito; armadura N3–N7 da ponta (ND-LET-PP01 det. 1 e 2); basculamento e montagem pelas alças AL-P do topo; depois de montada a placa, cortar as alças rente ao topo (disco, sem aquecer o concreto) e proteger as pontas com epóxi antes de montar a placa de cima (junta de 5 mm); desforma deitada por 4 pontos na face interna (insertos IZ-1 a 0,104 L e 0,396 L de cada ponta, meia altura) com balancim (sem balancim a face de cima fica no limite de tração); estocagem EM PÉ em cavalete (placa na posição de montagem, apoiada nos 2 calços a 0,21 L da base) — não estocar deitada: deitada a placa flecha ~7 mm na hora e ~27 mm com a fluência e fica empenada; {PRT_} simétricos nas 2 faces e em altura, sem curvatura na liberação.",
        f"Montagem (sistema Trejor, DEC-026/031): consoles da face C já concretados com o pilar (CC-1); nas faces laterais soldar o CS-1 na CE-1 no nível da topografia; a placa encosta no pilar com o braço entrando no NC-1 e desce até o teto apoiar no M16 de nível (G {GF.T['G']:g} ± {GF.T['G_tol']:g}), afastamento {GF.T['a']:g} ± {GF.T['a_tol']:g} pelo prisioneiro frontal (sequência na ND-LET-PP01). Cada placa é independente e leva só o próprio peso nos seus 2 consoles: folga de 5 mm na junta macho-fêmea, sem elastômero. Pinos guia PT-1 (só na placa de baixo) na junta (ou PT-2 no pé, nas placas de pacote suspenso) antes de soltar o guindaste.",
        f"Cargas por console: G = {f(FX['cargas_por_console']['G_k_kN'])} kN (k), Vd = {f(FX['cargas_por_console']['Vd_kN'])} kN (montagem, γf·βa = 1,69), vento {f(FX['cargas_por_console']['vento_d_kN'])} kN (d); PT-1 só guia de montagem (não transmite esforço — DEC-035), PT-2 {f(FX['trava_pe_PT2']['F_d_kN'])} kN. Medidas do CS-1/NC-1 de pré-dimensionamento: confirmar com o catálogo Trejor (consoles para painéis de fachada).",
        "Tipo = comprimento; nas pontas de canto a placa vai até a face externa do pilar de canto. Posição de cada peça: pranchas das vistas (ND-LET-PP-A … PP-I).",
        "Tolerâncias (NBR 9062:2017 5.2.2): comprimento ±5 mm (de projeto, para a junta de 20 mm), espessura −5/+10 mm, planicidade ±L/1000, insertos ±15 mm; montagem: prumo H/300 ≤ 25 mm, nível ±10 mm. Içamento na vertical pelas alças do topo: estabilidade lateral verificada (6.1).",
        "Cotas de concreto em cm, metálicas em mm. Não medir no desenho."], 190)
    avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-PP00")
    print("PP00", len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos", [a for a in avisos if a[0] == "ERRO" or "sobrep" in a[1]][:8])


# ================================================================== ND-LET-CM01 rev 02 — locação e ordem das vistas
def prancha_cm():
    pr = carimbo("ND-LET-CM01", "PLACAS DE FECHAMENTO — LOCAÇÃO CONFORME AS VISTAS DO R01 (A A J), ORDEM DE MONTAGEM DAS VISTAS E PENDÊNCIAS", "01/01", rev="03")
    pr.revisao("01", "12/10/2026", "LOCAÇÃO E VISTAS CONFORME R01 (A–J)")
    pr.revisao("02", "12/10/2026", "GEOMETRIA DA LOCAÇÃO DO R01; H/J LATERAIS DO ANEXO; E/F ABERTAS ATÉ +7,50; 2 PORTÕES; PRANCHAS POR VISTA")
    pr.revisao("03", "14/10/2026", "PLACAS 125 × 10; LIGAÇÕES SEM SOLDA; VT DO EIXO A A +6,25; PORTÕES ATÉ +7,40")
    pr.revisao("04", "16/10/2026", "NBR 9062: SEM VT; E E F ABERTAS ATÉ +7,50; JUNTA VERTICAL 20 mm")
    pr.revisao("06", "17/10/2026", "FIXAÇÃO TREJOR (CS-1/CC-1 + CE-1 + NC-1 + PT-1/PT-2); TOLERÂNCIA ±12 (DEC-031)")
    Q = pr.quadro
    XC = Q[2] - 190
    pr.cabecalho_peca("CM", f"PLACAS PROTENDIDAS 125 × 10 — {N_TOT} PEÇAS · {len(TIPO)} TIPOS · 10 VISTAS · {f(PESO_TOT, 0)} t",
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
    for _yc in (46.317, 62.833):                                           # DEC-058: dois PC-03 40×40
        kp.ret(M(19.75) - 200, M(_yc) - 200, 400, 400, "CORTADO")
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
    # rev10 (Nathan 25/10/2026): cada parede na cor da sua vista (mesmas cores das PP-x e do isométrico)
    _r = lambda x0, y0, x1, y1: [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    _faixas = [("I", _r(FACE_X[0], FACE_Y[0] - o - 150, FACE_X[1], FACE_Y[0] - o)), ("A", _r(FACE_X[0], FACE_Y[1] + o, FACE_X[1], FACE_Y[1] + o + 150)),
               ("G", _r(FACE_X[0], M(Y_LIN[1]) + 300 + o, FACE_X[1], M(Y_LIN[1]) + 300 + o + 150)),
               ("H", _r(xe0, FACE_Y[0], xe1, M(Y_LIN[1]))), ("E", _r(xe0, M(Y_LIN[1]), xe1, M(Y_LIN[3]))), ("B", _r(xe0, M(Y_LIN[3]), xe1, FACE_Y[1])),
               ("J", _r(xd0, FACE_Y[0], xd1, M(Y_LIN[1]))), ("F", _r(xd0, M(Y_LIN[1]), xd1, M(Y_LIN[3]))), ("D", _r(xd0, M(Y_LIN[3]), xd1, FACE_Y[1]))]
    for b, (xa, xb) in enumerate(zip(X_L4[:-1], X_L4[1:])):
        if b in (1, 4):
            continue
        _faixas.append(("C", _r(FACE_X[0] if b == 0 else M(xa), M(Y_LIN[3]) - 200 - o - 150, FACE_X[1] if b == 5 else M(xb), M(Y_LIN[3]) - 200 - o)))
    for V_, pts_ in _faixas:
        hachura_cor(kp, [(x_, y_) for x_, y_ in pts_], V_, 0.2)
    lg = pr.vista("LEGENDA", (Q[0] + 18, Q[1] + 118), 1, titulo="CORES DAS PAREDES (VISTAS)", subtitulo="mesmas cores nas pranchas PP-x e no isométrico", unidade="mm")
    for k_, V_ in enumerate("ABCDEFGHIJ"):
        yy_ = -k_ * 7.0
        hachura_cor(lg, _r(0, yy_, 10, yy_ + 5), V_, 0.4)
        lg.poli(_r(0, yy_, 10, yy_ + 5), "VISTA", fechada=True)
        lg.texto((13, yy_ + 1), f"VISTA {V_} — {VISTAS[V_]['titulo'].split(' — ')[1].split(' (')[0]}", "min")
    pr.imagem(XC, Q[1] + 140, XC + 186, Q[1] + 290, "/home/claude/letsara/pranchas/img/iso_fachadas.png",
              titulo="ISOMÉTRICO DO FECHAMENTO — CORES POR PAREDE", subtitulo="placas com transparência de 60 %; pilares e vigas em cinza")
    pos = {"A": (19.75, 85.6), "B": (-5.5, 54.5), "C": (19.75, 25.5), "D": (45.0, 54.5), "E": (-5.5, 19.7), "F": (45.0, 19.7),
           "G": (19.75, 13.5), "H": (-5.5, 4.8), "I": (19.75, -3.6), "J": (45.0, 4.8)}
    for V, (x, y) in pos.items():
        if V in ("C", "G"):
            x = 14.8                                                                  # rev08: fora da linha do eixo C
        kp.circulo((M(x), M(y)), 1500, "INDICACAO")
        kp.texto((M(x), M(y) + 250), V, "titulo", "MIDDLE_CENTER")
        kp.texto((M(x), M(y) - 700), f"{len(DADOS[V][0])} pç", "min", "MIDDLE_CENTER")
    kp.texto((M(24.7), M(45)), "PAVILHÃO (fechado por B, D, A e C)", "nota", "MIDDLE_CENTER")
    kp.texto((M(24.7), M(23.0)), "laterais E e F abertas até +7,50", "min", "MIDDLE_CENTER")
    kp.texto((M(24.7), M(5.5)), "ANEXO / MEZANINO (H, J, I, G)", "nota", "MIDDLE_CENTER")
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
        rows.append([i, V, VISTAS[V]["titulo"].split(" — ")[1].split(" (")[0], len(pec), f(sum(peso_t(p["Lk"]) for p in pec), 1), f"ND-LET-{folha}"])
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
        "Vistas como no R01: B e D (linhas 4–9) fechadas, 8 fiadas; E (eixo A) e F (eixo E), linhas 2–4, só as 2 fiadas de cima (rev04, sem VT); H, J (anexo) e I (fachada da linha 1) com faixas de esquadria de +1,25 a +2,50 e de +5,00 a +6,25 e porta na I; A (linha 9) fechada.",
        "Paredes internas C (linha 4) e G (linha 2) com placas até +7,50 (vão A–B até +6,25: a TS-01 desce a +7,19 junto ao eixo A); acima, até a telha, fechamento metálico leve — confirmar com o cliente.",
        "Linha 4: 2 portões 500 × 750 (P9–P10 e P10–P12), livres até +7,50 (DEC-059: PG apoiam a TS-01A); placa PV-1 sobre o portão PG-04–PG-03; o trecho P10–P11–P10 é fechado.",
        "Placas 125 × 10 (rev03) por fora dos pilares (folga 25 mm), juntas verticais de 20 mm no eixo dos pilares (rev04; tolerância de comprimento da placa ±5 mm); rev06 (DEC-026, sistema Trejor): cada placa nos seus 2 consoles CS-1 (concretados com o pilar na face C — CC-1, DEC-031 — ou soldados na obra nas CE-1 das faces laterais), nicho NC-1 nas pontas, folga de 5 mm na junta horizontal (sem empilhar peso), 2 pinos guia PT-1 por junta (só guia, não transmitem esforço) ou trava de pé PT-2 nos pacotes suspensos: ND-LET-PP00.",
        "Rev04: sem vigas de travamento VT (só entram com ponte rolante ou carga especificada); o fechamento é isostático (consoles com folga e pinos com furo oblongo vertical) e não é contado no contraventamento — a contribuição medida no modelo global foi desprezível (9,9 → 9,8 mm).",
        "Cotas de concreto em cm, níveis em m. Não medir no desenho."], 190)
    avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-CM01")
    print("CM01", len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos", [a for a in avisos if a[0] == "ERRO" or "sobrep" in a[1]][:8])


# ================================================================== ND-LET-VT01 rev 02 — vigas de travamento
def vt_barras(Lc):
    """Armadura da VT 25×60 (cm): N1 3 Ø12,5 inferior (só no corpo), N2 3 Ø12,5 superior, N3 pele 4 Ø8, N4 estribos Ø6,3 c/15,
    N5 tirante do dente 2 Ø12,5 por ponta, N6 suspensão 2 estribos Ø8 por ponta, N7 estribos do dente 3 Ø6,3 por ponta."""
    Lb = round(Lc - 46)
    n4 = int((Lc - 46) // 15) + 1
    return [dict(pos="N1", diam=12.5, qtd=3, comp=Lb, forma=[(0, 0), (85, 0)], trechos=[f"{Lb}"]),
            dict(pos="N2", diam=12.5, qtd=3, comp=round(Lc - 6), forma=[(0, 0), (85, 0)], trechos=[f"{round(Lc - 6)}"]),
            dict(pos="N3", diam=8.0, qtd=4, comp=Lb, forma=[(0, 0), (85, 0)], trechos=[f"{Lb}"]),
            dict(pos="N4", diam=6.3, qtd=n4, comp=162, forma=[(0, 0), (19, 0), (19, 54), (0, 54), (0, 0), (2, 2)], trechos=["19", "54", "", ""]),
            dict(pos="N5", diam=12.5, qtd=4, comp=70, forma=[(0, 6), (0, 0), (64, 0)], trechos=["6", "64"]),
            dict(pos="N6", diam=8.0, qtd=4, comp=162, forma=[(0, 0), (19, 0), (19, 54), (0, 54), (0, 0), (2, 2)], trechos=["19", "54", "", ""]),
            dict(pos="N7", diam=6.3, qtd=6, comp=102, forma=[(0, 0), (19, 0), (19, 24), (0, 24), (0, 0), (2, 2)], trechos=["19", "24", "", ""])]


def prancha_vt():
    agr = {}
    for i in range(1, 8):
        agr.setdefault(round(Y_LIN[i + 1] - Y_LIN[i] - 0.40, 3), []).append(f"L{i+1}–L{i+2}")
    lista = sorted(agr.items(), key=lambda t: -t[0])
    MK = {L: f"VT-{k+1:02d}" for k, (L, _) in enumerate(lista)}
    peso = lambda L: 0.25 * 0.60 * L * 25
    pr = carimbo("ND-LET-VT01", "VIGAS DE TRAVAMENTO VT 25 × 60 (EIXOS A E E, +7,50 A +8,10, DENTES GERBER) — PLANTA, ELEVAÇÃO, SEÇÃO E APOIO", "01/01", rev="03")
    pr.revisao("01", "12/10/2026", "VT/VV A +6,25/+6,85 COM DENTES GERBER")
    pr.revisao("02", "12/10/2026", "GEOMETRIA DO R01; VT A +7,50/+8,10 ATRÁS DA FIADA +7,50; SEM VERGAS (PORTÕES SOB A TS-01)")
    pr.revisao("03", "12/10/2026", "CP-VT 25×20×29 SEM CHANFRO (FUNDO ALINHADO À VT); DENTE REDESENHADO; RELAÇÃO DO AÇO")
    Q = pr.quadro
    XC = Q[2] - 190
    pr.cabecalho_peca("VT", f"VIGA DE TRAVAMENTO 25 × 60 cm — L = {lista[-1][0]*100:.1f} A {lista[0][0]*100:.1f} cm — 14 PEÇAS".replace(".", ","),
                      "eixos A e E, linhas 2 a 9; eixo A: +6,25/+6,85 (assento +6,54); eixo E: +7,50/+8,10 (assento +7,79); dentes 30 × 20 nos consolos CP-VT", largura=XC - Q[0] - 10)
    v = pr.vista("PLANTA", (Q[0] + 50, Q[1] + 60), 400, titulo="PLANTA — VT (A: +6,25/+6,85 · E: +7,50/+8,10)", subtitulo="eixos A e E, linhas 2 a 9", unidade="cm")
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
    e = pr.vista("ELEVAÇÃO", (Q[0] + 75 - M(Y_LIN[1]) / 150, Q[3] - 140), 150, titulo="ELEVAÇÃO — EIXO A, LINHAS 2 A 9 (vista de dentro)", subtitulo="VT a +6,25/+6,85 atrás da fiada +6,25/+7,50; linhas 2–4: placas só acima de +6,25", unidade="cm")
    for i in range(1, 9):
        e.ret(M(Y_LIN[i]) - 200, -500, 400, 10500, "CORTADO"); e.texto((M(Y_LIN[i]), 10250), f"L{i+1}", "min", "BOTTOM_CENTER")
    e.linha((M(Y_LIN[1]) - 1000, 0), (M(Y_LIN[8]) + 1000, 0), "TERRENO")
    for i in range(1, 8):
        L = round(Y_LIN[i + 1] - Y_LIN[i] - 0.40, 3)
        xi, Lm = M(Y_LIN[i]) + 225, M(L) - 50
        za0, za1, _ = Z_VT_A
        e.poli([(xi, za0 + 300), (xi + 200, za0 + 300), (xi + 200, za0), (xi + Lm - 200, za0), (xi + Lm - 200, za0 + 300), (xi + Lm, za0 + 300), (xi + Lm, za1), (xi, za1)], "VISTA", fechada=True)
        e.texto((M((Y_LIN[i] + Y_LIN[i + 1]) / 2), za1 + 250), MK[L], "min", "BOTTOM_CENTER")
        for z in range(6250 if i <= 2 else 0, 10000, H_PL):
            e.ret(M(Y_LIN[i]) + 5, z + 5, M(Y_LIN[i + 1] - Y_LIN[i]) - 10, H_PL - 10, "OCULTA")
    e.cota_h([M(y) for y in Y_LIN[1:]], -500, -8, total=False)
    e.cota_v([0, Z_VT_A[0], Z_VT_A[1], 7500, 10000], M(Y_LIN[8]) + 400, 8, total=False)
    e.chamada((M(Y_LIN[2]) + 3000, Z_VT_A[1]), (8, 24), "fiada de placas +6,25/+7,50 (por fora) esconde a VT")
    s = pr.vista("SEÇÃO", (Q[0] + 300, Q[1] + 60), 10, titulo="SEÇÃO VT", subtitulo="25 × 60, C40", unidade="cm")
    pts = [(0, 0), (250, 0), (250, 600), (0, 600)]
    s.poli(pts, "CORTADO", fechada=True); s.hachura(pts, "AR-CONC", 0.03)
    s.poli([(30, 30), (220, 30), (220, 570), (30, 570)], "ARM_TRANSV", fechada=True)
    for x in (45, 125, 205):
        s.ponto_barra((x, 45), 12.5); s.ponto_barra((x, 555), 12.5)
    for yy in (220, 380):
        s.ponto_barra((40, yy), 8); s.ponto_barra((210, yy), 8)
    s.cota_h([0, 250], 0, -8); s.cota_v([0, 600], 250, 8)
    s.chamada((205, 555), (12, 8), "N1/N2 — 3 Ø12,5 em cima e embaixo"); s.chamada((210, 380), (12, 0), "N3 pele 2 Ø8/face"); s.chamada((220, 300), (12, -10), "N4 estribo Ø6,3 c/15")
    a = pr.vista("DETALHE 1", (Q[0] + 400, Q[1] + 205), 10, titulo="DETALHE 1 — DENTE GERBER DA VT NO CONSOLO CP-VT", subtitulo="dente 30 × 20; CP-VT + PN-1 Ø20; neoprene 200×150×10", unidade="cm")
    a.ret(-600, -500, 600, 1700, "VISTA")
    a.ret(0, 10, 200, 290, "VISTA")                                                   # CP-VT 20 × 29 (proj.) sem chanfro: fundo alinhado ao da VT
    a.ret(100 - 10, 100, 20, 400, "OCULTA"); a.chapa(25, 300, 200, 10)
    a.poli([(25, 310), (225, 310), (225, 10), (1025, 10), (1025, 610), (25, 610)], "VISTA", fechada=True)   # VT com dente 20 × 30
    a.interrupcao((1025, 10), (1025, 610))
    a.poli([(60, 370), (60, 340), (700, 340)], "ARMADURA"); a.poli([(260, 40), (260, 580)], "ARM_TRANSV"); a.poli([(340, 40), (340, 580)], "ARM_TRANSV")
    a.cota_h([-600, 0, 200, 225, 1025], -500, -8, total=False); a.cota_v([10, 300, 310, 610], 1025, 8, total=False)
    a.chamada((100, 150), (14, -30), "CP-VT (b 25, proj. 20, h 29) sem chanfro, faces laterais dos pilares (assento +6,54 no eixo A, +7,79 no E)")
    a.chamada((100, 450), (14, 10), "PN-1 Ø20 no TB-1 Ø50 da viga"); a.chamada((-300, 1000), (-10, 8), "pilar")
    a.chamada((500, 340), (4, -30), "N5 tirante 2 Ø12,5 (NBR 9062:2017 7.4)"); a.chamada((300, 500), (12, 14), "N6 suspensão 2 estribos Ø8")
    y = Q[3] - 40
    linhas = [[MK[L], ", ".join(pos), 2 * len(pos), f"{L*100:.1f}".replace(".", ","), f(peso(L) / 9.81, 2)] for L, pos in lista]
    y = pr.tabela(XC, y, "MARCAS — VT 25×60 (eixos A e E)", ["MARCA", "TRECHO (linhas)", "QT", "L (cm)", "PESO (t)"], linhas, [18, 90, 12, 24, 26], h_lin=5.5)
    ins = [["TB-1", "Tubo Ø50×3,0 L=280, passante, sem solda", 2, "a 10 cm das pontas"], ["AL-1", "Laço de cordoalha Ø12,7", 2, "a L/5 das pontas"]]
    y = pr.tabela(XC, y - 4, "INSERTOS POR VIGA — mm", ["MARCA", "DESCRIÇÃO", "QT", "POSIÇÃO"], ins, [16, 100, 10, 64])
    Lmax = lista[0][0] * 100
    y = pr.tabela_croqui(XC, y - 4, vt_barras(Lmax), h_lin=9.0)["y_base"]
    kgm = {6.3: 0.245, 8.0: 0.395, 12.5: 0.963}
    kg = lambda Lc: sum(b["qtd"] * b["comp"] / 100 * kgm[b["diam"]] for b in vt_barras(Lc)) * 1.10
    y = pr.tabela(XC, y - 4, "AÇO CA-50 POR MARCA (+10% perdas)", ["MARCA", "L (cm)", "QT", "kg/peça", "kg total"],
                  [[MK[L], f"{L*100:.1f}".replace(".", ","), 2 * len(pos), f(kg(L * 100), 1), f(kg(L * 100) * 2 * len(pos), 1)] for L, pos in lista], [18, 30, 14, 30, 30], h_lin=5.5)
    y = pr.legenda_armadura(XC, y - 4, False)
    pr.notas(XC, y - 4, [f"Relação do aço desenhada para {MK[lista[0][0]]} (L = {Lmax:.1f} cm); nas demais marcas N1, N2, N3 e a quantidade de N4 seguem o comprimento da peça (tabela por marca).".replace(".", ",", 1),
                         "Eixo A (rev03): fundo +6,25, topo +6,85, atrás da fiada +6,25/+7,50, assento do CP-VT +6,54 — abaixo do recuo +7,19 dos pilares P1 (assento da TS-01). Eixo E: fundo +7,50, topo +8,10, atrás da fiada +7,50/+8,75, assento +7,79. Dentes Gerber 30 × 20 nos consolos CP-VT.",
                         "Linha 4 sem verga: os portões ficam sob a TS-01A da linha 4, livres até +7,50 (DEC-059); placa PV-1 sobre o portão PG-04–PG-03.",
                         "Linhas 2–4: vista E (eixo A) aberta até +6,25 e vista F (eixo E) até +7,50; a VT fica aparente por dentro e escondida por fora pela fiada de placas.",
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
    if "vt" in so:                                       # rev04: VT retiradas (sem ponte rolante)
        prancha_vt()
    for k, (Vs, des) in enumerate(PRANCHAS_VISTA, 1):
        if not so or des.split("-")[-1].lower() in so:
            prancha_vista(Vs, des, f"{k:02d}/{len(PRANCHAS_VISTA):02d}")
    print({V: len(DADOS[V][0]) for V in VISTAS}, "total", N_TOT, f"{PESO_TOT:.1f} t", {TIPO[L]: (L, len(v)) for L, v in TIPOS.items()})
