---
name: "revisao-compatibilizacao-instalacoes"
description: "Revisa projetos de instalações (elétrica, hidrossanitária, pluvial, climatização, incêndio, gás) contra arquitetura e estrutura, com foco em pré-moldado. Use em compatibilização, furos em peças ou 'o duto passa?'."
---

# Revisão de Compatibilização de Instalações

Passa o conjunto de projetos de instalações por oito eixos de compatibilização, na ordem em que um projeto é de fato conferido, e registra o resultado num arquivo datado que diz o que foi comparado com o quê.

É a leitura do engenheiro de estruturas / compatibilizador sobre os desenhos de outras disciplinas. Encontra os pontos onde duas pranchas discordam sobre o mesmo espaço do edifício, e encontra lendo, não modelando.

Em obra pré-moldada a compatibilização pesa mais: furo, rebaixo, inserto ou tubo embutido que não estiver no projeto da peça antes da fabricação vira retrabalho, furo em campo ou peça condenada. Esta revisão existe principalmente para pegar isso a tempo.

## Gatilhos

"compatibilização", "compatibilizar projetos", "revisar instalações", "revisão de complementares", "o duto passa?", "cabe no forro?", "altura de entreforro", "shaft", "furo na viga", "furo na peça pré-moldada", "tubo embutido no pilar", "descida pluvial no pilar", "insertos para eletrocalha", "casa de máquinas cabe?", ou o envio de pranchas de instalações com pergunta de encaixe.

## Escopo e limites — ler primeiro

**O que faz.** Recebe os projetos de instalações junto com a arquitetura e a estrutura (incluindo projetos de fabricação das peças pré-moldadas, quando houver), compara nos oito eixos e escreve uma revisão que nomeia as duas pranchas por trás de cada conflito.

**O que não faz.**

- **Não conhece nenhuma dimensão.** Nenhuma altura de entreforro, dimensão de shaft, área de casa de máquinas, afastamento frente a quadro elétrico, velocidade em duto, vazão de renovação de ar, distância entre tomada e descarga de ar, diâmetro ou posição admissível de furo em peça. Tudo vem dos desenhos, do projetista responsável, da norma que ele indicar ou de você. Isso é a revisão, não uma lacuna.
- **Não faz detecção automática de interferências (clash).** Não há modelo BIM aqui. Lê desenhos: acha conflitos que um corte ou uma cota revelam e perde os que só um modelo mostraria. Dizer isso no relatório.
- Não dimensiona nem seleciona equipamentos, não calcula cargas térmicas, elétricas ou vazões, não verifica sistemas contra norma de desempenho.
- **Não é verificação de norma de incêndio ou de aprovação.** Compartimentação, shafts resistentes ao fogo, dampers corta-fogo, hidrantes, sprinklers e saídas de emergência são do projeto de PPCI e do Corpo de Bombeiros (CBMPR, CBMSC etc.). Exigências de prefeitura e de vigilância sanitária idem.
- **Não autoriza furo em peça estrutural.** Furo, rebaixo ou corte em viga, pilar, laje alveolar, painel ou peça protendida é decisão do projetista estrutural responsável (ART) e, em pré-moldado, também da fábrica. A revisão aponta e pergunta; não aprova.
- **Cada projetista responde pelo seu sistema.** A revisão levanta questões para os responsáveis técnicos; não responde por eles.

**O que é preciso antes de começar.** As pranchas de instalações, a arquitetura (plantas, cortes e planta de forro) na mesma revisão, a estrutura (formas, e em pré-moldado as pranchas de fabricação/montagem das peças), a fase do projeto e as folgas que o projeto ou os projetistas exigem.

## Fluxo de trabalho

### Passo 1. Preparar a pasta

Se `docs/revisoes-instalacoes/` não existir, criar junto com `docs/revisoes-instalacoes/indice.md` contendo só um título.

### Passo 2. Ancorar o conjunto

