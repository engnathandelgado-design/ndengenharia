---
name: "tanques-reservatorios-concreto"
description: "Use ao projetar, verificar, revisar memoriais ou ensinar tanques e reservatórios de concreto armado — cilíndricos e retangulares, incluindo estações elevatórias de esgoto (EEE): ações, flutuação/subpressão, parede em casca ou placa, laje de fundo, junta parede-laje, durabilidade e estanqueidade."
---

# Tanques e reservatórios de concreto armado (cilíndricos e retangulares/EEE)

Integração com as skills da casa:
- `projetos-estruturais-concreto-armado-protendido` — dimensionamento ELU/ELS (seções 15–16), MEF (Parte C), resumo teórico desta skill na **seção 25**, convenções do software na Parte D (módulo `reservatorios`).
- `mef-opensees-opsvis` — código validado `tanques_nd.py` na **seção 13** (parede como viga sobre base elástica, laje circular em casca, testes T11–T17). Gravar o arquivo de lá antes de calcular.
- `interacao-solo-estrutura` — laje de fundo apoiada no solo (tanque cheio), molas e recalques.

Postura: português técnico, item de norma citado, toda conta em Python conferida por caminho independente (solução fechada × OpenSees). A responsabilidade técnica (ART) é do Nathan: sinalizar hipóteses que pedem decisão dele (NA de projeto, parâmetros do solo, tipo de ligação parede-fundo, critério de estanqueidade). Valores com (conferir) devem ser checados na norma vigente.

## 1. Fonte
- Koneski, G. F. *Dimensionamento da laje de fundo de tanque enterrado em concreto armado com formato cilíndrico com ênfase na verificação de estabilidade contra flutuação*. TCC, Engenharia Civil, UDESC/CCT (Joinville), 2013. Orientadora: Sandra Denise Krüger Alves. Base: NBR 6118:2003, EC7 (2004), Rocha (1985), Guerrin (2003), Vasconcelos (1998), Cruz (2009), Ramos (2010), Godoy (1972), BS 8007.
- Lida integralmente (pdf.js, 100 p.). As Tabelas 5 (coeficientes K1–K3, C1–C2 de Rocha) e 6–8 (coeficientes do EC7) são imagens e não foram extraídas: os coeficientes de Rocha foram substituídos pela solução fechada de Timoshenko (idêntica, ver 4.2) e os do EC7 vêm do conhecimento próprio (conferir).
- Segunda fonte (seções 11–12): memorial estrutural da EEE Presidente Vargas (Fortaleza, 2020) — caixa retangular por tabelas de Bares, revisado pela ND.
- Nível: graduação; útil como roteiro e, principalmente, como **estudo de caso de patologia** (tanque que flutuou). A revisão da ND (seção 8) encontrou erros que mudam a conclusão — ensinar com eles.

## 2. Tipologia e concepção
- Implantação: apoiado (terreno com capacidade), semi-enterrado (topografia, paisagem, custo de escavação), enterrado (proteção térmica, sem impacto visual; contra: escavação cara, inspeção difícil, **subpressão**), elevado (pressão mínima na rede).
- Forma: a circular é a mais econômica (parede trabalha em tração anelar de membrana). Até 25–30 m de diâmetro a parede engastada no fundo pode ter espessura constante ou variável; acima disso as deformações pesam e se recorre a cúpulas/abóbadas (Guerrin).
- Concreto armado é usual até ~1 500 m³; acima disso a protensão circunferencial costuma ser mais econômica e controla a fissuração (Cruz 2009). O caso do TCC tem 2 000 m³ em CA.
- Fundo de grandes dimensões: laje maciça espessa (simples, muito concreto), fundo nervurado ou laje fina sobre reticulado de vigas ortogonais; com subpressão alta, ancoragem por estacas/tirantes de tração.
- Ligação parede-fundo (Cruz & Cruz 1996; BS 8007):
  - monolítica: deslocamento radial e rotação iguais na parede e na laje;
  - rótula fixa: radial contínuo, rotação livre;
  - deslizante: os dois livres — parede em membrana pura. Executar e manter essa junta é difícil; considerar a parede livre no cálculo do anel é a favor da segurança para Nθ, mas o engaste real gera momento vertical na base que precisa de armadura.
