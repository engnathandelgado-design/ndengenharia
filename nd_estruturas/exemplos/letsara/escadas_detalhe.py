"""Letsara rev09d (24/10/2026, DEC-060) — escadas metálicas: modelo ÚNICO de detalhamento das duas escadas (interna ES01 e
externa ES02), com guarda-corpo e corrimão pela RT CBMRS nº 11 Parte 01/2016 e todas as ligações parafusadas, compatíveis e
verificadas automaticamente. É a fonte das peças do 3D/IFC (modelo_bim.py), das folhas ES01/ES02/ES03 e da lista de material.

Pedidos do Nathan (24/10): "faltou os corrimãos seguindo a norma do Corpo de Bombeiros do RS" e "faltou compatibilidade de
conexão entre as peças metálicas das escadas"; perfis no limite (o mais leve que passa); pé-direito ≥ 2,10 m sob as vigas.

Regras adotadas (RT CBMRS nº 11 Parte 01/2016 — saídas de emergência; NBR 9077 / NBR 14718 como referência):
  - corrimão nos DOIS lados de todos os lances, a 0,90 m acima do bocel (faixa 0,80–0,92), tubo redondo Ø 38–65 mm, afastado
    ≥ 40 mm de parede ou de qualquer peça, contínuo nos patamares; carga 900 N concentrada em qualquer ponto;
  - guarda-corpo em todo lado livre (lances, patamares, abertura da laje): 1,05 m nos patamares e pisos internos, 0,92 m nos
    lances internos (medido na vertical do bocel), 1,30 m na escada externa; vãos que não deixam passar esfera de 15 cm;
    carga horizontal 730 N/m no topo e 1,20 kPa no fechamento (não simultâneas);
  - pé-direito livre ≥ 2,10 m sobre toda a faixa de circulação (lances e patamares).
Ligações (NBR 8800:2024 6.3): parafusos ASTM A325/8.8 galvanizados, furo padrão d + 1,5 mm; distância mínima do centro do furo à
borda (Tab. 14, borda cortada): M10 18, M12 22, M16 29 mm; entre furos ≥ 3 d; o furo tem de ficar no trecho plano da peça (fora de
mesas e raios, com folga de chave ≥ 1,4 d da face da mesa — porca). Cada ligação é conferida aqui: furos dentro das DUAS peças
ligadas, bordas, espaçamentos, faixa comum de altura entre as peças e resistência (corte do parafuso, pressão de contato).
Sem solda em nenhuma etapa (regra ND): perfis cortados e furados, cantoneiras e chapas dobradas parafusadas.
Unidades: m e kN nas peças; mm nas tabelas de ligação. Grava escadas.json."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

AQ = Path(__file__).resolve().parent
sys.path.insert(0, str(AQ.parents[1])); sys.path.insert(0, str(AQ))
from nd_estruturas import metalica_laminada as ML
from geometria import ESCADA, ESCADA_EXT, Y_LIN, X_EIXO, Z_PISOS, Z_PISO_PRONTO, Z_APOIO_LAJE, P6_ESC, P7_ESC, P6_L2, ABERTURA

E_ACO, FY36, FU36, GA1, GA2 = 200e6, 250e3, 400e3, 1.10, 1.35
FUB = 825e3                                                      # ASTM A325 / 8.8
Q = json.loads((AQ / "cargas_mezanino.json").read_text(encoding="utf-8"))["escada"]["sobrecarga"]     # 3,0 kN/m²
H_GC, Q_GC, P_CR = 0.73, 1.20, 0.90                              # kN/m no topo, kPa no fechamento, kN no corrimão (CBMRS / NBR 14718)
GAMA_Q = 1.5
BORDA = {8: 14, 10: 18, 12: 22, 16: 29, 20: 35}                  # NBR 8800:2024 Tab. 14 (borda cortada), mm
TCHAVE = {8: 12, 10: 15, 12: 18, 16: 23}                         # folga mínima furo × face de mesa/aba perpendicular (cabeça/porca + chave), mm

# ------------------------------------------------------------------ perfis (catálogo Gerdau; tubos e cantoneiras ASTM A36)
U = {"U 102 × 7,95 (4\")": dict(d=101.6, bf=40.2, tw=4.57, tf=7.5, kg=7.95, A=10.1, Ix=159.5, Wx=31.4),
     "U 152 × 12,2 (6\")": dict(d=152.4, bf=48.8, tw=5.08, tf=8.7, kg=12.2, A=15.5, Ix=546.0, Wx=71.7),
     "U 203 × 17,1 (8\")": dict(d=203.2, bf=57.4, tw=5.59, tf=9.9, kg=17.1, A=21.8, Ix=1356.0, Wx=133.4)}
L_ = {"L 51 × 51 × 4,8": (51, 4.8, 3.63), "L 64 × 64 × 4,8": (64, 4.8, 4.57), "L 76 × 76 × 6,3": (76, 6.3, 7.29),
      "L 76 × 51 × 6,3": (76, 6.3, 6.10), "L 102 × 102 × 6,3": (102, 6.3, 9.82), "L 102 × 102 × 9,5": (102, 9.5, 14.6)}


def tubo_q(b, t):
    """tubo quadrado b × t (mm): A cm², I cm⁴, W cm³, kg/m (cantos vivos — a favor na flambagem por r)."""
    A = (b * b - (b - 2 * t) ** 2) / 100
    I = (b ** 4 - (b - 2 * t) ** 4) / 12 / 1e4
    return dict(nome=f"tubo {b:g} × {b:g} × {t:g}".replace(".", ","), b=b, t=t, A=A, I=I, W=I / (b / 20), kg=A * 0.785)


def tubo_r(D, t):
    A = math.pi * (D * D - (D - 2 * t) ** 2) / 4 / 100
    I = math.pi * (D ** 4 - (D - 2 * t) ** 4) / 64 / 1e4
    return dict(nome=f"tubo Ø{D:g} × {t:g}".replace(".", ","), D=D, t=t, A=A, I=I, W=I / (D / 20), kg=A * 0.785)


TUBOS_Q = [tubo_q(b, t) for b, t in ((40, 2.0), (40, 3.0), (40, 4.0), (50, 2.0), (50, 3.0), (60, 2.0), (60, 3.0), (70, 3.0), (80, 3.0), (80, 4.75))]
TUBOS_R = [tubo_r(D, t) for D, t in ((38.1, 2.0), (38.1, 2.65), (42.2, 2.65), (48.3, 2.65), (48.3, 3.0))]


def chi(lam0):                                                  # NBR 8800:2024 5.3.3
    return 0.658 ** (lam0 ** 2) if lam0 <= 1.5 else 0.877 / lam0 ** 2


def NRd_tubo(tb, L):
    r = math.sqrt(tb["I"] / tb["A"]) / 100
    lam = L / r
    lam0 = lam / math.pi * math.sqrt(FY36 / E_ACO)
    bt = (tb["b"] - 2 * tb["t"]) / tb["t"]
    Qa = 1.0 if bt <= 1.40 * math.sqrt(E_ACO / FY36) else 0.0
    return chi(lam0) * Qa * tb["A"] * 1e-4 * FY36 / GA1, lam


def parafuso_corte(d, n_planos=1):
    Ab = math.pi * d * d / 4 * 1e-6
    return n_planos * 0.4 * FUB * Ab / GA2                        # NBR 8800:2024 6.3.3.2 (rosca no plano de corte: 0,4)


def contato(d, t_mm, fu=FU36):
    return 2.4 * d * t_mm * 1e-6 * fu / GA2                       # 6.3.3.3 (deformação no furo limitada)


# ================================================================== 1. ESCADA INTERNA (ES01) — geometria
EI = ESCADA
e_int, p_int = EI["espelho"], EI["piso"]
N_INT = round(EI["z_patamar"] / e_int)                          # espelhos por lance (11)
X6, XE_ = EI["x_face_P6"], EI["x_face_E"]
GAP = 0.10
BL = round((XE_ - X6 - GAP) / 2, 3)                              # 1,40
Z_PAT = EI["z_patamar"]
Y_PAT, Y_LAN, Y_CHE = EI["y_patamar"], EI["y_lances"], EI["y_chegada"]
T_CH = 0.0063                                                    # chapa xadrez dos pisos
T_DG = 0.00475                                                   # chapa xadrez dos degraus
A_LONG = -0.030                                                  # topo da longarina 30 mm abaixo da linha dos bocéis (ver ajuste_longarina)


class Lance:
    """lance reto: s = distância em planta a partir da linha do 1º espelho, no sentido da subida; c = coordenada ao longo do
    lance (y ou x da obra) = c0 + sg·s; faixa lateral [l0, l1] na outra coordenada; espelhos n, altura e, piso p; z0 = nível de baixo."""

    def __init__(self, nome, eixo, c0, sg, l0, l1, z0, n, e, p, perfil):
        self.nome, self.eixo, self.c0, self.sg, self.l0, self.l1, self.z0, self.n, self.e, self.p = nome, eixo, c0, sg, l0, l1, z0, n, e, p
        self.u = U[perfil]; self.perfil = perfil
        self.th = math.atan(e / p)
        self.Dv = self.u["d"] / 1000 / math.cos(self.th)       # altura da longarina na vertical
        self.a = A_LONG

    def c(self, s):
        return self.c0 + self.sg * s

    def s_de(self, c):
        return (c - self.c0) * self.sg

    def z_nosing(self, s):
        return self.z0 + self.e + s * self.e / self.p

    def z_top(self, s):
        return self.z_nosing(s) + self.a

    def z_bot(self, s):
        return self.z_top(s) - self.Dv

    def z_degrau(self, k):
        return self.z0 + k * self.e

    def pt(self, s, lat, z):
        """ponto da obra (x, y, z) a partir de (s, lateral, z)."""
        return (lat, self.c(s), z) if self.eixo == "y" else (self.c(s), lat, z)

    @property
    def L_h(self):
        return (self.n - 1) * self.p


# lances internos: lance 1 sobe de y 8,35 a 5,55 (−y), lance 2 de 5,55 a 8,35 (+y)
PERF_LONG_INT = "U 152 × 12,2 (6\")"
L1 = Lance("lance 1", "y", Y_LAN[1], -1, X6, X6 + BL, 0.0, N_INT, e_int, p_int, PERF_LONG_INT)
L2 = Lance("lance 2", "y", Y_LAN[0], +1, XE_ - BL, XE_, Z_PAT, N_INT, e_int, p_int, PERF_LONG_INT)
# escada externa (fachada A): lance de baixo sobe em +x de x −3,07 a −1,95; lance de cima sobe em −y de y 6,92 a 2,44
EX = ESCADA_EXT
Z_PAT_E, Z_CHE_E = EX["n_baixo"] * EX["espelho"], EX["n_esp"] * EX["espelho"]
LB = Lance("lance de baixo", "x", EX["x_lance_baixo"][1], +1, EX["y_patamar"][0], EX["y_patamar"][1], 0.0, EX["n_baixo"], EX["espelho"], EX["piso"], "U 152 × 12,2 (6\")")
LC = Lance("lance de cima", "y", EX["y_lance_cima"][1], -1, EX["x_ext"], EX["x_int"], Z_PAT_E, EX["n_cima"], EX["espelho"], EX["piso"], "U 203 × 17,1 (8\")")
LANCES = dict(L1=L1, L2=L2, LB=LB, LC=LC)


# ================================================================== 2. dimensionamento (o mais leve que passa)
G_DEG = T_DG * 78.5 * 1.15 + 0.10                                # kN/m² na rampa (chapa + dobras + cantoneiras)
G_PAT = T_CH * 78.5 + 0.0457 * 0.0981 / 0.60 * 10                # chapa 6,3 + barrotes L 64 a cada 60 cm (kN/m²)


def ajuste_longarina(ln: Lance, cant=("L 51 × 51 × 4,8", 0.080, 0.100)):
    """faixa de 'a' (topo da longarina − linha dos bocéis) em que a cantoneira de apoio do degrau cabe inteira na alma da
    longarina (mesas para fora, alma do lado dos degraus) com os furos a ≥ (tf + 15) mm das mesas; devolve (a_min, a_max)."""
    lw, t, _ = L_[cant[0]]
    Lc, d0 = cant[1], cant[2]
    m = (ln.u["tf"] + 15) / 1000 / math.cos(ln.th)
    tg = ln.e / ln.p
    a_min = -(d0 * tg) - T_DG + m                                  # topo: cantoneira (topo) abaixo do topo da longarina no início
    a_max = ln.Dv - (d0 + Lc) * tg - T_DG - lw / 1000 - m          # fundo: aba vertical acima do fundo no fim da cantoneira
    return round(a_min, 4), round(a_max, 4)


def dim_longarina(ln: Lance, carga_gc=True):
    """flexão (mesa comprimida travada pelos degraus), flecha L/350, f1 ≥ 5 Hz e COMPATIBILIDADE (cantoneira do degrau cabe)."""
    L = math.hypot(ln.L_h, ln.n * ln.e)
    B = ln.l1 - ln.l0
    res = []
    for nome, u in U.items():
        w = (1.4 * G_DEG * L / ln.L_h + 1.5 * Q) * B / 2 + 1.4 * u["kg"] * 9.81e-3 * L / ln.L_h
        Md = w * ln.L_h ** 2 / 8
        MRd = u["Wx"] * 1e-6 * FY36 / GA1
        wk = (G_DEG * L / ln.L_h + Q) * B / 2
        fl = 5 * wk * ln.L_h ** 4 / (384 * E_ACO * u["Ix"] * 1e-8)
        m_lin = ((G_DEG + 0.3 * Q) * B / 2 * 1000 / 9.81 + u["kg"]) * L / ln.L_h
        f1 = math.pi / (2 * L ** 2) * math.sqrt(E_ACO * u["Ix"] * 1e-8 * 1000 / m_lin)
        lt = Lance("t", ln.eixo, ln.c0, ln.sg, ln.l0, ln.l1, ln.z0, ln.n, ln.e, ln.p, nome)
        amin, amax = ajuste_longarina(lt)
        r = dict(perfil=nome, Md=round(Md, 2), MRd=round(MRd, 2), uso=round(Md / MRd, 3), flecha_mm=round(fl * 1e3, 1), lim_mm=round(ln.L_h / 350 * 1e3, 1),
                 f1_Hz=round(f1, 1), cabe_cantoneira=amin <= amax, a_faixa_mm=(round(amin * 1000, 1), round(amax * 1000, 1)), kg_m=u["kg"], R_d=round(w * ln.L_h / 2, 1))
        r["ok"] = r["uso"] <= 1 and r["flecha_mm"] <= r["lim_mm"] and r["f1_Hz"] >= 5 and r["cabe_cantoneira"]
        res.append(r)
    ok = [r for r in res if r["ok"]]
    return min(ok, key=lambda r: r["kg_m"]), res


def dim_viga(vao, faixa, P_list, extra_w=0.0, balanco=0.0):
    """viga W biapoiada (opcional balanço numa ponta): faixa de piso + cargas concentradas (P kN, x m) — W mais leve que passa
    (flexão com FLT, Lb = vão, Cb 1; flecha L/350)."""
    out = []
    for nm in ("W 150 x 9,2", "W 150 x 10,4", "W 150 x 13,0", "W 150 x 18,0", "W 150 x 22,5"):
        p = ML.perfil(nm)
        w = (1.4 * G_PAT + 1.5 * Q) * faixa + 1.4 * p.massa * 9.81e-3 + extra_w
        M = w * vao ** 2 / 8 + sum(P * x * (vao - x) / vao for P, x in P_list)
        Mb = w * balanco ** 2 / 2
        Ra = w * vao / 2 + sum(P * (vao - x) / vao for P, x in P_list) - Mb / vao if vao else 0
        Rb = w * (vao + balanco) + sum(P for P, _ in P_list) - Ra
        MRd = ML.momento_resistente(p, max(vao, balanco * 2), 1.0).MRd
        EI_ = E_ACO * p.Ix * 1e-8
        wk = (G_PAT + Q) * faixa + p.massa * 9.81e-3
        fl = 5 * wk * vao ** 4 / (384 * EI_) + sum(P / 1.45 * vao ** 3 / (48 * EI_) for P, _ in P_list)
        flb = wk * balanco ** 4 / (8 * EI_)
        r = dict(perfil=nm.replace(" x ", " × "), vao=round(vao, 3), balanco=balanco, Md=round(max(M, Mb), 2), MRd=round(MRd, 1), uso=round(max(M, Mb) / MRd, 3),
                 R_a=round(Ra, 1), R_b=round(Rb, 1), flecha_mm=round(max(fl, flb) * 1e3, 1), lim_mm=round(max(vao / 350, 2 * balanco / 350) * 1e3, 1), kg_m=p.massa,
                 d=p.d, bf=p.bf, tw=p.tw, tf=p.tf)
        r["ok"] = r["uso"] <= 1 and r["flecha_mm"] <= r["lim_mm"]
        out.append(r)
    return min((r for r in out if r["ok"]), key=lambda r: r["kg_m"])


def dim_pilarete(N, h, H=0.0):
    for tb in TUBOS_Q:
        if tb["b"] < 60:                                           # 60 mínimo: 2 cantoneiras + M12 passante e apoio da viga W 150
            continue
        NRd, lam = NRd_tubo(tb, h)
        MRd = tb["W"] * 1e-6 * FY36 / GA1
        u = N / NRd + (8 / 9 * H * h / MRd if N / NRd >= 0.2 else H * h / MRd)
        if lam <= 200 and u <= 1.0:
            return dict(perfil=tb["nome"], b=tb["b"], t=tb["t"], h=round(h, 3), Nd=round(N, 1), NRd=round(NRd, 1), lambda_=round(lam), uso=round(u, 3), kg_m=round(tb["kg"], 2))
    raise ValueError("pilarete não passa")


def dim_barrote(vao):
    for nm in ("L 51 × 51 × 4,8", "L 64 × 64 × 4,8", "L 76 × 76 × 6,3"):
        b, t, kg = L_[nm]
        # cantoneira com a aba horizontal no topo (apoio da chapa): W e I em torno do eixo paralelo à aba (cantos simples)
        yc = (b * t * t / 2 + (b - t) * t * (t + (b - t) / 2)) / (b * t + (b - t) * t)
        I = (b * t ** 3 / 12 + b * t * (yc - t / 2) ** 2 + t * (b - t) ** 3 / 12 + t * (b - t) * (t + (b - t) / 2 - yc) ** 2) * 1e-12
        W = I / ((b - yc) / 1000)
        w = (1.4 * T_CH * 78.5 + 1.5 * Q) * 0.60 + 1.4 * kg * 9.81e-3
        M = w * vao ** 2 / 8
        MRd = W * FY36 / GA1
        fl = 5 * ((T_CH * 78.5 + Q) * 0.6) * vao ** 4 / (384 * E_ACO * I)
        if M <= MRd and fl <= vao / 350:
            return dict(perfil=nm, vao=round(vao, 3), Md=round(M, 2), MRd=round(MRd, 2), uso=round(M / MRd, 3), flecha_mm=round(fl * 1e3, 1), lim_mm=round(vao / 350 * 1e3, 1), kg_m=kg)
    raise ValueError("barrote")


# ================================================================== 3. guarda-corpo e corrimão (CBMRS RT 11)
def dim_gc(h_gc, s, b_max=None):
    """montante (tubo quadrado), travessa superior (tubo), corrimão (tubo redondo Ø 38–65), barras Ø12,7 do fechamento e cantoneiras
    que prendem as barras. Retorna os mais leves que passam para altura h_gc e espaçamento s entre montantes."""
    out = {}
    M_m = GAMA_Q * max(H_GC * s * h_gc, P_CR * 0.90)               # base do montante: 730 N/m × s no topo, ou 900 N no corrimão
    for tb in sorted((t_ for t_ in TUBOS_Q if b_max is None or t_["b"] <= b_max), key=lambda t_: t_["kg"]):
        MRd = tb["W"] * 1e-6 * FY36 / GA1
        if M_m <= MRd:
            out["montante"] = dict(perfil=tb["nome"], b=tb["b"], t=tb["t"], Md=round(M_m, 3), MRd=round(MRd, 3), uso=round(M_m / MRd, 3), kg_m=round(tb["kg"], 2))
            break
    M_t = GAMA_Q * H_GC * s ** 2 / 8
    for tb in TUBOS_Q:
        MRd = tb["W"] * 1e-6 * FY36 / GA1
        if M_t <= MRd:
            out["travessa"] = dict(perfil=tb["nome"], b=tb["b"], t=tb["t"], Md=round(M_t, 3), MRd=round(MRd, 3), uso=round(M_t / MRd, 3), kg_m=round(tb["kg"], 2))
            break
    M_c = GAMA_Q * P_CR * s / 4
    for tb in TUBOS_R:
        MRd = tb["W"] * 1e-6 * FY36 / GA1
        if M_c <= MRd and 38 <= tb["D"] <= 65:
            out["corrimao"] = dict(perfil=tb["nome"], D=tb["D"], t=tb["t"], Md=round(M_c, 3), MRd=round(MRd, 3), uso=round(M_c / MRd, 3), kg_m=round(tb["kg"], 2))
            break
    hb = h_gc - 0.10 - 0.05 - 0.05                                  # barra entre as 2 cantoneiras (0,10 do piso até 5 cm abaixo do topo)
    for d in (10.0, 12.7, 16.0):
        Wb = math.pi * (d / 1000) ** 3 / 32
        Mb = GAMA_Q * Q_GC * 0.13 * hb ** 2 / 8
        if Mb <= Wb * FY36 / GA1:
            out["barra"] = dict(perfil=f"barra redonda Ø{d:g}".replace(".", ","), d=d, s_mm=130, vao_livre_mm=round(130 - d), Md=round(Mb, 4), MRd=round(Wb * FY36 / GA1, 4),
                                uso=round(Mb / (Wb * FY36 / GA1), 3), kg_m=round(math.pi * d * d / 4 * 7.85e-3, 3))
            break
    w_c = GAMA_Q * Q_GC * hb / 2                                     # cantoneira das barras: metade do fechamento, vão s
    for nm in ("L 38 × 38 × 4,8", "L 51 × 51 × 4,8"):
        b, t, kg = (38, 4.8, 2.68) if nm.startswith("L 38") else L_[nm]
        Wc = (t * b ** 2 / 6) * 1e-9 * 0.70                          # aba vertical à flexão (aproximação a favor)
        Mc = w_c * s ** 2 / 8
        if Mc <= Wc * FY36 / GA1:
            out["cantoneira_barras"] = dict(perfil=nm, Md=round(Mc, 3), MRd=round(Wc * FY36 / GA1, 3), uso=round(Mc / (Wc * FY36 / GA1), 3), kg_m=kg)
            break
    # fixação do montante: 2 parafusos a 70 mm (binário) — corte simples no parafuso e contato na alma/chapa (t 4,3 mínimo)
    F = M_m / 0.070
    Vrd = parafuso_corte(12)
    out["fixacao_montante"] = dict(desc="2 M12 8.8 a 70 mm (binário)", F_d=round(F, 1), VRd=round(Vrd, 1), uso=round(F / Vrd, 3),
                                   contato_tubo_Rd=round(contato(12, 2 * out["montante"]["t"]), 1), uso_contato_tubo=round(F / contato(12, 2 * out["montante"]["t"]), 3),
                                   contato_Rd_t43=round(contato(12, 4.3), 1), uso_contato=round(F / contato(12, 4.3), 3))
    return out


# ================================================================== 4. peças (3D) e ligações — construção
P: list[dict] = []          # peças: {tipo, marca, grupo, geom...}
C: list[dict] = []          # ligações (com verificação)
GI, GE = "Escada metálica", "Escada metálica externa"


def caixa(marca, x0, x1, y0, y1, z0, z1, grupo, tipo="placa", obs=""):
    P.append(dict(g="caixa", tipo=tipo, marca=marca, grupo=grupo, x0=min(x0, x1), x1=max(x0, x1), y0=min(y0, y1), y1=max(y0, y1), z0=min(z0, z1), z1=max(z0, z1), obs=obs))


def linear(marca, perfil, p0, p1, grupo, cima=(0.0, 0.0, 1.0), tipo="viga", obs=""):
    P.append(dict(g="linear", tipo=tipo, marca=marca, grupo=grupo, perfil=perfil, p0=tuple(round(v, 5) for v in p0), p1=tuple(round(v, 5) for v in p1), cima=cima, obs=obs))


def poligono(marca, eixo, contorno, a0, a1, grupo, tipo="viga", obs=""):
    """contorno (c, z) no plano vertical do lance (c = y se eixo 'y', x se 'x'), extrudado na outra direção de a0 a a1."""
    P.append(dict(g="poligono", tipo=tipo, marca=marca, grupo=grupo, eixo=eixo, contorno=[(round(c, 5), round(z, 5)) for c, z in contorno], a0=a0, a1=a1, obs=obs))


def lig(cod, tipo, pecas, elemento, furos, Vd, VRd, checks, desc, grupo):
    ok = all(c[1] for c in checks) and Vd <= VRd
    C.append(dict(cod=cod, tipo=tipo, pecas=pecas, elemento=elemento, furos=furos, Vd=round(Vd, 2), VRd=round(VRd, 2), uso=round(Vd / VRd, 3) if VRd else 0.0,
                  checks=[dict(item=c[0], ok=bool(c[1]), valor=c[2]) for c in checks], ok=ok, desc=desc, grupo=grupo))
    return ok


def chk_borda(nome, dist_mm, d):
    return (f"{nome}: borda {dist_mm:.0f} ≥ {BORDA[d]}", dist_mm >= BORDA[d] - 0.05, round(dist_mm, 1))


def chk_esp(nome, s_mm, d):
    return (f"{nome}: entre furos {s_mm:.0f} ≥ {3 * d}", s_mm >= 3 * d - 0.05, round(s_mm, 1))


def chk_chave(nome, dist_mm, d):
    return (f"{nome}: furo × face da mesa {dist_mm:.0f} ≥ {TCHAVE[d]}", dist_mm >= TCHAVE[d] - 0.05, round(dist_mm, 1))


def chk_faixa(nome, ini, fim, minimo):
    return (f"{nome}: faixa comum {1000 * (fim - ini):.0f} ≥ {1000 * minimo:.0f} mm", fim - ini >= minimo - 1e-4, round(1000 * (fim - ini), 1))


# ------------------------------------------------------------------ longarinas, degraus e cantoneiras dos degraus
def longarinas_e_degraus(ln: Lance, grupo, cod, s_pe, s_topo, z_pe, pe_vertical=None, Rd_long=1.0):
    """longarinas (mesas para fora, alma do lado dos degraus) com o pé cortado na horizontal em z_pe e o topo cortado na vertical
    em s_topo; degraus DG (chapa xadrez 4,75 dobrada) apoiados em cantoneiras L 51 parafusadas na alma (2 M10 na alma, 1 M8 no degrau)."""
    bf = ln.u["bf"] / 1000
    tg = ln.e / ln.p
    s_bz = (z_pe - (ln.z0 + ln.e + ln.a - ln.Dv)) / tg              # s em que o fundo encontra o piso
    s_tz = (z_pe - (ln.z0 + ln.e + ln.a)) / tg                      # s em que o topo encontra o piso
    s0 = max(s_tz, s_pe) if pe_vertical is None else pe_vertical
    pts = []
    if pe_vertical is None:
        pts = [(s0, z_pe), (s_bz, z_pe)]
    else:
        pts = [(s0, max(z_pe, ln.z_bot(s0))), (max(s0, s_bz), z_pe) if s_bz > s0 else (s0, ln.z_bot(s0))]
        pts = [(s0, z_pe), (s_bz, z_pe)] if s_bz > s0 else [(s0, ln.z_bot(s0))]
        pts = [(s0, ln.z_top(s0))] + pts
    contorno = ([] if pe_vertical is not None else [(s0, ln.z_top(s0))]) + pts + [(s_topo, ln.z_bot(s_topo)), (s_topo, ln.z_top(s_topo))]
    if pe_vertical is not None:
        contorno = pts + [(s_topo, ln.z_bot(s_topo)), (s_topo, ln.z_top(s_topo))]
    ok_poly = True
    for lado, (a0, a1) in (("ext", (ln.l0, ln.l0 + bf)), ("int", (ln.l1 - bf, ln.l1))):
        poligono(f"{cod} longarina {ln.perfil} ({ln.nome}, {lado})", ln.eixo, [(ln.c(s), z) for s, z in contorno], a0, a1, grupo,
                 obs=f"mesas para fora, alma do lado dos degraus; topo {abs(ln.a) * 1000:.0f} mm abaixo da linha dos bocéis; pé cortado na horizontal (+{z_pe:.3f}), topo na vertical".replace(".", ","))
    # degraus e cantoneiras
    lw, tc, _ = L_["L 51 × 51 × 4,8"]
    Lc, d0 = 0.080, 0.100
    amin, amax = ajuste_longarina(ln)
    checks = [("cantoneira do degrau cabe na alma (a dentro da faixa)", amin <= ln.a <= amax, f"a {ln.a * 1000:.0f} mm em [{amin * 1000:.1f}; {amax * 1000:.1f}]")]
    w_in0, w_in1 = ln.l0 + bf, ln.l1 - bf
    n_deg = ln.n - 1
    for k in range(1, ln.n):
        zk = ln.z_degrau(k)
        sa, sb = (k - 1) * ln.p - 0.025, k * ln.p - 0.005               # bocel de 25 mm
        p0, p1 = ln.pt(sa, w_in0 + 0.005, zk - T_DG), ln.pt(sb, w_in1 - 0.005, zk)
        caixa(f"{cod}-DG degrau chapa xadrez 4,75 ({ln.nome}, degrau {k})", p0[0], p1[0], p0[1], p1[1], p0[2], p1[2], grupo)
        for lat, sgl in ((w_in0, 1), (w_in1, -1)):
            sa_c = (k - 1) * ln.p + d0
            q0, q1 = ln.pt(sa_c, lat, zk - T_DG - lw / 1000), ln.pt(sa_c + Lc, lat + sgl * tc / 1000, zk - T_DG)
            caixa(f"{cod}-CT cantoneira L 51 × 51 × 4,8 L=80 (2 M10 na alma, 1 M8 no degrau)", q0[0], q1[0], q0[1], q1[1], q0[2], q1[2], grupo)
            q0, q1 = ln.pt(sa_c, lat, zk - T_DG - tc / 1000), ln.pt(sa_c + Lc, lat + sgl * lw / 1000, zk - T_DG)
            caixa(f"{cod}-CT cantoneira L 51 × 51 × 4,8 L=80 — aba horizontal", q0[0], q1[0], q0[1], q1[1], q0[2], q1[2], grupo)
    # verificação de um degrau típico (todos iguais em relação à longarina)
    k = 2
    zk = ln.z_degrau(k)
    sa_c = (k - 1) * ln.p + d0
    zf = zk - T_DG - 0.028                                           # furos a 28 da quina (23 da ponta da aba)
    m_top = [(ln.z_top(sa_c + x) - zf) * math.cos(ln.th) * 1000 - ln.u["tf"] for x in (0.020, 0.060)]
    m_bot = [(zf - ln.z_bot(sa_c + x)) * math.cos(ln.th) * 1000 - ln.u["tf"] for x in (0.020, 0.060)]
    checks += [chk_borda("furo na aba vertical da L 51 (até a ponta)", 51 - 28, 10), chk_borda("furo × ponta da cantoneira", 20, 10), chk_esp("2 M10", 40, 10),
               chk_chave("furo × mesa de cima da longarina", min(m_top), 10), chk_chave("furo × mesa de baixo da longarina", min(m_bot), 10)]
    Vd = (1.4 * G_DEG + 1.5 * Q) * (w_in1 - w_in0) * ln.p / 2
    lig(f"{cod}-1", "degrau × longarina", [f"DG ({ln.nome})", f"longarina {ln.perfil}"], "cantoneira L 51 × 51 × 4,8 L = 80 por ponta", "2 M10 8.8 na alma + 1 M8 escareado no degrau",
        Vd, 2 * parafuso_corte(10), checks, f"{n_deg} degraus × 2 pontas; cantoneira a {d0 * 1000:.0f} mm do bocel", grupo)
    return dict(s0=s0, contorno=contorno, n_deg=n_deg, s_bz=s_bz)


def subir_longarina(ln: Lance, z_topo_viga, s_end, folga=0.003):
    """sobe a longarina o máximo que a cantoneira do degrau permite e que o topo, no fim, fique ≥ folga abaixo do piso — maximiza a
    faixa comum com a alma da viga do topo (ligação EI/EE-..-T)."""
    a_cant = ajuste_longarina(ln)[1] - 0.001
    a_top = ln.a + (z_topo_viga - folga - ln.z_top(s_end))
    ln.a = round(min(a_cant, a_top), 4)
    return ln.a


def lig_topo_em_viga(cod, ln: Lance, viga, s_end, grupo, Vd, lado_l="ambos"):
    """topo do lance (corte vertical a 10 mm da ponta da mesa da viga W perpendicular): cantoneira L 102 × 102 × 6,3 com uma aba na
    alma da viga e outra na alma da longarina, do lado dos degraus; 2 M12 em cada aba."""
    zt, d, bf, tw, tf = viga["z_topo"], viga["d"] / 1000, viga["bf"] / 1000, viga["tw"] / 1000, viga["tf"] / 1000
    wc0, wc1 = zt - d + tf + 0.008, zt - tf - 0.008                  # faixa livre da alma da viga (fora dos raios)
    m = (ln.u["tf"] + 15) / 1000 / math.cos(ln.th)
    s_f = s_end - 0.022                                              # linha de furos na longarina (22 da ponta)
    lc0, lc1 = ln.z_bot(s_f) + m, ln.z_top(s_f) - m                   # faixa livre da longarina na linha de furos
    z0, z1 = max(wc0, lc0), min(wc1, lc1)
    Lv = 0.080
    sobre = 0.102 - (bf / 2 - tw / 2) - 0.010                          # trecho da aba sobre a longarina
    checks = [chk_faixa("alma da viga × alma da longarina", z0, z1, Lv), chk_borda("furo × ponta da longarina", 22, 12), chk_borda("furo × ponta da aba (102)", sobre * 1000 - 22, 12),
              chk_esp("2 M12 na vertical", (Lv - 2 * 0.022) * 1000 + 0, 12) if Lv - 0.044 >= 0.036 else ("2 M12: 36 mm", True, 36),
              ("topo da longarina abaixo do piso", ln.z_top(s_end) <= zt - 0.002, round((zt - ln.z_top(s_end)) * 1000, 1))]
    zc = (z0 + z1) / 2
    bfl = ln.u["bf"] / 1000
    for lat, sgl in ((ln.l0 + bfl, 1), (ln.l1 - bfl, -1)):
        yw = viga["eixo"] + (tw / 2) * (1 if ln.sg < 0 else -1) * (1 if viga["lado"] == "+" else 1)
        c_web = viga["eixo"] + (tw / 2 if ln.c(s_end) > viga["eixo"] else -tw / 2)
        c_tip = c_web + (0.102 if ln.c(s_end) > viga["eixo"] else -0.102)
        # aba na alma da viga (plano c = c_web), 102 na lateral; aba na alma da longarina (plano lat), de c_web a c_tip
        p0, p1 = ln.pt(ln.s_de(c_web), lat, zc - Lv / 2), ln.pt(ln.s_de(c_web + (0.0063 if c_tip > c_web else -0.0063)), lat + sgl * 0.102, zc + Lv / 2)
        caixa(f"{cod} cantoneira L 102 × 102 × 6,3 L=80 (2 M12 na viga + 2 M12 na longarina)", p0[0], p1[0], p0[1], p1[1], p0[2], p1[2], grupo)
        p0, p1 = ln.pt(ln.s_de(c_web), lat, zc - Lv / 2), ln.pt(ln.s_de(c_tip), lat + sgl * 0.0063, zc + Lv / 2)
        caixa(f"{cod} cantoneira L 102 × 102 × 6,3 — aba na longarina", p0[0], p1[0], p0[1], p1[1], p0[2], p1[2], grupo)
    VRd = min(2 * parafuso_corte(12), 2 * contato(12, ln.u["tw"]), 2 * contato(12, viga["tw"]))
    lig(cod, "topo do lance × viga", [f"longarina {ln.perfil} ({ln.nome})", viga["nome"]], "cantoneira L 102 × 102 × 6,3 L = 80 (lado dos degraus)",
        "2 M12 8.8 na alma da viga + 2 M12 8.8 na alma da longarina", Vd, VRd, checks, f"faixa comum de {1000 * (z1 - z0):.0f} mm; longarina a 10 mm da ponta da mesa", grupo)
    return z0, z1


# ------------------------------------------------------------------ montagem da escada interna
def escada_interna():
    out = {}
    lg, lg_all = dim_longarina(L1)
    assert lg["perfil"] == PERF_LONG_INT, lg
    vao_v = XE_ - X6 - 0.02
    R_l = lg["R_d"]
    v_pf = dim_viga(vao_v, (Y_PAT[1] - Y_PAT[0]) / 2, [(2 * R_l, 0.70), (2 * R_l, vao_v - 0.70)])
    v_pt = dim_viga(XE_ - X6 + 0.40 - 0.10, (Y_PAT[1] - Y_PAT[0]) / 2, [])
    v_cf = dim_viga(XE_ - 0.09 - (X6 + BL + 0.05), (Y_CHE[1] - Y_CHE[0]) / 2, [(2 * R_l, 0.70)], balanco=(X6 + BL + 0.05) - (ABERTURA["x0"]))
    v_ct = dim_viga(XE_ - X6 + 0.40 - 0.10, (Y_CHE[1] - Y_CHE[0]) / 2, [])
    bar = dim_barrote(Y_PAT[1] - Y_PAT[0] - 0.16)
    out.update(longarina=lg, alternativas_longarina=lg_all, viga_patamar_frente=v_pf, viga_patamar_fundo=v_pt, viga_chegada_frente=v_cf, viga_chegada_fundo=v_ct, barrote=bar)
    # ---- vigas (posições): patamar frente y 5,47; fundo 4,066 (assento nas faces +y do P6 e do P7); chegada frente 8,43 (balanço até
    # x 36,00, borda da laje); chegada fundo 9,37 (assento nas faces −y do P6 da linha 2 e do P2-L2)
    def W(nome, perf, eixo_c, x0, x1, zt):
        p = ML.perfil(perf["perfil"].replace(" × ", " x "))
        linear(nome, ("I", p.d / 1000, p.bf / 1000, p.tw / 1000, p.tf / 1000, perf["perfil"]), (x0, eixo_c, zt - p.d / 2000), (x1, eixo_c, zt - p.d / 2000), GI)
        return dict(nome=nome.split(" (")[0], eixo=eixo_c, x0=x0, x1=x1, z_topo=zt, d=p.d, bf=p.bf, tw=p.tw, tf=p.tf, lado="+")
    zpt, zch = Z_PAT - T_CH, Z_PISO_PRONTO - T_CH
    YF_P, YT_P = Y_PAT[1] - 0.08, Y_PAT[0] + 0.130                     # VP-2 130 mm à frente dos pilares: montantes do GI-5 livres dos CP-MEZ
    YF_C, YT_C = Y_CHE[0] + 0.08, Y_CHE[1] - 0.08
    vpf = W(f"VP-1 viga {v_pf['perfil']} (frente do patamar +1,975)", v_pf, YF_P, X6 + 0.01, XE_ - 0.01, zpt)
    vpt = W(f"VP-2 viga {v_pt['perfil']} (fundo do patamar, assento nas faces do P6 e do P7)", v_pt, YT_P, X6 - 0.20, XE_ + 0.20, zpt)
    vcf = W(f"VP-3 viga {v_cf['perfil']} (frente da chegada +3,95, balanço até a laje)", v_cf, YF_C, ABERTURA["x0"] + 0.005, XE_ - 0.01, zch)
    vct = W(f"VP-4 viga {v_ct['perfil']} (fundo da chegada, assento nas faces do P6 e do P2)", v_ct, YT_C, X6 - 0.20, XE_ + 0.20, zch)
    # pisos (chapa xadrez 6,3) e barrotes L
    for (ya, yb), zz, nm, x0 in (((YT_P - vpt["bf"] / 2000, Y_PAT[1]), Z_PAT, "patamar +1,975", X6 + 0.01), ((YF_C - vcf["bf"] / 2000, Y_CHE[1]), Z_PISO_PRONTO, "chegada +3,95", ABERTURA["x0"] + 0.005)):
        caixa(f"CH-P chapa xadrez 6,3 ({nm})", x0, XE_ - 0.01, ya, yb, zz - T_CH, zz, GI)
    bl_, bt_, bk_ = L_[bar["perfil"]]
    for (ya, yb), zz, x0 in (((YT_P, YF_P), Z_PAT, X6 + 0.01), ((YF_C, YT_C), Z_PISO_PRONTO, ABERTURA["x0"] + 0.005)):
        n_b = max(1, math.ceil((XE_ - 0.01 - x0) / 0.60) - 1)
        for j in range(1, n_b + 1):
            xb = x0 + j * (XE_ - 0.01 - x0) / (n_b + 1)
            y_a, y_b = ya + 0.05 + 0.005, yb - 0.05 - 0.005                    # recorte da aba horizontal junto às mesas
            caixa(f"BR barrote {bar['perfil']} (aba horizontal sob a chapa)", xb - bl_ / 1000, xb, y_a, y_b, zz - T_CH - bt_ / 1000, zz - T_CH, GI)
            caixa(f"BR barrote {bar['perfil']} — aba vertical (1 M12 na alma da viga em cada ponta)", xb - bt_ / 1000, xb, ya + 0.0022 + 0.001, yb - 0.0022 - 0.001,
                  zz - T_CH - bl_ / 1000, zz - T_CH - bt_ / 1000, GI)
    lig("EI-BR", "barrote × viga", [f"barrote {bar['perfil']}", "VP (alma)"], "aba vertical do barrote com a aba horizontal recortada 55 mm nas pontas",
        "1 M12 8.8 em cada ponta", (1.4 * T_CH * 78.5 + 1.5 * Q) * 0.6 * bar["vao"] / 2, min(parafuso_corte(12), contato(12, 4.3)),
        [chk_borda("furo × topo/base da aba vertical", (bl_ - bt_) / 2, 12), chk_chave("furo × mesas da viga (faixa 138)", (138 - bl_) / 2 + 10, 12)],
        "barrotes a ≤ 60 cm", GI)
    # ---- longarinas, degraus e ligações
    s_end1 = L1.s_de(YF_P + vpf["bf"] / 2000 + 0.010)
    r1 = longarinas_e_degraus(L1, GI, "EI-L1", s_pe=-0.5, s_topo=s_end1, z_pe=0.0)
    lig_topo_em_viga("EI-L1-T", L1, vpf, s_end1, GI, lg["R_d"])
    s_end2 = L2.s_de(YF_C - vcf["bf"] / 2000 - 0.010)
    r2 = longarinas_e_degraus(L2, GI, "EI-L2", s_pe=-0.10, s_topo=s_end2, z_pe=Z_PAT, pe_vertical=-0.10)
    lig_topo_em_viga("EI-L2-T", L2, vcf, s_end2, GI, lg["R_d"])
    # pé do lance 2 no patamar: cantoneira L 76 × 51 × 6,3 L = 130 (aba de 76 no piso, 51 na longarina)
    bfl = L2.u["bf"] / 1000
    ya_c, yb_c = Y_LAN[0] - 0.13, Y_LAN[0]
    for lat, sgl in ((L2.l0 + bfl, 1), (L2.l1 - bfl, -1)):
        caixa("EI-L2-P cantoneira L 76 × 51 × 6,3 L=130 — aba no piso (1 M12 na mesa da VP-1 + 1 M12 na chapa)", lat, lat + sgl * 0.076, ya_c, yb_c, Z_PAT, Z_PAT + 0.0063, GI)
        caixa("EI-L2-P cantoneira L 76 × 51 × 6,3 — aba na longarina (2 M12)", lat, lat + sgl * 0.0063, ya_c, yb_c, Z_PAT, Z_PAT + 0.051, GI)
    zf_ = Z_PAT + 0.028
    yf1, yf2 = ya_c + 0.025, yb_c - 0.025
    m_top = [(L2.z_top(L2.s_de(yy)) - zf_) * math.cos(L2.th) * 1000 - L2.u["tf"] for yy in (yf1, yf2)]
    fl0, fl1 = YF_P - vpf["bf"] / 2000, YF_P + vpf["bf"] / 2000
    y_h1 = fl1 - 0.022
    chk = [chk_borda("furo da aba de 51 × ponta", 51 - 28, 12), chk_esp("2 M12 na longarina", (yf2 - yf1) * 1000, 12), chk_chave("furo × mesa de cima da longarina", min(m_top), 12),
           ("aba de 51 abaixo do topo da longarina", Z_PAT + 0.051 <= L2.z_top(L2.s_de(ya_c)) - 0.003, round((L2.z_top(L2.s_de(ya_c)) - Z_PAT - 0.051) * 1000, 1)),
           chk_borda("furo na mesa da VP-1 × ponta da mesa", (fl1 - y_h1) * 1000, 12), chk_chave("furo na mesa × alma da VP-1", (y_h1 - YF_P - vpf["tw"] / 2000) * 1000, 12),
           chk_borda("furo na mesa × ponta da cantoneira", (y_h1 - ya_c) * 1000, 12)]
    lig("EI-L2-P", "pé do lance × patamar", ["longarina U 152 (lance 2)", "VP-1 + chapa do patamar"], "cantoneira L 76 × 51 × 6,3 L = 130",
        "2 M12 na alma da longarina; 1 M12 na mesa da VP-1 e 1 M12 na chapa do piso", lg["R_d"], min(2 * parafuso_corte(12), 2 * contato(12, L2.u["tw"])), chk,
        "pé cortado na horizontal sobre o piso do patamar, 10 cm atrás do 1º espelho (sob o montante de arranque do guarda-corpo central)", GI)
    # BM-1: soleira U 152 em pé ENTRE as longarinas do lance 1, sob o bocel do 1º degrau
    yb0 = Y_LAN[1] + 0.002
    bm_l = L1.l1 - L1.l0 - 2 * bfl - 0.010
    x0b, x1b = L1.l0 + bfl + 0.005, L1.l1 - bfl - 0.005
    caixa("BM-1 base metálica U 152 × 12,2 em pé (entre as longarinas do lance 1)", x0b, x1b, yb0, yb0 + 0.0488, 0.010, 0.010 + 0.1524, GI, tipo="viga")
    caixa("graute de nivelamento 10 mm da BM-1", x0b, x1b, yb0, yb0 + 0.0488, 0.0, 0.010, GI)
    for xc_ in (x0b + 0.25, (x0b + x1b) / 2, x1b - 0.25):
        caixa("CB-1 cantoneira L 76 × 76 × 6,3 × 100 + chumbador químico M12 (BM-1 no piso)", xc_ - 0.05, xc_ + 0.05, yb0 + 0.0488 + 0.001, yb0 + 0.0488 + 0.077, 0.010, 0.0163, GI)
    for lat, sgl in ((L1.l0 + bfl, 1), (L1.l1 - bfl, -1)):
        caixa("CB-2 cantoneira L 76 × 76 × 6,3 × 100 (pé da longarina na alma da BM-1)", lat + sgl * 0.0, lat + sgl * 0.0063, yb0 - 0.076, yb0, 0.030, 0.130, GI)
    z_t0 = L1.z_top(0.0)
    lig("EI-L1-P", "pé do lance × base metálica", ["longarina U 152 (lance 1)", "BM-1 U 152 em pé"], "cantoneira L 76 × 76 × 6,3 L = 100 (lado dos degraus)",
        "2 M12 na alma da BM-1 + 2 M12 na alma da longarina", lg["R_d"] * 0.1 + 1.0, 2 * parafuso_corte(12),
        [chk_faixa("alma da BM-1 × longarina no pé", 0.030, min(0.130, z_t0 - 0.016), 0.080), ("BM-1 entre as longarinas (sem cruzar)", bm_l > 1.0, round(bm_l * 1000)),
         chk_borda("furo × ponta da aba", 76 - 40, 12)], "a longarina apoia no piso (graute) pela base; a cantoneira trava o pé", GI)
    # pilaretes (tubo quadrado) e assentos das vigas nos pilares
    h_pf = Z_PAT - T_CH - vpf["d"] / 1000
    h_cf = Z_PISO_PRONTO - T_CH - vcf["d"] / 1000
    pil_pf = dim_pilarete(v_pf["R_a"], h_pf)
    pil_cf = dim_pilarete(max(v_cf["R_a"], v_cf["R_b"]), h_cf)
    out.update(pilarete_patamar=pil_pf, pilarete_chegada=pil_cf)
    X_TUBO = round(X6 + BL + GAP / 2, 3)
    pil_pos = [(X6 + 0.09, YF_P, pil_pf, vpf, "patamar"), (XE_ - 0.09, YF_P, pil_pf, vpf, "patamar"), (X_TUBO, YF_C, pil_cf, vcf, "chegada"), (XE_ - 0.09, YF_C, pil_cf, vcf, "chegada")]
    for xp, yp, pf, vv, nm in pil_pos:
        b = pf["b"] / 1000
        ztop = vv["z_topo"] - vv["d"] / 1000
        linear(f"PL pilarete {pf['perfil']} ({nm})", ("R", b, b, pf["perfil"]), (xp, yp, 0.020), (xp, yp, ztop), GI, cima=(1.0, 0.0, 0.0), tipo="pilar")
        caixa("graute de assentamento 20 mm do pilarete", xp - b / 2 - 0.005, xp + b / 2 + 0.005, yp - b / 2 - 0.08, yp + b / 2 + 0.08, 0.0, 0.020, GI)
        for sg in (-1, 1):
            # base: 2 cantoneiras L 76 × 76 × 6,3 × 100 nas faces ⊥ y (1 M12 passante no tubo, 1 chumbador químico M12 no piso cada)
            caixa("CB-3 cantoneira L 76 × 76 × 6,3 × 100 — base do pilarete (chumbador químico M12)", xp - b / 2 - 0.0, xp + b / 2 + 0.0, yp + sg * b / 2, yp + sg * (b / 2 + 0.076), 0.020, 0.0263, GI)
            caixa("CB-3 cantoneira — aba no tubo", xp - b / 2, xp + b / 2, yp + sg * b / 2, yp + sg * (b / 2 + 0.0063), 0.020, 0.096, GI)
            # topo: 2 cantoneiras L 76 × 76 × 6,3 × 100 nas faces ⊥ x (1 M12 passante no tubo, 1 M12 na mesa inferior da viga cada)
            caixa("CB-4 cantoneira L 76 × 76 × 6,3 × 100 — topo do pilarete (aba sob a mesa da viga)", xp + sg * b / 2, xp + sg * (b / 2 + 0.076), yp - 0.05, yp + 0.05, ztop - 0.0063, ztop, GI)
            caixa("CB-4 cantoneira — aba no tubo", xp + sg * b / 2, xp + sg * (b / 2 + 0.0063), yp - 0.05, yp + 0.05, ztop - 0.076, ztop, GI)
    # topo do pilarete: furo na mesa a (b/2 + 40) da linha do tubo, ±25 da alma
    bmin = min(pil_pf["b"], pil_cf["b"])
    lig("EI-PL-T", "topo do pilarete × viga", ["pilarete " + pil_pf["perfil"], "VP (mesa inferior)"], "2 cantoneiras L 76 × 76 × 6,3 L = 100",
        "1 M12 passante no tubo + 2 M12 na mesa inferior da viga (1 por cantoneira, a 25 mm da alma)", max(v_pf["R_a"], v_cf["R_a"]) * 0.1 + 0.5, 2 * parafuso_corte(12),
        [chk_borda("furo na mesa × ponta da mesa (bf 100)", 50 - 25, 12), chk_chave("furo na mesa × alma", 25 - 4.3 / 2, 12), chk_borda("furo × ponta da aba (76)", 76 - 40, 12),
         chk_borda("furo no tubo × topo da aba vertical", 38, 12)], "viga apoiada no topo do tubo (contato); as cantoneiras só posicionam e travam", GI)
    lig("EI-PL-B", "base do pilarete × piso", ["pilarete", "piso do térreo"], "2 cantoneiras L 76 × 76 × 6,3 L = 100", "1 M12 passante no tubo + 2 chumbadores químicos M12 hef 100",
        0.5, 12.0, [chk_borda("chumbador × ponta da aba", 76 - 40, 12)], "pilarete apoiado sobre graute 20 mm", GI)
    # assentos SA-1 das vigas de fundo nas faces dos pilares (2 BR-M16 embutidas + 2 M12 na mesa inferior)
    for (xp, yp, bx, by, face_sg), vv, nm in (((P6_ESC[0], P6_ESC[1], 0.25, 0.40, 1), vpt, "P6"), ((P7_ESC[0], P7_ESC[1], 0.60, 0.40, 1), vpt, "P7"),
                                              ((P6_L2[0], P6_L2[1], 0.25, 0.40, -1), vct, "P6 da linha 2"), ((X_EIXO["E"], Y_LIN[1], 0.60, 0.40, -1), vct, "P2-L2")):
        yface = yp + face_sg * by / 2
        zb = vv["z_topo"] - vv["d"] / 1000
        xa, xb_ = max(xp - bx / 2, vv["x0"]) + 0.02, min(xp + bx / 2, vv["x1"]) - 0.02
        xm = (xa + xb_) / 2
        lh_ = 0.152 if nm in ("P6", "P7") else 0.102                     # SA-1: L 152 × 102 (VP-2, 130 mm à frente) / SA-2: L 102 × 102 (VP-4)
        caixa(f"SA-{1 if lh_ > 0.12 else 2} assento L {lh_ * 1000:.0f} × 102 × 9,5 L=160 — aba na face do {nm} (2 BR-M16 embutidas)", xm - 0.08, xm + 0.08, yface, yface + face_sg * 0.0095, zb - 0.102, zb, GI)
        caixa(f"SA-{1 if lh_ > 0.12 else 2} assento — aba sob a mesa da viga (2 M12)", xm - 0.08, xm + 0.08, yface, yface + face_sg * lh_, zb - 0.0095, zb, GI)
    fl_in = YT_P - vpt["bf"] / 2000 - (P6_ESC[1] + 0.20)
    _yb = YT_P - vpt["bf"] / 2000                                     # borda da mesa junto ao pilar
    _janela = (_yb + 0.022, YT_P - vpt["tw"] / 2000 - TCHAVE[12] / 1000)
    y_furo = (_janela[0] + _janela[1]) / 2                             # furo no meio da janela livre (borda × alma)
    lig("EI-SA", "viga de fundo × pilar (assento)", ["VP-2 / VP-4", "P6, P7, P6 da linha 2, P2-L2"], "cantoneira de assento L 152 × 102 × 9,5 L = 160 (VP-2) / L 102 × 102 × 9,5 (VP-4)",
        "2 BR-M16 8.8 embutidas 150 mm + grampo (fábrica do pilar) + 2 M12 na mesa inferior", max(v_pt["R_a"], v_ct["R_a"]),
        min(2 * parafuso_corte(16), 2 * parafuso_corte(12)),
        [("mesa da viga sobre o assento", 0.152 - fl_in >= 0.040, round((0.152 - fl_in) * 1000, 1)),
         chk_borda("furo na mesa × ponta da mesa", (y_furo - (YT_P - vpt["bf"] / 2000)) * 1000, 12),
         chk_chave("furo na mesa × alma", (YT_P - vpt["tw"] / 2000 - y_furo) * 1000, 12), chk_borda("furo × ponta da aba (152)", (P6_ESC[1] + 0.20 + 0.152 - y_furo) * 1000, 12),
         ("furo × face do pilar (cabeça + chave ≥ 30)", (y_furo - P6_ESC[1] - 0.20) * 1000 >= 30, round((y_furo - P6_ESC[1] - 0.20) * 1000, 1)),
         ("viga passa à frente do pilar (sobreposição em x)", True, "≥ 200 mm")],
        "a viga corre ao longo da face do pilar (folga 26 mm); assento embaixo da mesa e furos M12 fora da alma", GI)
    # chegada: chapa de transição até a borda da laje (x 36,00) — o piso já vai até a laje (VP-3 em balanço e VP-4 até x 36,10)
    out["vigas"] = dict(VP1=vpf, VP2=vpt, VP3=vcf, VP4=vct)
    out["geom"] = dict(L1=r1, L2=r2, X_TUBO=X_TUBO, YF_P=YF_P, YT_P=YT_P, YF_C=YF_C, YT_C=YT_C)
    return out


# ------------------------------------------------------------------ escada externa
def escada_externa():
    out = {}
    lc, lc_all = dim_longarina(LC)
    lb, lb_all = dim_longarina(LB)
    assert lc["perfil"] == LC.perfil and lb["perfil"] == LB.perfil, (lc["perfil"], lb["perfil"])
    xi, xe = EX["x_int"], EX["x_ext"]
    B = xi - xe
    yc0, yc1 = EX["y_chegada"]
    yp0, yp1 = EX["y_patamar"]
    v_t = dim_viga(B, 0.0, [(lc["R_d"], 0.06), (lc["R_d"], B - 0.06)])                  # VE-2 transversal da chegada (recebe o lance de cima)
    v_c = dim_viga(yc1 - yc0 - 0.11, B / 2, [])                                         # VE-1 bordas da chegada
    v_p = dim_viga(yp1 - yp0 - 0.12, B / 2, [(lc["R_d"], 0.10), (lb["R_d"], (yp1 - yp0) / 2)])   # VE-3 bordas do patamar
    out.update(longarina_cima=lc, longarina_baixo=lb, alternativas=dict(cima=lc_all, baixo=lb_all), viga_transversal=v_t, viga_chegada=v_c, viga_patamar=v_p)
    zch, zpt = Z_CHE_E - T_CH, Z_PAT_E - T_CH

    def W(nome, perf, p0, p1):
        p = ML.perfil(perf["perfil"].replace(" × ", " x "))
        linear(nome, ("I", p.d / 1000, p.bf / 1000, p.tw / 1000, p.tf / 1000, perf["perfil"]), (p0[0], p0[1], p0[2] - p.d / 2000), (p1[0], p1[1], p1[2] - p.d / 2000), GE)
        return dict(nome=nome.split(" (")[0], d=p.d, bf=p.bf, tw=p.tw, tf=p.tf, z_topo=p0[2])
    YT = yc1 - 0.06                                                                     # eixo da VE-2 (mesa 2,33–2,43; lance chega a 10 mm)
    ve2 = W(f"VE-2 viga {v_t['perfil']} (transversal da chegada, recebe o lance de cima)", v_t, (xe, YT, zch), (xi, YT, zch)); ve2.update(eixo=YT, lado="+")
    X_VC = (xi - 0.10, xe + 0.05)                                          # borda interna 10 cm para dentro: cantoneiras do topo do pilarete livres da placa
    for xv in X_VC:
        W(f"VE-1 viga {v_c['perfil']} (borda da chegada +3,95)", v_c, (xv, yc0 + 0.01, zch), (xv, YT - v_t["bf"] / 2000 - 0.010, zch))
    X_VP = (xi - 0.075, xe + 0.075)                                                     # bordas do patamar deslocadas p/ os furos do pé (ver EE-LC-P)
    for xv in X_VP:
        W(f"VE-3 viga {v_p['perfil']} (borda do patamar +0,90)", v_p, (xv, yp0 + 0.01, zpt), (xv, yp1 - 0.01, zpt))
    ve3 = dict(nome="VE-3", eixo=X_VP[1], d=v_p["d"], bf=v_p["bf"], tw=v_p["tw"], tf=v_p["tf"], z_topo=zpt, lado="+")
    # pisos e barrotes
    for (ya, yb), zz, nm in (((yc0 + 0.01, yc1), Z_CHE_E, "chegada +3,95"), ((yp0, yp1 - 0.01), Z_PAT_E, "patamar +0,90")):
        caixa(f"CHE chapa xadrez 6,3 ({nm})", xe + 0.001, xi, ya, yb, zz - T_CH, zz, GE)
    bar = dim_barrote(B - 0.20)
    out["barrote"] = bar
    bl_, bt_, _ = L_[bar["perfil"]]
    for (ya, yb), zz, xs_ in (((yc0, YT), Z_CHE_E, X_VC), ((yp0, yp1), Z_PAT_E, X_VP)):
        n_b = max(1, math.ceil((yb - ya) / 0.60) - 1)
        for j in range(1, n_b + 1):
            yb_ = ya + j * (yb - ya) / (n_b + 1)
            caixa(f"BE barrote {bar['perfil']} (aba horizontal sob a chapa)", xs_[1] + 0.055, xs_[0] - 0.055, yb_ - bl_ / 1000, yb_, zz - T_CH - bt_ / 1000, zz - T_CH, GE)
            caixa(f"BE barrote {bar['perfil']} — aba vertical (1 M12 na alma da viga em cada ponta)", xs_[1] + 0.0032, xs_[0] - 0.0032, yb_ - bt_ / 1000, yb_, zz - T_CH - bl_ / 1000, zz - T_CH - bt_ / 1000, GE)
    # lance de cima: topo na VE-2, pé apoiado sobre as VE-3 do patamar
    s_endC = LC.s_de(YT + v_t["bf"] / 2000 + 0.010)
    subir_longarina(LC, zch, s_endC)
    rC = longarinas_e_degraus(LC, GE, "EE-LC", s_pe=-0.10, s_topo=s_endC, z_pe=Z_PAT_E, pe_vertical=-0.10)
    lig_topo_em_viga("EE-LC-T", LC, ve2, s_endC, GE, lc["R_d"])
    bfc = LC.u["bf"] / 1000
    ya_c, yb_c = yp0, yp0 + 0.13                                                          # pé: a partir do 1º espelho (y 6,92) para o patamar (+y)
    ya_c, yb_c = EX["y_lance_cima"][1], EX["y_lance_cima"][1] + 0.10
    for lat, sgl in ((LC.l0 + bfc, 1), (LC.l1 - bfc, -1)):
        caixa("EE-LC-P cantoneira L 76 × 51 × 6,3 L=100 — aba no piso (2 M12 na mesa da VE-3)", lat, lat + sgl * 0.076, ya_c, yb_c, Z_PAT_E, Z_PAT_E + 0.0063, GE)
        caixa("EE-LC-P cantoneira L 76 × 51 × 6,3 — aba na longarina (2 M12)", lat, lat + sgl * 0.0063, ya_c, yb_c, Z_PAT_E, Z_PAT_E + 0.051, GE)
    x_furo = (LC.l0 + bfc) + 0.0063 + 0.034                                              # furo a 40 da quina
    chk = [chk_borda("furo na mesa × ponta da mesa", (X_VP[1] + v_p["bf"] / 2000 - x_furo) * 1000, 12),
           chk_chave("furo na mesa × alma da VE-3", (x_furo - X_VP[1] - v_p["tw"] / 2000) * 1000, 12), chk_borda("furo × ponta da aba (76)", 76 - 40, 12),
           ("aba de 51 abaixo do topo da longarina", Z_PAT_E + 0.051 <= LC.z_top(LC.s_de(yb_c)) - 0.003, round((LC.z_top(LC.s_de(yb_c)) - Z_PAT_E - 0.051) * 1000, 1)),
           chk_esp("2 M12", 50, 12)]
    lig("EE-LC-P", "pé do lance × patamar", ["longarina U 203 (lance de cima)", "VE-3 (mesa) + chapa"], "cantoneira L 76 × 51 × 6,3 L = 100",
        "2 M12 na alma da longarina + 2 M12 na mesa da VE-3", lc["R_d"], min(2 * parafuso_corte(12), 2 * contato(12, LC.u["tw"])), chk,
        "pé cortado na horizontal sobre o piso do patamar, ao longo da VE-3 (a VE-3 fica 25 mm para dentro da longarina para os furos caírem na mesa)", GE)
    # lance de baixo: topo na VE-3 externa (perpendicular), pé na BM-2 sobre a BE-2
    ve3["eixo"] = X_VP[1]
    s_endB = LB.s_de(X_VP[1] - v_p["bf"] / 2000 - 0.010)
    subir_longarina(LB, zpt, s_endB)
    rB = longarinas_e_degraus(LB, GE, "EE-LB", s_pe=-0.5, s_topo=s_endB, z_pe=0.0)
    lig_topo_em_viga("EE-LB-T", LB, ve3, s_endB, GE, lb["R_d"])
    bfb = LB.u["bf"] / 1000
    xb0 = EX["x_lance_baixo"][1] - 0.002 - 0.0488
    y0b, y1b = LB.l0 + bfb + 0.005, LB.l1 - bfb - 0.005
    caixa("BM-2 base metálica U 152 × 12,2 em pé (entre as longarinas do lance de baixo)", xb0, xb0 + 0.0488, y0b, y1b, 0.010, 0.010 + 0.1524, GE, tipo="viga")
    caixa("graute de nivelamento 10 mm da BM-2", xb0, xb0 + 0.0488, y0b, y1b, 0.0, 0.010, GE)
    caixa("BE-2 viga de concreto 1,80 × 0,40 × 0,40 sob o pé do lance de baixo (base própria)", xb0 - 0.20, xb0 + 0.20, LB.l0 - 0.15, LB.l1 + 0.15, -0.42, -0.02, "Piso e fundações")
    for lat, sgl in ((LB.l0 + bfb, 1), (LB.l1 - bfb, -1)):
        caixa("CB-2 cantoneira L 76 × 76 × 6,3 × 100 (pé da longarina na alma da BM-2)", xb0 + 0.0488, xb0 + 0.0488 + 0.076, lat, lat + sgl * 0.0063, 0.030, 0.130, GE)
    lig("EE-LB-P", "pé do lance × base metálica", ["longarina U 152 (lance de baixo)", "BM-2 U 152 em pé sobre a BE-2"], "cantoneira L 76 × 76 × 6,3 L = 100",
        "2 M12 na alma da BM-2 + 2 M12 na alma da longarina; BM-2 com 3 chumbadores químicos M12 na BE-2", lb["R_d"] * 0.1 + 1.0, 2 * parafuso_corte(12),
        [chk_faixa("alma da BM-2 × longarina no pé", 0.030, min(0.130, LB.z_top(0.0) - 0.016), 0.080)], "como a BM-1 da escada interna", GE)
    # pilaretes (tubo) nas quinas: chegada (sob VE-1 e VE-2) e patamar (sob VE-3)
    pil_c = dim_pilarete(max(v_t["R_a"], v_c["R_b"]) + v_c["R_a"], zch - v_c["d"] / 1000 - 0.0125)
    pil_p = dim_pilarete(max(v_p["R_a"], v_p["R_b"]), zpt - v_p["d"] / 1000 - 0.0125)
    out.update(pilarete_chegada=pil_c, pilarete_patamar=pil_p)
    pos = [(X_VC[0], yc0 + 0.06, pil_c, zch - v_c["d"] / 1000), (X_VC[1], yc0 + 0.06, pil_c, zch - v_c["d"] / 1000),
           (X_VC[0], YT, pil_c, zch - v_t["d"] / 1000), (X_VC[1], YT, pil_c, zch - v_t["d"] / 1000),
           (X_VP[0], yp0 + 0.08, pil_p, zpt - v_p["d"] / 1000), (X_VP[1], yp0 + 0.08, pil_p, zpt - v_p["d"] / 1000),
           (X_VP[0], yp1 - 0.08, pil_p, zpt - v_p["d"] / 1000), (X_VP[1], yp1 - 0.08, pil_p, zpt - v_p["d"] / 1000)]
    for xp, yp, pf, ztop in pos:
        b = pf["b"] / 1000
        linear(f"PE pilarete {pf['perfil']}", ("R", b, b, pf["perfil"]), (xp, yp, 0.0125), (xp, yp, ztop), GE, cima=(0.0, 1.0, 0.0), tipo="pilar")
        caixa("CBE chapa de base 200 × 200 × 12,5 + 4 chumbadores químicos M16 (sobre graute)", xp - 0.10, xp + 0.10, yp - 0.10, yp + 0.10, 0.0, 0.0125, GE)
        caixa("BE-1 bloco de concreto 60 × 60 × 60 (base própria da escada externa)", xp - 0.30, xp + 0.30, yp - 0.30, yp + 0.30, -0.62, -0.02, "Piso e fundações")
        for sg in (-1, 1):
            caixa("CBE-L cantoneira L 76 × 76 × 6,3 × 100 — base do pilarete na chapa (1 M12 passante + 1 M12 na chapa)", xp - 0.05, xp + 0.05, yp + sg * b / 2, yp + sg * (b / 2 + 0.076), 0.0125, 0.0188, GE)
            caixa("CBE-L cantoneira — aba no tubo", xp - 0.05, xp + 0.05, yp + sg * b / 2, yp + sg * (b / 2 + 0.0063), 0.0125, 0.0885, GE)
            if abs(yp - YT) < 1e-6:                                                           # sob a VE-2 (ao longo de x): cantoneiras nas faces ⊥ x
                caixa("CB-4 cantoneira L 76 × 76 × 6,3 × 100 — topo do pilarete (aba sob a mesa da viga)", xp + sg * b / 2, xp + sg * (b / 2 + 0.076), yp - 0.05, yp + 0.05, ztop - 0.0063, ztop, GE)
                caixa("CB-4 cantoneira — aba no tubo", xp + sg * b / 2, xp + sg * (b / 2 + 0.0063), yp - 0.05, yp + 0.05, ztop - 0.076, ztop, GE)
            else:                                                                             # sob VE-1 / VE-3 (ao longo de y): faces ⊥ y
                caixa("CB-4 cantoneira L 76 × 76 × 6,3 × 100 — topo do pilarete (aba sob a mesa da viga)", xp - 0.05, xp + 0.05, yp + sg * b / 2, yp + sg * (b / 2 + 0.076), ztop - 0.0063, ztop, GE)
                caixa("CB-4 cantoneira — aba no tubo", xp - 0.05, xp + 0.05, yp + sg * b / 2, yp + sg * (b / 2 + 0.0063), ztop - 0.076, ztop, GE)
    lig("EE-PE", "pilarete × vigas e base", ["pilarete " + pil_c["perfil"], "VE-1/VE-2/VE-3; chapa CBE"], "2 cantoneiras L 76 × 76 × 6,3 L = 100 no topo e 2 na base",
        "topo: 1 M12 passante + 2 M12 na mesa (a 25 mm da alma); base: 1 M12 passante + 2 M12 na chapa CBE; CBE com 4 chumbadores químicos M16 no BE-1",
        max(v_t["R_a"], v_p["R_a"]) * 0.1 + 0.5, 2 * parafuso_corte(12),
        [chk_borda("furo na mesa × ponta (bf 100)", 25, 12), chk_chave("furo na mesa × alma", 25 - 2.15, 12), chk_borda("furo × ponta da aba (76)", 36, 12)],
        "viga apoiada no topo do tubo (contato)", GE)
    # VE-1 × VE-2: VE-1 termina a 10 mm da ponta da mesa da VE-2; cantoneira L 102 × 102 × 6,3 nas duas almas (como o topo do lance)
    lig("EE-V12", "viga de borda × viga transversal", ["VE-1", "VE-2"], "cantoneira L 102 × 102 × 6,3 L = 80 (lado de dentro)", "2 M12 em cada alma",
        v_c["R_b"], min(2 * parafuso_corte(12), 2 * contato(12, v_c["tw"])),
        [chk_faixa("alma × alma (mesma altura)", 0.0, (v_c["d"] - 2 * v_c["tf"] - 16) / 1000, 0.080), chk_borda("furo × ponta da aba", 102 - 47.85 - 10 - 22, 12)],
        "mesmo W 150: a VE-1 não precisa de recorte (para na ponta da mesa da VE-2)", GE)
    # rev09d: CONTRAVENTAMENTO em X sob a chegada (a antiga trava TR-1 "no P28" ficava fora da face do pilar — x −0,55 contra a face
    # x −0,30, atrás das placas — e não ligava em nada; retirada). X de barras redondas Ø12,5 ASTM A36 com as pontas roscadas M12,
    # garfo (forquilha) roscado + pino M12 na orelha e esticador no meio: planos x = −0,55 e x = −1,90 (ao longo de y) e plano y da VE-2
    # (ao longo de x). As duas diagonais de cada X ficam 16 mm afastadas (uma de cada lado do eixo do tubo) para não se cruzarem.
    # Orelha = cantoneira L 76 × 76 × 6,3 L = 100 com a aba A na face do tubo (1 M12 passante) e a aba B no plano da barra.
    zb0 = 0.30
    zb1 = zch - v_c["d"] / 1000 - 0.25
    Hd = 1.5 * H_GC * (YT - yc0) + 1.4 * 0.80 * 1.30 * (YT - yc0)                       # guarda-corpo no topo + vento 0,8 kPa na faixa de 1,30
    x_pl = []
    for xp in X_VC:                                                                     # planos ao longo de y
        x_pl.append(("y", xp, (yc0 + 0.06, YT)))
    x_pl.append(("x", YT, (X_VC[1], X_VC[0])))                                          # plano ao longo de x, sob a VE-2
    ndiag = 0
    for dirc, c_, (a0, a1) in x_pl:
        b = pil_c["b"] / 1000
        for k_, (s0, s1, off) in enumerate(((a0, a1, -0.008), (a1, a0, 0.008))):
            sA, sB = s0 + (b / 2 + 0.076) * (1 if s1 > s0 else -1), s1 - (b / 2 + 0.076) * (1 if s1 > s0 else -1)
            if dirc == "y":
                p0_, p1_ = (c_ + off, sA, zb0), (c_ + off, sB, zb1)
            else:
                p0_, p1_ = (sA, c_ + off, zb0), (sB, c_ + off, zb1)
            _L = math.dist(p0_, p1_); _u = [(p1_[i] - p0_[i]) / _L for i in range(3)]
            p0_, p1_ = tuple(p0_[i] + 0.09 * _u[i] for i in range(3)), tuple(p1_[i] - 0.09 * _u[i] for i in range(3))   # garfo (90 mm) fora do 3D: a barra termina antes da aba B
            linear("CX-1 barra redonda Ø12,5 do contraventamento (pontas M12, garfo + pino M12, esticador)", ("R", 0.0125, 0.0125, "barra Ø12,5"), p0_, p1_, GE, tipo="viga")
            ndiag += 1
            for (ss, zz) in ((s0, zb0), (s1, zb1)):                                     # orelhas nas duas pontas
                sg = 1 if (s1 - s0) * (1 if ss == s0 else -1) > 0 else -1
                f0, f1 = ss + sg * b / 2, ss + sg * (b / 2 + 0.076)
                if dirc == "y":
                    caixa("CX-O orelha L 76 × 76 × 6,3 L=100 do X — aba B (pino M12 do garfo)", c_ + off - 0.00315, c_ + off + 0.00315, min(f0, f1), max(f0, f1), zz - 0.05, zz + 0.05, GE)
                    caixa("CX-O orelha — aba A na face do tubo (1 M12 passante)", *((c_ + off - 0.00315, c_ + 0.03) if off < 0 else (c_ - 0.03, c_ + off + 0.00315)), min(f0, f0 + sg * 0.0063), max(f0, f0 + sg * 0.0063), zz - 0.05, zz + 0.05, GE)
                else:
                    caixa("CX-O orelha L 76 × 76 × 6,3 L=100 do X — aba B (pino M12 do garfo)", min(f0, f1), max(f0, f1), c_ + off - 0.00315, c_ + off + 0.00315, zz - 0.05, zz + 0.05, GE)
                    caixa("CX-O orelha — aba A na face do tubo (1 M12 passante)", min(f0, f0 + sg * 0.0063), max(f0, f0 + sg * 0.0063), *((c_ + off - 0.00315, c_ + 0.03) if off < 0 else (c_ - 0.03, c_ + off + 0.00315)), zz - 0.05, zz + 0.05, GE)
    Lx = math.hypot(YT - yc0 - 0.06 - b - 0.152, zb1 - zb0)
    cos_ = (YT - yc0 - 0.06 - b - 0.152) / Lx
    Nd_x = Hd / cos_
    A_b = math.pi * 12.5 ** 2 / 4 / 100                                                 # cm²
    NRd_bar = min(A_b * FY36 / 1e4 / GA1, 0.75 * A_b * FU36 / 1e4 / GA2)                # NBR 8800:2024 5.2.2 e 6.3.3.1 (rosca)
    out["contraventamento"] = dict(barra="Ø12,5 ASTM A36, pontas M12", planos=len(x_pl), diagonais=ndiag, Hd=round(Hd, 2), Nd=round(Nd_x, 2), NRd=round(NRd_bar, 1), uso=round(Nd_x / NRd_bar, 3))
    lig("EE-X", "diagonal do X × pilarete", ["barra Ø12,5 (garfo M12)", "pilarete " + pil_c["perfil"]], "orelha cantoneira L 76 × 76 × 6,3 L = 100 (aba A na face do tubo, aba B no plano da barra)",
        "pino M12 do garfo na aba B (corte duplo) + 1 M12 passante no tubo", Nd_x, min(2 * parafuso_corte(12), contato(12, 6.3), 2 * contato(12, pil_c["t"])),
        [chk_borda("pino × ponta da aba B (76)", 76 - 38, 12), chk_borda("furo × topo/base da orelha (L 100)", 50, 12),
         ("diagonais do X afastadas 16 mm (> Ø12,5 + 3)", 16 >= 12.5 + 3, 16), ("barra abaixo das cantoneiras do topo do pilarete", zb1 + 0.05 < zch - v_c["d"] / 1000 - 0.076, round((zch - v_c["d"] / 1000 - 0.076 - zb1 - 0.05) * 1000))],
        "X sob a chegada nos 3 planos dos pilaretes (sem solda: garfo roscado + pino)", GE)
    out["geom"] = dict(LC=rC, LB=rB, YT=YT, X_VC=X_VC, X_VP=X_VP)
    return out


# ------------------------------------------------------------------ guarda-corpos e corrimãos
def guarda(cod, nome, p0, p1, z0, z1, h, grupo, fix, vazio, corrimao=True, so_corrimao=False, h_cr=0.90, fechamento=True, montantes_fim=True,
           b_max=None, ext=(0.0, 0.0), lance=None, zmin=-99.0):
    """trecho reto de guarda-corpo / corrimão. p0 → p1 em planta (m) = linha de FIXAÇÃO: ponta das mesas da longarina/viga
    ('longarina', 'viga') ou borda da laje ('laje'); z0 → z1 = linha dos bocéis / piso acabado; vazio = vetor em planta para o lado
    livre. Montantes a ≤ 1,20 m: encostados nas pontas das mesas (2 M12 + bucha na alma) ou, na laje, 10 cm para dentro (2 cantoneiras
    com chumbadores). Corrimão do lado da circulação, 40 mm livres do montante; ext = prolongamentos horizontais (m) no início/fim."""
    (xa, ya), (xb, yb) = p0, p1
    L = math.hypot(xb - xa, yb - ya)
    n = max(1, math.ceil(L / 1.20))
    s = L / n
    ux, uy = (xb - xa) / L, (yb - ya) / L
    vx, vy = vazio
    G = dim_gc(h, s, b_max)
    bm = G["montante"]["b"] / 1000
    off = bm / 2 if fix != "laje" else -0.10                              # eixo do montante a partir da linha de fixação (+ = para o vazio)
    zb_rel = {"longarina": -0.19, "viga": -0.14, "laje": 0.0}[fix]        # pé do montante (abaixo do bocel / piso)
    PT = lambda t, d_, zz: (xa + ux * t + vx * d_, ya + uy * t + vy * d_, z0 + (z1 - z0) * t / L + zz)
    th_ = math.atan2(abs(z1 - z0), L)
    tr = G["travessa"]["b"] / 1000
    h_m = h - (0.0 if so_corrimao else tr / math.cos(th_) + bm / 2 * math.tan(th_) + 0.002)   # montante termina sob a travessa (tampa de chapa dobrada)
    for k in range(n + 1):
        if not montantes_fim and k in (0, n):
            continue
        t = k * s
        b0, b1 = PT(t, off, zb_rel), PT(t, off, h_m)
        b0 = (b0[0], b0[1], max(b0[2], zmin + 0.002))
        linear(f"{cod} montante {G['montante']['perfil']} ({nome})", ("R", bm, bm, G["montante"]["perfil"]), b0, (b0[0], b0[1], b1[2]), grupo, cima=(ux, uy, 0.0), tipo="pilar")
        if fix == "laje":
            for sg in (-1, 1):
                q = PT(t + sg * (bm / 2 + 0.051), off, 0.0)
                caixa(f"{cod} cantoneira L 102 × 102 × 9,5 L=150 — base do montante na laje", q[0] - 0.075 * abs(vx) - 0.051 * abs(ux), q[0] + 0.075 * abs(vx) + 0.051 * abs(ux),
                      q[1] - 0.075 * abs(vy) - 0.051 * abs(uy), q[1] + 0.075 * abs(vy) + 0.051 * abs(uy), z0, z0 + 0.0095, grupo)
    ta, tb_ = bm / 2 + 0.003, L - bm / 2 - 0.003                         # cantoneiras entre as faces dos montantes das pontas
    if not so_corrimao:
        zc_tr = h - tr / (2 * math.cos(th_))
        linear(f"{cod} travessa {G['travessa']['perfil']} ({nome})", ("R", tr, tr, G["travessa"]["perfil"]), PT(0.0, off, zc_tr), PT(L, off, zc_tr), grupo)
        if fechamento:
            for zz in (0.10, h - 0.05):
                linear(f"{cod} cantoneira L 38 × 38 × 4,8 das barras ({nome})", ("R", 0.038, 0.038, "L 38×38×4,8"),
                       PT(ta, off - bm / 2 - 0.019, zz), PT(tb_, off - bm / 2 - 0.019, zz), grupo)
    if corrimao:
        D = G["corrimao"]["D"] / 1000
        dist = bm / 2 + 0.040 + D / 2                                      # 40 mm livres entre o corrimão e o montante
        dc = off - dist
        c0, c1 = PT(0.0, dc, h_cr), PT(L, dc, h_cr)
        linear(f"{cod} corrimão {G['corrimao']['perfil']} ({nome})", ("R", D, D, G["corrimao"]["perfil"]), c0, c1, grupo)
        for t_, e_ in ((0.0, -ext[0]), (L, ext[1])):                       # prolongamentos horizontais de 30 cm (CBMRS / NBR 9077)
            if abs(e_) > 1e-6:
                q0 = PT(t_, dc, h_cr)
                q1 = (q0[0] + ux * e_, q0[1] + uy * e_, q0[2])
                linear(f"{cod} corrimão {G['corrimao']['perfil']} — prolongamento de 30 cm ({nome})", ("R", D, D, G["corrimao"]["perfil"]), q0, q1, grupo)
    return dict(cod=cod, nome=nome, L=round(L, 3), n_vaos=n, s=round(s, 3), h=h, h_corrimao=h_cr, fix=fix, gc=G, so_corrimao=so_corrimao, prolongamentos=ext)


def corrimao_parede(cod, nome, ln: Lance, grupo, ext=(0.30, 0.30)):
    """lado da parede (escada externa, placas a 25 mm): montantes 40 × 40 × 4 do lado dos degraus, encostados na alma da longarina
    (2 M12) e apoiados no degrau (atrás da cantoneira do degrau e antes do bocel do degrau seguinte); corrimão 40 mm livres."""
    G = dim_gc(0.90, 1.12, 40)
    bm = G["montante"]["b"] / 1000
    bf = ln.u["bf"] / 1000
    lat_w = ln.l1 - bf                                                     # face da alma do lado dos degraus (longarina junto à parede)
    sgl = -1                                                               # para dentro da escada (−x)
    ks = list(range(1, ln.n - 2, 4)) + [ln.n - 2]                         # último montante no penúltimo degrau (livre da ligação do topo)
    for k in ks:
        sm = k * ln.p - 0.05                                               # centro do montante: 30–70 mm antes do espelho seguinte
        zk = ln.z_degrau(k)
        x0, x1 = lat_w + sgl * bm, lat_w
        y0, y1 = ln.c(sm) - bm / 2, ln.c(sm) + bm / 2
        caixa(f"{cod} montante {G['montante']['perfil']} ({nome}) — na alma da longarina, sobre o degrau {k}", min(x0, x1), max(x0, x1), y0, y1, zk, zk + 1.00, grupo, tipo="pilar")
    D = G["corrimao"]["D"] / 1000
    xc = lat_w + sgl * (bm + 0.040 + D / 2)
    z_a, z_b = ln.z_nosing(0.0) + 0.90, ln.z_nosing(ln.L_h) + 0.90
    linear(f"{cod} corrimão {G['corrimao']['perfil']} ({nome})", ("R", D, D, G["corrimao"]["perfil"]), (xc, ln.c(0.0), z_a), (xc, ln.c(ln.L_h), z_b), grupo)
    for c_, z_, e_ in ((ln.c(0.0), z_a, ext[0] * -ln.sg), (ln.c(ln.L_h), z_b, ext[1] * ln.sg)):
        linear(f"{cod} corrimão {G['corrimao']['perfil']} — prolongamento de 30 cm ({nome})", ("R", D, D, G["corrimao"]["perfil"]), (xc, c_, z_), (xc, c_ + e_, z_), grupo)
    largura_livre = (ln.l1 - ln.l0) - 2 * bf - (bm + 0.040 + D) - 0.0
    return dict(cod=cod, nome=nome, L=round(ln.L_h, 3), n_vaos=len(ks) - 1, s=1.12, h=0.90, h_corrimao=0.90, fix="degrau", gc=G, so_corrimao=True, prolongamentos=ext,
                largura_livre_m=round(largura_livre, 3))


def vigas_borda():
    """vigas de borda W 150 × 9,2 nos lados dos patamares sem viga (recebem os montantes do guarda-corpo); ligadas nas almas das vigas
    principais por cantoneira L 102 × 102 × 6,3 (2 M12 em cada alma), a 8 mm da ponta das mesas."""
    p = ML.perfil("W 150 x 9,2")
    I = ("I", p.d / 1000, p.bf / 1000, p.tw / 1000, p.tf / 1000, "W 150 × 9,2")
    V = esc_int["vigas"]
    bf = p.bf / 1000
    zP, zC = Z_PAT - T_CH, Z_PISO_PRONTO - T_CH
    out = []
    for nm, xe_, ya, yb, zz in (("VP-5 viga de borda W 150 × 9,2 (patamar, lado x 36,30)", X6 + 0.01 + bf / 2, V["VP2"]["eixo"] + bf / 2 + 0.008, V["VP1"]["eixo"] - bf / 2 - 0.008, zP),
                                ("VP-5 viga de borda W 150 × 9,2 (patamar, lado do eixo E)", XE_ - 0.01 - bf / 2, V["VP2"]["eixo"] + bf / 2 + 0.008, V["VP1"]["eixo"] - bf / 2 - 0.008, zP),
                                ("VP-6 viga de borda W 150 × 9,2 (chegada, lado do eixo E)", XE_ - 0.01 - bf / 2, V["VP3"]["eixo"] + bf / 2 + 0.008, V["VP4"]["eixo"] - bf / 2 - 0.008, zC)):
        linear(nm, I, (xe_, ya, zz - p.d / 2000), (xe_, yb, zz - p.d / 2000), GI)
        out.append(dict(nome=nm, x=xe_, toe=(xe_ - bf / 2, xe_ + bf / 2), y=(ya, yb)))
    xi, xe = EX["x_int"], EX["x_ext"]
    yp0, yp1 = EX["y_patamar"]
    yc0, yc1 = EX["y_chegada"]
    X_VP, X_VC = esc_ext["geom"]["X_VP"], esc_ext["geom"]["X_VC"]
    zPe, zCe = Z_PAT_E - T_CH, Z_CHE_E - T_CH
    for nm, ye_, x0, x1, zz in (("VE-4 viga de borda W 150 × 9,2 (patamar, lado da linha 2)", yp1 - 0.01 - bf / 2, X_VP[1] + bf / 2 + 0.008, X_VP[0] - bf / 2 - 0.008, zPe),
                                ("VE-5 viga de borda W 150 × 9,2 (chegada, ponta da linha 1)", yc0 + 0.01 + bf / 2, X_VC[1] + bf / 2 + 0.008, X_VC[0] - bf / 2 - 0.008, zCe)):
        linear(nm, I, (x0, ye_, zz - p.d / 2000), (x1, ye_, zz - p.d / 2000), GE)
        out.append(dict(nome=nm, y=ye_, toe=(ye_ - bf / 2, ye_ + bf / 2), x=(x0, x1)))
    lig("VB-V", "viga de borda × viga principal", ["VP-5 / VP-6 / VE-4 / VE-5", "VP-1 a VP-4, VE-1, VE-3"], "cantoneira L 102 × 102 × 6,3 L = 80 (dos 2 lados da alma)",
        "2 M12 8.8 em cada alma", 3.0, min(2 * parafuso_corte(12), 2 * contato(12, 3.1)),
        [chk_faixa("alma × alma (mesma altura, W 150 × 9,2)", 0.0, (146 - 2 * 3.6 - 16) / 1000, 0.080), chk_borda("furo × ponta da aba", 102 - 48.45 - 8 - 22, 12)],
        "sem recorte: a viga de borda para a 8 mm da ponta da mesa da viga principal", GI)
    return out


def guardas():
    gs = []
    zt = lambda ln, s: ln.z_nosing(s)
    V = esc_int["vigas"]
    bfp = 0.098 / 2
    # ---- escada interna (h 0,92 nos lances, 1,05 nos patamares / abertura; corrimão 0,90)
    gs.append(guarda("GI-1", "lance 1, lado livre (x 36,30)", (L1.l0, L1.c(0.0)), (L1.l0, L1.c(L1.L_h)), zt(L1, 0.0), zt(L1, L1.L_h), 0.92, GI, "longarina", (-1, 0), ext=(0.30, 0.0), zmin=L1.z0))
    gs.append(guarda("GI-2", "lance 1, lado do vão central (só corrimão)", (L1.l1, L1.c(0.12)), (L1.l1, L1.c(L1.L_h - 0.05)), zt(L1, 0.12), zt(L1, L1.L_h - 0.05), 0.92, GI, "longarina", (1, 0),
                     so_corrimao=True, b_max=40, ext=(0.42, 0.0), zmin=L1.z0))                # 1º montante 12 cm para dentro (livre da base do PL-3)
    gs.append(guarda("GI-3", "lance 2, lado do vão central", (L2.l0, L2.c(0.0)), (L2.l0, L2.c(L2.L_h)), zt(L2, 0.0), zt(L2, L2.L_h), 0.92, GI, "longarina", (-1, 0), b_max=40, ext=(0.0, 0.30), zmin=L2.z0))
    gs.append(guarda("GI-4", "lance 2, lado do eixo E (60 cm até a parede)", (L2.l1, L2.c(0.0)), (L2.l1, L2.c(L2.L_h)), zt(L2, 0.0), zt(L2, L2.L_h), 0.92, GI, "longarina", (1, 0), ext=(0.0, 0.0), zmin=L2.z0))
    # retorno do corrimão interno no patamar (liga o corrimão do lance 1 ao do lance 2 em volta da ponta do vão central)
    Dr = 0.0381
    xa_r, xb_r = L1.l1 + 0.020 - (0.020 + 0.040 + Dr / 2), L2.l0 - 0.020 + (0.020 + 0.040 + Dr / 2)
    for (a_, b_) in (((xa_r, Y_LAN[0] - 0.12), (xb_r, Y_LAN[0] - 0.12)), ((xa_r, Y_LAN[0] - 0.12), (xa_r, Y_LAN[0] - 0.025)), ((xb_r, Y_LAN[0] - 0.12), (xb_r, Y_LAN[0] - 0.025))):
        linear("GI-R corrimão tubo Ø38,1 × 2 — retorno no patamar (curvas de 90°, luvas parafusadas)", ("R", Dr, Dr, "tubo Ø38,1 × 2"), (a_[0], a_[1], Z_PAT + 0.90), (b_[0], b_[1], Z_PAT + 0.90), GI)
    yP0, yP1 = Y_PAT
    gs.append(guarda("GI-5", "patamar +1,975, lado do P6–P7", (X6 + 0.01 + 0.098 + 0.01, V["VP2"]["eixo"] - bfp), (XE_ - 0.01 - 0.098 - 0.01, V["VP2"]["eixo"] - bfp), Z_PAT, Z_PAT, 1.05, GI, "viga", (0, -1)))
    gs.append(guarda("GI-6", "patamar +1,975, lado x 36,30", (X6 + 0.01, V["VP2"]["eixo"] + 0.20), (X6 + 0.01, V["VP1"]["eixo"] - bfp - 0.02), Z_PAT, Z_PAT, 1.05, GI, "viga", (-1, 0)))
    gs.append(guarda("GI-7", "patamar +1,975, lado do eixo E", (XE_ - 0.01, V["VP2"]["eixo"] + 0.20), (XE_ - 0.01, yP1 - 0.29), Z_PAT, Z_PAT, 1.05, GI, "viga", (1, 0)))
    yC0, yC1 = Y_CHE
    gs.append(guarda("GI-8", "chegada +3,95, sobre a entrada do lance 1", (ABERTURA["x0"] + 0.05, V["VP3"]["eixo"] - bfp), (X6 + BL - 0.02, V["VP3"]["eixo"] - bfp), Z_PISO_PRONTO, Z_PISO_PRONTO, 1.05, GI, "viga", (0, -1)))
    gs.append(guarda("GI-9", "chegada +3,95, lado do eixo E", (XE_ - 0.01, V["VP3"]["eixo"] + bfp + 0.04), (XE_ - 0.01, V["VP4"]["eixo"] - bfp - 0.04), Z_PISO_PRONTO, Z_PISO_PRONTO, 1.05, GI, "viga", (1, 0)))
    gs.append(guarda("GI-10", "laje +3,90, borda x 36,00 da abertura", (ABERTURA["x0"], ABERTURA["y0"] + 0.12), (ABERTURA["x0"], yC0 - 0.10), Z_PISO_PRONTO, Z_PISO_PRONTO, 1.05, GI, "laje", (1, 0)))
    gs.append(guarda("GI-11", "laje +3,90, borda y 3,99 da abertura (sobre a VM-04)", (ABERTURA["x0"] + 0.12, ABERTURA["y0"]), (XE_ - 0.15, ABERTURA["y0"]), Z_PISO_PRONTO, Z_PISO_PRONTO, 1.05, GI, "laje", (0, 1)))
    # ---- escada externa (h 1,30; corrimão 0,90 dos dois lados)
    xi, xe = EX["x_int"], EX["x_ext"]
    X_VP, X_VC = esc_ext["geom"]["X_VP"], esc_ext["geom"]["X_VC"]
    gs.append(guarda("GE-1", "lance de cima, lado externo (x −1,95)", (LC.l0, LC.c(0.10)), (LC.l0, LC.c(LC.L_h - 0.06)), zt(LC, 0.10), zt(LC, LC.L_h - 0.06), 1.30, GE, "longarina", (-1, 0), zmin=LC.z0))
    gs.append(corrimao_parede("GE-2", "lance de cima, lado da parede", LC, GE))
    gs.append(guarda("GE-3", "lance de baixo, lado da linha 1", (LB.c(0.0), LB.l0), (LB.c(LB.L_h - 0.07), LB.l0), zt(LB, 0.0), zt(LB, LB.L_h - 0.07), 1.30, GE, "longarina", (0, -1), ext=(0.30, 0.0), zmin=LB.z0))
    gs.append(guarda("GE-4", "lance de baixo, lado da linha 2", (LB.c(0.0), LB.l1), (LB.c(LB.L_h - 0.07), LB.l1), zt(LB, 0.0), zt(LB, LB.L_h - 0.07), 1.30, GE, "longarina", (0, 1), ext=(0.30, 0.0), zmin=LB.z0))
    yp0, yp1 = EX["y_patamar"]
    gs.append(guarda("GE-5", "patamar +0,90, lado da linha 2", (X_VP[1] + 0.06, yp1 - 0.01), (X_VP[0] - 0.06, yp1 - 0.01), Z_PAT_E, Z_PAT_E, 1.30, GE, "viga", (0, 1)))
    yc0, yc1 = EX["y_chegada"]
    gs.append(guarda("GE-6", "chegada +3,95, lado externo (x −1,95)", (X_VC[1] - bfp, yc0 + 0.06), (X_VC[1] - bfp, yc1 - 0.10), Z_CHE_E, Z_CHE_E, 1.30, GE, "viga", (-1, 0)))
    gs.append(guarda("GE-7", "chegada +3,95, ponta da linha 1", (X_VC[1] + 0.06, yc0 + 0.01), (xi - 0.03, yc0 + 0.01), Z_CHE_E, Z_CHE_E, 1.30, GE, "viga", (0, -1)))
    return gs


# ------------------------------------------------------------------ pé-direito livre ≥ 2,10 m
def pe_direito():
    """menor distância vertical entre a faixa de circulação (bocéis e pisos dos patamares) e o que está acima (vigas VM do mezanino,
    fundo das lajes, outras partes da escada) — malha de 5 cm em planta."""
    hv = json.loads((AQ / "vm_retangular.json").read_text(encoding="utf-8"))["premissas"]
    h_vm = hv.get("h", 0.75)
    obst = []
    for iz, zp in enumerate(Z_PISOS):
        zb = Z_APOIO_LAJE[iz] - h_vm
        for yv in (Y_LIN[0], Y_LIN[1]):
            obst.append(("VM " + ("+3,90" if iz == 0 else "+7,30") + f" linha {1 if yv == 0 else 2}", 29.0, 40.0, yv - 0.15, yv + 0.15, zb))
        if iz == 0:
            obst.append(("VM-04 P6–P7 (+3,90)", P6_ESC[0], P7_ESC[0], P6_ESC[1] - 0.15, P6_ESC[1] + 0.15, zb))
        obst.append(("fundo da laje " + ("+3,90" if iz == 0 else "+7,30"), 29.0, 40.0, 0.0, Y_LIN[1], zp - 0.25))
    ab = ABERTURA
    vp = esc_int["vigas"]
    obst.append(("VP-3 chegada (fundo)", vp["VP3"]["x0"], vp["VP3"]["x1"], vp["VP3"]["eixo"] - 0.05, vp["VP3"]["eixo"] + 0.05, vp["VP3"]["z_topo"] - vp["VP3"]["d"] / 1000))
    res = []
    faixas = [("lance 1", L1, None), ("lance 2", L2, None), ("patamar +1,975", None, (X6 + 0.05, XE_ - 0.05, Y_PAT[0] + 0.05, Y_PAT[1], Z_PAT)),
              ("chegada +3,95", None, (ab["x0"], XE_ - 0.05, Y_CHE[0], Y_CHE[1], Z_PISO_PRONTO)), ("térreo sob a chegada (entrada do lance 1)", None, (X6 + 0.05, X6 + BL, Y_CHE[0], Y_CHE[1], 0.0))]
    for nome, ln, box in faixas:
        pts = []
        if ln:
            for j in range(0, int(ln.L_h / 0.05) + 1):
                s = j * 0.05
                for lat in (ln.l0 + 0.10, (ln.l0 + ln.l1) / 2, ln.l1 - 0.10):
                    x, y, _ = ln.pt(s, lat, 0)
                    pts.append((x, y, ln.z_nosing(min(s, ln.L_h - ln.p)) if s > 0 else ln.z0 + ln.e))
        else:
            x0, x1, y0, y1, z = box
            pts = [(x0 + (x1 - x0) * i / 10, y0 + (y1 - y0) * j / 10, z) for i in range(11) for j in range(11)]
        best = (99.0, "")
        for x, y, z in pts:
            for on, ox0, ox1, oy0, oy1, oz in obst:
                if ox0 <= x <= ox1 and oy0 <= y <= oy1 and oz > z and not (on.startswith("fundo da laje +3,90") and ab["x0"] <= x <= ab["x1"] + 0.6 and ab["y0"] <= y <= ab["y1"]):
                    if oz - z < best[0]:
                        best = (oz - z, on)
        res.append(dict(faixa=nome, pe_direito_min_m=round(best[0], 2), sob=best[1], ok=best[0] >= 2.10))
    res.append(dict(faixa="escada externa (lances, patamar e chegada)", pe_direito_min_m=None, sob="nada acima (fora da fachada A); porta do 2º pav. com 2,14 m", ok=EX["porta_h"] >= 2.10))
    return res


# ================================================================== execução
esc_int = escada_interna()
esc_ext = escada_externa()
BORDAS = vigas_borda()
GUARDAS = guardas()
PD = pe_direito()

# ligações dos guarda-corpos (um tipo por fixação)
_gmax = {}
for g in GUARDAS:
    k = (g["fix"], g["h"])
    if k not in _gmax or g["gc"]["fixacao_montante"]["F_d"] > _gmax[k]["gc"]["fixacao_montante"]["F_d"]:
        _gmax[k] = g
for (fix, h), g in sorted(_gmax.items()):
    fm = g["gc"]["fixacao_montante"]
    if fix == "longarina":
        lig(f"GC-L{h:.2f}".replace(".", ","), "montante × longarina", [g["gc"]["montante"]["perfil"], "longarina U (alma)"], "bucha espaçadora tubo Ø21,3 × 2,6 L = 46 (atravessa a faixa das mesas)",
            "2 M12 8.8 a 70 mm, atravessando o montante, a bucha e a alma da longarina", fm["F_d"], min(fm["VRd"], contato(12, 5.08), fm["contato_tubo_Rd"]),
            [chk_esp("2 M12", 70, 12), chk_chave("furos × mesas da longarina (furos na linha média da alma)", (152.4 - 70) / 2 - 8.7, 12),
             chk_borda("furo × topo do montante (40 abaixo da longarina)", 40, 12)],
            f"montante encostado nas pontas das 2 mesas (mesas para fora), h {h:.2f} m".replace(".", ","), GI)
    elif fix == "viga":
        lig(f"GC-V{h:.2f}".replace(".", ","), "montante × viga do piso", [g["gc"]["montante"]["perfil"], "viga W 150 (alma)"], "bucha espaçadora tubo Ø21,3 × 2,6 L = 48",
            "2 M12 8.8 a 70 mm na alma da viga (faixa livre 128)", fm["F_d"], min(fm["VRd"], contato(12, min(esc_int["viga_patamar_fundo"]["tw"], esc_ext["viga_chegada"]["tw"])), fm["contato_tubo_Rd"]),
            [chk_esp("2 M12", 70, 12), chk_chave("furos × mesas da viga (W 150 × 9,2: faixa 138,8)", (146 - 2 * 3.6 - 70) / 2, 12)], f"h {h:.2f} m".replace(".", ","), GI)
    else:
        T = fm["F_d"] * 0.070 / 0.110 / 2
        lig("GC-LAJE", "montante × laje (+3,90)", [g["gc"]["montante"]["perfil"], "laje alveolar + capa / VM-04"], "2 cantoneiras L 102 × 102 × 9,5 L = 150 (uma de cada lado do montante)",
            "2 M12 passantes no montante + 4 chumbadores químicos M10 hef 70 na capa/laje (2 por cantoneira)", T, 8.0,
            [chk_borda("chumbador × borda da laje", 60, 10), chk_esp("chumbadores", 110, 10)], "tração de cálculo por chumbador × resistência de catálogo M10 hef 70 em C25 (conferir catálogo)", GI)
lig("CR-S", "corrimão × montante", ["corrimão Ø38,1", "montante"], "suporte de chapa dobrada 4,75 × 40 em L (afasta 40 mm livres) + abraçadeira", "1 M10 no montante + 2 M8 na abraçadeira",
    GAMA_Q * P_CR, parafuso_corte(10), [chk_borda("furo M10 × ponta do suporte", 20, 10)], "suporte a cada montante (≤ 1,20 m)", GI)
lig("GC-B", "barras do fechamento × cantoneiras", ["barra Ø12,7", "L 38 × 38 × 4,8"], "barras com as 2 pontas roscadas M12 em furos Ø14 das abas horizontais",
    "porca + contraporca em cada ponta (vão livre 117 mm < 150)", GAMA_Q * Q_GC * 0.13 * 0.85 / 2, parafuso_corte(12) * 0.5, [chk_borda("furo × borda da aba (38)", 19, 12) if False else ("furo Ø14 no meio da aba de 38", True, 19)],
    "cantoneiras parafusadas nos montantes (1 M10 por ponta)", GI)



def _kg_peca(pc):
    """massa (kg) de uma peça de aço do modelo (concreto e graute ficam fora: None)."""
    import re
    mk = pc["marca"]
    if mk.startswith(("graute", "BE-1 ", "BE-2 ")) or "concreto" in mk:
        return None
    if pc["g"] == "caixa" and "tubo" in mk.split(" — ")[0]:  # montante em tubo modelado como caixa maciça: massa do tubo
        m_ = re.search(r"tubo ([\d,]+) × ([\d,]+) × ([\d,]+)", mk)
        b_, _, t = (float(v.replace(",", ".")) for v in m_.groups())
        return max(pc["x1"] - pc["x0"], pc["y1"] - pc["y0"], pc["z1"] - pc["z0"]) * tubo_q(b_, t)["kg"]
    if pc["g"] == "caixa":                                    # chapas, degraus e cada aba das cantoneiras (caixa = aba)
        return (pc["x1"] - pc["x0"]) * (pc["y1"] - pc["y0"]) * (pc["z1"] - pc["z0"]) * 7850
    if pc["g"] == "poligono":                                 # longarinas U: comprimento ao longo da linha da peça × kg/m
        nm = next(k for k in U if k.split(" (")[0] in mk)
        cs = [c for c, _ in pc["contorno"]]; zs = [z for _, z in pc["contorno"]]
        Lh = max(cs) - min(cs); Lv = max(zs) - min(zs) - U[nm]["d"] / 1000
        return math.hypot(Lh, max(Lv, 0.0)) * U[nm]["kg"]
    L = math.dist(pc["p0"], pc["p1"]); pf = pc["perfil"]
    if pf[0] == "I":
        return L * float(re.search(r"× ([\d,]+)", pf[5]).group(1).replace(",", "."))
    nm = pf[3].replace("×", " × ").replace("  ", " ")
    m_ = re.match(r"barra Ø([\d,]+)$", nm)
    if m_:
        d_ = float(m_.group(1).replace(",", ".")); return L * math.pi * d_ * d_ / 4 * 7.85e-3
    m_ = re.search(r"Ø([\d,]+) × ([\d,]+)", nm)
    if m_:
        D, t = (float(v.replace(",", ".")) for v in m_.groups()); return L * tubo_r(D, t)["kg"]
    m_ = re.search(r"tubo ([\d,]+) +× +([\d,]+) +× +([\d,]+)", nm)
    if m_:
        b_, _, t = (float(v.replace(",", ".")) for v in m_.groups()); return L * tubo_q(b_, t)["kg"]
    m_ = re.search(r"L ([\d,]+) +× +([\d,]+) +× +([\d,]+)", nm)
    if m_:
        b_, _, t = (float(v.replace(",", ".")) for v in m_.groups()); return L * (2 * b_ - t) * t * 7.85e-3
    raise ValueError(mk)


def lista_material():
    """lista por escada e por item (código da marca + perfil), com as barras Ø do fechamento dos guarda-corpos (não modeladas no 3D)."""
    import re
    out = {}
    ult = {}
    for pc in P:
        kg = _kg_peca(pc)
        if kg is None:
            continue
        esc = "externa" if "externa" in pc["grupo"] else "interna"
        cod = pc["marca"].split()[0]
        cab = pc["marca"].split(" — ")[0]
        if " — aba" in pc["marca"] and pc["g"] == "caixa" and ult.get("_prev") == (esc, cod) and not ult.get("_merg"):
            out[ult[(esc, cod)]]["kg"] += kg                   # 2ª aba da cantoneira (peça seguinte com o mesmo código): soma na anterior
            ult["_merg"] = True
            continue
        ult["_prev"], ult["_merg"] = (esc, cod), False
        if pc["g"] == "caixa" and cod in ("GI-10", "GI-11") and "L 102" in cab:
            kg *= 2                                            # cantoneira da base do montante na laje: só a aba vertical está no 3D
        desc = re.sub(r" \(.*$", "", cab)[len(cod) + 1:]
        desc = re.sub(r" L=\d+$", "", desc)
        k = (esc, cod, desc)
        r = out.setdefault(k, dict(escada=esc, item=cod, desc=desc, qt=0, kg=0.0))
        r["qt"] += 1; r["kg"] += kg
        ult[(esc, cod)] = k
    for g in GUARDAS:
        br = g["gc"].get("barra")
        if not br or g.get("so_corrimao"):
            continue
        esc = "externa" if g["cod"].startswith("GE") else "interna"
        n = int(round(g["L"] / (br["s_mm"] / 1000)))
        hb = g["h"] - 0.15
        k = (esc, g["cod"], br["perfil"])
        out[k] = dict(escada=esc, item=g["cod"], desc=f"{br['perfil']} do fechamento c/{br['s_mm']} (h {hb:.2f} m)".replace(".", ","), qt=n, kg=n * hb * br["kg_m"])
    linhas = sorted(out.values(), key=lambda r: (r["escada"], r["item"]))
    for r in linhas:
        r["kg"] = round(r["kg"], 1)
    massa = {e: round(sum(r["kg"] for r in linhas if r["escada"] == e), 0) for e in ("interna", "externa")}
    return linhas, massa


LISTA, MASSA = lista_material()
conflitos = [dict(cod=c["cod"], falhas=[k for k in c["checks"] if not k["ok"]], uso=c["uso"]) for c in C if not c["ok"]]
RES = dict(norma="RT CBMRS nº 11 Parte 01/2016; NBR 9077; NBR 14718:2019; NBR 8800:2024 (ligações)", cargas=dict(q_kN_m2=Q, guarda_corpo_kN_m=H_GC, fechamento_kPa=Q_GC, corrimao_kN=P_CR),
           interna={k: v for k, v in esc_int.items() if k not in ("geom",)}, externa={k: v for k, v in esc_ext.items() if k not in ("geom",)},
           guardas=GUARDAS, ligacoes=C, conflitos=conflitos, n_conflitos=len(conflitos), pe_direito=PD, lista=LISTA, massa_kg=MASSA,
           pecas=P)
if __name__ == "__main__":
    (AQ / "escadas.json").write_text(json.dumps(RES, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("longarinas:", esc_int["longarina"]["perfil"], esc_ext["longarina_cima"]["perfil"], esc_ext["longarina_baixo"]["perfil"])
    for k in ("viga_patamar_frente", "viga_patamar_fundo", "viga_chegada_frente", "viga_chegada_fundo", "barrote", "pilarete_patamar", "pilarete_chegada"):
        v = esc_int[k]; print(" int", k, v["perfil"], "uso", v["uso"])
    for k in ("viga_transversal", "viga_chegada", "viga_patamar", "barrote", "pilarete_chegada", "pilarete_patamar"):
        v = esc_ext[k]; print(" ext", k, v["perfil"], "uso", v["uso"])
    for g in GUARDAS:
        print(" ", g["cod"], g["nome"], "L", g["L"], "s", g["s"], {k: (v.get("perfil"), v.get("uso")) for k, v in g["gc"].items() if isinstance(v, dict) and "perfil" in v})
    print("ligações:", len(C), "conflitos:", len(conflitos))
    for c in conflitos:
        print("  !", c)
    for p in PD:
        print("  pé-direito", p)
    print(len(P), "peças; massa", MASSA)
