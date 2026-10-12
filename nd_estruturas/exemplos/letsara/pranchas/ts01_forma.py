"""ND-LET-TS01-1 — TS-01: fôrma, insertos e transitórias (A0). Padrão de prancha de peça pré-moldada (cast unit)."""
import json
from prancha_nd import Prancha
from ts01_dados import P, L, H, DX, sec, R, TR, V, peso, ALCA_Fd, ALCA_cap, tipo_terca, f

LG = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/ligacoes.json"))
pr = Prancha("A0", dict(cliente="MARQUE ENGENHARIA", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="TS-01 — VIGA I90 DE COBERTURA PROTENDIDA — FÔRMA, INSERTOS E TRANSITÓRIAS",
                        desenho="ND-LET-TS01-1", folha="01/03", fase="PARA APROVAÇÃO"))
mac, yfi, yci, ycs, yfs = P["mac"], 150, 230, 700, 780
TER, NOS, ALC, EST = P["tercas"], P["nos"], P["alcas"], P["estoque"]
sk = lambda h: h * DX / H                  # deslocamento da ponta a prumo na altura h


def chapa_topo(v, s, plano=False):
    t = tipo_terca(s)
    ds = 150 if t == "CH-T2" else 100
    if plano:
        dy = 190 if t == "CH-T2" else 100
        v.ret(s - ds, -dy, 2 * ds, 2 * dy, "METALICA")
        for yy in (-50, 50):
            v.circulo((s + 55, yy), 9, "METALICA")
        if t == "CH-T2":
            for so, yo in ((140, 140), (-140, 140), (140, -140), (-140, -140)):
                v.ret(s + so - 5, yo - 45, 10, 90, "METALICA")
    else:
        v.ret(s - ds, H - 12.5, 2 * ds, 12.5, "METALICA")
        if t == "CH-T2":
            for so in (-140, 140):
                v.ret(so + s - 45, H, 90, 80, "METALICA")


# ------------------------------------------------------------------ PLANTA SUPERIOR 1:25
vp = pr.vista("PLANTA SUPERIOR", (80, 742), 25, titulo="PLANTA SUPERIOR — TS-01", subtitulo="face superior (topo da mesa)")
vp.ret(DX, -200, L, 400, "VISTA")
for s in TER:
    chapa_topo(vp, s + DX, plano=True)
for s in ALC:
    vp.ret(s + DX - 50, -8, 100, 16, "METALICA")
vp.cota_ord([0] + [s + DX for s in TER] + [L + DX], 200, 6, x0=0,
            rotulos=["0"] + [f"{s + DX:.0f}" for s in TER] + [f"{L + DX:.0f}"])
vp.cota_ord([s + DX for s in ALC], -200, -6, x0=0, rotulos=[f"{s + DX:.0f}" for s in ALC])
vp.chamada((TER[0] + DX, 100), (10, 30), "CH-T2 (nós de contraventamento, 7x)")
vp.chamada((TER[1] + DX, 100), (14, 26), "CH-T1 (terças, 6x)")
vp.chamada((ALC[0] + DX, 0), (8, -26), "AL-1 (4 alças de cordoalha)")
vp.cota_v([-200, 200], L + DX, 8)

# ------------------------------------------------------------------ ELEVAÇÃO 1:25
ve = pr.vista("ELEVAÇÃO", (80, 612), 25, titulo="ELEVAÇÃO — TS-01",
              subtitulo="peça fabricada reta; pontas a prumo na posição montada (caimento 3%)")
ve.poli([(0, 0), (L, 0), (L + DX, H), (DX, H)], "VISTA", fechada=True)
for y in (yfi, yci, ycs, yfs):
    ve.linha((mac + sk(y), y), (L - mac + sk(y), y), "VISTA")
for x in (mac, L - mac):
    ve.linha((x + sk(yfi), yfi), (x + sk(yci), yci), "VISTA"); ve.linha((x + sk(ycs), ycs), (x + sk(yfs), yfs), "VISTA")
