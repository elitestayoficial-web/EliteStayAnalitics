#!/usr/bin/env python3
import os
import sys
import threading
import logging
from dotenv import load_dotenv

# --- CONFIGURACIÓN DE PATHS ---
# Forzamos a Python a mirar en la raíz y en la carpeta 'backend'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
if os.path.exists(os.path.join(BASE_DIR, 'backend')):
    sys.path.insert(0, os.path.join(BASE_DIR, 'backend'))

load_dotenv()

# Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- IMPORTACIÓN DINÁMICA DE LA APP ---
app = None

# Intento 1: Importar server.py de la raíz (el más probable según tu lista)
try:
    from server import app
    logger.info("✅ App cargada desde la raíz (server.py)")
except ImportError:
    # Intento 2: Importar desde la carpeta backend
    try:
        from backend.api.server import app
        logger.info("✅ App cargada desde backend.api.server")
    except ImportError as e:
        logger.error(f"❌ No se encontró 'app' en ninguna ubicación: {e}")
        sys.exit(1)

# --- INICIALIZACIÓN ---
def initialize():
    """Inicializa DB y Scheduler buscando los archivos donde sea que estén"""
    if os.environ.get('INITIALIZED') == 'true':
        return

    try:
        # Intentar importar schema e iniciar DB
        try:
            from schema import init_database
        except ImportError:
            from backend.database.schema import init_database
        
        init_database()
        logger.info("✅ Base de datos inicializada")

        # Intentar importar scheduler e iniciar hilo
        try:
            from scheduler import Scheduler
        except ImportError:
            from backend.automated.scheduler import Scheduler
            
        scheduler = Scheduler()
        threading.Thread(target=scheduler.run, daemon=True).start()
        logger.info("⏰ Scheduler iniciado")
        
        os.environ['INITIALIZED'] = 'true'
    except Exception as e:
        logger.error(f"⚠️ Error en inicialización: {e}")

# Ejecutar inicio
initialize()

# Referencia para Gunicorn
application = app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


