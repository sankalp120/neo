import requests
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# CONFIG
# -----------------------------
API_KEY = "DEMO_KEY"  # replace later with your real key
URL = "https://api.nasa.gov/neo/rest/v1/feed"

START_DATE = "2024-01-01"
END_DATE = "2024-01-03"

# -----------------------------
# FETCH DATA FROM NASA
# -----------------------------
params = {
    "start_date": START_DATE,
    "end_date": END_DATE,
    "api_key": API_KEY
}

response = requests.get(URL, params=params)
response.raise_for_status()
data = response.json()

# -----------------------------
# FLATTEN JSON INTO TABLE
# -----------------------------
rows = []

for date in data["near_earth_objects"]:
    for neo in data["near_earth_objects"][date]:
        approach = neo["close_approach_data"][0]

        rows.append({
            "name": neo["name"],
            "date": date,
            "diameter_m": neo["estimated_diameter"]["meters"]["estimated_diameter_max"],
            "velocity_kph": float(approach["relative_velocity"]["kilometers_per_hour"]),
            "miss_distance_km": float(approach["miss_distance"]["kilometers"]),
            "hazardous": neo["is_potentially_hazardous_asteroid"]
        })

df = pd.DataFrame(rows)

print("Dataset preview:")
print(df.head())
print("\nTotal asteroids:", len(df))

# -----------------------------
# EDA PLOTS
# -----------------------------

# 1. Velocity distribution
plt.figure()
plt.hist(df["velocity_kph"], bins=20)
plt.xlabel("Velocity (km/h)")
plt.ylabel("Count")
plt.title("Distribution of Asteroid Velocities")
plt.show()

# 2. Miss distance vs diameter
plt.figure()
plt.scatter(
    df["miss_distance_km"],
    df["diameter_m"]
)
plt.xlabel("Miss Distance (km)")
plt.ylabel("Diameter (m)")
plt.title("Miss Distance vs Asteroid Diameter")
plt.show()

# 3. Hazardous vs Non-Hazardous count
counts = df["hazardous"].value_counts()

plt.figure()
plt.bar(counts.index.astype(str), counts.values)
plt.xlabel("Hazardous")
plt.ylabel("Count")
plt.title("Hazardous vs Non-Hazardous Asteroids")
plt.show()
