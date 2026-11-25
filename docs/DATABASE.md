# Database BookNest — Day11 local, 23/11/2026

**Bổ sung Day12–14:** có `booknest/repository.py` và migration002 để lưu support snapshot. [16 kiểm tra integration thực tế](../reports/day12_14/postgres_repository_20261123/summary.md) đạt trên PostgreSQL18.6/SCRAM qua Psycopg3.3.9;51 Python tests đạt. UI chưa nối repository, OIDC/Neon chưa kiểm. Mô tả migration001 phía dưới giữ nguyên; schema mới gồm thêm bảng support có RLS.

Migration ở `db/migrations/001_initial.sql`, importer ở `db/import_books.sql`. Đã thực thi trên PostgreSQL nhúng PGlite0.5.17 (engine tự báo PostgreSQL18.7) và PostgreSQL18.6 native cài sẵn, chưa chạy Neon. Docker executable có nhưng daemon không hoạt động; không tự khởi động Docker hoặc đổi cấu hình hệ thống. Native PostgreSQL không nằm trong PATH, được tìm thấy ở Program Files sau lượt PGlite.

## Ranh giới dữ liệu

`books` chứa metadata vận hành, `book_descriptions` chứa provenance và intro cần review. Không nhập gần sáu triệu ratings benchmark vào database website. `app_users`, `user_ratings`, `reading_list`, `recommendation_runs`, `recommendation_items` chỉ chứa dữ liệu người dùng ứng dụng. Goodbooks user_id không phải tài khoản website. Chưa nhập genres/tags toàn nguồn hoặc thêm chúng vào recommender.

Exporter lấy các trường metadata cho phép từ Day3 v2 đã kiểm hash; không xuất raw descriptions, ảnh, ratings hoặc user IDs benchmark. 10.000 rows đều metadata pending, cover pending/null. Không tự biến matching thành quyền hiển thị.

Ứng dụng chỉ có SELECT trên `public_catalogue`, không có quyền đọc `books`/`book_descriptions` trực tiếp. View chỉ có metadata approved và evidence không rỗng; intro còn cần identity_verified, content_reviewed và rights approved có evidence. Thiếu intro trả “Chưa có mô tả được xác minh”; thiếu quyền ảnh trả NULL để UI dùng placeholder. Evidence URL/flag do người duyệt có trách nhiệm cung cấp, SQL không tự xác minh tính hợp lệ pháp lý. Hiện public view **0 sách**, vì chưa có metadata được duyệt; không lấy việc giữ đủ benchmark làm phép public.

Role `booknest_local_reviewer` chỉ đọc metadata/text nội bộ, không dữ liệu người dùng. Không cấp role này cho ứng dụng public. Cả runtime và reviewer được tạo NOLOGIN; credentials phải được cấp riêng sau khi chốt môi trường. Không có mật khẩu mặc định.

## Ownership và authentication

Runtime là role không sở hữu schema/table, không SUPERUSER/BYPASSRLS/CREATEROLE/CREATEDB. Năm bảng dữ liệu cá nhân bật ENABLE và FORCE RLS; chỉ row có user_id bằng context được đọc/sửa. Không có context thì mặc định không thấy row nào. Users chỉ được sửa display_name, không auth_issuer/subject. Provisioning identity thuộc backend tin cậy sau xác minh OIDC, chưa được triển khai ở Day11.

Khóa ngoại ghép `(run_id,user_id)` ngăn gắn recommendation item sang run người khác, kể cả tự khai owner của item là mình. Ratings1–5, reading state có allowlist, rank1–10, mỗi run không trùng sách; có index user/time cho lịch sử. Runtime không được TRUNCATE hoặc duyệt metadata. Xóa tài khoản bởi quy trình quản trị sẽ cascade dữ liệu cá nhân; chưa triển khai giao diện/quy trình xác nhận xóa.

Mỗi request backend phải nằm trong một transaction:

```sql
BEGIN;
SELECT set_config('booknest.user_id', $1, true);
-- Parameter $1 is the UUID resolved server-side from verified auth identity.
-- Execute parameterized application queries, then COMMIT or ROLLBACK.
COMMIT;
```

Không lấy UUID này từ form/query string/JSON của browser để tin là danh tính. Không giữ context cấp session trong connection pool. Người có credentials runtime và khả năng chạy SQL tùy ý có thể tự SET context; vì vậy RLS này là defense-in-depth cho backend tin cậy, **không phải cơ chế xác thực JWT ở database** hoặc một API SQL an toàn cho client. Không trao database credentials cho browser. Không cấp quyền role migration cho runtime. Những lỗi constraint phải được ánh xạ sang thông báo chung, không lộ chi tiết tài khoản khác.

Theo [PostgreSQL RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html), owner thường bypass RLS, superuser/BYPASSRLS luôn bypass; kiểm quyền phải dùng runtime role. [Neon connection pooling](https://github.com/neondatabase/website/blob/main/content/docs/connect/connection-pooling.md) phân biệt transaction pool với direct connection; migration dùng direct URL. Chưa xác nhận transaction context dưới Neon pool hoặc hành vi nhiều connection bằng test thực tế.

## Chạy và kiểm local

```powershell
npm ci --prefix tools/db-test --ignore-scripts --no-audit --no-fund --cache data/dev/npm-cache
node tools/db-test/verify-schema.mjs
.venv\Scripts\python.exe -B scripts/day11_catalogue_export.py
node tools/db-test/verify-import.mjs
```

[PGlite](https://pglite.dev/docs/about) chạy PostgreSQL dạng WebAssembly local. Dependency pin 0.5.17 và package-lock có integrity, node_modules/cache bị ignore Git. Tests dùng database in-memory biệt lập; không service/network port. Lượt tải npm trong sandbox bị chặn mạng; lượt có quyền mạng cài thành công, không chạy package lifecycle scripts.

24 kiểm tra database với fixtures giả được đánh dấu synthetic, không dùng chúng làm kết quả recommender. Import test riêng nhập 10.000 metadata thật vào database nhúng mới, đọc lại đủ mọi field khớp, public view rỗng, bảng cá nhân rỗng; import lặp bị từ chối để tránh ghi đè quyết định quyền. Migration cũng từ chối chạy lần hai; thay schema cần migration mới, không sửa ngầm database đã triển khai.

## Còn thiếu trước Neon/public

Bổ sung [kiểm native](../reports/day11/native_postgres_20261123/summary.md): cluster tạm riêng, SCRAM login thật/sai, hai identity RLS, reset context sau COMMIT và5 hành động bị cấm đã đạt. Cluster được dừng và dọn sạch; không thay services. Đây là kiểm PostgreSQL local, chưa pool/OIDC/Neon. Chạy bằng `scripts/verify_native_postgres.py`; Windows sandbox có thể cần quyền chạy pg_ctl tạo restricted token.

Chưa kết nối Neon, chưa nghiệm thu role provisioning thực tế, OIDC, TLS, secrets, pooling, tải đồng thời, backup/restore, migration rollback trên dịch vụ, hoặc quyền metadata public. Cần direct database URL được đặt ở môi trường server, không gửi trong chat; mọi áp dụng cloud cần được cho phép rõ. Hiện chỉ có SQL và kiểm local, không đánh dấu Day11 cloud hoàn tất.
