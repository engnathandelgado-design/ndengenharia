---
name: "consultoria-fabricas-pre-moldados"
description: "Use ao prestar assessoria/consultoria a fábricas de pré-moldados ou orientar clientes: concepção, detalhamento de peças, NBR 9062, manual fib, ligações, insertos, folgas, furos, tolerâncias, produção, montagem e contratação."
---

# Consultoria para fábricas de pré-moldados (ND Engenharia)

A ND Engenharia vende assessoria e consultoria a fábricas de pré-moldados. Nathan tem anos como engenheiro de produção/projeto em fábricas (Metal Ferro, Premolfort, Inarmento, Luke Concreto). Objetivos desta skill: (1) riqueza de detalhamento em projetos de todos os tipos de peça; (2) informação técnica para orientar fábrica e cliente final. Responder em português técnico, citando item da norma. Cálculo detalhado (protensão, seção composta, ELU/ELS, MEF, bielas e tirantes) fica na skill `projetos-estruturais-concreto-armado-protendido`; consolos e dentes Gerber na ferramenta própria do Nathan; fundações em `interacao-solo-estrutura`; orçamento em `orcamentista-obras`; pranchas em `pranchas-tecnicas-nd`.

## 0. Fontes incorporadas
- Doniak, Í. L. O. (ABCIC) e Livi, L. O. B. *Estruturas Pré-fabricadas de Concreto — Do projeto à obra pronta* (slides, 88 p., hospedado em feb.unesp.br/pbastos). Base: NBR 9062:2006 ("edição 2007"). Cobre histórico, mercado, normalização, aplicações e PROJETO; os tópicos anunciados de fabricação, montagem, qualidade, contratação e patologias NÃO estão no PDF (seções 8–11 abaixo são conhecimento próprio).
- Van Acker, A. *Manual de Sistemas Pré-Fabricados de Concreto* (fib/FIP 2002; trad. Marcelo de Araújo Ferreira, ABCIC 2003; 129 p., feb.unesp.br/pbastos/pre-moldados/Manual Fib.pdf). Lido inteiro em 07/10/2026 (cap. 1 aspectos gerais, 2 sistemas, 3 estabilidade, 4 ligações, 5 esqueleto, 6 pisos, 7 painéis estruturais, 8 fachadas). Base normativa: Eurocode 2 (EN 1992-1-1:2002), BS 8110, DIN 1045, CEB-FIB MC 1978. Conteúdo na seção 13.
- Marcação: [Iria] = material Doniak/Livi; [fib] = manual Van Acker; [ND] = conhecimento próprio/complemento; (conferir) = checar na norma vigente antes de usar em projeto.
- Norma vigente: **NBR 9062:2017** (numeração de itens mudou em relação à 2006 — os itens citados pelo material são da edição antiga) e **NBR 6118:2023**. Valores [fib] são referência europeia: no Brasil, a NBR prevalece quando divergir; usar [fib] para pré-dimensionamento, detalhamento construtivo e quando a NBR for omissa.

## 1. Conceitos e argumentos de venda [Iria]
- **Pré-moldado** (NBR 9062 3.x): moldado fora do local definitivo, controle conforme especificações do item de controle (12.1.1 na edição antiga). **Pré-fabricado**: pré-moldado executado industrialmente em instalação permanente destinada a isso, atendendo requisitos mínimos de controle (12.1.2 antiga). A diferença está nos "M's": matéria-prima, mão de obra, método, máquinas, meio ambiente (local adequado) e management. Na consultoria, usar isso como roteiro de diagnóstico da fábrica.
- Por que pré-fabricar: velocidade (payback menor), qualidade (indústria × obra), produtividade (mecanização), menos risco e custo fixo no canteiro, menos desperdício, regularidade dimensional (economia em revestimento, caixilhos e instalações antecipáveis), concretos mais resistentes (durabilidade).
- Argumento de **custo total**: comparar não só R$/m³, mas prazo, payback, "não qualidade", canteiro, logística, resíduos, passivo trabalhista, segurança, estrutura administrativa, clima, sindicatos.
- Argumentos extras [fib]: prazo < metade do moldado no local; CAD (> 50 MPa) aumenta 100–150% a capacidade relativa de pilares de 30 → 90 MPa; CAA reduz ruído, pressão na fôrma e bolhas; até 45% menos material, 30% menos energia, 40% menos resíduo de demolição; resistência ao fogo 60 min sem medida especial, 90–120 min aumentando cobrimento; adaptabilidade (estrutura 100 anos, fachada 30–60, instalações 20 — projetar subsistemas trocáveis).
- Mercado de aplicação: galpões logísticos e industriais, supermercados/shoppings, fachadas arquitetônicas, pipe racks, portos/estaleiros, arquibancadas e arenas, aeroportos, edifícios altos (Bélgica: até 45 pav. — ref. Van Acker), estruturas mistas.

