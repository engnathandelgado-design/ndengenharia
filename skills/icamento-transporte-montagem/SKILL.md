---
name: "icamento-transporte-montagem"
description: "Use ao verificar situações transitórias de pré-moldados pela NBR 9062:2017 — desforma, içamento com 2 a 6 pontos e com dois equipamentos, alças e insertos, tombamento lateral, transporte, estocagem e montagem — com imagem simulada do arranjo."
---

# Içamento, transporte, estocagem e montagem de pré-moldados

Skill de verificação das fases transitórias de peça pré-moldada, da desforma até a ligação definitiva. Responder em português técnico. Não repete concepção de sistema (`projeto-estruturas-pre-moldadas`), checklist de fábrica e exemplo de viga com capa na montagem (`consultoria-fabricas-pre-moldados`, seção 2) nem cálculo de viga protendida (`vigas-premoldadas-protendidas`).

## 1. Normas e edições

| Norma | Edição usada | Situação |
|---|---|---|
| ABNT NBR 9062 — Projeto e execução de estruturas de concreto pré-moldado | 2017 (publicada 15/03/2017) | vigente; revisão em andamento na ABNT (sem nova edição publicada até a pesquisa) |
| ABNT NBR 6118 — Projeto de estruturas de concreto | 2023 | vigente |
| ABNT NBR 15961-1 — Transporte e montagem de elementos pré-moldados, parte 1: estruturas | edição a confirmar (citada como 2011) | conferir |
| ABNT NBR 6123 — Forças devidas ao vento | edição a confirmar | conferir |
| ABNT NBR 7483 (cordoalhas), NBR ISO 2408 (cabos de aço), NBR 13541-1 (lingas de cabo), NBR 15637 (cintas têxteis), NBR 13545 (manilhas) | edição a confirmar | referências de acessórios |
| NR-11, NR-12, NR-18, NR-35 | versão vigente do MTE a confirmar | segurança da operação |
| PCI Design Handbook / Mast (1989, 1993) | referência técnica | estabilidade lateral |
| VDI/BV-BS 6205 (insertos de içamento) | 2021-09 | referência de fabricantes de insertos |

## 2. Escopo e quando NÃO usar
Usar para: fckj de desforma/saque, carga estática equivalente (coeficiente dinâmico), posição das alças (2 a 6 pontos, um ou dois equipamentos), força nos cabos, alças e insertos, tombamento lateral no içamento e no transporte, apoios de estocagem e carreta, plano de montagem (sequência, escoramento, contraventamento provisório, vento).

Não usar para:
- Dimensionamento final em serviço da peça: `vigas-premoldadas-protendidas`, `dimensionamento-concreto-armado-nbr`, `projetos-estruturais-concreto-armado-protendido`.
- Painéis de fachada (virada, insertos de fixação): `paineis-fechamento-pre-moldados`.
- Laje alveolar (estocagem e diferença de contraflecha): `lajes-alveolares-nbr14861`.
- Chumbador químico em montagem (ancoragem pós-instalada): `ancoragem-barras-pos-instaladas`.
- Pórtico/peça metálica provisória: `estruturas-metalicas-nd`.
- Plano de rigging operacional e logística de obra: `construtor-senior`; custo de guindaste e frete: `orcamentista-obras`.

## 3. Roteiro de verificação

