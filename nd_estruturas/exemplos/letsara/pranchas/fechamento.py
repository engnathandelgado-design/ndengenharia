"""ND-LET-CM01 (rev 01) — placas de fechamento conforme a locação do R01 (vistas A–J, portões na linha 3) e
ND-LET-VT01 — vigas de travamento e vergas (25 × 60) a +6,10, escondidas no fechamento. A1, cotas de concreto em cm."""
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha

f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
M = lambda v: round(v * 1000)
Y_LIN = [0.0, 10.05, 19.705, 29.36, 38.865, 48.445, 58.025, 67.605, 76.81]
X_FACH = [0.0, 9.87, 20.05, 29.63, 40.10]
H_PL, E_PL, JUNTA = 1250, 150, 10
Z_TOPO = 10000
Z_VERGA = 6100                                   # topo das vergas / vigas de travamento (fundo +5,50 = altura livre dos portões)
# pilares da linha 3 (parede dos portões): P1, P9 (40×40), P10 (25×25), P11 (40×40), P10, P12 (40×40), P2
X_L3 = [(0.0, 600, "PL-01"), (9.87, 400, "P9 40×40"), (14.96, 250, "P10 25×25"), (20.05, 400, "P11 40×40"), (25.14, 250, "P10 25×25"), (29.63, 400, "P12 40×40"), (40.10, 600, "PL-05")]
# linha 2 (parede do mezanino): P1, P8, P8A, P8B, P6 (25×40), P2
X_L2 = [(0.0, 600, "PL-02"), (9.87, 600, "PM-01"), (20.05, 500, "PC-01"), (29.63, 600, "PM-01"), (36.30, 250, "P6 25×40"), (40.10, 600, "PL-06")]


def fiadas(z0=0, z1=Z_TOPO):
    """fiadas de 125 cm entre z0 e z1 (a última pode ser menor)."""
    out, z = [], z0
    while z + 100 < z1:
        out.append((z, min(z + H_PL, z1)))
        z += H_PL
    return out


# ================================================================== vistas (elevações) — dados
def vista_lateral(nome, linhas_ini, linhas_fim, fiadas_z=(0, Z_TOPO)):
    """vista de um eixo lateral (A ou E): bays entre linhas consecutivas."""
    bays = []
    for i in range(linhas_ini, linhas_fim):
        bays.append((M(Y_LIN[i]), M(Y_LIN[i + 1]), 400, 400))
    return dict(nome=nome, bays=bays, pil=[(M(Y_LIN[i]), 400) for i in range(linhas_ini, linhas_fim + 1)], fiadas=fiadas(*fiadas_z), portao=[])


def vista_transv(nome, pilares, portoes=()):
    bays = []
    for (xa, ba, _), (xb, bb, _) in zip(pilares[:-1], pilares[1:]):
        bays.append((M(xa), M(xb), ba, bb))
    return dict(nome=nome, bays=bays, pil=[(M(x), b) for x, b, _ in pilares], fiadas=fiadas(), portao=list(portoes), nomes=[n for _, _, n in pilares])


VISTAS = {
    "A": dict(vista_transv("A", [(0.0, 600, "PL-04"), (9.87, 400, "PF-01"), (20.05, 400, "PF-02"), (29.63, 400, "PF-03"), (40.10, 600, "PL-08")]), titulo="VISTA A — FACHADA LINHA 9 (externa)"),
    "B": dict(vista_lateral("B", 3, 8), titulo="VISTA B — EIXO A, LINHAS 4 A 9 (externa)"),
    "E": dict(vista_lateral("E", 0, 3, (7500, Z_TOPO)), titulo="VISTA E — EIXO A, LINHAS 1 A 4 (docas: só as 2 fiadas de cima)"),
    "C": dict(vista_transv("C", X_L3, portoes=[(1, 4)]), titulo="VISTA C — PAREDE DA LINHA 3 COM PORTÕES (vista do pavilhão)"),
    "G": dict(vista_transv("G", X_L2), titulo="VISTA G — PAREDE DA LINHA 2 (vista do pavilhão; VISTA I = outra face)"),
    "H": dict(vista_transv("H", [(0.0, 600, "PL-03"), (9.87, 400, "PF-01")]), titulo="VISTA H — FACHADA LINHA 1, A–B"),
    "J": dict(vista_transv("J", [(29.63, 400, "PF-03"), (36.30, 250, "P7"), (40.10, 600, "PL-07")]), titulo="VISTA J — FACHADA LINHA 1, D–E"),
}
VISTAS["D"] = dict(VISTAS["B"], nome="D", titulo="VISTA D — EIXO E, LINHAS 4 A 9 (externa) = VISTA B espelhada")
VISTAS["F"] = dict(VISTAS["E"], nome="F", titulo="VISTA F — EIXO E, LINHAS 1 A 4 = VISTA E espelhada")

