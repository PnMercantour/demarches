-- DROP SCHEMA survol;

CREATE SCHEMA survol AUTHORIZATION postgres;

-- DROP TYPE survol."file_state";

CREATE TYPE survol."file_state" AS ENUM (
	'noneen_constructionen_instructionaccepterefusesans_suite');

-- DROP SEQUENCE survol.c_couloir_autorise_vol_libre_cav_id_seq;

CREATE SEQUENCE survol.c_couloir_autorise_vol_libre_cav_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 3
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE survol.c_drop_zone_dz_id_seq;

CREATE SEQUENCE survol.c_drop_zone_dz_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 127
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE survol.c_itineraire_survol_its_id_seq;

CREATE SEQUENCE survol.c_itineraire_survol_its_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 230
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE survol.t_calendrier_interdiction_survol_cis_id_seq;

CREATE SEQUENCE survol.t_calendrier_interdiction_survol_cis_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;-- survol.c_couloir_autorise_vol_libre_cav definition

-- Drop table

-- DROP TABLE survol.c_couloir_autorise_vol_libre_cav;

CREATE TABLE survol.c_couloir_autorise_vol_libre_cav (
	id bigserial NOT NULL,
	geom public.geometry(multipolygon, 2154) NULL,
	libelle varchar(254) NULL,
	CONSTRAINT c_couloir_autorise_vol_libre_cav_pkey PRIMARY KEY (id)
);
CREATE INDEX sidx_c_couloir_autorise_vol_libre_cav_geom ON survol.c_couloir_autorise_vol_libre_cav USING gist (geom);


-- survol.c_drop_zone_dz definition

-- Drop table

-- DROP TABLE survol.c_drop_zone_dz;

CREATE TABLE survol.c_drop_zone_dz (
	id serial4 NOT NULL,
	geom public.geometry(multipoint, 2154) NULL,
	localite varchar(254) NULL,
	type_dz varchar(50) NULL,
	dz_depart bool NOT NULL DEFAULT false,
	dz_arrivee bool NOT NULL DEFAULT false,
	details text NULL,
	CONSTRAINT c_drop_zone_dz_pkey PRIMARY KEY (id)
);
CREATE INDEX sidx_c_drop_zone_dz_geom ON survol.c_drop_zone_dz USING gist (geom);


-- survol.c_itineraire_survol_its definition

-- Drop table

-- DROP TABLE survol.c_itineraire_survol_its;

CREATE TABLE survol.c_itineraire_survol_its (
	id serial4 NOT NULL,
	geom public.geometry(multilinestring, 2154) NULL,
	dz_depart varchar(254) NULL,
	dz_arrivee varchar(254) NULL,
	type_survol varchar(50) NULL,
	recurrent bool NULL,
	prescription varchar(100) NULL,
	details text NULL,
	CONSTRAINT c_itineraire_survol_its_pkey PRIMARY KEY (id)
);
CREATE INDEX sidx_c_itineraire_survol_its_geom ON survol.c_itineraire_survol_its USING gist (geom);


-- survol.carte definition

-- Drop table

-- DROP TABLE survol.carte;

CREATE TABLE survol.carte (
	uuid uuid NOT NULL DEFAULT gen_random_uuid(),
	dossier_id varchar NULL,
	creation_date timestamp NOT NULL DEFAULT now()::timestamp without time zone,
	geom public.geometry(multilinestring, 4326) NOT NULL,
	start_dz uuid NULL,
	end_dz uuid NULL,
	is_temp bool NOT NULL DEFAULT true,
	CONSTRAINT carte_pk PRIMARY KEY (uuid)
);

-- Table Triggers

create trigger auto_find_dz after
insert
    on
    survol.carte for each row execute function survol.auto_find_dz();


-- survol.dossier definition

-- Drop table

-- DROP TABLE survol.dossier;

CREATE TABLE survol.dossier (
	dossier_id varchar NOT NULL,
	dossier_number int4 NOT NULL DEFAULT 0,
	CONSTRAINT dossier_pk PRIMARY KEY (dossier_id)
);


-- survol.drop_zones definition

-- Drop table

-- DROP TABLE survol.drop_zones;

CREATE TABLE survol.drop_zones (
	id uuid NOT NULL DEFAULT gen_random_uuid(),
	geom public.geometry NOT NULL,
	"label" varchar NULL,
	is_temp bool NOT NULL DEFAULT true,
	CONSTRAINT dz_history_pk PRIMARY KEY (id)
);


-- survol.flight_history definition

-- Drop table

-- DROP TABLE survol.flight_history;

CREATE TABLE survol.flight_history (
	uuid uuid NOT NULL DEFAULT gen_random_uuid(),
	dossier_id varchar NULL,
	creation_date timestamp NOT NULL DEFAULT now()::timestamp without time zone,
	geom public.geometry(multilinestring, 4326) NOT NULL,
	start_dz uuid NULL,
	end_dz uuid NULL,
	linked_template uuid NULL,
	raw_dz public."_geometry" NULL,
	dz _uuid NULL,
	region varchar NULL DEFAULT 'None'::character varying,
	CONSTRAINT flight_history_pk PRIMARY KEY (uuid)
);

-- Table Triggers

create trigger auto_dz after
insert
    on
    survol.flight_history for each row execute function survol.auto_find_dz();
create trigger fill_dz before
insert
    on
    survol.flight_history for each row execute function survol.auto_fill_dz();
create trigger auto_rg before
insert
    on
    survol.flight_history for each row execute function survol.auto_region();


-- survol.flight_templates definition

-- Drop table

-- DROP TABLE survol.flight_templates;

CREATE TABLE survol.flight_templates (
	uuid uuid NOT NULL DEFAULT gen_random_uuid(),
	geom public.geometry NOT NULL,
	start_dz uuid NULL,
	end_dz uuid NULL,
	dz _uuid NULL,
	CONSTRAINT flight_templates_pk PRIMARY KEY (uuid)
);


-- survol.qgis_projects definition

-- Drop table

-- DROP TABLE survol.qgis_projects;

CREATE TABLE survol.qgis_projects (
	"name" text NOT NULL,
	metadata jsonb NULL,
	"content" bytea NULL,
	CONSTRAINT qgis_projects_pkey PRIMARY KEY (name)
);


-- survol.st_token definition

