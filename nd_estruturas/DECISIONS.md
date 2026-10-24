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

## DEC-012 — Pilares pré-tracionados na cabeceira

**Data:** 2026-10-12
**Situação:** aceita

### Contexto
Pilares laterais e de fachada da Letsara: 40×60, 10 m em balanço, vento nos dois sentidos. Armados pediam 5 Ø20 por face (transversal) e 4 Ø25 por face (longitudinal). Nathan confirmou que as cabeceiras têm altura regulável, então cordoalhas a 250 mm do eixo nas duas faces são viáveis.

### Decisão
Pilares 40×60 pré-tracionados com 10 cordoalhas Ø12,7 (5 por face, a 250 mm do eixo no lado de 60), σp∞ ≈ 1000 MPa (4,1 MPa de compressão média), mais 4 Ø20 por face de 60 (8 Ø20 no total). Verificação pelo método geral com as cordoalhas como fibras com deformação inicial (`pilar_metodo_geral(cord=..., sig_pinf=...)`): λu = 1,22 na direção forte e 1,38 na fraca (lateral), 1,30 na fachada. Momento de fissuração sobe de 125 para ≈ 220 kN·m, contra 76 kN·m frequente de vento.

### Consequências
Pilar sem fissura em serviço e no içamento, menos aço passivo. A fábrica precisa regular a cabeceira a 525 mm (pilar deitado com 60 de altura). O detalhamento da armação do pilar sai na prancha própria.

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

## DEC-014 — Vigas do mezanino VM sem dente Gerber (2026-10-12)

O dente de 42,5 cm da I70 foi reprovado no MEF não linear (Vu < 1,06 Vd). Primeira versão adotou I70 sem dente (apoio direto); o cliente exige dentes Gerber nas vigas do mezanino, então as VM passam a I90 com dente 45×30 (MEF: Vu 436 ≥ 1,06 Vd, FS 1,14), 9 cord. Ø12,7, assentos CP-MEZ +2,45 e +5,85. Consequência: pé-direito livre sob a viga = nível − 1,15 m (2,00 m no +3,15) — avisado ao cliente.

## DEC-015 — Ligações de aço em kN e cm, como o Manual Gerdau (2026-10-13)

O módulo `ligacoes_aco.py` usa kN, cm e kN/cm² (exceção à DEC-002), porque todas as fórmulas, tabelas e exemplos do Manual Gerdau "Ligações para Estruturas de Aço" (NBR 8800:2024) estão nessas unidades e os testes reproduzem as tabelas sem conversão. A conversão para kN/m fica na borda (quem chama). Só ligações parafusadas (regra da ND: sem solda de campo). LCHE, LCHS, ligações rígidas, emendas de pilar e bases ficam para depois da leitura das págs. 79–340 do manual (arquivo de 11,3 MB acima do limite de download).

## DEC-016 — Perfis laminados: compressão por área efetiva e σr = 0,3·fy (2026-10-13)

`metalica_laminada.py` calcula NcRd com λ0 = √(Ag·fy/Ne) e NcRd = χ·Aef·fy/γa1, com larguras efetivas (c1/c2 da forma AISC 360-16 E7, σ = χ·fy), porque é o que reproduz a TCPA Gerdau (NBR 8800:2024) com desvio ≤ 0,05 % nas almas esbeltas; o método Q da 2008 fica como `metodo="2008"`. Diferente da TCPA, as mesas esbeltas também são reduzidas (HP 310×79: até 0,9 % a menos, a favor da segurança). σr padrão = 0,3·fy (Nota D.2.5-e da 2024, bate com a tabela de bitolas); as TVPA da Gerdau foram geradas com σr = 70 MPa, por isso `tvpa(..., sigma_r=70)` reproduz a tabela. Unidades: entrada/saída em kN, m, kN·m (DEC-002); propriedades de seção nas unidades do catálogo. Numeração exata de alguns itens da 2024 (Cb, interação, anexo de flambagem local) ainda a conferir no texto da norma.

## DEC-017 — Bases de pilares: modelo AISC DG1 calibrado nas tabelas Gerdau (2026-10-13)

