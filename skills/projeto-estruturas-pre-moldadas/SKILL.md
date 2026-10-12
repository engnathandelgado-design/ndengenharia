---
name: "projeto-estruturas-pre-moldadas"
description: "Use ao conceber, projetar, calcular, detalhar, modelar, orçar ou ensinar sistemas estruturais pré-moldados de concreto (galpões, esqueleto, pisos alveolares/TT, paredes e fachadas, ligações, estabilidade, integridade, incêndio, ligações semirrígidas e γz em esqueleto, cisalhamento de alveolar com capa/alvéolos preenchidos, consolos e chumbadores, cálice em bloco sobre estacas, reforço de ligação)."
---

# Projeto de sistemas estruturais pré-moldados — concepção, cálculo, detalhe, modelo e orçamento

Skill de **sistema** (o edifício pré-moldado como um todo). Peça isolada e fábrica ficam nas skills irmãs:
- `consultoria-fabricas-pre-moldados`: NBR 9062 (tolerâncias, cálice, apoios, elastômero), fases transitórias, checklist de detalhamento por peça, produção, montagem, contratação, patologias.
- `vigas-premoldadas-protendidas`: viga pré-tracionada, prancha de produção.
- `projetos-estruturais-concreto-armado-protendido`: protensão, perdas, ELS/ELU, seção composta, interface, dente Gerber, ligação semirrígida (beam-line), MEF; Parte D = software ND.
- `mef-opensees-opsvis`: modelos OpenSeesPy · `orcamentista-obras`: custos · `pranchas-tecnicas-nd`: pranchas · ferramenta ND de consolos/dentes Gerber.

Responder em português técnico; prática primeiro, justificativa normativa depois; (conferir) = checar na norma vigente antes de usar em projeto.

## 1. Fonte e nível
- Van Acker, A. (fib Commission 6) — *Planning and Design Handbook on Precast Building Structures* (fib/BIBM, 2002), tradução e notas de Marcelo A. Ferreira (NETPRE/UFSCar) como "Manual de Sistemas Pré-Fabricados de Concreto": caps. 1–9 + 2 apresentações (Cap. 1 Considerações preliminares; Cap. 2 Sistemas). Lido na íntegra em 07/10/2026 (texto extraído + tabelas conferidas em imagem).
- Base normativa do original: Eurocode 2 (EN 1992-1-1 e 1-2, versões 2000–2002), BS 8110, DIN 1045, CEB-FIB MC 78, fib Bulletin 6, PCI. **Converter para**: NBR 9062:2017 (pré-moldados), NBR 6118:2023, NBR 15200:2012 (incêndio, conferir edição) + NBR 14432 (TRRF), NBR 14861 (lajes alveolares, edição 2022 — conferir), NBR 16475:2017 (painéis de parede — conferir), NBR 8681 (combinações), NBR 6123 (vento).
- Ferreira, M. A.; Araújo, D. L.; Jeremias Jr., A. C.; Catoia, B.; Kataoka, M. N. — *Estabilidade global de estruturas pré-moldadas: efeito das ligações semi-rígidas* (apresentação NETPRE/UFSCar + UFG, apoio FAPESP; base NBR 6118:2003). Lido na íntegra (33 slides, texto + gráficos) em 07/10/2026 → seção 4.5 e 13.1.
- *Cadernos de Engenharia de Estruturas* (EESC-USP), v. 11, n. 53, 2009 — **Edição Especial ENDOSET 2009** (resumos expandidos de doutorado/mestrado do SET-EESC; 202 p., hospedado na página de pré-moldados do Prof. Paulo Bastos/UNESP). Lidos na íntegra em 07/10/2026 os 9 artigos de pré-moldado/ligações → **seção 16**. Pesquisas em andamento (resultados parciais) — usar como tendência e referência, não como critério normativo.
- Nível: graduação/pós e projetista; conceitual, com poucas fórmulas. As notas do tradutor corrigem o original em pontos importantes (ligações semirrígidas — ver 4.2).

## 2. Filosofia de projeto (o que sempre defender com o cliente e o arquiteto)
1. **Pré-moldado não é moldado in loco feito em outro lugar**: a estrutura nasce pré-moldada desde o estudo preliminar; adaptar projeto convencional perde as vantagens (custo/ligações).
2. Cinco princípios: (a) respeitar a filosofia do sistema — **contraventamento próprio, grandes vãos, integridade estrutural**; (b) **soluções padronizadas** (modulação, produtos de catálogo, detalhes internos padrão: programas, fck, armaduras, ligações, insertos, procedimentos); (c) **detalhes simples** (consolo em "coroa" nos 4 lados = difícil → usar 4 consolos simples ou concretar em 2 etapas; poucas bitolas, telas, raios de dobra, sem congestionamento); (d) **tolerâncias absorvidas nas ligações** (almofadas, ajuste nas 3 direções, contraflecha, movimentos de retração/temperatura); (e) **aproveitar a industrialização** (pré-tração em pista, peças repetidas, esperas na face superior da fôrma, nada de alteração de última hora).
3. **Não pré-moldar tudo**: pequenas áreas de piso, cantos triangulares, vãos < 2 m e bordas irregulares → moldar in loco junto com o chaveteamento/capa.
4. Vantagens a argumentar (valores do manual, Europa): prazo < metade do convencional; montagem contínua no frio; CAD > 100 MPa já rotineiro (pilar 30→90 MPa: +100 a 150 % de capacidade); CAA (sem vibração, menos bolhas, fôrma com menos pressão); 60 min de fogo sem medida especial, 90–120 min aumentando cobrimento; até −45 % materiais, −30 % energia, −40 % resíduo de demolição; adaptabilidade (estrutura ≥ 100 anos, fachada 30–60, instalações ~20 → subsistemas trocáveis).
5. Instalações integradas: eletrodutos/caixas em painéis, **tubo de águas pluviais dentro do pilar**, manta colada na telha na fábrica, dutos nos alvéolos (ativação térmica: > 30 % de economia). Tudo isso exige **instalações definidas antes** do projeto de produção.

## 3. Sistemas estruturais e escolha por tipologia
| Sistema | Composição | Uso |
|---|---|---|
| Aporticado (traves planas) | pilares engastados na fundação + viga de cobertura biapoiada | galpões, armazéns, indústria, comércio, ginásios (até ~40 m) |
| Esqueleto | pilares + vigas + lajes; estabilidade por pilares em balanço (≤ 3–4 pav., ≤ ~10 m) ou núcleos/paredes | escritórios, escolas, hospitais, estacionamentos, até 20+ pav. |
| Painéis portantes | paredes + lajes (transversais ou "envelope") | habitação, hotéis; paredes internas leves para flexibilidade |
| Pisos | alveolar, TT/π, maciça, pré-laje treliçada, vigota + bloco | todo tipo, também sobre aço/in loco |
| Fachadas | maciças ou sanduíche, portantes ou não | qualquer edifício |
| Células | módulos 3D (banheiros, shafts) | pouco flexível, transporte difícil |

Diretrizes de escolha por uso (cargas e vãos do manual):
- **Residência**: vãos 4–11 m, q ≈ 2 kN/m², face inferior lisa, ~60 min; vigota (Brasil, MO barata), alveolar estreita, pré-laje, alveolar 1,20 m.
- **Apartamentos**: grua no canteiro → alveolar protendida ou pré-laje; lajes de fachada a fachada até 11 m.
- **Escritórios**: grandes espaços, vãos 18–20 m, núcleos de contraventamento; **alveolar 400 mm vence 17 m com 5 kN/m²; 500 mm → 21 m**; < 6 m pré-laje (escorada).
- **Hotéis/hospitais**: q ≈ 5 kN/m², alveolar ou nervurada.
- **Escolas**: 8–12 m (salas), > 24 m (auditórios), q 3–4 kN/m²; TT para vãos maiores; viga-jacaré para arquibancada.
- **Industrial**: pórticos com pilares engastados; mezanino 8/12–15 m, q 5 a 15–20 kN/m² (o original escreve "5 até 1,5/2" — é 15/20) → TT é a única solução para os maiores vão × carga; alternativa: TT de cobertura duas águas sobre painéis portantes (vão até 32 m, módulo 2,4 m, pé-direito até 8 m).
- **Estacionamentos**: vãos 12–16 m (modulação 9,60 × 16 m), alveolar ou TT; pilares em balanço + núcleos de escada/elevador; níveis desencontrados com 2 vigas L costas com costas (desnível > ~750 mm).
- **Esportes**: pórticos até ~40 m; arquibancada com vigas dentadas + alveolar fina; cobertura em balanço com chumbadores protendidos (Dywidag).

## 4. Estabilidade global
### 4.1 Conceitos
- **Não contraventada (nós deslocáveis)**: pilares engastados na base em balanço; vigas articuladas. Bom até ~3 pavimentos (o manual limita a ~10 m de altura sem estabilização adicional por dimensão de pilar e deslocamento). Pode receber pórticos 2-D localizados ou diagonais metálicas.
- **Contraventada (nós fixos)**: núcleos (escada/elevador), paredes de cisalhamento, diagonais; pilares bi-rotulados entre pavimentos, fundação pode ser articulada, pilares mais esbeltos (menor l0), ligações simples. **Solução mais eficaz para múltiplos pavimentos**, pois núcleos já existem por função (custo adicional desprezível). Acima de 3 pavimentos o manual recomenda contraventar.
- **Ação de pórtico** (ligações viga-pilar resistentes a momento): pouco usada na Europa (forças concentradas, montagem difícil); pórticos em TT/H pré-moldados → transporte/içamento ruins, não recomendados. No Brasil a ligação semirrígida (NBR 9062:2017, αR) é usada — ver 4.5 e skill principal 10.9.
- **Diafragma**: laje como viga-parede horizontal apoiada nos núcleos/paredes (modelo arco + tirante); tirante = armadura periférica; cisalhamento nas juntas longitudinais (atrito, intertravamento do agregado, pino). **Cobertura leve (telha metálica/fibrocimento) não é diafragma** → contraventamento em X (barras/cantoneiras) entre vigas nos vãos extremos, ou cada pórtico resiste sozinho.
- Distribuição da força horizontal entre núcleos/paredes: proporcional à rigidez; centro de rigidez = centro de massa/força (evitar torção; núcleo excêntrico → paredes nas extremidades). Parede com grande abertura: só conta o trecho cheio, salvo se a parte acima da abertura trabalhar.
- **Juntas de dilatação do diafragma**: ~80 m (planta retangular) ou ~60 m (não retangular), dependendo de clima, estrutura e fundação.
- Regularidade em planta e altura sempre que possível. Analisar em 3D: as duas direções podem ter sistemas diferentes (ex.: núcleo numa, pilares em balanço noutra) e o sistema pode mudar com a altura (paredes embaixo, pórtico em cima).

### 4.2 Ligação viga-pilar com chumbador: articulada ou semirrígida? (nota do tradutor)
- Original: "pilares contínuos engastados + ligações viga-pilar articuladas". Tradutor (Ferreira 1999; Engström 1992): chumbadores **não são rótulas perfeitas**; em grandes deslocamentos surge binário (chumbador tracionado + concreto comprimido) → reserva de rigidez/resistência (útil em incêndio e colapso). Pela classificação semirrígida (EC3 → NBR 9062:2017, αR), a rigidez em serviço é baixa o bastante para **projetar como articulada** e tratar o resto como reserva.
- Na Europa (Itália) o chumbador é rosqueado e aparafusado no topo da viga (mecanismo diferente do Brasil, onde se usa chumbador grauteado + almofada de elastômero ou argamassa).

