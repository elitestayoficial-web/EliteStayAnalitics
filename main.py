from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "Servidor activo"

# Aquí pega el resto de tus rutas @app.route...
#!/usr/bin/env python3
# main.py - VERSIÓN COMPLETA (con todas tus rutas)

import os
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import requests

# --- Crear la aplicación Flask ---
app = Flask(__name__)
CORS(app)

# --- Configuración de la base de datos ---
DB_DIR = 'data'
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, 'elitestayanalitycs.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- RUTAS BÁSICAS (YA FUNCIONAN) ---
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

# --- RUTAS DE SEMÁFORO Y ALERTAS ---
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
        return jsonify({
            'yellow': row[0] if row else 0,
            'orange': row[1] if row else 0,
            'red': row[2] if row else 0
        })
    except Exception as e:
        return jsonify({'yellow': 0, 'orange': 0, 'red': 0})

@app.route('/api/alerts/<color>')
def get_alerts_by_color(color):
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

# --- RUTAS DE RANKINGS LOCALES ---
@app.route('/api/rankings/best')
def get_best():
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

# --- RUTAS DE HOTELES ---
@app.route('/api/hotel/<int:hotel_id>/complaints')
def get_hotel_complaints(hotel_id):
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

# --- RUTA PARA LA PÁGINA PRINCIPAL ---
@app.route('/elite')
def serve_elite():
    return send_from_directory('frontend/templates', 'elite_analytics.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend/templates', path)

# --- PUNTO DE ENTRADA PARA GUNICORN ---
application = app

# --- DATOS DE EJEMPLO PARA ACTIVAR LAS APIS ---
def init_sample_data():
    """Inicializa la base de datos con datos de ejemplo si está vacía"""
    conn = sqlite3.connect('data/elitestayanalitycs.db')
    cursor = conn.cursor()
    
    # Crear tablas si no existen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hotels (
            id INTEGER PRIMARY KEY,
            name TEXT,
            city TEXT,
            overall_score REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rankings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hotel_id INTEGER,
            rank INTEGER,
            score REAL,
            week_date TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hotel_id INTEGER,
            alert_level TEXT,
            alert_color TEXT,
            trigger_reason TEXT,
            complaint_count INTEGER,
            week_date DATE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resenas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hotel_id INTEGER,
            puntuacion REAL,
            source TEXT,
            fecha TEXT
        )
    ''')
    
    # Verificar si ya hay hoteles
    cursor.execute('SELECT COUNT(*) FROM hotels')
    if cursor.fetchone()[0] == 0:
        print("Insertando hoteles de ejemplo...")
        hoteles = [
            (1, 'Marriott Marquis', 'New York', 98),
            (2, 'Hilton Downtown', 'Chicago', 95),
            (3, 'Hyatt Regency', 'San Francisco', 92),
            (4, 'Four Seasons', 'Los Angeles', 96),
            (5, 'Ritz Carlton', 'Miami', 97),
            (6, 'Hotel Problemas', 'Las Vegas', 45),
            (7, 'Hotel Incidentes', 'Boston', 38),
            (8, 'Hotel Quejas', 'Seattle', 42),
            (9, 'Hotel Ritz Madrid', 'Madrid', 99),
            (10, 'Marriott Paris', 'Paris', 94),
            (11, 'Hilton London', 'London', 93),
            (12, 'Grand Hyatt Tokyo', 'Tokyo', 91),
        ]
        cursor.executemany('''
            INSERT INTO hotels (id, name, city, overall_score)
            VALUES (?, ?, ?, ?)
        ''', hoteles)
        
        # Insertar rankings
        week = datetime.now().strftime('%Y-%m-%d')
        rankings = [
            (9, 1, 99, week), (1, 2, 98, week), (5, 3, 97, week),
            (4, 4, 96, week), (2, 5, 95, week), (10, 6, 94, week),
            (11, 7, 93, week), (3, 8, 92, week), (12, 9, 91, week),
            (6, 10, 45, week), (8, 11, 42, week), (7, 12, 38, week),
        ]
        cursor.executemany('''
            INSERT INTO rankings (hotel_id, rank, score, week_date)
            VALUES (?, ?, ?, ?)
        ''', rankings)
        
        # Insertar alertas
        alerts = [
            (6, 'crisis', 'red', 'Múltiples quejas', 5, week),
            (7, 'crisis', 'red', 'Seguridad', 4, week),
            (8, 'crisis', 'red', 'Mantenimiento', 4, week),
            (14, 'incidencia', 'orange', 'Servicio', 3, week),
            (18, 'incidencia', 'orange', 'Aglomeraciones', 3, week),
            (13, 'alerta', 'yellow', 'Precios', 2, week),
            (15, 'alerta', 'yellow', 'WiFi', 2, week),
            (17, 'alerta', 'yellow', 'AC', 2, week),
            (19, 'alerta', 'yellow', 'Ruido', 1, week),
        ]
        for hotel_id, level, color, reason, count, week_date in alerts:
            cursor.execute('''
                INSERT INTO alerts (hotel_id, alert_level, alert_color, trigger_reason, complaint_count, week_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (hotel_id, level, color, reason, count, week_date))
        
        # Insertar reseñas de ejemplo
        import random
        for hotel_id in range(1, 13):
            for _ in range(random.randint(5, 20)):
                cursor.execute('''
                    INSERT INTO resenas (hotel_id, puntuacion, source, fecha)
                    VALUES (?, ?, 'google', ?)
                ''', (hotel_id, random.uniform(3.0, 5.0), week))
        
        conn.commit()
        print("✅ Datos de ejemplo insertados correctamente")
    
    conn.close()

