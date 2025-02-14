import pandas as pd
import random
import streamlit as st 

# Función para cargar datos desde Excel (cacheada)
@st.cache_data
def cargar_datos(ruta_archivo, solapa):
    return pd.read_excel(ruta_archivo, sheet_name=solapa)

# Función para reiniciar el quiz (limpiar session_state)
def reiniciar_quiz():
    for key in ['tema_seleccionado', 'datos', 'opciones_random', 'idioma_seleccionado']:
        if key in st.session_state:
            del st.session_state[key]
    # Limpiar también las respuestas de las preguntas
    for key in list(st.session_state.keys()):
        if key.startswith("pregunta_"):
            del st.session_state[key]

def main():
    st.title("Quiz de Italiano") 
    ruta_archivo = 'quiz_italiano.xlsx'

    # Cargar nombres de las solapas (temas)
    try:
        solapas = pd.ExcelFile(ruta_archivo).sheet_names
    except Exception as e:
        st.error(f"Error al cargar el archivo Excel: {e}")
        return

    # Selección de idioma
    if 'idioma_seleccionado' not in st.session_state:
        st.write("### Seleccione el idioma para las preguntas:")
        idioma = st.selectbox("Idioma:", ["Español", "Italiano"])
        if st.button("Seleccionar idioma"):
            st.session_state['idioma_seleccionado'] = idioma
            st.rerun()
    else:
        # Si no se ha seleccionado un tema, se muestra la selección
        if 'tema_seleccionado' not in st.session_state:
            st.write("### Seleccione el tema a estudiar:")
            tema = st.selectbox("Selecciona un tema:", solapas)
            if st.button("Seleccionar tema"):
                st.session_state['tema_seleccionado'] = tema
                st.rerun()
        else:
            # Botón para cambiar de tema (reinicia el quiz)
            if st.button("Volver al inicio"):
                reiniciar_quiz()
                st.rerun()  # Reiniciar la aplicación
            
            # Cargar los datos del tema seleccionado, si aún no se han cargado
            if 'datos' not in st.session_state:
                datos = cargar_datos(ruta_archivo, st.session_state['tema_seleccionado'])
                st.session_state['datos'] = datos
            datos = st.session_state['datos']
            
            # Precalcular y almacenar las opciones de cada pregunta de forma aleatoria
            if 'opciones_random' not in st.session_state:
                opciones_random = {}
                for i, row in datos.iterrows():
                    opciones = [row['Respuesta Correcta'], row['Opción 1'], row['Opción 2'], row['Opción 3']]
                    random.shuffle(opciones)
                    opciones_random[i] = opciones
                st.session_state['opciones_random'] = opciones_random
            
        
            st.markdown("Responde todas las preguntas y presiona **Siguiente** para ver los resultados.")
            
            # Usar un formulario para agrupar todas las preguntas
            with st.form("quiz_form"):
                for i, row in datos.iterrows():
                    st.markdown(f"### Pregunta {i+1} de {len(datos)}")
                    
                    # Mostrar la pregunta en el idioma seleccionado
                    if st.session_state['idioma_seleccionado'] == "Español":
                        st.markdown(f"**Ejercicio:** {row['Ejercicio (Español)']}")
                    else:
                        st.markdown(f"**Esercizio:** {row['Ejercicio (Italiano)']}")
                    
                    # Mostrar las opciones barajadas previamente
                    opciones = st.session_state['opciones_random'][i]
                    
                    # Inicializar la respuesta en session_state si no existe
                    if f"pregunta_{i}" not in st.session_state:
                        st.session_state[f"pregunta_{i}"] = None
                    
                    # Widget de selección (sin opción preseleccionada)
                    respuesta = st.radio(
                        "Selecciona una opción:",
                        opciones,
                        index=None,  # Ninguna opción preseleccionada
                        key=f"radio_{i}"
                    )
                    
                    # Actualizar el estado de la sesión con la respuesta seleccionada
                    st.session_state[f"pregunta_{i}"] = respuesta
                    st.write("---")
                
                submit = st.form_submit_button("Siguiente")
            
            # Al enviar el formulario, se validan todas las respuestas
            if submit:
                correctas = 0
                st.markdown("## Resultados")
                for i, row in datos.iterrows():
                    user_answer = st.session_state.get(f"pregunta_{i}")
                    correct_answer = row['Respuesta Correcta']
                    if user_answer is None:
                        st.warning(f"**Pregunta {i+1}:** No seleccionaste ninguna opción.")
                    elif user_answer == correct_answer:
                        correctas += 1
                        st.success(f"**Pregunta {i+1}:** Correcto")
                    else:
                        st.error(
                            f"**Pregunta {i+1}:** Incorrecto  \n"
                            f"Tu respuesta: *{user_answer}*  \n"
                            f"Respuesta correcta: *{correct_answer}*"
                        )
                puntaje = (correctas / len(datos)) * 10
                st.subheader(f"Puntaje final: {puntaje:.1f} de 10")
                
                if st.button("Reiniciar Quiz"):
                    reiniciar_quiz()
                    st.rerun()

if __name__ == "__main__":
    main()
