# backend/processors/deduplicator.py
import hashlib
import sqlite3
from collections import defaultdict
import textdistance

class Deduplicator:
    def __init__(self, db_path='data/elitestayanalitycs.db', threshold=0.85):
        self.db_path = db_path
        self.threshold = threshold
    
    def normalize(self, text):
        if not text:
            return ""
        return ' '.join(text.lower().split())
    
    def create_hash(self, text):
        return hashlib.sha256(self.normalize(text).encode()).hexdigest()
    
    def find_exact_duplicates(self, complaints):
        hash_map = defaultdict(list)
        for c in complaints:
            text = c.get('complaint_text', '')
            if text:
                hash_map[self.create_hash(text)].append(c)
        
        groups = []
        for h, group in hash_map.items():
            if len(group) > 1:
                groups.append({
                    'hash': h,
                    'complaints': group,
                    'count': len(group),
                    'type': 'exact'
                })
        return groups
    
    def find_similar_duplicates(self, complaints):
        if len(complaints) < 2:
            return []
        
        groups = []
        processed = set()
        
        for i in range(len(complaints)):
            if i in processed:
                continue
            
            group = [complaints[i]]
            processed.add(i)
            
            for j in range(i + 1, len(complaints)):
                if j in processed:
                    continue
                
                text1 = complaints[i].get('complaint_text', '')
                text2 = complaints[j].get('complaint_text', '')
                
                if text1 and text2:
                    similarity = textdistance.jaccard.normalized_similarity(
                        self.normalize(text1), 
                        self.normalize(text2)
                    )
                    
                    if similarity > self.threshold:
                        group.append(complaints[j])
                        processed.add(j)
            
            if len(group) > 1:
                groups.append({
                    'hash': hashlib.md5(f"group_{i}".encode()).hexdigest(),
                    'complaints': group,
                    'count': len(group),
                    'type': 'similar'
                })
        
        return groups
    
    def deduplicate(self, hotel_id=None, days=30):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if hotel_id:
            cursor.execute('''
                SELECT * FROM complaints 
                WHERE hotel_id = ? AND complaint_date >= date('now', ?)
            ''', (hotel_id, f'-{days} days'))
        else:
            cursor.execute('''
                SELECT * FROM complaints 
                WHERE complaint_date >= date('now', ?)
            ''', (f'-{days} days'))
        
        complaints = cursor.fetchall()
        
        stats = {
            'total': len(complaints),
            'exact': 0,
            'similar': 0,
            'unique': 0
        }
        
        # Exactos
        exact_groups = self.find_exact_duplicates(complaints)
        for group in exact_groups:
            ids = [c['id'] for c in group['complaints']]
            self._save_group(conn, group['hash'], ids)
            stats['exact'] += len(ids) - 1
            stats['unique'] += 1
        
        # Similares
        similar_groups = self.find_similar_duplicates(complaints)
        for group in similar_groups:
            ids = [c['id'] for c in group['complaints']]
            self._save_group(conn, group['hash'], ids)
            stats['similar'] += len(ids) - 1
            stats['unique'] += 1
        
        conn.close()
        print(f"✅ Deduplicación: {stats}")
        return stats
    
    def _save_group(self, conn, group_hash, complaint_ids):
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO duplicate_groups 
            (group_hash, complaint_ids, count, first_seen, last_seen)
            VALUES (?, ?, ?, date('now'), date('now'))
        ''', (group_hash, ','.join(map(str, complaint_ids)), len(complaint_ids)))
        
        for i, cid in enumerate(complaint_ids):
            cursor.execute('''
                UPDATE complaints 
                SET duplicate_group = ?, is_duplicate = ?
                WHERE id = ?
            ''', (group_hash, 1 if i > 0 else 0, cid))
        conn.commit()