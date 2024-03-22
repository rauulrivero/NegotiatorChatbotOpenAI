import openai
import streamlit as st

class StreamlitApp:
    def __init__(self, crud_service, chatbot, app, auth):
        self.openai_api_key = None
        self.crud_service = crud_service
        self.auth = auth
        self.chatbot = chatbot
        self.app = app


    def run(self):
        def clear_chat_history():
            st.session_state.messages = [
            {"role": "system", "content": system_message},
            ]
            self.chatbot.create_thread()

        st.title('🤖💬 SF OpenAI Chatbot')

        with st.sidebar:
            st.title('🔐 Iniciar Sesión')
            email = st.text_input('Email')
            password = st.text_input('Contraseña', type='password')
            login_button = st.button('Iniciar Sesión')

            if login_button:
                    
                with self.app.app_context():
                    if self.crud_service.validate_user(email, password):  
                        st.session_state['user'] = {'email': email, 'password': password}
                        st.success('¡Inicio de sesión exitoso!')
                    else:
                        st.error('Nombre de usuario o contraseña incorrectos')

            st.title('🤖💬 SF OpenAI Chatbot')
            st.sidebar.info("Este chatbot utiliza el modelo de lenguaje GPT-4 de OpenAI para responder a tus preguntas. ¡Pruébalo!")

            self.openai_api_key = st.text_input('Introduce tu API key de OpenAI', type='password')
            openai.api_key = self.openai_api_key

            if not (openai.api_key.startswith('sk-') and len(openai.api_key)==51):
                st.warning('Introduce tus credenciales', icon='⚠️')
            else:
                st.success('Puedes proceder a chatear', icon='👉')

            st.sidebar.button('Limpiar chat', on_click=clear_chat_history)


        self.chatbot.get_functions_call().set_debt_id(st.session_state.debt_id if 'debt_id' in st.session_state else None)
        openai.api_key = self.openai_api_key
        email = st.session_state['user']['email'] if 'user' in st.session_state else None
        password = st.session_state['user']['password'] if 'user' in st.session_state else None
        self.auth.set_user(email, password)

        system_message = self.chatbot.get_system_message()

       
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "system", "content": system_message}]

        assistant_message = "¡Hola! Soy el DebtNegotiationBot, tu asistente personal para la negociación de deudas. ¿En qué puedo ayudarte hoy?"

        st.markdown(assistant_message)

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["role"] != "system":
                    st.markdown(message["content"])

        if prompt := st.chat_input("Escribe aquí..."):

            if not (openai.api_key.startswith('sk-') and len(openai.api_key)==51):
                st.error("Por favor, introduce tu API key de OpenAI")
            elif self.auth.get_user_email() is None:
                st.error("Por favor, inicia sesión")
            else:
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                

                with st.chat_message("assistant"):
                    typing_message = st.empty()  
                    typing_message.text("Typing...")  

                    response = self.chatbot.ask_assistant(self.openai_api_key, {"role": "user", "content": prompt})

                    typing_message.empty() 

                    if self.chatbot.get_functions_call().get_debt_id() is not None:
                        st.session_state.debt_id = self.chatbot.get_functions_call().get_debt_id()
                
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
