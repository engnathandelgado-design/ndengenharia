"""Prancha genérica de pilar pré-moldado (em pé, faces A/B/C/D, consolos em qualquer face) — padrão ND.
Usada por PC-01/02 (centrais 50×50) e PM-01 (mezanino 40×60). Rodar: python pilar_generico.py pc | pm
Faces: A = x+, B = y+, C = x−, D = y−. Modelo em mm; cotas de concreto em cm; chaparia em mm."""
import json, math, subprocess, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from prancha_nd import Prancha, ALTURAS, _wtext, quebrar


def tabela_q(pr, x, y_topo, titulo, cab, linhas, larg, h_lin=6.0, h_sub=4.2):
    """rev08: tabela com quebra automática de linha nas células (texto que não cabe na coluna desce em 2+ linhas).
    Mesmo desenho e registro (_tabs, blocos_livres) do Prancha.tabela."""
    pr.__dict__.setdefault("_tabs", []).append(dict(titulo=titulo, cab=list(cab), linhas=[[str(c) for c in l] for l in linhas]))
    hn = ALTURAS["nota"]
    W = sum(larg)
    y = y_topo
    pr.ret(x, y - 8, x + W, y, "TABELA")
    pr.texto(x + W / 2, y - 4, titulo, "sub", "TITULO", "MIDDLE_CENTER")
    y -= 8
    for row_i, row in enumerate([cab] + [list(l) for l in linhas]):
        import renomear as _RN
        cel = [quebrar(_RN.renomear(str(c)), w - 2.0, hn) or [""] for c, w in zip(row, larg)]   # nomes novos antes de medir
        n = max(len(c) for c in cel)
        hr = h_lin if n == 1 else h_lin + (n - 1) * h_sub
        pr.linha((x, y - hr), (x + W, y - hr), "TABELA" if row_i == 0 else "TABELA_FINA")
        xx = x
        for c, w in zip(cel, larg):
            y0 = y - hr / 2 + (len(c) - 1) * h_sub / 2
            for k, t in enumerate(c):
                pr.texto(xx + w / 2, y0 - k * h_sub, "\x01" + t, "nota", "TEXTO", "MIDDLE_CENTER")
            xx += w
        y -= hr
    xx = x
    for w in larg[:-1]:
        xx += w
        pr.linha((xx, y_topo - 8), (xx, y), "TABELA_FINA")
    pr.ret(x, y, x + W, y_topo, "TABELA")
    pr.blocos_livres.append((x, y, x + W, y_topo, titulo))
    return y

f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
sys.path.insert(0, "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara")
from geometria import Y_LIN, X_FACH, X_EIXO, Y_P13
CONS_J = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/consolos.json"))
LG = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/ligacoes.json"))
ZF = lambda x: LG["Z0_TS"] + 0.03 * x
ASS_TS = lambda x: round((ZF(x) + 0.45 * (1 / (1 + 0.03 ** 2)) ** 0.5 - 0.01) * 1000)
Z_I130 = round(LG["Z_ASS_I130"] * 1000)                          # rev03: assento da I130 = topo − 1,30 + recorte 0,52 − neoprene 0,03
Z_TOP_C = round(LG["Z_TOPO_I130"] * 1000)                         # rev03: topo dos pilares centrais = topo da I130 (TS-01 apoiada no topo)
Z_TOP_CD = round(LG["Z_TOPO_I130_DIR"] * 1000)                    # rev04: metade do lado E do topo (degrau, NBR 9062 7.2.1.6: assentos horizontais)
_VMP = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/vm_meio_vaso.json"))["premissas"]
# rev04: VM meio vaso com dente: assento do CP-MEZ = piso − capa 5 − laje 20 − fita 1 − h da VM + recorte − neoprene 1
Z_MEZ_ASS = tuple(round(z - 260 - _VMP["h_pm"] * 1000 + _VMP["dente"]["recorte"] * 1000 - 10) for z in (3150, 6550))
H_C = {k: round(v["h_total_m"] * 1000) for k, v in CONS_J.items()}
import geo_fixacao as GF
CS = GF.C
XC_CS = 10 + GF.N["B"] / 2                     # rev06e: eixo do CS-1 a 80 mm do eixo do pilar (junta 20/2 + eixo do nicho 70)
ZT_CS = 940 + GF.N["H"] / 2 - GF.N["t_teto"] - GF.T["G"] - 922   # topo da mesa do CS-1 acima do centro da CE-1 (54,5)
IP_C = [1250 * k + 922 + 1000 for k in range(6)]    # rev06: CE-1 (centro)            # CE-1 das paredes internas (vistas C e G): fiadas 0 a 5 (até +7,50)
COB = 30
# direção horizontal de cada vista (olhando a face de fora, z para cima): (eixo, sinal) -> coordenada à direita
VISTA = {"A": ("y", 1), "B": ("x", -1), "C": ("y", -1), "D": ("x", 1)}
DIR = {"A": "B", "B": "C", "C": "D", "D": "A"}                    # face à direita de quem olha a face de fora
ESQ = {"A": "D", "B": "A", "C": "B", "D": "C"}
OPOSTA = {"A": "C", "B": "D", "C": "A", "D": "B"}


def furo_icamento(P, L_TOT, REC, cons):
    """rev07: furo de içamento FI-1 (verticalizar e montar, padrão usina): tubo Ø60 perdido, transversal, acima do CG, no corpo
    logo abaixo do recuo da cabeça; foge de consolos e CE-1.
    rev08: o eixo do furo é escolhido pelo caminho das lingas — nas duas faces por onde saem o pino e as manilhas não pode haver
    nada saliente ACIMA do furo (consolo de concreto ou CC-1 com console soldado), senão a linga apoia na peça ao verticalizar/montar.
    CE-1 rente (faces laterais) não atrapalha. Se nenhum eixo ficar livre, fica o padrão e a folha avisa (ver pendências)."""
    faces_ip = {ip["face"] for ip in P.get("ip01", [])}
    alvo = (REC["z"] - 450) if REC else (L_TOT - 700)
    zs_ip = [z for ip in P.get("ip01", []) for z in ip["z"]]

    def cota_z():
        for d_ in sorted(range(-1500, 1501, 25), key=abs):
            z = alvo + d_
            if z > (REC["z"] - 200 if REC else L_TOT - 400) or z < L_TOT * 0.55:
                continue
            if any(abs(z - zc) < 165 + 120 for zc in zs_ip):
                continue
            if any(c["z"] - c["h"] - 150 < z < c["z"] + 150 for c in cons):
                continue
            return z
        return alvo

    z = cota_z()
    def sem_consolo(eixo):               # consolo ou pino de apoio (já embutido na fábrica) acima do furo
        return not any(c["face"] in eixo and max(c["z"] - c["h"], c["z"] + c.get("pino_L", 0) - c.get("pino_emb", 0)) > z - 50 for c in cons)
    def sem_cc1(eixo):                   # CC-1: console metálico de fábrica saindo 64 mm da face C
        return not any(ip["face"] == "C" and "C" in eixo and ip.get("lados") and max(ip["z"]) > z for ip in P.get("ip01", []))
    livre = lambda e: sem_consolo(e) and sem_cc1(e)
    padrao = "AC" if (faces_ip & {"B", "D"}) else "BD"
    outro = "AC" if padrao == "BD" else "BD"
    eixo = next((e for e in (padrao, outro) if livre(e)), None) or next((e for e in (padrao, outro) if sem_consolo(e)), padrao)
    obst = "" if livre(eixo) else ("consoles CC-1 (64 mm)" if sem_consolo(eixo) else "consolo de concreto")
    return dict(z=z, eixo=eixo, d=60, livre=livre(eixo), obst=obst)


