# Day12–14 — lớp lưu PostgreSQL, 23/11/2026

Đã thêm `booknest/repository.py`: profile/display name, rating CRUD/upsert, kệ CRUD, public catalogue search, lưu/history/xóa recommendation run. Đây là backend thực thi PostgreSQL đã kiểm, **chưa nối vào Streamlit UI hoặc OIDC/Neon**. Demo UI vẫn là session-only.

Mỗi repository gắn với UUID do backend tin cậy phân giải sau authentication; các method không nhận UUID chủ sở hữu tùy ý từ form. Mỗi operation mở connection runtime mới, transaction riêng, kiểm không dùng owner/elevated role, SET context local rồi dùng query tham số hóa. Lỗi PostgreSQL trả thông báo chung, không đưa SQL/DSN/chi tiết tài khoản khác ra UI. Đây không phải cơ chế tự xác minh token; caller có quyền tạo repository vẫn phải chịu trách nhiệm auth.

Migration002 thêm bảng `recommendation_support` có RLS và composite FK run/user để giữ snapshot rating. Không sửa migration001 đã kiểm. Khi lưu run: khóa transaction theo user, đối chiếu profile với ratings hiện tại, rồi lưu run/support/items cùng transaction. Profile đã đổi thì báo stale và không lưu. Bất kỳ item không hợp lệ nào khiến toàn run rollback. Snapshot không có UPDATE grant/API; xóa run sở hữu sẽ cascade support/items.

**51 Python tests đạt**:47 trước+4 input-contract tests mới. **16 kiểm tra tích hợp đạt** qua Psycopg3.3.9 trên PostgreSQL18.6 native, SCRAM runtime login, cluster tạm biệt lập; [validation.json](validation.json):

- Đọc/ghi qua connection mới và repository instance mới; Alice/Bob không trộn dữ liệu.
- Upsert/delete rating không coi missing là0; kệ3 trạng thái lưu bền trong cluster đang chạy.
- Public catalogue chỉ thấy metadata approved; `%`, `_` và SQL-like input không thành wildcard/injection ngoài ý định.
- Không cho repository chạy bằng migration owner hoặc UUID chưa provision.
- Run/items/profile lưu và đọc lại đúng; userB không thấy/xóa run củaA; profile cũ không bị sửa theo rating mới.
- Item cuối pending làm rollback toàn run/support/items, không để records dở dang.
- 8 concurrent writes qua4 worker/fresh connections giữ ownership; không gọi đây là load test hoặc pool test.
- Xóa run cascade đúng; connection mới không mang user context cũ.

Native fixture đã dừng và dọn cluster sau lượt thành công. Không thay dịch vụ/database hiện có, không kết nối cloud. Psycopg binary3.3.9 tải từ PyPI trong .venv và pin requirements; không có credentials thật được ghi vào repo/report/argv. Password fixture ngẫu nhiên chỉ nằm trong process và bootstrap file tạm đã xóa.

Theo [Psycopg transaction docs](https://www.psycopg.org/psycopg3/docs/basic/transactions.html), transaction context quản lý commit/rollback. Implementation dùng connection mới, không pool; chưa chứng minh hành vi Neon/PgBouncer. Còn thiếu auth identity provisioning, UI adapter, catalogue quyền public, idempotency/retry sau mất mạng, pooling, session/device persistence end-to-end và visual QA.

```powershell
.venv\Scripts\python.exe -B -m unittest discover -s tests
.venv\Scripts\python.exe -B scripts/verify_repository.py
```

Script native có thể cần quyền chạy pg_ctl trên Windows; cluster chỉ ở BookNest/data/dev và localhost. Không tự commit/push/deploy hoặc sửa ScoutIQ. Giữ test/model đã khóa nguyên; không dùng kết quả test để chỉnh ranking.
