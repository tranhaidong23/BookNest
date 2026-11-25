"""Reproducible triage, not semantic certification or a production catalogue."""
import csv
import hashlib
import json
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
from audit_extended import sha, verify_manifest
from audit_source_descriptions import clean_text

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/day02/review_20261119'
DETAIL = ROOT / 'data/processed/review_20261119'

# Agent review of all 43 nonempty flagged descriptions, 19 Nov 2026.
# These are dispositions of flags, not independently verified book facts.
ALIASES = {'1000':'series_name_variant','1375':'ampersand_variant','9134':'subtitle_edition_specific_text',
           '113':'series_suffix','400':'series_suffix','3950':'series_suffix','706':'series_suffix_translation_specific_text',
           '413':'series_suffix','4010':'repeated_title_text'}
SHORT = {
 '5752':'title_only','636':'movie_companion_format_only','4210':'title_only','9757':'brief_premise',
 '7955':'format_only','4280':'ingest_placeholder','4415':'japanese_edition_promotion',
 '4431':'author_promotion','2052':'translation_year_only','5718':'generic_adaptation_format',
 '9850':'brief_topic','4622':'dramatization_identity_note_not_synopsis','7362':'brief_premise',
 '8701':'edition_volume_note','5864':'brief_premise','9512':'arabic_genre_only',
 '4815':'brief_topic_with_promotion','7408':'adaptation_specific_brief_premise','6850':'brief_premise',
 '9112':'bilingual_comic_format_only','2478':'brief_premise','6390':'brief_topic',
 '8027':'possible_companion_journal_mismatch'}
DUPES = {**dict.fromkeys(['1950','6846'],'shared_hellboy_origin_text_volume_uncertain'),
         **dict.fromkeys(['810','9906'],'shared_ouran_series_premise'),
         **dict.fromkeys(['2520','8223','6120'],'shared_1q84_general_text'),
         **dict.fromkeys(['6716','2215'],'shared_fudge_series_promotion'),
         **dict.fromkeys(['7696','7481'],'shared_two_poetry_editions_promotion')}

def disposition(book_id, text):
    if not text:
        return 'missing_source', 'empty_after_text_extraction'
    if book_id in SHORT:
        return ('reject_placeholder' if book_id == '4280' else 'needs_more_evidence'), SHORT[book_id]
    if book_id in DUPES:
        return 'hold_volume_specificity', DUPES[book_id]
    if book_id in ALIASES:
        return 'title_flag_resolved_only', ALIASES[book_id]
    raise ValueError('Nonempty flagged book has no explicit review: ' + book_id)

def main():
    manifest = json.loads((ROOT/'docs/DATA_MANIFEST.json').read_text(encoding='utf-8'))
    xml_manifest = json.loads((ROOT/'reports/day01/descriptions_20261119/xml_manifest.json').read_text(encoding='utf-8'))
    archive = ROOT/xml_manifest['path']
    verify_manifest(manifest)
    if sha(archive) != xml_manifest['sha256']:
        raise ValueError('Archive hash mismatch')
    queue_path = ROOT/'data/processed/descriptions_20261119/xml_review_queue.json'
    queue = json.loads(queue_path.read_text(encoding='utf-8'))
    reviews = []
    with zipfile.ZipFile(archive) as z:
        for r in queue:
            body = z.read(r['member'])
            if hashlib.sha256(body).hexdigest() != r['member_sha256']:
                raise ValueError('XML member hash mismatch')
            book = ET.fromstring(body).find('book')
            if book.findtext('id','').strip() != r['goodreads_book_id'] or book.findtext('work/id','').strip() != r['work_id']:
                raise ValueError('ID mismatch')
            text = clean_text(book.findtext('description',''))
            digest = hashlib.sha256(text.encode()).hexdigest() if text else ''
            if digest != r['description_sha256']:
                raise ValueError('Description hash mismatch')
            status, reason = disposition(r['book_id'], text)
            reviews.append({'book_id':r['book_id'], 'status':status, 'reason':reason,
                'reviewer':'Codex agent; not independent human review' if text else 'automated_empty_check',
                'member':r['member'], 'member_sha256':r['member_sha256'], 'description_sha256':digest,
                'description_chars':len(text), 'source_url':r['source_url'],
                'benchmark_keep':True, 'public_display_allowed':False, 'rights_status':'unresolved',
                'ready_for_60_100_word_intro':False})
    blocked = {r['book_id'] for r in reviews if r['status'] != 'title_flag_resolved_only'}
    with (ROOT/'data/raw/goodbooks-10k/books.csv').open(encoding='utf-8',newline='') as f:
        books = list(csv.DictReader(f))
    candidate_ids = {b['book_id'] for b in books} - blocked
    # Descriptive impact only: does not select books based on model/test performance.
    ratings = pd.read_csv(ROOT/'data/raw/goodbooks-10k/ratings.csv',dtype={'user_id':'int32','book_id':'int32','rating':'int8'})
    mask = ratings.book_id.isin({int(i) for i in candidate_ids})
    all_users = set(ratings.user_id)
    kept_users = set(ratings.loc[mask,'user_id'])
    languages = Counter(b['language_code'] or '(missing)' for b in books if b['book_id'] in blocked)
    DETAIL.mkdir(parents=True,exist_ok=True)
    OUT.mkdir(parents=True,exist_ok=True)
    (DETAIL/'review_decisions.json').write_text(json.dumps(reviews,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (DETAIL/'screening_candidate_ids.json').write_text(json.dumps(sorted(map(int,candidate_ids)),indent=2)+'\n',encoding='utf-8')
    verify_manifest(manifest)
    if sha(archive) != xml_manifest['sha256']:
        raise ValueError('Archive changed')
    result = {'checked_at_utc':datetime.now(timezone.utc).isoformat(),'queue_rows':len(queue),
        'status_counts':dict(Counter(r['status'] for r in reviews)),
        'agent_reviewed_nonempty':sum(r['description_chars']>0 for r in reviews),
        'automated_empty_rechecks':sum(r['description_chars']==0 for r in reviews),
        'independent_human_review':False,'benchmark_books_kept':len(books),
        'screening_candidates_not_semantically_approved':len(candidate_ids),
        'description_holds':len(blocked),'product_catalogue_finalized':False,
        'public_rights_cleared':0,'impact_if_candidate_filter_were_applied':{
            'all_ratings':len(ratings),'retained_ratings':int(mask.sum()),'excluded_ratings':int((~mask).sum()),
            'retained_fraction':float(mask.mean()),'users_all':len(all_users),'users_retained':len(kept_users),
            'users_losing_all_ratings':len(all_users-kept_users),'held_book_languages':dict(languages)},
        'raw_hashes_verified_before_after':True,'quality_metrics':None,
        'source_hashes':{'queue':sha(queue_path),'script':sha(Path(__file__)), 'archive':sha(archive)},
        'outputs':{str(p.relative_to(ROOT)):sha(p) for p in [DETAIL/'review_decisions.json',DETAIL/'screening_candidate_ids.json']}}
    (OUT/'review_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=True,indent=2))

if __name__=='__main__':
    main()
