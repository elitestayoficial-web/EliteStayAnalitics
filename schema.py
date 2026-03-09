# backend/database/schema.py
import sqlite3
import os

DB_PATH = os.getenv('DB_PATH', 'data/elitestayanalitycs.db')

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabla de cadenas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            headquarters TEXT,
            sustainability_rating REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de regiones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS regions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE
        )
    ''')
    
    # Insertar regiones
    regions = [('north_america', 'NA'), ('europe', 'EU'), ('asia', 'AS'), ('south_america', 'SA')]
    for name, code in regions:
        cursor.execute('INSERT OR IGNORE INTO regions (name, code) VALUES (?, ?)', (name, code))
    
    # Tabla de países
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS countries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            name TEXT,
            language_primary TEXT,
            region_id INTEGER REFERENCES regions(id)
        )
    ''')
    
    # Tabla de hoteles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hotels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chain_id INTEGER REFERENCES chains(id),
            region_id INTEGER REFERENCES regions(id),
            country_code TEXT REFERENCES countries(code),
            name TEXT NOT NULL,
            name_local TEXT,
            brand TEXT,
            country TEXT,
            city TEXT,
            email TEXT,
            manager_name TEXT,
            overall_score REAL DEFAULT 100,
            language_primary TEXT,
            last_scraped TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de quejas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hotel_id INTEGER REFERENCES hotels(id),
            source TEXT,
            complaint_text TEXT,
            complaint_text_original TEXT,
            language_detected TEXT,
            complaint_date DATE,
            rating INTEGER,
            category_primary TEXT,
            severity TEXT,
            sentiment_score REAL,
            summary_en TEXT,
            business_relevant INTEGER DEFAULT 0,
            department TEXT,
            is_grave INTEGER DEFAULT 0,
            duplicate_group TEXT,
            is_duplicate INTEGER DEFAULT 0,
            processed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de grupos duplicados
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS duplicate_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_hash TEXT UNIQUE,
            complaint_ids TEXT,
            count INTEGER,
            first_seen DATE,
            last_seen DATE
        )
    ''')
    
    # Tabla de alertas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hotel_id INTEGER REFERENCES hotels(id),
            alert_level TEXT,
            alert_color TEXT,
            trigger_reason TEXT,
            complaint_count INTEGER,
            week_date DATE,
            email_sent INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # TABLA DE RANKINGS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rankings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hotel_id INTEGER REFERENCES hotels(id),
            rank INTEGER,
            score REAL,
            week_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Base de datos creada correctamente con todas las tablas")

if __name__ == '__main__':
    init_database()