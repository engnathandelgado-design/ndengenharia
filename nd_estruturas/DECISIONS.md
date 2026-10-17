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
