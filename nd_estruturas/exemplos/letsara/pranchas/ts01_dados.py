"""TS-01 — dados únicos da peça (memória = prancha). Usado pelas 3 folhas (fôrma/insertos, armação, chaparia)."""
import math, sys, json
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas")
from nd_estruturas.prefabricados import (Concreto, Carregamento, secao_I, verificar_viga_pretracionada,
                                         icamento_viga, pressao_vento, transitorias_viga, CORD)

I_CAI = 0.03
L_H = 19710                                           # vão horizontal entre pontas (mm)
L = round(L_H / math.cos(math.atan(I_CAI)))           # comprimento de fabricação ao longo do eixo
H = 900
DX = round(H * I_CAI)                                 # ponta a prumo: topo deslocado 27 mm
P = dict(marca="TS-01", qtd=14, L=L, h=H, b=400, ts=120, ti=150, m=80, bw=150, mac=500,
         fck=50, fckj=35, n_cord=6, y_cord=75, x_cord=[-150, -100, -50, 50, 100, 150],
         alcas=[2100, 7400, L - 7400, L - 2100], estoque=[2100, L - 2100],
         tercas=[255 + 1600 * k for k in range(13)], nos=[255 + 3200 * k for k in range(7)],
         pino_x=150, h_tb2=600, L_pista=60, sig_pi=1453)
C = Concreto(P["fck"])
sec = secao_I(H / 1000, bs=0.40, ts=0.12, ms=0.08, bw=0.15, bi=0.40, ti=0.15, mi=0.08)
L_calc = (L - 2 * P["pino_x"]) / 1000
TRIB, qv = 9.655, pressao_vento(45.0, S3=0.95)
car = Carregamento(sec.A * 25, 0.25 * TRIB, 0.25 * TRIB, w=qv * TRIB, psi1=0.4, psi2=0.0)
R = verificar_viga_pretracionada(sec, L_calc, car, C, P["n_cord"], y_cord=P["y_cord"] / 1000, fckj=P["fckj"])
Ap = P["n_cord"] * CORD["12.7"]
V = sec.A * L / 1000 + (P["b"] * H / 1e6 - sec.A) * P["mac"] / 1000 * 2
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


def tipo_terca(s):
    return "CH-T2" if any(abs(s - n) < 1 for n in P["nos"]) else "CH-T1"


if __name__ == "__main__":
    print("L", L, "peso kN", round(peso, 1), "t", round(peso / 9.81, 2), "V", round(V, 3))
    print("TR", json.dumps(TR, indent=0))
    print("alça Fd", round(ALCA_Fd, 1), "cap", round(ALCA_cap, 1), "P0", R.linhas["P0_kN"])
