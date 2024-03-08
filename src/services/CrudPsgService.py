from src.models.models import User, Debt
from sqlalchemy.exc import IntegrityError
import json

class CRUDService:
    def __init__(self, session, app):
        self.session = session
        self.app = app

    def create_user(self, name, surname, email, telephone, password):
        with self.app.app_context():    
            try:
                user = User(name=name, surname=surname, email=email, telephone=telephone, password=password)
                self.session.add(user)
                self.session.commit()
                return user
            except IntegrityError:
                self.session.rollback()
                print("Error: El usuario ya existe.")
                return None
        
    def user_exists(self, email):
        with self.app.app_context():
            return self.session.query(User).filter(User.email == email).first() is not None

    def create_debt(self, total_debt, maximum_period_months, user_email):
        with self.app.app_context():     
            try:
                debt = Debt(total_debt=total_debt, maximum_period_months=maximum_period_months, minimum_accepted_payment=Debt.calculate_minimum_accepted_payment(total_debt, maximum_period_months), user_email=user_email)
                self.session.add(debt)
                self.session.commit()
                return debt
            except IntegrityError:
                self.session.rollback()
                print("Error: El usuario no existe.")
                return None
            
    def get_all_users(self):
        with self.app.app_context():
            return self.session.query(User).all()

    def get_user_by_email(self, email):
        with self.app.app_context():
            return self.session.query(User).filter(User.email == email).first()

    def delete_user_by_email(self, email):
        with self.app.app_context():
            user = self.session.query(User).filter(User.email == email).first()
            if user:
                self.session.delete(user)
                self.session.commit()
            else:
                print("Error: El usuario no existe.")

    def update_user_by_email(self, email, name, surname, telephone):
        with self.app.app_context():
            user = self.session.query(User).filter(User.email == email).first()
            if user:
                user.name = name
                user.surname = surname
                user.telephone = telephone
                self.session.commit()
            else:
                print("Error: El usuario no existe.")

    def get_debts_by_user_email(self, email):
        with self.app.app_context():
            return self.session.query(Debt).filter(Debt.user_email == email).all()
    
    def get_passwd_by_email(self, email):
        with self.app.app_context():
            return self.session.query(User).filter(User.email == email).first().passwd

    def get_debt_by_total_debt(self, total_debt):
        with self.app.app_context():
            return self.session.query(Debt).filter(Debt.total_debt == total_debt).first()
    
    def get_debt_by_id(self, id):
        with self.app.app_context():
            return self.session.query(Debt).filter(Debt.id == id).first()
    
    
    def get_all_debts_by_user(self, user_email):
        with self.app.app_context():
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
        
    def get_passwd_by_email(self, email):
        with self.app.app_context():
            return self.session.query(User).filter(User.email == email).first().password
    
    def validate_user(self, email, password):
        with self.app.app_context():
            return self.session.query(User).filter(User.email == email, User.password == password).first() is not None