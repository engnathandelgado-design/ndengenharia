"""Letsara rev09c (24/10/2026) — escada METÁLICA EXTERNA da fachada A (DEC-053, decisão do Nathan: opção B — entra no projeto).

Arquitetônico do cliente (DWG R01, bloco 55555 / 47893): escada em L encostada na fachada A, do pátio à porta do 2º pavimento
(+3,90), largura 1,50 m, piso 28 cm, 22 espelhos de 17,73 cm: lance de baixo com 5 espelhos (ao longo de x, para fora), patamar
1,50 × 1,50 a +0,886 na quina e lance de cima com 17 espelhos ao longo da fachada até o patamar de chegada (+3,90, y 0,20 a 2,44),
em frente à porta (y 0,89 a 1,79). Deslocada 15 cm para fora para passar livre das placas (face interna da escada em x = −0,45).

Estrutura (tudo parafusado, sem solda — padrão ND; galvanizada a fogo por ser externa):
  - lances: 2 longarinas por lance (perfil escolhido aqui: o mais leve que passa, regra do Nathan); degraus em chapa xadrez
    4,75 dobrada sobre cantoneiras L 38 × 38 × 4,8 parafusadas (2 M10 por ponta), como a escada interna;
  - patamares: piso em chapa xadrez 6,3 sobre barrotes U 102 × 7,4 a cada 60 cm; vigas de borda W (as longarinas chegam nelas);
  - pilaretes W nos 4 cantos de cada patamar, sobre blocos de concreto próprios (BE-1) com 4 chumbadores M16 — a escada NÃO apoia
    nas placas de fechamento;
  - estabilidade: a viga de borda interna do patamar de chegada é travada no P28 (pilar do canto linha 1 × eixo A) por um tirante
    rígido horizontal parafusado em 2 barras roscadas M16 embutidas na face do pilar; contraventamento em X (barras Ø12,5 com
    esticador) no plano externo (x = −1,95) entre os pilaretes do lance de cima.
Cargas: NBR 6120:2019 — escada com acesso público 3,0 kN/m²; guarda-corpo (por terceiros) 1,0 kN/m horizontal no topo (NBR 14718:2019).
Combinação ELU 1,4 G + 1,5 Q (NBR 8800:2024 4.7); flecha L/350 (piso, Anexo C, Tab. C.1); vibração f1 ≥ 5 Hz (conforto, referência).
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
from geometria import ESCADA_EXT as E

Q = json.loads((AQ / "cargas_mezanino.json").read_text(encoding="utf-8"))["escada"]["sobrecarga"]
G_DEG = 0.0475 * 78.5 / 10 * 1.15 + 0.10                      # chapa xadrez 4,75 (+15 % dobras) + cantoneiras (kN/m² na rampa)
G_PAT = 0.0063 * 78.5 + 0.0074 * 9.81 / 0.60                  # chapa 6,3 + U 102 a cada 60 cm
FY_U, GA1 = 250e3, 1.10
U = {  # perfis U laminados (ASTM A36) — Gerdau/catálogo: A, Ix, Wx, kg/m, d, bf
    "U 152 × 12,2 (6\")": dict(A=15.5e-4, Ix=546e-8, Wx=71.7e-6, kg=12.2, d=0.152, bf=0.0485),
    "U 203 × 17,1 (8\")": dict(A=21.8e-4, Ix=1356e-8, Wx=133.4e-6, kg=17.1, d=0.203, bf=0.0574),
    "U 254 × 22,7 (10\")": dict(A=29.0e-4, Ix=2800e-8, Wx=221.0e-6, kg=22.7, d=0.254, bf=0.0661),
}
ESP = E["espelho"]
Z_PAT = E["n_baixo"] * ESP
Z_TOPO = E["n_esp"] * ESP
B = E["largura"]


def longarina(Lh, H):
    """longarina biapoiada na projeção horizontal Lh, desnível H; metade da largura do lance por longarina."""
    L = math.hypot(Lh, H)
    res = []
    for nome, u in U.items():
        w = (1.4 * G_DEG * L / Lh + 1.5 * Q) * B / 2 + 1.4 * u["kg"] * 9.81e-3 * L / Lh
        M = w * Lh ** 2 / 8
        MRd = u["Wx"] * FY_U / GA1                          # mesa comprimida travada pelos degraus a cada 28 cm (FLT impedida)
        wk = (G_DEG * L / Lh + Q) * B / 2
        fl = 5 * wk * Lh ** 4 / (384 * 200e6 * u["Ix"])
        m_lin = ((G_DEG + 0.3 * Q) * B / 2 * 1000 / 9.81 + u["kg"]) * L / Lh   # kg/m
        f1 = math.pi / (2 * L ** 2) * math.sqrt(200e6 * u["Ix"] * 1000 / m_lin)
        r = dict(perfil=nome, Lh=round(Lh, 3), L_inclinado=round(L, 3), w_d=round(w, 2), Md=round(M, 2), MRd=round(MRd, 2), uso=round(M / MRd, 3),
                 flecha_mm=round(fl * 1e3, 1), lim_L350_mm=round(Lh / 350 * 1e3, 1), f1_Hz=round(f1, 1), R_d=round(w * Lh / 2, 1), kg_m=u["kg"])
        r["ok"] = r["uso"] <= 1.0 and r["flecha_mm"] <= r["lim_L350_mm"] and r["f1_Hz"] >= 5.0
        res.append(r)
    ok = [r for r in res if r["ok"]]
    return min(ok, key=lambda r: r["kg_m"]) if ok else max(res, key=lambda r: r["kg_m"]), res


def viga(vao, faixa, P_list, nomes=("W 150 x 13,0", "W 150 x 18,0", "W 150 x 22,5", "W 200 x 15,0", "W 200 x 19,3")):
    """viga de borda do patamar, biapoiada nos pilaretes: faixa do patamar + cargas concentradas das longarinas (P em kN, x)."""
    out = []
    for nm in nomes:
        p = ML.perfil(nm)
        w = (1.4 * G_PAT + 1.5 * Q) * faixa + 1.4 * p.peso
        M = w * vao ** 2 / 8 + sum(P * x * (vao - x) / vao for P, x in P_list)
        Ra = w * vao / 2 + sum(P * (vao - x) / vao for P, x in P_list)
        Rb = w * vao + sum(P for P, _ in P_list) - Ra
        MRd = ML.momento_resistente(p, vao, 1.0).MRd
        wk = (G_PAT + Q) * faixa + p.peso
        EI = 200e6 * p.Ix * 1e-8
        fl = 5 * wk * vao ** 4 / (384 * EI) + sum(P / 1.45 * vao ** 3 / (48 * EI) for P, _ in P_list)
        r = dict(perfil=nm.replace(" x ", " × "), vao=round(vao, 3), Md=round(M, 2), MRd=round(MRd, 1), uso=round(M / MRd, 3), R_a=round(Ra, 1), R_b=round(Rb, 1),
                 flecha_mm=round(fl * 1e3, 1), lim_L350_mm=round(vao / 350 * 1e3, 1), kg_m=p.peso / 9.81e-3)
        r["ok"] = r["uso"] <= 1.0 and r["flecha_mm"] <= r["lim_L350_mm"]
        out.append(r)
    ok = [r for r in out if r["ok"]]
    return min(ok, key=lambda r: r["kg_m"])


def pilarete(N, h, H=0.0, nomes=("W 150 x 13,0", "W 150 x 18,0", "W 150 x 22,5")):
    for nm in nomes:
        p = ML.perfil(nm)
        r = ML.verificar_barra(p, N=-N, Mx=H * h, KLx=h, KLy=h, Lb=h)
        if r["razao_interacao"] <= 1.0:
            return dict(perfil=nm.replace(" x ", " × "), h=round(h, 3), Nd=round(N, 1), Hd=round(H, 2), uso=round(r["razao_interacao"], 3), kg_m=round(p.peso / 9.81e-3, 1))
    raise ValueError("pilarete não passa")


def base_bloco(N, T=0.0):
    """bloco BE-1 de concreto C25 60 × 60 × 60 sob cada pilarete (sobre o terreno, tensão admissível adotada 150 kPa — CONFIRMAR com a
    sondagem); chapa de base 200 × 200 × 12,5 sobre graute 20 mm presa por 4 chumbadores químicos M16 hef 120 (pilarete parafusado na
    chapa por 2 cantoneiras L 102 × 102 × 9,5 × 200 — sem solda)."""
    A = 0.60 * 0.60
    peso = 25 * 0.6 ** 3
    sig = (N / 1.4 + peso) / A
    return dict(bloco="BE-1 60 × 60 × 60 C25 (armadura mínima: malha Ø8 c/15 em baixo + 4 Ø8 de estribo)", Nd=round(N, 1), sigma_solo_kPa=round(sig, 1),
                sigma_adm_kPa=150, uso=round(sig / 150, 3), chumbadores="4 químicos M16 hef 120 (cisalhamento da força horizontal; sem tração)",
                obs="tensão admissível do solo a confirmar na sondagem; se < 150 kPa, aumentar o bloco")


def main():
    Lh_cima = E["y_lance_cima"][1] - E["y_lance_cima"][0]
    H_cima = Z_TOPO - Z_PAT
    Lh_baixo = abs(E["x_lance_baixo"][1] - E["x_lance_baixo"][0])
    lc, lc_all = longarina(Lh_cima, H_cima)
    lb, _ = longarina(Lh_baixo, Z_PAT)
    # patamar de chegada (+3,90): vigas de borda ao longo de y (x_int e x_ext), vão = comprimento do patamar; a longarina do lance de
    # cima chega na viga transversal da ponta y = 2,44 (W de mesma família), que leva a reação às duas vigas de borda.
    vao_ch = E["y_chegada"][1] - E["y_chegada"][0]
    v_trans_ch = viga(B, 0.0, [(lc["R_d"], 0.0001), (lc["R_d"], B - 0.0001)])
    v_ch = viga(vao_ch, B / 2, [(v_trans_ch["R_a"], vao_ch - 0.0001)])
    # patamar intermediário (+0,886): 1,50 × 1,50; recebe o pé do lance de cima (y 6,92) e o topo do lance de baixo (x −1,95)
    vao_p = E["y_patamar"][1] - E["y_patamar"][0]
    v_p = viga(vao_p, B / 2, [(lc["R_d"], 0.0001), (lb["R_d"], vao_p / 2)])
    # guarda-corpo 1,0 kN/m a 1,10 m do piso → horizontal no topo do pilarete (aproximado) e força nocional 2 %
    H_gc = 1.0 * 1.5 * vao_ch / 2
    p_ch = pilarete(max(v_ch["R_a"], v_ch["R_b"]), Z_TOPO - 0.20, H=0.0)
    p_pat = pilarete(max(v_p["R_a"], v_p["R_b"]), Z_PAT - 0.20, H=0.0)
    trava = dict(F_d=round(1.5 * H_gc + 0.02 * 4 * p_ch["Nd"], 1), perfil="tubo 80 × 80 × 4,75 horizontal do patamar de chegada ao P28",
                 ligacao="2 barras roscadas M16 8.8 embutidas 150 mm na face do P28 (lado externo, z +3,80) + chapa 12,5 × 150 × 200 + 2 M16; na viga do patamar 2 M16",
                 Rd_barra=round(2 * 0.4 * 800e3 * 157e-6 / 1.35, 1))
    trava["uso"] = round(trava["F_d"] / trava["Rd_barra"], 3)
    contrav = dict(desc="X de barras redondas Ø12,5 com esticador e olhal parafusado (sem solda), plano x = −1,95, entre os pilaretes da chegada e do patamar",
                   F_d=round(0.02 * 4 * p_ch["Nd"] + 1.5 * 1.0 * 1.5, 1))
    contrav["uso"] = round(contrav["F_d"] * 1.5 / (0.75 * 400e3 * math.pi * 0.0125 ** 2 / 4 / 1.35), 3)
    base = base_bloco(max(p_ch["Nd"], p_pat["Nd"]))
    n_deg = E["n_esp"] - 2                                       # 20 degraus (2 espelhos chegam nos patamares)
    lista = [
        dict(item="LE-1", desc=f"longarina {lc['perfil']} — lance de cima", qt=2, L_m=round(lc["L_inclinado"] + 0.10, 3), kg_m=lc["kg_m"]),
        dict(item="LE-2", desc=f"longarina {lb['perfil']} — lance de baixo", qt=2, L_m=round(lb["L_inclinado"] + 0.10, 3), kg_m=lb["kg_m"]),
        dict(item="VE-1", desc=f"viga de borda {v_ch['perfil']} — patamar de chegada +3,90", qt=2, L_m=round(vao_ch, 3), kg_m=round(v_ch["kg_m"], 1)),
        dict(item="VE-2", desc=f"viga transversal {v_trans_ch['perfil']} — chegada (recebe o lance)", qt=1, L_m=B, kg_m=round(v_trans_ch["kg_m"], 1)),
        dict(item="VE-3", desc=f"viga de borda {v_p['perfil']} — patamar +0,89", qt=4, L_m=round(vao_p, 3), kg_m=round(v_p["kg_m"], 1)),
        dict(item="PE-1", desc=f"pilarete {p_ch['perfil']} — patamar de chegada", qt=4, L_m=round(Z_TOPO - 0.20, 3), kg_m=p_ch["kg_m"]),
        dict(item="PE-2", desc=f"pilarete {p_pat['perfil']} — patamar +0,89", qt=4, L_m=round(Z_PAT - 0.20, 3), kg_m=p_pat["kg_m"]),
        dict(item="BE-U", desc="barrote U 102 × 7,4 (4\") dos patamares a cada 60 cm", qt=7, L_m=B, kg_m=7.4),
        dict(item="DE-1", desc="degrau chapa xadrez 4,75 dobrada 1480 × 330", qt=n_deg, L_m=1.48, kg_m=round(0.33 * 4.75 * 7.85, 2)),
        dict(item="CE-1", desc="cantoneira L 38 × 38 × 4,8 de apoio do degrau (2 por degrau)", qt=2 * n_deg, L_m=0.30, kg_m=2.68),
        dict(item="CHE", desc="chapa xadrez 6,3 dos patamares", qt=1, L_m=round(vao_ch + vao_p, 3), kg_m=round(B * 6.3 * 7.85, 1)),
        dict(item="TR-1", desc="tubo 80 × 80 × 4,75 — trava do patamar de chegada ao P28", qt=1, L_m=0.45, kg_m=10.9),
        dict(item="XE-1", desc="barra redonda Ø12,5 com esticador (contraventamento em X)", qt=4, L_m=4.9, kg_m=0.96),
        dict(item="CBE", desc="chapa de base 200 × 200 × 12,5 dos pilaretes", qt=8, L_m=0.20, kg_m=round(0.20 * 12.5 * 7.85, 1)),
        dict(item="CT-E", desc="cantoneira L 102 × 102 × 9,5 × 200 (base dos pilaretes) e L 76 × 76 × 6,3 × 150 (ligações vigas/longarinas)", qt=40, L_m=0.17, kg_m=10.0),
    ]
    out = dict(geometria=dict(espelho_m=round(ESP, 4), piso_m=E["piso"], blondel_m=round(2 * ESP + E["piso"], 3), z_patamar=round(Z_PAT, 3), z_chegada=round(Z_TOPO, 3),
                              largura=B, x=(E["x_int"], E["x_ext"]), y_chegada=E["y_chegada"], y_lance_cima=E["y_lance_cima"], y_patamar=E["y_patamar"],
                              x_lance_baixo=E["x_lance_baixo"], porta_y=E["porta_y"], deslocamento_vs_arquitetonico_m=0.15),
               cargas=dict(q_kN_m2=Q, g_degraus=round(G_DEG, 3), g_patamar=round(G_PAT, 3), guarda_corpo_kN_m=1.0,
                           norma="NBR 6120:2019 (escada com acesso público 3,0 kN/m²); NBR 14718:2019 (guarda-corpo, por terceiros)"),
               longarina_cima=lc, longarina_baixo=lb, alternativas_longarina_cima=lc_all, viga_chegada=v_ch, viga_transversal_chegada=v_trans_ch, viga_patamar=v_p,
               pilarete_chegada=p_ch, pilarete_patamar=p_pat, trava_P28=trava, contraventamento=contrav, base=base, lista=lista,
               acabamento="galvanização a fogo (NBR 6323) de todas as peças, parafusos galvanizados; chumbadores químicos para uso externo")
    out["ok"] = all(x["uso"] <= 1.0 for x in (lc, lb, v_ch, v_trans_ch, v_p, p_ch, p_pat, trava, contrav, base))
    out["massa_kg"] = round(sum(i["qt"] * i["L_m"] * i["kg_m"] for i in lista))
    (AQ / "escada_externa.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    return out


if __name__ == "__main__":
    o = main()
    for k in ("longarina_cima", "longarina_baixo", "viga_chegada", "viga_transversal_chegada", "viga_patamar", "pilarete_chegada", "pilarete_patamar", "trava_P28", "contraventamento", "base"):
        print(k, {a: b for a, b in o[k].items() if a in ("perfil", "uso", "flecha_mm", "lim_L350_mm", "f1_Hz", "Nd", "R_d", "R_a", "R_b", "F_d", "sigma_solo_kPa")})
    print("ok", o["ok"], "massa", o["massa_kg"], "kg")
