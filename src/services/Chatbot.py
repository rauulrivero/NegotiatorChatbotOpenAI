# chatbot.py
import openai

class Chatbot:
    def __init__(self):
        self.functions_description = [
        {
            "name": "calculate_payment_plan",
            "description": "Calcula un plan de pago para saldar una deuda dentro de un plazo específico para un usuario dado, considerando la cantidad total de deuda propuesta.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "El correo electrónico del usuario para el cual se realizará el cálculo de la deuda."
                    },
                    "proposed_maximum_period_months": {
                        "type": "number",
                        "description": "El número máximo de meses permitidos para saldar la deuda propuesto por el usuario."
                    },
                    "id_debt": {
                        "type": "number",
                        "description": "El id de la deuda que el deudor quiere consultar."
                    },
                    "proposed_monthly_payment": {
                        "type": "number",
                        "description": "La cantidad que el deudor propone pagar cada mes."
                    }
                },
                "required": ["email", "maximum_period_months", "proposed_total_debt", "proposed_monthly_payment"]
            }
        },
        {
        "name": "get_all_debts_by_user",
        "description": "Obtiene todas las deudas asociadas a un usuario dado su correo electrónico y devuelve los resultados en formato JSON.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_email": {
                    "type": "string",
                    "description": "El correo electrónico del usuario para el cual se obtendrán las deudas."
                }
            },
            "required": ["user_email"]
        },
        "return": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "El ID de la deuda."},
                    "total_debt": {"type": "integer", "description": "La cantidad total de la deuda."},
                    "maximum_period_months": {"type": "integer", "description": "El número máximo de meses permitidos para saldar la deuda."},
                    "minimum_accepted_payment": {"type": "float", "description": "El pago mínimo aceptado para la deuda."},
                    "user_email": {"type": "string", "description": "El correo electrónico del usuario asociado a la deuda."}
                }
            },
            "description": "Una lista de todas las deudas asociadas al usuario, cada una representada como un objeto JSON."
        }
    }
    ]
        
    def detect_function(self, prompt, openai_apikey, model_name):
        """Give LLM a given prompt and get an answer."""
        openai.api_key = openai_apikey

        completion = openai.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],

            functions=self.functions_description,
            function_call="auto",  # specify the function call
        )

        output = completion.choices[0].message
        return output
    
    def function_calling(self, prompt, function, content, openai_apikey, model_name):
        """Give LLM a given prompt and get an answer."""
        openai.api_key = openai_apikey

        completion = openai.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt},
                    {"role":"function", "name": function, "content": content}],

            functions=self.functions_description,
            function_call="auto",  # specify the function call
        )

        output = completion.choices[0].message
        return output
    

    