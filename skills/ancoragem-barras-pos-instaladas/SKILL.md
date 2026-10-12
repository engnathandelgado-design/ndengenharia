---
name: "ancoragem-barras-pos-instaladas"
description: "Dimensionar, revisar ou especificar barras pós-instaladas com adesivo (chumbamento químico) em concreto e em rocha — ancoragem, cone, fendilhamento, EOTA TR 069, execução e ensaios; inclui cabeceiras de protensão em basalto."
---

# Barras pós-instaladas (chumbamento químico) — concreto e rocha

Use quando Nathan for chumbar ferros com adesivo (Hilti HIT-RE 500 V4, HIT-HY 200-R etc.) em concreto existente ou em rocha, ou revisar projeto/memória disso. Caso de origem: **bloco de cabeceira de protensão ancorado no basalto** ([[protensao-bloco-basalto]]).

## 1. Fonte
- Hilti, *Concrete-to-concrete connections using post-installed systems — Handbook ver. 02* (ago/2026, 160 p.), lido na íntegra pelo navegador (pdf.js). Base: EN 1992-1-1 (EC2), EN 1992-4, EN 1998-1, EAD 330087 / 332402 / 332347, EOTA TR 069 (ancoragens com momento), TR 066 (overlays), TR 086 (vida útil 50/100/120 anos). Nível: projeto profissional.
- **O handbook não trata de rocha** (nenhuma menção a rock/stone/basalt). Escopo das ETAs: concreto normal C12/15–C50/60, não carbonatado, barras 400–600 MPa. A seção 6 desta skill (rocha) é conhecimento próprio + normas de tirantes, marcado (conferir).
- No Brasil não há norma de barra pós-instalada: usar NBR 6118:2023 para a parte moldada no local e as ETAs/EC2/TR 069 para a parte chumbada, declarando isso na memória.

## 2. Mecanismo
- Duas interfaces: barra–adesivo e adesivo–substrato (no moldado só há barra–concreto). Desempenho **depende do produto** → sempre ler a ETA (Anexo B: uso/instalação; Anexo C: valores).
- Modos de ruína: escoamento do aço (desejável), arrancamento (pull-out, quando há confinamento ≥ ~3φ), fendilhamento (pouco cobrimento/espaçamento), cone de concreto (sem confinamento ativo — frágil).
- "Teoria de barra" (EC2): admite bielas locais/globais confinando a ancoragem; não verifica cone. "Teoria de chumbador" (TR 069): não admite confinamento; verifica cone + fendilhamento + aço.
- Graute cimentício com marca CE pela EN 1504-6 **não** serve para ligação estrutural (não avaliado em fissurado, carga sustentada, temperatura, limpeza, sismo).

## 3. Parâmetros e limites (handbook, tab. 3.2 / 4.1)
| Item | EAD 330087 (EC2) | EAD 332402 (TR 069) |
|---|---|---|
| Cobrimento mínimo | 2φ | 2φ |
| Confinamento | admitido | não admitido |
| lb mín. | lb,min EC2 (≈10φ / 15φ em emenda) | idem |
| lb máx. | ≈60φ | ≈60φ |
| Vida útil | 50/100/120 anos | 50/100 anos |

Produtos Hilti (tab. 4.1): RE 500 V4 — φ8–40, prof. máx. 3200 mm, −5/+40 °C, trabalho 30 min e cura 7 h a 20 °C, aceita HD/HDB/DD/DD+RT/CA, furo com água, TR 069, 120 anos; HY 200-R — φ8–40, máx. 1300 mm, cura 60 min, sem diamante liso (DD só com rugosificação); FP 700-R inorgânico (incêndio), cura 10 dias.

## 4. Fórmulas
**EC2 + ETA (ancoragem sem momento, compressão, ou com modelo de bielas):**
- lb,rqd = (φ/4)·σsd/fbd,PIR (fbd,PIR da ETA, em vez de 2,25·η1·η2·fctd).
- lbd = α2·α3·α5·lb,rqd ≥ lb,min; α1 = α4 = 1 (barra reta, sem transversal soldada); α2 = 1 − 0,15(cd − φ)/φ ∈ [0,7; 1]; α5 = 1 − 0,04p; α2·α3·α5 ≥ 0,7.
- lb,min = αlb·max(0,3·lb,rqd; 10φ; 100 mm) tração; 0,6·lb,rqd em compressão. αlb (1,0–1,5) da ETA.
- Apoio simples: força a ancorar FE = |VEd|·al/z + NEd (al = d em laje sem estribo); engastamento parcial ≥ 15% do momento do vão (barras superiores — fora da zona comprimida → verificar cone).