Antes de olhar qualquer coisa, registrar e repetir ao usuário:

- Obra, cliente, fase (estudo, anteprojeto, executivo, fabricação, as built) e área ou pavimento em revisão.
- Toda prancha em jogo, pelo número, com revisão (R00, R01…) e data.
- Quais disciplinas estão presentes e quais faltam (elétrica, SPDA, dados/CFTV, hidráulica, sanitário, pluvial, climatização/exaustão, incêndio/PPCI, gás, ar comprimido/vapor/utilidades industriais).
- Sistema estrutural: concreto moldado in loco, pré-moldado, metálico ou misto. Se pré-moldado, se as peças já foram fabricadas ou ainda não.
- Se arquitetura, estrutura e instalações estão na mesma revisão.

**A revisão das pranchas decide se o conflito é real.** Duas pranchas de revisões diferentes discordando não é achado, é base desatualizada. Dizer qual é o caso antes de anotar. Se as revisões divergem, a revisão inteira é provisória e o relatório diz isso no topo.

**Em pré-moldado, a situação de fabricação decide a gravidade.** O mesmo furo faltante é ajuste de prancha se a peça não foi fabricada, e é problema estrutural se já foi. Registrar o status de cada peça envolvida.

Pedir o que faltar. Não seguir com prancha suposta.

### Passo 3. Aplicar os oito eixos

Na ordem. Cada eixo gera um de três resultados: achado; aprovado, com a origem do limite nomeada; ou não verificado, porque o desenho ou o valor necessário não foi fornecido. Nunca um quarto.

**1. Shafts e prumadas.** Contar. Conferir se cada um sobe de piso a piso sem desviar para dentro de viga, consolo, escada ou caixa de elevador, e se termina em algum lugar: cobertura, veneziana, casa de máquinas, barrilete. Comparar o shaft da arquitetura com o que as instalações passam por ele. Shaft que leva quatro sistemas num pavimento e três no seguinte é o achado. Em pré-moldado: shaft atravessando laje alveolar ou pré-laje precisa estar na paginação das lajes (recorte, peça especial ou faixa moldada in loco).

**2. Forro e entreforro.** Tirar a altura do corte, não de nota genérica. Somar o que precisa caber no ponto mais crítico: estrutura (inclusive altura de viga pré-moldada, consolo, capa e mísulas), duto com isolamento e suportes, rede de sprinkler, luminárias, eletrocalhas e leitos, tubulações com caimento (esgoto e pluvial ganham altura ao longo do trecho) e as folgas entre eles. **Conferir o pior ponto, não o típico.** O corte típico é desenhado onde tudo cabe; o crítico costuma ser cruzamento de vigas, fim de trecho de esgoto ou sob viga de ponte rolante.

**3. Casas de máquinas e salas técnicas.** Área, pé-direito livre e porta. Depois o caminho: como o maior equipamento entra no primeiro dia e como sai quando for trocado. Sala alcançável só por corredor acabado com curva é achado mesmo se a sala for grande o bastante. Conferir também a carga do equipamento contra a estrutura (laje, viga, base) — sem calcular, só perguntar se o estrutural recebeu o peso. Em industrial: subestação, sala de compressores, caldeira, chillers, central de GLP.

**4. Distribuição horizontal e furos em estrutura.** Seguir as redes da origem até o fim do pavimento. Olhar cada ponto onde duto, tubo ou eletrocalha cruza viga, pilar, parede de concreto, painel de fechamento ou outra rede. Anotar onde o desenho mostra furo previsto e onde só mostra a instalação atravessando estrutura que não aparece na prancha de instalações.

