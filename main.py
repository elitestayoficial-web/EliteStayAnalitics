#!/usr/bin/env python3
# main.py - Busca server.py en raíz y en backend/api

import os
import sys
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Agregar rutas al path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'backend', 'api'))

# --- INTENTO 1: Importar desde la raíz ---
try:
    from server import app
    logger.info("✅ App importada desde server.py (raíz)")
except ImportError:
    logger.warning("⚠️ No se encontró server.py en la raíz")
    
    # --- INTENTO 2: Importar desde backend/api ---
    try:
        from backend.api.server import app
        logger.info("✅ App importada desde backend.api.server")
    except ImportError as e:
        logger.error(f"❌ No se encontró server.py en ninguna ubicación: {e}")
        logger.error(f"📁 Python busca en: {sys.path}")
        sys.exit(1)

# Para Gunicorn
application = app
app = application
if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    logger.info(f"Iniciando servidor en puerto {port}")
    app.run(host='0.0.0.0', port=port)


