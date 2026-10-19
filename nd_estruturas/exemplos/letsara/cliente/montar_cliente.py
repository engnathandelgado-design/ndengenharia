"""Gera a página do cliente (fixação das placas) a partir da geometria atual (geo_fixacao), do MEF e da folha 1 da MT01."""
import base64, io, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/claude/letsara/pranchas")
import geo_fixacao as GF
import fitz
SP = Path(sys.argv[1]); L = Path("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
AÇO, PAR, GRA = [168, 184, 200], [128, 128, 138], [196, 170, 98]
E = 40.0


def cor(s):
    return GRA if s.item in (7, 8) else (PAR if s.item in (15, 16, 17, 18, 21) else AÇO)


def peca(g, s0, s1, c=None, a=1.0):
    d = (np.mean([v for f in s1.faces for v in f], 0) - np.mean([v for f in s0.faces for v in f], 0)).round(2).tolist()
    return dict(g=g, i=s0.item or 0, c=c or cor(s0), a=a, f0=[[list(map(float, v)) for v in f] for f in s0.faces], d=d)


P = []
for g, f in (("CS-1", lambda e: GF.cs1_solidos(e)), ("NC-1", lambda e: GF.nc1_no_console(e * 1.5))):
    P += [peca(g, a, b) for a, b in zip(f(0), f(E))]
sh = (-70.0, 0.0, -55.5)
for a, b in zip(GF.ce1_solidos(0), GF.ce1_solidos(E)):
    a2, b2 = a.movido(sh), b.movido(sh).movido((0, -30, 0))
    P.append(peca("CE-1", a2, b2))
for s in GF.placa_ponta():
    P.append(dict(g="placa", i=0, c=[214, 212, 202], a=0.35, f0=[[list(map(float, v)) for v in f] for f in s.faces], d=[0, 60, 0]))
import re
tb = lambda it: [[n, d, re.sub(r"(\d)\.(\d)", r"\1,\2", dim), m, q, round(kg * q, 3)] for n, d, dim, m, q, kg in it]
ITN, ITC = tb(GF.nc1_itens()), tb(GF.cs1_itens())
kgn, kgc = sum(r[5] for r in ITN), sum(r[5] for r in ITC)
doc = fitz.open("/home/claude/letsara/entregas/ND-LET-MT01-rev06.pdf")
pix = doc[0].get_pixmap(dpi=110)
from PIL import Image
im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples); bio = io.BytesIO(); im.save(bio, "JPEG", quality=80)
C = GF.C
s = (SP / "cliente_tpl.html").read_text(encoding="utf-8")
alt = C["costas"]["z1"] - C["costas"]["z0"]
FX = json.loads((L / "fixacao_placas.json").read_text(encoding="utf-8"))
s = s.replace("Console CS-1 — 120 × 200 × 64 mm", f"Console CS-1 — {C['costas']['b']:g} × {alt:g} × {C['alma']['y1']:g} mm")
s = s.replace("(filete 6 mm nos 2 lados verticais)", f"(filete {FX['solda']['filete_mm']:g} mm nos 2 lados verticais)")
N01 = json.load(open("/home/claude/letsara/pranchas/pp01.json"))["n"]
rep = dict(VIS=(L / "saidas" / "mef_cs1_vis.json").read_text(), RES=(L / "mef_cs1.json").read_text(), PEC=json.dumps(P, separators=(",", ":")),
           ITN=json.dumps(ITN, ensure_ascii=False), ITC=json.dumps(ITC, ensure_ascii=False), KGN=f"{kgn:.2f}".replace(".", ","), KGC=f"{kgc:.2f}".replace(".", ","),
           NE=str(N01["NC1_E"]), ND=str(N01["NC1_D"]), NCS=str(N01["CS1"]), NCC=str(N01["CC1"] + N01["CC1E"] + N01["CC1D"]), NCE=str(N01["CE1_obra"]),
           G=f"{GF.T['G']:g}", GT=f"{GF.T['G_tol']:g}", DNC=f"{GF.N['B']:g} × {GF.N['H']:g} × {GF.N['P']:g}", IMG=base64.b64encode(bio.getvalue()).decode())
for k, v in rep.items():
    assert f"__{k}__" in s, k
    s = s.replace(f"__{k}__", v)
(SP / "fixacao_cliente.html").write_text(s, encoding="utf-8")
m = (SP / "tpl.html").read_text(encoding="utf-8").replace("__VIS__", rep["VIS"]).replace("__RES__", rep["RES"])
(SP / "mef_cs1.html").write_text(m, encoding="utf-8")
print("ok", len(P), "peças", kgn, kgc, len(s) // 1024, "kB")
