"""rev12 — fresta das vigas de borda (decisão do engenheiro de 26/10/2026, opção B do quadro decisao_fresta_fechamento):
VB 15×60 e consolo CP-VB alinhados à face externa do pilar de fachada (40×60, 60 ⊥ fachada), 2,5 cm até a placa.

Aplicado nos vãos entre pilares de fachada PF (B–C e C–D das linhas 1 e 9: VB-02, VB-03, VB-06, VB-07): o eixo da VB sai
e = 30,0 − 7,5 = 22,5 cm do eixo do pilar. rev12 (27/10, decisão do Nathan, opção D do quadro decisao_fresta_canto): os 4
pilares de canto saem 10 cm para fora (face externa = face dos PF) e os vãos de canto (A–B e D–E: VB-01, VB-04, VB-05, VB-08)
também ficam com a VB rente à face — nos PF o CP-VB fica rente à face nas duas faces laterais; no canto, o CP-VB da face A
fica e = 22,5 − 10,0 = 12,5 cm para o lado da fachada (rente à face externa).

Verificações (NBR 9062:2017 7.3; NBR 6118:2023 17.2.5 e 17.5):
 1. consolo C1 rente à face C (marca nova): mesma geometria, armadura e carga do C1 (consolos.json CP-VB); tirante em alça
    horizontal com cobrimento lateral 3,0 cm na face C (a alça entra no pilar pela face B/D, nada muda no nó);
 2. pilar: momento adicional ΔMd = Σ Vd·e no plano ⊥ à fachada (Mx), somado em valor absoluto ao Mx de TODAS as
    combinações do modelo integrado (a favor da segurança), com a armadura existente (14 Ø20) — flexão oblíqua 17.2.5.2;
 3. torção no pilar pela força horizontal do apoio (Hd = 0,16 Fd, elastômero, NBR 9062 7.3.1.2): Td = Hd·e ≤ TRd2,
    interação com a cortante (17.7.2.2) desprezível;
 4. VB: carga centrada no consolo (o consolo se move com a VB) → sem torção na viga.
Saída: consolos_face.json (lido por pilares_familia, consolos_marcas, modelo_bim e folhas)."""
import json, math, sys
from pathlib import Path

AQ = Path(__file__).resolve().parent
sys.path.insert(0, str(AQ))
sys.path.insert(0, str(AQ.parents[1]))
import dimensionar_pilares_r05 as DP

CONS = json.loads((AQ / "consolos.json").read_text(encoding="utf-8"))["CP-VB"]
B_PIL_Y, B_VB = 0.60, 0.15
E_VB = round(B_PIL_Y / 2 - B_VB / 2, 3)                 # 0,225 m
VD, FD, HD = CONS["Vd_kN"], CONS["Fd_kN"], CONS["Hd_kN"]
# faces dos PF com VB alinhada (linha 1: B do lado de x menor, D de x maior) — vãos B–C e C–D (entre PF)
from geometria import DY_CANTO
E_CANTO = round(E_VB - DY_CANTO, 3)                      # 0,125 m
FACES = {mk: ("B", "D") for mk in ("PF-01", "PF-02", "PF-03", "PF-05", "PF-04", "PF-06")}   # rev12 (opção D): todos os vãos
X_PF = {"PF-01": 9.87, "PF-02": 19.75, "PF-03": 29.63, "PF-05": 9.87, "PF-04": 19.75, "PF-06": 29.63}
# cantos: CP-VB na face A; excentricidade para a face da fachada (P1: A = +x → B = +y, D = −y; P2: A = −x → B = −y, D = +y)
CANTOS = {"PL-03": ("D", 0.0), "PL-04": ("B", 0.0), "PL-07": ("B", 39.50), "PL-08": ("D", 39.50)}


def torcao_resistente(bx, by, fck=40.0):
    """NBR 6118:2023 17.5.1.5: TRd2 = 0,5·αv2·fcd·Ae·he·sen 2θ (θ = 45°), seção vazada equivalente he = A/u."""
    A, u = bx * by, 2 * (bx + by)
    he = max(A / u, 2 * 0.045)
    Ae = (bx - he) * (by - he)
    av2 = 1 - fck / 250
    return 0.5 * av2 * fck / 1.4 * 1000 * Ae * he


out = dict(e_m=E_VB, Vd_kN=VD, Fd_kN=FD, Hd_kN=HD, norma="NBR 9062:2017 7.3; NBR 6118:2023 17.2.5.2 e 17.5.1.5", pilares={})
ITENS = [(mk, faces, E_VB, "C") for mk, faces in FACES.items()] + [(mk, ("A",), E_CANTO, fe) for mk, (fe, _) in CANTOS.items()]
for mk, faces, e_, exc_face in ITENS:
    pils = DP.GRUPOS[mk]
    b0 = DP.EST[next(iter(DP.EST))]["2a"][pils[0]]
    bx, by = b0["bx"], b0["by"]
    # rev12 (27/10): verificação com a armadura ADOTADA (dimensionamento_pilares_r05.json → arranjo das folhas), não a antiga
    pr_ = json.loads((AQ / "dimensionamento_pilares_r05.json").read_text(encoding="utf-8"))[mk]["proposto"]
    brs, _ = DP.barras(bx, by, pr_["nx"], pr_["ny"], pr_["d"])
    dM = len(faces) * VD * e_                            # kN·m, Mx (plano ⊥ à fachada)
    assert abs(DP.DM_CONS[pils[0]] - dM) < 0.01, (mk, dM)          # o mesmo ΔM entra no dimensionamento (dimensionar_pilares_r05)
    u0, _ = DP.secao_ok(dict(brs=brs), pils, com_dm=False)
    u1, onde = DP.secao_ok(dict(brs=brs), pils)
    Td = len(faces) * HD * e_
    TRd2 = torcao_resistente(bx, by)
    out["pilares"][mk] = dict(faces=list(faces), e_m=e_, exc_face=exc_face, x=X_PF.get(mk, CANTOS.get(mk, (0, 0))[1]), dM_kNm=round(dM, 2), uso_antes=round(u0, 3), uso_com_excentricidade=round(u1, 3), comb=onde,
                              Td_kNm=round(Td, 2), TRd2_kNm=round(TRd2, 1), uso_torcao=round(Td / TRd2, 3), ok=u1 <= 1.0 and Td <= TRd2)
    print(mk, faces, f"ΔM {dM:.1f} kN·m  uso {u0:.3f} → {u1:.3f}  Td {Td:.2f} / TRd2 {TRd2:.0f}")
out["consolo"] = dict(geometria=f"{CONS['b_m']*100:g} × {CONS['proj_m']*100:g} × {CONS['h_total_m']*100:g} (igual ao C1)", tirante=CONS["tirante"],
                      cobrimento_lateral_cm=3.0, ok=CONS["ok"],
                      obs="rente à face C do pilar (face lateral do consolo no plano da face C); mesma Fd e mesma armadura do C1 (a carga continua centrada no consolo)")
out["ok"] = all(v["ok"] for v in out["pilares"].values()) and CONS["ok"]
(AQ / "consolos_face.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("ok", out["ok"])