for x in (P["pino_x"], L - P["pino_x"]):
    for d in (-25, 25):
        ve.linha((x + d, 0), (x + d + DX, H), "OCULTA")
    ve.ret(x - 75, 0, 150, 12.5, "METALICA")
for s in TER:
    chapa_topo(ve, s + DX)
    ve.circulo((s + sk(P["h_tb2"]), P["h_tb2"]), 13.5, "METALICA")
for s in ALC:
    ve.poli([(s + DX - 50, H), (s + DX - 50, H + 110), (s + DX, H + 150), (s + DX + 50, H + 110), (s + DX + 50, H)], "METALICA")
    for d in (-50, 50):
        ve.linha((s + DX + d, H), (s + d + sk(200), 200), "OCULTA")
cgx, cgy = L / 2 + sk(sec.yc * 1000), sec.yc * 1000
ve.circulo((cgx, cgy), 100, "INDICACAO"); ve.linha((cgx - 180, cgy), (cgx + 180, cgy), "INDICACAO")
ve.linha((cgx, cgy - 180), (cgx, cgy + 180), "INDICACAO")
ve.chamada((cgx + 70, cgy + 70), (10, 12), f"CG (s = {f(cgx/1000,3)} m; h = {cgy:.0f} mm)")
ve.chamada((TER[5] + sk(600), 600), (8, -22), "TB-2 Ø25 passante (13x, h = 600)")
ve.chamada((P["pino_x"] + DX / 2, 300), (-12, -22), "TB-1 Ø50 a prumo")
ve.chamada((L - P["pino_x"], 6), (12, -18), "CH-A1 (2x)")
ve.cota_h([0, P["pino_x"], mac, ALC[0], ALC[1], ALC[2], ALC[3], L - mac, L - P["pino_x"], L], 0, -16)
ve.cota_v([0, yfi, yfs, H], 0, -10)
ve.cota((L, H), (L + DX, H), 6, 0)
ve.marcador_corte((TER[5] + 60, -60), (TER[5] + 60 + DX, H + 60), "A", lado=1)
ve.marcador_corte((P["pino_x"] + 260, -60), (P["pino_x"] + 260 + DX, H + 60), "B", lado=1)
ve.marcador_corte((TER[4] + 60, -60), (TER[4] + 60 + DX, H + 60), "C", lado=1)
ve.marcador_detalhe((600, 450), 650, 1, ang=150, dist=10)
ve.marcador_detalhe((ALC[1] + DX, H), 400, 2, ang=60, dist=6)

# ------------------------------------------------------------------ VISTA INFERIOR 1:25
vi = pr.vista("VISTA INFERIOR", (80, 532), 25, titulo="VISTA INFERIOR — TS-01", subtitulo="fundo da fôrma")
vi.ret(0, -200, L, 400, "VISTA")
for x in (P["pino_x"], L - P["pino_x"]):
    vi.ret(x - 75, -150, 150, 300, "METALICA"); vi.circulo((x, 0), 26, "METALICA")
for x in EST:
    vi.poli([(x - 120, -260), (x + 120, -260), (x, -205)], "INDICACAO", fechada=True)
vi.chamada((L - P["pino_x"], 150), (10, 10), "CH-A1 300×150×12,5 + furo Ø52")
vi.chamada((EST[0], -260), (10, -10), "calço de estoque/transporte (2x)")
vi.cota_h([0, P["pino_x"], EST[0], EST[1], L - P["pino_x"], L], -200, -9)

# ------------------------------------------------------------------ ESQUEMAS DE IÇAMENTO E ESTOCAGEM 1:100
vq = pr.vista("ESQUEMA DE IÇAMENTO", (60, 418), 100, titulo="IÇAMENTO — DESFORMA E MONTAGEM",
              subtitulo="4 alças AL-1, 2 balancins, cabos verticais")
