"""Estudo de LARGURA da VM (23/10/2026): cópia parametrizada de mef_vm_ret_dente_fases.py (dente Gerber em 2 fases).
Mudanças em relação ao original (artefatos que derrubavam a resistência):
  (1) capa colaborante na largura da VIGA (b), não 1,16 m: no estado plano a capa de 1,16 m ligada só pelo 2º estágio de 13 cm
      gerava concentração de deformação na mudança de espessura (o 25 × 50 "rompia" na capa a 1,3 m);
  (2) critério de 3,5‰ / 10‰ só na ZONA DO DENTE da peça pré-moldada (x ≤ ln + h + 0,5 m); o 2º estágio e o vão são
      relatados à parte (o vão é verificado pela memória: ELU F1/F2 da calc_vm_retangular);
  (3) opção de barras passivas retas no fundo da parte cheia, a partir do canto reentrante (cordoalhas ainda sem
      transferência ali: lbpt 0,88 m + 2 isoladas 1,5 m).
Uso: python3 mef_vm_largura_fases.py CONFIG.json CASO   (CASO = transitoria | final)
(texto original abaixo)
Estudo (23/10/2026): dente Gerber da VM retangular 25 × 80 em DUAS FASES, com o 2º estágio e a capa.

Pergunta do Nathan: o cálculo do dente considera o 2º estágio e a protensão?
- mef_vm_ret_dente.py (prancha rev09): protensão sim; 2º estágio/capa não — a reação total é aplicada só na peça, como
  carga concentrada no topo a 1,0 m da ponta, num trecho de 3 m com apoio fictício.
- Este estudo: meia viga real (simetria no meio do vão), carga DISTRIBUÍDA no topo da viga (onde a laje apoia),
  protensão com as 12 cordoalhas reais (σp∞, lbpt, 2 isoladas 1,5 m) e duas fases:
    fase 1 — peça isolada com γn·Vd1 (peso próprio + laje + capa e 2º estágio frescos);
    fase 2 — ativa o 2º estágio (13 × 25, C30) e a capa colaborante (5 cm, largura bf da memória) sobre a viga e
             carrega o restante (revestimento + sobrecarga) até a ruptura.
  Ativação sem tensão: o 2º estágio entra com nós novos (deslocamento zero = sem deformação) ligado ao topo da viga por
  molas de interface (alças + rugosidade, aderência total) com deformação inicial igual ao deslocamento do topo da viga
  no instante da ativação (InitStrainMaterial) — força zero na ativação, compatibilidade só para a carga da fase 2.
  Continuidade sobre o apoio (armadura negativa no 2º estágio) não é modelada: a reação da fase 2 já vem majorada por
  1,25 em calc_vm_meio_vaso (Vd), e o modelo leva essa reação com momentos de viga biapoiada (a favor da segurança no vão).
Uso: python3 mef_vm_ret_dente_fases.py HD CASO   (HD = 350 | 500; CASO = transitoria | final | validacao)
Saída: mef_fases_{HD}_{CASO}.json e .png nesta pasta.
"""
from __future__ import annotations
import json, math, os, sys
from collections import Counter
from pathlib import Path
import numpy as np

AQ = Path(__file__).resolve().parent
sys.path.insert(0, str(AQ.parents[1]))
os.environ["ND_SO_DADOS"] = "1"
from nd_estruturas.dente_consolo import Dente, AREA
from nd_estruturas.mef_dente import _asd_concreto, _estado

