"""Local-only demo. Session profiles are not authenticated accounts."""
import os
import sys
from pathlib import Path
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
import streamlit as st
from booknest.recommender import Recommender,load_local_catalogue,explanation
st.set_page_config(page_title='BookNest · Góc sách của bạn',page_icon='📚',layout='wide')
if os.environ.get('BOOKNEST_MODE')=='postgres':
    from app.account import render_account
    render_account();st.stop()
if os.environ.get('BOOKNEST_MODE','local')!='local':
    st.error('Bản công khai chưa được bật. Cần hoàn tất xác thực, database và quyền nội dung trước khi phát hành.');st.stop()

@st.cache_resource
def resources():return Recommender(),load_local_catalogue()

try:engine,catalogue=resources()
except (OSError,ValueError,KeyError):
    st.error('Chưa nạp được dữ liệu đã xác minh. Hãy kiểm tra artifacts local theo README.');st.stop()
for key,value in [('ratings',{}),('shelf',{}),('history',[]),('latest',None)]:
    if key not in st.session_state:st.session_state[key]=value
st.markdown('''<style>
.stApp {background:#f6f7fc;color:#202037} h1,h2,h3 {color:#302249}
[data-testid="stSidebar"] {background:#ece9f7}
.stButton button {border-radius:10px;min-height:42px}
p,li,label {font-size:1rem}
</style>''',unsafe_allow_html=True)
with st.sidebar:
    st.title('📚 BookNest');st.caption('Góc sách dành riêng cho bạn')
    page=st.radio('Đi đến',['Khám phá','Gợi ý cho bạn','Kệ sách','Lịch sử','Về dự án'])
    st.divider();st.metric('Sách đã đánh giá',len(st.session_state.ratings));st.metric('Sách trên kệ',len(st.session_state.shelf))
    st.caption('Hồ sơ riêng của phiên này. Chưa có tài khoản hoặc đồng bộ thiết bị; dữ liệu có thể mất khi phiên kết thúc.')
st.info('Bản thử nghiệm local · Metadata dùng cho nghiên cứu, chưa duyệt phát hành công khai. Mô tả và bìa chưa xác minh được thay bằng nội dung dự phòng.')

def card(book_id,context,reason=None):
    book=catalogue[book_id]
    with st.container(border=True):
        cover,text=st.columns([1,3])
        with cover:st.image(str(ROOT/'app/assets/cover-placeholder.svg'),width='stretch')
        with text:
            st.subheader(book['title']);st.write(book['authors']);st.caption('Chưa có mô tả được xác minh')
            if reason:st.write(reason)
            st.link_button('Xem nguồn thông tin',book['source_url'])
        current=st.session_state.ratings.get(book_id,3)
        rating=st.select_slider('Đánh giá của bạn',options=[1,2,3,4,5],value=current,key=f'rating_{context}_{book_id}')
        st.caption('1: không thích · 3: bình thường · 5: rất thích. Chỉ lưu khi bạn bấm nút.')
        left,right=st.columns(2)
        if left.button('Lưu đánh giá',key=f'save_{context}_{book_id}',width='stretch'):
            st.session_state.ratings[book_id]=int(rating);st.session_state.latest=None;st.rerun()
        if right.button('Bỏ đánh giá',key=f'del_{context}_{book_id}',disabled=book_id not in st.session_state.ratings,width='stretch'):
            st.session_state.ratings.pop(book_id,None);st.session_state.latest=None;st.rerun()
        states=['Muốn đọc','Đang đọc','Đã đọc'];previous=st.session_state.shelf.get(book_id,'Muốn đọc')
        state=st.selectbox('Trạng thái trên kệ',states,index=states.index(previous),key=f'shelf_{context}_{book_id}')
        left,right=st.columns(2)
        if left.button('Lưu vào kệ',key=f'add_{context}_{book_id}',width='stretch'):
            st.session_state.shelf[book_id]=state;st.rerun()
        if right.button('Bỏ khỏi kệ',key=f'remove_{context}_{book_id}',disabled=book_id not in st.session_state.shelf,width='stretch'):
            st.session_state.shelf.pop(book_id,None);st.rerun()

