"""Letsara rev06d — ombreira metálica OM-1 da porta da vista I (fachada da linha 1, vão C–D). Gera ombreira.json.

Decisão do Nathan (17/10/2026, DEC-028): ombreira metálica só no vão da porta, em perfil U que abraça a ponta da placa para não
perder vão livre; as demais placas ficam como estão (cada placa autoportante nos seus consoles).
Solução adotada: U rotulado na base e no topo. A base engastada (opção B do estudo) não passa: com o baldrame estreito os
chumbadores ficam a ±80 do eixo da parede e cada um puxaria 32 kN (uso 2,1 no cone), além de 10 kN·m de torção no baldrame.
  OM-1 = U dobrado 125 × 80 × 6,3 (A36) no plano da parede, alma voltada para a porta, abas por fora das 2 faces da placa
         I-13 / I-14 com calço de neoprene de 6 mm; do topo da chapa de base até 10 mm sob a placa de +2,50;
  base   chapa 12,5 × 200 × 180 soldada na oficina (filete 5 em todo o contorno) e 2 chumbadores químicos M16 5.8 hef 100 no
         baldrame (rótula: só cortante);
  topo   chapa de ligação CL-1 12,5 × 100 × 360 (A36) sobre a aba interna do U e a face interna da placa de +2,50 (I-15):
         1 M16 8.8 passante na aba do U e 1 M16 8.8 em bucha BR-1 M16 hef 70 na I-15 (oblongo vertical 18 × 40), calço 12;
         a placa I-15 leva as 2 buchas e 12 cordoalhas (6 por face) em vez de 8 por receber o topo das 2 ombreiras;
  ligação com a placa: 2 parafusos M16 8.8 passantes (furo Ø18 deixado na fábrica na ponta da placa, entre as cordoalhas) só
         para posicionar; o vento passa da placa para o U por contato das abas (neoprene).
A ponta da placa do lado da porta fica 20 mm antes do vão (junta de 13,7 mm até a alma do U); o vão livre de 1,80 é mantido.
Ações: vento NBR 6123 com o mesmo p_k das placas (q0 0,874 kN/m², coeficiente líquido 1,6, calc_placas); folha da porta 180 × 250
com metade da largura em cada ombreira; batente da esquadria vizinha na aba do U (faixa de 0,30 m de +1,25 a +2,50, a favor da
segurança); reação da ponta da placa pelo MEF de casca (OpenSeesPy ShellMITC4) com a borda do lado da porta apoiada no U.
Unidades: kN, m; mm e MPa nas seções.
"""
import json
import math
from pathlib import Path

import numpy as np
import openseespy.opensees as ops

from nd_estruturas.ancoragem import GrupoPinos

AQ = Path(__file__).parent
PL = json.loads((AQ / "placas.json").read_text(encoding="utf-8"))
p_k = PL["vento"]["p_k"]                               # kN/m² (cp líquido 1,6 — o mesmo das placas)
GF, GA1 = 1.4, 1.10
FY, FU, ES = 250.0, 400.0, 200000.0                    # A36
H_PL, E_PL = 1.250, 0.100
PORTA = (23.790, 25.590, 2.500)                        # vista I: vão livre da porta (m) e altura
S_VAO = (19.760, 29.620)
JUNTA_U = 0.020                                        # ponta da placa a 20 mm do vão
U = dict(h=125.0, b=80.0, t=6.3, neo=6.0)            # mm: altura (na espessura da parede), abas, chapa, calço de neoprene
BASE = dict(t=12.5, by=200.0, bx=180.0, ex=(60.0, 130.0))             # 2 chumbadores no eixo da parede, a 60 e 130 da alma
T_BASE, FOLGA = 0.0125, 0.010
L_U = PORTA[2] - T_BASE - FOLGA                        # 2,474 m
Z_PAR = (0.310, 0.940)                                 # parafusos passantes (entre as linhas de cordoalha 156/469 e 781/1094)
B_ESQ = 0.30                                           # faixa da esquadria vizinha que encosta no U (+1,25 a +2,50)
R = dict(peca="OM-1 U dobrado 125 × 80 × 6,3 A36, L = %.0f + chapa de base 12,5 × 200 × 180 + 2 chumbadores químicos M16 + chapa de ligação CL-1 12,5 × 100 × 360" % (L_U * 1000),
         p_k_kNm2=p_k, n=2, solucao="U rotulado na base (baldrame) e no topo (placa I-15 sobre a porta, com 12 cordoalhas)",
         base_engastada_descartada=dict(Md_kNm=10.38, T_chumbador_kN=32.5, uso_cone=2.12, torcao_baldrame_kNm=10.4))

