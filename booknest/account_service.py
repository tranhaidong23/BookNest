"""Authenticated product operations, restricted to approved catalogue candidates.

This product candidate universe is separate from the 10000-item benchmark. No
benchmark metric is claimed for filtered product recommendations.
"""
import numpy as np

def approved_catalogue(repository):
    return {row['book_id']:row for row in repository.catalogue_snapshot()}

def product_recommendations(engine,profile,catalogue):
    profile=engine.validate_profile(profile);seen={b for b,r in profile}
    choices=np.array([i for i,b in enumerate(engine.ids) if int(b) in catalogue and int(b) not in seen],dtype=int)
    if not len(choices):return {'items':[],'fallback':False,'support_count':len(profile)}
    positive=[(engine.mapping[b],r-3,b) for b,r in profile if r>=4];scores=np.zeros(len(engine.ids))
    if positive:
        rows=np.array([i for i,w,b in positive]);scales=np.array([w for i,w,b in positive])
        targets=engine.index[rows,:200].ravel();weights=(engine.weight[rows,:200]*scales[:,None]).ravel();valid=targets>=0
        scores=np.bincount(targets[valid],weights=weights[valid],minlength=len(engine.ids))
    fallback=not np.any(scores[choices]>0);ranking=engine.popularity if fallback else scores
    ordered=choices[np.lexsort((engine.ids[choices],-ranking[choices]))[:10]];items=[]
    for i in ordered:
        evidence=[]
        if not fallback:
            for source,scale,book in positive:
                if book not in catalogue:continue # Never expose a withdrawn support title.
                positions=np.flatnonzero(engine.index[source,:200]==i)
                if len(positions):evidence.append((float(engine.weight[source,int(positions[0])]*scale),book))
        evidence.sort(key=lambda row:(-row[0],row[1]))
        if fallback:reason='Một lựa chọn phổ biến trong dữ liệu học khi chưa đủ liên hệ từ hồ sơ của bạn.'
        elif evidence:reason='Gợi ý từ những sách bạn đánh giá cao: '+'; '.join(catalogue[b]['title'] for weight,b in evidence[:2])+'.'
        else:reason='Gợi ý theo hồ sơ đánh giá của bạn; chưa có thông tin nguồn phù hợp để giải thích chi tiết.'
        items.append({'book_id':int(engine.ids[i]),'explanation':reason})
    return {'items':items,'fallback':fallback,'support_count':len(profile)}

def create_saved_recommendations(repository,engine,catalogue):
    profile=sorted(repository.ratings().items())
    if len(profile)<3:raise ValueError('Cần ít nhất 3 đánh giá để tạo gợi ý')
    result=product_recommendations(engine,profile,catalogue)
    if result['items']:
        result['run_id']=repository.save_run(profile,result['items'],engine.version+':approved-catalogue','public_catalogue')
    return result

def safe_saved_explanation(engine,profile,book,catalogue):
    """Rebuild evidence from a saved profile, never replay stale stored title text."""
    if book not in catalogue or book not in engine.mapping:return 'Thông tin sách hiện chưa sẵn sàng để hiển thị.'
    target=engine.mapping[book];evidence=[]
    for row in profile:
        source=row['book_id'];rating=row['rating']
        if rating<4 or source not in catalogue or source not in engine.mapping:continue
        i=engine.mapping[source];positions=np.flatnonzero(engine.index[i,:200]==target)
        if len(positions):evidence.append((float(engine.weight[i,int(positions[0])]*(rating-3)),source))
    evidence.sort(key=lambda x:(-x[0],x[1]))
    if evidence:return 'Liên hệ với các sách bạn đã đánh giá cao trong lần gợi ý này: '+'; '.join(catalogue[b]['title'] for w,b in evidence[:2])+'.'
    return 'Gợi ý đã lưu; hiện chưa có thông tin nguồn phù hợp để giải thích chi tiết.'
