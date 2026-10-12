---
name: "casos-obras-pre-moldadas"
description: "Use ao buscar referência de obra real em concreto pré-moldado (estudos de caso brasileiros: esqueleto multipiso, emendas de pilar, estabilidade, prazos e produtividade de montagem) para projeto, orçamento ou consultoria ND."
---

# Estudos de caso de obras pré-moldadas (biblioteca ND)

Biblioteca de obras reais lidas e analisadas, para usar como referência em propostas, pré-dimensionamento, orçamento e consultoria a fábricas. Complementa as skills irmãs:
- `projeto-estruturas-pre-moldadas`: concepção do sistema, estabilidade (seção 4.5 ligações semirrígidas, γz), ligações, pisos, incêndio.
- `consultoria-fabricas-pre-moldados`: NBR 9062 (cálice, apoios, tolerâncias), detalhamento por peça, produção, montagem, patologias.
- `orcamentista-obras`: custos.

Regras: valores de cada caso são de projeto da época — usar como referência, não como padrão; conferir na norma vigente (NBR 9062:2017, NBR 6118:2023) antes de usar em projeto. Medidas tiradas de desenhos em slides estão em cm e podem ter pequena imprecisão de leitura. Marcação: [fonte] = dado do material; [ND] = recomendação/lição derivada.

Ao incluir um novo caso: mesma estrutura (fonte → programa e números → concepção → peças → ligações → estabilidade → problemas de obra → como usar na ND).

---

## Caso 1 — Edifício anexo do Instituto do Câncer do Ceará (Fortaleza, 2001)

### 1.0 Fonte
Mota, J. E. (Hugo A. Mota Consultoria e Engenharia de Projetos — estrutura) e Muratori, R.; Martins, D. (arquitetura) — *Projeto da estrutura pré-moldada de edifício do Instituto do Câncer do Ceará*. 25 slides, 1º Encontro Nacional de Pesquisa-Projeto-Produção em Concreto Pré-Moldado, São Carlos, nov/2005 (feb.unesp.br/pbastos/pre-moldados, arquivo "Art. Proj. Edif. PM Ceara.pdf"). Produção/montagem: Concretópolis. Lido na íntegra em 07/10/2026 (texto + desenhos conferidos em imagem). Base normativa da época: NBR 6118:2003 / NBR 9062:1985.

### 1.1 Programa e números [fonte]
- Obra pioneira de esqueleto multipiso pré-moldado no Nordeste: pilares, vigas e lajes pré-moldadas, ~30 m de altura.
- Terreno retangular 49,00 × 14,60 m, colado em prédio existente; 7 pisos com planta livre (serviços médicos variados); demanda urgente → pré-moldado com prazo de execução previsto de **120 dias**.
- Altura total dos pilares 29,58 m; pé-direito tipo 4,025 m (um pavimento de 4,12 m; base 1,85 + 3,485 m até o bloco).
- **Laje TT 5.500 m²; vigas + painéis 2.700 m²; montagem com 6 montadores em 40 dias.**
- [ND] Produtividade derivada: ≈ 140 m² de laje/dia e ≈ 23 m² de laje/montador/dia — referência para cronograma e custo de montagem (ajustar a guindaste, raio, acesso e logística).
- Contexto de mercado: só nos anos 90 surgiram fábricas grandes em Fortaleza; antes, "não se construía em pré-moldado por falta de tecnologia, e não havia tecnologia porque não se construía". [ND] Argumento de consultoria: a fábrica precisa de obras de referência para abrir mercado.