vq.ret(0, 0, L, H, "VISTA")
za, zb, zg = H + 1600, H + 3000, H + 4600
for a, b in ((ALC[0], ALC[1]), (ALC[2], ALC[3])):
    vq.linha((a, H + 150), (a, za), "INDICACAO"); vq.linha((b, H + 150), (b, za), "INDICACAO")
    vq.ret(a, za, b - a, 250, "METALICA")
    m = (a + b) / 2
    vq.linha((m, za + 250), (m, zb), "INDICACAO")
vq.ret(ALC[0] + 1500, zb, ALC[3] - ALC[0] - 3000, 300, "METALICA")
vq.linha(((ALC[0] + ALC[1]) / 2, zb), (L / 2, zb), "INDICACAO")
vq.linha((L / 2, zb + 300), (L / 2, zg), "INDICACAO")
vq.chamada((L / 2, zg), (8, 3), f"gancho: {f(peso,0)} kN ({f(peso/9.81,1)} t)")
vq.chamada(((ALC[0] + ALC[1]) / 2, za + 250), (-8, 6), "balancim")
vq.cota_h([0] + ALC + [L], 0, -7)
vq.texto((0, -2600), f"Reação por alça (×1,3): {f(ALCA_Fd,1)} kN ≤ {f(ALCA_cap,1)} kN (laço Ø12,7)", "nota")

ve2 = pr.vista("ESQUEMA DE ESTOCAGEM", (60, 348), 100, titulo="ESTOQUE E TRANSPORTE",
               subtitulo="2 calços sob a mesa inferior, sem empilhamento")
ve2.ret(0, 0, L, H, "VISTA")
for x in EST:
    ve2.poli([(x - 250, -400), (x + 250, -400), (x, 0)], "INDICACAO", fechada=True)
ve2.cota_h([0] + EST + [L], -400, -6)

# ------------------------------------------------------------------ CORTES 1:10
pts = [(x * 1000, y * 1000) for x, y in sec.pts]


def corte_I(nome, org, sub, s_tipo):
    v = pr.vista(nome, org, 10, titulo=nome, subtitulo=sub)
    v.poli(pts, "CORTADO", fechada=True); v.hachura(pts, "AR-CONC", 0.03)
    for x in P["x_cord"]:
        v.ponto_barra((x, P["y_cord"]), 12.7)
    t = s_tipo
    dy = 190 if t == "CH-T2" else 100
    v.ret(-dy, H - 12.5, 2 * dy, 12.5, "METALICA")
    for yy in (-50, 50):
        v.ret(yy - 12, H - 12.5 - 40, 24, 40, "METALICA")                       # luva M16 soldada
    for yy in (-dy + 30, dy - 30):
        v.poli([(yy, H - 12.5), (yy, H - 150), (yy + (20 if yy < 0 else -20), H - 170)], "METALICA")   # grapas
    v.ret(-75, P["h_tb2"] - 12.5, 150, 25, "METALICA")
    v.cota_h([-200, -75, 75, 200], 0, -16)
    v.cota_v([0, P["y_cord"], P["h_tb2"], H], 200, 12)
    v.cota_h([-dy, -50, 50, dy], H, 10)
    return v


va = corte_I("CORTE A-A", (110, 170), "seção corrente na CH-T1", "CH-T1")
va.chamada((60, H - 6), (14, 30), "CH-T1 200×200×12,5")
va.chamada((50, H - 40), (24, 18), "luva M16 soldada (2x)")
va.chamada((-80, H - 120), (-16, 10), "grapa Ø10")
va.chamada((60, P["h_tb2"]), (24, 0), "TB-2 tubo Ø25×2,0 L=150")
va.chamada((100, P["y_cord"]), (20, 10), "6 cord. Ø12,7")

vc = corte_I("CORTE C-C", (300, 170), "nó de contraventamento na CH-T2", "CH-T2")
for yo in (-140, 140):
    vc.ret(yo - 45, H, 90, 80, "METALICA")
    vc.circulo((yo, H + 35 if yo > 0 else H + 70), 8, "METALICA")
