import pytest
import joblib
import numpy as np
import os


def test_model_file_exists():
    assert os.path.exists("app/models/crop_model.pkl"), "Model file not found"
    assert os.path.exists("app/models/scaler.pkl"), "Scaler file not found"


def test_model_loads():
    model = joblib.load("app/models/crop_model.pkl")
    scaler = joblib.load("app/models/scaler.pkl")
    assert model is not None
    assert scaler is not None


def test_model_predicts():
    model = joblib.load("app/models/crop_model.pkl")
    scaler = joblib.load("app/models/scaler.pkl")
    
    # Sample input: N, P, K, temperature, humidity, ph, rainfall
    sample = np.array([[50, 40, 40, 25.0, 70.0, 6.5, 100.0]])
    scaled = scaler.transform(sample)
    prediction = model.predict(scaled)
    
    assert prediction is not None
    assert len(prediction) == 1
    assert isinstance(prediction[0], str)


def test_model_confidence():
    model = joblib.load("app/models/crop_model.pkl")
    scaler = joblib.load("app/models/scaler.pkl")
    
    sample = np.array([[90, 42, 43, 21.0, 82.0, 6.5, 202.0]])
    scaled = scaler.transform(sample)
    probabilities = model.predict_proba(scaled)[0]
    confidence = float(max(probabilities)) * 100
    
    assert confidence > 0
    assert confidence <= 100


def test_prediction_is_valid_crop():
    model = joblib.load("app/models/crop_model.pkl")
    scaler = joblib.load("app/models/scaler.pkl")
    
    valid_crops = [
        'rice', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas',
        'mothbeans', 'mungbean', 'blackgram', 'lentil', 'pomegranate',
        'banana', 'mango', 'grapes', 'watermelon', 'muskmelon',
        'apple', 'orange', 'papaya', 'coconut', 'cotton', 'jute', 'coffee'
    ]
    
    sample = np.array([[50, 40, 40, 25.0, 70.0, 6.5, 100.0]])
    scaled = scaler.transform(sample)
    prediction = model.predict(scaled)[0]
    
    assert prediction in valid_crops, f"Unexpected crop: {prediction}"