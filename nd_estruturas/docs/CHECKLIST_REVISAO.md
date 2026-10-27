# Checklist de revisão do jogo executivo — ND Engenharia

Lista única usada pelo revisor independente e pelas travas automáticas do `gerar_tudo`.
Cada correção do Nathan vira item aqui e, sempre que possível, uma checagem com ERRO no código.
Item marcado [auto] já tem checagem automática; [manual] o revisor confere olhando a folha.

## 1. Consistência (fonte única)
- [auto] Toda peça vem de um registro único por marca (seção, comprimento, armadura, cordoalha, insertos, peso, volume). Nenhum número redigitado em folha, lista, MC, 3D ou planta de cargas.
- [auto] Conferência cruzada zerada: desenho × tabela de ferros (posições, Ø, quantidade contada, comprimento ±1 cm), resumo do aço +10 %, listas, quantitativos, MC, IC01, CG01, 3D/IFC.
- [auto] Detalhes de ligação/apoio gerados do modelo; rótulos (marca de peça, neoprene, pino, consolo, nível, seção) iguais ao modelo; nenhuma marca antiga ou genérica ("vigas de cobertura", "NEO-3" onde é NEO-3C).
- [manual] Mudou seção ou armadura? Conferir tabelas e detalhamentos do projeto inteiro antes de dar como pronto.

## 2. Legibilidade
- [auto] Texto no papel: folhas de peças — cota 3,5 mm, posição N 3,5, tabelas 3,0, títulos 6, nome da peça 8; plantas e gerais — mínimo 2,5 (alvo 3,0). Setas 2,5–3 mm, afastamento ≥ 8 mm. Quem lê na fábrica são pessoas idosas.
- [auto] Zero texto sobreposto. Se não couber: dividir a folha, nunca reduzir texto.
- [auto] Seções e estribos em escala ≥ 2× a da elevação (pilar 1:50 → seção/estribo 1:25 ou 1:10); consolos, dentes e insertos 1:10/1:20; menor cota e menor espaçamento ≥ 3 mm no papel. Referência: pranchas SP301/SP302 da usina.
- [auto] PDF nítido no zoom do celular: desenho e isométricos em vetor; raster só render 3D, ≥ 400 ppi efetivos, PNG sem perda.

## 3. Plantas, cortes e organização
- [auto] Plantas de fôrmas: cada peça com nome e seção (P11 40×40; V400 I130 h120; V2xx 30×75; LA h20+5) e tabela marca–seção–comprimento–quantidade.
- [auto] Cortes: pilar abaixo do piso com embutimento no cálice cotado (comprimento, fundo, topo do cálice, graute); comprimento total junto ao nome.
- [manual] Cortes gerados da geometria: terças em perfil real (Z, não tubo), nomes reais dos pilares da linha, I130 em seção I com consolo, viga de cobertura com dente e apoio no recuo, níveis e inclinação.
- [manual] Ordem das folhas: em cada grupo primeiro a folha de localização, depois o detalhe (locação e cargas → pilares; fôrmas → vigas; CM01 → PP00 → PP0x → PP-A…; montagem → peças; EX01 no fim). Índice com página.
- [manual] Posição das escadas, aberturas e portões conferida contra a planta INTEIRA do arquitetônico (sobreposição nas coordenadas da obra).

## 4. Pilares
- [auto] Todo consolo com marca (C1, C2…) e com cota de nível/posição a partir da base e do piso, e dimensões (largura, projeção, altura na face e na ponta da mísula).
- [auto] Toda espera/barra de apoio (ex.: 2 BR-M16 + CA-L2) com comprimento embutido, comprimento livre (confere neoprene + chapa + arruela + porca + 2 fios), comprimento total, trecho roscado, tipo do ferro, cotas na seção transversal e linha na tabela de insertos; gabarito ±5 mm.
- [auto] Faces A, B, C com as alças AL-2 de CORDOALHA Ø12,7 (desforma e manuseio na FÁBRICA) cotadas, fora da platibanda; furo FI-1 (montagem na OBRA) cotado, com reforço em volta.
- [manual] Consolos e vigas de fachada não podem deixar fresta até o fechamento (placas por fora dos pilares): avaliar alinhamento à face externa com 2 cm de folga — decisão do Nathan.

## 5. Vigas e lajes
- [auto] Armadura passiva longitudinal Ø ≥ 12,5 e ≥ 2 barras inferiores.
- [auto] Cordoalha só Ø12,7 ou Ø9,5 em lajes alveolares e vigas protendidas; zero Ø15,2. "Alvéolos de 15,2 cm" (furo) não é cordoalha.
- [auto] Toda mudança de seção ao longo da viga (dente, trecho retangular/maciço, transição, seção corrente) com cota em cadeia que fecha no comprimento total e corte de cada trecho.
- [manual] Protensão: posição dos cabos na seção, isolamento por linha (quantidade, comprimento a partir da face, bainha PEAD), força no macaco, alongamento na pista de 60 m.
- [manual] Apoios com consolo com mísula onde decidido (ex.: CT-I130), neoprene real, assento cotado.
- [manual] Laje superior sem uso = laje de cobertura (NBR 6120 Tab. 10, acesso só para manutenção).
- [manual] Capa e 2º estágio: planta da armadura negativa por apoio (bainha no pilar + capa), corte do 2º estágio, chavetas, sequência de execução; folha EX01 para o cliente executar.

