from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import create_engine, exc
from sqlalchemy_utils import database_exists, create_database
import logging

class Database:
    db = SQLAlchemy()

    def __init__(self, app):
        self.app = app
        self.connect(self.app)
        self.create_db(self.app)

    def connect(self, app):
        self.db.init_app(app)

    def create_db(self, app):
        try:
            with app.app_context():
                db_url = app.config.get('SQLALCHEMY_DATABASE_URI')
                engine = create_engine(db_url)
                logging.debug(f"Checking if database at {db_url} exists")

                if not database_exists(engine.url):
                    logging.debug(f"Database at {db_url} does not exist, attempting to create")
                    create_database(engine.url)

                self.db.create_all()

        except exc.ProgrammingError as e:
            logging.error(f"ProgrammingError: {e}")

        except exc.OperationalError as e:
            logging.error(f"OperationalError: {e}")

        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
    