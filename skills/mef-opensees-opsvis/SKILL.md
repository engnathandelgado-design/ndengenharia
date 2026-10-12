---
name: "mef-opensees-opsvis"
description: "Use ao rodar análise estrutural por elementos finitos com OpenSeesPy + Opsvis (pórticos, vigas, P-Delta, seção de fibras/MRd, modal e transiente, juntas segmentais com zona coesiva e protensão externa, viga pré-tracionada com cordoalhas isoladas até a ruptura, tanques cilíndricos — parede em casca e laje circular) e gerar diagramas para memória de cálculo; complementa projetos-estruturais-concreto-armado-protendido."
---

# MEF com OpenSeesPy + Opsvis (pipeline ND Engenharia)

Complementa a skill `projetos-estruturais-concreto-armado-protendido` (Parte C, seção 21: teoria do MEF, `mef.py` próprio, testes de Gonçalves; seção 22: blocos; seção 23: fundamentos — forma fraca, convergência, Gauss/isoparamétrico, modal, Newmark — e `fem1d.py` para conferir o OpenSees; seção 24: juntas segmentais; seção 25: tanques; seção 10.12: Big Beam) e a `vigas-premoldadas-protendidas` (receita de peça de fábrica). **As convenções do software ND (unidades, sinal de N, JSON, dois motores) estão na Parte D da skill principal e valem aqui.** Aqui fica o **motor de análise de produção**: OpenSeesPy resolve, Opsvis desenha, `ops_nd.py` faz a ponte com as combinações NBR e o dimensionamento.

Postura: responder em português técnico; o MEF dá esforços — o dimensionamento continua pela NBR 6118/9062 (seções 8–12 e 15–16 da skill principal). Todo modelo novo passa pelos testes da seção 4 antes de virar número de projeto. A responsabilidade técnica (ART) é do Nathan: sinalizar hipóteses que pedem decisão dele (vínculos, rigidez de ligação, fator de rigidez da NBR 15.7.3, mola de solo).

## 1. Instalação
- `pip install openseespy opsvis` (testado: openseespy 3.8.0.0, opsvis 1.3.7, Python 3.13). No sandbox usar `--break-system-packages`.
- Opsvis: módulo de pré/pós-processamento de Seweryn Kokot (Univ. Tecnológica de Opole). Citação: *opsvis: Python module for pre-, post-processing and visualization for OpenSeesPy*, SoftwareX 34 (2026) 102615.
- Antes de usar num projeto, rodar `validar.py` (seção 4) e conferir os testes.

## 2. Quando usar OpenSeesPy em vez do `mef.py` próprio
| Caso | Ferramenta |
|---|---|
| Aula, auditoria transparente, pilar isolado NLF+NLG (Gonçalves) | `mef.py` (skill principal, 21.7) |
| Pórtico plano/espacial de projeto, várias combinações, envoltória | OpenSeesPy + `ops_nd.py` |
| P-Delta global, grandes rotações | `geomTransf('PDelta')` / `('Corotational')` |
| Seção qualquer, flexão composta/oblíqua, M-κ | `section Fiber` + `zeroLengthSection` |
| Pilar em balanço/flexão oblíqua com NLF | `forceBeamColumn` com seção de fibras + PDelta |
| Lajes/cascas | `ShellMITC4` / `ShellDKGQ` |
| Regiões D, blocos 3D não lineares | `quad`/`stdBrick` + `ASDConcrete3D` (validar contra Tabela 4 da seção 22) |
| Junta entre aduelas/segmentos pré-moldados (abertura, CZM), cabo externo com desviadores | `zeroLengthSection` com fibras ENT/Hysteretic + `Truss` com `InitStressMaterial` — `juntas_nd.py` (seção 12) |
| Modal / sísmica / dinâmica (ponte rolante, vibração de piso) | `-mass … -cMass` + `modal_nd` / `transiente_nd` (seção 11) + `opsv.plot_mode_shape` |
| Tanque cilíndrico: parede (casca axissimétrica), laje de fundo circular, junta parede-laje | `tanques_nd.parede_ops` (viga + molas E·t/a²) / `laje_circular_ops` (ShellMITC4 + ShellDKGT) — seção 13 |
| Viga pré-tracionada até a ruptura (fissuração, Pu, flecha), cordoalha aderente ou isolada, previsão de ensaio | `dispBeamColumn` + fibras `Concrete04` + `Truss` com `InitStressMaterial` presa por `rigidLink` — `viga_protendida_ops.py` (seção 14) |

## 3. Funções do Opsvis mais úteis
- `plot_model()` — geometria, numeração, apoios.
- `plot_defo(sfac)` — deformada interpolada (Hermite) com escala.
- `plot_loads_2d()` — cargas aplicadas (conferir sentido!).
- `plot_reactions()` — reações.
- `section_force_diagram_2d('N'|'T'|'M', sfac)` / `section_force_diagram_3d('N'|'Vy'|'Vz'|'T'|'My'|'Mz', sfac)` — diagramas de esforços (lê as `eleLoad` do domínio; 'T' = cortante em 2D).
- `plot_mode_shape(modo, sfac)`, `anim_defo`, `anim_mode` — modos e animações.
- `plot_fiber_section(fib_sec_list)` + `fib_sec_list_to_cmds(fib_sec_list)` — desenha a seção de fibras e cria os comandos OpenSees a partir da mesma lista (um só dado para modelo e figura). **A lista precisa de `['section','Fiber',tag,'-GJ',GJ]`** (sem `-GJ` dá IndexError na 1.3.7).
- `plot_stress_2d`, `plot_stress`, `sig_out_per_node` — tensões em `quad`/`tri31` (von Mises, principais) para regiões D.
- `plot_extruded_model_rect_section_3d` — vista 3D renderizada das barras.

## 4. Validação (rodada em 02/10/2026 — repetir após qualquer alteração)
E = 26,84 GPa; unidades kN, m.

| Teste | OpenSeesPy + ops_nd | Referência |
|---|---|---|
| T1 Viga biapoiada 20×50, L = 6 m, q = 20 kN/m: M / flecha / R | 90,000 kN·m / 6,0358 mm / 60 kN | qL²/8 = 90 / 5qL⁴/384EI = 6,0358 / qL/2 = 60 |
| T2 Pórtico biengastado (pilares 30×40, h = 6 m; viga 20×50, L = 10 m; q = 15 kN/m; H = 10 kN no topo) | M topo pilar esq. −77,428; M vão 97,715; M canto dir. −102,142; u topo 3,25 mm; ΣR ok | `mef.py` próprio: idênticos até 3 casas |
| T3 Balanço 30×30, L = 5 m, P = 0,5·Pcr + H: amplificação do topo | PDelta 1,982; Corotational 1,980 | 1/(1 − P/Pcr) ≈ 2,0 |
| T4 MRd seção 20×50, C30, As = 6,03 cm² (y = −20 cm), N = 0 | 108,07 kN·m (para em 10‰ no aço) | bloco retangular 108,54; `mef.py` MRd 108,03 |
| T5 MRd 20×50, C30, 2×4,02 cm² (±20 cm), N = 800 kN compressão | 179,8 kN·m (para em εcu) | `mef.py` MRd 178,3 (+0,8 %) |
| T6 Modal balanço L = 6 m, EI = 2,1e4, m = 0,5 t/m, 10 elementos: erro ω1/ω2/ω3 | `-cMass` +0,0001/+0,003/+0,025 %; lumped −0,46/−1,56/−2,55 % | 1,8751²·√(EI/m)/L² …; `fem1d` idêntico |
| T7 Transiente (liberação de deslocamento), Newmark γ = ½, β = ¼, Δt = T1/100, Rayleigh ζ = 5 % (modos 1–2) | T = 0,3155 s (eigen 0,3139; resolução Δt); ζ pelo decremento log = 0,0505 | ζ = 0,05 |

## 5. Convenções e armadilhas (aprendidas nos testes)
- **Sinais OpenSees:** `eleForce` = forças de extremidade em eixos **globais**; `eleResponse(e,'localForce')` = [Ni, Vi, Mi, Nj, Vj, Mj] em eixos locais, convenção de extremidade de barra (não de diagrama). `ops_nd.rodar` converte para diagrama: N tração +, M = (−Mi, Mj). Em pilar o sinal de M depende do sentido i→j: comparar **módulo** e conferir no desenho.
- **Seção de fibras:** OpenSees usa ε = ε0 − y·κ (κ > 0 comprime o topo, y para cima). Encurtamento no topo = κh/2 − ε0.
- `Concrete01` com (−0,85fcd, −2‰, −0,85fcd, −3,5‰) aproxima a parábola-retângulo (curva de Hognestad até εc2); diferença < 1 % no MRd. Para análise de esforços NLF usar 1,1·fcd (NBR 15.3.1) e para resistência 0,85·fcd — dois modelos de seção.
- Aço `Steel01` (fyd, Es = 210 GPa, b = 0) não desconta o concreto deslocado pela barra (diferença pequena; em pilar muito armado usar patch com furo ou descontar).
- Carga distribuída: `eleLoad -beamUniform wy` é no eixo **local** y; barra inclinada → decompor ou usar `wx`. O Opsvis só desenha a parábola certa se a carga estiver no domínio como `eleLoad`.
- Subdividir barras (≥ 4; pilar em 2ª ordem ≥ 10) — `ops_nd.subdividir`. Com subdivisão usar `end_max_values=False` nos diagramas para não poluir os rótulos.
- Materiais com o mesmo tag no mesmo domínio dão erro: `ops.wipe()` antes de criar outra seção.
- Unidades: kN, m, kPa em todo o modelo (E = 26,84e6 kPa). fck/fyk em MPa só na entrada das funções do `ops_nd`.
- `Ecs_nbr(fck, alpha_E)` segue NBR 6118 8.2.8 (fck ≤ 50 MPa).
- Rigidez para 2ª ordem global: usar `fator_I` na seção (0,4/0,5 vigas, 0,8 pilares, 0,3 lajes — NBR 15.7.3, conferir 2023).
- Massa: `elasticBeamColumn … '-mass', m` é **lumped só translacional** por padrão (erra −2,8/−8,8/−13,8 % nos 3 primeiros modos com 4 elementos); com `'-cMass'` fica consistente (Hermite, igual à skill principal 23.4). Massa em t (kN·s²/m) por m de barra — massa = (g + ψ2·q)/9,81 conforme o critério adotado.
- `ops.integrator('Newmark', gamma, beta)` — ordem γ, β (a apostila TM266 escreve (α, γ) = (γ, 2β)).
- **`patch('quad', …)`: vértices I-J-K-L em sentido anti-horário no plano (y, z).** Na ordem horária a área sai negativa sem aviso (EA e EI negativos: a protensão "empurra" e a contraflecha sai para baixo). Conferir com `ops.sectionStiffness` ou com a contraflecha elástica antes de seguir (seção 14).
- **`rigidLink` num nó que tem `fix`** (apoio) + `constraints('Transformation')` funciona no linear, mas no não linear gera rotação espúria no apoio e o Newton não converge. Usar `constraints('Penalty', 1e12, 1e12)` com `system('UmfPack')`.
- Sintoma desses dois erros: `forceBeamColumn` "could not invert flexibility" / Newton com norma parada. Corrigidos, `forceBeamColumn` (Lobatto 4) e `dispBeamColumn` (malha ≈ h/6, Gauss 2) dão o mesmo pico na viga da seção 14 (174,3 × 174,2 kN).

