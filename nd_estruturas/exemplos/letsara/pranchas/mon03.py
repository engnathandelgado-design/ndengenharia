"""ND-LET-MON03 — PLANO DE MONTAGEM DO FECHAMENTO LATERAL E SEQUÊNCIA GERAL DA OBRA (rev executiva, 21/10/2026).

PLANTA (1:200): paredes de placas (vistas A a J do R01), ordem de montagem das paredes e sentido de montagem vão a vão.
ELEVAÇÃO TÍPICA (1:50): vista B, linhas 5 a 7 — ordem das placas no vão (de baixo para cima), consoles nos nichos NC-1, pinos
guia PT-1 na junta de baixo, alças AL-P do topo, folgas de 0,5 cm na altura e 2 cm no comprimento (junta no eixo do pilar).
DETALHE 1 (1:10): junta no pilar vista de fora. DETALHE 2 (1:50): içamento da placa de pé pelas 2 alças do topo.
Tabelas: sequência geral da obra e içamento por tipo de peça (pesos da lista de peças). Dados de fechamento.py (mesmas peças das
pranchas PP) e de placas.json. A0."""
import json, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from prancha_nd import Prancha
from geometria import Y_LIN, X_EIXO
import fechamento as FCH
import pecas_obra as QT

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
PLJ = json.load(open(AQ + "placas.json"))
PQ = QT.PQ
import json as _jj
_IJ3 = _jj.load(open('/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/i110_r01.json'))
fd = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
M = lambda v: v * 1000
YL = [M(y) for y in Y_LIN]
XA = {k: M(v) for k, v in X_EIXO.items()}
COMP, LARG = YL[-1], XA["E"]
H_PL, JUNTA, E_PL = FCH.H_PL, FCH.JUNTA, FCH.E_PL
FOLGA_H = 5                                                # junta horizontal (cada placa no seu par de consoles)
ORDEM = ["C", "G", "I", "H", "J", "E", "F", "B", "D", "A"]       # decisão 21/10: C antes da TS-01 L4; G antes da TS-01 L2 (após o mezanino); externas no fim
PESO_PL = max(PQ[m][7] for m in PQ if m.startswith("PP-"))

pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="PLANO DE MONTAGEM DO FECHAMENTO LATERAL (PLACAS) E SEQUÊNCIA GERAL DA OBRA — IÇAMENTO E EQUIPAMENTOS",
                        desenho="ND-LET-MON03", folha="03/03", fase="EXECUTIVO", rev="00"))
pr.revisao("00", "21/10/2026", "EMISSÃO: MONTAGEM DAS PLACAS POR PAREDE, ELEVAÇÃO TÍPICA, JUNTAS, IÇAMENTO E SEQUÊNCIA DA OBRA")
Q = pr.quadro

# ================================================================== PLANTA 1:200 — paredes e ordem
E1 = 200
v = pr.vista("PLANTA", (Q[0] + 62, Q[3] - 245), E1, titulo="PLANTA DE MONTAGEM DO FECHAMENTO — ORDEM DAS PAREDES",
             subtitulo="número no círculo = ordem de montagem da parede; seta = sentido vão a vão; placas por fora dos pilares (paredes internas G e C do lado do pavilhão)", unidade="cm")
for k, y in enumerate(YL):
    v.linha((y, -2200), (y, LARG + 2200), "EIXO")
    v.circulo((y, LARG + 3200), 900, "BOLHA"); v.texto((y, LARG + 3200), str(k + 1), "nota", "MIDDLE_CENTER")
for nm, x in XA.items():
    v.linha((-2200, x), (COMP + 2200, x), "EIXO")
    v.circulo((-3200, x), 900, "BOLHA"); v.texto((-3200, x), nm, "nota", "MIDDLE_CENTER")
for y in YL:
    for nm, x in XA.items():
        if nm in "AE" or y in (YL[0], YL[1], YL[3], YL[8]):
            v.ret(y - 200, x - 300, 400, 600, "CORTADO")
