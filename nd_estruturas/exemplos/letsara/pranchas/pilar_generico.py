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
from geometria import Y_LIN, X_FACH, X_EIXO, Y_P13, Y_PC_C
CONS_J = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/consolos.json"))
LG = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/ligacoes.json"))
ZF = lambda x: LG["Z0_TS"] + 0.03 * x
ASS_TS = lambda x: round((ZF(x) + 0.45 * (1 / (1 + 0.03 ** 2)) ** 0.5 - 0.01) * 1000)
Z_I120 = round(LG["Z_ASS_I120"] * 1000)                          # rev03: assento da I120 = topo − 1,30 + recorte 0,52 − neoprene 0,03
Z_TOP_C = round(LG["Z_TOPO_I120"] * 1000)                         # rev03: topo dos pilares centrais = topo da I120 (TS-01 apoiada no topo)
Z_TOP_CD = round(LG["Z_TOPO_I120_DIR"] * 1000)                    # rev04: metade do lado E do topo (degrau, NBR 9062 7.2.1.6: assentos horizontais)
_VMP = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/vm_retangular.json"))["premissas"]
from geometria import Z_PISOS
# rev09 (DEC-045/047/048): VM retangular 30 × 75 com dente: assento do CP-MEZ = topo da capa − 26 − h da VM + recorte − neoprene fretado 21
Z_PISO_MM = tuple(round(z * 1000) for z in Z_PISOS)
Z_MEZ_ASS = tuple(round(z - 260 - _VMP["h_pm"] * 1000 + _VMP["dente"]["recorte"] * 1000 - 21) for z in Z_PISO_MM)
H_C = {k: round(v["h_total_m"] * 1000) for k, v in CONS_J.items()}
HP_C = {k: round(v.get("h_consolo_m", v["h_total_m"]) * 1000) for k, v in CONS_J.items()}   # DEC-054: altura na ponta (mísula)
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
    V = (B * H * z_rec + HB * HH * (L_TOT - z_rec)) / 1e9 + sum(c["larg"] * c["proj"] * (c["h"] + c["hp"]) / 2 for c in cons) / 1e9
    PESO = V * 25
    FI = furo_icamento(P, L_TOT, REC, cons)
    if not FI["livre"]:
        print(f"  ! {P['marca']}: FI-1 {FI['eixo']} com {FI['obst']} acima do furo nas faces das lingas (nenhum eixo livre)")
    json.dump(dict(fi=FI, B=B, H=H, L_TOT=L_TOT, consolos=cons, ip01=P.get("ip01", []), al=AL, al_face=P.get("al_face", "A"), marca=P["marca"], z_topo=Z_TOP / 1000, zoom=P.get("zoom", 3.2), rec=REC,
                   assento=P.get("assento"), pinos_topo=P.get("pinos_topo")),
              open(f"/home/claude/letsara/pranchas/{P['marca']}_geom.json", "w"))
    subprocess.run([sys.executable, "/home/claude/letsara/pranchas/iso3d_pilar_gen.py", f"/home/claude/letsara/pranchas/{P['marca']}_geom.json",
                    "/home/claude/letsara/pranchas/"], check=True, capture_output=True, env=__import__("gerar_imagens").env())   # rev11: render ≥ 400 ppi
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
        CABP = P.get("cabeca")                                          # DEC-042: armadura própria da cabeça (cabeca_pilares_r05.py)
        n_in = 0 if CABP else P.get("n13_inner", 0)
        if n_in:
            cantos += [(u0 + COB + 18 + k * (u1 - u0 - 2 * (COB + 18)) / (n_in - 1), w1 - COB - 16) for k in range(n_in)]
        xy_cab = []
        if CABP:
            cantos = [tuple(p_) for p_ in CABP["xy_cab"]]
        for c_ in cantos:
            if all(math.hypot(c_[0] - a, c_[1] - b) > 40 for a, b in xy_sobe + xy_cab):
                xy_cab.append((round(c_[0]), round(c_[1])))
    else:
        z_cab, xy_sobe, xy_para, xy_cab = [], xy, [], []
    D13 = (P.get("cabeca") or {}).get("phi", 16.0)
    EMB13 = (P.get("cabeca") or {}).get("emb", 600)
    n_est = len(z_est)
    pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                            conteudo=P["conteudo"], desenho=P["desenho"], folha="01/01", fase="PARA APROVAÇÃO",
                            marca=P["marca"], qtd=P["qtd"], peso=f(PESO, 1), volume=f(V, 2)))
    if P["marca"] == "PM-02":                                           # DEC-050: P14 sai do PM-01 e vira folha nova (só a emissão de 24/10)
        _rv = pr.revisao
        pr.revisao = lambda n, d, t, _rv=_rv: _rv(n, d, t) if d == "24/10/2026" else None
        pr.revisao("", "24/10/2026", "EMISSÃO INICIAL: P14 SEPARADO DO PM-01 (CABEÇA ATÉ O FUNDO DA VIGA METÁLICA DA LINHA 2, DEC-050)")
    pr.revisao("00", "12/10/2026", "EMISSÃO INICIAL")
    pr.revisao("04", "16/10/2026", "NBR 9062: SEM CP-VT; CONSOLOS COM ALÇAS; NEOPRENES REVISTOS; CP-MEZ P/ DENTE DA VM; CP-VB 15×27×29 P/ DENTE DA VB; PL 14 Ø20")
    r06 = ["CE-1 DOS CONSOLES CS-1 DAS PLACAS (TREJOR) NO LUGAR DOS TRILHOS TR-1"]
    if P["marca"] in ("PL-07", "PL-08"):
        r06.insert(0, "ESPERAS ES-1FL (FACE LATERAL) DO APOIO ST-1FL DA ÚLTIMA TERÇA")
    if P["marca"].startswith("PG"):
        r06.insert(0, "CABEÇA A 2 cm DA TS-01; INSERTOS IL-1 (LIGAÇÃO EM y COM A TS-01)")
    if any(ip["face"] == "C" for ip in P.get("ip01", [])):
        r06.append("CE-1 12,5; CC-1 (CS-1 DE FÁBRICA) NA FACE C; FACE C PARA CIMA NA FÔRMA (DEC-031)")
    elif P.get("ip01"):
        r06.append("CE-1 12,5")
    pr.revisao("06", "19/10/2026", "; ".join(r06))
    pr.revisao("07", "21/10/2026", "FÔRMA E ARMAÇÃO NA MESMA FOLHA (PADRÃO USINA)")
    if P.get("cabeca") or not P.get("rec") and P["marca"] in ("PL-03", "PL-04", "PL-07", "PL-08"):
        pr.revisao("08", "22/10/2026", "DEC-042: " + ("SEÇÃO CHEIA ATÉ O TOPO (SEM PLATIBANDA RECUADA)" + ("; ES-1FL NA FACE LATERAL" if P["marca"] in ("PL-07", "PL-08") else "")
                   if not P.get("rec") else "CABEÇA COM ARMADURA PRÓPRIA (N13 POR TRASPASSE)") + "; PLANTA-CHAVE COM NOMES")
    if P["marca"] in ("PM-01", "PC-01", "PE-03"):
        pr.revisao("", "24/10/2026", "DEC-050/052: SEM MONTANTE NO PILAR; CABEÇA DE CONCRETO ATÉ O FUNDO DA W 200 × 15,0 (MONTANTES NO MEIO DOS VÃOS); 4 BR-M16 L 450 + CA-L2" + ("; P14 PASSA A SER O PM-02" if P["marca"] == "PM-01" else ""))
    if any(c["tipo"] == "CP-I120" for c in P.get("consolos", [])):
        pr.revisao("", "24/10/2026", "DEC-054: I120 COM h 120; CONSOLO CP-I120 COM MÍSULA (49 NO PILAR, 39 NA PONTA, FUNDO ALINHADO À VIGA)")
    _r12 = [t for t, ok in (("CONSOLOS COM A LARGURA DA VIGA APOIADA: CP-MEZ 30 COM MÍSULA (40/27,9)", any(c["tipo"] == "CP-MEZ" for c in P.get("consolos", []))),
                             ("CP-I120 40", any(c["tipo"] == "CP-I120" for c in P.get("consolos", []))),
                             ("NEO-6 100 × 60", any(c["tipo"] == "CP-VB" for c in P.get("consolos", []))),
                             ("CP-MEZ RENTE À FACE EXTERNA (VM DA LINHA 1 NA FACE DOS PILARES)", any(c["tipo"] == "CP-MEZ" and c.get("exc") for c in P.get("consolos", []))),
                             ("EIXO 7,5 cm FORA DA LINHA 4: FACE NO PLANO DOS VIZINHOS 40 × 40 (DEC-092)", P["marca"] in ("PG-02", "PG-04")),
                             ("NEO-7 PELA DISTÂNCIA À BORDA (NBR 9062 7.2)", P["marca"].startswith("PG"))) if ok]
    if _r12:
        pr.revisao("R12", "27/10/2026", "; ".join(_r12))
    Q = pr.quadro
    XC = Q[2] - 190
    Y0 = 92
    ESC = 20
    pr.ret(Q[0] + 4, Q[3] - 30, Q[0] + 700, Q[3] - 4, "CARIMBO")
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
                t_as = ("ESP-1", f"{len(AS.get('x_pinos', (1,))) * len(AS['y_pinos'])} {AS.get('marca_b', AS['pino'])}", "ver DET. 3")   # rev11: dados completos no DET. 3 e no quadro
                z_p = z_rec + 10 + AS["L"] - AS["emb"]
                v.texto((W / 2, z_p + 1.5 * ESC), "ESP-1", "nota", "BOTTOM_CENTER")             # rev11: dados no DET. 3 e no quadro
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
            u_ = c.get("exc", 0) * (1 if DIR[face] == c.get("exc_face") else -1 if ESQ[face] == c.get("exc_face") else 0)   # rev12: consolo rente à face
            if c["face"] == face:                                                            # frontal
                v.ret((W - larg) / 2 + u_, zc - h, larg, h, "VISTA")
                v.linha(((W - larg) / 2 + u_, zc - hp), ((W + larg) / 2 + u_, zc - hp), "VISTA")
                v.ret(W / 2 + u_ - c["pino_d"] / 2, zc - c["pino_emb"], c["pino_d"], c["pino_emb"], "OCULTA")
                v.chapa(W / 2 + u_ - c["pino_d"] / 2, zc, c["pino_d"], c["pino_L"] - c["pino_emb"])
                v.chapa(W / 2 + u_ - c["neo"][0] / 2, zc, c["neo"][0], 10)
                if u_:
                    v.cota_h(sorted(set([0, (W - larg) / 2 + u_, (W + larg) / 2 + u_, W])), zc - h, -8, total=False)   # rev12 (item 22): sem cota 0 no consolo rente
                # rev11: só a MARCA do consolo (C1, C2…) dentro da face; geometria, pino e neoprene no quadro APOIOS E ESPERAS e no DET. 1
                import apoios_pilar as AP_
                zl_ = zc - h
                if face == P.get("al_face", "A"):
                    for z_al in AL:
                        if zc - h - 6.0 * ESC < z_al < zc - h:
                            zl_ = min(zl_, z_al - 12)
                v.texto((W / 2 + u_, zl_ - 1.5 * ESC - (12 * ESC if u_ else 0)), AP_.marca_consolo(c), "nota", "TOP_CENTER")
            elif c["face"] == OPOSTA[face]:
                v.ret((W - larg) / 2 + u_, zc - h, larg, h, "OCULTA")
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
                x_ce = (W - 380) / 2
                if ip.get("aresta_C"):                                                     # DEC-042: ponta de parede — CE-1 a 5 mm da aresta da face C
                    x_ce = (W - 385) if DIR[face] == "C" else 5
                for k_, z in enumerate(ip["z"]):
                    b_ce = ip.get("largo", {}).get(k_, 380)                               # DEC-044: CE-1L 840 (asas além do pilar) na fiada 5 dos PC
                    v.chapa(x_ce - (b_ce - 380) / 2, z - 165, b_ce, 330)
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
            v.texto((W / 2, z_fi), "FI-1", alinh="TOP_CENTER")       # rótulo dentro da face, sob o furo (as chamadas dos consolos ficam fora)
        else:                                                                                # atravessando (oculto)
            v.ret(0, FI["z"] - FI["d"] / 2, W, FI["d"], "OCULTA")
        af_ = P.get("al_face", "A")                                                         # rev11: AL-2 desenhada nas faces (Nathan 26/10)
        if face == af_:                                                                     # face de cima da fôrma: laço visto de frente
            for z in AL:
                v.poli([(W / 2 - 56, z - 7), (W / 2 + 56, z - 7), (W / 2 + 56, z + 7), (W / 2 - 56, z + 7)], "ARMADURA", fechada=True)
                v.circulo((W / 2 - 50, z), 6.35, "ARMADURA"); v.circulo((W / 2 + 50, z), 6.35, "ARMADURA")
            for z in AL:
                v.texto((W / 2, z - 30), "AL-2", "nota", "TOP_CENTER")                    # rev11: rótulo curto dentro da face
        elif DIR[face] == af_ or ESQ[face] == af_:                                          # faces laterais: laço de perfil (sai 12 cm da face)
            xe_ = W if DIR[face] == af_ else 0
            sg_ = 1 if xe_ == W else -1
            dp_ = (H if af_ in "AC" else B) - 30                                            # pernas até 3 cm da face oposta, laço aberto nas barras N1
            for z in AL:
                v.linha((xe_, z), (xe_ - sg_ * dp_, z), "OCULTA")
                v.poli([(xe_, z - 7), (xe_ + sg_ * 120, z - 7), (xe_ + sg_ * 120, z + 7), (xe_, z + 7)], "ARMADURA")
        for es in P.get("esperas_face", []):                                               # DEC-042: barras roscadas embutidas na face (padrão Mitsubishi)
            if face == "A" and es["face"] not in P["vistas"]:                               # face lateral sem vista: barras vistas de lado na face A
                x_e, sg_ = (W, 1) if DIR["A"] == es["face"] else (0, -1)
                v.linha((x_e, es["z"]), (x_e - sg_ * es["emb"], es["z"]), "OCULTA")
                v.chapa(min(x_e, x_e + sg_ * es["sai"]), es["z"] - es["d"] / 2, es["sai"], es["d"])
                v.chamada((x_e - sg_ * 60, es["z"]), (-4 * sg_, (L_TOT - es["z"]) / ESC + 6), f"{es['rot']} (face {es['face']})")
            if es["face"] == face:
                xA = (lambda a: W - a) if DIR[face] == "A" else (lambda a: a)
                for a in es["da"]:
                    v.circulo((xA(a), es["z"]), es["d"] / 2, "METALICA")
                    v.circulo((xA(a), es["z"]), es["d"] / 2 + 10, "OCULTA")
                sg_ = 1 if DIR[face] == "A" else -1                                        # chamada para fora, do lado da face A
                v.chamada((xA(es["da"][0]), es["z"]), (9 * sg_, (L_TOT - es["z"]) / ESC + 6), es["rot"])   # texto acima do topo do pilar
        cf = [c for c in cons if c["face"] == face]
        zs = sorted(set([0, L_CAL] + [c["z"] for c in cf] + [c["z"] - c["h"] for c in cf] + ([z_rec] if REC else []) + [L_TOT]
                    + [es["z"] for es in P.get("esperas_face", []) if es["face"] == face or (face == "A" and es["face"] not in P["vistas"])]
                    + (list(AL) if face == af_ or DIR[face] == af_ or ESQ[face] == af_ else [])          # rev11: posição das alças AL-2 cotada
                    + ([FI["z"]] if face in FI["eixo"] else [])))                                   # rev11: furo FI-1 cotado
        from ezdxf import bbox as _bb                                         # rev11: as cadeias ficam fora do que foi desenhado (consolo mais largo que a face)
        _g = [e_ for e_ in v.ents if e_.dxftype() not in ("TEXT", "MTEXT", "DIMENSION") and e_.dxf.layer not in ("CHAMADA", "EIXO")]
        _x = _bb.extents(_g, fast=True) if _g else None
        _xmin = min(-EXT[-1], (_x.extmin.x - v.o[0]) * v.esc) if _x and _x.has_data else -EXT[-1]
        _xmax = max(W + EXT[1], (_x.extmax.x - v.o[0]) * v.esc) if _x and _x.has_data else W + EXT[1]
        v.xl, v.xr = _xmin, _xmax
        v.cota_v(zs, _xmin, -11)
        v.zs_cota = list(zs)
        ords = sorted(set([0, L_CAL] + [es["z"] for es in P.get("esperas_face", []) if face == "A" and es["face"] not in P["vistas"]] + [c["z"] for c in cons if c["face"] == face] + [z for ip in P.get("ip01", []) if ip["face"] == face for z in ip["z"]] + [L_TOT]))   # rev12 (item 22): todas as faces cotadas ao CENTRO da chapa CE-1/CC-1
        v.zs_ords = list(ords) if len(ords) > 3 else []
        if len(ords) > 3:
            v.cota_v(ords, _xmax, 11)                                                    # rev06e: cadeia + total (usina), sem acumuladas
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
    XN = getattr(vA, "xl", -vA.ext[-1]) - 12.5 * ESC                                                                     # rev06e: níveis por fora das cadeias de cota
    nivel(vA, XN, L_CAL, "±0,00", -1)
    nivel(vA, XN, L_TOT, f"+{f(Z_TOP/1000, 2)}", -1)
    _zn = set()
    for c in sorted(cons, key=lambda c: c["z"]):                                       # rev11: nível de TODOS os consolos (qualquer face)
        if all(abs(c["z"] - q) > 4.5 * ESC for q in _zn):
            nivel(vA, XN, c["z"], f"+{f((c['z'] - L_CAL)/1000, 2)}", -1)
            _zn.add(c["z"])
    XM0, XM1 = getattr(vA, "xl", -vA.ext[-1]) - 10.5 * ESC, getattr(vA, "xr", largura(P["vistas"][0]) + vA.ext[1]) + 10.5 * ESC      # rev08: letras por fora das cadeias de cota
    meios = [(a + b) / 2 for zz in (vA.zs_cota, vA.zs_ords) for a, b in zip(zz[:-1], zz[1:])] + \
            [(zz[0] + zz[-1]) / 2 for zz in (vA.zs_cota, vA.zs_ords) if len(zz) > 2]           # textos das cotas totais
    proib = [(c["z"] - c["h"] - 10.5 * ESC, c["z"] + 3 * ESC) for c in cons]
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
    if _caixa(vs_[-1])[1] > XD - 4:                                      # rev11: a coluna da fôrma anda para a direita (texto maior)
        XD = _caixa(vs_[-1])[1] + 4

    # ------------------------------------------------------------ rev07: coluna de detalhes da fôrma (à direita das faces)
    YT = Q[3] - 38
    if xp > XD:
        print(f"  ! {P['marca']}: faces passam da coluna da fôrma ({xp:.0f} > {XD:.0f})")
    # planta-chave 1:750
    kp = pr.vista("PLANTA-CHAVE", (XD + 62, YT - 120), 750, titulo="PLANTA-CHAVE", subtitulo="peças desta folha circuladas", unidade="cm")
    Xm = lambda m: m * 1000
    for y in Y_LIN:
        kp.linha((Xm(-2.5 + 1.9), Xm(y)), (Xm(42.0), Xm(y)), "EIXO")                    # rev06e: eixo para na bolha
    for x in X_FACH:
        kp.linha((Xm(x), Xm(-2.5)), (Xm(x), Xm(85.5 - 1.9)), "EIXO")
    for i, y in enumerate(Y_LIN, 1):
        kp.circulo((Xm(-2.5), Xm(y)), 1800, "VISTA"); kp.texto((Xm(-2.5), Xm(y)), str(i), "nota", "MIDDLE_CENTER")
    for j, x in enumerate(X_FACH):
        kp.circulo((Xm(x), Xm(85.5)), 1800, "VISTA"); kp.texto((Xm(x), Xm(85.5)), "ABCDE"[j], "nota", "MIDDLE_CENTER")
    sel = []
    for nome, x, y, bx, by, mk in P["kp"]:
        pts = [(Xm(x) - bx / 2, Xm(y) - by / 2), (Xm(x) + bx / 2, Xm(y) - by / 2), (Xm(x) + bx / 2, Xm(y) + by / 2), (Xm(x) - bx / 2, Xm(y) + by / 2)]
        kp.poli(pts, "CORTADO", fechada=True)
        if mk == P["marca"]:
            kp.hachura(pts, "ANSI31", 0.3)
            sel.append((x, y))
    # rev08 (regra do Nathan, 22/10/2026): cada peça desta folha com CÍRCULO e CHAMADA com o nome próprio (P1, P2...),
    # rótulos fora da malha, à direita, um por posição (não cruzam eixos nem textos)
    NM = [q for q in json.load(open("/home/claude/letsara/pranchas/nomes.json", encoding="utf-8"))["pecas"] if q["tipo"] == "pilar"]
    import renomear as RN_
    nome_de = lambda x, y: RN_.MARCA_NOVO + min(NM, key=lambda q: math.hypot(q["x"] - x, q["y"] - y))["nome"]   # nome já novo: protegido da renomeação (P9 velho ≠ P9 novo)
    y_ocup = []
    for x, y in sorted(sel, key=lambda t: (t[1], t[0])):
        yl = Xm(y) / 750 + 2.5                                                          # papel (mm) relativo ao modelo
        while any(abs(yl - q) < 4.0 for q in y_ocup):
            yl += 4.0
        y_ocup.append(yl)
        kp.destaque((Xm(x), Xm(y)), nome_de(x, y), desloc_papel=((Xm(43.0) - Xm(x)) / 750, yl - Xm(y) / 750), r_papel=1.7)

    # ------------------------------------------------------------ CORTE A-A (1:10)
    YS = YT - 178 - H / 20
    v = pr.vista("CORTE A-A", (XD + 44, YS), 10, titulo="CORTE A-A", subtitulo="corrente (fôrma)", unidade="cm")
    pts = [(-B / 2, -H / 2), (B / 2, -H / 2), (B / 2, H / 2), (-B / 2, H / 2)]
    v.poli(pts, "CORTADO", fechada=True); v.hachura(pts, "AR-CONC", 0.03)
    v.cota_h([-B / 2, B / 2], -H / 2, -12); v.cota_v([-H / 2, H / 2], B / 2, 14)
    v.texto((0, H / 2 + 30), "FACE A", "min", "BOTTOM_CENTER"); v.texto((0, -H / 2 - 130), "FACE C", "min", "TOP_CENTER")
    v.texto((B / 2 + 170, 0), "FACE B", "min", "MIDDLE_LEFT", rot=90); v.texto((-B / 2 - 30, 0), "FACE D", "min", "MIDDLE_RIGHT", rot=90)

    if REC:
        vc = pr.vista("CORTE C-C", (XD + 44 + max(B / 10 + 52, 92), YS), 10, titulo="CORTE C-C", subtitulo="cabeça (fôrma)", unidade="cm")
        u0, u1 = -B / 2 + rd("D"), B / 2 - rd("B")
        w0, w1 = -H / 2 + rd("C"), H / 2 - rd("A")
        vc.poli([(-B / 2, -H / 2), (B / 2, -H / 2), (B / 2, H / 2), (-B / 2, H / 2)], "OCULTA", fechada=True)
        pc = [(u0, w0), (u1, w0), (u1, w1), (u0, w1)]
        vc.poli(pc, "CORTADO", fechada=True); vc.hachura(pc, "AR-CONC", 0.03)
        AS_ = P.get("assento")
        if AS_:                                                          # rev11: posição das barras do apoio no recuo, cotada até as faces
            f_r = max(REC["d"], key=lambda k: REC["d"][k])
            xs_ = AS_.get("x_pinos", (AS_["x_pino"],))
            if f_r in "AC":
                sgn_, wf_ = (1, w1) if f_r == "A" else (-1, w0)
                pts_ = [(y_, wf_ + sgn_ * x_) for x_ in xs_ for y_ in AS_["y_pinos"]]
                ux_ = sorted({p_[0] for p_ in pts_}); wy_ = sorted({p_[1] for p_ in pts_})
                for p_ in pts_:
                    vc.circulo(p_, AS_["d"] / 2 + 3, "METALICA")
                vc.cota_h(sorted(set([-B / 2] + ux_ + [B / 2])), H / 2 if f_r == "A" else -H / 2, 8 if f_r == "A" else -8, total=False)
                vc.cota_v(sorted(set([wf_] + wy_ + [H / 2 if f_r == "A" else -H / 2])), -B / 2, -8, total=False)
            else:
                sgn_, uf_ = (1, u1) if f_r == "B" else (-1, u0)
                pts_ = [(uf_ + sgn_ * x_, y_) for x_ in xs_ for y_ in AS_["y_pinos"]]
                for p_ in pts_:
                    vc.circulo(p_, AS_["d"] / 2 + 3, "METALICA")
                vc.cota_h(sorted(set([uf_] + [p_[0] for p_ in pts_] + [B / 2 if f_r == "B" else -B / 2])), -H / 2, -8, total=False)
                vc.cota_v(sorted(set([-H / 2] + [p_[1] for p_ in pts_] + [H / 2])), B / 2 if f_r == "B" else -B / 2, 8 if f_r == "B" else -8, total=False)
        else:
            vc.cota_h([u0, u1], w0, -8)
        vc.cota_v([w0, w1], u1, 8)

    # ------------------------------------------------------------ DETALHE 1 — consolo (1:10) e DETALHE 2 — base (1:20)
    YM = YS - H / 20 - 38                                               # rev08: CORTE A-A não encosta no DETALHE 1
    if cons:
        c0 = max(cons, key=lambda c: c["h"])
        d1 = pr.vista("DETALHE 1", (XD + 92, YM - 150), 10, titulo=f"DETALHE 1 — CONSOLO {c0['tipo']}",
                      subtitulo="fôrma, pino, neoprene" + (f"; caimento {c0.get('incl', 0.03) * 100:g} %" if c0.get("incl", 0.03) else ""), unidade="cm")
        PW = largura(OPOSTA[c0["face"]]) if c0["face"] in "BD" else H
        PW = H if c0["face"] in "AC" else B
        zc0, Z1, Z2 = 1000, 400, 1450
        proj, h, hp = c0["proj"], c0["h"], c0["hp"]
        d1.poli([(-PW, Z1), (-PW, Z2), (0, Z2), (0, Z1)], "VISTA"); d1.interrupcao((-PW, Z1), (0, Z1)); d1.interrupcao((-PW, Z2), (0, Z2))
        d1.poli([(0, zc0 - h), (proj, zc0 - hp), (proj, zc0 + proj * c0.get("incl", 0.03)), (0, zc0)], "VISTA")
        d1.ret(c0["pino_x"] - c0["pino_d"] / 2, zc0 - c0["pino_emb"] + 5, c0["pino_d"], c0["pino_emb"], "OCULTA")
        d1.chapa(c0["pino_x"] - c0["pino_d"] / 2, zc0 + 5, c0["pino_d"], c0["pino_L"] - c0["pino_emb"])
        d1.chapa(25, zc0 + 1, c0["neo"][1], 10)
        d1.cota_v(sorted(set([zc0 - h, zc0 - hp, zc0])), proj, 15, total=False)          # rev08: caimento no subtítulo (cota de 1,2 cruzava as linhas)
        d1.cota_h([0, c0["pino_x"], proj], zc0 - h, -12, total=False); d1.cota_h([-PW, 0], Z1, -15)
        d1.chamada((c0["pino_x"], zc0 + 350), (10, 10), f"{c0['pino_nome']} Ø{c0['pino_d']} {'roscado A36' if c0['pino_nome'] == 'PN-6' else 'CA-50'} L = {c0['pino_L']/10:g} cm")
        d1.chamada((150, zc0 + 6), (16, 20), f"neoprene {c0['neo'][0]}×{c0['neo'][1]}×{c0['neo'][2]} mm")
        # rev12 (revisão rev12, item 22): embutido, livre e trecho roscado do pino cotados no próprio detalhe
        lv_ = c0["pino_L"] - c0["pino_emb"]
        d1.cota_v([zc0 - c0["pino_emb"] + 5, zc0 + 5, zc0 + 5 + lv_], 0, -14, total=True)   # emb. + livre = total, dentro do contorno do pilar
        if c0["pino_nome"] == "PN-6":
            import apoios_pilar as _APr
            d1.linha((c0["pino_x"] - 18, zc0 + 5 + lv_ - _APr.PN6_ROSCA), (c0["pino_x"] + 18, zc0 + 5 + lv_ - _APr.PN6_ROSCA), "COTA")
            d1.chamada((c0["pino_x"], zc0 + 5 + lv_ - _APr.PN6_ROSCA / 2), (-14, 6), f"rosca M20 {_APr.PN6_ROSCA / 10:g} cm")


    YD2 = (YM - 150 + 400 / 10 - 34) if cons else YM
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
        posicao_forma(pr, P, cons, XD + 90, YD2 - 82 - 25 - 24 - H / 10 - 18); d2.chamada((H / 2, L_CAL), (16, -6), "piso ±0,000; graute")


    # ------------------------------------------------------------ tabelas
    y = Q[3] - 6
    y = tabela_q(pr, XC, y, f"MARCAS — {P['familia']}", ["MARCA", "POSIÇÃO", "QT", "CONSOLOS (face)", "INSERTOS"], P["marcas"], [16, 22, 8, 86, 50], h_lin=6.0)
    L_N1 = round((L_TOT - 80) / 10)
    EXT_B, EXT_H = B - 2 * COB, H - 2 * COB
    L_N1A = round((z_rec - 30 - 40) / 10 + 15)
    barras = ([dict(pos="N1", diam=D1, qtd=len(xy_sobe), comp=L_N1, trechos=[f"{L_N1}"], geo=dict(k="R", a=L_N1))] if xy_sobe else []) + \
             ([dict(pos="N1A", diam=D1, qtd=len(xy_para), comp=L_N1A, forma=[(0, 0), (85, 0), (85, 8)], trechos=[f"{L_N1A - 15}", "15"], geo=dict(k="L", a=L_N1A - 15, g=15))] if xy_para else []) + \
             ([dict(pos="N13", diam=D13, qtd=len(xy_cab), comp=round((L_TOT - 40 - (z_rec - EMB13)) / 10), trechos=[f"{round((L_TOT - 40 - (z_rec - EMB13)) / 10)}"], geo=dict(k="R", a=round((L_TOT - 40 - (z_rec - EMB13)) / 10)))] if xy_cab else []) + \
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
        import apoios_pilar as _AP
        marcas_c = "/".join(sorted({_AP.marca_consolo(c) for c in cs}, key=lambda m_: int(m_[1:]) if m_[1:].isdigit() else 99))   # rev12: marca do registro (C1…)
        arm_cons.append(dict(pos=(pa, pb, pc), tipos=tipos, marcas=marcas_c, n=n_cons, nt=nt, dt=dt, proj=proj, PW=PWc, larg=lg, h=hc, n6=len(range(60, proj - 40, 80)),
                             faces=[(c["face"], c["z"], c["tipo"]) for c in cs], incl=cs[0].get("incl", 0.03)))
        pr.posicoes_desenho.update({pa, pb, pc})
    area_f = (2 * (B + H) * z_rec + 2 * (HB + HH) * (L_TOT - z_rec) + B * H + (B * H - HB * HH) +
              sum(2 * c["proj"] * c["h"] + c["larg"] * c["h"] + c["larg"] * c["proj"] - c["larg"] * c["h"] for c in cons)) / 1e6
    json.dump(dict(marca=P["marca"], qtd=P["qtd"], desenho=P["desenho"], posicao=P["posicao"], B=B, H=H, L_TOT=L_TOT, L_CAL=L_CAL, Z_TOP=Z_TOP, COB=COB,
                   rec=REC, z_rec=z_rec, HB=HB, HH=HH, D1=D1, xy=xy, xy_sobe=xy_sobe, xy_para=xy_para, xy_cab=xy_cab, emb13=EMB13, d13=D13, grampos=P["grampos"], grampos_h=P.get("grampos_h", []),
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
    import apoios_pilar as AP
    rows_ap, err_ap = AP.linhas(P, cons, L_CAL, L_TOT, z_rec, REC, rd, B, H)
    pr.avisos_extra += err_ap
    if rows_ap:                                                                            # rev11 (item 13): apoios e esperas completos
        y = tabela_q(pr, XC, y - 4, f"APOIOS E ESPERAS — níveis em m (base em cm), barras em cm",
                     ["APOIO", "FACE", "NÍVEL (BASE)", "PEÇA / CHAPA", "BARRA", "EMB.", "LIVRE", "TOTAL"], [r_[:8] for r_ in rows_ap], [24, 15, 25, 30, 46, 13, 14, 15], h_lin=6.0)
        y = pr.notas(XC, y - 2, [f"{r_[0]}: {r_[8]}." for r_ in rows_ap], 182)
    import registro as _REGI                                                               # rev12 (itens 6/7): descrição única e 1 neoprene por apoio
    ins_ = [[r_[0], _REGI.DESC_CANON.get(r_[0], r_[1])] + list(r_[2:]) for r_ in ins_]
    for tp_, ap_ in _REGI.APARELHOS.items():
        n_c = sum(1 for c in cons if c["tipo"] == tp_)
        n_t = sum(int(r_[2]) for r_ in ins_ if r_[0] == ap_["marca"] and str(r_[2]).isdigit())
        outros = [r_[0] for r_ in ins_ if r_[0].startswith("NEO") and tp_ in str(r_[3]) and r_[0] != ap_["marca"]]
        if n_c != n_t or outros:
            pr.avisos_extra.append(("ERRO", f"{ap_['marca']}: {n_t} na tabela de insertos × {n_c} consolos {tp_}" + (f"; outro neoprene no mesmo apoio: {outros}" if outros else "")))
        if n_c and any(list(c["neo"]) != list(ap_["dims"]) for c in cons if c["tipo"] == tp_):
            pr.avisos_extra.append(("ERRO", f"{tp_}: neoprene da geometria ≠ {ap_['marca']} {ap_['dims']}"))
    for pn_ in ("PN-1", "PN-2", "PN-6"):
        n_c = sum(1 for c in cons if c["pino_nome"] == pn_)
        n_t = sum(int(r_[2]) for r_ in ins_ if r_[0] == pn_ and str(r_[2]).isdigit())
        if n_c != n_t:
            pr.avisos_extra.append(("ERRO", f"{pn_}: {n_t} na tabela de insertos × {n_c} consolos"))
    y = tabela_q(pr, XC, y - 4, f"INSERTOS POR PILAR ({P['marca']}) — dimensões em mm", ["MARCA", "DESCRIÇÃO", "QT", "POSIÇÃO"], ins_, [19, 80, 8, 75])
    qd = [["MARCA", P["marca"], "SEÇÃO", P.get("secao_xy", f"{H/10:g} × {B/10:g} cm (x × y)")], ["COMPRIMENTO", f"{L_TOT/10:g} cm", "CONCRETO", "C40"],
          ["VOLUME", f"{f(V, 2)} m³", "PESO", f"{f(PESO/10, 2)} t"], ["AÇO CA-50", f"{f(ta['total_kg'], 0)} kg", "TAXA", f"{f(len(xy) * 3.1416 * (D1 / 10) ** 2 / 4 / (B * H / 100) * 100, 2)} %"],
          ["QUANTIDADE", f"{P['qtd']}", "COBRIMENTO", "3,0 cm (CAA II)"]] + ([["CABEÇA", f"{HB/10:g} × {HH/10:g} cm acima de +{f((z_rec - L_CAL)/1000, 2)}", "", ""]] if REC else [])
    y = tabela_q(pr, XC, y - 4, "QUADRO DA PEÇA", ["ITEM", "VALOR", "ITEM", "VALOR"], qd, [30, 60, 30, 62])
    # rev11: sem "memória resumida" na folha do cliente (regra do Nathan) — as verificações ficam na MC11
    y = pr.legenda_armadura(XC, y - 4, False)
    ISO_ = f"/home/claude/letsara/pranchas/ISO-{P['marca']}-2v.png"
    import os as _os
    y_iso0 = QY_ARM + 40
    if P.get("assento") and REC:                                                           # rev11 (item 13): DETALHE 3 sob o isométrico
        AS_ = P["assento"]
        f_r = max(REC["d"], key=lambda k: REC["d"][k])
        HW_ = (H if f_r in "AC" else B) - REC["d"][f_r]
        org3 = (QX_ARM + 158 + 30 + HW_ / 10, QY_ARM + 40 + 30 + (AS_["emb"] + 150) / 10)
        AP.detalhe3(pr, P, REC, rd, B, H, L_TOT, z_rec, org3)
        y_iso0 = org3[1] + (min(L_TOT - z_rec, 450) + AS_["L"] - AS_["emb"] + 250) / 10 + 14
    if _os.path.exists(ISO_) and ra["ymeio"] - y_iso0 > 140:
        from PIL import Image as _Im
        wi_, hi_ = _Im.open(ISO_).size
        hh_ = min(ra["ymeio"] - 6 - y_iso0, 470, (220 - 6) * hi_ / wi_)
        ww_ = hh_ * wi_ / hi_ + 6
        xi0 = QX_ARM + 158 + (226 - ww_) / 2
        yi0 = y_iso0 + (ra["ymeio"] - 6 - y_iso0 - hh_) / 2
        pr.imagem(xi0, yi0, xi0 + ww_, yi0 + hh_, ISO_, titulo="ISOMÉTRICO DA PEÇA", subtitulo="duas vistas; sem escala")
    nota_fi = [] if FI["livre"] else [f"FI-1 (faces {FI['eixo'][0]}–{FI['eixo'][1]}): há {FI['obst']} acima do furo numa das faces por onde sobem as lingas. Verticalizar e montar com balancim (lingas verticais) e afastadores de madeira entre a linga e a saliência; a linga nunca pode apoiar na quina."]
    y_nt = pr.notas(XC, y - 4, P["notas"] + nota_fi + ["Desformar, bascular e transportar só com fcj ≥ 25 MPa (corpo de prova curado com a peça); cobrimento 3,0 cm (CAA II); transportar deitado em 2 apoios a 0,21 L das pontas, sem apoiar sobre consolos ou consoles metálicos. AL-2 — alças de cordoalha Ø12,7 (CP-190 RB, não engraxada — NBR 9062:2017 5.3.3): só na FÁBRICA, para tirar da fôrma, estocar e carregar no caminhão. FI-1 — furo de içamento: para a MONTAGEM na obra (verticalizar e colocar no cálice), com pino de aço passante + 2 manilhas (ND-LET-IC01).",
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


import geometria as _G
KP_CEN = [("P6E", 36.175, 3.79, 250, 400, "PE-01"), ("P7E", 39.50, 3.79, 600, 400, "PE-02"), ("P6", 36.175, Y_LIN[1], 250, 400, "PE-03"),
          ("P8A", X_EIXO["C"], Y_LIN[1], 400, 600, "PC-01"), ("P11", X_EIXO["C"], Y_LIN[3], 400, 400, "PC-02"), ("P13", X_EIXO["C"], Y_PC_C[0], 400, 400, "PC-03"), ("P13B", X_EIXO["C"], Y_PC_C[1], 400, 400, "PC-03"),
          ("P8", X_EIXO["B"], Y_LIN[1], 400, 600, "PM-01"), ("P8B", X_EIXO["D"], Y_LIN[1], 400, 600, "PM-02"),
          ("P9", 9.87, Y_LIN[3], 400, 400, "PG-01"), ("P12", 29.63, Y_LIN[3], 400, 400, "PG-03")] + \
         [(_G.PG_L4[k][0], _G.PG_L4[k][1], _G.Y_PG[k], round(_G.PG_L4[k][2] * 1000), round(_G.PG_L4[k][3] * 1000), k) for k in ("PG-02", "PG-04")]   # rev12: 25×40, eixo y no plano da face (DEC-092)
F = lambda v: f"{v/1000:.3f}".replace(".", ",")
TS_E, TS_A = ASS_TS(20.175), ASS_TS(19.325)
I120 = lambda face: consolo(face, Z_I120, "CP-I120", round(CONS_J["CP-I120"]["b_m"] * 1000), 400, H_C["CP-I120"], HP_C["CP-I120"], ("PN-2", 25, 900, 350, 200), (300, 200, 31), (CONS_J["CP-I120"]["tirante"].split(" (")[0], CONS_J["CP-I120"]["n_ramos"], CONS_J["CP-I120"]["d_tir"]))   # rev04: NEO-2 200 × 300 fretado; a2 = 10 cm
TSC = lambda face, z: consolo(face, z, "CP-TS", 400, 300, H_C["CP-TS"], H_C["CP-TS"])
MEZ = lambda face, z: consolo(face, z, "CP-MEZ", round(CONS_J["CP-MEZ"]["b_m"] * 1000), round(_VMP["dente"]["consolo_proj"] * 1000), H_C["CP-MEZ"], HP_C["CP-MEZ"], ("PN-1", 20, 630, 230, round(_VMP["x_pad"] * 1000)), (200, 200, 21), (CONS_J["CP-MEZ"]["tirante"].split(" (")[0], CONS_J["CP-MEZ"]["n_ramos"], CONS_J["CP-MEZ"]["d_tir"]))   # rev09: dente da VM retangular 30 × 75; pino 230 no consolo de 27,9 (não sai pelo fundo) + 400 no dente
EST_STD = dict(s_corr=150, s_dens=100, zona=1500)
NOTA_CONS = f"Consolos: altura na ponta = recorte do dente da viga − neoprene, fundo da ponta alinhado ao fundo da viga (CP-MEZ {str(H_C['CP-MEZ'] / 10).replace('.', ',')} cm; CP-I120 com MÍSULA de concreto: {H_C['CP-I120'] / 10:g} cm junto ao pilar e {HP_C['CP-I120'] / 10:g} cm na ponta, fundo inclinado; verificação na memória de cálculo, NBR 9062:2017 7.3). Tirante em alças horizontais (7.3.3: a2 ≥ c + 3,5Ø), costura Ø8 c/10 em 2/3 d."
NOTA_MEZ = " Acima dos CP-MEZ, na largura da VM (25) e até 50 cm acima do assento, face do pilar ÁSPERA (≥ 5 mm a cada 30 mm, NBR 9062:2017 6.3.3): junta da ponta da VM concretada antes das lajes (DEC-039)."
# rev09b (DEC-050, decisão do Nathan 24/10): sem montantes — a cabeça de concreto sobe até o fundo da W 310 da linha 2 (cada pilar na sua
# altura, seguindo a inclinação); a W apoia direto na chapa CA-L2 250 × 250 × 19 sobre graute 20 mm, parafusada em 4 BR-M20 embutidas
_CB2 = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/cob_linha2.json"))
Z_L2 = {a["nome"]: round(a["z_concreto"] * 1000) for a in _CB2["apoios_diretos"]}       # mm, topo do concreto em cada apoio
# DEC-052 (24/10): W 200 × 15,0 (montantes no meio dos vãos): 4 BR-M16 a 150 (x, ao longo da W) × 55 (y) atravessando a chapa e a mesa da W
W_L2 = _CB2["perfil"].replace("x", "×")
BRM20_TOPO = dict(nome="BR-M16", d=16, L=450, emb=350, xy=[(sx * 75, sy * 27.5) for sx in (-1, 1) for sy in (-1, 1)], aco="barra roscada M16 classe 8.8 (ISO 898-1), zincada a fogo", anc="grampo U Ø10 CA-50 na ponta embutida", rosca=150,
                  pilha=[("graute", 20), ("CA-L2", 19), ("mesa da W", 5.2), ("arruela", 3), ("porca", 13), ("contraporca", 13), ("2 fios de rosca", 4)], viga="W 200 × 15,0", destino="atravessa a CA-L2 e a mesa inferior da W")   # 150 × 55 no centro do topo
BRM20_INS = ["BR-M16", f"4 barras roscadas M16 8.8 L=450 (350 embutidos + grampo U Ø10), saem 100 — apoio direto da {W_L2} da linha 2: graute 20 + chapa CA-L2 250×250×19 + mesa da W + arruela, porca e contraporca (DEC-050/052)", 4, "topo, x ±75, y ±27,5 (centro da cabeça)"]
NOTA_W = ("Cabeça de concreto até o fundo da " + W_L2 + " da linha 2 (DEC-050/052, sem montante no pilar): topo HORIZONTAL em +{z}, 39 mm abaixo do fundo da W; graute de nivelamento 20 mm "
          "(ajuste ±10 mm), chapa de apoio CA-L2 250 × 250 × 19 (ASTM A36, galvanizada) e 4 barras roscadas BR-M16 8.8 embutidas 350 mm com grampo U Ø10 (padrão ND/Mitsubishi), "
          "a 150 (ao longo da W) × 55 (gabarito da mesa), atravessando a chapa e a mesa inferior da W; arruela, porca e contraporca por dentro da W. "
          "No eixo C (apoio fixo) furo padrão e torque; nos demais apoios furo oblongo na mesa (ao longo da W) e porca encostada (folga ≤ 1 mm) para a W deslizar na dilatação — tudo parafusado, sem solda. "
          "POSIÇÃO DAS BARRAS: ±2 mm (gabarito de chapa na fôrma).")


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
    # rev12 (revisão rev12, item 10): no título, o nome do PROJETO de cada peça da marca (registro de nomes), nunca o do R01
    import re as _re, renomear as _RNb
    _nm = _RNb.lista(_RNb.nomes_de(marca))
    if _nm:
        conteudo = _re.sub(rf"{_re.escape(marca)} \([^,()]+(?:, ([^()]*))?\)", lambda m_: _RNb.N(_nm) + f" — MARCA {marca}" + (f" ({m_.group(1)})" if m_.group(1) else ""), conteudo, count=1)
    grampos_h = []
    if marca in ARR:                                                     # DEC-040: arranjo do dimensionamento
        a = ARR[marca]
        xy, d1, grampos, grampos_h = [tuple(p) for p in a["xy"]], a["d"], a["grampos"]["across_B"], a["grampos"]["across_H"]
        notas = [nota_arm(marca)] + list(notas[1:])
    return dict(marca=marca, qtd=qtd, B=B, H=H, L_CAL=1000, Z_TOP=ztop, al=[ztop + 1000 - 2500, 1000 + 1500], consolos=cons, xy=xy, grampos=list(grampos),
                grampos_h=list(grampos_h), d_est=D_EST, est=EST_STD, vistas=list(vistas), ip01=list(ip01), d1=d1, zoom=zoom, desenho=desenho, conteudo=conteudo,
                posicao=posicao, familia=familia, kp=KP_CEN, marcas=marcas, insertos=insertos, memoria=[], notas=notas)


PN5_TOPO = dict(nome="PN-5", d=20, L=600, emb=300, xy=[(sx * 115, sy * 100) for sx in (-1, 1) for sy in (-1, 1)], aco="CA-50 (NBR 7480)", anc="reta, por aderência (300 = 15 Ø)", rosca=0, pilha=[("NEO-3", 10)], viga="TS-01", destino="furo da ponta da TS-01, grauteado")   # x ao longo de H (A–C), y ao longo de B


import renomear as _RNg0


def dados_pc1():
    cons = [I120("B"), MEZ("A", Z_MEZ_ASS[0]), MEZ("C", Z_MEZ_ASS[0]), MEZ("A", Z_MEZ_ASS[1]), MEZ("C", Z_MEZ_ASS[1])]
    return base("PC-01", 1, 600, 400, Z_L2["C"], cons, bars_ret(600, 400, 4, 3), "ND-LET-PC01",
                "PILAR CENTRAL PC-01 (P8A, 40×60) — EIXO C, LINHA 2 — FÔRMA, ARMAÇÃO, INSERTOS E LOCAÇÃO",
                "POSIÇÃO: eixo C, linha 2 (P8A); 40 em x × 60 em y", "PILAR CENTRAL PC-01",
                [["PC-01", "P8A (C2)", 1, f"topo +{F(Z_L2['C'])}: {W_L2} direto (CA-L2 + 4 BR-M16); CP-I120 (B); 2 CP-MEZ (A, C)", "5 CE-1 + 1 CE-1L (B); 2 AL-2"]],
                [["PN-2", "Pino Ø25 CA-50 L=900 (350 no consolo) — CP-I120", 1, "face B"], ["PN-1", "Pino Ø20 CA-50 L=630 (230 no consolo) — CP-MEZ", 4, "faces A e C"], BRM20_INS,
                 ["NEO-2", "Neoprene 300×200×31 fretado (rev04)", 1, "CP-I120"], ["NEO-5F", "Neoprene 200×200 fretado c/ furo Ø30 (dente da VM)", 4, "CP-MEZ"], ["BA-1", "Bainha corrugada Ø50 horizontal (N11)", 4, "12 cm acima da VM"],
                 ["CE-1", "CE-1 380×330×12,5 + 4 pinos Ø16 + 2 N18 (CS-1, vista G)", 5, "face B, centrada, fiadas 0 a 4"],
                 ["CE-1L", "CE-1L 840×330×12,5 (asas de 220 além das faces) + 4 pinos Ø16 + 2 N18 — placas recortadas G-11/G-17 (DEC-044, PP06)", 1, "face B, centrada, fiada 5 (+6,25)"], ["AL-2", "Alça laço cordoalha Ø12,7", 2, "face A"]],
                ["Concreto C40; 10 Ø20 retos de ponta a ponta; estribos N2 Ø8 c/15 (c/10 nos 150 cm do topo e no cálice), ganchos 135°.", NOTA_CONS + NOTA_MEZ,
                 NOTA_W.format(z=F(Z_L2["C"])) + f" A cabeça passa {(Z_L2['C'] - Z_TOP_C) / 10:g} cm acima do topo da I120 (+{F(Z_TOP_C)}); CP-I120 na face B (+{F(Z_I120)}) para a ponta da V400; CP-MEZ nas faces A e C para as VM dos dois níveis. Apoio FIXO da W (furos redondos).",
                 "CE-1 (chapa de espera dos consoles CS-1) na face B para as placas da parede interna da linha 2 (vista G)."],
                ip01=[dict(face="B", z=IP_C, largo={5: 840})]) | dict(pinos_topo=BRM20_TOPO)


def dados_pc2():
    cons = [I120("B"), I120("D")]
    return base("PC-02", 1, 400, 400, Z_TOP_C, cons, bars_ret(400, 400, 3, 3), "ND-LET-PC02",
                "PILAR CENTRAL PC-02 (P11, 40×40) — EIXO C, LINHA 4 — FÔRMA, ARMAÇÃO, INSERTOS E LOCAÇÃO",
                "POSIÇÃO: eixo C, linha 4 (P11), parede dos portões", "PILAR CENTRAL PC-02",
                [["PC-02", "P11 (C4)", 1, "topo: 2 TS-01; CP-I120 (B, D)", "5 CE-1 + 1 CE-1L (B); 2 AL-2"]],
                [["PN-2", "Pino Ø25 CA-50 L=900 — CP-I120", 2, "faces B e D"], ["PN-5", "Pino Ø20 CA-50 L=600 (300 no pilar) — topo (TS-01)", 4, "topo, x ±115, y ±100"],
                 ["NEO-2", "Neoprene 300×200×31 fretado (rev04)", 2, "CP-I120"], ["NEO-3", "Neoprene 100×300×10 c/ 2 furos Ø30", 2, "topo (TS-01)"],
                 ["CE-1", "CE-1 380×330×12,5 + 4 pinos Ø16 + 2 N18 (CS-1, vista C)", 5, "face B, centrada, fiadas 0 a 4"],
                 ["CE-1L", "CE-1L 840×330×12,5 (asas de 220 além das faces) + 4 pinos Ø16 + 2 N18 — placas recortadas C-11/C-17 (DEC-044, PP06)", 1, "face B, centrada, fiada 5 (+6,25)"], ["AL-2", "Alça laço cordoalha Ø12,7", 2, "face A"]],
                ["Concreto C40; 8 Ø20 retos; estribos N2 Ø8 c/15 (c/10 nos 150 cm do topo e no cálice), ganchos 135°.", NOTA_CONS,
                 f"CP-I120 nas faces B (V406) e D (V407), assento +{F(Z_I120)}; TS-01 da linha 4 apoiadas no topo (topo horizontal em 2 níveis: +{F(Z_TOP_C)} lado A / +{F(Z_TOP_CD)} lado E), NEO-3 100×300 e 2 pinos PN-5 Ø20 por TS-01, grauteados nos tubos TB-3.",
                 "CE-1 (chapa de espera dos consoles CS-1) na face B para as placas da parede dos portões (vista C, fiadas até +7,50)."],
                ip01=[dict(face="B", z=IP_C, largo={5: 840})]) | dict(pinos_topo=PN5_TOPO)


def dados_pc3():
    # DEC-058 (24/10/2026, arranjo C): dois PC-03 40×40 (P13 em y 46,317 e P13B em y 62,833), fora das linhas da cobertura
    cons = [I120("B"), I120("D")]
    return base("PC-03", 2, 400, 400, Z_TOP_C, cons, bars_ret(400, 400, 4, 3), "ND-LET-PC03",
                "PILARES CENTRAIS PC-03 (P13, P13B, 40×40) — EIXO C — FÔRMA, ARMAÇÃO, INSERTOS E LOCAÇÃO",
                "POSIÇÃO: eixo C, y = 46,317 m (P13) e y = 62,833 m (P13B) — 3 vãos iguais de 16,517 m da linha 4 à linha 9 (DEC-058)", "PILAR CENTRAL PC-03",
                [["PC-03", _RNg0.N(_RNg0.pilar_em(X_EIXO["C"], 46.317)) + " (y 46,317)", 1, "CP-I120 (B, D)", "2 AL-2"], ["PC-03", _RNg0.N(_RNg0.pilar_em(X_EIXO["C"], 62.833)) + " (y 62,833)", 1, "CP-I120 (B, D)", "2 AL-2"]],
                [["PN-2", "Pino Ø25 CA-50 L=900 — CP-I120", 2, "faces B e D"], ["NEO-2", "Neoprene 300×200×31 fretado (rev04)", 2, "CP-I120"],
                 ["AL-2", "Alça laço cordoalha Ø12,7", 2, "face A"]],
                ["Concreto C40; 10 Ø16 retos (dimensionar_pilares_r05: uso 0,54); estribos N2 Ø6,3 c/15 (c/10 nos 150 cm do topo e no cálice), ganchos 135°.", NOTA_CONS,
                 f"CP-I120 nas faces B e D, assento +{F(Z_I120)}: P13 recebe V406 (B) e V405 (D); P13B recebe V405 (B) e V404 (D); sem TS-01 no topo (os dois ficam fora das linhas 5 a 8 — TS-01 no topo da I120)."])


def _pm(marca, nome, ap, eixo):
    cons = [MEZ("A", Z_MEZ_ASS[0]), MEZ("C", Z_MEZ_ASS[0]), MEZ("A", Z_MEZ_ASS[1]), MEZ("C", Z_MEZ_ASS[1])]
    zt = Z_L2[ap]
    return base(marca, 1, 600, 400, zt, cons, bars_ret(600, 400, 4, 3), f"ND-LET-{marca.replace('-', '')}",
                f"PILAR DO MEZANINO {marca} ({nome}, 40×60) — LINHA 2, EIXO {eixo} — FÔRMA, ARMAÇÃO, INSERTOS E LOCAÇÃO",
                f"POSIÇÃO: linha 2, eixo {eixo} ({nome}); 40 em x × 60 em y; topo +{F(zt)}", f"PILAR DO MEZANINO {marca}",
                [[marca, nome, 1, f"4 CP-MEZ (A, C); topo +{F(zt)}: {W_L2} direto (CA-L2 + 4 BR-M16)", "6 CE-1 (B); 2 AL-2"]],
                [["PN-1", "Pino Ø20 CA-50 L=630 (230 no consolo)", 4, "consolos CP-MEZ"], ["NEO-5F", "Neoprene 200×200 fretado c/ furo Ø30 (dente da VM)", 4, "CP-MEZ"], ["BA-1", "Bainha corrugada Ø50 horizontal (N11)", 4, "12 cm acima da VM"], BRM20_INS,
                 ["CE-1", "CE-1 380×330×12,5 + 4 pinos Ø16 + 2 N18 (CS-1, vista G)", 6, "face B, centrada"], ["AL-2", "Alça laço cordoalha Ø12,7", 2, "face A"]],
                ["Concreto C40; 10 Ø20 retos; estribos N2 Ø8 c/15 (c/10 nos 150 cm das pontas e no cálice), ganchos 135°.", NOTA_CONS + NOTA_MEZ,
                 f"CP-MEZ nas faces A e C: assentos +{F(Z_MEZ_ASS[0])} e +{F(Z_MEZ_ASS[1])} (VM retangular 30 × 75 com dente Gerber 45 × 40: fundo do consolo = fundo da viga); pino PN-1 Ø20 no TB-1 do dente; sem peça antigiro: a junta VM × pilar é concretada (fck ≥ 30) antes das lajes — DEC-039.",
                 NOTA_W.format(z=F(zt)) + f" Acima da laje de cima (+{F(Z_PISO_MM[1])}) a cabeça sobe {(zt - Z_PISO_MM[1]) / 10:g} cm. CE-1 na face B para as placas da parede interna da linha 2 (vista G)."],
                ip01=[dict(face="B", z=IP_C)]) | dict(pinos_topo=BRM20_TOPO)


def dados_pm():
    return _pm("PM-01", "P8", "B", "B")


def dados_pm2():
    return _pm("PM-02", "P8B", "D", "D")


# rev06 (DEC-024): cabeça dos pilares dos portões a 2 cm do fundo da TS-01 da linha 4, ligada à viga em y por 2 cantoneiras
# L 102×102×9,5 (faces x do pilar) — 4 comprimentos → 4 marcas (mesma fôrma e armação por seção)
IL1 = ["IL-1", "Inserto rosqueado M16 hef 100 (cantoneira CL-P)", 2, "faces B e D, 75 do topo"]
NOTA_LIG = ("A cabeça do pilar APOIA a TS-01A da linha 4. Na fábrica: topo liso e nivelado 2 cm "
            "abaixo do fundo da TS-01A (a viga sobe 3 % de A para E). Na obra, com a TS-01A montada e antes da cobertura: neoprene NEO-7 "
            "(dimensões na tabela de insertos) colado na cabeça e graute fluido sem retração (fck ≥ 40) injetado no espaço de ~10 mm entre o neoprene e o fundo "
            "da viga — a viga não desce no vão dos portões (fundo ≥ +7,50; no PG-01 7,497, dentro da tolerância de ±10 mm). Reação de cálculo "
            "na cabeça: {rd}. Em cada face lateral (B e D) continua a cantoneira L 102×102×9,5 L = 250 (CL-P) com 1 M16 8.8 no inserto IL-1 "
            "(furo oblongo vertical 18 × 50) e 2 M16 nos insertos do fundo da TS-01A: trava a parede dos portões em y. " + __import__("registro").portao_txt().capitalize() + ".")
IL2 = ["IL-2", "2 barras roscadas M16 8.8 L=200 (150 embutidos + grampo U Ø10) por cantoneira — CL-V (apoio da PV-1) e CT-V (trava do topo)", 6, "face B: 2 a +7,42 e 1 a +7,80 por cantoneira"]


def _fiadas_c(x):
    """rev06e: fiadas com console na parede dos portões (vista C do fechamento) para o pilar em x (m) — fonte: fechamento."""
    import fechamento as FCH
    ks = set()
    for (xc, z) in FCH.DADOS["C"][1]:
        s_, b_, n_ = min(FCH.VISTAS["C"]["pil"], key=lambda q: abs(q[0] - xc))
        if abs(s_ - x * 1000) < 50:
            ks.add(round((z - FCH.Z_NC) / FCH.H_PL))
    return [IP_C[k] if k < len(IP_C) else 1250 * k + 922 + 1000 for k in sorted(ks)]


_PJ = json.load(open("/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/portao_l4.json"))
_RD_PG = {k: f"{v['Nd_kN']:.0f} kN ({v['Nd_tf']:.1f} tf)".replace(".", ",") for k, v in _PJ["pilares"].items()}


import renomear as _RNg


def _pg(marca, nome, x, b, ztop, desenho, d1, est=None):
    # rev12 (27/10): geometria de geometria.PG_L4 — PG-02/PG-04 25×40 (40 em x, ao longo da parede), eixo deslocado 7,5 cm
    _, x, bxm, bym = _G.PG_L4[marca]
    bx_, by_ = round(bxm * 1000), round(bym * 1000)
    b = by_                                                            # lado ⊥ à parede (calço do CS-1, flambagem)
    ztop = round((ZF(x) - 0.02) * 100) * 10
    secao = f"{by_//10}×{bx_//10}"
    zce = _fiadas_c(x)
    P = base(marca, 1, by_, bx_, ztop, [], bars_ret(by_, bx_, 2, 2), desenho,
             f"PILAR DOS PORTÕES {marca} ({nome}, {secao}) — LINHA 4, x = {x:.3f} m — FÔRMA, ARMAÇÃO, INSERTOS E LOCAÇÃO".replace(".", ","),
             f"POSIÇÃO: linha 4, x = {x:.3f} m" + (f", eixo {_G.DY_PG[marca] * 100:.1f} cm fora da linha 4 para o lado das placas (y = {_G.Y_PG[marca]:.3f})" if _G.DY_PG[marca] else "") + f" ({nome}); topo +{ztop/1000:.2f} (2 cm abaixo da TS-01A: neoprene + graute — APOIA a viga, DEC-059)".replace(".", ","), "PILARES DA PAREDE DOS PORTÕES",
             [[mk_, _RNg.N(_RNg.pilar_em(_G.PG_L4[mk_][1], _G.Y_PG[mk_])) + (f" (x {f(_G.PG_L4[mk_][1], 3)})" if mk_ in ("PG-02", "PG-04") else ""), 1, f"{round(_G.PG_L4[mk_][3] * 100)}×{round(_G.PG_L4[mk_][2] * 100)}; sem consolo; topo +{f(ZF(_G.PG_L4[mk_][1]) - 0.02, 2)}", "CE-1 (B); 2 IL-1; 2 AL-2"]
              for mk_, nm_ in (("PG-01", "P9"), ("PG-02", "P10"), ("PG-04", "P10"), ("PG-03", "P12"))],
             [["CE-1", "CE-1 380×330×12,5 + 4 pinos Ø16 + 2 N18 (CS-1" + (", face no plano dos vizinhos 40 × 40" if b == 250 else "") + ")", len(zce), "face B, centrada"], IL1,
              ["NEO-7", f"Neoprene {_PJ['neoprene'][marca]['dim_mm'].replace(' ', '')} + graute fluido ~10 mm na obra (apoio da TS-01A), centrado na cabeça", 1, "cabeça"],
              ["AL-2", "Alça laço cordoalha Ø12,7", 2, "face A"]] + ([IL2] if marca in ("PG-03", "PG-04") else []),
             [("Concreto C40; 4 Ø20 retos (cantos); " if bx_ == by_ else "Concreto C40; 4 Ø16 retos (cantos); ") + "estribos c/15 (c/10 nos 150 cm das pontas e no cálice), ganchos 135°.",
              NOTA_LIG.format(rd=_RD_PG.get(marca, "-")) + (" Na face B, as barras IL-2 das cantoneiras CL-V/CT-V da placa PV-1 sobre o portão PG-04–PG-03 (ND-LET-PV01)." if marca in ("PG-03", "PG-04") else ""),
              "Pilar de fechamento da parede dos portões (vista C): recebe as placas, a folha do portão e o vento; apoiado em y na TS-01A pela cabeça e, depois do graute, apoio vertical da TS-01A (compressão e esbeltez verificadas na memória de cálculo)."],
             ip01=[dict(face="B", z=zce)], d1=d1, zoom=2.8 if b == 400 else 2.6)
    if marca in ("PG-02", "PG-04"):        # rev12 (DEC-092): locação decidida — sem pendência
        P["notas"] = list(P["notas"]) + [f"Seção 25 × 40 com o lado de 40 ao longo da parede; eixo em x = {f(x, 3)} m (5,00 m livres face a face do portão, conforme o arquitetônico) "
                                         f"e {f(_G.DY_PG[marca] * 100, 1)} cm fora da linha 4, para o lado das placas: a face fica no plano dos vizinhos 40 × 40, sem fresta até as placas. "
                                         f"NEO-7 centrado na cabeça (a reação da TS-01A passa no eixo do pilar); CL-P e insertos IT-P centrados na TS-01A, IL-1 no eixo do pilar."]
    if est:
        P |= dict(d_est=est)
    return P


def dados_pg1():
    return _pg("PG-01", "P9", None, None, None, "ND-LET-PG01", 20.0)


def dados_pg2():
    return _pg("PG-02", "P10a", None, None, None, "ND-LET-PG02", 16.0, 6.3)


def dados_pg3():
    return _pg("PG-03", "P12", None, None, None, "ND-LET-PG03", 20.0)


def dados_pg4():
    return _pg("PG-04", "P10b", None, None, None, "ND-LET-PG04", 16.0, 6.3)


# rev09 (DEC-045): pilares da escada (R01). Faces como nos PM/PC: A = −x (lado do eixo A), B = +y (lado do pavilhão), C = +x, D = −y.
INS_ESC = ["IE-1", "4 barras roscadas M16 8.8 L=200 (150 embutidos + grampo U Ø10) — chapa de topo da viga W 150 da escada", 4, ""]


def dados_pe1():
    cons = [MEZ("C", Z_MEZ_ASS[0])]
    return base("PE-01", 1, 400, 250, Z_PISO_MM[0], cons, bars_ret(400, 250, 3, 2), "ND-LET-PE01",
                "PILAR DA ESCADA PE-01 (P6, 25×40) — x 36,175, y 3,79 — FÔRMA, ARMAÇÃO, INSERTOS E LOCAÇÃO",
                "POSIÇÃO: x = 36,175 m, y = 3,79 m (P6 do R01, escada); 25 em x × 40 em y; topo +3,90", "PILARES DA ESCADA",
                [["PE-01", "P6 (escada)", 1, "1 CP-MEZ (C) +3,90", "IE-1 (C) +1,95; 2 AL-2"]],
                [["PN-1", "Pino Ø20 CA-50 L=630 (230 no consolo)", 1, "CP-MEZ"], ["NEO-5F", "Neoprene 200×200 fretado c/ furo Ø30 (dente da VM)", 1, "CP-MEZ"],
                 INS_ESC[:3] + ["face C, patamar +1,95 (viga de fundo VP-1)"], ["AL-2", "Alça laço cordoalha Ø12,7", 2, "face D"]],
                ["Concreto C40; armadura longitudinal pelo modelo global (arranjo_pilares.json); estribos c/15 (c/10 nos 150 cm das pontas e no cálice), ganchos 135°.", NOTA_CONS + NOTA_MEZ,
                 "Pilar da escada metálica (DEC-045): CP-MEZ na face C para a viga P6–P7 (VM-04) do +3,90; na mesma face, 4 barras roscadas IE-1 M16 para a chapa de topo da viga de fundo do patamar +1,95 (W 150 × 22,5, ND-LET-ES01).",
                 "Topo do pilar no +3,90 (topo da capa); acima disso a laje +7,30 é contínua."], d1=16.0, zoom=2.6)


def dados_pe2():
    cons = [MEZ("A", Z_MEZ_ASS[0])]
    return base("PE-02", 1, 400, 600, Z_PISO_MM[0], cons, bars_ret(400, 600, 3, 3), "ND-LET-PE02",
                "PILAR DA ESCADA PE-02 (P7, 40×60) — EIXO E, y 3,79 — FÔRMA, ARMAÇÃO, INSERTOS E LOCAÇÃO",
                "POSIÇÃO: eixo E, y = 3,79 m (P7 do R01, escada); 60 em x × 40 em y; topo +3,90; as placas da fachada E passam por fora", "PILARES DA ESCADA",
                [["PE-02", "P7 (escada)", 1, "1 CP-MEZ (A) +3,90", "IE-1 (A) +1,95; 2 AL-2"]],
                [["PN-1", "Pino Ø20 CA-50 L=630 (230 no consolo)", 1, "CP-MEZ"], ["NEO-5F", "Neoprene 200×200 fretado c/ furo Ø30 (dente da VM)", 1, "CP-MEZ"],
                 INS_ESC[:3] + ["face A, patamar +1,95 (viga de fundo VP-1)"], ["AL-2", "Alça laço cordoalha Ø12,7", 2, "face D"]],
                ["Concreto C40; armadura longitudinal pelo modelo global (arranjo_pilares.json); estribos c/15 (c/10 nos 150 cm das pontas e no cálice), ganchos 135°.", NOTA_CONS + NOTA_MEZ,
                 "Pilar da escada metálica (DEC-045): CP-MEZ na face A (interna) para a viga P6–P7 (VM-04) do +3,90; na mesma face, IE-1 para a viga de fundo do patamar +1,95. Face externa alinhada com os pilares do eixo E: as placas da fachada E passam por fora, sem console neste pilar.",
                 "Topo do pilar no +3,90 (topo da capa)."], d1=16.0, zoom=2.8)


def dados_pe3():
    cons = [MEZ("A", Z_MEZ_ASS[0]), MEZ("A", Z_MEZ_ASS[1]), MEZ("C", Z_MEZ_ASS[1])]
    return base("PE-03", 1, 400, 250, Z_L2["P6"], cons, bars_ret(400, 250, 3, 2), "ND-LET-PE03",
                "PILAR DA LINHA 2 PE-03 (P6, 25×40) — x 36,175, LINHA 2 — FÔRMA, ARMAÇÃO, INSERTOS E LOCAÇÃO",
                f"POSIÇÃO: x = 36,175 m, linha 2 (P6 do R01); 25 em x × 40 em y; topo +{F(Z_L2['P6'])}", "PILARES DA ESCADA",
                [["PE-03", "P6 (linha 2)", 1, f"3 CP-MEZ (A +3,90; A, C +7,30); topo +{F(Z_L2['P6'])}: {W_L2} direto (CA-L2 + 4 BR-M16)", "IE-1 (C) +3,90; 2 AL-2"]],
                [["PN-1", "Pino Ø20 CA-50 L=630 (230 no consolo)", 3, "CP-MEZ"], ["NEO-5F", "Neoprene 200×200 fretado c/ furo Ø30 (dente da VM)", 3, "CP-MEZ"],
                 ["BA-1", "Bainha corrugada Ø50 horizontal (N11)", 1, "+7,30, 12 cm acima da VM"], BRM20_INS,
                 INS_ESC[:3] + ["face C, chegada +3,90 (viga de fundo VP-1)"], ["AL-2", "Alça laço cordoalha Ø12,7", 2, "face D"]],
                ["Concreto C40; armadura longitudinal pelo modelo global (arranjo_pilares.json); estribos c/15 (c/10 nos 150 cm das pontas e no cálice), ganchos 135°.", NOTA_CONS + NOTA_MEZ,
                 "Linha 2 (DEC-045/048): no +3,90 só a viga D → P6 (VM-03, face A) — do P6 ao eixo E fica a abertura da escada, com a viga de fundo da chegada metálica (W 150) presa nas 4 IE-1 da face C; no +7,30 as vigas VM-03 (face A) e VM-04 (face C).",
                 NOTA_W.format(z=F(Z_L2["P6"])) + " A parede G passa por fora (face B 10 cm atrás do plano dos pilares 40 × 60 da linha 2), sem console neste pilar."],
                d1=16.0, zoom=2.6) | dict(pinos_topo=BRM20_TOPO)


DADOS = dict(pe1=dados_pe1, pe2=dados_pe2, pe3=dados_pe3, pc1=dados_pc1, pc2=dados_pc2, pc3=dados_pc3, pm=dados_pm, pm2=dados_pm2, pg1=dados_pg1, pg2=dados_pg2, pg3=dados_pg3, pg4=dados_pg4)



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
            v.chamada((x0 + (12.5 if sg > 0 else 0), yc / 2 + 150 * sg), (8 * sg, -9 * sg), f"CE-1 face {F_}: rente na lateral")   # rev08: texto por fora da fôrma
    if any(c["face"] == "A" for c in cons):
        v.ret(-150, -60, 300, 60, "OCULTA")
        v.chamada((-100, -30), (-16, -8), "consolos face A: caixão no fundo")
    v.texto((0, yc - 40), "C (placas)", "nota", "TOP_CENTER"); v.texto((0, 30), "A (interna)", "nota", "BOTTOM_CENTER")
    v.texto((xb - 30, yc / 2), "B", "nota", "MIDDLE_CENTER"); v.texto((-xb + 30, yc / 2), "D", "nota", "MIDDLE_CENTER")
    v.texto((0, -80), "FUNDO DA FÔRMA", "nota", "TOP_CENTER")
    if P.get("rec"):
        v.texto((0, -125), f"cabeça: calço {P['rec']['d'].get('A', 300) / 10:g} cm no fundo", "nota", "TOP_CENTER")


if __name__ == "__main__":
    for q in (sys.argv[1:] or list(DADOS)):
        prancha_pilar(DADOS[q]())
