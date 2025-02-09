#import streamlit as st

#st.title('🎈 App Name')

#st.write('Hello world!')


import pandas as pd
import random
import streamlit as st

# Cargar los datos desde Excel
def cargar_datos(ruta_archivo, solapa):
    df = pd.read_excel(ruta_archivo, sheet_name=solapa)
    return df

# Función principal
def main():
    st.title("Quiz de Italiano")
    
    ruta_archivo = 'quiz_italiano.xlsx'
    solapas = pd.ExcelFile(ruta_archivo).sheet_names
    
    if 'tema_seleccionado' not in st.session_state:
        st.session_state['tema_seleccionado'] = None
    
    if st.session_state['tema_seleccionado'] is None:
        st.write("Seleccione el tema a estudiar")
        solapa = st.selectbox("Selecciona un tema:", solapas)
        if st.button("Seleccionar tema"):
            st.session_state['tema_seleccionado'] = solapa
    else:
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
            
            if pregunta_num < len(datos):
                fila = datos.iloc[pregunta_num]
                st.write(f"Pregunta {pregunta_num + 1} de {len(datos)}")
                st.write(f"Ejercicio (Español): {fila['Ejercicio (Español)']}")
                st.write(f"Ejercicio (Italiano): {fila['Ejercicio (Italiano)']}")
                
                if not st.session_state['opciones']:
                    opciones = [fila['Respuesta Correcta'], fila['Opción 1'], fila['Opción 2'], fila['Opción 3']]
                    random.shuffle(opciones)
                    st.session_state['opciones'] = opciones
                else:
                    opciones = st.session_state['opciones']
                
                respuesta_usuario = st.radio("Selecciona una opción:", opciones)
                
                if st.button("Verificar"):
                    if not st.session_state['verificado']:
                        if respuesta_usuario == fila['Respuesta Correcta']:
                            st.success("¡Correcto!\n\n¡Bien hecho!")
                            st.session_state['correctas'] += 1
                        else:
                            st.error(f"Incorrecto.\n\nLa respuesta correcta era: {fila['Respuesta Correcta']}")
                        
                        st.session_state['verificado'] = True
                
                if st.session_state['verificado'] and st.button("Siguiente"):
                    st.session_state['pregunta_num'] += 1
                    st.session_state['opciones'] = []
                    st.session_state['verificado'] = False
            else:
                puntaje = (correctas / len(datos)) * 10
                st.write(f"Has completado todas las preguntas.\n\nRespuestas correctas: {correctas} de {len(datos)}\n\nPuntaje: {puntaje:.1f} de 10")
                st.session_state['quiz_iniciado'] = False

if __name__ == "__main__":
    main()
