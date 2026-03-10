#!/usr/bin/env python3
# main.py - Versión ultra simple para Gunicorn

import os
import sys

# Asegurar que Python encuentra backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar la aplicación Flask DESDE backend.api.server
from backend.api.server import app

# Gunicorn buscará 'app' (ya está definida arriba)
# Pero por si acaso, también definimos 'application'
application = app

# Esto es solo para desarrollo local
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

# ... (todo tu código anterior)

# Esto es lo que Gunicorn está buscando
application = app 
app = application

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
