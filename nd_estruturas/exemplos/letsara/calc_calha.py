"""Letsara rev06 — calha de platibanda do eixo A (lado baixo da cobertura de uma água, 3 %), descidas, extravasores e
suportes. NBR 10844:1989 (instalações prediais de águas pluviais).

Geometria (DEC-025): a 1ª terça fica com 40 cm livres entre a face da cabeça dos pilares P1 (x = 0) e a aba superior
da terça (alma em x = 0,49 m). A calha corre ao longo do eixo A (79,35 m), entre a cabeça dos pilares/placas e a 1ª
terça; a telha entra na calha com pingadeira. Saídas junto aos pilares P1 das 9 linhas (descida ao lado do pilar,
fora da TS-01). Unidades: m, L/s, kN.
"""
import json, math
from pathlib import Path
AQ = Path(__file__).parent
LG = json.loads((AQ / "ligacoes.json").read_text(encoding="utf-8"))
from geometria import Y_LIN, X_EIXO

R = {}
# ------------------------------------------------------------------ chuva de projeto (NBR 10844:1989 5.1.2 e tabela 5)
I_MMH = 200.0          # mm/h, T = 5 anos, duração 5 min — ordem das capitais do Sul na tabela 5 (CONFIRMAR para a cidade da obra)
T_RET = 5
# ------------------------------------------------------------------ área de contribuição (5.2, fig. 2: superfície inclinada)
B_COB = X_EIXO["E"]                                  # largura em planta da água (m)
H_COB = 0.03 * B_COB                                 # desnível A → E
A_m = B_COB + H_COB / 2                              # m² por metro de calha
Q_m = I_MMH * A_m / 60                               # L/min por metro de calha (5.3: Q = I·A/60)
# saídas junto aos pilares das 9 linhas: cada trecho de calha escoa para a saída mais próxima (metade do vão de cada lado)
vaos = [Y_LIN[k + 1] - Y_LIN[k] for k in range(len(Y_LIN) - 1)]
Lmax_lado = max(vaos) / 2
Q_lado = Q_m * Lmax_lado / 60                        # L/s que chega a uma saída por um lado
Q_saida = 2 * Q_lado                                 # saída interna recebe dos dois lados
# ------------------------------------------------------------------ calha retangular (5.5.5 a 5.5.7: Manning-Strickler)
B_CALHA, H_CALHA, H_AGUA = 0.300, 0.150, 0.100       # largura, altura, lâmina de projeto (folga 50 mm)
I_CALHA = 0.005                                      # 0,5 % (mínimo da norma para calha de beiral/platibanda)
N_MAN = 0.011                                        # tabela 2: aço galvanizado / metal liso
A_mol, P_mol = B_CALHA * H_AGUA, B_CALHA + 2 * H_AGUA
RH = A_mol / P_mol
Q_calha = 60000 * A_mol / N_MAN * RH ** (2 / 3) * I_CALHA ** 0.5 / 60     # L/s (Q = K·S/n·RH^(2/3)·i^(1/2), K = 60 000, L/min)
uso_calha = Q_lado / Q_calha
# ------------------------------------------------------------------ descidas (condutores verticais, 5.6) — saída como orifício
# a favor da segurança (sem funil): Q = Cd·A·√(2gH), H = lâmina na calha; Ø 200 mm em cada linha, saída fora da TS-01
D_DESC = 0.200
Cd = 0.60
Q_desc = Cd * math.pi * D_DESC ** 2 / 4 * math.sqrt(2 * 9.81 * H_AGUA) * 1000
uso_desc = Q_saida / Q_desc
# extravasores: 1 em cada ponta da calha (fachadas 1 e 9), Ø 100 através da placa, 50 mm abaixo da borda da calha
# ------------------------------------------------------------------ suportes da calha (SC-1): ferro chato 38 × 6,35 A36 a cada 0,75 m,
# em balanço a partir da alma da 1ª terça (2 M10 na alma), calha cheia + chapa
G_CALHA, Q_AGUA = 0.12, B_CALHA * H_CALHA * 10.0     # kN/m
S_SUP = 0.75
BRACO = 0.49 - 0.02 - B_CALHA / 2                    # da alma da 1ª terça ao centro da calha
Md = (1.4 * G_CALHA + 1.4 * Q_AGUA) * S_SUP * BRACO
W_fc = 6.35 * 38 ** 2 / 6 / 1e9                       # m³ (chapa em pé, flexão no plano)
MRd = W_fc * 250e3 / 1.10
R.update(chuva=dict(I_mm_h=I_MMH, T_anos=T_RET, obs="NBR 10844:1989 tab. 5 — confirmar a intensidade da cidade da obra"),
         contribuicao=dict(A_por_m_m2=round(A_m, 2), Q_L_min_m=round(Q_m, 1), L_max_ate_saida_m=round(Lmax_lado, 3), Q_lado_L_s=round(Q_lado, 2),
                           Q_saida_L_s=round(Q_saida, 2), area_total_m2=round(A_m * Y_LIN[-1], 0)),
         calha=dict(secao=f"retangular {B_CALHA*1000:.0f} × {H_CALHA*1000:.0f} mm, chapa de aço galvanizado 1,25 mm (#18) com pintura eletrostática",
                    i=I_CALHA, n=N_MAN, lamina_m=H_AGUA, Q_cap_L_s=round(Q_calha, 1), uso=round(uso_calha, 3), L_m=Y_LIN[-1],
                    espaco_livre_m=0.40, posicao="x de +0,02 a +0,32 m do eixo A (face da cabeça do P1 em x = 0; aba da 1ª terça em x = 0,40)"),
         descidas=dict(n=len(Y_LIN), d_mm=D_DESC * 1000, Q_cap_L_s=round(Q_desc, 1), uso=round(uso_desc, 3),
                       onde="uma por linha (1 a 9), ao lado do pilar P1 (y = linha + 0,35 m, fora da TS-01), aparente na face lateral do pilar, até a caixa de areia"),
         extravasores=dict(n=2, d_mm=100, onde="pontas da calha nas fachadas 1 e 9, através da placa, 50 mm abaixo da borda"),
         suportes=dict(peca="SC-1 ferro chato 38 × 6,35 A36 galvanizado, dobrado em U, preso na alma da 1ª terça com 2 M10", s_m=S_SUP, n=math.ceil(Y_LIN[-1] / S_SUP) + 1,
                       Md_kNm=round(Md, 3), MRd_kNm=round(MRd, 3), uso=round(Md / MRd, 3)),
         carga_na_1a_terca=dict(G_kN_m=G_CALHA, Q_kN_m=round(Q_AGUA, 3), obs="aplicada na linha de terças 0 do modelo integrado"),
         rufos=["RF-1 rufo de capa da platibanda (topo +10,00) com pingadeira dos dois lados, sobre as cabeças dos pilares e as placas",
                "RF-2 rufo de fechamento entre a face interna das placas (x = −0,30) e a borda de trás da calha, nos trechos entre pilares do eixo A",
                "RF-3 rufo de encosto do lado alto (eixo E): fixado na face das cabeças/placas, cobre a telha 150 mm",
                "RF-4 rufo lateral nas fachadas 1 e 9 (encosto da telha na platibanda ao longo da água)",
                "pingadeira da telha entrando 100 mm na calha (telha avança 150 mm além da aba da 1ª terça)"])
assert uso_calha <= 1 and uso_desc <= 1 and Md <= MRd, R
(AQ / "calha.json").write_text(json.dumps(R, indent=1, ensure_ascii=False), encoding="utf-8")
if __name__ == "__main__":
    print(json.dumps(R, indent=1, ensure_ascii=False))
