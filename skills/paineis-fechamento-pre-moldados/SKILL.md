---
name: "paineis-fechamento-pre-moldados"
description: "Use ao conceber, calcular, detalhar, especificar fixações, orçar ou ensinar painéis pré-moldados de fechamento lateral/fachada (maciços, alveolares, arquitetônicos, sanduíche) e suas ligações com a estrutura."
---

# Painéis pré-moldados de fechamento — concepção, cálculo, ligações e detalhamento

Skill de **elemento + ligação** para o fechamento lateral (galpões, indústrias, fachadas). O sistema global fica em `projeto-estruturas-pre-moldadas` (seção 10 = fachadas pelo manual fib; seção 4.6 = ligações deformáveis). Irmãs: `consultoria-fabricas-pre-moldados` (NBR 9062, tolerâncias, fases transitórias, produção), `ancoragem-barras-pos-instaladas` (insertos/chumbadores pós-instalados), `estruturas-metalicas-nd` (cantoneiras, solda), `orcamentista-obras`, `pranchas-tecnicas-nd`. Responder em português técnico; (conferir) = checar na norma vigente antes de usar em projeto.

## 1. Fontes e nível
- **Castilho, V. C.; El Debs, M. K.; Gil, L. S. (2001)** — *Contribuição dos painéis pré-moldados de fechamento no enrijecimento da estrutura principal: estudo de caso*. Cadernos de Engenharia de Estruturas EESC-USP n. 17, p. 59-73 (caso real da Reago). Lido na íntegra em 07/10/2026 (pdf.js, aba do navegador). Único artigo do caderno sobre painéis — **o material é um estudo de caso de interação painel–estrutura, não um roteiro de projeto de painel**.
- **Ferreira, M. A.; El Debs, M. K. (2001)** — mesma revista, p. 75-104: resistência e deformabilidade de ligação com almofada + chumbador (Engström 1992; Dei Poli et al. 1992) → base para **pinos/chumbadores de fixação** (seção 6).
- O restante desta skill (tipos, esquema isostático, içamento, detalhamento, fixações) é **conhecimento próprio ND** apoiado em PCI Design Handbook (cap. de painéis arquitetônicos e manuseio), PCI *Architectural Precast Concrete*, fib/Van Acker (já na skill de sistemas), NBR 9062:2017, **NBR 16475:2017 (painéis de parede de concreto pré-moldado — conferir requisitos, espessuras e tolerâncias no texto)**, NBR 6118:2023, NBR 6123 (vento), NBR 8681. Tudo que não veio do caderno está marcado ou é prática corrente.

## 2. O que o estudo de caso ensina (Castilho et al.)
- Estrutura: pilares 600 × 600 engastados, vigas 200 × 400 articuladas por pino; painéis **horizontais** de concreto arquitetônico 2,50 m de altura × 180 mm (30 mm de camada de acabamento), **empilhados com tiras de elastômero**; peso vai do painel de cima para o de baixo e deste ao **consolo do pilar** ou ao bloco; ações horizontais vão **direto ao pilar** por insertos metálicos com pino Ø12,5 mm. A flexibilidade do pino acomoda temperatura, retração e fluência.
- Ações: vento 0,8 kN/m²; variação volumétrica do painel **ε = −25 × 10⁻⁵** (temperatura + retração + fluência). Modelo 3D LUSAS: pilares/vigas = barra, painéis = casca excêntrica (200 mm), ligação = barra de aço ("pino") de comprimento = excentricidade; elástico-linear; Ec 31,3 GPa.
- Resultados (topo, vento): pórtico sem painéis 11,24 mm; com painéis e pino 200 mm 11,03 mm → **fechamento com ligação flexível não enrijece** (como projetado). Forças na ligação ≤ 1 kN; **resistência característica da ligação em ensaio = 23 kN**.
- Variando o comprimento do pino (rigidez da ligação):

| Pino | Topo (mm) | Ligação, vento (kN) | Tensão princ. painel (kPa) | Ligação, vento + Δvol (kN) | Tensão (kPa) |
|---|---|---|---|---|---|
| 200 mm | 11,03 | 0,98 | 6,6 | 0,43 | 13,9 |
| 50 mm | 7,31 | 2,30 | 60 | 6,80 | 225 |
| 10 mm | 2,21 | 5,20 | 214 | **45,6 > 23** | 1391 |

- Com pino 50 mm dá para reduzir os pilares de **600 → 500 mm** com o mesmo deslocamento (11,15 mm): −31 % de concreto, ≈ −20 % no custo dos pilares, peso da peça −31 %; ρ do pilar quase igual (0,256 % × 0,278 %). Ligação: 6,80 × 1,4 = 9,5 kN < 23 kN → ok; tensões no painel 0,22–0,25 MPa → sem armadura adicional.
- **Lições**: (1) a rigidez da ligação decide se o painel é só vedação ou participa do contraventamento; (2) ligação rígida atrai a força da **variação volumétrica** — o esforço crítico é a ligação, não o painel (10 mm: 851 kN no caso pilar 600 + pino 10 → inviável); (3) usar o painel como enrijecedor é estratégia de projeto válida só com ligação **dimensionada para vento + Δvol + ciclos**, comportamento conhecido (ensaio) e durabilidade garantida — senão projetar como fechamento isostático e flexível.
- **Ressalvas do material**: o texto dá Iv = 0,0432 m⁴ e Ip = 0,00521 m⁴, incoerentes com 200 × 400 (0,00107) e 600 × 600 (0,0108; 0,00521 é de 500 × 500) — trocados/erros de digitação; os comprimentos dos painéis da Fig. 1 não são legíveis no texto → o modelo **não é reproduzível** com os dados publicados. Interpretação ND: o "pino" do modelo é uma barra bi-engastada Ø12,5 → k = 12EI/L³: 200 mm ≈ 0,38 kN/mm; 50 mm ≈ 24 kN/mm (64×); 10 mm ≈ 3000 kN/mm (aí a deformabilidade local do concreto, seção 6, governa — conferir).