**Bielas e tirantes Hilti (ligação rígida, 6.3.1):** θ = min{60°; atan[(hex − max(30; 2φ) − cs − lbd/2)/z1R]}, exigindo 30° ≤ θ ≤ 60°; z1R = 0,85z para momento de abertura; linst = z1R·tanθ + lbd/2 (+cs) ≤ hex − max(2φ; 30); biela: σ = F5/(lbd·w·cosθ) ≤ 0,85·(1 − fck/250)·fcd. θ menor encurta a barra mas aumenta muito o cortante no elemento existente.

**EOTA TR 069 (ligação com momento, sem bielas):** Rd = min(NRd,y; NRd,c; NRd,sp); γMs = 1,15; γMc = γinst·1,5; γMsp = γMp = γMc.
- Cone: N0Rk,c = k1·√fck·lb^1,5 (k1 = 7,7 fissurado / 11 não fissurado), A0c,N = 9lb², scr = 3lb; ψs,N = 0,7 + 0,3c/ccr,N ≤ 1; ψec,N = 1/(1 + 2eN/scr,N); ψre,N = 0,5 + lb/200 ≤ 1 (=1 se armadura existente com s ≥ 150 mm, ou φ ≤ 10 com s ≥ 100, ou se lb ≥ lb,min); ψM,N = 2 − z/(1,5lb) ≥ 1 (compressão do momento ajuda; exige CEd ≥ 0,8NEd e c ≥ 1,5lb).
- Fendilhamento (fib MC2020): τRk,sp = η1·Ak·(fck/25)^sp1·(25/φ)^sp2·[(cd/φ)^sp3·(cmax/cd)^sp4 + km·Ktr]·(7φ/lb)^lb1 ≤ τRk,max,ucr·Ωcr·ψsus (7φ ≤ lb ≤ 20φ) — e com fator (20φ/lb)^lb1 acima de 20φ. φ < 12 → usar 12 no termo (25/φ). cd = min(cs/2; cx; cy) ≥ 2φ; 1 ≤ cmax/cd ≤ 3,5. km = 12 / 6 / 0 (estribo envolvendo / afastado / não cruza); Ktr = nt·Ast/(nb·φ·st) ≤ 0,05. NRk,sp = τRk,sp·lb·φ·π por barra.
- Carga sustentada: ψsus = 1 se αsus ≤ ψ0sus; senão ψ0sus + 1 − αsus (αsus = parcela permanente/total no ELU; ψ0sus da ETA). **Protensão é carga permanente → αsus ≈ 1 → ψsus = ψ0sus.**
- Pressão transversal ρtr (média num cilindro de 3φ, tração +): Ωp,tr = 1 − 0,3·ρtr/fctm para 0 ≤ ρtr ≤ fctm (tração reduz); Ωp,tr = 1 − tanh[0,2·ρtr/(0,1·fcm)] para −fcm ≤ ρtr ≤ 0 (compressão aumenta) — TR 069 eq. 4.13 (conferir: texto do PDF veio parcialmente ilegível).
- Sismo: τ·αeq,sp; cone ×αeq (1,0 se w = 0,3 mm; 0,85 se > 0,3); dimensionar para escoamento (γRd 1,0 DCM / 1,2 DCH); w de projeto pela tab. 6.3 (DCL 0,3; DCM q ≤ 1,5 e lb/h ≥ 0,8 → 0,3; etc.).
- Hilti method: EC2 com τRk,sp (EAD 332402) no lugar de fbd: lb,rqd = (φ/4)·σsd·γMp/τRk,sp ≥ lb,min, sem fatores α.
- Transferência local para a armadura existente: lb/h ≥ 0,8 (TR 069 §8 / EC2-4 Anexo A); cisalhamento na interface e capacidade do elemento existente verificados à parte.
- Fadiga: aço Δσ conforme EC2 6.8.4 (ΔσRsk = 162,5 MPa a 10⁶, k1 = 5, k2 = 9, γs,fat = 1,15); aderência/cone sem regra europeia — recomendação Hilti: fator 0,5 (cone) e 0,4 (fendilhamento) para 10⁶ ciclos (EAD 330250); ou kfat = 0,5 sobre Rd.
- Incêndio: τ e fbd reduzidos por kfi(θ) ao longo da barra (integração por trechos ≤ 2φ); γ = 1,0; só para ancoragem sem momento no EC2; TR 069 tem método próprio.

