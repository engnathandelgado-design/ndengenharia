"""Letsara rev06c — acabamentos da cobertura no sistema Isoeste "zipada dupla com lã de rocha" (manual de
instalação da zipada, p. 28–47): pacote, rufos, fixações e quantitativos. Geometria única para a prancha ND-LET-COB04 e o IFC.

Bordas da cobertura (água única de 3 %, do eixo A ao eixo E; platibanda +10,00 em todo o perímetro, placas por fora dos pilares):
  eixo A (lado baixo)   calha 300 × 150; zipada com perfil pingadeira PG-1 100 mm dentro da calha; RF-2 da placa à calha entre
                        pilares e RF-2C na face da cabeça dos P1 (manual p. 42 — rufo pingadeira);
  eixo E (lado alto)    zipada termina 60 antes da face das cabeças dos P2; veda-onda + Z do veda-onda + massa; RF-3 rufo de topo
                        liso sobre a zipada até a placa, apoiado na cantoneira CR-1, subindo por baixo da aba do RF-1 (manual p. 40);
                        nos pilares RF-3P até a face da cabeça;
  linhas 1 e 9          rufo de acabamento de borda RB-1 (início) / RB-2 (fim) na última onda da zipada e rufo de acabamento lateral
                        RF-4 até a placa, com contra-rufo RF-4C (manual p. 34 e 37 — fechamento lateral em alvenaria);
  topo da platibanda    rufo chapéu RF-1 sobre as placas e RF-1C sobre as cabeças dos pilares + placa (manual p. 46).
Costura transversal dos rufos: transpasse 200 (100 + 100) com fita Tacky Tape 9,5 e massa vedante, 2 costuras PB 1/4"-14 × 7/8" P01
(manual p. 40–46). Fixação no concreto: PAR Tapper 1/4" × 2 3/4" a cada 500 mm + selante PU (manual p. 34/37).
Unidades: m (global, como o modelo_bim) e mm nas seções.
"""
import json
import math
from pathlib import Path

from geometria import X_EIXO, Y_LIN

AQ = Path(__file__).parent
LG = json.loads((AQ / "ligacoes.json").read_text(encoding="utf-8"))
I = 0.03
LARG, COMP = X_EIXO["E"], Y_LIN[-1]
Z0 = LG["Z0_TS"]
H_TS, Z_TERCA, H_TERCA = 0.90, 0.010, 0.302
PLAT = LG["platibanda"]["platibanda"]                    # +10,00
PAC = dict(tp40=0.040, cartola=0.040, zipada=0.070, painel=0.110)    # m (TP-40 STD, cartola, zipada 455, painel solar)
# faces (m): placas por fora dos pilares (face interna a 0,325 do eixo do pilar), cabeças dos pilares de borda com 0,30 de recuo
X_PLACA_A, X_PLACA_E = -0.325, LARG + 0.325
X_CAB_A, X_CAB_E = 0.0, LARG                             # face das cabeças dos P1 / P2 voltada para a cobertura
Y_PLACA_1, Y_PLACA_9 = -0.325, COMP + 0.325
X_TELHA_A, X_TELHA_E = 0.250, LARG - 0.060               # pontas da zipada (calha / sob o RF-3)
Y_TELHA_1, Y_TELHA_9 = -0.150, COMP + 0.150              # bordas laterais da cobertura (terças passam 0,11 do eixo da VB)
XC0, BC, HC = 0.020, 0.300, 0.150                        # calha (calc_calha.py)


def z_terca_topo(x):
    """topo da terça (face de apoio da TP-40) em x."""
    return Z0 + I * x + H_TS + Z_TERCA + H_TERCA


def z_zip(x):
    """face superior da chapa da zipada (fundo da onda) em x."""
    return z_terca_topo(x) + PAC["tp40"] + PAC["cartola"]


Z_TOP_CALHA = z_terca_topo(X_TELHA_A) - 0.040            # borda da calha 40 mm abaixo da face inferior da TP-40 na ponta
ESP = 0.00050                                            # rev11 (Nathan 26/10): funilaria em galvalume #0,50 (feita na obra pelo funileiro)


