import os, logging

def conf_logging():
    if not os.path.exists('backend/logs/'):
        os.makedirs('backend/logs/') # creas la carpeta si no existe

    logging.basicConfig(filename='backend/logs/app.log', filemode='a', format='%(asctime)s %(levelname)s %(name)s : %(message)s', level=logging.INFO)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)