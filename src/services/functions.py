import json

class FunctionsCall:
    def __init__(self, crud_service, auth):
        self.crud_service = crud_service
        self.auth = auth
        self.functions_description = [
            {
                "name": "calculate_payment_plan",
                "description": "Calculates a payment plan to settle a debt within a specific period for a given user, considering the proposed total debt.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "proposed_maximum_period_months": {
                            "type": "number",
                            "description": "The maximum number of months allowed to settle the debt as proposed by the user."
                        },
                        "debt_id": {
                            "type": "number",
                            "description": "The ID of the debt that the debtor wants to inquire about."
                        },
                        "proposed_monthly_payment": {
                            "type": "number",
                            "description": "The amount that the debtor proposes to pay each month."
                        }
                    },
                    "required": ["proposed_maximum_period_months", "debt_id", "proposed_monthly_payment"]
                }
            },
            {
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
        ]
  
    def calculate_payment_plan(self, proposed_maximum_period_months, debt_id, proposed_monthly_payment):
        email = self.auth.get_user_email()
        debts = self.crud_service.get_debts_by_user_email(email)
        if debts is None:
            return json.dumps({"error": "Este usuario no tiene deudas"})
        
        debt = self.crud_service.get_debt_by_id(debt_id)
        if debt is None:
            return json.dumps({"error": "No tiene ninguna deuda con esa cantidad total de deuda."})
        
        total_debt = debt.total_debt
        minimum_accepted_payment = debt.minimum_accepted_payment
        maximum_period_months = debt.maximum_period_months
        debt_id = debt.id

        if proposed_maximum_period_months is None:
            return json.dumps({"error": "El número máximo de meses permitidos para pagar su deuda es requerido."})
        
        if debt_id is None:
            return json.dumps({"error": "El id de deuda no existe."})
        
        if email is None:
            return json.dumps({"error": "Por favor, primero inicie sesión."})
        
        if proposed_monthly_payment is None:
            return json.dumps({"error": "El pago mensual propuesto es requerido."})
        
        if proposed_monthly_payment < minimum_accepted_payment:
            return json.dumps({
                "error": f"El pago propuesto es inferior al minimo aceptable. No se puede calcular un plan de pago. El pago mínimo aceptado es de ${minimum_accepted_payment}."
            })
        
        if proposed_maximum_period_months > maximum_period_months:
            return json.dumps({
                "error": f"El número máximo de meses permitido para pagar su deuda es de {maximum_period_months} meses."
            })
        
        remaining_debt = total_debt
        months = 0
    
        while remaining_debt >= proposed_monthly_payment and months < proposed_maximum_period_months:
            months += 1
            remaining_debt -= proposed_monthly_payment

        if remaining_debt <= 0:
            return json.dumps({
                "message": f"Si pagas ${proposed_monthly_payment} cada mes, cubririas la deuda de ${total_debt} en {months} meses."
            })
        else:
            months += 1
            last_payment = remaining_debt
            return json.dumps({
                "message": f"Si pagas ${proposed_monthly_payment} cada mes, cubririas la mayor parte de la deuda de ${total_debt} en {months - 1} meses. En el mes {months}, te quedaria un pago final de ${last_payment} para saldar completamente la deuda."
            })

    
    def get_all_debts(self):
        user_email = self.auth.get_user_email()
        debts = self.crud_service.get_debts_by_user_email(user_email)
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
    
    def get_functions_description(self):
        return self.functions_description
    
    