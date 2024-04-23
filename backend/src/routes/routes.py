from flask import request, jsonify, Blueprint, current_app
from src.database.Database import Database
from src.services.CrudPsgService import CRUDService
from src.services.NegotiatorChatbot import Negotiator
from src.auth.auth import Authentication
from src.services.tools.assistant_tools import Tooling
from src.services.Chatbot import Chatbot

api = Blueprint('api', __name__)

db_session = Database.db.session
crud_service = CRUDService(db_session, current_app)
auth = Authentication()
negotiator = Negotiator(crud_service, auth)
assistant_tools = Tooling()
chatbot = Chatbot(negotiator)




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



@api.route('/delete_assistant', methods=['POST'])
def delete_assistant():
    assistant_tools.delete_assistant()
    return jsonify({"message": "Asistente eliminado exitosamente"}), 200

@api.route('/delete_thread', methods=['POST'])
def delete_thread():
    assistant_tools.delete_thread()
    return jsonify({"message": "Hilo eliminado exitosamente"}), 200

@api.route('/delete_tool', methods=['POST'])
def delete_tool():
    data = request.get_json()
    tool_name = data['tool_name']
    assistant_tools.delete_tool(tool_name)
    return jsonify({"message": "Herramienta eliminada exitosamente"}), 200

@api.route('/add_tool', methods=['POST'])
def add_tool():
    data = request.get_json()
    tool = data['tool']
    assistant_tools.add_tool(tool)
    return jsonify({"message": "Herramienta añadida exitosamente"}), 201

@api.route('/get_tools', methods=['GET'])
def get_tools():
    return jsonify(assistant_tools.get_tools())

# Usadas en streamlit_app.py
@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    if crud_service.validate_user(email, password):
        auth.set_user(email, password)
        return jsonify({"message": "Se ha logueado exitosamente"}), 200
    else:
        return jsonify({"error": "Nombre de usuario o contraseña incorrectos"}), 401
    
@api.route('/logout', methods=['POST'])
def logout():
    auth.logout()
    return jsonify({"message": "Se ha deslogueado exitosamente"}), 200

@api.route('/ask_assistant', methods=['POST'])
def ask_assistant():
    data = request.get_json()
    message = data['message']
    return jsonify({"response": chatbot.ask_assistant(message)}), 200

@api.route('/set_api_key', methods=['POST'])
def set_api_key():
    data = request.get_json()
    api_key = data['api_key']

    if not (api_key.startswith('sk-') and len(api_key) == 51):
        return jsonify({"error": "La clave de API proporcionada es inválida. Asegúrate de que inicie con 'sk-' y que tenga 51 caracteres de longitud."}), 400

    chatbot.set_api_key(api_key)
    return jsonify({"message": "API key configurada correctamente"}), 200

@api.route('/clear_chat_history', methods=['POST'])
def create_thread():
    chatbot.delete_thread()
    chatbot.create_thread()
    return jsonify({"message": "Hilo creado exitosamente"}), 201

