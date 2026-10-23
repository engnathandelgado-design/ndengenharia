"""Estudo (23/10/2026, pedido do Nathan): V400 (V407), V401 (V406), V402 (V405) com h = 110 cm (limitação de fôrma do
cliente). Só cálculo — NÃO altera i110_r01.json, pranchas nem geradores. Saída: estudo_i130_h110.json.

Reaproveita a verificação vigente (calc_i110_r01.verificar: perdas 9.6.3, lbpt 9.4.5, ato 17.2.4.3.2, ELS-D frequente /
ELS-F rara — protensão completa DEC-043, ELU por compatibilidade, cortante 17.4.2.2, içamento NBR 9062 5.3.2, reação do
dente) com a seção, a alma (bw), a bitola (Ø12,7 / Ø15,2 CP-190 RB) e o arranjo parametrizados, e acrescenta:
  - flechas e contraflechas em 5 estágios (NBR 6118:2023 17.3.2.1.2 e Anexo A; NBR 9062:2017 5.4.3.4 Tab. 9), com Ecs(t),
    φ(t,t0) = φ(∞,t0) [Tab. 8.2, o mesmo das perdas] × desenvolvimento no tempo do Anexo A (βf, βd), perdas progressivas
    proporcionais a φ(t,t0)/φ(∞,t0) (χ = 0,8 na fluência da parcela perdida);
  - estabilidade lateral NBR 9062:2017 6.1 (L/bf ≤ 50 e L·h/bf² ≤ 500; senão Lebelle FS ≥ 2,5);
  - dente Gerber com h 110: o topo fica em +7,776 e a cota de apoio do dente no consolo CP-I130 também (hd 78 mantido,
    recorte 52 → 32 cm); MEF não linear (mef_dente) com a armação da prancha e o arranjo novo.
"""
import json, math, sys, itertools, os
from pathlib import Path
AQ = Path(__file__).parent
sys.path.insert(0, str(AQ.parents[1]))
sys.path.insert(0, str(AQ))
import nd_estruturas.prefabricados as PF

src = (AQ / "calc_i110_r01.py").read_text(encoding="utf-8").split("\nres = {}")[0]
for a, b in [("    bw = 0.15\n", "    bw = BW\n"),
             ('lbpt_cordoalha(FCKJ, pp["sig_p0"], gradual=True)', 'lbpt_cordoalha(FCKJ, pp["sig_p0"], diam_mm=DIAM, gradual=True)'),
             ('lbpt_cordoalha(FCKJ, pp["sig_p0"], gradual=False)', 'lbpt_cordoalha(FCKJ, pp["sig_p0"], diam_mm=DIAM, gradual=False)'),
             ("SIG_PI * 98.7 / 1000", "SIG_PI * CORD['12.7'] * 1000")]:
    assert a in src, a
    src = src.replace(a, b)
ns = {"__file__": str(AQ / "calc_i110_r01.py"), "BW": 0.15, "DIAM": 12.7}
exec(compile(src, "calc_i110_r01", "exec"), ns)
CORD0 = dict(PF.CORD)
KG_M = {12.7: 0.792, 15.2: 1.102}                   # kg/m CP-190 RB
Y_L = {12.7: (60, 100, 140, 180, 220), 15.2: (60, 110, 160, 210, 260)}   # Ø15,2: espaçamento vertical livre ≥ 2φ (18.6.2.3)
SECAO = dict(bs=0.40, ts=0.22, ms=0.08, bi=0.40, ti=0.25, mi=0.08)
TOPO_SUP = 7.776                                     # topo da I130 (mantido)


def config(H, bw, diam):
    """Ajusta os globais do cálculo vigente para (h, bw, Ø)."""
    sec = PF.secao_I(H, bw=bw, **SECAO)
    ns.update(H_I=H, BW=bw, DIAM=diam, sec=sec, SECP=PF.secao_retangular(0.40, H),
              U_AR=sum(math.dist(a, b) for a, b in zip(sec.pts, sec.pts[1:] + sec.pts[:1])),
              Y_N3=H - 0.030 - 0.0063 - 0.010)
    area = CORD0["15.2" if diam == 15.2 else "12.7"]
    PF.CORD["12.7"] = area                           # ato_pretracao (biblioteca) usa CORD["12.7"]
    ns["CORD"] = dict(CORD0, **{"12.7": area})
    return sec


