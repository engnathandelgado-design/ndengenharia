"""Letsara — estudo de terças sem mão-francesa: escolha automática do perfil mais leve por família.

Famílias (catálogos Isoeste no Drive: "perfis_estruturais" e catalogo_isoeste.py):
  - Ue CIVIL 300 e Ue ZAR 345 (bw×bf×D tabelados);
  - Z45 Isoeste (ISO Z152…Z350, CIVIL 300 e ZAR 345). O catálogo só dá alma, espessura e área; a aba bf sai da área
    (D = 20 mm, enrijecedor a 45°) — (conferir) com o fabricante antes de emitir.
Esquemas: biapoiada (wL²/8; δ = 5wL⁴/384EI) e contínua (Z por transpasse, Ue por luva) com vão extremo governando
(M+ ≈ wL²/11; δ ≈ 0,0069wL⁴/EI); sobre os apoios internos a seção é dupla (transpasse 0,1 L para cada lado).
Sem mão-francesa: apoio por cantoneira com 2 parafusos M12 na alma (braço z entre eles) resistindo à torção de apoio
T = R·e (e = carga no meio da mesa até o centro de torção). NBR 14762:2010 (MRD, 9.9), NBR 8800:2008 Anexo C (L/180).
Mesmos carregamentos de calc_cobertura_metalica.py (q0 0,874; Cp −1,0 geral e −1,6 nas faixas; escora Nd do modelo R01).
"""
import json, math, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from nd_estruturas.metalica_fria import PerfilUe, PerfilZ, pressao_contato_fino_Rd, parafuso_corte_Rd

AQUI = Path(__file__).parent
LG = json.loads((AQUI / "ligacoes.json").read_text(encoding="utf-8"))
CM = json.loads((AQUI / "cobertura_metalica.json").read_text(encoding="utf-8"))
from geometria import VAOS_Y

L = max(VAOS_Y); s = LG["passo_tercas"]; CC = LG["cargas_cob"]
q0, CP = 0.874, dict(geral=-1.0, borda=-1.6)
ND_ESC = CM["terca_escora"]["Nd_max"]          # maior compressão de escora (kN)
N_TERCAS = 2 * len(LG["s_tercas"])              # linhas de terças na cobertura (2 meias águas)
COMP_TOTAL = sum(VAOS_Y)                        # m por linha de terça
Z_DEV_D = 20.0

UE = {
    "CIVIL300": ("USI-SAC300", [2.00, 2.25, 2.65, 3.00],
                 [(200, 70, 20), (250, 65, 25), (300, 85, 25), (350, 110, 25)]),
    "ZAR345": ("ZAR345", [1.95, 2.30, 2.70], [(250, 65, 25), (350, 110, 25)]),
}
# Z45 Isoeste: alma -> {t: área cm²} (catálogo, p. 7)
Z_AREA = {
    "CIVIL300": ("USI-SAC300", {242: {2.00: 8.00, 2.25: 9.01, 2.65: 10.59, 3.00: 12.01},
                                272: {2.00: 9.20, 2.25: 10.36, 2.65: 12.18, 3.00: 13.81},
                                312: {2.00: 10.00, 2.25: 11.26, 2.65: 13.24, 3.00: 15.01},
                                350: {2.00: 11.20, 2.25: 12.61, 2.65: 14.83, 3.00: 16.81}}),
    "ZAR345": ("ZAR345", {242: {1.95: 7.81, 2.30: 9.20, 2.70: 10.79},
                          272: {1.95: 8.98, 2.30: 10.58, 2.70: 12.41},
                          312: {1.95: 9.76, 2.30: 11.50, 2.70: 13.49},
                          350: {1.95: 10.94, 2.30: 12.89, 2.70: 15.14}}),
}

# voestalpine Meincol / METSEC (catálogo "Purlins" 2019, p. 6-7): aço fy 400 MPa (fu 480 adotado — conferir), Z275.
# Z de abas desiguais (superior/inferior) com enrijecedores Lt/Lb inclinados (45° adotado — conferir); C com lábio L.
# série: (aba sup, aba inf, Lt, Lb) ; {t: kg/m}
METSEC_Z = {232: ((65, 60, 14, 16), {1.75: 5.09, 1.95: 5.66, 2.30: 6.63, 2.70: 7.73}),
            262: ((65, 60, 14, 16), {1.75: 5.50, 1.95: 6.11, 2.30: 7.17, 2.70: 8.37, 3.00: 9.25}),
            302: ((90, 82, 19, 21), {1.75: 6.84, 1.95: 7.60, 2.30: 8.92, 2.70: 10.42, 3.00: 11.54}),
            342: ((90, 82, 19, 21), {1.95: 8.21, 2.30: 9.65, 2.70: 11.27, 3.00: 12.48}),
            402: ((100, 92, 20, 22), {2.30: 11.13, 2.70: 13.01, 3.00: 14.41})}
