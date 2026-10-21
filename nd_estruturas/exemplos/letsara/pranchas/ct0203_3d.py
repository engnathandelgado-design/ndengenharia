"""Recortes 3D (sem marca) para as folhas CT02 e CT03, do mesmo modelo publicado (letsara_3d.html)."""
import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from render_recortes import cena
EX = ('Telhas', 'Rufos e acabamentos', 'Calha e descidas', 'Piso e fundações')
JOBS = {
    "img_ct02/mez.png": ((12.3, 20.3, -0.6, 10.4, 0.0, 7.3), [(27.0, 21.0, 10.5), (16.0, 4.8, 3.2), (0, 0, 1)],
                         ('Laje alveolar', 'Concreto de 2º estágio (obra, com a capa)'), EX + ('Placas de fechamento', 'Fixação das placas'), 1.0),
    "img_ct03/geral.png": ((-1.0, 41.0, -1.0, 80.5, -1.5, 10.5), [(118.0, -62.0, 72.0), (19.75, 39.7, 3.0), (0, 0, 1)],
                           (), EX + ('Placas de fechamento', 'Fixação das placas'), 1.0),
    "img_ct03/eixoC.png": ((17.9, 21.6, -1.0, 80.5, -1.5, 10.5), [(62.0, 8.0, 16.0), (19.75, 40.0, 5.0), (0, 0, 1)],
                           (), EX + ('Placas de fechamento', 'Fixação das placas'), 1.0),
}
for nome, (box, cam, tr, ex, k) in JOBS.items():
    if sys.argv[1:] and nome not in sys.argv[1:]:
        continue
    cena("/home/claude/letsara/pranchas/" + nome, box, cam, excl=ex, transp=tr, k=k)
    print(nome, flush=True)
