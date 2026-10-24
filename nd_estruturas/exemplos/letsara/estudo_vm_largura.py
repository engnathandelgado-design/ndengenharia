"""Estudo de largura da VM do mezanino (23/10/2026, pedido do Nathan): b = 25 (referência), 30, 35, 40 cm; h de 5 em 5 cm.

Para cada largura: menor h em que TODAS as marcas (VM-01 a VM-04) passam em tudo da calc_vm_retangular (protensão completa,
montagem sem escoramento, seção composta, flechas, interface, continuidade) e, com o maior Vd da marca, o menor dente
(altura de 5 em 5 cm) que passa na NBR 9062:2017 7.4 (consolo invertido + biela τwd ≤ 0,18 fck/1,4) e no PCI (Vmax),
com γn = 1,2 (obra = pré-moldado, 12.1.1; parcela variável ~45 % da reação → não preponderantemente permanente, 7.3.1.1).
O consolo do pilar tem a largura da face do pilar (40). O MEF em 2 fases (mef_vm_largura_fases.py) confirma os candidatos.
Saída: estudo_vm_largura.json.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

AQ = Path(__file__).resolve().parent
sys.path.insert(0, str(AQ.parents[1]))
sys.path.insert(0, str(AQ))
import calc_vm_retangular as R
import calc_vm_dente as D
from nd_estruturas.dente_consolo import Dente

GN = 1.2                                        # NBR 9062:2017 7.3.1.1 (pré-moldado, variável não preponderante)
QTD = {"VM-01": 8, "VM-02": 8, "VM-03": 2, "VM-04": 2}  # mesma contagem do ranking de calc_vm_retangular
B_CONSOLO = 0.40                                # face do pilar


def dente_ok(b, h, hd, Vd):
    Fd = GN * Vd
    dt = Dente("VM", Fd, 0.16 * Fd, b * 1000, hd * 1000, D.LN * 1000, (D.X_PAD - 0.03) * 1000, h * 1000, fck=40.0).dimensionar(16.0, 16.0)
    con = D.consolo(B_CONSOLO, D.PROJ, h - hd - 0.021, D.A_CONS, Fd)
    ok = dt["NBR"]["ok_biela"] and dt["PCI"]["ok_Vmax"] and bool(con and con["ok"])
    return ok, dict(Fd=round(Fd, 1), tau_wd=dt["NBR"]["tau_wd"], tau_lim=dt["NBR"]["tau_lim"], PCI_Vmax=dt["PCI"]["Vmax_kN"],
                    tirante=dt["adotado"]["tirante"], suspensao=dt["adotado"]["suspensao"], costura=dt["adotado"]["costura"],
                    consolo=None if not con else dict(h=con["h"], tirante=con["tirante"], tau=con["tau"], tau_u=con["tau_u"], ok=con["ok"]),
                    adotado=dt["adotado"])


def marca(b, h, mk):
    xs = int(round((b - 0.10) / 0.05)) + 1
    for n in range(4, 3 * xs + 1, 2):
        rs = [R.analisar(b, h, n, mk, c) for c in R.MARCA_CASOS[mk]]
        if all(r["ok_geral"] for r in rs):
            break
    else:
        return None
    Vd = max(r["cortante"]["Vd"] for r in rs)
    for hd in [round(0.25 + 0.05 * k, 2) for k in range(14) if 0.25 + 0.05 * k <= h - 0.20 + 1e-9]:
        ok, dd = dente_ok(b, h, hd, Vd)
        if ok:
            break
    else:
        return dict(marca=mk, b=b, h=h, n_inf=n, dente_ok=False, Vd=Vd)
    gov = max(rs, key=lambda r: r["ELU"]["M2d"])
    Lp = rs[0]["L_peca"]
    V = b * h * Lp - 2 * b * (h - hd) * D.LN
    kg_cord = (n + 2) * 0.775 * Lp
    As_d = dd["adotado"]
    kg_aco = 105 * V + 2 * (As_d["As_tir"] + As_d["As_sus"] + As_d["As_cost"]) / 100 * 1.2 * 0.785
    area_forma = (2 * h + b) * Lp                                # m² de fôrma (laterais + fundo)
    custo = V * R.PRECO["concreto"] + kg_cord * R.PRECO["cordoalha"] + kg_aco * R.PRECO["aco"]
    return dict(marca=mk, b=b, h=h, hd=hd, recorte=round(h - hd, 2), n_inf=n, n_cord=n + 2, Vd=round(Vd, 1), dente_ok=True, dente=dd,
                L_peca=Lp, L_calculo=gov["L_calculo"], cargas=gov["cargas"], pos_cordoalhas_mm=gov["pos_cordoalhas_mm"],
                isoladas_pontas=gov["isoladas_pontas"], sig_pinf=gov["protensao"]["perdas"]["sig_pinf"], lbpt_m=gov["ato"]["lbpt_m"],
                ELU=gov["ELU"], ELS=gov["ELS"], flecha=gov["flecha"], V_m3=round(V, 3), peso_t=round(V * 2.5, 2),
                kg_cord=round(kg_cord, 1), kg_aco=round(kg_aco, 1), forma_m2=round(area_forma, 2), custo_indice=round(custo))


def varrer(b):
    for h in [round(0.50 + 0.05 * k, 2) for k in range(9)]:
        sols = {mk: marca(b, h, mk) for mk in R.VAOS}
        if all(s and s["dente_ok"] for s in sols.values()):
            hd = max(s["hd"] for s in sols.values())                 # um dente só na fôrma (o da marca mais carregada)
            for mk, s in sols.items():
                if s["hd"] != hd:
                    ok, dd = dente_ok(b, h, hd, s["Vd"])
                    s.update(hd=hd, recorte=round(h - hd, 2), dente=dd)
            custo = sum(s["custo_indice"] * QTD[mk] for mk, s in sols.items())
            return dict(b=b, h=h, hd=hd, custo_total=custo, faixa_2e=round(b - 0.12, 2),
                        fundo=[round(z - 0.26 - h, 3) for z in R.Z_PISOS], solucoes=sols)
    return None


if __name__ == "__main__":
    out = []
    for b in (0.25, 0.30, 0.35, 0.40):
        r = varrer(b)
        if r:
            print(b, r["h"], r["hd"], r["custo_total"], {mk: (s["n_cord"], s["dente"]["tau_wd"], s["dente"]["PCI_Vmax"], s["dente"]["Fd"]) for mk, s in r["solucoes"].items()})
            out.append(r)
        else:
            print(b, "sem solução até h 0,90")
    (AQ / "estudo_vm_largura.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
