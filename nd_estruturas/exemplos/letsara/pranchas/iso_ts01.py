"""Isométrico 3D de detalhamento — TS-01 (viga I90 de cobertura). m."""
import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

D = json.load(open("/home/claude/letsara/pranchas/ts01.json"))
P = D["P"]; L, H = P["L"] / 1000, P["h"] / 1000
SEC = [(-0.20, 0), (0.20, 0), (0.20, 0.15), (0.075, 0.23), (0.075, 0.70), (0.20, 0.78), (0.20, 0.90),
       (-0.20, 0.90), (-0.20, 0.78), (-0.075, 0.70), (-0.075, 0.23), (-0.20, 0.15)]
CONC, ACO, NEO = "#cfcfcf", "#d9822b", "#3a3a3a"


def prisma(ax, sec_yz, x0, x1, cor, alpha=1.0, lw=0.3):
    n = len(sec_yz)
    a = [(x0, y, z) for y, z in sec_yz]; b = [(x1, y, z) for y, z in sec_yz]
    faces = [a, b] + [[a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]] for i in range(n)]
    ax.add_collection3d(Poly3DCollection(faces, facecolor=cor, edgecolor="#555", linewidths=lw, alpha=alpha))


def caixa(ax, x0, y0, z0, dx, dy, dz, cor, alpha=1.0):
    prisma(ax, [(y0, z0), (y0 + dy, z0), (y0 + dy, z0 + dz), (y0, z0 + dz)], x0, x0 + dx, cor, alpha)


def cilindro(ax, xc, yc, z0, z1, r, cor):
    t = np.linspace(0, 2 * np.pi, 16)
    for k in range(len(t) - 1):
        q = [(xc + r * np.cos(t[k]), yc + r * np.sin(t[k]), z0), (xc + r * np.cos(t[k + 1]), yc + r * np.sin(t[k + 1]), z0),
             (xc + r * np.cos(t[k + 1]), yc + r * np.sin(t[k + 1]), z1), (xc + r * np.cos(t[k]), yc + r * np.sin(t[k]), z1)]
        ax.add_collection3d(Poly3DCollection([q], facecolor=cor, edgecolor=cor, linewidths=0.2))


def alca(ax, x, z):
    t = np.linspace(0, np.pi, 20)
    ax.plot(x + 0.06 * np.cos(t), 0 * t, z + 0.12 * np.sin(t), color=ACO, lw=2.2)


def rot(ax, p, txt, d=(0.6, 0.0, 0.5)):
    q = (p[0] + d[0], p[1] + d[1], p[2] + d[2])
    ax.plot([p[0], q[0]], [p[1], q[1]], [p[2], q[2]], color="#222", lw=0.6)
    ax.text(*q, txt, fontsize=7.2, color="#111")


def peca(ax, x_ini=0.0, x_fim=None, rotulos=True):
    x_fim = L if x_fim is None else x_fim
    mc = P["maciço"] / 1000
    rb = [(-0.2, 0), (0.2, 0), (0.2, H), (-0.2, H)]
    if x_ini < mc:
        prisma(ax, rb, x_ini, mc, CONC)
    prisma(ax, SEC, max(x_ini, mc), min(x_fim, L - mc), CONC)
    if x_fim > L - mc:
        prisma(ax, rb, L - mc, x_fim, CONC)
    xt = [(P["terca_ini"] + k * P["terca_passo"]) / 1000 for k in range(P["n_tercas"])]
    for x in xt:
        if x_ini <= x <= x_fim:
            caixa(ax, x - 0.10, -0.06, H, 0.20, 0.12, 0.0125, ACO)                 # CH-T1
            ax.plot([x, x], [-0.075, 0.075], [H - 0.30, H - 0.30], color=ACO, lw=2)  # TB-2
    for x in (P["pino_x"] / 1000, L - P["pino_x"] / 1000):
        if x_ini <= x <= x_fim:
            cilindro(ax, x, 0, -0.03, H + 0.04, 0.025, "#7a7a7a")                    # TB-1 / pino
            caixa(ax, x - 0.075, -0.15, -0.0125, 0.15, 0.30, 0.0125, ACO)            # CH-A1
            caixa(ax, x - 0.075, -0.15, -0.0225, 0.15, 0.30, 0.010, NEO)             # neoprene
    for x in (P["a_alca"] / 1000, L - P["a_alca"] / 1000):
        if x_ini <= x <= x_fim:
            alca(ax, x, H)
    return xt


