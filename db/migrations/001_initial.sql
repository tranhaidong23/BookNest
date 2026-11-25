BEGIN;
CREATE SCHEMA booknest;
REVOKE ALL ON SCHEMA booknest FROM PUBLIC;

-- Group roles only: credentials/login provisioning is deliberately separate.
CREATE ROLE booknest_runtime NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
CREATE ROLE booknest_local_reviewer NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
GRANT USAGE ON SCHEMA booknest TO booknest_runtime,booknest_local_reviewer;

CREATE TABLE booknest.schema_migrations (
    version integer PRIMARY KEY,
    applied_at timestamptz NOT NULL DEFAULT now()
);
INSERT INTO booknest.schema_migrations(version) VALUES(1);

CREATE TABLE booknest.books (
    book_id integer PRIMARY KEY CHECK(book_id>0),
    title text NOT NULL CHECK(length(trim(title))>0),
    authors text NOT NULL CHECK(length(trim(authors))>0),
    goodreads_edition_id text,
    goodreads_work_id text,
    source_url text NOT NULL,
    source_revision text NOT NULL,
    metadata_status text NOT NULL DEFAULT 'pending' CHECK(metadata_status IN ('pending','approved','rejected')),
    metadata_evidence_url text,
    cover_url text,
    cover_status text NOT NULL DEFAULT 'pending' CHECK(cover_status IN ('pending','approved','rejected')),
    cover_evidence_url text,
    CHECK(metadata_status<>'approved' OR nullif(trim(metadata_evidence_url),'') IS NOT NULL),
    CHECK(cover_status<>'approved' OR (nullif(trim(cover_url),'') IS NOT NULL AND nullif(trim(cover_evidence_url),'') IS NOT NULL))
);
CREATE TABLE booknest.book_descriptions (
    description_id uuid PRIMARY KEY,
    book_id integer NOT NULL REFERENCES booknest.books(book_id),
    source_url text NOT NULL,
    source_revision text NOT NULL,
    source_text_sha256 text NOT NULL CHECK(source_text_sha256 ~ '^[0-9a-f]{64}$'),
    source_scope text NOT NULL CHECK(source_scope IN ('work','edition')),
    identity_verified boolean NOT NULL DEFAULT false,
    rights_status text NOT NULL DEFAULT 'pending' CHECK(rights_status IN ('pending','approved','rejected')),
    rights_evidence_url text,
    intro_vi text,
    content_reviewed boolean NOT NULL DEFAULT false,
    model_version text,
    prompt_version text,
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK(rights_status<>'approved' OR nullif(trim(rights_evidence_url),'') IS NOT NULL),
    CHECK(NOT content_reviewed OR (identity_verified AND nullif(trim(intro_vi),'') IS NOT NULL))
);
CREATE INDEX description_book_idx ON booknest.book_descriptions(book_id,created_at DESC);

-- Only this view is granted to the application: pending metadata never leaks.
CREATE VIEW booknest.public_catalogue WITH (security_barrier=true) AS
SELECT b.book_id,b.title,b.authors,
       CASE WHEN b.cover_status='approved' THEN b.cover_url ELSE NULL END AS cover_url,
       COALESCE(d.intro_vi,'Chưa có mô tả được xác minh') AS intro_vi,
       d.source_url AS intro_source_url,
       b.source_url AS metadata_source_url
FROM booknest.books b
LEFT JOIN LATERAL (
    SELECT x.intro_vi,x.source_url FROM booknest.book_descriptions x
    WHERE x.book_id=b.book_id AND x.identity_verified AND x.content_reviewed AND x.rights_status='approved'
    ORDER BY x.created_at DESC,x.description_id LIMIT 1
) d ON true
WHERE b.metadata_status='approved';
GRANT SELECT ON booknest.public_catalogue TO booknest_runtime;
GRANT SELECT ON booknest.books,booknest.book_descriptions TO booknest_local_reviewer;

