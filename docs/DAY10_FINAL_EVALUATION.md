# Day10 — khóa cấu hình trước test, 23/11/2026

Người dùng đã cho phép tiếp tục qua các mốc local. Mốc này mở test lần đầu để đánh giá chất lượng, sau khi lưu lock. Giữ protocol v0.1, split v1 và mọi model train-only đã fit; không refit hoặc tuning bằng test.

Mô hình chính: Item-KNN K200/shrink10 đã chọn bằng NDCG cold-validation5. Đối chứng ranking: popularity, bias lambda50 (cấu hình chọn trong họ Day5), MF16/lambda10 (Day8–9). Global mean là đối chứng dự đoán sao. Không chọn lại model theo kết quả test; không tính RMSE cho popularity/KNN. Không đưa bias10 vào grid test mới.

Chạy cold-test support3/5/10 trên target chung; warm-test dùng profile train, không dùng warm-validation. Candidate đủ catalogue trừ đúng profile được cung cấp, không loại hidden support pool/holdout còn lại. Giữ users không positive trong rating/coverage, loại khỏi macro ranking và báo số. Ranking relevance>=4, Top10 chưa clip, tie book_id; rating predictions clip[1,5]. Báo unseen items và pairs, fallback KNN, coverage, latency theo engine trước.

So sánh chính đã định trước: KNN trừ popularity, cold-test5 NDCG@10 và Recall@10; bootstrap users1.000 seed20261121, percentile95%. Các cấu hình/tình huống/đối chứng còn lại là phân tích bổ sung, không dùng để chọn model hoặc tuyên bố nhiều kiểm định đều có mức tin cậy đồng thời95%. CI offline chỉ phản ánh tái lấy mẫu users trong dataset, không chứng minh causal/online hoặc tổng quát sang người dùng thực tế.

`scripts/day10_evaluate.py --lock` chỉ đọc validation/model manifests và các model đã chọn, ghi `reports/day10/final_20261123/selection_lock.json` với thời điểm UTC, lựa chọn, protocol, hashes model/code. Chưa đọc file test. Runner yêu cầu lock và xác minh mọi hash trước khi mở input test; ghi `test_access.json` trước đọc test. Không sửa loader validation Day5. Allowlist Day10 riêng chỉ gồm train, catalogue, warm_test, cold_test_support và cold_test_target. Runner không có hàm fit.

Đầu ra mới ở data/processed/day10_final_v1, không ghi vào artifacts cũ. Reuse evaluator đã kiểm từ Day5/6/8, đổi thư mục output trong process Day10; không sửa source cũ. Per-user metrics và Top10 để audit; không ghi toàn bộ raw rating predictions. Verifier riêng tính metrics từ saved Top10 và target, kiểm selected KNN cold5 bằng cộng cạnh độc lập. Nếu phát hiện lỗi sau mở test, phải ghi rõ test đã được xem; không lặng lẽ đổi protocol/grid hoặc gọi test mới là độc lập.

Không thay raw/catalogue/split, không truy cập cloud, không commit/push/deploy. Sau Day10 tiếp tục phần local Day11 theo yêu cầu mới; deployment và quyền public vẫn chưa được phép/nghiệm thu.
