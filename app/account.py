"""PostgreSQL account UI, no unverified local catalogue fallback."""
from pathlib import Path
import streamlit as st
from booknest.auth_backend import AccountConfig,account_from_streamlit
from booknest.identity import IdentityError
from booknest.repository import StorageError,StaleProfileError
from booknest.recommender import Recommender
from booknest.account_service import approved_catalogue,create_saved_recommendations,safe_saved_explanation
ROOT=Path(__file__).resolve().parents[1]

@st.cache_resource
def model():return Recommender()

def get_account():
    try:
        settings=st.secrets['booknest'];auth=st.secrets['auth']
        config=AccountConfig(issuer=settings['expected_issuer'],client_id=auth['client_id'],runtime_dsn=settings['runtime_database_url'],broker_dsn=settings['broker_database_url'])
        if not auth.get('redirect_uri') or not auth.get('cookie_secret') or not auth.get('server_metadata_url') or not auth.get('client_secret'):
            raise ValueError('Missing provider configuration')
    except (KeyError,FileNotFoundError,ValueError):
        st.error('Chưa cấu hình đầy đủ đăng nhập và database phía server. Chế độ tài khoản chưa sẵn sàng.');st.stop()
    user=st.user.to_dict()
    if user.get('is_logged_in') is not True:
        st.title('Chào mừng bạn đến với BookNest')
        st.write('Đăng nhập để lưu đánh giá, kệ sách và lịch sử trên tài khoản của bạn.')
        if st.button('Đăng nhập',type='primary'):st.login()
        st.stop()
    try:return account_from_streamlit(user,config)
    except IdentityError:
        st.error('Phiên đăng nhập hoặc kết nối tài khoản chưa hợp lệ. Vui lòng đăng nhập lại hoặc kiểm tra cấu hình server.')
        if st.button('Đăng xuất phiên hiện tại'):st.logout()
        st.stop()

