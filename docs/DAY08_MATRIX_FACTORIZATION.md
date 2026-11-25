# Day8–9 — explicit MF với fold-in, v1, 23/11/2026

Định nghĩa trước chạy validation. Giữ split/protocol v0.1; không test, không đổi candidate set. Mô hình tham khảo dạng bias + tích vô hướng và regularization trên **ratings quan sát** trong [Koren, Bell, Volinsky 2009](https://gwern.net/doc/ai/tabular/2009-koren.pdf). Cách tối ưu/tách bias dưới đây là thiết kế của BookNest, không tái lập toàn bộ phương pháp Netflix.

## Mô hình và fit

Giữ cố định mu, b_user, b_item từ baseline bias lambda50 Day5 (cấu hình bias được chọn theo ranking). Các coefficients này chỉ học từ train và được xác minh hash. Với observed train pair, y_ui = r_ui-mu-b_user-b_item. Tối ưu:

`sum_observed (y_ui - p_u dot q_i)^2 + lambda*(sum ||p_u||^2 + sum ||q_i||^2)`.

Không có hạng lỗi cho missing pair, không impute 0. Residual bằng 0 **có quan sát** vẫn nằm trong sparse matrix. Dùng alternating least squares: cập nhật từng user bằng ridge trên các item đã được user chấm, rồi từng item từ các users đã chấm nó. Bias không cập nhật cùng factors; đây là MF residual hai giai đoạn, khác MF tối ưu đồng thời bias/factors.

Grid đúng 4 cấu hình: dimensions {16,32} × lambda {10,50}; seed 20261123, item factors khởi tạo Normal(0,0.1), user factors ban đầu zero. 8 vòng đầy đủ user rồi item; không chọn epoch theo test hoặc mở rộng grid khi thua KNN. Không tự gọi 8 vòng là hội tụ; lưu objective từng vòng và kiểm không tăng. Lambda không nhân theo số ratings. BLAS threads=1 trong process để tránh oversubscription ở hàng chục nghìn hệ nhỏ; không thay cấu hình hệ thống.

## Cold fold-in và inference

Chỉ lấy đúng support đã cung cấp. Trước hết user bias = sum(r-mu-b_item)/(50+n_support), cùng công thức baseline Day5. Giữ bias đó cố định rồi giải p_user bằng ridge trên các q_item support với lambda của cấu hình MF và residual r-mu-b_item-b_user. Không cập nhật q, b_item, mu hoặc dùng target. Empty support: p=0, b_user=0. Item không có train: q=0/b_item=0; không loại item/target, ghi số fallback.

Điểm dự đoán = mu+b_user+b_item+p dot q. Ranking dùng điểm **chưa clip**, tie book_id tăng, loại đúng các sách đã cung cấp. RMSE/MAE micro dùng clip[1,5]. Không dùng popularity làm feature/hybrid và không negative sampling. Warm dùng p_user/b_user train đã fit; cold chỉ dùng fold-in. Rating thấp có tham gia fold-in, khác biến thể KNN positive-only.

## Chọn cấu hình và đối chứng

Chọn NDCG@10 cold-validation support5, tie Recall rồi dimensions nhỏ/lambda nhỏ. Chỉ cấu hình thắng chạy thêm cold3/10 và warm. So với popularity, bias Day5 và selected KNN Day6 cùng split/candidate/target. Paired bootstrap 1.000 seed20261121 theo user cho delta cold5 NDCG/Recall so popularity và KNN; CI validation hậu chọn, không test evidence. Chưa khóa quyết định cuối cho Day10 trước khi đọc kết quả này.

## Kiểm và giới hạn dự kiến

Toy observed-only ALS normal equations; giữ observed-zero residual; objective không tăng; fold-in khớp hệ tuyến tính độc lập và không sửa item factors; target không truyền vào scoring; seen/tie/clip đúng. Verifier đọc lại model, so sampled train ALS item equations và tất cả selected cold5 Top10/metrics bằng phép tính độc lập. Timings tính cả fold-in cold và score/sort Top10, một process/cache warm; không gồm load/fit/metrics. Lưu per-user Top10/metric local cùng hashes.

MF này tối ưu dự đoán sao, không trực tiếp tối ưu Top10; có thể thua KNN/popularity về ranking dù RMSE tốt. Kết quả chỉ áp dụng grid/seed/8 vòng/biến thể đã thử. Không kết luận mọi MF tốt/xấu hơn KNN, không temporal/online/cold-item. Chưa fresh-install hoặc cloud benchmark.
