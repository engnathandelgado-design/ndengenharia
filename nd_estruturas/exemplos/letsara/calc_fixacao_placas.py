"""Letsara rev06 — fixação das placas 125 × 10 pelo sistema Trejor (console soldado), DEC-026.

Cada placa leva só o próprio peso e o vento (junta horizontal macho-fêmea com 5 mm de folga na altura: não há
empilhamento). Peças por placa:
  NC-1  nicho de chapa embutido na face interna, encostado em cada ponta, no terço superior (centro a 94 cm da base);
  CS-1  console soldado na obra na CE-1 do pilar; o parafuso de nível M16 apoia no teto do nicho (peso e nível),
        o prisioneiro frontal M16 apoia no fundo do nicho (sobrepressão e afastamento 25 mm) e os 2 dentes do console
        ficam atrás das 2 abas do nicho (sucção);
  CE-1  chapa de espera 380 × 330 × 16 com 4 pinos Ø16 + 2 grampos Ø10 na face externa do pilar, uma por fiada (2 consoles);
  PT-1  pino de travamento (cartola Trejor), 2 por junta horizontal, ao lado das alças de içamento AL-P (0,21 L + 15 cm):
        M16 nas luvas TSA das duas placas, furo oblongo vertical — só força fora do plano.

Cálculo:
  1. MEF de casca (OpenSeesPy ShellMITC4) do pano de 8 placas sobrepostas: reações nos consoles e nos pinos com vento
     ± e peso; momento na placa comparado com o MRd da placa protendida (placas.json);
  2. ponta da placa como dente Gerber (bielas e tirantes — NBR 9062:2017 7.3/7.4 + PCI 5.6), nariz acima do nicho;
  3. console CS-1 em MEF de casca (chapas) + NBR 8800:2008: von Mises nas chapas, solda de filete (6.2.5),
     parafusos de ajuste, CE-1 e pinos com cabeça no pilar (ACI 318-19 cap. 17, como em ancoragem.py);
  4. pino de travamento PT-1: parafuso M16 e luva TSA na placa de 10 cm.
Unidades: kN, m (MEF da parede); N, mm, MPa (console). Medidas de pré-dimensionamento: confirmar com o catálogo
09 da Trejor (consoles metálicos para painéis de fachada).
"""
import json
import math
import os
from pathlib import Path

import numpy as np
import openseespy.opensees as ops

from nd_estruturas.dente_consolo import Dente
from nd_estruturas.ancoragem import GrupoPinos, interacao, grampo_ancoragem_kN
from nd_estruturas.ligacoes_aco import Ft_Rd as Ft_Rd_cm, Fv_Rd as Fv_Rd_cm

AQ = Path(__file__).parent
PL = json.loads((AQ / "placas.json").read_text(encoding="utf-8"))
R = {}

# ------------------------------------------------------------------ dados
H, E_PL, L = 1.25, 0.100, PL["secao"]["L_max_m"]        # placa (m)
Ec = PL["secao"]["Ec_MPa"] * 1e3                         # kPa
PP = PL["secao"]["pp_kNm"] / H                           # kN/m² (peso por área)
p_k = PL["vento"]["p_k"]                                 # kN/m² (Cpe borda −1,4 + Cpi 0,2, todas as placas)
MRd_placa = PL["vento"]["MRd"]                           # kN·m por placa (1,25 m), cordoalhas de uma face
X_CS = 0.060                                             # centro do console a partir da ponta da placa
X_PT = round(0.21 * L + 0.15, 3)
Z_PT2 = 0.150                                            # trava de pé PT-2 acima da base da 1ª placa do pacote suspenso                         # pinos PT-1: 15 cm para dentro de cada alça AL-P (0,21 L)
Z_CS = 0.940                                             # centro do nicho a partir da base da placa
N_FIADAS = 8
GF, GQ = 1.4, 1.4                                        # NBR 8681 (peso: elemento pré-fabricado; vento)
BETA_MONT = 1.3 * 1.3                                    # NBR 9062:2017 5.3.2.1: γf 1,3 × βa 1,3 (montagem)
GN = 1.0                                                 # NBR 9062:2017 7.3.1.1: γn = 1,0 (pré-fabricado, permanente preponderante)