## 2. Concepção — o que orientar ao cliente/arquiteto [Iria + ND]
- **Modular sem padronizar**: vãos da mesma ordem de grandeza otimizam formas, pistas e montagem; as obras podem e devem ser diferentes entre si. [Iria]
- Avaliar desde o anteprojeto: vãos, modulação, repetibilidade, custos, locação no terreno, obras na divisa (montagem e acesso de guindaste), localização (transporte), durabilidade (CAA). [Iria]
- **Conceber em pré-moldado desde o início**, não adaptar projeto moldado no local [fib]. Filosofia: sistema de contraventamento próprio, grandes vãos, integridade estrutural, detalhes simples, soluções padronizadas, tolerâncias previstas desde o anteprojeto (ver 13.1).
- **Logística manda na peça**: não projetar peça que o caminhão não transporta, que não entra na obra ou que o guindaste não ergue. [Iria] Checar: comprimento e peso por peça, raio × capacidade do guindaste (tabela de carga do modelo), patolamento, acesso, rede elétrica aérea, curvas do trajeto, AET para cargas excedentes (conferir limites da resolução CONTRAN vigente). [ND]
- Faixas usuais (pré-dimensionamento, conferir caso a caso) [ND]: galpão com pilares engastados em cálice e vigas/terças articuladas; vigas de cobertura protendidas I/T 15–30 m; telha W/protendida de cobertura até ~25–30 m; lajes alveolares h 15–30 cm para ~6–14 m (com capa); vigas de piso T invertido/L com dente; pilares com consolos e emendas para multipavimentos. Faixas europeias [fib] na seção 13.9.
- Sistema de estabilidade (NBR 9062, 5.1.2.1 na edição antiga) [Iria]: (a) pilares engastados na fundação + vigas articuladas; (b) pórticos com ligações resistentes a momento; (c) contraventamento por paredes, núcleos, X; (d) diafragmas de piso/cobertura transferindo horizontais. Definir isso cedo: muda cálice, ligações e capa. Regras [fib]: pilar em balanço resolve até ~3–4 pavimentos / ~10 m de altura; acima disso, núcleos (escada/elevador) + paredes de contraventamento + diafragma; evitar pórtico rígido moldado (forças concentradas, montagem difícil) e pórticos pré-moldados em TT/H (transporte). Posicionar os elementos de contraventamento sem gerar torção (CG da rigidez = CG das forças horizontais).

## 3. Análise em todas as fases (transitórias) [Iria]
NBR 9062 (5.2.1.4 antiga): verificar ELU/ELS em **fabricação, manuseio (saque), armazenamento, transporte, montagem e construção (preliminar e final)**; seção pré-moldada isolada × seção completa (com capa); esforços de montagem × de utilização.

**Exemplo do material (viga 40×55 → 40×80 com capa, vão 6,55 m)**, conferido (M = q·L²/8, V = q·L/2):

| Fase | Seção | q (kgf/m) | M (kgf·m) | V (kgf) | As (cm²) | Asw (cm²/m) | fck |
|---|---|---|---|---|---|---|---|
| Saque | 40×55 | 700 | 3.753 | 2.293 | 2,41 | 2,52 | 12 |
| Montagem (laje + capa fresca, sc 1000 kgf/m²) | 40×55 | 3.722 | 19.960 | 12.180 | 13,7 | 4,11 | 25 |
| Serviço (sc 1000 kgf/m²) | 40×80 | 10.932 | 58.570 | 35.770 | 27,4 | 9,33 | 30 |
| Serviço (sc 100 kgf/m²) | 40×80 | 4.442 | 23.820 | 14.540 | 10,4 | 4,64 | 30 |

Lições: (1) o peso próprio de 550 kgf/m aparece como ~700 kgf/m no saque → coeficiente dinâmico ≈ 1,3 [ND, conferir coeficientes de manuseio/transporte na NBR 9062:2017]; (2) no saque o concreto ainda tem fck baixo (12 MPa) — o projeto deve informar fckj de desforma; (3) com sobrecarga baixa a **fase de montagem governa** a seção pré-moldada (13,7 cm² na montagem > 10,4 cm² no serviço) — erro clássico é dimensionar só a seção final.
[fib] Situações transitórias a listar no projeto: apoios provisórios de estocagem, içamento excêntrico, vento antes da estrutura completa (pilares em balanço sem diafragma), estabilização temporária até grautear/soldar.

## 4. Prescrições da NBR 9062 citadas no material (valores da edição 2006 — conferir na 2017)
### 4.1 Tolerâncias de montagem (5.2.2.4 antiga)
- Planta entre apoios consecutivos: ±1,0 cm; acumulado ≤ 0,1% do comprimento da estrutura.
- Verticalidade: ±H/300, máx. 2,5 cm.
- Nível dos apoios: ±1,0 cm; acumulado ≤ 3,0 cm (2,0 cm em caminho de rolamento).
- Pilares em planta e elevação: ±1,0 cm. Blocos pré-moldados sobre fundação: ±5,0 cm em planta.
- Contornos justapostos: ±2,0 cm.
- Peça fora de tolerância pode ser aceita se o projetista estrutural comprovar que não compromete desempenho estrutural, arquitetônico e durabilidade (5.2.2.8 antiga) — registrar por escrito (RNC + parecer).
- Folgas de projeto: prever folga = tolerância de fabricação + de montagem + deformações (retração, fluência, térmica) entre peças justapostas; tabela de tolerâncias de fabricação por tipo de peça na NBR 9062 (conferir valores). Ver também 13.2.

### 4.2 Embutimento do pilar no cálice (6.2.3 antiga)
- Interface lisa: Lemb ≥ 1,5h se Mk/(Nk·h) ≤ 0,15; Lemb ≥ 2,0h se Mk/(Nk·h) ≥ 2,00; interpolar linearmente entre os dois. h = dimensão do pilar paralela ao plano do momento; Mk e Nk de combinações concomitantes.
- Interface rugosa (chave ≥ 1 cm a cada 10 cm, no pilar E no cálice): multiplicar por 0,8 (equivale a 1,2h / 1,6h).
- Lemb ≥ 40 cm e compatível com a ancoragem da armadura do pilar.
- Na consultoria verificar também: paredes do cálice (armadura horizontal superior e vertical), folga para graute (usual ≥ 5 cm, conferir), graute com fck ≥ do pilar, cunhas/calços de montagem e escoramento até cura. [ND]
- [fib] Cálice liso: carga vertical admitida pela base do pilar; cálice dentado: parte por cisalhamento na interface. Alternativas ao cálice: esperas da fundação em bainhas grauteadas no pilar (diâmetro da bainha com folga para o graute envolver a barra) e base parafusada (chapa/cantoneiras soldadas à armadura do pilar + chumbadores; **furos da chapa de base sempre ampliados**).

