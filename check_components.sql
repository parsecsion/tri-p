-- Check Connected Components
-- This might take a few seconds
SELECT component, count(*) 
FROM pgr_connectedComponents(
    'SELECT ogc_fid as id, source, target, length_m as cost FROM lines'
)
GROUP BY component
ORDER BY count(*) DESC
LIMIT 10;
