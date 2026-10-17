"""Letsara — estudo de otimização do contraventamento da cobertura (rev05).

Algoritmo:
  1. Modelo global 3D (modelo_global_r04.py, OpenSeesPy) com pilares engastados, TS-01, I130, VB, terças-escora em todas
     as linhas e X (só tração) parametrizado: vãos contraventados (qualquer subconjunto dos 8 vãos, inclusive os de oitão,
     com orelha na VB) e largura do painel do X em espaços de terça (2, 4, 8 ou 16 — o painel de 8 dá diagonal ≈ 45°).
  2. Vento NBR 6123:1988 nas 4 direções (0°, 180°: nos oitões; 90°, 270°: nas laterais), com:
     - Cpe das paredes (Tab. 4, h/b ≤ 1/2, a/b = 2): barlavento +0,7; sotavento −0,3 (0°/180°) e −0,5 (90°/270°) — conferir;
     - aberturas reais: laterais A e E abertas até +7,50 entre as linhas 2 e 4 (área aberta), portões na parede da
       linha 4, anexo (linhas 1-2) e pavilhão (4-9) fechados; pressão interna por compartimento (6.2.5): fechado
       −0,3 / 0; área aberta +0,2 (vento normal às aberturas) e Cpe da face paralela (vento 0°/180°); pavilhão com os
       portões abertos = pressão da área aberta. As paredes internas das linhas 2 e 4 recebem a diferença de pressão
       interna entre os compartimentos (força em y que as terças e o X levam aos pilares);
     - excentricidade da resultante (6.6): e = 0,075·b (vento 0°/180°) e 0,075·a (90°/270°), nos dois sentidos.
  3. Para cada variante: força máxima na diagonal (bitola mínima), terças-escora linha a linha (Z 302 METSEC:
     N do modelo + M do MEF contínuo, NBR 14762 9.9), deslocamento ELS e momentos na base dos pilares; custo
     (diagonais, esticadores, orelhas, montagem e reforço de escoras que não passam).
  4. Etapa 1: todos os 255 subconjuntos de vãos com painel de 8 espaços; etapa 2: os melhores com todos os painéis.
Saída: estudo_contraventamento.json. Unidades kN, m.
"""
import itertools, json, math, os, sys, types
from multiprocessing import Pool
from pathlib import Path

AQ = Path(__file__).resolve().parent
sys.path.insert(0, str(AQ)); sys.path.insert(0, str(AQ.parents[1]))
from nd_estruturas.metalica_fria import barra_redonda_tracao_Rd

_src = (AQ / "modelo_global_r04.py").read_text(encoding="utf-8")
_src = _src[:_src.index("res = dict(combinacoes")]
mg = types.ModuleType("mg"); mg.__file__ = str(AQ / "modelo_global_r04.py")
exec(compile(_src, "modelo_global_r04.py", "exec"), mg.__dict__)
CB = json.loads((AQ / "cobertura_metalica.json").read_text(encoding="utf-8"))
Y, XE = mg.Y_LIN, mg.X_EIXO
LARG, COMP, XC = mg.LARG, mg.COMP, mg.XC
ESQ = sorted(mg.NOS + mg.MID)                   # 17 terças da meia água esquerda
DIR = sorted(mg.NOS_D + mg.MID_D)
q = lambda z: mg.pressao_vento(45.0, z=max(z, 3.0), S3=0.95)

# ------------------------------------------------------------------ paredes e compartimentos
Z_ABERTO = 7.50                                     # laterais abertas até +7,50 entre as linhas 2 e 4
Y_AB = (Y[1], Y[3])
H_INT = 7.50                                        # paredes internas das linhas 2 e 4 (placas até ~+6,25/+7,50)
PORTOES_L4 = [(9.87, 15.195), (24.305, 29.63)]       # vãos com portão na linha 4 (até +7,40)
CPE = {0: (0.7, -0.3), 180: (0.7, -0.3), 90: (0.7, -0.5), 270: (0.7, -0.5)}   # barlavento, sotavento (Tab. 4 — conferir)
CPI_FECHADO = (-0.3, 0.0)                           # 6.2.5 b (quatro faces igualmente permeáveis)
CPI_ABERTO = {90: 0.2, 270: 0.2, 0: -0.6, 180: -0.2}   # área aberta: normal às aberturas +0,2; paralelo: Cpe da face lateral