### 4.3 Ligações por compressão (apoios) (7.2.1 antiga)
- **Junta a seco**: σ ≤ 0,042·fcd (menor fcd dos materiais em contato) e ≤ 1 MPa; com rotação impedida ≤ 0,06·fcd e ≤ 1,5 MPa. ([fib]/EC2 admite contato direto só com grande precisão de fabricação ou σ ≤ 0,3 fcd — a NBR é muito mais restritiva; seguir a NBR.)
- **Argamassa intercalada**: assentar antes do início de pega; σ ≤ 5 MPa com controle tecnológico e traço estudado com aditivos; τ ≤ 10% da tensão de contato.
- **Concretagem local**: dimensões mínimas que permitam concretar; concreto/graute com fck ≥ menor fck das peças (comportamento monolítico).
- **Dispositivos metálicos**: chapas fixadas por grapas/parafusos ancorados; solda em chapa aparente ancorada só com execução controlada; verificar aquecimento do concreto e perda de aderência; evitar deformação localizada das chapas.
- **Elastômero** (Anexo A informativo): pressão ≤ 7 MPa (simples) e ≤ 11 MPa (cintado) (conferir na 2017); deformação de compressão em serviço ≤ 15% (usar dados experimentais por dureza e fator de forma); distorção por cisalhamento ≤ metade da altura total; para permanentes usar G = metade do G de cargas de curta duração. Sem proteção acima de 80 °C, prever substituição após incêndio. Em protendidos com grande encurtamento, permitir levantar a peça para aliviar a almofada.
- Checklist do aparelho de apoio [ND]: espessura × deslocamento horizontal (retração/térmica/fluência), giro da viga × compressão mínima (não descolar a borda), deslizamento (μ × N mínimo), distância à borda do consolo, fretagem do concreto sob o apoio. Regras construtivas [fib] em 13.4.

### 4.4 Ligações viga × pilar [Iria + ND]
- Classes: isostáticas (rotuladas), semirrígidas e rígidas/engastadas; hiperestáticas só com momento negativo (armadura de continuidade na capa) ou também com positivo no apoio (solda/chapas/luvas).
- Exemplos típicos: consolo + elastômero + chumbador em furo grauteado (rótula com travamento lateral); dente Gerber; chapa soldada; luvas/barras rosqueadas; continuidade pela capa. Classificação pelo fator de restrição αR e método Beam-Line: ver `projetos-estruturais-concreto-armado-protendido` seção 10.
- [fib] Ligação com chumbador não é rótula perfeita: é semirrígida (rotação limitada no ELU), mas o usual é desprezar e projetar como articulada. Detalhes de nicho, furo e chumbador em 13.6.

## 5. Detalhamento — o que todo projeto de produção deve ter
### 5.1 Itens imprescindíveis [Iria]
1. Fôrma da peça com todas as cotas: vista lateral, superior e cortes.
2. Locação e dimensão de alças de içamento e furos de montagem.
3. Armadura com dobras e resumo de aço **por peça**.
4. fck do concreto e fck mínimos para desforma, desprotensão e montagem.
5. Ligações: insertos para solda, chumbadores, locação dentro da peça, ancoragem.
6. Identificação (marca) da peça e quantidade de repetições.
7. Protendido: força por cabo e alongamento esperado.
- O pré-fabricado exige **nível de detalhamento elevado**: furos pequenos, embutidos de SPDA, eletrodutos, inserts de fachada, interferências com instalações — tudo no desenho, nada "resolvido na obra". [Iria]
- [fib] Detalhar região de ligação em escala ampliada sempre que houver suspeita de congestionamento (insertos + armadura de fretagem + tirante + estribos) e conferir espaço para vibrar/lançar o concreto.

### 5.2 Checklist ND por tipo de peça [ND]
- **Pilar**: comprimento total incluindo embutimento; consolos (cota de topo, a/d, armadura do tirante, costura, ancoragem em laço/chapa); chumbadores e furos para pinos de viga; chave de cisalhamento na base se rugosa; emenda (luva/chapa) se multipavimento; içamento com virada (verificar flexão na fase de giro e ponto de pega); calhas/condutores embutidos; consoles de ponte rolante; marca de prumo e nível. [fib] seção mínima 300 mm (ligações + ~2 h de fogo), arestas chanfradas, peça única até 20–24 m; consolos em várias faces → ver 13.5 (alturas defasadas ≥ 50 mm ou consolo em 2ª etapa).
- **Viga (retangular, I, T invertido, L)**: dentes Gerber (tirante, suspensão, costura, biela); furos de pino e elastômero; armadura de costura para capa; cobrimento e fretagem nos apoios; contraflecha esperada (protendida) e flecha de serviço; inserts de travamento lateral; estabilidade lateral de vigas esbeltas no içamento e montagem. [fib] nicho vertical 50×80 mm na extremidade para chumbador; vigas de borda com torção (laje de um lado) → ligação resistente à torção por binário (barras parafusadas/solda).
- **Laje alveolar**: paginação (planta LA 001…), cortes e recortes, aberturas, alvéolos preenchidos nos apoios, apoio mínimo, armadura de capa e de ligação, graute das juntas longitudinais, tirantes de diafragma; NBR 14861 (conferir edição vigente). Regras [fib] em 13.8.
- **Terça/telha W/cobertura protendida**: cabos, pontos de içamento, fixação, inclinação/caimento, calhas, juntas, ancoragem contra sucção de vento (NBR 6123).
- **Painel de fachada**: inserts de fixação (de suporte e de restrição), juntas e selantes, armadura de içamento e virada, acabamento (textura, cor, agregado exposto), painel sanduíche (conectores); NBR 16475 (conferir). Regras [fib] em 13.11–13.12.
- **Bloco/cálice pré-moldado, estaca**: tolerância ±5 cm em planta, nivelamento, graute; estacas pela NBR 6122 e emendas.
- **Escada/arquibancada**: apoios em dente, vibração, juntas de dilatação, drenagem.
- **Geral**: cobrimento por classe de agressividade (NBR 6118 + redução admitida para controle rigoroso, conferir), CAA, peso da peça na prancha, centro de gravidade, tabela de insertos, sequência de montagem e escoramento provisório.