Em pré-moldado, conferir também, peça a peça:
- Furo ou rebaixo atravessando viga, pilar ou painel: está na prancha de fabricação da peça? Se não está e a peça é protendida, sinalizar risco de cortar cordoalha — nunca sugerir furar em campo.
- Furos em laje alveolar: posição em relação aos alvéolos e às nervuras conforme o fabricante da laje (valor vem do fabricante, não desta skill).
- Insertos, chumbadores e trilhos para fixar eletrocalhas, suportes de tubulação, dutos e equipamentos: previstos na peça ou a fixar com chumbador pós-instalado? (pós-instalado → conferir com a skill `ancoragem-barras-pos-instaladas` e com o estrutural).
- Tubulação atravessando junta de dilatação ou ligação entre peças: há junta flexível prevista?
- Eletrodutos e caixas embutidos em painel ou pilar: estão na prancha da peça?

**5. Tomadas e descargas de ar, chaminés e exaustões.** Onde o edifício pega ar, onde solta ar e o que há perto de cada um. Conferir contra janelas, áreas de permanência, divisa do lote, tomadas de ar de vizinhos, e entre si. Em industrial: exaustão de fornos, câmaras frias, áreas de produção com exigência sanitária (SIF, vigilância sanitária). Perguntar qual afastamento o projeto adota antes de medir; descarga perto de tomada é achado contra esse afastamento, não contra número desta skill.

**6. Entradas de concessionárias e medição.** Onde entram energia, água, gás e esgoto/ligação de rede; onde ficam padrão de entrada, medidores, transformador/subestação, cavalete e hidrômetro, reservatórios, caixa de inspeção final. Os afastamentos e exigências vêm da concessionária (Copel, Celesc, Sanepar, Casan, Compagas, SCGás etc.), não desta skill nem de memória. Conferir se o padrão de entrada não conflita com pilar, muro pré-moldado, acesso de caminhão ou área de manobra.

**7. Acesso para manutenção.** Cada registro, válvula, damper, filtro, caixa VAV/evaporadora, caixa de passagem, caixa de inspeção, ralo e visita contra o tipo de forro ou piso acima/abaixo. Alçapão em forro de gesso precisa estar na planta de forro para existir. Se não está na planta de forro, não está no projeto. Em industrial: acesso a válvulas e equipamentos em altura (plataforma, escada marinheiro, passarela) e conflito com ponte rolante ou rota de empilhadeira.

**8. Coerência entre documentos.** Instalações contra arquitetura, contra planta de forro e contra estrutura (formas e, em pré-moldado, plano de montagem e pranchas de fabricação). Depois quadros/listas contra plantas: equipamento na lista que não está em planta, equipamento em planta que não está na lista, tag que não bate, quadro de cargas sem o circuito desenhado. Em pré-moldado, um item específico: **águas pluviais descendo dentro de pilar** — o tubo embutido, a posição de entrada na calha e a saída na base estão iguais no projeto de pluvial, no de fabricação do pilar e na fundação/bloco? Terminar com as revisões de todo o conjunto.

### Passo 4. Escrever a revisão

Nome do arquivo:

`docs/revisoes-instalacoes/<AAAA-MM-DD>-<slug>-instalacoes.md`

Regra do slug: minúsculas, sem acento, `[^a-z0-9-]` removido, máximo 40 caracteres, a partir de obra + pavimento ou área. Sufixo `-<n>` se data e slug já existirem.

Todo achado traz três coisas: as duas pranchas que discordam, o que cada uma mostra, e a cota ou folga contra a qual o conflito é medido, junto com a origem desse valor. Em pré-moldado, acrescentar a peça envolvida e se ela já foi fabricada. Achado sem valor por trás é observação, e vai numa lista separada com esse nome.

Classificar cada achado por quem precisa agir: projetista de instalações, projetista estrutural, fábrica de pré-moldados, arquitetura, obra.

O cabeçalho da revisão lista as pranchas com revisão e data. O rodapé diz quantos eixos foram conferidos e quantos ficaram não verificados.

Se o resultado for entregue ao cliente, gerar também uma versão legível (página/artefato ou documento) em padrão técnico, sem cara de texto genérico, identificada como ND Engenharia.