def linhas(diam, por_linha, l5, topo, H):
    X = {7: ns["X7"], 5: ns["X5"], 4: ns["X4"], 0: []}
    y = Y_L[diam]
    lin = [dict(y=yy, xs=list(X[n]), isol=i) for yy, n, i in zip(y[:4], por_linha, ns["ISOL"]) if n]
    if l5:
        lin.append(dict(y=y[4], xs=[-50, 50] if l5 == 2 else [-100, -50, 50, 100], isol=4000))
    if topo:
        lin.append(dict(y=round(H * 1000 - 100), xs=[-100, 100], isol=0))
    return lin


# ------------------------------------------------------------------ fluência no tempo (NBR 6118:2023 Anexo A)
def _beta_f(t, h):
    h = min(max(h, 0.05), 1.6)
    A = 42 * h ** 3 - 350 * h ** 2 + 588 * h + 113
    B = 768 * h ** 3 - 3060 * h ** 2 + 3234 * h - 23
    Cc = -200 * h ** 3 + 13 * h ** 2 + 1090 * h + 183
    D = 7579 * h ** 3 - 31916 * h ** 2 + 35343 * h + 1931
    return (t * t + A * t + B) / (t * t + Cc * t + D)


def _fc_rel(t):                                      # A.2.2.3: fc(t)/fc(t∞)
    return 9 * t * (t + 42) / ((9 * t + 40) * (t + 61))


def phi_t(phi_inf, t, t0, hfic_cm, U=70.0):
    """φ(t,t0) = φ(∞,t0) · [φa + φf∞(βf(t) − βf(t0)) + φd∞·βd] / [φa + φf∞(1 − βf(t0)) + φd∞]  (forma do Anexo A)."""
    if t >= 1e4:
        return phi_inf
    pa = 0.8 * (1 - _fc_rel(t0))
    pf = (4.45 - 0.035 * U) * (42 + hfic_cm) / (20 + hfic_cm)
    h = hfic_cm / 100
    num = pa + pf * (_beta_f(t, h) - _beta_f(t0, h)) + 0.4 * (t - t0 + 20) / (t - t0 + 70)
    den = pa + pf * (1 - _beta_f(t0, h)) + 0.4
    return phi_inf * num / den


