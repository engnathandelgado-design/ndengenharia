"""Quadro de decisão de projeto: uma imagem para o engenheiro analisar e escolher.

Uso típico (quando uma escolha muda o projeto):
    q = QuadroDecisao("Nível da laje de cima do mezanino", "Linha 2, junto ao eixo A")
    q.fonte("Corte AA' do R01 (estrutural)", "caa.png")          # recortes dos documentos do cliente
    q.opcao("A", "+7,30 do R01", desenhar_a, veredito="resolve", consequencias=["TS-01 da linha 2 com h 75"])
    q.opcao("B", "+7,96 do arquitetônico", desenhar_b, veredito="conflito", consequencias=[...])
    q.salvar("decisao.png")

Cada opção recebe um eixo matplotlib e desenha a solução em escala (a função é do projeto).
O quadro sempre mostra: a pergunta, o local, as fontes lado a lado, as opções com o veredito em cor
(resolve / com ressalva / conflito) e as consequências de cada uma, para a decisão ser tomada olhando o desenho.
Sem marca nem logo (o quadro é de trabalho interno com o projetista).
"""
from __future__ import annotations

from dataclasses import dataclass, field
import textwrap
from typing import Callable

CORES_VEREDITO = {"resolve": "#2e7d32", "ressalva": "#ef6c00", "conflito": "#c62828"}
ROTULO_VEREDITO = {"resolve": "RESOLVE", "ressalva": "RESOLVE COM RESSALVA", "conflito": "NÃO RESOLVE"}


class DadoInvalido(ValueError):
    pass


@dataclass
class _Opcao:
    letra: str
    titulo: str
    desenhar: Callable
    veredito: str
    consequencias: list = field(default_factory=list)


class QuadroDecisao:
    def __init__(self, pergunta: str, local: str = ""):
        if not pergunta.strip():
            raise DadoInvalido("o quadro precisa de uma pergunta")
        self.pergunta, self.local = pergunta, local
        self.fontes: list[tuple[str, str]] = []
        self.opcoes: list[_Opcao] = []

    def fonte(self, legenda: str, imagem_png: str):
        self.fontes.append((legenda, imagem_png))
        return self

    def opcao(self, letra: str, titulo: str, desenhar: Callable, veredito: str = "resolve", consequencias=(), prefixo: str = "Opção "):
        if veredito not in CORES_VEREDITO:
            raise DadoInvalido(f"veredito '{veredito}' desconhecido; use {sorted(CORES_VEREDITO)}")
        self.opcoes.append(_Opcao(f"{prefixo}{letra}", titulo, desenhar, veredito, list(consequencias)))
        return self

    def salvar(self, caminho: str, dpi: int = 150) -> str:
        if not self.opcoes:
            raise DadoInvalido("o quadro precisa de pelo menos uma opção")
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        nf, no = len(self.fontes), len(self.opcoes)
        larg = 7.0 * max(nf, no, 2)
        n_lin = max(sum(len(textwrap.wrap("- " + c, int(190 / no))) for c in o.consequencias) for o in self.opcoes)
        alt = 1.0 + (4.2 if nf else 0) + 4.4 + 0.2 * n_lin
        fig = plt.figure(figsize=(larg, alt), facecolor="white")
        topo = 1 - 0.9 / alt
        fig.text(0.01, 1 - 0.35 / alt, self.pergunta, fontsize=15, weight="bold", va="center")
        if self.local:
            fig.text(0.01, 1 - 0.72 / alt, self.local, fontsize=10, color="#444", va="center")
        y_op = topo
        if nf:
            h = 3.9 / alt
            for i, (leg, png) in enumerate(self.fontes):
                ax = fig.add_axes([0.01 + i / nf, topo - h, 1 / nf - 0.02, h - 0.3 / alt])
                ax.imshow(plt.imread(png)); ax.axis("off")
                ax.set_title(textwrap.fill(leg, int(95 / nf)), fontsize=10, loc="left")
            y_op = topo - h - 0.15 / alt
        h_des = 3.4 / alt
        for i, o in enumerate(self.opcoes):
            x0, w = 0.01 + i / no, 1 / no - 0.02
            cor = CORES_VEREDITO[o.veredito]
            fig.text(x0, y_op - 0.2 / alt, f"{o.letra}: {o.titulo}", fontsize=12, weight="bold", va="center")
            fig.text(x0 + w, y_op - 0.2 / alt, ROTULO_VEREDITO[o.veredito], fontsize=11, weight="bold", color=cor,
                     ha="right", va="center")
            ax = fig.add_axes([x0, y_op - 0.4 / alt - h_des, w, h_des])
            o.desenhar(ax)
            for s in ax.spines.values():
                s.set_edgecolor(cor); s.set_linewidth(2)
            ax.set_xticks([]); ax.set_yticks([])
            txt = "\n".join(textwrap.fill("- " + c, int(190 / no), subsequent_indent="  ") for c in o.consequencias)
            fig.text(x0, y_op - 0.55 / alt - h_des, txt, fontsize=9.5, va="top")
        fig.savefig(caminho, dpi=dpi, facecolor="white")
        plt.close(fig)
        return caminho
