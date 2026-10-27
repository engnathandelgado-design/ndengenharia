"""ND-LET-PV01 — placa PV-1 sobre o portão P10–P12 da linha 4 (DEC-059, opção A do Nathan): fôrma, armação, apoios e montagem
no padrão das folhas de peça (fôrma em cima, ferragem embaixo). Dados de calc_portao_l4.py (portao_l4.json). Cotas de concreto em cm,
chaparia em mm. A1."""
import json, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from prancha_nd import Prancha
import renomear as RN

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
PJ = json.load(open(AQ + "portao_l4.json"))
PV = PJ["placa_PV1"]
f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
L = round(PV["L_m"] * 1000)
H = round(PV["h_m"] * 1000)
T = 100
C = 25                                                     # cobrimento (CAA II interna, placa de fábrica)
pg4, pg3 = RN.lista(RN.nomes_de("PG-04")), RN.lista(RN.nomes_de("PG-03"))

pr = Prancha("A1", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="PLACA PV-1 SOBRE O PORTÃO DA LINHA 4 (ENTRE PG-04 E PG-03) — FÔRMA, ARMAÇÃO, APOIOS E MONTAGEM",
                        desenho="ND-LET-PV01", folha="01/01", fase="PARA APROVAÇÃO", rev="00"))
pr.revisao("00", "24/10/2026", "EMISSÃO (DEC-059): PORTÃO 500 × 750 LIVRE ATÉ +7,50; PLACA ENTRE +7,50 E A TS-01A")
pr.revisao("R12", "27/10/2026", "PG-04 COM A FACE NO PLANO DO PG-03: CL-V L 102 NOS DOIS; NEOPRENE 75 × 150; CT-V SOBRE O TOPO DA PLACA")
Q = pr.quadro
XC = Q[2] - 190
pr.cabecalho_peca("\x01PV-1", f"PLACA SOBRE O PORTÃO — 10 × {f(H / 10)} × {f(L / 10)} cm · 1 PEÇA · {f(PV['peso_kN'] / 10.0, 2)} t",
                  "\x01" + f"linha 4, entre os pilares {pg4} e {pg3} (portão do lado do eixo D), face do pavilhão, +{f(PV['z0'], 3)} a +{f(PV['z1'], 3)} · C40 armada · 2 apoios CL-V",
                  largura=XC - Q[0] - 10)

# ------------------------------------------------------------------ FÔRMA (1:20)
E = 20
x0 = Q[0] + 40
v = pr.vista("FÔRMA", (x0, Q[3] - 110), E, titulo="FÔRMA — ELEVAÇÃO (FACE DO PAVILHÃO)", subtitulo="cotas em cm; apoios CL-V nas duas pontas", unidade="cm")
v.ret(0, 0, L, H, "VISTA")
for xa in (75, L - 75):
    v.ret(xa - 75, -102, 150, 102, "METALICA")                 # CL-V sob a ponta (aba horizontal em vista)
for xa in (800, L - 800):                                       # alças AL-1 no topo a ~0,2 L
    v.circulo((round(0.2 * L) if xa < L / 2 else L - round(0.2 * L), H), 25, "VISTA")
v.cota_h([0, 75, round(0.2 * L), L - round(0.2 * L), L - 75, L], H, 10)
v.cota_v([0, H], L, 8)
v.chamada((round(0.2 * L), H), (-6, 22), "AL-1 alça de cordoalha Ø12,7 (1 laço) a 0,2 L")
v.chamada((75, -50), (-8, -10), "CL-V (apoio, ver det. 1)")
v.chamada((L * 0.62, H * 0.4), (4, -14), "face lisa de fôrma para o pavilhão; chanfro 1 × 1 cm nas arestas")
c = pr.vista("CORTE A-A", (x0 + L / E + 70, Q[3] - 125), 5, titulo="CORTE A-A", subtitulo="seção 10 × " + f(H / 10) + " (cm)", unidade="cm")
c.ret(0, 0, T, H, "CORTADO"); c.hachura([(0, 0), (T, 0), (T, H), (0, H)], "AR-CONC", 0.02)
for y_ in (C + 5 + 5, H - C - 5 - 5):
    for x_ in (C + 5 + 5, T - C - 5 - 5):
        c.circulo((x_, y_), 5, "ARMADURA")