METSEC_C = {232: ((65, 13), {1.75: 5.11, 1.95: 5.67, 2.30: 6.65, 2.70: 7.75}),
            262: ((65, 13), {1.75: 5.52, 1.95: 6.13, 2.30: 7.19, 2.70: 8.39, 3.00: 9.28}),
            302: ((88, 18), {1.75: 6.84, 1.95: 7.60, 2.30: 8.92, 2.70: 10.42, 3.00: 11.54}),
            342: ((88, 18), {1.95: 8.21, 2.30: 9.65, 2.70: 11.27, 3.00: 12.48}),
            402: ((95, 22), {2.30: 11.13, 2.70: 13.01, 3.00: 14.41})}
FAMILIAS = os.environ.get("ND_FAMILIAS", "todas")      # "metsec" roda só a Meincol e reaproveita o JSON anterior


def z_aba(bw, t, A_cm2, aco):
    """Aba bf (mm, externa) que reproduz a área do catálogo com D = 20 mm."""
    lo, hi = 40.0, 140.0
    for _ in range(40):
        bf = (lo + hi) / 2
        if PerfilZ(bw, bf, Z_DEV_D, t, aco).p["A"] < A_cm2 * 100:
            lo = bf
        else:
            hi = bf
    return round(bf, 1)


def verifica(u, esquema, n_lin):
    g = CC["g_total_sem_terca"] + u.peso_kNm / s
    g_fav = CC["g_favoravel_sucao"] + u.peso_kNm / s
    q = CC["sobrecarga"]
    kM, kd = (1 / 8, 5 / 384) if esquema == "biapoiada" else (1 / 11, 0.0069)
    Lb = L / (n_lin + 1) * 1000
    if not hasattr(u, "_cM"):
        u._cM = u.criticos("M")
        u._cN = u.criticos("N", L_dist_ref=u._cM["L_dist"])
    cM = u._cM
    Mg = u.MRd(0, crit=cM, contida=True)["MRd"]
    MRs = u.MRd(Lb, Cb=1.0, crit=cM)
    Ms = MRs["MRd"]
    w_g = (1.35 * g + 1.5 * q) * s
    w_s = (1.4 * abs(CP["borda"]) * q0 - g_fav) * s
    uso_g = w_g * L ** 2 * kM / Mg
    uso_s = w_s * L ** 2 * kM / Ms
    # escora (vãos com X): N do modelo + M da sucção de borda, amplificado (NBR 14762:2010 9.9)
    NR = u.NcRd(L * 1000, Lb, Lb, crit=u._cN)
    amp = 1 / (1 - ND_ESC / NR["Nex"])
    uso_e = ND_ESC / NR["NcRd"] + w_s * L ** 2 * kM * amp / Ms
    V = max(w_g, w_s) * L * (0.5 if esquema == "biapoiada" else 0.6)
    uso_v = V / u.VRd()
    EI = 200e6 * u.p["Ix"] * 1e-12
    fl = kd * (g + q) * s * L ** 4 / EI * 1000
    uso_f = fl / (L * 1000 / 180)
    # apoio sem MF: torção T = R·e resistida por binário de 2 M12 na alma (z = 0,6 bw), cortante dividida
    R = w_s * L * (0.5 if esquema == "biapoiada" else 0.6)
    e = (u.bf / 2 + u.m_ct) / 1000
    z = 0.6 * u.bw / 1000
    F = math.hypot(R * e / z, R / 2)
    Rb = min(pressao_contato_fino_Rd(12, u.t, u.fu), parafuso_corte_Rd(12, "8.8"))
    uso_a = F / Rb
    usos = dict(gravidade=uso_g, succao=uso_s, cortante=uso_v, flecha=uso_f, apoio_2M12=uso_a)
    gov = max(usos, key=usos.get)
    # a escora (Nd máx. do modelo com a sucção de borda, envoltória) vale só para as terças dos nós do X e do oitão:
    # informada à parte; a verificação linha a linha fica em calc_cobertura_metalica.py
    usos["escora_envoltoria"] = uso_e
    # peso por linha: contínua soma o transpasse de 0,2 L em cada apoio interno
    n_int = len(VAOS_Y) - 1
    comp = COMP_TOTAL + (0.2 * L * n_int if esquema == "continua" else 0.0)
    kgm = getattr(u, "kg_cat", None) or u.p["A"] * 7.85e-3      # massa do catálogo quando houver
    kg_linha = kgm * comp
    return dict(perfil=u.nome, aco=u.aco, kg_m=round(kgm, 2), esquema=esquema, correntes=n_lin,
                usos={k: round(v, 3) for k, v in usos.items()}, governa=gov, uso_max=round(usos[gov], 3),
                modo_succao=MRs["modo"], flecha_mm=round(fl, 1), T_apoio_kNm=round(R * e, 3), F_parafuso_kN=round(F, 2),
                peso_total_t=round(kg_linha * N_TERCAS / 1000, 2), ok=bool(usos[gov] <= 1.0))


