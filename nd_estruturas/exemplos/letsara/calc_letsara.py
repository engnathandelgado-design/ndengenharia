"""Letsara (Marque Engenharia) — pré-dimensionamento da estrutura pré-moldada, rodada 1.

Fonte da geometria: PROJETO LETSARA - PAVILHÃO R01 - ARQ-Model.pdf (lido em 12/10/2026).
Critérios de Nathan (12/10/2026): viga I de cobertura apoiada em consolo no pilar, platibanda,
água única 3%, terças metálicas Ue com insert rosqueado, pilares que apoiam viga de cobertura e
vigas I com largura mínima de 40 cm, laje alveolar com sobrecarga de 500 kgf/m², versão sem
vigas de travamento, buscar seções menores.

Rodar: python exemplos/letsara/calc_letsara.py  → resultados.json e resumo.md nesta pasta.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from nd_estruturas.prefabricados import (
    Carregamento, Concreto, armadura_minima_metodo_geral, menor_protensao, pressao_vento,
    secao_I, secao_retangular, torcao_retangular, verificar_viga_pretracionada,
)

AQUI = Path(__file__).parent
C40 = Concreto(40)

# ---------------------------------------------------------------- premissas (a confirmar)
P = dict(
    V0=45.0,                 # m/s — LOCAL DA OBRA A CONFIRMAR
    cpe_parede_barl=0.7, cpe_parede_sotav=0.5, cpe_cob=-0.8, cpi=0.2,
    g_cob=0.25,              # kN/m² telha + terças + instalações (sobre a viga I)
    telha=0.10,              # kN/m² (sobre a terça)
    q_cob=0.25,              # kN/m² sobrecarga de cobertura (NBR 6120:2019, conferir)
    placa=0.10 * 25,         # kN/m² placa 10 cm
    e_placa=0.40,            # m do eixo do pilar ao CG da placa (face 0,30 + folga + meia placa)
    alt_placas=10.0,
    trib=9.655,              # m maior faixa entre pórticos internos
    L_pilar=10.0,
    q_mez=5.0,               # kN/m² (500 kgf/m²)
    rev_mez=1.0, capa=0.05 * 25,
    pp_alveolar={"h20": 2.80, "h26.5": 3.70, "h32": 4.30},
    e_tor=0.25,              # m excentricidade do apoio em aba/dente na viga central
)
q_v = pressao_vento(P["V0"])
res = {"premissas": P, "q_vento_kN_m2": round(q_v, 3)}

# ---------------------------------------------------------------- 1. terças metálicas Ue


def ue_props(h, b, d, t):
    """Seção bruta pela linha média (cm, cm⁴, cm³, kg/m) — sem largura efetiva (NBR 14762, conferir)."""
    hm, bm, dm = h - t, b - t, d - t / 2
    A = t * (hm + 2 * bm + 2 * dm)
    Ix = t * hm ** 3 / 12 + 2 * bm * t * (hm / 2) ** 2 + 2 * (t * dm ** 3 / 12 + t * dm * (hm / 2 - dm / 2) ** 2)
    return dict(A=A, Ix=Ix, Wx=Ix / (h / 2), kg_m=A * 0.785)


UE = {
    "Ue 150x60x20x2,25": (15, 6, 2, 0.225), "Ue 200x75x25x2,65": (20, 7.5, 2.5, 0.265),
    "Ue 200x75x25x3,00": (20, 7.5, 2.5, 0.30), "Ue 250x85x25x2,65": (25, 8.5, 2.5, 0.265),
    "Ue 250x85x25x3,00": (25, 8.5, 2.5, 0.30), "Ue 300x85x25x3,00": (30, 8.5, 2.5, 0.30),
}
L_terca = P["trib"] - 0.40  # vão livre entre mesas das vigas I
fy = 250e3  # kPa (conferir aço do fornecedor; ZAR-345 reduz os perfis)
tercas = []
for s in (1.20, 1.60, 2.00, 2.45):
    escolha = None
    for nome, dims in UE.items():
        pr = ue_props(*dims)
        pp = pr["kg_m"] * 0.01
        qd = 1.25 * (P["telha"] * s + pp) + 1.5 * P["q_cob"] * s
        qw = 1.4 * (abs(P["cpe_cob"]) + P["cpi"]) * q_v * s - 1.0 * (P["telha"] * s + pp)
        Wm = pr["Wx"] * 1e-6
        Md, Mw = qd * L_terca ** 2 / 8, qw * L_terca ** 2 / 8
        ok_m = Md <= Wm * fy / 1.1 and Mw <= 0.7 * Wm * fy / 1.1  # 0,7: FLT na sucção com correntes a L/3 (conferir)
        EI = 200e6 * pr["Ix"] * 1e-8
        fl = 5 * (P["telha"] * s + pp + P["q_cob"] * s) * L_terca ** 4 / (384 * EI)
        ok_f = fl <= L_terca / 180
        if ok_m and ok_f:
            n_cob = math.ceil(20.05 / s) + 1
            escolha = dict(espac_m=s, perfil=nome, kg_m=round(pr["kg_m"], 2),
                           kg_m2=round(pr["kg_m"] / s, 2), flecha_mm=round(fl * 1000, 1),
                           util_flexao=round(max(Md / (Wm * fy / 1.1), Mw / (0.7 * Wm * fy / 1.1)), 2),
                           linhas_por_agua_20m=n_cob)
            break
    tercas.append(escolha or dict(espac_m=s, perfil="nenhum Ue da lista passa"))
res["tercas"] = tercas

# ---------------------------------------------------------------- 2. viga I de cobertura
L_I = 20.05 - 0.55 - 0.35  # eixo do pilar lateral → eixo da viga central, menos apoios
g2 = P["g_cob"] * P["trib"]
qI = P["q_cob"] * P["trib"]
wI = (abs(P["cpe_cob"]) + P["cpi"]) * q_v * P["trib"]
vigasI = []
for h in (0.70, 0.80, 0.90, 1.00, 1.10):
    for bw in (0.10, 0.12):
        sec = secao_I(h, bs=0.40, bi=0.40, bw=bw)
        car = Carregamento(g1=sec.A * 25, g2=g2, q=qI, w=wI)
        r = None
        for n in range(4, 25, 2):
            yc = 0.05 if n <= 8 else 0.075
            rr = verificar_viga_pretracionada(sec, L_I, car, C40, n, "12.7", y_cord=yc)
            if rr.ok:
                r = rr
                break
        Rg = (car.g1 + car.g2) * L_I / 2
        Rq = car.q * L_I / 2
        Rup_d = (1.4 * car.w - 1.0 * (car.g1 + car.g2)) * L_I / 2  # arrancamento no apoio
        Mneg_d = (1.4 * car.w - 1.0 * (car.g1 + car.g2)) * L_I ** 2 / 8
        As_top = max(0.0, Mneg_d / (0.9 * (h - 0.05) * 500 / 1.15 * 1000)) * 1e4
        vigasI.append(dict(secao=sec.nome, bw=bw, h=h, A_m2=round(sec.A, 4), peso_t=round(sec.A * 25 * (L_I + 0.4) / 9.81, 2),
                           passa=r is not None, n_cord_12_7=None if r is None else r.n_cord,
                           detalhes=None if r is None else r.linhas, avisos=None if r is None else r.avisos,
                           R_g_kN=round(Rg, 1), R_q_kN=round(Rq, 1),
                           arrancamento_d_kN=round(max(Rup_d, 0), 1), M_succao_d_kNm=round(max(Mneg_d, 0), 1),
                           As_sup_succao_cm2=round(As_top, 2)))
res["viga_I_cobertura"] = dict(L_calc_m=round(L_I, 2), g2_kN_m=round(g2, 2), q_kN_m=round(qI, 2),
                               w_succao_kN_m=round(wI, 2), opcoes=vigasI)
I_ok = [v for v in vigasI if v["passa"]]
I_esc = min(I_ok, key=lambda v: (v["A_m2"] * 25 + v["n_cord_12_7"] * 0.78 * 0.01)) if I_ok else None
res["viga_I_escolhida"] = I_esc

# ---------------------------------------------------------------- 3. viga central (recebe vigas I)
RgI, RqI = I_esc["R_g_kN"], I_esc["R_q_kN"]
g1I = I_esc["A_m2"] * 25
vc_cases = {
    "V407 (P8A–P11)": (19.31 - 0.6, [9.655 - 0.3]),
    "V406 (P11–P13)": (23.69 - 0.6, [9.505 - 0.3, 19.085 - 0.3]),
    "V405 (P13–P14)": (23.77 - 0.6, [4.98 - 0.3, 14.56 - 0.3]),
}


def mmax_pontos(L, xs, F):
    best = 0.0
    for xt in [L * i / 200 for i in range(201)]:
        Ra = sum(F * (L - x) / L for x in xs)
        M = Ra * xt - sum(F * (xt - x) for x in xs if x < xt)
        best = max(best, M)
    return best


centrais = []
for nome, (L, xs) in vc_cases.items():
    opcoes_sec = [secao_retangular(0.40, h) for h in (1.00, 1.20, 1.40, 1.60)] + \
                 [secao_I(h, bs=0.60, ts=0.15, bw=0.20, bi=0.60, ti=0.20, nome=f"I{h*100:.0f}/60") for h in (1.00, 1.20, 1.40)]
    for sec in opcoes_sec:
        h = sec.h
        g1 = sec.A * 25
        Mg2 = mmax_pontos(L, xs, 2 * RgI)
        Mq = mmax_pontos(L, xs, 2 * RqI)
        car = Carregamento(g1=g1, g2=8 * Mg2 / L ** 2, q=8 * Mq / L ** 2)
        r = menor_protensao(sec, L, car, C40, nmax=36, y_cord=0.10)
        # cortante real no apoio e torção (montagem com um lado e sobrecarga de um lado)
        Vd = 1.3 * (g1 * L / 2 + sum(2 * RgI * (L - x) / L for x in xs)) + 1.4 * sum(2 * RqI * (L - x) / L for x in xs)
        T_mont = 1.3 * (g1I * L_I / 2) * P["e_tor"] * len(xs) / 2  # vigas I de um lado só, sem terças
        T_serv = 1.4 * RqI * P["e_tor"] * len(xs) / 2
        Td = max(T_mont, T_serv)
        tor = torcao_retangular(0.40 if sec.nome.startswith("R") else 0.20, h, Td, Vd, C40)
        centrais.append(dict(viga=nome, L=round(L, 2), secao=sec.nome, A_m2=round(sec.A, 3),
                             peso_t=round(sec.A * 25 * (L + 0.6) / 9.81, 1), passa_flexao=r is not None,
                             n_cord_12_7=None if r is None else r.n_cord,
                             avisos=None if r is None else r.avisos,
                             flecha_mm=None if r is None else r.linhas["flecha_final_mm"],
                             Vd_kN=round(Vd, 1), Td_kNm=round(Td, 1), torcao=tor,
                             reacao_apoio_k_kN=round((g1 * L / 2 + sum(2 * (RgI + RqI) * (L - x) / L for x in xs)), 1)))
res["viga_central"] = centrais

# ---------------------------------------------------------------- 4. vigas do mezanino (laje de um lado)
L_mez = 9.87 - 0.6
mezanino = []
for laje in ("h20", "h26.5", "h32"):
    pass
g_laje = P["pp_alveolar"]["h26.5"] + P["capa"] + P["rev_mez"]
vao_laje = 10.05
for nome_sec, sec in [("R40x60", secao_retangular(0.40, 0.60)), ("R40x70", secao_retangular(0.40, 0.70)),
                      ("R40x80", secao_retangular(0.40, 0.80)), ("I70", secao_I(0.70, bw=0.15)),
                      ("I80", secao_I(0.80, bw=0.15))]:
    car = Carregamento(g1=sec.A * 25, g2=g_laje * vao_laje / 2, q=P["q_mez"] * vao_laje / 2, psi1=0.6, psi2=0.4)
    r = menor_protensao(sec, L_mez, car, C40, nmax=30, y_cord=0.075)
    e = 0.20 + 0.075
    t_mont = 1.3 * (P["pp_alveolar"]["h26.5"] + P["capa"]) * vao_laje / 2 * e  # kN·m/m antes da capa curar
    Td = t_mont * L_mez / 2
    Vd = (1.3 * (car.g1 + car.g2) + 1.4 * car.q) * L_mez / 2
    tor = torcao_retangular(0.40, sec.h, Td, Vd, C40) if nome_sec.startswith("R") else None
    mezanino.append(dict(secao=nome_sec, L=round(L_mez, 2), passa_flexao=r is not None,
                         n_cord_12_7=None if r is None else r.n_cord,
                         flecha_mm=None if r is None else r.linhas["flecha_final_mm"],
                         Td_montagem_kNm=round(Td, 1), torcao=tor, avisos=None if r is None else r.avisos))
res["vigas_mezanino"] = mezanino
# laje alveolar — momento de cálculo por metro (escolha pela tabela do fabricante)
lajes = {}
for k, pp in P["pp_alveolar"].items():
    hk = {"h20": 0.20, "h26.5": 0.265, "h32": 0.32}[k]
    Md = (1.3 * (pp + P["capa"] + P["rev_mez"]) + 1.4 * P["q_mez"]) * 9.6 ** 2 / 8
    Ap = Md / (0.9 * (hk + 0.05 - 0.04) * 1710 / 1.15 * 1000) * 1e4
    lajes[k] = dict(Md_kNm_m=round(Md, 1), Ap_cm2_m=round(Ap, 2), cord_12_7_por_painel_1_25m=math.ceil(Ap * 1.25 / 0.987))
res["laje_alveolar"] = lajes

# ---------------------------------------------------------------- 5. pilares (método geral, OpenSees)
W_placas = P["placa"] * P["trib"] * P["alt_placas"]
M_placas = W_placas * P["e_placa"]
pilares = []
Nk_lat = RgI + RqI + W_placas + 0.4 * 0.6 * 25 * 11 + 15  # +15 kN consolo/insertos
Nk_lat_perm = RgI + W_placas + 0.4 * 0.6 * 25 * 11 + 15
w_sot = P["cpe_parede_sotav"] * q_v * P["trib"]
w_barl = P["cpe_parede_barl"] * q_v * P["trib"]
for b, h in ((0.40, 0.50), (0.40, 0.60), (0.40, 0.70)):
    Nd = 1.3 * Nk_lat
    phi_ef = 2.0 * (1.0 * M_placas) / (1.3 * M_placas + 1.4 * w_sot * 50)
    r_sot = armadura_minima_metodo_geral(b, h, P["L_pilar"], Nd, 1.4 * w_sot, C40, Md_base=1.3 * M_placas, phi_ef=phi_ef)
    r_barl = armadura_minima_metodo_geral(b, h, P["L_pilar"], 1.0 * Nk_lat_perm, 1.4 * w_barl, C40,
                                          Md_base=-1.0 * M_placas, phi_ef=0.5)
    r_fraco = armadura_minima_metodo_geral(h, b, P["L_pilar"], Nd, 0.0, C40, phi_ef=2.0)
    EI = 0.7 * C40.Ecs * b * h ** 3 / 12
    d_els = 0.3 * w_barl * P["L_pilar"] ** 4 / (8 * EI) * 1000
    pilares.append(dict(pilar="lateral P1/P2", secao=f"{b*100:.0f}x{h*100:.0f}", Nk_kN=round(Nk_lat, 1),
                        topo_ELS_vento_freq_mm=round(d_els, 1), lim_H1700_mm=round(10000 / 1700, 1),
                        lim_H500_mm=20.0,
                        M_placas_k_kNm=round(M_placas, 1), transversal_sotavento=r_sot,
                        transversal_barlavento=r_barl, longitudinal_sem_travamento=r_fraco))
# pilar de fachada (frente/fundo) — vento longitudinal direto, sem travamento
w_fach = P["cpe_parede_barl"] * q_v * 9.87
for b, h in ((0.40, 0.60), (0.60, 0.40)):
    Nk = 0.15 * 0.70 * 25 * 9.87 + W_placas * 0 + 0.4 * 0.6 * 25 * 11 + P["placa"] * 9.87 * P["alt_placas"]
    r = armadura_minima_metodo_geral(b, h, P["L_pilar"], 1.3 * Nk, 1.4 * w_fach, C40, Md_base=1.3 * P["placa"] * 9.87 * 10 * 0.40, phi_ef=1.0)
    pilares.append(dict(pilar="fachada P3–P5 / P14–P16 (vento longitudinal)", secao=f"{b*100:.0f}x{h*100:.0f} (h na direção do vento)",
                        Nk_kN=round(Nk, 1), resultado=r))
# pilar central P11 (40x40): vigas I dos dois lados + V407 e V406
v407 = min((c for c in centrais if c["viga"].startswith("V407") and c["passa_flexao"]), key=lambda c: c["A_m2"])
v406 = min((c for c in centrais if c["viga"].startswith("V406") and c["passa_flexao"]), key=lambda c: c["A_m2"])
Nk_P11 = 2 * (RgI + RqI) + v407["reacao_apoio_k_kN"] + v406["reacao_apoio_k_kN"] + 0.4 * 0.4 * 25 * 11
for b, h in ((0.40, 0.40), (0.45, 0.45), (0.50, 0.50)):
    Md_desbal = 1.4 * RqI * 0.40
    r = armadura_minima_metodo_geral(b, h, P["L_pilar"], 1.35 * Nk_P11, 0.0, C40, Md_base=Md_desbal, phi_ef=2.0)
    pilares.append(dict(pilar="central P11", secao=f"{b*100:.0f}x{h*100:.0f}", Nk_kN=round(Nk_P11, 1),
                        nu=round(1.35 * Nk_P11 / (b * h * C40.fcd), 2), resultado=r))
res["pilares"] = pilares

(AQUI / "resultados.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(res, indent=1, ensure_ascii=False)[:200])
