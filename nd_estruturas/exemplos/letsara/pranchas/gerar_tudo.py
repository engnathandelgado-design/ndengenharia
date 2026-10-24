"""Regera o jogo executivo completo da Letsara na ordem certa e resume erros/avisos por folha (AVISOS_LOG).
Uso: python gerar_tudo.py  → log em gerar_tudo.jsonl; falha se alguma folha do índice tiver erro ou aviso."""
import json, os, subprocess, sys, time
PR = "/home/claude/letsara/pranchas/"
LOG = PR + "gerar_tudo.jsonl"
ORDEM = ["pilares_familia.py", "pilar_generico.py", "ts01_chaparia.py", "vigas_exec.py", "cob01.py", "cob02.py", "cob03.py", "cob04.py", "cob_l2.py", "mt01.py",
         "lajes_placas.py", "es01.py", "fechamento.py", "pp01.py", "pp02.py", "pp03.py", "pp04.py", "pp05.py", "pp06.py",
         "loc01.py", "cg01.py", "corte01.py", "ct02.py", "ct03.py", "ct04.py", "mon01.py", "mon02.py", "mon03.py",
         "quantitativos.py", "pr01.py", "ng01.py"]
if __name__ == "__main__":
    if os.path.exists(LOG):
        os.remove(LOG)
    env = dict(os.environ, AVISOS_LOG=LOG)
    for s in sys.argv[1:] or ORDEM:
        t = time.time()
        r = subprocess.run([sys.executable, s], cwd=PR, env=env, capture_output=True, text=True, timeout=3000)
        print(f"{s:22s} {'ok' if r.returncode == 0 else 'FALHOU'} {time.time() - t:5.0f} s", flush=True)
        if r.returncode:
            print(r.stderr[-1500:])
    final = {}
    for l in open(LOG, encoding="utf-8"):
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
    sys.exit(1 if ruins else 0)
