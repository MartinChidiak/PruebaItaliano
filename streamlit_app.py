import pandas as pd
import random
import streamlit as st

@st.cache_data
def cargar_datos(ruta_archivo, solapa):
    return pd.read_excel(ruta_archivo, sheet_name=solapa)

def reiniciar_quiz():
    for key in ['tema_seleccionado', 'datos', 'opciones_random', 'respuestas']:
        if key in st.session_state:
            del st.session_state[key]

def main():
    st.title("Quiz de Italiano")
    
    ruta_archivo = 'quiz_italiano.xlsx'
    
    try:
        solapas = pd.ExcelFile(ruta_archivo).sheet_names
    except Exception as e:
        st.error(f"Error al cargar el archivo Excel: {e}")
        return
    
    if 'tema_seleccionado' not in st.session_state:
        st.write("### Seleccione el tema a estudiar:")
        tema = st.selectbox("Selecciona un tema:", solapas)
        if st.button("Seleccionar tema"):
            st.session_state['tema_seleccionado'] = tema
            st.session_state['respuestas'] = {}  
            st.rerun()
    else:
        if st.button("Cambiar tema"):
            reiniciar_quiz()
            st.rerun()
        
        if 'datos' not in st.session_state:
            datos = cargar_datos(ruta_archivo, st.session_state['tema_seleccionado'])
            st.session_state['datos'] = datos

        datos = st.session_state['datos']
        
        if len(datos) == 0:
            st.warning("No hay preguntas disponibles en este tema.")
            return
        
        if 'opciones_random' not in st.session_state:
            opciones_random = {}
            for i, row in datos.iterrows():
                opciones = [row['Respuesta Correcta'], row['Opción 1'], row['Opción 2'], row['Opción 3']]
                random.shuffle(opciones)
                opciones_random[i] = opciones
            st.session_state['opciones_random'] = opciones_random

        st.markdown("## Quiz")
        
        with st.form("quiz_form"):
            st.write("Formulario iniciado")  # Depuración
            for i, row in datos.iterrows():
                st.markdown(f"### Pregunta {i+1} de {len(datos)}")
                st.markdown(f"**Ejercicio (Español):** {row['Ejercicio (Español)']}")
                st.markdown(f"**Ejercicio (Italiano):** {row['Ejercicio (Italiano)']}")
                
                opciones = st.session_state['opciones_random'][i]
                respuesta = st.radio("Selecciona una opción:", opciones, 
                                     index=None if f"pregunta_{i}" not in st.session_state['respuestas'] 
                                     else opciones.index(st.session_state['respuestas'][f"pregunta_{i}"]),
                                     key=f"pregunta_{i}")
            
            submit = st.form_submit_button("Siguiente")

        if submit:
            st.session_state['respuestas'] = {f"pregunta_{i}": st.session_state[f"pregunta_{i}"] for i in range(len(datos))}
            st.rerun()

        if 'respuestas' in st.session_state and len(st.session_state['respuestas']) == len(datos):
            correctas = 0
            st.markdown("## Resultados")
            for i, row in datos.iterrows():
                user_answer = st.session_state['respuestas'].get(f"pregunta_{i}")
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
                st.rerun()

if __name__ == "__main__":
    main()
