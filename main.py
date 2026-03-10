#!/usr/bin/env python3
# main.py - Aplicación Flask completa (Sin importaciones externas de server.py)

import os
import sys
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS

# --- Crear la aplicación Flask ---
app = Flask(__name__)
CORS(app)

# --- Configuración de la base de datos ---
# Asegurar que el directorio para la base de datos existe
DB_DIR = 'data'
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, 'elitestayanalitycs.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- RUTAS DE LA API (Copia de tu server.py) ---

@app.route('/')
def home():
    return jsonify({
        'name': 'Elite Stay Analytics',
        'status': 'online',
        'version': '1.0.0'
    })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/semaphore/stats')
def get_semaphore_stats():
    """Get semaphore statistics"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN alert_color = 'yellow' THEN 1 END) as yellow,
                COUNT(CASE WHEN alert_color = 'orange' THEN 1 END) as orange,
                COUNT(CASE WHEN alert_color = 'red' THEN 1 END) as red
            FROM alerts
            WHERE week_date = date('now')
        ''')
        row = cursor.fetchone()
        conn.close()
        return jsonify({
            'yellow': row[0] if row else 0,
            'orange': row[1] if row else 0,
            'red': row[2] if row else 0
        })
    except Exception as e:
        return jsonify({'yellow': 0, 'orange': 0, 'red': 0})

@app.route('/api/alerts/<color>')
def get_alerts_by_color(color):
    """Get hotels with specific alert color"""
    try:
        conn = get_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT h.name, a.complaint_count as count
            FROM alerts a
            JOIN hotels h ON a.hotel_id = h.id
            WHERE a.alert_color = ? AND a.week_date = date('now')
            ORDER BY a.complaint_count DESC
            LIMIT 10
        ''', (color,))
        alerts = cursor.fetchall()
        conn.close()
        return jsonify([dict(a) for a in alerts])
    except Exception as e:
        return jsonify([])

@app.route('/api/rankings/best')
def get_best():
    """Obtiene los mejores hoteles"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT h.id, h.name, h.city, h.overall_score as score
            FROM hotels h
            ORDER BY h.overall_score DESC
            LIMIT 10
        ''')
        hotels = cursor.fetchall()
        conn.close()
        return jsonify([dict(h) for h in hotels])
    except Exception as e:
        return jsonify([])

@app.route('/api/rankings/worst')
def get_worst():
    """Obtiene los peores hoteles"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT h.id, h.name, h.city, h.overall_score as score
            FROM hotels h
            WHERE h.overall_score IS NOT NULL
            ORDER BY h.overall_score ASC
            LIMIT 10
        ''')
        hotels = cursor.fetchall()
        conn.close()
        return jsonify([dict(h) for h in hotels])
    except Exception as e:
        return jsonify([])

@app.route('/api/hotel/<int:hotel_id>/complaints')
def get_hotel_complaints(hotel_id):
    """Obtiene todas las quejas de un hotel"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM complaints 
            WHERE hotel_id = ? 
            ORDER BY complaint_date DESC
        ''', (hotel_id,))
        complaints = cursor.fetchall()
        conn.close()
        return jsonify([dict(c) for c in complaints])
    except Exception as e:
        return jsonify([])

@app.route('/api/hotel/search')
def search_hotels():
    """Search hotels by name, city, or ID"""
    try:
        query = request.args.get('q', '').strip().lower()
        if not query:
            return jsonify([])
        
        conn = get_db()
        cursor = conn.cursor()
        
        if query.isdigit():
            cursor.execute('SELECT id, name, city FROM hotels WHERE id = ?', (int(query),))
        else:
            cursor.execute('''
                SELECT id, name, city FROM hotels 
                WHERE LOWER(name) LIKE ? OR LOWER(city) LIKE ?
                LIMIT 10
            ''', (f'%{query}%', f'%{query}%'))
        
        results = cursor.fetchall()
        conn.close()
        return jsonify([dict(r) for r in results])
    except Exception as e:
        return jsonify([])

@app.route('/elite')
def serve_elite():
    return send_from_directory('frontend/templates', 'elite_analytics.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend/templates', path)

# --- PUNTO DE ENTRADA PARA GUNICORN Y DESARROLLO LOCAL ---
# Gunicorn buscará la variable 'app' (definida arriba).
# Creamos un alias por compatibilidad, aunque no es estrictamente necesario.
application = app

if __name__ == '__main__':
    # Usar el puerto de la variable de entorno PORT (Render lo inyecta automáticamente)
    port = int(os.getenv('PORT', 10000))
    print(f"Iniciando servidor de desarrollo en puerto {port}...")
    # ¡CRUCIAL! Vincular a 0.0.0.0 para que Render pueda enrutar el tráfico.
    app.run(host='0.0.0.0', port=port)



