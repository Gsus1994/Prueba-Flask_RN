from src import create_app

app = create_app('development')  # Cambiar a 'production' en producción

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


#   Contruir imagen:
#        docker build -t gsus1994/too:latest .
#   Ejecutar container
#       docker run --name wsgi --env-file C:\\Users\\Usuario\\Desktop\\TOO_FLASK\\.env -p 5000:8000 gsus1994/too:latest