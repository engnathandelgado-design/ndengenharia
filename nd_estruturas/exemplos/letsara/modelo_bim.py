"""Letsara — modelo BIM (IFC + página 3D) a partir das definições de projeto.

Rodar: python exemplos/letsara/modelo_bim.py [pasta_de_saida]
Saída (em saidas/, fora do git): letsara.ifc e letsara_3d.html (publicar a página como artefato para ver no celular).

Fonte: documento de controle da obra (Drive, pasta "Obra Letsara — Marque Engenharia"), rodadas
1 e 1b de pré-dimensionamento e prancha de montagem da cobertura (12/10/2026).
Eixos: X na largura (0 = eixo A, lado baixo / P1; 40,10 = eixo E, lado alto / P2),
Y no comprimento (linhas 1 a 9), Z a partir do piso acabado. Unidades: m.

Ao fechar o projeto, atualizar aqui os parâmetros definitivos (níveis, seções, posição de
P13, pilares da parede C) e rodar de novo: IFC e 3D saem do mesmo modelo.
"""
import itertools
import sys
from pathlib import Path

import numpy as np

from nd_estruturas.bim import (
    ModeloBIM,
    PerfilI,
    PerfilRetangular,
    gravar_ifc,
    gravar_visualizador,
    ler_malha_ifc,
    quantitativos,
)

# ------------------------------------------------------------------ parâmetros da obra
LARG, COMP, N_LIN = 40.10, 79.75, 9
DY = COMP / (N_LIN - 1)                       # ≈ 9,969 m
Y_LIN = [i * DY for i in range(N_LIN)]
X_FACH = [0.0, 10.025, 20.05, 30.075, LARG]   # pilares das fachadas frente/fundo
X_C = 20.05                                   # eixo central (C)
TOPO_PLAT, Z_CALICE = 10.00, -1.00
INCL, Z_CONS_A = 0.03, 8.08                   # água única 3 %; consolo no eixo A


def z_cons(x):
    """Topo do consolo = face inferior da I90 em x (cai do eixo E para o eixo A)."""
    return Z_CONS_A + INCL * x


Y_P13 = Y_LIN[3] + 23.69                      # vão da V406 (prancha de montagem); conferir no R01
CENTRAIS = [("P8A", Y_LIN[1], 0.40, 0.60), ("P11", Y_LIN[3], 0.50, 0.50), ("P13", Y_P13, 0.50, 0.50)]
TOPO_CENTRAL = 8.68
I110_TRECHOS = [("V407", Y_LIN[1], Y_LIN[3]), ("V406", Y_LIN[3], Y_P13), ("V405", Y_P13, Y_LIN[8])]
Z_I110_BASE = 7.58

# seções padrão ND (12/10/2026): só duas I, largura 40, alma 15, mesma fôrma
I90 = PerfilI(h=0.90, b=0.40, tw=0.15, tf=0.15, nome="I90")
I110 = PerfilI(h=1.10, b=0.40, tw=0.15, tf=0.25, nome="I110")
VB = PerfilRetangular(0.15, 0.70, "VB 15x70")
VMEZ = PerfilRetangular(0.40, 0.70, "40x70")
TERCA = PerfilRetangular(0.085, 0.30, "Ue300x85x25x3,00 (envelope)")
NIVEIS_MEZ, H_LAJE = [3.15, 6.55], 0.265 + 0.05
LAJE = PerfilRetangular(1.24, H_LAJE, "LA h26,5+5")
ESP_TERCA = 1.60
H_PLACA, E_PLACA, N_FIADAS = 1.25, 0.10, 8
PLACA = PerfilRetangular(E_PLACA, H_PLACA, "Placa e=10 h=125")


