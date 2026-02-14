-- Efficient Update Strategy for Real-Time Costs
-- 1. Identify active sensors with recent data
-- 2. Update lines based on proximity to these sensors
-- 3. Use ST_DWithin and spatial indexing for speed

WITH active_sensors AS (
    SELECT geom, pm25 
    FROM sensor_readings 
    -- For simulation, we just use all sensors. In prod: WHERE last_updated > NOW() - INTERVAL '1 hour'
)
UPDATE lines l
SET pollution_cost = length_m * (
    CASE 
        -- If road is within 500m of a VERY BAD sensor (>150 AQI/PM2.5), penalty is 10x
        WHEN EXISTS (
            SELECT 1 FROM active_sensors s 
            WHERE s.pm25 > 150 
            AND ST_DWithin(l.geom::geography, s.geom::geography, 500)
        ) THEN 10.0
        
        -- If road is within 1km of a BAD sensor (>100 AQI/PM2.5), penalty is 5x
        WHEN EXISTS (
            SELECT 1 FROM active_sensors s 
            WHERE s.pm25 > 100 
            AND ST_DWithin(l.geom::geography, s.geom::geography, 1000)
        ) THEN 5.0

        -- If road is within 2km of a MODERATE sensor (>50 AQI/PM2.5), penalty is 2x
        WHEN EXISTS (
            SELECT 1 FROM active_sensors s 
            WHERE s.pm25 > 50 
            AND ST_DWithin(l.geom::geography, s.geom::geography, 2000)
        ) THEN 2.0
        
        ELSE 1.0
    END
)
-- Only update rows that are within range of ANY sensor (Optimization)
WHERE EXISTS (
    SELECT 1 FROM active_sensors s 
    WHERE ST_DWithin(l.geom::geography, s.geom::geography, 2000)
);
