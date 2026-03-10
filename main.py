#!/usr/bin/env python3
# main.py - Versión MÍNIMA para prueba

import os
from flask import Flask, jsonify

# Crear la aplicación Flask
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "ok",
        "message": "App mínima funcionando en Render"
    })

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})

# Para Gunicorn (buscará 'app')
application = app  # Alias por compatibilidad

if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port)


