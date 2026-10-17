"""Letsara — cobertura metálica: terças Z Metsec contínuas por transpasse (METLAP), correntes, contraventamento em X,
suporte ST-1P e esperas no concreto. Sem mão-francesa (rev05).

Rev. 05 (17/10/2026): terças Z 302×90/82×2,30 (voestalpine Meincol / METSEC, fy 400) contínuas nos 8 vãos por transpasse
sobre cada viga; esforços por MEF de viga contínua (nd_estruturas.viga_continua) com 2·EI no trecho do transpasse;
comprimento do transpasse escolhido como o menor que atende; parafusos do transpasse e do apoio (2 M12 8.8 na alma, sem
mão-francesa); escoras linha a linha com N do modelo global R01 e M do MEF contínuo.
Rev. 13/10/2026: esforços da terça-escora e do X lidos do modelo global R01; X só nos vãos 2-3 e 7-8; correntes Ø10.

Normas: NBR 14762:2010 (perfis formados a frio, MRD), NBR 8800:2008 (ligações, laminados, Anexo C flechas), NBR 8681:2003,
NBR 6123:1988 (vento), ACI 318-19 cap. 17 (chumbadores), AISI S100-16 D3.2 (travamento de terças Z). Unidades kN, m (perfis em mm).
"""
import json, math, os, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from nd_estruturas.metalica_fria import (PerfilZ, parafuso_corte_Rd, parafuso_tracao_Rd, pressao_contato_fino_Rd,
                                         pressao_contato_Rd, barra_redonda_tracao_Rd, compressao_laminado_Rd)
from nd_estruturas.ancoragem import GrupoPinos, interacao, grampo_ancoragem_kN
from nd_estruturas.viga_continua import analisar

AQUI = Path(__file__).parent
R = {}

# ------------------------------------------------------------------ dados
from geometria import VAOS_Y
LG = json.loads((AQUI / "ligacoes.json").read_text(encoding="utf-8"))
L = max(VAOS_Y)          # maior vão de terça (10,075 m)
s = LG["passo_tercas"]   # espaçamento entre terças (ao longo da água)
CC = LG["cargas_cob"]    # zipada 0,65 + lã de rocha 40 + TP40 0,50 + fixações + painéis solares + instalações (ligacoes.py)
q0 = 0.874               # kN/m² — V0 45 m/s, S2 cat. III classe C, S3 0,95
cp = dict(geral=-1.0, borda=-1.6)    # Cpe −0,8 / −1,4 (faixa de borda, NBR 6123 tab. 6) com Cpi +0,2
MG = json.loads((AQUI / "modelo_global_r01.json").read_text(encoding="utf-8"))
ELU = {k: v for k, v in MG["combinacoes"].items() if v["tipo"] == "ELU"}

# Z METSEC 302Z23 (catálogo voestalpine Meincol 2019 p. 6): aba sup. 90 / inf. 82, enrijecedores Lt 19 / Lb 21 (45° adotado,
# conferir), t 2,30, 8,92 kg/m; furos de fixação na alma a E = 55 do topo e F = 52 da base (entre furos 195). fy 400 (fu 480 adotado).
Z = dict(bw=302, bf_sup=90, bf_inf=82, D_sup=19, D_inf=21, t=2.30, kg_m=8.92, E=55, F=52, nome="Z 302×90/82×2,30 (METSEC 302Z23)")
u = PerfilZ(Z["bw"], Z["bf_sup"], Z["D_sup"], Z["t"], "METSEC400", 45.0, Z["bf_inf"], Z["D_inf"])
peso_kNm = Z["kg_m"] * 9.81e-3
g = CC["g_total_sem_terca"] + peso_kNm / s           # kN/m² (gravidade)
g_fav = CC["g_favoravel_sucao"] + peso_kNm / s       # kN/m² (sucção: painéis e instalações desprezados)
q = CC["sobrecarga"]
cM = u.criticos("M")
cN = u.criticos("N", L_dist_ref=cM["L_dist"])
R["perfil"] = dict(nome=Z["nome"], aco=u.aco, fy=u.fy, fu=u.fu, A_mm2=round(u.p["A"]), Ix_cm4=round(u.p["Ix"] / 1e4, 1),
                   Ixy_cm4=round(u.p["Ixy"] / 1e4, 1), W_cm3=round(u.W / 1e3, 1), kg_m=Z["kg_m"], peso_kNm=round(peso_kNm, 4),
                   furos=dict(E_topo=Z["E"], F_base=Z["F"], entre=Z["bw"] - Z["E"] - Z["F"]),
                   assinatura_M=dict(local=round(cM["f_local"], 3), L_local=cM["L_local"], dist=round(cM["f_dist"], 3), L_dist=cM["L_dist"]),
                   assinatura_N=dict(local=round(cN["f_local"], 3), L_local=cN["L_local"], dist=round(cN["f_dist"], 3), obs=cN["obs_dist"]))

