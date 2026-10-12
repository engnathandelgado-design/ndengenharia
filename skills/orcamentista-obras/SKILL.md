---
name: "orcamentista-obras"
description: "Orçamento executivo e cronograma de obras pelo método ND (EAP em células, MAT/MOE separados, indicadores de produtividade). Use para orçar, reorçar, equalizar ou planejar obra a partir de projetos ou planilha de licitação."
---

# Orçamentista de Obras — método ND Engenharia

Método aprendido do orçamento executivo de referência "CTN-NOV-DMS Orçamento Executivo R04" (Domus 544, Florianópolis/SC, 5.008,85 m², 23 pav.). Serve para obra privada (custo real MAT + MOE) e para obra pública (planilha de licitação SINAPI/SICRO + BDI), e sempre termina com cronograma físico-financeiro e checagem por indicadores.

## 1. Antes de orçar — levantar com o Nathan
Pergunte só o que não estiver nos documentos:
1. Base: orçar do zero pelos projetos, revisar uma planilha existente (licitação/contrato) ou orçar só o saldo a executar.
2. Referência de preço: SINAPI (UF, mês, desonerado ou não) + BDI, ou custo real de mercado (MAT/MOE).
3. Situação da obra (não iniciada, parada em X, em andamento — % por etapa) e data de início/reinício.
4. Prazo contratual, se houver. Sem prazo, calcule pelo indicador de produtividade (seção 6).

## 2. Estrutura da planilha (EAP em 4 níveis)
Hierarquia com código `CC.EEE.SSS.III`:
- **CÉLULA CONSTRUTIVA** (01, 02…) → **ETAPA** (01.001) → **SUBETAPA** (01.001.001) → **SERVIÇO** (01.001.001.001).
- Colunas: Item | Descrição | Unidade | Quant. | Preço un. | Total | Considerações (premissa/origem do quantitativo) | Situação (A orçar / Cotado / OK / Finalizado).
- Totais de etapa/célula sempre por SOMA dos filhos (nunca digitados).
- Separar três cadernos com a MESMA EAP: **1-ADM** (terreno, taxas, projetos, consultorias, administração local, impostos/seguros), **2-MAT** (materiais e serviços empreitados com material), **3-MOE** (mão de obra de execução, prefixo "MOE - …").
- Aba **CAPA/Resumo**: dados do empreendimento (área construída, nº pavimentos, prazo, quadro de áreas por pavimento) e QUADRO por célula com Valor, % do total e **R$/m²**.

Células padrão (adaptar à obra; separar por bloco/torre quando houver):
01 Canteiro de obras (despesas administrativas da obra) · 02 Movimentação de terra · 03 Contenções · 04 Infraestrutura/Fundações · 05 Supraestrutura · 06 Alvenarias e vedações · 07 Instalações elétricas, telecom e SPDA · 08 Instalações hidrossanitárias · 09 Gás · 10 Climatização/exaustão · 11 Revestimentos de argamassa · 12 Impermeabilizações · 13 Coberturas · 14 Revestimentos cerâmicos · 15 Forros · 16 Elevadores/plataformas · 17 Pinturas · 18 Esquadrias, vidros e ferragens · 19 Revestimentos complementares (soleiras, peitoris, pisos táteis…) · 20 Telecom/CFTV · 21 Louças e metais · 22 Áreas comuns e paisagismo · 23 Limpeza final · 24 Serviços complementares · 25 Fundo de reserva (≈1% do custo direto).

## 3. Abas de quantitativo (memória de cálculo)
Uma aba por disciplina, cada linha rastreável à prancha de origem (nome do arquivo/prancha na coluna "Projetos"):
- **Resumo Estrutura**: por pavimento × elemento (pilares, vigas, lajes, escadas, blocos, baldrames): fck, concreto (m³), forma (m²), aço por bitola (kg) a partir das tabelas de aço das pranchas.
- **Fundação rasa/blocos** (regras do modelo):
  - folga lateral de escavação = 0,60 m se H ≤ 1,0 m; 1,20 m se H > 1,0 m;
  - escavação = (A+folga)·(B+folga)·(H + h adicional + lastro)·n;
  - reaterro = escavação − volume do elemento; bota-fora = (escavação − reaterro)·1,30 (empolamento);
  - lastro 10 cm (área da base × 0,10); forma = perímetro × H × n.
