from flask import Blueprint, request, jsonify
import os
import requests
import random
import time
from utils.limiter import limiter

weather_bp = Blueprint('weather', __name__)

cache = {}
CACHE_TTL = 600 # 10 minutes

OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', 'placeholder_key')

@weather_bp.route('', methods=['GET'])
@limiter.limit("20 per minute")
def get_current_weather():
    city = request.args.get('city')
    if not city:
        return jsonify({"message": "City parameter is required"}), 400

    cache_key = f"weather_{city.lower()}"
    if cache_key in cache and time.time() - cache[cache_key]['timestamp'] < CACHE_TTL:
        return jsonify(cache[cache_key]['data']), 200

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code != 200:
            return jsonify({"message": data.get("message", "Error fetching weather")}), response.status_code
            
        # Simulate deterministic seasonal average rainfall (40-250) based on city
        rng = random.Random(city.lower().strip())
        estimated_rainfall = round(rng.uniform(50, 250), 2)

        result = {
            "temperature": data['main']['temp'],
            "humidity": data['main']['humidity'],
            "rainfall": estimated_rainfall,
            "description": data['weather'][0]['description']
        }
        cache[cache_key] = {'data': result, 'timestamp': time.time()}
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"message": "Failed to connect to weather service."}), 500

@weather_bp.route('/forecast', methods=['GET'])
@limiter.limit("20 per minute")
def get_weather_forecast():
    city = request.args.get('city')
    if not city:
        return jsonify({"message": "City parameter is required"}), 400

    cache_key = f"forecast_{city.lower()}"
    if cache_key in cache and time.time() - cache[cache_key]['timestamp'] < CACHE_TTL:
        return jsonify(cache[cache_key]['data']), 200

    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code != 200:
            return jsonify({"message": data.get("message", "Error fetching forecast")}), response.status_code
            
        forecast_list = []
        rain_days = 0
        # Group by day, simplified logic. OpenWeather returns 3-hour increments
        for item in data.get('list', [])[::8]: # get approx one per day
            desc = item['weather'][0]['description']
            if 'rain' in desc.lower():
                rain_days += 1
            forecast_list.append({
                "date": item['dt_txt'].split(" ")[0],
                "temperature": item['main']['temp'],
                "humidity": item['main']['humidity'],
                "description": desc
            })

        impact = "Normal"
        if rain_days >= 2:
            impact = "High Rainfall Risk - Ensure proper field drainage"

        result = {"city": city, "forecast": forecast_list, "crop_impact": impact}
        cache[cache_key] = {'data': result, 'timestamp': time.time()}
        
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"message": "Failed to connect to forecast service."}), 500
