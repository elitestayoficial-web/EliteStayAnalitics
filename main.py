#!/usr/bin/env python3
# main.py - Versión final para importar server.py

import os
import sys

# Agregar la ruta del proyecto para que Python encuentre los módulos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'backend'))
sys.path.insert(0, os.path.join(BASE_DIR, 'backend', 'api'))

# Importar la aplicación Flask
try:
    # Intento 1: Importar desde backend.api.server (estructura profesional)
    from backend.api.server import app
    print("✅ App importada desde backend.api.server")
except ImportError:
    try:
        # Intento 2: Importar directamente (si server.py está en la raíz)
        from server import app
        print("✅ App importada desde server.py (raíz)")
    except ImportError as e:
        print(f"❌ Error crítico: No se pudo importar la app - {e}")
        print(f"📁 Python busca en: {sys.path}")
        sys.exit(1)

# Para Gunicorn (compatibilidad máxima)
application = app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)


