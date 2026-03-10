#!/usr/bin/env python3
# main.py - Punto de entrada principal para EliteStayAnalytics (Versión Gunicorn)

import os
import sys
import threading
import logging
from dotenv import load_dotenv

# --- Configuración de Rutas (para que Python encuentre 'backend') ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# --- Crear el directorio de logs si no existe ---
LOG_DIR = os.path.join(BASE_DIR, 'logs')
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
    logger.error(f"Error importando backend: {e}")
    # Fallback por si la estructura es diferente
    from api.server import app

# --- Función de inicialización (se ejecuta una sola vez al arrancar) ---
def initialize():
    """Ejecuta tareas de inicialización (base de datos, scheduler)"""
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
        logger.info("⏰ Programador iniciado")
        
        logger.info("🌐 Servidor listo para recibir peticiones")
        
    except Exception as e:
        logger.error(f"❌ Error durante la inicialización: {e}")

# --- Ejecutar la inicialización ---
initialize()

# --- Exponer la aplicación para Gunicorn (redundante pero seguro) ---
application = app

# --- Bloque para ejecución local ---
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Iniciando servidor de desarrollo en puerto {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
