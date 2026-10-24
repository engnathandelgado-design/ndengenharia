"""Letsara rev09 (23/10/2026) — vigas do mezanino RETANGULARES PROTENDIDAS com 2º estágio (decisão do Nathan, DEC-047).

Substitui o meio vaso (calc_vm_meio_vaso.py). Seção pré-moldada b × h (b = 25, 30 ou 40; h de 5 em 5 cm); a laje alveolar
apoia 10 cm sobre o TOPO da viga (fita de neoprene 1 cm) e no restante da largura (b − 10 cm) saem os estribos em alça para o
2º estágio, concretado com a capa (C30, de obra). Topo da capa +3,90 / +7,30 (geometria.Z_PISOS); topo da viga = capa − 0,26.

Mesmo motor do meio vaso (calc_vm_meio_vaso.analisar), com a aba zerada: fases F0 (ato, içamento), F1 (montagem sem
escoramento: peça isolada + laje + capa + 2º estágio frescos + 1 kN/m²) e F2 (seção composta com 2º estágio e capa);
protensão completa (DEC-043); flechas NBR 9062:2017 Tab. 9; interface 6.3.3. SEM torção de montagem: as pontas são
concretadas dos dois lados antes das lajes (regra do Nathan, DEC-039) — a verificação de torção não entra.
Dente Gerber na ponta (preferência ND, fundo do consolo alinhado ao da viga): NBR 9062:2017 7.4 = consolo 7.3
(calc_vm_dente.consolo) e suspensão Fd/fyd.

Casos (kN/m² nas lajes; NBR 6120:2019):
  +3,90 piso (escritório/depósito do arquitetônico): sobrecarga 5,0, revestimento 1,0;
  +7,30 laje de cobertura do bloco SEM USO: Tabela 10 "coberturas com acesso apenas para manutenção" 1,0; revestimento
        (regularização + impermeabilização 8 cm do arquitetônico, γ 21) 1,7;
  linha 2 do +7,30: + cobertura metálica da linha 2 (W 150 sobre montantes, cob_linha2.json) como carga equivalente.
Marcas: VM-01 (vãos de ponta A–B / D–E, 9,37 entre faces), VM-02 (B–C / C–D, 9,48), VM-03 (linha 2, D → P6, 6,22),
VM-04 (P6 → E na linha 2 do +7,30 e P6–P7 da escada no +3,90, 2,90). Mesma seção em todas (largura única = largura da
laje igual em toda a obra); cordoalhas pela marca mais carregada de cada comprimento.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

AQ = Path(__file__).parent
sys.path.insert(0, str(AQ.parents[1]))
sys.path.insert(0, str(AQ))
import calc_vm_meio_vaso as M
import calc_vm_dente as D
from geometria import Z_PISOS

PRECO = D.PRECO
# rev09: apoio com neoprene fretado NEO-5F 200 × 200 (σ ≤ 11 MPa p/ a ≤ 200, NBR 9062:2017 7.2.1.6) — a2 ≥ c + 3,5Ø dos dois lados
# pede nariz do dente e projeção do consolo de 40 cm (o 150 × 300 do meio vaso não cabe na largura 25)
D.LN, D.PROJ, D.A_PAD, D.B_PAD = 0.40, 0.40, 0.20, 0.20
D.X_PAD = 0.111 + D.A_PAD / 2
D.A_CONS = D.X_PAD
D.A_DENTE = D.FOLGA + D.LN - D.X_PAD
GN = 1.2                                                   # NBR 9062:2017 7.3.1.1 (pré-moldado; variável ~45 % da reação, não preponderante — DEC-049)
FOLGA = 0.03
VAOS = {"VM-01": 9.37, "VM-02": 9.48, "VM-03": 6.22, "VM-04": 2.90}

# cobertura metálica da linha 2 sobre a viga do +7,30 (kN/m da linha, característicos): G_COB × faixa + W 150 + montantes
TRIB_L2 = (9.65 + 10.075) / 2
_LG = json.loads((AQ / "ligacoes.json").read_text(encoding="utf-8"))
G_COB = _LG["cargas_cob"]["g_total_sem_terca"] + 0.123 / _LG["passo_tercas"]
G_ROOF = G_COB * TRIB_L2 + 0.221 + 0.05                    # W 150 × 22,5 + montantes (média)
Q_ROOF = _LG["cargas_cob"]["sobrecarga"] * TRIB_L2
F_PONTUAL = 1.06                                           # montante no meio do vão (PL/4) × carga distribuída (wL²/8)

# DEC-047: sobrecarga do 2º pavimento (+3,90, "Depósito" no arquitetônico) — 5,0 kN/m² CONFIRMADA PELO NATHAN (23/10/2026); valor único da obra
_CM = json.loads((AQ / "cargas_mezanino.json").read_text(encoding="utf-8"))
Q_PISO_390 = _CM["piso_390"]["sobrecarga"]
CASOS = {
    "+3,90": dict(q=Q_PISO_390, rev=_CM["piso_390"]["revestimento"], roof=False),
    "+7,30 linha 1": dict(q=_CM["laje_730"]["sobrecarga"], rev=_CM["laje_730"]["revestimento"], roof=False),
    "+7,30 linha 2": dict(q=_CM["laje_730"]["sobrecarga"], rev=_CM["laje_730"]["revestimento"], roof=False),     # DEC-048 (opção 2): cobertura da linha 2 nos pilares, não na viga
    "+3,90 P6–P7": dict(q=Q_PISO_390, rev=_CM["piso_390"]["revestimento"], roof=False, trib=(3.79 - 0.25) / 2),
}
# quais casos cada marca enfrenta
MARCA_CASOS = {"VM-01": ["+3,90", "+7,30 linha 1", "+7,30 linha 2"], "VM-02": ["+3,90", "+7,30 linha 1", "+7,30 linha 2"],
               "VM-03": ["+3,90", "+7,30 linha 2"], "VM-04": ["+3,90 P6–P7", "+7,30 linha 2"]}


def cordoalhas_ret(n, h, n_top=0, b=None):
    """Grade 50 mm na largura (linhas a 50/120/190 mm do fundo), simétrica; n_top no topo a 50 mm, simétricas."""
    b = b or M.B_ALMA
    xs = [round(0.050 + 0.050 * k, 3) for k in range(int(round((b - 0.100) / 0.050)) + 1)]
    pos = []
    for y in M.Y_LINHAS:
        resto = n - len(pos)
        if resto <= 0:
            break
        if resto >= len(xs):
            linha = xs
        else:                                              # linha incompleta: pares simétricos a partir das bordas
            linha = []
            i, j = 0, len(xs) - 1
            while len(linha) < resto and i <= j:
                linha.append(xs[i])
                if len(linha) < resto and j != i:
                    linha.append(xs[j])
                i += 1; j -= 1
        pos += [(x, y) for x in linha]
    top = [(round(b / 2 - 0.05, 3), h - 0.05), (round(b / 2 + 0.05, 3), h - 0.05)][:n_top]
    return pos + top


def preparar(b, caso):
    """Seção retangular b (aba zerada) e cargas do caso."""
    M.B_ALMA, M.B_ABA, M.H_ABA = b, 0.0, 0.0
    M.B_TOT = b
    M.X_PONTA_LAJE = b - M.APOIO_LAJE
    M.VAO_LAJE = 9.65 - 2 * (b / 2 - M.APOIO_LAJE)
    M.TRIB = CASOS[caso].get("trib", M.VAO_LAJE / 2)
    c = CASOS[caso]
    larg = M.TRIB + b
    extra_g = (G_ROOF * F_PONTUAL / larg) if c["roof"] else 0.0
    extra_q = (Q_ROOF * F_PONTUAL / larg) if c["roof"] else 0.0
    M.REV, M.Q_MEZ = c["rev"] + extra_g, c["q"] + extra_q
    M.cordoalhas = lambda n, h, n_top=0: cordoalhas_ret(n, h, n_top, b)
    M.retangulos = lambda h: [(0.0, b, 0.0, h)]
    M.X_PAD = D.X_PAD
    M.DENTE = dict(M.DENTE, hd=HD_ADOT, recorte=round(H_ADOT - HD_ADOT, 2), consolo_h=round(H_ADOT - HD_ADOT - 0.021, 3))   # dente adotado (DEC-049) na negativa


def negativa_ret(L, g2, q2, h=0.80, n12=9):
    """Continuidade (F2) sobre os apoios internos — mesma formulação de calc_vm_meio_vaso.negativa (NBR 9062:2017 5.1.2.9 e
    5.1.2.10 tipologia 1), seção retangular 25: N11 6 Ø16 em 2 bainhas no pilar + N12 n12 Ø12,5 na capa."""
    hd = M.DENTE["hd"]
    Md = (1.4 * 0.107 * g2 + 1.4 * 0.121 * q2) * L ** 2
    d1, d2 = hd + 0.12, hd + M.H_LAJE + M.H_CAPA - 0.03
    A1, A2 = 6 * math.pi * 1.6 ** 2 / 4, n12 * math.pi * 1.25 ** 2 / 4
    T = (A1 + A2) * 1e-4 * M.FYD_ALCA
    x = T / (0.85 * M.FCD * M.B_TOT * 0.8)
    dm = (A1 * d1 + A2 * d2) / (A1 + A2)
    MRd_ = T * (dm - 0.4 * x)
    Led = 25 * 0.016 + M.X_PAD
    Rsec = 0.75 * (A1 + A2) * 1e-4 * M.ES * dm ** 2 / Led
    return dict(Md_kNm=round(Md, 1), MRd_kNm=round(MRd_, 1), secao=f"face do pilar: nariz {M.B_TOT*100:.0f} × {hd*100:.0f} + 2º estágio + capa",
                d_pilar_m=round(d1, 3), d_capa_m=round(d2, 3), x_m=round(x, 3), x_d=round(x / dm, 3),
                adotado=f"N11: 6 Ø16 em 2 bainhas corrugadas Ø50 no pilar (3 em cada, graute) + N12: {n12} Ø12,5 na capa; L = 600 cm (armadura de obra)",
                As_ef_cm2=round(A1 + A2, 2), frac_no_pilar=round(A1 / (A1 + A2), 2), ok=MRd_ >= Md and A1 / (A1 + A2) >= 0.5 and x / dm <= 0.45,
                Rsec_kNm_rad=round(Rsec), Led_m=round(Led, 3), norma="NBR 9062:2017 5.1.2.9 e 5.1.2.10 (tipologia 1)")


def analisar(b, h, n, marca, caso, n_top=2):
    preparar(b, caso)
    r = M.analisar(h, n, marca, VAOS[marca], n_top=n_top, n_isol=2 if n >= 6 else 0)
    r["negativa"] = negativa_ret(r["L_calculo"], r["cargas"]["g2"], r["cargas"]["q2"], h)
    r["ok"]["negativa"] = r["negativa"]["ok"]
    # sem torção de montagem (pontas concretadas dos dois lados antes das lajes — DEC-039): fora da verificação
    for k in ("torcao", "apoio"):
        r["ok"].pop(k, None)
    r.pop("torcao_montagem", None)
    r["ok_geral"] = all(r["ok"].values())
    r["caso"] = caso
    return r


def dente(b, h, hd, Vd):
    Fd = GN * Vd
    den = D.consolo(b, D.LN, hd, D.A_DENTE, Fd)
    con = D.consolo(B_CONSOLO, D.PROJ, h - hd - 0.021, D.A_CONS, Fd)      # DEC-049: consolo com a largura da face do pilar (40); NEO-5F 200 × 200 × 21
    from nd_estruturas.dente_consolo import Dente as _Dente                 # NBR 9062:2017 7.4 (biela τwd) + PCI (Vmax), como no estudo_vm_largura
    nbr = _Dente("VM", Fd, 0.16 * Fd, b * 1000, hd * 1000, D.LN * 1000, (D.X_PAD - 0.03) * 1000, h * 1000, fck=40.0).dimensionar(16.0, 20.0)
    As_sus = Fd / 43.5
    sus = math.ceil(As_sus / (2 * 2.011))
    ok = bool(den and con and den["ok"] and con["ok"] and nbr["NBR"]["ok_biela"] and nbr["PCI"]["ok_Vmax"])
    return dict(Fd=round(Fd, 1), dente=den, consolo=con, As_sus=round(As_sus, 2), nbr_pci=dict(NBR=nbr["NBR"], PCI=nbr["PCI"], adotado=nbr["adotado"]),
                suspensao=f"{sus} estribos fechados Ø16 (2 ramos) = {sus * 4.02:.1f} cm² ≥ {As_sus:.1f}", n_sus=sus, ok=ok)


def solucao(b, h, marca):
    """Menor nº de cordoalhas que passa em TODOS os casos da marca; dente com o maior Vd; custo índice."""
    for n in range(4, 3 * len([0.05 + 0.05 * k for k in range(int(round((b - 0.10) / 0.05)) + 1)]) + 1, 2):
        rs = [analisar(b, h, n, marca, c) for c in MARCA_CASOS[marca]]
        if all(r["ok_geral"] for r in rs):
            break
    else:
        return None
    Vd = max(r["cortante"]["Vd"] for r in rs)
    best = None
    for hd in [round(0.25 + 0.05 * k, 2) for k in range(12) if 0.25 + 0.05 * k <= h - 0.20]:
        dt = dente(b, h, hd, Vd)
        if dt["ok"]:
            best = (hd, dt)
            break
    if not best:
        return None
    hd, dt = best
    Lp = rs[0]["L_peca"]
    V = b * h * Lp - 2 * b * (h - hd) * D.LN
    kg_cord = (n + 2) * 0.775 * Lp
    kg_aco = 105 * V + 2 * (dt["dente"]["As"] + dt["As_sus"]) * 1.2 * 0.785
    custo = V * PRECO["concreto"] + kg_cord * PRECO["cordoalha"] + kg_aco * PRECO["aco"]
    return dict(marca=marca, b=b, h=h, hd=hd, recorte=round(h - hd, 2), n_inf=n, n_sup=2, n_cord=n + 2, casos=rs, dente=dt,
                V_m3=round(V, 3), peso_t=round(V * 2.5, 2), kg_cord=round(kg_cord, 1), kg_aco=round(kg_aco, 1), custo_indice=round(custo),
                h_final=round(h + 0.26, 2), fundo=[round(z - 0.26 - h, 3) for z in Z_PISOS])


def faixa_2e(b):
    """Faixa livre de 2º estágio sobre a viga para a chapa de base dos montantes: b − apoio 10 − folga 2 cm."""
    return round(b - M.APOIO_LAJE - 0.02, 3)


B_ADOT, H_ADOT, HD_ADOT = 0.30, 0.75, 0.45                 # DEC-049 (Nathan, 23/10, estudo_vm_largura): fôrma única 30 × 75, dente Gerber 45
B_CONSOLO = 0.40                                           # consolo CP-MEZ com a largura da face do pilar


def adotada():
    """Solução adotada: mesma seção e mesmo dente em todas as marcas; cordoalhas por marca."""
    out = {}
    for mk in VAOS:
        for n in range(4, 31, 2):
            rs = [analisar(B_ADOT, H_ADOT, n, mk, c) for c in MARCA_CASOS[mk]]
            if all(r["ok_geral"] for r in rs):
                break
        Vd = max(r["cortante"]["Vd"] for r in rs)
        dt = dente(B_ADOT, H_ADOT, HD_ADOT, Vd)
        Lp = rs[0]["L_peca"]
        V = B_ADOT * H_ADOT * Lp - 2 * B_ADOT * (H_ADOT - HD_ADOT) * D.LN
        gov = max(rs, key=lambda r: r["ELU"]["M2d"])               # caso que governa (+3,90): campos no topo (compatível com vm_meio_vaso.json)
        out[mk] = dict({k: v for k, v in gov.items() if k not in ("marca", "ok", "ok_geral")}, marca=mk, n_inf=n, n_sup=2, n_cord=n + 2, L_faces=VAOS[mk], L_peca=Lp, casos=rs, dente=dt, V_m3=round(V, 3), peso_t=round(V * 2.5, 2), caso_governa=gov["caso"],
                       kg_cord=round((n + 2) * 0.775 * Lp, 1), ok=all(r["ok_geral"] for r in rs) and dt["ok"])
    return out


if __name__ == "__main__" and "--adotada" in sys.argv:
    sol = adotada()
    for mk, s_ in sol.items():
        print(mk, s_["ok"], s_["n_cord"], s_["dente"]["Fd"], s_["dente"]["dente"]["tirante"], s_["dente"]["consolo"]["tirante"], [ (r["caso"], round(r["ELU"]["M2d"]/r["ELU"]["MRd2"],2), r["ELS"]["sig_D"]) for r in s_["casos"]])
    prem = dict(fck=M.FCK, fckj=M.FCKJ, fcj_icamento=M.FCKJ, fck_2estagio=M.FCK2, tipo="pré-moldado (NBR 9062:2017 12.1.1)", gama_c=M.GC_PF, gama_s=M.GS_PF,
                folga_m=FOLGA, neoprene=M.PAD, sem_escoramento=True, Eci_MPa=round(M.ECI(M.FCK) / 1e3), Ecs_MPa=round(M.ECS(M.FCK) / 1e3),
                h_pm=H_ADOT, b=B_ADOT, b_alma=B_ADOT, b_aba=0.0, h_aba=0.0, apoio_laje=M.APOIO_LAJE, faixa_2e=faixa_2e(B_ADOT),
                dente=dict(hd=HD_ADOT, ln=D.LN, recorte=round(H_ADOT - HD_ADOT, 2), consolo_h=round(H_ADOT - HD_ADOT - 0.021, 3), consolo_proj=D.PROJ, macico=1.00),
                x_pad=D.X_PAD, pad=(200, 200, 21), vao_laje=round(9.65 - 2 * (B_ADOT / 2 - M.APOIO_LAJE), 3), q_piso_390=Q_PISO_390,
                decisao="DEC-049: retangular protendida 30 × 75 em todas (fôrma única), dente Gerber 45 × 40, consolo 40 × 40 × 27,9; suspensão 3 Ø20 + 4 Ø16 retas no fundo", b_consolo=B_CONSOLO, extra_inf=[dict(n=4, d=16.0, y=110, L=2500)])
    (AQ / "vm_retangular.json").write_text(json.dumps(dict(sol, premissas=prem), indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    sys.exit()

if __name__ == "__main__":
    tab = {}
    for b in (0.25, 0.30, 0.40):
        for h in [round(0.40 + 0.05 * k, 2) for k in range(11)]:
            sols = {mk: solucao(b, h, mk) for mk in VAOS}
            if all(sols.values()):
                tab[(b, h)] = sols
                break                                          # menor h que passa nesta largura
    resumo = []
    for (b, h), sols in tab.items():
        L1 = sum(s["custo_indice"] * q for s, q in zip(sols.values(), (8, 8, 2, 2)))   # quantidades por marca (2 níveis)
        resumo.append(dict(b=b, h=h, custo_total=L1, cord={k: s["n_cord"] for k, s in sols.items()}, hd={k: s["hd"] for k, s in sols.items()},
                           faixa_2e_m=faixa_2e(b), fundo_390=sols["VM-02"]["fundo"][0]))
    resumo.sort(key=lambda r: r["custo_total"])
    for r in resumo:
        print(r)
    out = dict(ranking=resumo, solucoes={f"{b:.2f}x{h:.2f}": {k: {kk: vv for kk, vv in s.items()} for k, s in sols.items()} for (b, h), sols in tab.items()})
    (AQ / "vm_retangular_estudo.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