### 4.3 Modelagem (OpenSees / software ND)
- Galpão: pórtico plano por eixo; pilares engastados (cálice) com rigidez fissurada NLF (NBR 6118 15.7.3 / NBR 9062 — conferir coeficientes para pré-moldado); vigas biarticuladas (ou mola Rsec ↔ αR, 4.5); força de vento NBR 6123 + imperfeição (4.4); 2ª ordem (γz ou P-Δ). Sem diafragma: cada pórtico com a sua faixa de vento; com diafragma: nós do topo vinculados (rigid diaphragm) e a força distribuída pela rigidez.
- Esqueleto contraventado: núcleo como barra de parede (ou casca) + pilares bi-rotulados (só carga vertical); verificar o diafragma à parte (arco-tirante) e a torção (CR × CM).
- **Fases de montagem**: estrutura incompleta, sem diafragma e com ligações provisórias (vento na montagem, escoramento).
- Código: `mef-opensees-opsvis` (pórtico) e skill principal seção 21.

### 4.4 Imperfeições geométricas (EC2 5.2, citado no manual cap. 7)
θi = θ0·αh·αm, θ0 = 1/200, αh = 2/√l (2/3 ≤ αh ≤ 1, l em m), αm = √[0,5(1 + 1/m)] (m = nº de elementos que contribuem). Força no diafragma Hi = θi(Nb + Na)/2; no elemento de contraventamento Hi = θi(Nb − Na)/2. Simplificação CEB-FIB 78 para paredes: 1 % da carga vertical do andar, mín. 30 kN/m de painel (conferir). Pela NBR 6118 11.3.3.4: θ1 = 1/(100√H) ≥ 1/300 (pilar isolado 1/200 máx.) e θa = θ1·√[(1+1/n)/2] — **usar a NBR no projeto** (mesma forma do EC2).

### 4.5 Estabilidade global com ligações viga-pilar semirrígidas (Ferreira et al., NETPRE/UFSCar)
**Ideia central:** em esqueleto de múltiplos pavimentos, a armadura de continuidade na capa (grauteada no nível da laje) sobre consolo + chumbador transforma a ligação "articulada" em semirrígida e a estrutura passa a trabalhar como **pórtico** → menor deslocamento, menor momento na base do pilar, menor comprimento efetivo e γz menor. Só vale se a rigidez da ligação for conhecida (ensaio ou expressão normativa).
- **Curva momento-rotação (M-φ)**: rígida ideal (monolítica) → monolítica real (rigidez alta, finita) → semirrígida de alta/baixa rigidez e resistência. Parâmetros: My, Mu, rigidez secante **Ssec = Rsec** (PCI 1988: secante no ponto de escoamento / diagrama bilinear). O ponto E (ME, φE) é o cruzamento da curva M-φ com a **beam-line** da viga (reta entre M de engaste perfeito MR com φ = 0 e M = 0 com φ da viga biapoiada).
- **Fator de restrição**: αR = [1 + 3·(EcI)viga/(Rsec·Lviga)]⁻¹ (NBR 9062:2017 adota o mesmo αR — conferir item). Inversa: Rsec = 3EI/[L(1/αR − 1)].
- **Engastamento parcial**: ME/MR = 3αR/(2 + αR) (viga com carga uniforme e duas ligações iguais). Pares úteis: αR 0,14 → 20 %; 0,40 → 50 %; 0,67 → 75 %; 0,86 → 90 %; 0,71 → 80 %.
- **Classificação Ferreira & Elliott (2002)** (zonas da beam-line):

| Zona | ME/MR | αR | Critério de projeto |
|---|---|---|---|
| I articulada | < 0,20 | < 0,14 | ductilidade (capacidade de rotação) |
| II semirrígida baixa | 0,20–0,50 | 0,14–0,40 | resistência |
| III semirrígida média | 0,50–0,75 | 0,40–0,67 | resistência + rigidez + ductilidade |
| IV semirrígida alta | 0,75–0,90 | 0,67–0,86 | resistência + rigidez |
| V rígida | ≥ 0,90 | ≥ 0,86 | resistência |

NBR 9062:2017 usa 3 faixas: αR ≤ 0,15 articulada; 0,15 < αR < 0,85 semirrígida; ≥ 0,85 rígida (conferir), e traz expressão de Rsec para ligação com armadura de continuidade + consolo + chumbador do tipo k·As·Es·d²/Le (conferir k e Le na norma — não usar sem o texto).
- **Ensaios de referência** (curvas M-φ comparadas no artigo): Stanton et al. (1999, PCI) — armadura de continuidade + chapa soldada (BC-16, BC-26) e viga pré-moldada com pilar moldado in loco; Gorgun (1999) — continuidade + consolo metálico (BC-TW1); **Ferreira (2001) — continuidade + consolo de concreto + chumbador (BC-16A)** = a ligação típica brasileira.
- **Parâmetros de instabilidade** (o artigo usa NBR 6118:2003; mesmos na 2023): α = Htot·√[Nk/(EcsIc)] ≤ α1, α1 = 0,2 + 0,1n (n ≤ 3) ou 0,6 (n ≥ 4; 0,7 só pilares-parede; 0,5 só pórticos) — 15.5.2; γz = 1/(1 − ΔMtot,d/M1,tot,d) — 15.5.3: ≤ 1,10 nós fixos; ≤ 1,30 permite os esforços finais por **0,95γz × ações horizontais** (15.7.2); acima de 1,30 → análise P-Δ/NLG rigorosa. **NBR 6118 só aceita γz para estruturas reticuladas com ≥ 4 andares** (o slide de conclusões diz "menos de 4" — erro de digitação ou ressalva do autor; seguir a norma e, abaixo de 4 andares, conferir com P-Δ).
- **NLF simplificada usada**: vigas 0,4EcI, pilares 0,8EcI (NBR 6118 15.7.3; conferir se a NBR 9062:2017 pede outro coeficiente para pilar pré-moldado em pórtico com ligação semirrígida).

**Exemplo numérico do artigo (refeito e validado — 13.1):** pórticos de 3, 5, 7 e 10 pavimentos, 3 vãos × 6,5 m, pé-direito 4 m, vigas 30×60, pilares 50×50, C30, Ec = 35 GPa, combinação Fd = 1,3Fg + 1,4(0,7Fq + Fv) — as cargas do desenho já são de cálculo: horizontais 35/42/49…/28 kN (topo 28), q = 60 kN/m nos pisos e 30 kN/m na cobertura, 171/344/344/171 kN nos pilares **em todos os níveis** (o desenho mostra só no topo, mas só assim os gráficos fecham). Base engastada nos gráficos αR × resposta; casos A/B/C variam a base (αR 0,71 ≈ 80 %).

| Resultado (5 pav., P1) | αR → 0 | 0,14 (20 %) | 0,40 (50 %) | 1,0 |
|---|---|---|---|---|
| Deslocamento topo 1ª ordem | 0,42 m | 0,14 m | 0,061 m | 0,023 m |
| γz | instável (≈ 7,7) | 1,46 | 1,19 | 1,07 |
| M base P1, 1ª ordem | 600 kN·m (= ΣH·h/4) | 310 | 196 | 101 |

γz × engastamento: 3 pav. 1,13 (20 %) → 1,03 (100 %); 7 pav. 2,3 (20 %), 1,35 (50 %), 1,11 (100 %). Caso C (pilar 40×40, base 80 %): γz = 2,0 com 20 % e 1,12–1,15 com 100 %.

**Conclusões do artigo (para usar em projeto):**
1. Com engastamento parcial < 20 % (3 e 5 pav.) ou < 50 % (≥ 7 pav.) a estrutura deixa de trabalhar como pórtico — confirma a classificação acima: ligação zona I conta como articulada.
2. **Sem ensaio da ligação, só confiar no pórtico semirrígido se a estrutura, considerada perfeitamente rígida, tiver γz < 1,10** (margem para a perda de rigidez real).
3. γz aproxima bem a NLG (P-Δ) para αR > 0,14; majorar as ações horizontais por γz **sem** o 0,95 ficou mais próximo da NLG (a favor da segurança).
4. Rigidez do pilar e da ligação pilar-fundação pesam tanto quanto a ligação viga-pilar (casos A/B/C); a altura do pórtico eleva rápido a exigência de αR (γz ≤ 1,3: 3 pav. qualquer αR; 5 pav. αR ≳ 0,27; 7 pav. αR ≳ 0,47; 10 pav. αR ≳ 0,7).

**Roteiro ND:** (1) definir o detalhe da ligação (continuidade na capa + consolo + chumbador) e obter Rsec (ensaio/NBR 9062 — conferir); (2) αR por vão; classificar; (3) pórtico com molas (`estab_semirrigida_nd.py` ou OpenSees `zeroLength`) e NLF 0,4/0,8; (4) γz da hipótese **rígida** < 1,10 (sem ensaio) e γz real ≤ 1,30; (5) esforços finais por γz (ou P-Δ se > 1,3); (6) dimensionar a ligação para ME = αR-coerente **e** a viga para o caso biapoiado (envoltória); (7) checar fases de montagem (antes do graute da capa a ligação é articulada).

## 5. Integridade estrutural, tirantes e colapso progressivo
- Pré-moldado é **mais sensível a ações excepcionais** (explosão de gás, impacto de veículo, recalque) por causa das juntas → rede **tridimensional de tirantes** contínuos (barra com traspasse, luva, rosca), nas faixas de concreto in loco, alvéolos abertos, bainhas ou juntas: (1) internos do piso, (2) de borda, (3) de oitão, (4) piso-parede, (5) de continuidade em vigas internas, (6–7) periféricos, (8) de pilar de canto (2 direções), (9) pilar-viga, (10) verticais pilar-pilar, (11) verticais parede-parede.
- Valores (ELU; EC2 9.10.2, recomendados): **periférico Ftie = 10 kN/m × l ≥ 70 kN** (l = vão do piso); **interno ao longo da linha de vigas (piso sem capa): Ftie = q3·(l1 + l2)/2 com q3 = 20 kN/m, ≥ 70 kN** — o manual traduzido omite o "/2" (dobraria o valor; conferir EC2 9.10.2.3); tirantes internos distribuídos: 20 kN/m de largura. **Vertical** (BS 8110): cada pilar e parede portante amarrado da fundação à cobertura para a maior reação de cálculo (G + Q) de um pavimento.
- Periférico: dentro de 1,2 m da borda, contínuo nos cantos (traspasse com a armadura da peça ou junta concretada); em canto reentrante, ancorar para dentro dos dois lados. Pilares e paredes de fachada amarrados horizontalmente ao piso e à cobertura.
- **Tirante longitudinal da laje alveolar a meia altura** (nas juntas ou alvéolos abertos), nunca no topo (gera momento negativo de restrição) nem junto ao fundo: maximiza deformabilidade e evita que a laje caia em caso de dano. Ancoragem: **1,0–1,5 m na junta longitudinal; 0,6–0,8 m em alvéolo grauteado**.
- Projeto para dano localizado (paredes portantes): admitir a perda de um elemento e garantir caminho alternativo por (A) balanço da parede adjacente com viga-tirante no topo, (B) suspensão pela estrutura de cima (tirantes verticais contínuos), (C) efeito catenária/ponte das vigas-tirante, (D) impedir que lajes caiam em cascata (tirantes nos apoios).
- NBR 9062:2017 trata robustez/colapso progressivo (conferir item e valores; adotar os do EC2 como referência na ausência).

