"""Geometria da VB 15 × 60 com dente Gerber na POSIÇÃO MONTADA (caimento 3 %, sobe de A para E) e na peça (fabricada reta).

rev04 (NBR 9062:2017 7.2.1.6): face de apoio do dente HORIZONTAL na montagem (sobre o neoprene e o topo horizontal do CP-VB),
pontas e faces dos recortes A PRUMO. Na peça (fôrma reta) isso aparece como linhas inclinadas 3 % em relação ao eixo da viga.
Unidades: mm. Origem local: canto inferior da ponta baixa (lado A), eixo u ao longo do fundo, v perpendicular.
"""
import math

I = 0.03
H, HD, LN, XP = 600, 300, 270, 110          # altura, nariz, comprimento do nariz, centro do apoio a partir da ponta
REC = H - HD
C, S = 1 / math.sqrt(1 + I * I), I / math.sqrt(1 + I * I)


def montada(L):
    """Contorno na posição montada (x horizontal a partir da ponta baixa, z vertical a partir do fundo na ponta baixa).
    L = distância horizontal entre as pontas (mm)."""
    zb = lambda x: I * x                                       # fundo da viga sem recorte
    zt = lambda x: I * x + H / C                               # topo (H medido perpendicular ao eixo)
    znL = zb(XP) + REC                                         # face de apoio da ponta baixa (horizontal)
    znR = zb(L - XP) + REC                                     # face de apoio da ponta alta (horizontal)
    return [(0, znL), (LN, znL), (LN, zb(LN)), (L - LN, zb(L - LN)), (L - LN, znR), (L, znR), (L, zt(L)), (0, zt(0))]


def peca(L):
    """Mesmo contorno no sistema da peça fabricada reta (u ao longo do fundo, v perpendicular)."""
    return [(round(x * C + z * S, 1), round(-x * S + z * C, 1)) for x, z in montada(L)]


def comprimento_fundo(L):
    return round(L / C)


if __name__ == "__main__":
    for p in peca(9430):
        print(p)
