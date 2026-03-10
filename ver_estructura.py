# ver_estructura.py
import sqlite3

conn = sqlite3.connect('data/elitestayanalitycs.db')
cursor = conn.cursor()

# Ver columnas de la tabla hotels
cursor.execute("PRAGMA table_info(hotels)")
columnas = cursor.fetchall()

print("📋 COLUMNAS DE LA TABLA hotels:")
for col in columnas:
    print(f"  {col[1]} - {col[2]}")

conn.close()