## 6. Ligações — princípios (cap. 4)
### 6.1 Critérios
Resistência (inclusive ações indiretas: retração, fluência, temperatura, desaprumo); **mudanças de volume** — ou libera o movimento (almofada, furo oval, nicho com betume) ou resiste à força de restrição (deformabilidade ajuda); movimentos de flecha (painel de fachada preso no meio do vão de viga → furo/deslizamento ou rótula); **ductilidade** — projeto "equilibrado": o fusível dúctil (barra ancorada) escoa antes de qualquer componente frágil (ancoragem, solda, cantoneira dimensionados para a **capacidade última** da barra); durabilidade (pintura epóxi, cobrimento com graute, **inox quando sem manutenção**, evitar corrosão galvânica com arruelas/luvas isolantes); **tolerâncias** (ajuste em x-y-z: trilho, calço, furo oval); fogo (mesmo grau de proteção dos elementos; partes embutidas ficam mais frias; almofada de elastômero não precisa de proteção se o colapso não depender dela).

### 6.2 Mecanismos de transferência
Encaixe (cálice; consolo metálico oculto colado com epóxi) · traspasse/laço de barras com barra transversal (laço + pino) · **ação de pino** (resistência ∝ Ø² e √fc; cai muito com afastamento → **evitar almofada alta**; fretagem em volta do pino) · aderência (só baixas tensões; limpeza, umidade e cura pesam tanto quanto a rugosidade) · **atrito-cisalhamento** (armadura atravessando a junta gera compressão quando a junta abre) · chave de cisalhamento (exige tirantes no topo/base da junta ou laços) · chumbadores/luvas/trilhos (furo maior para tolerância) · solda (chapa com **folga de 2 mm em volta** para dilatação na soldagem; qualidade depende da MO — Europa evita solda em campo) · pós-tensão.

### 6.3 Compressão
- Contato seco só com grande precisão ou tensão ≤ 0,3 fcd (EC2) — **a NBR 9062 é bem mais restritiva: junta a seco σ ≤ 0,042 fcd e ≤ 1 MPa (≤ 0,06 fcd e 1,5 MPa com rotação impedida); argamassa ≤ 5 MPa; elastômero ≤ 7 MPa simples / 11 MPa cintado** (valores da edição 2006 — conferir na 2017; detalhes na skill consultoria 4.3).
- Junta de argamassa 10–30 mm; de concreto 30–50 mm. **A junta não governa se rc = f_arg/f_elemento ≥ 0,5 e rth = espessura/largura ≤ 0,7** (DIN 1045); junta confinada por capa estrutural atende sempre.
- Almofadas 2–20 mm (mais espessas liberam rotação/deslocamento); acima de certas cargas, elastômero **fretado (cintado)**. Afastar das bordas (lascamento) e permitir giro sem contato da viga com a borda do apoio.
- Material da junta com E ≥ 70 % do concreto → tração por concentração; E muito menor → fendilhamento por expansão lateral → **armadura de fretagem** nos elementos adjacentes.

### 6.4 Comprimento de apoio (EC2 10.9.5.2)
a = a1 + a2 + a3 + √(Δa2² + Δa3²)
- a1 = FEd/(b1·fRd), fRd = 0,4 fcd (seco) ou 0,85 fcd (almofada/argamassa) (conferir);
- a2 = distância não efetiva na borda do apoio: 10–15 mm (lajes, apoio contínuo), 10–25 mm (vigas, concentrado);
- a3 = idem na extremidade da peça apoiada: 5–15 mm;
- Δa2 = vão/1200 (10–30 mm para apoio de aço/pré-moldado), Δa3 = L/2500 (conferir faixas EC2 tab. 10.4/10.5).

Valores indicativos (manual tab. 4.26 e 6.25) — **adotar o maior entre fórmula e tabela** (teste T1: alveolar 200 mm dá 38 mm pela fórmula vs. 60–70 mm na tabela):
| Peça | Apoio | a nominal |
|---|---|---|
| Alveolar h ≤ 250 | concreto/aço | 60–70 mm (alvenaria 100) |
| Alveolar h > 250 | concreto/aço | 100–130 mm (alvenaria 120) |
| Alveolar 120–400 (estágio inicial) | viga aço/concreto | 70–130 mm (alvenaria 100–150) |
| TT com cargas altas | viga | 75–150 mm (apoiar nas **almas**) |
| Pré-laje | concreto | 30 mm escorada / 50 mm sem escora (alvenaria ≥ 40/≥ 50; 70–100 no início) |
| Vigota | concreto/aço | 85–100 mm (alvenaria ≥ 100–125) |
| Laje nervurada ≤ 15 m | concreto | 150 mm |
| Viga secundária de cobertura ≤ 8 m | concreto | 140 mm |
| Viga de piso 12–20 m | concreto | 200–230 mm |
| Viga de cobertura ≤ 24 m / ≤ 40 m | concreto | 195 / 225 mm |
NBR 9062:2017 tem comprimentos mínimos e tolerâncias próprios — conferir e usar a norma em projeto.

### 6.5 Consolos (manual 4.6) — usar a ferramenta ND de consolos/dentes para o cálculo
- Geometria: **a0 ≤ d (ideal 0,4–0,6 d); h1 (face externa) ≥ a0 e ≥ 0,5 h; l < 0,7 h (usual 0,5 h), padronizar l = 300 ou 400 mm**.
- Bielas e tirantes com 1,0 ≤ tg θ ≤ 2,5 (EC2 6.5). Força horizontal na falta de cálculo: **Hd = 0,15 Nd** (manual); NBR 9062 dá Hd em função do tipo de apoio (≈ 0,8 Vd junta seca; 0,5 Vd argamassa; 0,16 Vd elastômero — conferir) + ações de montagem/ponte rolante.
- Detalhe: tirante ancorado **além da linha da carga** — solda em barra transversal ou laços horizontais em U no topo; consolos opostos ligados pelo tirante; consolo único com tirante ancorado na face oposta e traspassado com a armadura do pilar; barras **Ø < 25 mm** (tensão na dobra); consolos em várias faces → defasar o topo ≥ 50 mm ou inserto metálico; **região de distúrbio no pilar: 1,5 h acima do topo e 1,5 h·cos θ abaixo da base do consolo** (Elliott) → estribos adicionais.
- Produção: consolo em mais de uma face → **concretar em 2 etapas** com luvas rosqueadas no pilar + recesso de ~20 mm (ou retardador) na interface; consolo numa face só → face superior da fôrma.
- Em parede: balanço curto (flexão + cisalhamento); sem almofada distribuidora, concentrar o apoio em ~600 mm por elemento de piso.

### 6.6 Critérios de produção, transporte e montagem
Evitar congestionamento (detalhar em escala maior); **evitar furos na fôrma** (projeções na face superior); minimizar insertos (fundo/lateral = posição precisa; topo = difícil); itens padronizados de mais de um fornecedor; **repetir detalhes** (mesmo com pequeno sobre-dimensionamento); aceitar alternativas do fabricante; detalhes "à prova de erro"; esperas salientes atrapalham estoque/caminhão → luvas rosqueadas; ligação acessível para parafusar, soldar e inspecionar; **içar, posicionar e soltar o guindaste rápido** (sem mover a peça na horizontal nem içar inclinada); situações transitórias (apoios provisórios, içamento excêntrico, vento antes do diafragma).

### 6.7 Ligações típicas de esqueleto/pórtico
Pilar-fundação: **cálice** (liso → carga vertical pela base; dentado/rugoso → por cisalhamento; moldado in loco ou pré-moldado), **esperas em bainhas grauteadas** (radier/blocos sobre estacas; bainha com folga para o graute), **chapa de base parafusada** (cantoneiras soldadas à armadura do pilar, furos alargados, ganchos de ancoragem na fundação). Pilar-pilar: igual à pilar-radier. Viga-pilar: **chumbador ou parafuso em nicho vertical ~50 × 80 mm** na ponta da viga, grauteado (fixo) ou com betume/plástico + porca (deslizante); viga de borda pode ocupar só meio topo do pilar (ampliação futura); consolos metálicos ocultos (estética). Torção em viga de borda → barras aparafusadas/soldadas formando binário nos apoios. Juntas de dilatação: duplicar pilares/vigas ou apoio deslizante.

## 7. Elementos — pré-dimensionamento (catálogo europeu; conferir catálogo da fábrica)
**Galpão/traves planas** (tab. 5.7, m):
| | mín. | ótimo | máx. |
|---|---|---|---|
| Viga principal de cobertura | 12 | 18–32 | 45 |
| Viga secundária | 4 | 8–12 | 12 |
| Viga primária (longitudinal, apoia as principais) | 12 | 12–18 | 24 |
| Altura do pilar | 4 | 8 | 20 |
Espaçamento entre pórticos: 6 m (concreto celular), 6–9 m (alveolar), 9–12 m (nervurada); vigas secundárias 8–12 m. **Viga principal de cobertura apoiada direto no topo do pilar; viga primária nos consolos** (não empilhar mais de 2 peças). Duas águas com TT de mesa inclinada: 9–32 m. Mezanino: vão 6–18 m, modulação 7,20–9,60 m (alveolar/nervurada), ≤ 6 m (celular).

**Esqueleto** (tab. 5.11): viga 5 / 6–9,60 / 14 m (o original traz "1–9,60", leia-se ~6–9,60); laje 6 / 7–14 / 18–20 m; pilar 3–4 / 6–12 / 20–25 m. Pilar contínuo por 2–4 pavimentos; peça única até 20–24 m.

**Pilares**: seção mínima **300 mm** (manuseio, ligação, ~2 h de fogo); séries 300–800 mm; arestas chanfradas; manter prumada; consolos/insertos no mesmo nível nas faces sempre que possível.

**Vigas** (tab. 5.18 e texto):
| Tipo | b (mm) | h (mm) | alma (mm) | vão (m) |
|---|---|---|---|---|
| I de altura variável (i = 5–12 %) | 250–300 | 800–1400 | 80–120 | 10–25 |
| idem | 300–400 | 1200–2000 | 80–120 | 15–25 |
| idem | 300–500 | 1300–2500 | 80–120 | 25–40 |
| I reta (cobertura e piso pesado) | — | — | — | 10–35 |
| Retangular (com dente para esconder consolo) | 300–600 | 400–800 | — | 4–14 |
| Shed (Itália) | — | — | — | 15–28 |
| Terças (retangular/I) | — | 250–600 | — | 6–12 |
| L / T invertida de piso | 200–500 | 350–380 (o original; conferir — usual ≥ 500) | aba 100–150 × 150–200 | 4,8–14,4 |
Viga L com **mesma largura do pilar** (laje com ponta reta, sem recorte) é preferível; se mais estreita, recortar a laje em volta do pilar (até 1/3 da largura do painel pode ser removido; junta longitudinal deve coincidir com o pilar).

