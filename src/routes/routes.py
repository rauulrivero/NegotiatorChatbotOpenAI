from flask import request, jsonify, Blueprint
from src.database.Database import Database
from src.services.CrudPsgService import CRUDService

api = Blueprint('api', __name__)
db_session = Database.db.session
crud_service = CRUDService(db_session)

@api.route('/', methods=['GET'])
def index():
    return jsonify({'response': 'Welcome to my API!'}), 200

@api.route('/debt/<user_email>', methods=['GET'])
def get_debts_by_user_email(user_email):
      return jsonify(crud_service.get_all_debts_by_user(user_email))

@api.route('/calculate_payment_plan', methods=['POST'])
def calculate_payment_plan():
    data = request.get_json()
    email = data['email']
    proposed_maximum_period_months = data['proposed_maximum_period_months']
    proposed_total_debt = data['proposed_total_debt']
    proposed_monthly_payment = data['proposed_monthly_payment']
    return jsonify(crud_service.calculate_payment_plan(email, proposed_maximum_period_months, proposed_total_debt, proposed_monthly_payment))
