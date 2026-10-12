---
name: "biblioteca-parametrica-nd"
description: "Estimar nova peça/estrutura (altura, aço, cordoalhas, volume, custo) combinando casos já calculados da ND, com semáforo de confiança contra extrapolação. Baseado no método LAMP (ICML 2026)."
---

# Biblioteca paramétrica ND (método LAMP adaptado)

Adaptação do LAMP (Nehme et al., MIT/Toyota, ICML 2026, github.com/ghadinehme/LAMP) para estruturas de concreto armado, protendido e pré-moldado. Do LAMP aproveitamos três ideias; a parte de redes neurais SDF/malhas NÃO se aplica a cálculo estrutural e fica de fora.

1. **Mistura afim de casos resolvidos**: um caso novo é estimado como combinação dos casos já calculados (pesos somam 1), escolhida para bater exatamente os parâmetros-alvo (vão, carga, pé-direito, fck...).
2. **Métrica de segurança da extrapolação**: semáforo que diz quando a estimativa sai da região confiável.
3. **Otimização guiada por desempenho**: fixa alguns parâmetros e varre os livres minimizando custo, aço ou volume.

## Quando usar
- Pré-dimensionamento rápido de vigas, pilares, lajes alveolares, terças, consolos, tesouras, blocos.
- Orçamento e proposta comercial antes do cálculo: taxa de aço, m³, cordoalhas, R$/m².
- Conferir se um resultado de projeto está fora do padrão da biblioteca (outlier = possível erro).
- Comparar alternativas (vão x altura x custo) para o cliente ou a fábrica.

## Quando NÃO usar
- Nunca como dimensionamento final. Todo resultado precisa de verificação pela NBR 6118 / 6120 / 6123 / 9062 / 8681 nas skills de dimensionamento.
- Casos fora da família (outro sistema estrutural, outra vinculação, outra classe de agressividade) não entram na mesma biblioteca.
- Status VERMELHO: calcular direto.

## Fluxo
1. **Montar a biblioteca** (CSV/planilha): uma linha por caso já calculado e verificado. Colunas de parâmetros (entrada) e colunas de resultado (saída). Separar por família: "viga I protendida biapoiada", "pilar com consolo", "laje alveolar h=20"... Mínimo prático: 8-10 casos por família; ideal 30+.
2. **Âncora**: o caso mais próximo da média da família (no LAMP é o modelo base). Útil como referência ao apresentar o resultado.
3. **Rodar `mistura_afim`** com k = 6 a 10 vizinhos mais próximos.
4. **Ler o semáforo**:
   - VERDE: dentro da faixa e trecho praticamente linear. Serve para orçamento e pré-dim.
   - AMARELO: fora da faixa, peso negativo relevante ou não linearidade. Só pré-dimensionamento, com margem.
   - VERMELHO: não usar; calcular direto.
5. **Verificar** pela norma com as skills de dimensionamento. Se o caso verificado for bom, **adicioná-lo à biblioteca** (ela melhora a cada projeto).
6. Para alternativas, rodar `otimizar_desempenho`.

## Cuidados de engenharia
- Grandezas com variação fortemente não linear (momento ~ L², flecha ~ L⁴) interpolam melhor se a biblioteca guardar também variáveis transformadas (ex.: q·L²/8, L/h). O teste mostrou erro <1% dentro da faixa e ~9% em extrapolação longa: por isso o semáforo.
- Resultados discretos (nº de cordoalhas, bitolas) saem contínuos: arredondar para cima e verificar.
- Normalização é automática; parâmetros com faixas muito diferentes não distorcem.
- Não misturar casos de fck, aço ou cobrimento diferentes sem colocar essas grandezas como parâmetro.
- Saída em tela (tabela/artefato), conforme preferência do Nathan; não entregar .zip.

## Código