# ------------------------------------------------------------------ 1. MEF de casca do pano
def mef_parede(sinal_vento=+1, com_peso=True, n_fiadas=N_FIADAS, pe="baldrame"):
    """sinal +1: sobrepressão (empurra a placa contra o pilar, −y); −1: sucção (+y). Retorna reações e esforços."""
    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)
    ops.section("ElasticMembranePlateSection", 1, Ec, 0.2, E_PL, 0.0)
    xs = sorted({0.0, X_CS, X_PT, L / 2, L - X_PT, L - X_CS, L} | {round(L * i / 40, 4) for i in range(41)})
    zs = [0.0, Z_PT2, 0.3125, 0.625, Z_CS, H]
    nid, ele = 0, 0
    tags, eles, con, pinos_bot, pinos_top = [], [], [], [], []
    trava = []
    for k in range(n_fiadas):
        z0 = k * H
        T = {}
        for j, z in enumerate(zs):
            for i, x in enumerate(xs):
                nid += 1
                ops.node(nid, x, 0.0, z0 + z)
                T[i, j] = nid
        for j in range(len(zs) - 1):
            for i in range(len(xs) - 1):
                ele += 1
                ops.element("ShellMITC4", ele, T[i, j], T[i + 1, j], T[i + 1, j + 1], T[i, j + 1], 1)
                eles.append((ele, k, xs[i], xs[i + 1], zs[j], zs[j + 1]))
        ic = [xs.index(X_CS), xs.index(L - X_CS)]
        jc = zs.index(Z_CS)
        for n_, i in enumerate(ic):                                  # consoles: y e z; x só no da esquerda
            ops.fix(T[i, jc], 1 if n_ == 0 else 0, 1, 1, 0, 0, 0)
            con.append((k, n_, T[i, jc]))
        ip = [xs.index(X_PT), xs.index(L - X_PT)]
        pinos_bot.append([T[i, 0] for i in ip]); pinos_top.append([T[i, len(zs) - 1] for i in ip])
        if k == 0 and pe == "trava":                                 # PT-2: trava de pé no pilar, só y, nas 2 pontas
            for i in ic:
                trava.append(T[i, zs.index(Z_PT2)])
        tags.append(T)
    # pinos de travamento: elemento de mola rígida só em y entre topo da placa k e base da k+1 (folga de 5 mm na altura)
    ops.uniaxialMaterial("Elastic", 9, 1e7)
    pin_e = []
    for k in range(n_fiadas - 1):
        for a, b in zip(pinos_top[k], pinos_bot[k + 1]):
            ele += 1
            ops.element("zeroLength", ele, a, b, "-mat", 9, "-dir", 2)  # só y: oblongo vertical, folga de 5 mm na altura
            pin_e.append(ele)
    for b_ in (pinos_bot[0] if pe == "baldrame" else trava):
        ops.fix(b_, 0, 1, 0, 0, 0, 0)                                # 1ª placa: pinos no baldrame ou travas PT-2 no pilar
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    for (e, k, x0, x1, z0, z1) in eles:                              # carga por área → 4 nós
        A = (x1 - x0) * (z1 - z0)
        nos = ops.eleNodes(e)
        for n_ in nos:
            fy = -sinal_vento * GQ * p_k * A / 4
            fz = -GF * PP * A / 4 if com_peso else 0.0
            ops.load(n_, 0.0, fy, fz, 0.0, 0.0, 0.0)
    ops.system("UmfPack"); ops.numberer("RCM"); ops.constraints("Transformation")
    ops.integrator("LoadControl", 1.0); ops.test("NormDispIncr", 1e-12, 10); ops.algorithm("Newton"); ops.analysis("Static")  # Newton: o estado dos elementos de casca só é atualizado com o resíduo (com "Linear" as tensões saem zeradas)
    assert ops.analyze(1) == 0
    ops.reactions()
    reac = [dict(fiada=k + 1, lado=n_, Ry=ops.nodeReaction(t, 2), Rz=ops.nodeReaction(t, 3)) for (k, n_, t) in con]
    pinos = [abs(ops.eleResponse(e, "force")[1]) for e in pin_e] + [abs(ops.nodeReaction(b_, 2)) for b_ in (pinos_bot[0] if pe == "baldrame" else [])]
    f_trava = [abs(ops.nodeReaction(b_, 2)) for b_ in trava]
    # momentos na direção do vão (Mxx local = X global) por metro, média das 4 integrações de cada elemento
    Mx = []
    for (e, k, x0, x1, z0, z1) in eles:
        s = np.array(ops.eleResponse(e, "stresses")).reshape(4, 8)
        Mx.append((abs(s[:, 3].mean()), k + 1, (x0 + x1) / 2, z0))
    Mmax = max(Mx)
    # momento resultante na placa = integral de Mxx na altura (seção do meio do vão de cada placa)
    Mplaca = 0.0                                                     # integral com sinal de Mxx na altura, em cada seção do vão
    xcols = sorted({x1 for (_, _, _, x1, _, _) in eles})
    for k in range(n_fiadas):
        for xc in xcols[:-1]:
            m = 0.0
            for (e, kk, x0, x1, z0, z1) in eles:
                if kk == k and abs(x1 - xc) < 1e-9:
                    s_ = np.array(ops.eleResponse(e, "stresses")).reshape(4, 8)
                    m += s_[:, 3].mean() * (z1 - z0)
            Mplaca = max(Mplaca, abs(m))
    uy = max(abs(ops.nodeDisp(n_, 2)) for T in tags for n_ in T.values())
    return dict(reac=reac, pinos=pinos or [0.0], trava=f_trava, Mxx_max=Mmax, M_placa=Mplaca, uy_max_mm=uy * 1000 / GQ)


res_m = {s: mef_parede(s) for s in (+1, -1)}
# pacotes suspensos (sem continuidade até o baldrame): com 2 placas e pinos PT-1 entre elas a de baixo passa de MRd (40,1 > 37,6 kN·m,
# verificado em 17/10/2026); adota-se trava de pé PT-2 em CADA placa desses pacotes, sem PT-1 — cada placa trabalha sozinha
pac = {"placa com trava de pé PT-2 (pacote suspenso)": {sg: mef_parede(sg, True, 1, "trava") for sg in (+1, -1)}}
F_pt2_d = max(max(v["trava"]) for c in pac.values() for v in c.values())
for c in pac.values():
    for v in c.values():
        assert v["M_placa"] <= MRd_placa
Ry_d = max([abs(r["Ry"]) for s in res_m.values() for r in s["reac"]] + [abs(r["Ry"]) for c in pac.values() for v in c.values() for r in v["reac"]])
Rz_d = max(abs(r["Rz"]) for s in res_m.values() for r in s["reac"])
F_pino_d = max(max(s["pinos"]) for s in res_m.values())
M_placa_d = max(s["M_placa"] for s in res_m.values())
# conferência à mão (viga biapoiada no vão entre consoles): reação y = p·H·Lv/2 (sem pino), pino ~ 0
Lv = L - 2 * X_CS
Ry_mao = GQ * p_k * H * Lv / 2
Rz_k = PP * H * L / 2                                   # peso por console (característico)
R["pacotes_suspensos"] = {k: dict(PT2_d_kN=round(max(max(v["trava"]) for v in c.values()), 2), pino_d_kN=round(max(max(v["pinos"]) for v in c.values()), 2),
                                   Ry_console_d_kN=round(max(abs(r["Ry"]) for v in c.values() for r in v["reac"]), 2), M_placa_d_kNm=round(max(v["M_placa"] for v in c.values()), 2))
                           for k, c in pac.items()}
