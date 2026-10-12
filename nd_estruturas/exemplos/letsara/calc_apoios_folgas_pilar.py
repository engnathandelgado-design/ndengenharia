"""Letsara — (1) folgas de montagem de todas as peças, (2) condições de apoio sobre os consolos (neoprene, pressão,
rotação, escorregamento, restrição do encurtamento) e (3) pilar lateral protendido (pré-tração na cabeceira).

Normas: NBR 9062:2017 (tolerâncias de fabricação e montagem, item 5.2/9; aparelhos de apoio 7.2), NBR 6118:2023,
NBR 19289 (aparelhos de apoio elastoméricos — pressão, rotação, distorção). Unidades kN, m, MPa.
"""
import json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from nd_estruturas.prefabricados import Concreto, pressao_vento, pilar_metodo_geral

AQ = Path(__file__).parent
LG = json.loads((AQ / "ligacoes.json").read_text(encoding="utf-8"))
DT = json.loads((AQ / "dentes.json").read_text(encoding="utf-8"))
R = {}

# ------------------------------------------------------------------ 1. folgas de montagem
# tolerâncias (NBR 9062:2017 Tabela 5 e 9.2 — valores adotados): comprimento de viga ±(10 + L/1000 → 10–15 mm);
# posição do pilar em planta ±10 mm; prumo do pilar 10 mm em 10 m; posição do consolo ±10 mm; furo do pino ±5 mm.
TOL = dict(comp_viga=lambda L: 10 + L, pilar_planta=10, prumo=10, consolo=10, furo=5)
pecas = {
    "TS-01 (pilar lateral)": dict(L=19.46, folga_ponta=25, folga_consolo=25, pino_folga_radial=12.5, dente_lateral=0),
    "TS-01 (lado da I110)": dict(L=19.46, folga_ponta=75, folga_consolo=25, pino_folga_radial=12.5, dente_lateral=0),
    "I110 (pilar central)": dict(L=23.0, folga_ponta=25, folga_consolo=25, pino_folga_radial=12.5, dente_lateral=0),
    "Viga do mezanino": dict(L=9.3, folga_ponta=25, folga_consolo=25, pino_folga_radial=12.5, dente_lateral=0),
    "Terça Ue (entre vigas)": dict(L=10.0, folga_ponta=5, folga_consolo=None, pino_folga_radial=None, dente_lateral=0),
}
fol = {}
for nome, p in pecas.items():
    t_total = TOL["comp_viga"](p["L"]) / 2 + TOL["pilar_planta"] + TOL["prumo"]       # desvio provável numa ponta
    t_consolo = TOL["consolo"] + TOL["comp_viga"](p["L"]) / 2
    ok_ponta = p["folga_ponta"] >= t_total
    ok_cons = p["folga_consolo"] is None or p["folga_consolo"] >= t_consolo
    fol[nome] = dict(folga_ponta_mm=p["folga_ponta"], desvio_provavel_mm=round(t_total), ok_ponta=ok_ponta,
                     folga_consolo_dente_mm=p["folga_consolo"], desvio_consolo_mm=round(t_consolo), ok_consolo=ok_cons,
                     pino_folga_radial_mm=p["pino_folga_radial"],
                     ok_pino=(p["pino_folga_radial"] or 99) >= TOL["furo"] + TOL["consolo"] / 2)
R["folgas"] = dict(tolerancias="NBR 9062:2017 (adotadas): comprimento ±(10 + L[m]) mm, pilar ±10, prumo 10/10 m, consolo ±10, furo ±5",
                   pecas=fol,
                   descida_vertical=dict(TS01_pilar="livre: a platibanda sobe reta acima do consolo e a ponta desce a prumo",
                                         TS01_I110="livre: topo da I110 (+8,88) fica 86 mm abaixo das terças e o dente desce ao lado da I110 com 75 mm",
                                         I110="livre: topo do pilar central = topo da I110 (+8,88)",
                                         mezanino="livre, mas 25 + 25 mm entre pilares em 9,3 m: pede pilares aprumados antes (± 10 mm)",
                                         tercas="descem entre as CT-1; furo d+2 e 5 mm de folga na ponta"))

