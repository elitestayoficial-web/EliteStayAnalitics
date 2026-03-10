# backend/processors/ai_classifier.py
import os
from .language_engine import LanguageEngine
from .sentiment_score import SentimentAnalyzer

class AIClassifier:
    def __init__(self):
        self.lang_engine = LanguageEngine()
        self.sentiment = SentimentAnalyzer()
    
    def classify(self, text, complaint_id=None):
        if not text:
            return {'category': 'other', 'severity': 'minor', 'sentiment': 5.0}
        
        processed = self.lang_engine.process(text, complaint_id)
        sentiment_score = self.sentiment.analyze(processed['translated'])
        severity = self.sentiment.get_severity(sentiment_score)
        
        # Reglas simples para categoría
        text_lower = processed['translated'].lower()
        
        if any(w in text_lower for w in ['wifi', 'internet', 'connection']):
            category = 'wifi'
        elif any(w in text_lower for w in ['bill', 'charge', 'payment', 'money']):
            category = 'billing'
        elif any(w in text_lower for w in ['clean', 'dirty', 'stain', 'smell']):
            category = 'cleanliness'
        elif any(w in text_lower for w in ['stole', 'security', 'safe', 'unsafe']):
            category = 'security'
        elif any(w in text_lower for w in ['staff', 'rude', 'friendly', 'service']):
            category = 'staff'
        else:
            category = 'other'
        
        return {
            'category': category,
            'severity': severity,
            'sentiment': sentiment_score,
            'business_relevant': category in ['wifi', 'billing'],
            'department': self._map_department(category),
            'summary': processed['translated'][:100],
            'original_language': processed['language'],
            'was_translated': processed['was_translated']
        }
    
    def _map_department(self, category):
        mapping = {
            'wifi': 'maintenance',
            'billing': 'front_desk',
            'cleanliness': 'housekeeping',
            'security': 'security',
            'staff': 'management'
        }
        return mapping.get(category, 'other')