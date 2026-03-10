# google_reviews_collector.py
import os
import sqlite3
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class GoogleReviewsCollector:
    """
    Recolecta reseñas de Google Places API (New)
    """
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_PLACES_API_KEY')
        if not self.api_key:
            raise ValueError("❌ GOOGLE_PLACES_API_KEY no encontrada en .env")
        
        self.base_url = "https://places.googleapis.com/v1/places"
        self.db_path = 'data/elitestayanalitycs.db'
        self.conectar_bd()
    
    def conectar_bd(self):
        """Conecta a la base de datos"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Asegurar que existe la tabla para Place IDs
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS google_place_ids (
                hotel_id INTEGER PRIMARY KEY,
                place_id TEXT,
                place_name TEXT,
                formatted_address TEXT,
                last_updated TIMESTAMP,
                UNIQUE(hotel_id)
            )
        ''')
        self.conn.commit()
    
    def buscar_place_id(self, nombre_hotel, ciudad, pais=""):
        """
        Busca el Place ID de un hotel en Google Maps
        """
        query = f"{nombre_hotel} {ciudad} {pais}".strip()
        url = "https://places.googleapis.com/v1/places:searchText"
        
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.api_key,
            'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress'
        }
        
        payload = {
            "textQuery": query,
            "maxResultCount": 3,
            "locationBias": {
                "rectangle": {
                    "low": {"latitude": -90, "longitude": -180},
                    "high": {"latitude": 90, "longitude": 180}
                }
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()
            
            if 'places' in data and data['places']:
                place = data['places'][0]  # Tomar el primer resultado
                return {
                    'place_id': place['id'],
                    'name': place['displayName']['text'],
                    'address': place.get('formattedAddress', '')
                }
            else:
                print(f"  ⚠️ No se encontró Place ID para: {query}")
                return None
                
        except Exception as e:
            print(f"  ❌ Error buscando Place ID: {e}")
            return None
    
    def obtener_resenas(self, place_id, hotel_id, max_reviews=20):
        """
        Obtiene reseñas detalladas de un lugar usando su Place ID
        """
        url = f"{self.base_url}/{place_id}"
        
        headers = {
            'X-Goog-Api-Key': self.api_key,
            'X-Goog-FieldMask': 'id,displayName,rating,userRatingCount,reviews,regularOpeningHours,websiteUri,internationalPhoneNumber,formattedAddress'
        }
        
        try:
            response = requests.get(url, headers=headers)
            data = response.json()
            
            if 'error' in data:
                print(f"  ❌ Error API: {data['error'].get('message', 'Desconocido')}")
                return []
            
            reviews = data.get('reviews', [])
            print(f"  📝 {len(reviews)} reseñas disponibles")
            
            # Guardar información general del hotel
            self.guardar_info_hotel(hotel_id, data)
            
            # Guardar reseñas
            for review in reviews[:max_reviews]:
                self.guardar_resena(hotel_id, review)
            
            return reviews
            
        except Exception as e:
            print(f"  ❌ Error obteniendo reseñas: {e}")
            return []
    
    def guardar_info_hotel(self, hotel_id, place_data):
        """
        Guarda/actualiza información del hotel desde Google
        """
        self.cursor.execute('''
            INSERT OR REPLACE INTO google_place_ids 
            (hotel_id, place_id, place_name, formatted_address, last_updated)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            hotel_id,
            place_data.get('id', ''),
            place_data.get('displayName', {}).get('text', ''),
            place_data.get('formattedAddress', ''),
            datetime.now().isoformat()
        ))
        self.conn.commit()
    
    def guardar_resena(self, hotel_id, review):
        """
        Guarda una reseña en la base de datos
        """
        try:
            # Verificar si ya existe
            review_text = review.get('text', {}).get('text', '')
            if not review_text:
                return
            
            # Crear un hash simple para detectar duplicados
            review_hash = str(hash(review_text[:200]))
            
            self.cursor.execute('''
                SELECT id FROM complaints 
                WHERE hotel_id = ? AND source = ? AND complaint_text = ?
            ''', (hotel_id, 'google_reviews', review_text[:200]))
            
            if not self.cursor.fetchone():
                # Determinar severidad basada en rating
                rating = review.get('rating', 3)
                if rating <= 2:
                    severidad = 'critical'
                elif rating <= 3:
                    severidad = 'moderate'
                else:
                    severidad = 'minor'
                
                # Extraer fecha aproximada (Google no siempre da fecha exacta)
                publish_time = review.get('publishTime', '')
                review_date = publish_time[:10] if publish_time else datetime.now().strftime('%Y-%m-%d')
                
                # Guardar nueva reseña
                self.cursor.execute('''
                    INSERT INTO complaints 
                    (hotel_id, source, complaint_text, complaint_text_original,
                     language_detected, complaint_date, rating, severity, processed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
                ''', (
                    hotel_id,
                    'google_reviews',
                    review_text,
                    review_text,
                    review.get('languageCode', 'en'),
                    review_date,
                    rating,
                    severidad
                ))
                self.conn.commit()
                print(f"      ✅ Reseña guardada (rating: {rating})")
            else:
                print(f"      ⏩ Reseña ya existe")
                
        except Exception as e:
            print(f"      ❌ Error guardando reseña: {e}")
    
    def procesar_hotel(self, hotel_id, nombre, ciudad):
        """
        Procesa un hotel completo: busca Place ID y obtiene reseñas
        """
        print(f"\n🏨 Procesando: {nombre} - {ciudad}")
        
        # Buscar Place ID
        place_info = self.buscar_place_id(nombre, ciudad)
        
        if place_info:
            print(f"  ✅ Place ID encontrado: {place_info['place_id']}")
            print(f"  📍 Nombre Google: {place_info['name']}")
            
            # Obtener reseñas
            total = self.obtener_resenas(place_info['place_id'], hotel_id)
            print(f"  📊 Total reseñas obtenidas: {len(total)}")
            return len(total)
        else:
            print(f"  ❌ No se pudo obtener Place ID")
            return 0
    
    def procesar_todos(self):
        """
        Procesa todos los hoteles de la base de datos
        """
        self.cursor.execute('SELECT id, name, city FROM hotels')
        hoteles = self.cursor.fetchall()
        
        print(f"\n{'='*60}")
        print(f"🔥 INICIANDO RECOPILACIÓN DE RESEÑAS GOOGLE")
        print(f"{'='*60}")
        print(f"📊 Hoteles a procesar: {len(hoteles)}")
        
        total_general = 0
        for hotel_id, nombre, ciudad in hoteles:
            total = self.procesar_hotel(hotel_id, nombre, ciudad)
            total_general += total
            
            # Pausa para no saturar la API (límite: 600 requests/minuto)
            time.sleep(1)
        
        print(f"\n{'='*60}")
        print(f"✅ RECOPILACIÓN COMPLETADA")
        print(f"📊 Total reseñas obtenidas: {total_general}")
        self.conn.close()
        return total_general
    
    def procesar_hotel_especifico(self, hotel_id):
        """
        Procesa un hotel específico por su ID
        """
        self.cursor.execute('SELECT id, name, city FROM hotels WHERE id = ?', (hotel_id,))
        hotel = self.cursor.fetchone()
        
        if hotel:
            return self.procesar_hotel(hotel[0], hotel[1], hotel[2])
        else:
            print(f"❌ No se encontró hotel con ID {hotel_id}")
            return 0


if __name__ == "__main__":
    import sys
    
    print("="*60)
    print("🚀 RECOPILADOR DE RESEÑAS DE GOOGLE PLACES")
    print("="*60)
    
    collector = GoogleReviewsCollector()
    
    print("\nOpciones:")
    print("  1. Procesar TODOS los hoteles")
    print("  2. Procesar un hotel específico")
    print("  3. Salir")
    
    opcion = input("\n📌 Selecciona una opción (1-3): ")
    
    if opcion == '1':
        collector.procesar_todos()
    elif opcion == '2':
        hotel_id = input("🔍 ID del hotel a procesar: ")
        try:
            collector.procesar_hotel_especifico(int(hotel_id))
        except:
            print("❌ ID inválido")
    else:
        print("👋 Hasta luego!")