**Pisos** (tab. 6.1 — conferida na imagem):
| Tipo | vão máx (m) | h (mm) | largura (mm) | peso (kN/m²) |
|---|---|---|---|---|
| Alveolar armada | 9 | 100–300 | 300–1200 | 2,0–4,0 |
| Alveolar protendida | 20 | 120–550 | 1200 (texto do PDF diz 200 — erro de digitação) | 2,0–4,8 |
| Duplo T (TT) | 24 (30) | 200–800 | 2400 | 2,0–5,0 |
| π / U invertido | 9 | 150–300 | 600 | 1,5–3,5 |
| Maciça (celular/leve) | 6 | 100–250 | 300–600 | 0,7–3,0 |
| Pré-laje treliçada | 7 | 100–200 | 600–2400 | 2,4–4,8 |
| Vigota + bloco | 7 | 200–300 | 200–600 | 1,8–2,4 |
- Alveolar: 30–50 % de vazios, largura nominal 1200 (real 3–6 mm menor), até 20 m, pista 80–150 m, extrusão ou fôrma deslizante, bordas com chave para cisalhamento vertical. Vãos < 2 m protendidos podem precisar de armadura passiva.
- TT: 2400 (2390 real) ou 3000 mm; h 150–800; até 22 m (texto) / 24–30 (tabela); mesa fina 40–50 mm exige **capa armada** (diafragma e distribuição); ponta chanfrada a 1/3 da altura reduz a altura total.
- Pré-laje: 0,6–2,4 m × 40–120 mm; escoras a 1,5–3,5 m (conforme banzo superior da treliça); banzo superior serve de armadura negativa (laje contínua); treliça ignorada no ELS, pode entrar no ELU.
- Vigota: espaçamento 0,4–0,8 m; blocos inertes (EPS), semirresistentes (transmitem carga transversal) ou resistentes (colaboram na compressão).
- Escadas: lances + patamares (ou combinados), monobloco/helicoidais.

**Paredes** (tab. 7.1/7.6): estruturais 180–240 mm (laje armada em 2 direções) ou 150–200 (1 direção); não estruturais 80–150 (180); poços 180–200; comprimento 6–14 m, altura 3,0–4,5 m (transporte limita ~4,20). Modulação: B (vão da laje) 4 / 6–12 / 14 m em n × 3M ou 6M; C (largura) ≥ 2,40 / 3,60–6,00 / 12 m em n × 6M ou 12M; H 2,60–3,30 / máx 4,20–4,50. Junta vertical na intersecção com a parede perpendicular. Parede dupla (2 placas ≥ 40 mm, afastadas 70–100 mm, treliça a cada ~0,6 m, núcleo concretado in loco).

**Fachadas**: altura = pé-direito, largura n × 300 mm; **peso ≤ 10 t** (içamento usual na fábrica; conferir raio do guindaste no canto da obra); **uma das dimensões ≤ 3,60 m** (transporte); espessura h/10 a h/15 do elemento estrutural; sanduíche: externa 70–90 mm, interna 120–160 mm, isolamento 50–150 mm.

## 8. Pisos — projeto
- Peça isolada: flexão, cisalhamento (+ torção em cantos/aberturas), punção, flecha, fogo, acústica, manuseio. Curvas de catálogo (sobrecarga × vão × armadura) já consideram flexão, cisalhamento e às vezes flecha; trazem contraflecha.
- **Alveolar sem estribo**: cisalhamento depende da tração do concreto (NBR 14861 / EC2 6.2.2):
  - não fissurada na flexão (perto do apoio): VRd,c = (I·bw/S)·√(fctd² + αl·σcp·fctd), αl = lx/lpt2 ≤ 1 (protensão transferida até o ponto da fissura);
  - fissurada: VRd,c = [CRd,c·k·(100ρl·fck)^(1/3) + 0,15σcp]·bw·d, CRd,c = 0,18/γc, k = 1 + √(200/d) ≤ 2, ρl ≤ 0,02 (armadura ancorada além de d + lb,net), d ≈ 0,9h. (Manual escreve 0,12 = 0,18/1,5.)
  - Apoio em viga flexível (deformação da viga) cria tensões transversais que reduzem VRd → fib Bulletin 6. Cisalhamento é crítico em painel < 3 m e sob cargas concentradas/lineares.
- Punção (ensaio, carga em 100 × 100 mm; perímetro a 2h da área carregada, só almas): h 150/200 → 20 kN (Ø50) / 30 kN (Ø100); 270 → 40/60; 320/400 → 45 (Ø100)/65 (Ø200); 500 → 60/80. (Colunas Ø = tamanho do alvéolo, conferir na imagem do original antes de usar.)
- **Distribuição transversal de carga concentrada** (juntas grauteadas como rótulas, graute não retrátil, deslocamento lateral impedido por tirante transversal com resistência ≥ cisalhamento vertical total nas juntas): regra simples — **largura efetiva = 3 painéis ou ¼ do vão para cada lado** da área carregada; gráficos fib (só para momento, não para cisalhamento perto do apoio). TT de mesa fina precisa de capa armada ou barras soldadas na mesa.
- Vigotas (capa armada transversal, espaçamento ≤ 800 mm, carga no meio do vão) — fração da carga por vigota:
| vigotas de cada lado | carregada | 1ª | 2ª | 3ª | 4ª | 5ª |
|---|---|---|---|---|---|---|
| 2 | 0,26 | 0,22 | 0,15 | 0 | | |
| 3 | 0,24 | 0,19 | 0,13 | 0,06 | 0 | |
| 4 | 0,22 | 0,17 | 0,12 | 0,07 | 0,03 | 0 |
| ≥ 5 | 0,21 | 0,17 | 0,12 | 0,07 | 0,03 | 0,01 |
(carga entre 2 vigotas: dividir entre as duas e aplicar a tabela.)
- **Diafragma**: tensão média de cisalhamento nas juntas longitudinais de alveolar ≤ **0,1 MPa (ELU, cap. 3)** — raramente crítica; alveolar dispensa capa como diafragma se as peças forem impedidas de se afastar. O cap. 6 diz "≤ 1,5 MPa no ELS" para atrito sem armadura transversal — incoerente com o 0,1 MPa (provável 0,15); usar 0,1 MPa até conferir no fib Bulletin 6 / NBR 14861; TT sem capa → barras soldadas em chapas das mesas; com capa estrutural → capa leva o cisalhamento, pré-moldado leva a compressão e impede flambagem da capa; armadura da capa ancorada nas paredes de contraventamento; cuidado com aberturas junto às paredes.
- **Capa**: só quando precisa (ação composta, cargas concentradas altas, empilhadeira, sismo); **sempre com tela soldada**.
- Balanços: TT pode ter balanço; alveolar não (só com capa armada ancorada em alvéolos abertos e cordoalhas sup.; consultar o fabricante). Sacada com rompedor de ponte térmica.
- Alveolar entre paredes com carga alta: momento negativo não intencional → apoio em consolo, preenchimento parcial ou **ponta chanfrada** (fissura fica na zona de apoio e a laje volta a ser biapoiada) com almofada de 4 mm, ou armadura negativa na capa.
- **Aberturas em alveolar** (comprimento/largura, mm; HC 180–300 | HC 400): canto 600/400 | 600/300; frente 600/400 | 600/200; borda 1000/400 | 1000/300; quadrada central 1000/400 | 1000/200; furo redondo pequeno (< 300–400) na fábrica ou depois. Maiores: **apoio indireto com cantoneira/estribo metálico ("trimmer") ou viga in loco**; painéis vizinhos armados para a carga extra. Clima frio: furo de drenagem nos alvéolos.
- **Aberturas em TT** (l/b, mm; TT-2400 | TT-3000): centro 1000/630 | 1000/930; borda e canto 1000/320 | 1000/460. **Nunca furo vertical na alma**; furo horizontal redondo na alma só acima das cordoalhas.
- Ligações de apoio (concreto, aço, alvenaria): comprimento + tolerâncias, planicidade, rotação sem lascar, tirantes, grau de restrição. Sobre viga metálica: barras passando sobre/através da alma; proteger aço exposto ao fogo.

## 9. Paredes portantes (cap. 7)
- Verificar: seção mais carregada, flambagem, juntas horizontais; ações verticais, horizontais (vento + excentricidade + desaprumo) e acidentais.
- Ligações entre painéis **articuladas**; excentricidades: laje sobre a parede — sem almofada/argamassa a reação fica a **1/3 do comprimento de apoio**; com almofada/argamassa, no centro do apoio; laje com apoio engastado: G antes do concreto in loco com a excentricidade do apoio simples, Q depois no eixo da parede. Imperfeições de execução (CEB-FIB 78): **desaprumo ep = 2‰ a 3‰ da altura; desalinhamento em = 5 mm (painel de baixo visível) ou 10 mm (não visível)**.
- **Junta horizontal parede–laje alveolar** (VTT/Pajari): pontas retas NRd = 0,5·fcd·bj·Lj, bj = min(bw, b_argamassa); pontas chanfradas NRd = 0,6·fcd·bw·Lj (fcd = menor entre parede e graute). Válido com **Ø16 horizontal em cada borda junto à junta + estribos Ø8 c/ ≤ 200 mm**. Preencher em 2 etapas (entre lajes; depois sob o painel superior) ou graute fluido de uma vez com a base do painel abaixo do topo da laje. PCI Hollow Core Manual tem método mais detalhado.
- Paredes compostas T/L/U/I só se as juntas verticais transferirem o cisalhamento (chaves + tirante concentrado na junta horizontal; laços sobrepostos só se a rigidez fora do plano for insuficiente). Contraventamento composto (várias prumadas) vs. parede simples em balanço; tirante vertical na base se a carga vertical não estabilizar.
- Tirantes em parede: **P** periférico (diafragma), **L** longitudinal (equilíbrio das paredes, ancora a laje), **T** transversal (componente horizontal das juntas verticais, redistribuição), **V** vertical (balanço da parede e suspensão em dano local).
- Fogo: painéis portantes até 6 h; vergas e montantes com dimensões mínimas para desforma/manuseio (fig. 7.18 do original).