- **Estacas**: Ø, quantidade, comprimento, concreto = π·Ø²/4·L, escavação = concreto, bota-fora = ·1,3, taxa de aço kg/m³.
- **Laje treliçada/pré-moldada**: área por pavimento, capa (e=5 cm → m³), tela (kg ou m²).
- **Arquitetura**: alvenaria (m²) por pavimento e tipo de bloco, mochetas, encunhamento (m), vergas/contravergas (m), chapisco/reboco paredes e tetos, contrapisos por espessura, pisos/rodapés/azulejos por ambiente, forros, pinturas por sistema, esquadrias por tipo (un ou m²).
- **Instalações** (elétrica, hidro, PCI, SPDA, telecom, climatização): por GRUPO/EAP e SUBGRUPO, item a item da lista de materiais do projeto; quando não houver lista, verba por pavimento-tipo.
- **Controle tecnológico**: por grupo de concretagem — coletas = ARREDONDAR.CIMA(V/8 × 4) (4 CPs por betoneira de 8 m³), ensaios de compressão = nº CPs, módulo de elasticidade (Eci) a cada 5 pavimentos ou troca de fornecedor, laudo + ART por grupo; arrancamento de argamassa e aderência cerâmica 1 ensaio por torre/referência.

## 4. Indicadores de checagem (referência Domus — sempre comparar)
Taxas de estrutura (concreto armado convencional, edifício alto):
- aço supraestrutura ≈ 100–105 kg/m³; forma ≈ 8,5–9 m²/m³; estacas raiz ≈ 118 kg/m³.
Mão de obra (MOE, Florianópolis 2025/26, R$):
- Forma: lajes 19,9/m² · pilares 26,6/m² · vigas 38,3/m² · escadas 60,1/m². Desforma: lajes 5,6 · pilares 7,3 · vigas 10,6 · escadas 16,5 /m².
- Armação: 2,3–2,6 /kg. Concretagem (lançamento/adensamento): ≈ 420–460 /m³. Piso de concreto alisado ≈ 226 /m².
- Alvenaria cerâmica 58,8/m² · encunhamento 9,6/m · contraverga 68,9/m · mocheta 142/m².
- Chapisco parede 8,2 · teto 10,5 · reboco parede 51,5 · teto 66,1 /m². Contrapiso 209–277 /m².
- Cerâmica piso 100,3/m² · azulejo 90,3/m² · rodapé 4,1/m.
- Pintura interna completa (selador+massa+3 demãos) ≈ 23–27/m² somando etapas; externa textura + 3 demãos 40/m².
- Elétrica por m² construído: eletrodutos 9,2 · fios 21,1 · quadros 12,3 · acabamentos 10,8 · luminárias 5,8 · SPDA 1,7.
- Hidráulica por m²: água fria 8,7 · água quente 4,2 · esgoto/pluvial 14,9 · bombas/reservatórios 27 · incêndio 3,0.
- Telhado 31,3/m² · calhas/rufos 23,7/m · louças 133/un · metais 31/un · limpeza final 5,0/m².
Materiais (MAT, mesma base, R$):
- Concreto usinado bombeável 35 MPa 621/m³ (sem bomba incluída 805/m³). Aço CA-50 6,2–7,2/kg; CA-60 Ø5 7,5/kg. Tela Q-95 12,8/m².
- Forma de pilar/viga em réguas sem reaproveitamento 54–61/m²; 2× reaproveitamento 19–36/m²; madeirite naval laje 43,8/m²; escoramento metálico 32,5/m².
- Laje treliçada TR12 + EPS/cerâmica H11 68,4/m².
- Alvenaria bloco cerâmico c/ argamassa estabilizada 53,2/m²; bloco corta-fogo 102,9/m².
- Chapisco 3,3/m²; reboco interno 15,6/m² (teto 25,6); reboco externo 25,4/m²; regularização piso 14,8/m²; contrapiso 8 cm 54,4/m².
- Impermeabilização: manta asfáltica 4 mm terraço 155,5/m²; argamassa polimérica flexível áreas molhadas 99/m²; tinta asfáltica baldrames 8,6/m².
- Forro gesso liso 52,5/m²; porcelanato assentado 57–116/m²; azulejo 30×60 54,7/m².
- Esquadria alumínio + vidro 707/m²; porta madeira completa 1.050–1.325/un; porta corta-fogo P60 1.177/un.
- Bacia c/ caixa acoplada 534/un; limpeza grossa 8,2/m² + fina 5,5/m².
Pesos de referência no total (residencial alto padrão): supraestrutura ≈ 8–9%, instalações elétricas+hidro ≈ 7%, esquadrias ≈ 5%, ADM (incl. terreno) ≈ 34%, MOE ≈ 19%.
Esses preços são de mercado de Florianópolis; para outra praça/data, atualizar por SINAPI/INCC ou cotação e registrar a fonte em "Considerações".

