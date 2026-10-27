"""TS-01 — dados únicos da peça (memória = prancha). Usado pelas 3 folhas (fôrma/insertos, armação, chaparia)."""
import math, sys, json
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas")
from nd_estruturas.prefabricados import (Concreto, Carregamento, secao_I, secao_retangular, verificar_viga_pretracionada,
                                         icamento_viga, pressao_vento, transitorias_viga, CORD, ato_pretracao,
                                         lbpt_cordoalha, GAMA_P_ATO, SIG_ACO_ATO)

I_CAI = 0.03
LG = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/ligacoes.json"))
L_H = round((LG["X_PONTA_CEN"] - LG["X_PONTA_ESQ"]) * 1000)   # rev03: sem dentes; ponta a 25 mm da cabeça do P1 e a 37,5 mm do eixo C
L = round(L_H / math.cos(math.atan(I_CAI)))           # comprimento de fabricação ao longo do eixo (ponto 0 a ponto 0)
H = 900
DX = round(H * I_CAI)                                 # ponta a prumo: topo deslocado 27 mm
HD, LN = 0, 0                                         # rev03: sem dente Gerber (apoio direto no assento do pilar / topo da I120)
N_ESP = len(LG["s_tercas"]) - 1
PASSO_T = round(LG["passo_tercas"] * 1000)
P = dict(marca="TS-01", qtd=12, L=L, h=H, b=400, ts=120, ti=150, m=80, bw=150, mac=500,
         # DEC-043 (22/10/2026): protensão COMPLETA (ELS-D na frequente, ELS-F na rara) → 10 cordoalhas: 5 a 5,5 cm + 5 a 10 cm
         # (x = 0, ±4, ±15,5 nas duas linhas); as 4 de 10 cm em x = ±4 e ±15,5 isoladas 3,00 m nas pontas (ato). Antes: 8 (limitada).
         fck=50, fckj=35, n_cord=10, y_cord=77.5, x_cord=[-155, -40, 0, 40, 155], x_cord2=[-155, -40, 0, 40, 155], y1=55, y2=100,
         isol=dict(n=4, x=[-155, -40, 40, 155], L=3000),
         # rev03: cordoalhas fora das faixas dos tubos TB-3 (y = ±100, Ø50) dos 2 pinos de cada apoio: |x| ≤ 40 ou |x| = 155
         tb=dict(d=50, y=(-100, 100), s_ext=round(LG["PINO_TS"] * 1000, 1), s_cen=round(LG["PINO_TS"] * 1000, 1), L=900),   # rev04: simétrico
         cunha=dict(L=round(LG["CUNHA"] * 1000), e=round(LG["DEGRAU_CUNHA"] * 1000)),   # rev04: cunha no fundo das pontas (face de apoio horizontal)
         alcas=[2100, 7600, L - 7600, L - 2100], estoque=[2100, L - 2100],
         tercas=[round(s * 1000) for s in LG["s_tercas"]], nos=[round(LG["s_tercas"][i] * 1000) for i in LG["idx_nos_x"]],   # rev06: 15 espaços; nós do X nas terças 0, 8, 15
         neo_ext=round((LG["NEO_EXT"]["xc"] - LG["X_PONTA_ESQ"]) * 1000), neo_cen=round((LG["X_PONTA_CEN"] - LG["NEO_CEN"]["xc"]) * 1000),
         pino_x=round((LG["NEO_EXT"]["xc"] - LG["X_PONTA_ESQ"]) * 1000), L_pista=60, sig_pi=1453, x_mac=1200)
C = Concreto(P["fck"])
sec = secao_I(H / 1000, bs=0.40, ts=0.12, ms=0.08, bw=0.15, bi=0.40, ti=0.15, mi=0.08)
L_calc = (L - P["neo_ext"] - P["neo_cen"]) / 1000    # entre centros dos neoprenes (apoio direto, sem dente)
TRIB, qv = 10.075, pressao_vento(45.0, S3=0.95)
CC = LG["cargas_cob"]
G_COB = CC["g_total_sem_terca"] + 0.123 / LG["passo_tercas"]
car = Carregamento(sec.A * 25, G_COB * TRIB, CC["sobrecarga"] * TRIB, w=qv * TRIB, psi1=0.4, psi2=0.0)
# DEC-032: perdas pela NBR 6118:2023 9.6.3 (U 70 %, t0 fictícia 5 dias, cobertura aplicada aos 60 dias) e γp 1,1 no ato
R = verificar_viga_pretracionada(sec, L_calc, car, C, P["n_cord"], y_cord=P["y_cord"] / 1000, fckj=P["fckj"], sig_pi=P["sig_pi"], nivel="completa")   # DEC-043
Ap = P["n_cord"] * CORD["12.7"]
V = sec.A * L / 1000 + (P["b"] * H / 1e6 - sec.A) * P["x_mac"] / 1000 * 2   # maciços de 1,20 m nas pontas
peso = V * 25
F_cord = P["sig_pi"] * 98.7 / 1000
Md_neg = max(0.0, (1.4 * car.w - car.g1 - car.g2) * L_calc ** 2 / 8)
ep = sec.yc - P["y_cord"] / 1000
# pontos de içamento/estocagem a 2,10 m ficam dentro do trecho isolado (3,00 m): 6 cordoalhas ativas (5 a 55 + 1 a 100 mm)
N_ISOL = P["isol"]["n"]
N_ATIVAS = P["n_cord"] - N_ISOL
N_C1_Y2 = len(P["x_cord2"]) - N_ISOL                                  # aderentes na 2ª linha (x = 0)
Y_ATIVAS = (len(P["x_cord"]) * P["y1"] + N_C1_Y2 * P["y2"]) / N_ATIVAS
TR = transitorias_viga(sec, L / 1000, GAMA_P_ATO * R.linhas["P0_kN"] * N_ATIVAS / P["n_cord"], sec.yc - Y_ATIVAS / 1000, C, P["fckj"],
                       [a / 1000 for a in P["alcas"]], [a / 1000 for a in P["estoque"]])
