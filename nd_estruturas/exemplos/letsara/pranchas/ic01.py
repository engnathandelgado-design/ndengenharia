"""ND-LET-IC01 — IÇAMENTO E MANUSEIO DAS PEÇAS (rev11, pedido do Nathan 26/10/2026), por tipo de peça, com dados lidos das mesmas
fontes das folhas de cada peça (arm/*.json e *_geom.json dos pilares, placas_icamento_4p.json, laje_alveolar.json, i110_r01.json,
ligacoes.json, vm_retangular.json): nº de pontos, posição, peso, carga por ponto e acessório. NBR 9062:2017 5.3.2/5.3.3
(βa 1,3 no saque/manuseio/montagem; alças dimensionadas com βa 3,0; γf 1,3).
PILARES em duas etapas: FÁBRICA — alças de cordoalha AL-2 (desforma, estocagem, carga); OBRA — furo FI-1 (verticalização e montagem)."""
import glob, json, math, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from prancha_nd import Prancha
import renomear as RN

AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
PR = "/home/claude/letsara/pranchas/"
f1 = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
NOMES = json.load(open(PR + "nomes.json", encoding="utf-8"))
nomes = lambda mk: [q["nome"] for q in NOMES["pecas"] if q.get("marca") == mk]
pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="IÇAMENTO E MANUSEIO DAS PEÇAS — PILARES (FÁBRICA E OBRA), VIGAS, PLACAS, LAJES ALVEOLARES E PEÇAS METÁLICAS",
                        desenho="ND-LET-IC01", folha="01/01", fase="PARA APROVAÇÃO"))
pr.revisao("00", "26/10/2026", "EMISSÃO INICIAL: IÇAMENTO POR TIPO DE PEÇA (PEDIDO DO NATHAN)")
Q = pr.quadro
pr.texto(Q[0] + 8, Q[3] - 16, "IÇAMENTO E MANUSEIO DAS PEÇAS", "grande", "TITULO")
pr.texto(Q[0] + 8, Q[3] - 26, "Pontos, cargas e acessórios por tipo de peça. Dados das folhas de cada peça (mesmo registro). NBR 9062:2017 5.3.2 e 5.3.3.", "nota", "TEXTO")

# ------------------------------------------------------------------ esquemas (1 por tipo)
def esquema_pilar(x, y):
    v = pr.vista("ESQ-PIL", (x, y), 100, titulo="PILAR — FÁBRICA E OBRA", subtitulo="1) desforma/estoque/carga pelas 2 AL-2  2) obra: FI-1 e pé no chão", unidade="cm")
    L = 11000
    v.ret(0, 0, L, 600, "VISTA")                                       # deitado (fábrica)
    for z in (3300, 7800):
        v.linha((z, 600), (z, 2600), "CHAMADA"); v.circulo((z, 640), 40, "ARMADURA")
    v.linha((3300, 2600), (5550, 3600), "CHAMADA"); v.linha((7800, 2600), (5550, 3600), "CHAMADA")
    v.texto((5550, 3700), "balancim / 2 cabos", "nota", "BOTTOM_CENTER")
    v.texto((5500, -300), "FÁBRICA: deitado, face C para cima — 2 alças AL-2", "nota", "TOP_CENTER")
    x2 = 13500                                                         # obra: verticalização
    v.ret(x2, 0, 600, L, "VISTA")
    v.circulo((x2 + 300, L - 1800), 60, "METALICA")
    v.linha((x2 + 300, L - 1800), (x2 + 300, L + 1500), "CHAMADA")
    v.texto((x2 + 900, L - 1800), "FI-1: pino passante + 2 manilhas", "nota", "MIDDLE_LEFT")
    v.texto((x2 + 300, -300), "OBRA: verticalizar e colocar no cálice", "nota", "TOP_CENTER")


def esquema_viga(x, y):
    v = pr.vista("ESQ-VIG", (x, y), 100, titulo="VIGAS — 2 OU 4 ALÇAS", subtitulo="cabos verticais com balancim; posição das alças na tabela", unidade="cm")
    L = 16500
    v.ret(0, 0, L, 1200, "VISTA")
    for a in (2500, L - 2500):
        v.linha((a, 1200), (a, 3000), "CHAMADA"); v.circulo((a, 1240), 50, "ARMADURA")
    v.linha((0, 3000), (L, 3000), "METALICA")
    v.linha((L / 2, 3000), (L / 2, 4200), "CHAMADA")
    v.texto((L / 2, 4300), "balancim", "nota", "BOTTOM_CENTER")


