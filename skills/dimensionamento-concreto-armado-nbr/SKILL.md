---
name: "dimensionamento-concreto-armado-nbr"
description: "Use ao dimensionar ou verificar peças de concreto armado pela NBR 6118:2023 — flexão (retangular, T, dupla), cisalhamento I/II, torção, ancoragem, fissuração, flecha, interação N-M e pilar-padrão."
---

# Dimensionamento de concreto armado — NBR 6118:2023 (calculadora ND)

Complementa a skill `projetos-estruturais-concreto-armado-protendido` (Parte B, seções 15–16, ficam como resumo conceitual; aqui está a ferramenta de cálculo). É o módulo `dimensionamento` do pacote `nd_estruturas` (Parte D daquela skill) e segue as mesmas convenções. Escopo inspirado na skill americana `concrete-design-calculator` (ACI 318), reescrito para a norma brasileira.

Postura: hipótese → equação → número → verificação → decisão, citando o item da norma. Toda conta em Python com `ca_nbr.py` (abaixo), conferida por caminho independente. A ART é do Nathan: itens "(conferir)" pedem confirmação no texto da NBR 6118:2023.

## 1. Convenções (iguais à Parte D)
- Unidades kN, m, kPa; fck e fyk em MPa só na entrada; armadura de saída em cm² (`_cm2`) ou cm²/m (`_cm2m`).
- Força normal: **compressão negativa**. Momento: + traciona a fibra inferior.
- Seção: y a partir do CG, + para o topo; camadas `[(As m², y m)]`.

## 2. Conceitos e roteiro por verificação

**Materiais (8.2, 17.2.2).** fcd = fck/1,4; σcd = αc·ηc·fcd, com αc = 0,85 até C50 e ηc = (40/fck)^(1/3) para fck > 40 MPa (novidade da 2023, conferir item). Até C50: λ = 0,8, εc2 = 2‰, εcu = 3,5‰, x/d ≤ 0,45; C55–C90: parâmetros reduzidos e x/d ≤ 0,35. Ecs = αi·Eci, Eci = αE·5600√fck.

**Flexão simples.** Bloco retangular λx com σcd. Se x/d passa do limite de ductilidade (14.6.4.3), armadura dupla com x fixado no limite. Seção T: se Md ≤ momento da mesa toda comprimida, calcula como retangular bf × h; senão separa abas + alma. As,mín pelo Md,mín = 0,8·W0·fctk,sup com ρ ≥ 0,15 % (17.3.5.2.1, tab. 17.3).

**Cisalhamento (17.4.2).** Modelo I: θ = 45°, Vc = Vc0 = 0,6·fctd·bw·d constante. Modelo II: 30° ≤ θ ≤ 45°, biela VRd2 menor, Vc1 cai linearmente de Vc0 (VSd ≤ Vc0) a zero (VSd = VRd2); estribo menor, mas a decalagem al cresce (al = 0,5d(cotθ − cotα), conferir) — Modelo II compensa em vigas com cortante alto e pede mais comprimento de barra longitudinal. ρsw,mín = 0,2·fctm/fywk; smáx e st,máx pela razão VSd/VRd2 (18.3.3.2).

**Torção de equilíbrio (17.5).** Seção vazada equivalente: he ≤ A/u e ≥ 2c1; Ae e ue na linha média. Biela: VSd/VRd2 + TSd/TRd2 ≤ 1 (mesmo θ). Estribo A90/s (por ramo, somar ao de cisalhamento por ramo) e longitudinal Asl/ue distribuída no perímetro, cantos obrigatórios. Torção de compatibilidade pode ser desprezada se houver estribo mínimo e a peça tolerar a fissuração (conferir 17.5.1.2).

**Ancoragem e traspasse (9.3–9.5).** fbd = η1·η2·η3·fctd (nervurada 2,25; má aderência 0,7; φ ≥ 32 reduz). lb = (φ/4)·fyd/fbd ≥ 25φ; lb,nec = α·lb·As,calc/As,ef ≥ máx(0,3lb; 10φ; 100 mm), α = 0,7 com gancho. Traspasse em tração l0t = α0t·lb,nec (α0t de 1,2 a 2,0 conforme % emendada na mesma seção). Referência rápida CA-50, boa aderência: C25 ≈ 38φ, C30 ≈ 33φ. Em má aderência (barras superiores de vigas altas, lajes concretadas em uma etapa > 60 cm) multiplicar por 1/0,7.