# ------------------------------------------------------------------ terça contínua por transpasse (MEF) — NBR 14762:2010
N_LIN = 3                                   # linhas de correntes por vão (L/4, L/2, 3L/4)
Lcorr = L / (N_LIN + 1)
MRc = u.MRd(0, crit=cM, contida=True)       # mesa superior comprimida, presa à telha (M > 0 aqui: traciona a fibra inferior)
MRb = u.MRd(Lcorr * 1000, Cb=1.0, crit=cM)  # mesa inferior comprimida, travada pelas correntes (M < 0)
VRd = u.VRd()
EI = 200e6 * u.p["Ix"] * 1e-12              # kN·m² (eixo geométrico: mesa superior travada pela telha)
xa = np.concatenate([[0.0], np.cumsum(VAOS_Y)])
n_v = len(VAOS_Y)
w_g, w_q = g * s, q * s


def casos(a):
    """Combinações ELU/ELS no MEF da linha de terças com transpasse ±a (m) em cada apoio interno."""
    tr = [(xa[i] - a, xa[i] + a, 2.0) for i in range(1, n_v)]
    alt = [[1.5 * w_q if (i % 2 == p) else 0.0 for i in range(n_v)] for p in (0, 1)]
    c = {"ELU grav": analisar(VAOS_Y, EI, 1.35 * w_g + 1.5 * w_q, EI_trechos=tr)}
    for p, al in enumerate(alt):
        c[f"ELU grav alt{p}"] = analisar(VAOS_Y, EI, [1.35 * w_g + v_ for v_ in al], EI_trechos=tr)
    for zona, c_ in cp.items():
        c[f"ELU suc {zona}"] = analisar(VAOS_Y, EI, -(1.4 * abs(c_) * q0 - 1.0 * g_fav) * s, EI_trechos=tr)
    els = dict(gq=analisar(VAOS_Y, EI, w_g + w_q, EI_trechos=tr),
               vento=analisar(VAOS_Y, EI, -(abs(cp["geral"]) * q0 - g_fav) * s, EI_trechos=tr))
    return tr, c, els


def verifica(a):
    tr, c, els = casos(a)
    x = c["ELU grav"]["x"]
    dentro = np.zeros_like(x, dtype=bool)
    for (t0, t1, _) in tr:
        dentro |= (x > t0 + 1e-6) & (x < t1 - 1e-6)
    pior = dict(uso=0)
    for nome, r in c.items():
        M, V = r["M"], r["V"]
        Mr = np.where(M >= 0, MRc["MRd"], MRb["MRd"])
        fat = np.where(dentro, 2.0, 1.0)
        uso_M = np.abs(M) / (fat * Mr)
        uso_MV = np.sqrt(uso_M ** 2 + (np.abs(V) / (fat * VRd)) ** 2)          # NBR 14762:2010 9.8.5 (M + V)
        for arr, tipo in ((uso_M, "flexão"), (uso_MV, "flexão + cortante")):
            i = int(np.argmax(arr))
            if arr[i] > pior["uso"]:
                pior = dict(uso=float(arr[i]), tipo=tipo, comb=nome, x_m=round(float(x[i]), 3), M=round(float(M[i]), 2),
                            V=round(float(V[i]), 2), MRd=round(float(Mr[i] * fat[i]), 2), trecho="transpasse (2 Z)" if dentro[i] else "seção simples")
    fl = max(float(np.max(np.abs(els["gq"]["v"]))), float(np.max(np.abs(els["vento"]["v"])))) * 1000
    lim = min(VAOS_Y) * 1000 / 180
    return dict(a=a, pior=pior, flecha_mm=round(fl, 1), flecha_lim_mm=round(lim, 1), ok=pior["uso"] <= 1.0 and fl <= lim), c, els, tr


