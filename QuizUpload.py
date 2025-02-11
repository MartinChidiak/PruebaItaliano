import streamlit as st
import pandas as pd

st.title("Cargar archivo TXT")

# Widget para subir archivo
uploaded_file = st.file_uploader("Sube un archivo TXT", type=["txt"])

if uploaded_file is not None:
    try:
        # Leer el archivo con pandas
        df = pd.read_csv(uploaded_file, sep="\t")  # Ajusta el separador según corresponda
        st.success("Archivo cargado correctamente!")
        st.write(df.head())
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
