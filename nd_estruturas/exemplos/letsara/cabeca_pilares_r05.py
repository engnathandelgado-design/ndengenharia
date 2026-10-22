"""DEC-042 — cabeça (platibanda) dos pilares 40×60 da Letsara: geometria dos cantos e armadura própria da cabeça.

Pedido do Nathan (22/10/2026): (A) "a platibanda tem carga menor — apoio e içamento fora dela, e ver se dá para ter menos
ferragem nessa parte"; (B) "os pilares do canto precisam de mais área de platibanda concretada para montar as peças
metálicas da platibanda".

Esforços na cabeça (balanço a partir do recuo, NBR 6118:2023 e NBR 9062:2017):
- vento nas placas da platibanda, que chega ao pilar pelos consoles CS-1 de cada fiada acima do recuo: Fd = 13,81 kN por
  console (fixacao_placas.json, q0 0,874 kPa × cp 1,6 × γf 1,4), nos dois sentidos (sobrepressão e sucção);
- peso das placas pendurado nos consoles com excentricidade e = 7,5 cm da face (folga 2,5 + meia placa 5): γf 1,4
  desfavorável (soma com a sucção) e 1,0 favorável (desconta da sobrepressão);
- força normal desprezada (a favor da segurança na flexão).
Nos pilares de canto as placas das duas fachadas chegam à cabeça: flexão em cada direção, separadamente (vento a 0° e 90°).

Seção resistente: barras do corpo que sobem até o topo (fileira da face C, w ≤ −240) + barras N13 da cabeça junto à face
interna (recuo) e, se preciso, N13C intercaladas na face C. MRd por compatibilidade de deformações (N = 0).
Ancoragem das N13 no corpo: traspasse l0t = α0t · lb · As,calc/As,ef (NBR 6118:2023 9.5.2.2), α0t = 2,0 (todas emendadas
na mesma seção), lb com má aderência (pilar concretado deitado; barras a menos de 30 cm do topo da fôrma), mínimo 60 cm.
Alças AL-2 e furo FI-1 conferidos: ficam no corpo (abaixo do recuo) em todas as marcas.

Grava cabeca_pilares.json (lido por pilares_familia.py / pilar_generico.py)."""
import json, math
from pathlib import Path
from manuseio_pilares_r05 import MRd0

AQ = Path(__file__).resolve().parent
PR = Path("/home/claude/letsara/pranchas")
FX = json.loads((AQ / "fixacao_placas.json").read_text(encoding="utf-8"))
ARR = json.loads((AQ / "arranjo_pilares.json").read_text(encoding="utf-8"))
VW = FX["cargas_por_console"]["vento_d_kN"]                   # kN por console (de cálculo)
GK = FX["cargas_por_console"]["G_k_kN"]                       # kN por console (característico)
E_PL = 0.075                                                  # m, excentricidade do peso da placa à face do pilar
COB, PHI_T = 30, 6.3
FCK, FYK = 40.0, 500.0
FYD = FYK / 1.15
AREA = {10.0: 78.5, 12.5: 122.7, 16.0: 201.1}
KG_M = {10.0: 0.617, 12.5: 0.963, 16.0: 1.578}
RECUO_CANTO = {"A": 200}                                      # DEC-042: canto sem recuo lateral; recuo A 30 → 20 cm


def lb_ma(phi):
    fctd = 0.7 * 0.3 * FCK ** (2 / 3) / 1.4
    fbd = 2.25 * 0.7 * 1.0 * fctd                              # η1 nervurada 2,25; η2 0,7 má aderência
    return phi / 4 * FYD / fbd


def l0t(phi, ratio):
    lb = lb_ma(phi)
    a0t = 2.0
    l0 = a0t * lb * min(1.0, ratio)
    l0min = max(0.3 * a0t * lb, 15 * phi, 200)
    return max(l0, l0min)


def forcas(g, rec):
    """momentos de cálculo na base da cabeça (kN·m): por direção, sucção (tração na face interna) e sobrepressão."""
    zr = rec["z"]
    out = {"C": dict(Mv=0.0, Mg_d=0.0, Mg_f=0.0, n=0), "L": dict(Mv=0.0, Mg_d=0.0, Mg_f=0.0, n=0)}
    for ip in g["ip01"]:
        dirc = "C" if ip["face"] == "C" else ("L" if ip["face"] in "BD" else None)
        if dirc is None:
            continue
        lados = ip.get("lados") or [None] * len(ip["z"])
        for z, ld in zip(ip["z"], lados):
            if z <= zr:
                continue
            n = len(ld) if ld else 1                          # face lateral do canto: 1 ponta de placa por fiada
            a = (z - zr) / 1000
            o = out[dirc]
            o["Mv"] += n * VW * a
            o["Mg_d"] += n * 1.4 * GK * E_PL
            o["Mg_f"] += n * 1.0 * GK * E_PL
            o["n"] += n
    return out