CREATE TABLE booknest.app_users (
    user_id uuid PRIMARY KEY,
    auth_issuer text NOT NULL,
    auth_subject text NOT NULL,
    display_name text NOT NULL CHECK(length(trim(display_name)) BETWEEN 1 AND 100),
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE(auth_issuer,auth_subject)
);
CREATE TABLE booknest.user_ratings (
    user_id uuid NOT NULL REFERENCES booknest.app_users(user_id) ON DELETE CASCADE,
    book_id integer NOT NULL REFERENCES booknest.books(book_id),
    rating smallint NOT NULL CHECK(rating BETWEEN 1 AND 5),
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY(user_id,book_id)
);
CREATE TABLE booknest.reading_list (
    user_id uuid NOT NULL REFERENCES booknest.app_users(user_id) ON DELETE CASCADE,
    book_id integer NOT NULL REFERENCES booknest.books(book_id),
    state text NOT NULL CHECK(state IN ('want_to_read','reading','finished')),
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY(user_id,book_id)
);
CREATE TABLE booknest.recommendation_runs (
    run_id uuid PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES booknest.app_users(user_id) ON DELETE CASCADE,
    model_version text NOT NULL,
    support_count integer NOT NULL CHECK(support_count>=0),
    catalogue_version text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE(run_id,user_id)
);
CREATE INDEX recommendation_user_time_idx ON booknest.recommendation_runs(user_id,created_at DESC);
CREATE TABLE booknest.recommendation_items (
    run_id uuid NOT NULL,
    user_id uuid NOT NULL,
    rank smallint NOT NULL CHECK(rank BETWEEN 1 AND 10),
    book_id integer NOT NULL REFERENCES booknest.books(book_id),
    explanation text NOT NULL,
    PRIMARY KEY(run_id,rank),
    UNIQUE(run_id,book_id),
    FOREIGN KEY(run_id,user_id) REFERENCES booknest.recommendation_runs(run_id,user_id) ON DELETE CASCADE
);

CREATE FUNCTION booknest.current_user_id() RETURNS uuid LANGUAGE sql STABLE
SET search_path=pg_catalog AS $$
    SELECT nullif(current_setting('booknest.user_id',true),'')::uuid
$$;
REVOKE ALL ON FUNCTION booknest.current_user_id() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION booknest.current_user_id() TO booknest_runtime;

ALTER TABLE booknest.app_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE booknest.app_users FORCE ROW LEVEL SECURITY;
CREATE POLICY user_self ON booknest.app_users TO booknest_runtime
    USING(user_id=booknest.current_user_id()) WITH CHECK(user_id=booknest.current_user_id());
GRANT SELECT ON booknest.app_users TO booknest_runtime;
GRANT UPDATE(display_name) ON booknest.app_users TO booknest_runtime;

ALTER TABLE booknest.user_ratings ENABLE ROW LEVEL SECURITY;
ALTER TABLE booknest.user_ratings FORCE ROW LEVEL SECURITY;
CREATE POLICY rating_owner ON booknest.user_ratings TO booknest_runtime
    USING(user_id=booknest.current_user_id())
    WITH CHECK(user_id=booknest.current_user_id() AND EXISTS(SELECT 1 FROM booknest.public_catalogue b WHERE b.book_id=user_ratings.book_id));
ALTER TABLE booknest.reading_list ENABLE ROW LEVEL SECURITY;
ALTER TABLE booknest.reading_list FORCE ROW LEVEL SECURITY;
CREATE POLICY reading_owner ON booknest.reading_list TO booknest_runtime
    USING(user_id=booknest.current_user_id())
    WITH CHECK(user_id=booknest.current_user_id() AND EXISTS(SELECT 1 FROM booknest.public_catalogue b WHERE b.book_id=reading_list.book_id));
ALTER TABLE booknest.recommendation_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE booknest.recommendation_runs FORCE ROW LEVEL SECURITY;
CREATE POLICY run_owner ON booknest.recommendation_runs TO booknest_runtime
    USING(user_id=booknest.current_user_id()) WITH CHECK(user_id=booknest.current_user_id());
ALTER TABLE booknest.recommendation_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE booknest.recommendation_items FORCE ROW LEVEL SECURITY;
CREATE POLICY item_owner ON booknest.recommendation_items TO booknest_runtime
    USING(user_id=booknest.current_user_id())
    WITH CHECK(user_id=booknest.current_user_id() AND EXISTS(SELECT 1 FROM booknest.public_catalogue b WHERE b.book_id=recommendation_items.book_id));
GRANT SELECT,INSERT,UPDATE,DELETE ON booknest.user_ratings,booknest.reading_list TO booknest_runtime;
GRANT SELECT,INSERT,DELETE ON booknest.recommendation_runs,booknest.recommendation_items TO booknest_runtime;
COMMIT;
