"""Letsara — registro da chaparia/insertos e checagem de compatibilidade das ligações (padrão Tekla).

Cada peça tem insertos em coordenadas locais (s ao longo da peça, n transversal, h altura).
Cada instância da peça tem uma transformação para coordenadas globais (x, y, z da obra).
Cada ligação reúne os insertos que precisam coincidir (pino × tubo, chapa × chapa, terça × chapa)
e a checagem confere distância, nível e folgas. Resultado: ligacoes.json + tabela para as pranchas.
"""
import json, math
from pathlib import Path

AQUI = Path(__file__).parent
TOL = 0.005                     # 5 mm entre eixos de pino/tubo e furos
I = 0.03                        # caimento da cobertura (3%)
from geometria import Y_LIN as YL, X_EIXO
X_CEN, X_P2 = X_EIXO["C"], X_EIXO["E"]
NEO = 0.010                     # neoprene


# Cobertura escondida pela platibanda (+10,00) com 10 cm de folga no lado alto (Nathan, 12/10/2026):
# telha junto ao P2 ≤ +9,90 → fundo da TS-01 no eixo do P1 em +7,46 (antes +8,08; desceu 0,62 m)
Z0_TS = 7.46


def z_fundo_viga(x):            # fundo da TS-01 montada (x a partir do eixo do P1)
    return Z0_TS + I * x


# ------------------------------------------------------------------ TS-01 (coordenadas locais, m)
# Dentes Gerber nas duas pontas (dente de 450 de altura e 300 de comprimento; apoio a 150 da ponta).
# Ponta do lado do pilar a 25 mm da face do pilar (40×60, face a 0,30 do eixo); ponta do lado central a 75 mm da face
# da I110 e dos pilares centrais P8A/P11 (todos com 400 em x) — mesmo comprimento nas 14 vigas (L_H 19 150).
X_PONTA_ESQ, X_PONTA_CEN = 0.325, X_CEN - 0.20 - 0.075
H_DENTE, L_DENTE = 0.45, 0.30
L_TS = round((X_PONTA_CEN - X_PONTA_ESQ) / math.cos(math.atan(I)), 3)
PASSO_T = round((L_TS - 2 * 0.255) / 12, 3)
TS = dict(L=L_TS, ponta_pino=0.15, alcas=[2.10, 7.40], estoque=[2.10],
          tercas=[round(0.255 + PASSO_T * k, 3) for k in range(13)], no_contrav=[round(0.255 + 2 * PASSO_T * k, 3) for k in range(7)])
# chapa da terça: CH-T1 nas terças comuns; CH-T2 (com furos extras do contraventamento) nos nós de painel
TS["alcas"] += [round(TS["L"] - a, 3) for a in reversed(TS["alcas"])]
TS["estoque"] += [round(TS["L"] - 2.10, 3)]
TS["insertos"] = (
    # ponta a prumo: na altura h a face da ponta está em s = h·tg(θ) a partir do canto inferior (ponto 0 da fôrma)
    [dict(id=f"TB-1.{k}", tipo="TB-1", s=round(s + H_DENTE * I, 4), n=0.0, h=H_DENTE) for k, s in enumerate((TS["ponta_pino"], TS["L"] - TS["ponta_pino"]))] +
    [dict(id=f"CH-A1.{k}", tipo="CH-A1", s=round(s + H_DENTE * I, 4), n=0.0, h=H_DENTE) for k, s in enumerate((TS["ponta_pino"], TS["L"] - TS["ponta_pino"]))] +
    [dict(id=f"{'CH-T2' if any(abs(s - c) < 1e-6 for c in TS['no_contrav']) else 'CH-T1'}.{k}",
          tipo="CH-T2" if any(abs(s - c) < 1e-6 for c in TS["no_contrav"]) else "CH-T1", s=s, n=0.0, h=0.90)
     for k, s in enumerate(TS["tercas"])] +
    [dict(id=f"TB-2.{k}", tipo="TB-2", s=s, n=0.0, h=0.60) for k, s in enumerate(TS["tercas"])] +
    [dict(id=f"AL-1.{k}", tipo="AL-1", s=s, n=0.0, h=0.90) for k, s in enumerate(TS["alcas"])])


def ts_global(x0, y, ins):
    """TS-01 montada com caimento de 3% (sobe com x). Ponta inicial em x0."""
    c, sn = 1 / math.sqrt(1 + I ** 2), I / math.sqrt(1 + I ** 2)
    xb = x0 + ins["s"] * c                      # ponto no fundo
    return (xb - ins["h"] * sn, y + ins["n"], z_fundo_viga(xb) + ins["h"] * c)


# ------------------------------------------------------------------ instâncias
inst = []
for i in range(1, 8):
    inst.append(dict(peca="TS-01", nome=f"TS-01 L{i+1} esq", x0=0.325, y=YL[i]))
    inst.append(dict(peca="TS-01", nome=f"TS-01 L{i+1} dir", x0=2 * X_CEN - X_PONTA_CEN, y=YL[i]))
