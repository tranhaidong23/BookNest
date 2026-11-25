BEGIN;
CREATE TABLE booknest.recommendation_support (
    run_id uuid NOT NULL,
    user_id uuid NOT NULL,
    book_id integer NOT NULL REFERENCES booknest.books(book_id),
    rating smallint NOT NULL CHECK(rating BETWEEN 1 AND 5),
    PRIMARY KEY(run_id,book_id),
    FOREIGN KEY(run_id,user_id) REFERENCES booknest.recommendation_runs(run_id,user_id) ON DELETE CASCADE
);
ALTER TABLE booknest.recommendation_support ENABLE ROW LEVEL SECURITY;
ALTER TABLE booknest.recommendation_support FORCE ROW LEVEL SECURITY;
CREATE POLICY support_owner ON booknest.recommendation_support TO booknest_runtime
    USING(user_id=booknest.current_user_id()) WITH CHECK(user_id=booknest.current_user_id());
-- Immutable snapshot: no UPDATE grant, removal cascades from an owned run.
GRANT SELECT,INSERT ON booknest.recommendation_support TO booknest_runtime;
INSERT INTO booknest.schema_migrations(version) VALUES(2);
COMMIT;
