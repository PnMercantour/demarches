WITH file AS (
    SELECT * FROM survol.dossier WHERE dossier_id = %s LIMIT 1
)
SELECT json_build_object(
        'id', dossier_id,
        'number', dossier_number,
        'state', state,
        'creation_date', creation_date,
        'last_carte', last_carte
    ) AS dossier
FROM file;
