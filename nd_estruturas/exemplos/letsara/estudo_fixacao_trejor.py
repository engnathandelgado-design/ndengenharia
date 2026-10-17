"""Letsara rev06 — estudo em IFC dos sistemas Trejor de fixação de painéis (https://www.trejor.com/fixacao-de-paineis)
para a placa protendida 125 × 10 (PP00): qual se adapta à espessura de 10 cm.

Um trecho de parede por sistema, lado a lado (afastados 4 m em x), cada um com o pilar 40 × 60 (lado de 40 na parede),
duas fiadas de placas e as peças do sistema:
  S1 console PARAFUSADO: TSA gabaritado no pilar + console parafusado + chapa de apoio/nicho na placa (placa por fora do pilar)
  S2 console SOLDADO: chapa de espera + console soldado + nicho — só para comparar; fora do padrão ND (sem solda)
  S3 console CONCRETADO: console embutido no pilar + nicho (placa por fora do pilar)
  S4 console FACA: gaveta no pilar + faca + nicho de topo na placa + shims (placa ENTRE pilares, abertura ≤ 20 mm)

A Trejor não publica dimensões: as medidas abaixo são de pré-dimensionamento (DIM) e precisam vir do catálogo/desenho
do fornecedor. O estudo confere a geometria contra a placa real (cordoalhas a 2,64 cm das faces nas alturas do corte A-A
do PP00, cobrimento 2,0 cm, junta 20 mm no eixo do pilar, folga 25 mm placa × pilar) e grava estudo_trejor.json.
Eixos locais: x ao longo da parede, y para fora (face externa do pilar em y = 0), z para cima. Unidades: m.
"""
import json
import sys
from pathlib import Path

from nd_estruturas.bim import ModeloBIM, PerfilRetangular, gravar_ifc

AQ = Path(__file__).parent
sys.path.insert(0, str(AQ))
from modelo_bim import caixa, barra_v  # noqa: E402

E, H, FOLGA, JUNTA = 0.100, 1.25, 0.025, 0.020          # placa (PP00), folga placa × pilar, junta no eixo
BP, DP = 0.40, 0.60                                       # pilar: lado na parede, profundidade
Z_CORD = [0.156, 0.469, 0.781, 1.094]                     # alturas das cordoalhas na placa (corte A-A do PP00)
D_CORD, Y_CORD = 0.0127, 0.0264                           # Ø e eixo a partir de cada face
COB = 0.020
GP, GE, GC = "Fixação das placas", "Esperas e insertos embutidos", "Placas de fechamento"

# ------------------------------------------------------------------ pré-dimensionamento das peças (DIM — confirmar com a Trejor)
DIM = dict(
    tsa=dict(b=0.120, h=0.260, t=0.0125, pino=0.016, hef=0.150, rosca="2 buchas M20"),
    console=dict(b=0.110, t_costas=0.016, h_costas=0.220, t_aba=0.0125, h_braco=0.100, nariz=0.055, paraf_sup="M20", paraf_frontal="M16"),
    nicho=dict(b=0.150, h=0.200, prof=0.060, t=0.00475, t_apoio=0.0125, z_centro=0.312),
    faca=dict(t=0.025, h=0.150, na_gaveta=0.110, na_placa=0.100, abertura=0.020),
    gaveta=dict(b=0.040, h=0.190, prof=0.130, t=0.00475),
    nicho_faca=dict(b=0.035, h=0.180, prof=0.115, t=0.00475),
)


def placas(m, x0, entre=False, y_placa=None):
    """Duas fiadas de placas. Por fora: juntas no eixo do pilar. Entre pilares: placas a partir das faces laterais + 20 mm."""
    regs = []
    for k in range(2):
        z0 = k * H
        if entre:
            trechos = [(x0 - 2.0, x0 - BP / 2 - DIM["faca"]["abertura"]), (x0 + BP / 2 + DIM["faca"]["abertura"], x0 + 2.0)]
            ya, yb = y_placa
        else:
            trechos = [(x0 - 2.0, x0 - JUNTA / 2), (x0 + JUNTA / 2, x0 + 2.0)]
            ya, yb = FOLGA, FOLGA + E
        for a, b in trechos:
            caixa(m, f"PP placa 125 × 10 (fiada {k + 1})", a, b, ya, yb, z0 + 0.005, z0 + H - 0.005, GC)
            for zc in Z_CORD:
                for yc in (ya + Y_CORD, yb - Y_CORD):
                    caixa(m, "C1 cordoalha Ø12,7", a + 0.002, b - 0.002, yc - D_CORD / 2, yc + D_CORD / 2, z0 + zc - D_CORD / 2, z0 + zc + D_CORD / 2, "Cordoalhas das placas")
            regs.append((a, b, ya, yb, z0))
    return regs


