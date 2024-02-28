from openai import OpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configure the OpenAI API key
client = OpenAI(
    api_key=os.getenv
    ("OPENAI_API_KEY"),
)

GPT_MODEL = "gpt-3.5-turbo-1106"

postgres = {
    'usuario': os.getenv("POSTGRES_USER"),
    'contraseña': os.getenv("POSTGRES_PASSWORD"),
    'host': os.getenv("POSTGRES_HOST"),
    'puerto': os.getenv("POSTGRES_PORT"),
    'nombre_basedatos': os.getenv("POSTGRES_DB")
}
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy import Float
import psycopg2

def conectar_db(usuario, contraseña, host, puerto, nombre_basedatos):
    cadena_conexion = f"postgresql://{usuario}:{contraseña}@{host}:{puerto}/{nombre_basedatos}"
    engine = create_engine(cadena_conexion, echo=True)
    return engine

# Conectar a la base de datos
engine = conectar_db(**postgres)
# Creamos las tablas
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    email = Column(String, primary_key=True)
    name = Column(String)
    surname = Column(String)
    telephone = Column(String, unique=True)

    debts = relationship("Debt", back_populates="user")

class Debt(Base):
    __tablename__ = 'debts'

    id = Column(Integer, primary_key=True)
    total_debt = Column(Integer)
    maximum_period_months = Column(Integer)
    minimum_accepted_payment = Column(Float)
    user_email = Column(String, ForeignKey('users.email'))

    user = relationship("User", back_populates="debts")

    @classmethod
    def calculate_minimum_accepted_payment(cls, total_debt, maximum_period_months):
        return round(total_debt / maximum_period_months, 2)

Base.metadata.create_all(engine)

def crear_sesion(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

session = crear_sesion(engine)

from sqlalchemy.exc import IntegrityError

def create_user(name, surname, email, telephone):
    try:
        user = User(name=name, surname=surname, email=email, telephone=telephone)
        session.add(user)
        session.commit()
        return user
    except IntegrityError:
        session.rollback()
        print("Error: El teléfono o el correo electrónico ya están en uso.")
        return None

def create_debt(total_debt, maximum_period_months, user_email):
    try:
        debt = Debt(total_debt=total_debt, maximum_period_months=maximum_period_months, minimum_accepted_payment=Debt.calculate_minimum_accepted_payment(total_debt, maximum_period_months) ,user_email=user_email)
        session.add(debt)
        session.commit()
        return debt
    except IntegrityError:
        session.rollback()
        print("Error: El usuario no existe.")
        return None

# get all debts
def get_all_debts():
    return session.query(Debt).all()

# get all debts by user
def get_all_debts_by_user(user_email):
    return session.query(Debt).filter(Debt.user_email == user_email).all()

# get all users
def get_all_users():
    return session.query(User).all()

# get user by email
def get_user_by_email(email):
    return session.query(User).filter(User.email == email).first()
    
# delete user by email
def delete_user_by_email(email):
    user = get_user_by_email(email)
    session.delete(user)
    session.commit()

# update user by email
def update_user_by_email(email, name, surname, telephone):
    user = get_user_by_email(email)
    user.name = name
    user.surname = surname
    user.telephone = telephone
    session.commit()

    # get debts by user email
def get_debts_by_user_email(email):
    return session.query(Debt).filter(Debt.user_email == email).all()

# get user by email
def get_user_by_email(email):
    return session.query(User).filter(User.email == email).first()

# get debt by total debt
def get_debt_by_total_debt(total_debt):
    return session.query(Debt).filter(Debt.total_debt == total_debt).first()

def calculate_payment_plan(email, maximum_period_months, proposed_total_debt, proposed_monthly_payment):
    debts = get_debts_by_user_email(email)
    if debts is None:
        return json.dumps({"error": "Este usuario no tiene deudas"})
    
    debt = get_debt_by_total_debt(proposed_total_debt)
    if debt is None:
        return json.dumps({"error": "No tiene ninguna deuda con esa cantidad total de deuda."})
    
    total_debt = debt.total_debt
    minimum_accepted_payment = debt.minimum_accepted_payment
    maximum_period_months = debt.maximum_period_months
    
    if proposed_monthly_payment < minimum_accepted_payment:
        return json.dumps({
            "error": f"El pago propuesto es inferior al minimo aceptable. No se puede calcular un plan de pago. El pago mínimo aceptado es de ${minimum_accepted_payment}."
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

function_descriptions = [
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
                "maximum_period_months": {
                    "type": "number",
                    "description": "El número máximo de meses permitidos para saldar la deuda."
                },
                "proposed_total_debt": {
                    "type": "number",
                    "description": "La cantidad total de deuda propuesta por el deudor."
                },
                "proposed_monthly_payment": {
                    "type": "number",
                    "description": "La cantidad que el deudor propone pagar cada mes."
                }
            },
            "required": ["email", "maximum_period_months", "proposed_total_debt", "proposed_monthly_payment"]
        }
    }
]


def detect_function(prompt):
    """Give LLM a given prompt and get an answer."""

    completion = client.chat.completions.create(
        model=GPT_MODEL,
        messages=[{"role": "user", "content": prompt}],

        functions=function_descriptions,
        function_call="auto",  # specify the function call
    )

    output = completion.choices[0].message
    return output

def function_calling(prompt, function, content):
    """Give LLM a given prompt and get an answer."""

    completion = client.chat.completions.create(
        model=GPT_MODEL,
        messages=[{"role": "user", "content": prompt},
                  {"role":"function", "name": function, "content": content}],

        functions=function_descriptions,
        function_call="auto",  # specify the function call
    )

    output = completion.choices[0].message
    return output
