# CLAUDE.md — nd_estruturas

Visão geral: README.md · Escopo: SPEC.md · Trabalho atual: TASKS.md · Decisões: DECISIONS.md

## Comandos

- Testes: `pytest -q`
- Testes de um módulo: `pytest tests/test_secoes.py -q`
- Lint / formatação: `ruff check . && ruff format .`
- Exemplo completo: `python -m nd_estruturas exemplos/portico_galpao.json`

Rode `pytest` antes de dar uma mudança por concluída. Se não houver teste cobrindo a mudança, diga isso em vez de afirmar que foi verificada.

## Convenções de engenharia (obrigatórias)

- Unidades internas: kN, m, kN·m, kPa (MPa só na leitura de fck/fyk, convertido na entrada).
- Sinal: compressão negativa, tração positiva.
- Entrada e saída do núcleo: objetos Python. JSON, DXF e PDF só nas bordas (raiz de composição e writers).
- Norma sempre citada com ano, por chave de registro: `"NBR6118:2023"`, `"NBR9062:2017"`, `"NBR6123:2023"`.
- Toda fórmula normativa leva comentário com a norma, o item e a equação. Ex.: `# NBR 6118:2023 item 17.3.2.1.1`.
- Objetos de valor validam a entrada: fck dentro da faixa da norma, d < h, aço CA-50/CA-60/CP-190 conhecido. Entrada inválida gera erro, nunca valor silencioso.
- Coeficientes (γc, γs, γf, ψ) vêm do registro de normas, nunca soltos no código.

## Verificação de cálculo

- Toda mudança de seção ou armadura só é dada como pronta depois da conferência cruzada zerada (letsara/pranchas/conferencia_cruzada.py, chamada no fim do gerar_tudo).

- Toda função de dimensionamento nova precisa de pelo menos um teste conferido à mão (exemplo de livro, apostila ou memória já entregue), com a fonte citada no teste.
- Resultado de MEF (OpenSeesPy) é conferido contra solução analítica simples ou contra o mef.py próprio antes de ser usado em memória de cálculo.
- Se um resultado parecer fora da ordem de grandeza (taxa de aço, flecha, reação), pare e aponte antes de seguir.

## Manter os documentos em dia

IMPORTANTE: depois de cada mudança relevante, atualize TASKS.md (mova o item para Feito) e adicione uma linha em CHANGELOG.md, em Não lançado.

- DECISIONS.md: nova entrada sempre que escolher entre alternativas reais.
- SPEC.md: só muda quando o escopo muda de verdade.

## Git

Não rode `git commit`, `git push` nem abra PR sem pedido explícito. Quando pedido: um assunto por commit, mensagem em português no imperativo ("Adiciona verificação de punção").

## Forma de trabalhar

- Pergunte antes de fazer algo fora da tarefa pedida. Ideias fora do escopo vão para TASKS.md, em Depois.
- Respostas curtas e diretas, em português. Sem preâmbulo e sem resumo no final.
- Sem emoji em código, documentos ou commits.

## Ao compactar a conversa

Manter: decisões e o motivo, estado da tarefa atual, dúvidas abertas. Descartar: conteúdo de arquivos já gravados e saídas de ferramenta já usadas.

## Armadilhas conhecidas

- OpenSeesPy guarda estado global: chame `ops.wipe()` no início de cada análise e nos testes.
- Ao reaproveitar lógica do HyperFrame, conferir os pontos listados em DECISIONS.md (DEC-005) antes de copiar.
