"""Letsara rev09 — cobertura METÁLICA da linha 2 (DEC-046 / DEC-048 / DEC-050 / DEC-052).

As duas TS-01 de concreto da linha 2 saem. No lugar: viga laminada (Gerdau, ASTM A572 Gr. 50) contínua do eixo A ao E, com o
TOPO na inclinação atual da cobertura (terças, telhado e platibanda não mudam).
  - DEC-048 (23/10): W 310 × 32,7 só sobre os pilares, por montantes W 150.
  - DEC-050 (24/10): sem montantes nos pilares — a cabeça de concreto de cada pilar sobe até o fundo da W.
  - DEC-052 (24/10, Nathan: "viga usando praticamente 100 % do aço", aceita apoio no meio dos vãos): W 200 × 15,0 contínua,
    apoiada nos 6 pilares (A recuo do P1-L2, B P8, C P8A, D P8B, P6 da linha 2, E recuo do P2-L2) e em 4 MONTANTES curtos
    W 150 × 13,0 no meio dos vãos A–B, B–C, C–D e D–P6, nascendo da espera EM-L2 na faixa de 2º estágio da VM do +7,30
    (montados depois da capa curada). P6–E (3,2 m) sem montante.
Ligações 100 % parafusadas (nenhuma solda): a W é presa por parafusos que atravessam a mesa inferior (gabarito 55);
nos pilares 4 barras roscadas M16 embutidas na cabeça; nos montantes 2 cantoneiras em cima e 2 embaixo.
Mesa inferior travada pela mão-francesa só se o cálculo pedir (Lb revisto com os vãos menores).

Cargas (kN/m na linha, faixa (9,65 + 10,075)/2): pacote da cobertura e terças (ligacoes.json), peso do perfil;
sobrecarga 0,25 kN/m² (NBR 6120); vento NBR 6123 (V0 45, S3 0,95): Cpe −0,8 no corpo e −1,4 nas faixas locais de 5,925 m junto
às fachadas A e E; Cpi 0 no anexo (mezanino) e +0,2 na área aberta (lado do pavilhão). Combinações NBR 8681 / NBR 8800:2024:
ELU1 1,4 G + 1,5 Q; ELU2 1,0 G(fav) + 1,4 W; ELS L/250 (Tab. C.1, viga de cobertura).
A viga contínua é resolvida duas vezes: apoios do meio rígidos (reações para montante, espera e VM) e com a mola da VM
(48 Ecs I / L³, peça 30 × 75 sozinha — mais flexível, a favor da W); vale a envoltória.
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
PERFIL, PERFIL_M = "W 200 x 15,0", "W 150 x 13,0"      # DEC-052: viga com apoio no meio dos vãos; montante curto
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




# ------------------------------------------------------------------ apoios
# pilares — eixo dos pilares; nos eixos A/E a W apoia no recuo (30 cm da face externa da cabeça). DEC-050: a cabeça de concreto
# sobe até o fundo da W; graute 20 + chapa CA-L2 250 × 250 × 19.
T_CHAPA, T_GRAUTE = 0.019, 0.020
APOIOS = [("A", 0.15, LG["REC"][0], "recuo do P1-L2"), ("B", X_EIXO["B"], 7.30, "topo do P8"), ("C", X_EIXO["C"], LG["Z_TOPO_I130"], "topo do P8A"),
          ("D", X_EIXO["D"], 7.30, "topo do P8B"), ("P6", P6_L2[0], 7.30, "topo do P6 da linha 2"), ("E", X_EIXO["E"] - 0.15, LG["REC"][1], "recuo do P2-L2")]
XA, XB = 0.025, X_EIXO["E"] - 0.025                           # pontas da W (25 mm da face da cabeça, como a TS-01)
# DEC-052: montantes no meio de cada VM do +7,30 da linha 2 (entre as faces dos pilares; meia-largura dos pilares como no modelo 3D)
MEIA = {"A": 0.30, "B": 0.20, "C": 0.20, "D": 0.20, "P6": 0.125}
VM_DO_VAO = {("A", "B"): "VM-01", ("B", "C"): "VM-02", ("C", "D"): "VM-02", ("D", "P6"): "VM-03"}
_xap = {nm: xa for nm, xa, _, _ in APOIOS}
_xeixo = {"A": 0.0, "B": X_EIXO["B"], "C": X_EIXO["C"], "D": X_EIXO["D"], "P6": P6_L2[0]}
MEIOS = []
for (a_, b_), mk in VM_DO_VAO.items():
    fa, fb = _xeixo[a_] + MEIA[a_], _xeixo[b_] - MEIA[b_]
    MEIOS.append(dict(nome=f"M{a_}{b_}", vao=f"{a_}–{b_}", vm=mk, x=round((fa + fb) / 2, 3), L_vm=round(fb - fa - 0.06, 3)))
# mola da VM no meio do vão (peça 30 × 75 isolada, C40: Ecs = αi Eci — NBR 6118:2023 8.2.8)
ECS_VM = (0.8 + 0.2 * 40 / 80) * 5600 * math.sqrt(40) * 1e3   # kN/m²
I_VM = 0.30 * 0.75 ** 3 / 12
for m_ in MEIOS:
    m_["k_mola"] = round(48 * ECS_VM * I_VM / m_["L_vm"] ** 3)


def viga_continua(cargas, molas=False, n_el=800):
    """Viga contínua Euler-Bernoulli (EI constante): apoios simples nos pilares; nos montantes apoio rígido ou mola da VM."""
    pts = [(nm, xa, None) for nm, xa, _, _ in APOIOS] + [(m_["nome"], m_["x"], m_["k_mola"] if molas else None) for m_ in MEIOS]
    xs = np.linspace(XA, XB, n_el + 1)
    for _, xa, _ in pts:
        xs = np.sort(np.unique(np.append(xs, xa)))
    n = len(xs)
    EI = 200e6 * W.Ix * 1e-8
    K = np.zeros((2 * n, 2 * n)); F = np.zeros(2 * n)

    def kel(L):
        return EI / L ** 3 * np.array([[12, 6 * L, -12, 6 * L], [6 * L, 4 * L * L, -6 * L, 2 * L * L], [-12, -6 * L, 12, -6 * L], [6 * L, 2 * L * L, -6 * L, 4 * L * L]])
    for i in range(n - 1):
        L = xs[i + 1] - xs[i]
        idx = [2 * i, 2 * i + 1, 2 * i + 2, 2 * i + 3]
        K[np.ix_(idx, idx)] += kel(L)
        w = cargas((xs[i] + xs[i + 1]) / 2)
        F[idx] += -w * np.array([L / 2, L * L / 12, L / 2, -L * L / 12])
    fix, mol = [], {}
    for nm, xa, k in pts:
        d = 2 * int(np.argmin(abs(xs - xa)))
        if k is None:
            fix.append(d)
        else:
            K[d, d] += k; mol[nm] = (d, k)
    livres = [d for d in range(2 * n) if d not in fix]
    u = np.zeros(2 * n)
    u[livres] = np.linalg.solve(K[np.ix_(livres, livres)], F[livres])
    R = K @ u - F
    M, V = np.zeros(n), np.zeros(n)
    for i in range(n - 1):
        L = xs[i + 1] - xs[i]
        idx = [2 * i, 2 * i + 1, 2 * i + 2, 2 * i + 3]
        w = cargas((xs[i] + xs[i + 1]) / 2)
        f = kel(L) @ u[idx] - (-w * np.array([L / 2, L * L / 12, L / 2, -L * L / 12]))
        M[i] = -f[1]; V[i] = f[0]
        M[i + 1] = f[3]
    reac = {}
    for nm, xa, k in pts:
        d = 2 * int(np.argmin(abs(xs - xa)))
        reac[nm] = float(mol[nm][1] * u[d]) * -1 if nm in mol else float(R[d])
    return xs, u[0::2], M, V, reac


def tstub(n_paraf_lado, leff_paraf, tf, fy, m, e, Ft_Rd, gama=1.10):
    """Mesa/aba em T-stub (referência: EN 1993-1-8:2005 6.2.4, modos 1, 2 e 3; a NBR 8800:2024 não traz o modelo).
    Devolve a força resistente de um lado (kN) com n parafusos; m, e em m; tf em m; fy em kPa."""
    Mpl = 0.25 * n_paraf_lado * leff_paraf * tf ** 2 * fy / gama
    n_ = min(e, 1.25 * m)
    F1 = 4 * Mpl / m
    F2 = (2 * Mpl + n_ * n_paraf_lado * Ft_Rd) / (m + n_)
    F3 = n_paraf_lado * Ft_Rd
    return min(F1, F2, F3), dict(modo1=round(F1, 1), modo2=round(F2, 1), modo3=round(F3, 1), m_mm=round(m * 1e3, 1), leff_mm=round(n_paraf_lado * leff_paraf * 1e3))


# parafusos e barras 8.8 (NBR 8800:2024 6.3.3): tração Abe = 0,75 Ab; corte com rosca no plano 0,4 Ab fub; γa2 = 1,35
def Ft(d_mm):
    return 0.75 * 800e3 * math.pi * (d_mm / 1000) ** 2 / 4 / 1.35


def Fv(d_mm):
    return 0.4 * 800e3 * math.pi * (d_mm / 1000) ** 2 / 4 / 1.35


def Fc(d_mm, t_m, fu=450e3):                                # pressão de contato no furo (NBR 8800:2024 6.3.3.3, rasgamento não governa)
    return 2.4 * d_mm / 1000 * t_m * fu / 1.35


G_MESA = 0.055                                              # gabarito dos furos na mesa da W 200 (bf 100): ±27,5 do eixo
R_W = (W.h - W.d_linha) / 2 / 1000                          # raio de concordância mesa-alma


def mesa_w_tstub(Nt_lado, n_lado=2):
    """Mesa inferior da W em T-stub: 2 parafusos de cada lado da alma (furos a ±27,5)."""
    m = G_MESA / 2 - W.tw / 2000 - 0.8 * R_W
    e = W.bf / 2000 - G_MESA / 2
    leff = min(2 * math.pi * m, 4 * m + 1.25 * e)
    Fr, det = tstub(n_lado, leff, W.tf / 1000, 345e3, m, e, Ft(16))
    return round(Nt_lado / Fr, 3), dict(det, F_Rd_lado=round(Fr, 1))


def main():
    casos = {
        "ELU1 gravidade (1,4 G + 1,5 Q)": lambda x: 1.4 * g_k + 1.5 * q_k,
        "ELU2 sucção (1,0 G + 1,4 W)": lambda x: g_fav + 1.4 * w_suc(x),
        "ELS G + Q": lambda x: g_k + q_k,
        "ELS G": lambda x: g_k,
        "ELS Q": lambda x: q_k,
    }
    res, env = {}, {}
    for nome, c in casos.items():
        for mol in (False, True):
            xs, d, M, V, R = viga_continua(c, molas=mol)
            res[(nome, mol)] = dict(xs=xs, M=M, V=V, d=d, R=R)
    for nome in casos:
        a, b = res[(nome, False)], res[(nome, True)]
        env[nome] = dict(Mmax=float(max(a["M"].max(), b["M"].max())), Mmin=float(min(a["M"].min(), b["M"].min())),
                         Vmax=float(max(abs(a["V"]).max(), abs(b["V"]).max())), d_mm=float(max(abs(a["d"]).max(), abs(b["d"]).max()) * 1e3),
                         R_rigido=a["R"], R_mola=b["R"])
    g1, g2 = env["ELU1 gravidade (1,4 G + 1,5 Q)"], env["ELU2 sucção (1,0 G + 1,4 W)"]
    # flexão (NBR 8800:2024 5.4.2 / Anexo D): mesa superior travada pelas terças (Lb = passo); mesa inferior: sem mão-francesa
    # travada só nos apoios (Lb = maior trecho entre apoios, Cb = 1 a favor da segurança); com mão-francesa Lb = passo
    xs_ap = sorted([xa for _, xa, _, _ in APOIOS] + [m_["x"] for m_ in MEIOS])
    L_trechos = [b - a for a, b in zip(xs_ap[:-1], xs_ap[1:])]
    Lmax = max(L_trechos)
    MRd_ter = ML.momento_resistente(W, S_TER, 1.0).MRd
    MRd_sem_mf = ML.momento_resistente(W, Lmax, 1.0).MRd
    M_sup_comp = max(g1["Mmax"], -g2["Mmin"])               # mesa superior comprimida: vão sob gravidade / apoio sob sucção
    M_inf_comp = max(-g1["Mmin"], g2["Mmax"])               # mesa inferior comprimida: apoio sob gravidade / vão sob sucção
    uso_sem_mf = max(M_sup_comp / MRd_ter, M_inf_comp / MRd_sem_mf)
    precisa_mf = uso_sem_mf > 1.0
    MRd_inf = MRd_ter if precisa_mf else MRd_sem_mf
    uso_M = max(M_sup_comp / MRd_ter, M_inf_comp / MRd_inf)
    VRd = ML.cortante_resistente(W)
    Vsd = max(g1["Vmax"], g2["Vmax"])
    flecha = dict(GQ_mm=round(env["ELS G + Q"]["d_mm"], 1), Q_mm=round(env["ELS Q"]["d_mm"], 1), lim_L250_mm=round(Lmax / 250 * 1e3, 1),
                  contraflecha_mm=0, obs="com a mola da VM no meio dos vãos; sem contraflecha")
    # ---------------- apoios nos pilares: W direto na cabeça (DEC-050), 4 BR-M16 atravessando a mesa (gabarito 55 × 150)
    lb_ch = 0.250
    k_ = (W.tf + R_W * 1000) / 1000
    tw, tf, d_ = W.tw / 1000, W.tf / 1000, W.d / 1000
    def alma(Nc, lb):                                        # NBR 8800:2024 5.7.3 (escoamento local) e 5.7.4 (enrugamento), sem enrijecedor
        Rd_esc = (5 * k_ + lb) * 345e3 * tw / 1.10
        Rd_enr = 0.66 * tw ** 2 * (1 + 3 * (lb / d_) * (tw / tf) ** 1.5) * math.sqrt(200e6 * 345e3 * tf / tw) / 1.10
        return Rd_esc, Rd_enr, Nc / min(Rd_esc, Rd_enr)
    pil = []
    for (nm, xa, z_ant, onde) in APOIOS:
        z_fundo_w = zt(xa) - W.d / 1000
        z_conc = math.floor((z_fundo_w - T_CHAPA - T_GRAUTE) * 1000) / 1000
        Nc = max(g1["R_rigido"][nm], g1["R_mola"][nm])
        Nt = max(0.0, -g2["R_rigido"][nm], -g2["R_mola"][nm])
        H_y = 0.02 * Nc                                      # força horizontal nocional (NBR 8800:2024 4.9.7)
        uso_bar = (Nt / 4 / Ft(16)) ** 2 + (H_y / 4 / Fv(16)) ** 2
        Rd_esc, Rd_enr, uso_alma = alma(Nc, lb_ch)
        uso_mesa, det_m = mesa_w_tstub(Nt / 2)
        pil.append(dict(nome=nm, onde=onde, x=round(xa, 3), z_concreto=z_conc, z_fundo_w=round(z_fundo_w, 3), z_antes=round(z_ant, 3),
                        sobe_m=round(z_conc - z_ant, 3), Nc_d=round(Nc, 1), Nt_d=round(Nt, 1), H_d=round(H_y, 2),
                        T_barra_d=round(Nt / 4, 1), Rd_barra=round(Ft(16), 1), uso_barra=round(uso_bar, 3),
                        alma_Rd_escoamento=round(Rd_esc, 1), alma_Rd_enrugamento=round(Rd_enr, 1), uso_alma=round(uso_alma, 3),
                        sig_concreto_MPa=round(Nc / (0.25 * 0.25) / 1000, 2), uso_mesa=uso_mesa, mesa_tstub=det_m,
                        detalhe="CA-L2 chapa de apoio 250 × 250 × 19 sobre graute 20 mm + 4 barras roscadas M16 8.8 L=450 (hef 350 + grampo U Ø10) embutidas no pilar a 55 × 150, "
                              "atravessando a chapa e a mesa inferior da W (arruela + porca + contraporca por dentro da W); furo oblongo em x na mesa fora do C (deslizante); torque só no C"))
    # ---------------- montantes no meio dos vãos (DEC-052)
    WM_ = WM
    ECC_Y = 0.03                                             # eixo do montante 3 cm para dentro da faixa de 2º estágio (W no eixo da linha 2)
    mts = []
    for m_ in MEIOS:
        x = m_["x"]
        z_fundo_w = zt(x) - W.d / 1000
        z_base = 7.30 + T_GRAUTE                             # topo da capa +7,30 + graute de nivelamento 20 mm
        Lm = round(z_fundo_w - z_base - 0.010, 3)            # 5 mm de folga em cima e embaixo do perfil (a carga passa pelas cantoneiras)
        Nc = max(g1["R_rigido"][m_["nome"]], g1["R_mola"][m_["nome"]])
        Nt = max(0.0, -g2["R_rigido"][m_["nome"]], -g2["R_mola"][m_["nome"]])
        cmp_ = ML.compressao_resistente(WM_, Lm, Lm)        # rotulado nas 2 pontas (topo travado pela W e pelas terças, base pelas barras)
        NcRd = cmp_.NcRd if hasattr(cmp_, "NcRd") else cmp_.NRd
        NtRd = ML.tracao_resistente(WM_)
        MyRd = ML.momento_resistente_y(WM_)
        H_ = 0.02 * Nc                                       # força nocional no topo (NBR 8800:2024 4.9.7) — vai para a W e as terças
        uso_c = ML.interacao(Nc, 0.0, Nc * ECC_Y, NcRd, 1e9, MyRd)
        uso_t = ML.interacao(Nt, 0.0, Nt * ECC_Y, NtRd, 1e9, MyRd)
        # ligações: 2 L 102 × 102 × 12,7 em cima (L 130) e embaixo (L 100), cada uma com 2 M16 na mesa do montante
        V_par = max(Nc, Nt) / 4                              # 4 M16 em corte simples (2 por cantoneira)
        uso_par_mt = V_par / min(Fv(16), Fc(16, WM_.tf / 1000))
        # cantoneira de cima: aba sob a mesa da W, 2 M16 a 55 da face; T-stub com a aba (A36)
        Fa_top, det_at = tstub(2, 0.065, 0.0127, 250e3, 0.055 - 0.0127 - 0.8 * 0.011, 0.102 - 0.055, Ft(16))
        Fa_bot, det_ab = tstub(2, 0.050, 0.0127, 250e3, 0.076 - 0.0127 - 0.8 * 0.011, 0.102 - 0.076, Ft(16))
        uso_ant = max(Nt / 2 / Fa_top, Nt / 2 / Fa_bot)
        uso_mesa, det_m = mesa_w_tstub(Nt / 2)
        Rd_esc, Rd_enr, uso_alma = alma(Nc, 0.148)           # alma da W sobre o montante (lb = altura do W 150)
        # espera EM-L2: 4 BR-M16 com gancho laçado na alça N9 (Ø10, 2 ramos) da VM; graute + 2º estágio C30
        prying = 1.3
        T_bar = Nt / 4 * prying
        uso_bar = T_bar / Ft(16)
        Rd_alca = 2 * math.pi * 0.010 ** 2 / 4 * 500e3 / 1.15
        uso_alca = 2 * T_bar / Rd_alca                       # as 2 barras de cada cantoneira (mesmo x) laçam a mesma alça
        sig_gr = Nc / (2 * 0.100 * 0.102) / 1000              # MPa sob as 2 abas
        uso_gr = sig_gr / (0.85 * 30 / 1.4)
        mts.append(dict(m_, perfil=PERFIL_M, L_m=Lm, z_base=round(z_base, 3), z_fundo_w=round(z_fundo_w, 3), Nc_d=round(Nc, 1), Nt_d=round(Nt, 1), H_d=round(H_, 2),
                        NcRd=round(NcRd, 1), NtRd=round(NtRd, 1), lambda_y=round(Lm / (WM_.ry / 100), 1), uso_compressao=round(uso_c, 3), uso_tracao=round(uso_t, 3),
                        uso_parafusos=round(uso_par_mt, 3), uso_cantoneiras=round(uso_ant, 3), cant_topo=det_at, cant_base=det_ab,
                        uso_mesa_w=uso_mesa, mesa_tstub=det_m, uso_alma_w=round(uso_alma, 3),
                        espera=dict(T_barra_d=round(T_bar, 1), uso_barra=round(uso_bar, 3), Rd_alca=round(Rd_alca, 1), uso_alca=round(uso_alca, 3),
                                    sig_graute_MPa=round(sig_gr, 2), uso_graute=round(uso_gr, 3)),
                        uso=round(max(uso_c, uso_t, uso_par_mt, uso_ant, uso_mesa, uso_alma, uso_bar, uso_alca, uso_gr), 3)))
    # ---------------- reações características no meio do vão para a VM (calc_vm_retangular: caso +7,30 linha 2)
    Rg = env["ELS G"]["R_rigido"]; Rq = env["ELS Q"]["R_rigido"]
    carga_vm = {}
    for m_ in mts:
        c_ = carga_vm.setdefault(m_["vm"], dict(Pg=0.0, Pq=0.0, Pup_d=0.0, L=m_["L_vm"]))
        c_["Pg"] = round(max(c_["Pg"], Rg[m_["nome"]]), 1); c_["Pq"] = round(max(c_["Pq"], Rq[m_["nome"]]), 1)
        c_["Pup_d"] = round(max(c_["Pup_d"], m_["Nt_d"]), 1); c_["L"] = max(c_["L"], m_["L_vm"])
    # ---------------- emendas: no ponto de momento nulo mais distante que ainda deixa módulo ≤ 12 m
    a_, b_ = res[("ELU1 gravidade (1,4 G + 1,5 Q)", False)], res[("ELU1 gravidade (1,4 G + 1,5 Q)", True)]
    xs = a_["xs"]; Mg = a_["M"]
    zeros = [float(xs[i]) for i in range(len(xs) - 1) if Mg[i] * Mg[i + 1] < 0]
    em, x0 = [], XA
    while XB - x0 > 11.9:
        cand = [z for z in zeros if x0 + 3.0 < z <= x0 + 11.9]
        em.append(round(max(cand), 2)); x0 = em[-1]
    mods = [round(b - a, 2) for a, b in zip([XA] + em, em + [XB])]
    emendas = []
    for xe in em:
        i = int(np.argmin(abs(xs - xe)))
        Me = max(abs(res[(k, mol)]["M"][i]) for k in ("ELU1 gravidade (1,4 G + 1,5 Q)", "ELU2 sucção (1,0 G + 1,4 W)") for mol in (False, True))
        Ve = max(abs(res[(k, mol)]["V"][i]) for k in ("ELU1 gravidade (1,4 G + 1,5 Q)", "ELU2 sucção (1,0 G + 1,4 W)") for mol in (False, True))
        Me_proj = max(Me, 0.25 * MRd_ter)                    # emenda dimensionada para no mínimo 25 % do MRd (o ponto de M nulo varia)
        Fm = Me_proj / (W.d / 1000 - W.tf / 1000)
        uso_tl1 = Fm / (4 * Fv(16))                          # 4 M16 de cada lado da junta em cada mesa
        uso_tl2 = Ve / (2 * 2 * Fv(16))                      # 2 M16 de cada lado, corte duplo (tala dos 2 lados da alma)
        uso_alma_e = Ve / 2 / Fc(16, W.tw / 1000)
        emendas.append(dict(x=xe, M_d=round(Me, 1), M_proj=round(Me_proj, 1), V_d=round(Ve, 1), uso_TL1=round(uso_tl1, 3), uso_TL2=round(uso_tl2, 3), uso_contato_alma=round(uso_alma_e, 3)))
    Fmesa = M_inf_comp / (W.d / 1000 - W.tf / 1000)
    F_mf = 0.02 * Fmesa
    import lig_cob                                       # rev11: geometria única da MF-1 (do furo da ponta do transpasse à mesa inferior)
    L_mf = lig_cob.L_MF()
    Ncr_mf = 200e6 * 2.9e-8 * math.pi ** 2 / L_mf ** 2
    kg_w = W.peso / 9.81e-3 * (XB - XA)
    kg_mt = sum(WM_.peso / 9.81e-3 * m_["L_m"] for m_ in mts)
    out = dict(
        perfil=PERFIL, aco="ASTM A572 Gr. 50 (fy 345 MPa)", montante=PERFIL_M, trib_m=round(TRIB, 3), decisao="DEC-052",
        cargas_kN_m=dict(g_k=round(g_k, 2), g_fav=round(g_fav, 2), q_k=round(q_k, 2), w_suc_corpo=round(w_suc(X_EIXO["C"]), 2), w_suc_local=round(w_suc(1.0), 2), qv=round(QV, 3)),
        apoios=[dict(nome=nm, x=round(xa, 3), z_apoio=z_ap, onde=o) for nm, xa, z_ap, o in APOIOS], vao_max_m=round(Lmax, 3), trechos_m=[round(t, 3) for t in L_trechos],
        esforcos={k: dict(Mmax=round(v["Mmax"], 1), Mmin=round(v["Mmin"], 1), Vmax=round(v["Vmax"], 1), d_mm=round(v["d_mm"], 1),
                          R_rigido={a: round(b, 1) for a, b in v["R_rigido"].items()}, R_mola={a: round(b, 1) for a, b in v["R_mola"].items()}) for k, v in env.items()},
        verificacoes=dict(MRd_Lb_terca=round(MRd_ter, 1), MRd_Lb_trecho=round(MRd_sem_mf, 1), M_mesa_sup=round(M_sup_comp, 1), M_mesa_inf=round(M_inf_comp, 1),
                          uso_sem_mao_francesa=round(uso_sem_mf, 3), precisa_mao_francesa=precisa_mf, Msd=round(max(M_sup_comp, M_inf_comp), 1), MRd=round(min(MRd_ter, MRd_inf), 1),
                          uso_M=round(uso_M, 3), VRd=round(VRd, 1), Vsd=round(Vsd, 1), uso_V=round(Vsd / VRd, 3), Lb_m=S_TER, Lb_trecho_m=round(Lmax, 3),
                          norma="NBR 8800:2024 5.4.2 / Anexo D e 5.4.3"),
        flecha=flecha, apoios_diretos=pil, montantes=mts, carga_vm=carga_vm, emendas_x=em, modulos_m=mods, emendas=emendas,
        mao_francesa=(dict(perfil="L 51 × 51 × 4,8 (2\" × 3/16\")", em="todas as terças da linha 2 (dos dois lados da W)", F_d=round(F_mf, 1), L_m=round(L_mf, 3),
                           Ncr_kN=round(Ncr_mf, 1), parafusos="1 M12 8.8 em cada ponta (em cima, no parafuso da ponta do transpasse; embaixo, na mesa inferior da W)", norma="NBR 8800:2024 4.11 (travamento: 2 % da força na mesa)") if precisa_mf else None),
        terca_sobre_W="ST-W: chapa dobrada 6,3 × 220 (como o ST-1P) parafusada na mesa superior da W com 2 M12 (gabarito 55) e nas 2 almas do transpasse com 4 M12 (furos de apoio da terça a ±60)",
        espera="EM-L2 (por montante): 4 barras roscadas M16 8.8 L 330 com gancho de 180° laçado na alça N9 da VM (2 ramos Ø10; as 2 barras de cada lado na mesma alça, "
               "eixo do montante sobre uma alça e barras a ±150), postas por quem faz a capa com gabarito de chapa 6,3 (furos a 300 × 60), na faixa de 2º estágio (18 cm) "
               "do +7,30 da linha 2, a 0 e 60 mm do eixo da linha 2 (para o lado da borda); saem 60 mm acima da capa",
        aco_kg=dict(viga=round(kg_w), montantes=round(kg_mt)),
        ok=uso_M <= 1 and Vsd <= VRd and flecha["GQ_mm"] <= flecha["lim_L250_mm"] and max(mods) <= 12.0
           and all(p_["uso_barra"] <= 1 and p_["uso_alma"] <= 1 and p_["uso_mesa"] <= 1 for p_ in pil) and all(m_["uso"] <= 1 for m_ in mts)
           and all(e_["uso_TL1"] <= 1 and e_["uso_TL2"] <= 1 for e_ in emendas),
    )
    (AQ / "cob_linha2.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    return out


if __name__ == "__main__":
    o = main()
    print(json.dumps({k: o[k] for k in ("cargas_kN_m", "verificacoes", "flecha", "modulos_m", "emendas", "carga_vm", "aco_kg", "ok")}, ensure_ascii=False, indent=1))
    for m_ in o["apoios_diretos"]:
        print({k: m_[k] for k in ("nome", "z_concreto", "sobe_m", "Nc_d", "Nt_d", "uso_barra", "uso_alma", "uso_mesa")})
    for m_ in o["montantes"]:
        print({k: m_[k] for k in ("nome", "x", "L_m", "Nc_d", "Nt_d", "uso_compressao", "uso_tracao", "uso_parafusos", "uso_cantoneiras", "uso_mesa_w", "uso_alma_w", "uso")}, m_["espera"])