## 3. Tipos usuais no Brasil e quando usar
| Tipo | Geometria típica | Uso / observações |
|---|---|---|
| **Alveolar protendido de fechamento** (horizontal) | h 150–200 mm (até 265), largura 1,20–1,25 m, vão entre pilares até ~10–12 m (catálogo) | galpões; macho-fêmea nas juntas horizontais; mais leve; furos/recortes limitados (alvéolos) |
| **Maciço armado/protendido** (horizontal ou vertical) | 100–200 mm; 2,0–3,0 m × 6–12 m | galpões, platibandas, muros; vertical entre baldrame e viga-calha |
| **Arquitetônico** | 120–200 mm + acabamento (agregado exposto, textura, cor) | fachadas; exige ELS sem fissura, juntas e fixação inoxidável/galvanizada |
| **Sanduíche** (2 placas + EPS/PIR + conectores) | externa 60–90, isolante 50–150, interna 80–160 mm | conforto térmico, câmaras frias, indústria alimentícia; dilatação diferencial (40 °C entre camadas) |
| **Nervurado / TT vertical** | TT de 2,4–3,0 m de largura | fechamentos altos (> 12 m) e grandes vãos entre pilares |
| **Painel de concreto celular / GRC** | leves | só vedação; fora do escopo de cálculo estrutural pesado |

Regras de concepção: altura do painel e vão entre pilares da modulação do galpão; **peso ≤ capacidade do guindaste no raio** (usual ≤ 10 t) e uma dimensão ≤ 3,60 m (transporte); juntas alinhadas com pilares; peças repetidas (poucos tipos); primeiro painel sobre baldrame/consolo do pilar; portões e janelas na modulação (vergas = painel/viga).

## 4. Sistema estático (o ponto mais importante)
1. **Isostático**: cada painel com **2 apoios de gravidade** (no mesmo nível, normalmente na base ou no terço inferior) + **2 (ou 4) tie-backs** que só seguram forças fora do plano. Mais de 2 apoios de gravidade na mesma linha = hiperestático: recalque/flecha da estrutura carrega um só apoio.
2. **Liberar movimentos no plano**: um apoio de gravidade fixo na horizontal, o outro deslizante (furo oblongo + arruela de PTFE/teflon ou almofada); tie-backs com folga vertical e horizontal (furo oblongo, haste flexível, trilho). Δ = α·ΔT·L (+ retração/fluência ≈ ε 25 × 10⁻⁵ do caso) — painel de 7,5 m com ΔT 30 °C → 2,25 mm; folga de projeto ≥ 3× o movimento + tolerância de montagem.
3. **Apoio no pilar, não no meio do vão da viga** (flecha/fluência da viga carrega o painel); se inevitável, ligação que acompanhe a flecha (furo vertical).
4. **Painel empilhado** (como no caso): só o painel de base apoia nos consolos; os de cima transmitem peso pela junta horizontal (elastômero/argamassa) → consolo dimensionado para n·W/2 e painel de base verificado como **viga-parede** com a carga acumulada; tie-backs de cada painel nos pilares.
5. **Excentricidade** do CG em relação ao apoio de gravidade gera binário H = W·e/z entre apoio e tie-back (soma ao vento); em viga de borda que recebe o apoio → **torção na viga**.
6. Decidir explicitamente: (a) fechamento puro (ligação flexível, não conta no contraventamento — padrão ND) ou (b) painel enrijecedor (ligação rígida calculada, pilar reduzido, seção 2). Registrar a hipótese na memória e nas pranchas.

## 5. Ações e verificações do painel
**Definitivas**: peso próprio (25 kN/m³ + acabamento), **vento NBR 6123** (q = 0,613·Vk², Vk = V0·S1·S2·S3; coeficientes de pressão externa nas zonas de canto/borda + pressão interna — galpão com portões abertos: cpi desfavorável até +0,8/−0,5, conferir), variação volumétrica (ΔT 30–60 °C conforme cor/exposição; gradiente na espessura 10–20 °C → arqueamento δ = α·ΔT·L²/(8t)), impacto de veículo/empilhadeira junto à base (proteção ou baldrame alto), cargas de fixação (calhas, instalações). **Transitórias**: desforma (sucção da fôrma 1,2–1,4 × peso conforme acabamento — PCI, conferir), içamento/basculamento (coef. dinâmico 1,3 — NBR 9062, conferir), estocagem (apoios a ~0,2 L), transporte, montagem (vento sem os tie-backs; escoramento).

