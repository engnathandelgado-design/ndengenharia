# Letsara — Rodada 1 de pré-dimensionamento (12/10/2026)

Script: `calc_letsara.py`. Os números completos estão em `resultados.json`. Este é um pré-dimensionamento e precisa ser confirmado no cálculo executivo.

## Premissas a confirmar
- **Vento:** V0 = 45 m/s, local ainda não informado. Terreno categoria III, classe C. Cpe da parede: +0,7 a barlavento e −0,5 a sotavento. Cpe da cobertura −0,8 e Cpi +0,2. Resulta q = 0,97 kN/m².
- **Cobertura:** permanente de 0,25 kN/m² (telha, terças e instalações) e sobrecarga de 0,25 kN/m².
- **Mezanino:** sobrecarga de 5,0 kN/m² (500 kgf/m²), revestimento de 1,0 kN/m², capa de 5 cm.
- **Concreto:** peças em C40, com fckj = 28 MPa na liberação. Cordoalhas CP-190 RB 12,7.
  - Perdas diferidas adotadas em 17 % de σpi.
  - Classe de agressividade II, protensão limitada (pré-tração).
- **Placas:** 2,5 kN/m², penduradas fora do pilar. A excentricidade de 0,40 m gera um momento permanente na base do pilar lateral de 97 kN·m.
- **Pilares:** analisados pelo método geral no OpenSeesPy, com fibras, corrotacional, fluência φef e imperfeição θ1. A ruptura é dada por εcu ou por 10‰ no aço.
  - Pilares independentes: a viga de cobertura não foi contada como escora. Isso deixa o resultado do lado da segurança.

## Resultados

| Peça | R01 | Menor seção que passa | Recomendação |
|---|---|---|---|
| Viga I de cobertura, L ≈ 19,2 m, 3 % | 90 cm | **I70** (mesas de 40, alma de 10 a 12), 8 cordoalhas Ø12,7, 8,6 t | I70 com alma de 12, ou I80 se a fábrica quiser mais rigidez lateral no içamento |
| Viga central V407, 19 m | 40×100 | 40×100 com 20 cordoalhas, ou I100/60 | 40×100 protendida |
| Viga central V406 e V405, 23 m, recebendo 2 linhas de vigas I | 40×100 | **40×100 não passa.** 40×120 com 26 cordoalhas (29 t) ou I120/60 com 22 cordoalhas (24,5 t) | Ver a questão 1 abaixo |
| Pilar lateral P1/P2, 10 m em balanço | 40×60 | 40×60: 5Ø25 por face (2,0 %) | 40×60. O 40×50 pede 2,95 % de aço e desloca 26 mm em serviço |
| Pilar de fachada, vento longitudinal | 40×60 | 40×60 com o 60 perpendicular à fachada, 6Ø25 por face | Orientar o 60 na direção do vento longitudinal. Com o 40 nessa direção não passa |
| Pilar central P11 (2 vigas I + V406 + V407) | 40×40 | **40×40 não passa** (λ = 173). 45×45: 6Ø20; 50×50: 6Ø12,5 | 50×50 |
| Viga de mezanino, laje de um lado | 25×60 | 40×70 com 14 cordoalhas, ou I80 com 10 | 40×70. Torção de montagem de 41 kN·m: interação de 0,40, mais estribo de torção de 3,0 cm²/m por ramo e armadura longitudinal de 5,1 cm² |
| Laje alveolar, 500 kgf/m², vão ≈ 9,6 m | h16/h20 | Md ≈ 170 kN·m/m | **h26,5 + 5**, com 6 cordoalhas Ø12,7 por painel de 1,25 m. Conferir na tabela do fabricante |
| Terças metálicas Ue, vão ≈ 9,25 m | ≈ 1,20 m | a 1,20 m: Ue 250×85×25×3,00 (9,0 kg/m²); a 1,60 m: Ue 300×85×25×3,00 (7,5 kg/m²); a 2,0 m ou mais nenhum Ue passa | 1,60 m, com correntes a L/3, se a telha vencer esse vão. Seção bruta; conferir a largura efetiva (NBR 14762) |

## Versão sem vigas de travamento
Passa. No sentido longitudinal, o pilar lateral só leva a imperfeição global e fecha com armadura mínima (5Ø12,5 por face no 40×60, λ = 173, método geral).

