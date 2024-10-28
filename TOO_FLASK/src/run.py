import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src import create_app

app = create_app('development')  # Cambiar a 'production' en producción

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)