"""Regera o jogo executivo completo da Letsara na ordem certa e resume erros/avisos por folha (AVISOS_LOG).
Uso: python gerar_tudo.py  → log em gerar_tudo.jsonl; falha se alguma folha do índice tiver erro ou aviso.
Em etapas (rev12, proteção contra reinício do container): python gerar_tudo.py --reset (limpa logs e travas);
python gerar_tudo.py --etapa 1 … --etapa N (ORDEM dividida em ETAPAS, acumula o log; --sem-cc pula a conferência);
python gerar_tudo.py --fim (só o resumo + conferência cruzada).
INCREMENTAL (27/10/2026, padrão): cada folha roda por rodar_rastreado.py, que grava em manifestos/<script>.json o que ela
leu e escreveu. Na próxima vez a folha é PULADA se o script, todos os arquivos lidos e as pastas listadas estão iguais e
as saídas existem (os avisos que ela gravou no log são repetidos). Mudou o P21 → só refazem as folhas que leem o que
mudou. --tudo força regenerar tudo. Antes de qualquer folha roda o gate de lançamento (verificar_lancamento.py); com
achado, para (--sem-lancamento pula, só para depuração). No fim grava alteradas.json (folhas cujo PDF mudou) para a
revisão por diferença. alteradas.json compara com emissao_revisada.json (gravado com --emissao ao mandar a revisão),
não com a última execução.
"""
import hashlib, json, os, subprocess, sys, time
PR = "/home/claude/letsara/pranchas/"
MAN = PR + "manifestos/"
EX = "/home/claude/ndengenharia/nd_estruturas/exemplos/letsara/"


def _h(p):
    try:
        return hashlib.sha1(open(p, "rb").read()).hexdigest()
    except OSError:
        return None


def _hp(p):
    try:
        return hashlib.sha1("\n".join(sorted(os.listdir(p))).encode()).hexdigest()
    except OSError:
        return None


def _h_pdf(p):
    """hash do PDF sem as datas e o /ID (o mesmo desenho gerado de novo dá o mesmo hash)."""
    import re
    try:
        b = open(p, "rb").read()
    except OSError:
        return None
    b = re.sub(rb"/(CreationDate|ModDate)\s*\([^)]*\)", b"", b)
    return hashlib.sha1(re.sub(rb"/ID\s*\[[^\]]*\]", b"", b)).hexdigest()


def pode_pular(s):
    return pode_pular_em(PR, s, MAN + s + ".json")


def pode_pular_em(pasta, s, f):
    """True se nada que o script leu mudou desde a última geração bem-sucedida."""
    if not os.path.exists(f):
        return False, "sem manifesto"
    m = json.load(open(f, encoding="utf-8"))
    if m["codigo"] != 0 or m["subprocesso"]:
        return False, "última geração falhou" if m["codigo"] else "chama subprocesso"
    if _h(pasta + s) != m["hash_script"]:
        return False, "script mudou"
    for p, h in m["entradas"].items():
        if _h(p) != h:
            return False, "mudou " + os.path.basename(p)
    for p, h in m["pastas"].items():
        if _hp(p) != h:
            return False, "pasta mudou " + os.path.basename(p)
    for p in m["saidas"]:
        if not os.path.exists(p):
            return False, "saída ausente " + os.path.basename(p)
    return True, m


def repetir_acrescimos(m):
    for p, txt in m.get("acrescimos", {}).items():
        if txt:
            with open(p, "a", encoding="utf-8") as f:
                f.write(txt)
LOG = PR + "gerar_tudo.jsonl"
ORDEM = ["consolos_marcas.py", "pilares_familia.py", "pilar_generico.py", "cs01.py", "ex01.py", "ts01_chaparia.py", "vigas_exec.py", "cob01.py", "cob02.py", "cob03.py", "cob04.py", "cob_l2.py", "cob06.py", "cob07.py", "cob08.py", "cob09.py", "mt01.py", "ts01_armacao.py",
         "lajes_placas.py", "es01.py", "es02.py", "es03.py", "es04.py", "fechamento.py", "pp01.py", "pp02.py", "pp03.py", "pp04.py", "pp05.py", "pp06.py", "pv01.py",
         "loc01.py", "cg01.py", "corte01.py", "ct02.py", "ct03.py", "ct04.py", "mon01.py", "mon02.py", "mon03.py",
         "quantitativos.py", "ic01.py", "pr01.py", "ng01.py"]