## 6. Placas de fechamento
- [auto] Todas as folhas de placas coloridas por fachada (paleta única A–J, hachura 60 %): vistas, tipos (faixas se o tipo aparece em mais de uma fachada), planta-chave com todas as paredes, corte típico, isométricos.
- [auto] Içamento por 4 pontos numa face com balancim em todos os detalhes de placa (desforma deitada → giro → montagem de pé), carga por ponto.

## 7. Içamento (folha IC01)
- [manual] Um quadro por tipo de peça: pilar (fábrica: alças; obra: furo), placa (4 pontos), alveolar (garra a ~0,2 L, estocagem), vigas por família (2 ou 4 alças, balancim, estabilidade lateral), metálicas. Tabela marca–peso–pontos–posição–carga–acessório–βa.

## 8. Estrutura metálica e cobertura
- [manual] Ligações 100 % parafusadas; isométricos explodidos de montagem por ligação (marca, perfil, parafusos Ø/classe/comprimento/quantidade, torque, chapas hachuradas, cotas em mm), gerados do 3D.
- [manual] Planta de enterçamento com comprimento de cada terça, transpasse, espaçamento e folgas de montagem em cadeia; furação de fabricação de cada marca (alma planificada).
- [manual] Telhas conferidas contra o manual do fornecedor (vão, inclinação, sobreposição, fixadores, clipes, dilatação, acabamentos).
- [manual] Acabamentos feitos por funileiro: seção dobrada cotada (abas, ângulos, desenvolvimento), espessura/material, posição montada, fixação e vedação, emendas, cantos em isométrico, calhas dimensionadas (NBR 10844).
- [manual] Perfis no limite de capacidade (o mais leve que passa).

## 9. Entrega
- [manual] PDFs para análise primeiro; zip com DXF + IFC só após aprovação.
- [manual] 3D republicado no mesmo link a cada revisão.
- [manual] Decisões que mudam o projeto: quadro com imagens (fontes + opções desenhadas), nunca só texto.

## 10. Itens acrescentados pela revisão independente da rev11 (26/10/2026)
- [auto] Renomeação R01 → projeto aplicada uma única vez; todo pilar citado numa tabela de apoio pertence, pela geometria, à linha/eixo daquele apoio.
- [auto] Nome do R01 só no quadro de correspondência; nunca usado onde coincide com marca do projeto.
- [auto] Densidade única do concreto: peso igual (±0,1 t) na IC01, folha da peça, PR01 e montagem; volume do quadro = resumo da folha.
- [auto] Quantidade de peças igual no título, isométrico, quadro e PR01.
- [auto] Nome da família coerente com a seção (ex.: I130 × h120) em todo o jogo, consolos e índice.
- [auto] Toda marca com geometria diferente tem elevação de fôrma própria.
- [manual] Textos dentro de imagens 3D: altura mínima e nomes atuais.
- [auto] Carimbo: revisão igual à descrição; nada de "LIBERADO" em folha com pendência que afete a peça; local e ART preenchidos.
- [auto] Nenhuma nota interna ("DEC-0xx", "decisão do Nathan") em folha do cliente.
- [auto] Pendência em decisão sinalizada em TODAS as folhas afetadas (PR01, NG01, folha da peça).
- [auto] Seções de pilar e viga sempre cotadas; concreto em cm com vírgula decimal.
- [auto] Pilar fora de eixo cotado na LOC01 a partir de dois eixos.
- [manual] Folga de montagem desenhada e cotada em todo detalhe de apoio.
- [auto] Vistas de placas com o nome atual de cada pilar.
- [auto] IC01 com todas as famílias, coluna βa e nenhum cálculo zerado.
- [manual] EX01 com planta-chave dos apoios de continuidade.
- [auto] MC, listas e quantitativos emitidos na mesma revisão das pranchas.
- [auto] Normas na versão vigente; mesma ocupação do mezanino em todas as notas.
- [auto] Bitola > Ø20 só com exceção registrada em DECISIONS.
- [manual] Placas: nicho de montagem (console/grapa) na parte superior da placa, não na inferior.

