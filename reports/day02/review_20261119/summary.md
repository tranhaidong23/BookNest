# Day2 — triage mô tả và chính sách catalogue

Ngày 19/11/2026. Đã rà toàn bộ hàng đợi 358: kiểm tự động lại 315 text rỗng, Codex agent đọc 43 text không rỗng và ghi quyết định. Không phải đánh giá độc lập của con người; không kiểm nghĩa toàn bộ 10.000 text. Không tạo giới thiệu hay sửa raw.

| Trạng thái mới | Sách |
|---|---:|
| Thiếu nguồn mô tả | 315 |
| Đóng cờ tựa, chưa duyệt nội dung/quyền | 9 |
| Đoạn ngắn cần thêm bằng chứng | 22 |
| Loại text placeholder khỏi nguồn giới thiệu | 1 |
| Giữ chờ mô tả đúng tập/edition vì text trùng | 11 |
| Tổng | 358 |

43 quyết định có lý do cụ thể; 315 rỗng được phân loại tự động, không gọi là đã đọc review thủ công. Cả 358 XML được đọc lại, kiểm hash member, hash text và ID edition/work với bằng chứng audit trước. Chi tiết: `data/processed/review_20261119/review_decisions.json` (không chứa toàn văn text), [review_audit.json](review_audit.json). Raw 7 file và ZIP khớp manifest trước/sau.

**Chốt benchmark local giữ đủ 10.000 sách.** Sau xử lý cờ tựa, 9.651 sách nằm trong tập ứng viên sàng lọc text; 349 mô tả còn giữ lại để bổ sung/kiểm nguồn. 9.651 không phải số text đã đủ căn cứ viết 60–100 từ, không là catalogue public đã duyệt và không tự dùng làm bộ lọc thí nghiệm.

Đã đo tác động **giả định**, không sửa dữ liệu: nếu lọc ratings theo 9.651 ứng viên thì giữ 5.885.338/5.976.479 ratings (98,475%), bỏ 91.141; vẫn có 53.424 users và không ai mất toàn bộ ratings. Điều này không chứng minh lọc vô hại: nhóm sách/ngôn ngữ và số support của từng người vẫn thay đổi. Không dùng các số này làm quality metrics. Phân bố ngôn ngữ của 349 sách giữ chờ có trong JSON; chưa xác định ngôn ngữ từ nội dung.

Quy tắc ở [CATALOGUE_POLICY.md](../../../docs/CATALOGUE_POLICY.md): benchmark không phụ thuộc mô tả; giữ book_id/ratings, null khi thiếu; metadata derived có provenance; không gộp các tập vì text trùng; source bổ sung phải đúng scope edition/work. Chưa chạy cleaning Day3 hoặc chia train/test.

Vừa đọc thêm [Google Books branding](https://developers.google.com/books/branding): yêu cầu attribution/liên kết và không sửa nội dung trả qua API. Chưa coi nguồn này được duyệt cho AI dịch/tóm lược. [Open Library licensing](https://openlibrary.org/developers/licensing) cũng chưa giải quyết quyền của mọi đóng góp. Không nguồn nào được tự duyệt toàn bộ mô tả/bìa public trong lượt này; điều kiện nguồn là blocker public, không chặn chuẩn bị local.

## File và kiểm chứng

- Mới: scripts/review_description_queue.py, tests/test_review_queue.py, docs/CATALOGUE_POLICY.md, báo cáo/JSON mốc này và 2 artifact trong data/processed/review_20261119.
- Script chỉ đọc local, xuất quyết định/ảnh hưởng giả định; không tải data, gọi AI, sửa app, train, commit/push/deploy hoặc đụng ScoutIQ.
- Lệnh tái lập: `.venv\Scripts\python.exe -B scripts/review_description_queue.py`. Chạy lại cập nhật báo cáo mốc này; báo cáo trước giữ nguyên.
- Kiểm mới: xem validation.json cùng thư mục, gồm output tests và hash. Kết quả 7 tests của lượt trước vẫn là lịch sử, không được dùng thay kết quả mới.

## Phản biện và bước tiếp

Vì sao không xóa 349 sách? Thiếu synopsis không làm mất tính hợp lệ của rating; xóa sẽ đổi benchmark và có thể thiên lệch. Vì sao không cho AI viết từ text ngắn? Có thể thêm cốt truyện hoặc thông tin không có nguồn để đủ số từ. Vì sao text trùng không deduplicate book_id? Các tập khác nhau có thể bị sao chép mô tả, ratings vẫn thuộc các tác phẩm khác.

Triage và policy local đã xong ở mốc này. Tiếp theo có thể chuẩn bị derived/EDA/protocol theo policy, đồng thời giải quyết nguồn/quyền cho catalogue sản phẩm; chưa gọi Day2 public-ready, chưa tự chạy giai đoạn tiếp theo.