def secoes():
    """seções dos rufos no plano normal à borda: lista de (marca, borda, pontos (u, v) em m, descrição)."""
    s = {}
    zA = z_zip(X_TELHA_A)
    # eixo A: RF-2 da placa até a calha (entre pilares) — u = x global, v = z global
    s["RF-2"] = ("A", [(X_PLACA_A, Z_TOP_CALHA + 0.300), (X_PLACA_A, Z_TOP_CALHA + 0.150), (XC0 - 0.010, Z_TOP_CALHA + 0.120), (XC0 - 0.010, Z_TOP_CALHA + 0.060)],
                 "rufo de fechamento placa → calha, entre pilares; aba vertical de 150 na placa com PAR Tapper a cada 500 + PU")
    s["RF-2C"] = ("A", [(X_CAB_A, Z_TOP_CALHA + 0.300), (X_CAB_A, Z_TOP_CALHA + 0.060), (XC0 + 0.010, Z_TOP_CALHA + 0.040)],
                  "contra-rufo na face da cabeça dos P1 (pilares do eixo A), dentro da calha")
    s["PG-1"] = ("A", [(X_TELHA_A + 0.120, zA + 0.002), (X_TELHA_A, zA + 0.002 - I * 0.120), (X_TELHA_A - 0.015, zA - 0.040), (X_TELHA_A - 0.015, zA - 0.100)],
                 "perfil pingadeira sob a ponta da zipada, 100 mm dentro da calha (manual p. 42)")
    # eixo E: zipada termina em X_TELHA_E; RF-3 por cima até a placa (CR-1 de apoio) e RF-3C na placa
    zE = z_zip(X_TELHA_E)
    zr = zE + PAC["zipada"] + 0.010                      # rufo 10 acima da costura da zipada
    s["RF-3"] = ("E", [(X_TELHA_E - 0.210, zE + 0.010), (X_TELHA_E - 0.210, zr), (X_PLACA_E, zr + 0.020), (X_PLACA_E, PLAT - 0.015)],
                 "rufo de topo liso sobre a ponta da zipada (aba de 150 + 60 de borda) até a placa, subindo por baixo da aba interna do RF-1 (85 de transpasse); apoiado na CR-1 (manual p. 40)")
    s["CR-1"] = ("E", [(X_PLACA_E - 0.040, zr - 0.001), (X_PLACA_E, zr - 0.001), (X_PLACA_E, zr - 0.041)],
                 "cantoneira de apoio do RF-3, L 40 × 40 #1,25 galvanizada, na placa com PAR Tapper a cada 500")
    s["RF-3P"] = ("E", [(X_TELHA_E - 0.210, zE + 0.010), (X_TELHA_E - 0.210, zr), (X_CAB_E, zr + 0.005), (X_CAB_E, PLAT - 0.015)],
                  "rufo de topo liso nos pilares P2: até a face da cabeça, por baixo do RF-1C (peça de 600 com cantos dobrados, rebitados e selados)")
    # linhas 1 e 9: u = distância horizontal da placa para dentro (m), v = z; desenhada na linha 1 (y global = Y_PLACA_1 + u)
    zl = z_zip(LARG / 2) + PAC["zipada"]                 # referência no meio da água (a seção sobe 3 % ao longo da borda)
    s["RF-4"] = ("1/9", [(0.0, zl + 0.120), (0.0, zl + 0.030), (Y_TELHA_1 - Y_PLACA_1 + 0.060, zl + 0.012), (Y_TELHA_1 - Y_PLACA_1 + 0.060, zl - 0.020)],
                 "rufo de acabamento lateral, da placa até a última onda da zipada (manual p. 34/37)")
    s["RF-4C"] = ("1/9", [(0.0, zl + 0.170), (0.030, zl + 0.140), (0.030, zl + 0.080)], "contra-rufo lateral na placa, paralelo à água (3 %): PAR Tapper a cada 500 + PU; no último trecho (eixo E) entra sob a aba do RF-1")
    s["RB-1/2"] = ("1/9", [(Y_TELHA_1 - Y_PLACA_1 - 0.020, zl - 0.070), (Y_TELHA_1 - Y_PLACA_1 - 0.020, zl + 0.004), (Y_TELHA_1 - Y_PLACA_1 + 0.080, zl + 0.004)],
                   "rufo de acabamento de borda sobre a última onda (RB-1 no início, RB-2 no fim da montagem)")
    # topo da platibanda: u = da face externa da placa para dentro, v = z
    s["RF-1"] = ("plat", [(-0.020 - 0.015, PLAT - 0.070 - 0.015), (-0.020, PLAT - 0.070), (-0.020, PLAT + 0.012), (0.120, PLAT + 0.005),
                          (0.120, PLAT - 0.100), (0.120, PLAT - 0.100 - 0.015)],
                  "rufo chapéu da platibanda sobre a placa de 10 cm, caimento 5 % para dentro; pingadeira externa dobrada, interna a prumo (5 mm livres da face do pilar; manual p. 46)")
    s["RF-1C"] = ("plat", [(-0.020 - 0.015, PLAT - 0.070 - 0.015), (-0.020, PLAT - 0.070), (-0.020, PLAT + 0.025), (0.445, PLAT + 0.005),
                           (0.445, PLAT - 0.100), (0.445 + 0.015, PLAT - 0.100 - 0.015)],
                   "rufo chapéu sobre a cabeça do pilar + placa (largura 100 + 25 + 300), peça de 600 sobre cada cabeça")
    return s