# Ejecutar la inicialización al arrancar
init_sample_data()

# ========== GOOGLE PLACES API (NUEVA 2025) ==========
from dotenv import load_dotenv

# Cargar API key
load_dotenv()
GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')

if GOOGLE_PLACES_API_KEY:
    print("✅ Google Maps API Key configurada")
else:
    print("⚠️ Google Maps API no configurada")

# ========== FUNCIÓN: BUSCAR HOTELES EN GOOGLE PLACES ==========
@app.route('/api/google/places')
def buscar_google_places():
    """Busca hoteles en Google Places usando la NUEVA API (POST)"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({"error": "Se requiere parámetro 'q'"}), 400
    
    if not GOOGLE_PLACES_API_KEY:
        return jsonify({"error": "Google Maps no configurado"}), 500
    
    try:
        url = "https://places.googleapis.com/v1/places:searchText"
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': GOOGLE_PLACES_API_KEY,
            'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.priceLevel'
        }
        body = {
            "textQuery": f"hotels in {query}",
            "pageSize": 15
        }
        
        response = requests.post(url, json=body, headers=headers)
        
        if response.status_code != 200:
            return jsonify({"error": f"Error Google API: {response.status_code}"}), response.status_code
        
        data = response.json()
        lugares = data.get('places', [])
        
        resultados = []
        for lugar in lugares:
            hotel = {
                'id': lugar.get('id', ''),
                'nombre': lugar.get('displayName', {}).get('text', ''),
                'direccion': lugar.get('formattedAddress', ''),
                'ciudad': query.title(),
                'puntuacion': lugar.get('rating', 0),
                'total_resenas': lugar.get('userRatingCount', 0),
                'precio': lugar.get('priceLevel', 'N/A'),
                'source': 'google'
            }
            resultados.append(hotel)
        
        return jsonify(resultados)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/google/review-summary')
def review_summary():
    """Obtiene el resumen de reseñas de un hotel usando la API oficial de Google"""
    place_id = request.args.get('place_id', '')
    
    if not place_id:
        return jsonify({"error": "Se requiere place_id"}), 400
    
    if not GOOGLE_PLACES_API_KEY:
        return jsonify({"error": "Google Maps no configurado"}), 500
    
    try:
        url = f"https://places.googleapis.com/v1/places/{place_id}"
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': GOOGLE_PLACES_API_KEY,
            'X-Goog-FieldMask': 'displayName,reviewSummary,googleMapsLinks.reviewsUri'
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return jsonify({"error": "Error al consultar Google API"}), response.status_code
        
        data = response.json()
        
        if 'reviewSummary' in data:
            resumen = data['reviewSummary'].get('text', {}).get('text', '')
            atribucion = data['reviewSummary'].get('disclosureText', {}).get('text', 'Summarized with Gemini')
            enlace_resenas = data.get('googleMapsLinks', {}).get('reviewsUri', '')
            flag_url = data['reviewSummary'].get('flagContentUri', '')
            
            return jsonify({
                'place_id': place_id,
                'resumen': resumen,
                'atribucion': atribucion,
                'enlace_resenas': enlace_resenas,
                'flag_url': flag_url
            })
        else:
            return jsonify({
                'place_id': place_id,
                'resumen': None,
                'mensaje': 'No hay suficientes reseñas para generar un resumen automático'
            }), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def buscar_hoteles_locales(query):
    """Función de respaldo que busca en tu BD local"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, city, overall_score as puntuacion
            FROM hotels 
            WHERE LOWER(name) LIKE ? OR LOWER(city) LIKE ?
            LIMIT 10
        ''', (f'%{query.lower()}%', f'%{query.lower()}%'))
        
        results = cursor.fetchall()
        conn.close()
        
        return jsonify([{
            'id': r[0],
            'nombre': r[1],
            'ciudad': r[2],
            'puntuacion': r[3] or 0,
            'source': 'local'
        } for r in results])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ========== RANKINGS GLOBALES ==========
@app.route('/api/rankings/global/best')
def get_global_best():
    """Top 10 hoteles mejor valorados del mundo"""
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                h.id,
                h.name,
                h.city,
                COALESCE(AVG(r.puntuacion), 0) as avg_rating,
                COUNT(r.id) as total_reviews
            FROM hotels h
            LEFT JOIN resenas r ON h.id = r.hotel_id AND r.source = 'google'
            GROUP BY h.id
            HAVING COUNT(r.id) >= 1
            ORDER BY avg_rating DESC, total_reviews DESC
            LIMIT 10
        """)
        best = cursor.fetchall()
        
        resultados = []
        for row in best:
            resultados.append({
                'id': row[0],
                'name': row[1],
                'city': row[2],
                'score': round(row[3], 2),
                'reviews': row[4]
            })
        return jsonify(resultados)
        
    except Exception as e:
        print(f"Error en /api/rankings/global/best: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/rankings/global/worst')
def get_global_worst():
    """Top 10 hoteles peor valorados del mundo"""
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                h.id,
                h.name,
                h.city,
                COALESCE(AVG(r.puntuacion), 0) as avg_rating,
                COUNT(r.id) as total_reviews
            FROM hotels h
            LEFT JOIN resenas r ON h.id = r.hotel_id AND r.source = 'google'
            GROUP BY h.id
            HAVING COUNT(r.id) >= 1
            ORDER BY avg_rating ASC, total_reviews DESC
            LIMIT 10
        """)
        worst = cursor.fetchall()
        
        resultados = []
        for row in worst:
            resultados.append({
                'id': row[0],
                'name': row[1],
                'city': row[2],
                'score': round(row[3], 2),
                'reviews': row[4]
            })
        return jsonify(resultados)
        
    except Exception as e:
        print(f"Error en /api/rankings/global/worst: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500
    finally:
        if conn:
            conn.close()

# ========== SEMÁFORO INTELIGENTE GLOBAL ==========
@app.route('/api/semaphore/global/stats')
def get_global_semaphore_stats():
    """Estadísticas globales del semáforo basadas en puntuaciones de reseñas"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN AVG(r.puntuacion) >= 4.5 THEN 1 END) as excelente,
                COUNT(CASE WHEN AVG(r.puntuacion) BETWEEN 4.0 AND 4.4 THEN 1 END) as bueno,
                COUNT(CASE WHEN AVG(r.puntuacion) BETWEEN 3.5 AND 3.9 THEN 1 END) as regular,
                COUNT(CASE WHEN AVG(r.puntuacion) BETWEEN 3.0 AND 3.4 THEN 1 END) as malo,
                COUNT(CASE WHEN AVG(r.puntuacion) < 3.0 THEN 1 END) as pesimo
            FROM hotels h
            JOIN resenas r ON h.id = r.hotel_id
            WHERE r.source = 'google'
            GROUP BY h.id
        """)
        stats = cursor.fetchone()
        conn.close()
        
        return jsonify({
            'excelente': stats[0] if stats else 0,
            'bueno': stats[1] if stats else 0,
            'regular': stats[2] if stats else 0,
            'malo': stats[3] if stats else 0,
            'pesimo': stats[4] if stats else 0
        })
    except Exception as e:
        print(f"Error en /api/semaphore/global/stats: {e}")
        return jsonify({"error": "Error interno"}), 500

@app.route('/api/semaphore/global/alerts/<category>')
def get_global_alerts(category):
    """Lista de hoteles por categoría de puntuación"""
    categories = {
        'excelente': (4.5, 5.1),
        'bueno': (4.0, 4.5),
        'regular': (3.5, 4.0),
        'malo': (3.0, 3.5),
        'pesimo': (0, 3.0)
    }
    
    min_score, max_score = categories.get(category, (0, 5))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                h.id,
                h.name,
                h.city,
                AVG(r.puntuacion) as avg_score,
                COUNT(r.id) as total_reviews
            FROM hotels h
            JOIN resenas r ON h.id = r.hotel_id
            WHERE r.source = 'google'
            GROUP BY h.id
            HAVING AVG(r.puntuacion) BETWEEN ? AND ?
            ORDER BY avg_score DESC
            LIMIT 10
        """, (min_score, max_score))
        alerts = cursor.fetchall()
        conn.close()
        
        return jsonify([{
            'id': a[0],
            'name': a[1],
            'city': a[2],
            'avg_score': round(a[3], 2),
            'total_reviews': a[4]
        } for a in alerts])
    except Exception as e:
        print(f"Error en /api/semaphore/global/alerts: {e}")
        return jsonify([]), 500

# ========== DETALLES DE HOTEL POR PLACE ID (VERSIÓN ÚNICA Y MEJORADA) ==========
@app.route('/api/google/place/<place_id>')
def detalle_google_place(place_id):
    """Obtiene detalles completos de un hotel incluyendo reseñas"""
    if not GOOGLE_PLACES_API_KEY:
        return jsonify({"error": "Google Maps no configurado"}), 500
    
    try:
        # URL de la API de Places (detalles) con fieldmask COMPLETO
        url = f"https://places.googleapis.com/v1/places/{place_id}"
        
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': GOOGLE_PLACES_API_KEY,
            # Incluir reviewSummary para obtener resumen IA
            'X-Goog-FieldMask': 'id,displayName,formattedAddress,rating,userRatingCount,priceLevel,reviews,websiteUri,nationalPhoneNumber,reviewSummary,googleMapsLinks.reviewsUri'
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return jsonify({"error": f"Error Google API: {response.status_code}"}), response.status_code
        
        data = response.json()
        
        # Procesar el resumen de reseñas si existe
        review_summary = None
        if 'reviewSummary' in data:
            review_summary = {
                'text': data['reviewSummary'].get('text', {}).get('text', ''),
                'disclosureText': data['reviewSummary'].get('disclosureText', {}).get('text', 'Resumido con Gemini'),
                'reviewsUri': data.get('googleMapsLinks', {}).get('reviewsUri', '')
            }
        
        # Transformar al formato que espera tu frontend
        resultado = {
            'place_id': data.get('id', ''),
            'nombre': data.get('displayName', {}).get('text', ''),
            'direccion': data.get('formattedAddress', ''),
            'puntuacion': data.get('rating', 0),
            'total_resenas': data.get('userRatingCount', 0),
            'precio': data.get('priceLevel', 'N/A'),
            'website': data.get('websiteUri', ''),
            'telefono': data.get('nationalPhoneNumber', ''),
            'reviews': data.get('reviews', []),
            'reviewSummary': review_summary  # NUEVO: resumen IA de reseñas
        }
        
        return jsonify(resultado)
        
    except Exception as e:
        print(f"Error en detalle_google_place: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port)














