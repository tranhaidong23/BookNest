# Day3 — làm sạch, EDA và thiết kế protocol, 20/11/2026

Đã tạo **derived day03_v2** riêng, giữ benchmark 10.000 sách và toàn bộ 5.976.479 ratings của 53.424 users. Không sửa catalogue v1, raw hoặc cache. Đây là dữ liệu nghiên cứu local, không phải catalogue public. Day3 thực hiện cleaning/EDA/thiết kế; tạo và kiểm split thực tế thuộc Day4, chưa train.

## Làm sạch đã áp dụng

| Hạng mục | Quyết định và kết quả |
|---|---|
| Ratings | Kiểm missing, thang 1–5, ID và cặp trùng/xung đột; giữ byte-identical CSV, không đổi nhãn, không điền cặp chưa chấm |
| To-read | Giữ byte-identical riêng; 2.200 cặp giao ratings vẫn giữ, không coi là lỗi hoặc negative |
| Metadata | Chỉ lấy trường nhận diện và mô tả có provenance; không mang average_rating/ratings_count vào bảng sách derived |
| ISBN | Đọc XML, kiểm cả edition/work và hash từng member, checksum/độ dài; 9.277 ISBN10 và 9.402 ISBN13 hợp lệ; không có ISBN hợp lệ dùng chung trong catalogue này |
| Text | Bỏ markup/script/style, chuẩn hóa whitespace; 315 mô tả trống + 1 placeholder thành null; text còn lại giữ trạng thái review, không tự duyệt feature/public |
| Missing metadata | 590 original_title, 1.084 language_code và 21 năm xuất bản là null; không điền giá trị giả |
| Năm | 31 giá trị không dương giữ nguyên với cờ review, vì có thể là niên đại trước Công nguyên |
| Tags | 999.912 dòng đầu vào; bỏ 6 bản sao giống hệt, cách ly 4 dòng thuộc 2 khóa count xung đột và 6 dòng count âm; còn 999.896 dòng |

File `book_tags_excluded.csv` giữ số dòng nguồn và lý do từng hàng. Khóa xung đột là Goodreads 3/tag 22743 (6066/6065) và 77449/tag 15169 (8/7); không đủ căn cứ chọn count đúng hoặc cộng hai count. Tags join về book_id bằng Goodreads edition ID với kiểm many-to-one. Chưa ánh xạ thể loại: cần allowlist có căn cứ ở bước feature/UI; không coi mọi shelf là genre. Tags đã làm sạch vẫn chưa được phép dùng làm feature do count toàn nguồn có nguy cơ leakage.

Lượt v1 phát hiện sau kiểm tra rằng 5 original_title chỉ chứa khoảng trắng còn là chuỗi. Đã tạo **v2** chuẩn hóa biên chuỗi và chuyển whitespace-only thành null, giữ v1 làm lịch sử và snapshot script v1 ở `../preparation_20261120/prepare_day03_v1.py.txt`. Chỉ dùng `data/processed/day03_v2` cho bước tiếp; không nhầm với catalogue v1 bất biến của Day2.

## EDA và ý nghĩa

| Quan sát toàn dữ liệu | Kết quả | Ý nghĩa |
|---|---:|---|
| Mật độ cặp có rating | 1,1187% | Missing rất nhiều; không gán rating 0 |
| Ratings mỗi user: min / median / max | 19 / 111 / 200 | Mọi user đủ điều kiện cơ học 10 support + ít nhất 1 target; không phải mẫu người dùng mới tự nhiên |
| Ratings mỗi sách: min / median / max | 8 / 248 / 22.806 | Phân phối không đều; cần báo coverage và item fallback |
| Tỷ trọng ratings của top 100 sách | 17,0871% | Popularity là đối chứng quan trọng |
| Rating trung bình mô tả | 3,9199 | Dữ liệu nghiêng về đánh giá cao; đây không phải baseline học từ train |

Phân phối 1–5 sao lần lượt: 124.195; 359.257; 1.370.916; 2.139.018; 1.983.093. Chi tiết và quantiles trong [eda.json](eda.json), [rating_distribution.csv](rating_distribution.csv). Thống kê user/item chi tiết nằm trong data local. Không tính quality metrics hoặc kết luận model hiệu quả từ EDA.

## Protocol v0.1 đã viết trước split/train

[EVALUATION_PROTOCOL.md](../../../docs/EVALUATION_PROTOCOL.md) quy định:

- Users chia 80/10/10 development/cold-validation/cold-test bằng hash có seed, độc lập thứ tự dòng và nhãn rating. Development users có train/warm-validation/warm-test riêng.
- Cold users không xuất hiện trong global train. Support 3/5/10 lồng nhau, 10 support pool và target còn lại chung; chọn support không nhìn rating. User eligibility >=11, không chọn user theo số positive target.
- Ranking toàn 10.000 sách, loại các sách đã cung cấp cho mô hình; giữ item chưa thấy trong train với fallback chỉ từ train. Không loại sách vì thiếu mô tả.
- Relevant target >=4; macro NDCG@10 và Recall@10 là chính. User không có positive target được báo riêng, không có NDCG giả. RMSE/MAE chỉ cho mô hình có dự đoán sao.
- Tuning trên cold-validation support=5, không xem test để chọn cấu hình; không refit train+validation trong v0.1. Warm và support 3/10 báo riêng. Similarity không phải accuracy.

Goodbooks không timestamp: đây là split ngẫu nhiên, không đánh giá thời gian. Users vốn có 19–200 ratings; cold-start là mô phỏng giới hạn đầu vào, không chứng minh hiệu quả onboarding thực tế. EDA đã xem toàn dữ liệu cho kiểm chất lượng/khả thi; không đưa các thống kê đó vào engine. Ranking chỉ truy hồi positive đã quan sát, item chưa chấm không phải dislike. Protocol có ghi rõ cách xử lý support pool chưa cung cấp ở mức 3/5 và giới hạn relevance tương ứng.

## Kiểm chứng và tái lập

19 unittest đạt (14 cũ + 5 mới), bao gồm xung đột tag, ratings sai/trùng, BCE/missing, output bất biến và whitespace-only. Script kiểm raw manifest, ZIP và catalogue v1 trước/sau; XML member hash và identity từng sách; ratings/to-read giữ nguyên. [manifest.json](manifest.json) ghi input/output/script hashes và môi trường. V2 chạy và replay thành công, kiểm lại mọi input/output hash cùng script; bằng chứng tại [validation.json](validation.json).

Lượt replay v1 gặp lỗi bảo vệ manifest vì script đã được sửa sang v2 trong lúc tiến trình cũ còn chạy: hash script thay đổi, output dữ liệu v1 vẫn khớp. Không ghi đè manifest hoặc gọi lượt này thành công. Sau đó v2 chạy/replay với script không đổi đều đạt; v1 giữ lịch sử, không dùng cho bước tiếp.

```powershell
.venv\Scripts\python.exe -B scripts/prepare_day03.py
.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

Script từ chối ghi đè artifact khác payload; thay quy tắc phải version mới. Data/processed bị loại khỏi Git theo policy. Không tải nguồn mới, không sửa app, không AI API/Neon/Render, không commit/push/deploy hoặc thay đổi ScoutIQ.

**Bước tiếp Day4:** triển khai split đúng protocol, kiểm không giao nhau/leakage, tái lập khi đảo input, eligibility/unseen items rồi khóa manifest. Sau đó mới sang baseline ở Day5. Chưa tạo split hoặc huấn luyện tại Day3.
