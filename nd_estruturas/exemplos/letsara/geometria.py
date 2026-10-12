"""Letsara — geometria única da obra, lida da PLANTA BAIXA - LOCAÇÃO DE PILARES do R01 (Marque Engenharia).

Convenção do modelo: x = 0 no eixo A (transversal), y = 0 no eixo da linha 1 (longitudinal), z = 0 no piso. Metros.
Ordenadas do R01 (cm, a partir da face externa): transversal 30 / 1017 / 2005 / 2993 / 3980 (face externa 4010);
longitudinal (da face da linha 9) 20 / 982,5 / 1982,5 / 2982,5 / 3982,5 / 4975 / 5982,5 / 6990 / 7955 (face 7975).
Revisão 12/10/2026: a geometria anterior (76,81 m) usava as cotas da planta de vigas de travamento, que são os
comprimentos das vigas entre faces, e o eixo C a 20,05 m do eixo A. Esta é a geometria correta (79,35 m entre eixos).
"""

# eixos transversais (m, a partir do eixo A)
X_EIXO = dict(A=0.0, B=9.87, C=19.75, D=29.63, E=39.50)
X_FACH = [X_EIXO[k] for k in "ABCDE"]
X_FACE_EXT = (-0.30, 39.80)            # faces externas dos pilares de canto (pilares 40 × 60, lado de 60 em x)
LARG = X_EIXO["E"]                     # eixo A ao eixo E

# linhas longitudinais (m, a partir do eixo da linha 1)
Y_LIN = [0.0, 9.65, 19.725, 29.80, 39.725, 49.725, 59.725, 69.725, 79.35]
Y_FACE_EXT = (-0.20, 79.55)            # faces externas das linhas 1 e 9 (pilares com lado de 40 em y)
COMP = Y_LIN[-1]
VAOS_Y = [round(b - a, 3) for a, b in zip(Y_LIN[:-1], Y_LIN[1:])]   # 9,65 / 10,075 / 10,075 / 9,925 / 10 / 10 / 10 / 9,625

# pilares especiais (nome, x, y, bx, by) — bx = dimensão em x, by = em y (m)
PILARES_ESPECIAIS = [
    ("P3", 9.87, Y_LIN[0], 0.40, 0.60), ("P4", 19.75, Y_LIN[0], 0.40, 0.60), ("P5", 29.63, Y_LIN[0], 0.40, 0.60),     # linha 1
    ("P7", 39.50, 3.79, 0.60, 0.40), ("P6", 36.175, 3.79, 0.25, 0.40),                                                  # anexo, eixo E
    ("P8", 9.87, Y_LIN[1], 0.40, 0.60), ("P8A", 19.75, Y_LIN[1], 0.40, 0.60), ("P8B", 29.63, Y_LIN[1], 0.40, 0.60),
    ("P6", 36.175, Y_LIN[1], 0.25, 0.40),                                                                                # linha 2
    ("P9", 9.87, Y_LIN[3], 0.40, 0.40), ("P10", 15.195, Y_LIN[3], 0.25, 0.25), ("P11", 19.75, Y_LIN[3], 0.40, 0.40),
    ("P10", 24.305, Y_LIN[3], 0.25, 0.25), ("P12", 29.63, Y_LIN[3], 0.40, 0.40),                                       # linha 4 (portões)
    ("P13", 19.75, 54.575, 0.60, 0.60),                                                                                  # central
    ("P3", 9.87, Y_LIN[8], 0.40, 0.60), ("P14", 19.75, Y_LIN[8], 0.40, 0.60), ("P5", 29.63, Y_LIN[8], 0.40, 0.60),   # linha 9
]
Y_P13 = 54.575
LINHA_PORTOES = 3                       # índice em Y_LIN (linha 4 do R01)
X_L4 = [0.0, 9.87, 15.195, 19.75, 24.305, 29.63, 39.50]      # P1, P9, P10, P11, P10, P12, P2
X_L2 = [0.0, 9.87, 19.75, 29.63, 36.175, 39.50]              # P1B, P8, P8A, P8B, P6, P2B