-- Drop table

-- DROP TABLE survol.st_token;

CREATE TABLE survol.st_token (
	"token" uuid NOT NULL,
	dossier_id varchar NOT NULL,
	CONSTRAINT st_token_pk PRIMARY KEY (dossier_id)
);


-- survol.t_calendrier_interdiction_survol_cis definition

-- Drop table

-- DROP TABLE survol.t_calendrier_interdiction_survol_cis;

CREATE TABLE survol.t_calendrier_interdiction_survol_cis (
	id serial4 NOT NULL,
	activite text NULL,
	aigle text NULL,
	gypaete text NULL,
	vautour text NULL,
	tetralyre text NULL,
	lagopede text NULL,
	bouquetin text NULL,
	chamois text NULL,
	CONSTRAINT t_calendrier_interdiction_survol_cis_pkey PRIMARY KEY (id)
);


-- survol.c_couloir_autorise_vol_libre_cav foreign keys

-- survol.c_drop_zone_dz foreign keys

-- survol.c_itineraire_survol_its foreign keys

-- survol.carte foreign keys

-- survol.dossier foreign keys

-- survol.drop_zones foreign keys

-- survol.flight_history foreign keys

-- survol.flight_templates foreign keys

-- survol.qgis_projects foreign keys

-- survol.st_token foreign keys

-- survol.t_calendrier_interdiction_survol_cis foreign keys

-- survol.dz_history source

CREATE OR REPLACE VIEW survol.dz_history
AS SELECT drop_zones.id,
    drop_zones.geom,
    drop_zones.label
   FROM survol.drop_zones
  WHERE drop_zones.is_temp = false;


-- survol.flights source

CREATE OR REPLACE VIEW survol.flights
AS SELECT fh.uuid,
    fh.geom::geometry AS geom,
    fh.dossier_id,
    fh.creation_date,
    fh.linked_template,
    fh.dz,
        CASE
            WHEN fh.dz IS NULL THEN NULL::character varying[]
            ELSE ARRAY( SELECT survol.dz_label(dz_item.dz_item) AS dz_label
               FROM unnest(fh.dz) dz_item(dz_item))
        END AS dz_label,
    fh.region
   FROM survol.flight_history fh;


-- survol.v_aire_aigle_enjeu_repro_survol source

CREATE OR REPLACE VIEW survol.v_aire_aigle_enjeu_repro_survol
AS WITH repro AS (
         WITH cisval AS (
                 SELECT string_agg(cis.aigle, ','::text) AS periode
                   FROM survol.t_calendrier_interdiction_survol_cis cis
                )
         SELECT row_number() OVER () AS id,
            s.id_aire,
            cisval.periode,
            count(s.id_aire) AS nb_succes_5ans,
            max(s.annee) AS annee_dernier_succes,
            max(c.enjeu_repro) AS max_enjeu_repro,
            avg(c.enjeu_repro)::numeric(2,0) AS moy_enjeu_repro,
            st_buffer(a_1.geom, 500::double precision)::geometry(Polygon,2154) AS geom
           FROM cisval,
            bd_aigle_royal.c_aires a_1
             LEFT JOIN bd_aigle_royal.t_suivi_repro s ON a_1.id_aire = s.id_aire
             LEFT JOIN bd_aigle_royal.tr_codes_repro c ON s.id_code_repro = c.id_code_repro
          WHERE s.annee >= (to_char(now(), 'YYYY'::text)::integer - 5) AND c.enjeu_repro > 0 AND s.id_aire > 0
          GROUP BY s.id_aire, cisval.periode, a_1.geom, a_1.id_aire
        ), repro_agg AS (
         SELECT DISTINCT row_number() OVER (ORDER BY (st_makevalid((st_dump(st_union(repro_1.geom))).geom))) AS id,
            st_makevalid((st_dump(st_union(repro_1.geom))).geom)::geometry(Polygon,2154) AS geom
           FROM repro repro_1
        )
 SELECT DISTINCT row_number() OVER (ORDER BY (st_makevalid((st_dump(st_union(repro.geom))).geom))) AS id,
    array_agg(repro.id_aire) AS id_aires,
    repro.periode,
    sum(repro.nb_succes_5ans) AS nb_succes_5ans,
    max(repro.annee_dernier_succes) AS annee_dernier_succes,
    max(repro.max_enjeu_repro) AS max_enjeu_repro,
    avg(repro.moy_enjeu_repro::double precision) AS moy_enjeu_repro,
    repro_agg.geom
   FROM repro_agg
     JOIN repro ON st_intersects(repro.geom, repro_agg.geom)
  GROUP BY repro_agg.geom, repro.periode
  ORDER BY (max(repro.annee_dernier_succes)) DESC, (avg(repro.moy_enjeu_repro::double precision)) DESC;


-- survol.v_aires_sensibilite source

CREATE OR REPLACE VIEW survol.v_aires_sensibilite
AS WITH time_areas AS (
         SELECT v_aire_aigle_enjeu_repro_survol.geom,
            unnest(string_to_array(v_aire_aigle_enjeu_repro_survol.periode, ','::text)) AS mois
           FROM survol.v_aire_aigle_enjeu_repro_survol
        UNION
         SELECT v_dortoir_vautour_enjeu_survol.geom,
            unnest(string_to_array(v_dortoir_vautour_enjeu_survol.periode, ','::text)) AS mois
           FROM survol.v_dortoir_vautour_enjeu_survol
        UNION
         SELECT v_gypaete_barbu_zone_vigilance_survol.geom,
            unnest(string_to_array(v_gypaete_barbu_zone_vigilance_survol.periode, ','::text)) AS mois
           FROM survol.v_gypaete_barbu_zone_vigilance_survol
        UNION
         SELECT v_lago_repro_enjeu_survol.geom,
            unnest(string_to_array(v_lago_repro_enjeu_survol.periode, ','::text)) AS mois
           FROM survol.v_lago_repro_enjeu_survol
        UNION
         SELECT v_ongules_comptage_enjeu_survol.geom,
            unnest(string_to_array(v_ongules_comptage_enjeu_survol.periode, ','::text)) AS mois
           FROM survol.v_ongules_comptage_enjeu_survol
        UNION
         SELECT v_ongules_hivernage_enjeu_survol.geom,
            unnest(string_to_array(v_ongules_hivernage_enjeu_survol.periode, ','::text)) AS mois
           FROM survol.v_ongules_hivernage_enjeu_survol
        UNION
         SELECT v_ongules_misebas_survol.geom,
            unnest(string_to_array(v_ongules_misebas_survol.periode, ','::text)) AS mois
           FROM survol.v_ongules_misebas_survol
        UNION
         SELECT v_tly_hivernage_enjeu_survol.geom,
            unnest(string_to_array(v_tly_hivernage_enjeu_survol.periode, ','::text)) AS mois
           FROM survol.v_tly_hivernage_enjeu_survol
        UNION
         SELECT v_tly_repro_enjeu_survol.geom,
            unnest(string_to_array(v_tly_repro_enjeu_survol.periode, ','::text)) AS mois
           FROM survol.v_tly_repro_enjeu_survol
        )
 SELECT time_areas.mois,
    st_union(time_areas.geom) AS st_union
   FROM time_areas
  GROUP BY time_areas.mois
  ORDER BY time_areas.mois;


