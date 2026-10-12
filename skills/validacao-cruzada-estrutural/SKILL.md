---
name: "validacao-cruzada-estrutural"
description: "Use para conferir resultados de software estrutural (nd_estruturas, HyperFrame, TQS, Eberick, CYPE) por caminho independente: pórtico no OpenSeesPy, peso, vento, γz e peças recalculadas."
---

# Validação cruzada de software estrutural — ND Engenharia

Roteiro para dizer, com números, se um programa calcula certo e o que ele deixa de verificar. Vale para o nosso software (`nd_estruturas`), para o HyperFrame e para saídas de TQS, Eberick ou CYPE que o Nathan mandar. Usar junto com `mef-opensees-opsvis` (motor), `dimensionamento-concreto-armado-nbr` (peças) e `normas-vigentes-nd` (tabelas 4.7 e 4.8 de lacunas típicas).

Regra central: nunca usar o código do programa para conferir o programa. Cada número é refeito por outro caminho: outro solver, outro algoritmo ou conta manual.

## 1. Roteiro (nesta ordem)

1. **Testes do próprio programa.** Rodar a suíte (ex.: `npm test`, `pytest`) e a checagem de tipos. Anotar quantos passam. Teste verde só prova coerência interna.
2. **Exportar o modelo.** Nós (x, y, z, apoio, mestre do diafragma), barras (nós, seção, A, Iy, Iz, J, eixos locais), cargas por caso (distribuídas locais e nodais) e resultados por caso (deslocamentos dos mestres, reações por apoio). JSON em SI: m, kN, kPa.
3. **Peso e equilíbrio.** Levantar G e Q à mão (lajes, vigas, pilares, alvenarias, regiões) e comparar com ΣFz das reações. Tolerância 0,5 %. Ver se furos e escadas substituem ou somam carga da laje.
4. **Vento.** Refazer S2, q(z) e Ca na edição vigente (NBR 6123:2023); se o programa usa 1988, conferir nos parâmetros dele e marcar ALERTA. Conferir F = Ca·q·A por pavimento e ΣFx.
5. **Pórtico no OpenSeesPy** (seção 2). Rodar G e vento X/Y nos dois passes de rigidez. Tolerância: deslocamento do topo e reações < 0,1 %. Diferença maior é erro de modelo (eixos, unidades, diafragma, cargas), não de norma.
6. **γz independente.** M1 = Σ γf·Fi·zi; ΔM = Σ (1,4Gi + 0,7Qi)·γf·δi com δ do passe ELU. γz = 1/(1 − ΔM/M1). Tolerância 0,5 % (o programa pode somar o δ da gravidade).
7. **Peças por outro algoritmo** (seção 3): vigas, lajes, pilares, sapatas, blocos.
8. **Lacunas.** Passar as tabelas 4.7 e 4.8 de `normas-vigentes-nd`: o que o programa NÃO verifica costuma pesar mais que o que ele calcula errado.
9. **Caso real da ND.** Rodar um elemento de obra nossa já calculado e comparar a conclusão, separando diferença de método de diferença de dado de entrada.
10. **Relatório** (Claude Docs): resumo com veredito → tabela "O que confere" (verificação | programa | cálculo ND | diferença) → tabela "Problemas" por gravidade com número do exemplo e item da norma → caso real → recomendação.

## 2. Pórtico espacial no OpenSeesPy (replica qualquer programa com diafragma rígido)

Hipóteses que precisam bater com as do programa: pilares engastados na base, diafragma rígido por pavimento (mestre com ux, uy, rz livres), elemento elástico de 12 GDL, sem trechos rígidos (ou com, se o programa usar), dois passes de rigidez.

| Passe | EI | EA | GJ |
|---|---|---|---|
| ELU (γz, esforços) | vigas 0,4·Eci·I, pilares 0,8·Eci·I (6118 15.7.3) | Ecs·A | Gc·J (vigas × fator de torção do programa, ex.: 0,05) |
| ELS (deslocamentos) | Ecs·I | Ecs·A | idem |

Como o elasticBeamColumn usa um E só para EA e EI, entrar com E = E_flexão e A' = Ecs·A/E_flexão.

