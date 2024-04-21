from src import create_app
from src.routes.routes import api as api_blueprint

app = create_app()

app.register_blueprint(api_blueprint) # Registramos el blueprint de la api que creamos en las rutas, o más si quieres organizarlo por tipo de servicio: login, chat, etc.

if __name__ == "__main__":
    app.run(host='0.0.0.0') # Damos acceso a todas las IPs. Por defecto, Flask se ejecuta en el puerto 5000