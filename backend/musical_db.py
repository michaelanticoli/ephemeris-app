import psycopg2
import json
from typing import Dict, List, Any
import os

class MusicalDatabase:
    def __init__(self):
        # Replace [YOUR-PASSWORD] with your actual Supabase password
        self.connection_string = "postgresql://postgres:[YOUR-PASSWORD]@db.pqxnvninbjjzddppaebf.supabase.co:5432/postgres"
    
    def get_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(self.connection_string)
        except Exception as e:
            print(f"Database connection error: {e}")
            raise
    
    def test_connection(self):
        """Test if database connection works"""
        try:
            conn = self.get_connection()
            conn.close()
            return True
        except:
            return False
    
    def get_planetary_music(self, planets: List[Dict]) -> List[Dict]:
        """Get musical data for planets"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            musical_data = []
            for planet in planets:
                cursor.execute("""
                    SELECT planet, musical_key, frequency, instrument, musical_theme 
                    FROM planetary_music 
                    WHERE planet = %s
                """, (planet['name'],))
                
                result = cursor.fetchone()
                if result:
                    musical_data.append({
                        'planet': result[0],
                        'musical_key': result[1],
                        'frequency': f"{result[2]}Hz" if result[2] else None,
                        'instrument': result[3],
                        'musical_theme': result[4]
                    })
            
            conn.close()
            return musical_data
            
        except Exception as e:
            print(f"Error getting planetary music: {e}")
            return []
    
    def get_aspect_music(self, aspects: List[Dict]) -> List[Dict]:
        """Get musical data for aspects"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            musical_data = []
            for aspect in aspects:
                cursor.execute("""
                    SELECT aspect_name, musical_interval, harmony_type, tension_level 
                    FROM aspect_music 
                    WHERE aspect_name = %s
                """, (aspect['aspect_name'],))
                
                result = cursor.fetchone()
                if result:
                    musical_data.append({
                        'aspect_name': result[0],
                        'musical_interval': result[1],
                        'harmony_type': result[2],
                        'tension_level': result[3]
                    })
            
            conn.close()
            return musical_data
            
        except Exception as e:
            print(f"Error getting aspect music: {e}")
            return []
    
    def generate_composition_suggestions(self, chart_data: Dict) -> Dict:
        """Generate composition based on chart"""
        try:
            if not chart_data.get('planets'):
                return self._fallback_composition()
            
            dominant_planet = chart_data['planets'][0]  # Usually Sun
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get the musical key for the dominant planet
            cursor.execute("""
                SELECT musical_key, instrument 
                FROM planetary_music 
                WHERE planet = %s
            """, (dominant_planet['name'],))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'dominant_key': result[0],
                    'mode': 'Ionian',
                    'base_tempo': 85,
                    'emotional_tone': 'contemplative',
                    'instruments': [result[1], 'piano', 'strings', 'cosmic bells'],
                    'time_signature': '4/4',
                    'key_progression': [result[0], 'Am', result[0]],
                    'tempo_progression': [80, 100, 85]
                }
            
            return self._fallback_composition()
            
        except Exception as e:
            print(f"Error generating composition: {e}")
            return self._fallback_composition()
    
    def _fallback_composition(self):
        """Fallback composition data"""
        return {
            'dominant_key': 'C',
            'mode': 'Ionian',
            'base_tempo': 85,
            'emotional_tone': 'contemplative',
            'instruments': ['piano', 'strings', 'cosmic bells'],
            'time_signature': '4/4',
            'key_progression': ['C', 'Am', 'C'],
            'tempo_progression': [80, 100, 85]
        }
    
    def get_enhanced_musical_data(self, planets: List[Dict], aspects: List[Dict]) -> Dict:
        """Get all musical data for the chart"""
        try:
            planetary_music = self.get_planetary_music(planets)
            aspect_music = self.get_aspect_music(aspects)
            composition = self.generate_composition_suggestions({'planets': planets})
            
            return {
                'planetary_music': planetary_music,
                'aspect_music': aspect_music,
                'composition_suggestions': composition,
                'harmonic_analysis': {
                    'complexity': 0.7,
                    'primary_intervals': ['Perfect Fifth', 'Major Third'],
                    'tension_curve': [0.3, 0.4, 0.6, 0.8, 1.0, 0.9, 0.7, 0.5, 0.3, 0.2]
                }
            }
            
        except Exception as e:
            print(f"Error getting enhanced musical data: {e}")
            return {
                'planetary_music': [],
                'aspect_music': [],
                'composition_suggestions': self._fallback_composition(),
                'harmonic_analysis': {
                    'complexity': 0.5,
                    'primary_intervals': ['Perfect Fifth'],
                    'tension_curve': [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
                }
            }
