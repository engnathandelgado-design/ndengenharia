---
name: "projetos-estruturais-concreto-armado-protendido"
description: "Use ao projetar, calcular, revisar ou ensinar estruturas de concreto armado e protendido pela NBR 6118/9062 (inclusive tanques e reservatórios cilíndricos), ao simular ou verificar sistemas estruturais pelo MEF (inclusive juntas de estruturas segmentadas e protensão externa) e ao desenvolver o software estrutural da ND Engenharia (Parte D)."
---

# Projetos estruturais em concreto armado e protendido

Fontes incorporadas:
- Hanai, *Fundamentos do Concreto Protendido* (EESC-USP, 2005; base NBR 6118:2003).
- Inforsato, T. B. *Considerações sobre o projeto, cálculo e detalhamento de vigas pré-fabricadas protendidas com aderência inicial em pavimentos de edificações*. Dissertação de Mestrado, PPGCiv-UFSCar, 2009, orient. Roberto Chust Carvalho (base NBR 6118:2003 e NBR 9062:2006).
- Real, M. V. *Análise probabilística de estruturas de concreto armado, sob estado plano de tensão, através do método dos elementos finitos*. Tese de Doutorado, PPGEC-UFRGS, 2000, orient. Américo Campos Filho (base NBR 6118/1980) — Parte B, seções 15 a 20.
- Gonçalves, M. M. O. *Análise dos efeitos de segunda ordem em pilares de concreto armado aplicando o método dos elementos finitos*. Projeto de Graduação, POLI/UFRJ, 2017, orient. Sérgio Hampshire de C. Santos e Claudia R. Eboli (base NBR 6118:2014) — Parte C, seção 21.
- Oliveira, D. S.; Barros, R.; Giongo, J. S. *Blocos de concreto armado sobre seis estacas: simulação numérica e dimensionamento pelo método de bielas e tirantes*. RIEM v. 7 n. 1, 2014 (base NBR 6118:2007), com os critérios de Andrade (1989) — Parte C, seção 22.
- *Introdução ao Método dos Elementos Finitos*, apostila TM266, DEMEC-UFPR (fundamentos, erro, Gauss/isoparamétrico, autovalores, dinâmica) — Parte C, seção 23.
- Spessatto, R. P. *Análise pelo MEF do comportamento das juntas de tabuleiro de ponte composto por aduelas pré-moldadas de concreto*. Dissertação, PPGEC/UFRGS, 2022, orient. Américo Campos Filho (base NBR 6118:2014, 7187:2021, 7188:2013) — Parte C, seção 24.
- Koneski, G. F. *Dimensionamento da laje de fundo de tanque enterrado em concreto armado com formato cilíndrico com ênfase na verificação de estabilidade contra flutuação*. TCC, UDESC/CCT Joinville, 2013, orient. Sandra Denise Krüger Alves (base NBR 6118:2003 + EC7) — Parte C, seção 25; detalhes na skill `tanques-reservatorios-concreto`.
- *PCI Big Beam Competition 2015 — Mr. Beam*, University of Washington (orient. John Stanton; produtor Concrete Technology Corp.), material de pré-moldados do Prof. Paulo Bastos (UNESP-Bauru) — viga pré-tracionada com cordoalhas isoladas, ensaiada até a ruptura (base ACI 318-11 / PCI) — seção 10, item 12; receita completa na skill `vigas-premoldadas-protendidas`; MEF em `mef-opensees-opsvis` 14.

Atualizar sempre para NBR 6118:2023 e NBR 9062:2017. O usuário é engenheiro estrutural com Master em Protendido e professor de concreto: responder em português técnico, citando item da norma. Valores com (conferir) devem ser checados na norma vigente.

## 1. Conceito
- Protensão = estado prévio de tensões que melhora resistência/comportamento (Hanai). CA x CP diferem só pela existência de forças de protensão.
- Isostática: esforços de protensão autoequilibrados. Hiperestática: somar hiperestáticos de protensão ao isostático P·e.
- Carga equivalente de cabo parabólico: u = 8·P·f/L².

## 2. Sistemas
- Pré-tração (aderência inicial): pista 80–200 m, ciclo ~24 h, cura térmica; pré-moldados (vigas, lajes alveolares, terças).
- Pós-tração com aderência posterior (bainha + calda) e sem aderência (cordoalha engraxada PEAD 12,7/15,2 mm).

## 3. Materiais
- CP-190 RB: fptk = 1900 MPa; fpyk ≈ 0,90 fptk (RB) / 0,85 fptk (RN). Ep ≈ 200 GPa (cordoalhas). Áreas: Ø9,5 = 0,548 cm²; Ø12,7 = 0,987 cm²; Ø15,2 = 1,40 cm² (conferir catálogo).
- Concreto: na transferência usar fckj, fctm,j, Eci(j). fctm = 0,3·fck^(2/3) (≤C50); fctk,inf = 0,7 fctm.
- ψ1000 (%), σpi/fptk = 0,6/0,7/0,8: cordoalha RN 3,5/7,0/12,0; RB 1,3/2,5/3,5; fio RN 2,5/5,0/8,5; RB 1,0/2,0/3,0; barras 1,5/4,0/7,0. ψ(t) = ψ1000·((t−t0)/41,67)^0,15 (dias); ψ∞ ≈ 2,5·ψ1000.

## 4. Tensão máxima na protensão (NBR 6118 9.6.1.2.1)
- Pré-tração: ≤ 0,77 fptk e ≤ 0,90 fpyk (RN) / 0,85 fpyk (RB) → CP-190 RB ≈ 1453 MPa.
- Pós-tração: ≤ 0,74 fptk e ≤ 0,87 fpyk (RN) / 0,82 fpyk (RB) → CP-190 RB ≈ 1402 MPa.
- Barras: ≤ 0,72 fptk e ≤ 0,88 fpyk.

## 5. Forças representativas
Pi (macaco) > Pa (ancorada, antes da transferência) > P0 (após perdas imediatas) > P∞. Perdas totais típicas 15–30 %; calcular de fato em vez de adotar porcentagem conservadora (Inforsato mostra que a consideração das perdas influencia a armadura).

## 6. Perdas imediatas
- Atrito (pós): P(x) = Pi·e^−(μΣα + kx), k ≈ 0,01μ. μ: 0,50 sem bainha; 0,30 barras nervuradas/bainha metálica; 0,20 fios/cordoalhas em bainha metálica; 0,10 lubrificada; 0,05 cordoalha engraxada.
- Cravação: área entre diagramas = δ·Ep·Ap; w = √(δ·Ep·Ap/p); ΔP(0) = 2pw. Pré-tração: ΔP = δ·Ep·Ap/L_pista.
- Encurtamento elástico: pré Δσp = αp·σcp(P0+g1); pós com n cabos: Δσp = αp(σcp+σcg)(n−1)/(2n).
- Pré-tração: relaxação inicial na pista entre ancoragem e liberação; efeito da cura térmica.

## 7. Perdas progressivas
- NBR 6118 9.6.3.4 (fase única): Δσp = [εcs·Ep − αp·σc,p0g·φ − σp0·χ] / [χp + χc·αp·η·ρp]; χ = −ln(1−ψ); χc = 1+0,5φ; χp = 1+χ; η = 1 + ep²Ac/Ic; ρp = Ap/Ac.
- **Seção composta / idades diferentes (Inforsato, cap. 4.3.4):** a peça pré-moldada recebe protensão em t0 (1–3 dias, cura térmica), a capa é lançada em t1 e carregamentos posteriores em t2. Calcular perdas por etapas (processo de perdas progressivas por intervalos): em cada intervalo, φ e εcs de cada concreto com a sua idade de carregamento; superpor fluência de cada parcela de carga com seu t de aplicação; após a capa, a retração diferencial capa × pré-moldado gera esforços adicionais.
- Estimativa rápida: Δσ_ret ≈ εcs·Ep; Δσ_flu ≈ αp·φ·σc,p0g; Δσ_rel ≈ ψ∞·σpi; reduzir 10–20 % pela interação.

## 8. Níveis de protensão e ELS (NBR 6118 tab. 13.4)
| Nível | CAA pré | CAA pós | Verificações |
|---|---|---|---|
| Parcial (1) | I | I e II | ELS-W wk ≤ 0,2 mm, comb. frequente |
| Limitada (2) | II | III e IV | ELS-F frequente; ELS-D quase permanente |
| Completa (3) | III e IV | — | ELS-F rara; ELS-D frequente |
- ELS-F: σct ≤ α·fctk,inf, α = 1,2 (T/duplo T), 1,3 (I/T invertido), 1,5 (retangular).
- Ato da protensão (17.2.4.3.2): γp = 1,1; compressão ≤ 0,70 fckj; tração ≤ 1,2 fctm,j, senão armadura passiva.
- γp ELU = 1,2 desfavorável / 0,9 favorável; ELS = 1,0.

## 9. Tensões normais
- σ = P/A + P·e/W ± M/W; núcleo central k1 = W2/A, k2 = W1/A (retangular h/6). Convenção Hanai: compressão negativa — sempre explicitar a convenção.
- Exemplo Hanai (0,20×0,75 m, L = 7 m, P = −600 kN): ep = h/6 → σ2,p = 0; ep = 0,325 m suporta q 2,31× maior com as mesmas tensões de serviço, mas gera +5,17 MPa em vazio na borda superior.
- Fuso limite / diagrama de Magnel para escolher P e e.

## 10. Vigas pré-tracionadas de seção composta (Inforsato 2009)
Roteiro sistematizado pelo autor para vigas de pavimento (pré-moldado + capa moldada no local):
1. **Lançamento estrutural:** vigas biapoiadas sobre consolos/dentes Gerber; definir vão, seção (retangular, I, T invertido), capa e lajes.
2. **Fases de carregamento e seção resistente:**
   - Fase 1 (seção simples do pré-moldado): protensão + g1 (peso próprio), depois laje + capa fresca.
   - Fase 2 (seção composta homogeneizada): revestimento, alvenaria, q. Homogeneizar a capa por n = Ec,capa/Ec,pm (concretos diferentes).
   - Tensões são acumuladas: cada parcela usa as propriedades (A, I, W) da seção que existia quando foi aplicada.
3. **Armadura longitudinal ativa:** dimensionar pelas condições de ELS do nível de protensão. **Conclusão do autor: a situação determinante foi a de serviço com descompressão (ELS-D)** — o ELU costuma ter folga. Depois verificar ELU e ato da protensão.
4. **Isolamento (embainhamento) de cordoalhas:** junto aos apoios o momento de g1 é ~0 e a borda superior fica tracionada no ato. Isolar parte das cordoalhas com tubos plásticos num trecho junto ao apoio, determinando a necessidade e o comprimento pela verificação de tensões em seções ao longo do vão (considerando lbpt). Prática: isolar simétrico, escalonar comprimentos, não isolar mais que ~25–40 % das cordoalhas (conferir); alternativa: cordoalhas superiores.
5. **Perdas:** iniciais + progressivas considerando idades diferentes (seção 7).
6. **Armadura transversal:** Modelo I (θ = 45°) e Modelo II (θ variável 30–45°) da NBR 6118 17.4; a protensão aumenta Vc via momento de descompressão: Vc = Vc0·(1 + M0/MSd,max) ≤ 2Vc0. **Conclusão do autor: considerando a protensão, a armadura de cisalhamento resultante foi a mínima.** Lembrar decalagem do diagrama (al).
7. **Interface pré-moldado/capa (armadura de costura):** NBR 9062 — τsd = Vd/(b·d) ≤ τud = βs·(As/(b·s))·fyd + βc·ftd, com βs e βc em função da taxa e da rugosidade (ex.: ρ ≤ 0,2 %: βs = 0, βc = 0,3; ρ ≥ 0,5 %: βs = 0,9, βc = 0,6) (conferir NBR 9062:2017). Estribos da viga podem servir como costura se ancorados na capa.
8. **Extremidades com dente Gerber:** modelo de bielas e tirantes da NBR 9062 — tirante horizontal no dente, armadura de suspensão vertical junto à face do recorte, costura horizontal e verificação da biela; atenção à região de transferência da protensão coincidir com o dente. Para cálculo detalhado usar a ferramenta de consolos/dentes Gerber do usuário.
9. **Ligações semirrígidas (cap. 7):** método Beam-Line — cruzar a reta da viga (rotação x momento entre biapoiada e engastada) com a curva momento-rotação da ligação (rigidez secante Rsec). Fator de restrição αR = 1 / (1 + 3·(EI)sec/(Rsec·L)); momento na extremidade ≈ αR·M_engaste perfeito. Classificação NBR 9062:2017: αR < 0,15 articulada; 0,15–0,85 semirrígida; > 0,85 rígida (conferir faixas). **Conclusão do autor: a eficiência das ligações semirrígidas fica reduzida pela presença do dente Gerber** (altura útil reduzida na ligação), mesmo aumentando a armadura negativa de continuidade na capa.
10. **Deformações (ELS-DEF):** flecha por etapas com a seção de cada fase, contraflecha de protensão e fluência de cada carregamento com sua idade; limites NBR 6118 tab. 13.3 (L/250 aceitabilidade sensorial; L/350 ou L/500 com alvenaria, conforme o caso).
11. **Comparação de seções:** **conclusão do autor: seção I tem melhor rendimento estrutural** que a retangular (rendimento geométrico de Guyon ρ = I/(A·y1·y2): retangular = 0,33; seções I maiores) — menos cordoalhas e menos peso; contrapartidas: forma mais cara, alma fina, estética/forro.
12. **Estudo de caso — PCI Big Beam 2015 (viga I pré-tracionada, ensaio de 4 pontos).** Peça de 5,49 m, vão de ensaio 5,18 m (17 ft), cargas a 2,13 m dos apoios; seção I h = 457 mm (A = 516 cm², I = 1,147·10⁻³ m⁴); concreto leve f'c ≈ 63 MPa; 4 cordoalhas Ø12,7 retas com o **trecho central de 3,35 m isolado** para tentar ganhar flecha na ruptura; σpe ≈ 1178 MPa. Ensaio: Pcr = 115,6 kN, Pu = 181,5 kN, flecha na ruptura 57 mm, ruptura por esmagamento da mesa comprimida. O que fica para projeto e aula:
    - **Fissuração** com seção bruta + Pe + resistência à tração na flexão acerta (−2 a +2 %). Pela NBR: α·fctm (α = 1,3 seção I).
    - **ELU com cordoalha não aderente** pela expressão da seção 11 (Δσp = 70 + fck/100ρp) dá Pu −20 % (a favor da segurança); a cordoalha real chegou perto de fpy. Usar a norma em projeto; σps entre a norma e fpy só para prever ensaio.
    - **Flecha na ruptura não sai do alongamento da cordoalha** (mecanismo de rótula previu 162 mm contra 57 mm): quando a mesa comprimida esmaga, quem limita a rotação é εcu do concreto. O MEF com seção de fibras e cordoalha em Truss isolado acertou Pu −4 % e flecha −5 % (`mef-opensees-opsvis` 14).
    - **Isolar o meio para ganhar ductilidade não funciona:** o modelo totalmente aderente deu Pu +8 % e flecha na ruptura maior (60 × 54 mm). Isolamento serve para o ato da protensão nas extremidades (item 4), não para ductilidade.
    - Detalhamento: enrijecedores (alma alargada e armada) em todo apoio e carga concentrada; estribos contínuos para garantir ruptura por flexão; gaiola de confinamento na mesa comprimida; conferir comprimento das bainhas antes de concretar; não dobrar tela/CA-60 a quente. Prancha de produção por marca de peça: skill `vigas-premoldadas-protendidas` (7.2) + `pranchas-tecnicas-nd` (6A).

## 11. ELU — flexão
- Pré-alongamento εpnd = σp∞,d/Ep (γp = 0,9) + Δεp da compatibilidade (εcu = 3,5‰ até C50); σpd pelo diagrama bilinear (fpyd = fpyk/1,15, fptd = fptk/1,15).
- Rcc = 0,85 fcd·b·0,8x = Ap·σpd + As·fyd; ductilidade x/d ≤ 0,45 (≤C50); armadura mínima (tab. 17.3).
- Seção composta: LN pode cair na capa (fcd da capa) ou no pré-moldado (dois concretos).
- Sem aderência: Δσp = 70 + fck/(100ρp) ≤ 420 MPa (L/h ≤ 35); 70 + fck/(300ρp) ≤ 210 MPa (L/h > 35). Conservadora para a resistência (Big Beam: Pu −20 % do ensaio — 10.12); não usar o alongamento da cordoalha não aderente para estimar a flecha última.

## 12. ELU — cisalhamento
- V_ef = V_Sd − Pd·senα (cabos inclinados); cabos retos (pré-tração) não dão componente vertical — o ganho vem de M0.
- Descontar bainhas em bw (pós-tração).

## 13. Mandamentos de Leonhardt (resumo)
Só comprime onde o encurtamento é livre; desvios geram forças internas; não usar cegamente tensões altas; evitar tração sob peso próprio; armadura passiva transversal e nas ancoragens; proteger o aço; não restringir encurtamento; protender em etapas conforme fckj; controlar alongamento × força; seguir procedimento normalizado.

## 14. Controle de fábrica/obra
- ΔL teórico = P_médio·L/(Ep·Ap); comparar com medido (tolerância conforme NBR 14931/9062) (conferir).
- Pré-tração: liberar cordoalhas só com fckj comprovado em CP curado junto à peça.

## Roteiro geral (viga protendida isostática)
1. CAA → nível de protensão e combinações.
2. Propriedades das seções (simples e composta homogeneizada).
3. Esforços por fase (g1, laje+capa, g2, q) e combinações.
4. Estimar perdas → P∞ pela descompressão/fissuração → nº de cordoalhas (σpi máx.).
5. Perdas reais por etapas → iterar.
6. Ato da protensão ao longo do vão → isolamento de cordoalhas.
7. ELS (F/D/W) e flechas por etapas.
8. ELU flexão e cisalhamento; costura da interface; dente Gerber/consolo; ligação.
9. Memória em planilha com hipóteses, convenção de sinais e itens normativos.