VMJ = json.loads((AQ / "vm_retangular.json").read_text(encoding="utf-8"))
P = VMJ["premissas"]
V2 = VMJ["VM-02"]                                                # maior reação (L cálculo 9,058 m)
GAMA_N = 1.2                                                     # obra = pré-moldado (12.1.1, DECISIONS item 7); 7.3.1.1
HH, BW, COB = round(P["h_pm"] * 1000), round(P["b"] * 1000), 25
LN = round(P["dente"]["ln"] * 1000)
MAC = round(P["dente"]["macico"] * 1000)
A_AP = round((P["x_pad"] - 0.03) * 1000)                         # centro do neoprene a partir da ponta
L_PECA = V2["L_peca"] * 1000
L_CALC = V2["L_calculo"]
LH = L_PECA / 2                                                  # meia viga (simetria)
car = V2["cargas"]
g1, qm, g2, q2 = car["g1"], car["q_mont"], car["g2"], car["q2"]
# reações de cálculo por fase (mesmas fórmulas de calc_vm_meio_vaso: Vd = 1,3 g1 L/2 + 1,4 (g2+q2) L/2 × 1,25)
V1_trans = (1.3 * g1 + 1.3 * qm) * L_CALC / 2                    # montagem: peça isolada com laje e capa frescas + 1 kN/m²
V1_perm = 1.3 * g1 * L_CALC / 2                                  # parcela da fase 1 que fica na peça isolada na fase final
V2_comp = 1.4 * (g2 + q2) * L_CALC / 2 * 1.25                    # parcela aplicada na seção composta
FCK, FCK2 = P["fck"], P["fck_2estagio"]
T2E, H2E = round(P["faixa_2e"] * 1000), 250                      # 2º estágio 13 × 25 sobre a viga
H_CAPA = 50
BF_CAPA = V2["secao"]["bf_capa"] * 1000                          # largura colaborante da capa (memória da VM)
EXTRA_INF = []                                                   # barras passivas extras no fundo da parte cheia
ZONA_X = None


def configurar(cfg):
    """Sobrescreve a geometria/protensão/cargas com um candidato da varredura de largura."""
    global HH, BW, LN, MAC, A_AP, L_PECA, L_CALC, LH, g1, qm, g2, q2, V1_trans, V1_perm, V2_comp, T2E, BF_CAPA, V2, EXTRA_INF, ZONA_X, GAMA_N
    HH, BW, LN, MAC, A_AP = cfg["h_mm"], cfg["b_mm"], cfg.get("ln_mm", LN), cfg.get("macico_mm", MAC), cfg.get("a_ap_mm", A_AP)
    L_PECA, L_CALC = cfg["L_peca_m"] * 1000, cfg["L_calculo_m"]
    LH = L_PECA / 2
    c = cfg["cargas"]
    g1, qm, g2, q2 = c["g1"], c["q_mont"], c["g2"], c["q2"]
    V1_trans = (1.3 * g1 + 1.3 * qm) * L_CALC / 2
    V1_perm = 1.3 * g1 * L_CALC / 2
    V2_comp = 1.4 * (g2 + q2) * L_CALC / 2 * 1.25
    T2E = BW - 120                                               # faixa de 2º estágio: b − 10 apoio − 2 folga
    BF_CAPA = BW                                                 # (1) capa só sobre a viga
    V2 = dict(pos_cordoalhas_mm=cfg["pos_cordoalhas_mm"], isoladas_pontas=cfg["isoladas_pontas"],
              protensao=dict(perdas=dict(sig_pinf=cfg["sig_pinf"])), ato=dict(lbpt_m=cfg["lbpt_m"]))
    EXTRA_INF = cfg.get("extra_inf", [])
    ZONA_X = LN + HH + 500                                       # (2)
    GAMA_N = cfg.get("gama_n", GAMA_N)


def cordoalhas():
    cnt = Counter(y for _, y in V2["pos_cordoalhas_mm"])
    out = []
    for y, n in sorted(cnt.items()):
        if y == min(cnt) and V2["isoladas_pontas"]:
            out += [dict(y=y, n=V2["isoladas_pontas"], isol=1500.0), dict(y=y, n=n - V2["isoladas_pontas"])]
        else:
            out.append(dict(y=y, n=n))
    return out