## 5. Detalhamento e execução (cap. 5.2 e 9)
- Espaçamento livre entre barras pós-instaladas ≥ max(40 mm; 4φ) (2φ com guia de furação). Emenda sem contato: se e > 4φ ou 50 mm, aumentar l0 de (e − 4φ).
- Cobrimento mínimo de furação (EAD 330087): HD/HDB φ < 25: 30 + 0,06lv ≥ 2φ (com guia 30 + 0,02lv); φ ≥ 25 ou DD+RT: 40 + 0,06lv ≥ 2φ (com guia 40 + 0,02lv). cmin = max(cmin,dur; cmin,ETA).
- Superfície da junta: rugosidade ≥ 3 mm pico-vale a cada ~40 mm; remover camada carbonatada em Ø φ + 60 mm em volta da barra.
- Sequência: escanear (ferroscan/radar) → preparar superfície → furar (HD martelete; HDB broca oca com aspirador dispensa limpeza; CA ar comprimido mais rápido, mais dano; DD diamantada lisa → só com adesivo qualificado ou rugosificador TE-YRT) → limpar conforme IFU (sopro + escova + sopro; furo diamantado: lavar até água limpa, soprar, escovar) → injetar do fundo com pistão (piston plug) e mangueira de extensão, volume calculado → inserir girando, conferir refluxo na boca, segurar barras horizontais/ascendentes até a cura → respeitar tempo de trabalho/cura pela temperatura do substrato.
- Sinais de vazio: barra "volta" ao inserir, barulho de ar, adesivo não aflora → refazer.
- Ensaio no local: (a) prova de carga para validar instalação; (b) obter valor de projeto quando o material base está fora da ETA — **não** usar ensaio para tirar τ maior que a ETA dentro do escopo dela.
- Checklist de obra (fig. 9.20): desenho/especificação, posição e nível, escaneamento, furação (Ø, profundidade, método), limpeza, adesivo aprovado e lote, temperatura, volume, embutimento e prumo, cura, ensaio.

## 6. Chumbar em ROCHA (basalto) — fora do handbook, conhecimento próprio (conferir)
Modos a verificar para cada barra e para o grupo:
1. **Aço**: NRd,y = As·fyd (CA-50: 435 MPa). Projetar para que governe.
2. **Barra–adesivo**: usar no máximo o τ da ETA para concreto C50/60 não fissurado (ex.: limite τRk,max,ucr do produto) × ψsus (carga permanente) — o adesivo não fica mais forte por estar em rocha.
3. **Adesivo–rocha**: sem ETA para rocha → valor por **ensaio de arrancamento no local** (barras de sacrifício levadas à ruptura, no mesmo basalto, mesma furação/limpeza). Ordem de grandeza para pré-dimensionar (aderência média última calda–rocha, PTI DC35.1 / FHWA): granito e basalto ≈ 1,7–3,1 MPa (conferir); adesivo epóxi em basalto são e furado com martelete costuma dar bem mais, mas só usar com ensaio. Fator de segurança 2–3 sobre o último, ou γ ≥ 2,0 sobre o característico de ensaio (conferir critério adotado).
4. **Cone/cunha de rocha**: conservador = só peso próprio do cone (ápice 90° em rocha sã; 60° se fraturada), γrocha ≈ 26–28 kN/m³ (submerso se houver água), FS ≥ 1,5–2; cones do grupo se sobrepõem → usar o volume do grupo (prisma/tronco). Com resistência à tração da rocha só com caracterização (RQD, juntas).
5. **Bloco de concreto**: lado moldado no local ancorado pela NBR 6118 (gancho/placa permitidos); verificar bielas e tirantes do bloco, punção da placa/ancoragem dos cabos, deslizamento da interface bloco–rocha (atrito μ ≈ 0,6–1,0 com rocha rugosificada e limpa + pino) e tombamento.