c.ret(C, C, T - 2 * C, H - 2 * C, "ARM_TRANSV")
c.cota_h([0, T], 0, -8); c.cota_v([0, C, H - C, H], T, 8)
c.chamada((C + 10, C + 10), (-14, -16), "N1 2 Ø10 (embaixo)")
c.chamada((C + 10, H - C - 10), (-10, 8), "N2 2 Ø10 (em cima)")
c.chamada((C, H * 0.55), (-16, 4), "N3 Ø5 c/20")

# ------------------------------------------------------------------ ARMAÇÃO (1:20)
a = pr.vista("ARMAÇÃO", (x0, Q[3] - 230), E, titulo="ARMAÇÃO — ELEVAÇÃO", subtitulo="cobrimento 2,5 cm", unidade="cm")
a.ret(0, 0, L, H, "VISTA")
n3 = (L - 2 * 50) // 200 + 1
for k in range(n3):
    x_ = 50 + k * (L - 100) / (n3 - 1)
    a.linha((x_, C), (x_, H - C), "ARM_TRANSV")
a.barra([(C, C + 10), (L - C, C + 10)], "N1", 2, 10.0, comp_cm=round((L - 2 * C) / 10), desloc=(6, -8))
a.barra([(C, H - C - 10), (L - C, H - C - 10)], "N2", 2, 10.0, comp_cm=round((L - 2 * C) / 10), desloc=(6, 8))
a.barra([(50, C), (50, H - C)], "N3", n3, 5.0, espac=20, comp_cm=round((2 * (T - 2 * C + H - 2 * C) + 80) / 10), desloc=(8, 4))
bar = [dict(pos="N1", diam=10.0, qtd=2, comp=round((L - 2 * C) / 10), trechos=[f"{round((L - 2 * C) / 10)}"]),
       dict(pos="N2", diam=10.0, qtd=2, comp=round((L - 2 * C) / 10), trechos=[f"{round((L - 2 * C) / 10)}"]),
       dict(pos="N3", diam=5.0, qtd=n3, comp=round((2 * (T - 2 * C + H - 2 * C) + 80) / 10),
            forma=[(0, 0), ((T - 2 * C) / 10, 0), ((T - 2 * C) / 10, (H - 2 * C) / 10), (0, (H - 2 * C) / 10), (0, 0), (1, 1)],
            trechos=[f"{(T - 2 * C) / 10:g}", f"{(H - 2 * C) / 10:g}", "", ""])]

# ------------------------------------------------------------------ DETALHES 1:5 — apoio CL-V e trava CT-V
d1 = pr.vista("DETALHE 1", (Q[0] + 330, Q[1] + 90), 5, titulo="DETALHE 1 — APOIO CL-V NO PG (CORTE)", subtitulo="cantoneira de apoio + neoprene 5; trava CT-V no topo (mm)", unidade="mm")
d1.ret(0, -250, 250, 250 + H + 150, "CORTADO"); d1.hachura([(0, -250), (250, -250), (250, H + 150), (0, H + 150)], "AR-CONC", 0.02)   # PG (face B à esquerda)
# rev12 (DEC-092): PG-03 e PG-04 com a face no mesmo plano → CL-V L 102 × 102 nos dois; placa 25 mm à frente da face do PG
_GP = 25
d1.chapa(-9.5, -102, 9.5, 102); d1.chapa(-102, -9.5, 102, 9.5)                    # CL-V L 102 × 102
d1.ret(-_GP - 100, 5, 100, H, "CORTADO"); d1.hachura([(-_GP - 100, 5), (-_GP, 5), (-_GP, 5 + H), (-_GP - 100, 5 + H)], "AR-CONC", 0.02)  # placa (10 cm)
d1.ret(-102, 0, 102 - _GP, 5, "VISTA")                                             # neoprene na aba (102 − 25)
d1.chapa(-6.3, 5 + H - 70, 6.3, 76.3); d1.chapa(-76, 5 + H, 76, 6.3)                # CT-V: aba na face do PG (na folga de 25) + aba sobre o topo da placa
d1.linha((-60, 5 + H - 60), (-60, 5 + H + 30), "METALICA")                         # M12 vertical na bucha BR-2 do topo
for z_ in (-30, -75):
    d1.linha((0, z_), (150, z_), "METALICA")
