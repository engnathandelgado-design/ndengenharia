"""Página: casca em planta quadrada apoiada nos 4 cantos (JAX FDM -> OpenSeesPy)."""
import threading

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from comum import fmt, marcar

# OpenSeesPy guarda estado global: uma análise por vez no servidor
_TRAVA = threading.Lock()

st.title("Casca apoiada nos cantos")
st.caption("Forma funicular pelo JAX FDM e análise linear em cascas (ShellMITC4) no OpenSeesPy. kN, m, kPa.")

with st.form("entrada_casca"):
    L = st.number_input("Lado em planta L (m)", 6.0, 40.0, 20.0, 1.0)
    n = st.select_slider("Malha (divisões por lado)", [8, 12, 16, 20], 12)
    q = st.number_input("Carga em planta (kPa)", 0.5, 20.0, 3.5, 0.1)
    Hc = st.number_input("Altura no centro (m)", 0.5, 15.0, 4.0, 0.1)
    Ha = st.number_input("Altura no meio das bordas (m)", 0.2, 15.0, 2.5, 0.1)
    t = st.number_input("Espessura da casca t (m)", 0.04, 0.40, 0.10, 0.01)
    fck = st.number_input("fck (MPa)", 20, 50, 30, 5)
    bv = st.number_input("Viga de borda b = h (m)", 0.15, 1.0, 0.35, 0.05)
    ok = st.form_submit_button("Calcular", type="primary")

if Ha >= Hc:
    st.error("A altura no centro precisa ser maior que a do meio das bordas.")
    st.stop()
if not ok and "casca_ok" not in st.session_state:
    st.info("Preencha os dados e toque em Calcular. Malha 12 leva poucos segundos; 20 pode levar mais de um minuto.")
    st.stop()
st.session_state["casca_ok"] = True


@st.cache_data(show_spinner=False)
def calcular(L, n, q, Hc, Ha, t, fck, bv):
    from nd_estruturas import formfinding as ff
    forma = ff.forma_casca(L=L, n=n, carga=q, H_coroa=Hc, H_arco=Ha)
    with _TRAVA:
        mod = ff.modelo_casca(forma["xyz"], t=t, fck=fck, viga=(bv, bv))
        P = ff.cargas(mod, lambda x, y: q)
        if not ff.analisar_linear():
            raise RuntimeError("A análise linear não convergiu.")
        out, R, w = ff.esforcos(mod)
        vig = ff.esforcos_vigas(mod)
    return forma["xyz"], out, [list(map(float, r)) for r in R], float(w), float(P), vig


with st.spinner("Achando a forma e analisando..."):
    try:
        xyz, out, R, w, P, (Nv_min, Nv_max, Mv_max) = calcular(float(L), int(n), float(q), float(Hc),
                                                               float(Ha), float(t), int(fck), float(bv))
    except Exception as e:  # noqa: BLE001
        st.error(f"Não foi possível calcular: {e}")
        st.stop()

H = float(np.hypot(*R[0][:2]))
Vc = float(R[0][2])
N2 = min(o["N2"] for o in out)
N1 = max(o["N1"] for o in out)
sig_max = max(o["sig_max"] for o in out)
sig_min = min(o["sig_min"] for o in out)
M_max = max(o["M_abs"] for o in out)

c = st.columns(4)
c[0].metric("Reação vertical por canto", f"{fmt(Vc, 1)} kN")
c[1].metric("Empuxo horizontal por canto", f"{fmt(H, 1)} kN")
c[2].metric("Flecha máxima", f"{fmt(abs(w) * 1000, 2)} mm")
c[3].metric("Carga total", f"{fmt(P, 1)} kN")

soma = sum(r[2] for r in R)
(st.success if abs(soma - P) / P < 1e-4 else st.warning)(
    f"Equilíbrio: soma das reações verticais = {fmt(soma, 2)} kN; carga aplicada = {fmt(P, 2)} kN."
)

# superfície 3D colorida pela compressão principal (média por elemento levada aos nós)
nn = xyz.shape[0]
campo = np.zeros((nn, nn)); cont = np.zeros((nn, nn))
for o in out:
    for di in (0, 1):
        for dj in (0, 1):
            campo[o["i"] + di, o["j"] + dj] += o["N2"]; cont[o["i"] + di, o["j"] + dj] += 1
campo /= np.maximum(cont, 1)

fig = go.Figure(go.Surface(x=xyz[:, :, 0], y=xyz[:, :, 1], z=xyz[:, :, 2], surfacecolor=campo,
                           colorscale="RdBu", reversescale=False,
                           colorbar=dict(title="N2 (kN/m)", len=0.7)))
fig.update_layout(scene=dict(aspectmode="data", xaxis_title="x (m)", yaxis_title="y (m)", zaxis_title="z (m)"),
                  title="Forma funicular — esforço principal de compressão")
st.plotly_chart(marcar(fig, 520), use_container_width=True)

st.subheader("Esforços na casca")
d = st.columns(3)
d[0].metric("Compressão principal mín. N2", f"{fmt(N2, 1)} kN/m")
d[1].metric("Tração principal máx. N1", f"{fmt(N1, 2)} kN/m")
d[2].metric("Momento máx. |M|", f"{fmt(M_max, 3)} kN·m/m")
e = st.columns(3)
e[0].metric("Tensão mín. (faces)", f"{fmt(sig_min / 1000, 2)} MPa")
e[1].metric("Tensão máx. (faces)", f"{fmt(sig_max / 1000, 2)} MPa")
e[2].metric("Viga de borda: |M| máx.", f"{fmt(Mv_max, 1)} kN·m")
st.caption(f"Viga de borda: N entre {fmt(Nv_min, 1)} e {fmt(Nv_max, 1)} kN. "
           "Tensões em estádio I, média dos pontos de Gauss por elemento.")

st.caption("Análise linear elástica de casca perfeita. Flambagem (imperfeição, fluência, fissuração), "
           "cargas assimétricas e vento precisam ser verificados à parte antes do dimensionamento.")