## 10. Fachadas (cap. 8)
- Portantes (sanduíche com camada interna estrutural; "spandrel" como viga) ou não portantes (fixadas em pilares/vigas, ou **autoportantes empilhadas sobre baldrame** com ligações só de travamento horizontal). "Pele dupla": painel interno estrutural + isolamento + pele externa independente (sem ponte térmica, cavidade ventilada; mais peças).
- Estabilidade: em geral só fechamento (ligações rotuladas fora do plano); portante com rigidez no plano pode contraventar (juntas verticais grauteadas ou soldadas).
- **Movimentos**: ΔT de projeto 60 °C (verão × inverno, montagem acima de 0 °C) e **40 °C entre camadas do sanduíche**; superfície escura chega a +60 °C → fixações com furo alargado, arruela sintética, espaçador; ligação entre camadas que deixa a externa dilatar.
- Sanduíche: conectores de apoio (peso + vento), de torção e espaçadores (isolamento até ~100 mm); com isolamento espesso (~150 mm) **estribos diagonais de inox** a cada 600–1200 mm + barras perimetrais.
- Fixadores: traspasse + concreto in loco (tolerância grande, barato, durável, resistente ao fogo, **sem estabilidade imediata → escorar**); parafusados (desmontáveis, imediatos, ajuste 3D, trilho + M12, chapa 100 × 8 × 100); soldados (comuns nos EUA). Fixadores não inspecionáveis: cobrimento ou metal anticorrosivo (inox AISI 316, bronze); **folga painel–estrutura ≥ 25–30 mm**; mesmo tipo de ancoragem em toda a fachada; esperas na face superior da fôrma.
- **Juntas de vedação**: face selada (polissulfeto/PU/silicone, aplicada a pistola com tira de apoio, levemente recuada) ou dreno aberto/2 estágios (chicana + câmara de expansão + selo de ar; dente horizontal 50–70 mm). Largura efetiva **8–30 mm**; selante elástico deforma ±25 %. Mínimo por largura do painel: 1,8 m → 12 mm; 2,4 → 12; 3,6 → 14; 4,8 → 15; 6,0 → 16 mm.
- Acabamentos: jato d'água/ácido (textura de pedra), retardador + lavagem (agregado exposto, brilhante), jateamento de areia (fosco), polimento (fosco/polido/brilhante); pigmentos inorgânicos (tons escuros variam mais); revestimento cerâmico ≤ 300 × 300 mm só por aderência, pedra natural com inserto inox e camada não aderente.
- Cantos: painel com canto integrado, peça de canto separada ou meia-esquadria (frágil, evitar); eixos modulares pelo lado interno da fachada.

## 11. Incêndio (cap. 9) — usar NBR 15200 + NBR 14432 no projeto
- Critérios **R** (portante), **E** (estanqueidade), **I** (isolamento: ΔT médio ≤ 140 K, pontual ≤ 180 K). Função só portante → R; só separação → E (+I); ambas → REI.
- Concreto falha raramente por perda de material; falha por **incompatibilidade de deformação térmica** (expansão restringida — fogo central em planta grande gera compressão enorme; vãos sucessivos acumulam ≥ 100 mm). Projeto global: **núcleo central + ligações rotuladas + pilares esbeltos** acompanham a dilatação; juntas de dilatação em espaçamento e largura adequados; checar expansão local com ΔT de 100–150 °C.
- Placa sob fogo inferior: ISO 1 h → ~600 °C embaixo, ~60 °C em cima; gradiente não linear → compressão nas faces e **tração no meio da alma** (crítico para alveolar sem estribo) e aumento de momento negativo nos apoios contínuos.
- Redução (Tabela 9.1, EC2 1-2): concreto silicoso fc,θ/fck = 1,00 (100 °C) · 0,95 (200) · 0,85 (300) · 0,75 (400) · 0,60 (500) · 0,45 (600) · 0,30 (700) · 0,15 (800); calcário 0,97/0,91/0,85/0,74/0,60/0,43/0,27; CA laminado a quente fsy,θ/fyk = 1,0 até 400 °C, 0,78 (500), 0,47 (600), 0,23 (700), 0,11 (800); trefilado 0,94 (400), 0,67, 0,40, 0,12; **cordoalha fpy,θ/(0,9fpk) = 0,99 (100), 0,87 (200), 0,72 (300), 0,46 (400), 0,22 (500), 0,10 (600)** → protensão perde resistência muito antes (por isso +10 mm de distância ao eixo para barras ativas e +15 mm para fios e cordoalhas).
- **Método da isoterma de 500 °C**: concreto > 500 °C desprezado, < 500 °C com fck integral; barras com a sua temperatura (podem ficar fora da seção reduzida e contar); γ = 1,0; ações da combinação frequente (ψ1 = 0,5 em residencial/comercial no EC0; na NBR 8681/15200 combinação excepcional com ψ2 — conferir). Não vale para pilar com 2ª ordem relevante. Largura mínima da viga: R60 90 · R90 120 · R120 160 · R180 200 · R240 280 mm.
- ηfi = (Gk + ψfi·Qk)/(γG·Gk + γQ·Qk); tabelas EC2 com ηfi = 0,7. Concreto calcário/leve: dimensões −10 %. Distância média am = Σ(Asi·ai)/ΣAsi.
- Vigas biapoiadas (3 faces; tab. 9.11, combinações bmin/a em mm; alma mín. bw):
| | col. 2 | col. 3 | col. 4 | col. 5 | bw |
|---|---|---|---|---|---|
| R60 | 120/40 | 160/35 | 200/30 | 300/25 | 100 |
| R90 | 150/55 | 200/45 | 300/40 | 400/35 | 110 |
| R120 | 200/65 | 240/60 | 300/55 | 500/50 | 130 |
| R180 | 240/80 | 300/70 | 400/65 | 600/60 | 150 |
| R240 | 280/90 | 350/80 | 500/75 | 700/70 | 170 |
Barra de canto com 1 camada: asd = a + 10 mm (dispensado se b ≥ coluna 4). Viga I: mesa inferior com deff ≥ d1 + 0,5d2; se b > 1,4bw e b·deff < 2bmin² → aeff = a(1,85 − (deff/bmin)·√(bw/b)) ≥ a (conferir fórmula no EC2 1-2 5.6.1). Aberturas na alma não afetam se a área tracionada restante ≥ 2bmin².
- Pilares contraventados (ω = 0,3, l = 3,0–3,5 m; bmin/a mm; µfi = 0,2 | 0,5 | 0,7; 1 face exposta µfi 0,7): R60 200/25 | 200/36 ou 300/31 | 250/46 ou 350/40 | 155/25 · R90 200/31 ou 300/25 | 300/45 ou 400/38 | 350/53 ou 450/40* | 155/25 · R120 250/40 ou 350/35 | 350/45* ou 450/40* | 350/57* ou 450/51* | 175/35 · R180 350/45* | 350/63* | 450/70* | 230/55 · R240 350/61* | 450/75* | — | 295/70 (* mín. 8 barras). Validade: λfi ≤ 30, e/b ≤ 0,025 (emax 100 mm), l0,fi = 0,5l (intermediários) e 0,5–0,7l (último); preferir mais barras finas (pilar C90 280 × 280 com 4Ø28 flambou as barras) e mais estribos acima de R90.
- Paredes não portantes EI: 60 → 80 · 90 → 100 · 120 → 120 · 180 → 150 · 240 → 175 mm; altura/espessura ≤ 40. Portantes (espessura/a; µfi 0,35 1 face | 2 faces | µfi 0,7 1 face | 2 faces): REI90 120/c | 140/c | 140/c | 170/c · REI120 150/25 | 160/25 | 160/35 | 220/35 · REI180 180/40 | 200/45 | 210/50 | 270/55 · REI240 230/55 | 250/55 | 270/60 | 350/60 (c = cobrimento normal). Painéis 140–300 mm atendem 60 min.
- **Lajes alveolares** (prEN 1168; h mín / a passiva / a ativa): R60 120/20/35 · R90 140/30/45 · R120 160/40/55 · R180 200/55/70 mm. Ensaios: 2–3 h com ligações usuais. Para o cisalhamento no fogo: **barras grauteadas em alvéolos/juntas a meia altura nos apoios (Ø12)**, tirantes periféricos, capa armada, proteger a mesa da viga metálica de apoio; considerar **comprimento de transmissão 1,5·lpt** (escorregamento da cordoalha de até 10 mm em painel sem ligação).
- **Exemplo do manual (alveolar 265 mm, R120) — refeito em Python (T13/T14)**: 10 cord. 3/8" a 40 mm (θ = 440 °C → kp ≈ 0,36) + 4 a 60 mm (300 °C → 0,72), fpk 1860 → x = 17 mm, MRd,fi = 117 kN·m (por painel de 1,2 m). O texto compara com MEd,fi = 117 kN·m calculado **por metro** com vão 12 m (e escreve 9² na conta). Coerente: por painel, vão 12 m → 140 kN·m > 117 → **não atende R120**; vão 9 m → 79 kN·m → atende. Lição: **compatibilizar largura (por m × por painel) e vão** antes de concluir.
- Ligações: apoio simples com chumbador é ótimo no fogo (rotação + binário de reserva); ligação laje-viga fica na zona fria; insertos metálicos expostos (parafusos, cantoneiras) com proteção; juntas de piso/parede atendem E/I pela espessura total + tirante perimetral; parede corta-fogo ligada ao pilar em toda a altura.

## 12. Do projeto ao orçamento — o que extrair do sistema (padrão ND)
1. **Concepção** (seções 2–3, 7): sistema por direção, modulação (M = 100 mm; 3M/12M; pisos 600/1200/2400; pórticos 6–12 m), lista de tipos de peça (minimizar), vãos × catálogo da fábrica.
2. **Estabilidade** (4): escolher balanço × núcleo, diafragma ou contraventamento de cobertura; modelo OpenSees; γz/2ª ordem; fases de montagem.
3. **Peças e ligações** (6–10): apoios (6.4), consolos (6.5 + ferramenta ND), cálice (skill consultoria 4.2), juntas de parede (9), tirantes (5), incêndio (11).
4. **Detalhe/pranchas**: plantas de montagem com marcas, lista de peças (peso, volume, quantidade), detalhes de ligação padronizados, prancha de produção por marca (skill vigas/pranchas).
5. **Quantitativo para orçamento** (`orcamentista-obras`): por marca — volume de concreto (m³), aço passivo (kg, resumo por bitola), cordoalha (kg; força por cabo), insertos/chapas/chumbadores (un, kg, galv./inox), alças de içamento; **peso por peça → guindaste no raio e frete** (painel ≤ 10 t e lado ≤ 3,60 m como regra; comprimentos > limite rodoviário = AET); serviços in loco: graute de juntas/cálices/nichos (m³), capa (m² × espessura + tela), almofadas (un), selantes (m), tirantes (kg), escoramento (pré-laje/vigota), montagem (h de guindaste + equipe por peça). Pesos próprios de piso da tab. 6.1 servem para estimativa preliminar.
6. **Checklist de consistência**: mesma seção/peso em memória, lista de peças e orçamento; tolerâncias e folgas compatíveis com os apoios; instalações embutidas definidas antes do projeto de produção.

