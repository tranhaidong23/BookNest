# Day15 — công cụ nội dung có nguồn, phần local

23/11/2026. Đã tạo `booknest/content_review.py`, CLI `scripts/prepare_content_review.py` và [rubric/quy trình](../../../docs/CONTENT_REVIEW.md). Đây là chuẩn bị prompt và kiểm cấu trúc bản nháp offline, chưa gọi AI/provider hoặc đánh giá chất lượng văn bản thật.

## Đã thực hiện

Packet kiểm book ID, scope work/edition, source URL/revision/entity, SHA-256 text UTF-8 và các đoạn trích bằng offset chính xác. Prompt tách chỉ dẫn khỏi dữ liệu nguồn, yêu cầu tối đa120 từ, mỗi câu gắn evidence IDs và không thêm dữ kiện thiếu căn cứ. Draft được kiểm schema, giới hạn và reference; luôn giữ pending/needs_human_review, không tự bật identity/content/rights approval.

CLI chỉ tạo file mới trong data/dev; từ chối ghi đè hoặc xuất ngoài vùng này. Không ghi database, sửa catalogue hoặc gửi nguồn ra mạng. Chưa có packet thực được duyệt cho provider.

## Bằng chứng

- **68 Python tests đạt**, gồm5 tests Day15: hash/offset, phân tách nguồn không tin cậy, reference/giới hạn, không suy semantic/rights approval, CLI tạo file và chặn ghi đè/ngoài vùng. `unit_validation.json` ghi hash bộ tests tại lần chạy cuối.
- **8 kiểm tra PostgreSQL native đạt**: pending fallback; identity+content chưa đủ quyền; đủ ba cổng mới hiện intro/source; rút rights hoặc content review trở lại fallback; bìa duyệt độc lập; rút metadata ẩn toàn record. [Validation](validation.json) ghi hashes tại thời điểm kiểm database, trước khi bổ sung test CLI.
- Cluster tạm đã dừng/dọn. Mọi approved row trong kiểm tra là dữ liệu tổng hợp, không có mô tả thực nào được cấp quyền.

## Chưa xác minh

Không đo factual accuracy/hallucination/tiếng Việt vì chưa chạy model trên mẫu thực có quyền. Câu bịa dẫn ID hợp lệ vẫn có thể qua kiểm cấu trúc; test chủ động thể hiện giới hạn này. Prompt chưa được kiểm khả năng chống injection với provider. Rubric cần người kiểm ý nghĩa/identity và bằng chứng quyền; URL tồn tại không chứng minh quyền.

Day15 mới hoàn tất phần công cụ/rubric local, chưa nghiệm thu AI sản phẩm. Các phần tiếp theo có thể làm local: Day16–17 hiệu năng engine, kiểm hồi quy và phương án vận hành; deploy/cloud/provider vẫn chưa được phép. Raw, catalogue, split và mô hình không thay; không tuning sau test, không commit/push/deploy/ScoutIQ.
