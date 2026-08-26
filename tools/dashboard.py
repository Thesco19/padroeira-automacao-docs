import streamlit as st
import os

st.set_page_config(page_title="Lab Padroeira Control", layout="wide")
st.title("🚀 Hermes Core: Padroeira MCP")

st.sidebar.success("Servidor MCP Conectado")

if st.button("Disparar Gatilho de Consolidação"):
    st.write("Executando automação...")
    # Aqui chamaremos a ferramenta do MCP futuramente
    st.success("Comando enviado!")

st.write("Explorador de Arquivos:")
st.write(os.listdir("/home/teco/work_out"))
