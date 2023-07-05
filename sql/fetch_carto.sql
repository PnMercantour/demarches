WITH attached_dossier AS (
SELECT dossier_id FROM survol.carte WHERE uuid = %s  LIMIT 1
),
carto AS (
    SELECT geom, uuid, creation_date, dossier_id
    FROM survol.carte
    WHERE dossier_id = (SELECT dossier_id FROM attached_dossier) ORDER BY creation_date DESC
),
geom AS (
    SELECT  
        json_build_object(
        'type', 'Feature',
        'properties', json_build_object(
            'id', uuid,
            'creation_date', creation_date,
            'dossier_id', dossier_id
        ),
        'geometry', st_asgeojson (st_transform (geom, 4326), 6)::json
    ) AS feature
    FROM
    carto
)

SELECT json_build_object(
    'type', 'FeatureCollection',
    'features', json_agg(feature)
)::text AS geojson
FROM(
    SELECT feature
    FROM geom
) AS f;
