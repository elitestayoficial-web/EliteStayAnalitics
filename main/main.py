#!/usr/bin/env python3
# main.py - Punto de entrada principal para EliteStayAnalytics

import os
import sys
import threading
import logging
from dotenv import load_dotenv

# --- Asegurar que Python encuentra los módulos ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# --- Logs ---
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

# --- IMPORTAR LA APLICACIÓN FLASK ---
# Esta es la línea MÁS IMPORTANTE para Gunicorn
from backend.api.server import app

# --- INICIALIZACIÓN (OPCIONAL) ---
def initialize():
    """Ejecuta tareas de inicialización (base de datos, scheduler)"""
    if os.environ.get('INITIALIZED') == 'true':
        return
    
    logger.info("🚀 INICIANDO CONFIGURACIÓN")
    
    try:
        # Inicializar base de datos
        from backend.database.schema import init_database
        init_database()
        logger.info("✅ Base de datos inicializada")
        
        # Iniciar scheduler
        from backend.automated.scheduler import Scheduler
        scheduler = Scheduler()
        scheduler_thread = threading.Thread(target=scheduler.run, daemon=True)
        scheduler_thread.start()
        logger.info("⏰ Programador iniciado")
        
        os.environ['INITIALIZED'] = 'true'
    except Exception as e:
        logger.error(f"❌ Error en inicialización: {e}")

# Ejecutar inicialización en segundo plano
if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
    init_thread = threading.Thread(target=initialize, daemon=True)
    init_thread.start()

# --- PARA GUNICORN ---
# La variable 'app' ya está importada arriba
# Gunicorn buscará 'app' o 'application'
application = app  # Por si acaso

# --- MODO DESARROLLO ---
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