## 6. Formato de entrada (JSON) — padrão para a IA montar modelos
```json
{
  "modelo": {
    "nos": {"1": [0, 0], "2": [0, 6], "3": [10, 6], "4": [10, 0]},
    "apoios": {"1": [1, 1, 1], "4": [1, 1, 1]},
    "fck": 30,
    "secoes": {"P": {"b": 0.3, "h": 0.4, "fator_I": 0.8}, "V": {"b": 0.2, "h": 0.5, "fator_I": 0.4}},
    "barras": {"1": [1, 2, "P"], "2": [2, 3, "V"], "3": [4, 3, "P"]},
    "geomTransf": "PDelta"
  },
  "casos": {"G": {"q": {"2": -15}}, "Q": {"q": {"2": -5}}, "W": {"P": {"2": [10, 0, 0]}}},
  "combinacoes": {
    "ELU1": {"G": 1.4, "Q": 1.4, "W": 0.84},
    "ELU2": {"G": 1.4, "Q": 0.7, "W": 1.4},
    "ELU3": {"G": 1.0, "W": 1.4},
    "ELS_QP": {"G": 1.0, "Q": 0.4}
  }
}
```
ψ0/ψ1/ψ2 conforme NBR 8681 / NBR 6118 tab. 11.2 (conferir por tipo de uso). Incluir combinação com G favorável (γg = 1,0) quando vento/sucção puder inverter esforços (coberturas de barracão).

## 7. Roteiro de uso
1. Montar o JSON (geometria pelo eixo, vínculos reais, seções, casos, combinações).
2. `r = rodar(modelo, comb, casos, nsub=4)` → `checar_equilibrio(r, casos, comb)['ok']` deve ser True.
3. Conferir ordem de grandeza com conta manual (qL²/8, qL²/12, Euler).
4. `figuras('saida.png', titulo, sfac_defo, sM, sV)` → prancha modelo/deformada/M/V para a memória.
5. `env = envoltoria(modelo, combinacoes, casos)` → Md, Vd, Nd por barra com a combinação que governa.
6. Dimensionar: flexão/cisalhamento pela skill principal (seções 15–16); pilar → `MRd_fibras(b, h, camadas, fck, N=-Nd)` ≥ Md,tot; protensão → seções 8–12.
7. Memória: hipóteses, malha, combinações, tabela de validação, figuras, limitações.

## 8. Código — gravar como `ops_nd.py`
```python
"""ops_nd.py — camada ND Engenharia sobre OpenSeesPy + Opsvis.
Pórtico plano a partir de um dicionário/JSON -> combinações NBR 8681/6118 -> esforços, envoltórias e figuras.
Unidades: kN, m, kPa (kN/m²). fck/fyk em MPa (convertidos internamente).
"""
import json
import numpy as np
import openseespy.opensees as ops
import opsvis as opsv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def Ecs_nbr(fck, alpha_E=1.0):
    """Ecs (kPa) pela NBR 6118 8.2.8 (fck<=50 MPa). alpha_E: 1,2 basalto/diabásio; 1,0 granito/gnaisse; 0,9 calcário; 0,7 arenito."""
    Eci = alpha_E * 5600 * np.sqrt(fck)
    ai = min(0.8 + 0.2 * fck / 80, 1.0)
    return ai * Eci * 1e3


def build(model):
    """model = {'nos': {id: [x, y]}, 'apoios': {id: [ux, uy, rz]} (1 = fixo),
      'secoes': {nome: {'b','h'} ou {'A','I'}, 'fator_I' opcional}, 'E' (kPa) ou 'fck' (MPa),
      'barras': {id: [no_i, no_j, secao]}, 'geomTransf': 'Linear'|'PDelta'|'Corotational'}"""
    ops.wipe(); ops.model('basic', '-ndm', 2, '-ndf', 3)
    E = model.get('E') or Ecs_nbr(model['fck'], model.get('alpha_E', 1.0))
    for n, (x, y) in model['nos'].items():
        ops.node(int(n), float(x), float(y))
    for n, fx in model['apoios'].items():
        ops.fix(int(n), *fx)
    ops.geomTransf(model.get('geomTransf', 'Linear'), 1)
    for e, (i, j, s) in model['barras'].items():
        sec = model['secoes'][s]
        A = sec.get('A', sec.get('b', 0) * sec.get('h', 0)); I = sec.get('I', sec.get('b', 0) * sec.get('h', 0) ** 3 / 12)
        ops.element('elasticBeamColumn', int(e), int(i), int(j), A, E, I * sec.get('fator_I', 1.0), 1)
    return E


def subdividir(model, n=4):
    """Divide cada barra em n elementos (necessário em P-Delta local e para flechas)."""
    nos = {int(k): list(v) for k, v in model['nos'].items()}; barras = {}; prox_no = max(nos) + 1; prox_el = 1
    mapa = {}
    for e, (i, j, s) in model['barras'].items():
        xi, xj = np.array(nos[int(i)]), np.array(nos[int(j)]); ids = [int(i)]
        for k in range(1, n):
            nos[prox_no] = list(xi + (xj - xi) * k / n); ids.append(prox_no); prox_no += 1
        ids.append(int(j)); mapa[int(e)] = []
        for a, b in zip(ids[:-1], ids[1:]):
            barras[prox_el] = [a, b, s]; mapa[int(e)].append(prox_el); prox_el += 1
    m = dict(model); m['nos'] = nos; m['barras'] = barras; m['_mapa'] = mapa
    return m


def aplicar_caso(caso, fator=1.0, ts=1, mapa=None):
    """caso = {'q': {barra: q_local (kN/m, negativo = para baixo em barra horizontal)}, 'P': {no: [Fx, Fy, Mz]}}"""
    ops.timeSeries('Constant', ts); ops.pattern('Plain', ts, ts)
    for e, q in caso.get('q', {}).items():
        for el in (mapa[int(e)] if mapa else [int(e)]):
            ops.eleLoad('-ele', el, '-type', '-beamUniform', q * fator)
    for n, F in caso.get('P', {}).items():
        ops.load(int(n), *[f * fator for f in F])


def rodar(model, combinacao, casos, nsub=4, passos=1):
    """combinacao = {'G': 1.4, 'Q': 1.4, ...}; casos = {'G': caso, ...}.
    Retorna deslocamentos, reações e esforços por elemento (convenção de diagrama)."""
    m = subdividir(model, nsub) if nsub > 1 else dict(model, _mapa=None)
    build(m)
    for k, (nome, gamma) in enumerate(combinacao.items(), start=1):
        if gamma:
            aplicar_caso(casos[nome], gamma, k, m['_mapa'])
    ops.constraints('Transformation'); ops.numberer('RCM'); ops.system('BandGeneral')
    ops.test('NormDispIncr', 1e-8, 50); ops.algorithm('Newton')
    ops.integrator('LoadControl', 1.0 / passos); ops.analysis('Static')
    ok = ops.analyze(passos)
    ops.reactions()
    res = dict(ok=(ok == 0), modelo=m)
    res['desloc'] = {n: ops.nodeDisp(n) for n in ops.getNodeTags()}
    res['reacoes'] = {int(n): ops.nodeReaction(int(n)) for n in model['apoios']}
    res['esforcos'] = {}
    for e in ops.getEleTags():
        f = ops.eleResponse(e, 'localForce')          # [Ni,Vi,Mi,Nj,Vj,Mj] locais, convenção de extremidade
        res['esforcos'][e] = dict(N=(-f[0], f[3]), V=(f[1], -f[4]), M=(-f[2], f[5]))
    return res


def checar_equilibrio(res, casos, combinacao, tol=1e-3):
    """Soma das reações + soma das cargas = 0."""
    m = res['modelo']; Fx = Fy = 0.0
    for nome, g in combinacao.items():
        c = casos[nome]
        for n, F in c.get('P', {}).items():
            Fx += g * F[0]; Fy += g * F[1]
        for e, q in c.get('q', {}).items():
            for el in (m['_mapa'][int(e)] if m['_mapa'] else [int(e)]):
                i, j, _ = m['barras'][el]; xi, xj = np.array(m['nos'][i]), np.array(m['nos'][j])
                L = np.linalg.norm(xj - xi); cx, cy = (xj - xi) / L
                Fx += g * q * L * (-cy); Fy += g * q * L * cx
    Rx = sum(r[0] for r in res['reacoes'].values()); Ry = sum(r[1] for r in res['reacoes'].values())
    return dict(Rx=Rx, Ry=Ry, cargas_x=Fx, cargas_y=Fy,
                ok=abs(Rx + Fx) < tol * max(1, abs(Fx)) + tol and abs(Ry + Fy) < tol * max(1, abs(Fy)) + tol)


def envoltoria(model, combinacoes, casos, nsub=4):
    """Roda todas as combinações; devolve Mmax/Mmin, |V|max, Nmax/Nmin por barra original e a combinação que governa."""
    env = {}
    for nome, comb in combinacoes.items():
        r = rodar(model, comb, casos, nsub)
        for eo, els in (r['modelo']['_mapa'] or {int(e): [int(e)] for e in model['barras']}).items():
            Ms = [v for el in els for v in r['esforcos'][el]['M']]
            Vs = [v for el in els for v in r['esforcos'][el]['V']]
            Ns = [v for el in els for v in r['esforcos'][el]['N']]
            d = env.setdefault(eo, dict(Mmax=(-np.inf, None), Mmin=(np.inf, None), Vabs=(0, None), Nmax=(-np.inf, None), Nmin=(np.inf, None)))
            if max(Ms) > d['Mmax'][0]: d['Mmax'] = (max(Ms), nome)
            if min(Ms) < d['Mmin'][0]: d['Mmin'] = (min(Ms), nome)
            va = max(abs(v) for v in Vs)
            if va > d['Vabs'][0]: d['Vabs'] = (va, nome)
            if max(Ns) > d['Nmax'][0]: d['Nmax'] = (max(Ns), nome)
            if min(Ns) < d['Nmin'][0]: d['Nmin'] = (min(Ns), nome)
    return env


def figuras(arquivo, titulo='', sfac_defo=None, sM=None, sV=None):
    """Prancha 2x2 (modelo, deformada, M, V) da análise que está no domínio — chamar logo após rodar."""
    fig, ax = plt.subplots(2, 2, figsize=(12, 8.5))
    opsv.plot_model(ax=ax[0, 0], node_labels=0, element_labels=0); ax[0, 0].set_title('Modelo')
    opsv.plot_defo(sfac=sfac_defo or False, ax=ax[0, 1]); ax[0, 1].set_title('Deformada (ampliada)')
    for a, t, s, nome in ((ax[1, 0], 'M', sM, 'Momento fletor [kN·m]'), (ax[1, 1], 'T', sV, 'Cortante [kN]')):
        opsv.section_force_diagram_2d(t, s or 1.0, ax=a, number_format='.1f', end_max_values=False); a.set_title(nome)
    fig.suptitle(titulo); fig.tight_layout(); fig.savefig(arquivo, dpi=130); plt.close(fig)
    return arquivo


def secao_fibras_ret(tag, b, h, camadas, fck, fyk=500, gc=1.4, gs=1.15, psi=0.85, nfy=40):
    """b, h em m; camadas = [(As m², y m a partir do CG, + topo)]. Concrete01 (psi·fcd em 2‰ até 3,5‰); Steel01 fyd, Es 210 GPa.
    Retorna a lista fib_sec (serve para opsv.plot_fiber_section)."""
    fcd = fck / gc * 1e3; fyd = fyk / gs * 1e3
    ops.uniaxialMaterial('Concrete01', 1, -psi * fcd, -0.002, -psi * fcd, -0.0035)
    ops.uniaxialMaterial('Steel01', 2, fyd, 210e6, 0.0)
    fib = [['section', 'Fiber', tag, '-GJ', 1.0e6], ['patch', 'rect', 1, nfy, 1, -h / 2, -b / 2, h / 2, b / 2]]
    for As, y in camadas:
        fib.append(['layer', 'straight', 2, 1, As, y, 0.0, y, 0.0])
    opsv.fib_sec_list_to_cmds(fib)
    return fib


def MRd_fibras(b, h, camadas, fck, N=0.0, fyk=500, eps_s_lim=0.010, eps_c_lim=0.0035, npassos=400):
    """MRd por momento-curvatura (zeroLengthSection), parando em εcu (topo) ou 10‰ (aço). N em kN (compressão negativa).
    Retorna (MRd kN·m, curvatura, critério)."""
    ops.wipe(); ops.model('basic', '-ndm', 2, '-ndf', 3)
    secao_fibras_ret(1, b, h, camadas, fck, fyk)
    ops.node(1, 0, 0); ops.node(2, 0, 0); ops.fix(1, 1, 1, 1); ops.fix(2, 0, 1, 0)
    ops.element('zeroLengthSection', 1, 1, 2, 1)
    if N:
        ops.timeSeries('Constant', 1); ops.pattern('Plain', 1, 1); ops.load(2, N, 0, 0)
        ops.integrator('LoadControl', 0); ops.system('BandGeneral'); ops.numberer('Plain'); ops.constraints('Plain')
        ops.test('NormUnbalance', 1e-6, 50); ops.algorithm('Newton'); ops.analysis('Static'); ops.analyze(1)
        ops.loadConst('-time', 0.0); ops.wipeAnalysis()      # mantém N e libera a análise para a curvatura
    ops.timeSeries('Linear', 2); ops.pattern('Plain', 2, 2); ops.load(2, 0, 0, 1.0)
    ys = min(y for _, y in camadas); kmax = (eps_c_lim + eps_s_lim) / (h / 2 - ys)
    ops.integrator('DisplacementControl', 2, 3, kmax / npassos); ops.system('BandGeneral'); ops.numberer('Plain'); ops.constraints('Plain')
    ops.test('NormUnbalance', 1e-6, 50); ops.algorithm('Newton'); ops.analysis('Static')
    Mprev = 0.0; k = 0.0
    for _ in range(npassos):
        if ops.analyze(1) != 0:
            return Mprev, ops.nodeDisp(2, 3), 'não convergiu'
        k = ops.nodeDisp(2, 3); e0 = ops.nodeDisp(2, 1); M = ops.getLoadFactor(2)
        e_top = k * h / 2 - e0          # encurtamento no topo (+); OpenSees: ε = ε0 − y·κ
        e_s = e0 - k * ys               # alongamento na camada inferior (+)
        if e_top >= eps_c_lim or e_s >= eps_s_lim:
            return Mprev, k, ('εcu no concreto' if e_top >= eps_c_lim else '10‰ no aço')
        Mprev = M
    return Mprev, k, 'fim da varredura'


if __name__ == '__main__':
    import sys
    m = json.load(open(sys.argv[1]))
    env = envoltoria(m['modelo'], m['combinacoes'], m['casos'])
    for b, d in env.items():
        print(b, {k: (round(v[0], 2), v[1]) for k, v in d.items()})
```