TRANSPASSES = [0.45, 0.60, 0.75, 0.90, 1.05, 1.20]
estudo_tr = []
for a in TRANSPASSES:
    res, c, els, tr = verifica(a)
    estudo_tr.append(dict(a_m=a, uso=round(res["pior"]["uso"], 3), governa=f'{res["pior"]["tipo"]} — {res["pior"]["comb"]} em x = {res["pior"]["x_m"]} ({res["pior"]["trecho"]})',
                          flecha_mm=res["flecha_mm"], ok=res["ok"]))
    if res["ok"]:
        break
assert res["ok"], estudo_tr
A_TR, CASOS, ELS, TRECHOS = res["a"], c, els, tr

# momentos e reações por vão / apoio (envoltória ELU)
xg = CASOS["ELU grav"]["x"]
por_vao = []
for i in range(n_v):
    msk = (xg >= xa[i]) & (xg <= xa[i + 1])
    Mmax = max(float(np.max(r["M"][msk])) for r in CASOS.values())
    Mmin = min(float(np.min(r["M"][msk])) for r in CASOS.values())
    por_vao.append(dict(vao=f"{i+1}-{i+2}", L_m=VAOS_Y[i], M_pos=round(Mmax, 2), M_neg=round(Mmin, 2)))
Msup = [min(float(r["M"][r["apoio_idx"][j]]) for r in CASOS.values()) for j in range(n_v + 1)]    # hogging no apoio (gravidade)
Msup_s = [max(float(r["M"][r["apoio_idx"][j]]) for r in CASOS.values()) for j in range(n_v + 1)]  # sucção
Rgrav = [max(float(r["reacoes"][j]) for k_, r in CASOS.items() if "grav" in k_) for j in range(n_v + 1)]
Rsuc = [-min(float(r["reacoes"][j]) for k_, r in CASOS.items() if "suc" in k_) for j in range(n_v + 1)]

# parafusos do transpasse: em cada ponta do transpasse 2 M12 8.8 na alma (furos E/F), atravessando as 2 almas.
# O perfil que termina leva M_apoio/2 no apoio e zero na ponta, a uma distância a: força transferida na ponta = (|M|/2)/a,
# dividida pelos 2 parafusos (+ parcela da cortante local, a favor da segurança).
Rb_M12 = min(pressao_contato_fino_Rd(12, u.t, u.fu), parafuso_corte_Rd(12, "8.8"))
F_tr = max((max(abs(Msup[j]), abs(Msup_s[j])) / 2 / A_TR) / 2 for j in range(1, n_v))
# apoio (ST-1P): 4 M12 8.8 na alma (2 colunas a ±60 do eixo do apoio × 2 linhas nos furos E/F, sem mão-francesa); no apoio
# interno os 4 parafusos atravessam ST-1P + as 2 almas do transpasse. A torção de apoio T = R·e (carga no meio da mesa superior
# até a alma) é resistida pelo binário das 2 linhas (braço z = 195): a linha de cima tracionada (T/z, 2 parafusos) e a alma
# apoiada no ST-1P embaixo; a reação R e a força de escora N vão em corte nos 4 parafusos.
z_par = (Z["bw"] - Z["E"] - Z["F"]) / 1000
e_tor = Z["bf_sup"] / 2 / 1000
Ft_M12 = parafuso_tracao_Rd(12, "8.8")
Pov = 0.5 * 1.5 * u.t * 24 * u.fu / 1e3                    # arrancamento da alma pela arruela Ø24 (AISI S100-16 J6.2.2, φ 0,5)
Y_COL = 0.060                                              # colunas de furos do ST-1P a ±60 do eixo do apoio
def f_apoio(Rk, Nk):
    Tb = Rk * e_tor / z_par / 2
    Vb = math.hypot(Rk, Nk) / 4
    it = (Tb / min(Ft_M12, Pov)) ** 2 + (Vb / Rb_M12) ** 2
    return dict(R=round(Rk, 2), T_parafuso=round(Tb, 2), V_parafuso=round(Vb, 2), interacao=round(it, 3))
