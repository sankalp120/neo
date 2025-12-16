import requests
import pandas as pd

API_KEY = "DEMO_KEY"
URL = "https://api.nasa.gov/neo/rest/v1/feed"

params = {
    "start_date": "2024-01-01",
    "end_date": "2024-01-03",
    "api_key": API_KEY
}

response = requests.get(URL, params=params)
response.raise_for_status()
data = response.json()

rows = []

for date in data["near_earth_objects"]:
    for neo in data["near_earth_objects"][date]:
        approach = neo["close_approach_data"][0]

        rows.append({
            "name": neo["name"],
            "date": date,
            "diameter_min_m": neo["estimated_diameter"]["meters"]["estimated_diameter_min"],
            "diameter_max_m": neo["estimated_diameter"]["meters"]["estimated_diameter_max"],
            "velocity_kph": float(approach["relative_velocity"]["kilometers_per_hour"]),
            "miss_distance_km": float(approach["miss_distance"]["kilometers"]),
            "hazardous": neo["is_potentially_hazardous_asteroid"]
        })

df = pd.DataFrame(rows)

print(df.head())
print("\nTotal asteroids:", len(df))
