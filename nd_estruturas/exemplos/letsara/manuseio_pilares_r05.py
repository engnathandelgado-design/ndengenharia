"""DEC-040 — arranjo final por marca no referencial das folhas (B × H, nb barras ao longo de B, nh ao longo de H) e
verificação do manuseio com a armadura nova (NBR 9062:2017 5.3.2): desforma/estocagem/transporte deitado nas 2 alças AL-2
(face C para cima: altura = H) e verticalização apoiado na base e no furo FI-1 (altura conforme o eixo do furo).
γf 1,3 × βa 1,3 no ELU (MRd com N = 0) e σs ≤ 0,5 fyk = 250 MPa com Mk·βa (seção fissurada, z = 0,9 d). Grava arranjo_pilares.json."""
import json, math
from pathlib import Path
AQ = Path(__file__).resolve().parent
PR = Path("/home/claude/letsara/pranchas")
COB, PHI_T, DL = 30, 6.3, 16.0
C = COB + PHI_T + DL / 2                                   # mm, eixo da barra à face


def arranjo(mk, e):
    """(nb, nh) nas folhas: B e H como em pilar_generico.base (H = direção A–C da peça)."""
    if mk.startswith("PF"):
        return e["nx"], e["ny"]
    return e["ny"], e["nx"]                                # PL, PC, PM, PG: B ↔ y global, H ↔ x global


def xy(B, H, nb, nh, c=C):
    xs = [-B / 2 + c + k * (B - 2 * c) / (nb - 1) for k in range(nb)]
    ys = [-H / 2 + c + k * (H - 2 * c) / (nh - 1) for k in range(nh)]
    pts = {(round(x), round(y)) for x in xs for y in (ys[0], ys[-1])} | {(round(x), round(y)) for y in ys for x in (xs[0], xs[-1])}
    return sorted(pts)


def grampos(B, H, nb, nh, phi_t=PHI_T, c=C):
    """barras a mais de 20 φt de um canto de estribo (com mais de 2 barras no trecho) precisam de grampo (NBR 6118 18.2.4)."""
    lim = 20 * phi_t
    def precisa(n, L):
        if n <= 2:
            return []
        s = (L - 2 * c) / (n - 1)
        out = []
        for k in range(1, n - 1):
            dk = min(k, n - 1 - k) * s
            if dk > lim + 0.5 or min(k, n - 1 - k) > 2:
                out.append(-L / 2 + c + k * s)
        return out
    return dict(across_B=[round(y) for y in precisa(nh, H)],     # grampo atravessa B na cota y (barras das faces B/D)
                across_H=[round(x) for x in precisa(nb, B)])     # grampo atravessa H na posição x (barras das faces A/C)


def MRd0(b, h, bars, eixo):
    fcd, fyd, Es = 40 / 1.4, 500 / 1.15, 200e3
    def F(x):
        a = min(0.8 * x, h); Cc = 0.85 * fcd * b * a; Mc = Cc * (h / 2 - a / 2); Fs = Ms = 0.0
        for bx_, by_, A in bars:
            yy = by_ if eixo == "y" else bx_
            eps = 0.0035 * (x - (h / 2 - yy)) / x
            sg = max(-fyd, min(fyd, Es * eps)); Fs += sg * A; Ms += sg * A * yy
        return Cc + Fs, Mc + Ms
    lo, hi = 1.0, 5 * h
    for _ in range(80):
        x = (lo + hi) / 2
        lo, hi = (lo, x) if F(x)[0] > 0 else (x, hi)
    return F((lo + hi) / 2)[1] / 1e6                     # kN·m


def momentos(L, w, apoios, n=2001):
    """viga isostática em 2 apoios com balanços: M máx |.| (kN·m)."""
    a, b = sorted(apoios)
    s = b - a
    Rb = w * L * (L / 2 - a) / s; Ra = w * L - Rb
    mx = 0.0
    for i in range(n):
        z = L * i / (n - 1)
        M = -w * z * z / 2 + (Ra * (z - a) if z > a else 0) + (Rb * (z - b) if z > b else 0)
        mx = max(mx, abs(M))
    return mx


if __name__ == "__main__":
  D = json.loads((AQ / "dimensionamento_pilares_r05.json").read_text(encoding="utf-8"))
  out = {}
  for mk, r in D.items():
      e = r["proposto"]
      g = json.loads((PR / f"{mk}_geom.json").read_text(encoding="utf-8"))
      B, H, L = g["B"], g["H"], g["L_TOT"] / 1000
      nb, nh = arranjo(mk, e)
      pts = xy(B, H, nb, nh)
      A1 = math.pi * DL ** 2 / 4
      bars = [(x, y, A1) for x, y in pts]
      w = B * H / 1e6 * 25 * 1.10                             # +10 % consolos e insertos
      casos = []
      al = [z / 1000 for z in g["al"]]
      casos.append(("desforma / estocagem / transporte (2 AL-2, face C para cima)", momentos(L, w, al), "H"))
      fi = g["fi"]
      casos.append((f"verticalização (base + FI-1 {fi['eixo']})", momentos(L, w, [0.0, fi["z"] / 1000]), "H" if fi["eixo"] == "BD" else "B"))
      res = []
      for nome, Mk, dirc in casos:
          h, b, eixo = (H, B, "y") if dirc == "H" else (B, H, "x")
          MRd = MRd0(b, h, bars, eixo)
          k = 1 if eixo == "y" else 0
          ymax = max(p[k] for p in pts)
          At = sum(A1 for p in pts if abs(p[k] - ymax) < 1)
          d = h / 2 + ymax
          sig = Mk * 1.3 * 1e6 / (At * 0.9 * d)
          res.append(dict(caso=nome, Mk=round(Mk, 1), Md=round(1.69 * Mk, 1), MRd0=round(MRd, 1), uso=round(1.69 * Mk / MRd, 2), sigma_s=round(sig), ok=1.69 * Mk <= MRd and sig <= 250))
      gr = grampos(B, H, nb, nh)
      out[mk] = dict(B=B, H=H, nb=nb, nh=nh, n=len(pts), d=DL, xy=pts, c=round(C, 1), grampos=gr, manuseio=res,
                     tipo=e.get("tipo"), As_cm2=e["As_cm2"], uso_secao=e["uso_secao"], lambda_u=e["lambda_u"])
      print(f"{mk:6s} {B}×{H} nb {nb} nh {nh} n {len(pts)} grampos {gr} | " + " | ".join(f"{x['uso']} σs {x['sigma_s']}{'' if x['ok'] else ' FALHA'}" for x in res))
  (AQ / "arranjo_pilares.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
  