def candidatos():
    if FAMILIAS in ("todas", "metsec"):
        for bw, ((bs, bi, lt, lb), ts) in METSEC_Z.items():
            for t, kg in ts.items():
                u = PerfilZ(bw, bs, lt, t, "METSEC400", 45.0, bi, lb); u.kg_cat = kg
                yield "Z Metsec", u
        for bw, ((b, l), ts) in METSEC_C.items():
            for t, kg in ts.items():
                u = PerfilUe(bw, b, l, t, "METSEC400"); u.kg_cat = kg
                yield "C Metsec", u
    if FAMILIAS == "metsec":
        return
    for fam, (aco, ts, secs) in UE.items():
        for (bw, bf, D) in secs:
            for t in ts:
                yield f"Ue {fam}", PerfilUe(bw, bf, D, t, aco)
    for fam, (aco, tab) in Z_AREA.items():
        for bw, ts in tab.items():
            for t, A in ts.items():
                yield f"Z45 {fam}", PerfilZ(bw, z_aba(bw, t, A, aco), Z_DEV_D, t, aco)


res = []
if FAMILIAS == "metsec":
    _ant = json.loads((AQUI / "estudo_tercas_sem_mf.json").read_text(encoding="utf-8"))["todos"]
    for r in _ant:
        if "Metsec" not in r["familia"]:
            r["usos"].setdefault("escora_envoltoria", r["usos"].pop("escora", None))
            u_ = {k: v for k, v in r["usos"].items() if k != "escora_envoltoria"}
            r["governa"] = max(u_, key=u_.get); r["uso_max"] = u_[r["governa"]]; r["ok"] = r["uso_max"] <= 1.0
            res.append(r)
for i, (fam, u) in enumerate(candidatos()):
    print(i, u.nome, flush=True)
    for esq in ("biapoiada", "continua"):
        for n in (2, 3):
            r = verifica(u, esq, n)
            r["familia"] = fam
            res.append(r)

melhores = {}
for r in res:
    if not r["ok"]:
        continue
    k = (r["familia"], r["esquema"], r["correntes"])
    if k not in melhores or r["peso_total_t"] < melhores[k]["peso_total_t"]:
        melhores[k] = r
atual = next(r for r in res if r["perfil"].startswith("Ue 300×85×25×2,65") and r["esquema"] == "biapoiada" and r["correntes"] == 3)
out = dict(dados=dict(L_m=L, s_m=s, Nd_escora=ND_ESC, linhas_tercas=N_TERCAS, comp_linha_m=COMP_TOTAL),
           atual=atual, melhores=sorted(melhores.values(), key=lambda r: r["peso_total_t"]), todos=res)
(AQUI / "estudo_tercas_sem_mf.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=lambda o: o.item()), encoding="utf-8")
if __name__ == "__main__":
    print("ATUAL", atual["perfil"], atual["usos"], atual["peso_total_t"])
    for r in out["melhores"]:
        print(f'{r["familia"]:14s} {r["esquema"]:9s} {r["correntes"]}L  {r["perfil"]:26s} {r["kg_m"]:5.2f} kg/m  '
              f'{r["peso_total_t"]:5.2f} t  {r["governa"]:10s} {r["uso_max"]:.2f}  esc {r["usos"]["escora_envoltoria"]:.2f}  fl {r["flecha_mm"]} mm  F {r["F_parafuso_kN"]} kN')
