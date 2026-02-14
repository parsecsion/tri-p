-- 1. Count Total Rows
SELECT count(*) as total_edges FROM lines;

-- 2. Breakdown by Highway Type
SELECT highway, count(*) 
FROM lines 
GROUP BY highway 
ORDER BY count(*) DESC;

-- 3. Check for NULL geometries or weird IDs
SELECT count(*) FROM lines WHERE geom IS NULL;

-- 4. Check Topology Table (lines_vertices_pgr)
SELECT count(*) as total_nodes FROM lines_vertices_pgr;

-- 5. Connectivity Diagnostic: Check disconnected subgraphs (approximated by component analysis if possible, or just checking degree)
-- Let's check nodes with degree=1 (dead ends) vs degree>1
SELECT cnt as degree, count(*) 
FROM lines_vertices_pgr 
GROUP BY cnt 
ORDER BY cnt 
LIMIT 10;
