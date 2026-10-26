"""DEC-042 — checagem geométrica de colisão na região da platibanda (cabeça dos pilares), com as caixas envolventes reais do
modelo 3D (modelo_bim.montar()), não visual.

1) CE-1 (chapa de espera 380 × 330) apoiada no concreto: a chapa tem de ficar inteira dentro da face do pilar onde está
   (corpo ou cabeça), com folga ≥ 4 mm até a aresta; acusa a chapa que sai do concreto (caso dos cantos antes da DEC-042).
2) Interpenetração (> 1 mm) entre a cabeça de concreto de cada pilar e qualquer peça que não seja embutida nela
   (telhas, calha, terças, suportes ST, cantoneiras, rufos, placas, VB, TS-01, consoles CS-1).
Saída: colisao_platibanda.json."""
import json, sys
from pathlib import Path
AQ = Path(__file__).parent
sys.path.insert(0, str(AQ)); sys.path.insert(0, str(AQ.parent.parent))
import modelo_bim as MB
from colisao_ct1 import aabb, pen

EMBUTIDAS = ("pino", "espera", "ES-", "bucha", "chumbador", "PN-", "N18", "grampo", "BR-", "barra roscada", "porca", "TB-", "tubo",
             "neoprene", "NEO", "alça", "AL-", "FI-1", "M16", "M20", "M12", "graute", "junta", "CE-1")


def main():
    m = MB.montar()
    pecas = [(p, aabb(p)) for p in m.pecas]
    conc = [(p, bb) for p, bb in pecas if p.grupo == "Pilares"]
    cab = [(p, bb) for p, bb in conc if p.marca.endswith(" cabeça")]
    # DEC-042: cantos de seção cheia — a parte acima de +8,50 conta como "cabeça" (região da platibanda)
    cab += [(p, ((a[0], a[1], max(a[2], 8.50)), b)) for p, (a, b) in conc
            if not p.marca.endswith(" cabeça") and b[2] > 9.99 and a[2] < 8.0 and (a[1] < 0.5 or b[1] > MB.COMP - 0.5) and (a[0] < 0.5 or b[0] > MB.LARG - 0.5)]
    ce = [(p, bb) for p, bb in pecas if p.marca.startswith("CE-1 chapa")]
    res = dict(ce1_fora=[], colisoes=[], n_ce1=len(ce), n_cabecas=len(cab))
    # 1) CE-1 dentro de uma face de concreto
    for p, (a, b) in ce:
        ok = False
        # rev12: a face pode ser formada por mais de uma caixa do mesmo pilar (corpo + cabeça rentes, peça monolítica):
        # a chapa está ok se cada ponto de uma grade 9 × 9 sobre ela cai dentro (folga 4 mm) de alguma caixa que toca o plano dela
        for ax in range(3):
            outros = [i for i in range(3) if i != ax]
            toc = [(c, d) for q, (c, d) in conc if min(abs(a[ax] - d[ax]), abs(b[ax] - c[ax]), abs(b[ax] - d[ax]), abs(a[ax] - c[ax])) < 0.003
                   and all(c[i] < b[i] and d[i] > a[i] for i in outros)]
            if not toc:
                continue
            lo = [a[o] - 0.004 for o in outros]; hi = [b[o] + 0.004 for o in outros]          # chapa + 4 mm de borda de concreto
            pts = [(lo[0] + (hi[0] - lo[0]) * u / 8, lo[1] + (hi[1] - lo[1]) * w / 8) for u in range(9) for w in range(9)]
            cob_ = lambda pt: any(c[outros[0]] - 1e-6 <= pt[0] <= d[outros[0]] + 1e-6 and c[outros[1]] - 1e-6 <= pt[1] <= d[outros[1]] + 1e-6 for c, d in toc)
            if all(cob_(pt) for pt in pts):
                ok = True
                break
        if not ok:
            res["ce1_fora"].append(dict(peca=p.marca, xyz_min=[round(v, 3) for v in a], xyz_max=[round(v, 3) for v in b]))
    # 2) cabeça × demais peças
    for q, cb in cab:
        for p, bb in pecas:
            if p is q or p.grupo in ("Pilares", "Rufos e acabamentos") or any(t.lower() in p.marca.lower() for t in EMBUTIDAS):
                continue                                         # rufos: chapas dobradas sobre a cabeça (a caixa envolvente engloba o concreto)
                continue
            e = pen(cb, bb)
            if e > 0.001 and p.perfil.b <= 0.04 and p.perfil.h <= 0.04 and p.comprimento > 0.5:
                # rev11: barra esbelta inclinada (X Ø16, corrente): a caixa envolvente engana — testa o eixo amostrado
                r_ = max(p.perfil.b, p.perfil.h) / 2
                n_ = max(2, int(p.comprimento / 0.002))
                e = max(min(min(p.p0[i] + (p.p1[i] - p.p0[i]) * k / n_ - (cb[0][i] - r_), (cb[1][i] + r_) - (p.p0[i] + (p.p1[i] - p.p0[i]) * k / n_))
                            for i in range(3)) for k in range(n_ + 1))
            if e > 0.001:
                res["colisoes"].append(dict(cabeca=q.marca, peca=p.marca, grupo=p.grupo, penetracao_mm=round(e * 1000, 1)))
    (AQ / "colisao_platibanda.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"CE-1: {len(ce)} chapas, {len(res['ce1_fora'])} fora do concreto | cabeças: {len(cab)}, colisões: {len(res['colisoes'])}")
    for r in res["ce1_fora"][:12]:
        print("  CE-1 fora:", r)
    for r in res["colisoes"][:20]:
        print("  colisão:", r)
    return res


if __name__ == "__main__":
    main()
