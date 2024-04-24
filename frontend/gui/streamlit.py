import requests
import streamlit as st

class StreamlitApp:

    def run(self):
        def clear_chat_history():
            st.session_state.messages = []
            requests.post('http://localhost:5000/clear_chat_history')

        def create_user(email, password, name, surname, telephone):
            user_data = {
                "email": email,
                "password": password,
                "name": name,
                "surname": surname,
                "telephone": telephone,
            }
            response = requests.post('http://localhost:5000/create_user', json=user_data)
            return response
        
        def login_user(email, password):
            auth_response = requests.post('http://localhost:5000/login', json={'email': email, 'password': password})
            return auth_response
        
        def logout_user():
            requests.post('http://localhost:5000/logout')
            st.session_state.pop('user')

        def create_debt(total_debt, maximum_period_months, user_email):
            debt_data = {
                "total_debt": total_debt,
                "maximum_period_months": maximum_period_months,
                "user_email": user_email,
            }
            
            response = requests.post('http://localhost:5000/create_debt', json=debt_data)
            return response

        def delete_api_key():
            st.session_state.pop('openai_api_key')

        st.title('🤖💬 SF OpenAI Chatbot')

        with st.sidebar:

            
            if 'user' not in st.session_state:
                st.title('🔐 Acceso')
                login_option = st.radio('Selecciona una opción', ['Iniciar Sesión', 'Registrarse'])

                if login_option == 'Iniciar Sesión':
                    email = st.text_input('Email')
                    password = st.text_input('Contraseña', type='password')
                    login_button = st.button('Iniciar Sesión')

                    if login_button:
                        auth_response = login_user(email, password)
                        if auth_response.status_code == 200:
                            st.session_state['user'] = {'email': email, 'password': password}
                            st.success('¡Inicio de sesión exitoso!')
                            st.rerun()
                        else:
                            st.error('Nombre de usuario o contraseña incorrectos')

                elif login_option == 'Registrarse':
                    st.title('🔐 Acceso')
                    reg_email = st.text_input('Email')
                    reg_password = st.text_input('Contraseña', type='password')
                    reg_name = st.text_input('Nombre')
                    reg_surname = st.text_input('Apellido')
                    reg_telephone = st.text_input('Teléfono')
                    register_button = st.button('Registrarse')

                    if register_button:
                        reg_response = create_user(reg_email, reg_password, reg_name, reg_surname, reg_telephone)

                        if reg_response.status_code == 201:
                            st.success('¡Usuario creado exitosamente!')
                        elif reg_response.status_code == 409:
                            st.error('El usuario ya existe')
                        else:
                            st.error('Error al crear el usuario. Por favor, verifica los datos ingresados.')
            
            else:
                st.title('👤 Usuario')
                st.write(f'Email: {st.session_state["user"]["email"]}')
                st.button('Cerrar Sesión', on_click=logout_user)

                st.empty()

                st.title('🔑 API Key')
                if 'openai_api_key' not in st.session_state:
                    api_key = st.text_input('Introduce tu API key de OpenAI', type='password')
                    if api_key:
                        api_response = requests.post('http://localhost:5000/set_api_key', json={'api_key': api_key})
                        st.session_state['openai_api_key'] = api_key

                        if api_response.status_code == 200:
                            st.success('API key guardada con éxito')
                            st.rerun()
                        if api_response.status_code == 400:
                            st.error('Por favor, introduce una API key de OpenAI válida')
                else:
                    st.success('API key guardada con éxito, puedes procedeer a chatear con el bot.')
                    st.button('Eliminar API key', on_click=delete_api_key)
                
                st.title('📝 Crear deuda')
                total_debt = st.number_input('Total de la deuda (euros)')
                maximum_period_months = st.number_input('Plazo máximo (meses)', step=1, min_value=1, value=1)

                debt_button = st.button('Crear deuda')

                if debt_button:
                    debt_response = create_debt(total_debt, maximum_period_months, st.session_state["user"]["email"])
                    if debt_response.status_code == 201:
                        st.success('Deuda creada exitosamente')
                    else:
                        st.error('Error al crear la deuda. Por favor, verifica los datos ingresados.')
                    
                st.empty()

                # ponle un emoticono al titulo de debajo, que sea limpiar el historial del chat
                st.title('🗑️ Limpiar historial')
                st.sidebar.button('🔧Nuevo chat', on_click=clear_chat_history)                

                

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

                    response = requests.post('http://localhost:5000/ask_assistant', json={'message': prompt}).json()['response']

                    typing_message.empty() 
                
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})


        
