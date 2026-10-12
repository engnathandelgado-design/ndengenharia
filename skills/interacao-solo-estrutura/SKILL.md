---
name: "interacao-solo-estrutura"
description: "Use ao considerar interação solo-estrutura (ISE) em pórticos de concreto sobre sapatas ou estacas: molas de fundação, recalques diferenciais, redistribuição de esforços e modelo MEF solo+estrutura."
---

# Interação solo-estrutura (ISE) em estruturas aporticadas

Complementa `projetos-estruturais-concreto-armado-protendido` (dimensionamento, Parte D: módulo `fundacoes` do software ND) e `mef-opensees-opsvis` (seção 12: código `ise_nd.py`, validado). Responder em português técnico. A decisão sobre parâmetros de solo e vínculos é do Nathan (ART): sempre declarar as hipóteses.

## 1. Fonte
- PEITZ, E. B. *Efeitos da interação solo-estrutura em estruturas aporticadas*. TCC (Graduação), UFRGS, 2024. Orientador: Jorge Luis Palomino Tamayo; coorientadora: Bárbara dos Santos Sánchez. LUME 10183/274468.
- Base normativa: NBR 6118:2023, NBR 6122:2022, NBR 6120:2019, NBR 6123:2023.
- Ferramenta do autor: ANSYS Mechanical APDL. Na ND, o equivalente é OpenSeesPy (ver `mef-opensees-opsvis` §12).
- Nível: graduação. É útil como roteiro e ordem de grandeza, não como prova geral.

## 2. Conceitos essenciais
- ISE (NBR 6122:2022, definição): análise que considera **juntas** as deformabilidades da fundação e da superestrutura. A hipótese de apoios indeslocáveis ignora o recalque diferencial e a redistribuição que ele causa.
- Efeitos típicos: os pilares mais carregados (centrais) recalcam mais, viram apoios "moles" e a carga migra para os pilares de periferia. As vigas perdem momento negativo nos apoios centrais e ganham momento positivo no vão. O momento de base dos pilares sob vento cai, e parte dele sobe para os pavimentos de cima.
- A redistribuição se concentra nos primeiros pavimentos. Com superestrutura rígida, ela se propaga para cima (Moura 1995; Antunes e Iwamoto 2000).
- Sequência construtiva: ISE sem faseamento considera a estrutura inteira rígida desde o início e **subestima** os recalques diferenciais. Sem ISE, eles ficam superestimados (Fonte et al. 1994).
- Prédios vizinhos: há sobreposição de bulbos e tombamento induzido conforme a época de construção (Costa Nunes 1956).
- Fundação rígida não quer dizer base engastada. O engaste depende também da rigidez do solo.

## 3. Níveis de modelagem
| Nível | Como | Quando |
|---|---|---|
| 0 | Apoios indeslocáveis | Solo muito rígido (rocha, estaca em rocha), pré-dimensionamento |
| 1 | Molas de Winkler por apoio (Kv, Kh, Kθ), lineares | Rotina de projeto: sapatas, blocos e pré-moldados com pilar engastado em cálice |
| 2 | Molas iteradas: recalque de cada apoio calculado com as reações da etapa anterior (Aoki-Lopes, Schmertmann) até convergir | Quando os bulbos dos vizinhos interagem |
| 3 | MEF 3D contínuo: solo em camadas + sapatas + pórtico, solo Drucker-Prager | Estudo, aferição das molas, obras especiais |

Molas isoladas **não** captam a influência dos pilares vizinhos (bulbos superpostos). O MEF contínuo capta.

## 4. Parâmetros do solo a partir do SPT (correlações usadas na fonte; conferir com ensaio)
- N_SPT brasileiro corresponde a cerca de 72 % de eficiência. Converter quando a correlação vier de outro padrão (N60).
- E do solo, simplificado pela fonte a partir de Hachich et al. (1998), em MPa: areias 3,5·N; solos intermediários 3,0·N; argilas saturadas 2,5·N. Vale para sapata quadrada rígida com recalque da ordem de 1 % do lado. (conferir: Teixeira e Godoy usam E = α·K·N com α e K tabelados)
- ν: areia fofa 0,2; areia compacta 0,4; silte 0,3–0,5; argila saturada 0,4–0,5; argila não saturada 0,1–0,3 (Hachich et al. 1998).
- c e φ por camada a partir do N_SPT: tabela de Joppert Jr. (2007). Na fonte a tabela está em imagem; os valores usados foram φ = 20–27°, c = 20–50 kPa.
- Dilatância ψ: ψ = φ dá fluxo associado (o que a fonte adotou). ψ < φ dá fluxo não associado, e ψ = 0 conserva volume. Para solos reais, ψ ≈ φ − 30° em areias (conferir); ψ = φ superestima a dilatação.
- Tensão admissível de sapata (Mello 1975): σa = 100·(√N − 1) kPa, com N médio entre a cota de apoio e o fim do bulbo L_b = 2B a 3B (B = menor lado; Joppert 2007). Iterar B ↔ N médio.
- Concreto: E = Ecs (NBR 6118 8.2.8), ν = 0,2.