### Passo 5. Atualizar o índice

Acrescentar uma linha em `docs/revisoes-instalacoes/indice.md`:

`- <AAAA-MM-DD> — <obra>, <área> — <n> achados, <n> não verificados — <arquivo>`

Lista, não tabela, de propósito.

### Passo 6. Relatar

Informar os números: eixos conferidos, achados, observações sem valor por trás, eixos não verificados. Listar os não verificados com o que cada um precisa para fechar. Em pré-moldado, destacar à parte os achados que afetam peças ainda não fabricadas — são os que dá para resolver só mudando prancha. Fechar com:

> Toda dimensão nesta revisão veio de você ou dos desenhos. Eixos não verificados não foram conferidos, e leitura de desenho não encontra o que só um modelo mostraria. Furos e alterações em peças estruturais dependem de aprovação do projetista estrutural responsável.

## Regras

- **Nunca fornecer uma dimensão.** Nem altura de entreforro, nem folga, nem tamanho de sala, nem posição admissível de furo — nem de memória, nem de catálogo. Perguntar ou marcar o eixo como não verificado. Normas (NBR 5410, 5626, 8160, 10844, 16401, 6118, 9062, instruções do Corpo de Bombeiros etc.) podem ser citadas como onde o responsável deve conferir, nunca como fonte de um número tirado de memória.
- **Nomear as duas pranchas em todo achado.** Conflito que não se rastreia a dois documentos é opinião.
- **Conferir revisões antes de chamar de conflito.** Revisões diferentes significam base desatualizada até prova em contrário.
- **Eixo sem desenho é não verificado, não aprovado.** Silêncio sobre um eixo é lido como aprovação.
- **Nunca sugerir furo em campo em peça pré-moldada ou protendida.** Encaminhar ao estrutural e à fábrica.
- Encaminhar compartimentação, shafts corta-fogo, exaustão obrigatória e dampers ao projeto de PPCI e ao Corpo de Bombeiros, sem responder aqui.
- Relatório para cliente não antecipa diagnóstico de patologia; se a revisão levantar suspeita de dano em peça existente, isso vai para laudo, não para a revisão.

## Antipadrões

- Ler o corte típico e declarar o entreforro livre. O ponto crítico está em outro lugar, e é o único que importa.
- Tratar o entreforro como vazio porque a estrutura não está desenhada na prancha de instalações. Ausência num desenho de uma disciplina não é ausência no edifício.
- Citar folga "padrão" de memória. Folgas variam por concessionária, fabricante, Corpo de Bombeiros e equipamento especificado.
- Chamar de conflito duas pranchas em revisões diferentes.
- Relatar oito eixos quando três desenhos nunca foram enviados.
- Esquecer de checar se a peça pré-moldada já foi fabricada antes de classificar a gravidade.
- Esquecer o caimento: esgoto e pluvial ganham altura no fim do trecho.
- Dimensionar qualquer coisa. Quando a revisão propõe diâmetro de tubo ou seção de duto, deixou de ser revisão e virou parecer de projeto que ninguém pediu.

## Recursos

Esta skill não traz arquivos de referência, de propósito: todo valor que ela guardaria é específico da obra, do fabricante, da concessionária ou do Corpo de Bombeiros local.

Skills relacionadas:

- `projeto-estruturas-pre-moldadas` — quando o achado exige rever a peça (furo, inserto, rebaixo, consolo).
- `vigas-premoldadas-protendidas` — furos e aberturas em vigas protendidas.
- `paineis-fechamento-pre-moldados` — eletrodutos, caixas e aberturas em painéis.
- `ancoragem-barras-pos-instaladas` — fixações por chumbador pós-instalado.
- `consultoria-fabricas-pre-moldados` — levar os achados para o fluxo de projeto/fabricação da fábrica cliente.
- `pranchas-tecnicas-nd` — quando a revisão gerar prancha de compatibilização para entrega.