def flechas(r, sec, H, lin, diam):
    """Flecha no meio do vão (mm; + para baixo, − contraflecha) em 5 estágios, integração numérica da curvatura com P(x)
    (lbpt e isolamentos) entre os apoios (pino a 175 da ponta)."""
    C = ns["C"]
    pp = r["perdas"]
    L, Lp, a_ap = r["L_calc"], r["L_peca"], 0.175
    xs_c = r["x_cargas_m"]
    Pg, Pq = r["cargas_concentradas_kN"]["g"], r["cargas_concentradas_kN"]["q"]
    lt = r["ato"]["lbpt_m"]
    LN, HD = ns["LN"], ns["HD"]
    area = ns["CORD"]["12.7"]
    grupos = [dict(n=len(l["xs"]), y=l["y"] / 1000, x0=(LN if l["y"] / 1000 < H - HD else 0.0) + l["isol"] / 1000) for l in lin]
    ai = min(1.0, 0.8 + 0.2 * C.fck / 80)
    Ecs28 = C.Ecs
    Ecsj = ai * PF.eci_j(C, ns["FCKJ"])
    g1 = sec.A * 25
    n = 400
    dx = L / n
    xs = [(k + 0.5) * dx for k in range(n)]

    def m_unit(x):
        return x / 2 if x <= L / 2 else (L - x) / 2

    def Mp(sig):                                     # momento da protensão (kN·m, negativo = contraflecha) na seção x
        out = []
        for x in xs:
            xp = x + a_ap
            xm = min(xp, Lp - xp)
            F = My = 0.0
            for gr in grupos:
                f = min(1.0, max(0.0, (xm - gr["x0"]) / lt)) * gr["n"] * area * sig * 1000
                F += f
                My += f * gr["y"]
            out.append(-F * (sec.yc - (My / F if F else 0)) if F else 0.0)
        return out

    def M_g1(x):
        return g1 * x * (L - x) / 2

    def M_P(P, x):
        RA = sum(P * (L - a) / L for a in xs_c)
        return RA * x - sum(P * (x - a) for a in xs_c if a < x)

    def f(Ms, E):                                    # ∫ M·m/EI dx
        return sum(M * m_unit(x) for M, x in zip(Ms, xs)) * dx / (E * sec.I)

    Mg1 = [M_g1(x) for x in xs]
    Mg2 = [M_P(Pg, x) for x in xs]
    Mq = [M_P(Pq, x) for x in xs]
    fp0_j, fpinf_j = f(Mp(pp["sig_p0"]), Ecsj), f(Mp(pp["sig_pinf"]), Ecsj)
    fp0_28, fpinf_28 = f(Mp(pp["sig_p0"]), Ecs28), f(Mp(pp["sig_pinf"]), Ecs28)
    fg1_j, fg1_28 = f(Mg1, Ecsj), f(Mg1, Ecs28)
    fg2, fq = f(Mg2, Ecs28), f(Mq, Ecs28)
    T0, TM, hfic = ns["T0"], ns["T_G2"], pp["h_fic_cm"]
    phi_inf = pp["phi"]
    phi_m = phi_t(phi_inf, TM, T0, hfic)             # liberação → montagem (60 d)
    phi_g2, _ = PF.fluencia_retracao(ns["U"], hfic, TM)   # cobertura aplicada aos 60 d → ∞
    r_m = phi_m / phi_inf                            # fração das perdas progressivas até a montagem
    dP28 = fpinf_28 - fp0_28                         # > 0: a perda progressiva reduz a contraflecha

    def estagio(phi, frac):
        return fg1_j + fp0_j + (fg1_28 + fp0_28) * phi + frac * dP28 * (1 + 0.8 * phi)

    e1 = fg1_j + fp0_j
    e2 = estagio(phi_m, r_m)
    e3 = e2 + fg2
    e4 = estagio(phi_inf, 1.0) + fg2 * (1 + phi_g2) + ns["PSI2"] * fq
    e5 = ns["PSI1"] * fq
    lim_fin = 250 if L <= 15 else 300 if L <= 20 else 350
    mm = lambda v: round(v * 1000, 1)
    out = dict(
        Ecs_liberacao_MPa=round(Ecsj / 1000), Ecs_28_MPa=round(Ecs28 / 1000), phi_inf_t0=round(phi_inf, 2), phi_montagem=round(phi_m, 2),
        phi_inf_cobertura_60d=round(phi_g2, 2), perda_progressiva_ate_montagem_pct=round(r_m * pp["perda_progressiva_pct"], 1),
        e1_liberacao=mm(e1), e2_montagem=mm(e2), e3_apos_cobertura=mm(e3), e4_final_qp=mm(e4), e5_sobrecarga_freq=mm(e5),
        sobrecarga_total=mm(fq), fg2_cobertura=mm(fg2),
        lim=dict(fabricacao_L300=mm(L / 300), peca_isolada_montagem_L500=mm(L / 500), montagem_L250=mm(L / 250),
                 final=f"L/{lim_fin}", final_mm=mm(L / lim_fin)))
    out["ok"] = dict(e1=abs(e1) <= L / 300, e2=abs(e2) <= L / 250, e3=(e3 <= L / 500 and -e3 <= L / 250), e4=abs(e4) <= L / lim_fin)
    out["criterio"] = ("e1 |contraflecha de fabricação| ≤ L/300; e2 |contraflecha na montagem| ≤ L/250; e3 flecha para baixo da peça isolada após montagem ≤ L/500 (para cima, ≤ L/250); e4 |final, quase-permanente| ≤ L/" + str(lim_fin))
    return out


def lateral(sec, H, bw, Lp, fckj):
    """NBR 9062:2017 6.1 — L/bf ≤ 50 e L·h/bf² ≤ 500; senão Lebelle qcr = 28,3·√(E·Iy·G·J)/L³ ≥ 2,5·(1,3·g)."""
    bs, ts, bi, ti = SECAO["bs"], SECAO["ts"], SECAO["bi"], SECAO["ti"]
    hw = H - ts - ti
    Iy = ts * bs ** 3 / 12 + ti * bi ** 3 / 12 + hw * bw ** 3 / 12
    J = sum(b * t ** 3 / 3 * (1 - 0.63 * t / b) for b, t in ((bs, ts), (bi, ti))) + hw * bw ** 3 / 3 * (1 - 0.63 * bw / hw)
    E = 0.85 * PF.eci_j(ns["C"], fckj)
    g = sec.A * 25
    out = {}
    for caso, L in (("montagem (apoiada nos dentes, antes do travamento)", Lp - 0.35), ("içamento (alças a 2,50 m)", Lp - 2 * ns["ALCA_A"])):
        qcr = 28.3 * math.sqrt(E * Iy * E / 2.4 * J) / L ** 3
        out[caso] = dict(L=round(L, 2), FS_lebelle=round(qcr / (1.3 * g), 2))
    crit = Lp / bs <= 50 and Lp * H / bs ** 2 <= 500
    FSmin = min(v["FS_lebelle"] for v in out.values())
    return dict(L_bf=round(Lp / bs, 1), Lh_bf2=round(Lp * H / bs ** 2), criterio_simples=crit, casos=out, FS_min=FSmin,
                ok=crit or FSmin >= 2.5)


