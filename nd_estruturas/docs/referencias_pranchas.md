# Referências de apresentação de pranchas (A1) para o gerador prancha_nd

Documento de convenções extraídas de dois conjuntos de pranchas de referência, para que o
gerador de pranchas da ND Engenharia (ezdxf -> PDF) reproduza o mesmo nível de
apresentação. Registram-se apenas convenções de desenho; textos literais, logos e nomes de
responsáveis das empresas de origem não foram copiados.

Origem dos arquivos analisados:

- Conjunto 1 (estrutura metálica, escritório de cálculo): `/home/claude/letsara/ref_metalica/1129-PB-01-00{1,3,4,5,6,7,8,9}*.pdf`
- Conjunto 2 (pré-moldados de concreto + fechamento + telhado, projeto executivo de PCH): `/home/claude/letsara/ref_premoldado/*.pdf`

Todos os PDFs são A1 (841 x 594 mm), 1 página, vetoriais com fontes em curvas. O único A4 é a
guia de remessa (GRD011).

---

## 1. Conjunto 1 — estrutura metálica (projeto básico de galpão, 9 x 7 eixos, cobertura em tesouras treliçadas)

Numeração do conjunto: `NNNN-PB-01-XXX` (número do projeto, fase PB = projeto básico, disciplina 01, folha XXX), revisão `_R0X` no nome do arquivo.

| Folha | Título (carimbo) | Escala | Conteúdo |
|---|---|---|---|
| 001 | Isométrico | 1:125 (isométrico) + "INDICADA" | Isométrico da estrutura completa em arame (pilares, tesouras, terças, contraventos); eixos em bolhas (A..G, 1..9) no pé do isométrico; LISTA DE MATERIAIS global (canto sup. esq.); NOTAS gerais 1..13 (canto dir., acima do carimbo); legenda de abreviaturas e de símbolos. |
| 003 | Planta de bases | 1:100 (planta), 1:10 (detalhes) | Planta de locação das bases com eixos, cotas entre eixos e offsets, perfil do pilar + marca da base + tipo (ex. `W150X13 / BASE B.3 / TIPO 2`); indicação de norte e sistema de coordenadas X/Y; na faixa inferior: 3 detalhes `BASE TIPO 1/2/3` em planta + 2 cortes A e B (chumbadores, graute, nível da chapa). |
| 004 | Planta do banzo superior | 1:100 (planta), 1:10 (detalhes) | Planta da cobertura e travamento: tesouras nomeadas (`TESOURA 1..10`), contraventos em X tracejados (`BRØ 5/8" (TIP P/ CVH)`), tubos de travamento `TB150X150X2`, marcação `MF` (mão-francesa) em cada apoio; detalhes: `FIXAÇÃO TIRANTE Ø5/8"` (8 variantes), `TIRANTES DE TRAVAMENTO Ø5/8"`, `MÃO-FRANCESA`. |
| 005 | Planta da cobertura | 1:100 (planta), 1:10 (detalhes) | Planta de terças e travamento das terças: cadeia de espaçamentos de terças no topo e na base, inclinações (`7.7%`, `10.5%`) com triângulo de caimento, tirantes rígidos (`L51X3.2`) e flexíveis (`BRØ 3/8"`), terça típica `UE250X65X18X2.25 (TIP)`; detalhes: `TRAVAMENTO DAS TERÇAS` + corte A, `SUPORTE DE TERÇA (UE150)`, `SUPORTE DE TERÇA (UE250)` x2. |
| 006 | Eixos 1 a 3 | 1:50 (elevações), 1:10 (detalhes) | Elevações das tesouras dos eixos 1, 2 e 3 (vigas W e treliça); níveis `EL.+6.000`, `EL.+8.200`; detalhes `LIGAÇÃO DE DIAGONAIS E MONTANTES` (2x, com tabela Lmin por perfil) + seções A e B; `DETALHE TÍPICO DE PRESILHA` com tabela de espaçamento máximo por cantoneira. |
| 007 | Eixos 4 a 6 | 1:50 / 1:10 | Elevações das tesouras treliçadas dos eixos 4, 5, 6; detalhes: `EMENDA DO BANZO U200`, `EMENDA DO BANZO W200` (chapa, parafusos A325), `DET. EMENDA DA TESOURA`, `DET. COLUNA COM TESOURA` (com tabela perfil / t chapa / parafusos). |
| 008 | Eixos 7 a 9 | 1:50 | Elevações das tesouras 7, 8, 9 e `EIXO FACE NORTE` (viga de borda em W310/W410 com inclinação). Sem detalhes; notas remetem à 001. |
| 009 | Travamento das filas | 1:100 (elevações), 1:10 (detalhe) | Elevações longitudinais `TRAVAMENTO FACE OESTE`, `FILA D`, `FILA G` com tubos `TB150X150X2` e X de `BRØ 5/8"`; `DETALHE DE FIXAÇÃO TB150`; tabela `FILETE MÍNIMO DE SOLDA` (espessura da chapa x filete). |

(A folha 002 não fazia parte do conjunto fornecido.)

## 2. Conjunto 2 — pré-moldados + fechamento + telhado (casa de força de PCH)

Numeração: `PE.<obra>.<unidade>.DES.SP.NNN` (fase PE = projeto executivo, DES = desenho, SP = superestrutura), revisão `R0A, R0B, ... R0E` (letra). Séries: 00x = seções arquitetônicas/arranjo, 2xx = fôrmas/montagem, 3xx = armaduras, 7xx = estrutura metálica (treliças, telhado, fechamento).

