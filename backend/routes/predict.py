import os
import joblib
import pandas as pd
from flask import Blueprint, request, jsonify
from utils.auth_utils import token_required
from utils.db import get_db
import requests
import datetime
import numpy as np
import time
from utils.limiter import limiter

predict_bp = Blueprint('predict', __name__)

models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
try:
    xgb_model = joblib.load(os.path.join(models_dir, 'xgb_model.joblib'))
    cat_model = joblib.load(os.path.join(models_dir, 'cat_model.joblib'))
    rf_model = joblib.load(os.path.join(models_dir, 'rf_model.joblib'))
    scaler = joblib.load(os.path.join(models_dir, 'scaler.joblib'))
    label_encoder = joblib.load(os.path.join(models_dir, 'label_encoder.joblib'))
except FileNotFoundError:
    print("Warning: Models not found. Training script may need to be run first.")
    xgb_model, cat_model, rf_model, scaler, label_encoder = None, None, None, None, None

CROP_GEO_DICT = {
    'Rice': {'season': 'Kharif (June - October)', 'regions': 'West Bengal, UP, Punjab, Andhra Pradesh'},
    'Maize': {'season': 'Kharif (June - October)', 'regions': 'Karnataka, MP, Bihar, Tamil Nadu'},
    'Chickpea': {'season': 'Rabi (October - March)', 'regions': 'MP, Maharashtra, Rajasthan, UP'},
    'Kidneybeans': {'season': 'Kharif/Rabi (July - Nov)', 'regions': 'Maharashtra, Karnataka, AP'},
    'Pigeonpeas': {'season': 'Kharif (June - October)', 'regions': 'Maharashtra, Karnataka, MP'},
    'Mothbeans': {'season': 'Kharif (July - October)', 'regions': 'Rajasthan, Haryana, Gujarat'},
    'Mungbean': {'season': 'Zaid/Kharif (March - June)', 'regions': 'Rajasthan, Maharashtra, AP'},
    'Blackgram': {'season': 'Kharif (June - October)', 'regions': 'UP, AP, Maharashtra, MP'},
    'Lentil': {'season': 'Rabi (October - March)', 'regions': 'UP, MP, Bihar, West Bengal'},
    'Pomegranate': {'season': 'All Year (Ideal planting Feb-Mar)', 'regions': 'Maharashtra, Gujarat, Karnataka'},
    'Banana': {'season': 'All Year (May - July planting)', 'regions': 'Tamil Nadu, Maharashtra, Gujarat'},
    'Mango': {'season': 'Summer (Planted July-Aug)', 'regions': 'UP, AP, Karnataka, Bihar'},
    'Grapes': {'season': 'Feb-March / Oct-Nov', 'regions': 'Maharashtra, Karnataka, Tamil Nadu'},
    'Watermelon': {'season': 'Summer (Zaid: Feb - March)', 'regions': 'UP, AP, Karnataka, West Bengal'},
    'Muskmelon': {'season': 'Summer (Zaid: Feb - March)', 'regions': 'UP, Punjab, MP, AP'},
    'Apple': {'season': 'Winter (Nov - Feb planting)', 'regions': 'Jammu & Kashmir, Himachal Pradesh, Uttarakhand'},
    'Orange': {'season': 'Monsoon (July - August)', 'regions': 'Maharashtra, MP, Assam'},
    'Papaya': {'season': 'All Year (Planted June/Oct/Feb)', 'regions': 'AP, Gujarat, Karnataka, MP'},
    'Coconut': {'season': 'All Year (Planted May-August)', 'regions': 'Kerala, Tamil Nadu, Karnataka'},
    'Cotton': {'season': 'Kharif (May - October)', 'regions': 'Gujarat, Maharashtra, Telangana'},
    'Jute': {'season': 'Zaid/Kharif (March - July)', 'regions': 'West Bengal, Bihar, Assam'},
    'Coffee': {'season': 'All Year (Planted Monsoon)', 'regions': 'Karnataka, Kerala, Tamil Nadu'}
}