## 11. Itens acrescentados pela revisão independente da rev12 (27/10/2026)
Travas automáticas no `conferencia_cruzada.py` (rodado no fim do `gerar_tudo`), com o código da verificação entre parênteses.
- [auto] Mudança de geometria propaga em todas as saídas: volume, peso e cabeça (seção cheia × cabeça recuada) iguais na folha da peça, PR01, lista e xlsx (±0,005 m³, ±0,02 t) — registro único por marca em `registro.py` (C22; IC01 em C16).
- [auto] CS01 gerada das folhas de pilar: pilares e quantidade de cada consolo contados na geometria, tipo do consolo coerente com a posição do pilar (CP-VB nas fachadas 1/9, CP-MEZ no mezanino, CP-I120 no eixo C), sem texto genérico ("pilares do eixo A") e sem duas marcas com dados idênticos (C26, C7).
- [auto] Toda marca de peça metálica citada em nota tem linha de lista e desenho de fabricação ou linha de material (C27).
- [auto] Item de lista de uma fonte só e com uma descrição; insertos por pilar fecham com o número de pilares (AL-2 = 2 × pilares, FI-1 = pilares, pinos = consolos) e as chapas das placas embutidas no pilar fecham com as vistas (C25).
- [auto] Aparelho de apoio único por apoio: uma marca e uma dimensão de neoprene por tipo de consolo na tabela de insertos, nota, folha da viga e lista; contagem de neoprenes = número de apoios (C24; trava também na folha do pilar).
- [auto] Fórmulas do xlsx: recalculado no LibreOffice, gravado com valores, totais de volume, peso, peças e aço iguais aos da lista (±1 %); cabeçalho de todas as abas com a revisão do pacote (C23); aço por peça da lista = resumo da folha (C3).
- [auto] Detalhes das folhas de cortes (CT01–CT04) lidos do registro da peça (armadura ativa da laje, folgas); cordoalha Ø15,2 procurada em TODAS as folhas (C4).
- [auto] Nomes nas cargas de fundação e em todas as folhas = nomes do projeto pela posição; nome interno do modelo (P1C-L1) ou do R01 (P8A, P13B, P10a, "(P6, …)") só no quadro de correspondência da LOC01 (C28).
- [manual + auto] 3D × 2D nas peças espelhadas: consolo excêntrico na mesma face no isométrico, no IFC e nas faces da folha (C32 confere o IFC contra o registro; isométrico conferido a olho).
- [auto] Nenhum nome de arquivo, script ou revisão interna em folha do cliente (".json", ".py", "calc_", "r05", "rev06", "NATHAN") (C8).
- [auto] Valores únicos de projeto: folgas de montagem (da geometria do modelo), altura livre dos portões e chegada da escada — um só registro, comparado nas notas (C29).
- [manual + auto] Pendência também nas folhas de montagem (MON02 na trava C21) e quadro de decisão com imagens anexado ao pacote quando citado (ND-LET-DECISAO-VM-CANTO).
- [auto] Carimbo datado pela última alteração (rev 12 de 27/10/2026) e histórico sem lacuna (…09, 10, 11, 12) (C30).
- [auto] Folhas de detalhe de uma família logo após a folha-mãe (I120 → I120-2 → I120-3), cobertura em sequência e EX01 por último (C31).
- [auto] Largura de todo consolo igual à largura da viga que ele apoia (CP-MEZ = VM, CP-VB = VB, CP-I120 = ponta da I120, CT-I120 = mesa da TS-01), na memória e no que está desenhado em cada pilar; neoprene com borda lateral ≥ 1,5c e ≥ 3 cm (C33).
- [auto] Pendência já decidida não aparece mais em nenhuma folha (C34).
- [auto] Pilar fora da linha (cantos, PG-02/PG-04): face no plano dos vizinhos, sem fresta até as placas; portões com 5,00 m livres face a face conforme o arquitetônico; NEO-7 com a distância à borda na cabeça do pilar e na mesa da TS-01A; nenhuma folha cita a locação dos PG como pendente (C21).
- [manual] Pilar fora do eixo cotado a partir de dois eixos na LOC01 e com o quadro N·e na CG01.

## 0. Processo (27/10/2026) — vale antes de todas as seções acima
- [auto] Gate de lançamento zerado antes de gerar qualquer folha (`verificar_lancamento.py` sobre o modelo BIM): face externa de pilares, vigas de borda e consolos no plano das placas no perímetro; consolo com a largura da viga que apoia; vão livre de cada abertura igual ao arquitetônico; apoio de cada laje alveolar ≥ mínimo. O `gerar_tudo` para com código 2 se houver achado.
- [auto] Geração incremental: cada folha guarda o que leu (manifestos/); só refaz o que mudou. `alteradas.json` lista as folhas cujo desenho mudou.
- [manual] Revisão por diferença: folhas de `alteradas.json` + folhas-resumo (PR01, IC01, CS01, CG01, NG01, LOC01, listas, xlsx) + amostra de ~10 % das demais. Revisão completa só na 1ª emissão.
- [manual] Decisões do Nathan aplicadas em lote, num ciclo só; dúvidas de geometria levadas juntas num quadro, antes do detalhamento.
