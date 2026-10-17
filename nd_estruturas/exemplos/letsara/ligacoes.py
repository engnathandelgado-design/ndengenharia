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
NEO_EXT = dict(x=0.200, y=0.300, e=0.010, xc=X_PONTA_ESQ + 0.125)        # neoprene no assento do pilar lateral (rev04: centro a 12,5 cm da ponta)
PINO_TS = 0.0775                                                         # rev04: pinos a 7,75 cm da ponta nos 4 apoios (TS-01 simétrica: uma marca serve aos dois lados)
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
# rev06 (Nathan, 17/10/2026): 1ª terça do lado baixo (eixo A) com 40 cm livres entre a face da cabeça do pilar e a aba da
# terça, para a calha; no lado alto (eixo E) a última terça fica a 21,5 cm da cabeça do P2 (≥ 15 cm pedidos; mais perto, a
# última terça da meia água esquerda bateria na cabeça do pilar C das fachadas). Número ÍMPAR de espaços (15, c/ ≈ 1,263 m)
# para os pilares B e D das fachadas caírem entre duas terças (com 16 espaços a terça do meio cai sobre eles — DEC-025).
S0_TERCA = round((0.400 + 0.090 + 0.027 - X_PONTA_ESQ) / math.cos(math.atan(I)), 3)   # alma a 0,49 m do eixo A (aba sup. 90 para A)
S1_TERCA = round(L_TS - 0.255, 3)
N_ESP = 15
PASSO_T = round((S1_TERCA - S0_TERCA) / N_ESP, 4)
IDX_NOS_X = [0, 8, N_ESP]                                # nós do X (DEC-024/025): painéis de 8 e 7 espaços
TS = dict(L=L_TS, alcas=[2.10, 7.60], estoque=[2.10],
          tercas=[round(S0_TERCA + PASSO_T * k, 4) for k in range(N_ESP + 1)])
TS["no_contrav"] = [TS["tercas"][i] for i in IDX_NOS_X]
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

# rev04 (NBR 9062:2017 7.2.1.6: aparelho de apoio horizontal; face inclinada da peça → detalhe que deixe o aparelho horizontal):
# cada ponta da TS-01 tem uma CUNHA rebaixada no fundo (fôrma com calço em cunha 3 %, 0 → 9 mm em 30 cm), que deixa a face de
# apoio HORIZONTAL na posição montada; os assentos (recuo dos pilares, topo da I130 e dos pilares centrais) são horizontais.
#   ponta baixa (lado A da peça): plano horizontal pelo fundo a 30 cm da ponta → cunha de 9 mm na ponta, 0 a 30 cm;
#   ponta alta (lado E da peça): plano horizontal pelo fundo na ponta → 0 na ponta, 9 mm a 30 cm (degrau de 9 mm para o fundo).
# As duas TS-01 da linha são a mesma marca; sobre a I130 a ponta alta da esquerda e a ponta baixa da direita ficam em níveis
# diferentes → topo da I130 e dos pilares centrais em DOIS NÍVEIS (degrau no eixo C).
CUNHA = 0.30
DEGRAU_CUNHA = round(I * CUNHA, 4)
face_baixa = lambda x_ponta: round(z_fundo_viga(x_ponta + CUNHA), 4)       # x_ponta = ponta baixa (menor x)
face_alta = lambda x_ponta: round(z_fundo_viga(x_ponta), 4)                # x_ponta = ponta alta (maior x)
X_PONTA_DIR = 2 * X_CEN - X_PONTA_CEN
REC = (round(face_baixa(X_PONTA_ESQ) - NEO_EXT["e"], 3), round(face_alta(X_FIM) - NEO_EXT["e"], 3))   # recuo (assento horizontal) P1 / P2
Z_TOPO_I130 = round(face_alta(X_PONTA_CEN) - NEO_CEN["e"], 3)               # topo da I130 / P8A / P11 / P13 — metade do lado A (x < C)
Z_TOPO_I130_DIR = round(face_baixa(X_PONTA_DIR) - NEO_CEN["e"], 3)          # metade do lado E (x > C)
DEGRAU_C = round(Z_TOPO_I130_DIR - Z_TOPO_I130, 4)
apoios = dict(P1=dict(x_neo=NEO_EXT["xc"], z=REC[0], comp_apoio=round(0.30 - X_PONTA_ESQ, 3), assento="horizontal"),
              P2=dict(x_neo=X_P2 - NEO_EXT["xc"], z=REC[1], comp_apoio=round(0.30 - X_PONTA_ESQ, 3), assento="horizontal"),
              centro_esq=dict(x_neo=NEO_CEN["xc"], z=Z_TOPO_I130, comp_apoio=round(X_PONTA_CEN - (X_CEN - 0.20), 4), assento="horizontal"),
              centro_dir=dict(x_neo=2 * X_CEN - NEO_CEN["xc"], z=Z_TOPO_I130_DIR, assento="horizontal"))
