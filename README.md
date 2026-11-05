# CareCast AI — Medical Insurance Premium Estimator

A modern, responsive web application and production-grade REST API powered by a tuned **Random Forest Regressor (R² = 87.20%)** to predict individual medical insurance charges.

---

## 📁 Project Structure

```text
insurance/
├── app.py                      # Flask web application & REST API
├── insurance_model_bundle.pkl  # Trained model bundle (Random Forest + metadata)
├── train_model.py              # Script to retrain or export model bundle
├── requirements.txt            # Python dependencies
├── Procfile                    # Render / Heroku / Railway web process
├── Dockerfile                  # Containerized deployment spec
├── templates/
│   └── index.html              # Responsive frontend UI
└── static/
    ├── css/
    │   └── style.css           # Clean healthcare design system
    └── js/
        └── app.js              # Real-time BMI calc, animations & API integration
```

---

## 🚀 Running Locally

1. **Activate your environment and install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the application:**
   ```bash
   python app.py
   ```

3. **Open in your browser:**
   ```text
   http://127.0.0.1:5000
   ```

---

## 🌐 Deploying to the Cloud

### Option 1: Render (Recommended, Free & Fast)
1. Push this folder to a GitHub repository.
2. In [Render Dashboard](https://dashboard.render.com), click **New + > Web Service**.
3. Connect your GitHub repository.
4. Set:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Click **Create Web Service**. Your live public URL will be ready in 1-2 minutes!

### Option 2: Railway
1. Install Railway CLI or connect via GitHub on [railway.app](https://railway.app).
2. Railway will automatically detect the `Procfile` or `Dockerfile` and deploy with zero extra configuration.

### Option 3: Docker
Build and run the container locally or on any cloud server:
```bash
docker build -t insurance-estimator .
docker run -p 5000:5000 insurance-estimator
```

---

## 📡 REST API Documentation

### `POST /predict`
Send patient parameters in JSON or Form-URLencoded format:

#### Request Body
```json
{
  "age": 35,
  "sex": "male",
  "bmi": 26.5,
  "children": 2,
  "smoker": "no",
  "region": "southwest"
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "prediction": {
    "annual_charge": 5420.30,
    "monthly_charge": 451.69,
    "formatted_annual": "₹5,420.30",
    "formatted_monthly": "₹451.69"
  },
  "profile": {
    "age": 35,
    "sex": "Male",
    "bmi": 26.5,
    "bmi_category": "Overweight",
    "children": 2,
    "smoker": "No",
    "region": "Southwest"
  },
  "risk_analysis": {
    "tier": "Low",
    "tier_color": "#10b981",
    "drivers": [
      "Overweight BMI classification mildly increases base premium."
    ]
  },
  "model_metadata": {
    "algorithm": "RandomForestRegressor (Tuned)",
    "r2_score": "87.20%",
    "feature_count": 9
  }
}
```

### `GET /health`
Returns model status, algorithm details, and feature names.