O = 375
PAREDE = {  # vista: (eixo da placa na planta: 'h' = ao longo de y obra (horizontal), posição, início, fim)
    "I": ("v", -O, 0, LARG), "H": ("h", -O, 0, YL[1]), "J": ("h", LARG + O, 0, YL[1]), "G": ("v", YL[1] + O, 0, LARG),
    "E": ("h", -O, YL[1], YL[3]), "F": ("h", LARG + O, YL[1], YL[3]), "C": ("v", YL[3] + 275, 0, LARG),
    "B": ("h", -O, YL[3], COMP), "D": ("h", LARG + O, YL[3], COMP), "A": ("v", COMP + O, 0, LARG)}
NOTA_P = {"I": "fachada linha 1", "H": "anexo, eixo A", "J": "anexo, eixo E", "G": "interna, linha 2", "E": "eixo A, L2–L4 (alto)",
          "F": "eixo E, L2–L4 (alto)", "C": "interna, portões", "B": "lateral eixo A", "D": "lateral eixo E", "A": "fachada linha 9"}
for ordem, V in enumerate(ORDEM, 1):
    d_, pos, a, b = PAREDE[V]
    n = len(FCH.DADOS[V][0])
    if d_ == "h":
        pts = [(a, pos - 50), (b, pos - 50), (b, pos + 50), (a, pos + 50)]
        c = ((a + b) / 2 + 2500, pos + (-1300 if pos < 0 else 1300))
        seta = [(a + 600, pos + (-650 if pos < 0 else 650)), (a + 3000, pos + (-650 if pos < 0 else 650))]
    else:
        pts = [(pos - 50, a), (pos + 50, a), (pos + 50, b), (pos - 50, b)]
        c = (pos + (-1300 if pos < 0 else 1300), (a + b) / 2 + 4900)               # fora do eixo C
        seta = [(pos + (-650 if pos < 0 else 650), a + 600), (pos + (-650 if pos < 0 else 650), a + 3000)]
    v.poli(pts, "CORTADO", True); v.hachura(pts, "SOLID", 1)
    v.circulo(c, 650, "INDICACAO"); v.texto(c, str(ordem), "sub", "MIDDLE_CENTER")
    v.poli(seta, "INDICACAO")
    tx, ty = seta[1]
    if d_ == "h":
        v.poli([(tx, ty), (tx - 400, ty + 160), (tx - 400, ty - 160), (tx, ty)], "INDICACAO", True)
    else:
        v.poli([(tx, ty), (tx + 160, ty - 400), (tx - 160, ty - 400), (tx, ty)], "INDICACAO", True)
lin_p = []
for ordem, V in enumerate(ORDEM, 1):
    pc = FCH.DADOS[V][0]
    lin_p.append([str(ordem), V, NOTA_P[V], str(len(pc)), {"A": "PP-A", "B": "PP-B", "C": "PP-C", "D": "PP-D", "E": "PP-EF", "F": "PP-EF", "G": "PP-G",
                                                         "H": "PP-HJ", "J": "PP-HJ", "I": "PP-I"}[V]])
pr.tabela(Q[0] + 300, Q[3] - 330, "ORDEM DE MONTAGEM DAS PAREDES", ["ORDEM", "VISTA", "PAREDE", "PLACAS", "FOLHA"], lin_p, [16, 14, 56, 18, 26], h_lin=5.0)

# ================================================================== ELEVAÇÃO TÍPICA 1:50 — vista B, linhas 5 a 7
E2 = 50
ya_, yb_ = YL[4], YL[6]
w = pr.vista("ELEVACAO", (Q[0] + 515 - ya_ / E2, Q[3] - 250), E2, titulo="ELEVAÇÃO TÍPICA DE MONTAGEM — VISTA B (EIXO A, LINHAS 5 A 7), VISTA DE FORA",
             subtitulo="número = ordem de montagem no vão (de baixo para cima, vão a vão no sentido da seta); pilares ocultos atrás das placas", unidade="cm")
pecas, cons, _ = FCH.DADOS["B"]
sel = [p for p in pecas if p["s0"] >= ya_ - 50 and p["s1"] <= yb_ + 50]
for y in (YL[4], YL[5], YL[6]):                           # pilares atrás (40 em y) e eixos
    w.poli([(y - 200, 0), (y + 200, 0), (y + 200, 10000), (y - 200, 10000)], "OCULTA", True)
    w.linha((y, -900), (y, 10700), "EIXO")
    w.circulo((y, -1400), 400, "BOLHA"); w.texto((y, -1400), str(YL.index(y) + 1), "sub", "MIDDLE_CENTER")