def esquema_placa(x, y):
    v = pr.vista("ESQ-PLA", (x, y), 100, titulo="PLACAS — 4 PONTOS IZ-1 NUMA FACE", subtitulo="desforma deitada → giro → montagem de pé; balancim duplo", unidade="cm")
    L, h = 10000, 1250
    v.ret(0, 0, L, h, "VISTA")
    xs = [0.104 * L, 0.396 * L, L - 0.396 * L, L - 0.104 * L]
    for a in xs:
        v.circulo((a, h / 2), 50, "METALICA"); v.linha((a, h / 2), (a, h + 1800), "CHAMADA")
    v.linha((xs[0], h + 1800), (xs[1], h + 1800), "METALICA"); v.linha((xs[2], h + 1800), (xs[3], h + 1800), "METALICA")
    v.linha(((xs[0] + xs[1]) / 2, h + 1800), (L / 2, h + 3000), "CHAMADA"); v.linha(((xs[2] + xs[3]) / 2, h + 1800), (L / 2, h + 3000), "CHAMADA")
    v.cota_h([0] + xs + [L], 0, -13, total=False)


def esquema_laje(x, y):
    v = pr.vista("ESQ-LAJ", (x, y), 100, titulo="LAJE ALVEOLAR — GARRA NAS PONTAS", subtitulo="garras a 0,30 m das pontas; sem alça embutida", unidade="cm")
    L = 9550
    v.ret(0, 0, L, 200, "VISTA")
    for a in (300, L - 300):
        v.ret(a - 120, -60, 240, 320, "METALICA"); v.linha((a, 260), (a, 2200), "CHAMADA")
    v.linha((300, 2200), (L - 300, 2200), "METALICA")
    v.cota_h([0, L], -60, -13)
    v.texto((300, 2300), "garra a 0,30 m", "nota", "BOTTOM_LEFT")


esquema_pilar(Q[0] + 60, Q[3] - 230)
esquema_viga(Q[0] + 60, Q[3] - 330)
esquema_placa(Q[0] + 60, Q[3] - 460)
esquema_laje(Q[0] + 60, Q[3] - 580)

# ------------------------------------------------------------------ tabelas (mesmo registro das folhas)
BA, GF = 1.3, 1.3
lin_p = []
for fj in sorted(glob.glob(PR + "arm/*.json")):
    J = json.load(open(fj, encoding="utf-8"))
    mk = J["marca"]
    try:
        G = json.load(open(PR + f"{mk}_geom.json", encoding="utf-8"))
    except Exception:
        G = {}
    peso = J["V"] * 25.0
    al = sorted(J.get("al") or [])
    fi = (G.get("fi") or {}).get("z")
    nm = ", ".join(nomes(mk)) or mk
    Pk = peso / 2
    sig = GF * BA * peso / (60 * min(J["B"], J["H"])) * 1000 / 1000      # MPa: furo Ø60 × largura da peça
    lin_p.append([mk, nm[:40], f1(peso / 10.0, 2), "2 AL-2: " + " e ".join(f"{z / 10:.0f}" for z in al) + " cm da base" if al else "—", f1(Pk),
                  (f"FI-1 a {(J['L_TOT'] - fi) / 10:.0f} cm do topo" if fi else "FI-1"), f"{f1(sig)} MPa"])
pr.tabela(Q[0] + 420, Q[3] - 40, "PILARES — FÁBRICA (AL-2) E OBRA (FI-1)", ["MARCA", "PEÇAS", "PESO (t)", "FÁBRICA: ALÇAS AL-2", "Pk/alça (kN)", "OBRA: FURO", "σ no furo (d)"],
          lin_p, [20, 70, 18, 60, 22, 48, 24], h_lin=5.6)
I1 = json.load(open(AQ + "i110_r01.json", encoding="utf-8"))
LG = json.load(open(AQ + "ligacoes.json", encoding="utf-8"))
lin_v = []
for k, v_ in I1.items():
    ic = v_.get("icamento") if isinstance(v_, dict) else None
    if ic:
        nv = RN.novo(k) if hasattr(RN, "novo") else k
        lin_v.append([nv, "I130", f1(ic["peso_kN"] / 10.0, 2), f"2 AL-3 a {f1(ic['a_alca_m'], 2)} m das pontas", f1(ic["peso_kN"] / 2), f"{ic['n_lacos']} laços Ø12,7; Fd(βa 3) {f1(ic['F_alca_beta3_kN'])} kN"])
