"""ND-LET-LA01 — lajes alveolares do mezanino (planta de lajes, seção, apoio, chavetas, capa) e
ND-LET-CM01 — placas de fechamento protendidas 125 × 15 (elevação de montagem, seção, insertos e ligação com o IP-01). A1."""
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha

f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
Y_LIN = [0.0, 10.05, 19.705, 29.36, 38.865, 48.445, 58.025, 67.605, 76.81]
X_FACH = [0.0, 9.87, 20.05, 29.63, 40.10]
M = lambda v: v * 1000


def notas_padrao(pr, XC, y, extra):
    pr.notas(XC, y, extra + ["Cotas de concreto em cm, chaparia em mm, níveis em m. Não medir no desenho. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."], 182)


# ================================================================== LA-01
def lajes():
    L_P, B_P, H_P = 9850, 1250, 200                                     # painel: 985 × 125 × 20 (apoio 10 cm nas mesas das VM)
    N = 31
    pr = Prancha("A1", dict(cliente="MARQUE ENGENHARIA", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                            conteudo="LAJES ALVEOLARES LA-01 / LA-02 (h20 + capa 5) DO MEZANINO — PLANTA DE LAJES, SEÇÃO, APOIO E CHAVETAS",
                            desenho="ND-LET-LA01", folha="01/01", fase="PARA APROVAÇÃO", marca="LA-01", qtd=2 * N, peso=f(1.25 * 9.85 * 2.65, 1), volume=f(0.125 * 9.85, 2)))
    pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL")
    Q = pr.quadro
    XC = Q[2] - 190
    pr.ret(Q[0] + 4, Q[3] - 30, Q[0] + 520, Q[3] - 4, "CARIMBO")
    pr.texto(Q[0] + 10, Q[3] - 24, "LA-01", "grande", "TITULO")
    pr.texto(Q[0] + 62, Q[3] - 24, f"LAJE ALVEOLAR h20 + CAPA 5 — LA-01 (125 × {L_P/10:.0f} cm) · LA-02 (75 × {L_P/10:.0f})", "titulo", "TITULO")
    pr.texto(Q[0] + 10, Q[3] - 14, f"mezanino, níveis +3,15 e +6,55; vão 9,65 m entre as vigas VM; {2*N} LA-01 + 2 LA-02   ·   PESO LA-01 {f(1.25*9.85*2.65/10, 2)} t   ·   fabricante a confirmar (tabela de carga)", "nota", "TEXTO")
    # planta de lajes 1:100 (um nível; o outro é igual)
    v = pr.vista("PLANTA", (Q[0] + 40, Q[3] - 175), 100, titulo="PLANTA DE LAJES — NÍVEIS +3,15 E +6,55 (IGUAIS)", subtitulo="painéis de A para E; LA-02 (75 cm) junto ao eixo E; capa 5 cm com tela Q138", unidade="cm")
    for x in X_FACH:
        v.eixo((M(x), -1500), (M(x), M(10.05) + 1500), 500)
        v.circulo((M(x), M(10.05) + 2300), 500, "VISTA"); v.texto((M(x), M(10.05) + 2300), "ABCDE"[X_FACH.index(x)], "nota", "MIDDLE_CENTER")
    for k, y in ((1, 0.0), (2, 10.05)):
        v.eixo((-1500, M(y)), (M(40.1) + 1500, M(y)), 500)
        v.circulo((-2300, M(y)), 500, "VISTA"); v.texto((-2300, M(y)), str(k), "nota", "MIDDLE_CENTER")
    for y in (0.0, 10.05):
        v.ret(300, M(y) - 200, M(40.1) - 600, 400, "VISTA")
    for k in range(N):
        x0 = 300 + k * B_P
        v.ret(x0, 100, B_P - 10, L_P, "VISTA")
        if k % 4 == 0:
            v.texto((x0 + B_P / 2, M(5.0)), f"LA-01 ({k + 1})", "min", "MIDDLE_CENTER", rot=90)
    x0 = 300 + N * B_P
    v.ret(x0, 100, 740, L_P, "CORTADO"); v.texto((x0 + 370, M(5.0)), "LA-02 (75)", "min", "MIDDLE_CENTER", rot=90)
    for x, bx, by in ((0, 600, 400), (9870, 400, 600), (20050, 400, 600), (29630, 400, 600), (40100, 600, 400)):
        for y in (0.0, 10.05):
            v.ret(x - bx / 2, M(y) - by / 2, bx, by, "CORTADO")
    v.cota_h([M(x) for x in X_FACH], -2000, -8)
    v.cota_h([300, 300 + B_P, 300 + 2 * B_P], M(10.05) + 300, 8, total=False)
    v.cota_v([0, 100, 100 + L_P, M(10.05)], M(40.1) + 1500, 8, total=False)
    v.chamada((M(5.0), 100), (10, -14), "apoio 10 cm sobre a mesa da VM (faixa de neoprene 10 × 3 mm)")
    v.marcador_detalhe((300 + 3 * B_P, 100), 600, 1, ang=-45, dist=8)
    # seção do painel 1:10 (mm? concreto → cm)
    s = pr.vista("SEÇÃO DO PAINEL", (Q[0] + 60, Q[3] - 300), 10, titulo="SEÇÃO DO PAINEL LA-01", subtitulo="alveolar h20 (5 alvéolos) + capa 5; geometria do fabricante a confirmar", unidade="cm")
    s.ret(0, 0, B_P, H_P, "CORTADO")
    for k in range(5):
        cx = 125 + k * 250
        s.circulo((cx, 100), 70, "VISTA")
    for k in range(7):
        s.ponto_barra((125 + k * 166.7, 35), 12.7)
    s.hachura([(0, 200), (B_P, 200), (B_P, 250), (0, 250)], "AR-CONC", 0.02); s.linha((0, 250), (B_P, 250), "VISTA")
    s.linha((20, 230), (B_P - 20, 230), "ARMADURA")
    s.poli([(0, 200), (-30, 150), (-30, 60), (0, 40)], "VISTA"); s.poli([(B_P, 200), (B_P + 30, 150), (B_P + 30, 60), (B_P, 40)], "VISTA")
    s.cota_h([0, B_P], 0, -8); s.cota_v([0, 35, 200, 250], B_P + 30, 10, total=False)
    s.chamada((125 + 3 * 166.7, 35), (14, -12), "7 cord. Ø12,7 (genérico — confirmar com o fabricante)")
    s.chamada((B_P / 2, 230), (14, 14), "capa 5 cm C25 com tela Q138")
    s.chamada((B_P + 30, 105), (12, 6), "chaveta lateral grauteada (graute fluido ≥ 30 MPa)")
    # detalhe apoio 1:10
    d = pr.vista("DETALHE 1", (Q[0] + 330, Q[3] - 300), 10, titulo="DETALHE 1 — APOIO NA VIGA VM", subtitulo="laje sobre a mesa superior da I70; capa monolítica", unidade="cm")
    d.poli([(-200, -120), (200, -120), (200, 0), (-200, 0)], "CORTADO"); d.hachura([(-200, -120), (200, -120), (200, 0), (-200, 0)], "AR-CONC", 0.03)
    d.poli([(-75, -120), (-75, -500), (75, -500), (75, -120)], "VISTA")
    for sg in (-1, 1):
        d.ret(min(sg * 100, sg * 200), 0, 100, 200, "CORTADO")
        d.ret(min(sg * 100, sg * 200), -3, 100, 3, "METALICA")
    d.hachura([(-200, 200), (200, 200), (200, 250), (-200, 250)], "AR-CONC", 0.02); d.linha((-200, 250), (200, 250), "VISTA")
    d.hachura([(-100, 0), (100, 0), (100, 200), (-100, 200)], "AR-CONC", 0.02)
    d.poli([(-250, 230), (250, 230)], "ARMADURA"); d.poli([(-400, 20), (400, 20)], "ARMADURA")
    d.cota_h([-200, -100, 100, 200], -120, -10, total=False); d.cota_v([-120, 0, 200, 250], 200, 10, total=False)
    d.chamada((150, -2), (12, -14), "neoprene 10 × 3 mm (faixa)"); d.chamada((0, 100), (18, 22), "preenchimento entre painéis (graute) + N1 2 Ø10 passantes")
    d.chamada((250, 230), (10, 12), "tela Q138 na capa; armadura negativa 2 Ø10 c/ painel sobre o apoio"); d.chamada((-75, -300), (-12, -10), "VM I70 (ND-LET-VM01)")
    # tabelas
    y = Q[3] - 6
    y = pr.tabela(XC, y, "MARCAS — LAJES ALVEOLARES", ["MARCA", "DESCRIÇÃO", "QT", "PESO (t)", "NÍVEIS"],
                  [["LA-01", f"125 × {L_P/10:.0f} × 20, 7 Ø12,7 (genérico)", 2 * N, f(1.25 * 9.85 * 2.65 / 10, 2), "+3,15 e +6,55"],
                   ["LA-02", f"75 × {L_P/10:.0f} × 20 (recorte de fábrica)", 2, f(0.75 * 9.85 * 2.65 / 10, 2), "+3,15 e +6,55 (junto ao eixo E)"]], [18, 80, 14, 20, 56])
    qd = [["VÃO", "965 cm (entre mesas)", "APOIO", "10 cm + neoprene"], ["SOBRECARGA", "500 kgf/m² + revest. 100", "CAPA", "5 cm C25, tela Q138"],
          ["h TOTAL", "25 cm", "ESCORAMENTO", "nenhum"], ["PAINÉIS", f"{2*N} LA-01 + 2 LA-02", "CONTRAFLECHA", "fabricante (≤ L/300)"]]
    y = pr.tabela(XC, y - 4, "QUADRO DAS LAJES", ["ITEM", "VALOR", "ITEM", "VALOR"], qd, [30, 62, 30, 60])
    mem = [["ELU seção genérica 7 Ø12,7", "209 > 192 kN·m — NÃO PASSA"], ["Descompressão (ELS-D)", "só até 9,05 m"], ["Alternativas", "tabela do fabricante com 9 Ø12,7 ou h26,5 + 5"]]
    y = pr.tabela(XC, y - 4, "MEMÓRIA RESUMIDA (ND-LET-MC02)", ["VERIFICAÇÃO", "RESULTADO"], mem, [70, 112])
    notas_padrao(pr, XC, y - 4, ["! A laje alveolar h20 + 5 em 9,65 m com 500 kgf/m² não passou na seção genérica: o fabricante deve apresentar a tabela de carga do painel (ou adotar h26,5 + 5). Não fabricar antes.",
                                 "Painéis apoiados 10 cm sobre a mesa superior das VM, com faixa de neoprene; chavetas grauteadas e capa de 5 cm (C25, tela Q138) concretadas após a montagem de todo o nível.",
                                 "Armadura negativa sobre os apoios: 2 Ø10 por painel, L = 200 cm, dentro da capa; preenchimento dos alvéolos nas pontas (20 cm) para evitar graute nos vazios.",
                                 "Içamento por garras ou balancim do fabricante; estocar sobre 2 calços a 30 cm das pontas, máximo 6 painéis por pilha."])
    avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-LA01")
    print("LA01", len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos", [a for a in avisos if a[0] == "ERRO" or "sobrep" in a[1]])


# ================================================================== CM-01
def placas():
    H_PL, E_PL = 1250, 150
    vaos = [(Y_LIN[i + 1] - Y_LIN[i]) for i in range(8)]
    marcas = {}
    for i, vao in enumerate(vaos):
        Lp = round(vao * 1000 - 10)
        marcas.setdefault(Lp, []).append(f"L{i+1}–L{i+2}")
    vaos_f = [(X_FACH[i + 1] - X_FACH[i]) + (0.4 if i in (0, 3) else 0.0) for i in range(4)]
    for i, vao in enumerate(vaos_f):
        Lp = round(vao * 1000 - 10)
        marcas.setdefault(Lp, []).append(f"{'ABCDE'[i]}–{'ABCDE'[i+1]} (fach.)")
    lista = sorted(marcas.items(), key=lambda t: -t[0])
    MK = {Lp: f"CM-0{k+1}" for k, (Lp, _) in enumerate(lista)}
    L0 = lista[0][0]
    peso = lambda Lp: 1.25 * 0.15 * Lp / 1000 * 25
    pr = Prancha("A1", dict(cliente="MARQUE ENGENHARIA", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                            conteudo="PLACAS DE FECHAMENTO PROTENDIDAS CM-01 A CM-08 (125 × 15) — ELEVAÇÃO DE MONTAGEM, SEÇÃO, INSERTOS E LIGAÇÃO COM OS PILARES",
                            desenho="ND-LET-CM01", folha="01/01", fase="PARA APROVAÇÃO", marca="CM-01", qtd=16, peso=f(peso(L0), 1), volume=f(1.25 * 0.15 * L0 / 1000, 2)))
    pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL")
    Q = pr.quadro
    XC = Q[2] - 190
    pr.ret(Q[0] + 4, Q[3] - 30, Q[0] + 520, Q[3] - 4, "CARIMBO")
    pr.texto(Q[0] + 10, Q[3] - 24, "CM-01", "grande", "TITULO")
    pr.texto(Q[0] + 62, Q[3] - 24, f"PLACA DE FECHAMENTO PROTENDIDA 125 × 15 — CM-01 (L = {L0/10:.0f} cm) · CM-02 A CM-08", "titulo", "TITULO")
    pr.texto(Q[0] + 10, Q[3] - 14, f"8 fiadas de 125 cm (±0,00 a +10,00) por fora dos pilares; 4 cord. Ø9,5 CP-190; fixação nos IP-01 dos pilares   ·   PESO CM-01 {f(peso(L0)/10, 2)} t   ·   192 placas", "nota", "TEXTO")
    # elevação de montagem da fachada eixo A (1:200)
    v = pr.vista("ELEVAÇÃO", (Q[0] + 40, Q[3] - 150), 200, titulo="ELEVAÇÃO DE MONTAGEM — FACHADA EIXO A (EIXO E SIMÉTRICO)", subtitulo="8 fiadas; marcas por vão; juntas de 10 mm", unidade="cm")
    for i, y in enumerate(Y_LIN):
        v.ret(M(y) - 200, -1000, 400, 11000, "CORTADO")
        v.texto((M(y), 10300), str(i + 1), "nota", "BOTTOM_CENTER")
    for i, vao in enumerate(vaos):
        Lp = round(vao * 1000 - 10)
        for k in range(8):
            v.ret(M(Y_LIN[i]) + 5, k * H_PL, Lp, H_PL - 10, "VISTA")
        v.texto((M(Y_LIN[i]) + vao * 500, 4 * H_PL + 300), MK[Lp], "min", "BOTTOM_CENTER")
    v.linha((-1500, 0), (M(76.81) + 1500, 0), "TERRENO")
    v.cota_h([M(y) for y in Y_LIN], -1000, -8)
    v.cota_v([0, H_PL, 2 * H_PL, 8 * H_PL], M(76.81) + 500, 8, total=False)
    v.chamada((M(Y_LIN[2]), 7 * H_PL + 600), (8, 14), "IP-01 no pilar a cada fiada (a 10 cm abaixo do topo da placa)")
    v.marcador_detalhe((M(Y_LIN[1]), 3 * H_PL), 900, 1, ang=30, dist=8)
    # seção da placa 1:10 (cm) e insertos
    s = pr.vista("SEÇÃO", (Q[0] + 60, Q[3] - 345), 10, titulo="SEÇÃO DA PLACA", subtitulo="protendida; 2 + 2 cord. Ø9,5", unidade="cm")
    s.ret(0, 0, E_PL, H_PL, "CORTADO"); s.hachura([(0, 0), (E_PL, 0), (E_PL, H_PL), (0, H_PL)], "AR-CONC", 0.03)
    for x in (40, 110):
        for yy in (200, 1050):
            s.ponto_barra((x, yy), 9.5)
    s.poli([(30, 30), (120, 30), (120, 1220), (30, 1220)], "ARMADURA", fechada=True)
    s.poli([(0, H_PL), (20, H_PL - 20), (E_PL - 20, H_PL - 20), (E_PL, H_PL)], "VISTA"); s.poli([(0, 0), (20, 20), (E_PL - 20, 20), (E_PL, 0)], "VISTA")
    s.cota_h([0, 40, 110, E_PL], 0, -8, total=True); s.cota_v([0, 200, 1050, H_PL], E_PL, 10, total=False)
    s.chamada((110, 1050), (12, -6), "C1 — 4 cord. Ø9,5 CP-190 RB (2 + 2), 56 kN cada")
    s.chamada((120, 600), (12, 0), "tela Q92 nas duas faces + estribo de borda Ø6,3 c/20")
    s.chamada((75, H_PL), (12, 8), "encaixe macho-fêmea 2 cm (junta de 10 mm c/ selante)")
    # detalhe ligação com o pilar 1:10 (planta)
    d = pr.vista("DETALHE 1", (Q[0] + 300, Q[3] - 290), 10, titulo="DETALHE 1 — LIGAÇÃO PLACA × PILAR (PLANTA)", subtitulo="cantoneira soldada em obra ao IP-01 do pilar e ao CH-P1 da placa", unidade="cm")
    d.ret(-300, -600, 600, 400, "CORTADO"); d.hachura([(-300, -600), (300, -600), (300, -200), (-300, -200)], "AR-CONC", 0.03)
    d.chapa(-75, -200, 150, 9.5)                                                           # IP-01 na face externa (x−)... aqui face externa para cima
    for sg in (-1, 1):
        d.ret(sg * 305 if sg > 0 else -305 - 1200, -140, 1200, 150, "CORTADO")
        d.chapa(sg * 305 if sg > 0 else -305 - 100, -140 - 9.5, 100, 9.5)
    d.chapa(-75, -190.5, 150, 9.5)
    d.chapa(-60, -190.5, 63, 6.3); d.chapa(-60, -190.5, 6.3, 63)
    d.chapa(60 - 6.3, -190.5, 6.3, 63); d.chapa(-3, -190.5, 63, 6.3)
    d.cota_h([-300, 300], -600, -8); d.cota_h([-305 - 100, -305, 305, 405], -140, 10, total=False); d.cota_v([-200, -140, 10], -305 - 1200, -8, total=False)
    d.chamada((0, -195), (14, -14), "IP-01 chapa 150×150×9,5 + 2 pinos Ø12,5 (pilar)")
    d.chamada((60, -160), (16, 24), "L 63×63×6,3 L=120, soldada ao IP-01 e ao CH-P1 (solda 5 mm, 100 mm)")
    d.chamada((355, -149), (12, -10), "CH-P1 100×150×9,5 + 2 pinos Ø12,5 (na placa, 2 por ponta)")
    d.chamada((-305, 0), (-10, 8), "placa CM 125 × 15"); d.chamada((305, 5), (10, 30), "junta 10 mm (selante PU)")
    # tabelas
    y = Q[3] - 6
    linhas = [[MK[Lp], ", ".join(pos), 8 * len(pos) * (2 if "fach" not in pos[0] else 2), f"{Lp/10:.0f}", f(peso(Lp) / 10, 2)] for Lp, pos in lista]
    y = pr.tabela(XC, y, "MARCAS — PLACAS DE FECHAMENTO 125 × 15 (8 fiadas)", ["MARCA", "VÃOS", "QT", "L (cm)", "PESO (t)"], linhas, [18, 70, 12, 22, 24], h_lin=6.0)
    ins = [["CH-P1", "Chapa 100×150×9,5 + 2 pinos Ø12,5 c/ cabeça", 4, "face interna, 2 por ponta (a 15 e 110 cm)"], ["CT-P", "Cantoneira L 63×63×6,3 L=120 (solda em obra)", 4, "IP-01 × CH-P1"],
           ["AL-P", "Alça laço cordoalha Ø9,5", 2, "topo, a L/5 das pontas"]]
    y = pr.tabela(XC, y - 4, "INSERTOS POR PLACA — dimensões em mm", ["MARCA", "DESCRIÇÃO", "QT", "POSIÇÃO"], ins, [16, 100, 10, 56])
    mem = [["Vento (q 0,87 kN/m², Cpe 1,0)", "M = 12,7 kN·m por placa"], ["σ no bordo (P/A ± M/W)", "1,18 ± 2,7 → tração 1,5 ≤ fctk,inf 2,9 MPa"],
           ["Flecha (I bruto, 9,65 m)", "≈ 19 mm ≤ L/250 = 39 mm"], ["Fixação (4 cantoneiras)", "R = 2,6 kN por ponto — M12 / solda 5 mm"]]
    y = pr.tabela(XC, y - 4, "MEMÓRIA RESUMIDA (NBR 6118 / NBR 6123)", ["VERIFICAÇÃO", "RESULTADO"], mem, [70, 112])
    notas_padrao(pr, XC, y - 4, ["Placas protendidas 125 × 15 (C40, fckj 25 MPa) com 4 cordoalhas Ø9,5 (2 + 2) — vento nos dois sentidos; encaixe macho-fêmea de 2 cm entre fiadas; junta 10 mm selada.",
                                 "Fixação: em cada ponta da placa, 2 cantoneiras L 63×6,3 soldadas em obra ao IP-01 do pilar e ao CH-P1 da placa (acerta tolerâncias de ±10 mm); primeira fiada apoiada na viga baldrame (projeto de fundações).",
                                 "Montagem após a cobertura: de baixo para cima, por vão; conferir prumo da face externa a cada fiada.",
                                 "Se o fabricante preferir placa armada (sem protensão), a espessura passa a 15 cm com 2 telas Q196 e 4 Ø10 longitudinais — reapresentar para verificação."])
    avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-CM01")
    print("CM01", len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos", [a for a in avisos if a[0] == "ERRO" or "sobrep" in a[1]])


if __name__ == "__main__":
    lajes()
    placas()
