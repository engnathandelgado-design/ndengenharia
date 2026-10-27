"""Letsara DEC-059 (24/10/2026, decisão do Nathan: opção A do quadro decisao_portao_l4) — pilares dos portões da linha 4
(PG-01 a PG-04) passam a APOIAR a TS-01A depois da montagem: neoprene na cabeça + calço de graute injetado entre o neoprene e o
fundo da TS-01A (folga de montagem de 20 mm), feito com a TS-01A montada e antes da cobertura. Assim a viga não desce nos vãos
dos portões e o fundo fica ≥ +7,50 (portões 500 × 750 do arquitetônico).

Fases (NBR 9062:2017 5.2.1.4):
  1) montagem: TS-01A biapoiada (pilar lateral × P11), peso próprio g1 e protensão — sem mudança (ts01_dados);
  2) depois do graute: g2 (cobertura completa) + q (sobrecarga) + vento na viga CONTÍNUA sobre os 2 PG de cada metade
     (apoio unilateral: o PG só comprime; na sucção a viga levanta do PG e vale a viga biapoiada — já verificada em ts01_dados).
Verificações: momento negativo sobre o PG (ELU, NBR 6118:2023 17.2: N2 4 Ø12,5 + cordoalhas ignoradas a favor), tensão no topo
sobre o PG (ELS-F na combinação rara, protensão completa, DEC-043: P∞ + g1 biapoiado + (g2 + q) contínuo ≤ 1,3·fctk,inf,
17.3.4), alívio do positivo, reação no PG (compressão do pilar, NBR 6118:2023 15.8.3.3.2, pilar-padrão com curvatura aproximada,
topo travado pela TS-01A em x pelo neoprene e em y pelas CL-P → le = 0,7·H), neoprene (NBR 9062:2017 7.2.1.6).
A fluência da protensão depois do graute é para CIMA (afasta a viga do PG) e foi desprezada a favor da segurança no negativo.
Unidades kN, m, MPa. Grava portao_l4.json."""
import json, math, sys
from pathlib import Path
AQ = Path(__file__).resolve().parent
sys.path.insert(0, str(AQ)); sys.path.insert(0, str(AQ / "pranchas")); sys.path.insert(0, str(AQ.parents[1]))
import ts01_dados as T
from geometria import X_L4, X_EIXO, PG_L4, Y_PG, DY_PG, Y_FACE_L4

LG = T.LG
XC = X_EIXO["C"]
E = T.C.Ecs * 1e3                                    # kPa
I = T.sec.I
g2, q = T.car.g2, T.car.q
# apoios das duas metades (x ao longo da obra, m): neoprene do pilar lateral, 2 PG, neoprene no eixo C (P11)
X_NE, X_NC = LG["NEO_EXT"]["xc"], LG["NEO_CEN"]["xc"]
METADES = {"A–C (V410)": [X_NE, X_L4[1], X_L4[2], X_NC], "C–E (V411)": [2 * XC - X_NC, X_L4[4], X_L4[5], X_EIXO["E"] - X_NE]}
NOMES_PG = {"A–C (V410)": ("PG-01", "PG-02"), "C–E (V411)": ("PG-04", "PG-03")}


def viga_continua(xs_ap, w, n_el=200):
    """viga contínua (Euler-Bernoulli) com apoios em xs_ap e carga uniforme w (kN/m, para baixo): reações e M(x)."""
    x0, x1 = xs_ap[0], xs_ap[-1]
    nos = sorted(set([x0 + (x1 - x0) * k / n_el for k in range(n_el + 1)] + list(xs_ap)))
    n = len(nos)
    K = [[0.0] * (2 * n) for _ in range(2 * n)]
    F = [0.0] * (2 * n)
    for e in range(n - 1):
        L = nos[e + 1] - nos[e]
        k = E * I / L ** 3
        ke = [[12, 6 * L, -12, 6 * L], [6 * L, 4 * L * L, -6 * L, 2 * L * L], [-12, -6 * L, 12, -6 * L], [6 * L, 2 * L * L, -6 * L, 4 * L * L]]
        dofs = [2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3]
        fe = [-w * L / 2, -w * L * L / 12, -w * L / 2, w * L * L / 12]
        for a in range(4):
            F[dofs[a]] += fe[a]
            for b in range(4):
                K[dofs[a]][dofs[b]] += k * ke[a][b]
    fixos = [2 * nos.index(x) for x in xs_ap]
    livres = [d for d in range(2 * n) if d not in fixos]
    import numpy as np
    Kf = np.array([[K[a][b] for b in livres] for a in livres]); Ff = np.array([F[a] for a in livres])
    u = np.zeros(2 * n); u[livres] = np.linalg.solve(Kf, Ff)
    R = np.array(K) @ u - np.array(F)
    reac = [float(R[d]) for d in fixos]
    # momento por equilíbrio a partir da esquerda (positivo = tração embaixo)
    M = []
    for x in nos:
        m = sum(r * (x - xa) for r, xa in zip(reac, xs_ap) if xa <= x + 1e-9) - w * (x - x0) ** 2 / 2
        M.append(m)
    return dict(x=nos, M=M, R=reac)