Verificações:
- **Flexão fora do plano** (vento): painel horizontal como laje armada numa direção entre pilares, Md = γ·p·L²/8 por metro de altura; armadura mínima de laje (NBR 6118 tab. 17.3) em **duas faces** (sucção e sobrepressão); flecha L/250 e compatível com a junta/vedação (conferir limite em NBR 16475).
- **Flexão no plano** (peso): painel = viga-parede entre os apoios; armadura de borda inferior (z ≈ 0,8 min(H, L)) + **reforço de borda perimetral** (usual 2Ø8–2Ø10).
- **Fissuração** (arquitetônico, manuseio): σ ≤ fctk,inf(j)/1,5 na idade da operação (sem fissura visível); peças estruturais comuns podem aceitar ELS-W.
- **Cisalhamento/punção local** nos insertos e nas alças; esmagamento no apoio (elastômero/argamassa — consultoria 4.3).
- **Instabilidade** de painel vertical alto apoiado na base (esbeltez fora do plano e 2ª ordem se portante).
- **Incêndio**: fechamento corta-fogo → EI pela espessura (skill de sistemas, 11: EI 60 → 80 mm, 90 → 100, 120 → 120 mm); ligações metálicas protegidas se o colapso do painel ameaçar rotas de fuga (conferir IT do Corpo de Bombeiros).
- **Durabilidade**: cobrimento pela classe de agressividade (fachada externa ≥ CAA II; indústria/litoral III–IV); NBR 9062 permite reduzir 5 mm com controle de fábrica (conferir).

## 6. Ligações e sistemas de fixação
### 6.1 Catálogo de soluções
| Fixação | Função | Movimentos | Prós / contras |
|---|---|---|---|
| **Consolo de concreto do pilar** (com elastômero) | gravidade | rotação; deslizamento pelo elastômero | barato; definir na fábrica do pilar; dimensionar para n·W/2 (empilhado) |
| **Consolo/cantoneira metálica** em inserto do pilar | gravidade | furo oblongo horizontal | ajustável; exige proteção anticorrosiva e ao fogo |
| **Apoio no baldrame** (argamassa/elastômero + pino de posicionamento) | gravidade (painel vertical) | — | simples; nivelamento do baldrame é crítico |
| **Encaixe em ranhura do pilar** (pilar com aba/rebaixo, painel desliza) | vento (e posicionamento) | livre no plano | sem metal, rápido; verificar aba do pilar à flexão/cisalhamento, lascamento das bordas, folga para tolerância, vedação com mastique |
| **Trilho embutido** (perfil C ancorado, tipo Halfen/Jordahl) + parafuso T + cantoneira | tie-back / gravidade leve | ajuste ao longo do trilho + oblongo | ajuste 3D, desmontável; capacidade do catálogo do fabricante do trilho; ancoragem do trilho em zona sem fissura |
| **Bucha/inserto rosqueado + barra roscada + cantoneira com furo oblongo e arruela PTFE** | tie-back | deslizante no plano | padrão para painel arquitetônico; torque controlado para não travar o deslizamento |
| **Chapa de inserto + cantoneira soldada** | ponto fixo | nenhum | rígido: atrai Δvol (seção 2) → só **um** ponto fixo por painel; solda em campo = controle de qualidade e corrosão |
| **Pino/chumbador grauteado** (Castilho: Ø12,5 em inserto) | tie-back | flexibilidade do pino | resistência pela ação de pino (6.2); ensaio de referência 23 kN (característico) |
| **Haste/tirante** fino (Ø12–16 roscado) | tie-back de painel alto | flexível no plano, rígido axial | permite ajuste de prumo; checar flambagem se comprimida |

### 6.2 Cálculo de pino/chumbador em concreto (Engström 1992; Ferreira & El Debs 2001 — validado, T29–T55)
- **Escoamento (2 rótulas plásticas na barra)**: Fvy = n·Cr·Ce·C1·φ²·√(fcc·fsy); C1 ≈ 1,19–1,29 (tab. por fc; 1,24 nos ensaios); **Ce = √[1 + (C1·ε)²] − C1·ε**, ε = (3e/φ)·√(fcc/fsy), **e = metade da altura livre** (almofada/folga); Cr = 1 a 1,42 (restrição à rotação relativa). Fvy,min com o concreto mais fraco (graute), Fvy com o mais forte.
- **Resistência total (barra ancorada nas duas pontas, efeito de tirante + atrito)**: Fv,tot = n·[C1·φ²·√(fcc·fsy,red) + μ·σsm·As], fsy,red = fsy − σsm (recomendado fsy,red ≈ 0,7 fsy); μ: concreto–concreto 0,6; aço–concreto 0,4; concreto–neoprene 0,3–0,4 (o artigo usou 0,5 e 0,4 nos protótipos 3/4). Sem ancoragem superior não contar o atrito.
- **Deformabilidade (mm/kN)**: λ = [G·Ao/hn + n/(hn³/(12EsIb) + 1/(3,5EsIbα1³) + 1/(3,5EsIbα2³))]⁻¹, α = [kc·φ/(4EsIb)]^¼, **kc = 127·√fc/φ^(2/3)** (MPa/mm, φ e fc em mm/MPa). Vale para almofada com fator de forma B < 5 (protótipo com B = 6,8 errou 2,5×).
- **Deslocamento no escoamento**: α_crit = 1,75·fsy,red/(Es·φ[m]) (empírica), x = φ/(3C1)·√(fsy,red/fc), ℓp = x1 + x2 + hn, a_vy = α_crit·ℓp (≈ 2,7 mm nos protótipos) → diagrama trilinear F × δ.
- Ensaios (aço 1020, fyk 250, graute 30 MPa): 1Ø16/almofada 150 × 300 × 10 → Fvu 34 kN; 2Ø16 → 60; 2Ø25/250 × 300 × 10 → 170; 2Ø25/200 × 300 × 15 → 156 kN. Teoria/ensaio: Fvy,min 1,00 (CV 16 %), Fvy 0,99 (7,5 %), Fvu 0,96 (8 %); λ calculado 1,23× o real.
- **Recomendações de detalhe**: almofada com B < 5 e a/hn < 20; **φ/hn > 1 (> 1,5 para rigidez)**; quanto maior a folga/almofada, maior a flexão local do pino (Ce cai); força normal até 30 kN não mudou a rigidez inicial; giro relativo dos elementos aumenta a flexão no pino (escoou com 15 kN em vez de 60 kN).
- Para fixação de painel: e = folga painel–pilar/2 (+ espessura de calço); usar Fvy,min/γ (γ ≥ 1,5–2,0 sobre a resistência de ensaio/característica, conferir NBR 9062 para ligações) e checar também a **ancoragem do inserto** (cone de arrancamento, borda — skill `ancoragem-barras-pos-instaladas`, EN 1992-4/ACI 318 cap. 17) e a solda/cantoneira (capacidade ≥ a do fusível dúctil: "projeto equilibrado").

