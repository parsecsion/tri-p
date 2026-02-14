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

# OpenAQ API Endpoint for Karachi (v3) - Locations Query
URL = "https://api.openaq.org/v3/locations?coordinates=24.8607,67.0011&radius=25000&limit=100"

# ---------------------------------------------------------
# 🔑 PASTE YOUR OPENAQ API KEY BELOW
# ---------------------------------------------------------
API_KEY = "56796d9bc569cef87a84d0c47792fd275eeb1655e3c2b8b967fea686011ae3e7" 
# ---------------------------------------------------------

def fetch_and_store():
    # Check if user added key
    if API_KEY == "YOUR_API_KEY_HERE":
        print("❌ ERROR: Please open 'd:\\Projects\\tri-p\\fetch_aqi.py' and paste your OpenAQ API Key in the `API_KEY` variable.")
        return

    try:
        print(f"Fetching LOCATIONS from {URL}...")
        
        headers = {
            "X-API-Key": API_KEY,
            "Accept": "application/json"
        }
        
        response = requests.get(URL, headers=headers)
        
        if response.status_code == 401:
            print("❌ Unauthorized: Your API Key is invalid.")
            return

        if response.status_code != 200:
            print(f"❌ API Error {response.status_code}: {response.text}")
            return
            
        data = response.json()
        
        if 'results' not in data:
            print("No 'results' found in response.")
            return

        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        locations_found = len(data['results'])
        print(f"Found {locations_found} monitoring locations. Fetching measurements...")

        count_updated = 0
        
        for result in data['results']:
            loc_id = result.get('id')
            name = result.get('name', f"Station {loc_id}")
            
            coords = result.get('coordinates')
            if not coords:
                continue
            
            lat = coords.get('latitude')
            lon = coords.get('longitude')
            
            # Find PM2.5 sensor ID
            sensor_id = None
            
            for sensor in result.get('sensors', []):
                param = sensor.get('parameter', {}).get('name')
                if param == 'pm25':
                    sensor_id = sensor.get('id')
                    break
            
            if not sensor_id:
                continue
            
            # FETCH MEASUREMENT for this sensor
            # /v3/sensors/{id}/measurements?limit=1
            meas_url = f"https://api.openaq.org/v3/sensors/{sensor_id}/measurements?limit=1"
            try:
                meas_res = requests.get(meas_url, headers=headers)
                if meas_res.status_code == 200:
                    meas_data = meas_res.json()
                    results = meas_data.get('results', [])
                    if results:
                        pm25 = results[0].get('value')
                        
                        # UPSERT into DB
                        cur.execute("DELETE FROM sensor_readings WHERE sensor_name = %s", (name,))
                        
                        sql = """
                        INSERT INTO sensor_readings (sensor_name, lat, lon, pm25, geom)
                        VALUES (%s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
                        """
                        cur.execute(sql, (name, lat, lon, pm25, lon, lat))
                        count_updated += 1
                        print(f"Updated {name}: {pm25} µg/m³")
                    else:
                        print(f"No measurements for {name}")
            except Exception as e:
                print(f"Error fetching sensor {sensor_id}: {e}")

        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ Successfully updated {count_updated} sensors in the database.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_and_store()