O manual Gerdau (caps. 10–11) só traz σc,Rd e remete à NBR 8800:2024 (6.6.5, 6.7, base "tipo 2"), sem o texto da norma disponível. `bases_aco.py` usa o método do AISC Design Guide 1, que reproduz as tabelas: PBE com bloco retangular de tensões, m = (A − 0,95d)/2 sem tração e m = (A − d)/2 com chumbadores tracionados (desvio ≤ 1 % na maior parte, até 2,7 % com tração; com 0,95d em todo o domínio fica 5–17 % a favor da segurança); PBR com ℓ = máx(m, n, n') e λ = 1, t_ef = t − 0,5 mm (reproduz 173 de 273 linhas em 2 %). As outras 85 linhas PBR (placa pouco maior que o perfil) são governadas por um modo não identificado — o cálculo dá até 63 % acima — e por isso `pbr_NRd` limita NRd ao valor tabelado (`dados/pbr_gerdau.csv`) e avisa quando o detalhe não é tabelado. As emendas EP1/EP2 do manual são soldadas; pela regra da ND, a alternativa é `EmendaPilarParafusada` (talas).

## DEC-018 — Ligações viga-pilar: hipóteses das tabelas Gerdau no lugar do texto (2026-10-13)

As tabelas do Manual Gerdau (caps. 4–8) só são reproduzidas com hipóteses diferentes do texto das fórmulas: LMPA com corte do parafuso × 0,75 na interação tração-corte; LT com braço b1 (o texto, b1 − 0,5d, dá Td ~35% maior, contra a segurança); LCHS com lf = e − (dh + 0,2)/2. Adotadas as hipóteses das tabelas (desvio ≤ 1,9%). LMPA caso 1 com Ø3/4" fica +4,6% acima da tabela (pág. 125) sem hipótese identificada: Md reduzido 5% nesse caso, com aviso. Verificações do pilar suporte pela NBR 8800:2008 5.7 / AISC J10 (conferir 2024).

## DEC-019 — Letsara rev03: TS-01 sem dente e cobertura toda parafusada (2026-10-14)

Pedido do Nathan: tirar os dentes Gerber das I90 de cobertura, apoiar 30 cm sobre o pilar e sobre a viga central, rebaixar a cobertura para o pacote TP40 + lã 40 + zipada 0,65 + painéis solares com ≥ 15 cm de folga à platibanda, e nenhuma solda nas ligações. Escolhas: (1) apoio da TS-01 no degrau do recuo da cabeça do pilar (apoio útil 27,5 cm, NEO-4 + 2 PN-3 Ø25) e no topo da I130 (16,25 cm, NEO-3 + 2 PN-5 Ø20), com tubos passantes TB-3 Ø50,8×2,0 em y = ±100; as cordoalhas saem da faixa dos tubos (|x| ≤ 40 e x = ±155, linhas a 55 e 100 mm), o que mantém o CG em 72 mm e o ELS-D com 8 cordoalhas. (2) I110 não passa com a carga dos painéis nos vãos de 24 m → I130 (h 1,30), 26 cordoalhas em 4 linhas, 14 isoladas 2 m, fckj 40. (3) Terça Ue 300×2,65 (a 3,00 passava com folga; a 250 não passa): escora do eixo C dividida pelas 2 terças reais. (4) Ligações sem solda: ST-1P (chapa dobrada) em 2 esperas M16 concretadas, OR-X (cantoneira) em 1 espera M16, mão-francesa em clipe na espera horizontal M16 (a 100 mm do fundo, fora das cordoalhas); placas com trilho TR-1 nas faces laterais do pilar + bucha BR-1 + cantoneira CL-1, e consolo CA-1 em cantoneira L 152×102×19 com 2 M20 em luvas — capacidade do trilho e da bucha a conferir no catálogo do fornecedor. (5) VT do eixo A rebaixada para +6,25 (CP-VT abaixo do recuo +7,19): a vista E fica aberta só até +6,25.

## DEC-020 — Letsara rev04: reanálise pela NBR 9062:2017 (2026-10-16)

Pedido do Nathan: reanalisar e representar toda a obra com a skill da NBR 9062 e as regras novas da ND. Escolhas:
(1) Sem vigas de travamento VT (não há ponte rolante): estabilidade por pilares engastados + cobertura (TS-01, terças-escora, X) + diafragma do mezanino; γz 1,07–1,09 (5.1.2.12), ELU com 0,4·Eci·Ic nos pilares (Anexo A) e desaprumo H/400 (5.2.3).
(2) Limite de deslocamento horizontal pela Tab. 7 da 9062 (galpão H/400; mezanino H/500 e Hi/750) no lugar do H/1700 da NBR 6118: uso 0,40.
(3) Fechamento isostático mantido (CL-1 com furo oblongo): a variante com a fiada superior ligada mudou o deslocamento de 9,9 para 9,8 mm, sem ganho que justifique atrair esforço de temperatura.
(4) Pilares laterais 40×60: 20 Ø20 → 14 Ø20 (método geral com as barras reais: λu 1,62 → 1,23).
(5) VM do mezanino em meio vaso (as duas linhas são de borda): alma 25 + aba 15 × 20, 2º estágio e capa de obra, alças N9 Ø10 c/15, sem escoramento, continuidade por bainhas (tipologia 1), CT-1 parafusada contra a torção de montagem. A pedido do Nathan, com dente Gerber (fundo do consolo alinhado): varredura de 5 em 5 cm; o analítico aprova h 65, mas o MEF não linear reprova h 65 (Vu 305) e h 75 (440); adotado h 80 com dente 50 × 35 (MEF 484 kN ≥ 1,06 × 1,1 × 404). Altura total 106 cm (I90: 115).
(6) Consolos com tirante em alças horizontais (a2 da 7.3.3); NEO-2 200 × 300 fretado; NEO-1 da VB trocado por 100 × 100 (pressão mínima 7.2.1.6); junta vertical das placas 20 mm com tolerância de projeto ±5 mm; TS-01 com tolerância de comprimento ±10 mm.
(7) Classificação: pré-moldado (γc 1,4, γs 1,15, γn 1,1/1,2) até a fábrica comprovar 12.1.2; o cobrimento de 2 cm das placas depende dessa comprovação.

## DEC-021 — Letsara rev04: VB 15 × 60 com dente Gerber (2026-10-16)

Pedido do Nathan: VB das fachadas 1 e 9 com dente para ganhar altura livre embaixo, testando alturas menores. Topo fixo (apoio das terças do vão de oitão); consolo CP-VB escondido no recorte, com a largura da viga. Varredura b 15/20 × h 90 a 40 de 5 em 5 cm (`calc_vb_dente.py`): passa até h 50 (h 45 reprova na flecha L/250); a mais barata era 15 × 55, o Nathan escolheu 15 × 60 (flecha 24 de 38 mm). Dente 30 × 27, CP-VB 15 × 27 × 29 (1 alça Ø12,5), NEO-6 100 × 100 × 10. A sucção da faixa de borda (cp −1,6) levanta a viga mais leve no apoio (28 kN de cálculo): pino PN-6 Ø20 roscado A36 com porca no topo do dente. Ganho de altura livre: 66 cm. Verificação analítica (carga do dente 42 kN de cálculo, sem MEF). Os momentos da VB no modelo global foram extraídos: Mz horizontal ≤ 2,2 kN·m; o T de 12 kN·m é do acoplamento equalDOF, não da ligação real.

## DEC-022 — Letsara rev04: apoios horizontais e encaixes das vigas inclinadas (2026-10-16)

Pedido do Nathan: ajustar as vigas de cobertura inclinadas (3 %), os dentes e os apoios para dar o caimento com encaixes perfeitos. A NBR 9062:2017 7.2.1.6 pede aparelho de apoio horizontal e, em face inclinada, detalhe que o deixe horizontal; os assentos estavam inclinados 3 %. Escolhas:
(1) TS-01: cunha rebaixada no fundo das duas pontas (calço de aço em cunha na fôrma, 30 cm, 0 → 9 mm): a face de apoio fica horizontal na montagem; pontas e tubos já eram a prumo. Ponta baixa sempre no lado A, peça única.
(2) Tubos TB-3 e pinos a 7,75 cm das 4 pontas (antes 14 cm no pilar e 7,75 na I130): com a peça única nas duas meias águas os tubos da TS-01 do lado E não coincidiam com os pinos. NEO-4 recentrado a 12,5 cm da ponta; PN-3 a 10,25 cm da cabeça do pilar.
(3) Assentos horizontais: recuo dos pilares P1 (+7,195) e P2 (+8,369); topo da I130 e dos pilares P8A/P11 em dois níveis (+7,776 lado A, +7,788 lado E, degrau de 12 mm no eixo C), porque a ponta alta de uma TS-01 e a ponta baixa da outra ficam em níveis diferentes.
(4) VB: pontas, recortes e tubos a prumo e face de apoio do dente horizontal na montagem (inclinados 3 % na fôrma reta, `vb_geom.py`); CP-VB com topo horizontal e nível próprio em cada face (diferença de 2 cm entre as faces do mesmo pilar); VB-05 a VB-08 da fachada 9 espelhadas (ES-3 na face interna).
(5) BIM: `PerfilPoligono` + `ModeloBIM.extrusao_y` para modelar a elevação real (pontas a prumo, cunhas, dentes) em vez de prismas inclinados.

## DEC-023 — Letsara rev05: terças Z METSEC contínuas por transpasse, sem mão-francesa (2026-10-17)

Pedido do Nathan: terças sem mão-francesa; testar os perfis Z dos catálogos do Drive e do catálogo Purlins (voestalpine Meincol / METSEC). Estudo automático (`estudo_tercas_sem_mf.py`, NBR 14762 MRD): a mais leve biapoiada foi a C 342×2,30 METSEC (26,0 t); o Nathan escolheu a **Z 302×90/82×2,30 METSEC contínua por transpasse (METLAP)** (28,3 t; folga maior, encaixe das peças). Escolhas:
(1) Terça contínua nos 8 vãos por MEF de viga contínua (`nd_estruturas.viga_continua`) com 2·EI no transpasse; transpasse escolhido como o menor que atende: 450 mm para cada lado de cada TS-01 (uso 0,80, flecha 14,6 mm de 53,5); peças de 10,19 a 10,98 m (≤ 12 m).
(2) Sem mão-francesa: 4 M12 8.8 por apoio (2 colunas a ±60 nos furos METSEC E 55 / F 52) atravessando o ST-1P e as 2 almas; torção de apoio pelo binário das linhas (interação 0,24); 2 M12 em cada ponta do transpasse (uso 0,74). Saem ES-3, CMF-1 e MF-1 das TS-01 e das VB.
(3) Aba de 90 voltada para o lado A, sobre o ST-1P (aba vertical 290 < 312 da terça), para não mexer nas esperas ES-1; correntes de Z pela componente Ixy/Ix (AISI S100-16 D3.2), uso 0,83 com Ø10.
(4) Pendências com o fabricante: fu do aço (480 adotado), ângulo dos enrijecedores (45°), encaixe e furação no transpasse. A tabela do fabricante (por ensaio) pode dar espessuras menores; se usada, substitui a verificação da MC06.


## DEC-024 — Letsara rev06: contraventamento otimizado no modelo integrado (2026-10-17)

Pedido do Nathan: estudar o contraventamento num modelo único com toda a estrutura (pilares, TS-01, I130, VB, mezanino rígido, terças, correntes, tirantes, X), com o vento da NBR 6123 e as aberturas, usando a Mitsubishi como referência. `modelo_integrado_r05.py` + `nd_estruturas.vento_nbr6123`; 14 arranjos em 33 combinações ELU (`estudo_contraventamento_integrado.py`). O arranjo da rev05 (X nos vãos 2-3 e 7-8, painel de 2 terças) não muda nada em relação a não ter X. Escolhas (aprovadas pelo Nathan no croqui):
(1) X Ø16 nos 5 vãos do pavilhão (4-5 a 8-9), painéis de ≈ 45° com nós nas terças 0, 8 e 15 de cada meia água; pilares de 0,71 para 0,66 de uso, X com Td 31 kN (uso 0,70). Mais vãos rendem pouco: o anexo e a área aberta ficam travados pelo mezanino.
(2) As diagonais atravessam as terças intermediárias por furos oblongos 18 × 28 (marcas X1..X7, Y1..Y6); ES-2 só nos 3 nós de cada TS-01; no eixo 9 as orelhas vão na VB (ES-2V a ±200 da terça).
(3) ST-1V-R na VB do eixo 9: o vento do oitão entra pelas terças (até 49 kN ao longo da terça); 2 esperas M20 hef 400 (descem até a armadura inferior da VB 15 cm) + grampo U Ø10. ST-1P com grampo U Ø10 em cada ES-1 (escora até 47 kN nos beirais).
(4) Pilares dos portões da linha 4 com a cabeça a 2 cm do fundo da TS-01, ligados em y por 2 cantoneiras L 102 com furo oblongo vertical (Fd até 23 kN); 4 marcas PG-01 a PG-04; TS-01A (linha 4) com 6 insertos IT-P. A folha do portão fechado leva a diferença de pressão interna aos pilares.

## DEC-025 — Letsara rev06: 15 espaços de terça e calha no eixo A (2026-10-17)

Pedido do Nathan: 1ª terça com 40 cm livres no lado baixo (eixo A) para a calha e a última a 15 cm do pilar no lado alto. Com 16 espaços a terça do meio caía sobre os pilares B e D das fachadas (cabeça 40 × 30 acima da VB); número ímpar de espaços resolve. Adotado (escolha do Nathan): 15 espaços c/1,263 m, 16 terças por meia água (32 linhas, eram 34); no lado alto a última terça fica a 21,5 cm (mais perto bateria na cabeça do pilar C das fachadas). Terça governante 0,95 no modelo integrado. Calha de platibanda 300 × 150 em chapa galvanizada 1,25 a 0,5 %, 9 descidas Ø200 junto aos pilares P1, extravasores nas pontas e rufos RF-1 a RF-4 (`calc_calha.py`, NBR 10844:1989; I = 200 mm/h a confirmar com a cidade); a calha cheia carrega a 1ª terça (0,12 + 0,45 kN/m) no modelo. Prancha nova ND-LET-COB03.

## DEC-026 — Letsara rev06: placas fixadas pelo sistema Trejor com console soldado (2026-10-17)

Pedido do Nathan: fixação das placas de fechamento como nos sistemas Trejor (trejor.com/fixacao-de-paineis), estudados em IFC para a placa de 10 cm. Comparados console parafusado (TSA), soldado, concretado e faca: os três externos cabem nos 10 cm (nicho 60 de fundo, 40 de concreto atrás, sem cortar cordoalha); a faca exige placa entre pilares. Escolha do Nathan: **console soldado** — exceção à regra de ligações metálicas parafusadas, só para CS-1 × CE-1 (solda de campo, filete 6 E70XX). Também do Nathan: nicho encostado na ponta da placa (sem os 40 mm), cada placa só com o próprio peso e o vento (folga de 5 mm na junta macho-fêmea, sem empilhamento), o console resiste também ao vento (sai CL-1 + TR-1 + BR-1 e CA-1 + IB-1), e o pé de cada placa travado por 2 pinos de travamento (cartola Trejor) ao lado das alças de içamento. O MEF de casca mostrou: 1 pino no meio da junta deixa a placa no limite (37,5 / 37,6 kN·m, pico local 1,08) → 2 pinos (uso 0,90); pacotes suspensos sem pano até o baldrame viram mecanismo só com pinos entre placas → trava de pé PT-2 nos pilares em cada placa desses pacotes (escolha do Nathan). Ponta da placa calculada como dente Gerber por bielas e tirantes; aço do console por MEF de casca + NBR 8800; CE-1 com 4 pinos Ø16 × 150 + 2 grampos U Ø10 (borda a 80 mm governa). Medidas de pré-dimensionamento até chegar o catálogo 09 da Trejor (no e-mail de 05/02/2021, anexos não acessíveis pelo conector).

**Adendo rev06b (2026-10-17):** proposta de encaixe em U invertido descartada pelo Nathan (não monta). Mantida a solução com M16 frontal no fundo do nicho e dente atrás da aba. Como a parede de concreto de 40 mm atrás do fundo não resiste sozinha (10,9 < 13,8 kN), o NC-1 virou caixa fechada (fundo 12,5 vencendo o vão teto–base, base 9,5, aba 9,5, 4 grampos U Ø8 ancorados nos estribos N5/N6); M20 de nível trocado por M16 (braço do console até 58 mm), CE-1 de 12,5 para 16 mm e grampos N18 Ø10 nos pilares. Detalhamento executivo na ND-LET-PP01.

**Adendo rev06c (2026-10-18):** a pedido do Nathan, a parede lateral do nicho (sem esforço) passou a 3 mm. Na compatibilização peça a peça apareceram conflitos na rev06b (dente de 6 mm com engate de 4 mm, que sumia com o ajuste de nível; porca de nível sobre o dente; parafuso sem rosca engatada no fim do curso). Correção dentro da mesma solução: 2 abas 12,5 só nas laterais do nicho e 2 dentes 19 sobre as almas (o meio fica livre para o M16 de nível), M16 de nível com porca soldada na mesa + contraporca, prisioneiro M16 frontal com porca soldada atrás da chapa de ponta, almas com raiz 80 (janela de montagem de 20 mm), NC-1 em A572-50; tolerâncias adotadas: afastamento 25 ± 5 (desvio maior do pilar com calço entre CS-1 e CE-1), G 50 ± 10, posição ± 5. Grampos Ø6,3 a 31 mm da boca, dentro dos estribos N5/N6 (no lugar dos Ø8 a 18 mm, que ficavam fora do estribo).

## DEC-027 — Letsara: cobertura Kingspan zipada dupla com lã de rocha e acabamentos do fabricante (2026-10-18)

Contexto: o Nathan informou que a cobertura é o sistema Kingspan Isoeste "telha + lã de rocha + telha" exatamente como na p. 28 do manual da zipada (TP-40 STD 980 #0,65, perfil cartola #0,65 sobre cada terça, lã FSR 32, clipe fixo/deslizante, zipada 455 #0,50), e pediu os acabamentos (beirais, platibandas) modelados no IFC e detalhados para execução.
Decisão: cargas do pacote pelo sistema (g 0,137 kN/m² na sucção, contra 0,158 antes); todas as verificações refeitas (maior uso da cobertura 0,889, OR-X). Na verificação das fixações à sucção, a costura cartola × TP-40 a cada 2 ondas (padrão do manual) não passa nem na zona geral (uso 1,07; borda 1,80): adotada costura em todas as ondas (0,54 / 0,90). Acabamentos pelos detalhes do fabricante adaptados às placas: PG-1 na calha (p. 42), rufo de topo liso RF-3 no lado alto subindo sob o rufo chapéu (p. 40), rufo lateral RF-4 + RB-1/RB-2 nas linhas 1 e 9 (p. 34/37), rufo chapéu RF-1/RF-1C na platibanda (p. 46), costura transversal de 200 com Tacky Tape; fixação no concreto com PAR Tapper a cada 500 + PU. Prancha ND-LET-COB04.
Pendências: confirmar com a Kingspan os valores de arrancamento em chapa #0,65, a distribuição dos clipes e a dispensa de junta de dilatação na água de 39,6 m.

## DEC-028 — Letsara: ombreira metálica OM-1 em U na porta da vista I (2026-10-18)

Contexto: as placas I-13 / I-14 ao lado da porta da vista I não tinham apoio fora do plano na ponta do lado da porta. O Nathan pediu ombreiras metálicas só no vão da porta, em perfil U que abrace a ponta da placa para não perder vão livre; as demais placas ficam como estão (cada placa autoportante nos seus consoles).
Alternativas: (A) U rotulado na base e no topo, topo preso na placa de +2,50; (B) U engastado no baldrame com topo solto. A B foi descartada no cálculo: com o baldrame estreito os chumbadores ficam a ±80 mm do eixo da parede e cada um puxaria 32 kN (uso 2,1 no cone), além de ~10 kN·m de torção no baldrame.
Decisão: A. OM-1 = U dobrado 125 × 80 × 6,3 A36 (abas por fora das faces da placa, neoprene 6), base 12,5 × 200 × 180 com 2 chumbadores químicos M16 (rótula), topo pela chapa CL-1 12,5 × 100 × 360 em bucha BR-1 na placa I-15 (oblongo vertical). A I-15 recebe o topo das 2 ombreiras e passa a ter 12 cordoalhas (6 por face, fora do nicho), tipo PP-05P (uso 0,88; com 8 seria 1,22). Pontas das placas I-13 / I-14 a 20 mm do vão (vão livre 1,80 mantido). calc_ombreira.py, prancha ND-LET-PP05, IFC.
Registro: no estudo apareceu que as placas vizinhas às faixas de janela (H, I, J) recebem metade do vento das janelas se o caixilho for preso nelas; o Nathan decidiu manter essas placas como estão. A fixação das esquadrias fica com o fornecedor.


## DEC-029 — Letsara: costas do CS-1 com 130 mm de altura (2026-10-18)

Contexto: o Nathan observou que a chapa de 16 mm das costas só precisa existir na parte de cima, onde a carga da placa chega ao console.
Estudo (calc_fixacao_placas + mef_cs1, alturas de 120 a 200 e espessuras 12,5 e 16): todas passam; a solda de campo vai de 0,23 (200) a 0,47 (120).
Decisão: costas 16 × 120 × 130 (z −100 a +30): 20 mm abaixo da raiz das almas para o retorno da solda de oficina; solda de campo 2 × 130 (uso 0,42); espessura mantida em 16 (costas 0,33 no MEF; com 12,5 seria 0,52).

## DEC-030 — Letsara: espessura de cada chapa da fixação das placas pelo cálculo (2026-10-18)

Contexto: o Nathan pediu "só a chapa que precisa em cada lugar": as chapas laterais, de trás e de baixo do nicho poderiam ser finas; a de cima, que recebe o M16 de nível, grossa.
Estudo: MEF de casca do nicho apoiado no concreto por molas só de compressão, com os grampos como molas e sem contar os 40 mm de concreto atrás do fundo (`mef_nc1.py`), e MEF de casca do console (`mef_cs1.py`); von Mises nas faces, percentil 99 por chapa, ≤ fy/γa1. Soldas verificadas linha a linha: força por mm na borda da chapa junto a cada cordão (N⊥/2 + M⊥/t com os cisalhamentos), média em 10 mm (o pico do canto reentrante depende da malha), ≤ 0,6·fw·Aw/γw2 (NBR 8800:2008 6.2.5.1).
Decisão (menor chapa comercial que atende, usos do MEF):
- NC-1: teto 12,5 (0,76; 9,5 daria 1,07), abas 12,5 (0,96; 9,5 daria 1,56), fundo 9,5 (0,73; 8 daria 1,02 — o prisioneiro frontal apoia nele, não pode ser fino), base 3 (0,82), parede lateral 2 A36 (0,69). A parede não é "sem esforço": na sucção ela trava o canto do teto na boca (414 N/mm na linha de solda); com filete 2 dos dois lados passa (0,86 → 0,71 na verificação final). Soldas: teto × fundo 5 (0,45), base × fundo 3 (0,37), parede 2 dos dois lados (0,71, AWS D1.3), aba × teto CJP + 6, grampos 3 × 20.
- CS-1: costas 9,5 × 120 × 130 (0,88), almas 6,3 (0,74), mesa 16 (0,66 — fica em 16 pela geometria: com G mínimo a ponta do M16 × 45 de nível não pode passar da face de baixo da mesa; 12,5 falha na montagem), ponta 8 (0,86; 6,3 daria 1,25), dentes 19 (0,79). Soldas: alma × costas 5 (0,53), mesa × costas 8 (0,73; com 5 daria 1,16 e com 6, 0,97 — 8 para não depender da média de 10 mm), dentes × mesa 6 (0,84; era 8), ponta 5 (0,72). Solda de campo costas × CE-1 de 6 para 5 (mínimo AWS para 9,5; uso 0,50).
- CE-1: 16 → 12,5 (σ 133 ≤ 227 MPa; 9,5 não passa).
Economia: NC-1 3,92 → 3,05 kg (−349 kg nos 404), CS-1 4,50 → 2,44 kg (−812 kg), CE-1 15,8 → 12,3 kg (−935 kg nas 271) ≈ 2,1 t de aço.
Sem teste automatizado: os dois MEF levam cerca de 1 e 2,5 min; `calc_fixacao_placas.py` lê os JSON e recusa espessura diferente ou uso > 1.


## DEC-031 — Letsara: consoles da face C concretados com o pilar (CC-1) e tolerância ±12 (2026-10-19)

Contexto: o catálogo 09 da Trejor indica a posição de cada inserto na fôrma do pilar. O Nathan definiu a posição de concretagem: face C (cabeça/platibanda, onde ficam as placas) para cima, face A no fundo da fôrma, e propôs que os consoles da face C venham concretados com o pilar.
Problema: sem a solda de campo, a posição do console não se ajusta mais na obra; a folga do conjunto CS-1 × NC-1 (G 50 ± 10, x ± 5) não cobria fábrica + montagem.
Alternativas: (1) CC-1 concretado na face C com nicho mais largo e parafuso de nível mais longo; (2) manter tudo soldado na obra.
Decisão: (1), confirmada pelo Nathan. Tolerância global estatística (NBR 9062:2017 3.15): fábrica ±5 (5.2.2.5), montagem do pilar ±10 (5.2.2.6), placa ±5 → ±12 em x e na altura. Geometria nova: nicho NC-1 140 × 200 × 60 (grampos em 24–56 e 84–116), mesa do CS-1 104, almas a ±45, dentes 13 × 35 a 39–52, M16 × 50 de nível com G = 51 ± 12 (Y_NIV 46). A regra "ponta do nível acima da face de baixo da mesa" foi trocada pela folga do nível à chapa de ponta. Todas as folgas ≥ 0 (mín. 0,6 mm cabeça × abas); janela de montagem 27 mm.
MEF refeitos: NC-1 ≤ 0,80 (abas), soldas ≤ 0,70; CS-1 0,97 (ponta, sobrepressão), solda dentes × mesa 0,93; CE-1 interação 0,877.
CC-1 = CE-1 380 × 330 × 12,5 + CS-1 soldados na fábrica do pilar (mesma ancoragem verificada). Contagem: 110 CC-1 (2 consoles), 28 CC-1E e 36 CC-1D (1 console), 97 CE-1 lisas nas faces laterais B/D para solda na obra (120 CS-1 de obra, 284 de fábrica).
Hipóteses adotadas (sem pergunta ao Nathan, registrar): consolos da face A no caixão no fundo da fôrma; pilares genéricos PC/PM/PG mantêm CE-1 na face B com solda de campo e sem detalhe de posição na fôrma.
Pranchas: posição na fôrma em cada pilar com face C, vista CC-1 na PP04, tabelas PP01/PP00, quantitativos, MC07, páginas do cliente.

## DEC-032 — Letsara: revisão das peças protendidas, dos dentes Gerber e do padrão gráfico (2026-10-19)

Contexto: o Nathan pediu uma revisão de profissional experiente: console concretado CC-1 nos pilares, protensão (ato, ELS, ELU), detalhamento das vigas, ganchos, ancoragens, biela dos dentes Gerber e cotas/camadas/cores comparadas ao projeto padrão da usina (PCH Três Capões). A auditoria independente (contas refeitas sem o pacote) achou erros reais.
Achados e decisões:
- Pilares/CC-1: o console CS-1 não aparecia nas vistas nem no isométrico; 7 marcas tinham as CE-1 nas fiadas erradas (o fechamento pede 0, 2, 3, 5, 6, 7); alças AL-2 na face A ficariam no fundo da fôrma; faltava respiro na CE-1 horizontal. Corrigido: fiadas lidas das vistas do fechamento, CS-1 desenhado (face C, perfil e 3D), AL-2 na face C fora das chapas (cortadas rente após a montagem), 4 furos Ø20 de respiro.
- I130 (V405/V406): com 1400 MPa da prancha o ELS-D tracionava a base e o topo passava do limite no fim do isolamento no ato. Decisão do Nathan: 28 cordoalhas embaixo (7 por linha) + 2 na mesa superior, σpi 1453 MPa (143,4 kN) no cálculo e na prancha (fonte única: i110_r01.json), isolamento 2,0 m (linha 14) e 4,0 m (linha 18), fckj 45. Resultado: ato topo 3,39 ≤ 4,55 e base −27,9 ≥ −31,5; ELS-D −0,72; ELU 3227 ≤ 4301 (x/d 0,38); içamento por 3 laços por alça. V407 com 20 cordoalhas.
- Dente da I130: a reação real é 555 kN (TS-01 fora do centro), não 472. Fd = γn 1,1 × 555 = 610,5 kN, Hd 97,7. Suspensão 4 → 5 estribos Ø16; costura e nariz 3 → 4 Ø10; N8 fora do tubo TB-2. MEF não linear com a armação da prancha: Vu 832 kN ≥ 1,06 Fd (1,36). Tirante N5 desenhado em alças horizontais (U deitado), sem o gancho que saía pelo fundo do dente. A tabela de ferros contava as barras do dente de uma ponta só: corrigido para as duas.
- Dente da VM: o MEF anterior usava 12 cordoalhas (2 inexistentes) e outra armação, com γn 1,1. Refeito (mef_vm_dente.py) com a armação e as cordoalhas da prancha e γn 1,2 (parcela variável ≈ 50 %). Resultado: Fd 485 kN; com a carga no fim do maciço (1,0 m, a/h 1,25 como a I130) Vu 533 kN = 1,10 Fd (passa); com a carga a 1,3 m Vu 452 kN = 0,93 Fd e com C45 476 kN = 0,98 Fd — esmaga o nó do topo junto à face do dente, com a reação total na peça sem 2º estágio e capa. Armação não governa. Decisão do Nathan (20/10): aceitar a verificação com a carga a 1,0 m (opção A); pranchas sem mudança (DEC-033).
- Perdas: calculadas pela NBR 6118 9.6.3 (processo 9.6.3.4.2 com fases, U 70 %, t0 fictícia 5 dias) no lugar de 5–7 % / 20 % fixos; γp 1,1 no ato em todas as peças. Totais: I130 28,6 %, VM 23 %, placas 25 %, TS-01 19,8 %. Todas passam.
- TS-01: tração no topo no ato pede 6,1 cm²; acrescentados N9 2 Ø10 de 250 cm em cada ponta (6,48 cm²).
- Placas: lbpt e liberação gradual indicadas; combinação rara não é exigida em protensão limitada (registrada como informativa).
- Padrão gráfico (prancha_nd.py), pelo projeto da usina: cotas marrons com seta e texto 1,8 mm, cadeias próximas (parcial perto, total a 4,5 mm), sem cotas acumuladas; armadura passiva verde fina, protensão magenta; concreto preto mais grosso que armadura; chapas com contorno preto e hachura cinza fina (a hachura preta era bug do ezdxf, cor 7); textos 1,6–2,0 mm.
- VB: modelo global com a VB presa nas 2 pontas: ±69 kN de força normal na VB, terças e ST-1P passam (0,96 / 0,98). Com a VB solta numa ponta: terça 1,07 e esperas da ST-1P 1,41 — não passam. A VB precisa ser presa nas duas pontas; o detalhe da ligação (±69 kN) fica para o Nathan escolher.
Memória nova ND-LET-MC08 (memoria_protendidas.py) com todas as verificações; MC05 rev06 atualizada.

## DEC-033 — Letsara: decisões sobre folga dos PG, dente da VM e ligação da VB (2026-10-20)

Contexto: três pontos da revisão de obra mostrados ao Nathan em imagem (como está × proposta).

- Folga dos pilares PG sob a TS-01: proposta de baixar 3 cm a cabeça dos 4 PG (folga 5 cm, oblongo 18×70). Decisão do Nathan: não. Mantidos folga 2 cm e oblongo 18×50. Registro: a descida calculada da TS-01 depois da montagem (≈ 30 mm no PG-01/PG-03 e ≈ 20 mm no PG-02/PG-04) é maior que a folga e o curso do oblongo (±16 mm).
- Dente da VM: decisão do Nathan, opção A — verificação com a carga a 1,0 m (Vu 533 kN = 1,10 Fd). Nada muda nas pranchas.
- Ligação da VB: decisão do Nathan, seguir com o detalhe atual (PN-6 grauteado numa ponta, outra ponta solta). Registro (refeito em 21/10, estudo_vb_solta.json, opção vb_solta do modelo_integrado_r05): com uma ponta da VB solta em x a terça passa (0,97 ponta alta / 0,91 ponta baixa; 0,95 presa) e só 1 ST-1P não passa — esperas do ST-1P da 1ª terça (beiral) no eixo 2: 1,06 (0,98 presa), cortante 49 kN em 2 M16. Os valores 1,07 / 1,41 citados antes não se confirmaram. Reforço proposto: 4 esperas nesse ST-1P (barras 0,26; falta conferir o concreto da TS-01 na borda) — aguardando o Nathan. Estudo de mais X (estudo_vb_solta_x.json, VB solta): X também nos vãos 1-2, 2-3 ou nos dois → terça 0,98 e esperas 1,04 (sem ganho): a terça é governada pela flexão vertical com a mesa travada pela telha (≈ 80 % do uso, modo distorcional), o N de escora é ≈ 14 %, e as correntes só governam o caso de sucção, que não é o crítico.

## DEC-034 — Letsara: placas de fechamento com cordoalhas Ø9,5 (2026-10-21)

Contexto: o Nathan propôs dimensionar a placa 125 × 10 só pelo peso próprio (10 fios Ø5/Ø6 CP-175, como já executado com vão de 3 m entre pilares) e descartou mudar o vão entre pilares. Mostrado o modelo: placa biapoiada fora do plano entre consoles (vão 10,075 m), vento q0 0,874 × cp 1,6 → Md 31,1 kN·m; 10 Ø6 resiste 14,9 (uso 2,09). Peso próprio no plano não governa (±1,5 MPa).
Decisão do Nathan: cordoalhas Ø9,5. Adotado 14 Ø9,5 CP-190 RB (7 por face, z = 95/156/469/625/781/1094/1155 mm, simétricas nas 2 faces e na altura, eixo a 2,48 cm das faces, cobrimento 2,0 — decisão de 13/10), 77,7 kN por cordoalha no macaco. 12 Ø9,5 passava à mão (0,94) mas dava 1,02 no MEF de casca da parede (pinos PT-1 entre fiadas): 14 → 0,89 no MEF, 0,82 à mão. PP-05P (I-15, sobre a porta): 18 Ø9,5 (9 por face), uso 0,98.
Manuseio: concretar deitada, desformar com 4 pontos e balancim, bascular e ESTOCAR EM PÉ (deitada em 2 calços a placa flecha ~27 mm com a fluência e fica empenada).
Nesta obra (projeto da fábrica) as imagens não levam a marca "projeto da ND Engenharia".

## DEC-035 — Letsara: placa de fechamento só pelo peso próprio, fios Ø6, pino PT-1 guia (2026-10-21)

Decisão do Nathan (responsável técnico): as placas 125 × 10 são dimensionadas só pelo peso próprio — o vento NÃO é considerado na flexão da placa (registrado: pelo modelo biapoiado entre consoles com o vento da NBR 6123 o uso seria 2,17). Cada placa é independente nos seus 2 consoles (folga 5 mm na altura, junta 20 mm no comprimento mantida); o pino PT-1 vira só guia de montagem (M16 só na placa de baixo, não transmite esforço). Cabos de preferência fios Ø6, depois Ø5, Ø9,5 só se não houver jeito.
Adotado: 10 fios Ø6 CP-175 RB (5 por face, z = 156/469/625/781/1094 mm, simétricos, eixo a 2,3 cm), σpi 1295 MPa (36,6 kN/fio), perdas 19 % (relaxação com fptk 1750 — parâmetro novo fptk em perdas_pretracao), lbpt de fio entalhado (ηp1 1,4) 52 cm.
Verificações (σ em MPa, tração +): desforma deitada por 4 pontos numa face com balancim −1,21 (sem balancim +0,07, no limite 1,20), içamento em pé −2,17, estocagem em pé −2,25, montada nos consoles (descompressão sob peso próprio) −0,85. PP-05P (I-15) passa a ser igual à típica. Fixação (CS-1, NC-1, CE-1, PT-2) mantida como calculada (com vento, a favor da segurança).
Mínimo com fios Ø5: 10 fios (5 por face), com a descompressão no limite (0,00) — por isso Ø6.

## DEC-036 — Letsara: ST-1P4 nos beirais do eixo 2 e marca TS-01B (2026-10-21)

Decisão do Nathan (21/10, emissão executiva): aprovado o ST-1P4 na 1ª terça do beiral do eixo 2 (lado A e lado E), onde a VB grauteada numa ponta só (DEC-033) leva a escora da terça ao suporte: com o ST-1P de 2 esperas o modelo integrado dá 1,06 (Fy 48,9 kN, Fx 10,3 kN, Rz,up 24,7 kN).
- ST-1P4: mesma chapa dobrada 9,5 × 220 A36 do ST-1P, aba horizontal de 200 (em vez de 150) com 4 oblongos 18 × 40, sobre 4 esperas ES-1 M16 (hef 150, gancho + grampo U Ø10 em cada uma) a 7,5 e 15,5 cm antes do eixo da terça, y = ±6 cm. 8,0 kg. 2 peças na obra (ST-1P passa a 222).
- TS-01B (2 peças da linha 2): TS-01 + 2 ES-1 extras na 1ª e na última terça (peça simétrica, para não depender do sentido de montagem: 8 ES-1 extras, 4 usadas). Marcas: TS-01 = 10, TS-01A = 2 (linha 4, IT-P), TS-01B = 2.
- Verificação do grupo (ACI 318-19 cap. 17, C50, concreto fissurado, nas pontas maciças 40 × 90 da TS-01, borda lateral 14 cm, borda à ponta 31,5 cm): tração φNn 84,4 kN (cone) para Nu 30,8 kN; cortante ao longo da terça φVn 141 kN (aço; ruptura de borda 35,5 kN sem grampo → os 4 grampos U Ø10 são a armadura de ancoragem, 17.5.2.1) para Vu 48,9 kN; ao longo da viga φVn 33,6 kN (borda) para 10,3 kN; interação 0,59 (era 0,94 com 2 esperas pelo mesmo método). Esperas (barras) 0,26 no modelo integrado.
- Pranchas: ND-LET-TS01-1 (planta superior, insertos e nota da TS-01B), TS01-3 (vista do ST-1P4 e lista), COB01 (lista e nota). No 3D (modelo_bim.py) as esperas do ST-1P4 estão a −0,150/−0,070 da alma; nas pranchas ficaram a 75 e 155 mm antes do eixo da terça (as 2 do ST-1P comum + 2 a 80 mm) — alinhar o 3D.

## DEC-037 — Esquadrias sem vento; placa I-15 igual à típica; emissão executiva (21/10/2026)
Decisão do Nathan: não considerar o vento nas esquadrias. A placa I-15 (sobre a porta, PP-05P) fica igual à típica (10 fios Ø6, só peso próprio, DEC-035); as ombreiras OM-1 ficam como peça construtiva de enquadramento da esquadria, sem levar vento à placa (o uso 3,2 da I-15 com o vento da esquadria fica só registrado, não governa).
Emissão: jogo completo sai como EXECUTIVO — LIBERADO PARA PRODUÇÃO E MONTAGEM (prancha_nd.EMISSAO acrescenta a revisão nova em cada folha e troca a nota "para aprovação, não executar"). Fôrma e armação na mesma folha por marca; folhas AR-PIL-01..06, AR-VIG-01..05 e TS01-2 obsoletas. Furo de içamento FI-1 no eixo sem saliência acima (PC-03 → A–C; PL-02/03/04/06/07/08 e PM-01 → B–D); PF-01..06 sem eixo livre: A–C com balancim e afastadores (nota na folha).

## DEC-038 — Letsara: CT-1 antigiro da VM sem trilho e sem solda, CT-1P no topo nos PL (2026-10-21) — SUBSTITUÍDA PELA DEC-039

Substituída no mesmo dia pela DEC-039 (CT-1/CT-1P e buchas BR-3/BR-4/BR-5 removidas). Mantida como registro.

Decisão do coordenador / regra do Nathan (metálica só parafusada, nada de solda): a cantoneira antigiro da VM meio vaso deixa o trilho TR-2 (IP-02) embutido no pilar e passa a fixar em buchas rosqueadas embutidas, com furos oblongos para ajuste. Força: H_CT1,d = 28,0 kN no topo da VM (torção de montagem, vm_meio_vaso.json VM-02, T_F1 15,0 kN·m, z 0,695; NBR 9062:2017 11.1 e 7.2.2.2); para fora 2,4 kN. Cálculo: `exemplos/letsara/calc_ct1.py` → ct1.json (ACI 318-19 cap. 17 via nd_estruturas.ancoragem, C40 fissurado; aço NBR 8800:2024).
- Bucha escolhida: BR-3 = inserto rosqueado M16 (bucha de aço de catálogo, tipo BR/TSA) hef 150 com barra transversal Ø10, 2 por consolo CP-MEZ. Na VM: BR-4 M20 hef 200 + barra Ø10 (lateral, CT-1) e BR-5 M20 hef 150 vertical + grampo U Ø10 (topo, CT-1P).
- CT-1 (24 un., pilares PF, PC, PM — pilar 10 cm mais largo que a VM do lado externo): L 152×102×15,9 A36 laminada inteira, L = 150. Braço reduzido aproximando o furo do canto: M20 na BR-4 a 5 cm da ponta da VM (8 cm da face do pilar), 7,5 abaixo do topo, oblongo 22×52 horizontal (junta 3 ± 1,5). Aba 152 em balanço do furo à raiz: braço 66,1 mm (junta + tolerância + 50 − t − r), M = 1,85 kN·m, Z = 9480 mm³, MRd = 2,15 kN·m, uso 0,859. Menor espessura comercial que passa: com 12,5 o uso seria 1,46; a peça antiga (12,5, furo a 14 cm) dava 2,94. Aba 102 na face do CP-MEZ: 2 BR-3 a 5 cm da aresta externa (gabarito 50 do dorso, arruela livre da raiz 6,1 mm), 4 e 11 cm abaixo do topo da VM (s 7), oblongos 18×36 verticais (±9; borda 22 mm = mínimo da Tabela 14 da NBR 8800). Interação tração × corte do grupo 0,515; BR-4 à tração 0,818 (cone, φNn 34,2 kN); M16 ao corte 0,376, M20 à tração 0,201.
- CT-1P (8 un., pilares PL): a mesma cantoneira laminada L 152×102×15,9 L = 150 no TOPO da VM, sobre a alma (dentro da largura da viga, embutida no 2º estágio): aba 152 horizontal com 1 M20 vertical na BR-5 a 7 cm da ponta (φVn 49,5 kN com o grampo como armadura de ancoragem, 12,8 sem; uso 0,566); aba 102 vertical na face do CP-MEZ acima da VM com 2 BR-3 lado a lado (s 10, 7,5 cm da aresta externa, eixo 4,5 acima da aba horizontal): concreto 0,515, aço da bucha 0,801 (22,1 kN por M16 com o binário no plano da aba), M16 0,594, M20 ao corte 0,482. Uso máximo do conjunto 0,859. A CT-1P lateral com 2 BR-3 na face lateral do PL (proposta do coordenador) foi descartada pela checagem de colisão: bate na descida DE-1 Ø200 no P1 da linha 2 e o PL não tem face lateral além da VM.
- Colisão (geométrica, caixas envolventes no modelo_bim, `colisao_ct1.py` → colisao_ct1.json, 32 pontas de VM): CT-1 lateral nos PL — aba 102 sem pilar atrás em 8 de 8 pontas; CT-1P lateral — 2 colisões (DE-1); CT-1P no topo — 0; CT-1 nos PF/PC/PM — 0 (na linha 1 o PF passa exatamente 10 cm da face da VM e a aba 102 sobra 2 mm, livre das placas a −0,325). Com L = 200 a CT-1 bate (9,5 mm) na trava PT-2 das placas na mesma face do PF (16,5 cm abaixo do topo da VM) — por isso L = 150 e BR-3 a s 7. Peças adotadas no 3D: 160 peças (CT-1, CT-1P, BR-3/4/5), 0 colisões.
- Por que não apareceu antes: o cálculo antigo só verificou os 2 M16 ao corte (força direta, sem o braço do furo até a raiz da aba — flexão da aba nunca conferida, uso real 2,94) e o trilho TR-2 nunca foi conferido contra a largura do PL (40 = largura da VM: faces coplanares, a aba 102 lateral não tem onde apoiar). A conferência 3D era só visual.
- Pranchas: VM01 (det. 2 CT-1 em planta, det. 3 CT-1P, insertos BR-4/BR-5 e CT-1/CT-1P por marca, nota de torção), pilares PL/PF (pilares_familia.py) e PC/PM (pilar_generico.py): BR-3 na tabela de insertos, nas vistas das faces (com chamada) e no isométrico; CT04 (det. 4 e nota), CT02 (nota), quantitativos (CT-1 24, CT-1P 8, BR-4 24, BR-5 8; BR-3 pelas folhas dos pilares), modelo_bim.py (3D/IFC). MON01–03 não mexidas.

## DEC-039 — Letsara: giro de montagem da VM travado pela ponta concretada; sem CT-1 (2026-10-21)

Decisão do Nathan (21/10, 19:49): "essa torção não existe porque, para montar as lajes, são concretados os extremos de cada lado da viga". Antes de montar as lajes concretam-se as juntas VM × pilar das duas pontas; é essa ligação que segura o giro na montagem. Substitui a DEC-038: saem a CT-1, a CT-1P e as buchas BR-3/BR-4/BR-5 de todas as folhas, das listas, dos quantitativos e do 3D (calc_ct1.py, ct1.json, colisao_ct1.py marcados OBSOLETO).
- Binário no apoio (calc_vm_meio_vaso.py, torcao_montagem): neoprene NEO-5 embaixo + junta concretada no topo, z = 0,695 m. T_F1 = 15,0 kN·m (R = 145,8 kN; sem travamento a resultante sai do núcleo b/6 do neoprene), Hd = 1,3 T/z = 28,0 kN; peça sozinha gira para fora com 1,3 kN·m (menor).
- Junta: 3 cm, largura da ponta maciça 40 cm, do recorte do dente ao topo (h 50 cm), graute ou concreto fck ≥ 30 MPa, fôrma lateral nas 2 faces, ponta da VM e face do pilar ásperas (≥ 5 mm a cada 30 mm). A força H é horizontal e transversal à viga, no PLANO da junta: não há compressão de contato contra o pilar (bloco parcialmente carregado não se aplica) nem tração atravessando a junta em nenhum dos dois sentidos do giro — a junta trabalha ao cisalhamento na interface (NBR 9062:2017 6.3.3, Tab. 10 com ρ < 0,2 %: βs = 0, βc = 0,3). Área resistente = metade superior da junta, 0,10 m²: τsd = 0,280 MPa; τRd (fck 30) = 0,434 MPa, uso 0,64. Não precisa de espera; a N11 dos apoios internos atravessa a junta depois, com o 2º estágio, para a negativa.
- Liberação das lajes: fcj mínimo calculado 16 MPa → adotado fcj ≥ 20 MPa (τRd 0,332, uso 0,84), por corpo de prova da obra.
- Embaixo, neoprene à distorção: Hk 21,5 kN, tg γ = 0,48 ≤ 0,7 (NBR 9062:2017 7.2.1). Torção da própria VM mantida: Td 31,8 kN·m, TRd2 124,7, interação 0,41, Asw 3,35 cm²/m por ramo, Asl 5,76 cm².
- Sequência (VM01, CT02, CT04, MON02, MON03, LA01, NG01): montar VM → concretar as pontas dos dois lados → aguardar fcj ≥ 20 MPa → montar as lajes → bainhas BA-1 com N11 → 2º estágio + capa.


## DEC-040 — Pilares redimensionados com o modelo integrado r05: Ø16, estribos Ø6,3, pinos visíveis (22/10/2026)
Pedido do Nathan: "por que estribos de 8 mm? a armadura parece exagerada, com ferros de 16 dá para ajustar? não vi os pinos de apoio das vigas".
- Origem dos 14 Ø20: rev04, modelo_global_r04 (sem a cobertura e as placas travando) + método geral no pilar mais solicitado (λu 1,23), aplicado a toda a família 40×60. No modelo integrado r05 o uso desses pilares caiu para 0,22–0,60.
- Método (exemplos/letsara/estudo_pilares_r05.py → estudo_pilares_r05.json; dimensionar_pilares_r05.py → dimensionamento_pilares_r05.json; manuseio_pilares_r05.py → arranjo_pilares.json): as 33 combinações ELU do r05 (P-Δ global, 0,4 EciIc — NBR 9062:2017 Anexo A —, desaprumo H/400) com os esforços de cada trecho de cada pilar. Por marca, o arranjo de MENOR aço (Ø16) que passa em TODAS as verificações:
  (a) seção da base com a 2ª ordem global + fluência e_cc (NBR 6118:2023 15.8.4, φ = 2,0, le = 2H, quase permanente ≈ ELU sobrecarga/1,35), flexão oblíqua (17.2.5.2);
  (b) método geral (15.8.3.2) no pilar isolado engastado, com as cargas nos níveis reais (forças verticais dos consolos do mezanino, da I130 e da cobertura onde entram, forças horizontais e momentos de cada nó do r05), fibras, corrotacional, φef 0,5, θ1 — λu ≥ 1,0 (a 1ª versão, com N todo no topo, superdimensionava os pilares do mezanino e foi descartada);
  (c) manuseio NBR 9062 5.3.2: deitado nas 2 AL-2 e verticalização na base + FI-1 (γf 1,3 × βa 1,3 com N = 0 e σs ≤ 0,5 fyk = 250 MPa) — governou PL-06/07, PF-01 a 03, PG-01/04;
  (d) ρ ≥ max(0,15 Nd/fyd; 0,4 %), espaçamento ≤ 40 cm (18.4.2.2).
- Resultado (antes → depois, Ø16): PL-01 14Ø20 → 14; PL-02/03 → 6; PL-04/05/08/12 → 12; PL-06/07/09/11 → 10; PL-10 → 14; PF-01/02 → 10; PF-03/04 → 12; PF-05/06 → 14; PC-01 10Ø20 → 8; PC-02 8Ø20 → 12Ø16; PC-03 12Ø20 → 16Ø16; PM-01 10Ø20 → 6; PG-01 4Ø20 → 6Ø16; PG-03 4Ø20 → 8Ø16; PG-02 4Ø16 = 4; PG-04 4Ø16 → 6 (manuseio). Aço dos pilares: 15.156 → 9.752 kg (−36 %).
- Estribos: Ø6,3 CA-50 (18.4.2: φt ≥ 5 mm e ≥ φl/4 = 4 mm; s ≤ min(20 cm; b; 12 φl = 19,2 cm) → c/15, c/10 nos 150 cm do cálice e das pontas). Cortante: Vd máx 57 kN < Vc0 ≈ 230 kN → sem armadura mínima de cortante (17.4.1.1.2, pilar comprimido). Cálice com chaves (interface rugosa, NBR 9062 7.7) → transferência como monolítica, sem pico de cortante no embutimento. Grampos N3/N3A Ø6,3 nas barras a mais de 20 φt (126 mm) do canto do estribo (18.2.4), calculados por marca. Ø8 fica só nas peças dos consolos (estribos verticais N6) e Ø10 nos estribos horizontais do consolo e N18 — dimensionados com o consolo.
- Barras: a mais longa (N1) tem 1092 cm < 1200 cm (barra da usina) — nenhuma emenda nos pilares.
- Pinos: existiam no cálculo e nas tabelas; agora aparecem rotulados nas vistas de fôrma (consolo frontal "pino PN-x Øxx", assento da TS-01 "2 PN-3 Ø25 sai 30 + NEO-4", topo dos PC-01/PC-02 "4 PN-5 Ø20 sai 30") e em vermelho com rótulo nos isométricos; a saliência fica no DETALHE 1 de cada consolo.
- O r05 continua verificando os pilares com o ARM do r04 (pilar_uso_max) — para conferência; o dimensionamento vale o arranjo_pilares.json.

## DEC-041 — Barras de usina de 12 m (traspasse) e nomenclatura P/V por leitura (22/10/2026)
Decisões do Nathan: (1) a fábrica usa barras de 1200 cm — toda barra maior é emendada por traspasse; (2) pilares P1…P33 e vigas V200…/V300…/V400… (série por nível começando no número redondo), um nome por peça, em sentido de leitura; a folha de detalhamento lista as peças iguais que detalha.
- Traspasse (arm_nd.dividir_barras, automático em qualquer folha): NBR 6118:2023 9.4.2.4 / 9.5.2.2, lb = φ/4·fyd/fbd ≥ 25φ (γc 1,4, η1 2,25, η2 1,0 boa / 0,7 má aderência por 9.3.1), l0t = α0t·lb ≥ máx(0,3α0t lb; 15φ; 20 cm), arredondado a 5 cm; metade das barras emenda num ponto e a outra metade defasada ≥ 1,3 l0t (50 % por seção → α0t 1,8); trechos iguais no grupo A, grupo B procurado para defasar (com um trecho a mais se preciso); trecho mínimo 2 l0t. Ø ≤ 32 (traspasse permitido, 9.5.2.1). Resultados: TS-01 N2 Ø12,5 (má, l0t 80) e N5 Ø10 (boa) em 2 trechos; I130 N3 Ø20 (má, l0t 125) em 2 (V400) ou 3 trechos (V401/V402), N4 Ø8 (l0t 40) e N12 Ø10 (l0t 45) em 2–3 trechos. As barras emendadas são construtivas/porta-estribo ou de compressão (a tração principal é a protensão).
- Nomes: nomes.py → nomes.json; renomear.py troca no texto desenhado as marcas internas e as referências do R01 (LOC01 e NG01 têm o quadro de correspondência com o R01, que usa P1–P14 e V405–V407 com outro significado). As I130 antigas V407/V406/V405 viram V400/V401/V402.

## DEC-042 — Cabeça (platibanda) dos pilares: cantos de seção cheia e armadura própria da cabeça (22/10/2026)
Pedidos do Nathan: (A) a platibanda tem carga menor — apoio e içamento fora dela e ver se dá menos ferragem; (B) os cantos precisam de mais área de platibanda concretada para montar as peças metálicas.
- (B) Os cantos (P1, P9, P25, P33 = PL-07, PL-08, PL-03, PL-04) tinham cabeça 30 × 30 (recuo 30 na face A + 10 na face lateral interna, rev02 "a validar"); a CE-1/CC-1 de 380 não cabia. Primeiro proposto cabeça 40 × 40 (recuo A de 20); **decisão do Nathan (22/10, 07:54): canto SEM platibanda recuada — seção cheia 40 × 60 até +10,00, sem recuo em nenhuma face.** Consequências: (1) as CE-1/CC-1 das duas faces externas ficam na face inteira; (2) sem N13 nos cantos — as barras do corpo vão inteiras até o topo; acima do CP-VB (2,20 m em PL-03/04, 1,04 m em PL-07/08) o vento das placas dá uso 0,26/0,40 (PL-03) e ≤ 0,08 (PL-07/08) — cabeca_pilares_r05.py, canto_cheio(); (3) a VB continua no CP-VB da face A (abaixo do topo) — nada mudou; (4) a última terça do lado E, que apoiava no recuo (ST-1F, 2 M20 verticais), termina a 1 cm da face lateral interna do canto (face D do PL-07, face B do PL-08) e apoia no ST-1FL: chapa dobrada 9,5 × 290 (190 na face + 100 na alma, 2 M12) presa por 2 barras roscadas M20 A36 horizontais embutidas na face (ES-1FL, hef 150 + grampo U Ø10, a 7 e 15 cm da aresta da face A, padrão Mitsubishi). Reações REAIS da terça de ponta (22/10, modelo_integrado_r05, grupo "ST-1FL canto", x = 39,22, envoltória ELU das 48 combinações): Fy 15,7 (⊥ à face), Fx 4,0, Rz 8,2 kN (levantamento; 4,5 para baixo) — no lugar da envoltória emprestada do ST-1V-R (Fy 49,1). verif_st1fl.py (ACI 318-19 cap. 17, C40, fissurado, borda 70, φ 0,75 com o grampo): N = 1,25·Fy + Rz = 27,9 kN contra φNcbg 57,6 (o 122 anterior não tinha ψed nem a área reduzida pela borda) e φNsa 147 → 0,48; V 9,1 kN, Fx ⊥ à aresta contra φVcb 11,2 → 0,37; interação 0,85 ≤ 1,2; chapa 9,5 (balanço 60 mm até a 1ª barra) M 0,94 / 1,37 kN·m → 0,69; 2 M12 8.8 na alma Z 2,30: 9,1 / 16,7 kN → 0,55. ES-1FL e chapa mantidos; (5) calha começa/termina a 22 cm do eixo das linhas 1 e 9 (2 cm da face); extravasor: decisão do Nathan (22/10) — saída por dentro da obra, furo na placa executado na obra, sem detalhamento nem marca de placa nova (só nota na COB03); (6) RF-2C/RF-3P dos cantos na face A do canto (30 cm para dentro da cabeça dos demais); TP-40/lã/zipada/painéis das faixas junto às fachadas recortados no canto (x 0,31 a 39,19 até 21 cm do eixo da linha); RF-4/RF-4C/RB de face a face dos cantos. Folga da cobertura escondida (15 cm) e topo +10,00 sem mudança. Manuseio dos cantos: sem mudança — já era calculado com o peso da seção cheia (DEC-040); FI-1 a L − 0,70 m e AL-2 no corpo.
- CE-1 nas faces laterais em ponta de parede (cantos e PL das paredes internas): o console CS-1 da ponta da placa fica a 70 mm da aresta da face C; a chapa centrada no pilar (±190 em face de 600) não o alcançava. A CE-1 passa a ficar a 5 mm da aresta da face C (pinos a 75 mm da aresta).
- (A) A cabeça não tinha dimensionamento próprio (armadura construtiva: fileira da face C + 4 N13 Ø16 ancoradas 60 cm). Calculada como balanço a partir do recuo com o vento das placas da platibanda (13,81 kN de cálculo por console, nos dois sentidos) e o peso das placas excêntrico (7,5 cm): cabeças altas (2,80 m: PL-01/02/09/10) tinham uso 1,32 na sucção e PL-02/09 2,11 na sobrepressão — a carga vertical é menor, mas o vento na platibanda governa. Resultado (cabeca_pilares_r05.py → cabeca_pilares.json): N13 por marca, de 2 Ø10 (PF-06) a 6 + 3 Ø16 (PL-02/09); cantos sem N13, ancoradas por traspasse l0t (NBR 6118:2023 9.5.2.2, α0t 2,0, má aderência) de 60 a 125 cm. Aço das N13 na obra: 370 → 391 kg (as cabeças baixas caem, as altas sobem, os 4 cantos zeram 55 kg).
- Alças AL-2 e furo FI-1: já estavam no corpo (abaixo do recuo) em todas as marcas; nada muda no manuseio (DEC-040).
- Planta-chave das folhas de pilar: cada peça da folha com círculo e chamada com o nome próprio.
- Checagem geométrica (colisao_platibanda.py, caixas envolventes do modelo 3D): achados fora desta decisão, para o Nathan — (1) nas fachadas 1 e 9 o plano das placas segue a face dos PF (0,30 do eixo da linha), mas a face lateral dos pilares de canto está a 0,20: as CE-1/consoles de canto ficam 10 cm à frente do concreto; (2) paredes internas das linhas 2 e 4: as CE-1 ficam 15 a 25 cm à frente da face dos PL/PM/PC; (3) a zipada/TP-40 (borda em y = −0,15) entra 15 cm na cabeça dos PF; (4) X Ø16 toca 6 mm a cabeça dos PF da linha 9.

## DEC-043 — Vigas protendidas em PROTENSÃO COMPLETA; VB 15×60 mantida; otimização das demais famílias = manter (22/10/2026)
Decisão do Nathan: as vigas protendidas (I130 V400–V402, I90 de cobertura V407–V420, VM meio vaso V200–V207/V300–V307) são de protensão COMPLETA (NBR 6118:2023 Tab. 13.4, nível 3): ELS-D (descompressão) na combinação FREQUENTE (ψ1) e ELS-F (formação de fissuras, σ ≤ α·fctk,inf) na combinação RARA (ψ = 1). Antes estavam verificadas em protensão limitada (ELS-D quase permanente, ELS-F frequente). O nível entrou como parâmetro (`nivel="completa"`) em prefabricados.verificar_viga_pretracionada, calc_i110_r01.py e calc_vm_meio_vaso.py.
Resultado (menor nº de cordoalhas que passa em completa + ELU + ato + manuseio, seções mantidas):
- I90 de cobertura (14 peças): 8 → 10 cordoalhas Ø12,7 (5 a 5,5 + 5 a 10 cm, x 0/±4/±15,5); com 8 a descompressão na frequente dava +0,21 MPa. Ato: as 4 de 10 cm em x ±4 e ±15,5 isoladas 3,00 m (6 ativas nas pontas, como antes): topo 3,03 ≤ 3,85 MPa, As 6,04 ≤ 6,48 cm² (N2 + N9). ELS-D freq. −1,99, ELS-F rara −0,47 MPa.
- I130 V400 (ex-V407): 20 → 17 (5+4+4+4, sem cordoalhas na mesa superior): ELS-D freq. −0,33 (folga MARGEM_D 0,25), ELS-F rara 0,61 ≤ 3,71 MPa.
- I130 V401/V402 (ex-V406/V405): 30 → 32 (28 + 2 a 22 cm em x ±5, isoladas 4,0 m, + 2 na mesa superior); 28 + 2 dava +0,012 MPa na V401. Mesmo arranjo nas duas (dividem a pista de 60 m: 24,1 + 24,0 m). ELS-D freq. −1,02 / −1,22; ato topo 3,37 ≤ 4,55 MPa.
- VM meio vaso h 80 (16 peças): 8 + 2 → 10 + 2 (4 a 5, 4 a 12, 2 a 19 cm + 2 na aba); 8 + 2 dava +0,37/+0,66 MPa na frequente. ELS-D freq. −1,82/−1,53, ELS-F rara 0,04/0,37 ≤ 2,95 MPa. h 80 mantido (dente validado pelo MEF).
- Cordoalha da obra: 7.646 → ≈ 8.390 kg (+ ~740 kg).
- VB 15×60 mantida (15×55 economizaria 122 kg de CA-50 mas baixa o CP-VB e muda o nível: Nathan manteve). Laje alveolar LP20 7 Ø12,7 inalterada (CAA I / parcial decidida antes).
- Otimização das outras famílias (placas, lajes, consolos, fixação das placas, cobertura metálica): já no mínimo no critério atual (< 2 % de ganho) — manter (otimizar_resumo.json).

## DEC-044 — I130 do eixo C atravessando as paredes internas G e C: RECORTE nas placas + CE-1L; CS-1 com CALÇO onde a face do pilar fica atrás do plano dos consoles (22/10/2026)
Contexto: a checagem do modelo inteiro (colisao_modelo.py) achou 12 colisões, todas de projeto: o consolo CP-I130 (50 × 40 × 49) e o nariz do dente do I130 (V400 na linha 2; V401/V402 na linha 4) entram 24 / 19 cm na placa de cima (fiada +6,25) das paredes G-11/G-17 e C-11/C-17; e nos pilares de 40 ⊥ à parede (cantos P1/P9/P25/P33 nas vistas A/I, P1B/P2B na vista G) e de 25 (P10 na vista C) a CE-1 fica 100 / 75 mm atrás do plano dos consoles (os PF têm 60). Alternativas: deslocar as paredes internas ou terminar o I130 antes da parede (muda estrutura/arquitetura); girar os PF; pilares com 60 ⊥ à parede (muda fôrma). Decisão do Nathan: "Recorte nas placas" e "Calço/console especial".
Recorte (placas.json → `recorte`, ND-LET-PP06): nas 4 placas (tipos PP-05RE/RD e PP-08RE/RD — RE/RD = recorte à esquerda/direita na elevação da vista; não são a mesma peça virada, a face interna fica para o pilar) recorte de 260 × 1130 mm na ponta do eixo C (folga 20 ao consolo, 70 ao nariz; toco 260 × 120 embaixo, 66 mm ao fundo do consolo descontada a janela de 40). Os 10 fios param na face do recorte (lbpt contado dela); o console dessa ponta vai para 330 mm da ponta (nicho NC-1 de 260 a 400, aberto na face do recorte) e o dente Gerber N3–N7 é o da PP01 com a ponta na face do recorte; toco sem protensão com N8/N9 2 Ø8 de borda, N10 2 Ø8 diagonais e N11 Ø6,3 c/8. Desforma 4 pontos com balancim: face do recorte 0.74 MPa, ponto de desforma -1.29 ≤ 1.2 MPa; montada (vão 9.46 m) -1.03 MPa ≤ 0.
CE-1L (fixacao_placas.json → `CE1L`): o console a 340 do eixo do pilar (largura 400) cai fora da CE-1 → CE-1L 840 × 330 × 12,5 com asas de 220 além das faces, mesmos 4 pinos e N18, só na fiada +6,25 de P8A (PC-01) e P11 (PC-02) — 2 peças. Asa em balanço de 140: flexão no plano 16.5 + torção 90.7 MPa → von Mises 158.0 ≤ 227.3 MPa (uso 0.695); pinos iguais à CE-1 (2 consoles; os momentos no plano das 2 asas se anulam).
Calço (`calcos`): CS-1C (e = 100: cantos das vistas A/I, P1B/P2B da vista G — 39 pç) e CS-1D (e = 75: P10 da vista C — 12 pç) = CS-1 comum + caixa fechada de chapa 9,5, 120 × 330 × e (a altura toda da CE-1), soldada na fábrica nas costas do CS-1; na obra o fundo da caixa é soldado na CE-1 (filete 6, 2 × 330). Com a caixa de 330 o binário do console entra na CE-1 com braço 2/3 · 330 (com uma caixa de 130 a flexão local da CE-1 dava 366 > 227 MPa): CS-1C braço 154.0 mm, M 4.13 kN·m, pinos T 21.6 ≤ 47,3 kN (interação 0.607), flexão local 144.1 ≤ 227 MPa, caixa 9.8 MPa, solda de campo 33.1 ≤ 215.6 MPa; CS-1D folgado. Nesses pilares a CE-1 recebe 1 console só. Modelo 3D: placas recortadas (corpo + toco), consoles nas posições reais, CE-1 na face real do pilar com a caixa do calço → colisao_modelo.py = 0.
Pendência achada no caminho (não aplicada, precisa de decisão): P8 e P8B (PM-01, topo +6,55) recebem 6 CE-1 na face B (fiadas 0 a 5) mas a 6ª (centro +7,17) fica acima do topo do pilar — as placas G-11 (ponta em P8), G-17 e G-23 (pontas em P8B) da fiada +6,25 não têm onde apoiar nessa ponta. Proposta: PM-01 até +7,45 (P8, 2 cm abaixo da TS-01 em +7,49) e +7,50 (P8B).

## DEC-045 — Pisos do mezanino +3,90 / +7,30, abertura e escada metálica, P6/P7 da escada e P6 da linha 2 (23/10/2026)
Decisão do Nathan: topo da capa do mezanino em +3,90 e +7,30 (antes +3,15 / +6,55), numa fonte só (geometria.Z_PISOS) usada por cálculo, pranchas e 3D. Escada só até o +3,90, metálica, em U: 22 espelhos de 17,73 cm, piso 28 cm, patamar intermediário +1,95 e patamar de chegada +3,90 junto à linha 2; longarinas U 152 parafusadas, 1º degrau apoiado no piso. Abertura da laje +3,90 de x 36,00 a 39,20 e de y 3,99 à linha 2, entre o P6 (25 × 40, x 36,175), o P7 (40 × 60, eixo E) e o P6 da linha 2; viga VM-04 P6–P7 no +3,90 e lajes curtas LA-03/LA-04 (7 Ø9,5) da linha 1 a ela. Pilares novos PE-01 (P6 da escada), PE-02 (P7) e PE-03 (P6 da linha 2), dimensionados no modelo r05. Sobrecarga do +3,90 (depósito) = 5,0 kN/m², confirmada pelo Nathan em 23/10/2026 (cargas_mezanino.json). Na chegada a viga de frente fica em balanço de 1,45 m sobre a entrada do lance 1 com pilarete em tubo 80 × 80 entre os lances (a entrada do lance 1 fica livre; ND-LET-ES01).

## DEC-046 — Laje de cima (+7,30) sem uso: sobrecarga 1,0 + revestimento 1,7 kN/m² (23/10/2026)
Decisão do Nathan: o +7,30 é laje de cobertura do bloco, sem uso — NBR 6120:2019 acesso só para manutenção 1,0 kN/m² e regularização + impermeabilização 1,7 kN/m². A mesma marca de laje (LA-01) serve aos dois níveis (o +3,90 governa); VM, pilares e cargas de fundação refeitos.

## DEC-047 — Vigas do mezanino retangulares protendidas com 2º estágio (sem meio vaso) (23/10/2026)
Decisão do Nathan (coordenação 10:21): todas as vigas que apoiam laje passam a retangulares protendidas; a laje alveolar apoia 10 cm no topo da viga (neoprene em fita, folga de 2 cm) e as alças do 2º estágio saem na faixa restante, concretada com a capa; topo da viga = capa − 0,25 (+ fita); protensão completa; dente Gerber preferido; sem torção de montagem (pontas concretadas antes das lajes, DEC-039). Substitui o meio vaso da rev04–rev08.

## DEC-048 — Linha 2 sem TS-01: W 310 × 32,7 contínua só sobre os pilares, mão-francesa em toda terça (23/10/2026)
Decisão do Nathan (opção 2 do quadro de 23/10): na linha 2 a cobertura é uma W 310 metálica contínua de A a E, apoiada só nos pilares (A recuo do P1-L2, B, C topo do P8A, D, P6 da linha 2, E recuo do P2-L2) por montantes W 150 × 22,5 com chapa de base e 4 barras M20 embutidas (padrão Mitsubishi); terças no clip ST-W e mão-francesa L 51 × 51 × 4,8 em toda terça (trava a mesa inferior, comprimida na sucção); sem montantes sobre as vigas do mezanino. O cálculo (calc_cobertura_linha2.py, NBR 8800:2024) leva a W 310 × 32,7 (uso 0,796; flecha 32,4 ≤ 39,5 mm) — a W 310 × 44,5 do quadro era estimativa. TS-01 passa a 12 peças (linhas 3 a 8; sem TS-01B nem ST-1P4). Folha nova ND-LET-COB05.

## DEC-049 — VM do mezanino 30 × 75 com dente Gerber 45 em todas as marcas (substitui o 25 × 80 da DEC-048) (23/10/2026)
Contexto: com a VM 25 × 80 o MEF não linear do dente 25 × 35 reprovou (Vu 224 kN, pico 348 kN < 1,06·Fd 497 kN, γn 1,2) e a biela da NBR 9062:2017 7.4 também (τwd 6,35 > 5,14 MPa). Estudo de largura (estudo_vm_largura.py): b 25/30/35/40 com o menor h e o menor dente que passam em tudo; MEF de 1 fase e 2 fases (mef_vm_largura_1f.py / _fases.py).
Decisão do Nathan: todas as VM retangulares 30 × 75 (fôrma única), dente Gerber 45 × 40, recorte 30, consolo CP-MEZ com a largura da face do pilar (40 × 40 × 27,9) e NEO-5F 200 × 200 × 21; 12 cordoalhas nas VM-01/VM-02 e 6 nas VM-03/VM-04; suspensão 3 estribos Ø20 + 4 Ø16 retas no fundo a partir do canto reentrante; γn 1,2; fundo da viga +2,89 / +6,29; faixa de 2º estágio de 18 cm. Biela 4,01 ≤ 5,14 MPa, PCI Vmax 488,8 ≥ Fd 475,7 kN, MEF pico 519,5 ≥ 475,7 kN.
Ressalva do MEF (registrada na MC09 e na VM01): o elemento do canto inferior junto ao recorte, onde as cordoalhas começam a transferir, passa de 3,5‰ a ~290 kN — esmagamento local da zona de ancoragem; tratado com fretagem N14 (estribos fechados Ø8 c/5 nos 50 cm a partir do canto reentrante, envolvendo as 2 camadas inferiores) + N13 4 Ø16 retas e liberação gradual com fcj ≥ 32 MPa. Laje alveolar passa a 9,55 m (2 Ø15,2 + 5 Ø12,7, uso 0,91; f1 4,77 Hz, ok para depósito). As I130 V401/V402 ficam como estão (h 130, com dente) até decisão do Nathan.

## DEC-050 — Linha 2 sem montantes: W 310 direto na cabeça de concreto dos pilares (24/10/2026)
Decisão do Nathan (24/10): tirar os montantes MT W 150 e as chapas CB 250 × 250 × 19 dos apoios da W 310 × 32,7 da linha 2 e subir a cabeça de concreto de cada pilar até o fundo da W, cada um na sua altura (inclinação 3 %). Topo do concreto (m): A +7,747 (sobe 0,55); B +8,039 (sobe 0,74); C +8,335 (sobe 0,56); D +8,632 (sobe 1,33); P6 +8,828 (sobe 1,53); E +8,923 (sobe 0,55). Ligação sem solda: chapa CA-L2 250 × 250 × 19 sobre graute 20 mm, 4 barras roscadas M20 8.8 L 520 (hef 400 + grampo) a 150 × 150, fora da mesa (bf 102), e 2 presilhas PR-L2 19 × 80 × 200 sobre calços 12,5 prendendo a mesa; torque só no C (apoio fixo), porca encostada nos demais (deslizantes). Usos máximos (calc_cobertura_linha2.py, NBR 8800:2024): barras 0.067, alma (escoamento/enrugamento local) 0.193, presilha 0.748. O P14 (P8B, eixo D) sai do PM-01 e vira a marca PM-02 (alturas diferentes); PM-01 = P25 (B), PC-01 = P18 (P8A, C), PE-03 = P5 (P6 da linha 2), PL-02 e PL-06 com o recuo no topo novo. Folhas: COB05 rev 02, pilares, LOC/CT/MON, lista metálica e quantitativos.
Alternativa descartada: manter os montantes (mais peças metálicas, ligação extra e chapa de base) — o Nathan preferiu o concreto até a W.

## DEC-051 — Escada metálica sem nenhuma solda e com base metálica BM-1 no térreo (24/10/2026)
Pedido do Nathan: "precisa ter uma base metálica para apoio da escada". O pé do lance 1 e o 1º degrau apoiam numa soleira BM-1 U 152 × 12,2 L 1500 em pé no piso do térreo, sobre graute 10–20 mm, presa por 3 pares de L 76 × 76 × 6,3 × 100 com chumbador químico M12 hef 100; o pé de cada longarina vai na alma da soleira por L 76 × 120 (4 M12) e o bocel do 1º degrau na aba de cima (2 M10). Uso dos chumbadores 0,037; σ no piso 0,18 MPa. Piso: laje do térreo e ≥ 12 cm, fck ≥ 25 (confirmar na obra); senão bloco 50 × 50 × 40 sob cada apoio. Na mesma revisão saíram as soldas que ainda havia (chapa de topo das VP-1, chapa do pé da longarina, base dos pilaretes): VP-1 na face dos pilares por 2 L 76 × 76 × 6,3 × 140 + 4 BR-M16; pilaretes com 2 L 102 × 102 × 9,5 × 200 + 4 chumbadores químicos M12. Posição da escada conferida contra o arquitetônico e o R01 (canto E entre P6, P7 e a linha 2, sobe pelo lado do P6 a partir da linha 2): mantida; a escada externa em L da fachada A fica em aberto (quadro scratchpad/conf/decisao_escada_posicao.png).

## DEC-052 — Linha 2: W 200 × 15,0 contínua com montantes curtos no meio dos vãos sobre as VM do +7,30 (24/10/2026)
Decisão do Nathan (24/10): viga usando praticamente 100 % do aço, aceitando apoio no meio dos vãos. W 200 × 15,0 (A572 Gr. 50) contínua de A a E em 4 módulos (emendas TL-1/TL-2 perto do momento nulo), apoiada nos 6 pilares (cabeça de concreto subida até 39 mm abaixo do fundo da W, CA-L2 250 × 250 × 19 sobre graute, 4 BR-M16 L 450 pela mesa) e em 4 montantes W 150 × 13,0 (L 0,72 a 1,55 m) no meio dos vãos A–B, B–C, C–D e D–P6, sobre as VM do +7,30. Base do montante: espera EM-L2 (4 BR-M16 8.8 L 330 com gancho laçado na alça N9 da VM, posta antes da capa com gabarito), montagem só com a capa curada. Usos (calc_cobertura_linha2.py, NBR 8800:2024): flexão 0,80 com mão-francesa MF-1 em todas as terças (sem ela 2,99), cortante 0,28, flecha G+Q 11,0 mm ≤ L/250 = 19,8; montante máx. 0,735 (alça da VM com a tração de sucção 77,3 kN de cálculo no MAB; barra 0,28, compressão 0,28, tração 0,38, cantoneiras 0,57). W 200 × 15,0 é o perfil W mais leve que passa: o único mais leve, W 150 × 13,0, dá flexão 1,20 e flecha 21,2 mm > 19,8 (mesmo cálculo, rodado em 24/10). VM-01/02/03 verificadas com a carga concentrada do montante no meio do vão (calc_vm_retangular.py). Aço da linha 2: 1,30 t (W 310 × 32,7, DEC-050) para 0,59 t de viga + 0,06 t de montantes.
Alternativa descartada: W 310 × 32,7 só nos pilares (DEC-050): o dobro de aço, uso baixo.

## DEC-053 — Escada metálica externa em L na fachada A até a porta do 2º pavimento (+3,90) (24/10/2026)
Decisão do Nathan (24/10, opção B do quadro decisao_escada_posicao): escada externa em L junto à fachada A, 22 espelhos de 17,7 cm e piso 28 (Blondel 63,5), largura 1,50, patamar no +0,886 (5 degraus) e lance de 17 degraus até o patamar de chegada no +3,90 na porta (vão na placa da vista H, y 0,89–1,79, h 2,14). Geometria do arquitetônico deslocada 15 cm para fora para afastar das placas. Longarinas U 203 × 17,1 (lance de cima, uso 0,36, f1 7,2 Hz) e U 152 × 12,2 (lance de baixo), vigas e pilaretes W 150 × 13,0, bases próprias em blocos BE-1 60 × 60 × 60 C25 (σadm 150 kPa a confirmar na sondagem), não apoiadas nas placas; travamento horizontal TR-1 no pilar P28 (eixo A). Tudo parafusado, galvanizado a fogo. Porta: as placas acima do vão apoiam em ombreiras internas OM-2 U 152 do piso do térreo (sem placa sobre placa). Folha ND-LET-ES02; modelo 3D grupo "Escada metálica externa".
Alternativa descartada: escada interna no canto E (mantida, DEC-051) como único acesso ao 2º pavimento.

## DEC-054 — I130 V401/V402 (V406/V405) com h 120, dente Gerber e consolo CP-I130 com mísula (24/10/2026)
Decisão do Nathan (24/10, opção A do quadro decisao_i130_h120): h 120 COM dente 78 × 35 (recorte 52 → 42), protensão LIMITADA (CAA II, pré-tração, NBR 6118:2023 Tab. 13.4 nível 2), C50 com liberação SÓ com fckj 50 MPa (nota na ND-LET-I130), 24 Ø15,2 (7+5+5+5, linhas 16 e 21 isoladas 2,0/4,0 m + 2 na mesa superior), N3 6 Ø25. V405/V406: ELU 0,72, x/d 0,366, ELS-D −0,39/−0,62 MPa, ELS-F 0,80 ≤ 3,71, ato 3,98/−31,8 (lim 4,89/−35,0), Fd 610,5 kN. V400 (V407) também passa para h 120 (fôrma única das três): 18 Ø15,2 (5+5+4+4), ELU 2085/3412. Dente pelo MEF não linear (calc_dentes.py, armação da prancha): Vu = 728,5 kN, FS 1,19 ≥ 1,06 — a falta de convergência anterior (Vu 32 kN) era do passo de deslocamento de 0,05 mm no 1º passo depois da fissuração da protensão; com 0,02 mm a análise vai até o fim (mesmo modelo e critério). Consolo CP-I130 com MÍSULA: 49 junto ao pilar e 39 na ponta (fundo da ponta alinhado ao fundo da viga +6,576), NBR 9062:2017 7.3: a/d 0,45, τ 3,47 (3,91 na seção da carga) ≤ 5,86 MPa, tirante 4 alças Ø16 (uso 0,80); assento +6,966 inalterado. Pilares P18 (PC-01), P20 (PC-02), P22 (PC-03), P23 (PF-04). Biblioteca: prefabricados.ato_pretracao recebeu `area` (cordoalha Ø15,2).
Alternativas descartadas: h 120 sem dente com consolo rebaixado 39 cm (opção B); apoio centralizado no topo dos pilares (opção C).

## DEC-055 — Piso do 2º pavimento: topo da capa +3,90, piso pronto ~+3,95; escadas com espelhos de 17,95 (24/10/2026)
Decisão do Nathan (24/10): o nível do 2º pavimento é o topo da capa +3,90 (estrutura inalterada: lajes, VM e consolos); o piso pronto fica em ~+3,95 (revestimento 5 cm). As duas escadas chegam no piso pronto: 22 espelhos de 3,95/22 = 17,95 cm, piso 28 (2e + p = 63,9 cm). Interna (ES01): patamar +1,975, chegada +3,95; externa (ES02): patamar +0,898, chegada +3,95 na porta da vista H. Fonte única: geometria.Z_PISO_PRONTO. Usos refeitos (calc_escada_metalica / calc_escada_externa): longarina interna 0,24, externa 0,36.

## DEC-056 — Área "Doca" com piso nivelado, sem rebaixo (24/10/2026)
Decisão do Nathan (24/10): a área da doca tem o piso no mesmo nível do restante (sem rebaixo nem muro de doca). O projeto estrutural já não tinha rebaixo; fica registrado para fundações/piso.

## DEC-057 — Sem ponte rolante (24/10/2026)
Confirmação do Nathan (24/10): não há ponte rolante. Mantém-se o que já estava adotado (rev04): sem vigas de travamento VT, limites de deslocamento da NBR 9062:2017 Tab. 7 para galpão sem ponte, pilares e consolos sem carga de ponte.

## DEC-058 — Eixo C no arranjo C: pilar novo P23 (PC-03), 3 vãos iguais de 16,517 m e I130 com cordoalha Ø12,7 (24/10/2026)
Decisão do Nathan (24/10): P20 fica na linha 4; P22 (R01 P13, PC-03) passa para y 46,317 e entra um pilar novo PC-03 40 × 40 em y 62,833 — três vãos iguais de 16,517 m até a linha 9; a V400 (20,15 m) não muda. Nomes: a regra de nomes (ordem de leitura) foi aplicada e a cascata ficou aceitável (P23 novo; P24 a P37 renumerados automaticamente por renomear.py), então não foi preciso usar "próximo número livre". As três I130 novas (V401, V402, V403) são uma marca de fôrma e armação. Cordoalha Ø12,7 CP-190 RB, fckj 50, protensão limitada (ELS-D com margem −0,25 MPa): a busca percorre os arranjos candidatos × os 4 padrões de isolamento escalonado (linha de baixo sempre aderente) e adota o que passa com menos cordoalha — V401–V403: 13 (5 + 4 + 4), só a linha y 14 isolada 235 cm da ponta (padrão 0/0/2000/4000); V400: 18 (7 + 5 + 4 + 2), padrão 0/2000/2000 + linha 22 a 4000. Bainha de PEAD vedada nas pontas. Dente: MEF com passo 0,02, FS 1,53 (Fd 474,4 kN). Modelo r05 corrigido junto: I130 como vãos simplesmente apoiados, montantes da linha 2 modelados e G favorável só com vento. Consequência: as ES-1V M16 do ST-1V do eixo 1 ganham grampo U Ø10 (Fy até 16 kN; interação 0,61).

## DEC-059 — Portões da linha 4, opção A: PG apoiam a TS-01A e placa PV-1 sobre o portão (24/10/2026)
Decisão do Nathan (24/10): os PG-01 a PG-04 viram apoios da TS-01A (neoprene NEO-7 + graute depois da montagem), o fundo da viga no vão dos portões fica em +7,50 (portões 500 × 750 livres) e entra a placa PV-1 10 × 37 (+7,50 a +7,88) sobre o portão PG-04–PG-03, apoiada nas cantoneiras CL-V das faces dos PG e travada pelas CT-V. TS-01A contínua sobre os PG para g2 + q: Md− 86,5 ≤ 165,2 kN·m, topo comprimido sobre o PG; reações Rd 9,8 tf (PG-01/03) e 3,5 tf (PG-02/04) somadas às cargas da fundação. calc_portao_l4.py, folha ND-LET-PV01.

## DEC-060 — Escadas: guarda-corpo e corrimão pela RT CBMRS 11, ligações compatíveis verificadas e perfis no limite (24/10/2026)
Pedido do Nathan (24/10). Modelo único escadas_detalhe.py (3D/IFC, ligações, lista e folhas ES01/ES02/ES03). Corrimão nos dois lados a 0,90 m, Ø38,1, 40 mm livres, contínuo nos patamares com 30 cm de prolongamento; guarda-corpo 0,92 nos lances internos, 1,05 nos patamares e na laje, 1,30 na externa; barras com vão livre < 150 mm; cargas 0,73 kN/m, 1,2 kPa, 0,9 kN. Perfis: o mais leve que passa (longarinas U 152 interna, U 203/U 152 externa; VP-1 W 150 × 13,0; demais W 150 × 9,2; barrotes L 64 / L 51; pilaretes tubo 60 × 60 × 2; montantes 40 × 40 × 4 / 50 × 50 × 2 / 60 × 60 × 2). Vigas de fundo da interna em assentos SA-1/SA-2 nas faces dos pilares. Escada externa: a trava TR-1 da rev 00 não alcançava a face do P28 (ficava atrás das placas) — retirada; estabilidade pelo X de barras Ø12,5 com garfo, pino e esticador sob a chegada em 3 planos (uso 0,40). Pé-direito mínimo 3,10 m. 28 ligações, 0 conflitos; 3D com 0 colisões.

