# SPEC — nd_estruturas

_Atualizado em: 2026-10-11_

## Descrição em uma linha

Software estrutural próprio da ND Engenharia para análise e dimensionamento de estruturas de concreto armado, protendido e pré-moldado, com memória de cálculo rastreável à norma.

## Problema

Os cálculos da ND hoje estão espalhados em planilhas e scripts avulsos (consolos e dentes Gerber, blocos sobre estacas, taxa de aço metálica). Cada projeto refaz parte do trabalho, a conferência é manual e os softwares comerciais não cobrem bem pré-moldado (ligações, cálice, situações transitórias da NBR 9062).

## Objetivos (em ordem de prioridade)

- [ ] Núcleo de cálculo único, testado, com convenção única de unidades e sinais.
- [ ] Dimensionamento de seções, pilares e fundações pela NBR 6118:2023, com memória de cálculo gerada automaticamente.
- [ ] Módulos de pré-moldado (NBR 9062:2017) e protendido, que são o diferencial da ND.
- [ ] Análise de pórticos por MEF com OpenSeesPy, com figuras de tensão e deformação em qualidade de relatório.
- [ ] Reaproveitar as ferramentas existentes da ND por uma camada de adaptação (`nd_api.py`).

## Fora do objetivo

- Não é um software comercial para venda nesta fase.
- Não substitui a responsabilidade técnica do engenheiro: toda saída é revisada antes de ir para o cliente.
- Não terá modelador gráfico próprio na versão 1.

## Escopo da versão 1

**Dentro:**

- Módulos `secoes`, `porticos`, `pilares`, `fundacoes`, `protendido`, `prefabricados`, `memoria`.
- Entrada e saída em JSON.
- Motor de análise trocável: OpenSeesPy, mef.py próprio ou stub de teste.

**Fora (por enquanto):**

- Vento NBR 6123 automático, sísmica, incêndio, alvenaria estrutural.
- Exportação DXF de armação executiva.
- Interface web ou desktop.

## Restrições

- Python 3.11 ou superior, OpenSeesPy, Opsvis, pytest.
- Dados do projeto guardados no Google Drive para uso na web.
- Normas brasileiras vigentes, sempre com o ano.

## Critérios de sucesso

- Um bloco sobre estacas, um consolo e um pilar de projeto já entregue recalculados pelo software, com diferença menor que 2% em relação à memória original.
- Memória de cálculo gerada sem edição manual de fórmulas.
- Todos os testes passando antes de cada uso em projeto real.

## Questões em aberto

- Interface final: planilha, web ou desktop.
- Formato da memória de cálculo: PDF próprio (ReportLab) ou documento editável.
