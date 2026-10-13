"""Letsara — modelo BIM (IFC + página 3D) a partir das definições de projeto. Revisão de 12/10/2026 (tarde).

Rodar: PYTHONPATH=. python exemplos/letsara/modelo_bim.py [pasta_de_saida]
Saída (em saidas/, fora do git): letsara.ifc e letsara_3d.html (publicar a página como artefato para ver no celular).

Geometria = a mesma da checagem de ligações (ligacoes.json) e do modelo global:
- eixos Y (linhas 1 a 9) e X (A a E) do R01 como usados nos cálculos;
- cobertura baixada para ficar escondida na platibanda (+10,00) com 10 cm de folga no lado alto;
- TS-01 com dentes Gerber nas duas pontas, apoiadas em consolos (pilares laterais, pilares centrais e I110);
- I110 com consolos dos dois lados nas linhas das TS-01 (diafragma maciço);
- terças Ue 300 nas posições da TS-01 (c/1,579), mezanino com laje alveolar h20 + 5 sobre vigas I90 com dentes.
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
REC = (8.40, 9.55)                                 # recuo da cabeça dos pilares laterais (a validar) — ND-LET-LOC01
TOPO_PLAT, Z_CALICE = 10.00, -1.00
INCL = 0.03
Z0 = LG["Z0_TS"]                                   # fundo da TS-01 no eixo A
C3 = math.cos(math.atan(INCL))
zf = lambda x: Z0 + INCL * x                       # fundo (altura cheia) da TS-01 em x
H_TS, H_DENTE, L_DENTE = 0.90, 0.45, 0.30
L_TS = LG["L_TS"] * C3                             # projeção horizontal entre pontas
PONTAS = [(0.325, 0.325 + L_TS), (LARG - 0.325 - L_TS, LARG - 0.325)]
Z_I110_TOPO, H_I110 = 8.88, 1.10
CENTRAIS = [("P8A", Y_LIN[1]), ("P11", Y_LIN[3]), ("P13", Y_P13)]
I110_TRECHOS = [("V407", Y_LIN[1], Y_LIN[3]), ("V406", Y_LIN[3], Y_P13), ("V405", Y_P13, Y_LIN[8])]   # V405 vai até a linha 9 (P14)
NIVEIS_MEZ, H_LAJE = [3.15, 6.55], 0.20 + 0.05

I90 = PerfilI(h=0.90, b=0.40, tw=0.15, tf=0.15, nome="I90")
I110 = PerfilI(h=1.10, b=0.40, tw=0.15, tf=0.25, nome="I110")
I70 = PerfilI(h=0.70, b=0.40, tw=0.15, tf=0.15, nome="I70")
VB = PerfilRetangular(0.15, 0.90, "VB 15x90")
TERCA = PerfilRetangular(0.085, 0.30, "Ue300x85x25x3,00 (envelope)")
LAJE = PerfilRetangular(1.24, H_LAJE, "LA h20+5")
TELHA = PerfilRetangular(1.00, 0.03, "telha 0,5 + PIR 30")
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
    z_vb = lambda x: zf(x)                                                  # fundo da VB (sem dente) = topo do CP-VB
    rec_vb = lambda x: math.ceil((z_vb(x) + 0.90) / 0.05) * 0.05           # recuo da cabeça dos pilares de fachada: topo da VB 15×90

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
            if not canto:
                xp = 0.475 if sg > 0 else LARG - 0.475
                m.bloco("consolo", f"CP-TS L{i}", (x0 + sg * 0.45, y, ass_ts(xp)), 0.30, 0.40, hC("CP-TS"), "Consolos")
    # pilares das fachadas 1 e 9 (60 ⊥ fachada) com cabeça recuada acima da VB
    for j, x in enumerate(X_FACH[1:-1]):
        for nome, y, sg in ((["P3", "P4", "P5"][j], 0.0, 1), (["P3", "P14", "P5"][j], COMP, -1)):
            zr = rec_vb(x)
            m.pilar(f"{nome}-L{1 if sg > 0 else 9}", x, y, 0.40, 0.60, Z_CALICE, zr, obs="60 ⊥ fachada; cabeça recuada acima da VB")
            m.pilar(f"{nome}-L{1 if sg > 0 else 9} cabeça", x, y - sg * 0.15, 0.40, 0.30, zr, TOPO_PLAT, obs="cabeça 40×30")
    # centrais (R01): P8A 40×60, P11 40×40, P13 60×60 — topo +8,88 (topo da I110)
    for (marca, y), (bx, by) in zip(CENTRAIS, ((0.40, 0.60), (0.40, 0.40), (0.60, 0.60))):
        m.pilar(marca, X_C, y, bx, by, Z_CALICE, Z_I110_TOPO, obs=f"{bx*100:.0f}×{by*100:.0f}; apoio I110 / TS-01")
    for marca, x in (("P8", X_EIXO["B"]), ("P8B", X_EIXO["D"])):
        m.pilar(marca, x, Y_LIN[1], 0.40, 0.60, Z_CALICE, NIVEIS_MEZ[1], obs="mezanino 40×60")
    # pilares dos portões (linha 4): P9, P12 40×40 e P10 25×25, topo +7,50 (parede da vista C só até +7,50; a TS-01 passa por cima)
    for nome, x, b_ in (("P9", 9.87, 0.40), ("P10", 15.195, 0.25), ("P10", 24.305, 0.25), ("P12", 29.63, 0.40)):
        m.pilar(nome, x, Y_LIN[LINHA_PORTOES], b_, b_, Z_CALICE, 7.50, obs="parede dos portões (vista C), topo +7,50")

    # 2. vigas centrais I110 (comprimentos do R01) e consolos CP-I110 / CV-TS
    zc = Z_I110_TOPO - H_I110 / 2
    meia = {Y_LIN[1]: 0.30, Y_LIN[3]: 0.20, Y_P13: 0.30, Y_LIN[8]: 0.30}
    z_ass_i110 = Z_I110_TOPO - H_I110 + (H_I110 - 0.66) - 0.03
    for marca, ya, yb in I110_TRECHOS:
        y0, y1 = ya + meia[ya] + 0.075, yb - meia[yb] - 0.075
        m.linear("viga", marca, I110, (X_C, y0, zc), (X_C, y1, zc), "Vigas centrais I110",
                 obs=f"L = {y1 - y0:.3f} m; protendida 24 cord. Ø12,7 + 4 Ø20 na mesa superior; dente 660")
        for yy, sg in ((ya, 1), (yb, -1)):
            m.bloco("consolo", f"CP-I110 {marca}", (X_C, yy + sg * (meia[yy] + 0.20), z_ass_i110), 0.50, 0.40, hC("CP-I110"), "Consolos")
    for i in range(2, 9):
        y = Y_LIN[i - 1]
        tipo = "CP-TS" if any(abs(y - yy) < 0.01 for _, yy in CENTRAIS) else "CV-TS"
        for xc, x_ap in ((X_C - 0.20 - 0.175, PONTAS[0][1] - 0.15), (X_C + 0.20 + 0.175, PONTAS[1][0] + 0.15)):
            m.bloco("consolo", f"{tipo} L{i} (eixo C)", (xc, y, ass_ts(x_ap)), 0.35, 0.40, hC(tipo), "Consolos")

    # 3. TS-01: corpo I90 inclinado + dentes nas pontas
    for i in range(2, 9):
        y = Y_LIN[i - 1]
        for lado, (xa, xb) in zip("ab", PONTAS):
            a, b = xa + L_DENTE, xb - L_DENTE
            m.linear("viga", f"TS-01 L{i}{lado}", I90, (a, y, zf(a) + H_TS / 2), (b, y, zf(b) + H_TS / 2),
                     "Vigas I90 de cobertura", obs="inclinada 3 %, dentes 450×300, L 19,15 m")
            for xd in (xa + L_DENTE / 2, xb - L_DENTE / 2):
                m.bloco("viga", f"dente TS-01 L{i}{lado}", (xd, y, zf(xd) + H_TS), L_DENTE, 0.40, H_TS - H_DENTE, "Vigas I90 de cobertura")

    # vigas de borda VB 15×90 das fachadas 1 e 9 (sem dente, sobre CP-VB; acompanham o caimento)
    for y in (0.0, COMP):
        for xa, xb in itertools.pairwise(X_FACH):
            a, b = xa + (0.30 if xa == 0 else 0.20) + 0.025, xb - (0.30 if xb == LARG else 0.20) - 0.025
            m.linear("viga", "VB", VB, (a, y, zf(a) + 0.45), (b, y, zf(b) + 0.45), "Vigas de borda")
            for xx, sg in ((xa, 1), (xb, -1)):
                xc = xx + sg * ((0.30 if xx in (0.0, LARG) else 0.20) + 0.15)
                m.bloco("consolo", "CP-VB 30×40×35", (xc, y, zf(xx) - 0.01), 0.30, 0.40, 0.35, "Consolos")

    # 4. terças Ue 300 e telha
    for xa, _ in PONTAS:
        for s in LG["s_tercas"]:
            x = xa + s * C3 - 0.027
            zt = zf(x) + H_TS + 0.010 + TERCA.h / 2
            for k in range(len(Y_LIN) - 1):
                m.linear("terca", "Ue300", TERCA, (x, Y_LIN[k] + 0.01, zt), (x, Y_LIN[k + 1] - 0.01, zt), "Terças metálicas", material="aco")
    for k in range(int(COMP // 1.0)):
        y = 0.5 + k * 1.0
        z0, z1 = zf(0.18) + H_TS + 0.010 + 0.30 + 0.015, zf(LARG - 0.18) + H_TS + 0.010 + 0.30 + 0.015
        m.linear("placa", "telha", TELHA, (0.18, y, z0), (LARG - 0.18, y, z1), "Telhas", material="aco")

    # 5. mezanino (linhas 1–2): VM I90 com dentes nos CP-MEZ (fundo alinhado) e laje alveolar h20 + capa 5
    faces = [(0.30, X_EIXO["B"] - 0.20), (X_EIXO["B"] + 0.20, X_C - 0.20), (X_C + 0.20, X_EIXO["D"] - 0.20), (X_EIXO["D"] + 0.20, LARG - 0.30)]
    for nivel in NIVEIS_MEZ:
        zv = nivel - H_LAJE - I90.h / 2
        z_as = nivel - H_LAJE - 0.45 - 0.01
        for y in (Y_LIN[0], Y_LIN[1]):
            for fa, fb in faces:
                m.linear("viga", f"VM {nivel:+.2f}", I90, (fa + 0.05, y, zv), (fb - 0.05, y, zv), "Vigas de mezanino",
                         obs=f"I90 protendida, dentes 45×30, L = {fb - fa - 0.10:.2f} m; 2º estágio N9")
                for xx, sg in ((fa, 1), (fb, -1)):
                    m.bloco("consolo", "CP-MEZ 40×30×44", (xx + sg * 0.15, y, z_as), 0.30, 0.40, hC("CP-MEZ"), "Consolos")
                    m.bloco("inserto", "PN-1 pino Ø20 (VM)", (xx + sg * 0.15, y, z_as + 0.40), 0.02, 0.02, 0.70, "Pinos, tubos e neoprenes")
        for x0, b_, mk in PAINEIS_MEZ:                              # mesma paginação da ND-LET-LA01 (30 LA-01 + 2 LA-02 por nível)
            x = (x0 + b_ / 2) / 1000
            perf = LAJE if b_ == 1250 else PerfilRetangular(0.70, H_LAJE, "Laje alveolar 70")
            m.linear("laje", f"{mk} {nivel:+.2f}", perf, (x, Y_LIN[0] + 0.10, nivel - H_LAJE / 2), (x, Y_LIN[1] - 0.10, nivel - H_LAJE / 2), "Laje alveolar")

    # 6. placas de fechamento: as mesmas peças das pranchas PP (fechamento.py, vistas do R01)
    PL = PerfilRetangular(0.15, 1.25, "Placa 125×15 protendida")
    o_ext, o_c = 0.30 + 0.025 + 0.075, 0.20 + 0.025 + 0.075
    pos = {"A": ("x", COMP + o_ext), "I": ("x", -o_ext), "G": ("x", Y_LIN[1] + o_ext), "C": ("x", Y_LIN[LINHA_PORTOES] + o_c),
           "B": ("y", -o_ext), "E": ("y", -o_ext), "H": ("y", -o_ext), "D": ("y", LARG + o_ext), "F": ("y", LARG + o_ext), "J": ("y", LARG + o_ext)}
    for V, (pecas, ca1, _) in FCH.DADOS.items():
        ax, c = pos[V]
        for pc in pecas:
            s0, s1, z = pc["s0"] / 1000, pc["s1"] / 1000, (pc["z0"] + pc["z1"]) / 2000
            p0, p1 = ((s0, c, z), (s1, c, z)) if ax == "x" else ((c, s0, z), (c, s1, z))
            m.linear("placa", f"{pc['id']} (vista {V})", PL, p0, p1, "Placas de fechamento", obs=f"L = {pc['L']} mm; apoio: {pc['apoio']}")
    # vigas de travamento VT 25×60 (+7,50/+8,10) nos eixos A e E, linhas 2 a 9 (vistas B, D, E, F), com consolos CP-VT
    VT = PerfilRetangular(0.25, 0.60, "VT 25x60")
    for i in range(1, 8):
        for x in (0.0, LARG):
            ya, yb = Y_LIN[i] + 0.20 + 0.025, Y_LIN[i + 1] - 0.20 - 0.025
            m.linear("viga", f"VT L{i+1}-L{i+2}", VT, (x, ya, 7.80), (x, yb, 7.80), "Vigas de travamento VT", obs="dentes 30×20; fundo +7,50")
            for yy, sg in ((Y_LIN[i], 1), (Y_LIN[i + 1], -1)):
                m.bloco("consolo", "CP-VT 25×20×29", (x, yy + sg * (0.20 + 0.10), 7.79), 0.25, 0.20, hC("CP-VT"), "Consolos")

    # 7. insertos e ligações (conferência no 3D)
    INS, PIN = "Insertos metálicos", "Pinos, tubos e neoprenes"
    for i in range(2, 9):
        y = Y_LIN[i - 1]
        for xp in LG["X_PINO"]:
            z_as = ass_ts(xp)
            m.bloco("inserto", "PN-1 pino Ø20 L=700", (xp, y, z_as + 0.40), 0.02, 0.02, 0.70, PIN)
            m.bloco("inserto", "NEO-1 300×150×10", (xp, y, z_as + 0.01), 0.30, 0.15, 0.01, PIN)
        for xa, _ in PONTAS:
            for k, s_ in enumerate(LG["s_tercas"]):
                x = xa + s_ * C3 - 0.027
                no_ = k % 2 == 0
                m.bloco("inserto", "CH-T2 300×380×12,5 (nó do X)" if no_ else "CH-T1 200×200×12,5", (x, y, zf(x) + H_TS + 0.0125),
                        0.30 if no_ else 0.20, 0.38 if no_ else 0.20, 0.0125, INS)
                m.bloco("inserto", "CH-MF 150×360×12,5", (x, y, zf(x)), 0.15, 0.36, 0.0125, INS)
    for V, (pecas, ca1, _) in FCH.DADOS.items():                            # IP-01: uma por ponta de placa, na face do pilar
        ax, c = pos[V]
        for pc in pecas:
            for s in (pc["s0"] / 1000 + 0.05, pc["s1"] / 1000 - 0.05):
                z = pc["z1"] / 1000 - 0.175
                pt = (s, c, z) if ax == "x" else (c, s, z)
                m.bloco("inserto", "IP-01 150×150×9,5 + CL-1", pt, 0.15, 0.15, 0.15, INS)
        for (s, z0) in ca1:
            pt = (s / 1000, c, z0 / 1000) if ax == "x" else (c, s / 1000, z0 / 1000)
            m.bloco("inserto", "CA-1 consolo metálico", pt, 0.20, 0.20, 0.016, INS)

    # 8. piso e fundações (indicativos): piso de concreto 15 cm e blocos de fundação com cálice sob cada pilar
    m.linear("laje", "PISO e=15 (indicativo)", PerfilRetangular(LARG + 1.0, 0.15), (LARG / 2, -0.5, -0.075), (LARG / 2, COMP + 0.5, -0.075), "Piso e fundações")
    for peca in list(m.pecas):
        if peca.tipo == "pilar":
            x, y, _ = peca.p0
            bx, by = peca.perfil.b + 0.9, peca.perfil.h + 0.9
            m.bloco("fundacao", f"BLOCO/CÁLICE {peca.marca} (indicativo)", (x, y, -1.0 + 0.0), max(bx, 1.5), max(by, 1.5), 1.2, "Piso e fundações")

    pl = LG["platibanda"]
    m.pendente(f"Cobertura escondida: telha junto ao P2 em +{pl['telha_P2']:.3f}, {pl['folga_P2_mm']} mm abaixo da platibanda +10,00; "
               f"junto ao P1 em +{pl['telha_P1']:.3f}.")
    m.pendente("Laje alveolar h20 + 5 do mezanino (9,35 m, 500 kgf/m²) com 8 Ø12,7: MRd 215 ≥ 192 kN·m por painel; ELS-D ok (−0,91 MPa). Confirmar com a tabela do fabricante.")
    m.pendente("! Pórtico global (OpenSeesPy, P-Δ): ELU ok (γz 1,035); ELS frequente 9,3 mm em x — passa H/500 (17 mm), não passa H/1700 (5,9 mm). Definir o limite com o cliente.")
    m.pendente("! Pilares P6 e P7 do R01 (anexo) sem função definida: fora do modelo e das pranchas até confirmação.")
    m.pendente("Consolos sem chanfro com h = altura da viga − dente − neoprene (fundos alinhados): CP-TS/CV-TS/CP-MEZ 44, CP-I110 41, CP-VB 35, CP-VT 29 cm; nenhum precisou de mísula (NBR 9062:2017 7.3).")
    m.pendente("Vigas do mezanino em I90 com dentes 45×30 (dente da I70 reprovado no MEF): assentos CP-MEZ +2,45 / +5,85; pé-direito livre sob a viga = nível − 1,15 m.")
    m.pendente("Geometria do R01: 79,35 m entre os eixos 1 e 9 e 39,50 m entre A e E; TS-01 com 19,15 m. Pilares laterais com a cabeça recuada (40×30) acima de +8,40 (A) / +9,55 (E) (aprovado).")
    m.pendente("Terças, laje, consolos e dentes como envelope; contraventamento em X (nó a nó), correntes e mãos-francesas nas pranchas COB01/COB02, não modelados no 3D.")
    m.pendente("Placas conforme a locação do R01 (vistas A–J); vistas E/F (docas) e centro da fachada 1 sem placas — a confirmar; VT/VV 25×60 de +7,50 a +8,10 com dentes Gerber nos consolos CP-VT; portões na linha 4.")
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
                 ("ND-LET-PIL-A01", "pilar PL-01 armado (opção A) — cabeça recuada 40×30"), ("ND-LET-PIL-P01", "pilar PL-01 protendido (opção B) — cabeça recuada 40×30"), ("ND-LET-PC01", "pilar central PC-01 (P8A)"), ("ND-LET-PC02", "pilar central PC-02 (P11)"), ("ND-LET-PC03", "pilar central PC-03 (P13)"),
                 ("ND-LET-PM01", "pilares do mezanino PM-01"), ("ND-LET-PG01", "pilares dos portões PG-01 (P9, P12)"), ("ND-LET-PG02", "pilares dos portões PG-02 (P10)"), ("ND-LET-TS01-COB-rev02", "TS-01 fôrma, armação, chaparia; cobertura metálica COB01 (enterçamento e travamento, ST-1, mão-francesa) e COB02 (X nó a nó, correntes, tirantes, diagonais)"),
                 ("ND-LET-I110", "vigas centrais I110 V405/406/407"), ("ND-LET-VB01", "vigas de borda VB-01 a VB-04"), ("ND-LET-VM01", "vigas do mezanino VM-01 e VM-02"),
                 ("ND-LET-LA01", "lajes alveolares do mezanino"), ("ND-LET-CM01", "placas de fechamento — locação e ordem das vistas (R01)"),
                 ("ND-LET-PP00", "placa protendida típica — fôrma, protensão, insertos, ligações"), ("ND-LET-PP-I", "placas da vista I (produção e montagem)"),
                 ("ND-LET-PP-HJ", "placas das vistas H e J"), ("ND-LET-PP-G", "placas da vista G"), ("ND-LET-PP-EF", "placas das vistas E e F"),
                 ("ND-LET-PP-C", "placas da vista C (portões)"), ("ND-LET-PP-B", "placas da vista B"), ("ND-LET-PP-D", "placas da vista D"),
                 ("ND-LET-PP-A", "placas da vista A"), ("ND-LET-VT01", "vigas de travamento 25×60 (+7,50/+8,10)")]
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