-- survol.v_dortoir_vautour_enjeu_survol source

CREATE OR REPLACE VIEW survol.v_dortoir_vautour_enjeu_survol
AS SELECT DISTINCT row_number() OVER (ORDER BY (st_makevalid((st_dump(st_union(st_buffer(vfd.geom, 500::double precision)))).geom))) AS id,
    periode.vautour AS periode,
    st_makevalid((st_dump(st_union(st_buffer(vfd.geom, 500::double precision)))).geom)::geometry(Polygon,2154) AS geom
   FROM faune.c_vautour_fauve_dortoir_vfd vfd,
    survol.t_calendrier_interdiction_survol_cis periode
  WHERE periode.activite = 'Estive'::text
  GROUP BY periode.vautour;


-- survol.v_gypaete_barbu_zone_vigilance_survol source

CREATE OR REPLACE VIEW survol.v_gypaete_barbu_zone_vigilance_survol
AS SELECT DISTINCT c_gypaete_barbu_zone_vigilance_gbz.id,
    periode.gypaete AS periode,
    c_gypaete_barbu_zone_vigilance_gbz.geom
   FROM faune.c_gypaete_barbu_zone_vigilance_gbz,
    ( SELECT cis.gypaete
           FROM survol.t_calendrier_interdiction_survol_cis cis
          WHERE cis.activite = 'Prospection territoriale'::text) periode;


-- survol.v_itineraire_survol_hors_zc source

CREATE OR REPLACE VIEW survol.v_itineraire_survol_hors_zc
AS SELECT its.id,
    its.dz_depart,
    its.dz_arrivee,
    its.type_survol,
    its.recurrent,
    its.prescription,
    false AS zone_coeur,
    its.details,
    st_makevalid(st_multi(st_difference(its.geom, c.geom)))::geometry(MultiLineString,2154) AS geom
   FROM survol.c_itineraire_survol_its its
     JOIN limregl.cr_pnm_coeur_topo c ON st_intersects(its.geom, c.geom) AND NOT st_within(its.geom, c.geom)
UNION
 SELECT its.id,
    its.dz_depart,
    its.dz_arrivee,
    its.type_survol,
    its.recurrent,
    its.prescription,
    false AS zone_coeur,
    its.details,
    st_makevalid(st_multi(st_difference(its.geom, c.geom)))::geometry(MultiLineString,2154) AS geom
   FROM survol.c_itineraire_survol_its its
     JOIN limregl.cr_pnm_coeur_topo c ON NOT st_within(its.geom, c.geom);


-- survol.v_itineraire_survol_zc source

CREATE OR REPLACE VIEW survol.v_itineraire_survol_zc
AS WITH itineraire_zc AS (
         SELECT its.id,
            its.dz_depart,
            its.dz_arrivee,
            its.type_survol,
            its.recurrent,
            its.prescription,
            true AS zone_coeur,
            its.details,
            st_makevalid(st_multi(st_intersection(its.geom, c.geom)))::geometry(MultiLineString,2154) AS geom
           FROM survol.c_itineraire_survol_its its
             LEFT JOIN limregl.cr_pnm_coeur_topo c ON st_intersects(its.geom, c.geom)
        )
 SELECT DISTINCT itineraire_zc.id,
    itineraire_zc.dz_depart,
    itineraire_zc.dz_arrivee,
    itineraire_zc.type_survol,
    itineraire_zc.recurrent,
    itineraire_zc.prescription,
    itineraire_zc.zone_coeur,
    itineraire_zc.details,
    itineraire_zc.geom
   FROM itineraire_zc
  WHERE itineraire_zc.geom IS NOT NULL;


-- survol.v_lago_repro_enjeu_survol source

CREATE OR REPLACE VIEW survol.v_lago_repro_enjeu_survol
AS SELECT row_number() OVER (ORDER BY (st_makevalid((st_dump(st_union(st_buffer(lsr.geom, 200::double precision)))).geom))) AS id,
    periode.lagopede AS periode,
    st_makevalid((st_dump(st_union(st_buffer(lsr.geom, 200::double precision)))).geom) AS geom
   FROM faune.c_lago_zone_repro_lzr lsr,
    ( SELECT cis.lagopede
           FROM survol.t_calendrier_interdiction_survol_cis cis
          WHERE cis.activite = 'Manifestations territoriales'::text OR cis.activite = 'Ponte - Couvaison'::text) periode
  GROUP BY periode.lagopede;


-- survol.v_ongules_comptage_enjeu_survol source

CREATE OR REPLACE VIEW survol.v_ongules_comptage_enjeu_survol
AS SELECT DISTINCT row_number() OVER (ORDER BY (st_makevalid((st_dump(st_union(ocs.geom))).geom))) AS id,
    periode.bouquetin AS periode,
    st_makevalid((st_dump(st_union(ocs.geom))).geom)::geometry(Polygon,2154) AS geom
   FROM faune.c_chamois_comptages_sites_ccs ocs,
    ( SELECT cis.bouquetin
           FROM survol.t_calendrier_interdiction_survol_cis cis
          WHERE cis.activite = 'Comptage'::text) periode
  GROUP BY periode.bouquetin;


-- survol.v_ongules_hivernage_enjeu_survol source