- Tampa: o esforço radial no topo sob empuxo de água é quase nulo → calcular a parede desligada da tampa (Rocha).

## 3. Ações
- Peso próprio 25 kN/m³; revestimento/impermeabilização ≈ 1,0 kN/m²; sobrecarga na tampa ≥ 0,5 kN/m² (Araújo 2003).
- Líquido: p = γ·z (triangular na parede, uniforme γ·h no fundo). Lodo de ETA ≈ água (ρL = ρag·(1 − Cs/ρs) + Cs; no caso, 70 % água / 30 % lodo → adotado γ = 10 kN/m³). Efluentes mais densos: usar γ real.
- Empuxo de terra na parede: **repouso**, não ativo — a parede de concreto é rígida e não mobiliza o estado ativo (EC7 9.5.2: deslocamento < 5·10⁻⁴·h). K0 = 1 − sen φ' (NC); σh = K0·σ'v + u abaixo do NA. Adotar o ativo subdimensiona.
- Subpressão na face inferior da laje: p = γw·hw (hw = NA até a face inferior). Considerar o **NA máximo** (chuvas, cheias, rio próximo); sem série histórica, NA no terreno (o TCC fez isso: NA medido a 3,2 m, adotado na cota do terreno).
- Rebaixamento do NA (obra): aumenta a tensão efetiva → recalque de vizinhos, grave em argila mole/turfa; desligar o rebaixamento antes do reaterro e do peso final faz o tanque flutuar.
- Outras (fora do TCC, considerar em projeto): temperatura e gradiente na parede (gera Mθ), retração restringida pela laje, fluência (fundo), sismo/hidrodinâmica (Housner), vento em reservatório elevado, cargas de passarelas e casa de bombas.
- Correlações de solo sem ensaio (Godoy 1972 — usar só em anteprojeto): γ de argilas por N do SPT ≤ 2: 13; 3–5: 15; 6–10: 17; 11–19: 19; ≥ 20: 21 kN/m³; areias φ ≈ 28° + 0,4·N. Classificação por NBR 7250 (substituída — usar NBR 6484/NBR 6502, conferir).

