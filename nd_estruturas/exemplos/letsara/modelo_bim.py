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

from nd_estruturas.bim import (ModeloBIM, PerfilI, PerfilRetangular, gravar_ifc, gravar_visualizador,
                               ler_malha_ifc, quantitativos)

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
hC = lambda t: CONS[t]["h_total_m"]
sys.path.insert(0, "/home/claude/letsara/pranchas")
import fechamento as FCH
from lajes_placas import paineis_mez
PAINEIS_MEZ = paineis_mez()[0]                                                   # placas: mesma fonte das pranchas PP (vistas do R01)


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
        for sx in (-1, 1):
            m.bloco("inserto", "CL-P L 102×102×9,5 L=250 (ligação em y à TS-01)", (x + sx * (b_ / 2 + 0.005), Y_LIN[LINHA_PORTOES], zf(x)), 0.010, 0.25, 0.102, "Insertos metálicos")

    # 2. vigas centrais I130 (comprimentos do R01) e consolos CP-I130 / CV-TS
    zc = Z_I130_TOPO - H_I130 / 2
    meia = {Y_LIN[1]: 0.30, Y_LIN[3]: 0.20, Y_P13: 0.30, Y_LIN[8]: 0.30}
    z_ass_i110 = LG["Z_ASS_I130"]
    for marca, ya, yb in I130_TRECHOS:
        y0, y1 = ya + meia[ya] + 0.075, yb - meia[yb] - 0.075
        m.linear("viga", marca, I130, (X_C, y0, zc), (X_C, y1, zc), "Vigas centrais I130",
                 obs=f"L = {y1 - y0:.3f} m; protendida 26 cord. Ø12,7 (V407: 16) + 4 Ø20 na mesa superior; dente 780 × 350")
        m.linear("viga", f"{marca} degrau do topo", PerfilRetangular(0.20, LG["DEGRAU_C"]), (X_C + 0.10, y0, Z_I130_TOPO + LG["DEGRAU_C"] / 2), (X_C + 0.10, y1, Z_I130_TOPO + LG["DEGRAU_C"] / 2),
                 "Vigas centrais I130", obs="rev04: topo em 2 níveis — metade do lado E 12 mm acima (apoio horizontal das TS-01)")
        for yy, sg in ((ya, 1), (yb, -1)):
            m.bloco("consolo", f"CP-I130 {marca}", (X_C, yy + sg * (meia[yy] + 0.20), z_ass_i110), 0.50, 0.40, hC("CP-I130"), "Consolos")

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
                m.bloco("inserto", "PN-6 Ø20 roscado + porca", (xb_, y, zt + 0.01 + 0.30 - 0.03), 0.02, 0.02, 0.58, "Pinos, tubos e neoprenes")

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
                    m.bloco("inserto", "ST-1V (chapa dobrada) nas esperas ES-1V da VB", (xw - 0.075, yl, zb - 0.010 + 0.30), 0.15, 0.22, 0.30, "Insertos metálicos")
    for k in range(int(COMP // 1.0)):
        y = 0.5 + k * 1.0
        xa_, xb_ = 0.25, LARG - 0.06                          # rev06: telha entra 150 na calha (eixo A); no eixo E sob o rufo RF-3
        z0, z1 = zf(xa_) + H_TS + 0.010 + 0.302 + 0.0046 + TELHA.h / 2, zf(xb_) + H_TS + 0.010 + 0.302 + 0.0046 + TELHA.h / 2
        m.linear("placa", "telha", TELHA, (xa_, y, z0), (xb_, y, z1), "Telhas", material="aco")
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
                    m.linear("inserto", "X Ø16 A36 + esticador", BAR16, (x1, ya, zf(x1) + H_TS + dz), (x2, yb, zf(x2) + H_TS + dz), "Contraventamento", material="aco")
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
        for xa, _ in PONTAS:
            for k, s_ in enumerate(LG["s_tercas"]):
                x = xa + s_ * C3 - 0.027
                m.bloco("inserto", "ST-1P (chapa dobrada) nas esperas ES-1", (x - 0.075, y, zf(x) + H_TS + 0.15), 0.15, 0.22, 0.30, INS)
    for V, (pecas, ca1, _) in FCH.DADOS.items():                            # CL-1 (trilho TR-1 do pilar + bucha BR-1 da placa), sem solda
        ax, c = pos[V]
        for pc in pecas:
            for s in (pc["s0"] / 1000 + 0.255, pc["s1"] / 1000 - 0.255):
                z = pc["z1"] / 1000 - 0.15
                pt = (s, c, z) if ax == "x" else (c, s, z)
                m.bloco("inserto", "CL-1 L 102×102×12,5 (TR-1 + BR-1)", pt, 0.15, 0.10, 0.10, INS)
        for (s, z0) in ca1:
            pt = (s / 1000, c, z0 / 1000) if ax == "x" else (c, s / 1000, z0 / 1000)
            m.bloco("inserto", "CA-1 L 152×102×19 (2 M20 em luvas IB-1)", pt, 0.30, 0.15, 0.10, INS)

    # 8. piso e fundações (indicativos): piso de concreto 15 cm e blocos de fundação com cálice sob cada pilar
    m.linear("laje", "PISO e=15 (indicativo)", PerfilRetangular(LARG + 1.0, 0.15), (LARG / 2, -0.5, -0.075), (LARG / 2, COMP + 0.5, -0.075), "Piso e fundações")
    for peca in list(m.pecas):
        if peca.tipo == "pilar":
            x, y, _ = peca.p0
            bx, by = peca.perfil.b + 0.9, peca.perfil.h + 0.9
            m.bloco("fundacao", f"BLOCO/CÁLICE {peca.marca} (indicativo)", (x, y, -1.0 + 0.0), max(bx, 1.5), max(by, 1.5), 1.2, "Piso e fundações")

    pl = LG["platibanda"]
    m.pendente(f"Cobertura escondida (rev03): topo dos painéis solares junto ao P2 em +{pl['topo_painel_P2']:.3f}, {pl['folga_P2_mm']} mm abaixo da platibanda +10,00 (mínimo 150); junto ao P1 em +{pl['topo_painel_P1']:.3f}.")
    m.pendente("Pórtico global rev04 (OpenSeesPy, P-Δ, sem VT): ELU ok, γz até 1,09; ELS frequente 9,9 mm em x — passa NBR 9062:2017 Tab. 7 (H/400 e Hi/750; uso 40 %).")
    m.pendente("! Pé-direito: fundo da TS-01 em +7,19 junto ao eixo A (antes +7,46); mezanino superior (+6,55) com fundo das terças a +8,10 junto ao eixo A — conferir o uso.")
    m.pendente("! Painéis solares adotados com 0,15 kN/m² e instalações 0,10 kN/m²: confirmar com o fornecedor.")
    m.pendente("! Pilares P6 e P7 do R01 (anexo) sem função definida: fora do modelo e das pranchas até confirmação.")
    m.pendente("TS-01 sem dentes: apoio 27,5 cm no recuo dos pilares laterais (NEO-4 + 2 PN-3 Ø25) e 16,25 cm no topo da I130 / pilares centrais (NEO-3 + 2 PN-5 Ø20).")
    m.pendente("Todas as ligações metálicas parafusadas (sem solda): ST-1P nas esperas ES-1 (4 M12 pelas 2 terças do transpasse), ST-1V nas ES-1V das VB, OR-X nas ES-2, sem mão-francesa; placas com trilho TR-1 + bucha BR-1 + CL-1 e consolo CA-1 parafusado.")
    m.pendente("Terças, laje, consolos e pacote da cobertura como envelope; X Ø16 modelado (barras retas de orelha a orelha); correntes, tirantes, rufos e orelhas só nas pranchas COB01 a COB03.")
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
        LISTA = [("ND-LET-LOC01", "locação de pilares e vigas"), ("ND-LET-CT01", "cortes da estrutura"), ("ND-LET-MON01", "montagem da cobertura"), ("ND-LET-MON02", "montagem do mezanino"),
                 ] + [(f"ND-LET-AR-PIL-{k:02d}", f"armaduras dos pilares — folha {k} de 6 (padrão de armação)") for k in range(1, 7)] + [(f"ND-LET-AR-VIG-{k:02d}", f"armaduras das vigas — {t}") for k, t in enumerate(("TS-01", "I130", "VM", "VB"), 1)] + [] + [(f"ND-LET-{m.replace('-', '')}", f"pilar {m} (família 40×60)") for m in ("PL-01", "PL-02", "PL-03", "PL-04", "PL-05", "PL-06", "PL-07", "PL-08", "PL-09", "PL-10", "PL-11", "PL-12", "PF-01", "PF-02", "PF-03", "PF-04", "PF-05", "PF-06")] + [ ("ND-LET-PC01", "pilar central PC-01 (P8A)"), ("ND-LET-PC02", "pilar central PC-02 (P11)"), ("ND-LET-PC03", "pilar central PC-03 (P13)"),
                 ("ND-LET-PM01", "pilares do mezanino PM-01"), ("ND-LET-PG01", "pilar do portão PG-01 (P9)"), ("ND-LET-PG02", "pilar do portão PG-02 (P10a)"), ("ND-LET-PG03", "pilar do portão PG-03 (P12)"), ("ND-LET-PG04", "pilar do portão PG-04 (P10b)"), ("ND-LET-TS01-1", "TS-01 fôrma"), ("ND-LET-TS01-2", "TS-01 armação e protensão"), ("ND-LET-TS01-3", "TS-01 esperas e peças de ligação"), ("ND-LET-COB01", "cobertura metálica: enterçamento Z contínuo, apoios ST-1P/ST-1V e emendas por transpasse (sem solda)"), ("ND-LET-COB02", "cobertura metálica: contraventamento X, correntes, tirantes"), ("ND-LET-COB03", "calha do eixo A, descidas e rufos"),
                 ("ND-LET-I130", "vigas centrais I130 V405/406/407"), ("ND-LET-VB01", "vigas de borda VB-01 a VB-04"), ("ND-LET-VM01", "vigas do mezanino VM-01 e VM-02 (meio vaso) — fôrma"), ("ND-LET-VM02", "vigas do mezanino — 2º estágio, apoio e insertos"),
                 ("ND-LET-LA01", "lajes alveolares do mezanino"), ("ND-LET-CM01", "placas de fechamento — locação e ordem das vistas (R01)"),
                 ("ND-LET-PP00", "placa protendida típica — fôrma, protensão, insertos, ligações"), ("ND-LET-PP-I", "placas da vista I (produção e montagem)"),
                 ("ND-LET-PP-HJ", "placas das vistas H e J"), ("ND-LET-PP-G", "placas da vista G"), ("ND-LET-PP-EF", "placas das vistas E e F"),
                 ("ND-LET-PP-C", "placas da vista C (portões)"), ("ND-LET-PP-B", "placas da vista B"), ("ND-LET-PP-D", "placas da vista D"),
                 ("ND-LET-PP-A", "placas da vista A")]
        for nome, desc in LISTA:
            arq = pasta_pr / f"{nome}.pdf"
            if not arq.exists():
                continue
            doc = pymupdf.open(arq)
            for k, pg in enumerate(doc):
                pix = pg.get_pixmap(dpi=int(1800 / pg.rect.width * 72))
                img = pix.tobytes("jpeg", jpg_quality=72)
                pranchas.append(dict(nome=nome + (f" ({k + 1}/{len(doc)})" if len(doc) > 1 else ""), desc=desc,
                                     img="data:image/jpeg;base64," + base64.b64encode(img).decode()))
    cx = json.loads((AQ / "conexoes.json").read_text(encoding="utf-8")) if (AQ / "conexoes.json").exists() else []
    gravar_visualizador(malha, saida / "letsara_3d.html", "Letsara · modelo estrutural e projetos",
                        "Pavilhão pré-moldado 39,50 × 79,35 m · Marques Engenharia e Construções · cobertura escondida na platibanda · pranchas e conferência de insertos",
                        pendencias=modelo.pendencias, quant=q, ocultas=("Placas de fechamento", "Telhas", "Piso e fundações"), pranchas=pranchas, conexoes=cx,
                        logo_cliente=AQ / "pranchas" / "logos" / "marques.jpg", cliente="Marques Engenharia e Construções")
    for g, d in q.items():
        print(f"{g:26s} {d['pecas']:4d} peças  {d['volume_m3']:8.1f} m³")
    print("pendências:", len(modelo.pendencias), "->", saida)
