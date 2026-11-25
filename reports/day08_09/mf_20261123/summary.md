# Day8–9 — Matrix Factorization và validation, 23/11/2026

**Đã hoàn tất grid MF; Item-KNN vẫn dẫn đầu ranking validation.** MF được chọn trong họ là **16 chiều, lambda10**, không thay thế Item-KNN. Chưa đọc hoặc đánh giá test; bước tiếp là Day10 khóa cấu hình và đánh giá cuối theo protocol khi được yêu cầu.

## Thiết kế và thực thi

[Định nghĩa trước chạy](../../../docs/DAY08_MATRIX_FACTORIZATION.md): MF residual, giữ bias lambda50 từ Day5 cố định, fit chỉ 3.863.209 train ratings của 42.739 users. ALS tối ưu lỗi bình phương trên cặp đã quan sát và regularization factors. Missing không gán 0; residual 0 có quan sát vẫn được giữ. Tất cả 10.000 item có train, không cần fallback item chưa thấy.

Grid dimensions16/32 × lambda10/50, seed20261123, đúng 8 vòng mỗi cấu hình. Objective giảm ở mọi vòng; chưa tuyên bố hội tụ. Đây là biến thể bias cố định hai giai đoạn, không phải MF tối ưu đồng thời bias/factors. Không mở rộng grid sau xem kết quả.

Cold user bias và vector chỉ giải từ đúng support3/5/10; không cập nhật item factors hoặc dùng target. Rating thấp có tham gia fold-in. Warm dùng user factors đã học từ train. Ranking dùng điểm chưa clip, loại đúng sách đã cung cấp, tie theo book_id; dự đoán sao clip[1,5] khi tính RMSE/MAE. Candidate là toàn catalogue còn lại, không sampled negatives hoặc lọc metadata.

## Grid cold-validation support5

5.342 users, 5.341 có positive target; giữ user không positive trong rating metrics và coverage. Target 545.103 ratings; relevance >=4.

| Mô hình | NDCG@10 | Recall@10 | Precision@10 | Coverage | RMSE | MAE |
|---|---:|---:|---:|---:|---:|---:|
| Popularity Day5 | 0,255947 | 0,034853 | 0,237559 | 0,13% | — | — |
| Item-KNN K200/shrink10 | **0,471873** | **0,066420** | **0,442258** | **49,79%** | — | — |
| **MF d16/l10** | **0,097247** | **0,012989** | **0,092380** | **4,32%** | **0,922190** | **0,731018** |
| MF d16/l50 | 0,024318 | 0,003665 | 0,025276 | 0,24% | 0,931955 | 0,741783 |
| MF d32/l10 | 0,094788 | 0,012531 | 0,088747 | 5,16% | 0,924102 | 0,733205 |
| MF d32/l50 | 0,023788 | 0,003596 | 0,024771 | 0,21% | 0,931957 | 0,741815 |

Chọn MF theo NDCG cold5, không đổi tiêu chí sang coverage hoặc RMSE. Selected MF đề xuất 432 sách khác nhau. 364/545.103 dự đoán sao cold5 cần clip. Popularity/KNN không có đầu ra số sao, không tính RMSE từ affinity.

RMSE MF tốt hơn mean Day5 (0,987718) và bias50 (0,935507), nhưng kém bias10 (0,904851). Vì vậy không kết luận MF thắng tất cả baseline ở dự đoán sao. Bias50 được dùng làm nền vì đó là cấu hình đã chọn trong họ bias theo ranking, không phải tối ưu RMSE.

## Phân tích bổ sung, giữ nguyên cấu hình

| Validation | MF NDCG@10 | KNN NDCG@10 | Popularity NDCG@10 | MF Recall@10 | MF RMSE | MF coverage |
|---|---:|---:|---:|---:|---:|---:|
| Cold3 | 0,071277 | 0,401397 | 0,253602 | 0,009716 | 0,931860 | 3,66% |
| Cold5 | 0,097247 | 0,471873 | 0,255947 | 0,012989 | 0,922190 | 4,32% |
| Cold10 | 0,128648 | 0,546965 | 0,262693 | 0,017005 | 0,905484 | 5,51% |
| Warm | 0,017805 | 0,152098 | 0,052785 | 0,018355 | 0,849449 | 10,67% |

