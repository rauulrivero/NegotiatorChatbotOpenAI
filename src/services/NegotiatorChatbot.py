import json
from src.services.tools.assistant_tools import Tooling

class Negotiator:
    def __init__(self, crud_service, auth):
        self.current_price = None
        self.max_discount = 20  
        self.current_discount = 5
        self.incremental_discount = 5  
        self.max_attempts = 10  
        self.current_attempts = 0  
        self.auth = auth
        self.crud_service = crud_service
        self.debt_id = None

        self.functions_available = { 
                "set_debt_id": self.set_debt_id,
                "manage_negotiation": self.manage_negotiation,
                "get_all_debts": self.get_all_debts,
                "calculate_payment_plan": self.calculate_payment_plan,
                "proposed_payment_plan": self.propose_payment_plan,
                "propose_partial_immediate_payment": self.propose_partial_immediate_payment
            }

        self.system_message = """
            Hola, soy Pedro, especialista en ofrecer descuentos por pagos inmediatos y en negociar planes de pagos personalizados, utilizando el euro como moneda. Estoy aquí para asistirte con una variedad de servicios enfocados en la gestión de deudas. Además de mis servicios de negociación, tengo acceso a información sobre los festivos de apertura de Las Arenas, aunque este detalle es adicional y no esencial para nuestras interacciones directas.

            Funcionalidades Disponibles:

            - set_debt_id: Establece el ID de la deuda actual para la negociación, asegurando que todas las operaciones subsiguientes se realicen con respecto a la deuda correcta.
            - get_all_debts: Muestra todas las deudas asociadas al usuario, facilitando la selección para negociar.
            - calculate_payment_plan: Calcula un plan de pago personalizado basado en propuestas específicas del usuario.
            - manage_negotiation: Maneja el proceso de negociación de deudas, permitiendo al usuario solicitar una oferta inmediata de pago, responder con una contraoferta, o recibir una propuesta inicial.
            - propose_payment_plan: Formula un plan de pago adaptado sin necesidad de entrada adicional del usuario.
            - propose_partial_immediate_payment: Calcula un plan de pago ajustado para el saldo restante tras un pago parcial inmediato.

            Mi objetivo es ayudarte a calcular un plan de pagos adaptado a tu situación financiera, evaluar contraofertas y ofrecer soluciones flexibles para la gestión eficiente de tu deuda. No aceptaré ninguna oferta sin la especificación clara de una de las funciones que tengo implementadas. Esto asegura que todas nuestras negociaciones se basen en servicios específicos que puedo ofrecer, optimizando el proceso para ambas partes.

            Al final de nuestra interacción, te presentaré un resumen de las opciones disponibles, incluyendo la oferta de descuento por pago inmediato y un plan de pagos adaptado a tus necesidades. Tu información será revisada cuidadosamente, y serás contactado con cualquier propuesta de seguimiento.

            Gracias por tu tiempo, y espero poder ayudarte a aprovechar esta oportunidad para gestionar tu deuda con beneficios adicionales y un plan que se ajuste a tu situación financiera. Importante: Recuerda, antes de iniciar cualquier negociación, preguntar el ID de la deuda con la que vas a negociar.
            """
        
        
        tools_data = Tooling("src/services/tools/negotiator_tools.json").load_tools()

        self.tools_list = self._generate_tools_list(tools_data)



    def _generate_tools_list(self, tools_data):
        tools_list = []
        for tool_name, tool_info in tools_data.items():
            tool_dict = {
                "type": "function",
                "function": tool_info
            }
            tools_list.append(tool_dict)
        return tools_list

    def _increase_attempt_or_maxed_out(self):
        self.current_attempts += 1
        if self.current_attempts > self.max_attempts:
            return json.dumps({"error": "Límite de negociaciones alcanzadas."})
        elif self.current_attempts == self.max_attempts:
            return self._ultima_oferta()
        return None

    def _get_discounted_price(self):
        return int(self.current_price - (self.current_price * (self.current_discount / 100)))
  
    def _aumentar_oferta(self):
        if self.current_discount < self.max_discount:
            self.current_discount += self.incremental_discount
            self.current_discount = min(self.current_discount, self.max_discount)
        return None
    
    def _ultima_oferta(self):  
        self._aumentar_oferta()
        price = self._get_discounted_price()
        return json.dumps({"message": f"Mi última oferta es que te lo lleves a {price}€. ¿Aceptas?"})
    
    def _rechazar_oferta(self):
        price = self._get_discounted_price()
        return json.dumps({
            "message": f"No puedo aceptar tu oferta. Actualmente, podemos ofrecerte un descuento del {self.current_discount}% sobre el total de tu deuda, lo que deja el monto a pagar en {price}€. ¿Estás dispuesto a considerar esta oferta o puedes mejorar tu contraoferta?"
        })
 
    def _aceptar_oferta(self):
        return json.dumps({"message": f"¡Perfecto! Trato hecho. El precio final es de {self._get_discounted_price()}€."})
    
    def _get_min_price(self):
        return int(self.initial_price - (self.initial_price * (self.max_discount / 100)))
    
    def _validate_input(self, email):
        if self.debt_id is None:
            return json.dumps({"error": "El id de deuda no existe."})
        if email is None:
            return json.dumps({"error": "Por favor, primero inicie sesion."})
        return None
        

    def manage_negotiation(self, counteroffer=None, request_immediate_payment_offer=False):
        if self.debt_id is None:
            return json.dumps({"error": "Por favor, introduce un ID de deuda válido."})
        
        if self.current_price is None:       
            debt = self.crud_service.get_debt_by_id(self.debt_id)
            if debt is None:
                return json.dumps({"error": "No tiene ninguna deuda con ese ID."})
            else:
                self.current_price = self.initial_price = debt.total_debt

        if request_immediate_payment_offer:
            self._aumentar_oferta()
            offer = self._get_discounted_price()
            return json.dumps({"message": f"¿Qué te parece si saldas la deuda hoy mismo y se te aplica un {self.current_discount} con un monto total de {offer}€? ¿Aceptas?"})
        
        if counteroffer is not None:
            if type(counteroffer) not in [int, float]:
                return json.dumps({"error": "Por favor, introduce un número válido."})
            
            self._aumentar_oferta()
            response = self._increase_attempt_or_maxed_out()
            if response:
                return response

            if counteroffer < self._get_min_price():
                return self._rechazar_oferta()
            elif counteroffer >= self.current_price:
                return self._aceptar_oferta()
            else:
                price = self._get_discounted_price()
                return json.dumps({"message": f"Mi oferta es de un descuento del {self.current_discount}%, se te quedaría en {price}€. ¿Aceptas?"})

        offer = self._get_discounted_price()
        return json.dumps({"message": f"¿Qué te parece si saldas la deuda hoy mismo y se te aplica un {self.current_discount} con un monto total de {offer}€? ¿Aceptas?"})


    def get_all_debts(self):
        user_email = self.auth.get_user_email()
        if user_email is None:
            return json.dumps({"error": "Por favor, primero inicie sesion."})
       
        
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
    

    def calculate_payment_plan(self, proposed_maximum_period_months=None, proposed_monthly_payment=None):
        if self.debt_id is None:
            return json.dumps({"error": "Por favor, introduce un ID de deuda válido."})
        
        email = self.auth.get_user_email()
        debts = self.crud_service.get_debts_by_user_email(email)
        if debts is None:
            return json.dumps({"error": "Este usuario no tiene deudas"})

        debt = self.crud_service.get_debt_by_id(self.debt_id)
        if debt is None:
            return json.dumps({"error": "No existe una deuda con ese ID."})

        maximum_period_months = debt.maximum_period_months
        total_debt = debt.total_debt
        minimum_accepted_payment = debt.minimum_accepted_payment
        
        # Si solo se proporciona el pago mensual
        if proposed_monthly_payment is not None and proposed_maximum_period_months is None:
            if proposed_monthly_payment < minimum_accepted_payment:
                return json.dumps({"error": f"El pago propuesto es inferior al mínimo aceptable. El pago mínimo aceptado es de {minimum_accepted_payment}€."})
            
            months_needed = total_debt / proposed_monthly_payment
            if months_needed > maximum_period_months:
                return json.dumps({"error": f"No es posible saldar la deuda en {months_needed:.0f} meses con ese pago mensual, ya que supera el máximo permitido de {maximum_period_months} meses."})
            
            months_needed = max(1, round(months_needed))  # Asegurar al menos 1 mes y redondear
            final_payment = total_debt - (months_needed - 1) * proposed_monthly_payment
            final_payment = final_payment if months_needed > 1 else proposed_monthly_payment  # Ajustar si se paga en un solo mes

            message = f"Con un pago mensual de {proposed_monthly_payment}€, la deuda de {total_debt}€ se saldaría en {months_needed} meses."
            if months_needed > 1:
                message += f" El último pago sería de {final_payment:.2f}€."
            return json.dumps({"message": message})

        # Si solo se proporciona el periodo máximo
        if proposed_maximum_period_months is not None and proposed_monthly_payment is None:
            if proposed_maximum_period_months > maximum_period_months:
                return json.dumps({"error": f"El número máximo de meses permitido para pagar su deuda es de {maximum_period_months} meses."})
            
            monthly_payment_needed = total_debt / proposed_maximum_period_months
            if monthly_payment_needed < minimum_accepted_payment:
                return json.dumps({"error": f"El pago mensual necesario para saldar la deuda en {proposed_maximum_period_months} meses es inferior al mínimo aceptable de {minimum_accepted_payment}€."})

            return json.dumps({"message": f"Necesitarás hacer pagos mensuales de {monthly_payment_needed:.2f}€ para saldar la deuda en {proposed_maximum_period_months} meses."})

        # Si se proporcionan ambos
        if proposed_monthly_payment is not None and proposed_maximum_period_months is not None:
            if proposed_maximum_period_months > maximum_period_months:
                return json.dumps({"error": f"El número máximo de meses permitido para pagar su deuda es de {maximum_period_months} meses."})
            if proposed_monthly_payment < minimum_accepted_payment:
                return json.dumps({"error": f"El pago propuesto es inferior al mínimo aceptable. El pago mínimo aceptado es de {minimum_accepted_payment}€."})
            
            total_debt = debt.total_debt

            remaining_debt = total_debt
            months = 0

            while remaining_debt >= proposed_monthly_payment and months < proposed_maximum_period_months:
                months += 1
                remaining_debt -= proposed_monthly_payment

            if remaining_debt <= 0:
                return json.dumps({
                    "message": f"Si pagas {proposed_monthly_payment}€ cada mes, cubrirías la deuda de {total_debt}€ en {months} meses."
                })
            else:
                months += 1
                last_payment = remaining_debt
                return json.dumps({
                    "message": f"Si pagas {proposed_monthly_payment}€ cada mes, cubririas la mayor parte de la deuda de ${total_debt} en {months - 1} meses. En el mes {months}, te quedaría un pago final de {last_payment}€ para saldar completamente la deuda."
                })
        
        
        return json.dumps({"message": "Por favor, proporciona o el período máximo de meses o el pago mensual propuesto en el que quiere pagar su deuda."})

    
    def propose_payment_plan(self):
        debt = self.crud_service.get_debt_by_id(self.debt_id)
        if debt is None:
            return json.dumps({"error": "No tiene ninguna deuda con ese ID."})
        
        maximum_period_months = debt.maximum_period_months
        minimum_accepted_payment = debt.minimum_accepted_payment
        return json.dumps({
            "debt_id": self.debt_id,
            "meses_a_pagar": maximum_period_months,
            "pago_mensual": minimum_accepted_payment
        })
    

    def propose_partial_immediate_payment(self, immediate_payment_amount):
        def calculate_adjusted_payment_plan(remaining_debt):
            payment_period_months = 8
            monthly_payment = remaining_debt / payment_period_months

            # Podrías incluir lógica adicional aquí para ajustar el plan de pago
            # basado en criterios específicos, como la capacidad de pago del deudor

            message = f"Se propone un plan de pago de {payment_period_months} meses, con un pago mensual de {monthly_payment:.2f}€."
            return message

        if self.debt_id is None:
            return json.dumps({"error": "Por favor, establece un ID de deuda válido."})

        debt_details = self.crud_service.get_debt_by_id(self.debt_id)
        if debt_details is None:
            return json.dumps({"error": "No se encontró la deuda especificada."})
        
        total_debt = debt_details.total_debt
        payment_percentage = (immediate_payment_amount / total_debt) * 100

        if payment_percentage < 50:
            return json.dumps({"error": f"El pago inmediato debe ser al menos el 50% de la deuda total para considerar un plan de pago para el saldo restante."})
        elif payment_percentage < 75:
            current_discount = 7.5
        else:
            current_discount = 15

        remaining_debt = total_debt - immediate_payment_amount
        discounted_remaining = remaining_debt * (1 - (current_discount / 100))

        # Llamada a la función para calcular el plan de pago ajustado
        payment_plan_message = calculate_adjusted_payment_plan(discounted_remaining)

        message = f"Con tu pago inmediato de {immediate_payment_amount}€, que representa el {payment_percentage:.2f}% de tu deuda total, te hemos aplicado un descuento de {current_discount}%, Recuerda que si pagas mas del 75% ahora mismo se te aplicará un descuento del 15%. El saldo restante de tu deuda es ahora de {discounted_remaining:.2f}€. {payment_plan_message}"
        return json.dumps({"message": message})


    def set_debt_id(self, debt_id):
        self.debt_id = debt_id
        return json.dumps({"message": f"Las negociaciones se realizaron con la deuda de id {debt_id}."})

    def get_debt_id(self):
        return self.debt_id
    
    def get_tools_list(self):
        return self.tools_list

    def get_functions_available(self):
        return self.functions_available

    def get_system_message(self):
        return self.system_message