def biapoiada(x, xa, xb, w):
    L = xb - xa
    s = x - xa
    return w * s * (L - s) / 2


out = {}
Pinf = T.R.linhas["Pinf_kN"]
ep = T.sec.yc - T.P["y_cord"] / 1000
Ws = T.sec.I / (T.sec.h - T.sec.yc)
lim_F = 1.3 * T.C.fctk_inf
As_N2 = 4 * 1.227e-4
d_top = T.sec.h - 0.04
for nome, xs in METADES.items():
    xa, xb = xs[0], xs[-1]
    rg, rq = viga_continua(xs, g2), viga_continua(xs, q)
    rb_g = [biapoiada(x, xa, xb, g2) for x in rg["x"]]
    i_pg = [rg["x"].index(x) for x in xs[1:3]]
    # ELU: negativo sobre o PG (1,3 g2 + 1,4 q no contínuo; g1 biapoiado é positivo e alivia: ignorado no negativo, a favor)
    Md_neg = min(1.3 * rg["M"][i] + 1.4 * rq["M"][i] for i in i_pg)
    # momento positivo total depois do graute ≤ biapoiado (alívio)
    alivio = max(rb_g) - max(rg["M"])
    # ELU resistente ao negativo: N2 4 Ø12,5 no topo (zona tracionada), braço 0,9 d; cordoalhas embaixo comprimidas (desprezadas)
    MRd_neg = As_N2 * 435e3 * 0.9 * d_top
    # ELS-F (rara, completa): topo sobre o PG = P∞ (tração no topo) + g1 biapoiado + (g2 + q) contínuo
    els = []
    for i in i_pg:
        x = rg["x"][i]
        Mg1 = biapoiada(x, xa, xb, T.car.g1)
        M = Mg1 + rg["M"][i] + rq["M"][i]
        s_top = -Pinf / T.sec.A + Pinf * ep / Ws - M / Ws       # MPa·1e-3 → kPa
        els.append(round(s_top / 1000, 3))
    # reações nos PG: característica e de cálculo (só compressão)
    R = [dict(pg=pg, Rg=round(rg["R"][k], 1), Rq=round(rq["R"][k], 1), Rd=round(1.3 * rg["R"][k] + 1.4 * rq["R"][k], 1)) for k, pg in zip((1, 2), NOMES_PG[nome])]
    out[nome] = dict(apoios_x=[round(v, 3) for v in xs], Md_neg_kNm=round(Md_neg, 1), MRd_neg_kNm=round(MRd_neg, 1), uso_neg=round(-Md_neg / MRd_neg, 3),
                     sig_topo_PG_rara_MPa=els, lim_F_MPa=round(lim_F, 2), alivio_positivo_kNm=round(alivio, 1), reacoes=R,
                     ok=(-Md_neg <= MRd_neg) and max(els) <= lim_F)

