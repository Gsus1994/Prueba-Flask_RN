from src import create_app

app = create_app('development')  # Cambiar a 'production' en producción

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



#Correr el comando:
# .\ngrok.exe http 5000
# para abrir el puerto 5000 y exponer la app corriendo.