def rodar(nome, H, bw, diam, por_linha, l5, topo):
    sec = config(H, bw, diam)
    lin = linhas(diam, por_linha, l5, topo, H)
    ya, yb, cargas = ns["VIGAS"][nome]
    r = ns["verificar"](nome, ya, yb, cargas, lin)
    fl = flechas(r, sec, H, lin, diam)
    lat = lateral(sec, H, bw, r["L_peca"], ns["FCKJ"])
    ok = {k: v for k, v in r["ok"].items() if k != "flecha"}
    ok.update(ELS_D_margem=r["ELS"]["D_base"] <= -ns["MARGEM_D"], flechas=all(fl["ok"].values()), lateral=lat["ok"])
    n = r["arranjo"]["n_cord"]
    Lp = r["L_peca"]
    peso = r["icamento"]["peso_kN"]
    desc = "+".join(str(x) for x in por_linha) + (f" + {l5} (y {Y_L[diam][4] / 10:g})" if l5 else "") + (" + 2 topo" if topo else "")
    return dict(viga=nome, h_cm=round(H * 100), bw_cm=round(bw * 100), mesas="sup 40×22 + mísula 8; inf 40×25 + mísula 8",
                cordoalha=f"Ø{diam:g}", arranjo=desc, n_cord=n, F_macaco_kN=r["arranjo"]["F_macaco_kN"], F_total_macaco_kN=round(n * r["arranjo"]["F_macaco_kN"]),
                peso_t=round(peso / 9.81, 2), peso_kN=peso, m3=round(peso / 25, 2), kg_cordoalha=round(n * Lp * KG_M[diam], 1),
                L_peca=Lp, L_calc=r["L_calc"],
                usos=dict(ELU_Md_MRd=round(r["ELU"]["Md"] / r["ELU"]["MRd"], 2), x_d=r["ELU"]["x_d"],
                          cortante_Vd_VRd2=round(r["cortante"]["Vd_max"] / r["cortante"]["VRd2"], 2),
                          cortante_Asw=f"{r['cortante']['pior']['Asw_req']:.2f}/{r['cortante']['pior']['Asw_ef']:.2f} cm²/m",
                          ELS_D_MPa=r["ELS"]["D_base"], ELS_F_MPa=r["ELS"]["F_base"], ELS_F_topo_MPa=r["ELS"]["F_topo"], lim_F_MPa=r["ELS"]["lim_F"],
                          ELS_D_transf_MPa=r["ELS"]["D_base_transferencia"],
                          ato_topo_MPa=round(r["ato"]["topo_max"], 2), ato_base_MPa=round(r["ato"]["base_min"], 2),
                          ato_lim=f"{r['ato']['lim_t']:.2f} / {r['ato']['lim_c']:.1f}", ato_As_topo=f"{r['ato']['As_topo_cm2']:.2f} ≤ {r['ato']['As_N3_cm2']:.2f} cm²",
                          icamento_topo_MPa=r["icamento"]["topo_alca"], icamento_lim_t=r["icamento"]["lim_t"]),
                perdas_pct=dict(imediata=round(r["perdas"]["perda_imediata_pct"], 1), total=round(r["perdas"]["perda_total_pct"], 1)),
                lbpt_m=r["ato"]["lbpt_m"], sig_pinf=round(r["perdas"]["sig_pinf"], 1), dente=r["dente"], flechas=fl, lateral=lat, ok=ok, ok_geral=all(ok.values()), _lin=lin)