# alça de cordoalha: 1 laço (2 pernas) Ø12,7 CP-190; trabalho = 2 × Fptk/4 × 0,7 (redução por curvatura do laço)
FPTK1 = 98.7 * 1900 / 1000
ALCA_cap = 2 * FPTK1 / 4 * 0.7
ALCA_Fd = peso / 4 * 1.3                              # 4 pontos com balancins (reações iguais), coef. dinâmico 1,3
cg_s = L / 2 + DX / 2 * (sec.yc * 1000 / H)           # CG ao longo do fundo (ponta inclinada desloca pouco)
assert R.ok and TR["desforma_montagem"]["ok"] and TR["estoque_transporte"]["ok"] and ALCA_Fd <= ALCA_cap
f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")


# ------------------------------------------------------------------ ato da protensão ao longo da peça (DEC-032)
# NBR 6118:2023 17.2.4.3.2: γp 1,1; transferência em lbpt (9.4.5, liberação gradual); C2 (2 cord. a 10 cm) isoladas 3,00 m;
# maciço 40 × 90 nos 1,20 m das pontas; peça apoiada nas pontas na pista (M = g1·x·(L − x)/2).
SIG_P0 = R.linhas["sigma_p0_MPa"]
LBPT, LBP, _ = lbpt_cordoalha(P["fckj"], SIG_P0, gradual=True)
LBPT_BRUSCA = lbpt_cordoalha(P["fckj"], SIG_P0, gradual=False)[0]
SEC_PONTA = secao_retangular(0.40, H / 1000)
GRUPOS = [dict(n=len(P["x_cord"]), y=P["y1"] / 1000, x0=0.0), dict(n=N_C1_Y2, y=P["y2"] / 1000, x0=0.0), dict(n=N_ISOL, y=P["y2"] / 1000, x0=P["isol"]["L"] / 1000)]
ATO = ato_pretracao(sec, SEC_PONTA, P["x_mac"] / 1000, L / 1000, GRUPOS, SIG_P0, car.g1, P["fckj"], LBPT)
AS_N2 = 4 * 1.227                                                       # N2 4 Ø12,5 no topo (cm²)
# 17.2.4.3.2 c): As = R/250 MPa onde o topo está tracionado; complemento N9 nas pontas até cobrir As − N2 + lb
_xs_falta = [p["x"] for p in ATO["pontos"] if p["R_tracao"] / (SIG_ACO_ATO * 1000) * 1e4 > AS_N2]
LB_N9 = 12.5 / 4 * (500 / 1.15) / (2.25 * 0.7 * 0.3 * P["fckj"] ** (2 / 3) / 1.4) / 1000      # NBR 6118:2023 9.4.2.4 (Ø12,5, fckj)
L_N9 = max(2500, math.ceil(((max(_xs_falta) if _xs_falta else 0) + LB_N9) * 1000 / 50) * 50)
AS_TOPO = AS_N2 + 2 * 1.227                                             # N2 + N9 2 Ø12,5 na zona das pontas
ATO["As_topo_adotada_cm2"] = round(AS_TOPO, 2)
ATO["L_N9_mm"] = L_N9
assert ATO["ok"] and ATO["As_topo_cm2"] <= AS_TOPO, (ATO["topo_max"], ATO["base_min"], ATO["As_topo_cm2"])
SIG_TOPO_ISOL = max(p["topo"] for p in ATO["pontos"] if abs(p["x"] - (P["isol"]["L"] / 1000 + LBPT)) < 0.03)
LIM_T_ATO = ATO["lim_t"]


