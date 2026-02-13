import psycopg2
import json

# DB CONFIG
DB_CONFIG = {
    "dbname": "karachi_routing",
    "user": "postgres",
    "password": "080907", # Password from context
    "host": "localhost",
    "port": "5432"
}

def get_route(start_id, end_id, cost_column):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # We use pgr_dijkstra. 
        # Note: We select 'ogc_fid' as id, because ogr2ogr uses that.
        query = f"""
        SELECT seq, node, edge, cost, agg_cost 
        FROM pgr_dijkstra(
            'SELECT ogc_fid as id, source, target, {cost_column} as cost FROM lines',
            {start_id}, 
            {end_id}, 
            directed := false
        );
        """
        
        cur.execute(query)
        rows = cur.fetchall()
        
        # Calculate total physical distance (sum of lengths, not costs)
        # We need to fetch the actual length of the edges returned
        total_meters = 0
        if rows:
            # edge is the 3rd column (index 2). -1 is the last node
            edge_ids = [str(r[2]) for r in rows if r[2] != -1] 
            if edge_ids:
                # Need to cast to string for the IN clause
                cur.execute(f"SELECT sum(length_m) FROM lines WHERE ogc_fid IN ({','.join(edge_ids)})")
                res = cur.fetchone()
                if res and res[0]:
                    total_meters = res[0]

        cur.close()
        conn.close()
        # Return count of nodes, total physical distance, and the rows
        return len(rows), total_meters, rows
        
    except Exception as e:
        print(f"Error: {e}")
        return 0, 0, []

# --- MAIN EXECUTION ---

def find_and_test_route():
    # List of 50 guaranteed connected nodes from largest component
    nodes = [
        80007, 1386572, 1976240, 123373, 1509906, 528224, 469990, 145624, 40077, 555407, 
        3914, 158897, 747121, 267748, 12108, 1838101, 1139641, 1954188, 1719144, 679537, 
        1099488, 232098, 1120091, 13750, 42725, 649886, 46533, 1977545, 1791319, 945619, 
        1289795, 624305, 707377, 15427, 1317718, 1600788, 1163605, 2040808, 353259, 1109496, 
        67867, 99777, 22594, 32423, 542750, 77090, 1779529, 1717997, 1699655, 28665
    ]
    
    import random
    
    attempts = 0
    max_attempts = 50
    
    while attempts < max_attempts:
        attempts += 1
        print(f"Attempt {attempts} to find a DIVERGENT route...")
        
        # Pick two random nodes from our list
        start_node = random.choice(nodes)
        end_node = random.choice(nodes)
        
        if start_node == end_node:
            continue
            
        # Check fast route
        count_fast, dist_fast, _ = get_route(start_node, end_node, 'length_m')
        
        if count_fast > 0:
            print(f"Found path ({dist_fast:.0f}m)... checking clean route...")

            # Check clean route
            count_clean, dist_clean, _ = get_route(start_node, end_node, 'pollution_cost')
            
            # If routes differ significantly (by > 1 meter)
            if dist_clean > dist_fast + 1.0:
                print(f"\nFOUND DIVERGENT PATH from Node {start_node} to {end_node}")
                print("-" * 50)
                
                print(f"🚗 FAST ROUTE (Minimize Meters):")
                print(f"   - Nodes Visited: {count_fast}")
                print(f"   - Total Distance: {dist_fast:.2f} meters")

                print(f"\n🍃 CLEAN ROUTE (Minimize Pollution):")
                print(f"   - Nodes Visited: {count_clean}")
                print(f"   - Total Distance: {dist_clean:.2f} meters")

                print("-" * 50)
                print("✅ SUCCESS: The Clean algorithm chose a DIFFERENT, LONGER path to avoid pollution.")
                diff = dist_clean - dist_fast
                print(f"   - You traveled {diff:.2f} extra meters to breathe cleaner air.")
                
                cur.close()
                conn.close()
                return
            else:
                 print(f"   - Routes are identical (or very close). Trying again...")

    print("⚠️ NEUTRAL: Could not find a divergent path after multiple attempts.")
    print("   - All sampled pairs had identical fast vs clean paths.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    find_and_test_route()
