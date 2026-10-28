"""Planta da linha 4 (portões) para conferência do Nathan — tudo de geometria.py / portao_l4.json."""
import sys, json
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import geometria as G
PJ = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/portao_l4.json"))
sys.path.insert(0, "/home/claude/letsara/pranchas")
import renomear as RN
Y4 = G.Y_LIN[G.LINHA_PORTOES]
o = 0.025; tpl = 0.10                                     # folga placa–pilar e espessura da placa (modelo_bim)
y_pl1 = G.Y_FACE_L4 - o; y_pl0 = y_pl1 - tpl
PIL = [("PG-01", *G.PG_L4["PG-01"][1:]), ("PG-02", *G.PG_L4["PG-02"][1:]), ("P11", G.X_EIXO["C"], 0.40, 0.40), ("PG-04", *G.PG_L4["PG-04"][1:]), ("PG-03", *G.PG_L4["PG-03"][1:])]
YP = {"PG-01": G.Y_PG["PG-01"], "PG-02": G.Y_PG["PG-02"], "P11": Y4, "PG-04": G.Y_PG["PG-04"], "PG-03": G.Y_PG["PG-03"]}
NOME = {k: RN.pilar_em(x, YP[k]) for k, x, *_ in PIL}
C_PIL, C_PL, C_COT, C_EIXO = "#555555", "#2f7d32", "#b5520a", "#1f5fa8"
fs = 9

def cota_h(ax, x0, x1, y, txt, dy=0.0):
    ax.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<|-|>", color=C_COT, lw=0.9, shrinkA=0, shrinkB=0))
    ax.text((x0 + x1) / 2, y + dy, txt, color=C_COT, ha="center", va="bottom", fontsize=fs)

def cota_v(ax, y0, y1, x, txt, lado=1):
    ax.annotate("", (x, y0), (x, y1), arrowprops=dict(arrowstyle="<|-|>", color=C_COT, lw=0.9, shrinkA=0, shrinkB=0))
    ax.text(x + lado * 0.01, (y0 + y1) / 2, txt, color=C_COT, ha="left" if lado > 0 else "right", va="center", fontsize=fs)

fig = plt.figure(figsize=(16.5, 11.7))
# ---------------------------------------------------------------- 1) linha 4 inteira (eixo B ao eixo D)
ax = fig.add_axes([0.04, 0.58, 0.92, 0.31])
ax.set_title("LINHA 4 — PORTÕES: PLANTA (vista de cima, y cresce para a linha 9)", fontsize=12, loc="left")
xa, xb = G.X_EIXO["B"] - 1.2, G.X_EIXO["D"] + 1.2
ax.axhline(Y4, color=C_EIXO, lw=0.7, ls=(0, (8, 3, 1, 3))); ax.text(11.0, Y4 + 0.03, "eixo da linha 4", color=C_EIXO, fontsize=fs)
for e in "BCD":
    ax.axvline(G.X_EIXO[e], color=C_EIXO, lw=0.7, ls=(0, (8, 3, 1, 3))); ax.text(G.X_EIXO[e], Y4 + 1.12, e, color=C_EIXO, ha="center", fontsize=11, weight="bold")
ax.add_patch(Rectangle((xa, Y4 - 0.20), xb - xa, 0.40, fill=False, ec="#999999", ls="--", lw=0.8))
ax.text(13.3, Y4 + 0.21, "TS-01A (mesa 40, por cima)", color="#777777", ha="center", va="bottom", fontsize=fs)
for k, x, bx, by in PIL:
    y = YP[k]
    ax.add_patch(Rectangle((x - bx / 2, y - by / 2), bx, by, color=C_PIL))
    ax.text(x + 0.25, y + by / 2 + 0.05, f"{NOME[k]}\n{k if k != 'P11' else 'PC-02'} {round(by*100)}×{round(bx*100)}", ha="left", va="bottom", fontsize=fs)
xs_pl = [(G.X_EIXO["B"] - 1.2, G.PG_L4["PG-01"][1]), (G.PG_L4["PG-02"][1], G.PG_L4["PG-04"][1]), (G.PG_L4["PG-03"][1], G.X_EIXO["D"] + 1.2)]
for x0, x1 in xs_pl:
    ax.add_patch(Rectangle((x0, y_pl0), x1 - x0, tpl, color=C_PL, alpha=0.75))
ax.text(G.X_EIXO["C"], y_pl0 - 0.05, "placas de fechamento (parede C, lado da área aberta)", color=C_PL, ha="center", va="top", fontsize=fs)
for (a, b), nm in (((G.PG_L4["PG-01"][1] + 0.20, G.PG_L4["PG-02"][1] - 0.20), "portão 1"), ((G.PG_L4["PG-04"][1] + 0.20, G.PG_L4["PG-03"][1] - 0.20), "portão 2")):
    cota_h(ax, a, b, Y4 - 0.48, f"{nm}: vão livre {b - a:.2f} m (face a face)".replace(".", ","))