As vigas de travamento V401–V404 não mudam o comprimento de flambagem (le = 2L), porque não há ponto contraventado. Quem segura o vento longitudinal são os pilares das fachadas, cada um no seu balanço. Portanto, sem travamento é preciso:
- pilar de fachada com o 60 na direção longitudinal;
- terças ligadas e contraventamento metálico em X nos vãos extremos da cobertura, para a montagem e para a transferência de esforços (detalhar).

## Pontos de atenção que saíram do cálculo
- **Sucção na viga I:** a carga de vento para cima (9,4 kN/m) supera o peso. Isso dá 61 kN de arrancamento de cálculo por apoio, que precisa de chumbador ou pino verificado à tração. Também pede 11,5 cm² de armadura passiva no topo da I70 para o momento negativo de 300 kN·m.
- **Ato da protensão nos apoios:** isolar cordoalhas nas pontas das vigas I, centrais e de mezanino. A viga de mezanino precisa de 2 cordoalhas superiores.
- **Torção na viga central:** sai baixa com e = 0,25 m (interação de 0,15 a 0,45). Ela é governada pela montagem com as vigas I de um lado só.
- **Deslocamento de serviço do pilar lateral** (vento frequente): 15 mm no 40×60. Atende H/500, mas não atende H/1700 da NBR 6118 13.3. Decidir o critério adotado para pavilhão com placas fixadas por pino e furo oblongo.

## Rodada 1b (12/10/2026) — decisões de Nathan
- **Vão central mantido**, com vigas centrais em **seção I**. As vigas I de cobertura apoiam em **consolos na viga central**, com **enrijecedor de concreto** (diafragma maciço) em cada linha. Todas as vigas são protendidas com cordoalhas Ø12,7 nuas, aderentes (pré-tração).
- **V0 = 45 m/s** confirmado.
- **Telha:** aço 0,5 mm com PIR de 30 mm (≈ 0,07 kN/m²; o cálculo usou 0,10). Terças a 1,60 m com Ue 300×85×25×3,00.
- **Vigas centrais, forma única I110** (mesa superior 50, mesa inferior 60, alma 20):
  - V406 e V405 (23 m): 24 cordoalhas, 22,2 t, flecha final de 35 mm (limite de 92 mm).
  - V407 (19 m): 16 cordoalhas, 18,1 t.
- **Pilar lateral para H/1700:** 40×80, com 4,5 mm em estádio I. Sob vento frequente, o momento (≈ 195 kN·m) fica abaixo do momento de fissuração (≈ 210 kN·m). Com 40×60, o deslocamento é de 10,7 mm, o que atende só H/500.

## Rodada 2 (12/10/2026) — refinada e com cordoalhas na grade da cabeceira

**Cordoalhas na grade dos cabeçotes REV05.**
- Cabeçote inferior: 7 × 5 furos Ø17, passo 50 × 42 mm. Linha de baixo adotada a 75 mm do fundo da fôrma.
- Cabeçote superior: 2 linhas, a partir de 1.050 mm do fundo da fôrma.

**Refinamentos em relação à rodada 1:**
- vento com S3 = 0,95, o que dá q = 0,874 kN/m²;
- ψ2 = 0 na sobrecarga de cobertura;
- ELU por compatibilidade de deformações, com σpd de cerca de 1.570 MPa;
- viga I funcionando como escora do pórtico e travamento + contraventamento repartindo o vento longitudinal entre 24 pilares (8,1 kN por pilar).

| Peça | Seção | Cordoalhas Ø12,7 (na grade) | Peso | Obs. |
|---|---|---|---|---|
| Viga I de cobertura | I70 (mesas 40×12, alma 12) | **7** (1 linha completa) | 9,1 t | Flecha final de 25 mm |
| Viga central V406/V405 (23 m) | I120 padrão (mesas 40×25, chanfro 15, alma 20) | **21** (3 linhas de 7) | 22,3 t | Com C50, a I110 passa com 23 a 24 cordoalhas |
| Viga central V407 (19 m) | I110 padrão | **14** (2 linhas de 7) | 17,2 t | |
| Pilar lateral 40×60, transversal | 5Ø20 por face | — | — | Deslocamento de serviço de 8,3 mm |
| Pilar lateral 40×60, longitudinal com travamento | 4Ø25 por face | — | — | Recebe parte do vento das fachadas |
| Pilar de fachada 40×60 (40 na direção do vento) | 5Ø25 por face | — | — | Mesma orientação dos pilares laterais |

Com a viga I de cobertura no padrão de mesas 40×25 (I90), as vigas centrais de 23 m não passam nem em I120. A cobertura tem que ser a I70 de mesas finas.