def prancha_pilar(P):
    B, H, L_CAL, Z_TOP = P["B"], P["H"], P["L_CAL"], P["Z_TOP"]
    L_TOT = L_CAL + Z_TOP
    D1 = P.get("d1", 20.0)
    AL = P["al"]
    cons = P["consolos"]
    REC = P.get("rec")                                                   # cabeça recuada: dict(z = nível abs (mm), d = {face: recuo mm})
    rd = (lambda fc: REC["d"].get(fc, 0)) if REC else (lambda fc: 0)
    z_rec = REC["z"] if REC else L_TOT
    HB, HH = B - rd("B") - rd("D"), H - rd("A") - rd("C")               # seção da cabeça (B–D × A–C)
    V = (B * H * z_rec + HB * HH * (L_TOT - z_rec)) / 1e9 + sum(c["larg"] * c["proj"] * c["h"] for c in cons) / 1e9
    PESO = V * 25
    FI = furo_icamento(P, L_TOT, REC, cons)
    if not FI["livre"]:
        print(f"  ! {P['marca']}: FI-1 {FI['eixo']} com {FI['obst']} acima do furo nas faces das lingas (nenhum eixo livre)")
    json.dump(dict(fi=FI, B=B, H=H, L_TOT=L_TOT, consolos=cons, ip01=P.get("ip01", []), al=AL, al_face=P.get("al_face", "A"), marca=P["marca"], z_topo=Z_TOP / 1000, zoom=P.get("zoom", 3.2), rec=REC,
                   assento=P.get("assento"), pinos_topo=P.get("pinos_topo")),
              open(f"/home/claude/letsara/pranchas/{P['marca']}_geom.json", "w"))
    subprocess.run([sys.executable, "/home/claude/letsara/pranchas/iso3d_pilar_gen.py", f"/home/claude/letsara/pranchas/{P['marca']}_geom.json",
                    "/home/claude/letsara/pranchas/"], check=True, capture_output=True)
    # armadura
    xy = P["xy"]
    EST = P["est"]
    z_est = sorted(set(list(range(50, EST["zona"] + L_CAL, EST["s_dens"])) + list(range(EST["zona"] + L_CAL, L_TOT - EST["zona"], EST["s_corr"])) +
                       list(range(L_TOT - EST["zona"], L_TOT - 40, EST["s_dens"]))))
    if REC:                                                              # corpo até o recuo; cabeça com estribos próprios (N14 c/10)
        z_est = [z for z in z_est if z <= z_rec + 40]
        z_cab = list(range(z_rec + 100, L_TOT - 40, 100))
        u0, u1 = -B / 2 + rd("D"), B / 2 - rd("B")
        w0, w1 = -H / 2 + rd("C"), H / 2 - rd("A")
        dentro = lambda u, w: u0 + 40 <= u <= u1 - 40 and w0 + 40 <= w <= w1 - 40
        sw = P.get("sobe_w")
        xy_sobe = [p_ for p_ in xy if dentro(*p_) and (sw is None or p_[1] <= sw)]
        xy_para = [p_ for p_ in xy if p_ not in xy_sobe]
        cantos = [(u, w) for u in (u0 + COB + 18, u1 - COB - 18) for w in (w0 + COB + 18, w1 - COB - 18)]
        n_in = P.get("n13_inner", 0)
        if n_in:
            cantos += [(u0 + COB + 18 + k * (u1 - u0 - 2 * (COB + 18)) / (n_in - 1), w1 - COB - 16) for k in range(n_in)]
        xy_cab = []
        for c_ in cantos:
            if all(math.hypot(c_[0] - a, c_[1] - b) > 40 for a, b in xy_sobe + xy_cab):
                xy_cab.append((round(c_[0]), round(c_[1])))
    else:
        z_cab, xy_sobe, xy_para, xy_cab = [], xy, [], []
    n_est = len(z_est)
    pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                            conteudo=P["conteudo"], desenho=P["desenho"], folha="01/01", fase="PARA APROVAÇÃO",
                            marca=P["marca"], qtd=P["qtd"], peso=f(PESO, 1), volume=f(V, 2)))
    pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL")
    pr.revisao("04", "16/10/2026", "NBR 9062: SEM CP-VT; CONSOLOS COM ALÇAS; NEOPRENES REVISTOS; CP-MEZ P/ DENTE DA VM; CP-VB 15×27×29 P/ DENTE DA VB; PL 14 Ø20")
    r06 = ["CE-1 DOS CONSOLES CS-1 DAS PLACAS (TREJOR) NO LUGAR DOS TRILHOS TR-1"]
    if P["marca"] in ("PL-07", "PL-08"):
        r06.insert(0, "ESPERAS ES-1F DO APOIO ST-1F DA ÚLTIMA TERÇA")
    if P["marca"].startswith("PG"):
        r06.insert(0, "CABEÇA A 2 cm DA TS-01; INSERTOS IL-1 (LIGAÇÃO EM y COM A TS-01)")
    if any(ip["face"] == "C" for ip in P.get("ip01", [])):
        r06.append("CE-1 12,5; CC-1 (CS-1 DE FÁBRICA) NA FACE C; FACE C PARA CIMA NA FÔRMA (DEC-031)")
    elif P.get("ip01"):
        r06.append("CE-1 12,5")
    pr.revisao("06", "19/10/2026", "; ".join(r06))
    pr.revisao("07", "21/10/2026", "FÔRMA E ARMAÇÃO NA MESMA FOLHA (PADRÃO USINA)")
    Q = pr.quadro
    XC = Q[2] - 190
    Y0 = 92
    ESC = 20
    pr.ret(Q[0] + 4, Q[3] - 30, Q[0] + 560, Q[3] - 4, "CARIMBO")
    import renomear as RN
    from prancha_nd import _wtext as _wt, ALTURAS as _AL
    nm_ = RN.renomear(P["marca"])                                        # rev08: nomes das peças que esta folha detalha (P1…P33)
    pr.texto(Q[0] + 10, Q[3] - 24, RN.novo(nm_), "grande", "TITULO")
    qtxt = f"{P['qtd']} {'PEÇA' if P['qtd'] == 1 else 'PEÇAS IGUAIS'}"
    pr.texto(Q[0] + 10 + _wt(nm_, _AL["grande"]) + 8, Q[3] - 24, RN.novo(f"{'PILAR' if P['qtd'] == 1 else 'PILARES'} PRÉ-MOLDADOS  {P.get('secao_txt', f'{H/10:g} × {B/10:g} cm (x × y)')}   ·   L = {L_TOT/10:g} cm (cálice {L_CAL/10:g} + {Z_TOP/10:g})   ·   C40   ·   {qtxt}".replace("PILAR PRÉ-MOLDADOS", "PILAR PRÉ-MOLDADO")), "titulo", "TITULO")
    pr.texto(Q[0] + 10, Q[3] - 14, P["posicao"] + f"   ·   PESO {f(PESO/10, 2)} t   ·   VOLUME {f(V, 2)} m³   ·   {P.get('faces_txt', 'FACES: A = x+, B = y+, C = x−, D = y−')}   ·   desenhado em pé, como montado", "nota", "TEXTO")

    # ------------------------------------------------------------ vistas das faces (em pé)
    def largura(face):
        return B if face in "AC" else H
    def nivel(v, x, z, txt, lado=1):
        """rev06e: nível no padrão da usina — triângulo cheio com a ponta na linha, valor sublinhado, preto."""
        e_ = v.esc
        xa = x + lado * 1.0 * e_
        v.hachura([(xa, z), (xa + lado * 1.2 * e_, z + 2.0 * e_), (xa - lado * 1.2 * e_, z + 2.0 * e_)], "SOLID", camada="TEXTO")
        v.linha((x, z), (x + lado * 14 * e_, z), "TEXTO")
        val = txt.split(" ")[0]
        v.texto((x + lado * 3.5 * e_, z + 0.6 * e_), val, "min", "BOTTOM_LEFT" if lado > 0 else "BOTTOM_RIGHT")

    def vista_face(face, x_papel):
        W = largura(face)
        eixo, sg = VISTA[face]
        v = pr.vista(f"FACE {face}", (x_papel, Y0), ESC, titulo=f"FACE {face}" + (" (CONSOLOS)" if any(c["face"] == face for c in cons) else ""), subtitulo="pilar em pé", unidade="cm")
        dr, dl = rd(DIR[face]), rd(ESQ[face])
        v.poli([(0, 0), (W, 0), (W, z_rec), (W - dr, z_rec), (W - dr, L_TOT), (dl, L_TOT), (dl, z_rec), (0, z_rec)], "VISTA", True)
        if REC and rd(face):
            v.linha((dl, z_rec), (W - dr, z_rec), "VISTA")
        AS = P.get("assento")                                                                # rev03: TS-01 apoiada no recuo (neoprene + pinos)
        if AS and REC:
            nx_, ny_ = AS["neo"][0], AS["neo"][1]
            if rd(face) and face == "A":                                                     # frontal: assento visto de frente
                v.chapa(W / 2 - ny_ / 2, z_rec, ny_, 10)
                for dy in AS["y_pinos"]:
                    v.ret(W / 2 + dy - AS["d"] / 2, z_rec - AS["emb"], AS["d"], AS["emb"], "OCULTA")
                    v.chapa(W / 2 + dy - AS["d"] / 2, z_rec + 10, AS["d"], AS["L"] - AS["emb"])
                t_as = (f"apoio da viga:", f"{len(AS['y_pinos'])} {AS['pino']}", f"sai {(AS['L'] - AS['emb']) / 10:g} + {AS['neo_nome'].split()[0]}")
                z_C = z_rec + 0.62 * (L_TOT - z_rec)                                         # rev08: rótulo dentro da cabeça, abaixo do corte C-C
                z_p = z_rec + 10 + AS["L"] - AS["emb"]
                if z_p + 9.6 * ESC < z_C - 1.0 * ESC:                                          # logo acima dos pinos
                    v.texto((W / 2, z_p + 7.0 * ESC), t_as[0], "min", "BOTTOM_CENTER")
                    v.texto((W / 2, z_p + 4.4 * ESC), t_as[1], "min", "BOTTOM_CENTER")
                    v.texto((W / 2, z_p + 1.8 * ESC), t_as[2], "min", "BOTTOM_CENTER")
                else:
                    v.chamada((W / 2 + AS["y_pinos"][-1], z_rec + 150), ((W / 2 - AS["y_pinos"][-1] + ext_face(face)[1]) / ESC + 11.5, (L_TOT - z_rec - 150) / ESC + 16), " ".join(t_as))
            elif dr or dl:                                                                   # lateral: degrau do recuo
                xa = (W - dr) if dr else dl
                sgn = 1 if dr else -1
                x_n0, x_n1 = sorted((xa + sgn * AS["x_neo"][0], xa + sgn * AS["x_neo"][1]))
                v.chapa(x_n0, z_rec, x_n1 - x_n0, 10)
                xp_ = xa + sgn * AS["x_pino"]
                v.ret(xp_ - AS["d"] / 2, z_rec - AS["emb"], AS["d"], AS["emb"], "OCULTA")
                v.chapa(xp_ - AS["d"] / 2, z_rec + 10, AS["d"], AS["L"] - AS["emb"])
        PT = P.get("pinos_topo")                                                             # DEC-040: pinos PN-5 no topo (TS-01 apoiada no topo)
        if PT:
            us = sorted({(q[1] if face in "AC" else q[0]) for q in PT["xy"]})
            for u_ in us:
                v.ret(W / 2 + u_ - PT["d"] / 2, L_TOT - PT["emb"], PT["d"], PT["emb"], "OCULTA")
                v.chapa(W / 2 + u_ - PT["d"] / 2, L_TOT, PT["d"], PT["L"] - PT["emb"])
            v.texto((W / 2, L_TOT + PT["L"] - PT["emb"] + 1.2 * ESC), f"{len(PT['xy'])} {PT['nome']} Ø{PT['d']:g} sai {(PT['L'] - PT['emb']) / 10:g}", "min", "BOTTOM_CENTER")
        v.linha((0, L_CAL), (W, L_CAL), "EIXO")
        for k in range(3):                                                                   # chaves de cisalhamento (frontal)
            v.ret(50, 150 + k * 300 + 40, W - 100, 120, "OCULTA")
        EXT = {1: 0.0, -1: 0.0}                                                              # rev06e: saliências laterais (cotas por fora)
        for c in cons:
            zc, proj, h, hp, larg = c["z"], c["proj"], c["h"], c["hp"], c["larg"]
            if c["face"] == face:                                                            # frontal
                v.ret((W - larg) / 2, zc - h, larg, h, "VISTA")
                v.linha(((W - larg) / 2, zc - hp), ((W + larg) / 2, zc - hp), "VISTA")
                v.ret(W / 2 - c["pino_d"] / 2, zc - c["pino_emb"], c["pino_d"], c["pino_emb"], "OCULTA")
                v.chapa(W / 2 - c["pino_d"] / 2, zc, c["pino_d"], c["pino_L"] - c["pino_emb"])
                v.chapa(W / 2 - c["neo"][0] / 2, zc, c["neo"][0], 10)
                # rev08: rótulo em 2 linhas dentro da face, logo abaixo do consolo (a chamada para fora cruzava as cadeias de cota)
                v.texto((W / 2, zc - h - 1.8 * ESC), c["tipo"], "nota", "TOP_CENTER")
                v.texto((W / 2, zc - h - 4.8 * ESC), f"{larg/10:g}×{proj/10:g}×{h/10:g}" + (f"/{hp/10:g}" if hp != h else ""), "nota", "TOP_CENTER")
                v.texto((W / 2, zc - h - 7.6 * ESC), f"pino {c['pino_nome']} Ø{c['pino_d']:g}", "min", "TOP_CENTER")   # DEC-040: pino do apoio (saliência no DET. 1)
            elif c["face"] == OPOSTA[face]:
                v.ret((W - larg) / 2, zc - h, larg, h, "OCULTA")
            else:                                                                            # lateral: projeção para fora
                lado = 1 if (VISTA[face][0] == "y" and c["face"] == "B") or (VISTA[face][0] == "x" and c["face"] == "A") else -1
                lado *= sg if VISTA[face][0] == "y" else 1
                # regra: à direita da vista fica a face cuja coordenada cresce no sentido de `sg`
                lado = 1 if ((c["face"] == "B" and eixo == "y" and sg > 0) or (c["face"] == "D" and eixo == "y" and sg < 0) or
                             (c["face"] == "A" and eixo == "x" and sg > 0) or (c["face"] == "C" and eixo == "x" and sg < 0)) else -1
                x0 = W if lado > 0 else 0
                EXT[lado] = max(EXT[lado], proj)
                v.poli([(x0, zc - h), (x0 + lado * proj, zc - hp), (x0 + lado * proj, zc + proj * c.get("incl", 0.03)), (x0, zc)], "VISTA")
                v.ret(x0 + lado * c["pino_x"] - c["pino_d"] / 2, zc - c["pino_emb"], c["pino_d"], c["pino_emb"], "OCULTA")
                v.chapa(x0 + lado * c["pino_x"] - c["pino_d"] / 2, zc, c["pino_d"], c["pino_L"] - c["pino_emb"])
                v.chapa(x0 + (25 if lado > 0 else -25 - c["neo"][1]), zc, c["neo"][1], 10)
        for ip in P.get("ip01", []):                                                       # rev06: CE-1 = chapa de espera 380 × 330 na face
            F_ = ip["face"]                                                                # das placas, centrada (consoles CS-1 soldados)
            cc = F_ == "C" and ip.get("lados")                                               # rev06e (DEC-031): CC-1 = CE-1 + CS-1 de fábrica
            if F_ == face:
                for k_, z in enumerate(ip["z"]):
                    v.chapa((W - 380) / 2, z - 165, 380, 330)
                    if cc:
                        for ld in ip["lados"][k_]:                                           # vista de fora: E à esquerda, D à direita
                            xc = W / 2 + (-XC_CS if ld == "E" else XC_CS)
                            v.ret(xc - CS["costas"]["b"] / 2, z + ZT_CS + CS["costas"]["z0"], CS["costas"]["b"], CS["costas"]["z1"] - CS["costas"]["z0"], "METALICA")
                            v.ret(xc - CS["mesa"]["b"] / 2, z + ZT_CS - CS["mesa"]["t"], CS["mesa"]["b"], CS["mesa"]["t"], "METALICA")
                        tp = {"DE": "CC-1", "E": "CC-1E", "D": "CC-1D"}[ip["lados"][k_]]
                        v.texto((W / 2, z - 175), tp, "min", "TOP_CENTER")
            elif F_ != OPOSTA[face]:
                lado = 1 if ((F_ == "B" and eixo == "y" and sg > 0) or (F_ == "D" and eixo == "y" and sg < 0) or
                             (F_ == "A" and eixo == "x" and sg > 0) or (F_ == "C" and eixo == "x" and sg < 0)) else -1
                xt = (W - 12.5) if lado > 0 else 0
                for z in ip["z"]:
                    v.chapa(xt, z - 165, 12.5, 330)
                    v.ret(W - 162.5 if lado > 0 else 12.5, z - 148, 150, 16, "OCULTA"); v.ret(W - 162.5 if lado > 0 else 12.5, z + 132, 150, 16, "OCULTA")
                    if cc:                                                                   # perfil do CS-1 saindo 64 mm da face C
                        x0 = W if lado > 0 else 0
                        EXT[lado] = max(EXT[lado], CS["mesa"]["y1"])
                        X = lambda y_: x0 + lado * y_
                        co, me, de = CS["costas"], CS["mesa"], CS["dente"]
                        zt = z + ZT_CS
                        v.chapa(min(X(0), X(co["t"])), zt + co["z0"], co["t"], co["z1"] - co["z0"])
                        v.poli([(X(y_), zt + z_) for y_, z_ in GF.alma_poli()], "METALICA", fechada=True)
                        v.chapa(min(X(me["y0"]), X(me["y1"])), zt - me["t"], me["y1"] - me["y0"], me["t"])
                        v.ret(min(X(de["y0"]), X(de["y0"] + de["t"])), zt, de["t"], de["h"], "METALICA")
        if face in FI["eixo"]:                                                              # rev07: furo de içamento FI-1 (de frente)
            v.circulo((W / 2, FI["z"]), FI["d"] / 2, "METALICA"); v.circulo((W / 2, FI["z"]), FI["d"] / 2 - 3, "METALICA")
            z_fi = FI["z"] - FI["d"] / 2 - 30
            if face == P.get("al_face", "A"):                                                  # rev08: rótulo abaixo da alça AL-2 se ela cruzar o texto
                for z_al in AL:
                    if z_fi - 2.6 * ESC - 15 < z_al < z_fi + 15:
                        z_fi = z_al - 7 - 30
            for c in cons:                                                                   # rev08: nem sobre o pino de consolo frontal
                if c["face"] == face and c["z"] - 20 < z_fi and z_fi - 2.6 * ESC < c["z"] + c["pino_L"] - c["pino_emb"] + 20:
                    z_fi = FI["z"] + FI["d"] / 2 + 30 + 2.0 * ESC
            v.texto((W / 2, z_fi), "FI-1 Ø60", alinh="TOP_CENTER")       # rótulo dentro da face, sob o furo (as chamadas dos consolos ficam fora)
        else:                                                                                # atravessando (oculto)
            v.ret(0, FI["z"] - FI["d"] / 2, W, FI["d"], "OCULTA")
        if face == P.get("al_face", "A"):                                                  # rev06e: AL-2 na face de cima da fôrma
            for z in AL:
                v.linha((W / 2 - 50, z), (W / 2 + 50, z), "METALICA"); v.circulo((W / 2 - 50, z), 6.35, "METALICA"); v.circulo((W / 2 + 50, z), 6.35, "METALICA")
        cf = [c for c in cons if c["face"] == face]
        zs = sorted(set([0, L_CAL] + [c["z"] for c in cf] + [c["z"] - c["h"] for c in cf] + ([z_rec] if REC else []) + [L_TOT]))
        v.cota_v(zs, -EXT[-1], -9)
        v.zs_cota = list(zs)
        ords = sorted(set([0, L_CAL] + [c["z"] for c in cons if c["face"] == face] + [z + (ZT_CS if (ip["face"] == "C" and ip.get("lados")) else 0) for ip in P.get("ip01", []) if ip["face"] == face for z in ip["z"]] + [L_TOT]))
        v.zs_ords = list(ords) if len(ords) > 3 else []
        if len(ords) > 3:
            v.cota_v(ords, W + EXT[1], 9)                                                    # rev06e: cadeia + total (usina), sem acumuladas
        v.cota_h([0, W], 0, -8)
        if REC and (dl or dr):
            v.cota_h(sorted(set([0, dl, W - dr, W])), L_TOT, 8, total=False)
        v.ext = EXT
        return v

    def ext_face(face):                                                   # rev07: saliências laterais de cada vista (para o espaçamento)
        eixo, sg = VISTA[face]
        e_ = {1: 0.0, -1: 0.0}
        def lado_de(F_):
            return 1 if ((F_ == "B" and eixo == "y" and sg > 0) or (F_ == "D" and eixo == "y" and sg < 0) or
                         (F_ == "A" and eixo == "x" and sg > 0) or (F_ == "C" and eixo == "x" and sg < 0)) else -1
        for c in cons:
            if c["face"] not in (face, OPOSTA[face]):
                e_[lado_de(c["face"])] = max(e_[lado_de(c["face"])], c["proj"])
        for ip in P.get("ip01", []):
            if ip["face"] == "C" and ip.get("lados") and ip["face"] not in (face, OPOSTA[face]):
                e_[lado_de("C")] = max(e_[lado_de("C")], CS["mesa"]["y1"])
        return e_
    xs_faces = {}
    QX_ARM = XC - 4 - 485                                                 # rev07: armação (padrão usina) à direita da fôrma
    XD = QX_ARM - 10 - 186                                                # coluna dos detalhes da fôrma
    exts = [ext_face(fc) for fc in P["vistas"]]
    occ = [(e_[-1] + largura(fc) + e_[1]) / ESC for fc, e_ in zip(P["vistas"], exts)]
    folga = (XD - 6 - (Q[0] + 30) - sum(occ)) / len(occ)                  # sobra repartida entre as faces (cotas dos dois lados)
    EXTRA_M = 8.0                                                         # rev08: letras dos cortes A/C à direita da 1ª face (fora das cotas)
    folga = (XD - 6 - (Q[0] + 30) - sum(occ) - EXTRA_M) / len(occ)
    folga = max(folga, 26)
    # rev08: os títulos das faces ("FACE C (CONSOLOS)") não podem encostar: distância mínima entre centros pelas larguras dos títulos
    tw = [_wtext(("FACE " + fc + (" (CONSOLOS)" if any(c["face"] == fc for c in cons) else "")).upper(), ALTURAS["titulo"]) + 5 for fc in P["vistas"]]
    xs0, xp = [], Q[0] + 30
    for k_f, (face, e_) in enumerate(zip(P["vistas"], exts)):
        xp += e_[-1] / ESC + folga * 0.62
        xs0.append(xp)
        xp += (largura(face) + e_[1]) / ESC + folga * 0.38 + (EXTRA_M if k_f == 0 else 0)
    cen = lambda k: xs0[k] + (largura(P["vistas"][k]) / 2) / ESC
    for k in range(1, len(xs0)):
        falta = (tw[k - 1] + tw[k]) / 2 - (cen(k) - cen(k - 1))
        if falta > 0:
            for j in range(k, len(xs0)):
                xs0[j] += falta
    for face, x_ in zip(P["vistas"], xs0):
        xs_faces[face] = vista_face(face, x_)
    xp = xs0[-1] + (largura(P["vistas"][-1]) + exts[-1][1]) / ESC
    vA = xs_faces[P["vistas"][0]]
    XN = -vA.ext[-1] - 12.5 * ESC                                                                     # rev06e: níveis por fora das cadeias de cota
    nivel(vA, XN, L_CAL, "±0,00", -1)
    nivel(vA, XN, L_TOT, f"+{f(Z_TOP/1000, 2)}", -1)
    for c in cons:
        if c["face"] == P["vistas"][0]:
            nivel(vA, XN, c["z"], f"+{f((c['z'] - L_CAL)/1000, 2)}", -1)
    XM0, XM1 = -vA.ext[-1] - 10.5 * ESC, largura(P["vistas"][0]) + vA.ext[1] + 10.5 * ESC      # rev08: letras por fora das cadeias de cota
    meios = [(a + b) / 2 for zz in (vA.zs_cota, vA.zs_ords) for a, b in zip(zz[:-1], zz[1:])] + \
            [(zz[0] + zz[-1]) / 2 for zz in (vA.zs_cota, vA.zs_ords) if len(zz) > 2]           # textos das cotas totais
    proib = [(c["z"] - c["h"] - 7 * ESC, c["z"] + 3 * ESC) for c in cons]
    cand = sorted(range(2500, int((z_rec if REC else L_TOT) - 800), 25), key=lambda z_: abs(z_ - 4300))
    livre = lambda z_: all((m - z_) > 10.5 * ESC or (z_ - m) > 4 * ESC for m in meios)      # seta/letra sobem ~10 mm acima da linha
    Z_A = next((z_ for z_ in cand if livre(z_) and all(not (a < z_ < b) for a, b in proib)), 4300)
    vA.marcador_corte((XM0, Z_A), (XM1, Z_A), "A", lado=1)
    if REC:
        vA.marcador_corte((XM0, z_rec + 0.62 * (L_TOT - z_rec)), (XM1, z_rec + 0.62 * (L_TOT - z_rec)), "C", lado=1)
        nivel(vA, XN, z_rec, f"+{f((z_rec - L_CAL)/1000, 2)}", -1)
    # rev08: afasta as faces cujas caixas (desenho + cotas + letras dos cortes + título) encostam na anterior (≥ 4 mm)
    from prancha_nd import _wtext as _wt
    def _caixa(v_):
        b_ = v_.bbox_papel()
        cx_ = (b_[0] + b_[2]) / 2
        w1_ = _wt(v_.titulo.upper(), ALTURAS["titulo"]) / 2
        w2_ = _wt(f"ESC. 1:{v_.esc:g} — COTAS EM {v_.unidade.upper()}" + (f" — {v_.subtitulo}" if v_.subtitulo else ""), ALTURAS["nota"]) / 2
        return min(b_[0], cx_ - w1_, cx_ - w2_), max(b_[2], cx_ + w1_, cx_ + w2_)
    vs_ = [xs_faces[fc] for fc in P["vistas"]]
    for k in range(1, len(vs_)):
        d_ = 4.0 - (_caixa(vs_[k])[0] - _caixa(vs_[k - 1])[1])
        if d_ > 0:
            for v_ in vs_[k:]:
                for e_ in v_.ents:
                    e_.translate(d_, 0, 0)
                v_.o = (v_.o[0] + d_, v_.o[1])
    sobra_ = _caixa(vs_[-1])[1] - (XD - 4)
    if sobra_ > 0:                                                        # rev08: usa a folga da margem esquerda
        d_ = -min(sobra_, max(0.0, _caixa(vs_[0])[0] - (Q[0] + 6)))
        for v_ in vs_:
            for e_ in v_.ents:
                e_.translate(d_, 0, 0)
            v_.o = (v_.o[0] + d_, v_.o[1])
    if _caixa(vs_[-1])[1] > XD - 4:
        print(f"  ! {P['marca']}: faces avançam na coluna da fôrma ({_caixa(vs_[-1])[1]:.0f} > {XD - 4:.0f})")

    # ------------------------------------------------------------ rev07: coluna de detalhes da fôrma (à direita das faces)
    YT = Q[3] - 38
    if xp > XD:
        print(f"  ! {P['marca']}: faces passam da coluna da fôrma ({xp:.0f} > {XD:.0f})")
    # planta-chave 1:750
    kp = pr.vista("PLANTA-CHAVE", (XD + 62, YT - 120), 750, titulo="PLANTA-CHAVE", subtitulo=f"{P['marca']} hachurado", unidade="cm")
    Xm = lambda m: m * 1000
    for y in Y_LIN:
        kp.linha((Xm(-2.5 + 1.1), Xm(y)), (Xm(42.0), Xm(y)), "EIXO")                    # rev06e: eixo para na bolha
    for x in X_FACH:
        kp.linha((Xm(x), Xm(-2.5)), (Xm(x), Xm(85.5 - 1.1)), "EIXO")
    for i, y in enumerate(Y_LIN, 1):
        kp.circulo((Xm(-2.5), Xm(y)), 1100, "VISTA"); kp.texto((Xm(-2.5), Xm(y)), str(i), "nota", "MIDDLE_CENTER")
    for j, x in enumerate(X_FACH):
        kp.circulo((Xm(x), Xm(85.5)), 1100, "VISTA"); kp.texto((Xm(x), Xm(85.5)), "ABCDE"[j], "nota", "MIDDLE_CENTER")
    rot_kp = {}
    for nome, x, y, bx, by, mk in P["kp"]:
        pts = [(Xm(x) - bx / 2, Xm(y) - by / 2), (Xm(x) + bx / 2, Xm(y) - by / 2), (Xm(x) + bx / 2, Xm(y) + by / 2), (Xm(x) - bx / 2, Xm(y) + by / 2)]
        kp.poli(pts, "CORTADO", fechada=True)
        if mk == P["marca"]:
            kp.hachura(pts, "ANSI31", 0.3)
            rot_kp.setdefault(round(y, 2), []).append(nome)
    for y, nomes in rot_kp.items():                                                     # rev08: fora da malha (não cruza eixo), um rótulo por linha
        kp.texto((Xm(42.0) + 600, Xm(y)), f"{' / '.join(nomes)} {P['marca']}", "min", "MIDDLE_LEFT")

    # ------------------------------------------------------------ CORTE A-A (1:10)
    YS = YT - 178 - H / 20
    v = pr.vista("CORTE A-A", (XD + 32, YS), 10, titulo="CORTE A-A", subtitulo="corrente (fôrma)", unidade="cm")
    pts = [(-B / 2, -H / 2), (B / 2, -H / 2), (B / 2, H / 2), (-B / 2, H / 2)]
    v.poli(pts, "CORTADO", fechada=True); v.hachura(pts, "AR-CONC", 0.03)
    v.cota_h([-B / 2, B / 2], -H / 2, -8); v.cota_v([-H / 2, H / 2], B / 2, 8)
    v.texto((0, H / 2 + 30), "FACE A", "min", "BOTTOM_CENTER"); v.texto((0, -H / 2 - 130), "FACE C", "min", "TOP_CENTER")
    v.texto((B / 2 + 110, 0), "FACE B", "min", "MIDDLE_LEFT", rot=90); v.texto((-B / 2 - 30, 0), "FACE D", "min", "MIDDLE_RIGHT", rot=90)

    if REC:
        vc = pr.vista("CORTE C-C", (XD + 32 + max(B / 10 + 52, 92), YS), 10, titulo="CORTE C-C", subtitulo="cabeça recuada (fôrma)", unidade="cm")
        u0, u1 = -B / 2 + rd("D"), B / 2 - rd("B")
        w0, w1 = -H / 2 + rd("C"), H / 2 - rd("A")
        vc.poli([(-B / 2, -H / 2), (B / 2, -H / 2), (B / 2, H / 2), (-B / 2, H / 2)], "OCULTA", fechada=True)
        pc = [(u0, w0), (u1, w0), (u1, w1), (u0, w1)]
        vc.poli(pc, "CORTADO", fechada=True); vc.hachura(pc, "AR-CONC", 0.03)
        vc.cota_h([u0, u1], w0, -8); vc.cota_v([w0, w1], u1, 8)

    # ------------------------------------------------------------ DETALHE 1 — consolo (1:10) e DETALHE 2 — base (1:20)
    YM = YS - H / 20 - 38                                               # rev08: CORTE A-A não encosta no DETALHE 1
    if cons:
        c0 = max(cons, key=lambda c: c["h"])
        d1 = pr.vista("DETALHE 1", (XD + 92, YM - 150), 10, titulo=f"DETALHE 1 — CONSOLO {c0['tipo']}",
                      subtitulo="fôrma, pino e neoprene" + (f"; topo com caimento {c0.get('incl', 0.03) * 100:g} %" if c0.get("incl", 0.03) else "") + " (armação: DET. C1)", unidade="cm")
        PW = largura(OPOSTA[c0["face"]]) if c0["face"] in "BD" else H
        PW = H if c0["face"] in "AC" else B
        zc0, Z1, Z2 = 1000, 400, 1450
        proj, h, hp = c0["proj"], c0["h"], c0["hp"]
        d1.poli([(-PW, Z1), (-PW, Z2), (0, Z2), (0, Z1)], "VISTA"); d1.interrupcao((-PW, Z1), (0, Z1)); d1.interrupcao((-PW, Z2), (0, Z2))
        d1.poli([(0, zc0 - h), (proj, zc0 - hp), (proj, zc0 + proj * c0.get("incl", 0.03)), (0, zc0)], "VISTA")
        d1.ret(c0["pino_x"] - c0["pino_d"] / 2, zc0 - c0["pino_emb"] + 5, c0["pino_d"], c0["pino_emb"], "OCULTA")
        d1.chapa(c0["pino_x"] - c0["pino_d"] / 2, zc0 + 5, c0["pino_d"], c0["pino_L"] - c0["pino_emb"])
        d1.chapa(25, zc0 + 1, c0["neo"][1], 10)
        d1.cota_v(sorted(set([zc0 - h, zc0 - hp, zc0])), proj, 10, total=False)          # rev08: caimento no subtítulo (cota de 1,2 cruzava as linhas)
        d1.cota_h([0, c0["pino_x"], proj], zc0 - h, -8, total=False); d1.cota_h([-PW, 0], Z1, -10)
        d1.chamada((c0["pino_x"], zc0 + 350), (10, 10), f"{c0['pino_nome']} Ø{c0['pino_d']} {'roscado A36' if c0['pino_nome'] == 'PN-6' else 'CA-50'} L={c0['pino_L']/10:g}")
        d1.chamada((150, zc0 + 6), (16, 20), f"neoprene {c0['neo'][0]}×{c0['neo'][1]}×{c0['neo'][2]} mm")

    YD2 = (YM - 150 + 400 / 10 - 26) if cons else YM
    d2 = pr.vista("DETALHE 2", (XD + 60, YD2 - 82), 20, titulo="DETALHE 2 — BASE NO CÁLICE", subtitulo="embutimento 100 cm; chaves", unidade="cm")
    d2.poli([(-H / 2, 0), (H / 2, 0), (H / 2, 1600), (-H / 2, 1600)], "VISTA")
    for k in range(3):
        z0 = 150 + k * 300
        for sg in (-1, 1):
            d2.poli([(sg * H / 2, z0), (sg * (H / 2 + 30), z0 + 40), (sg * (H / 2 + 30), z0 + 160), (sg * H / 2, z0 + 200)], "VISTA")
    d2.linha((-H / 2 - 400, L_CAL), (H / 2 + 400, L_CAL), "EIXO")
    d2.poli([(-H / 2 - 150, L_CAL), (-H / 2 - 150, -500), (H / 2 + 150, -500), (H / 2 + 150, L_CAL)], "OCULTA")
    d2.cota_v([0, L_CAL, 1500], H / 2 + 150, 10, total=False); d2.cota_h([-H / 2, H / 2], 0, -8)
    d2.chamada((H / 2 + 30, 250), (14, 4), "chaves 4×20 (4 faces)"); d2.chamada((H / 2, 1350), (12, 8), "graute ≥ 30 MPa")
    d2.chamada((H / 2 + 150, -300), (8, -8), "cálice (fundações)")
    if any(ip["face"] == "C" for ip in P.get("ip01", [])):
        posicao_forma(pr, P, cons, XD + 78, YD2 - 82 - 25 - 24 - H / 10 - 18); d2.chamada((H / 2, L_CAL), (16, -6), "piso ±0,000; graute")


    # ------------------------------------------------------------ tabelas
    y = Q[3] - 6
    y = tabela_q(pr, XC, y, f"MARCAS — {P['familia']}", ["MARCA", "POSIÇÃO", "QT", "CONSOLOS (face)", "INSERTOS"], P["marcas"], [16, 22, 8, 86, 50], h_lin=6.0)
    L_N1 = round((L_TOT - 80) / 10)
    EXT_B, EXT_H = B - 2 * COB, H - 2 * COB
    L_N1A = round((z_rec - 30 - 40) / 10 + 15)
    barras = ([dict(pos="N1", diam=D1, qtd=len(xy_sobe), comp=L_N1, trechos=[f"{L_N1}"], geo=dict(k="R", a=L_N1))] if xy_sobe else []) + \
             ([dict(pos="N1A", diam=D1, qtd=len(xy_para), comp=L_N1A, forma=[(0, 0), (85, 0), (85, 8)], trechos=[f"{L_N1A - 15}", "15"], geo=dict(k="L", a=L_N1A - 15, g=15))] if xy_para else []) + \
             ([dict(pos="N13", diam=16.0, qtd=len(xy_cab), comp=round((L_TOT - 40 - (z_rec - 600)) / 10), trechos=[f"{round((L_TOT - 40 - (z_rec - 600)) / 10)}"], geo=dict(k="R", a=round((L_TOT - 40 - (z_rec - 600)) / 10)))] if xy_cab else []) + \
             ([dict(pos="N14", diam=P.get("d_est", 8.0), qtd=len(z_cab), comp=round((2 * (HB - 60 + HH - 60) + 160) / 10), forma=[(0, 0), ((HB - 60) / 10, 0), ((HB - 60) / 10, (HH - 60) / 10), (0, (HH - 60) / 10), (0, 0), (2, 2)], trechos=[f"{(HB-60)/10:g}", f"{(HH-60)/10:g}", "", ""], geo=dict(k="E", a=(HH - 60) / 10, b=(HB - 60) / 10))] if z_cab else []) + [
              dict(pos="N2", diam=P.get("d_est", 8.0), qtd=n_est, comp=round((2 * (EXT_B + EXT_H) + 160) / 10), forma=[(0, 0), (EXT_B / 10, 0), (EXT_B / 10, EXT_H / 10), (0, EXT_H / 10), (0, 0), (2, 2)], trechos=[f"{EXT_B/10:g}", f"{EXT_H/10:g}", "", ""], geo=dict(k="E", a=EXT_H / 10, b=EXT_B / 10))]
    if P["grampos"]:
        barras.append(dict(pos="N3", diam=P.get("d_est", 8.0), qtd=len(P["grampos"]) * n_est, comp=round((EXT_B + 160) / 10), forma=[(0, 6), (0, 0), (EXT_B / 10, 0), (EXT_B / 10, 6)], trechos=["8", f"{EXT_B/10:g}", "8"], geo=dict(k="G", a=EXT_B / 10, g=8)))
    if P.get("grampos_h"):                                                                 # DEC-040: grampos na direção A–C
        barras.append(dict(pos="N3A", diam=P.get("d_est", 8.0), qtd=len(P["grampos_h"]) * n_est, comp=round((EXT_H + 160) / 10), forma=[(0, 6), (0, 0), (EXT_H / 10, 0), (EXT_H / 10, 6)], trechos=["8", f"{EXT_H/10:g}", "8"], geo=dict(k="G", a=EXT_H / 10, g=8)))
    n_ce = sum(len(i["z"]) for i in P.get("ip01", []))
    if n_ce:                                                                               # rev06b: N18 = 2 grampos U Ø10 por CE-1 (ND-LET-PP01 det. 5)
        barras.append(dict(pos="N18", diam=10.0, qtd=2 * n_ce, comp=96, forma=[(0, 45), (0, 0), (6, 0), (6, 45)], trechos=["45", "6", "45"], geo=dict(k="U", a=45, b=6, g=0)))
        pr.posicoes_desenho.add("N18")
    grupos, arm_cons = {}, []
    for c in cons:
        PWc = (H if c["face"] in "AC" else B)
        grupos.setdefault((c["n_tir"], c["d_tir"], c["proj"], PWc, c["larg"], c["h"]), []).append(c)
    nomes_pos = [("N4", "N5", "N6"), ("N7", "N8", "N9"), ("N10", "N11", "N12"), ("N15", "N16", "N17")]
    for k, ((nt, dt, proj, PWc, lg, hc), cs) in enumerate(grupos.items()):
        pa, pb, pc = nomes_pos[k]
        n_cons = len(cs)
        tipos = "/".join(sorted(set(c["tipo"] for c in cs)))
        lgu, wu, hu = round((PWc + proj - 80) / 10), round((lg - 60) / 10), round((hc - 60) / 10)       # perna do U, largura útil e altura útil (cm)
        barras += [dict(pos=pa, diam=dt, qtd=nt * n_cons, comp=2 * lgu + wu + 30, forma=[(0, 15), (0, 0), (85, 0), (85, 34), (0, 34), (0, 49)], trechos=["15", f"{lgu}", f"{wu}", "", "15"],
                        geo=dict(k="U", a=lgu, b=wu, g=15)),
                   dict(pos=pb, diam=10.0, qtd=2 * n_cons, comp=2 * (lgu + wu) + 16, forma=[(0, 0), (70, 0), (70, 34), (0, 34), (0, 0), (2, 2)], trechos=[f"{lgu}", f"{wu}", "", ""],
                        geo=dict(k="E", a=lgu, b=wu)),
                   dict(pos=pc, diam=8.0, qtd=len(range(60, proj - 40, 80)) * n_cons, comp=2 * (wu + hu) + 16, forma=[(0, 0), (34, 0), (34, 40), (0, 40), (0, 0), (2, 2)], trechos=[f"{wu}", f"{hu}", "", ""],
                        geo=dict(k="E", a=wu, b=hu))]
        arm_cons.append(dict(pos=(pa, pb, pc), tipos=tipos, n=n_cons, nt=nt, dt=dt, proj=proj, PW=PWc, larg=lg, h=hc, n6=len(range(60, proj - 40, 80)),
                             faces=[(c["face"], c["z"], c["tipo"]) for c in cs], incl=cs[0].get("incl", 0.03)))
        pr.posicoes_desenho.update({pa, pb, pc})
    area_f = (2 * (B + H) * z_rec + 2 * (HB + HH) * (L_TOT - z_rec) + B * H + (B * H - HB * HH) +
              sum(2 * c["proj"] * c["h"] + c["larg"] * c["h"] + c["larg"] * c["proj"] - c["larg"] * c["h"] for c in cons)) / 1e6
    json.dump(dict(marca=P["marca"], qtd=P["qtd"], desenho=P["desenho"], posicao=P["posicao"], B=B, H=H, L_TOT=L_TOT, L_CAL=L_CAL, Z_TOP=Z_TOP, COB=COB,
                   rec=REC, z_rec=z_rec, HB=HB, HH=HH, D1=D1, xy=xy, xy_sobe=xy_sobe, xy_para=xy_para, xy_cab=xy_cab, grampos=P["grampos"], grampos_h=P.get("grampos_h", []),
                   z_est=z_est, z_cab=z_cab, est=EST, d_est=P.get("d_est", 8.0), cons=[dict(face=c["face"], z=c["z"], tipo=c["tipo"], larg=c["larg"], proj=c["proj"], h=c["h"], hp=c["hp"], incl=c.get("incl", 0.03)) for c in cons],
                   arm_cons=arm_cons, barras=barras, V=V, area_forma=area_f, al=AL, n_ip=sum(len(i["z"]) for i in P.get("ip01", []))),
              open(f"/home/claude/letsara/pranchas/arm/{P['marca']}.json", "w"), ensure_ascii=False, indent=1)
    if P.get("so_arm"):
        return
    # ------------------------------------------------------------ rev07: ARMAÇÃO na mesma folha (padrão usina, à direita da fôrma)
    import armaduras_pilares as AP_
    from arm_nd import Arm
    PJ = json.load(open(f"/home/claude/letsara/pranchas/arm/{P['marca']}.json"))
    QY_ARM = Q[1] + 6
    A_ = Arm(pr)
    pr.linha((QX_ARM - 5, Q[1]), (QX_ARM - 5, Q[3] - 34), "CARIMBO_FINO")
    ra = AP_.quadrante(A_, PJ, QX_ARM, QY_ARM, ref="fôrma nesta folha (à esquerda)", esc=25, qh=Q[3] - 36 - QY_ARM)
    ta = dict(total_kg=ra["kg"])
    ins_ = list(P["insertos"]) + [["FI-1", "Furo de içamento: tubo aço Ø60,3 × 3 perdido", 1,
                                    f"faces {FI['eixo'][0]}–{FI['eixo'][1]}, {(L_TOT - FI['z']) / 10:g} cm do topo"]]
    y = tabela_q(pr, XC, y - 4, f"INSERTOS POR PILAR ({P['marca']}) — dimensões em mm", ["MARCA", "DESCRIÇÃO", "QT", "POSIÇÃO"], ins_, [13, 84, 8, 77])
    qd = [["MARCA", P["marca"], "SEÇÃO", f"{H/10:g} × {B/10:g} cm (x × y)"], ["COMPRIMENTO", f"{L_TOT/10:g} cm", "CONCRETO", "C40"],
          ["VOLUME", f"{f(V, 2)} m³", "PESO", f"{f(PESO/10, 2)} t"], ["AÇO CA-50", f"{f(ta['total_kg'], 0)} kg", "TAXA", f"{f(len(xy) * 3.1416 * (D1 / 10) ** 2 / 4 / (B * H / 100) * 100, 2)} %"],
          ["QUANTIDADE", f"{P['qtd']}", "COBRIMENTO", "3,0 cm (CAA II)"]] + ([["CABEÇA", f"{HB/10:g} × {HH/10:g} cm acima de +{f((z_rec - L_CAL)/1000, 2)}", "", ""]] if REC else [])
    y = tabela_q(pr, XC, y - 4, "QUADRO DA PEÇA", ["ITEM", "VALOR", "ITEM", "VALOR"], qd, [30, 60, 30, 62])
    y = pr.tabela(XC, y - 4, "MEMÓRIA RESUMIDA (NBR 6118:2023)", ["VERIFICAÇÃO", "RESULTADO"], P["memoria"], [70, 112])
    y = pr.legenda_armadura(XC, y - 4, False)
    ISO_ = f"/home/claude/letsara/pranchas/ISO-{P['marca']}-2v.png"
    import os as _os
    if _os.path.exists(ISO_) and ra["ymeio"] - (QY_ARM + 40) > 180:
        from PIL import Image as _Im
        wi_, hi_ = _Im.open(ISO_).size
        hh_ = min(ra["ymeio"] - 6 - (QY_ARM + 40), 470, (228 - 6) * hi_ / wi_)
        ww_ = hh_ * wi_ / hi_ + 6
        xi0 = QX_ARM + 158 + (230 - ww_) / 2
        yi0 = QY_ARM + 40 + (ra["ymeio"] - 6 - (QY_ARM + 40) - hh_) / 2
        pr.imagem(xi0, yi0, xi0 + ww_, yi0 + hh_, ISO_, titulo="ISOMÉTRICO DA PEÇA", subtitulo="duas vistas; sem escala")
    nota_fi = [] if FI["livre"] else [f"FI-1 (faces {FI['eixo'][0]}–{FI['eixo'][1]}): há {FI['obst']} acima do furo numa das faces por onde sobem as lingas. Verticalizar e montar com balancim (lingas verticais) e afastadores de madeira entre a linga e a saliência; a linga nunca pode apoiar na quina."]
    y_nt = pr.notas(XC, y - 4, P["notas"] + nota_fi + ["Desformar, bascular e transportar só com fcj ≥ 25 MPa (corpo de prova curado com a peça); cobrimento 3,0 cm (CAA II); transportar deitado em 2 apoios a 0,21 L das pontas, sem apoiar sobre consolos ou consoles metálicos. Tirar da fôrma pelas alças AL-2; verticalizar e montar pelo furo FI-1 (pino de aço passante + 2 manilhas; Ø do pino e capacidade a confirmar com a fábrica).",
                                     "Armação no padrão de entrega da usina, nesta folha: barras explodidas com a forma e o comprimento de corte, seções S.1/S.2, consolos (DETALHE C), tabela de ferros e resumo do aço +10%. Aço CA-50 (NBR 7480); dobramento NBR 6118:2023 tab. 9.1; estribos com ganchos 135° e ponta 10Ø; barras sem emenda.",
                                     "Cotas de concreto em cm, chaparia em mm, níveis em m. Não medir no desenho. PROJETO DA ND ENGENHARIA — PARA APROVAÇÃO, NÃO EXECUTAR."], 182)
    pr.posicoes_desenho.update({b["pos"] for b in barras if b["pos"] in ("N1", "N1A", "N13", "N14")})
    pr.posicoes_desenho.discard("N1") if not xy_sobe else None
    avisos = pr.salvar(f"/home/claude/letsara/pranchas/{P['desenho']}")
    print(P["desenho"], len([a for a in avisos if a[0] == "ERRO"]), "erros,", len(avisos), "avisos")
    for a in avisos:
        print("  ", a)


