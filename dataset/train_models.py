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
    """Generates a synthetic Crop Recommendation dataset similar to the Kaggle one."""
    print("Generating synthetic crop dataset...")
    np.random.seed(42)
    crops = ['rice', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas',
             'mothbeans', 'mungbean', 'blackgram', 'lentil', 'cotton', 'jute', 'coffee']
    
    data = []
    for crop in crops:
        # Base stats per crop (approximate logic for synthetic generation)
        base_n = np.random.randint(0, 120)
        base_p = np.random.randint(5, 140)
        base_k = np.random.randint(5, 200)
        base_temp = np.random.uniform(15, 40)
        base_hum = np.random.uniform(14, 100)
        base_ph = np.random.uniform(4.5, 9.0)
        base_rain = np.random.uniform(20, 298)
        
        for _ in range(100):
            n = max(0, min(140, base_n + np.random.normal(0, 10)))
            p = max(5, min(145, base_p + np.random.normal(0, 10)))
            k = max(5, min(205, base_k + np.random.normal(0, 10)))
            temp = max(8, min(45, base_temp + np.random.normal(0, 2)))
            hum = max(10, min(100, base_hum + np.random.normal(0, 5)))
            ph = max(3.5, min(9.9, base_ph + np.random.normal(0, 0.5)))
            rain = max(10, min(300, base_rain + np.random.normal(0, 15)))
            
            data.append([n, p, k, temp, hum, ph, rain, crop])

    df = pd.DataFrame(data, columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'label'])
    df.to_csv(os.path.join(os.path.dirname(__file__), 'synthetic_crop_data.csv'), index=False)
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