# pilares PG à compressão (pilar-padrão com curvatura aproximada, NBR 6118:2023 15.8.3.3.2; topo travado: le = 0,7 H)
# rev12 (27/10): PG-02 e PG-04 25×40 (40 em x, ao longo da parede) — b = lado menor (flambagem), bx × by na área
PG = {mk: (min(bx, by), x, bx, by) for mk, (_, x, bx, by) in PG_L4.items()}
ARRJ = json.loads((AQ / "arranjo_pilares.json").read_text(encoding="utf-8"))
pg_out = {}
for mk, (b, x, bx, by) in PG.items():
    Nd = max(r["Rd"] for m in out.values() for r in m["reacoes"] if r["pg"] == mk)
    H = (T.LG["Z0_TS"] + 0.03 * x - 0.02) + 1.0          # topo (fundo da TS − 20 mm) + 1,00 de cálice
    le = 0.7 * H
    lam = le / (b / math.sqrt(12))
    fcd = 40e3 / 1.4
    nu = Nd / (bx * by * fcd)
    r1 = 0.005 / (b * (nu + 0.5))
    e2 = le ** 2 / 10 * min(r1, 0.005 / b)
    M1min = Nd * (0.015 + 0.03 * b)
    Mtot = M1min + Nd * e2
    a = ARRJ.get(mk, {})
    As = a.get("n", 4) * math.pi * (a.get("d", 16) / 1000) ** 2 / 4
    NRd = 0.85 * fcd * bx * by + As * 400e3 / 1.0
    pg_out[mk] = dict(secao_cm=f"{round(by * 100)}×{round(bx * 100)}", x_m=x, y_m=Y_PG[mk], dy_linha4_m=DY_PG[mk], Nd_kN=round(Nd, 1), Nd_tf=round(Nd / 10, 1), H_m=round(H, 2), le_m=round(le, 2), lambda_=round(lam, 1), Md_tot_kNm=round(Mtot, 2),
                      NRd_kN=round(NRd, 0), uso_N=round(Nd / NRd, 3), ok=lam <= 90 and Nd <= NRd,
                      norma="NBR 6118:2023 15.8.3.3.2 (λ ≤ 90) e 11.3.3.4.3 (M1d,mín); flexão do vento nas placas já está no dimensionamento DEC-040")
# neoprene NEO-7 na cabeça do PG: σ ≤ 7 MPa (NBR 9062:2017 7.2.1.6, elastômero simples). rev12 (DEC-092): distância à borda do
# apoio a0 ≥ 1,5 c e ≥ 3 cm (NBR 9062:2017 7.2, c = 3 cm) nas 4 faces da cabeça e na borda da mesa inferior da TS-01A (40, centrada
# na linha 4); neoprene centrado no eixo do pilar → a reação da TS-01A passa no eixo do PG (e = 0 no pilar e na fundação).
A0 = max(1.5 * 0.03, 0.03)
B_TS = 0.40
neo = {}
for mk, (b, x, bx, by) in PG.items():
    Nk = max(r["Rg"] + r["Rq"] for m in out.values() for r in m["reacoes"] if r["pg"] == mk)
    nx = math.floor((bx - 2 * A0) * 100 + 1e-9) / 100                      # ao longo da viga (x)
    ny = min(0.20, math.floor((by - 2 * A0) * 100 + 1e-9) / 100)          # ⊥ à viga (y)
    yc = Y_PG[mk]
    a_ts = round(min(yc - ny / 2 - Y_FACE_L4, (Y_FACE_L4 + B_TS) - (yc + ny / 2)), 3)   # borda da mesa da TS-01A
    a_pg = round(min((bx - nx) / 2, (by - ny) / 2), 3)
    A = nx * ny
    neo[mk] = dict(dim_mm=f"{round(nx * 1000)} × {round(ny * 1000)} × 10", nx_mm=round(nx * 1000), ny_mm=round(ny * 1000), sigma_MPa=round(Nk / A / 1000, 2),
                   a0_min_cm=round(A0 * 100, 1), borda_pilar_cm=round(a_pg * 100, 1), borda_mesa_TS_cm=round(a_ts * 100, 1),
                   y_neo_m=yc, e_pilar_m=0.0, e_na_TS_m=DY_PG[mk],
                   ok=Nk / A / 1000 <= 7.0 and a_pg >= A0 - 1e-9 and a_ts >= A0 - 1e-9)
