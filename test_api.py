import requests
import json
import time

URL = "http://127.0.0.1:8000/route"

# Coordinates from previous successful manual routing test
# Start: Node 74739 (approx lat/lon needed)
# End: Node 9418 

# Since I don't have exact lat/lon for those nodes handy without querying DB,
# I'll use generic Karachi coordinates and let the API find nearest nodes.
# Karachi Bounds: ~24.7 to 25.1 N, ~66.8 to 67.2 E

# Coordinates for known connected nodes 74739 -> 9418
# We'll fetch them from DB dynamically to be safe
import psycopg2

DB_CONFIG = {
    "dbname": "karachi_routing",
    "user": "postgres",
    "password": "080907",
    "host": "localhost",
    "port": "5432"
}

def get_node_coords(node_id):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(f"SELECT ST_X(the_geom), ST_Y(the_geom) FROM lines_vertices_pgr WHERE id = {node_id}")
    row = cur.fetchone()
    conn.close()
    return row

def test_api():
    print("Fetching coordinates for known connected nodes...")
    start_coords = get_node_coords(74739)
    end_coords = get_node_coords(9418)
    
    if not start_coords or not end_coords:
        print("❌ Could not fetch coordinates from DB.")
        return

    # Test Invalid Route (Disconnected Nodes)
    # 679346 and 195051 failed before
    # NOW: Should succeed by snapping to major roads!
    print("\nTesting Disconnected Route (Expect 200 with Retry)...")
    try:
        response = requests.post(f"{URL}", json={
            "start_lat": 24.8607, # Dummy lat
            "start_lon": 67.0011,
            "end_lat": 24.9000, 
            "end_lon": 67.0500,
            "mode": "clean"
        })
        if response.status_code == 200:
             print("✅ Success: Route found via Major Road fallback!")
             data = response.json()
             print(f"   Nodes visited: {data['metadata']['nodes_visited']}")
        else:
             print(f"❌ Failed: {response.status_code}")
             print(response.text)

    except Exception as e:
        print(f"❌ Error during invalid route test: {e}")

    req_data = {
        "start_lat": start_coords[1],
        "start_lon": start_coords[0],
        "end_lat": end_coords[1],
        "end_lon": end_coords[0],
        "mode": "clean"
    }
    
    print(f"Testing route from {start_coords} to {end_coords}...")
    
    print("Sending request to API...")
    try:
        start_time = time.time()
        response = requests.post(URL, json=req_data)
        end_time = time.time()
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Response Metadata:")
            print(json.dumps(data.get("metadata", {}), indent=2))
            
            features = data.get("features", [])
            print(f"Received {len(features)} path segments.")
            
            if len(features) > 0:
                print("✅ API Test Passed: Route found.")
            else:
                print("⚠️ API Test Warning: Route found but empty features?")
                
        else:
            print(f"❌ API Test Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    # Wait a bit for server to start if run immediately
    time.sleep(2) 
    test_api()