## Armadilhas
- Misturar convenções de sinal; esquecer γp = 1,1 no ato; usar fck em vez de fckj.
- Calcular tudo na seção composta (cargas da fase 1 atuam só no pré-moldado).
- Ignorar idades diferentes e retração diferencial capa × pré-moldado.
- Esquecer as extremidades em pré-tração (isolamento, lbpt, dente Gerber).
- Contar com engastamento alto em ligação com dente Gerber.
- fpyk = 0,85 fptk para aço RB (é 0,90).
- Isolar cordoalhas no meio do vão esperando ductilidade: concentra a deformação numa fissura única e a mesa comprimida esmaga antes (10.12).
- Prever a flecha última pelo mecanismo de cordoalha não aderente (erro de 3× no Big Beam); usar MEF de fibras ou declarar a incerteza.

---

# Parte B — Concreto armado: cálculo como calculista, análise não-linear e confiabilidade

Postura: explicar hipótese → equação → número → verificação → decisão de projeto, sempre com unidades (kN, cm, kN/cm²; 1 kN/cm² = 10 MPa). Toda conta relevante em Python, conferida por caminho independente (equilíbrio, ordem de grandeza, tabela). Projeto pela NBR 6118:2023 (+ NBR 6120, NBR 8681); os β da tese de Real são referência conceitual, não critério de projeto. A responsabilidade técnica (ART) é do Nathan — sinalizar hipóteses que pedem decisão dele.

## 15. Dimensionamento (ELU) — NBR 6118:2023, concretos até C50

Materiais: fcd = fck/1,4; σcd = 0,85·fcd; fyd = fyk/1,15 (CA-50: 43,48 kN/cm²); Es = 210 GPa; εcu = 3,5‰; εc2 = 2,0‰. Bloco retangular: altura 0,8x, tensão 0,85fcd.

**Flexão simples (seção retangular)**
- Md = γf·Mk (γf = 1,4 combinação normal, ou combinação de cálculo NBR 8681).
- x = 1,25d·[1 − √(1 − Md/(0,425·bw·d²·fcd))]; exigir x/d ≤ 0,45 (ductilidade). Se exceder: armadura dupla ou aumentar seção.
- As = Md / [fyd·(d − 0,4x)]; As ≥ As,mín (ρmín ≈ 0,15% para C20–C30, cresce com fck — conferir tabela 17.3).
- Domínios: 2/3 com aço escoando (εs ≥ εyd = 2,07‰ p/ CA-50).

**Cisalhamento — Modelo I (θ = 45°)**
- VRd2 = 0,27·αv2·fcd·bw·d, αv2 = 1 − fck/250 (fck em MPa) → biela.
- Vc0 = 0,6·fctd·bw·d, fctd = 0,21·fck^(2/3)/1,4 (MPa); Vsw = VSd − Vc; Asw/s = Vsw/(0,9·d·fywd), fywd ≤ 43,5 kN/cm².
- Armadura mínima ρsw,mín = 0,2·fct,m/fywk; espaçamentos máximos do item 18.3.3.2.

**Pilares — método do pilar-padrão com curvatura aproximada (λ ≤ 90)**
- λ = le·√12/h; M1d,mín = Nd·(1,5 + 0,03h) [cm]; λ1 = (25 + 12,5·e1/h)/αb, 35 ≤ λ1 ≤ 90.
- Se λ > λ1: 1/r = 0,005/[h(ν + 0,5)] ≤ 0,005/h, ν = Nd/(Ac·fcd); Md,tot = αb·M1d,A + Nd·le²/10·(1/r) ≥ M1d,A.
- Armadura por ábacos de flexo-compressão ou pelo modelo de fibras deste skill (equilíbrio de N e M na seção).
- 90 < λ ≤ 140: pilar-padrão com rigidez κ aproximada ou método geral; λ > 140: método geral + fluência obrigatória.
- Dimensão mínima 19 cm (14 cm com γn); ρ entre 0,4% e 8% (incluindo emendas).

## 16. Serviço (ELS)