R["mef_parede"] = dict(x_pinos_m=[X_PT, round(L - X_PT, 3)], modelo="ShellMITC4, 8 placas 125 × 10 sobrepostas, consoles a 6 cm das pontas e 94 cm da base, 2 pinos por junta a 0,21 L + 15 cm das pontas",
                       Ry_d_kN=round(Ry_d, 2), Ry_mao_sem_pino_kN=round(Ry_mao, 2), Rz_d_kN=round(Rz_d, 2), Rz_k_kN=round(Rz_k, 2),
                       F_pino_d_kN=round(F_pino_d, 2), M_placa_d_kNm=round(M_placa_d, 2), M_mao_kNm=round(GQ * p_k * H * Lv ** 2 / 8, 2), MRd_placa_kNm=MRd_placa,
                       Mxx_local_max_kNm_m=round(max(s["Mxx_max"][0] for s in res_m.values()), 2), MRd_por_m=round(MRd_placa / H, 2),
                       uso_flexao_placa=round(M_placa_d / MRd_placa, 3), uy_k_mm=round(max(s["uy_max_mm"] for s in res_m.values()), 1),
                       por_fiada={("sobrepressao" if s > 0 else "succao"): [dict(fiada=r["fiada"], lado=r["lado"], Ry=round(r["Ry"], 2), Rz=round(r["Rz"], 2))
                                                                             for r in v["reac"] if r["lado"] == 0] for s, v in res_m.items()},
                       pinos_kN={("sobrepressao" if s > 0 else "succao"): [round(p, 2) for p in v["pinos"]] for s, v in res_m.items()})
assert abs(Rz_d - GF * Rz_k) / (GF * Rz_k) < 0.02, (Rz_d, GF * Rz_k)       # peso: estático
assert M_placa_d <= MRd_placa and max(s_["Mxx_max"][0] for s_ in res_m.values()) <= MRd_placa / H

# ------------------------------------------------------------------ 2. ponta da placa = dente Gerber (bielas e tirantes)
Vd = GN * max(GF, BETA_MONT) * Rz_k                     # kN — montagem governa (γf·βa = 1,69)
Hd = 0.4 * Vd                                           # aço × aço no parafuso de apoio (μ 0,4): retração/temperatura da placa
NB, NH, NP = 120, 200, 60                               # nicho (mm): comprimento a partir da ponta, altura, profundidade
h_nariz = round((H - Z_CS) * 1000 - NH / 2 - 5)         # teto do nicho → topo da placa (−5 do macho/fêmea)
den = Dente("NC-1 ponta da placa", Vd=Vd, Hd=Hd, b=E_PL * 1000, h_dente=h_nariz, ln=NB, a_apoio=X_CS * 1000,
            h_total=H * 1000, fck=PL["secao"]["fck"], c_tir=20.0, x_ash=30.0)   # rev06b: N3 a 20 mm do teto (z 1060), N4 a 30 mm da parede do nicho
rd = den.dimensionar(diam_tir=8.0, diam_sus=8.0, diam_cost=6.3)
R["dente_ponta"] = dict(Vd_kN=round(Vd, 2), Hd_kN=round(Hd, 2), nariz_mm=dict(h=h_nariz, ln=NB, b=round(E_PL * 1000)), resultado=rd,
                        obs="nariz = concreto acima do nicho (teto a 104 cm); tirante horizontal Ø8 sobre o teto do nicho, suspensão em grampos Ø8 junto à face interna do nicho, até as cordoalhas de baixo")
assert rd["adotado"]["ok"]

# ------------------------------------------------------------------ 3. console CS-1 (N, mm, MPa)
# rev06c (18/10/2026): geometria compatibilizada peça a peça (ver GEO, que alimenta as pranchas PP01–PP04 e o IFC).
# Eixos do console: y a partir da face da CE-1 (rumo à placa), z a partir do topo da mesa, x no eixo do console.
FY, FU, ES = 345.0, 450.0, 200000.0                     # A572-50
GA1, GA2, GW2 = 1.10, 1.35, 1.35                         # NBR 8800:2008 tab. 3
T_COST = float(os.environ.get("CS1_T_COST", 16.0))     # costas (soldada na CE-1)
Z0_COST, Z1_COST = float(os.environ.get("CS1_Z0_COST", -100.0)), 30.0   # rev06d: costas 130 (z −100 a +30; antes −170, 200 mm): só a altura da ligação com almas e mesa + 20 abaixo da raiz
B_COST, H_COST = 120.0, Z1_COST - Z0_COST
T_ALMA, X_ALMA = 9.5, 35.0                              # 2 almas a ±35 do eixo
Y_PONTA, H_RAIZ, H_PONTA = 64.0, 80.0, 50.0             # ponta do braço e alturas da alma (raiz 80: janela de montagem, ver abaixo)
T_MESA, B_MESA = 16.0, 80.0                             # mesa y 16–64, x ±40
Y_NIV = 48.0                                            # parafuso de nível M16 (porca ISO 4032 soldada no topo da mesa + contraporca ISO 4035)
Y_M20 = Y_NIV                                           # (nome histórico)
DENTE = dict(t=19.0, b=13.0, h=32.0, y0=44.5, x0=27.0)  # 2 dentes y 44,5–63,5, x ±(27–40), 32 de altura
Y_DENTE = DENTE["y0"] + DENTE["t"] / 2
PONTA = dict(t=9.5, y0=54.5, z0=-50.0, z1=-16.0, b=2 * (X_ALMA - T_ALMA / 2))   # chapa de ponta entre as almas (60,5)
Z_FRONT = -33.0                                         # prisioneiro M16 frontal (porca ISO 4032 soldada atrás da chapa de ponta)
# folgas e tolerâncias de montagem (mm)
A_NOM, A_TOL = 25.0, 5.0                                # afastamento placa–pilar (face interna da placa a y = a)
G_NOM, G_TOL = 50.0, 10.0                               # topo da mesa → face inferior do teto do nicho (regulado pelo M16 de nível)
NC = dict(B=120.0, H=200.0, P=60.0, y_gr=31.0, d_gr=6.3, x_gr=((20.0, 52.0), (68.0, 100.0)), h_gr_teto=40.0, h_gr_base=28.0, t_teto=12.5, t_base=9.5, t_fundo=12.5, t_parede=3.0, t_aba=12.5, h_aba=38.0,
          aba_e=(0.0, 39.0), aba_d=(81.0, 117.0))      # nicho: x a partir da ponta da placa; abas só nas laterais (o meio fica livre para o M16 de nível)
X_TOL = 5.0                                             # posição do console em relação ao nicho (comprimento da placa ±5, soldagem do CS-1 ±3)
HEX = dict(s=24.0, e=26.75, k=10.0, m=14.8, m_fina=8.0)  # M16: ISO 4017 / ISO 4032 / ISO 4035
L_NIV, L_FRONT = 45.0, 45.0                             # M16 × 45 8.8 rosca total (nível) e prisioneiro M16 × 45 ISO 4026 (frontal)
Vd_N = Vd * 1e3
Fy_N = Ry_d * 1e3                                       # vento por console (sobrepressão no frontal / sucção nos dentes)

