# Day10 — đánh giá test cuối, 23/11/2026

**Item-KNN đã chọn bằng validation vượt popularity trên cold-test3/5/10 và warm-test.** So sánh chính cold5: NDCG@10 0,462428 so0,248938; Recall@10 0,065387 so0,033484. Giữ Item-KNN K200/shrink10 cho engine sản phẩm; không chọn lại hoặc tuning sau test.

## Khóa trước khi mở test

[Thiết kế trước test](../../../docs/DAY10_FINAL_EVALUATION.md), [selection lock](selection_lock.json). Lock lưu lúc 08:10:33 UTC; [journal mở test](test_access.json) ghi08:10:45 UTC ngày23/11/2026. Khóa KNN K200/shrink10 chính, popularity/bias50/MF16-lambda10 đối chứng ranking, mean đối chứng sao. Hash toàn model-family artifacts, source evaluators, protocol và split manifest được kiểm trước/sau chạy. Không refit train+validation; giữ train3.863.209 và đủ10.000 candidate items. Các file test đã được mở để đánh giá và **không còn là test chưa xem** cho thay đổi mô hình tương lai.

Warm profile chỉ train, không thêm warm-validation. Cold profile chỉ support prefix3/5/10; phần support10 chưa cung cấp không được dùng để loại candidate hoặc làm target. Cold target chung543.667 ratings, 5.343 users, 5.342 có positive target. Warm target458.825, 42.739 users, 42.543 có positive (196 không positive). Không bỏ user để làm đẹp kết quả; các users không positive vẫn tính coverage/rating metrics. Mọi item/target item đều có train; unseen count0 ở cả bốn tình huống.

## Kết quả chính: cold5

| Mô hình | NDCG@10 | Recall@10 | Precision@10 | Coverage | RMSE | MAE |
|---|---:|---:|---:|---:|---:|---:|
| Popularity | 0,248938 | 0,033484 | 0,228940 | 0,14% | — | — |
| Bias lambda50 | 0,016466 | 0,002437 | 0,016979 | 0,11% | 0,935092 | 0,745273 |
| MF16/lambda10 | 0,095395 | 0,012814 | 0,089948 | 4,56% | 0,921183 | 0,730963 |
| **Item-KNN K200/shrink10** | **0,462428** | **0,065387** | **0,434575** | **50,24%** | — | — |
| Global mean | — | — | — | — | 0,986034 | 0,770939 |

KNN đề xuất5.024 sách khác nhau so14 của popularity. 84/5.343 users fallback popularity; vẫn tính toàn bộ trong kết quả, 840 Top10 slots không có affinity dương. MF clip372 dự đoán sao ngoài[1,5], ranking vẫn dùng raw score. Không tính RMSE cho affinity KNN hoặc popularity.

Paired bootstrap users1.000, seed20261121; KNN trừ popularity trên cùng5.342 users:

- NDCG delta **+0,213490**, CI95% **[0,205643; 0,221704]**.
- Recall delta **+0,031903**, CI95% **[0,030594; 0,033235]**.

Đây là so sánh test đã định trước. Cả hai khoảng không chứa0, ủng hộ cải thiện truy hồi positive đã quan sát trong benchmark. Không diễn giải CI thành95% xác suất thuật toán thắng mọi người dùng hoặc hiệu quả online.

## Phân tích bổ sung

| Tình huống | KNN NDCG | Popularity NDCG | MF NDCG | KNN Recall | Popularity Recall | KNN coverage | KNN fallback |
|---|---:|---:|---:|---:|---:|---:|---:|
| Cold3 | 0,400849 | 0,246315 | 0,069033 | 0,056167 | 0,033071 | 56,92% | 288 |
| Cold5 | 0,462428 | 0,248938 | 0,095395 | 0,065387 | 0,033484 | 50,24% | 84 |
| Cold10 | 0,542567 | 0,255365 | 0,127751 | 0,077848 | 0,034574 | 37,93% | 23 |
| Warm | 0,152072 | 0,052137 | 0,017225 | 0,143584 | 0,052254 | 30,83% | 19 |