vc.chamada((140, H + 80), (14, 18), "orelha 90×80×9,5 furo Ø16 (4x)")
vc.chamada((-120, H - 6), (-16, 26), "CH-T2 300×380×12,5")
vc.cota_v([H, H + 35, H + 70], 205, 22, total=False)

vb = pr.vista("CORTE B-B", (455, 170), 10, titulo="CORTE B-B", subtitulo="maciço da ponta, junto ao TB-1")
rb = [(-200, 0), (200, 0), (200, H), (-200, H)]
vb.poli(rb, "CORTADO", fechada=True); vb.hachura(rb, "AR-CONC", 0.03)
vb.ret(-25, 0, 50, H, "VISTA")
vb.ret(-150, 0, 300, 12.5, "METALICA")
for yy in (-120, 120):
    vb.poli([(yy, 12.5), (yy, 280), (yy + (25 if yy < 0 else -25), 300)], "METALICA")
for x in P["x_cord"]:
    vb.ponto_barra((x, P["y_cord"]), 12.7)
vb.chamada((25, 650), (20, 6), "TB-1 tubo Ø50 (pino Ø25 grauteado)")
vb.chamada((140, 6), (18, -12), "CH-A1 300×150×12,5")
vb.chamada((-120, 200), (-18, 10), "grapa Ø10 (4x)")
vb.cota_h([-200, -150, -25, 25, 150, 200], 0, -16)
vb.cota_v([0, H], 200, 12)

# ------------------------------------------------------------------ DETALHE 1 — ponta (1:10)
d1 = pr.vista("DETALHE 1", (630, 160), 10, titulo="DETALHE 1 — PONTA E APOIO", subtitulo="posição montada: caimento 3%")
d1.poli([(1300, 0), (0, 0), (DX, H), (1300 + DX, H)], "VISTA")
d1.interrupcao((1300, 0), (1300 + DX, H))
for y in (yfi, yci, ycs, yfs):
    d1.linha((mac + sk(y), y), (1300 + sk(y), y), "VISTA")
d1.linha((mac + sk(yfi), yfi), (mac + sk(yci), yci), "VISTA"); d1.linha((mac + sk(ycs), ycs), (mac + sk(yfs), yfs), "VISTA")
for d in (-25, 25):
    d1.linha((P["pino_x"] + d, 0), (P["pino_x"] + d + DX, H), "OCULTA")
d1.ret(P["pino_x"] - 75, 0, 150, 12.5, "METALICA")
d1.ret(P["pino_x"] - 75, -10, 150, 10, "VISTA")                                  # neoprene
d1.linha((P["pino_x"], -300), (P["pino_x"] + sk(400), 400), "EIXO")
d1.ret(P["pino_x"] - 12.5, -300, 25, 700, "OCULTA")                              # pino PN-1 (no consolo)
d1.poli([(-150, -10), (700, -10), (700, -400)], "OCULTA")                        # consolo do pilar
d1.cota_h([0, P["pino_x"] - 75, P["pino_x"], P["pino_x"] + 75, mac], 0, -14)
d1.cota((0, H), (DX, H), 8, 0)
d1.cota_v([-10, 0, H], 1300 + DX, 10, total=False)
d1.chamada((DX / 2, H / 2), (-12, 10), "ponta a prumo na montagem")
d1.chamada((P["pino_x"], 300), (14, 26), "TB-1 Ø50 inclinado 3% na fôrma")
d1.chamada((P["pino_x"] + 60, -5), (22, -6), "neoprene 300×150×10 c/ furo Ø40")
d1.chamada((P["pino_x"], -250), (-10, -8), "pino PN-1 Ø25 (consolo)")
d1.chamada((600, -200), (8, -12), "consolo do pilar (topo a 3%)")

# ------------------------------------------------------------------ DETALHE 2 — alça AL-1 (1:10)
d2 = pr.vista("DETALHE 2", (850, 150), 10, titulo="DETALHE 2 — ALÇA AL-1", subtitulo="laço de cordoalha Ø12,7 CP-190 RB")
d2.poli([(-300, 0), (300, 0), (300, H), (-300, H)], "VISTA")
for y in (yfi, yci, ycs, yfs):
    d2.linha((-300, y), (300, y), "VISTA")