cota_h(ax, G.X_EIXO["B"], G.PG_L4["PG-02"][1], Y4 + 0.85, f"{G.PG_L4['PG-02'][1] - G.X_EIXO['B']:.3f}".replace(".", ","))
cota_h(ax, G.PG_L4["PG-04"][1], G.X_EIXO["D"], Y4 + 0.85, f"{G.X_EIXO['D'] - G.PG_L4['PG-04'][1]:.3f}".replace(".", ","))
ax.set_xlim(xa, xb); ax.set_ylim(Y4 - 0.75, Y4 + 1.30); ax.set_aspect(4.0); ax.set_yticks([]); ax.set_xlabel("x (m, a partir do eixo A)")
ax.text(xa, Y4 - 0.73, "escala vertical (y) ampliada 4× para mostrar o alinhamento", fontsize=8, color="#666666")
# ---------------------------------------------------------------- 2) detalhes em escala real nos PG-02 e PG-04
for i, k in enumerate(("PG-02", "PG-04")):
    ax2 = fig.add_axes([0.04 + i * 0.49, 0.06, 0.44, 0.46])
    x = G.PG_L4[k][1]; bx, by = G.PG_L4[k][2], G.PG_L4[k][3]; y = YP[k]
    lado = -1 if k == "PG-02" else 1                       # portão à esquerda do PG-02, à direita do PG-04
    viz = "PG-01" if k == "PG-02" else "PG-03"
    ax2.set_title(f"DETALHE {i + 1} — {NOME[k]} ({k}) e alinhamento das faces (sem escala vertical ampliada)", fontsize=11, loc="left")
    ax2.axhline(Y4, color=C_EIXO, lw=0.7, ls=(0, (8, 3, 1, 3))); ax2.text(x + 0.62 * (-lado), Y4 + 0.012, "eixo da linha 4", color=C_EIXO, fontsize=fs, ha="center")
    ax2.axvline(x, color=C_EIXO, lw=0.6, ls=(0, (8, 3, 1, 3)))
    ax2.axhline(y, xmin=0.0, xmax=1.0, color=C_PIL, lw=0.5, ls=":")
    ax2.add_patch(Rectangle((x - bx / 2, y - by / 2), bx, by, color=C_PIL))
    ax2.text(x, y + 0.035, f"{NOME[k]} {round(by*100)}×{round(bx*100)}", color="white", ha="center", va="center", fontsize=fs)
    # placa contínua do lado fechado (P11 / continuidade) e portão do outro lado
    xp0, xp1 = (x, x + 0.95) if k == "PG-02" else (x - 0.95, x)
    ax2.add_patch(Rectangle((xp0, y_pl0), xp1 - xp0, tpl, color=C_PL, alpha=0.75)); ax2.text((xp0 + xp1) / 2, y_pl0 + tpl / 2, "placa", color="white", ha="center", va="center", fontsize=fs)
    ax2.axhline(G.Y_FACE_L4, color="#c62828", lw=1.0, ls="--")
    ax2.text(x - 1.07, Y4 - 0.465, "- - -  plano das faces dos pilares 40×40 (PG-01, P11, PG-03) = face do PG; placas a 2,5 cm", color="#c62828", ha="left", va="bottom", fontsize=fs)
    ax2.add_patch(Rectangle((x - bx / 2, Y4 - by / 2), bx, by, fill=False, ec="#999999", ls="--", lw=0.8))
    ax2.text(x - bx / 2, Y4 + by / 2 + 0.008, "antes: 25×40 centrado na linha (face 7,5 cm atrás)", color="#999999", fontsize=8, va="bottom")
    neo = PJ["neoprene"][k]
    ax2.add_patch(Rectangle((x - neo["nx_mm"] / 2000, y - neo["ny_mm"] / 2000), neo["nx_mm"] / 1000, neo["ny_mm"] / 1000, fill=False, ec="#f9a825", lw=1.2))
    ax2.text(x, y - 0.045, f"NEO-7 {neo['dim_mm']}", color="#f9a825", ha="center", va="center", fontsize=7)
    xc = x + lado * (bx / 2 + 0.12)
    cota_v(ax2, Y4, y, xc, f"{(Y4 - y) * 100:.1f} cm (eixo PG × linha 4)".replace(".", ","), lado)
    cota_v(ax2, G.Y_FACE_L4, y, xc + lado * 0.36, f"{(y - G.Y_FACE_L4) * 100:.1f} cm".replace(".", ","), lado)
    cota_v(ax2, y_pl1, G.Y_FACE_L4, x - lado * (bx / 2 + 0.62), "2,5 cm até a placa", -lado)
    cota_v(ax2, Y4, G.Y_FACE_L4, x - lado * (bx / 2 + 0.14), f"{(Y4 - G.Y_FACE_L4) * 100:.0f} cm (meia seção dos 40×40)", -lado)
    xf = x + lado * bx / 2
    ax2.annotate("", (xf, y - by / 2 - 0.15), (xf + lado * 0.60, y - by / 2 - 0.15), arrowprops=dict(arrowstyle="-|>", color=C_COT, lw=0.9))
    ax2.text(xf + lado * 0.30, y - by / 2 - 0.145, f"portão: 5,00 m livres até a face do {NOME[viz]}", color=C_COT, ha="center", va="bottom", fontsize=fs)
    ax2.set_xlim(x - 1.1, x + 1.1); ax2.set_ylim(Y4 - 0.48, Y4 + 0.30); ax2.set_aspect("equal"); ax2.set_yticks([]); ax2.set_xlabel(f"x (m) — eixo do pilar em x = {x:.3f}".replace(".", ","))
fig.text(0.04, 0.965, "LETSARA — linha 4 (portões): P21 (PG-02) e P19 (PG-04) com a face no plano dos vizinhos — rev12, 27/10/2026", fontsize=14, weight="bold")
fig.text(0.04, 0.94, f"Eixo dos PG-02/PG-04 deslocado {G.DY_PG['PG-02']*100:.1f} cm da linha 4 para o lado das placas (y = {G.Y_PG['PG-02']:.3f}); x mantido em {G.PG_L4['PG-02'][1]:.3f} e {G.PG_L4['PG-04'][1]:.3f} (5.00 m livres face a face, conferido no arquitetônico R01)".replace(".", ","), fontsize=10)
fig.savefig(sys.argv[1], dpi=170)
print("ok", sys.argv[1])