1. **Listar as fases** de cada peça: desforma (saque), giro/virada, estocagem, carga na carreta, transporte, descarga, içamento na obra, posição provisória, ligação definitiva. Para cada fase: esquema estático, apoios, idade/fckj, carga.
2. **Hipótese de resistência**: fckj na idade da fase (desforma e liberação ≠ fck28). Com cura térmica, usar corpo de prova curado junto da peça. Ecj e fctj pelas expressões da NBR 6118 com fckj.
3. **Carga estática equivalente**: g_eq = β_a · g_pp, com β_a da seção 4.1. No saque somar a aderência/sucção da fôrma quando relevante (conferir no PDF, item 5.3.2).
4. **Posição das alças** (seção 4.2) para minimizar momento; calcular M+ e M- com g_eq; verificar fissuração (σt ≤ fctk,inf,j em peça que não pode fissurar; em protendida, combinar com a protensão na idade j) e ELU com γ da NBR 9062 para a fase.
5. **Força na alça**: F = g_eq·P / (n · sen θ) (θ medido da horizontal) ou F = g_eq·P/(n · cos α) (α medido da vertical). Escolher alça ou inserto com carga de trabalho ≥ F na direção real (axial, oblíqua, transversal).
6. **Ancoragem da alça/inserto** no concreto com fckj do içamento: comprimento, armadura de reforço do fabricante, distância à borda e entre insertos.
7. **Tombamento lateral** (vigas longas e esbeltas): içamento e transporte pelo método de Mast (seção 4.5); decidir balancim, ponto de pega, travamento.
8. **Estocagem e transporte**: apoios nos mesmos pontos do içamento, balanço máximo na carreta, momento negativo, fissuração por torção em estrada irregular.
9. **Montagem**: plano de montagem obrigatório (seção 4.7), sequência, escoramento, contraventamento provisório, vento na fase sem diafragma.
10. **Imagem simulada** do arranjo (seção 4.2.2).
11. **Decisão**: registrar na prancha fckj de desforma/içamento, posição das alças cotada, pontos de estocagem/transporte, ângulo mínimo de linga, sequência e travamentos provisórios.

## 4. Valores normativos

### 4.1 Coeficiente de amplificação dinâmica (carga estática equivalente)
- Item: NBR 9062:2017, 5.3.2 (solicitações dinâmicas no manuseio, transporte e montagem) [verificado: NBR 9062:2017 5.3.2; Marin, apresentação ABCIC 24/08/2017].
- β_a = 1,3 quando o acréscimo de g é desfavorável; β_a = 0,8 quando o alívio de g é desfavorável [verificado: NBR 9062:2017 5.3.2; dissertação UFU "Análise dinâmica de vigas longas... içamento", que transcreve a norma].
- β_a = 1,4 sob circunstâncias desfavoráveis de manuseio/transporte [verificado: mesma fonte UFU; conferir no PDF, item 5.3.2, quais circunstâncias].
- Peças com peso acima de 300 kN: permite-se coeficiente inferior a 1,3 [verificado: mesma fonte UFU; valor mínimo admitido (conferir no PDF, item 5.3.2)].
- Tensão na armadura do pilar no transporte e içamento limitada a 0,5 fyk [verificado: NBR 9062:2017 5.3.2; Marin, ABCIC 2017].
- Referência comparativa: PCI usa 1,2 a 1,5 conforme a operação [verificado: PCI Bridge Design Manual 2014, via dissertação UFU].
- Rigging (fator do plano de içamento, não do cálculo da peça): FAD 1,15 para peças até 100 t; fator de peso calculado 1,05 a 1,10; fator de utilização do guindaste 0,8 a 0,9, e 0,75 com dois guindastes [verificado: ABCIC, Manual de Montagem 2019, slides F. Francisco; não é texto da NBR 9062].

### 4.2 Pontos de içamento ótimos (peça prismática, carga uniforme)
Dedução própria (equilíbrio, conferida numericamente em Python em 11/10/2026). Posições que igualam os momentos positivo e negativo, com reações iguais (balancim, polias ou equalizador), medidas a partir de cada ponta:

| Pontos | Posições (fração de L) | M máx | Redução vs. 2 pontos |
|---|---|---|---|
| 2 | 0,207 · 0,793 | q·L²/46,6 | 1,0× |
| 3 | 0,138 · 0,500 · 0,862 | q·L²/105 | 2,3× |
| 4 | 0,104 · 0,394 · 0,606 · 0,896 | q·L²/186 | 4,0× |
| 5 | 0,083 · 0,304 · 0,500 · 0,696 · 0,917 | q·L²/291 | 6,2× |
| 6 | 0,069 · 0,255 · 0,421 · 0,579 · 0,745 · 0,931 | q·L²/420 | 9,0× |