# conferência: neoprenes dentro do trecho da cunha nas duas pontas
assert NEO_EXT["xc"] + NEO_EXT["x"] / 2 - X_PONTA_ESQ <= CUNHA and X_PONTA_CEN - (NEO_CEN["xc"] - NEO_CEN["x"] / 2) <= CUNHA
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
# contraventamento em X Ø16 A36 — rev05 (DEC-024, modelo integrado r05): X nos 5 vãos do pavilhão (4-5 a 8-9), painel de
# 8 espaços de terças (nós nas terças 0, 8 e 16 de cada meia água: eixos A, ≈B, C, ≈D, E), diagonal a ≈45°. Cada diagonal vai
# da orelha OR-X de um nó à orelha do nó seguinte na outra viga (TS-01 ou VB do eixo 9) e atravessa as 7 terças intermediárias
# do painel por furos oblongos na alma (as duas diagonais do painel: '/' a 45 e '\' a 85 mm do concreto). Terças dos nós = escoras.
# Orelhas em s = ±140 mm do eixo da terça do nó e y = ±140 mm do eixo da viga (na VB do eixo 9: y = 0, ver COB02).
CT2 = dict(y_orelha=0.140, s_orelha=0.140, z_baixo=0.045, z_alto=0.085, mesa_terca=0.085, d_tir=0.016, z_fundo_terca=0.010)
PAINEL_X = 8                                        # espaços do 1º painel (o 2º tem N_ESP − 8 = 7)
VAOS = [(k, k + 1) for k in (3, 4, 5, 6, 7)]       # vãos contraventados 4-5 a 8-9 (índices das linhas); ES-2 em todas as TS-01 (marca única)
nos_x = paineis                                    # rev06: paineis = os 3 nós do X
x_ter = [round(X_PONTA_ESQ + s * math.cos(math.atan(I)), 3) for s in TS["tercas"]]
tir = []
N_SUB = 1
for (ia, ib) in VAOS:
    y_or_b = 0.0 if ib == len(YL) - 1 else CT2["y_orelha"]          # VB do eixo 9: orelha no eixo da VB
    for k in range(len(nos_x) - 1):
        xa, xb = nos_x[k], nos_x[k + 1]
        ya, yb = YL[ia] + CT2["y_orelha"], YL[ib] - y_or_b
        s_b = 0.200 if ib == len(YL) - 1 else CT2["s_orelha"]       # VB do eixo 9: orelha a ±200 da terça (ES-2V fora das ES-1V)
        for nome, (x1, x2), z in (("/", (xa + CT2["s_orelha"], xb - s_b), CT2["z_baixo"]),
                                  ("\\", (xb - CT2["s_orelha"], xa + s_b), CT2["z_alto"])):
            fol = CT2["s_orelha"] - CT2["mesa_terca"]          # pior lado: mesa da terça voltada para a orelha
            furos = []
            for xt in x_ter:
                if min(xa, xb) + 0.01 < xt < max(xa, xb) - 0.01:
                    t = (xt - x1) / (x2 - x1)
                    furos.append(dict(x_m=xt, y_m=round(ya + t * (yb - ya) - YL[ia], 3)))
            tir.append(dict(vao=f"L{ia+1}-L{ib+1}", painel=k + 1, diagonal=nome,
                            comp_m=round(math.dist((x1, ya), (x2, yb)), 3),
                            ang_eixo_viga=round(math.degrees(math.atan2(yb - ya, abs(x2 - x1))), 1),
                            folga_terca_no_mm=round(fol * 1000), h_furo_mm=round((z - CT2["z_fundo_terca"]) * 1000), furos=furos,
                            furo_terca_interm=dict(y_m=furos[len(furos) // 2]["y_m"], h_mm=round((z - CT2["z_fundo_terca"]) * 1000))))
gap_cruz = (CT2["z_alto"] - CT2["z_baixo"] - CT2["d_tir"]) * 1000
furo_min = min(t["furo_terca_interm"]["h_mm"] for t in tir) - 9          # borda do furo Ø18 ao fundo da terça
ok_tir = all(t["folga_terca_no_mm"] >= 20 for t in tir) and gap_cruz >= 5 and furo_min >= 20
erros += not ok_tir
z_topo = lambda x: z_fundo_viga(x) + H_PAC * math.cos(math.atan(I))
folga_plat = dict(platibanda=PLATIBANDA, pacote_m=round(H_PAC, 3), pacote=PACOTE, topo_painel_P2=round(z_topo(X_FIM), 3), topo_painel_P1=round(z_topo(X_PONTA_ESQ), 3),
                  folga_P2_mm=round((PLATIBANDA - z_topo(X_FIM)) * 1000), ok=PLATIBANDA - z_topo(X_FIM) >= FOLGA_PLAT - 1e-6)
erros += not folga_plat["ok"]
res = dict(tol_mm=TOL * 1000, erros=erros, platibanda=folga_plat, Z0_TS=Z0_TS, L_TS=TS["L"], passo_tercas=PASSO_T, s_tercas=TS["tercas"],
           X_PONTA_ESQ=X_PONTA_ESQ, X_PONTA_CEN=X_PONTA_CEN, apoios_ts=apoios, REC=REC, Z_TOPO_I130=Z_TOPO_I130, Z_TOPO_I130_DIR=Z_TOPO_I130_DIR, DEGRAU_C=DEGRAU_C, CUNHA=CUNHA, DEGRAU_CUNHA=DEGRAU_CUNHA, PINO_TS=PINO_TS, Z_ASS_I130=Z_ASS_I130, H_I130=H_I130, HD_I130=HD_I130, cargas_cob=CARGAS_COB, NEO_EXT=NEO_EXT, NEO_CEN=NEO_CEN,
           contraventamento=dict(chapa=CT2, n_tirantes=len(tir), subpaineis=N_SUB, amostra=tir[:4], tirantes=tir, borda_furo_fundo_terca_mm=furo_min,
           folga_min_terca_mm=min(t["folga_terca_no_mm"] for t in tir), comp_max_m=max(t["comp_m"] for t in tir),
           folga_cruzamento_mm=gap_cruz, ok=ok_tir), apoios=[r for r in rel if r["ligacao"] == "apoio"], tercas=[r for r in rel if r["ligacao"] == "terças"],
           berco_I130=berco, nos_contraventamento_x_esq=paineis, idx_nos_x=IDX_NOS_X, x_tercas_esq=x_ter, painel_x=PAINEL_X, vaos_x=[ia for ia, _ in VAOS], nos_x_esq=nos_x,
           alcas=TS["alcas"], estoque=TS["estoque"])
(AQUI / "ligacoes.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
print("erros:", erros)
print("contraventamento:", json.dumps(res["contraventamento"], ensure_ascii=False)[:900])
for r in rel[:4] + rel[-2:]:
    print(r)
print("apoios:", apoios, "REC", REC, "I130", Z_TOPO_I130)
print("nós de contraventamento (x global, meia água esquerda):", paineis)
