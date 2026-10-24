import sys
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas")
from nd_estruturas.quadro_decisao import QuadroDecisao
from matplotlib.patches import Rectangle, Polygon
O = "/tmp/claude-0/-home-claude/0574df45-d9be-51d9-b05f-044e952fe1f4/scratchpad/conf/"
RED, GRN, BLU = "#c62828", "#2e7d32", "#1565c0"
zf = lambda x: 7.195 + 0.03 * x          # fundo da TS-01A montada (modelo_bim: Z0_TS + 3 %)
X = [(9.67, 10.07, "PG-01"), (15.07, 15.32, "P21 PG-02"), (24.18, 24.43, "P19 PG-04"), (29.43, 29.83, "PG-03")]

def base(ax, desce=(0.030, 0.020), sub=0.0, ts_extra=None, apoio=False, placas=True, porta=7.50):
    ax.set_xlim(9.3, 30.2); ax.set_ylim(6.6, 8.75)
    xs = [9.3, 30.2]
    ax.fill_between(xs, [zf(x) + sub for x in xs], [zf(x) + sub + 0.9 for x in xs], color="#7f8fa6", ec="k", lw=.6)
    ax.text(20, zf(20) + sub + 0.45, "TS-01A (V410 / V409) — fundo montado " + f"{zf(10.07)+sub:.3f} → {zf(29.43)+sub:.3f}".replace(".", ","), ha="center", fontsize=7.5)
    for a, b, n in X:
        top = zf(a) - (0.0 if apoio else 0.02) + sub
        ax.add_patch(Rectangle((a, 6.6), b - a, top - 6.6, fc="#9a9a9a", ec="k", lw=.5))
        ax.text((a + b) / 2, 6.65, n, rotation=90, fontsize=6, ha="center", va="bottom")
    for a, c in ((10.07, 15.07), (24.43, 29.43)):
        ax.add_patch(Rectangle((a, 6.6), c - a, porta - 6.6, fc="none", ec=RED, lw=1.4, ls="--"))
        ax.plot([a, c], [7.5, 7.5], color=RED, lw=.8)
        ax.text((a + c) / 2, 6.95, f"portão 500 × {porta*100:.0f}".replace(".", ","), ha="center", fontsize=7, color=RED)
        if placas:
            topo = min(zf(a) + sub, zf(c) + sub) - 0.06
            if topo - porta > 0.15:
                ax.add_patch(Rectangle((a, porta), c - a, topo - porta, fc="#c9c4ba", ec="k", lw=.6))
                ax.text((a + c) / 2, (porta + topo) / 2, f"placa {round((topo-porta)*100)} cm", ha="center", va="center", fontsize=6.5)
    ax.set_aspect("auto")

def gA(ax):
    base(ax, apoio=True)
    ax.text(12.57, 7.56, "fundo 7,497 → 7,647 (não desce: apoiada no PG)", ha="center", fontsize=6.5, color=BLU)
def gB(ax):
    base(ax, sub=0.06)
    ax.text(12.57, 7.60, "fundo 7,557 → 7,707; desce ~3 cm → 7,53", ha="center", fontsize=6.5, color=BLU)
def gC(ax):
    base(ax, porta=7.40)
    ax.text(12.57, 7.44, "fundo 7,497 → 7,467 depois de descer", ha="center", fontsize=6.5, color=BLU)

q = QuadroDecisao("Portão B–P21 da linha 4 com 7,50: como dar o fundo da viga em +7,50 limpo?",
                  "Linha 4, TS-01A (V410 A–C e V409 C–E), inclinada 3 %. Fundo montado no vão B–P21: 7,497 (face do PG-01) a 7,647 (face do P21); "
                  "a TS-01 desce ~30 mm no PG-01 e ~20 mm no P21 depois da montagem (registro DEC dos PG). P19–D: fundo 7,93–8,08 → placa entre 7,50 e a viga (resolvido).")
q.opcao("A", "PG-01 a PG-04 viram apoio da TS-01A", gA, "ressalva", [
    "cabeça dos PG encosta no fundo da TS-01A (NEO + graute depois da montagem): a viga não desce mais nos portões",
    "fundo fica 7,497 na face do PG-01 (3 mm abaixo de 7,50, dentro da tolerância de fabricação ±10 mm) → 7,647 no P21",
    "TS-01A da linha 4 passa a ter 3 apoios na fase de cobertura/sobrecarga: verificar negativo sobre o PG (só 2 cordoalhas no topo) e o PG a compressão",
    "P19–D: placa 37–52 cm entre 7,50 e a viga em ambas as opções"])
q.opcao("B", "subir a linha 4 inteira 6 cm", gB, "ressalva", [
    "TS-01A V409/V410 6 cm acima das linhas 3 e 5: fundo 7,557 → depois de descer ~7,53 no PG-01",
    "telhado: terças passam pela linha 4 com 6 cm a mais (calço/ST mais alto só na linha 4) ou telha com degrau — mexe na cobertura",
    "pilares da linha 4 (A, E) com recuo 6 cm acima e calço 6 cm sobre a I130 no P20"])
q.opcao("C", "portão B–P21 com 7,40", gC, "conflito", [
    "sem mudança estrutural; acabamento com placa/rufo entre 7,40 e a viga",
    "contraria a altura do arquitetônico (7,50) só neste portão"])
q.salvar(O + "decisao_portao_l4.png")
print("ok")
