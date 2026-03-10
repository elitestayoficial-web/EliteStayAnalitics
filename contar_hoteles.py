# contar_hoteles.py
import sqlite3

conn = sqlite3.connect('data/elitestayanalitycs.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM hotels')
total = cursor.fetchone()[0]
conn.close()
print(f"📊 Total hoteles en base de datos: {total}")