BEGIN;
CREATE ROLE booknest_identity_broker NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
GRANT USAGE ON SCHEMA booknest TO booknest_identity_broker;
-- This role is server-only and cannot read ratings, shelves, runs or source text.
GRANT SELECT(user_id,auth_issuer,auth_subject,display_name) ON booknest.app_users TO booknest_identity_broker;
GRANT INSERT(user_id,auth_issuer,auth_subject,display_name) ON booknest.app_users TO booknest_identity_broker;
CREATE POLICY broker_resolve ON booknest.app_users FOR SELECT TO booknest_identity_broker
    USING(auth_issuer=current_setting('booknest.auth_issuer',true) AND auth_subject=current_setting('booknest.auth_subject',true));
CREATE POLICY broker_provision ON booknest.app_users FOR INSERT TO booknest_identity_broker
    WITH CHECK(auth_issuer=current_setting('booknest.auth_issuer',true) AND auth_subject=current_setting('booknest.auth_subject',true));
INSERT INTO booknest.schema_migrations(version) VALUES(3);
COMMIT;
