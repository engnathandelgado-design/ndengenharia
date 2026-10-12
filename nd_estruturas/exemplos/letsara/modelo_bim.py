"""Letsara — modelo BIM (IFC + página 3D) a partir das definições de projeto. Revisão de 12/10/2026 (tarde).

Rodar: PYTHONPATH=. python exemplos/letsara/modelo_bim.py [pasta_de_saida]
Saída (em saidas/, fora do git): letsara.ifc e letsara_3d.html (publicar a página como artefato para ver no celular).

Geometria = a mesma da checagem de ligações (ligacoes.json) e do modelo global:
- eixos Y (linhas 1 a 9) e X (A a E) do R01 como usados nos cálculos;
- cobertura baixada para ficar escondida na platibanda (+10,00) com 10 cm de folga no lado alto;
- TS-01 com dentes Gerber nas duas pontas, apoiadas em consolos (pilares laterais, pilares centrais e I110);
- I110 com consolos dos dois lados nas linhas das TS-01 (diafragma maciço);
- terças Ue 300 nas posições da TS-01 (c/1,579), mezanino com laje alveolar h20 + 5 sobre vigas I90 com dentes.
Unidades: m.
"""
import itertools
import json
import math
import sys
from pathlib import Path

from nd_estruturas.bim import (ModeloBIM, PerfilI, PerfilRetangular, gravar_ifc, gravar_visualizador,
                               ler_malha_ifc, quantitativos)

AQ = Path(__file__).parent
LG = json.loads((AQ / "ligacoes.json").read_text(encoding="utf-8"))

# ------------------------------------------------------------------ parâmetros da obra (iguais aos cálculos)
LARG = 40.10
Y_LIN = [0.0, 10.05, 19.705, 29.36, 38.865, 48.445, 58.025, 67.605, 76.81]
COMP = Y_LIN[-1]
X_FACH = [0.0, 9.87, 20.05, 29.63, LARG]
X_C = 20.05
TOPO_PLAT, Z_CALICE = 10.00, -1.00
INCL = 0.03
Z0 = LG["Z0_TS"]                                   # fundo da TS-01 no eixo A
C3 = math.cos(math.atan(INCL))
zf = lambda x: Z0 + INCL * x                       # fundo (altura cheia) da TS-01 em x
H_TS, H_DENTE, L_DENTE = 0.90, 0.45, 0.30
L_TS = LG["L_TS"] * C3                             # projeção horizontal entre pontas
PONTAS = [(0.325, 0.325 + L_TS), (2 * X_C - (0.325 + L_TS), 2 * X_C - 0.325)]
Z_I110_TOPO, H_I110 = 8.88, 1.10
Y_P13 = Y_LIN[5] + 4.6
CENTRAIS = [("P8A", Y_LIN[1]), ("P11", Y_LIN[3]), ("P13", Y_P13)]
I110_TRECHOS = [("V407", Y_LIN[1], Y_LIN[3]), ("V406", Y_LIN[3], Y_P13), ("V405", Y_P13, Y_LIN[8])]   # V405 vai até a linha 9 (P14)
NIVEIS_MEZ, H_LAJE = [3.15, 6.55], 0.20 + 0.05

I90 = PerfilI(h=0.90, b=0.40, tw=0.15, tf=0.15, nome="I90")
I110 = PerfilI(h=1.10, b=0.40, tw=0.15, tf=0.25, nome="I110")
I70 = PerfilI(h=0.70, b=0.40, tw=0.15, tf=0.15, nome="I70")
VB = PerfilRetangular(0.15, 0.70, "VB 15x70")
TERCA = PerfilRetangular(0.085, 0.30, "Ue300x85x25x3,00 (envelope)")
LAJE = PerfilRetangular(1.24, H_LAJE, "LA h20+5")
TELHA = PerfilRetangular(1.00, 0.03, "telha 0,5 + PIR 30")
H_PLACA, E_PLACA, N_FIADAS = 1.25, 0.10, 8
PLACA = PerfilRetangular(E_PLACA, H_PLACA, "Placa e=10 h=125")


