# Authentication boundary — local preparation, 23/11/2026

Đã có `booknest/identity.py`, `booknest/auth_backend.py`, migration003 identity broker và UI `app/account.py` gọi bootstrap từ `st.user`. **Chưa đăng ký OIDC client, chưa đăng nhập qua provider và chưa xác minh cookie/redirect/logout trên trình duyệt**. Không có mật khẩu/credentials mặc định hoặc cơ chế giả đăng nhập bằng UUID form. UI kiểm thiếu secrets thì dừng; 11 kiểm tra UI/database dùng danh tính tiêm trong test, không thay xác minh provider.

## Nguồn danh tính

Caller chỉ truyền `st.user` do Streamlit đã xử lý OIDC, không truyền request JSON/query params hoặc payload JWT tự decode chưa xác minh. Theo [st.login](https://docs.streamlit.io/develop/api-reference/user/st.login), Streamlit thực hiện luồng OIDC và đưa claims vào st.user. Module BookNest không thay signature/nonce/authorization-code verification của framework.

BookNest kiểm thêm `is_logged_in is True`, issuer khớp cấu hình chính xác, subject không rỗng, audience có đúng client_id; nhiều audience cần azp đúng. Kiểm exp chưa hết hạn, iat hợp lệ, optional nbf, giá trị thời gian hữu hạn; chấp nhận clock skew tối đa60 giây cho iat/nbf tương lai. Giới hạn tuổi phiên8 giờ là lựa chọn dự án hiện tại, có thể thay bằng cấu hình trước nghiệm thu auth. Expiry kiểm mỗi lần bootstrap, không dựa riêng cookie còn tồn tại. [st.user docs](https://docs.streamlit.io/develop/api-reference/user/st.user) lưu ý ứng dụng cần kiểm thời hạn claims; đây là lý do thêm gate này.

Tài khoản được khóa bằng `(issuer,subject)`, không bằng email, display name hoặc UUID từ client. Email thay đổi không tạo người dùng mới; cùng sub ở issuer khác là tài khoản khác. Tên từ provider chỉ làm tên ban đầu; đăng nhập lại không ghi đè tên người dùng đã sửa.

## Phân quyền database

Migration003 tạo `booknest_identity_broker` NOLOGIN, không elevated flags. Login cụ thể được quản trị cấp riêng sau, chưa tạo trên Neon. Broker chỉ có SELECT một số cột app_users và INSERT; không UPDATE/DELETE identities, không đọc ratings/shelf/run/source text. RLS lookup/provision giới hạn đúng issuer/sub được backend đặt transaction-local. Không có context thì không thấy identities.

`resolve_identity` mở fresh broker connection, từ chối migration owner/elevated role, đặt context theo claims đã kiểm, INSERT ON CONFLICT DO NOTHING rồi resolve UUID. Concurrency dựa unique(issuer,subject), không gộp bằng tên/email. `account_from_streamlit` phân giải UUID rồi trả PostgresRepository dùng **connection runtime riêng**. Không dùng broker để phục vụ dữ liệu người đọc.

Credentials broker vẫn là credentials tin cậy phía server: người có khả năng chạy SQL tùy ý bằng broker có thể khai issuer/sub. RLS không tự xác minh token; không trao credentials hoặc API SQL cho browser. Database không chứng minh OIDC đã đúng chỉ vì resolver trả UUID.

`AccountConfig` giữ issuer/client_id và hai DSN, repr ẩn DSN. `local_connection_factory` chỉ nhận explicit localhost/127.0.0.1/::1, pin hostaddr loopback, từ chối hostaddr ngoài và libpq service. Không cho kết nối cloud ở mốc này; không thử đọc hoặc gửi connection string thật qua chat. Không khởi tạo connection khi claims invalid.

## Bằng chứng

59 Python tests đạt:5 claims-policy tests,3 bootstrap/config tests mới ngoài51 trước. Kiểm logged-out/wrong issuer/audience/multi-audience/exp/NaN/infinity/missing subject, email không làm khóa, không gọi database cho claims invalid và không cho DSN remote.

[8 native PostgreSQL integration checks](../reports/day12_14/identity_20261123/validation.json): resolve lặp cùngUUID;8 concurrent first-login calls tạo đúng1account; khác issuer tách; tên app không bị ghi đè; context broker reset;6 hành động ngoài quyền bị chặn; owner/runtime không provision; tổng đúng3accounts synthetic. PostgreSQL18.6/SCRAM thật, claims là fixtures giả lập có ghi rõ, không test OIDC exchange. Cluster tạm đã dừng/dọn.

## Còn lại

Chọn/configure OIDC provider bằng secrets phía server, quản lý redirect URI/cookie secret, kiểm UI login/logout/expired-session thực tế. Repository và quyền catalogue đã nối UI, có bằng chứng local riêng. Cần kiểm hai tài khoản thật và reconnect qua browser, provider revocation/logout across tabs, cookie/CSRF behavior và Neon/TLS/pool trước public. Không tự tạo tài khoản cloud/keys/ủy quyền hoặc deploy. Session demo ở chế độ local vẫn không xác thực.