w.linha((ya_ - 1200, 0), (yb_ + 1200, 0), "TERRENO")
for p in sel:
    s0, s1, z0, z1 = p["s0"], p["s1"], p["z0"] + (FOLGA_H if p["k"] > 0 else 0), p["z1"]
    w.poli([(s0, z0), (s1, z0), (s1, z1), (s0, z1)], "VISTA", True)
    w.circulo(((s0 + s1) / 2, (z0 + z1) / 2), 220, "INDICACAO"); w.texto(((s0 + s1) / 2, (z0 + z1) / 2), str(p["seq"]), "nota", "MIDDLE_CENTER")
    w.texto(((s0 + s1) / 2 + 400, (z0 + z1) / 2), p["id"], "min", "MIDDLE_LEFT")
    for xa in (s0 + 0.21 * p["L"], s1 - 0.21 * p["L"]):   # alças AL-P do topo (montagem em pé)
        w.poli([(xa - 60, z1), (xa - 60, z1 + 120), (xa + 60, z1 + 120), (xa + 60, z1)], "ARMADURA")
    if p["k"] > 0:
        for xp in (s0 + FCH.X_PT(p["L"]), s1 - FCH.X_PT(p["L"])):   # pinos guia PT-1 na junta de baixo
            w.circulo((xp, z0), 60, "OCULTA")
for s_, z_ in cons:                                        # consoles nos nichos NC-1 das pontas
    if ya_ - 50 <= s_ <= yb_ + 50:
        for zc in (z_,):                                      # (s, z) já vem por fiada
            w.poli([(s_ - FCH.NC_B / 2, zc - FCH.NC_H / 2), (s_ + FCH.NC_B / 2, zc - FCH.NC_H / 2), (s_ + FCH.NC_B / 2, zc + FCH.NC_H / 2), (s_ - FCH.NC_B / 2, zc + FCH.NC_H / 2)], "OCULTA", True)
w.poli([(YL[5] + 1200, 10500), (YL[5] + 4500, 10500)], "INDICACAO")
w.poli([(YL[5] + 4500, 10500), (YL[5] + 4100, 10660), (YL[5] + 4100, 10340), (YL[5] + 4500, 10500)], "INDICACAO", True)
w.texto((YL[5] + 4800, 10500), "sentido de montagem: linha 4 → linha 9", "min", "MIDDLE_LEFT")
w.cota_h([YL[4], YL[5], YL[6]], 0, -14, total=False)
w.cota_v([k * H_PL for k in range(9)], yb_ + 900, 8, total=False)
w.chamada((YL[5], 3 * H_PL + 600), (16, 8), f"junta vertical {JUNTA / 10:g} cm no eixo do pilar (tarucel + PU)")
w.chamada((YL[4] + 2500, 2 * H_PL), (12, -6), f"junta horizontal {FOLGA_H / 10:g} cm (macho-fêmea, sem apoio entre placas)".replace(".", ","))
w.chamada((YL[5] + 70, FCH.Z_NC + 4 * H_PL), (12, 12), "console CS-1 / CC-1 no nicho NC-1 (2 por placa)")
p_ = [p for p in sel if p["k"] == 3][-1]
w.chamada((p_["s1"] - FCH.X_PT(p_["L"]), p_["z0"] + FOLGA_H), (-10, 4), "PT-1 pino guia (só na placa de baixo)")
p_ = [p for p in sel if p["k"] == 7][0]
w.chamada((p_["s0"] + 0.21 * p_["L"], p_["z1"] + 120), (8, 10), "AL-P alças de montagem (0,21 L)")

# ================================================================== DETALHE 1 — junta no pilar (vista de fora), 1:10
E3 = 10
d = pr.vista("DET1", (Q[0] + 110, 200 - 2 * H_PL / E3), E3, titulo="DETALHE 1 — JUNTAS NO PILAR (VISTA DE FORA)",
             subtitulo="cada placa nos seus 2 consoles; nenhuma placa apoia na outra; nichos NC-1 nas pontas", unidade="cm")
