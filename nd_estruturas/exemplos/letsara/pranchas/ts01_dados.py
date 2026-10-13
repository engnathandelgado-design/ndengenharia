"""TS-01 — dados únicos da peça (memória = prancha). Usado pelas 3 folhas (fôrma/insertos, armação, chaparia)."""
import math, sys, json
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas")
from nd_estruturas.prefabricados import (Concreto, Carregamento, secao_I, verificar_viga_pretracionada,
                                         icamento_viga, pressao_vento, transitorias_viga, CORD)

I_CAI = 0.03
L_H = 19150                                           # entre as faces das pontas (a prumo): 0,325 → 19,475 m (geometria R01)
L = round(L_H / math.cos(math.atan(I_CAI)))           # comprimento de fabricação ao longo do eixo (ponto 0 a ponto 0)
H = 900
DX = round(H * I_CAI)                                 # ponta a prumo: topo deslocado 27 mm
HD, LN = 450, 300                                     # dente Gerber: altura e comprimento (nas duas pontas)
PASSO_T = round((L - 510) / 12)
P = dict(marca="TS-01", qtd=14, L=L, h=H, b=400, ts=120, ti=150, m=80, bw=150, mac=500,
         fck=50, fckj=35, n_cord=6, y_cord=75, x_cord=[-150, -100, -50, 50, 100, 150],
         alcas=[2100, 7400, L - 7400, L - 2100], estoque=[2100, L - 2100],
         tercas=[255 + PASSO_T * k for k in range(13)], nos=[255 + 2 * PASSO_T * k for k in range(7)],
         pino_x=150, L_pista=60, sig_pi=1453, x_mac=1200)
C = Concreto(P["fck"])
sec = secao_I(H / 1000, bs=0.40, ts=0.12, ms=0.08, bw=0.15, bi=0.40, ti=0.15, mi=0.08)
L_calc = (L - 2 * P["pino_x"]) / 1000          # entre pinos (apoios nos dentes)
TRIB, qv = 10.075, pressao_vento(45.0, S3=0.95)
car = Carregamento(sec.A * 25, 0.25 * TRIB, 0.25 * TRIB, w=qv * TRIB, psi1=0.4, psi2=0.0)
R = verificar_viga_pretracionada(sec, L_calc, car, C, P["n_cord"], y_cord=P["y_cord"] / 1000, fckj=P["fckj"])
Ap = P["n_cord"] * CORD["12.7"]
V = (sec.A * L / 1000 + (P["b"] * H / 1e6 - sec.A) * P["x_mac"] / 1000 * 2
     - 2 * P["b"] * (H - HD) * LN / 1e9)              # maciços de 1,20 m nas pontas, menos o recorte dos dentes
peso = V * 25
F_cord = P["sig_pi"] * 98.7 / 1000
Md_neg = max(0.0, (1.4 * car.w - car.g1 - car.g2) * L_calc ** 2 / 8)
ep = sec.yc - P["y_cord"] / 1000
TR = transitorias_viga(sec, L / 1000, R.linhas["P0_kN"], ep, C, P["fckj"],
                       [a / 1000 for a in P["alcas"]], [a / 1000 for a in P["estoque"]])
# alça de cordoalha: 1 laço (2 pernas) Ø12,7 CP-190; trabalho = 2 × Fptk/4 × 0,7 (redução por curvatura do laço)
FPTK1 = 98.7 * 1900 / 1000
ALCA_cap = 2 * FPTK1 / 4 * 0.7
ALCA_Fd = peso / 4 * 1.3                              # 4 pontos com balancins (reações iguais), coef. dinâmico 1,3
cg_s = L / 2 + DX / 2 * (sec.yc * 1000 / H)           # CG ao longo do fundo (ponta inclinada desloca pouco)
assert R.ok and TR["desforma_montagem"]["ok"] and TR["estoque_transporte"]["ok"] and ALCA_Fd <= ALCA_cap
f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")


DT = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/dentes.json"))["TS-01"]
AD = DT["calculo"]["adotado"]
ANC = AD["ancoragem_tirante_mm"]


