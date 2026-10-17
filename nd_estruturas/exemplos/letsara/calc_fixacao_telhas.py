"""Letsara rev06c — fixação da cobertura Kingspan Isoeste "zipada dupla com lã de rocha" (manual de instalação, p. 28):
TP-40 STD 980 #0,65 na terça, perfil cartola #0,65 sobre cada terça, lã FSR 32, clipe fixo/deslizante #0,65 e zipada 455 #0,50.

Verifica a sucção do vento (NBR 6123, mesmas pressões da memória MC06) no caminho de forças das fixações:
  zipada → clipe → 2 PB 12-14 × 3/4" na cartola → cartola → costura PB 1/4"-14 × 7/8" na crista da TP-40 → TP-40 → PB 12-14 × 3/4" na terça.
Resistências de parafusos auto-atarraxantes: NBR 14762:2010 10.6 (arrancamento 0,85·t·d·fu e rasgamento 1,5·t·dw·fu, γ = 2,0 —
conferir no texto da norma), como AISI S100-16 J4.4. Valores de catálogo/ensaio do fabricante podem substituir estes.
Unidades: kN, m, mm, MPa.
"""
import json
from pathlib import Path

AQ = Path(__file__).parent
LG = json.loads((AQ / "ligacoes.json").read_text(encoding="utf-8"))
s = LG["passo_tercas"]                        # m, faixa de influência de cada linha de terça
CC = LG["cargas_cob"]
q0 = 0.874                                    # kN/m² (MC06)
cp = dict(geral=-1.0, borda=-1.6)             # Cpe −0,8 / −1,4 + Cpi +0,2 (MC06)
g_fav = CC["g_favoravel_sucao"]               # telhas + lã + cartola (painéis e instalações desprezados)
GQ, GAM = 1.4, 2.0
FU_TELHA, FU_TERCA = 360.0, 480.0             # MPa: aço revestido das telhas (adotado, conferir) e terça METSEC (fu 480)
R = dict(sistema="Kingspan Isoeste zipada dupla com lã de rocha (manual p. 28): TP-40 #0,65 + cartola #0,65 + lã FSR 32 + clipe #0,65 + zipada 455 #0,50",
         q0_kNm2=q0, g_fav_kNm2=g_fav, passo_tercas_m=s)


def arranc(t, d, fu):                          # NBR 14762:2010 10.6 / AISI J4.4.1 — arrancamento (pull-out) da chapa de base
    return 0.85 * t * d * fu / GAM / 1e3


def rasg(t, dw, fu):                           # rasgamento da chapa sob a cabeça/arruela (pull-over)
    return 1.5 * t * dw * fu / GAM / 1e3


lig = {
    "clipe → cartola (PB 12-14 × 3/4\", 2 por clipe)": dict(Rd=min(arranc(0.65, 5.5, FU_TELHA), rasg(0.65, 11.0, FU_TELHA)), n_m=2 / 0.455),
    "cartola → TP-40 (PB 1/4\"-14 × 7/8\" P01, a cada 2 ondas)": dict(Rd=min(arranc(0.65, 6.3, FU_TELHA), rasg(0.65, 11.0, FU_TELHA)), n_m=1 / 0.49),
    "cartola → TP-40 (PB 1/4\"-14 × 7/8\" P01, em todas as ondas)": dict(Rd=min(arranc(0.65, 6.3, FU_TELHA), rasg(0.65, 11.0, FU_TELHA)), n_m=1 / 0.245),
    "TP-40 → terça (PB 12-14 × 3/4\" P03, 4 por telha)": dict(Rd=min(arranc(2.30, 5.5, FU_TERCA), rasg(0.65, 16.0, FU_TELHA)), n_m=4 / 0.98),
}
res = {}
for zona, c in cp.items():
    w = GQ * abs(c) * q0 - g_fav              # kN/m² de cálculo (para cima)
    f_lin = w * s                              # kN/m por linha de terça
    res[zona] = dict(w_d_kNm2=round(w, 3), f_linha_kNm=round(f_lin, 3),
                     ligacoes={k: dict(F_kN=round(f_lin / v["n_m"], 3), Rd_kN=round(v["Rd"], 3), uso=round(f_lin / v["n_m"] / v["Rd"], 2)) for k, v in lig.items()})
R["zonas"] = res
R["conclusao"] = ("Com a costura da cartola a cada 2 ondas (padrão do manual) a sucção não passa nem na zona geral; com costura em TODAS as "
                  "ondas passa nas duas zonas. Clipes com 2 parafusos na cartola passam (borda no limite). TP-40 na terça com folga. "
                  "Confirmar com a Kingspan os valores de arrancamento dos parafusos na chapa #0,65 e a distribuição de clipes para o vento da obra.")
ok = all(v["uso"] <= 1.0 for z in res.values() for k, v in z["ligacoes"].items() if "2 ondas" not in k)
R["ok_com_costura_em_todas_as_ondas"] = ok
(AQ / "fixacao_telhas.json").write_text(json.dumps(R, indent=1, ensure_ascii=False), encoding="utf-8")
assert ok, res
if __name__ == "__main__":
    print(json.dumps(R, indent=1, ensure_ascii=False))
