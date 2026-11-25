# Phạm vi đề xuất cho commit đầu ngày25 tháng11 năm2026

Mục đích là công khai mã nguồn và bằng chứng tổng hợp của đồ án, không phát hành catalogue sản phẩm hoặc dataset. Chưa commit/push; danh sách staged phải được người dùng cho phép trước hai thao tác này.

## Phân loại đã rà

- Mã nguồn app/booknest/scripts/tests, SQL và tools/db-test: thuật toán, ứng dụng và fixtures tổng hợp. Không có model arrays, raw books/ratings hay archive nguồn trong vùng này.
- Reports JSON/CSV: metrics, số đếm/quantiles, decisions, URLs/revisions/hash và môi trường. Kiểm các trường dễ nhầm như original_title trong audit/EDA cho thấy đây là missing-count590, không phải một cột nội dung catalogue.
- `reports/day01/descriptions_20261119/matches.json`: có bảng tựa/tác giả/publisher/ISBN từ nguồn đối chiếu; giữ local bằng .gitignore, không sửa file gốc hoặc hashes.
- Reports về nguồn có ví dụ tên tác phẩm, liên kết và nhận định do dự án viết; không đóng gói cache HTML/XML/wikitext hoặc các đoạn mô tả ứng viên từ data/. Đây là phạm vi tài liệu nghiên cứu, không phê duyệt metadata cho giao diện public.
- Data/artifacts/môi trường/editor/secrets đều bị Git ignore; .streamlit/config.toml chỉ chứa cấu hình local/theme, không secrets.

Không thêm license cho code khi người dùng chưa chọn. Không coi việc source text nằm trong vùng ignored là đã có quyền dùng cho dịch/tóm lược qua API. Token scan chỉ kiểm một số mẫu, không bảo đảm phát hiện mọi secret. Quyết định loại bảng metadata giúp giữ nguyên hồ sơ nghiên cứu tại máy mà không cần đưa tất cả lên repo.

README ghi rõ prerequisites và file bị loại. Full benchmark/app tests không chạy đủ trên clone chưa có artifacts; kết quả tests local không được gọi là CI hoặc clean-clone pass. Không thêm workflow CI xanh giả bằng cách bỏ kiểm model.
