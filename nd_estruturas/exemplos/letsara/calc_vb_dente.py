"""Letsara rev04 — vigas de borda VB das fachadas 1 e 9 COM DENTE GERBER (pedido do Nathan, 16/10/2026: ganhar altura livre
embaixo; testar alturas menores). O topo da VB fica fixo (apoio das terças do vão de oitão); o consolo CP-VB fica escondido no
recorte do dente (fundo do consolo = fundo da viga) e com a mesma largura da viga.

Varredura: b = 15 e 20 cm; h = 90 a 40 cm de 5 em 5; hd de 5 em 5 (hd ≥ h/2). Verificações por variante:
  - flexão ELU (gravidade 1,4·(g+q)) + tração do modelo global (ELU-1 vento x, 95,8 kN) — NBR 6118:2023 17.2;
  - sucção da cobertura (faixa de borda, cp −1,6, γ 1,4, peso favorável 1,0) → momento negativo e levantamento no apoio;
  - cortante (NBR 6118:2023 17.4.2.2, modelo I, Vc = 0 por haver tração);
  - flecha diferida (Branson, αf NBR 6118:2023 17.3.2.1.2) ≤ L/250 (NBR 9062:2017 Tab. 8, cobertura sem empoçamento);
  - fissuração ELS-W pela Tab. 17.2 da NBR 6118:2023 (wk 0,3 mm, CAA II);
  - estabilidade lateral NBR 9062:2017 6.1 (Lebelle FS ≥ 2,5 quando L/bf > 50);
  - dente e consolo escondido (NBR 9062:2017 7.4 → 7.3, γn 1,1 com permanente preponderante), suspensão Fd/fyd;
  - neoprene NBR 9062:2017 7.2.1.6 (pressão, Nmin, distorção, levantamento).
Esforços laterais do modelo global (rev04, mesmo modelo com captura dos momentos da VB): Mz no plano horizontal ≤ 2,2 kN·m
(desprezível); T ≤ 12 kN·m vem do acoplamento de rotação imposto no modelo (equalDOF) e não existe na ligação real por pino.
"""
import json, math, sys
from pathlib import Path
AQ = Path(__file__).parent
sys.path.insert(0, str(AQ.parents[1]))
from nd_estruturas.prefabricados import Concreto

C40 = Concreto(40)
FCK, FYD, FCD = 40.0, 500 / 1.15, 40 / 1.4
FCTM = 0.3 * FCK ** (2 / 3)
GN, G_NEO = 1.1, 1.0
L_PECA = 9.43                         # VB-02/03 (maior), m
FOLGA, A_PAD = 0.025, 0.10           # ponta da viga a 2,5 cm da face do pilar; neoprene 100 na direção do vão
X_PAD = FOLGA + 0.06 + A_PAD / 2       # 6 cm da ponta da viga à borda do neoprene (a2 ≥ c + 3,5Ø com alça Ø10 no nariz) → centro a 13,5 cm
LN = PROJ = 0.27                      # nariz do dente = projeção do consolo (folga de 2,5 cm entre a ponta do consolo e o recorte)
A_DENTE = FOLGA + LN - X_PAD
TRIB = 9.63 / 2                       # faixa de cobertura que apoia na VB (vão de oitão L1–L2)
G_TERCA, Q_COB = 0.495, 0.25          # kN/m² (rev03, com painéis solares) e sobrecarga de cobertura
G_FAV, CP_SUC, Q0 = 0.158 + 0.087, -1.6, 0.874   # sucção: telha+isolamento+fixações+terça; faixa de borda; kN/m²
N_TRACAO = 95.8                       # kN, ELU-1 vento x (modelo_global_r04)
ADOTADO = (0.15, 0.60, 0.30)          # rev04: VB 15 × 60, dente 30 (Nathan, 16/10/2026)
PRECO = dict(concreto=1800.0, aco=9.0)
AREA = {10.0: 0.785, 12.5: 1.227, 16.0: 2.011, 20.0: 3.142}


