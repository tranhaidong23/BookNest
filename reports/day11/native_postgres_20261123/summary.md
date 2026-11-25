# Day11 — kiểm PostgreSQL native local bổ sung, 23/11/2026

Đã chạy migration trên **PostgreSQL18.6 cài sẵn trên Windows**, trong cluster tạm riêng dưới `BookNest/data/dev`, chỉ nghe127.0.0.1, cổng ngẫu nhiên còn trống. Không dùng cluster/service hiện có; không kết nối Neon.

Lượt cuối `scripts/verify_native_postgres.py` thoát0, đã dừng server sở hữu và dọn thư mục tạm. [validation.json](validation.json) ghi engine, hash migration/script và kết quả:

- Runtime login thật bằng SCRAM thành công; mật khẩu thử sai bị từ chối.
- Hai UUID thử nghiệm Alice/Bob chỉ thấy rating của mình; không context thì không thấy dữ liệu.
- Trong cùng connection, context transaction-local không còn sau COMMIT; transaction tiếp theo không thấy dữ liệu cá nhân.
- Update rating người khác ảnh hưởng0 rows.
- Năm thao tác bị từ chối: đọc base metadata, sửa auth_subject, insert run cho người khác, SET ROLE sang owner và TRUNCATE.

Đây là bổ sung cho24 checks PGlite và import10.000 rows trước đó, không thay thế hoặc gọi chung thành một số unittest. Fixtures synthetic trong cluster biệt lập, không làm dữ liệu nghiên cứu/website thật.

Lượt sandbox đầu bị pg_ctl chặn tạo restricted token. Lượt có quyền chạy native sau đó đã khởi động server nhưng subprocess giữ PIPE đầu ra của daemon, làm chờ timeout90 giây; đã xác minh postmaster ready và dừng đúng cluster thử bằng pg_ctl. Sửa lifecycle command ghi output vào file riêng và cleanup cả khi start chưa trả về. Lượt chạy lại hoàn tất trong khoảng7 giây; không sửa PostgreSQL services hoặc security settings hệ thống.

Không còn lỗi native lifecycle ở lượt cuối. Chưa kiểm Neon/TLS/connection pool, OIDC, tải đồng thời hoặc nhiều thiết bị. Runtime context vẫn do backend tin cậy đặt, không phải database tự xác minh danh tính cuối. Chưa nối app session demo vào database.