def _at(nome, z):
    p = next(p for p in mg.pil if p["nome"] == nome)
    return p["ns"][p["zs"].index(min(p["zs"], key=lambda zz: abs(zz - z)))]


def _faixas(p):
    zs = p["zs"]
    out = []
    for k in range(1, len(zs)):
        z0 = (zs[k] + zs[k - 1]) / 2
        z1 = (zs[k] + zs[k + 1]) / 2 if k + 1 < len(zs) else zs[k]
        out.append((p["ns"][k], z0, z1, zs[k]))
    return out


def _forca_parede(p, larg_fun, cp_fun):
    """Σ cp·q·área por nó do pilar; larg_fun(z_meio) = largura tributária efetiva (m) na faixa."""
    f = {}
    for n, z0, z1, zk in _faixas(p):
        zm = (z0 + z1) / 2
        f[n] = f.get(n, 0.0) + cp_fun(zm) * q(zk) * larg_fun(zm) * (z1 - z0)
    return f


def vento(direcao, ecc, interno):
    """Forças nodais do vento (kN). direcao 0/180/90/270; ecc ∈ {−1, 0, +1}; interno = (cpi_anexo, cpi_aberta, cpi_pavilhao)."""
    F = {}
    def add(n, fx, fy):
        v = F.setdefault(n, [0.0] * 6); v[0] += fx; v[1] += fy
    cb, cs = CPE[direcao]
    if direcao in (0, 180):
        faces = {0.0: ["P1C-L1", "P3-L1", "P4-L1", "P5-L1", "P2C-L1"], COMP: ["P1C-L9", "P3-L9", "P14-L9", "P5-L9", "P2C-L9"]}
        sg = 1 if direcao == 0 else -1
        lista = []
        for yface, nomes in faces.items():
            barl = (yface == 0.0) == (direcao == 0)
            cp = cb if barl else -cs                         # sotavento: sucção para fora = mesmo sentido do vento
            for i, nm in enumerate(nomes):
                p = next(pp for pp in mg.pil if pp["nome"] == nm)
                for n, fy in _forca_parede(p, lambda zm, i=i: mg.TRIB_X[i], lambda zm, cp=cp: cp).items():
                    lista.append((n, p["x"], sg * fy))
        R = sum(f for _, _, f in lista)
        e = 0.075 * LARG * ecc
        xm = sum(x * f for _, x, f in lista) / R
        den = sum(f * (x - xm) ** 2 for _, x, f in lista)
        c = e * R / den if den else 0.0
        for n, x, f in lista:
            add(n, 0.0, f * (1 + c * (x - xm)))
        # paredes internas (linhas 2 e 4): diferença de pressão interna; +y quando o lado de menor y tem maior pressão
        ca, cab, cpv = interno
        for iy, nomes, xs, dp, port in ((1, ["P1-L2", "P8", "P8A", "P8B", "P2-L2"], [0.0, XE["B"], XC, XE["D"], LARG], ca - cab, []),
                                        (3, ["P1-L4", "P9", "P10a", "P11", "P10b", "P12", "P2-L4"],
                                         [0.0, 9.87, 15.195, XC, 24.305, 29.63, LARG], cab - cpv, PORTOES_L4)):
            for i, nm in enumerate(nomes):
                p = next(pp for pp in mg.pil if pp["nome"] == nm)
                xa = xs[i - 1] if i > 0 else xs[i]; xb = xs[i + 1] if i + 1 < len(xs) else xs[i]
                lados = [(xa, xs[i]), (xs[i], xb)]
                def larg(zm, lados=lados):
                    if zm > H_INT:
                        return 0.0
                    w = 0.0
                    for a, b in lados:
                        aberto = any(abs(a - pa) < 0.05 and abs(b - pb) < 0.05 for pa, pb in port)
                        if not aberto or zm > 7.40:
                            w += abs(b - a) / 2
                    return w
                for n, fy in _forca_parede(p, larg, lambda zm, dp=dp: dp).items():
                    add(n, 0.0, fy)
    else:
        nomes_A = ["P1C-L1"] + [f"P1-L{i+1}" for i in range(1, 8)] + ["P1C-L9"]
        nomes_E = ["P2C-L1"] + [f"P2-L{i+1}" for i in range(1, 8)] + ["P2C-L9"]
        sg = 1 if direcao == 90 else -1
        lista = []
        for xface, nomes in ((0.0, nomes_A), (LARG, nomes_E)):
            barl = (xface == 0.0) == (direcao == 90)
            cp = cb if barl else -cs
            for i, nm in enumerate(nomes):
                p = next(pp for pp in mg.pil if pp["nome"] == nm)
                ya = Y[i - 1] if i > 0 else Y[i]; yb = Y[i + 1] if i + 1 < len(Y) else Y[i]
                def larg(zm, ya=ya, yy=Y[i], yb=yb):
                    w = 0.0
                    for a, b in ((ya, yy), (yy, yb)):
                        aberto = (a >= Y_AB[0] - 1e-6 and b <= Y_AB[1] + 1e-6) and zm < Z_ABERTO
                        if not aberto:
                            w += (b - a) / 2
                    return w
                for n, fx in _forca_parede(p, larg, lambda zm, cp=cp: cp).items():
                    lista.append((n, p["y"], sg * fx))
        R = sum(f for _, _, f in lista)
        e = 0.075 * COMP * ecc
        ym = sum(y * f for _, y, f in lista) / R
        den = sum(f * (y - ym) ** 2 for _, y, f in lista)
        c = e * R / den if den else 0.0
        for n, y, f in lista:
            add(n, f * (1 + c * (y - ym)), 0.0)
    return F


