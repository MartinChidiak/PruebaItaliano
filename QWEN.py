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
            # Iterar sobre las filas del DataFrame filtrado usando enumerate
            for idx, row in enumerate(datos.itertuples(index=False), start=1):  # Usamos itertuples para evitar problemas con índices
                st.markdown(f"### Pregunta {idx} de {len(datos)}")  # Numeración corregida
                st.markdown(f"**Pregunta:** {row.Pregunta}")  # Accedemos a los datos usando atributos
                
                # Mostrar las opciones barajadas previamente
                opciones = st.session_state['opciones_random'][idx - 1]  # Usamos idx - 1 como clave (basado en posición)
                st.radio("Selecciona una opción:", opciones, key=f"pregunta_{idx}")  # Usamos idx como clave única
                st.write("---")
            
            submit = st.form_submit_button("Siguiente")
        
        # Al enviar el formulario, se validan todas las respuestas
        if submit:
            correctas = 0
            st.markdown("## Resultados")
            for idx, row in enumerate(datos.itertuples(index=False), start=1):  # Iteramos nuevamente para mostrar resultados
                user_answer = st.session_state.get(f"pregunta_{idx}")  # Obtenemos la respuesta del usuario
                correct_answer = row.Respuesta_Correcta  # Accedemos a la respuesta correcta
                if user_answer == correct_answer:
                    correctas += 1
                    st.success(f"**Pregunta {idx}:** Correcto")
                else:
                    st.error(
                        f"**Pregunta {idx}:** Incorrecto  \n"
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