glob = {}
for it in inst:
    for ins in TS["insertos"]:
        glob[(it["nome"], ins["id"])] = (ins["tipo"], ts_global(it["x0"], it["y"], ins))

# apoios das outras peças (coordenadas globais definidas pelo projeto dos pilares/I110)
apoios = []
# cotas de topo dos consolos como saem nas pranchas dos pilares e da I110 (arredondadas ao mm, topo inclinado 3%)
zc = lambda x: round(z_fundo_viga(x) + H_DENTE * math.cos(math.atan(I)) - NEO, 3)
X_PINO = [X_PONTA_ESQ + 0.15, X_PONTA_CEN - 0.15, 2 * X_CEN - X_PONTA_CEN + 0.15, X_P2 - X_PONTA_ESQ - 0.15]
for i in range(1, 8):
    y = YL[i]
    apoios.append(dict(peca=f"P1 L{i+1}", tipo="PN-1 Ø20 no consolo CP-TS", x=round(X_PINO[0], 3), y=y, z=zc(X_PINO[0]), face=0.30))
    apoios.append(dict(peca=f"P2 L{i+1}", tipo="PN-1 Ø20 no consolo CP-TS", x=round(X_PINO[3], 3), y=y, z=zc(X_PINO[3]), face=X_P2 - 0.30))
    sup = "pilar central P8A/P11 40×60 (consolo CP-TS)" if i in (1, 3) else "I110 (consolo CV-TS)"
    meia = 0.20
    for x, f_ in ((X_PINO[1], X_CEN - meia), (X_PINO[2], X_CEN + meia)):
        apoios.append(dict(peca=f"{sup} L{i+1}", tipo="PN-1 Ø20 no consolo", x=round(x, 3), y=y, z=zc(x), face=f_))
# ------------------------------------------------------------------ checagens
rel, erros = [], 0
for it in inst:
    for ins_id in ("TB-1.0", "TB-1.1"):
        tipo, (x, y, z) = glob[(it["nome"], ins_id)]
        cand = min(apoios, key=lambda a: math.dist((a["x"], a["y"]), (x, y)))
        d = math.dist((cand["x"], cand["y"]), (x, y)); dz = (z - NEO) - cand["z"]
        ok = d <= TOL and abs(dz) <= 0.003
        # folgas: ponta × face do apoio (≥ 20 mm) e ponta do consolo × face reentrante do dente (≥ 20 mm)
        ponta = it["x0"] if ins_id.endswith(".0") else it["x0"] + TS["L"] * math.cos(math.atan(I))
        folga_ponta = abs(ponta - cand["face"])
        proj = 0.35 if "I110" in cand["peca"] else 0.30                 # balanço do consolo a partir da face
        folga_consolo = folga_ponta + L_DENTE * math.cos(math.atan(I)) - proj
        ok = ok and folga_ponta >= 0.020 and folga_consolo >= 0.020
        erros += not ok
        rel.append(dict(ligacao="apoio", peca=it["nome"], inserto=ins_id, com=cand["peca"], tipo=cand["tipo"],
                        dist_mm=round(d * 1000, 1), dz_mm=round(dz * 1000, 1), ok=ok, folga_ponta_mm=round(folga_ponta * 1000), folga_consolo_mm=round(folga_consolo * 1000),
                        z_assento=round(cand["z"], 4)))
# terças: alinhamento entre todas as vigas de mesmo lado (a terça corre em y)
for lado in ("esq", "dir"):
    xs_ref = None
    for it in [i for i in inst if i["nome"].endswith(lado)]:
        xs = [glob[(it["nome"], f"{t}.{k}")][1][0] for k, t in
              ((k, "CH-T2" if any(abs(s - c) < 1e-6 for c in TS["no_contrav"]) else "CH-T1") for k, s in enumerate(TS["tercas"]))]
        if xs_ref is None:
            xs_ref = xs
        dif = max(abs(a - b) for a, b in zip(xs, xs_ref))
        ok = dif <= TOL
        erros += not ok
        rel.append(dict(ligacao="terças", peca=it["nome"], inserto="CH-T1/T2", com=f"linha de terças ({lado})",
                        tipo="Ue 300×85×25×3,00", dist_mm=round(dif * 1000, 1), dz_mm=0.0, ok=ok))
# cotas dos consolos que recebem os dentes (topo inclinado 3%) e topo da I110 abaixo das terças
Z_TOPO_I110 = 8.88
berco = []
for i in (2, 4, 5, 6, 7):
    za, zb = zc(X_PINO[1]), zc(X_PINO[2])
    z_terca = z_fundo_viga(X_PONTA_CEN) + 0.90 + 0.0125                # face inferior da terça junto à I110
    berco.append(dict(linha=i + 1, consolo_esq=za, consolo_dir=zb, desnivel_mm=round((zb - za) * 1000, 1),
                      topo_I110=Z_TOPO_I110, fundo_I110=round(Z_TOPO_I110 - 1.10, 3),
                      folga_topo_I110_tercas_mm=round((z_terca - Z_TOPO_I110) * 1000), ok=z_terca - Z_TOPO_I110 >= 0.05))
