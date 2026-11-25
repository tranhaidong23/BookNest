"""Replay agent-reviewed work matches; keep public and edition gates closed."""
import hashlib
import json
from collections import Counter
from pathlib import Path
from audit_extended import sha, verify_manifest

ROOT = Path(__file__).resolve().parents[1]
REL = 'data/processed/wikipedia_gap_20261119'
OUT = ROOT / 'reports/day02/wikipedia_gap_20261119'
# Manually reviewed candidates and bounded source spans, not fuzzy auto-approval.
MATCHES = {
    '8947': (2380715, 'narrative_candidate', '[[Quenton Cassidy]] is', '\n\nCassidy, who', 'Plot summary: exclude opening quotation, ending and reception; citation warning remains.'),
    '6317': (10988343, 'narrative_candidate', "''The Looming Tower'' is largely", '\n\n== Awards', 'Overview only; nofootnotes warning retained; corroboration required.'),
    '7878': (6554966, 'narrative_candidate', 'The protagonist is Joseph', ' The [[moral]]', 'Premise only; exclude quoted moral/reviews and adaptation. Re-illustrated 1977/1999 versions not edition-matched.'),
    '7917': (3773860, 'thin_source', 'Winchester examines', '\n\n==Critical', 'Short summary; do not pad to 60-100 words or import volcano article as book content.'),
    '6390': (684924, 'narrative_candidate', "In ''The Te of Piglet''", '\n\n==Reception', 'Synopsis only; exclude reviews and quotations from reviews.'),
    '6716': (2870221, 'narrative_candidate', 'As the story begins', '\n\nThat plan backfires', 'Opening plot paragraph distinguishes this volume; exclude spoilers and reception.'),
    '2215': (2040389, 'narrative_candidate', 'At the beginning of this book', '\n\nPeter deals', 'First two plot paragraphs identify this volume; exclude ending/adaptations.'),
    '7696': (1878707, 'thin_source', "'''''Now We Are Six''''' is", '\n\n==Title', 'Lead only; exclude poems, quotations, analysis and media. Limited basis for a long intro.'),
}
HOLDS = {
    '8120': 'Search returned award lists; no book-specific source in top 3. Not proof Wikipedia lacks an article.',
    '9685': 'Film/TV adaptations only. The Executioners is an alternate-title lead requiring a separate lookup.',
    '7547': 'Author and strategy topics are not a description of this specific book.',
    '4765': 'Magazine/film/author sources do not establish the Marvel Illustrated collection edition.',
    '3651': 'Nana series is not volume 1.',
    '3159': 'Cookbook family spanning editions; contents of target edition not established.',
    '3636': 'Individual Inheritance novels are not this three-book omnibus.',
    '3546': 'Author biography mentions memoir but provides no book-specific synopsis.',
    '5752': 'Preacher series is not volume 9.',
    '4622': 'Kafka novel is not the Fishelson dramatization.',
    '7408': 'Returned pages are unrelated; cannot substitute generic Andersen tale for Janet Stevens version.',
    '6120': 'Whole 1Q84 novel spans three volumes; no specific volume-3 segment verified.',
}

def checked_payload(path):
    payload = json.loads(path.read_text(encoding='utf-8'))
    if hashlib.sha256(payload['body'].encode('utf-8')).hexdigest() != payload['body_sha256']:
        raise ValueError('Response hash mismatch: ' + str(path))
    data = json.loads(payload['body'])
    if data.get('error'):
        raise ValueError(data['error'])
    return data

def extract_span(content, start, end):
    if content.count(start) != 1:
        raise ValueError('Ambiguous or missing reviewed span')
    offset = content.index(start)
    stop = content.index(end, offset)
    return content[offset:stop].strip()

