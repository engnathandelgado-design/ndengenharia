"""Letsara — rodada 2 (refinada), 12/10/2026.

Mudanças em relação à rodada 1:
- vento com S3 = 0,95 (NBR 6123, grupo 3: edificação industrial com baixo fator de ocupação);
- sobrecarga de cobertura com ψ2 = 0 (cobertura sem acesso, só manutenção);
- ELU das vigas por compatibilidade de deformações na seção real (σpd > fpyd);
- estrutura trabalhando em conjunto: a viga I de cobertura funciona como escora e tirante entre
  os pilares do pórtico (o vento divide entre barlavento e sotavento e os momentos das placas
  dos dois lados se equilibram); travamentos + contraventamento da cobertura repartem o vento
  longitudinal entre todos os pilares;
- viga central em I com mesas 40×25, chanfro de 15 cm e alma de 20 (padrão de Nathan).
"""
from __future__ import annotations

import json
from pathlib import Path

from nd_estruturas.prefabricados import (
    Carregamento, Concreto, armadura_minima_metodo_geral, menor_protensao_grade, pressao_vento, secao_I,
)

AQUI = Path(__file__).parent
TRIB, LP = 9.655, 10.0
qv = pressao_vento(45.0, S3=0.95)
w_cob = (0.8 + 0.2) * qv * TRIB
out = {"q_vento_kN_m2": round(qv, 3)}


def I_padrao(h):  # mesas 40×25, chanfro 15, alma 20
    return secao_I(h, bs=0.40, ts=0.25, ms=0.15, bw=0.20, bi=0.40, ti=0.25, mi=0.15, nome=f"I{h*100:.0f}p")


def I_fina(h):  # mesas 40×12, chanfro 8, alma 12
    return secao_I(h, bs=0.40, ts=0.12, ms=0.08, bw=0.12, bi=0.40, ti=0.15, mi=0.08, nome=f"I{h*100:.0f}f")


# ------------------------------------------------------------ viga I de cobertura
L_I = 19.15
cob = []
for fck in (40, 50):
    C = Concreto(fck)
    for sec in [I_fina(h) for h in (0.60, 0.70, 0.80)] + [I_padrao(h) for h in (0.80, 0.90)]:
        car = Carregamento(sec.A * 25, 0.25 * TRIB, 0.25 * TRIB, w=w_cob, psi1=0.4, psi2=0.0)
        r = menor_protensao_grade(sec, L_I, car, C)
        cob.append(dict(fck=fck, secao=sec.nome, A=round(sec.A, 3), peso_t=round(sec.A * 25 * 19.55 / 9.81, 1),
                        cord=None if r is None else r.n_cord, sup=None if r is None else r.linhas["n_cord_sup"],
                        ycg=None if r is None else r.linhas["y_cg_mm"],
                        flecha_mm=None if r is None else r.linhas["flecha_final_mm"],
                        Rg=round((sec.A * 25 + 0.25 * TRIB) * L_I / 2, 1), Rq=round(0.25 * TRIB * L_I / 2, 1),
                        arranc_d=round(max(0, (1.4 * w_cob - sec.A * 25 - 0.25 * TRIB) * L_I / 2), 1)))
out["viga_I_cobertura"] = cob

# ------------------------------------------------------------ viga central I padrão


def mmax(L, xs, F):
    best = 0.0
    for i in range(401):
        xt = L * i / 400
        Ra = sum(F * (L - x) / L for x in xs)
        best = max(best, Ra * xt - sum(F * (xt - x) for x in xs if x < xt))
    return best


casos = {"V407": (18.71, [9.355]), "V406": (23.09, [9.205, 18.785]), "V405": (23.17, [4.68, 14.26])}
central = []
for base in ("I70f", "I90p"):
    ref = next(c for c in cob if c["secao"] == base and c["fck"] == 40)
    for fck in (40, 50):
        C = Concreto(fck)
        for nome, (L, xs) in casos.items():
            for h in (1.0, 1.1, 1.2):
                sec = I_padrao(h)
                car = Carregamento(sec.A * 25, 8 * mmax(L, xs, 2 * ref["Rg"]) / L ** 2,
                                   8 * mmax(L, xs, 2 * ref["Rq"]) / L ** 2, psi1=0.4, psi2=0.0)
                r = menor_protensao_grade(sec, L, car, C)
                central.append(dict(cobertura=base, fck=fck, viga=nome, secao=sec.nome,
                                    peso_t=round(sec.A * 25 * (L + 0.6) / 9.81, 1),
                                    cord=None if r is None else r.n_cord,
                                    sup=None if r is None else r.linhas['n_cord_sup'],
                                    ycg=None if r is None else r.linhas['y_cg_mm'],
                                    flecha_mm=None if r is None else r.linhas["flecha_final_mm"]))
out["viga_central"] = central

# ------------------------------------------------------------ pilares com a estrutura trabalhando junto
C40 = Concreto(40)
ref = next(c for c in cob if c["secao"] == "I70f" and c["fck"] == 40)
W_placas = 2.5 * TRIB * LP
Nk = ref["Rg"] + ref["Rq"] + W_placas + 0.4 * 0.6 * 25 * 11 + 15
w1, w2 = 0.7 * qv * TRIB, 0.5 * qv * TRIB
w_med = (w1 + w2) / 2  # viga I como escora: os dois pilares do pórtico deslocam juntos
# longitudinal: vento nas fachadas repartido por travamento + contraventamento entre n pilares
n_pil = 24
wf_frente, wf_fundo = 0.7 * qv * 9.87, 0.5 * qv * 9.87
soma = 3 * LP / 8 * (5 * wf_frente + 5 * wf_fundo)
k_delta = soma / n_pil  # força no topo de cada pilar (kN)
pil = []
for b, h in ((0.40, 0.50), (0.40, 0.60)):
    EI = 1.0 * C40.Ecs * b * h ** 3 / 12
    d_els = 0.3 * w_med * LP ** 4 / (8 * EI) * 1000
    tr = armadura_minima_metodo_geral(b, h, LP, 1.3 * Nk, 1.4 * w_med, C40, phi_ef=0.5)
    lg = armadura_minima_metodo_geral(h, b, LP, 1.3 * Nk, 0.0, C40, Hd_top=1.4 * k_delta, phi_ef=0.5)
    pil.append(dict(pilar="lateral P1/P2", secao=f"{b*100:.0f}x{h*100:.0f}", Nk=round(Nk, 1),
                    transversal=tr, longitudinal=lg, topo_ELS_mm=round(d_els, 1)))
Nk_f = 0.15 * 0.70 * 25 * 9.87 + 0.4 * 0.6 * 25 * 11 + 2.5 * 9.87 * LP
for b, h in ((0.40, 0.50), (0.40, 0.60)):
    # pilar de fachada com o 40 na direção do vento longitudinal (mesma orientação dos laterais)
    r = armadura_minima_metodo_geral(h, b, LP, 1.3 * Nk_f, 1.4 * wf_frente, C40,
                                     Hd_top=-1.4 * (3 * wf_frente * LP / 8 - k_delta), phi_ef=0.5)
    pil.append(dict(pilar="fachada (40 na direção do vento)", secao=f"{b*100:.0f}x{h*100:.0f}", Nk=round(Nk_f, 1), longitudinal=r))
out["pilares"] = pil
out["k_delta_kN"] = round(k_delta, 1)

(AQUI / "resultados_r2.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
