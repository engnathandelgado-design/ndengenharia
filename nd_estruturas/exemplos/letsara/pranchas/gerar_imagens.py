"""rev11 (26/10/2026): regera os isométricos/renders 3D das folhas em alta resolução (≥ 450 ppi no tamanho impresso),
com o patch _hd/sitecustomize.py (janela × S, linhas, pontos e fontes × S; linhas ≥ 3,2 px ≈ 0,18 mm a 450 ppi).
S por gerador = ceil(460 / ppi da rev10), medido com pdfimages -list. Rodar ANTES do gerar_tudo (que usa os mesmos S
para os geradores chamados pelas folhas). Uso: python gerar_imagens.py"""
import json, os, subprocess, sys, time
PR = "/home/claude/letsara/pranchas/"
MAPA = {"iso3d_pilar_gen.py": 3, "iso3d_ts01.py": 4, "iso3d_vm.py": 3, "iso3d_vigas.py": 4, "iso_la_pp.py": 3, "iso_fachadas.py": 2,
        "es04.py": 4, "ct0203_3d.py": 5, "ct04_3d.py": 3, "ng01_render2.py": 3}


def env():
    return dict(os.environ, PYTHONPATH=PR + "_hd", ND_PV_SCALE_MAP=json.dumps(MAPA), ND_PV_LWMIN="3.2")


JOBS = [(["iso3d_ts01.py"], PR), (["iso3d_vm.py"], PR), (["iso3d_vigas.py", "i130", "vb", "vm"], PR), (["iso_la_pp.py"], PR),
        (["iso_fachadas.py"], PR), (["ct0203_3d.py"], PR), (["ct04_3d.py"], PR),
        (["mk_malha.py"], PR + "img_ng01/"), (["ng01_render2.py"], PR + "img_ng01/")]
if __name__ == "__main__":
    for cmd, cwd in JOBS:
        t = time.time()
        r = subprocess.run([sys.executable, cwd + cmd[0]] + cmd[1:], cwd=cwd, env=env(), capture_output=True, text=True, timeout=7200)
        print(f"{cmd[0]:20s} {'ok' if r.returncode == 0 else 'FALHOU'} {time.time() - t:5.0f} s", flush=True)
        if r.returncode:
            print(r.stderr[-1500:])