def pilar(m, x0, nome):
    m.pilar(nome, x0, -DP / 2, BP, DP, -0.20, 2.70, obs="40 × 60 (lado de 40 na parede) — trecho do estudo")


def nicho_face(m, xc, z0, ya, marca="NI chapa de apoio / nicho (placa)"):
    """Nicho na face interna da placa (y = ya), aberto para o pilar; chapa de apoio no teto."""
    n = DIM["nicho"]
    zc, b, h, p, t = z0 + n["z_centro"], n["b"], n["h"], n["prof"], n["t"]
    x0, x1, z_a, z_b, y1 = xc - b / 2, xc + b / 2, zc - h / 2, zc + h / 2, ya + p
    caixa(m, marca, x0, x1, y1 - t, y1, z_a, z_b, GE, obs="fundo")
    caixa(m, marca, x0, x0 + t, ya, y1, z_a, z_b, GE)
    caixa(m, marca, x1 - t, x1, ya, y1, z_a, z_b, GE)
    caixa(m, marca, x0, x1, ya, y1, z_a, z_a + t, GE)
    caixa(m, marca + " — chapa de apoio", x0, x1, ya, y1, z_b - n["t_apoio"], z_b, GE, obs="teto: recebe o parafuso superior")
    for dx in (-0.05, 0.05):                                          # grampos de ancoragem Ø8 na placa
        caixa(m, "grampo Ø8 do nicho", xc + dx - 0.004, xc + dx + 0.004, ya + 0.03, y1, z_b, z_b + 0.25, GE)
    return dict(x0=x0, x1=x1, z_a=z_a, z_b=z_b, y0=ya, y1=y1)


def console_externo(m, xc, z_ap, tipo):
    """Console com braço saindo da face externa do pilar até o nicho. z_ap = face inferior da chapa de apoio do nicho."""
    c, t = DIM["console"], DIM["tsa"]
    y_ini = 0.0
    if tipo == "parafusado":
        caixa(m, "TSA gabaritado (pilar)", xc - t["b"] / 2, xc + t["b"] / 2, -t["t"], 0.0, z_ap - 0.20, z_ap + 0.06, GE, obs=t["rosca"])
        for dz in (-0.15, 0.00):
            caixa(m, "TSA pino de ancoragem Ø16", xc - 0.008, xc + 0.008, -t["t"] - t["hef"], -t["t"], z_ap + dz - 0.008, z_ap + dz + 0.008, GE)
        caixa(m, "CP console parafusado — costas", xc - c["b"] / 2, xc + c["b"] / 2, 0.0, c["t_costas"], z_ap - 0.19, z_ap + 0.03, GP)
        for dz in (-0.15, 0.00):
            caixa(m, "M20 8.8 (console × TSA)", xc - 0.010, xc + 0.010, -0.040, c["t_costas"] + 0.012, z_ap + dz - 0.010, z_ap + dz + 0.010, GP)
        y_ini = c["t_costas"]
        nome = "CP console parafusado"
    elif tipo == "soldado":
        caixa(m, "CE chapa de espera (pilar)", xc - 0.08, xc + 0.08, -0.0125, 0.0, z_ap - 0.22, z_ap + 0.06, GE)
        for dz in (-0.15, 0.00):
            caixa(m, "CE pino Ø16", xc - 0.008, xc + 0.008, -0.16, -0.0125, z_ap + dz - 0.008, z_ap + dz + 0.008, GE)
        caixa(m, "SOLDA de campo (fora do padrão ND)", xc - c["b"] / 2 - 0.006, xc + c["b"] / 2 + 0.006, 0.0, 0.006, z_ap - 0.12, z_ap - 0.01, GP)
        nome = "CS console soldado"
    else:
        caixa(m, "CC console concretado — chapa embutida", xc - c["b"] / 2, xc + c["b"] / 2, -0.016, 0.0, z_ap - 0.19, z_ap + 0.03, GE)
        for dz in (-0.15, 0.00):
            caixa(m, "CC pino de ancoragem Ø16", xc - 0.008, xc + 0.008, -0.17, -0.016, z_ap + dz - 0.008, z_ap + dz + 0.008, GE)
        nome = "CC console concretado"
    y_fim = FOLGA + c["nariz"]                                        # ponta do braço dentro do nicho
    zt = z_ap - 0.035                                                 # topo do braço (35 mm de curso do parafuso superior)
    for sx in (-1, 1):
        caixa(m, f"{nome} — aba", xc + sx * (c["b"] / 2 - c["t_aba"]), xc + sx * c["b"] / 2, y_ini, y_fim, zt - c["h_braco"], zt, GP)
    caixa(m, f"{nome} — mesa", xc - c["b"] / 2, xc + c["b"] / 2, y_ini, y_fim, zt - 0.016, zt, GP)
    caixa(m, f"parafuso superior {c['paraf_sup']} (ajuste vertical)", xc - 0.010, xc + 0.010, y_fim - 0.035, y_fim - 0.015, zt, z_ap, GP)
    caixa(m, f"parafuso frontal {c['paraf_frontal']} (ajuste de profundidade)", xc - 0.008, xc + 0.008, y_fim, y_fim + 0.010, zt - 0.060, zt - 0.044, GP)
    return dict(y_fim=y_fim, x0=xc - c["b"] / 2, x1=xc + c["b"] / 2)


