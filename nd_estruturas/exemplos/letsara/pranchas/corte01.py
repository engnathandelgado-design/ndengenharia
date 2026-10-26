"""ND-LET-CT01 — cortes transversais da estrutura (eixos 2 e 3) e detalhes dos apoios da cobertura (A0)."""
from portico import *                                                   # rev11: geometria do pórtico em módulo comum (MON01 usa a mesma)
from prancha_nd import Prancha, _seg_rect
def nivel(v, x, z, txt, lado=1):
    v.linha((x, z), (x + lado * 900, z), "INDICACAO")
    v.poli([(x + lado * 450 - 150, z + 260), (x + lado * 450 + 150, z + 260), (x + lado * 450, z)], "INDICACAO", True)
    v.texto((x + lado * 650, z + 80), txt, "nota", alinh="BOTTOM_LEFT" if lado > 0 else "BOTTOM_RIGHT")


pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="CORTES TRANSVERSAIS DA ESTRUTURA — EIXOS 2 E 3",
                        desenho="ND-LET-CT01", folha="01/01", fase="PARA APROVAÇÃO", rev="07"))
pr.revisao("01", "12/10/2026", "geometria do R01 (79,35 × 39,50 m); cabeça dos pilares laterais recuada; placas 15 cm por fora")
pr.revisao("02", "12/10/2026", "CONSOLOS SEM CHANFRO (FUNDO ALINHADO À VIGA); VM I90 COM DENTE 45×30; LAJE 8 Ø12,7")
pr.revisao("03", "14/10/2026", "TS-01 SEM DENTES (APOIO NO RECUO E NO TOPO DA I120); PACOTE COM PAINÉIS; COBERTURA REBAIXADA; PLACAS 10 cm")
pr.revisao("04", "16/10/2026", "NBR 9062: SEM VT; MEZANINO EM MEIO VASO COM DENTE")
pr.revisao("05", "17/10/2026", "TERÇAS Z 302 CONTÍNUAS POR TRANSPASSE, SEM MÃO-FRANCESA")
pr.revisao("07", "21/10/2026", "COTAS EM CM; MARCAS DOS PILARES NOS CORTES; DETALHES DE APOIO PASSAM PARA A ND-LET-CT04")
pr.revisao("10", "24/10/2026", "DEC-052/054: EIXO 2 COM W 200 × 15,0 E MONTANTES; I120 COM h 120")
pr.revisao("09", "23/10/2026", "DEC-045/047/048/049: PISOS +3,90/+7,30; VM 30 × 75; LINHA 2 COM COBERTURA METÁLICA (SEM TS-01); P6 DA LINHA 2")
z_tel = lambda x: zf(x) + (H + 10 + 300 + sum(PAC.values()) * 1000) * c       # topo dos painéis solares
for k, (eixo, org, nome) in enumerate(((2, (100, 560), "CORTE 2-2"), (3, (100, 170), "CORTE 3-3"))):
    v = pr.vista(nome, org, 60, titulo=f"{nome} — EIXO {eixo} (y = {[9.65, 19.725][k]:.3f} m)".replace(".", ","),
                 subtitulo="olhando para o eixo 9; níveis em metros" + ("; mezanino entre os eixos 1 e 2" if eixo == 2 else ""), unidade="cm")
    R = Recorte(v)
    v.linha((-1500, 0), (41000, 0), "TERRENO")
    estrutura(R, eixo)
    for x, nomex in ((0, "A"), (9870, "B"), (19750, "C"), (29630, "D"), (39500, "E")):
        v.linha((x, -1800), (x, 11600), "EIXO")
        v.circulo((x, -2250), 400, "BOLHA"); v.texto((x, -2250), nomex, "sub", alinh="MIDDLE_CENTER")
    v.cota_h([0, 9870, 19750, 29630, 39500], 0, -40, total=False)
    from prancha_nd import DIM_K, DIM_DLI
    _yt = -40 * DIM_K * v.esc - DIM_DLI * v.esc
    _d = pr.msp.add_linear_dim(base=v.P((0, _yt)), p1=v.P((0, 0)), p2=v.P((39500, 0)), angle=0, location=v.P((14800, _yt)), dimstyle="ND",
                               override={"dimlfac": v.esc * v.fator, "dimdec": 1, "dimzin": 8, "dimtmove": 2}, dxfattribs={"layer": "COTA"})
    _d.render(); v._add(_d.dimension)                                                 # total com o texto fora do eixo C
    MKS = {2: [(0, "PL-02"), (9870, "PM-01"), (19750, "PC-01"), (29630, "PM-02"), (36300, "PE-03"), (39500, "PL-06")], 3: [(0, "PL-09"), (39500, "PL-11")]}[eixo]
    import pe_pilar as PP                                                           # rev11: pé dos pilares no cálice + L total
    y_l = [9.65, 19.725][k]
    for x_, mk_ in MKS:
        nm_ = PP.pe(v, x_ / 1000, y_l, x_, "x", cotar=(x_ == 0), lado=-1)
        if x_ == 39500:
            _r1, _r2 = (PP.rotulo(nm_).split(" — ", 1) + [""])[:2]                  # pilar do eixo E: rótulo em 2 linhas (cabe entre P5 e P4)
            v.texto((x_ - 350, 250 + 300), _r1, "nota", "BOTTOM_RIGHT")
            v.texto((x_ - 350, 250), _r2, "nota", "BOTTOM_RIGHT")
        else:
            v.texto((x_ + 350 if x_ != 36300 else x_ - 300, 250 if x_ != 36300 else 950), PP.rotulo(nm_), "nota", "BOTTOM_LEFT" if x_ != 36300 else "BOTTOM_RIGHT")
    nivel(v, 40100, -1000, "fundo dos pilares −1,000; fundo do cálice −1,050 (graute 5 cm)")
    v.cota_v([0, REC[0] if eixo == 3 else ZL2["A"], Z_TOP_PIL], -2600, -8, total=False)
    v.cota_v([0, REC[1] if eixo == 3 else ZL2["E"], Z_TOP_PIL], 42300, 8, total=False)
    nivel(v, -300, 0, "±0,000", -1)
    nivel(v, -450, REC[0] if eixo == 3 else ZL2["A"], f"assento TS {f(REC[0] / 1000)}" if eixo == 3 else f"apoio da W {f(ZL2['A'] / 1000)}", -1)
    nivel(v, 300, Z_TOP_PIL, f"platibanda {f(Z_TOP_PIL / 1000)}", -1)
    nivel(v, 39950, REC[1] if eixo == 3 else ZL2["E"], f"assento TS {f(REC[1] / 1000)}" if eixo == 3 else f"apoio da W {f(ZL2['E'] / 1000)}")
    nivel(v, 39800, Z_TOP_PIL, f"platibanda {f(Z_TOP_PIL / 1000)} (painéis {f(z_tel(39475) / 1000)})")
    v.linha((XC + 200, Z_TOP_C), (XC + 1100, Z_TOP_C), "INDICACAO")                  # nível do topo da I120: texto abaixo da TS-01
    v.poli([(XC + 650 - 150, Z_TOP_C + 260), (XC + 650 + 150, Z_TOP_C + 260), (XC + 650, Z_TOP_C)], "INDICACAO", True)
    v.texto((XC + 300, Z_TOP_C - 120), f"topo I120 / pilar central {f(Z_TOP_C / 1000)}", "nota", alinh="TOP_LEFT")
    if eixo == 3:
        nivel(v, 19950, Z_TOP_C - H_I120, f"fundo I120 {f((Z_TOP_C - H_I120) / 1000)}")
    else:
        for zm in Z_MEZ:
            nivel(v, 4500, zm, f"piso mezanino {f(zm / 1000)}")
    v.chamada((20300, z_tel(20300)), (2, 14), "cobertura Isoeste: TP-40 + lã de rocha 40 + zipada #0,50 + painéis (COB01)")
    if eixo == 3:
        v.chamada((10000, zf(10000) + 450), (8, -16), "TS-01 — viga I90 protendida, caimento 3 %, sem dentes (apoio direto)")
    else:
        v.chamada((12000, zf(12000) + 1150), (8, 12), f"{CB2['perfil'].replace(' x ', ' × ')} nos pilares e em montantes no meio dos vãos (ND-LET-COB05)")
    v.chamada((39875, 5000), (6, 0), "placa 10 cm (por fora)")
    v.chamada((39350, 9950), (8, 20), f"cabeça 40×30; folga de {Z_TOP_PIL - z_tel(39475):.0f} mm do topo dos painéis à platibanda")
    if eixo == 3:
        v.chamada((XC, Z_TOP_C - 650), (10, -30), f"I120: TS-01 apoiadas no topo (NEO-3 + 2 PN-5 por viga)")
    else:
        v.chamada((XC + 200, 800), (10, 8), "P8A 40×60 (40 em x): cabeça até a W 200")
        v.chamada((12000, Z_MEZ[1] - 600), (8, 17), "VM 30 × 75 + laje h20 + capa 5")
        v.chamada((P6_L2[0] * 1000, 2000), (-10, 8), "P6 da linha 2 (25 × 40)")

