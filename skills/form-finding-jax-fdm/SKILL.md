---
name: "form-finding-jax-fdm"
description: "Use ao achar a forma de cascas, arcos, gridshells, redes de cabos ou treliças pelo método das densidades de força com o JAX FDM (form-finding inverso) e levar a geometria para o OpenSees (cascas, vigas de borda, estabilidade)."
---

# Form-finding com JAX FDM → OpenSees (pipeline ND Engenharia)

Complementa a `mef-opensees-opsvis` (motor de análise) e a Parte D da `projetos-estruturais-concreto-armado-protendido` (convenções do software `nd_estruturas`: kN·m, compressão negativa, JSON). O JAX FDM **acha a forma**; o OpenSees **analisa**; o dimensionamento continua pela NBR 6118. Responder em português técnico. A ART é do Nathan: sinalizar vínculos, rigidez de borda, espessura e cargas que pedem decisão dele.

## 1. Quando usar
| Caso | Use |
|---|---|
| Casca/abóbada de compressão, arco, gridshell, cúpula, sela | JAX FDM + `formfinding.modelo_casca` |
| Rede de cabos, membrana, tensegridade (forma e protensão) | JAX FDM (sem a parte de casca) |
| Treliça com banzo de força constante, arco de volume mínimo | JAX FDM com metas de força / load path |
| Pilar, viga, laje alveolar, pórtico convencional | **Não** — usar `ops_nd` direto |

## 2. Instalação
`pip install jax-fdm openseespy opsvis` (testado: jax-fdm 0.14.1, JAX 0.11.2, OpenSeesPy 3.8, Python 3.13; no sandbox `--break-system-packages`). Repositório: github.com/arpastrana/jax_fdm (MIT). Primeira chamada compila (JIT) ≈ 2,5 s.

## 3. Teoria (resumo para memória de cálculo)
1. **FDM (Linkwitz & Schek 1971; Schek 1974, CMAME 3:115-134).** Incógnita q = N/L por barra torna o equilíbrio linear, separado em x, y, z:
   `D·x_livre = p − C_livreᵀ·Q·C_apoio·x_apoio`, `D = C_livreᵀ·Q·C_livre` (simétrica, esparsa). q < 0 em todas as barras → forma funicular só de compressão. Sem material nem seção.
2. **Inverso:** `min L(q) = Σ wᵢ (gᵢ(x(q)) − alvoᵢ)²` com limites em q (variáveis também podem ser apoios e cargas). Metas suaves (goals) entram na perda; restrições rígidas (constraints) exigem SLSQP/trust-constr e o solver denso (mais lento: 15 s × 0,2 s no exemplo da sela).
3. **Gradiente exato pelo adjunto** (diferenciação implícita): `D·λ = ∂L/∂x` (mesma D, simétrica) → `dL/dq = −λᵀ(∂D/∂q·x − ∂b/∂q)`. Um solve extra, independente do número de variáveis (`sparse.py`, `jax.custom_vjp`).
4. **Otimizador:** L-BFGS-B padrão (Byrd et al. 1995); também BFGS, Newton-CG, trust-region, SLSQP e métodos sem gradiente.
5. **Cargas dependentes da forma** (peso por área real, cargas seguidoras): ponto fixo (`tmax > 1`) com gradiente pelo teorema da função implícita.
6. Citação: Pastrana, Oktay, Bletzinger, Adams, Adriaenssens. *Differentiable force density method for the design of lightweight structures.* CMAME 458, 118783, 2026.

