"""Barracão 20×30 Vitalle — opção 2 (duas águas 15°, meias-tesouras T60 rotuladas na cumeeira + tirante).
Teste do pipeline JAX FDM -> OpenSees no pórtico transversal. Unidades: kN, m.
Hipóteses (a confirmar pelo Nathan): pórticos a cada 5,90 m; G cobertura 0,45 kN/m² (telha + terças);
Q 0,25 kN/m²; vento V0 = 40 m/s, S1 = S3 = 1, S2 = 0,85 (cat. III, classe B, z ≈ 9 m) -> q = 0,71 kN/m²;
sucção líquida ΔCp = Cpe − Cpi com Cpe = −0,8 nas duas águas e Cpi = +0,2 (fechado) ou +0,8 (portão aberto).
"""
import json
import math
import numpy as np
import openseespy.opensees as ops

L, f15 = 20.0, 10.0 * math.tan(math.radians(15))     # vão entre eixos; flecha de 15° = 2,68 m
s = 5.90; gcob, qcob = 0.45, 0.25
# T60: mesa 40×14, alma 20×46
A_T = 0.40 * 0.14 + 0.20 * 0.46
yc = (0.056 * 0.07 + 0.092 * 0.37) / A_T
I_T = 0.40 * 0.14**3 / 12 + 0.056 * (yc - 0.07)**2 + 0.20 * 0.46**3 / 12 + 0.092 * (0.37 - yc)**2
pp_T = 25 * A_T                                        # kN/m ao longo da peça
nx = 20; dx = L / nx; xs = np.linspace(-L / 2, L / 2, nx + 1)
Vk = 40 * 0.85; qv = 0.613 * Vk**2 / 1000              # kN/m²
Ecs = min(0.8 + 0.2 * 40 / 80, 1.0) * 5600 * math.sqrt(40) * 1e3   # C40, αE = 1 — NBR 6118:2023 item 8.2.8


def cargas_nodais(z, fator_g=1.0, fator_q=1.0):
    """Carga vertical por nó (kN, para baixo +): cobertura por largura em planta + peso da peça pelo comprimento real."""
    P = np.zeros(nx + 1)
    for i in range(nx):
        Lr = math.hypot(dx, z[i + 1] - z[i])
        w = fator_g * (gcob * s * dx + pp_T * Lr) + fator_q * qcob * s * dx
        P[i] += w / 2; P[i + 1] += w / 2
    return P


