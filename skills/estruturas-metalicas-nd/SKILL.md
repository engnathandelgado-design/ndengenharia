---
name: "estruturas-metalicas-nd"
description: "Use ao conceber, pré-dimensionar ou detalhar coberturas, tesouras, terças, vigas de rolamento, barracões e mezaninos metálicos da ND (NBR 8800, NBR 14762, NBR 6123, manuais Gerdau) e a ferramenta nd_metalica."
---

# Estruturas metálicas ND — coberturas, barracões e mezaninos

Nathan (ND Engenharia, CREA-SC 168298-1) desenvolve com o Claude uma ferramenta própria de projeto de estruturas metálicas. Responder em português técnico. A ferramenta dá **pré-dimensionamento e memória**; a responsabilidade técnica é dele: sempre listar hipóteses que pedem decisão dele e marcar "(conferir)" valores normativos incertos. Convenções do software ND valem aqui (skill `projetos-estruturais-concreto-armado-protendido`, Parte D): kN, m, kPa; **N < 0 compressão**; JSON de entrada; dois motores (numpy próprio × OpenSeesPy, diferença ≈ 0). Detalhamento/pranchas: skill `detalhamento-metalico-nd`. MEF geral: `mef-opensees-opsvis`. Modelo 3D e material de divulgação: skill `modelagem-3d-reels-nd`.

## 1. Onde estão as coisas
- Google Drive do Nathan, pasta **"materiais gerdau"** (id `1WGIoUgoN-D3xHK0ngNmmHjruog6jvWA_`): 6 PDFs-fonte + subpasta **`ferramenta/`** com o código `nd_metalica` (arquivos .py, README, exemplos JSON, memória de exemplo). Baixar com `read_file_content`/`download_file_content`; PDFs > 10 MB não baixam pelo conector (pedir anexo ou versão dividida).
- Montar localmente: pasta `nd_metalica/` com `perfis.py, vento.py, verificacao.py, trelica.py, projeto.py, memoria.py, __main__.py, tests/` (+ `__init__.py`).
- `pip install --break-system-packages openseespy numpy matplotlib python-docx pytest`.
- Rodar: `python -m nd_metalica entrada.json [saida/]` → `memoria.md` + `memoria.docx` + 3 figuras + `resultado.json`. Testes: `python -m pytest nd_metalica/tests -q` (16 testes; repetir após qualquer alteração).

## 2. Fontes incorporadas (pasta "materiais gerdau")
| Fonte | O que dá | Uso |
|---|---|---|
| Gerdau, *Galpões em pórticos com perfis W* (set/2025; NBR 8800:2024, 6123:2023, 6120:2019) | ações, combinações, limites, tabelas de pré-dimensionamento de pórticos W (L 15–50, H 6/9/12, B 6/9/12, i = 10 %), curvas de consumo kg/m², exemplo de galpão completo | etapa 2 (pórticos W); referência de taxa |
| Gerdau, *Tabela de vãos e cargas* (6ª ed., NBR 8800:2024) | MRd, VRd, Lp de 105 perfis W/HP; TVPA-1 a 4 (vigas biapoiadas, mesa travada, valores ELU/1,5); TCPA (colunas, γa1 = 1,10) | mezaninos; conferência de vigas W |
| Gerdau, *Catálogo de perfis estruturais* | propriedades de 110 W/HP, A572 Gr50 (fy 345, fu 450 MPa) | `perfis.csv` (a incorporar no `perfis.py`) |
| Gerdau, *Ligações para estruturas de aço* (NBR 8800:2024 + AISC; só lidas pp. 1–78 de ~340) | parafusos A325, soldas E70XX, LCPP/LCSP/LCHE com exemplos | etapa de ligações |
| Figueroa & Dias, *Tipologias projetuais* (Gerdau 2012) | concepção qualitativa (14 casos), sem números | concepção |
| Projeto *Mercado Municipal de Arauá/SE* (DIP, jun/2025) | cobertura treliçada real em U dobrado | caso de validação |

O material da pasta é quase todo de **perfis W laminados**. NBR 14762, Cpe/Cpi, ligações de treliça (gusset/Whitmore) e clips de terça vieram do conhecimento próprio → marcados "(conferir)".

