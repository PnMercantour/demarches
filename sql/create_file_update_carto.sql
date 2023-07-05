WITH id AS (
    INSERT INTO survol.dossier (dossier_id,dossier_number, last_carte) VALUES (%s,%s,%s) RETURNING dossier_id
)
-- update carto
UPDATE survol.carte SET dossier_id = (SELECT dossier_id FROM id) WHERE uuid = %s;



