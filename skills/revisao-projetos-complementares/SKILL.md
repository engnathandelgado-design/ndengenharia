---
name: "revisao-projetos-complementares"
description: "Lê o projeto de qualquer consultor ou complementar (estrutural, elétrico, hidráulico, PPCI, climatização, paisagismo etc.) contra o arquitetônico para compatibilização, sem conferir cálculo."
---

# Revisão de Projetos Complementares

Uma obra tem vários projetistas — estrutural, elétrico, hidrossanitário, PPCI, climatização, cozinha industrial, acústica, segurança, paisagismo, drenagem/terraplenagem — e muitos desses projetos só são lidos contra o arquitetônico quando alguém encontra o conflito na obra.

As falhas são as mesmas em qualquer disciplina, por isso uma única skill cobre todas.

Acione quando o usuário disser: "revisa os complementares", "lê esse projeto do engenheiro", "isso bate com a arquitetura?", "compatibilização", "emitiram uma revisão, o que eu confiro?", ou quando entregar pranchas de qualquer projetista.

## Escopo e limites — ler primeiro

**O que esta skill faz.** Lê o projeto de qualquer consultor contra o arquitetônico, procurando as cinco coisas que dão errado em qualquer disciplina: a base de desenho, os eixos e níveis, as interferências, os serviços transferidos sem responsável, e as divergências diretas entre os dois projetos.

**O que esta skill não faz.**

- **Não confere cálculo nenhum.** Nem dimensão, nem carga, nem capacidade, nem vazão. Isso tem responsável técnico com ART, e questionar a engenharia a partir da compatibilização não serve para nada.
- **Não traz valores de referência.**
- Não substitui revisões mais profundas da disciplina. Se houver skill específica (por exemplo, `revisao-engenheiro-senior` para um olhar estrutural), use-a onde ela existir e esta onde não existir.
- Não monta o quadro de furos e passagens — isso é trabalho à parte.
- Não resolve os conflitos; só os registra. O acompanhamento até o fechamento fica num registro de compatibilização.
- Não substitui os projetistas nem o responsável técnico pelo projeto.

**O que é preciso antes de começar.** As pranchas do consultor e o projeto arquitetônico, com a revisão de cada um informada. A base arquitetônica que o consultor usou para desenhar. Qual deveria ser o escopo daquele consultor.

## Fluxo de trabalho

### Passo 1. Definir o que está sendo comparado

Pergunte, numa única mensagem:

> 1. Qual consultor/disciplina, e qual o escopo dele?
> 2. Qual a revisão de cada projeto, e **sobre qual base arquitetônica o consultor desenhou?**
> 3. Para que foi emitido: compatibilização, orçamento/concorrência, execução?
> 4. Quais restrições arquitetônicas importam aqui: pés-direitos livres, dimensões fixas, áreas que precisam ficar livres?
> 5. Existe modelo federado (BIM), ou são pranchas separadas?

**Sempre a pergunta 2 primeiro.** Um projeto desenhado sobre uma base superada vai divergir da arquitetura atual em todo lugar, e revisá-lo linha a linha antes de confirmar isso desperdiça a revisão e desrespeita o consultor. Se a base estiver desatualizada, pare e diga isso.

### Passo 2. Eixos, níveis e nomenclatura

Nada depois disso faz sentido se isto não bater:

- Designação e espaçamento dos eixos, nos dois projetos.
- Nomes dos níveis e suas cotas, nos dois projetos.
- **O que cada projeto entende por um nome de nível.** Topo de laje, piso acabado, topo da estrutura, topo do bloco: o mesmo nome significando coisas diferentes é a maior fonte de erro entre dois projetos.
- Contorno da edificação e indicação do norte.
- Nomes e números dos ambientes, se o consultor os usar.

### Passo 3. Achar o que está onde não pode

Em qualquer disciplina, o desenho põe coisas no espaço:

| Local | O que o consultor mostra | O que existe na arquitetura | Conflito |
|---|---|---|---|

Percorra: qualquer coisa num ambiente que precisa ficar livre, numa área de circulação ou afastamento exigido, atravessando parede ou laje com exigência de compartimentação/resistência ao fogo, num entreforro que já está cheio, numa parede que é envidraçada, num shaft, acima de ambiente com pé-direito fixo, e qualquer coisa fora da edificação que caia em rota de fuga, recuo ou área de paisagismo.

Informe os dois valores em todo conflito e não decida nenhum.

### Passo 4. Achar o que foi transferido, e para quem

Todo projeto transfere serviços, legitimamente, e a transferência precisa cair em alguém:

- Tudo marcado como "por terceiros", "pela contratada", "projeto do fornecedor", "a confirmar" ou "verificar no local".
- Tudo mostrado de forma esquemática que alguém vai ter que detalhar de verdade.
- Tudo que exige abertura, furo, suporte, base/plinto ou reforço que ainda não está em projeto nenhum.
- Tudo que exige acesso para manutenção que nenhum forro ou alçapão oferece hoje.

**Item transferido sem dono é um buraco que sobra para quem compatibiliza.** Liste cada um com quem deveria ser o responsável.

### Passo 5. Achar o que nenhum dos dois projetos mostra

É a lista mais valiosa e a mais difícil de fazer. Percorra o que o escopo desse consultor pressupõe e confira se cada item aparece em algum lugar: no projeto dele, no arquitetônico, ou em lugar nenhum.

Informe a terceira categoria item por item. Numa obra com vários projetistas, a maior parte do que se descobre no canteiro está nessa lista.

### Passo 6. Relatório

| # | Constatação | Consultor mostra | Arquitetônico mostra | Tipo |
|---|---|---|---|---|

Tipo é `base`, `eixo ou nível`, `conflito`, `transferido`, `lacuna` ou `duplicidade`.

Ordem: problemas de base e de nível primeiro, porque invalidam o resto; depois conflitos que afetam dimensão fixa; depois itens transferidos sem dono; depois lacunas.

Feche dizendo que nenhuma engenharia foi conferida e indicando o registro de compatibilização para acompanhar os itens até o fechamento.

### Passo 7. Salvar, se pedido

Pergunte se deve gerar o relatório como documento e onde.

## Regras

- **Confira a revisão da base antes de ler qualquer coisa.** Pare se estiver desatualizada.
- **Nunca confira nem comente o cálculo.**
- Defina o que cada projeto entende por cada nome de nível.
- Informe os dois valores em todo conflito e não decida nenhum.
- Liste todo item transferido com um responsável, ou aponte que não tem.
- Produza a lista do que nenhum dos dois projetos mostra.
- Onde existir skill mais profunda para a disciplina, indique-a.

## Erros a evitar

- Revisar linha a linha um projeto desenhado sobre base superada.
- Conferir se a engenharia está certa.
- Supor que dois projetos entendem a mesma coisa pelo mesmo nome de nível.
- Escolher qual projeto está correto.
- Tratar uma nota de transferência como problema de outro por padrão.
- Revisar só as disciplinas que têm skill própria.
- Listar conflitos e nunca produzir a lista de lacunas.