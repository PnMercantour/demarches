with flight as (
SELECT uuid::text, dossier_id, creation_date::text, dz_label, region FROM survol.flights WHERE uuid = %s
UNION
SELECT uuid::text, null, null,array(select survol.dz_label(unnest(dz))), ''::text as region FROM survol.flight_templates WHERE uuid = %s
)
select uuid, dossier_id, creation_date, dz_label, region from flight