erros += sum(not b_["ok"] for b_ in berco)
# contraventamento: nós de painel nas CH-T2 — mesma posição nas duas vigas do vão
paineis = [round(TS["x0"] if False else 0.325 + s, 3) for s in TS["no_contrav"]]
# contraventamento em X Ø16 A36 (padrão das coberturas de referência): cada diagonal vai de nó a nó das vigas TS-01 do vão
# (CH-T2 de uma linha à CH-T2 da linha seguinte), abrangendo 2 espaços de terças; terças dos nós = montantes (escoras).
# CH-T2 com 4 orelhas, simétrica por rotação de 180° (uma só peça): orelhas em s = ±140 mm do eixo da terça (fora da mesa
# de 85 mm e do ST-1) e y = ±140 mm do eixo da viga. As duas diagonais do X cruzam-se no meio do vão, exatamente sobre a
# terça intermediária: uma passa a 45 mm e a outra a 85 mm acima do concreto (furos Ø18 na alma dessa terça, a 35 e 75 mm
# do fundo dela, que fica 10 mm acima do concreto).
CT2 = dict(y_orelha=0.140, s_orelha=0.140, z_baixo=0.045, z_alto=0.085, mesa_terca=0.085, d_tir=0.016, z_fundo_terca=0.010)
VAOS = [(1, 2), (6, 7)]                            # vãos contraventados (2-3 e 7-8, vizinhos aos oitões); CH-T2 mantida em todas as TS-01 (marca única)
tir = []
N_SUB = 1
for (ia, ib) in VAOS:
    for k in range(len(paineis) - 1):
        xa, xb = paineis[k], paineis[k + 1]
        ya, yb = YL[ia] + CT2["y_orelha"], YL[ib] - CT2["y_orelha"]
        for nome, (x1, x2), z in (("/", (xa + CT2["s_orelha"], xb - CT2["s_orelha"]), CT2["z_baixo"]),
                                  ("\\", (xb - CT2["s_orelha"], xa + CT2["s_orelha"]), CT2["z_alto"])):
            fol = CT2["s_orelha"] - CT2["mesa_terca"]          # pior lado: mesa da terça voltada para a orelha
            xm = (xa + xb) / 2
            t = (xm - x1) / (x2 - x1)
            tir.append(dict(vao=f"L{ia+1}-L{ib+1}", painel=k + 1, diagonal=nome,
                            comp_m=round(math.dist((x1, ya), (x2, yb)), 3),
                            ang_eixo_viga=round(math.degrees(math.atan2(yb - ya, abs(x2 - x1))), 1),
                            folga_terca_no_mm=round(fol * 1000), furo_terca_interm=dict(y_m=round(ya + t * (yb - ya) - YL[ia], 3),
                                                                                       h_mm=round((z - CT2["z_fundo_terca"]) * 1000))))
gap_cruz = (CT2["z_alto"] - CT2["z_baixo"] - CT2["d_tir"]) * 1000
furo_min = min(t["furo_terca_interm"]["h_mm"] for t in tir) - 9          # borda do furo Ø18 ao fundo da terça
ok_tir = all(t["folga_terca_no_mm"] >= 20 for t in tir) and gap_cruz >= 5 and furo_min >= 20
erros += not ok_tir
z_telha = lambda x: z_fundo_viga(x) + (0.90 + 0.0125 + 0.30 + 0.03) * math.cos(math.atan(I))
folga_plat = dict(platibanda=10.00, telha_P2=round(z_telha(X_P2 - 0.30), 3), telha_P1=round(z_telha(0.30), 3),
                  folga_P2_mm=round((10.00 - z_telha(X_P2 - 0.30)) * 1000), ok=10.00 - z_telha(X_P2 - 0.30) >= 0.10)
erros += not folga_plat["ok"]
res = dict(tol_mm=TOL * 1000, erros=erros, platibanda=folga_plat, Z0_TS=Z0_TS, L_TS=TS["L"], passo_tercas=PASSO_T, s_tercas=TS["tercas"], X_PINO=[round(v, 3) for v in X_PINO],
           TB1_s_fabricacao=[i_["s"] for i_ in TS["insertos"] if i_["tipo"] == "TB-1"], contraventamento=dict(chapa=CT2, n_tirantes=len(tir), subpaineis=N_SUB, amostra=tir[:4], borda_furo_fundo_terca_mm=furo_min,
           folga_min_terca_mm=min(t["folga_terca_no_mm"] for t in tir), comp_max_m=max(t["comp_m"] for t in tir),
           folga_cruzamento_mm=gap_cruz, ok=ok_tir), apoios=rel[:28], tercas=[r for r in rel if r["ligacao"] == "terças"],
           berco_I110=berco, nos_contraventamento_x_esq=paineis,
           alcas=TS["alcas"], estoque=TS["estoque"])
(AQUI / "ligacoes.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
print("erros:", erros)
print("contraventamento:", json.dumps(res["contraventamento"], ensure_ascii=False)[:900])
for r in rel[:4] + rel[-2:]:
    print(r)
print("berço:", berco[0])
print("nós de contraventamento (x global, meia água esquerda):", paineis)