H_VM = round(_VMP["h_pm"] * 1000)


def consolo(face, z_assento, tipo, larg, proj, h, hp, pino=("PN-1", 20, 700, 300, 175), neo=(300, 150, 10), tir=("3 Ø16", 3, 16.0)):
    return dict(face=face, z=z_assento + 1000, tipo=tipo, larg=larg, proj=proj, h=h, hp=hp, pino_nome=pino[0], pino_d=pino[1], pino_L=pino[2],
                pino_emb=pino[3], pino_x=pino[4], neo=list(neo), tir=tir[0], n_tir=tir[1], d_tir=tir[2])


KP_CEN = [("P8A", X_EIXO["C"], Y_LIN[1], 400, 600, "PC-01"), ("P11", X_EIXO["C"], Y_LIN[3], 400, 400, "PC-02"), ("P13", X_EIXO["C"], Y_P13, 600, 600, "PC-03"),
          ("P8", X_EIXO["B"], Y_LIN[1], 400, 600, "PM-01"), ("P8B", X_EIXO["D"], Y_LIN[1], 400, 600, "PM-01"),
          ("P9", 9.87, Y_LIN[3], 400, 400, "PG-01"), ("P12", 29.63, Y_LIN[3], 400, 400, "PG-03"), ("P10", 15.195, Y_LIN[3], 250, 250, "PG-02"), ("P10", 24.305, Y_LIN[3], 250, 250, "PG-04")]
