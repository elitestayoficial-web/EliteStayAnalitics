#!/usr/bin/env python3
import os
import sys
import threading
import logging

# 1. Forzar que Python vea la raíz del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# 2. Configurar Logging para ver errores en Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 3. IMPORTACIÓN CRÍTICA
# Como tus archivos están en la raíz, importamos directamente 'app' de 'server'
try:
    from server import app
    logger.info("✅ App importada exitosamente desde server.py")
except ImportError as e:
    logger.error(f"❌ No se encontró server.py o la variable app: {e}")
    # Plan B: Si por alguna razón los archivos están dentro de 'backend'
    try:
        sys.path.append(os.path.join(BASE_DIR, 'backend'))
        from server import app
        logger.info("✅ App importada desde la subcarpeta backend")
    except ImportError:
        logger.error("❌ ERROR FATAL: No se encuentra el objeto 'app' en ningún lado.")
        sys.exit(1)

# 4. INICIALIZACIÓN DE SERVICIOS (DB y Scheduler)
def initialize_services():
    try:
        # Importamos las funciones de tus otros archivos sueltos
        from schema import init_database
        from scheduler import Scheduler
        
        init_database()
        logger.info("✅ Base de datos inicializada")
        
        sc = Scheduler()
        thread = threading.Thread(target=sc.run, daemon=True)
        thread.start()
        logger.info("⏰ Scheduler iniciado en segundo plano")
    except Exception as e:
        logger.error(f"⚠️ Error al iniciar servicios secundarios: {e}")

# Ejecutar servicios antes de que Gunicorn tome el mando
initialize_services()

# 5. PARA GUNICORN
# Esta línea es la que está fallando. Aseguramos que la variable se llame 'app'
# al nivel principal del archivo.
application = app 
app = application
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