## 3. Ações e combinações (padrão da ferramenta)
- Permanentes (kPa): telha 0,06–0,12 (padrão 0,07); terças calculadas; contraventamento + correntes 0,05; tesoura iterada (começa 0,10 em projeção). Gerdau: terças + tirantes ≈ 0,05; contraventamentos 0,05. Painel fotovoltaico quando houver (ex.: 18 kgf/m² = 0,18 kPa).
- Sobrecarga de cobertura 0,25 kPa em projeção horizontal (NBR 8800 anexo B).
- Vento NBR 6123: Vk = V0·S1·S2·S3; q = 0,613·Vk² (N/m²); S2 = b·Fr·(z/10)^p (tab. 1 da edição 1988, z ≥ 5 m; conferir 2023 — Gerdau usou S2 = 0,83 cat. III classe B). Classe A ≤ 20 m, B 20–50 m, C > 50 m.
- Cpe médios de telhado duas águas h/b ≤ 1/2 (θ: α=90° EF/GH; α=0° EG/FH): 0° −0,8/−0,4, −0,8/−0,4; 5° −0,9/−0,4, −0,8/−0,4; 10° −1,2/−0,4, −0,8/−0,6; 15° −1,0/−0,4, −0,8/−0,6; 20° −0,4/−0,4, −0,7/−0,6; 30° 0/−0,4, −0,7/−0,6; 45° +0,3/−0,5, −0,7/−0,6 (conferir). Cpi: fechado +0,2/−0,3; abertura dominante a barlavento até +0,8 (conferir razão de áreas). Casos: W1 (90°, Cpi máx), W2 (0°, Cpi máx), W1i (90°, Cpi mín), W3 pressão se Cpe,máx − Cpi,mín > 0.
- ELU (NBR 8800 tab. 1–2): γg aço 1,25, elementos industrializados 1,35, favorável 1,00; γq 1,5; γw 1,4; ψ0 SC 0,5, vento 0,6. Combinações: 1,25Gm+1,35Gc+1,5SC; **1,0G+1,4W (sucção — costuma governar)**; G+1,4W+0,75SC; G+1,5SC+0,84W.
- ELS: tesoura/treliça de cobertura L/250; terça L/180; deslocamento de pilar H/300 (Gerdau); viga de piso L/350 (tabela de vãos); viga de rolamento L/600 (conferir com o fabricante da ponte).

## 4. Perfis formados a frio (perfis.py)
- Propriedades pela **linha média com cantos arredondados, raio interno = t** (padrão de dobra). Isso reproduz o catálogo: U100x50x6,3 = 8,86 kg/m; U100x50x3,8 = 5,59; U75x40x2 = 2,33; Ue200x75x20x2,25 = 6,63 (lista Arauá ±0,5 %). Cantos vivos superestimam ~4 %.
- Centro de torção e Cw por coordenada setorial integrada nos segmentos (validado contra e = 3b²/(6b+h) e Cw = t·b³h²(3b+2h)/[12(6b+h)]).
- Famílias: U, Ue, L dobrada, L laminada (cantos vivos: L 3"x3/16" = 5,52 kg/m, rz 1,50 cm), 2U em I (costas com costas), 2U em caixa (Bredt), barra redonda. Espessuras comerciais 1,55–6,3 mm; espessura mínima padrão 2,0 mm.
- Eixos: alma vertical; x horizontal = eixo de simetria do U (flexão forte, acopla com torção); y = eixo fraco.

