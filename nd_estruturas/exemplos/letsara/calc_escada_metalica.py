"""Letsara rev09 (23/10/2026) — escada METÁLICA do mezanino (DEC-045, decisão do Nathan: só até o 1º nível, metálica).

Arquitetônico R01: escada em U, 22 degraus de 17,72 cm × 28 cm, patamar intermediário +1,95 (160 cm), lances de 2,80 m.
Abertura da laje +3,90 entre o P6 (25×40), o P7 (40×60) e a linha 2; laje +7,30 contínua.
Estrutura (tudo parafusado, sem solda de campo — padrão ND):
  - lances: 2 longarinas U 152 × 12,2 (6") por lance; degraus em chapa xadrez 4,75 mm dobrada sobre cantoneiras
    L 38 × 38 × 4,8 parafusadas nas longarinas (2 M10 por ponta);
  - patamar +1,95: viga de fundo W 150 × 22,5 parafusada nas faces do P6 e do P7 (4 barras roscadas M16 embutidas por face);
    viga de frente W 150 × 22,5 sobre 2 pilaretes W 150 × 22,5; piso em chapa xadrez 6,3 sobre perfis U 102 × 7,4 a cada 60 cm;
  - chegada +3,90 (faixa de 1,08 m junto à linha 2): viga de frente W 150 × 22,5 sobre 2 pilaretes; viga de fundo W 150 × 22,5
    parafusada nas faces do P6 da linha 2 e do P2-L2; piso igual ao do patamar;
  - 1º degrau: pé das longarinas com chapa de base 200 × 150 × 12,5 e 2 chumbadores químicos M12 no piso (apoio próprio no piso).
Cargas: NBR 6120:2019 — escada com acesso público 3,0 kN/m² (cargas_mezanino.json); peso próprio da chapa e perfis.
Combinação ELU 1,4 G + 1,5 Q (NBR 8800:2024 4.7); flecha L/350 (piso, Tab. B.1); vibração: f1 ≥ 5 Hz (conforto, referência).
Unidades: kN, m.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

AQ = Path(__file__).parent
sys.path.insert(0, str(AQ.parents[1]))
sys.path.insert(0, str(AQ))
from nd_estruturas import metalica_laminada as ML
from geometria import ESCADA, Y_LIN

E = ESCADA
Q = json.loads((AQ / "cargas_mezanino.json").read_text(encoding="utf-8"))["escada"]["sobrecarga"]
G_DEG = 0.0475 * 78.5 / 10 * 1.15 + 0.10                     # chapa xadrez 4,75 (+15 % dobras) + cantoneiras, kN/m² na rampa
G_PAT = 0.0063 * 78.5 * 10 / 10 * 1.0 + 0.0074 * 9.81 / 0.60  # chapa 6,3 + U 102 a cada 60 cm
LARG_LANCE = round((E["x_face_E"] - E["x_face_P6"] - 0.10) / 2, 3)     # dois lances lado a lado, 10 cm de folga entre eles
U152 = dict(nome="U 152 × 12,2 (6\")", A=15.5e-4, Ix=546e-8, Wx=71.7e-6, kg=12.2, d=0.152, bf=0.0485)
FY = 250e3                                                    # ASTM A36 nos U e cantoneiras; W em A572-50
GA1 = 1.10


def lance():
    Lh = E["y_lances"][1] - E["y_lances"][0]
    H = E["z_patamar"]
    L = math.hypot(Lh, H)
    w_area = 1.4 * (G_DEG * L / Lh) + 1.5 * Q                  # por m² de projeção horizontal
    w = w_area * LARG_LANCE / 2 + 1.4 * U152["kg"] * 9.81e-3 * L / Lh
    M = w * Lh ** 2 / 8
    MRd = 1.0 * U152["Wx"] * FY / GA1 * 1.0                    # U com mesa travada pelos degraus (FLT impedida); classe compacta em flexão x
    wk = (G_DEG * L / Lh + Q) * LARG_LANCE / 2
    flecha = 5 * wk * Lh ** 4 / (384 * 200e6 * U152["Ix"]) * (Lh / L) ** 0
    m_lin = (G_DEG + 0.3 * Q) * LARG_LANCE / 2 / 9.81 + U152["kg"] / 1000 * 1000 / 1000
    f1 = math.pi / (2 * L ** 2) * math.sqrt(200e6 * U152["Ix"] / max(m_lin, 1e-6))
    R = w * Lh / 2
    return dict(Lh=round(Lh, 3), L_inclinado=round(L, 3), largura=LARG_LANCE, w_d=round(w, 2), Md=round(M, 2), MRd=round(MRd, 2), uso=round(M / MRd, 3),
                flecha_mm=round(flecha * 1e3, 1), lim_L350_mm=round(Lh / 350 * 1e3, 1), f1_Hz=round(f1, 1), R_longarina_d=round(R, 1), perfil=U152["nome"])


def viga_patamar(vao, faixa, R_conc):
    """W 150 × 22,5 biapoiada: carga do patamar (faixa) + reações das longarinas (R_conc em kN, posições a vao/4 e 3vao/4)."""
    p = ML.perfil("W 150 x 22,5")
    w = (1.4 * G_PAT + 1.5 * Q) * faixa + 1.4 * p.peso
    M = w * vao ** 2 / 8 + sum(R_conc) / 2 * vao / 4
    MRd = ML.momento_resistente(p, vao, 1.0).MRd
    V = w * vao / 2 + sum(R_conc) / 2
    wk = (G_PAT + Q) * faixa + p.peso
    fl = 5 * wk * vao ** 4 / (384 * 200e6 * p.Ix * 1e-8) + sum(R_conc) / 2 / 1.45 * vao ** 3 * 0.0171 / (200e6 * p.Ix * 1e-8)
    return dict(perfil="W 150 × 22,5", vao=round(vao, 3), Md=round(M, 2), MRd=round(MRd, 1), uso=round(M / MRd, 3), Vd=round(V, 1),
                flecha_mm=round(fl * 1e3, 1), lim_L350_mm=round(vao / 350 * 1e3, 1), R_apoio_d=round(V, 1))


def pilarete(N, h):
    p = ML.perfil("W 150 x 22,5")
    r = ML.verificar_barra(p, N=-N, KLx=h, KLy=h, Lb=h)
    return dict(perfil="W 150 × 22,5", h=round(h, 3), Nd=round(N, 1), NRd=round(r["NRd"], 1), uso=round(r["razao_interacao"], 3),
                base="chapa 200 × 200 × 12,5 + 4 chumbadores químicos M12 hef 100 no piso")


def pilarete_tubo(N, h):
    """pilarete entre os lances (vão livre de 10 cm entre as longarinas): tubo quadrado 80 × 80 × 4,75 A36 — NBR 8800:2024 5.3 (χ pela Fig. 4)."""
    A, I = 13.9e-4, 128e-8                                       # tubo 80 × 80 × 4,75 (A 13,9 cm², I 128 cm⁴)
    r = (I / A) ** 0.5
    lam0 = h / r / math.pi * (250e3 / 200e6) ** 0.5
    chi = 0.658 ** (lam0 ** 2) if lam0 <= 1.5 else 0.877 / lam0 ** 2
    NRd = chi * A * 250e3 / 1.10
    return dict(perfil="tubo quadrado 80 × 80 × 4,75", h=round(h, 3), Nd=round(N, 1), NRd=round(NRd, 1), uso=round(N / NRd, 3), lambda0=round(lam0, 2),
                base="chapa 150 × 150 × 12,5 + 4 chumbadores químicos M12 hef 100 no piso; topo com chapa 12,5 e 2 M16 na mesa inferior da viga")


def ligacao_face(R):
    """viga W 150 nas faces do pilar (P6, P7, P6 da linha 2, P2-L2): chapa de topo 12,5 + 4 barras roscadas M16 8.8 embutidas."""
    Rd = 4 * 0.4 * 800e3 * 157e-6 / 1.35                       # cisalhamento: 0,4 fub Ab / γa2 (NBR 8800:2024 6.3.3.2), rosca no plano
    return dict(Vd=round(R, 1), VRd=round(Rd, 1), uso=round(R / Rd, 3), detalhe="chapa de topo 12,5 × 150 × 250 + 4 barras roscadas M16 8.8 embutidas 150 mm com grampo")


if __name__ == "__main__":
    ln = lance()
    vao = E["x_face_E"] - E["x_face_P6"] - 0.02
    pat_f = viga_patamar(vao, (E["y_patamar"][1] - E["y_patamar"][0]) / 2, [2 * ln["R_longarina_d"], 2 * ln["R_longarina_d"]])
    pat_t = viga_patamar(vao, (E["y_patamar"][1] - E["y_patamar"][0]) / 2, [])
    ch_f = viga_patamar(vao, (E["y_chegada"][1] - E["y_chegada"][0]) / 2, [2 * ln["R_longarina_d"]])
    ch_t = viga_patamar(vao, (E["y_chegada"][1] - E["y_chegada"][0]) / 2, [])
    out = dict(
        geometria=dict(n_espelhos=E["n_esp"], espelho_m=round(E["espelho"], 4), piso_m=E["piso"], blondel_m=round(2 * E["espelho"] + E["piso"], 3),
                       z_patamar=round(E["z_patamar"], 3), largura_lance=ln["largura"], y_patamar=E["y_patamar"], y_lances=E["y_lances"], y_chegada=E["y_chegada"],
                       x_faces=(E["x_face_P6"], E["x_face_E"])),
        cargas=dict(q_kN_m2=Q, g_degraus=round(G_DEG, 3), g_patamar=round(G_PAT, 3), norma="NBR 6120:2019 (escada com acesso público 3,0 kN/m²)"),
        longarina=ln, patamar_frente=pat_f, patamar_fundo=pat_t, chegada_frente=ch_f, chegada_fundo=ch_t,
        pilaretes=[pilarete(pat_f["R_apoio_d"], E["z_patamar"] - 0.152), pilarete(ch_f["R_apoio_d"], 3.90 - 0.152), pilarete_tubo(2 * ch_f["R_apoio_d"], 3.90 - 0.152)],
        chegada_apoios=dict(x_tubo=round(E["x_face_P6"] + LARG_LANCE + 0.05, 3), x_W=round(E["x_face_E"] - 0.09, 3),
                            obs="viga de frente da chegada: apoio no tubo entre os lances e no pilarete W 150 do lado E; balanço de 1,45 m sobre a entrada do lance 1 (o M do balanço = M do vão de 2,9 m usado na verificação)"),
        ligacoes_face=[ligacao_face(max(pat_t["R_apoio_d"], ch_t["R_apoio_d"]))],
        pe_do_lance=dict(Rd=ln["R_longarina_d"], detalhe="chapa de base 200 × 150 × 12,5 soldada de fábrica na longarina + 2 chumbadores químicos M12 hef 100 no piso"),
        lista=[dict(item="LG-1", desc="longarina U 152 × 12,2 (6\")", qt=4, L_m=ln["L_inclinado"] + 0.10, kg_m=U152["kg"]),
               dict(item="VP-1", desc="viga W 150 × 22,5 dos patamares", qt=4, L_m=round(vao, 3), kg_m=22.5),
               dict(item="PL-1", desc="pilarete W 150 × 22,5 (patamar +1,95)", qt=2, L_m=round(E["z_patamar"] - 0.152, 3), kg_m=22.5),
               dict(item="PL-2", desc="pilarete W 150 × 22,5 (chegada +3,90, lado E)", qt=1, L_m=round(3.90 - 0.152, 3), kg_m=22.5),
               dict(item="PL-3", desc="pilarete tubo quadrado 80 × 80 × 4,75 (chegada +3,90, entre os lances)", qt=1, L_m=round(3.90 - 0.152, 3), kg_m=10.9),
               dict(item="BR-1", desc="barrote U 102 × 7,4 (4\") dos patamares a cada 60 cm", qt=12, L_m=1.56, kg_m=7.4),
               dict(item="DG-1", desc="degrau chapa xadrez 4,75 dobrada 1300 × 330", qt=20, L_m=1.30, kg_m=round(0.33 * 4.75 * 7.85 * 1.0, 2)),
               dict(item="CT-1", desc="cantoneira L 38 × 38 × 4,8 de apoio do degrau (2 por degrau)", qt=40, L_m=0.30, kg_m=2.68),
               dict(item="CH-P", desc="chapa xadrez 6,3 dos patamares", qt=2, L_m=round(vao, 3), kg_m=round(1.56 * 6.3 * 7.85, 1))],
    )
    out["ok"] = all(x["uso"] <= 1.0 for x in (ln, pat_f, pat_t, ch_f, ch_t, *out["pilaretes"], *out["ligacoes_face"])) and ln["flecha_mm"] <= ln["lim_L350_mm"]
    out["massa_kg"] = round(sum(i["qt"] * i["L_m"] * i["kg_m"] for i in out["lista"]))
    (AQ / "escada_metalica.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1)[:3000])
