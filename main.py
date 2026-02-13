from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import time
import json

app = FastAPI()

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

        # 1. Find Nearest Nodes to Lat/Lon (PostGIS Nearest Neighbor)
        # We use <-> operator for fast KNN from lines_vertices_pgr
        # We need to make sure lines_vertices_pgr has a geometry index on 'the_geom'
        node_query = """
        SELECT id FROM lines_vertices_pgr 
        ORDER BY the_geom <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326) LIMIT 1;
        """
        
        cur.execute(node_query, (req.start_lon, req.start_lat))
        start_node_row = cur.fetchone()
        if not start_node_row:
             raise HTTPException(status_code=404, detail="Start location not found in graph")
        start_node = start_node_row[0]
        
        cur.execute(node_query, (req.end_lon, req.end_lat))
        end_node_row = cur.fetchone()
        if not end_node_row:
             raise HTTPException(status_code=404, detail="End location not found in graph")
        end_node = end_node_row[0]

        # 2. Define Cost Column based on Mode
        # We use the SQL function get_traffic_penalty(current_hour, highway)
        current_hour = time.localtime().tm_hour
        
        if req.mode == "clean":
            # Dynamic Cost Function
            # Cost = length_m * Static_Pollution_Penalty * Traffic_Penalty
            # Static Penalty is already in 'pollution_cost' column? 
            # Wait, 'pollution_cost' in DB is length_m * static_penalty.
            # So we can just use pollution_cost * get_traffic_penalty(...)
            
            # Let's check if we updated pollution_cost in DB or if it's dynamic.
            # In Phase 1 user instruction: "UPDATE lines SET pollution_cost = length_m * 5.0 ..."
            # So 'pollution_cost' ALREADY includes the static road type penalty.
            
            # So Dynamic Cost = pollution_cost * get_traffic_penalty(hour, highway)
            
            cost_sql = f"""
                pollution_cost * get_traffic_penalty({current_hour}, highway)
            """
        else:
            # Simple Distance
            cost_sql = "length_m"

        # 3. Run Routing
        # We join with lines table to get geometry
        routing_query = f"""
        SELECT seq, node, edge, cost, agg_cost, ST_AsGeoJSON(l.geom) as geojson, l.highway, l.length_m
        FROM pgr_dijkstra(
            'SELECT ogc_fid as id, source, target, {cost_sql} as cost FROM lines',
            {start_node}, {end_node}, directed := false
        ) as r
        LEFT JOIN lines l ON r.edge = l.ogc_fid;
        """
        
        # print(f"Executing Query: {routing_query}") # Debug
        cur.execute(routing_query)
        rows = cur.fetchall()
        
        if not rows:
             raise HTTPException(status_code=404, detail="No path found")

        # 4. Format GeoJSON for Frontend
        features = []
        total_dist = 0
        total_cost = 0
        
        for row in rows:
            # seq, node, edge, cost, agg_cost, geojson, highway, length
            if row[5]: # If geometry exists (it might be null for the last node row where edge is -1)
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

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
