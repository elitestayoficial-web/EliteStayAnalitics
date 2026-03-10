#!/usr/bin/env python3
# main.py - Punto de entrada para Gunicorn (estructura profesional)

import os
import sys

# Asegurar que Python encuentra backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar la app DESDE backend/api/server.py
from backend.api.server import app

# Por compatibilidad con Gunicorn
application = app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

