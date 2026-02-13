BEGIN;

ALTER TABLE lines ADD COLUMN IF NOT EXISTS source integer;
ALTER TABLE lines ADD COLUMN IF NOT EXISTS target integer;

DROP TABLE IF EXISTS lines_vertices_pgr;
CREATE TABLE lines_vertices_pgr (
    id SERIAL PRIMARY KEY,
    cnt integer,
    chk integer,
    ein integer,
    eout integer,
    the_geom geometry(Point, 4326)
);

CREATE INDEX lines_vertices_pgr_geom_idx ON lines_vertices_pgr USING GIST (the_geom);

-- Insert unique vertices (snapped)
INSERT INTO lines_vertices_pgr (the_geom, cnt, chk, ein, eout)
SELECT DISTINCT ST_SnapToGrid(pt, 0.00001), 0, 0, 0, 0
FROM (
    SELECT ST_StartPoint(geom) AS pt FROM lines WHERE geom IS NOT NULL
    UNION ALL
    SELECT ST_EndPoint(geom) AS pt FROM lines WHERE geom IS NOT NULL
) AS points;

ANALYZE lines_vertices_pgr;

-- Update source
UPDATE lines l
SET source = v.id
FROM lines_vertices_pgr v
WHERE ST_SnapToGrid(ST_StartPoint(l.geom), 0.00001) = v.the_geom;

-- Update target
UPDATE lines l
SET target = v.id
FROM lines_vertices_pgr v
WHERE ST_SnapToGrid(ST_EndPoint(l.geom), 0.00001) = v.the_geom;

CREATE INDEX IF NOT EXISTS lines_source_idx ON lines(source);
CREATE INDEX IF NOT EXISTS lines_target_idx ON lines(target);

COMMIT;