# ------------------------------------------------------------------ HOJE (h 130, arranjo vigente DEC-043)
vig = json.loads((AQ / "i110_r01.json").read_text(encoding="utf-8"))
HOJE = {"V407": ((5, 4, 4, 4), 0, False), "V406": ((7, 7, 7, 7), 2, True), "V405": ((7, 7, 7, 7), 2, True)}
NOMES = {"V407": "V400", "V406": "V401", "V405": "V402"}
res = dict(hoje={}, h110={}, tentativas={})
for nome, (pl, l5, tp) in HOJE.items():
    r = rodar(nome, 1.30, 0.15, 12.7, pl, l5, tp)
    assert r["n_cord"] == vig[nome]["arranjo"]["n_cord"], (nome, r["n_cord"])
    res["hoje"][nome] = r
    print("HOJE", NOMES[nome], r["arranjo"], r["n_cord"], r["ok_geral"], {k: v for k, v in r["ok"].items() if not v}, r["flechas"]["e1_liberacao"], r["flechas"]["e4_final_qp"])

# ------------------------------------------------------------------ h 110: busca do menor arranjo
combos = sorted({c for c in itertools.product((7, 5, 4, 0), repeat=4) if c[0] >= c[1] >= c[2] >= c[3] and c[0] > 0 and c[1] > 0})
GRUPOS = {"V407": ["V407"], "V406+V405": ["V406", "V405"]}   # V401 e V402 na mesma pista de 60 m → mesmo arranjo
for grupo, membros in GRUPOS.items():
    achados = []
    for diam in (12.7, 15.2):
        for bw in (0.15, 0.20, 0.25):
            cand = []
            for pl in combos:
                for l5 in (0, 2, 4):
                    for tp in (False, True):
                        n = sum(pl) + l5 + 2 * tp
                        cand.append((n, pl, l5, tp))
            cand.sort(key=lambda c: (c[0], -c[1][0]))
            for n, pl, l5, tp in cand:
                try:
                    rs = [rodar(m, 1.10, bw, diam, pl, l5, tp) for m in membros]
                except Exception as e:
                    continue
                if all(r["ok_geral"] for r in rs):
                    achados.append(dict(diam=diam, bw=bw, n=n, pl=pl, l5=l5, tp=tp, rs=rs))
                    print("h110", grupo, f"Ø{diam} bw {bw}", rs[0]["arranjo"], n, "OK")
                    break
            else:
                print("h110", grupo, f"Ø{diam} bw {bw}", "nenhum arranjo passa")
                ult = [rodar(m, 1.10, bw, diam, (7, 7, 7, 7), 4, True) for m in membros]
                res["tentativas"][f"{grupo} Ø{diam} bw{bw*100:.0f} (máx 7+7+7+7+4+2)"] = {r["viga"]: {k: v for k, v in r["ok"].items() if not v} for r in ult}
    res["tentativas"][grupo] = [dict(cord=f"Ø{a['diam']:g}", bw_cm=round(a["bw"] * 100), arranjo=a["rs"][0]["arranjo"], n=a["n"],
                                     kg=sum(r["kg_cordoalha"] for r in a["rs"]), m3=sum(r["m3"] for r in a["rs"])) for a in achados]
    # escolha: menor alma (menos concreto/peso), depois menor custo de cordoalha
    if achados:
        best = min(achados, key=lambda a: (a["bw"], sum(r["kg_cordoalha"] for r in a["rs"])))
        for r in best["rs"]:
            res["h110"][r["viga"]] = r

# ------------------------------------------------------------------ V401/V402: o que falta nas melhores tentativas
res["V401_V402_tentativas"] = []
for diam, bw, pl, l5, tp, n3 in [(12.7, 0.25, (7, 7, 7, 7), 4, True, (4, 20.0)), (15.2, 0.25, (7, 7, 5, 5), 0, True, (4, 20.0)),
                                 (15.2, 0.25, (7, 7, 7, 7), 2, True, (4, 20.0)), (15.2, 0.25, (7, 7, 7, 7), 2, True, (6, 25.0)),
                                 (15.2, 0.40, (7, 7, 7, 7), 4, True, (6, 25.0))]:
    ns["N3"] = n3
    r = rodar("V406", 1.10, bw, diam, pl, l5, tp)
    res["V401_V402_tentativas"].append(dict(cord=r["cordoalha"], bw_cm=r["bw_cm"], arranjo=r["arranjo"], n=r["n_cord"], N3=f"{n3[0]} Ø{n3[1]:g}",
                                           peso_t=r["peso_t"], falhas=[k for k, v in r["ok"].items() if not v], usos=r["usos"],
                                           flechas={k: r["flechas"][k] for k in ("e1_liberacao", "e2_montagem", "e3_apos_cobertura", "e4_final_qp", "lim")}))
