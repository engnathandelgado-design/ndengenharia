---
name: "aprender-material-tecnico"
description: "Use quando o usuário pedir para 'aprender' um livro, apostila, norma ou PDF técnico de engenharia (aberto no navegador ou anexado) e transformar o conteúdo em skill reutilizável ou atualizar as skills existentes."
---

# Aprender material técnico e virar skill

O usuário é engenheiro civil/estrutural (fundações, concreto armado e protendido, pré-moldados) e professor. Quando ele diz "aprenda sobre X" apontando um material, o objetivo é que o conhecimento fique disponível nas próximas sessões. Ler não basta: o entregável é uma proposta de skill (propose_skills). Responder em português técnico.

## 1. Obter o conteúdo
1. Material aberto no navegador: tentar `get_page_text` na aba atual. Se falhar (PDF costuma falhar), para repositórios acadêmicos usar a extração com pdf.js da skill `ler-tese-academica` (leitura integral, página a página); senão `WebFetch` com a URL do PDF e um prompt pedindo extração detalhada: sumário, conceitos, fórmulas com símbolos, valores normativos, tabelas e exemplos numéricos.
2. Arquivo anexado: ler direto (Read / skill pdf).
3. Não contornar bloqueios de fetch com curl/python. Se nada funcionar, pedir o arquivo como anexo.
4. Avisar o usuário quando o conteúdo veio por resumo automático (WebFetch) e não pela leitura integral: o resumo pode errar fórmulas e valores.

## 2. Foco pedido pelo usuário
- Se ele pedir um recorte (ex.: "principalmente fundações"), fazer um segundo WebFetch dirigido: pedir todas as passagens sobre o tema, com trecho literal curto e capítulo/seção.
- Se o material tratar pouco do recorte, dizer isso claramente (citando o que existe) e completar com conhecimento próprio, separado do que veio do livro.

## 3. Revisar antes de escrever
- Conferir cada fórmula e valor normativo contra o próprio conhecimento; corrigir erros do resumo (ex.: fptk do CP-190 = 1900 MPa; fpyk = 0,90 fptk para RB).
- Identificar a edição da norma em que o livro se baseia (ex.: NBR 6118:2003) e atualizar para a vigente (ex.: NBR 6118:2023), citando item/tabela.
- Marcar com "(conferir)" todo valor crítico de que não haja certeza total ou que não tenha vindo do material.
- Não transcrever trechos longos (direitos autorais): resumir com as próprias palavras; no máximo uma citação curta.
- Método numérico/fórmula de projeto: implementar em Python no motor ND e validar contra solução fechada ou contra os números do material; registrar a tabela de validação (teste, resultado, referência) na skill.

## 4. Estrutura da skill proposta
- Frontmatter: `name` em kebab-case pelo assunto; `description` dizendo quando usar (assunto + tipo de tarefa: calcular, revisar, ensinar).
- Corpo:
  1. Fonte (autor, título, ano, norma base) e nível do público.
  2. Conceitos essenciais.
  3. Materiais/parâmetros com valores.
  4. Fórmulas com símbolos definidos e unidades.
  5. Tabelas normativas resumidas com item da norma.
  6. Verificações/estados limites.
  7. Exemplo numérico do material (resumido, com a lição que ensina).
  8. Roteiro de cálculo passo a passo.
  9. Armadilhas comuns.
- Se o recorte pedido for um tema à parte, propor uma skill complementar separada (ex.: `concreto-protendido` + `protensao-em-fundacoes`) referenciando a primeira.

## 5. Atualizar as skills existentes (padrão do Nathan)
- Skills da casa: `projetos-estruturais-concreto-armado-protendido` (teoria, critérios, Parte D = software ND), `mef-opensees-opsvis` (motor OpenSeesPy e código validado), `ler-tese-academica`, `aprender-material-tecnico`. Quando ele diz "continuando a skill…", "atualize as duas/as skills", **não criar skill nova**: propor `kind: "improvement"` com `target` = nome existente.
- Onde vai cada coisa: teoria/critérios/receita do trabalho → nova seção numerada na skill principal (Parte C) + linha em "Fontes incorporadas" + D.2 (módulo) + D.4 (backlog); código OpenSeesPy validado e testes → nova seção na `mef-opensees-opsvis` (tabela do item 2, limitações do item 9).
- Manter as referências cruzadas coerentes (número da seção, nomes dos testes T…).
- Antes de propor: ler de novo o SKILL.md atual de cada skill (cópia sincronizada em `~/.claude/skills/synced/*/<nome>/SKILL.md`) e montar o texto completo sobre ele — outras sessões podem ter atualizado a skill no meio do trabalho (o `propose_skills` recusa se a cópia mudou). Conferir com `cmp`/`diff` logo antes de enviar.
- Uma proposta substitui o SKILL.md inteiro: incluir tudo o que existe + o novo; nunca proposta parcial.

## 6. Entregar
- Chamar `propose_skills` (não escrever SKILL.md em disco, não mandar arquivo), com todas as skills afetadas na mesma chamada quando possível.
- Resposta curta: o que foi lido, o que a skill cobre/mudou (lista enxuta), avisos (resumo automático, norma desatualizada, itens "(conferir)") e oferta de aprofundar um capítulo ou incorporar material complementar (catálogo, norma, projeto).
- Se o usuário pedir "salve a skill": explicar que ele salva clicando em Salvar no cartão; só repropor se o cartão não aparecer.