def casos_vento():
    """Lista (nome, direção, ecc, interno) — ELU com vento principal."""
    out = []
    for d in (0, 180):
        cab = CPI_ABERTO[d]
        # portões fechados: extremos de cpi do anexo e do pavilhão; portões abertos: pavilhão = área aberta
        internos = {("fechado", ca, cpv): (ca, cab, cpv) for ca in CPI_FECHADO for cpv in CPI_FECHADO}
        internos[("portões abertos", 0.0, None)] = (0.0, cab, cab)
        # escolhe os 2 extremos de força interna total em y (linha 2: ca − cab; linha 4: cab − cpv)
        tot = {k: (v[0] - v[1]) * 1.0 + (v[1] - v[2]) * 1.6 for k, v in internos.items()}
        kmax, kmin = max(tot, key=tot.get), min(tot, key=tot.get)
        for kk in ([kmax] if internos[kmax] == internos[kmin] else [kmax, kmin]):
            for ecc in (-1, 1):
                out.append((f"V{d} e{ecc:+d} {kk[0]}", d, ecc, internos[kk]))
    for d in (90, 270):
        for ecc in (-1, 1):
            out.append((f"V{d} e{ecc:+d}", d, ecc, (0.0, 0.2, 0.0)))
    return out


CASOS = casos_vento()
FAT_ELU = lambda d: {"G": 1.3, "W": 1.4, "Qm": 1.4 * 0.7, "Qc": 1.4 * 0.5, ("Dy" if d in (0, 180) else "Dx"): 1.3 * (1 if d in (0, 90) else -1)}

# ------------------------------------------------------------------ terça-escora (Z 302): resistências por vão
TE = {e["vao"]: e for e in CB["terca_escora"]["por_vao"]}
TC = CB["terca"]
MNEG = {v["vao"]: abs(v["M_neg"]) for v in TC["por_vao"]}                 # sucção de borda (envoltória do MEF)
_LG = mg.LG
_w = lambda cp: 1.4 * abs(cp) * 0.874 - (_LG["cargas_cob"]["g_favoravel_sucao"] + CB["perfil"]["peso_kNm"] / _LG["passo_tercas"])
R_GERAL = _w(-1.0) / _w(-1.6)
EI_Z = 200e6 * CB["perfil"]["Ix_cm4"] * 1e-8
Y_LOC = min(9.9, 0.15 * LARG)


