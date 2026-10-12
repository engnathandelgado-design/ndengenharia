"""Letsara — modelo BIM (IFC + página 3D) a partir das definições de projeto. Revisão de 12/10/2026 (tarde).

Rodar: PYTHONPATH=. python exemplos/letsara/modelo_bim.py [pasta_de_saida]
Saída (em saidas/, fora do git): letsara.ifc e letsara_3d.html (publicar a página como artefato para ver no celular).

Geometria = a mesma da checagem de ligações (ligacoes.json) e do modelo global:
- eixos Y (linhas 1 a 9) e X (A a E) do R01 como usados nos cálculos;
- cobertura baixada para ficar escondida na platibanda (+10,00) com 10 cm de folga no lado alto;
- TS-01 com dentes Gerber nas duas pontas, apoiadas em consolos (pilares laterais, pilares centrais e I110);
- I110 com consolos dos dois lados nas linhas das TS-01 (diafragma maciço);
- terças Ue 300 nas posições da TS-01 (c/1,579), mezanino com laje alveolar h20 + 5 sobre vigas I70.
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
I110_TRECHOS = [("V407", Y_LIN[1], Y_LIN[3]), ("V406", Y_LIN[3], Y_P13), ("V405", Y_P13, Y_LIN[7])]
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
        zv = nivel - H_LAJE - I70.h / 2
        for y in (Y_LIN[0], Y_LIN[1]):
            for xa, xb in itertools.pairwise(X_FACH):
                m.linear("viga", f"VM {nivel:+.2f}", I70, (xa + 0.325, y, zv), (xb - 0.325, y, zv),
                         "Vigas de mezanino", obs="I70 protendida, dente 425 + 2º estágio")
        for k in range(int((LARG - 0.60) // 1.25)):
            x = 0.925 + k * 1.25
            m.linear("laje", f"LA {nivel:+.2f}", LAJE, (x, Y_LIN[0] + 0.20, nivel - H_LAJE / 2),
                     (x, Y_LIN[1] - 0.20, nivel - H_LAJE / 2), "Laje alveolar")

    # 6. placas de fechamento por fora das faces dos pilares (8 fiadas de 1,25 m = +10,00)
    for k in range(N_FIADAS):
        z = k * H_PLACA + H_PLACA / 2
        for x, nome in ((-0.30 - E_PLACA / 2 - 0.05, "PL-A"), (LARG + 0.30 + E_PLACA / 2 + 0.05, "PL-E")):
            for i in range(len(Y_LIN) - 1):
                m.linear("placa", nome, PLACA, (x, Y_LIN[i], z), (x, Y_LIN[i + 1], z), "Placas de fechamento")
        for y, nome in ((-0.30 - E_PLACA / 2, "PL-1"), (COMP + 0.30 + E_PLACA / 2, "PL-9")):
            for xa, xb in itertools.pairwise(X_FACH):
                a = xa - 0.40 if xa == 0 else xa
                b = xb + 0.40 if xb == LARG else xb
                m.linear("placa", nome, PLACA, (a, y, z), (b, y, z), "Placas de fechamento")

    pl = LG["platibanda"]
    m.pendente(f"Cobertura escondida: telha junto ao P2 em +{pl['telha_P2']:.3f}, {pl['folga_P2_mm']} mm abaixo da platibanda +10,00; "
               f"junto ao P1 em +{pl['telha_P1']:.3f}.")
    m.pendente("! Laje alveolar h20 + 5 com 500 kgf/m² em 9,75 m NÃO passa com 7 Ø12,7 (seção genérica): ELU 209 > 192 kN·m "
               "por painel; descompressão só até 9,05 m. Confirmar com a tabela do fabricante ou manter h26,5 + 5.")
    m.pendente("Vigas do mezanino I70 (10 cord. Ø12,7) passam na flexão; dente de 425 em verificação no MEF.")
    m.pendente("Comprimento entre fachadas adotado nos cálculos: 76,81 m (eixos 1–9). Conferir com o R01 (havia 79,75 em outro registro).")
    m.pendente("Terças, laje, consolos e dentes como envelope; contraventamento e correntes não modelados no 3D.")
    return m


if __name__ == "__main__":
    saida = Path(sys.argv[1] if len(sys.argv) > 1 else AQ / "saidas")
    saida.mkdir(parents=True, exist_ok=True)
    modelo = montar()
    q = quantitativos(modelo)
    ifc = gravar_ifc(modelo, saida / "letsara.ifc")
    malha = ler_malha_ifc(ifc)
    gravar_visualizador(malha, saida / "letsara_3d.html", "Letsara · modelo estrutural",
                        "Pavilhão pré-moldado 40,10 × 76,81 m · Marque Engenharia · cobertura escondida na platibanda",
                        pendencias=modelo.pendencias, quant=q, ocultas=("Placas de fechamento", "Telhas"))
    for g, d in q.items():
        print(f"{g:26s} {d['pecas']:4d} peças  {d['volume_m3']:8.1f} m³")
    print("pendências:", len(modelo.pendencias), "->", saida)
