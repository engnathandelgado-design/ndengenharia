"""Letsara — modelo BIM (IFC + página 3D) a partir das definições de projeto. Revisão de 12/10/2026 (tarde).

Rodar: PYTHONPATH=. python exemplos/letsara/modelo_bim.py [pasta_de_saida]
Saída (em saidas/, fora do git): letsara.ifc e letsara_3d.html (publicar a página como artefato para ver no celular).

Geometria = a mesma da checagem de ligações (ligacoes.json) e do modelo global:
- eixos Y (linhas 1 a 9) e X (A a E) do R01 como usados nos cálculos;
- rev03 (14/10/2026): cobertura rebaixada (TP40 + lã 40 + zipada + painéis solares) com ≥ 15 cm de folga à platibanda (+10,00);
- TS-01 sem dentes, apoiada no recuo dos pilares laterais e no topo da I120 / pilares centrais (neoprene + 2 pinos);
- vigas centrais I120 (h 1,30) com dente 78 × 35 nos consolos CP-I120;
- terças Z 302×90/82×2,30 METSEC c/1,20 m contínuas por transpasse (rev05: peças com o polígono real, transpasse, ST-1P/ST-1V
  e parafusos M12 do apoio e da emenda; sem mão-francesa), ligações todas parafusadas (sem solda); mezanino com laje alveolar h20 + 5 sobre vigas I90.
- rev04 (16/10/2026, NBR 9062): sem VT; VM em meio vaso com dente Gerber, 2º estágio e alças; folgas reais; consolos com fundo alinhado.
Unidades: m.
"""
import itertools
import json
import math
import sys
from pathlib import Path

from nd_estruturas.bim import (ModeloBIM, PerfilI, PerfilRetangular, PerfilPoligono, Peca, gravar_ifc, gravar_visualizador,
                               ler_malha_ifc, quantitativos)
import acabamentos_cob as AC

AQ = Path(__file__).parent
LG = json.loads((AQ / "ligacoes.json").read_text(encoding="utf-8"))

# ------------------------------------------------------------------ parâmetros da obra (iguais aos cálculos)
from geometria import Y_PG, Z_PISO_PRONTO, Y_LIN, X_FACH, X_EIXO, Y_P13, Y_PC_C, X_L2, X_L4, LINHA_PORTOES, Z_PISOS, P6_ESC, P7_ESC, P6_L2, ABERTURA, ESCADA, y_vb, y_canto, y_canto_int, PG_L4, DY_CANTO, Y_VM1
LARG = X_EIXO["E"]
COMP = Y_LIN[-1]
X_C = X_EIXO["C"]
REC = tuple(LG["REC"])                             # recuo = assento da TS-01 (rev03)
TOPO_PLAT, Z_CALICE = 10.00, -1.00
INCL = 0.03
Z0 = LG["Z0_TS"]                                   # fundo da TS-01 no eixo A
C3 = math.cos(math.atan(INCL))
zf = lambda x: Z0 + INCL * x                       # fundo (altura cheia) da TS-01 em x
H_TS = 0.90
L_TS = LG["L_TS"] * C3                             # projeção horizontal entre pontas
X0P = LG["X_PONTA_ESQ"]
PONTAS = [(X0P, X0P + L_TS), (LARG - X0P - L_TS, LARG - X0P)]
Z_I120_TOPO, H_I120 = LG["Z_TOPO_I120"], LG["H_I120"]
CENTRAIS = [("P8A", Y_LIN[1]), ("P11", Y_LIN[3]), ("P13", Y_PC_C[0]), ("P13B", Y_PC_C[1])]          # DEC-058: dois PC-03 40×40
I120_TRECHOS = [("V407", Y_LIN[1], Y_LIN[3]), ("V406", Y_LIN[3], Y_PC_C[0]), ("V405", Y_PC_C[0], Y_PC_C[1]), ("V404", Y_PC_C[1], Y_LIN[8])]   # V404 vai até a linha 9 (P14)
NIVEIS_MEZ, H_LAJE = list(Z_PISOS), 0.20 + 0.05          # rev09 (DEC-045): topo da capa +3,90 / +7,30

I90 = PerfilI(h=0.90, b=0.40, tw=0.15, tf=0.15, nome="I90")
I120 = PerfilI(h=LG["H_I120"], b=0.40, tw=0.15, tf=0.25, nome="I120")       # DEC-054: h 1,20
I70 = PerfilI(h=0.70, b=0.40, tw=0.15, tf=0.15, nome="I70")
VB = PerfilRetangular(0.15, 0.60, "VB 15x60")
VB_N = PerfilRetangular(0.15, 0.30, "VB nariz do dente")
TERCA = PerfilRetangular(0.172, 0.302, "Z302 (envelope)")
PARAF = PerfilRetangular(0.012, 0.012, "M12 8.8")
LAJE = PerfilRetangular(1.24, H_LAJE, "LA h20+5")
TELHA = PerfilRetangular(1.00, sum(LG["platibanda"]["pacote"].values()), "TP40 + lã 40 + zipada + painéis solares")
H_PLACA, E_PLACA, N_FIADAS = 1.25, 0.10, 8
PLACA = PerfilRetangular(E_PLACA, H_PLACA, "Placa e=10 h=125")


CONS = json.loads((AQ / "consolos.json").read_text(encoding="utf-8"))
I1J = json.loads((AQ / "i110_r01.json").read_text(encoding="utf-8"))               # rev06 (DEC-032): arranjo das cordoalhas da I120
GD_ = json.loads((AQ / "dentes.json").read_text(encoding="utf-8"))["I120"]["geometria"]
hC = lambda t: CONS[t]["h_total_m"]
sys.path.insert(0, "/home/claude/letsara/pranchas")
import fechamento as FCH
import geo_fixacao as GF
import numpy as np
from lajes_placas import paineis_mez, paineis_nivel
PAINEIS_MEZ = paineis_mez()[0]
# rev09b (DEC-050): cabeça de concreto dos pilares da linha 2 sobe até o fundo da W da linha 2 (sem montantes)
Z_L2 = {a["nome"]: a["z_concreto"] for a in json.loads((AQ / "cob_linha2.json").read_text(encoding="utf-8"))["apoios_diretos"]}                                                   # placas: mesma fonte das pranchas PP (vistas do R01)



# ------------------------------------------------------------------ peças metálicas como executadas (rev06: iguais às pranchas)
GM, GE, GP = "Ligações da cobertura", "Esperas e insertos embutidos", "Fixação das placas"


def caixa(m, marca, x0, x1, y0, y1, z0, z1, grupo, obs=""):
    """Chapa / barra como prisma alinhado aos eixos (aço)."""
    xa, xb, ya, yb, za, zb = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1)
    if zb - za < 1e-4 or xb - xa < 1e-4 or yb - ya < 1e-4:
        return None
    return m.linear("inserto", marca, PerfilRetangular(round(xb - xa, 5), round(yb - ya, 5)), ((xa + xb) / 2, (ya + yb) / 2, za),
                    ((xa + xb) / 2, (ya + yb) / 2, zb), grupo, cima=(0.0, 1.0, 0.0), material="aco", obs=obs)


def barra_v(m, marca, x, y, z0, z1, d, grupo):
    return caixa(m, marca, x - d / 2, x + d / 2, y - d / 2, y + d / 2, z0, z1, grupo)


def espera(m, marca, x, y, zc, d, hef, sai, grupo=GE, grampo=False, porcas=True):
    """Barra roscada com gancho embutida (hef) + saliência; porca de nivelamento, porca e contraporca; grampo U Ø10 opcional."""
    barra_v(m, marca, x, y, zc - hef, zc + sai, d, grupo)
    caixa(m, marca + " (gancho)", x, x + 0.060, y - d / 2, y + d / 2, zc - hef, zc - hef + d, grupo)
    if porcas:
        for z_ in (zc + 0.0095, zc + 0.0095 + 0.014):
            caixa(m, f"porca M{d*1000:.0f}", x - 0.6 * d - 0.004, x + 0.6 * d + 0.004, y - 0.6 * d - 0.004, y + 0.6 * d + 0.004, z_, z_ + 0.014, GM)
    if grampo:
        for dx in (-0.045, 0.045):
            barra_v(m, "grampo U Ø10", x + dx, y, zc - 0.20, zc - 0.03, 0.010, grupo)
        caixa(m, "grampo U Ø10", x - 0.045, x + 0.045, y - 0.005, y + 0.005, zc - 0.20, zc - 0.19, grupo)


def suporte_st(m, marca, xw, y, zc, lado=-1, esperas=(), d=0.016, hef=0.150, grampo=False, aba=0.150, dy_ch=0.0):
    """ST-1P / ST-1V / ST-1V-R / ST-1F: chapa dobrada 9,5 × 220 — aba vertical 290 contra a alma da terça (lado `lado` da
    alma) e aba horizontal 150 sobre o concreto, presa em `esperas` (x, y relativos à alma e ao eixo do apoio)."""
    t = 0.0095
    yc = y + dy_ch                                  # rev12: ST-1V/ST-1V-R com a borda rente à ponta da terça (VB rente à face, placa a 15 mm)
    caixa(m, marca, xw, xw + lado * t, yc - 0.11, yc + 0.11, zc, zc + 0.290, GM, obs="chapa dobrada 9,5 × 220 A36 galv., aba vertical 290")
    caixa(m, marca, xw + lado * t, xw + lado * aba, yc - 0.11, yc + 0.11, zc, zc + t, GM, obs=f"aba horizontal {aba*1000:.0f}, oblongos")
    for dx, dy in esperas:
        espera(m, marca.split()[0].replace("ST-1P4", "ES-1").replace("ST-1P", "ES-1").replace("ST-1V-R", "ES-1R").replace("ST-1V", "ES-1V").replace("ST-1F", "ES-1F"),
               xw + dx, y + dy, zc, d, hef, 0.12 if d < 0.02 else 0.12, grampo=grampo)


def suporte_fl(m, marca, xw, y_face, sy, zc):
    """ST-1FL (DEC-042): chapa dobrada 9,5 × 290 — aba de 190 encostada na face lateral do pilar de canto (plano y = y_face,
    normal sy), presa por 2 ES-1FL M20 horizontais (hef 150 + grampo U Ø10) a 70 e 150 mm da face A; aba de 100 contra a
    alma da terça (lado −x), 2 M12 8.8. A terça termina 10 mm antes da face."""
    t, LARG_ = 0.0095, xw + 0.3065
    x0, x1 = xw - t, LARG_ - 0.30 + 0.175                    # aba na face: da alma até 2,5 cm além da 2ª espera
    caixa(m, marca, x0, x1, y_face, y_face + sy * t, zc, zc + 0.290, GM, obs="chapa dobrada 9,5 × 290 A36 galv., aba 190 na face lateral, 2 furos Ø22")
    ya, yb = sorted((y_face + sy * t, y_face + sy * 0.100))
    caixa(m, marca, xw - t, xw, ya, yb, zc, zc + 0.290, GM, obs="aba 100 contra a alma da terça, 2 furos Ø14 (M12)")
    zm = zc + 0.145
    for xe in (LARG_ - 0.30 + 0.070, LARG_ - 0.30 + 0.150):
        m.linear("inserto", "ES-1FL barra roscada M20 A36 L=400 (horizontal)", PerfilRetangular(0.020, 0.020, "M20"),
                 (xe, y_face - sy * 0.320, zm), (xe, y_face + sy * 0.080, zm), GE, material="aco",
                 obs="hef 150 + grampo U Ø10; 80 mm saliente (arruela + porca + contraporca)")
        caixa(m, "grampo U Ø10", xe - 0.045, xe + 0.045, *sorted((y_face - sy * 0.13, y_face - sy * 0.14)), zm - 0.005, zm + 0.005, GE)
        caixa(m, "porca M20", xe - 0.016, xe + 0.016, *sorted((y_face + sy * t, y_face + sy * (t + 0.018))), zm - 0.016, zm + 0.016, GM)


def orelha(m, x, y, zc, ux, uy, h_furo):
    """OR-X L 102×76×6,3 L = 80 girada ⊥ ao tirante (direção ux, uy saindo do nó), na espera ES-2 a 45 mm atrás."""
    px, py = -uy, ux
    w = 0.040
    a, b = (x + px * w, y + py * w, zc), (x - px * w, y - py * w, zc)
    m.linear("inserto", "OR-X L 102×76×6,3 L=80", PerfilRetangular(0.0063, 0.102, "aba 102"), (a[0], a[1], zc + 0.051), (b[0], b[1], zc + 0.051), GM,
             cima=(0, 0, 1), material="aco", obs=f"furo Ø18 a {h_furo*1000:.0f} do concreto")
    cx, cy = x - ux * 0.038, y - uy * 0.038
    m.linear("inserto", "OR-X L 102×76×6,3 L=80", PerfilRetangular(0.076, 0.0063, "aba 76"), (cx + px * w, cy + py * w, zc + 0.00315),
             (cx - px * w, cy - py * w, zc + 0.00315), GM, cima=(0, 0, 1), material="aco")
    espera(m, "ES-2", x - ux * 0.045, y - uy * 0.045, zc, 0.016, 0.110, 0.05, grampo=True, porcas=False)
    caixa(m, "porca M16", x - ux * 0.045 - 0.014, x - ux * 0.045 + 0.014, y - uy * 0.045 - 0.014, y - uy * 0.045 + 0.014, zc + 0.0063, zc + 0.0203, GM)