ETAPAS = [ORDEM[0:3], ORDEM[3:7], ORDEM[7:18], ORDEM[18:24], ORDEM[24:31], ORDEM[31:40], ORDEM[40:]]
if __name__ == "__main__":
    args = sys.argv[1:]
    sem_cc = "--sem-cc" in args
    tudo = "--tudo" in args
    sem_lanc = "--sem-lancamento" in args
    com_3d = "--3d" in args
    args = [a for a in args if a not in ("--sem-cc", "--tudo", "--sem-lancamento", "--3d", "--emissao")]
    os.makedirs(MAN, exist_ok=True)
    if not args or args[0] == "--reset":
        for f in (LOG, PR + "travas_geometria.jsonl"):     # rev12: travas de geometria do jogo inteiro
            if os.path.exists(f):
                os.remove(f)
        if args:
            sys.exit(0)
    if args and args[0] == "--etapa":
        lista = ETAPAS[int(args[1]) - 1]
    elif args and args[0] == "--fim":
        lista = []
    else:
        lista = args or ORDEM
    env = dict(os.environ, AVISOS_LOG=LOG)
    if lista and not sem_lanc:                                  # gate de lançamento: geometria fechada antes das folhas
        r = subprocess.run([sys.executable, "verificar_lancamento.py"], cwd=EX, capture_output=True, text=True, timeout=1800)
        print(r.stdout[-3000:])
        if r.returncode:
            print("PARADO: o lançamento tem achados (verificacao_lancamento.json). Resolver a geometria antes das pranchas.")
            sys.exit(2)
    pdf_antes = {f: _h_pdf(PR + f) for f in os.listdir(PR) if f.endswith(".pdf")}
    rodadas, puladas = [], []
    for s in lista:
        t = time.time()
        if not tudo:
            ok, info = pode_pular(s)
            if ok:
                repetir_acrescimos(info)
                puladas.append(s)
                print(f"{s:22s} igual (pulada)", flush=True)
                continue
            motivo = info
        else:
            motivo = "--tudo"
        r = subprocess.run([sys.executable, "rodar_rastreado.py", s, MAN + s + ".json"], cwd=PR, env=env, capture_output=True, text=True, timeout=3000)
        rodadas.append(s)
        print(f"{s:22s} {'ok' if r.returncode == 0 else 'FALHOU'} {time.time() - t:5.0f} s  ({motivo})", flush=True)
        if r.returncode:
            print(r.stderr[-1500:])
    if com_3d:                                                  # 3D/IFC uma vez, no fim (≈ 20 min); pulado se nada que ele lê mudou
        m3 = MAN + "modelo_bim.json"
        ok, info = (False, "--tudo") if tudo else pode_pular_em(EX, "modelo_bim.py", m3)
        if ok and os.path.exists(m3) and any(os.path.getmtime(PR + f) > os.path.getmtime(m3) for f in os.listdir(PR) if f.startswith("ND-LET-") and f.endswith(".pdf")):
            ok, info = False, "folhas mudaram (o 3D embute as pranchas; o pymupdf abre o PDF fora do rastreio)"
        if ok:
            print("modelo_bim.py          igual (pulado)")
        else:
            t = time.time()
            r = subprocess.run([sys.executable, PR + "rodar_rastreado.py", EX + "modelo_bim.py", m3], cwd=EX, env=dict(os.environ, PYTHONPATH="/home/claude/ndengenharia/nd_estruturas"), capture_output=True, text=True, timeout=7000)
            print(f"modelo_bim.py          {'ok' if r.returncode == 0 else 'FALHOU'} {time.time() - t:5.0f} s  ({info})")
            if r.returncode:
                print(r.stderr[-1500:])
    base = PR + "emissao_revisada.json"                          # folhas como estavam na última emissão revisada (--emissao grava)
    ref = json.load(open(base, encoding="utf-8")) if os.path.exists(base) else pdf_antes
    alt = sorted(f[:-4] for f in os.listdir(PR) if f.endswith(".pdf") and f.startswith("ND-LET-") and _h_pdf(PR + f) != ref.get(f))
    if "--emissao" in sys.argv:
        json.dump({f: _h_pdf(PR + f) for f in os.listdir(PR) if f.endswith(".pdf")}, open(base, "w", encoding="utf-8"), indent=0)
        print("emissão registrada: próximas revisões comparam com estas folhas")
    if lista or "--emissao" in sys.argv:
        # rev12b (C44): registra a base da comparação — a última emissão revisada; sem ela, avisa (a revisão por diferença perde a referência)
        json.dump(dict(base="emissao_revisada.json" if os.path.exists(base) else "execução anterior (sem emissão revisada registrada)", rodadas=rodadas, puladas=puladas,
                       folhas_alteradas=alt), open(PR + "alteradas.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"rodadas {len(rodadas)}, puladas {len(puladas)}; PDFs alterados: {len(alt)}")
    final = {}
    for l in (open(LOG, encoding="utf-8") if os.path.exists(LOG) else []):
        d = json.loads(l)
        final[d["folha"]] = d["avisos"]                       # a última geração de cada folha vale
    idx = json.load(open(PR + "indice.json", encoding="utf-8"))["ordem"]
    ruins = {f: final.get(f) for f in idx if final.get(f) is None or final.get(f)}
    for f in idx:
        a = final.get(f)
        print(f"{f:16s}", "não gerada" if a is None else f"{sum(x[0] == 'ERRO' for x in a)} erros, {sum(x[0] != 'ERRO' for x in a)} avisos")
    for f, a in ruins.items():
        for x in (a or [])[:8]:
            print("  ", f, x)
    if sem_cc:
        sys.exit(0)
    cc = subprocess.run([sys.executable, "conferencia_cruzada.py"], cwd=PR, capture_output=True, text=True)   # rev11: conferência cruzada
    print(cc.stdout[-4000:])
    sys.exit(1 if (ruins or cc.returncode) else 0)
