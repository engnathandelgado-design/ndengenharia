"""Letsara rev04 — modelo global 3D (OpenSeesPy) revisto pela NBR 9062:2017: sem vigas de travamento (não há ponte rolante),
travamento pela cobertura (TS-01 + terças-escora + X) e pelo diafragma do mezanino; variante com a fiada superior das placas
ligada aos pilares (furo redondo) para medir a contribuição do fechamento (5.1.2.1 c/d; regra ND).

Mudanças em relação ao r01:
  - sem VT (eixos A e E): os pilares laterais ficam ligados só pelas terças-escora no nível do assento da TS-01;
  - rigidez ELU dos pilares 0,4·Eci·Ic (NBR 9062:2017 Anexo A, galpão com ligações articuladas), vigas articuladas;
    ELS com o módulo secante Ecs·Ic (5.4.2);
  - desaprumo H/400 nas duas direções (5.2.3), somado ao vento nas combinações ELU;
  - γz pela 5.1.2.12: γz = 1/(1 − ΔMtot,d/M1,tot,d) com os deslocamentos de 1ª ordem;
  - limites de deslocamento horizontal da Tab. 7 (frequente): galpão H/400 (sem ponte rolante, H = altura total);
    pilares do mezanino H/500 no topo e Hi/750 entre pisos;
  - mezanino com VM em meio vaso (0,1925 m² + 2º estágio 1,5 kN/m).

Texto original do r01:

Sistema (pré-moldado): pilares engastados no cálice (barras 3D elásticas, cabeça recuada 40×30 acima do recuo); vigas TS-01,
I130, VT, VB e VM articuladas (pino + neoprene) = barras de treliça; terças como escoras entre as vigas nos nós do
contraventamento e em todas as 26 linhas de terças (como no modelo 3D), inclusive nos vãos de oitão (L1–L2 e L8–L9, apoiadas na VB 15×90 modelada como viga articulada nos pilares); X Ø16 só nos vãos 2-3 e 7-8 (rev. 13/10/2026: retirados os X dos vãos 4-5 e 5-6 — esforço no X praticamente igual; só tração: as diagonais comprimidas foram retiradas, A ≈ 0); mezanino
(laje alveolar + capa) como diafragma rígido nos níveis +3,15 e +6,55.

Rigidez: ELU com 0,8·Ecs·Ic nos pilares (NBR 6118:2023 15.7.3, análise global com não linearidade física aproximada) e
P-Δ; ELS com Ecs·Ic (estádio I), também com P-Δ.
Ações: G (peso das peças, cobertura rev03: zipada + lã + TP40 + painéis solares + instalações 0,41 kN/m² + terças, mezanino 2,8 + 1,25 + 1,0 kN/m²), Qc (cobertura 0,25 kN/m²),
Qm (mezanino 5 kN/m²), vento NBR 6123 (V0 45 m/s, S2 cat. III classe C variando com a altura, S3 0,95; Cpe +0,7/−0,5).
Combinações (NBR 8681:2003): ELU γg 1,3 (pré-moldado), γq 1,4, ψ0 vento 0,6, ψ0 mezanino 0,7, ψ0 cobertura 0,5;
ELS frequente com ψ1 vento 0,3 e ψ1 mezanino 0,6. Limite de deslocamento horizontal do topo: H/1700 (NBR 6118:2023
tabela 13.3, combinação frequente) — conferir com o limite de galpão adotado no contrato.
Saída: modelo_global_r01.json (nós, barras, deslocamentos por combinação, reações e momentos na base de cada pilar).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import openseespy.opensees as ops

AQ = Path(__file__).parent
sys.path.insert(0, str(AQ.parents[1]))
from nd_estruturas.prefabricados import Concreto, pressao_vento
from geometria import Y_LIN, X_EIXO, Y_P13, LINHA_PORTOES

LG = json.loads((AQ / "ligacoes.json").read_text(encoding="utf-8"))
C40 = Concreto(40)
LARG, COMP, XC = X_EIXO["E"], Y_LIN[-1], X_EIXO["C"]
Z0, I = LG["Z0_TS"], 0.03
zf = lambda x: Z0 + I * x
REC = tuple(LG["REC"])                    # assento da TS-01 no recuo dos pilares P1 / P2 (rev03, sem dente)
Z_TOP_C = LG["Z_TOPO_I130"]                  # topo da I130 e dos pilares P8A/P11/P13 (TS-01 apoiada no topo)
Z_MEZ = (3.15, 6.55)
Z_VT = ()                                  # rev04: sem VT (NBR 9062 + regra ND: só com ponte rolante)
PLACAS = False                             # variante: fiada superior das placas ligada aos pilares (furo redondo)
A_VM, G_2E = 0.1925, 1.5                   # VM meio vaso (calc_vm_meio_vaso.py) e 2º estágio (kN/m)
Z_I130 = LG["Z_ASS_I130"]                 # assento da I130 nos consolos CP-I130 (rev03)
NOS = LG["nos_contraventamento_x_esq"]
NOS_D = [round(x + (2 * XC - LG["X_PONTA_CEN"]) - LG["X_PONTA_ESQ"], 3) for x in NOS]
G_COB = LG["cargas_cob"]["g_total_sem_terca"] + 0.123 / LG["passo_tercas"]   # + terça Ue 300×85×25×3,00 (12,5 kg/m)
Q_COB = LG["cargas_cob"]["sobrecarga"]
VAOS_X = [(1, 2), (6, 7)]               # X só nos vãos 2-3 e 7-8 (vizinhos aos oitões)
MID = [round((a + b) / 2, 3) for a, b in zip(NOS[:-1], NOS[1:])]          # terças intermediárias (entre os nós do X)
MID_D = [round((a + b) / 2, 3) for a, b in zip(NOS_D[:-1], NOS_D[1:])]
TRIB = [(Y_LIN[min(i + 1, 8)] - Y_LIN[max(i - 1, 0)]) / 2 for i in range(9)]
XF = [X_EIXO[k] for k in "ABCDE"]
TRIB_X = [(XF[min(i + 1, 4)] - XF[max(i - 1, 0)]) / 2 for i in range(5)]

nos, tag, pil, bar = {}, [0], [], []
POR_VAO = {}                                    # esforços das terças-escora e do X por vão (última análise)


def no(x, y, z):
    k = (round(x, 3), round(y, 3), round(z, 3))
    if k not in nos:
        tag[0] += 1
        nos[k] = tag[0]
        ops.node(tag[0], *k)
    return nos[k]


def montar(fator_EI=1.0, pdelta=True):
    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)
    nos.clear(); tag[0] = 0; pil.clear(); bar.clear()
    ops.geomTransf("PDelta" if pdelta else "Linear", 1, 1, 0, 0)
    ops.uniaxialMaterial("Elastic", 9, C40.Ecs)
    ops.uniaxialMaterial("Elastic", 10, 200e6, 0.0, 0.0)  # aço só tração (X Ø16): Eneg = 0
    ops.uniaxialMaterial("Elastic", 11, 200e6)
    E, G = C40.Ecs * fator_EI, C40.Ecs * fator_EI / 2.4

    def pilar(nome, x, y, bx, by, ztop, zs_extra=(), rec=None, cab=None):
        zs = sorted(set([0.0, 2.5, 5.0, ztop] + [z for z in zs_extra if z < ztop] + ([rec] if rec else [])))
        ns = [no(x, y, z) for z in zs]
        ops.fix(ns[0], 1, 1, 1, 1, 1, 1)
        for k, (a, b) in enumerate(zip(ns[:-1], ns[1:])):
            sx, sy = (cab if (rec and zs[k] >= rec - 1e-6) else (bx, by))
            A, Iy, Iz = sx * sy, sy * sx ** 3 / 12, sx * sy ** 3 / 12
            J = 0.2 * min(sx, sy) ** 3 * max(sx, sy)
            ops.element("elasticBeamColumn", 100000 + len(pil) * 100 + k, a, b, A, E, G, J, Iy, Iz, 1)
        pil.append(dict(nome=nome, x=x, y=y, bx=bx, by=by, zs=zs, ns=ns))
        return ns

    def at(nome, z):
        p = next(p for p in pil if p["nome"] == nome)
        return p["ns"][p["zs"].index(min(p["zs"], key=lambda zz: abs(zz - z)))]

    def barra(n1, n2, A, grupo, mat=9):
        t = 500000 + len(bar)
        ops.element("Truss", t, n1, n2, A, mat)
        bar.append(dict(tag=t, n1=n1, n2=n2, grupo=grupo))

    def no_livre(x, y, z):
        n = no(x, y, z)
        try:
            ops.fix(n, 0, 0, 1, 1, 1, 1)
        except Exception:
            pass
        return n

    # ---------------- pilares
    for i, y in enumerate(Y_LIN):
        canto = i in (0, 8)
        for nome, x0, k in (("P1", 0.0, 0), ("P2", LARG, 1)):
            zs = [REC[k]] + list(Z_VT[k:k + 1]) + (list(Z_MEZ) if i <= 1 else []) + ([8.75] if PLACAS else [])
            zr = REC[k] if not canto else math.ceil((zf(x0) + 0.90) / 0.05) * 0.05
            pilar(f"{nome}{'C' if canto else ''}-L{i+1}", x0, y, 0.60, 0.40, 10.0, zs, rec=zr, cab=(0.30, 0.30 if canto else 0.40))
    for j, x in enumerate(XF[1:4]):
        for nome, y in ((["P3", "P4", "P5"][j] + "-L1", 0.0), (["P3", "P14", "P5"][j] + "-L9", COMP)):
            zs = [zf(x) - 0.01] + (list(Z_MEZ) if y == 0 else []) + ([Z_I130] if "P14" in nome else []) + ([8.75] if PLACAS else [])
            pilar(nome, x, y, 0.40, 0.60, 10.0, zs, rec=math.ceil((zf(x) + 0.90) / 0.05) * 0.05, cab=(0.40, 0.30))
    pilar("P8A", XC, Y_LIN[1], 0.40, 0.60, Z_TOP_C, [Z_I130] + list(Z_MEZ))
    pilar("P11", XC, Y_LIN[3], 0.40, 0.40, Z_TOP_C, [Z_I130])
    pilar("P13", XC, Y_P13, 0.60, 0.60, Z_TOP_C, [Z_I130])
    for nome, x in (("P8", X_EIXO["B"]), ("P8B", X_EIXO["D"])):
        pilar(nome, x, Y_LIN[1], 0.40, 0.60, Z_MEZ[1], list(Z_MEZ))
    for nome, x, b in (("P9", 9.87, 0.40), ("P10a", 15.195, 0.25), ("P10b", 24.305, 0.25), ("P12", 29.63, 0.40)):
        pilar(nome, x, Y_LIN[LINHA_PORTOES], b, b, 7.50)

    # ---------------- TS-01 (linhas 2 a 8) com nós nos pontos do contraventamento; apoio central no pilar (L2, L4) ou na I130
    lin_cen = {}
    for i in range(1, 8):
        y = Y_LIN[i]
        nA = at(f"P1-L{i+1}", REC[0]); nE = at(f"P2-L{i+1}", REC[1])
        if i == 1:                               # rev03: linha 2 com furo oblongo no topo do P8A (desliza em x): o mezanino já trava P1-L2/P8A/P2-L2
            nc = no_livre(XC, y, Z_TOP_C)
        elif i == 3:
            nc = at("P11", Z_TOP_C)
        else:
            nc = no_livre(XC, y, Z_TOP_C)            # TS-01 apoiada no topo da I130 (rev03)
        lin_cen[i] = nc
        cadeia = [nA] + [no_livre(x, y, zf(x) + 0.45) for x in sorted(NOS[1:-1] + MID)] + [nc]
        cadeia_d = [nc] + [no_livre(x, y, zf(x) + 0.45) for x in sorted(NOS_D[1:-1] + MID_D)] + [nE]
        for c in (cadeia, cadeia_d):
            for a, b in zip(c[:-1], c[1:]):
                barra(a, b, 0.2225, "TS-01")
    # I130: P8A → L3 → P11 → L5 → L6 → P13 → L7 → L8 → P14
    ch = [at("P8A", Z_I130), lin_cen[2], at("P11", Z_I130), lin_cen[4], lin_cen[5], at("P13", Z_I130), lin_cen[6], lin_cen[7], at("P14-L9", Z_I130)]
    for a, b in zip(ch[:-1], ch[1:]):
        barra(a, b, 0.333, "I130")
    # terças-escora entre linhas nos nós do contraventamento (todos os vãos internos) e X nos vãos contraventados
    def no_linha(x, i):
        y = Y_LIN[i]
        if abs(x) < 1e-6:
            return at(f"P1-L{i+1}", REC[0])
        if abs(x - LARG) < 1e-6:
            return at(f"P2-L{i+1}", REC[1])
        if abs(x - XC) < 1e-6:
            return lin_cen[i]
        return nos[(round(x, 3), round(y, 3), round(zf(x) + 0.45, 3))]
    xs_no = [0.0] + NOS[1:-1] + [XC] + NOS_D[1:-1] + [LARG]
    xs_t = sorted(xs_no + MID + MID_D)                                   # todas as 26 linhas de terças
    for i in range(1, 7):
        for x in xs_t:
            barra(no_linha(x, i), no_linha(x, i + 1), 15.2e-4, "terça-escora", mat=11)
    for (ia, ib) in VAOS_X:
        for k in range(len(xs_no) - 1):
            a, b = xs_no[k], xs_no[k + 1]
            barra(no_linha(a, ia), no_linha(b, ib), 2.01e-4, "X Ø16", mat=10)
            barra(no_linha(b, ia), no_linha(a, ib), 2.01e-4, "X Ø16", mat=10)
    # VT 25×60 nos eixos A e E (linhas 2 a 9), VB nas fachadas 1 e 9
    if PLACAS:                                   # fiada +7,50/+8,75 com CL-1 de furo redondo nas duas pontas: tirante elástico
        # rigidez axial de um vão de placa = placa (E A / L) em série com 2 CL-1 (k_CL1 cada, flexão da aba 102 x 12,5 + parafuso)
        k_cl = 2 * 3 * 200e6 * (0.15 * 0.0125 ** 3 / 12) / 0.06 ** 3       # 2 CL-1 por ponta (uma por placa adjacente), aba em balanço 60 mm
        def tirante(na, nb, L):
            k_pl = C40.Ecs * 0.125 / L
            k = 1 / (1 / k_pl + 2 / k_cl)
            barra(na, nb, k * L / 200e6, "placa-tirante", mat=11)
        for nome in ("P1", "P2"):
            nomes = [f"{nome}C-L1"] + [f"{nome}-L{i+1}" for i in range(1, 8)] + [f"{nome}C-L9"]
            for a_, b_, (ya, yb) in zip(nomes[:-1], nomes[1:], zip(Y_LIN[:-1], Y_LIN[1:])):
                tirante(at(a_, 8.75), at(b_, 8.75), yb - ya)
        for y_, nomes in ((0.0, ["P1C-L1", "P3-L1", "P4-L1", "P5-L1", "P2C-L1"]), (COMP, ["P1C-L9", "P3-L9", "P14-L9", "P5-L9", "P2C-L9"])):
            for a_, b_, (xa, xb) in zip(nomes[:-1], nomes[1:], zip(XF[:-1], XF[1:])):
                tirante(at(a_, 8.75), at(b_, 8.75), xb - xa)
    # VB 15×90 das fachadas 1 e 9: viga (flexão no plano horizontal) articulada nos pilares, com nós nas terças do vão de
    # oitão (L1–L2 e L8–L9), que apoiam no topo da VB e levam o vento da fachada para a cobertura (escoras como nos vãos internos)
    ops.geomTransf("Linear", 2, 0, 0, 1)
    Ivb_lat, Ivb_v, Jvb = 0.90 * 0.15 ** 3 / 12, 0.15 * 0.90 ** 3 / 12, 0.2 * 0.15 ** 3 * 0.90
    def no_novo(x, y, z):
        tag[0] += 1
        ops.node(tag[0], x, y, z)
        nos[(round(x, 3), round(y, 3), round(z, 3), tag[0])] = tag[0]        # nó duplicado (rótula), chave única
        return tag[0]
    vb_no = {}
    for y, il, nomes in ((0.0, 0, ["P1C-L1", "P3-L1", "P4-L1", "P5-L1", "P2C-L1"]), (COMP, 8, ["P1C-L9", "P3-L9", "P14-L9", "P5-L9", "P2C-L9"])):
        for k in range(4):
            xa, xb = XF[k], XF[k + 1]
            pa, pb = at(nomes[k], zf(xa)), at(nomes[k + 1], zf(xb))
            ea, eb = no_novo(xa, y, zf(xa)), no_novo(xb, y, zf(xb))
            for e_, p_ in ((ea, pa), (eb, pb)):
                ops.equalDOF(p_, e_, 1, 2, 3, 4)
            meio = [x for x in xs_t if xa + 0.05 < x < xb - 0.05]
            cadeia = [ea]
            for x in meio:
                n = no_novo(x, y, zf(x))
                ops.fix(n, 0, 0, 1, 1, 1, 0)
                vb_no[(il, round(x, 3))] = n
                cadeia.append(n)
            cadeia.append(eb)
            for a, b in zip(cadeia[:-1], cadeia[1:]):
                t = 600000 + len(bar)
                ops.element("elasticBeamColumn", t, a, b, 0.135, E, G, Jvb, Ivb_v, Ivb_lat, 2)
                bar.append(dict(tag=t, n1=a, n2=b, grupo="VB"))
        for x in xs_t:                                       # terças do vão de oitão: linha 2 (ou 8) → VB
            i_in = 1 if il == 0 else 7
            alvo = vb_no.get((il, round(x, 3)))
            if alvo is None:                                 # terça sobre pilar de canto / P4: nó do pilar
                alvo = at(nomes[[0.0, XF[1], XC, XF[3], LARG].index(min([0.0, XF[1], XC, XF[3], LARG], key=lambda xx: abs(xx - x)))], zf(x))
            barra(no_linha(x, i_in), alvo, 15.2e-4, "terça-escora", mat=11)
    # mezanino: VM + diafragma
    for z in Z_MEZ:
        l1 = [at(n, z) for n in ("P1C-L1", "P3-L1", "P4-L1", "P5-L1", "P2C-L1")]
        l2 = [at(n, z) for n in ("P1-L2", "P8", "P8A", "P8B", "P2-L2")]
        for row in (l1, l2):
            for a, b in zip(row[:-1], row[1:]):
                barra(a, b, 0.2225, "VM")
        mestre = no(XC, Y_LIN[1] / 2, z)
        ops.fix(mestre, 0, 0, 1, 1, 1, 0)
        ops.rigidDiaphragm(3, mestre, *(l1 + l2))


def cargas_basicas():
    """Forças nodais de cada caso básico: dict caso -> {nó: [Fx..Mz]}."""
    C = {k: {} for k in ("G", "Qc", "Qm", "Wx", "Wy", "Dx", "Dy")}

    def add(caso, n, f):
        v = C[caso].setdefault(n, [0.0] * 6)
        for k in range(6):
            v[k] += f[k]

    def at(nome, z):
        p = next(p for p in pil if p["nome"] == nome)
        return p["ns"][p["zs"].index(min(p["zs"], key=lambda zz: abs(zz - z)))]
    for p in pil:                                         # peso próprio dos pilares (lumped)
        for k, (za, zb) in enumerate(zip(p["zs"][:-1], p["zs"][1:])):
            P = p["bx"] * p["by"] * 25 * (zb - za)
            add("G", p["ns"][k], [0, 0, -P / 2, 0, 0, 0]); add("G", p["ns"][k + 1], [0, 0, -P / 2, 0, 0, 0])
    # TS-01: reação por apoio
    L_TS = LG["L_TS"]
    for i in range(1, 8):
        g = (0.2225 * 25 + G_COB * TRIB[i]) * L_TS / 2
        q = Q_COB * TRIB[i] * L_TS / 2
        for n in (at(f"P1-L{i+1}", REC[0]), at(f"P2-L{i+1}", REC[1])):
            add("G", n, [0, 0, -g, 0, 0, 0]); add("Qc", n, [0, 0, -q, 0, 0, 0])
        if i in (1, 3):
            n = at("P8A" if i == 1 else "P11", Z_TOP_C)
            add("G", n, [0, 0, -2 * g, 0, 0, 0]); add("Qc", n, [0, 0, -2 * q, 0, 0, 0])
    # I130: reações (peso próprio + 2 TS por linha) nos pilares de apoio — vigas biapoiadas
    apo = [("P8A", Y_LIN[1]), ("P11", Y_LIN[3]), ("P13", Y_P13), ("P14-L9", COMP)]
    for (na, ya), (nb, yb) in zip(apo[:-1], apo[1:]):
        L = yb - ya
        Ra_g = Rb_g = 0.333 * 25 * L / 2
        Ra_q = Rb_q = 0.0
        for i in range(1, 8):
            y = Y_LIN[i]
            if ya < y < yb:
                g = 2 * (0.2225 * 25 + G_COB * TRIB[i]) * L_TS / 2
                q = 2 * Q_COB * TRIB[i] * L_TS / 2
                Ra_g += g * (yb - y) / L; Rb_g += g * (y - ya) / L
                Ra_q += q * (yb - y) / L; Rb_q += q * (y - ya) / L
        for nome, Rg, Rq in ((na, Ra_g, Ra_q), (nb, Rb_g, Rb_q)):
            n = at(nome, Z_I130)
            add("G", n, [0, 0, -Rg, 0, 0, 0]); add("Qc", n, [0, 0, -Rq, 0, 0, 0])
    # VT e VB (peso), mezanino (VM + laje + capa + revestimento; sobrecarga) — reações nos pilares
    gm, qm = 2.8 + 1.25 + 1.0, 5.0
    for z in Z_MEZ:
        for row, y in ((("P1C-L1", "P3-L1", "P4-L1", "P5-L1", "P2C-L1"), 0.0), (("P1-L2", "P8", "P8A", "P8B", "P2-L2"), Y_LIN[1])):
            for k, nm in enumerate(row):
                larg = TRIB_X[k]
                add("G", at(nm, z), [0, 0, -(gm * 9.65 / 2 + A_VM * 25 + G_2E) * larg, 0, 0, 0])
                add("Qm", at(nm, z), [0, 0, -qm * 9.65 / 2 * larg, 0, 0, 0])
    # vento: forças nodais nos pilares das fachadas (área de influência × altura entre nós)
    for p in pil:
        lateral = p["nome"].startswith(("P1-", "P1C-", "P2-", "P2C-"))
        fach = p["nome"].endswith(("-L1", "-L9"))
        zs, ns = p["zs"], p["ns"]
        for k in range(1, len(zs)):
            dz = (zs[k] - zs[k - 1]) / 2 + ((zs[k + 1] - zs[k]) / 2 if k + 1 < len(zs) else 0)
            qz = pressao_vento(45.0, z=max(zs[k], 3.0), S3=0.95)
            if lateral:
                iy = min(range(9), key=lambda i: abs(Y_LIN[i] - p["y"]))
                cp = 0.7 if p["x"] < 1 else 0.5
                add("Wx", ns[k], [cp * qz * TRIB[iy] * dz, 0, 0, 0, 0, 0])
            if fach:
                ix = min(range(5), key=lambda i: abs(XF[i] - p["x"]))
                cp = 0.7 if p["y"] < 1 else 0.5
                add("Wy", ns[k], [0, cp * qz * TRIB_X[ix] * dz, 0, 0, 0, 0])
    # desaprumo H/400 (NBR 9062:2017 5.2.3): força horizontal fictícia = carga vertical do nó x 1/400 nas duas direções
    # (equivale à excentricidade acumulada h/400 em cada nível de apoio), com G + Qc + Qm
    for caso in ("G", "Qc", "Qm"):
        for n, v in C[caso].items():
            add("Dx", n, [-v[2] / 400, 0, 0, 0, 0, 0]); add("Dy", n, [0, -v[2] / 400, 0, 0, 0, 0])
    return C


COMB = {
    "ELU-1 vento x": ("ELU", {"G": 1.3, "Wx": 1.4, "Qm": 1.4 * 0.7, "Qc": 1.4 * 0.5, "Dx": 1.3}),
    "ELU-2 vento y": ("ELU", {"G": 1.3, "Wy": 1.4, "Qm": 1.4 * 0.7, "Qc": 1.4 * 0.5, "Dy": 1.3}),
    "ELU-3 sobrecarga + vento x": ("ELU", {"G": 1.3, "Qm": 1.4, "Qc": 1.4 * 0.5, "Wx": 1.4 * 0.6, "Dx": 1.3}),
    "ELU-4 sobrecarga + vento y": ("ELU", {"G": 1.3, "Qm": 1.4, "Qc": 1.4 * 0.5, "Wy": 1.4 * 0.6, "Dy": 1.3}),
    "ELS-F vento x": ("ELS", {"G": 1.0, "Wx": 0.3, "Qm": 0.6}),
    "ELS-F vento y": ("ELS", {"G": 1.0, "Wy": 0.3, "Qm": 0.6}),
}


def rodar(nome, fatores, fator_EI, pdelta=True):
    montar(fator_EI, pdelta)
    C = cargas_basicas()
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    tot = {}
    for caso, f in fatores.items():
        for n, v in C[caso].items():
            t = tot.setdefault(n, [0.0] * 6)
            for k in range(6):
                t[k] += f * v[k]
    for n, v in tot.items():
        ops.load(n, *v)
    ops.system("UmfPack"); ops.numberer("RCM"); ops.constraints("Transformation")
    ops.test("NormDispIncr", 1e-8, 50); ops.algorithm("Newton")
    ops.integrator("LoadControl", 0.1); ops.analysis("Static")
    ok = ops.analyze(10)
    ops.reactions()
    d = {n: [ops.nodeDisp(n, k) for k in (1, 2, 3)] for n in nos.values()}
    base = {}
    for p in pil:
        r = ops.nodeReaction(p["ns"][0])
        topo = d[p["ns"][-1]]
        base[p["nome"]] = dict(bx=p["bx"], by=p["by"], N=round(r[2], 1), Vx=round(-r[0], 1), Vy=round(-r[1], 1), Mx=round(-r[3], 1), My=round(-r[4], 1),
                               topo_mm=[round(topo[0] * 1000, 1), round(topo[1] * 1000, 1)], H=p["zs"][-1])
    forcas = {}
    POR_VAO.clear()
    for b in bar:
        f = ops.basicForce(b["tag"])[0]
        g = forcas.setdefault(b["grupo"], [0.0, 0.0])
        g[0] = min(g[0], f); g[1] = max(g[1], f)
        if b["grupo"] in ("terça-escora", "X Ø16"):            # envoltória por vão (linha i a i+1) para a verificação das terças
            ym = (ops.nodeCoord(b["n1"])[1] + ops.nodeCoord(b["n2"])[1]) / 2
            iv = max(k for k in range(8) if Y_LIN[k] <= ym + 1e-6)
            gv = POR_VAO.setdefault(b["grupo"], {}).setdefault(f"{iv+1}-{iv+2}", [0.0, 0.0])
            gv[0] = min(gv[0], round(f, 2)); gv[1] = max(gv[1], round(f, 2))
            if b["grupo"] == "terça-escora":                    # por linha de terça (x da terça, m) — faixas de beiral
                xm = round((ops.nodeCoord(b["n1"])[0] + ops.nodeCoord(b["n2"])[0]) / 2, 2)
                gl = POR_VAO.setdefault("terça-escora por linha", {}).setdefault(f"{iv+1}-{iv+2}", {}).setdefault(f"{xm:.2f}", [0.0, 0.0])
                gl[0] = min(gl[0], round(f, 2)); gl[1] = max(gl[1], round(f, 2))
    rodar.tot = tot
    return ok == 0, d, base, forcas


F_ELU = 0.4 * C40.Eci / C40.Ecs           # NBR 9062:2017 Anexo A: pilares de galpão com ligações articuladas 0,4·Eci·Ic
import os
PLACAS = os.environ.get("PLACAS", "0") == "1"
SAIDA = "modelo_global_r04" + ("_placas" if PLACAS else "") + ".json"


def gama_z(d1, tot, dir_):
    """NBR 9062:2017 5.1.2.12: γz = 1/(1 − ΔMtot,d/M1,tot,d), ΔM = Σ Pd·u (1ª ordem), M1 = Σ Hd·z."""
    k = 0 if dir_ == "x" else 1
    coord = {n: c for c, n in nos.items()}
    dM = sum(-v[2] * d1[n][k] for n, v in tot.items() if n in d1)
    M1 = sum(v[k] * coord[n][2] for n, v in tot.items() if n in coord)
    return 1 / (1 - dM / M1) if M1 else None


def lim_pilar(p):
    """Tab. 7 (5.4.3.3), combinação frequente, sem encunhamento: galpão H/400 (sem ponte rolante, H = altura total);
    pilar com mezanino: H/500 no topo."""
    tem_mez = any(abs(z - Z_MEZ[0]) < 1e-3 for z in p["zs"])
    return p["zs"][-1] * 1000 / (500 if tem_mez else 400)


res = dict(combinacoes={}, nos=None, barras=None, pilares=None)
for nome, (tipo, fat) in COMB.items():
    okP, dP, baseP, fP = rodar(nome, fat, F_ELU if tipo == "ELU" else 1.0, True)
    pvP = {g: dict(sorted(v.items())) for g, v in POR_VAO.items()}
    if tipo == "ELU":
        ok1, d1, _, _ = rodar(nome, fat, F_ELU, False)
        gz = gama_z(d1, rodar.tot, "x" if "x" in nome else "y")
    dmax = max(math.hypot(v[0], v[1]) for v in dP.values()) * 1000
    pmax = max(baseP, key=lambda k: math.hypot(*baseP[k]["topo_mm"]))
    item = dict(tipo=tipo, convergiu=okP, desl_max_mm=round(dmax, 1), pilar_desl_max=pmax,
                deslocamentos={str(n): [round(c * 1000, 2) for c in v] for n, v in dP.items()},
                base=baseP, forcas_barras={k: [round(v[0], 1), round(v[1], 1)] for k, v in fP.items()},
                por_vao=pvP)
    if tipo == "ELU":
        dl = max(math.hypot(v[0], v[1]) for v in d1.values()) * 1000
        item["gama_z_aprox"] = round(dmax / dl, 3) if dl > 0.05 else None
        item["gama_z_9062"] = round(gz, 3)
    else:
        lims = {p["nome"]: lim_pilar(p) for p in pil}
        item["limite_mm"] = round(min(lims.values()), 1)
        item["uso_desl"] = {n: round(math.hypot(*b["topo_mm"]) / lims[n], 3) for n, b in baseP.items()}
        item["uso_desl_max"] = max(item["uso_desl"].values())
        item["pilar_uso_max"] = max(item["uso_desl"], key=item["uso_desl"].get)
        # entre pisos do mezanino (Hi/750): P1C-L1 … P2-L2 nos níveis +3,15 / +6,55
        di = []
        for p in pil:
            if any(abs(z - Z_MEZ[0]) < 1e-3 for z in p["zs"]):
                zz = [0.0] + list(Z_MEZ)
                u = [dP[p["ns"][p["zs"].index(min(p["zs"], key=lambda q: abs(q - z)))]] for z in zz]
                for a_, b_, za_, zb_ in zip(u[:-1], u[1:], zz[:-1], zz[1:]):
                    di.append((math.hypot(b_[0] - a_[0], b_[1] - a_[1]) * 1000 / ((zb_ - za_) * 1000 / 750), p["nome"]))
        item["uso_Hi750_max"] = round(max(di)[0], 3) if di else 0.0
        item["ok_ELS"] = item["uso_desl_max"] <= 1.0 and item["uso_Hi750_max"] <= 1.0
    res["combinacoes"][nome] = item
    print(f"{nome:28s} desl máx {dmax:6.1f} mm ({pmax})" + (f" γz {item['gama_z_9062']}" if tipo == "ELU" else f" uso {item['uso_desl_max']} ({item['pilar_uso_max']}) Hi/750 {item['uso_Hi750_max']} ok={item['ok_ELS']}"))
res["nos"] = {str(n): list(k[:3]) for k, n in nos.items()}
res["barras"] = [dict(n1=b["n1"], n2=b["n2"], grupo=b["grupo"]) for b in bar]
res["pilares"] = [dict(nome=p["nome"], ns=p["ns"], cab=bool(p.get("zs"))) for p in pil]
(AQ / SAIDA).write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")


# ------------------------------------------------------------------ ELU: flexão composta oblíqua na base dos pilares
# NBR 6118:2023 17.2.4 (bloco retangular 0,85 fcd, λ 0,8, εcu 3,5‰, CA-50) e 17.2.5.2 (verificação simplificada da
# flexão oblíqua: (Mx/MRx)^α + (My/MRy)^α ≤ 1, α = 1,2). Momentos de 1ª + 2ª ordem global (P-Δ) do modelo; os efeitos
# locais de 2ª ordem dos pilares em balanço foram verificados pelo método geral nas pranchas dos pilares (λu).
ARM = {"PL": (0.40, 0.60, 5, 7, 20.0), "P8A": (0.40, 0.60, 5, 7, 20.0), "P11": (0.40, 0.40, 4, 4, 20.0), "P13": (0.60, 0.60, 6, 6, 20.0),
       "PM": (0.40, 0.60, 3, 4, 20.0), "PG": (0.40, 0.40, 3, 3, 16.0), "P10": (0.25, 0.25, 2, 2, 16.0)}


def barras(bx, by, nx, ny, d, c=0.048):
    xs = [-bx / 2 + c + k * (bx - 2 * c) / (nx - 1) for k in range(nx)]
    ys = [-by / 2 + c + k * (by - 2 * c) / (ny - 1) for k in range(ny)]
    pts = {(round(x, 4), round(y, 4)) for x in xs for y in (ys[0], ys[-1])} | {(round(x, 4), round(y, 4)) for y in ys for x in (xs[0], xs[-1])}
    return [(x, y, math.pi * (d / 1000) ** 2 / 4) for x, y in pts]


def MRd(b, h, bars, Nd, eixo):
    """Momento resistente (kN·m) para Nd (kN, compressão +) com a linha neutra paralela ao lado b (flexão em torno do eixo
    paralelo a b; altura h). bars: (x, y, A) com y na direção de h."""
    fcd, fyd, Es = 40e3 / 1.4, 500e3 / 1.15, 200e6
    def forcas(x):
        yc = h / 2
        a = min(0.8 * x, h)
        Cc = 0.85 * fcd * b * a
        Mc = Cc * (yc - a / 2)
        Fs = Ms = 0.0
        for bx_, by_, A in bars:
            yy = by_ if eixo == "y" else bx_
            dist = yc - yy                                          # profundidade a partir da borda comprimida
            eps = 0.0035 * (x - dist) / x
            sig = max(-fyd, min(fyd, Es * eps))
            Fs += sig * A; Ms += sig * A * yy
        return Cc + Fs, Mc + Ms
    lo, hi = 1e-4, 5 * h
    for _ in range(100):
        x = (lo + hi) / 2
        if forcas(x)[0] > Nd:
            hi = x
        else:
            lo = x
    return forcas((lo + hi) / 2)[1]


def tipo_pilar(nome):
    if nome.startswith(("P1-", "P1C-", "P2-", "P2C-", "P3-", "P4-", "P5-", "P14-")):
        return "PL"
    return {"P8A": "P8A", "P11": "P11", "P13": "P13", "P8": "PM", "P8B": "PM", "P9": "PG", "P12": "PG"}.get(nome, "P10")


verif = {}
for nome_c, item in res["combinacoes"].items():
    if item["tipo"] != "ELU":
        continue
    for nome, b in item["base"].items():
        d1, d2, n1, n2, d = ARM[tipo_pilar(nome)]
        bx, by = b["bx"], b["by"]
        nx, ny = (n1, n2) if abs(bx - d1) < 1e-6 else (n2, n1)
        brs = barras(bx, by, nx, ny, d)
        Nd = max(b["N"], 0.0)
        MRx = MRd(bx, by, brs, Nd, "y")            # flexão no plano yz (momento em torno de x): altura = by
        MRy = MRd(by, bx, brs, Nd, "x")            # flexão no plano xz: altura = bx
        Mx, My = abs(b["Mx"]), abs(b["My"])
        u = (Mx / MRx) ** 1.2 + (My / MRy) ** 1.2
        v = verif.get(nome)
        if v is None or u > v["uso"]:
            verif[nome] = dict(comb=nome_c, N=b["N"], Mx=round(Mx, 1), My=round(My, 1), MRx=round(MRx, 1), MRy=round(MRy, 1), uso=round(u, 3),
                               secao=f"{bx*100:.0f}×{by*100:.0f}", armadura=f"{len(brs)} Ø{d:g}")
res["verificacao_pilares"] = verif
ruins = {k: v for k, v in verif.items() if v["uso"] > 1}
print("pilares:", len(verif), "uso máx", max(v["uso"] for v in verif.values()), "reprovados:", list(ruins)[:10])
for k in sorted(verif, key=lambda k: -verif[k]["uso"])[:6]:
    print(" ", k, verif[k])
(AQ / SAIDA).write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")

# método geral (2ª ordem local + não linearidade física + fluência φef 0,5) no pilar mais solicitado — NBR 6118:2023 15.8.3.2
from nd_estruturas.prefabricados import pilar_metodo_geral
crit = max(verif, key=lambda k: verif[k]["uso"])
bc = res["combinacoes"][verif[crit]["comb"]]["base"][crit]
w_eq = 2 * (abs(bc["My"]) / res["combinacoes"][verif[crit]["comb"]]["gama_z_aprox"]) / bc["H"] ** 2
mg = pilar_metodo_geral(0.40, 0.60, bc["H"], 21.99, bc["N"], w_eq, C40, phi_ef=0.5)
res["metodo_geral"] = dict(pilar=crit, comb=verif[crit]["comb"], Nd=bc["N"], w_eq_kNm=round(w_eq, 2), **mg)
print("método geral", res["metodo_geral"])
(AQ / SAIDA).write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