## 9. Limitações (declarar na memória)
- `ops_nd` cobre pórtico plano com `elasticBeamColumn`; NLF de barra exige trocar por `forceBeamColumn` com seção de fibras (1,1·fcd para esforços).
- Sem rótulas internas nem molas de ligação ainda: usar `zeroLength` com material de rigidez Rsec (beam-line, skill principal 10.9) quando necessário.
- `checar_equilibrio` considera q perpendicular ao eixo local; cargas em projeção horizontal (telhado) devem ser convertidas antes.
- `MRd_fibras`: seção retangular, flexão reta; resolução da varredura ≈ 0,25 % (aumentar `npassos` perto do limite).
- Valores normativos a conferir na NBR 6118:2023 / NBR 8681 (ψ, γ, fator_I).
- `juntas_nd`: viga reta horizontal 2D, seção retangular na junta, cabo reto (traçado poligonal só via desviadores), sem esmagamento na junta, sem cabo aderente atravessando a junta (seção 12).
- `viga_protendida_ops`: viga reta biapoiada 2D, aderência perfeita no trecho aderente (sem comprimento de transferência lbpt nem escorregamento), sem confinamento da mesa nem fluência/retração; pós-pico dependente da malha (localização) — usar o pico e a flecha no pico (seção 14).
- `tanques_nd`: carga e geometria axissimétricas; parede e laje elásticas com rigidez bruta (sem fissuração); `junta_parede_laje` ignora a aba e a excentricidade da parede; laje sem solo (tanque cheio sobre o solo → molas da `interacao-solo-estrutura`); sem temperatura, retração restringida nem sismo (seção 13).

## 10. Alinhamento com o software ND (Parte D da skill principal)
- `ops_nd` já segue a convenção do software: kN·m, compressão negativa (`MRd_fibras(N=-800)`), esforços em convenção de diagrama na saída de `rodar`.
- Toda função nova vai para o módulo correspondente do pacote `nd_estruturas` (D.2) e ganha um teste em `tests/`.
- Correção 02/10/2026: `MRd_fibras` com N fazia o OpenSees avisar "can't set handler after analysis is created"; agora usa `loadConst` + `wipeAnalysis` entre a etapa de N e a de curvatura (resultado igual: 179,76 kN·m).

## 11. Modal e dinâmica (validado em 02/10/2026 — T6, T7)
Teoria e critérios na skill principal, seção 23 (23.4 autovalores, 23.5 Newmark/estabilidade). Regras práticas:
- **Massa consistente (`-cMass`)** para modal de barras. A massa lumped exige mais elementos (o erro é por baixo e cresce com o modo). Confiar só nos modos baixos de cada malha: refinar até o modo de interesse variar < 1 %.
- O `ops.eigen(n)` padrão funciona com a massa rotacional nula; `'-fullGenLapack'` só para extrair todos os modos (lento).
- **Newmark de aceleração média (γ = ½, β = ¼)** é incondicionalmente estável. Escolher Δt ≤ T/20 do maior modo de interesse (erro de período ≈ (ωΔt)²/12). Explícito (diferença central, `CentralDifference`) só para impacto, com Δt < 2/ωmax.
- **Rayleigh:** `rayleigh_coef(ωi, ωj, ζ)` → `ops.rayleigh(a0, 0, 0, a1)`. O termo de rigidez fica no `betaKcomm` para não gerar amortecimento espúrio quando a rigidez tangente cai (fissuração). Modos fora de [ωi, ωj] ficam mais amortecidos pela parcela de rigidez.
- Carga estática antes do transiente: `loadConst('-time', 0.0)` e depois `remove('loadPattern', …)` para liberar, ou manter para vibrar em torno da deformada.
- Conferir sempre o modal com `fem1d.modal` (skill principal 23.7) numa viga equivalente e com as fórmulas exatas de 23.4.
- Critérios normativos de vibração (NBR 6118 23.3: frequência própria acima da crítica, conferir valores na 2023) entram no módulo `dinamica` do software (D.2).

```python
"""Acrescentar ao ops_nd.py — modal e transiente (kN, m, t, s)."""
import numpy as np
import openseespy.opensees as ops


def rayleigh_coef(w_i, w_j, zeta_i=0.05, zeta_j=None):
    """a0 (massa) e a1 (rigidez) para ζ(ω) = a0/(2ω) + a1·ω/2 com ζ fixado nos modos i e j."""
    zeta_j = zeta_i if zeta_j is None else zeta_j
    A = np.array([[1/(2*w_i), w_i/2], [1/(2*w_j), w_j/2]])
    return np.linalg.solve(A, [zeta_i, zeta_j])


def modal_nd(nmodos=3, solver=None):
    """Modal do domínio atual (massas já definidas: '-mass' por elemento, com '-cMass' para consistente,
    ou ops.mass nos nós). Retorna ω (rad/s), T (s), f (Hz). Massa em t (kN·s²/m)."""
    lam = np.array(ops.eigen(solver, nmodos) if solver else ops.eigen(nmodos))
    w = np.sqrt(lam)
    return dict(omega=w, T=2*np.pi/w, f=w/(2*np.pi))


def transiente_nd(no, gdl, dt, npassos, zeta=None, modos=(1, 2), gamma=0.5, beta=0.25):
    """Integração Newmark (aceleração média por padrão) do domínio atual; cargas/condições iniciais já aplicadas.
    zeta: amortecimento de Rayleigh igual nos modos 'modos'. Retorna t, u(no, gdl)."""
    if zeta:
        w = np.sqrt(ops.eigen(max(modos)))
        a0, a1 = rayleigh_coef(w[modos[0]-1], w[modos[1]-1], zeta)
        ops.rayleigh(a0, 0.0, 0.0, a1)          # a1 na rigidez "committed": evita amortecimento espúrio pós-fissuração
    ops.wipeAnalysis()
    ops.constraints('Plain'); ops.numberer('RCM'); ops.system('BandGeneral')
    ops.test('NormDispIncr', 1e-10, 20); ops.algorithm('Newton')
    ops.integrator('Newmark', gamma, beta); ops.analysis('Transient')
    t, u = [], []
    for _ in range(npassos):
        if ops.analyze(1, dt) != 0:
            break
        t.append(ops.getTime()); u.append(ops.nodeDisp(no, gdl))
    return np.array(t), np.array(u)
```