### 6.3 Regras de projeto das ligações
- Forças: gravidade W/2 por apoio (+ binário de excentricidade); vento por área tributária (sobrepressão **e** sucção); Δvol só se a ligação restringir; montagem (painel apoiado só embaixo, escorado). Majorar 1,4 (NBR 8681) e usar coeficiente adicional de ligação/fixação se a norma pedir (NBR 9062, conferir; PCI usa fator extra para conexões).
- Folga painel–estrutura ≥ 25–30 mm (fib); calços de nivelamento metálicos/plásticos (não madeira); ajuste nas 3 direções.
- Um único tipo de fixação por fachada; insertos padronizados de fornecedor com catálogo; nada de solda em campo em painel arquitetônico se houver alternativa.
- Aço exposto: galvanização a fogo (≥ 85 µm) ou inox AISI 304/316 (agressivo/sem manutenção); separar metais diferentes (arruela isolante).
- Inspeção: ligação acessível depois de montada (ou definitiva sem manutenção).

## 7. Detalhamento (prancha do painel — o que não pode faltar)
1. **Fôrma**: dimensões, espessura, chanfros 15–20 mm, macho-fêmea/encaixes, pingadeira, face acabada (lado fôrma ou desempenada), recortes e aberturas cotados.
2. **Insertos**: posição cotada da face de referência, tipo/fabricante/capacidade, armadura de ancoragem (grampos/"hairpins" atrás do inserto), distância a bordas (≥ 1,5 hef sempre que possível); alças de **içamento**, de **basculamento** e de **desforma** separadas quando as direções diferem.
3. **Armadura**: telas nas duas faces (ou uma central só em painel fino de vedação, conferir), **barras de borda perimetrais**, reforço de aberturas (barras paralelas ≥ área cortada + **diagonais 2Ø10 nos cantos** contra fissura de canto), reforço junto a alças e insertos, cobrimento e espaçadores; protensão (alveolar/maciço protendido): cordoalhas, transferência, comprimento de ancoragem em recortes.
4. **Dados**: marca, peso (kN e t), volume, fck e **fcj de desforma/içamento**, CAA e cobrimento, posição de estocagem e de transporte, sequência de montagem.
5. **Detalhe de ligação** em escala 1:5/1:10 com folgas, furos oblongos (comprimento = 2× movimento + tolerância), arruelas, torque, solda, proteção anticorrosiva.
6. **Juntas**: largura de projeto (8–30 mm; selante deforma ±25 % → largura ≥ movimento/0,25 + tolerância; skill de sistemas 10 tem a tabela fib), tarucel/tira de apoio, selante PU/silicone neutro, drenagem/chicana em junta horizontal (dente 50–70 mm).

## 8. Manuseio, estocagem e montagem
- Içamento com 2 alças (pontos a 0,207 L das pontas): M+ = M− = 0,0214·w·L² (w por metro). 4 pontos com balancim equalizador ≈ 1/4 desse momento (0,0054 wL² — PCI, conferir). Desforma deitada × basculamento (mesa basculante) muda totalmente o esforço.
- Força por alça = W·k_din·k_sucção/n_efetivo ÷ sen(ângulo do cabo) — com 4 alças sem balancim considerar **só 2 efetivas**; cabo a 60° → +15 %.
- Estocagem vertical em cavalete (arquitetônico) ou deitada com apoios alinhados verticalmente a ~0,2 L.
- Montagem: sequência de baixo para cima; prumo e alinhamento por calços; tie-backs definitivos antes de soltar o guindaste ou escoramento provisório; vedação das juntas por último.

