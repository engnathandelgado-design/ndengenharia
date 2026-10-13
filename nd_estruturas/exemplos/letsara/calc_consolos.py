"""Letsara — consolos de apoio das vigas (NBR 9062:2017 item 7.3), com a regra de projeto pedida pelo Nathan (12/10/2026):

    a altura do consolo é pelo menos a do recorte do dente da viga (altura da viga − altura do dente − neoprene), para que o
    fundo do consolo fique alinhado com o fundo da viga (sem chanfro na ponta). Quando essa altura não basta (a/d > 1, biela ou
    tirante acima do razoável para a largura), acrescenta-se uma mísula de concreto 45° abaixo do consolo.

Modelo biela-tirante de consolo curto/muito curto: As,tir = Vd·a/(0,9·d·fyd) + Hd/fyd (Hd ≥ 0,2·Vd sem ligação que impeça o
deslizamento — NBR 9062:2017 7.3.1, conferir); τwd = Vd/(b·d) ≤ τwu = min(0,27·αv2·fcd ; 6 MPa) (conferir 7.3.2.2).
Unidades: kN, m, MPa.
"""
import json, math
from pathlib import Path

AQ = Path(__file__).parent
I110 = json.loads((AQ / "i110_r01.json").read_text(encoding="utf-8"))
DT = json.loads((AQ / "dentes.json").read_text(encoding="utf-8"))
fyd = 500 / 1.15
BAR = {16: 2.011, 20: 3.142, 12.5: 1.227, 10: 0.785}

# tipo: (onde, b, proj, a (face → eixo do pino), h_viga, h_dente, neoprene, Vd, fck do pilar/viga que recebe)
CONS = {
    "CP-TS":  ("pilares PL (eixos A/E) e P8A/P11 — apoio da TS-01", 0.40, 0.30, 0.175, 0.90, 0.45, 0.010, DT["TS-01"]["Vd"], 40),
    "CV-TS":  ("I110 (linhas 3, 5, 6, 7, 8) — apoio da TS-01 (b = apoio da TS, maciço de 100 cm)", 0.40, 0.35, 0.200, 0.90, 0.45, 0.010, DT["TS-01"]["Vd"], 50),
    "CP-I110": ("P8A, P11, P13, P14 — apoio da I110", 0.50, 0.40, 0.200, 1.10, 0.66, 0.030, max(v["linhas"]["Vd_kN"] for v in I110.values()), 40),
    "CP-MEZ": ("PL linha 1/2, P3/P4/P5, P8/P8B — apoio da VM I90", 0.40, 0.30, 0.150, 0.90, 0.45, 0.010, 383.0, 40),
    "CP-VT":  ("pilares laterais e de portão — apoio da VT/VV 25×60", 0.25, 0.20, 0.10, 0.60, 0.30, 0.010, 49.0, 40),
    "CP-VB":  ("pilares das fachadas 1 e 9 — apoio da VB 15×90 (sem dente: consolo de 35 cm sem chanfro)", 0.30, 0.30, 0.150, 0.70, 0.35, 0.0, 35.0, 40),
}
res = {}
for nome, (onde, b, proj, a, hv, hd, neo, Vd, fck) in CONS.items():
    fcd = fck / 1.4
    tau_wu = min(0.27 * (1 - fck / 250) * fcd, 6.0)
    Hd = 0.2 * Vd
    h0 = round(hv - hd - neo, 3)                       # altura que deixa o fundo do consolo alinhado com o fundo da viga
    out = None
    for misula in (0.0, 0.15, 0.25, 0.35):
        h = h0 + misula
        d = h - 0.05
        ad = a / d
        tau = Vd / (b * d) / 1000
        As = (Vd * a / (0.9 * d) + Hd) / fyd * 10       # cm²
        As = max(As, 0.04 * fcd / fyd * b * d * 1e4)   # NBR 9062:2017 7.3.3 — ρ,min = 0,04 fcd/fyd (conferir)
        # bitolas: até 4 Ø16 em b ≤ 0,40; até 5 Ø16 em b = 0,50
        nmax = 3 if b <= 0.30 else 4                 # acima disso usa mísula (prática ND: tirante em uma camada, até 4 barras)
        esc = None
        for dd in ((16, 20) if b >= 0.40 else (12.5, 16)):
            n = max(2, math.ceil(As / BAR[dd]))
            if n <= nmax:
                esc = (n, dd)
                break
        ok = ad <= 1.0 and tau <= tau_wu and esc is not None
        out = dict(onde=onde, b_m=b, proj_m=proj, a_m=a, h_recorte_viga_m=round(hv - hd, 3), h_consolo_m=round(h0, 3), misula_m=misula,
                   h_total_m=round(h, 3), d_m=round(d, 3), a_d=round(ad, 2), tipo="muito curto" if ad <= 0.5 else "curto",
                   Vd_kN=round(Vd, 1), Hd_kN=round(Hd, 1), tau_wd_MPa=round(tau, 2), tau_wu_MPa=round(tau_wu, 2),
                   As_tir_cm2=round(As, 2), tirante=f"{esc[0]} Ø{esc[1]:g}".replace(".", ",") if esc else "-",
                   As_ef_cm2=round(esc[0] * BAR[esc[1]], 2) if esc else 0, ok=ok)
        if ok:
            break
    res[nome] = out
    print(f"{nome:8s} h={out['h_consolo_m']} mísula={out['misula_m']} a/d={out['a_d']} τ={out['tau_wd_MPa']}/{out['tau_wu_MPa']} As={out['As_tir_cm2']} → {out['tirante']} ok={out['ok']}")
(AQ / "consolos.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
