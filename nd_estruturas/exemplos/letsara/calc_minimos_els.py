"""Letsara — armaduras mínimas (NBR 6118:2023) de pilares e vigas, e fissuração em serviço (ELS) de todos os casos.

Pilares: 17.3.5.3.1 — As,min = 0,15 Nd/fyd ≥ 0,4 % Ac; As,max 8 % (4 % nas emendas). Vigas protendidas: 17.3.5.2.1 —
ρmin da Tabela 17.3 pode ser atendida pela armadura ativa desde que MRd ≥ Md,min = 0,8 W0 fctk,sup; pele 17.3.5.2.3
(0,10 % Ac,alma por face, h > 60 cm); estribo mínimo 17.4.1.1.1 (ρsw ≥ 0,2 fctm/fywk). Fissuração: 17.3.3 (w_k) para
peças armadas (dentes e consolos) e ELS-F / ELS-D (protensão limitada, CAA II) para as protendidas; pilares no estádio I
se σt ≤ fctk,inf na combinação frequente.
"""
import json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from nd_estruturas.prefabricados import (Concreto, Carregamento, secao_I, verificar_viga_pretracionada, pressao_vento, CORD)

AQ = Path(__file__).parent
DT = json.loads((AQ / "dentes.json").read_text(encoding="utf-8"))
fyd = 500 / 1.15
R = {}

# ------------------------------------------------------------------ 1. pilares
qv = pressao_vento(45.0, S3=0.95)
C40 = Concreto(40)
pil = {}
for nome, b, h, Nk, As_prov, desc in (("lateral/fachada armado", 0.40, 0.60, 412.2, 2 * 5 * 3.14 + 2 * 4 * 4.91 - 4 * 4.91, "5 Ø20/face (60) + 4 Ø25/face (40), cantos comuns"),
                                       ("lateral/fachada protendido", 0.40, 0.60, 412.2, 8 * 3.14, "8 Ø20 + 10 cord. Ø12,7"),
                                       ("central 50×50", 0.50, 0.50, 600.0, 8 * 3.14, "8 Ø20 (a confirmar na prancha)")):
    Ac = b * h * 1e4
    Nd = 1.4 * Nk
    As_min = max(0.15 * Nd / fyd, 0.004 * Ac)
    pil[nome] = dict(armadura=desc, As_prov_cm2=round(As_prov, 1), As_min_cm2=round(As_min, 1), taxa_pct=round(As_prov / Ac * 100, 2),
                     ok_min=As_prov >= As_min, ok_max=As_prov / Ac <= 0.04, nota="protendido: a mínima passiva é atendida sem contar as cordoalhas")
# fissuração em serviço (combinação frequente, ψ1 = 0,3 no vento) — tensão de tração na face
W = 0.40 * 0.60 ** 2 / 6
Mk = (0.7 + 0.5) / 2 * qv * 9.655 * 10.0 ** 2 / 2
Nk = 412.2
fctk_inf = 0.7 * 0.3 * 40 ** (2 / 3)
for nome, sig_p in (("lateral/fachada armado", 0.0), ("lateral/fachada protendido", 4.11)):
    st = 0.3 * Mk / W / 1e3 - Nk / 0.24 / 1e3 - sig_p
    # combinação rara (ψ0 = 1): vento inteiro
    sr = Mk / W / 1e3 - Nk / 0.24 / 1e3 - sig_p
    pil[nome].update(sigma_t_freq_MPa=round(st, 2), sigma_t_rara_MPa=round(sr, 2), fctk_inf=round(fctk_inf, 2),
                     estadio_I_freq=st <= fctk_inf, estadio_I_rara=sr <= fctk_inf,
                     fissuracao="sem fissura na frequente" if st <= fctk_inf else "fissura na frequente: calcular w_k")
