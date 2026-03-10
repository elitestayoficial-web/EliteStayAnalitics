#!/usr/bin/env python3
import os
import sys
import threading
import logging
from dotenv import load_dotenv

# --- CONFIGURACIÓN DE RUTAS (Blindaje total) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Si la carpeta 'backend' existe, la metemos al path también
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')
if os.path.exists(BACKEND_DIR) and BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# --- Logs ---
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'elitestayanalitycs.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- IMPORTACIÓN DE LA APP ---
try:
    # Intento 1: Importación absoluta (La mejor para Gunicorn)
    from backend.api.server import app
    logger.info("✅ App importada mediante 'backend.api.server'")
except ImportError:
    try:
        # Intento 2: Importación relativa si ya estamos dentro de backend
        from api.server import app
        logger.info("✅ App importada mediante 'api.server'")
    except ImportError as e:
        logger.error(f"❌ ERROR FATAL: No se encontró la aplicación Flask: {e}")
        sys.exit(1)

# --- Inicialización ---
def initialize():
    """Ejecuta tareas de inicialización (base de datos, scheduler)"""
    # Evitar que el scheduler arranque dos veces en Render
    if os.environ.get('INITIALIZED') == 'true':
        return
    
    logger.info("🚀 ELITE STAY ANALYTICS - INICIANDO CONFIGURACIÓN")
    
    try:
        # Importación dinámica para evitar errores circulares
        from backend.database.schema import init_database
        init_database()
        logger.info("✅ Base de datos inicializada")
        
        from backend.automated.scheduler import Scheduler
        scheduler = Scheduler()
        scheduler_thread = threading.Thread(target=scheduler.run, daemon=True)
        scheduler_thread.start()
        logger.info("⏰ Programador iniciado")
        
        os.environ['INITIALIZED'] = 'true'
    except Exception as e:
        logger.error(f"❌ Error durante la inicialización: {e}")

initialize()

# --- PARA GUNICORN ---
# Render buscará 'app' o 'application' en este archivo
application = app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

