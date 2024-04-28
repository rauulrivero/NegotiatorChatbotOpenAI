from gui.app_interface import StreamlitApp
from api.api_handler import ApiHandler

def main():
    api_handler = ApiHandler("http://localhost:5000")
    app = StreamlitApp(api_handler)
    app.run()


if __name__ == "__main__":
    main()