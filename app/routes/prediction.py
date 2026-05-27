import time
import joblib
import numpy as np
from flask import Blueprint, request, jsonify
from app.utils.weather import get_weather_data
from app.utils.disease_risk import calculate_disease_risk
from app.utils.logger import log_request, init_db

prediction_bp = Blueprint("prediction", __name__)

# Load model and scaler once when the app starts
model = None
scaler = None

def load_models():
    global model, scaler
    try:
        model = joblib.load("app/models/crop_model.pkl")
        scaler = joblib.load("app/models/scaler.pkl")
        print("✅ Models loaded successfully")
    except FileNotFoundError:
        print("⚠️  Models not found — train them first via notebooks/")


@prediction_bp.before_app_request
def setup():
    init_db()


@prediction_bp.route("/predict", methods=["POST"])
def predict():
    start_time = time.time()

    if model is None or scaler is None:
        return jsonify({"error": "Model not loaded. Please train the model first."}), 503

    data = request.get_json()

    # Validate required fields
    required_fields = ["location", "N", "P", "K", "ph"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    # Fetch live weather data
    try:
        weather = get_weather_data(data["location"])
    except Exception as e:
        return jsonify({"error": f"Weather API error: {str(e)}"}), 502

    # Build feature array: N, P, K, temperature, humidity, ph, rainfall
    features = np.array([[
        float(data["N"]),
        float(data["P"]),
        float(data["K"]),
        float(weather["temperature"]),
        float(weather["humidity"]),
        float(data["ph"]),
        float(weather["rainfall"])
    ]])

    features_scaled = scaler.transform(features)
    prediction = model.predict(features_scaled)[0]
    probabilities = model.predict_proba(features_scaled)[0]
    confidence = round(float(max(probabilities)) * 100, 1)

    # Calculate disease risk
    risk = calculate_disease_risk(
        prediction,
        weather["temperature"],
        weather["humidity"],
        weather["rainfall"]
    )

    response_ms = round((time.time() - start_time) * 1000, 2)

    # Log request to SQLite
    log_request(
        location=data["location"],
        prediction=prediction,
        confidence=confidence,
        disease_risk=risk["risk_level"],
        response_ms=response_ms,
        cache_hit=weather.get("cache_hit", False)
    )

    return jsonify({
        "recommended_crop": prediction,
        "confidence": confidence,
        "disease_risk": risk,
        "weather_used": weather,
        "response_ms": response_ms
    })