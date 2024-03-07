import json
import openai
import streamlit as st
from src.services.CrudPsgService import CRUDService
from src.services.Chatbot import Chatbot
from src.services.functions import FunctionsCall

class StreamlitApp:
    def __init__(self, session, app, auth):
        self.openai_api_key = None
        self.model_name = None
        self.crud_service = CRUDService(session)
        self.auth = auth
        self.functions_call = FunctionsCall(self.crud_service, self.auth)
        self.chatbot = Chatbot(self.functions_call.get_functions_description())
        self.app = app

    def setgui(self):
        def clear_chat_history():
            st.session_state.messages = [
            {"role": "system", "content": system_message},
            ]

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
            st.sidebar.info("Este chatbot utiliza el modelo de lenguaje GPT-3.5 o GPT-4 de OpenAI para responder a tus preguntas. ¡Pruébalo!")

            self.openai_api_key = st.text_input('Intruduce tu API key de OpenAI', type='password')
            openai.api_key = self.openai_api_key

            if not (openai.api_key.startswith('sk-') and len(openai.api_key)==51):
                st.warning('Introduce tus credenciales', icon='⚠️')
            else:
                st.success('Puedes proceder a chatear', icon='👉')

            system_message = st.text_area(label='Mensaje de sistema:',
                                        height=180,
                                        placeholder='Instrucciones que complementan el comportamiento de tu modelo de fine-tuning. Ej: Responde siempre alegre.')

            st.session_state["openai_model"] = st.radio("Selecciona el modelo que deseas usar:", ("gpt-3.5-turbo", "gpt-4-turbo-preview"))
            st.sidebar.button('Limpiar chat', on_click=clear_chat_history)

        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "system", "content": system_message}]



    def run(self):
        self.setgui()

        openai.api_key = self.openai_api_key
        email = st.session_state['user']['email'] if 'user' in st.session_state else None
        password = st.session_state['user']['password'] if 'user' in st.session_state else None
        self.auth.set_user(email, password)


        system_message = "¡Hola! Soy el chatbot de OpenAI. Antes de chatear conmigo, por favor, inicia sesión, introduce tu apikey y selecciona el modelo que deseas usar."
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "system", "content": system_message}]

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
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
                    self.model_name = st.session_state["openai_model"]

        
                    output = self.chatbot.detect_function(prompt, self.openai_api_key, self.model_name)
                

                    if output.function_call is None:
                        message_placeholder = st.empty()
                        full_response = ""
                        model_name = st.session_state["openai_model"]
                        for response in openai.chat.completions.create(
                            model=model_name,
                            messages=[
                                {"role": m["role"], "content": m["content"]}
                                for m in st.session_state.messages
                            ],
                            stream=True
                        ):
                            full_response += str(response.choices[0].delta.content)
                            message_placeholder.markdown(full_response[:-4] + "▌")
                        message_placeholder.markdown(full_response[:-4])
                        st.session_state.messages.append({"role": "assistant", "content": full_response[:-4]})

                    else:

                        try:
                            params = json.loads(output.function_call.arguments)
                        except json.JSONDecodeError as e:
                            st.error(f"Error parsing JSON: {e}")
                            return

                        if output.function_call.name == "calculate_payment_plan":
                            with self.app.app_context():        
                                json_result = self.functions_call.calculate_payment_plan(**params)
                
                        elif output.function_call.name == "get_all_debts":
                            with self.app.app_context():
                                json_result = self.functions_call.get_all_debts(**params)

                        try:
                            output = self.chatbot.function_calling(prompt, output.function_call.name, json_result, self.openai_api_key, self.model_name)
                        except Exception as e:
                            st.error(f"Error calling function: {e}")
                            return
                        
                        response = output.content

                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
