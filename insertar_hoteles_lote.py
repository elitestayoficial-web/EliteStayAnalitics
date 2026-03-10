# insertar_hoteles_lote.py
import sqlite3
from datetime import datetime

print("="*60)
print("🏨 INSERTANDO LOTE DE HOTELES")
print("="*60)

conn = sqlite3.connect('data/elitestayanalitycs.db')
cursor = conn.cursor()

# Verificar estado actual
cursor.execute('SELECT COUNT(*) FROM hotels')
total_antes = cursor.fetchone()[0]
print(f"📊 Hoteles antes: {total_antes}")

# Obtener el último ID
cursor.execute('SELECT MAX(id) FROM hotels')
ultimo_id = cursor.fetchone()[0] or 0
print(f"🔢 Último ID usado: {ultimo_id}")

# LISTA DE HOTELES (SOLO con las columnas que existen)
# Asumiendo que tu tabla tiene: id, name, city, overall_score
hoteles_nuevos = [
    # NUEVA YORK
    ("The St. Regis New York", "New York", 99),
    ("Mandarin Oriental New York", "New York", 99),
    ("Aman New York", "New York", 100),
    ("The Peninsula New York", "New York", 99),
    ("Four Seasons New York", "New York", 98),
    ("The Ritz-Carlton New York", "New York", 98),
    ("Baccarat Hotel", "New York", 98),
    ("The Mark Hotel", "New York", 97),
    ("The Lowell", "New York", 97),
    ("Crosby Street Hotel", "New York", 96),
    
    # LOS ANGELES
    ("Hotel Bel-Air", "Los Angeles", 99),
    ("The Beverly Hills Hotel", "Beverly Hills", 99),
    ("L'Ermitage Beverly Hills", "Beverly Hills", 98),
    ("Four Seasons Los Angeles", "Los Angeles", 98),
    ("The Peninsula Beverly Hills", "Beverly Hills", 98),
    ("The Ritz-Carlton Los Angeles", "Los Angeles", 97),
    ("Shutters on the Beach", "Santa Monica", 96),
    ("Casa del Mar", "Santa Monica", 95),
    
    # MIAMI
    ("Faena Hotel Miami Beach", "Miami Beach", 98),
    ("The Setai Miami Beach", "Miami Beach", 98),
    ("Four Seasons Surf Club", "Miami", 99),
    ("Acqualina Resort", "Miami", 98),
    ("The Ritz-Carlton South Beach", "Miami Beach", 97),
    ("1 Hotel South Beach", "Miami Beach", 96),
    ("Fontainebleau Miami Beach", "Miami Beach", 95),
    
    # CHICAGO
    ("The Langham Chicago", "Chicago", 99),
    ("Trump International Hotel", "Chicago", 98),
    ("The Peninsula Chicago", "Chicago", 98),
    ("Four Seasons Chicago", "Chicago", 97),
    ("The Ritz-Carlton Chicago", "Chicago", 97),
    
    # LAS VEGAS
    ("Wynn Las Vegas", "Las Vegas", 98),
    ("Encore at Wynn Las Vegas", "Las Vegas", 98),
    ("The Palazzo Resort", "Las Vegas", 97),
    ("The Venetian Resort", "Las Vegas", 96),
    ("ARIA Resort & Casino", "Las Vegas", 96),
    
    # SAN FRANCISCO
    ("Four Seasons San Francisco", "San Francisco", 97),
    ("The Ritz-Carlton San Francisco", "San Francisco", 97),
    ("Fairmont San Francisco", "San Francisco", 95),
    ("The St. Regis San Francisco", "San Francisco", 96),
    ("The Scarlet Huntington", "San Francisco", 94),
    
    # HAWAII
    ("Four Seasons Resort Hualalai", "Hawaii", 100),
    ("Four Seasons Resort Lanai", "Lanai", 99),
    ("Halekulani Honolulu", "Honolulu", 98),
    ("The Ritz-Carlton Kapalua", "Maui", 97),
    ("Mauna Kea Beach Hotel", "Hawaii", 96),
    
    # BOSTON
    ("Mandarin Oriental Boston", "Boston", 98),
    ("Raffles Boston", "Boston", 98),
    ("Four Seasons Boston", "Boston", 97),
    
    # WASHINGTON DC
    ("The Hay-Adams", "Washington D.C.", 97),
    ("Rosewood Washington D.C.", "Washington D.C.", 97),
]

print(f"\n📥 Hoteles a insertar: {len(hoteles_nuevos)}")

# Insertar
insertados = 0
for nombre, ciudad, score in hoteles_nuevos:
    try:
        cursor.execute('''
            INSERT INTO hotels (name, city, overall_score)
            VALUES (?, ?, ?)
        ''', (nombre, ciudad, score))
        insertados += 1
        print(f"  ✅ {nombre} - {ciudad} (score: {score})")
    except Exception as e:
        print(f"  ❌ Error con {nombre}: {e}")

conn.commit()

# Verificar nuevo total
cursor.execute('SELECT COUNT(*) FROM hotels')
total_despues = cursor.fetchone()[0]

print(f"\n📊 Resumen:")
print(f"  - Insertados: {insertados}")
print(f"  - Total anterior: {total_antes}")
print(f"  - Total actual: {total_despues}")

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
print(f"🏆 Rankings actualizados con {min(50, len(mejores))} hoteles")

conn.close()
print("\n✅ ¡Lote completado!")