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

## DEC-011 — Dentes Gerber verificados por MEF não linear 2D

**Data:** 2026-10-12
**Situação:** aceita

### Contexto
Dentes Gerber são regiões D: o dimensionamento por bielas e tirantes (NBR 9062 / PCI) é a base, mas Nathan pediu a conferência por MEF para não haver risco de colapso. O material de concreto PlaneStressUserMaterial não existe no OpenSeesPy disponível e o PlasticDamageConcretePlaneStress não convergiu após a fissuração.

### Decisão
Dimensionar pelo maior entre NBR 9062:2017 (7.3/7.4) e PCI 5.6, e verificar com `mef_dente.analisar`: ASDConcrete3D em estado plano (IMPL-EX), barras aderentes, cordoalhas com deformação inicial no comprimento de transferência, apoio em placa de aço sobre um pino, resistências de cálculo, ruptura por 10‰ no aço, 3,5‰ no concreto ou pico. O amolecimento à tração foi encurtado (10 εt0) porque, com a energia de fratura distribuída, o modelo superestimava a flexão em ~20%. Validado contra viga retangular (+6%); critério Vu ≥ 1,06 Vd.

### Consequências
Verificação independente do modelo de bielas, com mapa de fissuração para a memória. Custa alguns minutos por dente; o teste de validação fica fora da suíte rápida (ND_MEF_LENTO=1).

## DEC-010 — Perfis formados a frio pelo MRD com faixas finitas

**Data:** 2026-10-12
**Situação:** aceita

### Contexto
As terças Ue tinham sido escolhidas pela seção bruta. A NBR 14762:2010 permite largura efetiva (MLE) ou resistência direta (MRD, Anexo C); o MRD precisa das forças críticas local e distorcional.

### Decisão
MRD com Mcr/Ncr local e distorcional da curva de assinatura por faixas finitas (pycufsm, com a correção para numpy 2 aplicada em tempo de execução) e global pelas expressões analíticas da norma (conferidas contra a curva: 1%). Sem mínimo distorcional distinto na compressão, usa-se o valor da curva no comprimento distorcional da flexão.

### Consequências
Qualquer Ue/U fica verificável sem tabela de fabricante. Resultado prático: Ue 300×85×25×3,00 só atende com três linhas de correntes.

## DEC-009 — IFC como saída de modelo, sem Tekla

**Data:** 2026-10-12
**Situação:** aceita

### Contexto
Nathan não tem licença do Tekla Structures. Os servidores MCP do Tekla exigem o programa aberto no Windows. Clientes e fábricas trocam modelos em IFC.

### Decisão
Gerar e ler IFC4 com ifcopenshell (módulo `bim`, extra opcional `bim`). O modelo de peças é a fonte; IFC e página 3D (three.js, publicada como artefato) são writers nas bordas. Cada obra tem `exemplos/<obra>/modelo_bim.py`, regenerado ao fechar o projeto. Saídas fora do git.

### Consequências
Modelo abre no Tekla, Revit e visualizadores sem licença. Geometria é envelope do perfil (sem alvéolos, recortes e armadura); detalhamento de fábrica continua nas pranchas. Quando o `prefabricados` tiver o objeto peça, o ModeloBIM passa a ser gerado dele.

## DEC-008 — Modelo único de peças pré-moldadas (padrão "cast unit")

**Data:** 2026-10-12
**Situação:** aceita

### Contexto
Pranchas, listas, 3D e orçamento eram feitos em scripts separados por obra, com números redigitados. Os manuais do Tekla Structures 2026 mostram o fluxo do mercado: um modelo de peças alimenta análise, desenhos e relatórios.

### Decisão
Módulo `prefabricados`: peça de concretagem = principal + secundárias + recortes + insertos + armaduras; volume, pesos e CG calculados; marca por identidade (prefixo da convenção ND + número) e posição de armadura por identidade; modelo analítico gerado das peças (OpenSees pelo Protocol do motor); pranchas de peça e de montagem, listas e quantitativos gerados do modelo. Convenção de marcas e padrão de prancha em `skills/pranchas-tecnicas-nd` 6B.

### Consequências
Mais trabalho inicial por tipo de peça (pilar, viga, terça, tesoura, placa, laje). Em troca, mudança de projeto regenera tudo e prancha nunca diverge da memória. Primeiro teste real: obra Letsara (Marque Engenharia).

## DEC-007 — GitHub como fonte única; Streamlit como interface web

**Data:** 2026-10-12
**Situação:** aceita

### Contexto
O código existia no GitHub e em cópia na pasta do Drive, o que leva a versões divergentes. Era preciso rodar as ferramentas no PC e no celular. O Drive não executa código nem versiona; o GitHub versiona e alimenta serviços que rodam Python online.

### Decisão
Código e skills ficam só no repositório privado `ndengenharia`. Drive guarda materiais, entradas das obras e resultados. Interface web inicial em Streamlit (`streamlit_app.py` na raiz), publicada no Streamlit Community Cloud; no PC roda com `streamlit run`. As páginas só leem entrada e mostram resultado: o cálculo fica no pacote.

### Consequências
Uma versão só do código, atualizada por `git pull` no PC e automaticamente online. Streamlit atende uso interno e de poucas pessoas; se virar produto para clientes, reavaliar FastAPI. OpenSeesPy tem estado global: as páginas usam trava para uma análise por vez.

## DEC-006 — JAX FDM para form-finding, OpenSees para análise

**Data:** 2026-10-12
**Situação:** aceita

### Contexto
Cascas, arcos atirantados, gridshells e redes de cabos precisam de forma antes do dimensionamento. Alternativas: escrever um FDM próprio, usar relaxação dinâmica ou usar o JAX FDM (Princeton, MIT), que já traz form-finding inverso com gradiente exato. Testado em 12 exemplos oficiais e numa casca 20 × 20 m conferida contra a rede (empuxo +1,4 %).

### Decisão
Usar o JAX FDM só para achar a forma (módulo `formfinding`). Toda verificação continua no OpenSeesPy e no dimensionamento pela NBR 6118:2023. Resultado do FDM sempre conferido com conta de mão (H = M0/f no arco) ou com o modelo de cascas.

### Consequências
Dependência extra (jax, jax-fdm, compas). A solução inversa não é única e metas incompatíveis não dão erro: conferir perda final e cada meta. O módulo ainda chama o OpenSees direto; falta passar pelo Protocol do motor (DEC-004).

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
