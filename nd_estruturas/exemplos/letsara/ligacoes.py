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


# rev03 (Nathan, 13–14/10/2026): terças a cada 1,20 m; telha zipada trapezoidal 0,65 (480 × 70) + lã de rocha 40 mm +
# telha inferior TP40 0,50; painéis solares em toda a cobertura; folga ≥ 15 cm do topo do painel ao topo da platibanda (+10,00);
# TS-01 sem dentes: apoiada no assento do pilar lateral (30 cm, recuo da cabeça) e no topo da I130 / pilares centrais.
PLATIBANDA = 10.00
FOLGA_PLAT = 0.15
PACOTE = dict(tp40=0.040, espacador_la=0.040, zipada=0.070, painel_solar=0.110)   # m acima do topo da terça (painel: grampo + trilho + módulo)
H_TS, H_TERCA, Z_TERCA = 0.90, 0.30, 0.010             # terça 10 mm acima do concreto (suporte ST-1P)
X_PONTA_ESQ = 0.025                                     # ponta a 25 mm da face da cabeça do P1 (x = 0); assento 0 → 0,30
X_PONTA_CEN = X_CEN - 0.0375                            # 75 mm entre as pontas das duas TS-01 sobre a I130 (b = 40)
X_FIM = X_P2 - X_PONTA_ESQ                              # ponta da TS-01 direita (face da cabeça do P2)
NEO_EXT = dict(x=0.200, y=0.300, e=0.010, xc=X_PONTA_ESQ + 0.140)        # neoprene no assento do pilar lateral
NEO_CEN = dict(x=0.100, y=0.300, e=0.010, xc=X_PONTA_CEN - 0.0775)       # neoprene no topo da I130 / pilar central (x 19,585 → 19,685)
H_PAC = H_TS + Z_TERCA + H_TERCA + sum(PACOTE.values())
# cargas da cobertura (kN/m²) — rev03; pesos de catálogo usuais (conferir com os fornecedores da telha e dos painéis)
CARGAS_COB = dict(zipada_065=0.065, la_rocha_40=0.025, tp40_050=0.048, espacadores_fixacoes=0.020, paineis_solares=0.150,
                  instalacoes=0.100, sobrecarga=0.25)
CARGAS_COB["g_total_sem_terca"] = round(sum(v for k, v in CARGAS_COB.items() if k != "sobrecarga"), 3)
CARGAS_COB["g_favoravel_sucao"] = round(CARGAS_COB["zipada_065"] + CARGAS_COB["la_rocha_40"] + CARGAS_COB["tp40_050"] + CARGAS_COB["espacadores_fixacoes"], 3)
Z0_TS = math.floor((PLATIBANDA - FOLGA_PLAT - H_PAC / math.cos(math.atan(I)) - I * X_FIM) * 200) / 200     # arredonda para baixo (5 mm)


def z_fundo_viga(x):            # fundo da TS-01 montada (x a partir do eixo do P1)
    return Z0_TS + I * x


