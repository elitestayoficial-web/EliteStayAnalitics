# ver_hoteles_actuales.py
import sqlite3

conn = sqlite3.connect('data/elitestayanalitycs.db')
cursor = conn.cursor()
cursor.execute('SELECT id, name, city, country FROM hotels ORDER BY id')
hoteles = cursor.fetchall()
conn.close()

print("="*60)
print("🏨 HOTELES ACTUALES")
print("="*60)
for h in hoteles:
    print(f"ID {h[0]:3}: {h[1]} - {h[2]}, {h[3]}")
print(f"\n📊 Total: {len(hoteles)} hoteles")