## 13. Código validado — `premoldados_nd.py` (rodado em 07/10/2026, 18/18 PASS) e `estab_semirrigida_nd.py` (13.1, 14/14 PASS)
| Teste | Resultado | Referência / lição |
|---|---|---|
| T1 apoio alveolar 200 mm, 8 m, 60 kN | 38 mm (fórmula) | tab. 4.26: 60–70 mm → adotar o maior |
| T2 apoio viga 24 m, 400 kN, b1 250 mm | 128 mm (a1 = 66) | tab.: 195 mm |
| T3/T4 tirante periférico l = 5 / 12 m | 70 / 120 kN | 10 kN/m ≥ 70 kN |
| T5 tirante interno 9 + 9 m | 180 kN | EC2 com /2 (manual daria 360) |
| T6 As do tirante 180 kN CA-50 | 4,14 cm² | fyd = 435 MPa |
| T7/T8 θi (l = 3 m, m = 1) / (16 m, m = 4) | 1/200 / 1/379 | αh, αm |
| T9 Hi diafragma (Na 1000, Nb 1200, 1/200) | 5,5 kN | θi(Na+Nb)/2 |
| T10 junta parede–laje C30, bw 200, arg. 160 | 1714 / 2571 kN/m | 0,5·fcd·bj / 0,6·fcd·bw |
| T11 junta de argamassa | rc ≥ 0,5; rth ≤ 0,7 | DIN 1045 |
| T12 consolo a0 150, d 300, h 350, l 300 | l ≥ 0,7h → aumentar h ≥ 430 | Hd = 0,15·500 = 75 kN |
| T13 MRd,fi alveolar 265 R120 | 117,9 kN·m, x = 17 mm | manual 117,15 (kp arredondado) |
| T14 MEd,fi | 117 kN·m/m → 140 por painel | erro de unidade do exemplo |
| T15 ηfi (G 5, Q 3) | 0,578 | < 0,7 |
| T16 VRd,c fissurada (bw 200, d 175, 7 × 55 mm², C45, σcp 4) | 54,0 kN | conta à mão |
| T17 selante painel 6 m, ΔT 60 °C | 14,4 mm | tab. 8.20: 16 mm |
| T18 Σ fatores vigota (≥ 5 de cada lado) | 1,01 | consistência da tab. 6.21 |

```python
"""premoldados_nd.py — verificações de concepção/ligações de estruturas pré-moldadas
(base: manual fib/Van Acker trad. UFSCar, caps. 3, 4, 6, 7, 9; EC2 EN 1992-1-1/1-2 citado no manual).
Unidades: kN, m, kPa, salvo indicação (mm onde dito). (conferir) = checar contra NBR 9062:2017 / 6118:2023 / 15200 / 14861."""
import math

def comprimento_apoio(FEd, b1, fcd, a2, a3, vao, L_elem, seco=False, dA2_lim=(0.010, 0.030), dA3_lim=(0.005, 0.010)):
    """a = a1 + a2 + a3 + √(Δa2² + Δa3²); fRd = 0,4 fcd (seco) / 0,85 fcd (almofada). Δa2 = vão/1200, Δa3 = L/2500 (faixas: conferir EC2 tab 10.4/10.5)."""
    fRd = (0.4 if seco else 0.85) * fcd
    a1 = FEd / (b1 * fRd)
    d2 = min(max(vao / 1200, dA2_lim[0]), dA2_lim[1]); d3 = min(max(L_elem / 2500, dA3_lim[0]), dA3_lim[1])
    return dict(a1=a1, dA2=d2, dA3=d3, a=a1 + a2 + a3 + math.hypot(d2, d3))

def tirante_periferico(l, q1=10.0, Q2=70.0):          # EC2 9.10.2.2
    return max(l * q1, Q2)

def tirante_interno(l1, l2, q3=20.0, Q4=70.0):        # EC2 9.10.2.3(4) — com /2
    return max((l1 + l2) / 2 * q3, Q4)

def area_tirante(F, fyk=500e3, gs=1.15):              # cm²
    return F / (fyk / gs) * 1e4

def inclinacao(l, m, theta0=1 / 200):                 # EC2 5.2
    ah = min(max(2 / math.sqrt(l), 2 / 3), 1.0); am = math.sqrt(0.5 * (1 + 1 / m))
    return theta0 * ah * am

def forca_imperfeicao(theta_i, Na, Nb, diafragma=True):
    return theta_i * ((Nb + Na) if diafragma else (Nb - Na)) / 2

def forca_imperfeicao_simplificada(N_andar, L_painel):  # CEB-FIB MC78 (conferir)
    return max(0.01 * N_andar, 30.0 * L_painel)

def junta_parede_laje(fcd, bw, b_arg, Lj, ponta_chanfrada=False):  # VTT/Pajari; Ø16 nas bordas + estribos Ø8 c/200
    return 0.6 * fcd * bw * Lj if ponta_chanfrada else 0.5 * fcd * min(bw, b_arg) * Lj

def junta_argamassa_ok(f_arg, f_menor_elemento, t, b):              # DIN 1045
    return f_arg / f_menor_elemento >= 0.5 and t / b <= 0.7

def consolo_geometria(a0, d, h, h1, l, Nd):
    return dict(a0_ok=a0 <= d, a0_ideal=0.4 * d <= a0 <= 0.6 * d, h1_ok=h1 >= max(a0, 0.5 * h),
                l_ok=l < 0.7 * h, a_d=a0 / d, Hd=0.15 * Nd)

def vrd_alveolar_nao_fissurada(I, bw, S, fctd, sig_cp, alfa_l=1.0):  # kPa, m → kN
    return I * bw / S * math.sqrt(fctd ** 2 + alfa_l * sig_cp * fctd)

def vrd_alveolar_fissurada(bw, d, As, fck, sig_cp, gc=1.4):         # mm, mm², MPa → kN
    k = min(1 + math.sqrt(200 / d), 2.0); rho = min(As / (bw * d), 0.02)
    v = (0.18 / gc) * k * (100 * rho * fck) ** (1 / 3) + 0.15 * sig_cp
    vmin = 0.035 * k ** 1.5 * math.sqrt(fck) + 0.15 * sig_cp
    return max(v, vmin) * bw * d / 1000

_KP = [(20, 1.00), (100, 0.99), (200, 0.87), (300, 0.72), (400, 0.46), (500, 0.22), (600, 0.10),
       (700, 0.08), (800, 0.05), (900, 0.03), (1000, 0.0)]                       # fpy,θ/(0,9fpk)
_KS_LAMINADO = [(20, 1.0), (400, 1.0), (500, 0.78), (600, 0.47), (700, 0.23), (800, 0.11), (900, 0.06), (1000, 0.04)]
_KC_SILICOSO = [(20, 1.0), (100, 1.0), (200, 0.95), (300, 0.85), (400, 0.75), (500, 0.60), (600, 0.45),
                (700, 0.30), (800, 0.15), (900, 0.08), (1000, 0.04), (1100, 0.01), (1200, 0.0)]

def interp(tab, x):
    for (x0, y0), (x1, y1) in zip(tab, tab[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return tab[-1][1]

def mrd_incendio_protendido(camadas, fpk, h, b, fck):
    """camadas = [(Ap m², a m, θ °C)]; isoterma 500 °C, γ = 1; z = h − 0,4x − a."""
    forces = [(Ap * interp(_KP, th) * 0.9 * fpk, a) for Ap, a, th in camadas]
    T = sum(f for f, _ in forces); x = T / (0.8 * b * fck)
    return dict(T=T, x=x, M=sum(f * (h - 0.4 * x - a) for f, a in forces))

def eta_fi(Gk, Qk, psi_fi=0.5, gG=1.35, gQ=1.5):
    return (Gk + psi_fi * Qk) / (gG * Gk + gQ * Qk)

_VIGOTA = {2: [0.26, 0.22, 0.15, 0], 3: [0.24, 0.19, 0.13, 0.06, 0],
           4: [0.22, 0.17, 0.12, 0.07, 0.03, 0], 5: [0.21, 0.17, 0.12, 0.07, 0.03, 0.01, 0]}

def fatores_vigota(n_lado):
    return _VIGOTA[min(max(n_lado, 2), 5)]

def largura_junta_selante(L_painel, dT=60.0, alfa=1e-5, mov_adm=0.25, tol=0.0):  # mm
    return min(max(alfa * dT * L_painel * 1000 / mov_adm + tol, 8.0), 30.0)
```
(Os testes T1–T18 ficam no `__main__` do arquivo de trabalho; refazer após qualquer alteração.) Destino no software ND: módulo `prefabricados` (Parte D da skill principal) — funções de apoio, tirantes, imperfeição, juntas de parede, alveolar e incêndio.

### 13.1 `estab_semirrigida_nd.py` — pórtico com ligações semirrígidas (rodado em 07/10/2026, 14/14 PASS)
Pórtico plano (numpy, Euler-Bernoulli + Kg), molas rotacionais nas extremidades das vigas (gdl de rotação extra) e na base; 1ª ordem, γz pela NBR 6118 e P-Δ iterado. Referências lidas nos gráficos do artigo (slides 23–31).

| Teste | Resultado | Referência |
|---|---|---|
| T19/T20 ME/MR para αR 0,14 / 0,857 | 0,196 / 0,900 | 20 % / 90 % (slide 31) |
| T21 M base P1, 5 pav., αR → 0 | 597 kN·m | ΣH·h/4 = 602 (slide 27) |
| T22 5 pav., αR = 1: d1 / M base / γz | 0,023 m / 101 kN·m / 1,069 | 0,023 / ~100 / ~1,07 |
| T23/T24 5 pav. γz αR 0,40 / 0,14 | 1,185 / 1,461 | ~1,19 / ~1,47 (slide 31) |
| T25 3 pav. γz αR 0,14 | 1,135 | ~1,13 |
| T26 7 pav. γz αR 0,40 / 1,0 | 1,351 / 1,111 | ~1,35 / ~1,11 |
| T27 5 pav. αR 0,3: M base 1ª / P-Δ ÷ (γz·M1) | 227 kN·m / 1,00 | ~225 / γz ≈ NLG |
| T28 caso C (40×40, base 0,71), 20 % | γz 2,01 | ~2,03 (slide 30) |
| T29 Fonseca & Hanai 2009: ME/MR = 0,60 → αR; Rsec 3500, EI 3100 kN·m² | αR = 0,50 (zona III); L implícito 2,66 m | "semirrígida, resistência média"; vão coerente com pórtico 1:3 (seção 16.4) |

Casos A e B do slide 30 ficam 2–4 % abaixo do gráfico (hipótese da mola de base não documentada — conferir). 10 pav. não testado (cargas não legíveis).