R["terca"] = dict(perfil=Z["nome"], sistema="contínua nos 8 vãos por transpasse sobre os apoios internos (METLAP)",
                  transpasse_cada_lado_m=A_TR, transpasse_total_m=round(2 * A_TR, 2), estudo_transpasse=estudo_tr,
                  L_m=L, vaos_m=VAOS_Y, s_m=s, Lb_corr_mm=round(Lcorr * 1000), MRd_contida=MRc, MRd_correntes=MRb, VRd=round(VRd, 1),
                  governante=res["pior"], por_vao=por_vao, M_apoio_grav=[round(m_, 2) for m_ in Msup], M_apoio_suc=[round(m_, 2) for m_ in Msup_s],
                  R_grav=[round(r_, 2) for r_ in Rgrav], R_suc=[round(r_, 2) for r_ in Rsuc],
                  flecha_mm=res["flecha_mm"], flecha_lim_mm=res["flecha_lim_mm"],
                  parafusos_transpasse=dict(desc="2 M12 8.8 em cada ponta do transpasse (furos E/F da alma, atravessando as 2 almas)",
                                            Fd=round(F_tr, 2), Rd=round(Rb_M12, 1), uso=round(F_tr / Rb_M12, 3)),
                  apoio=None,
                  nota="MEF de viga contínua (Euler-Bernoulli), 2·EI no transpasse; M > 0 (mesa superior comprimida, travada pela telha) "
                       "contra MRd sem FLT; M < 0 (mesa inferior comprimida) contra MRd com Lb entre correntes; no transpasse 2 perfis; "
                       "sobrecarga alternada nos vãos; NBR 14762:2010 9.8 e 9.8.5; flecha L/180 (NBR 8800 Anexo C).")

_Mx = np.array([r_["M"] for r_ in CASOS.values()])
R["terca"]["envoltoria"] = dict(x=[round(float(v_), 3) for v_ in xg[::4]], M_max=[round(float(v_), 2) for v_ in _Mx.max(0)[::4]],
                                M_min=[round(float(v_), 2) for v_ in _Mx.min(0)[::4]], x_apoios=[round(float(v_), 3) for v_ in xa])

# ------------------------------------------------------------------ terça escora (N do modelo global + M do MEF contínuo, linha a linha)
from geometria import X_EIXO
H_COB = 9.9
B_MENOR = X_EIXO["E"]
Y_LOC = min(H_COB, 0.15 * B_MENOR)
VAO_FAIXA_OITAO = ("1-2", "8-9")
COMB_VENTO = {"ELU-1 vento x": "90°", "ELU-2 vento y": "0°"}
Mneg_vao = {zona: [] for zona in cp}
for zona in cp:
    r = CASOS[f"ELU suc {zona}"]
    for i in range(n_v):
        msk = (xg >= xa[i]) & (xg <= xa[i + 1])
        Mneg_vao[zona].append(abs(float(np.min(r["M"][msk]))))