## 5. Canteiro e despesas indiretas (fórmulas do modelo)
- Produtividade média **Pm = 49 h/m²** (edifício convencional; ajustar: obra térrea/institucional simples 30–40 h/m²).
- Nº de funcionários **NF = ARREDONDAR.CIMA(AC × Pm / prazo(meses) / 180 h/mês)**.
- Produção mensal = AC / prazo (m²/mês). Equipe administrativa ≈ 5 (engenheiro, mestre, almoxarife, técnico seg., administrativo) em obra média.
- Instalações provisórias: vestiário 1,5 m²/func; refeitório 1 m²/func; 1 bacia/chuveiro por 20 func; 1 ponto de água por 20 func; bebedouro 1 a cada 5 pav.; escritório 8 m²/pessoa; almoxarifado ≈ 100 m²; centrais de aço/forma/argamassa 15 m² cada.
- Ferramentas R$ 800/func; EPI R$ 500/func (2 uniformes).
- Mensais: energia, água, telecom, manutenção provisória (canteiro, elétrica, hidro), vigilância/monitoramento, cópias, controle tecnológico — tudo em "mês" × prazo.
- Proteções coletivas (EPC): bandeja salva-vidas, guarda-corpo, linha de vida, tela fachadeira — pelo perímetro/área de fachada.
- Locação de obra (m de perímetro) e topografia (meia diária por laje).

## 6. Cronograma
1. Derive o prazo: se não for dado, prazo = AC × Pm / (NF viável × 180). Teste 2–3 cenários de equipe.
2. Sequência lógica por célula: mobilização/canteiro → terra/contenção → fundações → supraestrutura (ciclo por pavimento) → alvenaria (inicia 2 lajes atrás) → instalações embutidas → revestimentos argamassa → impermeabilização → cobertura → contrapiso/cerâmica → forro → esquadrias → pintura → louças/metais → limpeza → entrega.
3. Duração de cada atividade = (quantidade × índice h/un ou custo MOE ÷ custo-hora da equipe) ÷ (equipe × 8,8 h/dia × 22 dias).
4. Entregar: Gantt mensal (ou semanal em obras < 6 meses), curva S física e financeira (MAT + MOE + ADM distribuídos pelo período de cada atividade), histograma de mão de obra.

## 7. Obra pública (planilha de licitação)
- Manter itens, códigos e unidades da planilha licitada; revisar quantidades contra os projetos e apontar divergência (Qtd licitação × Qtd projeto × Δ%).
- Preço: SINAPI/SICRO da UF e mês indicados (desonerado ou não), composições próprias com cotação (mín. 3) quando não houver código; BDI separado (TCU Acórdão 2622/2013 como faixa de referência).
- Se for saldo de contrato/aditivo: apontar acréscimos e supressões e o limite de 25% (Lei 14.133/2021, art. 125).

## 8. Validação antes de entregar
- Somatórios fecham por célula, etapa e total; nenhum total digitado.
- R$/m² por célula comparado com a seção 4 — explicar desvios > 30%.
- Taxas kg/m³ e m²/m³ dentro da faixa; quantidades de chapisco = reboco; pintura ≥ reboco.
- Cronograma: soma do financeiro = orçamento; histograma compatível com o canteiro dimensionado.
- Entregável em Excel com abas: CAPA, ADM, MAT, MOE (ou ORÇAMENTO único em obra pública), quantitativos por disciplina, CANTEIRO, CONT.TECNOL., CRONOGRAMA, CURVA S.