al_ts = LG["alcas"]
lin_v.append(["V408 … V419", "TS-01", "12,0", "4 AL-1 a " + ", ".join(f1(a, 2) for a in al_ts) + " m (2 balancins)", f1(120 / 4), "laço Ø12,7, 2 pernas"])
lin_v.append(["VM-01 … VM-04", "VM 30×75", "—", "2 AL-1 a 1,10 m das pontas", "—", "laço Ø12,7, 2 pernas"])
lin_v.append(["VB", "VB 15×60", "—", "2 AL-1 a 1,50 m das pontas", "—", "laço Ø12,7, 2 pernas"])
y = pr.tabela(Q[0] + 420, Q[3] - 330, "VIGAS — ALÇAS DE CORDOALHA (não engraxada, NBR 9062 5.3.3)", ["MARCA", "TIPO", "PESO (t)", "PONTOS", "Pk/ponto (kN)", "ALÇA"],
              lin_v, [34, 22, 18, 76, 22, 90], h_lin=5.6)
PL = json.load(open(AQ + "placas_icamento_4p.json", encoding="utf-8"))
LA = json.load(open(AQ + "laje_alveolar.json", encoding="utf-8"))["icamento"]
lin_o = [["PLACAS PP", f1(PL["peso_t"], 2), PL["pontos"], f"{f1(PL['Pk_kN'])} (Pd {f1(PL['Pd_kN'])} ≤ {f1(PL['P_disp_kN'])})", "IZ-1 (inserto de içamento) + balancim duplo"],
         ["LAJE ALVEOLAR LA-01", f1(LA["peso_t"], 2), f"2 garras a {f1(LA['ponto_m'], 2)} m das pontas", f"Fd {f1(LA['F_por_garra_d_kN'])} por garra", "garra mecânica; fcj ≥ " + f1(LA["fcj_icamento"], 0) + " MPa"],
         ["ESCADAS METÁLICAS", "ver ES01/ES02", "2 cintas nas longarinas, a 1/4 do comprimento", "—", "cintas de poliéster; sem içar pelos guarda-corpos"],
         ["W 200 × 15,0 (linha 2)", "≈ 0,18 por módulo de 12 m", "2 cintas a 1/4 do comprimento", "—", "cintas; montar e parafusar antes de soltar"]]
y2 = pr.tabela(Q[0] + 420, y - 8, "PLACAS, LAJES E PEÇAS METÁLICAS", ["PEÇA", "PESO (t)", "PONTOS", "CARGA POR PONTO (kN)", "ACESSÓRIO"], lin_o, [44, 24, 120, 50, 104], h_lin=5.6)
pr.notas(Q[0] + 420, y2 - 8, [
    "Pilares: AL-2 (alças de cordoalha Ø12,7 CP-190 RB não engraxada) só na FÁBRICA — tirar da fôrma, estocar e carregar no caminhão. FI-1 (furo de içamento, tubo Ø60,3 perdido) só na OBRA — verticalizar e colocar no cálice, com pino de aço passante e 2 manilhas, o pé apoiado no chão sobre madeira. Pontos fora da platibanda.",
    "Cargas: Pk = peso/nº de pontos (cabos verticais). Alças dimensionadas com βa 3,0 e γf 1,3 (NBR 9062:2017 5.3.2); saque, manuseio e montagem com βa 1,3. σ no furo = γf·βa·peso/(Ø60 × menor lado), muito abaixo de fcd.",
    "Placas: desforma deitada pelos 4 IZ-1 da face interna com balancim duplo (cargas iguais), giro e montagem de pé pelos mesmos 4 pontos (ND-LET-PP00 e MON03, det. 2). Lajes: garra mecânica, sem alça embutida. Içar só com fcj indicado na folha da peça.",
    "Estoque: calços alinhados na vertical, nas posições das alças (pilares e vigas) ou a 0,30 m das pontas (lajes); nunca sobre consolos ou insertos."], 400)
av = pr.salvar(PR + "ND-LET-IC01")
print("ND-LET-IC01", len([a for a in av if a[0] == "ERRO"]), "erros,", len(av), "avisos")
for a in av:
    print("  ", a)
