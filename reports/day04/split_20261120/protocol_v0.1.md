# Protocol đánh giá v0.1 — thiết kế Day3, 20/11/2026

Đây là quyết định thiết kế trước split/train, không phải kết quả đã chạy. Day4 triển khai và kiểm bất biến, khóa manifest split trước huấn luyện. Thay đổi protocol phải tăng version và ghi lý do trước khi xem test metrics.

## Câu hỏi và phạm vi

Thí nghiệm chính: với 3/5/10 ratings đầu vào, mô hình có cải thiện gợi ý so với popularity trên người dùng chưa tham gia train không? Thí nghiệm warm-start báo riêng, không dùng để chứng minh cold-start. Benchmark giữ 10.000 sách, không lọc theo độ đầy đủ mô tả. Đây là đánh giá offline trên các đánh giá tự nguyện trong Goodbooks, không đại diện mọi người đọc hoặc tác động khi triển khai.

Không có timestamp. Split ngẫu nhiên tái lập, không gọi là temporal hoặc tương lai. Các thống kê EDA toàn dữ liệu đã được xem để kiểm chất lượng/khả thi; đây là giới hạn đã biết. Chúng không được dùng làm feature, popularity, item selection hoặc mục tiêu tối ưu test.

## Phân chia người dùng và interactions

Seed gốc 20261120. Để độc lập thứ tự CSV và phiên bản RNG, xếp theo SHA-256 UTF-8 của `booknest|v0.1|20261120|namespace|user_id|book_id`, ID thập phân không số 0 đầu. Khi xếp users, để book_id rỗng. Nếu hash trùng, phá hòa bằng ID tăng dần. Namespace tách `users`, `cold_support`, `warm_pairs`.

1. Sắp users theo namespace users; lấy floor(0,8*N) làm development users, floor(0,1*N) tiếp làm cold-validation users, phần còn lại làm cold-test users. Không stratify bằng ratings/positive count. Không user nào thuộc hai nhóm.
2. Chỉ development users tham gia học mô hình. Trong mỗi development user, xếp cặp theo warm_pairs: floor(0,1*n) cặp đầu warm-validation, floor(0,1*n) tiếp warm-test, phần còn lại train. Yêu cầu tối thiểu một cặp mỗi holdout và một cặp train; nếu không đủ, đưa user vào train-only và ghi số lượng. Với dữ liệu hiện tại dự kiến không cần loại, phải kiểm khi chạy.
3. Cold users cần ít nhất 11 ratings để có 10 support và ít nhất 1 target. Xếp các cặp theo cold_support, dùng 10 đầu làm support pool; phần còn lại là target chung. Chọn support không nhìn giá trị rating. Support 3/5/10 là các prefix lồng nhau.
4. Khi đánh giá cold ở mức 3 hoặc 5, phần còn lại của pool 10 **không** dùng huấn luyện, tạo hồ sơ hoặc gán relevance; không đưa vào target. Candidate chỉ loại support thực sự đã cung cấp, không loại bằng thông tin ẩn. Những cặp pool chưa cung cấp có thể nằm trong candidate nhưng không được coi là positive target; báo rõ hạn chế này.
5. Cold-validation và cold-test không góp rating nào vào global item factors, similarity, mean, bias, popularity hoặc chọn siêu tham số. Chỉ support của chính user được dùng tạo hồ sơ/fold-in ở lúc chấm. Không cập nhật item factors bằng support/target đó.

V0.1 không refit train+validation trước test, để giữ một mô hình và item universe nhất quán. Validation dùng chọn model/tham số; test chỉ chạy sau khi khóa cấu hình. File test có thể được kiểm ID, số dòng, tính rời nhau và eligibility cơ học; không dùng nhãn test để điều chỉnh thiết kế/model. Nếu phát hiện lỗi sau test, ghi việc test đã được xem và giới hạn kết luận.

## Candidate set và item không có trong train

