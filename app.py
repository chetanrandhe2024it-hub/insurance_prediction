"""
Flask Web Application for Medical Insurance Premium Prediction
Serves modern HTML/CSS/JS frontend and /predict REST API.
"""

import os
import joblib
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, static_folder='static', template_folder='templates')

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'insurance_model_bundle.pkl')

def load_bundle():
    """Load model and metadata from bundle."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model bundle not found at {MODEL_PATH}")
    
    bundle = joblib.load(MODEL_PATH)
    if isinstance(bundle, dict):
        model = bundle.get('model')
        feature_columns = bundle.get('feature_columns', [
            'age', 'sex', 'bmi', 'children', 'smoker',
            'region_northeast', 'region_northwest', 'region_southeast', 'region_southwest'
        ])
        metrics = bundle.get('metrics', {'r2': 0.8720})
    else:
        model = bundle
        feature_columns = [
            'age', 'sex', 'bmi', 'children', 'smoker',
            'region_northeast', 'region_northwest', 'region_southeast', 'region_southwest'
        ]
        metrics = {'r2': 0.8720}
    return model, feature_columns, metrics

try:
    model, feature_columns, metrics = load_bundle()
    print(f"Loaded model successfully. Features: {feature_columns}")
except Exception as e:
    print(f"Error loading model: {e}")
    model, feature_columns, metrics = None, [], {}


def get_bmi_category(bmi: float) -> dict:
    if bmi < 18.5:
        return {"category": "Underweight", "status": "info", "description": "BMI is below normal"}
    elif 18.5 <= bmi <= 24.9:
        return {"category": "Normal weight", "status": "success", "description": "Healthy weight range"}
    elif 25.0 <= bmi <= 29.9:
        return {"category": "Overweight", "status": "warning", "description": "Slightly elevated health risk"}
    else:
        return {"category": "Obese", "status": "danger", "description": "Significant risk factor for chronic conditions"}


def get_risk_analysis(age: int, smoker: int, bmi: float, charges: float) -> dict:
    drivers = []
    if smoker == 1:
        drivers.append("Smoking history is the primary cost multiplier (~3x-4x increase).")
    if bmi >= 30:
        drivers.append("High BMI (Obesity classification) notably elevates health & claims risk.")
    elif bmi >= 25:
        drivers.append("Overweight BMI classification mildly increases base premium.")
    if age >= 50:
        drivers.append("Age bracket (>50) contributes to higher actuarial baseline charges.")
    
    if not drivers:
        drivers.append("Standard baseline profile with minimal individual risk multipliers.")

    if charges < 6000:
        tier = "Low"
        tier_color = "#10b981"
    elif charges < 15000:
        tier = "Moderate"
        tier_color = "#3b82f6"
    elif charges < 30000:
        tier = "Elevated"
        tier_color = "#f59e0b"
    else:
        tier = "High"
        tier_color = "#ef4444"

    return {
        "tier": tier,
        "tier_color": tier_color,
        "drivers": drivers
    }


@app.route('/')
def home():
    """Render the main frontend single-page interface."""
    return render_template('index.html', model_accuracy="87.20%")


@app.route('/health', methods=['GET'])
def health():
    """Health check and model metadata endpoint."""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "algorithm": "RandomForestRegressor (Tuned 500 Estimators)",
        "r2_score": metrics.get('r2', 0.872),
        "features": feature_columns
    })


@app.route('/predict', methods=['POST'])
def predict():
    """
    Accepts JSON payload:
    {
        "age": 35,
        "sex": "male" or 1,
        "bmi": 26.5,
        "children": 2,
        "smoker": "no" or 0,
        "region": "southwest"
    }
    """
    if model is None:
        return jsonify({"success": False, "error": "Model is not initialized on server."}), 500

    try:
        # Handle both JSON and Form submissions
        data = request.get_json(silent=True) or request.form.to_dict()
        if not data:
            return jsonify({"success": False, "error": "No input data provided."}), 400

        # Validate & parse age
        age_raw = data.get('age')
        if age_raw is None or str(age_raw).strip() == '':
            return jsonify({"success": False, "error": "Field 'age' is required."}), 400
        age = int(float(age_raw))
        if age < 18 or age > 120:
            return jsonify({"success": False, "error": "Age must be between 18 and 120."}), 400

        # Validate & parse sex (female: 0, male: 1)
        sex_raw = str(data.get('sex', '')).strip().lower()
        if sex_raw in ['1', 'male', 'm']:
            sex = 1
            sex_label = "Male"
        elif sex_raw in ['0', 'female', 'f']:
            sex = 0
            sex_label = "Female"
        else:
            return jsonify({"success": False, "error": "Sex must be 'male' or 'female'."}), 400

        # Validate & parse BMI
        bmi_raw = data.get('bmi')
        if bmi_raw is None or str(bmi_raw).strip() == '':
            return jsonify({"success": False, "error": "Field 'bmi' is required."}), 400
        bmi = float(bmi_raw)
        if bmi < 10.0 or bmi > 70.0:
            return jsonify({"success": False, "error": "BMI must be between 10.0 and 70.0."}), 400

        # Validate & parse children
        children_raw = data.get('children', 0)
        children = int(float(children_raw)) if str(children_raw).strip() != '' else 0
        if children < 0 or children > 20:
            return jsonify({"success": False, "error": "Children count must be between 0 and 20."}), 400

        # Validate & parse smoker (no: 0, yes: 1)
        smoker_raw = str(data.get('smoker', '')).strip().lower()
        if smoker_raw in ['1', 'yes', 'y', 'true']:
            smoker = 1
            smoker_label = "Yes"
        elif smoker_raw in ['0', 'no', 'n', 'false']:
            smoker = 0
            smoker_label = "No"
        else:
            return jsonify({"success": False, "error": "Smoker must be 'yes' or 'no'."}), 400

        # Validate & parse region
        region_raw = str(data.get('region', '')).strip().lower()
        valid_regions = ['northeast', 'northwest', 'southeast', 'southwest']
        if region_raw not in valid_regions:
            return jsonify({
                "success": False,
                "error": f"Invalid region '{region_raw}'. Must be one of: {', '.join(valid_regions)}"
            }), 400

        # Construct input row matching model feature columns
        row = {
            'age': age,
            'sex': sex,
            'bmi': bmi,
            'children': children,
            'smoker': smoker,
            'region_northeast': 1 if region_raw == 'northeast' else 0,
            'region_northwest': 1 if region_raw == 'northwest' else 0,
            'region_southeast': 1 if region_raw == 'southeast' else 0,
            'region_southwest': 1 if region_raw == 'southwest' else 0
        }

        # Model expects DataFrame with columns
        input_df = pd.DataFrame([row])[feature_columns]

        # Predict
        predicted_charge = float(model.predict(input_df)[0])
        predicted_charge = max(round(predicted_charge, 2), 0.0)
        monthly_charge = round(predicted_charge / 12.0, 2)

        bmi_info = get_bmi_category(bmi)
        risk_info = get_risk_analysis(age, smoker, bmi, predicted_charge)

        return jsonify({
            "success": True,
            "prediction": {
                "annual_charge": predicted_charge,
                "monthly_charge": monthly_charge,
                "formatted_annual": f"₹{predicted_charge:,.2f}",
                "formatted_monthly": f"₹{monthly_charge:,.2f}",
            },
            "profile": {
                "age": age,
                "sex": sex_label,
                "bmi": round(bmi, 1),
                "bmi_category": bmi_info["category"],
                "bmi_status": bmi_info["status"],
                "bmi_description": bmi_info["description"],
                "children": children,
                "smoker": smoker_label,
                "region": region_raw.capitalize()
            },
            "risk_analysis": risk_info,
            "model_metadata": {
                "algorithm": "RandomForestRegressor (Tuned)",
                "r2_score": "87.20%",
                "feature_count": len(feature_columns)
            }
        })

    except ValueError as ve:
        return jsonify({"success": False, "error": f"Input formatting error: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Prediction server error: {str(e)}"}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
