import pickle, numpy as np, pyvista as pv, sys
pv.OFF_SCREEN = True
M = pickle.load(open("malha.pkl", "rb"))
COR = {"Pilares": "#b9b4aa", "Consolos": "#b9b4aa", "Vigas centrais I130": "#cfc8bb", "Vigas I90 de cobertura": "#cfc8bb", "Vigas de borda": "#cfc8bb",
       "Vigas de mezanino (meio vaso)": "#cfc8bb", "Vigas de mezanino (retangulares protendidas)": "#cfc8bb", "Escada metálica": "#d8751f", "Escada metálica externa": "#d8751f", "Cobertura metálica da linha 2": "#4f7ea8", "Concreto de 2º estágio (obra, com a capa)": "#9aa3a8", "Laje alveolar": "#d9d4ca",
       "Terças metálicas": "#4f7ea8", "Contraventamento": "#c8541f", "Correntes, tirantes rígidos e diagonais": "#c8541f", "Calha e descidas": "#7d8a93",
       "Placas de fechamento": "#c9c4ba", "Telhas": "#aeb6bb", "Rufos e acabamentos": "#8f989e", "Piso e fundações": "#8d8a84",
       "Ligações da cobertura": "#d8751f", "Insertos metálicos": "#d8751f", "Fixação das placas": "#d8751f"}
def malha(g, filtro=None):
    pts, fs, off = [], [], 0
    for it in M.get(g, []):
        if filtro and not filtro(it): continue
        v = np.array(it["v"]).reshape(-1, 3); f = np.array(it["f"]).reshape(-1, 3)
        pts.append(v); fs.append(np.hstack([np.full((len(f), 1), 3), f + off])); off += len(v)
    if not pts: return None
    return pv.PolyData(np.vstack(pts), np.vstack(fs).ravel())
def render(grupos, arq, cam, filtros={}, w=2400, h=1500, caixa=None, zoom=1.15, foco=None):
    p = pv.Plotter(off_screen=True, window_size=(w, h)); p.set_background("white")
    for g in grupos:
        m = malha(g, filtros.get(g))
        if m is not None and caixa is not None:
            m = m.clip_box(caixa, invert=False)
        if m is not None and m.n_points:
            p.add_mesh(m, color=COR.get(g, "#bbbbbb"), smooth_shading=False, ambient=0.25, diffuse=0.75, specular=0.05)
    import os as _os
    if not _os.environ.get("ND_PV_SCALE_MAP"):                      # rev11: em alta resolução (janela × S) sem SSAA (estoura o framebuffer)
        p.enable_anti_aliasing("ssaa")
    p.view_vector(cam[0], viewup=(0, 0, 1)); p.reset_camera(); p.camera.zoom(zoom)
    p.screenshot(arq); p.close()
EST = ["Pilares", "Consolos", "Vigas centrais I130", "Vigas I90 de cobertura", "Vigas de borda", "Vigas de mezanino (meio vaso)", "Vigas de mezanino (retangulares protendidas)", "Escada metálica", "Escada metálica externa", "Cobertura metálica da linha 2",
       "Concreto de 2º estágio (obra, com a capa)", "Laje alveolar", "Terças metálicas", "Contraventamento", "Correntes, tirantes rígidos e diagonais", "Calha e descidas"]
c = np.array([39.68, 19.75, 4.0])
cam1 = [(-1.0, -1.15, 0.75)]
render(EST, "ng01_estrutura.png", cam1)
# obra completa: placas e telhas; telhas só metade (corte para mostrar a estrutura)
render(EST + ["Placas de fechamento", "Telhas", "Rufos e acabamentos"], "ng01_completa.png", [(1.0, -1.1, 0.55)])

# rev09: mezanino +3,90 com a laje +7,30 e a cobertura cortadas (z < 5,0) para mostrar o vão e a escada metálica
if "mez" in sys.argv or len(sys.argv) == 1:
    render(EST, "ng01_mezanino.png", [(-0.55, 1.0, 0.85)], caixa=(22.0, 41.0, -1.0, 13.0, -0.5, 5.0), zoom=1.05)