MF RMSE cold3/5/10 lần lượt0,930866/0,921183/0,904561; warm0,852723 so bias50 0,868888 và mean0,993561. MF cải thiện số sao so các đối chứng sao đã khóa trong lượt test, nhưng không thắng ranking. Không thêm bias10 vào test sau khi thấy kết quả; Day5 validation từng cho thấy bias10 có RMSE tốt hơn MF cold5, đó là giới hạn cần giữ khi trình bày.

CI cho các tình huống/đối chứng bổ sung có trong metrics nhưng không hiệu chỉnh nhiều so sánh; không gọi mọi CI là bằng chứng xác nhận độc lập. Không so trực tiếp độ lớn warm/cold như cùng bài toán. Support tăng vừa thêm bằng chứng vừa loại thêm sách đã biết. Coverage giảm theo support không có nghĩa metadata bị mất.

## Kiểm tra và tái lập

42 Python tests đạt trước lock/test. Hai tests mới bảo vệ tách allowlist validation/test và phát hiện model/config đổi sau lock. Verifier đọc lại toàn bộ Top10 của4 mô hình ×4 tình huống, kiểm seen/unique/candidate/per-user metrics/aggregates/coverage, không chỉ đọc số summary. Riêng cold5 kiểm độc lập KNN bằng cộng từng cạnh và MF bằng augmented least-squares; đối chiếu cả MF rating aggregates. [Bằng chứng thực thi](validation.json).

Không replay toàn CLI lần hai; chưa kiểm độc lập rating metrics của mean/bias hoặc MF ngoài cold5 bằng engine thứ hai. Không gọi lại full raw audit; không thao tác sửa raw/catalogue/split/models. Test metrics được giữ nguyên; nếu về sau tìm thấy lỗi phải version mới và công bố test đã xem, không giả lập một holdout độc lập khác từ cùng kết quả.

KNN cold5 p50/p95 inference0,6891/1,9726ms; warm1,4772/3,4710ms. MF cold5 1,7252/4,0481ms. Engine đo cached score/filter/full-sort, MF gồm fold-in; baseline đo lấy Top10 từ thứ tự global cache nên phạm vi chi phí khác. Máy có công việc kiểm local song song; đây không phải benchmark tải riêng hoặc SLA Render. [Timing](timing_latest.json).

```powershell
.venv\Scripts\python.exe -B -m unittest discover -s tests
.venv\Scripts\python.exe -B scripts/day10_evaluate.py --lock
.venv\Scripts\python.exe -B scripts/day10_evaluate.py
.venv\Scripts\python.exe -B scripts/verify_day10.py
```

[Metrics](metrics.json), [manifest](manifest.json). Output `data/processed/day10_final_v1` chứa per-user metrics/Top10, được ignore Git. Lock đã tồn tại thì --lock chỉ xác minh, không ghi mới thời điểm hoặc chọn lại model.

## Phạm vi kết luận và bước tiếp

Kết quả offline trả lời câu hỏi nghiên cứu trong Goodbooks: với3–5 ratings hỗ trợ, KNN tốt hơn popularity về truy hồi positive đã quan sát. Missing là unjudged, không dislike; sách phổ biến và người dùng vốn có nhiều ratings tạo selection bias. Không có timestamps nên không temporal, không cold-item, không causal/online. Chưa kiểm người mới thực tế hoặc rubric chính thức.

Người dùng đã cho phép tiếp tục nhiều mốc local. Day11 schema/ownership được chuẩn bị và kiểm PostgreSQL nhúng riêng, không đổi recommender sau test. Tiếp theo local app; cloud/auth/public rights vẫn cần chứng cứ thực tế, không tự commit/push/deploy hoặc sửa ScoutIQ.
