import pandas as pd
import random
import streamlit as st

# Función para cargar datos desde un archivo .txt (cacheada)
@st.cache
def cargar_datos(ruta_archivo):
    return pd.read_csv(ruta_archivo)

# Función para reiniciar el quiz (limpiar session_state)
def reiniciar_quiz():
    for key in ['tema_seleccionado', 'datos', 'opciones_random']:
        if key in st.session_state:
            del st.session_state[key]

def main():
    st.title("Quiz de Italiano")
    
    ruta_archivo = 'preguntas_italiano.txt'  # Cambia aquí el nombre del archivo .txt
    
    # Cargar los datos del archivo .txt
    try:
        datos = cargar_datos(ruta_archivo)
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
        
        # Usar un formulario para agrupar todas las preguntas
        with st.form("quiz_form"):
            for i, row in datos.iterrows():
                st.markdown(f"### Pregunta {i+1} de {len(datos)}")  # Muestra el número de pregunta y el total
                st.markdown(f"**Pregunta:** {row['Pregunta']}")
                
                # Mostrar las opciones barajadas previamente
                opciones = st.session_state['opciones_random'][i]
                st.radio("Selecciona una opción:", opciones, key=f"pregunta_{i}")
                st.write("---")
            
            submit = st.form_submit_button("Siguiente")
        
        # Al enviar el formulario, se validan todas las respuestas
        if submit:
            correctas = 0
            st.markdown("## Resultados")
            for i, row in datos.iterrows():
                user_answer = st.session_state.get(f"pregunta_{i}")
                correct_answer = row['Respuesta Correcta']
                if user_answer == correct_answer:
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
                return

if __name__ == "__main__":
    main()
