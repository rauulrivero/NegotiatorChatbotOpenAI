from src.models.models import User, Debt
from sqlalchemy.exc import IntegrityError
import json

class CRUDService:
    def __init__(self, db):
        self.session = db.db.session

    def create_user(self, name, surname, email, telephone):
        try:
            user = User(name=name, surname=surname, email=email, telephone=telephone)
            self.session.add(user)
            self.session.commit()
            return user
        except IntegrityError:
            self.session.rollback()
            print("Error: El teléfono o el correo electrónico ya están en uso.")
            return None

    def create_debt(self, total_debt, maximum_period_months, user_email):
        try:
            debt = Debt(total_debt=total_debt, maximum_period_months=maximum_period_months, minimum_accepted_payment=Debt.calculate_minimum_accepted_payment(total_debt, maximum_period_months), user_email=user_email)
            self.session.add(debt)
            self.session.commit()
            return debt
        except IntegrityError:
            self.session.rollback()
            print("Error: El usuario no existe.")
            return None

    def get_all_debts(self):
        return self.session.query(Debt).all()

    def get_all_users(self):
        return self.session.query(User).all()

    def get_user_by_email(self, email):
        return self.session.query(User).filter(User.email == email).first()

    def delete_user_by_email(self, email):
        user = self.session.query(User).filter(User.email == email).first()
        if user:
            self.session.delete(user)
            self.session.commit()
        else:
            print("Error: El usuario no existe.")

    def update_user_by_email(self, email, name, surname, telephone):
        user = self.session.query(User).filter(User.email == email).first()
        if user:
            user.name = name
            user.surname = surname
            user.telephone = telephone
            self.session.commit()
        else:
            print("Error: El usuario no existe.")

    def get_debts_by_user_email(self, email):
        return self.session.query(Debt).filter(Debt.user_email == email).all()

    def get_debt_by_total_debt(self, total_debt):
        return self.session.query(Debt).filter(Debt.total_debt == total_debt).first()
    
    
    def get_all_debts_by_user(self, user_email):
        """
        Obtiene todas las deudas asociadas a un usuario dado su correo electrónico.
        
        Args:
            user_email (str): El correo electrónico del usuario.
        
        Returns:
            str: Las deudas del usuario en formato JSON.
        """
        debts = self.session.query(Debt).filter(Debt.user_email == user_email).all()
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
    
    
    def calculate_payment_plan(self, email, proposed_maximum_period_months, proposed_total_debt, proposed_monthly_payment):
        debts = self.get_debts_by_user_email(email)
        if debts is None:
            return json.dumps({"error": "Este usuario no tiene deudas"})
        
        debt = self.get_debt_by_total_debt(proposed_total_debt)
        if debt is None:
            return json.dumps({"error": "No tiene ninguna deuda con esa cantidad total de deuda."})
        
        total_debt = debt.total_debt
        minimum_accepted_payment = debt.minimum_accepted_payment
        maximum_period_months = debt.maximum_period_months

        if proposed_maximum_period_months is None:
            return json.dumps({"error": "El número máximo de meses permitidos para pagar su deuda es requerido."})
        
        if proposed_total_debt is None:
            return json.dumps({"error": "La cantidad total de deuda es requerida."})
        
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
    
        while remaining_debt >= proposed_monthly_payment and months < maximum_period_months:
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