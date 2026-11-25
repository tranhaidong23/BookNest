# Day12–14 — identity policy và broker, 23/11/2026

Đã thêm backend phân giải danh tính OIDC đã được Streamlit xác minh thành UUID ứng dụng, role broker riêng và migration003. **Chưa gọi OIDC provider hoặc đăng nhập thật; UI chưa nối backend này.** [Thiết kế và giới hạn](../../../docs/AUTHENTICATION.md).

59 Python tests đạt.8 checks PostgreSQL native/SCRAM đạt; [validation.json](validation.json). Fixtures synthetic, ba danh tính dự kiến,8 lần provision đồng thời cùng danh tính không trùng tài khoản. Broker không đọc dữ liệu cá nhân/source text, không sửa/xóa identity, lookup bị scope theo issuer/sub trong transaction. Tên ứng dụng đã sửa không bị provider name ghi đè.

Identity dùng issuer/sub, email không làm khóa. Claims gate từ chối phiên không đăng nhập, sai issuer/audience/authorized party, thiếu sub, thời gian không hữu hạn/hết hạn/quá tuổi8giờ. Caller phải truyền st.user do framework xác minh, không payload tự decode. Bootstrap kiểm claims trước database và chỉ cho DB loopback, ẩn DSN khỏi config repr. Nó không phải standalone JWT verifier hoặc bằng chứng hoàn thành authentication end-to-end.

Migration001/002, model artifacts và test results nguyên. Fixture chỉ áp dụng migration003 vào cluster tạm mới; không services/DB hiện có hoặc Neon. Không credentials thật/log/argv, không public/deploy/commit/push/ScoutIQ. Tiếp UI/repository integration và kiểm flow; những việc phụ thuộc provider/cloud còn chưa thực hiện.