## 4. Parede cilíndrica
### 4.1 Membrana (r ≥ 20t)
- Nθ = p·a = γ·a·(d − x) (tração anelar, x a partir do fundo, d = lâmina d'água); Ny = −(G + g·y) (compressão vertical: peso próprio + tampa).
- Sem vínculo no fundo: Nθ,máx = γ·a·d na base.
### 4.2 Perturbação de borda (Rocha 1985 = Timoshenko)
- β⁴ = 3(1 − ν²)/(a²t²); L = 1/β ≈ 0,76·√(a·t). O efeito do fundo amortece em ≈ πL.
- Engaste perfeito (casca longa, βH ≥ 3):
  - momento no engaste M0 = γ·L²·(d − L)/2 — traciona a face **interna** (armadura vertical interna na base);
  - força radial Q0 = γ·L·(2d − L)/2;
  - momento negativo no vão (face externa) bem menor; Nθ reduzido perto da base e máximo um pouco acima.
- Rótula: M = 0 na base, momento de vão maior que no engaste.
- Mθ = ν·Mx (+ gradiente térmico ou carga não axissimétrica).
- Parede curta (βH < 3), espessura variável, empuxo de solo externo ou base elástica real → `parede_ops` (OpenSees): faixa meridional de 1 m como viga sobre base elástica, EI = D = E·t³/12(1 − ν²), molas radiais k = E·t/a² (é a rigidez do anel — analogia exata da casca axissimétrica).
- Armadura (Rocha): M0 → vertical interna; M de vão → vertical externa; Nθ,máx → anéis nas duas faces.
- Tanque enterrado vazio: solo + água externos comprimem o anel e invertem os momentos → verificar as duas faces e as duas situações (vazio com aterro; cheio sem aterro = teste de estanqueidade).

## 5. Laje de fundo circular
### 5.1 Placa de Kirchhoff (carga uniforme q; ν = 0,2; a = raio; l = 2a)
- Engastada no contorno:
  - Mr = q/16·[a²(1 + ν) − r²(3 + ν)]; Mt = q/16·[a²(1 + ν) − r²(1 + 3ν)];
  - borda: Mr = −q·a²/8 = −q·l²/32; Mt = −q·a²/40 = −q·l²/160;
  - centro: Mr = Mt = q·a²(1 + ν)/16 = q·l²/53,33;
  - flecha w0 = q·a⁴/(64D) = 0,0113·q·l⁴/(E·h³), D = E·h³/12(1 − ν²).
- Apoiada: Mr = q(3 + ν)(a² − r²)/16; centro q·a²(3 + ν)/16; w0 = q·a⁴(5 + ν)/(64D(1 + ν)).
- Momento uniforme Me aplicado na borda soma Me constante a Mr e Mt em toda a placa (superposição).
### 5.2 A laje não é "engastada na parede" por decreto
- Junta monolítica = nó de Cross: o momento é o mesmo na parede e na laje (mais a aba, se houver). Momento final:
  M = (S_l·FEM_p + S_p·FEM_l)/(S_p + S_l).
  - S_p = 2Dβ (parede longa com w = 0 na base);
  - S_l = D_l(1 + ν)/a (placa inteira sob momento de borda);
  - FEM = momentos de engaste perfeito, convenção + = tração na face interna.
- Laje grossa com parede fina → a borda gira e a laje se aproxima de **apoiada**. Isso aumenta o momento no centro e reduz o da borda, e a parede passa a receber momento de base que precisa armar. Conferir a casca da parede com `parede_ops(base='mola', k_theta=S_l)` e a placa com `laje_circular_ops`.
- Tanque cheio apoiado no solo: a carga do fundo vai em grande parte direto ao solo → placa sobre Winkler (skill `interacao-solo-estrutura`); a hipótese "vão livre entre paredes" do TCC só vale para subpressão líquida (tanque vazio).
### 5.3 Armadura
- Radial + circunferencial cruza barras demais no centro → usar 3–4 grupos de barras paralelas cruzando no centro, completados por radiais na periferia, ou malha ortogonal; variar a seção do centro para a periferia (Cruz 2009).
- Malha ortogonal sob momentos principais Mr, Mt (Wood-Armer): com o mesmo sinal, mx* = my* = máx(|Mr|, |Mt|). No centro Mr = Mt (isótropo), portanto **o fator √2 do TCC/Cruz é conservador**, não obrigatório. Com sinais opostos, armar as duas faces.
- Aba (balanço da laje além da parede): viga em balanço com (solo + peso − subpressão) ou só a subpressão líquida conforme a etapa.

## 6. Estabilidade contra flutuação (UPL)
- Etapa crítica: **tanque vazio** com NA máximo (inclusive durante a obra, se o rebaixamento for desligado antes do reaterro).
- EC7 (2.4.7.4, tab. A.15 — conferir): Vdst,d = Gdst,d + Qdst,d ≤ Gstb,d + Rd.
  - γG,dst = 1,0; γQ,dst = 1,5; γG,stb = 0,9.
  - Gdst,d = γG,dst·γw·hw·A_base, com A_base = **área total da face inferior** (inclui parede e aba).
  - Gstb,d = 0,9·(parede + laje + aba + solo sobre a aba + lastro).
  - Rd = A_lateral·σ'h·tan δ (atrito lateral) → desprezar, a favor da segurança.
- Solo sobre a aba: com a subpressão na área total, usar o peso **saturado** abaixo do NA (equivale a subpressão na área interna + peso submerso). Contar o volume do prisma vertical sobre a aba (φ = 0); a cunha só com parâmetros confiáveis.
- Norma brasileira: conferir NBR 6122:2022 (subpressão/levantamento) e NBR 8681 (combinação de equilíbrio); na prática FS ≥ 1,1–1,3 sem atrito (conferir com o critério do contratante).
- Soluções quando não passa:
  - aba maior: só funciona se 0,9·(γsolo·h_solo + γc·h_laje) > γw·hw por m², senão nenhuma aba resolve;
  - laje mais espessa: cada metro a mais também aumenta hw;
  - estacas/tirantes de tração (permitem laje fina sobre vigas — a conclusão do TCC só fecha com ancoragem, porque a laje fina pesa menos);
  - lastro;
  - drenagem permanente sob a laje com válvulas de alívio (exige manutenção e aceita a entrada de água);
  - rebaixamento permanente (evitar).

## 7. Verificações e detalhes de estanqueidade
- ELU por faixa de 1 m (seção 15 da skill principal): flexão da laje (borda, centro, aba), parede (M0, M de vão) e anel (As = Nθ,d/fyd, nas duas faces).
- **Cortante da laje sem estribos** junto à parede: VRd1 (NBR 6118 19.4.1). O TCC não verificou; no caso revisado passa (Vd = 412 kN/m < VRd1 = 533 kN/m).
- **ELS-W é o estado que governa o reservatório.** A NBR 6118 tab. 13.4 (wk ≤ 0,3 mm em CAA III) não garante estanqueidade. Prática:
  - wk ≤ 0,1–0,2 mm, ou EN 1992-3 classe 1 com wk1 = 0,2 mm para hD/h ≤ 5 até 0,05 mm para hD/h ≥ 35 (conferir); ACI 350 como alternativa;
  - anel não fissurado: σct = Nk/(Ac + (αe − 1)As) ≤ fctk,inf;
  - ou σs limitada no anel (100–160 MPa conforme Ø e espaçamento — conferir).
- Armadura mínima de retração/temperatura em peças restringidas (EN 1992-3: As,min = kc·k·fct,eff·Act/σs — conferir); nas duas faces.
- Flecha da laje: imediata × (1 + αf) ≤ l/250 (NBR 6118 tab. 13.3); o TCC usou 2 × imediata. Com subpressão a flecha é para cima (passarelas e tubulações apoiadas no fundo sentem isso).
- Durabilidade: ETA/ETE, esgoto e efluentes → CAA III/IV (tab. 6.1 — conferir); a/c e classe pela tab. 7.1 (III: ≤ 0,55, ≥ C30; IV: ≤ 0,45, ≥ C40); cobrimento pela tab. 7.2 (o TCC: CAA III, 4,0 cm).
- Detalhes:
  - juntas de concretagem parede-laje com mata-junta (PVC/bentonítico);
  - emendas dos anéis defasadas (NBR 6118 9.5.2 proíbe traspasse em tirantes — conferir aplicabilidade à casca; senão luvas ou traspasse ≤ 25–33 % por seção);
  - impermeabilização interna compatível com o líquido;
  - teste de estanqueidade cheio **antes do reaterro** (situação de cálculo própria).

## 8. Estudo de caso (TCC) e revisão ND
### 8.1 Dados
- Tanque de equalização da ETL do Cubatão (Cia. Águas de Joinville), concluído no fim de 2012.
- Geometria: V = 2 000 m³, Øint = 23 m (a = 11,5 m), parede 0,30 m × 7,75 m, enterrado 6,95 m (topo da laje); laje maciça 0,50 m com aba de 1,0 m além da parede (raio da base 12,8 m).
- Solo e NA: argila mole (γ = 15 kN/m³, φ = 0 adotado); NA a 3,2 m, adotado no terreno.
- Patologia: após a construção o tanque flutuou e inclinou. Ao esvaziar com poços de rebaixamento, o centro da passarela subiu 2 cm (laje abaulando) e o esgotamento foi interrompido. A projetista executou reforço da laje para 1,2 m (498,57 m³ de concreto).
### 8.2 Cálculo do TCC
- Flutuação: subpressão 74,5 kPa; Gdst = 10·7,45·π·11,5² = 30 953 kN; Gstb = 0,9·4 254,7 (parede) + 6 434 (laje) = 9 620 kN; solo na aba 8 057 kN → 30 953 > 17 677 → flutua (confirma o ocorrido). O texto cita depois 11 198,98 kN como acréscimo necessário, inconsistente com a diferença de 13 276 kN.
- Proposta: laje 1,0 m + aba 1,9 m. A flecha "6,8 cm > 9,32/2" levou a laje para 1,2 m e aba 1,6 m.
- Hipóteses da laje (engastada na parede, vão 23,3 m):
  1. vazio sem aterro: q = 81,5 − 30 − 1 = 50,5 kPa para cima → Mr,borda = 856,75, Mt,borda = 171,35, Mcentro = 514,08 kN·m/m; As = 24,73 cm²/m na borda (Ø20 c/12) e mínimo 0,15 % = 18 cm²/m (Ø16 c/11) no resto;
  2. cheio sem aterro (teste de estanqueidade): q = −19 kPa;
  3. vazio com aterro: aba com 53,75 kPa;
  4. cheio com aterro: repete 2 e 3.
- Conclusão da autora: a laje maciça de 1,2 m é antieconômica (676,93 m³ contra 257,36 m³ executados); seria melhor laje fina sobre reticulado de vigas.
### 8.3 Revisão ND (07/10/2026, `tanques_nd.py`)
1. **Subpressão na área errada:** o TCC aplicou na área interna (π·11,5²) e somou o peso total do solo da aba (dupla contagem favorável); o 0,9 entrou só na parede. Na área total (π·12,8²): Vdst = 38 347 kN.
   - Projeto original: FS = 0,44.
   - Solução do TCC (1,2 m + aba 1,6 m): FS = 0,67 → **ainda flutuaria** pelo EC7.
   - Aba necessária com laje de 1,2 m: 5,6 m (γ = 15) ou 4,0 m (γsat = 18). Inviável → a resposta certa é ancoragem (estacas de tração) ou drenagem com alívio.
2. **Flecha com erro de 10×** (kgf/cm² misturado com tf/m²): w0 = 0,0113·53,5·23,3⁴/(26 072 MPa·1,0³) = **0,68 cm**, não 6,8 cm; com 1,2 m, 0,37 cm (não 3,7). O aumento 1,0 → 1,2 m foi motivado por esse erro; a flecha nunca governou.
3. **Engaste impossível:** Mr,borda = 857 kN·m/m teria de ser equilibrado pela parede de 0,30 m (MRd,máx ≈ 336 kN·m/m com x/d = 0,45). Compatibilizando, com S_l/S_p ≈ 4,7 e FEM da parede vazia (solo φ = 0, K0 = 1): borda ≈ −220 kN·m/m e centro ≈ +1 150 kN·m/m (tração na face superior/interna), contra 514 do TCC. Isso é coerente com o abaulamento observado no centro.
   - É ordem de grandeza: falta a aba e a excentricidade da parede; modelo completo no OpenSees para fechar.
4. Não verificados no TCC: cortante VRd1 (passa), ELS-W/estanqueidade, anel da parede, situação de obra com rebaixamento desligado.
5. Ponto positivo: o roteiro de hipóteses por etapa (vazio/cheio × com/sem aterro) está certo e deve ser mantido.

## 9. Roteiro ND (tanque cilíndrico)
1. Dados:
   - geometria (a, t, H, d, h_laje, aba, cota de assentamento);
   - líquido (γ, nível máximo);
   - sondagem (NA máximo, γ, φ', camadas moles);
   - CAA e critério de estanqueidade combinados com o contratante.
2. Situações de projeto:
   - (a) vazio + NA máximo + aterro;
   - (b) cheio sem aterro (teste);
   - (c) cheio + aterro (+ NA mínimo, sem alívio);
   - (d) obra: vazio, sem aterro, rebaixamento ligado/desligado.
3. Flutuação (seção 6) com `flutuacao()` → decidir lastro/aba/ancoragem antes de dimensionar a laje, porque a decisão muda a espessura.
4. Parede: `ParedeCilindrica` (βH ≥ 3) e `parede_ops` (conferência, parede curta, solo externo, base elástica).
5. Laje: `laje_circular` (engastada e apoiada como envoltória) → `junta_parede_laje` para o momento real da borda → `laje_circular_ops` se houver furos, poço, pilares ou solo (Winkler).
6. ELU: `As_flexao` (laje, aba, parede), `As_anel`, `VRd1_laje`; ELS: fissuração/estanqueidade, flecha com αf, retração.
7. Detalhamento: malha/grupos de barras, anéis com emendas defasadas, mata-junta, cobrimento.
8. Memória: hipóteses (NA, φ, ligação), tabela de situações × esforços, validação Timoshenko × OpenSees, figuras.

## 10. Armadilhas
- Calcular flutuação com a área interna e ainda contar o peso total do solo da aba.
- Adotar NA de sondagem pontual (seca) em vez do NA máximo.
- Empuxo ativo em parede rígida.
- Laje "engastada" na parede fina sem conferir se a parede absorve o momento (e sem armar a base da parede para ele).
- Unidades mistas (kgf/cm², tf/m², kN/m²) — o TCC errou a flecha em 10× assim.
- Esquecer o teste de estanqueidade antes do reaterro e a fase de obra com rebaixamento.
- Verificar só ELU: em reservatório quem governa é a fissuração/estanqueidade.
- Aplicar √2 na malha do centro achando obrigatório (é conservador).
- Usar solução de casca longa em parede curta (βH < 3).
- Laje fina sobre vigas "resolve" flexão mas piora a flutuação (menos peso) — precisa de ancoragem.

## 11. Reservatórios retangulares e estações elevatórias de esgoto (EEE)
### 11.1 Concepção
- EEE típica: poço úmido (sucção) + poço seco/caixa de válvulas e, às vezes, caixa de chegada/gradeamento; paredes e laje de fundo maciças, tampa com aberturas para bombas (talha/monovia), escada e casa de comando sobre pilares e vigas.
- Caixa retangular: não há tração anelar de membrana; as paredes trabalham como **placas à flexão** (e tração/compressão no plano vinda das paredes perpendiculares). Por isso, para o mesmo volume, armam bem mais que a cilíndrica.
- Vinculação usual (tabelas de Bares/Czerny/PCA "Rectangular Concrete Tanks"):
  - parede: base engastada na laje, bordas verticais engastadas nas paredes vizinhas, topo livre (sem tampa) ou apoiado (tampa monolítica);
  - laje de fundo: engastada nas paredes;
  - tampa: apoiada ou engastada conforme a rigidez relativa.
- Notação das tabelas de Bares usada nos memoriais: m = μ·p·l²/100, l = menor vão; na parede, Mx/M'x = direção vertical (M'x na base), My/M'y = horizontal (M'y nas bordas verticais), Myb/M'yb = horizontal ao longo da borda livre do topo. Carga triangular (hidrostática/empuxo) com p = ordenada máxima na base.
- λ = ly/lx ≥ 2 → laje armada em uma direção: faixa biengastada M' = p·l²/12 (μ = 8,33) e M = p·l²/24 (μ = 4,17). Serve de conferência rápida das tabelas.
### 11.2 Compatibilização dos momentos
- Entre paredes vizinhas e entre parede e laje o momento de borda é um só (nó). Prática dos escritórios: adotar o **maior** dos dois momentos de engaste. É conservador no apoio, mas:
  - o vão do elemento mais flexível foi calculado com engaste perfeito e passa a ter momento positivo maior do que o tabelado; corrigir pelo equilíbrio (Cross/NBR 6118 14.7.6.2: no mínimo o maior entre a média e 0,8 do maior, com correção dos vãos — conferir);
  - modelo de cascas no OpenSees (função de caixa retangular ainda não existe no `tanques_nd.py` — backlog) fecha o problema em caixas com aberturas, poços e paredes de alturas diferentes.
