"""Letsara — cobertura metálica: terças Z Metsec contínuas por transpasse (METLAP), correntes, contraventamento em X,
suporte ST-1P e esperas no concreto. Sem mão-francesa (rev05).

Rev. 05 (17/10/2026): terças Z 302×90/82×2,30 (voestalpine Meincol / METSEC, fy 400) contínuas nos 8 vãos por transpasse
sobre cada viga; esforços por MEF de viga contínua (nd_estruturas.viga_continua) com 2·EI no trecho do transpasse;
comprimento do transpasse escolhido como o menor que atende; parafusos do transpasse e do apoio (2 M12 8.8 na alma, sem
mão-francesa). Rev. 05b (17/10/2026, DEC-024): N das escoras, forças do X, das correntes, dos apoios ST-1P/ST-1V e das
ligações dos pilares dos portões lidos do MODELO INTEGRADO r05 (toda a estrutura num modelo: pilares, TS-01, I130, VB,
mezanino rígido, terças contínuas, correntes, tirantes, diagonais e X; 33 combinações ELU, NBR 6123 completa);
X nos vãos 4-5 a 8-9, painel de 8 terças, Ø16.
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
_MI = AQUI / "modelo_integrado_r05.json"
MI = json.loads(_MI.read_text(encoding="utf-8"))["envoltoria"] if _MI.exists() else None     # modelo integrado (envoltória ELU)

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

# ------------------------------------------------------------------ terça escora: resistências por vão (NBR 14762:2010 9.7 e 9.8)
# A interação N + M de cada elemento de terça (N, My e Mz da mesma combinação) é feita DENTRO do modelo integrado r05, com
# estas resistências; aqui ficam NcRd e MRd por vão e o resultado governante lido do modelo.
esc_vaos = []
for iv, Lv in enumerate(VAOS_Y):
    Lb_v = Lv / (N_LIN + 1) * 1000
    NR = u.NcRd(Lv * 1000, Lb_v, Lb_v, crit=cN)
    MR = u.MRd(Lb_v, Cb=1.0, crit=cM)
    esc_vaos.append(dict(vao=f"{iv+1}-{iv+2}", L_m=Lv, NcRd=round(NR["NcRd"], 1), Nex=round(NR["Nex"], 1), modo_N=NR["modo"], MRd=round(MR["MRd"], 2)))
if MI:
    gov = MI["terca"]
    te_v = next(e for e in esc_vaos if e["vao"] == gov["vao"])
    R["terca_escora"] = dict(Nd=gov["N"], NcRd=te_v["NcRd"], modo_N=te_v["modo_N"], Md=abs(gov["My"]), Mz=gov["Mz"], MRd=te_v["MRd"],
                             interacao=gov["it"], ok=gov["it"] <= 1.0, vao_governante=gov["vao"], linha_governante_x_m=gov["x"],
                             transpasse=gov["transpasse"], Nd_max=gov["N"], por_vao=esc_vaos, fonte="modelo_integrado_r05.json (33 combinações ELU)",
                             nota="Interação em cada elemento de terça do modelo integrado, com N, My e Mz da mesma combinação: "
                                  "Nc/NcRd + |My|·[1/(1 − Nc/Nex)]/MRd + |Mz|/MRz ≤ 1 (NBR 14762:2010 9.9), 2 perfis no transpasse.")
    assert gov["it"] <= 1.0, gov
else:
    R["terca_escora"] = dict(por_vao=esc_vaos, fonte="sem modelo integrado (rodar modelo_integrado_r05.py e repetir este cálculo)")
Nd = R["terca_escora"].get("Nd_max", 0.0)

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
                      modelo_integrado=(dict(corrente_T_max=MI["corrente"]["max"], uso_corrente=MI["usos"]["corrente"], diagonal_T_max=MI["diagonal de ancoragem"]["max"],
                                             uso_diagonal=MI["usos"]["diagonal"], tirante_C_max=-MI["tirante rígido"]["min"], uso_tirante=MI["usos"]["tirante"]) if MI else None),
                      diagonal=dict(barra="Ø16 A36, rosca M16", comp_L4_m=round(d_q, 2), comp_L2_m=round(d_m, 2), Td_L4=round(T_q, 1), Td_L2=round(T_m, 1),
                                    Td=round(T_diag, 1), NtRd=round(td, 1), uso=round(T_diag / td, 3),
                                    liga="do nó da corrente na 2ª terça (L/4, L/2, 3L/4) ao furo Ø18 do ST-1 da 1ª terça, na viga"))

# ------------------------------------------------------------------ contraventamento em X — rev05 (DEC-024)
# X nos 5 vãos do pavilhão (4-5 a 8-9), painel de 8 espaços de terças (nós nas terças 0, 8 e 16 de cada meia água), diagonal
# ≈ 45°, Ø16 A36 de orelha a orelha (OR-X nas ES-2 da TS-01; no eixo 9, na VB) atravessando as terças intermediárias por furos
# oblongos. Tração de cálculo: máximo do modelo integrado (barras só à tração).
CXT = LG["contraventamento"]["tirantes"]
T_X = MI["X"]["max"] if MI else 0.0
t16 = barra_redonda_tracao_Rd(16.0)
L_X = max(t_["comp_m"] for t_ in CXT)
ang_X = sum(t_["ang_eixo_viga"] for t_ in CXT) / len(CXT)
ang = math.radians(ang_X)
V_d = T_X * math.sin(ang)
R["contraventamento"] = dict(painel_x_m=round(LG["painel_x"] * s, 3), espacos_terca=LG["painel_x"], subpaineis=1, L_diag_m=L_X, ang_graus=round(ang_X, 1),
                             vaos=[f"{k+1}-{k+2}" for k in LG["vaos_x"]], n_diagonais=len(CXT), fonte="modelo_integrado_r05.json (máx. ELU)",
                             V_painel_d=round(V_d, 1), T_diag_d=round(T_X, 2), NtRd_16=round(t16, 1), uso_diag=round(T_X / t16, 3),
                             no=dict(Fx_kN=round(2 * T_X * math.cos(ang), 2), Fy_kN=round(2 * T_X * math.sin(ang), 2)),
                             barra=f"Ø16 A36 em 2 trechos unidos por esticador M16 (rosca direita/esquerda), L ≈ {L_X:.1f} m de orelha a orelha",
                             furos_tercas="oblongos 18 × 28 (eixo maior ao longo da terça) a 35 ('/') e 75 ('\\') do fundo da terça",
                             nota="X de nó a nó das vigas a cada 8 espaços de terças (≈ 9,6 × 10 m), nos vãos 4-5 a 8-9; terças dos nós = escoras")
assert T_X <= t16

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
GR = (MI or {}).get("ST1P_grupos", {})
R["ST1P"] = dict(peca="chapa dobrada 9,5 × 220 (aba vertical 290, aba horizontal 150) A36 galvanizada", reacao_suc_kN=round(T_st, 2), reacao_grav_kN=round(Vgrav_int, 2),
                 M12_alma=dict(Fd=ap_int["V_parafuso"], T=ap_int["T_parafuso"], uso=ap_int["interacao"]),
                 aba=dict(Md_kNm=round(M_aba, 3), MRd_kNm=round(MRd_aba, 3), uso=round(M_aba / MRd_aba, 3)),
                 esperas=dict(barra="2 barras roscadas M16 A36 (fu 400) com gancho, hef 150, saliência 120", Td=round(Td_esp, 2), Vd=round(Vd_esp, 2),
                              Ft_Rd=round(Ft_esp, 1), Fv_Rd=round(Fv_esp, 1), interacao=round((Td_esp / Ft_esp) ** 2 + (Vd_esp / Fv_esp) ** 2, 3)),
                 rasgamento_alma=dict(e_mm=45, Fd=round(Nd / 2, 2), Rd=round(u.t * 45 * u.fu / 1.45 / 1e3, 1)),
                 modelo_integrado={k_: v_ for k_, v_ in GR.items()},
                 nota="Cada apoio verificado no modelo integrado com as forças do próprio cleat (Rz, Fy ao longo da terça, Fx): "
                      "4 M12 na alma (T = R·e/z, V = √(R² + Fy² + Fx²)/4) e esperas (T = 1,25·Rz↑/n, V = √(Fy² + Fx²)/n).")
if "ST-1P" in GR:
    assert GR["ST-1P"]["it"] <= 1.0, GR["ST-1P"]

# ------------------------------------------------------------------ ST-1V-R — apoio das terças na VB 15×60 do eixo 9 (oitão), rev05 (DEC-024)
# O vento do oitão entra na cobertura pelas terças (escoras): até ≈ 53 kN ao longo da terça no ST-1V da linha 9 (modelo
# integrado, rev05 sem reforço: esperas M16 com uso 1,23 a 1,29), concentrado nas terças junto aos pilares da fachada.
# Reforço sem mudar a geometria do ST-1V: 2 esperas M20 A36 longas (hef 400, descem até a armadura inferior da VB) no lugar
# das M16 de hef 150 — a VB tem só 15 cm, então o cone e o pryout dependem da profundidade —, cada uma com grampo U Ø10
# (armadura de ancoragem para a ruptura de borda, ACI 318-19 17.5.2.1). Mesmas posições (eixo da VB, 45 e 105 da alma);
# oblongos 22 × 44 na aba.
g9 = GR.get("ST-1V-R eixo 9", dict(Fy_max=0.0, Fx_max=0.0, Rz_up=0.0))
Fy9, Fx9, Up9 = g9["Fy_max"], g9["Fx_max"], g9["Rz_up"]
A20 = math.pi * 20 ** 2 / 4
Ft20, Fv20 = 0.75 * A20 * 400 / 1.35 / 1e3, 0.4 * A20 * 400 / 1.35 / 1e3        # NBR 8800 6.3.3.1 / 6.3.3.2 (A36, fu 400)
Te9, Ve9 = Up9 * 1.25 / 2, math.hypot(Fy9, Fx9) / 2
gr10 = grampo_ancoragem_kN(10, pernas=2)
g9c = GrupoPinos(d=20, d_cabeca=40, hef=400, nx=2, ny=1, sx=60, sy=0, cx_neg=2000, cx_pos=2000, cy_neg=75, cy_pos=75, ha=600, fc=40.0)
t9, v9 = g9c.tracao(), g9c.cortante("y-", armadura_ancoragem_kN=2 * gr10)
v9s = g9c.cortante("y-")
R["ST1V_R"] = dict(onde="VB do eixo 9 (34 apoios)", peca="ST-1V (chapa dobrada 9,5 × 220 × 290) com oblongos 22 × 44 na aba horizontal",
                   esperas="2 barras roscadas M20 A36 L = 520 + gancho (hef 400), no eixo da VB a 45 e 105 da alma, amarradas aos estribos + grampo U Ø10 em cada espera",
                   Fy_d=Fy9, Fx_d=Fx9, Rz_up_d=Up9, aco=dict(Td=round(Te9, 2), Vd=round(Ve9, 2), Ft_Rd=round(Ft20, 1), Fv_Rd=round(Fv20, 1),
                   interacao=round((Te9 / Ft20) ** 2 + (Ve9 / Fv20) ** 2, 3)),
                   concreto=dict(phiNn=round(t9["phiNn_kN"], 1), modoN=t9["modo"], phiVn_sem_grampo=round(v9s["phiVn_kN"], 1), modo_sem_grampo=v9s["modo"],
                                 grampos_kN=round(2 * gr10, 1), phiVn=round(v9["phiVn_kN"], 1), modoV=v9["modo"],
                                 interacao=round(interacao(Up9 * 1.25, t9["phiNn_kN"], math.hypot(Fy9, Fx9), v9["phiVn_kN"])[0], 3)))
assert R["ST1V_R"]["aco"]["interacao"] <= 1 and R["ST1V_R"]["concreto"]["interacao"] <= 1, R["ST1V_R"]
g1v = GR.get("ST-1V eixo 1", dict(Fy_max=0.0, Fx_max=0.0, Rz_up=0.0))
g1c = GrupoPinos(d=16, d_cabeca=32, hef=150, nx=2, ny=1, sx=60, sy=0, cx_neg=2000, cx_pos=2000, cy_neg=75, cy_pos=75, ha=600, fc=40.0)
t1v, v1v = g1c.tracao(), g1c.cortante("y-")
R["ST1V_eixo1"] = dict(Fy_d=g1v["Fy_max"], Rz_up_d=g1v["Rz_up"], phiNn=round(t1v["phiNn_kN"], 1), phiVn=round(v1v["phiVn_kN"], 1), modoV=v1v["modo"],
                       interacao=round(interacao(g1v["Rz_up"] * 1.25, t1v["phiNn_kN"], math.hypot(g1v["Fy_max"], g1v["Fx_max"]), v1v["phiVn_kN"])[0], 3))
assert R["ST1V_eixo1"]["interacao"] <= 1, R["ST1V_eixo1"]

# ------------------------------------------------------------------ esperas no concreto (ACI 318-19 cap. 17), C50
# ST-1P: 2 M16 com gancho (≈ pino com cabeça de 32 mm), hef 150, s 120 em y; mesa superior 400 (borda lateral 140)
ch = {}
g1 = GrupoPinos(d=16, d_cabeca=32, hef=150, nx=1, ny=2, sx=0, sy=120, cx_neg=2000, cx_pos=2000, cy_neg=140, cy_pos=140, ha=900)
# rev05 (DEC-024): a escora da terça (Fy, ao longo da terça = largura da TS-01) chega a ≈ 44 kN nos beirais; a força vai para
# a borda lateral da mesa (140 mm): grampo U Ø10 em cada ES-1 (armadura de ancoragem, ACI 17.5.2.1).
gp = GR.get("ST-1P", {})
gr = grampo_ancoragem_kN(10, pernas=2)
Nu1 = max(T_st, gp.get("Rz_up", 0.0)) * 1.25
Vy1 = gp.get("Fy_max", 0.0)                                   # ao longo da terça (modelo integrado)
Vx1 = max(T_diag * s / diag_len, gp.get("Fx_max", 0.0))       # ao longo da viga (diagonais de ancoragem / modelo)
t1, v1x = g1.tracao(), g1.cortante("x+")
v1y_s, v1y = g1.cortante("y+"), g1.cortante("y+", armadura_ancoragem_kN=2 * gr)
ch["ST-1P"] = dict(esperas="2 M16 com gancho, hef 150 (s 120) + 1 grampo U Ø10 em cada espera", Nu=round(Nu1, 1), Vu_terca=round(Vy1, 1), Vu_viga=round(Vx1, 1),
                   phiNn=round(t1["phiNn_kN"], 1), modoN=t1["modo"], phiVn_terca_sem_grampo=round(v1y_s["phiVn_kN"], 1),
                   phiVn_terca=round(v1y["phiVn_kN"], 1), modoV_terca=v1y["modo"], phiVn_viga=round(v1x["phiVn_kN"], 1), modoV_viga=v1x["modo"],
                   interacao=round(max(interacao(Nu1, t1["phiNn_kN"], Vy1, v1y["phiVn_kN"])[0], interacao(Nu1, t1["phiNn_kN"], Vx1, v1x["phiVn_kN"])[0]), 3))
assert ch["ST-1P"]["interacao"] <= 1, ch["ST-1P"]
# nó do X: cada diagonal na sua orelha OR-X (L 102×76×6,3) com 1 espera M16 (ES-2) a y = ±140 (borda 60) + grampo U Ø10
g2 = GrupoPinos(d=16, d_cabeca=32, hef=110, nx=1, ny=1, sx=0, sy=0, cx_neg=2000, cx_pos=2000, cy_neg=60, cy_pos=340, ha=900)
v2 = g2.cortante("y-", armadura_ancoragem_kN=gr)
Vor = T_X                               # 1 diagonal por orelha (rev05)
ch["OR-X"] = dict(esperas="1 M16 com gancho por orelha, hef 110 + grampo U Ø10", Vu=round(Vor, 1), phiVn=round(v2["phiVn_kN"], 1), modoV=v2["modo"],
                  uso=round(Vor / v2["phiVn_kN"], 3))
# OR-X na VB do eixo 9: orelha no eixo da VB (bordas 75), 1 espera M16 hef 110 + grampo U Ø10; força da diagonal com componente
# ⊥ à VB = T·sen(ang)
g3 = GrupoPinos(d=16, d_cabeca=32, hef=110, nx=1, ny=1, sx=0, sy=0, cx_neg=2000, cx_pos=2000, cy_neg=75, cy_pos=75, ha=600, fc=40.0)
v3 = g3.cortante("y-", armadura_ancoragem_kN=gr)
ch["OR-X VB"] = dict(esperas="1 M16 com gancho por orelha, hef 110 + grampo U Ø10 (VB 15×60, eixo 9)", Vu=round(Vor, 1), phiVn=round(v3["phiVn_kN"], 1),
                     modoV=v3["modo"], uso=round(Vor / v3["phiVn_kN"], 3))
assert ch["OR-X"]["uso"] <= 1 and ch["OR-X VB"]["uso"] <= 1
R["chumbadores"] = ch

# ------------------------------------------------------------------ ligação da cabeça dos pilares dos portões (linha 4) à TS-01 — rev05 (DEC-024)
# Cabeça do pilar a 2 cm do fundo da TS-01; em cada face x do pilar, 1 cantoneira L 102×102×9,5 (L = 250, ao longo de y):
# aba horizontal sob a TS-01 com 2 M16 8.8 em insertos rosqueados do fundo da viga (y = ±97,5 do eixo, entre as colunas de
# cordoalhas, hef 80) e aba vertical na face do pilar com 1 M16 8.8 em inserto (hef 100) por furo oblongo vertical 18 × 50
# (a TS-01 flete e o pilar não carrega a viga). Força só em y (vento entre o pavilhão e a área aberta), em corte nos parafusos.
FP = (MI or {}).get("portoes", {})
F_pt = max(FP.values()) if FP else 0.0
Vb16 = parafuso_corte_Rd(16, "8.8")
pino_ts = GrupoPinos(d=16, d_cabeca=30, hef=80, nx=1, ny=2, sx=0, sy=195, cx_neg=2000, cx_pos=2000, cy_neg=102, cy_pos=102, ha=150)
pino_pl = GrupoPinos(d=16, d_cabeca=30, hef=100, nx=1, ny=1, sx=0, sy=0, cx_neg=75, cx_pos=2000, cy_neg=125, cy_pos=125, ha=250, fc=40.0)
vts, vpl = pino_ts.cortante("y+"), pino_pl.cortante("y+")
F_cant = F_pt / 2                                                     # 2 cantoneiras por pilar
M_cant = F_cant * 0.060                                               # excentricidade aba/parafuso ≈ 60 mm
MRd_cant = 250 * 9.5 ** 2 / 4 * 250 / 1.10 / 1e6
R["ligacao_portoes"] = dict(forcas_kN=FP, Fd_max=round(F_pt, 2), peca="2 cantoneiras L 102×102×9,5 L = 250 por pilar (faces x), A36 galvanizadas",
                            parafusos=dict(Fd_TS=round(F_cant / 2, 2), Fd_pilar=round(F_cant, 2), Rd_M16_88=round(Vb16, 1), uso=round(F_cant / Vb16, 3)),
                            insertos_TS=dict(phiVn=round(vts["phiVn_kN"], 1), modo=vts["modo"], Vu=round(F_cant, 2), uso=round(F_cant / vts["phiVn_kN"], 3)),
                            inserto_pilar=dict(phiVn=round(vpl["phiVn_kN"], 1), modo=vpl["modo"], Vu=round(F_cant, 2), uso=round(F_cant / vpl["phiVn_kN"], 3)),
                            cantoneira=dict(Md=round(M_cant, 3), MRd=round(MRd_cant, 3), uso=round(M_cant / MRd_cant, 3)),
                            cabeca_pilares_m={"P9": 7.47, "P10a": 7.63, "P10b": 7.90, "P12": 8.06})
assert all(R["ligacao_portoes"][k_]["uso"] <= 1 for k_ in ("parafusos", "insertos_TS", "inserto_pilar", "cantoneira")), R["ligacao_portoes"]

(AQUI / "cobertura_metalica.json").write_text(json.dumps(R, indent=1, ensure_ascii=False, default=float), encoding="utf-8")
if __name__ == "__main__":
    print(json.dumps(R, indent=1, ensure_ascii=False, default=float)[:6000])

