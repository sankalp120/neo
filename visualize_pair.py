import requests
import math
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt

# -----------------------------
# CONFIG
# -----------------------------
load_dotenv()

NASA_API_KEY = os.getenv("NASA_API_KEY")
NASA_URL = "https://api.nasa.gov/neo/rest/v1/feed"

START_DATE = "2024-01-01"
END_DATE = "2024-01-07"

# -----------------------------
# PAIR COMPONENTS
# -----------------------------
def compute_pair_components(diameter_m, velocity_kph, miss_distance_km):
    D0 = 384000  # Earth–Moon distance (km)
    probability = math.exp(-miss_distance_km / D0)

    diameter_n = diameter_m / 2000
    velocity_n = velocity_kph / 100000

    impact = (diameter_n ** 3) * (velocity_n ** 2)
    return probability, impact

# -----------------------------
# FETCH DATA
# -----------------------------
params = {
    "start_date": START_DATE,
    "end_date": END_DATE,
    "api_key": NASA_API_KEY
}

data = requests.get(NASA_URL, params=params).json()

if "near_earth_objects" not in data:
    print("NASA API error:", data)
    exit()

# -----------------------------
# COLLECT POINTS
# -----------------------------
prob_hazard, impact_hazard = [], []
prob_safe, impact_safe = [], []

for date in data["near_earth_objects"]:
    for neo in data["near_earth_objects"][date]:
        approach = neo["close_approach_data"][0]

        diameter = neo["estimated_diameter"]["meters"]["estimated_diameter_max"]
        velocity = float(approach["relative_velocity"]["kilometers_per_hour"])
        distance = float(approach["miss_distance"]["kilometers"])

        p, i = compute_pair_components(diameter, velocity, distance)

        if neo["is_potentially_hazardous_asteroid"]:
            prob_hazard.append(p)
            impact_hazard.append(i)
        else:
            prob_safe.append(p)
            impact_safe.append(i)

# -----------------------------
# VISUALIZATION
# -----------------------------
plt.figure()

plt.scatter(prob_safe, impact_safe, label="Non-hazardous", alpha=0.6)
plt.scatter(prob_hazard, impact_hazard, label="Hazardous", alpha=0.9)

plt.xlabel("Impact Probability (proxy)")
plt.ylabel("Impact Severity (proxy)")
plt.yscale("log")
plt.title("PAIR: Probability vs Impact (Color-coded by NASA Hazard Flag)")
plt.legend()
plt.show()
