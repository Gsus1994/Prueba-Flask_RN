# app.py

import os
from src import create_app

config_name = os.getenv('FLASK_CONFIG', 'production')
app = create_app(config_name)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)



#   Contruir imagen:
#        docker build -t TooHeroku .
#   Ejecutar container
#       docker run --name wsgi --env-file C:\\Users\\Usuario\\Desktop\\TOO_FLASK\\.env -p 5000:8000 TooHeroku