F = lambda v: f"{v/1000:.3f}".replace(".", ",")
TS_E, TS_A = ASS_TS(20.175), ASS_TS(19.325)
I130 = lambda face: consolo(face, Z_I130, "CP-I130", 500, 400, H_C["CP-I130"], H_C["CP-I130"], ("PN-2", 25, 900, 350, 200), (300, 200, 31), (CONS_J["CP-I130"]["tirante"].split(" (")[0], CONS_J["CP-I130"]["n_ramos"], CONS_J["CP-I130"]["d_tir"]))   # rev04: NEO-2 200 × 300 fretado; a2 = 10 cm
TSC = lambda face, z: consolo(face, z, "CP-TS", 400, 300, H_C["CP-TS"], H_C["CP-TS"])
MEZ = lambda face, z: consolo(face, z, "CP-MEZ", 400, 350, H_C["CP-MEZ"], H_C["CP-MEZ"], ("PN-1", 20, 700, 300, 186), (300, 150, 10), (CONS_J["CP-MEZ"]["tirante"].split(" (")[0], CONS_J["CP-MEZ"]["n_ramos"], CONS_J["CP-MEZ"]["d_tir"]))   # rev04: dente da VM meio vaso
EST_STD = dict(s_corr=150, s_dens=100, zona=1500)
NOTA_CONS = "Consolos sem chanfro: altura = recorte do dente da viga − neoprene, fundo do consolo alinhado ao fundo da viga (CP-MEZ 29, CP-I130 49 cm — memória consolos.json, NBR 9062:2017 7.3). Tirante em alças horizontais (7.3.3: a2 ≥ c + 3,5Ø), costura Ø8 c/10 em 2/3 d."
NOTA_MEZ = " Acima dos CP-MEZ, na largura da VM e até 50 cm acima do assento, face do pilar ÁSPERA (≥ 5 mm a cada 30 mm, NBR 9062:2017 6.3.3): junta da ponta da VM concretada antes das lajes (DEC-039)."


