# backend/database/db_manager.py
import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.getenv('DB_PATH', 'data/elitestayanalitycs.db')

class DatabaseManager:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    # Hoteles
    def get_hotel(self, hotel_id):
        with self.get_connection() as conn:
            return conn.execute('SELECT * FROM hotels WHERE id = ?', (hotel_id,)).fetchone()
    
    def search_hotels(self, query, limit=20):
        with self.get_connection() as conn:
            return conn.execute('''
                SELECT * FROM hotels 
                WHERE name LIKE ? OR city LIKE ? 
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', limit)).fetchall()
    
    def update_hotel_score(self, hotel_id, score):
        with self.get_connection() as conn:
            conn.execute('UPDATE hotels SET overall_score = ? WHERE id = ?', (score, hotel_id))
            conn.commit()
    
    # Quejas
    def add_complaint(self, data):
        with self.get_connection() as conn:
            cur = conn.execute('''
                INSERT INTO complaints 
                (hotel_id, source, complaint_text, complaint_text_original,
                 language_detected, complaint_date, rating)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (data['hotel_id'], data['source'], data['text'], 
                  data['text_original'], data.get('language', 'en'), 
                  data['date'], data['rating']))
            conn.commit()
            return cur.lastrowid
    
    def get_unprocessed_complaints(self, limit=100):
        with self.get_connection() as conn:
            return conn.execute('''
                SELECT * FROM complaints 
                WHERE processed = 0 LIMIT ?
            ''', (limit,)).fetchall()
    
    def update_complaint(self, complaint_id, updates):
        with self.get_connection() as conn:
            conn.execute('''
                UPDATE complaints SET
                    category_primary = ?,
                    severity = ?,
                    sentiment_score = ?,
                    business_relevant = ?,
                    department = ?,
                    summary_en = ?,
                    processed = 1
                WHERE id = ?
            ''', (updates.get('category', 'other'),
                  updates.get('severity', 'minor'),
                  updates.get('sentiment', 0),
                  1 if updates.get('business_relevant') else 0,
                  updates.get('department', 'other'),
                  updates.get('summary', ''),
                  complaint_id))
            conn.commit()
    
    # Duplicados
    def mark_duplicates(self, group_hash, complaint_ids):
        with self.get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO duplicate_groups 
                (group_hash, complaint_ids, count, first_seen, last_seen)
                VALUES (?, ?, ?, date('now'), date('now'))
            ''', (group_hash, ','.join(map(str, complaint_ids)), len(complaint_ids)))
            
            for i, cid in enumerate(complaint_ids):
                conn.execute('''
                    UPDATE complaints 
                    SET duplicate_group = ?, is_duplicate = ?
                    WHERE id = ?
                ''', (group_hash, 1 if i > 0 else 0, cid))
            conn.commit()
    
    # Alertas
    def create_alert(self, alert):
        with self.get_connection() as conn:
            cur = conn.execute('''
                INSERT INTO alerts 
                (hotel_id, alert_level, alert_color, trigger_reason, 
                 complaint_count, week_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (alert['hotel_id'], alert['level'], alert['color'],
                  alert['reason'], alert['count'], alert['week_date']))
            conn.commit()
            return cur.lastrowid
    
    def get_active_alerts(self):
        with self.get_connection() as conn:
            return conn.execute('''
                SELECT a.*, h.name, h.email 
                FROM alerts a
                JOIN hotels h ON a.hotel_id = h.id
                WHERE a.week_date = date('now') AND a.email_sent = 0
            ''').fetchall()
    
    # Rankings
    def save_ranking(self, rankings):
        with self.get_connection() as conn:
            week = conn.execute('SELECT date("now")').fetchone()[0]
            conn.execute('DELETE FROM rankings WHERE week_date = ?', (week,))
            
            for r in rankings:
                conn.execute('''
                    INSERT INTO rankings (hotel_id, rank, score, week_date)
                    VALUES (?, ?, ?, ?)
                ''', (r['hotel_id'], r['rank'], r['score'], week))
            conn.commit()
    
    def get_best_hotels(self, limit=10):
        with self.get_connection() as conn:
            return conn.execute('''
                SELECT r.*, h.name, h.city 
                FROM rankings r
                JOIN hotels h ON r.hotel_id = h.id
                WHERE r.week_date = (SELECT MAX(week_date) FROM rankings)
                ORDER BY r.rank ASC LIMIT ?
            ''', (limit,)).fetchall()
    
    def get_worst_hotels(self, limit=10):
        with self.get_connection() as conn:
            return conn.execute('''
                SELECT r.*, h.name, h.city 
                FROM rankings r
                JOIN hotels h ON r.hotel_id = h.id
                WHERE r.week_date = (SELECT MAX(week_date) FROM rankings)
                ORDER BY r.rank DESC LIMIT ?
            ''', (limit,)).fetchall()