DROP TABLE IF EXISTS components;

-- 1. Create components table using pgr_connectedComponents
-- We just need connectivity, no cost.
CREATE TABLE components AS
SELECT * FROM pgr_connectedComponents(
    'SELECT ogc_fid as id, source, target FROM lines'
);

-- 2. Index it for speed
CREATE INDEX components_node_idx ON components(node);
CREATE INDEX components_component_idx ON components(component);

-- 3. Show largest components
SELECT component, count(*) 
FROM components 
GROUP BY component 
ORDER BY count(*) DESC 
LIMIT 10;
