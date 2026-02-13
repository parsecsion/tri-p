-- Find largest connected component to guarantee routability
BEGIN;

-- 1. Create components table (takes time)
CREATE TEMP TABLE IF NOT EXISTS graph_components AS
SELECT * FROM pgr_connectedComponents(
    'SELECT ogc_fid as id, source, target, length_m as cost, length_m as reverse_cost FROM lines WHERE source IS NOT NULL AND target IS NOT NULL'
);

-- 2. Find the largest component
CREATE TEMP TABLE IF NOT EXISTS largest_component AS
SELECT component, count(*) as cnt
FROM graph_components
GROUP BY component
ORDER BY count(*) DESC
LIMIT 1;

-- 3. Pick 50 random nodes from the largest component
SELECT node 
FROM graph_components 
WHERE component = (SELECT component FROM largest_component)
ORDER BY random()
LIMIT 50;

ROLLBACK;