d2.poli([(-50, 200), (-50, H + 110), (0, H + 150), (50, H + 110), (50, 200)], "ARMADURA")
for d in (-50, 50):
    d2.linha((d, 200), (d - 40, 120), "ARMADURA"); d2.linha((d, 200), (d + 40, 120), "ARMADURA")
d2.cota_v([200, H, H + 150], 50, 18, total=False)
d2.cota_h([-50, 50], H + 150, 8)
d2.chamada((-50, 500), (-14, 10), "2 pernas na alma")
d2.chamada((50, 160), (12, -8), "pontas desfiadas")
d2.chamada((0, H + 150), (10, 10), "laço livre 150")

# ------------------------------------------------------------------ ISOMÉTRICO
pr.imagem(400, 312, 980, 488, "/home/claude/letsara/pranchas/ISO-TS01-geral-crop.png", "ISOMÉTRICO — TS-01",
          "modelo 3D da peça com insertos (sem escala)")

# ------------------------------------------------------------------ coluna da direita
x0, y = pr.quadro[2] - 180, pr.quadro[3] - 6
n2 = sum(tipo_terca(s) == "CH-T2" for s in TER)
ins = [["AL-1", "Alça laço cordoalha Ø12,7, 2 pernas 700", 4, "1,3", "ver planta"],
       ["CH-T1", "Chapa 200×200×12,5 + 2 luvas M16 + 2 grapas", len(TER) - n2, "4,6", "terças pares"],
       ["CH-T2", "Chapa 300×380×12,5 + 2 luvas M16 + 4 orelhas", n2, "13,2", "nós c/ 3,20 m"],
       ["TB-2", "Tubo Ø25×2,0 L=150 passante na alma", len(TER), "0,2", "h = 600"],
       ["TB-1", "Tubo Ø50×3,0 L=900 a prumo (pino Ø25)", 2, "3,2", f"s = {P['pino_x']}"],
       ["CH-A1", "Chapa 300×150×12,5 furo Ø52 + 4 grapas Ø10", 2, "5,2", "fundo"]]
y = pr.tabela(x0, y, "INSERTOS (CHAPARIA NA FOLHA 03)", ["MARCA", "DESCRIÇÃO", "QT", "kg/un", "POSIÇÃO"], ins,
              [16, 92, 10, 16, 46])
qd = [["MARCA", P["marca"], "QUANTIDADE", f"{P['qtd']}"],
      ["COMPR. FÔRMA", f"{L} mm", "VÃO HORIZ.", "19.710 mm"],
      ["VOLUME", f"{f(V,3)} m³", "PESO", f"{f(peso,1)} kN ({f(peso/9.81,2)} t)"],
      ["CONCRETO", f"C{P['fck']} / fckj {P['fckj']}", "PROTENSÃO", f"{P['n_cord']} cord. Ø12,7"],
      ["CAIMENTO", "3% (sobe p/ eixo C)", "PONTA", f"a prumo (desl. {DX} mm)"]]
y = pr.tabela(x0, y - 4, "QUADRO DA PEÇA", ["ITEM", "VALOR", "ITEM", "VALOR"], qd, [30, 60, 30, 60])
dm, es = TR["desforma_montagem"], TR["estoque_transporte"]
tr = [["Desforma / montagem", "4 alças", f"{f(dm['Mpos'],0)} / {f(dm['Mneg'],0)}",
       f"{f(max(dm['tens_sup_inf_Mpos'][0], dm['tens_sup_inf_Mneg'][0]),2)} / {f(min(dm['tens_sup_inf_Mpos'][1], dm['tens_sup_inf_Mneg'][1]),2)}", "OK"],
      ["Estoque / transporte", "2 calços", f"{f(es['Mpos'],0)} / {f(es['Mneg'],0)}",
       f"{f(max(es['tens_sup_inf_Mpos'][0], es['tens_sup_inf_Mneg'][0]),2)} / {f(min(es['tens_sup_inf_Mpos'][1], es['tens_sup_inf_Mneg'][1]),2)}", "OK"]]
