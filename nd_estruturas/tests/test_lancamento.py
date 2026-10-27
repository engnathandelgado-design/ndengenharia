"""Testes do gate de lançamento com casos reais da Letsara (rev12, 27/10/2026), montados à mão:
pilar de canto 10 cm para dentro da face dos PF, consolo de 40 sob VM de 30, portão de 4,925 m em vez de 5,00 m
e laje alveolar com 5 cm de apoio. Fonte das regras: decisões do Nathan (DEC-084, DEC-085 e mensagens de 27/10)."""
from nd_estruturas.bim import Peca, PerfilRetangular
from nd_estruturas.lancamento import Abertura, ConfigLancamento, Fachada, caixa, verificar


def pilar(marca, x, y, bx, by, h=8.0):
    # PerfilRetangular: b ao longo do X local, h ao longo do Y local; peça vertical com cima = +y global → X local = −x
    return Peca("pilar", "Pilares", marca, PerfilRetangular(bx, by), (x, y, 0.0), (x, y, h), cima=(0.0, 1.0, 0.0))


def viga_x(grupo, marca, x0, x1, yc, b, zb, h):
    return Peca("viga", grupo, marca, PerfilRetangular(b, h), (x0, yc, zb + h / 2), (x1, yc, zb + h / 2))


def cfg(**kw):
    base = dict(fachadas=[Fachada("linha 1", 1, -0.30, -1)], grupos_viga_borda=("VM",), grupos_viga=("VM",), grupos_laje=("LA",))
    base.update(kw)
    return ConfigLancamento(**base)


def test_caixa_pilar_vertical():
    c = caixa(pilar("P", 0.0, 0.0, 0.60, 0.40))
    assert abs((c[1] - c[0]) - 0.60) < 1e-9 and abs((c[3] - c[2]) - 0.40) < 1e-9


def test_pilar_de_canto_recuado_e_vm_alinhada():
    pf = pilar("PF", 9.87, 0.0, 0.40, 0.60)                      # face externa −0,30 (60 em y)
    canto_errado = pilar("P29", 0.0, 0.0, 0.60, 0.40)           # 40 em y no eixo: face −0,20 → 10 cm recuado
    canto_certo = pilar("P29", 0.0, -0.10, 0.60, 0.40)          # opção D: eixo 10 cm para fora
    vm = viga_x("VM", "VM-01", 0.30, 9.67, -0.15, 0.30, 2.89, 0.75)
    ach = verificar([pf, canto_errado, vm], cfg())
    assert [a["peca"] for a in ach] == ["P29"] and abs(ach[0]["valor"] - (-0.20)) < 1e-6
    assert verificar([pf, canto_certo, vm], cfg()) == []


def test_vm_no_eixo_gera_fresta():
    vm = viga_x("VM", "VM-01", 0.30, 9.67, 0.0, 0.30, 2.89, 0.75)  # VM no eixo: face −0,15 → 15 cm de fresta (fora da faixa)
    vm5 = viga_x("VM", "VM-01", 0.30, 9.67, -0.10, 0.30, 2.89, 0.75)  # opção A antiga: 5 cm para fora → ainda 5 cm de fresta
    assert verificar([vm5], cfg())[0]["regra"] == "alinhamento_fachada"
    assert verificar([vm], cfg(faixa=0.20))[0]["regra"] == "alinhamento_fachada"


def test_consolo_mais_largo_que_a_viga():
    vm = viga_x("VM", "VM-01", 0.30, 9.67, 5.0, 0.30, 2.89, 0.75)
    cons40 = Peca("viga", "Consolos", "CP-MEZ", PerfilRetangular(0.40, 0.40), (0.40, 5.0, 2.68), (0.40, 5.0, 2.88))
    cons30 = Peca("viga", "Consolos", "CP-MEZ", PerfilRetangular(0.40, 0.30), (0.40, 5.0, 2.68), (0.40, 5.0, 2.88))
    a = verificar([vm, cons40], cfg(fachadas=[]))
    assert len(a) == 1 and a[0]["regra"] == "largura_consolo" and abs(a[0]["valor"] - 0.40) < 1e-6
    assert verificar([vm, cons30], cfg(fachadas=[])) == []


def test_portao_perde_75_mm():
    c = cfg(fachadas=[], aberturas=[Abertura("portão", 0, 29.80, 12.57, 5.00)])
    ok = [pilar("PG-01", 9.87, 29.80, 0.40, 0.40), pilar("PG-02", 15.27, 29.80, 0.40, 0.25)]
    ruim = [pilar("PG-01", 9.87, 29.80, 0.40, 0.40), pilar("PG-02", 15.195, 29.80, 0.40, 0.25)]
    assert verificar(ok, c) == []
    a = verificar(ruim, c)
    assert a[0]["regra"] == "vao_livre" and abs(a[0]["valor"] - 4.925) < 1e-6


def test_apoio_da_laje():
    vm1 = viga_x("VM", "VM-01", 0.30, 9.67, -0.15, 0.30, 2.89, 0.75)
    vm2 = viga_x("VM", "VM-02", 0.30, 9.67, 9.65, 0.40, 2.89, 0.75)
    def laje(y0, y1):
        return Peca("laje", "LA", "LA-01", PerfilRetangular(1.20, 0.25), (1.0, y0, 3.775), (1.0, y1, 3.775))
    c = cfg(fachadas=[])
    assert verificar([vm1, vm2, laje(-0.10, 9.60)], c) == []        # 10 cm em cada viga
    a = verificar([vm1, vm2, laje(-0.05, 9.60)], c)                  # 5 cm na VM-01
    assert len(a) == 1 and a[0]["regra"] == "apoio_laje" and abs(a[0]["valor"] - 0.05) < 1e-6