## 6. Produção — pontos para consultoria na fábrica [ND]
- Controle de concreto (NBR 12655) com resistências por idade (desforma, desprotensão, transporte); curva de cura térmica (taxa de aquecimento, patamar, resfriamento) conferida por corpos de prova curados junto com a peça.
- Pista de protensão: aferição de macaco/manômetro, ΔL teórico × medido (tolerância conforme norma — conferir), sequência de desprotensão simétrica, verificação de fissuras na transferência.
- Fôrmas: estanqueidade, tolerâncias dimensionais, desmoldante, rodízio e reaproveitamento.
- Armação: conferência de bitolas, cobrimento com espaçadores, posição de insertos (gabaritos).
- Rastreabilidade: marca da peça, data, lote de concreto e aço, inspeção liberatória (checklist assinado), RNC.
- Lean/5S/Kaizen/TPM aplicados a setups de pista e fôrma (experiência de Nathan na Luke Concreto).
- Estocagem: apoios nos pontos previstos em projeto, empilhamento máximo, calços alinhados verticalmente.
- Regras de projeto que facilitam a produção [fib] em 13.7.

## 7. Transporte e montagem [ND]
- Plano de rigging/içamento por peça crítica (peso, raio, capacidade, cintas/balancim, ângulo de lingas), NR-11/NR-18 e NR-35.
- Sequência de montagem garantindo estabilidade provisória (escoras, travamentos, contraventos temporários) até grautear/soldar as ligações.
- Conferência topográfica antes (locação de cálices/blocos) e durante (prumo, nível dos consolos) pelas tolerâncias da seção 4.1.
- [fib] Ligação boa de montar: peça içada, posicionada e desenganchada rápido; travamento provisório simples e independente do clima; evitar ligações que exijam deslocar a peça na horizontal já na posição final ou içar inclinada; parafusos/soldas acessíveis para executar e inspecionar; não empilhar mais de 2 peças pré-moldadas uma sobre a outra no mesmo apoio (estabilidade na montagem).

## 8. Qualidade, segurança e meio ambiente [ND]
- NBR 9062 (controle de qualidade e inspeção) + Selo de Excelência ABCIC como referência de mercado (conferir requisitos atuais).
- Indicadores sugeridos para a fábrica: m³/dia por pista, índice de retrabalho, % de peças com RNC, perda de concreto e aço, aderência ao prazo de entrega, acidentes.
- [fib] Garantia da qualidade em 4 pilares: mão de obra; instalações/equipamentos; matéria-prima e processos; controle de execução (autocontrole com ou sem 3ª parte, registros disponíveis ao cliente).

## 9. Contratação — orientar o cliente final [ND]
- Escopo claro: projeto (quem é o RT), fabricação, transporte, montagem, grauteamento, solda de ligações, capa, impermeabilização/selantes de juntas, fundações e cálices (pré-moldados ou moldados no local?), elastômeros, inserts de terceiros.
- Interfaces: fundação × pilar (cota de arranque, tolerâncias), arquitetura × modulação, instalações × furações (congelar antes da produção), cobertura metálica × pré-moldado.
- Prazo realista: projeto executivo e aprovação → produção → montagem; liberar produção só com projeto aprovado e furações congeladas. [fib] Instalações embutidas (eletrodutos, caixas, condutores pluviais no pilar, nichos) exigem projeto complementar definido ANTES do usual — vender isso como vantagem (antecipa decisões) e cobrar o congelamento.
- [fib] Permitir ao fabricante materiais/métodos alternativos de ligação desde que atendam o projeto (gera ligações mais econômicas).

## 10. Patologias e problemas recorrentes [ND]
- Fissura em consolo/dente por armadura de tirante mal ancorada ou carga excêntrica; esmagamento de borda por elastômero mal posicionado.
- Contraflecha excessiva/diferencial entre peças protendidas vizinhas (afeta capa e piso).
- Junta de laje alveolar fissurada por falta de graute ou de tirantes de diafragma.
- Corrosão em insertos/soldas expostos sem proteção; selantes de fachada vencidos.
- Pilar fora de prumo por graute de cálice sem cura antes de carregar.
- [fib] Lascamento do concreto em volta de chapa embutida soldada na obra (sem folga de 2 mm); almofada faceando a borda do apoio (lasca a borda); laje alveolar com água congelada/acumulada nos alvéolos (fazer furos de dreno na face inferior); painel de fachada empenado por ligação que impede movimento térmico; corrosão galvânica por contato entre metais diferentes.

## 11. Roteiro de consultoria ND
1. Diagnóstico da fábrica pelos 6 M's (seção 1) + indicadores (seção 8).
2. Revisão de projeto da peça/obra: sistema de estabilidade, fases transitórias (seção 3), ligações (seção 4 e 13), checklist de detalhamento (seção 5 e 13).
3. Revisão de processo: produção (6), transporte/montagem (7).
4. Relatório com não conformidades, item de norma, risco e ação recomendada; para o cliente final, orientação de escopo e interfaces (9).

## 12. Armadilhas
- Citar item da NBR 9062:2006 como se fosse da 2017 (numeração mudou).
- Citar valor [fib]/Eurocode como se fosse NBR (ex.: contato a seco 0,3 fcd do EC2 × 0,042 fcd ≤ 1 MPa da NBR).
- Dimensionar só a seção final e esquecer saque/montagem.
- Projetar peça intransportável ou acima da capacidade do guindaste no raio real.
- Deixar furação/embutidos para "resolver na obra".
- Apoio a seco acima de 1 MPa ou elastômero sem verificar deslizamento e giro.
- Comprimento de apoio sem somar tolerâncias e distâncias não efetivas (13.3).
- Ligação sem ajuste nas 3 direções ou furo justo (sem folga) para chumbador/parafuso.