## 12. Juntas segmentais e protensão externa (Spessatto 2022 — validado em 04/10/2026, T8–T10)
Teoria, critérios de projeto, receita ANSYS e resultados da Nova Ponte do Guaíba: skill principal, seção 24. Aqui fica a versão de barras (minutos em vez das 114 h do 3D sólido da tese).

**Modelo:** viga em `elasticBeamColumn`; em cada junta, dois nós coincidentes ligados por `zeroLengthSection` com seção de fibras cuja "deformação" é a **abertura** (Δu − y·Δθ, em m) — a lei de fibra é tensão × abertura, exatamente como o par CONTA174/TARGE170 com CZM. Cisalhamento da junta (chaves) por `section Aggregator` com mola 'Vy'. Cabo externo = `Truss` com `InitStressMaterial` (equivale ao INISTATE da tese: tensão já descontadas as perdas), ligado à viga por `rigidLink 'beam'` nas ancoragens e desviadores.
- Junta seca/projeto: `ENT` (só compressão). Junta concretada/colada (simulação): `Hysteretic` bilinear com σmax = fctm e δc (tese: 0,01 cm).
- Kn = rigidez de penalidade (kPa/m); 50·Ecs/h converge bem. O início da abertura não depende de Kn; a rotação após abrir depende (é física só se Kn representar a junta real).
- Etapas como a tese: (1) PP + protensão, (2) permanentes, (3) móveis — `analise_etapas` faz `loadConst` entre elas (= multiframe restart).
- Deslizamento no desviador: `deslizamento=True` usa um só elemento ancoragem-ancoragem (força uniforme).

| Teste (viga 0,50×1,00 m, L = 12 m biapoiada, 6 aduelas de 2 m, E = 30 GPa; cabo reto e = 0,35 m, Ap = 20 cm², σ0 = 1200 MPa, desviadores em 4 e 8 m) | MEF | Referência |
|---|---|---|
| T8 Momento de abertura da junta do meio, CZM σmax = 3,5 MPa (Kn = 50 e 500·E/h) | 1549,7 kN·m (P = 2408 kN) | M_ab = P·ep + (fctm + P/A)·I/yb = 1550,0 (−0,02 %) |
| T9 Junta seca (ENT), rotação Δθ após descomprimir, contato c = 0,58 / 0,18 m | +0,12 % / +1,25 % | Winkler parcial θ = 2P/(Kn·b·c²), c = 3(h/2 − eN) |
| T9 com c = 0,03–0,06 m (≈ 0,05h) | +12 a +93 % | fibras de 2 cm insuficientes; σc = 2P/(bc) > 300 MPa → esmaga antes (ENT é elástica) |
| T10 Cabo preso × deslizando, q total = 112 kN/m | forças 2272/2476/2454 × 2401 kN; flecha 14,57 × 14,72 mm | tese: deslizamento → força uniforme, flecha quase igual (11,25 × 11,35 cm) |

Regras aprendidas:
- Ler a abertura na fibra extrema com `abertura_junta(mod, x, y)`; comparar com δ1 = σmax/Kn para saber se a junta "abriu".
- Quando c < ~0,15h: refinar fibras (nfib ≥ 100) e trocar a compressão elástica por lei de concreto (esmagamento) — senão o resultado não vale.
- Perto da carga de colapso por abertura o Newton pode não convergir (T10 parou em 98 % da carga): reduzir passo ou usar `DisplacementControl`.
- Cabo **aderente** atravessando junta (REINF264 da tese): ligar o cabo à viga em todos os nós, deixando um comprimento livre lb de cada lado da junta (análogo à "malha de vazios"); o acréscimo de tensão concentra junto à junta. Ainda não implementado/validado.

```python
"""juntas_nd.py — juntas entre segmentos pré-moldados (aduelas, vigas segmentadas) e protensão externa em OpenSeesPy.
Baseado em Spessatto (2022, PPGEC/UFRGS): junta = interface de contato com zona coesiva bilinear (CZM, modo I),
abertura só pela interface, cabo externo ancorado nas extremidades e preso (ou não) nos desviadores.
Unidades: kN, m, kPa. Tração positiva. Abertura da junta positiva.
"""
import numpy as np
import openseespy.opensees as ops


def material_junta(tag, Kn, sig_max=0.0, delta_c=1e-4):
    """Lei tensão × abertura da junta (kPa × m).
    sig_max = 0  -> junta seca/sem armadura passante: ENT (só compressão, rigidez Kn).
    sig_max > 0  -> junta colada/concretada: CZM bilinear — elástica até sig_max (= fctm), amolece até 0 em delta_c.
    Kn = rigidez normal da interface (kPa/m) — penalidade: ~10–100·Ecs/h (não deve mudar o resultado; testar 2 valores).
    Obs.: o Hysteretic descarrega com a rigidez inicial (a CZM do ANSYS descarrega pela secante até a origem):
    exato para carga monotônica; para ciclos, aceitar como aproximação."""
    if sig_max <= 0:
        ops.uniaxialMaterial('ENT', tag, Kn)
        return
    e1 = sig_max / Kn
    assert delta_c > e1, 'delta_c deve ser maior que sig_max/Kn'
    big = 1e3 * sig_max
    ops.uniaxialMaterial('Hysteretic', tag, sig_max, e1, 1e-6 * sig_max, delta_c,
                         -big, -big / Kn, -2 * big, -2 * big / Kn, 1.0, 1.0, 0.0, 0.0, 0.0)


def secao_junta(tag, mat, b, h, nfib=50, Kv=None, mat_v=None):
    """Seção de fibras retangular da junta (2D) + rigidez ao cisalhamento (chaves de cisalhamento/atrito) via Aggregator.
    Tags usados: tag (Aggregator), tag+1000 (fibras), mat_v (material de cisalhamento)."""
    ops.section('Fiber', tag + 1000)
    ops.patch('rect', mat, nfib, 1, -h / 2, -b / 2, h / 2, b / 2)
    mat_v = mat_v or mat + 500
    ops.uniaxialMaterial('Elastic', mat_v, Kv if Kv else 1e3 * b * h * 1e6)
    ops.section('Aggregator', tag, mat_v, 'Vy', '-section', tag + 1000)


def viga_segmentada(L, b, h, juntas, E, nseg=4, Kn=None, sig_max=0.0, delta_c=1e-4,
                    cabo=None, apoios='biapoiada'):
    """Viga reta segmentada (eixo x, y para cima) com juntas zeroLengthSection.
    juntas  = lista de abscissas x das juntas; nseg = elementos por trecho entre juntas.
    cabo    = dict(e=excentricidade abaixo do CG (m), Ap (m²), Ep (kPa), sig0 (kPa, tensão após perdas),
                   desviadores=[x...], deslizamento=False) — cabo externo reto ancorado em x=0 e x=L.
    Retorna dict com tags úteis."""
    ops.wipe(); ops.model('basic', '-ndm', 2, '-ndf', 3)
    A, I = b * h, b * h ** 3 / 12
    Kn = Kn or 50 * E / h
    xs = [0.0] + sorted(juntas) + [L]
    ops.geomTransf('Linear', 1)
    no, el, lado_esq, lado_dir, eles_viga = 1, 1, {}, {}, []
    material_junta(10, Kn, sig_max, delta_c); secao_junta(20, 10, b, h)
    prev_end = None
    for k in range(len(xs) - 1):
        xa, xb = xs[k], xs[k + 1]
        ids = []
        for i in range(nseg + 1):
            ops.node(no, xa + (xb - xa) * i / nseg, 0.0); ids.append(no); no += 1
        for a, c in zip(ids[:-1], ids[1:]):
            ops.element('elasticBeamColumn', el, a, c, A, E, I, 1); eles_viga.append(el); el += 1
        if prev_end is not None:                       # junta entre prev_end (esq.) e ids[0] (dir.)
            ops.element('zeroLengthSection', el, prev_end, ids[0], 20)
            lado_esq[xa], lado_dir[xa] = prev_end, ids[0]; el += 1
        prev_end = ids[-1]
    n_ini, n_fim = 1, no - 1
    if apoios == 'biapoiada':
        ops.fix(n_ini, 1, 1, 0); ops.fix(n_fim, 0, 1, 0)
    else:                                              # 'engastada' (como no modelo da tese)
        ops.fix(n_ini, 1, 1, 1); ops.fix(n_fim, 1, 1, 1)
    out = dict(A=A, I=I, Kn=Kn, h=h, b=b, juntas=sorted(juntas), esq=lado_esq, dir=lado_dir,
               n_ini=n_ini, n_fim=n_fim, eles_viga=eles_viga, cabos=[])
    if cabo:
        out['cabos'] = cabo_externo(cabo, L, no, el, out)
    return out


def _no_mais_proximo(x):
    return min(ops.getNodeTags(), key=lambda n: abs(ops.nodeCoord(n)[0] - x) + 10 * abs(ops.nodeCoord(n)[1]))


def cabo_externo(cabo, L, no, el, mod):
    """Cabo reto à profundidade e: tirante(s) Truss com tensão inicial (InitStressMaterial, ~ INISTATE da tese),
    ligados à viga por rigidLink 'beam' nas ancoragens e, se deslizamento=False, também nos desviadores.
    deslizamento=True: um só elemento ancoragem-ancoragem (força uniforme no cabo)."""
    e, Ap, Ep, sig0 = cabo['e'], cabo['Ap'], cabo['Ep'], cabo['sig0']
    pts = [0.0, L] if cabo.get('deslizamento') else [0.0] + sorted(cabo.get('desviadores', [])) + [L]
    ops.uniaxialMaterial('Elastic', 900, Ep); ops.uniaxialMaterial('InitStressMaterial', 901, 900, sig0)
    tnos, teles = [], []
    for x in pts:
        nb = _no_mais_proximo(x)
        ops.node(no, ops.nodeCoord(nb)[0], -e); ops.rigidLink('beam', nb, no); tnos.append(no); no += 1
    for a, c in zip(tnos[:-1], tnos[1:]):
        ops.element('Truss', el, a, c, Ap, 901); teles.append(el); el += 1
    return teles


def forca_cabos(mod):
    return [ops.eleResponse(t, 'axialForce')[0] for t in mod['cabos']]


def abertura_junta(mod, x, y):
    """Abertura (m) da junta em x, na fibra y (a partir do CG): Δu − y·Δθ (positivo = abre)."""
    i, j = mod['esq'][x], mod['dir'][x]
    du = ops.nodeDisp(j, 1) - ops.nodeDisp(i, 1); dth = ops.nodeDisp(j, 3) - ops.nodeDisp(i, 3)
    return du - y * dth, dth


def analise_etapas(etapas, passos=(1, 20, 20), tol=1e-8):
    """Análise por etapas (como os load steps + multiframe restart da tese).
    etapas = [função que aplica as cargas da etapa (cria pattern)], cada etapa fica constante (loadConst) na seguinte.
    Retorna a lista de códigos ok por etapa."""
    oks = []
    for k, (aplicar, n) in enumerate(zip(etapas, passos), start=1):
        aplicar(k)
        ops.constraints('Transformation'); ops.numberer('RCM'); ops.system('BandGeneral')
        ops.test('NormDispIncr', tol, 100); ops.algorithm('Newton')
        ops.integrator('LoadControl', 1.0 / n); ops.analysis('Static')
        oks.append(ops.analyze(n) == 0)
        ops.loadConst('-time', 0.0); ops.wipeAnalysis()
    return oks


def carga_uniforme(mod, q):
    """Pattern com carga distribuída q (kN/m, negativo = para baixo) em todas as barras da viga."""
    def aplicar(k):
        ops.timeSeries('Linear', 100 + k); ops.pattern('Plain', 100 + k, 100 + k)
        for e in mod['eles_viga']:
            ops.eleLoad('-ele', e, '-type', '-beamUniform', q)
    return aplicar


def nbr7188_coef(Liv, n_faixas=2, concreto=True, perto_junta=True):
    """Coeficientes da carga móvel (NBR 7188:2013 — conferir revisão vigente): CIV, CNF, CIA e o produto φ.
    CIV = 1 + 1,06·20/(Liv + 50) para 10 ≤ Liv ≤ 200 m (senão 1,35, conforme a tese — conferir);
    CNF = 1 − 0,05(n − 2) ≥ 0,9 (só elementos longitudinais); CIA = 1,25 (concreto/misto) ou 1,15 (aço) até 5 m de juntas."""
    civ = 1 + 1.06 * 20 / (Liv + 50) if 10 <= Liv <= 200 else 1.35
    cnf = max(1 - 0.05 * (n_faixas - 2), 0.9)
    cia = (1.25 if concreto else 1.15) if perto_junta else 1.0
    return dict(CIV=civ, CNF=cnf, CIA=cia, phi=civ * cnf * cia)
```
Validação: reproduzir T8–T10 com os dados da tabela (viga 0,5×1,0, cabo, cargas g = 12,5 kN/m + q até 120 kN/m em 240 passos) — repetir após qualquer alteração.