def bars_ret(B, H, nb, nh, c=48):
    """Barras no perímetro: nb ao longo de B (faces de cima/baixo da seção), nh ao longo de H (inclui cantos)."""
    xs = [-B / 2 + c + k * (B - 2 * c) / (nb - 1) for k in range(nb)]
    ys = [-H / 2 + c + k * (H - 2 * c) / (nh - 1) for k in range(nh)]
    pts = {(round(x), round(y)) for x in xs for y in (ys[0], ys[-1])} | {(round(x), round(y)) for y in ys for x in (xs[0], xs[-1])}
    return sorted(pts)


# DEC-040 (22/10/2026): armadura longitudinal redimensionada com o modelo integrado r05 (2ª ordem global + fluência e método geral
# com as cargas nos níveis reais) e o manuseio — arranjo por marca em arranjo_pilares.json (Ø16; estribos Ø6,3; grampos onde a
# barra fica a mais de 20 φt do canto do estribo, NBR 6118 18.2.4)
ARR = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/arranjo_pilares.json"))
D_EST = 6.3


def nota_arm(marca):
    a = ARR[marca]
    gr = len(a["grampos"]["across_B"]) + len(a["grampos"]["across_H"])
    return (f"Concreto C40; {a['n']} Ø{a['d']:g} longitudinais ({a['nb']} em cada face de {a['B']/10:g} e {a['nh']} em cada face de {a['H']/10:g}, cantos comuns), "
            f"retos, sem emenda (barra mais longa < 12 m); estribos N2 Ø{D_EST:g} c/15 (c/10 nos 150 cm do cálice e das pontas)"
            + (f" + {gr} grampo{'s' if gr > 1 else ''} por estribo (N3/N3A)" if gr else "") + ", ganchos 135° com ponta reta de 7 cm. "
            "Armadura dimensionada no modelo global (DEC-040): 2ª ordem global P-Δ + fluência (NBR 6118:2023 15.8.4) e método geral (15.8.3.2) "
            "com as cargas nos níveis reais; manuseio (desforma, transporte e verticalização, NBR 9062:2017 5.3.2) verificado.")