# ---- geometria: verificação de interferências e da janela de montagem (todas as combinações extremas de a, G e x)
r_hex = HEX["e"] / 2
int_ = NC["H"] - NC["t_teto"] - NC["t_base"]            # 178: vão livre interno
y_aba_max = A_NOM + A_TOL + NC["t_aba"]                 # face de trás da aba no pior caso
y_fundo_min = A_NOM - A_TOL + NC["P"] - NC["t_fundo"]   # face interna do fundo no pior caso
D_boca = H_RAIZ - (H_RAIZ - H_PONTA) * (A_NOM - A_TOL - T_COST) / (Y_PONTA - T_COST)   # altura do braço no plano da boca (a mínimo)
eng = [NC["h_aba"] + DENTE["h"] - G for G in (G_NOM - G_TOL, G_NOM + G_TOL)]
chk = {
    "aba atrás x dente (y)": DENTE["y0"] - y_aba_max,
    "ponta x fundo (y)": y_fundo_min - Y_PONTA,
    "porca de nível na mesa (y)": min(Y_NIV - r_hex - T_COST, Y_PONTA - (Y_NIV + r_hex)),
    "cabeça do nível sob o teto (y)": min(Y_NIV - r_hex - (A_NOM + A_TOL), y_fundo_min - (Y_NIV + r_hex)),
    "cabeça do nível x abas (x)": min(NC["B"] / 2 - X_TOL - r_hex - NC["aba_e"][1], NC["aba_d"][0] - (NC["B"] / 2 + X_TOL + r_hex)),
    "dente dentro da aba E (x)": min(NC["B"] / 2 - X_TOL - (DENTE["x0"] + DENTE["b"]) - NC["aba_e"][0], NC["aba_e"][1] - (NC["B"] / 2 + X_TOL - DENTE["x0"])),
    "dente dentro da aba D (x)": min(NC["B"] / 2 - X_TOL + DENTE["x0"] - NC["aba_d"][0], NC["aba_d"][1] - (NC["B"] / 2 + X_TOL + DENTE["x0"] + DENTE["b"])),
    "dente x porca de nível (x)": DENTE["x0"] - r_hex,
    "aba x mesa com G mínimo (z)": G_NOM - G_TOL - NC["h_aba"],
    "dente x teto com G mínimo (z)": G_NOM - G_TOL - DENTE["h"],
    "engate aba–dente com G máximo (z)": min(eng),
    "cabeça x contraporca com G mínimo (z)": G_NOM - G_TOL - HEX["k"] - (HEX["m"] + HEX["m_fina"]),
    "rosca engatada do nível com G máximo (z)": (HEX["m"] + HEX["m_fina"]) - (G_NOM + G_TOL - HEX["k"] - L_NIV),
    "ponta do nível acima da face de baixo da mesa (z)": (G_NOM - G_TOL - HEX["k"] - L_NIV) + T_MESA,
    "porca frontal abaixo da mesa (z)": -T_MESA - (Z_FRONT + r_hex),
    "prisioneiro: ponta de trás x costas (y)": (A_NOM - A_TOL + NC["P"] - NC["t_fundo"]) - L_FRONT - T_COST,
    "prisioneiro: rosca na porca com a máximo (y)": PONTA["y0"] - HEX["m"] - ((A_NOM + A_TOL + NC["P"] - NC["t_fundo"]) - L_FRONT),
}
# janela de montagem: a placa chega pela face interna com o teto R acima da posição final, a aba passa por cima dos dentes
# (aba ≥ dente + 5) e a base passa por baixo do braço no plano da boca (base ≤ braço − 5)
jan = {}
for G in (G_NOM - G_TOL, G_NOM, G_NOM + G_TOL):
    R_min = DENTE["h"] + 5 + NC["h_aba"] - G
    R_max = int_ - G - D_boca - 5
    jan[f"G={G:.0f}"] = (round(R_min, 1), round(R_max, 1))
    chk[f"janela de montagem G={G:.0f} (z)"] = R_max - R_min
R["montagem_CS1_NC1"] = dict(folgas_mm={k: round(v, 1) for k, v in chk.items()}, janela_R_mm=jan,
                             obs="R = altura do teto do nicho acima da posição final ao encostar a placa; tolerâncias a = 25 ± 5, G = 50 ± 10, x ± 5")
bad = {k: v for k, v in chk.items() if v < (10.0 if k.startswith("janela") or k.startswith("engate") else (16.0 if k.startswith("rosca") else 0.0))}
assert not bad, bad


