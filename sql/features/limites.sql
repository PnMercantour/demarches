WITH dp AS(
    SELECT * FROM limites.area WHERE name = 'coeur'
),
features AS (
    SELECT geom,
    json_build_object(
        'type', 'Feature',
        'properties', json_build_object(
            'tooltip', 'Coeur de parc'
        ),
        'geometry', st_asgeojson (st_transform (st_geometryN(geom,1), 4326), 6)::json
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