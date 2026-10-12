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
    # NBR 6118:2023 item 8.2.8: Eci = αE·5600·√fck; Ecs = αi·Eci, αi = 0,8 + 0,2·fck/80 ≤ 1,0 (fck ≤ 50 MPa). Saída em kPa.
    # TODO: vir do registro de normas (DEC-004) quando ele existir.
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


# ----------------------------------------------------------------------------- 5. arco/meia-tesoura funicular 2D
def arco_funicular(xs, P, f_alvo=None, H_alvo=None):
    """Corrente 2D com nós em xs (abscissas das terças, extremos = apoios na mesma cota 0) e cargas verticais P (kN, + para baixo).
    Meta: flecha f_alvo no nó central OU empuxo H_alvo (= força no tirante). x dos nós preso por meta.
    Retorna z, H e as forças nas barras. Conferência à mão: H = M0/f (M0 = momento de viga biapoiada no meio)."""
    from jax_fdm.datastructures import FDNetwork
    from jax_fdm.equilibrium import constrained_fdm
    from jax_fdm.goals import NodeXCoordinateGoal, NodeZCoordinateGoal, NodeResidualForceGoal
    from jax_fdm.losses import Loss, SquaredError
    from jax_fdm.optimization import LBFGSB
    from jax_fdm.parameters import EdgeForceDensityParameter
    if (f_alvo is None) == (H_alvo is None):
        raise ValueError('informe f_alvo OU H_alvo')
    xs = np.asarray(xs, float); P = np.asarray(P, float); n = len(xs) - 1
    net = FDNetwork(); nos = [net.add_node(x=float(x), y=0.0, z=0.0) for x in xs]
    for a, b in zip(nos[:-1], nos[1:]):
        net.add_edge(a, b); net.edge_forcedensity((a, b), -50.0)
    net.node_anchor(nos[0]); net.node_anchor(nos[-1])
    for k in nos[1:-1]:
        net.node_load(k, load=[0.0, 0.0, -float(P[k])])
    metas = [NodeXCoordinateGoal(k, target=float(xs[k])) for k in nos[1:-1]]
    if f_alvo is not None:
        metas.append(NodeZCoordinateGoal(nos[n // 2], target=f_alvo, weight=10.0))
    else:
        metas.append(NodeResidualForceGoal(nos[0], target=float(np.hypot(H_alvo, P[1:-1].sum() / 2)), weight=10.0))
    r = constrained_fdm(net, optimizer=LBFGSB(), parameters=[EdgeForceDensityParameter(e, None, -1e-3) for e in net.edges()],
                        loss=Loss(SquaredError(metas)), maxiter=3000, tol=1e-14)
    z = np.array([r.node_coordinates(k)[2] for k in nos])
    return dict(z=z, H=abs(r.node_reaction(nos[0])[0]), forcas=[float(r.edge_force(e)) for e in r.edges()])