def mef_console(Fz, Fy, ponto_y, Mx=0.0):
    """Casca: costas (plano x-z em y = T/2), 2 almas (planos y-z em x = ±35), mesa (plano x-y no topo).
    Engaste nas duas bordas verticais das costas (linhas de solda). Fz no M16 de nível; Fy na chapa de ponta (frontal)
    ou nos dentes (com o momento Mx = Fy·braço do contato ao topo da mesa)."""
    ops.wipe(); ops.model("basic", "-ndm", 3, "-ndf", 6)
    ops.section("ElasticMembranePlateSection", 1, ES, 0.3, T_COST, 0.0)
    ops.section("ElasticMembranePlateSection", 2, ES, 0.3, T_ALMA, 0.0)
    ops.section("ElasticMembranePlateSection", 3, ES, 0.3, T_MESA, 0.0)
    nos = {}
    def no(x, y, z):
        k = (round(x, 3), round(y, 3), round(z, 3))
        if k not in nos:
            nos[k] = len(nos) + 1
            ops.node(nos[k], *k)
        return nos[k]
    E = []
    def malha(p00, p10, p01, p11, n1, n2, sec, nome):
        P = lambda u, v: [p00[i] * (1 - u) * (1 - v) + p10[i] * u * (1 - v) + p01[i] * (1 - u) * v + p11[i] * u * v for i in range(3)]
        for i in range(n1):
            for j in range(n2):
                a = no(*P(i / n1, j / n2)); b = no(*P((i + 1) / n1, j / n2)); c = no(*P((i + 1) / n1, (j + 1) / n2)); d = no(*P(i / n1, (j + 1) / n2))
                e = len(E) + 1000
                ops.element("ShellMITC4", e, a, b, c, d, sec)
                E.append((e, sec, nome))
    yc = T_COST / 2
    zt = 0.0
    malha((-60, yc, zt + Z0_COST), (60, yc, zt + Z0_COST), (-60, yc, zt + Z1_COST), (60, yc, zt + Z1_COST), 24, round(H_COST / 10), 1, "costas")
    for xa in (-X_ALMA, X_ALMA):
        malha((xa, yc, zt - H_RAIZ), (xa, Y_PONTA, zt - H_PONTA), (xa, yc, zt), (xa, Y_PONTA, zt), 14, round(H_RAIZ / 10), 2, "alma")   # 10 mm na raiz = malha das costas (nós comuns)
    malha((-X_ALMA, yc, zt), (X_ALMA, yc, zt), (-X_ALMA, Y_PONTA, zt), (X_ALMA, Y_PONTA, zt), 14, 14, 3, "mesa")
    if True:
        ops.section("ElasticMembranePlateSection", 4, ES, 0.3, PONTA["t"], 0.0)
        malha((-X_ALMA, Y_PONTA, zt - H_PONTA), (X_ALMA, Y_PONTA, zt - H_PONTA), (-X_ALMA, Y_PONTA, zt), (X_ALMA, Y_PONTA, zt), 14, round(H_RAIZ / 10), 4, "chapa de ponta")
    solda = [n_ for (x, y, z), n_ in nos.items() if abs(abs(x) - 60) < 1e-6 and abs(y - yc) < 1e-6]
    for n_ in solda:
        ops.fix(n_, 1, 1, 1, 1, 1, 1)
    ops.timeSeries("Linear", 1); ops.pattern("Plain", 1, 1)
    def mais_prox(x, y, z):
        return min(nos.items(), key=lambda kv: (kv[0][0] - x) ** 2 + (kv[0][1] - y) ** 2 + (kv[0][2] - z) ** 2)[1]
    anel = [n_ for (x, y, z), n_ in nos.items() if abs(z - zt) < 1e-6 and math.hypot(x, y - Y_NIV) <= HEX["s"] / 2 + 0.5]
    for n_ in anel:                                      # porca de nível soldada: apoio na área da porca (s = 24)
        ops.load(n_, 0, 0, -Fz / len(anel), 0, 0, 0)
    if ponto_y == Y_DENTE:                               # 2 dentes sobre as almas: força + momento no topo da mesa
        Fc = Mx / DENTE["t"]                             # momento do dente como binário vertical na base do dente (sobre a alma)
        for xa in (-X_ALMA, X_ALMA):
            ops.load(mais_prox(xa, ponto_y, zt), 0, Fy / 2, 0, 0, 0, 0)
            ops.load(mais_prox(xa, DENTE["y0"] + DENTE["t"], zt), 0, 0, Fc / 2, 0, 0, 0)
            ops.load(mais_prox(xa, DENTE["y0"], zt), 0, 0, -Fc / 2, 0, 0, 0)
    else:                                                # porca do prisioneiro frontal na chapa de ponta (área da porca)
        anf = [n_ for (x, y, z), n_ in nos.items() if abs(y - Y_PONTA) < 1e-6 and math.hypot(x, z - (zt + Z_FRONT)) <= HEX["s"] / 2 + 0.5]
        for n_ in anf:
            ops.load(n_, 0, Fy / len(anf), 0, 0, 0, 0)
    ops.system("UmfPack"); ops.numberer("RCM"); ops.constraints("Plain")
    ops.integrator("LoadControl", 1.0); ops.test("NormDispIncr", 1e-12, 10); ops.algorithm("Newton"); ops.analysis("Static")  # Newton: o estado dos elementos de casca só é atualizado com o resíduo (com "Linear" as tensões saem zeradas)
    assert ops.analyze(1) == 0
    ops.reactions()
    t_sec = {1: T_COST, 2: T_ALMA, 3: T_MESA, 4: PONTA["t"]}
    vm = []
    for (e, sec, nome) in E:
        s = np.array(ops.eleResponse(e, "stresses")).reshape(4, 8).mean(0)
        t = t_sec[sec]
        for sg in (+1, -1):
            sx = s[0] / t + sg * 6 * s[3] / t ** 2
            sy = s[1] / t + sg * 6 * s[4] / t ** 2
            txy = s[2] / t + sg * 6 * s[5] / t ** 2
            vm.append((math.sqrt(sx ** 2 - sx * sy + sy ** 2 + 3 * txy ** 2), nome, e))
    vm.sort(reverse=True)
    vals = [v for v, _, _ in vm]
    v95 = float(np.percentile(vals, 99))
    flecha = abs(ops.nodeDisp(mais_prox(0, Y_NIV, zt), 3))
    Rsol = [(ops.nodeCoord(n_), ops.nodeReaction(n_)) for n_ in solda]
    return dict(vm_max=vm[0][0], vm_p99=v95, flecha_mm=flecha, reac_solda=Rsol)


BR_DENTE = DENTE["h"] - 5.0                              # contato no engate mínimo (10 mm): resultante a 5 mm do topo do dente
casos = {"peso + sobrepressão": (Vd_N, -Fy_N, Y_PONTA, 0.0), "peso + sucção": (Vd_N, +Fy_N, Y_DENTE, -Fy_N * BR_DENTE)}
mc = {k: mef_console(*v) for k, v in casos.items()}
sig_Rd = FY / GA1
vm_proj = max(v["vm_p99"] for v in mc.values())
R["console_mef"] = {k: dict(vm_max_MPa=round(v["vm_max"], 1), vm_p99_MPa=round(v["vm_p99"], 1), flecha_mm=round(v["flecha_mm"], 3)) for k, v in mc.items()}
R["console_mef"]["criterio"] = f"von Mises (percentil 99, sem o pico singular no canto engastado) ≤ fy/γa1 = {sig_Rd:.0f} MPa — critério de von Mises do EN 1993-1-1:2005 6.2.1(5), γa1 = 1,10 da NBR 8800:2008"
R["console_mef"]["uso"] = round(vm_proj / sig_Rd, 3)
assert vm_proj <= sig_Rd

