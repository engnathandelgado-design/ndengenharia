"""ND-LET-NG01 — FOLHA DE ROSTO, ÍNDICE DAS FOLHAS E NOTAS GERAIS DO PROJETO EXECUTIVO (rev07, emissão executiva 21/10/2026).

Tudo lido dos JSON de cálculo (exemplos/letsara/*.json) e das tabelas das próprias folhas (*.tabelas.json): nada de valor
escrito à mão que já exista numa fonte. Grava também indice.json ({"ordem": [...], "titulos": {...}}) lido pelo unir_pranchas.py.
Sem tabela de verificação (regra do Nathan) e sem marca da ND nas imagens (o projeto é da fábrica).
Uso: python ng01.py"""
import json, os, sys, glob
sys.path.insert(0, "/home/claude/letsara/pranchas")
import pymupdf
from PIL import Image
from prancha_nd import Prancha, Vista, ALTURAS

PR = "/home/claude/letsara/pranchas/"
AQ = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"
J = lambda n: json.load(open(AQ + n + ".json", encoding="utf-8"))
f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")

LAJ, PLJ, NBR, LIG, VMJ, IJ = J("laje_alveolar"), J("placas"), J("nbr9062"), J("ligacoes"), J("vm_retangular"), J("i110_r01")
CONS = J("consolos")


def tab(folha, inicio):
    d = json.load(open(PR + folha + ".tabelas.json", encoding="utf-8"))
    for t in d["tabelas"]:
        if t["titulo"].upper().startswith(inicio.upper()):
            return t
    raise KeyError((folha, inicio))


def tab_any(folhas, inicio):
    """a mesma tabela pode estar em mais de uma folha da família (ex.: cordoalhas da TS-01 na folha 1 ou 2)."""
    for fl in folhas:
        try:
            return tab(fl, inicio)
        except (KeyError, FileNotFoundError):
            continue
    raise KeyError((folhas, inicio))


def quadro(folha, inicio="QUADRO"):
    d = {}
    for l in tab(folha, inicio)["linhas"]:
        for k in range(0, len(l) - 1, 2):
            if l[k]:
                d[l[k]] = l[k + 1]
    return d


# ------------------------------------------------------------------ índice (ordem combinada com o coordenador)
ORDEM = (["ND-LET-NG01", "ND-LET-PR01", "ND-LET-LOC01", "ND-LET-CG01", "ND-LET-CT01", "ND-LET-CT02", "ND-LET-CT03", "ND-LET-CT04",
          "ND-LET-MON01", "ND-LET-MON02", "ND-LET-MON03", "ND-LET-IC01"]                    # rev11: geral → localização → detalhe
         + [f"ND-LET-PL{k:02d}" for k in range(1, 13)] + [f"ND-LET-PF{k:02d}" for k in range(1, 7)]
         + [f"ND-LET-PC{k:02d}" for k in range(1, 4)] + ["ND-LET-PM01", "ND-LET-PM02"] + [f"ND-LET-PG{k:02d}" for k in range(1, 5)] + [f"ND-LET-PE{k:02d}" for k in range(1, 4)]
         + ["ND-LET-CS01"]
         + ["ND-LET-TS01-1", "ND-LET-TS01-2", "ND-LET-TS01-3", "ND-LET-I130", "ND-LET-VM01", "ND-LET-VB01", "ND-LET-LA01"]
         + [f"ND-LET-ES{k:02d}" for k in range(1, 6)]
         + ["ND-LET-CM01"] + [f"ND-LET-PP{k:02d}" for k in range(0, 7)] + [f"ND-LET-PP-{v}" for v in ("A", "B", "C", "D", "EF", "G", "HJ", "I")] + ["ND-LET-PV01"]
         + ["ND-LET-COB01", "ND-LET-COB07", "ND-LET-COB08", "ND-LET-COB02", "ND-LET-COB03", "ND-LET-COB04", "ND-LET-COB06", "ND-LET-COB05", "ND-LET-COB09", "ND-LET-MT01-1", "ND-LET-MT01-2", "ND-LET-EX01"])