## 13. Manual fib (Van Acker 2002 / ABCIC 2003) — detalhamento, insertos, folgas e furos [fib]

### 13.1 Princípios de projeto de ligações
- Ligação = conjunto: dispositivo + junta + material de preenchimento + superfície de interface + **zona de extremidade das peças** (armar para as forças que o dispositivo introduz). Não é escolher item de catálogo.
- Critérios: resistência (incluir ações indiretas: retração, fluência, temperatura, desaprumo; e excepcionais), deformabilidade/ductilidade, durabilidade, fogo, tolerâncias, fabricação, transporte e montagem.
- **Variação volumétrica**: ou deixar a ligação deslizar/girar ou projetá-la para a força de restrição; na prática intermediário (alguma deformabilidade no eixo da viga). Fachada ligada no meio do vão de viga/laje → detalhe deve permitir a flecha (furo oblongo/deslizamento) ou funcionar como rótula.
- **Projeto "equilibrado" por ductilidade**: eleger o elo dúctil (ex.: barras de ancoragem) e dimensionar todos os outros elos (ancoragem no concreto, cantoneiras, solda, barra de ligação) para a capacidade ÚLTIMA do elo dúctil, não para o escoamento.
- **Ajuste nas 3 direções** em toda ligação (ex. Fig. 4.2: z por trilho de ancoragem, x por calços metálicos entre cantoneira e trilho, y por furo oval na cantoneira).
- Mecanismos de transferência: encaixe (cálice; consolo metálico oculto em recesso da viga, preenchido com epóxi), traspasse/laços (com barra transversal dentro dos laços quando falta comprimento), pino/chumbador, aderência (só tensões baixas — capa), atrito/atrito-cisalhamento, chaves de cisalhamento (exigem tirante no topo e base da junta ou laços ao longo dela), chumbadores rosqueados/luvas/trilhos, solda, pós-tensão.
- Fogo: ligação vital deve ter a mesma proteção ao fogo que as peças (cobrimento com concreto in loco ou material isolante); apoios laje-viga e viga-pilar em geral dispensam cuidado; almofada de elastômero normalmente não precisa proteção (sua perda não colapsa a estrutura); juntas de paredes/pisos devem barrar chamas e gases quentes.
- Durabilidade: metais expostos com proteção permanente (epóxi/antiferruginoso ou cobrimento de argamassa/concreto); ligação sem manutenção possível → vida útil ≥ da estrutura, preferir **inox**; evitar contato entre metais diferentes (corrosão galvânica — usar arruelas/luvas isolantes).

### 13.2 Tolerâncias e folgas
- Tolerância total = produção (dimensão, forma, esquadro, curvatura de protendidas, posição de insertos) + marcação/locação no canteiro + montagem (posição e alinhamento). Discutir tolerâncias com o fabricante já no anteprojeto.
- Desvios se concentram nas ligações → absorver via comprimento de apoio, almofadas, furos ampliados/oblongos, trilhos, calços.
- Considerar curvaturas e **diferenças de contraflecha** entre peças protendidas vizinhas e movimentos (retração, térmica).
- Folgas práticas citadas: peça × estrutura moldada no local / fachada × estrutura **≥ 25–30 mm** (não visível; pode ser tão larga quanto a montagem exigir); **2 mm** de folga em volta de chapa embutida a ser soldada na obra (evita lascar o concreto pela dilatação da chapa); largura real da laje alveolar 3–6 mm menor que a nominal (1196 mm para 1200) para não acumular largura no pano; furos de chapa de base de pilar sempre ampliados; "tolerâncias garantidas por meio de orifícios maiores no elemento a ser conectado" (chumbadores).
- Excentricidades de montagem (CEB-FIB MC78) para paredes/pilares sobrepostos: desaprumo e_p = 2l/1000 a 3l/1000; posicionamento e_m = 5 mm (peça inferior visível na montagem) ou 10 mm (não visível).

### 13.3 Comprimento nominal de apoio (EC2)
- a = a1 + a2 + a3 + √(Δa2² + Δa3²)
  - a1 = comprimento da almofada pela tensão de contato (b1 = largura).
  - a2 = trecho não efetivo na borda do elemento SUPORTE: 10–15 mm (apoio linear de laje); 10–25 mm (apoio concentrado de viga em pilar/consolo).
  - a3 = trecho não efetivo na extremidade do elemento APOIADO: 5–15 mm.
  - Δa2 = tolerância de distância entre apoios = vão/1200; Δa3 = tolerância de comprimento da peça = comprimento/2500.
- Exemplo conferido: viga 15 m em consolo, almofada a1 = 150 mm, a2 = 20, a3 = 10 → Δa2 = 12,5; Δa3 = 6,0; √ = 13,9 → a ≈ 194 → **adotar 200 mm**.
- Valores indicativos (Tabela 4.26; "=" no original = ≤/≥):

| Elemento apoiado | Apoio | Condição | a nominal |
|---|---|---|---|
| Laje alveolar | concreto/aço | h ≤ 250 / > 250 mm | 60–70 / 100–130 mm |
| Laje alveolar | alvenaria | h ≤ 250 / > 250 mm | 100 / 120 mm |
| Pré-laje (placa) | concreto | com / sem escoramento | 30 / 50 mm |
| Pré-laje (placa) | alvenaria | com / sem escoramento | ≥ 40 / ≥ 50 mm |
| Laje com vigotas | concreto/aço · alvenaria | — | 85–100 · ≥ 100 mm |
| Laje nervurada (TT) | concreto | — | 150 mm |
| Viga secundária de cobertura | concreto | L ≤ 15 m | 140 mm |
| Viga de piso | concreto | L ≤ 8 m · 12–20 m | 200–230 mm (faixa) |
| Viga de cobertura | concreto | L ≤ 24 m · ≤ 40 m | 195 · 225 mm |