def render_account(repository=None,engine=None):
    # Optional arguments are dependency injection for headless integration tests,
    # never read from URL/query params or browser widgets.
    repository=get_account() if repository is None else repository
    try:
        identity=str(repository.user_id)
        if st.session_state.get('account_identity')!=identity:
            for key in list(st.session_state):
                if key.startswith('account_'):del st.session_state[key]
            st.session_state['account_identity']=identity
        engine=model() if engine is None else engine
        catalogue=approved_catalogue(repository);profile=repository.profile();ratings=repository.ratings();shelf=repository.shelf()
        with st.sidebar:
            st.title('📚 BookNest');st.write(profile['display_name'])
            page=st.radio('Tài khoản',['Khám phá','Gợi ý','Kệ sách','Lịch sử','Hồ sơ'],key='account_navigation')
            st.caption(f'{len(ratings)} sách đã đánh giá · {len(shelf)} sách trên kệ')
            if st.button('Đăng xuất',key='account_logout'):
                for key in list(st.session_state):
                    if key.startswith('account_'):del st.session_state[key]
                st.logout()
        st.caption('Chế độ tài khoản PostgreSQL local · chỉ hiển thị metadata và nội dung đã được duyệt.')

        def card(book,context,reason=None):
            row=catalogue.get(book)
            if row is None:
                st.info('Thông tin sách hiện chưa sẵn sàng để hiển thị.')
                if book in ratings and st.button('Bỏ đánh giá đã lưu',key=f'account_hidden_rating_{context}_{book}'):
                    repository.delete_rating(book);st.rerun()
                if book in shelf and st.button('Bỏ sách khỏi kệ',key=f'account_hidden_shelf_{context}_{book}'):
                    repository.delete_shelf(book);st.rerun()
                return
            with st.container(border=True):
                st.subheader(row['title']);st.write(row['authors'])
                st.write(row['intro_vi'])
                if reason:st.write(reason)
                # Covers remain project-owned placeholders until URL serving is separately reviewed.
                st.image(str(ROOT/'app/assets/cover-placeholder.svg'),width=100)
                if row.get('intro_source_url'):st.link_button('Nguồn giới thiệu',row['intro_source_url'])
                st.link_button('Nguồn metadata',row['metadata_source_url'])
                value=st.select_slider('Đánh giá của bạn',[1,2,3,4,5],value=ratings.get(book,3),key=f'account_rating_{context}_{book}')
                c1,c2=st.columns(2)
                if c1.button('Lưu đánh giá',key=f'account_save_{context}_{book}'):
                    repository.save_rating(book,value);st.rerun()
                if c2.button('Bỏ đánh giá',disabled=book not in ratings,key=f'account_delete_rating_{context}_{book}'):
                    repository.delete_rating(book);st.rerun()
                labels={'want_to_read':'Muốn đọc','reading':'Đang đọc','finished':'Đã đọc'}
                states=list(labels);state=st.selectbox('Trên kệ',states,index=states.index(shelf.get(book,'want_to_read')),format_func=labels.get,key=f'account_shelf_{context}_{book}')
                c1,c2=st.columns(2)
                if c1.button('Lưu vào kệ',key=f'account_add_{context}_{book}'):repository.save_shelf(book,state);st.rerun()
                if c2.button('Bỏ khỏi kệ',disabled=book not in shelf,key=f'account_remove_{context}_{book}'):repository.delete_shelf(book);st.rerun()

        if page=='Khám phá':
            st.title('Tìm cuốn sách tiếp theo')
            query=st.text_input('Tìm tựa sách hoặc tác giả',key='account_search').strip().casefold()
            matches=[b for b,r in catalogue.items() if query in (r['title']+' '+r['authors']).casefold()]
            if not matches:st.info('Chưa có sách đã duyệt phù hợp. Catalogue nghiên cứu không được dùng thay thế ở chế độ này.')
            pages=max(1,(len(matches)+7)//8);page_number=st.number_input('Trang',1,pages,1,key='account_page_'+query)
            for book in matches[(int(page_number)-1)*8:int(page_number)*8]:card(book,'catalogue')
        elif page=='Gợi ý':
            st.title('Gợi ý cho bạn');st.write(f'Bạn đã lưu {len(ratings)} đánh giá. Cần ít nhất 3 để bắt đầu.')
            if st.button('Tạo và lưu gợi ý',disabled=len(ratings)<3,key='account_generate'):
                result=create_saved_recommendations(repository,engine,catalogue)
                if result['items']:st.success('Đã lưu gợi ý vào lịch sử tài khoản.')
                else:st.info('Chưa có sách đã duyệt phù hợp để gợi ý.')
            latest=repository.history(limit=1)
            if latest:
                st.caption('Lần gợi ý đã lưu gần nhất; đánh giá mới chỉ dùng khi bạn tạo lại gợi ý.')
                for item in latest[0]['items']:
                    # Never render stored explanation text: it may contain a now-withdrawn title.
                    card(item['book_id'],'recommendation',safe_saved_explanation(engine,latest[0]['profile'],item['book_id'],catalogue))
        elif page=='Kệ sách':
            st.title('Kệ sách của bạn')
            section=st.radio('Danh sách',['Muốn đọc','Đang đọc','Đã đọc','Đã đánh giá'],key='account_shelf_filter')
            state={'Muốn đọc':'want_to_read','Đang đọc':'reading','Đã đọc':'finished'}.get(section)
            books=list(ratings) if state is None else [b for b,s in shelf.items() if s==state]
            if not books:st.info('Danh sách này đang trống.')
            for book in books:card(book,'library')
        elif page=='Lịch sử':
            st.title('Lịch sử gợi ý');runs=repository.history()
            if not runs:st.info('Bạn chưa có lần gợi ý nào.')
            for run in runs:
                with st.expander(f"{run['created_at'].strftime('%d/%m/%Y %H:%M')} · {run['support_count']} đánh giá"):
                    for item in run['items']:
                        row=catalogue.get(item['book_id']);st.write(row['title'] if row else 'Thông tin sách hiện chưa sẵn sàng để hiển thị.')
                    if st.button('Xóa lần gợi ý này',key='account_delete_run_'+str(run['run_id'])):repository.delete_run(run['run_id']);st.rerun()
        elif page=='Hồ sơ':
            st.title('Hồ sơ của bạn');name=st.text_input('Tên hiển thị',value=profile['display_name'],max_chars=100,key='account_display_name')
            if st.button('Lưu tên',key='account_save_name'):repository.update_display_name(name);st.rerun()
    except StaleProfileError:
        st.warning('Đánh giá vừa thay đổi. Hãy tạo lại gợi ý để dùng hồ sơ mới nhất.')
    except (StorageError,ValueError,OSError):
        st.error('Chưa thể hoàn tất thao tác. Dữ liệu chưa được lưu một phần; vui lòng thử lại sau.')
