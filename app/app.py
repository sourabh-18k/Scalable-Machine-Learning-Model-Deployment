import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os


# Correct path handling
current_dir = os.path.dirname(os.path.abspath(__file__))  # Path of app.py
parent_dir = os.path.dirname(current_dir)  # Go one level up, where models/ is

# Load models and scaler using the correct path
rf_model = joblib.load(os.path.join(parent_dir, 'models', 'rf_model.pkl'))
gb_model = joblib.load(os.path.join(parent_dir, 'models', 'gb_model.pkl'))
scaler = joblib.load(os.path.join(parent_dir, 'models', 'scaler.pkl'))

st.title("🚗Vehiclesale Price Predictor")

st.markdown("Fill in the car details to get the predicted resale price.")

# Input form
with st.form("prediction_form"):
    registered_year = st.slider("Registered Year", 2000, 2025, 2015)
    engine_capacity = st.number_input("Engine Capacity (cc)", min_value=500, max_value=5000, value=1200)
    kms_driven = st.number_input("Kilometers Driven", min_value=0, max_value=500000, value=30000)
    owner_type = st.selectbox("Owner Type", ["First Owner", "Second Owner", "Third Owner", "Fourth Owner", "Fifth Owner"])
    max_power = st.number_input("Max Power (bhp)", min_value=20.0, max_value=500.0, value=85.0)
    seats = st.slider("Seats", 2, 10, 5)
    mileage = st.number_input("Mileage (kmpl)", min_value=5.0, max_value=40.0, value=18.0)

    transmission_type_encoded = st.selectbox("Transmission Type", ["Manual", "Automatic"])
    fuel_type_encoded = st.selectbox("Fuel Type", ["Diesel", "Petrol", "CNG", "LPG", "Electric"])
    body_type_encoded = st.selectbox("Body Type", ["Hatchback", "Sedan", "SUV", "MUV", "Minivan", "Pickup", "Coupe", "Wagon", "Convertibles"])

    brand_encoded = st.number_input("Brand Avg Resale Price", value=500000)
    model_freq = st.number_input("Model Popularity (Frequency)", value=0.01)

    model_choice = st.radio("Select Prediction Model", ("Random Forest", "Gradient Boosting"))

    submit = st.form_submit_button("Predict")

if submit:
    # Map values
    owner_map = {"First Owner": 1, "Second Owner": 2, "Third Owner": 3, "Fourth Owner": 4, "Fifth Owner": 5}
    transmission_map = {"Manual": 1, "Automatic": 0}
    fuel_map = {"Diesel": 4, "Petrol": 1, "CNG": 3, "LPG": 2, "Electric": 0}
    body_map = {"Hatchback": 2, "Sedan": 3, "SUV": 6, "MUV": 5, "Minivan": 1, "Pickup": 4, "Coupe": 0, "Wagon": 8, "Convertibles": 7}

    input_data = pd.DataFrame([[
        registered_year, engine_capacity, kms_driven,
        owner_map[owner_type], max_power, seats, mileage,
        transmission_map[transmission_type_encoded],
        fuel_map[fuel_type_encoded],
        body_map[body_type_encoded],
        brand_encoded, model_freq
    ]], columns=[
        "registered_year", "engine_capacity", "kms_driven", "owner_type",
        "max_power", "seats", "mileage",
        "transmission_type_encoded", "fuel_type_encoded", "body_type_encoded",
        "brand_encoded", "model_freq"
    ])

    # Scale numerical features
    numerical_cols = ["registered_year", "engine_capacity", "kms_driven", "max_power", "seats", "mileage"]
    input_data[numerical_cols] = scaler.transform(input_data[numerical_cols])

    # Predict
    model = gb_model if model_choice == "Gradient Boosting" else rf_model
    log_price = model.predict(input_data)[0]
    predicted_price = np.expm1(log_price)  # Inverse of log1p

    st.success(f"💰 Estimated Resale Price: ₹ {predicted_price:,.0f}")
