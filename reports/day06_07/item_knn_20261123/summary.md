# Day6–7 — Item-KNN và đối chứng validation, 23/11/2026

**Item-KNN vượt popularity trên validation ở cả cold 3/5/10 và warm.** Cấu hình chọn theo cold-validation 5 support là **K=200, shrink=10**. Đây là kết quả chọn mô hình trên validation, chưa phải test hoặc chứng minh hiệu quả online.

## Mô hình đã chạy

[Định nghĩa và grid trước chạy](../../../docs/DAY06_ITEM_KNN.md): cosine trên incidence positive (train rating >=4), nhân shrink C/(C+shrink), tối thiểu 2 users đồng positive; bỏ self-link. Giữ topK neighbors mỗi source item, có hướng sau cắt. 2.663.008 positive pairs lấy từ 3.863.209 train ratings; cold-validation không tham gia học similarity. K=50/200, shrink=10/100, đúng 4 cấu hình.

Score cộng similarity nhân (support rating-3) từ các source được chấm >=4. Đây là affinity ranking, không phải số sao/xác suất thích. Không tính RMSE từ score. Rating thấp vẫn dùng loại sách đã biết nhưng chưa đóng góp negative weight. Zero incidence là thiếu positive quan sát, không gán missing rating bằng 0.

Phương pháp item-item tham khảo [Sarwar et al.](https://grouplens.org/site-content/uploads/Item-Based-WWW-2001.pdf); biến thể positive-only/shrink/source-neighbors và score trên là lựa chọn dự án, không gọi là adjusted cosine/Pearson hoặc tái lập nguyên bài báo. Dùng SciPy CSR và NumPy; SciPy 1.17.0 cài trong .venv BookNest, pin requirements. Lượt pip trong sandbox bị chặn socket; lượt có quyền mạng sau đó cài thành công, NumPy giữ 2.4.6. Không fresh-install toàn môi trường.

## Grid cold-validation, 5 ratings đầu vào

5.342 users; 5.341 có positive target để tính macro ranking; target chung 545.103 ratings. Candidate đủ 10.000 trừ đúng 5 sách đã cung cấp, không lọc sách thiếu mô tả hoặc dùng target để loại candidate.

| Cấu hình | NDCG@10 | Recall@10 | Precision@10 | Coverage |
|---|---:|---:|---:|---:|
| Popularity Day5 | 0,255947 | 0,034853 | 0,237559 | 0,13% |
| K50, shrink10 | 0,462401 | 0,064990 | 0,432091 | 51,46% |
| **K200, shrink10** | **0,471873** | **0,066420** | **0,442258** | **49,79%** |
| K50, shrink100 | 0,460182 | 0,064300 | 0,429657 | 39,55% |
| K200, shrink100 | 0,464206 | 0,064876 | 0,433589 | 39,09% |

Chọn theo NDCG, không thay sang coverage để chọn cấu hình khác. Coverage là 4.979 sách từng xuất hiện trong Top10 của tất cả 5.342 users, so với 13 của popularity. Không phải tỷ lệ catalogue có metadata/public rights.

Paired bootstrap 1.000 lần, seed 20261121, KNN được chọn trừ popularity trên cùng 5.341 users: delta NDCG **+0,215927**, percentile CI95% [0,207896; 0,224341]; delta Recall **+0,031567**, CI [0,030296; 0,032828]. CI này dùng validation sau chọn cấu hình, không phải bằng chứng độc lập; chưa mở test để xác nhận.

## Cấu hình đã chọn trên các tình huống khác

| Tập validation | KNN NDCG@10 | Popularity NDCG@10 | KNN Recall@10 | Popularity Recall@10 | KNN coverage | Users fallback |
|---|---:|---:|---:|---:|---:|---:|
| Cold 3 support | 0,401397 | 0,253602 | 0,055658 | 0,034462 | 57,36% | 301/5.342 |
| Cold 5 support | 0,471873 | 0,255947 | 0,066420 | 0,034853 | 49,79% | 97/5.342 |
| Cold 10 support | 0,546965 | 0,262693 | 0,078198 | 0,035939 | 37,79% | 14/5.342 |
| Warm | 0,152098 | 0,052785 | 0,144211 | 0,052898 | 30,83% | 19/42.739 |

Không chọn lại cấu hình bằng cold3/10 hoặc warm. Warm có 42.510 ranking users (229 không positive target), target 458.825 ratings; cold có target chung và cùng 1 user không positive. Không so trực tiếp độ lớn metric warm với cold như cùng bài toán.

Fallback popularity chỉ khi profile không tạo score dương cho bất kỳ candidate hợp lệ. Trong lượt này mọi slot score=0 ở Top10 đều nằm trong các users fallback: cold3/5/10 lần lượt 3.010/970/140 slots; warm 190. Các users fallback vẫn được giữ trong kết quả, không loại để tăng metrics. Khi có score dương, các candidate score0 vẫn có thể được xếp tiếp theo book_id, không biến mất khỏi candidate set.

## Diễn giải và giới hạn

Khác baseline bias, KNN thay đổi thứ tự theo sách user đã thích. Tăng support cho mô hình thêm bằng chứng và loại thêm sách đã biết; thí nghiệm này không tách riêng hai tác động đó. Kết quả cải thiện trên positive đã quan sát không chứng minh item chưa chấm là không thích. Goodbooks là mẫu thiên về sách phổ biến, cold-user được mô phỏng từ users vốn có nhiều ratings, không cold-item và không temporal.

TopK graph có thể bỏ các liên hệ hữu ích, rating thấp chưa được dùng như phản chứng, và các tập sách cùng series có thể hỗ trợ nhau trong split ngẫu nhiên. Không bổ sung truyện/genre features từ tags toàn nguồn hoặc metadata ngoài train trong mốc này. Không thay grid/seed sau xem kết quả.

## Kiểm tra và khả năng tái lập

- **35 tests đạt** (30 cũ + 5 mới): incidence positive, cosine/shrink tính tay, min overlap/self/tie, profile thay thứ tự, seen rating thấp bị loại, fallback, score so explicit sum và không sửa graph.
- Verifier đọc lại hashes mọi input/output/model/script/metrics; kiểm toàn graph không self, neighbor trùng, số âm hoặc non-finite. Kiểm 10 source rows chọn bằng seed cố định, cả hai shrink: tính lại đủ top200 từ giao tập users train, đối chiếu neighbors/weights.
- Verifier tính lại **toàn bộ 5.342 Top10 cold5** của cấu hình chọn bằng cộng từng cạnh riêng, sort full catalogue, kiểm fallback/zero slots; tính lại NDCG/Recall/Precision/coverage bằng math. Bằng chứng thực thi: [validation.json](validation.json).
- Không replay toàn CLI lần hai; chưa kiểm độc lập mọi grid/warm/cold3/10 bằng verifier thứ hai. Test paths vẫn bị loader allowlist Day5 chặn; không đọc hoặc hash các file test. Không chạy lại audit raw/ZIP, không có thao tác sửa nguồn/split/catalogue.

Fit graph cả hai shrink khoảng 29,77 giây. Cấu hình chọn cold5 p50/p95 inference **0,8605/1,7287 ms**, warm **1,5257/3,6067 ms**. Bao gồm score, loại seen và full-catalogue sort Top10, một tiến trình/cache đã warm; không gồm load/fit/metrics hoặc mạng. Popularity Day5 dùng thứ tự global cache nên phạm vi chi phí khác; không suy latency Render/đa user. Các arrays của cả hai shrink + IDs/counts tổng 48.160.768 bytes, không phải peak RAM. [Timing log](timing_latest.json).

[Metrics](metrics.json), [manifest](manifest.json). Arrays neighbors/weights, per-user metrics và Top10 nằm `data/processed/day06_item_knn_v1`, không đưa Git. Snapshot split/protocol và Day5 artifacts được tham chiếu bằng hash, không sửa. Artifact tất định từ chối ghi đè khác payload; timing riêng được cập nhật khi chạy lại.

```powershell
.venv\Scripts\python.exe -B -m unittest discover -s tests -v
.venv\Scripts\python.exe -B scripts/day06_item_knn.py
.venv\Scripts\python.exe -B scripts/verify_day06.py
```

**Bước tiếp Day8–9:** Matrix Factorization với fold-in từ support, tuning cùng validation và so cả popularity/KNN. Chưa bắt đầu MF, chưa đánh giá test cuối, không AI/DB/UI/cloud, không commit/push/deploy hoặc sửa ScoutIQ. Backlog quyền public giữ nguyên.