Cuidados específicos do basalto da Formação Serra Geral (PR/SC): diferenciar basalto denso (UCS ≈ 100–250 MPa, conferir) de basalto vesicular/amigdaloide e de zonas de disjunção/fraturas horizontais; caracterizar com sondagem rotativa (RQD) ou ao menos inspeção do maciço exposto. Fraturas abertas consomem adesivo (controlar volume injetado vs. teórico). Furação com martelete (furo rugoso) é melhor que diamantada lisa. Rocha úmida/água no furo → adesivo qualificado para furo com água (RE 500 V4). Rocha quente ao sol / fria → janela de temperatura do adesivo.

**Cabeceira de pista de protensão:** a força de protensão das cordoalhas é aplicada e retirada a cada ciclo de produção (~1 ciclo/dia → poucos milhares de ciclos na vida útil: não é fadiga de alto ciclo, mas é carga repetida e, durante a cura, permanente). Logo: αsus ≈ 1; verificar ELU com γf da protensão (NBR 6118: 1,2 na ação de protensão desfavorável — conferir o valor adotado na cabeceira), checar deslocamento da cabeceira (perda de protensão na pista) e prever ensaio de recebimento de parte das barras com carga ≥ 1,2–1,5 × a de serviço (critério tipo NBR 5629 tirantes — conferir).

## 7. Exemplos do handbook (validados no `pir_nd.py`)
- 6.8.1 laje 250 mm em parede, HY 200-R (fbd = 2,3): φ14 inferior σsd = 144 MPa → lb,rqd = 219, lbd = 153 mm (α2 = 0,7); φ10 superior (engaste 15%) σsd = 250 → lbd = 190 mm; cone fissurado NRd,c = 105,5 kN > 98 kN. Lição: a barra superior não está confinada → verificar cone.
- 6.8.2 parede de reservatório em laje 600 mm (S&T, RE 500): φ12 c/125, σsd = 418 → lbd = 382; θ = 49,6°; furo 571 mm; biela 1,97 < 10,4 MPa. Com θ = 30°: furo 398 mm mas cortante no existente 401 → 747 kN. Com τ do TR 069 (6,48 MPa) e θ = 30°: lb = 194, furo 304 mm.
- 6.8.3 viga 300×300 em parede 350 mm, TR 069, RE 500 V4 (Ak = 4,4; sp1 = 0,29; sp2 = 0,27; sp3 = 0,68; sp4 = 0; lb1 = 0,60; τmax,ucr = 15 MPa em C20 × (fck/20)^0,1 — valores lidos do exemplo, confirmar na ETA-20/0539): estático lb = 168 mm, τ = 10,0 MPa, NRd,c = 133 kN; sísmico lb = 288 mm, τ = 6,9 MPa, NRd,sp = 49,9 kN; R90 governa. O próprio livro imprime "41,7 kN > 42,0 kN" no fendilhamento estático — erro de digitação (o cálculo dá ≈ 42,1 kN).

## 8. Roteiro
1. Definir esforços na interface (N, M, V; parcela permanente αsus) e o tipo: emenda / ancoragem sem momento / com momento / overlay.
2. Escolher método: EC2+ETA (confinado), S&T Hilti, ou TR 069 (não confinado, momento). Em rocha: seção 6.
3. Escolher produto pela ETA (diâmetro, profundidade máx., furação, água, temperatura, vida útil, sismo/incêndio).
4. Calcular lb por modo (aço, aderência/fendilhamento, cone) — de preferência deixar o aço governar (gráfico de "hierarquia de resistência" lb × Rd).
5. Verificar geometria: cobrimentos de furação, espaçamentos, linst ≤ espessura disponível, lb/h ≥ 0,8 para transferência local.
6. Verificar o elemento existente/maciço e a interface (cisalhamento-atrito).
7. Especificar execução (furação, limpeza, injeção com pistão, cura) e ensaios; anexar checklist.

## 9. Armadilhas
- Usar fbd do EC2 ou valores de catálogo sem checar a ETA do produto/furação (diamantada lisa derruba a aderência).
- Esquecer ψsus em carga permanente (protensão!).
- Ancoragem fora da zona comprimida sem verificar cone.
- Aplicar ETA de concreto a rocha/alvenaria sem ensaio.
- Ensaio de arrancamento curto demais (mede só o topo) ou em rocha diferente da de projeto.
- Graute cimentício "estrutural" no lugar de adesivo qualificado.
- Furo sem limpeza, adesivo fora da validade/temperatura, barra sem travamento durante a cura.

