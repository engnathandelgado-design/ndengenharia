---
name: "paredes-concreto-nbr16055"
description: "Use ao projetar, verificar ou revisar paredes de concreto moldadas in loco (NBR 16055) e pilares-parede (NBR 6118:2023) - espessura, armaduras mínimas, aberturas, esbeltez, cargas concentradas, juntas e cobrimento."
---

# Paredes de concreto moldadas in loco (NBR 16055) e pilar-parede (NBR 6118:2023)

Formato inspirado em skill de dimensionamento de paredes pelo ACI 318 cap. 11 (espessura mínima, armaduras mínimas, espaçamento, aberturas, esbeltez, cargas concentradas, juntas, cobrimento), reescrito para as normas brasileiras. A ART é do Nathan: todo valor com "(conferir no PDF ...)" deve ser checado no texto vigente antes de entrar em memorial.

## 1. Normas e edições

| Norma | Edição usada | Situação |
|---|---|---|
| ABNT NBR 16055 - Parede de concreto moldada no local para a construção de edificações | 2022 (válida a partir de 28/10/2022) + Emenda 1:2026 (publicada 28/05/2026) | Vigente. Substituiu a edição 2012. Conteúdo da Emenda 1:2026 não verificado - ler antes de usar |
| ABNT NBR 6118 - Projeto de estruturas de concreto | 2023 | Vigente (pilar-parede, detalhamento, cobrimento) |
| ABNT NBR 6120 / NBR 6123 / NBR 8681 | edição a confirmar (ver normas-vigentes-nd) | Ações e combinações |
| ABNT NBR 15823-1 (concreto autoadensável) | edição a confirmar | Citada pela NBR 16055 para o concreto |

Observação sobre a edição: o catálogo da Target ainda mostrava a NBR 16055 como "04/2012 vigente", mas o boletim CBIC de alterações 2022 lista a NBR 16055 publicada e válida a partir de 28/10/2022, e o boletim CBIC mai-jun/2026 lista a Emenda 1:2026. Usar 2022 + Emenda. Muitos TCCs ainda citam valores da 2012; quando o valor diverge entre edições, isso está indicado.

## 2. Escopo e quando NÃO usar

Usar para:
- edifícios em paredes de concreto moldadas no local (sistema de fôrmas metálicas/alumínio, tela soldada central), inclusive "edifício simplificado" da NBR 16055;
- pilares-parede de concreto armado (caixas de escada/elevador, núcleos, paredes de subsolo trabalhando como pilar) pela NBR 6118:2023;
- revisão de projeto de terceiros nesses sistemas.

NÃO usar para (chamar outra skill):
- painel de fechamento pré-moldado ou parede pré-moldada (NBR 16475 / NBR 9062) -> `paineis-fechamento-pre-moldados` e `projeto-estruturas-pre-moldadas`;
- muro de arrimo/contenção, parede de subsolo com empuxo como função principal -> `muros-contencao`;
- reservatório, tanque, EEE -> `tanques-reservatorios-concreto`;
- dimensionamento de seção (flexão, N-M, cisalhamento, pilar-padrão) -> `dimensionamento-concreto-armado-nbr`;
- análise global, modelo de pórtico/cascas -> `projetos-estruturais-concreto-armado-protendido` e `mef-opensees-opsvis`;
- alvenaria estrutural (NBR 16868) -> fora do escopo ND atual.

## 3. Roteiro de verificação/projeto

1. **Classificar o elemento.** Hipótese: elemento de superfície vertical comprimido.
   - NBR 6118: pilar-parede quando, em alguma das superfícies, a menor dimensão é menor que 1/5 da maior [verificado: NBR 6118 item 14.4.2.4, transcrito em Bastos (UNESP, 2017) e monografia UFRN].
   - NBR 16055: a definição de "parede" usa comprimento mínimo em função da espessura; as fontes divergem entre > 5t e > 10t (conferir no PDF, item 3 - definições).
   - Decisão: sistema parede de concreto de edifício (fôrma integral, tela central) -> NBR 16055; lâmina isolada/núcleo em estrutura reticulada -> NBR 6118 pilar-parede.