```python
"""estab_semirrigida_nd.py — estabilidade global de pórtico plano pré-moldado com ligações viga-pilar
semirrígidas (mola rotacional Rsec ↔ αR) e base semirrígida opcional. 1ª ordem, γz e P-Δ (Kg iterado).
Base: Ferreira, Araújo, Jeremias Jr., Catoia, Kataoka (NETPRE/UFSCar). Unidades kN, m. N > 0 = compressão (interno)."""
import numpy as np

def alfaR(EI, L, Rsec):  return 1.0 / (1.0 + 3.0 * EI / (Rsec * L))          # fator de restrição
def Rsec_de_alfaR(EI, L, aR):
    return np.inf if aR >= 1 else (3.0 * EI / (L * (1.0 / aR - 1.0)) if aR > 0 else 0.0)
def ME_MR(aR):  return 3.0 * aR / (2.0 + aR)                                  # engastamento parcial (beam-line)
def classe_FE(aR):                                                            # Ferreira & Elliott (2002)
    m = ME_MR(aR)
    return ('I articulada' if m < .20 else 'II semirrígida baixa' if m < .50 else
            'III semirrígida média' if m < .75 else 'IV semirrígida alta' if m < .90 else 'V rígida')

def portico(nv, Lv, npav, h, EIp, EAp, EIv, EAv, H, qv, Pcol, aR=1.0, aR_base=1.0, P_todos=True, it=20):
    """H[j], qv[j]: força horizontal (no pilar da esquerda) e carga distribuída nas vigas do nível j+1;
    Pcol: cargas concentradas nos pilares (em todos os níveis se P_todos, senão só no topo)."""
    nc = nv + 1; nodes = [(i * Lv, j * h) for j in range(npav + 1) for i in range(nc)]
    nid = lambda i, j: j * nc + i; ndof = [3 * len(nodes)]; elems = []; springs = []
    def rot():  ndof[0] += 1; return ndof[0] - 1
    for j in range(npav):
        for i in range(nc):
            a, b = nid(i, j), nid(i, j + 1); da = [3 * a, 3 * a + 1, 3 * a + 2]
            if j == 0 and aR_base < 1:
                r = rot(); springs.append((3 * a + 2, r, Rsec_de_alfaR(EIp, h, aR_base))); da[2] = r
            elems.append((a, b, da + [3 * b, 3 * b + 1, 3 * b + 2], EAp, EIp, 'P', 0.0))
    for j in range(1, npav + 1):
        for i in range(nv):
            a, b = nid(i, j), nid(i + 1, j); da = [3 * a, 3 * a + 1, 3 * a + 2]; db = [3 * b, 3 * b + 1, 3 * b + 2]
            if aR < 1:
                k = Rsec_de_alfaR(EIv, Lv, aR); ra, rb = rot(), rot()
                springs += [(3 * a + 2, ra, k), (3 * b + 2, rb, k)]; da[2], db[2] = ra, rb
            elems.append((a, b, da + db, EAv, EIv, 'V', qv[j - 1]))
    n = ndof[0]; F = np.zeros(n); fixed = {d for i in range(nc) for d in (3 * i, 3 * i + 1, 3 * i + 2)}
    for j in range(1, npav + 1): F[3 * nid(0, j)] += H[j - 1]
    for jj in (range(1, npav + 1) if P_todos else [npav]):
        for i, P in enumerate(Pcol): F[3 * nid(i, jj) + 1] -= P
    for e in elems:                                                          # cargas nodais equivalentes da viga
        q, L, d = e[6], Lv, e[2]
        if q: F[d[1]] -= q * L / 2; F[d[4]] -= q * L / 2; F[d[2]] -= q * L * L / 12; F[d[5]] += q * L * L / 12
    def kloc(e, N):
        (x1, y1), (x2, y2) = nodes[e[0]], nodes[e[1]]; L = np.hypot(x2 - x1, y2 - y1); c, s = (x2 - x1) / L, (y2 - y1) / L
        EA, EI = e[3], e[4]; k = np.zeros((6, 6)); k[0, 0] = k[3, 3] = EA / L; k[0, 3] = k[3, 0] = -EA / L
        kb = EI / L**3 * np.array([[12, 6*L, -12, 6*L], [6*L, 4*L*L, -6*L, 2*L*L], [-12, -6*L, 12, -6*L], [6*L, 2*L*L, -6*L, 4*L*L]])
        kg = N / (30 * L) * np.array([[36, 3*L, -36, 3*L], [3*L, 4*L*L, -3*L, -L*L], [-36, -3*L, 36, -3*L], [3*L, -L*L, -3*L, 4*L*L]])
        ix = [1, 2, 4, 5]; k[np.ix_(ix, ix)] += kb - kg
        R = np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]]); T = np.zeros((6, 6)); T[:3, :3] = R; T[3:, 3:] = R
        return T, k, L
    def solve(Ns):
        K = np.zeros((n, n))
        for e, N in zip(elems, Ns):
            T, k, _ = kloc(e, N); K[np.ix_(e[2], e[2])] += T.T @ k @ T
        for a, b, k in springs:
            k = 1e12 if np.isinf(k) else k; K[a, a] += k; K[b, b] += k; K[a, b] -= k; K[b, a] -= k
        fr = [i for i in range(n) if i not in fixed]; u = np.zeros(n)
        u[fr] = np.linalg.solve(K[np.ix_(fr, fr)], F[fr]); out = []
        for e in elems:
            T, k, L = kloc(e, 0.0); f = k @ T @ u[e[2]]; q = e[6]
            f = f - np.array([0, q*L/2, q*L*L/12, 0, q*L/2, -q*L*L/12]); out.append(f)
        return u, out
    Ns = [0.0] * len(elems); u1, f1 = solve(Ns)
    M1 = sum(H[j] * (j + 1) * h for j in range(npav))
    dM = sum(sum(-F[3 * nid(i, j) + 1] for i in range(nc)) * u1[3 * nid(0, j)] for j in range(1, npav + 1))
    gz = 1.0 / (1.0 - dM / M1) if dM < M1 else np.inf
    for _ in range(it):                                                      # P-Δ (NLG simplificada)
        Ns = [f[0] if e[5] == 'P' else 0.0 for e, f in zip(elems, f1 if _ == 0 else f2)]
        u2, f2 = solve(Ns)
    top = 3 * nid(0, npav)
    return dict(d1=u1[top], d2=u2[top], gz=gz, M1=M1, dM=dM, Mb1=abs(f1[0][2]), Mb2=abs(f2[0][2]))

def ex_ferreira(npav=5, aR=1.0, bp=.5, hp=.5, red_p=.8, aR_base=1.0, Ec=35e6):
    """Exemplo do artigo: 3 vãos de 6,5 m, pé-direito 4 m, vigas 30×60 (0,4EI), pilares 50×50 (0,8EI), C30, Ec 35 GPa.
    Cargas de cálculo do slide (Fd = 1,3Fg + 1,4(0,7Fq + Fv)): H de baixo p/ cima 35, 42, 49…, topo 28 kN;
    q = 60 kN/m (pisos) e 30 kN/m (cobertura); 171/344/344/171 kN nos pilares em cada nível (conferido pelos gráficos)."""
    H = [35, 42] + [49] * (npav - 3) + [28] if npav > 3 else [35, 42, 28][:npav - 1] + [28]
    Iv = .3 * .6**3 / 12
    return portico(3, 6.5, npav, 4.0, red_p * Ec * bp * hp**3 / 12, Ec * bp * hp, .4 * Ec * Iv, Ec * .18,
                   H, [60] * (npav - 1) + [30], [171, 344, 344, 171], aR, aR_base)
```
(Testes T19–T28 no `__main__` do arquivo de trabalho.) Destino no software ND: módulo `prefabricados`/`porticos` (Parte D da skill principal); para modelos maiores, mesma mola em OpenSees (`zeroLength` com `uniaxialMaterial Elastic Rsec`, skill `mef-opensees-opsvis`).

## 14. Roteiro — projeto de estrutura pré-moldada
1. Programa + arquitetura → tipologia (seção 3) e direções dos vãos (galpão: viga no lado menor; escritório: laje perpendicular à fachada).
2. Malha modular e catálogo da fábrica (seção 7): peças, vãos, pesos, transporte/guindaste.
3. Sistema de estabilidade por direção + diafragma ou contraventamento (4); juntas de dilatação (≤ 60–80 m).
4. Cargas (NBR 6120, 6123, 8681), imperfeições (4.4), situações transitórias.
5. Modelo (OpenSees/software): pilares engastados/NLF, vigas articuladas ou αR (4.5: γz rígido < 1,10 sem ensaio; γz ≤ 1,30), diafragma; 2ª ordem; montagem.
6. Peças: pisos (8), vigas (`vigas-premoldadas-protendidas`), pilares e cálice (`consultoria-fabricas-pre-moldados`), paredes (9), fachadas (10).
7. Ligações (6): apoio, consolo/dente (ferramenta ND), chumbadores, juntas; ductilidade "equilibrada"; tolerâncias e ajuste 3D.
8. Integridade (5): rede de tirantes P/L/T/V com valores e ancoragens.
9. Incêndio (11): TRRF (NBR 14432) → tabelas/isoterma; ligações e juntas.
10. Pranchas (montagem + produção), lista de peças, quantitativos e orçamento (12).

**Modelo único de peças (desde 12/10/2026):** do passo 2 em diante, toda peça entra no modelo de peças do `nd_estruturas.prefabricados` (marca por identidade, armadura, insertos, CG, peso). O modelo analítico (passo 5) é gerado dele — eixo de cada peça, link rígido até o apoio, liberações por grau de liberdade (rótula, engaste ou grau de conexão 0–1 do consolo/chumbador, seção 4.5), grupos de carga e combinações NBR 8681 — e os esforços voltam gravados em cada peça. Pranchas, listas e orçamento (passo 10) saem do mesmo modelo — ver `pranchas-tecnicas-nd` 6B.

## 15. Armadilhas
- Adaptar projeto moldado in loco para pré-moldado (ligações caras, peças únicas).
- Galpão com cobertura leve tratado como diafragma rígido.
- Contar com pórtico semirrígido sem Rsec de ensaio/norma, ou com ligação zona I (αR < 0,14) — vira pilar em balanço; 5 pav. em balanço puro é instável (γz → ∞).
- Usar só o 0,95γz quando γz ≈ 1,2–1,3 em pórtico semirrígido (o artigo mostra que γz cheio aproxima melhor a NLG); aplicar γz em estrutura < 4 andares sem conferir com P-Δ.
- Esquecer a fase de montagem: antes do graute da capa a ligação viga-pilar é articulada (estabilidade só pelos pilares em balanço + escoramento).
- Dimensionar a viga só com o momento negativo da ligação semirrígida (precisa também do caso biapoiado: envoltória).
- Ligação de chumbador assumida rígida no ELS (é articulada; a semirrigidez é reserva) — ou o contrário, ignorar o binário em análise de colapso.
- Comprimento de apoio só pela tensão de contato (sem tolerâncias e distâncias não efetivas), ou só pela fórmula quando a tabela prática pede mais.
- Almofada alta sob chumbador (perde a ação de pino); almofada faceando a borda (lascamento).
- Consolo em várias faces no mesmo nível (congestionamento, fôrma especial) e tirante sem ancoragem além da carga.
- Tirante da laje alveolar no topo (momento de restrição) ou sem continuidade/ancoragem.
- Furo vertical na alma de TT; abertura em alveolar maior que a tabela sem apoio indireto.
- Alveolar curta (< 3 m) ou com carga concentrada sem verificar cisalhamento; alveolar apoiada em viga flexível sem fib Bulletin 6.
- Fachada presa no meio do vão de viga sem liberar a flecha; sanduíche sem folga para os 40 °C entre camadas.
- Exemplo/ábaco comparando grandeza por metro com resistência por painel (exemplo de incêndio do manual).
- Usar tabelas EC2 de fogo sem confirmar NBR 15200 e o TRRF da NBR 14432; esquecer +10/+15 mm de distância ao eixo na protensão.
- Painel acima de 10 t ou com as duas dimensões > 3,60 m sem estudo de içamento e transporte.
- Achar que encher mais alvéolos aumenta o cisalhamento na mesma proporção (Catoia 2009: 4 alvéolos ≈ 2 alvéolos; a nervura central sem preenchimento governa) — preencher alvéolos distribuídos e conferir a margem.
- Capa em alveolar "para resistir mais ao cortante" sem lembrar que a ruptura fica menos dúctil.
- Copiar curva M-φ de ligação de outra geometria (inclinação do chumbador, almofada, graute) — a rigidez muda muito (Miotto 2002 × Baldissera 2006).
- Dimensionar bloco com cálice embutido como bloco comum sem considerar que a biela nasce nas paredes do cálice (sem método consagrado; seção 16.6).

