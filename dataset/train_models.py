import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score
import joblib
from xgboost import XGBClassifier
from catboost import CatBoostClassifier
from sklearn.ensemble import RandomForestClassifier

# Ensure models directory exists
models_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'models')
os.makedirs(models_dir, exist_ok=True)

def generate_synthetic_data():
    """Generates a synthetic Crop Recommendation dataset for 22 crops."""
    print("Generating comprehensive synthetic crop dataset (22 crops)...")
    np.random.seed(42)
    
    # Expert Profiles (N, P, K, Temp, Hum, pH, Rain)
    profiles = {
        'rice': (100, 95, 20, 32, 65, 5.2, 65),
        'maize': (10, 40, 170, 34, 45, 8.4, 80),
        'chickpea': (105, 63, 160, 22, 44, 8.0, 205),
        'kidneybeans': (55, 52, 120, 35, 62, 4.9, 215),
        'pigeonpeas': (65, 60, 185, 16, 50, 6.5, 220),
        'mothbeans': (18, 31, 128, 16, 31, 8.8, 268),
        'mungbean': (60, 48, 180, 40, 35, 6.8, 270),
        'blackgram': (110, 87, 127, 31, 88, 8.5, 272),
        'lentil': (106, 77, 94, 29, 59, 7.9, 23),
        'cotton': (105, 54, 119, 25, 85, 5.4, 165),
        'jute': (10, 110, 82, 38, 59, 6.0, 63),
        'coffee': (72, 34, 9, 15, 36, 6.9, 27),
        'pomegranate': (40, 18, 40, 28, 55, 7.0, 50),
        'banana': (100, 80, 50, 26, 80, 6.2, 225),
        'mango': (30, 30, 30, 27, 50, 6.0, 100),
        'grapes': (25, 130, 20, 22, 82, 6.5, 70),
        'watermelon': (50, 15, 50, 26, 85, 6.4, 50),
        'muskmelon': (90, 15, 50, 28, 92, 6.7, 25),
        'apple': (20, 130, 190, 23, 92, 5.8, 110),
        'orange': (20, 15, 10, 23, 95, 6.5, 110),
        'papaya': (50, 55, 50, 28, 95, 6.7, 150),
        'coconut': (20, 15, 30, 28, 95, 6.0, 150)
    }
    
    data = []
    for crop, (bN, bP, bK, bT, bH, bPH, bR) in profiles.items():
        for _ in range(120): # Increased sample size to 120 per crop
            n = max(0, min(140, bN + np.random.normal(0, 8)))
            p = max(5, min(145, bP + np.random.normal(0, 8)))
            k = max(5, min(205, bK + np.random.normal(0, 8)))
            temp = max(5, min(50, bT + np.random.normal(0, 1.5)))
            hum = max(5, min(100, bH + np.random.normal(0, 4)))
            ph = max(3.0, min(10.0, bPH + np.random.normal(0, 0.4)))
            rain = max(5, min(400, bR + np.random.normal(0, 10)))
            
            data.append([n, p, k, temp, hum, ph, rain, crop])

    df = pd.DataFrame(data, columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'label'])
    csv_path = os.path.join(os.path.dirname(__file__), 'synthetic_crop_data.csv')
    df.to_csv(csv_path, index=False)
    
    # Save descriptive stats for reference
    df.groupby('label').mean().to_csv(os.path.join(os.path.dirname(__file__), 'stats.txt'), sep='\t')
    
    return df

if __name__ == "__main__":
    df = generate_synthetic_data()
    
    # Preprocessing
    X = df.drop('label', axis=1)
    y = df['label']
    
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    
    # Scale data
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    def log_metrics(model_name, y_true, y_pred):
        acc = accuracy_score(y_true, y_pred)
        prec = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        rec = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        print(f"{model_name} - Accuracy: {acc:.4f}, Precision: {prec:.4f}, Recall: {rec:.4f}")

    # Training XGBoost
    print("Training XGBoost...")
    xgb_model = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42)
    xgb_model.fit(X_train_scaled, y_train)
    xgb_preds = xgb_model.predict(X_test_scaled)
    log_metrics("XGBoost", y_test, xgb_preds)
    
    # Train CatBoost
    print("Training CatBoost...")
    cat_model = CatBoostClassifier(verbose=0, random_state=42)
    cat_model.fit(X_train_scaled, y_train)
    cat_preds = cat_model.predict(X_test_scaled)
    log_metrics("CatBoost", y_test, cat_preds)

    # Train Random Forest
    print("Training Random Forest...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train_scaled, y_train)
    rf_preds = rf_model.predict(X_test_scaled)
    log_metrics("Random Forest", y_test, rf_preds)
    
    # Save Models
    print("Saving models to backend/models/...")
    joblib.dump(xgb_model, os.path.join(models_dir, 'xgb_model.joblib'))
    joblib.dump(cat_model, os.path.join(models_dir, 'cat_model.joblib'))
    joblib.dump(rf_model, os.path.join(models_dir, 'rf_model.joblib'))
    joblib.dump(scaler, os.path.join(models_dir, 'scaler.joblib'))
    joblib.dump(le, os.path.join(models_dir, 'label_encoder.joblib'))
    print("DONE. Models are ready for production.")