2. **Verificar se o edifício é "simplificado"** (NBR 16055 2022). Condições citadas: até 5 pavimentos, laje com vão livre até 4 m, sobrecarga até 3 kN/m² [verificado: NBR 16055:2022 item 3.9 via projeto de revisão 2022 e Master em Modelagem]; aberturas até 1,40 m, pé-direito até 3 m, pressão de vento < 1 kN/m², densidade de paredes >= 0,5 m/m² e >= 0,2 m/m² por direção, sem laje pré-moldada, uma única transição de vão até 1,40 m (conferir no PDF, item 3.9). Não simplificado -> avaliação de projeto obrigatória (CBIC 2022).
3. **Espessura mínima** (item 4).
4. **Ações e modelo:** cargas verticais por espraiamento a 45°, vento e desaprumo distribuídos às paredes por rigidez; modelo de cascas quando houver transição, aberturas grandes ou assimetria.
5. **Resistência à compressão + esbeltez** (item 4): λ = le·√12/t; obter k1, k2; nd,resist; comparar com nd por metro.
6. **Cisalhamento e flexão no plano** (vento): ver NBR 16055 item 17.6 (conferir no PDF, item 17.6) e `dimensionamento-concreto-armado-nbr`.
7. **Armaduras mínimas, espaçamento, tela simples ou dupla.**
8. **Aberturas:** vergas, contravergas, reforço em volta e nos cantos; distribuição de carga excluindo as zonas de 45° sob a abertura.
9. **Cargas concentradas e tensão de contato.**
10. **Juntas, frisos, eletrodutos embutidos.**
11. **Cobrimento e durabilidade.**
12. Decisão: preencher a tabela da seção 6; qualquer ERRO bloqueia emissão. A aba Parede das Ferramentas ND aplica as verificações principais.

## 4. Valores normativos

### 4.1 Materiais
- fck máximo considerado no cálculo: 40 MPa [verificado: NBR 16055 item 12, projeto de revisão 2022 + artigo UFCG que cita a NBR 16055:2022].
- Concreto: a 2022 recomenda concreto autoadensável de baixa retração [verificado: TCC Unichristus citando NBR 16055:2022, item a localizar no PDF].
- Microfibras contra retração plástica: comprimento 12 a 20 mm, diâmetro 12 a 18 µm, >= 2 500 km/m³ [verificado: Target/Qualidade Online 2022 e TCC Unichristus, item a localizar].

### 4.2 Espessura mínima
- Parede com altura até 3 m: t >= 10 cm [verificado: NBR 16055 itens 13.1/14.4, projeto de revisão 2022; artigo UFCG; Qualidade Online 10/2022].
- Paredes internas de edificações de até 2 pavimentos: t >= 8 cm [verificado: mesmas fontes].
- Altura > 3 m: t >= h/30 [verificado: mesmas fontes].
- Pilar-parede (NBR 6118): t >= 19 cm; entre 19 e 14 cm só em casos especiais, com γn = 1,95 - 0,05·b (b em cm) multiplicando as ações; área >= 360 cm² [verificado: NBR 6118 item 13.2.3 e Tabela 13.1, transcrito em Bastos UNESP 2017 (texto 2014); numeração confirmada nas citações de 2023 da monografia UFRN - conferir no PDF 2023].

### 4.3 Armaduras mínimas e espaçamento (NBR 16055)
- Vertical: As,v >= 0,09 % da seção de concreto (aço CA-60); até 2 pavimentos admite-se 66 % desse valor [verificado: NBR 16055:2022 item 17.3.1 via projeto de revisão 2022 e TCC UFGD (Amorim) que cita 2022; mesmo valor na 2012, TCC UFRJ].
- Horizontal: As,h >= 0,15 % da seção de concreto [verificado: mesmas fontes].
- Reduções: concreto de baixa retração, ou paredes externas até 6 m e internas até 8 m entre juntas -> 60 %; 2 pavimentos -> 40 % (conferir no PDF, item 17.3.1 - redação da 2022 difere da 2012).
- Tela dupla: vertical vale por face; para t > 18 cm a vertical pode ser reduzida em 33 % (conferir no PDF, item 17.3.1).
- Espaçamento máximo entre barras verticais e horizontais: 30 cm [verificado: NBR 16055 item 17.3.2 via projeto de revisão 2022; artigo UFCG; TCC UFGD]. UFGD acrescenta o limite 2t (conferir no PDF, item 17.3.2). Barras isoladas de ligação em edifício simplificado até 50 cm (conferir no PDF, item 17.1).
- Uma tela centrada é a regra. Tela nas duas faces obrigatória: t > 18 cm na 2022 (era t > 15 cm na 2012); térreo sujeito a choque de veículo; parede que engasta marquise ou balanço [verificado para 2012 (15 cm): TCC UFRJ; 18 cm na 2022 pelo artigo Graziano/Núcleo Parede de Concreto 2022 e projeto de revisão item 17.3.3 - conferir no PDF, item 17.3.3, porque UFGD 2023 ainda cita 15 cm].
- Fibras em edifício simplificado no lugar da armadura distribuída: dosagem mínima 4,0 kg/m³ (poliméricas e de vidro) e 8 kg/m³ (metálicas) (conferir no PDF, item 17.3.1 - valor só do projeto de revisão).
- Zona confinada nas extremidades: comprimento <= menor entre 1 m e 6t; taxa até 1,5 % em duas telas amarradas quando o cálculo pedir mais de 1 % (conferir no PDF, item a localizar - fonte: artigo Graziano).

