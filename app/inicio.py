import streamlit as st

st.title("ND Engenharia — Ferramentas")
st.write(
    "Ferramentas de cálculo do pacote **nd_estruturas**, as mesmas que rodam no PC. "
    "Escolha a ferramenta no menu ao lado (no celular, toque na seta do canto superior esquerdo)."
)

st.subheader("Disponíveis")
st.markdown(
    "- **Arco / tesoura funicular** — forma funicular de arco ou meia-tesoura atirantada para uma carga "
    "distribuída, com empuxo no tirante e conferência H = M0/f.\n"
    "- **Casca apoiada nos cantos** — forma funicular de casca em planta quadrada (JAX FDM) "
    "e análise linear em cascas no OpenSeesPy."
)

st.subheader("Unidades e sinais")
st.write("kN, m, kN·m, kPa. Compressão negativa, tração positiva.")

st.info(
    "Os resultados são para estudo e pré-dimensionamento e não dispensam a revisão do engenheiro "
    "responsável. ND Engenharia e Assessoria LTDA."
)
