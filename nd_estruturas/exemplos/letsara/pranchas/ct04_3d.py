import sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
from render_recortes import cena
O = "/home/claude/letsara/pranchas/img_ct04/"
EX = ('Telhas', 'Rufos e acabamentos', 'Placas de fechamento', 'Calha e descidas', 'Fixação das placas', 'Piso e fundações')
jobs = {
 "a1": ((-0.45, 1.3, 19.35, 20.1, 6.5, 8.6), [(2.2, 17.9, 8.9), (0.2, 19.725, 7.4), (0, 0, 1)]),
 "a2": ((18.6, 20.9, 19.35, 20.1, 6.8, 9.0), [(21.9, 17.9, 9.3), (19.75, 19.725, 7.9), (0, 0, 1)]),
 "a3": ((19.15, 20.35, 29.75, 31.3, 6.2, 7.77), [(22.0, 31.9, 6.55), (19.75, 30.35, 7.05), (0, 0, 1)]),
 "a4": ((9.45, 11.2, 9.15, 10.15, 2.45, 4.05), [(11.9, 11.6, 2.65), (10.2, 9.7, 3.25), (0, 0, 1)]),
 "a5": ((9.55, 11.1, -0.35, 0.45, 7.2, 8.8), [(11.9, 2.0, 7.5), (10.25, 0.0, 8.0), (0, 0, 1)]),
 "a6": ((4.4, 5.7, -0.35, 1.0, 2.75, 4.0), [(6.9, 1.9, 3.65), (5.0, 0.15, 3.5), (0, 0, 1)]),
}
TR = {'a1': ('Vigas I90 de cobertura',), 'a2': ('Vigas I90 de cobertura', 'Vigas centrais I130'), 'a3': ('Vigas centrais I130', 'Consolos'), 'a4': ('Vigas de mezanino (retangulares protendidas)', 'Concreto de 2º estágio (obra, com a capa)', 'Laje alveolar'), 'a5': ('Vigas de borda',), 'a6': ('Concreto de 2º estágio (obra, com a capa)', 'Laje alveolar')}
for k, (box, cam) in [(k_, jobs[k_]) for k_ in (sys.argv[1:] or jobs)]:
    cena(O + k + ".png", box, cam, excl=EX + (('Esperas e insertos embutidos',) if k == 'a3' else ()), titulo="", transp=TR.get(k, ()), k=1.6)
    print(k, flush=True)