### 4.4 Resistência à compressão e esbeltez (NBR 16055 item 17.5)
- λ = √12·le/t; le pela Figura 2 (h = piso a piso), com redução por continuidade com as lajes (Anexo B, Jackson-Moreland) (conferir no PDF, item 17.2 e Anexo B).
- Faixas [verificado: NBR 16055 item 17.5.1 via projeto de revisão 2022 e TCC UFGD]:
  - λ <= 35: k1 = 1, k2 = 0 (conferir no PDF a forma exata da faixa baixa);
  - 35 < λ <= 86: k1 = λ/35, k2 = 0;
  - 86 < λ <= 120: k1 = λ/35, k2 = (λ - 86)/35;
  - λ > 120: fora do método da norma -> ERRO (redimensionar t).
- nd,resist = (0,85·fcd + ρ·fscd)·t / [k1·(1 + 3·k2·(2 - k2))], com fscd = Es·0,002/γs, ρ = taxa vertical (até 1 %) [verificado na forma: projeto de revisão 2022 e TCC UFGD]. O γc aplicado (1,4 ou 1,4·1,2 = 1,68) e o teto da expressão (0,4·fcd·t; UFGD cita também divisor 1,643) divergem entre fontes (conferir no PDF, item 17.5.1). Não usar a fórmula em memorial sem conferir.
- Método alternativo (item 17.5.4): limite 0,4·fcd·t (tela centrada) e 0,63·fcd·t (duas telas amarradas), válido para λ < 90 (conferir no PDF, item 17.5.4 - fonte: artigo Graziano e projeto de revisão).
- Pilar-parede NBR 6118: dispensa de 2ª ordem localizada se a base e o topo de cada lâmina estão fixados às lajes e λi < 35; processo aproximado para 35 <= λi <= 90, dividindo a lâmina em faixas de largura ai = 3h <= 100 cm tratadas como pilares isolados [verificado: NBR 6118 itens 15.9.2 e 15.9.3, monografia UFRN (texto 2014)].

### 4.5 Aberturas
- Abertura com dimensão horizontal >= 40 cm: armadura horizontal nas faces superior (verga) e inferior (contraverga), dimensionada por modelo elástico ou biela-tirante [verificado: NBR 16055 item 17.8 via projeto de revisão 2022, TCC UFGD e artigo UFCG].
- Mínimos: verga >= 1 cm²; contraverga >= 0,5 cm² [verificado: mesmas fontes].
- Borda superior livre do último pavimento: + 1 cm² numa faixa de altura 2t (conferir no PDF, item 17.4).
- Carga vertical redistribuída excluindo as zonas definidas por planos a 45° tangentes às bordas da abertura (conferir no PDF, item 11.3.3).
- Distância entre aberturas: na 2012, trecho entre aberturas menor que a soma das metades dos vãos -> tratar como pilar-parede [verificado para 2012: TCC UFRJ] (conferir no PDF 2022, item a localizar).
- Barras diagonais nos cantos: a NBR 16055 não traz valor nas fontes consultadas; a ND adota 1 a 2 barras Ø 8-10 mm a 45° em cada canto, l >= 2·lb (prática ND, inspirada no ACI 318 - não é exigência normativa verificada).

