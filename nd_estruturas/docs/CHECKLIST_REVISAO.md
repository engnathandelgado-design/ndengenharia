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
