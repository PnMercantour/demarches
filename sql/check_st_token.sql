SELECT EXISTS (
    SELECT 1
    FROM survol.st_token
    WHERE dossier_id = %s AND token = %s
) AS result;