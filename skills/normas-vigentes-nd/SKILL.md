---
name: "normas-vigentes-nd"
description: "Use em toda resposta técnica da ND que cite norma, valor normativo ou verificação (concreto, pré-moldado, fundação, aço, incêndio): edição vigente, protocolo de citação de item, marcação verificado/conferir e tabelas finais ERRO/ALERTA."
---

# Normas vigentes e protocolo de verificação — ND Engenharia

Skill transversal. Vale junto com qualquer skill técnica da ND. Objetivo: nenhum número sai sem item da norma, nenhum valor de edição antiga é usado sem aviso, e toda verificação termina numa tabela OK / ERRO / ALERTA.

## 1. Edições de referência

Regra: usar a edição desta tabela. Se uma skill citar edição anterior, tratar como **histórico** (para entender projeto antigo ou laudo de obra existente), nunca como base de cálculo nova.

| Norma | Assunto | Edição a usar | Situação |
|---|---|---|---|
| NBR 6118 | Projeto de estruturas de concreto | 2023 | confirmada |
| NBR 9062 | Projeto e execução de pré-moldado | 2017 | confirmada (fontes ABCIC/dissertações) |
| NBR 14861 | Lajes alveolares protendidas | 2022 (mar/2022) | confirmada (catálogo Target) |
| NBR 16475 | Painéis de parede de concreto pré-moldado | 2017 | conferir no catálogo |
| NBR 16055 | Parede de concreto moldada no local | 2022 + Emenda 1:2026 (mai/2026) | confirmada; ler a emenda; 2012 é histórico |
| NBR 6120 | Ações para o cálculo de estruturas | 2019 | 1980 é histórico |
| NBR 6123 | Forças devidas ao vento | 2023 | confirmada (implementada no CYPE, out/2026); 1988 é histórico — programas que ainda usam 1988 (ex.: HyperFrame v0.2.50) precisam de aviso |
| NBR 8681 | Ações e segurança nas estruturas | 2003 | conferir no catálogo |
| NBR 6122 | Projeto e execução de fundações | 2019 (ou posterior) | 2010 é histórico; conferir se há emenda/revisão 2022 |
| NBR 15421 | Projeto sismo-resistente | conferir edição | raramente governa no Sul |
| NBR 15200 | Concreto em situação de incêndio | 2024 (jun/2024) | confirmada; 2012 é histórico; ver verificacao-incendio-nbr15200 |
| NBR 14432 | Exigências de resistência ao fogo (TRRF) | 2001 | conferir |
| NBR 8800 | Estruturas de aço e mistas | 2024 | 2008 é histórico; conferir texto final |
| NBR 14762 | Perfis formados a frio | 2010 | conferir |
| NBR 12655 | Concreto — preparo, controle, recebimento | conferir edição | |
| NBR 14931 | Execução de estruturas de concreto | 2023 | conferir |
| NBR 7480 / 7483 | Barras / cordoalhas | conferir edição | |
| NBR 11682 | Estabilidade de encostas (muros) | 2009 | confirmada; revisão em andamento |
| NBR 16747 | Inspeção predial | 2020 | confirmada |
| NBR 13752 | Perícias de engenharia | 2024 | confirmada; 1996 é histórico |
| NBR 15575 | Desempenho | 2013 + Emenda 1 (mar/2021) | confirmada |

Quando "conferir": antes de usar em memória com ART, olhar o catálogo ABNT (abntcatalogo.com.br) e atualizar esta tabela.

## 2. Protocolo de citação (obrigatório)

1. Todo valor normativo leva **norma + edição + item ou tabela**: "ρmín = 0,15 % (NBR 6118:2023, 17.3.5.2.1, tab. 17.3)".
2. Marcadores de confiança:
   - `[verificado: PDF NBR xxxx:aaaa, item]` — conferido no texto da norma.
   - `[verificado: fonte secundária]` — conferido em apostila, tese ou livro que transcreve o item; citar a fonte.
   - `(conferir no PDF, item X)` — de memória. Pode orientar estudo e pré-dimensionamento, **não** pode ir para memória de cálculo assinada sem conferência.
3. Não inventar número de item. Se não souber: "(conferir no PDF, item a localizar)".
4. Não guardar fórmula não confirmada. Melhor "verificar no item X" do que fórmula errada.
5. Quando o Nathan mandar o PDF de uma norma, trocar os marcadores das tabelas das skills para `[verificado: PDF ...]` e registrar a página.
6. Fato x hipótese: em laudo e revisão, separar o observado do inferido.

## 3. Precedência entre skills

- Tanques e reservatórios: `tanques-reservatorios-concreto` prevalece sobre a parte de tanques de `projetos-estruturais-concreto-armado-protendido`.
- Cálculo numérico de peça de concreto armado: `dimensionamento-concreto-armado-nbr` (calculadora). A parte conceitual fica em `projetos-estruturais-concreto-armado-protendido`.
- Paredes moldadas in loco e pilar-parede: `paredes-concreto-nbr16055`. Painel pré-moldado de fechamento: `paineis-fechamento-pre-moldados`.
- Içamento, transporte, estocagem, montagem: `icamento-transporte-montagem`.
- Lajes alveolares: `lajes-alveolares-nbr14861`.
- Incêndio: `verificacao-incendio-nbr15200`.
- Contenções: `muros-contencao`. Fundações com ISE: `interacao-solo-estrutura`.
- Conferir resultado de software (nosso, HyperFrame, TQS, Eberick, CYPE): `validacao-cruzada-estrutural`.
- Laudos: `laudos-vistoria-nd`. Proposta comercial nunca antecipa diagnóstico.

