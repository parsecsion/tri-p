from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
import time
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB CONFIG
DB_CONFIG = {
    "dbname": "karachi_routing",
    "user": "postgres",
    "password": "080907",
    "host": "localhost",
    "port": "5432"
}

class RouteRequest(BaseModel):
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    mode: str = "clean"  # 'clean' or 'fast'

@app.post("/route")
def get_route(req: RouteRequest):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Helper to find nearest node
        def find_nearest_node(lon, lat, major_roads_only=False):
            if major_roads_only:
                # Find nearest node on a major road
                # We join lines_vertices_pgr with lines to filter by highway type
                # Excluding 'tertiary' to reduce risk of disconnected islands
                query = """
                SELECT v.id, l.highway, ST_Distance(v.the_geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326)) as dist
                FROM lines_vertices_pgr v
                JOIN lines l ON (v.id = l.source OR v.id = l.target)
                WHERE l.highway IN ('motorway', 'trunk', 'primary', 'secondary', 'motorway_link', 'trunk_link', 'primary_link')
                ORDER BY v.the_geom <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326)
                LIMIT 1;
                """
                cur.execute(query, (lon, lat, lon, lat))
            else:
                # Standard Nearest Neighbor found in lines_vertices_pgr
                query = """
                SELECT id FROM lines_vertices_pgr 
                ORDER BY the_geom <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326) LIMIT 1;
                """
                cur.execute(query, (lon, lat))
            
            row = cur.fetchone()
            return row[0] if row else None

        # 1. Try Standard Routing first
        start_node = find_nearest_node(req.start_lon, req.start_lat)
        end_node = find_nearest_node(req.end_lon, req.end_lat)

        if not start_node or not end_node:
             raise HTTPException(status_code=404, detail="Start/End location not found in graph")

        # 2. Define Cost Column based on Mode
        current_hour = time.localtime().tm_hour
        
        if req.mode == "clean":
            cost_sql = f"pollution_cost * get_traffic_penalty({current_hour}, highway)"
        else:
            cost_sql = "length_m"

        # 3. Encapsulate Dijkstra in a function for retry
        def run_dijkstra(s_node, e_node):
            routing_query = f"""
            SELECT seq, node, edge, cost, agg_cost, ST_AsGeoJSON(l.geom) as geojson, l.highway, l.length_m
            FROM pgr_dijkstra(
                'SELECT ogc_fid as id, source, target, {cost_sql} as cost FROM lines',
                {s_node}, {e_node}, directed := false
            ) as r
            LEFT JOIN lines l ON r.edge = l.ogc_fid;
            """
            cur.execute(routing_query)
            return cur.fetchall()

        rows = run_dijkstra(start_node, end_node)
        
        # 4. Retry Logic: If no path, try snapping to MAJOR roads
        if not rows:
            print("DEBUG: Standard route failed. Retrying with Major Roads...")
            start_node_major = find_nearest_node(req.start_lon, req.start_lat, major_roads_only=True)
            end_node_major = find_nearest_node(req.end_lon, req.end_lat, major_roads_only=True)
            
            if start_node_major and end_node_major and (start_node_major != start_node or end_node_major != end_node):
                print(f"DEBUG: Retrying from {start_node_major} to {end_node_major}")
                rows = run_dijkstra(start_node_major, end_node_major)

        if not rows:
             print("DEBUG: No rows returned from Dijkstra (even after retry)")
             raise HTTPException(status_code=404, detail="No path found (try moving points closer to main roads)")

        # 5. Format GeoJSON for Frontend
        features = []
        total_dist = 0
        total_cost = 0
        
        for row in rows:
            # seq, node, edge, cost, agg_cost, geojson, highway, length
            if row[5]: # If geometry exists
                geom = json.loads(row[5])
                features.append({
                    "type": "Feature",
                    "geometry": geom,
                    "properties": {
                        "seq": row[0],
                        "cost": row[3],
                        "highway": row[6],
                        "length_m": row[7]
                    }
                })
                if row[7]:
                    total_dist += row[7]
            
            if row[4]:
                total_cost = max(total_cost, row[4]) # agg_cost is cumulative
                
        conn.close()
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "start_node": start_node,
                "end_node": end_node,
                "nodes_visited": len(rows), 
                "mode": req.mode,
                "total_distance_m": total_dist,
                "total_cost": total_cost,
                "traffic_hour": current_hour
            }
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