### 4.6 Cargas concentradas
- Espraiamento a 45° na parede [verificado: NBR 16055 item 11.3.2 via projeto de revisão 2022 e artigo UFCG].
- Tensão de contato de cálculo de elementos não contínuos (viga apoiada, laje de transição): σcont,d <= 0,85·fcd (conferir no PDF, item 17.7).
- Carga concentrada sobre lintel/verga ou próxima à borda: verificar como bloco parcialmente carregado (NBR 6118, item 21.2) e armadura de fendilhamento (conferir no PDF NBR 6118, item 21.2).

### 4.7 Juntas, frisos e eletrodutos (NBR 16055 item 13)
- Juntas verticais de controle, sem ensaio de retração: espaçamento <= 8 m (internas) e <= 6 m (externas); profundidade mínima recomendada 2 cm [verificado: NBR 16055 item 13.2.1, projeto de revisão 2022 + Qualidade Online 10/2022].
- Junta de dilatação: recomendada a cada 30 m em planta e em mudança brusca de geometria ou carga vertical [verificado: item 13.2.3, mesmas fontes].
- Junta horizontal sob a última laje: opcional, com reforço de borda (conferir no PDF, item 13.2.2).
- Frisos: profundidade <= t/10, largura <= 10 cm, um horizontal por pavimento, espaçamento vertical > 30t [verificado: Qualidade Online 10/2022, item a localizar no PDF].
- Eletroduto vertical: Ø <= 25 % de t sem reforço, afastamento 5 cm; até 50 % de t com tela nas duas faces (largura >= 60 cm); tubo metálico não admitido; horizontal não admitido salvo trecho não estrutural <= 1/3 do comprimento e <= 1 m; nada a menos de 3t de encontro de paredes [verificado: Qualidade Online 10/2022, item a localizar no PDF].

### 4.8 Cobrimento
- Paredes seguem os cobrimentos da NBR 6118 para pilares [verificado: NBR 16055 item 7 via projeto de revisão 2022 e Qualidade Online].
- Cobrimento nominal de pilar (Δc = 10 mm): CAA I 25 mm, II 30 mm, III 40 mm, IV 50 mm (conferir no PDF NBR 6118:2023, item 7.4.7.2, Tabela 7.2). Com tela centrada em parede de 10 cm o cobrimento real é ~ 4,5 cm de cada lado; o crítico é a posição da tela na fôrma (espaçador).

### 4.9 Pilar-parede - detalhamento (NBR 6118)
- Armadura longitudinal: As,mín = 0,15·Nd/fyd >= 0,4 % Ac; As,máx = 8 % Ac incluindo traspasse [verificado: NBR 6118 item 17.3.5.3, Scadelai & Pinheiro (texto 2003) e TCC UFGD (texto 2014)] (conferir no PDF 2023, item 17.3.5.3 - redação de 4 % fora da emenda).
- Barras longitudinais: Ø >= 10 mm e <= 1/8 da menor dimensão; espaçamento entre eixos <= 2b e <= 400 mm [verificado: NBR 6118 item 18.4.2, Scadelai & Pinheiro e monografia UFRN].
- Estribos: Ø >= 5 mm e >= Øl/4; espaçamento <= 200 mm, <= menor dimensão, <= 12Øl (CA-50) [verificado: NBR 6118 item 18.4.3, mesmas fontes].
- Armadura transversal do pilar-parede, sem cálculo de flexão de placa: >= 25 % da armadura longitudinal por metro da maior face da lâmina [verificado: NBR 6118 item 18.5, monografia UFRN (paráfrase)] (conferir no PDF 2023, item 18.5 - texto completo sobre grampos e estribos suplementares).

## 5. Prática ND / erros comuns de obra e fábrica

