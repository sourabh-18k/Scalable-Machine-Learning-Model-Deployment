from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import os
import numpy as np
import pandas as pd
import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
from fastapi.responses import Response

# load models
current_dir = os.path.dirname(os.path.abspath(__file__))
rf_path = os.path.join(current_dir, 'models', 'rf_model.pkl')
gb_path = os.path.join(current_dir, 'models', 'gb_model.pkl')
scaler_path = os.path.join(current_dir, 'models', 'scaler.pkl')

rf_model = joblib.load(rf_path)
gb_model = joblib.load(gb_path)
scaler = joblib.load(scaler_path)

app = FastAPI(title="Car Resale Price Prediction API")

# Prometheus metrics
requests_total = Counter(
    'carprice_api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'carprice_api_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

predictions_total = Counter(
    'carprice_api_predictions_total',
    'Total predictions made',
    ['model_type', 'status']
)

prediction_duration = Histogram(
    'carprice_api_prediction_duration_seconds',
    'Prediction duration in seconds',
    ['model_type']
)

predictions_in_progress = Gauge(
    'carprice_api_predictions_in_progress',
    'Predictions currently being processed'
)

class PredictRequest(BaseModel):
    
    registered_year: int
    engine_capacity: float
    kms_driven: float
    owner_type: str
    max_power: float
    seats: int
    mileage: float
    transmission_type: str
    fuel_type: str
    body_type: str
    brand_encoded: float
    model_freq: float
    model_choice: str 

def preprocess(req: PredictRequest):
    owner_map = {"First Owner": 1, "Second Owner": 2, "Third Owner": 3, "Fourth Owner": 4, "Fifth Owner": 5}
    transmission_map = {"Manual": 1, "Automatic": 0}
    fuel_map = {"Diesel": 4, "Petrol": 1, "CNG": 3, "LPG": 2, "Electric": 0}
    body_map = {"Hatchback": 2, "Sedan": 3, "SUV": 6, "MUV": 5, "Minivan": 1, "Pickup": 4, "Coupe": 0, "Wagon": 8, "Convertibles": 7}

    df = pd.DataFrame([[
        req.registered_year,
        req.engine_capacity,
        req.kms_driven,
        owner_map.get(req.owner_type, 1),
        req.max_power,
        req.seats,
        req.mileage,
        transmission_map.get(req.transmission_type, 1),
        fuel_map.get(req.fuel_type, 1),
        body_map.get(req.body_type, 2),
        req.brand_encoded,
        req.model_freq
    ]], columns=[
        "registered_year", "engine_capacity", "kms_driven", "owner_type",
        "max_power", "seats", "mileage",
        "transmission_type_encoded", "fuel_type_encoded", "body_type_encoded",
        "brand_encoded", "model_freq"
    ])
    
    numerical_cols = ["registered_year", "engine_capacity", "kms_driven", "max_power", "seats", "mileage"]
    df[numerical_cols] = scaler.transform(df[numerical_cols])
    return df

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(REGISTRY), media_type="text/plain")


@app.get("/")
def root():
    return {"message": "Car Price Prediction API — use /health or /predict"}

@app.post("/predict")
def predict(req: PredictRequest):
    predictions_in_progress.inc()
    start_time = time.time()
    
    try:
        df = preprocess(req)
        model = gb_model if req.model_choice == "Gradient Boosting" else rf_model
        log_price = model.predict(df)[0]
        predicted_price = float(np.expm1(log_price))
        
        # Record metrics
        duration = time.time() - start_time
        request_duration.labels(method='POST', endpoint='/predict').observe(duration)
        requests_total.labels(method='POST', endpoint='/predict', status=200).inc()
        prediction_duration.labels(model_type=req.model_choice).observe(duration)
        predictions_total.labels(model_type=req.model_choice, status='success').inc()
        
        return {"model": req.model_choice, "predicted_price": predicted_price}
    
    except Exception as e:
        duration = time.time() - start_time
        request_duration.labels(method='POST', endpoint='/predict').observe(duration)
        requests_total.labels(method='POST', endpoint='/predict', status=500).inc()
        predictions_total.labels(model_type="unknown", status='error').inc()
        raise
    
    finally:
        predictions_in_progress.dec()

