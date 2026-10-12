"""Página: forma funicular de arco / meia-tesoura atirantada (JAX FDM)."""
import math

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from comum import fmt, marcar

st.title("Arco / tesoura funicular")
st.caption("Forma em que a carga vertical vira só compressão axial, com o empuxo no tirante. kN, m.")

with st.form("entrada"):
    L = st.number_input("Vão entre apoios L (m)", 4.0, 80.0, 20.0, 0.5)
    nx = st.number_input("Número de trechos (par)", 4, 60, 20, 2)
    s = st.number_input("Espaçamento entre pórticos (m)", 1.0, 15.0, 5.90, 0.05)
    g = st.number_input("Carga em planta g + q (kN/m²)", 0.05, 20.0, 0.70, 0.05)
    pp = st.number_input("Peso próprio da peça (kN/m, em planta)", 0.0, 50.0, 0.0, 0.1)
    meta = st.radio("Meta", ["Flecha na cumeeira", "Empuxo no tirante"], horizontal=True)
    if meta == "Flecha na cumeeira":
        f_alvo = st.number_input("Flecha f (m)", 0.2, 30.0, round(L / 2 * math.tan(math.radians(15)), 2), 0.05)
        H_alvo = None
    else:
        H_alvo = st.number_input("Empuxo H (kN)", 1.0, 1e5, 200.0, 5.0)
        f_alvo = None
    ok = st.form_submit_button("Calcular", type="primary")

if nx % 2:
    st.error("Use número de trechos par (precisa existir nó na cumeeira).")
    st.stop()


@st.cache_data(show_spinner=False)
def calcular(L, nx, w, f_alvo, H_alvo):
    from nd_estruturas.formfinding import arco_funicular
    xs = np.linspace(-L / 2, L / 2, nx + 1)
    P = np.full(nx + 1, w * L / nx)
    P[0] = P[-1] = 0.0                                   # carga dos extremos vai direto ao apoio
    r = arco_funicular(xs, P, f_alvo=f_alvo, H_alvo=H_alvo)
    return xs, P, r


w = g * s + pp                                           # kN/m em planta
if not ok and "arco_ok" not in st.session_state:
    st.info("Preencha os dados e toque em Calcular.")
    st.stop()
st.session_state["arco_ok"] = True

with st.spinner("Achando a forma (JAX FDM)..."):
    xs, P, r = calcular(float(L), int(nx), float(w), f_alvo, H_alvo)

z, H, forcas = r["z"], r["H"], np.array(r["forcas"])
f = float(z[int(nx) // 2])
V = P[1:-1].sum() / 2
# conferência à mão: H = M0 / f, M0 = momento de viga biapoiada no meio do vão sob as mesmas cargas
meio = int(nx) // 2
M0 = V * L / 2 - sum(P[i] * (xs[meio] - xs[i]) for i in range(1, meio))
H_mao = M0 / f
N_max = float(np.abs(forcas).max())
ang = math.degrees(math.atan2(z[1] - z[0], xs[1] - xs[0]))

c = st.columns(4)
c[0].metric("Empuxo no tirante H", f"{fmt(H, 1)} kN")
c[1].metric("Reação vertical V", f"{fmt(V, 1)} kN")
c[2].metric("Compressão máx. no arco", f"{fmt(N_max, 1)} kN")
c[3].metric("Flecha f", f"{fmt(f, 3)} m")

dif = abs(H - H_mao) / H_mao * 100
(st.success if dif < 0.5 else st.warning)(
    f"Conferência à mão: H = M0/f = {fmt(M0, 1)} / {fmt(f, 3)} = {fmt(H_mao, 1)} kN "
    f"(diferença {fmt(dif, 3)} %)."
)

# parábola de mesma flecha, para comparação
zp = f * (1 - (2 * xs / L) ** 2)
fig = go.Figure()
fig.add_scatter(x=xs, y=z, mode="lines+markers", name="Funicular (FDM)", line=dict(width=3))
fig.add_scatter(x=xs, y=zp, mode="lines", name="Parábola de mesma flecha", line=dict(dash="dot"))
fig.add_scatter(x=[xs[0], xs[-1]], y=[0, 0], mode="lines", name="Tirante",
                line=dict(color="gray", width=2))
fig.update_yaxes(scaleanchor="x", scaleratio=1, title="z (m)")
fig.update_xaxes(title="x (m)")
st.plotly_chart(marcar(fig, 420), use_container_width=True)

st.caption(f"Inclinação no apoio: {fmt(ang, 1)}°. Carga linear usada: {fmt(w, 2)} kN/m em planta.")

with st.expander("Tabela de nós e barras"):
    barras = pd.DataFrame({
        "Barra": range(1, int(nx) + 1),
        "x inicial (m)": xs[:-1].round(3),
        "x final (m)": xs[1:].round(3),
        "N (kN, compr. −)": forcas.round(2),
    })
    nos = pd.DataFrame({"x (m)": xs.round(3), "z (m)": z.round(4), "P (kN)": P.round(2)})
    st.dataframe(nos, hide_index=True, use_container_width=True)
    st.dataframe(barras, hide_index=True, use_container_width=True)
    st.download_button("Baixar nós (CSV)", nos.to_csv(index=False, sep=";", decimal=","),
                       "arco_funicular_nos.csv", "text/csv")

st.caption("Forma funicular para a carga informada. Outras combinações (vento, carga assimétrica) geram "
           "flexão no arco e precisam ser verificadas no pórtico completo.")