fig = plt.figure(figsize=(16, 9.5), dpi=150)
# --- 1) peça inteira
ax = fig.add_subplot(2, 1, 1, projection="3d")
xt = peca(ax)
ax.set_box_aspect((L, 1.6, 1.8)); ax.set_xlim(0, L); ax.set_ylim(-0.8, 0.8); ax.set_zlim(-0.2, 1.6)
ax.view_init(elev=22, azim=-62); ax.set_axis_off()
rot(ax, (P["a_alca"] / 1000, 0, H + 0.12), "AL-1 alça de içamento (2x)", (0.4, 0, 0.5))
rot(ax, (xt[4], 0, H), f"CH-T1 chapa com furos p/ terça ({len(xt)}x, c/1,60 m)", (0.3, 0, 0.55))
rot(ax, (xt[8], 0.075, H - 0.30), "TB-2 furo passante p/ mão-francesa", (0.6, 0, -0.75))
rot(ax, (L - 0.15, 0, -0.02), "CH-A1 + neoprene + TB-1 (pino Ø25)", (-3.2, 0, -0.55))
rot(ax, (0.25, 0.2, 0.5), "maciço 500", (0.6, 0, 0.8))
ax.set_title(f"{P['marca']} — viga I90 de cobertura · {P['L']/1000:.2f} m · {D['peso']/10.0:.1f} t · {P['qtd']} peças".replace(".", ","), fontsize=11, pad=-10)

# --- 2) detalhe da ponta com terça, cantoneira e mão-francesa
ax2 = fig.add_subplot(2, 2, 3, projection="3d")
peca(ax2, 0, 1.2)
x = xt[0]
# terças Ue 300 (dos dois lados da viga, perpendiculares) — trecho representativo
for s in (1, -1):
    yy0 = 0.0 if s > 0 else -1.0
    caixa(ax2, x - 0.0425, yy0 + (0.03 if s > 0 else -0.03), H + 0.0125, 0.085, 1.0, 0.30, "#9fb6cc", 0.95)
    caixa(ax2, x - 0.11, -0.05 if s > 0 else -0.01, H + 0.0125, 0.07, 0.06, 0.12, "#5d7fa3")       # cantoneira de apoio
    ax2.plot([x, x], [s * 0.075, s * 0.55], [H - 0.30, H + 0.0125], color="#2f4f6f", lw=3)          # mão-francesa L50×5
ax2.set_box_aspect((1.2, 2.0, 1.4)); ax2.set_xlim(0, 1.2); ax2.set_ylim(-1.0, 1.0); ax2.set_zlim(-0.1, 1.3)
ax2.view_init(elev=20, azim=-50); ax2.set_axis_off()
rot(ax2, (x, 0.4, H + 0.3), "terça Ue 300×85×25×3,00", (0.1, 0.2, 0.25))
rot(ax2, (x - 0.08, 0.0, H + 0.1), "cantoneira de apoio (2 M16 na CH-T1)", (0.25, -0.6, 0.35))
rot(ax2, (x, 0.3, H - 0.15), "mão-francesa L 50×5 (TB-2)", (0.35, 0.3, -0.45))
rot(ax2, (0.15, 0, -0.03), "TB-1 / pino Ø25 grauteado", (0.4, -0.4, -0.25))
ax2.set_title("Detalhe A — ponta, apoio e ligação da terça", fontsize=9.5)

# --- 3) seção com cordoalhas
ax3 = fig.add_subplot(2, 2, 4)
ys, zs = zip(*(SEC + [SEC[0]]))
ax3.fill(ys, zs, color=CONC, ec="k", lw=1.2)
for xc in P["x_cord"]:
    ax3.add_patch(plt.Circle((xc / 1000, P["y_cord"] / 1000), 0.0085, color="#c0392b"))
ax3.add_patch(plt.Rectangle((-0.10, H), 0.20, 0.0125, color=ACO))
ax3.plot([-0.075, 0.075], [H - 0.3, H - 0.3], color=ACO, lw=3)
ax3.set_aspect("equal"); ax3.axis("off")
ax3.text(0.24, 0.07, "6 cordoalhas Ø12,7 (cabeçote 50×42)", fontsize=8)
ax3.text(0.24, 0.90, "CH-T1", fontsize=8); ax3.text(0.24, 0.60, "TB-2", fontsize=8)
ax3.set_xlim(-0.35, 0.9); ax3.set_title("Seção corrente", fontsize=9.5)
fig.savefig("/home/claude/letsara/pranchas/ISO-TS01.png", bbox_inches="tight")
