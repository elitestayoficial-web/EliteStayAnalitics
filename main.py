#!/usr/bin/env python3
import os
import sys
import threading
import logging
from dotenv import load_dotenv

# --- CONFIGURACIÓN DE RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

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
    # Como server.py está en la raíz, la importación es directa
    from server import app
    logger.info("✅ App importada exitosamente desde server.py")
except ImportError as e:
    logger.error(f"❌ ERROR FATAL: No se pudo encontrar server.py o la variable 'app': {e}")
    sys.exit(1)

# --- INICIALIZACIÓN ---
def initialize():
    """Ejecuta tareas de inicialización (base de datos, scheduler)"""
    if os.environ.get('INITIALIZED') == 'true':
        return
    
    logger.info("🚀 INICIANDO CONFIGURACIÓN DE ELITESTAY")
    
    try:
        # Importamos directamente desde la raíz
        from schema import init_database
        init_database()
        logger.info("✅ Base de datos inicializada")
        
        from scheduler import Scheduler
        scheduler = Scheduler()
        scheduler_thread = threading.Thread(target=scheduler.run, daemon=True)
        scheduler_thread.start()
        logger.info("⏰ Programador iniciado")
        
        os.environ['INITIALIZED'] = 'true'
    except Exception as e:
        logger.error(f"❌ Error en inicialización: {e}")

# Ejecutamos la inicialización antes de que Gunicorn tome el control
initialize()

# --- PARA GUNICORN ---
application = app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

