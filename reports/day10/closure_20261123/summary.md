# Chốt Day10 sau rà soát ngày23 tháng11 năm2026

Theo yêu cầu quay lại hoàn tất Day10, đã đối chiếu trạng thái hiện tại với [thiết kế đánh giá](../../../docs/DAY10_FINAL_EVALUATION.md), [báo cáo kết quả](../final_20261123/summary.md), selection lock, journal mở test và bằng chứng audit. **Day10 đã hoàn tất trong phạm vi protocol đã khóa.** Không cần huấn luyện lại hoặc chọn cấu hình mới.

## Bằng chứng vừa kiểm

[integrity.json](integrity.json) ghi88 hashes trong khóa cấu hình,5input hashes và32output hashes đều khớp; metrics và evaluator khớp manifest; verifier và manifest khớp bằng chứng audit trước. Lock vẫn có trước lần mở test đầu. Đủ bốn tình huống cold3/5/10 và warm.

Lượt này kiểm tính toàn vẹn, không tính lại toàn bộ metrics hoặc chạy lại tests. Audit trước đã kiểm235.072 danh sách Top10, kiểm độc lập KNN/MF cold5 cho5.343users và rating aggregates MF cold5.42tests là số đạt trước mở test; không nhầm với68tests của toàn dự án ở mốc sau. Giới hạn fullCLI replay và kiểm độc lập các rating metrics còn lại vẫn được giữ trong báo cáo gốc.

## Kết luận để trình bày

| Cold test với5 đánh giá hỗ trợ | Item KNN | Popularity |
|---|---:|---:|
| NDCG@10 | 0,462428 | 0,248938 |
| Recall@10 | 0,065387 | 0,033484 |
| Coverage trên10.000sách | 50,24% | 0,14% |

Item-KNN K200/shrink10 được chọn bằng validation trước test, giữ nguyên cho sản phẩm. Chênh lệch NDCG +0,213490 với CI95%[0,205643;0,221704] theo paired bootstrap đã định trước. Không gọi NDCG là accuracy46,24%; đây là thước đo thứ tự truy hồi các positive đã quan sát. Missing vẫn là chưa được đánh giá, không phải dislike.

Test đã được xem: không dùng kết quả này để tuning tiếp hoặc tuyên bố một holdout chưa mở. Không gán các metrics benchmark cho catalogue sản phẩm đã lọc quyền. Raw/split/model không sửa, không commit/push/deploy hoặc ScoutIQ. Các phần ứng dụng đã làm sau Day10 vẫn giữ nguyên; lượt quay lại này không khởi chạy giai đoạn mới.
