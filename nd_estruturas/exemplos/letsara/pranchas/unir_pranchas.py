"""Junta as pranchas por tipo em arquivos únicos (para análise da engenharia que aprova):
PDF único por grupo (páginas na ordem) e DXF único por grupo (cada folha vira um bloco FOLHA_<desenho>, inserido lado a lado
no model space, com o número da folha acima). Saída em /home/claude/letsara/entregas/."""
import os, subprocess, sys
sys.path.insert(0, "/home/claude/letsara/pranchas")
import ezdxf
from ezdxf import bbox as _bbox
from ezdxf.addons import Importer

PR = "/home/claude/letsara/pranchas/"
OUT = "/home/claude/letsara/entregas/"
REV = "rev08-executivo"
# Emissão executiva (21/10/2026): fôrma e armação na mesma folha por marca; folhas AR-PIL/AR-VIG obsoletas.
# A ordem segue o índice da NG01 (indice.json, quando existir).
GRUPOS = [
    ("00-GERAIS", "FOLHA DE ROSTO, NOTAS GERAIS, PRODUÇÃO, LOCAÇÃO, CARGAS, CORTES E MONTAGEM",
     ["ND-LET-NG01", "ND-LET-PR01", "ND-LET-LOC01", "ND-LET-CG01", "ND-LET-CT01", "ND-LET-CT02", "ND-LET-CT03", "ND-LET-CT04",
      "ND-LET-MON01", "ND-LET-MON02", "ND-LET-MON03"]),
    ("01-PILARES", "PILARES — FÔRMA E ARMAÇÃO POR MARCA",
     [f"ND-LET-PL{k:02d}" for k in range(1, 13)] + [f"ND-LET-PF{k:02d}" for k in range(1, 7)] +
     ["ND-LET-PC01", "ND-LET-PC02", "ND-LET-PC03", "ND-LET-PM01", "ND-LET-PG01", "ND-LET-PG02", "ND-LET-PG03", "ND-LET-PG04"]),
    ("02-VIGAS", "VIGAS — FÔRMA, ARMAÇÃO E PROTENSÃO POR MARCA", ["ND-LET-TS01-1", "ND-LET-TS01-3", "ND-LET-I130", "ND-LET-VM01", "ND-LET-VB01"]),
    ("03-LAJES-E-FECHAMENTO", "LAJES ALVEOLARES E FECHAMENTO LATERAL",
     ["ND-LET-LA01", "ND-LET-PP00", "ND-LET-PP01", "ND-LET-PP02", "ND-LET-PP03", "ND-LET-PP04", "ND-LET-PP05", "ND-LET-PP06",
      "ND-LET-PP-A", "ND-LET-PP-B", "ND-LET-PP-C", "ND-LET-PP-D", "ND-LET-PP-EF", "ND-LET-PP-G", "ND-LET-PP-HJ", "ND-LET-PP-I", "ND-LET-CM01"]),
    ("04-COBERTURA", "COBERTURA METÁLICA — PLANTA, TRAVAMENTO, LIGAÇÕES, CALHA, ACABAMENTOS E LISTAS",
     ["ND-LET-COB01", "ND-LET-COB02", "ND-LET-COB03", "ND-LET-COB04", "ND-LET-MT01-1", "ND-LET-MT01-2"]),
]


def _ordem():
    """ordem do índice da NG01 (indice.json), senão a dos grupos; folhas extras dos grupos entram no fim do seu grupo."""
    import json
    base = [f for _, _, fl in GRUPOS for f in fl]
    try:
        idx = [("ND-LET-" + f if not f.startswith("ND-LET-") else f) for f in json.load(open(PR + "indice.json", encoding="utf-8"))["ordem"]]
        return [f for f in idx if f in base] + [f for f in base if f not in idx]
    except Exception:
        return base


def unir_dxf(nome, folhas):
    alvo = ezdxf.new("R2018", setup=True, units=4)
    for n, padrao, desc in (("ACAD_ISO02W100", [15.0, 12.0, -3.0], "ISO dashed __ __ __"),
                            ("ACAD_ISO10W100", [18.0, 12.0, -3.0, 0.0, -3.0], "ISO dash dot __ . __ .")):
        if n not in alvo.linetypes:
            alvo.linetypes.add(n, pattern=padrao, description=desc)
    msp = alvo.modelspace()
    x = 0.0
    for f in folhas:
        src = ezdxf.readfile(PR + f + ".dxf")
        for dim in list(src.modelspace().query("DIMENSION")):      # cotas viram linhas/textos (o Importer não leva os blocos *D)
            dim.explode()
        ext = _bbox.extents(src.modelspace(), fast=True)
        W = ext.extmax.x - min(0.0, ext.extmin.x) if ext.has_data else 1189.0
        blk = alvo.blocks.new(name=f"FOLHA_{f}")
        imp = Importer(src, alvo)
        imp.import_entities(list(src.modelspace()), target_layout=blk)
        imp.finalize()
        msp.add_blockref(blk.name, (x, 0))
        x += W + 100.0
    alvo.header["$LTSCALE"] = 0.5
    alvo.header["$PSLTSCALE"] = 0
    alvo.header["$LWDISPLAY"] = 1
    caminho = OUT + f"ND-LET-{nome}-{REV}.dxf"
    alvo.saveas(caminho)
    chk = ezdxf.readfile(caminho)
    aud = chk.audit()
    return caminho, len(aud.errors), len(aud.fixes)


def unir_pdf(nome, folhas):
    caminho = OUT + f"ND-LET-{nome}-{REV}.pdf"
    tmp = caminho + ".tmp.pdf"
    subprocess.run(["qpdf", "--empty", "--pages"] + [PR + f + ".pdf" for f in folhas] + ["--", tmp], check=True)
    from compactar_pdf import compactar
    compactar(tmp, caminho)                                  # coordenadas a 0,01 pt: arquivo ~20% menor, sem perda visível
    os.remove(tmp)
    return caminho


if __name__ == "__main__":
    so = sys.argv[1:]
    todas = _ordem()
    falta = [f for f in todas if not os.path.exists(PR + f + ".pdf")]
    assert not falta, falta
    p = unir_pdf("PRANCHAS", todas)
    print("PDF único:", p, len(todas), "folhas,", os.path.getsize(p) // 1024, "kB")
    for nome, titulo, folhas in GRUPOS:
        if so and nome not in so:
            continue
        falta = [f for f in folhas if not os.path.exists(PR + f + ".dxf")]
        assert not falta, falta
        p = unir_pdf(nome, folhas)
        d, ne, nf = unir_dxf(nome, folhas)
        print(nome, len(folhas), "folhas |", os.path.getsize(p) // 1024, "kB pdf |", os.path.getsize(d) // 1024, "kB dxf | audit erros", ne, "correções", nf)