esc_vaos, esc_linhas = [], []
for iv, Lv in enumerate(VAOS_Y):
    nome = f"{iv+1}-{iv+2}"
    Lb_v = Lv / (N_LIN + 1) * 1000
    NR = u.NcRd(Lv * 1000, Lb_v, Lb_v, crit=cN)
    MR = u.MRd(Lb_v, Cb=1.0, crit=cM)
    pior = None
    for comb, ang_v in COMB_VENTO.items():
        for xs_, (nmin, _) in MG["combinacoes"][comb]["por_vao"]["terça-escora por linha"].get(nome, {}).items():
            x_ = float(xs_)
            beiral = x_ <= Y_LOC or x_ >= B_MENOR - Y_LOC
            zona = "borda" if (nome in VAO_FAIXA_OITAO or beiral) else "geral"
            Nd_l = max(0.0, -nmin)
            if abs(x_ - X_EIXO["C"]) < 0.01:
                Nd_l /= 2
            Md_l = Mneg_vao[zona][iv]
            amp_l = 1 / (1 - Nd_l / NR["Nex"])
            it = Nd_l / NR["NcRd"] + Md_l * amp_l / MR["MRd"]
            reg_ = dict(vao=nome, x_m=x_, faixa=" + ".join(f_ for f_, c_ in (("oitão", nome in VAO_FAIXA_OITAO), ("beiral", beiral)) if c_) or "interna",
                        vento=ang_v, cp=cp[zona], L_m=Lv, Nd=round(Nd_l, 1), NcRd=round(NR["NcRd"], 1), modo_N=NR["modo"], Md=round(Md_l, 2),
                        MRd=round(MR["MRd"], 2), amplificacao=round(amp_l, 3), interacao=round(it, 3))
            esc_linhas.append(reg_)
            if pior is None or it > pior["interacao"]:
                pior = reg_
    esc_vaos.append(pior)
gov = max(esc_linhas, key=lambda e: e["interacao"])
Nd = max(e["Nd"] for e in esc_linhas)
bei = [e for e in esc_linhas if "beiral" in e["faixa"]]
gov_bei = max(bei, key=lambda e: e["interacao"])
assert gov["interacao"] <= 1, gov
R["terca_escora"] = dict(Nd=gov["Nd"], NcRd=gov["NcRd"], modo_N=gov["modo_N"], Md=gov["Md"], amplificacao=gov["amplificacao"],
                         MRd=gov["MRd"], interacao=gov["interacao"], ok=gov["interacao"] <= 1.0, vao_governante=gov["vao"],
                         linha_governante_x_m=gov["x_m"], faixa_governante=gov["faixa"], vento_governante=gov["vento"], Nd_max=Nd,
                         faixa_beiral=dict(y_m=round(Y_LOC, 2), Nd_max=max(e["Nd"] for e in bei), governante=gov_bei),
                         por_vao=esc_vaos, fonte="modelo_global_r01.json (ELU-1 e ELU-2) + MEF da terça contínua",
                         nota="N do modelo global e M da sucção do MESMO vento (γ 1,4) tirado do MEF contínuo (maior |M−| do vão); "
                              "NBR 14762:2010 9.9 — Nc,Sd/Nc,Rd + Cm·Mx,Sd/[(1 − Nc,Sd/Nex)·Mx,Rd] ≤ 1, Cm = 1,0 (Lx = vão, a favor da segurança)")

# ------------------------------------------------------------------ correntes (AISI S100-16 D3.2.1 — Z: componente do produto de inércia)
# Z sob carga no plano da alma tende a girar para o lado do eixo principal: força lateral por corrente P = W·Ixy/Ix (+ caimento),
# acumulada nas terças da meia água até as ancoragens (a favor da segurança: sem a restrição da telha).
a_c = L / (N_LIN + 1)
n_run = len(LG["s_tercas"])
k_xy = abs(u.p["Ixy"]) / u.p["Ix"]
casos_c = {}
for nome, wq, incl in (("sucção", (1.4 * abs(cp["geral"]) * q0 - g_fav) * s, 0.0), ("gravidade", (1.35 * g + 1.5 * q) * s, 0.03)):
    W = wq * a_c * 1.1                                       # 1,1: continuidade (reação interna da corrente)
    PL = (k_xy + incl) * W
    casos_c[nome] = dict(W_kN=round(W, 2), PL_por_terca_kN=round(PL, 3), F_acumulada_kN=round(PL * n_run, 2))
