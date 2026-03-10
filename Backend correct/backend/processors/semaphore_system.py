# backend/processors/semaphore_system.py
import sqlite3
from datetime import datetime
import os

class SemaphoreSystem:
    def __init__(self, db_path='data/elitestayanalitycs.db'):
        self.db_path = db_path
    
    def analyze_hotel(self, hotel_id, week_date=None):
        if not week_date:
            week_date = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM complaints
            WHERE hotel_id = ? AND complaint_date >= date('now', '-7 days')
            AND (is_duplicate = 0 OR is_duplicate IS NULL)
        ''', (hotel_id,))
        
        complaints = cursor.fetchall()
        
        if not complaints:
            conn.close()
            return None
        
        # Verificar quejas graves
        grave = [c for c in complaints if c['is_grave']]
        if grave:
            alert = {
                'level': 'crisis',
                'color': 'red',
                'reason': f"{len(grave)} queja(s) grave(s)",
                'count': len(complaints),
                'week_date': week_date
            }
            self._save_alert(hotel_id, alert, cursor)
            conn.commit()
            conn.close()
            return alert
        
        # Volumen alto
        if len(complaints) >= 10:
            alert = {
                'level': 'crisis',
                'color': 'red',
                'reason': f"{len(complaints)} quejas totales",
                'count': len(complaints),
                'week_date': week_date
            }
            self._save_alert(hotel_id, alert, cursor)
            conn.commit()
            conn.close()
            return alert
        
        # Mismo departamento
        from collections import Counter
        depts = Counter(c['department'] for c in complaints if c['department'])
        for dept, count in depts.items():
            if 3 <= count <= 5:
                alert = {
                    'level': 'incidencia',
                    'color': 'orange',
                    'reason': f"{count} quejas en {dept}",
                    'count': len(complaints),
                    'week_date': week_date
                }
                self._save_alert(hotel_id, alert, cursor)
                conn.commit()
                conn.close()
                return alert
        
        # Variadas
        if len(complaints) >= 3:
            alert = {
                'level': 'alerta',
                'color': 'yellow',
                'reason': f"{len(complaints)} quejas variadas",
                'count': len(complaints),
                'week_date': week_date
            }
            self._save_alert(hotel_id, alert, cursor)
            conn.commit()
            conn.close()
            return alert
        
        conn.close()
        return None
    
    def _save_alert(self, hotel_id, alert, cursor):
        cursor.execute('''
            INSERT INTO alerts 
            (hotel_id, alert_level, alert_color, trigger_reason, complaint_count, week_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (hotel_id, alert['level'], alert['color'], alert['reason'], alert['count'], alert['week_date']))
