#!/usr/bin/env python3
# main.py - Versión Súper Flexible para Render

import os
import sys
import threading
import logging
from dotenv import load_dotenv

# --- CONFIGURACIÓN DE RUTAS (BÚSQUEDA INTELIGENTE) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Buscar recursivamente el archivo server.py
def find_server_file(start_path):
    """Busca server.py en todas las subcarpetas"""
    for root, dirs, files in os.walk(start_path):
        if 'server.py' in files:
            return root
    return None

server_dir = find_server_file(BASE_DIR)
if server_dir and server_dir not in sys.path:
    sys.path.insert(0, server_dir)
    print(f"✅ Encontrado server.py en: {server_dir}")

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

# --- IMPORTACIÓN DE LA APP (MÚLTIPLES INTENTOS) ---
app = None

# Intento 1: Si server_dir se encontró
if server_dir:
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "server_module", 
            os.path.join(server_dir, 'server.py')
        )
        server_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server_module)
        app = getattr(server_module, 'app', None)
        if app:
            logger.info("✅ App cargada dinámicamente desde server.py")
    except Exception as e:
        logger.warning(f"⚠️ Carga dinámica falló: {e}")

# Intento 2: Importación tradicional
if app is None:
    try:
        from backend.api.server import app
        logger.info("✅ App importada como 'backend.api.server'")
    except ImportError:
        try:
            from api.server import app
            logger.info("✅ App importada como 'api.server'")
        except ImportError:
            try:
                from server import app
                logger.info("✅ App importada como 'server'")
            except ImportError as e:
                logger.error(f"❌ ERROR FATAL: No se pudo importar la app: {e}")
                sys.exit(1)

# --- INICIALIZACIÓN ---
def initialize():
    """Ejecuta tareas de inicialización (base de datos, scheduler)"""
    if os.environ.get('INITIALIZED') == 'true':
        return
    
    logger.info("🚀 INICIANDO CONFIGURACIÓN")
    
    try:
        # Intentar importar desde múltiples ubicaciones
        try:
            from backend.database.schema import init_database
        except ImportError:
            from database.schema import init_database
        
        init_database()
        logger.info("✅ Base de datos inicializada")
        
        try:
            from backend.automated.scheduler import Scheduler
        except ImportError:
            from automated.scheduler import Scheduler
            
        scheduler = Scheduler()
        scheduler_thread = threading.Thread(target=scheduler.run, daemon=True)
        scheduler_thread.start()
        logger.info("⏰ Programador iniciado")
        
        os.environ['INITIALIZED'] = 'true'
    except Exception as e:
        logger.error(f"❌ Error en inicialización: {e}")
        # No salimos para que al menos la web funcione

initialize()

# --- PARA GUNICORN ---
application = app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
