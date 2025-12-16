import requests

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

print("Total NEOs returned:", data["element_count"])
print("Days returned:", len(data["near_earth_objects"]))

first_day = list(data["near_earth_objects"].keys())[0]
first_asteroid = data["near_earth_objects"][first_day][0]

print("\nSample asteroid")
print("Name:", first_asteroid["name"])
print("Hazardous:", first_asteroid["is_potentially_hazardous_asteroid"])
print(
    "Diameter (m):",
    first_asteroid["estimated_diameter"]["meters"]["estimated_diameter_min"]
)
print(
    "Miss distance (km):",
    first_asteroid["close_approach_data"][0]["miss_distance"]["kilometers"]
)