| Folha | Título (carimbo) | Escala | Conteúdo |
|---|---|---|---|
| GRD011 | Guia de remessa de documentos (A4) | – | Tabela com lista de documentos emitidos (nome, descrição), emissão, data, finalidade (PI/PA/PE/EF). |
| SP.002 | Arquitetônico — Seções S.01 e S.02 | 1:50 e 1:75 (escala gráfica) | Seção transversal e longitudinal da casa de força com pilares/vigas pré-moldadas, ponte rolante (`40 t / 3 t`), treliça de cobertura, telhas, calhas; régua de cotas de nível em metros (900..914) nas duas laterais; cotas em metros (`5,33`, `0,60`); nuvens de revisão em vermelho com texto. |
| SP.003 | Arquitetônico — Seções S.03 e S.04 | 1:50 / 1:75 | Idem, outras seções (portão roll-up, guarda-corpo). |
| SP.200 | Pré-moldados — Planta de montagem (EL. 911,90) — Planta, seções e detalhes | 1:75 (escala gráfica), detalhes sem escala | Planta de montagem com marcas `P-01..P-19 (50x60cm)` e `V-01..V-14 (55x60cm)`; seções S.1 e S.2 (elevações das filas com níveis 908,30 / 908,50 / 908,90 / 911,90); `DETALHE 01/02/03` do apoio viga-pilar (pinos de montagem, neoprene, inserts); notas; lista de documentos de referência. |
| SP.201 | Fôrmas — Pré-moldados — Vigas — Plantas e seções | 1:50 (vigas), 1:25 (seções), 1:10 (insert) | Para cada grupo de vigas iguais: PLANTA + SEÇÃO longitudinal (S.1, S.6, S.7, S.8, S.9); seções transversais S.2..S.5, S.10, S.11; `INSERT TIPO 1` (planta + seção S.A); quadro `PROPRIEDADES DO CONCRETO`, `ACABAMENTO DE FÔRMA`, `QUANTITATIVO MATERIAIS INSERTS`. |
| SP.202 | Fôrmas — Pré-moldados — Pilares — Plantas, seções e detalhe | 1:50 (pilares), 1:25 (seções), 1:10 (inserts) | 8 elevações de pilares (um por grupo de pilares iguais), `DETALHE 01` (embutimento no cálice com graute), seções S.1..S.11, inserts tipo 1, 2 e 3 (planta + seção), quantitativo de inserts. |
| SP.301 | Armaduras — Pré-moldados — Vigas — Seções e lista do aço | 1:50 | Para cada grupo de vigas: elevação da armadura, barras desenhadas individualmente (`N1..N9`), seções S.1..S.12, `TABELA DE FERROS — 1 UNIDADE` e `— N UNIDADES` + `RESUMO DO AÇO +10%`. |
| SP.302 | Armaduras — Pré-moldados — Pilares — Seções e lista do aço | 1:50 | Idem para pilares (6 grupos), com `FERRO DE IÇAMENTO N2`, `VISTA V.1` do topo. |
| SP.700 | Estrutura metálica — Treliça metálica — Planta, seções, detalhes e lista de materiais | 1:100 (planta), 1:50 (conjuntos montados), 1:20 (treliça), 1:15 e 1:10 (detalhes) | Planta baixa das treliças, seção dos conjuntos montados, elevação de um conjunto com todas as barras numeradas em bolhas (1..35), detalhes 01..06 (perfil duplo, cantoneira de apoio, cantoneira de reforço), isométrico, `LISTA DE MATERIAIS — TRELIÇA (01 CONJUNTO)` (POS/QTE/PERFIL/COMP/MATERIAL/PESO/DESCRIÇÃO). |
| SP.705 | Estrutura metálica — Telhado — Planta, seções, detalhes e lista de materiais | 1:75 (planta), 1:25 (seções), 1:15 (detalhes) | Planta de terças e contraventamento do telhado (X de barra redonda), seções 1, S.2, detalhes 01..04 e S.A/S.B (terça sobre cantoneira, calha, contraventamento), isométrico, lista de materiais do telhado (incl. telhas, calha, cumeeira com área em m²). |
| SP.710 | Treliça metálica — Sala de comando | 1:50 (planta), 1:20 (seções), 1:10 (detalhes) | Planta, seções S.1/S.2/S.3 (conjuntos 01..03), detalhes 01/02 (apoio na laje com chapa + parabolt), seções S.A/S.B, `DETALHE — CHAPA FIXAÇÃO LAJE`, 3 listas de material (uma por conjunto), vista 3D. |
| SP.715 | Telhado — Sala de comando | 1:50 (planta), 1:20 (seções), 1:10 (detalhes) | Planta de terças, seções S.1/S.2/S.3 por conjunto, detalhes 1..4 e S.A/S.B, lista de materiais do telhado + lista de drenagem (calhas, tubos PVC). |
| SP.720 | Fechamento lateral | 1:50 (plantas eixos), 1:75 (seções/fachadas), 1:10 e 1:15 (detalhes) | Plantas dos eixos 1 e 3 (vigas de fechamento), `DETALHE — ESTRUTURA FECHAMENTO` (oitão), fachadas S.1 e S.2 com fiadas de terças cotadas e níveis, detalhes 1, 2, 3 e seções S.A/S.B/S.C, lista de materiais do fechamento lateral, 2 isométricos. |
| SP.725 | Fechamento montante e jusante | 1:75 (vistas), 1:25 (seções), 1:15 (detalhes) | `VISTA DE MONTANTE` e `VISTA DE JUSANTE` com marcas 1A..9A / 1B..16B, seções S.A/S.B (pilar + fechamento + calha), detalhe 3 (terças p/ venezianas), seções S.C/S.D (chapa de fixação), listas de material separadas por fachada + lista de drenagem. |
| SP.730 | Fechamento lateral — Sala de comando | 1:50 (planta), 1:20 (seções), 1:10 (detalhes) | Planta, seções S.1/S.2/S.3, detalhe 4 (fixação terça), detalhe chapa fixação terça, seção S.A (perfil fixado na laje), lista de materiais, vista 3D. |

---

## 3. Convenções observadas (concretas e replicáveis)

### 3.1 Formato, margens e grade de referência

Conjunto 1:
- A1 paisagem. Moldura externa a ~5 mm da borda; moldura interna (área útil) a ~10 mm, com margem de encadernação maior à esquerda (~20 mm).
- Faixa de grade de referência entre as duas molduras: 12 colunas numeradas (1..12, ~68 mm cada) no topo e na base; 8 linhas com letras (A..H, ~70 mm cada) nas laterais. Os números/letras ficam centralizados em cada célula, em texto pequeno (~2,5 mm), e as divisões são marcadas por traços curtos na faixa.
- Canto inferior esquerdo (girado 90°): quadro `PADRÃO DE IMPRESSÃO` com a tabela cor da pena x espessura de linha (vermelho 0,1; amarelo 0,2; verde 0,3; cyan 0,4; azul 0,5; magenta 0,6; branco 0,7 mm) e a indicação `A1(841x594)`.
- Isso permite remeter a um ponto da prancha por célula (ex. "detalhe em G-3").

Conjunto 2:
- A1 paisagem. Moldura externa fina perto da borda e moldura interna ~15 mm da borda (esquerda ~35 mm para encadernação); marcas de dobra/divisão no topo e na base (traços curtos saindo da moldura externa a cada ~1/4 da largura).
- Sem grade alfanumérica. A área útil é subdividida por linhas finas em "quadros" (painéis) retangulares; cada painel contém um desenho ou grupo (planta, seção, detalhes, lista), com o título e a escala gráfica no canto inferior esquerdo do painel. A coluna da direita (~22% da largura) é reservada para isométrico, listas, notas e carimbo.

### 3.2 Carimbo (canto inferior direito)