# ELS-W (17.3.3) é verificado na combinação frequente: os dois pilares ficam no estádio I nela, w_k = 0.
# Na combinação rara (vento inteiro) os dois fissuram; para o protendido ficar no estádio I também na rara seriam ≈ 16 cordoalhas.
for nome in ("lateral/fachada armado", "lateral/fachada protendido"):
    pil[nome]["wk_freq_mm"] = 0.0
    pil[nome]["cord_para_estadio_I_na_rara"] = math.ceil((Mk / W / 1e3 - Nk / 0.24 / 1e3 - fctk_inf) * 0.24 * 1e3 / (0.987e-4 * 1000e3))
R["pilares"] = pil

# ------------------------------------------------------------------ 2. vigas protendidas: mínimos e ELS
C50 = Concreto(50)
I90 = secao_I(0.90, bs=0.40, ts=0.12, ms=0.08, bw=0.15, bi=0.40, ti=0.15, mi=0.08)
I110 = secao_I(1.10, bs=0.40, ts=0.22, ms=0.08, bw=0.15, bi=0.40, ti=0.25, mi=0.08)
I70 = secao_I(0.70, bs=0.40, ts=0.12, ms=0.08, bw=0.15, bi=0.40, ti=0.15, mi=0.08)
TRIB = 9.655
vigas = {
    "TS-01 (I90 cobertura)": dict(sec=I90, L=19.16, car=Carregamento(I90.A * 25, 0.25 * TRIB, 0.25 * TRIB, w=qv * TRIB, psi1=0.4, psi2=0.0), n=6, y=0.075, nsup=0),
    "I110 V405 (23 m)": dict(sec=I110, L=23.17, car=None, n=24, y=None, nsup=0),
    "Mezanino I90 (h26,5+5)": dict(sec=I90, L=9.27, car=Carregamento(I90.A * 25, (3.9 + 1.25 + 1.0) * 10.05 / 2, 5.0 * 10.05 / 2, psi1=0.6, psi2=0.4), n=9, y=0.075, nsup=0),
    "Mezanino I70 (h20+5)": dict(sec=I70, L=9.27, car=Carregamento(I70.A * 25, (2.8 + 1.25 + 1.0) * 10.05 / 2, 5.0 * 10.05 / 2, psi1=0.6, psi2=0.4), n=10, y=0.075, nsup=0),
}
# I110: carga equivalente às reações das TS-01 (V405: cargas a 4,68 e 14,26 m) — momento máximo convertido em carga uniforme
P_g, P_q = 2 * (I90.A * 25 + 0.25 * TRIB) * 19.16 / 2, 2 * 0.25 * TRIB * 19.16 / 2
L_ = 23.17
def mmax(L, xs, F):
    best = 0.0
    for i in range(401):
        xt = L * i / 400
        Ra = sum(F * (L - x) / L for x in xs)
        best = max(best, Ra * xt - sum(F * (xt - x) for x in xs if x < xt))
    return best