- A tabela só vale com reações iguais. Para 3 ou mais pontos num único gancho isso exige balancim em cascata, polias ou equalizador; sem isso as reações ficam desiguais.
- **Cabos fixos sem equalização (3 a 6 pontos)**: a peça vira viga contínua sobre apoios elásticos e a distribuição depende do comprimento real de cada cabo. Calcular como viga contínua sobre apoios rígidos para ter a ordem de grandeza, mas dimensionar alças e insertos supondo só 2 pontos efetivos (conferir no PDF, item a localizar). Na viga contínua sobre 3 apoios iguais, o apoio central leva 62,5 % da carga — erro clássico de quem divide por 3.
- Pilar içado na horizontal e virado: na virada com 1 ponto de pega e a base no chão, o ótimo muda (ponta apoiada); calcular o giro em várias inclinações.
- Desvio executivo da alça: até 25 mm (1") admitido pelo PCI, pode elevar a tração máxima em até 30% [verificado: PCI 2011 via UFU, "Avaliação da segurança durante o içamento"].
- **Pontos fora da posição ótima ou peça com seção variável** (vigas I com bloco de extremidade, painel com abertura, pilar com consolo): o CG sai do centro. Com equalização a peça inclina até o CG ficar sob o gancho; verificar a inclinação e a folga da carga.

### 4.2.1 Içamento com dois equipamentos (tandem)
- Cada equipamento recebe a carga pela estática com as resultantes de cada grupo de pontos: F_A = W·(c_B − x_CG)/(c_B − c_A) e F_B = W − F_A, onde c_A e c_B são os centros dos grupos de pontos de cada guindaste.
- Dentro de cada grupo, com balancim, as reações são iguais (F_A/k_A). Com 2+2 pontos nas posições da tabela de 4 pontos, os momentos ficam iguais aos de 4 pontos equalizados.
- Utilização de cada guindaste em tandem ≤ 75 % da capacidade no raio [verificado: ABCIC, Manual de Montagem 2019, prática de rigging, não é texto da NBR 9062]. Um guindaste só, 80 a 90 %.
- Se o CG sair do trecho entre c_A e c_B, um guindaste descarrega e o outro leva tudo: ERRO.
- Movimento coordenado: um sinaleiro, mesma velocidade de içamento, sem giro simultâneo; plano de rigging assinado (NR-11/NR-18).
- Virada de peça com dois equipamentos (pilar, painel deitado → vertical): no início da virada um equipamento leva quase tudo; calcular as cargas em 0°, 30°, 60° e 90°.

### 4.2.2 Imagem simulada do arranjo (obrigatória em plano de içamento e em proposta)
Sempre que a resposta envolver arranjo de içamento, gerar um desenho esquemático em SVG, ou usar a aba Içamento das Ferramentas ND, com:
1. peça em escala, com CG marcado;
2. gancho(s) e equipamentos identificados (A, B);
3. balancim(ns) desenhado(s) quando houver equalização; cabos em linha do gancho até cada alça;
4. reação de cada alça em kN, já com o coeficiente dinâmico;
5. diagrama de momentos abaixo da peça, com máximos positivo e negativo;
6. ângulo do cabo e comprimento do balancim cotados;
7. selo "projeto da ND Engenharia" no canto do desenho (padrão ND para imagens).
Para material de cliente ou marketing, não indicar perfil, bitola ou material do balancim nem das alças.

### 4.3 Ângulo dos cabos e força na alça
- Ângulo do cabo com a vertical menor que 45° (cabo a mais de 45° da horizontal); linga com pernas a 60° da vertical não é permitida [verificado: NBR 9062:2017 11.2.4; ABCIC, Manual de Montagem 2019, slides].
- Força por perna: F = W_eq / (n · cos α), α em relação à vertical. α = 0°: 1,00; 30°: 1,15; 45°: 1,41; 60°: 2,00 (trigonometria).
- Componente horizontal H = F·sen α comprime a peça e solicita a alça lateralmente: usar balancim quando α > 45° ou quando a peça é esbelta.
- Lingas e ganchos: fator de segurança 5:1 e gancho com trava [verificado: ABCIC, Manual de Montagem 2019; NR-11/NBR 13541 (conferir no PDF, item a localizar)].
- Em 4 pernas sem equalizador, considerar só 2 trabalhando (prática de rigging; conferir no PDF, item a localizar).

### 4.4 Alças e insertos de içamento
- Item: NBR 9062:2017, 5.3.3 (alças e dispositivos de içamento) [verificado: Marin, ABCIC 2017].
- Vedado o aço CA-25; alternativa ASTM A36 [verificado: NBR 9062:2017 5.3.3; Marin, ABCIC 2017].
- Materiais admitidos: ASTM A36, cordoalhas (NBR 7483) e cabos de aço (NBR ISO 2408); ASTM A36 só nas bitolas de 10 mm a 25 mm [verificado: NBR 9062:2017 5.3.3; TCC FAG 2024 que transcreve o item].
- CA-50/CA-60 dobrado como alça: fora da lista acima, portanto não usar (conferir no PDF, item 5.3.3).
- Alça deve resistir com segurança a impactos, acelerações, choques, inclinações e cargas dinâmicas, com os coeficientes de 5.3.2 [verificado: NBR 9062:2017 5.3.3; TCC FAG].
- Coeficiente de segurança/tensão admissível da alça, diâmetro do pino/gancho e comprimento de ancoragem: (conferir no PDF, item 5.3.3). Não usar fórmula de memória.
- Alça de cordoalha: capacidade cresce com o diâmetro do pino/gancho; laço curto em gancho fino corta a cordoalha [verificado: ABCIC, Manual de Montagem 2019].
- Insertos comerciais (âncora com cabeça, bucha rosqueada, âncora chata): usar a carga de trabalho (WLL) do catálogo, que já embute fatores de segurança de aço e de cone de concreto; exigir do fabricante tabela por fckj mínimo, distância à borda, espessura da peça, direção da carga (axial, oblíqua 45°, transversal/virada) e armadura de reforço. Base de ensaio: VDI/BV-BS 6205:2021. Valores dos fatores (aço e concreto): (conferir no PDF do fabricante / VDI 6205, item a localizar).
- Ancoragem de alça em barra com solda de barra transversal: α = 0,7 (NBR 6118:2023, 9.4.2.5) [verificado: NBR 6118:2023 9.4.2.5; TCC FAG].

### 4.5 Tombamento lateral (vigas longas)
- Pré-verificação geométrica da NBR 9062:2017: L·h/bf² e L/bf com limites 500 e 50 [verificado parcialmente: NBR 9062:2017 via UFU "Avaliação da segurança durante o içamento", que transcreve com sinal ambíguo; (conferir no PDF, item a localizar) o sentido das desigualdades]. NBR 6118:2023 15.10: b ≥ l0/50 e b ≥ βfl·h (βfl = 0,4 para seção retangular) (conferir no PDF, item 15.10).
- Atender à verificação geométrica não dispensa Mast em viga protendida longa com alças próximas das pontas.
- Método de Mast (viga pendurada gira em torno do eixo das alças):
  - θi = ei / yr; yr = altura do eixo de giro acima do CG (inclui altura do laço).
  - z0 = q/(12·E·Iy·L) · (l1⁵/10 − a²·l1³ + 3a⁴·l1 + 6a⁵/5), l1 = L − 2a (a = balanço) [verificado: Mast 1993 via Krahl 2014 (EESC) e IDEA StatiCa, exemplo de verificação].
  - Equilíbrio (θ < 0,2 rad): θ = ei / (yr − z0). yr ≤ z0 → instável.
  - Fator de segurança à fissuração: FSc = 1 / (z0/yr + θi/θmax); θmax = ângulo que fissura a mesa superior (M_lateral de fissuração / M_peso próprio) [verificado: Mast 1993 via Krahl 2014].
  - Limites: FSc ≥ 1,0 e FS ruptura ≥ 1,5 [verificado: Mast 1993 via Krahl 2014 e UFU]; Imper e Laszlo: 1,5 em fábrica e 1,75 em campo [verificado: via Krahl 2014].
  - ei = varredura lateral + desvio da alça. Varredura: EN 15050 L/500, EHE-08 L/750, PCI L/960, fib MC2010 L/300; medição em 128 vigas: L/472 [verificado: UFU "Avaliação da segurança durante o içamento"].
  - E: usar Ecj na idade do içamento.
- Balanço maior (alças afastadas das pontas) reduz z0 aproximadamente na 4ª potência do trecho livre e melhora a estabilidade [verificado: IDEA StatiCa; UFU].
- Transporte: mesma lógica com rigidez à rotação da carreta/apoio e inclinação transversal da via (Mast 1993); exigir FS ≥ 1,5 à ruptura [verificado: Mast 1993 via Krahl 2014]. Inclinação de pista e rigidez dos pneus: (conferir no PDF, item a localizar — PCI).

### 4.6 Desforma, estocagem e transporte
- Liberação de protensão em peça pré-tracionada: fckj ≥ 21 MPa [verificado: NBR 9062:2017 (item a localizar); ABCIC, slides de controle de qualidade].
- Desforma de peça armada: fckj ≥ 0,5 fck e ≥ 10 MPa [verificado: El Debs 2000, via TCC UFMG; não é texto confirmado da NBR 9062 — conferir no PDF, item a localizar].
- Estocagem: peças não apoiadas no solo; apoios em terreno plano e firme; empilhamento com dispositivos de apoio intercalados sem contato direto; atenção a deformação por pouca idade [verificado: NBR 9062:2017 (item a localizar); TCC UFMG que transcreve].
- No máximo duas linhas de apoio por peça empilhada (evita hiperestaticidade por recalque de calço) [verificado: El Debs 2000 via TCC UFMG].
- Calços alinhados na vertical em toda a pilha; altura máxima de pilha: (conferir no PDF, item a localizar) ou definir em projeto pela tensão no calço e estabilidade.
- Transporte: coeficiente da seção 4.1 vale também para a carreta; balanço máximo e dimensões/peso pelo CONTRAN vigente (AET quando exceder) (conferir no PDF, resolução CONTRAN vigente).

### 4.7 Montagem (NBR 9062:2017, seção 11)
- Plano de montagem obrigatório; sequência de trabalho, carregamento crítico, contraventamento e apoios, calços de nivelamento e escoramentos [verificado: NBR 9062:2017 seção 11; Marin, ABCIC 2017].
- Tolerâncias vinculadas às situações transitórias da montagem (seção 11) [verificado: Marin, ABCIC 2017]; valores numéricos (conferir no PDF, seção 11).
- Travamentos provisórios em todas as plantas de montagem; vigas L/T com travamento contra giro quando houver carga de um lado só [verificado: ABCIC, Manual de Montagem 2019].
- Plano de sequenciamento para estabilidade global transitória [verificado: ABCIC, Manual de Montagem 2019].
- Vento na montagem: velocidade máxima de operação do guindaste pela tabela do fabricante; para a estrutura incompleta, vento da NBR 6123 com fator estatístico reduzido para fase de construção (conferir no PDF da NBR 6123, Tabela do fator S3 — valor a confirmar).
- Pilar em balanço sem viga/diafragma: verificar vento + desaprumo de montagem + 2ª ordem com Ecj; escorar/estaiar até grautear cálice e ligar vigas.

## 5. Prática ND — erros comuns de fábrica e obra
- Projeto sem fckj de desforma/içamento: a fábrica saca com 12 MPa e fissura a peça; notas da prancha devem trazer fckj por fase.
- Alça em CA-50 dobrado a frio ou alça de vergalhão reaproveitado: proibido; usar A36 nas bitolas permitidas, cordoalha ou inserto certificado.
- Alça posicionada pela conveniência da fôrma e não pelo 0,207 L: momento negativo fissura o topo da viga protendida (que já tem tração no topo na liberação).
- Mesma peça içada com 4 cabos sem balancim: duas alças levam tudo.
- Linga curta (ângulo aberto) para "caber no pé-direito do galpão": força na alça dobra a 60° e comprime viga esbelta.
- Calços desalinhados na pilha e terceira linha de apoio: fissura transversal por momento negativo e torção.
- Carreta com balanço maior que o previsto (peça comprida) e pista irregular: fissura de torção nas pontas.
- Viga longa içada com alças muito próximas das pontas e varredura lateral grande: tombamento no ar; medir varredura antes de içar.
- Montagem de pilares sem estai e vento à tarde: pilar fora de prumo ou queda antes do graute do cálice.
- Inserto comercial usado com fckj menor que o do catálogo, ou em carga transversal na virada sem a tabela de carga oblíqua.
- Plano de montagem inexistente ou genérico: hoje é obrigatório pela NBR 9062:2017 seção 11.
- Tandem com guindastes de velocidades diferentes ou sem sinaleiro único: um equipamento passa a levar a peça inteira.

## 6. Tabela final de verificação

| Verificação | Condição de falha | Ação |
|---|---|---|
| fckj por fase na prancha | prancha sem fckj de desforma/liberação/içamento | ERRO: incluir fckj por fase (NBR 9062:2017 5.3.2 e item de liberação a localizar) |
| Liberação de protensão | fckj < 21 MPa | ERRO: não liberar; aguardar resistência (NBR 9062:2017, item a localizar) |
| Coeficiente dinâmico | cálculo de içamento sem β_a, ou β_a < 1,3 em peça < 300 kN | ERRO: usar 1,3 (1,4 desfavorável; 0,8 quando alívio é crítico) (NBR 9062:2017 5.3.2) |
| Armadura de pilar no içamento | σs > 0,5 fyk | ERRO: reposicionar pega ou aumentar armadura (NBR 9062:2017 5.3.2) |
| Posição das alças | alças nas pontas ou fora da tabela 4.2 sem cálculo | ALERTA: recalcular M+ e M- e fissuração com β_a |
| Pontos x equalização | 3 a 6 pontos (ou 4 cabos fixos) considerados com reações iguais sem balancim/polias | ERRO: recalcular como viga contínua e dimensionar com 2 pontos efetivos |
| Ângulo do cabo | ângulo com a vertical ≥ 45° | ERRO: usar balancim ou lingas mais longas (NBR 9062:2017 11.2.4) |
| Material da alça | CA-25 | ERRO: vedado (NBR 9062:2017 5.3.3) |
| Material da alça | CA-50/CA-60 ou A36 fora de 10 a 25 mm | ERRO: usar A36 10–25 mm, cordoalha ou cabo (NBR 9062:2017 5.3.3) |
| Inserto comercial | WLL do catálogo < F na direção real ou fckj < mínimo do catálogo | ERRO: trocar inserto ou aguardar resistência |
| Inserto comercial | sem armadura de reforço/distância à borda do catálogo | ALERTA: detalhar conforme fabricante |
| Tombamento no içamento | FSc < 1,0 ou FS ruptura < 1,5 (Mast) | ERRO: afastar alças das pontas, balancim, travamento lateral |
| Varredura lateral | varredura medida > L/500 antes do içamento | ALERTA: recalcular ei e FS; corrigir apoio de estocagem |
| Esbeltez lateral | fora dos limites L·h/bf² e L/bf da NBR 9062 | ALERTA: fazer Mast completo (conferir desigualdades no PDF) |
| Tandem | guindaste acima de 75 % da capacidade no raio | ERRO: trocar equipamento ou raio (prática ABCIC) |
| Tandem | CG fora do trecho entre os grupos de pontos | ERRO: um equipamento descarrega |
| Estocagem | mais de 2 linhas de apoio ou calços desalinhados | ERRO: 2 linhas, calços alinhados, apoios nos pontos de içamento |
| Estocagem | peça sobre o solo ou terreno sem preparo | ERRO: apoios em base firme e plana (NBR 9062:2017, item a localizar) |
| Transporte | balanço na carreta maior que o considerado no cálculo | ERRO: recalcular M- e torção ou mudar apoios |
| Transporte | peso/dimensão acima do limite rodoviário | ALERTA: AET e escolta (CONTRAN vigente) |
| Plano de montagem | inexistente | ERRO: elaborar plano (NBR 9062:2017 seção 11) |
| Travamento provisório | pilar/viga sem estai/escora até a ligação definitiva | ERRO: detalhar contraventamento provisório na planta de montagem |
| Vento na montagem | operação sem limite de vento | ALERTA: fixar velocidade máxima pelo guindaste e verificar a estrutura incompleta |
| Rigging | lingas/ganchos sem FS 5:1 ou sem trava | ERRO: substituir acessório (ABCIC/NR-11) |
| Desenho | plano de içamento sem esquema com reações e momentos | ALERTA: gerar imagem simulada (4.2.2) |

## 7. Ligação com outras skills
- `projeto-estruturas-pre-moldadas` — concepção, critérios de produção/transporte, peso e dimensões de painéis.
- `consultoria-fabricas-pre-moldados` — fases transitórias no checklist da fábrica, exemplo de viga em que a montagem governa, transporte e montagem.
- `vigas-premoldadas-protendidas` — tensões na liberação e no içamento de viga protendida, notas de prancha.
- `lajes-alveolares-nbr14861` — estocagem, içamento com garras e contraflecha de alveolares.
- `paineis-fechamento-pre-moldados` — virada e içamento de painéis.
- `ancoragem-barras-pos-instaladas` — ancoragens provisórias e chumbadores químicos.
- `construtor-senior` — plano de rigging, guindaste, segurança da operação.
- `orcamentista-obras` — custo de guindaste, carreta, AET e equipe de montagem.
- `pranchas-tecnicas-nd` — notas e cotas de içamento na prancha.
- `mef-opensees-opsvis` — modelo de pilar em balanço na montagem e viga suspensa.
- `normas-vigentes-nd` — edições e protocolo de citação.
- `revisao-engenheiro-senior` — revisão final do plano.

## Fontes consultadas
- Marin, M. C. "ABNT NBR 9062 — Projeto e execução de estruturas de concreto pré-moldado" (ABCIC, 24/08/2017): https://abcic.org.br/Arquivos/mp3cydr3.pdf
- ABCIC, Manual de Montagem 2019 (slides, Seminário Concrete): https://abcic.org.br/Arquivos/SLIDES_Apresentação_Manual_Montagem_2019_%20SeminárioConcrete_Francisco.pdf
- ABCIC, slides de controle de qualidade NBR 9062 (fck de liberação, cobrimento): https://abcic.org.br/Arquivos/z3qgj2uu.pdf
- UFU, "Análise dinâmica de vigas longas de concreto protendido pré-moldadas durante operações de içamento": https://repositorio.ufu.br/bitstream/123456789/36223/1/AnaliseDinamicaVigas.pdf
- UFU, "Avaliação da segurança durante o içamento de vigas pré-moldadas": https://repositorio.ufu.br/bitstream/123456789/22523/3/AvaliacaoSegurancaDurante.pdf
- Krahl, P. A. Dissertação EESC-USP 2014 (instabilidade lateral de vigas pré-moldadas): https://producaocientifica.eesc.usp.br/producao/2014ME_PabloAugustoKrahl.pdf
- IDEA StatiCa, "Lateral stability of long prestressed concrete beams during lifting": https://www.ideastatica.com/pt/support-center/verification-examples/lateral-stability-of-long-prestressed-concrete-beams-during-lifting
- TCC FAG 2024 (alças de içamento, NBR 9062 5.3.3): https://www2.fag.edu.br/coopex/arquivos/producao/176498216569337d95b88ff.pdf
- TCC UFMG (estocagem pela NBR 9062:2017, El Debs 2000): https://repositorio.ufmg.br//bitstreams/53552bc6-ccea-4589-8128-fe2b4dbb7f72/download
- VDI/BV-BS 6205:2021: https://vdi.de/richtlinien/details/vdibv-bs-6205-lifting-inserts-and-lifting-systems-for-precast-concrete-elements
- Posições ótimas de içamento de 2 a 6 pontos (tabela 4.2): dedução própria conferida em Python, 11/10/2026.