# ---------------------------------------------------------------- 1. placa ao lado da porta (I-13 / I-14), casca, borda da porta no U
L_pl = PORTA[0] - JUNTA_U - S_VAO[0]


def placa_porta(com_U, nx=78, nz=25):
    Ec = PL["secao"]["Ec_MPa"] * 1e3
    ops.wipe(); ops.model("basic", "-ndm", 3, "-ndf", 6)
    ops.nDMaterial("ElasticIsotropic", 1, Ec, 0.2); ops.section("PlateFiber", 1, 1, E_PL)
    xs, zs = np.linspace(0, L_pl, nx + 1), np.linspace(0, H_PL, nz + 1)
    tag = lambda i, j: 1 + i + j * (nx + 1)
    for j, z in enumerate(zs):
        for i, x in enumerate(xs):
            ops.node(tag(i, j), x, 0, z)
    e = 1
    for j in range(nz):
        for i in range(nx):
            ops.element("ShellMITC4", e, tag(i, j), tag(i + 1, j), tag(i + 1, j + 1), tag(i, j + 1), 1); e += 1
    near = lambda x, z: tag(int(round(x / L_pl * nx)), int(round(z / H_PL * nz)))
    xpt = 0.21 * L_pl + 0.150
    ap = [near(0.060, 0.940), near(xpt, 0.0), near(L_pl - xpt, 0.0)]
    ops.fix(ap[0], 1, 1, 1, 0, 0, 0); ops.fix(ap[1], 0, 1, 0, 0, 0, 0); ops.fix(ap[2], 0, 1, 0, 0, 0, 0)
    borda = [tag(nx, j) for j in range(nz + 1)]
    if com_U:
        for n_ in borda:
            ops.fix(n_, 0, 1, 0, 0, 0, 0)
    ops.timeSeries("Linear", 1); ops.pattern("Plain", 1, 1)
    a = (L_pl / nx) * (H_PL / nz)
    for j in range(nz + 1):
        for i in range(nx + 1):
            ops.load(tag(i, j), 0, p_k * a * (0.5 if i in (0, nx) else 1) * (0.5 if j in (0, nz) else 1), 0, 0, 0, 0)
    ops.system("UmfPack"); ops.numberer("RCM"); ops.constraints("Plain"); ops.integrator("LoadControl", 1.0)
    ops.algorithm("Linear"); ops.analysis("Static"); ops.analyze(1); ops.reactions()
    U_ = np.array([[ops.nodeDisp(tag(i, j), 2) for i in range(nx + 1)] for j in range(nz + 1)])
    hx, hz, D = L_pl / nx, H_PL / nz, Ec * E_PL ** 3 / (12 * (1 - 0.04))
    kx = (U_[1:-1, 2:] - 2 * U_[1:-1, 1:-1] + U_[1:-1, :-2]) / hx ** 2
    kz = (U_[2:, 1:-1] - 2 * U_[1:-1, 1:-1] + U_[:-2, 1:-1]) / hz ** 2
    m = max(np.abs(D * (kx + 0.2 * kz)).max(), np.abs(D * (kz + 0.2 * kx)).max())
    r_ap = [-ops.nodeReaction(n_, 2) for n_ in ap]
    r_b = [-ops.nodeReaction(n_, 2) for n_ in borda] if com_U else []
    ops.wipe()
    return dict(flecha_mm=round(float(np.abs(U_).max()) * 1000, 1), sigma_k_MPa=round(m * 6 / E_PL ** 2 / 1e3, 2),
                reacoes_pontuais_kN=[round(r, 2) for r in r_ap], reacao_borda_U_kN=round(sum(r_b), 2),
                soma_kN=round(sum(r_ap) + sum(r_b), 2), carga_kN=round(p_k * L_pl * H_PL, 2)), (zs, np.array(r_b))


A_, _ = placa_porta(False)
B_, (zb, rb) = placa_porta(True)
assert abs(A_["soma_kN"] - A_["carga_kN"]) < 0.05 and abs(B_["soma_kN"] - B_["carga_kN"]) < 0.05   # equilíbrio do MEF
R["placa_porta"] = dict(L_m=round(L_pl, 3), sem_U=A_, com_U=B_, sig_cp_inf_MPa=PL["protensao"]["sig_cp_inf_MPa"])