def barras(As, b):
    """Menor arranjo (até 2 camadas) com Ø ≤ 16 que cabe em b (cobrimento 3, estribo 6,3, espaçamento ≥ Ø e 2 cm)."""
    for d in (10.0, 12.5, 16.0):
        livre = b * 100 - 2 * 3.0 - 2 * 0.63
        n_cam = int((livre + max(d / 10, 2.0)) // (d / 10 + max(d / 10, 2.0)))
        for n in range(2, 2 * n_cam + 1):
            if n * AREA[d] >= As:
                cam = 1 if n <= n_cam else 2
                return dict(n=n, d=d, As=round(n * AREA[d], 2), camadas=cam, txt=f"{n} Ø{d:g}".replace(".", ","))
    return None


def consolo(b, proj, h, a, Fd, c=2.5):
    """NBR 9062:2017 7.3 — muito curto (a/d ≤ 0,5) ou curto (0,5 < a/d ≤ 1); tirante em alças horizontais."""
    Hd = 0.16 * Fd
    d = h - 0.05
    if d <= 0.10:
        return None
    ad = a / d
    if ad > 1.0:
        return None
    Asv = 0.8 * Fd / (FYD * 1.4) * 10 if ad <= 0.5 else (0.1 + ad) * Fd / FYD * 10
    As = max(Asv + Hd / FYD * 10, 0.04 * FCK / 500 * b * d * 1e4)
    a2 = round(proj - (a + A_PAD / 2), 4)
    esc = None
    for dd in (10.0, 12.5, 16.0):
        if round(a2 * 100, 2) < round(c + 3.5 * dd / 10, 2):
            continue
        for n in (2, 4):
            esp = (b * 100 - 2 * c - dd / 10) / (n - 1)
            if n * AREA[dd] >= As and esp >= dd / 10 + 2.0 and esp <= min(15 * dd / 10, d * 100):
                esc = (n, dd, n * AREA[dd])
                break
        if esc:
            break
    rho = (esc[2] if esc else As) / (b * d * 1e4)
    tau = Fd / (b * d) / 1e3
    tau_u = min(3.0 + 0.9 * rho * FYD, 0.27 * (1 - FCK / 250) * FCD, 8.0) if ad <= 0.5 else 0.27 * (1 - FCK / 250) * FCD
    return dict(h=round(h, 2), d=round(d, 3), a_d=round(ad, 2), As=round(As, 2),
                tirante=(f"{esc[0]//2} alça{'s' if esc[0] > 2 else ''} Ø{esc[1]:g} ({esc[2]:.2f} cm²)".replace(".", ",") if esc else "-"),
                tau=round(tau, 2), tau_u=round(tau_u, 2), a2_cm=round(a2 * 100, 1), ok=esc is not None and tau <= tau_u)


def neo(a, b, h, Ng, Nq, ah, thg, thq):
    """NBR 9062:2017 7.2.1.6.18 a 7.2.1.6.23 (simples, G = 1,0 MPa)."""
    A = a * b
    Al = (a - ah) * b
    S = A / (2 * (a + b) * h)
    sg, sgq = Ng * 1e3 / Al, (Ng + Nq) * 1e3 / Al
    h1, h2 = h * sg / (10 * G_NEO * S + 2 * sg), h * sgq / (10 * G_NEO * S + 2 * sgq)
    Hk = G_NEO * A * ah / h / 1e3
    desl = max(Hk / ((0.1 + 0.6 / sg) * Ng), Hk / ((0.1 + 0.6 / sgq) * (Ng + Nq)))
    ok = dict(pressao=(Ng + Nq) * 1e3 / A <= 7.0, Nmin=sg >= 1 + a / b, distorcao=ah <= 0.5 * h, deslizamento=desl <= 0.85,
              levantamento=math.tan(thg) + 1.5 * math.tan(thq) < 2 * h2 / a and math.tan(thg) < 2 * h1 / a, estabilidade=h < a / 5)
    return dict(nome=f"{a:.0f}×{b:.0f}×{h:.0f}", sigma=round((Ng + Nq) * 1e3 / A, 2), sigma_g=round(sg, 2), lim_Nmin=round(1 + a / b, 2),
                ok=all(ok.values()), detalhe=ok)


def tab_17_2(d):
    """NBR 6118:2023 Tab. 17.2, wk ≤ 0,3 mm: tensão máxima no aço (MPa) para o Ø da barra."""
    return {10.0: 360, 12.5: 320, 16.0: 280, 20.0: 240}[d]


def variante(b, h, hd):
    L = L_PECA
    pp = 25 * b * h
    g, q = pp + G_TERCA * TRIB, Q_COB * TRIB
    Md = 1.4 * (g + q) * L ** 2 / 8
    Vd = 1.4 * (g + q) * L / 2
    w_up = 1.4 * abs(CP_SUC) * Q0 * TRIB - 1.0 * (G_FAV * TRIB + pp)       # kN/m (positivo = para cima)
    Md_neg = max(w_up, 0) * L ** 2 / 8
    R_up = max(w_up, 0) * L / 2
    # flexão + tração (NBR 6118 17.2.2): As = Md/(z·fyd) + N/(2·fyd), z = 0,9 d
    d1 = h - 0.03 - 0.0063 - 0.008
    As_inf = Md / (0.9 * d1 * FYD) * 10 + N_TRACAO / (2 * FYD) * 10
    As_min = 0.15 / 100 * b * h * 1e4 * 1.0                                 # ρmin C40 = 0,179 % (Tab. 17.3) → usar 0,179
    As_min = 0.179 / 100 * b * h * 1e4
    bi = barras(max(As_inf, As_min), b)
    if not bi:
        return None
    d_ = h - 0.03 - 0.0063 - bi["d"] / 2000 - (0.5 * (bi["d"] / 1000 + 0.02) if bi["camadas"] == 2 else 0)
    As_inf = Md / (0.9 * d_ * FYD) * 10 + N_TRACAO / (2 * FYD) * 10
    bi = barras(max(As_inf, As_min), b)
    As_sup = max(Md_neg / (0.9 * d_ * FYD) * 10 + N_TRACAO / (2 * FYD) * 10, As_min)
    bs = barras(As_sup, b)
    x = 1.25 * d_ * (1 - math.sqrt(max(1 - Md / (0.425 * b * d_ ** 2 * FCD * 1e3), 0.0)))
    ok_x = x / d_ <= 0.45
    # cortante (17.4.2.2), modelo I, Vc = 0 (tração)
    VRd2 = 0.27 * (1 - FCK / 250) * FCD * 1e3 * b * d_
    Asw = max(Vd / (0.9 * d_ * FYD) * 10, 0.2 * FCTM / 500 * b * 100 * 100)    # cm²/m
    # flecha (17.3.2.1): Branson + αf
    Ec = C40.Ecs                                                             # kPa
    I = b * h ** 3 / 12
    Mr = 1.5 * FCTM * 0.7 * 1e3 * I / (h / 2)                                # fctk,inf (17.3.1)
    ae = 200e6 / Ec
    As_m = bi["As"] * 1e-4
    xII = (-ae * As_m + math.sqrt((ae * As_m) ** 2 + 2 * b * ae * As_m * d_)) / b
    III = b * xII ** 3 / 3 + ae * As_m * (d_ - xII) ** 2
    Ma = g * L ** 2 / 8                                                      # quase permanente (ψ2 = 0 na cobertura)
    Ie = min(I, (Mr / Ma) ** 3 * I + (1 - (Mr / Ma) ** 3) * III) if Ma > Mr else I
    f0 = 5 * g * L ** 4 / (384 * Ec * Ie) * 1000
    af = 1.32 / (1 + 50 * bs["As"] * 1e-4 / (b * d_))
    flecha = f0 * (1 + af)
    # fissuração (ELS-W, frequente g + 0·q na cobertura; usado g + 0,3q a favor da segurança)
    Mf = (g + 0.3 * q) * L ** 2 / 8
    sig_s = Mf / ((d_ - xII / 3) * As_m) / 1e3 + 0.3 * 20.1 / (bi["As"] * 1e-4) / 1e3 / 2   # + ELS vento x 20,1 kN
    ok_w = sig_s <= tab_17_2(bi["d"])
    # estabilidade lateral (6.1)
    Iy, J = h * b ** 3 / 12, h * b ** 3 / 3 * (1 - 0.63 * b / h)
    Ej = 0.85 * 5600 * math.sqrt(25) * 1e3
    FS = 28.3 * math.sqrt(Ej * Iy * Ej / 2.4 * J) / L ** 3 / (1.3 * pp)
    crit = L / b <= 50 and L * h / b ** 2 <= 500
    # dente e consolo escondido
    Fd = GN * Vd
    if hd < h / 2 - 1e-9 or h - hd < 0.21 - 1e-9:
        return None
    den = consolo(b, LN, hd, A_DENTE, Fd)
    con = consolo(b, PROJ, h - hd - 0.010, X_PAD, Fd)
    if not den or not con:
        return None
    As_sus = Fd / FYD * 10
    sus = barras(As_sus / 2, b)                   # estribos de 2 ramos junto ao recorte
    # neoprene: ladeado de 1,5 cm na largura; tenta 100×(b−3) e 80×(b−3)
    Ng, Nq = g * L / 2, q * L / 2
    EI = 0.5 * Ec * I
    thg, thq = g * L ** 3 / (24 * EI) * 3.0, q * L ** 3 / (24 * EI)
    ah = 35e-5 * L / 2 * 1000
    bn = min(100.0, b * 1000 - 30)
    n_ok = None
    for a_n in (100.0, 80.0, 60.0):
        r = neo(a_n, bn, 10.0, Ng, Nq, ah, thg, thq)
        if r["ok"]:
            n_ok = r
            break
    pino = dict(R_up_d=round(R_up, 1), cap_PN1_d=round(2.45 * 25 / 1.15, 1), ok=R_up <= 2.45 * 25 / 1.15)   # PN-1 Ø20 roscado ASTM A36 (área útil da rosca 2,45 cm²)
    ok = all([bi, bs, ok_x, Vd <= VRd2, flecha <= L * 1000 / 250, ok_w, crit or FS >= 2.5, den["ok"], con["ok"], sus, n_ok, pino["ok"]])
    V = b * h * L - 2 * b * (h - hd) * LN
    kg = (bi["As"] + bs["As"]) * 1e-4 * L * 7850 * 1.1 + Asw * 1e-4 * 2 * (b + h) * L * 7850 * 1.3 + 2 * (den["As"] + As_sus) * 1e-4 * 1.2 * 7850 + 0.0158 * h * L * 2 * 2 / 0.3 * 0 \
        + (4 * 0.395 * L if h >= 0.60 else 0)                               # pele 2 Ø8 por face quando h ≥ 60
    custo = V * PRECO["concreto"] + kg * PRECO["aco"]
    ganho = (0.90 + 0.35 + 0.01) - h
    return dict(b=b, h=h, hd=hd, recorte=round(h - hd, 2), consolo_h=round(h - hd - 0.01, 2), ok=bool(ok), pp=round(pp, 2), g=round(g, 2), q=round(q, 2),
                Md=round(Md, 1), Vd=round(Vd, 1), Md_neg=round(Md_neg, 1), R_up_d=round(R_up, 1), d=round(d_, 3),
                As_inf=round(As_inf, 2), inf=bi["txt"] + (" (2 camadas)" if bi["camadas"] == 2 else ""), As_sup=round(As_sup, 2), sup=bs["txt"] if bs else "-",
                x_d=round(x / d_, 2), VRd2=round(VRd2, 1), Asw_cm2m=round(Asw, 2), flecha_mm=round(flecha, 1), flecha_lim=round(L * 1000 / 250, 1),
                sigma_s=round(sig_s), sigma_lim=tab_17_2(bi["d"]), L_bf=round(L / b, 1), Lh_bf2=round(L * h / b ** 2), FS_lebelle=round(FS, 1),
                dente=den, consolo=con, suspensao=(f"{sus['n']} estribos Ø{sus['d']:g} (2 ramos) ≥ {As_sus:.2f} cm²".replace(".", ",") if sus else "-"),
                neoprene=n_ok, pino=pino, V_m3=round(V, 3), peso_t=round(V * 2.5, 2), kg_aco=round(kg, 1), custo_indice=round(custo),
                fundo_rel_topo=-h, ganho_altura_livre_m=round(ganho, 2))


if __name__ == "__main__":
    res, todos = [], []
    for b in (0.15, 0.20):
        for h in [round(0.90 - 0.05 * k, 2) for k in range(11)]:
            melhor = None
            for hd in [round(0.20 + 0.05 * k, 2) for k in range(15) if 0.20 + 0.05 * k <= h - 0.21 + 1e-9]:
                s = variante(b, h, hd)
                if s and s["ok"] and (melhor is None or s["custo_indice"] < melhor["custo_indice"]):
                    melhor = s
            todos.append((b, h, melhor))
            if melhor:
                res.append(melhor)
    for b, h, s in todos:
        if s:
            print(f"b{b*100:.0f} h{h*100:.0f} hd{s['hd']*100:.0f} cons{s['consolo_h']*100:.0f} inf {s['inf']:<20} sup {s['sup']:<8} flecha {s['flecha_mm']:5.1f}/{s['flecha_lim']}"
                  f" σs {s['sigma_s']}/{s['sigma_lim']} FS {s['FS_lebelle']:5.1f} dente {s['dente']['tirante']} consolo {s['consolo']['tirante']} neo {s['neoprene']['nome']}"
                  f" Rup {s['R_up_d']} V {s['V_m3']} custo {s['custo_indice']} ganho {s['ganho_altura_livre_m']}")
        else:
            print(f"b{b*100:.0f} h{h*100:.0f}: não passa")
    ref = variante(0.15, 0.90, 0.55)
    adot = variante(*ADOTADO)
    res.sort(key=lambda s: s["custo_indice"])
    (AQ / "vb_dente.json").write_text(json.dumps(dict(adotado=adot, melhor=res[0] if res else None, ranking=res, referencia_15x90=ref), indent=1, ensure_ascii=False, default=str),
                                     encoding="utf-8")
