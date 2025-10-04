# Importamos la funcion create_app del modulo app
from app import create_app, db

#   Ejecutamos la aplicacion

if __name__ == '__main__':
    app = create_app() # Creamos la aplicacion llamando a la funcion create_app
    app.run(debug=True) # Ejecutamos la aplicacion en modo debug


