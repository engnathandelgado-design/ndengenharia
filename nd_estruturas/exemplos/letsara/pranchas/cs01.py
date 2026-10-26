"""ND-LET-CS01 — CONSOLOS DOS PILARES POR MARCA (rev11, pedido do Nathan 26/10/2026): cada consolo de pilar tem marca própria
C1, C2… (consolos_marcas.py; iguais = mesma geometria, pino, neoprene e tirante). Por marca: fôrma em vista lateral 1:10 cotada
(largura, projeção, altura na face e na ponta da mísula, caimento), pino com embutido/livre/total, neoprene, armadura (tirante U,
costura e estribos — as mesmas posições do DETALHE C da folha de cada pilar) e a lista "usado nos pilares". Tudo lido do registro."""
import json, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha
import apoios_pilar as AP

R = json.load(open(AP._REG, encoding="utf-8"))
g = AP.g
pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="CONSOLOS DOS PILARES — MARCAS C1 A C%d: FÔRMA, PINO, NEOPRENE, ARMADURA E PILARES QUE USAM" % len(R["lista"]),
                        desenho="ND-LET-CS01", folha="01/01", fase="PARA APROVAÇÃO"))
pr.revisao("00", "26/10/2026", "EMISSÃO INICIAL: MARCA PRÓPRIA DE CADA CONSOLO (C1, C2…) — PEDIDO DO NATHAN")
Q = pr.quadro
pr.texto(Q[0] + 8, Q[3] - 16, "CONSOLOS DOS PILARES — MARCAS C1 A C%d" % len(R["lista"]), "grande", "TITULO")
pr.texto(Q[0] + 8, Q[3] - 26, R["criterio"], "nota", "TEXTO")
x0, y0 = Q[0] + 40, Q[3] - 70
ARM = {}
import glob
for f in glob.glob("/home/claude/letsara/pranchas/arm/*.json"):
    try:
        J = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    for a in J.get("arm_cons", []):
        for fc, z, tp in a["faces"]:
            ARM.setdefault((tp, a["larg"], a["proj"], a["h"]), (a, J["marca"]))
col = 0
for k, e in enumerate(R["lista"]):
    cx = Q[0] + 30 + (k % 3) * 385
    cy = Q[3] - 60 - (k // 3) * 380
    v = pr.vista(e["marca"], (cx + 60, cy - 50), 10, titulo=f"{e['marca']} — {e['tipo']} (vista lateral)", subtitulo="fôrma; topo " + ("com caimento %g %%" % (e["incl"] * 100) if e["incl"] else "horizontal"), unidade="cm")
    proj, h, hp, larg = e["proj"], e["h"], e["hp"], e["larg"]
    v.poli([(-250, -h - 150), (-250, 250), (0, 250), (0, -h - 150)], "VISTA")
    v.interrupcao((-250, -h - 150), (0, -h - 150)); v.interrupcao((-250, 250), (0, 250))
    v.poli([(0, -h), (proj, -hp), (proj, proj * e["incl"]), (0, 0)], "VISTA")
    v.hachura([(0, -h), (proj, -hp), (proj, proj * e["incl"]), (0, 0)], "AR-CONC", 0.03)
    v.cota_v(sorted(set([-h, -hp, 0])), proj, 10, total=False)
    v.cota_h([0, proj], -h, -10)
    v.texto((-125, 120), "pilar", "nota", "MIDDLE_CENTER")
    a = ARM.get((e["tipo"], larg, proj, h))
    lin = [["LARGURA × PROJEÇÃO", f"{g(larg / 10)} × {g(proj / 10)} cm"], ["ALTURA FACE / PONTA", f"{g(round(h / 10, 1))} / {g(round(hp / 10, 1))} cm"],
           ["PINO", e["pino"]], ["NEOPRENE", "%d×%d×%d mm" % tuple(e["neo"])], ["TIRANTE", e["tirante"]]]
    if a:
        aa, mk = a
        lin.append(["ARMADURA", f"{aa['pos'][0]} {aa['nt']} Ø{g(aa['dt'])} (U) · {aa['pos'][1]} 2 Ø10 (costura) · {aa['pos'][2]} {aa['n6']} Ø8 (estribos) — DET. C da folha do pilar"])
    lin.append(["QUANTIDADE", f"{e['n']} consolos"])
    lin.append(["PILARES", ", ".join(e["pilares"])])
    pr.tabela(cx, cy - 175, f"{e['marca']} — DADOS", ["ITEM", "VALOR"], lin, [60, 250])
pr.notas(Q[0] + 30 + 2 * 385, Q[3] - 60 - 380 - 10, ["Marca própria de cada consolo (C1, C2…); consolos com a mesma geometria, pino, neoprene e tirante têm a mesma marca. "
                                  "A marca aparece nas faces dos pilares, no quadro APOIOS E ESPERAS de cada folha de pilar e nesta folha.",
                                  "Fôrma em cm; pinos e neoprene em mm. Armadura: DETALHE C da folha de cada pilar (mesmas posições).",
                                  "Topo do consolo com o caimento indicado; neoprene centrado no eixo do consolo; pino a partir da face do pilar conforme a tabela."], 190)
av = pr.salvar("/home/claude/letsara/pranchas/ND-LET-CS01")
print("ND-LET-CS01", len([x for x in av if x[0] == "ERRO"]), "erros,", len(av), "avisos")
for x in av:
    print("  ", x)