- Pisos (Tab. 6.25, estágio inicial): sobre viga de aço/concreto — alveolar 120–400 mm: 70–130; TT com carga alta: 75–150; pré-laje: 70; vigota: 100. Sobre alvenaria — alveolar: 100–150; pré-laje: 100; vigota: 125 (mm). TT com carga alta → usar o máximo e apoiar nas almas (mesmo com chapa de topo saliente).
- Laje alveolar sem almofada sob carga leve (residencial) pode apoiar direto; nos demais casos usar almofada (neoprene cintado, argamassa, fibrocimento).

### 13.4 Juntas de compressão e almofadas
- Juntas de argamassa 10–30 mm; de concreto 30–50 mm (pilares/paredes; às vezes laje-viga; raramente sob viga).
- Junta "dura" pilar/parede (DIN 1045): capacidade governada pelas peças, não pela junta, se r_c = fc,argamassa / fc,peça ≥ 0,5 e r_th = espessura/largura da junta ≤ 0,7 (juntas confinadas por concreto estrutural atendem sempre) (conferir leitura dos sinais).
- Almofada de elastômero: 2–20 mm; mais espessa para liberar giro e deslocamento; acima de certa espessura/carga usar cintado (chapas intercaladas). **Não facear a borda** do suporte nem da peça (evita lascar); a viga deve girar sem encostar a face inferior na quina do apoio. Almofada alta reduz muito a capacidade do chumbador (pino trabalha com braço maior) → evitar almofadas muito altas onde há pino.
- Tração transversal (fendilhamento): junta rígida (E ≥ ~70% do concreto) concentra força; junta mole expande lateralmente → armadura de fretagem nas peças adjacentes.

### 13.5 Consolos de concreto
- Geometria (Fig. 4.28): a0 ≤ d (recomendado 0,4d–0,6d); altura na face externa h1 ≥ 0,5h; balanço l ≤ 0,7h (usual 0,5h) — **padronizar l = 300 ou 400 mm**.
- Bielas e tirantes (EC2 6.5 / BS 8110 5.2.7): 1,0 ≤ tg θ ≤ 2,5. Força horizontal sem cálculo melhor: **Hd = 0,15 Nd** (fib) — NBR 9062 define Hd em função do tipo de apoio (conferir 2017, ex. 0,16 Fd com elastômero); somar ações de montagem/ponte rolante.
- Ancoragem do tirante além da linha de carga: solda em barra transversal na borda OU laço/"U" horizontal no topo; tirante de consolo simples ancorado na face oposta do pilar e traspassado com longitudinais; consolos opostos ligados pelo mesmo tirante. Barras Ø < 25 mm (tensão de contato na dobra).
- Região perturbada no pilar (Elliott): 1,5h acima do topo do consolo e 1,5h·cos θ abaixo da base — armadura adicional nessa faixa.
- Consolos em várias faces no mesmo nível: congestionam → **defasar cota de topo ≥ 50 mm** ou usar inserto metálico para o tirante. Tipo "cruz" (4 faces em peça única) é difícil de fôrma/armação → preferir 4 consolos simples.
- Produção: consolo numa só face fica na face de cima da fôrma (fôrma padrão). Várias faces → **concretar em 2 etapas**: pilar com luvas rosqueadas ancoradas na posição do consolo + recesso ±20 mm (ou retardador para expor agregado); após desforma, rosquear tirantes, montar estribos e concretar o consolo dias depois.
- Consolo metálico oculto (estética, sem saliência): inserto no pilar encaixado em recesso/caixa na extremidade da viga, preenchido com graute/epóxi; ou chapa deslizante em caixa na viga encaixando em caixa no pilar.

### 13.6 Chumbadores, nichos, furos e solda
- Viga–pilar padrão: chumbador/parafuso saindo do topo do pilar ou consolo + **nicho vertical 50×80 mm** na extremidade da viga + almofada; nicho grauteado após montagem (pino trava horizontal). Para **liberar movimento** (junta/apoio deslizante): nicho com material betuminoso/plástico (não grautear) + chumbador rosqueado com porca no topo da viga para estabilidade.
- Pino: resistência depende de Ø e fck; cai muito com afastamento entre peças (almofada alta); armadura de fendilhamento em volta conforme distância à borda; ancorado por aderência/gancho soma atrito-cisalhamento.
- Tipos de fixação por tração: parafuso em inserto, barra rosqueada ancorada, "para-bolts", acopladores mecânicos, trilhos (anchor rails), chapas ancoradas. Tolerância por furo maior/oblongo na peça a conectar.
- Fachada em laje (Fig. 4.16): trilho vertical + furo oval na cantoneira + calços = ajuste 3D. Versão soldada (4.17): cantoneira soldada entre chapa do painel e cantoneira da borda da laje, com **folga de 2 mm** em volta das chapas embutidas.
- Solda: direta em barras salientes, ou peça intermediária soldada em barras/chapas/cantoneiras embutidas (ancoradas por aderência ou mecanicamente). Na Europa pouco usada na obra (qualidade de mão de obra/clima); preferir parafusada quando possível. Proteger contra corrosão após solda.
- Pilar–pilar e pilar–fundação: barras em **bainhas grauteadas** (bainha com folga para o graute) ou chapas/cantoneiras soldadas à armadura + parafusos (furos ampliados).
- Barras salientes atrapalham estocagem e carga do caminhão → substituir por **luvas rosqueadas embutidas** + barra rosqueada colocada na obra.

