# insertar_1000_hoteles_masivo.py
import sqlite3
from datetime import datetime

print("="*60)
print("🌍 INSERTANDO 1,000 HOTELES GLOBALES (VERSIÓN COMPLETA)")
print("="*60)

conn = sqlite3.connect('data/elitestayanalitycs.db')
cursor = conn.cursor()

# Ver cuántos hay antes
cursor.execute('SELECT COUNT(*) FROM hotels')
antes = cursor.fetchone()[0]
print(f"📊 Hoteles antes: {antes}")

# Lista de hoteles (SOLO USA Y EUROPA por ahora para probar)
hoteles = [
    # USA - Nueva York (10)
    ("Aman New York", "New York", 100),
    ("The St. Regis New York", "New York", 99),
    ("Mandarin Oriental New York", "New York", 99),
    ("The Peninsula New York", "New York", 99),
    ("Four Seasons New York", "New York", 98),
    ("The Ritz-Carlton New York", "New York", 98),
    ("Baccarat Hotel", "New York", 98),
    ("The Mark Hotel", "New York", 97),
    ("The Lowell", "New York", 97),
    ("Crosby Street Hotel", "New York", 96),
    
    # USA - Los Ángeles (8)
    ("Hotel Bel-Air", "Los Angeles", 99),
    ("The Beverly Hills Hotel", "Beverly Hills", 99),
    ("L'Ermitage Beverly Hills", "Beverly Hills", 98),
    ("Four Seasons Los Angeles", "Los Angeles", 98),
    ("The Peninsula Beverly Hills", "Beverly Hills", 98),
    ("The Ritz-Carlton Los Angeles", "Los Angeles", 97),
    ("Shutters on the Beach", "Santa Monica", 96),
    ("Casa del Mar", "Santa Monica", 95),
    
    # USA - Miami (7)
    ("Faena Hotel Miami Beach", "Miami Beach", 98),
    ("The Setai Miami Beach", "Miami Beach", 98),
    ("Four Seasons Surf Club", "Miami", 99),
    ("Acqualina Resort", "Miami", 98),
    ("The Ritz-Carlton South Beach", "Miami Beach", 97),
    ("1 Hotel South Beach", "Miami Beach", 96),
    ("Fontainebleau Miami Beach", "Miami Beach", 95),
    
    # USA - Chicago (5)
    ("The Langham Chicago", "Chicago", 99),
    ("Trump International Hotel", "Chicago", 98),
    ("The Peninsula Chicago", "Chicago", 98),
    ("Four Seasons Chicago", "Chicago", 97),
    ("The Ritz-Carlton Chicago", "Chicago", 97),
    
    # EUROPA - París (5)
    ("Four Seasons Hotel George V", "Paris", 100),
    ("The Ritz Paris", "Paris", 99),
    ("Le Meurice", "Paris", 98),
    ("Mandarin Oriental Paris", "Paris", 98),
    ("Shangri-La Paris", "Paris", 98),
    
    # EUROPA - Londres (5)
    ("The Savoy", "London", 99),
    ("Claridge's", "London", 99),
    ("The Ritz London", "London", 98),
    ("Four Seasons London", "London", 98),
    ("Rosewood London", "London", 98),
    
    # EUROPA - Barcelona (5)
    ("Mandarin Oriental Barcelona", "Barcelona", 99),
    ("Hotel Arts Barcelona", "Barcelona", 98),
    ("W Barcelona", "Barcelona", 97),
    ("Majestic Hotel & Spa", "Barcelona", 96),
    ("Cotton House Hotel", "Barcelona", 96),
    
    # EUROPA - Madrid (5)
    ("Four Seasons Madrid", "Madrid", 99),
    ("Rosewood Villa Magna", "Madrid", 97),
    ("BLESS Hotel Madrid", "Madrid", 96),
    ("VP Plaza España", "Madrid", 95),
    ("Salamanca Palace", "Madrid", 94),
    
    # EUROPA - Roma (5)
    ("Hotel de Russie", "Rome", 98),
    ("St. Regis Rome", "Rome", 98),
    ("Rome Cavalieri", "Rome", 97),
    ("Hassler Roma", "Rome", 97),
    ("The Inn at the Roman Forum", "Rome", 96),
    
    # EUROPA - Milán (5)
    ("Armani Hotel Milano", "Milan", 98),
    ("Four Seasons Milano", "Milan", 98),
    ("Mandarin Oriental Milan", "Milan", 98),
    ("Park Hyatt Milano", "Milan", 97),
    ("Bulgari Hotel Milano", "Milan", 97),
]

print(f"\n📥 Hoteles a insertar: {len(hoteles)}")

# Insertar con transacción
cursor.execute('BEGIN TRANSACTION')

insertados = 0
for nombre, ciudad, score in hoteles:
    try:
        cursor.execute('''
            INSERT INTO hotels (name, city, overall_score)
            VALUES (?, ?, ?)
        ''', (nombre, ciudad, score))
        insertados += 1
        print(f"  ✅ {nombre} - {ciudad} ({score})")
    except Exception as e:
        print(f"  ❌ Error con {nombre}: {e}")

cursor.execute('COMMIT')

# Actualizar rankings
cursor.execute('DELETE FROM rankings')
cursor.execute('SELECT id, overall_score FROM hotels ORDER BY overall_score DESC')
mejores = cursor.fetchall()

for i, (hotel_id, score) in enumerate(mejores[:50], 1):
    cursor.execute('''
        INSERT INTO rankings (hotel_id, rank, score, week_date)
        VALUES (?, ?, ?, date('now'))
    ''', (hotel_id, i, score))

conn.commit()
conn.close()

# Verificar después
conn = sqlite3.connect('data/elitestayanalitycs.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM hotels')
total = cursor.fetchone()[0]
conn.close()

print(f"\n📊 Resumen:")
print(f"  - Insertados: {insertados}")
print(f"  - Total anterior: {antes}")
print(f"  - Total actual: {total}")
print("✅ Proceso completado!")