# ---------------------------------------------------------------- 2. U biapoiado (base e topo)
q_porta = p_k * (PORTA[1] - PORTA[0]) / 2
zs = np.linspace(0, L_U, 1001)
z_rb = zb - T_BASE
cargas = [(z_, r_) for z_, r_ in zip(z_rb, rb)]                       # ponta da placa (nós da borda)
z_e0 = 1.25 - T_BASE
n_e = 50
for k in range(n_e):                                                  # batente da esquadria vizinha (+1,25 a +2,50)
    z_ = z_e0 + (k + 0.5) * (L_U - z_e0) / n_e
    cargas.append((z_, p_k * B_ESQ * (L_U - z_e0) / n_e))
R_top = q_porta * L_U / 2 + sum(r_ * z_ / L_U for z_, r_ in cargas)
R_bas = q_porta * L_U + sum(r_ for _, r_ in cargas) - R_top
M = np.array([R_bas * z - q_porta * z ** 2 / 2 - sum(r_ * (z - z_) for z_, r_ in cargas if z > z_) for z in zs])
Mk = float(M.max())
h, b, t = U["h"], U["b"], U["t"]
I = t * h ** 3 / 12 + 2 * (b - t) * t ** 3 / 12 + 2 * (b - t) * t * (h / 2 - t / 2) ** 2
W = I / (h / 2)
Zp = t * h ** 2 / 4 + 2 * (b - t) * t * (h - t)
lam_aba, lam_p_aba = b / t, 0.56 * math.sqrt(ES / FY)                  # NBR 8800:2008 tabela F.1 (FLM, mesa livre)
MRd = min(Zp, 1.5 * W) * FY / GA1 / 1e6                                # NBR 8800:2008 anexo G (seção compacta)
VRd = 0.6 * (h - 2 * t) * t * FY / GA1 / 1e3                           # NBR 8800:2008 5.4.3.1
Vk = max(R_bas, R_top)
EI = ES * I * 1e-9
kap = M / EI
th = np.concatenate([[0], np.cumsum((kap[1:] + kap[:-1]) / 2 * np.diff(zs))])
v = np.concatenate([[0], np.cumsum((th[1:] + th[:-1]) / 2 * np.diff(zs))])
v = v - zs / L_U * v[-1]
fl = float(np.abs(v).max()) * 1000
R["U"] = dict(L_mm=round(L_U * 1000), q_porta_kNm=round(q_porta, 3), R_placa_kN=round(float(rb.sum()), 2), R_base_k_kN=round(R_bas, 2), R_topo_k_kN=round(R_top, 2),
              Mk_kNm=round(Mk, 2), Md_kNm=round(GF * Mk, 2), MRd_kNm=round(MRd, 2), uso_flexao=round(GF * Mk / MRd, 3),
              b_t_aba=round(lam_aba, 1), lim_b_t=round(lam_p_aba, 1), Vd_kN=round(GF * Vk, 2), VRd_kN=round(VRd, 1),
              flecha_k_mm=round(fl, 1), lim_mm=round(L_U * 1000 / 300, 1), I_mm4=round(I), kg_m=round((h + 2 * (b - t)) * t * 7.85e-3, 2))
assert lam_aba <= lam_p_aba and GF * Mk <= MRd and GF * Vk <= VRd and fl <= L_U * 1000 / 300

# ---------------------------------------------------------------- 3. ligações
Fb, Ft = GF * R_bas, GF * R_top
Fv_ch = 0.6 * 157 * 500 / 1.25 / 1e3                                   # chumbador M16 5.8, aço ao cortante (EN 1992-4, γMs 1,25)
V_cone_borda = 0.0                                                     # (cortante pequeno; arrancamento de borda conferido no catálogo)
bucha = GrupoPinos(d=16.0, d_cabeca=30.0, hef=70.0, nx=1, ny=1, sx=0, sy=0, cx_neg=150.0, cx_pos=1000.0, cy_neg=60.0, cy_pos=1000.0, ha=100.0, fc=25.0).tracao()
Ft_m16 = 0.75 * 157 * 800 / 1.35 / 1e3                                 # NBR 8800:2008 6.3.3.1
W_cl = 100 * 12.5 ** 2 / 6
M_cl = Ft * 75.0                                                        # kN·mm: braço de meia distância entre os parafusos (150/2)
uso_cl = M_cl * 1e3 / W_cl / (FY / GA1)
R["ligacoes"] = dict(base=dict(Vd_kN=round(Fb, 2), chumbadores="2 M16 5.8 químicos hef 100", Fv_Rd_2_kN=round(2 * Fv_ch, 1), uso=round(Fb / (2 * Fv_ch), 3)),
                     topo=dict(Fd_kN=round(Ft, 2), bucha_BR1_phiN_kN=round(bucha["phiNn_kN"], 1), M16_Ft_Rd_kN=round(Ft_m16, 1), chapa_CL1_uso=round(uso_cl, 3),
                               uso=round(max(Ft / bucha["phiNn_kN"], Ft / Ft_m16, uso_cl), 3)),
                     placa=dict(obs="vento da placa passa ao U por contato das abas (neoprene 6); 2 M16 passantes só posicionam", R_k_kN=round(float(rb.sum()), 2)))