### 13.7 Regras de produção para o projetista
- Evitar **furos na fôrma** (trabalhosos e reduzem vida da fôrma): saliências/esperas só pela face superior de concretagem.
- Minimizar itens embutidos, sobretudo na face superior (difícil fixar com precisão); chapa no fundo ou na lateral da fôrma fica precisa.
- Itens padronizados, de mais de um fornecedor; detalhes semelhantes **idênticos** mesmo com pequeno excesso de cálculo; repetição reduz preparo de fôrma e erro.
- Detalhes **à prova de erro** (só encaixa na posição/orientação correta).
- Esperas para traspasse na face superior da fôrma; mesmo tipo de ancoragem em toda a fachada.
- Posicionar detalhes de modo a reduzir tempo de serviço; descrição simples do projeto; mudanças não previstas prejudicam o planejamento da produção.

### 13.8 Pisos pré-moldados
- Tipos (Tab. 6.1 — vão máx · espessura · largura · peso): alveolar 20 m · 120–550 · 1200 · 2,0–4,8 kN/m²; TT 24 (30) m · 200–800 · 2400 · 2,0–5,0; pré-laje 7 m · 100–200 (total) · 600–2400; vigota ~6–7 m (vigotas a 0,4–0,8 m). Modulação 300 mm; larguras 600/1200/2400 (TT real 2390; também 3000).
- Alveolar: vazios 30–50%; até 20 m; pista 80–150 m; alveolar 400 mm vence ~17 m e 500 mm ~21 m com 5 kN/m²; bordas perfiladas para cisalhamento na junta grauteada (graute não retrátil).
- Recorte junto a pilar: até **1/3 da largura** da laje sem problema; fazer juntas longitudinais coincidirem com pilares; preferir vigas mais largas que pilares (lajes com ponta reta).
- Vão < 2 m: protensão pouco efetiva → armadura passiva ou moldar no local (também em cantos triangulares).
- Aberturas na alveolar (comprimento/largura, mm): HC 180–300 — canto 600/400, frente 600/400, borda 1000/400, quadrada central 1000/400, circular central deixando nervura mín. 20 mm; HC 400 — canto 600/300, frente 600/200, borda 1000/300, quadrada 1000/200, circular Ø135. Maiores → apoio indireto com cantoneira/"chair" metálico ou viga moldada no local, com tirantes periféricos e internos ao redor.
- TT: **nunca abrir furo vertical nas almas**; furos circulares na alma só acima da armadura ativa. Aberturas (l/b, mm): TT-2400 centro 1000/630, borda 1000/320, canto 1000/320; TT-3000 centro 1000/930, borda 1000/460, canto 1000/460.
- Drenagem: furos na face inferior para escoar água dos alvéolos (umidade/frio).
- Punção alveolar (ensaio, carga em 100×100 mm, resistências típicas): perímetro de controle a 2h da carga, só almas contam; valores 20–80 kN conforme espessura (150/200 → 270 → 320/400 → 500) e Ø do alvéolo — conferir com o fabricante.
- Cisalhamento crítico em alveolar < 3 m ou com cargas concentradas/lineares; sobre viga flexível há tensões transversais → fib Bulletin 6. Alveolar não recomendada em balanço direto (só com capa ancorada em alvéolos abertos preenchidos + armadura).
- Distribuição transversal de carga concentrada (simplificado): largura efetiva = 3 lajes ou L/4 de cada lado; requer juntas grauteadas e deslocamento lateral impedido (tirante transversal ≥ força total de cisalhamento nas juntas). Lajes com vigotas: fatores Tab. 6.21 (capa armada, vigotas ≤ 800 mm).
- Tirantes: periféricos dentro de **1,2 m da borda**, contínuos nos cantos; longitudinais nas juntas (ancoragem **1,0–1,5 m**) ou em alvéolos abertos/bainhas grauteadas (**0,6–0,8 m**), colocados a **meia altura** da laje (não no topo — gera momento de restrição; nem no fundo — pior para integridade). TT: esperas da viga ou solda; capa: tela sobre vigas internas traspassando esperas.
- Diafragma: cisalhamento médio nas juntas longitudinais ELU ≤ 0,1 N/mm² (cap. 3) — o cap. 6 cita 1,5 N/mm² para atrito-cisalhamento no ELS (valores conflitantes no manual; usar o menor no pré-dimensionamento e verificar pela NBR). Capa só quando necessária (ação composta, cargas concentradas altas, empilhadeira, sismo) e sempre com tela.
- Pré-laje treliçada: escoramento a cada 1,5–3,5 m (depende do banzo superior); banzo serve de armadura negativa.
- Laje alveolar engastada sob paredes (carga alta): apoiar em consolo, juntas parcialmente preenchidas ou **extremidades chanfradas** (+ neoprene 4 mm) para não gerar momento negativo não previsto.

### 13.9 Esqueleto e galpões — faixas de dimensões
- Traves planas (galpão): pilares engastados + viga de cobertura em chumbadores; espaçamento entre traves 6 m (concreto celular), 6–9 m (alveolar), 9–12 m (nervurada); viga principal 12–(18–32)–45 m; viga secundária 4–(8–12)–12 m; viga primária 12–(12–18)–24 m; pilar 4–8–20 m (mín–ótimo–máx). Duas águas em TT: 9–32 m (galpão até 32 m, módulo 2,4 m, pé-direito até 8 m).
- Viga principal de cobertura **direto no topo do pilar**; vigas primárias (longitudinais) em consolos → evita 3 peças empilhadas e facilita montagem. Viga de borda pode ocupar só meio topo do pilar (ampliação futura).
- Vigas de cobertura de altura variável (I, inclinação 5–12%): b 250–300 / h 800–1400 / alma 80–120 / 10–25 m; b 300–400 / h 1200–2000 / 15–25 m; b 300–500 / h 1300–2500 / 25–40 m. I reta 10–35 m. Retangular b 300–600, h 400–800, vão 4–14 m (normalmente com dente para esconder consolo). Shed 15–28 m. Terças 6–12 m, h 250–600.
- Vigas de piso L/T invertido: L 4,8–14,4 m; h 350–380 (até mais); b 200–500; aba b1 100–150, h1 150–200 mm. Desnível > ~750 mm → duas vigas L costas com costas com pequena folga (atenção aos tirantes transversais). Viga L da largura do pilar é preferível (laje sem recorte).
- Esqueleto multipavimentos: viga 5–(≤ 9,6)–14 m; laje 6–(7–14)–18/20 m; pilar 3–4 / 6–12 / 20–25 m (pilar contínuo até ~4 pavimentos); grade exemplo 6,00 × 9,60 m.
- Juntas de dilatação no diafragma a cada ~80 m (planta retangular) ou ~60 m (não retangular); executar duplicando pilares/vigas ou com almofadas deformáveis + junta com argamassa semiplástica/betume.

