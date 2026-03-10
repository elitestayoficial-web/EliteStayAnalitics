# backend/automated/scheduler.py
import schedule
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self):
        self.setup_jobs()
    
    def setup_jobs(self):
        # Diario a las 2 AM
        schedule.every().day.at("02:00").do(self.daily_task)
        
        # Semanal (lunes 6 AM)
        schedule.every().monday.at("06:00").do(self.weekly_task)
        
        logger.info("Tareas programadas listas")
    
    def daily_task(self):
        logger.info("Ejecutando tarea diaria...")
        # Aquí iría la lógica diaria
        logger.info("Tarea diaria completada")
    
    def weekly_task(self):
        logger.info("Ejecutando auditoria semanal...")
        from backend.database.db_manager import DatabaseManager
        from backend.processors.semaphore_system import SemaphoreSystem
        
        db = DatabaseManager()
        semaphore = SemaphoreSystem()
        
        # Obtener hoteles
        hotels = db.search_hotels("", limit=100)
        
        alerts = 0
        for h in hotels:
            alert = semaphore.analyze_hotel(h['id'])
            if alert:
                alerts += 1
                alert['hotel_id'] = h['id']
                db.create_alert(alert)
        
        logger.info(f"Auditoria completada - {alerts} alertas generadas")
    
    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(60)