```python
import openseespy.opensees as ops

def portico(nodes, members, masters, mem_loads, nod_loads, cp, red, passe='els', torc_viga=0.05):
    """nodes: [{id,x,y,z,support,kind,levelIndex}], members: [{id,ni,nj,props{A,Iy,Iz,J},zLocal,ref{kind}}],
    masters: {nivel: id_mestre}, mem_loads: [{wx,wy,wz}] por barra (kN/m, eixos locais),
    nod_loads: [{node,dof(0-5),value}], cp: {eci,ecs,gc} kPa, red: {'beams':0.4,'columns':0.8}."""
    ops.wipe(); ops.model('basic', '-ndm', 3, '-ndf', 6)
    for n in nodes:
        ops.node(n['id'], n['x'], n['y'], n['z'])
        if n['support']: ops.fix(n['id'], 1, 1, 1, 1, 1, 1)
        if n['kind'] == 'master': ops.fix(n['id'], 0, 0, 1, 1, 1, 0)
    for lvl, mid in masters.items():
        esc = [n['id'] for n in nodes if n['levelIndex'] == lvl and n['kind'] != 'master' and not n['support']]
        ops.rigidDiaphragm(3, mid, *esc)
    for m in members:
        viga = m['ref']['kind'] == 'beam'
        E = cp['ecs'] if passe == 'els' else cp['eci'] * red['beams' if viga else 'columns']
        p = m['props']
        ops.geomTransf('Linear', m['id'] + 1, *m['zLocal'])          # vecxz = eixo z local
        ops.element('elasticBeamColumn', m['id'] + 1, m['ni'], m['nj'], cp['ecs'] * p['A'] / E, E, cp['gc'],
                    p['J'] * (torc_viga if viga else 1.0), p['Iy'], p['Iz'], m['id'] + 1)
    ops.timeSeries('Linear', 1); ops.pattern('Plain', 1, 1)
    for i, w in enumerate(mem_loads):
        if any(w.values()): ops.eleLoad('-ele', i + 1, '-type', '-beamUniform', w['wy'], w['wz'], w['wx'])
    for nl in nod_loads:
        v = [0.0] * 6; v[nl['dof']] = nl['value']; ops.load(nl['node'], *v)
    ops.constraints('Transformation'); ops.numberer('RCM'); ops.system('UmfPack')
    ops.algorithm('Linear'); ops.integrator('LoadControl', 1.0); ops.analysis('Static')
    assert ops.analyze(1) == 0
    ops.reactions()
    R = [sum(ops.nodeReaction(n['id'], d) for n in nodes if n['support']) for d in (1, 2, 3)]  # GDL 1-based
    topo = {lvl: [ops.nodeDisp(mid, 1), ops.nodeDisp(mid, 2), ops.nodeDisp(mid, 6)] for lvl, mid in masters.items()}
    return R, topo
```

Armadilhas: `nodeReaction(tag, dof)` usa GDL a partir de 1; `-beamUniform` em 3D recebe (Wy, Wz, Wx); o vento costuma entrar no mestre com momento de torção F·e (excentricidade) — replicar.

Rodada extra que vale a pena: a mesma análise com seções retangulares puras (sem mesa colaborante) para medir quanto a hipótese do programa enrijece a estrutura.

## 3. Peças por algoritmo diferente

