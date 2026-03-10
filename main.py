#!/usr/bin/env python3
# main.py - Punto de entrada principal para EliteStayAnalytics

import os
import threading
import logging
import sys
from dotenv import load_dotenv

# --- Configuración de Rutas ---
# Asegura que Python encuentre la carpeta 'backend' aunque se ejecute desde la raíz
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- Crear el directorio de logs si no existe ---
LOG_DIR = 'logs'
os.makedirs(LOG_DIR, exist_ok=True)

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'elitestayanalitycs.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Importar la aplicación Flask ---
# Intentamos la importación absoluta que espera Gunicorn
try:
    from backend.api.server import app
except ImportError as e:
    logger.error(f"Error importando la app: {e}")
    # Fallback por si la estructura de carpetas varía en el entorno
    from api.server import app

# --- Función de inicialización ---
def initialize():
    """Ejecuta tareas de inicialización (BD y Scheduler)"""
    # Usamos una variable de entorno para asegurar que el scheduler 
    # solo arranque en el proceso principal y no en cada worker de Gunicorn
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not os.environ.get('GUNICORN_WORKERS'):
        logger.info("="*60)
        logger.info("🚀 ELITE STAY ANALYTICS - INICIANDO")
        logger.info("="*60)
        
        try:
            # Inicializar base de datos
            from backend.database.schema import init_database
            init_database()
            logger.info("✅ Base de datos inicializada")
            
            # Iniciar scheduler en segundo plano
            from backend.automated.scheduler import Scheduler
            scheduler = Scheduler()
            scheduler_thread = threading.Thread(target=scheduler.run)
            scheduler_thread.daemon = True
            scheduler_thread.start()
            logger.info("⏰ Programador iniciado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error durante la inicialización: {e}")

    logger.info("🌐 Instancia del servidor lista")

# Ejecutamos la inicialización
initialize()

# Exponemos 'app' para Gunicorn explícitamente
application = app

# --- Modo Desarrollo ---
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
