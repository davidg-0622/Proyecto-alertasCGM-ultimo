# Importamos la funcion create_app del modulo app
from app import create_app, db

#   Ejecutamos la aplicacion

if __name__ == '__main__':
    app = create_app() # Creamos la aplicacion llamando a la funcion create_app
    #app.run(debug=True) # Habilita el modo de depuración local host 
    #app.run(host='10.156.149.100', port=8502, debug=True)
    app.run(host='0.0.0.0', port=8502, debug=True) # Habilita en DG 

