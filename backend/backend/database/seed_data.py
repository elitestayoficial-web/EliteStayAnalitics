# backend/database/seed_data.py
import sqlite3
from datetime import datetime

def seed_data():
    conn = sqlite3.connect('data/elitestayanalitycs.db')
    cursor = conn.cursor()
    
    # Limpiar tablas
    cursor.execute('DELETE FROM rankings')
    cursor.execute('DELETE FROM hotels')
    
    # Insertar hoteles de ejemplo
    hoteles = [
        (1, 'Marriott Marquis', 'New York', 'marriott@test.com', 'EE.UU.', 98),
        (2, 'Hilton Downtown', 'Chicago', 'hilton@test.com', 'EE.UU.', 95),
        (3, 'Hyatt Regency', 'San Francisco', 'hyatt@test.com', 'EE.UU.', 92),
        (4, 'Four Seasons', 'Los Angeles', 'fourseasons@test.com', 'EE.UU.', 96),
        (5, 'Ritz Carlton', 'Miami', 'ritz@test.com', 'EE.UU.', 97),
        (6, 'Hotel Problemas', 'Las Vegas', 'problemas@test.com', 'EE.UU.', 45),
        (7, 'Hotel Incidentes', 'Boston', 'incidentes@test.com', 'EE.UU.', 38),
        (8, 'Hotel Quejas', 'Seattle', 'quejas@test.com', 'EE.UU.', 42),
        (9, 'Hotel Ritz Madrid', 'Madrid', 'ritz@spain.com', 'España', 99),
        (10, 'Marriott Paris', 'Paris', 'marriott@france.com', 'Francia', 94),
        (11, 'Hilton London', 'London', 'hilton@uk.com', 'Reino Unido', 93),
        (12, 'Grand Hyatt Tokyo', 'Tokyo', 'hyatt@japan.com', 'Japón', 91),
    ]
    
    for hotel in hoteles:
        cursor.execute('''
            INSERT OR REPLACE INTO hotels (id, name, city, email, country, overall_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', hotel)
    
    # Insertar rankings
    week = datetime.now().strftime('%Y-%m-%d')
    
    # Mejores hoteles
    mejores = [1, 4, 5, 2, 3, 9, 10, 11, 12]  # IDs
    for i, hotel_id in enumerate(mejores, 1):
        score = 100 - i  # Puntajes decrecientes
        cursor.execute('''
            INSERT OR REPLACE INTO rankings (hotel_id, rank, score, week_date)
            VALUES (?, ?, ?, ?)
        ''', (hotel_id, i, score, week))
    
    # Peores hoteles
    peores = [6, 7, 8]  # IDs
    for i, hotel_id in enumerate(peores, 1):
        score = 50 - i*5
        cursor.execute('''
            INSERT OR REPLACE INTO rankings (hotel_id, rank, score, week_date)
            VALUES (?, ?, ?, ?)
        ''', (hotel_id, i + 10, score, week))
    
    conn.commit()
    
    # Verificar
    cursor.execute('SELECT COUNT(*) FROM hotels')
    hoteles_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM rankings')
    rankings_count = cursor.fetchone()[0]
    
    conn.close()
    print(f"✅ Datos insertados: {hoteles_count} hoteles, {rankings_count} rankings")

if __name__ == '__main__':
    seed_data()