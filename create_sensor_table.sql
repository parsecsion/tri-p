CREATE TABLE IF NOT EXISTS sensor_readings (
    id SERIAL PRIMARY KEY,
    sensor_name VARCHAR(100),
    lat FLOAT,
    lon FLOAT,
    pm25 FLOAT, -- The killer pollutant
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Enable spatial queries on sensors
-- Check if column exists first to avoid error on rerun
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'sensor_readings' AND column_name = 'geom') THEN
        PERFORM AddGeometryColumn('sensor_readings', 'geom', 4326, 'POINT', 2);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_sensor_geom ON sensor_readings USING GIST(geom);