if page=='Khám phá':
    st.title('Cuốn sách tiếp theo của bạn');st.write('Tìm vài cuốn bạn từng đọc, đánh giá thật lòng, rồi khám phá gợi ý dành cho mình.')
    query=st.text_input('Tìm theo tên sách hoặc tác giả',placeholder='Ví dụ: Harry Potter, Jane Austen…').strip().casefold()
    ordered=sorted(catalogue,key=lambda b:(-engine.popularity[engine.mapping[b]],b))
    matches=[b for b in ordered if not query or query in (catalogue[b]['title']+' '+catalogue[b]['authors']).casefold()]
    st.caption(f'{len(matches):,} sách phù hợp · Sắp theo độ phổ biến trong dữ liệu học')
    pages=max(1,(len(matches)+7)//8);number=st.number_input('Trang',min_value=1,max_value=pages,value=1,key='catalogue_page_'+query)
    if not matches:st.info('Chưa tìm thấy sách phù hợp. Thử tên tác giả hoặc từ khóa ngắn hơn.')
    for start in range((int(number)-1)*8,min(int(number)*8,len(matches)),2):
        for col,b in zip(st.columns(2),matches[start:start+2]):
            with col:card(b,'catalogue')
elif page=='Gợi ý cho bạn':
    st.title('Một góc đọc mới, từ sở thích của bạn');count=len(st.session_state.ratings)
    st.write(f'Bạn đã đánh giá {count} cuốn sách. Hãy bắt đầu với ít nhất 3 cuốn; 5–10 đánh giá sẽ cung cấp thêm thông tin.')
    if st.button('Tìm 10 gợi ý',type='primary',disabled=count<3):
        profile=sorted(st.session_state.ratings.items());result=engine.recommend(profile)
        result['created_at']=datetime.now().isoformat(timespec='seconds');result['profile']=profile
        st.session_state.latest=result;st.session_state.history.insert(0,result);st.session_state.history=st.session_state.history[:20]
    result=st.session_state.latest
    if result:
        if result['fallback']:st.info('Chưa tìm được liên hệ đủ mạnh từ các sách bạn thích. Dưới đây là những lựa chọn phổ biến để bạn khám phá.')
        for i in range(0,len(result['items']),2):
            for col,item in zip(st.columns(2),result['items'][i:i+2]):
                with col:card(item['book_id'],'recommendation',explanation(item,catalogue))
    elif count>=3:st.caption('Bấm tìm gợi ý để sử dụng các đánh giá hiện tại. Các sách bạn đã đánh giá sẽ được loại khỏi danh sách.')
elif page=='Kệ sách':
    st.title('Kệ sách của phiên này');selected=st.radio('Xem',['Muốn đọc','Đang đọc','Đã đọc','Đã đánh giá'],horizontal=True)
    books=list(st.session_state.ratings) if selected=='Đã đánh giá' else [b for b,state in st.session_state.shelf.items() if state==selected]
    if not books:st.info('Kệ này còn trống. Tìm một cuốn sách ở mục Khám phá để bắt đầu.')
    for b in books:card(b,'library')
elif page=='Lịch sử':
    st.title('Những lần khám phá gần đây');st.caption('Lưu tối đa 20 lần gợi ý trong phiên này; thay đổi đánh giá không sửa lại lịch sử cũ.')
    if not st.session_state.history:st.info('Bạn chưa tạo gợi ý nào.')
    for index,run in enumerate(st.session_state.history):
        with st.expander(f"{run['created_at'].replace('T',' ')} · {run['support_count']} đánh giá",expanded=index==0):
            for item in run['items']:
                st.write(catalogue[item['book_id']]['title']);st.caption(explanation(item,catalogue))
elif page=='Về dự án':
    st.title('BookNest và cách gợi ý sách')
    st.write('BookNest tìm liên hệ giữa các sách được những người đọc khác đánh giá cao. Các đánh giá của bạn giúp chọn những liên hệ phù hợp. Điểm liên hệ không phải xác suất bạn sẽ thích sách.')
    st.write('Thử nghiệm offline với 5 đánh giá ban đầu: Item-KNN đạt NDCG@10 0,4624; danh sách phổ biến đạt 0,2489. Đây là kết quả trên Goodbooks-10k, chưa phải kiểm nghiệm với người dùng website thực tế.')
    st.caption('Nguồn benchmark: Goodbooks-10k · Mô hình chỉ học train · Cấu hình khóa trước test · Không sử dụng AI để bịa cốt truyện hoặc review.')
    st.link_button('Nguồn dữ liệu Goodbooks-10k','https://github.com/zygmuntz/goodbooks-10k')