CREATE OR REPLACE VIEW survol.v_ongules_hivernage_enjeu_survol
AS WITH bzh_last_year AS (
         SELECT c_bouquetin_zone_hivernage_bzh.annee_donnee,
            c_bouquetin_zone_hivernage_bzh.echelle_saisie,
            c_bouquetin_zone_hivernage_bzh.source,
            c_bouquetin_zone_hivernage_bzh.date_donnee,
            c_bouquetin_zone_hivernage_bzh.geom,
            c_bouquetin_zone_hivernage_bzh.id
           FROM faune.c_bouquetin_zone_hivernage_bzh
          WHERE c_bouquetin_zone_hivernage_bzh.date_donnee = (( SELECT max(c_bouquetin_zone_hivernage_bzh_1.date_donnee) AS date_max
                   FROM faune.c_bouquetin_zone_hivernage_bzh c_bouquetin_zone_hivernage_bzh_1))
        )
 SELECT DISTINCT row_number() OVER (ORDER BY (st_makevalid((st_dump(st_union(st_buffer(bzh.geom, 200::double precision)))).geom))) AS id,
    periode.bouquetin AS periode,
    st_makevalid((st_dump(st_union(st_buffer(bzh.geom, 200::double precision)))).geom)::geometry(Polygon,2154) AS geom
   FROM bzh_last_year bzh,
    ( SELECT cis.bouquetin
           FROM survol.t_calendrier_interdiction_survol_cis cis
          WHERE cis.activite = 'Hivernage'::text) periode
  GROUP BY periode.bouquetin;


-- survol.v_ongules_misebas_survol source

CREATE OR REPLACE VIEW survol.v_ongules_misebas_survol
AS SELECT DISTINCT c_ongules_misebas_com.id,
    periode.bouquetin AS periode,
    c_ongules_misebas_com.geom
   FROM faune.c_ongules_misebas_com,
    ( SELECT cis.bouquetin
           FROM survol.t_calendrier_interdiction_survol_cis cis
          WHERE cis.activite = 'Mise bas'::text) periode
  GROUP BY c_ongules_misebas_com.id, periode.bouquetin;


-- survol.v_tly_hivernage_enjeu_survol source

CREATE OR REPLACE VIEW survol.v_tly_hivernage_enjeu_survol
AS SELECT DISTINCT row_number() OVER (ORDER BY (st_makevalid((st_dump(st_union(st_buffer(tzq.geom, 100::double precision)))).geom))) AS id,
    periode.tetralyre AS periode,
    st_makevalid((st_dump(st_union(st_buffer(tzq.geom, 100::double precision)))).geom)::geometry(Polygon,2154) AS geom
   FROM faune.c_tly_zone_quietude_tzq tzq,
    ( SELECT cis.tetralyre
           FROM survol.t_calendrier_interdiction_survol_cis cis
          WHERE cis.activite = 'Hivernage'::text) periode
  GROUP BY periode.tetralyre;


-- survol.v_tly_repro_enjeu_survol source

CREATE OR REPLACE VIEW survol.v_tly_repro_enjeu_survol
AS SELECT DISTINCT row_number() OVER (ORDER BY (st_makevalid((st_dump(st_union(st_buffer(tqc.geom, 100::double precision)))).geom))) AS id,
    periode.tetralyre AS periode,
    st_makevalid((st_dump(st_union(st_buffer(tqc.geom, 100::double precision)))).geom)::geometry(Polygon,2154) AS geom
   FROM faune.c_tly_quartier_comptage_chant_tqc tqc,
    ( SELECT cis.tetralyre
           FROM survol.t_calendrier_interdiction_survol_cis cis
          WHERE cis.activite = 'Manifestations territoriales'::text) periode
  GROUP BY periode.tetralyre;


-- survol.vm_itineraire_survol_hors_zc source

CREATE MATERIALIZED VIEW survol.vm_itineraire_survol_hors_zc
TABLESPACE pg_default
AS SELECT its.id,
    its.dz_depart,
    its.dz_arrivee,
    its.type_survol,
    its.recurrent,
    its.prescription,
    false AS zone_coeur,
    its.details,
    st_makevalid(st_multi(st_difference(its.geom, c.geom)))::geometry(MultiLineString,2154) AS geom
   FROM survol.c_itineraire_survol_its its
     JOIN limregl.cr_pnm_coeur_topo c ON st_intersects(its.geom, c.geom) AND NOT st_within(its.geom, c.geom)
UNION
 SELECT its.id,
    its.dz_depart,
    its.dz_arrivee,
    its.type_survol,
    its.recurrent,
    its.prescription,
    false AS zone_coeur,
    its.details,
    st_makevalid(st_multi(st_difference(its.geom, c.geom)))::geometry(MultiLineString,2154) AS geom
   FROM survol.c_itineraire_survol_its its
     JOIN limregl.cr_pnm_coeur_topo c ON NOT st_within(its.geom, c.geom)
WITH DATA;

-- View indexes:
CREATE UNIQUE INDEX idx_vm_itineraire_survol_hors_zc_id ON survol.vm_itineraire_survol_hors_zc USING btree (id);


-- survol.vm_itineraire_survol_zc source

CREATE MATERIALIZED VIEW survol.vm_itineraire_survol_zc
TABLESPACE pg_default
AS WITH itineraire_zc AS (
         SELECT its.id,
            its.dz_depart,
            its.dz_arrivee,
            its.type_survol,
            its.recurrent,
            its.prescription,
            true AS zone_coeur,
            its.details,
            st_makevalid(st_intersection(its.geom, c.geom)) AS geom
           FROM survol.c_itineraire_survol_its its
             JOIN limregl.cr_pnm_coeur_topo c ON st_intersects(its.geom, c.geom)
        )
 SELECT DISTINCT itineraire_zc.id,
    itineraire_zc.dz_depart,
    itineraire_zc.dz_arrivee,
    itineraire_zc.type_survol,
    itineraire_zc.recurrent,
    itineraire_zc.prescription,
    itineraire_zc.zone_coeur,
    itineraire_zc.details,
    itineraire_zc.geom
   FROM itineraire_zc
  WHERE itineraire_zc.geom IS NOT NULL
WITH DATA;

-- View indexes:
CREATE UNIQUE INDEX idx_vm_itineraire_survol_zc_id ON survol.vm_itineraire_survol_zc USING btree (id);


