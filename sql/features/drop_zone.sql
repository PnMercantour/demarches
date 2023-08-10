WITH dp AS(
    SELECT geom, label, id, is_temp FROM survol.drop_zones
),
features AS (
    SELECT
    json_build_object(
        'type', 'Feature',
        'properties', json_build_object(
            'id', id,
            'tooltip', label,
            'is_temp', is_temp
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