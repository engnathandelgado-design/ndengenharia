"""Imagens sombreadas (PNG) do CS-1 e do NC-1 para a metalúrgica — montado, explodido e conjunto encaixado. Marca 'projeto da ND Engenharia'."""
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import geo_fixacao as GF

L = np.array([0.45, -0.55, 0.70]); L /= np.linalg.norm(L)
ROT = {10: "10 costas", 11: "11 alma", 12: "12 mesa", 13: "13 dente", 14: "14 chapa de ponta", 15: "15 porca", 16: "16 M16 de nível", 17: "17 contraporca", 18: "18 prisioneiro",
       1: "1 teto", 2: "2 base", 3: "3 fundo", 4: "4 parede", 5: "5 aba E", 6: "6 aba D", 7: "7 grampo", 8: "8 grampo"}


def render(solidos, arq, elev=24, azim=-58, titulo="", rotulos=False, alpha_conc=None):
    fig = plt.figure(figsize=(7.2, 6.0), dpi=200)
    ax = fig.add_subplot(111, projection="3d")
    polys, cols = [], []
    for s in solidos:
        base = np.array(s.cor) / 255.0
        for f, n in zip(s.faces, s.normais):
            k = 0.45 + 0.55 * max(0.0, float(n @ L))
            polys.append(f); cols.append(np.clip(base * k * 1.05, 0, 1))
    pc = Poly3DCollection(polys, facecolors=cols, edgecolors=(0.15, 0.17, 0.19, 0.55), linewidths=0.35)
    ax.add_collection3d(pc)
    P = np.vstack([np.vstack(s.faces) for s in solidos])
    c, r = (P.max(0) + P.min(0)) / 2, (P.max(0) - P.min(0)).max() / 2 * 0.78
    ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r); ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1)); ax.view_init(elev=elev, azim=azim); ax.set_axis_off()
    if rotulos:
        feito = set()
        for s in solidos:
            if s.item in ROT and s.item not in feito:
                feito.add(s.item)
                p = s.centro
                ax.text(p[0], p[1], p[2], "  " + ROT[s.item].split()[0], fontsize=8, color="#a9470c", weight="bold")
    fig.text(0.02, 0.02, "projeto da ND Engenharia", fontsize=9, style="italic", color="#5d6870")
    if titulo:
        fig.text(0.02, 0.95, titulo, fontsize=12, weight="bold", color="#1d2327")
    plt.subplots_adjust(0, 0, 1, 1)
    fig.savefig(arq, dpi=200, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    D = "/home/claude/letsara/pranchas/img/"
    render(GF.cs1_solidos(0), D + "cs1_montado.png", titulo="CS-1 — console soldado (lado da placa)", azim=58)
    render(GF.cs1_solidos(34), D + "cs1_explodido.png", titulo="CS-1 — explodido (nº = item da lista)", azim=58, rotulos=True)
    render(GF.nc1_solidos(0), D + "nc1_montado.png", titulo="NC-1 — nicho soldado (vista pela boca)", azim=-62, elev=22)
    render(GF.nc1_solidos(34), D + "nc1_explodido.png", titulo="NC-1 — explodido (nº = item da lista)", azim=-62, elev=22, rotulos=True)
    render(GF.nc1_no_console(0) + GF.cs1_solidos(0), D + "conjunto.png", titulo="CS-1 encaixado no NC-1 (posição final, G = 50; concreto oculto)", azim=28, elev=30)
    print("ok")
