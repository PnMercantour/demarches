with flight as (
SELECT uuid::text, dossier_id, creation_date::text,start_dz,end_dz FROM survol.flights WHERE uuid = %s
UNION
SELECT uuid::text, null, null, survol.dz_label(start_dz), survol.dz_label(end_dz) FROM survol.flight_templates WHERE uuid = %s
)
select uuid, dossier_id, creation_date, start_dz, end_dz from flight