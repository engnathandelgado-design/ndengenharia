import os, tempfile, ezdxf, pymupdf
from prancha_nd import Prancha, MASSA_ACO
D = dict(cliente="X", obra="Y", local="Z", conteudo="TESTE", desenho="T-01")
tmp, ok = tempfile.mkdtemp(), []
def check(nome, cond):
    ok.append(cond); print(("PASS " if cond else "FAIL ") + nome)

p = Prancha("A1", D); v = p.vista("PLANTA", (100, 300), 20)
v.ret(0, 0, 3000, 1500); v.cota_h([0, 3000], 0, -10); p.salvar(os.path.join(tmp, "t1"))
pg = pymupdf.open(os.path.join(tmp, "t1.pdf"))[0]
check("T1a PDF A1 em 1:1", abs(pg.rect.width / 72 * 25.4 - 841) < 1 and abs(pg.rect.height / 72 * 25.4 - 594) < 1)
doc = ezdxf.readfile(os.path.join(tmp, "t1.dxf"))
dim = [e for e in doc.modelspace() if e.dxftype() == "DIMENSION"][0]
check("T1b cota = 3000 com geometria 1:20", [e.plain_text() for e in dim.virtual_entities() if e.dxftype() == "MTEXT"][0] == "3000")
pl = [e for e in doc.modelspace() if e.dxftype() == "LWPOLYLINE" and e.dxf.layer == "CORTADO"][0]
xs = [q[0] for q in pl.get_points("xy")]
check("T1c 3000 mm -> 150 mm no papel", abs(max(xs) - min(xs) - 150) < 1e-6)

p = Prancha("A3", dict(D, cliente="")); v = p.vista("CORTE A-A", (60, 120), 25)
v.ret(0, 0, 2000, 1000); v.texto((500, 500), "TEXTO SOBRE A LINHA")
v.texto((500, 1000), "CRUZA CONTORNO", alinh="MIDDLE_LEFT"); v.texto((560, 1000), "OUTRO", alinh="MIDDLE_LEFT")
v.marcador_detalhe((0, 0), 200, 7)
msgs = " | ".join(m for _, m in p.salvar(os.path.join(tmp, "t2")))
check("T2a carimbo vazio", "campo 'cliente' vazio" in msgs)
check("T2b textos sobrepostos", "textos sobrepostos" in msgs)
check("T2c linha cruza texto", "cruza o texto 'CRUZA CONTORNO'" in msgs)
check("T2d detalhe órfão", "DETALHE 7 sem vista" in msgs)

p = Prancha("A3", D)
r = p.tabela_aco(200, 280, [dict(pos="N1", diam=12.5, qtd=10, comp=320), dict(pos="N2", diam=10, qtd=16, comp=170)])
esp = (10 * 3.20 * MASSA_ACO[12.5] + 16 * 1.70 * MASSA_ACO[10.0]) * 1.10
check(f"T3 massa = {esp:.2f} kg", abs(r["total_kg"] - esp) < 1e-6)
check("T3b posição sem chamada", any("sem chamada" in m for _, m in p.verificar()))
p = Prancha("A3", D)
r = p.tabela_cordoalhas(200, 280, [dict(pos="C1", diam=12.7, qtd=4, y=51, forca=137.0, isol=3350, local="CENTRO"),
                                   dict(pos="C2", diam=12.7, qtd=1, y=380, forca=150.0, isol=0)], 100)
lin = [e.dxf.text for e in p.msp if e.dxftype() == "TEXT"]
check("T5a ΔL = 712 mm (137 kN, 100 m, Ep 195 GPa, Ap 98,7)", "712" in lin)
check("T5b σpi 1520 > 1454 MPa vira ERRO no verificar()", sum("C2: σpi" in m for n, m in p.verificar() if n == "ERRO") == 1)
check("T5c cordoalha tabelada não acusa 'sem linha'", "C1" in p.posicoes_tabela)
print(f"{sum(ok)}/{len(ok)} PASS")