WIKI_TITLE_MAP = {
    "blackgram": "Vigna_mungo",
    "kidneybeans": "Kidney_bean",
    "mothbeans": "Vigna_aconitifolia",
    "mungbean": "Vigna_radiata",
    "pigeonpeas": "Cajanus_cajan",
    "chickpea": "Chickpea",
    "muskmelon": "Muskmelon",
    "watermelon": "Watermelon",
    "pomegranate": "Pomegranate",
    "banana": "Banana",
    "mango": "Mango",
    "grapes": "Grape",
    "apple": "Apple",
    "orange": "Orange_(fruit)",
    "papaya": "Papaya",
    "coconut": "Coconut",
    "cotton": "Cotton",
    "jute": "Jute",
    "coffee": "Coffee",
    "rice": "Rice",
    "maize": "Maize",
    "lentil": "Lentil"
}

def fetch_crop_info_from_wiki(crop_name):
    wiki_title = WIKI_TITLE_MAP.get(crop_name.lower(), crop_name.capitalize())
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_title}"
    headers = {
        "User-Agent": "SmartCropApp/1.0 (https://github.com/example/react-flask)"
    }
    try:
        response = requests.get(url, headers=headers, timeout=2)
        if response.status_code == 200:
            data = response.json()
            return {
                "description": data.get("description", "Biological crop"),
                "extract": data.get("extract", "No biological summary found."),
                "image_url": data.get("thumbnail", {}).get("source", None)
            }
    except Exception as e:
        print("Wiki fetch error:", str(e))
    return {
        "description": "Crop details unavailable",
        "extract": "Could not retrieve comprehensive agricultural data.",
        "image_url": None
    }

