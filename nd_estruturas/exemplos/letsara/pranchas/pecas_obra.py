"""Peças da obra (marca → descrição, L, quantidade, volume, peso, fck, folha) da MESMA fonte das listas de materiais
(quantitativos.py), lendo só o trecho que monta a lista de peças — as folhas gerais não dependem das tabelas de insertos."""
import pathlib
_src = pathlib.Path(__file__).with_name("quantitativos.py").read_text(encoding="utf-8")
_ns = {"__name__": "quantitativos_pecas", "__file__": str(pathlib.Path(__file__).with_name("quantitativos.py"))}
exec(compile(_src[:_src.index("# ------------------------------------------------------------------ aço CA-50")], "quantitativos.py", "exec"), _ns)
pecas = _ns["pecas"]
PQ = {p_[1]: p_ for p_ in pecas}
