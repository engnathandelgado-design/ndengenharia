

def test_perfil_z_ponto_simetrico_e_area_catalogo():
    # Isoeste "Perfis Estruturais" (catálogo, Z45 ZAR345): ISO Z272G t = 2,30 → A = 10,58 cm².
    # Mesa e borda não constam no catálogo: 77 × 20 mm estimados pela área (conferir com o fabricante).
    from nd_estruturas.metalica_fria import PerfilZ
    z = PerfilZ(272, 77, 20, 2.30)
    assert abs(z.p["A"] / 100 - 10.58) / 10.58 < 0.02
    assert abs(z.p["x0"]) < 1e-6 * z.bw and abs(z.p["y0"]) < 1e-6 * z.bw   # CT = CG (seção ponto-simétrica)
    assert z.p["Ixy"] != 0                                                  # eixos principais inclinados


def test_perfil_z_abas_desiguais_metsec():
    """Z 302Z23 METSEC (catálogo voestalpine Meincol 2019, p. 6): A = 11,37 cm²; cantos vivos dão um pouco mais."""
    from nd_estruturas.metalica_fria import PerfilZ
    u = PerfilZ(302, 90, 19, 2.30, "METSEC400", 45.0, 82, 21)
    assert abs(u.p["A"] / 1137 - 1) < 0.03
    assert u.nome == "Z 302×90/82×2,30"
