# Decisões — nd_estruturas

Registro das escolhas de arquitetura e de engenharia, para ninguém (nem o Claude) rediscutir sem motivo. A mais recente fica no topo.

Quando registrar: sempre que houver escolha entre alternativas viáveis. Correção de bug e detalhe reversível vão no commit ou no CHANGELOG.

---

## Modelo

```
## DEC-NNN — Título curto

**Data:** AAAA-MM-DD
**Situação:** proposta | aceita | substituída pela DEC-XXX

### Contexto
O que estava em jogo, o que já foi tentado ou descartado.

### Decisão
O que foi decidido, de forma específica.

### Consequências
O que fica mais fácil, o que fica mais difícil, o que se abriu mão.
```

---

## DEC-005 — Cuidados ao reaproveitar o HyperFrame

**Data:** 2026-10
**Situação:** aceita

### Contexto
O HyperFrame (MIT, TypeScript) tem recursos que a ND ainda não tem, mas a conferência encontrou pontos que não podem ser copiados como estão.

### Decisão
Antes de portar qualquer lógica, conferir: fundações dimensionadas só com G+Q (vento ignorado); blocos de 6 a 16 estacas com cortante só contra VRd2; flexo-compressão oblíqua sempre com 0,85·fcd; α1 = 0,6 até para pórtico puro (deveria ser 0,5); vento pela NBR 6123:1988 em vez da edição vigente de 2023; momentos do pilar não distribuídos entre as estacas.

### Consequências
Porte mais lento, mas sem herdar erro de norma.

## DEC-004 — Arquitetura limpa no núcleo de cálculo

**Data:** 2026-10
**Situação:** aceita

### Contexto
Revisão do plugin python-clean-architecture (base Arjan Codes) para decidir o que serve ao `nd_estruturas`.

### Decisão
Motor de análise como Protocol trocável (OpenSeesPy, mef.py ou stub); normas em registro por chave com ano; objetos de valor que validam a entrada; núcleo sem JSON, DXF ou PDF; uma única raiz de composição que lê o JSON; testes com stub e com conferência manual. FastAPI só se a interface final for web.

### Consequências
Dá para testar o dimensionamento sem rodar o OpenSeesPy e trocar de motor sem reescrever os módulos.

## DEC-003 — OpenSeesPy + Opsvis como motor de análise

**Data:** 2026-10
**Situação:** aceita

### Contexto
Era preciso um motor de elementos finitos confiável e gratuito, que gere figuras de qualidade de relatório.

### Decisão
OpenSeesPy com Opsvis (`ops_nd.py`) para análise de projeto. O `mef.py` próprio fica para aula, auditoria e pilar isolado.

### Consequências
Dependência externa, mas validada pela comunidade. O `mef.py` serve de segunda conferência.

## DEC-002 — Convenção única de unidades e sinais

**Data:** 2026-10
**Situação:** aceita

### Decisão
kN e m em todo o núcleo, compressão negativa, entrada e saída em JSON.

### Consequências
Fim da conversão espalhada entre planilhas. Toda leitura de dado externo converte na borda.

## DEC-001 — Adotar a estrutura padrão de documentos

**Data:** 2026-10-11
**Situação:** aceita

### Decisão
Usar o conjunto README, CLAUDE.md, SPEC, TASKS, ROADMAP, CHANGELOG e DECISIONS, adaptado ao padrão da ND.

### Consequências
Cada sessão com o Claude começa de uma base conhecida, sem reexplicar o projeto.