- **Vigas, flexão.** Bisseção em x de Md = 0,68·fcd·b·x·(d − 0,4x) (o programa costuma usar a fórmula fechada). Usar o mesmo d do programa (ex.: h − c − φt − φl/2). Comparar max(As, As,mín). Seção T só quando 0,8x ≤ hf.
- **Vigas, cortante.** Modelo I: Vc = 0,6·fctd·bw·d, Asw/s = (Vd − Vc)/(0,9·d·fywd) ≥ 0,2·fctm/fywk·bw. Conferir também VRd2 (dele dá para deduzir o d usado).
- **Lajes, Marcus.** Quinhão kA = cB·lB⁴/(cA·lA⁴ + cB·lB⁴) com c = 5 (apoiada-apoiada), 2 (apoiada-engastada; exato 2,08 = 384/185) e 1 (biengastada). Momentos wl²/8, 9wl²/128, wl²/24 e negativos wl²/8, wl²/12. Até 2,5 % de diferença vem só da escolha do coeficiente 2 × 2,08; dizer qual foi usado. Ver se o programa aplica a redução de Marcus no positivo.
- **Pilares, flexão oblíqua.** Fibras com parábola-retângulo (εc2 = 2 ‰, εcu = 3,5 ‰, aço bilinear, pivô C a 3h/7). Para o Nd da combinação: varrer o ângulo da LN, achar por bisseção a profundidade que dá N = Nd, montar a curva (MRd,u; MRd,v) e intersectar com o raio do momento solicitante: utilização = |Md|/|MRd| na mesma direção. Diferença > 3 % com o programa mais folgado → procurar bloco retangular com 0,85·fcd em zona comprimida que estreita.
- **Sapatas.** σ = 1,05·N/(a·b)·(1 + 6ea/a + 6eb/b) e tirante pelas bielas T = Nd·(a − ap)/(8d). Refazer COM vento (tabela 4.8).
- **Blocos.** Blévot (2–5 estacas) com o mesmo h do programa; CEB-70 para 6+ com limite de cortante de bloco sem estribo; distribuir momentos entre estacas.

## 4. Critério de veredito

| Resultado | Leitura |
|---|---|
| Solver < 0,1 % e peças < 1 % | Motor confiável para aquela hipótese |
| Peças 1–5 % com causa identificada (coeficiente, bloco de tensões) | Aceitável; registrar a hipótese |
| Diferença sem causa ou > 5 % contra a segurança | ERRO até explicar |
| Verificação ausente (vento em fundação, cortante de bloco) | ERRO de escopo, mesmo com tudo que existe batendo |

Nenhum programa vira base de memória com ART só porque passou aqui; a conferência cobre o edifício testado.

## 5. Registro — HyperFrame v0.2.50 (11/10/2026)

Repositório github.com/candidoalfilho/hyperframe (MIT, TypeScript, motor em `packages/engine`, zero dependências). Rodar sem interface:

```bash
git clone --depth 1 https://github.com/candidoalfilho/hyperframe.git
cd hyperframe && npm install --workspace @hyperframe/engine && npm test
# script tsx: import { createSampleProject, analyze } from '.../packages/engine/src/index'
# modelo interno: buildAnalysisModel(project) → { model, internal: { memberLoads, nodalLoads } }
```

Convenções dele: SI (m, kN, kPa); vigas com y local = Z global e Iz = bw·h³/12; pilares com x local para cima; diafragma mestre-escravo; resultados por caso em `cases.elu` / `cases.els`. Não fazer commit nem push no repositório dele; se o `npm install` mexer no `package-lock.json`, desfazer.

Edifício exemplo (8 pav., 12 pilares 25×60, vigas 20×50, laje 12 cm, C30, V0 = 40 m/s, cat. IV):

| Verificação | HyperFrame | ND | Diferença |
|---|---|---|---|
| G / Q totais | 9.065,5 / 1.428,7 kN | igual (manual) | 0 % |
| q topo (z = 23 m) | 0,838 kPa | 0,839 kPa | 0,1 % |
| Topo ELS vento X / Y | 4,28 / 8,95 mm | igual (OpenSeesPy) | < 0,001 % |
| γz X / Y | 1,032 / 1,041 | igual | < 0,1 % |
| Vigas, 136 As/Asw | — | idênticas | 0 % |
| Lajes, momentos | — | até 2,5 % | coeficiente Marcus |
| Pilares, utilização oblíqua | 0,55–0,88 | 0,53–0,91 | ≤ 3,5 % (0,85·fcd constante) |

Lacunas encontradas: fundações só com G + Q (sapata de canto 371 kPa com vento contra σadm 250); blocos 6+ com cortante só contra VRd2; momentos do pilar não distribuídos nas estacas; α1 = 0,6 para pórtico puro; vento pela 6123:1988; água de reservatório como Q. No Bloco B39 (3 estacas Ø40, N = 342 tf) ele concorda que não atende (estaca a 134 %), mas majora por 1,4 — confirmar se a carga de entrada já é de cálculo.