# ----------------------------------------------------------------------------- 1. JAX FDM
def funicular(f_alvo=None, H_alvo=None, fator_g=1.0, fator_q=1.0):
    """Corrente de nós nas terças (x fixo por meta), apoios nos pés. Meta: flecha f_alvo na cumeeira
    OU empuxo H_alvo (reação horizontal no apoio = força no tirante). Itera 3× a carga de peso próprio pelo comprimento."""
    from jax_fdm.datastructures import FDNetwork
    from jax_fdm.equilibrium import constrained_fdm
    from jax_fdm.goals import NodeXCoordinateGoal, NodeZCoordinateGoal, NodeResidualForceGoal
    from jax_fdm.losses import Loss, SquaredError
    from jax_fdm.optimization import LBFGSB
    from jax_fdm.parameters import EdgeForceDensityParameter
    z = np.where(np.abs(xs) < 1e-9, f15, f15 * (1 - np.abs(xs) / (L / 2)))
    for _ in range(3):
        P = cargas_nodais(z, fator_g, fator_q)
        net = FDNetwork()
        nodes = [net.add_node(x=float(x), y=0.0, z=float(zz)) for x, zz in zip(xs, z)]
        for a, b in zip(nodes[:-1], nodes[1:]):
            net.add_edge(a, b); net.edge_forcedensity((a, b), -50.0)
        net.node_anchor(nodes[0]); net.node_anchor(nodes[-1])
        for k in nodes[1:-1]:
            net.node_load(k, load=[0.0, 0.0, -float(P[k])])
        goals = [NodeXCoordinateGoal(k, target=float(xs[k])) for k in nodes[1:-1]]
        if f_alvo is not None:
            goals.append(NodeZCoordinateGoal(nodes[nx // 2], target=f_alvo, weight=10.0))
        else:
            V = P[1:-1].sum() / 2
            goals.append(NodeResidualForceGoal(nodes[0], target=math.hypot(H_alvo, V), weight=10.0))
        params = [EdgeForceDensityParameter(e, None, -1e-3) for e in net.edges()]
        r = constrained_fdm(net, optimizer=LBFGSB(), parameters=params, loss=Loss(SquaredError(goals)),
                            maxiter=3000, tol=1e-14)
        z = np.array([r.node_coordinates(k)[2] for k in nodes])
    R = r.node_reaction(nodes[0])
    return dict(z=z, H=abs(R[0]), V=abs(R[2]), forcas=[float(r.edge_force(e)) for e in r.edges()], P=P)


# ----------------------------------------------------------------------------- 2. OpenSees (pórtico)
def portico(z, comb, tirante_A=11.4e-4, so_tracao=True, hp=6.0):
    """Pilares 25×40 engastados (h = 6 m), meias-tesouras T60 rotuladas no pilar e na cumeeira, tirante entre os pés.
    comb = dict(g=γg, q=γq, w=γw, cpi=…). Retorna esforços."""
    ops.wipe(); ops.model('basic', '-ndm', 2, '-ndf', 3)
    ops.node(1, -L / 2, -hp); ops.node(2, L / 2, -hp); ops.fix(1, 1, 1, 1); ops.fix(2, 1, 1, 1)
    ops.node(3, -L / 2, 0.0); ops.node(4, L / 2, 0.0)                   # topo dos pilares
    ops.geomTransf('Linear', 1); ops.geomTransf('Linear', 2)
    Ip = 0.25 * 0.40**3 / 12
    ops.element('elasticBeamColumn', 1, 1, 3, 0.10, Ecs, Ip, 1); ops.element('elasticBeamColumn', 2, 2, 4, 0.10, Ecs, Ip, 1)
    # nós da peça: 100+i ; cumeeira duplicada (rótula) 200
    for i, (x, zz) in enumerate(zip(xs, z)):
        ops.node(100 + i, float(x), float(zz))
    ops.node(200, 0.0, float(z[nx // 2]))
    ops.equalDOF(3, 100, 1, 2); ops.equalDOF(4, 100 + nx, 1, 2)         # pé rotulado no pilar
    ops.equalDOF(100 + nx // 2, 200, 1, 2)                              # rótula na cumeeira
    e = 10; ele = []
    for i in range(nx):
        a = 100 + i; b = 100 + i + 1
        if i == nx // 2: a = 200                                        # meia-tesoura direita começa no nó duplicado
        ops.element('elasticBeamColumn', e, a, b, A_T, Ecs, I_T, 2); ele.append(e); e += 1
    mat = 50
    if so_tracao:
        ops.uniaxialMaterial('Elastic', mat, 200e6, 0.0, 0.0)            # Eneg = 0 -> só tração
    else:
        ops.uniaxialMaterial('Elastic', mat, 200e6)
    ops.element('Truss', 99, 3, 4, tirante_A, mat)
    ops.timeSeries('Linear', 1); ops.pattern('Plain', 1, 1)
    P = cargas_nodais(z, comb['g'], comb['q'])
    for i in range(nx + 1):
        ops.load(100 + i, 0.0, -float(P[i]), 0.0)
    if comb.get('w'):
        dcp = -0.8 - comb['cpi']                                        # pressão líquida (negativa = sucção, sai da superfície)
        p = comb['w'] * dcp * qv * s                                    # kN/m ao longo da peça, normal à superfície
        for i in range(nx):
            x1, z1, x2, z2 = xs[i], z[i], xs[i + 1], z[i + 1]
            Lr = math.hypot(x2 - x1, z2 - z1); nxv, nzv = -(z2 - z1) / Lr, (x2 - x1) / Lr   # normal para cima/fora
            F = -p * Lr / 2                                             # sucção puxa para fora (+normal)
            for k in (i, i + 1):
                ops.load(100 + k, F * nxv, F * nzv, 0.0)
    ops.constraints('Transformation'); ops.numberer('RCM'); ops.system('BandGeneral')
    ops.test('NormDispIncr', 1e-9, 100); ops.algorithm('Newton'); ops.integrator('LoadControl', 0.1)
    ops.analysis('Static'); ok = ops.analyze(10); ops.reactions()
    Mr = []; Nr = []
    for el in ele:
        fl = ops.eleResponse(el, 'localForce'); Mr += [abs(fl[2]), abs(fl[5])]; Nr += [-fl[0], fl[3]]
    Mp = max(abs(ops.eleResponse(k, 'localForce')[2]) for k in (1, 2))
    T = ops.eleResponse(99, 'axialForce')[0]
    return dict(ok=ok == 0, T=T, Mraf=max(Mr), Nraf=min(Nr), Mpil=Mp,
                u_topo=max(abs(ops.nodeDisp(3, 1)), abs(ops.nodeDisp(4, 1))) * 1e3,
                w_cum=-ops.nodeDisp(200, 2) * 1e3)


if __name__ == '__main__':
    out = dict(hip=dict(L=L, f=f15, s=s, gcob=gcob, qcob=qcob, A_T=A_T, I_T=I_T, pp_T=pp_T, qv=qv, Ecs=Ecs))
    reta = f15 * (1 - np.abs(xs) / (L / 2))
    F1 = funicular(f_alvo=f15, fator_g=1.4, fator_q=1.4)
    # conferência: H = M0/f com as mesmas cargas nodais
    P = F1['P']
    # M0 no meio = V·L/2 − Σ P_i·|x_i| para os nós à esquerda
    V = P[1:-1].sum() / 2; M0 = V * L / 2 - sum(P[i] * (0 - xs[i]) for i in range(1, nx // 2))
    print('funicular: H FDM', round(F1['H'], 2), ' M0/f', round(M0 / f15, 2), ' z max', round(F1['z'].max(), 3))
    out['fun'] = dict(z=F1['z'].tolist(), H=F1['H'], H_mao=M0 / f15)
    # inverso: flecha para um tirante de cálculo de 150 kN (barra A36 Ø1.1/4")
    F2 = funicular(H_alvo=150.0, fator_g=1.4, fator_q=1.4)
    print('para H = 150 kN: flecha', round(F2['z'].max(), 3), ' H', round(F2['H'], 2), ' mão M0/H', round(M0 / 150, 3))
    out['inv'] = dict(z=F2['z'].tolist(), H=F2['H'], f=float(F2['z'].max()), f_mao=M0 / 150)
    combos = {
        'ELU gravidade 1,4G + 1,4Q': dict(g=1.4, q=1.4),
        'ELU sucção 1,0G + 1,4W (Cpi +0,2)': dict(g=1.0, q=0.0, w=1.4, cpi=0.2),
        'ELU sucção 1,0G + 1,4W (Cpi +0,8, portão aberto)': dict(g=1.0, q=0.0, w=1.4, cpi=0.8),
    }
    out['res'] = {}
    for nome, zz in (('Reta 15° (opção 2)', reta), ('Funicular, mesma flecha', F1['z'])):
        for cn, c in combos.items():
            r = portico(zz, c); out['res'][f'{nome}|{cn}'] = r
            print(f'{nome:28s} {cn:48s}', {k: (round(v, 1) if isinstance(v, float) else v) for k, v in r.items()})
    json.dump(out, open('portico_res.json', 'w'))
