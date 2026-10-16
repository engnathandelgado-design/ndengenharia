

def test_perfil_z_ponto_simetrico_e_area_catalogo():
    # Isoeste "Perfis Estruturais" (catálogo, Z45 ZAR345): ISO Z272G t = 2,30 → A = 10,58 cm².
    # Mesa e borda não constam no catálogo: 77 × 20 mm estimados pela área (conferir com o fabricante).
    from nd_estruturas.metalica_fria import PerfilZ
    z = PerfilZ(272, 77, 20, 2.30)
    assert abs(z.p["A"] / 100 - 10.58) / 10.58 < 0.02
    assert abs(z.p["x0"]) < 1e-6 * z.bw and abs(z.p["y0"]) < 1e-6 * z.bw   # CT = CG (seção ponto-simétrica)
    assert z.p["Ixy"] != 0                                                  # eixos principais inclinados
