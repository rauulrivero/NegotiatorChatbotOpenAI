from src.models.models import User, Debt
from sqlalchemy.exc import IntegrityError
import json

class CRUDService:
    def __init__(self, session):
        self.session = session

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
    
    def get_debt_by_id(self, id):
        return self.session.query(Debt).filter(Debt.id == id).first()
    
    
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