"""ND-LET-ES03 — guarda-corpos e corrimãos das duas escadas metálicas (rev09d, DEC-060) pela RT CBMRS nº 11 Parte 01/2016, com as
ligações parafusadas verificadas em escadas_detalhe.py. Elevações desenvolvidas de cada trecho (GI-1 a GI-11 da escada interna, GE-1 a
GE-7 da externa) projetadas das peças do modelo 3D, detalhes típicos das fixações e tabelas de trechos, ligações e pé-direito. A1."""
import math
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from prancha_nd import Prancha
import escadas_vista as E

EJ = E.EJ
f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")

pr = Prancha("A1", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="ESCADAS METÁLICAS — GUARDA-CORPOS, CORRIMÃOS (RT CBMRS 11) E LIGAÇÕES PARAFUSADAS",
                        desenho="ND-LET-ES03", folha="01/01", fase="PARA APROVAÇÃO", rev="00"))
pr.revisao("00", "24/10/2026", "EMISSÃO INICIAL (DEC-060): GUARDA-CORPOS E CORRIMÃOS DAS ESCADAS INTERNA E EXTERNA E TABELA DE LIGAÇÕES")
pr.revisao("09", "25/10/2026", "DEC-062: CORRIMÃO DUPLO 0,92 / 0,70 (RT CBMRS 11 + NBR 9050); DETALHES NAS ND-LET-ES04 / ES05")
Q = pr.quadro
XC = Q[2] - 190
pr.cabecalho_peca("GC", "GUARDA-CORPOS E CORRIMÃOS — ESCADA INTERNA (GI-1 A GI-11) E EXTERNA (GE-1 A GE-7)",
                  "RT CBMRS nº 11 Parte 01/2016 · corrimão duplo 0,92 / 0,70 nos dois lados · guarda 0,92 nos lances, 1,05 nos patamares e na laje, 1,30 na escada externa · tudo parafusado, galvanizado",
                  largura=XC - Q[0] - 10)


def pecas_de(cod):
    return [pc for pc in E.P if E.cod(pc) == cod]