def base(marca, qtd, B, H, ztop, cons, xy, desenho, conteudo, posicao, familia, marcas, insertos, notas, ip01=(), d1=20.0, grampos=(), vistas=("A", "B", "C"), zoom=3.2):
    grampos_h = []
    if marca in ARR:                                                     # DEC-040: arranjo do dimensionamento
        a = ARR[marca]
        xy, d1, grampos, grampos_h = [tuple(p) for p in a["xy"]], a["d"], a["grampos"]["across_B"], a["grampos"]["across_H"]
        notas = [nota_arm(marca)] + list(notas[1:])
    return dict(marca=marca, qtd=qtd, B=B, H=H, L_CAL=1000, Z_TOP=ztop, al=[ztop + 1000 - 2500, 1000 + 1500], consolos=cons, xy=xy, grampos=list(grampos),
                grampos_h=list(grampos_h), d_est=D_EST, est=EST_STD, vistas=list(vistas), ip01=list(ip01), d1=d1, zoom=zoom, desenho=desenho, conteudo=conteudo,
                posicao=posicao, familia=familia, kp=KP_CEN, marcas=marcas, insertos=insertos, memoria=[], notas=notas)


PN5_TOPO = dict(nome="PN-5", d=20, L=600, emb=300, xy=[(sx * 115, sy * 100) for sx in (-1, 1) for sy in (-1, 1)])   # x ao longo de H (A–C), y ao longo de B


