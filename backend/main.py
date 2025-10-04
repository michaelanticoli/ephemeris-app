from flask import Flask, request, jsonify
from flask_cors import CORS
import swisseph as swe
from datetime import datetime, timezone, timedelta
import math
from musical_db import MusicalDatabase

app = Flask(__name__)
CORS(app)

# Initialize musical database
musical_db = MusicalDatabase()

# Planet constants
PLANETS = [
    ('Sun', swe.SUN),
    ('Moon', swe.MOON),
    ('Mercury', swe.MERCURY),
    ('Venus', swe.VENUS),
    ('Mars', swe.MARS),
    ('Jupiter', swe.JUPITER),
    ('Saturn', swe.SATURN),
    ('Uranus', swe.URANUS),
    ('Neptune', swe.NEPTUNE),
    ('Pluto', swe.PLUTO)
]

SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

def julian_day(year, month, day, hour, minute, timezone_offset):
    """Calculate Julian Day Number"""
    # Convert to UTC
    utc_hour = hour - timezone_offset
    utc_time = utc_hour + minute / 60.0
    
    return swe.julday(year, month, day, utc_time, swe.GREG_CAL)

def longitude_to_sign_and_degree(longitude):
    """Convert longitude to zodiac sign and degree"""
    sign_index = int(longitude / 30)
    degree = longitude % 30
    return SIGNS[sign_index], degree

def calculate_house(longitude, houses):
    """Determine which house a planet is in"""
    for i in range(12):
        next_house = (i + 1) % 12
        if houses[next_house] < houses[i]:  # Handle wrap around 360°
            if longitude >= houses[i] or longitude < houses[next_house]:
                return i + 1
        else:
            if houses[i] <= longitude < houses[next_house]:
                return i + 1
    return 1  # Default to 1st house

def calculate_planets(birth_data):
    """Calculate planetary positions"""
    jd = julian_day(
        birth_data['year'], birth_data['month'], birth_data['day'],
        birth_data['hour'], birth_data['minute'], birth_data['timezone_offset']
    )
    
    planets = []
    for name, planet_id in PLANETS:
        result, ret = swe.calc_ut(jd, planet_id)
        longitude = result[0]
        speed = result[3]
        
        sign, degree = longitude_to_sign_and_degree(longitude)
        
        planets.append({
            'name': name,
            'longitude': longitude,
            'zodiac_sign': sign,
            'zodiac_degree': degree,
            'house': 1,  # Will be calculated with houses
            'retrograde': speed < 0
        })
    
    return planets

def calculate_houses(birth_data):
    """Calculate house cusps using Placidus system"""
    jd = julian_day(
        birth_data['year'], birth_data['month'], birth_data['day'],
        birth_data['hour'], birth_data['minute'], birth_data['timezone_offset']
    )
    
    try:
        houses, ascmc = swe.houses(jd, birth_data['latitude'], birth_data['longitude'], b'P')
        return list(houses)
    except:
        # Fallback: equal houses
        ascendant = 0  # This should be calculated properly
        return [(ascendant + i * 30) % 360 for i in range(12)]

def calculate_aspects(planets):
    """Calculate aspects between planets"""
    ASPECT_DEFINITIONS = [
        {'name': 'Conjunction', 'angle': 0, 'orb': 8},
        {'name': 'Sextile', 'angle': 60, 'orb': 6},
        {'name': 'Square', 'angle': 90, 'orb': 8},
        {'name': 'Trine', 'angle': 120, 'orb': 8},
        {'name': 'Opposition', 'angle': 180, 'orb': 8},
        {'name': 'Quincunx', 'angle': 150, 'orb': 3}
    ]
    
    aspects = []
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            planet1 = planets[i]
            planet2 = planets[j]
            
            # Calculate angle difference
            angle_diff = abs(planet1['longitude'] - planet2['longitude'])
            if angle_diff > 180:
                angle_diff = 360 - angle_diff
            
            # Check for aspects
            for aspect_def in ASPECT_DEFINITIONS:
                orb = abs(angle_diff - aspect_def['angle'])
                if orb <= aspect_def['orb']:
                    aspects.append({
                        'planet1': planet1['name'],
                        'planet2': planet2['name'],
                        'aspect_name': aspect_def['name'],
                        'orb': orb,
                        'exact_angle': angle_diff
                    })
                    break
    
    return aspects

@app.route('/natal-chart', methods=['POST'])
def calculate_natal_chart():
    """Calculate natal chart with optional musical analysis"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['year', 'month', 'day', 'hour', 'minute', 'latitude', 'longitude', 'timezone_offset']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Calculate planets
        planets = calculate_planets(data)
        
        # Calculate houses
        houses = calculate_houses(data)
        
        # Assign houses to planets
        for planet in planets:
            planet['house'] = calculate_house(planet['longitude'], houses)
        
        # Base response
        response = {
            'planets': planets,
            'houses': houses,
            'calculation_time': datetime.now(timezone.utc).isoformat()
        }
        
        # Add musical analysis if requested
        if data.get('include_musical_analysis'):
            try:
                aspects = calculate_aspects(planets)
                musical_data = musical_db.get_enhanced_musical_data(planets, aspects)
                response['musical_data'] = musical_data
            except Exception as e:
                print(f"Musical analysis error: {e}")
                # Continue without musical data
                response['musical_data'] = None
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error calculating chart: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'services': {
            'swiss_ephemeris': 'available',
            'supabase': 'connected' if musical_db.test_connection() else 'disconnected'
        }
    })

if __name__ == '__main__':
    # Set Swiss Ephemeris path (optional)
    swe.set_ephe_path('/usr/share/swisseph')  # Adjust path as needed
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
