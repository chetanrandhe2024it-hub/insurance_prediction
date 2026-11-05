"""
Medical Insurance Premium Prediction - Model Training Script
Trains a tuned Random Forest Regressor on the insurance dataset.
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def train_and_export():
    dataset_path = 'insurance.csv'
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Cannot find {dataset_path}")

    print("Loading dataset...")
    df = pd.read_csv(dataset_path)

    # Preprocessing
    df['sex'] = df['sex'].map({'female': 0, 'male': 1})
    df['smoker'] = df['smoker'].map({'no': 0, 'yes': 1})
    df = pd.get_dummies(df, columns=['region'])
    df = df.astype(int)

    feature_cols = [c for c in df.columns if c != 'charges']
    x = df[feature_cols]
    y = df['charges']

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.20, random_state=42)

    print(f"Training tuned RandomForestRegressor (n_estimators=500)...")
    model = RandomForestRegressor(
        n_estimators=500,
        max_depth=15,
        min_samples_split=15,
        min_samples_leaf=2,
        random_state=42
    )
    model.fit(x_train, y_train)

    # Evaluate
    y_pred = model.predict(x_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    print(f"Validation R2 Score : {r2:.4f}")
    print(f"Validation MAE      : ${mae:.2f}")
    print(f"Validation RMSE     : ${rmse:.2f}")

    bundle = {
        'model': model,
        'feature_columns': feature_cols,
        'metrics': {
            'r2': float(r2),
            'mae': float(mae),
            'rmse': float(rmse)
        },
        'mappings': {
            'sex': {'female': 0, 'male': 1},
            'smoker': {'no': 0, 'yes': 1},
            'regions': ['northeast', 'northwest', 'southeast', 'southwest']
        }
    }

    joblib.dump(bundle, 'insurance_model_bundle.pkl')
    print("Exported trained model bundle to insurance_model_bundle.pkl")

if __name__ == '__main__':
    train_and_export()