def montar() -> ModeloBIM:
    m = ModeloBIM("Letsara — Pavilhão pré-moldado", obra="Obra Letsara (Marque Engenharia)")

    # 1. pilares laterais (60 na direção X) com consolos CP-TS para os dentes da TS-01
    for i, y in enumerate(Y_LIN, start=1):
        m.pilar(f"P1-L{i}", 0.0, y, 0.60, 0.40, Z_CALICE, TOPO_PLAT, obs="60 na direção X; platibanda até +10,00")
        m.pilar(f"P2-L{i}", LARG, y, 0.60, 0.40, Z_CALICE, TOPO_PLAT, obs="60 na direção X; platibanda até +10,00")
        if 2 <= i <= 8:
            for x_ap, xc in ((0.475, 0.45), (LARG - 0.475, LARG - 0.45)):
                m.bloco("consolo", f"CP-TS L{i}", (xc, y, zf(x_ap) + H_DENTE * C3 - 0.01), 0.30, 0.40, 0.45, "Consolos")

    # pilares das fachadas frente e fundo, centrais e do mezanino
    for j, x in enumerate(X_FACH[1:-1]):
        m.pilar(["P3", "P4", "P5"][j], x, 0.0, 0.40, 0.60, Z_CALICE, TOPO_PLAT, obs="60 ⊥ fachada")
        m.pilar(["P14", "P15", "P16"][j], x, COMP, 0.40, 0.60, Z_CALICE, TOPO_PLAT, obs="60 ⊥ fachada")
    for marca, y in CENTRAIS:
        m.pilar(marca, X_C, y, 0.50, 0.50, Z_CALICE, Z_I110_TOPO, obs="50×50; apoio I110 / TS-01")
    for marca, x in (("P8", 9.87), ("P8B", 29.63)):
        m.pilar(marca, x, Y_LIN[1], 0.60, 0.40, Z_CALICE, NIVEIS_MEZ[1], obs="mezanino")

    # 2. vigas centrais I110 (dentes nas pontas) e consolos CV-TS nas linhas das TS-01
    zc = Z_I110_TOPO - H_I110 / 2
    for marca, ya, yb in I110_TRECHOS:
        m.linear("viga", marca, I110, (X_C, ya + 0.275, zc), (X_C, yb - 0.275, zc), "Vigas centrais I110",
                 obs="protendida, 24 cord. Ø12,7 (10 isoladas nas pontas); dente 660")
    # consolo CP-I110 na face interna do P14 (linha 9, eixo C) para a ponta da V405
    m.bloco("consolo", "CP-I110 (P14)", (X_C, COMP - 0.30 - 0.20, 8.19 - 0.01), 0.40, 0.40, 0.50, "Consolos")
    for i in range(2, 9):
        y = Y_LIN[i - 1]
        if any(abs(y - yy) < 0.01 for _, yy in CENTRAIS):
            for xc, x_ap in ((X_C - 0.40, PONTAS[0][1] - 0.15), (X_C + 0.40, PONTAS[1][0] + 0.15)):
                m.bloco("consolo", f"CP-TS central L{i}", (xc, y, zf(x_ap) + H_DENTE * C3 - 0.01), 0.30, 0.40, 0.45, "Consolos")
        else:
            for xc, x_ap in ((X_C - 0.375, PONTAS[0][1] - 0.15), (X_C + 0.375, PONTAS[1][0] + 0.15)):
                m.bloco("consolo", f"CV-TS L{i}", (xc, y, zf(x_ap) + H_DENTE * C3 - 0.01), 0.35, 0.40, 0.45, "Consolos")

    # 3. TS-01: corpo I90 inclinado + dentes (blocos) nas pontas
    for i in range(2, 9):
        y = Y_LIN[i - 1]
        for lado, (xa, xb) in zip("ab", PONTAS):
            a, b = xa + L_DENTE, xb - L_DENTE
            m.linear("viga", f"TS-01 L{i}{lado}", I90, (a, y, zf(a) + H_TS / 2), (b, y, zf(b) + H_TS / 2),
                     "Vigas I90 de cobertura", obs="inclinada 3 %, dentes 450×300")
            for xd in (xa + L_DENTE / 2, xb - L_DENTE / 2):
                m.bloco("viga", f"dente TS-01 L{i}{lado}", (xd, y, zf(xd) + H_TS), L_DENTE, 0.40, H_TS - H_DENTE,
                        "Vigas I90 de cobertura")

    # vigas de borda das fachadas 1 e 9 (acompanham o caimento)
    for y in (0.0, COMP):
        for xa, xb in itertools.pairwise(X_FACH):
            a, b = xa + 0.25, xb - 0.25
            m.linear("viga", "VB-01", VB, (a, y, zf(a) + 0.35), (b, y, zf(b) + 0.35), "Vigas de borda")

    # 4. terças Ue 300 nas posições da TS-01 e telha
    for xa, _ in PONTAS:
        for s in LG["s_tercas"]:
            x = xa + s * C3 - 0.027
            zt = zf(x) + H_TS + 0.0125 + TERCA.h / 2
            for k in range(len(Y_LIN) - 1):
                m.linear("terca", "Ue300", TERCA, (x, Y_LIN[k] + 0.005, zt), (x, Y_LIN[k + 1] - 0.005, zt),
                         "Terças metálicas", material="aco")
    for k in range(int(COMP // 1.0)):
        y = 0.5 + k * 1.0
        z0, z1 = zf(0.30) + H_TS + 0.0125 + 0.30 + 0.015, zf(LARG - 0.30) + H_TS + 0.0125 + 0.30 + 0.015
        m.linear("placa", "telha", TELHA, (0.30, y, z0), (LARG - 0.30, y, z1), "Telhas", material="aco")

    # 5. mezanino (linhas 1–2): vigas I70 com dentes e laje alveolar h20 + 5
    for nivel in NIVEIS_MEZ:
        zv = nivel - H_LAJE - I90.h / 2
        for y in (Y_LIN[0], Y_LIN[1]):
            for xa, xb in itertools.pairwise(X_FACH):
                m.linear("viga", f"VM {nivel:+.2f}", I90, (xa + 0.325, y, zv), (xb - 0.325, y, zv),
                         "Vigas de mezanino", obs="I90 protendida com dentes Gerber 45×30 (MEF FS 1,14), capa como 2º estágio")
        for k in range(int((LARG - 0.60) // 1.25)):
            x = 0.925 + k * 1.25
            m.linear("laje", f"LA {nivel:+.2f}", LAJE, (x, Y_LIN[0] + 0.20, nivel - H_LAJE / 2),
                     (x, Y_LIN[1] - 0.20, nivel - H_LAJE / 2), "Laje alveolar")

    # 6. placas de fechamento conforme a locação do R01 (vistas A–J): perímetro (eixos A/E nas linhas 4–9 inteiros,
    #    linhas 1–4 só as 2 fiadas de cima = docas), fachada 9 inteira, fachada 1 só nas extremidades (A–B e D–E),
    #    parede da linha 2 inteira e parede da linha 3 com 4 portões (placas só acima de +6,10)
    E_PL, Z_VERGA = 0.15, 6.25
    def fiadas(z0=0.0):
        z = z0
        while z + 1.0 < TOPO_PLAT:
            yield z + H_PLACA / 2
            z += H_PLACA
    X_L3 = [0.0, 9.87, 14.96, 20.05, 25.14, 29.63, LARG]                   # P1, P9, P10, P11, P10, P12, P2
    X_L2 = [0.0, 9.87, 20.05, 29.63, 36.30, LARG]                          # P1, P8, P8A, P8B, P6, P2
    for x, nome in ((-0.30 - E_PL / 2 - 0.05, "CM eixo A"), (LARG + 0.30 + E_PL / 2 + 0.05, "CM eixo E")):
        for i in range(len(Y_LIN) - 1):
            z0 = 0.0 if i >= 3 else 7.50                                   # linhas 1–4: docas, só as 2 fiadas de cima
            for z in fiadas(z0):
                m.linear("placa", nome, PLACA, (x, Y_LIN[i], z), (x, Y_LIN[i + 1], z), "Placas de fechamento")
    for z in fiadas():
        for xa, xb in itertools.pairwise(X_FACH):                            # fachada linha 9 inteira
            m.linear("placa", "CM linha 9", PLACA, (xa - 0.40 if xa == 0 else xa, COMP + 0.30 + E_PL / 2, z), (xb + 0.40 if xb == LARG else xb, COMP + 0.30 + E_PL / 2, z), "Placas de fechamento")
        for xa, xb in ((-0.40, 9.87), (29.63, LARG + 0.40)):                 # fachada linha 1: só A–B e D–E (vistas H e J)
            m.linear("placa", "CM linha 1", PLACA, (xa, -0.30 - E_PL / 2, z), (xb, -0.30 - E_PL / 2, z), "Placas de fechamento")
        for xa, xb in itertools.pairwise(X_L2):                              # parede da linha 2 (vistas G/I)
            m.linear("placa", "CM linha 2", PLACA, (xa, Y_LIN[1] + 0.20 + E_PL / 2, z), (xb, Y_LIN[1] + 0.20 + E_PL / 2, z), "Placas de fechamento")
    for k, (xa, xb) in enumerate(itertools.pairwise(X_L3)):                 # parede da linha 3 (vista C): portões nas 4 bays centrais
        gate = 1 <= k <= 4
        for z in fiadas(Z_VERGA if gate else 0.0):
            m.linear("placa", "CM linha 3" + (" (sobre o portão)" if gate else ""), PLACA, (xa, Y_LIN[2] + 0.20 + E_PL / 2, z), (xb, Y_LIN[2] + 0.20 + E_PL / 2, z), "Placas de fechamento")
    # pilares dos portões (linha 3) e do anexo (linha 2), indicativos
    for x, b in ((9.87, 0.40), (14.96, 0.25), (20.05, 0.40), (25.14, 0.25), (29.63, 0.40)):
        m.pilar(f"P-portão {x:.2f}", x, Y_LIN[2], b, b, Z_CALICE, 7.0, obs="pilar dos portões (R01: P9/P10/P11/P12), topo a confirmar")
    m.pilar("P6", 36.30, Y_LIN[1], 0.25, 0.40, Z_CALICE, 7.0, obs="anexo (R01), a confirmar")
    # vigas de travamento VT e vergas VV 25×60 (+5,50 a +6,10), atrás das placas
    VT = PerfilRetangular(0.25, 0.60, "VT 25x60")
    for i in range(1, 8):
        for x in (0.0, LARG):
            m.linear("viga", f"VT L{i+1}-L{i+2}", VT, (x, Y_LIN[i] + 0.20, Z_VERGA + 0.30), (x, Y_LIN[i + 1] - 0.20, Z_VERGA + 0.30), "Vigas de travamento VT/VV")
    for xs, y in ((X_L2, Y_LIN[1]), (X_L3, Y_LIN[2])):
        for k, (xa, xb) in enumerate(itertools.pairwise(xs)):
            nome = "VV (verga do portão)" if (y == Y_LIN[2] and 1 <= k <= 4) else "VT"
            m.linear("viga", nome, VT, (xa + 0.20, y, Z_VERGA + 0.30), (xb - 0.20, y, Z_VERGA + 0.30), "Vigas de travamento VT/VV")

    # 7. insertos metálicos e conexões (para conferir no 3D o que está nas pranchas)
    INS = "Insertos metálicos"
    PIN = "Pinos, tubos e neoprenes"
    for i in range(2, 9):                                                   # TS-01: TB-1 + PN-1 + NEO-1 em cada ponta (28 apoios)
        y = Y_LIN[i - 1]
        for xp in LG["X_PINO"]:
            z_as = zf(xp) + H_DENTE * C3 - 0.01
            m.bloco("inserto", "PN-1 pino Ø20 L=700", (xp, y, z_as + 0.40), 0.02, 0.02, 0.70, PIN)
            m.bloco("inserto", "TB-1 tubo Ø50×3,0 L=450 (no dente)", (xp, y, z_as + 0.45), 0.05, 0.05, 0.45, PIN)
            m.bloco("inserto", "NEO-1 300×150×10", (xp, y, z_as + 0.01), 0.30, 0.15, 0.01, PIN)
            m.bloco("inserto", "CH-A1 300×150×12,5 (fundo do dente)", (xp, y, z_as + 0.0225), 0.30, 0.15, 0.0125, INS)
    for i in range(2, 9):                                                   # CH-T1/T2 no topo e CH-MF no fundo das TS-01; AL-1
        y = Y_LIN[i - 1]
        for xa, _ in PONTAS:
            for k, s_ in enumerate(LG["s_tercas"]):
                x = xa + s_ * C3 - 0.027
                no = k % 2 == 0
                m.bloco("inserto", "CH-T2 300×200×12,5 (nó do contraventamento)" if no else "CH-T1 150×150×12,5", (x, y, zf(x) + H_TS + 0.0125),
                        0.30 if no else 0.15, 0.20 if no else 0.15, 0.0125, INS)
                if 0 < k < len(LG["s_tercas"]) - 1:
                    m.bloco("inserto", "CH-MF 150×360×12,5 (mão-francesa, fundo)", (x, y, zf(x)), 0.15, 0.36, 0.0125, INS)
            for s_ in LG["alcas"]:
                x = xa + s_ * C3
                m.bloco("inserto", "AL-1 alça cordoalha Ø12,7", (x, y, zf(x) + H_TS + 0.14), 0.12, 0.02, 0.14, INS)
    for i, y in enumerate(Y_LIN, start=1):                                  # IP-01 nas faces externas dos pilares laterais (8 fiadas)
        for k in range(N_FIADAS):
            z = 1.25 * (k + 1) - 0.10
            m.bloco("inserto", "IP-01 150×150×9,5 + 2 pinos Ø12,5", (-0.30 - 0.00475, y, z + 0.075), 0.0095, 0.15, 0.15, INS)
            m.bloco("inserto", "IP-01 150×150×9,5 + 2 pinos Ø12,5", (LARG + 0.30 + 0.00475, y, z + 0.075), 0.0095, 0.15, 0.15, INS)
    for x in X_FACH[1:-1]:                                                  # IP-01 nos pilares de fachada (faces y− / y+)
        for k in range(N_FIADAS):
            z = 1.25 * (k + 1) - 0.10
            m.bloco("inserto", "IP-01 150×150×9,5 + 2 pinos Ø12,5", (x, -0.30 - 0.00475, z + 0.075), 0.15, 0.0095, 0.15, INS)
            m.bloco("inserto", "IP-01 150×150×9,5 + 2 pinos Ø12,5", (x, COMP + 0.30 + 0.00475, z + 0.075), 0.15, 0.0095, 0.15, INS)
    # consolos CP-VB (fachadas) e CP-MEZ (linhas 1–2, dois níveis) com pinos
    for y in (0.0, COMP):
        for x in X_FACH:
            for sg in ((1,) if x == 0 else (-1,) if x == LARG else (-1, 1)):
                xc = x + sg * (0.20 + 0.15)
                m.bloco("consolo", "CP-VB 30×40×35/20", (xc, y, zf(x) - 0.01), 0.30, 0.40, 0.35, "Consolos")
                m.bloco("inserto", "PN-1 pino Ø20 (VB-01)", (xc, y, zf(x) + 0.39), 0.02, 0.02, 0.70, PIN)
    for nivel in NIVEIS_MEZ:
        z_as = nivel - H_LAJE - 0.45                                        # VM I90 com dente 45: assento = nível − laje − capa − dente
        for y in (Y_LIN[0], Y_LIN[1]):
            for x in X_FACH:
                for sg in ((1,) if x == 0 else (-1,) if x == LARG else (-1, 1)):
                    xc = x + sg * (0.30 + 0.15)
                    m.bloco("consolo", "CP-MEZ 30×40×35/20", (xc, y, z_as - 0.01), 0.30, 0.40, 0.35, "Consolos")
                    m.bloco("inserto", "PN-1 pino Ø20 (VM)", (xc, y, z_as + 0.39), 0.02, 0.02, 0.70, PIN)
                    m.bloco("inserto", "NEO 300×150×10", (xc, y, z_as + 0.01), 0.15, 0.30, 0.01, PIN)

    # 8. piso e fundações (indicativos): piso de concreto 15 cm e blocos de fundação com cálice sob cada pilar
    m.linear("laje", "PISO e=15 (indicativo)", PerfilRetangular(LARG + 1.0, 0.15), (LARG / 2, -0.5, -0.075), (LARG / 2, COMP + 0.5, -0.075), "Piso e fundações")
    for peca in list(m.pecas):
        if peca.tipo == "pilar":
            x, y, _ = peca.p0
            bx, by = peca.perfil.b + 0.9, peca.perfil.h + 0.9
            m.bloco("fundacao", f"BLOCO/CÁLICE {peca.marca} (indicativo)", (x, y, -1.0 + 0.0), max(bx, 1.5), max(by, 1.5), 1.2, "Piso e fundações")

    pl = LG["platibanda"]
    m.pendente(f"Cobertura escondida: telha junto ao P2 em +{pl['telha_P2']:.3f}, {pl['folga_P2_mm']} mm abaixo da platibanda +10,00; "
               f"junto ao P1 em +{pl['telha_P1']:.3f}.")
    m.pendente("! Laje alveolar h20 + 5 com 500 kgf/m² em 9,75 m NÃO passa com 7 Ø12,7 (seção genérica): ELU 209 > 192 kN·m "
               "por painel; descompressão só até 9,05 m. Confirmar com a tabela do fabricante ou manter h26,5 + 5.")
    m.pendente("Vigas do mezanino em I90 com dentes 45×30 (dente da I70 reprovado no MEF): assentos CP-MEZ +2,45 / +5,85; pé-direito livre sob a viga = nível − 1,15 m.")
    m.pendente("Comprimento entre fachadas adotado nos cálculos: 76,81 m (eixos 1–9). Conferir com o R01 (havia 79,75 em outro registro).")
    m.pendente("Terças, laje, consolos e dentes como envelope; contraventamento e correntes não modelados no 3D.")
    m.pendente("Placas conforme a locação do R01 (vistas A–J); vistas E/F (docas) e centro da fachada 1 sem placas — a confirmar; VT/VV 25×60 de +6,25 a +6,85 com dentes Gerber nos consolos CP-VT; altura livre dos portões 6,25 m.")
    cx = json.loads((AQ / "conexoes.json").read_text(encoding="utf-8")) if (AQ / "conexoes.json").exists() else []
    for c in cx:
        if not c["ok"] or c["obs"].startswith("!"):
            m.pendente("! " + f"{c['peca_a']} × {c['peca_b']}: {c['obs'].lstrip('! ')}")
    return m


if __name__ == "__main__":
    saida = Path(sys.argv[1] if len(sys.argv) > 1 else AQ / "saidas")
    saida.mkdir(parents=True, exist_ok=True)
    modelo = montar()
    q = quantitativos(modelo)
    ifc = gravar_ifc(modelo, saida / "letsara.ifc")
    malha = ler_malha_ifc(ifc)
    pranchas = []
    pasta_pr = Path("/home/claude/letsara/pranchas")
    if pasta_pr.exists():
        import base64, io
        import pymupdf
        LISTA = [("ND-LET-LOC01", "locação de pilares e vigas"), ("ND-LET-CT01", "cortes da estrutura"), ("ND-LET-MON01", "montagem da cobertura"), ("ND-LET-MON02", "montagem do mezanino"),
                 ("ND-LET-PIL-A01", "pilar PL-01 armado (opção A)"), ("ND-LET-PIL-P01", "pilar PL-01 protendido (opção B)"), ("ND-LET-PC01", "pilares centrais PC-01/02 50×50"),
                 ("ND-LET-PM01", "pilares do mezanino PM-01"), ("ND-LET-TS01-COB01-rev01", "TS-01 fôrma, armação, chaparia; cobertura metálica COB01 (enterçamento, ST-1, mão-francesa) e COB02 (correntes, diagonais)"),
                 ("ND-LET-I110", "vigas centrais I110 V405/406/407"), ("ND-LET-VB01", "vigas de borda VB-01 a VB-04"), ("ND-LET-VM01", "vigas do mezanino VM-01 a VM-04"),
                 ("ND-LET-LA01", "lajes alveolares do mezanino"), ("ND-LET-CM01", "placas de fechamento (vistas A–J, portões)"), ("ND-LET-VT01", "vigas de travamento e vergas 25×60 (+5,50/+6,10)")]
        for nome, desc in LISTA:
            arq = pasta_pr / f"{nome}.pdf"
            if not arq.exists():
                continue
            doc = pymupdf.open(arq)
            for k, pg in enumerate(doc):
                pix = pg.get_pixmap(dpi=int(1800 / pg.rect.width * 72))
                img = pix.tobytes("jpeg", jpg_quality=72)
                pranchas.append(dict(nome=nome + (f" ({k + 1}/{len(doc)})" if len(doc) > 1 else ""), desc=desc,
                                     img="data:image/jpeg;base64," + base64.b64encode(img).decode()))
    cx = json.loads((AQ / "conexoes.json").read_text(encoding="utf-8")) if (AQ / "conexoes.json").exists() else []
    gravar_visualizador(malha, saida / "letsara_3d.html", "Letsara · modelo estrutural e projetos",
                        "Pavilhão pré-moldado 40,10 × 76,81 m · Marque Engenharia · cobertura escondida na platibanda · pranchas e conferência de insertos",
                        pendencias=modelo.pendencias, quant=q, ocultas=("Placas de fechamento", "Telhas", "Piso e fundações"), pranchas=pranchas, conexoes=cx)
    for g, d in q.items():
        print(f"{g:26s} {d['pecas']:4d} peças  {d['volume_m3']:8.1f} m³")
    print("pendências:", len(modelo.pendencias), "->", saida)
