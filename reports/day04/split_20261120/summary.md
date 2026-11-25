# Day4 — split đã tạo và khóa manifest, 20/11/2026

Đã thực thi protocol v0.1 trên derived day03_v2, tạo `data/processed/day04_split_v1/` và khóa [manifest.json](manifest.json). **Toàn bộ 5.976.479 ratings được phân hoạch, ID/nhãn giữ nguyên, không trùng cặp giữa các phần.** Chưa fit model, chưa tạo prediction hoặc quality metrics.

## Các tập dữ liệu

Users được chia bằng SHA-256 theo seed 20261120: 42.739 development, 5.342 cold-validation và 5.343 cold-test. Hai nhóm cold không có bất kỳ rating nào trong global train. Warm holdouts nằm trong nhóm development.

| Tập | Ratings | Users |
|---|---:|---:|
| Train | 3.863.209 | 42.739 |
| Warm-validation | 458.825 | 42.739 |
| Warm-test | 458.825 | 42.739 |
| Cold-validation support pool | 53.420 | 5.342 |
| Cold-validation target | 545.103 | 5.342 |
| Cold-test support pool | 53.430 | 5.343 |
| Cold-test target | 543.667 | 5.343 |
| Cold ineligible, cả hai nhóm | 0 | 0 |

Train có đủ 10.000 sách; không có item target chưa thấy trong train ở split này. Không có development user train-only; mọi cold user đủ >=11 ratings. Không dựa trên positive count để chọn/loại user.

Support pool có rank 1–10 theo hash. Các profile 3/5/10 lấy prefix theo rank, lồng nhau và dùng chung file target. Ở mức 3/5, support chưa cung cấp không được dùng cho profile hoặc làm positive target, cũng không được loại khỏi candidate bằng thông tin ẩn. Đây là giới hạn relevance đã ghi trước split.

## Kiểm tra đã chạy

- 24 unittest đạt: 19 cũ chạy lại + 5 mới về công thức hash/floor độc lập, support lồng nhau, bất biến theo thứ tự/nhãn, cold thiếu dữ liệu không lọt train, cặp trùng bị từ chối.
- Kiểm phân hoạch đủ toàn bộ interactions, cặp duy nhất, nhãn/ID bằng nguồn; mỗi user chỉ một nhóm, cold users rời train.
- Tạo lại assignment trên **toàn bộ input đảo ngược và thay mọi rating bằng 6-rating**: assignment không đổi. Không thay hoặc ghi các nhãn nhiễu này vào split; đây là dữ liệu tạm trong RAM để kiểm thuật toán.
- Đọc lại từng CSV xuất ra, so mọi ID/rating/support_rank với kết quả chuẩn; support/target rời nhau, prefix đủ 3/5/10, target chung qua ba mức.
- Kiểm raw manifest, input/output Day3, ZIP, catalogue v1 và protocol hashes trước/sau; không sửa nguồn. [validation.json](validation.json) kiểm lại hashes của 11 file split, audit, snapshot protocol và script.

Đã kiểm khả năng tái tạo **assignment** bằng lượt tính lại toàn dữ liệu; chưa chạy toàn bộ CLI lần thứ hai sau khi xuất file. Guard từ chối payload khác được dùng từ Day3 và có test. Tái lập không được báo quá phạm vi kiểm đã thực hiện.

## Quyết định diễn giải

Số user không có positive target (rating >=4): warm-validation 229, warm-test 196; cold-validation 1, cold-test 1. Đây là thống kê eligibility đã quy định, không phải metric hiệu quả. Giữ các user đó trong dữ liệu; không tham gia macro ranking nhưng vẫn thuộc đánh giá sao/coverage theo protocol. Không thay seed hoặc chọn lại split để làm đẹp số liệu.

Đây là **cold-user**, không phải cold-item: toàn bộ sách có trong train. Goodbooks không timestamp, không gọi split này là đánh giá theo thời gian. Người dùng gốc vốn có nhiều ratings, nên 3/5/10 là mô phỏng giới hạn thông tin đầu vào. Test labels chỉ được đọc để kiểm toàn vẹn và thống kê cơ học; chưa dùng chọn model/siêu tham số. File test local không có khóa truy cập OS riêng, cần tuân thủ log thí nghiệm.

## Dùng ở Day5

Đọc [SPLIT_USAGE.md](../../../docs/SPLIT_USAGE.md) và [snapshot protocol](protocol_v0.1.md). **Chỉ train.csv được dùng tính popularity/mean/bias/item factors/similarity.** Không fit toàn bộ ratings.csv hoặc dùng book_counts.csv Day3 vì chứa holdout. Tuning trên cold-validation support=5; test chờ khóa cấu hình. Rank cùng 10.000 candidates trừ sách đã cung cấp theo protocol.

```powershell
.venv\Scripts\python.exe -B scripts/split_day04.py
.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

Day4 hoàn tất split và kiểm tra. **Bước tiếp Day5:** định nghĩa và triển khai baselines/metrics validation, không tự mở test để tối ưu. Chưa triển khai Day5 trong lượt này. Không đổi raw/catalogue v1, không AI/DB/UI/cloud, không commit/push/deploy hoặc sửa ScoutIQ. Quyền public nội dung vẫn là backlog riêng.
