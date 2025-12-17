import requests
import math
import os
from dotenv import load_dotenv
# -----------------------------
# CONFIG
# -----------------------------
load_dotenv()
API_KEY = os.getenv("NASA_API_KEY") 
NASA_URL = "https://api.nasa.gov/neo/rest/v1/feed"

START_DATE = "2024-01-01"
END_DATE = "2024-01-07"

PAIR_THRESHOLD = 40 

# -----------------------------
# PAIR MODEL (same as API)
# -----------------------------
def compute_pair_risk(diameter_m, velocity_kph, miss_distance_km):
    D0 = 384000
    probability = math.exp(-miss_distance_km / D0)

    diameter_n = diameter_m / 2000
    velocity_n = velocity_kph / 100000

    impact = (diameter_n ** 3) * (velocity_n ** 2)
    risk = probability * impact

    return min(risk * 1e6, 100)

# -----------------------------
# FETCH DATA
# -----------------------------
params = {
    "start_date": START_DATE,
    "end_date": END_DATE,
    "api_key": API_KEY
}

data = requests.get(NASA_URL, params=params).json()
if "near_earth_objects" not in data:
    print("NASA API error response:")
    print(data)
    exit()
# -----------------------------
# VALIDATION LOOP
# -----------------------------
TP = FP = TN = FN = 0

for date in data["near_earth_objects"]:
    for neo in data["near_earth_objects"][date]:
        approach = neo["close_approach_data"][0]

        diameter = neo["estimated_diameter"]["meters"]["estimated_diameter_max"]
        velocity = float(approach["relative_velocity"]["kilometers_per_hour"])
        distance = float(approach["miss_distance"]["kilometers"])

        pair_score = compute_pair_risk(diameter, velocity, distance)

        predicted_hazardous = pair_score >= PAIR_THRESHOLD
        actual_hazardous = neo["is_potentially_hazardous_asteroid"]

        if predicted_hazardous and actual_hazardous:
            TP += 1
        elif predicted_hazardous and not actual_hazardous:
            FP += 1
        elif not predicted_hazardous and not actual_hazardous:
            TN += 1
        else:
            FN += 1

# -----------------------------
# METRICS
# -----------------------------
precision = TP / (TP + FP) if (TP + FP) else 0
recall = TP / (TP + FN) if (TP + FN) else 0

print("PAIR Validation Results")
print("-----------------------")
print(f"Threshold: {PAIR_THRESHOLD}")
print(f"TP: {TP}, FP: {FP}, TN: {TN}, FN: {FN}")
print(f"Precision: {precision:.2f}")
print(f"Recall: {recall:.2f}")