# ------------------------------------------------------------------ TS-01 (coordenadas locais, m)
L_TS = round((X_PONTA_CEN - X_PONTA_ESQ) / math.cos(math.atan(I)), 3)
N_ESP = math.ceil((L_TS - 2 * 0.255) / 1.20 - 1e-9)
PASSO_T = round((L_TS - 2 * 0.255) / N_ESP, 3)
TS = dict(L=L_TS, alcas=[2.10, 7.60], estoque=[2.10],
          tercas=[round(0.255 + PASSO_T * k, 3) for k in range(N_ESP + 1)], no_contrav=[round(0.255 + 2 * PASSO_T * k, 3) for k in range(N_ESP // 2 + 1)])
TS["alcas"] += [round(TS["L"] - a, 3) for a in reversed(TS["alcas"])]
TS["estoque"] += [round(TS["L"] - 2.10, 3)]
TS["insertos"] = (
    [dict(id=f"{'ST-2' if any(abs(s - c) < 1e-6 for c in TS['no_contrav']) else 'ST-1'}.{k}",
          tipo="ST-2" if any(abs(s - c) < 1e-6 for c in TS["no_contrav"]) else "ST-1", s=s, n=0.0, h=0.90)
     for k, s in enumerate(TS["tercas"])] +
    [dict(id=f"AL-1.{k}", tipo="AL-1", s=s, n=0.0, h=0.90) for k, s in enumerate(TS["alcas"])])


def ts_global(x0, y, ins):
    """TS-01 montada com caimento de 3% (sobe com x). Ponta inicial em x0."""
    c, sn = 1 / math.sqrt(1 + I ** 2), I / math.sqrt(1 + I ** 2)
    xb = x0 + ins["s"] * c                      # ponto no fundo
    return (xb - ins["h"] * sn, y + ins["n"], z_fundo_viga(xb) + ins["h"] * c)


# ------------------------------------------------------------------ instâncias
inst = []
for i in range(1, 8):
    inst.append(dict(peca="TS-01", nome=f"TS-01 L{i+1} esq", x0=X_PONTA_ESQ, y=YL[i]))
    inst.append(dict(peca="TS-01", nome=f"TS-01 L{i+1} dir", x0=2 * X_CEN - X_PONTA_CEN, y=YL[i]))
glob = {}
for it in inst:
    for ins in TS["insertos"]:
        glob[(it["nome"], ins["id"])] = (ins["tipo"], ts_global(it["x0"], it["y"], ins))

# apoios sem dente: assento (topo inclinado 3 %) = fundo da viga − neoprene, sob o centro do neoprene
assento = lambda x: round(z_fundo_viga(x) - NEO_EXT["e"], 4)
apoios = dict(P1=dict(x_neo=NEO_EXT["xc"], z=assento(NEO_EXT["xc"]), comp_apoio=round(0.30 - X_PONTA_ESQ, 3)),
              P2=dict(x_neo=X_P2 - NEO_EXT["xc"], z=assento(X_P2 - NEO_EXT["xc"]), comp_apoio=round(0.30 - X_PONTA_ESQ, 3)),
              centro_esq=dict(x_neo=NEO_CEN["xc"], z=assento(NEO_CEN["xc"]), comp_apoio=round(X_PONTA_CEN - (X_CEN - 0.20), 4)),
              centro_dir=dict(x_neo=2 * X_CEN - NEO_CEN["xc"], z=assento(2 * X_CEN - NEO_CEN["xc"])))
REC = (round(z_fundo_viga(0.15) - NEO_EXT["e"], 3), round(z_fundo_viga(X_P2 - 0.15) - NEO_EXT["e"], 3))   # recuo (assento) dos pilares P1 / P2 no eixo do assento
Z_TOPO_I130 = round(z_fundo_viga(X_CEN) - NEO_CEN["e"], 3)          # topo da I130 e dos pilares P8A/P11/P13 no eixo C (topo inclinado 3 %)
H_I130, HD_I130, NEO_I130 = 1.30, 0.78, 0.03                       # viga central I130 (rev03): dente 78 × 35 nos consolos CP-I130
Z_ASS_I130 = round(Z_TOPO_I130 - H_I130 + (H_I130 - HD_I130) - NEO_I130, 3)   # assento do consolo CP-I130 (fundo do dente − neoprene)
rel, erros = [], 0
for it in inst:
    x_ini = it["x0"]; x_fim = it["x0"] + TS["L"] * math.cos(math.atan(I))
    for lado, xp, face in (("ext", x_ini if it["nome"].endswith("esq") else x_fim, 0.0 if it["nome"].endswith("esq") else X_P2),
                           ("cen", x_fim if it["nome"].endswith("esq") else x_ini, X_CEN)):
        folga = abs(xp - face) if lado == "ext" else abs(xp - X_CEN)
        comp = (0.30 - folga) if lado == "ext" else (0.20 - folga)
        ok = folga >= 0.020 and comp >= (0.25 if lado == "ext" else 0.15)
        erros += not ok
        rel.append(dict(ligacao="apoio", peca=it["nome"], ponta=lado, folga_mm=round(folga * 1000), apoio_mm=round(comp * 1000), ok=ok))
# terças: alinhamento entre todas as vigas de mesmo lado (a terça corre em y)
for lado in ("esq", "dir"):
    xs_ref = None
    for it in [i for i in inst if i["nome"].endswith(lado)]:
        xs = [glob[(it["nome"], ins["id"])][1][0] for ins in TS["insertos"] if ins["tipo"] in ("ST-1", "ST-2")]
        if xs_ref is None:
            xs_ref = xs
        dif = max(abs(a - b) for a, b in zip(xs, xs_ref))
        ok = dif <= TOL
        erros += not ok
        rel.append(dict(ligacao="terças", peca=it["nome"], com=f"linha de terças ({lado})", dist_mm=round(dif * 1000, 1), ok=ok))
berco = []
# contraventamento: nós de painel nas CH-T2 — mesma posição nas duas vigas do vão
paineis = [round(X_PONTA_ESQ + s * math.cos(math.atan(I)), 3) for s in TS["no_contrav"]]
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
z_topo = lambda x: z_fundo_viga(x) + H_PAC * math.cos(math.atan(I))
folga_plat = dict(platibanda=PLATIBANDA, pacote_m=round(H_PAC, 3), pacote=PACOTE, topo_painel_P2=round(z_topo(X_FIM), 3), topo_painel_P1=round(z_topo(X_PONTA_ESQ), 3),
                  folga_P2_mm=round((PLATIBANDA - z_topo(X_FIM)) * 1000), ok=PLATIBANDA - z_topo(X_FIM) >= FOLGA_PLAT - 1e-6)
erros += not folga_plat["ok"]
res = dict(tol_mm=TOL * 1000, erros=erros, platibanda=folga_plat, Z0_TS=Z0_TS, L_TS=TS["L"], passo_tercas=PASSO_T, s_tercas=TS["tercas"],
           X_PONTA_ESQ=X_PONTA_ESQ, X_PONTA_CEN=X_PONTA_CEN, apoios_ts=apoios, REC=REC, Z_TOPO_I130=Z_TOPO_I130, Z_ASS_I130=Z_ASS_I130, H_I130=H_I130, HD_I130=HD_I130, cargas_cob=CARGAS_COB, NEO_EXT=NEO_EXT, NEO_CEN=NEO_CEN,
           contraventamento=dict(chapa=CT2, n_tirantes=len(tir), subpaineis=N_SUB, amostra=tir[:4], borda_furo_fundo_terca_mm=furo_min,
           folga_min_terca_mm=min(t["folga_terca_no_mm"] for t in tir), comp_max_m=max(t["comp_m"] for t in tir),
           folga_cruzamento_mm=gap_cruz, ok=ok_tir), apoios=[r for r in rel if r["ligacao"] == "apoio"], tercas=[r for r in rel if r["ligacao"] == "terças"],
           berco_I130=berco, nos_contraventamento_x_esq=paineis,
           alcas=TS["alcas"], estoque=TS["estoque"])
(AQUI / "ligacoes.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
print("erros:", erros)
print("contraventamento:", json.dumps(res["contraventamento"], ensure_ascii=False)[:900])
for r in rel[:4] + rel[-2:]:
    print(r)
print("apoios:", apoios, "REC", REC, "I130", Z_TOPO_I130)
print("nós de contraventamento (x global, meia água esquerda):", paineis)