ZJ = 2 * H_PL                                              # junta entre as fiadas 1 e 2 (relativa)
d.poli([(-200, ZJ - 700), (200, ZJ - 700), (200, ZJ + 800), (-200, ZJ + 800)], "OCULTA", True)        # pilar atrás
d.linha((0, ZJ - 800), (0, ZJ + 900), "EIXO")
for sx in (-1, 1):
    xi = sx * JUNTA / 2
    for z0, z1 in ((ZJ - 650, ZJ), (ZJ + FOLGA_H, ZJ + 750)):
        x0, x1 = sorted((xi, sx * 650))
        d.poli([(x0, z0), (x1, z0), (x1, z1), (x0, z1)], "VISTA", True)
        if z1 > ZJ + 100 or z0 < ZJ - 100:
            pass
    for zc in (ZJ - H_PL + FCH.Z_NC, ZJ + FCH.Z_NC):
        if ZJ - 650 < zc < ZJ + 750:
            xc = sx * (JUNTA / 2 + FCH.X_CS)
            d.poli([(xc - FCH.NC_B / 2, zc - FCH.NC_H / 2), (xc + FCH.NC_B / 2, zc - FCH.NC_H / 2), (xc + FCH.NC_B / 2, zc + FCH.NC_H / 2), (xc - FCH.NC_B / 2, zc + FCH.NC_H / 2)], "OCULTA", True)
for sx in (-1, 1):
    d.interrupcao((sx * 650, ZJ - 650), (sx * 650, ZJ + 750))
d.cota_h([-JUNTA / 2 - 300, -JUNTA / 2], ZJ + 750, 10, total=False)
d.cota_h([JUNTA / 2, JUNTA / 2 + 300], ZJ + 750, 10, total=False)
d.cota_v([ZJ - 650, ZJ, ZJ + 750], 650, 12, total=False)
d.chamada((0, ZJ + 400), (76, 14), f"junta vertical {JUNTA / 10:g} cm: tarucel Ø25 + selante PU (±25 %)")
d.chamada((300, ZJ + FOLGA_H / 2), (50, -18), "junta horizontal 0,5 cm: macho-fêmea sem contato de carga")
d.chamada((JUNTA / 2 + FCH.X_CS, ZJ - H_PL + FCH.Z_NC - FCH.NC_H / 2), (82, -10), "nicho NC-1 + console (2 por placa)")
d.chamada((-200, ZJ - 500), (-12, -10), "pilar (oculto)")

# ================================================================== DETALHE 2 — içamento da placa de pé, 1:50
E4 = 50
Lp = PLJ["secao"]["L_max_m"] * 1000
q = pr.vista("DET2", (Q[0] + 300, 190), E4, titulo="DETALHE 2 — IÇAMENTO DA PLACA PARA MONTAGEM (DE PÉ)",
             subtitulo=f"2 alças AL-P no topo a 0,21 L; balancim e cabos verticais; maior placa {fd(Lp / 1000, 2)} m, {fd(PESO_PL, 2)} t", unidade="cm")
q.poli([(0, 0), (Lp, 0), (Lp, H_PL), (0, H_PL)], "VISTA", True)
xa = [0.21 * Lp, 0.79 * Lp]
for x in xa:
    q.poli([(x - 60, H_PL), (x - 60, H_PL + 120), (x + 60, H_PL + 120), (x + 60, H_PL)], "ARMADURA")
    q.linha((x, H_PL + 120), (x, H_PL + 1600), "METALICA")
q.poli([(xa[0] - 200, H_PL + 1600), (xa[1] + 200, H_PL + 1600), (xa[1] + 200, H_PL + 1750), (xa[0] - 200, H_PL + 1750)], "METALICA", True)
q.linha((xa[0], H_PL + 1750), (Lp / 2, H_PL + 3300), "METALICA"); q.linha((xa[1], H_PL + 1750), (Lp / 2, H_PL + 3300), "METALICA")
q.circulo((Lp / 2, H_PL + 3450), 150, "METALICA")
q.cota_h([0, xa[0], xa[1], Lp], 0, -10, total=False)
q.chamada((xa[1] + 200, H_PL + 1675), (10, 0), "balancim (cabos verticais nas alças)")
q.chamada((xa[1], H_PL + 60), (12, 14), f"AL-P: {PLJ['transitorias']['F_alca_kN']:.1f} kN por alça (cálculo, βa 1,3)".replace(".", ","))
q.texto((Lp / 2, H_PL / 2), "placa de pé — face externa para fora", "nota", "MIDDLE_CENTER")