- Tela deslocada para a face na concretagem (falta de espaçador ou caranguejo): a tela centrada vira tela de face, muda o braço e o cobrimento. Exigir espaçador a cada ~ 50 cm e conferência antes de fechar a fôrma.
- Eletroduto e caixa elétrica agrupados no mesmo trecho, ou passando a menos de 3t do canto: furo na parede estrutural. Compatibilizar com `revisao-compatibilizacao-instalacoes` antes de liberar fôrma.
- Abertura de janela ou porta deslocada na obra sem consulta: muda verga, zona de 45° e distância entre aberturas. Tratar como alteração de projeto.
- Fissura a 45° no canto de abertura: falta de barra diagonal ou de concreto de baixa retração; cura mal feita nas primeiras 24 h.
- Desforma precoce com fôrma de alumínio no ciclo de 1 dia: verificar resistência mínima de desforma e escoramento das lajes.
- Junta de controle esquecida em parede externa longa: fissura vertical regular a cada 4-6 m.
- Projeto de "edifício simplificado" que não atende alguma condição (vão > 4 m, laje pré-moldada, transição) e foi calculado como simplificado: refazer como não simplificado.
- Pilar-parede de núcleo calculado só no ELU global sem 2ª ordem localizada nas extremidades da lâmina.
- Concreto autoadensável sem controle de espalhamento: ninho sob janela e no pé da parede.

## 6. Tabela final de verificação

| Verificação | Condição de falha | Ação |
|---|---|---|
| Edição da norma | Memorial citando NBR 16055:2012 ou ignorando a Emenda 1:2026 | ALERTA: atualizar para 2022 + Emenda 1:2026 |
| Classificação | Edifício declarado simplificado sem atender todas as condições | ERRO: recalcular como não simplificado (NBR 16055 item 3.9) |
| Espessura | t < 10 cm (h <= 3 m), t < 8 cm interna até 2 pav., ou t < h/30 | ERRO: aumentar t (NBR 16055 itens 13.1/14.4) |
| Espessura pilar-parede | t < 19 cm sem γn, ou t < 14 cm, ou A < 360 cm² | ERRO: redimensionar (NBR 6118 item 13.2.3) |
| fck | fck de cálculo > 40 MPa | ERRO: limitar a 40 MPa no cálculo (NBR 16055 item 12) |
| Esbeltez | λ > 120 (NBR 16055) ou λi > 90 sem método específico (NBR 6118) | ERRO: aumentar t ou travar a parede (NBR 16055 item 17.5.1; NBR 6118 item 15.9.3) |
| Compressão | nd > nd,resist | ERRO: aumentar t, fck ou ρ (NBR 16055 item 17.5) |
| Armadura vertical | As,v < 0,09 % Ac (ou redução não justificada) | ERRO: aumentar tela (NBR 16055 item 17.3.1) |
| Armadura horizontal | As,h < 0,15 % Ac (ou redução não justificada) | ERRO: aumentar tela (NBR 16055 item 17.3.1) |
| Espaçamento | s > 30 cm | ERRO: reduzir espaçamento (NBR 16055 item 17.3.2) |
| Tela dupla | t > 18 cm, choque de veículo ou engaste de balanço com tela única | ERRO: duas telas amarradas (NBR 16055 item 17.3.3) |
| Abertura | Vão >= 40 cm sem verga >= 1 cm² e contraverga >= 0,5 cm² | ERRO: detalhar verga/contraverga (NBR 16055 item 17.8) |
| Cantos de abertura | Sem barra diagonal | ALERTA: incluir diagonais (prática ND) |
| Trecho entre aberturas | Menor que a soma das metades dos vãos | ALERTA: verificar como pilar-parede |
| Carga concentrada | σcont,d > 0,85·fcd ou bloco parcialmente carregado sem fendilhamento | ERRO: aumentar apoio ou armar (NBR 16055 item 17.7; NBR 6118 item 21.2) |
| Juntas | Parede externa > 6 m ou interna > 8 m sem junta e sem ensaio | ALERTA: prever junta de controle (NBR 16055 item 13.2.1) |
| Junta de dilatação | Planta > 30 m sem junta | ALERTA: prever junta ou justificar (NBR 16055 item 13.2.3) |
| Eletroduto | Ø > 25 % t sem tela nas faces, > 50 % t, metálico ou horizontal estrutural | ERRO: relocar (NBR 16055 item 13, a localizar) |
| Cobrimento | Abaixo da Tabela 7.2 para a CAA | ERRO: corrigir espaçador/cobrimento (NBR 6118 item 7.4.7) |
| Pilar-parede longitudinal | As < 0,15 Nd/fyd ou < 0,4 % Ac; > 8 % na emenda | ERRO: ajustar armadura (NBR 6118 item 17.3.5.3) |
| Pilar-parede transversal | < 25 % da longitudinal por metro da maior face | ERRO: aumentar transversal (NBR 6118 item 18.5) |
| Valores "(conferir no PDF)" | Usados no memorial sem conferência | ALERTA: conferir no texto vigente antes de emitir |

