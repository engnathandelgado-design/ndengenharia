"""ND-LET-CS01 — CONSOLOS DOS PILARES POR MARCA (rev11, pedido do Nathan 26/10/2026): cada consolo de pilar tem marca própria
C1, C2… (consolos_marcas.py; iguais = mesma geometria, pino, neoprene e tirante). Por marca: fôrma em vista lateral 1:10 cotada
(largura, projeção, altura na face e na ponta da mísula, caimento), pino com embutido/livre/total, neoprene, armadura (tirante U,
costura e estribos — as mesmas posições do DETALHE C da folha de cada pilar) e a lista "usado nos pilares". Tudo lido do registro."""
import json, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha
import apoios_pilar as AP
import renomear as RN

R = json.load(open(AP._REG, encoding="utf-8"))
g = AP.g
pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                        conteudo="CONSOLOS DOS PILARES — MARCAS C1 A C%d: FÔRMA, PINO, NEOPRENE, ARMADURA E PILARES QUE USAM" % len(R["lista"]),
                        desenho="ND-LET-CS01", folha="01/01", fase="PARA APROVAÇÃO"))
pr.revisao("00", "26/10/2026", "EMISSÃO INICIAL: MARCA PRÓPRIA DE CADA CONSOLO (C1, C2…)")
pr.revisao("R12", "27/10/2026", "PILARES E QUANTIDADES DE CADA CONSOLO PELA GEOMETRIA; POSIÇÃO NA FACE E CAIMENTO NA TABELA; DESENHOS 1:5")
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
FACE_POS = {"D": "rente à face externa (fachada)", "B": "rente à face externa (fachada)", "C": "rente à face C (externa, placas)"}
for k, e in enumerate(R["lista"]):
    cx = Q[0] + 30 + (k % 3) * 385
    cy = Q[3] - 80 - (k // 3) * 335
    v = pr.vista(e["marca"], (cx + 120, cy - 40), 5, titulo=f"{e['marca']} — {e['tipo']} (vista lateral)", subtitulo="fôrma; topo " + ("com caimento %g %%" % (e["incl"] * 100) if e["incl"] else "horizontal"), unidade="cm")
    proj, h, hp, larg = e["proj"], e["h"], e["hp"], e["larg"]
    v.poli([(-250, -h - 150), (-250, 150), (0, 150), (0, -h - 150)], "VISTA")
    v.interrupcao((-250, -h - 150), (0, -h - 150)); v.interrupcao((-250, 150), (0, 150))
    v.poli([(0, -h), (proj, -hp), (proj, proj * e["incl"]), (0, 0)], "VISTA")
    v.hachura([(0, -h), (proj, -hp), (proj, proj * e["incl"]), (0, 0)], "AR-CONC", 0.03)
    v.cota_v(sorted(set([-h, -hp, 0])), proj, 10, total=False)
    v.cota_h([0, proj], -h, -10)
    v.texto((-125, 60), "pilar", "nota", "MIDDLE_CENTER")
    # rev12 (item 2): vista de frente da face do pilar com a posição do consolo (centrado ou rente) — o que distingue C1 de C2
    G0 = json.load(open(f"/home/claude/letsara/pranchas/{e['marcas_pilar'][0]}_geom.json", encoding="utf-8"))
    c0 = next(c for c in G0["consolos"] if AP.marca_consolo(c) == e["marca"])
    W = G0["B"] if c0["face"] in "AC" else G0["H"]
    vf = pr.vista(e["marca"] + "F", (cx + 250, cy - 40), 10, titulo=f"{e['marca']} — FRENTE", subtitulo=f"face {c0['face']} do pilar ({AP.g(W / 10)} cm)", unidade="cm")
    vf.poli([(-W / 2, -h - 150), (-W / 2, 150), (W / 2, 150), (W / 2, -h - 150)], "VISTA")
    vf.interrupcao((-W / 2, -h - 150), (W / 2, -h - 150)); vf.interrupcao((-W / 2, 150), (W / 2, 150))
    u_ = e["exc"] * (-1 if e["exc_face"] in ("D", "C") else 1)
    vf.ret(u_ - larg / 2, -h, larg, h, "VISTA"); vf.hachura([(u_ - larg / 2, -h), (u_ + larg / 2, -h), (u_ + larg / 2, 0), (u_ - larg / 2, 0)], "AR-CONC", 0.03)
    vf.linha((0, -h - 150), (0, 150), "EIXO")
    vf.cota_h(sorted(set([-W / 2, u_ - larg / 2, u_ + larg / 2, W / 2])), -h, -10, total=False)
    if e["exc"]:
        vf.texto((-W / 2, 160), "face " + e["exc_face"], "min", "BOTTOM_CENTER")
    a = ARM.get((e["tipo"], larg, proj, h))
    pos_face = (f"{FACE_POS.get(e['exc_face'], 'rente à face ' + e['exc_face'])}: eixo do consolo a {AP.g(e['exc'] / 10)} cm do eixo da face" if e["exc"] else "centrado na face")
    lin = [["LARGURA × PROJEÇÃO", f"{AP.g(larg / 10)} × {AP.g(proj / 10)} cm"], ["ALTURA FACE / PONTA", f"{AP.g(round(h / 10, 1))} / {AP.g(round(hp / 10, 1))} cm"],
           ["POSIÇÃO NA FACE", pos_face], ["TOPO", ("caimento %g %%" % (e["incl"] * 100)) if e["incl"] else "horizontal"],
           ["PINO", e["pino"]], ["NEOPRENE", "%d×%d×%d mm" % tuple(e["neo"])], ["TIRANTE", e["tirante"]]]
    if a:
        aa, mk = a
        lin.append(["ARMADURA", f"{aa['pos'][0]} {aa['nt']} Ø{AP.g(aa['dt'])} (U) · {aa['pos'][1]} 2 Ø10 (costura) · {aa['pos'][2]} {aa['n6']} Ø8 (estribos) — DET. C da folha do pilar"])
    # rev12 (revisão rev12, item 2): pilares e quantidades contados da geometria das folhas (registro), nomes protegidos da renomeação
    lin.append(["QUANTIDADE", f"{e['n']} consolos"])
    lin.append(["PILARES (consolos)", RN.N(", ".join(f"{n_} ({q_})" for n_, q_ in e["por_pilar"].items()))])
    pr.tabela(cx, cy - 62 - (h + 150) / 5, f"{e['marca']} — DADOS", ["ITEM", "VALOR"], lin, [60, 250])
pr.notas(Q[0] + 8, Q[3] - 30, ["Marca própria de cada consolo (C1, C2…); consolos com a mesma geometria, posição na face, caimento, pino, neoprene e tirante têm a mesma marca. "
                                  "A marca aparece nas faces dos pilares, no quadro APOIOS E ESPERAS de cada folha de pilar e nesta folha.",
                                  "Fôrma em cm (vistas 1:5); pinos e neoprene em mm. Pilares e quantidades contados nas folhas de cada pilar (quadro APOIOS E ESPERAS). Armadura: DETALHE C da folha de cada pilar (mesmas posições).",
                                  "Topo do consolo com o caimento indicado; neoprene centrado no eixo do consolo; pino a partir da face do pilar conforme a tabela."], 900)
av = pr.salvar("/home/claude/letsara/pranchas/ND-LET-CS01")
print("ND-LET-CS01", len([x for x in av if x[0] == "ERRO"]), "erros,", len(av), "avisos")
for x in av:
    print("  ", x)