# conferência à mão das almas na raiz: M = Vd·(Y_NIV − T_COST), W = 2·t·h²/6
M_raiz = Vd_N * (Y_NIV - T_COST)
W_almas = 2 * T_ALMA * H_RAIZ ** 2 / 6
b_mesa = Y_PONTA - T_COST
M_mesa = Vd_N * 2 * X_ALMA / 4
R["console_mao"] = dict(M_raiz_Nmm=round(M_raiz), sigma_almas_MPa=round(M_raiz / W_almas, 1), tau_almas_MPa=round(Vd_N / (2 * T_ALMA * H_RAIZ), 1),
                        mesa_faixa_MPa=round(6 * M_mesa / (b_mesa * T_MESA ** 2), 1), obs="mesa como faixa biapoiada nas almas (sem efeito de placa): limite superior do MEF")

# dentes (2 × 19 × 13 × 32, A572-50): balanço com a sucção no topo — NBR 8800:2008 5.4.2 (Wel·fy/γa1) e solda de filete 8 no contorno
F_den = Fy_N / 2
M_den = F_den * BR_DENTE
W_den = DENTE["b"] * DENTE["t"] ** 2 / 6
aw8 = 0.707 * 8.0
Sw_den = DENTE["b"] * DENTE["t"] + DENTE["t"] ** 2 / 3                  # módulo do contorno (por mm de garganta), flexão no sentido de t
f_w_den = math.hypot(M_den / (Sw_den * aw8), F_den / (2 * (DENTE["b"] + DENTE["t"]) * aw8))
fw_Rd = 0.60 * 485.0 / GW2
R["dentes_CS1"] = dict(peca="2 dentes ch. 19 × 13 × 32 A572-50 sobre as almas, filete 8 no contorno", F_por_dente_kN=round(F_den / 1e3, 2), braco_mm=BR_DENTE,
                       sigma_MPa=round(M_den / W_den, 1), lim_MPa=round(sig_Rd, 1), uso=round(M_den / W_den / sig_Rd, 3),
                       solda_MPa=round(f_w_den, 1), solda_lim_MPa=round(fw_Rd, 1), uso_solda=round(f_w_den / fw_Rd, 3))
assert M_den / W_den <= sig_Rd and f_w_den <= fw_Rd

# solda de campo CS-1 × CE-1: 2 cordões verticais de 200 mm, perna 6 (garganta 4,24) — NBR 8800:2008 6.2.5.1 (método vetorial elástico)
A_W, L_W, FW = 6.0, H_COST, 485.0
tw = 0.707 * A_W
Aw = 2 * L_W * tw
Iw = 2 * tw * L_W ** 3 / 12
e_z = Y_NIV
z_max = L_W / 2
f_v = Vd_N / Aw
f_n_M = Vd_N * e_z * z_max / Iw
f_n_F = Fy_N / Aw + Fy_N * abs((Z0_COST + Z1_COST) / 2) * z_max / Iw   # vento normal à CE-1 + braço até o centroide do cordão
f_res = math.sqrt(f_v ** 2 + (f_n_M + f_n_F) ** 2)
R["solda"] = dict(filete_mm=A_W, cordoes="2 × 200 verticais", eletrodo="E70XX", f_res_MPa=round(f_res, 1), fw_Rd_MPa=round(fw_Rd, 1),
                  uso=round(f_res / fw_Rd, 3), obs="solda de campo: inspeção visual 100 % e líquido penetrante por amostragem; galvanização a frio após a solda")
assert f_res <= fw_Rd

# parafusos de ajuste: M16 × 45 8.8 de nível (compressão; λ = 2·40/(16/4) = 20), prisioneiro M16 × 45 frontal
fub88 = 800.0
A16 = 157.0
Nc_niv = A16 * 640 / GA1
Nc_fr = A16 * 450 / GA1                                  # prisioneiro classe 45H: fy de referência 450 MPa (a favor da segurança)
dw = 22.5                                                # diâmetro de apoio da cabeça M16 (ISO 4017)
sig_cab = Vd_N / (math.pi * (dw ** 2 - 17.5 ** 2) / 4)
w_porca_fr = 6 * HEX["s"] / math.sqrt(3) * 0.707 * 5.0 * fw_Rd   # filete 5 no contorno da porca frontal (6 lados de s/√3), tracionada pela sobrepressão
R["parafusos_ajuste"] = dict(M16_nivel=dict(N_Sd_kN=round(Vd, 1), N_Rd_kN=round(Nc_niv / 1e3, 1), uso=round(Vd_N / Nc_niv, 3)),
                             M16_frontal=dict(N_Sd_kN=round(Ry_d, 1), N_Rd_kN=round(Nc_fr / 1e3, 1), uso=round(Fy_N / Nc_fr, 3),
                                              solda_porca_kN=round(w_porca_fr / 1e3, 1)),
                             contato_teto_nicho=dict(obs="cabeça do M16 de nível (dw 22,5) contra o teto 12,5 do nicho",
                                                     sigma_MPa=round(sig_cab, 1), lim_MPa=round(1.5 * FY / GA2, 0)))
assert Vd_N <= Nc_niv and Fy_N <= Nc_fr and Fy_N <= w_porca_fr and sig_cab <= 1.5 * FY / GA2

# CE-1 no pilar: 4 pinos Ø16 c/ cabeça Ø32, hef 150 + 2 grampos U Ø10, a ±120 (x) e ±140 (z) — 2 consoles por chapa, carga das 2 placas
V_ce = 2 * Vd                                            # kN
M_ce = 2 * Vd * (Y_NIV + 8.0) / 1000                    # kN·m (do plano médio da CE-1)
N_ce_vento = 2 * Ry_d                                    # sucção puxa a CE-1 (as duas placas no mesmo sentido)
z_ce = 280.0                                             # braço entre linhas de pinos
T_linha = M_ce * 1000 / z_ce + N_ce_vento / 2            # tração na linha superior (2 pinos)
T_CE = 16.0                                              # rev06b: CE-1 em 16 mm
grp = GrupoPinos(d=16.0, d_cabeca=32.0, hef=150.0, nx=2, ny=2, sx=240.0, sy=280.0, cx_neg=80.0, cx_pos=80.0,
                 cy_neg=400.0, cy_pos=400.0, ha=600.0, fc=40.0)
