import pandas as pd
import random
import streamlit as st

# 1. Uso de caché para cargar los datos desde Excel
@st.cache_data
def cargar_datos(ruta_archivo, solapa):
    return pd.read_excel(ruta_archivo, sheet_name=solapa)

# Función para reiniciar el quiz
def reiniciar_quiz():
    for key in ['tema_seleccionado', 'datos', 'pregunta_num', 'correctas', 'quiz_iniciado', 'opciones', 'verificado']:
        if key in st.session_state:
            del st.session_state[key]

def main():
    st.title("Quiz de Italiano")
    
    ruta_archivo = 'quiz_italiano.xlsx'
    
    # Manejo de errores al cargar el archivo Excel
    try:
        solapas = pd.ExcelFile(ruta_archivo).sheet_names
    except Exception as e:
        st.error(f"Error al cargar el archivo Excel: {e}")
        return

    # Inicializar la selección de tema si no existe
    if 'tema_seleccionado' not in st.session_state:
        st.session_state['tema_seleccionado'] = None

    # Si aún no se ha seleccionado un tema
    if st.session_state['tema_seleccionado'] is None:
        st.write("Seleccione el tema a estudiar:")
        tema = st.selectbox("Selecciona un tema:", solapas)
        if st.button("Seleccionar tema"):
            st.session_state['tema_seleccionado'] = tema
    else:
        # Botón para cambiar de tema (reinicia el quiz)
        if st.button("Cambiar tema"):
            reiniciar_quiz()
            st.experimental_rerun()

        # Inicializar variables del quiz en session_state
        if 'datos' not in st.session_state:
            datos = cargar_datos(ruta_archivo, st.session_state['tema_seleccionado'])
            st.session_state['datos'] = datos
            st.session_state['pregunta_num'] = 0
            st.session_state['correctas'] = 0
            st.session_state['quiz_iniciado'] = True
            st.session_state['opciones'] = []
            st.session_state['verificado'] = False
        
        if st.session_state['quiz_iniciado']:
            datos = st.session_state['datos']
            pregunta_num = st.session_state['pregunta_num']
            correctas = st.session_state['correctas']
            
            # Mostrar las preguntas mientras haya preguntas disponibles
            if pregunta_num < len(datos):
                fila = datos.iloc[pregunta_num]
                st.write(f"**Pregunta {pregunta_num + 1} de {len(datos)}**")
                st.markdown(f"**Ejercicio (Español):** {fila['Ejercicio (Español)']}")
                st.markdown(f"**Ejercicio (Italiano):** {fila['Ejercicio (Italiano)']}")
                
                # Preparar y mostrar las opciones
                if not st.session_state['opciones']:
                    opciones = [fila['Respuesta Correcta'], fila['Opción 1'], fila['Opción 2'], fila['Opción 3']]
                    random.shuffle(opciones)
                    st.session_state['opciones'] = opciones
                else:
                    opciones = st.session_state['opciones']
                
                respuesta_usuario = st.radio("Selecciona una opción:", opciones, key=f"pregunta_{pregunta_num}")
                
                # Verificar la respuesta solo si aún no se ha verificado
                if not st.session_state.get('verificado', False):
                    if st.button("Verificar"):
                        # Lógica de verificación...
                        if respuesta_usuario == fila['Respuesta Correcta']:
                            st.success("¡Correcto! ¡Bien hecho!")
                            st.session_state['correctas'] += 1
                        else:
                            st.error(f"Incorrecto. La respuesta correcta era: {fila['Respuesta Correcta']}")
                        st.session_state['verificado'] = True
                        st.experimental_rerun()  # Fuerza un rerun para actualizar la UI inmediatamente.
                else:
                    if st.button("Siguiente"):
                        st.session_state['pregunta_num'] += 1
                        st.session_state['opciones'] = []
                        st.session_state['verificado'] = False
                        st.experimental_rerun()

            else:
                # Mostrar el resultado final del quiz
                puntaje = (correctas / len(datos)) * 10
                st.success(f"Has completado el quiz.\n\nRespuestas correctas: {correctas} de {len(datos)}\nPuntaje: {puntaje:.1f} de 10")
                if st.button("Reiniciar Quiz"):
                    reiniciar_quiz()
                    st.experimental_rerun()

if __name__ == "__main__":
    main()
