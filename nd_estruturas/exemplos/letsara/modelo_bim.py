"""Letsara — modelo BIM (IFC + página 3D) a partir das definições de projeto. Revisão de 12/10/2026 (tarde).

Rodar: PYTHONPATH=. python exemplos/letsara/modelo_bim.py [pasta_de_saida]
Saída (em saidas/, fora do git): letsara.ifc e letsara_3d.html (publicar a página como artefato para ver no celular).

Geometria = a mesma da checagem de ligações (ligacoes.json) e do modelo global:
- eixos Y (linhas 1 a 9) e X (A a E) do R01 como usados nos cálculos;
- rev03 (14/10/2026): cobertura rebaixada (TP40 + lã 40 + zipada + painéis solares) com ≥ 15 cm de folga à platibanda (+10,00);
- TS-01 sem dentes, apoiada no recuo dos pilares laterais e no topo da I130 / pilares centrais (neoprene + 2 pinos);
- vigas centrais I130 (h 1,30) com dente 78 × 35 nos consolos CP-I130;
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
from geometria import Y_LIN, X_FACH, X_EIXO, Y_P13, X_L2, X_L4, LINHA_PORTOES
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
Z_I130_TOPO, H_I130 = LG["Z_TOPO_I130"], LG["H_I130"]
CENTRAIS = [("P8A", Y_LIN[1]), ("P11", Y_LIN[3]), ("P13", Y_P13)]
I130_TRECHOS = [("V407", Y_LIN[1], Y_LIN[3]), ("V406", Y_LIN[3], Y_P13), ("V405", Y_P13, Y_LIN[8])]   # V405 vai até a linha 9 (P14)
NIVEIS_MEZ, H_LAJE = [3.15, 6.55], 0.20 + 0.05

I90 = PerfilI(h=0.90, b=0.40, tw=0.15, tf=0.15, nome="I90")
I130 = PerfilI(h=1.30, b=0.40, tw=0.15, tf=0.25, nome="I130")
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
I1J = json.loads((AQ / "i110_r01.json").read_text(encoding="utf-8"))               # rev06 (DEC-032): arranjo das cordoalhas da I130
GD_ = json.loads((AQ / "dentes.json").read_text(encoding="utf-8"))["I130"]["geometria"]
hC = lambda t: CONS[t]["h_total_m"]
sys.path.insert(0, "/home/claude/letsara/pranchas")
import fechamento as FCH
import geo_fixacao as GF
import numpy as np
from lajes_placas import paineis_mez
PAINEIS_MEZ = paineis_mez()[0]                                                   # placas: mesma fonte das pranchas PP (vistas do R01)



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


def suporte_st(m, marca, xw, y, zc, lado=-1, esperas=(), d=0.016, hef=0.150, grampo=False, aba=0.150):
    """ST-1P / ST-1V / ST-1V-R / ST-1F: chapa dobrada 9,5 × 220 — aba vertical 290 contra a alma da terça (lado `lado` da
    alma) e aba horizontal 150 sobre o concreto, presa em `esperas` (x, y relativos à alma e ao eixo do apoio)."""
    t = 0.0095
    caixa(m, marca, xw, xw + lado * t, y - 0.11, y + 0.11, zc, zc + 0.290, GM, obs="chapa dobrada 9,5 × 220 A36 galv., aba vertical 290")
    caixa(m, marca, xw + lado * t, xw + lado * aba, y - 0.11, y + 0.11, zc, zc + t, GM, obs=f"aba horizontal {aba*1000:.0f}, oblongos")
    for dx, dy in esperas:
        espera(m, marca.split()[0].replace("ST-1P4", "ES-1").replace("ST-1P", "ES-1").replace("ST-1V-R", "ES-1R").replace("ST-1V", "ES-1V").replace("ST-1F", "ES-1F"),
               xw + dx, y + dy, zc, d, hef, 0.12 if d < 0.02 else 0.12, grampo=grampo)


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
            zr = rec_vb(x0) if canto else REC[0 if sg > 0 else 1]
            nome = f"{lado}{'C' if canto else ''}-L{i}"
            m.pilar(nome, x0, y, 0.60, 0.40, Z_CALICE, zr, obs=f"40×60; cabeça recuada acima de +{zr:.2f}".replace(".", ","))
            if canto:      # canto: só o quarto externo (30 × 30) sobe
                m.pilar(nome + " cabeça", x0 - sg * 0.15, y + (-0.05 if i == 1 else 0.05), 0.30, 0.30, zr, TOPO_PLAT, obs="cabeça recuada nas duas faces internas")
            else:
                m.pilar(nome + " cabeça", x0 - sg * 0.15, y, 0.30, 0.40, zr, TOPO_PLAT, obs="cabeça recuada 40×30")
    # pilares das fachadas 1 e 9 (60 ⊥ fachada) com cabeça recuada acima da VB
    for j, x in enumerate(X_FACH[1:-1]):
        for nome, y, sg in ((["P3", "P4", "P5"][j], 0.0, 1), (["P3", "P14", "P5"][j], COMP, -1)):
            zr = rec_vb(x)
            m.pilar(f"{nome}-L{1 if sg > 0 else 9}", x, y, 0.40, 0.60, Z_CALICE, zr, obs="60 ⊥ fachada; cabeça recuada acima da VB")
            m.pilar(f"{nome}-L{1 if sg > 0 else 9} cabeça", x, y - sg * 0.15, 0.40, 0.30, zr, TOPO_PLAT, obs="cabeça 40×30")
    # centrais (R01): P8A 40×60, P11 40×40, P13 60×60 — topo +8,88 (topo da I130)
    for (marca, y), (bx, by) in zip(CENTRAIS, ((0.40, 0.60), (0.40, 0.40), (0.60, 0.60))):
        m.pilar(marca, X_C, y, bx, by, Z_CALICE, Z_I130_TOPO, obs=f"{bx*100:.0f}×{by*100:.0f}; apoio I130 / TS-01; topo em 2 níveis")
        if marca != "P13":                                     # rev04: metade do lado E 12 mm mais alta (assentos horizontais das TS-01)
            m.bloco("pilar", f"{marca} degrau do topo", (X_C + bx / 4, y, LG["Z_TOPO_I130_DIR"]), bx / 2, by, LG["DEGRAU_C"], "Pilares")
    for marca, x in (("P8", X_EIXO["B"]), ("P8B", X_EIXO["D"])):
        m.pilar(marca, x, Y_LIN[1], 0.40, 0.60, Z_CALICE, NIVEIS_MEZ[1], obs="mezanino 40×60")
    # pilares dos portões (linha 4), rev06 (DEC-024): cabeça a 2 cm do fundo da TS-01, ligada em y por 2 cantoneiras CL-P
    for nome, x, b_ in (("P9 (PG-01)", 9.87, 0.40), ("P10 (PG-02)", 15.195, 0.25), ("P10 (PG-04)", 24.305, 0.25), ("P12 (PG-03)", 29.63, 0.40)):
        zt_ = round(zf(x) - 0.02, 2)
        m.pilar(nome, x, Y_LIN[LINHA_PORTOES], b_, b_, Z_CALICE, zt_, obs=f"parede dos portões (vista C), topo +{zt_:.2f}; portão livre até +7,40")
        yl4 = Y_LIN[LINHA_PORTOES]
        for sx in (-1, 1):
            xf_ = x + sx * b_ / 2
            caixa(m, "CL-P L 102×102×9,5 L=250", xf_, xf_ + sx * 0.0095, yl4 - 0.125, yl4 + 0.125, zf(x) - 0.102, zf(x), GM, obs="aba no pilar, 1 M16 em oblongo vertical")
            caixa(m, "CL-P L 102×102×9,5 L=250", xf_, xf_ + sx * 0.102, yl4 - 0.125, yl4 + 0.125, zf(x) - 0.0095, zf(x), GM, obs="aba sob a TS-01A, 2 M16 nos IT-P")
            m.linear("inserto", "M16 8.8 (IL-1)", PerfilRetangular(0.016, 0.016), (xf_ - sx * 0.10, yl4, zf(x) - 0.06), (xf_ + sx * 0.03, yl4, zf(x) - 0.06), GM, material="aco")
            for dy in (-0.0975, 0.0975):
                barra_v(m, "M16 8.8 + IT-P (fundo da TS-01A)", xf_ + sx * 0.06, yl4 + dy, zf(x) - 0.03, zf(x) + 0.08, 0.016, GM)

    # 2. vigas centrais I130 (comprimentos do R01) e consolos CP-I130 / CV-TS
    zc = Z_I130_TOPO - H_I130 / 2
    meia = {Y_LIN[1]: 0.30, Y_LIN[3]: 0.20, Y_P13: 0.30, Y_LIN[8]: 0.30}
    z_ass_i110 = LG["Z_ASS_I130"]
    for marca, ya, yb in I130_TRECHOS:
        y0, y1 = ya + meia[ya] + 0.075, yb - meia[yb] - 0.075
        arr = I1J[marca]["arranjo"]
        ob_ = (f"L = {y1 - y0:.3f} m; protendida {arr['n_cord']} cord. Ø12,7 ({arr['n_inf']} embaixo + {arr['n_cord'] - arr['n_inf']} na mesa superior), "
               f"σpi {I1J[marca]['perdas'].get('sig_pi', 1453):.0f} MPa, fckj 45; dente {GD_['hd']} × {GD_['ln']}, maciço {GD_['x_mac'] / 1000:.2f} m (DEC-032)")
        ln_, mac_, hd_ = GD_["ln"] / 1000, GD_["x_mac"] / 1000, GD_["hd"] / 1000
        m.linear("viga", marca, I130, (X_C, y0 + mac_, zc), (X_C, y1 - mac_, zc), "Vigas centrais I130", obs=ob_)
        for ya_, yb_ in ((y0, y0 + mac_), (y1 - mac_, y1)):
            ys_ = (ya_ + ln_, yb_) if ya_ == y0 else (ya_, yb_ - ln_)
            m.linear("viga", f"{marca} ponta maciça", PerfilRetangular(0.40, H_I130), (X_C, ys_[0], zc), (X_C, ys_[1], zc), "Vigas centrais I130", obs=ob_)
            yn_ = (y0, y0 + ln_) if ya_ == y0 else (y1 - ln_, y1)
            m.linear("viga", f"{marca} nariz do dente", PerfilRetangular(0.40, hd_), (X_C, yn_[0], Z_I130_TOPO - hd_ / 2), (X_C, yn_[1], Z_I130_TOPO - hd_ / 2),
                     "Vigas centrais I130", obs=ob_)
        m.linear("viga", f"{marca} degrau do topo", PerfilRetangular(0.20, LG["DEGRAU_C"]), (X_C + 0.10, y0, Z_I130_TOPO + LG["DEGRAU_C"] / 2), (X_C + 0.10, y1, Z_I130_TOPO + LG["DEGRAU_C"] / 2),
                 "Vigas centrais I130", obs="rev04: topo em 2 níveis — metade do lado E 12 mm acima (apoio horizontal das TS-01)")
        for yy, sg in ((ya, 1), (yb, -1)):
            m.bloco("consolo", f"CP-I130 {marca}", (X_C, yy + sg * (meia[yy] + 0.20), z_ass_i110), 0.50, 0.40, hC("CP-I130"), "Consolos")
            m.bloco("inserto", "NEO-2 300×200×31 fretado", (X_C, yy + sg * (meia[yy] + 0.20), z_ass_i110 + 0.031), 0.30, 0.20, 0.031, "Pinos, tubos e neoprenes")
            m.bloco("inserto", "PN-2 pino Ø25 L=900 (350 no consolo; grauteado numa ponta só)", (X_C, yy + sg * (meia[yy] + 0.20), z_ass_i110 + 0.55), 0.025, 0.025, 0.90,
                    "Pinos, tubos e neoprenes")

    # 3. TS-01: I90 inclinada, sem dentes (rev03)
    # rev04: elevação real na posição montada — pontas a prumo, cunhas de 30 cm no fundo das pontas (face de apoio horizontal,
    # NBR 9062:2017 7.2.1.6), mesas, alma e maciços de 50 cm; ponta baixa sempre no lado A (as 14 peças são a mesma marca)
    CUN, HV, TI, TSUP, MAC = LG["CUNHA"], H_TS / C3, 0.15, 0.12, 0.50
    zt = lambda x: zf(x) + HV
    for i in range(2, 9):
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
            cont = [(a + u / 1000, z_vb(a) + v / 1000) for u, v in VG.montada(Lh)]       # pontas, recortes e tubos a prumo; dentes horizontais
            m.extrusao_y("viga", "VB", cont, y, 0.15, "Vigas de borda", obs=f"15×60 com dente 30 × 27, L = {b - a:.3f} m; caimento 3 %, faces de apoio horizontais")
            for xf, sg in ((fa, 1), (fb, -1)):
                xb_ = xf + sg * 0.135                                                   # centro do apoio
                zt = z_vb(xb_) + 0.29                                                   # topo HORIZONTAL do CP-VB = face do dente − neoprene
                m.bloco("consolo", "CP-VB 15×27×29", (xf + sg * 0.135, y, zt), 0.27, 0.15, 0.29, "Consolos")
                m.bloco("inserto", "NEO-6 100×100×10", (xb_, y, zt + 0.01), 0.10, 0.10, 0.01, "Pinos, tubos e neoprenes")
                m.bloco("inserto", "PN-6 Ø20 roscado + porca e contraporca (nicho grauteado só numa ponta; a outra livre — DEC-033)",
                        (xb_, y, zt + 0.01 + 0.30 - 0.03), 0.02, 0.02, 0.58, "Pinos, tubos e neoprenes")

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
            for k in range(n_v):
                e0 = EXT_F if k == 0 else A_TR
                e1 = EXT_F if k == n_v - 1 else A_TR
                dk = t_z if k % 2 else 0.0                           # vãos alternados: perfil encaixado por fora no transpasse
                ya, yb = Y_LIN[k] - e0, Y_LIN[k + 1] + e1
                pk = next(p_ for p_ in PC_["por_vao"] if p_["vao"] == f"{k+1}-{k+2}")
                m.extrusao_y("terca", f"Z302 vão {k+1}-{k+2} L={pk['L_mm']}", z_contorno(xw + dk, zb + dk), (ya + yb) / 2, yb - ya,
                             "Terças metálicas", material="aco", obs="Z 302×90/82×2,30 METSEC, contínua por transpasse")
            for j, yl in enumerate(Y_LIN):
                ys = (-0.06, 0.06) if j in (0, n_v) else (-0.06, 0.06, -(A_TR - B_TR), A_TR - B_TR)
                for dy in ys:
                    for zz in (ZF1, ZF2):
                        m.linear("inserto", "M12 8.8 (apoio/emenda da terça)", PARAF, (xw - 0.012, yl + dy, zb + zz), (xw + 0.016, yl + dy, zb + zz),
                                 "Parafusos da cobertura", material="aco")
                if j in (0, n_v):
                    zc = zb - 0.010
                    if xw > LARG - 0.325 - 0.04:                     # última terça do lado E: no recuo do pilar de canto (ST-1F espelhado)
                        suporte_st(m, f"ST-1F (pilar de canto, eixo {j+1})", xw, yl, zc, lado=+1, esperas=((0.075, 0.0), (0.135, 0.0)), d=0.020, hef=0.150)
                    elif j == n_v:                                   # eixo 9: ST-1V-R, 2 M20 hef 400 + grampo
                        suporte_st(m, "ST-1V-R (VB eixo 9)", xw, yl, zc, esperas=((-0.045, 0.0), (-0.105, 0.0)), d=0.020, hef=0.400, grampo=True)
                    else:
                        suporte_st(m, "ST-1V (VB eixo 1)", xw, yl, zc, esperas=((-0.045, 0.0), (-0.105, 0.0)), d=0.016, hef=0.150)
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
            m.linear("placa", nome_, PerfilRetangular(bfx - 0.002, dz1 - dz0, nome_), (xa_, y, AC.z_terca_topo(xa_) + pz), (xb_, y, AC.z_terca_topo(xb_) + pz), grp_, material="aco")
    for xt_ in LG["x_tercas_esq"] + [x + (2 * X_EIXO["C"] - LG["X_PONTA_CEN"]) - LG["X_PONTA_ESQ"] for x in LG["x_tercas_esq"]]:
        xc_ = xt_ - 0.027 - 0.045                         # cartola centrada na aba superior (90) da terça
        m.linear("placa", "perfil cartola #0,65", PerfilRetangular(0.12, 0.04, "cartola"), (xc_, y0_, AC.z_terca_topo(xc_) + 0.06), (xc_, y1_, AC.z_terca_topo(xc_) + 0.06), "Telhas", material="aco")
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
    tre = [(PIL_Y[i] + 0.20, PIL_Y[i + 1] - 0.20) for i in range(len(PIL_Y) - 1)]
    for ya, yb in tre:
        rufo_y("RF-2", ya, yb); rufo_y("RF-3", ya, yb); rufo_y("CR-1", ya, yb)
    for yp in PIL_Y:
        rufo_y("RF-2C", yp - 0.30, yp + 0.30); rufo_y("RF-3P", yp - 0.30, yp + 0.30)
        rufo_y("RF-1C", yp - 0.30, yp + 0.30, lambda u, v: (AC.X_PLACA_A - 0.100 + u, v))
        rufo_y("RF-1C", yp - 0.30, yp + 0.30, lambda u, v: (AC.X_PLACA_E + 0.100 - u, v))
    rufo_y("PG-1", y0_, y1_)
    rufo_y("RF-1", AC.Y_PLACA_1 - 0.10, AC.Y_PLACA_9 + 0.10, lambda u, v: (AC.X_PLACA_A - 0.100 + u, v))
    rufo_y("RF-1", AC.Y_PLACA_1 - 0.10, AC.Y_PLACA_9 + 0.10, lambda u, v: (AC.X_PLACA_E + 0.100 - u, v))
    zl_ = AC.z_zip(LARG / 2) + AC.PAC["zipada"]
    za_r, zb_r = AC.z_zip(xa_) + AC.PAC["zipada"], AC.z_zip(xb_) + AC.PAC["zipada"]
    for yface, sg in ((AC.Y_PLACA_1, 1), (AC.Y_PLACA_9, -1)):
        for mk in ("RF-4", "RF-4C", "RB-1/2"):
            rufo_x(mk, xa_, xb_, za_r, zb_r, lambda u, v, yf=yface, s_=sg: (yf + s_ * u, v - zl_))
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
                    pa, pb = (x1, ya, zf(x1) + H_TS + dz), (x2, yb, zf(x2) + H_TS + dz)
                    m.linear("inserto", "X Ø16 A36 (trecho A + B)", BAR16, pa, pb, "Contraventamento", material="aco")
                    L_ = math.dist(pa, pb); ux, uy = (pb[0] - pa[0]) / L_, (pb[1] - pa[1]) / L_
                    e0 = [pa[i] + (pb[i] - pa[i]) * 9.0 / L_ for i in range(3)]
                    m.linear("inserto", "esticador M16", PerfilRetangular(0.036, 0.036), e0, [e0[i] + (pb[i] - pa[i]) * 0.2 / L_ for i in range(3)],
                             "Contraventamento", material="aco")
                    zc_b = zf(x2) + H_TS if k + 1 < len(Y_LIN) - 1 else zf(x2) + H_TS     # VB do eixo 9: topo da VB = topo da TS-01
                    orelha(m, x1, ya, zf(x1) + H_TS, ux, uy, dz)
                    orelha(m, x2, yb, zc_b, -ux, -uy, dz)
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
    m.extrusao_y("placa", "CA-1 calha 300×150 chapa galv. 1,25", cal, COMP / 2, COMP, "Calha e descidas", material="aco", obs="NBR 10844; i = 0,5 % para as saídas")
    for yl in Y_LIN:
        yd = yl + (0.35 if yl < COMP else -0.35)
        m.linear("pilar", "DE-1 descida Ø200 (envelope)", PerfilRetangular(0.20, 0.20, "Ø200"), (0.17, yd, 0.0), (0.17, yd, zt_c - 0.15), "Calha e descidas", material="aco")

    # 5. mezanino (linhas 1–2), rev04: VM em MEIO VASO (alma do lado da borda, aba para dentro, topo = apoio da laje) com dente
    #    Gerber nas pontas maciças; consolos CP-MEZ com fundo alinhado; 2º estágio (obra, com a capa) e alças N9 saindo da peça;
    #    neoprene NEO-5, pino PN-1, cantoneira antigiro CT-1; folga real de 3 cm na ponta (NBR 9062:2017 3.1)
    VMP = json.loads((AQ / "vm_meio_vaso.json").read_text(encoding="utf-8"))["premissas"]
    hv, ba, bb, ha = VMP["h_pm"], VMP["b_alma"], VMP["b_aba"], VMP["h_aba"]
    DT_ = VMP["dente"]
    hd, ln, rec, hcm, prj, mac = DT_["hd"], DT_["ln"], DT_["recorte"], DT_["consolo_h"], DT_["consolo_proj"], DT_["macico"]
    bt = ba + bb
    FOL = 0.03
    faces = [(0.30, X_EIXO["B"] - 0.20), (X_EIXO["B"] + 0.20, X_C - 0.20), (X_C + 0.20, X_EIXO["D"] - 0.20), (X_EIXO["D"] + 0.20, LARG - 0.30)]
    E2, VMG = "Concreto de 2º estágio (obra, com a capa)", "Vigas de mezanino (meio vaso)"
    for nivel in NIVEIS_MEZ:
        za = nivel - H_LAJE - 0.01                          # topo da peça = apoio da laje (fita de neoprene 1 cm)
        zb = za - hv
        for y, so in ((Y_LIN[0], -1), (Y_LIN[1], 1)):      # so: lado da borda (alma) — linha 1 para fora (−y), linha 2 para o pavilhão (+y)
            y_alma = y + so * (bt / 2 - ba / 2)
            y_aba = y - so * (bt / 2 - bb / 2)
            for fa, fb in faces:
                xa, xb = fa + FOL, fb - FOL
                L_ = xb - xa
                mk = "VM-01" if fa < 1 or fb > LARG - 1 else "VM-02"
                ob = f"meio vaso {bt*100:.0f}×{hv*100:.0f}, dente {hd*100:.0f}×{ln*100:.0f}, L = {L_:.2f} m"
                m.linear("viga", f"{mk} alma {nivel:+.2f}", PerfilRetangular(ba, hv - rec), (xa, y_alma, zb + rec + (hv - rec) / 2), (xb, y_alma, zb + rec + (hv - rec) / 2), VMG, obs=ob)
                m.linear("viga", f"{mk} alma inf. {nivel:+.2f}", PerfilRetangular(ba, rec), (xa + ln, y_alma, zb + rec / 2), (xb - ln, y_alma, zb + rec / 2), VMG, obs=ob)
                m.linear("viga", f"{mk} aba {nivel:+.2f}", PerfilRetangular(bb, ha), (xa, y_aba, za - ha / 2), (xb, y_aba, za - ha / 2), VMG, obs=ob)
                for x0_, x1_ in ((xa, xa + mac), (xb - mac, xb)):      # pontas maciças (enchimento sob a aba) e nariz do dente
                    m.linear("viga", f"{mk} maciço {nivel:+.2f}", PerfilRetangular(bb, hd - ha), (x0_, y_aba, zb + rec + (hd - ha) / 2), (x1_, y_aba, zb + rec + (hd - ha) / 2), VMG, obs="ponta maciça")
                    xr0, xr1 = (xa + ln, xa + mac) if x0_ == xa else (xb - mac, xb - ln)
                    m.linear("viga", f"{mk} maciço inf. {nivel:+.2f}", PerfilRetangular(bb, rec), (xr0, y_aba, zb + rec / 2), (xr1, y_aba, zb + rec / 2), VMG, obs="ponta maciça")
                m.linear("viga", f"2º estágio {nivel:+.2f}", PerfilRetangular(bt - 0.10, 0.21), (fa, y + so * 0.05, za + 0.105), (fb, y + so * 0.05, za + 0.105), E2,
                         obs="C30, concretado com a capa por quem faz a capa")
                xx = xa + 0.15
                while xx < xb - 0.10:                                      # alças N9 da alma saindo 20 cm (a cada 15 cm; uma a cada 30 cm no 3D)
                    m.bloco("inserto", "alça N9 Ø10", (xx, y_alma, za + 0.20), 0.012, ba - 0.06, 0.20, "Alças N9 (2º estágio)")
                    xx += 0.30
                for xf, sg in ((fa, 1), (fb, -1)):
                    m.bloco("consolo", f"CP-MEZ 40×{prj*100:.0f}×{hcm*100:.0f}", (xf + sg * prj / 2, y, zb + hcm), prj, bt, hcm, "Consolos")
                    m.bloco("inserto", "NEO-5 300×150×10", (xf + sg * 0.186, y, zb + hcm + 0.01), 0.15, 0.30, 0.01, "Pinos, tubos e neoprenes")
                    m.bloco("inserto", "PN-1 pino Ø20 (VM)", (xf + sg * 0.186, y, zb + hcm + 0.40), 0.02, 0.02, 0.70, "Pinos, tubos e neoprenes")
                    m.bloco("inserto", "CT-1 L152×102×12,5", (xf + sg * 0.076, y + so * (bt / 2 + 0.006), za), 0.152, 0.0125, 0.15, "Insertos metálicos")
                    m.bloco("inserto", "graute junta 3 cm", (xf + sg * FOL / 2, y, za), FOL, bt, hd, E2)
        for x0, b_, mk in PAINEIS_MEZ:                              # mesma paginação da ND-LET-LA01 (30 LA-01 + 2 LA-02 por nível)
            x = (x0 + b_ / 2) / 1000
            perf = LAJE if b_ == 1250 else PerfilRetangular(0.70, H_LAJE, "Laje alveolar 70")
            m.linear("laje", f"{mk} {nivel:+.2f}", perf, (x, Y_LIN[0] + 0.10, nivel - H_LAJE / 2), (x, Y_LIN[1] - 0.10, nivel - H_LAJE / 2), "Laje alveolar")

    # 6. placas de fechamento: as mesmas peças das pranchas PP (fechamento.py, vistas do R01)
    PL = PerfilRetangular(0.10, 1.25, "Placa 125×10 protendida")
    o_ext, o_c = 0.30 + 0.025 + 0.05, 0.20 + 0.025 + 0.05
    pos = {"A": ("x", COMP + o_ext), "I": ("x", -o_ext), "G": ("x", Y_LIN[1] + o_ext), "C": ("x", Y_LIN[LINHA_PORTOES] + o_c),
           "B": ("y", -o_ext), "E": ("y", -o_ext), "H": ("y", -o_ext), "D": ("y", LARG + o_ext), "F": ("y", LARG + o_ext), "J": ("y", LARG + o_ext)}
    for V, (pecas, ca1, _) in FCH.DADOS.items():
        ax, c = pos[V]
        for pc in pecas:
            s0, s1, z = pc["s0"] / 1000, pc["s1"] / 1000, (pc["z0"] + pc["z1"]) / 2000
            p0, p1 = ((s0, c, z), (s1, c, z)) if ax == "x" else ((c, s0, z), (c, s1, z))
            m.linear("placa", f"{pc['id']} (vista {V})", PL, p0, p1, "Placas de fechamento", obs=f"L = {pc['L']} mm; apoio: {pc['apoio']}")
    # rev04: sem vigas de travamento VT (não há ponte rolante — NBR 9062:2017 5.1.2.1 e regra ND)

    # 7. insertos e ligações (conferência no 3D)
    INS, PIN = "Insertos metálicos", "Pinos, tubos e neoprenes"
    for i in range(2, 9):
        y = Y_LIN[i - 1]
        AP, PT = LG["apoios_ts"], LG["PINO_TS"]                 # rev04: assentos horizontais; pinos a 7,75 cm das 4 pontas
        for (xn, z_as), xpin, nome_, neo, dpin in (((AP["P1"]["x_neo"], AP["P1"]["z"]), PONTAS[0][0] + PT, "2 PN-3 Ø25 + NEO-4", (0.20, 0.30), 0.025),
                                                  ((AP["centro_esq"]["x_neo"], AP["centro_esq"]["z"]), PONTAS[0][1] - PT, "2 PN-5 Ø20 + NEO-3", (0.10, 0.30), 0.020),
                                                  ((AP["centro_dir"]["x_neo"], AP["centro_dir"]["z"]), PONTAS[1][0] + PT, "2 PN-5 Ø20 + NEO-3", (0.10, 0.30), 0.020),
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
    def rasgo(V, c):
        """normal da parede: (eixo do pilar, sentido para fora) a partir da posição da placa."""
        return (1 if (c > COMP / 2 if pos[V][0] == "x" else c > LARG / 2) else -1)
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
            if rot_ != "porta":
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
            for (t, d) in ((pc["s0"], 1), (pc["s1"], -1)):
                uc = t + d * FCH.X_CS
                if (round(uc), round(pc["z0"] + FCH.Z_NC)) not in cons:
                    continue                                               # ponta da porta: sem console
                u = uc / 1000
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
                        cx(ua, ub, -y1_ / 1000, -y0_ / 1000, zt + z0_ / 1000, zt + z1_ / 1000, mk_, grupo,
                           obs=("solda de fábrica do CC-1, concretado com o pilar (DEC-031)" if cc_ else "solda de campo filete 5 E70XX nos 2 lados verticais (DEC-030)") if so.nome == "costas" else "")
                # CE-1 do pilar (uma por pilar e fiada)
                s_ax = min((sp for sp, _, _ in pil), key=lambda sp: abs(sp - uc)) / 1000
                bw = next(b_ for sp, b_, _ in pil if abs(sp / 1000 - s_ax) < 1e-6) / 1000
                if (s_ax, pc["k"]) not in ce_feitas:
                    ce_feitas.add((s_ax, pc["k"]))
                    zce = z0p + FCH.Z_CE / 1000
                    ub = min(0.19, bw / 2 - 0.01)
                    tce = GF.TCE / 1000
                    cx(s_ax - ub, s_ax + ub, 0.0, tce, zce - 0.165, zce + 0.165, f"CE-1 chapa de espera 380×330×{GF.TCE:g}".replace(".", ","), GE)
                    for du in (-0.12, 0.12):
                        for dz in (-0.14, 0.14):
                            cx(s_ax + du - 0.008, s_ax + du + 0.008, tce, tce + 0.150, zce + dz - 0.008, zce + dz + 0.008, "CE-1 pino Ø16 × 150 c/ cabeça", GE)
            # pinos PT-1 (junta de baixo) ou travas de pé PT-2
            if pc["trava"] == "PT-1":
                for xp in (pc["s0"] + FCH.X_PT(pc["L"]), pc["s1"] - FCH.X_PT(pc["L"])):
                    u = xp / 1000
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
    m.linear("laje", "PISO e=15 (indicativo)", PerfilRetangular(LARG + 1.0, 0.15), (LARG / 2, -0.5, -0.075), (LARG / 2, COMP + 0.5, -0.075), "Piso e fundações")
    for peca in list(m.pecas):
        if peca.tipo == "pilar":
            x, y, _ = peca.p0
            bx, by = peca.perfil.b + 0.9, peca.perfil.h + 0.9
            m.bloco("fundacao", f"BLOCO/CÁLICE {peca.marca} (indicativo)", (x, y, -1.0 + 0.0), max(bx, 1.5), max(by, 1.5), 1.2, "Piso e fundações")

    pl = LG["platibanda"]
    m.pendente(f"Cobertura escondida (rev03): topo dos painéis solares junto ao P2 em +{pl['topo_painel_P2']:.3f}, {pl['folga_P2_mm']} mm abaixo da platibanda +10,00 (mínimo 150); junto ao P1 em +{pl['topo_painel_P1']:.3f}.")
    m.pendente("Modelo global integrado (OpenSeesPy, P-Δ, terças, correntes, X e laje como diafragma): pilares 0,66; terça mais carregada 0,97; ELS dentro da NBR 9062:2017 Tab. 7.")
    m.pendente("! Folga na cabeça dos PG-01 a PG-04 mantida em 2 cm (decisão de 20/10): a TS-01 desce ~30 mm (PG-01/PG-03) e ~20 mm (PG-02/PG-04) depois de montada — a viga pode encostar no PG.")
    m.pendente("! VB com o PN-6 grauteado só numa ponta (decisão de 20/10): o modelo global reprova só o ST-1P da 1ª terça do beiral no eixo 2 (1,06). Proposto o ST-1P4 com 4 esperas (0,26), no 3D em laranja — falta conferir o cone de arrancamento do grupo e a aprovação do Nathan.")
    m.pendente("Dente Gerber da VM aceito com a carga a 1,0 m (Vu 533 kN = 1,10 Fd, decisão de 20/10).")
    m.pendente("! Painéis solares adotados com 0,15 kN/m² e instalações 0,10 kN/m²: confirmar com o fornecedor.")
    m.pendente("! Pilares P6 e P7 do R01 (anexo) sem função definida: fora do modelo e das pranchas até confirmação.")
    m.pendente("I130 (DEC-032): V405/V406 com 30 cordoalhas (28 embaixo + 2 na mesa), V407 com 20; σpi 1453 MPa, fckj 45; NEO-2 300×200×31 fretado e PN-2 Ø25 grauteado numa ponta só.")
    m.pendente("TS-01 sem dentes: apoio no recuo dos pilares laterais (NEO-4 + 2 PN-3 Ø25) e no topo da I130 / pilares centrais (NEO-3 + 2 PN-5 Ø20).")
    m.pendente("Ligações modeladas como na execução: ST-1P/ST-1P4/ST-1V/ST-1V-R/ST-1F em chapa dobrada com esperas, porcas e grampos; correntes Ø10, tirantes rígidos L 51 e diagonais de ancoragem Ø16 (COB02); X Ø16 com esticador e OR-X nas ES-2; placas Trejor: CC-1 (CE-1 12,5 + CS-1 de fábrica) na face C e CS-1 soldado na obra nas faces laterais, NC-1, PT-1/PT-2; CL-P dos pilares dos portões. Rufos e telhas em camadas.")
    m.pendente("Fora do 3D (só nas pranchas): armaduras, cordoalhas, alças de içamento AL-1/AL-2/AL-3, grampos e porcas das placas, furos de içamento dos pilares.")
    cx = json.loads((AQ / "conexoes.json").read_text(encoding="utf-8")) if (AQ / "conexoes.json").exists() else []
    for c in cx:
        if not c["ok"] or c["obs"].startswith("!"):
            m.pendente("! " + f"{c['peca_a']} × {c['peca_b']}: {c['obs'].lstrip('! ')}")
    return m


if __name__ == "__main__":
    saida = Path(sys.argv[1] if len(sys.argv) > 1 else AQ / "saidas")
    saida.mkdir(parents=True, exist_ok=True)
    modelo = montar()
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
                pix = pg.get_pixmap(dpi=int(1300 / pg.rect.width * 72))   # rev06c: 1300 px (página ≤ 16 MB)
                img = pix.tobytes("jpeg", jpg_quality=55)
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