**Fissuração (17.3.3).** σs no estádio II (αe = 15) com combinação frequente; wk = menor de w1 (fissuração sistemática) e w2 (área de envolvimento Acri, 7,5φ ao redor da barra). Limites CA: CAA I 0,4 mm; II e III 0,3 mm; IV 0,2 mm. Na prática, controla-se reduzindo φ ou o espaçamento, não aumentando cobrimento.

**Flecha (17.3.2).** Mr = α·fctm·Ic/yt (α 1,5 retangular, 1,2 T); Branson para Ieq com Ma da combinação quase-permanente; αe = Es/Ecs. Diferida αf = Δξ/(1 + 50ρ'), Δξ = 2 − ξ(t0) (t0 = 1 mês → 1,32). Limite visual L/250; acidental L/350; elementos frágeis apoiados L/500 ou 10 mm (tab. 13.3, conferir). A contraflecha pode ser dada até L/350.

**Flexo-compressão (17.2).** Diagrama de interação N-M por fibras (parábola-retângulo), varrendo os pivôs A (aço a 10‰), B (εcu no topo) e C (εc2 a 3/7 h do topo até C50). `MRd_N` interpola o MRd para a Nd da combinação. Flexão oblíqua: verificar (Md,x/MRd,x)^α + (Md,y/MRd,y)^α ≤ 1 com α = 1,2 em seção retangular (simplificação 17.2.5.2, conferir) ou pelo modelo de fibras da skill principal.

**Pilar-padrão (15.8.3.3).** λ = le√12/h; M1d,mín = Nd(0,015 + 0,03h); λ1 = (25 + 12,5e1/h)/αb entre 35 e 90; com momento mínimo governando, αb = 1. Curvatura aproximada até λ ≤ 90 (mais conservador); rigidez κ até λ ≤ 140 (resolve a equação do 2º grau; κ/ν = 32(1 + 5Md,tot/(h·Nd))). Acima de 90 considerar fluência; acima de 140 método geral (`mef.py`, seção 21). Fazer as duas direções e checar Md,tot ≤ MRd_N.

## 3. Saída típica (memória de cálculo)
Dados e materiais → combinação que governa → ELU (flexão, cortante, torção, N-M) → ELS (wk, flecha) → detalhamento (bitolas, estribos, lb e l0) → hipóteses e itens a conferir. Tabelas com unidade em todas as colunas. Para planilha de uso repetido, levar as mesmas fórmulas para Excel com fórmulas vivas.

## 4. Validação (rodada em 11/10/2026 — repetir após qualquer alteração)
| Teste | Resultado | Referência |
|---|---|---|
| MRd 20×50, C30, 6,03 cm², N = 0 | 108,03 kN·m | `nd_api`/`mef.py` 108,03 |
| MRd 20×50, 2×4,02 cm², N = −800 kN | 178,34 kN·m | `nd_api` 178,34 |
| Flexão Md = 100 kN·m (20×50, d = 45, C30) | As = 5,51 cm²; volta pelo N-M 99,5 kN·m | conta manual 5,51; bloco × parábola ≈ 0,5 % |
| Armadura dupla Md = 250 kN·m | As 15,43 / A's 1,85 cm²; volta 248,3 | ida e volta |
| Cisalhamento 20×45, C25, VSd = 200 kN, Modelo I | VRd2 390,5; Vc 69,3; 7,43 cm²/m | conta manual |
| Mesmo, Modelo II θ = 30° | VRd2 338,2; 5,39 cm²/m | conta manual |
| Torção 25×50, c1 = 4 cm, T = 20, V = 100 | TRd2 46,5; interação 0,63; A90/s = Asl/ue = 3,31 cm²/m | conta manual |
| Ancoragem φ12,5, C25, boa / φ16 má | 37,7φ / 53,8φ | tabelas usuais 38φ / 54φ |
| Pilar 25×25, le = 3 m, Nd = −800, M1 < mín | curvatura 31,1 / κ 24,9 kN·m | κ conferido por iteração direta (24,907) |

## 5. Armadilhas
- Usar fck > 40 sem ηc (2023) superestima MRd de pilares.
- Esquecer a decalagem al ao adotar Modelo II com θ baixo.
- Somar estribo de torção (por ramo) com o de cisalhamento (total, 2 ramos) sem dividir este por 2.
- Flecha com Ma de ELU ou com Eci em vez de Ecs.
- Pilar: verificar só a direção do momento de 1ª ordem; a outra direção sempre tem pelo menos M1d,mín.
- Interação N-M: lembrar de espelhar as camadas para momento negativo (armadura assimétrica).

## Apêndice — gravar como `ca_nbr.py`
Funções: `materiais`, `As_min`, `flexao_ret`, `flexao_T`, `cisalhamento`, `torcao`, `ancoragem`, `estadio2`, `abertura_fissura` (`WK_LIM`), `flecha`, `interacao_NM`, `MRd_N`, `pilar_padrao`.

```python
"""ca_nbr.py — dimensionamento e verificação de concreto armado pela NBR 6118:2023.
Convenção do software ND (Parte D): kN, m, kPa; fck/fyk em MPa na entrada; armaduras de saída em cm²
(sufixo _cm2) ou cm²/m (sufixo _cm2m); FORÇA NORMAL: COMPRESSÃO NEGATIVA; momento + traciona a fibra inferior.
Itens marcados (conferir) devem ser checados no texto da NBR 6118:2023."""
import math
import numpy as np

ES = 210e6  # kPa

# ------------------------------------------------------------------ materiais (8.2, 17.2.2)
def materiais(fck, fyk=500, gc=1.4, gs=1.15, agregado='granito'):
    aE = {'basalto': 1.2, 'diabasio': 1.2, 'granito': 1.0, 'gnaisse': 1.0, 'calcario': 0.9, 'arenito': 0.7}[agregado]
    if fck <= 50:
        lam, ac, ec2, ecu, n = 0.8, 0.85, 2.0e-3, 3.5e-3, 2.0
        fctm = 0.3 * fck ** (2 / 3)
        Eci = aE * 5600 * math.sqrt(fck)
        xd_lim = 0.45
    else:
        lam = 0.8 - (fck - 50) / 400
        ac = 0.85 * (1 - (fck - 50) / 200)
        ec2 = (2.0 + 0.085 * (fck - 50) ** 0.53) * 1e-3
        ecu = (2.6 + 35 * ((90 - fck) / 100) ** 4) * 1e-3
        n = 1.4 + 23.4 * ((90 - fck) / 100) ** 4
        fctm = 2.12 * math.log(1 + 0.11 * fck)
        Eci = 21.5e3 * aE * (fck / 10 + 1.25) ** (1 / 3)
        xd_lim = 0.35
    eta_c = 1.0 if fck <= 40 else (40 / fck) ** (1 / 3)      # NBR 6118:2023 (conferir item)
    ai = min(0.8 + 0.2 * fck / 80, 1.0)
    fcd = fck / gc
    return dict(fck=fck, fcd=fcd * 1e3, sigcd=ac * eta_c * fcd * 1e3, lam=lam, ac=ac, eta_c=eta_c,
                ec2=ec2, ecu=ecu, n=n, fctm=fctm * 1e3, fctk_inf=0.7 * fctm * 1e3, fctk_sup=1.3 * fctm * 1e3,
                fctd=0.7 * fctm / gc * 1e3, Eci=Eci * 1e3, Ecs=ai * Eci * 1e3, fyk=fyk, fyd=fyk / gs * 1e3,
                eyd=fyk / gs * 1e3 / ES, xd_lim=xd_lim, av2=1 - fck / 250)

RHO_MIN = {20: .150, 25: .150, 30: .150, 35: .164, 40: .179, 45: .194, 50: .208, 55: .211, 60: .219,
           65: .226, 70: .233, 75: .239, 80: .245, 85: .251, 90: .256}   # % — tab. 17.3, seção retangular

def As_min(b, h, fck, fyk=500):
    """Armadura mínima de tração (17.3.5.2.1): Md,mín = 0,8·W0·fctk,sup, com ρ ≥ 0,15 %. Retorna cm²."""
    m = materiais(fck, fyk)
    d = 0.9 * h
    Mmin = 0.8 * b * h ** 2 / 6 * m['fctk_sup']
    As = Mmin / (m['fyd'] * 0.9 * d)
    tab = RHO_MIN[min(RHO_MIN, key=lambda k: abs(k - fck))] / 100 * b * h
    return max(As, 0.0015 * b * h, tab if fck > 30 else 0) * 1e4

# ------------------------------------------------------------------ flexão simples (17.2)
def flexao_ret(b, h, d, Md, fck, fyk=500, d_linha=0.05):
    """Seção retangular. Md > 0 (kN·m). Armadura dupla automática se x/d > limite de ductilidade (14.6.4.3)."""
    m = materiais(fck, fyk)
    s = m['sigcd']
    disc = d ** 2 - 2 * Md / (s * b)
    y = d - math.sqrt(disc) if disc > 0 else float('inf')
    x = y / m['lam']
    out = dict(materiais=m)
    if x / d <= m['xd_lim']:
        As = Md / (m['fyd'] * (d - y / 2))
        out.update(x=x, x_d=x / d, As_cm2=As * 1e4, Asl_cm2=0.0, dupla=False)
    else:
        x = m['xd_lim'] * d
        y = m['lam'] * x
        M1 = s * b * y * (d - y / 2)
        dM = Md - M1
        es_l = m['ecu'] * (x - d_linha) / x
        sig_l = min(es_l * ES, m['fyd'])
        Asl = dM / (sig_l * (d - d_linha))
        As = M1 / (m['fyd'] * (d - y / 2)) + dM / (m['fyd'] * (d - d_linha))
        out.update(x=x, x_d=x / d, As_cm2=As * 1e4, Asl_cm2=Asl * 1e4, dupla=True, sig_sl=sig_l / 1e3)
    out['As_min_cm2'] = As_min(b, h, fck, fyk)
    out['As_adot_cm2'] = max(out['As_cm2'], out['As_min_cm2'])
    out['dominio'] = 2 if out['x_d'] <= m['ecu'] / (m['ecu'] + 0.010) else 3
    return out

def flexao_T(bf, bw, hf, h, d, Md, fck, fyk=500, d_linha=0.05):
    """Seção T (mesa comprimida). Se a LN cair na mesa, calcula como retangular bf × h."""
    m = materiais(fck, fyk)
    s = m['sigcd']
    Mmesa = s * bf * hf * (d - hf / 2)
    if Md <= Mmesa:
        r = flexao_ret(bf, h, d, Md, fck, fyk, d_linha); r['caso'] = 'LN na mesa'
        r['As_min_cm2'] = As_min(bw, h, fck, fyk); r['As_adot_cm2'] = max(r['As_cm2'], r['As_min_cm2'])
        return r
    Mf = s * (bf - bw) * hf * (d - hf / 2)
    Asf = Mf / m['fyd'] / (d - hf / 2)
    r = flexao_ret(bw, h, d, Md - Mf, fck, fyk, d_linha)
    r['As_cm2'] += Asf * 1e4
    r['As_min_cm2'] = As_min(bw, h, fck, fyk)
    r['As_adot_cm2'] = max(r['As_cm2'], r['As_min_cm2'])
    r['caso'] = 'LN na alma'
    return r

# ------------------------------------------------------------------ cisalhamento (17.4)
def cisalhamento(bw, d, Vsd, fck, fyk=500, modelo='I', theta=45, alpha=90):
    """Estribos (cm²/m). Flexão simples. modelo 'I' (θ=45°) ou 'II' (30° ≤ θ ≤ 45°)."""
    m = materiais(fck, fyk)
    a, t = math.radians(alpha), math.radians(45 if modelo == 'I' else theta)
    fywd = min(m['fyd'], 435e3)
    Vc0 = 0.6 * m['fctd'] * bw * d
    if modelo == 'I':
        VRd2 = 0.27 * m['av2'] * m['fcd'] * bw * d
        Vc = Vc0
        k = 0.9 * d * fywd * (math.sin(a) + math.cos(a))
    else:
        VRd2 = 0.54 * m['av2'] * m['fcd'] * bw * d * math.sin(t) ** 2 * (1 / math.tan(a) + 1 / math.tan(t))
        Vc = Vc0 if Vsd <= Vc0 else max(0.0, Vc0 * (VRd2 - Vsd) / (VRd2 - Vc0))
        k = 0.9 * d * fywd * (1 / math.tan(a) + 1 / math.tan(t)) * math.sin(a)
    Asw = max(Vsd - Vc, 0) / k
    Asw_min = 0.2 * m['fctm'] / (fyk * 1e3) * bw * math.sin(a)
    smax = min(0.6 * d, 0.30) if Vsd <= 0.67 * VRd2 else min(0.3 * d, 0.20)
    stmax = min(d, 0.80) if Vsd <= 0.20 * VRd2 else min(0.6 * d, 0.35)
    return dict(VRd2=VRd2, biela_ok=Vsd <= VRd2, Vc=Vc, Asw_s_cm2m=Asw * 1e4, Asw_min_cm2m=Asw_min * 1e4,
                Asw_adot_cm2m=max(Asw, Asw_min) * 1e4, s_max=smax, st_max=stmax)

# ------------------------------------------------------------------ torção (17.5)
def torcao(b, h, c1, Tsd, Vsd, fck, fyk=500, modelo='I', theta=45):
    """Seção vazada equivalente. c1 = distância da face ao eixo da barra longitudinal de canto (m).
    Retorna estribo de torção por ramo (cm²/m), longitudinal total (cm²/m de perímetro e cm²) e interação V+T."""
    m = materiais(fck, fyk)
    t = math.radians(45 if modelo == 'I' else theta)
    A, u = b * h, 2 * (b + h)
    he = A / u
    obs = ''
    if he < 2 * c1:
        obs = 'A/u < 2c1: he = A/u (deve ser ≤ b − 2c1) — conferir 17.5.1.4.1'
    Ae, ue = (b - he) * (h - he), 2 * (b + h - 2 * he)
    fywd = min(m['fyd'], 435e3)
    TRd2 = 0.5 * m['av2'] * m['fcd'] * Ae * he * math.sin(2 * t)
    VRd2 = cisalhamento(b, 0.9 * h, Vsd, fck, fyk, modelo, theta)['VRd2']
    inter = Vsd / VRd2 + Tsd / TRd2
    A90 = Tsd / (2 * Ae * fywd / math.tan(t))
    Asl = Tsd / (2 * Ae * fywd * math.tan(t))
    rmin = 0.2 * m['fctm'] / (fyk * 1e3)
    return dict(he=he, Ae=Ae, ue=ue, TRd2=TRd2, interacao=inter, ok=inter <= 1.0,
                A90_s_cm2m=max(A90, rmin * b / 2) * 1e4,     # por ramo (mínimo: ρsw·bw dividido em 2 ramos)
                Asl_ue_cm2m=max(Asl, rmin * b) * 1e4, Asl_total_cm2=max(Asl, rmin * b) * ue * 1e4, obs=obs)

# ------------------------------------------------------------------ ancoragem e traspasse (9.3, 9.4, 9.5)
def ancoragem(phi_mm, fck, fyk=500, aderencia='boa', superficie='nervurada', As_calc=1.0, As_ef=1.0,
              gancho=False, pct_emendada=50, compressao=False):
    m = materiais(fck, fyk)
    e1 = {'lisa': 1.0, 'entalhada': 1.4, 'nervurada': 2.25}[superficie]
    e2 = 1.0 if aderencia == 'boa' else 0.7
    e3 = 1.0 if phi_mm < 32 else (132 - phi_mm) / 100
    fbd = e1 * e2 * e3 * m['fctd']
    phi = phi_mm / 1000
    lb = max(phi / 4 * m['fyd'] / fbd, 25 * phi)
    alfa = 0.7 if (gancho and not compressao) else 1.0
    lb_min = max(0.3 * lb, 10 * phi, 0.10)
    lb_nec = max(alfa * lb * As_calc / As_ef, lb_min)
    a0t = 1.2 if pct_emendada <= 20 else 1.4 if pct_emendada <= 25 else 1.6 if pct_emendada <= 33 else 1.8 if pct_emendada <= 50 else 2.0
    if compressao:
        l0 = max(lb * As_calc / As_ef, 0.6 * lb, 15 * phi, 0.20)
    else:
        l0 = max(a0t * lb_nec, 0.3 * a0t * lb, 15 * phi, 0.20)
    return dict(fbd=fbd / 1e3, lb=lb, lb_phi=lb / phi, lb_nec=lb_nec, l0=l0, l0_phi=l0 / phi, alfa_0t=a0t)

# ------------------------------------------------------------------ estádio II e fissuração (17.3.3)
def estadio2(b, d, As, Asl=0.0, d_linha=0.05, M=0.0, alfa_e=15):
    """Seção retangular fissurada. As em m². Retorna x2, I2 (m⁴) e σs (MPa) para o momento M (kN·m)."""
    a = b / 2
    bb = alfa_e * (As + Asl)
    c = -alfa_e * (As * d + Asl * d_linha)
    x = (-bb + math.sqrt(bb ** 2 - 4 * a * c)) / (2 * a)
    I2 = b * x ** 3 / 3 + alfa_e * As * (d - x) ** 2 + alfa_e * Asl * (x - d_linha) ** 2
    return dict(x2=x, I2=I2, sigma_s=alfa_e * M * (d - x) / I2 / 1e3)

def abertura_fissura(phi_mm, sigma_s, fck, Acri=None, Asi=None, cobr=0.03, espac=None, eta1=2.25):
    """wk (mm), combinação frequente. σs em MPa (estádio II, αe = 15). Acri: área de envolvimento da barra (m²);
    se None, aproxima por min(espac, 15φ) × (cobr + φ/2 + 7,5φ) (conferir no detalhamento)."""
    m = materiais(fck)
    phi = phi_mm / 1000
    if Acri is None:
        largura = 15 * phi if espac is None else min(espac, 15 * phi)
        Acri = largura * (cobr + phi / 2 + 7.5 * phi)
    if Asi is None:
        Asi = math.pi * phi ** 2 / 4
    rho = Asi / Acri
    fct = m['fctm'] / 1e3
    w1 = phi_mm / (12.5 * eta1) * sigma_s / 210000 * 3 * sigma_s / fct
    w2 = phi_mm / (12.5 * eta1) * sigma_s / 210000 * (4 / rho + 45)
    return dict(w1=w1, w2=w2, wk=min(w1, w2), rho_ri=rho)

WK_LIM = {'I': 0.4, 'II': 0.3, 'III': 0.3, 'IV': 0.2}   # mm, tab. 13.4 (CA)

# ------------------------------------------------------------------ flecha (17.3.2)
def flecha(b, h, d, As, Ma, L, fck, Asl=0.0, k=5 / 48, t0_meses=1, alfa_fis=1.5, agregado='granito'):
    """Flecha imediata (Branson) e total com fluência. Ma = momento da combinação quase-permanente (kN·m).
    k: a = k·Ma·L²/(E·I) — 5/48 biapoiada com carga distribuída; 1/4 balanço com carga distribuída;
    1/12 biapoiada com carga concentrada no meio. As, Asl em m²."""
    m = materiais(fck, agregado=agregado)
    Ecs = m['Ecs']
    Ic = b * h ** 3 / 12
    Mr = alfa_fis * m['fctm'] * Ic / (h / 2)
    ae = ES / Ecs
    I2 = estadio2(b, d, As, Asl, h - d, Ma, ae)['I2']
    Ieq = Ic if Ma <= Mr else min((Mr / Ma) ** 3 * Ic + (1 - (Mr / Ma) ** 3) * I2, Ic)
    a0 = k * Ma * L ** 2 / (Ecs * Ieq)
    xi = lambda t: 2.0 if t > 70 else 0.68 * 0.996 ** t * t ** 0.32
    af = (2.0 - xi(t0_meses)) / (1 + 50 * Asl / (b * d))
    at = a0 * (1 + af)
    return dict(Mr=Mr, Ic=Ic, I2=I2, Ieq=Ieq, Ecs=Ecs, a_imed=a0, alfa_f=af, a_total=at,
                lim_L250=L / 250, ok=at <= L / 250)

# ------------------------------------------------------------------ flexo-compressão: diagrama N-M (17.2)
def _sigc(e, m):
    """Parábola-retângulo, compressão positiva aqui (convertida na saída)."""
    if e <= 0: return 0.0
    if e >= m['ec2']: return m['sigcd']
    return m['sigcd'] * (1 - (1 - e / m['ec2']) ** m['n'])

def _esforcos(b, h, camadas, m, eps_top, eps_bot, nf=200):
    ys = np.linspace(h / 2, -h / 2, nf + 1)
    yc = (ys[:-1] + ys[1:]) / 2
    dy = h / nf
    eps = lambda y: eps_bot + (eps_top - eps_bot) * (y + h / 2) / h      # + encurtamento
    N = M = 0.0
    for y in yc:
        s = _sigc(eps(y), m) * b * dy
        N += s; M += s * y
    for As, y in camadas:
        e = eps(y)
        s = max(-m['fyd'], min(m['fyd'], e * ES))
        if e > 0 and abs(y) <= h / 2: s -= _sigc(e, m)       # desconta o concreto deslocado
        N += s * As; M += s * As * y
    return -N, M        # saída: compressão NEGATIVA; M + comprime o topo (traciona a fibra inferior)

def interacao_NM(b, h, camadas, fck, fyk=500, npts=120):
    """Curva (N, M) resistente de cálculo para M ≥ 0 (topo comprimido). camadas = [(As m², y m, + topo)].
    Para M < 0, chamar com as camadas espelhadas (y → −y)."""
    m = materiais(fck, fyk)
    ymin = min(y for _, y in camadas)
    d = h / 2 - ymin
    pts = []
    # pivô A: aço inferior a 10‰ de alongamento; topo de +10‰ alongamento até εcu
    for et in np.linspace(-0.010, m['ecu'], npts):
        es = -0.010
        eb = et + (es - et) * h / d
        pts.append(_esforcos(b, h, camadas, m, et, eb))
    # pivô B: topo em εcu; LN de x23 até h
    x23 = m['ecu'] / (m['ecu'] + 0.010) * d
    for x in np.linspace(x23, h, npts):
        pts.append(_esforcos(b, h, camadas, m, m['ecu'], m['ecu'] * (x - h) / x))
    # pivô C: ponto a (1 − εc2/εcu)h do topo com εc2
    yC = (1 - m['ec2'] / m['ecu']) * h
    for et in np.linspace(m['ecu'], m['ec2'], npts):
        eb = et + (m['ec2'] - et) * h / yC
        pts.append(_esforcos(b, h, camadas, m, et, eb))
    return np.array(pts)

def MRd_N(b, h, camadas, fck, Nd, fyk=500):
    """MRd (kN·m, positivo) para a força normal de cálculo Nd (compressão negativa)."""
    c = interacao_NM(b, h, camadas, fck, fyk, 300)
    N, M = c[:, 0], c[:, 1]
    best = None
    for i in range(len(N) - 1):
        if (N[i] - Nd) * (N[i + 1] - Nd) <= 0 and N[i] != N[i + 1]:
            Mi = M[i] + (M[i + 1] - M[i]) * (Nd - N[i]) / (N[i + 1] - N[i])
            best = Mi if best is None else max(best, Mi)
    return best   # None: Nd fora do intervalo resistente

# ------------------------------------------------------------------ pilar-padrão (15.8.3.3)
def pilar_padrao(b, h, le, Nd, M1A, M1B=None, metodo='curvatura', alfa_b=None, fck=30):
    """Uma direção (h = dimensão na direção do momento). Nd < 0 (compressão). M1A ≥ |M1B| (kN·m);
    M1B com sinal: + mesma curvatura do M1A. alfa_b=None → pilar biapoiado sem carga transversal."""
    m = materiais(fck)
    N = -Nd
    lam = le * math.sqrt(12) / h
    M1min = N * (0.015 + 0.03 * h)
    usa_min = M1A < M1min
    MA = max(M1A, M1min)
    if alfa_b is None:
        alfa_b = 1.0 if (usa_min or M1B is None) else max(0.6 + 0.4 * M1B / M1A, 0.4)
    e1 = MA / N
    lam1 = min(max((25 + 12.5 * e1 / h) / alfa_b, 35), 90)
    nu = N / (b * h * m['fcd'])
    if lam <= lam1:
        Mtot = MA
    elif metodo == 'curvatura':
        r = min(0.005 / (h * (nu + 0.5)), 0.005 / h)
        Mtot = max(alfa_b * MA + N * le ** 2 / 10 * r, MA)
    else:   # rigidez κ aproximada — raiz positiva da equação de 2º grau
        A = 5 * h
        B = h ** 2 * N - N * le ** 2 / 320 - 5 * h * alfa_b * MA
        C = -N * h ** 2 * alfa_b * MA
        Mtot = max((-B + math.sqrt(B ** 2 - 4 * A * C)) / (2 * A), MA)
    return dict(lambda_=lam, lambda1=lam1, nu=nu, M1d_min=M1min, alfa_b=alfa_b,
                segunda_ordem=lam > lam1, Md_tot=Mtot, valido=lam <= (90 if metodo == 'curvatura' else 140))
```