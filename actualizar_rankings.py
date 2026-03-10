# actualizar_rankings.py
import sqlite3
from datetime import datetime

print("="*60)
print("🏆 ACTUALIZANDO RANKINGS GLOBALES")
print("="*60)

conn = sqlite3.connect('data/elitestayanalitycs.db')
cursor = conn.cursor()

# Ver cuántos hoteles hay
cursor.execute('SELECT COUNT(*) FROM hotels')
total_hoteles = cursor.fetchone()[0]
print(f"📊 Total hoteles en BD: {total_hoteles}")

# Limpiar rankings anteriores
cursor.execute('DELETE FROM rankings')
print("🧹 Rankings anteriores eliminados")

# Obtener hoteles ordenados por puntaje
cursor.execute('''
    SELECT id, name, city, overall_score 
    FROM hotels 
    ORDER BY overall_score DESC
''')
hoteles = cursor.fetchall()

# Insertar nuevos rankings (Top 50)
print("\n📥 Generando nuevos rankings...")
for i, (hotel_id, nombre, ciudad, score) in enumerate(hoteles[:50], 1):
    cursor.execute('''
        INSERT INTO rankings (hotel_id, rank, score, week_date)
        VALUES (?, ?, ?, date('now'))
    ''', (hotel_id, i, score))
    print(f"  {i:2d}. {nombre} - {ciudad} ({score})")

conn.commit()
conn.close()

print(f"\n✅ Rankings actualizados con {min(50, len(hoteles))} hoteles")
print(f"📊 Total rankings generados: {len(hoteles[:50])}")