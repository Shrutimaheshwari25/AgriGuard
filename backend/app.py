import os
import sys
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Load env variables
load_dotenv()

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask App
app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = "shruti_agri_project_2026_secure"
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/agri_db')

from utils.limiter import limiter
limiter.init_app(app)

# Register Blueprints
from routes.auth import auth_bp
from routes.predict import predict_bp
from routes.weather import weather_bp
from routes.dashboard import dashboard_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(predict_bp, url_prefix='/api/predict')
app.register_blueprint(weather_bp, url_prefix='/api/weather')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "running", "message": "Smart Crop API is healthy"}), 200

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"message": f"Rate limit exceeded: {e.description}"}), 429

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Server Error: {str(e)}", exc_info=True)
    return jsonify({
        "message": "Internal Server Error",
        "error": str(e) if app.debug else "An unexpected error occurred."
    }), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
    