def dados_pc1():
    cons = [I130("B"), MEZ("A", Z_MEZ_ASS[0]), MEZ("C", Z_MEZ_ASS[0]), MEZ("A", Z_MEZ_ASS[1]), MEZ("C", Z_MEZ_ASS[1])]
    return base("PC-01", 1, 600, 400, Z_TOP_C, cons, bars_ret(600, 400, 4, 3), "ND-LET-PC01",
                "PILAR CENTRAL PC-01 (P8A, 40×60) — EIXO C, LINHA 2 — FÔRMA, ARMAÇÃO, INSERTOS E LOCAÇÃO",
                "POSIÇÃO: eixo C, linha 2 (P8A); 40 em x × 60 em y", "PILAR CENTRAL PC-01",
                [["PC-01", "P8A (C2)", 1, "topo: 2 TS-01 (oblongo); CP-I130 (B); 2 CP-MEZ (A, C)", "6 CE-1 (B); 2 AL-2"]],
                [["PN-2", "Pino Ø25 CA-50 L=900 (350 no consolo) — CP-I130", 1, "face B"], ["PN-1", "Pino Ø20 CA-50 L=700 — CP-MEZ", 4, "faces A e C"], ["PN-5", "Pino Ø20 CA-50 L=600 (300 no pilar) — topo (TS-01)", 4, "topo, x ±115, y ±100"],
                 ["NEO-2", "Neoprene 300×200×31 fretado (rev04)", 1, "CP-I130"], ["NEO-5", "Neoprene 300×150×10 c/ furo Ø30 (dente da VM)", 4, "CP-MEZ"], ["BA-1", "Bainha corrugada Ø50 horizontal (N11)", 4, "12 cm acima da VM"], ["NEO-3", "Neoprene 100×300×10 c/ 2 furos Ø30", 2, "topo (TS-01)"],
                 ["CE-1", "CE-1 380×330×12,5 + 4 pinos Ø16 + 2 N18 (CS-1, vista G)", 6, "face B, centrada, fiadas 0 a 5"], ["AL-2", "Alça laço cordoalha Ø12,7", 2, "face A"]],
                ["Concreto C40; 10 Ø20 retos de ponta a ponta; estribos N2 Ø8 c/15 (c/10 nos 150 cm do topo e no cálice), ganchos 135°.", NOTA_CONS + NOTA_MEZ,
                 f"TS-01 da linha 2 apoiadas no topo do pilar (topo horizontal em 2 níveis: +{F(Z_TOP_C)} na metade do lado A e +{F(Z_TOP_CD)} na metade do lado E, degrau no eixo C), NEO-3 100×300 e 2 pinos PN-5 Ø20 por TS-01, com os tubos TB-3 da viga preenchidos com mastique (sem graute: a viga desliza ±15 mm em x, o mezanino já trava o pilar); CP-I130 na face B (+{F(Z_I130)}) para a ponta da V407; CP-MEZ nas faces A e C para as VM dos dois níveis.",
                 f"Topo do pilar horizontal em 2 níveis: +{F(Z_TOP_C)} (metade do lado A) e +{F(Z_TOP_CD)} (metade do lado E), degrau de {Z_TOP_CD - Z_TOP_C} mm no eixo C, igual ao topo da I130. CE-1 (chapa de espera dos consoles CS-1) na face B para as placas da parede interna da linha 2 (vista G)."],
                ip01=[dict(face="B", z=IP_C)]) | dict(pinos_topo=PN5_TOPO)


def dados_pc2():
    cons = [I130("B"), I130("D")]
    return base("PC-02", 1, 400, 400, Z_TOP_C, cons, bars_ret(400, 400, 3, 3), "ND-LET-PC02",
                "PILAR CENTRAL PC-02 (P11, 40×40) — EIXO C, LINHA 4 — FÔRMA, ARMAÇÃO, INSERTOS E LOCAÇÃO",
                "POSIÇÃO: eixo C, linha 4 (P11), parede dos portões", "PILAR CENTRAL PC-02",
                [["PC-02", "P11 (C4)", 1, "topo: 2 TS-01; CP-I130 (B, D)", "6 CE-1 (B); 2 AL-2"]],
                [["PN-2", "Pino Ø25 CA-50 L=900 — CP-I130", 2, "faces B e D"], ["PN-5", "Pino Ø20 CA-50 L=600 (300 no pilar) — topo (TS-01)", 4, "topo, x ±115, y ±100"],
                 ["NEO-2", "Neoprene 300×200×31 fretado (rev04)", 2, "CP-I130"], ["NEO-3", "Neoprene 100×300×10 c/ 2 furos Ø30", 2, "topo (TS-01)"],
                 ["CE-1", "CE-1 380×330×12,5 + 4 pinos Ø16 + 2 N18 (CS-1, vista C)", 6, "face B, centrada"], ["AL-2", "Alça laço cordoalha Ø12,7", 2, "face A"]],
                ["Concreto C40; 8 Ø20 retos; estribos N2 Ø8 c/15 (c/10 nos 150 cm do topo e no cálice), ganchos 135°.", NOTA_CONS,
                 f"CP-I130 nas faces B (V406) e D (V407), assento +{F(Z_I130)}; TS-01 da linha 4 apoiadas no topo (topo horizontal em 2 níveis: +{F(Z_TOP_C)} lado A / +{F(Z_TOP_CD)} lado E), NEO-3 100×300 e 2 pinos PN-5 Ø20 por TS-01, grauteados nos tubos TB-3.",
                 "CE-1 (chapa de espera dos consoles CS-1) na face B para as placas da parede dos portões (vista C, fiadas até +7,50)."],
                ip01=[dict(face="B", z=IP_C)]) | dict(pinos_topo=PN5_TOPO)


def dados_pc3():
    cons = [I130("B"), I130("D")]
    return base("PC-03", 1, 600, 600, Z_TOP_C, cons, bars_ret(600, 600, 4, 4), "ND-LET-PC03",
                "PILAR CENTRAL PC-03 (P13, 60×60) — EIXO C — FÔRMA, ARMAÇÃO, INSERTOS E LOCAÇÃO",
                "POSIÇÃO: eixo C, y = 54,575 m (P13), entre as V406 e V405", "PILAR CENTRAL PC-03",
                [["PC-03", "P13", 1, "CP-I130 (B, D)", "2 AL-2"]],
                [["PN-2", "Pino Ø25 CA-50 L=900 — CP-I130", 2, "faces B e D"], ["NEO-2", "Neoprene 300×200×31 fretado (rev04)", 2, "CP-I130"],
                 ["AL-2", "Alça laço cordoalha Ø12,7", 2, "face A"]],
                ["Concreto C40; 12 Ø20 retos; estribos N2 Ø8 c/15 (c/10 nos 150 cm do topo e no cálice), ganchos 135°.", NOTA_CONS,
                 f"CP-I130 nas faces B (V405) e D (V406), assento +{F(Z_I130)}; sem TS-01 (P13 fica entre as linhas 6 e 7)."])


