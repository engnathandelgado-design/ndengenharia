"""Testes conferidos à mão: perfis formados a frio (props, FSM × analítico), chumbadores (ACI 318-19),
dente Gerber (PCI 5.6) e validação do MEF não linear contra flexão de viga retangular (NBR 6118)."""
import math, os
import pytest
from nd_estruturas.metalica_fria import props_parede_fina, PerfilUe
from nd_estruturas.ancoragem import GrupoPinos
from nd_estruturas.dente_consolo import Dente


def test_canal_centro_de_torcao_e_cw():
    # U simples 200×100×2 (linha média): e = 3b²/(h + 6b) = 37,5 mm da alma; Cw = t b³ h² (3b + 2h) / [12 (6b + h)]
    p = props_parede_fina([(100, 200), (0, 200), (0, 0), (100, 0)], 2.0)
    assert abs(-(p["x0"] + p["xc"]) - 37.5) < 1e-6
    assert abs(p["Cw"] - 2 * 100 ** 3 * 200 ** 2 * (300 + 400) / (12 * (600 + 200))) / p["Cw"] < 1e-9


def test_ue300_fsm_global_bate_com_analitico():
    # Ue 300×85×25×3,00: em L ≈ 3,24 m a curva de assinatura (faixas finitas) e Me da NBR 14762 9.8.2.2 diferem < 3%
    u = PerfilUe(300, 85, 25, 3.0)
    Ls, f = u.assinatura("M", Ls=[3237.0])
    assert abs(f[0] - u.Ne_flt(3237.0) / (u.W * u.fy)) < 0.03
    assert abs(u.p["A"] - 1524) < 1 and abs(u.W - 133.6e3) < 300     # catálogo: A 15,4 cm², Wx ≈ 136 cm³ (cantos vivos)


def test_pino_com_cabeca_isolado_cone():
    # ACI 318-19 17.6.2: Nb = 10·√50·100^1,5 = 70,7 kN; φ = 0,70 → 49,5 kN (governa sobre aço 67,9 e arrancamento 169)
    g = GrupoPinos(16, 32, 100, 1, 1, 0, 0, 1000, 1000, 1000, 1000, 500)
    t = g.tracao()
    assert t["modo"] == "cone" and abs(t["phiNn_kN"] - 49.5) < 0.1


def test_dente_suspensao_pci():
    # PCI 5.6.2.3: Ash = Vu/(φ fy) = 138 000/(0,75·500) = 368 mm²
    r = Dente("t", 138, 40, 400, 450, 300, 150, 900).dimensionar()
    assert r["PCI"]["Ash"] == 368


@pytest.mark.skipif(not os.environ.get("ND_MEF_LENTO"), reason="MEF não linear (~3 min): ND_MEF_LENTO=1")
def test_mef_flexao_viga_retangular():
    # 400×600, 3 Ø20 (942 mm²) a 50 do fundo, C30 e CA-50 de cálculo: MRd = As fyd (d − 0,4x) = 213,7 kN·m
    # (NBR 6118, diagrama retangular). O MEF dá ~226 kN·m (+6%): o critério dos dentes exige Vu ≥ 1,06 Vd.
    from nd_estruturas.mef_dente import analisar
    g = dict(H=600, b=400, bw=400, ti=0, mi=1, ts=0, ms=1, hd=600, ln=0, a_apoio=100, x_mac=1e9, l_apoio=150)
    arm = [dict(tipo="h", pos=50, ini=0, fim=3000, area_total=942, nome="tirante"),
           dict(tipo="h", pos=550, ini=0, fim=3000, area_total=226, nome="sup")]
    arm += [dict(tipo="v", pos=x, ini=25, fim=575, area_total=157, nome="estribo") for x in range(100, 3000, 100)]
    r = analisar(g, arm, [], Vd=100, Hd=0, fck=30, malha=25, Ls=3000, xP=1500, passos=300)
    Mu = r["Vu_kN"] * 1.4
    assert 0.95 * 213.7 <= Mu <= 1.10 * 213.7
