# test_google_api.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GOOGLE_PLACES_API_KEY')
print(f"🔑 API Key: {api_key[:15]}...")

url = "https://places.googleapis.com/v1/places:searchText"
headers = {
    'Content-Type': 'application/json',
    'X-Goog-Api-Key': api_key,
    'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress'
}
payload = {
    "textQuery": "Four Seasons Los Angeles",
    "maxResultCount": 1
}

print(f"\n📡 Probando conexión a Google Places API...")
response = requests.post(url, headers=headers, json=payload)
print(f"   Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    if 'places' in data and data['places']:
        place = data['places'][0]
        print(f"\n✅ ¡CONEXIÓN EXITOSA!")
        print(f"   Hotel encontrado: {place['displayName']['text']}")
        print(f"   Place ID: {place['id']}")
        print(f"   Dirección: {place.get('formattedAddress', 'N/A')}")
    else:
        print("❌ No se encontraron resultados")
else:
    print(f"\n❌ Error en la conexión:")
    print(response.text)