def verifica_nicho(nic, regs_placa):
    """Folgas reais do nicho: atrás (até a face externa), às cordoalhas, à ponta da placa."""
    a, b, ya, yb, z0 = regs_placa
    atras = yb - nic["y1"]
    folga_cord = min(min(abs(nic["z_a"] - (z0 + zc)), abs(nic["z_b"] - (z0 + zc))) - D_CORD / 2 for zc in Z_CORD)
    corta_cord = any(nic["z_a"] < z0 + zc < nic["z_b"] for zc in Z_CORD) and nic["y1"] > ya + Y_CORD - D_CORD / 2
    ponta = min(nic["x0"] - a, b - nic["x1"])
    return dict(prof_mm=round((nic["y1"] - nic["y0"]) * 1000), concreto_atras_mm=round(atras * 1000), folga_cordoalha_mm=round(folga_cord * 1000),
                corta_cordoalha=corta_cord, dist_ponta_placa_mm=round(ponta * 1000))


def montar():
    m = ModeloBIM("Letsara — estudo Trejor de fixação das placas 125 × 10", obra="Obra Letsara (Marques Engenharia e Construções)")
    R = {}
    for i, tipo in enumerate(("parafusado", "soldado", "concretado")):
        x0 = i * 4.5
        pilar(m, x0, f"S{i + 1} pilar")
        regs = placas(m, x0)
        res = []
        for reg in regs:
            a, b, ya, yb, z0 = reg
            xc = (b - 0.11) if b < x0 else (a + 0.11)                  # console no meio da sobreposição placa × pilar
            nic = nicho_face(m, xc, z0, ya)
            con = console_externo(m, xc, nic["z_b"] - DIM["nicho"]["t_apoio"], tipo)
            v = verifica_nicho(nic, reg)
            v.update(borda_pilar_mm=round((BP / 2 - abs(con["x1" if xc > x0 else "x0"] - x0)) * 1000) if True else None)
            res.append(v)
        R[f"S{i + 1} console {tipo}"] = res[0]
    # S4 console faca: placa entre pilares, faces alinhadas à face externa do pilar (y de −0,10 a 0)
    x0 = 3 * 4.5
    pilar(m, x0, "S4 pilar")
    yp = (-E, 0.0)
    regs = placas(m, x0, entre=True, y_placa=yp)
    fa, gv, nf = DIM["faca"], DIM["gaveta"], DIM["nicho_faca"]
    res = []
    for reg in regs:
        a, b, ya, yb, z0 = reg
        lado = 1 if a > x0 else -1
        xf = x0 + lado * BP / 2                                      # face lateral do pilar
        yc, zc = (ya + yb) / 2, z0 + DIM["nicho"]["z_centro"]
        # gaveta no pilar
        g0, g1 = xf - lado * gv["prof"], xf
        caixa(m, "GV gaveta pilar para faca", g0, g1, yc - gv["b"] / 2, yc + gv["b"] / 2, zc - gv["h"] / 2, zc - gv["h"] / 2 + gv["t"], GE)
        caixa(m, "GV gaveta pilar para faca", g0, g1, yc - gv["b"] / 2, yc - gv["b"] / 2 + gv["t"], zc - gv["h"] / 2, zc + gv["h"] / 2, GE)
        caixa(m, "GV gaveta pilar para faca", g0, g1, yc + gv["b"] / 2 - gv["t"], yc + gv["b"] / 2, zc - gv["h"] / 2, zc + gv["h"] / 2, GE)
        # faca
        f0, f1 = xf - lado * fa["na_gaveta"], xf + lado * (fa["abertura"] + fa["na_placa"])
        zf0 = zc - gv["h"] / 2 + gv["t"] + 0.006
        caixa(m, "CF console faca", f0, f1, yc - fa["t"] / 2, yc + fa["t"] / 2, zf0, zf0 + fa["h"], GP)
        caixa(m, "SH shims de nível (3 × 2 mm)", f0, f0 + lado * 0.08, yc - fa["t"] / 2, yc + fa["t"] / 2, zf0 - 0.006, zf0, GP)
        # nicho de topo na placa
        n0, n1 = (a if lado > 0 else b), (a if lado > 0 else b) + lado * nf["prof"]
        zna = zf0 + fa["h"] - nf["h"]
        nic = dict(x0=min(n0, n1), x1=max(n0, n1), y0=yc - nf["b"] / 2, y1=yc + nf["b"] / 2, z_a=zna, z_b=zna + nf["h"])
        for (u0, u1, v0, v1) in ((nic["y0"], nic["y0"] + nf["t"], 0, 1), (nic["y1"] - nf["t"], nic["y1"], 0, 1)):
            caixa(m, "NF nicho painel para faca", nic["x0"], nic["x1"], u0, u1, nic["z_a"], nic["z_b"], GE)
        caixa(m, "NF nicho painel para faca — chapa de apoio", nic["x0"], nic["x1"], nic["y0"], nic["y1"], zf0 + fa["h"], zf0 + fa["h"] + 0.0125, GE)
        parede = min(nic["y0"] - ya, yb - nic["y1"])
        folga_cord = min(min(abs(nic["z_a"] - (z0 + z)), abs(nic["z_b"] + 0.0125 - (z0 + z))) - D_CORD / 2 for z in Z_CORD)
        res.append(dict(prof_mm=round(nf["prof"] * 1000), parede_concreto_cada_lado_mm=round(parede * 1000),
                        folga_cordoalha_mm=round(folga_cord * 1000),
                        corta_cordoalha=any(nic["z_a"] < z0 + z < nic["z_b"] + 0.0125 for z in Z_CORD) and parede < Y_CORD + D_CORD / 2,
                        gaveta_ate_barra_canto_mm=round((abs(yp[1] - (yc + gv['b'] / 2)) - 0.03 - 0.01 - 0.008) * 1000)))
    R["S4 console faca"] = res[0]
    m.pendente("Estudo Trejor: dimensões de pré-dimensionamento (DIM) — confirmar com o catálogo/desenhos da Trejor (TSA, console, nicho, faca, gaveta).")
    return m, R


if __name__ == "__main__":
    saida = Path(sys.argv[1] if len(sys.argv) > 1 else AQ / "saidas")
    saida.mkdir(parents=True, exist_ok=True)
    m, R = montar()
    gravar_ifc(m, saida / "estudo_trejor.ifc")
    out = dict(placa=dict(e_mm=E * 1000, cordoalhas="8 Ø12,7, eixo a 26,4 mm das faces", z_cordoalhas_m=Z_CORD, cobrimento_mm=COB * 1000),
               dim_predimensionamento=DIM, conferencia=R)
    (AQ / "estudo_trejor.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(R, indent=1, ensure_ascii=False))