def secao_cabeca(B, H, rec):
    d = rec["d"]
    u0, u1 = -B / 2 + d.get("D", 0), B / 2 - d.get("B", 0)
    w0, w1 = -H / 2 + d.get("C", 0), H / 2 - d.get("A", 0)
    return u0, u1, w0, w1


def mrd(bars, u0, u1, w0, w1, eixo, tracao_interna):
    """bars: [(u, w, A)]. eixo 'w': flexão no plano A–C (vento ⊥ face C); tracao_interna = tração na face do recuo (w1).
    eixo 'u': flexão no plano B–D (vento ⊥ face lateral do canto), o menor dos dois sentidos.
    MRd0 comprime o lado +y da seção."""
    uc, wc = (u0 + u1) / 2, (w0 + w1) / 2
    if eixo == "w":
        sg = -1 if tracao_interna else 1                      # tração interna → comprime a face C (w0) → espelha
        return MRd0(u1 - u0, w1 - w0, [(0.0, sg * (w - wc), A) for u, w, A in bars], "y")
    return min(MRd0(w1 - w0, u1 - u0, [(0.0, sg * (u - uc), A) for u, w, A in bars], "y") for sg in (1, -1))


def dimensionar(mk, g, canto):
    B, H = g["B"], g["H"]
    rec = dict(z=g["rec"]["z"], d=dict(RECUO_CANTO) if canto else dict(g["rec"]["d"]))
    u0, u1, w0, w1 = secao_cabeca(B, H, rec)
    hc = g["L_TOT"] - rec["z"]
    a = ARR[mk]
    d_corpo = a["d"]
    sobe = [(u, w) for u, w in a["xy"] if u0 + 40 <= u <= u1 - 40 and w0 + 40 <= w <= -240]
    F = forcas(g, rec)
    cobr = COB + PHI_T
    w_in = w1 - cobr - 8                                       # eixo da N13 junto à face interna
    melhores = []
    for phi in (10.0, 12.5, 16.0):
        for n_in in range(2, 7):
            us_in = [u0 + cobr + phi / 2 + k * (u1 - u0 - 2 * (cobr + phi / 2)) / (n_in - 1) for k in range(n_in)]
            for n_cx in range(0, 4):                           # N13C intercaladas na face C (entre as que sobem)
                xs_c = sorted(u for u, w in sobe if w < w0 + 80)
                livres = []
                if n_cx:                                      # malha uniforme na face C; novas onde não há barra do corpo a < 40 mm
                    N = len(xs_c) + n_cx
                    grade = [u0 + cobr + phi / 2 + k * (u1 - u0 - 2 * (cobr + phi / 2)) / (N - 1) for k in range(N)]
                    livres = [u for u in grade if all(abs(u - x) > 40 for x in xs_c)]
                if n_cx > len(livres):
                    continue
                bars = [(u, w, AREA[float(d_corpo)]) for u, w in sobe] + [(u, w_in, AREA[phi]) for u in us_in] + \
                       [(u, w0 + cobr + phi / 2, AREA[phi]) for u in livres[:n_cx]]
                As = sum(A for *_, A in bars)
                if As < 0.004 * (u1 - u0) * (w1 - w0):          # armadura mínima de pilar (NBR 6118 17.3.5.3.1)
                    continue
                Md_in = F["C"]["Mv"] + F["C"]["Mg_d"]
                Md_C = max(0.0, F["C"]["Mv"] - F["C"]["Mg_f"])
                M_in = mrd(bars, u0, u1, w0, w1, "w", True)
                M_C = mrd(bars, u0, u1, w0, w1, "w", False)
                usos = [Md_in / M_in if Md_in else 0.0, Md_C / M_C if Md_C else 0.0]
                if canto and F["L"]["n"]:
                    Md_L = F["L"]["Mv"] + F["L"]["Mg_d"]
                    usos.append(Md_L / mrd(bars, u0, u1, w0, w1, "u", True))
                if max(usos) > 1.0:
                    continue
                ratio = max(usos[0], usos[1])
                emb = math.ceil(max(600, l0t(phi, ratio)) / 50) * 50
                L13 = hc - 40 + emb
                if L13 > 12000:
                    continue
                kg = (n_in + n_cx) * KG_M[phi] * L13 / 1000
                melhores.append(dict(phi=phi, n_in=n_in, n_cx=n_cx, emb=emb, L13=round(L13), kg=round(kg, 1), usos=[round(x, 2) for x in usos],
                                     Md_in=round(Md_in, 1), Md_C=round(Md_C, 1), Md_L=round(F["L"]["Mv"] + F["L"]["Mg_d"], 1) if F["L"]["n"] else 0.0,
                                     MRd_in=round(M_in, 1), MRd_C=round(M_C, 1), n_sobe=len(sobe), us_in=[round(u) for u in us_in],
                                     us_cx=[round(u) for u in livres[:n_cx]]))
    if not melhores:
        raise ValueError(f"{mk}: nenhuma armadura de cabeça passa")
    best = min(melhores, key=lambda r: (r["kg"], r["n_in"] + r["n_cx"]))
    return rec, hc, F, best


