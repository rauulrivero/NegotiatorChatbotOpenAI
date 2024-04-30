import streamlit as st

class StreamlitApp:


    def __init__(self, api_handler):
        self.api_handler = api_handler 

    def clear_chat_history(self):
        st.session_state.messages = []
        self.api_handler.post_request('clear_chat_history', {})

    def unlink_api_key(self):
        st.session_state.pop('openai_api_key')

    def display_login_section(self):
        email, password = st.text_input("Email"), st.text_input("Contraseña", type="password")
        if st.button("Iniciar sesión"):
            auth_response = self.api_handler.post_request("login", {"email": email, "password": password})
            if auth_response.status_code == 200:
                st.success("¡Inicio de sesión exitoso!")
                st.session_state["user"] = {"email": email, "password": password}
                st.rerun()
            else:
                st.error("No se ha podido iniciar sesión")

    def display_register_section(self):
        user_details = {
            "email": st.text_input("Email"),
            "password": st.text_input("Contraseña", type="password"),
            "name": st.text_input("Nombre"),
            "surname": st.text_input("Apellido"),
            "telephone": st.text_input("Teléfono"),
        }
        if st.button("Registrar"):
            reg_response = self.api_handler.post_request("create_user", user_details)
            if reg_response.status_code == 201:
                st.success("¡Usuario creado exitosamente!")
            elif reg_response.status_code == 409:
                st.error("El usuario ya existe")
            else:
                st.error("Error al crear el usuario. Por favor, verifica los datos ingresados.")


    def display_user_section(self):
        st.title('👤 Usuario')
        st.write(f"Email: {st.session_state['user']['email']}")
        if st.button("Cerrar Sesión"):
            self.api_handler.post_request("logout", {})
            st.session_state.pop("user")
            st.rerun()


    def run(self):

        st.title('🤖💬 SF OpenAI Chatbot')

        with st.sidebar:
    
            if 'user' not in st.session_state:
                st.title('🔐 Acceso')
                login_option = st.radio('Selecciona una opción', ['Iniciar Sesión', 'Registrarse'])

                if login_option == "Iniciar Sesión":
                    self.display_login_section()
                elif login_option == "Registrarse":
                    self.display_register_section()
            else:
                self.display_user_section()
                st.empty()


                st.title('🔑 API Key')
                if 'openai_api_key' not in st.session_state:
                    api_key = st.text_input('Introduce tu API key de OpenAI', type='password')
                    if api_key:
                        api_response = self.api_handler.post_request('set_api_key', {'api_key': api_key})
                        st.session_state['openai_api_key'] = api_key

                        if api_response.status_code == 200:
                            st.success('API key guardada con éxito')
                            st.rerun()
                        if api_response.status_code == 400:
                            st.error('Por favor, introduce una API key de OpenAI válida')
                else:
                    st.success('API key guardada con éxito, puedes procedeer a chatear con el bot.')
                    st.button('Desvincular API key', on_click=self.unlink_api_key)
                
                st.title('📝 Crear deuda')
                total_debt = st.number_input('Total de la deuda (euros)')
                maximum_period_months = st.number_input('Plazo máximo (meses)', step=1, min_value=1, value=1)

                debt_button = st.button('Crear deuda')

                if debt_button:
                    debt_response = self.create_debt(total_debt, maximum_period_months, st.session_state["user"]["email"])
                    if debt_response.status_code == 201:
                        st.success('Deuda creada exitosamente')
                    else:
                        st.error('Error al crear la deuda. Por favor, verifica los datos ingresados.')
                    
                st.empty()

                st.title('🗑️ Limpiar historial')
                st.sidebar.button('🔧Nuevo chat', on_click=self.clear_chat_history)                

                

            st.empty()
             


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

                    response = self.api_handler.post_request('ask_assistant', {'message': prompt}).json()['response']


                    typing_message.empty() 
                
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})



        