def dados_pm():
    cons = [MEZ("A", Z_MEZ_ASS[0]), MEZ("C", Z_MEZ_ASS[0]), MEZ("A", Z_MEZ_ASS[1]), MEZ("C", Z_MEZ_ASS[1])]
    return base("PM-01", 2, 600, 400, 6550, cons, bars_ret(600, 400, 4, 3), "ND-LET-PM01",
                "PILARES DO MEZANINO PM-01 (P8 E P8B, 40×60) — FÔRMA, ARMAÇÃO, INSERTOS E LOCAÇÃO",
                "POSIÇÃO: linha 2, eixos B e D (P8 e P8B); 40 em x × 60 em y", "PILARES DO MEZANINO PM-01",
                [["PM-01", "P8, P8B", 2, "2 CP-MEZ (A, C)", "6 CE-1 (B); 2 AL-2"]],
                [["PN-1", "Pino Ø20 CA-50 L=700 (300 no consolo)", 4, "consolos CP-MEZ"], ["NEO-5", "Neoprene 300×150×10 c/ furo Ø30 (dente da VM)", 4, "CP-MEZ"], ["BA-1", "Bainha corrugada Ø50 horizontal (N11)", 4, "12 cm acima da VM"],
                 ["CE-1", "CE-1 380×330×12,5 + 4 pinos Ø16 + 2 N18 (CS-1, vista G)", 6, "face B, centrada"], ["AL-2", "Alça laço cordoalha Ø12,7", 2, "face A"]],
                ["Concreto C40; 10 Ø20 retos; estribos N2 Ø8 c/15 (c/10 nos 150 cm das pontas e no cálice), ganchos 135°.", NOTA_CONS + NOTA_MEZ,
                 f"CP-MEZ nas faces A e C: assentos +{F(Z_MEZ_ASS[0])} e +{F(Z_MEZ_ASS[1])} (VM meio vaso com dente Gerber: fundo do consolo = fundo da viga); pino PN-1 Ø20 no TB-1 do dente; sem peça antigiro: a junta VM × pilar é concretada (fck ≥ 30) antes das lajes — DEC-039.",
                 "Topo do pilar em +6,550 (piso superior do mezanino). CE-1 na face B para as placas da parede interna da linha 2 (vista G)."],
                ip01=[dict(face="B", z=IP_C)])


# rev06 (DEC-024): cabeça dos pilares dos portões a 2 cm do fundo da TS-01 da linha 4, ligada à viga em y por 2 cantoneiras
# L 102×102×9,5 (faces x do pilar) — 4 comprimentos → 4 marcas (mesma fôrma e armação por seção)
IL1 = ["IL-1", "Inserto rosqueado M16 hef 100 (cantoneira CL-P)", 2, "faces B e D, 75 do topo"]
NOTA_LIG = ("Cabeça a 2 cm do fundo da TS-01 da linha 4 (a viga sobe 3 % de A para E): em cada face lateral (B e D) uma cantoneira "
            "L 102×102×9,5 L = 250 (CL-P) parafusada com 1 M16 8.8 no inserto IL-1 (furo oblongo vertical 18 × 50, a TS-01 flete livre) e com 2 M16 8.8 "
            "nos insertos do fundo da TS-01; segura só em y a parede dos portões (Fd até 23 kN, cobertura_metalica.json). Portões livres até +7,40.")


def _fiadas_c(x):
    """rev06e: fiadas com console na parede dos portões (vista C do fechamento) para o pilar em x (m) — fonte: fechamento."""
    import fechamento as FCH
    ks = set()
    for (xc, z) in FCH.DADOS["C"][1]:
        s_, b_, n_ = min(FCH.VISTAS["C"]["pil"], key=lambda q: abs(q[0] - xc))
        if abs(s_ - x * 1000) < 50:
            ks.add(round((z - FCH.Z_NC) / FCH.H_PL))
    return [IP_C[k] if k < len(IP_C) else 1250 * k + 922 + 1000 for k in sorted(ks)]


def _pg(marca, nome, x, b, ztop, desenho, d1, est=None):
    secao = f"{b//10}×{b//10}"
    zce = _fiadas_c(x)
    P = base(marca, 1, b, b, ztop, [], bars_ret(b, b, 2, 2), desenho,
             f"PILAR DOS PORTÕES {marca} ({nome}, {secao}) — LINHA 4, x = {x:.3f} m — FÔRMA, ARMAÇÃO, INSERTOS E LOCAÇÃO".replace(".", ","),
             f"POSIÇÃO: linha 4, x = {x:.3f} m ({nome}); topo +{ztop/1000:.2f} (2 cm abaixo da TS-01)".replace(".", ","), "PILARES DA PAREDE DOS PORTÕES",
             [["PG-01", "P9", 1, "sem consolo; topo +7,47", "CE-1 (B); 2 IL-1; 2 AL-2"], ["PG-02", "P10 (x 15,195)", 1, "sem consolo; topo +7,63", "CE-1 (B); 2 IL-1; 2 AL-2"],
              ["PG-04", "P10 (x 24,305)", 1, "sem consolo; topo +7,90", "CE-1 (B); 2 IL-1; 2 AL-2"], ["PG-03", "P12", 1, "sem consolo; topo +8,06", "CE-1 (B); 2 IL-1; 2 AL-2"]],
             [["CE-1", "CE-1 380×330×12,5 + 4 pinos Ø16 + 2 N18 (CS-1)", len(zce), "face B, centrada"], IL1,
              ["AL-2", "Alça laço cordoalha Ø12,7", 2, "face A"]],
             [("Concreto C40; 4 Ø20 retos (cantos); " if b == 400 else "Concreto C40; 4 Ø16 retos (cantos); ") + "estribos c/15 (c/10 nos 150 cm das pontas e no cálice), ganchos 135°.",
              NOTA_LIG,
              "Pilar de fechamento da parede dos portões (vista C): recebe as placas, a folha do portão e o vento; apoiado em y na TS-01 pela cabeça (modelo integrado r05)."],
             ip01=[dict(face="B", z=zce)], d1=d1, zoom=2.8 if b == 400 else 2.4)
    if est:
        P |= dict(d_est=est)
    return P


def dados_pg1():
    return _pg("PG-01", "P9", 9.87, 400, 7470, "ND-LET-PG01", 20.0)


def dados_pg2():
    return _pg("PG-02", "P10a", 15.195, 250, 7630, "ND-LET-PG02", 16.0, 6.3)


def dados_pg3():
    return _pg("PG-03", "P12", 29.63, 400, 8060, "ND-LET-PG03", 20.0)


def dados_pg4():
    return _pg("PG-04", "P10b", 24.305, 250, 7900, "ND-LET-PG04", 16.0, 6.3)


DADOS = dict(pc1=dados_pc1, pc2=dados_pc2, pc3=dados_pc3, pm=dados_pm, pg1=dados_pg1, pg2=dados_pg2, pg3=dados_pg3, pg4=dados_pg4)



def posicao_forma(pr, P, cons, x, y):
    """rev06e (DEC-031): seção do pilar deitado na fôrma — face C (placas) para cima com os CC-1 (consoles já soldados na CE-1,
    concretados com o pilar); face A no fundo; CE-1 das faces laterais B/D rentes, presas na lateral da fôrma."""
    B, H = P["B"], P["H"]
    v = pr.vista("POSIÇÃO NA FÔRMA", (x, y), 10, titulo="POSIÇÃO NA FÔRMA", subtitulo="seção do pilar deitado; face C para cima", unidade="cm")
    xb, yc = B / 2, H                                                    # x: D (−) → B (+); y: A (0, fundo) → C (H, em cima)
    v.ret(-xb - 60, -60, B + 120, 60, "VISTA"); v.ret(-xb - 60, 0, 60, H + 40, "VISTA"); v.ret(xb, 0, 60, H + 40, "VISTA")
    pts = [(-xb, 0), (xb, 0), (xb, yc), (-xb, yc)]
    v.poli(pts, "CORTADO", fechada=True); v.hachura(pts, "AR-CONC", 0.03)
    faces = {ip["face"] for ip in P["ip01"]}
    if "C" in faces:                                                     # CC-1 na face de cima
        v.chapa(-190, yc - 12.5, 380, 12.5)
        for xs in (-120, 120):
            v.ret(xs - 8, yc - 12.5 - 150, 16, 150, "OCULTA")
        for xc_ in (-XC_CS, XC_CS):
            v.ret(xc_ - 52, yc, 104, 64, "METALICA")
        v.chamada((-XC_CS, yc + 50), (-16, 10), "CC-1 (CS-1 de fábrica, sai 64)")
        if P.get("al_face") == "C":
            v.chamada((0, yc), (14, 16), "AL-2 (cortar após montar)")
    for F_, sg in (("B", 1), ("D", -1)):                                 # CE-1 rente na lateral
        if F_ in faces:
            x0 = xb - 12.5 if sg > 0 else -xb
            v.chapa(x0, yc / 2 - 190, 12.5, 380)
            for yy in (yc / 2 - 120, yc / 2 + 120):
                v.ret(x0 - 150 if sg > 0 else x0 + 12.5, yy - 8, 150, 16, "OCULTA")
            v.chamada((x0 + (12.5 if sg > 0 else 0), yc / 2 + 150 * sg), (16 * sg, -6 * sg), f"CE-1 face {F_}: rente, presa na lateral")   # rev08: texto por fora da fôrma
    if any(c["face"] == "A" for c in cons):
        v.ret(-150, -60, 300, 60, "OCULTA")
        v.chamada((-100, -30), (-16, -8), "consolos face A: caixão no fundo")
    v.texto((0, yc - 40), "C (placas)", "nota", "TOP_CENTER"); v.texto((0, 30), "A (interna)", "nota", "BOTTOM_CENTER")
    v.texto((xb - 30, yc / 2), "B", "nota", "MIDDLE_CENTER"); v.texto((-xb + 30, yc / 2), "D", "nota", "MIDDLE_CENTER")
    v.texto((0, -80), "FUNDO DA FÔRMA", "nota", "TOP_CENTER")
    if P.get("rec"):
        v.texto((0, -125), "cabeça: calço 30 cm no fundo", "nota", "TOP_CENTER")


if __name__ == "__main__":
    for q in (sys.argv[1:] or list(DADOS)):
        prancha_pilar(DADOS[q]())
