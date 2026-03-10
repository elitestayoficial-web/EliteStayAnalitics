# locales/translations.py
TRANSLATIONS = {
    'en': {
        'app_name': 'ELITE STAY ANALYTICS',
        'search': 'Search',
        'rankings': 'Rankings',
        'pricing': 'Pricing',
        'about': 'About',
        'hotels_monitored': 'Hotels monitored',
        'reviews_month': 'Reviews/month',
        'alerts_week': 'Alerts this week',
        'best_hotels': '🏆 Top 10 Best Hotels',
        'worst_hotels': '⚠️ Top 10 Hotels with most incidents',
        'dark_mode': '🌙 Dark',
        'light_mode': '☀️ Light'
    },
    'es': {
        'app_name': 'ELITE STAY ANALYTICS',
        'search': 'Buscar',
        'rankings': 'Rankings',
        'pricing': 'Precios',
        'about': 'Nosotros',
        'hotels_monitored': 'Hoteles monitoreados',
        'reviews_month': 'Reseñas/mes',
        'alerts_week': 'Alertas/semana',
        'best_hotels': '🏆 Top 10 Mejores Hoteles',
        'worst_hotels': '⚠️ Top 10 Hoteles con más incidentes',
        'dark_mode': '🌙 Dark',
        'light_mode': '☀️ Light'
    }
}

def get_text(lang, key):
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)