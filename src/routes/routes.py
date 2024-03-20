from flask import request, jsonify, Blueprint, current_app
from src.database.Database import Database
from src.services.CrudPsgService import CRUDService
from src.services.NegotiatorChatbot import Negotiator
from src.auth.auth import Authentication

api = Blueprint('api', __name__)

db_session = Database.db.session
crud_service = CRUDService(db_session, current_app)
auth = Authentication()
negotiator = Negotiator(crud_service, auth)




@api.route('/', methods=['GET'])
def index():
    return jsonify({'response': 'Welcome to my API!'}), 200

@api.route('/debts/<user_email>', methods=['GET'])
def get_debts_by_user_email(user_email):
      return jsonify(crud_service.get_all_debts_by_user(user_email))

@api.route('/create_user', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data['name']
    password = data['password']
    surname = data['surname']
    email = data['email']
    telephone = data['telephone']

    if not all([name, password, surname, email, telephone]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400
        
    if crud_service.user_exists(email):
        return jsonify({"error": "El usuario ya existe"}), 409
        
    crud_service.create_user(name, surname, email, telephone, password)
    return jsonify({"message": "Usuario creado exitosamente"}), 201


@api.route('/delete_user', methods=['DELETE'])
def delete_user():
    data = request.get_json()
    email = data['email']

    if not email:
        return jsonify({"error": "Falta el email"}), 400
    
    if not crud_service.user_exists(email):
        return jsonify({"error": "El usuario no existe"}), 404
    
    crud_service.delete_user_by_email(email)
    return jsonify({"message": "Usuario eliminado exitosamente"}), 200


@api.route('/create_debt', methods=['POST'])
def create_debt():
    data = request.get_json()
    total_debt = data['total_debt']
    maximum_period_months = data['maximum_period_months']
    user_email = data['user_email']

    if not all([total_debt, maximum_period_months, user_email]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400
    
    if not crud_service.user_exists(user_email):
        return jsonify({"error": "El usuario no existe"}), 404

    crud_service.create_debt(total_debt, maximum_period_months, user_email)
    return jsonify({"message": "Deuda creada exitosamente"}), 201


@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    user = crud_service.get_user_by_email(email) 

    if user and user.password == password:
        auth.set_user(email, password)
        return jsonify({"message": "Se ha logueado exitosamente"}), 200
    else:
        return jsonify({"error": "Nombre de usuario o contraseña incorrectos"}), 401