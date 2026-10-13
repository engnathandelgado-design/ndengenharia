"""ND-LET — modelo 3D em DXF (malhas do IFC, uma camada por grupo), em metros, eixo Z vertical."""
import sys
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas")
import ezdxf
from nd_estruturas.bim import ler_malha_ifc

ifc, saida = sys.argv[1], sys.argv[2]
malha = ler_malha_ifc(ifc)
doc = ezdxf.new("R2010", setup=True)
doc.units = ezdxf.units.M
msp = doc.modelspace()
CORES = {"Pilares": 8, "Consolos": 9, "Vigas centrais I110": 5, "Vigas I90 de cobertura": 5, "Vigas de borda": 4, "Vigas de travamento VT": 4,
         "Vigas de mezanino": 3, "Laje alveolar": 7, "Placas de fechamento": 252, "Terças metálicas": 30, "Telhas": 254,
         "Insertos metálicos": 1, "Pinos, tubos e neoprenes": 6, "Piso e fundações": 251}
n = 0
for grupo, pecas in malha.items():
    lay = grupo.upper().replace(",", "")[:60]
    if lay not in doc.layers:
        doc.layers.add(lay, color=CORES.get(grupo, 7))
    for p in pecas:
        v, f = p["v"], p["f"]
        pts = [tuple(v[i:i + 3]) for i in range(0, len(v), 3)] if v and not isinstance(v[0], (list, tuple)) else [tuple(x) for x in v]
        fs = [tuple(f[i:i + 3]) for i in range(0, len(f), 3)] if f and not isinstance(f[0], (list, tuple)) else [tuple(x) for x in f]
        pf = msp.add_polyface(dxfattribs={"layer": lay})          # POLYFACE: lido por qualquer versão do AutoCAD
        pf.append_faces([[pts[i] for i in fc] for fc in fs], dxfattribs={"layer": lay})
        pf.optimize()
        n += 1
msp.add_text("LETSARA — MODELO 3D — PROJETO DA ND ENGENHARIA", dxfattribs={"layer": "0", "height": 1.0}).set_placement((0, -6, 0))
doc.saveas(saida)
print("ok", n, "malhas", saida)
