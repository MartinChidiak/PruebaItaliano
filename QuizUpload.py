import pandas as pd
import random
import streamlit as st

# Function to load data from a .txt file (cached using st.cache_data)
@st.cache_data
def cargar_datos(archivo):
    if archivo is not None:
        try:
            return pd.read_csv(archivo, sep="\t")  # Adjust the separator as needed
        except Exception as e:
            st.error(f"Error reading the file: {e}")
            return None
    return None

# Function to reset the quiz (clear session_state)
def reiniciar_quiz():
    for key in ['tema_seleccionado', 'datos', 'opciones_random']:
        if key in st.session_state:
            del st.session_state[key]

# File upload section
uploaded_file = st.file_uploader("Upload a TXT file", type=["txt"])
if uploaded_file is None:
    st.warning("Please upload a TXT file to proceed.")
    st.warning("It must maintain the exact structure: Category,Question,Correct Answer,Incorrect 1,Incorrect 2,Incorrect 3.")
else:
    try:
        datos = cargar_datos(uploaded_file)
        if datos is None or datos.empty:
            st.error("The file is empty or invalid.")
        else:
            # Proceed with the main application logic only if data loading succeeds
            def main():
                st.title("Italian Quiz")

                # If no topic has been selected, show the selection
                if 'tema_seleccionado' not in st.session_state:
                    st.write("### Select the topic to study:")
                    temas = datos['Categoría'].unique()  # Get unique categories as topics
                    tema = st.selectbox("Select a topic:", temas)
                    if st.button("Select topic"):
                        st.session_state['tema_seleccionado'] = tema
                else:
                    # Button to change topic (resets the quiz)
                    if st.button("Change topic"):
                        reiniciar_quiz()
                        return  # Restart app after clearing state

                    # Filter data according to selected topic
                    if 'datos' not in st.session_state:
                        datos_filtrados = datos[datos['Categoría'] == st.session_state['tema_seleccionado']].reset_index(drop=True)
                        st.session_state['datos'] = datos_filtrados

                    datos = st.session_state['datos']

                    # Pre-calculate and store each question's options randomly
                    if 'opciones_random' not in st.session_state:
                        opciones_random = {}
                        for i, row in datos.iterrows():
                            opciones = [row['Respuesta Correcta'], row['Incorrecta 1'], row['Incorrecta 2'], row['Incorrecta 3']]
                            random.shuffle(opciones)
                            opciones_random[i] = opciones
                        st.session_state['opciones_random'] = opciones_random

                    st.markdown("## Quiz")
                    st.markdown("Answer all questions and press **Next** to see the results.")

                    with st.form("quiz_form"):
                        idx = 1
                        for index, row in datos.iterrows():
                            st.markdown(f"### Question {idx} of {len(datos)}")
                            st.markdown(f"**Question:** {row['Pregunta']}")

                            opciones = st.session_state['opciones_random'][index]
                            st.radio("Select an option:", opciones, key=f"pregunta_{idx}")
                            st.write("---")
                            idx += 1

                        submit = st.form_submit_button("Next")

                    if submit:
                        correctas = 0
                        st.markdown("## Results")

                        idx = 1
                        for index, row in datos.iterrows():
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

                        puntaje = (correctas / len(datos)) * 10
                        st.subheader(f"Final Score: {puntaje:.1f} out of 10")

                        if st.button("Restart Quiz"):
                            reiniciar_quiz()
                            return

            if __name__ == "__main__":
                main()

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
