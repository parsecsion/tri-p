-- Check node 87613
SELECT id, cnt, ST_AsText(the_geom) 
FROM lines_vertices_pgr 
WHERE id = 87613;

-- Check edges connected to 87613
SELECT ogc_fid, source, target, highway, name, ST_AsText(geom) 
FROM lines 
WHERE source = 87613 OR target = 87613;

-- Check node 56841
SELECT id, cnt, ST_AsText(the_geom) 
FROM lines_vertices_pgr 
WHERE id = 56841;

-- Check edges connected to 56841
SELECT ogc_fid, source, target, highway, name, ST_AsText(geom) 
FROM lines 
WHERE source = 56841 OR target = 56841;

-- Try Dijkstra between them with NO cost (just topology)
SELECT * FROM pgr_dijkstra(
    'SELECT ogc_fid as id, source, target, 1 as cost FROM lines',
    87613, 56841, directed := false
);