t = grp.tracao()
v_perp = grp.cortante("x+")                              # ruptura de borda perpendicular à face lateral (c1 = 80)
# cortante vertical: paralelo às faces laterais do pilar → ACI 318-19 17.7.2.1(c): 2 × Vcbg perpendicular, ψed = 1
v_par = 2 * v_perp["todos_kN"]["borda"]
V_grampos = 2 * grampo_ancoragem_kN(10.0)                # 2 grampos U Ø10 envolvendo os pinos (armadura de ancoragem, ACI 17.5.2.1)
cands = dict(aco=v_perp["todos_kN"]["aco"], borda_paralela=max(v_par, V_grampos), pryout=v_perp["todos_kN"]["pryout"])
v = dict(phiVn_kN=min(cands.values()), modo=min(cands, key=cands.get), todos_kN=cands)
# tração: só a linha superior (2 pinos) — grupo de 2: proporcional
phiN_linha = t["phiNn_kN"] / 2
ri, ok_i = interacao(T_linha, phiN_linha, V_ce, v["phiVn_kN"])
R["CE1"] = dict(peca="CE-1 380 × 330 × 16 A36 + 4 pinos Ø16 × 150 c/ cabeça Ø32 (a 240 × 280) + 2 grampos U Ø10 no pilar", V_kN=round(V_ce, 1), M_kNm=round(M_ce, 2),
                T_linha_sup_kN=round(T_linha, 1), phiN_linha_kN=round(phiN_linha, 1), phiV_kN=round(v["phiVn_kN"], 1), modo_V=v["modo"],
                modo_N=t["modo"], interacao=round(ri, 3), ok=ok_i)
assert ok_i

# ------------------------------------------------------------------ 4. pino de travamento PT-1 (cartola Trejor)
Fv_M16 = Fv_Rd_cm(1.6, fub=80.0) if False else 0.45 * 201 * fub88 / GA2 / 1e3      # kN, corte (rosca no plano)
Ft_M16 = 0.75 * 201 * fub88 / GA2 / 1e3
# luva TSA M16 na placa de 10 cm: hef 70, borda à junta 60 mm (tração = força fora do plano)
lv = GrupoPinos(d=16.0, d_cabeca=30.0, hef=70.0, nx=1, ny=1, sx=0, sy=0, cx_neg=500.0, cx_pos=500.0, cy_neg=60.0, cy_pos=1000.0, ha=100.0, fc=25.0)
tl = lv.tracao()
R["pino_travamento"] = dict(peca="PT-1 cartola Trejor (chapa dobrada 6,3 × 80, oblongo vertical 18 × 40) + 2 M16 8.8 nas luvas TSA M16 das duas placas; 2 por junta, ao lado das alças AL-P",
                            F_d_kN=round(F_pino_d, 2), Ft_M16_kN=round(Ft_M16, 1), luva_phiN_kN=round(tl["phiNn_kN"], 1), modo=tl["modo"],
                            uso=round(F_pino_d / min(Ft_M16, tl["phiNn_kN"]), 3), fc_usado="fckj 25 MPa (montagem a favor da segurança)")
assert F_pino_d <= min(Ft_M16, tl["phiNn_kN"])

# ------------------------------------------------------------------ 5. trava de pé PT-2 (1ª placa de pacote suspenso: E/F e acima das esquadrias)
# L 102×102×9,5 A36 L = 150: aba na face lateral do pilar (M16 8.8 em bucha BR-2 M16 hef 100, oblongo vertical 18 × 40) e aba na face
# interna da placa (M16 8.8 em bucha BR-1 M16 hef 70, oblongo horizontal 18 × 40), a 15 cm da base da placa. Só força fora do plano.
M_pt2 = F_pt2_d * 0.050                                   # kN·m: braço do furo à face da outra aba (50 mm)
MRd_pt2 = 0.150 * 0.0095 ** 2 / 6 * 250e3 / 1.10          # NBR 8800:2008 (Wel·fy/γa1)
bucha_placa = GrupoPinos(d=16.0, d_cabeca=30.0, hef=70.0, nx=1, ny=1, sx=0, sy=0, cx_neg=250.0, cx_pos=1000.0, cy_neg=150.0, cy_pos=1000.0, ha=100.0, fc=25.0).tracao()
bucha_pilar = GrupoPinos(d=16.0, d_cabeca=30.0, hef=100.0, nx=1, ny=1, sx=0, sy=0, cx_neg=60.0, cx_pos=340.0, cy_neg=1000.0, cy_pos=1000.0, ha=400.0, fc=40.0)
vp = bucha_pilar.cortante("x-")                           # na bucha do pilar a força fora do plano da placa é cortante, rumo à face externa (60 mm)
R["trava_pe_PT2"] = dict(peca="PT-2 L 102×102×9,5 A36 L=150 + 2 M16 8.8 (bucha BR-2 hef 100 na face lateral do pilar, bucha BR-1 hef 70 na placa), oblongos 18 × 40",
                         F_d_kN=round(F_pt2_d, 2), M_aba_kNm=round(M_pt2, 3), MRd_aba_kNm=round(MRd_pt2, 3), uso_aba=round(M_pt2 / MRd_pt2, 3),
                         bucha_placa_phiN_kN=round(bucha_placa["phiNn_kN"], 1), bucha_pilar_phiV_kN=round(vp["phiVn_kN"], 1), modo_pilar=vp["modo"],
                         uso=round(max(M_pt2 / MRd_pt2, F_pt2_d / bucha_placa["phiNn_kN"], F_pt2_d / vp["phiVn_kN"]), 3))
assert R["trava_pe_PT2"]["uso"] <= 1, R["trava_pe_PT2"]