-- survol.vm_zones_sensibles source

CREATE MATERIALIZED VIEW survol.vm_zones_sensibles
TABLESPACE pg_default
AS WITH periodes_aigle AS (
         WITH aigle AS (
                 SELECT st_buffer(c_aires.geom, 500::double precision, 'quad_segs=2'::text) AS geom
                   FROM bd_aigle_royal.c_aires
                     LEFT JOIN bd_aigle_royal.t_suivi_repro suivi USING (id_aire)
                     JOIN bd_aigle_royal.tr_codes_repro tcr USING (id_code_repro)
                  WHERE suivi.annee > 2012 AND tcr.enjeu_repro > 0
                  GROUP BY c_aires.id_aire
                ), periode AS (
                 SELECT DISTINCT unnest(string_to_array(cis.aigle, ','::text)) AS mois
                   FROM survol.t_calendrier_interdiction_survol_cis cis
                  WHERE cis.activite <> 'Emancipation'::text
                )
         SELECT aigle.geom,
            periode.mois
           FROM aigle,
            periode
        ), periodes_vautour AS (
         WITH vautour AS (
                 SELECT st_buffer(c_vautour_fauve_dortoir_vfd.geom, 500::double precision, 'quad_segs=2'::text) AS geom
                   FROM faune.c_vautour_fauve_dortoir_vfd
                ), periode AS (
                 SELECT DISTINCT unnest(string_to_array(cis.vautour, ','::text)) AS mois
                   FROM survol.t_calendrier_interdiction_survol_cis cis
                  WHERE cis.activite = 'Estive'::text
                )
         SELECT vautour.geom,
            periode.mois
           FROM vautour,
            periode
        ), periodes_gypaete AS (
         WITH gypaete AS (
                 SELECT c_zsm_gypaete_barbu_zgb.geom
                   FROM faune.c_zsm_gypaete_barbu_zgb
                  WHERE c_zsm_gypaete_barbu_zgb.active
                ), periode AS (
                 SELECT DISTINCT unnest(string_to_array(cis.gypaete, ','::text)) AS mois
                   FROM survol.t_calendrier_interdiction_survol_cis cis
                )
         SELECT gypaete.geom,
            periode.mois
           FROM gypaete,
            periode
        ), periodes_lagopede AS (
         WITH lagopede AS (
                 SELECT c_lago_zone_repro_lzr.geom
                   FROM faune.c_lago_zone_repro_lzr
                ), periode AS (
                 SELECT DISTINCT unnest(string_to_array(cis.lagopede, ','::text)) AS mois
                   FROM survol.t_calendrier_interdiction_survol_cis cis
                  WHERE cis.activite = ANY (ARRAY['Manifestations territoriales'::text, 'Ponte - Couvaison'::text, 'Elevage jeune'::text])
                )
         SELECT lagopede.geom,
            periode.mois
           FROM lagopede,
            periode
        ), periodes_bouquetin_hivernage AS (
         WITH bouquetin AS (
                 SELECT c_bouquetin_zone_hivernage_bzh.geom
                   FROM faune.c_bouquetin_zone_hivernage_bzh
                  WHERE c_bouquetin_zone_hivernage_bzh.annee_donnee >= 2017
                ), periode AS (
                 SELECT DISTINCT unnest(string_to_array(cis.bouquetin, ','::text)) AS mois
                   FROM survol.t_calendrier_interdiction_survol_cis cis
                  WHERE cis.activite = 'Hivernage'::text
                )
         SELECT bouquetin.geom,
            periode.mois
           FROM bouquetin,
            periode
        ), periodes_bouquetin_misebas AS (
         WITH bouquetin AS (
                 SELECT c_ongules_misebas_com.geom
                   FROM faune.c_ongules_misebas_com
                  WHERE c_ongules_misebas_com.enjeux::text ~~ '%bouquetin%'::text
                ), periode AS (
                 SELECT DISTINCT unnest(string_to_array(cis.bouquetin, ','::text)) AS mois
                   FROM survol.t_calendrier_interdiction_survol_cis cis
                  WHERE cis.activite = 'Mise bas'::text
                )
         SELECT bouquetin.geom,
            periode.mois
           FROM bouquetin,
            periode
        ), periodes_chamois_misebas AS (
         WITH chamois AS (
                 SELECT c_ongules_misebas_com.geom
                   FROM faune.c_ongules_misebas_com
                  WHERE c_ongules_misebas_com.enjeux::text ~~ '%chamois%'::text
                ), periode AS (
                 SELECT DISTINCT unnest(string_to_array(cis.chamois, ','::text)) AS mois
                   FROM survol.t_calendrier_interdiction_survol_cis cis
                  WHERE cis.activite = 'Mise bas'::text
                )
         SELECT chamois.geom,
            periode.mois
           FROM chamois,
            periode
        ), periodes_tetralyre_hivernage AS (
         WITH tetralyre AS (
                 SELECT st_buffer(c_tly_zone_quietude_tzq.geom, 100::double precision, 'quad_segs=2'::text) AS geom
                   FROM faune.c_tly_zone_quietude_tzq
                ), periode AS (
                 SELECT DISTINCT unnest(string_to_array(cis.tetralyre, ','::text)) AS mois
                   FROM survol.t_calendrier_interdiction_survol_cis cis
                  WHERE cis.activite = 'Hivernage'::text
                )
         SELECT tetralyre.geom,
            periode.mois
           FROM tetralyre,
            periode
        ), periodes_tetralyre_repro AS (
         WITH tetralyre AS (
                 SELECT st_buffer(c_tly_quartier_comptage_chant_tqc.geom, 100::double precision, 'quad_segs=2'::text) AS geom
                   FROM faune.c_tly_quartier_comptage_chant_tqc
                ), periode AS (
                 SELECT DISTINCT unnest(string_to_array(cis.tetralyre, ','::text)) AS mois
                   FROM survol.t_calendrier_interdiction_survol_cis cis
                  WHERE cis.activite = 'Manifestations territoriales'::text
                )
         SELECT tetralyre.geom,
            periode.mois
           FROM tetralyre,
            periode
        ), toutes_especes AS (
         SELECT periodes_aigle.geom,
            periodes_aigle.mois
           FROM periodes_aigle
        UNION
         SELECT periodes_vautour.geom,
            periodes_vautour.mois
           FROM periodes_vautour
        UNION
         SELECT periodes_gypaete.geom,
            periodes_gypaete.mois
           FROM periodes_gypaete
        UNION
         SELECT periodes_lagopede.geom,
            periodes_lagopede.mois
           FROM periodes_lagopede
        UNION
         SELECT periodes_bouquetin_hivernage.geom,
            periodes_bouquetin_hivernage.mois
           FROM periodes_bouquetin_hivernage
        UNION
         SELECT periodes_bouquetin_misebas.geom,
            periodes_bouquetin_misebas.mois
           FROM periodes_bouquetin_misebas
        UNION
         SELECT periodes_chamois_misebas.geom,
            periodes_chamois_misebas.mois
           FROM periodes_chamois_misebas
        UNION
         SELECT periodes_tetralyre_hivernage.geom,
            periodes_tetralyre_hivernage.mois
           FROM periodes_tetralyre_hivernage
        UNION
         SELECT periodes_tetralyre_repro.geom,
            periodes_tetralyre_repro.mois
           FROM periodes_tetralyre_repro
        )
 SELECT toutes_especes.mois::integer AS id,
    toutes_especes.mois,
    st_simplifypreservetopology(st_union(toutes_especes.geom), 50::double precision) AS geom
   FROM toutes_especes
  GROUP BY toutes_especes.mois
  ORDER BY toutes_especes.mois