def main():
    original = json.loads((ROOT/'docs/DATA_MANIFEST.json').read_text(encoding='utf-8'))
    verify_manifest(original)
    frozen = ROOT/'data/processed/catalogue_v1/catalogue.jsonl'
    expected = '869aa530a03b016a0795cfc1f752a927f59dc5df5f49d4054e6a4e9806c1de55'
    assert sha(frozen) == expected
    rows = json.loads((ROOT/REL/'candidates.json').read_text(encoding='utf-8'))
    assert {r['book_id'] for r in rows} == set(MATCHES) | set(HOLDS)
    snapshot = ROOT/'data/external/wikipedia/gap_20261119/matched_revisions.json'
    data = checked_payload(snapshot)
    pages = {p['pageid']: p for p in data['query']['pages']}
    manifest = json.loads((OUT/'response_manifest.json').read_text(encoding='utf-8'))
    for entry in manifest:
        assert sha(ROOT/entry['path']) == entry['cache_sha256']
        checked_payload(ROOT/entry['path'])
    overlay = []
    for row in rows:
        bid = row['book_id']
        record = {k: row[k] for k in ('book_id','work_id','title','authors','group')}
        record.update(reviewer='Codex agent; not independent human review', edition_verified=False,
                      public_ready=False, rights_status='pending_segment_review', intro_vi=None)
        if bid in HOLDS:
            record.update(identity_status='hold', reason=HOLDS[bid], source=None)
        else:
            pid, status, start, end, note = MATCHES[bid]
            candidate = next(p for p in row['candidates'] if p['pageid'] == pid)
            rev = pages[pid]['revisions'][0]
            assert rev['revid'] == candidate['revisions'][0]['revid']
            content = rev['slots']['main']['content']
            span = extract_span(content, start, end)
            record.update(identity_status='work_match', content_status=status, reason=note,
                source={'page_id':pid, 'revision_id':rev['revid'], 'title':pages[pid]['title'],
                        'url':candidate['fullurl'], 'revision_url':f"https://en.wikipedia.org/w/index.php?oldid={rev['revid']}",
                        'history_url':candidate['fullurl']+'?action=history',
                        'snapshot_path':str(snapshot.relative_to(ROOT)), 'snapshot_sha256':sha(snapshot),
                        'wikitext_sha256':hashlib.sha256(content.encode()).hexdigest(),
                        'selected_wikitext':span, 'selected_wikitext_sha256':hashlib.sha256(span.encode()).hexdigest(),
                        'site_declared_license':data['query']['rightsinfo'],
                        'reuse_conditions':['Attribute article and contributors/history','Link license','Indicate translation/summary changes','ShareAlike for adapted text','Do not reuse images or third-party quotes'],
                        'review_limit':'Selected spans inspected; history/talk/imported material not fully audited. Not public approval.'})
        overlay.append(record)
    target = ROOT/REL/'source_overlay.json'
    target.write_text(json.dumps(overlay,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    groups = {}
    for group in sorted({r['group'] for r in rows}):
        subset = [r for r in overlay if r['group']==group]
        groups[group] = {'sample':len(subset), 'work_matches':sum(r['identity_status']=='work_match' for r in subset),
                         'narrative_candidates':sum(r.get('content_status')=='narrative_candidate' for r in subset)}
    attempts = list((ROOT/'data/external/wikipedia/gap_20261119').glob('*.json'))
    errors = [p for p in attempts if json.loads(p.read_text(encoding='utf-8')).get('error')]
    result = {'sample_size':len(rows),'work_matches':8,'narrative_candidates':6,'thin_sources':2,'held':12,
              'edition_verified':0,'public_ready':0,'strata':groups,'initial_error_attempts':len(errors),
              'final_search_errors':sum(bool(r['error']) for r in rows),
              'overlay_sha256':sha(target),'frozen_catalogue_sha256':sha(frozen),
              'raw_hashes_verified':True,'quality_metrics':None,
              'limits':'Fixed stratified pilot; not population coverage or independent matching accuracy.',
              'artifact_manifest':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in [snapshot,*errors]]}
    assert Counter(r['identity_status'] for r in overlay) == {'work_match':8,'hold':12}
    verify_manifest(original)
    assert sha(frozen) == expected
    (OUT/'review_audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__ == '__main__':
    main()