### 11.3 Situações de carga (mesma lógica do tanque cilíndrico, seção 9)
- Parede externa:
  - (a) cheio sem aterro (teste de estanqueidade): água interna, tração na face interna no vão e externa nos engastes;
  - (b) vazio com aterro + NA máximo: empuxo de solo **em repouso** (K0 = 1 − sen φ'), γ' abaixo do NA + pressão d'água γw·hw — inverte as faces;
  - (c) cheio com aterro: diferença das duas (alívio) — não governa, mas vale para a fase de operação.
- **Nunca somar** a água interna com o empuxo externo como se agissem na mesma face: atuam em faces opostas e se aliviam. Somar só "parece" a favor da segurança (magnitude), mas arma a face errada nas situações reais.
- Parede interna (entre poços): um lado cheio e outro vazio (manutenção) — carga hidrostática total.
- Laje de fundo:
  - vazio + NA máximo: subpressão γw·hw − peso próprio, para cima, vão entre paredes;
  - cheio: a carga d'água vai direto ao solo; a laje sofre o momento de borda das paredes e a reação do solo sob as paredes (placa sobre Winkler, skill `interacao-solo-estrutura`).
- Flutuação (seção 6) obrigatória sempre que a laje for calculada com subpressão: se há subpressão para fletir a laje, há para levantar a caixa.
- Tampa: além de 2 kN/m², considerar equipamento (bombas, painéis), carga de içamento na viga de talha e, em EEE sob passeio/rua, veículo (NBR 7188 — conferir). Aberturas grandes viram bordas livres na laje.
### 11.4 Durabilidade e estanqueidade em esgoto
- Ambiente de esgoto (H2S → ácido sulfúrico biogênico na zona não submersa): **CAA IV**, C40, a/c ≤ 0,45, cobrimento nominal ≥ 45–50 mm (NBR 6118 tab. 6.1, 7.1, 7.2 nota c — conferir na edição 2023). Cobrimento vale para **todos** os elementos em contato com o efluente/gases, inclusive vigas e pilares internos — conferir se o arquivo de critérios do TQS/Eberick foi ajustado (o padrão do programa é 2,5 cm).
- Revestimento interno anticorrosivo (epóxi, poliureia, argamassa polimérica) na zona de variação de nível e no teto.
- ELS-W governa (seção 7): wk ≤ 0,1–0,2 mm ou σs ≤ 150–200 MPa em serviço nas faces molhadas; com σs ≈ 300 MPa (armadura de ELU pura) a abertura passa de 0,3 mm.
- Armadura mínima de retração nas duas faces; juntas de concretagem com mata-junta; tubulações atravessando paredes com flange de vedação/pré-chumbadas.

## 12. Estudo de caso: EEE Presidente Vargas (Fortaleza-CE) e revisão ND
### 12.1 Fonte e dados
- Memorial de cálculo e descritivo, projeto estrutural executivo da EEE do bairro Presidente Vargas, SEINF/Prefeitura de Fortaleza, jan/2020, rev. 00 (21 p., anexo de edital público). Projetista: escritório de estruturas de Fortaleza, ART própria. Lido integralmente em 07/10/2026 (texto por pdf.js; pp. 7–16 são imagens, lidas renderizadas). 6 pranchas citadas (formas, cortes, armaduras de lajes, paredes, pilares/vigas/sapatas, escada) **não** estavam no PDF.
- Normas citadas: NBR 6118:2014, NBR 6120:1980, NBR 6122:2010, NBR 8681:2003, NBR 15575:2013 → vigentes: NBR 6118:2023, NBR 6120:2019, NBR 6122:2022 (conferir).
- Materiais: CAA IV, C40 (Ecs 32 GPa), cobrimento 50 mm em contato com o solo reduzido 5 mm por controle (7.4.7.4), CA-50/60; σadm = 2,0 kgf/cm² (SPT out/2019).
- Método: placas por tabelas de **Bares** (cargas uniformes e triangulares); vigas e pilares por relatórios TQS (vigas 20×60, vão 7,0 m; pilares 25×30).
- Geometria lida nos quadros:
  - poço 1 (laje fundo 11,56 × 4,30 m, λ = 2,70; paredes PAR7=PAR15 de 11,56 × 5,4 m e PAR26 de 4,30 × 5,4 m);
  - poço 2 (laje 4,30 × 2,80 m; PAR6=PAR14 de 2,80 × 6,5 m; parede interna PAR17=PAR21 de 4,30 × 6,5 m);
  - lajes de fundo 0,30 m; tampa 0,20 m (4,30 × 2,80, q = 0,2 + 0,15 + 0,5 = 0,85 tf/m²). Espessura das paredes não consta (admitido 0,30 m na revisão).
### 12.2 Hipóteses decodificadas (não escritas no memorial — reconstruídas pelos números)
- Pressão d'água = 0,855·γw·h (equivale a nível operacional a ~85 % da altura): PAR17 5,57 = 0,857·6,5.
- Parede externa: P = 0,855·γw·h + Ka·γ·h com Ka = 0,33 (ativo, φ = 30°) e γ = 1,8 tf/m³ seco, sem NA → 7,84 (h = 5,4) e 9,43 (h = 6,5) conferem a ±0,2 %.
- Laje de fundo: P = 0,855·γw·h − 0,75 (peso da laje) → 3,88 e 4,82 conferem: é **subpressão** com o tanque vazio.
- Conferência das tabelas: laje 1 (λ = 2,7) μx' = 8,33 e μx = 4,17 = faixa biengastada 1/12 e 1/24 ✓; momentos m = μ·p·l²/100 reproduzidos em todos os quadros.
### 12.3 Revisão ND (`eee_check.py`)
1. **Água e solo somados na mesma face** (parede externa): estão em faces opostas; as situações corretas são (a) cheio sem aterro e (b) vazio com aterro + NA. Além disso o empuxo é ativo (deveria ser repouso, K0 ≈ 0,5 → +50 %) e o solo foi tomado seco, enquanto a laje foi calculada com subpressão → **hipóteses de NA incoerentes** entre parede e laje.
2. **Flutuação não verificada.** Se a laje recebe subpressão, a caixa pode subir. Estimativa do poço 1 (paredes e laje 0,30, tampa 0,20 — conferir nas pranchas), EC7 com 0,9·G:
   - NA no terreno: U = 3 396 kN × 0,9G = 1 870 kN → FS = 0,55;
   - NA na hipótese do próprio memorial (0,855·h): FS = 0,64;
   - só passa com NA abaixo de ~meia altura (FS = 1,16 com hw = 2,7 m).
   - Mesmo diagnóstico do tanque do TCC (seção 8): exige aba com aterro, lastro ou estacas de tração — e a fase de obra com rebaixamento.
3. **Bitolas menores que a área calculada** (As do memorial reproduzida pela ND com d ≈ 0,245 m, C40):
   - laje M'x = 23,58 tf·m/m: As = 36,3 cm²/m × Ø20 c/17 = 18,5 cm²/m (metade);
   - PAR7 M'yb = 16,57: 24,5 × Ø12,5 c/10 = 12,3 (metade); M'y = 10,99: 15,7 × 12,3;
   - PAR26 M'x e laje 1 M'y = 5,51: 7,6 × Ø10 c/14 = 5,6.
   - Pode ser barra dupla/duas camadas indicada só na prancha — **conferir nas pranchas antes de concluir**; se não for, é falha de detalhamento.
4. **Cobrimento incoerente:** memorial especifica CAA IV (45 mm), mas os relatórios TQS de vigas e pilares rodaram com cobrimento 2,5 cm (critério padrão).
5. **Nó parede-laje:** a laje 1 adotou M'x = 23,58 da parede PAR7 (contra 5,97 dela própria) e a parede manteve Mx = 1,21 de engaste perfeito. Correto seria equilibrar o nó (seção 5.2/11.2); o momento real de base fica entre os dois e o positivo vertical da parede aumenta. Ponto positivo: a compatibilização pelo maior momento entre paredes vizinhas foi feita sistematicamente (coluna "M adotado").
6. **Não verificados:** ELS-W/estanqueidade (σs ≈ 300 MPa em serviço no engaste da laje → wk > 0,3 mm; para σs ≈ 150 MPa precisaria ~dobrar As ou engrossar a seção), cortante sem estribos (VRd1) nas lajes e paredes de 0,30, armadura mínima de retração, parede interna com um lado vazio, situação de obra.
7. Tampa com 2 kN/m² sem carga de equipamento/içamento; normas de 1980–2014 citadas.
8. Lição: memorial de EEE que só traz tabelas de Bares + relatórios do TQS não demonstra as hipóteses de NA, empuxo e flutuação — que são justamente o que derruba esse tipo de obra. Na ND, o memorial de reservatório deve abrir com o quadro de situações (cheio/vazio × com/sem aterro × NA) e o FS à flutuação.
### 12.4 Roteiro ND (caixa retangular / EEE)
1. Dados: geometria de cada poço (vãos internos, alturas, espessuras), níveis operacionais e de extravasão, sondagem (NA máximo, γ, φ'), cargas de equipamento e tráfego na tampa, CAA IV.
2. Flutuação primeiro (seção 6), com a área total da base.
3. Paredes por situação (11.3) com tabelas (Bares/PCA) ou placa no OpenSees; laje de fundo com subpressão (vazio) e sobre Winkler (cheio).
4. Compatibilizar nós e corrigir vãos.
5. ELU (flexão, cortante VRd1, tração no plano das paredes perpendiculares), ELS-W (σs/wk), mínimos de retração.
6. Detalhamento coerente com As calculada; cobrimento CAA IV em todos os elementos internos; mata-junta, passagens de tubo.
7. Memória com o quadro de hipóteses e conferência independente (faixa 1/12–1/24, ou OpenSees).