### 1.2 Concepção estrutural — planta do pavimento tipo [fonte]
- **Sem pilares internos**: 16 pilares só nas duas fachadas longas (P1–P8 e P9–P16), eixos 1–8, vãos 7,15 / 7,15 / 5,00 / 7,30 / 7,50 / 7,50 / 7,40 m (= 49,00 m).
- Vão transversal de **14,60 m vencido direto pela laje TT de 70 cm**, apoiada nas **vigas L** das fachadas → planta totalmente livre.
- Núcleo: **pilar-parede** da caixa de escada (P17–P22) entre os eixos 3 e 4 (o vão de 5,00 m é o do núcleo).
- Contraventamento transversal (Y): **painéis de contraventamento** nas empenas (eixos 1 e 8) com **ligação rígida** aos pilares, formando "pórticos de travamento", + núcleo da escada.
- Contraventamento longitudinal (X): pórticos das fachadas + **tirantes do sistema de travamento longitudinal** na capa, no eixo central do pavimento (4Ø16 c/15 em cada vão).
- Diafragma: **capa estrutural de 8 cm armada com tela soldada**; **armadura do diafragma** (banzos) de 3Ø12,5 ao longo das vigas L em cada vão.
- [ND] Segue a filosofia do sistema: grandes vãos, poucas peças-tipo, estabilidade por elementos próprios (painéis rígidos + núcleo) e diafragma bem armado — não por nós rígidos moldados in loco.

### 1.3 Peças (dimensões dos desenhos) [fonte]
- **Pilares**: seção reduzida por trechos 70 × 100 (base) → 70 × 85 → 70 × 70 cm (topo); 29,58 m em **duas peças: trecho 1 = 21,58 m, trecho 2 = 8,00 m**, com emenda (1.4).
  - [ND] Pilar de 21,58 m: conferir transporte (AET), pontos de içamento, fissuração na desforma e no tombamento, e estabilidade montado em balanço antes do diafragma.
- **Cálice de fundação** sobre bloco de coroamento (topo do bloco −1,90 m; piso pronto ±0,00): colarinho 190 × 220 cm em planta (paredes de 45 cm), abertura interna ~100 × 130 cm para o pilar 70 × 100 (**folga de 15 cm por lado**), **embutimento 160 cm ≈ 1,6·h** (h = 100 cm), topo do colarinho 25 cm abaixo do piso pronto. Armadura do colarinho: verticais Ø16, horizontais concentradas no topo (4Ø16 + 4Ø12,5 nos 50 cm superiores) e estribos ao longo da altura.
  - [ND] Conferir embutimento (interface lisa × rugosa) e armaduras pela NBR 9062:2017 — ver `consultoria-fabricas-pre-moldados` 4.2.
- **Laje TT** protendida: largura 249 cm, altura 70 cm, mesa 5 cm; nervuras com eixo a eixo 128 cm e balanços de 61 cm; nervura ~15 cm no topo afinando para ~8–9 cm na base; **pré-tração com cordoalhas Ø12,7 mm** no talão; tela #4,2 – 15 × 15 na mesa; Ø10 na mesa "armadura para o ato da protensão" (tração no topo na liberação); estribos Ø6,3. Com capa de 8 cm: h = 78 cm para 14,60 m (≈ L/19). Apoio na viga L com extremidade da TT rebaixada (dente, 65 cm de altura no apoio).
- **Reforço com fibra de carbono**: detalhe de lâmina CF-130 (5,5 cm de largura) colada na face inferior da nervura da TT. O slide não diz o motivo. [ND] Indica peças que precisaram de reforço à flexão depois de prontas → em consultoria, reforçar controle de protensão, fck na liberação e contraflecha, e ter plano de reforço para peça fora do especificado.
- **Viga L** (borda): altura 91 cm (alma 66 + aba 25), alma ~14 cm, aba ~12,5 cm; **bainhas Ø40 mm nas extremidades** para a ligação com o pilar (pinos/chumbadores grauteados); estribos fechados na alma + estribos de suspensão na aba.
- **Painel de contraventamento** (empenas): altura 300 cm; **ligação rígida painel-pilar por binário** — no topo, ligação ao pilar trabalhando à tração T (a 25 cm do topo, ancoragem de 100 cm no painel); na base, **chapa metálica + ancoragem em laço** trabalhando à compressão C; braço ≈ 2,40 m.
- **Painel de fachada**: apoio vertical em consolo junto ao pilar/viga L; fixação com **insertos tipo trilho (Halfen) + parafuso T** no pilar e na viga. [ND] Bom padrão a replicar: ajuste nas 3 direções e liberação de movimentos.
- **Consolos com laço** (alça de aço) nos pilares para apoio e fixação das peças na montagem.
- Sequência de montagem: pilares → lajes TT (sobre vigas L) → painéis.