def armacao(a, hd):
    """Barras como na prancha (armaduras_vigas.armacao_vm / mef_vm_ret_dente.armacao_prancha), até o meio do vão."""
    rec = HH - hd
    arm = [dict(tipo="h", nome="tirante", pos=rec + 55, ini=COB, fim=LN + a["ancoragem_tirante_mm"], area_total=a["n_tir"] * AREA[a["d_tir"]])]
    for k in range(a["n_sus"]):
        arm.append(dict(tipo="v", nome="suspensao", pos=LN + 40 + 50 * k, ini=40, fim=HH - 40, area_total=2 * AREA[a["d_sus"]]))
    nc = a["n_cost"]
    for k in range(nc):
        arm.append(dict(tipo="h", nome="costura", pos=rec + 120 + k * (hd - 160) / max(nc - 1, 1), ini=COB, fim=LN + 450,
                        area_total=2 * AREA[a["d_cost"]]))
    nv = max(2, a["n_v"])
    for k in range(nv):
        arm.append(dict(tipo="v", nome="nariz", pos=60 + k * (LN - 120) / max(nv - 1, 1), ini=rec + 40, fim=HH - 40, area_total=2 * AREA[10.0]))
    x_ult = LN + 40 + 50 * (a["n_sus"] - 1)
    for x in range(LN + 40, MAC, 100):
        if x > x_ult + 30:
            arm.append(dict(tipo="v", nome="N11", pos=x, ini=40, fim=HH - 40, area_total=2 * AREA[8.0]))
    for x in list(range(MAC, 1500, 100)) + list(range(1500, int(LH), 150)):
        arm.append(dict(tipo="v", nome="N2", pos=x, ini=40, fim=HH - 40, area_total=2 * AREA[8.0]))
    arm.append(dict(tipo="h", nome="N3 topo", pos=HH - COB - 10, ini=COB, fim=LH, area_total=2 * AREA[12.5]))
    arm.append(dict(tipo="h", nome="N12 fundo", pos=85, ini=LN + COB, fim=LH, area_total=2 * AREA[10.0]))
    arm.append(dict(tipo="h", nome="N5 meia altura", pos=HH / 2, ini=COB, fim=LH, area_total=2 * AREA[10.0]))
    for ex in EXTRA_INF:                                         # (3) barras retas no fundo a partir do canto reentrante
        arm.append(dict(tipo="h", nome="inf ponta", pos=ex["y"], ini=LN + COB, fim=LN + ex["L"], area_total=ex["n"] * AREA[ex["d"]]))
    return arm