## 5. Rigidez das molas (sapata rígida, semiespaço homogêneo; Gazetas 1991)
Com G = E/[2(1+ν)], L ≥ B as semidimensões, χ = A/(4L²):
- Vertical: Kv = 2GL/(1−ν)·(0,73 + 1,54·χ^0,75). Para sapata quadrada de lado a, dá Kv ≈ 2,27·G·a/(1−ν) ≈ E·a/[(1−ν²)·0,88], o mesmo que a sapata rígida com Iw = 0,88.
- Horizontal: Ky = 2GL/(2−ν)·(2 + 2,5·χ^0,85).
- Rotação em torno do eixo longo: Kr = G/(1−ν)·Ib^0,75·(L/B)^0,25·(2,4 + 0,5B/L). Para sapata quadrada, ≈ 0,45·G·a³/(1−ν). (conferir)
- Coeficiente de reação equivalente: kv = Kv/A (kN/m³).
- O embutimento e uma camada rígida rasa aumentam a rigidez (fatores de Gazetas; conferir). Sem essas correções, o modelo fica a favor de mais redistribuição.
- Estacas: mola axial = EA/L do fuste **em série** com a mola do solo (recalque da estaca). Em blocos, uma mola por estaca (ver skill principal §22.5: solo rígido dá reações desiguais).

## 6. Modelo MEF contínuo (receita da fonte, para replicar no OpenSees)
- Elementos: vigas e pilares em barra Timoshenko quadrática (BEAM189, 10 elementos por barra); lajes em casca de 8 nós (SHELL281, 10×10); sapatas e solo em sólido de 8 nós (SOLID65, malha de 50 cm); concreto elástico linear.
- **Ligação pilar–sapata:** o sólido só tem translações. Um nó de barra ligado a um nó de sólido vira **rótula**. Solução da fonte: placa (SHELL181) com a seção do pilar e E altíssimo na face da sapata, que transmite o momento por binário de forças nodais. No OpenSees: `rigidLink('beam', nó_pilar, nós_da_face)` ou um conjunto de barras rígidas radiais.
- Interface solo–sapata: nós compartilhados (aderência perfeita). Isso superestima a aderência; um elemento de contato daria mais redistribuição.
- Contorno do maciço: base fixa em x, y e z, à profundidade do impenetrável/fim do SPT. Faces laterais com rolete na normal.
- Tamanho do maciço por estudo de convergência: modelo elástico, sem superestrutura, com 2× a carga do pilar mais carregado em todas as sapatas, aumentando a folga lateral até o recalque estabilizar. Na fonte, a folga ficou em 12,6 m além das sapatas extremas, com maciço de 35,2 × 11 × 40,2 m.
- Solução não linear: carga incremental (75 a 500 subpassos), Newton-Raphson modificado, convergência em deslocamento com tolerância de 1 %.
- Verificação antes do uso: pórtico comparado com o TQS (as diferenças vêm da rigidez à torção das vigas, que o TQS despreza) e sapata rígida em argila (φ = 0, von Mises): Smith, Griffiths e Margetts 2014 com E = 105 MPa, Su = 100 kPa; Chen e Mizuno 1990 com E = 206 MPa, Su = 120 kPa; e Drucker-Prager com c = 69 kPa, φ = ψ = 20°.

## 7. Exemplo da fonte e resultados
- Edifício comercial em Porto Alegre, 3 pavimentos de 3 m, 2 × 3 vãos de 5 m. Pilares 25×25, vigas 25×50, lajes de 10 cm, C30 (E = 27 GPa).
- Sapatas iguais de 180×180×100 cm. SPT de 11 m na zona norte, em 11 camadas de 1 m com E = 3,3–8,4 MPa, c = 20–50 kPa, φ = 20–27°, ψ = φ, ν = 0,3.
- Cargas: PP com 25 kN/m³; alvenaria de 2,3 kN/m² × altura; uso de 2,5 kN/m²; vento com V0 = 45 m/s e S1 = S2 = S3 = 1, q = 0,613·Vk², Fa = Ca·q·Ae.
- Combinações: ELS-QP = G + 0,4Q; ELU = 1,4G + 1,4(W + 0,7Q).
- Resultados (ISE contra engastado):

| Grandeza | Variação com ISE |
|---|---|
| Vigas, M− nos apoios centrais (plano do vento) | até −65 % |
| Vigas, M+ no vão (plano do vento) | até +16 % |
| Vigas, M− / M+ (outro plano) | até −33 % / +7 % |
| Pilares, M crítico (plano do vento) | até ±18 %; inversão de M nos pilares do pórtico central |
| Pilares de fachada | **acréscimo** de momento (recebem a redistribuição) |
| Vigas, cortante | ligeiramente menor |
| Flechas das vigas de cobertura | cerca de 2× (ainda < L/250) |
| Normal nos pilares | variação pequena |