## 13. Tanques cilíndricos — parede em casca, laje circular e flutuação (Koneski 2013 — validado em 07/10/2026, T11–T17)
Teoria, critérios, estudo de caso e roteiro: skill `tanques-reservatorios-concreto` e seção 25 da skill principal. Aqui fica o código `tanques_nd.py` e os testes.

**Modelos:**
- Parede axissimétrica = faixa meridional de 1 m como viga sobre base elástica (analogia exata da casca): `elasticBeamColumn` com E/(1 − ν²) e I = t³/12 (D da placa), molas `zeroLength` radiais com k = E·t/a² por m de altura (rigidez do anel), pressão nodal por área tributária; Nθ = E·t·w/a.
- Base: engaste, rótula, livre (junta deslizante) ou mola rotacional kθ (rigidez da laje D_l(1 + ν)/a, ou laje sobre solo).
- Laje circular: malha polar com `ShellDKGT` no anel central e `ShellMITC4` no resto, `ElasticMembranePlateSection`.
- Solução fechada de conferência: Timoshenko (= Rocha 1985) para a parede e Kirchhoff para a placa (classes `ParedeCilindrica` e `laje_circular`).

| Teste | `tanques_nd` (OpenSees) | Referência |
|---|---|---|
| T11 Parede engastada a = 11,65, t = 0,30, H = 7,75, d = 7,0 m, E = 26,07 GPa (βH = 5,4): M base / M− vão / Nθ,máx | 57,28 / −15,19 kN·m/m / 446,3 kN/m | Timoshenko 57,30 / −15,17 / 447,3; Rocha X2 = γL²(d − L)/2 = 57,30; X1 = 90,16 = Q base |
| T12 Mesma parede, base rotulada: M− vão / Nθ,máx | −23,26 / 552,2 | −23,24 / 552,9 |
| T13 Base livre (junta deslizante): Nθ,máx | 816,0 | γ·a·d = 815,5 |
| T14 Base com mola kθ = D_laje(1 + ν)/a (laje 1,2 m): M base | 47,29 | solução fechada com mola 47,30; Cross `junta_parede_laje` 47,30 |
| T15 Placa circular a = 5, h = 0,30, q = 10 kPa, E = 25 GPa, malha 16×48: engastada w0 / \|Mr,borda\| (reações); apoiada w0 | 1,693 mm (+1,6 %) / 31,19 (−0,2 %); 7,254 mm (+0,4 %) | qa⁴/64D = 1,667; qa²/8 = 31,25; 7,222 |
| T16 Laje do TCC (q = 50,5 kPa, l = 23,3 m, h = 1,2 m): Mr,borda / Mt,borda / Mcentro; As borda (d = 1,145 m, C30) | 856,75 / 171,35 / 514,05 kN·m/m; 24,73 cm²/m | TCC 856,75 / 171,35 / 514,08; 24,73 |
| T16 flecha imediata | 0,37 cm | TCC 3,7 cm — **erro de unidade de 10× no TCC** |
| T17 Flutuação, geometria original, critério do TCC (`area_total=False`): Gdst / G parede / G laje / G solo | 30 952,93 / 4 254,70 / 6 433,98 / 8 056,77 kN | idênticos ao TCC; corrigido (área total): Vdst = 38 346,5 kN, FS = 0,44 |

Regras aprendidas:
- A analogia viga-Winkler reproduz a casca a < 0,2 % com 400 elementos. Usar ≥ 10 elementos por comprimento L = 1/β ≈ 0,76√(a·t).
- Momento de borda da placa pelas reações: sai com o sinal das reações (comparar o módulo); a flecha MITC4 converge por cima com a malha polar usada (+1,6 % em 16 anéis).
- Sinal: em `parede_ops` (Y radial para fora) a convenção de diagrama (−Mi, Mj) já dá + = tração na face interna — não inverter.
- `junta_parede_laje`: S_parede = 2Dβ, S_laje = D(1 + ν)/a. No caso do TCC, S_laje/S_parede ≈ 4,7 → a borda "engastada" de 857 kN·m/m cai para ≈ 220 e o centro sobe para ≈ 1 150 kN·m/m (sem aba). Confirmar com modelo acoplado quando a decisão depender disso.
- Pendente (não validado): modelo 3D em casca do cilindro + laje para cargas não axissimétricas (passarela, casa de bombas, sismo); laje sobre solo (Winkler) e estacas de tração; temperatura/retração restringida.

