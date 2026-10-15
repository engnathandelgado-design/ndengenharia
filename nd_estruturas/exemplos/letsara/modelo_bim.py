"""Letsara — modelo BIM (IFC + página 3D) a partir das definições de projeto. Revisão de 12/10/2026 (tarde).

Rodar: PYTHONPATH=. python exemplos/letsara/modelo_bim.py [pasta_de_saida]
Saída (em saidas/, fora do git): letsara.ifc e letsara_3d.html (publicar a página como artefato para ver no celular).

Geometria = a mesma da checagem de ligações (ligacoes.json) e do modelo global:
- eixos Y (linhas 1 a 9) e X (A a E) do R01 como usados nos cálculos;
- rev03 (14/10/2026): cobertura rebaixada (TP40 + lã 40 + zipada + painéis solares) com ≥ 15 cm de folga à platibanda (+10,00);
- TS-01 sem dentes, apoiada no recuo dos pilares laterais e no topo da I130 / pilares centrais (neoprene + 2 pinos);
- vigas centrais I130 (h 1,30) com dente 78 × 35 nos consolos CP-I130;
- terças Ue 300×2,65 c/1,20 m, ligações todas parafusadas (sem solda); mezanino com laje alveolar h20 + 5 sobre vigas I90.
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
VB = PerfilRetangular(0.15, 0.90, "VB 15x90")
TERCA = PerfilRetangular(0.085, 0.30, "Ue300x85x25x2,65 (envelope)")
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
    # pilares das fachadas 1 e 9 (60 ⊥ fachada) com cabeça recuada acima da VB
    for j, x in enumerate(X_FACH[1:-1]):
        for nome, y, sg in ((["P3", "P4", "P5"][j], 0.0, 1), (["P3", "P14", "P5"][j], COMP, -1)):
            zr = rec_vb(x)
            m.pilar(f"{nome}-L{1 if sg > 0 else 9}", x, y, 0.40, 0.60, Z_CALICE, zr, obs="60 ⊥ fachada; cabeça recuada acima da VB")
            m.pilar(f"{nome}-L{1 if sg > 0 else 9} cabeça", x, y - sg * 0.15, 0.40, 0.30, zr, TOPO_PLAT, obs="cabeça 40×30")
    # centrais (R01): P8A 40×60, P11 40×40, P13 60×60 — topo +8,88 (topo da I130)
    for (marca, y), (bx, by) in zip(CENTRAIS, ((0.40, 0.60), (0.40, 0.40), (0.60, 0.60))):
        m.pilar(marca, X_C, y, bx, by, Z_CALICE, Z_I130_TOPO, obs=f"{bx*100:.0f}×{by*100:.0f}; apoio I130 / TS-01")
    for marca, x in (("P8", X_EIXO["B"]), ("P8B", X_EIXO["D"])):
        m.pilar(marca, x, Y_LIN[1], 0.40, 0.60, Z_CALICE, NIVEIS_MEZ[1], obs="mezanino 40×60")
    # pilares dos portões (linha 4): P9, P12 40×40 e P10 25×25, topo +7,40 (rev03; a TS-01 passa por cima)
    for nome, x, b_ in (("P9", 9.87, 0.40), ("P10", 15.195, 0.25), ("P10", 24.305, 0.25), ("P12", 29.63, 0.40)):
        m.pilar(nome, x, Y_LIN[LINHA_PORTOES], b_, b_, Z_CALICE, 7.40, obs="parede dos portões (vista C), topo +7,40")

    # 2. vigas centrais I130 (comprimentos do R01) e consolos CP-I130 / CV-TS
    zc = Z_I130_TOPO - H_I130 / 2
    meia = {Y_LIN[1]: 0.30, Y_LIN[3]: 0.20, Y_P13: 0.30, Y_LIN[8]: 0.30}
    z_ass_i110 = LG["Z_ASS_I130"]
    for marca, ya, yb in I130_TRECHOS:
        y0, y1 = ya + meia[ya] + 0.075, yb - meia[yb] - 0.075
        m.linear("viga", marca, I130, (X_C, y0, zc), (X_C, y1, zc), "Vigas centrais I130",
                 obs=f"L = {y1 - y0:.3f} m; protendida 26 cord. Ø12,7 (V407: 16) + 4 Ø20 na mesa superior; dente 780 × 350")
        for yy, sg in ((ya, 1), (yb, -1)):
            m.bloco("consolo", f"CP-I130 {marca}", (X_C, yy + sg * (meia[yy] + 0.20), z_ass_i110), 0.50, 0.40, hC("CP-I130"), "Consolos")

    # 3. TS-01: I90 inclinada, sem dentes (rev03)
    for i in range(2, 9):
        y = Y_LIN[i - 1]
        for lado, (xa, xb) in zip("ab", PONTAS):
            m.linear("viga", f"TS-01 L{i}{lado}", I90, (xa, y, zf(xa) + H_TS / 2), (xb, y, zf(xb) + H_TS / 2),
                     "Vigas I90 de cobertura", obs=f"inclinada 3 %, sem dentes, L {LG['L_TS']:.2f} m; 8 cord. Ø12,7")

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
        z0, z1 = zf(0.18) + H_TS + 0.010 + 0.30 + TELHA.h / 2, zf(LARG - 0.18) + H_TS + 0.010 + 0.30 + TELHA.h / 2
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
    # vigas de travamento VT 25×60 nos eixos A (+6,25/+6,85) e E (+7,50/+8,10), linhas 2 a 9, com consolos CP-VT
    VT = PerfilRetangular(0.25, 0.60, "VT 25x60")
    for i in range(1, 8):
        for x, zv, zass in ((0.0, 6.55, 6.54), (LARG, 7.80, 7.79)):
            ya, yb = Y_LIN[i] + 0.20 + 0.025, Y_LIN[i + 1] - 0.20 - 0.025
            m.linear("viga", f"VT L{i+1}-L{i+2}", VT, (x, ya, zv), (x, yb, zv), "Vigas de travamento VT", obs=f"dentes 30×20; fundo +{zv - 0.30:.2f}".replace(".", ","))
            for yy, sg in ((Y_LIN[i], 1), (Y_LIN[i + 1], -1)):
                m.bloco("consolo", "CP-VT 25×20×29", (x, yy + sg * (0.20 + 0.10), zass), 0.25, 0.20, hC("CP-VT"), "Consolos")

    # 7. insertos e ligações (conferência no 3D)
    INS, PIN = "Insertos metálicos", "Pinos, tubos e neoprenes"
    for i in range(2, 9):
        y = Y_LIN[i - 1]
        for xp, nome_, neo in ((LG["NEO_EXT"]["xc"], "2 PN-3 Ø25 + NEO-4", (0.20, 0.30)), (LG["NEO_CEN"]["xc"], "2 PN-5 Ø20 + NEO-3", (0.10, 0.30)),
                               (2 * X_C - LG["NEO_CEN"]["xc"], "2 PN-5 Ø20 + NEO-3", (0.10, 0.30)), (LARG - LG["NEO_EXT"]["xc"], "2 PN-3 Ø25 + NEO-4", (0.20, 0.30))):
            z_as = zf(xp) - 0.01
            for dy in (-0.10, 0.10):
                m.bloco("inserto", nome_, (xp, y + dy, z_as + 0.30), 0.025, 0.025, 0.60, PIN)
            m.bloco("inserto", nome_, (xp, y, z_as + 0.005), neo[0], neo[1], 0.01, PIN)
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
    m.pendente("! Pórtico global (OpenSeesPy, P-Δ): ELU ok; ELS frequente 9,9 mm em x — passa H/500 (17 mm), não passa H/1700 (5,9 mm). Definir o limite com o cliente.")
    m.pendente("! Pé-direito: fundo da TS-01 em +7,19 junto ao eixo A (antes +7,46); mezanino superior (+6,55) com fundo das terças a +8,10 junto ao eixo A — conferir o uso.")
    m.pendente("! Vista E (eixo A, linhas 2–4) aberta só até +6,25: VT do eixo A rebaixada para +6,25/+6,85 (CP-VT abaixo do recuo +7,19).")
    m.pendente("! Painéis solares adotados com 0,15 kN/m² e instalações 0,10 kN/m²: confirmar com o fornecedor.")
    m.pendente("! Pilares P6 e P7 do R01 (anexo) sem função definida: fora do modelo e das pranchas até confirmação.")
    m.pendente("TS-01 sem dentes: apoio 27,5 cm no recuo dos pilares laterais (NEO-4 + 2 PN-3 Ø25) e 16,25 cm no topo da I130 / pilares centrais (NEO-3 + 2 PN-5 Ø20).")
    m.pendente("Todas as ligações metálicas parafusadas (sem solda): ST-1P nas esperas ES-1, OR-X nas ES-2, mão-francesa no CMF-1 das ES-3; placas com trilho TR-1 + bucha BR-1 + CL-1 e consolo CA-1 parafusado.")
    m.pendente("Terças, laje, consolos e pacote da cobertura como envelope; contraventamento em X, correntes e mãos-francesas nas pranchas COB01/COB02, não modelados no 3D.")
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
                 ] + [(f"ND-LET-AR-PIL-{k:02d}", f"armaduras dos pilares — folha {k} de 6 (padrão de armação)") for k in range(1, 7)] + [(f"ND-LET-AR-VIG-{k:02d}", f"armaduras das vigas — {t}") for k, t in enumerate(("TS-01", "I130", "VM", "VB", "VT"), 1)] + [] + [(f"ND-LET-{m.replace('-', '')}", f"pilar {m} (família 40×60)") for m in ("PL-01", "PL-02", "PL-03", "PL-04", "PL-05", "PL-06", "PL-07", "PL-08", "PL-09", "PL-10", "PL-11", "PL-12", "PF-01", "PF-02", "PF-03", "PF-04", "PF-05", "PF-06")] + [ ("ND-LET-PC01", "pilar central PC-01 (P8A)"), ("ND-LET-PC02", "pilar central PC-02 (P11)"), ("ND-LET-PC03", "pilar central PC-03 (P13)"),
                 ("ND-LET-PM01", "pilares do mezanino PM-01"), ("ND-LET-PG01", "pilares dos portões PG-01 (P9, P12)"), ("ND-LET-PG02", "pilares dos portões PG-02 (P10)"), ("ND-LET-TS01-1", "TS-01 fôrma"), ("ND-LET-TS01-2", "TS-01 armação e protensão"), ("ND-LET-TS01-3", "TS-01 esperas e peças de ligação"), ("ND-LET-COB01", "cobertura metálica: enterçamento, ST-1P, mão-francesa (sem solda)"), ("ND-LET-COB02", "cobertura metálica: contraventamento X, correntes, tirantes"),
                 ("ND-LET-I130", "vigas centrais I130 V405/406/407"), ("ND-LET-VB01", "vigas de borda VB-01 a VB-04"), ("ND-LET-VM01", "vigas do mezanino VM-01 e VM-02"),
                 ("ND-LET-LA01", "lajes alveolares do mezanino"), ("ND-LET-CM01", "placas de fechamento — locação e ordem das vistas (R01)"),
                 ("ND-LET-PP00", "placa protendida típica — fôrma, protensão, insertos, ligações"), ("ND-LET-PP-I", "placas da vista I (produção e montagem)"),
                 ("ND-LET-PP-HJ", "placas das vistas H e J"), ("ND-LET-PP-G", "placas da vista G"), ("ND-LET-PP-EF", "placas das vistas E e F"),
                 ("ND-LET-PP-C", "placas da vista C (portões)"), ("ND-LET-PP-B", "placas da vista B"), ("ND-LET-PP-D", "placas da vista D"),
                 ("ND-LET-PP-A", "placas da vista A"), ("ND-LET-VT01", "vigas de travamento 25×60 (A +6,25 / E +7,50)")]
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