def antes(mk, g):
    """armadura da cabeça como saiu na rev08 (4 N13 Ø16 junto ao recuo + cantos livres, 60 cm no corpo) e o uso dela."""
    B, H, rec = g["B"], g["H"], g["rec"]
    u0, u1, w0, w1 = secao_cabeca(B, H, rec)
    a = ARR[mk]
    sobe = [(u, w) for u, w in a["xy"] if u0 + 40 <= u <= u1 - 40 and w0 + 40 <= w <= -240]
    cantos = [(u, w) for u in (u0 + COB + 18, u1 - COB - 18) for w in (w0 + COB + 18, w1 - COB - 18)]
    cantos += [(u0 + COB + 18 + k * (u1 - u0 - 2 * (COB + 18)) / 3, w1 - COB - 16) for k in range(4)]
    cab = []
    for c in cantos:
        if all(math.hypot(c[0] - x, c[1] - y) > 40 for x, y in sobe + cab):
            cab.append(c)
    hc = g["L_TOT"] - rec["z"]
    F = forcas(g, rec)
    bars = [(u, w, AREA[float(a["d"])]) for u, w in sobe] + [(u, w, AREA[16.0]) for u, w in cab]
    Md_in = F["C"]["Mv"] + F["C"]["Mg_d"]
    Md_C = max(0.0, F["C"]["Mv"] - F["C"]["Mg_f"])
    us = [Md_in / mrd(bars, u0, u1, w0, w1, "w", True), Md_C / mrd(bars, u0, u1, w0, w1, "w", False) if Md_C else 0.0]
    if F["L"]["n"]:
        us.append((F["L"]["Mv"] + F["L"]["Mg_d"]) / mrd(bars, u0, u1, w0, w1, "u", True))
    L13 = hc - 40 + 600
    return dict(n13=len(cab), kg=round(len(cab) * KG_M[16.0] * L13 / 1000, 1), usos=[round(x, 2) for x in us], secao=f"{u1 - u0:.0f}×{w1 - w0:.0f}")


if __name__ == "__main__":
    res = {}
    print(f"{'marca':6s} {'cabeça':>9s} {'h':>5s} | antes: N13 kg usos | depois: N13 kg emb usos | Md_in Md_C Md_L | AL-2 / FI-1 no corpo?")
    for f in sorted(PR.glob("P[LF]-*_geom.json")):
        g = json.loads(f.read_text())
        mk = g["marca"]
        canto = mk in ("PL-03", "PL-04", "PL-07", "PL-08")
        rec, hc, F, best = dimensionar(mk, g, canto)
        av = antes(mk, g)
        al_ok = all(z < rec["z"] - 165 for z in g["al"])
        fi_ok = g["fi"]["z"] + g["fi"]["d"] / 2 < rec["z"]
        u0, u1, w0, w1 = secao_cabeca(g["B"], g["H"], rec)
        res[mk] = dict(rec=rec, h_cabeca=hc, secao=f"{u1 - u0:.0f}×{w1 - w0:.0f}", antes=av, depois=best, AL2_no_corpo=al_ok, FI1_no_corpo=fi_ok,
                       z_AL2=g["al"], z_FI1=g["fi"]["z"], z_recuo=rec["z"])
        print(f"{mk:6s} {av['secao']:>4s}→{res[mk]['secao']:<7s} {hc:5.0f} | {av['n13']} Ø16 {av['kg']:5.1f} {av['usos']} | "
              f"{best['n_in']}+{best['n_cx']} Ø{best['phi']:g} {best['kg']:5.1f} {best['emb']} {best['usos']} | "
              f"{best['Md_in']} {best['Md_C']} {best['Md_L']} | {al_ok} / {fi_ok}")
    (AQ / "cabeca_pilares.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    (PR / "cabeca_pilares.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
