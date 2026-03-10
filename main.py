#!/usr/bin/env python3
# main.py - Punto de entrada principal para EliteStayAnalytics

import os
import threading
import logging
from dotenv import load_dotenv

# === NUEVO: Crear el directorio de logs si no existe ===
LOG_DIR = 'logs'
os.makedirs(LOG_DIR, exist_ok=True)
# =====================================================

# Cargar variables de entorno
load_dotenv()

# Configurar logging (ahora con ruta segura)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'elitestayanalitycs.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Función principal que inicia todos los servicios"""
    
    logger.info("="*60)
    logger.info("🚀 ELITE STAY ANALYTICS - INICIANDO")
    logger.info("="*60)
    
    # Importar módulos
    from backend.database.schema import init_database
    from backend.automated.scheduler import Scheduler
    from backend.api.server import app
    
    # Inicializar base de datos
    init_database()
    logger.info("✅ Base de datos inicializada")
    
    # Iniciar scheduler en segundo plano
    scheduler = Scheduler()
    scheduler_thread = threading.Thread(target=scheduler.run)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    logger.info("⏰ Programador iniciado")
    
    # Iniciar servidor
    port = int(os.getenv('PORT', 5000))
    logger.info(f"🌐 Servidor en http://localhost:{port}")
    logger.info("Presiona Ctrl+C para detener\n")
    
    try:
        # IMPORTANTE: En producción, debug debe estar en False
        app.run(host='0.0.0.0', port=port, debug=False)
    except KeyboardInterrupt:
        logger.info("👋 Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error en el servidor: {e}")

if __name__ == '__main__':
    main()
