"""ND-LET-LA01 — lajes alveolares do mezanino (planta de lajes, seção, apoio, chavetas, capa) e
ND-LET-CM01 — placas de fechamento protendidas 125 × 15 (elevação de montagem, seção, insertos e ligação com o IP-01). A1."""
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha

f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from geometria import Y_LIN, X_FACH, X_EIXO
Y2 = Y_LIN[1]
LARG = X_EIXO["E"]
M = lambda v: v * 1000


def notas_padrao(pr, XC, y, extra):
    pr.notas(XC, y, extra + ["Cotas de concreto em cm, chaparia em mm, níveis em m. Não medir no desenho. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."], 182)


# ================================================================== LA-01
def paineis_mez():
    """Painéis de um nível do mezanino: [(x0 mm, largura mm, marca)], quantidades nos 2 níveis, L_P (mm)."""
    L_P, B_P = round((Y2 - 0.20) * 1000), 1250                          # apoio 10 cm na mesa de cada VM (eixo ± 10 cm)
    N, B2, x_ini = 30, 700, 300                                          # 30 LA-01 + 2 LA-02 de 70 cm (pontas A e E)
    pn = [(x_ini, B2, "LA-02")] + [(x_ini + B2 + k * B_P, B_P, "LA-01") for k in range(N)] + [(x_ini + B2 + N * B_P, B2, "LA-02")]
    PIL = [M(x) for x in X_FACH[1:4]]                                    # P3/P4/P5 (L1) e P8/P8A/P8B (L2): 40 em x → recorte nas pontas
    rec = lambda x0, b: any(x0 < xp + 225 and x0 + b > xp - 225 for xp in PIL)
    pn = [(x0, b, (mk + "R") if rec(x0, b) else mk) for x0, b, mk in pn]
    qt = {}
    for _, b, mk in pn:
        qt[mk] = qt.get(mk, 0) + 2
    return pn, qt, L_P


