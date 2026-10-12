---
name: "vigas-premoldadas-protendidas"
description: "Use ao calcular, detalhar, desenhar a prancha de produção ou prever/analisar ensaio de vigas pré-moldadas protendidas (pré-tração, cordoalhas retas, isolamento) e vigas L de borda (spandrel: aba, torção de equilíbrio, suspensão, consolo de extremidade), e ao ensinar o tema."
---

# Vigas pré-moldadas protendidas — cálculo, detalhamento e prancha de produção

Complementa `projetos-estruturais-concreto-armado-protendido` (teoria, perdas, ELS/ELU, seção composta — seções 1–14) e `pranchas-tecnicas-nd` (motor gráfico `prancha_nd.py`, padrão ND, QA). Aqui fica a **receita de peça de fábrica**: o que calcular, como detalhar e o que a prancha de produção precisa conter. Responder em português técnico, citando NBR 6118:2023 e NBR 9062:2017; itens com (conferir) devem ser checados na norma vigente. Vigas L de borda (spandrel): seção 11.

## 1. Fonte
- *PCI Big Beam Competition 2015 — Mr. Beam (Team #2)*, University of Washington, orient. Prof. John Stanton; produtor Concrete Technology Corp. (CTC, Tacoma). Relatório de 35 p. (disponibilizado pelo Prof. Paulo Bastos, UNESP-Bauru, material de pré-moldados). Base ACI 318-11 e PCI Design Handbook, unidades americanas — convertido para SI e NBR aqui. Lido integralmente em 07/10/2026 (texto por pdf.js + pranchas renderizadas).
- Nível: graduação (equipe sem curso prévio de protendido) — ótimo como estudo de caso de aula e como checklist de peça real.
- Seção 11: Raths (1984), *Spandrel Beam Behavior and Design*, PCI Journal — mesmo acervo do Prof. Paulo Bastos; ver 11.1 para a data e o que foi superado depois.

## 2. A viga (dados para replicar)
| Item | Valor (original → SI) |
|---|---|
| Comprimento / vão de ensaio | 18'-0" = 5,49 m / 17'-0" = 5,18 m (apoios a 1'-0" das pontas) |
| Carregamento | 2 cargas concentradas a 7'-0" = 2,13 m dos apoios (trecho central de 0,91 m) |
| Seção I constante | h = 18" = 457 mm; mesas 6" = 152 mm (sup. 5" = 127, inf. 4" = 102); alma 2,5" = 64 mm × 7"; chanfros 1" de altura × 1,75" |
| Propriedades (conferidas) | A = 80 in² = 516 cm²; yb = 9,175" = 233 mm; I = 2755 in⁴ = 1,147·10⁻³ m⁴; Wb = 300 in³ = 4,92·10⁻³ m³ |
| Enrijecedores | 4 alargamentos da alma até a largura da mesa (9" = 229 mm) nos apoios e nos pontos de carga, transição em chanfro de 3" |
| Concreto | leve (agregado graúdo e miúdo leves), a/c 0,40, γ = 17,2 kN/m³; f'ci liberação 5000 psi = 34,5 MPa; f'c 28 d projeto 9000 psi = 62 MPa, real 9170–9220 psi ≈ 63 MPa; MOR 986 psi = 6,8 MPa |
| Protensão | 4 cordoalhas ½" (12,7 mm, 0,1519 in² = 98 mm²) ASTM A416 gr. 270 RB (fptk 1862 MPa), retas, a 2/4/6/8" da base (CG a 127 mm; dp = 330 mm); tensionadas a 30,9 kip/cord. = 137 kN (σpi = 0,75 fptk); σpe estimada 170,9 ksi = 1178 MPa (perdas ≈ 16 %) |
| Isolamento | trecho **central** de 11' = 3,35 m isolado com bainha plástica; ~0,9 m aderente em cada ponta; cunhas (strand chucks) + chapa nas pontas instaladas antes do ensaio |
| Passiva | 2 barras #3 (Ø10) CA-60 equiv. na mesa superior (ancorar estribos, compressão no ELU, tração no ato) |
| Transversal | tela soldada W2.9 (Ø4,9 mm) malha 3"×3" (76 mm) dobrada em U estreito ao longo de toda a viga; U largo nos enrijecedores; gaiola retangular de confinamento na mesa superior no trecho central |
| Peso | 4,83 kN (1,09 kip) |

## 3. Cálculos do relatório (conferidos em Python — seção 8)
1. **Fissuração** (seção bruta, sem peso próprio): −Pe/A − Pe·e/Wb + Mcr/Wb = fct → Mcr = (fct + Pe/A + Pe·e/Wb)·Wb. Com Pe = 103,8 kip (462 kN), e = 4,175" (106 mm), fct = 0,965 ksi (6,65 MPa): Mcr = 1113 kip·in (125,8 kN·m) → P = 2Mcr/a = 26,5 kip (118 kN). Ensaio: 26,0 kip (115,6 kN). ✔
2. **Ruptura**: tensão σps assumida → T = Ap·σps; a = T/(0,85 f'c b); Mn = T(dp − a/2). Com ε_ps total = 1 % e a fórmula de potência do PCI para gr. 270 [fps = 268 − 0,075/(εps − 0,0065) ksi] → 246,6 ksi (1700 MPa); a = 3,19" (81 mm); Mn = 1708 kip·in (193 kN·m) → Pu = 40,7 kip (181 kN). Ensaio: 40,8 kip (181,5 kN). ✔
3. **Flecha na ruptura** (mecanismo de corpos rígidos: 2 metades girando em torno de uma rótula no meio do vão, cordoalha não aderente alonga uniformemente no trecho isolado): ΔL = Δεp·L_isol; θ = ΔL/(dp − c); δ = (vão/2)·θ. Com Δεp = 1 % − 0,602 % e L_isol = 127,3" → δ = 6,39" (162 mm) + contraflecha/fissuração = 6,69". Ensaio: **2,23" (57 mm) — erro de 3×**.
4. **Retroanálise**: M total na ruptura = 1740 kip·in (com peso próprio) → T ≈ 152 kip → σps ≈ 250 ksi ≈ 1730 MPa, ou seja, a cordoalha chegou perto do escoamento (fpy do certificado = 261 ksi = 1802 MPa), mas a flecha foi limitada pelo concreto.

## 4. Lições de cálculo (aplicadas à NBR)
- **Fissuração** se prevê bem com seção bruta + tensão efetiva + resistência à tração na flexão. Pela NBR (17.3.1 / 13.4.2): α·fctm com α = 1,3 (seção I) e fctm = 2,12·ln(1 + 0,11 fck) para > C50 → 5,71 MPa → Pcr = 113,5 kN (−1,8 % do ensaio). Para previsão de ensaio use o MOR medido; para projeto, fctk,inf.
- **Cordoalha não aderente em peça robusta** (L/h = 11,3): a expressão de acréscimo de tensão (ACI 18-2; NBR 6118 17.2.2: Δσp = 70 + fck/(100ρp) ≤ 420 MPa para L/h ≤ 35) dá σps = 1178 + 151 = 1329 MPa → Pu = 145,8 kN (−20 %). É **conservadora para resistência**; a viga real atingiu σps ≈ fpy (com σps = fpy, Pu = 190 kN, +5 %). Para prever ensaio: σps entre a fórmula e fpy; para projeto: manter a norma.
- **Flecha última não se calcula pela deformação da cordoalha** quando a ruptura é por esmagamento: a rotação da rótula é limitada por εcu do concreto (θ ≈ εcu·lp/c, lp = comprimento da rótula plástica — conferir modelo), e a ruptura veio antes de a cordoalha chegar a 1 %. Isolar cordoalhas para "ganhar ductilidade" não funcionou: a mesa comprimida governou.
- Com isolamento central, a deformação concentra numa **fissura única** no meio do vão e a deformada fica em V (rótula), não em U (curvatura distribuída) — o oposto do comportamento aderente, que distribui fissuras.
- **Erros encontrados no relatório** (servem de alerta para memória ND): (i) planilha de área usou só um chanfro (75,75 in²) enquanto o cálculo de fissuração usou 80 in² — compatibilizar a seção num só lugar; (ii) na ACI 18-2 somaram f'c (9,2 ksi) no lugar da constante 10 ksi (191,9 × 192,7 ksi — efeito pequeno, mas é erro de fórmula); (iii) relatório diz tela 3×3 e barras #3, a prancha diz 4X4-W2.9 e marca 401 — prancha e memória têm de dizer a mesma coisa.

## 5. Detalhamento — o que a peça ensina
1. **Seção I prismática com cordoalhas retas** simplifica forma e pista (a equipe anterior teve problemas com seção variável). Seção I > T para tombamento lateral; rendimento melhor que retangular (ver seção 10.11 da skill principal).
2. **Enrijecedores (alma alargada) em todo ponto de carga concentrada e apoio**, com armadura própria (U largo amarrado à gaiola superior). Em 2014 os enrijecedores romperam de forma frágil; em 2015, mais largos e armados, ficaram íntegros. Em projeto ND: apoios de viga I sobre consolo/neoprene e pontos de carga de terças/lajes → alargar a alma (bloco de extremidade) e armar para a região D (bielas e tirantes / NBR 9062).
3. **Estribos contínuos** ao longo da viga com taxa alta para garantir ruptura por flexão (a equipe de 2014 teve cordoalhas "estourando" a alma fina). Em alma de 64 mm, o estribo em U de tela dá cobrimento de ~13 mm — só aceitável em peça de ensaio; em obra respeitar cobrimento da CAA (NBR 6118 tab. 7.2, pré-moldado com controle rigoroso pode reduzir 5 mm — NBR 9062, conferir) → alma mínima prática ≈ 100–120 mm.
4. **Gaiola de confinamento na mesa comprimida** no trecho de momento máximo aumentou a deformabilidade do núcleo (o concreto dentro da gaiola ficou íntegro; esmagou o cobrimento acima dela). Simplificar a geometria da gaiola: a forma ideal no limite da norma não foi executável.
5. **Barras passivas superiores** para tração no ato da protensão (NBR 6118 17.2.4.3.2: σct ≤ 1,2 fctm,j, senão armadura) e para ancorar os estribos.
6. **Ancoragem das cordoalhas**: comprimento aderente de ~0,9 m é curto para lbd de Ø12,7 (verificar lbpt e lbd — NBR 6118 9.4.5). Prevenção: cunhas na ponta com espaçador removível. Não houve escorregamento (concreto de 63 MPa + estribos ajudaram a aderência).
7. **Dobramento**: a tela era frágil demais para dobrar a frio em raio pequeno e foi dobrada com maçarico. Em obra no Brasil **não aquecer CA-60/tela** (NBR 14931 — conferir item); especificar estribo dobrado em máquina ou tela pré-dobrada de fábrica com diâmetro de pino da NBR 6118 9.4.
8. **Insertos**: 2 alças de içamento (ancoragem 2,5 t com nicho de 3/8") a 1'-0" das pontas; chapas 6×10×½" com 2 pinos 3/8"×4" nas extremidades (apoio da cunha). Içamento, estocagem e transporte apoiados no mesmo ponto (1'-0" de cada ponta).

## 6. Produção e controle (checklist de fábrica)
- Sequência: armação (cortar/dobrar telas) → montagem na forma → passar cordoalhas embainhadas → **conferir comprimento das bainhas antes de concretar** (aqui variavam 10,0–10,9 ft para 11 ft de projeto) → protensão em 2 etapas (50 % → conferir posição da armação → 100 %) → concretagem no dia seguinte → liberação aos 7 dias com fckj comprovado (CP curado com a peça).
- Controle do concreto: curva resistência × idade (cilindros a 1, 3, 6, 7, 14, 21, 28 d), MOR em prismas, Eci; traço com correção de umidade dos agregados (planilha de traço da fábrica no anexo).
- Certificados da cordoalha que acompanham a entrega: relatório de inspeção (lote, especificação, carga de ruptura/escoamento a 1 %), composição química, curva carga × deformação com área e módulo (aqui 0,1519 in², 28,4 Msi = 196 GPa, escoamento 39,7 kip).
- Ensaio (4 pontos): pré-carga de 5 kip para testar instrumentos → descarregar e zerar → carregar até 22 kip, parar e inspecionar fissuras de perto → levar à ruptura. Potenciômetros por fio presos a barra colada entre os pontos de carga + régua no meio do vão como redundância; 2 câmeras de vídeo para correlacionar carga × fissura (fissura em protendido é difícil de ver). Cada membro com uma função (tempo, aquisição, vídeo, foto, fissuras).

## 7. Prancha de produção — padrão de fábrica e como a ND entrega

### 7.1 O que a prancha da CTC tem (1 folha 11×17" paisagem por marca de peça)
- **Vistas**: PLAN VIEW (topo: comprimento de concretagem, insertos de içamento cotados das pontas) · ELEVATION (forma: cadeia de cotas ao longo do comprimento — 9" / 6'-4½" / 9" / 2'-3" / 9" / 6'-4½" / 9" — enrijecedores, chanfros, alturas parciais, projeção das cordoalhas "PROJ", marcadores de corte A e B) · REINFORCEMENT ELEVATION (trechos de tela W1/W2/W1, barras com bolha de marca, cunhas "install after casting", projeção 1'-0") · TYPICAL END VIEW (grade das cordoalhas "(3) sp @ 2" = 6"", chapa A, nota "DEBOND 11'-0" AT CENTER, (4) PLACES") · SECTION A (no enrijecedor) · SECTION B (típica), com cobrimentos "½" CLR. TYP.".
- **Coluna direita**: REINFORCEMENT SCHEDULE (grau, marca da barra, quantidade, reta/nº de dobras, comprimento de corte, croqui de dobra; legenda tipo–bitola–nº, ex. X402) · WWR SCHEDULE (marca, descrição 4X4-W2.9xW2.9, quantidade, comprimento) · GENERAL NOTES (concreto: resistência na liberação e aos 28 d; protensão: cordoalha, grau, relaxação, "STRAIGHT: (4) strands jacked to 123.6 kips (30.9 k/str.)"; acabamentos por face — topo desempenado, laterais/fundo/pontas de forma; YARD HAULING / STORAGE BUNKING / SHIPPING BUNKING a 1'-0" das pontas) · INSERT & ASSEMBLY SCHEDULE (marca, descrição, prime/galv, quantidade por peça e total).
- **Carimbo**: "PRODUCTION DRAWING", PRODUCT MARK BM-2, QTY 1, WT 1.23 KIPS, Dwg No., Job No., data; bloco do fabricante e do cliente; projeto/desenho/verificação/aprovação; **"DO NOT SCALE"**; nota de propriedade intelectual; selo exigido ("WSDOT STAMP REQ'D"); "MARKED END" no canto (orientação da peça na pista).
- **Revisões com status**: Rev 0 SUBMITTAL (para aprovação, 10/03) → Rev 1 FOR CONST. (liberado para produção, 17/03), com "by / app'd / date" e triângulo de revisão junto ao nº do desenho.
- **Ficha de insertos separada** (HARDWARE ORDER, 4 cartões por folha): por conjunto metálico — croqui cotado (chapa, furos, pinos), Assembly A, Make 2, aço, chumbadores, peso (8 lb), acabamento (prime/galv), bordas, instruções especiais, job/data/folha.

### 7.2 Adaptação ND (usar com `prancha_nd.py`)
- **Uma prancha por marca de peça** (V-01, V-02…), A2 ou A3, título "PRANCHA DE PRODUÇÃO — PEÇA V-01"; no carimbo: MARCA, QUANT., PESO (kN), VOLUME (m³), pista/forma, fase (PARA APROVAÇÃO → LIBERADO PARA PRODUÇÃO) e a nota "NÃO MEDIR NO DESENHO".
- **Vistas mínimas**: PLANTA (topo, insertos) · ELEVAÇÃO DE FORMA (cadeia + total, enrijecedores, chanfros, dentes/consolos, cortes) · ELEVAÇÃO DE ARMAÇÃO (trechos de estribo por espaçamento, posições N, cordoalhas com **trecho isolado cotado e lado**, projeção das pontas) · VISTA DE TOPO (grade das cordoalhas cotada, quais isoladas) · CORTE TÍPICO e CORTE NO ENRIJECEDOR/APOIO (cobrimentos).
- **Tabelas (coluna direita)**: RELAÇÃO DO AÇO + RESUMO (padrão ND) · **TABELA DE CORDOALHAS** (posição, Ø, quantidade, força por cordoalha na pista, alongamento teórico ΔL = P·L_pista/(Ep·Ap), comprimento isolado e extremidade) · TABELA DE INSERTOS (alças, chapas, tubos, quant. por peça/total, acabamento galvanizado/pintado, ficha de referência).
- **Notas paramétricas**: fck; **fckj para liberação, desforma e içamento**; CAA e cobrimento; aço CP-190 RB e força por cordoalha; sequência de protensão (etapas) e de liberação (simétrica); conferência dos isolamentos antes da concretagem; acabamento por face; pontos de içamento, estocagem e transporte (posição cotada; coef. dinâmicos NBR 9062 — conferir); tolerâncias de fabricação NBR 9062; "EXTREMIDADE MARCADA" para orientação.
- **Ficha de insertos** em A4 separada por conjunto (croqui cotado, aço, chumbadores, peso, acabamento, quantidade).
- **Pacote de entrega**: pranchas de produção + fichas de insertos + memória de cálculo + (quando houver ensaio/controle) traço, curva fckj × idade e certificados das cordoalhas.

## 8. Código validado (`viga_ensaio_nd.py`, rodado em 07/10/2026)
| Teste | Resultado | Referência |
|---|---|---|
| Seção I Big Beam: A, yb, Wb | 516 cm², 233 mm, 4,92·10⁻³ m³ | 80 in², 9,175", 300,26 in³ (relatório) |
| Pcr com fct = 6,65 MPa | 117,9 kN | 26,5 kip = 117,9 kN (relatório); ensaio 115,6 |
| Pcr com α·fctm NBR (5,71 MPa) | 113,5 kN | ensaio 115,6 (−1,8 %) |
| Pu com εps = 1 % (PCI) | 180,9 kN | 40,7 kip = 181,0 (relatório); ensaio 181,5 |
| Pu com Δσp NBR 17.2.2 | 145,8 kN | ensaio 181,5 (−20 %, conservador) |
| Flecha pelo mecanismo | 162 mm | 6,39" = 162 mm (relatório); ensaio 57 mm |

```python
"""viga_ensaio_nd.py — previsão de fissuração, ruptura e flecha última de viga pré-tracionada
biapoiada com 2 cargas concentradas (ensaio de 4 pontos), cordoalhas retas com trecho central isolado.
Unidades: kN, m, kPa (MPa só na entrada). Base: PCI Big Beam 2015 (UW)."""
import math

def secao(partes):
    """partes = [(b_inf, b_sup, h)] de baixo para cima (trapézio; retângulo se b_inf = b_sup). Retorna A, yb, I, Wb, Wt (m)."""
    A = S = 0.0; y0 = 0.0; L = []
    for b1, b2, h in partes:
        a = (b1 + b2) / 2 * h; yc = y0 + h * (b1 + 2 * b2) / (3 * (b1 + b2))
        i0 = h**3 * (b1**2 + 4 * b1 * b2 + b2**2) / (36 * (b1 + b2))
        L.append((a, yc, i0)); A += a; S += a * yc; y0 += h
    yb = S / A; I = sum(i0 + a * (yc - yb)**2 for a, yc, i0 in L)
    return dict(A=A, yb=yb, h=y0, I=I, Wb=I / yb, Wt=I / (y0 - yb))

def prever(sec, Ap, yp, sig_pe, fc, fct, bf, vao, a_cort, eps_ps=0.01, beta1=0.65, Ep=196e6, L_isol=None, sig_ps=None):
    """Ap m²; yp = altura do CG das cordoalhas (m, da base); sig_pe tensão efetiva (kPa); fc, fct (kPa, valores reais/MOR);
    bf largura da mesa comprimida; a_cort = distância apoio–carga (m). eps_ps: deformação total assumida na ruptura;
    sig_ps: tensão na ruptura (None → fórmula de potência PCI para gr. 270). L_isol: trecho isolado (m) p/ flecha.
    beta1 = 0,65 é do ACI para f'c alto; pela NBR usar λ = 0,8 − (fck−50)/400 (conferir 17.2.2)."""
    Pe = sig_pe * Ap; e = sec['yb'] - yp; dp = sec['h'] - yp
    Mcr = (fct + Pe / sec['A'] + Pe * e / sec['Wb']) * sec['Wb']        # momento externo de fissuração (sem peso próprio)
    if sig_ps is None:
        sig_ps = min((268 - 0.075 / (eps_ps - 0.0065)) * 6894.76, 1862e3)  # PCI, ksi → kPa
    T = Ap * sig_ps; a = T / (0.85 * fc * bf); c = a / beta1; Mn = T * (dp - a / 2)
    r = dict(Pe=Pe, e=e, dp=dp, Mcr=Mcr, Pcr=2 * Mcr / a_cort, sig_ps=sig_ps, a=a, c=c, Mn=Mn, Pu=2 * Mn / a_cort)
    if L_isol:  # 2 corpos rígidos + rótula no meio do vão (fissura única); superestima se a ruptura for por esmagamento
        dL = (eps_ps - sig_pe / Ep) * L_isol; th = dL / (dp - c); r.update(dL=dL, theta=th, flecha=vao / 2 * th)
    return r

if __name__ == '__main__':
    p = 0.0254
    s = secao([(6*p, 6*p, 4*p), (6*p, 2.5*p, p), (2.5*p, 2.5*p, 7*p), (2.5*p, 6*p, p), (6*p, 6*p, 5*p)])
    r = prever(s, 4*0.1519*p*p, 5*p, 170.9*6894.76, 9.2*6894.76, 0.965*6894.76, 6*p, 17*12*p, 7*12*p,
               Ep=28400*6894.76, L_isol=127.26*p)
    print("Pcr=%.1f kN (117,9)  Pu=%.1f kN (180,9)  flecha=%.0f mm (162)" % (r['Pcr'], r['Pu'], r['flecha']*1000))
```
Destino no software ND: módulo `protendido` (previsão de ensaio / verificação rápida) — ver Parte D da skill principal.

## 9. Roteiro — viga pré-moldada protendida de fábrica
1. Lançamento: vão, apoios (consolo/dente/neoprene), cargas concentradas → posição dos enrijecedores.
2. Seção (I prismática de preferência) e pista disponível; propriedades num único lugar (função `secao`).
3. Fases: pista (σpi ≤ 0,77 fptk e 0,85 fpyk RB), liberação (fckj, γp = 1,1), içamento/estocagem/transporte (apoios cotados), montagem, serviço, ELU.
4. Nº de cordoalhas pelo ELS do nível de protensão; perdas (skill principal, seções 6–7).
5. Ato da protensão ao longo do vão → isolamento nas extremidades (prática usual) ou passiva superior; lbpt/lbd nas pontas.
6. ELU flexão (aderente: compatibilidade; não aderente: NBR 17.2.2) e cisalhamento; regiões D nos apoios e cargas.
7. Detalhamento: estribos, enrijecedores, confinamento da mesa se necessário, insertos de içamento e ligação.
8. Prancha de produção (seção 7.2) + ficha de insertos + memória com tabela de verificações.
9. Para ensaio/protótipo: prever Pcr, Pu e flecha com valores reais (MOR, f'c, σps entre norma e fpy) e declarar a incerteza da flecha.

## 10. Armadilhas
- Superestimar a flecha última com o mecanismo de cordoalha não aderente: a mesa comprimida esmaga antes.
- Achar que isolar o trecho central aumenta a ductilidade da peça — aumenta a abertura da fissura única, não a capacidade de rotação do concreto.
- Bonded length curto nas pontas sem verificar lbd (usar cunha de segurança em protótipo; em peça de obra, redimensionar).
- Comprimento de bainha executado diferente do projeto — conferir antes da concretagem.
- Detalhe de armadura no limite da norma que a armação não consegue montar (simplificar a gaiola).
- Dobrar tela/CA-60 a quente.
- Memória e prancha com dados divergentes (malha, bitola, área da seção).
- Esquecer apoios de içamento/estocagem/transporte na prancha e na verificação (momento negativo no balanço).

## 11. Vigas L de borda (spandrel) — comportamento, cálculo e detalhamento

### 11.1 Fonte, data e o que já foi superado
- Raths, C. H. *Spandrel Beam Behavior and Design*. PCI Journal 29(2), mar–abr 1984, p. 62–131 (Raths, Raths & Johnson — escritório de perícia de falhas; experiência de projeto, obra, perícia e reforço). Lido integralmente em 07/10/2026 (70 p., texto por pdf.js; acervo do Prof. Paulo Bastos, UNESP-Bauru). Base: ACI 318-77, PCI Design Handbook 2ª ed. (1978), PCI Connections Manual (1973); φ = 0,85 cisalhamento / 0,90 flexão / 0,65 concreto simples; unidades americanas → SI aqui.
- **É de 1984. Prevalece sobre Raths** (conferir equações vigentes antes do cálculo final):
  - Lucier, Rizkalla, Zia & Klein (2011, relatório PCI em 2 partes, *slender spandrel beams*): vigas L **esbeltas** rompem por **flexão oblíqua (skew bending) num plano a ~45° junto aos apoios**, não por torção em espiral; com essa verificação, a alma pode ter armadura **aberta** (barras em L + tela), sem estribo fechado nem armadura longitudinal de torção. Raths (e o ACI) mandam estribo fechado — continua correto para vigas L **compactas** e é o lado seguro.
  - Nafadi et al. (PCI Journal mar–abr 2018, 3 artigos): ensaios de abas de vigas L de vão curto e longo e **novas diretrizes de projeto da aba** (punção, suspensão, interação com a excentricidade); mostraram limitações das equações de punção do PCI DH, que descendem das de Raths.
  - Hassan et al. (PCI Journal mar–abr 2019): vigas L compactas com armadura de alma alternativa.
  - φ atuais (ACI 318-19): 0,75 cisalhamento/torção. PCI DH 8ª ed. (2017) traz o projeto atual da aba.
- **Uso na ND**: Raths = conceito, caminhos de carga, patologias, checklist de ligações e pré-dimensionamento (fórmulas validadas na 11.7). Cálculo final: NBR 6118:2023 (torção 17.5 — aqui é **torção de equilíbrio, obrigatória**; cisalhamento 17.4; armadura de suspensão para carga indireta — conferir item), NBR 9062:2017 (consolos, dentes, apoios, ligações) e PCI DH 8ª ed./Nafadi 2018 para a aba.

### 11.2 Patologias observadas (o que o projeto tem de evitar)
1. **Falta de equilíbrio global à torção** (maioria dos casos): cargas das nervuras da TT na aba não alinhadas com a reação no pilar e sem ligação que forme o binário → giro da viga, esmagamento da capa, apoio com tensão concentrada, ruptura de consolo do pilar. Almofada de elastômero agrava (deforma e deixa girar).
2. **Fissura a 45° na extremidade** (dentro de d): flexão da alma pela força H da ligação superior de equilíbrio + torção interna + nervura próxima do apoio.
3. **Aba na extremidade funcionando como consolo invertido** sem armadura para a reação inteira → ruptura.
4. **Insert de tração** do binário arrancado (cone de concreto).
5. **Dente (dap) na extremidade da aba** sem armadura → ruptura como concreto simples; armadura de dente/suspensão insuficiente.
6. **Aba destacada da alma** em vigas de alma fina: a carga entra na aba como num "dente de cabeça para baixo" (flexão + tração direta na alma).

### 11.3 Cargas e equilíbrio
- Gravidade: cargas concentradas das nervuras com excentricidade e_t ao centro de cisalhamento → cortante + torção distribuída. Se a reação no apoio estiver alinhada com as cargas (e_s ≥ e_t), não precisa de ligação de equilíbrio.
- **Não reduzir cortante e torção a d (ou d/2) da face**: o binário H da extremidade equilibra **todas** as cargas excêntricas do vão, não só as além de d; a ACI 318-77 permitia e Raths mostra que isso subdimensiona em ~1/3 a região da ponta. (Na NBR, a redução de 17.4.1.2.1 vale para carga direta próxima ao apoio — carga pendurada na aba é indireta.)
- Binário de extremidade: H = ΣP·e_t / z (z = braço entre a ligação superior e a inferior). Torque de projeto em qualquer seção: T = Pu·e_p − Hu·e_H − Nu·e_N (combinar os casos que não atuam juntos).
- Impacto de veículo em estacionamento (barreira): resistido em balanço (diafragma + aba como viga horizontal) ou pela viga entre apoios com equilíbrio garantido.
- Variação volumétrica (retração, fluência, temperatura): força N axial nas ligações rígidas (soldadas/atrito alto) — reduz a resistência ao cisalhamento/torção; com almofadas é pequena. Gradiente térmico pouco importa em spandrel (mesa estreita); importa em TT com ligação rígida (mesa ~17 °C mais quente que a alma, clima frio dos EUA — adaptar ao Brasil).
- **Equilíbrio do pilar**: se o pilar não for ligado diretamente ao diafragma, as ligações de equilíbrio da viga recebem também a reação horizontal do pilar → aumento grande da força de projeto. Modelar pórtico com dimensões reais (base com 20–50 % de engastamento via pilar fictício; viga com largura de alma × min(8·bw, altura) para flexão no plano vertical) e simular a variação volumétrica com barras fictícias encurtadas.
- Centro de cisalhamento: para carga só vertical, admitir **no eixo da alma** (conservador; no exemplo, 5,06" contra 5,0" do eixo).
- Eixos principais de inércia: considerar em vigas L **baixas** (sobretudo protendidas) quando as ligações não impedem o giro: tg 2θ = 2Ixy/(Iy − Ix); I = (Ix+Iy)/2 ± √[((Ix−Iy)/2)² + Ixy²]. Cordoalhas fora do eixo principal causam desvio lateral (sweep). Em vigas altas, desprezar.
- Barras longitudinais usadas para torção/equilíbrio não contam na flexão.

### 11.4 Verificações (Raths; √fc em MPa: 1·√f'c[psi] = 0,083·√fc[MPa]; φ do artigo)
| Verificação | Expressão (SI) | Limites / distribuição |
|---|---|---|
| Binário de extremidade | Hu = ΣPu·e_t / z | todas as cargas excêntricas do meio vão |
| Armadura a 45° na ponta, lado da aba (Eq.1–3) | Aw = Hu·e_m/(0,85·d_w·fy); Awv = Awl = Aw/√2 (usar o menor dos dois existentes) | espaçamento ≤ 305 mm; ganchos/estribos fechados; **somar** à armadura de cisalhamento (mesmo plano de fissura) |
| Ligação aba–alma sem armadura (Eq.4) | ft = Vu/(bw·m) + 6Vu(bw/2 + 0,75 l_p)/(bw²·m) ≤ 3λ√f'c ≈ 0,25λ√fc | carga a 3/4 l_p da alma (tolerâncias); m = s (interna), d_e + s/2 (extremidade); λ = 1,0 normal / 0,85 leve |
| Armadura aba–alma (Eq.5) | A_l = Vu(bw + 0,75 l_p − 12,7)/[0,85 fy (bw − d_l − 12,7)] em m | espaç. ≤ 457 mm; não soma com cisalhamento/torção (outro plano) — vale o maior |
| Punção da aba, interna, d_e ≥ 2h (Eq.6/7) | s > bt+2h: φVn = 0,85·3λ√f'c·h(2l_p + bt + h); s ≤ bt+2h: 0,85·λ√f'c·h·s | √f'c em psi (×0,083 em MPa) |
| Punção da aba, extremidade d_e < 2h (Eq.8/9) | s > bt+2h: 0,85·λ√f'c·h[2l_p + (bt+h)/2 + d_e]; s ≤ bt+2h: 0,85·λ√f'c·h(d_e + s/2) | carga distribuída: Eq.7 com s = faixa |
| Suspensão (pendural) (Eq.11) | A_sh = Vu/(0,85 fy) | tensão no plano vertical h(bt+h) ≤ 10λ√f'c ≈ 0,83λ√fc; dentro de bt + h (interna) ou d_e + (bt+h)/2 (extremidade — conferir, OCR ilegível); não soma com estribos de cisalhamento, mas os estribos na posição da carga têm de somar A_sh |
| Longitudinal no topo da aba | A_h ≥ A_sh/2; grampo (hairpin) confinando a ponta da aba | distribui a carga concentrada |
| Flexão da aba (Eq.12) | A_s = [Vu·(0,75 l_p)/d + Nu·h/d]/(0,85 fy), Nu = 0,15 Vu no exemplo | em bt + h centrado na carga; espaç. ≤ h e ≤ 457 mm; mínimo Ø10 no espaçamento máximo; a barra dobrada **não** confina o apoio (ver 11.6) |
| Flexão da alma sem ligação superior (Eq.13–16) | w_tu = T_½vão/[(L/2)h_h]; Hu = w_tu·L/2; f_b = 6w_tu·e_t/bw² ≤ 3λ√f'c; senão A_s = w_tu·e_t/(0,85 d fy) por metro | parte inferior da alma (altura h_w) leva Hu à ponta como viga horizontal; soma com Eq.5/11 (mesmo plano); espaç. ≤ 457 mm e ≤ 3h |
| Aba como consolo na extremidade (Eq.17–22), reação alinhada | As1 = máx[0,75 Vu l_p/(0,85 fy d1); Vu²/(0,85 fy·2λ·6,9·b1 d1); 0,08·6,9·b1 d1/fy]; A_vh = máx[Vu²/(0,85 fy·4λ·6,9·b1 d1); 0,04·6,9·b1 d1/fy]; As2 = (d1/d2)As1 (alma, lado oposto) | b1 = 1,5h; τ = Vu/(b1 d1) ≤ 5,5 MPa (800 psi); As1 e As2 dentro de 1,5h; A_vh da ponta até 2h além do apoio, espaç. ≤ h/2; além de 1,5h a alma resiste à torção total da reação excêntrica (6,9 = 1 ksi em MPa, constante embutida nas fórmulas) |

### 11.5 Exemplos do artigo em SI (todos reproduzidos na 11.7)
- **Ex. 1 — spandrel de garagem** (alma 254 mm, aba l_p = 152 × h = 356 mm, TT com nervuras a 1,52 m, bt = 121 mm, d_e = 502 mm, fc = 34,5 MPa, fy = 414 MPa): P = 112,5 kN serviço por nervura (D 68,5 + L 44,0) → fator combinado 1,52; Vu na aba = 4/3 · 1,52 · 112,5 = **228 kN** (fator de ligação 4/3). Binário: e_t = 241 mm, z = 1,57 m → Hu = 78,5 kN → Aw = 839 mm² → Awv = Awl = 594 mm² + estribos de torção/cisalhamento → **Ø12,5 c/ 10 cm nos 1,5 m da ponta, longitudinal Ø12,5 c/ 30 cm**. Aba–alma: ft = 4,76 MPa ≫ 1,46 MPa → A_l = 1135 mm² em 1,26 m → **Ø12,5 c/ 15 cm na ponta (1,37 m) e c/ 17,5 cm no restante**. Punção interna 345 kN > 228 → ok sem A_sh; na extremidade 154 kN < 228 → A_sh = 652 mm², já há 400 mm² dos estribos → **+2 estribos Ø12,5 em cada nervura de ponta**. Flexão da aba 342 mm² por nervura → Ø12,5 c/ 30 cm + 2 barras extras em cada nervura. Lição: na ponta, punção, aba–alma e equilíbrio somam — a ponta é a região crítica.
- **Ex. 2 — aba como consolo** (pilar sob a aba, reação alinhada com 3 nervuras): Vu = 684 kN; τ = 4,04 MPa ≤ 5,5 ✓; As1 = 703 mm² → **4 Ø16 com barra transversal soldada**; A_vh = 284 mm² → Ø12,5 c/ ≤ 17,5 cm; As2 = 1032 mm² em 533 mm (somando aos estribos). Faltava checar apoio não uniforme da almofada e tensão na borda da aba (pode exigir chapa + barras ancoradas).
- **Ex. 3 — eixos principais** (spandrel de edifício): Ixy = −6394 in⁴, θ = 8,71°, Imáx = 55 003 in⁴ (+1,8 %), mas W_inf,mín = 3188 in³ contra 3450 do eixo x (**−7,6 %**) → tensão de serviço maior que a calculada no eixo geométrico; protensão: momento = força × distância CG–cordoalhas paralela ao eixo principal.

### 11.6 Ligações e boas práticas (checklist ND / consultoria de fábrica)
- **Equilíbrio à torção na montagem e na fase final**: ligação de topo (chapa soldada na capa/mureta, barra rosqueada, insert) + apoio inferior; ou aba como consolo com reação alinhada (corte no pilar/dente na ponta — limita o pilar a ~457 mm na face). Nunca contar com o cisalhamento da almofada para o binário.
- **Evitar insert de tração para o binário** (tolerâncias): pilar ±10–13 mm, furo na viga ±10–13 mm, desvio angular ±6 mm, comprimento da viga ±13 mm, locação do pilar ±13–25 mm → para barra de 25 mm, furo de 63 mm (só insert) a 83 mm (insert + furo). Escolher detalhes **insensíveis a tolerância** (chapa solta soldada em cantoneira, não chapa com chapa "perfeitamente alinhada").
- **Limitar força de variação volumétrica por escoamento controlado**: chapa de ligação TT–viga 6,3 × 51 × 102 mm (A36 → ~80 kN), soldada **só nas pontas**; ou cantoneira soldada só nas abas. Furos na chapa se precisar reduzir a força. A tração dessa chapa gera torção adicional na viga.
- Peças embutidas que recebem chapa solta/barra rosqueada: capacidade ≥ 4/3 da peça solta.
- **Fatores de carga** (Raths, base ACI 1977): ligações ≥ 2,0 (= 4/3 × 1,5); se depende de cone de concreto, 3,0 (2,5 justificado); variação volumétrica com o fator da sobrecarga; Nu mínimo em toda ligação (0,15 Vu no exemplo — no PDF o valor está ilegível). **Hoje**: NBR 9062 (γn adicional em ligações e Hd mínimo: 0,16Vd com elastômero, 0,5Vd com argamassa, 0,8Vd sem nivelamento — conferir item) e ancoragens por ACI 318-19 cap. 17 / skill `ancoragem-barras-pos-instaladas`.
- **Apoios**: preferir concreto simples + almofada; tensão média em serviço 5,5–6,9 MPa; evitar chapa de apoio; sempre alguma armadura para N; almofada com fibras sintéticas e borracha 10–13 mm; neoprene só grau estrutural quando controlar variação volumétrica for crítico. **Nunca apoio compartilhado** (almofada metade sobre aço, metade sobre concreto) — chapa da viga maior que a do consolo. Prever giro de contraflecha da TT longa e chapas tortas (3–5 mm entre cantos).
- Barra dobrada da aba só serve à flexão; para apoio armado, barras ancoradas com barra transversal soldada ou chapa + barras (fig. 38–39 do artigo).
- **Detalhamento 3D obrigatório**: dobras com raio (não 90° vivo); diâmetro real ≈ nominal + 3 mm (nervuras); folga de 19 mm entre armaduras de planos diferentes; tolerância de posição de barras críticas ±6 mm; estribos ±13 mm + 13 mm fora de esquadro; barras de ligação Ø10–Ø16; âncoras de chapa com 19 mm de folga (tolerância de chapa ±13 mm de cada lado → até 25 mm somados); a grade de cordoalhas de 50 mm não fica toda disponível. Não soldar perto de dobra a frio, nunca ponto de solda; soldagem de barra com procedimento (composição química, eletrodo baixo hidrogênio, pré-aquecimento).
- **Seção mínima**: alma ≥ 254 mm (nunca < 203); projeção da aba ≥ 152 mm; altura da aba ≥ 254 mm (≥ 356 para reações grandes); largura da mesa comprimida ≥ L/50. Armação e encaixe de insertos podem governar a seção.
- **Folgas**: ≥ 25 mm entre a viga e as outras peças; 38 mm para vigas ≥ 1,22 m de altura, vão grande ou que apoiam peças ≥ 18 m. Projetar com a tolerância que gera a maior força.
- **Corrosão**: cobrimento com tolerância (artigo: 32 mm; 57 mm com cloretos e a/c ≤ 0,40 — no Brasil usar NBR 6118 tab. 7.2 por CAA); chapas expostas em estacionamento no mínimo galvanizadas (inox em ambiente agressivo); soldar antes de aplicar a proteção; especificar o revestimento, não só "anticorrosivo".
- **Pórtico com spandrel** (raro): soldar só as ligações necessárias, após a carga permanente, em sequência que minimize retração de solda; chapa vertical com coluna de graute (chave de cisalhamento) melhor que chapa plana; inspeção e ensaio das soldas embutidas e de campo — sem inspeção, não usar.
- **Pilar**: no último nível, a viga **não** apoia no topo do pilar — o pilar sobe até o topo da viga e a viga apoia em consolo (reação horizontal do pilar + equilíbrio da viga). Projetar o pilar para as forças do binário.
- **Inspeção**: projetista confere posição da armadura de ligação na fábrica; "um projetista responsável" pela compatibilização viga–ligação–pórtico; diagrama de corpo livre completo de cada ligação.

### 11.7 Código validado — `spandrel_nd.py` (rodado em 07/10/2026, 18/18 PASS contra os exemplos do artigo)
| Teste | Resultado | Referência (Raths 1984) |
|---|---|---|
| Hu binário / Aw Eq.1 / Awv Eq.2 | 17,65 kip / 1,295 in² / 0,916 in² | 17,7 / 1,30 / 0,92 |
| Vu aba / ft Eq.4 / 3√f'c | 51,28 kip / 690,5 psi / 212,0 psi | 51,3 / 691 / 212 |
| A_l Eq.5 | 1,759 in² | 1,76 |
| φVn punção interna Eq.6 / extremidade Eq.8 | 77,59 / 34,59 kip | 77,6 / 34,6 |
| A_sh Eq.11 / A_s aba Eq.12 | 1,005 / 0,531 in² | 1,01 / 0,53 |
| Consolo: As1 / A_vh / As2 / τ | 1,086 / 0,442 / 1,597 in² / 586 psi | 1,09 / 0,44 / 1,60 / 586 |
| Eixos principais θ / Imáx / Imín | 8,713° / 55 004 / 12 303 in⁴ | 8,71 / 55 003 / 12 304 |

```python
"""spandrel_nd.py — viga L (spandrel) pré-moldada: equações de Raths (PCI J. 1984), em SI.
Unidades: N, mm, MPa. raiz(fc) em MPa: 1·√f'c[psi] = 0,083·√fc[MPa]. phi conforme o artigo (ACI 318-77);
para projeto NBR trocar phi por 1/γ e conferir (ver 11.1)."""
import math
K = 0.083  # √psi -> √MPa
def rt(fc, lam=1.0): return lam * K * math.sqrt(fc)

def H_equilibrio(Pu_total, e, z):            # binário de equilíbrio à torção na extremidade
    return Pu_total * e / z
def A_w(Hu, em, dw, fy, phi_j=0.85):          # Eq.1 armadura a 45° na alma (lado da aba)
    return Hu * em / (phi_j * dw * fy)
def A_w_comp(Aw): return Aw / math.sqrt(2)    # Eq.2/3 componente vertical = horizontal
def ft_aba_alma(Vu, bw, lp, m):               # Eq.4 tração na ligação aba–alma sem armadura
    return Vu / (bw * m) + 6 * Vu * (bw / 2 + 0.75 * lp) / (bw**2 * m)
def A_l(Vu, bw, lp, dl, fy, phi=0.85, a2=12.7):  # Eq.5 armadura aba–alma (em m)
    return Vu * (bw + 0.75 * lp - a2) / (phi * fy * (bw - dl - a2))
def Vn_puncao(h, lp, bt, fc, s, de, lam=1.0, phi=0.85):  # Eq.6–9
    r = rt(fc, lam)
    if de >= 2 * h:
        return phi * 3 * r * h * (2 * lp + bt + h) if s > bt + 2 * h else phi * r * h * s
    return phi * r * h * (2 * lp + (bt + h) / 2 + de) if s > bt + 2 * h else phi * r * h * (de + s / 2)
def A_sh(Vu, fy, phi=0.85): return Vu / (phi * fy)            # Eq.11 suspensão (pendural)
def A_s_aba(Vu, Nu, lp, h, d, fy, phi=0.85):                  # Eq.12 flexão da aba
    return (Vu * 0.75 * lp / d + Nu * h / d) / (phi * fy)
def w_tu(T_meio, L, hh): return T_meio / (L / 2 * hh)          # Eq.13 (N/mm)
def fb_alma(wtu, et, bw): return 6 * wtu * et / bw**2          # Eq.15 (por mm)
def A_s_alma(wtu, et, d, fy, phi=0.85): return wtu * et / (phi * d * fy)  # Eq.16 (mm²/mm)
C1 = 6.895  # 1 ksi em MPa — constante embutida nas Eq.18–21
def consolo_extremo(Vu, lp, d1, d2, b1, fy, lam=1.0, phi=0.85):  # Eq.17–22
    As1 = max(0.75 * Vu * lp / (phi * fy * d1), Vu**2 / (phi * fy * 2 * lam * C1 * b1 * d1), 0.08 * C1 * b1 * d1 / fy)
    Avh = max(Vu**2 / (phi * fy * 4 * lam * C1 * b1 * d1), 0.04 * C1 * b1 * d1 / fy)
    return dict(As1=As1, Avh=Avh, As2=d1 / d2 * As1, tau=Vu / (b1 * d1))
def eixos_principais(Ix, Iy, Ixy):            # Eq.23–25
    th = 0.5 * math.degrees(math.atan(2 * Ixy / (Iy - Ix)))
    m, r = (Ix + Iy) / 2, math.hypot((Ix - Iy) / 2, Ixy)
    return th, m + r, m - r

if __name__ == '__main__':
    i, k, ksi, psi = 25.4, 4448.22, 6.89476, 0.00689476
    fc, fy = 5000 * psi, 60 * ksi; T = []
    def chk(n, v, ref, tol=0.02): T.append((n, v, ref, abs(v / ref - 1) <= tol))
    Hu = H_equilibrio(1.52 * 75.8 * k, 9.5 * i, 62 * i); chk('Hu (kip)', Hu / k, 17.7)
    Aw = A_w(Hu, 31.8 * i, 8.5 * i, fy); chk('Aw Eq1 (in2)', Aw / i**2, 1.30)
    chk('Awv Eq2 (in2)', A_w_comp(Aw) / i**2, 0.92)
    Vu = 4 / 3 * 1.52 * 25.3 * k; chk('Vu aba (kip)', Vu / k, 51.3)
    chk('ft Eq4 (psi)', ft_aba_alma(Vu, 10 * i, 6 * i, 49.75 * i) / psi, 691)
    chk('3√fc (psi)', 3 * rt(fc) / psi, 212, 0.01)
    chk('Al Eq5 (in2)', A_l(Vu, 10 * i, 6 * i, 1.5 * i, fy) / i**2, 1.76)
    chk('Vn interno Eq6 (kip)', Vn_puncao(14 * i, 6 * i, 4.75 * i, fc, 60 * i, 30 * i) / k, 77.6)
    chk('Vn extremo Eq8 (kip)', Vn_puncao(14 * i, 6 * i, 4.75 * i, fc, 60 * i, 19.75 * i) / k, 34.6)
    chk('Ash Eq11 (in2)', A_sh(Vu, fy) / i**2, 1.01)
    chk('As aba Eq12 (in2)', A_s_aba(Vu, 0.15 * Vu, 6 * i, 14 * i, 12.5 * i, fy) / i**2, 0.53)
    c = consolo_extremo(4 / 3 * 1.52 * 3 * 25.3 * k, 6 * i, 12.5 * i, 8.5 * i, 21 * i, fy)
    chk('As1 Eq17 (in2)', c['As1'] / i**2, 1.09); chk('Avh Eq20 (in2)', c['Avh'] / i**2, 0.44)
    chk('As2 Eq22 (in2)', c['As2'] / i**2, 1.60); chk('tau consolo (psi)', c['tau'] / psi, 586)
    th, Imax, Imin = eixos_principais(54024, 13283, -6394)
    chk('theta (graus)', th, 8.71); chk('Imax (in4)', Imax, 55003); chk('Imin (in4)', Imin, 12304)
    for n, v, r, ok in T: print(f"{'PASS' if ok else 'FAIL'}  {n:22s} {v:10.3f}  ref {r}")
    print(sum(t[3] for t in T), '/', len(T), 'PASS')
```
Destino no software ND: módulo `premoldados` (vigas L) — ligar à ferramenta ND de consolos/dentes Gerber para a ponta da aba e ao `premoldados_nd.py` (skill `projeto-estruturas-pre-moldadas`, seção 13).

### 11.8 Roteiro — viga L de borda
1. Arranjo pilar–viga–laje: a reação alinha com as cargas da aba (aba sobre consolo/dente) ou precisa de binário? Definir o sistema de equilíbrio **na montagem e no final**.
2. Seção: alma, aba (l_p, h), centro de cisalhamento no eixo da alma; em viga baixa/protendida, eixos principais.
3. Cargas por nervura (D, L), impacto de veículo, variação volumétrica (N), equilíbrio do pilar; combinações e fatores (NBR 8681 + γn de ligação da NBR 9062).
4. Ponta: binário H com **todas** as cargas → armadura a 45° (Aw) somada ao cisalhamento/torção; ou consolo de extremidade (As1, A_vh, As2, τ ≤ 5,5 MPa).
5. Torção interna + cortante pela NBR 6118 (torção de equilíbrio) — estribos fechados; para viga esbelta com armadura aberta, só com a verificação de flexão oblíqua (Lucier 2011 / PCI DH 8ª ed.).
6. Aba: ligação aba–alma (ft ou A_l), punção interna/extremidade, suspensão A_sh, A_h ≥ A_sh/2, flexão da aba, apoio (armado ou não). Conferir com Nafadi 2018 / PCI DH 8ª ed.
7. Sem ligação superior: flexão da alma e viga horizontal inferior (Eq.13–16).
8. Ligações: diagrama de corpo livre, tolerâncias e folgas, escoamento controlado, peças embutidas ≥ 4/3, cone de concreto com fator 3, galvanização.
9. Detalhe 3D das armaduras da ponta (aba, dente, estribos, cordoalhas, insertos) antes de fechar a seção; prancha de produção (seção 7.2) com tolerâncias de posição das barras críticas.

### 11.9 Armadilhas (vigas L)
- Reduzir cortante/torção a d da face na viga L com carga na aba.
- Contar com a almofada de elastômero (cisalhamento) para o equilíbrio à torção; esquecer a fase de montagem (antes da capa).
- Aba na ponta sem armadura de consolo quando a reação está sob a aba.
- Insert de tração no binário sem considerar o acúmulo de tolerâncias e o cone (fator 3).
- Projetar ligação sem a reação horizontal do pilar (pilar não ligado ao diafragma).
- Chapa soldada "rígida" atraindo força de retração/temperatura sem limite de escoamento.
- Apoio compartilhado aço/concreto; chapas de apoio desalinhadas; giro de contraflecha da TT ignorado.
- Armadura "típica" que não cabe: raios de dobra, diâmetro real, cordoalhas, insertos — detalhe 3D na fase de projeto.
- Usar as fórmulas de 1984 como definitivas: φ e equações da aba foram revistos (11.1).