with flight as (
    select geom, start_dz, end_dz from survol.flight_history where uuid = %s
)
INSERT INTO survol.flight_templates (geom, start_dz, end_dz) select geom, start_dz, end_dz from flight RETURNING uuid::text;