def montar() -> ModeloBIM:
    m = ModeloBIM("Letsara — Pavilhão pré-moldado", obra="Obra Letsara (Marques Engenharia e Construções)")
    ass_ts = lambda x_pino: zf(x_pino) + H_DENTE * C3 - 0.01               # topo do consolo que recebe a TS-01
    z_vb = lambda x: zf(x) + 0.30                                           # rev04: fundo da VB 15×60 (topo = zf + 0,90, linha das terças)
    rec_vb = lambda x: math.ceil((z_vb(x) + 0.60) / 0.05) * 0.05           # recuo da cabeça dos pilares de fachada: topo da VB

    # 1. pilares laterais (60 em x) com cabeça recuada 40×30 e consolos CP-TS (fundo alinhado ao da TS-01)
    for i, y in enumerate(Y_LIN, start=1):
        canto = i in (1, 9)
        for lado, x0, sg in (("P1", 0.0, 1), ("P2", LARG, -1)):
            zr = rec_vb(x0) if canto else (Z_L2["A" if sg > 0 else "E"] if i == 2 else REC[0 if sg > 0 else 1])   # rev09b: linha 2 = fundo da W
            nome = f"{lado}{'C' if canto else ''}-L{i}"
            if canto:      # DEC-042 (decisão do Nathan, 22/10): canto SEM platibanda recuada — seção cheia 40×60 até o topo
                # rev12 (27/10, opção D): eixo 10 cm para fora da linha → face externa = face dos PF
                m.pilar(nome, x0, y_canto(y), 0.60, 0.40, Z_CALICE, TOPO_PLAT,
                        obs=f"40×60, seção cheia até o topo (sem platibanda recuada; DEC-042); eixo {DY_CANTO*100:.0f} cm para fora da linha {i} (face externa = face dos PF)")
                continue
            m.pilar(nome, x0, y, 0.60, 0.40, Z_CALICE, zr, obs=f"40×60; cabeça recuada acima de +{zr:.2f}".replace(".", ","))
            m.pilar(nome + " cabeça", x0 - sg * 0.15, y, 0.30, 0.40, zr, TOPO_PLAT, obs="cabeça recuada 40×30")
    # pilares das fachadas 1 e 9 (60 ⊥ fachada) com cabeça recuada acima da VB
    for j, x in enumerate(X_FACH[1:-1]):
        for nome, y, sg in ((["P3", "P4", "P5"][j], 0.0, 1), (["P3", "P14", "P5"][j], COMP, -1)):
            zr = rec_vb(x)
            m.pilar(f"{nome}-L{1 if sg > 0 else 9}", x, y, 0.40, 0.60, Z_CALICE, zr, obs="60 ⊥ fachada; cabeça recuada acima da VB")
            m.pilar(f"{nome}-L{1 if sg > 0 else 9} cabeça", x, y - sg * 0.15, 0.40, 0.30, zr, TOPO_PLAT, obs="cabeça 40×30")
    # centrais: P8A 40×60, P11 40×40, P13 e P13B 40×40 (DEC-058) — topo = topo da I120
    for (marca, y), (bx, by) in zip(CENTRAIS, ((0.40, 0.60), (0.40, 0.40), (0.40, 0.40), (0.40, 0.40))):
        zt_c = Z_L2["C"] if marca == "P8A" else Z_I120_TOPO             # rev09b: P8A sobe até o fundo da W da linha 2 da linha 2
        m.pilar(marca, X_C, y, bx, by, Z_CALICE, zt_c, obs=(f"{bx*100:.0f}×{by*100:.0f}; apoio I120 / TS-01; topo em 2 níveis" if marca == "P11" else f"{bx*100:.0f}×{by*100:.0f}; PC-03, apoio das I120 (DEC-058)") if marca != "P8A" else
                f"{bx*100:.0f}×{by*100:.0f}; CP-I120 da V400; topo +{zt_c:.3f} = fundo da W da linha 2 − 40 mm (DEC-050)".replace(".", ","))
        if marca == "P11":                                     # rev04: metade do lado E 12 mm mais alta (assentos das TS-01); rev09: P8A sem TS-01
            m.bloco("pilar", f"{marca} degrau do topo", (X_C + bx / 4, y, LG["Z_TOPO_I120_DIR"]), bx / 2, by, LG["DEGRAU_C"], "Pilares")
    for marca, x, ap in (("P8", X_EIXO["B"], "B"), ("P8B", X_EIXO["D"], "D")):
        m.pilar(marca, x, Y_LIN[1], 0.40, 0.60, Z_CALICE, Z_L2[ap], obs=f"mezanino 40×60; cabeça até +{Z_L2[ap]:.3f} = fundo da W da linha 2 − 40 mm (DEC-050)".replace(".", ","))
    # rev09 (DEC-045): pilares da escada do R01 — P6 25×40 e P7 40×60 até o +3,90 (viga P6–P7); P6 da linha 2 até o +7,30
    m.pilar("P6", P6_ESC[0], P6_ESC[1], 0.25, 0.40, Z_CALICE, NIVEIS_MEZ[0], obs="25×40, escada: viga P6–P7 no +3,90 e patamar +1,95")
    m.pilar("P7", P7_ESC[0], P7_ESC[1], 0.60, 0.40, Z_CALICE, NIVEIS_MEZ[0], obs="40×60 no eixo E, escada: viga P6–P7 no +3,90 e patamar +1,95")
    m.pilar("P6 (linha 2)", P6_L2[0], P6_L2[1], 0.25, 0.40, Z_CALICE, Z_L2["P6"], obs=f"25×40, linha 2: vigas D–P6 e P6–E; cabeça até +{Z_L2['P6']:.3f} = fundo da W da linha 2 − 40 mm (DEC-050)".replace(".", ","))
    # pilares dos portões (linha 4), rev06 (DEC-024): cabeça a 2 cm do fundo da TS-01, ligada em y por 2 cantoneiras CL-P
    # rev12 (27/10): PG-02/PG-04 25×40 (40 em x, ao longo da parede), eixo 7,5 cm para longe do portão (5,00 m livres)
    # rev12 (DEC-092): PG-02/PG-04 com o eixo 7,5 cm fora da linha 4 (face −y no plano dos vizinhos 40×40, sem fresta até as placas)
    _PJn = json.loads((AQ / "portao_l4.json").read_text(encoding="utf-8"))["neoprene"]
    for mk_pg, nome, x, b_, by_ in [(mk, f"{r01} ({mk})", x_, bx_, by_) for mk, (r01, x_, bx_, by_) in PG_L4.items()]:
        zt_ = round(zf(x) - 0.02, 2)
        ypg = Y_PG[mk_pg]
        m.pilar(nome, x, ypg, b_, by_, Z_CALICE, zt_, obs=f"parede dos portões (vista C), {by_*100:.0f}×{b_*100:.0f}, topo +{zt_:.2f}; portão livre até +7,50" + (f"; eixo y {ypg:.3f} (face no plano dos vizinhos 40×40)" if ypg != Y_LIN[LINHA_PORTOES] else ""))
        yl4 = Y_LIN[LINHA_PORTOES]                                           # eixo da TS-01A (CL-P e IT-P centrados na viga)
        for sx in (-1, 1):
            xf_ = x + sx * b_ / 2
            zcl = zf(min(xf_, xf_ + sx * 0.102))              # 22/10: aba encostada no fundo da TS-01A no ponto mais baixo (3 %)
            caixa(m, "CL-P L 102×102×9,5 L=250", xf_, xf_ + sx * 0.0095, yl4 - 0.125, yl4 + 0.125, zcl - 0.102, zcl, GM, obs="aba no pilar, 1 M16 em oblongo vertical")
            caixa(m, "CL-P L 102×102×9,5 L=250", xf_, xf_ + sx * 0.102, yl4 - 0.125, yl4 + 0.125, zcl - 0.0095, zcl, GM, obs="aba sob a TS-01A, 2 M16 nos IT-P")
            m.linear("inserto", "M16 8.8 (IL-1)", PerfilRetangular(0.016, 0.016), (xf_ - sx * 0.10, ypg, zf(x) - 0.06), (xf_ + sx * 0.03, ypg, zf(x) - 0.06), GM, material="aco")   # IL-1 no eixo do pilar
            for dy in (-0.0975, 0.0975):
                barra_v(m, "M16 8.8 + IT-P (fundo da TS-01A)", xf_ + sx * 0.06, yl4 + dy, zf(x) - 0.03, zf(x) + 0.08, 0.016, GM)
        # DEC-059 (24/10, opção A do Nathan): a cabeça do PG passa a APOIAR a TS-01A — neoprene NEO-7 colado na cabeça + graute
        # injetado entre o neoprene e o fundo da viga depois da montagem (a viga não desce no vão dos portões: fundo ≥ +7,50)
        _zt = zf(x - b_ / 2)
        _nx, _ny = _PJn[mk_pg]["nx_mm"] / 1000, _PJn[mk_pg]["ny_mm"] / 1000      # rev12: a0 ≥ 4,5 cm das bordas (NBR 9062:2017 7.2)
        m.bloco("inserto", f"{'NEO-7' if b_ == by_ else 'NEO-7A'} neoprene {_PJn[mk_pg]['dim_mm'].replace(' ', '')} + graute 10 mm (apoio da TS-01A, DEC-059), centrado no pilar", (x, ypg, _zt - 0.001), _nx, _ny, 0.019, "Pinos, tubos e neoprenes")

    # 2. vigas centrais I120 (comprimentos do R01) e consolos CP-I120 / CV-TS
    zc = Z_I120_TOPO - H_I120 / 2
    meia = {Y_LIN[1]: 0.30, Y_LIN[3]: 0.20, Y_PC_C[0]: 0.20, Y_PC_C[1]: 0.20, Y_LIN[8]: 0.30}
    z_ass_i110 = LG["Z_ASS_I120"]
    for marca, ya, yb in I120_TRECHOS:
        y0, y1 = ya + meia[ya] + 0.075, yb - meia[yb] - 0.075
        arr = I1J[marca]["arranjo"]
        ob_ = (f"h {H_I120:.2f}; L = {y1 - y0:.3f} m; protendida {arr['n_cord']} cord. {arr.get('cordoalha', 'Ø12.7').replace('.', ',')} ({arr['n_inf']} embaixo + {arr['n_cord'] - arr['n_inf']} na mesa superior), "
               f"σpi {I1J[marca]['perdas'].get('sig_pi', 1453):.0f} MPa, fckj {arr['fckj']:g}, protensão limitada; dente {GD_['hd']} × {GD_['ln']}, maciço {GD_['x_mac'] / 1000:.2f} m (DEC-054)")
        ln_, mac_, hd_ = GD_["ln"] / 1000, GD_["x_mac"] / 1000, GD_["hd"] / 1000
        m.linear("viga", marca, I120, (X_C, y0 + mac_, zc), (X_C, y1 - mac_, zc), "Vigas centrais I120", obs=ob_)
        for ya_, yb_ in ((y0, y0 + mac_), (y1 - mac_, y1)):
            ys_ = (ya_ + ln_, yb_) if ya_ == y0 else (ya_, yb_ - ln_)
            m.linear("viga", f"{marca} ponta maciça", PerfilRetangular(0.40, H_I120), (X_C, ys_[0], zc), (X_C, ys_[1], zc), "Vigas centrais I120", obs=ob_)
            yn_ = (y0, y0 + ln_) if ya_ == y0 else (y1 - ln_, y1)
            m.linear("viga", f"{marca} nariz do dente", PerfilRetangular(0.40, hd_), (X_C, yn_[0], Z_I120_TOPO - hd_ / 2), (X_C, yn_[1], Z_I120_TOPO - hd_ / 2),
                     "Vigas centrais I120", obs=ob_)
        m.linear("viga", f"{marca} degrau do topo", PerfilRetangular(0.20, LG["DEGRAU_C"]), (X_C + 0.10, y0, Z_I120_TOPO + LG["DEGRAU_C"] / 2), (X_C + 0.10, y1, Z_I120_TOPO + LG["DEGRAU_C"] / 2),
                 "Vigas centrais I120", obs="rev04: topo em 2 níveis — metade do lado E 12 mm acima (apoio horizontal das TS-01)")
        for yy, sg in ((ya, 1), (yb, -1)):
            # DEC-054: CP-I120 com mísula — 49 junto à face do pilar, 39 na ponta (fundo inclinado), extrudado em x
            _hf, _hp, _pj = hC("CP-I120"), CONS["CP-I120"]["h_consolo_m"], CONS["CP-I120"]["proj_m"]
            _yf = yy + sg * meia[yy]
            _pts = [(0.0, 0.0), (sg * _pj, 0.0), (sg * _pj, -_hp), (0.0, -_hf)]
            if sg < 0:
                _pts = _pts[::-1]
            from nd_estruturas.bim import Peca as _Peca, PerfilPoligono as _PP
            m.add(_Peca("consolo", "Consolos", f"CP-I120 {marca}", _PP(tuple(_pts), "CP-I120 com mísula"), (X_C - CONS["CP-I120"]["b_m"] / 2, _yf, z_ass_i110), (X_C + CONS["CP-I120"]["b_m"] / 2, _yf, z_ass_i110), (0.0, 0.0, 1.0), "concreto",
                        f"b {CONS['CP-I120']['b_m']*100:.0f} (largura da I120); 49 junto ao pilar / 39 na ponta (mísula, DEC-054)"))
            m.bloco("inserto", "NEO-2 300×200×31 fretado", (X_C, yy + sg * (meia[yy] + 0.20), z_ass_i110 + 0.031), 0.30, 0.20, 0.031, "Pinos, tubos e neoprenes")
            m.bloco("inserto", "PN-2 pino Ø25 L=900 (350 no consolo; grauteado numa ponta só)", (X_C, yy + sg * (meia[yy] + 0.20), z_ass_i110 + 0.55), 0.025, 0.025, 0.90,
                    "Pinos, tubos e neoprenes")

    # 3. TS-01: I90 inclinada, sem dentes (rev03)
    # rev04: elevação real na posição montada — pontas a prumo, cunhas de 30 cm no fundo das pontas (face de apoio horizontal,
    # NBR 9062:2017 7.2.1.6), mesas, alma e maciços de 50 cm; ponta baixa sempre no lado A (as 14 peças são a mesma marca)
    CUN, HV, TI, TSUP, MAC = LG["CUNHA"], H_TS / C3, 0.15, 0.12, 0.50
    zt = lambda x: zf(x) + HV
    for i in range(3, 9):                                  # rev09 (DEC-048): linha 2 com cobertura metálica (abaixo)
        y = Y_LIN[i - 1]
        for lado, (xa, xb) in zip("ab", PONTAS):
            ob = f"inclinada 3 %, pontas a prumo, cunhas de apoio {CUN*100:.0f} cm; L {LG['L_TS']:.2f} m; 8 cord. Ø12,7"
            za, zb_ = zf(xa + CUN), zf(xb)
            m.extrusao_y("viga", f"TS-01 L{i}{lado} maciço A", [(xa, za), (xa + CUN, za), (xa + MAC, zf(xa + MAC)), (xa + MAC, zt(xa + MAC)), (xa, zt(xa))],
                         y, 0.40, "Vigas I90 de cobertura", obs=ob)
            m.extrusao_y("viga", f"TS-01 L{i}{lado} maciço E", [(xb - MAC, zf(xb - MAC)), (xb - CUN, zf(xb - CUN)), (xb - CUN, zb_), (xb, zb_), (xb, zt(xb)), (xb - MAC, zt(xb - MAC))],
                         y, 0.40, "Vigas I90 de cobertura", obs=ob)
            x0, x1 = xa + MAC, xb - MAC
            m.extrusao_y("viga", f"TS-01 L{i}{lado} mesa inf.", [(x0, zf(x0)), (x1, zf(x1)), (x1, zf(x1) + TI), (x0, zf(x0) + TI)], y, 0.40, "Vigas I90 de cobertura", obs=ob)
            m.extrusao_y("viga", f"TS-01 L{i}{lado} alma", [(x0, zf(x0) + TI), (x1, zf(x1) + TI), (x1, zt(x1) - TSUP), (x0, zt(x0) - TSUP)], y, 0.15, "Vigas I90 de cobertura", obs=ob)
            m.extrusao_y("viga", f"TS-01 L{i}{lado} mesa sup.", [(x0, zt(x0) - TSUP), (x1, zt(x1) - TSUP), (x1, zt(x1)), (x0, zt(x0))], y, 0.40, "Vigas I90 de cobertura", obs=ob)

    # vigas de borda VB 15×60 das fachadas 1 e 9, rev04: dente Gerber 30 × 27 nas pontas sobre o CP-VB 15 × 27 × 29 escondido
    #   (fundo do consolo = fundo da VB); NEO-6 100×100×10 e PN-6 Ø20 roscado com porca (anti-levantamento); folga 2,5 cm
    LNV = 0.27
    sys.path.insert(0, str(AQ / "pranchas"))
    import vb_geom as VG
    for y in (0.0, COMP):
        for xa, xb in itertools.pairwise(X_FACH):
            fa, fb = xa + (0.30 if xa == 0 else 0.20), xb - (0.30 if xb == LARG else 0.20)       # faces dos pilares
            a, b = fa + 0.025, fb - 0.025
            Lh = round((b - a) * 1000)
            yv = y_vb((xa + xb) / 2, y)                                                # rev12: VB rente à face externa nos vãos entre PF
            cont = [(a + u / 1000, z_vb(a) + v / 1000) for u, v in VG.montada(Lh)]       # pontas, recortes e tubos a prumo; dentes horizontais
            m.extrusao_y("viga", "VB", cont, yv, 0.15, "Vigas de borda", obs=f"15×60 com dente 30 × 27, L = {b - a:.3f} m; caimento 3 %, faces de apoio horizontais"
                         + ("; rente à face externa dos pilares (fresta 2,5 cm até a placa)" if yv != y else ""))
            for xf, sg in ((fa, 1), (fb, -1)):
                xb_ = xf + sg * 0.135                                                   # centro do apoio
                zt = z_vb(xb_) + 0.29                                                   # topo HORIZONTAL do CP-VB = face do dente − neoprene
                m.bloco("consolo", "CP-VB 15×27×29" + (" rente à face externa (fachada)" if yv != y else ""), (xf + sg * 0.135, yv, zt), 0.27, 0.15, 0.29, "Consolos")
                m.bloco("inserto", "NEO-6 100×60×10", (xb_, yv, zt + 0.01), 0.10, CONS["CP-VB"]["neoprene_mm"][0] / 1000, 0.01, "Pinos, tubos e neoprenes")
                m.bloco("inserto", "PN-6 Ø20 roscado + porca e contraporca (nicho grauteado só numa ponta; a outra livre)",
                        (xb_, yv, zt + 0.01 + 0.30 - 0.03), 0.02, 0.02, 0.58, "Pinos, tubos e neoprenes")

    # 4. terças Z 302 METSEC contínuas por transpasse (METLAP), ST-1V nas VB, parafusos do apoio e da emenda; e telha
    from shapely.geometry import LineString
    CBM_ = json.loads((AQ / "cobertura_metalica.json").read_text(encoding="utf-8"))
    PC_ = CBM_["pecas"]
    A_TR, EXT_F, B_TR = PC_["transpasse_cada_lado_mm"] / 1000, PC_["extensao_fachada_mm"] / 1000, PC_["furos_transpasse_da_ponta_mm"] / 1000
    ZF1, ZF2 = PC_["furos_z_mm"][0] / 1000, PC_["furos_z_mm"][1] / 1000
    t_z, c45 = 0.0023, math.cos(math.radians(45))

    def z_contorno(xw, z0):
        cl = [(xw + 0.082 - 0.021 * c45, z0 + 0.021 * c45), (xw + 0.082, z0), (xw, z0), (xw, z0 + 0.302), (xw - 0.090, z0 + 0.302),
              (xw - 0.090 + 0.019 * c45, z0 + 0.302 - 0.019 * c45)]
        pol = LineString(cl).buffer(t_z / 2, cap_style=2, join_style=2).simplify(0.0002)
        return [(round(x_, 5), round(z_, 5)) for x_, z_ in list(pol.exterior.coords)[:-1]]

    n_v = len(Y_LIN) - 1
    for xa, _ in PONTAS:
        for s in LG["s_tercas"]:
            xw = xa + s * C3 - 0.027                                 # alma da terça na face +x do ST-1P (linha das terças)
            zb = zf(xw) + H_TS + 0.010                               # fundo da terça
            ult_E = xw > LARG - 0.325 - 0.04                         # DEC-042: última terça do lado E encosta na face lateral do canto (seção cheia)
            for k in range(n_v):
                e0 = EXT_F if k == 0 else A_TR
                e1 = EXT_F if k == n_v - 1 else A_TR
                dk = t_z if k % 2 else 0.0                           # vãos alternados: perfil encaixado por fora no transpasse
                ya, yb = Y_LIN[k] - e0, Y_LIN[k + 1] + e1
                if k == 0:
                    ya = y_vb(xw, Y_LIN[0]) - e0                         # rev12: VB rente à face dos PF (faixa B–D)
                if k == n_v - 1:
                    yb = y_vb(xw, Y_LIN[-1]) + e1
                if ult_E and k == 0:
                    ya = y_canto_int(Y_LIN[0]) + 0.01                    # rev12 (opção D): face interna do canto deslocado
                if ult_E and k == n_v - 1:
                    yb = y_canto_int(Y_LIN[-1]) - 0.01
                pk = next(p_ for p_ in ((PC_.get("por_vao_faixa_pf", []) if not ult_E else PC_.get("por_vao_canto_fl", [])) if k in (0, n_v - 1) else [])
                           + PC_["por_vao"] if p_["vao"] == f"{k+1}-{k+2}")
                m.extrusao_y("terca", f"Z302 vão {k+1}-{k+2} L={pk['L_mm']}", z_contorno(xw + dk, zb + dk), (ya + yb) / 2, yb - ya,
                             "Terças metálicas", material="aco", obs="Z 302×90/82×2,30 METSEC, contínua por transpasse")
            for j, yl in enumerate(Y_LIN):
                if j in (0, n_v):
                    yl = y_vb(xw, yl)                                    # rev12: apoio no eixo da VB deslocada
                ys = (-0.06, 0.06) if j in (0, n_v) else (-0.06, 0.06, -(A_TR - B_TR), A_TR - B_TR)
                if ult_E and j in (0, n_v):
                    ys = ((y_canto_int(Y_LIN[0]) + 0.06 if j == 0 else y_canto_int(Y_LIN[-1]) - 0.06) - yl,)   # M12 da aba do ST-1FL, fora do pilar
                for dy in ys:
                    for zz in (ZF1, ZF2):
                        m.linear("inserto", "M12 8.8 (apoio/emenda da terça)", PARAF, (xw - 0.012, yl + dy, zb + zz), (xw + 0.016, yl + dy, zb + zz),
                                 "Parafusos da cobertura", material="aco")
                if j in (0, n_v):
                    zc = zb - 0.010
                    if ult_E:                                        # DEC-042: ST-1FL na face lateral do canto, 2 ES-1FL M20 horizontais (padrão Mitsubishi)
                        suporte_fl(m, f"ST-1FL (pilar de canto, eixo {j+1})", xw, y_canto_int(Y_LIN[j]), 1 if j == 0 else -1, zc)
                    elif j == n_v:                                   # eixo 9: ST-1V-R, 2 M20 hef 400 + grampo
                        suporte_st(m, "ST-1V-R (VB eixo 9)", xw, yl, zc, esperas=((-0.045, 0.0), (-0.105, 0.0)), d=0.020, hef=0.400, grampo=True,
                                   dy_ch=-(0.110 - EXT_F))
                    else:
                        suporte_st(m, "ST-1V (VB eixo 1)", xw, yl, zc, esperas=((-0.045, 0.0), (-0.105, 0.0)), d=0.016, hef=0.150, dy_ch=0.110 - EXT_F)
    # 22/10 (colisão): zonas ocupadas pelo concreto acima da cobertura junto às fachadas 1 e 9 —
    # cantos de seção cheia (|y − linha| ≤ 0,20, x < 0,31 / x > LARG − 0,31) e cabeças 40 × 30 dos pilares de fachada
    # (x = eixo ± 0,21; y entre a face externa e a face da cabeça, que fica no eixo da linha: ≤ 0,01 do eixo)
    _XPF = [x for x in X_FACH[1:-1]]
    _YCI = (y_canto_int(Y_LIN[0]), y_canto_int(Y_LIN[-1]))            # rev12 (opção D): faces internas dos cantos deslocados

    def _bandas_fachada(t0, t1):
        cortes = sorted({t0, t1} | {c for c in (Y_LIN[0] + 0.01, _YCI[0] + 0.01, _YCI[1] - 0.01, Y_LIN[-1] - 0.01) if t0 < c < t1})
        return list(zip(cortes[:-1], cortes[1:]))

    def _livres(t0, t1, xa_k, xb_k):
        ym = (t0 + t1) / 2
        ocup = []
        if ym < _YCI[0] + 0.01 or ym > _YCI[1] - 0.01:
            ocup += [(-9.0, 0.31), (LARG - 0.31, LARG + 9.0)]
        if ym < Y_LIN[0] + 0.01 or ym > Y_LIN[-1] - 0.01:
            ocup += [(x - 0.21, x + 0.21) for x in _XPF]
        out, x = [], xa_k
        for a, b in sorted(ocup):
            if b <= x or a >= xb_k:
                continue
            if a > x:
                out.append((x, a))
            x = max(x, b)
        if x < xb_k:
            out.append((x, xb_k))
        return [(a, b) for a, b in out if b - a > 0.02]

    # rev06c: cobertura Kingspan zipada dupla com lã de rocha (manual p. 28) em camadas, cartolas sobre as terças e rufos (ND-LET-COB04)
    xa_, xb_ = AC.X_TELHA_A, AC.X_TELHA_E
    y0_, y1_ = AC.Y_TELHA_1, AC.Y_TELHA_9
    nfx = math.ceil((y1_ - y0_) / 1.0)
    bfx = (y1_ - y0_) / nfx
    for nome_, dz0, dz1, grp_ in (("TP-40 STD #0,65", 0.0, 0.040, "Telhas"), ("lã de rocha FSR 32", 0.040, 0.080, "Telhas"),
                                  ("zipada 455 #0,50", 0.080, 0.150, "Telhas"), ("painéis solares (envelope)", 0.150, 0.260, "Telhas")):
        for k in range(nfx):
            y = y0_ + (k + 0.5) * bfx
            pz = (dz0 + dz1) / 2
            # DEC-042: cantos de seção cheia (x < 0,30 e x > LARG − 0,30, |y − linha| < 0,20) — faixa junto às fachadas recortada no canto
            # 22/10 (colisão): recorte também nas cabeças 40 × 30 dos pilares de fachada (B, C, D das linhas 1 e 9), até 1 cm da face
            # da cabeça (eixo da linha) — RF-4P de 600 dobrado em volta da cabeça (ND-LET-COB04)
            yk0, yk1 = y0_ + k * bfx, y0_ + (k + 1) * bfx
            trechos = []
            for t0, t1 in _bandas_fachada(yk0, yk1):
                for xa_k, xb_k in _livres(t0, t1, xa_, xb_):
                    trechos.append((t0, t1, xa_k, xb_k))
            if nome_.startswith("painéis"):
                # 22/10 (colisão): campo de painéis recuado 0,15 m das bordas y e 0,30 / 0,60 m das bordas x (A / E), livre dos rufos RB / RF-3P
                trechos = [(max(y0_ + 0.15, yk0), min(y1_ - 0.15, yk1), xa_ + 0.30, xb_ - 0.60)]
                trechos = [t for t in trechos if t[1] - t[0] > 0.05]
            for t0, t1, xa_k, xb_k in trechos:
                yk = (t0 + t1) / 2
                m.linear("placa", nome_, PerfilRetangular(t1 - t0 - 0.002, dz1 - dz0, nome_), (xa_k, yk, AC.z_terca_topo(xa_k) + pz), (xb_k, yk, AC.z_terca_topo(xb_k) + pz), grp_, material="aco")
    for xt_ in LG["x_tercas_esq"] + [x + (2 * X_EIXO["C"] - LG["X_PONTA_CEN"]) - LG["X_PONTA_ESQ"] for x in LG["x_tercas_esq"]]:
        xc_ = xt_ - 0.027 - 0.045                         # cartola centrada na aba superior (90) da terça
        yc0, yc1 = (_YCI[0] + 0.01, _YCI[1] - 0.01) if xc_ + 0.06 > LARG - 0.30 else (y0_, y1_)   # DEC-042: última cartola do lado E entre os cantos
        m.linear("placa", "perfil cartola #0,65", PerfilRetangular(0.12, 0.04, "cartola"), (xc_, yc0, AC.z_terca_topo(xc_) + 0.06), (xc_, yc1, AC.z_terca_topo(xc_) + 0.06), "Telhas", material="aco")
    SEC = AC.secoes()

    def chapa_contorno(pts, t=0.002):
        """polilinha (u, v) → contorno fechado de chapa com espessura t (deslocada para a esquerda de cada trecho)."""
        import numpy as _np
        P = _np.array(pts, float)
        n = []
        for i in range(len(P) - 1):
            d = P[i + 1] - P[i]; d /= _np.linalg.norm(d); n.append(_np.array((-d[1], d[0])))
        off = [P[0] + t * n[0]] + [P[i] + t * (n[i - 1] + n[i]) / max(_np.linalg.norm(n[i - 1] + n[i]), 1e-9) for i in range(1, len(P) - 1)] + [P[-1] + t * n[-1]]
        return [tuple(p) for p in P] + [tuple(p) for p in reversed(off)]

    def rufo_y(mk, ya, yb, conv=lambda u, v: (u, v)):
        cont = chapa_contorno([conv(u, v) for u, v in SEC[mk][1]])
        m.extrusao_y("placa", f"{mk} rufo #0,65", cont, (ya + yb) / 2, yb - ya, "Rufos e acabamentos", material="aco", obs=SEC[mk][2])

    def rufo_x(mk, xa, xb, za, zb, conv):
        cont = chapa_contorno([conv(u, v) for u, v in SEC[mk][1]])
        u0, v0 = cont[0]
        perf = PerfilPoligono(tuple((round(u - u0, 6), round(v - v0, 6)) for u, v in cont), mk)
        m.add(Peca("placa", "Rufos e acabamentos", f"{mk} rufo #0,65", perf, (xa, u0, za + v0), (xb, u0, zb + v0), (0.0, 0.0, 1.0), "aco", SEC[mk][2]))

    PIL_Y = list(Y_LIN)
    _fi = lambda i, sg: (_YCI[0] if i == 0 else _YCI[1] if i == len(PIL_Y) - 1 else PIL_Y[i] + sg * 0.20)   # rev12: face interna (canto deslocado)
    tre = [(_fi(i, 1), _fi(i + 1, -1)) for i in range(len(PIL_Y) - 1)]
    for ya, yb in tre:
        rufo_y("RF-2", ya, yb); rufo_y("RF-3", ya, yb); rufo_y("CR-1", ya, yb)
    for yp in PIL_Y:
        dc = 0.30 if yp in (PIL_Y[0], PIL_Y[-1]) else 0.0                 # DEC-042: canto de seção cheia — face A 30 cm para dentro
        # 22/10 (colisão): no canto de seção cheia o RF-2C / RF-3P vai só até a face lateral do pilar (y = linha ± 0,20); dali segue o RF-2 / RF-3
        ya_c, yb_c = (yp - 0.30, _YCI[0]) if yp == PIL_Y[0] else (_YCI[1], yp + 0.30) if yp == PIL_Y[-1] else (yp - 0.30, yp + 0.30)   # rev12: canto deslocado
        rufo_y("RF-2C", ya_c, yb_c, lambda u, v, d_=dc: (min(u + d_, AC.X_CAB_A + d_ + 0.005) if d_ else u, v));   # canto: pé do RF-2C rente à face (a telha começa em 0,31)
        rufo_y("RF-3P", ya_c, yb_c, lambda u, v, d_=dc: (u - d_, v))
        # 22/10 (colisão): nos cantos de seção cheia o chapéu RF-1C cobre os 60 cm do topo (aba interna na face A, a 0,30 do eixo)
        rufo_y("RF-1C", yp - 0.30, yp + 0.30, lambda u, v, d_=dc: (AC.X_PLACA_A - 0.100 + (u + d_ if u > 0.44 else u), v))
        rufo_y("RF-1C", yp - 0.30, yp + 0.30, lambda u, v, d_=dc: (AC.X_PLACA_E + 0.100 - (u + d_ if u > 0.44 else u), v))
    rufo_y("PG-1", _YCI[0] + 0.01, _YCI[1] - 0.01)                    # 22/10: entre as faces laterais dos cantos de seção cheia
    rufo_y("RF-1", AC.Y_PLACA_1 - 0.10, AC.Y_PLACA_9 + 0.10, lambda u, v: (AC.X_PLACA_A - 0.100 + u, v))
    rufo_y("RF-1", AC.Y_PLACA_1 - 0.10, AC.Y_PLACA_9 + 0.10, lambda u, v: (AC.X_PLACA_E + 0.100 - u, v))
    zl_ = AC.z_zip(LARG / 2) + AC.PAC["zipada"]
    za_r, zb_r = AC.z_zip(xa_) + AC.PAC["zipada"], AC.z_zip(xb_) + AC.PAC["zipada"]
    for yface, sg in ((AC.Y_PLACA_1, 1), (AC.Y_PLACA_9, -1)):
        for mk in ("RF-4", "RF-4C", "RB-1/2"):                          # DEC-042: entre as faces A dos cantos de seção cheia (x 0,31 … LARG − 0,31)
            for xa_r, xb_r in _livres(Y_LIN[0] - 0.1, Y_LIN[0] - 0.05, 0.31, LARG - 0.31):   # 22/10: interrompidos nas cabeças dos PF (RF-4P)
                rufo_x(mk, xa_r, xb_r, AC.z_zip(xa_r) + AC.PAC["zipada"], AC.z_zip(xb_r) + AC.PAC["zipada"], lambda u, v, yf=yface, s_=sg: (yf + s_ * u, v - zl_))
        rufo_x("RF-1", AC.X_PLACA_A - 0.10, AC.X_PLACA_E + 0.10, 0.0, 0.0, lambda u, v, yf=yface, s_=sg: (yf - s_ * 0.100 + s_ * u, v))
    # contraventamento em X Ø16 (rev06, DEC-024/025): vãos 4-5 a 8-9, nós nas terças 0, 8, 15 de cada meia água
    BAR16 = PerfilRetangular(0.016, 0.016, "Ø16")
    CT = LG["contraventamento"]["chapa"]
    off_d = (2 * X_EIXO["C"] - LG["X_PONTA_CEN"]) - LG["X_PONTA_ESQ"]
    for meia in (LG["nos_x_esq"], [x + off_d for x in LG["nos_x_esq"]]):
        for k in LG["vaos_x"]:
            ya, yb = Y_LIN[k] + CT["y_orelha"], Y_LIN[k + 1] - (0.0 if k + 1 == len(Y_LIN) - 1 else CT["y_orelha"])
            sb = 0.200 if k + 1 == len(Y_LIN) - 1 else CT["s_orelha"]
            for xa, xb in zip(meia[:-1], meia[1:]):
                for (x1, x2), dz in (((xa + CT["s_orelha"], xb - sb), CT["z_baixo"]), ((xb - CT["s_orelha"], xa + sb), CT["z_alto"])):
                    yb_ = y_vb(x2, Y_LIN[-1]) if k + 1 == len(Y_LIN) - 1 else yb      # rev12: orelha no eixo da VB deslocada (faixa B–D)
                    pa, pb = (x1, ya, zf(x1) + H_TS + dz), (x2, yb_, zf(x2) + H_TS + dz)
                    m.linear("inserto", "X Ø16 A36 (trecho A + B)", BAR16, pa, pb, "Contraventamento", material="aco")
                    L_ = math.dist(pa, pb); ux, uy = (pb[0] - pa[0]) / L_, (pb[1] - pa[1]) / L_
                    e0 = [pa[i] + (pb[i] - pa[i]) * 9.0 / L_ for i in range(3)]
                    m.linear("inserto", "esticador M16", PerfilRetangular(0.036, 0.036), e0, [e0[i] + (pb[i] - pa[i]) * 0.2 / L_ for i in range(3)],
                             "Contraventamento", material="aco")
                    zc_b = zf(x2) + H_TS if k + 1 < len(Y_LIN) - 1 else zf(x2) + H_TS     # VB do eixo 9: topo da VB = topo da TS-01
                    orelha(m, x1, ya, zf(x1) + H_TS, ux, uy, dz)
                    orelha(m, x2, yb_, zc_b, -ux, -uy, dz)
    # rev06 (DEC-033): correntes Ø10 a L/4, L/2 e 3L/4 entre todas as terças; tirantes rígidos L 51×51×3,2 no 1º espaço de cada
    # ponta da meia água; diagonais de ancoragem Ø16 do nó da corrente na 2ª terça até o ST-1 da 1ª terça (ND-LET-COB02, det. 6 e 7)
    GC = "Correntes, tirantes rígidos e diagonais"
    Z_COR_, Z_DG_T, Z_DG_S = PC_["furo_corrente_z_mm"] / 1000, 0.245, 0.255
    R10, L51_ = PerfilRetangular(0.010, 0.010, "Ø10"), PerfilRetangular(0.051, 0.051, "L 51×51×3,2")
    for xa, _ in PONTAS:
        xws = [xa + s_ * C3 - 0.027 for s_ in LG["s_tercas"]]
        nt_ = len(xws)
        zb_ = lambda xw: zf(xw) + H_TS + 0.010
        for k in range(len(Y_LIN) - 1):
            ya, yb = Y_LIN[k], Y_LIN[k + 1]
            Lk = yb - ya
            for yq in (ya + Lk / 4, ya + Lk / 2, ya + 3 * Lk / 4):
                for j in range(nt_ - 1):
                    x1, x2 = xws[j] + 0.003, xws[j + 1] - 0.003
                    rig = j in (0, nt_ - 2)
                    m.linear("inserto", "R1 tirante rígido L 51×51×3,2" if rig else "C1 corrente flexível Ø10 (rosca M10)", L51_ if rig else R10,
                             (x1, yq, zb_(x1) + Z_COR_), (x2, yq, zb_(x2) + Z_COR_), GC, material="aco")
            for j0, j1 in ((1, 0), (nt_ - 2, nt_ - 1)):
                for yq, ye in ((ya + Lk / 4, ya), (ya + 3 * Lk / 4, yb)):
                    m.linear("inserto", "D diagonal de ancoragem Ø16 (2ª terça → ST-1 da 1ª)", BAR16, (xws[j0], yq, zb_(xws[j0]) + Z_DG_T),
                             (xws[j1] + (0.02 if j1 == 0 else -0.02), ye + (0.12 if ye == ya else -0.12), zf(xws[j1]) + H_TS + Z_DG_S), GC, material="aco")
    # calha do eixo A (rev06, calc_calha.py / ND-LET-COB03): 300 × 150, de x = 0,02 a 0,32, borda 40 mm abaixo da telha
    zt_c = zf(0.517) + H_TS + 0.010 + 0.302 - 0.03 * (0.49 - 0.25) - 0.040
    t_c = 0.003
    cal = [(0.02, zt_c + 0.12), (0.02, zt_c - 0.15), (0.32, zt_c - 0.15), (0.32, zt_c), (0.32 - t_c, zt_c), (0.32 - t_c, zt_c - 0.15 + t_c),
           (0.02 + t_c, zt_c - 0.15 + t_c), (0.02 + t_c, zt_c + 0.12)]
    m.extrusao_y("placa", "CA-1 calha 300×150 chapa galv. 1,25", cal, COMP / 2, COMP - 2 * (_YCI[0] + 0.02), "Calha e descidas", material="aco",
                 obs=f"NBR 10844; i = 0,5 % para as saídas; DEC-042: começa/termina a {(_YCI[0] + 0.02)*100:.0f} cm do eixo das linhas 1 e 9 (face interna do canto de seção cheia, rev12)")
    for yl in Y_LIN:
        yd = yl + (0.35 if yl < COMP else -0.35)
        if yl == Y_LIN[1]:
            yd = yl + 0.535                                   # 22/10 (colisão): na linha 2 a parede G ocupa y = linha + 0,325 a 0,425 → descida na frente dela
        m.linear("pilar", "DE-1 descida Ø200 (envelope)", PerfilRetangular(0.20, 0.20, "Ø200"), (0.17, yd, 0.0), (0.17, yd, zt_c - 0.15), "Calha e descidas", material="aco")

    # 5. mezanino (linhas 1–2), rev09 (DEC-047/048): VM RETANGULAR PROTENDIDA 30 × 75 com dente Gerber 45 × 40 nas pontas (DEC-049); laje
    #    apoiada 10 cm no topo da viga (fita 1 cm), 2º estágio de obra na faixa restante até o topo da capa, alças N9 saindo da
    #    peça; consolos CP-MEZ 40 × 40 × 27,9 (largura da face do pilar) com fundo alinhado; NEO-5F fretado; junta da ponta concretada antes das lajes (DEC-039).
    #    +3,90: abertura da escada (P6 → E, viga P6–P7 → linha 2), sem viga P6 → E na linha 2; +7,30: laje contínua.
    VMJ_ = json.loads((AQ / "vm_retangular.json").read_text(encoding="utf-8"))
    VMP = VMJ_["premissas"]
    hv, bt = VMP["h_pm"], VMP["b"]
    DT_ = VMP["dente"]
    hd, ln, rec, hcm, prj = DT_["hd"], DT_["ln"], DT_["recorte"], DT_["consolo_h"], DT_["consolo_proj"]
    FOL = 0.03
    E2, VMG = "Concreto de 2º estágio (obra, com a capa)", "Vigas de mezanino (retangulares protendidas)"
    meia_x = lambda nm: {"P1": 0.30, "P2": 0.30, "P6": 0.125}.get(nm, 0.20)
    fila1 = [("P1", 0.0), ("P3", X_EIXO["B"]), ("P4", X_EIXO["C"]), ("P5", X_EIXO["D"]), ("P2", LARG)]
    fila2 = [("P1", 0.0), ("P8", X_EIXO["B"]), ("P8A", X_EIXO["C"]), ("P8B", X_EIXO["D"]), ("P6", P6_L2[0]), ("P2", LARG)]
    MK_VM = {9.37: "VM-01", 9.48: "VM-02", 6.22: "VM-03", 2.90: "VM-04"}
    for iz, nivel in enumerate(NIVEIS_MEZ):
        za = nivel - H_LAJE - 0.01                          # topo da peça = apoio da laje (fita de neoprene 1 cm)
        zb = za - hv
        vigas = []                                          # (y, so, fa, fb): so = lado da laje (+1 para +y)
        for (pa, xa), (pb, xb) in zip(fila1[:-1], fila1[1:]):
            vigas.append((Y_VM1, 1, xa + meia_x(pa), xb - meia_x(pb)))          # rev12 (27/10): VM da linha 1 alinhada à face externa (eixo −0,15)
        for (pa, xa), (pb, xb) in zip(fila2[:-1], fila2[1:]):
            if iz == 0 and pa == "P6":
                continue                                    # +3,90: abertura da escada (sem viga P6 → E)
            vigas.append((Y_LIN[1], -1, xa + meia_x(pa), xb - meia_x(pb)))
        if iz == 0:
            vigas.append((P6_ESC[1], -1, P6_ESC[0] + 0.125, P7_ESC[0] - 0.30))      # viga P6–P7 (laje curta do lado da linha 1)
        for y, so, fa, fb in vigas:
            xa, xb = fa + FOL, fb - FOL
            L_ = xb - xa
            mk = MK_VM[min(MK_VM, key=lambda k: abs(k - (fb - fa)))]
            ob = f"retangular protendida {bt*100:.0f}×{hv*100:.0f}, dente {hd*100:.0f}×{ln*100:.0f}, L = {L_:.2f} m"
            m.linear("viga", f"{mk} corpo {nivel:+.2f}", PerfilRetangular(bt, hv), (xa + ln, y, zb + hv / 2), (xb - ln, y, zb + hv / 2), VMG, obs=ob)
            for x0_, x1_ in ((xa, xa + ln), (xb - ln, xb)):
                m.linear("viga", f"{mk} nariz {nivel:+.2f}", PerfilRetangular(bt, hd), (x0_, y, za - hd / 2), (x1_, y, za - hd / 2), VMG, obs=ob)
            b2 = bt - 0.10 - 0.02                            # faixa de 2º estágio: largura − apoio 10 − folga 2
            y2 = y - so * (bt / 2 - b2 / 2)
            m.linear("viga", f"2º estágio {nivel:+.2f}", PerfilRetangular(b2, nivel - za), (fa, y2, (za + nivel) / 2), (fb, y2, (za + nivel) / 2), E2,
                     obs="C30, concretado com a capa por quem faz a capa (faixa de 2º estágio sobre a viga)")
            m.bloco("inserto", "NEO-L fita 10 × 100", ((xa + xb) / 2, y + so * (bt / 2 - 0.05), za + 0.01), L_, 0.10, 0.01, "Pinos, tubos e neoprenes")
            xx = xa + 0.15
            while xx < xb - 0.10:                                      # alças N9 da viga saindo 20 cm (a cada 15 cm; uma a cada 30 cm no 3D)
                m.bloco("inserto", "alça N9 Ø10", (xx, y2, za + 0.20), 0.012, max(b2 - 0.05, 0.05), 0.20, "Alças N9 (2º estágio)")
                xx += 0.30
            for xf, sg in ((fa, 1), (fb, -1)):
                bc_ = CONS["CP-MEZ"]["b_m"]                                   # rev12: consolo com a largura da VM (30), sob a VM, com mísula
                hf_ = CONS["CP-MEZ"]["h_total_m"]
                _pts = [(0.0, 0.0), (sg * prj, 0.0), (sg * prj, -hcm), (0.0, -hf_)]
                if sg < 0:
                    _pts = _pts[::-1]
                from nd_estruturas.bim import Peca as _PecaM, PerfilPoligono as _PPM
                m.add(_PecaM("consolo", "Consolos", f"CP-MEZ {bc_*100:.0f}×{prj*100:.0f}", _PPM(tuple(_pts), "CP-MEZ com mísula"),
                             (xf, y + bc_ / 2, zb + hcm), (xf, y - bc_ / 2, zb + hcm),   # eixo −y: u local = +x (como o CP-I120)
                             (0.0, 0.0, 1.0), "concreto",
                             f"b {bc_*100:.0f} (largura da VM), projeção {prj*100:.0f}, h {hf_*100:.0f} na face / {hcm*100:.1f} na ponta"))
                m.bloco("inserto", "NEO-5F 200×200 fretado", (xf + sg * VMP["x_pad"], y, zb + hcm + 0.021), 0.20, 0.20, 0.021, "Pinos, tubos e neoprenes")
                m.bloco("inserto", "PN-1 pino Ø20 (VM)", (xf + sg * VMP["x_pad"], y, zb + hcm + 0.40), 0.02, 0.02, 0.63, "Pinos, tubos e neoprenes")
                m.bloco("inserto", "junta da ponta concretada 3 cm (fck ≥ 30, antes das lajes)", (xf + sg * FOL / 2, y, za), FOL, bt, hd, E2)
        for x0, b_, mk, yl0_, yl1_ in paineis_nivel(iz):           # mesma paginação da ND-LET-LA01 (+3,90 com LA-03 / LA-04 no vão da escada)
            x = (x0 + b_ / 2) / 1000
            xa_l, xb_l = x0 / 1000, (x0 + b_) / 1000
            ya_l, yb_l = yl0_ / 1000, yl1_ / 1000
            perf = LAJE if b_ == 1250 else PerfilRetangular(0.70, H_LAJE, "Laje alveolar 70")
            furos = []
            for q in m.pecas:
                if q.grupo == "Pilares" and q.tipo == "pilar" and min(q.p0[2], q.p1[2]) < nivel and max(q.p0[2], q.p1[2]) > nivel - H_LAJE:
                    qx, qy, bx_, by_ = q.p0[0], q.p0[1], q.perfil.b, q.perfil.h
                    fx0, fx1, fy0, fy1 = qx - bx_ / 2 - 0.02, qx + bx_ / 2 + 0.02, qy - by_ / 2 - 0.02, qy + by_ / 2 + 0.02
                    if fx0 < xb_l and fx1 > xa_l and fy0 < yb_l and fy1 > ya_l:
                        furos.append((fx0, fx1, fy0, fy1))
            if not furos:
                m.linear("laje", f"{mk} {nivel:+.2f}", perf, (x, ya_l, nivel - H_LAJE / 2), (x, yb_l, nivel - H_LAJE / 2), "Laje alveolar")
            else:
                ys_ = sorted({ya_l, yb_l} | {v for f in furos for v in (f[2], f[3]) if ya_l < v < yb_l})
                for t0, t1 in zip(ys_[:-1], ys_[1:]):
                    tm = (t0 + t1) / 2
                    xs_ = [(xa_l, xb_l)]
                    for fx0, fx1, fy0, fy1 in furos:
                        if fy0 <= tm <= fy1:
                            xs_ = [seg for a, b in xs_ for seg in ((a, min(b, fx0)), (max(a, fx1), b)) if seg[1] - seg[0] > 0.01]
                    for a, b in xs_:
                        m.linear("laje", f"{mk} {nivel:+.2f}", PerfilRetangular(b - a, H_LAJE, f"Laje alveolar (recorte) {b - a:.2f}"),
                                 ((a + b) / 2, t0, nivel - H_LAJE / 2), ((a + b) / 2, t1, nivel - H_LAJE / 2), "Laje alveolar")

    # 5b. rev09 (DEC-048/052): cobertura metálica da linha 2 — W 200 contínua (topo na inclinação da cobertura) sobre montantes W 150
    #     nos pilares (A recuo, B, C, D, P6, E recuo); emendas parafusadas; ST-W das terças e mão-francesa em toda terça
    CB2 = json.loads((AQ / "cob_linha2.json").read_text(encoding="utf-8"))
    GL2 = "Cobertura metálica da linha 2"
    from nd_estruturas import metalica_laminada as _ML
    W_ = _ML.perfil(CB2["perfil"])
    PW = PerfilI(h=W_.d / 1000, b=W_.bf / 1000, tw=W_.tw / 1000, tf=W_.tf / 1000, nome=CB2["perfil"])
    y2 = Y_LIN[1]
    z_top = lambda x: zf(x) + H_TS / C3
    zc_w = lambda x: z_top(x) - W_.d / 2000
    cortes = [0.025] + CB2["emendas_x"] + [LARG - 0.025]
    for k_, (x0w, x1w) in enumerate(zip(cortes[:-1], cortes[1:])):
        m.linear("viga", f"W-L2 módulo {k_ + 1} ({CB2['perfil']})", PW, (x0w + 0.002, y2, zc_w(x0w + 0.002)), (x1w - 0.002, y2, zc_w(x1w - 0.002)), GL2, material="aco",
                 obs=f"{CB2['perfil']} A572-50, L = {x1w - x0w:.2f} m; topo na inclinação da cobertura (3 %)")
    # rev11 (26/10/2026): emendas, apoios nos pilares, montantes e ST-W/MF-1 gerados de lig_cob.py — a mesma geometria dos
    # isométricos da ND-LET-COB09 (DEC-052: CA-L2 + 4 BR-M16 no gabarito 55; montantes W 150 com CB-M1/CB-M2 nas esperas EM-L2)
    import lig_cob as LCB

    def _lig(partes, ox, oy, oz, grupo):
        for p_ in partes:
            if p_["ctx"] or p_["marca"] in ("T", "W-L2"):          # terças e W já modeladas (contínuas e inclinadas)
                continue
            nm_ = f"{p_['marca']} {p_['desc']}".strip() or p_["marca"]
            if p_["g"] == "caixa":
                x0_, x1_, y0_, y1_, z0_, z1_ = p_["b"]
                caixa(m, nm_, ox + x0_ / 1000, ox + x1_ / 1000, oy + y0_ / 1000, oy + y1_ / 1000, oz + z0_ / 1000, oz + z1_ / 1000, grupo)
            elif p_["g"] in ("cil", "hex"):
                c_, h_, r_ = p_["c"], p_["h"] / 1000, p_["r"] / 1000
                a_ = (ox + c_[0] / 1000, oy + c_[1] / 1000, oz + c_[2] / 1000)
                ax_ = "xyz".index(p_["eixo"])
                b_ = list(a_); b_[ax_] += h_
                if abs(h_) > 1e-4:
                    m.linear("inserto", nm_, PerfilRetangular(2 * r_, 2 * r_, p_["marca"]), a_, tuple(b_), "Parafusos da cobertura",
                             cima=(0.0, 0.0, 1.0) if ax_ != 2 else (0.0, 1.0, 0.0), material="aco")
            elif p_["g"] == "barra":
                a_ = tuple(o + v / 1000 for o, v in zip((ox, oy, oz), p_["a"]))
                b_ = tuple(o + v / 1000 for o, v in zip((ox, oy, oz), p_["b"]))
                m.linear("inserto", nm_, PerfilRetangular(0.051, 0.051, "L 51×51×4,8"), a_, b_, grupo, material="aco")

    for xe in CB2["emendas_x"]:
        _lig(LCB.emenda_w(), xe, y2, zc_w(xe) - W_.d / 2000, GL2)
    for a_ in CB2["apoios_diretos"]:
        _lig(LCB.apoio_w_pilar(), a_["x"], y2, a_["z_concreto"], GL2)
    for mt_ in CB2["montantes"]:
        _lig(LCB.montante(mt_["L_m"] * 1000), mt_["x"], y2, mt_["z_base"] - 0.020, GL2)
    for xt_ in LG["x_tercas_esq"] + [x + (2 * X_EIXO["C"] - LG["X_PONTA_CEN"]) - LG["X_PONTA_ESQ"] for x in LG["x_tercas_esq"]]:
        xw = xt_ - 0.027
        _lig(LCB.terca_w(), xw, y2, z_top(xw), GL2)

    # 5c/5d. rev09d (DEC-060, 24/10): escadas metálicas interna (ES01) e externa (ES02) com guarda-corpos e corrimãos (RT CBMRS 11)
    # e todas as ligações parafusadas — peças geradas por escadas_detalhe.py (fonte única: pranchas ES01/ES02/ES03, lista e 3D)
    import escadas_detalhe as ESD
    from nd_estruturas.bim import Peca as _PecaE, PerfilPoligono as _PPE
    for pc in ESD.P:
        if pc["g"] == "caixa":
            caixa(m, pc["marca"], pc["x0"], pc["x1"], pc["y0"], pc["y1"], pc["z0"], pc["z1"], pc["grupo"])
        elif pc["g"] == "linear":
            pf = pc["perfil"]
            prf = PerfilI(h=pf[1], b=pf[2], tw=pf[3], tf=pf[4], nome=pf[5]) if pf[0] == "I" else PerfilRetangular(pf[1], pf[2], pf[3])
            m.linear(pc["tipo"], pc["marca"], prf, pc["p0"], pc["p1"], pc["grupo"], cima=pc["cima"], material="aco", obs=pc.get("obs", ""))
        else:
            c0, z0_ = pc["contorno"][0]
            pts_ = tuple((round(c - c0, 6), round(z - z0_, 6)) for c, z in pc["contorno"])
            if pc["eixo"] == "y":                                    # contorno (y, z), extrudado em x de a0 a a1 (u local = +y)
                p0_, p1_ = (pc["a0"], c0, z0_), (pc["a1"], c0, z0_)
            else:                                                    # contorno (x, z), extrudado em y: eixo −y (u local = +x)
                p0_, p1_ = (c0, pc["a1"], z0_), (c0, pc["a0"], z0_)
            m.add(_PecaE(pc["tipo"], pc["grupo"], pc["marca"], _PPE(pts_, pc["marca"][:40]), p0_, p1_, (0.0, 0.0, 1.0), "aco", pc.get("obs", "")))
    GEX = "Escada metálica externa"
    # ombreiras OM-2 internas da porta do 2º pav. (vista H): U 152 do piso do térreo a +5,00, por trás das placas, travadas no P28
    for yj, dd in ((FCH.PORTA_H[0] / 1000 - 0.020 - 0.0485, -1), (FCH.PORTA_H[1] / 1000 + 0.020, 1)):
        m.linear("pilar", "OM-2 ombreira interna U 152 × 12,2 (porta do 2º pav., vista H)", PerfilRetangular(0.152, 0.0485, "U 152 × 12,2"),
                 (-0.325 + 0.076, yj + 0.02425, 0.0125), (-0.325 + 0.076, yj + 0.02425, 5.0), GEX, material="aco")
        # rev12: placa da vista H 10 cm mais longa (canto deslocado) → pino PT-1 da fiada 0 em y ≈ 1,94; a chapa de base da OM-2 do lado
        # da linha 2 fica para o lado da porta (y − 0,125 … + 0,075), livre do PT-1
        _yb = (yj - 0.125, yj + 0.075) if dd > 0 else (yj - 0.075, yj + 0.125)
        caixa(m, "OM-2 chapa de base 12,5 × 200 × 200 + 4 chumbadores químicos M12", -0.325, -0.125, _yb[0], _yb[1], 0.0, 0.0125, GEX)
        _yc = (yj - 0.10, yj) if dd < 0 else (yj + 0.0485, yj + 0.1485)   # console ao lado da ombreira (na aba), do lado da placa
        caixa(m, "OM-2 console L 102 × 102 × 9,5 (apoio da ponta da placa da fiada +3,75)", -0.325, -0.223, _yc[0], _yc[1], 3.75 - 0.0095, 3.75, GEX)
        # rev09d: OM-2 do lado do P28 travada no P28 em +4,30 e +4,90 (acima do PT-2 da fiada +3,75); a outra ombreira travada
        # na primeira só em +3,88, abaixo da soleira da porta (+3,95) — nenhuma trava atravessa o vão da porta
        travas = ((0.20, yj, 4.30), (0.20, yj, 4.90)) if dd < 0 else ((FCH.PORTA_H[0] / 1000 - 0.020, yj, 3.88),)
        for y_ini, y_fim, zt_ in travas:
            caixa(m, "OM-2 trava L 76 × 76 × 6,3 até o P28 (2 BR-M16 na face do pilar)" if dd < 0 else "OM-2 trava L 76 × 76 × 6,3 até a outra ombreira (sob a soleira, 2 M12)",
                  -0.30, -0.224, y_ini, y_fim, zt_ - 0.038, zt_ + 0.038, GEX)

    # 5e. DEC-059 (24/10): placa PV-1 sobre o portão P19–D da linha 4 (+7,50 até 6 cm abaixo do fundo da TS-01A), apoiada nas
    #     cantoneiras CL-V das faces dos PG-04 e PG-03 (BR-M16 embutidas) e travada no topo pelas CT-V; portões livres até +7,50
    PJ = json.loads((AQ / "portao_l4.json").read_text(encoding="utf-8"))
    yl4 = Y_LIN[LINHA_PORTOES]
    yc_pl = yl4 - (0.20 + 0.025 + 0.05)                                   # mesmo plano da parede C (placas a 2,5 cm da face dos PG 40×40)
    x0v, x1v = X_L4[4] + 0.010, X_L4[5] - 0.010
    z0v, z1v = PJ["placa_P19_D"]["z0"] + 0.005, PJ["placa_P19_D"]["z1"]
    m.linear("placa", "PV-1 placa sobre o portão P19–D (10 × 37, DEC-059)", PerfilRetangular(0.10, z1v - z0v, "PV-1 10×37"),
             (x0v, yc_pl, (z0v + z1v) / 2), (x1v, yc_pl, (z0v + z1v) / 2), "Placas de fechamento", obs="armada, C40; peso próprio nos 2 apoios CL-V; ND-LET-PV01")
    for mk_pg, xpg, bpg, lh in (("PG-04", X_L4[4], PG_L4["PG-04"][3], 0.102), ("PG-03", X_L4[5], PG_L4["PG-03"][3], 0.102)):   # DEC-092: faces no mesmo plano
        yface = Y_PG[mk_pg] - bpg / 2
        caixa(m, f"CL-V cantoneira L {lh * 1000:.0f} × 102 × 9,5 L=150 — apoio da PV-1 (2 BR-M16 na face do PG)", xpg - 0.075, xpg + 0.075, yface - lh, yface, z0v - 0.005 - 0.0095, z0v - 0.005, GM)
        caixa(m, f"CL-V cantoneira — aba na face do PG", xpg - 0.075, xpg + 0.075, yface - 0.0095, yface, z0v - 0.005 - 0.102, z0v - 0.005, GM)
        caixa(m, "CT-V cantoneira L 76 × 76 × 6,3 L=80 — aba na face do PG (1 BR-M16)", xpg - 0.04, xpg + 0.04, yface - 0.0063, yface, z1v - 0.07, z1v + 0.0063, GM)
        caixa(m, "CT-V cantoneira — aba sobre o topo da PV-1 (1 M12 vertical na bucha BR-2)", xpg - 0.04, xpg + 0.04, yface - 0.076, yface - 0.0063, z1v + 0.0005, z1v + 0.0063, GM)

    # 6. placas de fechamento: as mesmas peças das pranchas PP (fechamento.py, vistas do R01)
    PL = PerfilRetangular(0.10, 1.25, "Placa 125×10 protendida")
    o_ext, o_c = 0.30 + 0.025 + 0.05, 0.20 + 0.025 + 0.05
    pos = {"A": ("x", COMP + o_ext), "I": ("x", -o_ext), "G": ("x", Y_LIN[1] + o_ext), "C": ("x", Y_LIN[LINHA_PORTOES] - o_c),   # 22/10: parede C do lado −y da linha 4 (área aberta), como na ND-LET-CM01
           "B": ("y", -o_ext), "E": ("y", -o_ext), "H": ("y", -o_ext), "D": ("y", LARG + o_ext), "F": ("y", LARG + o_ext), "J": ("y", LARG + o_ext)}
    for V, (pecas, ca1, _) in FCH.DADOS.items():
        ax, c = pos[V]
        for pc in pecas:
            s0, s1, z = pc["s0"] / 1000, pc["s1"] / 1000, (pc["z0"] + pc["z1"]) / 2000
            if pc.get("rec"):                                            # DEC-044: placa recortada na ponta do eixo C (toco 260 × 120 embaixo)
                rb, rz = FCH.REC_B / 1000, FCH.REC_Z0 / 1000
                (a0, a1), (b0, b1) = ((s0, s1 - rb), (s1 - rb, s1)) if pc["rec"] == "s1" else ((s0 + rb, s1), (s0, s0 + rb))
                z0p = pc["z0"] / 1000
                for (u0, u1, zc, prf, nm) in ((a0, a1, z, PL, ""), (b0, b1, z0p + rz / 2, PerfilRetangular(0.10, rz, "Placa 125×10 — toco do recorte"), " toco do recorte")):
                    p0, p1 = ((u0, c, zc), (u1, c, zc)) if ax == "x" else ((c, u0, zc), (c, u1, zc))
                    m.linear("placa", f"{pc['id']} (vista {V}){nm}", prf, p0, p1, "Placas de fechamento",
                             obs=f"L = {pc['L']} mm; {FCH.TIPO[pc['Lk']]}: recorte {FCH.REC_B} × {FCH.H_PL - FCH.REC_Z0} na ponta do eixo C (DEC-044, ND-LET-PP06); apoio: {pc['apoio']}")
                continue
            p0, p1 = ((s0, c, z), (s1, c, z)) if ax == "x" else ((c, s0, z), (c, s1, z))
            m.linear("placa", f"{pc['id']} (vista {V})", PL, p0, p1, "Placas de fechamento", obs=f"L = {pc['L']} mm; apoio: {pc['apoio']}")
    # rev04: sem vigas de travamento VT (não há ponte rolante — NBR 9062:2017 5.1.2.1 e regra ND)

    # 7. insertos e ligações (conferência no 3D)
    INS, PIN = "Insertos metálicos", "Pinos, tubos e neoprenes"
    for i in range(3, 9):                                  # rev09: linha 2 sem TS-01 (W 200 + ST-W, mais abaixo)
        y = Y_LIN[i - 1]
        AP, PT = LG["apoios_ts"], LG["PINO_TS"]                 # rev04: assentos horizontais; pinos a 7,75 cm das 4 pontas
        # rev10 (DEC-061): nas linhas sobre a I120 (3, 5, 6, 7, 8) a TS-01 assenta na mesa + consolo lateral CT-I120 com NEO-3C 150 × 300;
        # na linha 4 (topo do P11) continua o NEO-3 100 × 300
        _ce, _cd, _nn, _dn = (("centro_esq", "centro_dir", "2 PN-5 Ø20 + NEO-3", (0.10, 0.30)) if i == 4 else
                              ("i130_esq", "i130_dir", "2 PN-5 Ø20 + NEO-3C (sobre o consolo CT-I120)", (0.15, 0.30)))
        if i != 4:
            _ct = LG["CT_I120"]
            _pj, _hh, _he, _bh = _ct["proj"], _ct["h"], _ct["h_ext"], _ct["b"] / 2
            _pl = [(0.20, 0.0), (0.20, -0.25), (0.075, -0.25), (0.075, -_hh), (0.20, -_hh), (0.20 + _pj, -_he), (0.20 + _pj, 0.0)]
            _dg = LG["DEGRAU_C"]                                   # lado E: topo 12 mm acima (degrau), fundo no mesmo nível do lado A
            _plE = [(u, v + _dg if v == 0.0 else v) for u, v in _pl]
            for _zr, _poly, _lado in ((Z_I120_TOPO, _pl, "lado A"), (Z_I120_TOPO, [(-u, v) for u, v in _plE][::-1], "lado E")):
                m.add(Peca("consolo", "Consolos", f"CT-I120 L{i} {_lado}", PerfilPoligono(tuple(_poly), "CT-I120 com mísula"),
                           (X_C, y - _bh, _zr), (X_C, y + _bh, _zr), (0.0, 0.0, 1.0), "concreto",
                           f"consolo lateral da I120 (DEC-061): b {_ct['b']*100:.0f}, projeção {_pj*100:.0f}, h {_hh*100:.0f}/{_he*100:.0f}; apoio da TS-01"))
        for (xn, z_as), xpin, nome_, neo, dpin in (((AP["P1"]["x_neo"], AP["P1"]["z"]), PONTAS[0][0] + PT, "2 PN-3 Ø25 + NEO-4", (0.20, 0.30), 0.025),
                                                  ((AP[_ce]["x_neo"], AP[_ce]["z"]), PONTAS[0][1] - PT, _nn, _dn, 0.020),
                                                  ((AP[_cd]["x_neo"], AP[_cd]["z"]), PONTAS[1][0] + PT, _nn, _dn, 0.020),
                                                  ((AP["P2"]["x_neo"], AP["P2"]["z"]), PONTAS[1][1] - PT, "2 PN-3 Ø25 + NEO-4", (0.20, 0.30), 0.025)):
            for dy in (-0.10, 0.10):
                m.bloco("inserto", nome_, (xpin, y + dy, z_as + 0.31), dpin, dpin, 0.61, PIN)
            m.bloco("inserto", nome_, (xn, y, z_as + 0.010), neo[0], neo[1], 0.01, PIN)
        nst = len(LG["s_tercas"])
        for ip_, (xa, _) in enumerate(PONTAS):
            for k, s_ in enumerate(LG["s_tercas"]):
                x = xa + s_ * C3 - 0.027
                if i == 2 and ((ip_ == 0 and k == 0) or (ip_ == 1 and k == nst - 1)):   # rev06 (DEC-033): beirais do eixo 2 — 4 esperas
                    suporte_st(m, "ST-1P4 (TS-01B eixo 2, beiral; 4 esperas — aprovado DEC-036)", x, y, zf(x) + H_TS, aba=0.200,
                               esperas=((-0.155, -0.06), (-0.155, 0.06), (-0.075, -0.06), (-0.075, 0.06)), d=0.016, hef=0.150, grampo=True)
                else:
                    suporte_st(m, "ST-1P (TS-01)", x, y, zf(x) + H_TS, esperas=((-0.075, -0.06), (-0.075, 0.06)), d=0.016, hef=0.150, grampo=True)
    # rev06 (DEC-026): fixação das placas pelo sistema Trejor, como no PP00 — CE-1 no pilar (uma por fiada), console CS-1 soldado,
    # nicho NC-1 nas pontas da placa, pinos PT-1 nas juntas (panos contínuos até o baldrame) e trava de pé PT-2 (pacotes suspensos)
    LINHA_PAREDE = {"A": COMP, "I": 0.0, "G": Y_LIN[1], "C": Y_LIN[LINHA_PORTOES], "B": 0.0, "E": 0.0, "H": 0.0, "D": LARG, "F": LARG, "J": LARG}

    def rasgo(V, c):
        """sentido da normal da parede, do eixo dos pilares para a placa (22/10: pela linha da parede — antes pela metade da
        obra, o que punha a CE-1/CS-1 das paredes internas G e C do lado errado do pilar)."""
        return 1 if c > LINHA_PAREDE[V] else -1
    for V, (pecas, ca1, _) in FCH.DADOS.items():
        ax, c = pos[V]
        out = rasgo(V, c)
        y_face = c - out * (0.025 + 0.05)                                  # face do pilar do lado das placas (v = 0; v > 0 entra no pilar)
        P_ = lambda u, v, z: (u, y_face - out * v, z) if ax == "x" else (y_face - out * v, u, z)
        def cx(u0, u1, v0, v1, z0, z1, marca, grupo=GP, obs=""):
            (a0, b0, _), (a1, b1, _) = P_(u0, v0, 0), P_(u1, v1, 0)
            caixa(m, marca, a0, a1, b0, b1, z0, z1, grupo, obs)
        pil = FCH.VISTAS[V]["pil"]
        # rev06d (DEC-028): ombreiras OM-1 em U na porta (ND-LET-PP05) — abas abraçando a ponta das placas, base no baldrame, CL-1 no topo
        for (a0_, a1_, _z0, _z1, rot_) in FCH.DADOS[V][2]:
            if rot_ != "porta" or _z0 > 0:                              # rev09c: porta do 2º pav. (vista H) usa a OM-2 interna, não a OM-1
                continue
            for xe, dd in ((a0_ / 1000, -1), (a1_ / 1000, 1)):           # dd: sentido da placa a partir da face do vão
                def ux(a, b):
                    return sorted((xe + dd * a, xe + dd * b))
                ua, ub = ux(0.0, 0.0063); cx(ua, ub, -0.1373, -0.0127, 0.0125, 2.490, "OM-1 alma U 125×80×6,3", GP, obs="ND-LET-PP05")
                ua, ub = ux(0.0, 0.080)
                cx(ua, ub, -0.019, -0.0127, 0.0125, 2.490, "OM-1 aba interna", GP); cx(ua, ub, -0.1373, -0.131, 0.0125, 2.490, "OM-1 aba externa", GP)
                ua, ub = ux(-0.160, 0.020); cx(ua, ub, -0.175, 0.025, 0.0, 0.0125, "OM-1 chapa de base 12,5×200×180", GP)
                for xc_ in (-0.060, -0.130):
                    ua, ub = ux(xc_ - 0.008, xc_ + 0.008); cx(ua, ub, -0.083, -0.067, -0.100, 0.035, "OM-1 chumbador químico M16 hef 100", GP)
                ua, ub = ux(-0.010, 0.090); cx(ua, ub, -0.0127, -0.0002, 2.340, 2.700, "CL-1 chapa de ligação 12,5×100×360", GP, obs="M16 em bucha BR-1 na I-15")
        cons = {(round(s_), round(z_)) for (s_, z_) in ca1}
        ce_feitas = set()
        for pc in pecas:
            z0p = pc["z0"] / 1000
            zt = z0p + (FCH.Z_NC + FCH.NC_H / 2 - GF.N["t_teto"] - GF.T["G"]) / 1000   # topo da mesa do CS-1 (rev06c, PP03)
            for (t, d, xcs_, e_cal) in ((pc["s0"], 1, pc["xcs"][0], pc["calco"][0]), (pc["s1"], -1, pc["xcs"][1], pc["calco"][1])):
                uc = t + d * xcs_                                          # DEC-044: 330 da ponta nas placas recortadas
                if (round(uc), round(pc["z0"] + FCH.Z_NC)) not in cons:
                    continue                                               # ponta da porta: sem console
                u = uc / 1000
                ecal = e_cal / 1000                                        # DEC-044: calço CS-1C/CS-1D — a face real do pilar fica ecal atrás do plano dos consoles
                # NC-1 / NC-1' e CS-1 com a geometria das pranchas PP02/PP03 (geo_fixacao, caixas envolventes de cada peça)
                for sol, grupo, pref in ((GF.nc1_no_console(0), GE, "NC-1"), (GF.cs1_solidos(0), GP, "CS-1")):
                    for so in sol:
                        if so.item in (7, 8, 15, 17):
                            continue                               # grampos e porcas: só nas pranchas (IFC mais leve)
                        P3 = np.vstack(so.faces)
                        x0_, y0_, z0_ = P3.min(0); x1_, y1_, z1_ = P3.max(0)
                        ua, ub = sorted(((uc + d * x0_) / 1000, (uc + d * x1_) / 1000))
                        bw_c = next(b_ for sp, b_, _ in pil if abs(sp - min((q for q, _, _ in pil), key=lambda q: abs(q - uc))) < 1e-6)
                        cc_ = GF.concretado(V, bw_c)
                        mk_ = (f"CC-1 {pref} {so.nome} (de fábrica, face C)" if cc_ else f"{pref} {so.nome} (soldado na obra)") if pref == "CS-1" else f"{pref} {so.nome}"
                        if ecal and pref == "CS-1":
                            mk_ = f"{FCH.CALCO_MARCA[e_cal]} {so.nome} (CS-1 com calço {e_cal:g}, DEC-044)"
                        cx(ua, ub, -y1_ / 1000, -y0_ / 1000, zt + z0_ / 1000, zt + z1_ / 1000, mk_, grupo,
                           obs=("solda de fábrica do CC-1, concretado com o pilar (DEC-031)" if cc_ else "solda de campo filete 5 E70XX nos 2 lados verticais (DEC-030)") if so.nome == "costas" else "")
                if ecal:                                                   # caixa do calço 120 × 330 × e (chapa 9,5), entre as costas do CS-1 e a CE-1
                    zce_ = z0p + FCH.Z_CE / 1000
                    cx(u - 0.06, u + 0.06, 0.0, ecal, zce_ - 0.165, zce_ + 0.165, f"{FCH.CALCO_MARCA[e_cal]} caixa de calço 120×330×{e_cal:g} ch. 9,5", GP,
                       obs="soldada na fábrica nas costas do CS-1; fundo soldado na CE-1 na obra (filete 6, 2 × 330) — DEC-044, ND-LET-PP06")
                # CE-1 do pilar (uma por pilar e fiada)
                s_ax = min((sp for sp, _, _ in pil), key=lambda sp: abs(sp - uc)) / 1000
                bw = next(b_ for sp, b_, _ in pil if abs(sp / 1000 - s_ax) < 1e-6) / 1000
                if (s_ax, pc["k"]) not in ce_feitas:
                    ce_feitas.add((s_ax, pc["k"]))
                    zce = z0p + FCH.Z_CE / 1000
                    ub = min(0.19, bw / 2 - 0.01)
                    tce = GF.TCE / 1000
                    c_ce = s_ax
                    nome_ce = f"CE-1 chapa de espera 380×330×{GF.TCE:g}".replace(".", ",")
                    if pc.get("rec") and abs(u - s_ax) > 0.25:              # DEC-044: CE-1L com asas (console a 340 do eixo do pilar)
                        ub = FCH.CE1L_B / 2000
                        nome_ce = f"CE-1L chapa de espera {FCH.CE1L_B}×330×{GF.TCE:g} (asas de 220 além do pilar)".replace(".", ",")
                    elif abs(u - s_ax) + 0.06 > ub - 0.005:                  # DEC-042: ponta de parede — CE-1 a 5 mm da aresta, sob o console
                        c_ce = s_ax + math.copysign(bw / 2 - 0.005 - 0.19, u - s_ax)
                        ub = 0.19
                    cx(c_ce - ub, c_ce + ub, ecal, ecal + tce, zce - 0.165, zce + 0.165, nome_ce, GE)
                    for du in (-0.12, 0.12):
                        for dz in (-0.14, 0.14):
                            cx(c_ce + du - 0.008, c_ce + du + 0.008, ecal + tce, ecal + tce + 0.150, zce + dz - 0.008, zce + dz + 0.008, "CE-1 pino Ø16 × 150 c/ cabeça", GE)
            # pinos PT-1 (junta de baixo) ou travas de pé PT-2
            if pc["trava"] == "PT-1":
                for j_, xp in enumerate((pc["s0"] + FCH.X_PT(pc["L"]), pc["s1"] - FCH.X_PT(pc["L"]))):
                    u = xp / 1000
                    if pc.get("pt1r", [False, False])[j_]:              # rev12: junta em frente à VB rente à face — chapa plana PT-1R
                        cx(u - 0.04, u + 0.04, -0.025, -0.0187, z0p - 0.11, z0p + 0.11, "PT-1R chapa plana 6,3 × 80 × 220 (junta em frente à VB)")
                        cx(u - 0.012, u + 0.012, -0.0187, -0.0057, z0p - 0.082, z0p - 0.058, "PT-1R cabeça M16 + arruela", GE)
                    else:
                        cx(u - 0.04, u + 0.04, -0.025, 0.0113, z0p - 0.11, z0p + 0.11, "PT-1 cartola Trejor 6,3 × 80")
                    for dz in (-0.07, 0.07):
                        cx(u - 0.008, u + 0.008, -0.095, -0.025, z0p + dz - 0.008, z0p + dz + 0.008, "TSA luva M16 hef 70", GE)
            for (xp, zp) in pc["pt2"]:
                d = 1 if xp > min(abs(xp - sp) for sp, _, _ in pil) and any(abs(xp - 51 - (sp + b_ / 2)) < 2 for sp, b_, _ in pil) else -1
                uf = (xp - d * 51) / 1000
                zpp = zp / 1000
                cx(uf, uf + d * 0.0095, -0.025, 0.077, zpp - 0.075, zpp + 0.075, "PT-2 L 102×102×9,5 L=150 (aba no pilar)")
                cx(uf, uf + d * 0.102, -0.025, -0.0155, zpp - 0.075, zpp + 0.075, "PT-2 L 102×102×9,5 L=150 (aba na placa)")

    # 8. piso e fundações (indicativos): piso de concreto 15 cm e blocos de fundação com cálice sob cada pilar
    m.linear("laje", "PISO e=15 (indicativo)", PerfilRetangular(AC.X_PLACA_E - AC.X_PLACA_A, 0.15), ((AC.X_PLACA_A + AC.X_PLACA_E) / 2, AC.Y_PLACA_1, -0.075),
             ((AC.X_PLACA_A + AC.X_PLACA_E) / 2, AC.Y_PLACA_9, -0.075), "Piso e fundações")        # 22/10: até a face interna das placas
    for peca in list(m.pecas):
        if peca.tipo == "pilar":
            x, y, _ = peca.p0
            bx, by = peca.perfil.b + 0.9, peca.perfil.h + 0.9
            m.bloco("fundacao", f"BLOCO/CÁLICE {peca.marca} (indicativo)", (x, y, -1.0 + 0.0), max(bx, 1.5), max(by, 1.5), 1.2, "Piso e fundações")

    pl = LG["platibanda"]
    m.pendente(f"Cobertura escondida (rev03): topo dos painéis solares junto ao P2 em +{pl['topo_painel_P2']:.3f}, {pl['folga_P2_mm']} mm abaixo da platibanda +10,00 (mínimo 150); junto ao P1 em +{pl['topo_painel_P1']:.3f}.")
    m.pendente("Modelo global integrado (OpenSeesPy, P-Δ, terças, correntes, X e laje como diafragma): pilares 0,66; terça mais carregada 0,97; ELS dentro da NBR 9062:2017 Tab. 7.")
    m.pendente("! Folga na cabeça dos PG-01 a PG-04 mantida em 2 cm (decisão de 20/10): a TS-01 desce ~30 mm (PG-01/PG-03) e ~20 mm (PG-02/PG-04) depois de montada — a viga pode encostar no PG.")
    m.pendente("rev09 (DEC-048/052): linha 2 sem TS-01 — W 200 × 15,0 contínua nos pilares e em 4 montantes W 150 no meio dos vãos sobre as VM do +7,30; terças no ST-W e mão-francesa MF-1 em toda terça.")
    m.pendente("rev09 (DEC-047/049/053/055): VM retangulares protendidas 30 × 75 com dente 45 × 40; escada interna e escada externa em L (fachada A) chegando no piso pronto +3,95.")
    m.pendente("DEC-059: portões da linha 4 livres até +7,50 — PG-01 a PG-04 apoiam a TS-01A (NEO-7 + graute após a montagem; fundo 7,497 na face do PG-01, dentro da tolerância de ±10 mm); placa PV-1 sobre o portão P19–D.")
    m.pendente("! Painéis solares adotados com 0,15 kN/m² e instalações 0,10 kN/m²: confirmar com o fornecedor.")
    m.pendente("rev09 (DEC-045): P6, P7 e P6 da linha 2 do R01 são os pilares da escada metálica (abertura só no +3,90).")
    m.pendente(f"I120 (DEC-054/058): h 120 com dente 78 × 35; eixo C com dois PC-03 40×40 (y 46,317 e 62,833), V406/V405/V404 de 16,517 m com {I1J['V406']['arranjo']['n_cord']} Ø12,7 e V407 com {I1J['V407']['arranjo']['n_cord']} Ø12,7; protensão limitada, liberação com fckj 50; consolo CP-I120 com mísula 49/39; NEO-2 fretado e PN-2 Ø25.")
    m.pendente("TS-01 sem dentes: apoio no recuo dos pilares laterais (NEO-4 + 2 PN-3 Ø25) e no topo da I120 / pilares centrais (NEO-3 + 2 PN-5 Ø20).")
    m.pendente("Ligações modeladas como na execução: ST-1P/ST-1P4/ST-1V/ST-1V-R/ST-1FL em chapa dobrada com esperas, porcas e grampos; correntes Ø10, tirantes rígidos L 51 e diagonais de ancoragem Ø16 (COB02); X Ø16 com esticador e OR-X nas ES-2; placas Trejor: CC-1 (CE-1 12,5 + CS-1 de fábrica) na face C e CS-1 soldado na obra nas faces laterais, NC-1, PT-1/PT-2; CL-P dos pilares dos portões. Rufos e telhas em camadas.")
    m.pendente("Fora do 3D (só nas pranchas): armaduras, cordoalhas, alças de içamento AL-1/AL-2/AL-3, grampos e porcas das placas, furos de içamento dos pilares.")
    cx = json.loads((AQ / "conexoes.json").read_text(encoding="utf-8")) if (AQ / "conexoes.json").exists() else []
    for c in cx:
        if not c["ok"] or c["obs"].startswith("!"):
            m.pendente("! " + f"{c['peca_a']} × {c['peca_b']}: {c['obs'].lstrip('! ')}")
    return m


