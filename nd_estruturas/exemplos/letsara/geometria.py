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
# rev12 (27/10/2026, decisão do Nathan, opção D do quadro decisao_fresta_canto): os 4 pilares de canto 40×60 (linhas 1 e 9,
# eixos A e E) saem DY_CANTO para fora em y → a face externa coincide com a dos PF (60 ⊥ fachada): −0,30 / COMP + 0,30.
DY_CANTO = 0.10
Y_FACE_EXT = (round(Y_LIN[0] - 0.30, 3), round(Y_LIN[-1] + 0.30, 3))        # faces externas das linhas 1 e 9 (PF e cantos alinhados)


def y_canto(y_linha):
    """eixo (y) do pilar de canto da linha de fachada y_linha (0 ou COMP); seção 40 em y."""
    return round(y_linha - DY_CANTO if y_linha < COMP / 2 else y_linha + DY_CANTO, 3)


def y_canto_int(y_linha):
    """face interna (y) do pilar de canto (lado do pavilhão)."""
    return round(y_canto(y_linha) + (0.20 if y_linha < COMP / 2 else -0.20), 3)
COMP = Y_LIN[-1]
VAOS_Y = [round(b - a, 3) for a, b in zip(Y_LIN[:-1], Y_LIN[1:])]   # 9,65 / 10,075 / 10,075 / 9,925 / 10 / 10 / 10 / 9,625

# pilares especiais (nome, x, y, bx, by) — bx = dimensão em x, by = em y (m)
PILARES_ESPECIAIS = [
    ("P3", 9.87, Y_LIN[0], 0.40, 0.60), ("P4", 19.75, Y_LIN[0], 0.40, 0.60), ("P5", 29.63, Y_LIN[0], 0.40, 0.60),     # linha 1
    ("P7", 39.50, 3.79, 0.60, 0.40), ("P6", 36.175, 3.79, 0.25, 0.40),                                                  # anexo, eixo E
    ("P8", 9.87, Y_LIN[1], 0.40, 0.60), ("P8A", 19.75, Y_LIN[1], 0.40, 0.60), ("P8B", 29.63, Y_LIN[1], 0.40, 0.60),
    ("P6", 36.175, Y_LIN[1], 0.25, 0.40),                                                                                # linha 2
    ("P9", 9.87, Y_LIN[3], 0.40, 0.40), ("P10", 15.27, Y_LIN[3], 0.40, 0.25), ("P11", 19.75, Y_LIN[3], 0.40, 0.40),
    ("P10", 24.23, Y_LIN[3], 0.40, 0.25), ("P12", 29.63, Y_LIN[3], 0.40, 0.40),                                        # linha 4 (portões)
    ("P13", 19.75, 46.317, 0.40, 0.40), ("P13B", 19.75, 62.833, 0.40, 0.40),                                           # centrais (DEC-058)
    ("P3", 9.87, Y_LIN[8], 0.40, 0.60), ("P14", 19.75, Y_LIN[8], 0.40, 0.60), ("P5", 29.63, Y_LIN[8], 0.40, 0.60),   # linha 9
]
# DEC-058 (24/10/2026, decisão do Nathan, arranjo C de estudo_i130_pilar_extra): o P13 (PC-03) sai de y 54,575 (60×60) e
# vai para y 46,317; entra um pilar novo (P13B, também PC-03, 40×40) em y 62,833 → 3 vãos iguais de 16,517 m da linha 4
# à linha 9; a I120 da linha 2 à 4 (20,15 m) não muda. Os dois PC-03 ficam fora das linhas da cobertura (TS-01 no topo da I120).
Y_PC_C = (46.317, 62.833)
Y_P13 = Y_PC_C[0]
LINHA_PORTOES = 3                       # índice em Y_LIN (linha 4 do R01)
# rev12 (27/10, decisão do Nathan): PG-02 e PG-04 passam de 25×25 a 25×40 (40 ao longo da parede da linha 4, em x). Para manter
# os 5,00 m livres de cada portão (face a face), o eixo sai 7,5 cm para longe do portão: PG-02 15,195 → 15,270; PG-04 24,305 → 24,230.
# PENDÊNCIA visível: confirmar com o arquitetônico/cliente os 5,00 m livres e a nova locação dos PG-02/PG-04.
PG_L4 = {"PG-01": ("P9", 9.87, 0.40, 0.40), "PG-02": ("P10", 15.27, 0.40, 0.25), "PG-04": ("P10", 24.23, 0.40, 0.25), "PG-03": ("P12", 29.63, 0.40, 0.40)}
VAO_PORTAO = 5.00
X_L4 = [0.0, 9.87, PG_L4["PG-02"][1], 19.75, PG_L4["PG-04"][1], 29.63, 39.50]      # P1, P9, P10, P11, P10, P12, P2
X_L2 = [0.0, 9.87, 19.75, 29.63, 36.175, 39.50]              # P1B, P8, P8A, P8B, P6, P2B