Warm có 42.739 users, 42.510 ranking users, 458.825 target ratings. Không so độ lớn warm/cold như cùng bài toán. Support tăng vừa thêm bằng chứng vừa loại thêm sách đã biết; chưa tách hai tác động.

Paired bootstrap 1.000 lần, seed20261121 trên 5.341 cold5 ranking users, lấy MF trừ đối chứng:

| Đối chứng | Delta NDCG | CI95% NDCG | Delta Recall | CI95% Recall |
|---|---:|---|---:|---|
| Popularity | -0,158700 | [-0,164814; -0,152337] | -0,021864 | [-0,022688; -0,020967] |
| Item-KNN | -0,374626 | [-0,381930; -0,367491] | -0,053430 | [-0,054561; -0,052209] |

Đây là CI trên validation sau chọn cấu hình, không phải bằng chứng test độc lập. Kết quả chỉ áp dụng grid/seed/8 vòng/biến thể đã thử. MF tối ưu lỗi sao, không trực tiếp tối ưu Top10; kết quả này không chứng minh mọi MF đều kém KNN. Ground truth thiếu ratings, Goodbooks thiên về sách phổ biến, cold-user mô phỏng từ users có nhiều ratings; không kết luận temporal, cold-item hoặc hiệu quả online.

## Kiểm tra và artifacts

40 tests đạt (35 cũ +5 mới): ridge so augmented least-squares, observed zero khác missing, ALS objective và phương trình item cuối, fold-in không sửa Q/empty support, ranking chưa clip/seen/tie. Verifier độc lập dùng augmented least-squares thay normal-equation solver của engine; bằng chứng thực thi và phạm vi kiểm ở [validation.json](validation.json). Kiểm đủ selected cold5 Top10/per-user metrics/rating aggregates và 20 phương trình item mẫu từ train; kiểm hashes, factors hữu hạn, traces không tăng và catalogue_v1 hash nguyên. Không kiểm độc lập toàn warm/cold3/10 hoặc mọi grid bằng verifier thứ hai; chưa full training CLI replay/fresh-install.

Fit từng cấu hình khoảng 61–82 giây; selected d16/l10 63,24 giây. Cold5 inference p50/p95 2,1832/4,4350 ms; warm 1,8706/3,4307 ms. Gồm cold fold-in, score toàn catalogue, loại seen, full sort Top10; một process/cache warm, BLAS threads yêu cầu1, không gồm load/fit/metrics hoặc mạng. Không suy tốc độ Render hay concurrency từ số này. [Timing](timing_latest.json).

[Metrics](metrics.json), [training objectives](training_objectives.json), [manifest](manifest.json). Arrays P/Q, biases, IDs, Top10 và per-user ranking metrics ở `data/processed/day08_mf_v1`, được ignore Git; không lưu mọi dự đoán sao theo cặp. Inputs/model/script có SHA-256, artifact tất định từ chối ghi đè khác payload. Không đọc/hash file test; không sửa raw/catalogue/split/Day5/Day6. Không chạy lại full raw audit ở mốc này.

```powershell
.venv\Scripts\python.exe -B -m unittest discover -s tests
.venv\Scripts\python.exe -B scripts/day08_mf.py
.venv\Scripts\python.exe -B scripts/verify_day08.py
```

**Đề xuất Day10:** khóa Item-KNN K200/shrink10 làm mô hình ranking chính; popularity đối chứng và MF d16/l10 là đối chứng mô hình đã chọn. Chốt danh sách/cấu hình trước khi mở test, chạy 3/5/10 và warm theo protocol, không dùng test tuning hoặc refit train+validation. Day10 chưa bắt đầu. Không AI/DB/UI/cloud, không commit/push/deploy hoặc sửa ScoutIQ. Backlog quyền public giữ nguyên.