### 13.10 Integridade estrutural (tirantes)
- Rede 3D de tirantes (Fig. 3.14: centrais e de extremidade de piso, de borda, piso–parede, continuidade de vigas internas, periféricos, de canto, pilar–viga, verticais em pilares e paredes) em faixas de concreto in loco, bainhas ou juntas; contínuos por traspasse, luva rosqueada ou soquete.
- Valores citados (ELU, EC2 simplificado — conferir EN 1992-1-1 e NBR 9062:2017): periférico F = l·10 kN/m ≥ 70 kN; interno F = (l1 + l2)·20 kN/m ≥ 70 kN; vertical (BS 8110): cada pilar/parede contínuo da fundação à cobertura, resistindo à tração da maior reação de cálculo (G+Q) de um pavimento.
- Colapso progressivo: caminhos alternativos (balanço de paredes adjacentes, suspensão por tirantes verticais, catenária de vigas de amarração, impedir queda de lajes — tirantes longitudinais a meia altura).

### 13.11 Painéis estruturais e paredes
- Espessuras (Tab. 7.1): estrutural com laje 2 direções 180–240 mm; 1 direção 150–200; não estrutural 80–150 (180); poço de elevador/escada 180–200. Altura = pé-direito ≤ 4,20 m (exc. 4,50, limitado por transporte); comprimento 2,40–14 m.
- Aberturas (Fig. 7.18): montante de borda **≥ 0,20 m**; montante entre aberturas **≥ 0,30 m**; verga **≥ 0,30 m**.
- Modulação: B (vão de laje) 4–(6–12)–14 m em n×3M/n×6M; C 2,40–(3,6–6)–12 m em n×6M/n×12M; H 2,60–3,30 m.
- Junta horizontal parede–laje alveolar: preencher em 2 etapas ou graute líquido de uma vez (base do painel um pouco abaixo do topo da laje). Resistência (VTT): ponta reta N_Rd = 0,5·fcd·b_j·L_j (b_j = min{b_w, b_argamassa}); ponta chanfrada N_Rd = 0,6·fcd·b_w·L_j — desde que haja barra Ø16 horizontal em cada borda do painel junto à junta e estribos Ø8 a cada ≤ 200 mm.
- Excentricidades: laje sem almofada → reação a 1/3 do apoio; com argamassa/almofada → centro. Desaprumo θi = θ0·αh·αm (θ0 = 1/200) ou simplificado H = 1% da vertical do andar, mín. 30 kN/m por painel.
- Juntas verticais de cisalhamento: faces dentadas (chaves) + tirante concentrado na junta horizontal (preferível a laços na vertical); parede dupla (2 placas ≥ 40 mm, afastadas 70–100 mm, treliças a ~0,6 m, núcleo concretado na obra).

### 13.12 Fachadas arquitetônicas
- Painel ≤ 10 t (içamento usual de fábrica; conferir raio do guindaste nos cantos); para transporte, uma das dimensões ≤ 3,60 m; largura em múltiplos de 300 mm; altura = pavimento; eixos modulares do lado de dentro da fachada.
- Espessura de elemento estrutural entre h/10 e h/15 da altura (conforme manual, conferir); sanduíche: camada externa 70–90 mm, interna 120–160 mm; isolamento 50–150 mm.
- Conectores do sanduíche: de apoio (peso + vento), de torção, espaçadores (sem restringir movimento lateral) — camadas até ~100 mm de afastamento; ou armadura diagonal inox (isolamento ~150 mm) a cada 600–1200 mm + barras no perímetro.
- Fixadores: ajustáveis nas 3 direções; inox AISI 316 ou bronze/cobre para peças não embutidas; arruelas sintéticas, espaçadores e **furos ampliados** para movimentos térmicos; folga fachada–estrutura ≥ 25–30 mm. Tipos: esperas traspassadas com concreto in loco (tolerância grande, barata, durável, mas precisa escora provisória), parafusadas (trilho + parafuso M12, cantoneira com 3 graus de ajuste), soldadas (chapa faceada com o concreto; ex. chapa 100×8×100).
- Movimentos: ΔT de projeto 60 °C (fachada/cobertura, montagem acima de 0 °C) e 40 °C entre camadas do sanduíche; superfície de -20 a +60 °C (escura).
- Juntas seladas: largura efetiva 8–30 mm; selante (PU/silicone) deforma até 25%; largura mínima nominal por largura do painel: 1,8 m → 12 mm; 2,4 → 12; 3,6 → 14; 4,8 → 15; 6,0 → 16 mm; selante um pouco recuado; bordas sem retardador. Junta drenada (2 estágios): chicana + câmara de expansão na vertical, **dente de 50–70 mm** na horizontal, rufo no cruzamento, selante de ar por trás.
- Revestimento incorporado: cerâmica ≤ 300×300 mm só aderência; pedra natural exige conector inox + camada não aderente (dilatação diferente).