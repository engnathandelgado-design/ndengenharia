"""rev10 (Nathan 25/10/2026): isométrico do fechamento com cada parede (vista A a J) numa cor, placas com transparência de ~60 %
(opacity 0,4), pilares e vigas em cinza. Cores = fechamento.COR_VISTA (as mesmas das elevações das pranchas PP-x e da CM01).
Gera img/iso_fachadas.png (lida pela ND-LET-CM01)."""
import io, contextlib, re, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas")
import numpy as np
import pyvista as pv
from PIL import Image, ImageChops
with contextlib.redirect_stdout(io.StringIO()):
    import modelo_bim as MB
    import colisao_modelo as CM
    import fechamento as FCH
    m = MB.montar()


def malha(p):
    so = CM.solido(p).to_mesh()
    v, t = np.asarray(so.vert_properties)[:, :3], np.asarray(so.tri_verts)
    return pv.PolyData(v, np.hstack([np.full((len(t), 1), 3), t]).ravel())


pv.OFF_SCREEN = True
pl = pv.Plotter(off_screen=True, window_size=(2400, 1700)); pl.set_background("white")
cinza = {"Pilares": "#9a9a9a", "Vigas I90 de cobertura": "#c8c8c8", "Vigas centrais I120": "#c8c8c8", "Vigas de borda": "#c8c8c8"}
por_v = {}
for p in m.pecas:
    if p.grupo in cinza:
        pl.add_mesh(malha(p), color=cinza[p.grupo], smooth_shading=False)
    elif p.grupo == "Placas de fechamento":
        mm = re.search(r"vista (\w+)", p.marca)
        V = mm.group(1) if mm else "C"
        por_v.setdefault(V, []).append(malha(p))
for V, ms in por_v.items():
    mb = ms[0].merge(ms[1:]) if len(ms) > 1 else ms[0]
    r, g, b = FCH.COR_VISTA[V]
    pl.add_mesh(mb, color=(r / 255, g / 255, b / 255), opacity=0.40, show_edges=True, edge_color=(r / 400, g / 400, b / 400), line_width=0.6)
    c = np.array(mb.center); pl.add_point_labels([c + (0, 0, 6.5)], [f"VISTA {V}"], font_size=26, text_color=(r / 300, g / 300, b / 300), shape_opacity=0.0, show_points=False, always_visible=True)
pl.camera_position = [(-38, -48, 42), (19.75, 39.7, 3.0), (0, 0, 1)]
pl.reset_camera(); pl.camera.zoom(1.25)
arq = "/home/claude/letsara/pranchas/img/iso_fachadas.png"
pl.screenshot(arq); pl.close()
im = Image.open(arq).convert("RGB")
bb = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
im.crop((max(bb[0] - 20, 0), max(bb[1] - 20, 0), min(bb[2] + 20, im.width), min(bb[3] + 20, im.height))).save(arq)
print("ok", arq, {V: len(v) for V, v in por_v.items()})
