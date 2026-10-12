---
name: "comparar-sistemas-estruturais"
description: "Use ao comparar dois ou mais sistemas estruturais (pré-moldado, moldado in loco, metálico, madeira, alvenaria estrutural) lado a lado em critérios definidos, com valores fornecidos pelo usuário/calculista."
---

# Comparar Sistemas Estruturais

O sistema estrutural é escolhido uma vez, cedo, e tudo o que a arquitetura faz depois vive dentro dele. Também é a decisão mais herdada do que tomada: o sistema de costume do escritório, do calculista, o da última obra. Esta skill torna a comparação explícita, nos critérios definidos, com os números de quem é responsável por eles.

## Escopo e limites — ler primeiro

**O que faz.** Recebe dois ou mais sistemas estruturais com os valores que o usuário e o calculista têm para cada um, recebe os critérios de decisão, monta uma única matriz e informa onde a comparação é realmente decidível e onde não é.

**O que não faz.**

- Não carrega **nenhum valor**. Nenhum vão, altura, modulação, custo, carbono ou TRRF. Todo número vem do calculista, do orçamentista ou de uma fonte nomeada pelo usuário.
- Não escolhe o sistema. O engenheiro estrutural responsável decide e assina (ART) as consequências. A skill compara o que cada opção faz com a obra, para a conversa começar por critérios e não por hábito.
- Não verifica elementos isolados (vigas, pilares, ligações) — isso é dimensionamento, feito em outras ferramentas.
- Não é comparação genérica de alternativas de projeto nem de sistemas de vedação/fechamento.

**O que é preciso antes de começar.** Os sistemas candidatos, nomeados. Os critérios de decisão. Para cada critério, um valor por sistema vindo do calculista ou orçamentista, ou um `desconhecido` explícito.

## Entradas necessárias

1. **Os sistemas**, nomeados com precisão. "Concreto" não é sistema; "laje lisa protendida moldada in loco" é. "Pré-moldado" não é sistema; "pórtico pré-moldado com laje alveolar protendida" é.
2. **Os critérios.** Perguntar se não forem dados. Os usuais: altura estrutural e efeito no pé-direito/piso a piso; vão e flexibilidade de malha; estratégia de proteção ao fogo e o que ela acrescenta; desempenho acústico entre pavimentos; estrutura aparente como acabamento; passagem de instalações (MEP) através ou abaixo da estrutura; velocidade de montagem e sensibilidade a chuva; demanda na fundação; adaptabilidade futura; custo; carbono incorporado; e se o mercado local executa bem o sistema (fábricas, montadoras, mão de obra).
3. **Um valor por sistema por critério**, cada um com sua fonte, ou a palavra `desconhecido`.

Nunca substituir um desconhecido por valor típico. Nunca copiar um valor de um sistema para outro porque "os vãos são parecidos".

## Fluxo de trabalho

### Passo 1 — Confirmar os sistemas

Nomear cada sistema por extenso e confirmar a edificação para a qual está sendo comparado: pavimentos, uso e área aproximada, como o usuário informar. Os mesmos dois sistemas se comparam de forma diferente em outra edificação; uma matriz sem edificação vinculada é matéria de revista.

### Passo 2 — Fixar os critérios antes de ver qualquer valor

Acordar a lista de critérios primeiro e registrá-la. Critérios escolhidos depois que os valores estão na mesa são critérios escolhidos para chegar a uma resposta.

Perguntar quais critérios são **limites** (precisam passar) e quais são **trade-offs** (quanto mais, melhor). Repetir de volta qual é qual.

### Passo 3 — Montar a matriz

| Critério | Limite ou trade-off | Sistema A | Sistema B | Fonte por célula | Comparável? |
|---|---|---|---|---|---|

A última coluna é o objetivo. Marcar a linha como **não comparável** quando um sistema tem número e outro tem `desconhecido`, quando os números vêm de tipos diferentes de fonte, ou quando um é número de projeto e o outro é regra prática. Não preencher lacuna para a linha parecer completa.

### Passo 4 — Relatório

- Quais sistemas reprovam em algum limite, e em qual critério.
- Qual lidera em cada trade-off, entre as linhas comparáveis.
- **A quantidade de linhas não comparáveis**, listadas por nome, informada antes de qualquer conclusão, porque é ela que define se existe conclusão.
- O que perguntar ao calculista ou orçamentista para tornar comparáveis as linhas que não são, redigido como as perguntas a enviar.

Se mais de duas ou três linhas não forem comparáveis, dizer claramente que a comparação ainda não é decidível e nomear o que falta, em vez de ranquear pelas linhas que por acaso estão preenchidas.

### Passo 5 — Salvar, se pedido

Perguntar se deve gravar a matriz e em qual formato (documento, planilha, Markdown ou CSV).

## Regras

- **Nunca fornecer um valor.** Nem vão, nem altura, nem custo, nem carbono, nem como marcador que pareça número.
- Fixar os critérios antes de os valores ficarem visíveis.
- Um `desconhecido` permanece `desconhecido` durante toda a execução.
- Informar a quantidade de linhas não comparáveis antes da conclusão, sempre.
- Nunca ranquear com dados parciais sem dizer que os dados são parciais.
- Dizer em toda execução que a decisão do sistema é do engenheiro estrutural responsável; esta matriz é o insumo da conversa, não a decisão.

## Antipadrões

- Preencher lacuna com vão ou altura típica para a tabela parecer pronta.
- Comparar o número de concreto desta obra com o número de metálica da obra anterior sem sinalizar.
- Acrescentar um critério depois de ver os valores.
- Ranquear sistemas com metade da matriz desconhecida.
- Tratar custo como único limite porque foi o primeiro a chegar.
- Recomendar um sistema. A skill relata; o engenheiro e a equipe decidem.