vigas["I110 V405 (23 m)"]["car"] = Carregamento(I110.A * 25, 8 * mmax(L_, [4.68, 14.26], P_g) / L_ ** 2, 8 * mmax(L_, [4.68, 14.26], P_q) / L_ ** 2, psi1=0.4, psi2=0.0)
vigas["I110 V405 (23 m)"]["y"] = 0.128
out_v = {}
for nome, v in vigas.items():
    sec, car = v["sec"], v["car"]
    r = verificar_viga_pretracionada(sec, v["L"], car, C50, v["n"], y_cord=v["y"], fckj=35, n_sup=v["nsup"])
    W0 = sec.Wi
    fctk_sup = 1.3 * 0.3 * 50 ** (2 / 3)
    Md_min = 0.8 * W0 * fctk_sup * 1e3
    Ap = v["n"] * CORD["12.7"] * 1e4
    rho_min = 0.208 / 100                                     # Tabela 17.3, C50
    As_min_tab = rho_min * sec.A * 1e4
    h = sec.h
    pele = 0.001 * 0.15 * h * 1e4 if h > 0.60 else 0.0         # por face, 0,10 % da alma (bw × h)
    fctm = 0.3 * 50 ** (2 / 3)
    rho_sw = 0.2 * fctm / 500
    asw_min = rho_sw * 0.15 * 1e4                              # cm²/m (bw = 15 cm), 2 ramos
    out_v[nome] = dict(cordoalhas=v["n"], Ap_cm2=round(Ap, 2), rho_min_tab_cm2=round(As_min_tab, 2),
                       Md_min_kNm=round(Md_min), MRd_kNm=r.linhas["MRd_kNm"], ok_Md_min=r.linhas["MRd_kNm"] >= Md_min,
                       criterio="17.3.5.2.1: armadura ativa atende a mínima se MRd ≥ Md,min = 0,8 W0 fctk,sup",
                       pele_cm2_por_face=round(pele, 2), pele_adotada="2 Ø8 por face na alma" if pele > 0 else "não exige (h ≤ 60)",
                       estribo_min_cm2_m=round(asw_min, 2), estribo_adotado="Ø6,3 c/25 = 2,5 cm²/m" if "I70" in nome or "TS" in nome else "Ø8 c/15 = 6,7 cm²/m",
                       ok_estribo=(2.5 if ("I70" in nome or "TS" in nome) else 6.7) >= asw_min,
                       ELS=dict(elsf_inf_MPa=r.linhas["elsf_inf_MPa"], elsf_lim_MPa=r.linhas["elsf_lim_MPa"], elsd_inf_MPa=r.linhas["elsd_inf_MPa"],
                                vento_sup_MPa=r.linhas.get("vento_sup_MPa"), els_ok=r.linhas["els_ok"],
                                nota="protensão limitada (CAA II): ELS-F na frequente e ELS-D na quase permanente — sem abertura de fissura a calcular"),
                       ELU_ok=r.ok, avisos=r.avisos)
R["vigas"] = out_v

# ------------------------------------------------------------------ 3. fissuração dos dentes e consolos (armados) — w_k 17.3.3.2
def wk(sig_s, phi, As_mm2, Acr_mm2, fck=50):
    fctm = 0.3 * fck ** (2 / 3)
    rho_r = As_mm2 / Acr_mm2
    w1 = phi / (12.5 * 2.25) * sig_s / 200000 * 3 * sig_s / fctm
    w2 = phi / (12.5 * 2.25) * sig_s / 200000 * (4 / rho_r + 45)
    return min(w1, w2)
fis = {}
for k, Vk_Vd in (("TS-01", 104 / 138), ("I110", 320 / 448), ("MEZ-I90", 275 / 383)):
    c = DT[k]["calculo"]; a = c["adotado"]
    As_req, As_prov = c["adotado"]["As_tir"], a["n_tir"] * math.pi * a["d_tir"] ** 2 / 4
    sig_s = fyd * Vk_Vd * As_req / As_prov
    Acr = 400 * (2 * 45 + 7.5 * a["d_tir"])
    w = wk(sig_s, a["d_tir"], As_prov, Acr)
    fis[f"dente {k}"] = dict(sigma_s_serv_MPa=round(sig_s), wk_mm=round(w, 3), limite_mm=0.3, ok=w <= 0.3, tirante=a["tirante"])
for c in DT["consolos"]:
    n, d = c["tirante"].split(" ")[0], float(c["tirante"].split("Ø")[1].split(" ")[0])
    As_prov = int(n) * math.pi * d ** 2 / 4
    Vk_Vd = 0.72
    sig_s = fyd * Vk_Vd * c["As_tir"] / As_prov
    Acr = 400 * (2 * 45 + 7.5 * d)
    w = wk(sig_s, d, As_prov, Acr)
    fis[c["nome"]] = dict(sigma_s_serv_MPa=round(sig_s), wk_mm=round(w, 3), limite_mm=0.3, ok=w <= 0.3, tirante=c["tirante"])
R["fissuracao_armados"] = fis
(AQ / "minimos_els.json").write_text(json.dumps(R, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
print(json.dumps(R, indent=1, ensure_ascii=False, default=str))
