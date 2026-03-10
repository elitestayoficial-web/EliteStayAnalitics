# backend/reports/pdf_generator.py
from fpdf import FPDF
import sqlite3
from datetime import datetime

class PDFGenerator:
    def __init__(self, db_path='data/elitestayanalitycs.db'):
        self.db_path = db_path
    
    def generate_hotel_report(self, hotel_id, days=30):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Datos del hotel
        cursor.execute('''
            SELECT h.*, c.name as chain_name 
            FROM hotels h
            LEFT JOIN chains c ON h.chain_id = c.id
            WHERE h.id = ?
        ''', (hotel_id,))
        hotel = cursor.fetchone()
        
        if not hotel:
            conn.close()
            return None
        
        # Quejas recientes
        cursor.execute('''
            SELECT category_primary, severity, COUNT(*) as count
            FROM complaints
            WHERE hotel_id = ? AND complaint_date >= date('now', ?)
            AND (is_duplicate = 0 OR is_duplicate IS NULL)
            GROUP BY category_primary, severity
            ORDER BY count DESC
        ''', (hotel_id, f'-{days} days'))
        
        complaints = cursor.fetchall()
        conn.close()
        
        # Crear PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Título
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, f'Hotel Audit Report', 0, 1, 'C')
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f'{hotel[3]} - {hotel[6]}', 0, 1, 'C')
        pdf.ln(10)
        
        # Fecha
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 10, f'Generado: {datetime.now().strftime("%Y-%m-%d")}', 0, 1, 'R')
        pdf.ln(10)
        
        # Resumen
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Resumen de Incidencias', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        if complaints:
            for cat, sev, count in complaints[:5]:
                pdf.cell(60, 8, cat or 'other', 1)
                pdf.cell(40, 8, sev or 'unknown', 1)
                pdf.cell(30, 8, str(count), 1, 1)
        else:
            pdf.cell(0, 8, 'No hay incidencias en el período', 1, 1)
        
        # Guardar
        filename = f'reports/hotel_{hotel_id}_{datetime.now().strftime("%Y%m%d")}.pdf'
        pdf.output(filename)
        return filename