def desenv(pts):
    return sum(math.dist(a, b) for a, b in zip(pts[:-1], pts[1:]))


def quantitativos():
    S = secoes()
    n_pil_A = len(Y_LIN)                                  # P1 de cada linha (eixo A) e P2 (eixo E)
    perim = 2 * (Y_PLACA_9 - Y_PLACA_1) + 2 * (X_PLACA_E - X_PLACA_A)
    L = {"RF-2": COMP - n_pil_A * 0.40, "RF-2C": n_pil_A * 0.60, "PG-1": COMP - 0.42, "RF-3": COMP - n_pil_A * 0.40,
         "CR-1": COMP - n_pil_A * 0.40, "RF-3P": n_pil_A * 0.60, "RF-4": 2 * (X_TELHA_E - X_TELHA_A) / math.cos(math.atan(I)),
         "RF-4C": 2 * (X_PLACA_E - X_PLACA_A) / math.cos(math.atan(I)), "RB-1/2": 2 * (X_TELHA_E - X_TELHA_A) / math.cos(math.atan(I)),
         "RF-1": perim - 2 * n_pil_A * 0.60, "RF-1C": 2 * n_pil_A * 0.60}
    linhas = []
    for mk, (borda, pts, desc) in S.items():
        d = desenv(pts) * 1000
        comp = L[mk]
        n3 = round(comp / 0.6) if mk in ("RF-2C", "RF-3P", "RF-1C") else math.ceil(comp / 2.8)   # peças de 600 nos pilares; demais de 3 m com 200 de transpasse
        linhas.append(dict(marca=mk, borda=borda, desenv_mm=round(d / 10) * 10 + 10, comprimento_m=round(comp, 1), pecas=n3,
                           chapa="#1,25 galv." if mk == "CR-1" else "galvalume #0,50", descricao=desc))
    # 22/10 (colisão): RF-4P — rufo de recorte em volta das 6 cabeças 40 × 30 dos pilares de fachada (B, C, D das linhas 1 e 9):
    # peça de 600 dobrada nas 3 faces (16 + 42 + 16 cm de contorno), aba de 150 subindo na cabeça + 60 sobre a zipada
    linhas.append(dict(marca="RF-4P", borda="1/9", desenv_mm=210, comprimento_m=round(6 * 0.74, 1), pecas=6, chapa="galvalume #0,50",
                       descricao="rufo de recorte nas cabeças dos pilares de fachada (peça de 600 dobrada nas 3 faces, rebitada e selada)"))
    n_zip = math.ceil((Y_TELHA_9 - Y_TELHA_1) / 0.455)                    # telhas zipadas (455 úteis)
    tapper = math.ceil((L["RF-2"] + L["RF-2C"] + L["CR-1"] + L["RF-3P"] + L["RF-4C"] + L["RF-1"] + L["RF-1C"]) / 0.5)
    costuras = sum(2 * max(l["pecas"] - 1, 0) for l in linhas) + math.ceil((L["RF-3"] + L["RF-4"] + L["PG-1"]) / 0.5)
    acess = [dict(item="veda-onda + Z do veda-onda", uso="ponta alta da zipada (eixo E), 1 por telha", qtd=n_zip),
             dict(item="massa vedante (tubo 25 m)", uso="veda-ondas, costuras e topo dos contra-rufos", qtd=math.ceil((2 * COMP + sum(L.values()) * 0.5) / 25)),
             dict(item="fita Tacky Tape 9,5 (rolo 12 m)", uso="costura transversal dos rufos (transpasse 200)", qtd=math.ceil(sum(max(l['pecas'] - 1, 0) * l['desenv_mm'] / 1000 for l in linhas) / 12) + 1),
             dict(item="PAR Tapper 1/4\" × 2 3/4\" + bucha", uso="rufos e contra-rufos no concreto, a cada 500", qtd=tapper),
             dict(item="PB 1/4\"-14 × 7/8\" P01", uso="costuras dos rufos e da pingadeira", qtd=costuras),
             dict(item="selante PU (sachê 600 ml)", uso="topo dos contra-rufos e encontros com as cabeças", qtd=math.ceil((L["RF-2"] + L["RF-4C"] + 2 * n_pil_A * 1.2) / 12)),
             dict(item="base deslizante #0,80 + perfil cartola especial", uso="bordas laterais (linhas 1 e 9), a cada terça", qtd=2 * 32)]
    return dict(rufos=linhas, acessorios=acess, n_zipadas=n_zip, perimetro_platibanda_m=round(perim, 1))