## 4. Tabelas finais de verificação por elemento

Toda verificação termina com tabela: **Verificação | Condição de falha | Ação**. Ação = `ERRO: ... (item)` ou `ALERTA: ...` ou `OK`.

Status dos valores abaixo: transcritos de memória técnica com o item indicado — `(conferir no PDF)` uma vez e trocar o status. São os itens mais usados da NBR 6118:2023.

### 4.1 Cobrimento nominal (6118, tab. 7.2, Δc = 10 mm)
| CAA | Laje | Viga/pilar | Elemento em contato com solo |
|---|---|---|---|
| I | 20 mm | 25 mm | 30 mm |
| II | 25 mm | 30 mm | 30 mm |
| III | 35 mm | 40 mm | 40 mm |
| IV | 45 mm | 50 mm | 50 mm |
Pré-moldado com controle rigoroso: redução de Δc para 5 mm (6118, 7.4.7.4) — `(conferir no PDF)`; justificar controle no projeto.

### 4.2 Viga
| Verificação | Condição de falha | Ação |
|---|---|---|
| Largura mínima | bw < 12 cm | ERRO: bw mínimo 12 cm (13.2.2), 10 cm só nos casos excepcionais do item |
| Ductilidade | x/d > 0,45 (fck ≤ 50) | ERRO: aumentar seção ou armadura dupla (14.6.4.3) |
| As mínima | ρ < ρmín (≥ 0,15 %) | ERRO: armadura mínima (17.3.5.2.1) |
| As máxima | As + As' > 4 % Ac | ERRO: armadura máxima (17.3.5.2.4) |
| Armadura de pele | h > 60 cm sem 0,10 % Ac,alma por face | ERRO: armadura de pele (17.3.5.2.3) |
| Estribo mínimo | ρsw < 0,2·fctm/fywk | ERRO: estribo mínimo (17.4.1.1.1) |
| Espaçamento estribo | s > 0,6d e 300 mm (Vd ≤ 0,67 VRd2) ou s > 0,3d e 200 mm | ERRO: espaçamento máximo (18.3.3.2) |
| Biela | VSd > VRd2 | ERRO: aumentar seção (17.4.2) |
| Flecha | a > l/250 | ERRO: aceitabilidade sensorial (13.3) |
| Fissura | wk acima do limite da CAA (0,4 / 0,3 / 0,2 mm) | ERRO: abertura de fissura (13.4, tab. 13.4) |

### 4.3 Pilar
| Verificação | Condição de falha | Ação |
|---|---|---|
| Dimensão mínima | b < 19 cm (14 cm só com γn) | ERRO: 13.2.3 |
| Área mínima | Ac < 360 cm² | ERRO: 13.2.3 |
| Esbeltez | λ > 200 | ERRO: não permitido (15.8.1) |
| Esbeltez | 90 < λ ≤ 140 / > 140 | ALERTA: fluência obrigatória / método geral (15.8) |
| As mínima | As < 0,15·Nd/fyd e < 0,4 % Ac | ERRO: 17.3.5.3.1 |
| As máxima | As > 8 % Ac incluindo emenda | ERRO: 17.3.5.3.2 |
| Bitola longitudinal | φ < 10 mm ou φ > b/8 | ERRO: 18.4.2.1 |
| Espaçamento longitudinal | s > 2b e > 40 cm | ERRO: 18.4.2.2 |
| Estribo | φt < 5 mm ou < φ/4 | ERRO: 18.4.3 |
| Espaçamento estribo | s > 20 cm, > menor dimensão, > 12φ (CA-50) | ERRO: 18.4.3 |
| Flexão oblíqua com bloco retangular | 0,85·fcd usado quando a largura da zona comprimida diminui para a borda (canto comprimido) | ALERTA: usar 0,9·αc·fcd ou parábola-retângulo por fibras (17.2.2 e, conferir no PDF); no HyperFrame v0.2.50 isso deu 3,5 % contra a segurança |
| Momento mínimo | M1d,mín = Nd(0,015 + 0,03h) não aplicado nas DUAS direções | ERRO: 11.3.3.4.3 |

### 4.4 Laje maciça
| Verificação | Condição de falha | Ação |
|---|---|---|
| Espessura | < 7 cm cobertura / 8 cm piso / 10 cm balanço / 10 cm veículo ≤ 30 kN / 12 cm > 30 kN / 16 cm lisa / 14 cm cogumelo | ERRO: 13.2.4.1 |
| Armadura mínima | abaixo da tab. 19.1 (positiva 2 direções ≥ 0,67ρmín) | ERRO: 19.3.3.2 |
| Secundária | < 20 % da principal ou < 0,9 cm²/m | ERRO: tab. 19.1 |
| Espaçamento principal | s > 2h e > 20 cm | ERRO: 20.1 |
| Punção | τSd > τRd | ERRO: 19.5 |
| Carga concentrada em área pequena | reservatório ou escada espalhados na laje inteira | ALERTA: média serve para o pórtico; momento local, punção e flecha pedem a carga no lugar real |