def lajes():
    paineis, qt, L_P = paineis_mez()
    B_P, B2, H_P, N = 1250, 700, 200, 30
    PESO1 = 1.25 * L_P / 1000 * 2.65
    pr = Prancha("A1", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                            conteudo="LAJES ALVEOLARES DO MEZANINO (h20 + CAPA 5) — PLANTA DE LAJES, SEÇÃO, APOIO E CHAVETAS",
                            desenho="ND-LET-LA01", folha="01/01", fase="PARA APROVAÇÃO", marca="LA-01", qtd=qt.get("LA-01", 0), peso=f(PESO1, 1), volume=f(0.125 * L_P / 1000, 2), rev="01"))
    pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL")
    pr.revisao("01", "12/10/2026", "GEOMETRIA DO R01 (VÃO 9,65 m); 8 Ø12,7; LA-02 70 cm NAS PONTAS; RECORTES NOS PILARES")
    pr.revisao("04", "16/10/2026", "NBR 9062: APOIO NA ABA DA VM EM MEIO VASO; 2º ESTÁGIO E CAPA C30 DE OBRA")
    Q = pr.quadro
    XC = Q[2] - 190
    pr.ret(Q[0] + 4, Q[3] - 30, Q[0] + 560, Q[3] - 4, "CARIMBO")
    pr.texto(Q[0] + 10, Q[3] - 24, "LA-01", "grande", "TITULO")
    pr.texto(Q[0] + 62, Q[3] - 24, f"LAJE ALVEOLAR h20 + CAPA 5 — LA-01 (125 × {L_P/10:.0f} cm) · LA-01R · LA-02 (70 × {L_P/10:.0f} cm)", "titulo", "TITULO")
    pr.texto(Q[0] + 10, Q[3] - 14, f"mezanino, níveis +3,15 e +6,55; vão 9,65 m entre as vigas VM (linhas 1 e 2); {sum(qt.values())} painéis (2 níveis)   ·   PESO LA-01 {f(PESO1/10, 2)} t   ·   8 cord. Ø12,7 (seção genérica — confirmar com o fabricante)", "nota", "TEXTO")
    v = pr.vista("PLANTA", (Q[0] + 40, Q[3] - 165), 100, titulo="PLANTA DE LAJES — NÍVEIS +3,15 E +6,55 (IGUAIS)", subtitulo="painéis de A para E; LA-02 (70 cm) nas pontas; R = recorte nas pontas junto aos pilares; capa 5 cm com tela Q138", unidade="cm")
    for x in X_FACH:
        v.eixo((M(x), -1500), (M(x), M(Y2) + 1500), 500)
        v.circulo((M(x), M(Y2) + 2300), 500, "VISTA"); v.texto((M(x), M(Y2) + 2300), "ABCDE"[X_FACH.index(x)], "nota", "MIDDLE_CENTER")
    for k, y in ((1, 0.0), (2, Y2)):
        v.eixo((-1500, M(y)), (M(LARG) + 1500, M(y)), 500)
        v.circulo((-2300, M(y)), 500, "VISTA"); v.texto((-2300, M(y)), str(k), "nota", "MIDDLE_CENTER")
    for y in (0.0, Y2):
        v.ret(300, M(y) - 200, M(LARG) - 600, 400, "VISTA")
    for i, (x0, b, mk) in enumerate(paineis):
        v.ret(x0, 100, b - 10, L_P, "VISTA" if mk == "LA-01" else "CORTADO")
        if mk != "LA-01" or i % 4 == 1:
            v.texto((x0 + b / 2, M(Y2 / 2)), mk, "min", "MIDDLE_CENTER", rot=90)
    for x, bx, by in [(0, 600, 400)] + [(M(xx), 400, 600) for xx in X_FACH[1:4]] + [(M(LARG), 600, 400)]:
        for y in (0.0, Y2):
            v.ret(x - bx / 2, M(y) - by / 2, bx, by, "CORTADO")
    v.cota_h([M(x) for x in X_FACH], -2000, -8)
    v.cota_h([300, 300 + B2, 300 + B2 + B_P], M(Y2) + 300, 8, total=False)
    v.cota_v([0, 100, 100 + L_P, M(Y2)], M(LARG) + 1500, 8, total=False)
    v.chamada((M(6.5), 100), (10, -14), "apoio 10 cm sobre a aba da VM (neoprene em fita 10 mm)")
    v.chamada((M(X_FACH[1]) + 200, 300), (8, 18), "recorte 45 × 20 cm na ponta (pilar 40 × 60)")
    v.marcador_detalhe((300 + B2 + 3 * B_P, 100), 600, 1, ang=-45, dist=8)
    # seção do painel 1:10 (mm? concreto → cm)
    s = pr.vista("SEÇÃO DO PAINEL", (Q[0] + 60, Q[3] - 300), 10, titulo="SEÇÃO DO PAINEL LA-01", subtitulo="alveolar h20 (5 alvéolos) + capa 5; geometria do fabricante a confirmar", unidade="cm")
    s.ret(0, 0, B_P, H_P, "CORTADO")
    for k in range(5):
        cx = 125 + k * 250
        s.circulo((cx, 100), 70, "VISTA")
    for k in range(8):
        s.ponto_barra((100 + k * 150, 35), 12.7)
    s.hachura([(0, 200), (B_P, 200), (B_P, 250), (0, 250)], "AR-CONC", 0.02); s.linha((0, 250), (B_P, 250), "VISTA")
    s.linha((20, 230), (B_P - 20, 230), "ARMADURA")
    s.poli([(0, 200), (-30, 150), (-30, 60), (0, 40)], "VISTA"); s.poli([(B_P, 200), (B_P + 30, 150), (B_P + 30, 60), (B_P, 40)], "VISTA")
    s.cota_h([0, B_P], 0, -8); s.cota_v([0, 35, 200, 250], B_P + 30, 10, total=False)
    s.chamada((550, 35), (14, -12), "8 cord. Ø12,7 (genérico — confirmar com o fabricante)")
    s.chamada((B_P / 2, 230), (14, 14), "capa 5 cm C30 com tela Q138")
    s.chamada((B_P + 30, 105), (12, 6), "chaveta lateral grauteada (graute fluido ≥ 30 MPa)")
    # detalhe apoio 1:10 — rev04: VM em MEIO VASO (laje de um lado só; alma do lado da borda, aba 15 × 20 para dentro)
    d = pr.vista("DETALHE 1", (Q[0] + 355, Q[3] - 300), 10, titulo="DETALHE 1 — APOIO NA VIGA VM (MEIO VASO)",
                 subtitulo="laje sobre a aba da VM; 2º estágio sobre a alma, concretado com a capa", unidade="cm")
    ext = [(0, -500), (250, -500), (250, -200), (400, -200), (400, 0), (0, 0)]
    d.poli(ext, "CORTADO", fechada=True); d.hachura(ext, "AR-CONC", 0.03); d.interrupcao((-20, -500), (270, -500))
    e2 = [(0, 0), (300, 0), (300, 210), (0, 210)]
    d.poli(e2, "OCULTA", fechada=True); d.hachura(e2, "ANSI31", 0.6)
    d.ret(300, 10, 700, 200, "CORTADO"); d.ret(300, 0, 100, 10, "METALICA")
    d.circulo((450, 110), 76, "VISTA"); d.circulo((660, 110), 76, "VISTA"); d.interrupcao((1000, 0), (1000, 270))
    d.hachura([(0, 210), (1000, 210), (1000, 260), (0, 260)], "ANSI31", 0.6); d.linha((0, 260), (1000, 260), "VISTA")
    d.poli([(40, -480), (40, 200)], "ARM_TRANSV"); d.poli([(210, -480), (210, 200)], "ARM_TRANSV")
    d.poli([(20, 235), (980, 235)], "ARMADURA"); d.poli([(150, 120), (900, 120)], "ARMADURA")
    d.cota_h([0, 250, 300, 400], -500, -10, total=False); d.cota_v([-200, 0, 10, 210, 260], 1000, 10, total=False)
    d.chamada((350, 5), (14, -16), "apoio 10 cm na aba + neoprene em fita 10")
    d.chamada((150, 120), (-26, 20), "2º estágio C30 (obra) + negativa nos alvéolos")
    d.chamada((600, 235), (10, 14), "capa 5 cm C30 + tela Q138")
    d.chamada((210, -300), (14, -8), "alças N9 Ø10 c/15 da VM")
    d.chamada((125, -450), (-20, -10), "VM meio vaso (ND-LET-VM01)")
    # tabelas
    y = Q[3] - 6
    y = pr.tabela(XC, y, "MARCAS — LAJES ALVEOLARES (2 NÍVEIS)", ["MARCA", "DESCRIÇÃO", "QT", "PESO (t)", "OBS."],
                  [[mk, f"{(B_P if mk.startswith('LA-01') else B2)/10:.0f} × {L_P/10:.0f} × 20, 8 Ø12,7", qt[mk], f((B_P if mk.startswith('LA-01') else B2) / 1000 * L_P / 1000 * 2.65 / 10, 2),
                    "recorte 45 × 20 nas 2 pontas" if mk.endswith("R") else ("corte longitudinal de fábrica" if mk.startswith("LA-02") else "-")] for mk in sorted(qt)], [18, 70, 12, 20, 62])
    qd = [["VÃO", f"{L_P/10 - 10:.0f} cm (entre centros de apoio)", "APOIO", "10 cm + neoprene"], ["SOBRECARGA", "500 kgf/m² + revest. 100", "CAPA", "5 cm C30, tela Q138"],
          ["h TOTAL", "25 cm", "ESCORAMENTO", "nenhum"], ["PAINÉIS", f"{sum(qt.values())} (2 níveis)", "CONTRAFLECHA", "fabricante (≤ L/300)"]]
    y = pr.tabela(XC, y - 4, "QUADRO DAS LAJES", ["ITEM", "VALOR", "ITEM", "VALOR"], qd, [30, 62, 30, 60])
    notas_padrao(pr, XC, y - 4, ["Laje alveolar h20 + 5 no vão do R01 (9,35 m de cálculo) com 500 kgf/m²: na seção genérica 7 Ø12,7 não passa (ELU no limite e descompressão); com 8 Ø12,7 passa (MRd 215 ≥ Md 192 kN·m por painel; ELS-D comprimido −0,9 MPa). O fabricante confirma pela tabela de carga do painel dele antes de fabricar.",
                                 "Painéis apoiados 10 cm sobre a aba das VM em meio vaso (rev04), com neoprene em fita de 10 mm; chavetas grauteadas; 2º estágio sobre a alma da VM e capa de 5 cm (C30, tela Q138) concretados juntos, por quem executa a capa, após a montagem de todo o nível. Lajes e vigas sem escoramento; montar as lajes só depois das cantoneiras CT-1 das VM.",
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
    pr = Prancha("A1", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
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
    # placas() — substituída por fechamento.py (CM01 rev 02 + PP00 + pranchas por vista)