def armacao_ts01():
    """Armação passiva da TS-01 (cm na relação; geo = forma em escala para a prancha de armaduras)."""
    X_SUS = [LN + 40 + k * 60 for k in range(AD["n_sus"])]
    zona = 1500
    ini = LN + 40 + AD["n_sus"] * 60 + 100
    x_est = sorted(set(list(range(ini, zona + 1, 150)) + list(range(zona + 250, L - zona, 250)) + list(range(L - ini, L - zona - 1, -150))))
    n1 = len(x_est)
    cN1, cN3, cN6 = round((2 * (90 + 840) + 140) / 10), round((2 * (340 + 70) + 140) / 10), round((2 * (340 + 840) + 140) / 10)
    n3 = round(L / 250) + 1
    LN8 = round((LN + ANC) / 10)
    barras = [dict(pos="N1", diam=6.3, qtd=n1, comp=cN1, forma=[(0, 0), (9, 0), (9, 84), (0, 84), (0, 0), (1.5, 1.5)], trechos=["9", "84", "9", "84"], geo=dict(k="E", a=9, b=84)),
              dict(pos="N2", diam=12.5, qtd=4, comp=round((L - 60) / 10), trechos=[f"{(L - 60) / 10:.0f}"], geo=dict(k="R", a=round((L - 60) / 10))),
              dict(pos="N3", diam=6.3, qtd=n3, comp=cN3, forma=[(0, 0), (34, 0), (34, 7), (0, 7), (0, 0), (1.5, 1.5)], trechos=["34", "7", "34", "7"], geo=dict(k="E", a=34, b=7)),
              dict(pos="N4", diam=6.3, qtd=n3, comp=cN3, forma=[(0, 0), (34, 0), (34, 7), (0, 7), (0, 0), (1.5, 1.5)], trechos=["34", "7", "34", "7"], geo=dict(k="E", a=34, b=7)),
              dict(pos="N5", diam=10.0, qtd=2, comp=round((L - 2 * LN - 60) / 10), trechos=[f"{(L - 2 * LN - 60) / 10:.0f}"], geo=dict(k="R", a=round((L - 2 * LN - 60) / 10))),
              dict(pos="N6", diam=8.0, qtd=14, comp=cN6, forma=[(0, 0), (34, 0), (34, 84), (0, 84), (0, 0), (1.5, 1.5)], trechos=["34", "84", "34", "84"], geo=dict(k="E", a=34, b=84)),
              dict(pos="N7", diam=10.0, qtd=8, comp=94, forma=[(0, 6), (0, 0), (34, 0), (34, 6)], trechos=["6", "34", "6"], geo=dict(k="G", a=34, g=6)),
              dict(pos="N8", diam=AD["d_tir"], qtd=2 * AD["n_tir"] // 2, comp=2 * LN8 + 30,
                   forma=[(LN8, 0), (0, 0), (0, 30), (LN8, 30)], trechos=[f"{LN8}", "30", f"{LN8}"], geo=dict(k="U", a=LN8, b=30, g=0)),
              dict(pos="N9", diam=AD["d_sus"], qtd=2 * AD["n_sus"], comp=cN6, forma=[(0, 0), (34, 0), (34, 84), (0, 84), (0, 0), (1.5, 1.5)], trechos=["34", "84", "34", "84"], geo=dict(k="E", a=34, b=84)),
              dict(pos="N10", diam=10.0, qtd=2 * AD["n_cost"], comp=round((2 * (750 + 340) + 140) / 10),
                   forma=[(0, 0), (75, 0), (75, 34), (0, 34), (0, 0), (1.5, 1.5)], trechos=["75", "34", "75", "34"], geo=dict(k="E", a=75, b=34)),
              dict(pos="N11", diam=10.0, qtd=4, comp=round((2 * (340 + 390) + 140) / 10),
                   forma=[(0, 0), (34, 0), (34, 39), (0, 39), (0, 0), (1.5, 1.5)], trechos=["34", "39", "34", "39"], geo=dict(k="E", a=34, b=39))]
    return x_est, X_SUS, barras


def tipo_terca(s):
    return "CH-T2" if any(abs(s - n) < 1 for n in P["nos"]) else "CH-T1"


if __name__ == "__main__":
    print("L", L, "peso kN", round(peso, 1), "t", round(peso / 9.81, 2), "V", round(V, 3))
    print("TR", json.dumps(TR, indent=0))
    print("alça Fd", round(ALCA_Fd, 1), "cap", round(ALCA_cap, 1), "P0", R.linhas["P0_kN"])