Fc = max(v["F_acumulada_kN"] for v in casos_c.values())
D_COR = 10.0
cf = barra_redonda_tracao_Rd(D_COR)
A_L51, rz_L51 = 313.0, 10.0
cr, lam0_cr, esb_cr = compressao_laminado_Rd(A_L51, rz_L51, s * 1000, fy=250)
d_q = math.hypot(s, L / 4); d_m = math.hypot(s, L / 2)
T_q, T_m = Fc * d_q / s, Fc / 2 * d_m / s
T_diag, diag_len = max(T_q, T_m), (d_q if T_q >= T_m else d_m)
td = barra_redonda_tracao_Rd(16.0)
uso_cor = Fc / cf
D_COR_ADOT = 10.0 if uso_cor <= 1 else 12.5
cf = barra_redonda_tracao_Rd(D_COR_ADOT)
R["correntes"] = dict(linhas_por_vao=N_LIN, posicao="a L/4, L/2 e 3L/4, furo Ø12 no meio da alma (151 do fundo)", casos=casos_c,
                      Ixy_sobre_Ix=round(k_xy, 3), F_max_kN=Fc,
                      flexivel=dict(barra=f"Ø{D_COR_ADOT:g} A36, roscas M{D_COR_ADOT:g}, porca + contraporca e arruela dos 2 lados de cada terça", d_mm=D_COR_ADOT, furo="Ø12" if D_COR_ADOT == 10 else "Ø14",
                                    NtRd=round(cf, 1), uso=round(Fc / cf, 3)),
                      rigida=dict(perfil="L 51×51×3,2 (A36), presa em clipe L 32×32×3 com 1 M10 em furo oval 11×23 na alma", L_mm=round(s * 1000), NcRd=round(cr, 1),
                                  esbeltez=round(esb_cr), uso=round(Fc / cr, 3), onde="1º espaço de terças junto a cada ancoragem (beiral e eixo C de cada meia água)"),
                      diagonal=dict(barra="Ø16 A36, rosca M16", comp_L4_m=round(d_q, 2), comp_L2_m=round(d_m, 2), Td_L4=round(T_q, 1), Td_L2=round(T_m, 1),
                                    Td=round(T_diag, 1), NtRd=round(td, 1), uso=round(T_diag / td, 3),
                                    liga="do nó da corrente na 2ª terça (L/4, L/2, 3L/4) ao furo Ø18 do ST-1 da 1ª terça, na viga"))

# ------------------------------------------------------------------ contraventamento em X (padrão das coberturas de referência)
# Treliça no plano da cobertura: cordas = vigas TS-01 das duas linhas do vão; montantes = terças dos nós (escoras, a cada
# 2 espaços de terças); diagonais em X Ø16 A36 de nó a nó (CH-T2 de uma viga à CH-T2 da outra), cada uma com esticador.
T_X_d = max(c["forcas_barras"].get("X Ø16", [0.0, 0.0])[1] for c in ELU.values())      # tração de cálculo na diagonal (modelo R01)
P_X = 2 * s
amostra = LG["contraventamento"]["amostra"][0]
L_X = amostra["comp_m"]
ang = math.radians(amostra["ang_eixo_viga"])
T_X = T_X_d
V_d = T_X * math.sin(ang)                                                          # cortante do painel (componente y)
t16 = barra_redonda_tracao_Rd(16.0)
Fx_no = 2 * T_X * math.cos(ang)                                                    # 2 diagonais no mesmo nó (painéis vizinhos)
Fy_no = 2 * T_X * math.sin(ang)
R["contraventamento"] = dict(painel_x_m=round(P_X, 3), subpaineis=1, L_diag_m=L_X, ang_graus=amostra["ang_eixo_viga"],
                             vaos=["2-3", "7-8"], fonte="modelo_global_r01.json (máx. ELU)", V_painel_d=round(V_d, 1), T_diag_d=round(T_X, 2),
                             NtRd_16=round(t16, 1), uso_diag=round(T_X / t16, 3),
                             no=dict(Fx_kN=round(Fx_no, 2), Fy_kN=round(Fy_no, 2)),
                             barra="Ø16 A36 em 2 trechos (≈ 9,0 m + 1,2 m) unidos por esticador M16 (rosca direita/esquerda), pré-tensão manual",
                             nota="X de nó a nó das vigas, abrangendo 2 espaços de terças, só nos vãos 2-3 e 7-8 (vizinhos aos oitões); terças dos nós trabalham como escoras")

