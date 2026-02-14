import psycopg2
import time
import json

DB_CONFIG = {
    "dbname": "karachi_routing",
    "user": "postgres",
    "password": "080907",
    "host": "localhost",
    "port": "5432"
}

def test_routing():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 1. Mock Request Data (Coordinates from user request or similar)
        # Clifton to Gulshan coords (approx)
        start_lat, start_lon = 24.82, 67.03 
        end_lat, end_lon = 24.92, 67.09

        # 2. Find Start Node
        node_query = """
        SELECT id FROM lines_vertices_pgr 
        ORDER BY the_geom <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326) LIMIT 1;
        """
        cur.execute(node_query, (start_lon, start_lat))
        start_node = cur.fetchone()[0]
        print(f"Start Node: {start_node}")

        # 3. Find End Node
        cur.execute(node_query, (end_lon, end_lat))
        end_node = cur.fetchone()[0]
        print(f"End Node: {end_node}")

        # 4. Define Cost SQL
        current_hour = 20 # Force rush hour
        cost_sql = f"pollution_cost * get_traffic_penalty({current_hour}, highway)"
        
        print(f"Cost SQL: {cost_sql}")

        # 5. Run Routing Query
        routing_query = f"""
        SELECT seq, node, edge, cost, agg_cost, ST_AsGeoJSON(l.geom) as geojson, l.highway, l.length_m
        FROM pgr_dijkstra(
            'SELECT ogc_fid as id, source, target, {cost_sql} as cost FROM lines',
            {start_node}, {end_node}, directed := false
        ) as r
        LEFT JOIN lines l ON r.edge = l.ogc_fid;
        """
        
        print("Executing pgr_dijkstra...")
        cur.execute(routing_query)
        rows = cur.fetchall()
        print(f"Got {len(rows)} rows.")
        
        conn.close()
        print("✅ Success!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_routing()
