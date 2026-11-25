# Day6–7 — Item-KNN ranking v1, định nghĩa trước chạy

Ngày 23/11/2026. Giữ protocol/split v0.1. Chỉ train học similarity; tuning cold-validation support=5. Không test hoặc MF. Phương pháp item-item tham khảo [Sarwar et al., WWW 2001](https://grouplens.org/site-content/uploads/Item-Based-WWW-2001.pdf); lựa chọn cụ thể dưới đây là thiết kế của BookNest, không tuyên bố tái lập nguyên thuật toán trong bài.

Ma trận incidence A[u,i]=1 khi **rating train >=4**, còn vị trí khác không có positive quan sát. Zero trong ma trận này là không có bằng chứng positive, không phải rating 0 hoặc dislike. C_ij = A_i^T A_j; f_i = số users train chấm i >=4. Similarity = C_ij/sqrt(f_i*f_j) nhân C_ij/(C_ij+shrink). Bỏ self-link, C_ij<2 và item f=0. Đây là cosine trên positive incidence, không adjusted cosine/Pearson trên số sao.

Grid cố định: shrink {10,100} × K {50,200}, 4 cấu hình. Giữ K neighbors lớn nhất **mỗi source item**, hòa similarity theo book_id tăng. Graph sau cắt có hướng; không giả định đối xứng. Tính block 256 source items bằng sparse matrices để tránh ma trận user-item dense. Dùng SciPy CSR, [tài liệu chính thức](https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csr_matrix.html). Float64 similarity, số đếm float64 để tránh tràn số nguyên nhỏ.

Profile được phép: train ratings của warm user; đúng 3/5/10 support ratings của cold user. Score candidate j = tổng từ source i có rating>=4 trong profile của (rating_i-3)*similarity_ij nếu j nằm trong K neighbors của i. Không chia cho tổng similarity mỗi candidate vì sẽ loại lợi ích nhiều bằng chứng đồng thuận trong ranking biến thể này. Không dự đoán sao/RMSE từ affinity score. Ties score dùng book_id tăng, loại **mọi** sách đã cung cấp kể cả rating thấp.

Nếu không còn candidate có score dương (không positive profile hoặc không có neighbor dùng được), fallback toàn danh sách sang popularity tính chỉ từ train. Nếu có score dương, candidate score=0 vẫn được xếp sau positive theo book_id; không âm thầm lọc item khỏi catalogue. Báo số user fallback, số vị trí Top10 không có score dương và coverage. Low ratings không được dùng như negative weight trong biến thể đầu, đây là giới hạn có chủ đích.

Chọn theo NDCG@10 cold-validation support=5, tie Recall rồi K nhỏ, shrink nhỏ. Chỉ cấu hình thắng chạy thêm cold 3/10 và warm-validation. Đối chiếu popularity Day5 cùng user/candidate/target; paired bootstrap 1000 seed20261121 cho delta NDCG/Recall k5, ghi giới hạn CI validation hậu chọn cấu hình. Không kết luận độc lập/test.

Kiểm trước nghiệm thu: toy cooccurrence tính tay, không self-neighbor, topK/tie đúng, cold support không sửa model, loại seen, fallback, sparse output so phép cộng độc lập, hashes inputs/model/metrics, samples similarity đối chiếu sets users train. Đo latency score+Top10 đã warm/cache, tách fit/load; không so số latency cached popularity như kiến trúc tương đương KNN. Lưu artifacts version mới, không sửa Day5.