# ------------------------------------------------------------------ suporte ST-1P: chapa dobrada 9,5 mm A36, sem solda, parafusada em
# 2 esperas M16 (A36, gancho) concretadas na mesa superior da TS-01 (±60 do eixo, 120 acima do concreto), furos oblongos 18 × 40.
# Apoio interno: as 2 terças sobrepostas (transpasse) presas pelos MESMOS 2 M12 (atravessam ST-1P + 2 almas). Sem mão-francesa.
ap_int = max((f_apoio(max(Rgrav[j], Rsuc[j]), Nd) for j in range(1, n_v)), key=lambda d_: d_["interacao"])
ap_ext = max((f_apoio(max(Rgrav[j], Rsuc[j]), Nd) for j in (0, n_v)), key=lambda d_: d_["interacao"])
R["terca"]["apoio"] = dict(desc="ST-1P com 4 M12 8.8 na alma (2 colunas a ±60 × furos E 55 / F 52, entre furos 195), sem mão-francesa",
                           e_torcao_mm=Z["bf_sup"] / 2, Ft_Rd=round(Ft_M12, 1), arrancamento_alma_Rd=round(Pov, 1), Vb_Rd=round(Rb_M12, 1),
                           interno=ap_int, extremo=ap_ext, uso=max(ap_int["interacao"], ap_ext["interacao"]),
                           nota="tração T = R·e/z nos 2 parafusos de cima (binário com o apoio da alma no ST-1P) + corte √(R² + N²)/4; (T/TRd)² + (V/VRd)² ≤ 1")
assert R["terca"]["apoio"]["uso"] <= 1 and R["terca"]["parafusos_transpasse"]["uso"] <= 1, R["terca"]
# peças (METLAP): cada terça vence um vão e passa a do apoio interno; nas fachadas (VB, linhas 1 e 9) passa 110 além do eixo
# (2 colunas de furos ±60 + borda 50). Furos do transpasse a 40 da ponta.
EXT_FACH, BORDA_TR = 0.110, 0.040
pecas = []
for i, Lv in enumerate(VAOS_Y):
    e0 = EXT_FACH if i == 0 else A_TR
    e1 = EXT_FACH if i == n_v - 1 else A_TR
    pecas.append(dict(vao=f"{i+1}-{i+2}", L_vao_mm=round(Lv * 1000), ext_ini_mm=round(e0 * 1000), ext_fim_mm=round(e1 * 1000),
                      L_mm=round((Lv + e0 + e1) * 1000)))
R["pecas"] = dict(transpasse_cada_lado_mm=round(A_TR * 1000), transpasse_total_mm=round(2 * A_TR * 1000), extensao_fachada_mm=round(EXT_FACH * 1000),
                  furos_transpasse_da_ponta_mm=round(BORDA_TR * 1000), colunas_apoio_mm=[-60, 60], furos_z_mm=[Z["F"], Z["bw"] - Z["E"]],
                  furo_corrente_z_mm=round(Z["bw"] / 2), por_vao=pecas, L_max_mm=max(p_["L_mm"] for p_ in pecas))
