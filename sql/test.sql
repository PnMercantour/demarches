WITH dp AS(
    SELECT * FROM survol.c_drop_zone_dz
),
features AS (
    SELECT geom, id, localite,
    json_build_object(
        'type', 'Feature',
        'properties', json_build_object(
            'id', id,
            'tooltip', localite
        ),
        'geometry', st_asgeojson (st_transform (geom, 4326), 6)::json
    ) feature
FROM 
dp
)

SELECT json_build_object(
    'type', 'FeatureCollection',
    'features', json_agg(feature)
)::text geojson
FROM (
    SELECT feature
    FROM features
) f;