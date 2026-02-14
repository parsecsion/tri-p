-- FAST CHECK
-- 1. Check if 'highway' and 'pollution_cost' exist in 'lines'
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'lines' AND column_name IN ('highway', 'pollution_cost', 'length_m');

-- 2. Test get_traffic_penalty function
SELECT get_traffic_penalty(18, 'motorway') as penalty_rush_hour;
SELECT get_traffic_penalty(3, 'motorway') as penalty_night;

-- 3. Test the cost query directly on a single row
SELECT ogc_fid, source, target, pollution_cost * get_traffic_penalty(18, highway) as computed_cost 
FROM lines 
LIMIT 5;
