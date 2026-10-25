"""Letsara rev04 — verificações da NBR 9062:2017 em toda a obra (memória MC05). Lê os JSON dos cálculos e grava nbr9062.json.

Seções:
  0 classificação e coeficientes (3.8/3.9, 8.1, 7.3.1.1)
  1 estabilidade global (5.1.2, 5.2.3, Tab. 7) — modelo_global_r04(.json, _placas.json)
  2 aparelhos de apoio de elastômero (7.2.1.6)
  3 consolos (7.3) e cintamento do topo dos pilares (6.2.3)
  4 apoios sem recorte (7.5) e dente Gerber da I130 (7.4)
  5 cálices (7.7, Tab. 15)
  6 situações transitórias (5.3.2, 6.1, 5.3.3, 6.2.4) e flechas (5.4.3.4)
  7 folgas e tolerâncias (3.1, 5.2.2)
  8 incêndio e cobrimentos (5.3.1.5, 9.2.1.1)
Unidades: kN, m; MPa nas tensões.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

AQ = Path(__file__).parent
sys.path.insert(0, str(AQ.parents[1]))
sys.path.insert(0, "/home/claude/letsara/pranchas")
from nd_estruturas.prefabricados import Concreto, secao_I

J = lambda n: json.loads((AQ / n).read_text(encoding="utf-8"))
MG, MGP, VM, I1J, DT, LG = J("modelo_global_r04.json"), J("modelo_global_r04_placas.json"), J("vm_retangular.json"), J("i110_r01.json"), J("dentes.json"), J("ligacoes.json")
import ts01_dados as TS

FYD = 500 / 1.15                     # MPa
OUT = {}

# ================================================================== 0 classificação
OUT["classificacao"] = dict(
    tipo="pré-moldado (NBR 9062:2017 3.8, controle 12.1.1) até a fábrica comprovar 12.1.2",
    gama_c=1.4, gama_s=1.15, gama_n_permanente=1.1, gama_n_outros=1.2,
    obs="Com certificação de pré-fabricado (12.1.2: laboratório próprio, Sd ≤ 3,5 MPa, cura controlada) caem para γc 1,3, γs 1,10 e γn 1,0/1,1 "
        "e o cobrimento pode reduzir 5 mm (9.2.1.1). Os cálculos desta revisão usam os valores de pré-moldado (a favor da segurança).")

# ================================================================== 1 estabilidade global
def resumo_mg(m):
    c = m["combinacoes"]
    return dict(gama_z={k: v["gama_z_9062"] for k, v in c.items() if v["tipo"] == "ELU"},
                ELS={k: dict(desl_max_mm=v["desl_max_mm"], uso_tab7=v["uso_desl_max"], pilar=v["pilar_uso_max"], uso_Hi750=v["uso_Hi750_max"], ok=v["ok_ELS"])
                     for k, v in c.items() if v["tipo"] == "ELS"},
                uso_ELU_pilares=max(v["uso"] for v in m["verificacao_pilares"].values()),
                metodo_geral=m["metodo_geral"])
mg = resumo_mg(MG)
mgp = resumo_mg(MGP)
OUT["estabilidade"] = dict(
    sistema="5.1.2.1 a) pilares engastados nos cálices + d) cobertura (TS-01 articuladas, terças-escora e X Ø16 nos vãos 2-3 e 7-8) "
            "e diafragma do mezanino. Sem vigas de travamento: não há ponte rolante nem carga especificada que as peça.",
    ligacoes="vigas articuladas (αR < 0,15: pino grauteado + elastômero) — 5.1.2.3; rotações acomodadas pelos aparelhos (item 2 desta memória)",
    rigidez="ELU: pilares 0,4·Eci·Ic (Anexo A, galpão articulado), vigas como barras articuladas; ELS: Ecs·Ic (5.4.2)",
    desaprumo="H/400 nas duas direções (5.2.3) somado ao vento nas combinações ELU",
    sem_VT=mg, com_placas_ligadas=mgp,
    contribuicao_fechamento=dict(
        desl_ELS_x_mm=(mg["ELS"]["ELS-F vento x"]["desl_max_mm"], mgp["ELS"]["ELS-F vento x"]["desl_max_mm"]),
        desl_ELS_y_mm=(mg["ELS"]["ELS-F vento y"]["desl_max_mm"], mgp["ELS"]["ELS-F vento y"]["desl_max_mm"]),
        conclusao="As placas ligadas (fiada superior com furo redondo) quase não mudam os deslocamentos: no vento transversal (x) as paredes laterais "
                  "trabalham fora do plano e as fachadas só ajudam os pórticos de ponta; no vento longitudinal (y) a cobertura já liga todas as "
                  "cabeças de pilar. Fica o fechamento isostático (CL-1 com furo oblongo), que não atrai esforço de variação volumétrica."),
    deslocabilidade="γz ≤ 1,10 em todas as combinações → 2ª ordem global desprezável (5.1.2.12); efeitos locais pelo método geral (λu)")

# ================================================================== 2 aparelhos de elastômero (7.2.1.6)
G = 1.0                              # MPa, dureza Shore A 60 a 20 °C (7.2.1.6)


def neo_simples(nome, a, b, h, Ng, Nq, ah, thg, thq, uso):
    """a = dimensão na direção do vão (mm), b transversal, h espessura (mm); N em kN; ah em mm; θ em rad."""
    A = a * b                                                       # mm²
    sig = (Ng + Nq) * 1e3 / A
    Al = (a - ah) * b
    S = a * b / (2 * (a + b) * h)
    sg = Ng * 1e3 / Al
    sgq = (Ng + Nq) * 1e3 / Al
    h1 = h * sg / (10 * G * S + 2 * sg)
    h2 = h * sgq / (10 * G * S + 2 * sgq)
    Hk = G * A * ah / h / 1e3                                       # kN — força da distorção imposta
    mu_g, mu_gq = 0.1 + 0.6 / sg, 0.1 + 0.6 / sgq
    desl = max(Hk / (mu_g * Ng), Hk / (mu_gq * (Ng + Nq)))
    ok = dict(pressao=sig <= 7.0, distorcao=ah <= 0.5 * h, Nmin=sg >= 1 + a / b, deslizamento=desl <= 0.85,
              levantamento_g=math.tan(thg) < 2 * h1 / a, levantamento_gq=math.tan(thg) + 1.5 * math.tan(thq) < 2 * h2 / a, estabilidade=h < a / 5)
    return dict(aparelho=nome, uso=uso, tipo="simples", a_mm=a, b_mm=b, h_mm=h, Ng_kN=round(Ng, 1), Nq_kN=round(Nq, 1), sigma_MPa=round(sig, 2), lim_sigma=7.0,
                ah_mm=round(ah, 1), lim_ah_mm=0.5 * h, sigma_g_Al=round(sg, 2), lim_Nmin=round(1 + a / b, 2), Hk_kN=round(Hk, 1), uso_deslizamento=round(desl, 2),
                theta_g=round(thg, 4), theta_q=round(thq, 4), lim_theta_g=round(2 * h1 / a, 4), lim_theta_gq=round(2 * h2 / a, 4), S=round(S, 2),
                ok=ok, ok_geral=all(ok.values()), norma="NBR 9062:2017 7.2.1.6.18 a 7.2.1.6.23")


def neo_fretado(nome, a, b, hi, n_int, hs, Ng, Nq, ah, thg, thq, uso):
    """a, b externos (mm); camadas internas hi (n_int) e externas hs (2); chapas internas com cobrimento lateral 4 mm (Fig. 11)."""
    ap, bp = a - 8, b - 8
    Shi = sum([hi] * n_int + [hs, hs])
    A = a * b
    sig = (Ng + Nq) * 1e3 / A
    lim_sig = 8.0 if a <= 150 else 11.0 if a <= 200 else 12.5 if a <= 300 else 15.0
    Si = ap * bp / (2 * (ap + bp) * hi)
    sg = Ng * 1e3 / ((ap - ah) * bp)
    sgq = (Ng + Nq) * 1e3 / ((ap - ah) * bp)
    h1 = sum(x * sg / (4 * G * (ap * bp / (2 * (ap + bp) * x)) ** 2 + 3 * sg) for x in [hi] * n_int + [hs, hs])
    h2 = sum(x * sgq / (4 * G * (ap * bp / (2 * (ap + bp) * x)) ** 2 + 3 * sgq) for x in [hi] * n_int + [hs, hs])
    tau_n = 1.5 / Si * (Ng + 1.5 * Nq) * 1e3 / A
    tau_h = G * ah / Shi
    tau_t = G * a ** 2 / (2 * hi * Shi) * (math.tan(thg) + 1.5 * math.tan(thq))
    Al = (a - ah) * b
    ok = dict(pressao=sig <= lim_sig, distorcao=ah <= 0.5 * Shi, Nmin=Ng * 1e3 / Al > 2.0, levantamento_g=math.tan(thg) < 6 * h1 / ap,
              levantamento_gq=math.tan(thg) + 1.5 * math.tan(thq) < 6 * h2 / ap, cisalhamento=tau_n + tau_h + tau_t <= 5 * G, estabilidade=Shi < a / 5)
    return dict(aparelho=nome, uso=uso, tipo=f"fretado ({n_int} camadas de {hi} + 2 de {hs} mm, chapas inox 2 mm)", a_mm=a, b_mm=b, h_mm=Shi + 2 * (n_int + 1),
                Ng_kN=round(Ng, 1), Nq_kN=round(Nq, 1), sigma_MPa=round(sig, 2), lim_sigma=lim_sig, ah_mm=round(ah, 1), Nmin_MPa=round(Ng * 1e3 / Al, 2),
                tau_total_MPa=round(tau_n + tau_h + tau_t, 2), lim_tau=5 * G, theta_g=round(thg, 4), theta_q=round(thq, 4),
                lim_theta_g=round(6 * h1 / ap, 4), lim_theta_gq=round(6 * h2 / ap, 4), Si=round(Si, 2),
                ok=ok, ok_geral=all(ok.values()), norma="NBR 9062:2017 7.2.1.6.13 a 7.2.1.6.26")


def theta(w, L, EI):
    return w * L ** 3 / (24 * EI)


PHI = 2.0
# --- TS-01 (C50, I 0,02071, L 19,48)
C50, C40 = Concreto(50), Concreto(40)
EI_ts = C50.Ecs * TS.sec.I
Pts, ets = TS.R.linhas["Pinf_kN"], TS.ep
g_ts = TS.car.g1 + TS.car.g2
th_ts = abs(theta(g_ts, TS.L_calc, EI_ts) - Pts * ets * TS.L_calc / (2 * EI_ts)) * (1 + PHI)
thq_ts = theta(TS.car.q, TS.L_calc, EI_ts)
Ng_ts, Nq_ts = g_ts * TS.L_calc / 2, TS.car.q * TS.L_calc / 2
ah_ts = 40e-5 * TS.L / 1000 / 2 * 1000                              # mm — ε 40·10⁻⁵ (retração 20, fluência 5, ΔT ±15 °C) / 2 pontas
# --- I130 (V406, a maior)
v = I1J["V406"]
sI = secao_I(1.30, bs=0.40, ts=0.22, ms=0.08, bw=0.15, bi=0.40, ti=0.25, mi=0.08)
EI_i = C40.Ecs * sI.I
gI = v["linhas"]["peso_kN_m"] + v["g2_equiv"]
th_i = abs(theta(gI, v["L_calc"], EI_i) - v["linhas"]["Pinf_kN"] * (sI.yc - 0.1231) * v["L_calc"] / (2 * EI_i)) * (1 + PHI)
thq_i = theta(v["q_equiv"], v["L_calc"], EI_i)
Ng_i = v["linhas"]["peso_kN_m"] * v["L_calc"] / 2 + v["cargas_concentradas_kN"]["g"]
Nq_i = v["cargas_concentradas_kN"]["q"]
ah_i = 40e-5 * v["L_peca"] / 2 * 1000
# --- VM retangular 30 × 75 (VM-02) — rev09 DEC-049
m = VM["VM-02"]
EI_vm1, EI_vm2 = C40.Ecs * m["secao"]["I"], C40.Ecs * m["secao"]["I_comp"]
Lv = m["L_calculo"]
th_vm = abs(theta(m["cargas"]["g1"], Lv, EI_vm1) + theta(m["cargas"]["g2"], Lv, EI_vm2) - m["protensao"]["Pinf"] * m["protensao"]["ep"] * Lv / (2 * EI_vm1)) * (1 + PHI)
thq_vm = theta(m["cargas"]["q2"], Lv, EI_vm2)
Ng_vm = m["cargas"]["g1"] * Lv / 2 + 1.25 * m["cargas"]["g2"] * Lv / 2
Nq_vm = 1.25 * m["cargas"]["q2"] * Lv / 2
ah_vm = 35e-5 * m["L_peca"] / 2 * 1000
# --- VB 15 × 60 com dente 30 (rev04, concreto armado, vão 9,43 m) — calc_vb_dente.py
VBD = J("vb_dente.json")["adotado"]
EI_vb = 0.5 * C40.Ecs * 0.15 * 0.60 ** 3 / 12                       # estádio II aproximado (0,5 EI)
th_vb = theta(VBD["g"], 9.43, EI_vb) * (1 + PHI)
thq_vb = theta(VBD["q"], 9.43, EI_vb)
Ng_vb, Nq_vb = VBD["g"] * 9.43 / 2, VBD["q"] * 9.43 / 2

NEO = [
    neo_simples("NEO-4 200×300×10 (simples)", 200, 300, 10, Ng_ts, Nq_ts, ah_ts, th_ts, thq_ts, "TS-01 no recuo dos pilares laterais P1/P2"),
    neo_simples("NEO-4 150×300×10 (simples)", 150, 300, 10, Ng_ts, Nq_ts, ah_ts, th_ts, thq_ts, "TS-01 no recuo — alternativa rev04"),
    neo_simples("NEO-3 100×300×10 (simples)", 100, 300, 10, Ng_ts, Nq_ts, ah_ts, th_ts, thq_ts, "TS-01 no topo do P11 (pilar central da linha 4)"),
    neo_simples("NEO-3C 150×300×10 (simples, rev10)", 150, 300, 10, Ng_ts, Nq_ts, ah_ts, th_ts, thq_ts, "TS-01 no topo da I130 + consolo lateral CT-I130 (rev10, DEC-059)"),
    neo_fretado("NEO-2 300×250 fretado (rev03)", 250, 300, 10, 2, 2.5, Ng_i, Nq_i, ah_i, th_i, thq_i, "I130 nos consolos CP-I130"),
    neo_fretado("NEO-2 200×300 fretado (rev04)", 200, 300, 10, 2, 2.5, Ng_i, Nq_i, ah_i, th_i, thq_i, "I130 nos consolos CP-I130 — rev04 (a2 do consolo)"),
    neo_fretado("NEO-5F 200×200 fretado (rev09)", 200, 200, 10, 2, 2.5, Ng_vm, Nq_vm, ah_vm, th_vm, thq_vm, "VM retangular 30 × 75 (dente 45 × 40) nos consolos CP-MEZ 40"),
    neo_simples("NEO-6 100×100×10 (rev04)", 100, 100, 10, Ng_vb, Nq_vb, 1.4, th_vb, thq_vb, "VB 15×60 (dente 30) nos consolos CP-VB — rev04"),
]
OUT["aparelhos"] = NEO

# ================================================================== 3 consolos (7.3)
BAR = {10: 0.785, 12.5: 1.227, 16: 2.011, 20: 3.142}


def consolo(nome, onde, b, proj, h, a, a_pad, b_pad, Vd, gn, fck=40, c=2.5, h_ext=None, c_tir=0.05):
    """b largura, proj projeção, h altura (m) junto à face do pilar; a = face do pilar ao centro do aparelho; a_pad/b_pad dimensões do aparelho (m).
    Vd já majorado (γf); gn = γn (7.3.1.1). Tirante em alças horizontais (Fig. 17).
    h_ext: altura na extremidade (consolo com mísula de fundo inclinado); None = consolo reto."""
    h_ext = h if h_ext is None else h_ext
    fcd = fck / 1.4
    Fd = gn * Vd
    Hd = 0.16 * Fd                                                   # 7.3.9 — elastômero
    d = h - c_tir                                                    # c_tir: topo ao eixo do tirante
    ad = a / d
    modelo = "viga em balanço" if ad > 1 else "consolo curto" if ad > 0.5 else "consolo muito curto"
    if ad <= 0.5:
        Asv = 0.8 * Fd / (FYD * 1.4) * 10                             # 7.3.5.3 — μ = 1,4 (monolítico)
    else:
        Asv = (0.1 + ad) * Fd / FYD * 10                              # 7.3.5.2
    As = Asv + Hd / FYD * 10
    As_min = 0.04 * fck / 500 * b * d * 1e4                           # ω > 0,04 (7.3.5.1)
    As = max(As, As_min)
    a2 = proj - (a + a_pad / 2)
    esc = None
    for dd in (12.5, 16, 20):
        a2_min = c + (3.5 if dd < 20 else 5.0) * dd / 10
        for n in range(2, 9, 2):                                     # alças: número par de ramos
            esp = (b * 100 - 2 * c - dd / 10) / max(n - 1, 1)
            if n * BAR[dd] >= As and round(a2 * 100, 2) >= round(a2_min, 2) and esp <= min(15 * dd / 10, d * 100) and dd / 10 <= min(b, h) * 100 / 8 and esp >= dd / 10 + 2.0:
                esc = (n, dd, a2_min)
                break
        if esc:
            break
    rho = (esc[0] * BAR[esc[1]] if esc else As) / (b * d * 1e4)
    tau = Fd / (b * d) / 1e3
    tau_u = min(3.0 + 0.9 * rho * FYD, 0.27 * (1 - fck / 250) * fcd, 8.0) if ad <= 0.5 else 0.27 * (1 - fck / 250) * fcd
    kc = 0.5 if ad <= 0.5 else 0.4
    As_cost = max(kc * Asv / (d * 100) * 100, 0.15 * b * 100)       # cm²/m (7.3.6)
    As_cost_tot = As_cost * (2 / 3 * d)
    As_v = 0.0015 * b * h * 1e4                                      # 7.3.7 — a/d ≤ 1, carga direta
    T_fend = 0.25 * Fd * (1 - b_pad / b)                             # bloco parcialmente carregado (aparelho afastado das faces)
    # mísula: altura na extremidade >= metade da altura junto ao pilar (NBR 9062:2017 7.3, detalhamento; Fig. 16)
    # e biela verificada também com a altura útil na seção da carga (fundo inclinado), a favor da segurança
    d_a = h_ext + (h - h_ext) * (1 - a / proj) - c_tir
    tau_a = Fd / (b * d_a) / 1e3
    ok = dict(tirante=esc is not None, biela=tau <= tau_u, a_d=ad <= 1.0, h_ext=h_ext >= h / 2 - 1e-9, biela_na_carga=tau_a <= tau_u)
    return dict(consolo=nome, onde=onde, b_m=b, proj_m=proj, h_m=h, d_m=round(d, 3), a_m=a, a_d=round(ad, 2), modelo=modelo, gama_n=gn,
                Vd_kN=round(Vd, 1), Fd_kN=round(Fd, 1), Hd_kN=round(Hd, 1), Asv_cm2=round(Asv, 2), As_tir_cm2=round(As, 2), As_min_cm2=round(As_min, 2),
                tirante=(f"{esc[0] // 2} alça{'s' if esc[0] > 2 else ''} horizonta{'is' if esc[0] > 2 else 'l'} Ø{esc[1]:g} ({esc[0]} ramos, {esc[0] * BAR[esc[1]]:.2f} cm²)".replace(".", ",") if esc else "não cabe"),
                a2_cm=round(a2 * 100, 1), a2_min_cm=round(esc[2], 1) if esc else None, tau_wd_MPa=round(tau, 2), tau_wu_MPa=round(tau_u, 2),
                costura_cm2_m=round(As_cost, 2), costura_total_cm2=round(As_cost_tot, 2), costura="estribos horizontais Ø8 c/10 em 2/3 d" if As_cost <= 10.05 else "Ø10 c/7,5",
                estribos_verticais_cm2=round(As_v, 2), fendilhamento_kN=round(T_fend, 1), As_fend_cm2=round(T_fend / FYD * 10, 2),
                h_ext_m=h_ext, misula_m=round(h - h_ext, 3), d_carga_m=round(d_a, 3), tau_carga_MPa=round(tau_a, 2),
                ok=ok, ok_geral=all(ok.values()), norma="NBR 9062:2017 7.3.2 a 7.3.9")


HD_VM = VM["premissas"]["dente"]["hd"]
CON = [
    consolo("CP-I130", "P8A, P11, P13, P14 — I130 h 120 (dente 78 × 35, recorte 42), NEO-2 200×300; mísula 10 (DEC-054)", 0.50, 0.40, 0.49, 0.20, 0.20, 0.30,
            max(x["linhas"]["Vd_kN"] for x in I1J.values()) * 1.25, 1.1, h_ext=0.39),   # DEC-054: extremidade 39 = recorte 42 − neoprene 3 (alinhada ao fundo da viga +6,58); face 49       # Vd do JSON da viga é por apoio com γ 1,4 do pré-dim.; 1,25 = reserva da reação real com as TS
    consolo("CP-MEZ", "pilares das linhas 1 e 2 e da escada — dente 45 × 40 da VM retangular 30 × 75, NEO-5F 200×200 fretado; consolo com a largura da face do pilar (40); h = recorte − neoprene (fundo alinhado)", VM["premissas"].get("b_consolo", VM["premissas"]["b"]), VM["premissas"]["dente"]["consolo_proj"], VM["premissas"]["dente"]["consolo_h"], VM["premissas"]["x_pad"], 0.20, 0.20, m["cortante"]["Vd"], 1.2),
    consolo("DENTE VM", f"nariz do dente Gerber da VM retangular 30 × {VM['premissas']['h_pm']*100:.0f}, h {HD_VM*100:.0f}, LN {VM['premissas']['dente']['ln']*100:.0f} — 7.4 = consolo 7.3", VM["premissas"]["b"], VM["premissas"]["dente"]["ln"], HD_VM, 0.03 + VM["premissas"]["dente"]["ln"] - VM["premissas"]["x_pad"], 0.20, 0.20, m["cortante"]["Vd"], 1.2),
    # rev10 (DEC-059): consolo lateral CT-I130 nas duas faces da mesa superior da I130 onde chega cada TS-01 (linhas 3, 5, 6, 7, 8):
    # b 50 (ao longo da I130), projeção 20 além da mesa (40 → 80), h 30 na face e 15 na ponta (mísula), topo = topo da I130.
    # NEO-3C 150 × 300 de 12 a 27 cm da ponta da TS-01 (centro 3,25 cm além da face da mesa); a favor da segurança: Fd inteiro no consolo.
    consolo("CT-I130", "I130 V400/V401/V402/V403 — apoio das TS-01 (linhas 3, 5, 6, 7, 8), nas duas faces da mesa superior; NEO-3C 150×300; mísula 15 (DEC-059)",
            0.50, 0.20, 0.30, 0.0325, 0.15, 0.30, 1.4 * (Ng_ts + Nq_ts), 1.2, fck=50, h_ext=0.15, c_tir=0.075),   # tirante a 7,5 cm do topo, abaixo do N3 6 Ø25 da mesa
    consolo("CP-VB", "pilares das fachadas 1 e 9 — dente 30 × 27 da VB 15×60, NEO-6 100×100", 0.15, 0.27, 0.29, 0.135, 0.10, 0.10, VBD["Vd"], 1.1),
]
OUT["consolos"] = CON

# cintamento do topo dos pilares (6.2.3)
def cintamento(nome, b_pil, a_pad, b_pad, Fd, gn=1.1, c=0.03):
    Hd = 0.16 * Fd
    T = 0.25 * Fd * (1 - a_pad / b_pil)
    As = (gn * Hd + T) / FYD * 10
    h1 = b_pil
    n8 = math.ceil(As / (2 * 0.503))
    return dict(topo=nome, Fd_kN=round(Fd, 1), Hd_kN=round(Hd, 1), T_bloco_kN=round(T, 1), As_cm2=round(As, 2), distribuir_em_cm=round(h1 * 100),
                adotar=f"{max(n8, 3)} estribos Ø8 (2 ramos) nos {round(h1 * 100)} cm do topo, 2/3 no terço superior", a0_min_cm=round(max(1.5 * c, 0.03) * 100, 1),
                norma="NBR 9062:2017 6.2.3 (Fig. 9)")


Fd_ts = 1.3 * Ng_ts + 1.4 * Nq_ts
OUT["cintamento"] = [cintamento("P1/P2 — recuo (cabeça 30 × 40), TS-01 em NEO-4", 0.30, 0.15, 0.30, Fd_ts),
                     cintamento("P11 — topo, 2 TS-01 em NEO-3 (rev09: P8A sem TS-01, montante da W 310)", 0.40, 0.10, 0.30, 2 * Fd_ts)]

# ================================================================== 4 apoios sem recorte (7.5) e dente (7.4)
def sem_recorte(nome, Fd, prov):
    Hd = 0.16 * Fd
    Asd = (Fd / 1.2 + Hd) / FYD * 10
    Ash = Fd / (8 * FYD) * 10
    return dict(peca=nome, Fd_kN=round(Fd, 1), Hd_kN=round(Hd, 1), Asd_cm2=round(Asd, 2), Ash_Asv_cm2=round(Ash, 2), adotado=prov, norma="NBR 9062:2017 7.5 (Fig. 24)")


OUT["apoios_sem_recorte"] = [
    sem_recorte("TS-01 (pontas)", TS.R.linhas["Vd_kN"], "Asd: 3 grampos N7 Ø10 por ponta = 6 ramos = 4,71 cm²; Ash/Asv: N6 8 Ø8 + N8 2 Ø10 por ponta"),
    # VM rev04: apoio por dente Gerber (item dente_VM), não sem recorte
]
_mf = AQ / f"mef_vm_ret_dente_{round(VM['premissas']['h_pm'] * 1000)}_{round(VM['premissas']['dente']['hd'] * 1000)}{VM['premissas'].get('mef_suf', '')}.json"
MV = json.loads(_mf.read_text(encoding="utf-8")) if _mf.exists() else None
_GN_VM = MV.get("gama_n", 1.2) if MV else 1.2                       # DEC-032: γn 1,2 (parcela variável ≈ 50 %, 7.3.1.1)
_FD_VM = MV.get("Vd", MV.get("Fd")) if MV else round(_GN_VM * m["cortante"]["Vd"], 1)
OUT["dente_VM"] = dict(geometria=f"dente {HD_VM*100:.0f} × {VM['premissas']['dente']['ln']*100:.0f} (nariz), recorte {VM['premissas']['dente']['recorte']*100:.0f}, seção retangular {VM['premissas']['b']*100:.0f} × {VM['premissas']['h_pm']*100:.0f}", Fd_kN=_FD_VM, gama_n=_GN_VM,
                       Vd_reacao_kN=round(m["cortante"]["Vd"], 1),
                       MEF_Vu_kN=(MV["mef"]["Vu_kN"] if MV else None), ok_MEF=(MV["mef"]["V_pico_kN"] >= 1.06 * _FD_VM if MV else None), MEF_V_pico_kN=(MV["mef"]["V_pico_kN"] if MV else None),
                       ressalva_MEF=(MV.get("ressalva") if MV else None),
                       armacao_MEF=(MV["mef"].get("armacao") if MV else None), adotado=(MV["calculo"]["adotado"] if MV else None),
                       suspensao=f"{math.ceil(_FD_VM / 43.5 / 4.02)} estribos fechados Ø16 (2 ramos) junto ao recorte (fyd ≤ 435 MPa, 7.4)",
                       norma="NBR 9062:2017 7.4 + MEF não linear (estudo_vm_largura / mef_vm_largura_1f.py)")
OUT["dente_VB"] = dict(geometria="VB 15 × 60: dente 30 (nariz 27), recorte 30; consolo CP-VB 15 × 27 × 29 escondido, fundo alinhado ao fundo da viga",
                       Vd_kN=VBD["Vd"], Fd_kN=round(1.1 * VBD["Vd"], 1), dente=VBD["dente"], consolo_calc=VBD["consolo"], suspensao=VBD["suspensao"],
                       levantamento=dict(R_up_d_kN=VBD["R_up_d"], pino="PN-1 Ø20 roscado com porca e arruela no topo do dente", cap_kN=VBD["pino"]["cap_PN1_d"]),
                       viga=dict(Md=VBD["Md"], Md_neg=VBD["Md_neg"], inf=VBD["inf"], sup=VBD["sup"], flecha_mm=VBD["flecha_mm"], flecha_lim_mm=VBD["flecha_lim"],
                                 sigma_s=VBD["sigma_s"], sigma_lim=VBD["sigma_lim"]),
                       norma="NBR 9062:2017 7.4 (dente = consolo 7.3, γn 1,1) e Tab. 8; NBR 6118:2023 17.2, 17.3, 17.4 (calc_vb_dente.py)")
d130 = DT["I130"]
_m130 = d130.get("mef", {})
OUT["dente_I130"] = dict(MEF_Vu_kN=_m130.get("Vu_kN"), Fd_kN=d130["Vd"], Vd_reacao_kN=d130.get("Vd_reacao"), gama_n=d130.get("gama_n"), Hd_kN=d130["Hd"],
                         FS=round(_m130["Vu_kN"] / d130["Vd"], 2) if _m130 else None, ok_MEF=_m130.get("ok"), armacao_MEF=_m130.get("armacao"),
                         adotado=d130["calculo"]["adotado"],
                         suspensao="estribos fechados concentrados junto ao recorte (até dvig/4), fyd ≤ 435 MPa, Fd total (7.4)",
                         tirante="ancorado com alças horizontais (7.3.3), entrando lb além de (dvig − d)",
                         restricao="somada ao tirante a força de restrição de retração e fluência após a montagem (7.4, protendida): Hd = 0,16 Fd já incluído",
                         norma="NBR 9062:2017 7.4 (Fig. 22 e 23) + MEF não linear (5.5 não exigido: modelo numérico documentado)")

# ================================================================== 5 cálices (7.7, Tab. 15 — interface com chaves)
LEMB = 1.00
cal = []
for nome, vv in MG["verificacao_pilares"].items():
    for dirc, (Md, hh) in (("x", (vv["My"], vv["secao"].split("×")[0])), ("y", (vv["Mx"], vv["secao"].split("×")[1]))):
        h_ = float(hh) / 100
        e = Md / max(vv["N"], 1.0) / h_
        k = 1.2 if e <= 0.15 else 1.6 if e >= 2 else 1.2 + 0.4 * (e - 0.15) / 1.85
        cal.append((k * h_, nome, dirc, round(e, 2), round(k, 2)))
pior = max(cal)
OUT["calices"] = dict(Lemb_m=LEMB, interface="chaves (≥ 1 cm, Fig. 25 c) no pilar e no cálice", Lemb_min_m=round(pior[0], 3), pilar=pior[1], direcao=pior[2],
                      e_rel=pior[3], k=pior[4], ok=LEMB >= pior[0] and LEMB >= 0.40,
                      ancoragem="barras do pilar Ø20 como traspasse com o cálice (7.7.5): l0t = 2·lb,nec ≈ 0,55 m < 1,00 m (uso das barras ≈ 0,5)",
                      norma="NBR 9062:2017 7.7.2 Tab. 15; dimensionamento do colarinho (7.7.4) no projeto de fundações")

# ================================================================== 6 transitórias e flechas
def lebelle(nome, Iy, J, L, w, fcj):
    E = 0.85 * 5600 * math.sqrt(fcj) * 1e3
    qcr = 28.3 * math.sqrt(E * Iy * E / 2.4 * J) / L ** 3
    return round(qcr / (1.3 * w), 1)


trans = []
_HI = json.loads((AQ / "ligacoes.json").read_text(encoding="utf-8"))["H_I130"]
for nome, L, bf, h, w, Iy, Jt, fcj in (
        ("TS-01", TS.L / 1000, 0.40, 0.90, TS.car.g1, 0.12 * 0.40 ** 3 / 12 + 0.15 * 0.40 ** 3 / 12, 0.4 * 0.12 ** 3 / 3 + 0.4 * 0.15 ** 3 / 3 + 0.63 * 0.15 ** 3 / 3, 35),
        ("I130 (V406)", v["L_peca"], 0.40, _HI, v["linhas"]["peso_kN_m"], 0.22 * 0.4 ** 3 / 12 + 0.25 * 0.4 ** 3 / 12, 0.4 * 0.22 ** 3 / 3 + 0.4 * 0.25 ** 3 / 3 + (_HI - 0.47) * 0.15 ** 3 / 3, v["arranjo"]["fckj"]),   # DEC-054: h 1,20, fckj 50
        ("VM retangular 30 × 75", m["L_peca"], 0.30, 0.75, m["cargas"]["g_pm"], 0.75 * 0.30 ** 3 / 12, 0.75 * 0.30 ** 3 / 3 * (1 - 0.63 * 0.30 / 0.75), 32),
        ("VB 15×60", 9.43, 0.15, 0.60, 2.25, 0.60 * 0.15 ** 3 / 12, 0.60 * 0.15 ** 3 / 3 * (1 - 0.63 * 0.15 / 0.60), 25),
        ("Placa 125×10 (içada na vertical)", 10.15, 0.10, 1.25, 3.12, 1.25 * 0.10 ** 3 / 12, 1.25 * 0.10 ** 3 / 3 * 0.95, 25)):
    r1, r2 = L / bf, L * h / bf ** 2
    trans.append(dict(peca=nome, L_m=round(L, 2), bf_m=bf, L_bf=round(r1, 1), Lh_bf2=round(r2, 1), criterio_6_1=r1 <= 50 and r2 <= 500,
                      FS_lebelle=lebelle(nome, Iy, Jt, L, w, fcj), ok=(r1 <= 50 and r2 <= 500) or lebelle(nome, Iy, Jt, L, w, fcj) >= 2.5))
OUT["estabilidade_lateral"] = dict(itens=trans, norma="NBR 9062:2017 6.1 (L/bf ≤ 50 e L·h/bf² ≤ 500 sem carga crítica conhecida; acima disso, carga crítica de "
                                   "Lebelle q_cr = 28,3·√(EIy·GJ)/L³ com peso βa 1,3 e FS ≥ 2,5)")
OUT["transitorias"] = dict(
    beta_a=dict(saque_montagem=1.3, transporte_desfavoravel=1.3, transporte_favoravel=0.8, alcas=3.0, pilares="1,3 com σs ≤ 0,50 fyk"),
    TS01=dict(alcas_kN=getattr(TS, "ALCA_Fd", None), cap_kN=getattr(TS, "ALCA_cap", None)),
    VM=VM["VM-02"]["icamento"],
    pilar_PL=dict(peso_kN_m=6.0, L_m=11.0, M_basculamento_d=round(1.3 * (6.0 * 8.5 ** 2 / 8 - 6.0 * 2.5 ** 2 / 4), 1),
                  sigma_s_MPa=round(1.3 * (6.0 * 8.5 ** 2 / 8 - 6.0 * 2.5 ** 2 / 4) / (15.7e-4 * 0.9 * 0.35) / 1e3, 0), lim=250,
                  obs="basculamento pela alça de topo com a base no chão; transporte apoiado em 2 pontos a 0,21 L"),
    resistencias_minimas="fcj ≥ 21 MPa para liberar protensão e manusear peças protendidas; ≥ 15 MPa peças armadas (8.2.2.2) — adotados: TS-01 " + f"{TS.P['fckj']:g}, I130 {I1J['V406']['arranjo']['fckj']:g}, VM {VM['premissas'].get('fckj', 32):g}, placas 25, VB/pilares 25",
    estoque="pressão nos calços ≤ 0,3 fcj (10.2)")
OUT["flechas"] = [
    dict(peca="TS-01 (cobertura, i = 3 %, sem empoçamento)", final_mm=TS.R.linhas["flecha_final_mm"], lim_mm=round(TS.L_calc * 1000 / 250, 1), regra="Tab. 8: L/250",
         contraflecha_mm=round(Pts * ets * TS.L_calc ** 2 / (8 * EI_ts) * 1000, 1), lim_contraflecha_mm=round(TS.L_calc * 1000 / 150, 1)),
    dict(peca="I130 V406 (linear, L > 20 m)", final_mm=v["linhas"]["flecha_final_mm"], lim_mm=round(v["L_calc"] * 1000 / 350, 1), regra="Tab. 9: L/350"),
    dict(peca="VM retangular 30 × 75 (piso, solidarizada)", final_mm=m["flecha"]["final_mm"], lim_mm=m["flecha"]["lim_final_mm"], regra="Tab. 9: L/250 (L ≤ 15 m)",
         montagem_mm=m["flecha"]["montagem_mm"], lim_montagem_mm=m["flecha"]["lim_montagem_L500"]),
]

# ================================================================== 7 folgas e tolerâncias
def tex(L):
    return 10 if L <= 5 else 15 if L <= 10 else 20                   # Tab. 2 (comprimento, ±mm)


def folga(peca, L, adotada, apoio_nom, apoio_min, dT=15, eps_cs=0.0, tex_proj=None):
    t = tex_proj if tex_proj is not None else tex(L)
    D = (1e-5 * dT) * L * 1000                                       # alongamento térmico (mm); retração encurta (a favor)
    req = t / 2 + 10 + D / 2                                         # meia tolerância de fabricação + locação ±10 (5.2.2.6) + Δ/2
    return dict(peca=peca, L_m=L, tex_mm=t, tloc_mm=10, Delta_mm=round(D, 1), folga_req_mm=round(req, 1), folga_adotada_mm=adotada,
                apoio_nominal_mm=apoio_nom, apoio_pior_mm=round(apoio_nom - req, 1) if apoio_nom else None, apoio_min_mm=apoio_min,
                ok=adotada >= req and (apoio_nom is None or apoio_nom - req >= apoio_min))


OUT["folgas"] = [
    folga("TS-01 — ponta no pilar lateral (face da platibanda)", 19.70, 25, 275, 200),
    folga("TS-01 — ponta central (metade do vão de 38; tolerância de projeto do comprimento ±10 mm)", 19.70, 19, 162, 100, tex_proj=10),
    folga("I130 — ponta no pilar central (dente no CP-I130)", 24.13, 25, 350, 200),
    folga("VM retangular — ponta no pilar (consolo CP-MEZ 40)", m["L_peca"], 30, 400 - 30, 200),
    folga("VB 15×60 — ponta no pilar (dente no CP-VB)", 9.43, 25, 270, 100),
    folga("Placa 125×10 — junta vertical no eixo do pilar (rev03: 10 mm)", 10.15, 10, None, 0, tex_proj=5),
    folga("Placa 125×10 — junta vertical no eixo do pilar (rev04: 20 mm, tolerância de projeto ±5)", 10.15, 20, None, 0, tex_proj=5),
]
OUT["tolerancias"] = dict(
    fabricacao="Tab. 2: lineares L ≤ 5 m ±10, 5–10 m ±15, > 10 m ±20 mm; seção −5/+10; linearidade ±L/1000. Placas: tolerância de projeto ±5 mm no comprimento "
               "(mais apertada que a Tab. 2, 5.2.1.2), planicidade ±L/1000. Cordoalhas ±10 mm, centro resultante ±5, insertos ±15 (5.2.2.5).",
    montagem="5.2.2.6: planta ±10 entre apoios consecutivos (acumulado 0,1 % do comprimento); prumo H/300 ≤ 25 mm; nível dos apoios ±10 (acumulado 30); "
             "pilares ±10 em planta e elevação.")

# ================================================================== 8 incêndio e cobrimentos
OUT["incendio_cobrimentos"] = dict(
    cobrimentos="CAA II. Pré-moldado (9.2.1.1, Δc = 5 mm): vigas e pilares armados 25 mm; protendidos 30 mm junto à armadura ativa. "
                "Placas 10 cm (elemento delgado, 3.5): cordoalha com 20 mm de cobrimento — aceito só com fábrica pré-fabricada (12.1.2), fck ≥ 40 MPa e "
                "a/c ≤ 0,45, por analogia aos mínimos de elementos delgados protendidos (15–20 mm) em CAA I/II; confirmar com a fábrica.",
    placas="espessura 100 mm de concreto com agregado silicoso: TRRF 90 min como vedação (Tab. 6: 80 mm para 1 h, 100 mm para 1,5 h)",
    laje_alveolar="h20 + capa 5: TRRF 60 com c1 ≥ 30 mm (Tab. 3); confirmar c1 e MSd,fi/MRd com o fabricante",
    metalicos="terças e ST-1P não são elementos de estabilidade do pórtico de concreto; pinos e cantoneiras de ligação ficam embutidos/grauteados",
    TRRF="confirmar o TRRF exigido pela IT do Corpo de Bombeiros (ocupação e área) — não informado")

# ================================================================== resumo
fal = []
for n in NEO:
    if not n["ok_geral"] and "rev03" not in n["aparelho"]:
        fal.append(f"{n['aparelho']}: " + ", ".join(k for k, v in n["ok"].items() if not v))
for c in CON:
    if not c["ok_geral"]:
        fal.append(f"{c['consolo']}: " + ", ".join(k for k, v in c["ok"].items() if not v))
for t in trans:
    if not t["ok"]:
        fal.append(f"lateral {t['peca']}")
for f_ in OUT["folgas"]:
    if not f_["ok"] and "rev03" not in f_["peca"]:
        fal.append(f"folga {f_['peca']}")
OUT["pendencias_calculo"] = fal
(AQ / "nbr9062.json").write_text(json.dumps(OUT, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
if __name__ == "__main__":
    for n in NEO:
        print(n["aparelho"], n["ok_geral"], {k: v for k, v in n["ok"].items() if not v}, n["sigma_MPa"], n.get("theta_g"), n.get("lim_theta_g"), n.get("lim_theta_gq"))
    for c in CON:
        print(c["consolo"], c["ok_geral"], c["a_d"], c["As_tir_cm2"], c["tirante"], c["tau_wd_MPa"], c["tau_wu_MPa"], c["a2_cm"], c["a2_min_cm"])
    for t in trans:
        print(t)
    for f_ in OUT["folgas"]:
        print(f_["peca"], f_["folga_req_mm"], f_["folga_adotada_mm"], f_["ok"])
    print(OUT["calices"])
    print(OUT["cintamento"])
    print(OUT["apoios_sem_recorte"])
    print("estab", mg["gama_z"], mg["ELS"])
    print("PENDÊNCIAS:", fal)
