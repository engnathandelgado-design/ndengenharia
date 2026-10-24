import sys, json, pickle, numpy as np
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas")
from nd_estruturas.bim import ler_malha_ifc
import pyvista as pv
pv.OFF_SCREEN = True
IFC = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/saidas/letsara.ifc"
M = ler_malha_ifc(IFC)
print({g: len(v) for g, v in M.items()})
pickle.dump(M, open("malha.pkl", "wb"))
