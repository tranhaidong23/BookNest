# Day11 — schema và quyền local, 23/11/2026

Đã tạo migration PostgreSQL, exporter metadata vận hành và kiểm thực thi local. **Chưa kết nối hoặc migration Neon.** Đây là hoàn thành phần local của Day11, không nghiệm thu hệ thống cloud/auth/public.

- `db/migrations/001_initial.sql`: catalogue/provenance, app users, ratings, reading list, recommendation runs/items; RLS và grants tách owner/runtime/reviewer; constraints và khóa ngoại ghép ownership.
- `db/import_books.sql` và `scripts/day11_catalogue_export.py`: chỉ metadata từ Day3 đã khóa hash; không descriptions/ảnh/ratings/users benchmark. Tất cả 10.000 sách pending về quyền metadata; không tự duyệt nguồn.
- **24 kiểm tra PostgreSQL đạt** trong PGlite0.5.17, engine báo18.7. Hai danh tính chỉ thấy dữ liệu riêng; chặn cross-user write/owner change, chặn đọc nguồn chưa duyệt, không context thì deny, transaction context được reset, kiểm constraints và migration lặp. [Bằng chứng](validation.json).
- Import riêng đọc lại **10.000 rows toàn bộ fields khớp**; public catalogue0, toàn bảng cá nhân0, import lặp bị từ chối. [Bằng chứng](import_validation.json), [manifest metadata](catalogue_manifest.json).

Test ban đầu ở khóa ngoại run/user dùng sách đã tồn tại trong run nên nhận lỗi unique trước; đã sửa fixture dùng run rỗng để kiểm chính xác foreign key ownership. Không thay schema nhằm làm yếu kiểm tra. Lượt cuối toàn bộ24 checks đạt; fixtures chỉ là dữ liệu tổng hợp trong DB in-memory, không đưa vào catalogue thật hoặc báo cáo model.

Docker executable có nhưng daemon không chạy; dùng [PostgreSQL nhúng PGlite](https://pglite.dev/docs/about), không đổi dịch vụ hệ thống. Cài một dev dependency npm local có pin/integrity, không lifecycle scripts. Chưa kiểm network login, auth OIDC, Neon pool, nhiều connection đồng thời, cloud permissions hoặc backup/restore. Test SET LOCAL ROLE trong session quản trị không chứng minh runtime login đã được cấp đúng trên Neon.

Runtime chỉ đọc view có gate metadata; intro và ảnh có gate riêng. Việc exporter giữ 10.000 sách là giữ phạm vi local/benchmark, không có nghĩa 10.000 sách đã được public. Context UUID phải do backend xác minh auth và đặt theo transaction, không lấy tùy ý từ client. RLS không thay thế authentication, credentials runtime không được đưa cho browser. [Thiết kế, nguồn và lệnh tái lập](../../../docs/DATABASE.md).

Không commit/push/deploy hoặc sửa ScoutIQ. Phần local Day12–14 có thể tiếp tục; auth/cloud và quyền public phải ghi là chưa kiểm cho tới khi có bằng chứng thực tế.