assert R["pecas"]["L_max_mm"] <= 12000
T_st = max(Rsuc[1:n_v])                                    # arrancamento no ST-1P interno (as 2 terças do transpasse)
Vgrav_int = max(Rgrav[1:n_v])
e_al = 75 - 9.5 - 8
M_aba = T_st * 1.25 * e_al / 2 / 1000
MRd_aba = 220 * 9.5 ** 2 / 4 * 250 / 1.10 / 1e6
Ft_esp = 0.75 * math.pi * 16 ** 2 / 4 * 400 / 1.35 / 1e3     # NBR 8800 6.3.3.1 (barra redonda rosqueada A36: fu 400)
Fv_esp = 0.4 * math.pi * 16 ** 2 / 4 * 400 / 1.35 / 1e3
Td_esp, Vd_esp = T_st * 1.25 / 2, Nd / 2
R["ST1P"] = dict(peca="chapa dobrada 9,5 × 220 (aba vertical 290, aba horizontal 150) A36 galvanizada", reacao_suc_kN=round(T_st, 2), reacao_grav_kN=round(Vgrav_int, 2),
                 M12_alma=dict(Fd=ap_int["V_parafuso"], T=ap_int["T_parafuso"], uso=ap_int["interacao"]),
                 aba=dict(Md_kNm=round(M_aba, 3), MRd_kNm=round(MRd_aba, 3), uso=round(M_aba / MRd_aba, 3)),
                 esperas=dict(barra="2 barras roscadas M16 A36 (fu 400) com gancho, hef 150, saliência 120", Td=round(Td_esp, 2), Vd=round(Vd_esp, 2),
                              Ft_Rd=round(Ft_esp, 1), Fv_Rd=round(Fv_esp, 1), interacao=round((Td_esp / Ft_esp) ** 2 + (Vd_esp / Fv_esp) ** 2, 3)),
                 rasgamento_alma=dict(e_mm=45, Fd=round(Nd / 2, 2), Rd=round(u.t * 45 * u.fu / 1.45 / 1e3, 1)))

# ------------------------------------------------------------------ esperas no concreto (ACI 318-19 cap. 17), C50
# ST-1P: 2 M16 com gancho (≈ pino com cabeça de 32 mm), hef 150, s 120 em y; mesa superior 400 (borda lateral 140)
ch = {}
g1 = GrupoPinos(d=16, d_cabeca=32, hef=150, nx=1, ny=2, sx=0, sy=120, cx_neg=2000, cx_pos=2000, cy_neg=140, cy_pos=140, ha=900)
Nu1 = T_st * 1.25
Vx1 = T_diag * s / diag_len           # 1ª terça das ancoragens das correntes: componente na direção da viga
t1, v1 = g1.tracao(), g1.cortante("x+")
ch["ST-1P"] = dict(esperas="2 M16 com gancho, hef 150 (s 120)", Nu=round(Nu1, 1), Vu=round(Vx1, 1), phiNn=round(t1["phiNn_kN"], 1),
                   modoN=t1["modo"], phiVn=round(v1["phiVn_kN"], 1), modoV=v1["modo"],
                   interacao=round(interacao(Nu1, t1["phiNn_kN"], Vx1, v1["phiVn_kN"])[0], 3))
# nó do X (vãos 2-3 e 7-8): ST-1P + 2 OR-X (L 76×76×6,3) cada uma em 1 espera M16 a y = ±140 (borda 60) com grampo U Ø10
g2 = GrupoPinos(d=16, d_cabeca=32, hef=110, nx=1, ny=1, sx=0, sy=0, cx_neg=2000, cx_pos=2000, cy_neg=60, cy_pos=340, ha=900)
gr = grampo_ancoragem_kN(10, pernas=2)
T_or = T_X_d
v2 = g2.cortante("y-", armadura_ancoragem_kN=gr)
Vor = 2 * T_or                          # 2 diagonais do X na mesma orelha (painéis vizinhos), a favor da segurança
ch["OR-X"] = dict(esperas="1 M16 com gancho por orelha, hef 110 + grampo U Ø10", Vu=round(Vor, 1), phiVn=round(v2["phiVn_kN"], 1), modoV=v2["modo"],
                  uso=round(Vor / v2["phiVn_kN"], 3))
R["chumbadores"] = ch

(AQUI / "cobertura_metalica.json").write_text(json.dumps(R, indent=1, ensure_ascii=False, default=float), encoding="utf-8")
if __name__ == "__main__":
    print(json.dumps(R, indent=1, ensure_ascii=False, default=float)[:6000])