```python
import numpy as np
from scipy.optimize import minimize


def normalizar(P):
    mu, sd = P.mean(0), P.std(0)
    sd[sd == 0] = 1.0
    return mu, sd


def mistura_afim(P, Y, alvo, k=None, lam=1e-3, ancora=None):
    """P: (n,m) parâmetros dos casos; Y: (n,q) resultados; alvo: (m,).
    Retorna Y estimado e diagnóstico com semáforo."""
    P, Y, alvo = np.asarray(P, float), np.asarray(Y, float), np.asarray(alvo, float)
    mu, sd = normalizar(P)
    Pn, tn = (P - mu) / sd, (alvo - mu) / sd
    d = np.linalg.norm(Pn - tn, axis=1)
    idx = np.argsort(d)[: (k or len(P))]
    Pk, Yk, dk = Pn[idx], Y[idx], d[idx]
    n = len(idx)
    w = 1.0 + dk / (dk.mean() + 1e-9)
    a0 = np.full(n, 1.0 / n) if ancora is None else np.eye(n)[0]
    obj = lambda a: np.sum(w * (a - a0) ** 2) + lam * np.sum(a ** 2)
    cons = [{"type": "eq", "fun": lambda a: a.sum() - 1.0},
            {"type": "eq", "fun": lambda a: Pk.T @ a - tn}]
    r = minimize(obj, a0, constraints=cons, method="SLSQP",
                 options={"maxiter": 500, "ftol": 1e-12})
    a = r.x
    y = Yk.T @ a
    neg = float(-a[a < 0].sum())
    fora = bool(np.any((alvo < P.min(0)) | (alvo > P.max(0))))
    loo = []
    for j in range(n):
        m_ = np.ones(n, bool); m_[j] = False
        A = np.c_[Pk[m_], np.ones(m_.sum())]
        coef, *_ = np.linalg.lstsq(A, Yk[m_], rcond=None)
        pred = np.r_[Pk[j], 1.0] @ coef
        loo.append(np.abs(pred - Yk[j]) / (np.abs(Yk[j]) + 1e-9))
    mismatch = float(np.mean(loo))
    if not r.success or neg > 0.5 or mismatch > 0.15:
        status = "VERMELHO - não usar; calcular direto"
    elif fora or neg > 0.1 or mismatch > 0.05:
        status = "AMARELO - extrapolação/não linearidade; só pré-dimensionamento"
    else:
        status = "VERDE - interpolação confiável para estimativa"
    diag = dict(casos=idx.tolist(), alfa=np.round(a, 4).tolist(),
                peso_negativo=round(neg, 3), fora_da_faixa=fora,
                mismatch_linear=round(mismatch, 4), status=status,
                restricao_ok=bool(np.allclose(Pk.T @ a, tn, atol=1e-6)))
    return y, diag


def otimizar_desempenho(P, Y, fixos, livres_faixa, custo_col, k=None):
    """fixos: {indice: valor}; livres_faixa: {indice: (min, max, passos)}.
    Minimiza a coluna custo_col de Y, ignorando combinações VERMELHAS."""
    import itertools
    grades = {i: np.linspace(*f) for i, f in livres_faixa.items()}
    melhor = None
    for comb in itertools.product(*grades.values()):
        alvo = np.zeros(np.asarray(P).shape[1])
        for i, v in fixos.items(): alvo[i] = v
        for i, v in zip(grades, comb): alvo[i] = v
        y, dg = mistura_afim(P, Y, alvo, k=k)
        if dg["status"].startswith("VERMELHO"): continue
        if melhor is None or y[custo_col] < melhor[1][custo_col]:
            melhor = (alvo, y, dg)
    return melhor
```

## Validação (teste sintético, viga biapoiada, 30 casos L=8-20 m, q=20-60 kN/m)
| Alvo | As estimado | As real | Semáforo |
|---|---|---|---|
| L=14, q=40 (dentro) | 323,9 | 320,9 | VERDE (erro 0,9%) |
| L=19, q=55 (borda) | 593,4 | 598,1 | AMARELO |
| L=26, q=70 (fora) | 959,7 | 1049,2 | VERMELHO (erro 8,5%) |

## Apresentação do resultado
Tabela curta: parâmetros-alvo, valores estimados, casos usados (com pesos), semáforo e a frase "estimativa por biblioteca ND — verificar pela NBR antes de emitir". Em imagens/relatórios para cliente, marcar "projeto da ND Engenharia".

## Ligação com outras skills
- Biblioteca alimentada por: vigas-premoldadas-protendidas, dimensionamento-concreto-armado-nbr, projeto-estruturas-pre-moldadas, mef-opensees-opsvis.
- Consumida por: orcamentista-obras, comparar-sistemas-estruturais, consultoria-fabricas-pre-moldados.
- Futuro módulo do software estrutural ND (nd_estruturas).