- Fissuração: Mr = α·fct·Ic/yt (α = 1,5 retangular; fct,m = 0,3·fck^(2/3) MPa; usar fctk,inf = 0,7·fct,m no ELS de formação de fissuras e fct,m no ELS de deformação). Abertura wk pelo item 17.3.3 (limites 0,2–0,4 mm conforme CAA).
- Flecha imediata: Branson, Ieq = (Mr/Ma)³·Ic + [1 − (Mr/Ma)³]·III ≤ Ic, com Ecs = αi·Eci, Eci = αE·5600√fck, αi = 0,8 + 0,2·fck/80 ≤ 1. Combinação quase-permanente (ψ2).
- Diferida: αf = Δξ/(1 + 50ρ'); total = imediata·(1 + αf). Limite visual L/250.
- Lição da tese: perto da carga de fissuração a flecha real tem grande dispersão (CV até ~0,3); o modelo "Estádio II puro" superestima a flecha. Branson/Ieq é melhor estimativa do valor médio.

## 17. Análise não-linear (modelo da tese, adaptado para fibras)

Concreto (CEB-FIP 1990, como na tese):
- Compressão: σ = −fc·(kη − η²)/(1 + (k − 2)η), η = ε/εc1, εc1 = 2,2‰, k = Eco/(fc/εc1), Eco = 2150·fcm^(1/3) [kN/cm²].
- Pós-pico: reta até 0,2fc em εcu = n·εc1, n = 4,81·fck^(−0,66) (fck em kN/cm²; n ≈ 3,0 p/ C20, 1,2 p/ C80).
- Tração: linear até 0,9fct; fct em ε = 0,15‰; tension-stiffening σ = 0,6fct(1 − ε/0,002). fctm = 0,14·fck^(2/3) [kN/cm²].
- Biaxial (só no MEF): critério de Kupfer & Gerstle, deformação uniaxial equivalente, fissuras distribuídas com G reduzido, ν = 0,2 até fissurar.
Aço: bilinear (CA-50 tipo A, Es2 = 0).
Viga biapoiada: pu = 8·Mmáx/L² (pico do diagrama M–κ); flecha = ∫κ·m̄ dx (trabalhos virtuais).
Pilar birrotulado: M(x) = P·(e1 + y(x)), integra curvaturas iterativamente até convergir; Pu = maior P com equilíbrio estável (bissecção).

## 18. Confiabilidade (Monte Carlo)

Variáveis (tese, cap. 6/8): fc normal, V = 0,15; fct com V = 1,2·Vfc; Ec com V = Vfc; correlações ρ(fc,fct) = 0,8, ρ(fct,Ec) = 0,7, ρ(fc,Ec) = 0,9 (Cholesky); fy normal V = 0,05; Es V = 0,025; b, h com σ = 0,5 cm; amostras truncadas em ±2,325σ; propriedades do concreto perfeitamente correlacionadas ao longo da peça (hipótese mais desfavorável).
Médias a partir de característicos: resistência μ = Xk/(1 − 1,645V); ação μ = Xk/(1 + 1,645V). Ações: G com V = 0,10, Q com V = 0,40.
Índice: M = R − S; β = (μR − μS)/√(σR² + σS²); Pf = Φ(−β). Alternativa lognormal: β ≈ ln(μR/μS)/√(VR² + VS²). 250 simulações já convergem média e desvio (conferir gráfico de convergência).
Interpretação: β da tese (vigas ≈ 9, pilares 5–7) ignora incerteza de modelo e o máximo da carga variável em 50 anos; para comparar com alvos normativos (ex.: EN 1990, β ≈ 3,8 em 50 anos, CC2) é preciso incluir essas incertezas. Use β principalmente para comparar alternativas de projeto entre si.

Lições práticas:
- Viga subarmada: R governado por fy (VR ≈ Vfy ≈ 0,05) → muito segura; controle tecnológico do aço importa mais que o do concreto para ELU.
- Pilar: R governado pelo concreto (VR 0,07–0,13) → β menor. β cresce com ρ, com e1/h e com λ. Pilares curtos, pouco armados e com carga quase centrada são os menos seguros — atenção ao controle do fck e à execução (dimensões).
- Média de R ≈ resposta com propriedades médias e dimensões nominais (diferença ≤ 2% nos pilares).

## 19. Script de referência (validado contra a tese)

`confiab_ca.py` (Apêndice) = modelo de fibras + Monte Carlo (250 simulações). Validação (μR / σR / β — tese × script):

| Peça | Tese | Script |
|---|---|---|
| V1 (ρ 0,42%) | 19,30 / 0,93 / 8,85 | 18,36 / 0,84 / 8,54 |
| V2 (ρ 0,67%) | 29,42 / 1,38 / 9,15 | 28,01 / 1,34 / 8,54 |
| V3 (ρ 0,94%) | 39,85 / 2,03 / 8,91 | 38,55 / 1,84 / 8,88 |
| P1 (λ26, ρ0,8%, e1/h 0,1) | 5004 / 651 / 5,27 | 4937 / 673 / 5,00 |
| P04 (λ26, ρ0,8%, e1/h 0,2) | 3773 / 453 / 5,57 | 3772 / 498 / 5,10 |
| P17 (λ52, ρ1,5%, e1/h 0,3) | 2641 / 251 / 6,27 | 2616 / 260 / 6,00 |
| P26 (λ78, ρ1,5%, e1/h 0,3) | 1856 / 139 / 6,88 | 1835 / 152 / 6,31 |
| P27 (λ78, ρ3,0%, e1/h 0,3) | 2629 / 195 / 7,04 | 2609 / 196 / 6,92 |

Vigas em kN/m, pilares em kN. Flecha média sob carga quase-permanente: 0,34 / 0,52 / 0,61 cm (tese 0,34 / 0,54 / 0,63). O script é ~5% conservador na ruptura de vigas e dá β 0,1–0,6 menor (conservador) — aceitável para comparar alternativas. Antes de usar num projeto, rodar de novo um caso desta tabela para conferir a instalação.
Uso: `Secao(b, h, [(y_topo, As), ...], props_concreto(fcm), fym)`; `viga_biapoiada(sec, L, p_serv)`; `pilar_birrotulado(sec, L, e1)`; `amostra(...)` para Monte Carlo; `acoes(Sk)` e `beta(...)`.

## 20. Entregáveis típicos

- Memória de cálculo (Word ou Docs) com: dados, hipóteses, combinações, dimensionamento ELU, verificações ELS, detalhamento resumido, e — se pedido — anexo de confiabilidade (tabela μR, σR, β).
- Planilha Excel com fórmulas vivas para rotinas repetitivas.
- Material de aula: mesma sequência, com exemplo numérico e "por que" de cada coeficiente (γc = 1,4 cobre a dispersão do concreto, que é a maior; γs = 1,15 porque o aço é industrial e pouco disperso — exatamente o que a tese mostra).

## Apêndice — confiab_ca.py

```python
"""
confiab_ca.py — Análise não-linear e de confiabilidade de vigas e pilares de concreto armado
Baseado em: REAL, M. V. (2000). Tese de doutorado PPGEC/UFRGS (modelo Darwin/CEB-FIP 1990 + Monte Carlo).
Simplificação adotada aqui: modelo de fibras (seção plana) em vez de EF de estado plano de tensão.
Unidades: kN, cm (tensões em kN/cm²; 1 kN/cm² = 10 MPa).
"""
import numpy as np

# ---------------------------------------------------------------- materiais
def props_concreto(fc, Vfc=0.15):
    """Propriedades derivadas (CEB-FIP 90, como na tese). fc = resistência média da simulação."""
    fck = fc * (1 - 1.645 * Vfc)
    Eco = 2150.0 * fc ** (1 / 3)                 # módulo tangente na origem
    fct = 0.14 * max(fck, 0.1) ** (2 / 3)        # tração média
    n = 4.81 * max(fck, 0.1) ** (-0.66)          # ductilidade pós-pico: eps_cu = n*eps_c1
    return dict(fc=fc, Eco=Eco, fct=fct, n=n, ec1=0.0022, ectu=0.002)

def sig_concreto(eps, c, tension_stiffening=True):
    """Tensão no concreto (compressão negativa). Curva CEB-FIP 90 + ramo pós-pico linear até 0,2fc em n*ec1."""
    fc, Eco, fct, n, ec1 = c["fc"], c["Eco"], c["fct"], c["n"], c["ec1"]
    s = np.zeros_like(eps)
    # compressão ascendente
    m = (eps < 0) & (-eps <= ec1)
    eta = -eps[m] / ec1
    k = Eco / (fc / ec1)
    s[m] = -fc * (k * eta - eta**2) / (1 + (k - 2) * eta)
    # pós-pico (strain-softening), mantém 0,2fc após eps_cu
    m = (eps < 0) & (-eps > ec1)
    ecu = n * ec1
    r = np.clip((-eps[m] - ec1) / (ecu - ec1), 0, 1)
    s[m] = -fc * (1 - 0.8 * r)
    # tração
    ect_f = 0.00015
    m = (eps > 0) & (eps <= ect_f)
    e = eps[m]
    e09 = 0.9 * fct / Eco
    s[m] = np.where(e <= e09, Eco * e, 0.9 * fct + 0.1 * fct * (e - e09) / (ect_f - e09))
    if tension_stiffening:
        m = (eps > ect_f) & (eps < c["ectu"])
        s[m] = 0.6 * fct * (1 - eps[m] / c["ectu"])
    return s

def sig_aco(eps, fy, Es=20000.0, Es2_rel=0.0):
    """Bilinear (tipo A: Es2=0; tipo B: Es2 = 5% Es)."""
    ey = fy / Es
    return np.where(np.abs(eps) <= ey, Es * eps,
                    np.sign(eps) * (fy + Es2_rel * Es * (np.abs(eps) - ey)))

# ---------------------------------------------------------------- seção retangular (fibras)
class Secao:
    def __init__(self, b, h, barras, conc, fy, Es=20000.0, Es2_rel=0.0, nfib=120, ts=True):
        """barras: lista de (y_desde_topo, As). Curvatura positiva comprime o topo."""
        self.b, self.h = b, h
        self.yc = (np.arange(nfib) + 0.5) * h / nfib      # profundidade da fibra a partir do topo
        self.Ac = b * h / nfib
        self.ys = np.array([y for y, _ in barras]); self.As = np.array([a for _, a in barras])
        self.c, self.fy, self.Es, self.Es2 = conc, fy, Es, Es2_rel
        self.ts = ts

    def esforcos(self, e0, k):
        """e0 = deformação no centro (y=h/2), k = curvatura. Retorna N (compressão negativa) e M.
        e0 pode ser escalar ou vetor (avaliação vetorizada)."""
        e0 = np.asarray(e0, dtype=float); esc = e0.ndim == 0
        e0 = np.atleast_1d(e0)[:, None]
        yc = self.yc - self.h / 2; ys = self.ys - self.h / 2
        ec = e0 + k * yc[None, :]          # topo (yc<0) comprime para k>0
        es = e0 + k * ys[None, :]
        sc = sig_concreto(ec, self.c, self.ts); ss = sig_aco(es, self.fy, self.Es, self.Es2)
        N = sc.sum(1) * self.Ac + (ss * self.As).sum(1)
        M = (sc * yc).sum(1) * self.Ac + (ss * self.As * ys).sum(1)
        return (N[0], M[0]) if esc else (N, M)

    def M_de_k(self, k, N=0.0):
        """Equilíbrio axial; retorna M para curvatura k e força normal N (compressão < 0).
        N(e0) não é monotônica (amolecimento do concreto): usa a raiz de menor encurtamento,
        varrendo e0 de +0,1 para baixo até a primeira troca de sinal, depois bissecção."""
        grid = np.linspace(0.1, -0.02, 241)
        f = self.esforcos(grid, k)[0] - N
        idx = np.where(np.sign(f[:-1]) != np.sign(f[1:]))[0]
        if len(idx) == 0:
            return -np.inf                                   # sem equilíbrio: seção esgotada
        i = idx[0]
        hi, lo = grid[i], grid[i + 1]
        flo = f[i + 1]
        for _ in range(22):
            mid = 0.5 * (lo + hi); fm = self.esforcos(mid, k)[0] - N
            if (fm > 0) == (flo > 0): lo, flo = mid, fm
            else: hi = mid
        return self.esforcos(0.5 * (lo + hi), k)[1]

    def curva_Mk(self, N=0.0, kmax=None, npts=80):
        kmax = kmax or 0.05 / self.h
        ks = np.concatenate([[0], np.geomspace(kmax * 1e-4, kmax, npts)])
        Ms = np.array([self.M_de_k(k, N) for k in ks])
        return ks, Ms

# ---------------------------------------------------------------- viga biapoiada, carga distribuída
def viga_biapoiada(sec, L, p_serv=None, npts=80):
    """Retorna carga de ruptura pu (kN/m) = 8 Mmax/L² e, se p_serv, a flecha central (cm) sob p_serv (kN/m)."""
    ks, Ms = sec.curva_Mk(0.0, npts=npts)
    ipk = int(np.argmax(Ms)); Mu = Ms[ipk]
    pu = 8 * Mu / L**2 * 100            # kN/cm -> kN/m
    out = {"pu": pu, "Mu": Mu}
    if p_serv is not None:
        p = p_serv / 100.0
        x = np.linspace(0, L / 2, 101)
        Mx = p * x * (L - x) / 2
        kx = np.interp(Mx, Ms[:ipk + 1], ks[:ipk + 1])  # ramo ascendente
        mbar = x / 2                                       # momento virtual (carga unitária no meio)
        out["flecha"] = 2 * np.trapezoid(kx * mbar, x)
    return out

# ---------------------------------------------------------------- pilar birrotulado, excentricidades iguais
def pilar_birrotulado(sec, L, e1, nseg=40, tol=1e-4):
    """Carga de ruptura (kN) com efeitos de 2ª ordem por integração de curvaturas (método geral simplificado)."""
    x = np.linspace(0, L, nseg + 1)

    def converge(P):
        ks, Ms = sec.curva_Mk(-P, npts=50)
        ipk = int(np.argmax(Ms)); Mmax = Ms[ipk]
        y = np.zeros_like(x)
        for _ in range(100):
            M = P * (e1 + y)
            if M.max() > Mmax: return False, None
            k = np.interp(M, Ms[:ipk + 1], ks[:ipk + 1])
            # integra y'' = -k com y(0)=y(L)=0
            th = np.concatenate([[0], np.cumsum((k[1:] + k[:-1]) / 2 * np.diff(x))])
            yy = np.concatenate([[0], np.cumsum((th[1:] + th[:-1]) / 2 * np.diff(x))])
            ynew = -(yy - yy[-1] * x / L)
            if np.abs(ynew - y).max() < tol: return True, ynew.max()
            y = ynew
        return False, None

    lo, hi = 0.0, sec.b * sec.h * sec.c["fc"] + sec.As.sum() * sec.fy
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        ok, _ = converge(mid)
        if ok: lo = mid
        else: hi = mid
        if hi - lo < 0.002 * hi: break
    return lo

# ---------------------------------------------------------------- Monte Carlo e confiabilidade
def normal_trunc(rng, size, lim=2.325):
    z = rng.standard_normal(size)
    return np.clip(z, -lim, lim)            # tese limita a ±2,325σ (98%)

def media_de_caracteristico(Xk, V, quantil_inferior=True):
    """Resistências: Xk = μ(1-1,645V). Ações: Xk = μ(1+1,645V)."""
    return Xk / (1 - 1.645 * V) if quantil_inferior else Xk / (1 + 1.645 * V)

def beta(muR, sR, muS, sS):
    from math import erf, sqrt
    b = (muR - muS) / np.hypot(sR, sS)
    Pf = 0.5 * (1 + erf(-b / sqrt(2)))
    return b, Pf

def acoes(Sk, frac_G=0.75, VG=0.10, VQ=0.40):
    muG = media_de_caracteristico(frac_G * Sk, VG, False); muQ = media_de_caracteristico((1 - frac_G) * Sk, VQ, False)
    return muG + muQ, np.hypot(VG * muG, VQ * muQ)

# ---------------------------------------------------------------- geração das propriedades aleatórias (cap. 6 da tese)
RHO_CT, RHO_TE, RHO_CE = 0.80, 0.70, 0.90       # correlações fc-fct, fct-Ec, fc-Ec (Mirza & MacGregor)

def amostra_concreto(rng, fcm, Vfc=0.15):
    """fc, fct, Ec correlacionados (Cholesky), campo perfeitamente correlacionado ao longo da peça."""
    V = np.array([Vfc, 1.2 * Vfc, Vfc])
    R = np.array([[1, RHO_CT, RHO_CE], [RHO_CT, 1, RHO_TE], [RHO_CE, RHO_TE, 1]])
    L = np.linalg.cholesky(R * np.outer(V, V))
    a = L @ normal_trunc(rng, 3)
    fck_pop = fcm * (1 - 1.645 * Vfc)
    c = props_concreto(fcm, Vfc)
    c["fc"] = fcm * (1 + a[0]); c["fct"] = c["fct"] * (1 + a[1]); c["Eco"] = c["Eco"] * (1 + a[2])
    c["n"] = 4.81 * fck_pop ** (-0.66)
    return c

def amostra(rng, fcm, fym, Vfc=0.15, Vfy=0.05, Esm=20000.0, VEs=0.025, b=None, h=None, sd_geo=0.5):
    z = normal_trunc(rng, 4)
    return dict(conc=amostra_concreto(rng, fcm, Vfc),
                fy=fym * (1 + Vfy * z[0]), Es=Esm * (1 + VEs * z[1]),
                b=b + sd_geo * z[2], h=h + sd_geo * z[3])
```

---

# Parte C — Método dos Elementos Finitos: simular e verificar sistemas estruturais

Postura: o MEF entra quando a pergunta não cabe numa conta de mão confiável (hiperestaticidade, 2ª ordem, rigidez de ligação, região D) ou para auditar um software. Sempre validar o modelo com um caso de solução conhecida antes de usar o número no projeto.

## 21. Método dos Elementos Finitos (MEF) — simular e verificar sistemas estruturais

### 21.1 Quando usar MEF (e quando não)
- **Usar:** verificar um cálculo manual ou de software comercial (TQS, Eberick, SAP2000); pórticos com 2ª ordem global (γz, P-Δ); pilares esbeltos pelo método geral (λ > 90 obrigatório considerar fluência; λ > 140 método geral obrigatório — NBR 6118 15.8); flambagem; ligações semirrígidas (molas rotacionais Rsec da seção 10.9); vigas/estacas sobre base elástica (molas de Winkler); regiões D (consolo, dente Gerber, aberturas, blocos) para orientar o modelo de bielas e tirantes; protensão como cargas equivalentes (u = 8Pf/L², forças de ancoragem).
- **Não substituir o dimensionamento normativo:** MEF dá esforços/tensões; o ELU/ELS continua pelas seções 8–12 (protendido) e 15–16 (CA). Em regiões D, a tensão elástica serve para posicionar bielas/tirantes, não para dimensionar direto (pico de tensão em canto reentrante é singularidade).
- Sempre conferir o MEF com uma conta de mão de ordem de grandeza (pl²/8, Pcr de Euler, reações).

### 21.2 Formulação (resumo para ensino e auditoria)
- **Passos:** discretizar → funções de forma N(x) → B = ∂N → ke = ∫Bᵀ D B dV → transformar (ke,glob = Tᵀ ke T, T ortogonal com cossenos diretores) → montar K = Σ ke → condições de contorno → resolver K d = F → recuperar esforços/tensões no elemento.
- **Viga de Euler-Bernoulli (2 nós, v e θ por nó):** funções de Hermite
  N1 = 1 − 3x²/L² + 2x³/L³; N2 = x − 2x²/L + x³/L²; N3 = 3x²/L² − 2x³/L³; N4 = −x²/L + x³/L².
  k = EI/L³·[[12, 6L, −12, 6L], [6L, 4L², −6L, 2L²], [−12, −6L, 12, −6L], [6L, 2L², −6L, 4L²]]. Pórtico plano soma EA/L nos gdl axiais (6×6).
  Exata nos nós para cargas nodais; carga distribuída entra como forças nodais equivalentes (qL/2, ±qL²/12) e o esforço do elemento desconta essa parcela.
- **Matriz geométrica (NLG):** da energia ½∫P(v')²dx → kg = P/(30L)·[[36, 3L, −36, 3L], [3L, 4L², −3L, −L²], [−36, −3L, 36, −3L], [3L, −L², −3L, 4L²]] (Gonçalves, eq. 4.2.20, escreve a mesma matriz como P·[1,2/L, 0,1, −1,2/L, 0,1; …; 4L/30, −L/30 …]). Compressão reduz a rigidez: (K + Kg)d = F.
- **Flambagem linear:** det(K + λ·Kg) = 0 → λcr = fator de carga crítica. 2 elementos já dão Pcr com erro < 1 %.
- **Timoshenko:** usar quando L/h < ~4 (vigas-parede, consolos em barra); inclui GA·κs (κs = 5/6 retangular). Em elemento de baixa ordem, integração reduzida no cisalhamento para evitar travamento (shear locking).
- **Estado plano (regiões D):** CST (deformação constante — ruim em flexão), Q4 bilinear (2×2 Gauss; rígido em flexão se houver só 1 elemento na altura), Q8/Q9 (preferível). Concreto: E = Ecs, ν = 0,2 (NBR 8.2.9).
- **Placas (lajes):** Kirchhoff (DKT) para delgadas; Mindlin/MITC4 para espessas. Comparar com tabelas de Bares/Czerny. Lajes: rigidez 0,3·EciIc na análise global de 2ª ordem (NBR 15.7.3).
- **Integração de Gauss:** n pontos integram exatamente polinômio de grau 2n − 1. Integração reduzida → risco de modos espúrios (hourglass). Fundamentos completos (forma fraca, taxas de convergência, isoparamétrico, modal, Newmark): seção 23.
- **Convergência:** refinamento h (mais elementos) ou p (maior grau). Teste da malha: refinar até a grandeza de interesse variar < 2–5 %. Não perseguir convergência em singularidade (carga pontual, canto vivo, apoio pontual) — ler a tensão a uma distância ~h/2 ou integrar a resultante.
- **Patch test e equilíbrio:** soma das reações = soma das cargas; simetria de K; deslocamento de corpo rígido sem tensão.

### 21.3 Não linearidades em concreto armado
- **NLG (2ª ordem):** P-Δ global por Kg ou iteração; NLG local por discretizar o pilar (≥ 4–10 elementos) com Kg.
- **NLF:** concreto parábola-retângulo (NBR 8.2.10.1: εc2 = 2 ‰, εcu = 3,5 ‰ até C50; C55–C90 com as fórmulas de n, εc2, εcu); aço bilinear Es = 210 GPa. Para análise de esforços usar **1,1·fcd** no lugar de 0,85·fcd e N = NRd/γf3 (γf3 = 1,1) — NBR 15.3.1; o resultado volta multiplicado por γf3 e é comparado com MRd (0,85·fcd).
- **Fluência:** multiplicar as deformações do diagrama σ-ε do concreto por (1 + φ) (NBR 15.8.4), ou excentricidade adicional ecc = (Msg/Nsg + ea)·(2,718^(φNsg/(Ne − Nsg)) − 1), Ne = 10·Eci·Ic/le².
- **Algoritmo de rigidez secante (Eboli/Gonçalves 2017):** (1) análise com Kg (N constante); (2) em cada elemento, pela curva M-κ da seção para o N atuante, achar κ que equilibra M e fazer EIsec = M/κ; (3) remontar K + Kg e repetir até ΔM < 0,1 kN·m. Se M passar do máximo da curva M-κ → sem equilíbrio = instabilidade/esgotamento.
- **Alternativa aproximada para pórticos (NBR 15.7.3):** lajes 0,3·EciIc; vigas 0,4·EciIc (As' ≠ As) ou 0,5·EciIc (As' = As); pilares 0,8·EciIc; ou 0,7·EciIc em vigas e pilares se γz < 1,3. Conferir na NBR 6118:2023.
- **Solução não linear geral:** Newton-Raphson (tangente), Newton modificado, controle de deslocamento ou arc-length (passa pelo pico/pós-pico). Critério: norma do resíduo e do incremento < 10⁻⁴–10⁻⁶.

### 21.4 Resultados de referência (Gonçalves 2017) — usar como teste de validação
- **Caso de verificação:** pilar biapoiado 100×25 cm, C20, CA-50, As = 49,09 cm² (10Ø25, ρ = 1,96 %), le = 3,608 m (λ = 50), Nd = 3650 kN com M1d,mín = Nd(0,015 + 0,03h) = 82,1 kN·m nas duas pontas, mesmo sentido (curvatura simples — o caso crítico).
  - Método geral (PCALC): Md,tot = 115,8 ≅ 117 kN·m. Mathcad/MEF: resistente 122,6 kN·m (FS 1,06; o PCALC desconta a área das barras).
- **Nmáx (kN) com momento mínimo, ρ = 1,96 %, 10 elementos:**

  | λ | Curv. aprox. | Rigidez aprox. | N,M,1/r | Método geral | MEF | Geral φ=2 | MEF φ=2 |
  |---|---|---|---|---|---|---|---|
  | 30 | 3775 | 3840 | 3890 | 3880 | 3932 | 3760 | 3812 |
  | 50 | 3370 | 3510 | 3680 | 3650 | 3703 | 3310 | 3352 |
  | 90 | 2060 | 2210 | 2490 | 2686 | 2725 | 1905 | 1923 |
  | 120 | 1380 | 1420 | 1272 | 1760 | 1799 | 1130 | 1128 |
  | 150 | 900 | 850 | 831 | 1210 | 1237 | 730 | 744 |

- **Conclusões do trabalho:**
  - MEF e método geral praticamente coincidem (diferença ~1–2 %, geral um pouco a favor da segurança); o MEF ganha por incluir a rotação nodal.
  - Pilar-padrão com rigidez aproximada e N,M,1/r **sem fluência** ficam **contra a segurança** comparados ao MEF com φ = 2 em pilares pouco armados (ρ = 0,39–0,97 %); com fluência ficam conservadores.
  - Instabilidade antes de esgotar a seção aparece com fluência, maior λ e menor ρ.
  - Fluência pesa muito: λ = 90, ρ = 1,96 % → Nmáx cai de 2725 para 1923 kN (−29 %) com φ = 2.

### 21.5 Ferramentas
- **Relação com a Parte B:** `confiab_ca.py` (seção 19) faz pilar birrotulado por integração de curvaturas com concreto CEB-FIP médio, unidades kN·cm e compressão negativa — serve para resistência média e β. O `mef.py` abaixo usa diagramas de cálculo da NBR (1,1fcd/0,85fcd), unidades kN·m e compressão positiva na seção — serve para verificação de projeto. Não misturar as convenções.
- **Motor de produção:** skill `mef-opensees-opsvis` (`ops_nd.py`: pórtico por JSON, combinações NBR, envoltória, figuras Opsvis, MRd por fibras). O `mef.py` desta seção fica para aula, auditoria e pilar isolado; os dois devem dar o mesmo resultado (conferido na Parte D).
- **Código próprio (21.7):** numpy/scipy, transparente para memória de cálculo e aula. Gravar como `mef.py` no workspace e importar.
- **OpenSeesPy** (`pip install openseespy`, testado e funcionando): para 3D, seção de fibras (`section Fiber` + `Concrete02`/`Steel02`), `dispBeamColumn`/`forceBeamColumn` com transformação `PDelta`/`Corotational`, cascas `ShellMITC4`, `quad`, análise com controle de deslocamento. Usar quando o modelo passar de pórtico plano/pilar isolado.
- **Comercial do usuário:** se o modelo veio do TQS/Eberick/SAP2000, reproduzir um trecho (pórtico, pilar crítico) no código próprio para auditar.

### 21.6 Roteiro para simular e verificar
1. Definir a pergunta (esforço? flecha? Pcr? γz? Nmáx do pilar?) e a hipótese de material (linear, rigidez reduzida da NBR 15.7.3, ou NLF com M-κ).
2. Modelo: geometria pelo eixo; vínculos reais (rótula, engaste, mola Rsec); trechos rígidos se nó for grande; unidades kN, m, kPa.
3. Cargas: combinações ELU/ELS da NBR 8681/6118; imperfeições (θ1 = 1/(100√H) global; M1d,mín local); protensão como carga equivalente.
4. Malha: pilar ≥ 10 elementos em 2ª ordem; vigas: nós nos pontos de carga; regiões D: ≥ 4–6 elementos na menor dimensão; estudo de convergência.
5. Rodar e conferir: equilíbrio das reações, deformada coerente, comparação com conta manual (21.8 traz os testes).
6. Pós-processar: esforços nas seções críticas → dimensionar pelas seções 8–12 e 15–16; regiões D → traçar bielas/tirantes; relatar fator de segurança λ = MRd/MSd.
7. Memória: hipóteses, malha, convergência, validação, limitações.

### 21.7 Código validado (gravar como mef.py)
```python
"""MEF compacto (numpy) — pórtico plano com P-Delta, flambagem, NLF de pilar CA, Q4 estado plano.
Unidades coerentes: kN, m, kPa (kN/m²)."""
import numpy as np
from scipy.linalg import eig
from scipy.optimize import brentq

# ---------- 1. Pórtico plano (3 gdl/nó: u, v, θ) ----------
def k_frame(E, A, I, L):
    a, b, c, d = E*A/L, 12*E*I/L**3, 6*E*I/L**2, E*I/L
    return np.array([[a,0,0,-a,0,0],[0,b,c,0,-b,c],[0,c,4*d,0,-c,2*d],
                     [-a,0,0,a,0,0],[0,-b,-c,0,b,-c],[0,c,2*d,0,-c,4*d]])

def kg_frame(N, L):
    """Matriz geométrica consistente (Hermite). N>0 tração, N<0 compressão."""
    f = N/(30*L)
    return f*np.array([[0,0,0,0,0,0],[0,36,3*L,0,-36,3*L],[0,3*L,4*L*L,0,-3*L,-L*L],
                       [0,0,0,0,0,0],[0,-36,-3*L,0,36,-3*L],[0,3*L,-L*L,0,-3*L,4*L*L]])

def T_frame(c, s):
    T = np.zeros((6, 6)); R = np.array([[c,s,0],[-s,c,0],[0,0,1]])
    T[:3,:3] = R; T[3:,3:] = R; return T

def q_equiv(q, L):
    """Carga distribuída transversal uniforme q (local) -> forças nodais equivalentes locais."""
    return np.array([0, q*L/2, q*L*L/12, 0, q*L/2, -q*L*L/12])

class Frame2D:
    def __init__(s, xy):
        s.xy = np.asarray(xy, float); s.n = len(s.xy); s.el = []
        s.F = np.zeros(3*s.n); s.fix = np.zeros(3*s.n, bool); s.springs = []
    def add(s, i, j, E, A, I, q=0.0):
        s.el.append(dict(i=i, j=j, E=E, A=A, I=I, q=q, N=0.0))
    def support(s, node, u=0, v=0, r=0):
        for k, f in enumerate((u, v, r)):
            if f: s.fix[3*node+k] = True
    def spring(s, node, dof, k):            # mola (ex.: ligação semirrígida, Winkler)
        s.springs.append((3*node+dof, k))
    def load(s, node, Fx=0, Fy=0, M=0):
        s.F[3*node:3*node+3] += (Fx, Fy, M)
    def _geo(s, e):
        d = s.xy[e['j']] - s.xy[e['i']]; L = np.hypot(*d); return L, d[0]/L, d[1]/L
    def _dofs(s, e):
        return np.r_[3*e['i']:3*e['i']+3, 3*e['j']:3*e['j']+3]
    def assemble(s):
        K = np.zeros((3*s.n, 3*s.n)); Kg = np.zeros_like(K); F = s.F.copy()
        for e in s.el:
            L, c, sn = s._geo(e); T = T_frame(c, sn); dof = s._dofs(e)
            K[np.ix_(dof, dof)] += T.T @ k_frame(e['E'], e['A'], e['I'], L) @ T
            Kg[np.ix_(dof, dof)] += T.T @ kg_frame(e['N'], L) @ T
            F[dof] += T.T @ q_equiv(e['q'], L)
        for dof, k in s.springs: K[dof, dof] += k
        return K, Kg, F
    def solve(s, pdelta=False, it=30, tol=1e-8):
        """Linear; pdelta=True itera N dos elementos até convergir (NLG aproximada)."""
        free = ~s.fix
        for _ in range(it if pdelta else 1):
            K, Kg, F = s.assemble()
            Kt = K + (Kg if pdelta else 0)
            d = np.zeros(3*s.n); d[free] = np.linalg.solve(Kt[np.ix_(free, free)], F[free])
            Nold = [e['N'] for e in s.el]; s.d = d; s.forces(pdelta)
            if pdelta and max(abs(e['N']-n0) for e, n0 in zip(s.el, Nold)) < tol*max(1, *map(abs, Nold)): break
        s.R = (K + (Kg if pdelta else 0)) @ d - F     # reações (só nos gdl fixos)
        return d
    def forces(s, geom=True):
        """Esforços locais [N_i,V_i,M_i,N_j,V_j,M_j] (convenção de extremidade de barra)."""
        for e in s.el:
            L, c, sn = s._geo(e); T = T_frame(c, sn); dl = T @ s.d[s._dofs(e)]
            f = (k_frame(e['E'], e['A'], e['I'], L) + (kg_frame(e['N'], L) if geom else 0)) @ dl - q_equiv(e['q'], L)
            e['f'] = f; e['N'] = -f[0]                # N>0 tração
    def buckling(s, nmodes=1):
        """Flambagem linear: (K + λ Kg) φ = 0 com N da análise linear. Retorna λcr."""
        s.solve(); K, Kg, _ = s.assemble(); fr = ~s.fix
        w = eig(-Kg[np.ix_(fr, fr)], K[np.ix_(fr, fr)], right=False)   # μ = 1/λ
        w = np.real(w[np.isfinite(w) & (np.abs(np.imag(w)) < 1e-9)]); w = 1/w[w > 1e-12]
        return np.sort(w)[:nmodes]

# ---------- 2. Seção retangular de CA (camadas) — NBR 6118 ----------
class RCSection:
    """b,h (m); camadas de aço [(As m², y m a partir do CG; + = topo)]; fck, fyk em MPa.
    psi=0.85 (ELU, fcd·0.85) ou 1.10 (análise NL: 1,1·fcd); phi = fluência (ε×(1+φ))."""
    def __init__(s, b, h, layers, fck, fyk=500, gc=1.4, gs=1.15, Es=210e3, psi=0.85, phi=0.0, nfib=200):
        s.b, s.h, s.layers, s.fck = b, h, layers, fck
        s.fcd = fck/gc; s.fyd = fyk/gs; s.Es = Es; s.psi = psi; s.phi = phi
        if fck <= 50: s.n, s.ec2, s.ecu = 2.0, 2.0e-3, 3.5e-3
        else:
            s.n = 1.4 + 23.4*((90-fck)/100)**4; s.ec2 = (2.0 + 0.085*(fck-50)**0.53)*1e-3
            s.ecu = (2.6 + 35*((90-fck)/100)**4)*1e-3
        s.y = np.linspace(-h/2, h/2, nfib+1); s.y = 0.5*(s.y[1:]+s.y[:-1]); s.dA = b*h/nfib
    def sc(s, e):        # tensão no concreto (MPa, compressão +) para encurtamento e>0
        e = np.asarray(e)/(1+s.phi); sig = np.where(e <= 0, 0.0,
            np.where(e < s.ec2, s.psi*s.fcd*(1-(1-e/s.ec2)**s.n), s.psi*s.fcd))
        return sig
    def ss(s, e):        # aço bilinear (MPa), e>0 encurtamento
        return np.clip(s.Es*e, -s.fyd, s.fyd)
    def NM(s, e0, k):    # e0 = encurtamento no CG; k = curvatura (topo comprimido +). Retorna N (kN, compr +), M (kN·m)
        e = e0 + k*s.y
        Nc = np.sum(s.sc(e))*s.dA*1e3; Mc = np.sum(s.sc(e)*s.y)*s.dA*1e3
        Ns = sum(As*(s.ss(e0+k*y) - (s.sc(e0+k*y) if e0+k*y > 0 else 0))*1e3 for As, y in s.layers)  # desconta concreto deslocado
        Ms = sum(As*(s.ss(e0+k*y) - (s.sc(e0+k*y) if e0+k*y > 0 else 0))*1e3*y for As, y in s.layers)
        return Nc+Ns, Mc+Ms
    def e0_for(s, N, k):
        f = lambda e0: s.NM(e0, k)[0] - N
        lo, hi = -0.02, 0.0035*(1+s.phi)*3
        return brentq(f, lo, hi)
    def M_kappa(s, N, kmax=None, npts=120):
        kmax = kmax or 0.05/s.h*(1+s.phi)
        ks = np.linspace(1e-7, kmax, npts); Ms = []
        for k in ks:
            try: Ms.append(s.NM(s.e0_for(N, k), k)[1])
            except ValueError: Ms.append(np.nan)
        Ms = np.array(Ms); i = np.nanargmax(Ms)
        return ks[:i+1], Ms[:i+1]                    # ramo ascendente até Mmax
    def EI_sec(s, N, M, curve):
        ks, Ms = curve; M = abs(M)
        if M >= Ms[-1]: return None                  # sem equilíbrio: esgotou a seção
        k = np.interp(M, Ms, ks); return M/k if k > 0 else Ms[1]/ks[1]

# ---------- 3. Pilar biapoiado — método geral via MEF (NLF + NLG), algoritmo Eboli/Gonçalves (2017) ----------
def pilar_nl(sec, le, Nd, M1_top, M1_base, nel=10, gf3=1.1, tol=0.1, it=100, Ec=None):
    """Nd>0 compressão (kN). Análise com N=Nd/γf3 e M=M1/γf3 sobre M-κ com 1,1fcd; resultado ×γf3.
    Retorna dict (Mmax_total_d, flecha, convergiu)."""
    N = Nd/gf3; xs = np.linspace(0, le, nel+1)
    fr = Frame2D(np.c_[np.zeros(nel+1), xs])
    A = sec.b*sec.h; I0 = sec.b*sec.h**3/12; Ec = Ec or 5600*np.sqrt(sec.fck)*1e3   # só chute inicial; o EI é recalculado pela M-κ
    for i in range(nel): fr.add(i, i+1, Ec, A, I0)
    fr.support(0, u=1, v=1); fr.support(nel, u=1)
    fr.load(nel, Fy=-N); fr.load(0, M=M1_base/gf3); fr.load(nel, M=-M1_top/gf3)   # momentos de mesmo sentido → curvatura simples
    curve = sec.M_kappa(N); Mprev = None
    for k in range(it):
        for e in fr.el: e['N'] = -N                 # N constante: Kg fixa (como no trabalho)
        K, Kg, F = fr.assemble(); free = ~fr.fix
        d = np.zeros(3*fr.n); d[free] = np.linalg.solve((K+Kg)[np.ix_(free, free)], F[free]); fr.d = d
        fr.forces(); Mel = np.array([max(abs(e['f'][2]), abs(e['f'][5])) for e in fr.el])
        if Mprev is not None and np.max(abs(Mel-Mprev)) < tol: return dict(M=Mel.max()*gf3, u=abs(d[0::3]).max(), ok=True, it=k)
        Mprev = Mel
        for e, M in zip(fr.el, Mel):
            EI = sec.EI_sec(N, M, curve)
            if EI is None: return dict(M=np.inf, u=np.inf, ok=False, it=k)
            e['I'] = EI/Ec
    return dict(M=Mel.max()*gf3, u=abs(d[0::3]).max(), ok=False, it=it)

# ---------- 4. Q4 estado plano de tensões (regiões D: consolos, dentes, aberturas) ----------
def q4_k(xy, E, nu, t):
    D = E/(1-nu**2)*np.array([[1,nu,0],[nu,1,0],[0,0,(1-nu)/2]]); K = np.zeros((8, 8)); g = 1/np.sqrt(3)
    for xi in (-g, g):
        for et in (-g, g):
            dN = 0.25*np.array([[-(1-et), (1-et), (1+et), -(1+et)], [-(1-xi), -(1+xi), (1+xi), (1-xi)]])
            J = dN @ xy; dNx = np.linalg.solve(J, dN); B = np.zeros((3, 8))
            B[0, 0::2] = dNx[0]; B[1, 1::2] = dNx[1]; B[2, 0::2] = dNx[1]; B[2, 1::2] = dNx[0]
            K += B.T @ D @ B * np.linalg.det(J) * t
    return K, D

def q4_mesh_beam(L, H, nx, ny, E, nu, t):
    xs, ys = np.linspace(0, L, nx+1), np.linspace(0, H, ny+1)
    XY = np.array([[x, y] for y in ys for x in xs]); nid = lambda i, j: j*(nx+1)+i
    els = [[nid(i,j), nid(i+1,j), nid(i+1,j+1), nid(i,j+1)] for j in range(ny) for i in range(nx)]
    K = np.zeros((2*len(XY),)*2)
    for el in els:
        ke, D = q4_k(XY[el], E, nu, t); dof = np.ravel([[2*n, 2*n+1] for n in el])
        K[np.ix_(dof, dof)] += ke
    return XY, els, K, nid

def MRd(sec, N, npts=400):
    """Momento resistente ELU (psi=0,85) para N (kN, compressão +): varre curvaturas respeitando
    εcu no topo, εc2 no ponto C (domínio 5) e 10‰ no aço."""
    best = 0.0; h = sec.h; yC = h/2 - h*(sec.ecu-sec.ec2)/sec.ecu; ys = min(y for _, y in sec.layers)
    for k in np.linspace(1e-6, (sec.ecu+0.010)/(h/2-ys)*1.0, npts):
        try: e0 = sec.e0_for(N, k)
        except ValueError: continue
        if e0+k*h/2 > sec.ecu+1e-9 or e0+k*yC > sec.ec2+1e-9 or e0+k*ys < -0.010-1e-9: continue
        best = max(best, sec.NM(e0, k)[1])
    return best   # resolução ~0,3 %: aumentar npts se o caso estiver no limite
```

### 21.8 Testes de validação (rodados; repetir após qualquer alteração no código)
| Teste | MEF (código acima) | Referência |
|---|---|---|
| Viga biapoiada, q = 20 kN/m, L = 6 m, 8 elementos: flecha | 5,400 mm | 5qL⁴/384EI = 5,400 mm |
| Mesma viga: M no meio / reações | 90,0 kN·m / 60 kN | qL²/8 = 90 / qL/2 = 60 |
| Euler biapoiado, 2 / 4 / 10 elementos: Pcr,MEF/Pcr | 1,0075 / 1,0005 / 1,00001 | 1 |
| Balanço: Pcr,MEF/(π²EI/4L²) | 1,000001 | 1 |
| Balanço com P = 0,5·Pcr, P-Δ: amplificação do topo | 1,986 | ≈ 1/(1 − P/Pcr) = 2,0 |
| Q4 40×10, balanço 2,0×0,5 m: flecha | 4,42 mm | Timoshenko 4,46 mm (−0,8 %) |
| Pilar de verificação Gonçalves (21.4), d' = 5 cm | Md,tot = 117,1 kN·m; MRd = 118,0 | 115,8 ≅ 117 kN·m |
| Nmáx ρ = 1,96 %, λ = 30 / 50 / 90 / 120 (d' = 5 cm) | 3886 / 3657 / 2633 / 1729 kN | MEF Gonçalves 3932 / 3703 / 2725 / 1799 |
| Nmáx λ = 90, φ = 2 | 1857 kN | 1923 kN |

- O pilar de referência não informa o cobrimento d'. Com d' = 5 cm o código fica 1–4 % abaixo de Gonçalves (a favor da segurança); com d' = 4 cm fica 0,5–12 % **acima** (λ = 90, φ = 2: 2147 contra 1923). **O resultado de pilar esbelto é sensível a d': usar sempre o d' real do detalhamento.**
- Uso típico do pilar:
  ```python
  As = 49.09e-4; lay = [(As/2, 0.075), (As/2, -0.075)]          # (área m², y a partir do CG)
  nl  = RCSection(1.0, 0.25, lay, fck=20, psi=1.10, phi=0.0)     # análise: 1,1·fcd
  elu = RCSection(1.0, 0.25, lay, fck=20, psi=0.85)              # resistência: 0,85·fcd
  r = pilar_nl(nl, le=3.608, Nd=3650, M1_top=82.1, M1_base=82.1)
  print(r['M'], MRd(elu, 3650), r['ok'])                         # Md,tot ≤ MRd e convergiu → ok
  ```
- Convenções do código: N > 0 tração nos elementos de pórtico; em `RCSection`/`pilar_nl`, compressão positiva. `e['f']` = esforços de extremidade em eixos locais [Ni, Vi, Mi, Nj, Vj, Mj] (sinal de extremidade de barra, não de diagrama: o momento no meio da biapoiada sai −90 = +90 de diagrama).

### 21.9 Limitações conhecidas do código (declarar na memória)
- `pilar_nl`: seção retangular, flexão composta reta, N constante, biapoiado; EIsec de cada elemento tomado pelo **maior** momento das duas pontas (conservador); sem resistência à tração do concreto (sem tension stiffening). Para pilar em balanço, flexão oblíqua ou seção qualquer → OpenSeesPy com seção de fibras.
- `MRd`: varredura discreta (erro ~0,3 %); aumentar `npts` se o caso estiver no limite.
- `Frame2D.solve(pdelta=True)`: P-Δ por iteração de N com Kg consistente — não é grandes rotações (para isso, Corotational no OpenSeesPy).
- Q4: rígido em flexão com poucos elementos na altura; usar ≥ 6–10 na altura ou Q8.
- Valores normativos com base NBR 6118:2014 (Gonçalves): conferir itens 15.3.1, 15.7.3, 15.8 na NBR 6118:2023.

### 21.10 Armadilhas de MEF
- Confiar em pico de tensão de singularidade; não fazer estudo de malha.
- Unidades misturadas (kN·m com MPa); E em MPa com A em m².
- Pilar com 1 elemento em análise de 2ª ordem (perde a NLG local).
- Esquecer as imperfeições (o modelo perfeito não flamba por flexão sem carga lateral).
- Usar rigidez bruta EcIc em 2ª ordem (superestima Nmáx); usar 0,85·fcd em vez de 1,1·fcd na análise de esforços.
- Momentos de extremidade com sentidos opostos (curvatura dupla) quando o caso crítico é curvatura simples.
- Ignorar fluência em λ > 90.
- Comparar tensões de membrana de casca com σ = M/W sem conferir o eixo local do elemento.

## 22. Blocos sobre estacas — bielas e tirantes (Andrade 1989) e MEF 3D (Oliveira, Barros & Giongo 2014)

Fonte: Oliveira, D. S.; Barros, R.; Giongo, J. S. *Blocos de concreto armado sobre seis estacas: simulação numérica e dimensionamento pelo método de bielas e tirantes*. Revista IBRACON de Estruturas e Materiais (RIEM), v. 7, n. 1, fev. 2014 (base NBR 6118:2007). Critérios de Andrade (1989, SET-EESC-USP), que generalizam Blévot & Frémy para n estacas e pilar retangular. Complementa a memória do Bloco B39 (método Blévot & Frémy) e as planilhas de ferragem de blocos do usuário.

### 22.1 Método analítico (Andrade 1989)
- **Origem das bielas no pilar:** dividir a seção do pilar em tantas partes quantas forem as estacas e partir cada biela do **centro da parte ligada àquela estaca** (não do centro do pilar). Bloco 2×3 (Fig. 1 do artigo): pilar bp (x, paralelo à linha de 3 estacas) × ap (y) dividido em 3 × 2 → pontos em (±bp/3, ±ap/4) para as estacas de canto e (0, ±ap/4) para as centrais. O MEF confirmou que as bielas acompanham o formato do pilar.
- **Ângulo:** θ = arctan(d / distância horizontal do ponto de origem ao eixo da estaca). Faixa recomendada 40° ≤ θ ≤ 55°; verificar com o θ da **biela mais abatida**. Na prática: biela mais abatida ≈ 40° para as demais ficarem ≤ 55° (no bloco do artigo as bielas das estacas centrais chegam a 58°: o limite superior não é atendido; o artigo aceita "se possível").
- **Tensão na biela junto ao pilar (eq. 1):** σcb,p = Fsd/(Ap·sen²θ) ≤ αp·0,85·fcd, com **αp = 2,6**.
- **Tensão na biela junto às estacas (eq. 2):** σcb,e = Fsd/(n·Ae·sen²θ) ≤ αe·0,85·fcd, com **αe = 1,0** (n = 6 no artigo; com reações desiguais usar Ri/(Ae·sen²θi) em cada estaca).
- **Tirante (eq. 3):** As = Rst/fyd. Reação uniforme R = Fsd/n; força horizontal da biela da estaca i: Hi = Ri·(distância horizontal)/d, decomposta nas direções x e y. Bloco 2×3: Rst,x = R·(sx − bp/3)/d por linha de estacas (2 linhas); Rst,y = R·(sy/2 − ap/4)/d por linha (3 linhas).
- **d:** do topo do bloco ao centro dos tirantes. No artigo, d = h − 14,5 cm (estaca embutida 10 cm, face inferior das barras 2 cm acima do topo da estaca, duas camadas Ø25 → centro médio a 12 + 2,5 = 14,5 cm do fundo). Esse valor reproduz exatamente as Tabelas 1 e 2.
- **Detalhamento:** armadura principal concentrada em faixas sobre as estacas com largura 1,2·D (NBR 6118:2007 item 22.5.4.1.1; 22.7.4.1.1 na 2014/2023 — conferir), formando a malha de tirantes x/y da Fig. 4. O artigo não verificou ancoragem (o MEF supôs aderência perfeita): **em projeto, verificar ancoragem e ganchos**.
- **Bloco rígido:** a altura atende aos critérios de bloco rígido do CEB-FIP Bol. 73 e da NBR 6118.

### 22.2 Como o artigo obteve Fcalc e As,calc (engenharia reversa, conferida)
- **Fcalc (força prevista, para comparar com o MEF) = αp·fck·Ap·sen²θ** — eq. 1 sem 0,85 e sem γc. Governa o nó do pilar; o nó das estacas (6·Ae·fck·sen²θ) fica acima em todos os blocos.
- **As,calc = Rst/fyk** (fy = 500 MPa sem γs), com R = Fcalc/6.
- Para projeto, aplicar 0,85·fcd e fyd: no B-4-30, Fsd,máx = 2,6·0,85·(30/1,4)·5005·sen²40,0° = **9 811 kN** (Fcalc/Fsd,máx = 1,4/0,85 = 1,65); nessa carga σcb,e = 14,0 ≤ 18,2 MPa; As,x = 38,1 cm² por linha; As,y = 23,4 cm² por linha.
- ⚠ **Tabela 1 × Tabela 2, bloco B-4-35-600:** a Tabela 1 dá pilar 144×36, mas Fcalc = 18 852 kN e As só batem com 143×35 (= 16 159·35/30). Com 144×36 daria 19 588 kN (+3,9 %). Provável erro de digitação na Tabela 1.

### 22.3 Dados do artigo (para replicar)
- **Geometria (Fig. 3):** bloco 480 × 300 × 145 cm; 6 estacas hélice contínua Ø60 em 2 linhas × 3; espaçamento 3D = 180 cm nas duas direções; 30 cm do plano tangente externo das estacas à face do bloco (60 cm do eixo). Estaca embutida 10 cm. Pilar com área ≈ 5 000 cm² e 3 % de armadura (Ø25, estribos Ø8 c/20).
- **Tabela 1 — parâmetros** (B-r-fck-k: r = relação dos lados do pilar; k = mola em kN/mm):

  | Bloco | bp (cm) | ap (cm) | h (cm) | fck (MPa) | k (kN/mm) | θ (°) |
  |---|---|---|---|---|---|---|
  | B-4-30-600 (referência) | 143 | 35 | 145 | 30 | 600 | 40 |
  | B-4-25-600 | 143 | 35 | 145 | 25 | 600 | 40 |
  | B-4-35-600 | 144 ⚠ | 36 ⚠ | 145 | 35 | 600 | 40 |
  | B-4-30-rig | 143 | 35 | 145 | 30 | rígido | 40 |
  | B-4-30-300 | 143 | 35 | 145 | 30 | 300 | 40 |
  | B-4-30-900 | 143 | 35 | 145 | 30 | 900 | 40 |
  | B-8-30-600 | 200 | 25 | 145 | 30 | 600 | 43 |
  | B-1-30-600 | 71 | 71 | 145 | 30 | 600 | 37 |

- **Tabela 2 — dimensionamento** (Ø25; x = 2 linhas de 3 estacas, y = 3 linhas de 2 estacas, Fig. 4):

  | Bloco | Fcalc (kN) | As,calc x / y (cm²) | n barras x / y | As,ef x / y (cm²) |
  |---|---|---|---|---|
  | B-4-30 (600, rig, 300, 900) | 16 159 | 54,66 / 33,56 | 12 / 7 | 58,90 / 34,36 |
  | B-4-25-600 | 13 466 | 45,55 / 27,96 | 10 / 6 | 49,09 / 29,45 |
  | B-4-35-600 | 18 852 | 63,76 / 39,15 | 13 / 8 | 63,81 / 39,27 |
  | B-8-30-600 | 18 005 | 52,14 / 38,53 | 11 / 8 | 54,00 / 39,27 |
  | B-1-30-600 | 14 342 | 57,33 / 26,49 | 12 / 6 | 58,90 / 29,45 |

- **Tabela 4 — MEF × analítico:**

  | Bloco | Fcalc (kN) | Fnum (kN) | Fnum/Fcalc |
  |---|---|---|---|
  | B-4-30-600 | 16 159 | 16 744 | 1,036 |
  | B-4-25-600 | 13 466 | 14 929 | 1,109 |
  | B-4-35-600 | 18 852 | 20 865 | 1,107 |
  | B-4-30-rig | 16 159 | 17 247 | 1,067 |
  | B-4-30-300 | 16 159 | 18 775 | 1,162 |
  | B-4-30-900 | 16 159 | 17 019 | 1,053 |
  | B-8-30-600 | 18 005 | 19 195 | 1,066 |
  | B-1-30-600 | 14 342 | 16 183 | 1,128 |

  O método de Andrade ficou sempre a favor da segurança (Fnum/Fcalc = 1,04–1,16) mesmo sem coeficientes de segurança.

### 22.4 Modelo MEF do artigo (receita para reproduzir em DIANA/ATENA/ABAQUS/OpenSees)
- **Elementos:** sólido CHX60 (hexaedro de 20 nós, quadrático); molas SP2TR só na vertical na base das estacas; 1/4 do bloco por simetria; malha mapeada ≤ 15 cm; estaca modelada com seção quadrada de mesma área (2 827,4 cm²).
- **Concreto do bloco:** total strain com fissuração distribuída; compressão parabólica; tração exponencial; redução por fissuração lateral e confinamento de Vecchio & Collins (1993); largura de banda de fissura = raiz cúbica do volume do elemento; Gc = 50·Gf (Feenstra & de Borst); β (retenção ao cisalhamento) = 0,2; ν = 0,2.
- **Tabela 3 (CEB-FIP MC90):**

  | fck (MPa) | 25 | 30 | 35 |
  |---|---|---|---|
  | Gf (N·mm/mm²) | 0,0699 | 0,0761 | 0,0847 |
  | Gc (N·mm/mm²) | 3,3472 | 3,8029 | 4,2362 |
  | Ec (MPa) | 29 180 | 31 008 | 32 643 |
  | fctm (MPa) | 2,6 | 2,9 | 3,2 |

  Conferido: Ec = 21 500·(fck/10)^(1/3) (o artigo usou fck, não fcm); fctm = 0,3·fck^(2/3); Gf ≈ 0,030·(fcm/10)^0,7 com fcm = fck + 8 (diâmetro máximo 16 mm).
- **Pilar e estacas:** elástico-linear (para forçar a ruptura no bloco). **Aço:** Von Mises elastoplástico perfeito, Es = 210 GPa, ν = 0,3, armadura embutida com aderência perfeita.
- **Solução:** deslocamento imposto no topo do pilar; Newton-Raphson regular; convergência em energia, tolerância 0,01.

### 22.5 Resultados e lições de projeto
- **Distribuição das reações (Fig. 7, E2 = estaca central da linha, E1 = estaca de canto):**
  - Apoio rígido: já na fase elástica E2 ≈ 24 % e E1 ≈ 13 % de F; perto da ruína E2 ≈ 34 % e E1 ≈ 8 %.
  - Molas 300–900 kN/mm: no início praticamente uniforme (≈ 16–18 %); com a fissuração as reações migram para as estacas próximas ao pilar (k = 300: E2 ≈ 21 %, E1 ≈ 14,5 % na ruína; k = 900: E2 chega a ≈ 25 %).
  - Quanto mais rígido o solo, mais desigual. **A hipótese de reações uniformes não vale em solo muito rígido (estaca em rocha):** fazer interação solo-estrutura ou dimensionar com as reações desiguais.
- **Resistência:** pouco sensível à rigidez do solo (o bloco redistribui esforços); k = 300 deu a maior (1,162). Mais rigidez → comportamento mais "serrilhado" e ruína com menor deslocamento.
- **Tirantes:** com apoio rígido o tirante central escoa enquanto os outros têm tensão baixa; solo mais deformável → tensões mais uniformes entre tirantes, mais próximo da treliça.
- **Seção do pilar:** pilar alongado distribui melhor as reações e as tensões nos tirantes; pilar quadrado concentra o tirante entre as estacas centrais e tem bielas mais abatidas. A resistência muda pouco: Fnum = 16 183 kN (quadrado), 16 744 kN (bp = 4ap) e 19 195 kN (bp = 8ap) — o artigo chama o ganho do pilar muito alongado de "pequeno", atribuído a bielas mais inclinadas para as estacas afastadas.
- **fck:** aumenta a resistência do bloco quase proporcionalmente, mas pouco altera a rigidez e a distribuição das reações.

### 22.6 Script de replicação (validado)
O código fica no fim desta seção (`blocos.py`): `bloco6_stm` (Andrade) e `bloco_6_estacas_mef` (MEF 3D elástico H8, 1/4 do bloco, estacas como molas distribuídas, pilar como pressão uniforme).

| Teste | Script | Artigo |
|---|---|---|
| Fcalc B-4-30 / B-4-25 / B-8-30 / B-1-30 (d = h − 14,5) | 16 159 / 13 466 / 18 005 / 14 342 kN | idem (erro < 0,05 %) |
| As,calc x/y B-4-30 | 54,62 / 33,54 cm² | 54,66 / 33,56 |
| θ B-8 / B-1 | 42,8° / 37,2° | 43° / 37° |
| Reações elásticas, apoio rígido, fuste 1,0 m (E2 / E1) | 24,9 % / 12,6 % | ≈ 24 % / 13 % (Fig. 7, início) |
| Reações elásticas, molas 900 / 600 / 300 kN/mm (E2 / E1) | 18,2/15,9 · 17,7/16,2 · 17,2/16,4 % | ≈ 17,5–18 / 16 % (Fig. 7, início) |
| Convergência de malha (15 → 10 cm) | variação < 0,1 ponto percentual | — |

- O comprimento do fuste no modelo do artigo não é informado; com apoio rígido o resultado depende dele (fuste 0,5 / 1,0 / 1,5 / 2,0 m → E2 = 27,7 / 24,9 / 23,2 / 22,1 %). Em projeto, usar o comprimento real da estaca e a rigidez axial EA/L em série com a mola do solo (recalque da estaca).
- O MEF do script é **elástico**: reproduz a distribuição inicial de reações e serve para decidir se a hipótese de reações uniformes é aceitável. A redistribuição pós-fissuração e a carga de ruína (Tabela 4) exigem análise não linear (total strain/fissuração distribuída) — usar DIANA/ATENA/ABAQUS ou OpenSeesPy (`stdBrick` + `ASDConcrete3D`, disponível na versão instalada) e validar contra a Tabela 4.
- Uso:
  ```python
  r = bloco6_stm(bp=143, ap=35, fck=30, d=130.5)              # força prevista (sem coeficientes), como o artigo
  r = bloco6_stm(143, 35, 30, d=130.5, Fsd=9000)               # projeto: σ ≤ α·0,85·fcd, As = Rst/fyd
  m = bloco_6_estacas_mef(1.43, 0.35, 1.45, E=31008e3, k_solo=600)   # % de F em E2 e E1
  ```
- Para outros arranjos (3, 4, 5, n estacas), aplicar a mesma regra: dividir o pilar em n partes, origem de cada biela no centróide da sua parte, θi pela distância horizontal até a estaca, tensões pelas eqs. 1–2 com a biela mais abatida, forças nos tirantes por equilíbrio do nó de cada estaca.

```python
"""Blocos sobre estacas: bielas e tirantes (Andrade 1989; Oliveira, Barros & Giongo 2014) + MEF 3D elástico H8.
STM em cm, kN, MPa. MEF em m, kN, kPa."""
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as spla

# ---------- 1. Bielas e tirantes — bloco 2x3 estacas (6), pilar bp (x, paralelo à linha de 3) x ap (y) ----------
def bloco6_stm(bp, ap, fck, d, sx=180, sy=180, D=60, fy=500, alpha_p=2.6, alpha_e=1.0,
               Fsd=None, gc=1.4, gs=1.15):
    """Fsd=None → força prevista sem coeficientes (como Fcalc do artigo: sem 0,85, sem γc, As com fyk).
    Fsd dado → verificação de projeto: σ ≤ α·0,85·fcd e As = Rst/fyd."""
    Ap, Ae = bp*ap, np.pi*D**2/4
    dx, dy = sx - bp/3, sy/2 - ap/4                 # estaca de canto → ponto (bp/3, ap/4) do pilar
    th = np.arctan(d/np.hypot(dx, dy)); th_c = np.arctan(d/dy)   # biela mais abatida; biela da estaca central
    s2 = np.sin(th)**2
    out = dict(theta=np.degrees(th), theta_central=np.degrees(th_c), Ap=Ap, Ae=Ae)
    if Fsd is None:
        fc = fck/10; f_y = fy/10; k = 1.0                       # kN/cm²
        out['F_pilar'] = alpha_p*fc*Ap*s2; out['F_estaca'] = alpha_e*fc*6*Ae*s2
        F = min(out['F_pilar'], out['F_estaca'])
    else:
        fcd = fck/gc/10; f_y = fy/gs/10; F = Fsd
        out['sig_pilar'] = F/(Ap*s2)*10; out['lim_pilar'] = alpha_p*0.85*fcd*10       # MPa
        out['sig_estaca'] = F/(6*Ae*s2)*10; out['lim_estaca'] = alpha_e*0.85*fcd*10
    R = F/6; out['F'] = F
    out['Rst_x'] = R*dx/d; out['Rst_y'] = R*dy/d                # por linha de estacas (x: 2 linhas; y: 3 linhas)
    out['Asx'] = out['Rst_x']/f_y; out['Asy'] = out['Rst_y']/f_y
    return out

# ---------- 2. MEF 3D elástico, hexaedro H8 (2x2x2 Gauss) ----------
def D_iso(E, nu):
    l = E*nu/((1+nu)*(1-2*nu)); m = E/(2*(1+nu)); D = np.zeros((6, 6))
    D[:3, :3] = l; D[range(3), range(3)] += 2*m; D[range(3, 6), range(3, 6)] = m; return D

_NAT = np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]])
def ke_h8(X, D):
    K = np.zeros((24, 24)); g = np.array([-1, 1])/np.sqrt(3); n = _NAT
    for a in g:
        for b in g:
            for c in g:
                dN = 0.125*n.T*np.array([(1+n[:,1]*b)*(1+n[:,2]*c), (1+n[:,0]*a)*(1+n[:,2]*c), (1+n[:,0]*a)*(1+n[:,1]*b)])
                J = dN @ X; dX = np.linalg.solve(J, dN); B = np.zeros((6, 24))
                B[0,0::3]=dX[0]; B[1,1::3]=dX[1]; B[2,2::3]=dX[2]
                B[3,0::3]=dX[1]; B[3,1::3]=dX[0]; B[4,1::3]=dX[2]; B[4,2::3]=dX[1]; B[5,0::3]=dX[2]; B[5,2::3]=dX[0]
                K += B.T @ D @ B * np.linalg.det(J)
    return K

def linhas(segs, h):
    """Coordenadas de malha passando por todos os limites de segmentos (alinha bordas de pilar/estaca)."""
    pts = set()
    for a, b in segs:
        m = max(1, int(np.ceil((b-a)/h - 1e-9))); pts.update(np.round(np.linspace(a, b, m+1), 6))
    return np.array(sorted(pts))

def trib(c, lo, hi):
    """Peso de área tributária 1D de cada nó da linha c dentro de [lo, hi]."""
    w = np.zeros(len(c))
    for i, x in enumerate(c):
        if lo-1e-9 <= x <= hi+1e-9:
            a = max(lo, (c[i-1]+x)/2 if i else x); b = min(hi, (c[i+1]+x)/2 if i < len(c)-1 else x); w[i] = max(b-a, 0)
    return w

def bloco_6_estacas_mef(bp, ap, h, E, nu=0.2, sx=1.8, sy=1.8, D=0.6, Lx=4.8, Ly=3.0,
                        k_solo=None, L_fuste=0.0, F=1000.0, h_el=0.15):
    """Modelo 1/4 (simetria x=0, y=0). Pilar = pressão uniforme no topo. Estaca = seção quadrada de mesma área,
    mola vertical distribuída na área: fuste EA/L em série com o solo k_solo (kN/mm; None = base rígida).
    Retorna % de F em cada estaca: E2 (central) e E1 (canto)."""
    a = np.sqrt(np.pi*D**2/4)/2
    xs = linhas([(0, a), (a, bp/2), (bp/2, sx-a), (sx-a, sx+a), (sx+a, Lx/2)], h_el)
    ys = linhas([(0, ap/2), (ap/2, sy/2-a), (sy/2-a, sy/2+a), (sy/2+a, Ly/2)], h_el)
    zs = linhas([(0, h)], h_el); nx, ny, nz = len(xs), len(ys), len(zs)
    nid = lambda i, j, k: (i*ny+j)*nz+k
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing='ij'); XYZ = np.c_[X.ravel(), Y.ravel(), Z.ravel()]
    Dm = D_iso(E, nu); r, c, v = [], [], []
    for i in range(nx-1):
        for j in range(ny-1):
            for k in range(nz-1):
                el = np.array([nid(i,j,k),nid(i+1,j,k),nid(i+1,j+1,k),nid(i,j+1,k),nid(i,j,k+1),nid(i+1,j,k+1),nid(i+1,j+1,k+1),nid(i,j+1,k+1)])
                ke = ke_h8(XYZ[el], Dm); dof = (3*el[:,None]+np.arange(3)).ravel()
                r.append(np.repeat(dof, 24)); c.append(np.tile(dof, 24)); v.append(ke.ravel())
    n = 3*len(XYZ); K = sp.coo_matrix((np.concatenate(v), (np.concatenate(r), np.concatenate(c))), shape=(n, n)).tocsr()
    f = np.zeros(n); wx, wy = trib(xs, 0, bp/2), trib(ys, 0, ap/2); p = (F/4)/(bp/2*ap/2)
    for i in np.nonzero(wx)[0]:
        for j in np.nonzero(wy)[0]: f[3*nid(i,j,nz-1)+2] -= p*wx[i]*wy[j]
    fixed = set(3*nid(0,j,k) for j in range(ny) for k in range(nz)) | set(3*nid(i,0,k)+1 for i in range(nx) for k in range(nz))
    Kd = np.zeros(n); grupos = {}
    for nome, (cx, cy, frac) in {'E2': (0.0, sy/2, 0.5), 'E1': (sx, sy/2, 1.0)}.items():
        A = (2*a)**2*frac
        kf = E*(2*a)**2/L_fuste if L_fuste > 0 else np.inf; ks = np.inf if k_solo is None else k_solo*1e3
        kt = None if np.isinf(kf) and np.isinf(ks) else frac/(1/kf + 1/ks)
        wx, wy = trib(xs, cx-a, cx+a), trib(ys, cy-a, cy+a); lst = []
        for i in np.nonzero(wx)[0]:
            for j in np.nonzero(wy)[0]:
                d = 3*nid(i,j,0)+2; w = wx[i]*wy[j]/A; lst.append((d, w))
                if kt is None: fixed.add(d)
                else: Kd[d] += kt*w
        grupos[nome] = (lst, kt, frac)
    K = K + sp.diags(Kd); free = np.setdiff1d(np.arange(n), list(fixed)); u = np.zeros(n)
    u[free] = spla.spsolve(K[free][:, free].tocsc(), f[free]); Rall = K @ u - f
    res = {}
    for nome, (lst, kt, frac) in grupos.items():
        Rq = sum(Rall[d] for d, _ in lst) if kt is None else -sum(kt*w*u[d] for d, w in lst)
        res[nome] = Rq/frac/F*100
    res['soma'] = 2*res['E2'] + 4*res['E1']; res['nos'] = len(XYZ)
    return res
```

## 23. Fundamentos do MEF, autovalores e dinâmica (apostila TM266 — DEMEC/UFPR)

Fonte: *Introdução ao Método dos Elementos Finitos*, apostila da disciplina TM266, DEMEC-UFPR (93 p., 7 capítulos; o PDF não traz o autor; notação e roteiro seguem Reddy, *An Introduction to the Finite Element Method*). Esta seção é a base teórica do núcleo MEF do software (`fem1d.py`, 23.7). As seções 21–22 aplicam essa base a concreto.

### 23.1 Formulação (caps. 2–4)
- **Da forma forte à forma fraca:** resíduo ponderado ∫w·R dx = 0 → integrar por partes. Isso divide as derivadas entre w e u (exige menos continuidade) e faz surgir os termos de contorno.
- **Variáveis primárias e secundárias:**
  - Primárias (u, v, θ) → condição **essencial**, imposta em u.
  - Secundárias (N, V, M, os coeficientes dos termos de contorno) → condição **natural**, entra em F.
  - Em cada ponto do contorno especifica-se uma ou outra de cada par, nunca as duas.
- **Funcional:** com B(·,·) bilinear simétrica, I(u) = ½B(u,u) − l(u) é a energia potencial total, e a solução minimiza I.
- **Métodos:**
  - Rayleigh-Ritz: minimiza I no espaço aproximado.
  - Galerkin: w = ψ (igual a Ritz quando B é simétrica).
  - Petrov-Galerkin: w ≠ ψ.
  - Também: mínimos quadrados e colocação (resíduo zero em pontos).
- **Funções de forma:** duas propriedades essenciais.
  - Delta de Kronecker ψi(xj) = δij: o grau de liberdade é o valor físico no nó.
  - Partição da unidade Σψi = 1: corpo rígido não gera deformação.
  - EDO de 2ª ordem (barra, calor) exige continuidade C0 → Lagrange. EDO de 4ª ordem (viga Euler-Bernoulli) exige C1 → Hermite (v, θ).
- **Montagem:** pela matriz de conectividade.
  - Nos nós: continuidade da variável primária e equilíbrio das secundárias (ΣQ = carga nodal aplicada).
  - Carga pontual no interior do elemento: fi = Q0·ψi(x0) (Dirac).
- **Solução particionada:** u2 = K22⁻¹(F2 − K21·u1); reações R1 = K11·u1 + K12·u2 − F1. É necessário descontar a carga equivalente do elemento.
- **Pós-processamento (importante para o software):** a derivada do interpolante dá esforços descontínuos e imprecisos nos nós. O esforço de extremidade correto é **Ke·ue − fe**, o equilíbrio do elemento.
  - No exemplo da apostila (balanço com 2 elementos e q), a reação pela derivada erra **q·h/2 na força e q·h²/12 no momento**.
  - Esse erro some com o refinamento, mas o caminho correto já é exato (V2).
  - `mef.py.forces` e o `eleResponse` do OpenSees já fazem assim.
- **Treliça/pórtico:** K = Tᵀ·K̄·T. A relação μ = A·h²/(2I) entre as rigidezes axial e de flexão mostra o mau condicionamento em barras longas e esbeltas.
- ⚠ **Convenção:** a apostila usa **θ = −dv/dx**, o que troca os sinais dos termos de rotação em K e em f. `mef.py`, `fem1d.py` e o OpenSees usam θ = +dv/dx. Ao transcrever um exemplo, trocar o sinal de rotações e momentos nodais.
- Errata de transcrição do exemplo do balanço: o fator de U é h/(6EI). Com ele, v_ponta = 16F0h²·h/(6EI) = F0L³/3EI.

### 23.2 Erro e convergência (cap. 5)
- **Fontes de erro:** domínio (geometria), integração numérica, arredondamento e aproximação (grau do polinômio).
- **Normas:** máximo, L2 (‖e‖0) e energia (‖e‖m, onde 2m é a ordem da EDO).
- **Taxas de convergência** (k = grau completo do polinômio, h = tamanho do elemento):
  - ‖e‖0 ≤ C·h^(k+1) e ‖e‖m ≤ C·h^(k+1−m); exige k ≥ m.
  - Elemento linear de barra, com h/2: o erro do deslocamento (L2) cai 4× e o da tensão cai 2×.
  - Conferido em V3: taxas 2,00/1,00 (k = 1) e 3,00/2,00 (k = 2).
- **A energia converge por cima** (I(uh) ≥ I(u)). O modelo de deslocamentos é mais rígido que o real, então em problema de carga os deslocamentos convergem por baixo.
- **Refinamento:** h (mais elementos), p (maior grau) ou hp.
- **Erro nodal nulo:** em 1D, com EDO de 2ª ou 4ª ordem e coeficientes constantes, o MEF é exato nos nós. Por isso a viga Hermite dá flecha exata nos nós (V2).
  - Com EI variável (fissuração, mísula) ou com Kg, isso deixa de valer, e é necessário estudar a malha.
- **Prática no software:** estimar o erro por dois refinamentos (Richardson): e_h ≈ (u_h − u_h/2)/(1 − 2^(−p)), com p igual à taxa teórica.

### 23.3 Integração numérica e formulação isoparamétrica (cap. 6)
- **Elemento mestre:** ξ ∈ [−1, 1]; x(ξ) = Σ Ψ̂i·xi; J = dx/dξ (no elemento linear, J = h/2).
  - d/dx = (1/J)·d/dξ, e Ke_ij = ∫ a·(1/J)·dΨi·dΨj dξ.
  - Classificação pelos nós da geometria (M) e da variável (N): subparamétrico M < N, isoparamétrico M = N, superparamétrico M > N.
- **Lagrange no mestre:** Ψ̂i = Π(ξ − ξj)/(ξi − ξj).
  - Linear: ½(1 ∓ ξ).
  - Quadrático: −½ξ(1 − ξ), (1 + ξ)(1 − ξ), ½ξ(1 + ξ).
- **Gauss-Legendre:**
  - Com r pontos integra exatamente polinômio de grau 2r − 1, logo **r_mín = ⌊p/2⌋ + 1**.
  - Pontos: r = 2 → ±0,5773502692 (peso 1); r = 3 → 0 (8/9) e ±0,7745966692 (5/9).
- **Erro da quadratura:** e ≤ c_r·h^(2r+1)·f^(2r), com c_r = 2(r!)⁴/((2r+1)[(2r)!]³).
  - c_r = 8,3e−2; 4,6e−4; 9,9e−7; 1,1e−9 para r = 1…4.
  - Com h/2 e r = 3, o erro cai 2⁷.
  - Integrando singular ou quase singular → refinar a malha ou usar mais pontos.
- **Pontos mínimos para resultado exato** (a, c, f e J constantes), para K / M / f:
  - linear: 1/2/1; quadrático: 2/3/2; cúbico: 3/4/3.
  - Em elemento distorcido (J variável) ou com coeficientes variáveis, usar mais pontos.
  - A integração reduzida abaixo desse mínimo é escolha deliberada (anti-travamento, ver 21.2) e traz risco de modos espúrios.
- Errata do exemplo ∫ξ⁶ e ∫ξ⁸: o ponto é 0,8611363116 (escrito 0,8611343116) e o peso 0,3478548451 (escrito 0,0347…). Os resultados (2/7 exato; −5,2 % e −35 % com 4 e 3 pontos) conferem (V1).
- **Fluxo do código:** pré-processamento (malha, propriedades, contorno, cargas) → processamento (Ke, montagem, contorno, solução) → pós-processamento (esforços, gráficos).

### 23.4 Problemas de autovalor: vibração e flambagem (caps. 7.2–7.3)
- Com separação de variáveis u = U(x)·T(t), chega-se a **(K − ω²M)·U = 0**.
  - Massa consistente: Mij = ∫ρA·ψi·ψj.
  - Viga Hermite: M = ρA·h/420·[[156, 22h, 54, −13h], [22h, 4h², 13h, −3h²], [54, 13h, 156, −22h], [−13h, −3h², −22h, 4h²]].
- **Flambagem:** (K − P·G)·U = 0, com G = ∫ψ'i·ψ'j (= Kg/P da 21.2).
- **Barra transiente de calor:** autovalor de −U'' = λU, com amortecimento temporal e^(−αλt).
- As condições de contorno são homogêneas. Eliminam-se os gdl prescritos e as equações cuja variável secundária é desconhecida.
- **Estimador:** 0 ≤ λh − λ ≤ C·h^(2(k+1−m))·λ^((k+1)/m).
  - **A massa consistente superestima os autovalores.**
  - O erro cresce com a ordem do modo: confiar só nos modos baixos de cada malha.
  - Barra com elemento linear: o erro em λ cai 4× a cada h/2 (V4).
- **Exemplo da apostila** (barra engastada-livre, 2 elementos lineares, EA/L = 1, ρAL = 12):
  - ω = 0,46518 e 1,62504 (exato (π/2, 3π/2)·√(EA/ρAL²) = 0,45345 e 1,36035).
  - Modos {0,70711; 1} e {0,70711; −1}.
  - A equação característica é ω⁴ − 20/7·ω² + 4/7 = 0. Reproduzido em V4a.
- **Massa diagonal (lumped):**
  - Soma da linha: Mii = ∫ρψi, usando a partição da unidade.
  - Proporcional (HRZ): diagonal consistente reescalonada para a massa total.
  - Para Lagrange linear ou quadrático com ρ constante, as duas coincidem.
  - Lumped tende a **subestimar** ω (V4b: −5,0 % contra +5,2 % da consistente com 2 elementos).
  - Na viga, o lumped só translacional (padrão do OpenSees) dá erros de −2,8/−8,8/−13,8 % nos 3 primeiros modos do balanço com 4 elementos. A massa consistente (`-cMass`) dá +0,003/+0,12/+0,77 %.
- **Referências exatas para teste:**
  - Viga biapoiada: ωn = (nπ)²·√(EI/m)/L².
  - Balanço: ωn = (1,8751; 4,6941; 7,8548)²·√(EI/m)/L².
  - Barra engastada-livre: ωn = (2n − 1)·π/2·√(E/ρ)/L.

### 23.5 Problemas transientes (caps. 7.4–7.5)
- **Modelo semidiscreto:** M2·ü + M1·u̇ + K·u = F (espaço por MEF e tempo por diferenças finitas).
- **Parabólico** (c2 = 0; calor, adensamento, difusão): família α.
  - Recorrência: (M1 + αΔt·K)·u_s+1 = (M1 − (1−α)Δt·K)·u_s + Δt·(α·F_s+1 + (1−α)·F_s).
  - Esquemas:
    - α = 0: diferença progressiva, explícito (com M1 diagonal), O(Δt).
    - α = ½: Crank-Nicolson, O(Δt²).
    - α = 2/3: Galerkin.
    - α = 1: diferença regressiva, O(Δt).
  - α ≥ ½ é incondicionalmente estável. Se α < ½, exige **Δt < 2/((1 − 2α)·λmax)**, com λmax de (K − λM1) (V6).
  - ⚠ A Tab. 7.1 da apostila atribui O(Δt²) a α = 2/3, mas só α = ½ é de 2ª ordem.
- **Hiperbólico** (c1 = 0; dinâmica): Newmark.
  - Os parâmetros (α, γ) da apostila correspondem a **(γ, 2β)** da notação usual. No OpenSees é `integrator('Newmark', gamma, beta)`.
  - Esquemas:
    - Aceleração média: γ = ½, β = ¼, incondicional.
    - Aceleração linear: γ = ½, β = 1/6, condicional (ωΔt ≤ 3,46).
    - Diferença central: γ = ½, β = 0, **Δt ≤ 2/ωmax** (V7a).
  - Limite geral para 2β < γ: Δt_crit = 1/(ωmax·√(γ/2 − β)).
  - Partida: ü0 = M⁻¹(F0 − C·u̇0 − K·u0). Depois u_s+1 da equação efetiva, ü_s+1 e u̇_s+1.
- **Vantagens da massa diagonal:**
  - O esquema explícito não inverte matriz.
  - Δt_crit fica maior (V7a: 2,7× maior com HRZ que com a consistente).
- **Prática estrutural (fora da apostila, conferida):**
  - Newmark de aceleração média é o padrão: sem amortecimento numérico, só alongamento de período ≈ (ωΔt)²/12. Usar **Δt ≤ T/20 do maior modo de interesse**; a estabilidade não governa.
  - O explícito fica para impacto e propagação de onda.
  - Amortecimento de Rayleigh: C = a0·M + a1·K, com ζ(ω) = a0/(2ω) + a1·ω/2. Para fixar ζ em dois modos, resolver a0 e a1 com ωi e ωj (OpenSees: ζ = 5 % medido pelo decremento logarítmico, ver `mef-opensees-opsvis` 11).

### 23.6 Validação (`test_fem1d.py`, rodado em 02/10/2026 — 13/13 PASS)
| Teste | Resultado | Referência |
|---|---|---|
| V1 Gauss ∫ξ⁶ (4 pts) / ∫ξ⁸ (4 e 3 pts) | 0,2857142857 / 0,2106122449 / 0,1440000000 | apostila 6.1.5 |
| V2 balanço 2 elementos Hermite: v_ponta (F0, M0, q) | 8/3, 2, 2 (exato nos nós) | FL³/3EI, ML²/2EI, qL⁴/8EI |
| V2 reação com q: equilíbrio × derivada | (−2; −2) × (−1,5; −1,917) | diferença qh/2 e qh²/12 (exemplo do balanço da apostila) |
| V3 taxa L2 / energia, k = 1 e k = 2 | 2,00 / 1,00 e 3,00 / 2,00 | k+1 / k |
| V4a barra engastada-livre, 2 elementos | ω = 0,465176 / 1,625040 | apostila 0,4651756 / 1,6250398 |
| V4b erro de λ1, 2/4/8/16 elementos (consist.) | +5,24/+1,29/+0,32/+0,08 % (lumped: −5,04…−0,08 %) | razão 1/4 |
| V5 biapoiada / balanço, 10 elementos: ω1, ω2 | +0,0007/+0,011 % e +0,0001/+0,003 % | fórmulas 23.4 |
| V5 flambagem biapoiada (K − PG), 8 elementos | Pcr/Euler = 1,00003 | π²EI/L² |
| V6 família α = 0 e ¼: 0,98·Δtc estável, 1,02·Δtc diverge | ok | Δtc = 2/((1−2α)λmax) |
| V6 Crank-Nicolson com Δt = 25·Δtc | estável | incondicional |
| V7a diferença central com massa HRZ: 0,98 × 1,02·Δtc | estável × diverge | Δtc = 2/ωmax |
| V7b Newmark γ = ½, β = ¼ com Δt = 100·Δtc | estável | incondicional |
| V7c SDOF, Δt = T/20: u(T) | 0,9987 | 1 (só erro de período) |
| OpenSees (`-cMass`) × `fem1d` — balanço 4 elementos | +0,0033 % / +0,1165 % | idênticos |

### 23.7 Código — gravar como `fem1d.py` (núcleo didático e de verificação)
```python
"""fem1d.py — núcleo MEF 1D (apostila TM266 UFPR): Lagrange isoparamétrico + Gauss, viga Hermite (K, M, f, G),
solução particionada, modal, lumping, família α (parabólico), Newmark e diferença central.
Convenção ND: θ = +dv/dx; kN, m, t (massa em t/m → ω em rad/s)."""
import numpy as np
from numpy.polynomial.legendre import leggauss
from math import factorial
from scipy.linalg import eigh

def gauss(r): return leggauss(r)                         # pontos, pesos em [-1, 1]
def c_r(r): return 2*factorial(r)**4/((2*r+1)*factorial(2*r)**3)
def r_min(p): return p//2 + 1                           # pontos para integrar grau p exatamente

def lagrange(N):
    """Funções de Lagrange de N nós equidistantes no mestre: Psi(ξ) -> (Ψ, dΨ/dξ)."""
    xn = np.linspace(-1, 1, N)
    def Psi(xi):
        P = np.ones(N); dP = np.zeros(N)
        for i in range(N):
            for j in range(N):
                if j != i: P[i] *= (xi - xn[j])/(xn[i] - xn[j])
            for m in range(N):
                if m == i: continue
                t = 1/(xn[i] - xn[m])
                for j in range(N):
                    if j not in (i, m): t *= (xi - xn[j])/(xn[i] - xn[j])
                dP[i] += t
        return P, dP
    return Psi

def bar_elem(x_e, a=1.0, c=0.0, f=0.0, rho=0.0, r=None):
    """Elemento isoparamétrico de -(a u')' + c u = f; massa rho. a, c, f, rho: constante ou função de x."""
    N = len(x_e); Psi = lagrange(N); r = r or N + 1
    fn = lambda g, x: g(x) if callable(g) else g
    K = np.zeros((N, N)); M = np.zeros((N, N)); F = np.zeros(N)
    for xi, w in zip(*gauss(r)):
        P, dP = Psi(xi); J = dP @ x_e; x = P @ x_e; dN = dP/J
        K += (fn(a, x)*np.outer(dN, dN) + fn(c, x)*np.outer(P, P))*J*w
        M += fn(rho, x)*np.outer(P, P)*J*w; F += fn(f, x)*P*J*w
    return K, M, F

def bar_mesh(L, ne, k=1, **kw):
    """Malha uniforme de ne elementos de grau k; devolve x, K, M, F globais."""
    nn = ne*k + 1; x = np.linspace(0, L, nn); K = np.zeros((nn, nn)); M = K.copy(); F = np.zeros(nn)
    for e in range(ne):
        idx = np.arange(e*k, e*k + k + 1); Ke, Me, Fe = bar_elem(x[idx], **kw)
        K[np.ix_(idx, idx)] += Ke; M[np.ix_(idx, idx)] += Me; F[idx] += Fe
    return x, K, M, F

def solve_part(K, F, fixed, u_fixed=None):
    """u2 = K22^-1 (F2 - K21 u1); reações R1 = K11 u1 + K12 u2 - F1."""
    n = len(F); u = np.zeros(n); fixed = np.array(fixed); free = np.setdiff1d(np.arange(n), fixed)
    if u_fixed is not None: u[fixed] = u_fixed
    u[free] = np.linalg.solve(K[np.ix_(free, free)], F[free] - K[np.ix_(free, fixed)] @ u[fixed])
    return u, K[fixed] @ u - F[fixed]

def lump(M, how='row'):
    """'row' = soma da linha; 'hrz' = proporcional à diagonal (preserva a massa total)."""
    if how == 'row': return np.diag(M.sum(1))
    d = np.diag(M); return np.diag(d/d.sum()*M.sum())

def beam_KMf(EI, h, m=0.0, q=0.0):
    """Viga Euler-Bernoulli (v, θ=+dv/dx): K, M consistente, f de q uniforme, G (geométrica unitária)."""
    K = EI/h**3*np.array([[12, 6*h, -12, 6*h], [6*h, 4*h*h, -6*h, 2*h*h], [-12, -6*h, 12, -6*h], [6*h, 2*h*h, -6*h, 4*h*h]])
    M = m*h/420*np.array([[156, 22*h, 54, -13*h], [22*h, 4*h*h, 13*h, -3*h*h], [54, 13*h, 156, -22*h], [-13*h, -3*h*h, -22*h, 4*h*h]])
    f = q*h/12*np.array([6, h, 6, -h])
    G = 1/(30*h)*np.array([[36, 3*h, -36, 3*h], [3*h, 4*h*h, -3*h, -h*h], [-36, -3*h, 36, -3*h], [3*h, -h*h, -3*h, 4*h*h]])
    return K, M, f, G

def beam_mesh(L, ne, EI, m=0.0, q=0.0):
    h = L/ne; n = 2*(ne + 1); K = np.zeros((n, n)); M = K.copy(); G = K.copy(); F = np.zeros(n)
    for e in range(ne):
        Ke, Me, fe, Ge = beam_KMf(EI, h, m, q); i = np.arange(2*e, 2*e + 4)
        K[np.ix_(i, i)] += Ke; M[np.ix_(i, i)] += Me; G[np.ix_(i, i)] += Ge; F[i] += fe
    return K, M, F, G

def modal(K, M, free, n=5):
    """Frequências angulares ω (rad/s) de (K - ω²M)U = 0 nos gdl livres."""
    w2 = eigh(K[np.ix_(free, free)], M[np.ix_(free, free)], eigvals_only=True)
    return np.sqrt(np.abs(w2[:n]))

def alpha_family(M1, K, F, u0, dt, nsteps, alpha):
    """M1 u' + K u = F. alpha: 0 explícito, 1/2 Crank-Nicolson, 2/3 Galerkin, 1 implícito."""
    A = M1 + alpha*dt*K; B = M1 - (1 - alpha)*dt*K; u = u0.copy(); H = [u.copy()]
    for _ in range(nsteps):
        u = np.linalg.solve(A, B @ u + dt*F); H.append(u.copy())
    return np.array(H)

def newmark(M, K, F, u0, v0, dt, nsteps, beta=0.25, gamma=0.5, C=None):
    """Newmark (β, γ) usual = (γ_ap/2, α_ap) da apostila. F constante ou função F(t)."""
    C = np.zeros_like(M) if C is None else C
    Ff = F if callable(F) else (lambda t: F)
    u, v = u0.copy(), v0.copy(); a = np.linalg.solve(M, Ff(0) - C @ v - K @ u); H = [u.copy()]
    Keff = M/(beta*dt*dt) + gamma/(beta*dt)*C + K
    for s in range(1, nsteps + 1):
        rhs = (Ff(s*dt) + M @ (u/(beta*dt*dt) + v/(beta*dt) + (1/(2*beta) - 1)*a)
               + C @ (gamma/(beta*dt)*u + (gamma/beta - 1)*v + dt*(gamma/(2*beta) - 1)*a))
        un = np.linalg.solve(Keff, rhs)
        an = (un - u)/(beta*dt*dt) - v/(beta*dt) - (1/(2*beta) - 1)*a
        v = v + dt*((1 - gamma)*a + gamma*an); u, a = un, an; H.append(u.copy())
    return np.array(H)

def central_diff(M, K, u0, v0, dt, nsteps):
    """Diferença central explícita (β=0, γ=1/2); usar M diagonal. Estável se dt < 2/ωmax."""
    Minv = np.linalg.inv(M); a = Minv @ (-K @ u0); um = u0 - dt*v0 + dt*dt/2*a; u = u0.copy(); H = [u.copy()]
    for _ in range(nsteps):
        up = 2*u - um + dt*dt*Minv @ (-K @ u); um, u = u, up; H.append(u.copy())
    return np.array(H)
```
- Uso típico (verificar o modal de um pórtico do OpenSees com uma viga equivalente; testar Δt antes de um transiente):
  ```python
  K, M, F, G = beam_mesh(6.0, 10, EI=2.1e4, m=0.5); fr = np.arange(2, K.shape[0])   # balanço
  print(modal(K, M, fr, 3))                       # comparar com 1,8751²·√(EI/m)/L² …
  ```
- Limitações: 1D (barra e viga plana); malha uniforme em `bar_mesh`/`beam_mesh`; sem amortecimento em `central_diff`; matrizes densas (didático e de verificação, não de produção).

## 24. Estruturas segmentadas — juntas entre aduelas pré-moldadas e protensão interna/externa (Spessatto 2022)

Fonte: Spessatto, R. P. *Análise pelo MEF do comportamento das juntas de tabuleiro de ponte composto por aduelas pré-moldadas de concreto*. Dissertação, PPGEC/UFRGS, 2022, orient. Américo Campos Filho, coorient. Bruna M. Lazzari (base NBR 6118:2014, NBR 7187:2021, NBR 7188:2013, NBR 8681:2003). Caso: Nova Ponte do Guaíba (Porto Alegre), vão 3, balanços sucessivos. Modelo numérico: ANSYS 21.2 APDL + USERMAT (linha CEMACOM/UFRGS: Lazzari 2016/2020, Hoffman 2020, Machado 2022, Soares 2022). Implementação própria em OpenSeesPy: `juntas_nd.py` (skill `mef-opensees-opsvis`, seção 12).

### 24.1 Sistema e comportamento
- **Balanços sucessivos com aduelas pré-moldadas** (seção caixão; aduela de disparo moldada sobre o pilar; treliça lançadora; aduelas içadas aos pares). Protensão **interna aderente** (cabos superiores nos balanços, inferiores do meio do vão em diante) a cada par içado, após a cura da junta; **protensão externa** após o fechamento, ancorada em blocos e desviada em desviadores. Mãos-francesas e lajes pré-moldadas + concreto in loco completam o tabuleiro. Primeiro balanço sucessivo do mundo: Emílio Baumgart, ponte sobre o Rio do Peixe (Herval d'Oeste–Joaçaba/SC, 1930, vão 68 m, concreto armado).
- **Juntas** (Rombach 2002): seca (match-cast), colada com epóxi, argamassa ou concreto moldado (Guaíba: 20 cm, fck ≥ 50 ou 60 MPa). **Sem armadura passiva passante → ponto mais fraco da superestrutura**; chaves de cisalhamento (dentes) transmitem o cortante por atrito + corte dos dentes e alinham a montagem.
- **Aderente × não aderente:** cabo aderente (interno) → muitas fissuras de pequena abertura, acréscimo de tensão alto e localizado junto à junta, melhor ductilidade e resistência última; cabo não aderente (externo) → poucas aberturas grandes, rotação concentrada nas juntas, Δσp moderado (alongamento distribuído no comprimento livre), ruptura com carga menor e flechas maiores, risco de colapso brusco se poucas juntas concentram a rotação. Vantagens do externo: inspeção, troca e reprotensão.
- **Mecanismo de ruína:** abertura progressiva das juntas → escoamento do cabo e subida da LN → esmagamento da laje superior. A protensão externa pode reduzir a capacidade última (pouco Δσp, mais compressão no concreto).

### 24.2 Critérios de projeto (prática)
- **Junta sem armadura passante:** em serviço, exigir **descompressão na junta** (σ ≤ 0 na combinação que a norma/CAA exigir); não contar com fctm do material da junta como critério de projeto — a CZM com σmax = fctm é ferramenta de simulação. Conferir NBR 7187:2021 e, para segmentadas, AASHTO LRFD / guia AASHTO de pontes segmentadas.
- **Momento de abertura da junta** (seção retangular ou com I, yb, A da seção da junta): M_ab = P·ep + (σt,lim + P/A)·I/yb, com σt,lim = 0 (junta seca/projeto) ou fctm (simulação de junta concretada). Validado no OpenSees (T8: −0,02 %).
- **Após a abertura (junta seca, seção retangular):** contato parcial c = 3(h/2 − eN), eN = (M − P·ep)/P; σc,máx = 2P/(b·c) → **verificar esmagamento** (cresce rápido quando c → 0; o MEF com interface elástica perde precisão quando c < ~0,15h — T9).
- **Cabo externo/não aderente no ELU:** Δσp pela seção 11 (70 + fck/100ρp ≤ 420 MPa ou /300ρp ≤ 210 MPa conforme L/h); preso no desviador → tensão maior no trecho central; deslizando → tensão uniforme (T10).
- **Cargas de ponte rodoviária (NBR 7188:2013 — conferir revisão vigente):** TB-450 = 6 rodas × 75 kN, eixos a 1,5 m, área 18 m²; p = 5 kN/m² na pista fora do veículo; p' = 3 kN/m² no passeio. Q = P·CIV·CNF·CIA; CIV = 1 + 1,06·20/(Liv + 50) (10 ≤ Liv ≤ 200 m); CNF = 1 − 0,05(n − 2) ≥ 0,9 (só longitudinais); CIA = 1,25 concreto/misto (1,15 aço) até 5 m de juntas. Permanentes (NBR 7187): 25 kN/m³ concreto armado/protendido, 24 kN/m³ pavimento, + 2 kN/m² de recapeamento. A tese usou ainda o caminhão real 3T4 (PBT 1015,6 kN, retorno de 50 anos — Moura 2019), descontando a multidão sob o veículo.
- **Perdas:** a tese adotou 10 % e 15 % (Pfeil: estimativa ~17 % para CP-190 RB pós-tracionado, com atrito e encurtamento). Aduelas estocadas ~500 dias antes do içamento → fluência e retração menores (parâmetro `texist`). Em projeto, calcular (seções 6–7).

### 24.3 Receita do modelo 3D da tese (ANSYS, para reproduzir ou auditar)
- Concreto: **SOLID186** (20 nós, integração completa). Modelo elastoplástico com fissuração na USERMAT (ruptura de Ottosen, compressão fib MC2010 com endurecimento isotrópico, tração com fissuras distribuídas — Hinton 1988 — e amolecimento; Poisson desprezado após fissurar). Unidades kN, cm, dias, °C; 21 constantes (fck, ν, s, βsc, α, UR, hf, ti, ts, t0, texist, tinf, ndec, chaves de fluência/retração/fissuração…). Na tese: fluência e retração desligadas (análise em serviço), ti = 0, ts = t0 = 28 d, texist = 365 d, UR 70 %, 23 °C.
- Cabos internos: **REINF264** (armadura incorporada, aderência perfeita) gerado por **MESH200 + EREINF** (malha independente). Protensão por **INISTATE** com deformação elástica inicial ε = σ/Ep (EPEL), um material por cabo para poder selecioná-lo. Aço CP-190 RB: BISO, Ep = 200 GPa (195 GPa no externo), escoamento 1900 MPa, Et = 1 % Ep (a tese usou fptk como "escoamento"; usar fpyk ≈ 0,9 fptk em projeto).
- Cabos externos: **LINK180**, um elemento entre ancoragem e desviador; nós acoplados ao concreto com **CP** (sem deslizamento: x, y, z; com deslizamento: liberar x).
- Armadura passiva **distribuída**: SOLID95 com **ANISO** (taxas ρx, ρy, ρz multiplicando E, G e fy em cada direção — 18 constantes) sobreposto ao concreto; taxas por região (laje superior, inferior, almas; 10–30 % nas ancoragens e desviadores para enrijecer).
- **Juntas:** volume da junta dividido ao meio com folga de 0,01 cm; **CONTA174/TARGE170** colados com **zona coesiva bilinear modo I** (TB,CZM,…,CBDD: C1 = σmax = fctm = 0,3·fck^(2/3); C2 = δc = 0,01 cm; C5 = η = 10⁻⁸). KEYOPT: (2) = 0 Lagrangiano aumentado; (4) = 1 detecção nodal normal ao contato; (5) = 3 ajuste automático CNOF; (9) = 1 ignora penetração inicial; (10) = 2 atualiza rigidez a cada iteração; (12) = 6 colado no contato inicial. Constantes reais: FKN = 0,1, FTOLN = −0,01, ICONT = −0,01 cm, FKOP = −0,1 (calibrados por tentativa — começar com FKN ≈ E e reduzir se não convergir; aumentar se penetrar). Fissuração do concreto da junta **desligada** para a abertura ocorrer só pela interface.
- CZM: P = Kn·un·(1 − dn); dn = ((un − ūn)/un)·(unC/(unC − ūn)) para un > ūn; GCn = ½·σmax·unC; regularização viscosa dv = (dn·Δt + dv,old·η)/(Δt + η), com η menor que o menor passo.
- **"Malha de vazios":** SOLID186 com E = 1 kN/cm², ν = 0,1, duplicada só nas juntas, para os cabos internos atravessarem a junta sem descontinuidade quando ela abre.
- Solução: Newton-Raphson com rigidez inicial; 3 load steps encadeados (multiframe restart): (1) peso próprio (ACEL, ρ = 2,54·10⁻⁸ t/cm³) + protensão, KBC em 20 incrementos; (2) permanentes (guarda-rodas 7,5/8,25 kN/m, CBUQ 7 cm = 1,68 kN/m² + 2 kN/m²) em 100 incrementos; (3) móveis em 100 incrementos. Contorno: extremidades do vão engastadas (simplificação).
- Porte: 608 864 elementos (314 592 SOLID186, 243 808 SOLID95, 15 855 REINF264, 193 LINK180, 17 208 pares de contato), script de 594 mil linhas, **114 h** em 16 núcleos / 128 GB.

### 24.4 Resultados (vão 3 da Nova Ponte do Guaíba)
| Flecha máxima do tabuleiro (cm), sem deslizamento | Sem perdas | 10 % | 15 % |
|---|---|---|---|
| Etapa 1 (PP + protensão) | 3,33 | 4,46 | 5,02 |
| Etapa 2 (+ permanentes) | 5,48 | 6,56 | 6,97 |
| Etapa 3, veículo no meio do vão | 10,08 | 11,25 | 11,80 |
- Deslizamento do cabo externo no desviador praticamente não muda a flecha (11,25 → 11,35 cm); a tensão no cabo externo fica uniforme (121,2–121,6 kN/cm²) em vez de variar por trecho (100,9–122,7).
- Cabos internos: tensão inicial 134,87 / 121,38 / 114,64 kN/cm²; máxima na etapa 3: 170,8 (sem perdas, = escoamento adotado) / 160,6 / 154,1. Acréscimo relativo cresce com as perdas (26,6 → 32,4 → 34,4 %): perder protensão reduz a rigidez e transfere mais deformação para o cabo, mas a tensão absoluta continua menor. Picos de tensão no cabo junto às juntas (o cabo "segura" a abertura).
- Seção mais solicitada: aduela onde começam os cabos internos inferiores e há desviador/ancoragem de cabo externo (inversão de momento, tração no topo, junta abrindo em cima). Juntas perto do engaste fechadas; maiores aberturas perto do veículo e em mudança de espessura da laje inferior.
- Tensões no concreto e nos cabos dentro dos limites; modelo considerado adequado, mas o engaste e a ausência das etapas construtivas alteram o comportamento.

### 24.5 Lições de modelagem (valem para qualquer software)
1. Contorno: engastar as pontas do vão **superestima o negativo nas extremidades e subestima o meio do vão** → modelar continuidade com vãos adjacentes/pilares e as etapas construtivas (o comportamento real depende delas).
2. Ancoragem sem placa/bloco gera concentração e "ruptura" numérica: modelar placa/bloco ou desligar a fissuração localmente — e declarar isso.
3. Abrir a junta só pela interface (sem fissuração no concreto da junta) e garantir continuidade do cabo interno através dela.
4. Omitir protensão transversal/longitudinal das lajes deixa deslocamentos e tensões locais exagerados nas lajes.
5. CZM é sensível à malha: refinar perto da interface; amortecimento viscoso pequeno para convergir.
6. Penalidade de contato (FKN, Kn): alta o bastante para não penetrar, baixa o bastante para convergir; checar a penetração ao final.
7. Começar pelo modelo de barras com juntas (`juntas_nd.py`, minutos) e reservar o 3D sólido para a região crítica (dias de processamento).
- Trabalhos futuros sugeridos pela autora: etapas construtivas reais; efeitos diferidos, vento e perdas calculadas; validar a CZM com monitoramento da obra; vão completo com pilares e fundações; comparar com modelos menos refinados; armadura passiva discreta × distribuída.

### 24.6 Uso na ND
- Pré-moldados: a mesma física vale para vigas segmentadas pós-tracionadas, juntas secas entre painéis/peças protendidas, ligações com cabo atravessando a junta e reforço com protensão externa (reabilitação). Critério de projeto: descompressão na junta em serviço + ELU com Δσp de cabo não aderente; simulação: `juntas_nd.py`.
- Aula/mestrado: exemplo completo de MEF não linear com interface coesiva, protensão por estado inicial e armadura distribuída anisotrópica.

## 25. Tanques e reservatórios cilíndricos de concreto armado (Koneski 2013)

Fonte: Koneski, G. F. *Dimensionamento da laje de fundo de tanque enterrado em concreto armado com formato cilíndrico com ênfase na verificação de estabilidade contra flutuação*. TCC, UDESC/CCT Joinville, 2013, orient. Sandra Denise Krüger Alves (base NBR 6118:2003 + EC7; Rocha 1985, Guerrin, Vasconcelos 1998, Cruz 2009, Ramos 2010). Roteiro operacional, critérios completos e o estudo de caso: skill `tanques-reservatorios-concreto`. Código validado: `tanques_nd.py` (skill `mef-opensees-opsvis`, seção 13, testes T11–T17).

### 25.1 Modelos de cálculo
- **Parede = casca cilíndrica** (r ≥ 20t) sob pressão axissimétrica.
  - Membrana: Nθ = p·a (hidrostática p = γ(d − x)); Ny = −(G + g·y).
  - Perturbação de borda (Timoshenko = Rocha 1985): β⁴ = 3(1 − ν²)/(a²t²), L = 1/β ≈ 0,76√(a·t).
  - Engaste: M0 = γL²(d − L)/2 (tração na face interna); Q0 = γL(2d − L)/2. Válido para βH ≥ 3; amortece em ≈ πL.
  - Mθ = ν·Mx (+ gradiente térmico e carga não axissimétrica).
  - Analogia exata para o MEF: faixa meridional = viga sobre base elástica com EI = D = Et³/12(1 − ν²) e k = Et/a².
- **Ligação parede-fundo:** monolítica (w = θ = 0), rótula (w = 0) ou deslizante (só membrana — junta de execução e manutenção difíceis).
- **Laje de fundo circular (Kirchhoff, ν = 0,2):**
  - engastada: Mr,borda = −qa²/8; Mt,borda = −qa²/40; Mcentro = qa²(1 + ν)/16 = ql²/53,3; w0 = qa⁴/64D = 0,0113·q·l⁴/(E·h³);
  - apoiada: Mcentro = qa²(3 + ν)/16; w0 = qa⁴(5 + ν)/(64D(1 + ν)).
- **Junta monolítica = nó de Cross:** M = (S_l·FEM_p + S_p·FEM_l)/(S_p + S_l), com S_p = 2Dβ e S_l = D_l(1 + ν)/a. O momento de borda da laje é limitado pelo que a parede absorve (mais a aba): laje grossa com parede fina fica quase apoiada.
- **Malha ortogonal:** Wood-Armer com momentos principais de mesmo sinal → máx(|Mr|, |Mt|); no centro (Mr = Mt) o fator √2 é conservador.

### 25.2 Critérios
- Empuxo de terra em **repouso** (K0 = 1 − sen φ'; EC7 9.5.2) — parede rígida não mobiliza o ativo; abaixo do NA: K0·σ'v + u.
- **Flutuação (EC7 UPL):** Vdst,d ≤ Gstb,d + Rd, com γG,dst = 1,0, γQ,dst = 1,5, γG,stb = 0,9 (conferir; ver também NBR 6122:2022 e NBR 8681).
  - Subpressão na **área total da base**.
  - Tanque vazio com NA máximo (NA no terreno sem série histórica).
  - Atrito lateral desprezado.
- **Estanqueidade governa:** a tab. 13.4 da NBR 6118 (wk ≤ 0,3 mm em CAA III) não basta. Prática:
  - wk ≤ 0,1–0,2 mm, ou EN 1992-3 classe 1: 0,2 mm (hD/h ≤ 5) a 0,05 mm (hD/h ≥ 35) — conferir;
  - ou anel no estádio I (σct ≤ fctk,inf) com σs limitada.
- Cortante da laje sem estribos: VRd1 (19.4.1).
- Flecha da laje: imediata·(1 + αf) ≤ l/250.
- CAA III/IV para ETA/ETE, esgoto e efluentes (tab. 6.1, 7.1, 7.2 — conferir).
- Situações de projeto obrigatórias: vazio + NA máximo + aterro; cheio sem aterro (teste de estanqueidade); cheio + aterro; obra com rebaixamento ligado/desligado.

### 25.3 Lições do estudo de caso (revisão ND, 07/10/2026)
- **Caso:** tanque de equalização Ø23 m, 2 000 m³, enterrado 6,95 m em argila mole com NA alto; laje maciça 0,50 m com aba 1,0 m. Flutuou e inclinou; ao esvaziar, o centro da laje subiu 2 cm. A laje foi reforçada para 1,2 m.
- **Erros do TCC:**
  - subpressão só na área interna somada ao peso total do solo da aba, e γG,stb só na parede → a solução proposta (1,2 m + aba 1,6 m) ainda tem FS = 0,67 pelo EC7;
  - flecha com unidade trocada (3,7 cm em vez de 0,37 cm) motivou o aumento de espessura;
  - laje "engastada" com 857 kN·m/m numa parede de 0,30 m: compatibilizando, ≈ 220 na borda e ≈ 1 150 kN·m/m no centro, contra 514;
  - VRd1 e ELS-W não verificados.
- **Lição:** com subpressão alta e solo mole, a solução é ancoragem (estacas de tração) ou drenagem com alívio, não espessura; laje fina sobre vigas só fecha com ancoragem.

---

# Parte D — Software estrutural ND Engenharia (especificação viva)

Objetivo: software próprio de análise e dimensionamento (NBR 6118/9062/8681) montado sobre os códigos validados desta skill e da `mef-opensees-opsvis`. Esta parte é a **fonte única** das convenções; código novo segue estas regras, e material novo que o Nathan mostrar entra no backlog (D.4) antes de virar módulo.

### D.1 Convenções (valem para toda função pública)
- **Unidades:** kN, m, kPa (kN/m²). fck, fyk em MPa só na entrada. Armadura de saída em cm² (uso prático), sempre com sufixo `_cm2`.
- **Força normal:** **compressão negativa**, tração positiva — em pórtico, pilar, seção e bloco de fundação (sem exceções; resultados que são capacidade, como a força prevista do bloco, saem em módulo e com nome explícito).
- **Momento:** convenção de diagrama (positivo traciona a fibra inferior em viga). Esforços de extremidade do OpenSees/`mef.py` são convertidos antes de sair.
- **Seção:** y a partir do CG, positivo para o topo; camadas de aço `[(As m², y m)]`.
- **Entrada/saída:** JSON (formato da seção 6 da `mef-opensees-opsvis`); cada resultado sai com hipóteses, combinação que governa e critério de parada.
- **Dois motores sempre que possível:** `mef.py` (parábola-retângulo) e `ops_nd` (Concrete01) — divergência > 2 % é sinal de erro de modelo.
- **Convenções internas dos códigos antigos (não mudar, só adaptar):** `mef.py` compressão + na seção (N > 0 tração no pórtico); `confiab_ca.py` kN·cm e compressão −; `blocos.py` cm/MPa; `ops_nd` kN·m, compressão −; `tanques_nd` kN·m, momento + = tração na face interna (molhada) e Nθ + = tração. A conversão fica em `nd_api.py` (D.3).

### D.2 Arquitetura proposta (pacote Python `nd_estruturas`)
| Módulo | Conteúdo | Base validada |
|---|---|---|
| `materiais` | Eci/Ecs NBR 8.2.8, fctm, diagramas σ-ε (NBR, CEB-FIP), aço CA/CP, relaxação | Partes A, B; 21.3 |
| `secoes` | propriedades, seção composta, fibras, MRd, M-κ, interação N-M | 21.7 (`mef.py`), `ops_nd.MRd_fibras` |
| `porticos` | JSON → OpenSeesPy, combinações, envoltória, P-Δ, γz | `ops_nd` |
| `pilares` | pilar-padrão (curvatura/rigidez κ), método geral MEF, fluência | 15; 21.4; `pilar_nl` |
| `protendido` | perdas, ELS-F/D/W, vazio, isolamento, flechas por fase, ELU, previsão de ensaio (Pcr, Pu, flecha) de viga pré-tracionada | Parte A (seções 1–14); `viga_ensaio_nd.py` (`vigas-premoldadas-protendidas` 8); `viga_protendida_ops.py` (`mef-opensees-opsvis` 14) |
| `prefabricados` | consolo, dente Gerber, interface, ligação semirrígida (beam-line), juntas segmentais (abertura, CZM, cabo externo) | 10.7–10.9; ferramenta de consolos do usuário; 24 + `juntas_nd` |
| `pontes` | cargas NBR 7188 (TB-450, CIV/CNF/CIA), etapas construtivas, verificação de juntas | 24.2; `juntas_nd.nbr7188_coef` |
| `fundacoes` | blocos (Blévot, Andrade n estacas), reações com interação solo-estrutura | 22; memória do Bloco B39 |
| `reservatorios` | tanques cilíndricos: ações (hidrostática, K0, subpressão), flutuação UPL, parede (casca/Winkler), laje circular, junta parede-laje, anel, VRd1, estanqueidade | 25; `tanques_nd` (`mef-opensees-opsvis` 13) |
| `confiabilidade` | Monte Carlo, β | 18–19 (`confiab_ca`) |
| `nucleo_mef` | Gauss, Lagrange/Hermite, montagem, modal (massa consistente/lumped), família α, Newmark; estimador de erro por refinamento | 23 (`fem1d.py`) |
| `dinamica` | modal de pórticos, vibração de piso, ponte rolante, transiente com Rayleigh | 23.4–23.5; `mef-opensees-opsvis` 11 |
| `memoria` | relatório (Word/Docs) + figuras Opsvis + tabela de validação | 20; `ops_nd.figuras` |
| `tests` | pytest com todos os casos de validação das tabelas 19, 21.8, 22.6, 23.6, da seção 8 da `vigas-premoldadas-protendidas` e das seções 4, 11, 13 e 14 da `mef-opensees-opsvis` | — |

Ordem sugerida de construção: `nucleo_mef` (base de testes) → `secoes` → `porticos` → `pilares` → `fundacoes` → `protendido` → `prefabricados` → `memoria`. Interface final a decidir com o Nathan (planilha, web ou desktop).

### D.3 Camada de convenções (`nd_api.py`, testada em 02/10/2026)
Resultados do autoteste `ensaio_convencoes()`:

| Teste | Resultado | Referência |
|---|---|---|
| MRd 20×50, C30, 6,03 cm², N = 0 — `mef` / `ops` | 108,03 / 108,07 kN·m | bloco retangular 108,54 |
| MRd 20×50, 2×4,02 cm², N = −800 kN — `mef` / `ops` | 178,34 / 179,76 kN·m | diferença 0,8 % |
| Pilar Gonçalves (100×25, λ = 50, N = −3650 kN) | Md,tot 117,1 ≤ MRd 118,0 → ok | 115,8 ≅ 117 kN·m |
| Bloco B-4-30 (força prevista) | 16 159 kN | Tabela 2 do artigo |
| Bloco B-4-30 com N = −9 811 kN (projeto) | As,x = 38,14 cm² por linha | 22.2 |

```python
"""nd_api.py — API única do software ND (convenção do software, ver Parte D).
Unidades: kN, m, kPa; fck/fyk em MPa. Força normal: COMPRESSÃO NEGATIVA. Momento: convenção de diagrama.
Converte para as convenções internas de mef.py (compressão +), blocos.py (cm) e confiab_ca.py (kN·cm, compressão −)."""
import numpy as np

def MRd(b, h, camadas, fck, N=0.0, fyk=500, motor='mef'):
    """MRd (kN·m) de seção retangular. camadas = [(As m², y m a partir do CG, + topo)]. N < 0 compressão.
    motor='mef' (parábola-retângulo, mef.py) ou 'ops' (Concrete01, ops_nd.py) — usar os dois para conferir."""
    if motor == 'mef':
        from mef import RCSection, MRd as _MRd
        return _MRd(RCSection(b, h, camadas, fck, fyk=fyk, psi=0.85), -N)
    from ops_nd import MRd_fibras
    return MRd_fibras(b, h, camadas, fck, N=N, fyk=fyk)[0]

def pilar_2a_ordem(b, h, camadas, fck, le, N, M1_topo, M1_base, phi=0.0, fyk=500, nel=10):
    """Pilar biapoiado, método geral via MEF (Gonçalves 2017). N < 0 compressão (kN, de cálculo).
    Retorna dict: Md_tot, MRd, ok (Md_tot ≤ MRd e convergiu), flecha (m)."""
    from mef import RCSection, pilar_nl, MRd as _MRd
    Nd = -N
    r = pilar_nl(RCSection(b, h, camadas, fck, fyk=fyk, psi=1.10, phi=phi), le, Nd, M1_topo, M1_base, nel=nel)
    mrd = _MRd(RCSection(b, h, camadas, fck, fyk=fyk, psi=0.85), Nd)
    return dict(Md_tot=r['M'], MRd=mrd, ok=bool(r['ok'] and r['M'] <= mrd), flecha=r['u'], convergiu=r['ok'])

def bloco_6_estacas(bp, ap, h, fck, N=None, D=0.6, s=1.8, fyk=500, cob_tirante=0.145):
    """Bloco 2x3 (Andrade 1989). Entradas em m e kN; N = força normal de cálculo do pilar (compressão negativa).
    d = h − cob_tirante. N=None → força prevista sem coeficientes (artigo), devolvida em F (módulo)."""
    Fsd = None if N is None else -N
    from blocos import bloco6_stm
    r = bloco6_stm(bp*100, ap*100, fck, d=(h - cob_tirante)*100, sx=s*100, sy=s*100, D=D*100, fy=fyk, Fsd=Fsd)
    out = {k: v for k, v in r.items()}
    for k in ('Ap', 'Ae'): out[k] = r[k]/1e4                       # cm² → m²
    for k in ('Asx', 'Asy'): out[k + '_cm2'] = out.pop(k)          # armadura mantida em cm² (uso prático)
    return out

def ensaio_convencoes():
    """Autoteste: as funções públicas concordam entre si e com os valores validados das skills."""
    t = {}
    t['MRd_mef_N0'] = MRd(0.2, 0.5, [(6.03e-4, -0.20)], 30)                                   # 108,03
    t['MRd_ops_N0'] = MRd(0.2, 0.5, [(6.03e-4, -0.20)], 30, motor='ops')                      # 108,07
    t['MRd_mef_N800'] = MRd(0.2, 0.5, [(4.02e-4, 0.2), (4.02e-4, -0.2)], 30, N=-800)          # 178,3
    t['MRd_ops_N800'] = MRd(0.2, 0.5, [(4.02e-4, 0.2), (4.02e-4, -0.2)], 30, N=-800, motor='ops')  # 179,8
    As = 49.09e-4
    t['pilar_Goncalves'] = pilar_2a_ordem(1.0, 0.25, [(As/2, 0.075), (As/2, -0.075)], 20, 3.608, -3650, 82.1, 82.1)  # 117,1 ≤ 118,0
    t['bloco_B4_30'] = bloco_6_estacas(1.43, 0.35, 1.45, 30)['F']                             # 16 159
    return t

if __name__ == '__main__':
    for k, v in ensaio_convencoes().items(): print(k, v)
```

### D.4 Backlog de conhecimento (material que o Nathan vai mostrar)
- Registrar aqui cada fonte nova: referência, o que ensina, método/equações, exemplo numérico para validar, módulo de destino.
- Já incorporadas: Hanai 2005, Inforsato 2009, Real 2000, Gonçalves 2017, Oliveira/Barros/Giongo 2014 (+ Andrade 1989), Opsvis (Kokot, SoftwareX 2026), apostila TM266 DEMEC-UFPR (fundamentos MEF e dinâmica, seção 23), Spessatto 2022 (juntas segmentais, seção 24; `juntas_nd.py` validado em 04/10/2026), Koneski 2013 (tanques cilíndricos, seção 25 + skill `tanques-reservatorios-concreto`; `tanques_nd.py` validado em 07/10/2026), PCI Big Beam 2015 (viga pré-tracionada com isolamento, 10.12 + skill `vigas-premoldadas-protendidas`; `viga_protendida_ops.py` validado contra o ensaio em 07/10/2026).
- Pendências conhecidas: juntas com lei de compressão do concreto (esmagamento) e cabo aderente atravessando junta no `juntas_nd`; exemplos numéricos completos de Inforsato (seções 15.0–15.7 da versão antiga desta skill, removidos numa atualização — reincorporar no módulo `protendido` se o Nathan quiser); d' não informado no pilar de Gonçalves; comprimento de fuste não informado no bloco de Oliveira; NLF de barra no `ops_nd` (forceBeamColumn + fibras); molas de ligação e rótulas no `ops_nd`; itens normativos marcados "(conferir)" para a NBR 6118:2023; autor da apostila TM266 não identificado no PDF; MEF 2D/3D isoparamétrico (Q8/Q9, H20) e não linear de material no `nucleo_mef` ainda não incorporados; critérios normativos de vibração (NBR 6118 23.3 — frequência crítica de pisos, conferir) a ligar ao módulo `dinamica`; tanques: critério de fissuração para estanqueidade (EN 1992-3/ACI 350 — fonte a obter), temperatura e retração restringida, sismo (Housner), tampa/cúpula, laje sobre solo (Winkler) e estacas de tração, modelo 3D em casca cilindro + laje para cargas não axissimétricas, Tabela 5 de Rocha (coeficientes K, imagem não extraída — substituída pela solução fechada); Big Beam: confinamento da mesa, comprimento de transferência (lbpt) e escorregamento da cordoalha não modelados no `viga_protendida_ops`; Ec do concreto leve estimado pelo ACI (o relatório não informa).