d1.linha((0, 5 + H - 40), (150, 5 + H - 40), "METALICA")
d1.cota_v([-102, 0, 5, 5 + H], 300, 10, total=False)
d1.cota_h([-_GP - 100, -102, -_GP, 0], -250, -8, total=False)
d1.chamada((75, -50), (46, -14), "2 BR-M16 8.8 L=200 embutidas 150 + grampo (IL-2)")
d1.chamada((-60, -5), (-12, -14), "CL-V L 102 × 102 × 9,5 L=150 (PG-03 e PG-04)")
d1.chamada((-60, 2), (-16, 8), "neoprene 75 × 150 × 5")
d1.chamada((-40, 5 + H + 3), (-40, 24), "CT-V L 76 × 76 × 6,3 L=80 + 1 M12 vertical em bucha BR-2")

# ------------------------------------------------------------------ tabelas e notas
y = Q[3] - 6
ta = pr.tabela_croqui(XC, y, bar, h_lin=9.0)
y = ta["y_base"]
V = T * H * L / 1e9
qd = [["MARCA", "PV-1", "SEÇÃO", f"10 × {f(H / 10)} cm"], ["COMPRIMENTO", f"{f(L / 10)} cm", "CONCRETO", "C40 / desforma fcj 15 MPa"],
      ["VOLUME", f"{f(V, 3)} m³", "PESO", f"{f(PV['peso_kN'] / 10.0, 2)} t"], ["AÇO CA-50/60", f"{f(ta['total_kg'], 1)} kg", "COBRIMENTO", "2,5 cm"]]
y = pr.tabela(XC, y - 4, "QUADRO DA PEÇA", ["ITEM", "VALOR", "ITEM", "VALOR"], qd, [30, 58, 30, 58])
ins = [["CL-V", "L 102 × 102 × 9,5 L=150, galvanizadas (PG-03 e PG-04, faces no mesmo plano)", 2, "face B dos PG, topo +7,50"],
       ["IL-2", "barras roscadas M16 8.8 L=200 (150 embutidas + grampo U Ø10) — na fábrica dos PG", 6, "2 por CL-V + 1 por CT-V"],
       ["CT-V", "L 76 × 76 × 6,3 L=80 + 1 M12 em bucha BR-2 da placa", 2, "topo, nas 2 pontas"],
       ["BR-2", "bucha rosqueada M12 hef 60 (no topo da placa, 75 da ponta, 35 da face B)", 2, "topo da placa"],
       ["AL-1", "alça de cordoalha Ø12,7 (1 laço)", 2, "topo, a 0,2 L"]]
y = pr.tabela(XC, y - 4, "INSERTOS E PEÇAS DE LIGAÇÃO", ["MARCA", "DESCRIÇÃO", "QT", "POSIÇÃO"], ins, [14, 104, 10, 48])
notas = [f"Cargas consideradas: peso próprio da placa ({f(PV['peso_kN'], 2)} kN); a placa não recebe a TS-01A nem outra placa (folga de 5 cm até o fundo da viga, fechada com mastique e rufo).",
         f"Portão 500 × 750 livre até +7,50 (DEC-059): os PG-01 a PG-04 apoiam a TS-01A depois da montagem (neoprene + graute, folhas ND-LET-PG01 a PG04) e a viga não desce no vão. A placa vai de +{f(PV['z0'], 3)} a +{f(PV['z1'], 3)}.",
         "Apoio: cada ponta sobre a CL-V com neoprene 75 × 150 × 5; trava do topo CT-V (1 M12 vertical na bucha do topo, furo oblongo horizontal ±10 mm) — a placa dilata livre. Tudo parafusado, sem solda.",
         "Içamento e montagem de pé pelas 2 alças AL-1 (balancim); concretar deitada, desformar com fcj ≥ 15 MPa (NBR 9062:2017 8.2.2.2), estocar de pé ou deitada sobre 2 calços a 0,2 L.",
         "Montar depois da TS-01A grauteada nos PG e antes do fechamento do portão; ajustar a altura com calços de aço sob o neoprene (nada abaixo de +7,50).",
         "Cotas de concreto em cm, chaparia em mm. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."]
pr.notas(XC, y - 4, notas, 176)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-PV01")
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
for a_ in avisos:
    print(a_)
