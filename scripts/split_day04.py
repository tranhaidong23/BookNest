"""Execute protocol v0.1. No fitting, feature construction, or model evaluation."""
import hashlib
import json
import platform
from pathlib import Path
import numpy as np
import pandas as pd
from audit_extended import sha, verify_manifest
from prepare_day03 import frozen_write, write_json, validate_ratings

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/processed/day04_split_v1'
OUT=ROOT/'reports/day04/split_20261120'
SEED=20261120
COLS=['user_id','book_id','rating']

def digest(namespace,user,book=''):
    return hashlib.sha256(f'booknest|v0.1|{SEED}|{namespace}|{user}|{book}'.encode('utf-8')).digest()

def user_groups(users):
    ordered=sorted(set(map(int,users)),key=lambda u:(digest('users',u),u))
    n=len(ordered); a=8*n//10; b=n//10
    return {u:('development' if i<a else 'cold_validation' if i<a+b else 'cold_test')
            for i,u in enumerate(ordered)}

def assign(ratings):
    """Assignments depend exclusively on IDs and number of observations, never labels."""
    f=ratings[COLS].copy()
    if f.duplicated(['user_id','book_id']).any():
        raise ValueError('Duplicate pairs')
    groups=user_groups(f['user_id'].unique())
    f['group']=f['user_id'].map(groups)
    cold=f['group'].ne('development').to_numpy()
    hashes=np.array([digest('cold_support' if c else 'warm_pairs',int(u),int(b))
                     for u,b,c in zip(f['user_id'],f['book_id'],cold)],dtype='S32')
    order=np.lexsort((f['book_id'].to_numpy(),hashes,f['user_id'].to_numpy()))
    del hashes
    f=f.iloc[order].copy()
    rank=f.groupby('user_id',sort=False).cumcount()+1
    size=f.groupby('user_id',sort=False)['book_id'].transform('size')
    cold=f['group'].ne('development')
    hold=size//10
    f['partition']='train'
    f.loc[~cold & (hold>=1) & (rank<=hold),'partition']='warm_validation'
    f.loc[~cold & (hold>=1) & (rank>hold) & (rank<=2*hold),'partition']='warm_test'
    for group in ['cold_validation','cold_test']:
        member=f['group'].eq(group)
        f.loc[member & (size>=11) & (rank<=10),'partition']=group+'_support'
        f.loc[member & (size>=11) & (rank>10),'partition']=group+'_target'
        f.loc[member & (size<11),'partition']=group+'_ineligible'
    f['support_rank']=np.where(cold & (size>=11) & (rank<=10),rank,0)
    return f.sort_values(['user_id','book_id']).reset_index(drop=True)

def support_prefix(frame,k):
    if k not in (3,5,10):
        raise ValueError('Protocol support size must be 3, 5, or 10')
    return frame.loc[frame['support_rank'].between(1,k),COLS].copy()

def check_partition(f,source):
    canonical=source[COLS].sort_values(['user_id','book_id']).reset_index(drop=True)
    pd.testing.assert_frame_equal(f[COLS],canonical,check_dtype=False)
    assert not f.duplicated(['user_id','book_id']).any()
    assert f.groupby('user_id')['group'].nunique().eq(1).all()
    train_users=set(f.loc[f['partition']=='train','user_id'])
    assert not train_users & set(f.loc[f['group']!='development','user_id'])
    for group in ['cold_validation','cold_test']:
        support=f.loc[f['partition']==group+'_support']
        target=f.loc[f['partition']==group+'_target']
        assert support.groupby('user_id').size().eq(10).all()
        assert set(support['user_id'])==set(target['user_id'])
        assert support.groupby('user_id')['support_rank'].apply(lambda x:set(x)==set(range(1,11))).all()
        for k in (3,5,10):
            assert support_prefix(support,k).groupby('user_id').size().eq(k).all()
        # Every pair has one partition; support ranks/prefix nesting share one target file.
        assert not set(zip(support.user_id,support.book_id)) & set(zip(target.user_id,target.book_id))
    warm=f.loc[f['group']=='development'].groupby(['user_id','partition']).size().unstack(fill_value=0)
    assert warm.get('train',pd.Series(dtype=int)).gt(0).all()

