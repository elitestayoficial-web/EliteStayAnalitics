#!/usr/bin/env python3
import os
import sys
import threading
import logging
from dotenv import load_dotenv

# --- FUERZA LA RUTA ACTUAL ---
# Esto es vital en Python 3.9 para que reconozca los archivos vecinos
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# --- Logs ---
LOG_DIR = os.path.join(CURRENT_DIR, 'logs')
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

# --- IMPORTACIÓN DIRECTA ---
try:
    # Importamos 'app' desde 'server.py' que está en la misma carpeta
    from server import app
    logger.info("✅ App importada desde server.py")
except ImportError as e:
    logger.error(f"❌ Error: No se encontró server.py o la variable app: {e}")
    sys.exit(1)

# --- INICIALIZACIÓN ---
def initialize():
    if os.environ.get('INITIALIZED') == 'true':
        return
    
    logger.info("🚀 INICIANDO SERVICIOS")
    
    try:
        # Importación de archivos locales (sin carpetas backend.xxxx)
        from schema import init_database
        init_database()
        logger.info("✅ Base de datos lista")
        
        from scheduler import Scheduler
        scheduler = Scheduler()
        t = threading.Thread(target=scheduler.run, daemon=True)
        t.start()
        logger.info("⏰ Scheduler en segundo plano")
        
        os.environ['INITIALIZED'] = 'true'
    except Exception as e:
        logger.error(f"⚠️ Error en inicialización: {e}")

initialize()

application = app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
