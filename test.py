import joblib, pandas as pd, numpy as np, os
models_dir = os.path.join('backend', 'models')
xgb_model = joblib.load(os.path.join(models_dir, 'xgb_model.joblib'))
label_encoder = joblib.load(os.path.join(models_dir, 'label_encoder.joblib'))
input_df = pd.DataFrame([[50, 50, 50, 25, 60, 6.5, 100]], columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])
xgb_probs = xgb_model.predict_proba(input_df)[0]
top5_indices = np.argsort(xgb_probs)[-5:][::-1]
top5_probs = xgb_probs[top5_indices]
top5_labels = label_encoder.inverse_transform(top5_indices)
print(top5_labels)