## 9. Exemplo ND (refeito em Python, `paineis_nd.py`)
Painel maciço horizontal 7,5 × 2,5 m × 180 mm, C40, galpão no PR (V0 = 45 m/s, S2 = 0,86, cp líquido 1,2):
- q = 0,92 kN/m² → p = 1,10 kN/m²; **Md vento = 1,4·1,10·7,5²/8 = 10,8 kN·m/m** → As ≈ 190 mm²/m < mínimo → **governa armadura mínima** nas duas faces.
- Peso W = 84,4 kN (8,6 t) → apoio 42,2 kN (k); vento por lado 10,3 kN (k) → 2 tie-backs por pilar ≈ 7,2 kN (d) cada — compare: ligação ensaiada de Castilho 23 kN (k).
- **Empilhado 4×** (10 m de altura): consolo de base Rd = 1,4·4·84,4/2 = **236 kN**; painel de base no plano Md = 443 kN·m → As de borda ≈ 509 mm² (3Ø16) com z = 2,0 m.
- **Desforma deitada com 2 linhas de alças**: m = 0,0214·11,25·7,5²/2,5 × 1,3 × 1,2 = 8,45 kN·m/m → σ = 1,56 MPa > fctk,inf(30)/1,5 = 1,35 MPa → **fissura**: usar 4 linhas com balancim (σ ≈ 0,4 MPa), mesa basculante, ou desformar com fcj maior.
- Alça na montagem (2 alças de topo, vertical): 84,4 × 1,3/2 = 55 kN por alça (63 kN com cabo a 60°) → escolher inserto de catálogo com fator de segurança do fabricante (usual 3–4 sobre a ruptura do concreto/aço — conferir).
- Dilatação 7,5 m, ΔT 30 °C → 2,25 mm; arqueamento por gradiente de 10 °C → 3,9 mm no meio do vão → junta e fixação com folga.

## 10. Código validado — `paineis_nd.py` (rodado em 07/10/2026, 38/38 PASS)
| Teste | Resultado | Referência |
|---|---|---|
| T29–T31 Ce, Fvy,min, Fvy (P1–P4) | 0,603/16,6/21,7; 0,584/32,1/45,0; 0,721/111,3/143,9; 0,621/91,7/117,2 kN | tab. 16 (Ferreira & El Debs) |
| T32–T35 Fv,tot P1–P4 | 29,9 / 64,1 / 157,5 / 148,7 kN | 29,9 / 64,1 / 157,5 / 148,9 |
| T36/T37 kc, α1 (P1) | 109,6 MPa/mm / 28,7 m⁻¹ | tab. 18 |
| T38–T41 λ P1–P4 | 0,0293 / 0,0155 / 0,0091 / 0,0095 mm/kN | tab. 18 (kc2 do P1 com fcj 55) |
| T52–T55 α_crit, ℓp, a_vy | 0,096 rad / 28 mm / 2,71 / 2,69 mm | tab. 20 |
| T42–T48 interface (viga 1 e 3 de Araújo) | 3,73 / 4,21 / 3,97 / 3,80 / 5,03 / 0,93 / 1,19 MPa | tab. 5(b), 7 |
| T49 rigidez pino 50/200 mm | 64× | 12EI/L³ |
| T50 Δ 6 m, ε 25e-5 | 1,5 mm | Castilho |
| T51 M içamento 2 pontos | 9,63 kN·m | 0,0214·w·L² |
| T56/T57 empilhado 4× | 236 kN / 509 mm² | conta à mão |

Achados na validação: (1) no artigo de Ferreira o **Ce é calculado com o concreto mais forte e usado também em Fvy,min**; (2) Fv,tot dos protótipos 1–2 usa fsy cheio (sem atrito) e dos 3–4 usa 0,7 fsy + atrito com μ 0,5 e 0,4; (3) a tab. 20 imprime λ dos P3/P4 como ×10⁻² (é ×10⁻³); (4) Mattock (1994) não foi reproduzido (fórmula ilegível no PDF).