WITH DATA;

-- View indexes:
CREATE UNIQUE INDEX vm_zones_sensibles_id_idx ON survol.vm_zones_sensibles USING btree (id);


-- survol.zone_sensible_geojson source

CREATE OR REPLACE VIEW survol.zone_sensible_geojson
AS WITH zs AS (
         SELECT zones_sensibles.mois,
            zones_sensibles.geom
           FROM survol.zones_sensibles
        ), features AS (
         SELECT zs.geom,
            json_build_object('type', 'Feature', 'properties', json_build_object('mois', zs.mois, 'tooltip', zs.mois), 'geometry', st_asgeojson(st_transform(zs.geom, 4326), 6)::json) AS feature
           FROM zs
        )
 SELECT json_build_object('type', 'FeatureCollection', 'features', jsonb_agg(f.feature))::text AS geojson
   FROM ( SELECT features.feature
           FROM features) f;


-- survol.zones_sensibles source

CREATE OR REPLACE VIEW survol.zones_sensibles
AS WITH periodes_aigle AS (
         WITH aigle AS (
                 SELECT st_buffer(c_aires.geom, 500::double precision) AS geom
                   FROM bd_aigle_royal.c_aires
                     LEFT JOIN bd_aigle_royal.t_suivi_repro suivi USING (id_aire)
                     JOIN bd_aigle_royal.tr_codes_repro tcr USING (id_code_repro)
                  WHERE suivi.annee > 2012 AND tcr.enjeu_repro > 0
                  GROUP BY c_aires.id_aire
                ), periode AS (
                 SELECT DISTINCT unnest(string_to_array(cis.aigle, ','::text)) AS mois
                   FROM survol.t_calendrier_interdiction_survol_cis cis
                )
         SELECT aigle.geom,
            periode.mois
           FROM aigle,
            periode
        ), periodes_vautour AS (
         WITH vautour AS (
                 SELECT st_buffer(c_vautour_fauve_dortoir_vfd.geom, 500::double precision) AS geom
                   FROM faune.c_vautour_fauve_dortoir_vfd
                ), periode AS (
                 SELECT DISTINCT unnest(string_to_array(cis.vautour, ','::text)) AS mois
                   FROM survol.t_calendrier_interdiction_survol_cis cis
                  WHERE cis.activite = 'Estive'::text
                )
         SELECT vautour.geom,
            periode.mois
           FROM vautour,
            periode
        ), periodes_gypaete AS (
         WITH gypaete AS (
                 SELECT c_gypaete_barbu_zone_vigilance_gbz.geom
                   FROM faune.c_gypaete_barbu_zone_vigilance_gbz
                ), periode AS (
                 SELECT DISTINCT unnest(string_to_array(cis.gypaete, ','::text)) AS mois
                   FROM survol.t_calendrier_interdiction_survol_cis cis
                  WHERE cis.activite = 'Prospection territoriale'::text
                )
         SELECT gypaete.geom,
            periode.mois
           FROM gypaete,
            periode
        ), periodes_lagopede AS (
         WITH lagopede AS (
                 SELECT c_lago_zone_repro_lzr.geom
                   FROM faune.c_lago_zone_repro_lzr
                ), periode AS (
                 SELECT DISTINCT unnest(string_to_array(cis.lagopede, ','::text)) AS mois
                   FROM survol.t_calendrier_interdiction_survol_cis cis
                  WHERE cis.activite = ANY (ARRAY['Manifestations territoriales'::text, 'Ponte - Couvaison'::text])
                )
         SELECT lagopede.geom,
            periode.mois
           FROM lagopede,
            periode
        ), periodes_bouquetin_hivernage AS (
         WITH bouquetin AS (
                 SELECT c_bouquetin_zone_hivernage_bzh.geom
                   FROM faune.c_bouquetin_zone_hivernage_bzh
                  WHERE c_bouquetin_zone_hivernage_bzh.annee_donnee >= 2017
                ), periode AS (
                 SELECT DISTINCT unnest(string_to_array(cis.bouquetin, ','::text)) AS mois
                   FROM survol.t_calendrier_interdiction_survol_cis cis
                  WHERE cis.activite = 'Hivernage'::text
                )
         SELECT bouquetin.geom,
            periode.mois
           FROM bouquetin,
            periode
        ), periodes_bouquetin_misebas AS (
         WITH bouquetin AS (
                 SELECT c_ongules_misebas_com.geom
                   FROM faune.c_ongules_misebas_com
                  WHERE c_ongules_misebas_com.enjeux::text ~~ '%bouquetin%'::text
                ), periode AS (
                 SELECT DISTINCT unnest(string_to_array(cis.bouquetin, ','::text)) AS mois
                   FROM survol.t_calendrier_interdiction_survol_cis cis
                  WHERE cis.activite = 'Mise bas'::text
                )
         SELECT bouquetin.geom,
            periode.mois
           FROM bouquetin,
            periode
        ), periodes_chamois_misebas AS (
         WITH chamois AS (
                 SELECT c_ongules_misebas_com.geom
                   FROM faune.c_ongules_misebas_com
                  WHERE c_ongules_misebas_com.enjeux::text ~~ '%chamois%'::text
                ), periode AS (
                 SELECT DISTINCT unnest(string_to_array(cis.chamois, ','::text)) AS mois
                   FROM survol.t_calendrier_interdiction_survol_cis cis
                  WHERE cis.activite = 'Mise bas'::text
                )
         SELECT chamois.geom,
            periode.mois
           FROM chamois,
            periode
        ), periodes_tetralyre_hivernage AS (
         WITH tetralyre AS (
                 SELECT st_buffer(c_tly_zone_quietude_tzq.geom, 100::double precision) AS geom
                   FROM faune.c_tly_zone_quietude_tzq
                ), periode AS (
                 SELECT DISTINCT unnest(string_to_array(cis.tetralyre, ','::text)) AS mois
                   FROM survol.t_calendrier_interdiction_survol_cis cis
                  WHERE cis.activite = 'Hivernage'::text
                )
         SELECT tetralyre.geom,
            periode.mois
           FROM tetralyre,
            periode
        ), periodes_tetralyre_repro AS (
         WITH tetralyre AS (
                 SELECT st_buffer(c_tly_quartier_comptage_chant_tqc.geom, 100::double precision) AS geom
                   FROM faune.c_tly_quartier_comptage_chant_tqc
                ), periode AS (
                 SELECT DISTINCT unnest(string_to_array(cis.tetralyre, ','::text)) AS mois
                   FROM survol.t_calendrier_interdiction_survol_cis cis
                  WHERE cis.activite = 'Manifestations territoriales'::text
                )
         SELECT tetralyre.geom,
            periode.mois
           FROM tetralyre,
            periode
        ), toutes_especes AS (
         SELECT periodes_aigle.geom,
            periodes_aigle.mois
           FROM periodes_aigle
        UNION
         SELECT periodes_vautour.geom,
            periodes_vautour.mois
           FROM periodes_vautour
        UNION
         SELECT periodes_gypaete.geom,
            periodes_gypaete.mois
           FROM periodes_gypaete
        UNION
         SELECT periodes_lagopede.geom,
            periodes_lagopede.mois
           FROM periodes_lagopede
        UNION
         SELECT periodes_bouquetin_hivernage.geom,
            periodes_bouquetin_hivernage.mois
           FROM periodes_bouquetin_hivernage
        UNION
         SELECT periodes_bouquetin_misebas.geom,
            periodes_bouquetin_misebas.mois
           FROM periodes_bouquetin_misebas
        UNION
         SELECT periodes_chamois_misebas.geom,
            periodes_chamois_misebas.mois
           FROM periodes_chamois_misebas
        UNION
         SELECT periodes_tetralyre_hivernage.geom,
            periodes_tetralyre_hivernage.mois
           FROM periodes_tetralyre_hivernage
        UNION
         SELECT periodes_tetralyre_repro.geom,
            periodes_tetralyre_repro.mois
           FROM periodes_tetralyre_repro
        )
 SELECT toutes_especes.mois,
    st_union(toutes_especes.geom) AS geom
   FROM toutes_especes
  GROUP BY toutes_especes.mois
  ORDER BY toutes_especes.mois;