PREVISTAS = {"ND-LET-NG01": "FOLHA DE ROSTO, ÍNDICE DAS FOLHAS E NOTAS GERAIS DO PROJETO EXECUTIVO",
             "ND-LET-PR01": "QUADRO DE PRODUÇÃO E CONCRETAGEM DAS PEÇAS — POR MARCA",
             "ND-LET-CT02": "CORTE DO MEZANINO — LAJES ALVEOLARES, VIGAS VM, CAPA E NÍVEIS",
             "ND-LET-CT03": "CORTE LONGITUDINAL DA ESTRUTURA",
             "ND-LET-MON03": "MONTAGEM DO FECHAMENTO LATERAL — PLACAS PROTENDIDAS"}


def _fmt_pdf(nome):
    arq = PR + nome + ".pdf"
    if not os.path.exists(arq):
        return ""
    r = pymupdf.open(arq)[0].rect
    w = round(max(r.width, r.height) * 25.4 / 72)
    return {1189: "A0", 841: "A1", 594: "A2", 420: "A3", 297: "A4"}.get(w, "ESP.")          # ESP.: largura A0, altura ajustada ao desenho


def _pag(n, ordem):
    """rev11: arquivo PDF unido (grupo) e página da folha dentro dele — mesma regra do unir_pranchas (ordem do índice)."""
    try:
        from unir_pranchas import GRUPOS
    except Exception:
        return ""
    for g, _, fl in GRUPOS:
        if n in fl:
            seq = [f for f in ordem if f in fl] + [f for f in fl if f not in ordem]
            return f"{g[:2]} p.{seq.index(n) + 1}"
    return ""


