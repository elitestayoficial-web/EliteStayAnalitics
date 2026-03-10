#!/usr/bin/env python3
# main.py - Punto de entrada principal para EliteStayAnalytics (Versión Gunicorn)

import os
import threading
import logging
from dotenv import load_dotenv

# --- Crear el directorio de logs si no existe ---
LOG_DIR = 'logs'
os.makedirs(LOG_DIR, exist_ok=True)
# ------------------------------------------------

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

# --- Importar la aplicación Flask (esto es lo que Gunicorn necesita) ---
# La aplicación se define en backend/api/server.py y se importa aquí
from backend.api.server import app

# --- Función de inicialización (se ejecuta una sola vez al arrancar) ---
def initialize():
    """Función que ejecuta tareas de inicialización (base de datos, scheduler)"""
    logger.info("="*60)
    logger.info("🚀 ELITE STAY ANALYTICS - INICIANDO")
    logger.info("="*60)
    
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
    
    logger.info(f"🌐 Servidor listo para recibir peticiones")
    logger.info("Presiona Ctrl+C para detener\n")

# --- Ejecutar la inicialización cuando se importa el módulo ---
# Esto es importante: Gunicorn importa este archivo, por lo que
# la inicialización debe ocurrir en el ámbito global.
initialize()

# --- Este bloque solo se ejecuta si se llama al script directamente ---
# (Ej: python main.py para desarrollo local)
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    # En desarrollo local, ejecutamos el servidor Flask directamente
    app.run(host='0.0.0.0', port=port, debug=True)