CREATE OR REPLACE FUNCTION survol.auto_fill_dz()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
	declare 
		past_dz uuid[];
	BEGIN
		if new.dz is null then 
			select dz into past_dz
			from survol.flight_history fh 
			where dossier_id = new.dossier_id
			order by creation_date desc
			limit 1;
		
			new.dz := past_dz;
		end if;
		return new;
	END;
$function$
;

CREATE OR REPLACE FUNCTION survol.auto_find_dz()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE
    dz_list uuid[];
begin
	if new.raw_dz is not null then
	SELECT array_agg(survol.get_nearest_dz(dz_geom, true))
    FROM unnest(new.raw_dz) AS dz_geom
    INTO dz_list;

    UPDATE survol.flight_history
    SET dz = dz_list
    WHERE uuid = new.uuid;
   
   	end if ;

    RETURN NEW;
END;
$function$
;

CREATE OR REPLACE FUNCTION survol.auto_region()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
	declare 
	rg varchar;
	BEGIN
		select string_agg(regions,':' order by regions) into rg  from survol.get_region(new.geom) as regions;
		new.region := rg;
		return new;
	END;
$function$
;

CREATE OR REPLACE FUNCTION survol.build_flight_json(uuid_param uuid)
 RETURNS json
 LANGUAGE plpgsql
AS $function$
	declare 
		returned_value json;
	begin
		with flight as (
			select geom, false as is_template, uuid, creation_date from survol.flights where uuid = uuid_param
			union
			select geom, true as is_template, uuid, null as creation_date from survol.flight_templates where uuid = uuid_param
		)
		select json_build_object(
	        'type', 'Feature',
	        'properties', json_build_object(
	            'is_template', is_template,
	            'id', uuid,
	            'creation_date', creation_date
	        ),
	        'geometry', st_asgeojson (geom, 6)::json
	    ) into returned_value from flight;
	   return returned_value;
	END;
$function$
;

CREATE OR REPLACE FUNCTION survol.build_map_json(uuid_param uuid, min_month integer, max_month integer)
 RETURNS TABLE(flight json)
 LANGUAGE plpgsql
