# Cách dùng split Day4 — v1

Nguồn duy nhất cho các file dưới: `data/processed/day04_split_v1/`. Kiểm hash theo `reports/day04/split_20261120/manifest.json` trước dùng. Protocol cố định ở `reports/day04/split_20261120/protocol_v0.1.md`; không sửa snapshot hoặc split sau khi đánh giá model.

| File | Mục đích |
|---|---|
| train.csv | Nguồn duy nhất học global mean/bias/popularity/item factors/similarity |
| warm_validation.csv | Chọn/kiểm trên development users có train; không đưa nhãn vào global fit |
| warm_test.csv | Holdout kết luận cuối warm-start; không dùng tuning |
| cold_validation_support.csv | 10 support mỗi user validation, có support_rank 1–10 |
| cold_validation_target.csv | Target chung cho 3/5/10; dùng đánh giá validation |
| cold_test_support.csv | 10 support mỗi user test; chỉ mở cho giai đoạn test đã khóa cấu hình |
| cold_test_target.csv | Target chung 3/5/10, chỉ dùng kết luận cuối |
| cold_validation_ineligible.csv / cold_test_ineligible.csv | Giữ các cặp cold users không đủ 11 ratings; có thể chỉ có header, không nhập vào train |
| user_groups.csv | Mỗi user thuộc đúng một trong development/cold_validation/cold_test |
| catalogue_ids.csv | Toàn bộ 10.000 book_id, mẫu số coverage và tập candidate gốc |

Mọi file interaction có `user_id,book_id,rating`; support thêm `support_rank`. ID là số nguyên nguồn, không phải index matrix 0-based. Nếu engine tạo index riêng, lưu mapping và kiểm round-trip. Không lấy thứ tự dòng làm timestamp hoặc làm thứ tự support; phải dùng support_rank.

Để tạo hồ sơ k=3/5/10, chỉ lấy support_rank <= k của đúng user. Hàm `support_prefix` trong scripts/split_day04.py thực hiện việc này và trả ba cột interaction. File target giữ nguyên cho mọi k. Không gộp support vào train toàn cục hoặc cập nhật item factors bằng support.

Candidate luôn là catalogue_ids trừ sách đã cung cấp cho mô hình: train của user warm, hoặc đúng k support của user cold. Không loại sách bằng thông tin trong target hoặc các support chưa cung cấp. Không dùng file book_counts.csv Day3 để xếp popularity: file đó thống kê toàn bộ dữ liệu, chứa holdout. Không dùng cả ratings.csv Day3 để fit khi đã có split.

V0.1 chưa refit train+validation trước test. Các file nằm local không có cơ chế phân quyền OS ngăn truy cập test; đây là kỷ luật thí nghiệm được ghi nhận bằng config/run logs. Day4 chỉ kiểm cấu trúc, toàn vẹn nhãn và số user không có positive target, chưa tính performance hoặc chọn model bằng test. Không gọi các kiểm này là đánh giá hiệu quả mô hình.

Tái lập từ nguồn đã xác minh:

```powershell
.venv\Scripts\python.exe -B scripts/split_day04.py
.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

Script tạo split, kiểm lại assignment khi đảo toàn bộ input và thay tất cả rating, đọc lại từng CSV để so nhãn/ID, rồi khóa manifest. Lần chạy lại phải cho cùng payload; nếu khác thì dừng, không ghi đè. Thay protocol/seed/input phải version mới, báo rõ nếu test đã được xem.