def interacao_escora(vao, x, Nd):
    e = TE[vao]
    L = e["L_m"]
    beiral = x <= Y_LOC or x >= LARG - Y_LOC
    borda = vao in ("1-2", "8-9") or beiral
    Md = MNEG[vao] * (1.0 if borda else R_GERAL)
    Nex = math.pi ** 2 * EI_Z / L ** 2
    if abs(x - XC) < 0.01:
        Nd /= 2                                                         # 2 terças reais no eixo C
    return Nd / e["NcRd"] + Md / (1 - Nd / Nex) / e["MRd"]


# ------------------------------------------------------------------ variante
def nos_x(n):
    def lado(xs, x0, x1):
        idx = sorted(set(list(range(0, len(xs), n)) + [len(xs) - 1]))
        v = [xs[i] for i in idx]
        v[0], v[-1] = x0, x1
        return v
    return lado(ESQ, 0.0, XC) + lado(DIR, XC, LARG)[1:]


def distorcao(desl):
    """Distorção de cisalhamento da cobertura em cada vão: |Δu_x| entre as linhas i e i+1 (mesmo x) / vão; máximo (1/x)."""
    por_linha = {}
    for k, n in mg.nos.items():
        x, y, z = k[0], k[1], k[2]
        for i, yl in enumerate(Y):
            if abs(y - yl) < 1e-3 and z > 6.9:
                por_linha.setdefault(i, {})[round(x, 2)] = n
    g = 0.0
    for i in range(8):
        a, b = por_linha.get(i, {}), por_linha.get(i + 1, {})
        for x in set(a) & set(b):
            g = max(g, abs(desl[a[x]][0] - desl[b[x]][0]) / (Y[i + 1] - Y[i]))
    return round(1 / g) if g > 0 else None