Conjunto 1 (largura ~190 mm, altura ~120 mm, blocos de cima para baixo):
1. Tabela de revisões (6 linhas vazias + preenchidas de baixo para cima; a linha de cabeçalho fica na base): colunas `REV. | DATA | DESCRIÇÃO | EXEC. | APROV.`. A revisão mais recente fica na linha de cima.
2. Faixa do logo / dados da empresa projetista (endereço, telefone, e-mail, site) e selo de certificação.
3. `RESPONSÁVEIS TÉCNICOS`: nome + CREA (dois engenheiros).
4. `TÍTULO` (nome da obra em caixa alta, maior; abaixo, fase e nome da folha em 2 linhas) à esquerda e `PRANCHA` (número da folha com 3 dígitos, fonte muito grande, ~12 mm) à direita.
5. Linha de rodapé: `ESCALA (INDICADA) | UNIDADE (mm) | ENGº PROJETISTA (iniciais) | NÚMERO DESENHO (NNNN-PB-01-XXX) | REV. (02)`.
- Rótulos dos campos em texto minúsculo (~1,5 mm) no canto superior esquerdo de cada célula; valores em ~3 mm.
- Logo acima do carimbo: bloco `NOTAS:` com "para notas gerais ver des. ...-001" (nas folhas que não a 001).

Conjunto 2 (largura ~190 mm, altura ~130 mm):
1. Tabela de revisões com 10 linhas (vazias acima), cabeçalho na base: `REV. | DATA | DESCRIÇÃO | ELAB. | VERIF. | APROV.`. Revisões por letra (R0A..R0E), descrição em caixa alta descrevendo o que mudou ("ajustado pilares P-03..."), três colunas de iniciais.
2. `CLIENTE:` com logos e razão social + CNPJ.
3. `RESPONSÁVEL TÉCNICO:` (nome + CREA, 2 linhas) à esquerda e `PROJETISTA:` (logo) à direita.
4. `FINALIDADE:` (PROJETO EXECUTIVO) | `PROJETO:` (nome do empreendimento).
5. `REFERÊNCIA:` 3 linhas: disciplina (ARRANJO / FÔRMAS / ARMADURAS / ESTRUTURA METÁLICA), objeto (PRÉ-MOLDADOS — VIGAS), conteúdo (PLANTAS E SEÇÕES / SEÇÕES E LISTA DO AÇO).
6. Rodapé: `ESCALA: INDICADA | COORDENADOR TÉCNICO: nome + CREA | DOCUMENTO: PE.xxx.DES.SP.201 | FOLHA: 01 de 01`.
- Acima do carimbo (mesma coluna): `DOCUMENTOS DE REFERÊNCIA` (lista de códigos) e `NOTAS` numeradas.

### 3.3 Composição da prancha

- Conjunto 1: desenho principal (planta ou 3 a 4 elevações empilhadas) ocupa ~75% da largura; faixa inferior (~20% da altura, abaixo da linha G) reservada aos detalhes 1:10 lado a lado; coluna direita (~22%) com notas + carimbo. Nas pranchas de elevações os 3 eixos ficam empilhados alinhados pelo eixo A à esquerda, com bolhas de eixo repetidas em cada elevação.
- Conjunto 2: malha de painéis. Padrão típico: planta no painel superior esquerdo, seções/elevações nos painéis inferiores, detalhes em coluna central ou direita, lista de materiais + isométrico + notas + carimbo na coluna direita. Painéis separados por linha contínua fina (mesma espessura da moldura interna).
- Cada vista tem título sublinhado em caixa alta e, abaixo, `ESC.: 1/10` (conj. 1) ou `ESCALA GRÁFICA 1:25` + régua gráfica (0 / 0,25 / 0,5 / 1,0 m) (conj. 2). No conj. 2 a régua é obrigatória em todas as vistas.
- Fichas de materiais (propriedades do concreto, acabamento de fôrma) são quadros pequenos com o símbolo que aparece no desenho (hexágono `E-1`, triângulo `F-2`) e a descrição.

### 3.4 Escalas usadas por tipo de vista

| Tipo de vista | Conj. 1 | Conj. 2 |
|---|---|---|
| Isométrico geral | 1:125 | sem escala |
| Planta de bases / cobertura / terças | 1:100 | 1:75 (montagem, telhado), 1:100 (planta treliças), 1:50 (sala de comando) |
| Elevações de pórticos/tesouras | 1:50 | 1:50 (conjuntos montados), 1:20 (treliça isolada), 1:75 (fachadas) |
| Elevações de travamento longitudinal | 1:100 | – |
| Fôrma de viga / pilar (elevação + planta) | – | 1:50 |
| Seção transversal de peça pré-moldada | – | 1:25 |
| Armadura (elevação) | – | 1:50 |
| Detalhes de ligação metálica | 1:10 | 1:10 e 1:15 |
| Inserts / chapas de fixação | – | 1:10 |
| Seções arquitetônicas | – | 1:50 / 1:75 |

### 3.5 Nomenclatura de eixos, peças e marcas

- Eixos: números (1..9) em uma direção, letras (A..G) na outra, em bolhas (elipses no conj. 1, círculos no conj. 2) nas extremidades das linhas de eixo (traço-ponto). Eixos secundários com apóstrofo não aparecem; o conj. 1 usa eixo adicional nomeado `A` dentro da bolha mesmo para linha intermediária.
- Conj. 1 (metálica): pilares identificados pelo perfil (`W150X13`, `W200X15`) + marca da base `BASE B.1..B.40` + `TIPO 1/2/3`; tesouras `TESOURA 1..10`; terças `UE250X65X18X2.25`; tubos `TB150X150X2`; tirantes `BRØ 5/8"`; chapas `CH6.3`, `CH16`, `CH19`, `CH22.4` (CH + espessura em mm); cantoneiras `L51X3.2`, `L64X4.8`, `L 1 1/4"x1/8"`; parafusos `PAR.Ø1/2"-A307`, `PAR.Ø3/4" A325`; mão-francesa `MF`; abreviaturas padronizadas na legenda (TV, TC, FICB, FIV, LA, LP, AL, PT, CVH, CVV, EA, US, LC).
- Conj. 2 (pré-moldado): pilares `P-01..P-19` com seção entre parênteses `(50x60cm)`; vigas `V-01..V-14 (55x60cm)`; seções `S.1, S.2 ... S.11`; detalhes `DETALHE 01`; inserts `INSERT TIPO 1/2/3` com quantidade `(17x)`; barras `N1..N12`; marcas de fechamento `1A..9A` (fachada A) e `1B..16B` (fachada B); marcas de treliça da sala de comando `1A, 2A ... 15C` (número + letra do conjunto); peças da treliça principal numeradas 1..35 em bolhas.
- Grupos de peças iguais: título do painel lista todas as marcas: `VIGAS (V-01, V-02, V-03, V-04, V-05 E V-06)`, `PILARES (P-01 E P-19)`.

### 3.6 Cotas

