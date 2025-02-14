import pandas as pd
import random
import streamlit as st

# Función para cargar datos desde un archivo .txt
@st.cache_data
def cargar_datos(archivo):
    if archivo is not None:
        try:
            datos = pd.read_csv(archivo, sep=",", encoding='utf-8')
            st.write("### Vista previa del archivo cargado:")
            st.write(datos.head())
            st.write("### Columnas del archivo:")
            st.write(datos.columns.tolist())
            return datos
        except Exception as e:
            st.error(f"Error reading the file: {e}")
            return None
    return None

# Función para reiniciar el quiz
def reiniciar_quiz():
    for key in ['tema_seleccionado', 'datos', 'opciones_random']:
        if key in st.session_state:
            del st.session_state[key]
    # Eliminar las respuestas almacenadas en session_state
    for key in list(st.session_state.keys()):
        if key.startswith("pregunta_"):
            del st.session_state[key]

# Inyectar CSS personalizado para el selectbox
st.markdown(
    """
    <style>
    /* Cambiar el fondo del selectbox a amarillo cuando no hay selección */
    div[data-baseweb="select"] .st-b7 {
        background-color: yellow !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Subida de archivo
uploaded_file = st.file_uploader("Upload a TXT file", type=["txt"])
if uploaded_file is None:
    st.warning("Please upload a TXT file to proceed.")
    st.warning("It must maintain the exact structure: Categoría,Pregunta,Respuesta Correcta,Incorrecta 1,Incorrecta 2,Incorrecta 3.")
else:
    try:
        datos = cargar_datos(uploaded_file)
        if datos is None or datos.empty:
            st.error("The file is empty or invalid.")
        else:
            columnas_esperadas = ['Categoría', 'Pregunta', 'Respuesta Correcta', 'Incorrecta 1', 'Incorrecta 2', 'Incorrecta 3']
            if not all(col in datos.columns for col in columnas_esperadas):
                st.error(f"The file does not have the expected columns. Columns found: {datos.columns.tolist()}")
            else:
                def main(datos):
                    st.title("Quiz")

                    if 'tema_seleccionado' not in st.session_state:
                        st.write("### Select the topic to study:")
                        temas = datos['Categoría'].unique()
                        tema = st.selectbox("Select a topic:", temas)
                        if st.button("Select topic"):
                            st.session_state['tema_seleccionado'] = tema
                            st.rerun()
                    else:
                        if st.button("Change topic"):
                            reiniciar_quiz()
                            return

                        if 'datos' not in st.session_state:
                            datos_filtrados = datos[datos['Categoría'] == st.session_state['tema_seleccionado']].reset_index(drop=True)
                            st.session_state['datos'] = datos_filtrados

                        datos_filtrados = st.session_state['datos']

                        if 'opciones_random' not in st.session_state:
                            opciones_random = {}
                            for i, row in datos_filtrados.iterrows():
                                opciones = [row['Respuesta Correcta'], row['Incorrecta 1'], row['Incorrecta 2'], row['Incorrecta 3']]
                                random.shuffle(opciones)
                                opciones_random[i] = opciones
                            st.session_state['opciones_random'] = opciones_random

                        st.markdown("## Quiz")
                        st.markdown("Answer all questions and press **Next** to see the results.")

                        with st.form("quiz_form"):
                            idx = 1
                            for index, row in datos_filtrados.iterrows():
                                st.markdown(f"### Question {idx} of {len(datos_filtrados)}")
                                st.markdown(f"**Question:** {row['Pregunta']}")

                                opciones = st.session_state['opciones_random'][index]
                                respuesta = st.selectbox(
                                    "Select an option:",
                                    [None] + opciones,
                                    key=f"pregunta_{idx}",
                                    format_func=lambda x: "Select an option" if x is None else x
                                )
                                st.write("---")
                                idx += 1

                            submit = st.form_submit_button("Next")

                        if submit:
                            correctas = 0
                            st.markdown("## Results")

                            idx = 1
                            for index, row in datos_filtrados.iterrows():
                                user_answer = st.session_state.get(f"pregunta_{idx}")
                                correct_answer = row['Respuesta Correcta']
                                if user_answer == correct_answer:
                                    correctas += 1
                                    st.success(f"**Question {idx}:** Correct")
                                else:
                                    st.error(
                                        f"**Question {idx}:** Incorrect\n"
                                        f"Your answer: *{user_answer}*\n"
                                        f"Correct answer: *{correct_answer}*"
                                    )
                                idx += 1

                            puntaje = (correctas / len(datos_filtrados)) * 10
                            st.subheader(f"Final Score: {puntaje:.1f} out of 10")

                            if st.button("Restart Quiz"):
                                reiniciar_quiz()
                                st.rerun()

                if __name__ == "__main__":
                    main(datos)

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
