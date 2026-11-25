# Day5 — baselines và validation, 23/11/2026

**Đã fit baselines chỉ từ 3.863.209 train ratings và đo validation. Popularity vượt rõ baseline bias về ranking; bias cải thiện dự đoán sao so với global mean.** Không đọc file test hoặc tính test performance; chưa Item-KNN/MF. Kết quả không chứng minh hệ thống đã cá nhân hóa tốt.

Định nghĩa/grid được ghi trước chạy tại [DAY05_BASELINES.md](../../../docs/DAY05_BASELINES.md). Popularity đếm tất cả rating train, không dùng rating count toàn nguồn. Mean là trung bình train. Bias tối ưu squared error có ridge, 10 vòng user/item updates, lambda 10 và 50; cold bias chỉ tính từ support của chính user, không cập nhật item. Đã kiểm objective train không tăng. Dự đoán sao clip [1,5], ranking dùng điểm chưa clip và book_id để phá hòa. Không đổi protocol/split v0.1.

## Kết quả chính: cold-validation, 5 support

5.342 users, 545.103 target ratings. Ranking macro tính trên 5.341 users có positive target; 1 user còn lại vẫn giữ trong rating metrics và coverage.

| Baseline | NDCG@10 | Recall@10 | Precision@10 | Coverage | RMSE | MAE |
|---|---:|---:|---:|---:|---:|---:|
| Popularity | 0,255947 | 0,034853 | 0,237559 | 0,13% (13 sách) | — | — |
| Global mean | — | — | — | — | 0,987718 | 0,771146 |
| Bias lambda 10 | 0,006474 | 0,000841 | 0,005916 | 0,11% (11 sách) | 0,904851 | 0,721308 |
| Bias lambda 50 | 0,017337 | 0,002525 | 0,017731 | 0,11% (11 sách) | 0,935507 | 0,744891 |

Theo tiêu chí NDCG@10 đã chốt, lambda 50 được chọn **trong họ bias**; nó vẫn thua popularity. Lambda 10 có RMSE thấp hơn nhưng không đổi tiêu chí chọn để làm đẹp kết quả. Popularity tiếp tục là đối chứng ranking chính ở bước sau. Count popularity không phải dự đoán sao, vì vậy không tính RMSE cho count.

Paired bootstrap 1.000 lần trên 5.341 users, seed 20261121, bias lambda 50 trừ popularity:

- Delta NDCG@10 = -0,238610; percentile CI 95% [-0,244858; -0,232247].
- Delta Recall@10 = -0,032328; CI [-0,033214; -0,031380].

Đây là CI trên validation đã dùng chọn lambda, không phải kiểm định độc lập hoặc kết luận test.

## Các mức support và warm-validation

| Tập | Popularity NDCG@10 | Bias lambda 50 NDCG@10 | Mean RMSE | Bias lambda 10 RMSE | Bias lambda 50 RMSE |
|---|---:|---:|---:|---:|---:|
| Cold 3 support | 0,253602 | 0,017325 | 0,987718 | 0,918223 | 0,941448 |
| Cold 5 support | 0,255947 | 0,017337 | 0,987718 | 0,904851 | 0,935507 |
| Cold 10 support | 0,262693 | 0,017400 | 0,987718 | 0,884794 | 0,922480 |
| Warm-validation | 0,052785 | 0,002136 | 0,990946 | 0,853025 | 0,865930 |

Warm-validation có 42.739 users, 458.825 target pairs; 229 users không positive target, nên ranking có 42.510 users. Warm/cold có số target và candidate loại trừ khác nhau; không dùng chênh lệch trực tiếp để khẳng định cold tốt hơn warm.

Chi tiết mọi cấu hình, Recall, Precision, mẫu số và coverage tại [metrics.json](metrics.json). Không chỉ báo cấu hình thắng; giữ cả hai lambda và ba mức support.

## Ý nghĩa và giới hạn