```python
"""paineis_nd.py — painéis pré-moldados de fechamento + ligações com pino/chumbador + interface (Caderno EESC 17/2001).
Unidades: N, mm, MPa salvo indicação. (conferir) = checar NBR 9062:2017 / 16475:2017 / 6118:2023 / 6123 / PCI."""
import math

# ---------- 1. Chumbador/pino em concreto: resistência (Engström 1992, via Ferreira & El Debs 2001) ----------
_C1 = [(15, 1.19), (25, 1.22), (35, 1.25), (45, 1.27), (55, 1.29)]          # f_c cilíndrico (tab. 1)
def C1_tab(fc):
    for (a, ya), (b, yb) in zip(_C1, _C1[1:]):
        if fc <= a: return ya
        if fc <= b: return ya + (yb - ya) * (fc - a) / (b - a)
    return _C1[-1][1]

def Ce(phi, e, fcc, fsy, C1):                    # fator de excentricidade (e = h_almofada/2 ou folga/2)
    eps = 3 * e / phi * math.sqrt(fcc / fsy)
    return math.sqrt(1 + (C1 * eps) ** 2) - C1 * eps

def F_vy(phi, fcc, fsy, e=0.0, n=1, Cr=1.0, C1=1.24, Ce_=None):
    """Força de escoamento (2 rótulas plásticas) por barra × n. Cr 1–1,42 (grau de restrição à rotação)."""
    ce = Ce(phi, e, fcc, fsy, C1) if Ce_ is None else Ce_
    return n * Cr * ce * C1 * phi ** 2 * math.sqrt(fcc * fsy)

def F_v_total(phi, fcc, fsy, n=1, mu=0.0, sig_sm=0.0, C1=1.03):
    """Pino + atrito (barra ancorada nas 2 pontas): C1·φ²·√(fcc·fsy,red) + μ·σsm·As, fsy,red = fsy − σsm."""
    As = math.pi * phi ** 2 / 4
    return n * (C1 * phi ** 2 * math.sqrt(fcc * (fsy - sig_sm)) + mu * sig_sm * As)

# ---------- 2. Deformabilidade ao cisalhamento: almofada + chumbador (Ferreira 1999, eq. 5) ----------
def kc(fc, phi):  return 127 * math.sqrt(fc) / phi ** (2 / 3)           # MPa/mm (Dei Poli et al. 1992)
def alfa(fc, phi, Es=200000):
    Ib = math.pi * phi ** 4 / 64
    return (kc(fc, phi) * phi / (4 * Es * Ib)) ** 0.25                       # 1/mm

def lambda_lig(G, Ao, hn, phi, fc1, fc2, n=1, Es=200000):
    """mm/N. Elastômero (G·Ao/hn) em paralelo com n×[barra bi-engastada na altura livre + 2 trechos embutidos]."""
    Ib = math.pi * phi ** 4 / 64
    flex_bar = hn ** 3 / (12 * Es * Ib) + sum(1 / (3.5 * Es * Ib * alfa(f, phi, Es) ** 3) for f in (fc1, fc2))
    return 1 / (G * Ao / hn + n / flex_bar)

def desloc_escoamento(phi, fc_min, fc_max, hn, fsy=250.0, C1=1.24, Es=200000, fsy_red_frac=0.7):
    """a_vy (mm) na formação das 2 rótulas no chumbador (Engström/Ferreira, eq. 8–11):
    α_crit = 1,75·fsy,red/(Es·φ[m]) (empírica, φ em metros); x_i = φ/(3C1)·√(fsy,red/fc_i); ℓp = x1 + x2 + hn."""
    fsr = fsy_red_frac * fsy
    a_crit = 1.75 * fsr / (Es * phi / 1000)
    x1 = phi / (3 * C1) * math.sqrt(fsr / fc_min); x2 = phi / (3 * C1) * math.sqrt(fsr / fc_max)
    lp = x1 + x2 + hn
    return dict(a_crit=a_crit, x1=x1, x2=x2, lp=lp, a_vy=a_crit * lp)

# ---------- 3. Interface pré-moldado × moldado no local (Araújo & El Debs 2001) ----------
def tau_walraven(fc, rfy):  return 0.878 * fc ** 0.406 * rfy ** (0.167 * fc ** 0.303)
def tau_mattock88(fc, rfy, sn=0.0):  return min(0.467 * fc ** 0.545 + 0.8 * (rfy + sn), 0.3 * fc)
def tau_mau_hsu(fc, rfy):  return min(0.66 * math.sqrt(fc * rfy), 0.3 * fc)
def tau_patnaik(fc, rfy):  return min(0.6 * math.sqrt((0.1 + rfy) * fc), 0.25 * fc)
def tau_tassios_lim(fc, sn):  return 0.44 * fc ** 0.67 * sn ** 0.33        # escorregamento ~1,4 mm
def tau_nbr9062(rho, fyd, ftd, interp_bc=True):
    """τrd = βs·ρ·fyd + βc·ftd; ρ ≤ 0,2 %: βs 0, βc 0,3; ρ ≥ 0,5 %: βs 0,9, βc 0,6; linear entre (conferir 9062:2017).
    Limite sugerido (FIP 1982 / artigo): τ ≤ 0,25 fc."""
    t = min(max((rho - 0.002) / 0.003, 0), 1)
    bs, bc = 0.9 * t, (0.3 + 0.3 * t) if interp_bc else 0.3
    return bs * rho * fyd + bc * ftd

# ---------- 4. Painel de fechamento — verificações de projeto (conhecimento ND; PCI/NBR, conferir) ----------
def vento_q(V0, S1=1.0, S2=1.0, S3=1.0):                                    # NBR 6123: kN/m²
    Vk = V0 * S1 * S2 * S3; return 0.613 * Vk ** 2 / 1000

def painel_horizontal(L, H, t, p_vento, gc=25.0, gamma_f=1.4):
    """Painel deitado entre pilares (vão L, altura H, espessura t, m; p kN/m²). Flexão fora do plano por faixa de 1 m."""
    Md = gamma_f * p_vento * L ** 2 / 8                                      # kN·m/m
    W = gc * L * H * t                                                       # kN
    return dict(Md_vento=Md, peso=W, reac_apoio_grav=W / 2, reac_vento_por_lado=p_vento * L * H / 2)

def icamento(W, n_alcas_efetivas, k_din=1.3, k_succao=1.0, ang_cabo_deg=90):
    """Força por alça (kN). Cabo inclinado: ÷ sen(ângulo com a horizontal). k_din 1,3 (NBR 9062, conferir);
    sucção na desforma 1,2–1,4 sobre o peso conforme acabamento (PCI, conferir)."""
    return W * k_din * k_succao / n_alcas_efetivas / math.sin(math.radians(ang_cabo_deg))

def momento_icamento_2pontos(w, a):                                          # alças a 0,207a das pontas: M+ = M− = 0,0214·w·a²
    return 0.0214 * w * a ** 2

def tensao_ok(M, b, t, fctk, FS=1.5):                                        # ELS sem fissura no manuseio (kN·m, m, MPa)
    sig = M / (b * t ** 2 / 6) / 1000; return sig, sig <= fctk / FS

def fctk_inf(fck):  return 0.7 * 0.3 * fck ** (2 / 3)                       # NBR 6118 (fck ≤ 50)

def k_pino(phi, L, E=210000, apoio='bi-engastado'):                          # N/mm
    I = math.pi * phi ** 4 / 64; c = 12 if apoio == 'bi-engastado' else 3
    return c * E * I / L ** 3

def dilatacao(L_mm, dT=None, eps=None, alfa=1e-5):
    return L_mm * (eps if eps is not None else alfa * dT)

def bowing_termico(L_mm, t_mm, dT_grad, alfa=1e-5):                          # flecha por gradiente na espessura
    return alfa * dT_grad * L_mm ** 2 / (8 * t_mm)

def forcas_ligacoes(W, e_cg, z, p, A_trib_topo, A_trib_base):
    """Esquema isostático: 2 apoios de gravidade na base (W/2 cada) + tie-backs no topo.
    e_cg = excentricidade do CG do painel em relação ao apoio (m), z = distância vertical apoio→tie-back (m).
    Binário H = W·e/z (tração/compressão nos tie-backs e reação oposta no apoio). Vento por área tributária."""
    H = W * e_cg / z
    return dict(V_apoio=W / 2, H_binario_total=H, vento_topo=p * A_trib_topo, vento_base=p * A_trib_base)

def painel_empilhado(n_paineis, W_painel, L, H, gamma_f=1.4, z_frac=0.8, fyd=435.0):
    """Painéis empilhados (junta horizontal com elastômero) e só o inferior apoiado nos consolos dos pilares:
    reação de cálculo por consolo e armadura de borda inferior do painel de base (viga-parede, z ≈ 0,8·H ≤ 0,8·L)."""
    Wtot = n_paineis * W_painel; Rd = gamma_f * Wtot / 2
    Md = gamma_f * Wtot * L / 8; z = z_frac * min(H, L)
    return dict(R_consolo_d=Rd, Md_plano=Md, As_borda_mm2=Md / z / fyd * 1e3)

if __name__ == '__main__':
    ok = []
    def T(nome, calc, ref, tol=0.03):
        good = abs(calc - ref) <= tol * abs(ref); ok.append(good)
        print(f"{'PASS' if good else 'FAIL'} {nome}: {calc:.4g} (ref {ref})")
    # Tab. 16/17 Ferreira & El Debs — Ce do artigo calculado com fc,máx e usado também em Fvy,min
    for nome, phi, n, Cr, e, fmin, fmax, ref in [
        ('P1', 16, 1, 1.0, 5, 30, 51.5, (16.6, 21.7, 0.60)), ('P2', 16, 2, 1.0, 5, 30, 59.0, (32.1, 45.0, 0.58)),
        ('P3', 25, 2, 1.15, 5, 30, 50.2, (111.3, 143.9, 0.72)), ('P4', 25, 2, 1.1, 7.5, 30, 49.0, (91.7, 117.4, 0.62))]:
        ce = Ce(phi, e, fmax, 250, 1.24)
        T(f'T29 {nome} Ce', ce, ref[2], 0.03)
        T(f'T30 {nome} Fvy,min kN', F_vy(phi, fmin, 250, n=n, Cr=Cr, Ce_=ce) / 1e3, ref[0])
        T(f'T31 {nome} Fvy kN', F_vy(phi, fmax, 250, n=n, Cr=Cr, Ce_=ce) / 1e3, ref[1])
    T('T32 P1 Fv,tot (pino, fsy cheio)', F_v_total(16, 51.5, 250) / 1e3, 29.9)
    T('T33 P2 Fv,tot', F_v_total(16, 59, 250, n=2) / 1e3, 64.1)
    T('T34 P3 Fv,tot (μ=0,5; σsm 75)', F_v_total(25, 50.2, 250, n=2, mu=0.5, sig_sm=75) / 1e3, 157.5)
    T('T35 P4 Fv,tot (μ=0,4; σsm 75)', F_v_total(25, 49.0, 250, n=2, mu=0.4, sig_sm=75) / 1e3, 148.93)
    # Tab. 18 — deformabilidade (kc2 do P1 usa fcj = 55 MPa no artigo)
    T('T36 kc P1 graute', kc(30, 16), 109.55, 0.01); T('T37 α1 P1 (1/m)', alfa(30, 16) * 1e3, 28.72, 0.01)
    T('T38 λ P1 (mm/kN)', lambda_lig(1.0, 45000, 10, 16, 30, 55, 1) * 1e3, 0.0293, 0.03)
    T('T39 λ P2', lambda_lig(1.0, 45000, 10, 16, 30, 59, 2) * 1e3, 0.0155, 0.04)
    T('T40 λ P3', lambda_lig(1.0, 75000, 10, 25, 30, 50.2, 2) * 1e3, 0.00917, 0.04)
    T('T41 λ P4', lambda_lig(1.0, 60000, 15, 25, 30, 49.0, 2) * 1e3, 0.00949, 0.04)
    d=desloc_escoamento(16,30,51.5,10); T('T52 α_crit φ16',d['a_crit'],0.096,0.01); T('T53 ℓp P1 (mm)',d['lp'],28,0.03); T('T54 a_vy P1 (mm)',d['a_vy'],2.71,0.02)
    T('T55 a_vy P4 (mm)',desloc_escoamento(25,30,49,15)['a_vy'],2.69,0.02)
    # Araújo & El Debs tab. 5(b), viga 1 (fc 39,8; ρfy 0,91)
    T('T42 Walraven', tau_walraven(39.8, 0.91), 3.73); T('T43 Mattock 88', tau_mattock88(39.8, 0.91), 4.20)
    T('T44 Mau-Hsu', tau_mau_hsu(39.8, 0.91), 4.00, 0.04); T('T45 Patnaik', tau_patnaik(39.8, 0.91), 3.80)
    T('T46 Tassios lim', tau_tassios_lim(39.8, 0.91), 4.97, 0.03)
    T('T47 NBR9062/85 viga 1 (sem γ)', tau_nbr9062(0.0015, 600, 0.06 * 39.8 + 0.7), 0.93)
    T('T48 NBR9062/85 viga 3 — artigo (βc fixo 0,3)', tau_nbr9062(0.0025, 600, 0.06 * 41.67 + 0.7, False), 1.19)
    # Castilho et al.: rigidez do "pino" Ø12,5 bi-engastado no modelo — razão 200→50 mm = 64×
    T('T49 k pino 50/200', k_pino(12.5, 50) / k_pino(12.5, 200), 64.0, 0.001)
    T('T50 Δ painel 6 m, ε = −25e-5 (mm)', dilatacao(6000, eps=25e-5), 1.5, 0.001)
    T('T51 M içamento 2 pontos w 4,5 kN/m a 10 m', momento_icamento_2pontos(4.5, 10), 9.63, 0.01)
    e=painel_empilhado(4,84.375,7.5,2.5); T('T56 empilhado 4×: R consolo d (kN)',e['R_consolo_d'],236.25,0.001); T('T57 As borda (mm²)',e['As_borda_mm2'],509.2,0.01)
    print(f"{sum(ok)}/{len(ok)} PASS")
```
Destino no software ND: módulo `prefabricados/paineis` (Parte D da skill `projetos-estruturais-concreto-armado-protendido`); interface e chumbador também servem às skills de sistemas e consultoria.