AS $function$
begin 
	return query
	with flight_obj as(
		select f.geom, f.dz from survol.flight_history f where uuid=uuid_param
	),
	limites_obj as(
		select st_transform(a.geom,4326) as geom from limites.area a where name = 'coeur'
	),
	segments as (
		select st_intersection(f.geom, l.geom) as geom, 'red' as color from flight_obj f, limites_obj l
		union
		select ST_difference(f.geom, st_intersection(f.geom, l.geom)), 'green' as geom from flight_obj f, limites_obj l
	),
	drop_zone as (
		select dz.geom, 'green' as color from survol.drop_zones dz, flight_obj f where id = f.dz[1]
		union
		select dz.geom, 'red' as color from survol.drop_zones dz, flight_obj f where id = ANY(ARRAY(SELECT UNNEST(f.dz) OFFSET 1))
	),
	zs AS (
     SELECT zones_sensibles.mois,
        zones_sensibles.geom
       FROM survol.zones_sensibles
       where mois::int >= min_month and mois::int <= max_month
    ), 
    zs_feature AS (
     SELECT
        json_build_object('type', 'Feature',
	        'properties', json_build_object(
	         	'color', 'red'
	        ),
	        'geometry', st_asgeojson(st_transform(zs.geom, 4326), 6)::json) AS feature
       FROM zs
    ),
	flight_feature as (
		select json_build_object(
	        'type', 'Feature',
	        'properties', json_build_object(
	            'color', color
	        ),
	        'geometry', st_asgeojson (geom, 6)::json
	    ) as feature
	    from segments
	),
	dz_feature as (
		select  json_build_object(
	        'type', 'Feature',
	        'properties', json_build_object(
	            'color', color
	        ),
	        'geometry', st_asgeojson (geom, 6)::json
	    ) as feature
	    from drop_zone
	),
	limites_feature as (
		select json_build_object(
	        'type', 'Feature',
	        'properties', json_build_object(
	            'color', 'red'
	        ),
	        'geometry', st_asgeojson (geom, 6)::json
	    ) as feature
	    from limites_obj
	)
	
	select 
		json_build_object(
	    'type', 'FeatureCollection',
	    'features', json_agg(f.feature)
		)
	from
		flight_feature as f
	union all select
			json_build_object(
	    'type', 'FeatureCollection',
	    'features', json_agg(dz.feature)
		)
	from
		dz_feature as dz
	union all select
		json_build_object(
	    'type', 'FeatureCollection',
	    'features', json_agg(l.feature)
		) 
	from
		limites_feature l
	union all select
		json_build_object(
	    'type', 'FeatureCollection',
	    'features', json_agg(zs.feature)
		) 
	from
		zs_feature zs;

end;


$function$
;

CREATE OR REPLACE FUNCTION survol.clear_orphean_flight()
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
    DECLARE
        rows_deleted int4;
    BEGIN
        -- Delete rows with NULL dossier_id and get the count of deleted rows
        DELETE FROM survol.flight_history WHERE dossier_id IS null;
        GET DIAGNOSTICS rows_deleted = ROW_COUNT;

        -- Return the number of deleted rows
        RETURN rows_deleted;
    END;
$function$
;

CREATE OR REPLACE FUNCTION survol.dz_label(uuid_param uuid)
 RETURNS character varying
 LANGUAGE plpgsql
AS $function$
	declare 
		return_value varchar;
	BEGIN
		select label into return_value from survol.drop_zones where id = uuid_param;
		return return_value;
	END;
$function$
;

CREATE OR REPLACE FUNCTION survol.get_flight_history(uuid_param uuid)
 RETURNS uuid[]
 LANGUAGE plpgsql
AS $function$
declare 
	return_value uuid[];
BEGIN
	select distinct array_agg(ft.uuid::text)
	into return_value
	from survol.flight_templates ft 
	join survol.flight_history fh on array[fh.dz] && ft.dz
	where(
		select count(*)
		from unnest(fh.dz) as dz_in_fh
		join unnest(ft.dz) as dz_in_ft on dz_in_fh = dz_in_ft
		where fh.uuid = uuid_param 
	) >= 2 ;
	return return_value;
END;
$function$
;

CREATE OR REPLACE FUNCTION survol.get_nearest_dz(point geometry)
 RETURNS uuid
 LANGUAGE plpgsql
AS $function$
	declare 
		trigger_box geometry;
	
		returned uuid;
	
	begin
		select st_buffer(point, 0.01) into trigger_box;
		select id into returned  as dist from survol.drop_zones where trigger_box && geom order by st_distance(geom, point) asc limit 1;
		IF returned IS NULL THEN
	        INSERT INTO survol.drop_zones (geom, label) values (point, 'NEW DROPZONE') returning id as new_dz_uuid into returned;
	    END IF;
		return returned;
	end
	
$function$
;

CREATE OR REPLACE FUNCTION survol.get_nearest_dz(point geometry, force_create boolean DEFAULT true)
 RETURNS uuid
 LANGUAGE plpgsql
AS $function$
	declare 
		trigger_box geometry;
	
		returned uuid;
	
	begin
		select st_buffer(point, 0.01) into trigger_box;
		select id into returned  as dist from survol.drop_zones where trigger_box && geom order by st_distance(geom, point) asc limit 1;
		IF returned IS null and force_create = true THEN
	        INSERT INTO survol.drop_zones (geom, label) values (point, 'NEW DROPZONE') returning id as new_dz_uuid into returned;
	    END IF;
		return returned;
	end
	
$function$
;

CREATE OR REPLACE FUNCTION survol.get_nearest_dz_from_line(linestring geometry)
 RETURNS uuid[]
 LANGUAGE plpgsql
AS $function$
	declare 
		final_result uuid[];
	begin
		with points as (
		select (dp).geom from (
			select st_dumppoints(linestring) as dp
		) as point
		),
		dz as (
		select distinct survol.get_nearest_dz(geom, false) as uuid from points
		)
		select array_agg(uuid) into final_result from dz where uuid is not null;
		return final_result;
	END;
$function$
;

CREATE OR REPLACE FUNCTION survol.get_region(geom_param geometry)
 RETURNS TABLE(region character varying)
 LANGUAGE plpgsql
AS $function$

	begin
		return query
		with regions as (select st_setsrid(st_transform(geom,4326),4326) as geom, name from limites.area where id_type = 2)
		select regions.name 
		from regions
		where ST_Intersects(regions.geom, geom_param);
	END;
$function$
;

CREATE OR REPLACE FUNCTION survol.last_flight(uuid_param uuid)
 RETURNS uuid
 LANGUAGE plpgsql
AS $function$
DECLARE
    tmp_dossier_id varchar;
    last_uuid UUID;
BEGIN
    select dossier_id into tmp_dossier_id
    from survol.flight_history
    where uuid = uuid_param;
    
    if tmp_dossier_id is null then 
    	return uuid_param;
    
    else 
		select uuid into last_uuid
		from survol.flight_history fh 
		where dossier_id = tmp_dossier_id
		order by creation_date desc
		limit 1;
		return last_uuid;
	end if;
END;
$function$
;