def x_tercas():
    """linhas de terça (m, alma), mesma regra do cob_comum.XT: 2 meias águas de TS-01."""
    lts = LG["L_TS"] / math.sqrt(1 + I ** 2)
    x0e, x0d = LG["X_PONTA_ESQ"], LARG - LG["X_PONTA_ESQ"] - lts
    return [x0e + s_ - 0.027 for s_ in LG["s_tercas"]] + [x0d + s_ - 0.027 for s_ in LG["s_tercas"]]


def quantitativos_telhas(L_MAX_TP=12.0, TRANSP=0.200, L_CART=3.0, PERDA=0.05):
    """pacote Isoeste — Telha Zipada Dupla com lã de rocha FSR-32 (manual de instalação Kingspan Isoeste, p. 27–28): TP-40 STD 980 #0,65, cartola #0,65, lã FSR 32, clipes e zipada 455 #0,50; líquido e compra."""
    XT = x_tercas()
    fi = 1 / math.cos(math.atan(I))                                 # comprimento na inclinação / projeção
    larg = Y_TELHA_9 - Y_TELHA_1                                    # largura coberta (direção y)
    comp = (X_TELHA_E - X_TELHA_A) * fi                             # comprimento da água
    n_zip = math.ceil(larg / 0.455)
    n_tp = math.ceil(larg / 0.980)                                  # colunas de TP-40 (980 úteis)
    # TP-40: peças ≤ 12 m (transporte) com emenda por transpasse de 200 sempre sobre uma terça
    cortes, x0 = [], X_TELHA_A
    while (X_TELHA_E - x0) * fi > L_MAX_TP - TRANSP:
        x_ok = [x for x in XT if x0 + 1.0 < x and (x - x0) * fi + TRANSP / 2 <= L_MAX_TP]
        cortes.append(x_ok[-1]); x0 = x_ok[-1]
    lims = [X_TELHA_A] + cortes + [X_TELHA_E]
    pecas_tp = [round((b - a) * fi + TRANSP / 2 * ((a != X_TELHA_A) + (b != X_TELHA_E)), 2) for a, b in zip(lims[:-1], lims[1:])]
    nT = len(XT)
    n_cart_lin = math.ceil(larg / L_CART)
    meio = sorted(range(nT), key=lambda k: abs(XT[k] - LARG / 2))[:2]   # clipes fixos nas 2 terças do meio da água
    n_clip = n_zip * nT
    n_fixo = n_zip * len(meio)
    ondas = math.ceil(larg / 0.245)                                 # cristas da TP-40 a cada 245 (costura em TODAS as ondas)
    area = larg * comp
    it = [dict(item="Telha zipada 455 #0,50 pré-pintada (Isoeste)", un="pç", liq=n_zip, compra=n_zip, obs=f"peça única de {comp:.2f} m (perfilada na obra), {n_zip * comp:.0f} m; área {area:.0f} m²"),
          dict(item="Telha TP-40 STD 980 #0,65 (inferior)", un="pç", liq=n_tp * len(pecas_tp), compra=n_tp * len(pecas_tp),
               obs=f"{n_tp} colunas × {len(pecas_tp)} peças ({' + '.join(f'{v:.2f}' for v in pecas_tp)} m), transpasse {TRANSP * 1000:.0f} sobre terça; {n_tp * sum(pecas_tp):.0f} m"),
          dict(item="Perfil cartola #0,65 h 40 (sobre cada terça)", un="pç 3 m", liq=n_cart_lin * nT, compra=n_cart_lin * nT,
               obs=f"{nT} linhas × {larg:.2f} m = {nT * larg:.0f} m; {n_cart_lin} peças de 3 m por linha"),
          dict(item="Perfil cartola especial (bordas laterais, linhas 1 e 9)", un="m", liq=round(2 * comp, 1), compra=math.ceil(2 * comp * (1 + PERDA)), obs="ao longo da água, com as bases deslizantes #0,80"),
          dict(item="Lã de rocha FSR 32 e = 40 (entre cartolas)", un="m²", liq=round(area), compra=math.ceil(area * (1 + PERDA)), obs="painéis entre as cartolas, sem frestas; manter seca"),
          dict(item="Clipe fixo #0,65", un="pç", liq=n_fixo, compra=math.ceil(n_fixo * (1 + PERDA)), obs=f"1 por zipada nas 2 terças do meio da água (x = {XT[meio[0]]:.2f} e {XT[meio[1]]:.2f} m)"),
          dict(item="Clipe deslizante #0,65 + base deslizante", un="cj", liq=n_clip - n_fixo, compra=math.ceil((n_clip - n_fixo) * (1 + PERDA)), obs="1 por zipada nas demais terças; a zipada dilata a partir do ponto fixo (≈ 12 mm em cada ponta para ΔT 50 °C — conferir curso do clipe com a Isoeste)"),
          dict(item='PB 12-14 × 3/4" P03 (TP-40 × terça)', un="pç", liq=n_tp * nT * 4, compra=math.ceil(n_tp * nT * 4 * (1 + PERDA)), obs="4 por telha em cada terça"),
          dict(item='PB 12-14 × 3/4" P03 (clipe × cartola)', un="pç", liq=2 * n_clip, compra=math.ceil(2 * n_clip * (1 + PERDA)), obs="2 por clipe"),
          dict(item='PB 1/4"-14 × 7/8" P01 (cartola × TP-40)', un="pç", liq=ondas * nT, compra=math.ceil(ondas * nT * (1 + PERDA)), obs="costura em TODAS as ondas (sucção de borda — calc_fixacao_telhas)")]
    return dict(itens=it, n_zipadas=n_zip, n_colunas_tp40=n_tp, pecas_tp40_m=pecas_tp, emendas_tp40_x_m=[round(c, 3) for c in cortes],
                n_linhas_terca=nT, x_tercas_m=[round(x, 3) for x in XT], area_m2=round(area, 1), comprimento_agua_m=round(comp, 3),
                largura_m=round(larg, 3), perda=PERDA)


NIVEIS = dict(zip_A=round(z_zip(X_TELHA_A), 3), zip_E=round(z_zip(X_TELHA_E), 3), calha_topo=round(Z_TOP_CALHA, 3),
              platibanda=PLAT, folga_zip_platibanda_E=round(PLAT - z_zip(X_TELHA_E) - PAC["zipada"], 3))

if __name__ == "__main__":
    R = dict(sistema="Isoeste — Telha Zipada Dupla com lã de rocha FSR-32 (manual de instalação Kingspan Isoeste, p. 27–28)", niveis=NIVEIS, **quantitativos(), telhas=quantitativos_telhas(),
             secoes={k: dict(borda=v[0], pts=[(round(a, 4), round(b, 4)) for a, b in v[1]], descricao=v[2]) for k, v in secoes().items()})
    (AQ / "acabamentos_cobertura.json").write_text(json.dumps(R, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(R["niveis"], indent=1), json.dumps(R["rufos"], indent=1, ensure_ascii=False)[:3000])