assert R["ligacoes"]["base"]["uso"] <= 1 and R["ligacoes"]["topo"]["uso"] <= 1

# ---------------------------------------------------------------- 4. placa I-15 (+2,50, sobre a porta) com o topo das 2 OM-1
L_sup = S_VAO[1] - S_VAO[0] - 2 * 0.060
x_om = [PORTA[0] - S_VAO[0] - 0.060, PORTA[1] - S_VAO[0] - 0.060]
xs = np.linspace(0, L_sup, 2001)
w_pl = p_k * H_PL


def M_sup(P):
    Ra = w_pl * L_sup / 2 + sum(P_ * (L_sup - a_) / L_sup for a_, P_ in P)
    return float(max(Ra * x - w_pl * x ** 2 / 2 - sum(P_ * (x - a_) for a_, P_ in P if x > a_) for x in xs))


M_so, M_com = M_sup([]), M_sup([(x_om[0], R_top), (x_om[1], R_top)])
fpd, Ap1, d_c, fcd = 1710 / 1.15, 98.7e-6, 0.020 + 0.0127 / 2, 40 / 1.4


def MRd_n(n_face):                                                     # mesma formulação do calc_placas (bloco retangular)
    Ap = n_face * Ap1
    x = Ap * fpd * 1e3 / (0.85 * fcd * 1e3 * 0.8 * H_PL)
    return Ap * fpd * 1e3 * (E_PL - d_c - 0.4 * x)


assert abs(MRd_n(4) - PL["vento"]["MRd"]) < 0.05                      # confere com placas.json
R["placa_I15"] = dict(vao_m=round(L_sup, 3), Mk_sem_OM_kNm=round(M_so, 2), Mk_com_OM_kNm=round(M_com, 2), Md_kNm=round(GF * M_com, 2),
                      MRd_8cord_kNm=round(MRd_n(4), 2), uso_8cord=round(GF * M_com / MRd_n(4), 3), MRd_10cord_kNm=round(MRd_n(5), 2),
                      uso_10cord=round(GF * M_com / MRd_n(5), 3), MRd_12cord_kNm=round(MRd_n(6), 2), uso_12cord=round(GF * M_com / MRd_n(6), 3),
                      sig_cp_inf_12cord_MPa=round(PL["protensao"]["sig_cp_inf_MPa"] * 12 / 8, 2),
                      sig_c0_12cord_MPa=round(-12 * PL["protensao"]["F_macaco_kN"] * 0.93 / (H_PL * E_PL) / 1e3, 2), lim_transf_MPa=round(-0.7 * 25, 1),
                      cordoalhas="12 Ø12,7 (6 por face, z = 95, 156, 469, 781, 1094, 1155 mm — simétricas, fora do nicho NC-1 de 840 a 1040) + 2 buchas BR-1 M16 hef 70 na face interna, a 150 da base, nas posições das OM-1")
assert GF * M_com <= MRd_n(6)
R["kg_un"] = round(R["U"]["kg_m"] * L_U + BASE["t"] * BASE["by"] * BASE["bx"] * 7.85e-6 + 12.5 * 100 * 360 * 7.85e-6, 2)
R["GEO"] = dict(U=U, BASE=BASE, CL1=dict(t=12.5, b=100.0, L=360.0, z0=2.34, z_par_U=2.40, z_bucha=2.65), L_U_mm=round(L_U * 1000, 1), T_BASE_mm=T_BASE * 1000,
                FOLGA_mm=FOLGA * 1000, JUNTA_U_mm=JUNTA_U * 1000, Z_PAR_mm=[z * 1000 for z in Z_PAR], PORTA=PORTA)
(AQ / "ombreira.json").write_text(json.dumps(R, indent=1, ensure_ascii=False), encoding="utf-8")
if __name__ == "__main__":
    print(json.dumps({k: v for k, v in R.items() if k != "GEO"}, indent=1, ensure_ascii=False))