```python
"""tanques_nd.py — tanques/reservatórios cilíndricos de concreto armado (apoiados, semi-enterrados, enterrados).
Base: Koneski (2013, TCC UDESC) — laje de fundo de tanque enterrado e flutuação; Rocha (1985); Timoshenko &
Woinowsky-Krieger (cascas cilíndricas e placas circulares); EC7 (UPL). Unidades: kN, m, kPa. Ângulos em graus.
Convenção de momentos na junta parede-laje: positivo = tração na face interna (molhada).
"""
import numpy as np
from math import pi, sqrt, sin, radians, tan
from scipy.optimize import brentq

GAMMA_W = 10.0      # kN/m³
GAMMA_C = 25.0


def Ecs_nbr(fck, alpha_E=1.0):
    """Ecs (kPa), NBR 6118:2023 8.2.8 (fck ≤ 50 MPa)."""
    Eci = alpha_E * 5600 * sqrt(fck)
    return min(0.8 + 0.2 * fck / 80, 1.0) * Eci * 1e3


# ------------------------------------------------------------------ ações
def subpressao(hw, gw=GAMMA_W):
    """Pressão de baixo para cima na face inferior da laje (kPa); hw = NA até a face inferior (m)."""
    return gw * max(hw, 0.0)


def K0(phi_deg, OCR=1.0):
    """Repouso (Jaky), NC: 1 − sen φ'; PA: ×OCR^sen φ' (Mayne-Kulhawy)."""
    s = sin(radians(phi_deg))
    return (1 - s) * OCR ** s


def pressao_lateral_solo(z, gamma, phi_deg, z_NA=None, gamma_sat=None, q=0.0, gw=GAMMA_W, OCR=1.0):
    """σh total (kPa) na profundidade z (m) a partir do terreno: K0·σ'v + u. Parede rígida → repouso
    (deslocamento < 5e-4·h, EC7 9.5.2), nunca ativo. q = sobrecarga no terreno."""
    k = K0(phi_deg, OCR)
    if z_NA is None or z <= z_NA:
        return k * (gamma * z + q)
    gs = gamma_sat or gamma
    sv_ef = gamma * z_NA + (gs - gw) * (z - z_NA) + q
    return k * sv_ef + gw * (z - z_NA)


# ------------------------------------------------------------------ flutuação (UPL)
def flutuacao(R_int, e_par, H_par, h_laje, aba, z_base, z_NA=0.0, gamma_solo=18.0, gc=GAMMA_C,
              G_extra=0.0, Q_dst=0.0, R_atrito=0.0, g_dst=1.0, g_stb=0.9, g_Qdst=1.5, area_total=True):
    """Estabilidade contra flutuação com o tanque VAZIO (etapa crítica).
    R_int: raio interno; e_par: espessura da parede; H_par: altura da parede acima da laje; h_laje: espessura
    da laje de fundo; aba: balanço da laje além da face externa da parede; z_base: profundidade da face
    INFERIOR da laje a partir do terreno; z_NA: profundidade do NA (0 = no terreno, recomendado).
    gamma_solo: peso do solo sobre a aba — se a subpressão atua na área total da base (correto), usar o peso
    SATURADO abaixo do NA. R_atrito: atrito lateral (desprezar a favor da segurança, como no TCC).
    Coeficientes EC7 tabela A.15 (UPL): γG,dst 1,0; γG,stb 0,9; γQ,dst 1,5 (conferir NBR 6122/8681).
    area_total=False reproduz o TCC (subpressão só na área interna — contra a segurança)."""
    R_ext = R_int + e_par
    R_b = R_ext + aba
    hw = z_base - z_NA
    A = pi * (R_b ** 2 if area_total else R_int ** 2)
    V_dst = g_dst * GAMMA_W * hw * A + g_Qdst * Q_dst
    G_par = gc * pi * (R_ext ** 2 - R_int ** 2) * H_par
    G_laje = gc * pi * R_b ** 2 * h_laje
    h_solo = z_base - h_laje                       # solo sobre a aba (do topo da laje ao terreno)
    G_solo = gamma_solo * pi * (R_b ** 2 - R_ext ** 2) * h_solo
    G_stb = g_stb * (G_par + G_laje + G_solo + G_extra) + R_atrito
    return dict(V_dst=V_dst, G_par=G_par, G_laje=G_laje, G_solo=G_solo, G_stb=G_stb,
                FS=G_stb / V_dst, ok=G_stb >= V_dst, deficit=max(V_dst - G_stb, 0.0), hw=hw, R_base=R_b)


def aba_necessaria(R_int, e_par, H_par, h_laje, z_base, **kw):
    """Balanço mínimo da aba (m) para Gstb,d = Vdst,d. Com area_total=True a aba só ajuda se
    (γsolo·h_solo + γc·h_laje)·0,9 > γw·hw por m² — senão não existe solução (retorna None)."""
    f = lambda b: flutuacao(R_int, e_par, H_par, h_laje, b, z_base, **kw)['G_stb'] - \
        flutuacao(R_int, e_par, H_par, h_laje, b, z_base, **kw)['V_dst']
    if f(0.0) >= 0:
        return 0.0
    if f(50.0) < 0:
        return None
    return brentq(f, 0.0, 50.0)


# ------------------------------------------------------------------ parede cilíndrica (casca longa)
class ParedeCilindrica:
    """Casca cilíndrica de espessura t, raio médio a, lâmina d'água d (pressão γ(d − x), x a partir da base).
    base: 'engaste' (w = w' = 0), 'rotula' (w = 0, M = 0), 'livre' (junta deslizante: só membrana),
    'mola' (w = 0, M = kθ·w'; kθ em kN·m/rad por m de perímetro).
    Solução de borda de Timoshenko (casca longa: βH ≳ 3). Para parede curta, carga qualquer ou junta elástica
    real usar parede_ops (viga sobre base elástica no OpenSees)."""

    def __init__(self, a, t, d, E, nu=0.2, gamma=GAMMA_W, base='engaste', k_theta=None, p0=0.0):
        self.a, self.t, self.d, self.E, self.nu, self.g = a, t, d, E, nu, gamma
        self.p0 = p0                                    # pressão uniforme adicional (kPa), ex.: gás/empuxo médio
        self.D = E * t ** 3 / (12 * (1 - nu ** 2))
        self.beta = (3 * (1 - nu ** 2) / (a * t) ** 2) ** 0.25
        c = a ** 2 / (E * t)
        w0, dw0 = c * (gamma * d + p0), -c * gamma      # membrana na base: w, dw/dx
        b = self.beta
        if base == 'livre':
            C1 = C2 = 0.0
        elif base == 'rotula':
            C1, C2 = -w0, 0.0
        elif base == 'engaste':
            C1 = -w0; C2 = C1 - dw0 / b
        elif base == 'mola':
            C1 = -w0
            # M(0) = −2Dβ²C2 (tração interna) = kθ·w'(0), w'(0) = dw0 + β(C2 − C1)
            C2 = -k_theta * (dw0 - b * C1) / (2 * self.D * b ** 2 + k_theta * b)
        self.C1, self.C2, self.base = C1, C2, base
        self.c = c

    def w(self, x):
        b = self.beta; x = np.asarray(x, float)
        return self.c * (self.g * np.clip(self.d - x, 0, None) + self.p0) + \
            np.exp(-b * x) * (self.C1 * np.cos(b * x) + self.C2 * np.sin(b * x))

    def Mx(self, x):
        """Momento meridional (kN·m/m); + = tração na face interna (M = D·w'', w + para fora)."""
        b = self.beta; x = np.asarray(x, float)
        return 2 * self.D * b ** 2 * np.exp(-b * x) * (self.C1 * np.sin(b * x) - self.C2 * np.cos(b * x))

    def Qx(self, x):
        """Cortante meridional (kN/m) = dM/dx."""
        b = self.beta; x = np.asarray(x, float)
        return 2 * self.D * b ** 3 * np.exp(-b * x) * ((self.C1 + self.C2) * np.cos(b * x) + (self.C2 - self.C1) * np.sin(b * x))

    def Ntheta(self, x):
        """Tração anelar (kN/m)."""
        return self.E * self.t * self.w(x) / self.a

    def Mtheta(self, x):
        return self.nu * self.Mx(x)

    def resumo(self, H=None, n=2001):
        H = H or self.d
        x = np.linspace(0, H, n); M = self.Mx(x); N = self.Ntheta(x)
        i, j = np.argmin(M), np.argmax(N)
        return dict(beta=self.beta, betaH=self.beta * H, M_base=float(self.Mx(0.0)), M_min=float(M[i]),
                    x_Mmin=float(x[i]), N_max=float(N[j]), x_Nmax=float(x[j]), Q_base=float(self.Qx(0.0)),
                    S_rot=2 * self.D * self.beta, aviso=None if self.beta * H >= 3 else 'βH < 3: usar parede_ops')


# ------------------------------------------------------------------ laje circular (placa de Kirchhoff)
def laje_circular(q, a, E, h, nu=0.2, borda='engastada', n=201):
    """Placa circular de raio a com carga uniforme q (kPa). q > 0 para baixo → M > 0 traciona a face inferior.
    Subpressão líquida (para cima) → q < 0. Retorna Mr(r), Mt(r), w0, V na borda e rigidez de borda S_rot.
    Engastada: Mr = q/16[a²(1+ν) − r²(3+ν)], Mt = q/16[a²(1+ν) − r²(1+3ν)], w0 = q a⁴/(64D).
    Apoiada:  Mr = q(3+ν)(a² − r²)/16, Mt = q/16[a²(3+ν) − r²(1+3ν)], w0 = q a⁴(5+ν)/(64D(1+ν))."""
    D = E * h ** 3 / (12 * (1 - nu ** 2))
    r = np.linspace(0, a, n)
    if borda == 'engastada':
        Mr = q / 16 * (a ** 2 * (1 + nu) - r ** 2 * (3 + nu)); Mt = q / 16 * (a ** 2 * (1 + nu) - r ** 2 * (1 + 3 * nu))
        w0 = q * a ** 4 / (64 * D)
    else:
        Mr = q * (3 + nu) * (a ** 2 - r ** 2) / 16; Mt = q / 16 * (a ** 2 * (3 + nu) - r ** 2 * (1 + 3 * nu))
        w0 = q * a ** 4 * (5 + nu) / (64 * D * (1 + nu))
    return dict(r=r, Mr=Mr, Mt=Mt, w0=w0, D=D, M_centro=float(Mr[0]), Mr_borda=float(Mr[-1]),
                Mt_borda=float(Mt[-1]), V_borda=q * a / 2, S_rot=D * (1 + nu) / a)


def momento_malha_ortogonal(Mr, Mt):
    """Malha x-y sob momentos principais Mr, Mt com direção qualquer (Wood-Armer): mx* = my* = max(|Mr|,|Mt|)
    quando têm o mesmo sinal (no centro Mr = Mt → isótropo, sem fator). O fator √2 de Cruz (2009)/TCC
    é conservador. Sinais opostos: armar as duas faces com |M| de cada sinal."""
    if Mr * Mt >= 0:
        return max(abs(Mr), abs(Mt))
    return dict(positivo=max(Mr, Mt), negativo=min(Mr, Mt))


def junta_parede_laje(FEM_par, S_par, FEM_laje, S_laje):
    """Compatibilização da rotação na junta monolítica (Cross de um nó, sem momento externo).
    FEM: momentos de engaste perfeito, + = tração na face interna. S: rigidez à rotação (kN·m/rad/m):
    parede longa S = 2Dβ (w = 0 na base); laje circular S = D(1+ν)/a. Retorna o momento final na junta."""
    return (S_laje * FEM_par + S_par * FEM_laje) / (S_par + S_laje)


# ------------------------------------------------------------------ dimensionamento (NBR 6118:2023)
def As_flexao(Md, d, fck, b=1.0, fyk=500):
    """Md kN·m/m, d m → As cm²/m e x/d (bloco retangular, ≤ C50)."""
    fcd = fck / 1.4 * 1e3; fyd = fyk / 1.15 * 1e3
    disc = 1 - Md / (0.425 * b * d ** 2 * fcd)
    if disc < 0:
        return dict(As=None, xd=None, msg='seção insuficiente')
    x = 1.25 * d * (1 - sqrt(disc))
    return dict(As=Md / (fyd * (d - 0.4 * x)) * 1e4, xd=x / d)


def As_anel(Nd, fyk=500, Nk=None, sigma_s_serv=None):
    """Tração anelar: As = Nd/fyd (cm²/m, total nas duas faces). sigma_s_serv (MPa) opcional limita a tensão
    em serviço para controle de fissuras (prática p/ estanqueidade 100–160 MPa — conferir critério adotado)."""
    As = Nd / (fyk / 1.15 * 1e3) * 1e4
    if Nk is not None and sigma_s_serv:
        As = max(As, Nk / (sigma_s_serv * 1e3) * 1e4)
    return As


def sigma_ct_anel(Nk, t, As_cm2, fck, Es=210e6, E=None):
    """Tensão de tração no concreto do anel no estádio I (kPa): Nk/(Ac + (αe − 1)As) — comparar com fctk,inf
    para anel sem fissura (critério de estanqueidade 'não fissurado')."""
    E = E or Ecs_nbr(fck)
    ae = Es / E
    return Nk / (t + (ae - 1) * As_cm2 * 1e-4)


def VRd1_laje(d, fck, As_cm2, b=1.0, sigma_cp=0.0):
    """NBR 6118 19.4.1 (laje sem armadura transversal), kN/m. k = |1,6 − d| ≥ 1 (d em m)."""
    fctd = 0.7 * 0.3 * fck ** (2 / 3) / 1.4 * 1e3
    tRd = 0.25 * fctd
    rho1 = min(As_cm2 * 1e-4 / (b * d), 0.02)
    k = max(abs(1.6 - d), 1.0)
    return (tRd * k * (1.2 + 40 * rho1) + 0.15 * sigma_cp) * b * d


# ------------------------------------------------------------------ MEF (OpenSeesPy) — ponte com ops_nd
def parede_ops(a, t, H, d, E, nu=0.2, gamma=GAMMA_W, base='engaste', k_theta=None, nel=200,
               p_ext=None, p0=0.0):
    """Faixa meridional de 1 m da parede como viga sobre base elástica (analogia exata da casca axissimétrica):
    EI = D = Et³/12(1−ν²) e molas radiais k = E·t/a² (kPa/m) — rigidez do anel. Serve para parede curta (βH < 3),
    espessura variável (trocar t por trecho), pressão de solo externa p_ext(x) (kPa, + para dentro) e base
    elástica (k_theta = rigidez da laje D_l(1+ν)/a ou de laje sobre solo). Retorna x, w, M (+ tração interna), Nθ."""
    import openseespy.opensees as ops
    ops.wipe(); ops.model('basic', '-ndm', 2, '-ndf', 3)
    D = E * t ** 3 / (12 * (1 - nu ** 2)); k = E * t / a ** 2
    xs = np.linspace(0, H, nel + 1); h = H / nel
    for i, x in enumerate(xs):                        # eixo local: X = altura, Y = radial (+ para fora)
        ops.node(i + 1, x, 0.0)
        ops.node(10000 + i + 1, x, 0.0); ops.fix(10000 + i + 1, 1, 1, 1)
    ops.uniaxialMaterial('Elastic', 1, 1.0)
    ops.geomTransf('Linear', 1)
    for i in range(nel):
        ops.element('elasticBeamColumn', i + 1, i + 1, i + 2, t, E / (1 - nu ** 2), t ** 3 / 12, 1)
    for i, x in enumerate(xs):
        trib = h if 0 < i < nel else h / 2
        ops.uniaxialMaterial('Elastic', 100 + i, k * trib)
        ops.element('zeroLength', 5000 + i, 10000 + i + 1, i + 1, '-mat', 100 + i, '-dir', 2)
    ops.fix(1, 1, 0, 0)                               # axial
    if base in ('engaste', 'rotula', 'mola'):
        ops.fix(1, 0, 1, 1 if base == 'engaste' else 0)
    if base == 'mola':
        ops.node(20000, 0.0, 0.0); ops.fix(20000, 1, 1, 1)
        ops.uniaxialMaterial('Elastic', 99, k_theta)
        ops.element('zeroLength', 9999, 20000, 1, '-mat', 99, '-dir', 3)
    ops.timeSeries('Linear', 1); ops.pattern('Plain', 1, 1)
    for i, x in enumerate(xs):
        trib = h if 0 < i < nel else h / 2
        p = gamma * max(d - x, 0.0) + p0 - (p_ext(x) if p_ext else 0.0)
        ops.load(i + 1, 0.0, p * trib, 0.0)
    ops.constraints('Transformation'); ops.numberer('RCM'); ops.system('BandGeneral')
    ops.test('NormDispIncr', 1e-10, 10); ops.algorithm('Linear'); ops.integrator('LoadControl', 1.0)
    ops.analysis('Static'); ops.analyze(1)
    w = np.array([ops.nodeDisp(i + 1, 2) for i in range(nel + 1)])
    M = np.zeros(nel + 1)
    for e in range(nel):
        f = ops.eleResponse(e + 1, 'localForce')       # [N,V,M]i,[N,V,M]j
        M[e] = -f[2]; M[e + 1] = f[5]
    # convenção de diagrama do ops_nd (−Mi, Mj) com Y radial para fora já resulta em + = tração interna
    return dict(x=xs, w=w, M=M, Ntheta=E * t * w / a)


def laje_circular_ops(q, a, h, E, nu=0.2, nr=12, ns=32, borda='engastada'):
    """Laje circular em ShellMITC4/ShellDKGT (malha polar). Valida a teoria de placas e permite carga/apoio
    quaisquer (furos, poço, pilares, molas de solo por nó → skill interacao-solo-estrutura).
    Retorna flecha central e o momento radial médio na borda pelas reações (ΣM_reação / 2πa)."""
    import openseespy.opensees as ops
    ops.wipe(); ops.model('basic', '-ndm', 3, '-ndf', 6)
    ops.section('ElasticMembranePlateSection', 1, E, nu, h, 0.0)
    ops.node(1, 0, 0, 0); tag = 2; ring = {0: [1] * ns}
    for i in range(1, nr + 1):
        r = a * i / nr; ring[i] = []
        for j in range(ns):
            th = 2 * pi * j / ns
            ops.node(tag, r * np.cos(th), r * np.sin(th), 0.0); ring[i].append(tag); tag += 1
    e = 1
    for j in range(ns):
        ops.element('ShellDKGT', e, 1, ring[1][j], ring[1][(j + 1) % ns], 1); e += 1
    for i in range(1, nr):
        for j in range(ns):
            jj = (j + 1) % ns
            ops.element('ShellMITC4', e, ring[i][j], ring[i + 1][j], ring[i + 1][jj], ring[i][jj], 1); e += 1
    for n in ring[nr]:
        ops.fix(n, 1, 1, 1, *( (1, 1, 1) if borda == 'engastada' else (0, 0, 1) ))
    # carga consistente simples: área tributária polar por nó
    ops.timeSeries('Linear', 1); ops.pattern('Plain', 1, 1)
    dr = a / nr
    ops.load(1, 0, 0, -q * pi * (dr / 2) ** 2, 0, 0, 0)
    for i in range(1, nr + 1):
        r = a * i / nr
        r1, r2 = r - dr / 2, min(r + dr / 2, a)
        A = pi * (r2 ** 2 - r1 ** 2) / ns
        for n in ring[i]:
            ops.load(n, 0, 0, -q * A, 0, 0, 0)
    ops.constraints('Plain'); ops.numberer('RCM'); ops.system('UmfPack')
    ops.test('NormDispIncr', 1e-10, 10); ops.algorithm('Linear'); ops.integrator('LoadControl', 1.0)
    ops.analysis('Static'); ops.analyze(1); ops.reactions()
    w0 = -ops.nodeDisp(1, 3)
    Mr = 0.0
    for n in ring[nr]:                                 # momento em torno da tangente = componente radial-perp
        x, y, _ = ops.nodeCoord(n); R = ops.nodeReaction(n)
        tx, ty = -y / a, x / a
        Mr += R[3] * tx + R[4] * ty
    return dict(w0=w0, Mr_borda=Mr / (2 * pi * a))
```