# coluna direita: tabela de níveis e notas
x0, y = pr.quadro[2] - 180, pr.quadro[3] - 6
niv = [["Assento da TS-01 no P1 (recuo)", f(REC[0] / 1000)], ["Assento da TS-01 no P2 (recuo)", f(REC[1] / 1000)],
       ["Topo da I120 / pilares centrais", f(Z_TOP_C / 1000)], ["Fundo da I120", f((Z_TOP_C - H_I120) / 1000)], ["Assento da I120 (CP-I120)", f(Z_ASS_I120 / 1000)],
       ["Topo dos painéis junto ao P1 / ao P2", f"{f(z_tel(X0[0]) / 1000)} / {f(z_tel(39475) / 1000)}"], ["Platibanda (todas)", f(Z_TOP_PIL / 1000)],
       ["Pisos do mezanino", f"{f(Z_MEZ[0] / 1000)} / {f(Z_MEZ[1] / 1000)}"]]
y = pr.tabela(x0, y, "NÍVEIS (m)", ["ELEMENTO", "NÍVEL"], niv, [110, 70])
notas = ["Cortes gerados do mesmo modelo usado na checagem das ligações.",
         f"Cobertura rebaixada (rev03) para o pacote Isoeste (TP-40 + lã de rocha 40 + zipada 455 #0,50) + painéis solares: topo dos painéis junto ao P2 em {f(z_tel(39475) / 1000)}, {(Z_TOP_PIL - z_tel(39475)):.0f} mm abaixo da platibanda +10,000 (pedido: ≥ 150 mm).",
         f"TS-01 com {LG['L_TS']:.3f} m entre pontas (a prumo), sem dentes: apoio de 27,5 cm no recuo dos pilares laterais (NEO-4 + 2 PN-3 Ø25) e de 16,25 cm no topo da I120 / pilar central (NEO-3 + 2 PN-5 Ø20); terças c/{LG['passo_tercas']:.3f} m.".replace(".", ","),
         "Cabeça dos pilares laterais recuada acima do assento da TS-01: só os 30 cm externos sobem até +10,00 (consolos externos pela cabeça).",
         "Vigas centrais I120 (h 120, DEC-054) com dentes 78 × 35 nos consolos CP-I120 com mísula; vigas do mezanino VM retangulares 30 × 75 protendidas com dente Gerber nos consolos CP-MEZ (fundo alinhado; rev09, ND-LET-VM01). Eixo 2: sem TS-01 — W 200 × 15,0 metálica contínua apoiada na cabeça dos pilares (que sobe até o fundo da W) e em montantes W 150 no meio dos vãos sobre as VM do +7,30 (DEC-052).",
         f"Pé-direito (rev03): fundo da TS-01 de +7,19 (eixo A) a +7,78 (eixo C); na laje superior (+7,30, laje de cobertura do bloco, acesso apenas para manutenção), fundo das terças entre as linhas 1 e 2 de {f((REC[0] + 900 + 10) / 1000)} (eixo A) a {f((Z_TOP_C + 10) / 1000)} (eixo C) Portões da linha 4 livres até +7,40.",
         "Detalhes de cada apoio na montagem: ND-LET-CT04. Corte do mezanino: ND-LET-CT02. Corte longitudinal: ND-LET-CT03.",
         "Cotas em cm, níveis em m. Fundações e cálices em projeto próprio. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(x0, y - 4, notas, 180)
pr.posicoes_desenho.clear()
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-CT01")
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
for a in avisos:
    print(a)

