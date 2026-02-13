Walkthrough: Ingesting OSM Data into PostGIS
We successfully ingested the Karachi OSM data into the karachi_routing database and built a routing topology. Due to OOM errors with osm2pgrouting, we adopted an alternative approach using ogr2ogr.

Approach Taken
Database Setup: Created karachi_routing with postgis and pgrouting extensions.
Data Conversion:
Attempted osm2pgrouting directly on PBF (failed).
Converted .osm.pbf to .osm (XML) using a custom Python script (
convert_pbf_to_xml_stream.py
).
Attempted osm2pgrouting on XML (failed with OOM).
Solution: Used ogr2ogr to convert .osm to a PostgreSQL dump (
.sql
), handling large data more efficiently.
Data Import: Imported the SQL dump into the database using psql.
Topology Creation:
pgr_createTopology failed due to missing function signature in pgrouting 4.0.0.
Solution: Implemented a manual topology creation script (
create_topology_manual.sql
) that:
Snapped geometries to a grid (0.00001 tolerance).
Created a lines_vertices_pgr table.
Populated source and target columns in the lines table.
Verification
We verified the ingestion and topology by running a sample pgr_dijkstra query on the graph.

Topology Stats
Edges: ~1.3 million (lines table)
Vertices: ~2.18 million (lines_vertices_pgr table)
Disconnected Edges: 0 (all edges have valid source/target)
Routing Test
Executed a query to find a path between two connected edges:

sql
WITH trip AS (
    SELECT l1.source as start_id, l2.target as end_id
    FROM lines l1
    JOIN lines l2 ON l1.target = l2.source
    LIMIT 1
)
SELECT * FROM pgr_dijkstra(
    'SELECT ogc_fid AS id, source, target, ST_Length(geom) AS cost FROM lines',
    (SELECT start_id FROM trip),
    (SELECT end_id FROM trip),
    directed := false
);
Result: Successfully returned a path with costs, confirming the graph is routable.

Key Files
convert_pbf_to_xml_stream.py
: Streaming converter for PBF to XML.
create_topology_manual.sql
: Manual topology creation logic.
test_routing.sql
: Verification query.