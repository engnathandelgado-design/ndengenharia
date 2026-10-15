"""Letsara — reverificação das vigas centrais I130 (V407, V406, V405) com a geometria do R01.

Vãos (eixo a eixo): V407 L2→L4 20,15 m; V406 L4→P13 24,775 m; V405 P13→L9 24,775 m. Cargas: peso próprio, TS-01
(2 por linha, apoiadas no topo da I130 — rev03, sem consolos CV-TS) como cargas concentradas convertidas em carga uniforme equivalente pelo momento máximo
(NBR 6118:2023 — verificação de flexão no meio do vão; cortante pelas reações reais). Unidades kN, m.
"""
import json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from nd_estruturas.prefabricados import Concreto, Carregamento, secao_I, verificar_viga_pretracionada
from geometria import Y_LIN, Y_P13

AQ = Path(__file__).parent
# rev03: com a cobertura nova (painéis solares) a I130 não atende nos vãos de 24 m (ato/ELS-D/ELU com x/d > 0,45) →
# seção I130 (h = 1,30 m, mesmas mesas e alma, mesma fôrma com 20 cm a mais de alma), C50, liberação com fckj 35 MPa
H_I = 1.30
sec = secao_I(H_I, bs=0.40, ts=0.22, ms=0.08, bw=0.15, bi=0.40, ti=0.25, mi=0.08)
C = Concreto(50)
TRIB = 10.075
LG = json.loads((Path(__file__).parent / "ligacoes.json").read_text(encoding="utf-8"))
L_TS = LG["L_TS"]
G_COB = LG["cargas_cob"]["g_total_sem_terca"] + 0.123 / LG["passo_tercas"]     # rev03: zipada + lã + TP40 + painéis + instalações + terças
g_ts = (0.2225 * 25 + G_COB * TRIB) * L_TS / 2          # reação de 1 TS-01 (apoiada no topo da I130, rev03)
q_ts = LG["cargas_cob"]["sobrecarga"] * TRIB * L_TS / 2
P_g, P_q = 2 * g_ts, 2 * q_ts                          # duas TS por linha
VIGAS = {"V407": (Y_LIN[1], Y_LIN[3], [Y_LIN[2]]), "V406": (Y_LIN[3], Y_P13, [Y_LIN[4], Y_LIN[5]]),
         "V405": (Y_P13, Y_LIN[8], [Y_LIN[6], Y_LIN[7]])}
FACES = {"V407": (0.30, 0.20), "V406": (0.20, 0.30), "V405": (0.30, 0.30)}   # meia largura dos pilares (P8A/P11 40, P13 60, P14 60 em y)
res = {}
for nome, (ya, yb, cargas) in VIGAS.items():
    fa, fb = FACES[nome]
    x0 = ya + fa + 0.075 + 0.175                        # pino a 175 da ponta; ponta a 75 da face
    x1 = yb - fb - 0.075 - 0.175
    L = x1 - x0
    xs = [y - x0 for y in cargas]
    def Mmax(P):
        best = 0
        for k in range(201):
            x = L * k / 200
            Ra = sum(P * (L - a) / L for a in xs)
            M = Ra * x - sum(P * (x - a) for a in xs if a < x)
            best = max(best, M)
        return best
    Mg2, Mq = Mmax(P_g), Mmax(P_q)
    g2e, qe = 8 * Mg2 / L ** 2, 8 * Mq / L ** 2
    car = Carregamento(sec.A * 25, g2e, qe, w=0.0, psi1=0.4, psi2=0.0)
    out = {}
    for n in range(16, 34, 2):
        r = verificar_viga_pretracionada(sec, L, car, C, n, y_cord=0.1231, fckj=40)   # 6@60, 6@100, 7@140, 7@180 (26); fckj 40
        out[n] = r
        if r.ok:
            break
    n_ok = min((n for n, r in out.items() if r.ok), default=None)
    r = out[n_ok] if n_ok else out[max(out)]
    V_d = 1.3 * (sec.A * 25 * L / 2 + P_g * len(xs) / 2 * 1.0) + 1.4 * P_q * len(xs) / 2
    L_peca = (yb - fb - 0.075) - (ya + fa + 0.075)
    res[nome] = dict(L_eixos=round(yb - ya, 3), L_peca=round(L_peca, 3), L_calc=round(L, 3), cargas_concentradas_kN=dict(g=round(P_g, 1), q=round(P_q, 1)),
                     g2_equiv=round(g2e, 2), q_equiv=round(qe, 2), n_cord_ok=n_ok, Vd_kN=round(V_d, 1),
                     linhas={k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.linhas.items()}, avisos=r.avisos)
(AQ / "i110_r01.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
for k, v in res.items():
    print(k, v["L_peca"], "n_ok", v["n_cord_ok"], "Vd", v["Vd_kN"], {kk: v["linhas"][kk] for kk in list(v["linhas"])[:12]})


# ------------------------------------------------------------------ ELU com armadura passiva de compressão na mesa superior
# (NBR 6118:2023 14.6.4.3: x/d ≤ 0,45 para fck ≤ 50 MPa; bloco retangular λ = 0,8, αc = 0,85; aço CA-50 fyd 434,8 MPa;
#  cordoalha CP-190 com σpd do resultado acima). Largura b(y) da seção I medida do topo.
def b_topo(y):
    h, ts, ms, bs, bw = H_I, 0.22, 0.08, 0.40, 0.15
    if y <= ts:
        return bs
    if y <= ts + ms:
        return bs - (bs - bw) * (y - ts) / ms
    return bw


def mrd_com_As_sup(n_cord, As_sup_cm2, sig_pd=1478.0, d_p=H_I - 0.1231, d_s=0.05):
    fcd = 50 / 1.4 * 1000
    Fp = n_cord * 98.7e-6 * sig_pd * 1000
    Fs = As_sup_cm2 * 1e-4 * 434.8e3
    lo, hi = 0.001, 1.0
    for _ in range(80):
        x = (lo + hi) / 2
        yb = 0.8 * x
        n = 200
        Cc = sum(0.85 * fcd * b_topo(yb * (k + 0.5) / n) * yb / n for k in range(n))
        if Cc + Fs > Fp:
            hi = x
        else:
            lo = x
    x = (lo + hi) / 2
    yb = 0.8 * x
    n = 200
    Mc = sum(0.85 * fcd * b_topo(yb * (k + 0.5) / n) * yb / n * (d_p - yb * (k + 0.5) / n) for k in range(n))
    return x / d_p, Mc + Fs * (d_p - d_s)


for nome in ("V406", "V405", "V407"):
    xd0, M0 = mrd_com_As_sup(24, 0.0)
    xd, M = mrd_com_As_sup(24, 12.57)
    res[nome]["ELU_24cord_sem_As_sup"] = dict(x_d=round(xd0, 3), MRd=round(M0, 1))
    res[nome]["ELU_24cord_4Ø20_sup"] = dict(x_d=round(xd, 3), MRd=round(M, 1), Md=res[nome]["linhas"]["Md_kNm"],
                                             ok=xd <= 0.45 and M >= res[nome]["linhas"]["Md_kNm"])
    print(nome, res[nome]["ELU_24cord_sem_As_sup"], res[nome]["ELU_24cord_4Ø20_sup"])
(AQ / "i110_r01.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