Rank toàn catalogue 10.000, không negative sampling. Warm-validation/test loại các sách trong train của user đó; không loại thêm bằng holdout còn lại. Cold loại đúng support được cung cấp. Mọi model cùng protocol dùng cùng candidate set. Phá hòa điểm bằng book_id tăng dần.

Item chưa có train vẫn ở catalogue và target. Mô hình không chấm được phải dùng fallback chỉ từ train (định nghĩa cụ thể trước fit), không lặng lẽ bỏ item hoặc target. Báo số item/cặp target chưa thấy trong train và tỷ lệ fallback. Warm user có train; cold user chỉ có support được phép. Missing interaction không có rating 0 và không chứng minh không thích.

## Metrics đã định nghĩa, chưa tính

Relevance nhị phân: target rating >=4. Với user u, R_u là tập target relevant; L_u là Top 10 hợp lệ, không trùng, từ candidate set. User có R_u rỗng không tham gia macro ranking, nhưng vẫn báo số/tỷ lệ và vẫn tham gia RMSE/MAE nếu có target. Không loại user theo việc model có hit.

- Recall@10 = |L_u ∩ R_u| / |R_u|.
- Precision@10 = |L_u ∩ R_u| / 10; nếu ít hơn 10 kết quả, vị trí thiếu tính không hit.
- DCG@10 = tổng từ i=1 đến 10 của 1[L_ui thuộc R_u] / log2(i+1); IDCG tương tự với min(10, |R_u|) relevant ở đầu. NDCG = DCG/IDCG.
- Macro NDCG@10 và Recall@10 là chính: trung bình trên cùng users có positive target cho mọi model. Báo riêng từng support size và từng split.
- RMSE = sqrt(mean((rating-prediction)^2)); MAE = mean(abs(rating-prediction)), micro theo cặp target. Chỉ báo cho model có đầu ra dự đoán sao được định nghĩa; không coi điểm popularity/similarity là số sao.
- Catalogue coverage = số book_id xuất hiện ít nhất một lần trong Top 10 / 10.000, tính trên tất cả users đủ eligibility, kể cả không có positive target; ghi số users.
- Latency: khi có engine, báo p50/p95 thời gian scoring + xếp Top 10 mỗi user, cache đã warm, một tiến trình trên cùng máy; tách thời gian load/train và thời gian mạng. Chưa đo.

Item chưa được chấm được xem là unjudged: không có hit quan sát, không gán nhãn dislike. Full-catalogue ranking vì thế đo khả năng truy hồi positive đã quan sát, không phải accuracy toàn bộ sở thích. Báo selection bias và incompleteness của ground truth.

Chọn cấu hình theo macro NDCG@10 cold-validation support=5; Recall@10 làm tie-break, sau đó chi phí suy luận/độ đơn giản. Support 3/10 và warm chỉ là phân tích bổ sung, không chọn lại theo test. Khoảng tin cậy dự kiến: paired bootstrap users 1.000 lần, seed riêng 20261121, percentile 95% cho chênh lệch so với popularity; không bootstrap từng rating như mẫu độc lập.

## Đặc trưng và điều kiện kiểm Day4

V0.1 chỉ dùng train ratings và support được phép. Không dùng average_rating, ratings_count, reviews, similar_books, popular_shelves hoặc tag count toàn nguồn. Tags và descriptions ở derived chưa được phép làm feature; normalization không loại bỏ nguy cơ leakage. To-read giữ riêng, không làm negative.

Day4 phải kiểm: hashes nguồn; bao phủ/phân hoạch đầy đủ interactions; cặp train/val/test rời nhau; cold users rời train và nhau; support/target rời và support lồng nhau; target chung 3/5/10; split không đổi khi đảo thứ tự input; thay giá trị holdout không đổi assignment; không chọn support theo rating; ID/nhãn giữ nguyên; tally eligibility và unseen items; ghi seed/namespace/hash output. Chưa có split artifacts hoặc model metrics tại Day3.
