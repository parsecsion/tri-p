CREATE OR REPLACE FUNCTION get_traffic_penalty(current_hour INT, road_type VARCHAR) 
RETURNS FLOAT AS $$
BEGIN
    -- RUSH HOUR (8-10 AM and 5-8 PM)
    IF (current_hour BETWEEN 8 AND 10) OR (current_hour BETWEEN 17 AND 20) THEN
        IF road_type IN ('trunk', 'motorway', 'primary', 'primary_link', 'trunk_link', 'motorway_link') THEN
            RETURN 3.0; -- 3x Penalty for highways during rush hour
        END IF;
    END IF;
    
    RETURN 1.0; -- No penalty otherwise
END;
$$ LANGUAGE plpgsql;