### 1.4 Emenda pilar-pilar — detalhe e problema de obra
- [fonte] Seção na emenda 85 × 70 cm (27,5 + 30 + 27,5 × 20 + 30 + 20); **encaixe macho-fêmea central 30 × 30 × 30 cm** para centrar o trecho superior.
- [fonte] Barras do pilar inferior entram em **bainhas corrugadas Ø40 mm × 120 cm** no pilar superior; depois **injeção de graute** pelas bainhas.
- [fonte] Sequência: posicionamento do trecho superior com guindaste + plataforma suspensa → abertura das bainhas → injeção.
- [fonte] **Problema**: o graute, mesmo sob pressão, **não teve fluidez para preencher as irregularidades entre as faces da junta horizontal**. O preenchimento total só foi garantido com **injeção de selante epóxi de baixa viscosidade**.
- [ND] Recomendações: (a) junta horizontal com espessura mínima definida (calços) e não contato concreto-concreto irregular; (b) faces da emenda planas e limpas (fôrma de topo, sem nata); (c) graute fluido/expansivo especificado e ensaiado (cone de fluidez), injeção de baixo para cima com respiros; (d) vedar o perímetro da junta antes; (e) prever no projeto e no orçamento o plano B com epóxi; (f) avaliar antes se o pilar inteiro (~30 m) é transportável e içável, evitando a emenda.

### 1.5 Estabilidade global — como foi feita [fonte]
- Pórticos nas duas direções (X: fachadas; Y: pórticos de travamento das empenas + núcleo da escada); vento no desenho ≈ 50 kgf/m² (leitura do slide — conferir).
- **NLG**: processo não incremental iterativo com matriz de rigidez geométrica e modos de flambagem global.
- **NLF**: rigidez secante, **2 iterações** ajustando as armaduras das seções críticas.
- Combinação ELU para análise não linear: **Fd = (1,4/1,1)·(Fg + Fq + 0,8·Fv)**, com γf3 = 1,1 aplicado depois sobre os esforços (procedimento da NBR 6118 para análise não linear — conferir na 2023).
- Resultados: **deslocamento horizontal máximo 3,5 cm** (H ≈ 29,6 m → ≈ H/850); **M(1+2) ≈ 1,25·M1** (≈ γz 1,25, dentro do limite prático de 1,30).
- Conclusão dos autores: os dois problemas centrais do esqueleto multipiso são **a ligação pilar-pilar (quando necessária)** e **a estabilidade global em todas as fases**; para viabilidade econômica, o projetista precisa de critérios práticos para ligações viga-pilar semirrígidas, NLF/NLG e efeitos reológicos — ver `projeto-estruturas-pre-moldadas` 4.5 e `estab_semirrigida_nd.py`.

### 1.6 Como usar na ND
- **Proposta/consultoria**: referência brasileira de edifício hospitalar de 7 pisos, montado em 40 dias com 6 montadores; argumentos de prazo e planta livre (TT de 14,60 m sem pilar interno).
- **Pré-dimensionamento**: TT 70 + capa 8 para ~15 m (≈ L/19); pilar 70 × 100 na base para 7 pisos contraventados por painéis + núcleo; cálice com embutimento ≈ 1,6h e folga de 15 cm por lado.
- **Orçamento**: separar m² de laje TT, m² de vigas/painéis, emendas de pilar (bainhas, graute, epóxi, plataforma, horas de guindaste), insertos tipo Halfen, armadura de diafragma e tirantes da capa, capa 8 cm com tela, transporte especial de pilar > 20 m e produtividade de montagem (1.1).
- **Checklist de projeto**: emenda de pilar (1.4), estabilidade em cada fase de montagem, diafragma com banzos e tirantes, ligação rígida dos painéis de travamento, apoio ajustável das fachadas.

### 1.7 Armadilhas destacadas pelo caso
- Confiar só no graute sob pressão para encher a junta horizontal de emenda de pilar.
- Pilar de ~20 m montado e solto antes de diafragma e painéis sem verificar balanço, vento de montagem e escoramento/estais.
- TT protendida sem controle de liberação/contraflecha → reforço posterior (fibra de carbono) caro e fora do cronograma.