# placas: por bay e fiada; comprimento = c-c + 40 (juntas de 10 mm no eixo dos pilares, placa passa 20 cm da face)
PLACAS = {}        # L -> [(vista, bay, fiada)]
def registrar(v):
    d = VISTAS[v]
    for k, (xa, xb, ba, bb) in enumerate(d["bays"]):
        gate = any(a <= k <= b for a, b in d["portao"])
        L = xb - xa + 400 - JUNTA if not gate else xb - xa - (ba + bb) // 2 - 2 * JUNTA
        for (z0, z1) in d["fiadas"]:
            if gate and z0 < Z_VERGA:
                continue
            PLACAS.setdefault((L, z1 - z0), []).append((v, k, z0))
for v in VISTAS:
    registrar(v)
ordem = sorted(PLACAS, key=lambda t: (-t[1], -t[0]))
MARCA = {k: f"CM-{i+1:02d}" for i, k in enumerate(ordem)}


def desenhar_vista(pr, v, origem, esc=200):
    d = VISTAS[v]
    sub = "placas 125 × 15 (juntas 10 mm); VT/VV 25×60 a +6,10 atrás das placas" if len(d["bays"]) > 2 else "idem"
    vv = pr.vista(f"VISTA {v}", origem, esc, titulo=d["titulo"], subtitulo=sub, unidade="cm")
    x0 = d["pil"][0][0]
    for x, b in d["pil"]:
        vv.ret(x - b / 2, -1000, b, Z_TOPO + 1000, "CORTADO")
    vv.linha((x0 - 1500, 0), (d["pil"][-1][0] + 1500, 0), "TERRENO")
    for k, (xa, xb, ba, bb) in enumerate(d["bays"]):
        gate = any(a <= k <= b for a, b in d["portao"])
        if gate:
            vv.ret(xa + ba / 2 + JUNTA, Z_VERGA - 600, xb - xa - (ba + bb) / 2 - 2 * JUNTA, 600, "OCULTA")       # verga escondida
            vv.texto(((xa + xb) / 2, Z_VERGA - 300), "VV", "min", "MIDDLE_CENTER")
            vv.poli([(xa + ba / 2 + 150, 0), (xa + ba / 2 + 150, Z_VERGA - 600), (xb - bb / 2 - 150, Z_VERGA - 600), (xb - bb / 2 - 150, 0)], "EIXO")
            if k == d["portao"][0][0]:
                vv.texto(((d["bays"][d["portao"][0][0]][0] + d["bays"][d["portao"][0][1]][1]) / 2, 2500), "PORTÕES — vão livre 5,50 m; vergas VV-xx 25×60 (+5,50/+6,10) escondidas nas placas", "nota", "MIDDLE_CENTER")
        else:
            vv.ret(xa + JUNTA / 2, Z_VERGA - 600, xb - xa - JUNTA, 600, "OCULTA")                                       # VT escondida
        for (z0, z1) in d["fiadas"]:
            if gate and z0 < Z_VERGA:
                continue
            L = (xb - xa + 400 - JUNTA) if not gate else (xb - xa - (ba + bb) // 2 - 2 * JUNTA)
            xi = xa - 200 + JUNTA / 2 if not gate else xa + ba / 2 + JUNTA
            vv.ret(xi, z0 + JUNTA / 2, L, z1 - z0 - JUNTA, "VISTA")
            if z0 == d["fiadas"][len(d["fiadas"]) // 2][0] or (gate and z0 == Z_VERGA):
                vv.texto(((xa + xb) / 2, z0 + (z1 - z0) / 2), MARCA[(L, z1 - z0)], "min", "MIDDLE_CENTER")
    vv.cota_h([x for x, _ in d["pil"]], -1000, -8)
    vv.cota_v([0, Z_VERGA - 600, Z_VERGA, Z_TOPO], d["pil"][-1][0] + 600, 8, total=False)
    if "nomes" in d:
        for (x, _), n in zip(d["pil"], d["nomes"]):
            vv.texto((x, Z_TOPO + 400), n, "min", "BOTTOM_CENTER")
    return vv


# ================================================================== ND-LET-CM01 rev 01
def prancha_cm():
    n_tot = sum(len(v) for v in PLACAS.values())
    L0, h0 = ordem[0]
    pr = Prancha("A1", dict(cliente="MARQUE ENGENHARIA", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                            conteudo="PLACAS DE FECHAMENTO PROTENDIDAS 125 × 15 — LOCAÇÃO CONFORME R01 (VISTAS A A J), PORTÕES NA LINHA 3, SEÇÃO E LIGAÇÃO COM OS PILARES",
                            desenho="ND-LET-CM01", folha="01/01", fase="PARA APROVAÇÃO", marca="CM-01", qtd=len(PLACAS[ordem[0]]), peso=f(1.25 * 0.15 * L0 / 1000 * 25, 1), volume=f(1.25 * 0.15 * L0 / 1000, 2)))
    pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL")
    pr.revisao("01", "12/10/2026", "LOCAÇÃO E VISTAS CONFORME R01 (A–J); PORTÕES NA LINHA 3 COM VERGAS A +6,10 ESCONDIDAS NO FECHAMENTO")
    Q = pr.quadro
    XC = Q[2] - 190
    pr.ret(Q[0] + 4, Q[3] - 30, Q[0] + 560, Q[3] - 4, "CARIMBO")
    pr.texto(Q[0] + 10, Q[3] - 24, "CM", "grande", "TITULO")
    pr.texto(Q[0] + 50, Q[3] - 24, f"PLACAS DE FECHAMENTO PROTENDIDAS 125 × 15 — {len(ordem)} MARCAS · {n_tot} PLACAS · VISTAS A A J", "titulo", "TITULO")
    pr.texto(Q[0] + 10, Q[3] - 14, "por fora dos pilares (juntas de 10 mm no eixo dos pilares); 4 cord. Ø9,5 CP-190; fixação nos IP-01; nas bays dos portões as placas começam em +6,10 sobre a verga VV-01", "nota", "TEXTO")
    # planta de locação 1:400
    kp = pr.vista("LOCAÇÃO", (Q[0] + 345, Q[3] - 395), 400, titulo="PLANTA DE LOCAÇÃO DAS PLACAS", subtitulo="letras = vistas (como no R01); linha 3 = parede dos portões", unidade="cm")
    for y in Y_LIN:
        kp.linha((M(-1.5), M(y)), (M(41.6), M(y)), "EIXO")
    for x in X_FACH:
        kp.linha((M(x), M(-1.5)), (M(x), M(78.3)), "EIXO")
    for i, y in enumerate(Y_LIN, 1):
        kp.texto((M(-2.2), M(y)), str(i), "min", "MIDDLE_RIGHT")
    for j, x in enumerate(X_FACH):
        kp.texto((M(x), M(78.6)), "ABCDE"[j], "min", "BOTTOM_CENTER")
    # placas (linhas grossas) : perímetro, linha 2, linha 3
    kp.linha((M(-0.3), M(0)), (M(-0.3), M(76.81)), "CORTADO"); kp.linha((M(40.4), M(0)), (M(40.4), M(76.81)), "CORTADO")
    kp.linha((M(0), M(76.81 + 0.3)), (M(40.1), M(76.81 + 0.3)), "CORTADO")
    kp.linha((M(0), M(-0.3)), (M(9.87), M(-0.3)), "CORTADO"); kp.linha((M(29.63), M(-0.3)), (M(40.1), M(-0.3)), "CORTADO")
    kp.linha((M(0), M(10.05)), (M(40.1), M(10.05)), "CORTADO")
    kp.linha((M(0), M(19.705)), (M(9.87), M(19.705)), "CORTADO"); kp.linha((M(29.63), M(19.705)), (M(40.1), M(19.705)), "CORTADO")
    kp.linha((M(9.87), M(19.705)), (M(29.63), M(19.705)), "OCULTA")
    for x, b, n in X_L3:
        kp.ret(M(x) - b / 2, M(19.705) - b / 2, b, b, "CORTADO")
    for x, b, n in X_L2:
        kp.ret(M(x) - b / 2, M(10.05) - 200, b, 400, "CORTADO")
    for i, y in enumerate(Y_LIN):
        kp.ret(M(0) - 300, M(y) - 200, 600, 400, "CORTADO"); kp.ret(M(40.1) - 300, M(y) - 200, 600, 400, "CORTADO")
    for x in X_FACH[1:-1]:
        kp.ret(M(x) - 200, -300, 400, 600, "CORTADO"); kp.ret(M(x) - 200, M(76.81) - 300, 400, 600, "CORTADO")
    for letra, (x, y, rot) in {"A": (20.05, 74.0, 0), "B": (3.0, 55.0, 90), "D": (37.0, 55.0, 90), "C": (20.05, 23.0, 0), "G": (20.05, 13.0, 0), "I": (20.05, 7.0, 0),
                               "E": (3.0, 14.0, 90), "F": (37.0, 14.0, 90), "H": (5.0, 3.0, 0), "J": (35.0, 3.0, 0)}.items():
        kp.circulo((M(x), M(y)), 900, "VISTA"); kp.texto((M(x), M(y)), letra, "nota", "MIDDLE_CENTER")
    kp.texto((M(20.05), M(43)), "pavilhão (lado das vistas B, D, A, C)", "min", "MIDDLE_CENTER")
    kp.texto((M(20.05), M(15.5)), "mezanino (linhas 1–3)", "min", "MIDDLE_CENTER")
    kp.cota_h([M(x) for x in X_FACH], M(-1.5), -6)
    # vistas 1:200
    desenhar_vista(pr, "B", (Q[0] + 340 - M(Y_LIN[3]) / 250, Q[3] - 110), 250)
    desenhar_vista(pr, "C", (Q[0] + 40, Q[3] - 115))
    desenhar_vista(pr, "A", (Q[0] + 40, Q[3] - 215))
    desenhar_vista(pr, "G", (Q[0] + 40, Q[3] - 315))
    desenhar_vista(pr, "E", (Q[0] + 40, Q[3] - 415))
    desenhar_vista(pr, "H", (Q[0] + 30, Q[3] - 515))
    desenhar_vista(pr, "J", (Q[0] + 140 - M(29.63) / 200, Q[3] - 515))

    # seção placa × pilar × viga de travamento (1:20) — a viga fica atrás da placa, entre os pilares
    s = pr.vista("SEÇÃO", (Q[0] + 640, Q[3] - 420), 25, titulo="SEÇÃO TÍPICA — PLACA, PILAR E VIGA DE TRAVAMENTO", subtitulo="VT/VV 25×60 escondida atrás das placas; placa por fora do pilar", unidade="cm")
    s.ret(-E_PL - 50, 0, E_PL, 4000, "CORTADO"); s.hachura([(-E_PL - 50, 0), (-50, 0), (-50, 4000), (-E_PL - 50, 4000)], "AR-CONC", 0.03)
    s.ret(0, 0, 600, 4000, "VISTA")                                                                 # pilar (atrás)
    s.ret(0, 0, 250, 0, "VISTA")
    s.poli([(0, 0), (250, 0), (250, 4000), (0, 4000)], "OCULTA")
    s.ret(-50, 1500 - 600, 250, 600, "CORTADO"); s.hachura([(-50, 900), (200, 900), (200, 1500), (-50, 1500)], "AR-CONC", 0.03)     # VT em corte
    s.chapa(-50 - 9.5, 2400, 9.5, 150); s.chapa(-50 - 9.5, 1150, 9.5, 150)
    s.cota_h([-E_PL - 50, -50, 200, 600], 0, -10, total=False)
    s.cota_v([0, 900, 1500, 2500, 3750], 600, 10, total=False)
    s.chamada((-100, 3300), (-6, 14), "placa CM 125 × 15"); s.chamada((100, 1200), (14, 10), "VT / VV 25×60 (+5,50/+6,10) atrás da placa")
    s.chamada((-55, 2475), (-8, 24), "IP-01 + cantoneira (rev. 00, det. 1)"); s.chamada((400, 3500), (10, 10), "pilar 40×60 (ao fundo)")
    s.texto((275, -600), "nível indicativo: corte na altura +4,00 a +7,75", "min", "MIDDLE_CENTER")
    # tabela de marcas
    y = Q[3] - 6
    linhas = []
    for k in ordem:
        L, h = k
        itens = PLACAS[k]
        vistas = sorted(set(i[0] for i in itens))
        linhas.append([MARCA[k], f"{L/10:.1f}".replace(".", ","), f"{h/10:g}", len(itens), ", ".join(vistas), f(1.25 * 0.15 * L / 1000 * 25 / 10 * (h / 1250), 2)])
    y = pr.tabela(XC, y, f"MARCAS — PLACAS 125 × 15 ({n_tot} placas)", ["MARCA", "L (cm)", "h (cm)", "QT", "VISTAS", "PESO (t)"], linhas, [18, 24, 18, 14, 86, 24], h_lin=5.5)
    mem = [["Vento (q 0,87 kN/m², Cpe 1,0)", "M = 12,7 kN·m por placa (vão 9,65 m)"], ["σ no bordo (P/A ± M/W)", "1,18 ± 2,7 → tração 1,5 ≤ 2,9 MPa"],
           ["Placas sobre a verga (vão ≈ 4,9 m)", "folga ampla"], ["Fixação (4 cantoneiras)", "R = 2,6 kN por ponto"]]
    y = pr.tabela(XC, y - 4, "MEMÓRIA RESUMIDA (NBR 6118 / NBR 6123)", ["VERIFICAÇÃO", "RESULTADO"], mem, [70, 112])
    pr.notas(XC, y - 4, ["Locação e vistas conforme o R01 do cliente (vistas A a J): perímetro, parede da linha 2 (G/I) e parede da linha 3 (C) com 4 portões entre P9, P10, P11, P10 e P12.",
                         "Nas bays dos portões as placas começam em +6,10, sobre a verga VV-01 25×60 (ND-LET-VT01), que fica escondida atrás das placas; vão livre dos portões 5,50 m — confirmar a altura dos portões com o cliente.",
                         "Vigas de travamento VT-01 25×60 em todos os demais vãos, no mesmo nível (+5,50 a +6,10), entre os pilares e atrás das placas: não aparecem pela face externa.",
                         "Vistas E e F (eixos A e E entre as linhas 1 e 4): só as 2 fiadas de cima (docas abertas) — a confirmar; vistas H e J: fachada da linha 1 nas extremidades, centro aberto — a confirmar.",
                         "Placas protendidas 125 × 15 (C40) com 4 cordoalhas Ø9,5; encaixe macho-fêmea; fixação em cada ponta por 2 cantoneiras soldadas ao IP-01 do pilar e ao CH-P1 da placa (detalhe na rev. 00).",
                         "Cotas de concreto em cm, níveis em m. Não medir no desenho. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."], 182)
    avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-CM01")
    print("CM01", len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos", [a for a in avisos if a[0] == "ERRO" or "sobrep" in a[1]][:8])


# ================================================================== ND-LET-VT01 — vigas de travamento e vergas
def prancha_vt():
    VT = []                                                                    # (marca, posição, L c-c − pilares)
    for i in range(1, 8):                                                      # eixos A e E, linhas 2–9
        VT.append((Y_LIN[i + 1] - Y_LIN[i] - 0.40, f"eixos A e E, L{i+1}–L{i+2}"))
    for (xa, ba, _), (xb, bb, _) in zip(X_L2[:-1], X_L2[1:]):
        VT.append((xb - xa - (ba + bb) / 2000, f"linha 2, {xa:.2f}–{xb:.2f}"))
    for (xa, ba, _), (xb, bb, _) in zip(X_L3[:-1], X_L3[1:]):
        VT.append((xb - xa - (ba + bb) / 2000, f"linha 3, {xa:.2f}–{xb:.2f}"))
    agr = {}
    for L, pos in VT:
        agr.setdefault(round(L, 2), []).append(pos)
    lista = sorted(agr.items(), key=lambda t: -t[0])
    MK = {}
    k = 1
    for L, pos in lista:
        verga = any("linha 3" in p and not ("0.00–9.87" in p or "29.63–40.10" in p) for p in pos)
        MK[L] = (f"VV-{k:02d}" if verga else f"VT-{k:02d}")
        k += 1
    L0 = lista[0][0]
    peso = lambda L: 0.25 * 0.60 * L * 25
    pr = Prancha("A1", dict(cliente="MARQUE ENGENHARIA", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                            conteudo="VIGAS DE TRAVAMENTO VT E VERGAS DOS PORTÕES VV (25 × 60, +5,50 A +6,10) — PLANTA, ELEVAÇÃO, SEÇÃO, APOIO E ARMAÇÃO",
                            desenho="ND-LET-VT01", folha="01/01", fase="PARA APROVAÇÃO", marca="VT-01", qtd=len(lista[0][1]) * 2, peso=f(peso(L0), 1), volume=f(0.15 * L0, 2)))
    pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL")
    Q = pr.quadro
    XC = Q[2] - 190
    pr.ret(Q[0] + 4, Q[3] - 30, Q[0] + 560, Q[3] - 4, "CARIMBO")
    pr.texto(Q[0] + 10, Q[3] - 24, "VT / VV", "grande", "TITULO")
    pr.texto(Q[0] + 75, Q[3] - 24, "VIGAS DE TRAVAMENTO E VERGAS 25 × 60 cm — NÍVEL +5,50 / +6,10 — ESCONDIDAS NO FECHAMENTO", "titulo", "TITULO")
    pr.texto(Q[0] + 10, Q[3] - 14, "entre os pilares, atrás das placas; nas bays dos portões (linha 3) a viga é a verga VV, no mesmo nível, deixando 5,50 m livres", "nota", "TEXTO")
    # planta 1:400 no nível +6,10
    v = pr.vista("PLANTA", (Q[0] + 40, Q[3] - 270), 400, titulo="PLANTA — VIGAS DE TRAVAMENTO E VERGAS (NÍVEL +6,10)", subtitulo="VT nos eixos A e E (linhas 2–9) e nas linhas 2 e 3; VV nos portões", unidade="cm")
    for y in Y_LIN:
        v.linha((M(-1.5), M(y)), (M(41.6), M(y)), "EIXO")
    for x in X_FACH:
        v.linha((M(x), M(-1.5)), (M(x), M(78.3)), "EIXO")
    for i, y in enumerate(Y_LIN, 1):
        v.texto((M(-2.2), M(y)), str(i), "min", "MIDDLE_RIGHT")
    for j, x in enumerate(X_FACH):
        v.texto((M(x), M(78.6)), "ABCDE"[j], "min", "BOTTOM_CENTER")
    for i, y in enumerate(Y_LIN):
        v.ret(-300, M(y) - 200, 600, 400, "CORTADO"); v.ret(M(40.1) - 300, M(y) - 200, 600, 400, "CORTADO")
    for x in X_FACH[1:-1]:
        v.ret(M(x) - 200, -300, 400, 600, "CORTADO"); v.ret(M(x) - 200, M(76.81) - 300, 400, 600, "CORTADO")
    for x, b, n in X_L3:
        v.ret(M(x) - b / 2, M(19.705) - b / 2, b, b, "CORTADO")
    for x, b, n in X_L2:
        v.ret(M(x) - b / 2, M(10.05) - 200, b, 400, "CORTADO")
    for i in range(1, 8):
        for xx in (0.0, 40.1):
            L = Y_LIN[i + 1] - Y_LIN[i] - 0.40
            v.ret(M(xx) - 125, M(Y_LIN[i]) + 200, 250, M(L), "VISTA")
            if xx == 0.0:
                v.texto((M(xx) + 400, M((Y_LIN[i] + Y_LIN[i + 1]) / 2)), MK[round(L, 2)], "min", "MIDDLE_LEFT", rot=90)
    for pil, y in ((X_L2, 10.05), (X_L3, 19.705)):
        for (xa, ba, _), (xb, bb, _) in zip(pil[:-1], pil[1:]):
            L = xb - xa - (ba + bb) / 2000
            v.ret(M(xa) + ba / 2, M(y) - 125, M(L), 250, "VISTA")
            v.texto((M((xa + xb) / 2), M(y) + 300), MK[round(L, 2)], "min", "BOTTOM_CENTER")
    v.cota_h([M(x) for x in X_FACH], M(-1.5), -6); v.cota_v([M(y) for y in Y_LIN], M(41.6), 6)
    # elevação da parede da linha 3 (1:200) com portões e vergas
    e = pr.vista("ELEVAÇÃO", (Q[0] + 40, Q[3] - 365), 200, titulo="ELEVAÇÃO — LINHA 3 (PORTÕES): VERGAS VV ESCONDIDAS NAS PLACAS", subtitulo="vista do pavilhão; placas acima de +6,10", unidade="cm")
    for x, b, n in X_L3:
        e.ret(M(x) - b / 2, -1000, b, 11000, "CORTADO"); e.texto((M(x), 10400), n, "min", "BOTTOM_CENTER")
    e.linha((-1500, 0), (M(41.6), 0), "TERRENO")
    for (xa, ba, _), (xb, bb, _) in zip(X_L3[:-1], X_L3[1:]):
        L = xb - xa - (ba + bb) / 2000
        e.ret(M(xa) + ba / 2, Z_VERGA - 600, M(L), 600, "VISTA")
        e.texto((M((xa + xb) / 2), Z_VERGA - 300), MK[round(L, 2)], "min", "MIDDLE_CENTER")
        gate = 9.87 <= xa < 29.63
        z0 = Z_VERGA if gate else 0
        for (fa, fb) in fiadas(z0):
            e.ret(M(xa) + ba / 2 + 5, fa + 5, M(L) - 10, fb - fa - 10, "OCULTA")
        if gate and abs(xa - 9.87) < 0.01:
            e.texto((M(19.75), 2800), "PORTÕES — 4 vãos, 5,50 m livres sob as vergas", "nota", "MIDDLE_CENTER")
    e.cota_h([M(x) for x, _, _ in X_L3], -1000, -8); e.cota_v([0, Z_VERGA - 600, Z_VERGA, 10000], M(40.1) + 600, 8, total=False)
    e.chamada((M(14.96) + 125 + 2000, Z_VERGA), (10, 12), "placas CM a partir de +6,10 (por fora, escondem a verga)")
    # seção 1:10 e apoio (consolo CP-VT) 1:20
    s = pr.vista("SEÇÃO", (Q[0] + 60, Q[3] - 500), 10, titulo="SEÇÃO VT / VV", subtitulo="25 × 60, C40", unidade="cm")
    pts = [(0, 0), (250, 0), (250, 600), (0, 600)]
    s.poli(pts, "CORTADO", fechada=True); s.hachura(pts, "AR-CONC", 0.03)
    s.poli([(30, 30), (220, 30), (220, 570), (30, 570)], "ARM_TRANSV", fechada=True)
    for x in (45, 125, 205):
        s.ponto_barra((x, 45), 12.5); s.ponto_barra((x, 555), 12.5)
    for yy in (220, 380):
        s.ponto_barra((40, yy), 8); s.ponto_barra((210, yy), 8)
    s.cota_h([0, 250], 0, -8); s.cota_v([0, 600], 250, 8)
    s.chamada((205, 555), (12, 8), "N1/N2 — 3 Ø12,5 em cima e embaixo"); s.chamada((210, 380), (12, 0), "N3 pele 2 Ø8/face"); s.chamada((220, 300), (12, -10), "N4 Ø6,3 c/15")
    a = pr.vista("DETALHE 1", (Q[0] + 230, Q[3] - 500), 20, titulo="DETALHE 1 — APOIO DA VT NO PILAR", subtitulo="consolo CP-VT 25×20×30/20 + pino PN-1 Ø20; neoprene 200×150×10", unidade="cm")
    a.ret(-600, -500, 600, 1700, "VISTA")
    a.poli([(0, 0), (200, 0), (200, 100), (0, 300)], "VISTA")
    a.ret(250 - 10, 100, 20, 400, "OCULTA"); a.chapa(25, 300, 150, 10)
    a.ret(25, 310, 1000, 600, "VISTA"); a.interrupcao((1025, 310), (1025, 910))
    a.cota_h([-600, 0, 200, 1025], -500, -8, total=False); a.cota_v([0, 300, 910], 1025, 8, total=False)
    a.chamada((100, 150), (14, -12), "CP-VT consolo 25 larg × 20 proj × 30/20 — nas faces B e D dos pilares laterais (a +5,20)")
    a.chamada((250, 600), (14, 10), "PN-1 Ø20 no TB-1 Ø50 da viga (graute numa ponta)"); a.chamada((-300, 1000), (-10, 8), "pilar")
    # tabelas
    y = Q[3] - 6
    linhas = [[MK[L], "; ".join(sorted(set(p.split(",")[0] for p in pos))), len(pos) * (2 if "eixos" in pos[0] else 1), f"{L*100:.0f}", f(peso(L) / 10, 2)] for L, pos in lista]
    y = pr.tabela(XC, y, "MARCAS — VIGAS 25×60 (+5,50 a +6,10)", ["MARCA", "POSIÇÃO", "QT", "L (cm)", "PESO (t)"], linhas, [18, 84, 12, 22, 24], h_lin=5.5)
    ins = [["TB-1", "Tubo Ø50×3,0 L=300 a prumo", 2, "a 12,5 das pontas"], ["CH-A3", "Chapa 200×150×9,5 + 2 grapas Ø10", 2, "fundo das pontas"], ["AL-1", "Laço de cordoalha Ø12,7", 2, "a L/5 das pontas"]]
    y = pr.tabela(XC, y - 4, "INSERTOS POR VIGA — mm", ["MARCA", "DESCRIÇÃO", "QT", "POSIÇÃO"], ins, [16, 100, 10, 56])
    mem = [["Função", "travamento dos pilares a meia altura (λ) e apoio das placas/portões"], ["Md (pp + placas 3 fiadas acima nas vergas)", "≈ 45 kN·m (vão 4,9 m)"],
           ["As adotada", "3 Ø12,5 + 3 Ø12,5 (simétrica) ≥ 0,15 %"], ["Cortante", "Ø6,3 c/15 ≥ mínimo"]]
    y = pr.tabela(XC, y - 4, "MEMÓRIA RESUMIDA (NBR 6118:2023)", ["VERIFICAÇÃO", "RESULTADO"], mem, [70, 112])
    y = pr.legenda_armadura(XC, y - 4, False)
    pr.notas(XC, y - 4, ["Todas as vigas de travamento e vergas no mesmo nível: fundo +5,50, topo +6,10, escondidas atrás das placas (face externa da viga rente à face do pilar).",
                         "Nas bays dos portões (linha 3, entre P9 e P12) a viga é a verga VV: nada abaixo de +5,50 — vão livre dos portões; confirmar com o cliente a altura dos portões.",
                         "Apoio em consolos CP-VT nas faces laterais dos pilares (a emitir nas pranchas dos pilares como revisão) com pino PN-1 e neoprene; graute numa ponta só.",
                         "Pilares dos portões P9, P11, P12 (40×40) e P10 (25×25) e P6/P7 do anexo: pranchas a emitir após confirmação da arquitetura dos portões.",
                         "Cotas de concreto em cm, níveis em m. Não medir no desenho. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."], 182)
    avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-VT01")
    print("VT01", len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos", [a for a in avisos if a[0] == "ERRO" or "sobrep" in a[1]][:8])


if __name__ == "__main__":
    prancha_cm()
    prancha_vt()
