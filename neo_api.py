from fastapi import FastAPI
import requests
import os
from dotenv import load_dotenv
load_dotenv()
app = FastAPI(title="NASA NEO API")

@app.get("/")
def root():
    return {"message": "NASA NEO API is running"}


API_KEY = os.getenv("NASA_API_KEY")
NASA_URL = "https://api.nasa.gov/neo/rest/v1/feed"

def fetch_neo_data(start_date: str, end_date: str):
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "api_key": API_KEY
    }
    response = requests.get(NASA_URL, params=params)
    response.raise_for_status()
    return response.json()

@app.get("/asteroids")
def get_asteroids(start_date: str, end_date: str):
    data = fetch_neo_data(start_date, end_date)

    asteroids = []

    for date in data["near_earth_objects"]:
        for neo in data["near_earth_objects"][date]:
            approach = neo["close_approach_data"][0]
            asteroids.append({
                "name": neo["name"],
                "date": date,
                "diameter_m": neo["estimated_diameter"]["meters"]["estimated_diameter_max"],
                "velocity_kph": float(approach["relative_velocity"]["kilometers_per_hour"]),
                "miss_distance_km": float(approach["miss_distance"]["kilometers"]),
                "hazardous": neo["is_potentially_hazardous_asteroid"]
            })

    return asteroids
