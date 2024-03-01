from flask import Flask
from config.config import Config, ProductionConfig, DevelopmentConfig, TestingConfig
from config.logger import conf_logging
from src.database.Database import Database

conf_logging()

def create_app(config_class=Config):
    app = Flask(__name__)

    if Config.FLASK_ENV == 'development':
        app.config.from_object(DevelopmentConfig)

    elif Config.FLASK_ENV == 'production':
        app.config.from_object(ProductionConfig)

    else:
        app.config.from_object(TestingConfig) # it'd be testing

    Database(app) # instanciamos la clase `Database` pasándole la instancia de la app de Flask

    return app