def rodar(hd, caso, saida):
    import openseespy.opensees as ops
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 2)
    m = 25.0
    y_d = HH - hd
    xs = np.unique(np.concatenate([np.arange(0, 1500 + 1e-6, m), np.arange(1500, LH, 50.0), [LH]]))
    ys = np.arange(0, HH + 1e-6, m)
    nx, ny = len(xs) - 1, len(ys) - 1
    ix = lambda x: int(np.argmin(np.abs(xs - x)))
    jy = lambda y: int(round(y / m))
    tag, k = {}, 0
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            if x < LN - 1e-6 and y < y_d - 1e-6:
                continue
            k += 1
            ops.node(k, float(x), float(y))
            tag[(i, j)] = k
    fcd, fctd = 0.85 * FCK / 1.4, 0.7 * 0.3 * FCK ** (2 / 3) / 1.4
    Ec = 0.85 * 5600 * math.sqrt(FCK)
    lin = caso == "validacao"
    if lin:
        ops.nDMaterial("ElasticIsotropic", 1, Ec, 0.2)
    else:
        _asd_concreto(ops, 10, Ec, fcd, fctd, m)
        ops.nDMaterial("PlaneStress", 1, 10)
    e = 0
    elem_c = []
    for i in range(nx):
        for j in range(ny):
            ns = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            if all(n in tag for n in ns):
                xc, yc = (xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2
                e += 1
                ops.element("quad", e, *[tag[n] for n in ns], float(BW), "PlaneStress", 1)
                elem_c.append((e, xc, yc))
    ops.uniaxialMaterial("Steel02", 2, 500 / 1.15, 200000.0, 0.001, 18, 0.925, 0.15)
    ops.uniaxialMaterial("Steel02", 3, 0.9 * 1900 / 1.15, 195000.0, 0.001, 18, 0.925, 0.15)
    sig_pe = V2["protensao"]["perdas"]["sig_pinf"]
    lt = V2["ato"]["lbpt_m"] * 1000
    eps_pe = sig_pe / 195000.0
    mt = [100]
    D = Dente("VM-RET", GAMA_N * (V1_perm + V2_comp), 0.16 * GAMA_N * (V1_perm + V2_comp), BW, hd, LN, A_AP, HH, fck=FCK)
    dim = D.dimensionar(diam_tir=16.0, diam_sus=16.0)
    barras = []
    if not lin:
        for b_ in armacao(dim["adotado"], hd):
            if b_["tipo"] == "h":
                j = jy(b_["pos"]); i0, i1 = ix(b_["ini"]), ix(b_["fim"])
                pares = [((i, j), (i + 1, j)) for i in range(i0, i1)]
            else:
                i = ix(b_["pos"]); j0, j1 = jy(b_["ini"]), jy(b_["fim"])
                pares = [((i, j), (i, j + 1)) for j in range(j0, j1)]
            for a, c in pares:
                if a in tag and c in tag:
                    e += 1
                    ops.element("Truss", e, tag[a], tag[c], b_["area_total"], 2)
                    barras.append((e, b_["nome"], b_["tipo"]))
    if not lin:
        for c in cordoalhas():
            j = jy(c["y"])
            x0 = (LN if c["y"] < y_d else 0.0) + c.get("isol", 0.0)
            for i in range(ix(x0), nx):
                a, b2 = (i, j), (i + 1, j)
                if a in tag and b2 in tag:
                    f = min(1.0, ((xs[i] + xs[i + 1]) / 2 - x0) / lt)
                    mt[0] += 1
                    ops.uniaxialMaterial("InitStrainMaterial", mt[0], 3, f * eps_pe)
                    e += 1
                    ops.element("Truss", e, tag[a], tag[b2], c["n"] * 98.7, mt[0])
                    barras.append((e, "cordoalha", "p"))
    # apoio no neoprene do dente: placa de aço com um nó no centro; simetria no meio do vão (ux = 0)
    ops.nDMaterial("ElasticIsotropic", 50, 200000.0, 0.3)
    i0, i1 = ix(A_AP - 100), ix(A_AP + 100)
    inf, sup = [], []
    for i in range(i0, i1 + 1):
        if (i, jy(y_d)) in tag:
            k += 1
            ops.node(k, float(xs[i]), float(y_d - 20.0))
            inf.append(k); sup.append(tag[(i, jy(y_d))])
    for q in range(len(inf) - 1):
        e += 1
        ops.element("quad", e, inf[q], inf[q + 1], sup[q + 1], sup[q], float(BW), "PlaneStress", 50)
    no_ap = inf[len(inf) // 2]
    ops.fix(no_ap, 0, 1)
    for j in range(ny + 1):
        if (nx, j) in tag:
            ops.fix(tag[(nx, j)], 1, 0)
    topo = [(i, tag[(i, ny)]) for i in range(nx + 1)]
    trib = [((xs[min(i + 1, nx)] - xs[max(i - 1, 0)]) / 2) for i, _ in topo]
    trib[-1] = (xs[nx] - xs[nx - 1]) / 2
    tot = sum(trib)

    def analise(test=("NormUnbalance", 1.0, 200)):
        ops.wipeAnalysis()
        ops.constraints("Transformation"); ops.numberer("RCM"); ops.system("UmfPack")
        ops.test(*test); ops.algorithm("Newton")

    # etapa 0: protensão
    ops.timeSeries("Constant", 1); ops.pattern("Plain", 1, 1)
    analise(); ops.integrator("LoadControl", 0.0); ops.analysis("Static")
    ok0 = ops.analyze(5)
    ops.reactions(); R0 = ops.nodeReaction(no_ap, 2)
    ops.loadConst("-time", 0.0)

    def padrao(ts, pat, nos):
        """carga vertical distribuída de resultante 1 N (= reação no dente por simetria) + Hd 0,16 no apoio."""
        ops.timeSeries("Linear", ts); ops.pattern("Plain", pat, ts)
        for (i, n), t in zip(nos, trib):
            ops.load(n, 0.0, -t / tot)
        ops.load(no_ap, -0.16, 0.0)

    def reacao():
        ops.reactions(); return (ops.nodeReaction(no_ap, 2) - R0) / 1e3

    ctrl = tag[(nx, ny)]
    perto = lambda xc, yc: abs(xc - A_AP) < 200 and abs(yc - y_d) < 200
    mon_c = [e_ for e_, xc, yc in elem_c if not perto(xc, yc) and (ZONA_X is None or xc <= ZONA_X)]
    mon_s = [e_ for e_, nome, tipo in barras if tipo != "p"]  # todas as barras passivas
    eps_ini = {e_: ops.basicDeformation(e_)[0] for e_, nome, tipo in barras if tipo == "p"}
    L_el = {}

    def criterio():
        es = max((ops.basicDeformation(e_)[0] / L_el.setdefault(e_, _comp(e_)) for e_ in mon_s), default=0.0)
        ep = max(((ops.basicDeformation(e_)[0] - eps_ini[e_]) / L_el.setdefault(e_, _comp(e_)) for e_ in eps_ini), default=0.0)
        ec, emin = 0.0, None
        for e_ in mon_c:
            st = ops.eleResponse(e_, "material", 1, "strain")
            ev = (st[0] + st[1]) / 2 - math.sqrt(((st[0] - st[1]) / 2) ** 2 + (st[2] / 2) ** 2)
            if ev < ec:
                ec, emin = ev, e_
        return es, ep, ec, emin

    def _comp(e_):
        n1, n2 = ops.eleNodes(e_)
        c1, c2 = ops.nodeCoord(n1), ops.nodeCoord(n2)
        return math.hypot(c2[0] - c1[0], c2[1] - c1[1])

    res = dict(hd=hd, caso=caso, gama_n=GAMA_N, protensao_ok=ok0 == 0, R0_kN=round(R0 / 1e3, 2),
               V1_trans=round(V1_trans, 1), V1_perm=round(V1_perm, 1), V2_comp=round(V2_comp, 1),
               dente_analitico=dict(NBR=dim["NBR"], PCI=dim["PCI"], adotado=dim["adotado"]))

    if caso == "validacao":                                       # elástico, sem armadura: flecha × viga de Timoshenko
        padrao(2, 2, topo)
        P_ = 100e3
        analise(("NormUnbalance", 1e-3, 50)); ops.integrator("LoadControl", P_ / 10); ops.analysis("Static"); ops.analyze(10)
        V = reacao()
        w = P_ / LH                                    # N/mm (carga até o meio, apoio em A_AP; aprox.)
        Lv = 2 * (LH - A_AP)
        I = BW * HH ** 3 / 12; Gc = Ec / 2.4; As = BW * HH / 1.2
        d_an = 5 * w * Lv ** 4 / (384 * Ec * I) + w * Lv ** 2 / (8 * Gc * As)
        d_mef = -ops.nodeDisp(tag[(nx, 0)], 2) + ops.nodeDisp(no_ap, 2)
        res.update(validacao=dict(V_kN=round(V, 2), P_kN=P_ / 1e3, flecha_mef_mm=round(d_mef, 4), flecha_viga_mm=round(d_an, 4),
                                  razao=round(d_mef / d_an, 3), obs="trecho 25 × 45 do dente e maciço reduzem a rigidez junto ao apoio"))
        ops.wipe()
        return res

    # fase 1: peça isolada
    alvo1 = GAMA_N * (V1_trans if caso == "transitoria" else V1_perm) * 1e3
    padrao(2, 2, topo)
    analise(("NormDispIncr", 1e-5, 60)); ops.algorithm("KrylovNewton")
    hist, lim = [], None
    if caso == "final":
        ops.integrator("LoadControl", alvo1 / 40); ops.analysis("Static")
        for _ in range(40):
            if ops.analyze(1) != 0:
                ops.integrator("LoadControl", alvo1 / 400)
                if any(ops.analyze(1) != 0 for _ in range(10)):
                    res["falha_fase1"] = True
                    break
                ops.integrator("LoadControl", alvo1 / 40)
            hist.append((-ops.nodeDisp(ctrl, 2), reacao(), 1))
        V_f1 = reacao()
        es, ep, ec, emin = criterio()
        res["fim_fase1"] = dict(V_kN=round(V_f1, 1), aco_permil=round(es * 1000, 2), cord_permil=round(ep * 1000, 2), conc_permil=round(ec * 1000, 2))
        ops.loadConst("-time", 0.0)
        # ativa 2º estágio + capa: nós novos (u = 0) e molas de interface com deformação inicial = deslocamento do topo
        Ec2 = 0.85 * 5600 * math.sqrt(FCK2)
        _asd_concreto(ops, 20, Ec2, 0.85 * FCK2 / 1.4, 0.7 * 0.3 * FCK2 ** (2 / 3) / 1.4, m)
        ops.nDMaterial("PlaneStress", 21, 20)
        ops.uniaxialMaterial("Elastic", 30, 1.0e6)
        ys2 = np.arange(0, H2E + 1e-6, m)
        t2 = {}
        for i, x in enumerate(xs):
            for j2, y2 in enumerate(ys2):
                k += 1
                ops.node(k, float(x), float(HH + y2))
                t2[(i, j2)] = k
        for i in range(nx):
            for j2 in range(len(ys2) - 1):
                yc2 = (ys2[j2] + ys2[j2 + 1]) / 2
                esp = T2E if yc2 < H2E - H_CAPA else BF_CAPA
                e += 1
                ops.element("quad", e, t2[(i, j2)], t2[(i + 1, j2)], t2[(i + 1, j2 + 1)], t2[(i, j2 + 1)], float(esp), "PlaneStress", 21)
                elem_c.append((e, (xs[i] + xs[i + 1]) / 2, HH + yc2))
                if ZONA_X is None:
                    mon_c.append(e)
        for i in range(nx + 1):
            nb, nc_ = tag[(i, ny)], t2[(i, 0)]
            for d in (1, 2):
                mt[0] += 1
                ops.uniaxialMaterial("InitStrainMaterial", mt[0], 30, ops.nodeDisp(nb, d))
                e += 1
                ops.element("zeroLength", e, nb, nc_, "-mat", mt[0], "-dir", d)
        for j2 in range(len(ys2)):
            ops.fix(t2[(nx, j2)], 1, 0)
        # fase 2: carga no topo da viga (apoio da laje), até a ruptura
        padrao(3, 3, topo)
        analise(("NormDispIncr", 1e-5, 60)); ops.algorithm("KrylovNewton")
        ops.integrator("LoadControl", 0.0); ops.analysis("Static"); ops.analyze(1)
        res["ativacao_V_kN"] = round(reacao(), 2)               # tem de ser = V_f1 (sem salto de força)
        base = V_f1
        fase = 2
    else:
        base, fase = 0.0, 1
    du = 0.02
    ops.integrator("DisplacementControl", ctrl, 2, -du); ops.analysis("Static")
    snap_d = None
    Fd_total = GAMA_N * ((V1_trans) if caso == "transitoria" else (V1_perm + V2_comp))
    for p in range(1500):
        r = ops.analyze(1)
        if r != 0:
            for div in (2, 4, 8, 16, 32):
                ops.integrator("DisplacementControl", ctrl, 2, -du / div)
                if all(ops.analyze(1) == 0 for _ in range(div)):
                    r = 0
                    break
            if r != 0:
                for alg in (("ModifiedNewton", "-initial"), ("NewtonLineSearch",)):
                    ops.algorithm(*alg); ops.test("NormDispIncr", 1e-4, 300)
                    ops.integrator("DisplacementControl", ctrl, 2, -du / 10)
                    if all(ops.analyze(1) == 0 for _ in range(10)):
                        r = 0
                    ops.algorithm("KrylovNewton"); ops.test("NormDispIncr", 1e-5, 60)
                    if r == 0:
                        break
            ops.integrator("DisplacementControl", ctrl, 2, -du)
            if r != 0:
                break
        V = reacao()
        hist.append((-ops.nodeDisp(ctrl, 2), V, fase))
        if lim is None:
            es, ep, ec, emin = criterio()
            if es >= 0.010 or ep >= 0.010 or ec <= -0.0035:
                lim = dict(V=round(V, 1), aco=round(es * 1000, 2), cordoalha=round(ep * 1000, 2), concreto=round(ec * 1000, 2),
                           criterio="aço 10‰" if es >= 0.010 else ("cordoalha +10‰" if ep >= 0.010 else "concreto 3,5‰"),
                           xy_concreto_mm=next(((round(xc), round(yc)) for e_, xc, yc in elem_c if e_ == emin), None))
        if snap_d is None and V >= Fd_total:
            snap_d = _estado(ops, elem_c, barras)
        if len(hist) > 30 and V < 0.80 * max(h[1] for h in hist):
            break
        if lim and V < lim["V"] * 0.9:
            break
    Vpico = max(h[1] for h in hist)
    Vu = min(Vpico, lim["V"]) if lim else Vpico
    snap_u = _estado(ops, elem_c, barras)
    res.update(Fd_kN=round(Fd_total, 1), Vu_kN=round(Vu, 1), V_pico_kN=round(Vpico, 1), limite=lim, FS=round(Vu / Fd_total, 2),
               ok=Vu >= 1.06 * Fd_total, criterio=f"Vu ≥ 1,06·Fd = {1.06 * Fd_total:.1f} kN",
               tensoes_em_Fd_MPa=None if snap_d is None else snap_d["max_tensao"],
               curva=[(round(a, 3), round(b, 1), f) for a, b, f in hist[::max(1, len(hist) // 80)]])
    _figura(saida.with_suffix(".png"), elem_c, snap_u, hist, res, hd)
    ops.wipe()
    return res


def _figura(caminho, elem_c, snap, hist, res, hd):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    fig = plt.figure(figsize=(13, 6.5))
    a1 = fig.add_axes([0.05, 0.42, 0.88, 0.5]); a2 = fig.add_axes([0.08, 0.07, 0.5, 0.27])
    pol, val = [], []
    for e_, xc, yc in elem_c:
        if xc > 2200:
            continue
        h = 12.5
        pol.append([(xc - h, yc - h), (xc + h, yc - h), (xc + h, yc + h), (xc - h, yc + h)])
        val.append(min(3.0, max(0.0, snap["eps1"].get(e_, 0.0) * 1000)))
    pc = PolyCollection(pol, array=np.array(val), cmap="inferno_r", edgecolors="none")
    pc.set_clim(0, 3); a1.add_collection(pc); a1.set_xlim(-20, 2220); a1.set_ylim(-40, HH + 300); a1.set_aspect("equal")
    a1.axhline(HH, color="#2e7d32", lw=1, ls="--")
    a1.text(1500, HH + 270, "2º estágio + capa (ativos na fase 2)" if res["caso"] == "final" else "peça isolada (montagem)", fontsize=9)
    fig.colorbar(pc, ax=a1, fraction=0.02, label="ε1 (‰) na ruptura")
    a1.set_title(f"Dente {BW} × {hd} — {'final em 2 fases' if res['caso'] == 'final' else 'transitória (peça isolada)'}: "
                 f"Vu {res['Vu_kN']:.0f} kN, Fd {res['Fd_kN']:.0f} kN, FS {res['FS']:.2f}", fontsize=10)
    xs_ = [h[0] for h in hist]; vs_ = [h[1] for h in hist]
    a2.plot(xs_, vs_, "-", color="#c62828"); a2.axhline(res["Fd_kN"], ls="--", color="k", lw=.8)
    a2.set_xlabel("flecha no meio do vão (mm)"); a2.set_ylabel("reação no dente (kN)"); a2.grid(alpha=.3)
    fig.text(0.62, 0.25, "\n".join([f"protensão: {len(V2['pos_cordoalhas_mm'])} cordoalhas, σp∞ {V2['protensao']['perdas']['sig_pinf']:.0f} MPa",
                                    f"fase 1 (peça): γn·Vd1 = {GAMA_N * (res['V1_trans'] if res['caso'] == 'transitoria' else res['V1_perm']):.0f} kN",
                                    "" if res["caso"] == "transitoria" else f"fase 2 (composta): γn·Vd2 = {GAMA_N * res['V2_comp']:.0f} kN",
                                    f"limite: {res['limite']['criterio'] if res['limite'] else 'pico'} em {res['limite']['xy_concreto_mm'] if res['limite'] else '-'}"]),
             fontsize=9, va="center")
    fig.savefig(caminho, dpi=130, facecolor="white"); plt.close(fig)


if __name__ == "__main__":
    cfg_path, caso = Path(sys.argv[1]), sys.argv[2]
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    configurar(cfg)
    out = cfg_path.with_name(cfg_path.stem + f"_{caso}.json")
    r = rodar(cfg["hd_mm"], caso, out)
    r["config"] = {k: v for k, v in cfg.items() if k != "pos_cordoalhas_mm"}
    out.write_text(json.dumps(r, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    print(json.dumps({k: r.get(k) for k in ("Fd_kN", "Vu_kN", "V_pico_kN", "FS", "ok", "limite", "fim_fase1")}, ensure_ascii=False))
