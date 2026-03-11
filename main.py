import os
import sqlite3
import requests  # <-- Añadido para conectar con Google
from datetime import datetime
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS

# --- Crear la aplicación Flask ---
app = Flask(__name__)
CORS(app)

# CONFIGURACIÓN GOOGLE API
GOOGLE_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY') # <-- PEGA AQUÍ TU CLAVE

# --- Configuración de la base de datos ---
DB_DIR = 'data'
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, 'elitestayanalitycs.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- RUTA NUEVA: BUSCADOR INTERACTIVO CON GOOGLE ---
@app.route('/api/get_google_data/<hotel_name>')
def get_google_data(hotel_name):
    try:
        # 1. Buscar el lugar para obtener el Place ID y el rating básico
        search_url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={hotel_name}&inputtype=textquery&fields=place_id,rating,user_ratings_total,formatted_address&key={GOOGLE_API_KEY}"
        search_res = requests.get(search_url).json()
        
        if search_res.get('candidates'):
            hotel_data = search_res['candidates'][0]
            return jsonify({
                "status": "success",
                "name": hotel_name,
                "rating": hotel_data.get('rating', 'N/A'),
                "user_ratings_total": hotel_data.get('user_ratings_total', 0),
                "address": hotel_data.get('formatted_address', '')
            })
        return jsonify({"status": "not_found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- TUS RUTAS ORIGINALES (MANTENIDAS) ---
@app.route('/')
def home():
    return jsonify({'name': 'Elite Stay Analytics', 'status': 'online', 'version': '1.0.0'})

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/semaphore/stats')
def get_semaphore_stats():
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
        return jsonify({'yellow': row[0] if row else 0, 'orange': row[1] if row else 0, 'red': row[2] if row else 0})
    except:
        return jsonify({'yellow': 0, 'orange': 0, 'red': 0})

@app.route('/api/alerts/<color>')
def get_alerts_by_color(color):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT h.name, a.complaint_count as count
            FROM alerts a
            JOIN hotels h ON a.hotel_id = h.id
            WHERE a.alert_color = ? AND a.week_date = date('now')
            ORDER BY a.complaint_count DESC
        ''', (color,))
        alerts = cursor.fetchall()
        conn.close()
        return jsonify([dict(a) for a in alerts])
    except:
        return jsonify([])

@app.route('/api/rankings/best')
def get_best():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT h.id, h.name, h.city, h.overall_score as score FROM hotels h ORDER BY h.overall_score DESC LIMIT 10')
        hotels = cursor.fetchall()
        conn.close()
        return jsonify([dict(h) for h in hotels])
    except:
        return jsonify([])

@app.route('/api/rankings/worst')
def get_worst():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT h.id, h.name, h.city, h.overall_score as score FROM hotels h WHERE h.overall_score IS NOT NULL ORDER BY h.overall_score ASC LIMIT 10')
        hotels = cursor.fetchall()
        conn.close()
        return jsonify([dict(h) for h in hotels])
    except:
        return jsonify([])

@app.route('/api/hotel/search')
def search_hotels():
    query = request.args.get('q', '').strip().lower()
    if not query: return jsonify([])
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, city FROM hotels WHERE LOWER(name) LIKE ? LIMIT 10', (f'%{query}%',))
    results = cursor.fetchall()
    conn.close()
    return jsonify([dict(r) for r in results])

@app.route('/elite')
def serve_elite():
    return send_from_directory('frontend/templates', 'elite_analytics.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend/templates', path)

application = app

# --- TU INICIALIZACIÓN DE DATOS (MANTENIDA) ---
def init_sample_data():
    conn = sqlite3.connect('data/elitestayanalitycs.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS hotels (id INTEGER PRIMARY KEY, name TEXT, city TEXT, overall_score REAL)')
    cursor.execute('CREATE TABLE IF NOT EXISTS rankings (id INTEGER PRIMARY KEY AUTOINCREMENT, hotel_id INTEGER, rank INTEGER, score REAL, week_date TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS alerts (id INTEGER PRIMARY KEY AUTOINCREMENT, hotel_id INTEGER, alert_level TEXT, alert_color TEXT, trigger_reason TEXT, complaint_count INTEGER, week_date DATE)')
    
    cursor.execute('SELECT COUNT(*) FROM hotels')
    if cursor.fetchone()[0] == 0:
        hoteles = [(1, 'Marriott Marquis', 'New York', 98), (9, 'Hotel Ritz Madrid', 'Madrid', 99)]
        cursor.executemany('INSERT INTO hotels (id, name, city, overall_score) VALUES (?, ?, ?, ?)', hoteles)
        conn.commit()
    conn.close()

init_sample_data()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
@app.route('/api/get_google_data/<hotel_name>')
def get_google_data(hotel_name):
    # Sustituye con tu clave real
    GOOGLE_API_KEY =os.getenv('GOOGLE_PLACES_API_KEY')
    try:
        import requests
        search_url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={hotel_name}&inputtype=textquery&fields=place_id,rating,user_ratings_total,formatted_address&key={GOOGLE_API_KEY}"
        response = requests.get(search_url).json()
        if response.get('candidates'):
            hotel = response['candidates'][0]
            return jsonify({
                "status": "success",
                "rating": hotel.get('rating', 0),
                "user_ratings_total": hotel.get('user_ratings_total', 0)
            })
        return jsonify({"status": "not_found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500






