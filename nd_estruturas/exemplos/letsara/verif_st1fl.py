"""ST-1FL / ES-1FL (DEC-042, 22/10/2026): verificação com as reações REAIS da terça de ponta do lado E nos cantos
(modelo_integrado_r05.json → ST1P_grupos["ST-1FL canto"], envoltória ELU das 48 combinações), no lugar da envoltória
emprestada do ST-1V-R. 2 barras roscadas M20 A36 horizontais na face lateral do pilar de canto (hef 150 + grampo U Ø10),
a 70 e 150 mm da aresta da face A, no meio da chapa (290 de altura); C40; ACI 318-19 cap. 17; chapa 9,5 A36; 2 M12 8.8 na alma."""
import json, math
from pathlib import Path
AQ = Path(__file__).parent
R = json.loads((AQ / "modelo_integrado_r05.json").read_text(encoding="utf-8"))["envoltoria"]["ST1P_grupos"]["ST-1FL canto"]
CB = json.loads((AQ / "cobertura_metalica.json").read_text(encoding="utf-8"))["terca"]["apoio"]
Fy, Fx, Rz = R["Fy_max"], R["Fx_max"], max(R["Rz_up"], R["Rz_down"])          # kN (ELU): Fy ⊥ à face (ao longo da terça)
fc, hef, d, c1, s = 40.0, 150.0, 20.0, 70.0, 80.0
Ase, futa = 245.0, 400.0
# tração no grupo: 1,25·Fy (efeito de alavanca) + Rz (excentricidade do apoio na alma) — mesmo critério do DEC-042
N = 1.25 * Fy + Rz
phiNsa = 2 * 0.75 * Ase * futa / 1000
Nb = 10 * math.sqrt(fc) * hef ** 1.5 / 1000                                     # kc = 10 (fissurado), SI
ANc = (min(c1, 1.5 * hef) + s + 1.5 * hef) * (3 * hef)
ANco = 9 * hef ** 2
psi_ed = 0.7 + 0.3 * c1 / (1.5 * hef)
phiNcbg = 0.75 * ANc / ANco * psi_ed * Nb * 1.0                                # φ 0,75 com o grampo (armadura suplementar)
# corte: Fx ⊥ à aresta da face A (c1 = 70, só a barra da borda), Rz ∥ à aresta (2·Vcb)
V = math.hypot(Fx, Rz)
phiVsa = 2 * 0.65 * 0.6 * Ase * futa / 1000
Vb = 0.6 * (min(hef, 8 * d) / d) ** 0.2 * math.sqrt(d) * math.sqrt(fc) * c1 ** 1.5 / 1000
phiVcb_perp, phiVcb_par = 0.75 * Vb, 0.75 * 2 * Vb
uV_conc = max(Fx / phiVcb_perp, Rz / phiVcb_par)
uN = max(N / phiNsa, N / phiNcbg)
uV = max(V / phiVsa, uV_conc)
inter = uN + uV if (uN > 0.2 and uV > 0.2) else max(uN, uV)
# chapa: aba da face em balanço da dobra (alma) até a 1ª barra: 76,5 − 16 (arruela) = 60 mm; seção líquida 290 − 22
M = Fy * 0.060
Mrd = (290 - 22) * 9.5 ** 2 / 4 * 250 / 1.10 / 1e6
# 2 M12 8.8 na alma da terça Z 2,30: corte + esmagamento (Vb_Rd do apoio)
Vp = math.sqrt(Fy ** 2 + Fx ** 2 + Rz ** 2) / 2
out = dict(reacoes_kN=dict(Fy=Fy, Fx=Fx, Rz=Rz, x=R["x"]), N_kN=round(N, 1), V_kN=round(V, 1),
           phiNsa=round(phiNsa, 1), phiNcbg=round(phiNcbg, 1), phiVsa=round(phiVsa, 1), phiVcb_perp=round(phiVcb_perp, 1), phiVcb_par=round(phiVcb_par, 1),
           uso_tracao=round(uN, 3), uso_corte=round(uV, 3), interacao=round(inter, 3), limite_interacao=1.2,
           chapa=dict(M_kNm=round(M, 2), Mrd_kNm=round(Mrd, 2), uso=round(M / Mrd, 3)),
           M12=dict(V_parafuso=round(Vp, 1), Vb_Rd=CB["Vb_Rd"], uso=round(Vp / CB["Vb_Rd"], 3)))
(AQ / "verif_st1fl.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(out, ensure_ascii=False, indent=1))