- Conj. 1: tudo em mm (campo UNIDADE = mm). Cotas com extensão fina, linha de cota contínua com tick oblíquo (barra 45°), texto sobre a linha, ~2 mm. Cadeias parciais entre eixos (`4100 | 7745 | 8000 ...`) e totais abaixo; nas tesouras, cadeia de espaçamentos de terças no banzo superior (`1994 x N`, usando notação `8X1994`, `14X994`) e cadeia de painéis no banzo inferior (`994 | 994 | ...`), com subtotais (`3230`, `650`, `7748`). Offsets de eixo (`250`, `295`, `228`) cotados localmente. Alturas de pilar a partir dos níveis (`316`, `300`, `800`).
- Níveis: bolha alongada (elipse) à esquerda das elevações com `EL.+6.000` e `EL.+8.200` (metros com ponto, 3 casas) na linha de referência traço-ponto; cotas de nível de apoio com triângulo preenchido e `EL+6.300` ao lado; `EL.+VER EIXOS` nos detalhes genéricos.
- Conj. 2 pré-moldado: tudo em cm (nota 1: "todas as dimensões em centímetro, exceto onde indicado"), com decimal por vírgula (`452,75`, `25,5`, `9,75`). Níveis em metros com vírgula (`908,90`, `911,90`) e triângulo de nível preenchido (nota 2). Cotas em cor laranja/marrom (cor diferente dos traços de desenho), tick oblíquo, texto acima da linha. Cadeias: comprimento total da peça, trechos (100 | 252,75 | 100), posição de furos/inserts (30 | 49 x 8 | 30), e cotas de altura (39 | 21 = 60).
- Conj. 2 metálica (7xx): tudo em mm (nota 1 "em milímetro"), cotas laranja, níveis em metros.
- Ângulos de inclinação: `i=10°` ou `7.7%` com triângulo de caimento na planta.

### 3.7 Indicação de cortes e detalhes

- Conj. 1: símbolo de corte = círculo dividido ao meio com a letra em cima (`A`) e o número da folha de destino em baixo (`-` quando é na mesma folha), encimado por um triângulo preto que indica o sentido de observação. Detalhes recebem `1`, `2`, `3` no mesmo símbolo; vistas recebem o mesmo círculo sem triângulo. Título da vista repete o símbolo: círculo `A/-` + `CORTE` + `ESC. 1:10`. Legenda do símbolo na folha 001 (A = nome da vista, B = folha de destino, D = folha de origem).
- Conj. 2: corte = semicírculo (meia-bolha) com `S.1` e um triângulo preto no topo apontando o sentido, nas duas extremidades da linha de corte (linha de corte não desenhada no meio). Detalhes: retângulo traço-ponto em volta da região + texto `DETALHE 01` com linha de chamada, ou círculo tracejado (`DETALHE 01` na planta de montagem). Vista ampliada do detalhe desenhada dentro de círculo tracejado grande (planta de montagem) ou em painel próprio.
- Indicador de revisão: triângulo com o número da revisão dentro (legenda na 001); nuvens de revisão em vermelho com texto explicativo no conj. 2.

### 3.8 Representação de perfis, chapas, parafusos, soldas, chumbadores (conj. 1)

- Perfis em elevação: duas linhas de mesa + linha de alma; em corte: contorno do I/U/L com espessura; tubos retangulares com cantos arredondados; em planta as terças U enrijecidas aparecem como linha dupla fina.
- Perfis laminados `W200X15`, `W310X21`; cantoneiras `L51X3.2` (aba x espessura, mm); U formados `U200X50X3.00`; U enrijecidos `UE250X65X18X2.25` (h x b x enrijecedor x t); tubo `TB150X150X2` (nota 10: TB H x L x e; tubo circular TBØ D x e); barra redonda `BRØ 5/8"`.
- Chapas `CH6.3`, `CH8`, `CH16`, `CH19`, `CH22.4` (espessura em mm); dimensões da chapa cotadas (140 x 340; 150 x 150). Chapas de base hachuradas em corte (hachura de seção 45°) e cotadas (180 x 240; furo + chumbador).
- Parafusos: em planta, cruz dentro de círculo (`+` com pequeno círculo); em elevação, retângulo preto (cabeça + porca) atravessando as chapas. Notação `PAR.Ø1/2"-A307`, `PAR.Ø3/4" A325`, `Ø5/8"`; nota geral define A325 para principais e A307 para secundários.
- Furos: `FURO OVAL Ø 11,5x23`; nos detalhes de base, `FURO Ø` em losango numerado (`21`) + `CHUMB. Ø5/8" A36`.
- Soldas: símbolo AWS (seta com bandeira triangular de filete, tamanho `5`, `6/6` nos dois lados; triângulo preenchido = solda de campo); nota geral "soldas conforme AWS D1.1"; tabela `FILETE MÍNIMO DE SOLDA` (chapa <6,3 → 4 mm; 6,3–9,5 → 5; 9,5–12,5 → 6; 12,5–16 → 8; ≥16 → 10).
- Chumbadores: barra com gancho em J ou L dentro do concreto (pontilhado de concreto na seção), `R35` no gancho, comprimento de ancoragem `300`, `35` de saliência, graute `GRAUTE` hachurado entre chapa e concreto (`50`), texto `CHUMBADORES ROTACIONADOS P/ B13, B16...` e ângulo (`2,36°`), nível `F.I.C.B.` (face inferior da chapa de base).
- Perfis das barras da treliça escritos ao longo da barra (texto alinhado com a diagonal): `L25X3.2`, `L32X3.2`, `L44X3.2`, `L64X4.8`; banzos `W200X15`, `U200X50X4.75`.

### 3.9 Representação de fôrmas de pré-moldados (conj. 2)

- Viga: PLANTA (vista de cima mostrando furos para pinos Ø4 cm, olhais de içamento Ø10 cm e inserts como quadrados tracejados) + SEÇÃO longitudinal (elevação com concreto pontilhado, dentes/rebaixos nas extremidades, níveis 908,90 / 908,30) + seções transversais 1:25 (S.2 pelo apoio com furos Ø4, S.3 pelo olhal, S.4/S.5 pelos inserts).
- Pilar: elevação vertical como montado (base no cálice, topo com insert tipo 1), com cálice representado por retângulo traço-ponto `DETALHE 01` e chave de cisalhamento (ranhuras) no trecho embutido (160 cm); consolo da ponte rolante com chanfro; cadeia de cotas à esquerda (total 1260 | 340 = trechos) e à direita (posição de cada insert a cada 115 cm, 92, 100, 110, 36); níveis à esquerda (899,30 / 900,50 / 908,50 / 911,90); indicação de cortes S.1..S.4 com meia-bolha em alturas diferentes; olhal de içamento cotado (170 do topo, 23 da face).
- Inserts: na elevação são pequenos retângulos com seta de chamada `INSERTS TIPO 2`; `PROJEÇÃO INSERTS TIPO 2` para os da face oculta (tracejado). Detalhe de insert: PLANTA (chapa 20x20 cm com 4 furos Ø1/2" e 4 barras J Ø3/8" em diagonal) + SEÇÃO S.A (barras J com gancho, `SOLDA`, concreto pontilhado) com bolhas de item `01`, `02` ligando ao `QUANTITATIVO MATERIAIS INSERTS` (ITEM | DESCRIÇÃO | PESO TOTAL | QTD.). Cada insert tem na legenda a quantidade de uso: `INSERT TIPO 1 (17x)`.
- Concreto em corte/elevação: pontilhado leve (hachura AR-CONC) em todo o corpo; símbolos `E-1` (hexágono = classe de concreto) e `F-2` (triângulo = acabamento de fôrma) apontando para as faces.
- Cálice/graute: `DETALHE 01` 1:25 com pilar 60 + 5 cm de graute cada lado = 70, chaves de 10 cm a cada ~1 (tip), `SIKAGROUT 250` como chamada.
- Apoio viga-pilar (planta de montagem): detalhe em círculo tracejado, viga sobre pilar com `APOIO DE NEOPRENE`, `PINOS DE MONTAGEM E TRAVAMENTO DA VIGA` em verde (Ø4 cm, furo preenchido com adesivo), cotas 50 | 24,5 | 24,5, níveis 908,30 / 908,50 / 908,90.

