# backend/processors/language_engine.py
from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator
import time

DetectorFactory.seed = 0

class LanguageEngine:
    def __init__(self):
        self.supported = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ja', 'ko', 'zh-cn']
        self.translator_map = {
            'ja': 'ja', 'ko': 'ko', 'zh-cn': 'zh-CN',
            'es': 'es', 'pt': 'pt', 'fr': 'fr',
            'de': 'de', 'it': 'it'
        }
    
    def detect(self, text):
        if not text or len(text.strip()) < 10:
            return 'unknown'
        try:
            lang = detect(text)
            return lang if lang in self.supported else 'unknown'
        except:
            return 'unknown'
    
    def translate(self, text, source_lang):
        if not text:
            return text
        try:
            if len(text) > 5000:
                text = text[:5000]
            source = self.translator_map.get(source_lang, source_lang)
            translator = GoogleTranslator(source=source, target='en')
            return translator.translate(text)
        except:
            return text
    
    def process(self, text, complaint_id=None):
        if not text:
            return {'original': '', 'language': 'unknown', 'translated': '', 'was_translated': False}
        
        lang = self.detect(text)
        if complaint_id:
            print(f"📝 #{complaint_id}: Idioma {lang}")
        
        if lang != 'en' and lang != 'unknown':
            translated = self.translate(text, lang)
            was_translated = True
        else:
            translated = text
            was_translated = False
        
        return {
            'original': text,
            'language': lang,
            'translated': translated,
            'was_translated': was_translated
        }