## 10. Código validado — gravar como `pir_nd.py` (motor ND)
```python
"""pir_nd.py — barras pós-instaladas (Hilti C2C Handbook v02, ago/2026; EC2-1-1 + EOTA TR 069). Unidades: N, mm, MPa."""
import math
def lb_rqd(phi, sigma_sd, fbd):                      # EC2 eq.8.3 (fbd = fbd,PIR da ETA)
    return phi/4*sigma_sd/fbd
def alpha2(cd, phi):                                  # barra reta, tração
    return max(0.7, min(1.0, 1-0.15*(cd-phi)/phi))
def lbd(phi, sigma_sd, fbd, cd, a3=1.0, a5=1.0, alpha_lb=1.0, tracao=True):
    lr = lb_rqd(phi, sigma_sd, fbd)
    a2 = alpha2(cd, phi) if tracao else 1.0
    prod = max(0.7, a2*a3*a5) if tracao else 1.0
    lmin = alpha_lb*max((0.3 if tracao else 0.6)*lr, 10*phi, 100)
    return max(prod*lr, lmin), lr, lmin
def cone(fck, lb, Ac_N, k1=7.7, psi_s=1.0, psi_ec=1.0, psi_re=1.0, psi_M=1.0, gMc=1.5):
    """TR069 eq.4.3/4.4 (k1=7.7 fissurado, 11 não fissurado). Retorna (N0Rk, NRd)."""
    N0 = k1*math.sqrt(fck)*lb**1.5
    A0 = 9*lb**2
    return N0, N0*Ac_N/A0*psi_s*psi_ec*psi_re*psi_M/gMc
def psi_M(z, lb):  return max(1.0, 2-z/(1.5*lb))
def psi_s(c, ccr): return min(1.0, 0.7+0.3*c/ccr)
def psi_ec(eN, scr): return 1/(1+2*eN/scr)
def psi_re(lb):    return min(1.0, 0.5+lb/200)
def tau_sp(fck, phi, cd, cmax, lb, Ak, sp1, sp2, sp3, sp4, lb1, eta1=1.0, km=0.0, Ktr=0.0,
           tau_max_ucr=None, Omega=1.0, psi_sus=1.0, a_seis=1.0):
    """TR069 eq.4.11a-c — parâmetros Ak, sp1..sp4, lb1, tau_max da ETA do produto."""
    ph = max(phi, 12)
    t = eta1*a_seis*Ak*(fck/25)**sp1*(25/ph)**sp2*((cd/phi)**sp3*min(3.5, max(1.0, cmax/cd))**sp4+km*Ktr)*(7*phi/lb)**lb1
    if tau_max_ucr is not None:
        tp = tau_max_ucr*(min(1.0, (20*phi/lb)**lb1) if lb > 20*phi else 1.0)*Omega*psi_sus
        t = min(t, tp)
    return t
def N_sp(tau, lb, phi, gM=1.5): return tau*lb*phi*math.pi/gM
def psi_sus(a_sus, psi0):   return 1.0 if a_sus <= psi0 else psi0+1-a_sus
def stm_theta(h_ex, phi, cs, lbd_, z_red):           # Hilti S&T (6.3.1), graus
    v = math.degrees(math.atan((h_ex-max(30, 2*phi)-cs-lbd_/2)/z_red))
    return min(60.0, v)
def stm_linst(z_red, theta, lbd_, cs=0.0):  return z_red*math.tan(math.radians(theta))+lbd_/2+cs
```
Testes (`test_pir.py`, rodado em 04/10/2026 — 16/16 PASS, tolerância 1%):
| Teste | Calculado | Handbook |
|---|---|---|
| T1 lb,rqd / lbd φ14 | 219,1 / 153,4 mm | 219 / 153 |
| T2 lbd φ10 topo | 190,2 mm | 190 |
| T3 N0Rk,c / NRd,c | 90,19 / 105,48 kN | 90,2 / 105,5 |
| T4 lbd, θ, linst, σbiela | 381,7 mm; 49,55°; 570 mm; 1,97 MPa | 382; 49,6°; 571; 1,97 |
| T5 τRk,sp / NRd,c / ψM | 9,98 MPa; 133,1 kN; 1,05 | 10,0; 133,4; 1,05 |
| T6 τ sísmico / NRd,sp / NRd,c,eq | 6,86 MPa; 49,7 kN; 209,5 kN | 6,9; 49,9; 210,0 |

Limitação: não implementa incêndio (perfil de temperatura) nem overlays TR 066; parâmetros de produto vêm sempre da ETA.