## 4. Regras aprendidas (testes de out/2026)
- **A solução não é única.** Mesmas metas, malha 12×12 → empuxo 901 kN/canto; 24×24 → 734 kN. Fixar critério extra (força uniforme na borda, `NetworkLoadPathGoal`/`MeshLoadPathGoal` = volume mínimo) quando o empuxo ou a distribuição importar.
- **Metas incompatíveis não dão erro**: a cúpula do repositório parou com perda 0,025 após 8.807 iterações. Conferir sempre a perda final e cada meta, não só "convergiu".
- Pesos mudam o resultado: na sela com várias metas o load path subiu 11 %.
- **Rede ≠ casca.** A rede quadrada sem diagonais não resiste a cisalhamento no plano; a casca redistribui pela compatibilidade. Mesmo empuxo total (+1,4 %), distribuição diferente (rede 84 kN/m concentrado no meio × casca ~45 kN/m uniforme). Por isso a passagem para o MEF é obrigatória.
- Funicular só para a carga do form-finding: carga assimétrica, vento e recalque geram flexão.
- A rede FDM move os nós em planta: aplicar a carga da casca pelo **espaçamento original** (cantos fixos), como o FDM fez — senão a carga total sai errada (erro real encontrado: 991 × 1.398 kN).
- Rodar exemplos do repositório sem janela: substituir `Viewer`/`Plotter` por um objeto que absorve qualquer atributo (`viewer.renderer.camera...`) e criar módulo falso para `compas_viewer` (dependência opcional).

## 5. Validação (repetir após qualquer alteração — `pytest -q tests/test_formfinding.py`, 5 testes, ~6 s)
Casca 20 × 20 m apoiada nos 4 cantos, 3,5 kPa em projeção, metas 4,0 m (centro) e 2,5 m (meio das bordas); casca 10 cm C30, vigas de borda 35 × 35, malha 24 × 24.
| Verificação | Modelo | Referência |
|---|---|---|
| Metas de altura | 4,000 / 2,500 m | alvo (25 iterações L-BFGS-B, 0,14 s) |
| Σ reações verticais | 1.397,6 kN | carga aplicada 1.397,6 kN |
| Empuxo por canto, casca × rede | 744,2 kN | 733,6 kN (+1,4 %) |
| Empuxo no corte central | 1.076 kN | 1.037 kN rede (+3,7 %) |
| Malha 24 × 24 × 48 × 48 (\|M\|, flecha) | 5,83 / 10,46 | 5,95 / 10,73 (−2 a −3 %) |
| Funicular × geométrica de mesmas alturas, ELU uniforme 1,4(G+Q) | \|M\| 1,36 × 5,83 kN·m/m; tração face 0,53 × 2,45 MPa; flecha 4,5 × 10,5 mm | geométrica fissura (> fctk,inf 2,03 MPa C30, NBR 6118:2023 — conferir) |
| Estabilidade elástica (ShellNLDKGQ, ELU assimétrica) | λ ≈ 43 funicular × 24 geométrica | casca perfeita, sem fissura: só comparativo |

Exemplos oficiais (12/12 rodaram em CPU, 3–25 s): gridshell planarizado 28 % → 100 % de painéis planos; treliça com banzo 0,91–1,66 → 1,500 em todas as barras; arco de volume mínimo −27 %; rede de cabos com borda 20,00 ± 0,001 kN; 6 arcos com direção de reação imposta (V/H 0,1 a 3,2).

## 6. Roteiro
1. Definir planta, apoios, carga de forma (G + ψ·Q, em projeção) e metas (flechas, alturas de borda, reações, comprimentos de peça, planaridade).
2. `F = forma_casca(...)` (ou montar `FDNetwork`/`FDMesh` própria). Conferir perda final, metas atingidas, sinal de todas as forças.
3. Se o empuxo/distribuição importar: acrescentar meta de load path ou força uniforme e comparar.
4. `mod = modelo_casca(F['xyz'], t, fck, viga)`; `cargas(mod, q_planta, gviga=...)`; `analisar_linear()`; `esforcos(mod)` e `esforcos_vigas(mod)` por combinação (uniforme e assimétrica no mínimo; vento à parte).
5. Conferir ΣRz = carga, empuxo casca × rede (< 5 %), malha (refinar até < 3 %).
6. `estabilidade_nl(...)` para comparar formas; para projeto aplicar imperfeição, fluência e fissuração (decisão do Nathan).
7. Dimensionar casca (tração > fctk,inf → armar; membrana tracionada As = N/fyd), vigas de borda (N + M) e apoios/tirantes (empuxo ELU) pela NBR 6118. Regiões dos cantos: modelo refinado ou região D.
8. Imagens marcadas "projeto da ND Engenharia"; entregar em página/artefato com 3D (sem .zip).