## 5. Verificações (verificacao.py)
- **Tração (NBR 14762 9.6):** min(A·fy/1,10; Ct·An·fu/1,65), Ct = 0,85 padrão para ligação soldada em parte dos elementos (conferir tab. 23); λ ≤ 300.
- **Compressão (9.7):** Nc,Rd = χ·Aef·fy/1,20; λ0 = √(A·fy/Ne); χ = 0,658^λ0² (λ0 ≤ 1,5) ou 0,877/λ0². Ne = min(Ney, Nexz) para monossimétrica, Nexz = (Nex+Nez)/[2(1−(x0/r0)²)]·{1 − √[1 − 4NexNez(1−(x0/r0)²)/(Nex+Nez)²]}, Nez = (π²ECw/(KzLz)² + GJ)/r0². Aef por largura efetiva (9.2.2: λp = (b/t)/[0,95√(kE/σ)], bef = b(1−0,22/λp)/λp se λp > 0,673; k = 4 AA, 0,43 AL; aba de Ue AA se D/b ≥ 0,2). λ ≤ 200. **Distorcional não verificada (conferir 9.7.3).**
- **Flexão de terça (9.8):** Me = Cb·r0·√(Ney·Nez); χFLT = 1 (λ0 ≤ 0,6), 1,11(1−0,278λ0²) (< 1,336), 1/λ0²; MRd = χFLT·Wc,ef·fy/1,10 (Wef por largura efetiva, alma k = 24). Lb = vão/(linhas de corrente + 1); sucção comprime a mesa livre. Flexão oblíqua Mx/MxRd + My/MyRd ≤ 1. Cortante kv = 5.
- **Tirante redondo (NBR 8800):** min(Ag·fy/1,10; 0,75·Ag·fu/1,35).
- Laminados W (NBR 8800 5.3/5.4): fórmulas da tabela Gerdau — TVPA reproduzida por `min(K·(MRd − pp·L²/8)/L, Vlim)`; TCPA com γa1 = 1,10. Ainda não no código.

