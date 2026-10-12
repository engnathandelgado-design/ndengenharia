"""ND Engenharia — ferramentas online (Streamlit).

Rodar no PC:  streamlit run streamlit_app.py
Online:       Streamlit Community Cloud apontando para este arquivo.
"""
import sys
from pathlib import Path

import streamlit as st

# o pacote nd_estruturas fica em ./nd_estruturas/nd_estruturas
RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "nd_estruturas"))
sys.path.insert(0, str(RAIZ / "app"))

st.set_page_config(page_title="ND Engenharia — Ferramentas", layout="wide")

paginas = [
    st.Page("app/inicio.py", title="Início", default=True),
    st.Page("app/arco_funicular.py", title="Arco / tesoura funicular"),
    st.Page("app/casca_cantos.py", title="Casca apoiada nos cantos"),
]
st.navigation(paginas).run()

st.sidebar.caption("ND Engenharia e Assessoria LTDA · uso interno")
