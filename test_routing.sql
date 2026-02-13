WITH trip AS (
    SELECT l1.source as start_id, l2.target as end_id
    FROM lines l1
    JOIN lines l2 ON l1.target = l2.source
    LIMIT 1
)
SELECT * FROM pgr_dijkstra(
    'SELECT ogc_fid AS id, source, target, ST_Length(geom) AS cost FROM lines',
    (SELECT start_id FROM trip),
    (SELECT end_id FROM trip),
    directed := false
);