def indice():
    idx = {"ordem": ORDEM, "titulos": {}}
    try:
        antigo = json.load(open(PR + "indice.json", encoding="utf-8"))
        idx["titulos"].update(antigo.get("titulos", {}))
        if antigo.get("ordem"):                       # rev11: a ORDEM daqui manda; folhas extras do índice antigo vão para o fim
            idx["ordem"] = list(ORDEM) + [f for f in antigo["ordem"] if f not in ORDEM]
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    linhas = []
    for k, n in enumerate(idx["ordem"], 1):
        tj = PR + n + ".tabelas.json"
        if os.path.exists(tj):
            dd = json.load(open(tj, encoding="utf-8"))["dados"]
            tit, rev = dd.get("conteudo", ""), dd.get("rev", "")
        else:
            tit, rev = PREVISTAS.get(n, idx["titulos"].get(n, "")), ""
        if n in PREVISTAS and n in ("ND-LET-NG01",):
            tit = PREVISTAS[n]
        idx["titulos"][n] = tit
        linhas.append([k, n.replace("ND-LET-", ""), tit, _fmt_pdf(n) or ("A0" if n == "ND-LET-NG01" else "—"), rev, _pag(n, idx["ordem"])])
    json.dump(idx, open(PR + "indice.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return linhas


def corta(png, saida, borda=30):
    im = Image.open(png).convert("RGB")
    from PIL import ImageOps
    bb = ImageOps.invert(im).getbbox()
    im.crop((max(bb[0] - borda, 0), max(bb[1] - borda, 0), min(bb[2] + borda, im.width), min(bb[3] + borda, im.height))).save(saida)
    return saida


# ------------------------------------------------------------------ dados das notas (das fontes)
TSQ = quadro("ND-LET-TS01-1")
I130Q = quadro("ND-LET-I130")
VMQ = quadro("ND-LET-VM01", "QUADRO DA PEÇA")
VBQ = quadro("ND-LET-VB01")
LAQ = quadro("ND-LET-LA01", "QUADRO DAS LAJES")
PLQ = quadro("ND-LET-PL01")
TS_CORD = tab_any(["ND-LET-TS01-1", "ND-LET-TS01-2"], "CORDOALHAS")["linhas"]
VM_CORD = tab("ND-LET-VM01", "CORDOALHAS")["linhas"]
P_ = PLJ["protensao"]
ncord = lambda ls: sum(int(l[2]) for l in ls)
CC = LIG["cargas_cob"]
CL = LAJ["cargas"]
TR = NBR["transitorias"]
FOLG = {d["peca"].split(" —")[0]: d for d in NBR["folgas"]}

MATERIAIS = [
    ["Pilares PL, PF, PC, PM, PG", PLQ["CONCRETO"], "—", "25", "armado (CA-50)", PLQ["COBRIMENTO"].replace(" (CAA II)", ""), "II"],
    ["Viga TS-01 (I90 de cobertura)", "C50", TSQ["CONCRETO"].split("fckj ")[1], TSQ["CONCRETO"].split("fckj ")[1],
     f"{ncord(TS_CORD)} Ø12,7 CP-190 RB — {TS_CORD[0][4]} kN", "3,0", "II"],
    ["Vigas I130 (V404, V405, V406, V407)", "C50", f"{IJ['V406']['arranjo']['fckj']:.0f}", f"{IJ['V406']['arranjo']['fckj']:.0f}",
     " / ".join(f"{k} {v['arranjo']['n_cord']}" for k, v in IJ.items()) + f" Ø12,7 — {f(IJ['V406']['arranjo']['F_macaco_kN'])} kN", "3,0", "II"],
    ["Vigas do mezanino VM-01 a VM-04 (30 × 75)", f"C{VMJ['premissas']['fck']:.0f}", f"{VMJ['premissas']['fckj']:.0f}", f"{VMJ['premissas']['fcj_icamento']:.0f}",
     f"{ncord(VM_CORD)} Ø12,7 CP-190 RB — {VM_CORD[0][4]} kN", "2,5 estribo / 3,0 cord.", "II"],
    ["Vigas de borda VB-01 a VB-08", VBQ["CONCRETO"], "—", "25", "armado (CA-50)", VBQ["COBRIMENTO"].replace(" (CAA II)", ""), "II"],
    ["Lajes alveolares LA (h20)", "C50", f"{LAJ['fckj']:.0f}", f"{LAJ['icamento']['fcj_icamento']:.0f}",
     f"{LAJ['n_cord']} Ø12,7 CP-190 RB — {tab('ND-LET-LA01', 'PROTENSÃO')['linhas'][0][5]} kN", f"eixo a {LAJ['incendio']['c1_mm'] / 10:g}", "I (interno)"],
    ["Placas de fechamento PP (125 × 10)", f"C{PLJ['secao']['fck']:.0f}", f"{PLJ['secao']['fckj']:.0f}", f"{PLJ['secao']['fckj']:.0f}",
     f"{P_['n']} fios Ø{P_['diam_mm']:g} CP-175 RB — {f(P_['F_macaco_kN'])} kN", f((P_['eixo_face_mm'] - P_['diam_mm'] / 2) / 10), "II"],
    ["Capa e 2º estágio (obra)", f"C{VMJ['premissas']['fck_2estagio']:.0f}", "—", "—", "tela Q138 + negativas N11/N12", "2,5 (tela a 2,5 do topo)", "I"],
    ["Graute de cálices, juntas e bainhas", "fck ≥ 30 MPa", "—", "—", "não retrátil, fluido", "—", "—"],
]

NORMAS = ("NBR 9062:2017 (projeto e execução de estruturas de concreto pré-moldado) — base do projeto; NBR 6118:2023 (concreto); NBR 14861:2022 (lajes alveolares); "
          "NBR 6123:1988 (vento); NBR 6120:2019 (ações); NBR 8681:2003 (ações e segurança); NBR 8800:2008 e NBR 14762:2010 (aço e perfis formados a frio); "
          "NBR 7480 (barras CA-50/CA-60); NBR 7482 (fios de protensão); NBR 7483 (cordoalhas); NBR 12655 (controle do concreto); NBR 6323 (galvanização a fogo).")

N_GERAIS = [
    "Estrutura pré-moldada do pavilhão Letsara: pilares engastados nos cálices, vigas articuladas (TS-01 de cobertura, I130 centrais, VB de borda, VM do mezanino), "
    "lajes alveolares com capa nos pisos +3,90 (depósito, 5,0 kN/m²) e +7,30 (laje de cobertura do bloco (acesso apenas para manutenção, NBR 6120:2019 Tab. 10): sobrecarga 1,0 + regularização/impermeabilização 1,7 kN/m²), escada metálica do térreo ao +3,90 (ND-LET-ES01), cobertura da linha 2 metálica: W 200 × 15,0 nos pilares e em montantes W 150 × 13,0 sobre as VM do +7,30 (ND-LET-COB05), cobertura metálica Isoeste (telha zipada dupla com lã de rocha) sobre terças Z escondida na platibanda (+10,00) e fechamento lateral em placas protendidas 125 × 10 por fora dos pilares.",
    f"Classificação: {NBR['classificacao']['tipo']}. Coeficientes adotados: γc {f(NBR['classificacao']['gama_c'])}, γs {f(NBR['classificacao']['gama_s'], 2)}, "
    f"γn {f(NBR['classificacao']['gama_n_permanente'])} (consolos com permanente preponderante) e {f(NBR['classificacao']['gama_n_outros'])} (demais) — NBR 9062:2017 7.3.1 e 8.1.",
    "Estabilidade global: pilares engastados na fundação, cobertura, terças, correntes e contraventamento em X junto aos oitões e o mezanino como diafragma rígido, num modelo global único "
    "(OpenSeesPy, P-Δ, pilares com 0,4 Eci·Ic — NBR 9062:2017 Anexo A), com desaprumo H/400 (5.2.3).",
    "Cotas de concreto em cm, peças metálicas em mm, níveis em m. Não medir no desenho. Em divergência entre folhas, vale a folha da peça (marca); consultar o projetista antes de executar.",
    "Fundações (blocos, cálices, estacas) em projeto próprio, com as cargas da ND-LET-CG01 (tf, tf·m) e o embutimento de 1,00 m dos pilares (NBR 9062:2017 7.7).",
]

N_CARGAS = [
    f"Cobertura (kN/m²): telha zipada {f(CC['zipada_050'], 3)}, lã de rocha {f(CC['la_rocha_fsr32_40'], 3)}, telha TP-40 {f(CC['tp40_065'], 3)}, cartolas e fixações {f(CC['cartola_clipes_fixacoes'], 3)}, "
    f"painéis solares {f(CC['paineis_solares'], 2)}, instalações {f(CC['instalacoes'], 2)}; sobrecarga {f(CC['sobrecarga'], 2)} (NBR 6120). Calha cheia na linha A.",
    f"Mezanino (kN/m²): laje alveolar {f(CL['g1'])}, capa e rejunte {f(CL['capa_rejunte'], 2)}, revestimento {f(CL['revestimento'])}, sobrecarga {f(CL['sobrecarga'])} (escritório); "
    f"montagem sem escoramento com {f(CL['montagem'])} kN/m² sobre a capa fresca.",
    "Vento (NBR 6123): V0 = 45 m/s, S1 = 1,00, S2 categoria III classe C, S3 = 0,95; q(10 m) = 0,874 kN/m²; 4 direções, Cpi máximo e mínimo e excentricidade ±e (6.6).",
    "Placas de fechamento: dimensionadas só pelo peso próprio, cada placa independente nos seus 2 consoles (decisão do responsável técnico, DEC-035); as fixações (consoles, nichos, chapas de espera, travas) "
    "foram calculadas com o vento.",
    "Não há ponte rolante. Combinações ELU (NBR 8681): 1,3 G + 1,4 V + 0,7·1,4 Q; 1,0 G + 1,4 V (sucção); 1,3 G + 1,4 Q. ELS pela NBR 6118 e NBR 9062:2017 5.4 (flechas Tab. 8 e 9; deslocamento horizontal Tab. 7).",
]

N_MATERIAIS = [
    "Aço passivo CA-50 (NBR 7480); telas soldadas CA-60 (Q92 nas pontas das placas, Q138 na capa). Barras até Ø20; dobramento pela NBR 6118:2023 9.4.6; ganchos de estribo 135° com 10Ø; sem emenda de barra nas peças.",
    "Protensão: cordoalhas CP-190 RB Ø12,7 (NBR 7483) nas vigas e lajes; fios entalhados CP-175 RB Ø6 (NBR 7482) nas placas. Força no macaco, posição de cada cabo, isolamentos e alongamento em cada folha.",
    "Alças de içamento: laço de cordoalha Ø12,7 não engraxada, sem separar os fios (NBR 9062:2017 5.3.3) — proibido CA-25, CA-50 ou CA-60 em alça. Furo de içamento FI-1 dos pilares: tubo Ø60,3 × 3 perdido.",
    "Chaparia e insertos: ASTM A36 (chapas, pinos, cantoneiras) e A572-50 (consoles CS-1 e nichos NC-1), galvanizados a fogo depois da solda de fábrica (NBR 6323, ≥ 85 µm); solda na obra só nos CS-1 laterais "
    "(filete E70XX, inspeção visual 100 %, galvanização a frio). Parafusos 8.8 zincados ou galvanizados; nenhuma ligação soldada na cobertura.",
    "Neoprenes (NEO-1 a NEO-6) e fitas de apoio: dimensões e furos conforme a folha de cada apoio (NBR 9062:2017 7.2.1.6). Graute não retrátil fck ≥ 30 MPa nos cálices, juntas e bainhas.",
]

N_PRODUCAO = [
    "Corpos de prova curados junto com a peça: liberar a protensão, desformar e içar só com o fcj da tabela de materiais (NBR 9062:2017 8.2.2.2 — mínimo 21 MPa protendido, 15 MPa armado). "
    "Transporte e montagem com fcj ≥ o de desforma.",
    "Liberação da protensão sempre gradual (macaco) e simétrica; liberação brusca proibida. Cordoalhas das placas e pilares simétricas nas faces (a peça não pode empenar).",
    f"Tolerâncias de fabricação: {NBR['tolerancias']['fabricacao']}",
    "Cobrimentos garantidos com espaçadores (plástico ou argamassa) a cada 1,0 m no máximo; insertos e chapas de espera presos à fôrma com gabarito (CE-1 ±5 mm); conferir cada peça contra a folha antes de concretar (check-list de pré-concretagem).",
    "Superfícies de ligação com o 2º estágio e a capa (topo das VM, chavetas das lajes) rugosas e limpas; saturar antes de concretar na obra. Marcar em cada peça: marca, data da concretagem e peso.",
    f"Içamento e manuseio (NBR 9062:2017 5.3.2): carga equivalente com βa {f(TR['beta_a']['saque_montagem'])} no saque, manuseio e montagem; alças com βa {f(TR['beta_a']['alcas'])}. "
    "Pilares: tirar da fôrma pelas 2 alças AL-2, verticalizar e montar pelo furo FI-1. Vigas: pelas alças da folha. Lajes: garra mecânica nas 2 pontas. Placas: desforma, giro e montagem de pé pelos mesmos 4 insertos IZ-1 de uma face, com balancim duplo (ND-LET-MON03 det. 2a–2c e ND-LET-IC01).",
    f"Estocagem e transporte: calços alinhados nos pontos indicados em cada folha ({TR['estoque']}); pilares deitados em 2 apoios a 0,21 L sem apoiar em consolos; placas EM PÉ em cavalete; lajes em pilhas de até 8 painéis.",
]

N_MONTAGEM = [
    f"Tolerâncias de montagem: {NBR['tolerancias']['montagem']}",
    "Folgas de projeto: TS-01 25 mm no pilar lateral e 19 mm no centro; I130 e VB 25 mm; VM 30 mm; placas 20 mm no comprimento (junta vertical no eixo do pilar) e 5 mm na altura. Apoios mínimos em cada folha.",
    "Sequência geral (ND-LET-MON03, 11 etapas): pilares de todas as linhas, aprumados e travados com cunhas, cálice grauteado no mesmo dia (vigas só 24 h depois, graute ≥ 15 MPa) → I130 V407/V406/V405/V404 → parede C (linha 4) → TS-01 da linha 8 para a 3 e VB-05 a VB-08 (guindaste de ré, sempre no vão sem cobertura) → cobertura dos vãos 3–4 a 8–9 → mezanino +3,90 e depois +7,30 (VM, pontas concretadas dos dois lados e fcj ≥ 20 MPa, lajes, 2º estágio e capa; carregar com fck ≥ 20 MPa — ND-LET-MON02) → parede G (linha 2) → W 200 × 15,0 da linha 2 (na cabeça dos pilares e nos montantes W 150 × 13,0 sobre as VM do +7,30, presilhas, mãos-francesas), VB-01 a VB-04 e terças dos vãos 1–2 e 2–3 → escada metálica → placas externas pelo lado de fora → telhas, rufos e calhas dos vãos 1–3.",
    "Exceções da ordem pilares → vigas → cobertura → mezanino → fechamento, por geometria: a cobertura dos vãos 1–3 só depois do mezanino (a laje de 9,55 m não passa entre a VB da linha 1 e a W 200 da linha 2) e as paredes internas C e G antes da viga de cobertura da própria linha (o balancim não passa entre a viga e as terças).",
    "Plano de rigging (NBR 9062:2017 3.17) e escolha do guindaste por conta da montadora, com os pesos de cada peça (ND-LET-PR01) e o raio de cada posição.",
    f"Incêndio: {NBR['incendio_cobrimentos']['TRRF']}. Placas 10 cm: {NBR['incendio_cobrimentos']['placas']}. Laje: {LAJ['incendio']['nota']}.",
]

PEND = [
    "Local da obra a confirmar no carimbo.",
    "TRRF exigido pelo Corpo de Bombeiros (ocupação e área) a confirmar.",
    "Inserto IZ-1 das placas, pino do furo FI-1 e alças: modelo e capacidade pelo catálogo do fornecedor da fábrica.",
    "Cobrimento 2,0 cm dos fios das placas exige controle de pré-fabricado (NBR 9062:2017 12.1.2) — confirmar com a fábrica.",
    "Lajes alveolares: protensão válida para a seção desenhada; se o fabricante extrudar outra seção, refazer a verificação.",
]


def gerar():
    import prancha_nd as _PN
    _PN.ALTURAS["nota"] = 2.5          # folha de rosto: texto maior (só nesta folha)
    lin_idx = indice()
    pr = Prancha("A0", dict(cliente="MARQUES ENGENHARIA E CONSTRUÇÕES", obra="LETSARA — PAVILHÃO COM MEZANINO", local="A CONFIRMAR",
                            conteudo=PREVISTAS["ND-LET-NG01"], desenho="ND-LET-NG01", folha="01/01", rev="06"))
    pr.revisao("06", "21/10/2026", "FOLHA DE ROSTO E NOTAS GERAIS")
    pr.revisao("", "24/10/2026", "ISOMÉTRICOS DO MODELO REV09 (VÃO DA ESCADA E ESCADA METÁLICA); LINHA 2 SEM MONTANTES (DEC-050)")
    x0, y0, x1, y1 = pr.quadro
    # ---------- título
    yt = y1 - 14
    pr.texto(x0 + 10, yt, "LETSARA — PAVILHÃO PRÉ-MOLDADO COM MEZANINO", 9.0, "TITULO")
    pr.texto(x0 + 10, yt - 11, "PROJETO EXECUTIVO DA ESTRUTURA — PRODUÇÃO, ARMAÇÃO, CONCRETAGEM E MONTAGEM", 5.0, "TITULO")
    pr.texto(x0 + 10, yt - 19, "Cliente: MARQUES ENGENHARIA E CONSTRUÇÕES · pavilhão 39,50 × 79,35 m · pilares, vigas, lajes alveolares, placas e cobertura metálica", 3.0)
    # ---------- índice (coluna 1)
    xi = x0 + 10
    y = pr.tabela(xi, yt - 28, f"ÍNDICE DAS FOLHAS — {len(lin_idx)} FOLHAS", ["Nº", "DESENHO", "CONTEÚDO", "FORM.", "REV.", "PDF/PÁG."],
                  [[a, b, (c if len(c) <= 88 else c[:85] + "..."), d, e, pg] for a, b, c, d, e, pg in lin_idx], [9, 20, 184, 12, 10, 16], h_lin=4.6)
    pr.texto(xi, y - 10, "PDF/PÁG. = nº do arquivo unido da entrega (00 gerais, 01 pilares, 02 vigas, 03 lajes e fechamento, 04 cobertura, 05 execução) e página dentro dele.", "min")
    pr.texto(xi, y - 5, "FORM. ESP. = largura do A0 com a altura ajustada ao desenho (fôrma em cima, armação embaixo). Folhas sem revisão: em emissão.", "min")
    pr.blocos_livres.append((xi, y - 11, xi + 251, y - 2, "nota do índice"))
    # ---------- imagens (coluna 2)
    S = "/home/claude/letsara/pranchas/img_ng01/"
    xa, xb = x0 + 275, x0 + 590
    pr.imagem(xa, yt - 205, xb, yt - 28, S + "ng01_estrutura_c.png", "ESTRUTURA — ISOMÉTRICO", "pilares, vigas, mezanino e cobertura metálica (sem telhas e sem placas)")
    pr.imagem(xa, yt - 420, xb, yt - 243, S + "ng01_completa_c.png", "OBRA COMPLETA — ISOMÉTRICO", "com as placas de fechamento, telhas e rufos")
    # ---------- materiais (coluna 2, abaixo)
    ym = pr.tabela(xa, yt - 445, "MATERIAIS E RESISTÊNCIAS POR PEÇA (MPa, cm)", ["PEÇA", "CONCRETO", "fcj LIBERAÇÃO", "fcj DESFORMA/IÇAMENTO", "PROTENSÃO (força no macaco por cabo)", "COBRIMENTO", "CAA"],
                   MATERIAIS, [64, 20, 26, 40, 96, 42, 18], h_lin=5.2)
    yn = pr.notas(xa, ym - 4, [NORMAS], 306, "NORMAS")
    # ---------- rev08: nomenclatura das peças × projeto do cliente (R01)
    import renomear as RN
    pil = [p for p in RN._D["pecas"] if p["tipo"] == "pilar"]
    por_lado = {}
    for p in pil:
        base = p["ref_R01"].split()[0]
        por_lado.setdefault(base if base in ("P1", "P2") and " L" in p["ref_R01"] else p["ref_R01"], []).append(p["nome"])
    lin_n = [[RN.novo(RN.lista(v)), RN.novo(f"{k} L1 a L9 (pilares laterais do eixo {'A' if k == 'P1' else 'E'})" if k in ("P1", "P2") else k)]
             for k, v in sorted(por_lado.items(), key=lambda kv: int(kv[1][0][1:]))]
    grp = lambda *mks: RN.lista([n for m in mks for n in RN.nomes_de(m)])
    lin_n += [[RN.novo(grp("V407")), RN.novo("V407 (I130, linhas 2–4)")], [RN.novo(grp("V406")), RN.novo("V406 (I130, linha 4 → PC-03 y 46,317)")],
              [RN.novo(grp("V405")), RN.novo("V405 (I130, PC-03 → PC-03, y 46,317 → 62,833)")], [RN.novo(grp("V404")), RN.novo("V404 (I130, PC-03 y 62,833 → linha 9)")],
              [RN.novo(grp("VM-01", "VM-02", "VM-03", "VM-04")), RN.novo("vigas do mezanino (+3,90 e +7,30)")],
              [RN.novo(grp(*[f"VB-0{k}" for k in range(1, 9)])), RN.novo("vigas de borda das fachadas 1 e 9")],
              [RN.novo(grp("TS-01", "TS-01A", "TS-01B")), RN.novo("vigas de cobertura das linhas 3 a 8")]]
    pr.tabela(xa, yn - 6, "NOMENCLATURA — NOME DA PEÇA × PROJETO DO CLIENTE (R01)", ["NOME (este projeto)", "NO R01 / DESCRIÇÃO"], lin_n, [130, 176], h_lin=4.8)
    # ---------- notas (colunas 3 e 4)
    xn1, xn2 = x0 + 600, x0 + 880
    y = pr.notas(xn1, yt + 6, N_GERAIS, 270, "NOTAS GERAIS")
    y = pr.notas(xn1, y - 3, N_CARGAS, 270, "CARGAS CONSIDERADAS")
    y = pr.notas(xn1, y - 3, N_MATERIAIS, 270, "MATERIAIS")
    import pr01 as P01                                  # mesmos totais do quadro de produção (ND-LET-PR01)
    conc, fam, bit, prot = P01.totais()
    fm = lambda v, d=1: f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    lf = [[F, fam[F]["qt"], fm(fam[F]["v"]), fm(fam[F]["p"]), fm(fam[F]["kg"], 0)] for F in P01.FAMS]
    lf.append(["TOTAL", sum(t["qt"] for t in fam.values()), fm(sum(t["v"] for t in fam.values())), fm(sum(t["p"] for t in fam.values())), fm(sum(t["kg"] for t in fam.values()), 0)])
    y = pr.tabela(xn1, y - 6, "RESUMO DAS PEÇAS PRÉ-MOLDADAS (detalhe por marca: ND-LET-PR01)", ["FAMÍLIA", "PEÇAS", "CONCRETO (m³)", "PESO (t)", "AÇO CA-50 (kg)"],
                  lf, [80, 30, 50, 50, 60], h_lin=5.2, destaque_ultima=True)
    lp = [[c, fm(v)] for c, v in sorted(conc.items())] + [[k, f"{fm(kg, 0)} kg ({fm(m, 0)} m)"] for k, (m, kg) in prot.items()]
    y = pr.tabela(xn1, y - 6, "CONCRETO POR CLASSE (m³) E PROTENSÃO", ["ITEM", "QUANTIDADE"], lp, [120, 150], h_lin=5.2)
    # rev09b (24/10, pedido do Nathan): isométrico do mezanino com a laje +7,30 e a cobertura cortadas — mostra o vão da escada no +3,90
    y_fim = max(y0 + 128, y - 10 - 175)
    pr.imagem(xn1, y_fim, xn1 + 270, y - 10, S + "ng01_mezanino_c.png", "MEZANINO +3,90 — ISOMÉTRICO",
              "laje +7,30 e cobertura cortadas: vão da escada (P6, P7, linha 2) e escada metálica")
    y = pr.notas(xn2, yt + 6, N_PRODUCAO, 270, "PRODUÇÃO, CONCRETAGEM E MANUSEIO")
    y = pr.notas(xn2, y - 3, N_MONTAGEM, 270, "MONTAGEM")
    y = pr.notas(xn2, y - 3, PEND, 270, "A CONFIRMAR ANTES DA PRODUÇÃO")
    simbologia(pr, xn1, y_simb(pr))
    return pr


def y_simb(pr):
    return pr.quadro[1] + 120


def simbologia(pr, x, yt):
    """legenda gráfica do jogo (mesmas camadas das folhas)."""
    pr.texto(x, yt - ALTURAS["sub"], "SIMBOLOGIA", "sub", "TITULO")
    v = Vista(pr, "SIMB", (x, yt - 14), 1.0)          # não registrada: sem título/escala de vista
    itens = []
    y = 0
    # eixo com bolha
    v.linha((0, y), (40, y), "EIXO"); v.circulo((46, y), 4, "INDICACAO"); v.texto((46, y), "3", "nota", "MIDDLE_CENTER", "TITULO"); itens.append((y, "eixo da obra (traço-ponto) e bolha do eixo"))
    y -= 12
    v.poli([(14, y - 2), (18, y + 2), (10, y + 2)], "INDICACAO", True); v.linha((0, y + 2), (40, y + 2), "INDICACAO"); v.texto((20, y + 3), "+7,195", "min"); itens.append((y, "nível em m (assento, topo, piso)"))
    y -= 12
    v.linha((0, y), (8, y), "INDICACAO"); v.linha((32, y), (40, y), "INDICACAO"); v.texto((-2, y), "A", "nota", "MIDDLE_RIGHT", "TITULO"); v.texto((42, y), "A", "nota", "MIDDLE_LEFT", "TITULO"); itens.append((y, "marcador de corte"))
    y -= 12
    v.ret(0, y - 3, 40, 6, "CORTADO"); v.hachura([(0, y - 3), (40, y - 3), (40, y + 3), (0, y + 3)], "ANSI31", 0.25, "HACHURA"); itens.append((y, "chapa / perfil metálico (hachurado)"))
    y -= 12
    v.linha((0, y), (40, y), "ARMADURA"); itens.append((y, "armadura passiva longitudinal (verde)"))
    y -= 9
    v.linha((0, y), (40, y), "ARM_TRANSV"); itens.append((y, "estribos, grampos, costura"))
    y -= 9
    v.linha((0, y), (40, y), "ARM_PROT"); v.circulo((48, y), 2, "ARM_PROT"); itens.append((y, "protensão: cordoalha/fio (círculo vazado na seção)"))
    y -= 9
    v.linha((0, y), (40, y), "OCULTA"); itens.append((y, "aresta oculta"))
    for yy, t in itens:
        v.texto((60, yy), t, "nota", "MIDDLE_LEFT")
    pr.blocos_livres.append((x, yt - 14 + y - 5, x + 260, yt, "SIMBOLOGIA"))


if __name__ == "__main__":
    os.makedirs(PR + "img_ng01", exist_ok=True)
    SC = sys.argv[1] if len(sys.argv) > 1 else PR + "img_ng01/"
    for n in ("ng01_estrutura", "ng01_completa", "ng01_mezanino"):
        if os.path.exists(SC + n + ".png"):
            corta(SC + n + ".png", PR + "img_ng01/" + n + "_c.png")
    pr = gerar()
    av = pr.salvar(PR + "ND-LET-NG01")
    for a in av:
        print(a)
    print(len([a for a in av if a[0] == "ERRO"]), "erros,", len(av), "avisos")