# ================================================================== TABELAS: sequência geral e içamento
seq = [["1", "Locação dos cálices e conferência dos níveis", "±1,0 cm em planta; fundo nivelado", "LOC01, CG01"],
       ["2", "Pilares, todas as linhas", "aprumar, cunhar, grautear no dia; 24 h e graute ≥ 15 MPa", "MON01"],
       ["3", "Vigas centrais I130 (V407, V406, V405, V404)", "NEO-2; PN-2 grauteado numa ponta", "MON01, CT03, CT04"],
       ["4", "Parede C (linha 4) — antes da TS-01 da linha 4", "cada placa nos seus 2 consoles", "MON03, PP-C"],
       ["5", "TS-01 L8 → L3 e VB-05 a VB-08 (guindaste de ré)", "pinos nos TB-3; VB escoradas", "MON01, CT04"],
       ["6", "Cobertura dos vãos 3–4 a 8–9 (terças, correntes, X, telhas)", "tudo parafusado; atrás do guindaste", "COB01 a COB04"],
       ["7", "Mezanino +3,90 e +7,30: VM, pontas concretadas (fcj ≥ 20), lajes, 2º estágio, capa; escada", "cobertura dos vãos 1–3 aberta; capa ≥ 20 MPa", "MON02, CT02"],
       ["8", "Parede G (linha 2) — antes da W 310 da linha 2", "cada placa nos seus 2 consoles", "MON03, PP-G"],
       ["9", "W 310 da linha 2, VB-01 a VB-04, terças dos vãos 1–2 e 2–3", "ST-W e MF-1 em toda terça da linha 2", "MON01, COB01, COB05"],
       ["10", "Placas externas I, H, J, E, F, B, D e A (por fora)", "guindaste no perímetro", "MON03, PP"],
       ["11", "Telhas, rufos e calhas dos vãos 1–3; acabamentos", "após a estrutura travada", "COB03, COB04"]]
yt = pr.tabela(Q[0] + 560, Q[3] - 330, "SEQUÊNCIA GERAL DA OBRA", ["ETAPA", "SERVIÇO", "CONDIÇÃO PARA SEGUIR", "FOLHAS"], seq, [13, 118, 104, 44], h_lin=5.2)
pz = lambda mks: max(PQ[m][7] for m in mks)
Lz = lambda mks: max(PQ[m][4] for m in mks)
pil = [m for m in PQ if m[:2] in ("PL", "PF", "PC", "PM", "PG")]
ica = [["Pilares", fd(pz(pil), 1), fd(Lz(pil), 2), "2 alças AL-2 (desforma) + furo FI-1 (verticalizar e montar)", "pino passante + 2 manilhas"],
       ["I130 (V404, V405, V406, V407)", fd(pz(["V404", "V405", "V406", "V407"]), 1), fd(Lz(["V404", "V405", "V406", "V407"]), 2), f"2 alças AL-3 ({_IJ3['V407']['icamento']['n_lacos']} laços cada)", "balancim"],
       ["TS-01", fd(pz(["TS-01"]), 1), fd(Lz(["TS-01"]), 2), "4 alças AL-1", "2 balancins, cabos verticais"],
       ["VM-01 / VM-02", fd(pz(["VM-01", "VM-02"]), 1), fd(Lz(["VM-01", "VM-02"]), 2), "2 alças AL-1", "cabos ≥ 45°"],
       ["VB-01 a VB-08", fd(pz([f"VB-0{k}" for k in range(1, 9)]), 1), fd(Lz([f"VB-0{k}" for k in range(1, 9)]), 2), "2 alças AL-1", "escorar após montar"],
       ["Lajes LA-01/01R/02", fd(pz(["LA-01", "LA-01R", "LA-02"]), 1), fd(Lz(["LA-01"]), 2), "garra mecânica nas 2 pontas", "sem alça embutida"],
       ["Placas PP", fd(PESO_PL, 1), fd(Lp / 1000, 2), "2 alças AL-P no topo (montagem de pé)", "balancim; desforma por 4 IZ-1"]]