Bias học mức độ thường được chấm cao của sách và xu hướng chấm sao của user. Vì b_user là một hằng số cộng cho mọi sách, nó không đổi thứ tự ranking của cùng user; personalization hiện chỉ nằm ở việc loại sách đã cung cấp. Thêm support giúp hiệu chỉnh rating, nhưng thay đổi ranking chủ yếu do loại thêm sách đã biết, không chứng minh học được sở thích thể loại.

Popularity tìm được nhiều positive đã quan sát hơn, nhưng chỉ phủ 13/10.000 sách ở cold k5. Đây là độ phủ rất thấp, cần xem cùng NDCG/Recall. Bias ưu tiên sách có item offset cao; objective dự đoán sao không trực tiếp tối ưu truy hồi positive trong full catalogue. Đây là lý do có thể giải thích kết quả, không phải chứng minh nhân quả hoặc đánh giá chất lượng văn học.

Không negative sampling; candidate đủ 10.000 trừ train của warm user hoặc đúng k support của cold user. Không lọc bằng target hoặc các support chưa cung cấp. Missing không phải dislike. Positive >=4 chỉ trên target đã quan sát. Chưa suy hiệu quả online, cold-item hoặc temporal.

## Thời gian và tái lập

Fit lambda 10/50 lần lượt khoảng 3,12/3,40 giây trong lượt này. Cold k5 p50/p95 popularity 0,0042/0,0089 ms; bias lambda 50 0,0034/0,0070 ms. Đây là lookup/filter/Top10 trên **thứ tự global đã cache**, một tiến trình, không gồm load/fit/metrics/serialization. Không dùng số này để dự đoán latency KNN/MF/web/cloud. Timing không tất định, lưu riêng [timing_latest.json](timing_latest.json) với thông tin máy.

- **30 unittest đạt**: 24 cũ chạy lại + 6 mới, gồm metrics tính tay, tie/exclusion, nghiệm ridge đối chiếu hệ tuyến tính độc lập, fold-in support không sửa items, từ chối file test trước I/O, bootstrap.
- Verifier độc lập đọc artifacts k5, tính lại Top10 bằng sort/mask toàn catalogue, tính ranking bằng math và rating predictions vector hóa từ model đã lưu; khớp kết quả cho cả ba ranking baselines và cả ba rating baselines.
- Kiểm hashes input cho phép trước/sau, model artifacts, metrics, script và snapshot protocol. Không đọc/test hash file test; không chạy lại audit raw/ZIP trong Day5. Không có thao tác sửa raw hoặc split.
- Chưa replay toàn CLI lần hai hoặc fresh-install môi trường. requirements thêm NumPy 2.4.6 đúng môi trường đang chạy vì code dùng trực tiếp; pandas/Streamlit giữ nguyên.

Manifest và bằng chứng: [manifest.json](manifest.json), [validation.json](validation.json). Model coefficients, train counts, per-user metrics và Top10 nằm local `data/processed/day05_baselines_v1`, thuộc data bị ignore Git. Không tạo public catalogue hoặc xuất text/ảnh.

```powershell
.venv\Scripts\python.exe -B -m unittest discover -s tests -v
.venv\Scripts\python.exe -B scripts/day05_baselines.py
.venv\Scripts\python.exe -B scripts/verify_day05.py
```

Artifacts tất định từ chối ghi đè payload khác; timing riêng được cập nhật khi chạy lại. Thay model/grid/protocol phải version mới. Input loader có allowlist 5 file validation/train/catalogue, chặn mọi tên khác; đó là guard code, không phải khóa OS toàn workspace.

**Day5 hoàn tất. Bước tiếp Day6–7:** Item-KNN theo cùng split/candidate set, tuning validation và so với popularity; chưa bắt đầu. Không mở test để chọn model; không commit/push/deploy, không thay ScoutIQ. Backlog quyền nguồn và fallback UI giữ nguyên.
