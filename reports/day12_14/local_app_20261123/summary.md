# Day12–14 — bản ứng dụng local đầu tiên, 23/11/2026

Đã thay trang khung Streamlit bằng catalogue tìm kiếm/phân trang, ratings, gợi ý KNN, kệ sách và lịch sử. Phạm vi là **hồ sơ theo session local**, chưa authentication, database persistence hoặc public release. [Hướng dẫn và giới hạn](../../../docs/LOCAL_DEMO.md).

Engine serving chỉ load graph/popularity/IDs Day6 đã kiểm hash, không fit hoặc dùng test. Đối chiếu5.342 hồ sơ validation: toàn bộ Top10/fallback khớp artifacts cũ; [serving_validation.json](serving_validation.json). Giải thích lấy đúng support books có contribution dương; fallback nói rõ popularity, không AI text hoặc review giả.

47 Python tests đạt tại mốc triển khai:42 cũ+5 mới. AppTest đã thực thi tìm kiếm rỗng, lưu3 ratings, lưu kệ, tạo10 gợi ý không trùng seen, giữ lịch sử cũ khi đổi ratings, hai session riêng và guard public mode. Session isolation không được gọi là auth/ownership giữa tài khoản thật. Trạng thái lưu hoàn toàn trong phiên, chưa ghi vào schema PostgreSQL đã tạo ở Day11.

10.000 metadata local, chưa duyệt public; không đọc/hiển thị description nguồn, dùng thông báo thiếu mô tả và SVG placeholder tự tạo. Không gọi missing rating là0, slider mặc định chưa lưu; chỉ nút Lưu đánh giá tạo rating. Lịch sử tối đa20, snapshot không bị sửa lại khi đổi profile. Không tự loại want-to-read khỏi gợi ý vì chưa phải rating/seen theo protocol.

Server local từng trả HTTP200 trên127.0.0.1:8501. **Chưa visual QA**: browser host không khả dụng; Computer Use Windows buộc dừng khi không xác định chắc URL Chrome. Không có screenshot, không kiểm mobile/keyboard thực tế hoặc tải nhiều phiên thật. AppTest không thay thế những bằng chứng này.

Không deploy/cloud/Neon/OIDC, không commit/push hoặc sửa ScoutIQ. Tiếp tục backend persistence và các phần local cần thiết; ghi rõ các cổng cloud/auth/public quyền vẫn chưa hoàn tất.