@predict_bp.route('', methods=['POST'])
@token_required
@limiter.limit("5 per minute")
def predict(current_user_id):
    start_time = time.time()
    if not xgb_model or not label_encoder or not scaler:
        return jsonify({"message": "Machine learning models not loaded."}), 500

    data = request.json
    
    n = data.get('N')
    p = data.get('P')
    k = data.get('K')
    ph = data.get('ph')
    parsed_date = data.get('date', 'Unknown')

    if None in [n, p, k, ph]:
        return jsonify({"message": "N, P, K, and pH are required"}), 400

    # Clean empty strings into valid numbers for safety
    try:
        n = float(n)
        p = float(p)
        k = float(k)
        ph = float(ph)
    except ValueError:
        return jsonify({"message": "NPK and pH must be numeric."}), 400

    temp = data.get('temperature')
    hum = data.get('humidity')
    rain = data.get('rainfall')

    if temp is None or hum is None or rain is None:
        return jsonify({"message": "Temperature, humidity, and rainfall must be provided"}), 400

    input_df = pd.DataFrame([[n, p, k, temp, hum, ph, rain]], 
                            columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])
    input_scaled = scaler.transform(input_df)

    # Calculate probabilities for all models
    xgb_probs = xgb_model.predict_proba(input_scaled)[0]
    cat_probs = cat_model.predict_proba(input_scaled)[0]
    rf_probs = rf_model.predict_proba(input_scaled)[0]

    # Find the model with absolute highest maximum probability
    max_xgb = np.max(xgb_probs)
    max_cat = np.max(cat_probs)
    max_rf = np.max(rf_probs)

    best_probs = xgb_probs
    selected_model_name = "XGBoost"
    if max_cat > max_xgb and max_cat > max_rf:
        best_probs = cat_probs
        selected_model_name = "CatBoost"
    elif max_rf > max_xgb and max_rf > max_cat:
        best_probs = rf_probs
        selected_model_name = "RandomForest"
    
    # Get Top 3 Predictions
    top3_indices = np.argsort(best_probs)[-3:][::-1]
    top3_probs = best_probs[top3_indices]
    top3_labels = label_encoder.inverse_transform(top3_indices)
    
    # Construct Chart Data array for frontend
    chart_data = [{"name": str(lbl).capitalize(), "value": round(float(pr) * 100, 2)} for lbl, pr in zip(top3_labels, top3_probs)]
    
    best_pred = str(top3_labels[0]).capitalize()
    confidence = round(float(top3_probs[0]) * 100, 2)

    fallback_str = None
    if confidence < 40.0:
        fallback_str = "Low confidence prediction. Soil nutrient levels may be sub-optimal or anomalous. Verify manually."

    # Fertilizer calculation based roughly on ideal 100-50-50 range heuristic
    suggestions = []
    n_deficit = max(0, 100 - n)
    p_deficit = max(0, 50 - p)
    k_deficit = max(0, 50 - k)
    
    if n_deficit > 20: suggestions.append(f"Add ~{int(n_deficit)}kg/ha of Nitrogen (Urea)")
    elif n < 30: suggestions.append("Consider light high-nitrogen fertilizer")
    
    if p_deficit > 10: suggestions.append(f"Add ~{int(p_deficit)}kg/ha of Phosphorus (DAP)")
    elif p < 20: suggestions.append("Apply basic DAP amounts")
    
    if k_deficit > 10: suggestions.append(f"Add ~{int(k_deficit)}kg/ha of Potassium (MOP)")
    elif k < 20: suggestions.append("Apply basic MOP amounts")
    
    if n_deficit <= 20 and p_deficit <= 10 and k_deficit <= 10:
        suggestions.append("Current NPK ratio is optimal.")

    # Soil Health
    soil_health = "Optimal"
    if ph < 5.5: soil_health = "Highly Acidic (Consider adding agricultural lime)"
    elif ph > 8.0: soil_health = "Highly Alkaline (Consider adding sulfur or organic matter)"
    elif ph >= 5.5 and ph <= 6.5: soil_health = "Slightly Acidic (Good for most crops)"
    
    # Irrigation
    irrigation = "Standard schedule"
    if rain < 50 and temp > 30:
        irrigation = "High risk of drought. Irrigate every 2-3 days."
    elif rain > 150:
        irrigation = "High rainfall detected. Delay irrigation."

    geo_info = CROP_GEO_DICT.get(best_pred, {'season': 'Unknown', 'regions': 'Varied'})
    wiki_info = fetch_crop_info_from_wiki(best_pred)

    comparison_data = []
    target_input = data.get('target_crop', '').strip()
    if target_input:
        target_crop_lower = target_input.lower()
        classes_lower = [str(c).lower() for c in label_encoder.classes_]
        target_prob = 0
        if target_crop_lower in classes_lower:
            idx = classes_lower.index(target_crop_lower)
            target_prob = round(float(best_probs[idx]) * 100, 2)
        
        comparison_data = [
            {"name": "Best Match", "crop": best_pred, "value": confidence},
            {"name": "Your Input", "crop": target_input.capitalize(), "value": target_prob}
        ]

    latency_ms = int((time.time() - start_time) * 1000)

    result = {
        'crop': best_pred,
        'confidence': confidence,
        'chart_data': chart_data,
        'comparison_data': comparison_data,
        'fertilizer': suggestions,
        'geo_advice': geo_info,
        'wiki_info': wiki_info,
        'fallback': fallback_str,
        'soil_health': soil_health,
        'irrigation': irrigation,
        'selected_model': selected_model_name,
        'latency_ms': latency_ms,
        'timestamp': datetime.datetime.utcnow().isoformat()
    }

    try:
        db = get_db()
        from bson.objectid import ObjectId
        db.predictions.insert_one({
            'user_id': ObjectId(current_user_id),
            'inputs': {
                'N': n, 'P': p, 'K': k, 'ph': ph,
                'temperature': temp, 'humidity': hum, 'rainfall': rain,
                'target_date': parsed_date
            },
            'result': result
        })
    except Exception as e:
        print("Could not save to db:", str(e))

    return jsonify(result), 200
