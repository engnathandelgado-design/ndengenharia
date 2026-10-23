"""Letsara rev09 (23/10/2026) — cobertura METÁLICA da linha 2 (DEC-046 / DEC-048, decisão do Nathan: opção 2 do quadro).

As duas TS-01 de concreto da linha 2 saem. No lugar: viga laminada W 310 × 44,5 (Gerdau, ASTM A572 Gr. 50) contínua do eixo A
ao E, com o TOPO na inclinação atual da cobertura (terças, telhado e platibanda não mudam), apoiada SÓ sobre os pilares por
montantes curtos W 150 × 22,5 (sem montante nas vigas do mezanino):
  A — recuo do P1-L2 (+7,195), B — topo do P8 (+7,30), C — topo do P8A (+7,776), D — topo do P8B (+7,30),
  P6 da linha 2 — topo (+7,30), E — recuo do P2-L2 (+8,369).
Mão-francesa em TODA terça da linha 2 (trava a mesa inferior, comprimida pela sucção). Ligações 100 % parafusadas; módulos
≤ 12 m emendados com talas parafusadas; montantes com chapa de base e 4 barras roscadas M20 embutidas no topo do pilar
(padrão Mitsubishi), grampo de ancoragem.

Cargas (kN/m na linha, faixa (9,65 + 10,075)/2): pacote da cobertura e terças (ligacoes.json), peso do perfil;
sobrecarga 0,25 kN/m² (NBR 6120); vento NBR 6123 (V0 45, S3 0,95): Cpe −0,8 no corpo e −1,4 nas faixas locais de 5,925 m junto
às fachadas A e E; Cpi 0 no anexo (mezanino) e +0,2 na área aberta (lado do pavilhão). Combinações NBR 8681 / NBR 8800:2024:
ELU1 1,4 G + 1,5 Q; ELU2 1,0 G(fav) + 1,4 W; ELS L/250 (Tab. B.1, viga de cobertura).
Unidades: kN, m.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

AQ = Path(__file__).parent
sys.path.insert(0, str(AQ.parents[1]))
sys.path.insert(0, str(AQ))
from nd_estruturas import metalica_laminada as ML
from nd_estruturas import vento_nbr6123 as VNT
from geometria import X_EIXO, Y_LIN, P6_L2

LG = json.loads((AQ / "ligacoes.json").read_text(encoding="utf-8"))
CB = json.loads((AQ / "cobertura_metalica.json").read_text(encoding="utf-8"))
PERFIL, PERFIL_M = "W 310 x 32,7", "W 150 x 22,5"      # 44,5 do quadro de 23/10 era estimativa; a contínua pede 32,7 (uso 0,79)
W, WM = ML.perfil(PERFIL), ML.perfil(PERFIL_M)
TRIB = (Y_LIN[1] - Y_LIN[0] + Y_LIN[2] - Y_LIN[1]) / 2
INCL, C3 = 0.03, math.cos(math.atan(0.03))
Z0 = LG["Z0_TS"]
zt = lambda x: Z0 + INCL * x + 0.90 / C3                    # topo da TS-01 de hoje = topo da W (inclinação da cobertura)
S_TER = LG["passo_tercas"]
W_TERCA = CB["perfil"]["kg_m"] * 9.81e-3 / S_TER            # kN/m² (terças)
CC = LG["cargas_cob"]
g_k = (CC["g_total_sem_terca"] + W_TERCA) * TRIB + W.peso
g_fav = (CC["g_favoravel_sucao"] + W_TERCA) * TRIB + W.peso
q_k = CC["sobrecarga"] * TRIB
QV = VNT.q(10.0, 45.0, S3=0.95)
CPE = VNT.cpe_cobertura(10.0, X_EIXO["E"])
LOC = CPE["largura_local"]
LADO = ((Y_LIN[1] - Y_LIN[0]) / 2, 0.0), ((Y_LIN[2] - Y_LIN[1]) / 2, VNT.cpi_duas_faces(True))   # (faixa, Cpi): anexo / área aberta


def w_suc(x):
    cpe = CPE["local"] if (x <= LOC or x >= X_EIXO["E"] - LOC) else CPE["barlavento"]
    return sum(b * (cpe - cpi) for b, cpi in LADO) * QV           # kN/m (negativo = para cima)


# apoios (centro dos montantes) — eixo dos pilares; nos eixos A/E o montante fica no recuo (30 cm da face externa da cabeça)
APOIOS = [("A", 0.15, LG["REC"][0], "recuo do P1-L2"), ("B", X_EIXO["B"], 7.30, "topo do P8"), ("C", X_EIXO["C"], LG["Z_TOPO_I130"], "topo do P8A"),
          ("D", X_EIXO["D"], 7.30, "topo do P8B"), ("P6", P6_L2[0], 7.30, "topo do P6 da linha 2"), ("E", X_EIXO["E"] - 0.15, LG["REC"][1], "recuo do P2-L2")]
XA, XB = 0.025, X_EIXO["E"] - 0.025                           # pontas da W (25 mm da face da cabeça, como a TS-01)


def viga_continua(cargas, n_el=800):
    """Viga contínua Euler-Bernoulli (EI constante) com apoios simples em APOIOS; cargas(x) em kN/m (+ para baixo)."""
    xs = np.linspace(XA, XB, n_el + 1)
    for _, xa, _, _ in APOIOS:
        xs = np.sort(np.unique(np.append(xs, xa)))
    n = len(xs)
    EI = 200e6 * W.Ix * 1e-8
    K = np.zeros((2 * n, 2 * n)); F = np.zeros(2 * n)
    for i in range(n - 1):
        L = xs[i + 1] - xs[i]
        k = EI / L ** 3 * np.array([[12, 6 * L, -12, 6 * L], [6 * L, 4 * L * L, -6 * L, 2 * L * L], [-12, -6 * L, 12, -6 * L], [6 * L, 2 * L * L, -6 * L, 4 * L * L]])
        idx = [2 * i, 2 * i + 1, 2 * i + 2, 2 * i + 3]
        K[np.ix_(idx, idx)] += k
        w = cargas((xs[i] + xs[i + 1]) / 2)
        F[idx] += -w * np.array([L / 2, L * L / 12, L / 2, -L * L / 12])
    fix = [2 * int(np.argmin(abs(xs - xa))) for _, xa, _, _ in APOIOS]
    livres = [d for d in range(2 * n) if d not in fix]
    u = np.zeros(2 * n)
    u[livres] = np.linalg.solve(K[np.ix_(livres, livres)], F[livres])
    R = K @ u - F
    M, V = np.zeros(n), np.zeros(n)
    for i in range(n - 1):
        L = xs[i + 1] - xs[i]
        k = EI / L ** 3 * np.array([[12, 6 * L, -12, 6 * L], [6 * L, 4 * L * L, -6 * L, 2 * L * L], [-12, -6 * L, 12, -6 * L], [6 * L, 2 * L * L, -6 * L, 4 * L * L]])
        idx = [2 * i, 2 * i + 1, 2 * i + 2, 2 * i + 3]
        w = cargas((xs[i] + xs[i + 1]) / 2)
        f = k @ u[idx] - (-w * np.array([L / 2, L * L / 12, L / 2, -L * L / 12]))
        M[i] = -f[1]; V[i] = f[0]
        M[i + 1] = f[3]
    reac = {nm: float(R[d]) for (nm, _, _, _), d in zip(APOIOS, fix)}
    return xs, u[0::2], M, V, reac


def main():
    casos = {
        "ELU1 gravidade (1,4 G + 1,5 Q)": lambda x: 1.4 * g_k + 1.5 * q_k,
        "ELU2 sucção (1,0 G + 1,4 W)": lambda x: g_fav + 1.4 * w_suc(x),
        "ELS G + Q": lambda x: g_k + q_k,
        "ELS Q": lambda x: q_k,
    }
    res = {}
    for nome, c in casos.items():
        xs, d, M, V, R = viga_continua(c)
        res[nome] = dict(Mmax=float(M.max()), Mmin=float(M.min()), Vmax=float(abs(V).max()), d_mm=float(abs(d).max() * 1e3), R=R,
                         x_Mmax=float(xs[int(np.argmax(M))]), x_Mmin=float(xs[int(np.argmin(M))]))
    # resistências (NBR 8800:2024): mesa superior travada pelas terças (Lb = passo); mesa inferior travada pelas mãos-francesas em toda terça
    MRd_tr = ML.momento_resistente(W, S_TER, 1.0).MRd
    VRd = ML.cortante_resistente(W)
    Lmax = max(b[1] - a[1] for a, b in zip(APOIOS[:-1], APOIOS[1:]))
    g1, g2 = res["ELU1 gravidade (1,4 G + 1,5 Q)"], res["ELU2 sucção (1,0 G + 1,4 W)"]
    Msd = max(abs(g1["Mmax"]), abs(g1["Mmin"]), abs(g2["Mmax"]), abs(g2["Mmin"]))
    flecha = dict(GQ_mm=round(res["ELS G + Q"]["d_mm"], 1), Q_mm=round(res["ELS Q"]["d_mm"], 1), lim_L250_mm=round(Lmax / 250 * 1e3, 1),
                  contraflecha_mm=0, obs="sem contraflecha (flecha de G + Q < L/250)")
    # montantes W 150 × 22,5 (altura = fundo da W − topo do apoio − chapa de base 12,5 − chapa de topo 12,5)
    mont = []
    for (nm, xa, z_ap, onde) in APOIOS:
        h = round(zt(xa) - W.d / 1000 - z_ap - 0.025, 3)
        Nc = g1["R"][nm]
        Nt = -g2["R"][nm]
        H_y = 0.02 * Nc                                         # força horizontal nocional (NBR 8800 4.9.7) + transferência de terça
        Msd_b = H_y * h
        comp = ML.verificar_barra(WM, N=-Nc, Mx=0.0, My=Msd_b, KLx=2.0 * h, KLy=2.0 * h, Lb=h)
        # chapa de base 250 × 250 × 19, 4 barras roscadas M20 8.8 embutidas 400 mm com grampo (padrão Mitsubishi)
        s_y = 0.150
        T_bar = max(0.0, Nt) / 4 + Msd_b / (2 * s_y)
        Rd_bar = 0.75 * 800e3 * 245e-6 / 1.35                    # NBR 8800:2024 6.3.3.1 (tração no parafuso, Abe = 0,75 Ab)
        mont.append(dict(apoio=nm, onde=onde, x=round(xa, 3), z_base=round(z_ap, 3), h_m=h, Nc_d=round(Nc, 1), Nt_d=round(max(0.0, Nt), 1),
                         My_base_d=round(Msd_b, 2), uso_compressao=round(comp["razao_interacao"], 3), T_barra_d=round(T_bar, 1), Rd_barra=round(Rd_bar, 1),
                         uso_barra=round(T_bar / Rd_bar, 3), base="chapa 250 × 250 × 19 + 4 barras roscadas M20 8.8 (hef 400 + grampo) embutidas no pilar"))
    # emendas: perto do ponto de momento nulo, módulos ≤ 12 m
    em = [11.60, 23.45, 33.30]
    mods = [round(b - a, 2) for a, b in zip([XA] + em, em + [XB])]
    # mão-francesa: L 51 × 51 × 4,8 da mesa inferior da W à terça; força 2 % da força na mesa (NBR 8800:2024 4.11.3)
    Fmesa = Msd / (W.d / 1000 - W.tf / 1000)
    F_mf = 0.02 * Fmesa
    L_mf = math.hypot(0.30, W.d / 1000)
    Ncr_mf = 200e6 * 2.9e-8 * math.pi ** 2 / L_mf ** 2          # L 51×51×4,8: I_min ≈ 2,9 cm⁴ (eixo z)
    out = dict(
        perfil=PERFIL, aco="ASTM A572 Gr. 50 (fy 345 MPa)", montante=PERFIL_M, trib_m=round(TRIB, 3),
        cargas_kN_m=dict(g_k=round(g_k, 2), g_fav=round(g_fav, 2), q_k=round(q_k, 2), w_suc_corpo=round(w_suc(X_EIXO["C"]), 2), w_suc_local=round(w_suc(1.0), 2), qv=round(QV, 3)),
        apoios=[dict(nome=nm, x=round(xa, 3), z_apoio=z_ap, onde=o) for nm, xa, z_ap, o in APOIOS], vao_max_m=round(Lmax, 3),
        esforcos={k: dict(Mmax=round(v["Mmax"], 1), Mmin=round(v["Mmin"], 1), Vmax=round(v["Vmax"], 1), d_mm=round(v["d_mm"], 1),
                          R={a: round(b, 1) for a, b in v["R"].items()}) for k, v in res.items()},
        verificacoes=dict(MRd=round(MRd_tr, 1), Msd=round(Msd, 1), uso_M=round(Msd / MRd_tr, 3), VRd=round(VRd, 1), Vsd=round(max(g1["Vmax"], g2["Vmax"]), 1),
                          uso_V=round(max(g1["Vmax"], g2["Vmax"]) / VRd, 3), Lb_m=S_TER, norma="NBR 8800:2024 5.4.2 / Anexo D e 5.4.3"),
        flecha=flecha, montantes=mont, emendas_x=em, modulos_m=mods,
        mao_francesa=dict(perfil="L 51 × 51 × 4,8 (2\" × 3/16\")", em="todas as terças da linha 2 (dos dois lados da W)", F_d=round(F_mf, 1), L_m=round(L_mf, 3),
                          Ncr_kN=round(Ncr_mf, 1), parafusos="1 M12 8.8 em cada ponta", norma="NBR 8800:2024 4.11 (travamento: 2 % da força na mesa)"),
        terca_sobre_W="ST-W: chapa dobrada 6,3 (igual ao ST-1P) parafusada na mesa superior da W com 2 M12 e na alma da terça com 2 M12 (furos da terça iguais)",
        ok=Msd <= MRd_tr and max(g1["Vmax"], g2["Vmax"]) <= VRd and flecha["GQ_mm"] <= flecha["lim_L250_mm"] and all(m_["uso_compressao"] <= 1 and m_["uso_barra"] <= 1 for m_ in mont)
           and max(mods) <= 12.0,
    )
    (AQ / "cob_linha2.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    return out


if __name__ == "__main__":
    o = main()
    print(json.dumps({k: o[k] for k in ("cargas_kN_m", "verificacoes", "flecha", "modulos_m", "ok")}, ensure_ascii=False, indent=1))
    for m_ in o["montantes"]:
        print(m_)
    for k, v in o["esforcos"].items():
        print(k, v)
