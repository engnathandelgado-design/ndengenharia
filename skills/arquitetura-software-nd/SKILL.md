---
name: "arquitetura-software-nd"
description: "Use ao escrever, organizar, revisar ou testar código Python do software estrutural da ND (nd_estruturas, OpenSeesPy, planilhas e ferramentas de cálculo)."
---

# Arquitetura de software ND (nd_estruturas)

Regras de organização de código para as ferramentas de cálculo da ND Engenharia. Adaptado para engenharia estrutural a partir do plugin python-clean-architecture (MKToronto, licença MIT, base nos cursos de Arjan Codes) — github.com/MKToronto/python-clean-architecture. Consulte as referências originais (references/ e references/patterns/) quando precisar de detalhe de um padrão.

Convenções fixas do nd_estruturas: kN, m, kN·m; compressão negativa; entrada e saída em JSON; normas sempre com ano.

## Camadas (dependência só de cima para baixo)

```
raiz de composição (cli / interface)  ->  operações (casos de uso)  ->  domínio + normas + motores
```

- **dominio.py** — objetos de valor imutáveis (`@dataclass(frozen=True)`) que validam no `__post_init__`: Concreto (fck 20–90 MPa), Aco (CA-25/50/60), SecaoRetangular (d < h), elementos e cargas. Erro de entrada vira `DadoInvalido` com mensagem em português que diz o que está errado e o limite.
- **analise.py** — `MotorAnalise` como `Protocol` com `analisar(modelo, cargas) -> Esforcos`. Implementações: analítica, OpenSeesPy (adapter, `import openseespy` dentro do método), mef.py próprio, stub de teste. Dicionário `MOTORES = {"analitico": ..., "opensees": ...}`.
- **normas.py** — registro por chave com ano: `REGISTRO_FLEXAO["NBR6118:2023"]`, `REGISTRO_VENTO["NBR6123:2023"]`. Norma nova = função nova registrada com decorador; nunca `if norma == ...` espalhado. A versão antiga continua registrada para reproduzir memórias antigas.
- **operacoes.py** — funções do caso de uso (dimensionar_viga, verificar_calice...). Recebem motor e chave da norma como parâmetro (injeção). Não leem arquivo, não imprimem, não desenham.
- **cli.py / interface** — único lugar que lê JSON, escolhe motor e norma concretos e grava saída (JSON, memória PDF, DXF). Interface final (planilha, web, desktop) entra só aqui.

## Sete princípios (ordem de prioridade)

1. Coesão: cada função faz uma coisa (calcular esforço ≠ dimensionar ≠ gerar memória).
2. Baixo acoplamento: passe só o que a função precisa.
3. Dependa de abstrações: `Protocol` e `Callable`, não classes concretas.
4. Composição em vez de herança: nada de mixins; hierarquias rasas.
5. Separe criação de uso: dicionário de mapeamento em vez de if/elif; uma raiz de composição.
6. Comece pelos dados: acerte as estruturas (seção, material, elemento, combinação) antes dos métodos.
7. Simples: DRY sem abstração precipitada; YAGNI — não criar FastAPI, eventos ou CQRS antes de precisar.

## Padrões úteis em cálculo estrutural

| Situação | Padrão |
|---|---|
| Vários métodos de cálculo para a mesma verificação (Blévot x biela-tirante) | Strategy (`Callable`) |
| Normas e versões | Registry por chave com ano |
| Envolver OpenSeesPy, Opsvis, ezdxf, bibliotecas externas | Adapter |
| Fluxo cargas -> combinações -> análise -> dimensionamento -> memória | Pipeline de funções puras |
| Entrada com unidade/limite (fck, cobrimento, classe de agressividade) | Value Object |
| Montar modelo com muitos itens opcionais (pórtico, galpão) | Builder retornando objeto congelado |
| Novos módulos (pré-moldado, protendido, metálica) sem mexer no núcleo | Plugin por registro |

## Testes (pytest) — obrigatório para cada verificação nova

- Um teste com **valor conferido à mão** (anotar no comentário os passos: Md, x, As).
- Um teste de **limite normativo** (x/d > limite, fck fora da faixa, As,mín governando).
- Um teste com **MotorStub** (esforço fixo) para testar dimensionamento sem solver.
- Um teste de **concordância entre motores** (OpenSees x analítico em caso isostático, rel=1e-6).
- Um teste **ponta a ponta** a partir do JSON de entrada.

Exemplo validado (out/2026): viga biapoiada 6 m, g=12, q=8 kN/m, 20×50, d=45 cm, C30, CA-50 -> Md=126 kN·m, x=10,61 cm, x/d=0,236, As=7,11 cm²; As,mín=1,50 cm² (0,15 %); OpenSees e analítico idênticos.

## Revisão de código (checklist)

Ao revisar código da ND, reportar por gravidade (Crítico / Importante / Sugestão), com arquivo e linha:
- Crítico: unidade misturada sem conversão explícita; norma sem ano; cálculo lendo arquivo ou imprimindo; resultado sem teste conferido à mão; erro silencioso (retorna None ou 0 em vez de avisar).
- Importante: if/elif por norma ou por tipo de peça; classe "deus" que modela, calcula e desenha; números mágicos sem referência ao item da norma; import de OpenSees no topo de módulo de domínio.
- Sugestão: nomes em português consistentes com a convenção ND; tipos anotados; funções longas divididas.

## Não fazer

- Não sacrificar clareza de engenharia por elegância de código: a memória de cálculo precisa ser auditável linha a linha.
- Não usar coeficiente ou limite normativo sem comentário com tabela/item.
- Não criar camada web, banco de dados ou async enquanto a interface final não estiver decidida.