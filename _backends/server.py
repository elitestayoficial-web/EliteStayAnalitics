# backend/api/server.py
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime
# backend/api/server.py
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime

# Importar el DatabaseManager
from backend.database.db_manager import DatabaseManager

app = Flask(__name__, 
            static_folder='../../frontend/static',
            template_folder='../../frontend/templates')
CORS(app)

# Inicializar DatabaseManager
db = DatabaseManager()

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
        conn = sqlite3.connect('data/elitestayanalitycs.db')
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
        conn = sqlite3.connect('data/elitestayanalitycs.db')
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
    """
    Obtiene los mejores hoteles desde la base de datos
    """
    try:
        hotels = db.get_best_hotels(10)
        if hotels and len(hotels) > 0:
            # Convertir las filas de sqlite3.Row a diccionarios
            result = []
            for h in hotels:
                result.append({
                    'name': h['name'] if h['name'] else 'Hotel sin nombre',
                    'city': h['city'] if h['city'] else '',
                    'score': float(h['score']) if h['score'] else 0
                })
            return jsonify(result)
        else:
            # Si no hay datos, devolver un mensaje claro
            return jsonify([{
                'name': 'No hay datos disponibles',
                'city': 'Agrega hoteles a la BD',
                'score': 0
            }])
    except Exception as e:
        print(f"Error en get_best: {e}")
        return jsonify([{
            'name': 'Error al cargar datos',
            'city': str(e),
            'score': 0
        }])

@app.route('/api/rankings/worst')
def get_worst():
    """
    Obtiene los peores hoteles desde la base de datos
    """
    try:
        hotels = db.get_worst_hotels(10)
        if hotels and len(hotels) > 0:
            result = []
            for h in hotels:
                result.append({
                    'name': h['name'] if h['name'] else 'Hotel sin nombre',
                    'city': h['city'] if h['city'] else '',
                    'score': float(h['score']) if h['score'] else 0
                })
            return jsonify(result)
        else:
            return jsonify([{
                'name': 'No hay datos disponibles',
                'city': 'Agrega hoteles a la BD',
                'score': 0
            }])
    except Exception as e:
        print(f"Error en get_worst: {e}")
        return jsonify([{
            'name': 'Error al cargar datos',
            'city': str(e),
            'score': 0
        }])

# Ruta ESPECÍFICA para elite_analytics.html
@app.route('/elite')
def serve_elite():
    return send_from_directory('../../frontend/templates', 'elite_analytics.html')

# Ruta genérica para archivos estáticos
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../../frontend/templates', path)
@app.route('/api/hotel/<int:hotel_id>/complaints')
def get_hotel_complaints(hotel_id):
    """Obtiene todas las quejas de un hotel específico"""
    try:
        conn = sqlite3.connect('data/elitestayanalitycs.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM complaints 
            WHERE hotel_id = ? 
            ORDER BY 
                CASE severity 
                    WHEN 'critical' THEN 1 
                    WHEN 'moderate' THEN 2 
                    ELSE 3 
                END,
                complaint_date DESC
        ''', (hotel_id,))
        
        complaints = cursor.fetchall()
        conn.close()
        
        return jsonify([dict(c) for c in complaints])
    except Exception as e:
        print(f"Error: {e}")
        return jsonify([])
@app.route('/api/hotel/search')
def search_hotels():
    """Search hotels by name, city, or ID"""
    try:
        query = request.args.get('q', '').strip().lower()
        
        if not query:
            return jsonify([])
        
        conn = sqlite3.connect('data/elitestayanalitycs.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Buscar por ID exacto
        if query.isdigit():
            cursor.execute('''
                SELECT id, name, city, overall_score 
                FROM hotels 
                WHERE id = ?
            ''', (int(query),))
        else:
            # Buscar por nombre o ciudad
            cursor.execute('''
                SELECT id, name, city, overall_score 
                FROM hotels 
                WHERE LOWER(name) LIKE ? OR LOWER(city) LIKE ?
                ORDER BY overall_score DESC
                LIMIT 10
            ''', (f'%{query}%', f'%{query}%'))
        
        results = cursor.fetchall()
        conn.close()
        
        return jsonify([dict(r) for r in results])
        
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify([])
if __name__ == '__main__':
    app.run(debug=True, port=5000)