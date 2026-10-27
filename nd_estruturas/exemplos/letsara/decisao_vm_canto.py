"""rev12 (27/10/2026) — quadro de decisão: apoio da VM de borda da linha 1 no pilar de canto deslocado 10 cm para fora (opção D).

Planta do canto A–1 no nível do apoio (+3,90 e +7,30): pilar de canto 60 × 40 com eixo em y = −0,10 (face externa −0,30,
face interna +0,10); VM 30 × 75 com dente 45 × 40 sobre o CP-MEZ 40 × 40 × 27,9 (largura = face de 40 do pilar), NEO-5F
200 × 200 no eixo da VM; placa da fachada 1 de −0,425 a −0,325; laje alveolar apoiada 10 cm no topo da VM (lado +y).
Grava decisao_vm_canto.png (pasta do exemplo) — quadro para o Nathan; nada é aplicado antes da resposta."""
import json
import sys
from pathlib import Path

AQ = Path(__file__).resolve().parent
sys.path.insert(0, str(AQ)); sys.path.insert(0, str(AQ.parents[1]))
from nd_estruturas.quadro_decisao import QuadroDecisao
from matplotlib.patches import Rectangle
from geometria import DY_CANTO

VMP = json.loads((AQ / "vm_retangular.json").read_text(encoding="utf-8"))["premissas"]
BT, BC, PRJ, XPAD = VMP["b"], VMP["b_consolo"], VMP["dente"]["consolo_proj"], VMP["x_pad"]
NEO = VMP["pad"][0] / 1000
RED, GRN, BLU, CINZA = "#c62828", "#2e7d32", "#1565c0", "#9a9a9a"
YC = -DY_CANTO                                            # eixo do pilar de canto


def base(ax, y_vm, consolo=(YC - 0.20, YC + 0.20), neo_y=None, nota=""):
    ax.set_xlim(-0.55, 1.35); ax.set_ylim(-0.55, 0.55)
    ax.set_aspect("equal")
    ax.add_patch(Rectangle((-0.30, YC - 0.20), 0.60, 0.40, fc=CINZA, ec="k", lw=0.8))
    ax.text(0.0, YC, "pilar de canto\n60 × 40\n(eixo −0,10)", ha="center", va="center", fontsize=6.5)
    ax.add_patch(Rectangle((-0.45, -0.425), 1.80, 0.10, fc="#c9c4ba", ec="k", lw=0.6))
    ax.text(1.0, -0.375, "placa fachada 1", ha="center", va="center", fontsize=6)
    c0, c1 = consolo
    ax.add_patch(Rectangle((0.30, c0), PRJ, c1 - c0, fc="#d7d7d7", ec="k", lw=0.6, ls="--"))
    ax.text(0.30 + PRJ / 2, c0 - 0.03, f"CP-MEZ {round((c1 - c0) * 100)} × {round(PRJ * 100)}", ha="center", va="top", fontsize=6)
    ax.add_patch(Rectangle((0.33, y_vm - BT / 2), 1.05, BT, fc="none", ec=BLU, lw=1.3))
    ax.text(1.05, y_vm, "VM 30 × 75 (dente 45 × 40)", ha="center", va="center", fontsize=6.5, color=BLU)
    ny = y_vm if neo_y is None else neo_y
    ax.add_patch(Rectangle((0.30 + XPAD - NEO / 2, ny - NEO / 2), NEO, NEO, fc="#333", ec="k", lw=0.4, alpha=0.55))
    ax.add_patch(Rectangle((0.33, y_vm + BT / 2 - VMP["apoio_laje"]), 1.05, 0.40, fc="#e6eef8", ec="#7aa", lw=0.5))
    ax.text(1.05, y_vm + BT / 2 + 0.15, "laje alveolar (apoio 10 cm na VM)", ha="center", fontsize=6)
    ax.axhline(0.0, color="#555", lw=0.5, ls="-.")
    ax.text(-0.53, 0.012, "eixo da linha 1", fontsize=6, color="#555")
    if nota:
        ax.text(-0.53, 0.47, nota, fontsize=6.5, color=RED, va="top")
    ax.set_xticks([]); ax.set_yticks([])


def gA(ax):
    base(ax, -0.05)
    ax.text(-0.53, 0.47, "VM a 5 cm para fora: nariz 30 inteiro no consolo,\nneoprene a 5 cm da borda interna do consolo", fontsize=6.5, color=GRN, va="top")


def gB(ax):
    base(ax, -0.05)
    ax.text(-0.53, 0.47, "igual à A só nos vãos de canto (A–B e D–E);\nB–C e C–D continuam no eixo", fontsize=6.5, color="#ef6c00", va="top")


def gC(ax):
    base(ax, 0.0, nota="VM no eixo: 5 cm do nariz fora do consolo;\nneoprene encosta na borda do consolo (0 cm)")
    ax.add_patch(Rectangle((0.33, YC + 0.20), 0.45, 0.05, fc=RED, ec=RED, alpha=0.35))


q = QuadroDecisao("VM de borda da linha 1 no pilar de canto deslocado 10 cm (opção D): onde fica a VM?",
                  "Mezanino +3,90 e +7,30, linha 1, vãos A–B e D–E (VM-01). Pilar de canto: face externa −0,30, face interna +0,10 "
                  "(antes ±0,20). VM 30 × 75 no eixo da linha: −0,15 a +0,15 → 5 cm do dente fora do CP-MEZ de 40.")
q.opcao("A", "VM da linha 1 inteira 5 cm para fora", gA, "resolve", [
    "VM-01 e VM-02 da linha 1 com eixo em y = −0,05 (+3,90 e +7,30): CP-MEZ de 40 inteiro no canto e nos PF (face de 60)",
    "lajes do vão 1–2 5 cm mais longas em toda a linha (9,55 → 9,60 m; uso no ELU 0,85 → ~0,86): mesma marca em todos os vãos",
    "VM a 12 cm da placa (face −0,20); 2º estágio e capa iguais; pilares de fachada sem mudança",
    "refazer lista/quantitativos das lajes e a paginação do +3,90 / +7,30"])
q.opcao("B", "só a VM-01 (vãos de canto) 5 cm para fora", gB, "ressalva", [
    "resolve o apoio, mas as lajes dos vãos A–B e D–E ficam 5 cm mais longas que as de B–D: 2 comprimentos de laje",
    "a VM-01 deixa de ser colinear com a VM-02 (dente de 5 cm na face da faixa de 2º estágio sobre o PF B / D)"])
q.opcao("C", "VM no eixo, consolo e neoprene excêntricos", gC, "conflito", [
    "o CP-MEZ não pode passar da face interna do pilar (+0,10): dente com 25 de 30 cm apoiados",
    "neoprene 200 × 200 no eixo da VM encosta na borda do consolo (NBR 9062:2017 7.2: distância à borda insuficiente)"])
q.salvar(str(AQ / "decisao_vm_canto.png"))
print("ok", AQ / "decisao_vm_canto.png")
