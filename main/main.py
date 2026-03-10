#!/usr/bin/env python3
# main.py - Versión corregida para estructura plana

import os
import sys
import threading
import logging

# Configuración básica de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Configurar logging para ver qué pasa en Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- IMPORTACIÓN CRÍTICA ---
try:
    # Como tu archivo se llama 'server.py' y está en la raíz:
    from server import app
    logger.info("✅ App importada exitosamente desde server.py")
except ImportError as e:
    logger.error(f"❌ Error importando server.py: {e}")
    # Intento de respaldo si por alguna razón moviste el archivo
    try:
        from backend.api.server import app
        logger.info("✅ App importada desde backend/api/server.py")
    except ImportError:
        logger.error("❌ No se encontró el módulo server en ninguna ubicación.")
        sys.exit(1)

# --- INICIALIZACIÓN (Base de datos y Scheduler) ---
def initialize_services():
    try:
        # Importamos desde la raíz ya que tus archivos están ahí
        from schema import init_database
        from scheduler import Scheduler
        
        init_database()
        logger.info("✅ Base de datos inicializada")
        
        sc = Scheduler()
        threading.Thread(target=sc.run, daemon=True).start()
        logger.info("⏰ Scheduler iniciado en segundo plano")
    except Exception as e:
        logger.error(f"⚠️ Error al iniciar servicios: {e}")

# Ejecutamos la inicialización
initialize_services()

# --- PARA GUNICORN ---
# Gunicorn buscará 'app' o 'application'
# Ya tenemos 'app' importada, pero por compatibilidad máxima:
application = app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

