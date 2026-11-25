"""Transfer parity against saved validation outputs; never reads test ratings."""
import sys
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pandas as pd
from booknest.recommender import Recommender,file_sha
from prepare_day03 import write_json

def main():
    engine=Recommender();source=ROOT/'data/processed/day04_split_v1/cold_validation_support.csv'
    sm=json.loads((ROOT/'reports/day04/split_20261120/manifest.json').read_text())
    assert file_sha(source)==sm['outputs'][str(source.relative_to(ROOT))]
    frame=pd.read_csv(source).query('support_rank <= 5');profiles={int(u):list(zip(map(int,g.book_id),map(int,g.rating))) for u,g in frame.groupby('user_id')}
    saved=ROOT/'data/processed/day06_item_knn_v1/cold5_s10_k200_top10.json'
    km=json.loads((ROOT/'reports/day06_07/item_knn_20261123/manifest.json').read_text())
    assert file_sha(saved)==km['outputs'][str(saved.relative_to(ROOT))]
    expected=json.loads(saved.read_text());assert set(profiles)=={r['user_id'] for r in expected}
    for row in expected:
        result=engine.recommend(profiles[row['user_id']])
        assert [i['book_id'] for i in result['items']]==row['book_ids']
        assert result['fallback']==row['fallback']
        for item in result['items']:
            assert all(e['book_id'] in {b for b,r in profiles[row['user_id']] if r>=4} for e in item['evidence'])
    write_json(ROOT/'reports/day12_14/local_app_20261123/serving_validation.json',{'validation_users_checked':len(expected),'all_top10_and_fallback_match':True,
        'test_data_read':False,'model_version':engine.version,'adapter_sha256':file_sha(ROOT/'booknest/recommender.py'),'verifier_sha256':file_sha(Path(__file__))})
    print('Serving adapter matches all',len(expected),'saved validation Top10/fallback decisions.')

if __name__=='__main__':main()