# ------------------------------------------------------------------ 6. nicho NC-1 (caixa de oficina) e ancoragem no concreto da placa
# rev06c: eixos do nicho — x a partir da ponta da placa (0–120), y a partir da boca (face interna da placa, 0–60), z a partir do fundo do nicho (0–200).
# teto 120 × 47,5 × 12,5 (z 187,5–200) e base 120 × 47,5 × 9,5 (z 0–9,5); fundo 120 × 200 × 12,5 (y 47,5–60) vence o vão entre teto e base;
# parede lateral 3 mm (x 117–120) só fecha o concreto (não recebe esforço); 2 abas 12,5 × 38 só nas laterais (x 0–39 e 81–117), soldadas sob
# o teto na boca, deixando o meio livre para o M16 de nível. Todas as chapas estruturais em A572-50; parede em A36.
# Caminho das forças: peso → M16 de nível → teto → nariz (compressão); sucção → dentes → abas → teto → grampos + estribo N5;
# sobrepressão → prisioneiro frontal → fundo (viga entre teto e base) → teto e base → grampos + estribos N5 (em cima) e N6 (embaixo).
FY36 = 250.0
FYNC = FY                                                # A572-50 no NC-1
Ls_f = int_                                              # vão livre do fundo entre teto e base (178)
a_f = int_ - G_NOM + Z_FRONT                             # altura do prisioneiro acima da base (95)
M_fundo = Fy_N * a_f * (Ls_f - a_f) / Ls_f               # N·mm (biapoiado entre teto e base, sem contar o concreto atrás)
W_fundo = NC["B"] * NC["t_fundo"] ** 2 / 6
R_teto = Fy_N * a_f / Ls_f; R_base = Fy_N - R_teto
b_aba = min(NC["aba_e"][1] - NC["aba_e"][0], NC["aba_d"][1] - NC["aba_d"][0])
M_aba = Fy_N / 2 * (NC["h_aba"] - 5.0)                    # cada aba recebe um dente; contato no engate mínimo, a 5 mm da borda
W_aba = b_aba * NC["t_aba"] ** 2 / 6
sig_teto = Vd_N / (NC["B"] * (NC["P"] - NC["t_fundo"]))   # compressão do teto no nariz (peso)
fcd = 40 / 1.4
fctd = 0.21 * 40 ** (2 / 3) / 1.4
V_parede = (200 + 40 + 2 * (120 + 20)) * 40 * 0.30 * fctd  # registro: parede de 40 mm atrás do fundo sem a caixa
phi_N5 = 0.75 * 2 * 31.2 * 420 / 1e3
F_teto = max(Fy_N, R_teto) / 1e3
F_base = R_base / 1e3
g8 = 0.75 * 4 * 31.2 * 250 / 1e3                          # rev06c: 2 grampos U Ø6,3 A36 (4 pernas) por chapa, dentro do estribo N5/N6 (y = 31 da boca)
R["nicho_NC1"] = dict(
    caixa="teto 12,5 + base 9,5 + fundo 12,5 + 2 abas 12,5 × 38 (A572-50) + parede lateral 3 (A36, sem esforço), solda de oficina MIG, galvanizado a fogo, + 4 grampos U Ø6,3 A36 (c/c 32, a 31 mm da boca, dentro dos estribos N5 e N6)",
    fundo=dict(M_kNmm=round(M_fundo / 1e3, 1), sigma_MPa=round(M_fundo / W_fundo, 1), lim_MPa=round(FYNC / GA1, 1), uso=round(M_fundo / W_fundo / (FYNC / GA1), 3)),
    aba=dict(sigma_MPa=round(M_aba / W_aba, 1), largura_mm=b_aba, uso=round(M_aba / W_aba / (FYNC / GA1), 3)),
    parede=dict(t_mm=NC["t_parede"], obs="sem esforço: as forças vão por teto, base e fundo; a parede só fecha o concreto na lateral do nicho"),
    teto_compressao=dict(sigma_MPa=round(sig_teto, 2), fcd_MPa=round(fcd, 1)),
    sem_caixa_parede_40mm=dict(V_Rd_kN=round(V_parede / 1e3, 1), F_kN=round(Fy_N / 1e3, 1), obs="fundo apoiado só na parede de 40 mm não passaria — por isso o fundo vence o vão entre teto e base"),
    ancoragem_teto=dict(F_kN=round(F_teto, 1), N5_phi_kN=round(phi_N5, 1), grampos_phi_kN=round(g8, 1), uso=round(F_teto / min(phi_N5, g8), 3)),
    ancoragem_base=dict(F_kN=round(F_base, 1), N6_phi_kN=round(phi_N5, 1), grampos_phi_kN=round(g8, 1), uso=round(F_base / min(phi_N5, g8), 3)))
assert M_fundo / W_fundo <= FYNC / GA1 and M_aba / W_aba <= FYNC / GA1 and F_teto <= min(phi_N5, g8) and F_base <= min(phi_N5, g8)
# geometria única para pranchas e IFC
R["GEO"] = dict(CS1=dict(costas=dict(t=T_COST, b=B_COST, z0=Z0_COST, z1=Z1_COST), alma=dict(t=T_ALMA, x=X_ALMA, y0=T_COST, y1=Y_PONTA, h_raiz=H_RAIZ, h_ponta=H_PONTA),
                         mesa=dict(t=T_MESA, b=B_MESA, y0=T_COST, y1=Y_PONTA), dente=DENTE, ponta=PONTA, y_nivel=Y_NIV, z_frontal=Z_FRONT,
                         L_nivel=L_NIV, L_frontal=L_FRONT),
                NC1=NC, hex=HEX, tol=dict(a=A_NOM, a_tol=A_TOL, G=G_NOM, G_tol=G_TOL, x_tol=X_TOL))
# CE-1 à flexão local: tração do topo do console (M = Vd·e / braço 2/3·200) levada ao pino mais próximo (40 mm), faixa de 100 mm
T_topo = Vd_N * (Y_NIV + 8) / (2 / 3 * H_COST)
M_ce_loc = T_topo * 40 / 2
R["CE1"]["flexao_chapa"] = dict(t_mm=T_CE, sigma_MPa=round(6 * M_ce_loc / (100 * T_CE ** 2), 1), lim_MPa=round(FY36 / GA1, 1))
assert 6 * M_ce_loc / (100 * T_CE ** 2) <= FY36 / GA1

R["cargas_por_console"] = dict(G_k_kN=round(Rz_k, 2), Vd_kN=round(Vd, 2), vento_d_kN=round(Ry_d, 2),
                               obs="placa PP-01 (L 10,165 m, 3,24 t); Vd com γf 1,3 × βa 1,3 de montagem (NBR 9062:2017 5.3.2), maior que 1,4 da fase final")
(Path(os.environ.get("CS1_SAIDA", AQ / "fixacao_placas.json"))).write_text(json.dumps(R, indent=1, ensure_ascii=False, default=float), encoding="utf-8")
if __name__ == "__main__":
    print(json.dumps(R, indent=1, ensure_ascii=False, default=float))