def renomear_pecas(modelo):
    """rev08 (22/10/2026): nome de cada pilar e viga pela nomenclatura nova (P1…P33, V200…/V300…/V400…, sentido de
    leitura — pranchas/nomes.json). A parte da peça (cabeça, mesa, alma, ponta maciça) fica depois do nome."""
    import dataclasses
    sys.path.insert(0, "/home/claude/letsara/pranchas")
    import renomear as RN
    GV = {"Vigas centrais I120", "Vigas I90 de cobertura", "Vigas de borda", "Vigas de mezanino (retangulares protendidas)"}
    novos = []
    for p in modelo.pecas:
        nm = None
        if p.grupo == "Pilares":
            nm = RN.pilar_em(p.p0[0], p.p0[1], tol=0.5)
        elif p.grupo in GV:
            pts = getattr(p.perfil, "pontos", None)
            if pts and abs(p.p0[0] - p.p1[0]) < 1e-9 and abs(p.p0[1] - p.p1[1]) > 1e-9 and isinstance(p.perfil, PerfilPoligono):
                us = [u for u, _ in pts]
                xm, ym, zm = p.p0[0] + (min(us) + max(us)) / 2, (p.p0[1] + p.p1[1]) / 2, p.p0[2] + sum(v for _, v in pts) / len(pts)
            else:
                xm, ym, zm = (p.p0[0] + p.p1[0]) / 2, (p.p0[1] + p.p1[1]) / 2, (p.p0[2] + p.p1[2]) / 2
            niv = "cobertura" if p.grupo != "Vigas de mezanino (retangulares protendidas)" else ("+3,90" if zm < 5.5 else "+7,30")
            fam = {"Vigas centrais I120": ("V404", "V405", "V406", "V407"), "Vigas I90 de cobertura": ("TS",), "Vigas de borda": ("VB",),
                   "Vigas de mezanino (retangulares protendidas)": ("VM",)}[p.grupo]
            nm = RN.viga_em(niv, xm, ym, tol=0.8, marcas=fam)
        if not nm and isinstance(p.marca, str):                       # insertos e afins: texto com a nomenclatura nova
            novos.append(dataclasses.replace(p, marca=RN.renomear(p.marca), obs=RN.renomear(p.obs or "")))
            continue
        if nm:
            parte = ""
            for k in ("cabeça", "mesa inf.", "alma", "mesa sup.", "ponta maciça", "dente", "nariz", "maciço inf.", "maciço A", "maciço E", "maciço", "corpo"):
                if k in p.marca:
                    parte = " " + k
                    break
            fl = next((q["folha"] for q in RN._D["pecas"] if q["nome"] == nm), "")
            p = dataclasses.replace(p, marca=nm + parte, obs=RN.renomear((p.obs + f" · folha {fl}").strip(" ·")))
        novos.append(p)
    modelo.pecas[:] = novos