- O teste rápido do `ise_nd` (pórtico de 3 pavimentos, molas de Gazetas, E = 60 MPa, sapata de 1,8 m) deu −48 % no M− do apoio central da viga do 1º pavimento. É a mesma ordem de grandeza da fonte.

## 8. Critérios de verificação
- Distorção angular β = δ/L (Skempton e MacDonald 1956; Bjerrum): danos estruturais se β > 1/150; trincas em paredes se β > 1/300; limite recomendado 1/500.
- Recalque total (Terzaghi e Peck 1967): 25 mm em areias e 40 mm em argilas, para sapatas isoladas.
- Flechas: NBR 6118:2023 tab. 13.3, no mínimo L/250 (aceitabilidade visual), **somando o recalque diferencial** dos apoios.
- Pré-dimensionamento usado pela fonte: lajes h = L/50 a L/40; vigas h ≈ L/10; pilar Ac = (Nd/σid)·γcorr com γcorr = 2 até 30 m de altura e 3 acima (Melo 2013); sapata A = P/σa; sapata rígida se h ≥ (a − ap)/3 (NBR 6118 22.6.1).

## 9. Roteiro ND (rotina de projeto, nível 1–2)
1. Ler o SPT e definir camadas, N médio no bulbo, E, ν (e c e φ se for usar o MEF 3D).
2. Pré-dimensionar as sapatas com reações de base engastada (Mello: σa) ou ler o projeto existente.
3. Calcular as molas (Kv, Kh, Kθ) de cada apoio com `molas_sapata`. Estacas: EA/L em série com a mola do solo.
4. Rodar o pórtico com molas na combinação **característica ou quase permanente**. A rigidez do solo é calibrada para serviço: não majorar a carga no solo não linear.
5. Se as reações mudarem mais de 10 %, recalcular os recalques (com a influência dos vizinhos) e as molas, e iterar (nível 2).
6. Com as molas fixadas, rodar as combinações de ELU no modelo linear e fazer a envoltória **das duas hipóteses** (engastado e ISE). Dimensionar pelo pior caso de cada seção: a ISE alivia uns elementos e carrega outros.
7. Verificar β, recalque total, flechas com recalque e o γz/2ª ordem com as molas de rotação (pilar em balanço de pré-moldado é muito sensível a Kθ).
8. Memória: correlações usadas, faixa de E, sensibilidade (E × 0,5 e × 2) e limitações.

## 10. Armadilhas e ressalvas
- **ISE nem sempre traz economia.** A fonte conclui "mais seguro e econômico", mas os pilares de fachada e o M+ das vigas **aumentam**. O correto é dizer "mais realista" e dimensionar pela envoltória.
- A fonte rodou o solo não linear sob cargas de ELU (γ = 1,4). Isso superestima a plastificação do solo. Geotecnia (NBR 6122) trabalha com cargas características.
- O concreto ficou elástico com rigidez bruta. Com as reduções da NBR 6118 15.7.3 (0,4EI em vigas, 0,8EI em pilares; conferir na 2023), a estrutura fica mais flexível e a redistribuição diminui. Testar as duas.
- Sapatas todas iguais à do pilar mais carregado distorcem os recalques diferenciais. Usar as dimensões reais.
- Interface aderente (sem contato) e falta de faseamento construtivo também distorcem os resultados.
- E vindo do N_SPT tem incerteza de ±50 % ou mais: fazer análise de sensibilidade.
- Em barracões pré-moldados (pilar engastado em cálice), a rotação da fundação aumenta o deslocamento no topo e o efeito de 2ª ordem. Considerar Kθ na verificação de ELS e de estabilidade global.
- Fatores de vento da fonte: S2 = 1 é simplificação. Usar S2 real (NBR 6123:2023).
- NBR 6122: conferir os itens que pedem ISE e o monitoramento de recalques para edifícios altos (≥ 55 m na edição de 2019/2022; conferir).

## 11. Referências úteis citadas pela fonte
Antoniazzi (2011, UFSM, dissertação sobre ISE com fundações superficiais); Souza e Reis (2008, Acta Sci.); Hachich et al., *Fundações: teoria e prática* (1998); Joppert Jr. (2007); Chen e Mizuno, *Nonlinear Analysis in Soil Mechanics* (1990); Smith, Griffiths e Margetts, *Programming the FEM* (2014); Espinoza (2022, UFRGS, grupos de estacas por MEF); Rachinhas (2020, UFRGS, processo construtivo); Junges (2016, UFSC, pórticos NLF/NLG).