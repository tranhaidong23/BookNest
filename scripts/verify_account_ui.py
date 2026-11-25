"""AppTest -> actual repository -> isolated PostgreSQL; auth identity is injected test input."""
import sys
import json
from pathlib import Path
from uuid import UUID
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from local_postgres_fixture import native_cluster
from booknest.repository import PostgresRepository
from booknest.recommender import Recommender
from streamlit.testing.v1 import AppTest
from audit_extended import sha

OUT=ROOT/'reports/day12_14/account_ui_20261123'
A=UUID('10000000-0000-0000-0000-000000000001');B=UUID('10000000-0000-0000-0000-000000000002')

def screen(repository,engine):
    import streamlit as st
    from app.account import render_account
    st.set_page_config(page_title='BookNest integration test')
    render_account(repository=repository,engine=engine)

def run_app(repo,engine):
    app=AppTest.from_function(screen,args=(repo,engine),default_timeout=30).run()
    assert not app.exception and not app.error
    return app

def main():
    checks=[];engine=Recommender()
    with native_cluster() as (owner,connect):
        with owner() as c:
            version=c.execute('SELECT version()').fetchone()[0]
            c.execute("INSERT INTO booknest.app_users(user_id,auth_issuer,auth_subject,display_name) VALUES(%s,'synthetic','a','Alice'),(%s,'synthetic','b','Bob')",(A,B))
            for book in range(1,16):
                c.execute("INSERT INTO booknest.books(book_id,title,authors,source_url,source_revision,metadata_status,metadata_evidence_url) VALUES(%s,%s,'Synthetic author','https://example.invalid','fixture',%s,%s)",(book,'SYNTHETIC SECRET TITLE' if book==1 else f'Synthetic book {book}','pending' if book==15 else 'approved',None if book==15 else 'https://example.invalid/evidence'))
        a=PostgresRepository(connect,A);b=PostgresRepository(connect,B)
        app=run_app(a,engine);assert len(app.select_slider)==8;checks.append('account catalogue renders approved records with pagination')
        for book in (1,2,3):
            app.select_slider(key=f'account_rating_catalogue_{book}').set_value(5).run()
            app.button(key=f'account_save_catalogue_{book}').click().run()
            assert not app.exception and not app.error
        assert a.ratings()=={1:5,2:5,3:5};checks.append('UI rating writes reach actual PostgreSQL')
        app.button(key='account_add_catalogue_1').click().run();assert a.shelf()=={1:'want_to_read'};checks.append('UI shelf write persists')
        app.sidebar.radio[0].set_value('Gợi ý').run();app.button(key='account_generate').click().run()
        assert not app.exception and not app.error
        history=a.history();assert len(history)==1 and len(history[0]['items'])==10
        ids={i['book_id'] for i in history[0]['items']};assert ids<=set(range(4,15));checks.append('UI generation atomically saves ten approved unseen recommendations and snapshot')
        fresh=run_app(PostgresRepository(connect,A),engine)
        assert '3 sách đã đánh giá' in fresh.sidebar.caption[0].value;checks.append('fresh UI session reloads stored ratings and shelf')
        bob=run_app(b,engine);assert b.ratings()=={} and b.history()==[]
        bob.sidebar.radio[0].set_value('Gợi ý').run();assert bob.button(key='account_generate').disabled;checks.append('second account UI sees no first-account profile or history')
        app.sidebar.radio[0].set_value('Hồ sơ').run();app.text_input(key='account_display_name').set_value('Alice updated').run();app.button(key='account_save_name').click().run()
        assert a.profile()['display_name']=='Alice updated' and b.profile()['display_name']=='Bob';checks.append('UI profile edit persists only for its owner')
        withdrawn=history[0]['items'][0]['book_id']
        with owner() as c:
            c.execute("UPDATE booknest.books SET metadata_status='pending' WHERE book_id IN (1,%s)",(withdrawn,))
            c.execute("UPDATE booknest.recommendation_items SET explanation='SYNTHETIC SECRET TITLE stale explanation'")
        app.sidebar.radio[0].set_value('Gợi ý').run();assert not app.exception and not app.error
        text='\n'.join(e.value for e in app.markdown)+ '\n'.join(e.value for e in app.subheader)
        assert 'SYNTHETIC SECRET TITLE' not in text and 'stale explanation' not in text
        app.sidebar.radio[0].set_value('Lịch sử').run()
        text='\n'.join(e.value for e in app.markdown);assert 'SYNTHETIC SECRET TITLE' not in text and 'stale explanation' not in text
        checks.append('withdrawn support/candidate titles and stale stored explanations never replay in UI')
        app.sidebar.radio[0].set_value('Kệ sách').run();app.button(key='account_hidden_shelf_library_1').click().run();assert a.shelf()=={}
        app.radio(key='account_shelf_filter').set_value('Đã đánh giá').run();app.button(key='account_hidden_rating_library_1').click().run();assert a.ratings()=={2:5,3:5}
        checks.append('owner can remove personal data for a withdrawn book without exposing metadata')
        app.sidebar.radio[0].set_value('Lịch sử').run();app.button(key='account_delete_run_'+str(history[0]['run_id'])).click().run();assert a.history()==[];checks.append('UI owned run deletion persists and cascades')
        with owner() as c:c.execute("UPDATE booknest.books SET metadata_status='pending'")
        app.sidebar.radio[0].set_value('Khám phá').run();assert not app.select_slider and not app.exception
        assert any('Chưa có sách đã duyệt' in e.value for e in app.info);checks.append('empty public catalogue does not fall back to research metadata')
    OUT.mkdir(parents=True,exist_ok=True)
    sources=['app/account.py','app/main.py','booknest/account_service.py','booknest/repository.py','scripts/verify_account_ui.py']
    (OUT/'validation.json').write_text(json.dumps({'engine':version,'checks_passed':len(checks),'checks':checks,
        'actual_repository_and_database':True,'auth_identity_injected_for_test':True,'external_oidc_verified':False,'browser_visual_qa':False,
        'neon_connected':False,'isolated_cluster_stopped_and_removed':True,'sources_sha256':{p:sha(ROOT/p) for p in sources}},indent=2)+'\n',encoding='utf-8')
    print('Passed',len(checks),'account UI/database checks; test identity injection only, no OIDC or cloud.')

if __name__=='__main__':main()
