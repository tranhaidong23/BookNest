# Day5 — định nghĩa baseline trước chạy validation, 23/11/2026

Giữ protocol/split v0.1 bất biến. Chỉ đọc train, warm-validation, cold-validation support/target và catalogue IDs. Không đọc file test, không fit nhãn validation. Đây là baseline, chưa Item-KNN/MF.

1. **Popularity:** điểm ranking = số ratings train của sách, bất kể sao; chưa thấy train thì 0. Đây là count quan sát, không phải rating 0 hoặc dislike. Phá hòa bằng book_id tăng dần. Không báo RMSE/MAE cho count.
2. **Global mean:** dự đoán sao bằng trung bình train; chỉ đối chứng RMSE/MAE, không xếp hạng các điểm bằng nhau để tạo metric ranking thiếu ý nghĩa.
3. **Regularized user/item bias:** dự đoán `mu + b_user + b_item`; minimize tổng bình phương sai số train + lambda nhân tổng bình phương biases. Mu cố định trung bình train. Khởi tạo biases=0; 10 vòng cập nhật tuần tự user rồi item theo nghiệm ridge từng nhóm. Thử đúng lambda=10 và 50, cùng lambda cho cả hai phía; không đổi grid sau xem kết quả. Dự đoán sao clip [1,5]. Ranking dùng điểm chưa clip để tránh tạo hòa giả. Unknown item bias=0; unknown user bias=0 nếu không support.

Cold user bias tính riêng từ đúng k support: tổng(r-mu-b_item)/(lambda+k); item biases không cập nhật. Đây chỉ là hiệu chỉnh xu hướng chấm sao: offset user không đổi thứ tự item, nên baseline bias **không cá nhân hóa thứ tự gợi ý** ngoài việc bỏ sách đã cung cấp. Không dùng kết quả này để kết luận 3/5 ratings đã học được sở thích nội dung.

Chọn lambda bias bằng NDCG@10 cold-validation k=5, tie-break Recall@10 rồi lambda theo thứ tự grid. Giữ popularity làm đối chứng dù bias thua. Báo cold k=3/5/10 và warm riêng, macro ranking chỉ trên user có positive target; coverage trên toàn bộ users. RMSE/MAE micro cho mean/bias.

Paired bootstrap 1.000 lần seed 20261121 theo users có positive, báo chênh lệch bias đã chọn so với popularity ở cold-validation k=5; đây là CI trên validation dùng chọn lambda, không là bằng chứng độc lập/test.

Top 10 dùng thứ tự điểm toàn catalogue đã cache của từng baseline (thứ tự bias không phụ thuộc user). Latency đo lookup/filter/extract Top 10, một tiến trình; không gồm load/fit, không gồm metric/serialization, có warm-up. Không suy sang latency KNN/MF, web hoặc cloud. Lưu per-user metrics/Top 10 local để audit; báo aggregate trong reports. Mọi payload model/metric có hash; timing có log riêng vì không tất định.
