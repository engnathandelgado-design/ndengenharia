"""Testes do módulo bim (modelo de peças -> IFC -> malha -> visualizador)."""
import math

import pytest

from nd_estruturas.bim import (
    DadoInvalido,
    ModeloBIM,
    Peca,
    PerfilI,
    gravar_ifc,
    gravar_visualizador,
    ler_malha_ifc,
    quantitativos,
)

I90 = PerfilI(h=0.90, b=0.40, tw=0.15, tf=0.15, nome="I90")


def test_area_e_volume_I90_conferidos_a_mao():
    # Seção padrão ND (Letsara, 12/10/2026): mesas 40 × 15, alma 15, h = 90 cm.
    # A = 2·0,40·0,15 + 0,15·(0,90 − 2·0,15) = 0,120 + 0,090 = 0,210 m²
    assert I90.area == pytest.approx(0.210)
    # Viga de 19,40 m: V = 0,210 · 19,40 = 4,074 m³ -> 10,2 t a 25 kN/m³ (≈ 2,5 t/m³)
    p = Peca("viga", "Vigas", "TS-01", I90, (0, 0, 8.08), (19.40, 0, 8.08))
    assert p.volume == pytest.approx(4.074)


def test_comprimento_de_viga_inclinada_a_3_por_cento():
    # L = √(19,40² + (0,03·19,40)²) = 19,40·√1,0009 = 19,4087 m
    p = Peca("viga", "Vigas", "TS-01", I90, (0, 0, 8.08), (19.40, 0, 8.08 + 0.03 * 19.40))
    assert p.comprimento == pytest.approx(19.40 * math.sqrt(1 + 0.03 ** 2))


@pytest.mark.parametrize("kw", [{"h": 0.9, "b": 0.40, "tw": 0.40, "tf": 0.15}, {"h": 0.3, "b": 0.40, "tw": 0.15, "tf": 0.15}])
def test_perfil_I_impossivel_e_recusado(kw):
    with pytest.raises(DadoInvalido):
        PerfilI(**kw)


def test_peca_sem_comprimento_ou_tipo_desconhecido_e_recusada():
    with pytest.raises(DadoInvalido):
        Peca("viga", "V", "V1", I90, (1, 1, 1), (1, 1, 1))
    with pytest.raises(DadoInvalido):
        Peca("tesoura", "V", "V1", I90, (0, 0, 0), (1, 0, 0))


def test_quantitativos_por_grupo():
    m = ModeloBIM("teste")
    m.pilar("P1", 0, 0, 0.60, 0.40, -1.0, 10.0)
    m.pilar("P2", 10, 0, 0.60, 0.40, -1.0, 10.0)
    q = quantitativos(m)["Pilares"]
    # 2 pilares · 0,60·0,40·11,00 = 2 · 2,64 = 5,28 m³
    assert q["pecas"] == 2 and q["volume_m3"] == pytest.approx(5.28)


def test_ponta_a_ponta_ifc_malha_visualizador(tmp_path):
    pytest.importorskip("ifcopenshell")
    m = ModeloBIM("teste", obra="Obra teste")
    m.pilar("P1", 0, 0, 0.60, 0.40, -1.0, 10.0)
    m.linear("viga", "TS-01", I90, (0.35, 0, 8.53), (19.80, 0, 8.53 + 0.03 * 19.45), "Vigas I90")
    m.pendente("! nível da cobertura a conferir")
    ifc = gravar_ifc(m, tmp_path / "t.ifc")
    malha = ler_malha_ifc(ifc)
    assert list(malha) == ["Pilares", "Vigas I90"]
    # volume tesselado = volume do domínio (extrusão exata, sem curvas)
    for grupo, pecas in zip(malha.values(), m.pecas):
        assert grupo[0]["vol"] == pytest.approx(pecas.volume, rel=1e-6)
    # orientação do pilar: 0,60 ao longo de X global, 0,40 ao longo de Y
    v = malha["Pilares"][0]["v"]
    xs, ys = v[0::3], v[1::3]
    assert max(xs) - min(xs) == pytest.approx(0.60, abs=1e-3)
    assert max(ys) - min(ys) == pytest.approx(0.40, abs=1e-3)
    html = gravar_visualizador(malha, tmp_path / "v.html", "Teste", pendencias=m.pendencias,
                               quant=quantitativos(m)).read_text(encoding="utf-8")
    assert "projeto da ND Engenharia" in html and "Vigas I90" in html and "/*DATA*/" not in html
