-- Parameter $1 is the validated JSON array from day11_operational_v1/books.json.
-- Run only as migration/catalogue curator, in one transaction, on an empty books table.
-- No conflict overwrite: a repeated import must fail, preserving rights decisions.
INSERT INTO booknest.books(book_id,title,authors,goodreads_edition_id,goodreads_work_id,source_url,source_revision,
    metadata_status,metadata_evidence_url,cover_url,cover_status,cover_evidence_url)
SELECT book_id,title,authors,goodreads_edition_id,goodreads_work_id,source_url,source_revision,
    'pending',NULL,NULL,'pending',NULL
FROM jsonb_to_recordset($1::jsonb) AS x(book_id integer,title text,authors text,
    goodreads_edition_id text,goodreads_work_id text,source_url text,source_revision text);
