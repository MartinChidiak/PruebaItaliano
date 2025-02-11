import pandas as pd
import random
import streamlit as st

# Función para cargar datos desde un archivo .txt (cacheada usando st.cache_data)
@st.cache_data
def cargar_datos(archivo):
    if archivo is not None:
        return pd.read_csv(archivo, sep="\t")  # Ajusta el separador según corresponda
    return None

# Función para reiniciar el quiz (limpiar session_state)
def reiniciar_quiz():
    for key in ['tema_seleccionado', 'datos', 'opciones_random']:
        if key in st.session_state:
            del st.session_state[key]

def main():
    st.title("Quiz de Italiano")

    # Widget para subir archivo
    uploaded_file = st.file_uploader("Sube un archivo TXT", type=["txt"])

    if uploaded_file is None:
        st.warning("Por favor, sube un archivo TXT para continuar.")
        st.warning("Debe mantener esta estructura exacta Categoría,Pregunta,Respuesta Correcta,Incorrecta 1,Incorrecta 2,Incorrecta 3.")
        return

    # Cargar los datos del archivo cargado
    try:
        datos = cargar_datos(uploaded_file)
        if datos is None or datos.empty:
            st.error("El archivo está vacío o no es válido.")
            return
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return

    # Si no se ha seleccionado un tema, se muestra la selección
    if 'tema_seleccionado' not in st.session_state:
        st.write("### Seleccione el tema a estudiar:")
        temas = datos['Categoría'].unique()  # Obtenemos las categorías únicas como temas
        tema = st.selectbox("Selecciona un tema:", temas)
        if st.button("Seleccionar tema"):
            st.session_state['tema_seleccionado'] = tema
    else:
        # Botón para cambiar de tema (reinicia el quiz)
        if st.button("Cambiar tema"):
            reiniciar_quiz()
            return  # Al limpiar el estado se reinicia la aplicación en la siguiente reejecución

        # Filtrar los datos según el tema seleccionado
        if 'datos' not in st.session_state:
            datos_filtrados = datos[datos['Categoría'] == st.session_state['tema_seleccionado']].reset_index(drop=True)
            st.session_state['datos'] = datos_filtrados
        datos = st.session_state['datos']

        # Precalcular y almacenar las opciones de cada pregunta de forma aleatoria
        if 'opciones_random' not in st.session_state:
            opciones_random = {}
            for i, row in datos.iterrows():
                opciones = [row['Respuesta Correcta'], row['Incorrecta 1'], row['Incorrecta 2'], row['Incorrecta 3']]
                random.shuffle(opciones)
                opciones_random[i] = opciones
            st.session_state['opciones_random'] = opciones_random

        st.markdown("## Quiz")
        st.markdown("Responde todas las preguntas y presiona **Siguiente** para ver los resultados.")

        with st.form("quiz_form"):
            # Inicializar idx en 1
            idx = 1

            # Iterar sobre las filas del DataFrame filtrado
            for index, row in datos.iterrows():  # Usamos iterrows para recorrer las filas
                st.markdown(f"### Pregunta {idx} de {len(datos)}")  # Numeración correcta (idx empieza en 1)
                st.markdown(f"**Pregunta:** {row['Pregunta']}")  # Accedemos a los datos usando el nombre de la columna

                # Mostrar las opciones barajadas previamente
                opciones = st.session_state['opciones_random'][index]  # Usamos el índice original como clave
                st.radio("Selecciona una opción:", opciones, key=f"pregunta_{idx}")  # Usamos idx como clave única
                st.write("---")

                # Incrementar idx manualmente
                idx += 1

            submit = st.form_submit_button("Siguiente")

        # Al enviar el formulario, se validan todas las respuestas
        if submit:
            correctas = 0
            st.markdown("## Resultados")

            # Reiniciar idx en 1 para mostrar los resultados
            idx = 1

            for index, row in datos.iterrows():  # Iteramos nuevamente para mostrar resultados
                user_answer = st.session_state.get(f"pregunta_{idx}")  # Obtenemos la respuesta del usuario
                correct_answer = row['Respuesta Correcta']  # Accedemos a la respuesta correcta
                if user_answer == correct_answer:
                    correctas += 1
                    st.success(f"**Pregunta {idx}:** Correcto")  # Numeración correcta (idx empieza en 1)
                else:
                    st.error(
                        f"**Pregunta {idx}:** Incorrecto  \n"
                        f"Tu respuesta: *{user_answer}*  \n"
                        f"Respuesta correcta: *{correct_answer}*"
                    )
                # Incrementar idx manualmente
                idx += 1

            puntaje = (correctas / len(datos)) * 10
            st.subheader(f"Puntaje final: {puntaje:.1f} de 10")

            if st.button("Reiniciar Quiz"):
                reiniciar_quiz()
                return


if __name__ == "__main__":
    main()
