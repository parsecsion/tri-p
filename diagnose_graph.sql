-- Check if nodes exist and get their degree
SELECT id, cnt, the_geom 
FROM lines_vertices_pgr 
WHERE id IN (679346, 195051);

-- Check if they are part of the main graph (checking edges connected to them)
SELECT * FROM lines WHERE source IN (679346, 195051) OR target IN (679346, 195051);

-- Check total graph size
SELECT count(*) FROM lines;

-- Attempt a short route with simple length cost to rule out function issues
SELECT * FROM pgr_dijkstra(
    'SELECT ogc_fid as id, source, target, length_m as cost FROM lines',
    679346, 195051, directed := false
);
