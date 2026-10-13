"""Compacta PDFs vetoriais do ezdxf/PyMuPDF: arredonda as coordenadas dos content streams a 2 casas (0,01 pt = 0,004 mm)."""
import re, sys
import pymupdf
NUM = re.compile(rb"-?\d*\.\d+")
def r(m):
    v = round(float(m.group(0)), 2)
    s = (b"%.2f" % v).rstrip(b"0").rstrip(b".")
    return s if s not in (b"-0", b"") else b"0"
def compactar(ent, sai):
    d = pymupdf.open(ent)
    for pg in d:
        for x in pg.get_contents():
            d.update_stream(x, NUM.sub(r, d.xref_stream(x)))
    d.save(sai, garbage=4, deflate=True, use_objstms=1)
if __name__ == "__main__":
    compactar(sys.argv[1], sys.argv[2])
