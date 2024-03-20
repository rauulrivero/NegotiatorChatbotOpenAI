from src.gui.streamlitNegotiation import StreamlitApp
from src.database.Database import Database
from flask import Flask
from config.config import Config, ProductionConfig, DevelopmentConfig, TestingConfig
from src.auth.auth import Authentication
from src.services.NegotiatorChatbot import Negotiator
from src.services.CrudPsgService import CRUDService
from src.services.Chatbot import Chatbot



def main():
    app = Flask(__name__)

    
    if Config.FLASK_ENV == 'development':
        app.config.from_object(DevelopmentConfig)

    elif Config.FLASK_ENV == 'production':
        app.config.from_object(ProductionConfig)

    else:
        app.config.from_object(TestingConfig) # it'd be testing

    auth = Authentication()
    db_session = Database(app).db.session
    crud_service = CRUDService(db_session, app)
    negotiator = Negotiator(crud_service, auth)
    chatbot = Chatbot(negotiator)

    app = StreamlitApp(crud_service, chatbot, app, auth)
    app.run()


if __name__ == "__main__":
    main()