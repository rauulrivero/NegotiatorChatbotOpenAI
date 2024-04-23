import requests
import streamlit as st

class StreamlitApp:

    def run(self):
        def clear_chat_history():
            st.session_state.messages = []
            requests.post('http://localhost:5000/clear_chat_history')

        st.title('🤖💬 SF OpenAI Chatbot')

        with st.sidebar:
            st.title('🔐 Iniciar Sesión')
            email = st.text_input('Email')
            password = st.text_input('Contraseña', type='password')
            login_button = st.button('Iniciar Sesión')

            if login_button:
                auth = requests.post('http://localhost:5000/login', json={'email': email, 'password': password})

                if auth.status_code == 200:
                    st.session_state['user'] = {'email': email, 'password': password}
                    st.success('¡Inicio de sesión exitoso!')
                else:
                    st.error('Nombre de usuario o contraseña incorrectos')
          
                
                        

            st.title('🤖💬 SF OpenAI Chatbot')
            st.sidebar.info("Este chatbot utiliza el modelo de lenguaje GPT-4 de OpenAI para responder a tus preguntas. ¡Pruébalo!")

            api_key = st.text_input('Introduce tu API key de OpenAI', type='password')
            if api_key:
                api_response = requests.post('http://localhost:5000/set_api_key', json={'api_key': api_key})
                st.session_state['openai_api_key'] = api_key

                if api_response.status_code == 200:
                    st.success('API key guardada con éxito')
                if api_response.status_code == 400:
                    st.error('Por favor, introduce una API key de OpenAI válida')


                st.sidebar.button('Limpiar chat', on_click=clear_chat_history)

        if "messages" not in st.session_state:
            st.session_state.messages = []

        assistant_message = "¡Hola! Soy el DebtNegotiationBot, tu asistente personal para la negociación de deudas. ¿En qué puedo ayudarte hoy?"

        st.markdown(assistant_message)

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["role"] != "system":
                    st.markdown(message["content"])

        if prompt := st.chat_input("Escribe aquí..."):

            if not "user" in st.session_state:
                st.error('Por favor, inicia sesión para poder usar el chatbot')
            elif not "openai_api_key" in st.session_state:
                st.error('Por favor, introduce tu API key de OpenAI para poder usar el chatbot')
            else:
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                

                with st.chat_message("assistant"):
                    typing_message = st.empty()  
                    typing_message.text("Typing...")  

                    response = requests.post('http://localhost:5000/ask_assistant', json={'message': prompt}).json()['response']

                    typing_message.empty() 
                
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
