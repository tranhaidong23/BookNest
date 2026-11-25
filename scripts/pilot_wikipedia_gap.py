"""Bounded 20-book gap pilot; caches API responses, never modifies catalogue v1."""
import argparse
import csv
import hashlib
import json
import random
import time
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from audit_extended import verify_manifest, sha
from pilot_descriptions import base_title

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/day02/wikipedia_gap_20261119'
CACHE=ROOT/'data/external/wikipedia/gap_20261119'

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--fetch',action='store_true')
    parser.add_argument('--retry-errors',action='store_true',help='One slow retry using separate immutable attempt files')
    args=parser.parse_args()
    original=json.loads((ROOT/'docs/DATA_MANIFEST.json').read_text(encoding='utf-8'))
    frozen=ROOT/'data/processed/catalogue_v1/catalogue.jsonl'
    frozen_hash=sha(frozen)
    verify_manifest(original)
    decisions=json.loads((ROOT/'data/processed/review_20261119/review_decisions.json').read_text(encoding='utf-8'))
    with (ROOT/'data/raw/goodbooks-10k/books.csv').open(encoding='utf-8',newline='') as f:
        books={b['book_id']:b for b in csv.DictReader(f)}
    rng=random.Random(20261120)
    selected=[]
    for status,n in [('missing_source',12),('needs_more_evidence',4),('hold_volume_specificity',4)]:
        group=sorted([r for r in decisions if r['status']==status],key=lambda r:int(r['book_id']))
        selected.extend(rng.sample(group,n))
    CACHE.mkdir(parents=True,exist_ok=True)
    OUT.mkdir(parents=True,exist_ok=True)
    manifest=[]; rows=[]
    for r in selected:
        b=books[r['book_id']]
        query=base_title(b['title'])+' '+b['authors'].split(',')[0]
        params={'action':'query','generator':'search','gsrsearch':query,'gsrlimit':3,'gsrnamespace':0,
                'prop':'extracts|revisions|info|pageprops','exintro':1,'explaintext':1,'rvprop':'ids|timestamp',
                'inprop':'url','ppprop':'disambiguation','format':'json','formatversion':2}
        url='https://en.wikipedia.org/w/api.php?'+urllib.parse.urlencode(params)
        path=CACHE/(b['book_id']+'.json')
        retry_path=CACHE/(b['book_id']+'_retry1.json')
        if retry_path.exists():
            path=retry_path
        elif args.retry_errors and path.exists() and json.loads(path.read_text(encoding='utf-8')).get('error'):
            path=retry_path
        if not path.exists():
            if not args.fetch:
                raise RuntimeError('Cache absent: '+b['book_id'])
            time.sleep(8)
            try:
                req=urllib.request.Request(url,headers={'User-Agent':'BookNest-Educational-Pilot/0.1'})
                with urllib.request.urlopen(req,timeout=30) as response:
                    body=response.read()
                payload={'url':url,'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),
                         'body':body.decode('utf-8'),'body_sha256':hashlib.sha256(body).hexdigest()}
            except urllib.error.HTTPError as exc:
                payload={'url':url,'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'error':str(exc),
                         'http_status':exc.code,'retry_after':exc.headers.get('Retry-After'),'body':'{}'}
                if exc.code==429:
                    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
                    raise RuntimeError('Rate limited: stop network requests; retry later respecting Retry-After') from exc
            except Exception as exc:
                payload={'url':url,'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'error':str(exc),'body':'{}'}
            path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
        payload=json.loads(path.read_text(encoding='utf-8'))
        if payload['url']!=url:
            raise ValueError('Query changed; create a new pilot version')
        if payload.get('body_sha256') and hashlib.sha256(payload['body'].encode()).hexdigest()!=payload['body_sha256']:
            raise ValueError('Cache body hash mismatch')
        data=json.loads(payload['body'])
        pages=sorted(data.get('query',{}).get('pages',[]),key=lambda p:p.get('index',999))
        row={'book_id':b['book_id'],'title':b['title'],'authors':b['authors'],'work_id':b['work_id'],
             'group':r['status'],'query':query,'candidates':pages,'error':payload.get('error') or data.get('error')}
        rows.append(row)
        manifest.append({k:v for k,v in payload.items() if k!='body'}|{'path':str(path.relative_to(ROOT)),'cache_sha256':sha(path)})
        print(b['book_id'],len(pages),'candidates',flush=True)
    detail=ROOT/'data/processed/wikipedia_gap_20261119'
    detail.mkdir(parents=True,exist_ok=True)
    (detail/'candidates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    verify_manifest(original)
    assert sha(frozen)==frozen_hash
    result={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'seed':20261120,'sample_size':len(rows),
        'selection':'12 missing, 4 short/insufficient, 4 duplicate-volume; fixed random sample inside each group',
        'sample_book_ids':[r['book_id'] for r in rows],'books_with_search_results':sum(bool(r['candidates']) for r in rows),
        'errors':sum(bool(r['error']) for r in rows),'matching_accepted':None,'source_coverage':None,
        'raw_hashes_verified_before_after':True,'frozen_catalogue_sha256_unchanged':frozen_hash,
        'candidates_sha256':sha(detail/'candidates.json'),'quality_metrics':None}
    (OUT/'search_audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (OUT/'response_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