def main():
    day3=ROOT/'reports/day03/preparation_v2_20261120/manifest.json'
    protocol=ROOT/'docs/EVALUATION_PROTOCOL.md'
    m=json.loads(day3.read_text(encoding='utf-8'))
    original=json.loads((ROOT/'docs/DATA_MANIFEST.json').read_text(encoding='utf-8'))
    verify_manifest(original)
    protected={**m['inputs'],**m['outputs'],str(day3.relative_to(ROOT)):sha(day3),
               str(protocol.relative_to(ROOT)):sha(protocol)}
    for p,h in protected.items():
        if sha(ROOT/p)!=h: raise ValueError('Input changed: '+p)
    ratings=pd.read_csv(ROOT/'data/processed/day03_v2/ratings.csv',dtype='int64')
    book_ids={json.loads(line)['book_id'] for line in (ROOT/'data/processed/day03_v2/books.jsonl').read_text(encoding='utf-8').splitlines()}
    validate_ratings(ratings,book_ids)
    print('Assigning all pairs using protocol hashes.',flush=True)
    f=assign(ratings)
    check_partition(f,ratings)
    print('Checking full-data reversal and label perturbation invariance.',flush=True)
    # Change ALL labels, including holdouts, and reverse order: IDs alone determine split.
    changed=ratings.iloc[::-1].copy()
    changed['rating']=6-changed['rating']
    replay=assign(changed)
    assignment_cols=['user_id','book_id','group','partition','support_rank']
    pd.testing.assert_frame_equal(f[assignment_cols],replay[assignment_cols])
    del changed,replay
    print('Writing immutable split files and auditing exported labels.',flush=True)
    outputs={}
    partitions=['train','warm_validation','warm_test','cold_validation_support','cold_validation_target',
                'cold_test_support','cold_test_target','cold_validation_ineligible','cold_test_ineligible']
    train_books=set(f.loc[f.partition=='train','book_id'])
    stats={}
    for name in partitions:
        subset=f.loc[f.partition==name]
        cols=COLS+(['support_rank'] if name.endswith('_support') else [])
        path=DATA/(name+'.csv')
        frozen_write(path,subset[cols].to_csv(index=False,lineterminator='\n').encode())
        restored=pd.read_csv(path,dtype='int64')
        pd.testing.assert_frame_equal(restored,subset[cols].reset_index(drop=True),check_dtype=False)
        outputs[str(path.relative_to(ROOT))]=sha(path)
        stats[name]={'rows':len(subset),'users':int(subset.user_id.nunique()),'books':int(subset.book_id.nunique()),
                     'unseen_train_item_rows':int((~subset.book_id.isin(train_books)).sum()),
                     'unseen_train_items':int(subset.loc[~subset.book_id.isin(train_books),'book_id'].nunique())}
        if name.endswith('_target') or name in ['warm_validation','warm_test']:
            positives=set(subset.loc[subset.rating>=4,'user_id'])
            stats[name]['users_without_positive_target']=int(subset.user_id.nunique()-len(positives))
    users=f[['user_id','group']].drop_duplicates().sort_values('user_id')
    users_path=DATA/'user_groups.csv'
    frozen_write(users_path,users.to_csv(index=False,lineterminator='\n').encode())
    outputs[str(users_path.relative_to(ROOT))]=sha(users_path)
    candidate_path=DATA/'catalogue_ids.csv'
    frozen_write(candidate_path,pd.DataFrame({'book_id':sorted(book_ids)}).to_csv(index=False,lineterminator='\n').encode())
    outputs[str(candidate_path.relative_to(ROOT))]=sha(candidate_path)
    write_json(OUT/'audit.json',{'source_rows':len(ratings),'source_users':len(users),'catalogue_books':len(book_ids),
        'user_groups':users['group'].value_counts().to_dict(),'partitions':stats,
        'development_train_only_users':int(users['group'].eq('development').sum()-stats['warm_validation']['users']),
        'catalogue_items_without_train':len(book_ids-train_books),
        'partition_exhaustive_disjoint':True,'source_ids_labels_preserved':True,
        'cold_users_absent_from_train':True,'support_nested_3_5_10':True,'targets_shared_across_support_sizes':True,
        'full_input_reversal_and_label_perturbation_assignment_equal':True,
        'export_readback_equal':True,'test_labels_inspected_for_structural_audit_only':True,
        'models_trained':False,'quality_metrics':None})
    # Capture immutable protocol bytes alongside split without changing Day3 document.
    frozen_write(OUT/'protocol_v0.1.md',protocol.read_bytes())
    verify_manifest(original)
    for p,h in protected.items():
        if sha(ROOT/p)!=h: raise ValueError('Input changed during run: '+p)
    manifest={'split_version':'day04_split_v1','protocol_version':'0.1','seed':SEED,
        'hash_pattern':'booknest|v0.1|20261120|namespace|user_id|book_id',
        'namespaces':['users','cold_support','warm_pairs'],'inputs':protected,'outputs':outputs,
        'protocol_snapshot_sha256':sha(OUT/'protocol_v0.1.md'),'audit_sha256':sha(OUT/'audit.json'),
        'script_sha256':sha(Path(__file__)),'python':platform.python_version(),'pandas':pd.__version__,'numpy':np.__version__,
        'models_trained':False,'test_evaluation_performed':False}
    write_json(OUT/'manifest.json',manifest)
    print(json.dumps({'user_groups':users['group'].value_counts().to_dict(),'partitions':stats},indent=2),flush=True)

if __name__=='__main__': main()