y = pr.tabela(x0, y - 4, f"TRANSITÓRIAS (×1,3; limites {f(TR['limites_MPa'][0],1)} / {f(TR['limites_MPa'][1],2)} MPa)",
              ["FASE", "APOIO", "M+ / M- (kN·m)", "σ sup. / inf. (MPa)", "OK"], tr, [42, 22, 38, 60, 18])
ct = LG["contraventamento"]
lg = [["TB-1 × pino PN-1/PN-2", "28 apoios", f"{max(a['dist_mm'] for a in LG['apoios']):.1f} mm", "OK"],
      ["CH-T1/T2 × linha de terças", "14 vigas", f"{max(t['dist_mm'] for t in LG['tercas']):.1f} mm", "OK"],
      ["Berço BR-1 na I110", "5 linhas", f"desnível {f(LG['berco_I110'][0]['desnivel_mm'],1)} mm", "OK"],
      ["Tirante × terça do nó", f"{ct['n_tirantes']} tirantes", f"folga {ct['folga_min_terca_mm']} mm", "OK"],
      ["Tirante × tirante (X)", "cruzamento", f"folga {f(ct['folga_cruzamento_mm'],1)} mm", "OK"]]
y = pr.tabela(x0, y - 4, f"CHECAGEM DE LIGAÇÕES NO MODELO (tol. {LG['tol_mm']:.0f} mm)", ["LIGAÇÃO", "INSTÂNCIAS", "DESVIO", "OK"],
              lg, [62, 38, 62, 18])
mem = [["ELU flexão", f"Md {f(R.linhas['Md_kNm'],0)} ≤ MRd {f(R.linhas['MRd_kNm'],0)} kN·m"],
       ["ELS-F / ELS-D (fundo)", f"{f(R.linhas['elsf_inf_MPa'],2)} / {f(R.linhas['elsd_inf_MPa'],2)} MPa"],
       ["Flecha final", f"{f(R.linhas['flecha_final_mm'],0)} mm ≤ {f(R.linhas['flecha_lim_mm'],0)} mm"]]
y = pr.tabela(x0, y - 4, "MEMÓRIA RESUMIDA", ["VERIFICAÇÃO", "RESULTADO"], mem, [62, 118])
notas = [f"Fabricar a peça reta com {L} mm no fundo da fôrma; as cabeceiras de ponta ficam inclinadas 3% (topo deslocado {DX} mm) para que as pontas fiquem a prumo na montagem.",
         "Cotas ordenadas a partir do ponto 0 = aresta inferior da ponta esquerda (lado do pilar P1, parte baixa do caimento).",
         "TB-1 montado a prumo na posição final: na fôrma fica inclinado 3% (gabarito). Folga do pino Ø25 no tubo Ø50 grauteada após o alinhamento.",
         f"Desforma, içamento e montagem só pelas 4 alças AL-1 com 2 balancins e cabos verticais; liberar com fckj ≥ {P['fckj']} MPa.",
         "Estoque e transporte sobre 2 calços de madeira sob a mesa inferior nas posições indicadas, sem empilhamento.",
         "Chapas CH-T1/CH-T2 faceando o topo, niveladas no plano da mesa; luvas e furos tamponados na concretagem; tolerância ±5 mm.",
         "Contraventamento Ø12,5 A36 nas orelhas da CH-T2 (uma diagonal a 35 mm e a outra a 70 mm da chapa), com esticador; furos Ø16 na alma da terça intermediária.",
         "Chaparia ASTM A36, galvanizada a fogo ou com pintura de fundo após a desforma. Medidas em mm.",
         "PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(x0, y - 4, notas, 180)
pr.posicoes_desenho.clear()
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-TS01-1")
for a in avisos:
    print(a)
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