## 6. Tesoura treliçada (trelica.py + projeto.py)
- Geração: Pratt (diagonais tracionadas sob gravidade), Howe, Warren com montantes; trapezoidal (h no apoio) ou triangular (h = 0); banzo inferior reto ou paralelo; apoios intermediários (`apoios_intermediarios`). Padrões: altura no meio ≈ L/11 (h apoio ≥ 0,5 m); painel ≤ 1,8 m (terças nos nós = vão da telha).
- **Diagonais: UM SÓ SENTIDO EM CADA ÁGUA, espelhadas apenas na cumeeira** (regra do Nathan — nunca inverter o sentido no meio da água). Em galpão de duas águas com pilar na cumeeira, a tesoura é contínua sobre ele (com fechamento completo, apoiada sem folga transversal nos 3 pilares para travá-los contra o vento). Escolher entre 'desce' (diagonais descem do beiral para a cumeeira) e 'sobe' resolvendo a treliça contínua com gravidade e sucção (`nd3d.verifica.sentido_diagonais()`): as diagonais longas, junto à cumeeira, devem ficar tracionadas no caso que governa. Caso galpão com pontes de 20 t (2 × 25,39 m, B 8,33 m, i 5 %, V0 45, fotovoltaico, sucção governa): 'desce' → +190 kN nas longas e compressão máx. −154 kN em diagonal curta de 2,4 m (2L 3"); 'sobe' → −194 kN em diagonal de 3,25 m. Pratt/Howe só fazem sentido para meia-água isolada.
- Concepção (Tipologias Gerdau): terças apoiadas nos nós; diagonais longas trabalhando à tração; mãos francesas travando o banzo inferior; X de tirantes no plano das terças; junta de dilatação em coberturas longas. Relações L/h reais: 9,6 a 12,5 (6,1 em cobertura especial).
- Comprimentos de flambagem: banzo superior L/L (terças + contraventamento); banzo inferior L no plano e n·L fora (mãos francesas a cada `travamento_banzo_inf_paineis`, padrão 2 — com sucção governando, usar mãos francesas em todos os nós); alma L. Banzo U com **alma no plano do telhado** (abas para dentro): no plano da tesoura eixo fraco, fora do plano eixo forte + flexo-torção (`orientacao_banzos: alma_horizontal`; `conservadora` = eixo fraco com o maior comprimento).
- Escolha: banzos com perfil único; alma com até 2 perfis (par que minimiza a massa); se a família não atende, tenta catálogo misto com 2U (aviso: chapas espaçadoras, NBR 14762 9.7.5). Peso próprio iterado até 2 %; acréscimo de ligações 5 %.
- Travamentos (pré-dimensionamento): contraventamento X de barra redonda em max(2, ⌈C/30⌉+1) vãos, força no oitão ≈ 1,3·q·L·h/2 (Cf conferir); correntes Ø10; mãos francesas L 50x3.
- Reações por tesoura em todas as combinações → V < 0 = arrancamento (chumbador/ligação no pilar).

## 6b. Ligações e detalhamento (padrão ND para apresentação e projeto)
- Ligações de campo **100 % parafusadas** (A325, um diâmetro padrão por obra, ex.: Ø19 na tesoura, Ø16 em terças/mãos francesas); soldas só de fábrica, de filete. Bisel/chanfro só se houver solda de penetração total (evitar no projeto). Arruela biselada nos tirantes inclinados.
- Nó de tesoura: chapa de nó 12,5 mm (= afastamento das cantoneiras) soldada na mesa do banzo (filete 6 mm dos dois lados), dupla cantoneira com 2 parafusos em corte duplo por extremidade; borda ≥ 40 mm, espaçamento ≥ 3d (65 mm para Ø19); furo padrão d + 1,5 mm.
- Apoio da tesoura em pilar pré-moldado: placa sobre inserto + chumbadores dimensionados ao **arrancamento** (ex.: 133 kN/apoio → 4 Ø19). Se a tesoura trava os pilares na transversal (fechamento completo), apoios sem furo oblongo nessa direção; furo oblongo só quando a estabilidade lateral não depende dela.
- Tesoura > 13 m: emendas de campo parafusadas fora do nó (talas nas mesas e na alma), segmentos ≤ ~12,7 m para transporte (+ peça de cumeeira sobre o pilar central).
- Terça W: clipe L 4"×3/8" soldado no banzo + 2 parafusos na alma; linhas de corrente Ø12 nos terços.
- Viga de rolamento W + U na mesa superior: biapoiada com junta sobre o apoio, enrijecedores de apoio, placa sobre consolo com chumbadores em furo oblongo (alinhamento), chapa de travamento lateral da mesa superior ao pilar, grampos do trilho a cada ~600 mm, batentes. Carga de roda e trilho: confirmar com o fabricante da ponte.
- Pré-dimensionamento do galpão com pontes de 20 t (referência, conferir): banzos W 150×22,5; diagonais 2L 3"×1/4" no primeiro painel do beiral e junto à cumeeira, 2L 2½"×1/4" nas intermediárias; montantes 2L 2½"×1/4"; terças W 200×15,0 (vão 8,33 m); viga de rolamento W 610×140 + U 310; taxa da cobertura ≈ 17 kg/m²; pilares pré-moldados revisados para 40×80 com o fechamento completo.

## 7. Validação (rodada em 06/10/2026 — 16/16 PASS)
| Teste | Resultado | Referência |
|---|---|---|
| M1 massas de 6 perfis dobrados | ±0,5 % | lista de materiais Arauá |
| M2 L 3"x3/16" laminada | 5,52 kg/m; rz 1,51 cm | 5,519; 1,50 |
| M3 U cantos vivos: x0, Cw, Ix | exatos (1e-9) | fórmulas fechadas |
| T1 Pratt 12 m/6 painéis/h 1,5, P = 10 kN | banzo meio −60,0; diagonal 41,67 | M/h; método dos nós |
| T2 numpy × OpenSeesPy (Howe inclinada, EA variável) | < 1e-8 kN | idênticos |
| T3 flecha banzos paralelos L 24, h 2 | ±3 % | viga equivalente I = A·h²/2 |
| C1–C3 curva χ, flexo-torção, largura efetiva | ok | NBR 14762 |
| W1 S2 cat. II A 10 m; q | 1,00; 0,613Vk² | NBR 6123 |
| P1 galpão 20×40, B 5, V0 45, fechado | 11,4 kg/m², tudo ≤ 1 | faixa usual 8–25 |

**Caso Arauá/SE** (43,94 × 64,30 m, B ≈ 5 m, 32 painéis, V0 30; altura e cargas ARBITRADAS porque as pranchas não foram vistas): ferramenta 37,5 t / 13,3 kg/m² × projeto 40,8 t / 14,4 kg/m². Mas a ferramenta pede banzos U200x75x6,3 contra U100x50x6,3 do projeto e terça Ue100 contra Ue200 → indica que no Arauá a tesoura tem **apoios intermediários** (treliças longitudinais tipo 02–04 / pilares) ou é bem mais alta. Fechar a validação com as pranchas (altura, apoios, vento).

## 8. Roteiro de uso
1. Coletar: vão, comprimento, espaçamento, pé-direito, inclinação/telha (vão máx. da telha), fechamento (fechado/aberto), V0 (isopleta), categoria do terreno, S3, apoios intermediários, aço disponível, perfis preferidos do cliente/fábrica, ponte rolante (capacidade, carga de roda, trilho).
2. Montar o JSON só com o que muda do padrão; rodar; ler os avisos.
3. Conferir ordem de grandeza: banzo ≈ M/h com M = qL²/8; taxa kg/m² (cobertura treliçada leve 8–18; pórtico W 18–44 pelas curvas Gerdau, sem fechamento lateral, + 6–12 de fechamento).
4. Conferir a orientação das diagonais pelo caso que governa (seção 6), as ligações (seção 6b) e o deslocamento lateral dos pilares quando houver fechamento completo.
5. Ajustar concepção (altura, painéis, travamento do banzo inferior, apoios) e rodar de novo; fixar perfis comerciais com `perfis.fixos` para verificar a escolha final.
6. Entregar memória (Word/MD + figuras) e quantitativo; listar "(conferir)" e limitações.

## 9. Armadilhas
- Em galpão fechado com V0 ≥ 40 a **sucção governa**: banzo inferior comprime → travamento fora do plano (mãos francesas) decide o perfil; tirantes redondos não servem onde inverte o esforço; diagonais longas devem ficar tracionadas na sucção, sempre num só sentido por água.
- U simples comprimido sofre flexo-torção: Nexz ≪ Nex; não verificar só por λ.
- Peso de catálogo de dobrado já desconta cantos (r = t); calcular com cantos vivos superestima.
- Tabela de vãos Gerdau: valores ELU/1,5 (comparar com serviço), peso próprio já descontado, L/350 só indicado por Llim — não serve para terça (ignora flexão oblíqua e sucção).
- Manual de galpões: erros de digitação (W460×740, W610×153) e reações do Ex.1 diferentes da tabela revisada — conferir.
- Diagonal extrema de dupla cantoneira 2½" não atende compressão de ~180–230 kN com 2,4 m — usar 3" ou mais.
- Pilar pré-moldado em balanço + fechamento lateral completo: o deslocamento de topo costuma governar a seção (caso 17,5 m: 40×60 → 63 mm freq.; 40×80 → 33 mm). Apoios da tesoura sem furo oblongo na transversal para os pilares trabalharem juntos; contraventamento vertical nas fachadas para o vento nos oitões e a frenagem das pontes.
- Terças de fechamento vencendo o vão entre pilares (~8,3 m) com vento de parede: W 150×18,0 a cada ~1,6 m com a alma horizontal (eixo forte contra o vento) e linhas de corrente; fixação por inserto no pilar + suporte parafusado com furo oblongo (conferir).

## 10. Backlog (próximas etapas combinadas com o Nathan)
- Coberturas: distorcional (NBR 14762 9.7.3/9.8.2.3), coeficientes locais de vento, terça contínua, ligações de nó (gusset, solda, Whitmore, bloco de cisalhamento), apoio tesoura–pilar e chumbadores, NBR 6123:2023, tubos/cantoneiras duplas, pilares metálicos.
- Etapa 2 — **barracões em pórtico W**: módulo `porticos_w` com OpenSees (barras + P-Δ), FLT/FLM/FLA da NBR 8800, tabelas e exemplos Gerdau como validação (Ex.3 GMQ6/30/9/6 = 25,6 kg/m² estrutura principal).
- Etapa 3 — **mezaninos**: vigas W pela TVPA (fórmula reproduzida), steel deck/laje, pilares pela TCPA, vibração de piso.
- Integrar `perfis.csv` (110 W/HP) e a calculadora comercial ND Metálica (taxa kg/m² para clientes) ao mesmo motor.
- Integrar `nd3d.verifica` (escolha de diagonais, ligações) e `nd3d.analise_portico` (deslocamentos) ao `nd_metalica`.
- Ler o manual de ligações completo (pp. 79–340: bases PBR/PBE, chumbadores, ligações rígidas) quando houver versão < 10 MB.