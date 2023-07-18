SELECT EXISTS (
    SELECT 1
    FROM survol.st_token
    WHERE dossier_id = %s
) AS result;