pr.tabela(Q[0] + 560, yt - 6, "IÇAMENTO POR TIPO DE PEÇA (PESO DA PEÇA MAIS PESADA)", ["PEÇA", "PESO (t)", "L (m)", "PONTOS DE IÇAMENTO", "ACESSÓRIO"],
          ica, [38, 16, 14, 128, 83], h_lin=5.2)

# ------------------------------------------------------------------ notas
notas = [f"Placas protendidas 125 × 10 (10 fios Ø6 CP-175 RB), dimensionadas só pelo peso próprio; cada placa é independente nos seus 2 consoles: folga de {FOLGA_H / 10:g} cm na altura (junta macho-fêmea sem contato de carga) e {JUNTA / 10:g} cm no comprimento (junta no eixo do pilar). O pino PT-1 é só guia de montagem: parafusado na placa de baixo, solto na de cima.".replace(".", ",").replace("125 × 10", "125 × 10"),
         "Montagem de cada parede vão a vão no sentido da seta e, em cada vão, de baixo para cima (número da elevação). A placa desce encostada no pilar com o braço do console entrando no nicho NC-1 até o teto apoiar no M16 de nível; aferir o afastamento pelo prisioneiro frontal; instalar os PT-1 (ou as travas PT-2 no pé das placas de pacote suspenso) antes de soltar o guindaste (ND-LET-PP00 e PP01).",
         "Consoles: os da face C dos pilares já vêm concretados (CC-1); nos pilares das faces laterais e das paredes internas, soldar o CS-1 na CE-1 no nível da topografia antes da placa (ND-LET-PP03).",
         "As placas são montadas de pé e concretadas deitadas: desforma por 4 insertos IZ-1 numa face com balancim, basculamento e estocagem EM PÉ em cavalete; transporte em pé (cavalete A). Não estocar nem transportar deitada (empena).",
         "Sequência (decisão do Nathan, 21/10/2026): pilares → vigas → cobertura → mezanino → fechamento. Não dá para cumprir 100 % com guindaste: (a) a laje de 9,55 m não passa entre a VB da linha 1 e a W 310 da linha 2 e as VM ficam embaixo delas → W 310 L2, VB-01 a 04 e terças dos vãos 1–2 e 2–3 só depois do mezanino; (b) a placa de 10 m das paredes G e C sobe pelo topo e o balancim não passa entre a viga de cobertura e as terças → C antes da TS-01 L4 e G antes da W 310 L2.",
         "Abaixo da cobertura montada a altura livre é de +7,19 (eixo A) a +7,78 (eixo C) no fundo da TS-01; sobre o piso +7,30 sobram 0,1 a 0,8 m: manipulador telescópico ou mini-guindaste sob a cobertura NÃO servem para lajes, VM nem placas (só para terças, chaparia e peças leves).",
         f"Guindastes: principal autopropelido classe 90–100 t (I130 V407 {fd(PQ['V407'][7], 1)} t a ~10–12 m, dentro do pavilhão, trabalhando de ré da linha 9 para a 3); mezanino e parede G com o guindaste no vão 2–3, entrando pela abertura lateral E/F (livre até +7,50); placas externas com guindaste de ~40–60 t no perímetro (3,24 t a até ~14 m). Conferir as classes na tabela de carga do equipamento e o solo das patolas; plano de rigging (NBR 9062:2017 3.17 e Seção 11) da montadora.",
         "Tolerâncias de montagem (NBR 9062:2017 5.2.2.6): ±1,0 cm em planta e no nível dos apoios; prumo ±H/300 até 2,5 cm; juntas medidas após a montagem.",
         "Cotas em cm, níveis em m. Não medir no desenho. EMISSÃO EXECUTIVA — LIBERADO PARA PRODUÇÃO, ARMAÇÃO, CONCRETAGEM E MONTAGEM."]
pr.notas(Q[2] - 180, Q[3] - 6, notas, 178)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-MON03")
for a in avisos:
    print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
