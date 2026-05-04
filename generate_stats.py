#!/usr/bin/env python3
"""
Script para generar estadísticas de interacciones con el bot Hermes Tarot.
Extrae datos del sistema de auditoría y genera JSON para la página stats.html
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Directorio de auditoría (mismo que en waha-hermes-webhook.py)
AUDIT_DIR = Path("/Users/quimera/.hermes/whatsapp-audit")

def get_all_audit_data():
    """Cargar todos los datos de auditoría."""
    audit_files = list(AUDIT_DIR.glob("*.json"))
    all_data = {}
    
    for f in audit_files:
        try:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                chat_id = f.stem.replace('_', '@')  # Restaurar formato original
                all_data[chat_id] = data
        except Exception as e:
            print(f"⚠️ Error cargando {f}: {e}")
    
    return all_data

def extract_topic(text):
    """Extraer tema principal del mensaje (simplificado)."""
    text_lower = text.lower()
    
    topic_keywords = {
        'tarot': ['tarot', 'carta', 'tirada', 'predicción', 'destino', 'futuro'],
        'amor': ['amor', 'pareja', 'novio', 'novia', 'relación', 'corazón', 'sentimientos'],
        'trabajo': ['trabajo', 'empleo', 'jefe', 'colega', 'desempleado', 'profesión'],
        'dinero': ['dinero', 'economía', 'gastos', 'ahorro', 'inversión', 'deuda'],
        'salud': ['salud', 'enfermo', 'bienestar', 'dieta', 'ejercicio', 'cuerpo'],
        'familiar': ['familia', 'padre', 'madre', 'hermano', 'hijo', 'abuelo'],
        'astrología': ['signo', 'planeta', 'luna', 'sol', 'ascendente', 'solar', 'natal'],
        'numerología': ['número', 'vidas', 'camino', 'destino', 'numerología'],
        'esoterismo': ['místico', 'espiritual', 'energía', 'meditación', 'ritual'],
        'personalidad': ['nombre', 'nacimiento', 'cumpleaños', 'edad'],
        'saludo': ['hola', 'buenos días', 'buenas tardes', 'buenas noches']
    }
    
    for topic, keywords in topic_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return topic
    
    return 'otro'

def generate_statistics():
    """Generar estadísticas completas."""
    all_data = get_all_audit_data()
    
    if not all_data:
        print("⚠️ No hay datos de auditoría disponibles")
        return None
    
    # Estadísticas globales
    stats = {
        'generated_at': datetime.now().isoformat(),
        'total_chats': len(all_data),
        'total_interactions': 0,
        'total_input_words': 0,
        'total_output_words': 0,
        'topic_distribution': defaultdict(int),
        'interactions_by_day': defaultdict(int),
        'interactions_by_month': defaultdict(int),
        'interactions_by_year': defaultdict(int),
        'chats_data': []
    }
    
    # Procesar cada chat
    for chat_id, interactions in all_data.items():
        chat_stats = {
            'chat_id': chat_id,
            'total_interactions': len(interactions),
            'first_interaction': None,
            'last_interaction': None,
            'total_input_words': 0,
            'total_output_words': 0,
            'topics': defaultdict(int)
        }
        
        for interaction in interactions:
            # Contar palabras
            input_text = interaction['input']['text']
            output_text = interaction['output']
            
            chat_stats['total_input_words'] += len(input_text.split())
            output_word_count = output_text.get('word_count', 0) if isinstance(output_text, dict) else 0
            chat_stats['total_output_words'] += output_word_count
            
            # Extraer tema
            topic = extract_topic(input_text)
            chat_stats['topics'][topic] += 1
            stats['topic_distribution'][topic] += 1
            
            # Extraer fecha
            timestamp = interaction['timestamp']
            dt = datetime.fromisoformat(timestamp)
            
            day_key = dt.strftime('%Y-%m-%d')
            month_key = dt.strftime('%Y-%m')
            year_key = dt.strftime('%Y')
            
            stats['interactions_by_day'][day_key] += 1
            stats['interactions_by_month'][month_key] += 1
            stats['interactions_by_year'][year_key] += 1
            
            # Actualizar rangos temporales
            if chat_stats['first_interaction'] is None:
                chat_stats['first_interaction'] = timestamp
            chat_stats['last_interaction'] = timestamp
        
        stats['total_interactions'] += len(interactions)
        stats['total_input_words'] += chat_stats['total_input_words']
        stats['total_output_words'] += chat_stats['total_output_words']
        
        # Convertir defaultdict a dict para JSON
        chat_stats['topics'] = dict(chat_stats['topics'])
        stats['chats_data'].append(chat_stats)
    
    # Convertir defaultdict a dict para JSON
    stats['topic_distribution'] = dict(stats['topic_distribution'])
    stats['interactions_by_day'] = dict(sorted(stats['interactions_by_day'].items()))
    stats['interactions_by_month'] = dict(sorted(stats['interactions_by_month'].items()))
    stats['interactions_by_year'] = dict(sorted(stats['interactions_by_year'].items()))
    
    # Calcular promedios
    if stats['total_interactions'] > 0:
        stats['avg_input_length'] = round(stats['total_input_words'] / stats['total_interactions'], 2)
        stats['avg_output_length'] = round(stats['total_output_words'] / stats['total_interactions'], 2)
    else:
        stats['avg_input_length'] = 0
        stats['avg_output_length'] = 0
    
    return stats

def main():
    """Generar archivo JSON de estadísticas."""
    print("🔍 Generando estadísticas de interacciones...")
    
    stats = generate_statistics()
    
    if not stats:
        print("❌ No se pudieron generar estadísticas")
        return
    
    # Guardar como JSON
    output_file = Path("/Users/quimera/hermes-landing-page/stats_data.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Estadísticas generadas: {output_file}")
    print(f"📊 Resumen:")
    print(f"   - Total chats: {stats['total_chats']}")
    print(f"   - Total interacciones: {stats['total_interactions']}")
    print(f"   - Palabras de entrada: {stats['total_input_words']}")
    print(f"   - Palabras de salida: {stats['total_output_words']}")
    print(f"   - Temas más comunes: {list(stats['topic_distribution'].keys())[:5]}")

if __name__ == "__main__":
    main()
