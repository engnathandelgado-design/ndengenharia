"""ND-LET-COB08 — terças: furação de fabricação por marca, alma planificada (rev11, Nathan 26/10/2026, checklist 8).
Uma faixa por peça-base (T1..T5) com todos os furos comuns (pontas, correntes) em ordenadas a partir da ponta inicial e os furos
das diagonais (marcas D); tabela por marca com os furos próprios (Ø18 das diagonais e oblongos do X), já medidos da ponta inicial.
Fonte: cob_comum.py (furos_ponta, furos_x, marca, lista_marcas) — a mesma da COB01, da lista e do 3D. Cotas em mm. A1."""
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha
from cob_comum import (VAOS, NT, L_TERCA, EXT, BASE_K, H_TERCA, Z_FURO, Z_COR, Z_DIAG, Z_X, IDX_2A, PESO_UE, PERFIL_TXT,
                       furos_ponta, furos_x, marca, lista_marcas, cabecalho)

pr = Prancha("A1", cabecalho("ND-LET-COB08", "01/01", "COBERTURA METÁLICA — TERÇAS: FURAÇÃO DE FABRICAÇÃO POR MARCA (ALMA PLANIFICADA)"))
pr.revisao("11", "26/10/2026", "EMISSÃO: FURAÇÃO DE CADA MARCA MEDIDA DA PONTA INICIAL (CHECKLIST 8)")
Q = pr.quadro
fm = lambda v: f"{v:,.0f}".replace(",", ".")
E = 25


def furos_base(k):
    """furos comuns da peça do vão k, medidos da ponta inicial (lado do eixo k+1): [(s, z, diam, tipo)]."""
    e0, e1 = EXT[k]
    L = L_TERCA[k]
    out = []
    for s in furos_ponta(e0):
        out += [(s, z, 14, "fix") for z in Z_FURO]
    for s in furos_ponta(e1):
        out += [(L - s, z, 14, "fix") for z in Z_FURO]
    for t in (0.25, 0.5, 0.75):
        out.append((round(e0 + VAOS[k] * t), Z_COR, 12, "cor"))
    return sorted(out)


def furos_d(k):
    e0 = EXT[k][0]
    q = [VAOS[k] * t for t in (0.25, 0.5, 0.75)]
    return [round(e0 + y) for y in (q[0], q[1] - 60, q[1] + 60, q[2])]


# ------------------------------------------------------------------ faixas por peça-base
bases = []
for k in range(8):
    if BASE_K[k] not in [b for b, _ in bases]:
        bases.append((BASE_K[k], k))
y_top = Q[3] - 30
for j, (bm, k) in enumerate(bases):
    L = L_TERCA[k]
    vaos = ", ".join(f"{i + 1}-{i + 2}" for i in range(8) if BASE_K[i] == bm)
    org = (Q[0] + 22, y_top - j * 98 - 46)
    v = pr.vista(f"PEÇA {bm}", org, E, titulo=f"PEÇA {bm} — L = {fm(L)} (VÃOS {vaos})",
                 subtitulo=f"alma planificada vista do lado da aba inferior; ponta inicial à esquerda (eixo {k + 1})")
    v.ret(0, 0, L, H_TERCA, "METALICA")
    fb = furos_base(k)
    for s, z, d, tp in fb:
        v.circulo((s, z), d / 2 * 2.5, "METALICA")                  # símbolo ampliado 2,5× (furo real na tabela de furos)
    for s in furos_d(k):
        v.circulo((s, Z_DIAG), 9 * 2.5, "OCULTA")
    v.linha((0, Z_FURO[0]), (L, Z_FURO[0]), "EIXO"); v.linha((0, Z_FURO[1]), (L, Z_FURO[1]), "EIXO")
    xs_cima = sorted({s for s, z, d, tp in fb})
    v.cota_ord(xs_cima, H_TERCA, 6, x0=0)
    v.cota_ord(furos_d(k), 0, -6, x0=0)
    v.texto((L + 250, H_TERCA / 2), "ponta final", "nota", "MIDDLE_LEFT")
    v.texto((-250, H_TERCA / 2), "inicial", "nota", "MIDDLE_RIGHT")

# ------------------------------------------------------------------ tabela por marca
LM = lista_marcas()
lin = []
for m, dd in LM.items():
    k = next(i for i in range(8) if BASE_K[i] == m[:2] and any(marca(i, ii) == m for ii in range(2 * NT)))
    i = next(ii for ii in range(2 * NT) if marca(k, ii) == m)
    dsc = " · ".join(fm(s) for s in furos_d(k)) if i in IDX_2A else "-"
    fx = furos_x(k, i)
    xs = " / ".join(fm(EXT[k][0] + y) for y, z, nm in fx) if fx else "-"
    lin.append([m, m[:2], fm(dd["L"]), f"{dd['qt']}", dsc, xs])
x0t = Q[2] - 182
y = pr.tabela(x0t, Q[3] - 4, "FUROS PRÓPRIOS DE CADA MARCA (DA PONTA INICIAL, mm)",
              ["MARCA", "PEÇA", "L", "QT", f"Ø18 DIAGONAIS (z {Z_DIAG})", f"OBLONGOS 18×28 X (z {Z_X[0]} / {Z_X[1]})"], lin, [20, 12, 16, 10, 66, 56], h_lin=5.4)
FUR = [["Ø14", f"{Z_FURO[0]} e {Z_FURO[1]}", "fixação (M12): apoio e emenda", "todas"],
       ["Ø12", f"{Z_COR}", "correntes Ø10 (L/4, L/2, 3L/4)", "todas"],
       ["Ø18", f"{Z_DIAG}", "diagonais de ancoragem Ø16", "marcas com D"],
       ["18×28", f"{Z_X[0]} ( / ) e {Z_X[1]} ( \\ )", "passagem das diagonais do X", "marcas com X / Y"]]
y = pr.tabela(x0t, y - 4, "FUROS NA ALMA (z DO FUNDO DA TERÇA)", ["FURO", "z (mm)", "USO", "MARCAS"], FUR, [16, 36, 80, 48])
notas = [f"Perfil {PERFIL_TXT}; furação de fábrica (puncionada ou furada antes da galvanização), tolerância ±1 mm na posição.",
         "Ponta inicial = ponta do lado do eixo de menor número; marcar a ponta inicial e a marca com tinta na alma. Aba superior (90) para o lado A da cobertura em todas as peças.",
         "Faixas: furos comuns de cada peça-base (em cima: fixação e correntes; embaixo, tracejados: Ø18 só das marcas D). Símbolos dos furos ampliados para leitura.",
         "Oblongos do X: eixo maior ao longo da terça; diagonal / a 35 e \\ a 75 do fundo.",
         "Quantidades e pesos: ND-LET-COB01; comprimentos e transpasses em cadeia: ND-LET-COB07."]
pr.notas(x0t, y - 4, notas, 180)
avisos = pr.salvar("/home/claude/letsara/pranchas/ND-LET-COB08")
for a in avisos:
    print(a)