# ------------------------------------------------------------------ rev09 (23/10/2026) — decisões do Nathan
# Níveis do mezanino pelo corte AA' do R01 (360 + 30 + 310 + 30): TOPO DA CAPA +3,90 e +7,30 (antes +3,15 / +6,55, errado).
# A laje de cima (+7,30) é a cobertura do bloco, sem uso (arquitetônico: "Nível Cobertura"), sem escada.
Z_PISOS = (3.90, 7.30)
Z_PISO_PRONTO = 3.95                   # DEC-055 (24/10): 2º pav. = topo da capa +3,90; piso pronto ~+3,95 (revestimento 5 cm) — chegada das escadas
NIV_TXT = ("+3,90", "+7,30")
H_LAJE_TOT = 0.25                       # alveolar h20 + capa 5
Z_APOIO_LAJE = tuple(round(z - H_LAJE_TOT - 0.01, 3) for z in Z_PISOS)   # topo das vigas do mezanino (fita de neoprene 1 cm)
# pilares do anexo da escada (R01): P6 25×40 em (36,175; 3,79) e na linha 2; P7 40×60 no eixo E em 3,79
P6_ESC, P7_ESC, P6_L2 = (36.175, 3.79), (39.50, 3.79), (36.175, Y_LIN[1])
# abertura da escada SÓ na laje +3,90 (DEC-045): de P6 ao eixo E, da viga P6–P7 à linha 2
ABERTURA = dict(nivel=Z_PISOS[0], x0=36.00, x1=39.20, y0=3.99, y1=Y_LIN[1] - 0.20)
# escada metálica em U (arquitetônico R01: 22 degraus H 17,72 B 28, patamar +1,95, lances de 2,80, patamar 1,60)
ESCADA = dict(n_esp=22, espelho=Z_PISO_PRONTO / 22, piso=0.28, z_patamar=11 * Z_PISO_PRONTO / 22,   # DEC-055: espelho 17,95
              x_face_P6=36.30, x_face_E=39.20, y_patamar=(3.99, 5.55), y_lances=(5.55, 8.35), y_chegada=(8.35, Y_LIN[1] - 0.20))
# cobertura metálica da linha 2 (DEC-046; DEC-050 sem montantes, W direto na cabeça dos pilares): do eixo A ao E, topo na inclinação da TS-01
X_MONT_L2 = (4.935, 9.87, 14.81, 19.75, 24.69, 29.63, 32.90, 36.175, 37.84)
# rev09c (24/10, decisão do Nathan: escada externa do arquitetônico entra no projeto, opção B do quadro decisao_escada_posicao)
# Escada metálica em L encostada na fachada A, do térreo à porta do 2º pavimento (+3,90). Arquitetônico (bloco 55555): largura 1,50,
# piso 28, 22 espelhos (5 no lance de baixo, ao longo de x; 17 no de cima, ao longo da fachada), patamar 1,50 × 1,50 na quina e
# patamar de chegada de 0,20 a 2,44 (y). Deslocada 30 cm para fora (e ~22 cm para a linha 2) em relação ao arquitetônico (sobreposição de 25/10) para passar livre das placas
# (face externa das placas −0,425; folga 25 mm): face interna da escada em x = −0,45.
ESCADA_EXT = dict(n_esp=22, espelho=Z_PISO_PRONTO / 22, piso=0.28,   # DEC-055: espelho 17,95, chegada no piso pronto +3,95
                  n_baixo=5, n_cima=17, largura=1.50,
                  x_int=-0.45, x_ext=-1.95, y_chegada=(0.20, 2.44), y_lance_cima=(2.44, 6.92), y_patamar=(6.92, 8.42),
                  x_lance_baixo=(-1.95, -3.07), porta_y=(0.89, 1.79), porta_h=2.14)

# rev12 (fresta das vigas de borda, opção B): nos vãos entre pilares de fachada PF (B–C e C–D das linhas 1 e 9) a VB 15×60 e o
# consolo CP-VB ficam rentes à face externa do pilar (60 ⊥ fachada): eixo da VB a E_VB_FACE para fora do eixo da linha.
# rev12 (27/10, opção D): com os cantos deslocados DY_CANTO, os vãos de canto (A–B, D–E) também ficam com a VB e o CP-VB rentes
# à face externa (fresta de 2,5 cm até a placa em toda a fachada).
E_VB_FACE = 0.225


def y_vb(x_meio, y_linha):
    """eixo (y) da VB na linha de fachada y_linha (0 ou COMP): rente à face externa dos pilares em todos os vãos (rev12, opção D)."""
    return y_linha - E_VB_FACE if y_linha < COMP / 2 else y_linha + E_VB_FACE