# placa PV-1 sobre o portão P19–D (P10–P12): 10 × 37 cm, C40 armada, apoiada nas 2 cantoneiras CL-V (vão entre apoios); só peso
# próprio (regra do Nathan para placas: cada placa nos seus apoios, sem carga de outra placa); manuseio por 2 alças a 0,2 L
fck_pv, b_pv, t_pv = 40.0, 0.10, 0.10
x0v, x1v = X_L4[4] + 0.010, X_L4[5] - 0.010
z0v = 7.505
z1v = round(T.LG["Z0_TS"] + 0.03 * (X_L4[4] + PG_L4["PG-04"][2] / 2) - 0.05, 3)
h_pv = round(z1v - z0v, 3)
L_pv = round(x1v - x0v, 3)
Lv = L_pv - 2 * 0.075                                             # vão entre os centros das cantoneiras (150 mm de apoio)
g_pv = 25 * b_pv * h_pv
Md_pv = 1.4 * g_pv * Lv ** 2 / 8                                  # flexão no plano da placa (eixo forte, altura h_pv)
d_pv = h_pv - 0.025 - 0.005 - 0.005
As_pv = Md_pv / (0.87 * d_pv * 435e3) * 1e4                       # cm² (braço 0,87 d)
fctk = 0.7 * 0.3 * fck_pv ** (2 / 3)
sig_pv = g_pv * Lv ** 2 / 8 / (b_pv * h_pv ** 2 / 6) / 1000        # MPa, ELS sem fissura (fctk,inf)
M_ic = 1.3 * 1.3 * g_pv * (0.2 * L_pv) ** 2 / 2                  # içamento βa 1,3 (NBR 9062 5.3.2), 2 alças a 0,2 L
pv = dict(dim=f"10 × {h_pv * 100:.1f} × {L_pv * 100:.1f} cm".replace(".", ","), L_m=L_pv, h_m=h_pv, z0=z0v, z1=z1v, peso_kN=round(g_pv * L_pv, 2), Md_kNm=round(Md_pv, 2),
          As_nec_cm2=round(As_pv, 2), As_adot="N1 2 Ø10 embaixo + N2 2 Ø10 em cima (1,57 cm² cada)", ok_flexao=As_pv <= 1.57, sigma_ELS_MPa=round(sig_pv, 2),
          fctk_inf_MPa=round(fctk, 2), ok_ELS=sig_pv <= fctk, M_icamento_kNm=round(M_ic, 3), alcas="2 alças de cordoalha Ø12,7 no topo a 0,2 L (1 laço cada)",
          estribos="N3 Ø5 c/20 (fechados, 2 ramos)", apoio=dict(CL_V="L 102 × 102 × 9,5 L=150 (PG-03 e PG-04, faces no mesmo plano — DEC-092) com 2 BR-M16 cada",
                                                                    R_d_kN=round(1.4 * g_pv * L_pv / 2, 2), neoprene="tira 75 × 150 × 5 (aba de 102 − folga de 25 até a placa)",
                                                                    trava="CT-V L 76 × 76 × 6,3 L=80 com 1 BR-M16 no PG e 1 M12 vertical em bucha no topo da placa (furo oblongo horizontal)"))
pv["ok"] = pv["ok_flexao"] and pv["ok_ELS"]
res = dict(ts01a=out, pilares=pg_out, neoprene=neo, placa_PV1=pv, ok=all(v["ok"] for v in out.values()) and all(v["ok"] for v in pg_out.values()) and all(v["ok"] for v in neo.values()) and pv["ok"],
           fundo_portao_m={"B–P21": round(T.LG["Z0_TS"] + 0.03 * (X_L4[1] + 0.20), 3), "P19–D": round(T.LG["Z0_TS"] + 0.03 * (X_L4[4] + PG_L4["PG-04"][2] / 2), 3)},
           vao_livre_portoes_m={"PG-01–PG-02": round(X_L4[2] - PG_L4["PG-02"][2] / 2 - X_L4[1] - PG_L4["PG-01"][2] / 2, 3),
                                "PG-04–PG-03": round(X_L4[5] - PG_L4["PG-03"][2] / 2 - X_L4[4] - PG_L4["PG-04"][2] / 2, 3)},
           placa_P19_D=dict(z0=7.50, z1=round(T.LG["Z0_TS"] + 0.03 * (X_L4[4] + PG_L4["PG-04"][2] / 2) - 0.05, 3)))
(AQ / "portao_l4.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(res, ensure_ascii=False, indent=1))
