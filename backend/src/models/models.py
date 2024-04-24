from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    email = Column(String, primary_key=True)
    password = Column(String)
    name = Column(String)
    surname = Column(String)
    telephone = Column(String, unique=True)

    debts = relationship("Debt", back_populates="user")

class Debt(Base):
    __tablename__ = 'debts'

    id = Column(Integer, primary_key=True)
    total_debt = Column(Float)
    maximum_period_months = Column(Integer)
    minimum_accepted_payment = Column(Float)
    user_email = Column(String, ForeignKey('users.email'))

    user = relationship("User", back_populates="debts")

    @classmethod
    def calculate_minimum_accepted_payment(cls, total_debt, maximum_period_months):
        return round(total_debt / maximum_period_months, 2)
