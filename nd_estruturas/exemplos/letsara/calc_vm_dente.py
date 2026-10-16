"""Letsara rev04 — VM meio vaso COM DENTE GERBER (preferência ND: fundo do consolo alinhado ao fundo da viga, sem perder
pé-direito). Varredura de largura da alma e altura da peça de 5 em 5 cm (pedido do Nathan, 16/10/2026) e escolha da solução
mais econômica que passa em tudo:
  - viga (calc_vm_meio_vaso.analisar): ELU F1/F2, ELS-F/D, ato, flecha, cortante, interface, torção de montagem, içamento;
  - dente (NBR 9062:2017 7.4 = consolo 7.3) na ponta maciça (largura total da peça, 1,0 m);
  - consolo CP-MEZ com altura = recorte − neoprene (fundo alinhado), NBR 9062 7.3;
  - suspensão Fd/fyd (fyd ≤ 435 MPa) junto ao recorte.
Geometria do apoio: folga 3 cm; neoprene NEO-5 150 × 300 × 10 com a2 ≥ c + 3,5Ø (alças Ø16) dos dois lados:
consolo com projeção 35, nariz do dente LN = 35, neoprene a 11,1–26,1 cm da face do pilar (centro 18,6).
"""
import json, math, sys
from pathlib import Path
AQ = Path(__file__).parent
sys.path.insert(0, str(AQ.parents[1]))
import calc_vm_meio_vaso as M

FOLGA, LN, PROJ, A_PAD, B_PAD = 0.03, 0.35, 0.35, 0.15, 0.30
X_PAD = 0.111 + A_PAD / 2                     # centro do neoprene a 18,6 cm da face do pilar
A_CONS = X_PAD
A_DENTE = FOLGA + LN - X_PAD
FYD, GN = 500 / 1.15, 1.2
PRECO = dict(concreto=1800.0, cordoalha=15.0, aco=9.0)   # R$/m³ instalado na fábrica (fôrma+produção) e R$/kg (índice de comparação)


def consolo(b, proj, h, a, Fd, c=2.5):
    """NBR 9062:2017 7.3 — muito curto (a/d ≤ 0,5) ou curto (0,5 < a/d ≤ 1); tirante em alças horizontais."""
    fcd = 40 / 1.4
    Hd = 0.16 * Fd
    d = h - 0.05
    ad = a / d
    if ad > 1.0 or d <= 0.1:
        return None
    Asv = 0.8 * Fd / (FYD * 1.4) * 10 if ad <= 0.5 else (0.1 + ad) * Fd / FYD * 10
    As = max(Asv + Hd / FYD * 10, 0.04 * 40 / 500 * b * d * 1e4)
    a2 = round(proj - (a + A_PAD / 2), 4)
    esc = None
    for dd, ar in ((12.5, 1.227), (16, 2.011), (20, 3.142)):
        if round(a2 * 100, 2) < round(c + (3.5 if dd < 20 else 5.0) * dd / 10, 2):
            continue
        for n in (2, 4, 6, 8):
            esp = (b * 100 - 2 * c - dd / 10) / (n - 1)
            if n * ar >= As and esp >= dd / 10 + 2.0 and esp <= min(15 * dd / 10, d * 100):
                esc = (n, dd, n * ar)
                break
        if esc:
            break
    rho = (esc[2] if esc else As) / (b * d * 1e4)
    tau = Fd / (b * d) / 1e3
    tau_u = min(3.0 + 0.9 * rho * FYD, 0.27 * (1 - 40 / 250) * fcd, 8.0) if ad <= 0.5 else 0.27 * (1 - 40 / 250) * fcd
    ok = esc is not None and tau <= tau_u
    return dict(h=h, d=round(d, 3), a_d=round(ad, 2), As=round(As, 2), tirante=(f"{esc[0]//2} alças Ø{esc[1]:g} ({esc[2]:.2f} cm²)" if esc else "-"),
                tau=round(tau, 2), tau_u=round(tau_u, 2), a2_cm=round(a2 * 100, 1), ok=ok)


