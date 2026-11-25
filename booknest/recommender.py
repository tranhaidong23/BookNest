"""Serving adapter for the frozen Day6 KNN; no fitting or test-data dependency."""
import hashlib
import json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
MODEL_VERSION='day06_item_knn_v1:s10_k200'

def file_sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

class Recommender:
    def __init__(self,root=ROOT):
        root=Path(root);base=root/'data/processed/day06_item_knn_v1'
        manifest=json.loads((root/'reports/day06_07/item_knn_20261123/manifest.json').read_text());arrays={}
        for name in ['catalogue_ids','popularity','neighbors_s10','weights_s10']:
            p=base/(name+'.npy')
            if file_sha(p)!=manifest['outputs'][str(p.relative_to(root))]:raise ValueError('Model artifact hash mismatch')
            arrays[name]=np.load(p,allow_pickle=False);arrays[name].flags.writeable=False
        self.ids=arrays['catalogue_ids'];self.popularity=arrays['popularity']
        self.index=arrays['neighbors_s10'];self.weight=arrays['weights_s10']
        self.mapping={int(b):i for i,b in enumerate(self.ids)};self.version=MODEL_VERSION

    def validate_profile(self,profile):
        clean=[];seen=set()
        for book,rating in profile:
            if type(book) is not int or type(rating) is not int:raise ValueError('IDs and ratings must be integers')
            if book not in self.mapping or book in seen:raise ValueError('Unknown or duplicate profile book')
            if not 1<=rating<=5:raise ValueError('Rating must be 1 to 5')
            clean.append((book,rating));seen.add(book)
        return clean

    def recommend(self,profile,limit=10):
        profile=self.validate_profile(profile)
        if type(limit) is not int or not 1<=limit<=10:raise ValueError('Limit must be 1 to 10')
        seen={b for b,r in profile};score=np.zeros(len(self.ids))
        positive=[(self.mapping[b],r-3,b) for b,r in profile if r>=4]
        if positive:
            si=np.array([i for i,w,b in positive]);scales=np.array([w for i,w,b in positive])
            target=self.index[si,:200].ravel();values=(self.weight[si,:200]*scales[:,None]).ravel();good=target>=0
            score=np.bincount(target[good],weights=values[good],minlength=len(self.ids))
        choices=np.array([i for i,b in enumerate(self.ids) if int(b) not in seen],dtype=int)
        fallback=not np.any(score[choices]>0);ranking=self.popularity if fallback else score
        order=choices[np.lexsort((self.ids[choices],-ranking[choices]))[:limit]];output=[]
        for i in order:
            evidence=[]
            if not fallback:
                for src,scale,book in positive:
                    positions=np.flatnonzero(self.index[src,:200]==i)
                    if len(positions):evidence.append({'book_id':book,'contribution':float(self.weight[src,int(positions[0])]*scale)})
                evidence.sort(key=lambda e:(-e['contribution'],e['book_id']))
            output.append({'book_id':int(self.ids[i]),'evidence':evidence[:2],
                'reason_kind':'popularity' if fallback else ('positive_neighbors' if evidence else 'no_positive_evidence')})
        return {'model_version':self.version,'fallback':fallback,'support_count':len(profile),'items':output}

def load_local_catalogue(root=ROOT):
    root=Path(root);m=json.loads((root/'reports/day11/schema_local_20261123/catalogue_manifest.json').read_text());p=root/m['output']
    if file_sha(p)!=m['output_sha256']:raise ValueError('Operational catalogue hash mismatch')
    rows=json.loads(p.read_text(encoding='utf-8'));return {row['book_id']:row for row in rows}

def explanation(item,catalogue):
    if item['reason_kind']=='popularity':return 'Một lựa chọn phổ biến trong dữ liệu học, khi chưa đủ liên hệ từ các sách bạn thích.'
    if item['reason_kind']=='no_positive_evidence':return 'Chưa có đủ liên hệ từ các sách bạn đã đánh giá cao.'
    titles=[catalogue[e['book_id']]['title'] for e in item['evidence']]
    return 'Gợi ý từ những sách bạn đánh giá cao: '+ '; '.join(titles)+'.'