## 7. Limitações
- Grelha quadrada apoiada nos 4 cantos em `forma_casca`; outras plantas: montar a rede à mão ou com `FDMesh.from_meshgrid`.
- Viga de borda no plano médio (sem excentricidade); concreto elástico, rigidez bruta; cargas só verticais.
- Picos junto aos apoios dependem da malha e do detalhe real.
- Restrições rígidas forçam o solver denso (lento em malhas grandes).

## 8. Código — `nd_estruturas/formfinding.py`
```python
"""nd_estruturas.formfinding — ponte JAX FDM -> OpenSeesPy (ND Engenharia).

1) forma_casca(): form-finding inverso (JAX FDM) de casca em grelha quadrada apoiada nos 4 cantos.
2) modelo_casca(): casca ShellMITC4/ShellNLDKGQ + vigas de borda sobre a geometria encontrada.
3) esforcos(): N, M por elemento, tensões nas faces, reações.
4) estabilidade_nl(): fator de carga elástico com não linearidade geométrica (ShellNLDKGQ + comprimento de arco).
Unidades: kN, m, kPa. Compressão negativa.
"""
import numpy as np
import openseespy.opensees as ops


# ----------------------------------------------------------------------------- 1. forma (JAX FDM)
def forma_casca(L=20.0, n=24, carga=3.5, H_coroa=4.0, H_arco=2.5, q_int=-25.0, q_borda=-120.0):
    """Grelha (n+1)x(n+1) em planta LxL, cantos fixos, carga vertical por área de influência em planta.
    Ajusta todas as densidades de força para atingir H_coroa (centro) e H_arco (meio das 4 bordas).
    Retorna xyz (n+1,n+1,3), forças nas barras, reações e o número de iterações."""
    from jax_fdm.datastructures import FDNetwork
    from jax_fdm.equilibrium import constrained_fdm
    from jax_fdm.goals import NodeZCoordinateGoal
    from jax_fdm.losses import Loss, SquaredError
    from jax_fdm.optimization import LBFGSB
    from jax_fdm.parameters import EdgeForceDensityParameter

    assert n % 2 == 0
    a = L / n
    net = FDNetwork(); k = {}
    for i in range(n + 1):
        for j in range(n + 1):
            k[i, j] = net.add_node(x=i * a - L / 2, y=j * a - L / 2, z=0.0)
    borda = set()
    for i in range(n + 1):
        for j in range(n + 1):
            for di, dj in ((1, 0), (0, 1)):
                if i + di <= n and j + dj <= n:
                    e = net.add_edge(k[i, j], k[i + di, j + dj])
                    if (di and j in (0, n)) or (dj and i in (0, n)):
                        borda.add(e)
    cantos = [k[0, 0], k[n, 0], k[0, n], k[n, n]]
    for c in cantos:
        net.node_anchor(c)
    for (i, j), kk in k.items():
        if kk in cantos:
            continue
        f = (0.5 if i in (0, n) else 1.0) * (0.5 if j in (0, n) else 1.0)
        net.node_load(kk, load=[0.0, 0.0, -carga * a * a * f])
    # q escala com 1/a para o chute dar altura parecida em qualquer malha
    for e in net.edges():
        net.edge_forcedensity(e, (q_borda if e in borda else q_int) * (12 / n))
    params = [EdgeForceDensityParameter(e, None, -1e-3) for e in net.edges()]
    goals = [NodeZCoordinateGoal(k[n // 2, n // 2], target=H_coroa)]
    goals += [NodeZCoordinateGoal(k[p], target=H_arco) for p in ((n // 2, 0), (n // 2, n), (0, n // 2), (n, n // 2))]
    rede = constrained_fdm(net, optimizer=LBFGSB(), parameters=params, loss=Loss(SquaredError(goals)),
                           maxiter=5000, tol=1e-12)
    xyz = np.array([[rede.node_coordinates(k[i, j]) for j in range(n + 1)] for i in range(n + 1)])
    forcas = {(u, v): float(rede.edge_force((u, v))) for u, v in rede.edges()}
    reac = [rede.node_reaction(c) for c in cantos]
    idx = {kk: ij for ij, kk in k.items()}
    return dict(xyz=xyz, forcas=forcas, reacoes=reac, borda=borda, idx=idx, L=L, n=n, a=a, carga=carga)


def forma_geometrica(L=20.0, n=24, H_coroa=4.0, H_arco=2.5):
    """Superfície analítica com as mesmas alturas-chave: z = A(f(x)+f(y)) + B f(x)f(y), f(u) = 1 − (2u/L)².
    Cantos em 0, meio das bordas em H_arco, centro em H_coroa. Não é funicular."""
    a = L / n; A = H_arco; B = H_coroa - 2 * H_arco
    xyz = np.zeros((n + 1, n + 1, 3))
    for i in range(n + 1):
        for j in range(n + 1):
            x, y = i * a - L / 2, j * a - L / 2
            fx, fy = 1 - (2 * x / L) ** 2, 1 - (2 * y / L) ** 2
            xyz[i, j] = (x, y, A * (fx + fy) + B * fx * fy)
    return xyz


# ----------------------------------------------------------------------------- 2. modelo (OpenSees)
def Ecs_nbr(fck, alpha_E=1.0):
    Eci = alpha_E * 5600 * np.sqrt(fck)
    return min(0.8 + 0.2 * fck / 80, 1.0) * Eci * 1e3


def modelo_casca(xyz, t=0.10, fck=30, viga=(0.35, 0.35), elem='ShellMITC4', nu=0.2):
    """Monta o domínio: nós da grelha, cascas quadrilaterais, vigas de borda (eixo no plano médio da casca,
    sem excentricidade) e apoios de 2º gênero nos 4 cantos (translações presas, rotações livres).
    Retorna mapas de tags."""
    ops.wipe(); ops.model('basic', '-ndm', 3, '-ndf', 6)
    n = xyz.shape[0] - 1; E = Ecs_nbr(fck)
    tag = lambda i, j: i * (n + 1) + j + 1
    for i in range(n + 1):
        for j in range(n + 1):
            ops.node(tag(i, j), *map(float, xyz[i, j]))
    ops.section('ElasticMembranePlateSection', 1, E, nu, t, 0.0)
    cascas = {}; e = 1
    for i in range(n):
        for j in range(n):                       # anti-horário visto de cima -> normal para cima
            ops.element(elem, e, tag(i, j), tag(i + 1, j), tag(i + 1, j + 1), tag(i, j + 1), 1)
            cascas[e] = (i, j); e += 1
    b, h = viga; A = b * h; Iy = b * h ** 3 / 12; Iz = h * b ** 3 / 12
    J = b * h ** 3 * (1 / 3 - 0.21 * (h / b) * (1 - (h / b) ** 4 / 12)) if b >= h else h * b ** 3 * (1 / 3 - 0.21 * (b / h) * (1 - (b / h) ** 4 / 12))
    G = E / (2 * (1 + nu))
    ops.geomTransf('Linear', 1, 0.0, 0.0, 1.0)
    vigas = {}
    lados = [[(i, 0) for i in range(n + 1)], [(i, n) for i in range(n + 1)],
             [(0, j) for j in range(n + 1)], [(n, j) for j in range(n + 1)]]
    for lado in lados:
        for p, q in zip(lado[:-1], lado[1:]):
            ops.element('elasticBeamColumn', e, tag(*p), tag(*q), A, E, G, J, Iy, Iz, 1)
            vigas[e] = (p, q); e += 1
    cantos = [tag(0, 0), tag(n, 0), tag(0, n), tag(n, n)]
    for c in cantos:
        ops.fix(c, 1, 1, 1, 0, 0, 0)
    return dict(n=n, tag=tag, cascas=cascas, vigas=vigas, cantos=cantos, E=E, t=t, viga=viga, xyz=xyz)


def cargas(mod, q_planta, ts=1, gviga=0.0):
    """q_planta(x, y) -> kPa em projeção horizontal (negativo não; valor positivo = para baixo).
    Carga nodal por área de influência em planta (mesmo critério do FDM). gviga = peso da viga de borda (kN/m)."""
    n, tag, xyz = mod['n'], mod['tag'], mod['xyz']
    a = (xyz[n, 0, 0] - xyz[0, 0, 0]) / n        # espaçamento original em planta (cantos não se movem)
    ops.timeSeries('Linear', ts); ops.pattern('Plain', ts, ts)
    total = 0.0
    for i in range(n + 1):
        for j in range(n + 1):
            if tag(i, j) in mod['cantos']:
                continue
            f = (0.5 if i in (0, n) else 1.0) * (0.5 if j in (0, n) else 1.0)
            P = q_planta(*xyz[i, j, :2]) * a * a * f
            ops.load(tag(i, j), 0, 0, -P, 0, 0, 0); total += P
    if gviga:
        for e, (p, q) in mod['vigas'].items():
            Lb = np.linalg.norm(xyz[p] - xyz[q]); P = gviga * Lb / 2
            for nd in (tag(*p), tag(*q)):
                if nd not in mod['cantos']:
                    ops.load(nd, 0, 0, -P, 0, 0, 0)
                total += P                          # parcela no canto vai direto ao apoio (fora da soma das reações)
    return total


def analisar_linear():
    ops.constraints('Plain'); ops.numberer('RCM'); ops.system('UmfPack')
    ops.test('NormDispIncr', 1e-10, 10); ops.algorithm('Linear')
    ops.integrator('LoadControl', 1.0); ops.analysis('Static')
    ok = ops.analyze(1); ops.reactions()
    return ok == 0


# ----------------------------------------------------------------------------- 3. resultados
def esforcos(mod):
    """Por elemento de casca: média dos 4 pontos de Gauss de [N11 N22 N12 M11 M22 M12 Q13 Q23] (por metro).
    Principais de N e M, tensões nas faces (σ = N/t ± 6M/t², estádio I) e reações."""
    t = mod['t']; out = []
    for e, (i, j) in mod['cascas'].items():
        s = np.array(ops.eleResponse(e, 'stresses')).reshape(-1, 8).mean(axis=0)
        N = np.array([[s[0], s[2]], [s[2], s[1]]]); M = np.array([[s[3], s[5]], [s[5], s[4]]])
        nN = np.linalg.eigvalsh(N); nM = np.linalg.eigvalsh(M)
        sup = np.linalg.eigvalsh(N / t - 6 * M / t ** 2)    # face superior (convenção: M+ traciona a inferior)
        inf = np.linalg.eigvalsh(N / t + 6 * M / t ** 2)
        out.append(dict(e=e, i=i, j=j, N1=nN[1], N2=nN[0], M_abs=np.abs(nM).max(),
                        sig_min=min(sup[0], inf[0]), sig_max=max(sup[1], inf[1])))
    R = [ops.nodeReaction(c)[:3] for c in mod['cantos']]
    w = min(ops.nodeDisp(nd, 3) for nd in ops.getNodeTags())
    return out, R, w


def esforcos_vigas(mod):
    """N, My, Mz máximos nas vigas de borda (eixo local)."""
    Ns, Ms = [], []
    for e in mod['vigas']:
        f = ops.eleResponse(e, 'localForce')          # [N Vy Vz T My Mz]_i [..]_j
        Ns += [-f[0], f[6]]; Ms += [abs(f[4]), abs(f[5]), abs(f[10]), abs(f[11])]
    return min(Ns), max(Ns), max(Ms)


def estabilidade_nl(xyz, q_planta, gviga=0.0, no_ctrl=None, ds=0.6, passos=400, **kw_modelo):
    """Trajetória fator de carga × flecha até o solver perder o equilíbrio (casca perfeita, elástica, sem fissuras).
    Retorna (lam, w, lam_max). Usar só para comparar formas: o valor real cai com imperfeição, fluência e fissuração."""
    mod = modelo_casca(xyz, elem='ShellNLDKGQ', **kw_modelo); cargas(mod, q_planta, gviga=gviga)
    n = mod['n']; ctrl = no_ctrl or mod['tag'](3 * n // 4, n // 2)
    ops.constraints('Plain'); ops.numberer('RCM'); ops.system('UmfPack')
    ops.test('NormDispIncr', 1e-7, 50); ops.algorithm('Newton')
    ops.integrator('LoadControl', 1.0); ops.analysis('Static'); ops.analyze(1)
    lam, w = [1.0], [ops.nodeDisp(ctrl, 3)]
    ops.integrator('ArcLength', ds, 1.0)
    for _ in range(passos):
        if ops.analyze(1) != 0:
            ops.test('NormDispIncr', 1e-6, 200)
            if ops.analyze(1) != 0:
                break
        lam.append(ops.getLoadFactor(1)); w.append(ops.nodeDisp(ctrl, 3))
        if lam[-1] < 0.8 * max(lam):
            break
    lam = np.array(lam); return lam, np.array(w), float(lam.max())
```