def montar() -> ModeloBIM:
    m = ModeloBIM("Letsara — Pavilhão pré-moldado", obra="Obra Letsara (Marque Engenharia)")

    # 1. pilares laterais (60 ⊥ fachada lateral) e consolos da I90
    for i, y in enumerate(Y_LIN, start=1):
        suf = "A" if i == 1 else "C" if i == N_LIN else ""
        m.pilar(f"P1{suf}", 0.0, y, 0.60, 0.40, Z_CALICE, TOPO_PLAT, obs="60 ⊥ fachada lateral")
        m.pilar(f"P2{suf}", LARG, y, 0.60, 0.40, Z_CALICE, TOPO_PLAT, obs="60 ⊥ fachada lateral")
        if 2 <= i <= 8:
            m.bloco("consolo", f"C-P1-L{i}", (0.50, y, z_cons(0.30)), 0.40, 0.40, 0.40, "Consolos")
            m.bloco("consolo", f"C-P2-L{i}", (LARG - 0.50, y, z_cons(LARG - 0.30)), 0.40, 0.40, 0.40, "Consolos")

    # pilares das fachadas frente e fundo (60 ⊥ fachada) e da linha central
    for j, x in enumerate(X_FACH[1:-1]):
        m.pilar(["P3", "P4", "P5"][j], x, 0.0, 0.40, 0.60, Z_CALICE, TOPO_PLAT, obs="60 ⊥ fachada frente")
        m.pilar(["P14", "P15", "P16"][j], x, COMP, 0.40, 0.60, Z_CALICE, TOPO_PLAT, obs="60 ⊥ fachada fundo")
    for marca, y, bx, by in CENTRAIS:
        m.pilar(marca, X_C, y, bx, by, Z_CALICE, TOPO_CENTRAL, obs="apoio I110 / TS-01")
    for marca, x in (("P8", 10.025), ("P8B", 30.075)):
        m.pilar(marca, x, Y_LIN[1], 0.40, 0.60, Z_CALICE, NIVEIS_MEZ[1] - H_LAJE, obs="mezanino")

    # 2. vigas centrais I110 e seus consolos
    zc = Z_I110_BASE + I110.h / 2
    for marca, ya, yb in I110_TRECHOS:
        m.linear("viga", marca, I110, (X_C, ya + 0.30, zc), (X_C, yb - 0.30, zc), "Vigas centrais I110",
                 obs="protendida, cord. Ø12,7")
        m.bloco("consolo", f"C-{marca}-a", (X_C, ya + 0.45, Z_I110_BASE), 0.40, 0.30, 0.40, "Consolos")
        m.bloco("consolo", f"C-{marca}-b", (X_C, yb - 0.45, Z_I110_BASE), 0.40, 0.30, 0.40, "Consolos")

    # 3. vigas I90 de cobertura (TS-01), inclinadas a 3 %, linhas 2 a 8
    for i in range(2, 9):
        y = Y_LIN[i - 1]
        for lado, xa, xb in (("a", 0.35, X_C - 0.25), ("b", X_C + 0.25, LARG - 0.35)):
            m.linear("viga", f"TS-01 L{i}{lado}", I90, (xa, y, z_cons(xa) + I90.h / 2),
                     (xb, y, z_cons(xb) + I90.h / 2), "Vigas I90 de cobertura", obs="inclinada 3 %")

    # vigas de borda das fachadas 1 e 9
    for y in (0.0, COMP):
        for xa, xb in itertools.pairwise(X_FACH):
            a, b = xa + 0.20, xb - 0.20
            m.linear("viga", "VB-01", VB, (a, y, z_cons(a) + 0.35), (b, y, z_cons(b) + 0.35), "Vigas de borda")

    # 4. terças metálicas a 1,60 m sobre as I90
    for x in np.arange(0.80, LARG - 0.5, ESP_TERCA):
        zt = z_cons(x) + I90.h + TERCA.h / 2
        for i in range(N_LIN - 1):
            m.linear("terca", "Ue300", TERCA, (x, Y_LIN[i] + 0.20, zt), (x, Y_LIN[i + 1] - 0.20, zt),
                     "Terças metálicas", material="aco")

    # 5. mezanino (faixa da frente, linhas 1–2): vigas 40×70 e laje alveolar h26,5 + 5
    for nivel in NIVEIS_MEZ:
        zv = nivel - H_LAJE - VMEZ.h / 2
        for y in (Y_LIN[0], Y_LIN[1]):
            for xa, xb in itertools.pairwise(X_FACH):
                m.linear("viga", f"VM {nivel:+.2f}", VMEZ, (xa + 0.25, y, zv), (xb - 0.25, y, zv),
                         "Vigas de mezanino", obs="Gerber + 2º estágio")
        for k in range(int((LARG - 0.60) // 1.25)):
            x = 0.925 + k * 1.25
            m.linear("laje", f"LA {nivel:+.2f}", LAJE, (x, Y_LIN[0] + 0.20, nivel - H_LAJE / 2),
                     (x, Y_LIN[1] - 0.20, nivel - H_LAJE / 2), "Laje alveolar")

    # 6. placas de fechamento por fora das faces dos pilares (8 fiadas de 1,25 m)
    for k in range(N_FIADAS):
        z = k * H_PLACA + H_PLACA / 2
        for x, nome in ((-0.30 - E_PLACA / 2, "PL-A"), (LARG + 0.30 + E_PLACA / 2, "PL-E")):
            for i in range(N_LIN - 1):
                m.linear("placa", nome, PLACA, (x, Y_LIN[i], z), (x, Y_LIN[i + 1], z), "Placas de fechamento")
        for y, nome in ((-0.30 - E_PLACA / 2, "PL-1"), (COMP + 0.30 + E_PLACA / 2, "PL-9")):
            for xa, xb in itertools.pairwise(X_FACH):
                a = xa - 0.40 if xa == 0 else xa
                b = xb + 0.40 if xb == LARG else xb
                m.linear("placa", nome, PLACA, (a, y, z), (b, y, z), "Placas de fechamento")

    # pendências (prefixo "!" = destaque na página)
    topo_terca_E = z_cons(LARG - 0.35) + I90.h + TERCA.h
    if topo_terca_E > TOPO_PLAT:
        m.pendente(f"! Cobertura acima da platibanda no lado alto: consolo em +{z_cons(LARG - 0.30):.2f}, "
                   f"topo da I90 em +{z_cons(LARG - 0.35) + I90.h:.2f} e da terça em +{topo_terca_E:.2f}, "
                   f"acima do topo do pilar em +{TOPO_PLAT:.2f}. Baixar os consolos ou subir os pilares.")
    m.pendente("Não modelados: pilares da parede C (P9, P10, P12), P6/P7, vergas V201 e contraventamento.")
    m.pendente("Posição de P13 tirada do vão da V406 (23,69 m); conferir no R01.")
    m.pendente("Terças, laje alveolar e consolos como envelope maciço.")
    return m


if __name__ == "__main__":
    saida = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / "saidas")
    saida.mkdir(parents=True, exist_ok=True)
    modelo = montar()
    q = quantitativos(modelo)
    ifc = gravar_ifc(modelo, saida / "letsara.ifc")
    malha = ler_malha_ifc(ifc)
    gravar_visualizador(malha, saida / "letsara_3d.html", "Letsara · modelo estrutural",
                        "Pavilhão pré-moldado 40,10 × 79,75 m · Marque Engenharia · modelo de estudo",
                        pendencias=modelo.pendencias, quant=q)
    for g, d in q.items():
        print(f"{g:26s} {d['pecas']:4d} peças  {d['volume_m3']:8.1f} m³")
    print("pendências:", len(modelo.pendencias), "->", saida)
