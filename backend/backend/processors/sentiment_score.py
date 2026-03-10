# backend/processors/sentiment_score.py
class SentimentAnalyzer:
    def __init__(self):
        self.positive = ['excellent', 'amazing', 'perfect', 'great', 'fantastic', 'love', 'best']
        self.negative = ['terrible', 'awful', 'horrible', 'worst', 'bad', 'poor', 'disappointing']
        self.critical = ['stole', 'robbery', 'unsafe', 'dangerous', 'emergency']
    
    def analyze(self, text, language='en'):
        if not text:
            return 5.0
        
        text_lower = text.lower()
        words = text_lower.split()
        
        pos_count = sum(1 for w in words if w in self.positive)
        neg_count = sum(1 for w in words if w in self.negative)
        
        if pos_count + neg_count == 0:
            return 5.0
        
        # Penalizar palabras críticas
        critical_penalty = 3 if any(c in text_lower for c in self.critical) else 0
        
        score = (pos_count / (pos_count + neg_count)) * 10
        score = max(0, min(10, score - critical_penalty))
        
        return round(score, 2)
    
    def get_severity(self, score):
        if score < 3:
            return 'critical'
        elif score < 5:
            return 'moderate'
        else:
            return 'minor'