### 4.5 Pilar-parede e parede
| Verificação | Condição de falha | Ação |
|---|---|---|
| Classificação | maior dimensão > 5× menor | ALERTA: é pilar-parede (14.4.2.4); verificar 15.9 e 18.5 |
| Armadura transversal | < 25 % da longitudinal da maior face | ERRO: 18.5 |
| Parede moldada in loco | qualquer item | ver tabela da skill paredes-concreto-nbr16055 |

### 4.6 Consolo e dente (NBR 9062)
| Verificação | Condição de falha | Ação |
|---|---|---|
| Classificação | a/d > 1,0 | ALERTA: tratar como viga em balanço, não como consolo |
| Classificação | a/d ≤ 0,5 | ALERTA: consolo muito curto — modelo de atrito-cisalhamento |
| Carga horizontal | Hd não considerada | ERRO: considerar Hd mínima do item (conferir no PDF) |
| Tirante | ancoragem do tirante fora da zona de apoio | ERRO: ancorar na extremidade (alça ou barra soldada) |

### 4.7 Estabilidade global e pórtico (6118 cap. 15, 6123, 8681)
| Verificação | Condição de falha | Ação |
|---|---|---|
| Limite do parâmetro α | α1 = 0,6 usado com contraventamento só por pórticos | ERRO: só pórticos → α1 = 0,5; pórticos + pilares-parede → 0,6; só pilares-parede → 0,7; n ≤ 3 → 0,2 + 0,1n (15.5.2, conferir no PDF) |
| γz | γz > 1,30 | ERRO: não usar 0,95·γz; enrijecer ou análise de 2ª ordem (15.7.2) |
| γz | 1,10 < γz ≤ 1,30 sem majorar esforços horizontais | ERRO: majorar por 0,95·γz (15.7.2) |
| Rigidez para γz | EI integral no ELU | ERRO: vigas 0,4·Ec·Ic, pilares 0,8·Ec·Ic (15.7.3) |
| Edição do vento | NBR 6123:1988 | ALERTA: vigente é 2023; refazer S2/Ca ou justificar |
| Desaprumo | não comparado com o vento | ERRO: comparar momentos de tombamento; 30 % do vento ≥ desaprumo → só vento (11.3.3.4.1, conferir) |
| Torção do vento | sem excentricidade em planta | ALERTA: considerar excentricidade da força de arrasto (6123, conferir item na 2023) |
| Mesa colaborante na rigidez lateral | inércia T nas vigas sob vento | ALERTA: reduz o deslocamento (23 % no exemplo HyperFrame); declarar a hipótese ou comparar com seção retangular |
| Trechos rígidos | ausentes | ALERTA: conservador (mais flexível); declarar a hipótese (14.6.2.1, conferir) |
| Deslocamento lateral | topo > H/1700 ou entre pisos > h/850 (combinação frequente do vento) | ERRO: tab. 13.3 |

### 4.8 Fundações (6122, 6118 cap. 22)
| Verificação | Condição de falha | Ação |
|---|---|---|
| Combinações | sapata ou bloco dimensionado só com G + Q | ERRO: incluir combinações com vento (G + Q + 0,6W e G + 0,5Q + W em serviço; ELU para armadura). No exemplo do HyperFrame as sapatas de canto foram de 260 para 371 kPa |
| Tensão de borda | σmáx > 1,3·σadm com vento, ou σmáx > σadm sem vento | ERRO: aumentar a sapata (6122, conferir item do acréscimo de 30 %) |
| Excentricidade | resultante fora do núcleo central | ALERTA: área comprimida parcial; verificar tombamento |
| Bloco: distribuição | momentos do pilar ignorados na carga das estacas | ERRO: Ri = N/n ± Mx·yi/Σy² ± My·xi/Σx² |
| Bloco 6+ estacas (CEB-70) | cortante na seção S2 comparada só com VRd2 de viga com estribo | ERRO: usar o limite do CEB-70 para bloco sem estribo (apud Bastos/UNESP) — VRd2 fica ~5× mais folgado |
| Bloco: bielas (Blévot) | σ > 1,4 / 1,75 / 2,1·KR·fcd (2 / 3 / 4 estacas) | ERRO: aumentar h, pilar ou estacas |
| Carga de entrada | envoltória de projeto (já de cálculo) multiplicada de novo por 1,4 | ERRO: confirmar se a carga é característica ou de cálculo antes de majorar |

## 5. Como fechar uma resposta técnica

1. Edição usada de cada norma (tabela 1).
2. Hipótese → equação → número → verificação → decisão, com item.
3. Tabela ERRO/ALERTA.
4. Lista do que ficou `(conferir no PDF)`.
5. Lembrete: a ART é do Nathan; o que está como "conferir" precisa de conferência antes de assinar.