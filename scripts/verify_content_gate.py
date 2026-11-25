"""Synthetic content lifecycle on isolated PostgreSQL; no real rights approvals."""
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from local_postgres_fixture import native_cluster
from booknest.content_review import check_draft,build_prompt

OUT=ROOT/'reports/day15/content_local_20261123'

def main():
    checks=[]
    with native_cluster() as (owner,runtime):
        with owner() as c:
            version=c.execute('SELECT version()').fetchone()[0]
            c.execute("INSERT INTO booknest.books(book_id,title,authors,source_url,source_revision,metadata_status,metadata_evidence_url) VALUES(1,'Synthetic title','Synthetic author','https://example.invalid/book','v1','approved','https://example.invalid/synthetic-evidence')")
            c.execute("INSERT INTO booknest.book_descriptions(description_id,book_id,source_url,source_revision,source_text_sha256,source_scope,intro_vi) VALUES('20000000-0000-0000-0000-000000000001',1,'https://example.invalid/intro','v1',%s,'work','Synthetic reviewed introduction')",('a'*64,))
        def visible():
            with runtime() as c:return c.execute('SELECT intro_vi,intro_source_url,cover_url FROM booknest.public_catalogue').fetchall()
        fallback=[('Chưa có mô tả được xác minh',None,None)]
        assert visible()==fallback;checks.append('pending description yields fallback without source link')
        with owner() as c:
            c.execute('UPDATE booknest.book_descriptions SET identity_verified=true,content_reviewed=true')
        assert visible()==fallback;checks.append('identity and content alone do not grant rights')
        with owner() as c:
            c.execute("UPDATE booknest.book_descriptions SET rights_status='approved',rights_evidence_url='https://example.invalid/synthetic-evidence'")
        assert visible()==[('Synthetic reviewed introduction','https://example.invalid/intro',None)];checks.append('all three approved gates expose reviewed introduction and source')
        with owner() as c:c.execute("UPDATE booknest.book_descriptions SET rights_status='rejected'")
        assert visible()==fallback;checks.append('revoked rights immediately restore fallback')
        with owner() as c:c.execute("UPDATE booknest.book_descriptions SET rights_status='approved',content_reviewed=false")
        assert visible()==fallback;checks.append('revoked content review restores fallback despite approved rights')
        with owner() as c:c.execute("UPDATE booknest.books SET cover_url='https://example.invalid/cover'")
        assert visible()==fallback;checks.append('pending cover URL is hidden')
        with owner() as c:c.execute("UPDATE booknest.books SET cover_status='approved',cover_evidence_url='https://example.invalid/synthetic-evidence'")
        assert visible()[0][2]=='https://example.invalid/cover';checks.append('cover approval is independent from description rights')
        with owner() as c:c.execute("UPDATE booknest.books SET metadata_status='rejected'")
        assert visible()==[];checks.append('metadata revocation hides whole public record')
    OUT.mkdir(parents=True,exist_ok=True)
    sources=['booknest/content_review.py','scripts/prepare_content_review.py','scripts/verify_content_gate.py','tests/test_content_review.py','db/migrations/001_initial.sql']
    result={'engine':version,'checks_passed':len(checks),'checks':checks,'synthetic_fixture_only':True,
        'real_content_approved':0,'provider_called':False,'semantic_quality_evaluated':False,
        'cluster_stopped_and_removed':True,'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources}}
    (OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Passed',len(checks),'synthetic content lifecycle checks; no real content approved.')

if __name__=='__main__':main()
