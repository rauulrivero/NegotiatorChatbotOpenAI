import streamlit as st
import json
from model import detect_function, function_calling


# Configurar la interfaz web con Streamlit
def main():
    st.title("Calculadora de Pagos")

    # Entrada del usuario: prompt
    user_prompt = st.text_area("Introduce tu consulta aquí:", """
    Soy un deudor que debe $1200 y quiere pagarlo en 12 meses. Estoy sugiriendo un pago mensual de $130.
    ¿Puedes verificar si este plan de pago es factible o decirme la cantidad mínima que necesitan pagar cada mes para cumplir con el plazo de 12 meses? 
    Mi correo electrónico es helloworld@singularfactory.es.
    """)

    # Botón para ejecutar la consulta
    if st.button("Enviar"):
        # Detectar la función que debe llamar el modelo
        output = detect_function(user_prompt)
        chosen_function = eval(output.function_call.name)
        
        # Llamar a la función detectada y obtener la respuesta
        params = json.loads(output.function_call.arguments)
        booking = chosen_function(**params)
        
        # Interactuar con el modelo utilizando la función detectada
        output = function_calling(user_prompt, output.function_call.name, booking.content)
        
        # Mostrar la respuesta del modelo
        st.write("RESPUESTA IA:", output.content)

if __name__ == "__main__":
    main()