if __name__ == "__main__":
    saida = Path(sys.argv[1] if len(sys.argv) > 1 else AQ / "saidas")
    saida.mkdir(parents=True, exist_ok=True)
    modelo = montar()
    renomear_pecas(modelo)
    q = quantitativos(modelo)
    ifc = gravar_ifc(modelo, saida / "letsara.ifc")
    malha = ler_malha_ifc(ifc)
    pranchas = []
    pasta_pr = Path("/home/claude/letsara/pranchas")
    if pasta_pr.exists():
        import base64, io
        import pymupdf
        idx = json.loads((pasta_pr / "indice.json").read_text(encoding="utf-8"))          # rev08: ordem e títulos do índice da NG01
        LISTA = [(n if n.startswith("ND-LET-") else "ND-LET-" + n, idx.get("titulos", {}).get(n, "").lower()) for n in idx["ordem"]]
        for nome, desc in LISTA:
            arq = pasta_pr / f"{nome}.pdf"
            if not arq.exists():
                continue
            doc = pymupdf.open(arq)
            for k, pg in enumerate(doc):
                pix = pg.get_pixmap(dpi=int(1100 / pg.rect.width * 72))   # rev06c: 1100 px (rev11: página ≤ 16 MB)
                img = pix.tobytes("jpeg", jpg_quality=50)
                pranchas.append(dict(nome=nome + (f" ({k + 1}/{len(doc)})" if len(doc) > 1 else ""), desc=desc,
                                     img="data:image/jpeg;base64," + base64.b64encode(img).decode()))
    cx = json.loads((AQ / "conexoes.json").read_text(encoding="utf-8")) if (AQ / "conexoes.json").exists() else []
    gravar_visualizador(malha, saida / "letsara_3d.html", "Letsara · modelo estrutural e projetos",
                        "Pavilhão pré-moldado 39,50 × 79,35 m · Marques Engenharia e Construções · cobertura escondida na platibanda · pranchas e conferência de insertos",
                        pendencias=modelo.pendencias, quant=q, ocultas=("Placas de fechamento", "Telhas", "Rufos e acabamentos", "Piso e fundações"), pranchas=pranchas, conexoes=cx,
                        logo_cliente=AQ / "pranchas" / "logos" / "marques.jpg", cliente="Marques Engenharia e Construções",
                        autoria="")                                    # projeto da fábrica: sem marca da ND nas imagens (21/10/2026)
    for g, d in q.items():
        print(f"{g:26s} {d['pecas']:4d} peças  {d['volume_m3']:8.1f} m³")
    print("pendências:", len(modelo.pendencias), "->", saida)
