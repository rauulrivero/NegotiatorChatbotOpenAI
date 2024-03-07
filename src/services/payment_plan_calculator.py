import json

class PaymentPlanCalculator:
    def __init__(self, crud_service):
        self.crud_service = crud_service
        
    def calculate_payment_plan(self, email, proposed_maximum_period_months, debt_id, proposed_monthly_payment):
        debts = self.crud_service.get_debts_by_user_email(email)
        if debts is None:
            return json.dumps({"error": "Este usuario no tiene deudas"})
        
        debt = self.crud_service.get_debt_by_id(debt_id)
        if debt is None:
            return json.dumps({"error": "No tiene ninguna deuda con esa cantidad total de deuda."})
        
        total_debt = debt.total_debt
        minimum_accepted_payment = debt.minimum_accepted_payment
        maximum_period_months = debt.maximum_period_months

        if proposed_maximum_period_months is None:
            return json.dumps({"error": "El número máximo de meses permitidos para pagar su deuda es requerido."})
        
        if id is None:
            return json.dumps({"error": "El id de deuda no existe."})
        
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

    
    