def solucao(bw, h, hd, nome="VM-02"):
    M.larguras(bw)
    M.X_PAD = X_PAD
    B = bw + M.B_ABA
    for n in (6, 8, 10, 12):
        r = M.analisar(h, n, nome, M.VAOS[nome], n_top=2)
        if r["ok_geral"]:
            break
    else:
        return None
    Fd = GN * r["cortante"]["Vd"]
    den = consolo(B, LN, hd, A_DENTE, Fd)
    con = consolo(B, PROJ, h - hd - 0.010, A_CONS, Fd)
    if not den or not con:
        return None
    As_sus = Fd / min(FYD, 43.5) * 1.0                      # cm² (fyd ≤ 435 MPa) — estribos fechados até dvig/4 do recorte
    sus = math.ceil(As_sus / (2 * 2.011))                   # estribos Ø16 de 2 ramos
    ok = den["ok"] and con["ok"] and sus * 0.05 <= (h - 0.05) / 4 + 0.05
    # custo índice por peça: concreto (corpo + maciços − recortes) + cordoalhas + aço passivo estimado
    Lp = r["L_peca"]
    V = r["secao"]["A"] * Lp + 2 * (B * h - r["secao"]["A"]) * 1.0 - 2 * B * (h - hd) * LN
    kg_cord = (n + 2) * 0.775 * Lp
    kg_aco = 105 * V + 2 * (den["As"] + con["As"] * 0 + As_sus) * 1.2 * 0.785   # ~105 kg/m³ corrente + reforço do dente
    custo = V * PRECO["concreto"] + kg_cord * PRECO["cordoalha"] + kg_aco * PRECO["aco"]
    return dict(bw=bw, b_total=round(B, 2), h=h, hd=hd, recorte=round(h - hd, 2), n_cord=n + 2, ok=ok, viga=r, dente=den, consolo=con,
                suspensao=f"{sus} estribos fechados Ø16 (2 ramos) = {sus*4.02:.1f} cm² ≥ {As_sus:.1f}", V_m3=round(V, 3), peso_t=round(V * 2.5, 2),
                kg_cord=round(kg_cord, 1), kg_aco=round(kg_aco, 1), custo_indice=round(custo), h_final=round(h + 0.25, 2))


if __name__ == "__main__":
    res = []
    for bw in (0.25, 0.30, 0.35):
        for h in (0.65, 0.70, 0.75, 0.80, 0.85):
            for hd in [round(0.25 + 0.05 * k, 2) for k in range(12) if 0.25 + 0.05 * k <= h - 0.25]:
                s = solucao(bw, h, hd)
                if s and s["ok"]:
                    res.append(s)
    res.sort(key=lambda s: s["custo_indice"])
    for s in res[:12]:
        print(s["bw"], s["b_total"], s["h"], s["hd"], s["n_cord"], s["dente"]["tirante"], s["dente"]["tau"], s["consolo"]["h"], s["consolo"]["tirante"], s["consolo"]["tau"], s["V_m3"], s["custo_indice"])
    # sem dente (solução atual) para comparar
    M.larguras(0.25); M.X_PAD = 0.15
    r0 = M.analisar(0.65, 10, "VM-02", M.VAOS["VM-02"], n_top=2)
    V0 = r0["secao"]["volume_m3"]
    c0 = V0 * PRECO["concreto"] + 12 * 0.775 * r0["L_peca"] * PRECO["cordoalha"] + 105 * V0 * PRECO["aco"]
    print("sem dente 25/65:", r0["ok_geral"], V0, round(c0))
    best = res[0] if res else None
    (AQ / "vm_dente.json").write_text(json.dumps(dict(melhor=best, ranking=[{k: v for k, v in s.items() if k != "viga"} for s in res[:15]],
                                                       sem_dente=dict(V=V0, custo_indice=round(c0))), indent=1, ensure_ascii=False, default=str), encoding="utf-8")