## 16. Pesquisa EESC-USP 2009 (ENDOSET) — o que serve para projeto, consultoria e aula
Fonte: *Cadernos de Eng. de Estruturas* v. 11, n. 53 (2009), artigos de pré-moldado do SET-EESC (orientadores El Debs, Hanai, Giongo, Pinheiro/Ferreira, Liborio). Página = página impressa da revista.

### 16.1 Cisalhamento em lajes alveolares — Catoia, Pinheiro & Ferreira (p. 7–11)
- Contexto Brasil: alveolares de **150–300 mm** (EUA/Europa 265–500) → mais cordoalha para o mesmo vão/carga, comportamento diferente das curvas estrangeiras.
- Extrudada não admite estribo; FIB (2000) dá a resistência no trecho **fissurado por flexão** para 3 casos (mesma forma da NBR 6118:2023 19.4.1 para laje sem armadura transversal):
  VRd1 = [τRd·k·(1,2 + 40ρ1) + 0,15σcp]·bw·d ≤ VRd2, τRd = 0,25 fctd, k = 1,6 − d ≥ 1 (d em m) (conferir k e ρ1 na NBR 14861).
  - com capa estrutural: usar d', bw' e ρ1' da seção composta;
  - com alvéolos preenchidos: bw' = bw + largura dos alvéolos cheios.
- Ensaio (FIP 1992 / EN 1168): carga a **2,5h do apoio**, peça ≥ max(4 m; 15h) — reproduzível em fábrica brasileira (bom serviço de consultoria/controle de qualidade). Peças: h = 200 mm, cordoalha Ø12,7 CP 190 RB, σpi = 1140 MPa, fc 35 MPa na liberação e 40 MPa aos 10 dias; capa 50 mm (33 MPa) com tela Ø5 c/200 ou 30 kg/m³ de fibra; 5 tipologias × 5 ensaios.

| Laje (h 200, vão 3 m) | Vu,exp (kN) | VRk | VRd1 | VS,máx = VRd1/1,4 | Vu/VRd1 |
|---|---|---|---|---|---|
| sem capa | 120,0 | 102,7 | 81,7 | 58,3 | 1,47 |
| capa + tela | 164,3 | 125,3 | 100,4 | 71,7 | 1,64 |
| capa + fibra | 201,0 | 125,3 | 100,4 | 71,7 | 2,00 |
| 2 alvéolos preenchidos | 170,2 | 157,3 | 120,8 | 86,3 | 1,41 |
| 4 alvéolos preenchidos | 179,8 | 211,7 | 159,8 | 114,2 | **1,12** |
(conferido: VS,máx = VRd1/1,4 e λ = Vu/VS,máx batem com a tabela do artigo.)
- **Lições**: (1) FIB/EN 1168 é coerente para sem capa, com capa e 2 alvéolos; (2) **4 alvéolos não rendem o dobro de 2** — a nervura central sem preenchimento vira o ponto fraco → a equação superestima (margem só 12 % sobre VRd1); preencher alvéolos de forma distribuída e não contar o ganho proporcional sem ensaio; (3) capa aumenta a resistência (ruptura migra para tração diagonal na nervura) mas **reduz a ductilidade**; (4) em h = 200 com carga a 2,5h a ruína perto do apoio é governada por fissura de flexão + **falha de ancoragem da cordoalha** (tração normal à armadura ativa) — conferir comprimento de transferência e ancoragem além da fissura; (5) sem capa apareceu ruptura combinada cisalhamento + torção (apoio irregular/carga excêntrica).

### 16.2 Consolos moldados em etapa anterior ao pilar — Menezes & El Debs (p. 13–16; base Costa 2009)
- Proposta produtiva: consolo pré-moldado antes, **só com o tirante** (sem estribos), em **CAD com fibras de aço** (fibra substitui a armadura de costura no controle do fendilhamento da biela); encaixado na fôrma do pilar com interface rugosa + esperas, pilar em concreto comum. Ganho: pilar com consolos em várias faces sem fôrma especial (resolve o problema da seção 6.5).
- Leonhardt: **estribo vertical não ajuda a transmitir a carga do consolo** (só enrijece a armação); estribos horizontais pouco espaçados aumentam a capacidade da biela para a/h ≈ 0,5–0,7.
- Ponto crítico: **interface consolo-pilar** (abertura de fissura) — testando adesivo epóxi e pasta de alta resistência. Pesquisa em andamento → em projeto, manter a armadura de costura da NBR 9062 e usar a ideia só com ensaio/protótipo da fábrica.

### 16.3 Chumbador grauteado em ligação viga-pilar semirrígida — Aguiar & El Debs (p. 17–20)
- Chumbador = componente que transmite cortante na interface por flexão (rótula plástica junto à interface); capacidade pelo modelo plástico de **Højlund-Rasmussen (1963, fib 2003)** — clássico: Vu ≈ c0·Ø²·√(fcc·fy), c0 ≈ 1,0–1,3 (conferir no fib Bulletin 43 antes de usar).
- Ensaio: 15 modelos 1:1, Ø16/20/25, inclinação 0°, 45° e 60°, 2 resistências de concreto, cargas horizontais simulando atrito; MEF (DIANA).
- Resultado: **chumbador inclinado → maior capacidade e menor deslocamento** que o reto; autor propôs expressão analítica com inclinação e fc. Motivação: grande diferença de rigidez entre Miotto (2002) e Baldissera (2006) para a mesma família de ligação → a rigidez depende muito do detalhe.

### 16.4 Rigidez de ligação e reforço — Almeida & Hanai (p. 57–61); Fonseca & Hanai (p. 63–67)
- Ligação típica de galpão (consolo + dente Gerber + chumbador + almofada + graute) **não é rótula perfeita** — confirma a seção 4.2.
- **Ensaio dinâmico** (vibração forçada na frequência natural + par de acelerômetros na ligação, método de Nóbrega 2004) deu rigidez da mesma ordem do ensaio estático: caminho para **verificar in loco** a rigidez real de ligações de estruturas existentes (laudo, monitoramento de dano), sem ensaio destrutivo.
- **Reforço com laminado de PRFC inserido em entalhe (NSM)** nas laterais da ligação (pórtico 1:3, pilar 15×15, viga 15×20, C57, almofada NR Shore 70A; laminado E = 131 GPa, ft = 2068 MPa, εu 17 ‰; resina Sikadur 330): ligação passou de articulada a **semirrígida — M ≈ 60 % do engaste perfeito, Rsec ≈ 3500 kN·m/rad**, flecha −50 % sob 55 kN. Momento na ligação obtido pela equivalência momento-curvatura da viga (Catoia 2007).
- Ruptura por **arrancamento do laminado com 5,3 ‰ (30 % de εu)** — distância à borda (3 cm Blaschko × 4 cm Kang) e comprimento colado curtos. Para projeto de reforço: borda ≥ 4 cm, comprimento de ancoragem suficiente, verificar descolamento.
- T29 (13.1): ME/MR = 0,60 → αR = 2m/(3 − m) = 0,50 (zona III Ferreira-El Debs-Elliott) e, com EI = 3100 kN·m², L implícito 2,66 m — coerente com o modelo reduzido. Uso: consultoria para galpão com flecha/deslocamento excessivo → reforçar ligação em vez de trocar viga/pilar.

### 16.5 Ligação monolítica equivalente com concreto com fibras — Oliveira Jr., El Debs & Araújo (p. 33–37)
- Traspasse de armadura + **concreto com fibras de aço** (Vf 1–2 %) no nó para comportamento ~monolítico (estático, cíclico, dinâmico). Ensaios de cisalhamento direto em interface com chaves: 187 kN (σn = 0,1 MPa) × 218 kN (σn = 0,5 MPa) — a **compressão normal à interface** ativa as chaves.
- Expectativa: traspasse < 30Ø com fibras (testados 5Ø a 30Ø com Ø12,5) — **não adotar sem os resultados finais**; NBR 6118 continua valendo.
- Modelagem da casa de força da UHE Foz do Chapecó (montagem): ligação com consolo e dente metálicos segura; **procedimento PCI 2004 para insertos metálicos conservador**; necessária armadura envolvendo o dente metálico (fissuração excessiva sem ela).

### 16.6 Cálice em bloco sobre 2 estacas — Barros & Giongo (p. 39–43)
- Três tipos: **externo** (colarinho saliente), **parcialmente embutido**, **embutido** (sem colarinho). Só o externo tem método de projeto consagrado (Melo 2004, NBR 9062); embutido/parcial ainda sem recomendação (pesquisa propõe biela-tirante refinado).
- Referências úteis: Blévot & Frémy 1967 (base do método das bielas; skill `interacao-solo-estrutura`/bloco B39 usa); Schlaich 1987: tensão nodal segura ≤ 0,6 fck; Rausch 1997: a estaca restringe o tirante e absorve parte da componente horizontal da biela; Miguel 2000 (3 estacas): Blévot conservador, ruína por fendilhamento da biela + escoamento; Delalibera 2006: biela diferente dos modelos, tensão nas estacas uniforme; Campos & Marcellino 2008: modelo de Melo (2004) **conservador** para cálice externo em bloco de 2 estacas; Barros 2009: viga de travamento perpendicular às estacas não altera o comportamento do bloco com cálice embutido (paredes do cálice levam a força às estacas).
- Uso ND (ex.: UCP Pitanga, cálice embutido em bloco): dimensionar paredes do cálice pela NBR 9062 (Melo/El Debs) e o bloco por bielas a partir da base do cálice, conferindo a biela nas paredes; documentar que é extrapolação conservadora.

### 16.7 Pilar misto preenchido com viga pré-moldada — Bezerra & El Debs (p. 27–31)
- Pilar de tubo de aço preenchido no lugar do pilar pré-moldado: seção menor, tubo = fôrma, sem armadura, mais ductilidade (bom com CAD), emenda pilar-pilar concretada.
- Consolo metálico com **chapas laterais alinhadas às paredes laterais do tubo** (a face frontal do tubo é flexível) + chapa horizontal + enrijecedores; conectores pino com cabeça/cantoneira internos para mobilizar o núcleo. Ensaio: enrijecedor interno cedeu a 270 kN, externo 650 kN, chapa lateral 900–1010 kN — colapso avisado, desejável. Momento negativo por armadura passante; positivo por parafuso passante (pouco eficiente — ainda incerto).

### 16.8 Pré-moldados esbeltos em CAD — Conceição & Liborio (p. 51–55)
- Receita de CAD/CAA para peças leves de acabamento aparente: **CP V ARI RS + ≥ 10 % de sílica ativa em volume**, superplastificante escolhido por miniabatimento (Kantro) — a/agl 0,35, sem perda de fluidez em 40 min; graúdo basáltico 9,5/6,3 mm; areias por empacotamento (63/27/10 % de 2,4/1,2/0,5 mm → massa unitária 1,79 kg/dm³); cura a vapor à pressão atmosférica. Argumento de consultoria: desforma rápida, durabilidade > 100 anos, mercado habitacional.

### 16.9 Também no volume (fora do escopo pré-moldado)
Sudano & Hanai (p. 1–5): efetividade do cobrimento em pilares encamisados com CAR (reforço de pilar); Kataoka & El Debs (p. 87–92): ligação viga metálica–pilar preenchido com laje steel deck, cíclica; madeira, aço em incêndio, MEC/MEF.