### 3.10 Representação de armaduras (conj. 2)

- Elevação da peça com contorno fino e concreto pontilhado; barras longitudinais em linhas verdes (cor por pena), estribos como linha vertical fina repetida; cada posição marcada por bolha `N1..N9` com linha de chamada.
- Cada posição é desenhada fora da peça, isolada, na forma real (gancho, dobra) e cotada: texto `6 N4 Ø25 C/9 C=144` (quantidade, posição em vermelho, bitola, espaçamento, comprimento total), trechos (`108`, `20`, `16`, `37`), raio interno de dobra `Ri=10`. Estribos: `2 N1 Ø12.5 C=145` com os lados `39`, `16`, ganchos `7`. Barras agrupadas `2x23 N7 Ø10 C/15` (duas camadas), `2x5 N6 Ø12.5 C/8 C=482`.
- Seções transversais (S.1, S.2 ...) com estribo e pontos das barras, posições em bolhas ao redor; ao lado, miniatura da seção com dimensões (`52 x 31`).
- Olhal e ferro de içamento identificados (`FERRO DE IÇAMENTO N2`, `OLHAL DE IÇAMENTO Ø10cm`); `INSERTS VER DES.SP.202` como chamada (não se repete o detalhe).
- Lista de aço = `TABELA DE FERROS — 1 UNIDADE` + `TABELA DE FERROS — N UNIDADES` (multiplicada pelo número de peças do grupo). Colunas: `TIPO (CA-50A/CA-25A) | POS. | BIT. (mm) | QUANT. | C.Unt. (cm) | C.Tot. (cm)`; linha de grupo `Det-1 (1 X)`; bloco `RESUMO DO AÇO +10%` com `PESO CA-50A Ø 10 ... m ... kg` por bitola, `PESO TOTAL CA-50A`, `PESO TOTAL =`; rodapé com `Fck = 30MPa`, `VOLUME DE CONCRETO = 1.45m3`, `ÁREA DE FÔRMA = 8.40m2`.
- Nota 3 "cobrimento da armadura 4 cm, exceto onde indicado".

### 3.11 Fechamento (conj. 2, SP.720/725/730)

- Vista de fachada (1:75) com pilares pré-moldados em cinza/pontilhado, telha com hachura de linhas verticais (telha trapezoidal), fiadas de terças como linhas duplas horizontais com marca em bolha (`5`, `6`, `1A`) no meio de cada vão; cadeia vertical das fiadas à esquerda (1096 | 1000 | 1096 | 1700 | 1150 x 5 | 400) e níveis em metros (900,50 / 900,90 / 906,65 / 908,35 / 911,54 / 911,93) à esquerda com triângulo; cadeia horizontal dos pilares/vãos (2667 | 1080 | 4253 | ...) e total 17130 em baixo; aberturas (venezianas, portões) como retângulos tracejados com marca; `FLUXO` com seta azul (orientação do rio); referência cruzada "P/ DETALHAMENTO DA TRELIÇA VER DES.SP.700".
- Painéis de telha translúcida e venezianas recebem marca própria na lista (13, 14) e a quantidade por área (m²) ou comprimento total.
- Detalhes de fixação da terça no pilar pré-moldado (1:10): chapa `CH 250x200x3` com 4 furos Ø3/8" para `PARABOLT 1/4"` e U da terça soldado, cotas 30 | 190 | 30, 100 | 100; seção com pilar hachurado, terça `Ue 200x75x25x2.66` e cantoneira `L 101.6x6.35`.

### 3.12 Planta de montagem (conj. 2, SP.200)

- Pilares como quadrados com X (seção hachurada) e marca `P-01 (50x60cm)` ao lado; vigas como retângulos com inserts (quadrados pequenos) e marca `V-01 (55x60cm)` abaixo, centrada no vão; eixos em bolhas; cotas de eixo a eixo (1000 / 2773 / 1685), largura dos pilares (50), vão livre (404), folga (1,0), balanço (2, 25,5); norte não indicado (orientado pelo fluxo).
- Seções S.1 e S.2 (elevações das duas filas) com todos os pilares, vigas, níveis (908,30 apoio, 908,50 fundo da viga, 908,90 topo, 911,90 topo do pilar), folga de 1,0 cm entre viga e pilar, pinos de montagem em verde, círculo tracejado indicando `DETALHE 01`.
- Notas fixas: 1) dimensões em cm; 2) elevações em m; 3) para detalhamento ver SP.201.

### 3.13 Tabelas

- `LISTA DE MATERIAIS` (conj. 1, global na folha 001): colunas `PERFIL | MATERIAL | COMPR._ÁREA (m_m2) | M. UNIT. (kg/m_kg/m2) | M. TOTAL (kg)`; perfis ordenados por família (UE, W, L, TB, BR, U); rodapé `TOTAL LÍQUIDO`, `LIGAÇÕES (~10%)`, `TOTAL`.
- `LISTA DE MATERIAIS — <conjunto>` (conj. 2, uma por prancha/conjunto): `POS. | QTE | PERFIL (ou DESCRIÇÃO) | COMP. (mm) | ÁREA (m²) | MATERIAL | PESO TOTAL (kgf) | DESCRIÇÃO (função: BANZO SUPERIOR, COLUNA TRELIÇA, TERÇA COBERTURA, CONTRAVENTAMENTO, TELHADO)`; `PESO TOTAL` na última linha; notas com asterisco abaixo (área sem sobreposição; parafusos em outro documento; pintura). Parafusos/porcas/arruelas e esticadores entram como POS. com traço nas colunas de comprimento/peso.
- `LISTA DE MATERIAIS — DRENAGEM CALHAS`: `POS. | QTE | PERFIL | Ø mm`.
- Tabelas auxiliares de detalhe: `PERFIL | Lmin (mm)` (comprimento mínimo de ligação por cantoneira), `PERFIL | t (mm) | paraf.` (ligação coluna-tesoura), `ESPAÇAMENTO MÁXIMO p/ L25 Gmax=250mm ...` (presilhas), `FILETE MÍNIMO DE SOLDA`.
- Quadros de propriedades: `PROPRIEDADES DO CONCRETO` (símbolo E-1 | CONCRETO ESTRUTURAL | fck 30 MPa / E ≥ 30,6 GPa / slump 9,0 ± 1,0 cm), `ACABAMENTO DE FORMA` (F-2 | LISO), `QUANTITATIVO MATERIAIS INSERTS`.
- Todas as tabelas: bordas finas, cabeçalho em caixa alta, título centralizado na primeira linha, números alinhados à direita (conj. 1) ou centralizados (conj. 2).

### 3.14 Notas gerais típicas (temas, não texto literal)

Conj. 1 (folha 001, 13 itens): 1) especificação de materiais por família (laminados, chapas, perfis soldados, barras, eletrodo, parafusos principais/secundários); 2) tratamento de superfície (jateamento, sistema de pintura por ambiente, espessuras de película, cor); 3) interface aço-concreto (cargas nominais, sinal das cargas, fck mínimo das bases, graute); 4) lista de material é indicativa, fabricante confere; 5) conferir medidas em obra; 6) legenda de abreviaturas; 7) legenda de símbolos (revisão, guarda-corpo, direção portante, ligação a momento / rotulada, símbolo de corte); 8) soldas conforme norma; 9) controle de qualidade de soldas (US em penetração total); 10) notação de tubos; 11) substituição de tubulares por U enrijecidos; 12) ensaio de chapas espessas (decoesão lamelar); 13) carregamentos considerados (sobrecarga, utilidades, fotovoltaica, vento V0).
Demais folhas: apenas "para notas gerais ver des. ...-001".

Conj. 2 (em cada prancha, 3 a 4 itens): unidade das dimensões (cm ou mm); elevações em metros; cobrimento (armaduras); referência cruzada à prancha de montagem/fôrmas/armaduras; para metálica: ligações soldadas em fábrica e parafusadas só em montagem; filete mínimo em todo o contorno de contato; mais `DOCUMENTOS DE REFERÊNCIA` (código do arquitetônico e de pranchas correlatas).

---

## 4. Cobertura metálica — detalhes com medidas (conj. 1, folhas 004/005/006 e conj. 2, SP.705)

### 4.1 Planta de terças (folha 005, 1:100)

- Terças desenhadas como linha dupla fina contínua no sentido longitudinal, apoiadas nas tesouras (linhas dos eixos 1..9). No alto e na base da planta, cadeia de espaçamento das terças ao longo da inclinação: `2050 | 2050 | 1825 | 1975 | 1975 | 1970 | 2080 | 1975 ...` (valores irregulares porque acompanham a geometria da cobertura, projeção horizontal); comprimento de vão entre eixos na linha de baixo (`4100 | 7745 | 8000 ... | 5026`).
- Tirantes de travamento das terças (linha-de-corrente) como linhas tracejadas em X entre terças a meio vão, com `TIRANTE RÍGIDO L51X3.2 (TIP)` nas bordas e `TIRANTE FLEXÍVEL BRØ 3/8" (TIP)` nos X internos; chamada `TERÇA UE250X65X18X2.25 (TIP)`.
- Nos apoios das terças sobre a tesoura: pequenos "bigodes" (traço inclinado ±) marcando a presilha/suporte em cada cruzamento.
- Inclinações com triângulo e percentual (`7.7%`, `10.5%`); transpasse/emendas não cotados (não há emenda de terça: um comprimento por vão).
- Marcas: a terça típica é identificada pelo perfil; não há marca individual (projeto básico). Em projeto executivo (conj. 2, SP.705) cada terça recebe marca em bolha (`1` = Ue 200x75x25x2,66 c=5001; `2` = c=4538), repetida em cada vão, e a lista dá quantidade (36 / 72) e comprimento; o contraventamento é `3` (barra redonda Ø12,5), `4`/`5` chapas de ligação e esticador; espaçamento de terças `1507` constante, primeira fiada a `656` do eixo e `112` da borda.

