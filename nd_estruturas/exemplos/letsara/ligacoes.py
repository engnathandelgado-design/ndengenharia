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
YL = [0.0, 10.05, 19.705, 29.36, 38.865, 48.445, 58.025, 67.605, 76.81]
X_CEN, X_P2 = 20.05, 40.10
NEO = 0.010                     # neoprene


def z_fundo_viga(x):            # fundo da TS-01 montada (x a partir do eixo do P1)
    return 8.08 + I * x


# ------------------------------------------------------------------ TS-01 (coordenadas locais, m)
TS = dict(L=round(19.71 / math.cos(math.atan(I)), 3), ponta_pino=0.15, alcas=[2.10, 7.40], estoque=[2.10],
          tercas=[0.255 + 1.60 * k for k in range(13)], no_contrav=[0.255 + 3.20 * k for k in range(7)])
# chapa da terça: CH-T1 nas terças comuns; CH-T2 (com furos extras do contraventamento) nos nós de painel
TS["alcas"] += [round(TS["L"] - a, 3) for a in reversed(TS["alcas"])]
TS["estoque"] += [round(TS["L"] - 2.10, 3)]
TS["insertos"] = (
    [dict(id=f"TB-1.{k}", tipo="TB-1", s=s, n=0.0, h=0.0) for k, s in enumerate((TS["ponta_pino"], TS["L"] - TS["ponta_pino"]))] +
    [dict(id=f"CH-A1.{k}", tipo="CH-A1", s=s, n=0.0, h=0.0) for k, s in enumerate((TS["ponta_pino"], TS["L"] - TS["ponta_pino"]))] +
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
    inst.append(dict(peca="TS-01", nome=f"TS-01 L{i+1} dir", x0=X_CEN + 0.015, y=YL[i]))
glob = {}
for it in inst:
    for ins in TS["insertos"]:
        glob[(it["nome"], ins["id"])] = (ins["tipo"], ts_global(it["x0"], it["y"], ins))

# apoios das outras peças (coordenadas globais definidas pelo projeto dos pilares/I110)
apoios = []
for i in range(1, 8):
    y = YL[i]
    apoios.append(dict(peca=f"P1 L{i+1}", tipo="PN-1 pino Ø25 no consolo", x=0.475, y=y, z=z_fundo_viga(0.475) - NEO))
    apoios.append(dict(peca=f"P2 L{i+1}", tipo="PN-1 pino Ø25 no consolo", x=X_P2 - 0.475, y=y, z=z_fundo_viga(X_P2 - 0.475) - NEO))
    sup = "topo do pilar" if i in (1, 3) else "berço BR-1 na I110"
    for x in (X_CEN - 0.165, X_CEN + 0.165):
        apoios.append(dict(peca=f"{sup} L{i+1}", tipo="PN-2 pino Ø25 no berço", x=x, y=y, z=z_fundo_viga(x) - NEO))

# ------------------------------------------------------------------ checagens
rel, erros = [], 0
for it in inst:
    for ins_id in ("TB-1.0", "TB-1.1"):
        tipo, (x, y, z) = glob[(it["nome"], ins_id)]
        cand = min(apoios, key=lambda a: math.dist((a["x"], a["y"]), (x, y)))
        d = math.dist((cand["x"], cand["y"]), (x, y)); dz = (z - NEO) - cand["z"]
        ok = d <= TOL and abs(dz) <= 0.003
        erros += not ok
        rel.append(dict(ligacao="apoio", peca=it["nome"], inserto=ins_id, com=cand["peca"], tipo=cand["tipo"],
                        dist_mm=round(d * 1000, 1), dz_mm=round(dz * 1000, 1), ok=ok,
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
# berço inclinado BR-1 na I110: diferença de nível entre os dois assentos da mesma linha
berco = []
for i in (2, 4, 5, 6, 7):
    za, zb = z_fundo_viga(X_CEN - 0.165) - NEO, z_fundo_viga(X_CEN + 0.165) - NEO
    berco.append(dict(linha=i + 1, z_esq=round(za, 4), z_dir=round(zb, 4), desnivel_mm=round((zb - za) * 1000, 1),
                      topo_I110=round(za - 0.020, 3)))
# contraventamento: nós de painel nas CH-T2 — mesma posição nas duas vigas do vão
paineis = [round(TS["x0"] if False else 0.325 + s, 3) for s in TS["no_contrav"]]
# contraventamento Ø12,5 A36 — CH-T2 com 4 orelhas, simétrica por rotação de 180° (uma só peça):
# orelhas em s = ±140 mm do eixo da terça (fora da mesa de 85 mm e da cantoneira) e y = ±140 mm do eixo da viga.
# Uma diagonal corre a 35 mm e a outra a 70 mm acima da chapa (furos na alma da terça intermediária a 35 mm entre centros).
CT2 = dict(y_orelha=0.140, s_orelha=0.140, z_baixo=0.035, z_alto=0.070, mesa_terca=0.085, d_tir=0.0125)
VAOS = [(1, 2), (3, 4), (4, 5), (6, 7)]            # vãos contraventados entre linhas com TS-01 (fachadas: VB)
tir = []
for (ia, ib) in VAOS:
    ya, yb = YL[ia] + CT2["y_orelha"], YL[ib] - CT2["y_orelha"]
    for k in range(len(paineis) - 1):
        xa, xb = paineis[k], paineis[k + 1]
        for nome, (x1, x2), z in (("/", (xa + CT2["s_orelha"], xb - CT2["s_orelha"]), CT2["z_baixo"]),
                                  ("\\", (xb - CT2["s_orelha"], xa + CT2["s_orelha"]), CT2["z_alto"])):
            fol = CT2["s_orelha"] - CT2["mesa_terca"]          # pior lado: mesa da terça voltada para a orelha
            xm = (xa + xb) / 2
            t = (xm - x1) / (x2 - x1)
            tir.append(dict(vao=f"L{ia+1}-L{ib+1}", painel=k + 1, diagonal=nome,
                            comp_m=round(math.dist((x1, ya), (x2, yb)), 3),
                            ang_eixo_viga=round(math.degrees(math.atan2(yb - ya, abs(x2 - x1))), 1),
                            folga_terca_no_mm=round(fol * 1000), furo_terca_interm=dict(y_m=round(ya + t * (yb - ya) - YL[ia], 2),
                                                                                       h_mm=round(z * 1000))))
gap_cruz = (CT2["z_alto"] - CT2["z_baixo"] - CT2["d_tir"]) * 1000
ok_tir = all(t["folga_terca_no_mm"] >= 20 for t in tir) and gap_cruz >= 5
erros += not ok_tir
res = dict(tol_mm=TOL * 1000, erros=erros, contraventamento=dict(chapa=CT2, n_tirantes=len(tir), amostra=tir[:4],
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
