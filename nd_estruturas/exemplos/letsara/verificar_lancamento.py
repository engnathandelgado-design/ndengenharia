"""Gate de lançamento da Letsara: roda as checagens de nd_estruturas.lancamento sobre o modelo BIM (≈ 20 s) antes das
pranchas. Saída: verificacao_lancamento.json. Código de saída 1 se houver achado (o gerar_tudo para aqui).
Uso: python verificar_lancamento.py"""
import json, sys
from pathlib import Path
AQ = Path(__file__).parent
sys.path.insert(0, str(AQ)); sys.path.insert(0, str(AQ.parent.parent))
import geometria as G
import modelo_bim as MB
from nd_estruturas.lancamento import Abertura, ConfigLancamento, Fachada, verificar

CFG = ConfigLancamento(
    fachadas=[Fachada("A (x mín.)", 0, G.X_FACE_EXT[0], -1), Fachada("E (x máx.)", 0, G.X_FACE_EXT[1], +1),
              Fachada("linha 1", 1, G.Y_FACE_EXT[0], -1), Fachada("linha 9", 1, G.Y_FACE_EXT[1], +1),
              Fachada(f"linha 4 (parede dos portões, placas {G.lado_placas_txt('C')})", 1, G.Y_FACE_L4, G.PAREDE_INTERNA["C"]["lado"])],
    aberturas=[Abertura("portão 1 da linha 4", 0, G.Y_LIN[G.LINHA_PORTOES], 12.57, G.VAO_PORTAO),
               Abertura("portão 2 da linha 4", 0, G.Y_LIN[G.LINHA_PORTOES], 26.93, G.VAO_PORTAO)],
    grupos_viga_borda=("Vigas de borda", "Vigas de mezanino (retangulares protendidas)"),
    grupos_viga=("Vigas de borda", "Vigas de mezanino (retangulares protendidas)", "Vigas centrais I120", "Vigas I90 de cobertura"),
    grupos_laje=("Laje alveolar",),
    apoio_min_laje=0.08,              # regra do Nathan (laje alveolar apoia 8 cm sobre a viga)
)

if __name__ == "__main__":
    m = MB.montar()
    MB.renomear_pecas(m) if hasattr(MB, "renomear_pecas") else None
    ach = verificar(m.pecas, CFG)
    print("conferido:", CFG.contagem)
    json.dump(dict(achados=ach, n=len(ach), conferido=CFG.contagem), open(AQ / "verificacao_lancamento.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    por = {}
    for a in ach:
        por.setdefault(a["regra"], []).append(a)
    for r, v in por.items():
        print(f"{r}: {len(v)}")
        for a in v[:15]:
            print("   ", a["peca"], "|", a["msg"])
    print("LANÇAMENTO LIBERADO" if not ach else f"LANÇAMENTO BLOQUEADO: {len(ach)} achados")
    sys.exit(1 if ach else 0)