def eixo_guarda(cod):
    """origem e direção horizontal do trecho: pelo corrimão principal (ou pelos montantes)."""
    cr = [pc for pc in pecas_de(cod) if pc["g"] == "linear" and "corrimão" in pc["marca"] and "prolong" not in pc["marca"]]
    if cr:
        pc = max(cr, key=lambda p: math.dist(p["p0"][:2], p["p1"][:2]))
        a, b = pc["p0"], pc["p1"]
    else:
        ms = [E.bbox(pc) for pc in pecas_de(cod)]
        cs = [((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2) for lo, hi in ms]
        a, b = min(cs), max(cs)
        a, b = (a[0], a[1], 0), (b[0], b[1], 0)
    d = (b[0] - a[0], b[1] - a[1]); n = math.hypot(*d) or 1.0
    return (a[0], a[1]), (d[0] / n, d[1] / n)


# ------------------------------------------------------------------ elevações desenvolvidas 1:50 (empacotadas em linhas)
G = EJ["guardas"]
linhas = [["GI-1", "GI-2", "GI-3", "GI-4", "GE-1", "GE-2"], ["GI-5", "GI-6", "GI-7", "GI-8", "GI-9", "GI-10", "GI-11"], ["GE-3", "GE-4", "GE-5", "GE-6", "GE-7"]]
ESC = 50
y_top = Q[3] - 62
for row in linhas:
    info = []
    for cod in row:
        g = next(x for x in G if x["cod"] == cod)
        o, d = eixo_guarda(cod)
        S = (lambda o, d: (lambda x, y, z: (((x - o[0]) * d[0] + (y - o[1]) * d[1]) * 1000, z * 1000)))(o, d)
        ps = pecas_de(cod)
        uv = [S(*p) for pc in ps for p in E.vertices(pc)]
        su = (min(p[0] for p in uv), max(p[0] for p in uv)); zw = (min(p[1] for p in uv), max(p[1] for p in uv))
        info.append((cod, g, o, d, S, su, zw))
    hmax = max((zw[1] - zw[0] + 250) / ESC for *_, zw in info)
    x = Q[0] + 14
    for cod, g, o, d, S, su, zw in info:
        w = max((su[1] - su[0]) / ESC, 56)
        org = (x - su[0] / ESC + (w - (su[1] - su[0]) / ESC) / 2, y_top - hmax - zw[0] / ESC + 250 / ESC)
        br = g["gc"]["barra"]
        sub = f"h {f(g['h'], 2)} m"
        v = pr.vista(f"EL {cod}", org, ESC, titulo=f"{cod}", subtitulo=sub, unidade="mm")

        def perto(pc, o=o, d=d, cod=cod, su=su, zw=zw):
            if E.guarda(pc) or pc["grupo"] == "Piso e fundações" or E.cod(pc) in ("graute", "CX-1", "CX-O"):
                return False
            lo, hi = E.bbox(pc)
            cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
            if abs(-(cx - o[0]) * d[1] + (cy - o[1]) * d[0]) > 0.15:
                return False
            ss = [((xx - o[0]) * d[0] + (yy - o[1]) * d[1]) * 1000 for xx in (lo[0], hi[0]) for yy in (lo[1], hi[1])]
            return min(ss) > su[0] - 300 and max(ss) < su[1] + 300 and lo[2] * 1000 > zw[0] - 350 and hi[2] * 1000 < zw[1]
        E.projetar(v, S, perto, cam="OCULTA")
        E.projetar(v, S, lambda pc, cod=cod: E.cod(pc) == cod, cam="METALICA")
        x += w + 22
    y_top -= hmax + 22

# ------------------------------------------------------------------ detalhes típicos 1:5
lg = {}
for l in EJ["ligacoes"]:
    lg.setdefault(l["cod"], l)
yb = Q[1] + 68
dA = pr.vista("DETALHE A", (Q[0] + 46, yb), 5, titulo="DETALHE A — MONTANTE NA LONGARINA", subtitulo="2 M12 8.8 a 70 + bucha Ø21,3 × 2,6 (mesas para fora)", unidade="mm")
dA.ret(0, 0, 5.1, 152.4, "METALICA"); dA.ret(5.1, 0, 43.7, 8.7, "METALICA"); dA.ret(5.1, 143.7, 43.7, 8.7, "METALICA")
dA.ret(48.8, -60, 50, 330, "METALICA")
for zz in (41, 111):
    dA.ret(5.1, zz - 10.65, 43.7, 21.3, "VISTA"); dA.linha((-15, zz), (115, zz), "METALICA")
dA.cota_v([41, 111], 140, 8, total=False)
dA.chamada((80, 200), (12, 10), "montante tubo 50 × 50 × 2 (60 × 60 × 2 na externa)")
dA.chamada((25, 41), (-16, -14), "bucha L 46")
dA.chamada((-10, 111), (-14, 10), "2 M12 8.8")
dA.chamada((2, 75), (-16, 0), "longarina U")
dB = pr.vista("DETALHE B", (Q[0] + 270, yb), 5, titulo="DETALHE B — MONTANTE NA LAJE (GI-10 / GI-11)", subtitulo=lg["GC-LAJE"]["furos"][:60], unidade="mm")
pts = [(-150, -200), (250, -200), (250, 0), (-150, 0)]
dB.poli(pts, "CORTADO", fechada=True); dB.hachura(pts, "AR-CONC", 0.03)
dB.ret(100, 0, 50, 250, "METALICA")
dB.ret(150, 0, 9.5, 102, "METALICA"); dB.ret(150, 0, 102, 9.5, "METALICA")
dB.ret(90.5, 0, 9.5, 102, "METALICA"); dB.ret(-2, 0, 102, 9.5, "METALICA")
dB.linha((205, -70), (205, 20), "METALICA"); dB.linha((45, -70), (45, 20), "METALICA")
dB.linha((80, 60), (170, 60), "METALICA")
dB.chamada((45, -50), (-30, -36), "chumbador químico M10 hef 70 (4)")
dB.chamada((170, 60), (14, 12), "2 L 102 × 102 × 9,5 × 150 + 2 M12 passantes")
dB.chamada((-120, -100), (-6, -16), "borda da laje ≥ 60")
dC = pr.vista("DETALHE C", (Q[0] + 446, yb), 5, titulo="DETALHE C — SUPORTE DO CORRIMÃO", subtitulo=lg["CR-S"]["furos"], unidade="mm")
dC.ret(0, -100, 50, 250, "METALICA")
dC.poli([(50, 60), (90, 60), (90, 110)], "METALICA")
dC.circulo((109, 129), 19.05, "METALICA"); dC.circulo((109, 129), 17.05, "METALICA")
dC.cota_h([50, 90], 30, -8, total=False)
dC.chamada((70, 60), (10, -18), "chapa dobrada 4,75 × 40 em L + 1 M10")
dC.chamada((125, 140), (12, 10), "corrimão Ø38,1 × 2 + abraçadeira 2 M8")
dC.chamada((25, 0), (-14, -8), "montante")
dD = pr.vista("DETALHE D", (Q[0] + 490, yb + 127), 5, titulo="DETALHE D — FECHAMENTO EM BARRAS", subtitulo="barras com as pontas roscadas, porca e contraporca nas L 38", unidade="mm")
dD.ret(0, 0, 38, 4.8, "METALICA"); dD.ret(0, 0, 4.8, 38, "METALICA")
dD.ret(0, 250, 38, 4.8, "METALICA"); dD.ret(0, 216.2, 4.8, 38, "METALICA")
for xb in (19, 149):
    dD.ret(xb - 5, -10, 10, 275, "VISTA")
dD.ret(38, 0, 120, 4.8, "VISTA"); dD.ret(38, 250, 120, 4.8, "VISTA")
dD.cota_h([24, 144], -40, -8, total=False)
dD.chamada((19, -8), (-12, -10), "porca + contraporca")
dD.chamada((80, 120), (14, 10), "vão livre < 150 (esfera de 15 cm não passa)")
dD.chamada((10, 252), (-4, 26), "L 38 × 38 × 4,8 (1 M10 em cada montante)")

# ------------------------------------------------------------------ tabelas e notas
y = Q[3] - 6
lin = []
for g in G:
    gc = g["gc"]
    lin.append([g["cod"], g["nome"][:48], f(g["h"], 2), gc["montante"]["perfil"].replace("tubo ", ""), g["fix"]])
y = pr.tabela(XC, y, "TRECHOS DE GUARDA-CORPO E CORRIMÃO", ["COD", "LOCAL", "h (m)", "MONTANTE", "FIXAÇÃO"], lin, [16, 90, 14, 28, 24], h_lin=4.4)
# rev11: tabela de verificação das ligações fora da folha do cliente (fica na memória e no escadas_detalhe.py)
lin = [[p["faixa"][:46], f(p["pe_direito_min_m"], 2) if p["pe_direito_min_m"] else "livre", p["sob"][:40]] for p in EJ["pe_direito"]]
y = pr.tabela(XC, y - 3, "PÉ-DIREITO LIVRE (≥ 2,10 m)", ["FAIXA", "m", "LIMITADO POR"], lin, [70, 16, 84], h_lin=4.4)
c = EJ["cargas"]
notas = ["RT CBMRS nº 11 Parte 01/2016 e NBR 9050:2020: corrimão DUPLO nos DOIS lados de todos os lances, a 0,92 m (faixa CBMRS 0,80–0,92) e 0,70 m do bocel, tubo redondo Ø38,1 (faixa 38–65), afastado 40 mm de qualquer peça ou parede, contínuo nos patamares, com prolongamento de 30 cm nas pontas livres.",
         "Guarda-corpo em todo lado livre: 0,92 m nos lances internos (vertical do bocel), 1,05 m nos patamares internos e na abertura da laje +3,90, 1,30 m em toda a escada externa; fechamento em barras verticais que não deixam passar a esfera de 15 cm.",
         f"Cargas: {f(c['guarda_corpo_kN_m'], 2)} kN/m horizontal no topo, {f(c['fechamento_kPa'], 2)} kPa no fechamento (não simultâneas) e {f(c['corrimao_kN'], 2)} kN concentrada no corrimão; γf 1,5. Montantes a ≤ 1,20 m.",
         "Ligações todas parafusadas, sem solda: montante encostado nas pontas das mesas da longarina/viga com 2 M12 a 70 e bucha (det. A); na laje, 2 cantoneiras L 102 e 4 chumbadores químicos M10 (det. B — conferir catálogo do chumbador); corrimão em suporte de chapa dobrada (det. C).",
         "As elevações são desenvolvidas ao longo de cada trecho, projetadas do modelo 3D (traço cheio: guarda-corpo; tracejado: longarina, vigas e degraus de apoio). Plantas e cortes nas ND-LET-ES01 e ES02.",
         "Aço ASTM A36 galvanizado a fogo depois da fabricação. Cotas em mm, níveis em m. Não medir no desenho."]
pr.notas(XC, y - 3, notas, 182)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-ES03")
print(len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
for a in avisos:
    print(a)
