from src.gui.streamlit import StreamlitApp
from src.database.Database import Database
from flask import Flask
from config.config import Config, ProductionConfig, DevelopmentConfig, TestingConfig



def main():
    app = Flask(__name__)

    
    if Config.FLASK_ENV == 'development':
        app.config.from_object(DevelopmentConfig)

    elif Config.FLASK_ENV == 'production':
        app.config.from_object(ProductionConfig)

    else:
        app.config.from_object(TestingConfig) # it'd be testing

    
    db_session = Database(app).db.session
    app = StreamlitApp(db_session, app)
    app.run()


if __name__ == "__main__":
    main()