### 4.2 Suporte de terça (folha 005, 1:10, 3 variantes)

- Cantoneira/chapa dobrada `CH6.3` soldada no banzo superior da tesoura (W ou U) e parafusada à alma da terça:
  - UE150: chapa com largura ~60 mm (30 + 30 em torno da linha de furos), altura 60 + 110 = 170 mm (60 acima da mesa e 110 descendo até o banzo), 2 parafusos `PAR.Ø1/2"-A307` a 25 mm da borda; vista lateral mostra chapa `CH4.75` de reforço e cota 20 do banzo.
  - UE250: chapa com 120 mm de altura entre furos (25 + 120), 2 parafusos espaçados 60 | 60 verticalmente, 10 mm entre a chapa e a mesa; outra variante com chapa apoiada 20 mm acima do banzo.
- Furos a 30 | 30 do eixo; solda de filete `5` nos dois lados (símbolo AWS) ligando a chapa ao banzo.
- Cada variante tem seu título `SUPORTE DE TERÇA (UE150)` / `(UE250)` e é desenhada em vista frontal (I do banzo embaixo) e vista lateral (terça C vista de lado, chapa como linha).

### 4.3 Travamento das terças (folha 005, 1:10)

- Tirante rígido `L51X51X3.2` entre terças, fixado por cantoneira `L 1 1/4"x1/8"` e parafuso `Ø3/8"`, com trecho rosqueado `(ROSCA) 70`, cotas `20 | 50` e `100 | 113` da chapa até o eixo da terça; corte A (1:10) mostra `FURO OVAL Ø 11,5x23` na alma da terça com cotas `80 | 73 | 100`, chapa `CH6,35` com cotas `15 | 59`, e chanfro `3`.
- Tirante flexível: `BRØ 3/8"` passando por furo na alma, com porca e arruela de cada lado.

### 4.4 Mão-francesa (folha 004, 1:10)

- Par de cantoneiras `L51x3.2 (TIP)` em V, do banzo superior da tesoura (onde está a chapa de ligação da terça) até a terça adjacente, fixadas com `PAR.Ø5/8"`; cantoneira de apoio `L51x4.8` na terça; cotas: 30 do furo à extremidade, 28 de folga vertical, `VARIÁVEL` para o comprimento (depende do espaçamento das terças); inclinação indicada por triângulo `1 : 1`.
- Na planta (004) a mão-francesa aparece como texto `MF` em cada apoio de terça sobre a tesoura, e uma chamada `L51x3.2 TIP P/ MÃO FRANCESA`.

### 4.5 Tirantes / fixação (folha 004, 1:10)

- `DETALHE: FIXAÇÃO TIRANTE Ø5/8"` com 8 variantes lado a lado (tirante no pilar W, no U, no tubo quadrado; horizontal e a ~45°): chapa `CH6.3` soldada (símbolo AWS) ao perfil, barra Ø5/8" com rosca, porca e contraporca, cota `30` da borda da chapa ao furo.
- `DETALHE: TIRANTES DE TRAVAMENTO Ø5/8"`: chapa `CH6.3` 150 mm (30 + 60 + 60) com furo a 30 mm; luva/esticador com cantoneira `L64X6.4`, `CH16` e `(ROSCA) 120`; cotas 16 | 120 | 30 | 35 | 25 | 10.

