-- 1. Add the columns
ALTER TABLE lines ADD COLUMN IF NOT EXISTS length_m FLOAT;
ALTER TABLE lines ADD COLUMN IF NOT EXISTS pollution_cost FLOAT;

-- 2. Calculate true length in meters (Transform to EPSG:3857)
-- Using ogc_fid as the primary key
UPDATE lines 
SET length_m = ST_Length(ST_Transform(geom, 3857));

-- 3. Initialize pollution_cost to be the same as length (Baseline)
UPDATE lines SET pollution_cost = length_m;

-- 4. Apply Pollution Penalty Logic

-- PENALIZE: High Traffic / High Pollution Roads (Multiplier: 5.0)
UPDATE lines 
SET pollution_cost = length_m * 5.0 
WHERE highway IN ('motorway', 'motorway_link', 'trunk', 'trunk_link', 'primary', 'primary_link');

-- NEUTRAL: Moderate Roads (Multiplier: 1.5)
UPDATE lines 
SET pollution_cost = length_m * 1.5 
WHERE highway IN ('secondary', 'secondary_link', 'tertiary', 'tertiary_link');

-- REWARD: Residential & Living Streets (Multiplier: 1.0 - Baseline)
UPDATE lines 
SET pollution_cost = length_m * 1.0 
WHERE highway IN ('residential', 'living_street', 'unclassified', 'road');

-- BONUS: Clean Air Zones (Multiplier: 0.8)
UPDATE lines 
SET pollution_cost = length_m * 0.8 
WHERE highway IN ('pedestrian', 'path', 'cycleway', 'track', 'service');
