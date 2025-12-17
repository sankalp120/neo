from fastapi import FastAPI
import requests
import math
import os
from dotenv import load_dotenv

# -----------------------------
# ENV + APP SETUP
# -----------------------------
load_dotenv()

app = FastAPI(title="NASA NEO Probabilistic Risk API")

NASA_API_KEY = os.getenv("NASA_API_KEY")
NASA_URL = "https://api.nasa.gov/neo/rest/v1/feed"

# -----------------------------
# NASA DATA FETCH
# -----------------------------
def fetch_neo_data(start_date: str, end_date: str):
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "api_key": NASA_API_KEY
    }
    response = requests.get(NASA_URL, params=params)
    response.raise_for_status()
    return response.json()

# -----------------------------
# PAIR: Probabilistic Asteroid Impact Risk
# -----------------------------
def compute_pair_risk(diameter_m, velocity_kph, miss_distance_km):
    """
    PAIR = P(impact) × Impact Severity
    """

    # ---- Probability of impact (distance-based decay) ----
    # Earth–Moon distance ≈ 384,000 km
    D0 = 384000
    probability = math.exp(-miss_distance_km / D0)

    # ---- Impact severity (kinetic energy proxy) ----
    # mass ∝ diameter^3, energy ∝ mass × velocity^2
    diameter_n = diameter_m / 2000        # normalize size
    velocity_n = velocity_kph / 100000    # normalize speed

    impact = (diameter_n ** 3) * (velocity_n ** 2)

    # ---- Final PAIR score ----
    raw_risk = probability * impact

    # Scale to human-friendly range (0–100)
    pair_score = min(raw_risk * 1e6, 100)

    return round(pair_score, 2), {
        "impact_probability": round(probability, 6),
        "impact_severity": round(impact, 6)
    }

# -----------------------------
# ROOT ENDPOINT
# -----------------------------
@app.get("/")
def root():
    return {"message": "NASA NEO Probabilistic Risk API is running"}

# -----------------------------
# ASTEROIDS ENDPOINT (WITH PAIR)
# -----------------------------
@app.get("/asteroids")
def get_asteroids(start_date: str, end_date: str):
    data = fetch_neo_data(start_date, end_date)
    asteroids = []

    for date in data["near_earth_objects"]:
        for neo in data["near_earth_objects"][date]:
            approach = neo["close_approach_data"][0]

            diameter_m = neo["estimated_diameter"]["meters"]["estimated_diameter_max"]
            velocity_kph = float(
                approach["relative_velocity"]["kilometers_per_hour"]
            )
            miss_distance_km = float(
                approach["miss_distance"]["kilometers"]
            )

            pair_score, pair_components = compute_pair_risk(
                diameter_m,
                velocity_kph,
                miss_distance_km
            )

            asteroids.append({
                "name": neo["name"],
                "date": date,
                "diameter_m": round(diameter_m, 2),
                "velocity_kph": round(velocity_kph, 2),
                "miss_distance_km": round(miss_distance_km, 2),
                "hazardous": neo["is_potentially_hazardous_asteroid"],
                "pair_risk_score": pair_score,
                "pair_components": pair_components
            })

    return asteroids