Validação (gravar como `validar_tanques.py` e rodar após qualquer alteração — saída deve reproduzir T11–T17):
```python
from tanques_nd import *
E = 26.0715e6   # TCC: 0,85·5600√30 MPa → kPa
print(flutuacao(11.5, 0.3, 7.75, 0.5, 1.0, 7.45, gamma_solo=15, area_total=False))      # T17 (TCC)
print(flutuacao(11.5, 0.3, 7.75, 0.5, 1.0, 7.45, gamma_solo=15)['FS'])                  # 0,44
print(aba_necessaria(11.5, 0.3, 7.75, 1.2, 8.15, gamma_solo=15))                          # 5,56 m
L = laje_circular(50.5, 23.3/2, E, 1.2); print(L['Mr_borda'], L['Mt_borda'], L['M_centro'], L['w0'])   # T16
print(As_flexao(1.4*856.75, 1.145, 30), VRd1_laje(1.145, 30, 24.73))                    # 24,73 cm²/m; 533 kN/m
for b in ('engastada', 'apoiada'):                                                        # T15
    print(b, laje_circular(10, 5, 25e6, 0.3, borda=b)['w0'], laje_circular_ops(10, 5, 0.3, 25e6, nr=16, ns=48, borda=b))
for base in ('engaste', 'rotula', 'livre'):                                               # T11–T13
    s = ParedeCilindrica(11.65, 0.3, 7.0, E, base=base).resumo(7.75); o = parede_ops(11.65, 0.3, 7.75, 7.0, E, base=base, nel=400)
    print(base, s['M_base'], o['M'][0], s['M_min'], o['M'].min(), s['N_max'], o['Ntheta'].max())
Sl = laje_circular(1, 11.65, E, 1.2)['S_rot']                                            # T14
print(ParedeCilindrica(11.65, 0.3, 7.0, E, base='mola', k_theta=Sl).Mx(0.0),
      parede_ops(11.65, 0.3, 7.75, 7.0, E, base='mola', k_theta=Sl, nel=400)['M'][0])
```

## 14. Viga pré-tracionada com cordoalhas isoladas — ensaio até a ruptura (PCI Big Beam 2015 — validado em 07/10/2026, T18–T21)
Dados da peça, cálculo manual (`viga_ensaio_nd.py`) e detalhamento: skill `vigas-premoldadas-protendidas`; resumo e lições de projeto: skill principal 10.12.