## 9. Testes — `tests/test_formfinding.py`
```python
"""Testes do módulo formfinding (JAX FDM -> OpenSees). Rodar: pytest -q tests/test_formfinding.py"""
import numpy as np
import pytest
from nd_estruturas.formfinding import (forma_casca, forma_geometrica, modelo_casca, cargas,
                                       analisar_linear, esforcos)

N = 12   # malha leve para o teste


@pytest.fixture(scope="module")
def forma():
    return forma_casca(n=N)


def test_metas_de_altura(forma):
    xyz = forma["xyz"]; c = N // 2
    assert xyz[c, c, 2] == pytest.approx(4.0, abs=1e-4)
    assert xyz[c, 0, 2] == pytest.approx(2.5, abs=1e-4)


def test_so_compressao(forma):
    assert max(forma["forcas"].values()) < 0


def test_equilibrio_rede(forma):
    Rz = sum(-r[2] for r in forma["reacoes"])
    assert Rz == pytest.approx(3.5 * 20 * 20 * (1 - 4 * 0.25 / N**2), rel=1e-6)   # cantos sem carga


def test_casca_reproduz_empuxo_da_rede(forma):
    mod = modelo_casca(forma["xyz"]); P = cargas(mod, lambda x, y: 3.5); assert analisar_linear()
    out, R, w = esforcos(mod)
    assert sum(r[2] for r in R) == pytest.approx(P, rel=1e-6)
    H_rede = np.hypot(*forma["reacoes"][0][:2]); H_casca = np.hypot(*R[0][:2])
    assert H_casca == pytest.approx(H_rede, rel=0.05)
    assert max(o["N1"] for o in out) < 0.05 * abs(min(o["N2"] for o in out))   # quase sem tração de membrana


def test_funicular_flete_menos_que_geometrica(forma):
    Ms = []
    for X in (forma["xyz"], forma_geometrica(n=N)):
        mod = modelo_casca(X); cargas(mod, lambda x, y: 3.5); analisar_linear()
        Ms.append(max(o["M_abs"] for o in esforcos(mod)[0]))
    assert Ms[0] < 0.6 * Ms[1]
```