_cm = lambda v: f"{v / 10:g}".replace(".", ",")
TXT_C1 = f"{N_ATIVAS} cord. Ø12,7 aderentes (y {_cm(P['y1'])}: x 0, ±4, ±15,5; y {_cm(P['y2'])}: x 0)"
TXT_C2 = f"{N_ISOL} cord. Ø12,7 (y {_cm(P['y2'])}, x ±4 e ±15,5) com bainha nos {P['isol']['L'] / 1000:.2f} m de cada ponta".replace("3.00", "3,00")
TXT_LINHAS = f"{len(P['x_cord'])} a {_cm(P['y1'])} + {len(P['x_cord2'])} a {_cm(P['y2'])} cm"


def armacao_ts01():
    """Armação passiva da TS-01 sem dente (cm na relação; geo = forma em escala para a prancha de armaduras).
    Apoio direto no neoprene: N7 grampos horizontais de apoio na mesa inferior e N8 estribos de fretagem (transferência da protensão)."""
    zona = 1500
    x_est = sorted(set(list(range(60, zona + 1, 150)) + list(range(zona + 250, L - zona, 250)) + list(range(L - 60, L - zona - 1, -150))))
    n1 = len(x_est)
    cN1, cN3, cN6 = round((2 * (90 + 840) + 140) / 10), round((2 * (340 + 70) + 140) / 10), round((2 * (340 + 840) + 140) / 10)
    n3 = round(L / 250) + 1
    barras = [dict(pos="N1", diam=6.3, qtd=n1, comp=cN1, forma=[(0, 0), (9, 0), (9, 84), (0, 84), (0, 0), (1.5, 1.5)], trechos=["9", "84", "9", "84"], geo=dict(k="E", a=9, b=84)),
              dict(pos="N2", diam=12.5, qtd=4, comp=round((L - 60) / 10), trechos=[f"{(L - 60) / 10:.0f}"], geo=dict(k="R", a=round((L - 60) / 10))),
              dict(pos="N3", diam=6.3, qtd=n3, comp=cN3, forma=[(0, 0), (34, 0), (34, 7), (0, 7), (0, 0), (1.5, 1.5)], trechos=["34", "7", "34", "7"], geo=dict(k="E", a=34, b=7)),
              dict(pos="N4", diam=6.3, qtd=n3, comp=cN3, forma=[(0, 0), (34, 0), (34, 7), (0, 7), (0, 0), (1.5, 1.5)], trechos=["34", "7", "34", "7"], geo=dict(k="E", a=34, b=7)),
              dict(pos="N5", diam=12.5, qtd=2, comp=round((L - 60) / 10), trechos=[f"{(L - 60) / 10:.0f}"], geo=dict(k="R", a=round((L - 60) / 10))),
              dict(pos="N6", diam=8.0, qtd=2 * 8, comp=cN6, forma=[(0, 0), (34, 0), (34, 84), (0, 84), (0, 0), (1.5, 1.5)], trechos=["34", "84", "34", "84"], geo=dict(k="E", a=34, b=84)),
              dict(pos="N7", diam=10.0, qtd=2 * 3, comp=2 * 60 + 34, forma=[(60, 0), (0, 0), (0, 34), (60, 34)], trechos=["60", "34", "60"], geo=dict(k="U", a=60, b=34, g=0)),
              dict(pos="N8", diam=10.0, qtd=2 * 2, comp=round((2 * (750 + 340) + 140) / 10),
                   forma=[(0, 0), (75, 0), (75, 34), (0, 34), (0, 0), (1.5, 1.5)], trechos=["75", "34", "75", "34"], geo=dict(k="E", a=75, b=34)),
              # DEC-032: tração no topo no ato (NBR 6118:2023 17.2.4.3.2 c) — 2 Ø10 complementares ao N2 em cada ponta
              dict(pos="N9", diam=12.5, qtd=2 * 2, comp=round(L_N9 / 10), trechos=[f"{L_N9 / 10:.0f}"], geo=dict(k="R", a=round(L_N9 / 10)))]
    return x_est, [], barras


def tipo_terca(s):
    return "CH-T2" if any(abs(s - n) < 1 for n in P["nos"]) else "CH-T1"


if __name__ == "__main__":
    print("L", L, "peso kN", round(peso, 1), "t", round(peso / 10.0, 2), "V", round(V, 3))
    print("TR", json.dumps(TR, indent=0))
    print("alça Fd", round(ALCA_Fd, 1), "cap", round(ALCA_cap, 1), "P0", R.linhas["P0_kN"])
    print("ATO", {k: v for k, v in ATO.items() if k != "pontos"}, "lbpt", round(LBPT, 3), round(LBPT_BRUSCA, 3), "L_N9", L_N9)
    print({k: v for k, v in R.linhas.items() if k != "perdas"})