### 4.6 Presilha (folha 006, 1:10)

- `DETALHE TÍPICO DE PRESILHA`: barras duplas de cantoneira com presilha `L25X25X3.2` soldada entre as duas abas, espaçamento `Gmax` cotado; tabela de espaçamento máximo por perfil: L25 250 mm, L31 310, L38 370, L44 440, L51 500, L64 630, L76 750, L102 1000; texto "fixar presilhas em todas as diagonais e montantes".
- `LIGAÇÃO DE DIAGONAIS E MONTANTES` (1:10): chapa de nó `CH4.75 SE NECESSÁRIO` e `#6.35mm (SE NECESSÁRIO)`; comprimento mínimo de solda/ligação `Lmin` por perfil (L25 40; L32 40; L38 50; L44 80; L51 80; L64 100 mm) em tabela ao lado; seções A e B mostram as duas cantoneiras abraçando o banzo U.

### 4.7 Elevações das tesouras (folhas 006-008, 1:50)

- Banzos em W200X15 / U200X50X4.75 desenhados com linha dupla e hachura leve; diagonais/montantes em cantoneira com nome do perfil escrito ao longo da barra; textos de altura `702`, `547`, `700` nos pontos de mudança; cumeeira cotada `1721 | 208 | 265 | 1760`; níveis de apoio com seta/triângulo `EL+6.700`, `EL+5.300`; emendas de montagem indicadas por `EMENDA` em texto vertical; terças representadas por "C" pequeno sobre o banzo em cada apoio e cadeia `8X1994`, `6X1960`.
- Em projeto executivo (SP.700) a treliça é 1:20, cada barra tem bolha numérica (1..35) e comprimento cotado ao longo da barra (`1077`, `914`, `1058`), painéis cotados no banzo inferior (`727 | 640 | 80 | 787 | 1507 ...`), caixas traço-ponto `DETALHE 03/04/05` em torno dos nós, `A` em círculo marcando o eixo de simetria.

---

## 5. Pré-moldados — pranchas de fôrmas e armaduras com medidas (conj. 2)

### 5.1 Fôrmas de vigas (SP.201)