## 7. Ligação com outras skills

- `dimensionamento-concreto-armado-nbr` - N-M, cisalhamento, pilar-padrão das faixas de pilar-parede.
- `projetos-estruturais-concreto-armado-protendido` - análise global, vento, estabilidade (γz), modelo de cascas.
- `mef-opensees-opsvis` - modelo de casca para parede com aberturas e transição.
- `muros-contencao` - paredes de subsolo com empuxo.
- `paineis-fechamento-pre-moldados` - quando a parede é pré-moldada.
- `revisao-compatibilizacao-instalacoes` - eletrodutos e furos em parede estrutural.
- `revisao-engenheiro-senior` - revisão final do memorial.
- `orcamentista-obras` - quantitativo de tela, fôrma e concreto do sistema.
- `normas-vigentes-nd` - edição e protocolo de citação.

## Fontes consultadas

- CBIC, Alterações de normas técnicas 2022 (NBR 16055 válida a partir de 28/10/2022): https://cbic.org.br/wp-content/uploads/2023/01/alteracoes-de-normas-tecnicas-setor-da-construcao-civil-2022.pdf
- CBIC, Boletim de normas técnicas mai-jun/2026 (Emenda 1:2026): https://cbic.org.br/wp-content/uploads/2026/06/boletim-de-normas-tecnicas-setor-da-construcao-civil-mai-e-jun26.pdf
- CBIC, consulta nacional da revisão (2022): https://cbic.org.br/inovacao/?p=7769
- Projeto de revisão NBR 16055 (09/02/2022), cópia em PDFCoffee: https://pdfcoffee.com/abnt-nbr-16055-revisao-2022-02-09-pdf-free.html
- Graziano, F. Recomendações NBR 16055 nova revisão (Núcleo Parede de Concreto, 2022): https://nucleoparededeconcreto.com.br/wp-content/uploads/2022/11/Artigo-Graziano_projeto-estrutural_SET22_v3.pdf
- Qualidade Online, parâmetros normativos da NBR 16055 de 10/2022: https://qualidadeonline.wordpress.com/2022/11/24/os-parametros-normativos-para-a-construcao-de-paredes-de-concreto-moldadas-in-loco/
- Artigo UFCG (cita NBR 16055:2022): https://revistas.editora.ufcg.edu.br/index.php/cicufcg/article/download/3902/4359/13023
- TCC UFGD, Amorim (cita NBR 16055:2022): https://repositorio.ufgd.edu.br/jspui/bitstream/prefix/5581/1/WellingtonValterDuartedeAmorim.pdf
- TCC Unichristus, Sousa (cita NBR 16055:2022): https://repositorio.unichristus.edu.br/jspui/bitstream/123456789/1723/1/Vanessa%20Araujo%20de%20Sousa.pdf
- TCC UFRJ Macaé, Zanon (NBR 16055:2012): https://ipoli.macae.ufrj.br/wp-content/uploads/2023/11/TCC_Diego_Medeiros_Zanon_Civil.pdf
- TCC UFRGS 2023 (NBR 16055:2022 na obra): https://lume.ufrgs.br/handle/10183/268453
- Master em Modelagem, guia NBR 16055:2022: https://www.masteremmodelagem.com.br/post/paredes-de-concreto-moldadas-no-local-guia-completo-de-dimensionamento-segundo-a-nbr-16055-2022-e-n
- Monografia UFRN sobre pilares-parede (NBR 6118): https://repositorio.ufrn.br/server/api/core/bitstreams/8acf93d2-3d85-461f-b590-78d6c5fc6b32/content
- Bastos, P. S. S., Pilares (UNESP, 2017; NBR 6118:2014): https://professor.pucgoias.edu.br/sitedocente/admin/arquivosUpload/14026/material/Pilares.pdf
- Scadelai & Pinheiro, Pilares (UNICAMP/USP; NBR 6118:2003): https://www.fec.unicamp.br/~almeida/ec802/Pilares/16%20Pilares.pdf
- Target/normas.com.br, ficha NBR 16055: https://normas.com.br/visualizar/abnt-nbr-nm/31807/abnt-nbr16055-parede-de-concreto-moldada-no-local-para-a-construcao-de-edificacoes-requisitos-e-procedimentos