def avaliar(variante):
    vaos, n = variante
    mg.VAOS_X = [(k, k + 1) for k in vaos]
    mg.XS_X = nos_x(n)
    orig = mg.__dict__["_cargas_orig"] if "_cargas_orig" in mg.__dict__ else mg.cargas_basicas
    mg.__dict__["_cargas_orig"] = orig
    res = dict(vaos=[f"{k+1}-{k+2}" for k in vaos], painel_espacos=n, casos={})
    Tmax, esc_max, esc_pior, falhas = 0.0, 0.0, None, set()
    for nome, d, ecc, interno in CASOS + [("ELS V0", 0, 1, (0.0, -0.6, 0.0)), ("ELS V90", 90, 1, (0.0, 0.2, 0.0))]:
        def cargas(d=d, ecc=ecc, interno=interno):
            C = orig()
            C["W"] = vento(d, ecc, interno)          # depois do montar(): nós do modelo atual
            return C
        mg.cargas_basicas = cargas
        els = nome.startswith("ELS")
        fat = {"G": 1.0, "W": 0.3, "Qm": 0.6} if els else FAT_ELU(d)
        ok, desl, base, forcas = mg.rodar(nome, fat, 1.0 if els else mg.F_ELU, True)
        gam = distorcao(desl)
        if els:
            res["casos"][nome] = dict(desl_max_mm=round(max(math.hypot(v[0], v[1]) for v in desl.values()) * 1000, 1), distorcao=gam)
            continue
        tx = forcas.get("X Ø16", [0.0, 0.0])[1]
        Tmax = max(Tmax, tx)
        for vao, linhas in mg.POR_VAO.get("terça-escora por linha", {}).items():
            for xs, (nmin, _) in linhas.items():
                it = interacao_escora(vao, float(xs), max(0.0, -nmin))
                if it > 1.0:
                    falhas.add((vao, xs))
                if it > esc_max:
                    esc_max, esc_pior = it, dict(caso=nome, vao=vao, x=float(xs), Nd=round(-nmin, 1), interacao=round(it, 3))
        Mb = max(math.hypot(b["Mx"], b["My"]) for b in base.values())
        res["casos"][nome] = dict(ok=ok, T_diag=round(tx, 2), escora_N_min=round(forcas["terça-escora"][0], 1), M_base_max=round(Mb, 1), distorcao=gam)
    mg.cargas_basicas = orig
    # bitola e custo
    dmin = next((d for d in (12.5, 16.0, 19.0, 22.0, 25.0) if barra_redonda_tracao_Rd(d) >= Tmax * 1.0), 25.0)
    xs = nos_x(n)
    n_pan = len(xs) - 1
    L_diag = []
    for k in vaos:
        Ly = Y[k + 1] - Y[k]
        for a, b in zip(xs[:-1], xs[1:]):
            L_diag += [math.hypot(b - a, Ly)] * 2
    kgm = math.pi * dmin ** 2 / 4 * 7.85e-3
    kg = sum(L_diag) * kgm
    n_d = len(L_diag)
    n_esc_falha = len(falhas)
    kg_reforco = n_esc_falha * 10.0 * (11.27 - 8.92)                      # escora que não passa: Z 302×2,70 no vão
    custo = 14.0 * kg + 55.0 * n_d + 2 * 30.0 * n_d + 80.0 * n_d + 13.0 * kg_reforco
    res.update(T_max=round(Tmax, 2), diametro=dmin, n_diagonais=n_d, L_diag_m=[round(min(L_diag), 2), round(max(L_diag), 2)] if L_diag else [0, 0],
               ang_graus=round(math.degrees(math.atan2(Y[2] - Y[1], (xs[1] - xs[0]))), 1) if n_pan else None, kg_X=round(kg), escora_interacao_max=round(esc_max, 3),
               escora_pior=esc_pior, escoras_reprovadas=n_esc_falha, kg_reforco_escoras=round(kg_reforco),
               desl_ELS_mm=max(v.get("desl_max_mm", 0) for v in res["casos"].values()),
               distorcao_ELS=min((v["distorcao"] for k_, v in res["casos"].items() if k_.startswith("ELS") and v.get("distorcao")), default=None),
               distorcao_ELU=min((v["distorcao"] for k_, v in res["casos"].items() if not k_.startswith("ELS") and v.get("distorcao")), default=None),
               M_base_max=max(v.get("M_base_max", 0) for v in res["casos"].values()), custo_R=round(custo))
    return res


def rodar_lote(lista, procs=2):
    with Pool(procs) as pool:
        return pool.map(avaliar, lista, chunksize=1)


if __name__ == "__main__":
    etapa1 = [(tuple(c), 8) for r in range(0, 9) for c in itertools.combinations(range(8), r)]
    if os.environ.get("RAPIDO"):
        etapa1 = etapa1[:6]
    r1 = rodar_lote(etapa1)
    ok1 = sorted([r for r in r1], key=lambda r: (r["escoras_reprovadas"] > 0, r["custo_R"]))
    top = [tuple(int(v.split("-")[0]) - 1 for v in r["vaos"]) for r in ok1[:12]]
    etapa2 = [(t, n) for t in top for n in (2, 4, 16)]
    r2 = rodar_lote(etapa2)
    todos = r1 + r2
    viaveis = sorted([r for r in todos if r["escoras_reprovadas"] == 0], key=lambda r: r["custo_R"])
    atual = next((r for r in todos if r["vaos"] == ["2-3", "7-8"] and r["painel_espacos"] == 2), None)
    out = dict(metodo=__doc__, casos=[c[0] for c in CASOS], atual=atual, melhores=viaveis[:20], todos=todos)
    (AQ / "estudo_contraventamento.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("variantes", len(todos), "viáveis", len(viaveis))
    for r in viaveis[:12]:
        print(r["vaos"], r["painel_espacos"], f"Ø{r['diametro']}", r["n_diagonais"], r["kg_X"], "kg", "T", r["T_max"], "esc", r["escora_interacao_max"], "desl", r["desl_ELS_mm"], "R$", r["custo_R"])