**Modelo:**
- Viga em `dispBeamColumn` (Gauss 2 pontos, elementos de 3" = 76 mm, nós em apoios, cargas e limites do isolamento) com seção I de fibras: `Concrete04` (Popovics, f'c = 63,4 MPa, εc = 3‰, εcu = 3,5‰, Ec = 25 GPa estimado pelo ACI para concreto leve de 17,2 kN/m³, fct = MOR = 6,8 MPa) + 2 barras superiores (Steel01).
- Cordoalha = `Truss` com `InitStressMaterial` sobre `ElasticMultiLinear` (elástica até 0,8 fpu, depois curva de potência do PCI), em nós próprios a yp = 127 mm da base, ligados à viga por `rigidLink 'beam'` **só no trecho aderente**. No trecho isolado, um único `Truss` entre os dois últimos nós aderentes: deformação uniforme, como a bainha.
- σ0 de pista iterado até a tensão efetiva após encurtamento elástico + peso próprio ser a desejada (1178 → 1281 MPa).
- Etapa 1: protensão + peso próprio (`loadConst`). Etapa 2: duas cargas iguais por `DisplacementControl` no meio do vão (KrylovNewton, Newton inicial de reserva), até a carga cair a 75 % do pico.
- Fissuração: P em que a fibra inferior do meio do vão passa de fct/Ec.

| Teste | MEF | Referência |
|---|---|---|
| T18 Contraflecha elástica / perda por encurtamento elástico | 5,45 mm / 103 MPa | Pe·e·L²/8EI − 5gL⁴/384EI ≈ 5,4 mm / αp·σcp = 106 MPa |
| T19 Pcr (fissuração) | 123,3 kN | ensaio 115,6 (+6,7 %); mão 117,9 |
| T19 Pu / flecha no pico / σps no pico | 174,2 kN / 54,3 mm / 1630 MPa | ensaio 181,5 kN (−4,0 %) / 57 mm (−5 %); retroanálise ≈ 1730 MPa; mecanismo de mão 162 mm |
| T20 Malha 6" (2× mais grossa) | Pu 174,1 kN / 54,0 mm | pico independe da malha |
| T21 Totalmente aderente / εcu = 4,5‰ | Pu 188,0 kN, 60,0 mm, σps 1776 MPa / Pu 174,7 kN, 55,3 mm | isolar o meio não deu ductilidade; εcu pouco muda o pico |

Regras aprendidas:
- O MEF de fibras acerta a flecha na ruptura que o mecanismo de corpos rígidos erra em 3×: a rotação é limitada pelo esmagamento da mesa, não pelo alongamento da cordoalha.
- Pcr do MEF sai acima do ensaio (+7 %) porque o MOR medido em prisma superestima a tração na peça e a cordoalha ganha tensão antes de fissurar; para prever fissuração de projeto usar fctk,inf.
- Conferir sempre a etapa 1 com o concreto elástico (`ELAST = True`): contraflecha e perda por encurtamento batem com a conta de mão; se a contraflecha sair para baixo, a seção de fibras está com área negativa (seção 5).
- A geometria do ensaio: apoios a 6" (0,15 m) das pontas, vão 17 ft; 1'-0" das pontas são os pontos de içamento/estocagem, não os apoios do ensaio.

```python
"""viga_protendida_ops.py — viga pré-tracionada (cordoalhas retas, trecho isolado) em OpenSeesPy, ensaio de 4 pontos.
Concreto e passiva em seção de fibras (dispBeamColumn, malha de 3"); cordoalha = Truss com InitStressMaterial ligada à viga por
rigidLink 'beam' só nos trechos aderentes (no trecho isolado, um único Truss → deformação uniforme, como bainha).
Unidades: kN, m, kPa. Base de validação: PCI Big Beam 2015 (UW, 'Mr. Beam')."""
import numpy as np
import openseespy.opensees as ops
ELAST = False             # True → concreto elástico (conferência da contraflecha e da perda por encurtamento)
ELEM = 'dispBeamColumn'   # 'forceBeamColumn' (npi=4, Lobatto) dá o mesmo pico: 174,3 kN / 54,3 mm


def curva_cordoalha(Ep=196e6, fpu=1862e3):
    """CP-190/gr. 270 RB: elástica até 0,8 fpu, depois curva de potência do PCI (268 − 0,075/(ε − 0,0065) ksi)."""
    ksi = 6894.76
    e = [0.0, 0.8 * fpu / Ep] + [0.0095, 0.012, 0.016, 0.02, 0.03, 0.05]
    s = [0.0, 0.8 * fpu] + [(268 - 0.075 / (x - 0.0065)) * ksi for x in e[2:]]
    return e, [min(v, fpu) for v in s]


def secao_I(tag, partes, yb, mc, ms=None, barras=(), nf=4):
    """partes = [(b_inf, b_sup, h)] de baixo para cima; y local = altura − yb. barras = [(As, y_da_base)]."""
    ops.section('Fiber', tag, '-GJ', 1e6)
    y0 = 0.0
    for b1, b2, h in partes:
        ya, yc = y0 - yb, y0 + h - yb
        n = max(2, int(round(h / 0.005)))            # fibras de ~5 mm na altura
        ops.patch('quad', mc, n, nf, ya, -b1 / 2, yc, -b2 / 2, yc, b2 / 2, ya, b1 / 2)   # anti-horário em (y, z)!
        y0 += h
    for As, y in barras:
        ops.fiber(y - yb, 0.0, As, ms)


def big_beam(dx=0.0762, sig_pe=1178e3, aderente=False, fc=63.4e3, Ec=25.0e6, fct=6.8e3, eps_c=0.003,
             eps_cu=0.0035, npi=2, ajustar=True, umax=0.10, du=2.5e-4):
    p = 0.0254
    L, xa, xb = 216 * p, 6 * p, 210 * p                 # peça 18 ft; apoios a 6" das pontas (vão 17 ft)
    xP = (90 * p, 126 * p)                               # cargas a 7 ft dos apoios
    xd = (42 * p, 174 * p)                               # trecho isolado central de 11 ft
    partes = [(6*p, 6*p, 4*p), (6*p, 2.5*p, p), (2.5*p, 2.5*p, 7*p), (2.5*p, 6*p, p), (6*p, 6*p, 5*p)]
    A = sum((a + b) / 2 * h for a, b, h in partes)
    yb = 9.175 * p; yp = 5 * p; Ap = 4 * 0.1519 * p * p; Ep = 28400 * 6894.76

    def montar(sig0):
        ops.wipe(); ops.model('basic', '-ndm', 2, '-ndf', 3)
        (ops.uniaxialMaterial('Elastic', 1, Ec) if ELAST else ops.uniaxialMaterial('Concrete04', 1, -fc, -eps_c, -eps_cu, Ec, fct, fct / Ec, 0.1))
        ops.uniaxialMaterial('Steel01', 2, 414e3, 200e6, 0.01)
        e, s = curva_cordoalha(Ep)
        ops.uniaxialMaterial('ElasticMultiLinear', 3, 0.0, '-strain', *(-np.array(e[::-1][:-1])).tolist(), *e,
                             '-stress', *(-np.array(s[::-1][:-1])).tolist(), *s)
        ops.uniaxialMaterial('InitStressMaterial', 4, 3, sig0)
        secao_I(1, partes, yb, 1, 2, barras=[(2 * 71e-6, 16.5 * p)])
        ops.beamIntegration('Legendre' if ELEM == 'dispBeamColumn' else 'Lobatto', 1, 1, npi); ops.geomTransf('Linear', 1)
        xs = np.round(np.arange(0, L + 1e-9, dx), 6)
        for x in (xa, xb, *xP, *xd):
            assert np.min(np.abs(xs - x)) < 1e-6, 'malha deve passar por apoios, cargas e limites do isolamento'
        n = len(xs)
        for i, x in enumerate(xs):
            ops.node(i + 1, x, 0.0)
        for i in range(n - 1):
            ops.element(ELEM, i + 1, i + 1, i + 2, 1, 1)
        nid = lambda x: int(np.argmin(np.abs(xs - x))) + 1
        ops.fix(nid(xa), 1, 1, 0); ops.fix(nid(xb), 0, 1, 0)
        # cordoalha: nós a −(yb − yp) presos à viga onde é aderente
        presos = [i + 1 for i, x in enumerate(xs) if aderente or x <= xd[0] + 1e-6 or x >= xd[1] - 1e-6]
        k0 = 1000; e0 = 1000
        for nb in presos:
            ops.node(k0 + nb, ops.nodeCoord(nb)[0], -(yb - yp)); ops.rigidLink('beam', nb, k0 + nb)
        tr = []
        for a, b in zip(presos[:-1], presos[1:]):
            ops.element('Truss', e0 + a, k0 + a, k0 + b, Ap, 4); tr.append(e0 + a)
        return dict(nid=nid, n=n, tr=tr, meio=nid(L / 2), xs=xs, ele_meio=nid(L / 2) - 1)

    def estatica(n, inc):
        ops.constraints('Penalty', 1e12, 1e12); ops.numberer('RCM'); ops.system('UmfPack')
        ops.test('NormDispIncr', 1e-9, 100); ops.algorithm('Newton')
        ops.integrator('LoadControl', inc); ops.analysis('Static')
        return ops.analyze(n)

    sig0 = sig_pe
    for _ in range(4 if ajustar else 1):                 # σ0 na pista tal que σpe após encurtamento = sig_pe
        m = montar(sig0)
        ops.timeSeries('Linear', 1); ops.pattern('Plain', 1, 1)
        for e in range(1, m['n']):
            ops.eleLoad('-ele', e, '-type', '-beamUniform', -4.83 / L)
        assert estatica(10, 0.1) == 0
        s_meio = ops.eleResponse(m['tr'][len(m['tr']) // 2], 'axialForce')[0] / Ap
        if not ajustar or abs(s_meio - sig_pe) < 0.1e3:
            break
        sig0 += sig_pe - s_meio
    ops.loadConst('-time', 0.0); ops.wipeAnalysis()
    v0 = ops.nodeDisp(m['meio'], 2)
    ops.timeSeries('Linear', 2); ops.pattern('Plain', 2, 2)
    for x in xP:
        ops.load(m['nid'](x), 0.0, -0.5, 0.0)            # P total = fator de carga
    ops.constraints('Penalty', 1e12, 1e12); ops.numberer('RCM'); ops.system('UmfPack')
    ops.test('NormDispIncr', 1e-8, 200); ops.algorithm('KrylovNewton')
    ops.integrator('DisplacementControl', m['meio'], 2, -du); ops.analysis('Static')
    P, d, sp, eb = [], [], [], []
    while abs(ops.nodeDisp(m['meio'], 2) - v0) < umax:
        if ops.analyze(1) != 0:
            ops.algorithm('Newton', '-initial')
            ok = ops.analyze(1); ops.algorithm('KrylovNewton')
            if ok != 0:
                break
        P.append(ops.getLoadFactor(2)); d.append(v0 - ops.nodeDisp(m['meio'], 2))
        sp.append(ops.eleResponse(m['tr'][len(m['tr']) // 2], 'axialForce')[0] / Ap)
        dfm = ops.eleResponse(m['ele_meio'], 'section', 1, 'deformation')  # [ε0, κ] no nó i do elemento do meio
        eb.append(dfm[0] + yb * dfm[1])                                  # ε na fibra inferior (+ tração)
        if len(P) > 20 and P[-1] < 0.75 * max(P):
            break
    P, d, sp, eb = map(np.array, (P, d, sp, eb))
    icr = int(np.argmax(eb >= fct / Ec)); ipk = int(np.argmax(P))
    return dict(sig0=sig0, Pcr=P[icr], Pu=P[ipk], d_pk=d[ipk], sp_pk=sp[ipk], P=P, d=d, sp=sp, A=A, camber=v0)


if __name__ == '__main__':
    for nome, kw in [('isolado, dx=3"', {}), ('isolado, dx=6"', dict(dx=0.1524)),
                     ('totalmente aderente', dict(aderente=True)),
                     ('isolado, εcu=4,5‰', dict(eps_cu=0.0045))]:
        r = big_beam(**kw)
        print('%-22s σ0=%6.1f MPa  contraflecha=%5.1f mm  Pcr=%6.1f  Pu=%6.1f kN  δ(Pu)=%5.1f mm  σps(Pu)=%6.0f MPa'
              % (nome, r['sig0'] / 1e3, r['camber'] * 1e3, r['Pcr'], r['Pu'], r['d_pk'] * 1e3, r['sp_pk'] / 1e3))
```