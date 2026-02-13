import requests
import psycopg2
import json

# DB CONFIG
DB_CONFIG = {
    "dbname": "karachi_routing",
    "user": "postgres",
    "password": "080907",
    "host": "localhost",
    "port": "5432"
}

# OpenAQ API Endpoint for Karachi
# Using a broader search or specific location ID might be needed if "Karachi" city query is strict
# OpenAQ API Endpoint for Karachi (v3)
# We need to find locations in Karachi first.
# Using bounding box for Karachi approx: 66.8, 24.7, 67.2, 25.1
# Or just searching by country/city if supported. v3 uses /locations
URL = "https://api.openaq.org/v3/locations?coordinates=67.0011,24.8607&radius=25000&limit=100"

def fetch_and_store():
    # Simulated Mode due to API Key requirement
    try:
        print("Using SIMULATED real-time data (OpenAQ API requires key)...")
        
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Simulate 5 sensors in Karachi
        simulated_sensors = [
            {"name": "US Consulate", "lat": 24.84, "lon": 67.00, "pm25": 150}, # Bad
            {"name": "Clifton Beach", "lat": 24.80, "lon": 67.03, "pm25": 80},  # Moderate
            {"name": "Gulshan-e-Iqbal", "lat": 24.92, "lon": 67.09, "pm25": 120}, # Bad
            {"name": "Malir Cantt", "lat": 24.95, "lon": 67.18, "pm25": 40},   # Good
            {"name": "Korangi Industrial", "lat": 24.83, "lon": 67.12, "pm25": 200} # Hazardous
        ]
        
        for s in simulated_sensors:
            cur.execute("DELETE FROM sensor_readings WHERE sensor_name = %s", (s['name'],))
            sql = """
            INSERT INTO sensor_readings (sensor_name, lat, lon, pm25, geom)
            VALUES (%s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
            """
            cur.execute(sql, (s['name'], s['lat'], s['lon'], s['pm25'], s['lon'], s['lat']))
            print(f"Simulated Update {s['name']}: {s['pm25']} µg/m³")

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_and_store()
