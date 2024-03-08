import json

class FunctionsCall:
    def __init__(self, crud_service, auth):
        self.crud_service = crud_service
        self.auth = auth
        self.tools_list = [
            {
                "type": "function",
                "function": {
                    "name": "validate_maximum_period",
                    "description": "Validates if the proposed maximum period is acceptable for a debt.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "debt_id": {
                                "type": "number",
                                "description": "The ID of the debt."
                            },
                            "proposed_maximum_period_months": {
                                "type": "number",
                                "description": "The proposed maximum period in months."
                            }
                        },
                        "required": ["debt_id", "proposed_maximum_period_months"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "validate_proposed_payment",
                    "description": "Validates if the proposed monthly payment is acceptable for a debt.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "debt_id": {
                                "type": "number",
                                "description": "The ID of the debt."
                            },
                            "proposed_monthly_payment": {
                                "type": "number",
                                "description": "The proposed monthly payment amount."
                            }
                        },
                        "required": ["debt_id", "proposed_monthly_payment"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_all_debts",
                    "description": "Obtains all debts associated with a user given their email address and returns the results in JSON format.",
                    "parameters": {},
                    "return": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer", "description": "The ID of the debt."},
                                "total_debt": {"type": "integer", "description": "The total amount of the debt."},
                                "maximum_period_months": {"type": "integer", "description": "The maximum number of months allowed to settle the debt."},
                                "minimum_accepted_payment": {"type": "float", "description": "The minimum accepted payment for the debt."},
                                "user_email": {"type": "string", "description": "The email address of the user associated with the debt."}
                            }
                        },
                        "description": "A list of all debts associated with the user, each represented as a JSON object."
                    }
                }
            }
        ]

        self.system_message = """Eres un chatbot ChatGPT normal, que cuenta con las siguientes funciones:
        - validate_maximum_period: Valida si el periodo máximo propuesto es aceptable para una deuda.
        - validate_proposed_payment: Valida si el pago mensual propuesto es aceptable para una deuda.
        - get_all_debts: Obtiene todas las deudas asociadas a un usuario dado su correo electrónico y devuelve los resultados en formato JSON.
        """

    def _validate_input(self, debt_id, email):
        if debt_id is None:
            return json.dumps({"error": "El id de deuda no existe."})
        if email is None:
            return json.dumps({"error": "Por favor, primero inicie sesión."})
        return None

    def validate_maximum_period(self, debt_id, proposed_maximum_period_months):
        email = self.auth.get_user_email()
        validation_error = self._validate_input(debt_id, email)
        if validation_error:
            return validation_error

        debt = self.crud_service.get_debt_by_id(debt_id)
        if debt is None:
            return json.dumps({"error": "No tiene ninguna deuda con ese ID."})
        
        maximum_period_months = debt.maximum_period_months
        if proposed_maximum_period_months > maximum_period_months:
            return json.dumps({
                "error": f"El número máximo de meses permitido para pagar su deuda es de {maximum_period_months} meses."
            })
        return json.dumps({"message": "El periodo propuesto es válido."})

    def validate_proposed_payment(self, debt_id, proposed_monthly_payment):
        email = self.auth.get_user_email()
        validation_error = self._validate_input(debt_id, email)
        if validation_error:
            return validation_error

        debt = self.crud_service.get_debt_by_id(debt_id)
        if debt is None:
            return json.dumps({"error": "No tiene ninguna deuda con ese ID."})
        
        minimum_accepted_payment = debt.minimum_accepted_payment
        if proposed_monthly_payment < minimum_accepted_payment:
            return json.dumps({
                "error": f"El pago propuesto es inferior al mínimo aceptable. El pago mínimo aceptado es de {minimum_accepted_payment}€."
            })
        return json.dumps({"message": "El pago propuesto es válido."})


    
    def get_all_debts(self):

        user_email = self.auth.get_user_email()
        if user_email is None:
            return json.dumps({"error": "Por favor, primero inicie sesión."})
       
        
        debts = self.crud_service.get_debts_by_user_email(user_email)
        if debts is None:
            return json.dumps({"error": "Este usuario no tiene deudas."})
        
        debts_data = []
        for debt in debts:
            debt_data = {
                "id": debt.id,
                "total_debt": debt.total_debt,
                "maximum_period_months": debt.maximum_period_months,
                "minimum_accepted_payment": debt.minimum_accepted_payment,
                "user_email": debt.user_email
            }
            debts_data.append(debt_data)
        return json.dumps(debts_data)
    
    
    
    def get_tools_list(self):
        return self.tools_list
    
    def get_functions_available(self):
        return {
            "validate_maximum_period": self.validate_maximum_period,
            "validate_proposed_payment" : self.validate_proposed_payment,
            "get_all_debts": self.get_all_debts,
        }
    
    def get_system_message(self):
        return self.system_message