## 11. Roteiro — projeto de painel de fechamento
1. Tipo de painel (3) pela arquitetura, isolamento, fogo, vão entre pilares, altura e fábrica disponível; modulação e peso por peça (guindaste/transporte).
2. Hipótese estrutural (4): fechamento isostático flexível (padrão) ou painel enrijecedor (ligação calculada e ensaiada) — registrar.
3. Ações (5): vento por zona (NBR 6123), peso, Δvol, transitórias com coeficientes dinâmicos.
4. Dimensionar o painel: fora do plano, no plano (empilhado = viga-parede), manuseio/desforma (fissura), aberturas.
5. Escolher e calcular as fixações (6): apoios de gravidade, tie-backs, pino/inserto/trilho; ancoragem no concreto; folgas e furos oblongos; corrosão; fogo.
6. Verificar o reflexo na estrutura: consolos dos pilares, torção em vigas de borda, vento transmitido aos pilares (o fechamento é que leva o vento ao pórtico).
7. Detalhar (7) e gerar pranchas (`pranchas-tecnicas-nd`): fôrma, armação, insertos, ligação 1:5, junta, plano de montagem com marcas.
8. Quantitativo/orçamento (`orcamentista-obras`): m² e m³ de painel, kg de aço/tela, cordoalha, un de insertos/alças/trilhos/cantoneiras (kg, galvanizado/inox), m de selante + tarucel, elastômero, horas de guindaste por peça, frete por peso/dimensão.