- Por grupo de vigas iguais, um painel (~1/3 da largura x 1/2 da altura) com: título `VIGAS (V-01, ..., V-06)` + escala gráfica 1:50; PLANTA em cima (vista superior: contorno, furos de pino Ø4 cm nas extremidades cotados 9,75 | 25,5 | 17,5 | 37,5, olhais Ø10 cm a 100 cm das pontas, 8 inserts a cada 49 cm a partir de 30 cm, cadeia total 452,75 = 25,5 + 100 + 252,75 + 100 + 25,5 ... ) e SEÇÃO S.1 em baixo (elevação longitudinal com dente nas extremidades: altura 60 = 39 + 21, dente de 25,5 de comprimento, vão de fundo 401,75, níveis 908,90 topo / 908,30 fundo do dente, símbolos E-1/F-2).
- Linhas de corte `S.2`, `S.3`, `S.4` com meia-bolha acima e abaixo da planta; `S.1` nas extremidades.
- Painel da direita: seções transversais 1:25 (S.2: 55 x 60 com dente 39/21 e furos Ø4 a 13 | 21 | 13; S.3: 55 x 60 com olhal Ø10 a 25 do topo; S.4/S.5: insert na face superior cotado 37,5 | 17,5 com nota em vermelho para a armadura; S.10/S.11: viga 30 x 50).
- Insert tipo 1 em planta e seção 1:10 com itens 01/02 e quantitativo (chapa 20x20x0,9 cm, 4 barras J Ø3/8" c=30 cm).
- Quadros: propriedades do concreto, acabamento de fôrma, documentos de referência, notas (cm; níveis em m; montagem ver SP.200); obs. "quantitativo de fôrmas e volume de concreto na lista de armaduras".

### 5.2 Fôrmas de pilares (SP.202)

- 8 elevações verticais lado a lado na metade superior (cada uma ~1/8 da largura), título `PILARES (P-01 E P-19)` + escala gráfica 1:50. Pilar desenhado em pé com cálice embaixo (160 cm embutido, traço-ponto + ranhuras), consolo/alargamento para a viga da ponte rolante, topo com insert tipo 1 (30 cm de largura no trecho superior, 60 no inferior). Cadeias à esquerda (total 1260 = 340 + 800 + 120 (cálice)) e à direita (posições dos inserts: 36 | 110 | 100 | 92 | 15 | 30 | 55 | 115 x 7 | 160). Níveis 899,30 / 900,50 / 908,50 / 911,90. Olhal de içamento Ø10 cm cotado (170 do topo do trecho largo, 23 da face). Cortes S.1..S.4 em alturas diferentes (meia-bolha).
- Faixa do meio: `DETALHE 01` do cálice 1:25 (60 + 2x5 graute = 70; chaves 10/1 tip; SIKAGROUT) e seções S.1..S.11 1:25 (30 x 50, 60 x 50 com inserts tipo 2 nas faces, cotas 15 | 15, 30 | 30, 25 | 25).
- Faixa direita: inserts tipo 1 (chapa 20x20x0,9 + 4 J Ø3/8"), tipo 2 (chapa 20x20x0,9 + chapa 10x10x0,9 soldada em T), tipo 3 (chapa 30x50x1,25 com chanfro 45° e 8 barras J Ø5/8" c=40) em planta + seção (S.A, S.B, S.C) 1:10 com itens 01..05 e quantitativo total (ex.: 235 chapas 20x20, 68 barras J Ø3/8", 218 chapas 10x10, 30 chapas 30x50, 240 J Ø5/8").

### 5.3 Armaduras de vigas (SP.301)

- Por grupo: elevação 1:50 da viga com armadura (verde), bolhas N1..N9; acima, estribos isolados (`2 N1 Ø12.5 C=145`, lados 39 / 16, gancho 7); barras de distribuição (`4 N2 Ø12.5 C/15 C=483`, comprimento 443 + 20 + 20); estribos do dente (`5 N5 Ø12.5 C/6 C=250`, 100 x 50); abaixo, barras longitudinais (`6 N4 Ø25 C/9 C=144` com dobra 16 + 20 e Ri=10; `6 N3 Ø25 C/9 C=481` 367 + dobras 37/20; `2x5 N6 Ø12.5 C/8 C=482`); estribos de pele `2x23 N7 Ø10 C/15` com cotas 10 | 8.
- Coluna de seções S.1..S.3 (1:25 aparente) com bolhas N2/N3/N4/N5/N6 nas faces e miniatura `52 x 31` ao lado.
- Coluna das tabelas: `TABELA DE FERROS — 1 UNIDADE` e `— 10 UNIDADES` (6 colunas), resumo por bitola, peso total, fck, volume e área de fôrma por unidade e por grupo.

### 5.4 Armaduras de pilares (SP.302)

- Elevação vertical do pilar com armadura; barras principais (`4 N6 Ø16 C/13 C=363`, `3 N2 Ø16 C=150` de ancoragem com gancho Ri=3,4), estribos (`18 N4 Ø10 C/20`, `47 N3 Ø10 C/20`) com comprimento ao longo da altura (335 | 150), estribos variáveis (`4 N9 Ø8 C/10 C=174 V (38 a 66) VAR`), grampos (`3 N11 Ø6.3 C/15 C=108 V (25 a 43)`); `FERRO DE IÇAMENTO N2` e olhal; `INSERTS VER DES.SM.202` como chamada; seções S.1, S.2 (42 x 52, 25 | 15) e `VISTA V.1` do topo.
- Tabelas iguais às de viga, separando CA-50A e CA-25A (ferro de içamento), 12 posições.

---

## 6. O que a ND deve adotar (diferenças em relação a uma prancha só com vistas + algumas tabelas)

1. Moldura dupla com grade de referência alfanumérica (12 colunas x 8 linhas em A1) e quadro de penas/espessuras no canto inferior esquerdo; marcas de dobra no topo/base.
2. Carimbo em blocos fixos: tabela de revisões (cabeçalho na base, linhas vazias acima, colunas REV/DATA/DESCRIÇÃO/ELAB/VERIF/APROV), cliente, responsável técnico + CREA, finalidade, projeto, referência (3 linhas: disciplina / objeto / conteúdo), rodapé com escala, unidade, documento, folha N de M e revisão; número da prancha em fonte grande.
3. Bloco `NOTAS` e `DOCUMENTOS DE REFERÊNCIA` sempre na coluna do carimbo; notas gerais só na folha 001 e remissão nas demais; em cada prancha de pré-moldado as 3 notas fixas (unidade cm, níveis em m, cobrimento / remissão).
4. Área útil dividida em painéis por linhas finas; cada painel com título sublinhado em caixa alta + `ESC.: 1/N` e, para projeto executivo, escala gráfica com régua.
5. Padrão de escalas: 1:100/1:75 plantas, 1:50 elevações e fôrmas, 1:25 seções de peças, 1:20 treliça isolada, 1:10/1:15 detalhes metálicos e inserts.
6. Eixos em bolhas nas duas extremidades, repetidos em cada elevação; níveis `EL.+x.xxx` em bolha alongada à esquerda das elevações e triângulos de nível nos apoios.
7. Cotas em cadeia + total, com tick oblíquo, cor própria (laranja) diferente do desenho, decimais com vírgula; notação `8X1994` para repetições; cotas de folga (1,0), balanço e offset de eixo cotadas localmente.
8. Unidades: mm para metálica, cm para fôrma/armadura de pré-moldado, m para níveis; declarar no carimbo (UNIDADE) e na nota 1.
9. Símbolo de corte padronizado (círculo letra/folha com triângulo de direção, ou meia-bolha `S.n`) e detalhe por retângulo traço-ponto ou círculo tracejado com `DETALHE 0n`; o título da vista ampliada repete o símbolo.
10. Marcas de peça com seção entre parênteses (`P-01 (50x60cm)`, `V-03 (55x60cm)`), grupos de peças iguais num só painel com todas as marcas listadas no título.
11. Chapas `CHt`, parafusos `PAR.Øx"-A307/A325`, furos ovais `Ø a x b`, cantoneiras `L a x t`, U enrijecidos `UE h x b x d x t`, tubos `TB H x L x e`, barras `BRØ`; perfis escritos ao longo das barras nas treliças.
12. Símbolos de solda AWS (filete com tamanho, solda de campo preenchida) + tabela de filete mínimo por espessura de chapa; nota "soldas conforme AWS D1.1".
13. Detalhes típicos de cobertura sempre presentes: suporte de terça (por tipo de terça), travamento das terças (corte com furo oval), mão-francesa, fixação de tirantes, presilha com tabela Gmax, ligação diagonal-montante com tabela Lmin, emenda de banzo, coluna com tesoura, base tipo (planta + corte com chumbador, graute e F.I.C.B.).
14. Planta de terças com cadeia de espaçamento no topo e na base, inclinação com triângulo e percentual, tirantes rígidos/flexíveis diferenciados e, em executivo, marca numérica por terça ligada à lista (qtd, comprimento, peso).
15. Fôrma de viga = PLANTA + SEÇÃO longitudinal + seções transversais numeradas (dente, olhal, insert); fôrma de pilar = elevação vertical como montado com cálice (traço-ponto + ranhuras), consolos, cadeias de cotas nos dois lados (geometria à esquerda, inserts à direita) e níveis.
16. Inserts detalhados uma vez (planta + seção 1:10, itens numerados) com quantidade de uso `(17x)`, `PROJEÇÃO INSERTS` para a face oculta e quadro `QUANTITATIVO MATERIAIS INSERTS`.
17. Símbolos de classe de concreto (hexágono `E-1`) e acabamento (triângulo `F-2`) apontando para as faces + quadros `PROPRIEDADES DO CONCRETO` e `ACABAMENTO DE FÔRMA`.
18. Armadura: barras desenhadas individualmente fora da peça com `n Nx Øb C/e C=L`, trechos e `Ri`, posição em bolha na elevação e nas seções, miniatura da seção cotada; `TABELA DE FERROS — 1 UNIDADE` e `— N UNIDADES` com 6 colunas, resumo por bitola +10%, fck, volume de concreto e área de fôrma.
19. Olhais/ferros de içamento e furos de pinos de montagem sempre cotados nas fôrmas e armaduras; detalhe do apoio viga-pilar (neoprene, pino, adesivo) na planta de montagem.
20. Planta de montagem com seções das filas (elevações) mostrando níveis de apoio, fundo e topo de viga e topo do pilar, folga entre viga e pilar, e círculo de chamada para o detalhe do apoio.
21. Fechamento: fachada por face com fiadas de terças cotadas em cadeia vertical, níveis, marcas em bolha por fiada, hachura de telha, aberturas tracejadas, detalhe de fixação no pilar (chapa + parabolt) e lista própria (perfis, chapas, chumbadores, telhas em m², venezianas, rufos).
22. Lista de materiais com coluna DESCRIÇÃO (função da peça) e PESO TOTAL, uma lista por conjunto/prancha em executivo e lista global com `LIGAÇÕES (~10%)` em projeto básico; notas de asterisco abaixo da lista.
23. Isométrico em arame da estrutura (ou do subconjunto da prancha) na coluna direita, com eixos em bolhas.
24. Legenda de abreviaturas e de símbolos (revisão, ligação rotulada/a momento, direção portante) na folha 001.
25. Nuvem de revisão em vermelho com texto e triângulo de revisão numerado nos pontos alterados; descrição da revisão no carimbo diz o que mudou.
