# Day16–17 — diễn tập backup/restore local

23/11/2026. `scripts/verify_backup_restore.py` chạy pg_dump custom-format rồi pg_restore vào database trống khác trong cluster PostgreSQL18.6 tạm. Chỉ dùng dữ liệu tổng hợp:2 identities,6books,1pending description,4ratings,2shelf rows,1run/3support/2items. Không backup dữ liệu cá nhân thật hoặc dữ liệu nghiên cứu ra ngoài máy.

**9 kiểm tra đạt**; [validation và source hashes](validation.json):

- Restore thành công, không ghi đè database nguồn.
- Toàn bộ hàng của các bảng booknest khớp chính xác, kể cả UUID/timestamps/source fields.
- Policy definitions, RLS/FORCE RLS flags và table grants khớp.
- Runtime repository đọc đúng rating/kệ/history riêng của hai identities; snapshot được giữ.
- Metadata pending và mô tả pending vẫn bị cổng public view chặn.
- Không context thì không đọc được ratings; runtime không đọc base metadata/text hoặc SET ROLE owner.
- Người khác không xóa được run; chủ xóa được và support/items cascade; database nguồn vẫn còn run.

Archive chỉ ở thư mục tạm data/dev và đã xóa; cluster đã dừng/dọn. Hash archive trong validation là bằng chứng lần diễn tập, không phải file backup hiện còn dùng để phục hồi.

## Giới hạn và quyết định

Roles đã tồn tại trong cùng cluster. pg_dump database này không phải bản sao đầy đủ cluster/roles/credentials; **chưa kiểm khôi phục roles sang cluster/máy mới**, rotation secrets, quyền filesystem, restore Neon, PITR/RPO/RTO hoặc mất toàn bộ máy. So sánh table grants và kiểm runtime là bằng chứng cụ thể; không gọi đó là audit toàn bộ security settings của PostgreSQL.

Không thay schema hoặc model.68 Python tests là kết quả mốc hiệu năng ngay trước; không chạy lại suite cho riêng script diễn tập này. Các phần còn thiếu được ghi ở docs/LOCAL_OPERATIONS.md. Tiếp báo cáo/slide có dẫn chứng và các kiểm tái lập cần thiết; cloud/OIDC/public vẫn chưa nghiệm thu.
