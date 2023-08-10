with flight as (
SELECT uuid::text, dossier_id, creation_date::text,NULL as start_dz,NULL as end_dz, dz_label FROM survol.flights WHERE uuid = %s
UNION
SELECT uuid::text, null, null, survol.dz_label(start_dz), survol.dz_label(end_dz),array(select survol.dz_label(unnest(dz))) FROM survol.flight_templates WHERE uuid = %s
)
select uuid, dossier_id, creation_date, start_dz, end_dz, dz_label from flight