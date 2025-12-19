import requests
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, classification_report

# =========================
# CONFIG
# =========================

API_URL = (
        "http://127.0.0.1:8000/asteroids?start_date=2024-01-01&end_date=2024-01-03"

)

RANDOM_STATE = 42

# =========================
# LOAD DATA
# =========================

print("Fetching asteroid data...")
response = requests.get(API_URL)
response.raise_for_status()

data = response.json()
df = pd.DataFrame(data)

print("Raw data shape:", df.shape)
print(df.head())

# =========================
# FEATURE ENGINEERING
# =========================

# Target
df["hazardous"] = df["hazardous"].astype(int)

# Log-scaled features (critical for ML)
df["log_diameter"] = np.log1p(df["diameter_m"])
df["log_velocity"] = np.log1p(df["velocity_kph"])
df["log_distance"] = np.log1p(df["miss_distance_km"])

# Physics-informed feature (VERY strong)
df["kinetic_energy_proxy"] = (df["diameter_m"] ** 3) * (df["velocity_kph"] ** 2)
df["log_ke"] = np.log1p(df["kinetic_energy_proxy"])

# Proximity risk
df["proximity_score"] = 1 / df["miss_distance_km"]

FEATURES = [
    "log_diameter",
    "log_velocity",
    "log_distance",
    "log_ke",
    "proximity_score",
]

X = df[FEATURES]
y = df["hazardous"]

# =========================
# TRAIN / TEST SPLIT
# =========================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    stratify=y,
    random_state=RANDOM_STATE
)

print("Train size:", X_train.shape)
print("Test size:", X_test.shape)

# =========================
# LOGISTIC REGRESSION
# =========================

print("\nTraining Logistic Regression...")

log_reg = LogisticRegression(
    max_iter=1000,
    class_weight="balanced",
    random_state=RANDOM_STATE
)

log_reg.fit(X_train, y_train)

y_prob_lr = log_reg.predict_proba(X_test)[:, 1]
y_pred_lr = log_reg.predict(X_test)

print("Logistic Regression ROC-AUC:",
      roc_auc_score(y_test, y_prob_lr))
print(classification_report(y_test, y_pred_lr))

coef_df = pd.DataFrame({
    "feature": FEATURES,
    "coefficient": log_reg.coef_[0]
}).sort_values(by="coefficient", ascending=False)

print("\nLogistic Regression Feature Weights:")
print(coef_df)

# =========================
# RANDOM FOREST
# =========================

print("\nTraining Random Forest...")

rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=10,
    class_weight="balanced",
    random_state=RANDOM_STATE,
    n_jobs=-1
)

rf.fit(X_train, y_train)

y_prob_rf = rf.predict_proba(X_test)[:, 1]

print("Random Forest ROC-AUC:",
      roc_auc_score(y_test, y_prob_rf))

rf_importance = pd.DataFrame({
    "feature": FEATURES,
    "importance": rf.feature_importances_
}).sort_values(by="importance", ascending=False)

print("\nRandom Forest Feature Importance:")
print(rf_importance)

# =========================
# SAVE PREDICTIONS (FOR 3D VIZ)
# =========================

df["ml_risk_score"] = rf.predict_proba(X)[:, 1]

output_cols = [
    "name",
    "date",
    "diameter_m",
    "velocity_kph",
    "miss_distance_km",
    "hazardous",
    "ml_risk_score",
]

df[output_cols].to_json(
    "asteroid_ml_scores.json",
    orient="records",
    indent=2
)

print("\nSaved ML predictions to asteroid_ml_scores.json")
