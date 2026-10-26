"""rev11 (26/10/2026, regra do Nathan: placas içadas por 4 pontos numa face): verificação da placa e do inserto IZ-1 na
VERTICALIZAÇÃO e no IÇAMENTO DE PÉ pelos mesmos 4 IZ-1 da desforma (0,104 L e 0,396 L de cada ponta, meia altura, face interna),
com balancim duplo (cargas iguais). Lê placas.json (seção, peso, fctk,j, desforma já verificada). Grava placas_icamento_4p.json.
NBR 9062:2017 5.3.2 (βa 1,3 manuseio/montagem; 3,0 nos dispositivos de içamento) e NBR 6118:2023 (tensões no concreto em serviço)."""
import json
from pathlib import Path
AQ = Path(__file__).parent
P = json.loads((AQ / "placas.json").read_text(encoding="utf-8"))
S, T = P["secao"], P["transitorias"]
b, h, L, pp = S["b_m"], S["h_m"], S["L_max_m"], S["pp_kNm"]          # b = altura da placa (1,25), h = espessura (0,10)
W = pp * L                                                            # kN (maior placa)
BA, BA_DISP = 1.3, 3.0                                                # NBR 9062:2017 5.3.2.2
Pk = W / 4                                                            # balancim duplo: 4 cargas iguais
w = pp * BA
# 4 apoios a 0,104 L e 0,396 L de cada ponta → momentos ≈ ±0,0054 w L² (mesmo coeficiente da desforma; PCI, apoios equivalentes)
M = 0.0054 * w * L ** 2
W_forte = h * b ** 2 / 6                                              # de pé: flexão NO PLANO da placa (eixo forte)
sig_pe = M / W_forte / 1e3                                            # MPa
# verticalização (giro de deitada para de pé com os 4 IZ-1 e o balancim): o momento no eixo fraco cai de M (deitada) a 0 (de pé);
# a pior posição é a inicial, igual à desforma já verificada em placas.json (T["sig_desforma"])
R = dict(norma="NBR 9062:2017 5.3.2 (βa); NBR 6118:2023 17.2.4 / 8.2.5 (fctk,j)",
         peso_kN=round(W, 1), peso_t=round(W / 9.81, 2), Pk_kN=round(Pk, 1), Pd_kN=round(BA * Pk, 1), P_disp_kN=round(BA_DISP * Pk, 1),
         pontos="4 IZ-1 na face interna, 0,104 L e 0,396 L de cada ponta, meia altura; balancim duplo (cargas iguais), cabos a prumo",
         verticalizacao=dict(sig_MPa=T["sig_desforma"], lim_MPa=round(T["fctk_j"] / 1.5, 2), ok=T["sig_desforma"] <= T["fctk_j"] / 1.5,
                             obs="pior posição = placa deitada no início do giro (= desforma com 4 pontos, já verificada)"),
         de_pe=dict(M_kNm=round(M, 2), W_m3=round(W_forte, 4), sig_MPa=round(sig_pe, 3), lim_MPa=round(T["fctk_j"] / 1.5, 2), ok=sig_pe <= T["fctk_j"] / 1.5,
                    obs="de pé a placa trabalha no plano (eixo forte, 1,25 m): tensão desprezível"),
         IZ1=dict(solicitacao_de_pe="cisalhamento (carga paralela à face) + pequena tração pela excentricidade de 5 cm do CG à face",
                  Pk_kN=round(Pk, 1), Pd_kN=round(BA * Pk, 1), trabalho_tracao_kN=12.7,
                  exigencia="cabeçote/olhal universal giratório certificado para carga a 90° com capacidade de trabalho ≥ βa·Pk por ponto (conferir no catálogo do fornecedor do IZ-1)",
                  ok_tracao=BA * Pk <= 12.7))
(AQ / "placas_icamento_4p.json").write_text(json.dumps(R, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(R, indent=1, ensure_ascii=False))