ns["N3"] = (4, 20.0)

# ------------------------------------------------------------------ dente com h 110 (MEF)
res["dente_h110"] = {}
if os.environ.get("SEM_MEF") != "1" and res["h110"]:
    os.environ["ND_SO_DADOS"] = "1"
    sys.argv = [sys.argv[0]]
    import calc_dentes as CD
    from nd_estruturas.dente_consolo import Dente
    from nd_estruturas.mef_dente import analisar
    rr = max(res["h110"].values(), key=lambda r: r["dente"]["Fd"])
    diam = float(rr["cordoalha"][1:])
    fator = CORD0["15.2" if diam == 15.2 else "12.7"] / CORD0["12.7"]   # MEF trabalha em "cordoalhas Ø12,7 equivalentes"
    cord = [dict(y=l["y"], n=len(l["xs"]) * fator, **({"isol": l["isol"]} if l["isol"] else {})) for l in rr["_lin"]]
    v = dict(CD.VIGAS["I130"])
    PF.CORD.update(CORD0)
    # força do detalhe atual do dente da I130 (Fd 610,5 / Hd 97,7, DEC-032) se for maior que a da viga em h 110
    v.update(H=1100, Vd=max(rr["dente"]["Fd"], v["Vd"]), Hd=max(rr["dente"]["Hd"], v["Hd"]), cord=cord, sig_pe=rr["sig_pinf"],
             lt=rr["lbpt_m"] * 1000)
    D = Dente("I110", v["Vd"], v["Hd"], 400, v["hd"], v["ln"], v["a_apoio"], v["H"])
    rd = D.dimensionar(diam_tir=v["d_tir"], diam_sus=v["d_sus"])
    g = dict(H=1100, b=400, bw=round(rr["bw_cm"] * 10), ti=v["ti"], mi=80, ts=v["ts"], ms=80, hd=v["hd"], ln=v["ln"], a_apoio=v["a_apoio"],
             x_mac=v["x_mac"], l_apoio=v["l_apoio"])
    arm = CD.armaduras_i130(v, rd["adotado"])
    arm = [a for a in arm if not (a.get("nome") == "pele" and a["pos"] > 1100 - 100)]
    m = analisar(g, arm, cord, v["Vd"], v["Hd"], fck=50.0, malha=25.0, Ls=v["Ls"], xP=v["xP"], passos=500, rampa_fim=v["rampa_fim"],
                 robusto=v["robusto"], sig_pe=v["sig_pe"], lt=v["lt"], saida_png=str(AQ / "mef_dente_I130_h110.png"), titulo="Dente Gerber I130 com h 110 (estudo)")
    m.pop("curva", None)
    hoje = json.loads((AQ / "dentes.json").read_text(encoding="utf-8"))["I130"]
    res["dente_h110"] = dict(geometria=dict(H=1100, hd=780, ln=350, recorte_mm=320, bw=g["bw"]), Fd=v["Vd"], Hd=v["Hd"], calculo=rd["adotado"],
                             MEF=dict(Vu_kN=m["Vu_kN"], FS=m["FS"], ok=m["Vu_kN"] >= 1.06 * v["Vd"], protensao_ok=m.get("protensao_ok"),
                                      aco_tirante_MPa=m.get("aco_tirante_em_Vd_MPa"), aco_suspensao_MPa=m.get("aco_suspensao_em_Vd_MPa")),
                             hoje=dict(Fd=hoje["Vd"], adotado=hoje["calculo"]["adotado"], Vu_kN=hoje["mef"]["Vu_kN"], FS=hoje["mef"]["FS"]))
    print("dente h110", res["dente_h110"]["MEF"], rd["adotado"])

PF.CORD.update(CORD0)
for bloco in ("hoje", "h110"):
    for r in res[bloco].values():
        r.pop("_lin", None)
res["niveis"] = dict(topo=TOPO_SUP, fundo_hoje=round(TOPO_SUP - 1.30, 3), fundo_h110=round(TOPO_SUP - 1.10, 3),
                     apoio_dente=round(TOPO_SUP - 1.30 + 0.52, 3), recorte_hoje_cm=52, recorte_h110_cm=32)
(AQ / "estudo_i130_h110.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
