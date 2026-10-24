import pickle, numpy as np, pyvista as pv, sys
pv.OFF_SCREEN = True
M = pickle.load(open("malha.pkl", "rb"))
COR = {"Pilares": "#b9b4aa", "Consolos": "#b9b4aa", "Vigas centrais I130": "#cfc8bb", "Vigas I90 de cobertura": "#cfc8bb", "Vigas de borda": "#cfc8bb",
       "Vigas de mezanino (meio vaso)": "#cfc8bb", "Concreto de 2º estágio (obra, com a capa)": "#9aa3a8", "Laje alveolar": "#d9d4ca",
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
def render(grupos, arq, cam, filtros={}, w=2400, h=1500):
    p = pv.Plotter(off_screen=True, window_size=(w, h)); p.set_background("white")
    for g in grupos:
        m = malha(g, filtros.get(g))
        if m is not None:
            p.add_mesh(m, color=COR.get(g, "#bbbbbb"), smooth_shading=False, ambient=0.25, diffuse=0.75, specular=0.05)
    p.enable_anti_aliasing("ssaa")
    p.view_vector(cam[0], viewup=(0, 0, 1)); p.reset_camera(); p.camera.zoom(1.15)
    p.screenshot(arq); p.close()
EST = ["Pilares", "Consolos", "Vigas centrais I130", "Vigas I90 de cobertura", "Vigas de borda", "Vigas de mezanino (meio vaso)",
       "Concreto de 2º estágio (obra, com a capa)", "Laje alveolar", "Terças metálicas", "Contraventamento", "Correntes, tirantes rígidos e diagonais", "Calha e descidas"]
c = np.array([39.68, 19.75, 4.0])
cam1 = [(-1.0, -1.15, 0.75)]
render(EST, "ng01_estrutura.png", cam1)
# obra completa: placas e telhas; telhas só metade (corte para mostrar a estrutura)
render(EST + ["Placas de fechamento", "Telhas", "Rufos e acabamentos"], "ng01_completa.png", [(1.0, -1.1, 0.55)])