## 12. Armadilhas
- Três ou mais apoios de gravidade na mesma linha, ou todos os pontos fixos: o painel trava, atrai Δvol e fissura (Castilho: pino curto → 45,6 kN contra 23 kN de resistência).
- Contar o painel no contraventamento sem ligação dimensionada para vento + Δvol (ou o contrário: ignorar o vento que o painel descarrega no pilar).
- Painel apoiado no meio do vão de viga sem liberar a flecha/fluência.
- Painel de base de pilha sem armadura de borda/viga-parede e consolo dimensionado só para o próprio peso.
- Armadura só numa face em painel de vento (sucção inverte o momento).
- Desforma/içamento verificados com fck de 28 dias (usar fcj da operação) e sem sucção/coef. dinâmico; 4 alças sem balancim contadas como 4.
- Pino/chumbador com folga grande (Ce baixo) ou φ/hn < 1; esquecer o giro relativo (flexão local no pino).
- Inserto perto de borda sem armadura de ancoragem; trilho em zona fissurada sem verificar a capacidade do catálogo.
- Junta mais estreita que movimento/0,25 + tolerância; selante aplicado sem tira de apoio (3 faces aderidas).
- Usar valores do estudo de caso (vento 0,8 kN/m², ε 25 × 10⁻⁵, 23 kN) como norma: são do caso Reago, não critérios gerais.