# ------------------------------------------------------------------ 2. apoios sobre consolos
C50 = Concreto(50)
G_NEO = 1.0            # MPa (dureza 60 Shore A)
apoios = {
    "TS-01 → CP-TS / CV-TS": dict(Rk=104.0, Rd=138.0, Hd=40.0, a=0.300, b=0.150, t=0.010, L=19.46, flecha=0.011, fretado=False, camadas=1),
    "I110 → CP-I110": dict(Rk=320.0, Rd=448.0, Hd=72.0, a=0.300, b=0.250, t=0.020, L=23.0, flecha=0.043, fretado=True, camadas=2),
    "Viga mezanino I90 → CP-MEZ": dict(Rk=275.0, Rd=383.0, Hd=65.0, a=0.300, b=0.200, t=0.015, L=9.3, flecha=0.002, fretado=True, camadas=2),
}
ap = {}
E_pil = C50.Ecs if hasattr(C50, "Ecs") else 0.85 * 5600 * math.sqrt(50) * 1e3
for nome, d in apoios.items():
    A = d["a"] * d["b"]
    sig_k, sig_d = d["Rk"] / A / 1e3, d["Rd"] / A / 1e3
    lim = 10.0 if d["fretado"] else 5.0                                       # NBR 9062 7.2 / NBR 19289 (simples 5, fretado 10 MPa)
    S = A / (2 * (d["a"] + d["b"]) * (d["t"] / d["camadas"]))               # fator de forma
    Ec = 3 * G_NEO * (1 + 2 * S ** 2)                                        # módulo à compressão aparente
    dz = sig_k / Ec * d["t"] * 1000                                          # recalque elástico (mm)
    theta = 3.2 * d["flecha"] / d["L"]                                       # rotação de apoio ≈ 16δ/5L (carga uniforme)
    dz_rot = theta * d["b"] / 2 * 1000
    enc = (0.15e-3 + 0.35e-3) * d["L"] / 2 * 1000                            # Δ térmico 15 °C + retração/fluência residual, meia viga (mm)
    gama = enc / (d["t"] * 1000)
    k_pil = 3 * E_pil * 0.40 * 0.60 ** 3 / 12 / 10.0 ** 3                   # rigidez do topo do pilar lateral (kN/m)
    F_restr = enc / 1000 * k_pil                                             # força se os dois pinos forem grauteados
    sig_conc = d["Rd"] / A / 1e3
    ap[nome] = dict(neoprene=f"{d['a']*1000:.0f}×{d['b']*1000:.0f}×{d['t']*1000:.0f}" + (" fretado" if d["fretado"] else " simples"),
                    pressao_k_MPa=round(sig_k, 2), pressao_d_MPa=round(sig_d, 2), limite_MPa=lim, ok_pressao=sig_k <= lim,
                    fator_forma=round(S, 1), recalque_mm=round(dz, 2), rotacao_mrad=round(theta * 1000, 2),
                    ok_rotacao=dz >= dz_rot, obs_rotacao="sem descolamento da borda (recalque ≥ θ·b/2)" if dz >= dz_rot else "borda descola: usar fretado ou mais espessura",
                    encurtamento_mm=round(enc, 1), distorcao=round(gama, 2), ok_distorcao=gama <= 0.7,
                    forca_restricao_pinos_kN=round(F_restr, 1),
                    pressao_concreto_consolo_MPa=round(sig_conc, 2), ok_concreto=sig_conc <= 0.85 * C50.fcd,
                    componente_3pct_kN=round(0.03 * d["Rd"], 1), borda_neoprene_mm=round((0.300 - d["b"]) / 2 * 1000) if d["b"] < 0.3 else 75)
R["apoios"] = dict(regras="pressão ≤ 5 MPa (simples) / 10 MPa (fretado); distorção ≤ 0,7; sem descolamento de borda; "
                          "pino grauteado só numa ponta de cada viga (a outra com graute flexível ou furo oblongo) ou aceitar a força de restrição",
                   apoios=ap)

# ------------------------------------------------------------------ 3. pilar lateral protendido
qv = pressao_vento(45.0, S3=0.95)
TRIB, LP = 9.655, 10.0
Nk = 412.2
w_med = (0.7 + 0.5) / 2 * qv * TRIB
C40 = Concreto(40)
Mk = w_med * LP ** 2 / 2
W = 0.40 * 0.60 ** 2 / 6
fctm = 0.3 * 40 ** (2 / 3)
opcoes = {}
for nome, As_face, cord in (("armado 5 Ø20 por face", 5 * 3.14, ()),
                            ("protendido: 6 cord. (3 por face a 250 do eixo) + 4 Ø12,5", 4 * 1.23, ((-0.25, 3), (0.25, 3))),
                            ("protendido: 8 cord. (4 por face) + 4 Ø12,5", 4 * 1.23, ((-0.25, 4), (0.25, 4)))):
    P = sum(n for _, n in cord) * 0.987e-4 * 1000e3                      # kN após perdas (σp∞ ≈ 1000 MPa)
    sig_p = P / (0.40 * 0.60) / 1e3
    Mr = (fctm + sig_p + Nk / 0.24 / 1e3) * W * 1e3                      # momento de fissuração com N e protensão (kN·m)
    r = pilar_metodo_geral(0.40, 0.60, LP, As_face, 1.3 * Nk, 1.4 * w_med, C40, phi_ef=0.5, cord=cord, sig_pinf=1000.0)
    opcoes[nome] = dict(P_inf_kN=round(P), sigma_p_MPa=round(sig_p, 2), M_fissuracao_kNm=round(Mr), Mk_vento_kNm=round(Mk),
                        fica_no_estadio_I=Mr >= 0.3 * Mk * 1.0 and Mr >= Mk * 0.3, lambda_u=r["lambda_u"], ok_ELU=r["ok"],
                        topo_mm_ELU=r["topo_mm"])
R["pilar_protendido"] = dict(secao="40×60, L = 10 m em balanço, C40, vento transversal (q = 0,874 kN/m²)",
                             Mk_base_vento_kNm=round(Mk), opcoes=opcoes,
                             cabeceira="cabeçote REV05: linha inferior 75–243 mm e superior 1050–1092 mm do fundo da fôrma — "
                                       "pilar de 60 deitado só alcança a linha inferior: cordoalhas a 250 do eixo nas DUAS faces exigem "
                                       "furar o cabeçote a 525 mm ou cabeçote intermediário; com 40 de altura (deitado de lado) idem (325 mm)",
                             transitorias="pilar de 11 m içado por 2 pontos a 0,21 L: M = 0,0215 w L² ≈ 7 kN·m·m⁻¹… ver cálculo no texto")
(AQ / "apoios_folgas_pilar.json").write_text(json.dumps(R, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
print(json.dumps(R, indent=1, ensure_ascii=False, default=str))
