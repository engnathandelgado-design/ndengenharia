"""Roda um gerador de folha e grava o que ele LEU e ESCREVEU (base da geração incremental do gerar_tudo).

Uso: python rodar_rastreado.py <script.py> <manifesto.json> [args...]
Registra, pelo audit hook do Python (open, listdir, scandir, glob, subprocess):
- entradas: arquivos lidos dentro de /home/claude e /tmp/claude-0 (inclusive módulos importados), com hash;
- pastas listadas (hash da listagem);
- saídas: arquivos escritos, com hash;
- acréscimos: o que o script anexou em arquivos abertos em modo 'a' (logs de avisos e travas), para repetir quando
  a folha for pulada;
- se o script chamou subprocesso, a folha não é pulada nunca (dependências fora do rastreio).
"""
import hashlib, json, os, runpy, sys, time

RAIZES = ("/home/claude/", "/tmp/claude-0/")
IGNORA = ("__pycache__", ".pyc", "/.git/", "gerar_tudo.jsonl.lock")


def _ok(p):
    return isinstance(p, str) and p.startswith(RAIZES) and not any(k in p for k in IGNORA)


def hash_arq(p):
    h = hashlib.sha1()
    try:
        with open(p, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                h.update(b)
    except OSError:
        return None
    return h.hexdigest()


def hash_pasta(p):
    try:
        return hashlib.sha1("\n".join(sorted(os.listdir(p))).encode()).hexdigest()
    except OSError:
        return None


def main():
    script, manifesto = os.path.abspath(sys.argv[1]), sys.argv[2]
    lidos, escritos, pastas, anexos = {}, set(), set(), {}
    estado = dict(sub=False, ativo=True)

    def hook(ev, args):
        if not estado["ativo"]:
            return
        if ev == "open":
            p, modo = args[0], args[1]
            if isinstance(p, int) or not isinstance(p, str):
                return
            p = os.path.abspath(p)
            if not _ok(p):
                return
            modo = modo or "r"
            if isinstance(modo, int):              # os.open: flags
                w = bool(modo & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND))
                a = bool(modo & os.O_APPEND)
            else:
                w = any(c in modo for c in "wxa+")
                a = "a" in modo
            if a and p not in anexos:
                anexos[p] = os.path.getsize(p) if os.path.exists(p) else 0
            if w:
                escritos.add(p)
            elif p not in escritos and os.path.isfile(p):
                lidos.setdefault(p, True)
        elif ev in ("os.listdir", "os.scandir"):
            p = args[0] if args and isinstance(args[0], str) else "."
            p = os.path.abspath(p)
            if _ok(p + "/"):
                pastas.add(p)
        elif ev == "glob.glob":
            p = os.path.abspath(os.path.dirname(args[0]) or ".")
            if _ok(p + "/"):
                pastas.add(p)
        elif ev in ("subprocess.Popen", "os.system", "os.posix_spawn", "os.exec"):
            estado["sub"] = True

    sys.argv = [script] + sys.argv[3:]
    sys.path.insert(0, os.path.dirname(script))
    sys.addaudithook(hook)
    t0, cod = time.time(), 0
    try:
        runpy.run_path(script, run_name="__main__")
    except SystemExit as e:
        cod = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    except BaseException:
        import traceback
        traceback.print_exc()
        cod = 1
    estado["ativo"] = False
    for m in list(sys.modules.values()):
        f = getattr(m, "__file__", None)
        if f and _ok(os.path.abspath(f)) and os.path.abspath(f) not in escritos:
            lidos.setdefault(os.path.abspath(f), True)
    lidos.pop(script, None)
    acresc = {}
    for p, ini in anexos.items():
        try:
            with open(p, "rb") as f:
                f.seek(ini)
                acresc[p] = f.read().decode("utf-8", "replace")
        except OSError:
            pass
    reg = dict(script=script, hash_script=hash_arq(script), codigo=cod, subprocesso=estado["sub"], segundos=round(time.time() - t0, 1),
               entradas={p: hash_arq(p) for p in sorted(lidos) if p not in anexos},
               pastas={p: hash_pasta(p) for p in sorted(pastas)},
               saidas={p: hash_arq(p) for p in sorted(escritos) if p not in anexos},
               acrescimos=acresc)
    with open(manifesto, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=0)
    sys.exit(cod)


if __name__ == "__main__":
    main()
